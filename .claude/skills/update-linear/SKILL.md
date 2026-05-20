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

## Naming reconciliation note

D3.4 §Per-stage gate inventory `/update-linear` row names one gate: `update-linear.diff-applied`. The parent `spec.md` AC-13 reads: "`.claude/skills/update-linear/SKILL.md` evaluates the `update-linear.diff-applied` gate." AC-13 uses D3.4's gate name verbatim; no divergent naming surface. This skill uses D3.4's name without further reconciliation.

D3.4 framing: "D2.1 v2 specifies this stage; D3.4 names its single gate for completeness." This section is the SKILL.md realisation of D3.4's row.

## Stage structure

`/update-linear` is a per-ticket stage that runs after `/plan`'s seal in the auto-fire chain `/plan → /review → /update-linear` (the Group E chain per D2.3 v1.3 §Pattern C). It propagates the spec's resolved AC list and per-child decomposition into Linear ticket descriptions for the parent ticket and every child the `/plan` decomposer emitted. The behavior is:

1. Read the `/plan` manifest's `outputs.child_tickets[]` and parent ticket.
2. For each ticket, compose its target Linear description (parent: spec link + decomposition summary; child: per-child block from `decomposition.md` rendered as ticket description).
3. Apply the updates via Linear MCP.
4. Compute `diff_sha256` over the applied diff per D2.1 v2 §`/update-linear` row.
5. Verify each ticket's current Linear state matches the diff — the `update-linear.diff-applied` gate (see §Gate evaluation).
6. Seal the manifest.

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

## Gate evaluation

One gate fires at `/update-linear` at-write per D3.4 §Per-stage gate inventory `/update-linear` row. The gate evaluates just before manifest seal — after all Linear writes from step 3 have completed and the eventual-consistency window per D2.1 v2 §Linear-sync has been observed (the v0.1 contract carries forward — `/update-linear` waits per the v0.1 backoff before re-reading).

```text
GATES_AT_UPDATE_LINEAR_AT_WRITE = ["update-linear.diff-applied"]

for gate in GATES_AT_UPDATE_LINEAR_AT_WRITE:
    evaluate; record per-gate result
if any gate has failing predicates:
    compose halt card per D3.4 §Aggregation rules (single-gate stage; aggregation degenerates to the single gate's halt)
    do NOT write manifest; exit with halt
else:
    write manifest
    seal /update-linear
```

### Gate 1 — `update-linear.diff-applied` (at-write; D2.1 v2 `/update-linear` row + §Linear-sync — v0.1 carry-forward)

V0.1's `/update-linear` already evaluates this predicate. The amendment renames it.

```text
# Read the in-memory record of writes applied in step 3
applied_diff ← read step-3 write log: list of (ticket_id, field, before_value, after_value)
diff_sha256 ← sha256 over the canonical-serialised applied_diff

# Predicate 1: each ticket's current Linear state matches the applied diff
for entry in applied_diff:
    current ← linear-mcp's read of entry.ticket_id's entry.field
    if current != entry.after_value:
        FAIL with §linear-state-inconsistent
        diagnostic: (
            f"ticket {entry.ticket_id}'s field '{entry.field}' currently '{truncate(current, 80)}'; "
            f"expected '{truncate(entry.after_value, 80)}' per applied diff"
        )
        continue

# Predicate 2: Linear-sync sanity check per D2.1 v2 §Linear-sync
# Eventually-consistent reads: the v0.1 contract reads twice with the v0.1-specified backoff
# between reads; if both reads return the expected value, the sync is sane.
for entry in applied_diff:
    first_read ← linear-mcp's read of entry.ticket_id's entry.field
    sleep(v0.1-specified backoff window)   # e.g., 750ms; v0.1 owns the constant
    second_read ← linear-mcp's read of entry.ticket_id's entry.field
    if first_read != second_read:
        FAIL with §linear-state-inconsistent
        diagnostic: (
            f"ticket {entry.ticket_id}'s field '{entry.field}' is unstable across the Linear-sync window: "
            f"first read '{truncate(first_read, 80)}', second read '{truncate(second_read, 80)}'; "
            f"Linear is still propagating the write or another writer is racing"
        )
        continue
    if first_read != entry.after_value:
        FAIL with §linear-state-inconsistent
        diagnostic: (
            f"ticket {entry.ticket_id}'s field '{entry.field}' stable but value '{truncate(first_read, 80)}' "
            f"differs from expected '{truncate(entry.after_value, 80)}'; the write did not land"
        )
```

Halt code: `§linear-state-inconsistent` (v0.1 carry-forward). Recovery options surfaced in the halt card:

- **Founder edits Linear manually** — for cases where the discrepancy is because a human (or another tool) wrote concurrently. Founder reconciles Linear to match `decomposition.md`'s view, then re-runs `/update-linear` or skips to `/build` directly (the auto-fire chain pauses at the halt).
- **`/update-linear --continue`** — retry after the eventual-consistency window. v0.1's `--continue` flag re-runs the diff-apply step with the same target state; if Linear was still propagating the original write, the retry usually clears the halt. v0.1's contract for `--continue` carries forward verbatim.

Per D3.4 §`/update-linear` row: "Each ticket's current Linear state matches `diff_sha256`; Linear-sync sanity check passes per D2.1 v2 §Linear-sync."

## Manifest write (on all-gates-pass)

Write the `/update-linear` manifest at `.cascade/manifests/<ticket>-update-linear.json` per D2.1 v2 `/update-linear` row. The v0.1 schema carries forward; no v0.2 additive fields specifically for `/update-linear`:

