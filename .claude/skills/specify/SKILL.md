---
name: specify
description: Author a heavyweight spec for a parent feature. Produces a sealed parent ticket (label scope:specified), spec markdown at docs/specs/NNNN-<slug>/spec.md, and an append-only four-hat Linear document. On seal, the cascade auto-fires through /plan → /review → /update-linear; user sees a single summary or halt-card at the end. Next user-invoked step is /build <MARKER>-N-K per child ticket. Fires on "/specify <topic>", "specify <topic>", "spec out <topic>", "write a spec for <topic>". Modes: `--continue` resumes in-progress, `--unseal` archives and rebuilds.
---

# specify

Author parent spec. User-facing entry point of the cascade. On seal, the cascade auto-fires through /plan → /review → /update-linear; the founder sees a single summary or halt-card at cascade end. Next user-invoked step is `/build <MARKER>-N-K` per child ticket.

## Trigger

- User: "/specify <topic>", "specify <topic>", "spec out <topic>", "write a spec for <topic>"
- Resume: "/specify <MARKER>-N --continue" — resumes an in-progress spec
- Unseal: "/specify <MARKER>-N --unseal" — archives the current spec and rebuilds (full re-run)

## Behavior

0. **Preconditions** (any failure halts with `NEEDS_CONTEXT` per `completion-status.md`; halt-card per `docs/templates/halt-messages.md`).
   - `docs/constitution.md` exists. Missing → `NEEDS_CONTEXT` per `§missing-context`: "no constitution; run `/discovery` (approve exit Task-invokes `/constitution`) or `/constitution reseed` if a north-star already exists." /review check j and downstream cascade stages assume a constitution; /specify halts here rather than letting the cascade fail three stages deep.
   - `docs/product/north-star.md` exists. Missing → `NEEDS_CONTEXT`: "no north-star; run `/discovery`."
   - Marker resolvable from `docs/.solo-config.json`. Unset → `NEEDS_CONTEXT`.

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

2. **Draft full spec** at `docs/specs/NNNN-<slug>/spec.md` per path conventions in `rules/naming.md`. Use `docs/templates/spec.md.template`. Six sections: Problem statement, Design & UX (or API contract for backend-only), Scope boundary (in/out both explicit), Acceptance criteria (behavior-oriented testable checkboxes), Failing-test seed (Code-Claude scaffolds these as the first commit), Related research findings (verbatim bullets linked to `[<MARKER>-RES-NNN]` summary + deep report).

