# `.claude/hooks/precompact-safe-boundary.sh` — PreCompact safe-boundary check

**Status:** Patch-ready new file. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing`.

**Scope:** wraps D2.2 §Compact mechanics §PreCompact as a `PreCompact` hook. Manages the three-band threshold model: increments `compact_cycles` in `.cascade/session/<session_id>.json`; if `>= 2`, sets `reset_due: true` and blocks the compact with "session reset required"; else checks the safe-boundary function; if safe, writes a precompact snapshot and allows the compact; if not safe, blocks with "compact deferred — mid-task."

**Deviation from handoff.** The Child 0001-B continuation 2 handoff prompt enumerated **six** hook scripts, omitting PreCompact. The `decomposition.md` row's "Files in scope" also names six. However:

- **D2.2 §Compact mechanics §PreCompact** specifies substantive PreCompact logic (increment + safe-boundary + snapshot + reset_due flagging) that must run in a hook.
- The failing-test seed `test_settings_json_wires_all_events` asserts `.claude/settings.json` contains entries for **PreToolUse, PostToolUse, SubagentStop, SessionStart, SessionEnd, PreCompact, Stop** — PreCompact explicitly enumerated.
- The `decomposition.md` settings.json description states "SessionStart, SessionEnd, PreCompact wired per D2.2 §Hook events table" — but no script is named for PreCompact.

The cleanest disposition is to **author the seventh script** so v0.2's hook infrastructure is complete end-to-end. The alternative (wiring PreCompact to another script) doesn't fit — PreCompact's predicate is distinct from Stop, SessionStart, SessionEnd. Authoring it here is consistent with the spec's intent.

**Surfaced item.** The handoff said "six hook scripts"; this session ships seven. The decomposition.md row should be amended at apply-time to enumerate the seventh script, and the spec's AC-14 will need a corresponding adjustment to "deterministic shell predicates" enumeration if the AC names specific scripts (it currently does not; AC-14 names categories: "pre-flight provenance check, pyramid-tampering check fired at /build, four-hat objection-coverage check fired on SubagentStop" — none of these is PreCompact's, so AC-14 is silent on it and the seventh script is unblocked by AC text).

**v0.1 reconciliation:** none. v0.1 has no `.claude/hooks/` per `repo-state-summary.md` Part 2.

---

## Output shape

PreCompact uses the standard `hookSpecificOutput` wrapper per D2.2 §Hook events table. Per D2.2 §Compact mechanics §PreCompact, the script returns the Stop-style top-level fields for blocking (per Anthropic's hooks reference convention for PreCompact "decision" handling, which uses the same top-level `decision`/`reason` shape as Stop):

```json
{"decision": "block", "reason": "Session reset required — too many compact cycles. Halt at next safe boundary."}
```

On allow: exit 0 with no stdout.

**Note on output shape ambiguity.** D2.2 §Stop / SubagentStop output schema quirk explicitly names Stop, SubagentStop, StopFailure as the events with the top-level quirk. PreCompact is not in that list — D2.2's PreCompact code blocks use `{"decision": "block", "reason": "..."}` shape, matching the Stop quirk. The cleanest interpretation: PreCompact follows the same quirk pattern (since blocking a compact is structurally similar to blocking a Stop). This script uses the top-level shape; the executing apply session should validate against Claude Code v2.0.76+ at script-test-time and surface any deviation. **Surfaced item.**

---

## Matcher

Wired in `.claude/settings.json` to PreCompact with no source matchers (catches both `manual` and `auto` triggers per D2.2 §Hook events table).

---

## Script content

```bash
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
```

---

## Design notes

### Why the safe-boundary check is conservative

D2.2 §Safe-boundary list enumerates per-stage safety cases ("after /wrap completes", "between subagent invocations", etc.). The current v0.2 run-state schema doesn't carry enough information to distinguish "build stage active mid-Ralph" from "build stage active at iteration-boundary" — both look like an entry in `active_stages[]`. The conservative implementation: any active stage → unsafe boundary.

This is over-restrictive (a build at iteration-boundary IS safe per D2.3 v1.2 §Within-group safe boundaries) but it errs toward correctness: a compact deferral is recoverable (the next safe boundary will retry); a compact-mid-Ralph is not.

**Surfaced item:** v0.2.x should add per-stage safety flags to run-state (e.g., `active_stages[N].at_safe_boundary: true`) written by skills at known safe points. This unlocks compact-at-iteration-boundary in Group F per D2.3 v1.2's promise.

### Why the script writes session-file initialization on first run

D2.2 §Compact mechanics §PreCompact assumes `.cascade/session/<session_id>.json` already exists (presumably initialized by the SessionStart hook, though no v0.2 spec names a SessionStart-writes-session-file responsibility). Defensive initialization here: if the file is absent, write it with sane defaults. The next PreCompact firing reads the file normally.

**Surfaced item:** decide at v0.2.x whether the session-file initialization should move to `session-start-state-restore.sh`'s `source=startup` branch. Cleanly attributing the file's owner is worth a one-paragraph clarification. For v0.2 walking-skeleton, defensive initialization in both hooks is acceptable.

### Why `next_chain_step` is read from run-state, not computed here

Per D2.3 v1.2 §Auto-fire compact behaviour step 3: `next_chain_step` is written to `cascade:run-state.json` by the per-stage skill at safe boundaries in Group F. PreCompact's role is to read it and propagate it into the precompact snapshot — not to compute it. If `next_chain_step` is null in run-state, the snapshot reflects that.

### `§session-reset-required` halt-card

The halt-card text for `§session-reset-required` is owned by Child A's `halt-messages-append.md` (per the F-2 fix's full halt-card surface). This script's diagnostic feeds into the existing card; no new card is authored here.

`§compact-deferred-unsafe` is novel — not in Child A's append. **Surfaced item:** add a halt-card stanza for `§compact-deferred-unsafe` at apply-time. Suggested text:

```markdown
## §compact-deferred-unsafe

