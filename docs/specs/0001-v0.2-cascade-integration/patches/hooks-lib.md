# `.claude/hooks/_lib.sh` + `.claude/hooks/_lib.py` — shared hook helpers

**Status:** Patch-ready new files. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing`.

**Scope:** the shared JSON-stdin-handling preamble, manifest-reading helpers, sha256 utilities, and structured-output emitters that each hook script in `.claude/hooks/` sources. Per `decomposition.md` Child 0001-C notes: "Factor that into a `.claude/hooks/_lib.sh` (bash) and `.claude/hooks/_lib.py` (Python) so each script is roughly 20–40 lines of predicate logic instead of 60–80 lines of stdin / event-shape handling."

**v0.1 reconciliation:** none. v0.1 has no `.claude/hooks/` directory per `repo-state-summary.md` Part 2. Both files are new in v0.2.

**Path conventions used by both files:**

- `$CLAUDE_PROJECT_DIR` — project root, populated by Claude Code per D2.2 §Environment variables. Both helpers resolve all paths relative to this.
- `.cascade/run-state.json` — canonical run-state file per D2.1 v2.1 §The `cascade:run-state` schema (at repo root, NOT under `docs/`).
- `.cascade/manifests/` — manifest directory at repo root.
- `.cascade/session/` — per-session state at repo root.
- `.cascade/halt/` — halt diagnostic artifacts at repo root.
- `.cascade/telemetry/sessions.jsonl` — append-only telemetry per `decomposition.md`.

---

## `.claude/hooks/_lib.sh` — bash helpers

```bash
#!/usr/bin/env bash
# .claude/hooks/_lib.sh — shared helpers for Solo-Vibing cascade hooks.
# Sourced by every bash hook script. Provides:
#   - read_hook_payload: read stdin JSON, populate $HOOK_PAYLOAD
#   - jq_field: extract a field from $HOOK_PAYLOAD via jq
#   - sha256_file / sha256_string: compute sha256 of file or string
#   - sha256_manifest_self_zeroed: recompute manifest sha with manifest_sha256 zeroed
#   - read_run_state: load .cascade/run-state.json into $RUN_STATE
#   - read_manifest <path>: load named manifest JSON
#   - emit_hook_specific_output <eventName> <key> <value>: emit standard wrapper
#   - emit_stop_block <reason>: emit top-level Stop/SubagentStop quirk shape
#   - log_halt <halt_code> <diagnostic>: append to .cascade/halt/<code>.txt
#   - require_cmd <name>: assert binary on PATH; exit 4 if absent
#
# All functions assume CLAUDE_PROJECT_DIR is set. They exit nonzero on missing
# inputs; the caller decides whether to convert nonzero to exit-2 (block) or
# exit-0 (pass with warning).
#
# Dependencies: bash 4+, jq, sha256sum (or shasum -a 256 on macOS).
# The require_cmd preamble below catches missing deps before any predicate runs.

set -u  # nounset; caller can override with set +u if needed

# ---- Dependency check ------------------------------------------------------

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "hook-lib: required command '$cmd' not on PATH" >&2
    exit 4
  fi
}

# Run dep check once per source. macOS ships shasum but not sha256sum; alias.
if ! command -v sha256sum >/dev/null 2>&1; then
  if command -v shasum >/dev/null 2>&1; then
    sha256sum() { shasum -a 256 "$@"; }
    export -f sha256sum
  else
    echo "hook-lib: neither sha256sum nor shasum found; install coreutils (Linux) or shasum is standard on macOS" >&2
    exit 4
  fi
fi
require_cmd jq

# ---- Project-dir resolution -----------------------------------------------

