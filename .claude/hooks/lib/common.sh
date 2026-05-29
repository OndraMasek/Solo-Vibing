#!/usr/bin/env bash
# .claude/hooks/lib/common.sh — shared helpers for Solo-Vibing cascade hooks.
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
  # This is the D2.1 v2 §Caller-side-verification step-3 recomputation predicate.
  #
  # CANONICAL SERIALIZATION (SOL-119): the zeroed manifest is serialized as
  #   json.dumps(data, sort_keys=True, separators=(",", ":"))   # ensure_ascii=True
  # i.e. compact, key-sorted, ASCII-escaped, no trailing newline — byte-for-byte
  # identical to tools/solo-verify's _sha256_manifest_self_zeroed. We delegate to
  # python3 (a documented repo prereq — see tools/solo-verify and the four-hat
  # hook) so the hook and the CLI share ONE serializer. A prior jq pipeline
  # (`jq -S | sha256sum`) silently diverged: jq pretty-prints, drops trailing
  # `.0` on floats, and emits raw UTF-8, none of which match python's json.dumps,
  # so the same manifest hashed to different values under the hook vs the CLI.
  local path="$1"
  if [ ! -f "$path" ]; then
    echo "hook-lib: sha256_manifest_self_zeroed: manifest absent: $path" >&2
    return 1
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    echo "hook-lib: sha256_manifest_self_zeroed requires python3 (canonical manifest serializer); not on PATH" >&2
    return 1
  fi
  python3 -c '
import json, hashlib, sys
with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)
data["manifest_sha256"] = ""
canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
print(hashlib.sha256(canonical.encode("utf-8")).hexdigest())
' "$path"
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
