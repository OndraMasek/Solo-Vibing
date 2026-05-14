---
name: verify
description: Manual acceptance walkthrough after all child tickets wrap. Founder confirms each parent AC pass/fail/skip/defer; on failure, Task-invokes the diagnoser agent per failed AC to produce root-cause findings plus fix-child mini-specs, then mints fix-children with scope:sealed (per scope-labels.md's /verify-fix exception). On full pass, transitions parent to Done and Task-invokes /retro when configured. Inserted between /wrap (last child) and parent → Done when workflow.verify is enabled. Manual override `/verify <MARKER>-N` for debugging or retroactive verification of a Done parent.
---

# verify

Manual acceptance walkthrough. Gate between mechanical test-pass (/wrap) and parent → Done. Catches "tests green, UX broken." References rules: `naming.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`. Invokes agent: `diagnoser`. Chains to skill via Task tool: `retro` (on full pass when config enables).

## Operating posture

`auditor-stance.md` applies verbatim. /verify-specific extensions:

- **Human-eyes gate.** Demand evidence; do not infer from code shape. The founder owns every verdict — /verify proposes verification steps and diagnoses failures, never decides pass/fail.
- **One AC at a time.** No grouped "AC-1 through AC-3 look good" — each AC gets its own walkthrough block and its own verdict.
- **Concrete verification steps.** For each AC, propose 1–3 steps tied to the spec's Design/UX flow or Failing-test seed. Not "try clicking around" — name the user action and the expected observable.
- **Founder verdicts (PASS / FAIL / SKIP / DEFER) recorded verbatim.** /verify never overrides.
- **On founder PASS that conflicts with diagnoser's suspicion (rare):** record both verbatim in the verify-report's Notes section. Founder's verdict stands; the note exists so future audits can revisit.

Forbidden phrasing (auditor-stance.md §State findings as facts + §No LGTM closures applied to /verify): "Looks like it's working", "Probably fine to mark pass", "Almost there / mostly works / close enough", "I think this passes", "Great work / looks great / nice job". /verify is an audit artifact, not a celebration.

## Trigger

- Cascade: Task-invoked by /wrap on the last child of parent **if** `workflow.verify = true` in `docs/.solo-config.json` (see `commands/config.md`, pending Batch 3).
- Manual: `/verify <MARKER>-N` — debugging or retroactive verification on a Done parent.

## Behavior

1. **Preconditions** (any failure halts with `BLOCKED` or `NEEDS_CONTEXT` per `completion-status.md`; halt-card per `docs/templates/halt-messages.md`).
   - Parent ticket <MARKER>-N exists. Label = `scope:planned` per `scope-labels.md` for normal cascade fire; `scope:planned` with parent state = Done acceptable for manual retroactive invocation.
   - All child tickets carry `scope:built` per `scope-labels.md`. Any child not yet built → `BLOCKED`: "child <MARKER>-N-K is not yet built; cannot run acceptance walkthrough."
   - Spec markdown exists at `docs/specs/NNNN-<slug>/spec.md` per `naming.md`. Missing → `NEEDS_CONTEXT`.
   - Children's `/wrap` session summaries exist as comments on each child ticket (needed to source commit/test summaries). Missing → `NEEDS_CONTEXT`: "rerun /wrap on <MARKER>-N-K to surface session summary."

2. **Read config knob.** If `workflow.verify = false` AND this is a cascade fire (not manual), /verify is a no-op — return `DONE` with a note. Manual invocation always proceeds.

3. **Load context.**
   - Parent ticket description + AC checkboxes (source-of-truth for AC list).
   - Spec markdown.
   - Each child's /wrap session-summary comment (commit count, test counts, files changed).
   - `docs/constitution.md` (passed to diagnoser per agent contract when failures occur).

4. **Render acceptance walkthrough.** For each AC in parent, present:

   ~~~
   AC-<n>: <AC text>

   Implemented in: <list of contributing children>
   Tests: <X/Y passing across children>
   Files changed: <one-line summary>

   Walk through this manually:
   1. <verification step derived from spec's Design/UX or failing-test seed>
   2. <verification step>

   Pass / Fail / Skip / Defer?
   ~~~

   Wait for founder verdict per AC. Record verbatim with any founder notes. Verdicts allowed: `PASS`, `FAIL`, `SKIP` (AC doesn't apply in practice — note why), `DEFER` (needs later human review but founder wants the cascade to advance now).

5. **Diagnose failures** (per AC marked FAIL). For each failed AC, Task-invoke `[SOL-AGENT] diagnoser`. Inputs: child ticket ID (the contributing child where the failure surfaces, or the most-implicated one when shared), failing-AC text + founder notes, parent spec path.

   The agent returns:
   - `## Findings` — root-cause analysis with severity (`low` | `med` | `high`). Auditor-stance per `auditor-stance.md`.
   - `## Artifact` — fix-child mini-spec (omitted when severity is `high` and root cause is spec-level).

6. **Map diagnoser output to /verify status and fix-child minting** per `completion-status.md` §Agent contract:
   - **All findings `low` or `med`** (any severity below `high`) → mint a fix-child per finding's `## Artifact` block. Continue to step 7.
   - **Any finding `high` with spec-level root cause** (diagnoser omitted the `## Artifact` section) → no fix-child. Halt with `BLOCKED`. Halt-card per `docs/templates/halt-messages.md` recommends `/specify <MARKER>-N --unseal` to re-spec the gap.
   - **Diagnoser surfaces unrelated findings** (post-build issues outside the failed AC) → record in verify-report Notes; do not auto-mint fix-children for unrelated issues. Founder's call.

7. **Mint fix-children** (same-turn batch per `write-discipline.md`) for each `med`-or-`low` fix from step 6:
   - Title: `[<MARKER>] fix <MARKER>-N AC-<n>: <verb-noun from diagnoser>`.
   - Label: `scope:sealed` per `scope-labels.md` /verify-fix exception (transition ownership: /plan owns scope:sealed normally; /verify-fix is the sole exception per the rule). The label is set directly because fix-children are mechanically derived from existing spec + failure evidence — they're scope-of-the-original-spec retries, not new feature work.
   - parentId: <MARKER>-N (same parent).
   - Description: failed AC + diagnoser's `## Findings` block (verbatim) + diagnoser's `## Artifact` mini-spec.
   - Branch: `<MARKER>-N-<slug>-fix-<K>` per `naming.md` (K monotonic within fix-children of this parent).

8. **Compile verify-report.** Write `docs/specs/NNNN-<slug>/verify-report.md` (template below). On re-run (the file already exists from a prior /verify pass), first archive the current file:
   - Scan `docs/specs/NNNN-<slug>/archive/` for existing `verify-report-v<N>.md`.
   - Set `next = max(N) + 1`, or `1` if no archives exist.
   - Move (copy then write fresh) current `verify-report.md` → `archive/verify-report-v<next>.md`.
   - Then write the fresh `verify-report.md` for this run.

   The archive pattern mirrors `archive/spec-v<N>.md` from /specify --unseal; same-turn write batch per `write-discipline.md` (archive copy + fresh write together).

9. **Outcome routing.**
   - **All AC pass** (or pass + skip + defer, no FAIL): transition parent state → Done. If `workflow.auto_retro = true`, Task-invoke /retro per audit decision #9. `DONE` or `DONE_WITH_CONCERNS` per status mapping.
   - **Any AC FAIL with fix-children minted**: parent stays In Progress with `scope:planned`. Post comment on parent: "/verify failed on <N> AC. Fix children: <MARKER>-N-fix-1, <MARKER>-N-fix-2. Resume build by running each through /build." `BLOCKED`.
   - **All AC skip or defer** (no PASS or FAIL): no transition. Post comment: "/verify completed with no PASS or FAIL. Re-run when ready to evaluate." `DONE_WITH_CONCERNS`.

10. **Update parent ticket** with verify-report link in Artifacts section regardless of outcome. Batched same-turn with step 9 writes per `write-discipline.md`.

## Verify-report template

Written at `docs/specs/NNNN-<slug>/verify-report.md`. Single same-turn write.

~~~markdown
# Verify report: <MARKER>-N <title>

> Date: YYYY-MM-DD
> Parent: <MARKER>-N
> Children: <MARKER>-N-1, <MARKER>-N-2, ...

## Outcome

<pass | partial | fail>

## AC results

- [X] AC-1: PASS — <founder notes if any>
- [X] AC-2: PASS
- [ ] AC-3: FAIL — <founder notes>
  - Diagnoser severity: med
  - Fix-child: <MARKER>-N-fix-1
- [~] AC-4: SKIP — <reason>
- [?] AC-5: DEFER — <reason>

## Diagnosed fixes (if any failures)

<one block per FAIL, verbatim from diagnoser's ## Findings + ## Artifact>

## Notes

<founder-PASS-disagrees-with-diagnostic cases, deferred items, unrelated findings the diagnoser surfaced that aren't being auto-fixed>
~~~

## Outputs

| Artifact | Location |
|---|---|
| Verify report | `docs/specs/NNNN-<slug>/verify-report.md` |
| Fix-child tickets (on FAIL) | Linear children, `scope:sealed` per /verify-fix exception, parentId = <MARKER>-N |
| Parent state | → Done (on full pass) or comment (on FAIL / all-SKIP) |

## Completion status

Per `completion-status.md`. v0.1 mappings:

- `DONE` — walkthrough complete; all AC PASS (no FAIL, no SKIP, no DEFER); verify-report written; parent → Done; /retro Task-invoked if config enables.
- `DONE_WITH_CONCERNS` — walkthrough complete with SKIP/DEFER entries; or a founder-PASS that conflicted with the diagnoser's suspicion (recorded in Notes); or unrelated diagnoser findings surfaced that aren't being auto-fixed.
- `BLOCKED` — any AC marked FAIL with fix-children minted (parent stays In Progress; founder resumes via /build on the fix-children); spec-level FAIL with no fix-child (`/specify <MARKER>-N --unseal` recommended).
- `NEEDS_CONTEXT` — parent ticket missing; spec markdown missing; children's /wrap session summaries missing.

## Chains

- **All pass**: Task-invoke /retro if `workflow.auto_retro = true` per audit decision #9. /retro is terminal (no further cascade). Otherwise terminal.
- **FAIL with fix-children**: terminal for this /verify run. Founder resumes by Task-invoking /build on each fix-child (manually fired per the /build user-invoked rule).
- **Spec-level FAIL**: terminal. Halt-card recommends `/specify <MARKER>-N --unseal`.
- **All skip/defer**: terminal. Founder re-runs /verify when ready.

## Notes

**/verify is the human-eyes gate /wrap can't provide.** /wrap verifies tests are green (mechanical); /verify verifies the feature actually works (perceptual). Without /verify, "tests green, UX broken" ships.

**Why pass/fail/skip/defer (four verdicts, not two).** Skip and Defer are escape valves: Skip = "AC doesn't apply in practice; document why." Defer = "needs human review later but I want to advance the cascade for now." Forcing binary judgments produces silent false-positives.

**Fix-children get `scope:sealed` directly.** This is the only sanctioned exception to "only /plan sets `scope:sealed`" — codified in `scope-labels.md` §Transition ownership. Diagnoser-derived fix-children are scope-of-the-original-spec retries; the /plan decomposition pass has already happened.

**Walkthrough is interactive but bounded** — one chat exchange per AC. For 10+ AC parents, /verify can span multiple chat turns; state is implicit (verify-report.md captures progress per AC as the founder answers).

**Config-driven cascade behavior** (see `commands/config.md`, pending Batch 3). `mode: yolo` skips /verify entirely (founder opt-in to mechanical-only verification). `mode: cascade-only` (default) honors `workflow.verify`. `mode: interactive` always runs /verify even with `workflow.verify = false`.

**Retroactive /verify on Done parents is allowed via manual invocation.** Useful for audits or when external feedback surfaces bugs post-cascade. Produces a verify-report that timestamps the post-hoc review; can chain to fix-children if failures found.

## Open questions (deferred to v1.1+)

- **Quasi-automated UI walkthroughs.** Browser MCP or screenshot tools could pre-walk each AC and present evidence rather than asking the founder to manually verify. v0.2 candidate.
- **Bounded chat span.** Long verify runs (10+ AC) currently span multiple chat turns implicitly; a formal `--resume` mode is v1.1.
- **Skill → command transformation.** Like the rest of the cascade, /verify may end up as a command in Batch 3 (the founder fires it; the skill is mostly orchestration). Currently tracked in batches doc §3 Batch 3.
- **Diagnoser-severity threshold tuning.** v0.1 mints fix-children for any `med`-or-`low` finding. v1.1 may add a config knob to require founder confirmation per fix-child for `low` severity.
