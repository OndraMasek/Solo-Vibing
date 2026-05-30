#!/usr/bin/env bash
# .claude/hooks/stop-orchestrator.sh
#
# Cascade's single Stop hook per D2.2 §Research-step resolution #3.
# Fires on every Stop event (Stop has no matchers).
#
# Responsibilities (in firing order):
#   1. Detect §kill-received-remote: read cascade:run-state.kill_in_progress.
#      If set for any active_stages[] ticket, emit halt + clear flag.
#   2. Detect §manual-halt-pending: read cascade:run-state.manual_halt.
#      If set, emit halt (do NOT clear; founder clears via /cascade-resume).
#   3. Dispatch per-skill completion check: read active_stages[]; for each
#      stage in a "finalize" state, invoke its solo-verify predicate.
#   4. (F-Eng-4 / F-Int-2 surface) Emit factual continuation context for
#      auto-fire chains in Group F: if cascade:run-state.next_chain_step is
#      non-null, emit a factual reason naming the next stage. The model
#      decides whether to Task-invoke; the hook does not command it.
#
# Output: top-level Stop quirk shape per D2.2 §Stop / SubagentStop output
# schema quirk. NO hookSpecificOutput wrapper.
#
# Exit codes: 0 (cascade proceeds, with or without continuation context),
# nonzero is reserved (the script always emits structured JSON and exit 0;
# real "block" semantics live in the JSON's decision field, not the exit code).

set -u

# Source the shared lib
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
. "$SCRIPT_DIR/lib/common.sh"

trace "stop-orchestrator: fired"

# ---- 0. SOL-132 loop-breaker: stop_hook_active guard ----------------------
#
# Every Stop/SubagentStop hook must short-circuit when the runtime is already
# re-invoking it because a prior invocation returned a block decision. Without
# this guard, any block path below (§kill-received-remote, §manual-halt-pending,
# finalize-predicate failures, next_chain_step) can be replayed unbounded and
# hang the session. Reading the payload here also makes the flag available to
# the checks below.

read_hook_payload
if [ "$(jq_field '.stop_hook_active')" = "true" ]; then
  trace "stop-orchestrator: stop_hook_active set; exiting clean to break loop"
  exit 0
fi

# ---- 1. Read run-state (required for every subsequent check) --------------

if ! read_run_state; then
  # No run-state means no active cascade. Stop hook is informational only.
  # Exit 0 with no decision — let the session end normally.
  trace "stop-orchestrator: no run-state; exiting clean"
  exit 0
fi

# ---- 2. §kill-received-remote check ---------------------------------------

kill_target="$(run_state_field '.kill_in_progress')"
if [ -n "$kill_target" ]; then
  # Is this ticket currently active?
  active_tickets="$(run_state_field '.active_stages[]?.ticket' | tr '\n' ' ')"
  if echo " $active_tickets " | grep -q " $kill_target "; then
    kill_at="$(run_state_field '.kill_initiated_at')"
    kill_from="$(run_state_field '.kill_initiated_from // "unknown"')"
    diagnostic="§kill-received-remote: /build-kill received for $kill_target (initiated at $kill_at from $kill_from). The Ralph loop has stopped at the next safe boundary. Queue version was incremented; this ticket is no longer in the active queue. See halt-messages.md §kill-received-remote for recovery options."

    log_halt "§kill-received-remote" "$diagnostic"

    # Clear kill_in_progress and remove ticket from active_stages
    # (atomic write per D2.1 v2 §run-state-as-lock semantics)
    state_path="$CLAUDE_PROJECT_DIR/.cascade/run-state.json"
    tmp_path="${state_path}.tmp"
    echo "$RUN_STATE" \
      | jq --arg t "$kill_target" \
          '.kill_in_progress = null
           | .kill_initiated_at = null
           | .kill_initiated_from = null
           | .active_stages = [.active_stages[]? | select(.ticket != $t)]' \
      > "$tmp_path"
    mv "$tmp_path" "$state_path"
    trace "stop-orchestrator: cleared kill_in_progress for $kill_target"

    emit_stop_block "$diagnostic"
    exit 0
  fi
fi

# ---- 3. §manual-halt-pending check ----------------------------------------

manual_halt="$(run_state_field '.manual_halt')"
if [ -n "$manual_halt" ]; then
  halt_at="$(run_state_field '.manual_halt_at')"
  halt_reason="$(run_state_field '.manual_halt_reason // ""')"
  reason_suffix=""
  if [ -n "$halt_reason" ]; then
    reason_suffix=" Reason: $halt_reason."
  fi
  diagnostic="§manual-halt-pending: /cascade-halt received for $manual_halt (initiated at $halt_at).${reason_suffix} The cascade has paused at the next safe boundary; run /cascade-resume to continue or solo-cascade resume per D4.6 v1.1. See halt-messages.md §manual-halt-pending for recovery options."

  log_halt "§manual-halt-pending" "$diagnostic"
  # Do NOT clear manual_halt — founder clears via /cascade-resume per design
  emit_stop_block "$diagnostic"
  exit 0
