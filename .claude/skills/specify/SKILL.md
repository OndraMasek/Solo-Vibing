---
name: specify
description: Author a heavyweight spec for a parent feature through an interactive authoring loop — draft a v1 end-state spec, then a relentless grill-me elaboration phase (one question at a time, recommended answers) raises it to buildable feature- and design-level detail, founder confirms progressively (Gate E0) before four-hat runs. Four-hat dispatch is orchestrated with founder-in-the-loop finding selection (Gate 1) and a post-synthesis review (Gate 2). Produces a sealed parent ticket (label scope:specified), spec markdown at docs/specs/NNNN-<slug>/spec.md, and an append-only four-hat Linear document. On seal, the cascade auto-fires through /plan → /review → /update-linear; user sees a single summary or halt-card at the end. Next user-invoked step is /build <MARKER>-N-K per child ticket. Fires on "/specify <topic>", "specify <topic>", "spec out <topic>", "write a spec for <topic>". Modes: `--continue` resumes the in-progress loop mid-elaboration or mid-gate, `--unseal` archives and rebuilds.
---

# specify

Author parent spec. User-facing entry point of the cascade. On seal, the cascade auto-fires through /plan → /review → /update-linear; the founder sees a single summary or halt-card at cascade end. Next user-invoked step is `/build <MARKER>-N-K` per child ticket.

## Trigger

- User: "/specify <topic>", "specify <topic>", "spec out <topic>", "write a spec for <topic>"
- Resume: "/specify <MARKER>-N --continue" — resumes an in-progress spec
- Unseal: "/specify <MARKER>-N --unseal" — archives the current spec and rebuilds (full re-run)

## Behavior

0. **Preconditions** (any failure halts with `NEEDS_CONTEXT` per `completion-status.md`; halt-card per `docs/templates/halt-messages.md`).

   ### 0.1 — Governing-doc materialization (self-heal, runs before the existence checks)

   `docs/constitution.md` and `docs/product/north-star.md` are authored by chat-Claude, which writes only to Linear and cannot write the repo by design. On the founder's first code-side `/specify`, those files may not yet exist on disk even though their canonical content is sealed in Linear — and no upstream skill owns committing them (the handoff lists them under "PENDING FILESYSTEM COMMITS"). `/specify` materializes them here rather than halting on a precondition nothing else writes.

   Before evaluating the existence checks below, for each of `docs/constitution.md` and `docs/product/north-star.md` that is **absent on disk**:

   1. **Resolve the canonical Linear doc id.** Read, in order, until resolved: `.cascade/handoff/last.md` (the most recent group-exit handoff — it lists the pending governing-doc commits with their `[<MARKER>-DOC-NNNN]` ids); then the `discovery: state` Linear doc; then, failing both, query Linear for the canonical title pattern per `rules/naming.md` (`[<MARKER>-DOC-NNNN] constitution: v<semver>` for the constitution — resolve the **highest** semver as current — and the north-star doc). Also resolve any prior-version constitution docs the handoff names for archive.
   2. **Fetch content** via Linear `get_document` for each resolved id.
   3. **Write the files** (same-turn batch per `rules/write-discipline.md`): `docs/constitution.md` (current version), `docs/product/north-star.md`, and every constitution archive copy at `docs/constitution/archive/v<semver>-<YYYY-MM-DD>.md`, named per the `/constitution` §Outputs convention.
   4. **Commit** the materialized files in one commit whose message references the source Linear doc ids — e.g. `docs(specify): materialize governing docs from [<MARKER>-DOC-0016] constitution v1.1.0, [<MARKER>-DOC-0015] north-star`. Provenance lives in the commit message, not the file body.
   5. **Proceed** to the existence checks, which now pass.

   This is **not** a general-purpose Linear→repo sync. `/specify` materializes only the governing-doc files (constitution + north-star + constitution archive copies). Orphaned research/deep-report files are out of scope.

   ### 0.2 — Existence checks (after materialization)

   - `docs/constitution.md` exists. Missing **after §0.1 materialization** → `NEEDS_CONTEXT` per `§missing-context`. Distinguish the two unrecoverable causes in the diagnostic: (a) **no Linear source** — "constitution absent on disk and no canonical `constitution: v<semver>` Linear doc resolvable (tried handoff, `discovery: state`, title-pattern query); run `/discovery` (approve exit Task-invokes `/constitution`) or `/constitution reseed` if a north-star already exists"; (b) **Linear fetch failed** — "constitution doc `[<MARKER>-DOC-NNNN]` resolved but `get_document` failed; retry when Linear MCP is reachable." Never fabricate constitution content to clear this gate — a missing Linear source is a real halt, not a self-heal case. /review check j and downstream cascade stages assume a constitution; /specify halts here rather than letting the cascade fail three stages deep.
   - `docs/product/north-star.md` exists. Missing after §0.1 → `NEEDS_CONTEXT`, same two-cause split: no resolvable north-star Linear doc → "run `/discovery`"; resolved-but-fetch-failed → retry hint. Never fabricate north-star content.
   - Marker resolvable from `docs/.solo-config.json`. Unset → `NEEDS_CONTEXT`. (§0.1 reads the marker from here too; an unset marker blocks doc-id title-pattern resolution, so this check is reported alongside any materialization failure.)

1. **Load context.**
   - `docs/product/north-star.md`
   - `docs/constitution.md`
   - `docs/onboarding/codebase-map.md` if present (brownfield context)
   - Scope-relevant ADRs from `docs/decisions/*.md`
   - Top 3 research summaries from /discovery Phase 2 closest to spec topic
   - Framing ticket from /discovery if this spec responds to one

   Before proposing a strategy from first principles, read `docs/.solo-config.json` and
   inspect the `workflow.default_strategy` field. If the field is present, non-empty, and
   in the canonical enum `{walking-skeleton, api-boundary, capability-cluster, refactor-spike, hybrid}`,
   use it as the proposal seed — record the proposal as "proposed by /specify from
   `workflow.default_strategy = <value>`; founder to confirm." If the field is absent, an
   empty string, or outside the enum, fall through to the first-principles signal scan
   (greenfield / brownfield, milestone parent, API-contract vs Design & UX vs refactor-pain
   language) and propose from there with the existing annotation "proposed by /specify;
   founder to confirm." The slot's behavioural wiring is v0.2.x; v0.2 treats it as a
   proposal hint only — the founder confirms at step 5 the same way regardless of where
   the proposal came from.