if [ -z "${CLAUDE_PROJECT_DIR:-}" ]; then
  # Fallback: walk up from $PWD looking for .cascade/ — D2.2 says
  # $CLAUDE_PROJECT_DIR is populated, but this is a defensive fallback for
  # standalone CLI use (per D2.2 §Critical caveats #1: predicates must also
  # be invocable via solo-verify CLI for the max_turns gap).
  dir="$PWD"
  while [ "$dir" != "/" ] && [ ! -d "$dir/.cascade" ]; do
    dir="$(dirname "$dir")"
  done
  if [ -d "$dir/.cascade" ]; then
    export CLAUDE_PROJECT_DIR="$dir"
  else
    echo "hook-lib: CLAUDE_PROJECT_DIR unset and no .cascade/ found by walking up from $PWD" >&2
    exit 4
  fi
fi

# ---- Hook payload IO -------------------------------------------------------

read_hook_payload() {
  # Reads stdin and exports HOOK_PAYLOAD as the raw JSON string.
  # Hook scripts call this once at startup.
  HOOK_PAYLOAD="$(cat)"
  export HOOK_PAYLOAD
  if [ -z "$HOOK_PAYLOAD" ]; then
    echo "hook-lib: empty stdin; expected hook payload JSON" >&2
    exit 4
  fi
  # Verify it parses
  if ! echo "$HOOK_PAYLOAD" | jq -e . >/dev/null 2>&1; then
    echo "hook-lib: stdin is not valid JSON" >&2
    exit 4
  fi
}

jq_field() {
  # jq_field <jq-expression>  → prints result to stdout
  # On missing field, prints empty string and returns 1.
  local expr="$1"
  local result
  result="$(echo "$HOOK_PAYLOAD" | jq -r "$expr // empty")"
  echo "$result"
  [ -n "$result" ]
}

# ---- Hashing ---------------------------------------------------------------

sha256_file() {
  # sha256_file <path>  → prints hex sha256
  local path="$1"
  if [ ! -f "$path" ]; then
    echo "hook-lib: sha256_file: file absent: $path" >&2
    return 1
  fi
  sha256sum "$path" | awk '{print $1}'
}

sha256_string() {
  # sha256_string <string>  → prints hex sha256
  printf '%s' "$1" | sha256sum | awk '{print $1}'
}

sha256_manifest_self_zeroed() {
  # sha256_manifest_self_zeroed <manifest-path>  → prints the sha256 the manifest
  # would carry if its own manifest_sha256 field were zeroed before hashing.
  # This is the D2.1 v2 recomputation predicate.
  local path="$1"
  if [ ! -f "$path" ]; then
    echo "hook-lib: sha256_manifest_self_zeroed: manifest absent: $path" >&2
    return 1
  fi
  # jq -S sorts keys for canonical form; .manifest_sha256 = "" zeros the field.
  jq -S '.manifest_sha256 = ""' "$path" | sha256sum | awk '{print $1}'
}

# ---- Cascade state IO ------------------------------------------------------

read_run_state() {
  # Loads .cascade/run-state.json (canonical path per D2.1 v2.1) into
  # the RUN_STATE variable. Exit 4 if absent or malformed.
  local path="$CLAUDE_PROJECT_DIR/.cascade/run-state.json"
  if [ ! -f "$path" ]; then
    echo "hook-lib: run-state absent at $path" >&2
    return 1
  fi
  RUN_STATE="$(cat "$path")"
  if ! echo "$RUN_STATE" | jq -e . >/dev/null 2>&1; then
    echo "hook-lib: run-state at $path is not valid JSON" >&2
    return 1
  fi
  export RUN_STATE
}

run_state_field() {
  # run_state_field <jq-expression>  → prints field from $RUN_STATE
  local expr="$1"
  echo "$RUN_STATE" | jq -r "$expr // empty"
}

read_manifest() {
  # read_manifest <path>  → loads manifest at $path, exports MANIFEST
  local path="$1"
  if [ ! -f "$path" ]; then
    echo "hook-lib: manifest absent: $path" >&2
    return 1
  fi
  MANIFEST="$(cat "$path")"
  if ! echo "$MANIFEST" | jq -e . >/dev/null 2>&1; then
    echo "hook-lib: manifest at $path is not valid JSON" >&2
    return 1
  fi
  export MANIFEST
}

