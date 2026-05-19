# D3.0 — Test-pyramid research synthesis

**Status:** Research, one-page synthesis.
**Phase:** 3.
**Feeds:** D3.2 (per-strategy pyramid shape) primarily; D3.3 (integration anchor for api-boundary and refactor-spike) secondarily.
**Scope:** the three questions named in the carry-forward note from the prior session. Searches dated May 19, 2026.

## Bottom line

1. **Pyramid-as-default is no longer the 2026 consensus shape.** Integration-heavy shapes (trophy, honeycomb, diamond) hold majority mindshare for non-monolith architectures. The pyramid retains validity for monolithic, domain-heavy code where most complexity lives in pure logic; outside that shape, "write a unit test first" is contested.
2. **LLM-generated code shifts the cost curve, but the direction is disputed.** Two coherent camps. Camp A (Bray, Garg, Jovanović, Autonoma, Shiplight): LLM-generated unit tests churn faster than the code they test because LLMs write implementation-mirror tests rather than behavior tests; integration tests on stable boundaries hold value longer per unit of upkeep, so the pyramid should flatten or invert. Camp B (de Pauw / ThinkingLabs): the pyramid's economic logic was never primarily about authoring cost — it was about feedback latency and signal precision at the commit-build stage. Cheap authoring doesn't change either; if LLM-coded systems have ephemeral implementations such that unit tests cannot serve, that's a flag to reconsider the LLM workflow, not the pyramid. Both camps agree integration tests at stable boundaries are durable assets. They disagree on whether unit tests retain their pyramid-base role.
3. **The "Boz-Bryden integration-coverage framing" referenced in the prior session's carry-forward note is not recoverable.** No public-discourse prior on test pyramids or integration coverage is published under that name; web search returns no relevant hits. Treating it as a typo, misremembered name, or session-note artifact. The recoverable priors covering the same conceptual ground are: Cohn (pyramid, 2009), Dodds (trophy, 2018), Spotify / Schaffer (honeycomb, 2018), Fowler (narrow-scoped integration tests), Rainsberger ("integrated tests are a scam" — the conceptual source of Spotify's distinction between integration tests and integrated tests). D3.2 should anchor on these.

## Q1 — Test-pyramid shape post-LLM-generated code in 2026

Mindshare is fragmented along architecture lines. For domain-heavy monoliths the pyramid still works; for distributed systems, API-centric services, and full-stack apps with thick boundaries, the trophy and honeycomb dominate the 2026 conversation. A March 2026 piece titled "The Test Pyramid Is Outdated" frames the consensus most cleanly: the question is no longer "what shape is correct" but "where do our bugs actually come from"; for distributed systems, the answer is usually integration boundaries, so the pyramid's default of "write a unit test first" produces a coverage gap at exactly the place bugs live.

The LLM cost-curve argument has crystallized in 2026 and is the new variable since training cutoff. The substance:

- **The Bray / Folding-Sky framing** (Nov 2025, still cited through 2026): unit tests are now near-free to author but expensive to maintain because LLM-generated tests mirror implementation rather than behavior, so they break on every internal refactor and trigger fix-loops that ratchet the code toward whatever shape happens to satisfy the test suite. Integration tests are still somewhat expensive to author but cheap to maintain because they test stable interfaces. Net effect: the relative ROI of integration vs unit tests has shifted toward integration.
- **The Jovanović framing** (April 2026): infrastructure (Testcontainers, Aspire, Playwright at-millisecond) has independently collapsed the historical cost premium on integration and E2E tests. Slow CI was the pyramid's economic argument; that argument is materially weaker in 2026.
- **The de Pauw / ThinkingLabs dissent** (April 2026): the pyramid's economic logic was never primarily about authoring cost. It was about commit-build feedback latency — unit tests run in seconds at every commit; integration tests don't. If LLM workflows are producing code so ephemeral that unit tests can't keep pace, the right response is to fix the LLM workflow, not invert the pyramid. The dissent is the minority view in 2026 discourse but is sharp on one point: inverting because tests churn is a symptom-treatment, not a fix.
- **Mutation testing has moved from niche to recommended-practice.** Mutmut (Python), Stryker (JS/TS), pitest (Java) are mature; running mutation tests on critical modules quarterly is the 2026 prescription for catching theatrical-but-not-verifying tests. Especially relevant for LLM-generated test suites because LLMs write theatrical tests by default.

**Read-out for D3.2.** The strategy-specific pyramid shape question lands cleanly given the discourse:

