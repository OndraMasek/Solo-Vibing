# `.claude/hooks/stop-orchestrator.sh` — the single Stop-hook orchestrator

**Status:** Patch-ready new file. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing`.

**Scope:** the cascade's single Stop hook per D2.2 §Research-step resolution #3. Fires on every `Stop` event (no matcher; Stop has no matchers per D2.2 §Hook events table). Dispatches to per-skill completion predicates by reading `cascade:run-state.active_stages[]`; handles the `kill_in_progress` and `manual_halt` flags per Child 0001-B continuation 1's `/build` `/Chains` "Interaction with sidecar commands" subsection (F-Int-3 disposition).

This is also the F-Eng-4 / F-Int-2 surface for `next_chain_step` Task-invoke: in Group F auto-fire chains, the orchestrator reads `cascade:run-state.next_chain_step` after a within-group safe boundary and emits factual-phrasing context for the model to continue the chain. Per D2.2 §Critical caveats #3 + D2.3 v1.2 four-hat review §F-Int-2: the `reason` string is FACTUAL; the cascade's forcing function is the `decision: block` itself + the model's compliance with the post-compact/post-stop context, NOT the prose of `reason`.

**v0.1 reconciliation:** none. v0.1 has no `.claude/hooks/` per `repo-state-summary.md` Part 2.

---

## Output shape

Stop event uses the top-level-fields-only quirk per D2.2 §Stop / SubagentStop output schema quirk. No `hookSpecificOutput` wrapper:

```json
{"decision": "block", "reason": "<factual diagnostic>"}
```

The lib's `emit_stop_block` handles the shape. The script's only decision is whether to call it (halt) or exit 0 (proceed).

---

## Halt-card text (embedded in script; authored here for `halt-messages.md` apply pass)

Per Child 0001-B continuation 1 Surfaced item #4 + the handoff prompt: the two halt codes `§kill-received-remote` and `§manual-halt-pending` are referenced in Child 0001-B continuation 1's `/build` amendment §Interaction with sidecar commands subsection but were not in v0.1 nor in Child A's `halt-messages-append.md`. This session authors them; the hook script's diagnostic text becomes the halt-card content.

### `§kill-received-remote`

```markdown
## §kill-received-remote

**When fired.** A sidecar `/build-kill <ticket>` invocation has set
`cascade:run-state.kill_in_progress = "<ticket>"` AND incremented `queue_version`.
The Group F chat (Claude Code) was running Ralph for the same ticket when the
Stop-hook orchestrator read the flag at the next safe boundary.

**Diagnostic context.** The active ticket, the kill timestamp (from
`cascade:run-state.kill_initiated_at`), the originating chat surface
(`cascade:run-state.kill_initiated_from`, typically `"sidecar"` or `"chat-Claude"`).

**Recovery.** None required for the cascade — the kill was intentional. The
orchestrator clears `cascade:run-state.kill_in_progress`, removes the ticket
from `active_stages[]`, and the founder picks up either by:

  - Opening a new chat for the next queued ticket (the `queue_version` increment
    means the killed ticket is no longer in the queue).
  - Running `/cascade-halt` to halt the cascade entirely (sets `manual_halt`).
  - Running `/build <ticket> --resume` if the kill was a mistake (re-queues
    the ticket; `queue_version` increments again).

The Stop hook itself takes no recovery action beyond clearing `kill_in_progress`
and surfacing this card. The cascade's continuation is the founder's next
deliberate input.
```

### `§manual-halt-pending`

```markdown
## §manual-halt-pending

**When fired.** A `/cascade-halt` invocation (founder-initiated; not
`/build-kill`) has set `cascade:run-state.manual_halt = "<ticket-or-marker>"`.
The Stop-hook orchestrator read the flag at the next safe boundary.

**Diagnostic context.** The active ticket or marker, the halt timestamp (from
`cascade:run-state.manual_halt_at`), the halt reason if the founder supplied
one via `/cascade-halt --reason="<text>"` (`cascade:run-state.manual_halt_reason`).

**Recovery.** The halt is intentional. To resume the cascade:

  - Run `/cascade-resume` (or `solo-cascade resume` per D4.6 v1.1) to re-derive
    the chat-end card and continue.
  - Clear the flag manually via direct edit to `.cascade/run-state.json` if
    the halt should be retired without resumption (advanced; rarely needed).