2. **Draft v1 spec — the end state** at `docs/specs/NNNN-<slug>/spec.md` per path conventions in `rules/naming.md`. Use `docs/templates/spec.md.template`. Six sections: Problem statement, Design & UX (or API contract for backend-only), Scope boundary (in/out both explicit), Acceptance criteria (behavior-oriented testable checkboxes), Failing-test seed (populated at step 5 — leave a stub here), Related research findings (verbatim bullets linked to `[<MARKER>-RES-NNN]` summary + deep report). This is an explicit first full pass drafted from the loaded discovery/research context — **not** the sealed draft. The grill-me elaboration at step 3 raises it to buildable detail before anything seals.

3. **Grill-me elaboration phase** (per D3.5 §A).

   After the v1 draft, enter a relentless interview that raises the spec to buildable feature- and design-level detail. The `grill-me` pattern is not installed as a skill in this repo; its mechanics are inlined here (the closest installed analog, `superpowers:brainstorming`, is a sibling pattern, not a substitute — this elaboration phase is `/specify`-owned). Operative mechanics (all are SOL-133 acceptance criteria):

   - **One question at a time.** No multi-question dumps.
   - **Recommend an answer for every question.** The founder confirms or overrides; they are never authoring from a blank page.
   - **Walk the decision tree dependency-ordered.** Resolve upstream decisions before the ones that depend on them; each answer may open or prune downstream branches.
   - **Explore before asking.** If a question is answerable from the codebase, existing specs, ADRs, or discovery/research outputs, resolve it from those sources instead of spending a founder question.
   - **Relentless until shared understanding.** The loop terminates when the spec carries buildable feature- and design-level detail — not after a fixed question count.

   Scope of the interview: *what* features exist, *how* each should behave, edge/error cases, and the **Design & UX** dimension. Design/UX answers populate the spec's Design & UX section (primary flow, key screens, customer journey, edge/error states) with real founder-sourced content — never placeholders.

   After each answer (or a small batch), edit `spec.md` in place so the spec is always the live state of the interview. The partial spec **is** the resumable state for `--continue` (see §Resumability). Record each resolved surface in the spec's **Clarifications** section as it is settled — step 11's clarify-walker reads that section and skips any surface already covered here, avoiding double-questioning.

4. **Progressive presentation + founder confirmation — Gate E0** (per D3.5 §B).

   Once elaboration reaches shared understanding, present the improved spec back **progressively** — never as one wall of spec:

   1. **High-level scope** first (Problem statement + Scope boundary).
   2. **Each feature** (or, for non-feature shapes, the end-solution shape) in turn.
   3. **Each iteration / slice** in detail.

   Chunking is keyed off the decomposition strategy confirmed at step 1: `walking-skeleton` → slices; `capability-cluster` → capabilities; `api-boundary` → contract surfaces; `refactor-spike` → the invariance target; `hybrid` → per-child shape. The founder reviews and refines each part in turn; edits flow back into `spec.md` in place.

   **Gate E0** is the founder's explicit confirmation that the elaborated spec is correct. Four-hat (step 6) does not run until E0 passes. E0 is a **conversational** gate, not a `spec.*` seal gate — it has no manifest predicate and controls flow only. Record the gate state in the `specify_phase` run-state marker (`awaiting-E0` while pending; advance on pass) per §Resumability.

