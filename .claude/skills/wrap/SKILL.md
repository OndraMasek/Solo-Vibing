---
name: wrap
description: Build-session close ritual. Invoked by /build on build-reviewer-pass (Task tool, finalize phase) — verifies tests green, verifies scope, pushes the branch, transitions child Linear state In Progress → Done, posts a session summary, checks parent completion. If all of the parent's children are Done, transitions the parent and Task-invokes /verify or /retro per workflow knobs. No manual Code-Claude session in the canonical v1 flow. Not user-invoked in normal operation. Manual override `/wrap <MARKER>-N-K` for debugging.
---

# wrap

Build-session close ritual. Verifies child completion, persists state, advances the parent if all children are done. References rules: `naming.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`. Invoked by /build via the Task tool. Chains to skills via Task tool: `verify`, `retro`.

## Trigger

Invoked by `/build` on build-reviewer-pass, in /build's finalize phase, via the Task tool (per audit decision #1). /build has, by this point: spawned Ralph, gotten a `built` exit, run the `build-reviewer` agent, and gotten a clean review. /wrap is the next step — commit, push, wave-merge (if applicable), state transition, parent-completion check.

Manual override: `/wrap <MARKER>-N-K` — debugging only. There is no manual Code-Claude session in the canonical v1 flow; /wrap is not a founder-fired session-end ritual.

Resume-merge: `/wrap <MARKER>-N-K --resume-merge` — re-run step 6 (wave-merge) after the founder has resolved a `§wave-merge-conflict` halt. Skips re-running test/scope verification and re-pushing.

## Behavior

1. **Verify AC green.** Re-run the child's failing-test seed (now expected passing). Any test still red → `BLOCKED` per `completion-status.md`, halt-card per `docs/templates/halt-messages.md`: "<MARKER>-N-K has X failing tests." /build's finalize phase surfaces this; the path back is `/build <MARKER>-N-K --continue`.

2. **Verify scope.** Changed files match the child's expected surface — no files outside scope. Out-of-scope changes → `BLOCKED`, halt-card: "<MARKER>-N-K modified files outside its scope: <list>." auditor-stance per `auditor-stance.md` — state the finding as a fact, list the loci.

3. **Commit + push** per `naming.md` §Branch names:
   - Stage all changes.
   - Commit message: `[<MARKER>] <MARKER>-N-K: <child title> — green`.
   - Push branch `<MARKER>-N-<slug>-K`.

4. **Post session summary on child ticket:**

   ~~~
   /wrap complete. <MARKER>-N-K is green and pushed.

   * Tests: <X>/<X> passing
   * Files changed: <N> (<one-line summary>)
   * Branch: <MARKER>-N-<slug>-K
   * Commits: <count>
   ~~~