- **walking-skeleton** — the slice forces every layer to participate, so the strategy's pyramid is naturally a thin column with smoke and perceptual carrying disproportionate weight. Unit tests are reserved for genuinely complex internal logic the slice exercises but does not exhaust (parsers, layout calculators, state-machine transitions). This shape survives the 2026 critique because the slice itself is integration-shaped — every test exercises multiple layers — without paying the maintenance cost of a separate trophy/honeycomb investment.
- **api-boundary** — trophy or honeycomb. Contract tests are first-class; the Spotify "Integration vs Integrated" distinction maps directly: contract tests against the spec's named surface dominate, implementation-detail unit tests cover internally-complex logic where it exists, full-system integrated tests are minimal-to-absent. Pyramid-default would invert this and produce an over-tested validator alongside under-tested contract semantics, which is the failure mode D3.1's api-boundary catalog row already calls out ("a malformed-input test is more valuable than 17 unit tests of the validator's branches").
- **capability-cluster** — honeycomb-ish with mass at the capability boundary. The capability composes multiple actions, so the integration anchor is the capability surface itself, not the individual action. Per-action unit tests exist; capability-boundary integration tests dominate.
- **refactor-spike** — pre-existing tests are the pyramid by definition. The strategy authors no new tests at the spec grain; the contract is invariance preservation. Mutation-testing reads suggest a parallel possibility (mutation-pass-rate parity pre/post-refactor as an invariance predicate) but D3.2 should not require it — the carry-forward note's predicate ("pre-existing test pass-count at the parent's spec_sealed_at timestamp is preserved at /verify time") is the simpler primitive and is the one D3.3 is staged to formalize.
- **hybrid** — no parent-level shape. Per-child shapes per the per-child strategy.

The LLM cost-curve discourse does not change which strategy applies in which case — that's D3.1's decision and is upstream. What it changes is the per-strategy default test mix at D3.2's grain. Specifically: for all five strategies, the prescription "write more unit tests first" is replaced with "write the test at the layer the strategy's primary risk lives at." That layer varies per strategy and is what D3.2's per-strategy pyramid stub fills in.

## Q2 — Integration coverage for non-UI products in 2026 practice

Two converging shapes for what counts as evidence:

- **Contract-test artifacts (Pact-shaped).** Consumer-driven contract testing is the canonical 2026 pattern for API boundaries. Pact's contract file is a JSON record of consumer-defined request/response pairs, generated as a side-effect of running consumer-side tests against a mock provider, then verified against the real provider. In multi-team architectures the pact file is exchanged via a broker (PactFlow, pact-broker); in single-team or solo contexts it lives in the repo. The shape is recognizable: a structured artifact, paired one-to-one with a named consumer scenario, regenerated by re-running the consumer-side test.
- **Recorded integration transcripts at known paths.** Less formalized than Pact contracts but increasingly common as the artifact-of-record for API behavior: a markdown or JSON record of canonical request/response sequences, checked into the repo at a documented path, regenerated on test-run. Frequently named "fixture", "snapshot", or "transcript" depending on the testing stack. The shape is what D3.1's api-boundary row pre-stages as `docs/specs/NNNN-<slug>/perceptual/integration-transcript.md`.

