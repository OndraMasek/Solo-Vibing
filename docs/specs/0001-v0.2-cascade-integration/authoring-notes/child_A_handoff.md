# Handoff — Solo Claude Stack, next session

**Authored:** 2026-05-19, end of "0001 integration spec Child A starts — chat-end-card.md authoring" session.
**Prior session deliverable:** two artifacts authored — `chat-end-card.md` (the canonical group-exit card template per D2.3 v1.3 §Chat-end card template; four variants encoded with HTML comment markers using the additive-deltas-from-normal scheme) and `child_A_chat_end_card_authoring_notes.md` (variant-encoding decision, F-Usr-3 disposition, failing-test seed for Child A's chat-end card slice, round-trip property statement, surfaced items for founder).

One item surfaced for founder ratification: variant-encoding choice (single-file additive-deltas-from-normal scheme as authored vs four-complete-bodies-in-one-file vs four separate files). Recommendation in the notes doc is the as-authored scheme. F-Usr-3 deferred from this session as orthogonal to template authoring; surfaces in subsequent Child A (Project Instructions text authoring) or Child C (hook output shape authoring).

---

## Next session: Child A continuation — `spec.md.template` amendments per D3.2 and `halt-messages.md` appendage

**Task:** 0001 integration spec Child A continuation — author the two largest remaining Child A items per `decomposition.md` Child 0001-A files-in-scope:

  1. Amend `docs/templates/spec.md.template` per D3.2 §Spec template addition — add `**Pyramid shape:**` preamble line with strategy-shaped placeholders, add per-test `— [tag] —` notation, provide three rendering variants for the §Failing-test seed section (regular for walking-skeleton/api-boundary/capability-cluster, refactor-spike no-tests-with-anchor-language, hybrid no-parent-shape with deferral-to-children language).
  2. Append eleven new halts to `docs/templates/halt-messages.md` per the union of D3.2, D3.3, and D3.4 halt-conditions sections — using the existing halt-card structure (When / Recommendation / Rationale / Alternatives / Diagnostic context).

These two are scoped together because they're both authoring work against existing template files, and together they form the "spec discipline" half of Child A (the other half — config templates, gitignore, gitkeep files — is the next-session-after).

**Phase:** Child 0001-A continuation (walking-skeleton strategy).

---

## Read first (use `project_knowledge_search`)

  - `00_PROJECT_INSTRUCTIONS.md`
  - `D3_2_test_pyramid_declaration.md` §Spec template addition (the binding spec for the `spec.md.template` `## Failing-test seed` section amendments — the **Pyramid shape:** preamble syntax, per-test `[tag]` notation rules, and the three rendering variants)
  - `D3_2_test_pyramid_declaration.md` §Halt conditions (the §pyramid-shape-violation, §pyramid-tag-invalid halt cards)
  - `D3_3_perceptual_and_invariance_predicates.md` §Halt conditions (the §perceptual-evidence-missing, §invariance-pass-set-regression, §invariance-config-missing, §invariance-pass-set-empty, §invariance-seal-tampering, §invariance-config-changed halt cards)
  - `D3_4_gate_definitions.md` §Halt conditions (the §strategy-annotation-unresolved, §verify-milestone-aggregation-failed, §provenance-chain-broken halt cards)
  - `D3_1_decomposition_negotiation.md` §Spec template addition (already lands the `## Decomposition strategy` section between `## Scope boundary` and `## Acceptance criteria` — confirm whether v0.1 → v0.2 amendment work already absorbed this; if not, fold it into this session's `spec.md.template` amendment scope)
  - `D3_1_decomposition_negotiation.md` §Halt conditions (§strategy-missing, §strategy-conflict-unresolved — likely already in halt-messages.md from D3.1's earlier amendment work; verify before re-adding)
  - `decomposition.md` Child 0001-A scope (files-in-scope row for `spec.md.template` and `halt-messages.md`)
  - `repo-state-summary.md` Part 1 (the v0.1 `docs/templates/` contents — `spec.md.template`, `halt-messages.md` both exist already; the amendment is in-place)
  - `child_A_chat_end_card_authoring_notes.md` (prior-session notes; variant-encoding decision pattern used in `chat-end-card.md` may inform the three rendering variants for `spec.md.template`'s §Failing-test seed section)

---

## Context

- **`spec.md.template` is in-place amendment, not a rewrite.** The v0.1 template already exists at `docs/templates/spec.md.template` per `repo-state-summary.md` Part 1. The D3.2 amendment adds a `**Pyramid shape:**` preamble and per-test tag notation INSIDE the existing `## Failing-test seed` section. Three rendering variants for that section reflect the three strategy classes: (a) walking-skeleton / api-boundary / capability-cluster (the "regular" pyramid case); (b) refactor-spike (no tests; the failing-test seed becomes an invariance-pass-set capture command per D3.3); (c) hybrid (no parent-level pyramid; defers shape declaration to children).

- **The variant-encoding precedent.** Per `decomposition.md` Child 0001-A notes ("spec.md.template variant rendering is conditional text in markdown, not Jinja or similar. Three alternative `## Failing-test seed` blocks live in the same file, each preceded by an HTML comment `<!-- variant: walking-skeleton -->` etc. The `/specify` skill at step 3 selects the variant by reading the declared strategy"), the established convention is HTML comment markers. The `chat-end-card.md` deliverable (prior session) followed this convention. The next-session author should match.

- **D3.1's `## Decomposition strategy` section may already be present.** D3.1 amended `spec.md.template` with a new `## Decomposition strategy` section between `## Scope boundary` and `## Acceptance criteria`. Verify whether this amendment is already in the v0.1 template (it may have been authored as part of a prior implementation pass) or whether this session needs to fold it in alongside the D3.2 amendments.

- **The eleven new halts are the union of D3.2, D3.3, D3.4 halt cards.** Per `decomposition.md` Child 0001-A: "Order: §pyramid-shape-violation, §pyramid-tag-invalid (D3.2); §perceptual-evidence-missing, §invariance-pass-set-regression, §invariance-config-missing, §invariance-pass-set-empty, §invariance-seal-tampering, §invariance-config-changed (D3.3); §strategy-annotation-unresolved, §verify-milestone-aggregation-failed, §provenance-chain-broken (D3.4)." D3.1's §strategy-missing and §strategy-conflict-unresolved are likely already present from D3.1's prior amendment work; confirm before re-adding to avoid duplicates.

- **Halt-card structure is fixed.** Per v0.1 `halt-messages.md`, each halt uses When / Recommendation / Rationale / Alternatives / Diagnostic context. Sub-cases live inside Diagnostic context (per `decomposition.md`: "Sub-cases listed inside Diagnostic context per D3.2's existing pattern"). The next-session author copies this structure for the eleven new halts.

- **F-Usr-3 may surface here if the Project Instructions text is also under Child A scope.** Per the prior-session notes (F-Usr-3 disposition), the Project Instructions block step 5 acknowledgment may need simplification. If `decomposition.md` Child 0001-A includes Project Instructions text as a templates item (e.g., a `docs/templates/project-instructions.md` template), F-Usr-3's resolution lives here. Verify scope.

- **No round-trip property for `spec.md.template` and `halt-messages.md`.** Unlike `chat-end-card.md`'s round-trip with D4.6 v1.1, these two files don't have a re-derivation counterparty. The correctness criterion is simpler: render-time validation by `/specify` at seal (D3.4's spec gates), surfaced as halts at the existing `halt-messages.md`-rendered halt cards. The next session doesn't need to design a round-trip; it just needs the templates to be correct per their binding specs.

---

## Task instructions

Session has two phases. The two phases are roughly equal weight; budget ~50% each.

**Phase 1 — amend `docs/templates/spec.md.template` per D3.2 (target ~50% of session budget):**

  1. Identify the current v0.1 `## Failing-test seed` section content (via `project_knowledge_search` against the prior SDG-style template or the v0.1 framework template inventory; if the search doesn't surface the exact wording, surface to founder for paste).
  2. Author the **Pyramid shape:** preamble line per D3.2 §Spec template addition. Syntax: `**Pyramid shape:** <strategy>-shaped; required: [unit, integration]; optional: [perceptual]; forbidden: [smoke]` (or whatever the D3.2 binding spec sets).
  3. Author the per-test `— [tag] —` notation rule for the **Tests.** subsection — each test in the list gains a `[tag]` annotation indicating which pyramid layer it lives in.
  4. Author the three rendering variants:
     - `<!-- variant: walking-skeleton -->` (also serves api-boundary and capability-cluster per the regular-pyramid case)
     - `<!-- variant: refactor-spike -->` (no-tests, with anchor-language pointing to D3.3's invariance-pass-set capture command)
     - `<!-- variant: hybrid -->` (no parent-level pyramid, deferral-to-children language)
  5. Encode using HTML comment markers per the `chat-end-card.md` precedent (single file, comment markers; the additive-vs-alternative encoding is a per-content decision — see if any of the three rendering variants share enough content to use deltas, otherwise author each as a complete alternative block).
  6. If D3.1's `## Decomposition strategy` section isn't already present, fold it in alongside the D3.2 amendments.

**Phase 2 — append the eleven new halts to `docs/templates/halt-messages.md` (target ~50% of session budget):**

  1. Identify the current v0.1 `halt-messages.md` structure (the existing halt-card When/Recommendation/Rationale/Alternatives/Diagnostic context pattern).
  2. Author the eleven new halt cards in the order specified by `decomposition.md` Child 0001-A:
     - D3.2 halts: §pyramid-shape-violation, §pyramid-tag-invalid
     - D3.3 halts: §perceptual-evidence-missing, §invariance-pass-set-regression, §invariance-config-missing, §invariance-pass-set-empty, §invariance-seal-tampering, §invariance-config-changed
     - D3.4 halts: §strategy-annotation-unresolved, §verify-milestone-aggregation-failed, §provenance-chain-broken
  3. Place sub-cases inside Diagnostic context per D3.2's existing pattern (some halts have multiple sub-cases — e.g., §pyramid-shape-violation might fire for shape-mismatch, missing-required-tag, present-forbidden-tag).
  4. Verify §strategy-missing and §strategy-conflict-unresolved (D3.1 halts) aren't accidentally re-added if already present.

**At session end:** the failing-test seeds for both files. Sketch the smoke tests Child A's `/specify` will need:
  - `test_spec_template_has_pyramid_shape_preamble` — `[smoke]`
  - `test_spec_template_has_three_rendering_variants` — `[smoke]`
  - `test_halt_messages_has_eleven_new_halt_codes` — `[smoke]` (asserts each of the eleven `§<halt-code>` substrings is in the file)
  - `test_halt_messages_no_duplicate_halt_codes` — `[unit]` (asserts no halt code appears more than once — guards against re-adding D3.1 halts)

---

## Deliverable

  - `docs/templates/spec.md.template` — amended in-place (the actual content drop; this lands in the framework repo via the executing Claude Code session, alongside the other Child A items in a single pass).
  - `docs/templates/halt-messages.md` — appended in-place.
  - `child_A_spec_template_and_halts_authoring_notes.md` — a notes doc describing the variant-encoding decisions for `spec.md.template`'s §Failing-test seed section, the D3.1 absorption status (did this session fold in §Decomposition strategy or was it already there), and the failing-test seeds.
  - Handoff prompt for the next session: "Child A continuation — author the remaining config templates (`docs/templates/.solo-config.json.template` invariance block + default_strategy slot; `docs/.solo-config.json` mirror; `docs/.solo-config.example.json` new file; `docs/templates/capability-artifact-types.md` new file), gitignore updates, and committed-empty-directory `.gitkeep` files."

---

## What lands in the framework repo (not in this project)

The three template files authored across this Child A session sequence (`chat-end-card.md` from the prior session, `spec.md.template` and `halt-messages.md` from this next session, and the config templates / gitkeep files from the session after) are *design deliverables* in this Claude.ai project, *implementation deliverables* in Claude Code against `OndraMasek/Solo-Vibing`.

The implementation pass against the framework repo is a Phase 4 task. It should be scheduled after:

  - Prior session (Child B design — done).
  - This handoff's prior session (Child A `chat-end-card.md` design — done).
  - Next session (Child A `spec.md.template` + `halt-messages.md` design — pending).
  - One more session for the remaining Child A items (config templates, gitignore, gitkeep).
  - Sessions for Child C (`.claude/hooks/` infrastructure), Child D (`tools/solo-verify` CLI), Child E (`CLAUDE.md` and `README.md` amendments) as appropriate.

Then a single multi-skill Claude Code session against the framework repo runs the full integration with all design deliverables in hand. Token-budget discipline per `00_PROJECT_INSTRUCTIONS.md` — split into per-child Claude Code sessions if any one would exceed the 100–200k effective-tokens target.

---

## Important amendments still queued from the v1.2 + D4.6 paired review

For the design owner's awareness in subsequent sessions. None of these block the next session's `spec.md.template` + `halt-messages.md` work; they remain queued for later Child A items, Child C, Child D, or v0.2.x.

**Fully absorbed inline (prior sessions):**
- F-Eng-1 — canonical run-state path `.cascade/run-state.json` (D2.1 v2.1, D2.3 v1.3, D4.6 v1.1, chat-end card template).
- F-Eng-2 / F-Int-1 — `last_group_artifacts[]` schema field dropped; D4.6 v1.1 reads exit manifest's `outputs` directly.
- F-Eng-3 — Group D manual-halt protocol (D2.3 v1.3 §Manual halt protocol).
- F-Int-6 — per-pattern group's exit manifest (D2.3 v1.3 §`/Chains` contract + new schema field `last_completed_group_exit_manifest_path`; D4.6 v1.1 reads it).

**Partially absorbed inline (prior sessions):**
- F-Rev-2 — D4.6 v1.1 §Halt conditions widens §cascade-resume-manifest-chain-broken to cover absent-exit-manifest cases (routed to D4.5 `--rerun=<exit-stage>`). The full F-Rev-2 disposition (per-stage `--reconcile` availability) remains queued for v0.2.x in D4.5's amendment plan.
- F-Int-3 — `/build`'s `/Chains` SKILL.md block carries a "Interaction with sidecar commands" subsection naming the `/cascade-halt` after `/build-kill` flow. The full F-Int-3 disposition (a new halt code `§kill-received-remote` and tighter Group F per-skill semantics) is queued.

**Not absorbed (queued for surfacing during Child B implementation pass or v0.2.x):**
- F-Eng-4 / F-Int-2 — Stop-hook output shape for `next_chain_step` Task-invoke. Likely surfaces during Child C (hook infrastructure) authoring.
- F-Eng-5 — chat-Claude multi-MCP-call atomicity for `.cascade/handoff/last.md` write. May surface during Child B implementation if a SKILL.md edit reveals the gap concretely.
- F-Eng-6 — chat-Claude 9-check predicate failure modes uncatalogued. v0.2.x measurement deferral (M-5).
- **F-Usr-3 — Project Instructions step 5 acknowledgment heavy for project-instruction layer.** Deferred from the prior Child A session (chat-end card was orthogonal). **May surface in the next session if Project Instructions text is in Child A scope** (check `decomposition.md` for `docs/templates/project-instructions.md` or similar); otherwise carries to Child C (hook output shape).

**Ten lower-priority amendments still queued for v0.2.x:** F-Usr-1 (consolidated halt message), F-Usr-2 (`/cascade-halt` auto-detect), F-Usr-4 (D4.6 `--rewrite-file` default), F-Usr-5 (pattern names), F-Rev-1 (M-5 measurement), F-Rev-3 (M-6 measurement), F-Rev-4 (pattern framing), F-Rev-5 (check 4a), F-Int-4 (gate-ordering wording), F-Int-5 (D1 step-7 housekeeping).