5. **Transition child Linear state** In Progress → Done per `scope-labels.md` (atomic transition per `write-discipline.md`). The child was set to In Progress by `/start`, which /build Task-invokes at its preconditions step — so the canonical-flow source state is always In Progress.

   The off-path Todo case occurs only on **manual `/wrap <MARKER>-N-K`** invocations against a child that was never `/start`-ed (debugging or ad-hoc tracking — never a /build-chained flow, since /build's contract guarantees /start has run). In that case /wrap also flips Todo → Done in one step. This is documented as a graceful path for the manual override; it cannot fire from /build.

   `scope:built` on the child is set by **/build**, not /wrap, per `scope-labels.md` §Transition ownership. /wrap moves the Linear-native state (In Progress → Done); /build moves the `scope:*` label (`scope:sealed → scope:built`). These are distinct and both happen in /build's finalize phase — /build sets the label, then Task-invokes /wrap which sets the state.

6. **Wave-merge** (load-bearing for multi-wave plans). Read `decomposition.md` to identify which wave this child belongs to and whether other siblings in the same wave are also Done.
   - **Wave incomplete** (other siblings in this wave still building) → no merge, no chain. Post wave-progress comment.
   - **Wave complete** (this child finishes its wave, AND a later wave exists) → merge this wave's child branches into the default branch:
     ~~~
     git fetch
     git switch <default-branch>
     git merge --no-ff <MARKER>-N-<slug>-K1 <MARKER>-N-<slug>-K2 ...
     git push
     ~~~
     On `git merge` failure → `BLOCKED` per `§wave-merge-conflict`. The founder resolves the conflict and re-runs `/wrap <MARKER>-N-K --resume-merge`.
   - **Final wave complete** (last wave, all children of this parent Done) → also merge to default (no later wave to enable, but the parent ships through default). Same merge logic, same halt pattern on conflict.

   The merge is non-skippable for multi-wave plans because Wave-(N+1) child branches are created from default; without the Wave-N merge they cannot see Wave-N's code.

7. **Check parent completion.** Query the parent's children:
   - **Not all done** → post on the parent: "<MARKER>-N-K complete. <X> of <Y> children done. Next Wave-eligible: <MARKER>-N-M." No chain. (Wave-merge in step 6 has already run if this child finished its wave.)
   - **All done AND `workflow.verify = true`** → Task-invoke `/verify <MARKER>-N` per audit decision #9. The parent stays In Progress; /verify owns the transition (Done on pass, fix-children on fail).
   - **All done AND `workflow.verify = false`** → transition the parent's Linear state to Done. If `workflow.auto_retro = true`, Task-invoke `/retro <MARKER>-N`.

   Steps 4–7 Linear writes batch same-turn per `write-discipline.md`. The git merge in step 6 is a separate operation that precedes the Linear writes.

## Same-turn write rules

Per `write-discipline.md`:
- Git commit + push: same turn.
- Linear writes (session summary comment + child state transition + parent comment or transition): batched same-turn.

## Outputs

| Artifact | Location |
|---|---|
| Commit + pushed branch | Git remote |
| Session summary | Child ticket comment |
| Child state | In Progress → Done (Todo → Done if /start was skipped) |
| Parent state (if all done) | → Done, or held by /verify |
| Next Wave-eligible hint | Parent ticket comment |

## Completion status

Per `completion-status.md`:

- `DONE` — tests green; committed and pushed; child → Done; parent completion checked and advanced per workflow knobs.
- `DONE_WITH_CONCERNS` — completed, but: the child was Todo (not In Progress) at /wrap start (the /start step was skipped); or next Wave-eligible siblings exist without a parallel-session setup.
- `BLOCKED` — step 1 red tests; step 2 out-of-scope file changes. Halt-card per `docs/templates/halt-messages.md`; /build's finalize phase surfaces it and the path back is `/build <MARKER>-N-K --continue`.
- `NEEDS_CONTEXT` — branch name doesn't match the `<MARKER>-N-<slug>-K` convention per `naming.md`; child ticket missing; parent ticket missing.

## Chains

Per audit decision #9 — all via the Task tool:
- All children done + `workflow.verify = true` → Task-invoke /verify. /verify owns the parent → Done transition.
- All children done + `workflow.verify = false` → parent → Done; Task-invoke /retro if `workflow.auto_retro = true`.
- Not all done → no chain; the next Wave child is started by the founder via `/build <MARKER>-N-M` (v0.2 subagent mode picks automatically).

/wrap is itself Task-invoked by /build (it does not run standalone in the canonical flow), so /wrap's status propagates back up: a /wrap `BLOCKED` becomes /build's `BLOCKED`, a /wrap `DONE` lets /build return `DONE`. See `[SOL-SKILL] build` finalize phase steps 6–7.

## Notes

**Trigger rewiring (audit "Trigger rewiring" §).** Pre-extraction /wrap was "Code-Claude session-end ritual. Internal: Code-Claude invokes at end of build session." The canonical v1 flow has no manual Code-Claude session — /build runs Ralph as a blackbox, and on build-reviewer-pass /build Task-invokes /wrap. /wrap's trigger is now "invoked by /build on build-reviewer-pass." The manual `/wrap <MARKER>-N-K` override is kept for debugging only.

**Why /wrap stays a skill** (audit decision #1, "Skills that stay skills" list). The founder explicitly rejected absorbing /wrap into /build — "wrap is quite complex, merging makes /build a monster." /wrap carries real logic: test re-verification, scope verification, the parent-completion check, and the /verify-vs-/retro routing. It stays a separate skill that /build Task-invokes.

**Label vs state — distinct, both in /build's finalize phase.** `scope:built` is a `scope:*` label set by /build per `scope-labels.md`. `In Progress → Done` is a Linear-native state set by /wrap. /build's finalize phase sets the label, then Task-invokes /wrap which sets the state. /wrap never touches `scope:*` labels.

**Test verification (step 1) is non-negotiable.** Red tests = no /wrap completion = no commit. The TDD gate is enforced here even though the `build-reviewer` agent already passed — the agent reviews the diff against the spec; /wrap re-runs the actual tests. Belt and suspenders.

**Scope verification (step 2)** catches a Ralph run that drifted. A child for "email validation" that modified the auth flow halts the wrap. Cheap insurance — the `build-reviewer` agent has a scope-boundary axis too, but /wrap's check is on the actual changed-file set.

**Pairs with `/start`** (now `[SOL-CMD] start`). /start opens the build-session window (Todo → In Progress); /wrap closes it (In Progress → Done + commit + push + parent check). Both are Task-invoked by /build — /start at preconditions, /wrap at finalize.

## Open questions (deferred to v1.1+)

- **v0.2 subagent parallelism.** v0.1 wraps one child per /build run. With subagent parallelism, /wrap fires per child completing and the parent-completion check converges asynchronously.
- **Next-Wave auto-start.** Currently "not all done" posts a hint and stops. v0.2 subagent mode picks the next Wave child automatically.
