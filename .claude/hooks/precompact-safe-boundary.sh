#!/usr/bin/env bash
# .claude/hooks/precompact-safe-boundary.sh
#
# PreCompact safe-boundary check per D2.2 §Compact mechanics §PreCompact.
# Manages three-band threshold model: increment compact_cycles, check
# safe-boundary, snapshot or defer/reset as appropriate.
#
# Output: Stop-quirk-style top-level fields on block; exit 0 silent on allow.
# Halt codes (written to .cascade/halt/):
#   §session-reset-required  (compact_cycles >= 2)
#   §compact-deferred-unsafe (not at a safe boundary)

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
. "$SCRIPT_DIR/_lib.sh"

trace "precompact-safe-boundary: fired"

read_hook_payload

# PreCompact payload shape per D2.2:
#   {"trigger": "manual" | "auto", "custom_instructions": "..." | null, "session_id": "..."}
session_id="$(jq_field '.session_id')"
trigger="$(jq_field '.trigger // "auto"')"

if [ -z "$session_id" ]; then
  # Without a session_id we can't track per-session state. Allow the compact;
  # the cascade will degrade gracefully (no snapshot, no cycle counting).
  trace "precompact-safe-boundary: no session_id; allowing compact"
  exit 0
fi

trace "precompact-safe-boundary: session_id=$session_id trigger=$trigger"

# Read or initialize session file
session_path="$CLAUDE_PROJECT_DIR/.cascade/session/$session_id.json"
mkdir -p "$(dirname "$session_path")"

if [ -f "$session_path" ]; then
  current_cycles="$(jq -r '.compact_cycles // 0' "$session_path")"
else
  # Initialize with started_at = now (best-effort; the real session-start
  # init would happen elsewhere if it existed). Defensive default.
  cat > "$session_path" <<EOF
{
  "session_id": "$session_id",
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "compact_cycles": 0,
  "last_safe_boundary": null,
  "reset_due": false
}
EOF
  current_cycles="0"
fi

new_cycles="$((current_cycles + 1))"
trace "precompact-safe-boundary: current_cycles=$current_cycles new_cycles=$new_cycles"

# ---- Cycle >= 2: reset required --------------------------------------------

if [ "$new_cycles" -ge 2 ]; then
  # Set reset_due:true and block. The cascade continues; the next safe-boundary
  # check (downstream of this hook) triggers the full reset.
  tmp_path="${session_path}.tmp"
  jq --argjson cycles "$new_cycles" \
     --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
     '. + {compact_cycles: $cycles, reset_due: true, reset_marked_at: $now}' \
     "$session_path" > "$tmp_path"
  mv "$tmp_path" "$session_path"

  diagnostic="Session reset required — compact_cycles would be $new_cycles (max allowed: 1). Per D2.2 §Compact mechanics's max-2-cycles rule, context signal has degraded; this compact is blocked. The cascade halts at the next safe boundary; founder picks up with claude --resume $session_id."
  log_halt "§session-reset-required" "$diagnostic"
  emit_stop_block "$diagnostic"
  exit 0
fi

# ---- Cycle 0 → 1 or 1 → 2: check safe boundary -----------------------------

# Safe-boundary function: derived from cascade:run-state.active_stages[].
# If zero active stages (everything either completed or never started), safe.
# Else, the stages-active list determines safety per D2.2 §Safe-boundary list.

is_safe_boundary="true"
if read_run_state 2>/dev/null; then
  # Per D2.2 §Safe-boundary list "Not safe" cases:
  # - Mid-Ralph-iteration (a build stage in active_stages without sealed manifest)
  # - During a four-hat in progress (review stage active)
  # - During update-linear writes
  # - During any stage whose verifier predicates have not yet been recomputed
  #
  # Simplified function: if any active stage exists, the boundary is unsafe
  # by default. The within-group safe-boundary nuances (per D2.3 v1.2's table)
  # require richer state than v0.2's run-state schema carries.
  #
  # Future refinement (v0.2.x): per-stage safety flags written by skills at
  # known safe points (e.g., between Ralph iterations).

  active_count="$(echo "$RUN_STATE" | jq -r '.active_stages | length')"
  if [ "$active_count" != "0" ]; then
    is_safe_boundary="false"
    trace "precompact-safe-boundary: $active_count active stages; boundary unsafe"
  else
    trace "precompact-safe-boundary: no active stages; boundary safe"
  fi