5. **Failing-test seed authoring.**

   Repositioned to run **after elaboration** (steps 3–4) so the seed is authored against the *elaborated* AC list, not the thin v1 draft. Step 5 receives a spec with `## Decomposition strategy` confirmed at step 1, `## Acceptance criteria` elaborated and E0-confirmed, and proceeds to populate `## Failing-test seed`. Three machinery additions over v0.1: a cached D3.2 catalog, per-test `[tag]` resolution rules, and per-strategy `artifact_path` / `artifact_type` drafting.

   ### 5.1 — Catalog cache (const block)

   Embed the D3.2 strategy → pyramid-shape catalog inline in the skill, not as a runtime file-read. Rationale: the catalog is small (five strategies × four fields), evolves at the same cadence as D3.2 itself (slowly), and the runtime-simplicity gain (no JSON load, no file path resolution, no failure mode for missing file) outweighs the maintenance cost of editing the skill when the catalog evolves. The const block is the single source of truth for the skill; D3.2 is the single source of truth for the project.

   ```text
   PYRAMID_CATALOG = {
     "walking-skeleton": {
       "required_tags":   ["smoke", "perceptual"],
       "optional_tags":   ["unit", "integration"],
       "forbidden_tags":  ["contract", "invariance"],
       "integration_anchor": null,
       "artifact_default":   "image"
     },
     "api-boundary": {
       "required_tags":   ["contract", "perceptual"],
       "optional_tags":   ["unit", "integration"],
       "forbidden_tags":  ["smoke", "invariance"],
       "integration_anchor": "consumer-facing-surface",
       "artifact_default":   "integration-transcript"
     },
     "capability-cluster": {
       "required_tags":   ["integration", "perceptual"],
       "optional_tags":   ["unit"],
       "forbidden_tags":  ["smoke", "contract", "invariance"],
       "integration_anchor": "capability-boundary",
       "artifact_default":   null   # founder declares per spec
     },
     "refactor-spike": {
       "required_tags":   ["invariance"],
       "optional_tags":   [],
       "forbidden_tags":  ["unit", "integration", "contract", "smoke", "perceptual"],
       "integration_anchor": null,
       "artifact_default":   null   # invariance artifact, not perceptual
     },
     "hybrid": null   # no parent-level shape; per-child only
   }
   ```

   A catalog mismatch between this block and the D3.2 binding-spec catalog is itself a defect surfaced by `solo-verify --explain spec.pyramid-shape`, which is expected to re-quote the binding spec; periodic audit is a v0.2.x retro task.

   ### 5.2 — Strategy-class dispatch

   Step 5 branches on the value of `## Decomposition strategy`:

   ```text
   strategy ← read §Decomposition strategy from the draft spec
   shape    ← PYRAMID_CATALOG[strategy]

   if strategy == "hybrid":
       populate §Failing-test seed using the hybrid variant of spec.md.template
           (the variant whose HTML comment marker reads <!-- variant: hybrid -->)
       skip the per-test drafting and §5.3–§5.6 below
       proceed to step 6 (four-hat dispatch)

   elif strategy == "refactor-spike":
       populate §Failing-test seed using the refactor-spike variant
           (the variant whose marker reads <!-- variant: refactor-spike -->)
       skip the per-test drafting and §5.3–§5.6 below
       proceed to step 6 (four-hat dispatch)

   else:   # walking-skeleton | api-boundary | capability-cluster
       populate §Failing-test seed using the regular variant
           (the variant whose marker reads <!-- variant: regular -->)
       proceed with §5.3 below
   ```

   The variant selection consumes the three-variant rendering shape established by Child A's `spec.md.template` deliverable; each variant is a complete §Failing-test seed body preceded by an HTML comment marker per Child A's variant-encoding pattern. Step 5's job is to choose the marker, strip the other two variants and their markers, and populate the chosen variant's placeholders.

   ### 5.3 — Populate the Pyramid shape line

   After variant selection, populate the `**Pyramid shape:**` preamble line in the chosen variant verbatim from `PYRAMID_CATALOG[strategy]`:

   ```text
   **Pyramid shape:** _<strategy>_-shaped — required: `<required_tags joined by ", " in backticks>`. Optional: `<optional_tags joined by ", " in backticks; "(none)" if empty>`. Forbidden: `<forbidden_tags joined by ", " in backticks>`.
   ```

   For the regular variant only. The refactor-spike and hybrid variants carry their own preamble text per Child A's template; step 5 does not rewrite those lines.

   ### 5.4 — Draft one or more tests per AC

   For each AC in `## Acceptance criteria`, draft at least one test entry under the variant's **Tests.** subsection. Each entry has four fields per D3.2 §Manifest schema additions:

   - `name` — the proposed test function name, in the spec's surface language (e.g., `test_login_form_mounts`).
   - `tag` — exactly one value from `{unit, integration, contract, smoke, perceptual, invariance}`, in `[<tag>]` notation following the name.
   - `asserts` — a short clause naming what the test verifies (1 sentence).
   - `covers_ac` — a list of AC identifiers the test covers (e.g., `AC-1`, or `AC-1, AC-2` for tests that span multiple).

   Render shape per Child A's spec.md.template regular variant:

   ```markdown
   - `test_<name>` — `[<tag>]` — asserts <behavior>; covers AC-N.
   ```

   **Tag resolution rules.** Tag choice is judgement based on what the test asserts, anchored to D3.2 §Tag enum:

   - Test exercises one function, method, or class in isolation, externals mocked → `unit`.
   - Test exercises 2+ in-process components together, externals mocked → `integration`.
   - Test produces or verifies a contract artifact (Pact-shape file, OpenAPI fixture) at an API surface → `contract`.
   - Test asserts a wired system starts or completes without crashing, no behavioural assertions → `smoke`.
   - Test produces or asserts against a human-inspectable artifact (screenshot, PDF, transcript, generated document) → `perceptual`.
   - The pre-existing test pass-set predicate (refactor-spike only; satisfied by strategy declaration, not by a per-test entry) → `invariance`.

   When ambiguity arises ("is this test `unit` or `integration`?") the founder's framing in the AC text usually settles it — an AC that names "the controller and the service together" is integration; an AC that names a pure function is unit.

   ### 5.5 — `artifact_path` drafting for `[perceptual]` entries

   For each test entry whose `tag` is `perceptual`, populate an `artifact_path` field on the entry. The path is strategy-determined:

   ```text
   spec_slug ← parse from §title or §frontmatter (e.g., "0042-login-flow")

   if strategy == "walking-skeleton":
       artifact_path ← f"docs/specs/{spec_slug}/perceptual/{founder-chosen-filename}.png"
       artifact_type ← omitted   # implicit "image" per D3.3 §Manifest representation

   elif strategy == "api-boundary":
       artifact_path ← f"docs/specs/{spec_slug}/perceptual/integration-transcript.md"
       artifact_type ← omitted   # implicit "integration-transcript" per D3.3

   elif strategy == "capability-cluster":
       artifact_type ← <see §5.6>
       artifact_extension ← <resolved from artifact_type via capability-artifact-types.md>
       artifact_path ← f"docs/specs/{spec_slug}/perceptual/{founder-chosen-filename}.{artifact_extension}"
   ```

   The api-boundary path is the fixed canonical path per D3.3 §Api-boundary perceptual predicate — every api-boundary spec writes its integration transcript to exactly that filename. Walking-skeleton and capability-cluster permit founder-chosen filenames under the strategy-determined extension.

   **Founder-chosen filename selection.** Walking-skeleton and capability-cluster `[perceptual]` filenames are descriptive of what the artifact captures (`post-login.png`, `invoice-2026-001.pdf`, `recommended-feed.json`). Step 5 proposes a filename derived from the AC text and the founder confirms or revises inline. No halt fires on filename choice; the only constraint enforced at seal is the path-prefix (`docs/specs/<slug>/perceptual/`) and the extension (matched against the strategy convention).

   ### 5.6 — `artifact_type` resolution for capability-cluster `[perceptual]` entries

   For capability-cluster only. Read `docs/templates/capability-artifact-types.md` (the Child A deliverable; the seven-row canonical table). For each `[perceptual]` entry, propose an `artifact_type` based on the AC text and confirm with the founder:

   ```text
   candidate_types ← rows of capability-artifact-types.md
     # rendered-document, image, scheduled-event, share-post, email,
     # api-response, plain-text

   if AC text matches a candidate (e.g., "renders a PDF" → rendered-document):
       propose artifact_type ← <matched candidate>
       artifact_extension   ← extension from the table row
   else:
       surface founder prompt: "AC-K names a `[perceptual]` artifact at the
       capability boundary, but the artifact type isn't a clean match for the
       canonical table (rendered-document, image, scheduled-event, share-post,
       email, api-response, plain-text). Declare the artifact_type and
       extension. Examples: `usdz` for an AR asset, `wav` for a generated
       audio file, `epub` for a packaged ebook."
       capture founder's response:
           artifact_type      ← <lowercased-hyphenated string>
           artifact_extension ← <founder-declared extension; dot-prefixed>
           record this as a novel-type extension on the manifest
   ```

   Novel types pass through to the manifest as free-form lowercase-hyphenated strings paired with the founder-declared extension; the framework checks file existence and byte-stability at `/verify` time but does not validate format. Per-format validators are parked for v0.2.x per D3.3 §Open questions.

   ### 5.7 — In-skill critique pass (draft-time)

   After §5.3–§5.6, evaluate the draft against the catalog and surface in-skill critiques (not halts — collaborative inline suggestions). Per D3.2 §Step 3 procedure step 5:

   - **Required-missing.** A tag in `shape.required_tags` does not appear in any drafted entry. Surface: "AC coverage drafted, but the pyramid shape requires `<tag>` and no `<tag>`-tagged entry exists yet. Either retag an existing entry or add one."
   - **Forbidden-present.** A tag in `shape.forbidden_tags` appears in a drafted entry. Surface: "`test_X` is tagged `[<forbidden-tag>]` which is forbidden for `<strategy>`. Retag to one of `<optional_tags>` or move the test concern to a different spec under a different strategy."
   - **Out-of-enum.** A drafted entry's tag is not in `{unit, integration, contract, smoke, perceptual, invariance}`. Surface: "`test_X` is tagged `[<bad>]` which is not a valid tag. Retag to a value in `{unit, integration, contract, smoke, perceptual, invariance}`."
   - **AC-uncovered.** An AC has no drafted test entry. Surface: "AC-K has no entry in §Failing-test seed yet. Add at least one test that covers it."

   The founder may accept any critique as a revision or override it explicitly. Overridden critiques flow to step 11 (clarify-walker) — see §Step 5 ↔ Step 11 below. Unhandled critiques at seal time become step-13 gate failures.

   ### Step 5 ↔ Step 11 interaction (strategy-conflict surface)

   If the founder's overrides accumulate to where the drafted seed contradicts the declared strategy (per D3.2 §Step 3 procedure step 7 — e.g., a walking-skeleton spec whose entire seed is overridden to `[unit]`), step 11's clarify-walker emits a strategy-conflict clarify question: "the failing-test seed at draft is `<dominant-tag>`-dominated, but the strategy is `<strategy>` which requires `<required_tags>`; confirm `<strategy>` with seed rework, or revise to a strategy whose shape matches the seed." This is the load-bearing step-5-to-step-11 bridge for the strategy-annotation negotiation per D3.1 §Negotiation protocol — and (per D3.5 §G) one of the two surfaces clarify-walker still carries after grill-me subsumes the deep elicitation.

