# Child 0001-B continuation 1 — `/review` + `/build` + `/wrap` + `/verify` SKILL.md amendments — authoring notes

**Authored:** 2026-05-19, end of "0001 integration spec Child 0001-B continuation 1 — runtime-gate-evaluation cluster design session."

**Session deliverables (five files):**

  1. `review-SKILL-amendments.md` — three `review.*` gates per AC-8; the cascade's single agent-type hook on SubagentStop with top-level-fields-only output shape.
  2. `build-SKILL-amendments.md` — four `build.*` gates per AC-9 (one more than D3.4 names — pyramid-tampering split out per AC-9); Ralph backpressure preserved verbatim; F-Int-3 disposition in `/Chains` subsection.
  3. `wrap-SKILL-amendments.md` — four `wrap.*` gates per AC-10 (one more than D3.4 names — tests-green split out per AC-10); naming-only standardization; D2.1 v2 carry-forward behavior.
  4. `verify-SKILL-amendments.md` — five `verify.*` gates per D3.4; per-strategy dispatch matrix; hybrid recursion capped at one level; `children_gate_outcomes[]` schema write; multi-child halt aggregation. **Largest single change in Child 0001-B.**
  5. This notes doc.

Four amendment files use the patch-ready amendment pattern Child 0001-B continuation 0 (the prior session) established (substitute-by-purpose-not-by-line, v0.1 reconciliation deferred to executing Claude Code session).

After this session: 6 of ~9 skills' design done. Remaining: `/onboard`, `/retro`, `/update-linear` (3 skills) for Child 0001-B continuation 2.

---

## Authoring decisions

### `/review` — Stop/SubagentStop output schema quirk handled

D2.2 §Stop / SubagentStop output schema quirk specifies that SubagentStop events emit `{"decision": "block", "reason": "..."}` at the **top level** of the hook output — **NOT** wrapped in `hookSpecificOutput` as other hook events do. This is verified on Claude Code v2.0.76 per anthropics/claude-code#15485.

The `/review` Gate 2 amendment specifies the hook output shape verbatim. The hook script `four-hat-objection-coverage.py` (Child 0001-C scope) emits this shape literally; no abstraction layer. The shape is unique to Stop and SubagentStop events; every other hook event in the cascade (PreToolUse, PostToolUse, SessionStart, SessionEnd, PreCompact) uses the standard `hookSpecificOutput` wrapper. The `/build` Gate 2's PreToolUse pyramid-tampering hook output explicitly contrasts with this shape (see `/build` amendment §Gate 2 PreToolUse hook predicate).

### `/review` — F-Int-2 factual-phrasing pattern carried through

D2.3 v1.2 four-hat review §F-Int-2 flagged ambiguity in Stop hooks generally about whether `reason` strings are factual or imperative. The resolution: factual phrasing per D2.2's pattern; the forcing function is the `decision: block` itself, not the prose of `reason`. The `/review` Gate 2 hook output follows this — `reason` is present-tense diagnostic + a recovery action sentence, not an imperative command to the model.

Example:
- Factual + recovery: `"§four-hat-incomplete/objections-section-missing: hat=user; transcript=<path>; '## Objections' section absent. Run /review --continue after addressing."`
- NOT imperative: `"You must add an Objections section to the user hat transcript."`

The amendment's hook output examples all use the factual + recovery pattern. F-Int-2 disposition is carried through this session without additional surfacing.

### `/build` — four gates vs D3.4's three (AC-9 split)

D3.4 §Per-stage gate inventory `/build` row names three gates: `build.provenance`, `build.test-execution`, `build.finalize`. D3.4's `build.provenance` row text composes both the manifest chain check AND the pyramid-tampering check into one gate.

Parent `spec.md` AC-9 names three gates: `build.provenance`, `build.pyramid-tampering`, `build.test-execution`. AC-9 splits pyramid-tampering out as its own named gate; AC-9 doesn't name `build.finalize` separately.

The amendment uses **four gates total**: `build.provenance` (chain check only), `build.pyramid-tampering` (D3.2 §Downstream consumer touch-points predicate), `build.test-execution` (Ralph loop), `build.finalize` (manifest-write preconditions). This composes D3.4 + AC-9: keeps pyramid-tampering as a distinct named gate (per AC-9, for `solo-verify --explain build.pyramid-tampering` clarity), keeps `build.finalize` as a distinct named gate (per D3.4, for `solo-verify --explain build.finalize` clarity).

