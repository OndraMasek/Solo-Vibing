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

## Gate evaluation

Three gates fire at `/review`, in firing order per D3.4 §Per-stage gate inventory `/review` row. All gates evaluate before any halt card is composed per D3.4 §Aggregation rules.

```text
GATES_AT_REVIEW = [
  "review.provenance",                  # pre-flight; manifest chain to /specify
  "review.four-hat-objection-coverage", # at-write; SubagentStop hook predicate
  "review.ac-list-seal"                 # at-write; seal_sha256 recomputes
]

for gate in GATES_AT_REVIEW:
    evaluate gate predicates and record per-gate result
    # do NOT short-circuit; all gates evaluate

if any gate has at least one failing predicate:
    compose aggregate halt card per D3.4 §Aggregation rules
    do NOT write the manifest
    exit with halt
else:
    write manifest, including four_hat_doc_id and seal_sha256 fields
    seal /review
```

### Gate 1 — `review.provenance` (pre-flight; manifest chain to `/specify`)

```text
read cascade:run-state from docs/.cascade/run-state.json

# Step 1: parent manifest must be /specify's seal
expected_parent_path ← cascade:run-state.last_completed_stage.postcondition_manifest_path
if expected_parent_path absent or path doesn't resolve to a file:
    FAIL with §provenance-chain-broken
    diagnostic: "expected /specify manifest at <path>; absent"
    continue

# Step 2: recompute manifest sha
recomputed_sha ← sha256 of parent manifest with manifest_sha256 field zeroed
expected_sha   ← cascade:run-state.last_completed_stage.postcondition_manifest_sha256
if recomputed_sha != expected_sha:
    FAIL with §provenance-chain-broken
    diagnostic: f"parent manifest sha mismatch at {expected_parent_path}; expected {expected_sha[:12]}..., got {recomputed_sha[:12]}..."
    continue

# Step 3: parent must be /specify (not /plan or another stage)
parent_outputs ← parse parent manifest's outputs
if parent_outputs.stage != "/specify":
    FAIL with §provenance-chain-broken
    diagnostic: f"/review's upstream must be /specify; got stage='{parent_outputs.stage}' at {expected_parent_path}"
```

Halt code: `§provenance-chain-broken`. Recovery: `--reconcile` per D2.1 v2.1's chain-recovery pattern.

### Gate 2 — `review.four-hat-objection-coverage` (at-write; SubagentStop hook predicate)

This is the cascade's **single agent-type hook** per D3.4 §What is a gate and D2.2 §Hook/script surface. Per D2.1 v2 §Subagent verification, the parent (`/review`) writes each subagent's manifest from an independently re-read transcript; the gate's predicate is the parent's recompute, **not** the subagent's self-report.

#### Predicate sequence

Four hat subagents are dispatched in parallel via Task-invoke per the v0.1 `/review` skill's subagent-dispatch step: `four-hat-user`, `four-hat-engineer`, `four-hat-pm`, `four-hat-skeptic`. Each subagent terminates with a `SubagentStop` event, at which point this gate's hook script (`.claude/hooks/four-hat-objection-coverage.py`, authored in Child 0001-C) fires per `agent_transcript_path`:

```text
for each hat ∈ {user, engineer, pm, skeptic}:
    transcript_path ← SubagentStop payload's agent_transcript_path for this hat
    transcript      ← read JSONL from transcript_path

    # Predicate 1: priming text present
    priming_text ← parse the first user-message-content from the transcript
    if priming_text does not match the expected four-hat priming for this hat:
        FAIL with §four-hat-incomplete/priming-text-missing
        diagnostic: f"hat={hat}; transcript={transcript_path}; expected priming text missing or malformed"
        continue

    # Predicate 2: structured objections section present
    last_assistant_message ← parse the final assistant-message-content from transcript
    objections_section ← extract block matching "^##? Objections" through next "^##? "
    if objections_section is absent:
        FAIL with §four-hat-incomplete/objections-section-missing
        diagnostic: f"hat={hat}; transcript={transcript_path}; '## Objections' section absent in final assistant message"
        continue

    # Predicate 3: concluding seal line present
    seal_line ← extract block matching "^##? Seal" or final line beginning with "Seal:"
    if seal_line is absent:
        FAIL with §four-hat-incomplete/seal-line-missing
        diagnostic: f"hat={hat}; transcript={transcript_path}; concluding seal line ('## Seal' or 'Seal:') absent"
        continue

    # Predicate 4: structured objection entries parseable
    objections ← parse objections_section per the four-hat-template shape (bullet entries with hat, locus, severity, finding)
    if any objection entry is malformed:
        FAIL with §four-hat-incomplete/objection-entry-malformed
        diagnostic: f"hat={hat}; objection N at line M malformed; expected '- **{{user|engineer|pm|skeptic}}** [{{severity}}] @ {{locus}}: {{finding}}'"
        continue

    # Predicate 5: write subagent manifest from parent's recompute
    write .cascade/manifests/<ticket>-<hat>.json with:
        outputs.objections[] ← parsed objections (the parent's recompute, not the subagent's claim)
        outputs.hat_id ← hat
        outputs.concluded_at ← transcript's final-message timestamp
        input_provenance.transcript_path ← transcript_path
```