6. **Orchestrated four-hat dispatch** (per D3.5 §C). Four-hat now critiques the detailed, E0-confirmed spec — not a thin draft.

   `/specify` (the orchestrator) fires the four `four-hat-*` subagents (`engineer`, `pm`, `skeptic`, `user`) in parallel via the Task tool, then **confirms completion orchestrator-side**:

   - Wait for all four subagents to terminate, then read each subagent's `## Findings` transcript / manifest.
   - **Objection/finding completeness is verified here, by the orchestrator reading the transcripts** — *not* by a termination-blocking `SubagentStop` hook. Per SOL-132 part A (landed), `four-hat-objection-coverage.py` is advisory-only: it records a triage note on a malformed transcript and exits clean; it can never veto termination. Completeness enforcement that previously (incorrectly) lived in the hook now lives in this step.
   - If a hat's transcript is **unreadable or empty**, re-dispatch that single hat once (bounded retry: one re-dispatch). If it is still unreadable, surface that hat as **incomplete** at Gate 1 for a founder decision rather than hanging.

   Record `specify_phase: four-hat-dispatched` in run-state before dispatch so `--continue` knows hats are in flight (see §Resumability).

7. **HITL Gate 1 — pre-synthesis finding selection** (per D3.5 §D).

   Before any synthesis, show the founder a **per-subagent summary** — each hat's findings in `auditor-stance` form (one finding per `{type, locus}`, `rules/auditor-stance.md`). The founder **selects which findings to address vs. skip**. Skipped findings are recorded with the founder's skip rationale — never silently dropped. Synthesis (step 8) runs only over the founder-confirmed set.

   The **scope-reduction guard** still applies: any finding that proposes dropping an AC is surfaced explicitly and confirmed one-by-one — a "skip" at Gate 1 may not silently drop an AC. Mark the gate state `awaiting-gate-1` in run-state until the founder's selection is captured.

8. **Synthesis** (per D3.5 §E). The orchestrator (this skill) synthesizes the founder-confirmed finding set into the four-hat document `[<MARKER>-DOC-NNNN] four-hat: <MARKER>-N <title>` per `rules/naming.md` — append-only, so re-runs add new sections and prior sections are preserved. Synthesis is "synergy" across hats: deduplicate overlapping findings, order by locus, and attach each to the AC/section it touches. Only confirmed findings enter; skipped findings are listed in a **Skipped (founder-confirmed)** subsection with rationale.

9. **HITL Gate 2 — post-synthesis review** (per D3.5 §F).

   Show the founder the **final synthesized report** before it is resolved/sealed. Gate 2 loops back to step 8 (re-synthesize) or step 7 (re-select) on founder request; it proceeds to resolution (step 10) on founder approval. Like E0, Gate 2 is a conversational gate, not a manifest predicate. Mark `awaiting-gate-2` in run-state until approved.

10. **Resolve every objection.** For each finding in the confirmed, synthesized set from steps 7–9:
   - **Incorporate** — edit spec in place.
   - **Defer** — record in Open Questions with rationale.
   - **Reject** — record in spec margin with rationale.

   **Scope-reduction guard:** any "drop AC" suggestion surfaces to the founder explicitly (already filtered once at Gate 1). Founder confirms each drop. Never silent — silent acceptance creates spec drift.

11. **Clarify phase — residual-gap pass only** (per D3.5 §G). Grill-me (step 3) subsumes the *deep* elicitation clarify-walker used to carry; clarify-walker is **retained as a narrow residual-gap pass**, not removed. Invoke the clarify-walker agent, but its job narrows to two surfaces only:
   - gaps introduced *by* four-hat resolution (an Incorporate edit at step 10 that opens a new question), and
   - the strategy-conflict clarify question (the step-5↔step-11 bridge above, per D3.1 §Negotiation protocol).

   To avoid double-questioning, clarify-walker **skips any surface already resolved during step-3 elaboration**: it reads the spec's Clarifications section (which step 3 populates as surfaces are settled) and only raises surfaces not already covered. Present residual questions to the founder, record answers in the Clarifications section. Unanswerable items move to Open Questions with rationale.

12. **Slug derivation.** Propose 2–4 word kebab-case slug; founder confirms. Branch name follows `rules/naming.md`.