**When fired.** PreCompact detected mid-cascade activity (one or more entries
in cascade:run-state.active_stages[] with unsealed manifests). The auto-compact
is blocked; the cascade continues; the next safe-boundary check will retry.

**Recovery.** None required — the deferral is intentional. The compact will
fire automatically when the cascade reaches the next safe boundary (typically
within minutes, at most one Ralph iteration). If the cascade runs out of
context before reaching a safe boundary, manual /compact at a safe boundary
will succeed.
```

---

## Failing-test seed

```python
def test_precompact_safe_boundary_blocks_on_cycle_2(tmp_cascade_repo):
    """asserts cycle 1→2 sets reset_due:true and emits block."""
    write_session_file(tmp_cascade_repo, "claude-cli-x", {
        "compact_cycles": 1,
        "reset_due": False,
    })
    result = run_hook(
        "precompact-safe-boundary.sh",
        payload={"session_id": "claude-cli-x", "trigger": "auto"},
        project_dir=tmp_cascade_repo,
    )
    output = json.loads(result.stdout)
    assert output["decision"] == "block"
    assert "Session reset required" in output["reason"]
    # session file has reset_due now
    session = read_session_file(tmp_cascade_repo, "claude-cli-x")
    assert session["reset_due"] is True
    assert session["compact_cycles"] == 2

def test_precompact_safe_boundary_defers_on_unsafe(tmp_cascade_repo):
    """asserts compact deferral when active_stages is non-empty."""
    write_run_state(tmp_cascade_repo, {
        "active_stages": [{"name": "build", "ticket": "TST-42"}],
    })
    write_session_file(tmp_cascade_repo, "claude-cli-x", {"compact_cycles": 0})
    result = run_hook("precompact-safe-boundary.sh",
                      payload={"session_id": "claude-cli-x", "trigger": "auto"},
                      project_dir=tmp_cascade_repo)
    output = json.loads(result.stdout)
    assert output["decision"] == "block"
    assert "Compact deferred" in output["reason"]

def test_precompact_safe_boundary_snapshots_on_safe(tmp_cascade_repo):
    """asserts safe-boundary case writes snapshot and exits 0."""
    write_run_state(tmp_cascade_repo, {
        "active_stages": [],
        "marker": "TST",
    })
    write_session_file(tmp_cascade_repo, "claude-cli-x", {"compact_cycles": 0})
    result = run_hook("precompact-safe-boundary.sh",
                      payload={"session_id": "claude-cli-x", "trigger": "auto"},
                      project_dir=tmp_cascade_repo)
    assert result.exit_code == 0
    assert result.stdout == ""  # no block
    # snapshot written
    snapshots = list((tmp_cascade_repo / ".cascade/session").glob("precompact-claude-cli-x-*.json"))
    assert len(snapshots) == 1
```

---

## Cross-references

- **D2.1 v2 §The cascade:run-state schema** + **D2.1 v2.1** — canonical `.cascade/run-state.json` path.
- **D2.2 §Hook events table** — `PreCompact` event semantics + `trigger`/`custom_instructions` payload.
- **D2.2 §Compact mechanics §PreCompact** — the binding for the increment + safe-boundary + snapshot logic this script implements.
- **D2.2 §Safe-boundary list** — the "safe" / "not safe" enumeration this script (conservatively) approximates.
- **D2.2 §Stop / SubagentStop output schema quirk** — the top-level-fields output shape this script uses for block decisions (PreCompact follows the same convention per code blocks in D2.2).
- **D2.3 v1.2 §Auto-fire compact behaviour** — the binding for `next_chain_step` write into the snapshot.
- **D2.3 v1.2 §Within-group safe boundaries** — the per-stage safety enumeration that v0.2.x will need per-stage flags to honor.
- **`.claude/hooks/_lib.sh`** — sourced for IO and emitter helpers.
- **`session-start-state-restore-hook.md`** (this session) — the SessionStart=compact branch that reads this hook's snapshot.
- **Child A `halt-messages-append.md`** — the `§session-reset-required` parent card; `§compact-deferred-unsafe` needs apply-time addition per surfaced item.
- **Parent spec AC-14** — covered by this script + the other six in this session; AC-14 does not enumerate specific scripts, so the seventh script does not violate AC text.