fi

# ---- 4. Per-skill completion dispatch -------------------------------------
#
# Stop fires when Claude finishes responding. If a cascade stage was active
# and is now in a "finalize" state (its completion predicates should pass),
# dispatch to solo-verify <stage> <ticket>. On predicate failure, halt.
#
# This is the load-bearing /build finalize gate per D2.2 §Mapping table:
#   `/build finalize: commit + fix-plan-zero + tests passing` → Stop (command).
#
# The dispatch table maps the active stage's name to the solo-verify subcommand.
# v0.2 ships /build finalize only on this surface; other stages' finalize
# predicates fire at their own at-write moments (inside the skill, not at Stop).

active_count="$(echo "$RUN_STATE" | jq -r '.active_stages | length')"
if [ "$active_count" = "0" ]; then
  trace "stop-orchestrator: no active stages; nothing to dispatch"
  # Check for next_chain_step continuation (Group F auto-fire)
  next_step="$(run_state_field '.next_chain_step')"
  if [ -n "$next_step" ]; then
    # F-Eng-4 / F-Int-2 surface: factual continuation context.
    # The hook does NOT command "Task-invoke X" — that's imperative phrasing
    # per D2.2 §Critical caveats #3. Instead, name the next stage factually;
    # the /Chains contract (per D2.3 v1.3) in the relevant skill carries the
    # actual continuation logic. The hook's role is to surface the pointer,
    # not to enforce the invocation.
    diagnostic="The next stage in the auto-fire chain is $next_step per cascade:run-state.next_chain_step. Continue per the /Chains contract in the relevant skill."
    emit_stop_block "$diagnostic"
    exit 0
  fi
  exit 0
fi

# For each active stage, check if it should finalize at this Stop event.
# v0.2 dispatch table:
#   /build (with fix_plan_unchecked_count == 0 in latest backpressure entry)
#     → solo-verify build-finalize <ticket>
# Other stages' completion predicates fire at their own at-write moments;
# this hook does not dispatch them.

failures=""
while IFS= read -r stage_json; do
  stage_name="$(echo "$stage_json" | jq -r '.name')"
  ticket="$(echo "$stage_json" | jq -r '.ticket')"

  case "$stage_name" in
    build)
      # Check whether build is in finalize state: latest backpressure entry's
      # fix_plan_unchecked_count == 0.
      backpressure_path="$CLAUDE_PROJECT_DIR/.ralph/$ticket/backpressure.jsonl"
      if [ ! -f "$backpressure_path" ]; then
        trace "stop-orchestrator: build $ticket has no backpressure log yet; skipping"
        continue
      fi
      last_line="$(tail -n 1 "$backpressure_path")"
      unchecked="$(echo "$last_line" | jq -r '.fix_plan_unchecked_count // -1')"
      if [ "$unchecked" = "0" ]; then
        trace "stop-orchestrator: dispatching solo-verify build-finalize $ticket"
        # solo-verify exits 0 (all passed) or non-zero (halt). Capture output.
        if ! solo_verify_out="$(solo-verify build-finalize "$ticket" 2>&1)"; then
          failures="${failures}${failures:+ ; }build-finalize $ticket: $solo_verify_out"
        fi
      fi
      ;;
    *)
      trace "stop-orchestrator: no Stop-event dispatch for stage=$stage_name"
      ;;
  esac
done < <(echo "$RUN_STATE" | jq -c '.active_stages[]')

if [ -n "$failures" ]; then
  diagnostic="Stop-hook dispatch detected one or more finalize-predicate failures: $failures. The session is paused; address each failure and re-run the relevant skill (typically /build <ticket> --continue) before continuing."
  emit_stop_block "$diagnostic"
  exit 0
fi

# ---- 5. next_chain_step continuation context (Group F auto-fire) ----------
#
# After a compact-recovery scenario in Group F, the post-compact SessionStart
# emits additionalContext with the chain pointer. This Stop hook is a redundant
# safety net: if next_chain_step is still set after the previous turn, surface
# it as factual context. Per F-Int-2 disposition: factual phrasing only.

next_step="$(run_state_field '.next_chain_step')"
if [ -n "$next_step" ]; then
  diagnostic="The next stage in the auto-fire chain is $next_step per cascade:run-state.next_chain_step. Continue per the /Chains contract in the relevant skill. The forcing function is this turn's continuation, not the prose of this reason."
  emit_stop_block "$diagnostic"
  exit 0
fi

# All checks passed; no decision out. The session continues normally.
trace "stop-orchestrator: clean exit"
exit 0
