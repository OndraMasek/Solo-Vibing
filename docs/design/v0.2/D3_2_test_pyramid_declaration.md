# D3.2 — Test-pyramid declaration per spec

**Status:** Design.
**Phase:** 3.
**Resolves:** F-3 (quality topology inversion), in conjunction with D3.1 + D3.3 + D3.4.
**Companion:** D3.1 (decomposition strategy catalog) — populator for D3.2's per-strategy pyramid shape; D3.3 (perceptual-AC integration coverage rule) — owns the meaning of `perceptual` evidence per strategy and the meaning of `invariance` evidence for refactor-spike; D3.4 (gate definitions) — composes pyramid_shape + failing_test_seed tags into per-stage gate-firing predicates against D2.1 v2's verifier framework.

**Anchors** (per D3.0): Cohn (pyramid), Dodds (trophy), Schaffer / Spotify (honeycomb — including the Integration vs Integrated distinction), Fowler (narrow-scoped integration tests), Rainsberger (the conceptual source for Spotify's distinction). The "Boz-Bryden" reference in the prior session's carry-forward note was not recoverable in 2026 web search and is treated as a session-note artifact; this is not load-bearing for D3.2.

## Problem

D3.1 named the five strategies but left the per-strategy test mix as directional language in the catalog ("heavy at smoke + perceptual", "Contract tests dominate", "Pre-existing tests are the pyramid", etc.). Without a concrete tag enum, an enforceable per-strategy pyramid declaration, and a `/specify`-side populator, three failure modes remain open:

1. **The Bomber failure mode is partially open.** D2.1 v2 catches a stage claiming completion against an artifact that doesn't exist. D3.1 makes decomposition intent first-class. But nothing yet prevents `/specify` from sealing a walking-skeleton spec whose entire failing-test seed is `[unit]` tests — which would deliver subsystem-correctness gates with no smoke or perceptual anchor, the exact failure F-3 names.
2. **The 2026 cost-curve shift has no representation in the spec.** Per D3.0, the discourse has moved from "unit tests are the default base, write more of them" to "write the test at the layer the strategy's primary risk lives at." If the spec doesn't declare which layer the risk lives at, /build's Ralph loop has no signal beyond test-pass/fail, and LLM-generated test churn at the wrong layer (the Bray / Folding-Sky failure mode) goes uncaught.
3. **The failing-test seed contract is under-typed.** /plan reads the seed as the contract; /build runs it every iteration; /wrap blocks on red. None of these consumers can today distinguish a unit test that mirrors implementation from an integration test that asserts boundary behavior. Drift detection (D2.1 v2's first-FAIL hash) catches stable failures but doesn't catch a seed composed entirely of theatrical assertions.

D3.2 closes these by giving the failing-test seed an explicit per-test layer tag and giving the spec an explicit per-strategy pyramid shape declaration. Both are sealed at /specify step 7, checked by verifier predicates at every downstream stage, and visible to the four-hats during review.

## Decision

The failing-test seed gains:

- **A per-test `tag`** drawn from a canonical six-value enum: `unit | integration | contract | smoke | perceptual | invariance`. Every seed entry carries exactly one tag.
- **A per-spec `pyramid_shape`** sealed at step 7, naming three sets: `required_tags`, `optional_tags`, `forbidden_tags`. The shape is populated by /specify step 3 from D3.1's strategy → shape mapping (catalog below). The shape is part of the spec's contract; it does not re-derive at downstream stages.

The pyramid declaration lives as a preamble line inside `## Failing-test seed`, not as a new top-level spec section. Rationale: the seed is the pyramid's instantiation; placing the shape contract where its instances live keeps both readable in one place and prevents the "declared one shape, populated another" failure mode that two-section separation would invite.

The verifier predicate is set-membership, not distribution: every required tag appears at least once across the seed; no forbidden tag appears at all. Optional tags are permitted but not required. This is intentionally stricter than 70/20/10-style proportional rules — proportions invite per-spec gaming ("does 17% count as `light`?") and don't bind to the strategy's primary-risk-layer framing that D3.0 surfaced. Set-membership binds.

The Code-Claude failure pattern from F-3 collapses cleanly under this contract: a walking-skeleton spec with a seed entirely tagged `unit` fails the predicate at /specify seal (required `smoke` and `perceptual` are missing), halting before /plan ever reads it.

## Tag enum

Six tags. Each carries (a) a definition, (b) a primary-risk-layer signal, (c) the canonical 2026 prior the tag aligns to.

### `unit`

- **Definition.** A test exercising one function, method, or class in isolation. External dependencies — file system, network, database, time, randomness — are mocked or replaced with deterministic fakes.
- **Primary risk caught.** Internal logical correctness in algorithmic or branch-heavy code. Best-fit for pure functions, parsers, state-machine transitions, validators, layout calculators.
- **Aligns to.** Cohn pyramid base; Dodds trophy unit slice; Spotify "Implementation Detail Tests".
- **2026 cost-curve note.** LLM-generated unit tests churn faster than the code under them when they mirror implementation. Per D3.0's read-out: keep `unit` for code whose primary risk is algorithmic; do not default to `unit` for code whose primary risk is at a seam.

### `integration`

- **Definition.** A test exercising two or more components together, with the boundary to externals (third-party services, the user's filesystem outside a working dir) mocked. Internal dependencies (databases, queues, in-process caches) run as real fixtures, ideally via Testcontainers / Aspire / equivalent.
- **Primary risk caught.** Behavior at internal seams — wiring, sequencing, state propagation, error envelopes, transaction integrity.
- **Aligns to.** Fowler's narrow integration test; Dodds trophy middle; Spotify "Integration Test" (as distinct from "Integrated Test" — see below).
- **Cost curve.** The most durable test type per D3.0's anchors. Cheap to maintain (interfaces are stable), expensive enough to author that LLM-generation produces fewer of them, and high signal per test.

### `contract`

- **Definition.** A test that records a consumer's request shape and the provider's expected response shape, producing a contract artifact (Pact-style JSON, OpenAPI fixture, equivalent) that is checked into the repo and verifiable independently from the consumer code.
- **Primary risk caught.** Provider drift breaking consumer expectations; consumer drift assuming provider behavior the provider doesn't owe.
- **Aligns to.** Pact / Pactflow consumer-driven contract testing; the consumer-side of Spotify's "Integration Test" framing when the boundary is an API surface.
- **Why distinct from `integration`.** A contract test asserts message shape and content at a boundary; an integration test asserts behavior across multiple components. The 2026 discourse keeps them distinct (per D3.0's Pact / Pactflow read) because they fail in different ways and the failure-mode mapping to AC differs. Conflating them under one tag would lose api-boundary's load-bearing distinction.

### `smoke`

- **Definition.** A test that asserts a wired system boots, mounts, or runs end-to-end without crashing, but makes *no* behavioral assertions beyond "completed and produced some output." The vertical-slice equivalent of "the lights turn on."
- **Primary risk caught.** Wiring regressions across layers. A walking-skeleton's slice that goes input → logic → output → render needs to be exercised as a single chain; `smoke` is the cheapest way to do that without paying the cost of full behavioral assertions at every layer.
- **Aligns to.** Cohn's "small smoke-test suite" inside the Commit Build (per de Pauw's framing in D3.0); the thin smoke layer in 2026 trophy and honeycomb diagrams.
- **Why distinct from `integration`.** Smoke makes no behavioral assertion. A `smoke` test that asserts the home page renders and a `[smoke]` decorator-tagged unit test asserting no exceptions during boot are both smoke. An `integration` test that asserts the home page renders **with the user's session reflected in the greeting** is integration, not smoke. The line is "did it run" vs "did it run correctly."

### `perceptual`

- **Definition.** A test that produces or asserts against an artifact a human can inspect — screenshot, screencast, rendered PDF, integration transcript, structured snapshot. The artifact is checked into the repo at a documented path; the test asserts the artifact regenerates when the test re-runs (no staleness).
- **Primary risk caught.** User-observable output that no other tag can verify. A unit-correct system can still render a checkout button hidden behind a CSS bug, ship an integration transcript with the wrong field, or produce a PDF whose layout is misaligned. Perceptual is the layer that catches what would otherwise reach a user.
- **Aligns to.** Dodds trophy's UI-test layer (broadened); Schaffer / Spotify integrated-test layer (narrowed to artifact inspection rather than through-real-systems); the 2026 visual-testing layer in Momentic / Autonoma / Shiplight framings.
- **Per-strategy meaning is D3.3's surface.** D3.2 owns the tag; D3.3 owns what counts as the perceptual artifact per strategy. Walking-skeleton's perceptual is the user-facing screenshot/screencast; api-boundary's perceptual is the integration transcript; capability-cluster's perceptual is the capability's inspectable output artifact. D3.2 names the tag and requires it where required; D3.3 fills in path conventions and inspection predicates.

### `invariance`

- **Definition.** A predicate, not a new test. Asserts that the pre-existing test pass-set at the parent's `spec_sealed_at` timestamp is preserved at `/verify` time. Pass-set, not pass-count: the same tests passing, not a swap of equal cardinality.
- **Primary risk caught.** Behavior change masquerading as a refactor. Schema migrations, dependency upgrades, performance rewrites, and security-hardening passes are supposed to preserve observable behavior. `invariance` is the predicate that catches the case where they don't.
- **Aligns to.** Refactor-spike's "no new tests; pre-existing tests are the pyramid" framing from D3.1. Mutation-testing parity is a possible richer predicate (per D3.0's read-out on Stryker / mutmut / pitest maturity in 2026) but is parked for v0.2.x; pass-set parity is v0.2's primitive.
- **D3.3 owns the predicate text** — D3.2 names the tag and requires it for refactor-spike; D3.3 specifies the pass-set capture mechanism (which test runner output, which storage path, which comparison rule).

## Per-strategy pyramid catalog

Each row names the strategy and its three tag sets. Required tags must appear at least once across the failing-test seed. Forbidden tags must not appear at all. Optional tags are permitted but not required.

### walking-skeleton

- **Required:** `smoke`, `perceptual`.
- **Optional:** `unit`, `integration`.
- **Forbidden:** `contract`, `invariance`.
- **Why this shape.** D3.1's framing — vertical-thin slices that exercise every layer and keep an end-to-end demoable artifact alive. The slice's primary risk is at the seams between layers (smoke catches wiring failures) and at the user-visible output (perceptual catches what would otherwise reach a user). Unit tests are reserved for algorithmically dense code the slice exercises (parsers, layout calculators); integration is allowed where two specific components have a non-trivial interaction worth isolating. `contract` is forbidden because walking-skeleton's deliverable is not a contract surface; `invariance` is forbidden because walking-skeleton authors new perceptible behavior, not behavior preservation.

### api-boundary

- **Required:** `contract`, `perceptual`.
- **Optional:** `unit`, `integration`.
- **Forbidden:** `smoke`, `invariance`.
- **Why this shape.** D3.1's framing — one consumer-facing surface bounded by an explicit external contract per child. Contract is the load-bearing tag (the Pact-shape artifact records what the consumer expects, what the provider returns). Perceptual is the integration-transcript surface per D3.0's read on api-boundary's evidence shape (`docs/specs/NNNN-<slug>/perceptual/integration-transcript.md` per D3.1's pre-stage; final path/schema is D3.3's). Unit is allowed for internally-complex logic (parsers, validators) where it exists; integration is allowed where the surface composes multiple internal components. `smoke` is forbidden because api-boundary's deliverable is a contract, not a wired-system check — a smoke-passing api-boundary spec is a /specify defect that masks contract gaps; `invariance` is forbidden for the same reason as walking-skeleton.

### capability-cluster

- **Required:** `integration`, `perceptual`.
- **Optional:** `unit`.
- **Forbidden:** `smoke`, `contract`, `invariance`.
- **Why this shape.** D3.1's framing — discrete user-visible capability composed of multiple user-meaningful actions. The capability boundary is where the primary risk lives (does the user invoking the capability end-to-end get the right artifact?). Integration tests at the capability boundary dominate; per-action unit tests cover algorithmic complexity within each action where it exists. Perceptual is the capability's inspectable output artifact (rendered PDF, scheduled event, share-post — D3.3 fills in path conventions). `smoke` is forbidden because a capability-cluster spec already has a walking skeleton beneath it (per D3.1's signal — capability-cluster is for products *past* greenfield); a smoke test at the capability grain is misclassified — it belongs in the underlying skeleton's spec. `contract` is forbidden because capability-cluster's deliverable is a user capability, not a consumer-facing contract; if a contract surface is part of the capability, the spec is likely hybrid.

### refactor-spike

- **Required:** `invariance`.
- **Optional:** (none).
- **Forbidden:** `unit`, `integration`, `contract`, `smoke`, `perceptual`.
- **Why this shape.** D3.1's framing — enabling change that preserves user-observable behavior. The strategy authors no new tests at the spec grain; the contract is invariance. The failing-test seed at the parent grain is empty (count = 0); the verifier predicate is "pre-existing test pass-set at `spec_sealed_at` is preserved at `/verify` time" (D3.3 owns the predicate text). All other tags are forbidden because their presence at the parent grain indicates the strategy is wrong — a refactor-spike spec that includes a new `[unit]` test is a /specify defect; clarify-walker surfaces it as "AC implies new perceptible behavior; strategy may be incorrect."

### hybrid

- **Pyramid shape at parent grain:** `null`. No parent-level required/forbidden tags; no parent-level failing_test_seed.
- **Per-child:** each child's pyramid_shape is populated per the child's strategy at `/plan`'s decomposer-write time. Validation cascades to per-child predicates; the parent has none.
- **Why this shape.** D3.1's framing — hybrid is a flag, not a guide. A parent-level pyramid declaration on a hybrid parent would either be a meaningless union of its children's shapes or a guess that downstream stages would have to override. Better: no parent-level shape, every child carries its own, gates compose at the child grain. /plan's decomposer halts §hybrid-without-child-overrides (per D3.1) if any child lands without an explicit strategy, which transitively means without a pyramid_shape.

### Catalog summary (machine-readable)

```json
{
  "walking-skeleton": {
    "required": ["smoke", "perceptual"],
    "optional": ["unit", "integration"],
    "forbidden": ["contract", "invariance"]
  },
  "api-boundary": {
    "required": ["contract", "perceptual"],
    "optional": ["unit", "integration"],
    "forbidden": ["smoke", "invariance"]
  },
  "capability-cluster": {
    "required": ["integration", "perceptual"],
    "optional": ["unit"],
    "forbidden": ["smoke", "contract", "invariance"]
  },
  "refactor-spike": {
    "required": ["invariance"],
    "optional": [],
    "forbidden": ["unit", "integration", "contract", "smoke", "perceptual"]
  },
  "hybrid": null
}
```

This map is cached as the populator at `/specify` step 3. Sealed specs hold their then-current pyramid_shape; future minor-version map changes do not retroactively invalidate sealed specs.

## Spec template addition

Modify `docs/templates/spec.md.template`'s `## Failing-test seed` section to:

```markdown
## Failing-test seed

**Pyramid shape:** _<strategy>_-shaped — required: `<tag1>`, `<tag2>`. Optional: `<tag3>`, `<tag4>`. Forbidden: `<tag5>`, `<tag6>`.

_Populated by /specify step 3 from the strategy declared in `## Decomposition strategy`. Off-shape composition is a /specify defect; /plan's decomposer halts on it._

**Tests.** Language-appropriate test functions. Code-Claude scaffolds these as the first commit; they are the backpressure contract /build runs every iteration. Name each test, tag its layer with one of `unit | integration | contract | smoke | perceptual | invariance`, and state what it asserts. Do not write the implementation here.

- `test_<name>` — `[<tag>]` — asserts <behavior>; covers AC-1.
- `test_<name>` — `[<tag>]` — asserts <behavior>; covers AC-2.
- `test_<name>` — `[<tag>]` — asserts <behavior>; covers AC-3.

Every AC must be covered by at least one named test. Every required tag in the pyramid shape must appear in at least one test. No forbidden tag may appear in any test. Violations are /specify defects — /plan's decomposer halts the cascade on them (halt-messages.md §pyramid-shape-violation, §pyramid-tag-invalid, §incomplete-failing-test-seed).
```

Three substantive changes from the current template: the **Pyramid shape** preamble line, the **per-test tag** in `[<tag>]` notation, and the bullet under it specifying tag enum and the three halt conditions.

For **refactor-spike**, the Tests block is rendered as:

```markdown
**Tests.** None at this spec grain. Refactor-spike preserves the pre-existing test pass-set; the invariance predicate is owned by /verify (see D3.3).

The pyramid shape's `invariance` tag is satisfied by the existence of a pre-existing test pass-set at `spec_sealed_at`; no per-test entries are authored.
```

For **hybrid parents**, the section is rendered as:

```markdown
**Pyramid shape:** _hybrid_ — no parent-level pyramid. See per-child shapes in `decomposition.md` after /plan runs.

**Tests.** None at this parent spec grain. Per-child tests live in each child's spec (heavyweight children) or ticket description (lightweight children).
```

## /specify mechanics — step 3 detail

The 7-step `/specify` flow per `specify-SKILL.md` and D3.1's Negotiation protocol table. Step 3 is where D3.2 enters.

### Inputs at step 3

1. `## Decomposition strategy` from the spec markdown (sealed-or-draft at step 1, confirmed at step 5; step 3 reads the current value).
2. `## Acceptance criteria` from the spec markdown (drafted at step 2).
3. The D3.2 catalog (the JSON map above), cached in the `/specify` skill.

### Step 3 procedure

1. **Look up the per-strategy pyramid shape** from the catalog. For hybrid, skip to step 8 (no parent-level seed). For refactor-spike, populate the Pyramid shape line and emit the no-tests rendering; skip to step 8.
2. **Populate the Pyramid shape line** in the spec markdown with the strategy's required / optional / forbidden tag sets verbatim.
3. **Draft tests per AC.** Every AC requires at least one test entry per the existing `## Failing-test seed` contract (unchanged from current template).
4. **Tag each test** with one of the six enum values. The tag is chosen by /specify based on what the test asserts:
   - Test asserts a single function or class in isolation → `unit`.
   - Test asserts behavior across 2+ in-process components with externals mocked → `integration`.
   - Test produces or verifies a contract artifact at an API surface → `contract`.
   - Test asserts a wired system completed without crashing, no behavioral assertions → `smoke`.
   - Test produces or asserts against a human-inspectable artifact → `perceptual`.
   - (Refactor-spike only.) The pre-existing test pass-set predicate → `invariance` (no per-test entry; satisfied by the strategy declaration itself).
5. **Validate the per-spec pyramid shape** against the drafted seed:
   - Every required tag appears in at least one drafted entry. Required-missing → in-skill critique at step 3 (not yet a halt): "AC-K's tests do not yet include any `<tag>`-tagged entry; add or retag at least one entry to satisfy the pyramid."
   - No forbidden tag appears. Forbidden-present → in-skill critique: "test `test_X` is tagged `<tag>`, which is forbidden for `<strategy>`; retag to one of `<optional>` or move the test concern to a different spec."
   - Tag is in-enum. Out-of-enum → in-skill critique: "test `test_X` has tag `<bad>`, which is not in `{unit, integration, contract, smoke, perceptual, invariance}`; retag."
6. **Founder may override** any in-skill critique by accepting the draft as-is. The override is not silent — overridden critiques are recorded under the spec's `## Open Questions` section with rationale, per the existing four-hat critique pattern.
7. **Off-shape draft surfaces a strategy-conflict clarify question at step 4.** If the founder's overrides accumulate to the point that the failing-test seed contradicts the declared strategy (e.g., a walking-skeleton spec whose entire seed is `[unit]` overrides), clarify-walker emits: "the failing-test seed at draft is `unit`-dominated, but the strategy is `walking-skeleton` which requires `smoke + perceptual`; confirm strategy `walking-skeleton` with seed rework, or revise strategy to one whose shape matches the seed."
8. **Step 7 seal** writes `outputs.pyramid_shape` and `outputs.failing_test_seed[]` to the manifest per the schema below. The seal verifier predicate (next section) catches any unresolved violation.

### Why steps 5 and 7 are non-redundant

Step 5 catches violations at draft-time, giving the founder an inline critique that's cheap to act on. Step 7's seal predicate catches violations the founder explicitly overrode (per step 6) but did not back up with an Open Question entry. The two layers are differently aimed: step 5 is collaborative ("here's a thing to fix"); step 7 is the hard gate ("the seal will not accept this state").

## Manifest schema additions

D2.1 v2's `/specify` manifest outputs gain two fields:

```json
"outputs": {
  "spec_path": "...",
  "ac_list_sha256": "...",
  "acceptance_criteria": [...],
  "decomposition_strategy": "walking-skeleton",
  "pyramid_shape": {
    "strategy": "walking-skeleton",
    "required_tags": ["smoke", "perceptual"],
    "optional_tags": ["unit", "integration"],
    "forbidden_tags": ["contract", "invariance"]
  },
  "failing_test_seed": [
    {
      "name": "test_login_form_mounts",
      "tag": "smoke",
      "asserts": "the login route mounts and the form renders without throwing",
      "covers_ac": ["AC-1"]
    },
    {
      "name": "test_login_redirects_on_success",
      "tag": "perceptual",
      "asserts": "screenshot at docs/specs/0042-login/perceptual/post-login.png regenerates and matches the expected layout token",
      "covers_ac": ["AC-2"]
    }
  ]
}
```

Two changes from D2.1 v2:

- **New top-level field `pyramid_shape`.** Object with `strategy`, `required_tags`, `optional_tags`, `forbidden_tags`. For hybrid parents: `null`. For refactor-spike: `{strategy: "refactor-spike", required_tags: ["invariance"], optional_tags: [], forbidden_tags: [...all others]}`.
- **`failing_test_seed[]` entry gains the `tag` field.** Existing fields (`name`, `asserts`, `covers_ac[]`) are unchanged. Per-entry shape becomes mandatory: `{name, tag, asserts, covers_ac}`. Entries without a `tag` field fail the verifier predicate.

For refactor-spike: `failing_test_seed[]` is an empty array (`[]`), not absent. For hybrid parents: also empty.

The schema is additive to D2.1 v2; sealed manifests under the prior schema (without `pyramid_shape` or per-entry `tag`) fail D3.2's verifier predicates at the next downstream stage's pre-flight. Migration path: re-seal under `/specify <MARKER>-N --unseal` is the only sanctioned recovery; there is no manifest-rewrite tool in v0.2 and back-patching the field by hand breaks `ac_list_sha256` chain integrity at the next stage.

## Verifier predicates

D2.1 v2's `/specify` verifier predicate block gains:

1. **`pyramid_shape.strategy == outputs.decomposition_strategy`.** The shape strategy field matches the decomposition strategy. Mismatch halts §pyramid-shape-violation.
2. **`pyramid_shape` content matches the catalog.** Given `decomposition_strategy`, `pyramid_shape.required_tags`, `optional_tags`, `forbidden_tags` are each set-equal to the catalog values. Tampering halts §pyramid-shape-violation. (Catalog version is implicit at seal; D2.1 v2's manifest already records `schema_version` per the model, which captures the catalog version for audit.)
3. **For non-hybrid, non-refactor-spike strategies:** every entry in `pyramid_shape.required_tags` appears in `{e.tag for e in failing_test_seed}`. Missing-required halts §pyramid-shape-violation.
4. **For non-hybrid, non-refactor-spike strategies:** `pyramid_shape.forbidden_tags ∩ {e.tag for e in failing_test_seed} == ∅`. Forbidden-present halts §pyramid-shape-violation.
5. **Every entry's tag is in-enum.** `∀ e ∈ failing_test_seed, e.tag ∈ {unit, integration, contract, smoke, perceptual, invariance}`. Out-of-enum halts §pyramid-tag-invalid.
6. **For refactor-spike:** `failing_test_seed[] == []` AND `pyramid_shape.required_tags == ["invariance"]`. Non-empty seed under refactor-spike halts §pyramid-shape-violation with the specific message "refactor-spike must have an empty failing-test seed; invariance is a /verify-time predicate, not an authored test."
7. **For hybrid parents:** `pyramid_shape == null` AND `failing_test_seed[] == []`. Non-null shape or non-empty seed on a hybrid parent halts §pyramid-shape-violation with message "hybrid parent must defer pyramid shape and tests to children."

Each predicate is independent and recomputable from the spec markdown's text — `/specify`'s seal verifies its own outputs, and every downstream stage that consumes `failing_test_seed[]` or `pyramid_shape` re-verifies them at pre-flight per D2.1 v2's chain.

### Downstream consumer touch-points

- **`/plan`'s decomposer** reads `pyramid_shape` to know which tags are required for children (per-child shapes are written by the decomposer at decomposition.md write time; a non-hybrid parent's children inherit the parent's pyramid_shape unless an override finding flips the child's strategy per D3.1). Children's `failing_test_seed[]` is a strict subset of parent's, per existing /plan-SKILL contract; D3.2 layers on top: each child's seed must satisfy its own pyramid_shape (inherited or overridden).
- **`/build`'s Ralph loop** is unchanged at the iteration level — the seed is still the backpressure contract. D3.2 adds that `/build`'s pre-flight reads `pyramid_shape` from the parent manifest and rejects a seed file that mutates tags from what was sealed. Drift detection (the first-FAIL hash from D2.1 v2) is unchanged.
- **`/wrap`** is unchanged. Red tests still block.
- **`/verify`** reads `pyramid_shape` to know which gates fire per stage. D3.4 owns the gate-firing logic; D3.2 only guarantees the shape is on the manifest.
- **`/retro`** can read `pyramid_shape` and tag distribution across children to surface "this milestone shipped 12 children, 9 walking-skeleton, 2 capability-cluster, 1 refactor-spike" framing. Not load-bearing; informational.

## Halt conditions

Two new entries for `docs/templates/halt-messages.md`.

### §pyramid-shape-violation

- **When:** /specify's seal verifier or /plan's pre-flight detected the failing-test seed violates the per-strategy pyramid shape. Specific sub-cases: missing required tag; forbidden tag present; pyramid_shape.strategy ≠ decomposition_strategy; pyramid_shape content ≠ catalog value for the strategy; refactor-spike with non-empty seed; hybrid parent with non-null shape or non-empty seed.
- **Recommendation:** `/specify <MARKER>-N --continue`, retag tests or revise the failing-test seed to satisfy the pyramid.
- **Rationale:** A pyramid-violating seed is a /specify defect; downstream stages cannot iterate around it because the seed shape is upstream of every downstream gate.
- **Alternatives:**
  1. `/specify <MARKER>-N --unseal` — if the violation is structural rather than a small retag (e.g., the strategy was wrong and the seed is correct).
  2. For refactor-spike with non-empty seed: consider whether the spec is genuinely refactor-spike or should be hybrid; re-seal under the correct strategy.
- **Diagnostic context:** violation sub-case (missing-required | forbidden-present | strategy-mismatch | shape-tampering | refactor-spike-nonempty | hybrid-nonempty), strategy verbatim, required tags verbatim, forbidden tags verbatim, the failing seed entry's name + tag if applicable.

### §pyramid-tag-invalid

- **When:** A test entry in the failing-test seed has a `tag` value not in `{unit, integration, contract, smoke, perceptual, invariance}`.
- **Recommendation:** `/specify <MARKER>-N --continue`, retag the offending entry to one of the canonical six.
- **Rationale:** Out-of-enum tags are unverifiable by definition; D3.4's gate-firing predicates cannot match against them.
- **Alternatives:** None — retag is the only recovery.
- **Diagnostic context:** offending entry name, offending tag value, canonical enum verbatim.

### Modification to §incomplete-failing-test-seed

The existing halt §incomplete-failing-test-seed (AC not covered by the parent's failing-test seed) is orthogonal to pyramid tagging and remains unchanged. When both fire simultaneously — e.g., an AC has no coverage AND the seed violates the pyramid — the halt-card surfaces both findings, with `§incomplete-failing-test-seed` taking precedence on the recommendation line because adding a test is the action that resolves both halts.

## Spec template example — walking-skeleton

For a concrete render, a walking-skeleton spec's `## Failing-test seed` section as authored by `/specify` step 3:

```markdown
## Failing-test seed

**Pyramid shape:** _walking-skeleton_-shaped — required: `smoke`, `perceptual`. Optional: `unit`, `integration`. Forbidden: `contract`, `invariance`.

_Populated by /specify step 3 from the strategy declared in `## Decomposition strategy`. Off-shape composition is a /specify defect; /plan's decomposer halts on it._

**Tests.**

- `test_login_route_mounts` — `[smoke]` — asserts the `/login` route mounts and the form renders without throwing; covers AC-1.
- `test_login_submit_round_trip` — `[smoke]` — asserts a submit handler fires against a mock auth endpoint and the loading state appears; covers AC-2.
- `test_login_redirect_screenshot` — `[perceptual]` — asserts the screenshot at `docs/specs/0042-login/perceptual/post-login.png` regenerates with the expected layout when a successful auth returns; covers AC-2.
- `test_password_validation_rules` — `[unit]` — asserts the password validator's branch coverage on length, character-class, and disallowed-pattern rules; covers AC-3.

Every AC must be covered by at least one named test. Every required tag in the pyramid shape must appear in at least one test. No forbidden tag may appear in any test. Violations are /specify defects.
```

The four entries collectively satisfy: required `smoke` appears (twice), required `perceptual` appears (once), optional `unit` appears (once), forbidden tags absent. AC-1, AC-2, AC-3 each have at least one named test.

## Spec template example — api-boundary

```markdown
## Failing-test seed

**Pyramid shape:** _api-boundary_-shaped — required: `contract`, `perceptual`. Optional: `unit`, `integration`. Forbidden: `smoke`, `invariance`.

_Populated by /specify step 3 from the strategy declared in `## Decomposition strategy`. Off-shape composition is a /specify defect; /plan's decomposer halts on it._

**Tests.**

- `test_create_invoice_contract` — `[contract]` — asserts the consumer-side Pact for `POST /v1/invoices` records the documented request shape and the 201 response envelope; covers AC-1, AC-2.
- `test_create_invoice_malformed_input` — `[contract]` — asserts the contract for malformed payload returns the documented `error_envelope` with `code = "INVALID_INPUT"`; covers AC-3.
- `test_create_invoice_idempotency` — `[contract]` — asserts the contract for a retried request with the same idempotency key returns the original resource without duplication; covers AC-4.
- `test_create_invoice_integration_transcript` — `[perceptual]` — asserts the integration transcript at `docs/specs/0042-invoices/perceptual/integration-transcript.md` regenerates from a documented consumer sequence and is byte-stable across runs; covers AC-1 through AC-4.

Every AC must be covered by at least one named test. Every required tag in the pyramid shape must appear in at least one test. No forbidden tag may appear in any test. Violations are /specify defects.
```

Required `contract` and `perceptual` both appear; forbidden `smoke` and `invariance` absent.

## Spec template example — refactor-spike

```markdown
## Failing-test seed

**Pyramid shape:** _refactor-spike_-shaped — required: `invariance`. Optional: (none). Forbidden: `unit`, `integration`, `contract`, `smoke`, `perceptual`.

_Populated by /specify step 3 from the strategy declared in `## Decomposition strategy`. Off-shape composition is a /specify defect; /plan's decomposer halts on it._

**Tests.** None at this spec grain. Refactor-spike preserves the pre-existing test pass-set; the invariance predicate is owned by /verify (see D3.3).

The pyramid shape's `invariance` tag is satisfied by the existence of a pre-existing test pass-set at `spec_sealed_at`; no per-test entries are authored.
```

## Carry-forward and forward-references

- **D3.1's catalog is D3.2's populator.** Any future change to the strategy → shape mapping updates D3.1 (the strategy semantics) and D3.2 (the populator catalog) in lockstep. The JSON catalog at the top of this doc is the canonical machine-readable form.
- **D3.3 owns the meaning of `perceptual` per strategy and the predicate text for `invariance`.** D3.2 names the tags and requires them where required; D3.3 fills in:
  - Walking-skeleton perceptual = screenshot/screencast at user-facing surface, path convention `docs/specs/NNNN-<slug>/perceptual/`.
  - Api-boundary perceptual = integration transcript, path convention `docs/specs/NNNN-<slug>/perceptual/integration-transcript.md`, schema TBD (markdown-only in v0.2; structured shadow as v0.2.x consideration per D3.0).
  - Capability-cluster perceptual = inspectable artifact at capability boundary, path convention per artifact type.
  - Refactor-spike invariance = "pre-existing test pass-set at `spec_sealed_at` timestamp is preserved at /verify time" — pass-set membership, not pass-count.
- **D3.4 composes pyramid_shape + tags into gate-firing logic.** Out of D3.2's scope. D3.2 only guarantees the shape is on the manifest and is checkable.
- **D2.1 v2's manifest schema is extended additively.** `pyramid_shape` is a new top-level outputs field; `tag` is a new per-entry field on `failing_test_seed[]`. No existing field's meaning changes.
- **The `[tag]` notation in the spec markdown** uses a one-word lowercase value in square brackets following the test name, separated by em-dash. The existing example in `docs/specs/0001-wrap-build-log/spec.md` uses `[unit]` exactly this way and is template-compliant under D3.2 with no rewrite needed.
- **Mutation testing is parked for v0.2.x.** Per D3.0, mutation-pass-rate parity is a plausible richer predicate for refactor-spike's invariance, but the install-and-CI surface area is non-trivial. v0.2 ships pass-set parity; v0.2.x re-evaluates.

## Open questions for downstream Phase 3 docs

1. **D3.3 (perceptual semantics and invariance predicate).** Already named above. D3.3 owns the path conventions and inspection predicates per strategy, plus the refactor-spike invariance predicate text. D3.2's `pyramid_shape.required_tags` containing `perceptual` or `invariance` is the contract that downstream stages route through D3.3 for execution.
2. **D3.4 (gate-firing logic).** Per-strategy, per-child, per-stage: which gates fire when? Walking-skeleton fires perceptual at every child; api-boundary fires perceptual at the milestone; capability-cluster fires perceptual at the capability's seal; refactor-spike fires invariance at /verify only. Hybrid composes per-child. D3.4 formalizes.
3. **Smoke vs integration boundary on capability-cluster.** D3.2 forbids `smoke` at the capability-cluster grain on the reasoning that capability-cluster sits atop an existing walking-skeleton. If a /specify defect produces a smoke-tagged test on a capability-cluster spec, the recommendation is to move the test concern into the underlying skeleton's spec. This is a /specify in-skill critique; D3.2 names the rule but does not specify the cross-spec routing UX. Founder-level open thread for whether v0.2 should support "promote this test concern to a different spec" as a /specify operation or whether founders should handle this manually.
4. **Catalog versioning.** D3.2's JSON catalog is implicitly versioned by the manifest's `schema_version` field. If the catalog changes in a future minor version (e.g., a new strategy is added or a tag enum value is renamed), existing sealed manifests are not retroactively re-validated. Open: do we want a `pyramid_catalog_version` field on the manifest for explicit catalog-version pinning? D3.2 says no for v0.2 — the implicit `schema_version` chain is sufficient — but the field is cheap to add later if catalog churn proves higher than expected.