```json
{
  "stage": "/update-linear",
  "ticket": "<MARKER>-<N>",
  "update_linear_sealed_at": "<ISO-8601 timestamp>",
  "outputs": {
    "summary":            "/update-linear propagated parent <MARKER>-<N> and <count> child tickets' descriptions from sealed decomposition.md to Linear; diff_sha256=<sha-short>.",
    "tickets_updated":    [
      {"ticket_id": "<MARKER>-<N>", "fields_changed": ["description", "labels"]},
      {"ticket_id": "<MARKER>-<N+1>", "fields_changed": ["description"]},
      ...
    ],
    "diff_sha256":        "<sha>",
    "linear_sync_observed_at": "<ISO-8601 timestamp>"
  },
  "input_provenance": {
    "parent_manifest_path":     ".cascade/manifests/<ticket>-plan.json",
    "parent_manifest_sha256":   "<sha>",
    "ac_list_sha256":           "<sha>",
    "four_hat_seal_sha256":     "<sha>"
  },
  "manifest_sha256": "<recomputed-zero-self-field>"
}
```

Schema rules carry forward from v0.1 with one addition:

- `outputs.summary` is the single-sentence description D4.6 v1.1 reads per D2.1 v2.1 common-manifest-fields. Per D2.3 v1.3 §`/Chains` contract Pattern C (Group E) row: `/update-linear`'s manifest is Group E's exit manifest (Group E's chain ends at `/update-linear`).

After write, update `cascade:run-state.json`'s `last_completed_stage` to point at this manifest path and sha. The chat-end card render at the `/Chains` block's Group E exit (per `child_B_chains_sections.md` Pattern C Group E variant) sets `cascade:run-state.last_completed_group = "E"`.

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

## Cross-references

- **D2.1 v2 §`/update-linear` row** — the upstream manifest schema and verifier-predicate baseline; this skill renames the predicate per AC-13 + D3.4 with no behavior change.
- **D2.1 v2 §Linear-sync** — the eventual-consistency sanity check Gate 1 Predicate 2 evaluates; the v0.1 backoff constant is owned by v0.1's `/update-linear` SKILL.md and carries forward.
- **D2.2 §Hook/script surface** — `/update-linear`'s PreToolUse matcher on Linear write tool (the existing v0.1 wiring carries forward).
- **D2.3 v1.3 §`/Chains` contract Pattern C (Group E)** — `/update-linear`'s manifest is the Group E exit manifest; this skill writes the schema D4.6 v1.1 re-derives from.
- **D3.4 §Per-stage gate inventory `/update-linear` row** — the one-gate inventory this skill implements.
- **D3.4 §Aggregation rules** — degenerates to the single gate's halt for `/update-linear`'s single-gate stage.
- **D4.5 §`/update-linear` reconciliation** — not present in D4.5 per F-Rev-2's queued disposition; v0.2 ships no `--reconcile` for `/update-linear`. The recovery surfaces in the halt card are `--continue` (v0.1 carry-forward) and founder-manual Linear edit. F-Rev-2 amends D4.5 in v0.2.x to add `--reconcile` for the four uncovered stages (`/onboard`, `/update-linear`, `/review`, `/verify`, `/retro`); Child 0001-D's design session is the implementation surface.
- **Child A `halt-messages-append.md`** — `§linear-state-inconsistent` is a v0.1 carry-forward.
- **`plan-SKILL-amendments.md`** (Child 0001-B continuation 0) — `/plan`'s manifest is the upstream this stage reads; the `child_tickets[]` and `decomposition_strategy` fields are read at step 2.
- **`wrap-SKILL-amendments.md`** (Child 0001-B continuation 1) — same naming-only-amendment shape; this skill matches the pattern.
- **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-13** — this skill amendment (combined with `onboard-SKILL-amendments.md`) satisfies AC-13 as authored.

## /Chains

**Pattern:** C (auto-fire-chain, Group E variant — chain's last stage)
**Group:** E
**Within-group transitions:** this skill is the chain's last stage; no further intra-Group-E transitions after seal. The chain `/plan` → `/review` → `/update-linear` terminates here.
**Group exit trigger:** `/update-linear` manifest seal at `.cascade/manifests/<ticket>-update-linear.json` after the `update-linear.diff-applied` gate per D3.4 §update-linear gates passes (Linear writes for Backlog tickets, decomposition.md diff applied, parent manifest's `outputs` reflects the new child tickets).
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant `normal`. After render, set `cascade:run-state.last_completed_group = "E"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<ticket>-update-linear.json"`, also increment `cascade:run-state.queue_version` (the Group E exit is the canonical queue-write event — `/plan`'s decomposition initially assigns the queue and `/update-linear` makes it Linear-canonical; `queue_version++` here defeats stale-card replay across the E→F boundary). Flush, write `.cascade/handoff/last.md`. Do not Task-invoke anything.
**Next group entry:** F (the first Group F chat: `/build SOL-<first-ticket>` where `<first-ticket>` is the first ticket in the decomposition's queue order). The founder pastes the handoff prompt into a new Claude Code session (Group F runs in Claude Code per §Execution surface per group; the handoff card includes the surface-shift framing).
**Auto-fire compact handling:** not applicable for chat-Claude. Group E lives in chat-Claude; the auto-fire compact behaviour applies only in Group F (per D2.3 v1.3 §Auto-fire compact behaviour scope).
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<ticket>-update-linear.json`. `/plan`'s and `/review`'s manifests are inputs (durable per D2.1 v2.1 but not the exit manifest). D4.6 v1.1 reads `/update-linear`'s manifest's `outputs` field to populate the chat-end card's "What was produced" section for Group E re-derivation.

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
