#!/usr/bin/env bash
# .claude/hooks/session-start-state-restore.sh
#
# Fires on SessionStart with source = startup, resume, or compact.
# Restores cascade state to the new session's context via additionalContext.
#
# Per D2.1 v2.1: canonical run-state at .cascade/run-state.json (repo root).
# Per D2.2: SessionStart re-fires on resume, so this is the right place to
# refresh cascade state (vs PostToolUse which replays from transcript).
#
# Output: hookSpecificOutput wrapper with additionalContext.

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
. "$SCRIPT_DIR/_lib.sh"

trace "session-start-state-restore: fired"

read_hook_payload

# Extract source from payload. SessionStart's payload shape per D2.2:
#   {"source": "startup" | "resume" | "compact" | "clear", "session_id": "...", ...}
source_kind="$(jq_field '.source')"
session_id="$(jq_field '.session_id')"

trace "session-start-state-restore: source=$source_kind session_id=$session_id"

# Read run-state
if ! read_run_state; then
  # No run-state means no cascade context. Emit a minimal banner so the
  # founder knows this session isn't tied to a cascade. Then exit clean.
  emit_additional_context \
"No .cascade/run-state.json found. This session has no active cascade context. If this is a fresh repo, run /onboard to bootstrap. If this is a working repo and run-state was lost, run solo-cascade resume (per D4.6 v1.1) to re-derive."
  exit 0
fi

# Extract canonical fields (per D2.1 v2 schema + D2.3 v1.2 schema additions)
marker="$(run_state_field '.marker')"
product="$(run_state_field '.product // "unset"')"
parent_feature="$(run_state_field '.parent_feature_name // "none"')"
last_group="$(run_state_field '.last_completed_group // "none"')"
last_group_at="$(run_state_field '.last_group_exit_at // "unknown"')"
active_milestone="$(run_state_field '.active_milestone // "none"')"
queue_version="$(run_state_field '.queue_version // 0')"
next_chain_step="$(run_state_field '.next_chain_step // ""')"
manual_halt="$(run_state_field '.manual_halt // ""')"
kill_in_progress="$(run_state_field '.kill_in_progress // ""')"

# Active stages (one per line)
active_stages_summary="$(echo "$RUN_STATE" | jq -r '
  if (.active_stages | length) == 0 then
    "  - (no active stages)"
  else
    .active_stages
    | map("  - \(.name) on \(.ticket) (started \(.started_at // "unknown"))")
    | join("\n")
  end
')"

# Last completed stage's manifest
last_completed_stage_name="$(run_state_field '.last_completed_stage.name // "none"')"
last_completed_manifest_path="$(run_state_field '.last_completed_stage.postcondition_manifest_path // ""')"
last_completed_manifest_sha_full="$(run_state_field '.last_completed_stage.postcondition_manifest_sha256 // ""')"
last_completed_manifest_sha="${last_completed_manifest_sha_full:0:16}"

# Compose the context block per source
context=""
case "$source_kind" in
  startup)
    context="Solo-Vibing cascade context (SessionStart source=startup).

Marker: $marker
Product: $product
Parent feature: $parent_feature
Active milestone: $active_milestone
Queue version: $queue_version

Last completed group: $last_group (at $last_group_at)
Last completed stage: $last_completed_stage_name
Last sealed manifest: $last_completed_manifest_path (sha256: ${last_completed_manifest_sha}...)

Active stages:
$active_stages_summary"
    ;;

  resume)
    # source=resume fires after `claude --resume`. The mid-session hooks have
    # replayed from transcript; this hook re-emits the current run-state for
    # context-freshness. Per D2.2 §Critical caveats #2.
    context="Solo-Vibing cascade context (SessionStart source=resume — session resumed via claude --resume).

Marker: $marker
Product: $product
Parent feature: $parent_feature
Active milestone: $active_milestone
Queue version: $queue_version

Last completed group: $last_group (at $last_group_at)
Last completed stage: $last_completed_stage_name
Last sealed manifest: $last_completed_manifest_path (sha256: ${last_completed_manifest_sha}...)

Active stages:
$active_stages_summary"

    # Surface manual_halt and kill_in_progress flags if present — the resume
    # may be the founder returning to a halted cascade.
    if [ -n "$manual_halt" ]; then
      context="$context

Manual halt is pending for $manual_halt. Run /cascade-resume (or solo-cascade resume per D4.6 v1.1) to clear and continue."
    fi
    if [ -n "$kill_in_progress" ]; then
      context="$context