The Stop hook itself takes no recovery action beyond surfacing this card and
preserving the `manual_halt` flag. The flag persists until the founder runs
`/cascade-resume` or clears it manually; the next chat opened detects it
during paste-verification (per D2.3 v1.3 §Handoff verification predicate)
and re-surfaces this card.

**Interaction with `kill_in_progress`.** The two flags are mutually exclusive
by convention; `/cascade-halt` errors out if `kill_in_progress` is non-null
(founder must `/build-kill` first or wait for the kill to complete). v0.2 ships
two-step; v0.2.x may chain per F-Usr-2's queued amendment.
```

These two halt-card stanzas fold into `docs/templates/halt-messages.md` at apply-time alongside Child A's `halt-messages-append.md` batch. **Surfaced item.**

---

## Script content

```bash
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
# shellcheck source=_lib.sh
. "$SCRIPT_DIR/_lib.sh"

trace "stop-orchestrator: fired"

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
```

---

## Design notes

### Why the orchestrator clears `kill_in_progress` but not `manual_halt`

`kill_in_progress` is a one-shot signal: it says "the sidecar requested this ticket be killed; the Group F chat should stop." Once the Group F chat sees the flag and stops, the signal has been delivered; clearing it prevents the next session from re-firing the same halt. The kill's downstream effects (queue_version increment, ticket removal) are durable; only the in-flight signal clears.

`manual_halt` is a sticky signal: it says "the cascade is paused until the founder explicitly resumes." The hook deliberately doesn't clear it. The founder's `/cascade-resume` (or `solo-cascade resume`) is the only path that clears the flag — anywhere else clearing it would defeat the halt's purpose.

### Why dispatch lives in the orchestrator, not in per-skill Stop hooks

Per D2.2 §Research-step resolution #3: "one Stop hook, not several. The single hook orchestrates: Ralph's `fix_plan_unchecked_count == 0` check, the build manifest's verifier predicates, and any session-level discipline checks. One decision out. This is the cleanest way to avoid the multi-hook conflict surface and dodges anthropics/claude-code#10412 (the plugin Stop-hook bug)." The orchestrator pattern is mandatory; per-skill Stop hooks are forbidden.

### Why `next_chain_step` continuation is factual, not imperative

Per D2.2 §Critical caveats #3: "imperative system instructions in stdout can trigger Claude's prompt-injection defenses." Per D2.3 v1.2 four-hat review §F-Int-2: the forcing function for chain continuation is the model's compliance with the post-compact/post-stop context, NOT the prose of `reason`. The hook says "the next stage is X"; the `/Chains` contract in the relevant skill carries the actual continuation logic. v0.2 ships this hint form; v0.2.x measurement (M-5 per F-Rev-1's deferral) will validate whether the chain-resumption reliability rate is acceptable.

### Solo-verify integration

The orchestrator shells out to `solo-verify build-finalize <ticket>` for the load-bearing /build finalize check. `solo-verify` is the Child 0001-D deliverable; this script depends on it being installed and on `$PATH`. **Surfaced item:** the dispatch fails silently (skips) if `solo-verify` is absent — acceptable for v0.2 (Child 0001-D's session ships solo-verify before this session's hooks are wired in production) but worth documenting.

### Why the script exits 0 unconditionally

Stop's halt semantics live in the JSON's `decision: block` field, not in the exit code. Exit 0 means "the hook ran"; the JSON tells Claude Code whether to continue or block. The `set -u` guard catches missing variable references at script-time; missing file references are handled by `read_run_state`'s graceful return.

---

## Failing-test seed

Per `decomposition.md` Child 0001-C failing-test-seed list:

```python
def test_stop_orchestrator_dispatches_correctly(tmp_cascade_repo, mock_solo_verify):
    """
    asserts the orchestrator routes to the right per-skill predicate based on
    `cascade:run-state` state; covers AC-14.
    """
    # Set up run-state with /build active and fix_plan_unchecked_count=0
    write_run_state(tmp_cascade_repo, {
        "active_stages": [{"name": "build", "ticket": "TST-42"}],
        "kill_in_progress": None,
        "manual_halt": None,
    })
    write_backpressure(tmp_cascade_repo, "TST-42", {"fix_plan_unchecked_count": 0})

    # Invoke the hook with an empty Stop payload
    result = run_hook(
        "stop-orchestrator.sh",
        payload={"stop_hook_active": False, "last_assistant_message": ""},
        project_dir=tmp_cascade_repo,
    )

    # Assert solo-verify build-finalize was invoked
    assert mock_solo_verify.calls == [("build-finalize", "TST-42")]
    # Assert clean exit (mock solo-verify returned 0)
    assert result.exit_code == 0
    assert result.stdout == ""  # no decision block