3. **Failing-test seed authoring.**

   Step 3 receives a draft spec with `## Decomposition strategy` confirmed at step 1, `## Acceptance criteria` drafted at step 2, and proceeds to populate `## Failing-test seed`. Three machinery additions over v0.1: a cached D3.2 catalog, per-test `[tag]` resolution rules, and per-strategy `artifact_path` / `artifact_type` drafting.

   ### 3.1 — Catalog cache (const block)

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

   ### 3.2 — Strategy-class dispatch

   Step 3 branches on the value of `## Decomposition strategy`:

   ```text
   strategy ← read §Decomposition strategy from the draft spec
   shape    ← PYRAMID_CATALOG[strategy]

   if strategy == "hybrid":
       populate §Failing-test seed using the hybrid variant of spec.md.template
           (the variant whose HTML comment marker reads <!-- variant: hybrid -->)
       skip the per-test drafting and §3.3–§3.6 below
       proceed to step 4 (clarify-walker)

   elif strategy == "refactor-spike":
       populate §Failing-test seed using the refactor-spike variant
           (the variant whose marker reads <!-- variant: refactor-spike -->)
       skip the per-test drafting and §3.3–§3.6 below
       proceed to step 4 (clarify-walker)

   else:   # walking-skeleton | api-boundary | capability-cluster
       populate §Failing-test seed using the regular variant
           (the variant whose marker reads <!-- variant: regular -->)
       proceed with §3.3 below
   ```

   The variant selection consumes the three-variant rendering shape established by Child A's `spec.md.template` deliverable; each variant is a complete §Failing-test seed body preceded by an HTML comment marker per Child A's variant-encoding pattern. Step 3's job is to choose the marker, strip the other two variants and their markers, and populate the chosen variant's placeholders.

   ### 3.3 — Populate the Pyramid shape line

   After variant selection, populate the `**Pyramid shape:**` preamble line in the chosen variant verbatim from `PYRAMID_CATALOG[strategy]`:

   ```text
   **Pyramid shape:** _<strategy>_-shaped — required: `<required_tags joined by ", " in backticks>`. Optional: `<optional_tags joined by ", " in backticks; "(none)" if empty>`. Forbidden: `<forbidden_tags joined by ", " in backticks>`.
   ```

   For the regular variant only. The refactor-spike and hybrid variants carry their own preamble text per Child A's template; step 3 does not rewrite those lines.

   ### 3.4 — Draft one or more tests per AC

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

   ### 3.5 — `artifact_path` drafting for `[perceptual]` entries

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
       artifact_type ← <see §3.6>
       artifact_extension ← <resolved from artifact_type via capability-artifact-types.md>
       artifact_path ← f"docs/specs/{spec_slug}/perceptual/{founder-chosen-filename}.{artifact_extension}"
   ```

   The api-boundary path is the fixed canonical path per D3.3 §Api-boundary perceptual predicate — every api-boundary spec writes its integration transcript to exactly that filename. Walking-skeleton and capability-cluster permit founder-chosen filenames under the strategy-determined extension.

   **Founder-chosen filename selection.** Walking-skeleton and capability-cluster `[perceptual]` filenames are descriptive of what the artifact captures (`post-login.png`, `invoice-2026-001.pdf`, `recommended-feed.json`). Step 3 proposes a filename derived from the AC text and the founder confirms or revises at step 5. No halt fires on filename choice; the only constraint enforced at seal is the path-prefix (`docs/specs/<slug>/perceptual/`) and the extension (matched against the strategy convention).

   ### 3.6 — `artifact_type` resolution for capability-cluster `[perceptual]` entries

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

   ### 3.7 — In-skill critique pass (draft-time)

   After §3.3–§3.6, evaluate the draft against the catalog and surface in-skill critiques (not halts — collaborative inline suggestions). Per D3.2 §Step 3 procedure step 5:

   - **Required-missing.** A tag in `shape.required_tags` does not appear in any drafted entry. Surface: "AC coverage drafted, but the pyramid shape requires `<tag>` and no `<tag>`-tagged entry exists yet. Either retag an existing entry or add one."
   - **Forbidden-present.** A tag in `shape.forbidden_tags` appears in a drafted entry. Surface: "`test_X` is tagged `[<forbidden-tag>]` which is forbidden for `<strategy>`. Retag to one of `<optional_tags>` or move the test concern to a different spec under a different strategy."
   - **Out-of-enum.** A drafted entry's tag is not in `{unit, integration, contract, smoke, perceptual, invariance}`. Surface: "`test_X` is tagged `[<bad>]` which is not a valid tag. Retag to a value in `{unit, integration, contract, smoke, perceptual, invariance}`."
   - **AC-uncovered.** An AC has no drafted test entry. Surface: "AC-K has no entry in §Failing-test seed yet. Add at least one test that covers it."

   The founder may accept any critique as a revision or override it explicitly. Overridden critiques flow to step 4 (clarify-walker) — see §Step 3 ↔ Step 4 below. Unhandled critiques at seal time become step-7 gate failures.

   ### Step 3 ↔ Step 4 interaction (strategy-conflict surface)

   If the founder's overrides accumulate to where the drafted seed contradicts the declared strategy (per D3.2 §Step 3 procedure step 7 — e.g., a walking-skeleton spec whose entire seed is overridden to `[unit]`), step 4's clarify-walker emits a strategy-conflict clarify question: "the failing-test seed at draft is `<dominant-tag>`-dominated, but the strategy is `<strategy>` which requires `<required_tags>`; confirm `<strategy>` with seed rework, or revise to a strategy whose shape matches the seed." This is the load-bearing step-3-to-step-4 bridge for the strategy-annotation negotiation per D3.1 §Negotiation protocol.

4. **Four-hat critique.** Invoke four-hat-engineer, four-hat-pm, four-hat-skeptic, four-hat-user agents in parallel via the Task tool. Aggregate findings into a Linear document `[<MARKER>-DOC-NNNN] four-hat: <MARKER>-N <title>` per `rules/naming.md`. The document is append-only — re-runs add new sections, prior sections preserved. Review history is permanent.

5. **Resolve every objection.** For each finding from the four-hat doc:
   - **Incorporate** — edit spec in place.
   - **Defer** — record in Open Questions with rationale.
   - **Reject** — record in spec margin with rationale.

   **Scope-reduction guard:** any "drop AC" suggestion surfaces to the founder explicitly. Founder confirms each drop. Never silent — silent acceptance creates spec drift.

6. **Clarify phase.** Invoke clarify-walker agent. The agent returns applicable clarification surfaces with per-surface questions. Present to founder, record answers in a Clarifications section appended to `docs/specs/NNNN-<slug>/spec.md`. Unanswerable items move to Open Questions with rationale.

7. **Slug derivation.** Propose 2–4 word kebab-case slug; founder confirms. Branch name follows `rules/naming.md`.

8. **Seal-time gate evaluation.**

   Step 8 is the manifest-writing seal. Before writing the manifest, evaluate the five `spec.*` gates per D3.4 §Per-stage gate inventory `/specify` row, in firing order. All gates evaluate before any halt card is composed (per D3.4 §`/specify` "all gates evaluate before halt card is composed; founder benefits from seeing every issue in one pass").

   **Naming reconciliation note.** D3.4 §Per-stage gate inventory names the five gates `spec.provenance`, `spec.ac-coverage`, `spec.pyramid-shape`, `spec.strategy-evidence`, `spec.strategy-annotation`. The parent `spec.md` AC-6 and `decomposition.md` Child 0001-B name them `spec.provenance`, `spec.failing-test-seed`, `spec.pyramid-shape`, `spec.perceptual-artifact-path`, `spec.strategy-annotation`. Same five gates, divergent names for two (`ac-coverage` ↔ `failing-test-seed`; `strategy-evidence` ↔ `perceptual-artifact-path`). The amendment below uses **D3.4's names** because D3.4 is the binding gate-definition spec; `spec.md` AC-6 and `decomposition.md` need a one-line follow-on amendment to match — see authoring notes §Surfaced item #1.

   ### 8.1 — Pre-flight: gate firing order

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

   ### 8.2 — `spec.provenance` (pre-flight; chain integrity)

   Applies when step 8 runs under `--continue` or `--unseal`. For fresh `/specify` runs (first seal of a new spec), there is no upstream manifest to chain to and this gate is vacuously satisfied.

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

   ### 8.3 — `spec.ac-coverage` (at-seal; AC coverage by failing-test seed)

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

   ### 8.4 — `spec.pyramid-shape` (at-seal; D3.2 predicates 1–7)

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

   ### 8.5 — `spec.strategy-evidence` (at-seal; D3.3 seal-time predicates)

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
                   # novel type — founder declared at step 3
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

   ### 8.6 — `spec.strategy-annotation` (at-seal; D3.1 step-1 annotation cleared)

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
   elif clarify-walker at step 4 emitted a strategy-conflict question:
       resolution ← read §Open Questions for the conflict's resolution entry
       if resolution absent, empty, or marked pending:
           FAIL with §strategy-conflict-unresolved
           diagnostic: <clarify question text + conflicting four-hat finding + founder's proposed strategy at seal>
   ```

   Halt codes: `§strategy-missing` (with sub-case `missing` | `malformed` | `invalid-value` | `annotation-present` in diagnostic), `§strategy-annotation-unresolved`, `§strategy-conflict-unresolved` (all three in Child A's halt-messages-append.md halts 12–14).

   ### 8.7 — Manifest write (on all-gates-pass)

   If every gate at §8.2–§8.6 passes, write the manifest at `.cascade/manifests/<ticket>-specify.json` per D2.1 v2 §Caller-side verification step 6 and D3.2/D3.3's schema additions:

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

   - **D3.1 §Negotiation protocol** — step-1 annotation, step-4 clarify-walker, step-5 founder confirm, step-7 seal flow.
   - **D3.1 §Halt conditions** — `§strategy-missing`, `§strategy-conflict-unresolved`, `§hybrid-without-child-overrides` (the third fires from `/plan`, not `/specify`).
   - **D3.2 §Step 3 procedure** — the eight-step authoring flow that §3.1–§3.7 above implements.
   - **D3.2 §Manifest schema additions** — the `pyramid_shape` object and per-entry `tag` field on `failing_test_seed[]`.
   - **D3.2 §Verifier predicates** — predicates 1–7 evaluated by `spec.pyramid-shape` gate at §8.4.
   - **D3.2 §Halt conditions** — `§pyramid-shape-violation`, `§pyramid-tag-invalid`.
   - **D3.3 §Walking-skeleton / Api-boundary / Capability-cluster perceptual predicate** — `artifact_path` conventions per strategy, consumed at §3.5–§3.6.
   - **D3.3 §Refactor-spike invariance predicate** — the capture command + pass-set sequence, consumed at §8.5 Part B.
   - **D3.3 §Manifest representation** — the `artifact_path`, `artifact_type`, `invariance_artifact` fields.
   - **D3.3 §Halt conditions** — `§perceptual-evidence-missing` (fires at `/verify`, not `/specify`), `§invariance-config-missing`, `§invariance-pass-set-empty`, `§invariance-pass-set-regression` (fires at `/verify`), `§invariance-seal-tampering` (fires at `/verify`), `§invariance-config-changed` (fires at `/verify`).
   - **D3.4 §Per-stage gate inventory `/specify`** — the five gates' firing order and predicate references.
   - **D3.4 §Aggregation rules** — all-gates-evaluate + single-card-aggregate semantics for the seal halt.
   - **D3.4 §Halt conditions** — `§strategy-annotation-unresolved`, `§provenance-chain-broken`.
   - **Child A `spec.md.template`** — the three-variant `## Failing-test seed` rendering shape consumed at §3.2.
   - **Child A `halt-messages-append.md`** — fourteen new halts authored verbatim; this skill references by halt-code, not by reproducing card text.
   - **Child A `capability-artifact-types.md`** — the seven-row canonical type-extension table consumed at §3.6.
   - **Child A `solo-config.example.json`** — per-runner `invariance.pass_set_capture_command` examples; the framework reads `docs/.solo-config.json` at §8.5 Part B, the example file is for founder cargo-culting only.
   - **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-6** — this skill amendment satisfies AC-6 as authored, modulo the gate-name reconciliation surfaced as Item #1 in the authoring notes.

All writes follow `rules/write-discipline.md`. Status semantics per `rules/completion-status.md`.

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
**Within-group transitions:** step 1 (strategy proposal — `spec.strategy-annotation` gate per D3.4 fires here; founder explicitly accepts or revises) → step 2 (AC drafting per `/specify` step 2) → four-hat fan-out (parallel four subagents: `user`, `engineer`, `pm`, `skeptic` per `.claude/agents/four-hat-panel/`) → merge (parent reads each subagent transcript and writes the subagent's manifest per D2.1 v2.1 §Caller-side verification) → seal. Each subagent's SubagentStop is an advisory PreCompact safe boundary (per D2.3 v1.3 §Within-group safe boundaries Group D row — four discrete safe boundaries, one per hat). Continuation between steps is project-instruction-driven (chat-Claude); the four-hat fan-out is dispatched via parallel Task-invokes to the named subagents.
**Group exit trigger:** spec seal — all four hat manifests at `.cascade/manifests/<ticket>-{user,engineer,pm,skeptic}.json` exist and pass structural verification; the merged outputs are written into `/specify`'s parent manifest at `.cascade/manifests/<ticket>-specify.json`; and the five `spec.*` gates (`spec.strategy-annotation`, `spec.pyramid-shape`, `spec.failing-test-seed`, `spec.perceptual-artifact-path`, `spec.provenance`) per D3.4 §spec gates evaluate and pass. SOL-62's `spec.md` inline render fires immediately before the chat-end card (`docs/specs/<ticket>/spec.md` is rendered inline in chat).
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant `normal`. After render, set `cascade:run-state.last_completed_group = "D"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<ticket>-specify.json"`, flush, write `.cascade/handoff/last.md`. Do not Task-invoke anything.

**Manual-halt branch:** if `/cascade-halt` fires mid-fan-out, follow D2.3 v1.3 §Manual halt protocol Group D subsection: wait for outstanding subagents to complete naturally, write each completed hat's manifest per D2.1 v2.1, then render the chat-end card with the manual-halt variant (the second `<optional>` block of the template). No spec seal occurs in this branch — the `/specify` manifest is *not* written, and `cascade:run-state.last_completed_group` does *not* advance to D. Instead, `cascade:run-state.partial_group_state.D.hat_manifests_sealed[]` records which hats sealed before halt. The handoff prompt's `Group entry:` value remains D so resumption restarts Group D from a fresh chat (the prior hat manifests remain on disk as historical evidence; the new run produces a fresh set).

**Next group entry:** E (`/plan` → `/review` → `/update-linear` auto-fire chain) on normal exit; D (re-entry) on manual-halt exit.
**Auto-fire compact handling:** not applicable. Group D runs in chat-Claude; no live PreCompact hook. The per-subagent safe boundaries in §Within-group safe boundaries Group D row are advisory in v0.2 (PreCompact deferral semantics fire only in Group F).
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<ticket>-specify.json` — containing the merged four-hat outputs in its `outputs` field. The four `<ticket>-<hat>.json` subagent manifests are *inputs* to `/specify`'s seal, not the exit manifest. D4.6 v1.1's re-derivation reads `<ticket>-specify.json` to populate the chat-end card's "What was produced" section; the subagent manifests are not consulted by D4.6.

## Notes

**Research-finding drill-down.** If the founder asks "tell me more about finding X" during or after /specify, read `docs/research/NNNN-<slug>.md` (the deep report linked from the relevant Phase 2 summary) and surface the section. The Related Research Findings section in the spec is intentionally terse — verbatim bullets only — so chat-based drill-down is the discovery path.

**spec.md is the sole canonical source of AC text.** The ticket's AC checkboxes are a read-only mirror written by /update-linear (or /specify at seal) and flipped (state only) by /build on completion. **Do not edit AC text directly on the Linear ticket** — edits get overwritten on the next /update-linear pass. To change an AC, edit `spec.md` and re-run `/specify --continue`. /build's preconditions include a `ticket_ac_text == spec_ac_text` check that halts on drift (`§ticket-ac-drift`).

**Failing-test seed is the contract /plan reads from.** Incomplete seeds halt the cascade at /plan — an incomplete failing-test seed is a /specify defect, never iterated on inside /plan. Author seeds carefully.