**Surfaced item in §Surfaced items #2.** Three D3.4-named gates vs three AC-9-named gates with one overlapping name (`build.provenance`) and two distinct splits. Cleanest: amend D3.4 §`/build` row to split into four gates matching this session's amendment.

### `/build` — Ralph backpressure preserved verbatim

Per `decomposition.md` Child 0001-B: "`build.test-execution` is the existing Ralph backpressure contract preserved unchanged." The amendment specifies the rename (v0.1 ad-hoc identifier → `build.test-execution`) but the predicate logic, the per-iteration loop, the `fix_plan` machinery, the first-FAIL-hash drift detection, the `.ralph/<ticket>/backpressure.jsonl` write, and the lock-acquisition step all carry forward from v0.1 verbatim. The executing Claude Code session reads v0.1's existing predicate logic, renames the identifier, and applies no other changes to this gate.

This is the cheapest part of `/build`'s amendment to apply; the executing session's effort is concentrated in `build.provenance`, `build.pyramid-tampering`, and `build.finalize` evaluators.

### `/build` — F-Int-3 disposition in `/Chains` subsection

The amendment appends a new subsection "Interaction with sidecar commands" to the existing `/Chains` block (sealed in `child_B_chains_sections.md` Pattern C Group F variant). The subsection specifies:

- `/build-kill <ticket>` writes `cascade:run-state.kill_in_progress = "<ticket>"` + increments `queue_version` in a single write.
- The Group F chat's Stop hook reads `kill_in_progress` at every safe boundary; if set for the active ticket, halts with `§kill-received-remote`.
- `/cascade-halt` (founder-initiated, not `/build-kill`) writes `cascade:run-state.manual_halt = "<ticket>"`; halts with `§manual-halt-pending`.
- The two flags are mutually exclusive.

The `§kill-received-remote` and `§manual-halt-pending` halt codes are not in v0.1's `halt-messages.md` nor in Child A's `halt-messages-append.md` — they were authored in D2.3 v1.2 amendments per F-Int-3. **Surfaced item in §Surfaced items #4** for v0.1 verification at apply-time.

### `/wrap` — naming-only amendment, but four gates instead of D3.4's three

Per `decomposition.md` Child 0001-B: "Behavior unchanged from D2.1 v2; naming standardized for `solo-verify` parity." The amendment is a renaming pass: every predicate is a v0.1 carry-forward with a new identifier.

The gate count split: D3.4 §Per-stage gate inventory `/wrap` row names three gates (`wrap.provenance`, `wrap.product-docs-mirrored`, `wrap.label-transition`); AC-10 names four (`wrap.provenance`, `wrap.tests-green`, `wrap.mirror-sha-match`, `wrap.linear-state-updated`). AC-10's split is more granular — `wrap.tests-green` is a distinct gate from mirror-sha-match.

The amendment uses **AC-10's four-gate split**. Rationale: a tests-green failure surfaces a different halt (`§wrap-tests-red`) than a mirror-sha failure (`§product-doc-mirror-drift`); surfacing them as separate gates is clearer at `solo-verify --list-gates` and `solo-verify --explain` time.

**Surfaced item in §Surfaced items #3.** D3.4 §/wrap row should be amended to match AC-10's four gates. One-line edit.

### `/verify` — the most substantive amendment

This is the largest single change in Child 0001-B by a wide margin. v0.1's `/verify` had a flat per-child check (the D2.1 v2 "perceptual gate evidence or N/A for non-UI" pattern that D3.1 explicitly closed). v0.2 replaces that with:

1. Two pre-flight gates (`verify.provenance`, `verify.child-completion`).
2. Per-child strategy dispatch — read each child's strategy from `/specify` manifest, route to `verify.perceptual-evidence` or `verify.invariance`.
3. Hybrid children recurse one level into their grandchildren (depth cap enforced by recursion-depth parameter; deeper halts `§hybrid-nesting-too-deep`).
4. Multi-child halt-card aggregation — every child stands alone in the milestone roll-up; no precedence selection across children.
5. `children_gate_outcomes[]` schema write per D3.4 §Manifest schema additions; refactor-spike children also record `seal_pass_set_count` and `verify_pass_set_count`.
6. Aggregation gate (`verify.milestone-aggregation`) that runs after the per-child loop and composes the milestone halt card if any child halted.

The amendment specifies all five gates' evaluator logic verbatim — predicate-by-predicate. The executing Claude Code session has the complete pseudocode for the per-child loop, the strategy dispatch, the recursion handling, the per-predicate evidence re-read, and the milestone-aggregation composition.