**Read-out for D3.3** (D3.3 owns the predicate text; D3.0 only validates that D3.1's framing is defensible):

- D3.1's api-boundary `integration-transcript.md` is defensible as an evidence shape — it's the solo-stack equivalent of a Pact contract file, with the consumer being "documentation reader / SDK author" rather than "another service." The transcript records a documented consumer-call sequence and its responses. It's perceptual in the sense that the user — the consumer — can read it and see what calling the API gets them.
- D3.3 should decide between markdown-only, structured (JSON / YAML) shadow, or both. Trade: markdown is human-readable and stable to diff; structured shadow is machine-checkable. The recommendation from the contract-testing discourse is to keep both — the human-readable form is the documentation; the structured form is the executable spec. For solo-stack v0.2 a single markdown transcript regenerated by the integration test suite is the lowest-friction starting point; structured shadow is a v0.2.x or v0.3 add-on.
- For refactor-spike the answer is simpler. Pre-existing tests are the anchor; the verifier predicate is invariance. The carry-forward note's phrasing is correct as a starting point and D3.3 should formalize it: pre-existing test pass-count (and pass-set membership — same tests passing, not a swapped set with equal count) at the parent's `spec_sealed_at` timestamp is preserved at `/verify` time. Mutation-testing parity is a possible richer predicate but is not load-bearing for v0.2.

## Q3 — Whether four-hat / Boz-Bryden integration-coverage framing is still the relevant prior

**Not recoverable as named.** "Boz-Bryden" returns no relevant hits in 2026 web search across multiple variants. Treating it as a session-note artifact — most likely a misremembered or garbled combination of two names. The four-hat critique pattern is internal to this project and is well-established here; it isn't the prior at issue in this question.

The recoverable priors covering the conceptual ground D3.2 needs to anchor on:

- **Mike Cohn** — pyramid (*Succeeding with Agile*, 2009). The default that is being contested in 2026.
- **Kent C. Dodds** — testing trophy (2018). "Write tests. Not too many. Mostly integration." Adds static analysis as the foundation layer.
- **André Schaffer / Spotify Engineering** — honeycomb (2018). Microservice-specific. Integration tests at the boundary dominate; implementation-detail tests cover internal complexity; integrated tests (through real downstream services) are minimal. Names the J. B. Rainsberger talk *Integrated Tests Are A Scam* as the conceptual source for the integration-vs-integrated distinction.
- **Martin Fowler** — narrow-scoped integration tests (`bliki:IntegrationTest`). The Spotify "integration test" maps to Fowler's "narrow integration test" cleanly.
- **Guillermo Rauch** — original "Write tests. Not too many. Mostly integration." quote, predates Dodds's trophy framing.

D3.2 anchors on Cohn for the historical baseline, Dodds/Spotify-Schaffer for the alternative shapes, and Rainsberger for the integration-vs-integrated distinction (which is load-bearing for capability-cluster's "capability-boundary, not integrated-through-real-systems" framing). No proprietary prior is required; D3.2 has enough public anchor points to compose.

**Open thread for the founder.** If "Boz-Bryden" was a specific prior the founder intended to cite and the carry-forward note garbled it, please reply with the correct reference before D3.2 anchors. If the carry-forward note was a placeholder or session-note error, no action needed; D3.2 proceeds against Cohn / Dodds / Spotify-Schaffer / Fowler / Rainsberger as the anchor set.

## Carry-forward to D3.2

D3.2 can proceed with the following anchored:

- **The cost-curve shift is real but doesn't change D3.1's strategy choice.** What it changes is the per-strategy default test layer mix. Recommendation: D3.2's pyramid-shape stubs per strategy should explicitly cite "primary-risk-layer" as the populator rather than implying a one-size-fits-all 70/20/10 split.
- **Per-strategy shapes per Q1's read-out** are the starting points to formalize. walking-skeleton column-with-smoke-and-perceptual; api-boundary trophy/honeycomb with contract dominant; capability-cluster honeycomb-with-mass-at-capability-boundary; refactor-spike no-new-tests with invariance predicate; hybrid no-parent-shape with per-child inheritance.
- **The failing-test seed in the spec template** is currently format-tagged at the per-test level (the example in `docs/specs/0001-wrap-build-log/spec.md` uses `[unit]`; the template doesn't formalize the tag set). D3.2 should formalize the tag enum and decide whether it's per-spec (declared once in a `## Test pyramid` subsection) or per-test (the existing inline `[unit]` shape). Recommendation: both — declared per-spec for the shape contract, tagged per-test in the seed so the contract is verifiable. D3.4 will read this for gate-firing logic.
- **The pyramid declaration's spec location.** The current spec template has `## Failing-test seed` as its own section between `## Acceptance criteria` and `## Related research findings`. D3.2 should put the pyramid declaration as a `## Test pyramid` subsection inside `## Failing-test seed`, not as a new top-level section, so the pyramid lives where the seed that populates it lives. This matches the carry-forward note's own framing.
- **Mutation testing is parked as a v0.2.x consideration**, not a v0.2 requirement. It's the right tool for catching theatrical LLM-generated tests but introducing it in v0.2 adds a non-trivial install-and-CI surface area that's outside D3.2's scope.

## Carry-forward to D3.3

- **api-boundary transcript shape:** markdown at `docs/specs/NNNN-<slug>/perceptual/integration-transcript.md` is defensible as the solo-stack equivalent of a Pact file. Structured JSON shadow is a possible v0.2.x add-on but not required for v0.2.
- **refactor-spike invariance predicate:** the carry-forward note's phrasing is correct as a starting point. D3.3 formalizes "pre-existing test pass-set is preserved at /verify time" — pass-count alone is insufficient (a refactor that breaks one test and fixes another would pass count-equality), so the predicate must be pass-set membership, not pass-count.
- **capability-cluster perceptual evidence shape:** D3.0 confirms D3.1's framing — the capability boundary's resulting artifact (rendered PDF, scheduled event, posted share) inspected against AC. D3.3 owns the path / schema specification; D3.0 has nothing to add beyond confirming the framing is current.

## Sources

External, all dated May 2025 – April 2026 unless noted:

- Naina Garg, *The Test Pyramid Is Outdated — Here's What Replaced It*, Medium, March 2026.
- Peter Bray, *Unit Tests in the Age of AI: Are They Working Against Us?*, Folding Sky, November 2025.
- Thierry de Pauw, *Don't Let AI Invert The Testing Pyramid*, ThinkingLabs, April 2026.
- Milan Jovanović, *The Test Pyramid Is a Lie (and What I Do Instead)*, April 2026.
- Autonoma blog, *The Testing Pyramid Is Upside Down: E2E Tests First*, March 2026.
- Shiplight AI, *Complete Guide to E2E Testing in 2026*, late April 2026.
- *Do We Need Unit Tests in 2026?*, Slavikdev, March 2026.
- Katalon Team, *Software Testing Models: From V-Model to Test Pyramid*, February 2026.
- André Schaffer, *Testing of Microservices*, Spotify Engineering, 2018 (the canonical honeycomb piece; still cited as the prior).
- Pact / Pactflow documentation; pact-foundation/pact-js current as of 2026.
- Mike Cohn, *Succeeding with Agile*, 2009 (the canonical pyramid piece; the prior being contested).
- Kent C. Dodds, *Static vs Unit vs Integration vs E2E Testing*, 2018 (the canonical trophy piece).
- Martin Fowler, `bliki:IntegrationTest`.
- J. B. Rainsberger, *Integrated Tests Are A Scam* (presentation, the conceptual source for integration-vs-integrated distinction).