After all four hat manifests are written, the gate's at-write predicate evaluates the merged unresolved count:

```text
# Predicate 6: unresolved_count == 0 across all four hats
all_objections ← union of objections[] across the four hat manifests
unresolved ← [obj for obj in all_objections if obj.resolution is absent or obj.resolution == "pending"]

if unresolved is non-empty:
    FAIL with §four-hat-objections-unresolved
    diagnostic: f"{len(unresolved)} unresolved objections across four hats; per-hat counts: user={count_user}, engineer={count_engineer}, pm={count_pm}, skeptic={count_skeptic}; objections listed under §Open Questions in {spec_path}"
```

Halt codes per D3.4 §Per-stage gate inventory `/review` row: `§four-hat-incomplete` (with sub-case in diagnostic — `priming-text-missing`, `objections-section-missing`, `seal-line-missing`, `objection-entry-malformed`), `§four-hat-objections-unresolved`. Pre-existing v0.1 halts where present; apply-time additions where absent (see authoring notes Surfaced item #1).

#### Hook output shape — top-level fields only

The hook script emits the Stop/SubagentStop top-level-fields-only output per D2.2 §Stop / SubagentStop output schema quirk. **No `hookSpecificOutput` wrapper.** Verified on Claude Code v2.0.76 per anthropics/claude-code#15485:

On per-hat failure (any of predicates 1–5):

```json
{
  "decision": "block",
  "reason": "§four-hat-incomplete/<sub-case>: hat=<hat>; transcript=<path>; <one-line diagnostic>. Run /review --continue after addressing."
}
```

On all-hats-pass + unresolved-count zero:

```json
{
  "decision": "approve"
}
```

(`"approve"` is also a top-level field; the hook signals continuation rather than blocking.)

On all-hats-pass but unresolved-count > 0 (predicate 6):

```json
{
  "decision": "block",
  "reason": "§four-hat-objections-unresolved: <N> unresolved objections across four hats; resolve under §Open Questions in <spec_path> and run /review --continue."
}
```

The hook script is `.claude/hooks/four-hat-objection-coverage.py` and lives in Child 0001-C's scope; this SKILL.md amendment specifies what the hook checks and what it returns, not the hook script's filesystem-and-IO scaffolding.

#### Imperative-phrasing carry-forward (F-Int-2 context)

The `reason` field above uses present-tense factual statements with a recovery action ("Run /review --continue after addressing"), per D2.2's "factual phrasing per the hooks-reference guidance, not imperative instructions" pattern. The forcing function is the `decision: block` itself — not the prose of `reason`. The prose's job is to make the halt diagnostic readable; the prose does NOT command the model to do anything. F-Int-2 (per D2.3 v1.2 four-hat review) flagged the ambiguity for Stop hooks generally; SubagentStop here follows the same shape resolution.

### Gate 3 — `review.ac-list-seal` (at-write; `seal_sha256` recomputes)

```text
spec_path        ← parent_outputs.spec_path (the /specify manifest's spec_path)
current_ac_list  ← parse §Acceptance criteria from spec_path
current_ac_sha   ← sha256 of canonicalized AC list per D2.1 v2 §input_provenance.ac_list_sha256

# The /review skill is about to write four_hat_seal_sha256 ← current_ac_sha
# Predicate 1: AC list matches /specify's sealed ac_list_sha256
specify_ac_sha ← parent_outputs.ac_list_sha256
if current_ac_sha != specify_ac_sha:
    FAIL with §four-hat-ac-list-drift
    diagnostic: f"AC list at {spec_path} has changed since /specify sealed; /specify ac_list_sha256={specify_ac_sha[:12]}..., current={current_ac_sha[:12]}...; /review's seal cannot proceed against a moving AC list"

# Predicate 2: every objection's covered_ac references resolve to AC IDs in the current list
all_covered_acs ← union of obj.covered_ac for obj in all_objections
ac_ids ← {ac.id for ac in current_ac_list}
unresolved_refs ← all_covered_acs - ac_ids
if unresolved_refs is non-empty:
    FAIL with §four-hat-ac-list-drift/objection-refs-stale
    diagnostic: f"objections reference AC IDs not in spec's current AC list: {sorted(unresolved_refs)}; spec AC IDs: {sorted(ac_ids)}"
```

Halt code: `§four-hat-ac-list-drift`. Recovery: re-run `/specify <MARKER>-N --unseal` to re-seal against the changed AC list; then re-run `/review`.

## Manifest write (on all-gates-pass)

Write the `/review` manifest at `.cascade/manifests/<ticket>-review.json` per D2.1 v2 §`/review` row:

```json
{
  "stage": "/review",
  "ticket": "<MARKER>-<N>",
  "review_sealed_at": "<ISO-8601 timestamp>",
  "outputs": {
    "four_hat_doc_id": "<Linear doc ID>",
    "seal_sha256": "<current_ac_sha — the AC-list hash at review seal time>",
    "objections_resolved": [
      {"hat": "...", "locus": "...", "severity": "...", "finding": "...", "resolution": "...", "covered_ac": ["AC-N"]},
      ...
    ],
    "unresolved_count": 0,
    "subagent_manifest_paths": [
      ".cascade/manifests/<ticket>-user.json",
      ".cascade/manifests/<ticket>-engineer.json",
      ".cascade/manifests/<ticket>-pm.json",
      ".cascade/manifests/<ticket>-skeptic.json"
    ]
  },
  "input_provenance": {
    "spec_path":                 "docs/specs/<NNNN>-<slug>/spec.md",
    "ac_list_sha256":            "<sha>",
    "parent_manifest_path":      ".cascade/manifests/<ticket>-specify.json",
    "parent_manifest_sha256":    "<sha>"
  },
  "manifest_sha256": "<recomputed-zero-self-field>"
}
```

The four subagent manifests at `.cascade/manifests/<ticket>-{user,engineer,pm,skeptic}.json` are inputs to `/review`'s seal (written by the parent during Gate 2 evaluation), not outputs in the chain sense; they remain on disk as audit history per D2.1 v2 §Subagent verification.

After write, update `cascade:run-state.json`'s `last_completed_stage` to point at this manifest path and sha.

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

## /Chains

**Pattern:** C (auto-fire-chain, Group E variant)
**Group:** E
**Within-group transitions:** this skill is the middle stage in the Group E chain. On `/review` manifest seal at `.cascade/manifests/<ticket>-review.json` (after the four-hat objection-coverage check fires as SubagentStop in Claude Code — or as the chat-Claude advisory analog in Group E — per D3.4 §review gates, and after the other `review.*` gates pass), this skill Task-invokes `/update-linear` to advance the chain. In chat-Claude, "Task-invoke" is project-instruction-driven continuation as in `/plan`. Review-internal safe boundaries: after the four-hat panel completes (per D2.3 v1.3 §Within-group safe boundaries Group E row, advisory in chat-Claude); after `/review`'s critique consolidation.
**Group exit trigger:** not this skill. `/review` is a Group E chain intermediate.
**Group exit render:** not this skill. Chain-intermediate; after `/review`'s manifest seals, this skill continues to `/update-linear` without rendering.
**Next group entry:** not this skill. See `/update-linear`'s `/Chains` section for the Group E exit transition.
**Auto-fire compact handling:** not applicable for chat-Claude. Same disposition as `/plan`'s row.
**Group's exit manifest:** not-this-skill — see `/update-linear`. `/review`'s manifest at `.cascade/manifests/<ticket>-review.json` is a chain intermediate. The four-hat agents' (`four-hat-{user,engineer,pm,skeptic}.md`) per-hat outputs (if Group E's `/review` also runs a four-hat fan-out, distinct from Group D's `/specify` fan-out) are inputs to `/review`'s seal, not the exit manifest.

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
