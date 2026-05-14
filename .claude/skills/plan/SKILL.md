---
name: plan
description: Decompose a sealed parent spec into child tickets with dependency graph and parallelization plan. Invokes the decomposer agent to draft children, then mints them as scope:sealed Linear tickets with blockedBy wiring, writes decomposition.md, transitions parent scope:specified → scope:planned, and Task-invokes /review. Internal cascade stage between /specify and /review — auto-fired by /specify via Task tool, not founder-invoked under the hidden-cascade model. Manual override `/plan <MARKER>-N` available for re-decomposition or debugging. Undecomposable parents halt back to /specify --unseal — no in-skill escape hatch.
---

# plan

Decompose specified parent into child tickets. Internal cascade stage. References rules: `naming.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`. Invokes agent: `decomposer`. Chains to skill via Task tool: `review` (on DONE / DONE_WITH_CONCERNS).

Definitions for `<N>`, `<K>`, `<MARKER>-N-K`, branch names, Linear doc IDs, and file paths: per `naming.md`. This skill does not redefine them.

## Trigger

- Cascade: Task-invoked by /specify on seal (parent label = `scope:specified`).
- Manual override: `/plan <MARKER>-N`, `plan <MARKER>-N`, `decompose <MARKER>-N`, `split <MARKER>-N` — re-decomposition or debugging. Not founder-documented. Manual fire against a parent already at `scope:planned` requires archived children (founder's responsibility) before re-decomposition.
<!-- accept-oversize mode removed: undecomposable parents halt to /specify --unseal per halt-messages §undecomposable-parent. -->

## Behavior

1. **Preconditions** (any failure halts with `BLOCKED` per `completion-status.md`; halt-card per `docs/templates/halt-messages.md`).
   - Parent ticket <MARKER>-N exists and carries label `scope:specified` per `scope-labels.md`.
     - `scope:planned` observed without manual override → `BLOCKED`: "<MARKER>-N already planned. Use manual override only after archiving prior children, or iterate via /review guidance."
     - No scope label → `BLOCKED`: "<MARKER>-N isn't specified yet. Run /specify first."
   - Spec markdown exists at `docs/specs/NNNN-<slug>/spec.md` per `naming.md`. Missing → `NEEDS_CONTEXT`.
   - Four-hat document `[<MARKER>-DOC-NNNN] four-hat: <MARKER>-N <title>` per `naming.md` exists, and every finding in its most recent iteration has a recorded resolution (Incorporate / Defer / Reject). Unresolved findings → `BLOCKED`. (Normally enforced by /specify at seal time; checked here as defense in depth.)
   - Marker resolvable from `docs/.solo-config.json`. Unset → `NEEDS_CONTEXT`.

2. **Task-invoke decomposer** per `[SOL-AGENT] decomposer`. Inputs: path to parent spec, marker, parent ticket ID (for K-numbering context). The agent reads the spec end-to-end, classifies each draft child as vertical or horizontal, and surfaces chunking concerns as findings.

   Returns two blocks:
   - `## Children` — per-child draft in proposed build order. Each child carries: title, classification (vertical | horizontal, with one-line justification when horizontal), description, AC subset (by parent-spec position), failing-test seed subset, blockers (sibling K-numbers or "none").
   - `## Findings` — optional. Chunking concerns, missing-AC-coverage flags, scope-resistance signals. Auditor-stance per `auditor-stance.md`.

3. **Map decomposer findings to /plan status** per `completion-status.md` §Agent contract.
   - Zero findings → proceed to step 4.
   - All findings below halt threshold (no `high` severity; no `missing-edge-case` against AC coverage; no scope-resistance markers) → proceed to step 4; findings forwarded to the summary on `DONE_WITH_CONCERNS`.
   - Any finding at or above halt threshold → `BLOCKED`. No Linear writes. Halt-card per `docs/templates/halt-messages.md` with a single recommended next action and alternatives. Recommendation logic:
     - **Incomplete failing-test seed** (decomposer flagged AC-X not covered by parent's seed) → recommend `/specify <MARKER>-N --continue` (expand seed). Alternative: `/specify <MARKER>-N --unseal` if multiple AC have seed gaps (systemic spec issue). Last resort: remove AC-X from spec (defer feature).
     - **Undecomposable parent** (decomposer flagged scope-resistance: AC resists chunking into Code-Claude-sized vertical or horizontal slices) → recommend `/specify <MARKER>-N --unseal` to split the parent into two parent specs. No in-skill escape hatch — undecomposability is a spec defect.
     - **Scope-out-of-bounds chunking** (decomposer's draft child would touch surfaces explicitly listed as out-of-scope in the spec) → recommend `/specify <MARKER>-N --unseal` to expand scope explicitly, or trim AC.

4. **Wire dependencies and detect parallelization waves.**
   - For each draft child K, parse the decomposer's `Blockers` field; map to Linear `blockedBy` relationships among siblings.
   - Pair-wise wave detection: two children are parallel-eligible unless (a) a `blockedBy` relation exists between them, or (b) they likely touch overlapping target surfaces (heuristic from decomposer description + spec scope). Group into waves. When in doubt, mark sequential — false parallelism causes merge conflicts; missed parallelism just costs wall-clock time.

5. **Same-turn write batch** per `write-discipline.md`:
   - Linear: batch-create all children with `scope:sealed` per `scope-labels.md`, parentId set, blockedBy wired, title and description from the decomposer draft, branch name `<MARKER>-N-<slug>-K` per `naming.md`.
   - Linear: post parallelization-plan comment on parent (wave list). Append the worktree-pattern block when Wave 1 has ≥2 parallel-eligible children AND `parallelization.enabled = true` in `docs/.solo-config.json` (see `commands/config.md` for config semantics, pending Batch 3 — currently inlined defaults):

     ~~~
     To run Wave 1 in parallel:
       git worktree add ../<repo>-<MARKER>-N-1 <MARKER>-N-<slug>-1
       git worktree add ../<repo>-<MARKER>-N-2 <MARKER>-N-<slug>-2
     Open one Code-Claude session per worktree. Serializing in one worktree is also fine.
     ~~~

     If `parallelization.enabled = false`, render the wave structure but suppress the worktree block — sequential build is the founder's chosen mode.

   - Linear: atomic parent label transition `scope:specified` → `scope:planned` per `scope-labels.md` (prior label removed in the same write).
   - Filesystem: write `docs/specs/NNNN-<slug>/decomposition.md` (template below).
   - All writes batched same-turn per `write-discipline.md`. Partial-failure handling per `write-discipline.md` §Partial failure: marker file at `docs/specs/NNNN-<slug>/.plan.sync.pending`; surface `BLOCKED` with a sync-retry hint pointing at manual re-fire of /plan.

6. **Heavyweight-child-spec hint** (Q2 conditional offer). For any child whose decomposer-draft description exceeds 250 words OR contains an "API contract" / "UX flow" section, append to the parallelization comment: "<MARKER>-N-K has substantial design surface — `/specify <MARKER>-N-K` will produce a heavyweight child spec before /build."

7. **Task-invoke /review** per audit decision #9 (chaining via Task tool, not labels). /review owns parallelization audit, decomposition critique, and any iteration-mode handoff back to /plan.

## Decomposition.md template

Written at `docs/specs/NNNN-<slug>/decomposition.md` alongside `spec.md`. Single same-turn write per step 5. Re-written in place on iteration (no archive; iteration tracking lives on the /review document).

~~~markdown
# Decomposition: <MARKER>-N <title>

> Parent: <MARKER>-N
> Children: <count>
> Plan run: YYYY-MM-DD (iteration <N> if not first)

## Chunking rationale
<1–2 paragraphs from the decomposer's output, explaining why these N children, why this granularity. Surface the journey segments / user-outcome units that drove the split.>

## Children
- **<MARKER>-N-1** — <title>. Vertical / horizontal (one-line justification if horizontal). Covers AC: <list>.
- **<MARKER>-N-2** — ...
- ...

## Dependency graph
```

<MARKER>-N-1 ──┬──> <MARKER>-N-3
<MARKER>-N-2 ──┘

```
(or text equivalent: `<MARKER>-N-3 blocked by [<MARKER>-N-1, <MARKER>-N-2]`)

## Parallelization map
- Wave 1 (parallel): <MARKER>-N-1, <MARKER>-N-2
- Wave 2 (after Wave 1): <MARKER>-N-3

## Rejected alternatives (optional)
- <only when the decomposer surfaced a near-miss worth recording>
~~~

## Iteration mode (when invoked with guidance from /review)

Invoked when /review surfaces findings that require re-decomposition. Guidance shape: `[{type, locus, suggestion}, ...]` per `auditor-stance.md`.

1. Load existing children for parent.
2. Re-invoke decomposer with the same spec PLUS the /review guidance as additional context. The agent re-emits Children + Findings, taking guidance into account.
3. Diff old children vs new children: identify merged-away siblings, redrafted siblings, new siblings, downgraded-to-sequential pairs.
4. Re-derive dependencies + parallelization waves on the new set.
5. Update affected child tickets in place per `write-discipline.md` — don't re-batch-create. Linear `update` for changed children; `delete` for merged-away; `create` for new. All same-turn.
6. Re-write `decomposition.md` in place.
7. Task-invoke /review again. If /review returns `DONE`, terminate; otherwise iterate (bounded by /review's iteration cap).

## Outputs

| Artifact | Location |
|---|---|
| Child tickets | scope:sealed, parentId set, blockedBy wired |
| Decomposition rationale | `docs/specs/NNNN-<slug>/decomposition.md` |
| Parallelization plan | Comment on parent ticket |
| Updated parent label | scope:specified → scope:planned |

## Completion status

Per `completion-status.md`. v0.1 mappings:

- `DONE` — decomposer returned zero findings; children created with `scope:sealed`; decomposition.md written; parallelization comment posted; parent transitioned to `scope:planned`; /review Task-invocation returned `DONE`.
- `DONE_WITH_CONCERNS` — completed end-to-end, but: decomposer surfaced sub-threshold concerns (forwarded to summary); horizontal-slice fallback used because vertical was infeasible; iteration mode applied /review guidance and converged.
- `BLOCKED` — preconditions failed; decomposer surfaced halt-threshold findings (incomplete failing-test seed, undecomposable parent, scope-resistance); Linear write failed (partial-failure marker dropped per `write-discipline.md`); /review returned `BLOCKED`.
- `NEEDS_CONTEXT` — spec markdown missing at expected path; `docs/.solo-config.json` `marker` unset; decomposer surfaced a question requiring founder input the skill cannot resolve.

## Chains

- **On `DONE` / `DONE_WITH_CONCERNS`**: Task-invokes /review per audit decision #9. /review chains downstream to /update-linear (with absorbed /push-to-chat renderer per audit decision #3). The founder sees a single summary card at cascade end.
- **On `BLOCKED` / `NEEDS_CONTEXT`**: no chain. Halt-card per `docs/templates/halt-messages.md` with a single recommended next action and alternatives.

## Notes

**State machine.** Parent: `scope:specified → scope:planned` (this skill). Child: `(Backlog) → scope:sealed` (this skill). `scope:built` is /build's terminal label. See `scope-labels.md` for full state machine, transition ownership, and refusal protocol on stale labels.

**Why decomposer-then-mint, not inline.** The chunking decision is judgment-heavy and shape-stable (per `[SOL-AGENT] decomposer` model recommendation: opus). The minting decision is mechanical Linear-API plumbing. Keeping them in separate primitives lets the agent run on a heavier model for judgment while the skill stays cheap.

**Conservative parallelization.** When in doubt about whether two children can run in parallel, mark sequential. /review's parallelization audit is the safety net for misses, and merge conflicts are far more expensive than serial wall-clock time.

**Parallel Wave 1 is opportunity, not obligation.** v0.1 CLAUDE.md line: "/plan identifies parallel-eligible children; opening multiple Code-Claude sessions is manual. Serializing is fine. v0.2 will spawn subagents automatically."

**Heavyweight child specs (Q2 conditional).** Default no. The 250-word OR API/UX heuristic is applied to the decomposer's draft description, not founder perception of complexity. Surface a /specify offer only when the threshold trips.

**Children's failing-test seeds are strict subsets of the parent's seed.** No fabrication inside /plan. Gap detection (AC-X not covered by parent's seed) is a /specify defect surfaced by the decomposer as a finding; /plan halts with `BLOCKED` pointing back to /specify. Never iterate on the seed inside /plan.

**Vertical preference biases /plan toward shorter dependency chains.** Vertical slices share less internal state than horizontal layers. Parallelization opportunities often increase as a side effect — don't engineer for this; let it emerge from the decomposer's classification rubric.

**Mixed-mode parents.** A parent spec with some user-visible AC and some pure-infrastructure AC gets a mixed-mode plan: vertical children for user-visible AC, horizontal children for infra AC, dependencies wired so infrastructure precedes vertical work. The decomposer handles classification; /plan handles dependency wiring.

**No oversize escape hatch in v0.1.** The pre-v0.1 `--accept-oversize` mode minted a `scope:sealed-oversize` child that was never in the state machine; /build refused to fire on it. The mode is removed. Undecomposable parents halt to `/specify <MARKER>-N --unseal` per halt-messages §undecomposable-parent — splitting the parent into two parents is the correct fix.

## Open questions (deferred to v1.1+)

<!-- scope:sealed-oversize label entry removed: --accept-oversize mode dropped in v0.1 audit. -->
- **Manual override semantics formalization.** Manual /plan <MARKER>-N against `scope:planned` parent currently requires founder to archive children out-of-band. A formal `--archive-children` flag is v1.1 territory.
- **Parallelization heuristic precision.** Pair-wise overlap detection is heuristic (decomposer description + spec scope). AST-level file-prediction is v1.1+ work.
- **Auto-iteration cap from /plan side.** v0.1 caps iteration via /review's halt protocol; /plan doesn't impose its own cap. Revisit if cascades thrash.
- **Skill → command transformation.** Like the rest of the internal-only cascade, /plan may end up as a command in a future refactor if internal-only auto-fire makes "skill" semantics overkill. Not v0.1.
