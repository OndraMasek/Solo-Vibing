---
name: update-linear
description: Final consolidation + user-facing rendering stage of the cascade. Internal. Task-invoked by /review — on a clean cascade it consolidates parent + children state into Linear and renders the summary card; on an upstream halt it renders the halt-card. Updates parent ticket description with consolidated post-cascade state, verifies child consistency, posts cascade-complete comment, then renders the single user-facing card that ends the cascade turn. Absorbs the former /push-to-chat renderer (audit decision #3). Mechanical writer; never halts on spec issues — halts only on environmental errors.
---

# update-linear

Final consolidation + cascade-end rendering. Internal cascade stage after /review. Takes the converged state of parent + children + side artifacts, writes the canonical post-cascade representation into Linear, then renders the single user-facing card (summary or halt) that ends the cascade turn. References rules: `naming.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`. Mechanical writer; not user-invoked.

## Trigger

Internal: Task-invoked by `/review` (per audit decision #9 — explicit Task-tool chaining) in two mutually-exclusive shapes:
- **Clean:** /review passes `(parent_id, children_ids[], autonomous_fixes_summary, adrs_filed[], review_iterations)` — consolidate + render summary card.
- **Halt:** /review (or an upstream stage routed through /review) passes `(parent_id, halt_messages[], autonomous_fixes_applied{}, source_stage)` — skip consolidation, render halt-card.

Manual override: `/update-linear <MARKER>-N` — debugging only.

## Behavior

### Clean-cascade path

1. Receive the clean payload from /review.

2. Fetch parent ticket, all children, parent spec markdown, four-hat document, review document, all ADR documents created during the cascade.

3. **Verify environmental consistency** (read-before-write per `write-discipline.md`):
   - Parent still exists, label still `scope:planned` per `scope-labels.md`.
   - Every child in `children_ids[]` exists with `parentId` pointing to this parent, label still `scope:sealed`.
   - `blockedBy` graph still matches /plan's last-written state.
   - Spec markdown still exists at `docs/specs/NNNN-<slug>/spec.md` per `naming.md`.

   Any inconsistency → `BLOCKED` per `completion-status.md`. Skip consolidation, jump to step 8 and render an environmental halt-card per `docs/templates/halt-messages.md` (the `§missing-context` / `§label-mismatch` patterns as applicable). The recommendation is "re-run /plan <MARKER>-N to re-converge — autonomous fixes from this cascade persist."

4. **Compose consolidated parent description** — replace the /specify-written description with the post-cascade canonical version. The Acceptance-criteria block is overwritten from `spec.md` verbatim (text only; checkbox state is preserved from current ticket state where /build has flipped boxes). spec.md is the sole canonical AC source per /specify Notes — any divergent ticket-side AC text is overwritten here.

   ~~~
   Problem
   <brief paragraph from spec markdown, verbatim>

   Acceptance criteria
   - [ ] AC-1: <from spec>
   - [ ] AC-2: <from spec>

   Plan
   * Wave 1 (parallel): <MARKER>-N-1, <MARKER>-N-2
   * Wave 2 (after Wave 1): <MARKER>-N-3

   Artifacts
   * Spec: `docs/specs/NNNN-<slug>/spec.md`
   * Decomposition: `docs/specs/NNNN-<slug>/decomposition.md`
   * Four-hat review: [<MARKER>-DOC-NNNN]
   * Plan review: [<MARKER>-DOC-NNNN]
   * ADRs auto-filed: [<MARKER>-DOC-NNNN] <slug>, ...
   * Branch: `<MARKER>-N-<slug>`

   Cascade audit
   * Children: N
   * Autonomous fixes applied: M
   * ADRs auto-filed: K
   * Review iterations: J
   ~~~

   Doc IDs and paths per `naming.md`.

5. **Verify child consistency** (mechanical): each child has `parentId` set, label `scope:sealed`, branch named per `naming.md` §Branch names, description with AC subset + failing-test seed + link to parent spec markdown. Any missing field → repair in place; log the repair in the cascade-complete comment.

6. **Post cascade-complete comment on parent:**

   ~~~
   Cascade complete. <MARKER>-N specified, planned, reviewed, ready to build.

   * Children: N (<MARKER>-N-1, <MARKER>-N-2, ...)
   * Wave structure: Wave 1 [...], Wave 2 [...]
   * Autonomous fixes: M (<one-line summary>)
   * ADRs auto-filed: K
   * Review iterations: J
   * Repairs applied: 0 (or list)
   ~~~

7. **Parent label stays `scope:planned`** per `scope-labels.md` — /update-linear transitions no labels. Build status is tracked through the children's Linear-native state machine (Todo → In Progress → Done), driven by `/start` and `/wrap`.

   Steps 4–6 are a single same-turn write batch per `write-discipline.md` (parent description replace + child repairs + cascade-complete comment). Partial failure → marker + `BLOCKED` per `write-discipline.md` §Partial failure.

### Rendering (absorbed /push-to-chat renderer — both paths converge here)

8. **Determine card mode** from how step 1–7 resolved:
   - Steps 2–7 completed clean → **summary card**.
   - Step 3 found an environmental inconsistency, or the trigger payload was the halt shape → **halt-card**.

9. **Render the single user-facing card** as the final chat message of the cascade turn:

   **Summary card** (clean):

   ~~~
   <MARKER>-N: <title> — specified, planned, ready to build.

   Plan
   * Wave 1 (parallel): <MARKER>-N-1, <MARKER>-N-2
   * Wave 2 (after Wave 1): <MARKER>-N-3
   (single child: "Wave 1: <MARKER>-N-1 (only child).")

   Decisions
   * <K> ADRs auto-filed: [<MARKER>-DOC-NNNN] (<slug>), ...
   (zero: "No new decisions.")

   Process
   * Review iterations: <J>
   * Autonomous fixes: <M> (<one-line summary or "none">)

   Next
   * /build <MARKER>-N-1 — start the first child. <If parallel Wave 1: "or /build <MARKER>-N-2 in a second session.">

   Drill-down (optional reading)
   * Spec: `docs/specs/NNNN-<slug>/spec.md`
   * Decomposition: `docs/specs/NNNN-<slug>/decomposition.md`
   * Four-hat review: [<MARKER>-DOC-NNNN]
   * Plan review: [<MARKER>-DOC-NNNN]
   * Branch: `<MARKER>-N-<slug>`
   ~~~

   **Halt-card:** render per `docs/templates/halt-messages.md` — the five-section schema, using the pattern that matches the halt's origin (`§missing-context` / `§label-mismatch` for environmental halts detected here; the upstream stage's own pattern for halt-messages passed through). If `autonomous_fixes_applied` is non-empty, include the note that those fixes persisted in Linear and re-running /plan preserves them.

10. The card is the final chat message of the cascade turn. Cascade ends.

## Same-turn write rules

Per `write-discipline.md`:
- Parent description replace + child repairs + cascade-complete comment: single same-turn batch.
- No label transitions (`scope-labels.md` — /update-linear mirrors state, never sets it).
- The rendered card is a chat message, not a Linear write.

## Outputs

| Artifact | Location |
|---|---|
| Updated parent description | Parent ticket (canonical post-cascade format) |
| Repaired children (if any) | Affected child tickets, in place |
| Cascade-complete comment | Parent ticket comment |
| Summary card OR halt-card | Final chat message of the cascade turn |

## Completion status

Per `completion-status.md`:

- `DONE` — environmental consistency verified, parent description replaced, cascade-complete comment posted, summary card rendered. Cascade succeeds.
- `DONE_WITH_CONCERNS` — completed, but child repairs were applied in place (missing parentId / label / branch name / description link auto-repaired); repairs logged in the cascade-complete comment.
- `BLOCKED` — environmental halt (parent label changed externally, child archived mid-cascade, spec markdown deleted, `blockedBy` graph diverged), OR the trigger payload was a pass-through halt. Halt-card rendered per `docs/templates/halt-messages.md`.
- `NEEDS_CONTEXT` — parent ticket missing entirely; spec markdown directory missing; one or more child IDs in the payload reference non-existent tickets.

## Chains

Terminal. /update-linear is the last cascade stage — it renders the card and the cascade turn ends. No downstream skill fires. The next user-invoked action is `/build <MARKER>-N-K` per child ticket, surfaced in the summary card's Next section.

## Notes

**Why /update-linear absorbs /push-to-chat** (audit decision #3). /push-to-chat was a pure-presentation cascade-internal skill — a primitive whose only job was rendering a card from a payload /update-linear had already assembled. Folding the renderer into /update-linear's tail saves a primitive and removes the cascade-internal-skill awkwardness. The `[SOL-SKILL] push-to-chat` file is deleted in Batch 3; its renderer logic is steps 8–9 above.

**Mechanical writer, not a router.** /review already decided the cascade is clean (or halted) before invoking /update-linear. /update-linear's job is to make Linear reflect that and render the outcome — it does not re-evaluate the cascade.

**Parent label stays `scope:planned`** through and after /update-linear. Build-time states (Todo / In Progress / Done) are Linear-native, not part of the `scope:*` machine per `scope-labels.md`. Children move through Linear states via `/start` and `/wrap`.

**Description replacement, not append, is deliberate.** /specify writes a brief problem + AC + links. After the cascade, the canonical description adds the plan summary + cascade audit + more artifact links. Replacing produces one coherent description; the original is preserved in the spec markdown.

**Environmental halt is the only halt /update-linear originates.** Causes: a child archived mid-cascade, spec markdown deleted, parent label manually changed. These are environmental, not spec defects — recovery is a /plan re-run. Spec-level halts are originated upstream (by /review, /plan) and merely rendered here.

**The "Next" line recommends `/build`.** Post-extraction, /build is the build entry point and Task-invokes /start itself. The summary card's Next section points the founder at `/build <MARKER>-N-K`, not at a manual /start (consistent with `[SOL-CMD] next` priority 4).

**Repair logic is light in v0.1** — fix missing parentId, label, branch name, description links. Does not recreate deleted children or undo external label changes. Heavier repair is v0.2.

## Open questions (deferred to v1.1+)

- **Auto-filed ADR content in the summary card.** Listed by slug only; the founder drills into Linear for content. Inlining a one-line ADR summary is a v1.1 nicety.
- **Multi-issue halt-cards.** The halt-messages template's "pick exactly one pattern per halt" rule applies; composite-pattern syntax for cascades that halt on multiple findings at once is a v1.1 item (tracked in `[SOL-TPL] halt-messages.md`'s own Open questions).
- **`scope:built` mirroring.** /update-linear runs at cascade end, before any build. It never sees `scope:built`. If a future cascade re-enters post-build, the consistency check in step 3 would need extending — v1.1+.