fi

# ---- Unsafe boundary: defer ------------------------------------------------

if [ "$is_safe_boundary" = "false" ]; then
  # Write deferral marker per D2.2
  deferral_path="$CLAUDE_PROJECT_DIR/.cascade/session/compact-deferred.json"
  jq -n \
    --arg session_id "$session_id" \
    --arg at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --argjson cycles "$new_cycles" \
    '{session_id: $session_id, deferred_at: $at, compact_cycles_attempted: $cycles}' \
    > "$deferral_path"

  diagnostic="Compact deferred — mid-task. The cascade has at least one active stage with unsealed manifest; auto-compact would lose work-in-progress. The compact will retry at the next safe boundary (after the active stages seal their manifests)."
  log_halt "§compact-deferred-unsafe" "$diagnostic"
  emit_stop_block "$diagnostic"
  exit 0
fi

# ---- Safe boundary: snapshot and allow -------------------------------------

# Per D2.2 §Compact mechanics step 3 + D2.3 v1.2 §Auto-fire compact behaviour step 2:
# snapshot cascade:run-state summary to .cascade/session/precompact-<id>-<ts>.json
# WITH the new field next_chain_step (the chain pointer for compact recovery).

snapshot_ts="$(date -u +%Y%m%dT%H%M%SZ)"
snapshot_path="$CLAUDE_PROJECT_DIR/.cascade/session/precompact-${session_id}-${snapshot_ts}.json"

# Derive next_chain_step from cascade:run-state.next_chain_step (already populated
# by the per-stage skill at safe boundaries in Group F per D2.3 v1.2 §Auto-fire
# compact behaviour step 3).
next_chain_step="null"
last_completed_stage="null"
marker="null"
if [ -n "${RUN_STATE:-}" ]; then
  next_chain_step="$(echo "$RUN_STATE" | jq -c '.next_chain_step // null')"
  last_completed_stage="$(echo "$RUN_STATE" | jq -c '.last_completed_stage // null')"
  marker="$(echo "$RUN_STATE" | jq -c '.marker // null')"
fi

# Compose the snapshot. The "summary" field is a short factual block the
# SessionStart=compact hook will read.
summary="Pre-compact snapshot at ${snapshot_ts}. Marker: $(echo "$marker" | tr -d '"'). Last completed stage: $(echo "$last_completed_stage" | jq -r '.name // "none"'). compact_cycles: $new_cycles."

jq -n \
  --arg session_id "$session_id" \
  --arg at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --argjson cycles "$new_cycles" \
  --argjson next_chain_step "$next_chain_step" \
  --argjson last_completed_stage "$last_completed_stage" \
  --argjson marker "$marker" \
  --arg summary "$summary" \
  '{
    session_id: $session_id,
    snapshot_at: $at,
    compact_cycles_post: $cycles,
    summary: $summary,
    next_chain_step: $next_chain_step,
    last_completed_stage: $last_completed_stage,
    marker: $marker
  }' > "$snapshot_path"

# Update session file with incremented counter + last_safe_boundary
tmp_path="${session_path}.tmp"
jq --argjson cycles "$new_cycles" \
   --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
   --arg snapshot "$snapshot_path" \
   '. + {compact_cycles: $cycles, last_compact_at: $now, last_precompact_snapshot: $snapshot}' \
   "$session_path" > "$tmp_path"
mv "$tmp_path" "$session_path"

trace "precompact-safe-boundary: snapshot written to $snapshot_path; allowing compact"
exit 0
