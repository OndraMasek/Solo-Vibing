---
name: review
description: Static-analysis pass + cascade router between /plan and /update-linear. Internal cascade stage. Task-invoked by /plan after decomposition. Runs eleven checks, applies stability + cap + per-type routing, executes autonomous fixes (parallelization downgrades, low-stakes dep ADR filing), composes halt-cards when iteration won't converge. Routes one of three ways: iterate (Task-invoke /plan with guidance), halt (Task-invoke /update-linear with halt-messages to render), or clean (Task-invoke /update-linear to consolidate). Not user-invoked. Manual override `/review <MARKER>-N` for debugging.
---

# review

Static analysis + cascade router. Eleven check categories + stability/cap rules + four-condition low-stakes dep test + halt-card composition. References rules: `naming.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`. Chains to skills via Task tool: `plan` (iterate), `update-linear` (clean or halt).

## Operating posture

/review is the cascade's auditor. Voice and shape of findings: per `auditor-stance.md` — state findings as facts, no preamble, no LGTM closures, one finding per `{type, locus}`, mark hypotheses with `uncertain:`, terse not curt. That rule is auto-loaded and authoritative; /review does not restate it.

**/review-specific extensions to the rule:**

- Every finding routes to exactly one of three buckets — **iterate-/plan**, **autonomous-fix**, **spec-halt**. There is no "soft suggestion" bucket; the rule's "no `could consider`" guidance maps here to "every finding has a routing decision."
- Routing decisions are deterministic (stability + cap + per-type rules). State them; never hedge.
- When the stability rule triggers spec-halt for the same `(type, locus)` across iterations, name both review docs explicitly: *"Same finding present in [<MARKER>-DOC-NNNN] review iter 1 and iter 2 — stability rule triggers spec-halt."*
- Autonomous fixes get recorded with their before/after state, not their justification — the justification lives in the check rules, not per-instance.

## Trigger

Internal: Task-invoked by `/plan` immediately after decomposition completes (parent label = `scope:planned` per `scope-labels.md`).
Manual override: `/review <MARKER>-N` — debugging only, not user-documented.

## Behavior

1. Load parent ticket, all children with `parentId = parent`, parent spec markdown, all prior review documents for this parent, and `docs/constitution.md`. Determine `iteration_count` from the number of **completed** prior review sections (Findings + Routing Applied + Autonomous Fixes + Halts Composed all present). Aborted mid-section runs don't count.

2. Run eleven checks. Each finding: `{type, severity, locus, suggestion}` per `auditor-stance.md`'s finding shape.

   | # | Check | Severity | Default routing |
   |---|-------|----------|-----------------|
   | a | AC coverage — every parent AC covered by ≥1 child | hard | iterate-/plan |
   | b | Failing-test seed completeness — derivable from parent seed | hard | **spec-halt** |
   | c | Dependency cycle in `blockedBy` graph | hard | iterate-/plan |
   | d | Scope-out compliance — children don't reintroduce out-of-scope items | hard | iterate-/plan |
   | e | Parallelization audit — parallel-eligible pairs don't share target | warn | autonomous-fix |
   | f | Budget estimate — each child ≤200k token estimate | warn | iterate-/plan |
   | g | ADR-reversal scan | warn | **spec-halt** |
   | h | New-dependency scan | warn | four-condition test below |
   | i | Vertical-slice audit — user-visible output OR horizontal-required justification | warn | iterate-/plan |
   | j | Constitution-check — spec or children don't violate `docs/constitution.md` | hard | **spec-halt** |
   | k | Completeness — no `[NEEDS CLARIFICATION: ...]` markers, no stub sections, all AC have text, failing-test seed isn't TODO | hard | **spec-halt** |