**Implementation cost note for the executing session:** the per-child loop's re-running of perceptual tests (P2) and invariance capture commands (P8) is the most expensive part of any cascade stage. Per D3.4 §Per-strategy gate-run cost notes, this is by design — `/verify` is the place where re-verification cost is paid. v0.2 always re-runs; v0.2.x may add `--trust-build` for milestones with many children.

### `/verify` — hybrid nesting recursion

The `evaluate_child_gate(child, recursion_depth)` function takes a `recursion_depth` parameter, defaulting to 0. When a child has `decomposition_strategy == "hybrid"`, the function recurses into the child's grandchildren with `recursion_depth + 1`. If `recursion_depth >= 1` at recurse-time, the function halts with `§hybrid-nesting-too-deep`.

This enforces D3.4's "one level of hybrid nesting in v0.2" constraint at runtime, complementing the `/plan` Gate 2 Predicate 4's upstream check from the prior session's amendment. Both checks fire: `/plan` catches it at decomposition.md write time; `/verify` catches it at milestone-aggregation time as a defensive backstop.

### `/verify` — reads `child_strategies[]` from `/plan`'s manifest

The amendment specifies that the per-child loop reads each child's strategy from the child's own `/specify` manifest (via `input_provenance` chain from `/wrap`). The previous session's `/plan` amendment introduced a `child_strategies[]` array on `/plan`'s manifest outputs as a flat lookup — `/verify` can read this instead of walking the full chain to each child's `/specify` manifest.

The amendment uses the chain-walk pattern (per-child `/wrap` → `/build` → ... → `/specify`) as the canonical source of truth, with `child_strategies[]` as an optional optimization. v0.2 implements the chain-walk; v0.2.x may switch to the `child_strategies[]` lookup if `/verify` pre-flight cost becomes a bottleneck.

### Multi-child halt-card shape — verbatim from D3.4

The milestone halt card shape in the `/verify` amendment §Multi-child halt aggregation is copied verbatim from D3.4 §Across children at /verify. No deviation; the example uses the same field order and indent as D3.4.

This is the canonical shape both `/verify` (in chat) and `solo-verify verify <milestone>` (CLI) emit. The `solo-verify` CLI binding lives in D3.4 §`solo-verify` CLI surface — out of this session's scope; in Child 0001-D's scope.

---

## Surfaced items for founder ratification

Four items.

### Surfaced item #1 — Three `/review` halt codes may not exist in v0.1

The `/review` Gate 2 amendment references three halt codes from D3.4 §Per-stage gate inventory `/review` row:

- `§four-hat-incomplete` (with four sub-cases: `priming-text-missing`, `objections-section-missing`, `seal-line-missing`, `objection-entry-malformed`)
- `§four-hat-objections-unresolved`
- `§four-hat-ac-list-drift` (also `§four-hat-ac-list-drift/objection-refs-stale` sub-case)

These are not in Child A's `halt-messages-append.md` (which authored the fourteen new Phase 3 halts: D3.2's two, D3.3's six, D3.4's three, D3.1's three). They are presumably v0.1 carry-forwards from the F-1 fix shipped in v0.1 (the four-hat verification machinery is core to D2.1 v2).

**Two paths:**

  1. **Verify-at-apply-time.** The executing Claude Code session checks v0.1 `halt-messages.md` for these three codes; if present, no action; if absent, the executing session adds minimal cards using the predicate text already in the amendment as diagnostic content.
  2. **Author now in a small append.** This session or the next authors halt cards as `halt-messages-append-2.md`.

**Recommendation:** path 1. The cards are mechanical extensions of the predicate text already in the amendment.

### Surfaced item #2 — `/build` four-gate split vs D3.4's three-gate inventory

D3.4 §Per-stage gate inventory `/build` row names three gates: `build.provenance` (composes chain check + pyramid-tampering), `build.test-execution`, `build.finalize`. AC-9 names three gates: `build.provenance` (chain check only), `build.pyramid-tampering`, `build.test-execution` (composes test-execution + finalize).

