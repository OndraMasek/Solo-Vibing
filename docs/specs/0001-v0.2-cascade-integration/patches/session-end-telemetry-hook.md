# `.claude/hooks/session-end-telemetry.sh` — async telemetry sink

**Status:** Patch-ready new file. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing`.

**Scope:** wraps the per-session telemetry emission as a `SessionEnd` hook with `async: true` per D2.2 §Critical caveats #4 (telemetry never gates progression — fire-and-forget). Appends one JSONL line to `.cascade/telemetry/sessions.jsonl` per session. The line captures session duration, stages touched (from `cascade:run-state.active_stages[]` history accumulated during the session), halt count (from `.cascade/halt/` file count), compact cycles (from `.cascade/session/<session_id>.json`), and the session's exit reason.

The output of this hook is consumed by `/retro` Section 3 (per Child 0001-B continuation 2 `retro-SKILL-amendments.md`) for per-milestone session-discipline rendering. **Path reconciliation:** `decomposition.md` says `.cascade/telemetry/sessions.jsonl` (single appended file); `retro-SKILL-amendments.md` continuation 2 says `.cascade/session/<milestone>-*.jsonl` (per-milestone files). This hook uses **`.cascade/telemetry/sessions.jsonl`** per the canonical author (`decomposition.md`); the retro skill amendment needs to be revised at apply-time to read from the single-file path and filter records by milestone. **Surfaced item.**

**v0.1 reconciliation:** none. v0.1 has no `.claude/hooks/` per `repo-state-summary.md` Part 2.

---

## Output shape

SessionEnd is wired with `async: true`, which makes the hook fire-and-forget. Per D2.2 §Hook events table SessionEnd row: "Last chance to flush state." There's no decision surface for SessionEnd (the session is already ending; no halt is possible). The hook writes to disk and exits 0.

The script writes nothing to stdout (no `hookSpecificOutput`, no decision). Any output would be discarded because async hooks don't block; emitting structured output would be a leak with no consumer.

---

## Matcher

Wired in `.claude/settings.json` to SessionEnd with no source matcher (catches all variants: `exit`, `sigint`, `error` per D2.2 §Hook events table).

---

## Telemetry JSONL schema

Each line is a single JSON object with these fields:

```json
{
  "session_id": "claude-cli-9f2a...",
  "session_started_at": "2026-05-18T14:00:00Z",
  "session_ended_at": "2026-05-18T16:42:11Z",
  "duration_seconds": 9731,
  "exit_reason": "exit",
  "marker": "BOM",
  "product": "Bomb",
  "active_milestone": "[BOM] M-2: First playable level",
  "last_completed_group": "F",
  "compact_cycles": 1,
  "stages_touched": ["build:SOL-117", "wrap:SOL-117"],
  "halts_emitted": [
    {"code": "§provenance-chain-broken", "at": ".cascade/halt/provenance-chain-broken.txt"}
  ],
  "halts_count": 1,
  "telemetry_schema_version": "0.2-childC"
}
```

Fields:

- `session_id` — from SessionEnd payload.
- `session_started_at` — from `.cascade/session/<session_id>.json` (the file the PreCompact hook initialized).
- `session_ended_at` — current timestamp.
- `duration_seconds` — computed.
- `exit_reason` — from SessionEnd payload (`exit`, `sigint`, `error`).
- `marker`, `product`, `active_milestone`, `last_completed_group` — from `cascade:run-state.json`.
- `compact_cycles` — from `.cascade/session/<session_id>.json`.
- `stages_touched` — derived from manifests written during the session (filesystem scan of `.cascade/manifests/*.json` modified during this session window).
- `halts_emitted` — file list from `.cascade/halt/*.txt` modified during this session window.
- `halts_count` — len of the above.
- `telemetry_schema_version` — `"0.2-childC"`; bumped if schema evolves.

If any source field is unavailable (no run-state, no session file, missing manifest dir), the field is set to `null` rather than the line being skipped. Telemetry should be best-effort, never blocking.

---

## Script content

```bash
#!/usr/bin/env bash
# .claude/hooks/session-end-telemetry.sh
#
# Async SessionEnd hook per D2.2 §Critical caveats #4: telemetry never gates
# progression. Appends one JSONL line per session to .cascade/telemetry/sessions.jsonl.
#
# Schema: see telemetry JSONL schema doc.
# Exit codes: always 0 (best-effort; never blocks the session ending).

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
. "$SCRIPT_DIR/_lib.sh"

trace "session-end-telemetry: fired"

read_hook_payload

# SessionEnd payload shape per D2.2:
#   {"reason": "exit" | "sigint" | "error", "session_id": "...", ...}
session_id="$(jq_field '.session_id')"
exit_reason="$(jq_field '.reason // "unknown"')"

if [ -z "$session_id" ]; then
  # Unusual but defend against it
  session_id="unknown-$(date -u +%s)"
fi

now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Read session-state for started_at + compact_cycles
session_path="$CLAUDE_PROJECT_DIR/.cascade/session/$session_id.json"
started_at="null"
compact_cycles="0"
if [ -f "$session_path" ]; then
  started_at="$(jq -r '.started_at // "null"' "$session_path")"
  compact_cycles="$(jq -r '.compact_cycles // 0' "$session_path")"
fi

# Compute duration_seconds if started_at is parseable
duration_seconds="null"
if [ "$started_at" != "null" ] && [ -n "$started_at" ]; then
  # Convert to epoch and subtract. macOS date and GNU date have different
  # flag syntax; try GNU first, fall back to BSD.
  start_epoch=""
  if start_epoch="$(date -u -d "$started_at" +%s 2>/dev/null)"; then
    : # GNU date worked
  elif start_epoch="$(date -j -u -f '%Y-%m-%dT%H:%M:%SZ' "$started_at" +%s 2>/dev/null)"; then
    : # BSD date worked
  fi
  if [ -n "$start_epoch" ]; then
    end_epoch="$(date -u +%s)"
    duration_seconds="$((end_epoch - start_epoch))"
  fi
fi

# Read run-state for marker, product, active_milestone, last_completed_group
marker="null"
product="null"
active_milestone="null"
last_completed_group="null"
if read_run_state 2>/dev/null; then
  marker="$(run_state_field '.marker' || echo null)"
  product="$(run_state_field '.product' || echo null)"
  active_milestone="$(run_state_field '.active_milestone' || echo null)"
  last_completed_group="$(run_state_field '.last_completed_group' || echo null)"
fi

# Collect stages_touched (manifests modified during this session)
# Window: between session start (if known) and now. Fallback: last 24h.
# Uses find -newer for the manifests dir.
stages_touched_json="[]"
manifests_dir="$CLAUDE_PROJECT_DIR/.cascade/manifests"
if [ -d "$manifests_dir" ]; then
  # If we have session_path with started_at, find files newer than that
  if [ "$started_at" != "null" ] && [ -f "$session_path" ]; then
    stages_touched_lines="$(find "$manifests_dir" -name "*.json" -newer "$session_path" 2>/dev/null \
      | while read -r path; do
          # Manifest filename convention: <ticket>-<stage>.json
          base="$(basename "$path" .json)"
          # Try to extract stage from manifest content (authoritative)
          stage="$(jq -r '.stage // ""' "$path" 2>/dev/null | sed 's|^/||')"
          ticket="$(jq -r '.ticket // ""' "$path" 2>/dev/null)"
          if [ -n "$stage" ] && [ -n "$ticket" ]; then
            echo "${stage}:${ticket}"
          else
            echo "$base"
          fi
        done | sort -u)"
    if [ -n "$stages_touched_lines" ]; then
      stages_touched_json="$(echo "$stages_touched_lines" | jq -R -s 'split("\n") | map(select(length > 0))')"
    fi
  fi
fi

# Collect halts emitted during this session
halts_json="[]"
halts_count="0"
halt_dir="$CLAUDE_PROJECT_DIR/.cascade/halt"
if [ -d "$halt_dir" ]; then
  halt_entries=""
  if [ -f "$session_path" ]; then
    # Halts modified since session start
    while IFS= read -r halt_file; do
      [ -z "$halt_file" ] && continue
      rel_path="${halt_file#"$CLAUDE_PROJECT_DIR"/}"
      # First line of file is "## <halt-code>"
      code="$(head -n 1 "$halt_file" | sed 's/^## //')"
      halt_entries="${halt_entries}$(printf '{"code":"%s","at":"%s"}' "$code" "$rel_path")"$'\n'
    done < <(find "$halt_dir" -name "*.txt" -newer "$session_path" 2>/dev/null)
  fi
  if [ -n "$halt_entries" ]; then
    halts_json="$(echo "$halt_entries" | jq -s '.')"
    halts_count="$(echo "$halts_json" | jq 'length')"
  fi
fi

# Compose the JSONL line
telemetry_line="$(jq -c -n \
  --arg session_id "$session_id" \
  --arg started_at "$started_at" \
  --arg ended_at "$now" \
  --argjson duration "$([ "$duration_seconds" = "null" ] && echo null || echo "$duration_seconds")" \
  --arg exit_reason "$exit_reason" \
  --arg marker "$marker" \
  --arg product "$product" \
  --arg active_milestone "$active_milestone" \
  --arg last_completed_group "$last_completed_group" \
  --argjson compact_cycles "$compact_cycles" \
  --argjson stages_touched "$stages_touched_json" \
  --argjson halts_emitted "$halts_json" \
  --argjson halts_count "$halts_count" \
  '{
    session_id: $session_id,
    session_started_at: (if $started_at == "null" then null else $started_at end),
    session_ended_at: $ended_at,
    duration_seconds: $duration,
    exit_reason: $exit_reason,
    marker: (if $marker == "null" then null else $marker end),
    product: (if $product == "null" then null else $product end),
    active_milestone: (if $active_milestone == "null" then null else $active_milestone end),
    last_completed_group: (if $last_completed_group == "null" then null else $last_completed_group end),
    compact_cycles: $compact_cycles,
    stages_touched: $stages_touched,
    halts_emitted: $halts_emitted,
    halts_count: $halts_count,
    telemetry_schema_version: "0.2-childC"
  }')"

# Append to telemetry file (create dir if needed)
telemetry_dir="$CLAUDE_PROJECT_DIR/.cascade/telemetry"
mkdir -p "$telemetry_dir"
telemetry_path="$telemetry_dir/sessions.jsonl"
echo "$telemetry_line" >> "$telemetry_path"

trace "session-end-telemetry: appended $(echo "$telemetry_line" | wc -c) bytes to $telemetry_path"
exit 0
```

---

## Design notes

### Why async

Per D2.2 §Critical caveats #4: telemetry is the only async-hook use case. The session is ending; blocking on a telemetry write would slow session exit by however long the disk IO takes. Async fire-and-forget is the right shape.

The trade: if the script errors after the session has detached, the founder won't see the error. Acceptable for telemetry — at worst, a few lines are missing from the JSONL. Telemetry is observational, not load-bearing.

### Why no Linear-mirror for telemetry

The telemetry file is local-only. Cross-machine session telemetry is v0.3+ territory (multi-host resume per D2.2 §What this doc does not cover). v0.2 assumes single machine.

### Why a single JSONL file vs per-milestone files

Three options were considered:

- **(a) Single file `.cascade/telemetry/sessions.jsonl`** (what this script does, per `decomposition.md` canonical). Simple to manage; `/retro` filters by milestone. Single point of contention if multiple sessions end concurrently (rare).
- **(b) Per-milestone files `.cascade/session/<milestone>-*.jsonl`** (per `retro-SKILL-amendments.md` continuation 2). Easier `/retro` reads (direct ls); harder to manage across milestone transitions.
- **(c) Per-session files `.cascade/telemetry/<session_id>.jsonl`** (one line per file). Trivial concurrency; awkward for `/retro` to aggregate.

(a) wins on the cascade-wide aggregation case (annual session-discipline reports, longitudinal halt-count metrics). The trade vs (b) is `/retro` needs to filter; jq makes that one-liner. **Surfaced item:** `retro-SKILL-amendments.md` Section 3 needs an apply-time amendment to read from the single file and filter by `active_milestone`.

### Why date handling tries both GNU and BSD flags

macOS ships BSD `date` by default; Linux ships GNU `date`. The two have incompatible flag syntax for parsing ISO 8601 timestamps. The script tries GNU first (`date -u -d`), falls back to BSD (`date -j -u -f`). If neither works (rare; very old systems), `duration_seconds` stays null and the rest of the telemetry record still writes.

### Concurrency note

If two sessions end at the same time, both will append to `sessions.jsonl` concurrently. Linux's POSIX append semantics guarantee atomic appends up to PIPE_BUF (typically 4096 bytes); a single telemetry line is typically <1500 bytes. Below PIPE_BUF, concurrent appends interleave cleanly. Above PIPE_BUF, interleaving could mix bytes from two lines. The schema is designed to stay under 1500 bytes; if a future expansion pushes it higher, switch to file locking. **Surfaced item:** validate line size at apply-time; flag for v0.2.x measurement.

---

## Failing-test seed

There's no `decomposition.md` failing-test-seed line for session-end-telemetry specifically (the script is best-effort + async, so determinism is loose). One could add a `[unit]` test asserting schema compliance, but that's a v0.2.x measurement step. The cascade's smoke surface is satisfied by `test_settings_json_wires_all_events` (which asserts SessionEnd is wired).

For documentation completeness, the apply-time `[unit]` test would look like:

```python
def test_session_end_telemetry_appends_valid_jsonl(tmp_cascade_repo):
    """asserts the hook appends a schema-compliant JSON line to sessions.jsonl."""
    write_run_state(tmp_cascade_repo, {"marker": "TST", "product": "Test"})
    write_session_file(tmp_cascade_repo, "claude-cli-x", {
        "started_at": "2026-05-19T15:00:00Z",
        "compact_cycles": 1,
    })
    result = run_hook(
        "session-end-telemetry.sh",
        payload={"session_id": "claude-cli-x", "reason": "exit"},
        project_dir=tmp_cascade_repo,
    )
    assert result.exit_code == 0
    # Read appended line
    telemetry_path = tmp_cascade_repo / ".cascade/telemetry/sessions.jsonl"
    line = telemetry_path.read_text().strip().splitlines()[-1]
    record = json.loads(line)
    assert record["session_id"] == "claude-cli-x"
    assert record["exit_reason"] == "exit"
    assert record["marker"] == "TST"
    assert record["compact_cycles"] == 1
    assert record["telemetry_schema_version"] == "0.2-childC"
```

---

## Cross-references

- **D2.1 v2 §The cascade:run-state schema** + **D2.1 v2.1** — canonical `.cascade/run-state.json` path the script reads.
- **D2.2 §Hook events table** — `SessionEnd` event semantics + reason payload field.
- **D2.2 §Critical caveats #4** — the async-only rule that this script honors.
- **D2.2 §Open questions item 4** — "Session-end stamping for Linear ticket telemetry" — v0.3 territory; this hook is the v0.2 filesystem-local realization.
- **D2.2 §Compact mechanics** — the `.cascade/session/<session_id>.json` schema the script reads for `compact_cycles`.
- **`retro-SKILL-amendments.md`** (Child 0001-B continuation 2) Section 3 — consumes this hook's output for session-discipline rendering; needs apply-time path amendment per surfaced item above.
- **`decomposition.md`** — canonical `.cascade/telemetry/sessions.jsonl` path this script writes to.
- **`.claude/hooks/_lib.sh`** — sourced for IO and emitter helpers (no emitter is used — async writes no stdout).
- **Parent spec AC-14** — covered by this script + the other six in this session.