Kill in progress for $kill_in_progress. The Stop hook orchestrator will clear this at the next safe boundary; the queue_version increment has already taken effect."
    fi
    ;;

  compact)
    # source=compact fires after Claude Code's auto-compact completes.
    # Read the most recent precompact snapshot for fine-grained restoration.
    # Per D2.2 §SessionStart source=compact.

    session_path="$CLAUDE_PROJECT_DIR/.cascade/session/$session_id.json"
    reset_due="false"
    if [ -f "$session_path" ]; then
      reset_due="$(jq -r '.reset_due // false' "$session_path")"
    fi

    if [ "$reset_due" = "true" ]; then
      # Per D2.2 §SessionStart source=compact: "if reset_due == true, return
      # additionalContext signaling 'session reset required' and write a halt
      # diagnostic. The founder is told via the next conversational turn to
      # exit and resume."
      halt_dir="$CLAUDE_PROJECT_DIR/.cascade/halt"
      mkdir -p "$halt_dir"
      cat > "$halt_dir/session-reset-required.txt" <<EOF
## §session-reset-required
Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Session: $session_id
Diagnostic:
The cascade has reached compact_cycle = 2. Per D2.2 §Compact mechanics's max-2-cycles rule, context signal has degraded below the working threshold; a session reset is required.

Recovery:
  Exit this session (Ctrl-D or /exit).
  Run: claude --resume $session_id
  The new session's SessionStart=resume hook will re-hydrate cascade state
  from .cascade/run-state.json; mid-Ralph state is preserved at the last
  safe boundary recorded in .cascade/session/$session_id.json.
---
EOF
      context="Solo-Vibing cascade reset required (SessionStart source=compact, compact_cycle=2).

The session has exceeded the max-2-cycle threshold. Per D2.2's mechanics, context signal has degraded below the working threshold.

To resume:
  1. Exit this session (Ctrl-D or /exit).
  2. Run: claude --resume $session_id
  3. The new session will SessionStart=resume and re-hydrate cascade state.

Marker: $marker
Last completed stage: $last_completed_stage_name
Last safe boundary recorded in .cascade/session/$session_id.json.

Halt diagnostic written to .cascade/halt/session-reset-required.txt."
    else
      # Normal compact recovery — restore via precompact snapshot
      snapshot_glob="$CLAUDE_PROJECT_DIR/.cascade/session/precompact-${session_id}-*.json"
      # Find most recent (lex-sort by filename, take last)
      snapshot_path="$(ls -1 $snapshot_glob 2>/dev/null | tail -n 1 || true)"

      if [ -n "$snapshot_path" ] && [ -f "$snapshot_path" ]; then
        snapshot_summary="$(jq -r '.summary // ""' "$snapshot_path")"
        snapshot_next_step="$(jq -r '.next_chain_step // ""' "$snapshot_path")"

        context="Solo-Vibing cascade context (SessionStart source=compact — context auto-compacted; resuming at safe boundary).

Marker: $marker
Product: $product
Parent feature: $parent_feature
Active milestone: $active_milestone

Last completed stage: $last_completed_stage_name
Last sealed manifest: $last_completed_manifest_path (sha256: ${last_completed_manifest_sha}...)

Precompact snapshot: $snapshot_path

Active stages:
$active_stages_summary"

        if [ -n "$snapshot_summary" ]; then
          context="$context

Snapshot summary:
$snapshot_summary"
        fi

        if [ -n "$snapshot_next_step" ]; then
          # F-Eng-4 / F-Int-2: factual phrasing for the chain pointer.
          # Do NOT issue imperative instructions; describe the state.
          context="$context

The next stage in the auto-fire chain is $snapshot_next_step per the precompact snapshot's next_chain_step field. Continue per the /Chains contract in the relevant skill."
        fi
      else
        # No snapshot — fall back to run-state alone (slight context loss)
        context="Solo-Vibing cascade context (SessionStart source=compact; no precompact snapshot found — falling back to run-state).

Marker: $marker
Product: $product
Last completed stage: $last_completed_stage_name
Last sealed manifest: $last_completed_manifest_path (sha256: ${last_completed_manifest_sha}...)

Active stages:
$active_stages_summary"
      fi
    fi
    ;;

  clear)
    # source=clear is the /clear command. The user explicitly wants a clean
    # slate; emit minimal context (no detailed state restoration).
    context="Solo-Vibing cascade (SessionStart source=clear — /clear invoked).

Marker: $marker
Product: $product
Active milestone: $active_milestone

Use /status (v0.1 founder-fired command) to see current cascade state."
    ;;

  *)
    # Unknown source — emit minimal banner
    context="Solo-Vibing cascade (SessionStart source=$source_kind).

Marker: $marker
Last completed stage: $last_completed_stage_name"
    ;;
esac

# Cap the context at ~3000 chars per the 10000-char additionalContext limit
# (leave headroom for additional hook contributions).
if [ ${#context} -gt 3000 ]; then
  context="${context:0:2900}

[truncated at ~3000 chars; full state in .cascade/run-state.json]"
fi

emit_additional_context "$context"
trace "session-start-state-restore: emitted $(echo "$context" | wc -c) bytes of context"
exit 0
