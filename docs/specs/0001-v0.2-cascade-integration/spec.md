# 0001 — v0.2 cascade integration

**Status:** Draft (hand-authored bootstrap; cascade not yet running in v0.2 form).
**Type:** Framework self-application — lands v0.2 cascade primitives into the framework's own repo.
**Strategy:** `hybrid` — parent flag; per-child strategies declared in `decomposition.md`.
**Marker:** `SOL` (per the framework's own `docs/.solo-config.json`).
**Date authored:** 2026-05-19.

---

## Motivation

The v0.2 design closed in two waves. Phase 2 (D2.1, D2.2, D2.3) defined the **trust model the entire cascade composes against** — manifest provenance, caller-side verification, distributed tainted-state with `--reconcile`-only clearing, `.cascade/` namespace, hybrid session boundaries. Phase 3 (D3.0–D3.4) built the decomposition + test-pyramid + gate-composition stack on top of that trust model:

- **D2.1 v2.1** — trust-model amendment-only pass over D2.1 v2 (per `D2_1_revision_decisions.md` and `D2_3_v1_2_and_D4_6_four_hat_review.md` F-Eng-1). Filesystem-canonical run-state moves to `.cascade/run-state.json`. Substantive trust-model carries from v2: manifest chain + sha-graph, caller-side verification, distributed tainted-state (`is_tainted` + `taint_reason` per manifest), AC-list-only hash, `--reconcile`-only taint clearing (no `/accept-taint` button).
- **D2.2** — hook event surface, single-Stop-orchestrator pattern, SubagentStop output-schema quirk, settings precedence.
- **D2.3 v1.3** — hybrid session boundary with `/onboard` step 7 wiring the initial run-state at the v2.1 path.
- **D1** — six Linear projects + Status doc, with marker-prefixed naming in multi-product teams.
- **D3.1** — five-strategy decomposition enum (`walking-skeleton`, `api-boundary`, `capability-cluster`, `refactor-spike`, `hybrid`) with `/specify` step-1 proposal + founder-confirm semantics and `/plan` decomposer override findings.
- **D3.2** — per-strategy test-pyramid declaration with a six-tag enum (`unit | integration | contract | smoke | perceptual | invariance`), an additive `pyramid_shape` field on `/specify` manifests, and a `[tag]`-per-test convention in `## Failing-test seed`.
- **D3.3** — concrete predicates for `[perceptual]` (per strategy: PNG byte-equality for walking-skeleton; markdown integration transcript for api-boundary; canonical extension-per-type for capability-cluster) and `[invariance]` (pass-set membership for refactor-spike), with `artifact_path` / `artifact_type` manifest additions and runner-agnostic `invariance.pass_set_capture_command` configuration.
- **D3.4** — a gate composition layer (22 named gates across 8 stages), per-strategy dispatch matrix at `/verify`, multi-failure aggregation rules, `children_gate_outcomes[]` on `/verify` outputs, and a fully enumerated `solo-verify` CLI surface (per-stage / per-gate / `--list-gates` / `--explain`, five exit codes).

The v0.1 framework — currently at https://github.com/OndraMasek/Solo-Vibing — has eleven cascade skills, six commands, seven subagents, six always-on rules, a worked-example sealed spec (`docs/specs/0001-wrap-build-log/`), centralized `halt-messages.md`, a `spec.md.template`, and a `bootstrap.sh` entry path. **It has no hooks** (CLAUDE.md explicitly states "no hooks in v0.1"), no `solo-verify` CLI, no pyramid declaration, no perceptual/invariance predicates, no gates abstraction, no manifest taint mechanics, and no CI. The Linear product layer is documented in D1 as a v0.2 delta but is not yet implemented in `/onboard`.

This spec lands those primitives into the existing repo so the framework becomes self-runnable under v0.2. After this spec ships, a subsequent session can run `/onboard` + `/specify` on a real non-meta feature to validate the cascade end-to-end on itself — the dogfood test.

The integration is intentionally scoped to **mechanical landings of Phase 2 + Phase 3 + selected Phase 4 design**. It does not introduce v0.3 design decisions; D4.x cleanup items (`/plan --drop-child`, `--reconcile` formalization beyond the consolidated chain-recovery halt, versioned `gates.json`, telemetry on `children_gate_outcomes[]`) stay deferred per the carry-forward thread.

Related research: see `D2_1_trust_model_v2_1.md`, `D2_1_revision_decisions.md`, `D2_2_hook_surface_research.md`, `D2_2_session_auto_management.md`, `D2_3_hybrid_session_boundary_v1_3.md`, `D1_linear_product_layer.md`, `D3_0_test_pyramid_research.md`, `D3_1_decomposition_negotiation.md`, `D3_2_test_pyramid_declaration.md`, `D3_3_perceptual_and_invariance_predicates.md`, `D3_4_gate_definitions.md`, `D4_1_template_bug_batch.md` (denylist § D4.1.7), `D4_2_skill_splitting.md` (code-markers carry-forward), `D0_1_repo_strategy.md` (CI provider).

---

## Acceptance criteria

Every AC below is covered by at least one child in `decomposition.md`. The parent has no failing-test seed at this grain (hybrid).

- **AC-1.** `docs/templates/spec.md.template` carries the **Pyramid shape** preamble line in `## Failing-test seed`, the per-test `— [tag] —` notation, and three rendering variants (regular for walking-skeleton/api-boundary/capability-cluster; refactor-spike no-tests; hybrid no-parent-shape). Per D3.2 §Spec template addition.
- **AC-2.** `docs/templates/halt-messages.md` carries the eleven new Phase 3 halts: `§pyramid-shape-violation` (with six sub-cases), `§pyramid-tag-invalid` (D3.2); `§perceptual-evidence-missing` (with five sub-cases), `§invariance-pass-set-regression`, `§invariance-config-missing` (with three sub-cases), `§invariance-pass-set-empty`, `§invariance-seal-tampering`, `§invariance-config-changed` (D3.3); `§strategy-annotation-unresolved`, `§verify-milestone-aggregation-failed`, `§provenance-chain-broken` (D3.4). Each follows the existing halt-message structure (When / Recommendation / Rationale / Alternatives / Diagnostic context).
- **AC-3.** `docs/.solo-config.json` template (and its `.example.json` sibling) carries an `invariance.pass_set_capture_command` slot (empty string default), with per-runner commented examples for `pytest`, `vitest`, `jest`, `go test`, `cargo test` in `.example.json`. Per D3.3 §Refactor-spike invariance predicate.
- **AC-4.** A new file `docs/templates/capability-artifact-types.md` exists, lists the seven canonical type-extension mappings from D3.3 §Capability-cluster perceptual predicate (`rendered-document` → `.pdf`, `image` → `.png`, `scheduled-event` → `.ics`, `share-post` → `.md`, `email` → `.eml` or `.md`, `api-response` → `.json`, `plain-text` → `.txt`), and is referenced by the `/specify` skill at step 3 for capability-cluster `artifact_type` resolution.
- **AC-5.** `.gitignore` excludes `docs/specs/*/invariance/pass-set-at-verify.txt`; committed-empty directory skeletons exist for `.cascade/manifests/`, `.cascade/halt/`, `.solo-locks/`, `.ralph/`, and `docs/product/` (each with a `.gitkeep` carrying a one-line purpose comment).
- **AC-6.** `.claude/skills/specify/SKILL.md` step 3 implements the pyramid populator from the D3.2 catalog (cached as a const block in the skill), the per-test `[tag]` resolution rules, `artifact_path` drafting per D3.3 (walking-skeleton `.png` under `perceptual/`, api-boundary single `integration-transcript.md`, capability-cluster from `docs/templates/capability-artifact-types.md`), and `artifact_type` recording for capability-cluster entries. Step 7 evaluates the five `spec.*` gates from D3.4 (`spec.strategy-annotation`, `spec.pyramid-shape`, `spec.failing-test-seed`, `spec.perceptual-artifact-path`, `spec.provenance`). Strategy step-1 annotation must clear before seal per D3.4 §strategy-annotation-unresolved.
- **AC-7.** `.claude/skills/plan/SKILL.md` evaluates the `plan.*` gates per D3.4 (`plan.provenance`, `plan.children-have-strategies-for-hybrid`, `plan.decomposition-doc-sealed`); D3.1 decomposition-override findings flow through standard incorporate/defer/reject pattern and write to `decomposition.md` under each child's block as a `Strategy:` field.
- **AC-8.** `.claude/skills/review/SKILL.md` evaluates the `review.*` gates per D3.4; the four-hat objection-coverage check fires as the cascade's **single** agent-type hook on `SubagentStop` per D2.2 §Stop / SubagentStop output schema quirk.
- **AC-9.** `.claude/skills/build/SKILL.md` evaluates the `build.*` gates per D3.4 (`build.provenance`, `build.pyramid-tampering`, `build.test-execution`), preserves the seed-as-backpressure contract unchanged, and pre-flights a pyramid-tampering check per D3.2 §Downstream consumer touch-points.
- **AC-10.** `.claude/skills/wrap/SKILL.md` evaluates the `wrap.*` gates per D3.4 (`wrap.provenance`, `wrap.tests-green`, `wrap.mirror-sha-match`, `wrap.linear-state-updated`); behavior is materially unchanged from D2.1 v2 — naming only for `solo-verify` parity.
- **AC-11.** `.claude/skills/verify/SKILL.md` dispatches per strategy per D3.4 §verify gate dispatch by strategy: walking-skeleton / api-boundary / capability-cluster → `verify.perceptual-evidence` (D3.3 P1–P4); refactor-spike → `verify.invariance` (D3.3 P5–P9); hybrid → recursive per child (one level of nesting in v0.2; deeper halts `§hybrid-nesting-too-deep`). Multi-child halt-card aggregation per D3.4 §Aggregation rules. Writes `children_gate_outcomes[]` on the `/verify` manifest per the schema in D3.4 §Manifest schema additions.
- **AC-12.** `.claude/skills/retro/SKILL.md` reads `children_gate_outcomes[]` from `/verify` manifests, surfaces tag distribution (e.g., "this milestone shipped 12 children — 9 walking-skeleton, 2 capability-cluster, 1 refactor-spike") and per-gate outcome counts.
- **AC-13.** `.claude/skills/onboard/SKILL.md` creates the **six** Linear projects per D1 (Product / Architecture / Design / Milestones / Backlog / Done), creates the Status document under the Product project, writes `docs/.solo-config.json` with `marker` populated, and includes an **optional** product-level default strategy slot (per D3.1 §`/onboard` product-level default — slot is optional, flows through to first `/specify` if set). `.claude/skills/update-linear/SKILL.md` evaluates the `update-linear.diff-applied` gate.
- **AC-14.** `.claude/hooks/` directory exists with deterministic shell predicates (bash for file-exists / sha256 / pass-set diff; Python for any structured-data manipulation): pre-flight provenance check, pyramid-tampering check fired at `/build`, four-hat objection-coverage check fired on `SubagentStop`. `.claude/settings.json` wires the hooks to the events from D2.2 §Hook events (PreToolUse, PostToolUse, SubagentStop, SessionStart source=startup/resume/compact, SessionEnd, Stop), using the single Stop-hook orchestrator pattern per D2.2 research-step resolution #3. Includes a `PreToolUse` denylist hook reading `.claude/agents/build-write-denylist.txt` per AC-21 / D4.1.7.
- **AC-15.** `tools/solo-verify` is a Python stdlib script implementing the full CLI surface from D3.4 §`solo-verify` CLI surface: per-stage invocations (`solo-verify onboard|specify|review|plan|update-linear|build|wrap|verify|retro <id>`), `--gate <name>`, `--list-gates [stage]`, `--explain <stage>.<gate-name>`, and exit codes 0 (all passed), 1 (standard halt), 2 (stage/gate unknown), 3 (manifest chain broken / provenance halt), 4 (filesystem-or-Linear inconsistency that prevents evaluation). Each gate's predicate logic is mirrored from the skill's verifier so the CLI can evaluate without Claude in the loop (the max_turns / resume gap per D2.2 critical caveat #1). Predicates evaluate taint state from manifest `is_tainted` (AC-18) and surface `--reconcile` as the recovery recommendation per D2.1 v2.1's consolidated chain-recovery halt.
- **AC-16.** `CLAUDE.md` is amended to reflect Phase 2 + Phase 3 primitives — drops the v0.1 "no hooks" sentence; adds a §Cascade gates section pointing at `docs/templates/halt-messages.md` and `solo-verify --list-gates`; adds §Strategy enum referencing `/specify` step 1; adds §Hooks referencing `.claude/settings.json`; adds §Tainted state pointing at AC-18's manifest fields and the `--reconcile`-only clearing path; adds §Code markers pointing at AC-19's `🤔/📝/☣️` convention; adds §CI pointing at AC-20's GitHub Actions workflow. The CLAUDE.md template at `docs/templates/CLAUDE.md` is amended in lockstep so future `/onboard` runs render the v0.2 version.
- **AC-17.** `README.md` is amended with a v0.2 announcement line in the Status block and a brief §What's new in v0.2 section listing the cascade primitives now in scope (gates, hooks, `solo-verify`, pyramid declaration, perceptual/invariance predicates).
- **AC-18.** Manifest schema carries `is_tainted: bool` and `taint_reason: string|null` per manifest, populated by the producing stage and read by downstream verifiers. `cascade:run-state.tainted_count` (derived integer) replaces v2-draft's `tainted_artifacts[]`. Taint clears only via `--reconcile` against the responsible stage (D4.5); no `/accept-taint` waiver button. Status-doc rendering reads taint from manifests at render time. Per `D2_1_revision_decisions.md` decisions 5 + 7 and D2.1 v2.1.
- **AC-19.** In-code marker convention extends v0.1's `🤔` (clarify question) and `📝` (copy pending) with `☣️` (tainted code region — implementation written against a manifest that has since been marked `is_tainted: true`, requires `--reconcile` re-evaluation). The convention is declared in a new `.claude/rules/code-markers.md` rule and surfaced in CLAUDE.md §Code markers. Per D4.2 §D4.4-deferred (markers convention now finalized in v0.2) and `D2_1_revision_decisions.md` decision 5.
- **AC-20.** A GitHub Actions workflow at `.github/workflows/ci.yml` runs on every PR and on push to `main`. The workflow runs (1) `python3 tools/solo-verify --list-gates` as a smoke check and (2) `python3 -m unittest discover tests/solo-verify/` as the test seed gate. Per D0.1 §CI workflow (GitHub Actions confirmed as the v0.2 CI provider per SOL-HANDOFF-008 decision 2) and D4.0 §CI workflow. Free tier, public repo. The synthetic-spec end-to-end CI test (D0.1's "framework's CI runs the cascade against a synthetic minimal spec") is scoped to v0.2.x.
- **AC-21.** `.claude/rules/write-discipline.md` gains a **denylist + reviewer-stance** section: a denylist of cascade-control file globs at `.claude/agents/build-write-denylist.txt` (per D4.1.7) enforced by the `PreToolUse` hook for hard halts; plus a reviewer-stance soft-check inside `/review` that surfaces write-discipline findings as auditor-voice observations (per `.claude/rules/auditor-stance.md`) without blocking when ambiguity exists. The soft-check is **not** a hard allow-list — allow-list semantics are explicitly out per SOL-HANDOFF-008 decision 3.

---

## Decomposition strategy

**Declared strategy:** `hybrid`. Per D3.1 §hybrid, this parent strategy is a flag, not a guide — every child must carry an explicit non-inherited strategy in `decomposition.md`. Per D3.2, the parent's `pyramid_shape` is `null` and the parent's `failing_test_seed[]` is empty; per-child shapes and seeds live in each child's spec.

_Annotation cycle (informal, per the bootstrap context — the cascade isn't yet running so the step-1 / step-5 annotation cycle from D3.1 is collapsed)._

- **Step 1 — proposal.** `hybrid`, because the integration spans five qualitatively different concerns (templates+config, skill-MD amendments, hook scripts, a new Python CLI, docs prose). A single non-hybrid strategy would either (a) force capability-cluster on all five and lose the walking-skeleton signal that templates and docs are end-to-end-shaped, or (b) force walking-skeleton on all five and lose the capability-cluster signal that the skill-MD amendments are nine independent capabilities. The two-strategies-or-more test from D3.1 is met.
- **Step 5 — founder-confirm.** Confirmed in this hand-authored draft. The next session may revise during repo execution if the inventory surfaces a reason to consolidate or split.

_The annotation "proposed by /specify; founder to confirm" required by D3.4 §spec.strategy-annotation is cleared here by the affirmative step-5 confirm._

---

## Failing-test seed

**Pyramid shape:** `null` (hybrid).

_Per D3.2 §hybrid, hybrid parents carry no parent-level pyramid shape and no parent-level failing-test seed. Per-child pyramid shapes and per-child seeds are declared in each child's `spec.md` and populated by `/specify` at child creation. `/plan`'s decomposer halts `§hybrid-without-child-overrides` if any child lands without an explicit strategy (and thus without a pyramid shape)._

**Tests at parent grain.** None.

---

## Related research findings

The Phase 2 + Phase 3 design docs and selected Phase 4 docs are the source material this spec executes against. Each AC traces to one or more of:

- **D2.1 v2.1 — trust model (amendment + carry-forward from v2).** Filesystem-canonical run-state at `.cascade/run-state.json`; manifest chain + caller-side verification; AC-list-only hash; distributed tainted-state with `--reconcile`-only clearing per `D2_1_revision_decisions.md` decisions 3, 4, 5, 7. Anchors every gate's predicate framing, AC-15 (`--reconcile`), AC-18 (taint mechanics), AC-19 (☣️ marker).
- **D2.2 — hook surface + session auto-management.** Hook events + matchers + settings precedence + Stop / SubagentStop output schema quirk + single Stop-hook orchestrator pattern. Anchors AC-14 (hook infrastructure).
- **D2.3 v1.3 — hybrid session boundary.** `/onboard` step 7 writes the initial run-state at the v2.1 path; per-resource write locks; chat-end card handoff prompt. Anchors AC-13 (onboard).
- **D1 — Linear product layer.** Six Linear projects + Status doc + marker prefix in multi-product teams. Anchors AC-13 (onboard).
- **D3.0 — test-pyramid research findings.** Cohn pyramid baseline, Spotify Honeycomb / Trophy, Rainsberger integration-vs-integrated. Anchors AC-1 (template) and AC-6 (specify-skill pyramid populator).
- **D3.1 — decomposition negotiation.** Five-strategy enum + signals + milestone-shape map + override-finding flow + `/onboard` product-level default slot. Anchors AC-6 (specify step 1 annotation), AC-7 (plan override flow), AC-13 (onboard default-strategy slot).
- **D3.2 — test-pyramid declaration.** Six-tag enum + per-strategy shape catalog + manifest schema addition + halts §pyramid-shape-violation / §pyramid-tag-invalid + per-strategy spec template variants. Anchors AC-1, AC-2 (D3.2 halts), AC-6, AC-9 (build pyramid-tampering pre-flight).
- **D3.3 — perceptual and invariance predicates.** Walking-skeleton PNG byte-equality, api-boundary single-markdown-transcript shape, capability-cluster canonical type table, refactor-spike pass-set parity with `invariance.pass_set_capture_command`, six new halts. Anchors AC-2 (D3.3 halts), AC-3 (config slot), AC-4 (artifact-types doc), AC-5 (.gitignore for verify pass-set), AC-6, AC-11.
- **D3.4 — gate composition.** 22 gates × 8 stages firing order + per-strategy dispatch matrix + multi-failure aggregation + `children_gate_outcomes[]` + full `solo-verify` CLI surface + three new halts. Anchors AC-2 (D3.4 halts), AC-6 through AC-13 (per-stage gates), AC-15 (CLI parity).
- **D4.1 §D4.1.7 — cascade-control denylist.** Anchors AC-21 (write-discipline denylist + PreToolUse hook).
- **D4.2 §D4.4-deferred — code markers convention.** Anchors AC-19 (☣️ marker, now finalized in v0.2 per SOL-HANDOFF-008 decision 1b).
- **D0.1 — repo strategy.** GitHub Actions confirmed as the v0.2 CI provider per SOL-HANDOFF-008 decision 2. Anchors AC-20 (CI workflow).

---

## Open questions

Surfaced during repo inventory and to be resolved by the founder (or by a subsequent session) before child-spec authoring. None of these blocks the parent-spec seal under hybrid; per-child specs may halt on individual items.

### Counter collision on spec-number 0001

The carry-forward handoff suggested the slug `0001-v0.2-cascade-integration`. The existing repo carries `docs/specs/0001-wrap-build-log/` as Solo-Setup's own worked-example sealed spec (called out in README as "Not shipped to forks"). Counter discipline (per the always-on rule `.claude/rules/counter-allocation.md`) would normally allocate `0002-...` next.

**Recommendation, pending founder confirm:** rename this parent to `0002-v0.2-cascade-integration`. The carry-forward instruction overrides counter discipline only if the founder intends to retire `0001-wrap-build-log` (move it to `docs/examples/` or delete). Both paths are valid; the founder picks at spec-execution time. Until then this document lives at the suggested path `0001-v0.2-cascade-integration` per the handoff, with the collision flagged here.

### CLAUDE.md amendment vs wholesale rewrite

The existing CLAUDE.md at the repo root (60 lines, 5.4 KB) is the framework's own session-instruction layer — not a template — and carries v0.1 truths that v0.2 contradicts (notably "no hooks in v0.1"). The CLAUDE.md template at `docs/templates/CLAUDE.md`, which `/onboard` renders for forks, is a separate file.

The v0.2 amendments are local (drop "no hooks" sentence; add gates / hooks / strategy-enum subsections) and amount to roughly 15–25 net new lines, not a rewrite. **Recommendation:** amendment, not rewrite, for both files in lockstep. Children A and E own the two files respectively; child E coordinates the diff.

### `docs/templates/capability-artifact-types.md` — v0.2 or v0.2.x?

D3.4 §Carry-forward flags this doc as a v0.2.x consideration ("promote to v0.2 if cheap"). The inventory finding is that a 30-line markdown file rendering the seven-row canonical table from D3.3 is materially cheaper than encoding the same table inline in the `/specify` skill's frontmatter and amending the skill on every v0.2.x row addition. **Recommendation, pending founder confirm:** promote to v0.2 — author it in child A.

### `/onboard` product-level default strategy slot — v0.2 or v0.2.x?

D3.1 names the slot as optional and "flows through if present"; D3.4 §Carry-forward names "/onboard product-level default strategy" as a Phase 4 cleanup. The inventory finding is that `/onboard` already writes `docs/.solo-config.json`, and adding one optional `workflow.default_strategy` key (with empty-string default for "no default") is a 5–10 line skill amendment + a 1-line config key. **Recommendation, pending founder confirm:** ship the slot in v0.2 with the config key empty by default. The behavioral wiring at `/specify` step 1 (consume the slot as the proposal seed) can defer to v0.2.x if budget is tight; the key being on the config file harms nothing in the interim.

### Hook script implementation language — bash vs Python

D2.2 didn't lock. The inventory finding is that the existing `scripts/` directory uses bash (`check_prereqs.sh`, `verify_linear_key.sh`). **Recommendation, pending founder confirm:** bash for trivial predicates (file-exists, sha256, pass-set diff, JSON key-present); Python (matching the `tools/solo-verify` stack) for any predicate that does structured-data manipulation across multiple manifests. Bash hooks live at `.claude/hooks/*.sh`; Python hooks live at `.claude/hooks/*.py` and are invoked from a thin bash wrapper that handles JSON stdin/stdout per Claude Code's hook contract. Child C owns the call.

### `solo-verify` distribution — Python stdlib script vs alternative

D3.4 §Carry-forward parks the distribution decision to D4.0. The inventory finding is that the repo has no committed Python runtime, no `pyproject.toml`, no `requirements.txt`. **Recommendation, pending founder confirm:** Python stdlib (3.10+) single-file script at `tools/solo-verify` with no third-party imports. v0.2.x or D4.0 may reconsider single-binary (PyInstaller / `pex` / `nuitka`) or Bun / Deno alternatives. Shipping a `python3 tools/solo-verify` invocation is acceptable for the v0.2 floor.

### Worked-example spec — keep or retire under v0.2?

`docs/specs/0001-wrap-build-log/` is the v0.1 worked example. Two paths:

1. **Retire** to `docs/examples/0001-wrap-build-log/` (or delete) once `0001-v0.2-cascade-integration` (this spec) lands as the new canonical worked example. Cleaner; one fewer file to mentally distinguish.
2. **Keep in place** as a v0.1-shaped reference for fork-time learning — adopters can see both shapes.

**Recommendation, pending founder confirm:** retire to `docs/examples/0001-wrap-build-log/v0.1.md` with a one-line README note pointing forks at this v0.2 spec as the current shape. This also resolves the counter-collision open question (above) — `0001` is freed for v0.2 use.

### Existing `four-hat-build-SKILL.md` etc. — current skill names vs Phase 3 references

The carry-forward thread named "current skill refs (build-SKILL.md, specify-SKILL.md, four-hat-build-SKILL.md) needed to compute v0.1 → v0.2 deltas." The repo's actual skill files live at `.claude/skills/<stage>/SKILL.md` (per the standard Claude Code skill layout — confirmed in README). The carry-forward names appear to be flat references from an earlier-iteration filename convention. **No action needed in this spec**; child B operates on the correctly-pathed `SKILL.md` files. Flagging here only to retire the carry-forward names so the next session does not search for them in vain.

### `four-hat-panel` agent layout

The README lists `four-hat panel` among `.claude/agents/`. D3.4 names the four-hat objection-coverage check as the cascade's single agent-type hook, encapsulated inside the `spec.four-hat-seal` gate at `/review`. **The inventory could not verify the agent layout** (robots.txt blocks directory listings; subdir contents not accessible via web_fetch in this session). Child B's first task is to view the agents directory and confirm the agent's frontmatter shape before amending the SubagentStop hook predicate to match.

---

## Notes for the executing session

- **The cascade is not yet running.** This spec is the bootstrap. Subsequent sessions can use the cascade on itself (`/onboard` was already run for v0.1; `/specify` against the existing 0001-wrap-build-log shape is the closest v0.1 analog). The dogfood test — running the v0.2 cascade against a real non-meta feature — is a separate session after this one ships.
- **The spec is runnable.** Each child in `decomposition.md` names full paths and content sketches for every file to create or modify. Claude Code, given this spec + the five Phase 3 design docs in context, can execute the integration mechanically.
- **D4.x cleanup items are explicitly out of scope.** `/plan --drop-child`, `--reconcile` formalization, versioned `gates.json`, telemetry on `children_gate_outcomes[]`, hybrid-nesting-beyond-one-level edge case — all deferred per the carry-forward thread.
- **`docs/templates/capability-artifact-types.md` and the `/onboard` product-level default strategy slot** are flagged in Open Questions as v0.2-vs-v0.2.x decisions. The default recommendation is **ship in v0.2** for both, on cost-vs-friction grounds.
- **SOL-HANDOFF-008 decisions reflected in this revision.** (1a) Trust-model first: D2.1 v2.1 leads Related-research; v2 references retired. (1b) Tainted-mode mechanics from `D2_1_revision_decisions.md` decisions 5 + 7 land as AC-18; the in-code marker convention from D4.2's deferred D4.4 lands as AC-19 with the glyph finalized as `☣️`. (2) GitHub Actions confirmed as the v0.2 CI provider per D0.1 — lands as AC-20. (3) Denylist + reviewer-stance soft-check (no allow-list) lands as AC-21, building on D4.1.7's cascade-control denylist.
- **What lands in this PR vs v0.2.x.** AC-18's manifest schema field additions (`is_tainted`, `taint_reason`) — the field-level schema change is **declared** here but the cross-manifest schema-bump lands in v0.2.x with a Linear issue (existing manifest readers are unaffected since they ignore unknown fields). AC-19's `.claude/rules/code-markers.md` lands in this PR as a small additional file. AC-20's `.github/workflows/ci.yml` lands in this PR. AC-21's `.claude/agents/build-write-denylist.txt` + amendment to `.claude/rules/write-discipline.md` land in this PR; the PreToolUse denylist hook itself is in Child C's scope.
