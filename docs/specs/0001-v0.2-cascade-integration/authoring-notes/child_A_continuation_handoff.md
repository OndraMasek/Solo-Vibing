# Handoff — Solo Claude Stack, next session

**Authored:** 2026-05-19, end of "0001 integration spec Child A continuation — `spec.md.template` + `halt-messages.md` authoring" session.

**Prior session deliverable:** three artifacts authored — `spec.md.template` (v0.2-shaped template with D3.2's Pyramid shape preamble + per-test tag notation + three rendering variants for §Failing-test seed; D3.1's §Decomposition strategy section defensively included), `halt-messages-append.md` (append-ready block with **fourteen** new halt cards: the eleven Phase 3 halts per D3.2/D3.3/D3.4 from `decomposition.md` Child 0001-A's specified order, plus the three D3.1 halts folded in per founder ratification of option (a) — see surfaced-items resolution below), and `child_A_spec_template_and_halts_authoring_notes.md` (variant-encoding pattern divergence rationale, D3.1 halts fold-in ratification record, F-Usr-3 disposition, v0.1 byte-for-byte reconciliation note, failing-test seeds for the four spec-discipline smoke/unit tests).

Three items surfaced for founder ratification — all resolved in this session:
  1. **Variant-encoding pattern divergence — ratified as-authored.** chat-end-card.md keeps additive-deltas-from-default; spec.md.template keeps three-complete-alternatives. Both use the same `<!-- variant: <name> -->` marker convention; the application logic differs per template (documented in each template's leading comment block).
  2. **D3.1 halts fold-in — option (a) accepted.** Three halts (§strategy-missing, §strategy-conflict-unresolved, §hybrid-without-child-overrides) folded into `halt-messages-append.md` as halts 12–14. Total halts in the appendage: fourteen.
  3. **Variant marker name — accepted default.** `<!-- variant: regular -->` retained.

**Follow-on action item for the parent spec edit pass.** Parent spec `0001-v0.2-cascade-integration/spec.md` AC-2 currently reads "the eleven new Phase 3 halts." This needs a one-line amendment to "the fourteen new halts, including the three D3.1 halts that enforce the §Decomposition strategy section's surface." This is a parent-spec edit, not a Child A authoring item — schedule it as a small standalone amendment session before the executing Claude Code session runs (or absorb it into the next Child A session if the founder prefers).

Two items deferred:
  - **F-Usr-3** (Project Instructions step 5 acknowledgment) confirmed not in Child A scope; carries to Child 0001-B (`/onboard` skill amendments) or Child 0001-C (`.claude/hooks/` infrastructure).
  - **v0.1 byte-for-byte reconciliation** of `spec.md.template` — the executing Claude Code session must read the actual v0.1 file before applying this session's draft as a patch.

---

## Next session: Child A continuation — remaining config templates, gitignore, gitkeep files

**Task:** 0001 integration spec Child A continuation — author the remaining Child A items per `decomposition.md` Child 0001-A files-in-scope. After this session, Child A's design pass is complete; the executing Claude Code session against `OndraMasek/Solo-Vibing` can run.

Five concrete artifacts:

  1. `docs/templates/.solo-config.json.template` — the rendered-by-`/onboard` config template. Add `"invariance": {"pass_set_capture_command": ""}` block at top level. Add `"workflow": {"default_strategy": ""}` slot (optional, empty default; behavioral wiring deferred per Open Question 4 of the parent spec at `spec.md`).
  2. `docs/.solo-config.json` — the framework's own config (not rendered by `/onboard` for forks; the framework's repo carries its own copy per `repo-state-summary.md`). Same additions; `invariance.pass_set_capture_command` empty (the framework itself does not run refactor-spike on itself in v0.2).
  3. `docs/.solo-config.example.json` — new file. Per-runner commented examples for the invariance capture command (`pytest`, `vitest`, `jest`, `go test`, `cargo test`). Framework reads neither this file nor `.example.json` at runtime — `.solo-config.json` is canonical; the example exists for founder cargo-culting per `decomposition.md` Child 0001-A files-in-scope row.
  4. `docs/templates/capability-artifact-types.md` — new file. Render the seven-row canonical type-extension table from D3.3 §Capability-cluster perceptual predicate verbatim (`rendered-document` → `.pdf`, `image` → `.png`, `scheduled-event` → `.ics`, `share-post` → `.md`, `email` → `.eml` or `.md`, `api-response` → `.json`, `plain-text` → `.txt`). Header note: "Read by `/specify` skill step 3 to resolve `artifact_type` and validate `artifact_path` extension for capability-cluster `[perceptual]` entries. Novel artifact types not in this table use founder-declared extensions recorded on the manifest." Footer note: "Versioned implicitly by D3.3's schema_version; v0.2.x can add rows without breaking sealed manifests."
  5. `.gitignore` amendments + `.gitkeep` files — `.gitignore` excludes `docs/specs/*/invariance/pass-set-at-verify.txt`. Committed-empty directory skeletons exist for `.cascade/manifests/`, `.cascade/halt/`, `.solo-locks/`, `.ralph/`, `docs/product/` — each with a `.gitkeep` carrying a one-line `#`-comment naming the directory's purpose to survive future "what's this empty directory" reviews.

**Phase:** Child 0001-A continuation (walking-skeleton strategy). After this session: Child A design is done; ready for executing Claude Code apply-pass.

---

## Read first (use `project_knowledge_search`)

  - `00_PROJECT_INSTRUCTIONS.md`
  - `D3_3_perceptual_and_invariance_predicates.md` §Capability-cluster perceptual predicate (the seven-row canonical type table for `docs/templates/capability-artifact-types.md` — copy verbatim).
  - `D3_3_perceptual_and_invariance_predicates.md` §Refactor-spike invariance predicate (the `invariance.pass_set_capture_command` semantics and per-runner shape — informs `.solo-config.example.json` per-runner commented examples).
  - `D3_1_decomposition_negotiation.md` §`/onboard` product-level default (the `workflow.default_strategy` slot's behavior — the empty default is intentional; the slot exists for v0.2.x wiring).
  - `decomposition.md` Child 0001-A files-in-scope (the canonical list of these five artifacts with their exact paths and content sketches; quote `decomposition.md` verbatim into the deliverable where possible).
  - `repo-state-summary.md` Part 1 (the v0.1 `docs/templates/` contents — `.solo-config.json.template` exists in v0.1; the others are new files; `.gitignore` exists in v0.1 — the amendment is in-place).
  - `child_A_spec_template_and_halts_authoring_notes.md` (prior-session notes; the v0.1 byte-for-byte reconciliation pattern applies to `.solo-config.json.template` and `.gitignore` as it did to `spec.md.template` and `halt-messages.md` — the executing Claude Code session reads v0.1 first, then patches).
  - `spec.md` AC-3, AC-4, AC-5 (the acceptance criteria these five artifacts collectively satisfy).

---

## Context

- **All five artifacts have explicit content sketches in `decomposition.md` Child 0001-A.** Unlike `chat-end-card.md` (where v1.3 had a full template body) and `halt-messages.md` (where the binding specs were prose), the next-session deliverables are largely mechanical: most of the content is named verbatim in `decomposition.md`. The author's job is structural — pick the right file paths, format the JSON correctly, render the seven-row table.

- **`.solo-config.json.template` is in-place amendment, not a rewrite.** v0.1 already has this file per `repo-state-summary.md` Part 1 (the v0.1 framework's config knobs include `marker`, `cascade-only`/`interactive`/`yolo` cascade behavior knobs, etc.). The amendment adds two new top-level keys: `invariance` (with its sub-key `pass_set_capture_command`) and `workflow` (with its sub-key `default_strategy`).

- **`.solo-config.example.json` is a NEW file.** Per `decomposition.md`: "The framework reads neither this nor the example file at runtime — `.solo-config.json` is canonical. The example exists for founder cargo-culting." The author renders it with per-runner commented examples; runtime behavior is identical to absence of the file.

- **`capability-artifact-types.md` is a NEW file.** Per `decomposition.md`: copy the seven-row table from D3.3 §Capability-cluster perceptual predicate verbatim. Add header + footer notes.

- **`.gitignore` is in-place amendment** — add one line (`docs/specs/*/invariance/pass-set-at-verify.txt`) plus any related patterns. The amendment is small; verify v0.1 doesn't already carry the line (it almost certainly doesn't — invariance was Phase 3 design and isn't in v0.1).

- **`.gitkeep` files are NEW.** Five files, one per directory: `.cascade/manifests/.gitkeep`, `.cascade/halt/.gitkeep`, `.solo-locks/.gitkeep`, `.ralph/.gitkeep`, `docs/product/.gitkeep`. Each carries a one-line `#`-comment naming the directory's purpose. Content sketches are in `decomposition.md`; this is mechanical.

- **The `workflow.default_strategy` slot is wiring-deferred.** Per the parent spec at `spec.md` Open Question 4: "the `workflow.default_strategy` slot ships in v0.2 but behavioral wiring (`/onboard` writing it from a founder prompt; `/specify` reading it as the step-1 proposal seed) is deferred." This session ships the slot empty; the wiring lands in Child 0001-B (`/onboard` and `/specify` skill amendments). The next-session author writes the slot with a comment naming the deferral and pointing at Child 0001-B.

---

## Task instructions

Session has three phases. The first two phases are roughly equal weight; the third is a cleanup phase.

**Phase 1 — author the two config templates and the example (target ~40% of session budget):**

  1. Read v0.1 `docs/templates/.solo-config.json.template` content (via `project_knowledge_search`; if not in KB, surface to founder for paste, OR author the v0.2 amendment as a self-contained "additions to v0.1 template" block in JSON merge-patch shape).
  2. Add the `invariance` and `workflow` top-level blocks. JSON syntax matters — the file is JSON, not JSONC; comments are not legal. Use sibling `_comment_*` keys or annotation `// ...` lines stripped by `/onboard`'s renderer (verify v0.1's convention before authoring).
  3. Mirror the additions into `docs/.solo-config.json` (the framework's own). Same blocks; same empty defaults.
  4. Author `docs/.solo-config.example.json` as a new file. Per-runner examples per `decomposition.md`:
     - pytest: `"pytest -q --tb=no | grep PASSED | sort"`
     - vitest: `"pnpm vitest run --reporter=json | jq -r '.testResults[].assertionResults[] | select(.status==\"passed\") | .fullName' | sort"`
     - jest: `"jest --listTests --testPathPattern=passed | sort"`
     - go test: `"go test -v ./... 2>&1 | grep -E '^--- PASS' | sort"`
     - cargo test: `"cargo test --quiet 2>&1 | grep 'test result' | sort"`
     Each commented with the runner name. Resolve the JSON-doesn't-allow-comments problem with sibling `_comment_*` keys or `// ...` annotation if v0.1 uses that convention.

**Phase 2 — author `capability-artifact-types.md` (target ~30% of session budget):**

  1. Render the seven-row canonical table from D3.3 §Capability-cluster perceptual predicate verbatim. Columns: artifact-type | extension | example | inspection-predicate (per D3.3's table shape; verify column names by reading the binding spec).
  2. Add the header note: "Read by `/specify` skill step 3 to resolve `artifact_type` and validate `artifact_path` extension for capability-cluster `[perceptual]` entries. Novel artifact types not in this table use founder-declared extensions recorded on the manifest."
  3. Add the footer note: "Versioned implicitly by D3.3's schema_version; v0.2.x can add rows without breaking sealed manifests."

**Phase 3 — gitignore + gitkeep files (target ~30% of session budget):**

  1. Author the `.gitignore` patch: add `docs/specs/*/invariance/pass-set-at-verify.txt` plus any related patterns (e.g., `.cascade/handoff/*.tmp` for atomicity-write half-files per D2.3 v1.3 §Group-exit mechanics atomicity step 3-5; verify v0.1 doesn't already carry these).
  2. Author the five `.gitkeep` files. Content for each is a one-line `#`-comment, e.g.:
     - `.cascade/manifests/.gitkeep` → `# manifest-chain artifacts per D2.1 v2.1; populated at runtime`
     - `.cascade/halt/.gitkeep` → `# halt-card diagnostics per D2.2; populated at halt-time`
     - `.solo-locks/.gitkeep` → `# per-resource lock sentinels per D2.1 v2.1 §Locks; populated at lock-acquire`
     - `.ralph/.gitkeep` → `# Ralph automation loop state per D4.2; populated by /build`
     - `docs/product/.gitkeep` → `# product-mirror per D1; populated by /wrap's filesystem-Linear sync`

**At session end:** failing-test seeds for the five artifacts. Sketch the smoke tests Child A's `/specify` will need:
  - `test_solo_config_template_has_invariance_block` — `[smoke]` — asserts `docs/templates/.solo-config.json.template` parses and contains `invariance.pass_set_capture_command`.
  - `test_solo_config_template_has_workflow_default_strategy` — `[smoke]` — asserts the file contains `workflow.default_strategy`.
  - `test_solo_config_example_parses_with_runner_keys` — `[unit]` — per `decomposition.md` AC: parses + at least five runner-name substrings (pytest, vitest, jest, go-test, cargo-test) present.
  - `test_capability_artifact_types_md_lists_seven_rows` — `[smoke]` — per `decomposition.md` AC: markdown table has at least seven data rows.
  - `test_gitignore_excludes_verify_pass_set` — `[smoke]` — per `decomposition.md` AC: `.gitignore` contains the line `docs/specs/*/invariance/pass-set-at-verify.txt`.
  - `test_committed_empty_directories_exist` — `[smoke]` — per `decomposition.md` AC: all five `.gitkeep` files exist.

(All six tests are sketched in `decomposition.md` Child 0001-A's failing-test seed already. The next-session author copies them verbatim into the notes doc.)

---

## Deliverable

  - `docs/templates/.solo-config.json.template` — amended (paste-ready for the executing Claude Code session).
  - `docs/.solo-config.json` — amended (the framework's own config).
  - `docs/.solo-config.example.json` — new file.
  - `docs/templates/capability-artifact-types.md` — new file.
  - `.gitignore` — amended patch (paste-ready).
  - `.cascade/manifests/.gitkeep`, `.cascade/halt/.gitkeep`, `.solo-locks/.gitkeep`, `.ralph/.gitkeep`, `docs/product/.gitkeep` — five new files.
  - `child_A_config_and_gitkeep_authoring_notes.md` — notes doc describing JSON-comments convention chosen, deferred wiring (`workflow.default_strategy` empty-default rationale), the `.gitignore` reconciliation pattern, and the six failing-test seeds.
  - Handoff prompt for the next session: "Child 0001-B start — author the nine `.claude/skills/*/SKILL.md` amendments per `decomposition.md` Child 0001-B. Capability-cluster strategy. Per-skill scope: `/onboard`, `/specify`, `/plan`, `/review`, `/build`, `/wrap`, `/verify`, `/retro`, and any one skill TBD per `decomposition.md` (verify count — Child 0001-B's row says 'nine' but the actual stage count is eleven; check whether `/discovery`, `/constitution`, `/update-linear` are in or out of Child 0001-B scope)."

---

## What lands in the framework repo (not in this project)

The five-artifact set from this next session, plus the prior session's `spec.md.template` and `halt-messages-append.md`, plus the session-before-that's `chat-end-card.md`, are *design deliverables* in this Claude.ai project, *implementation deliverables* in Claude Code against `OndraMasek/Solo-Vibing`.

After the next session: Child A design is complete. The executing Claude Code session for Child A can run, taking all three sessions' deliverables and applying them as a single coherent patch against the framework repo.

Subsequent design sessions cover:
  - **Child 0001-B** — nine (or eleven, TBD) `.claude/skills/*/SKILL.md` amendments. Capability-cluster strategy per `decomposition.md`. Likely 2-3 design sessions split per-skill or per-skill-cluster.
  - **Child 0001-C** — `.claude/hooks/` infrastructure + `.claude/settings.json` wiring. Walking-skeleton strategy. One session likely sufficient.
  - **Child 0001-D** — `tools/solo-verify` Python stdlib script implementing D3.4's CLI surface. Walking-skeleton with heavy `[unit]` coverage. One to two sessions.
  - **Child 0001-E** — `CLAUDE.md` and `README.md` amendments + lockstep update to `docs/templates/CLAUDE.md`. Walking-skeleton (rendered markdown is the perceptual artifact). One session.

Total Phase-2-design sessions remaining: ~6-8 after this one. Token budget per session targets 100–200k effective tokens per `00_PROJECT_INSTRUCTIONS.md`.

---

## Important amendments still queued

For the design owner's awareness in subsequent sessions. None block the next session's config-templates work.

**Fully absorbed inline (prior sessions):**
- F-Eng-1 — canonical run-state path `.cascade/run-state.json` (D2.1 v2.1, D2.3 v1.3, D4.6 v1.1, chat-end card template).
- F-Eng-2 / F-Int-1 — `last_group_artifacts[]` schema field dropped; D4.6 v1.1 reads exit manifest's `outputs` directly.
- F-Eng-3 — Group D manual-halt protocol (D2.3 v1.3 §Manual halt protocol).
- F-Int-6 — per-pattern group's exit manifest (D2.3 v1.3 §`/Chains` contract + new schema field `last_completed_group_exit_manifest_path`; D4.6 v1.1 reads it).

**Partially absorbed inline (prior sessions):**
- F-Rev-2 — D4.6 v1.1 §Halt conditions widens §cascade-resume-manifest-chain-broken to cover absent-exit-manifest cases (routed to D4.5 `--rerun=<exit-stage>`). The full F-Rev-2 disposition (per-stage `--reconcile` availability) remains queued for v0.2.x in D4.5's amendment plan. *(Surfaces in Child 0001-D when `tools/solo-verify` author hits the per-stage `--reconcile` flag set.)*
- F-Int-3 — `/build`'s `/Chains` SKILL.md block carries a "Interaction with sidecar commands" subsection naming the `/cascade-halt` after `/build-kill` flow. The full F-Int-3 disposition (a new halt code `§kill-received-remote` and tighter Group F per-skill semantics) is queued. *(Surfaces in Child 0001-B when `/build`'s SKILL.md is authored.)*

**Not absorbed (queued for surfacing during subsequent design sessions or v0.2.x):**
- F-Eng-4 / F-Int-2 — Stop-hook output shape for `next_chain_step` Task-invoke. *(Surfaces in Child 0001-C — `.claude/hooks/` infrastructure.)*
- F-Eng-5 — chat-Claude multi-MCP-call atomicity for `.cascade/handoff/last.md` write. *(May surface in Child 0001-B if a SKILL.md edit reveals the gap concretely.)*
- F-Eng-6 — chat-Claude 9-check predicate failure modes uncatalogued. v0.2.x measurement deferral (M-5).
- **F-Usr-3 — Project Instructions step 5 acknowledgment.** Confirmed not in this session's scope. *(Surfaces in Child 0001-B when `/onboard` step 7 is authored.)*

**New items surfaced in the prior session (this one's predecessor):**
- **D3.1 halts fold-in disposition.** Recommendation (a) — fold §strategy-missing, §strategy-conflict-unresolved, §hybrid-without-child-overrides into the executing Claude Code session's halt-messages.md pass. Surfaces for explicit founder signoff before apply-pass runs; if signoff is "yes," the executing session adds the three cards in D3.1's binding-spec format.
- **v0.1 byte-for-byte reconciliation pattern.** For every template-amendment session, the executing Claude Code session reads the v0.1 file first, then applies this project's drafts as patches against the actual v0.1 content. This pattern applies in the next session too (`.solo-config.json.template`, `.gitignore`).

**Ten lower-priority amendments still queued for v0.2.x:** F-Usr-1 (consolidated halt message), F-Usr-2 (`/cascade-halt` auto-detect), F-Usr-4 (D4.6 `--rewrite-file` default), F-Usr-5 (pattern names), F-Rev-1 (M-5 measurement), F-Rev-3 (M-6 measurement), F-Rev-4 (pattern framing), F-Rev-5 (check 4a), F-Int-4 (gate-ordering wording), F-Int-5 (D1 step-7 housekeeping).