The amendment uses **four gates**: `build.provenance` (chain only), `build.pyramid-tampering` (D3.2's predicate), `build.test-execution` (Ralph loop), `build.finalize` (manifest-write preconditions). The split is more granular than either D3.4 or AC-9 alone but composes both — D3.4's `build.finalize` is a distinct gate (for `solo-verify --explain build.finalize`); AC-9's `build.pyramid-tampering` is a distinct gate (for `solo-verify --explain build.pyramid-tampering`).

**Recommendation:** amend D3.4 §`/build` row to match the four-gate split. Two-row edit:

  - Split D3.4's `build.provenance` into two rows: one for chain-check-only `build.provenance`, one for `build.pyramid-tampering`.
  - Keep D3.4's `build.test-execution` and `build.finalize` rows as-is.

Also amend AC-9 to enumerate four gates rather than three. One-line edit. Both amendments absorb into the same small amendment pass as the prior session's Surfaced item #1 (gate-name reconciliation across D3.4 ↔ spec.md AC-6/AC-7).

### Surfaced item #3 — `/wrap` four-gate split vs D3.4's three-gate inventory

D3.4 §Per-stage gate inventory `/wrap` row names three gates: `wrap.provenance`, `wrap.product-docs-mirrored`, `wrap.label-transition`. AC-10 names four gates: `wrap.provenance`, `wrap.tests-green`, `wrap.mirror-sha-match`, `wrap.linear-state-updated`.

AC-10's split is more granular: separates `wrap.tests-green` (red-tests-block predicate) from `wrap.mirror-sha-match` (fs-Linear sha match). The amendment uses AC-10's four-gate split.

**Recommendation:** amend D3.4 §`/wrap` row to match AC-10's four-gate split. Split `wrap.product-docs-mirrored` into `wrap.tests-green` (D2.1 v2 red-tests-block predicate) and `wrap.mirror-sha-match` (D2.1 v2 fs-Linear sha match predicate). Rename `wrap.label-transition` to `wrap.linear-state-updated`. One-and-a-half-row edit in D3.4. Absorb into the same amendment pass.

### Surfaced item #4 — `§kill-received-remote` and `§manual-halt-pending` halt codes

The `/build` amendment's `/Chains` subsection references two halt codes from D2.3 v1.2 amendments per F-Int-3:

- `§kill-received-remote` — fires when `/build-kill` is invoked from a sidecar chat mid-Ralph and the Group F chat's Stop hook reads the flag.
- `§manual-halt-pending` — fires when `/cascade-halt` is founder-initiated mid-Ralph.

These are referenced in D2.3 v1.2 §Group F per-skill semantics but their full halt-card text may not be in either v0.1 `halt-messages.md` or Child A's `halt-messages-append.md`.

**Two paths:**

  1. **Verify-at-apply-time** (same as Surfaced item #1).
  2. **Author at Child 0001-C** when `.claude/hooks/stop-orchestrator.sh` is authored. The hook script's diagnostic text becomes the halt-card content.

**Recommendation:** path 2. Child 0001-C is the natural place — the hook script wires these halts, and the halt-card content is best authored alongside the hook predicate.

---

## Other notes

### Failing-test seeds for the four skills' amendments

Per `decomposition.md` Child 0001-B's failing-test seed list:

  - **`test_review_skill_subagent_stop_hook_fires`** — `[integration]` — asserts the SubagentStop hook predicate evaluates the four-hat transcript and emits the correct top-level Stop / SubagentStop output shape; covers AC-8.
  - **`test_build_skill_rejects_tampered_pyramid`** — `[integration]` — asserts `/build`'s pre-flight halts `§pyramid-shape-violation/shape-tampering` on a seed file whose tag set differs from the sealed parent's `pyramid_shape`; covers AC-9.
  - **(AC-10 / `/wrap`)** — `decomposition.md` does not name a specific test because the amendment is naming-only. The next-session author of Child 0001-D may sketch `test_wrap_skill_gate_names_match_solo_verify` `[integration]` as part of `tools/solo-verify --list-gates` parity verification.
  - **`test_verify_skill_dispatches_per_strategy`** — `[integration]` — asserts each of the five strategies routes to the documented gate set; covers AC-11.
  - **`test_verify_skill_writes_children_gate_outcomes`** — `[integration]` — asserts the sealed `/verify` manifest contains the documented `children_gate_outcomes[]` schema; covers AC-11.

Four `[integration]` tests for four AC; AC-10 is covered by `/wrap` carry-forward tests (the v0.1 wrap tests verify the v0.1 predicate behavior; the rename doesn't change the test surface).

### v0.1 reconciliation pattern for all four skills

None of the four v0.1 `.claude/skills/{review,build,wrap,verify}/SKILL.md` byte-for-byte content surfaced in `project_knowledge_search`. The amendments are authored as patch-ready blocks under the "amendments by purpose, not by line" pattern Child A established. The executing Claude Code session locates v0.1's equivalents by the step's purpose; substitutes per the amendment block; carries forward unchanged anything the amendment doesn't touch.

This is consistent with the prior session's `/specify` + `/plan` amendments and with `child_A_spec_template_and_halts_authoring_notes.md`'s "v0.1 byte-for-byte content not in KB — apply-time reconciliation required" section.

---

## Forward references and lockstep amendments queued

### Queued amendment pass before executing Claude Code sessions

Per the prior session's notes and predecessor sessions:

  - **Parent spec `spec.md` AC-2 amendment:** "eleven new Phase 3 halts" → "fourteen new halts" (from predecessor session).
  - **D3.3-vs-decomposition.md per-runner command divergence:** swap three buggy commands (from predecessor session).
  - **`.solo-locks/` path discrepancy:** root-level accepted (from predecessor session).
  - **`spec.md` AC-6 + AC-7 + `decomposition.md` Child 0001-B gate-name reconciliation:** five-name swap across three docs (from prior session).

This session adds:

  - **D3.4 §`/build` row** + **`spec.md` AC-9 gate-name reconciliation** (Surfaced item #2): split D3.4's row into four gates matching AC-9 + this session's split; amend AC-9 to enumerate four rather than three.
  - **D3.4 §`/wrap` row** + **`spec.md` AC-10 gate-name reconciliation** (Surfaced item #3): split D3.4's row into four gates matching AC-10's split.

Total amendment-pass scope: 4 D3.4 row edits + 4 spec.md AC edits + 1 decomposition.md edit + carryover edits from prior sessions = roughly 25 minutes of edits across `D3.4_gate_definitions.md`, `spec.md`, `decomposition.md`. Absorb in a single pass before the Child A executing Claude Code session runs.

### Subsequent design sessions after this one

  - **Child 0001-B continuation 2** — `/onboard`, `/retro`, `/update-linear` SKILL.md amendments. Setup + terminal + mirror cluster. Three skills. Includes the deferred `workflow.default_strategy` wiring (`/onboard` step 7 elicits and writes; this resolves the wiring-deferred pattern from the prior session). Includes F-Int-5 (D1's `/onboard` step 3 numeric reference fix). Includes F-Usr-3 (Project Instructions step 5 acknowledgment).
  - **Child 0001-C** — `.claude/hooks/` infrastructure (six hook scripts) + `.claude/settings.json` wiring. Walking-skeleton strategy. One session likely sufficient. Authors `§kill-received-remote` and `§manual-halt-pending` halt cards in `stop-orchestrator.sh`'s scope per Surfaced item #4.
  - **Child 0001-D** — `tools/solo-verify` Python stdlib script implementing D3.4's CLI surface. Walking-skeleton with heavy `[unit]` coverage. One to two sessions.
  - **Child 0001-E** — `CLAUDE.md` and `README.md` amendments + lockstep update to `docs/templates/CLAUDE.md`. Walking-skeleton. One session.

Total Phase-2-design sessions remaining after this one: ~4–5.

### Carried-forward queued items not absorbed in this session

Per the prior session's notes; none block continuation 2.

  - **F-Rev-2** — D4.5 per-stage `--reconcile` flag-set disposition. Surfaces in Child 0001-D.
  - **F-Eng-4 / F-Int-2** — Stop-hook output shape for `next_chain_step` Task-invoke. Surfaces in Child 0001-C.
  - **F-Eng-5** — chat-Claude multi-MCP-call atomicity for `.cascade/handoff/last.md` write. v0.2.x.
  - **F-Eng-6** — chat-Claude 9-check predicate failure modes uncatalogued. v0.2.x measurement deferral (M-5).
  - **F-Usr-3** — Project Instructions step 5 acknowledgment. **Surfaces in Child 0001-B continuation 2.**
  - **F-Int-5** — D1 step-7 housekeeping. **Surfaces in Child 0001-B continuation 2.**
  - Ten lower-priority amendments queued for v0.2.x (F-Usr-1, F-Usr-2, F-Usr-4, F-Usr-5, F-Rev-1, F-Rev-3, F-Rev-4, F-Rev-5, F-Int-4).

---

## Handoff prompt for next session

> **Title:** 0001 integration spec Child 0001-B continuation 2 — `/onboard` + `/retro` + `/update-linear` SKILL.md amendments.
>
> **Task:** Author the `/onboard`, `/retro`, `/update-linear` SKILL.md amendments per `decomposition.md` Child 0001-B files-in-scope. Three skills; the setup + terminal + mirror cluster. Capability-cluster strategy per parent. This session closes Child 0001-B's design phase.
>
> **Should fit in one session.** All three skills are smaller than the four runtime-evaluator skills in Child 0001-B continuation 1: `/onboard` is the most substantive (creates six Linear projects per D1, writes config, prompts founder for `workflow.default_strategy`); `/retro` reads `children_gate_outcomes[]` and surfaces tag distribution + per-gate counts; `/update-linear` evaluates a single gate.
>
> **Three concrete deliverables:**
>
>   1. **`.claude/skills/onboard/SKILL.md` amendments per AC-13** — creates the **six** Linear projects per D1 (Product / Architecture / Design / Milestones / Backlog / Done), with marker-prefixed names if `linear.project_naming = "prefixed"` (set by step 1 scan). Creates the Status document under the Product project. Writes `docs/.solo-config.json` with `marker` populated. Includes an **optional** product-level default strategy slot (per D3.1 §`/onboard` product-level default — `workflow.default_strategy` key, empty string by default, prompt at step 7 with a "skip" option). Evaluates `onboard.linear-projects` and `onboard.config-write` gates from D3.4. **The `workflow.default_strategy` write resolves the wiring-deferred pattern from Child 0001-B continuation 0's `/specify` step 1 read.**
>
>   2. **`.claude/skills/retro/SKILL.md` amendments per AC-12** — reads `children_gate_outcomes[]` from `/verify` manifests, surfaces tag distribution (count children per strategy: "this milestone shipped 12 children — 9 walking-skeleton, 2 capability-cluster, 1 refactor-spike") and per-gate outcome counts (e.g., "11/12 children passed `verify.perceptual-evidence`; 1 halted on `§perceptual-evidence-missing/byte-stability-failed`"). Per `decomposition.md`'s row: "tag distribution and per-gate outcome counts." Single gate per D3.4 §Per-stage gate inventory `/retro` row: `retro.doc-sealed` (Linear retro doc exists with sealed sha; Status doc lessons-line updated).
>
>   3. **`.claude/skills/update-linear/SKILL.md` amendments per AC-13** — evaluates the `update-linear.diff-applied` gate from D3.4 (each ticket's current Linear state matches `diff_sha256`; Linear-sync sanity check passes per D2.1 v2 §Linear-sync). Single gate; mostly naming-only standardization with the same v0.1-carry-forward pattern as `/wrap`.
>
> **Read first (use `project_knowledge_search`):**
>
>   - `00_PROJECT_INSTRUCTIONS.md`
>   - This session's five deliverables — `review-SKILL-amendments.md`, `build-SKILL-amendments.md`, `wrap-SKILL-amendments.md`, `verify-SKILL-amendments.md`, `child_B_review_build_wrap_verify_authoring_notes.md` — for the patch-ready amendment pattern, the gate-evaluator shape, and the surfaced-items context.
>   - **All prior Child 0001-B deliverables** — `specify-SKILL-amendments.md`, `plan-SKILL-amendments.md`, `child_B_specify_plan_authoring_notes.md` from Child 0001-B continuation 0; the `/specify` step 1's `workflow.default_strategy` read pattern is the contract this session's `/onboard` step 7 write satisfies.
>   - `D1_linear_product_layer.md` §`/onboard` changes (the six Linear projects, the Status document, the `/onboard` step amendments).
>   - `D1` §Linear product layer (the six-project layout, the marker-prefix convention, the Status-doc-as-fabrication-detector framing).
>   - `D3.1_decomposition_negotiation.md` §`/onboard` product-level default (the `workflow.default_strategy` slot's product-level intent).
>   - `D3.4_gate_definitions.md` §Per-stage gate inventory `/onboard`, `/retro`, `/update-linear` rows.
>   - `D3.4_gate_definitions.md` §Manifest schema additions (the `children_gate_outcomes[]` shape `/retro` reads).
>   - `decomposition.md` Child 0001-B files-in-scope rows for the three skills.
>   - `repo-state-summary.md` Part 2 (v0.1 SKILL.md existence + amendment-vs-rewrite shape for each).
>   - `spec.md` AC-12, AC-13.
>
> **Context:**
>
>   - **`/onboard` is Child 0001-B's most substantive remaining skill.** It creates the six Linear projects, writes the Status document, writes `docs/.solo-config.json`, and now prompts for `workflow.default_strategy`. The product-level default flows through to `/specify` step 1 as the proposal seed (per the prior session's `/specify` step 1 amendment, which reads-but-tolerates-empty until `/onboard` ships the write side). This session's amendment closes that loop.
>
>   - **F-Int-5 disposition** (D2.3 v1.2 four-hat review): D1's `/onboard` step 3 reference to "reuse existing /onboard step 7" is to v0.1's step 7, not v1.2's new step 7 (which is the new Project Instructions paste-block render). When this session amends `/onboard`'s SKILL.md, update D1's reference to be descriptive ("reuse existing v0.1 north-star seeding subroutine") rather than numeric. Amendment lands in D1, not in this skill — but the trigger is this session.
>
>   - **F-Usr-3 disposition** (Project Instructions step 5 acknowledgment): per the prior-session notes, F-Usr-3 surfaces in continuation 2. If the `/onboard` step amendments include rendering the Project Instructions block, F-Usr-3's resolution lives in this skill. Verify scope at the top of the session.
>
>   - **`/retro` is informational.** Per D3.4 §`/retro` row: "No hard gates. `/retro` is informational and produces findings, not predicate evaluations." The single `retro.doc-sealed` gate is at-write — confirms the retro doc was sealed with a sha and the Status doc's lessons line was updated. The skill's substantive work is reading `children_gate_outcomes[]` from `/verify` manifests and rendering structured summaries; no predicate-evaluation complexity.
>
>   - **`/update-linear` is the smallest.** Single gate, mostly naming-only standardization. The `update-linear.diff-applied` gate evaluates that each ticket's current Linear state matches `diff_sha256`. v0.1 carries the predicate; this session renames.
>
>   - **`workflow.default_strategy` wiring closure.** The prior session's `/specify` step 1 amendment reads `docs/.solo-config.json`'s `workflow.default_strategy` and falls through to first-principles if empty. This session's `/onboard` step 7 prompts the founder to set the slot (with a "skip" option per D3.1 §`/onboard` product-level default). After this session: the slot is fully wired end-to-end; the read becomes load-bearing without further skill amendments.
>
> **Failing-test seeds for these three skills' amendments** (verbatim from `decomposition.md` Child 0001-B's seed list):
>
>   - `test_onboard_skill_creates_six_linear_projects` — `[integration]` — asserts `/onboard` creates Product, Architecture, Design, Milestones, Backlog, and Done projects with marker-prefixed names when `linear.project_naming = "prefixed"`; covers AC-13.
>   - `test_onboard_skill_writes_workflow_default_strategy_when_set` — `[integration]` — asserts `/onboard` step 7 elicits a strategy choice with a skip option and writes the selected value (or empty string on skip) to `docs/.solo-config.json`'s `workflow.default_strategy` field; covers AC-13.
>   - `test_retro_skill_surfaces_tag_distribution` — `[integration]` — asserts `/retro` reads `children_gate_outcomes[]` from a mocked `/verify` manifest with three strategies represented and renders the documented "shipped N children — A walking-skeleton, B api-boundary, C capability-cluster" summary; covers AC-12.
>   - `test_retro_skill_surfaces_per_gate_outcomes` — `[integration]` — asserts `/retro` renders per-gate outcome counts including a halt case (e.g., "11/12 passed verify.perceptual-evidence; 1 halted on §perceptual-evidence-missing/byte-stability-failed"); covers AC-12.
>   - `test_update_linear_skill_evaluates_diff_applied_gate` — `[integration]` — asserts `/update-linear` halts `§linear-state-inconsistent` when a ticket's current Linear state diverges from `diff_sha256`; covers AC-13.
>
> **Phase:** Child 0001-B continuation 2 (capability-cluster strategy — per-skill scope, per-skill manifest, per-skill failing-test seed). **This session closes Child 0001-B's design phase.** After this session: all 9 of Child 0001-B's skills are designed; ready for the executing Claude Code session against `OndraMasek/Solo-Vibing`. Remaining Phase-2 design sessions: Child 0001-C (hooks + settings.json), Child 0001-D (solo-verify CLI), Child 0001-E (CLAUDE.md + README).
>
> **Deliverables:**
>
>   - `.claude/skills/onboard/SKILL.md` amendments (patch-ready).
>   - `.claude/skills/retro/SKILL.md` amendments (patch-ready).
>   - `.claude/skills/update-linear/SKILL.md` amendments (patch-ready).
>   - `child_B_onboard_retro_update_linear_authoring_notes.md` — notes doc covering: the `workflow.default_strategy` wiring closure pattern (the founder-prompt UI + skip handling + write side), F-Int-5 disposition (D1 step-3 numeric reference fix), F-Usr-3 disposition (if Project Instructions render is in scope), the `/retro` rendering schema, and any newly surfaced items.
>   - Handoff prompt for the next session: "Child 0001-C — `.claude/hooks/` infrastructure (six hook scripts: preflight-provenance, pyramid-tampering, four-hat-objection-coverage, stop-orchestrator, session-start-state-restore, session-end-telemetry) + `.claude/settings.json` wiring. Walking-skeleton strategy. Includes Stop-hook output shape for `next_chain_step` Task-invoke (F-Eng-4 / F-Int-2). Includes `§kill-received-remote` and `§manual-halt-pending` halt-card authoring (per Child 0001-B continuation 1 Surfaced item #4)."

---

## Cross-references

- **D2.1 v2 §Subagent verification** — binding for `/review` Gate 2's parent-writes-subagent-manifest pattern.
- **D2.1 v2 §Provenance binding (F-2 fix)** — binding for the AC-list-hash chain enforced across `/review` Gate 3, `/build` Gate 1, `/wrap` Gate 1, `/verify` Gate 1.
- **D2.1 v2 §`/review`, `/build`, `/wrap`, `/verify` rows** — upstream manifest schema baselines; all four amendments are additive.
- **D2.2 §Stop / SubagentStop output schema quirk** — binding for `/review` Gate 2's top-level-fields-only hook output shape.
- **D2.2 §Hook/script surface** — binding for `/build` Gate 2's PreToolUse hook output (using the standard `hookSpecificOutput` wrapper, contrasting with SubagentStop's quirk).
- **D2.3 v1.2 four-hat review §F-Int-2** — binding for the factual-phrasing pattern in `/review` Gate 2 hook output.
- **D2.3 v1.2 four-hat review §F-Int-3** — binding for `/build`'s `/Chains` "Interaction with sidecar commands" subsection.
- **D3.1 §Decomposition strategy** — binding for `/verify`'s per-child strategy read from each child's `/specify` manifest.
- **D3.2 §Downstream consumer touch-points** — binding for `/build` Gate 2's pre-flight pyramid-tampering predicate.
- **D3.3 §Walking-skeleton / Api-boundary / Capability-cluster perceptual predicate** — P1–P4 binding text for `/verify` Gate 3's `verify.perceptual-evidence`.
- **D3.3 §Refactor-spike invariance predicate** — P5–P9 binding text for `/verify` Gate 4's `verify.invariance`.
- **D3.3 §Halt conditions** — `§perceptual-evidence-missing` (with sub-cases), `§invariance-pass-set-regression`, `§invariance-seal-tampering`, `§invariance-config-changed`, `§invariance-config-missing` — referenced by halt-code across `/verify`'s per-child evaluators.
- **D3.4 §Per-stage gate inventory** rows for `/review`, `/build`, `/wrap`, `/verify` — gate firing order and predicate references.
- **D3.4 §Aggregation rules** — within-a-gate and across-children semantics applied to all four amendments.
- **D3.4 §`/verify` gate dispatch by strategy** — binding for `/verify`'s per-child loop.
- **D3.4 §Manifest schema additions** — `children_gate_outcomes[]` schema for `/verify`'s outputs.
- **D3.4 §hybrid-nesting-too-deep** — the v0.2 one-level cap enforced in `/verify`'s recursion guard.
- **Child A `spec.md.template`** — read by `/review` Gate 3 (§Acceptance criteria parsing).
- **Child A `halt-messages-append.md`** — referenced by all four amendments by halt-code where applicable; surfaced items #1 and #4 flag halt codes that may not be present.
- **Child A `solo-config.json`** + **Child A `solo-config.example.json`** — read by `/verify` Gate 4 at P7/P8.
- **Child A `.gitignore`** — `docs/specs/*/invariance/pass-set-at-verify.txt` excluded; `/verify` writes it freshly every run.
- **`child_B_chains_sections.md`** — `/Chains` blocks for `/review`, `/build`, `/wrap`, `/verify` were sealed in a prior session; this session's amendments land BEFORE the `/Chains` blocks in each SKILL.md.
- **`plan-SKILL-amendments.md`** (Child 0001-B continuation 0) — `child_strategies[]` array on `/plan`'s manifest read by `/verify`'s per-child loop as an optional optimization.
- **Child 0001-C** `.claude/hooks/four-hat-objection-coverage.py` — wraps `/review` Gate 2's predicate as a SubagentStop hook.
- **Child 0001-C** `.claude/hooks/pyramid-tampering.sh` — wraps `/build` Gate 2's PreToolUse predicate.
- **Child 0001-C** `.claude/hooks/stop-orchestrator.sh` — reads `kill_in_progress` and `manual_halt` per `/build`'s `/Chains` subsection.
- **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md`** AC-8, AC-9, AC-10, AC-11 — this session's four amendments satisfy these four ACs as authored, modulo gate-name reconciliation per Surfaced items #2 and #3.