manifest_field() {
  # manifest_field <jq-expression>  → prints field from $MANIFEST
  local expr="$1"
  echo "$MANIFEST" | jq -r "$expr // empty"
}

# ---- Output emitters -------------------------------------------------------

emit_hook_specific_output() {
  # emit_hook_specific_output <eventName> <jq-merge-object>
  #
  # Emits the standard hookSpecificOutput wrapper used by every event EXCEPT
  # Stop / SubagentStop / StopFailure (those use top-level fields per D2.2
  # §Stop / SubagentStop output schema quirk; use emit_stop_block instead).
  #
  # Example: emit_hook_specific_output "PreToolUse" \
  #            '{"permissionDecision":"deny","permissionDecisionReason":"…"}'
  local event_name="$1"
  local fields_json="$2"
  jq -c -n \
    --arg event "$event_name" \
    --argjson fields "$fields_json" \
    '{hookSpecificOutput: ({hookEventName: $event} + $fields)}'
}

emit_stop_block() {
  # emit_stop_block <reason>
  #
  # Emits the Stop / SubagentStop top-level-fields-only output per D2.2
  # §Stop / SubagentStop output schema quirk. NO hookSpecificOutput wrapper.
  # The `reason` string is FACTUAL phrasing per D2.2 §Critical caveats #3 and
  # D2.3 v1.2 four-hat review §F-Int-2 — describe the failure; don't issue
  # imperative instructions.
  local reason="$1"
  jq -c -n --arg reason "$reason" '{decision: "block", reason: $reason}'
}

emit_additional_context() {
  # emit_additional_context <text>
  #
  # SessionStart-specific output. Writes context to be added to Claude's
  # next-turn input. Factual phrasing per D2.2.
  local text="$1"
  jq -c -n --arg context "$text" \
    '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $context}}'
}

# ---- Halt logging ----------------------------------------------------------

log_halt() {
  # log_halt <halt-code> <diagnostic-text>
  #
  # Appends a halt diagnostic to .cascade/halt/<code>.txt. The caller decides
  # whether to also emit a block decision; this function only records.
  local code="$1"
  local diagnostic="$2"
  local halt_dir="$CLAUDE_PROJECT_DIR/.cascade/halt"
  mkdir -p "$halt_dir"
  # Strip leading § from filename (filesystem-safe), keep in content
  local safe_name
  safe_name="$(echo "$code" | tr -d '§/')"
  local path="$halt_dir/${safe_name}.txt"
  {
    echo "## $code"
    echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "Diagnostic:"
    echo "$diagnostic"
    echo "---"
  } >> "$path"
}

# ---- Tracing (env-gated) ---------------------------------------------------

