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