def test_stop_orchestrator_halts_on_kill_in_progress(tmp_cascade_repo):
    """asserts §kill-received-remote fires on kill_in_progress set."""
    write_run_state(tmp_cascade_repo, {
        "active_stages": [{"name": "build", "ticket": "TST-42"}],
        "kill_in_progress": "TST-42",
        "kill_initiated_at": "2026-05-19T15:00:00Z",
        "kill_initiated_from": "sidecar",
    })
    result = run_hook("stop-orchestrator.sh", payload={}, project_dir=tmp_cascade_repo)
    output = json.loads(result.stdout)
    assert output["decision"] == "block"
    assert "§kill-received-remote" in output["reason"]
    # Assert kill_in_progress was cleared
    state = read_run_state(tmp_cascade_repo)
    assert state["kill_in_progress"] is None

def test_stop_orchestrator_halts_on_manual_halt(tmp_cascade_repo):
    """asserts §manual-halt-pending fires on manual_halt set; flag is NOT cleared."""
    write_run_state(tmp_cascade_repo, {
        "active_stages": [],
        "manual_halt": "TST-42",
        "manual_halt_at": "2026-05-19T15:30:00Z",
    })
    result = run_hook("stop-orchestrator.sh", payload={}, project_dir=tmp_cascade_repo)
    output = json.loads(result.stdout)
    assert output["decision"] == "block"
    assert "§manual-halt-pending" in output["reason"]
    # Assert manual_halt was NOT cleared
    state = read_run_state(tmp_cascade_repo)
    assert state["manual_halt"] == "TST-42"
```

---

## Cross-references

- **D2.1 v2.1 §The `cascade:run-state` schema** — canonical `.cascade/run-state.json` path the script reads.
- **D2.2 §Research-step resolution #3** — binding for the single-Stop-hook orchestrator pattern.
- **D2.2 §Stop / SubagentStop output schema quirk** — top-level-fields-only output shape the script emits.
- **D2.2 §Critical caveats #3** — imperative-vs-factual phrasing constraint for `reason` strings.
- **D2.2 §Mapping table** `/build finalize` row — the solo-verify build-finalize dispatch this script invokes.
- **D2.3 v1.2 §Auto-fire compact behaviour** + §Group F per-skill semantics — the `next_chain_step` mechanic this script reads.
- **D2.3 v1.2 four-hat review §F-Int-2** — factual-phrasing pattern for Stop-hook `reason`.
- **D2.3 v1.2 four-hat review §F-Int-3** — `/build-kill` sidecar semantics that produce `kill_in_progress`.
- **D2.3 v1.3 §Handoff verification predicate** — the cross-session check that re-surfaces `§manual-halt-pending` if the founder doesn't return.
- **D4.2 `/build-kill` spec** (carried forward in v1.2 §Group F per-skill semantics) — the binding for `kill_in_progress` + `queue_version` increment.
- **D4.6 v1.1 §CLI surface** — `solo-cascade resume` clears `manual_halt` per the recovery flow.
- **Child 0001-B continuation 1 `/build` amendment §Interaction with sidecar commands** — the upstream contract this script enforces.
- **Child 0001-B continuation 1 Surfaced item #4** — flag for `§kill-received-remote` and `§manual-halt-pending` halt-card authoring, resolved in this file.
- **Child 0001-D** `tools/solo-verify` — the CLI this script shells out to for `build-finalize`.
- **`.claude/hooks/_lib.sh`** — sourced for IO and emitter helpers.
- **Parent spec AC-14** — covered by this script + the other six in this session.