3. For each finding, apply routing rules. Final bucket: **iterate-/plan**, **autonomous-fix**, or **spec-halt**.

   - **Stability check (all types):** `(type, locus)` present in any prior review doc → spec-halt regardless of default.
   - **Cap check (all types):** `iteration_count >= 3` and finding still present → spec-halt regardless of default.
   - **Per-type routing after stability/cap:**
     - a, c, d, f, i → iterate-/plan with suggestion
     - b, g, j, k → spec-halt (never iterates)
     - e → autonomous-fix (downgrade pair to sequential in the parent's parallelization comment)
     - h → four-condition test → pass: autonomous-fix (auto-file ADR); fail: spec-halt

4. **Four-condition low-stakes dep test for check h** (all four required): language-ecosystem standard utility; adds no runtime architectural lock-in; not a peer-competitor to an existing dep; project has ≥1 prior ADR. Any condition fails → spec-halt.

5. **Check j detail (constitution-check):** scan parent spec markdown, all child descriptions, decomposition.md, and generated artifacts against `docs/constitution.md`. Match against Core principles, Process rules, Architectural constraints, Decision-making triggers. Each violation → one finding with locus + verbatim-quoted violated principle; halt-card uses the relevant pattern in `docs/templates/halt-messages.md`. A constitution version mismatch is not itself a violation — only contradiction of the new principles is.

6. **Check k detail (completeness):** scan parent spec markdown for `[NEEDS CLARIFICATION: ...]` markers, empty AC checkboxes, failing-test-seed TODO/placeholder entries, unfilled `<...>` placeholders (excluding intentional template markers). Aggregate all incompleteness into one halt-card per parent (not one per location), with a bullet list of every incomplete locus.

7. **Execute actions:**
   - iterate-/plan findings → collect into a guidance list `[{type, locus, suggestion}, ...]` per `auditor-stance.md`'s tuple shape.
   - autonomous-fix on check e → update the parent's parallelization comment in place per `write-discipline.md`, mark the pair sequential; track in `autonomous_fixes_applied`.
   - autonomous-fix on check h → draft an ADR at `docs/decisions/NNNN-<slug>.md` (NNNN allocated per `counter-allocation.md` from the `adr` counter — scan `docs/decisions/`); create Linear document `[<MARKER>-DOC-NNNN] adr: <slug>` (NNNN allocated from the `doc` counter — scan Linear) with `Status: Accepted-Autonomous`; track in `autonomous_fixes_applied`.
   - spec-halt findings → compose a halt-card per `docs/templates/halt-messages.md`, picking the pattern that matches the check type.

8. **Write review document:** append a new dated section to `[<MARKER>-DOC-NNNN] review: <MARKER>-N <title>` per `naming.md`. Subsections per pass: Findings, Routing Applied, Autonomous Fixes, Halts Composed. Append-only across iterations. Single write per `write-discipline.md`; the auto-ADR file + Linear ADR doc (step 7) batch same-turn.

9. **Route to the next stage** (mutually exclusive, all via the Task tool per audit decision #9):
   - **Halts composed** → Task-invoke `/update-linear` with `(parent_id, halt_messages[], autonomous_fixes_applied, source_stage="review")`. /update-linear renders the halt-card (it absorbed the former /push-to-chat renderer). Cascade ends.
   - **Halts empty, guidance non-empty** → Task-invoke `/plan` with the guidance list. /plan re-decomposes; `iteration_count` increments on the next /review pass.
   - **All clean (or only autonomous fixes)** → Task-invoke `/update-linear` with the full clean payload. Cascade proceeds.

## Same-turn write rules

Per `write-discipline.md`:
- Review document append: single write.
- Auto-ADR file + Linear ADR document: same-turn batch.
- Autonomous fix on check e: parent comment updated in place, same turn.
- No ticket label changes — parent stays `scope:planned` through /review per `scope-labels.md`.

## Outputs

| Artifact | Location |
|---|---|
| Review document (append-only) | `[<MARKER>-DOC-NNNN] review: <MARKER>-N <title>` |
| Auto-filed ADRs (if any) | `docs/decisions/NNNN-<slug>.md` + `[<MARKER>-DOC-NNNN] adr: <slug>` |
| Iteration guidance (internal) | Task-passed to /plan |
| Halt-messages + autonomous_fixes_applied (internal) | Task-passed to /update-linear |
| Autonomous parallelization fixes | Parent ticket comment, edited in place |

## Completion status

Per `completion-status.md`. The cascade engine routes on this:

- `DONE` — all eleven checks ran; no findings, or only autonomous-fixes resolved everything; cascade clean → /update-linear.
- `DONE_WITH_CONCERNS` — checks ran; autonomous fixes applied (parallelization downgrade or low-stakes dep ADR); iterate-/plan guidance returned. Cascade continues — /plan re-fires with guidance.
- `BLOCKED` — at least one spec-halt finding (b, g, j, k, or any stability/cap-triggered halt). Halt-card composed and Task-passed to /update-linear for rendering. Founder action required before retry.
- `NEEDS_CONTEXT` — parent ticket missing `scope:planned` label; spec markdown missing; `docs/constitution.md` missing (check j cannot run); `docs/templates/halt-messages.md` missing (cannot compose halts).

## Chains

Three outbound routes per pass — mutually exclusive, all via the Task tool per audit decision #9:
- **Iterate:** Task-invoke /plan with the `guidance` parameter. /plan re-decomposes, /review fires again.
- **Halt:** Task-invoke /update-linear with the halt-message list + `autonomous_fixes_applied`. /update-linear renders the halt-card; cascade ends.
- **Clean:** Task-invoke /update-linear with the clean payload. Cascade proceeds to consolidation + summary card.

No re-firing of /specify. /review iterates only /plan; spec-level findings halt rather than iterate.

## Notes

**Why /review stays a skill.** Per the audit's "Skills that stay skills (11 files)" list, /review is orchestration — it routes the cascade. It is not a thin deterministic action (not a command) and not a focused specialist invoked by another skill (not an agent). It absorbed the former /decide's routing logic for v0.1 simplicity.

**Stability rule fires before cap.** Same `(type, locus)` in two consecutive review docs → spec-halt. Saves iteration budget. A different suggestion on the same finding doesn't reset stability — same defect = same conclusion.

**Halt-card patterns live in `docs/templates/halt-messages.md`** per audit decision #8 — one pattern per spec-halt check type, parameterized. /review composes; /update-linear renders. /review does not inline halt-card structure.

**ADR-reversal (g), constitution-check (j), completeness (k) are always spec-halt, never autonomous or iterate.** Constitution violations indicate spec drift, not decomposition error — /plan can't iterate out of them. Incompleteness means the Clarify phase didn't sweep — /plan also can't fix that. ADR reversals, even mechanically obvious ones, deserve founder approval.

**Autonomous fix for check e gets no ADR** — it's a routing change, not a decision. The parent-comment update is sufficient audit. Auto-filed ADRs (check h) carry `Status: Accepted-Autonomous` vs `Accepted` for human-ratified; a v0.2 sweep can find them for retroactive ratification.

**Routing to /update-linear, not /push-to-chat.** Pre-extraction, /review's halt and clean routes both went to /push-to-chat (halt) or /update-linear-then-/push-to-chat (clean). Per audit decision #3, /push-to-chat is deleted and its renderer absorbed into /update-linear — so both of /review's terminal routes now Task-invoke /update-linear, which consolidates (if clean) and renders the card (always).

**Cascade halt is not failure.** It's the intended escape valve when iteration won't converge or a spec-level issue surfaces. Halting cleanly is /review's primary value-add beyond detection.

## Open questions (deferred to v1.1+)

- **Split /review back into /review + /decide.** v0.1 absorbed /decide's routing for primitive-count economy. v0.2 split-out conditions are noted in the original `[SOL-RFC-001]`.
- **Budget-estimate heuristic.** v0.1 uses file-touch count + spec-section coverage + design surface area. v0.2 refines with Code-Claude session telemetry.
- **Halt-messages pattern coverage for /review's own checks.** `[SOL-TPL] halt-messages.md` carries patterns for the check types /review composes against; if a new check is added, its pattern lands in the template first (template-first cadence per the halt-messages doc).