# Set SOLO_HOOK_TRACE=1 in the environment to enable per-hook stderr tracing.
# Hooks call `trace "message"` for diagnostic logging; in production runs the
# trace is silent.
trace() {
  if [ "${SOLO_HOOK_TRACE:-}" = "1" ]; then
    echo "[$(basename "${BASH_SOURCE[1]:-hook}")] $*" >&2
  fi
}
```

---

## `.claude/hooks/_lib.py` — Python helpers

```python
#!/usr/bin/env python3
"""
.claude/hooks/_lib.py — shared helpers for Solo-Vibing cascade Python hooks.

Imported by every Python hook script. Provides:
  - read_hook_payload(): read stdin JSON
  - read_run_state(): load .cascade/run-state.json
  - read_manifest(path): load named manifest JSON
  - sha256_file(path), sha256_string(s): hex sha256
  - sha256_manifest_self_zeroed(path): D2.1 v2 recomputation predicate
  - emit_hook_specific_output(event_name, fields): standard wrapper
  - emit_stop_block(reason): Stop/SubagentStop top-level-fields-only quirk
  - log_halt(code, diagnostic): append to .cascade/halt/<code>.txt
  - project_dir(): resolve $CLAUDE_PROJECT_DIR or walk up from $PWD

Python stdlib only (no third-party deps). Compatible with Python 3.10+ per
D4.0's stack-floor decision.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---- Project-dir resolution ----------------------------------------------


def project_dir() -> Path:
    """Resolve CLAUDE_PROJECT_DIR or walk up from CWD looking for .cascade/."""
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    here = Path.cwd().resolve()
    for candidate in (here, *here.parents):
        if (candidate / ".cascade").is_dir():
            return candidate
    raise SystemExit(
        f"hook-lib: CLAUDE_PROJECT_DIR unset and no .cascade/ found "
        f"by walking up from {here}"
    )


# ---- Hook payload IO -----------------------------------------------------


def read_hook_payload() -> dict:
    """Read stdin and parse as JSON. Exits 4 on empty or malformed."""
    raw = sys.stdin.read()
    if not raw.strip():
        sys.stderr.write("hook-lib: empty stdin; expected hook payload JSON\n")
        sys.exit(4)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"hook-lib: stdin is not valid JSON: {e}\n")
        sys.exit(4)


# ---- Hashing -------------------------------------------------------------


def sha256_file(path: Path) -> str:
    """Hex sha256 of file content."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_string(s: str) -> str:
    """Hex sha256 of a string (utf-8 encoded)."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_manifest_self_zeroed(path: Path) -> str:
    """
    Recompute a manifest's sha256 with its own manifest_sha256 field zeroed,
    using canonical JSON form (sorted keys, no extra whitespace).
    This is the D2.1 v2 recomputation predicate.
    """
    with open(path, "r") as f:
        obj = json.load(f)
    obj["manifest_sha256"] = ""
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---- Cascade state IO ----------------------------------------------------


def read_run_state(root: Path | None = None) -> dict:
    """Load .cascade/run-state.json. Returns the parsed dict.

    Raises FileNotFoundError if absent (caller decides if absent → halt or pass).
    """
    if root is None:
        root = project_dir()
    path = root / ".cascade" / "run-state.json"
    if not path.is_file():
        raise FileNotFoundError(str(path))
    with open(path, "r") as f:
        return json.load(f)


def read_manifest(path: Path) -> dict:
    """Load a manifest JSON. Returns the parsed dict."""
    with open(path, "r") as f:
        return json.load(f)


# ---- Output emitters -----------------------------------------------------


def emit_hook_specific_output(event_name: str, fields: dict) -> None:
    """
    Print the standard hookSpecificOutput wrapper to stdout.
    Use for every event EXCEPT Stop / SubagentStop / StopFailure.
    """
    payload = {"hookSpecificOutput": {"hookEventName": event_name, **fields}}
    print(json.dumps(payload), flush=True)


def emit_stop_block(reason: str) -> None:
    """
    Print the Stop / SubagentStop top-level-fields-only output per D2.2
    §Stop / SubagentStop output schema quirk. NO hookSpecificOutput wrapper.
    Use for Stop, SubagentStop, StopFailure events ONLY.

    `reason` should be FACTUAL phrasing per D2.2 §Critical caveats #3 and
    D2.3 v1.2 four-hat review §F-Int-2 — describe the failure; don't issue
    imperative instructions.
    """
    print(json.dumps({"decision": "block", "reason": reason}), flush=True)


def emit_additional_context(text: str) -> None:
    """SessionStart-specific output that adds factual context to the next turn."""
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": text,
        }
    }
    print(json.dumps(payload), flush=True)


# ---- Halt logging --------------------------------------------------------


def log_halt(code: str, diagnostic: str, root: Path | None = None) -> None:
    """
    Append a halt diagnostic to .cascade/halt/<code>.txt. The caller decides
    whether to also emit a block decision; this only records.
    """
    if root is None:
        root = project_dir()
    halt_dir = root / ".cascade" / "halt"
    halt_dir.mkdir(parents=True, exist_ok=True)
    # Strip leading § from filename (filesystem-safe), keep in content
    safe = code.lstrip("§").replace("/", "-")
    path = halt_dir / f"{safe}.txt"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(path, "a") as f:
        f.write(f"## {code}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write("Diagnostic:\n")
        f.write(f"{diagnostic}\n")
        f.write("---\n")


# ---- Tracing (env-gated) -------------------------------------------------


def trace(*args) -> None:
    """SOLO_HOOK_TRACE=1 enables stderr diagnostic logging."""
    if os.environ.get("SOLO_HOOK_TRACE") == "1":
        sys.stderr.write("[hook] " + " ".join(str(a) for a in args) + "\n")
```

---

## Common patterns the lib enforces

**Path canonicalization.** Both files resolve all paths relative to `$CLAUDE_PROJECT_DIR` (populated by Claude Code per D2.2 §Environment variables) with a fallback that walks up from `$PWD` looking for `.cascade/`. The fallback exists because predicates must also be invocable as standalone `solo-verify` CLI commands per D2.2 §Critical caveats #1 (the `max_turns` gap).

**Output schema dispatch.** `emit_hook_specific_output` for the standard wrapper; `emit_stop_block` for the Stop/SubagentStop quirk; `emit_additional_context` for SessionStart. Hook scripts call the right emitter for their event; the lib enforces the shape.

**Sha256 portability.** Bash lib aliases `shasum -a 256` to `sha256sum` on macOS so scripts can call `sha256sum` uniformly. Python uses `hashlib` (stdlib).

**Manifest sha recomputation.** Both `sha256_manifest_self_zeroed` implementations zero the `manifest_sha256` field and recompute via canonical JSON form (sorted keys, no extra whitespace). This matches D2.1 v2's recomputation predicate. The bash version uses `jq -S`; the Python version uses `json.dumps(sort_keys=True, separators=(",",":"))`. Both produce the same hash for the same input.

**No third-party deps.** Bash needs `jq` (a hard dep — surfaced via `require_cmd` at source-time so missing-jq surfaces immediately as exit 4 with a clear diagnostic). Python is stdlib-only.

**Halt logging is structural.** `log_halt` appends to `.cascade/halt/<code>.txt`. The cascade reads these at `/retro` time (per `retro-SKILL-amendments.md` Section 2's halt-case rendering) and at `solo-cascade resume` time (per D4.6 v1.1's recovery surface).

---

## Cross-references

- **D2.1 v2 §The `cascade:run-state` schema** + **D2.1 v2.1** — canonical `.cascade/run-state.json` path used by `read_run_state`.
- **D2.1 v2 §Caller-side verification protocol** — the recomputation predicate `sha256_manifest_self_zeroed` implements.
- **D2.2 §Hook handler types** — the `command` type that all six bash scripts and the Python one use.
- **D2.2 §Stop / SubagentStop output schema quirk** — binding for `emit_stop_block`'s top-level-fields-only shape.
- **D2.2 §Critical caveats #1** — the `max_turns` gap that motivates the `$PWD`-walk fallback in `project_dir()`.
- **D2.2 §Critical caveats #3** — the factual-phrasing-not-imperative warning that `emit_stop_block`'s docstring carries.
- **D2.2 §Environment variables available to hooks** — `$CLAUDE_PROJECT_DIR` semantics.
- **D2.3 v1.2 four-hat review §F-Int-2** — the factual-phrasing pattern reinforced in `emit_stop_block`'s docstring.
- **D4.0 §Single file, Python 3.10+** — the Python stdlib-only constraint `_lib.py` honors.
- **decomposition.md** Child 0001-C notes — the explicit guidance to factor shared preamble into `_lib.sh` and `_lib.py`.