13. **Seal-time gate evaluation.**

   Step 13 is the manifest-writing seal. Before writing the manifest, evaluate the five `spec.*` gates per D3.4 §Per-stage gate inventory `/specify` row, in firing order. All gates evaluate before any halt card is composed (per D3.4 §`/specify` "all gates evaluate before halt card is composed; founder benefits from seeing every issue in one pass").

   **Naming reconciliation note.** D3.4 §Per-stage gate inventory names the five gates `spec.provenance`, `spec.ac-coverage`, `spec.pyramid-shape`, `spec.strategy-evidence`, `spec.strategy-annotation`. The parent `spec.md` AC-6 and `decomposition.md` Child 0001-B name them `spec.provenance`, `spec.failing-test-seed`, `spec.pyramid-shape`, `spec.perceptual-artifact-path`, `spec.strategy-annotation`. Same five gates, divergent names for two (`ac-coverage` ↔ `failing-test-seed`; `strategy-evidence` ↔ `perceptual-artifact-path`). The amendment below uses **D3.4's names** because D3.4 is the binding gate-definition spec; `spec.md` AC-6 and `decomposition.md` need a one-line follow-on amendment to match — see authoring notes §Surfaced item #1.

   ### 13.1 — Pre-flight: gate firing order

   ```text
   GATES_AT_SEAL = [
     "spec.provenance",         # pre-flight; chain integrity
     "spec.ac-coverage",        # AC coverage by failing-test seed
     "spec.pyramid-shape",      # D3.2 predicates 1-7
     "spec.strategy-evidence",  # D3.3 seal-time predicates
     "spec.strategy-annotation" # D3.1 step-1 annotation cleared
   ]

   for gate in GATES_AT_SEAL:
       evaluate gate predicates and record per-gate result
       # do NOT short-circuit; all gates evaluate

   if any gate has at least one failing predicate:
       compose aggregate halt card per D3.4 §Aggregation rules
       do NOT write the manifest
       exit with halt
   else:
       write manifest, including outputs.pyramid_shape and outputs.failing_test_seed[]
       seal /specify
   ```

   ### 13.2 — `spec.provenance` (pre-flight; chain integrity)

   Applies when step 13 runs under `--continue` or `--unseal`. For fresh `/specify` runs (first seal of a new spec), there is no upstream manifest to chain to and this gate is vacuously satisfied.

   ```text
   on --continue or --unseal:
       read cascade:run-state from .cascade/run-state.json
       expected_parent ← cascade:run-state.last_completed_stage.postcondition_manifest_path
       if expected_parent absent or path doesn't resolve to a file:
           FAIL spec.provenance with §provenance-chain-broken
           diagnostic: "expected parent manifest at <path>; absent"
       else:
           recompute manifest_sha256 of the parent manifest (with the field zeroed)
           if recomputed sha ≠ cascade:run-state.last_completed_stage.postcondition_manifest_sha256:
               FAIL spec.provenance with §provenance-chain-broken
               diagnostic: "parent manifest sha mismatch at <path>; expected <a>, got <b>"
           else:
               PASS
   ```

   Halt code: `§provenance-chain-broken`. Per Child A's halt-messages-append.md, this card is the consolidated chain-recovery halt; `--reconcile` is the standard recovery path. Diagnostic context lists the stage attempting to read, expected manifest path, found path, expected sha, found sha, expected parent name, found parent name.

   ### 13.3 — `spec.ac-coverage` (at-seal; AC coverage by failing-test seed)

   ```text
   acs ← parse §Acceptance criteria into a list of AC identifiers (AC-1, AC-2, ...)
   seed ← parse §Failing-test seed into a list of test entries
   covered ← union of entry.covers_ac for entry in seed

   for each ac in acs:
       if ac not in covered:
           FAIL spec.ac-coverage with §incomplete-failing-test-seed
           diagnostic: "AC-<N> has no named test in failing_test_seed[]."
   ```

   Halt code: `§incomplete-failing-test-seed` (existing in v0.1 halt-messages; carried forward). Recommendation: `/specify <MARKER>-N --continue`, add a named test covering the uncovered AC.

   For refactor-spike specs the seed is empty by design; `acs ⊆ {}` is vacuously satisfied — refactor-spike ACs are covered by the invariance predicate, not by per-AC entries. The gate's coverage check skips for refactor-spike. For hybrid parents the seed is also empty by design; the gate's coverage check skips for hybrid (per-child coverage is `/plan`'s child-inheritance gate, not `/specify`'s).

   ### 13.4 — `spec.pyramid-shape` (at-seal; D3.2 predicates 1–7)

   Evaluate the seven D3.2 predicates verbatim per D3.2 §Verifier predicates:

   ```text
   shape ← PYRAMID_CATALOG[strategy]   # may be null for hybrid

   # Predicate 1: pyramid_shape.strategy == outputs.decomposition_strategy
   if not hybrid and outputs.pyramid_shape.strategy != strategy:
       FAIL with §pyramid-shape-violation/strategy-mismatch
       diagnostic: "pyramid_shape.strategy = <a>, decomposition_strategy = <b>; mismatch"

   # Predicate 2: shape content matches catalog
   if not hybrid and (
       set(outputs.pyramid_shape.required_tags)  != set(shape.required_tags)  or
       set(outputs.pyramid_shape.optional_tags)  != set(shape.optional_tags)  or
       set(outputs.pyramid_shape.forbidden_tags) != set(shape.forbidden_tags)):
       FAIL with §pyramid-shape-violation/shape-tampering
       diagnostic: <expected vs actual tag sets verbatim>

   # Predicate 3: every required tag appears in seed (non-hybrid, non-refactor-spike)
   if strategy in {"walking-skeleton", "api-boundary", "capability-cluster"}:
       seed_tags ← {entry.tag for entry in failing_test_seed}
       missing ← set(shape.required_tags) - seed_tags
       if missing:
           FAIL with §pyramid-shape-violation/missing-required
           diagnostic: f"pyramid_shape requires {sorted(shape.required_tags)}; missing from seed: {sorted(missing)}"

   # Predicate 4: no forbidden tag appears (non-hybrid, non-refactor-spike)
   if strategy in {"walking-skeleton", "api-boundary", "capability-cluster"}:
       forbidden_present ← seed_tags & set(shape.forbidden_tags)
       if forbidden_present:
           FAIL with §pyramid-shape-violation/forbidden-present
           diagnostic: f"forbidden tags present in seed: {sorted(forbidden_present)}; pyramid_shape forbids {sorted(shape.forbidden_tags)} for {strategy}"

   # Predicate 5: every entry tag is in-enum
   ENUM = {"unit", "integration", "contract", "smoke", "perceptual", "invariance"}
   for entry in failing_test_seed:
       if entry.tag not in ENUM:
           FAIL with §pyramid-tag-invalid
           diagnostic: f"test '{entry.name}' has tag '[{entry.tag}]'; not in enum {sorted(ENUM)}"

   # Predicate 6: refactor-spike → empty seed
   if strategy == "refactor-spike" and len(failing_test_seed) > 0:
       FAIL with §pyramid-shape-violation/refactor-spike-nonempty
       diagnostic: "refactor-spike must have an empty failing-test seed; invariance is a /verify-time predicate, not an authored test"

   # Predicate 7: hybrid → null shape AND empty seed
   if strategy == "hybrid":
       if outputs.pyramid_shape is not None or len(failing_test_seed) > 0:
           FAIL with §pyramid-shape-violation/hybrid-nonempty
           diagnostic: "hybrid parent must defer pyramid shape and tests to children; pyramid_shape must be null and failing_test_seed[] must be empty at the parent grain"
   ```

   Halt codes: `§pyramid-shape-violation` (with sub-case in diagnostic per Child A's halt-messages-append.md) or `§pyramid-tag-invalid`.

   ### 13.5 — `spec.strategy-evidence` (at-seal; D3.3 seal-time predicates)

   Evaluate D3.3's seal-time predicates: `artifact_path` shape per strategy for `[perceptual]` entries; for refactor-spike, the invariance capture sequence.

   ```text
   # Part A: artifact_path for [perceptual] entries (walking-skeleton | api-boundary | capability-cluster)
   if strategy in {"walking-skeleton", "api-boundary", "capability-cluster"}:
       for entry in failing_test_seed where entry.tag == "perceptual":
           if entry.artifact_path is absent or not a string:
               FAIL with §pyramid-shape-violation/artifact-path-invalid
               diagnostic: f"[perceptual] entry '{entry.name}' missing artifact_path field"
               continue

           if not entry.artifact_path.startswith(f"docs/specs/{spec_slug}/perceptual/"):
               FAIL with §pyramid-shape-violation/artifact-path-invalid
               diagnostic: f"artifact_path '{entry.artifact_path}' must begin with 'docs/specs/{spec_slug}/perceptual/'"
               continue

           if strategy == "walking-skeleton":
               if not entry.artifact_path.endswith(".png"):
                   FAIL with §pyramid-shape-violation/artifact-path-invalid
                   diagnostic: f"walking-skeleton requires .png; got '{entry.artifact_path}'"

           elif strategy == "api-boundary":
               expected = f"docs/specs/{spec_slug}/perceptual/integration-transcript.md"
               if entry.artifact_path != expected:
                   FAIL with §pyramid-shape-violation/artifact-path-invalid
                   diagnostic: f"api-boundary requires exactly '{expected}'; got '{entry.artifact_path}'"

           elif strategy == "capability-cluster":
               # extension must match recorded artifact_type
               if entry.artifact_type is absent:
                   FAIL with §pyramid-shape-violation/artifact-path-invalid
                   diagnostic: f"capability-cluster [perceptual] entry '{entry.name}' missing artifact_type field"
                   continue

               artifact_types_table ← parse docs/templates/capability-artifact-types.md
               row ← lookup entry.artifact_type in artifact_types_table

               if row found:
                   expected_ext ← row.extension   # e.g., ".pdf", ".png", ".ics"
                   if not entry.artifact_path.endswith(expected_ext):
                       FAIL with §pyramid-shape-violation/artifact-path-invalid
                       diagnostic: f"artifact_type '{entry.artifact_type}' requires extension '{expected_ext}'; got '{entry.artifact_path}'"
               else:
                   # novel type — founder declared at step 5
                   # extension is free-form; framework records but doesn't validate
                   pass

   # Part B: refactor-spike invariance capture sequence
   if strategy == "refactor-spike":
       config ← read docs/.solo-config.json
       if config absent or not parseable:
           FAIL with §invariance-config-missing
           diagnostic: "docs/.solo-config.json absent or malformed; refactor-spike requires invariance.pass_set_capture_command"

       capture_command ← config.invariance.pass_set_capture_command
       if capture_command absent or empty string:
           FAIL with §invariance-config-missing
           diagnostic: "invariance.pass_set_capture_command absent or empty in docs/.solo-config.json"

       # Execute capture (this is the seal-time write side; /verify re-runs at verify-time)
       stdout, exit_code ← shell-execute capture_command from repo root
       if exit_code != 0:
           FAIL with §invariance-config-missing/capture-failed
           diagnostic: f"capture command '{capture_command}' exited with code {exit_code}; stderr: <captured>"

       pass_set ← stdout, filtered (blank lines and '#'-prefixed lines removed)
       if pass_set is empty:
           FAIL with §invariance-pass-set-empty
           diagnostic: f"capture command '{capture_command}' produced no pass-set output; refactor-spike requires a non-empty pre-existing pass-set at seal"

       # Write pass-set artifact
       write pass_set to f"docs/specs/{spec_slug}/invariance/pass-set-at-seal.txt"
       pass_set_sha256          ← sha256 of the written file's content
       capture_command_sha256   ← sha256 of capture_command string

       # Record on outputs for /verify to read
       outputs.invariance_artifact = {
           "pass_set_path":            f"docs/specs/{spec_slug}/invariance/pass-set-at-seal.txt",
           "pass_set_sha256":          pass_set_sha256,
           "capture_command":          capture_command,
           "capture_command_sha256":   capture_command_sha256,
           "captured_count":           len(pass_set)
       }
   ```

   Halt codes: `§pyramid-shape-violation/artifact-path-invalid`, `§invariance-config-missing`, `§invariance-pass-set-empty` (all in Child A's halt-messages-append.md).

   ### 13.6 — `spec.strategy-annotation` (at-seal; D3.1 step-1 annotation cleared)

   ```text
   section ← parse §Decomposition strategy from the spec markdown

   # Three failure modes per D3.1 §Halt conditions §strategy-missing diagnostic_context
   if section is absent:
       FAIL with §strategy-missing/missing
       diagnostic: "§Decomposition strategy section header absent"

   elif section body is empty or malformed:
       FAIL with §strategy-missing/malformed
       diagnostic: "§Decomposition strategy section present but body empty or unparseable"

   elif section value not in {"walking-skeleton", "api-boundary", "capability-cluster", "refactor-spike", "hybrid"}:
       FAIL with §strategy-missing/invalid-value
       diagnostic: f"§Decomposition strategy value '<value>' not in canonical enum; expected one of {walking-skeleton, api-boundary, capability-cluster, refactor-spike, hybrid}"

   # Annotation must be cleared (D3.4 §spec.strategy-annotation)
   elif "proposed by /specify" in section.text or "founder to confirm" in section.text:
       FAIL with §strategy-annotation-unresolved
       diagnostic: f"step-1 annotation comment block has not been removed; verbatim text detected: '<the annotation line>'"

   # Strategy-conflict resolution check (D3.1 §strategy-conflict-unresolved)
   elif clarify-walker at step 11 emitted a strategy-conflict question:
       resolution ← read §Open Questions for the conflict's resolution entry
       if resolution absent, empty, or marked pending:
           FAIL with §strategy-conflict-unresolved
           diagnostic: <clarify question text + conflicting four-hat finding + founder's proposed strategy at seal>
   ```

   Halt codes: `§strategy-missing` (with sub-case `missing` | `malformed` | `invalid-value` | `annotation-present` in diagnostic), `§strategy-annotation-unresolved`, `§strategy-conflict-unresolved` (all three in Child A's halt-messages-append.md halts 12–14).

   ### 13.7 — Manifest write (on all-gates-pass)

   If every gate at §13.2–§13.6 passes, write the manifest at `.cascade/manifests/<ticket>-specify.json` per D2.1 v2 §Caller-side verification step 6 and D3.2/D3.3's schema additions:

   ```json
   {
     "stage": "/specify",
     "ticket": "<MARKER>-<N>",
     "spec_sealed_at": "<ISO-8601 timestamp>",
     "outputs": {
       "spec_path": "docs/specs/<NNNN>-<slug>/spec.md",
       "ac_list_sha256": "<sha256>",
       "acceptance_criteria": [...],
       "decomposition_strategy": "<strategy>",
       "pyramid_shape": <object or null per strategy>,
       "failing_test_seed": [
         {
           "name": "...",
           "tag": "...",
           "asserts": "...",
           "covers_ac": ["AC-N"],
           "artifact_path": "...",       // only for [perceptual] entries
           "artifact_type": "..."        // only for capability-cluster [perceptual] entries
         },
         ...
       ],
       "invariance_artifact": <object or null per strategy>
     },
     "input_provenance": {...},
     "manifest_sha256": "<recomputed-zero-self-field>"
   }
   ```

   After write, update `cascade:run-state.json`'s `last_completed_stage` to point at this manifest path and sha per D2.1 v2 §Caller-side verification step 6.

   Also at seal (carried forward from v0.1):
   - Compute spec checksum: `sha256(docs/specs/NNNN-<slug>/spec.md)` truncated to 16 chars. Record in the four-hat doc's metadata header as `spec_sha256: <hash>` in the same write that appends the iteration's resolution summary. /build's drift guard reads this value.
   - Ticket title: `[<MARKER>] <verb-noun>`.
   - Parent ticket transition: set `scope:specified` per `rules/scope-labels.md` (atomic, in the same write as title + description + parentId).
   - Description: brief problem statement + AC checkboxes (mirrored verbatim from spec.md's Acceptance criteria section — text canonical, ticket is read-only mirror) + links to spec markdown + four-hat doc + declared branch name.

   The `scope:specified` label triggers the cascade engine. No further user action needed — /plan auto-fires through the cascade.

   ### Cross-references

   - **D3.1 §Negotiation protocol** — step-1 strategy annotation + founder confirm, step-4 progressive presentation (Gate E0), step-11 clarify-walker (residual-gap), step-13 seal flow.
   - **D3.1 §Halt conditions** — `§strategy-missing`, `§strategy-conflict-unresolved`, `§hybrid-without-child-overrides` (the third fires from `/plan`, not `/specify`).
   - **D3.2 §Step 3 procedure** — the eight-step authoring flow that §5.1–§5.7 above implements.
   - **D3.2 §Manifest schema additions** — the `pyramid_shape` object and per-entry `tag` field on `failing_test_seed[]`.
   - **D3.2 §Verifier predicates** — predicates 1–7 evaluated by `spec.pyramid-shape` gate at §13.4.
   - **D3.2 §Halt conditions** — `§pyramid-shape-violation`, `§pyramid-tag-invalid`.
   - **D3.3 §Walking-skeleton / Api-boundary / Capability-cluster perceptual predicate** — `artifact_path` conventions per strategy, consumed at §5.5–§5.6.
   - **D3.3 §Refactor-spike invariance predicate** — the capture command + pass-set sequence, consumed at §13.5 Part B.
   - **D3.3 §Manifest representation** — the `artifact_path`, `artifact_type`, `invariance_artifact` fields.
   - **D3.3 §Halt conditions** — `§perceptual-evidence-missing` (fires at `/verify`, not `/specify`), `§invariance-config-missing`, `§invariance-pass-set-empty`, `§invariance-pass-set-regression` (fires at `/verify`), `§invariance-seal-tampering` (fires at `/verify`), `§invariance-config-changed` (fires at `/verify`).
   - **D3.4 §Per-stage gate inventory `/specify`** — the five gates' firing order and predicate references.
   - **D3.4 §Aggregation rules** — all-gates-evaluate + single-card-aggregate semantics for the seal halt.
   - **D3.4 §Halt conditions** — `§strategy-annotation-unresolved`, `§provenance-chain-broken`.
   - **Child A `spec.md.template`** — the three-variant `## Failing-test seed` rendering shape consumed at §5.2.
   - **Child A `halt-messages-append.md`** — fourteen new halts authored verbatim; this skill references by halt-code, not by reproducing card text.
   - **Child A `capability-artifact-types.md`** — the seven-row canonical type-extension table consumed at §5.6.
   - **Child A `solo-config.example.json`** — per-runner `invariance.pass_set_capture_command` examples; the framework reads `docs/.solo-config.json` at §13.5 Part B, the example file is for founder cargo-culting only.
   - **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-6** — this skill amendment satisfies AC-6 as authored, modulo the gate-name reconciliation surfaced as Item #1 in the authoring notes.

All writes follow `rules/write-discipline.md`. Status semantics per `rules/completion-status.md`.

## Resumability

The elaboration loop (step 3) and the three conversational gates (E0, Gate 1, Gate 2) can span multiple turns, so `/specify <MARKER>-N --continue` must resume **mid-loop**, not restart. State persists in two places already owned by the cascade — no new persistence mechanism is invented (per D3.5 §Resumability):

- **Spec body.** Step 3 edits `spec.md` in place after each answer, so the partial spec **is** the resumable state for elaboration. The four-hat document's append-only structure preserves prior four-hat iterations the same way.
- **Run-state phase marker.** `/specify` records its current mid-loop phase in `.cascade/run-state.json` under a `specify_phase` field, mirroring the `discovery: state` `research_depth` resume pattern (SOL-131) rather than inventing a new mechanism. The field is `null` outside an active loop and otherwise one of:

  | `specify_phase` | Resume re-enters at |
  |---|---|
  | `elaborating` | step 3 (continue the grill-me interview from the spec's live state) |
  | `awaiting-E0` | step 4 (re-present the remaining chunks for confirmation) |
  | `four-hat-dispatched` | step 6 (read the hat transcripts; re-dispatch any unreadable hat once) |
  | `awaiting-gate-1` | step 7 (re-show the per-subagent summary for selection) |
  | `awaiting-gate-2` | step 9 (re-show the synthesized report for approval) |
  | `resolving` | step 10 (resume objection resolution over the confirmed set) |
  | `residual-clarify` | step 11 (residual-gap clarify pass) |

  `/specify` writes the marker at each phase boundary (same-turn with the `spec.md` edit per `rules/write-discipline.md`) and clears it to `null` on seal (step 13) or on the manual-halt branch. A `--continue` invocation reads `specify_phase` first, then re-enters at the indicated step. The field also rides the per-session PreCompact snapshot so a compaction mid-loop resumes at the same phase. Because E0 / Gate 1 / Gate 2 are conversational gates with no manifest predicate, the marker is the only record that they are pending — it is load-bearing for resume, not decorative.

## Unseal-and-respec mode

`/specify <MARKER>-N --unseal`:

1. Archive current `docs/specs/NNNN-<slug>/spec.md` → `docs/specs/NNNN-<slug>/archive/spec-v<N>.md`.
2. Post previous spec content as a comment on the four-hat document (preserves history outside markdown).
3. Re-run the full flow from step 1.
4. Four-hat document is the same one (append-only). Re-computed `spec_sha256` lands in the new iteration's metadata header; prior checksums stay in prior sections.
5. Cascade re-fires on completion.

Use when fundamental rework is needed — adding /plan guidance won't get there.

## Outputs

| Artifact | Location |
|---|---|
| Spec markdown | `docs/specs/NNNN-<slug>/spec.md` |
| Four-hat review document | `[<MARKER>-DOC-NNNN] four-hat: <MARKER>-N <title>` (metadata includes `spec_sha256`) |
| Parent ticket | `[<MARKER>] <verb-noun>`, label `scope:specified` |
| Branch name (declared) | `<MARKER>-N-<slug>` |

## /Chains

**Pattern:** F (fan-out-internal)
**Group:** D
**Within-group transitions:** step 1 (strategy proposal — `spec.strategy-annotation` gate per D3.4 fires here; founder explicitly accepts or revises) → step 2 (v1 draft — the end state) → step 3 (grill-me elaboration — relentless interview to buildable detail, `spec.md` edited in place) → step 4 (progressive presentation + **Gate E0** founder confirmation; four-hat does not run until E0 passes) → step 5 (failing-test seed authoring against the elaborated ACs) → four-hat fan-out (parallel four subagents: `user`, `engineer`, `pm`, `skeptic` per `.claude/agents/four-hat-{user,engineer,pm,skeptic}.md`) → **orchestrator-side completion confirmation** (the parent waits for all four to terminate and reads each transcript; completeness is verified here, not by a termination-blocking `SubagentStop` hook — `four-hat-objection-coverage.py` is advisory-only per SOL-132 part A; an unreadable hat is re-dispatched once, bounded) → **Gate 1** (per-subagent finding selection — founder picks address/skip; scope-reduction guard applies) → synthesis (confirmed set → append-only four-hat doc) → **Gate 2** (founder reviews the synthesized report; may loop back to re-select or re-synthesize) → resolve objections → step 11 (residual-gap clarify — skips surfaces already settled in step-3 elaboration) → seal. Each subagent's SubagentStop is an advisory PreCompact safe boundary (per D2.3 v1.3 §Within-group safe boundaries Group D row — four discrete safe boundaries, one per hat; advisory only — it never gates completion). Continuation between steps is project-instruction-driven (chat-Claude); the four-hat fan-out is dispatched via parallel Task-invokes to the named subagents. The conversational gates (E0, Gate 1, Gate 2) and the elaboration loop persist their phase in the `specify_phase` run-state marker so `--continue` resumes mid-loop (see §Resumability).
**Group exit trigger:** spec seal — all four hat manifests at `.cascade/manifests/<ticket>-{user,engineer,pm,skeptic}.json` exist and pass structural verification; the merged outputs are written into `/specify`'s parent manifest at `.cascade/manifests/<ticket>-specify.json`; and the five `spec.*` gates (`spec.strategy-annotation`, `spec.pyramid-shape`, `spec.ac-coverage`, `spec.strategy-evidence`, `spec.provenance`) per D3.4 §spec gates evaluate and pass. SOL-62's `spec.md` inline render fires immediately before the chat-end card (`docs/specs/<ticket>/spec.md` is rendered inline in chat).
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant `normal`. After render, set `cascade:run-state.last_completed_group = "D"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<ticket>-specify.json"`, flush, write `.cascade/handoff/last.md`. Do not Task-invoke anything.

**Manual-halt branch:** if `/cascade-halt` fires mid-fan-out, follow D2.3 v1.3 §Manual halt protocol Group D subsection: wait for outstanding subagents to complete naturally, write each completed hat's manifest per D2.1 v2.1, then render the chat-end card with the manual-halt variant (the second `<optional>` block of the template). No spec seal occurs in this branch — the `/specify` manifest is *not* written, and `cascade:run-state.last_completed_group` does *not* advance to D. Instead, `cascade:run-state.partial_group_state.D.hat_manifests_sealed[]` records which hats sealed before halt. The handoff prompt's `Group entry:` value remains D so resumption restarts Group D from a fresh chat (the prior hat manifests remain on disk as historical evidence; the new run produces a fresh set).

**Next group entry:** E (`/plan` → `/review` → `/update-linear` auto-fire chain) on normal exit; D (re-entry) on manual-halt exit.
**Auto-fire compact handling:** not applicable. Group D runs in chat-Claude; no live PreCompact hook. The per-subagent safe boundaries in §Within-group safe boundaries Group D row are advisory in v0.2 (PreCompact deferral semantics fire only in Group F).
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<ticket>-specify.json` — containing the merged four-hat outputs in its `outputs` field. The four `<ticket>-<hat>.json` subagent manifests are *inputs* to `/specify`'s seal, not the exit manifest. D4.6 v1.1's re-derivation reads `<ticket>-specify.json` to populate the chat-end card's "What was produced" section; the subagent manifests are not consulted by D4.6.

## Notes

**Research-finding drill-down.** If the founder asks "tell me more about finding X" during or after /specify, read `docs/research/NNNN-<slug>.md` (the deep report linked from the relevant Phase 2 summary) and surface the section. The Related Research Findings section in the spec is intentionally terse — verbatim bullets only — so chat-based drill-down is the discovery path.

**spec.md is the sole canonical source of AC text.** The ticket's AC checkboxes are a read-only mirror written by /update-linear (or /specify at seal) and flipped (state only) by /build on completion. **Do not edit AC text directly on the Linear ticket** — edits get overwritten on the next /update-linear pass. To change an AC, edit `spec.md` and re-run `/specify --continue`. /build's preconditions include a `ticket_ac_text == spec_ac_text` check that halts on drift (`§ticket-ac-drift`).

**Failing-test seed is the contract /plan reads from.** Incomplete seeds halt the cascade at /plan — an incomplete failing-test seed is a /specify defect, never iterated on inside /plan. Author seeds carefully.
