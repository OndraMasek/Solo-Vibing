# D3.1 — Decomposition strategy catalog and negotiation protocol

**Status:** Design.
**Phase:** 3.
**Resolves:** F-3 (quality topology inversion), in conjunction with D3.2 + D3.3 + D3.4.
**Companion:** D3.2 (test pyramid declaration) — reads `decomposition_strategy` to shape the per-spec pyramid; D3.3 (perceptual-AC integration-coverage rule) — reads strategy to determine integration anchor and perceptual-evidence shape; D3.4 (gate definitions) — composes strategy + pyramid + coverage anchor into gate-firing predicates against D2.1 v2's verifier framework and D2.2's hook surface.

## Problem

The Bomber dogfood decomposed horizontally. Grid first, then sprites, then input handler. Three back-to-back `scope:built` shipped on a game that didn't render because nothing in the spec or plan forced a vertically-perceptible increment per ticket. F-3 (quality topology inversion) is the headline: the cascade's gates were defined against subsystem completeness — "the grid module compiles, the sprite loader compiles" — rather than against user-perceptible progress.

The mechanical fix in D2.1 v2 + D2.2 (verifier predicates, provenance binding, session enforcement) catches a stage *claiming* completion against an artifact that doesn't exist. It does not catch a stage correctly claiming completion against an artifact that no human can perceive. The remaining failure mode is upstream: the spec authored a decomposition shape that admitted three subsystem-complete children before any user-facing increment.

The fix is to make decomposition *intent* a first-class field on the spec, sealed at the same point as the AC list, visible to the four-hats, /plan's decomposer, and downstream gates. The choice of "what kind of progress this child has to deliver" becomes a named contract, not an emergent property of how AC happened to be drafted.

## Decision

Strategy is one of five canonical values — `walking-skeleton | api-boundary | capability-cluster | refactor-spike | hybrid` — locked by D2.1 v2's `/specify` verifier predicate on the `outputs.decomposition_strategy` field.

The negotiation protocol, locked from founder verification:

- **`/specify` step 1 proposes** a strategy based on context signals (greenfield/brownfield, milestone parent, presence of API-contract vs Design&UX vs refactor-pain language in the problem statement). Founder may override at any step before seal.
- **Clarify-walker (step 4) surfaces conflict** — when a four-hat finding's locus implies a different strategy than the current proposal, clarify-walker emits a strategy-conflict clarify question. Founder explicitly re-confirms or revises. Answer recorded verbatim per existing clarify-walker pattern.
- **Step 5 founder confirm** removes the "proposed by /specify; founder to confirm" annotation; revisions require rationale verbatim in the spec's new `## Decomposition strategy` section.
- **Step 7 seal** lands strategy in `outputs.decomposition_strategy`. D2.1 v2's verifier predicate insists the value is in-enum; missing or out-of-enum halts.

Grain: **parent strategy is the default; per-child overrides are decomposer-surfaced.** `/plan`'s decomposer reads parent strategy at invocation. Children inherit unless the decomposer emits a `decomposition-override` finding, which the founder resolves through the standard incorporate/defer/reject critique pattern. A `hybrid` parent strategy is a flag, not a guide — every child under a `hybrid` parent must carry an explicit strategy or `/plan` halts.

## Catalog

Each entry uses a fixed shape: definition / signal / milestone shape / child-shape bias / AC shape / forward-to-D3.2 / forward-to-D3.3.

### walking-skeleton

- **Definition.** Each child delivers a vertically thin slice that exercises every layer of the stack and keeps an end-to-end demoable artifact alive across the cascade.
- **Signal.** Greenfield user-facing product; the question "does it actually work end-to-end" outweighs subsystem completeness; the founder can put a user in front of the artifact after every child and have something to show.
- **Milestone shape.** One playable/usable increment per milestone (per D1). Milestone title shape: "[MARKER] M-N: \<user can do X\>".
- **Child-shape bias.** Vertical-heavy. Each child is a slice through input → logic → output. Horizontal children only for genuine shared infrastructure (asset loader, state container, scene graph). The Bomber-failure shape — child = one subsystem in isolation — is a /specify defect under this strategy and clarify-walker surfaces it.
- **AC shape.** "User can X" exclusively at the parent grain. Every AC names an observable user action and an observable outcome. Subsystem-state AC ("the grid stores N×M cells in a 2D array") is a /specify defect under this strategy; clarify-walker surfaces it as a "AC-K is implementation-state, not observable behavior" finding.
- **Forward to D3.2.** Pyramid heavy at smoke (each layer minimally exercised by the slice) and perceptual (the demo at the end). Integration mid-thin.
- **Forward to D3.3.** Perceptual gate is dominant — screenshot, screencast, or interactive walkthrough required at every milestone; per-child perceptual evidence optional but encouraged.

### api-boundary

- **Definition.** Each child delivers one consumer-facing surface (endpoint, method, class, function signature) bounded by an explicit external contract.
- **Signal.** Library, SDK, backend service, CLI, anything where the deliverable is a contract a consumer integrates against. The spec contains an "API contract" or "DX section" block (per spec template) rather than a "Design & UX" block.
- **Milestone shape.** One API boundary delivered per milestone (per D1). Milestone title shape: "[MARKER] M-N: \<surface\> available".
- **Child-shape bias.** Vertical per surface; horizontal for shared auth, serialization, error-envelope, retry / backoff infrastructure. One child = one endpoint or one method, end to end (parse → validate → execute → respond).
- **AC shape.** "Consumer calling X with Y receives Z." Contract-shaped. Edge cases at the contract surface (malformed input, auth failures, rate limits, idempotency) are first-class AC, not "Edge cases & error states" footnotes.
- **Forward to D3.2.** Contract tests dominate. Integration above unit (a malformed-input test is more valuable than 17 unit tests of the validator's branches). Perceptual layer is end-to-end consumer-call sequences, not screenshots.
- **Forward to D3.3.** Perceptual evidence = end-to-end transcript of a documented consumer integration sequence at a known path (`docs/specs/NNNN-<slug>/perceptual/integration-transcript.md` or equivalent). This is one canonical replacement for D3.3's current "N/A for non-UI" escape hatch.

### capability-cluster

- **Definition.** Each child delivers one component of a discrete user-visible capability composed of multiple user-meaningful actions.
- **Signal.** Walking skeleton already exists; product growth happens by adding bundled capabilities rather than by deepening the skeleton. The spec describes a capability ("export to PDF", "share to social", "schedule recurring reminders") whose components are themselves user-meaningful ("page layout", "image embedding", "page numbering" inside the PDF export).
- **Milestone shape.** One capability live per milestone (per D1). Milestone title shape: "[MARKER] M-N: \<capability\> available".
- **Child-shape bias.** Mixed. Vertical children for each user-meaningful action within the capability; horizontal for shared utilities that bind the capability together (e.g., a PDF renderer underneath three vertical "export" children).
- **AC shape.** Mixed. Per-action "user can X" AC for each vertical component, plus capability-level invariant AC ("export preserves layout fidelity within 5%", "capability fails closed on quota exceeded").
- **Forward to D3.2.** Integration tests at the capability boundary dominate; unit tests under each action. Perceptual at the capability's user surface.
- **Forward to D3.3.** Perceptual evidence at the capability boundary — the user can invoke the capability end-to-end and the resulting artifact (PDF, share-post, scheduled-event) is inspectable.

### refactor-spike

- **Definition.** Each child performs an enabling change that preserves user-observable behavior. Pre-existing tests must remain green; no new perceptual AC is produced.
- **Signal.** Schema migration, dependency upgrade, internal restructure, performance rewrite, security hardening. The spec's "Problem statement" names internal pain (test slowness, schema drift, dep deprecation, security audit finding) rather than user pain.
- **Milestone shape.** Typically lives within an existing milestone rather than constituting one. A refactor-spike spanning multiple milestones is a hybrid candidate — /plan's decomposer flags it.
- **Child-shape bias.** Horizontal by definition. Vertical children are an anti-pattern under this strategy; if a "user can X" AC surfaces during drafting, the strategy is wrong and clarify-walker surfaces it.
- **AC shape.** Invariance AC. "All existing tests pass." "Behavior X is unchanged at the API boundary." "Schema migrates from V to V+1 with zero data loss." "p95 latency improves by Y under the documented load profile." No "user can X" AC at the spec grain.
- **Forward to D3.2.** Pre-existing tests are the pyramid. No new perceptual AC; the gate is "green test preservation across the refactor" plus any explicit invariance AC.
- **Forward to D3.3.** No perceptual evidence required at the spec grain — pre-existing integration tests are the anchor. (This is the second canonical replacement for the "N/A for non-UI" escape hatch: refactor-spike is one of the legitimate non-perceptual strategies.)

### hybrid

- **Definition.** A parent that genuinely contains slices of two strategies. Treated as a meta-strategy: the parent's strategy field is `hybrid` as a flag, not a guide; per-child overrides are required for every child.
- **Signal.** Rare. Either the founder picks consciously (a feature is half walking-skeleton, half refactor-spike), or /plan's decomposer surfaces a finding that the parent resists a single strategy. **First preference is to split the parent into two parents** under different strategies; hybrid is reserved for the case where the slices are too small or too coupled to split cleanly.
- **Milestone shape.** Per D1, hybrid milestones are unusual. A hybrid parent typically lives under an existing milestone whose primary strategy already matches one of the hybrid's component slices.
- **Child-shape bias.** Per-child explicit. `/plan`'s decomposer marks each child's strategy in `decomposition.md` under the child's block.
- **AC shape.** Per the per-child strategy. The parent AC list typically splits cleanly along strategy lines; if it doesn't, the hybrid is concealing a /specify defect and clarify-walker surfaces it.
- **Forward to D3.2.** Pyramid per-child; no parent-level pyramid declaration. Cross-child pyramid aggregation is D3.2's surface.
- **Forward to D3.3.** Per-child integration coverage anchor. The parent verify pass is the union of per-child verify outcomes.

## Negotiation protocol

The 7-step `/specify` flow per `specify-SKILL.md`, marking where strategy enters and leaves:

| Step | Strategy event |
|---|---|
| 1. Context-load | `/specify` reads spec's milestone parent (carries product-level default strategy from `/onboard` if set), problem statement, scope boundary signals (presence of API contract / Design & UX / DX section / refactor-pain language). Proposes one strategy. Records in spec's new `## Decomposition strategy` section with annotation: "proposed by /specify; founder to confirm." |
| 2. AC drafting | Strategy guides AC shape per the catalog's "AC shape" rows. Off-shape drafts trigger an in-skill critique to the founder during the drafting turn (not a halt — a flagged inline suggestion). |
| 3. Failing-test seed | Seed shaped by strategy + AC. D3.2 specs the shape; D3.1 only fixes the predicate that strategy is read here. |
| 4. Clarify-walker | Surfaces strategy-conflict findings as a clarify question. Trigger: a four-hat finding whose locus implies a different strategy than the proposal. Question shape: "your strategy proposal is X; \<hat\>'s finding implies Y; confirm X (with rationale for ignoring the finding) or revise to Y." Founder answer recorded verbatim. |
| 5. Founder confirm | Founder reviews `## Decomposition strategy` section. Annotation "proposed by /specify; founder to confirm" must be removed (presence at seal halts §strategy-missing). On revision, founder writes rationale verbatim. |
| 6. Four-hat review | Four-hats already read strategy via spec markdown. No separate handoff. Hats may produce strategy-conflict findings here; those route through clarify-walker on the next iteration. |
| 7. Seal | Strategy lands in `outputs.decomposition_strategy` per D2.1 v2 verifier predicate. Missing or out-of-enum halts. |

The annotation pattern at step 1 is load-bearing — it prevents an unattended /specify run from sealing with the strategy `/specify` proposed but the founder never reviewed. The annotation's presence at step 7 is itself a halt condition.

## /plan's decomposer reading

The decomposer (`.claude/agents/decomposer.md`) reads `## Decomposition strategy` from the parent spec at invocation, alongside its existing reads (problem statement, AC list, failing-test seed, scope boundary).

Children inherit the parent strategy by default. Per-child overrides surface as a new finding class added to the decomposer's output:

```
- **decomposition-override** [child: K] @ {locus in parent spec}: this child reads as {strategy}, not parent's {strategy}. Rationale: {1-2 sentences citing the AC or scope text that drove the call}.
```

Founder resolves these during `/plan`'s review pass the same as other critique findings — incorporate, defer, or reject. On **incorporate**: `decomposition.md` records the override under the child's block:

```markdown
### K. {verb-noun title}

- Classification: vertical | horizontal
- Strategy: {override-value if different from parent; else "inherited"}
- Description: ...
- AC: ...
- Failing-test seed: ...
- Blockers: ...
```

On **reject**: parent strategy stands for that child; the rejected finding is recorded as a margin note in `decomposition.md` per existing pattern.

A `hybrid` parent strategy implies every child must have an explicit non-inherited strategy. `/plan`'s decomposer halts with `BLOCKED §hybrid-without-child-overrides` if the parent is sealed as hybrid and the decomposition produces any child without a per-child strategy.

A non-hybrid parent with an override finding does **not** flip the parent to hybrid; the parent strategy field remains and the single override is recorded per child. Multiple overrides under a non-hybrid parent are themselves a signal — three or more override findings on a non-hybrid parent produces a decomposer-emitted critique recommending the parent re-seal as hybrid. The founder retains authority to ignore the recommendation.

## Spec template addition

New section in `docs/templates/spec.md.template`, between `## Scope boundary` and `## Acceptance criteria`:

```markdown
## Decomposition strategy

<one of: walking-skeleton | api-boundary | capability-cluster | refactor-spike | hybrid>

**Rationale:** <1-2 sentences naming why this strategy fits the spec's problem and scope boundary. Reference the catalog signal that applied.>

<!-- For hybrid parents only: -->
**Child overrides:** _Populated by /plan's decomposer at decomposition.md write; blank at /specify seal._
```

The section is required at seal. The rationale line is required and parsed by /plan's decomposer as context for its own chunking judgments.

## Halt conditions

Three new entries for `docs/templates/halt-messages.md`:

### §strategy-missing

- **When:** Spec sealed without `## Decomposition strategy` section, or with a value outside the five-strategy enum, or with the "proposed by /specify; founder to confirm" annotation still present.
- **Recommendation:** `/specify <MARKER>-N --continue`, add or correct the section.
- **Rationale:** D2.1 v2's verifier predicate requires the field; absence halts at /plan's pre-flight, but the friendlier halt is at /specify's seal step so the spec is fixed before downstream stages run.
- **Alternatives:** None — the field is load-bearing for /plan, D3.2's pyramid declaration, D3.3's integration anchor, and D3.4's gate composition.
- **Diagnostic context:** Spec path, current section state (missing | malformed | invalid-value with the offending value | annotation-present).

### §strategy-conflict-unresolved

- **When:** Clarify-walker surfaced a strategy-conflict clarify question and the spec sealed without the question being marked resolved (founder answer absent or empty).
- **Recommendation:** `/specify <MARKER>-N --unseal`, resolve the clarify question at step 4.
- **Rationale:** An unresolved strategy conflict is a sealed disagreement between founder and a four-hat finding; sealing without resolution buries the disagreement and downstream stages have no record of which view to trust.
- **Alternatives:** None — re-seal is the only sanctioned recovery. Manually editing the clarify section to mark resolved without `/specify` re-running breaks the manifest's `ac_list_sha256` chain (D2.1 v2 predicate) and is caught at /plan pre-flight anyway.
- **Diagnostic context:** Clarify question text, conflicting four-hat finding (hat, locus, severity), founder's proposed strategy at last seal attempt.

### §hybrid-without-child-overrides

- **When:** Parent sealed as `hybrid` and /plan's decomposer produced one or more children without an explicit per-child strategy.
- **Recommendation:** `/plan <MARKER>-N` re-decompose with explicit per-child strategy assignment.
- **Rationale:** Hybrid is a meta-strategy. Without per-child overrides, children inherit a flag, not a shape, and downstream gates (D3.4) cannot compose — there is no parent-level pyramid (per D3.2) or integration anchor (per D3.3) for hybrid parents.
- **Alternatives:** `/specify <MARKER>-N --unseal` if hybrid was the wrong call — first preference per the catalog is to split the parent into two parents under different strategies.
- **Diagnostic context:** Parent strategy = `hybrid`, list of children without strategy field, decomposer's output verbatim.

## Verifier predicates

D3.1 adds no new fields to D2.1 v2's manifest schema. The existing `outputs.decomposition_strategy ∈ {walking-skeleton, api-boundary, capability-cluster, refactor-spike, hybrid}` enum constraint stands.

What D3.1 adds is operational:

1. **Populator** — strategy set by `/specify` step 1 proposal + founder confirm at step 5.
2. **Negotiation surface** — clarify-walker at step 4 catches founder-vs-four-hat conflict.
3. **Downstream consumer** — `/plan`'s decomposer reads strategy and surfaces per-child override findings; halt §hybrid-without-child-overrides closes the override loop for hybrid parents.

D3.4 will compose strategy into gate-firing predicates that hook into D2.1 v2's verifier framework. Out of D3.1's scope.

## Carry-forward and forward-references

- **D2.1 v2's enum is canonical.** D3.1 names the five strategies; D2.1 v2 owns the field on `/specify`'s manifest. Any future change to the enum updates both docs in lockstep.
- **D1's milestone-shape mapping is D3.1's canonical map.** D1 already references "per D3.1" in its Milestones section. D3.1 confirms the three mappings D1 already names (walking-skeleton = playable increment, api-boundary = boundary delivered, capability-cluster = capability) and adds the two D1 did not yet need (refactor-spike, hybrid).
- **`/onboard` product-level default.** Founder may specify a product-level default strategy at `/onboard`. The default flows through to `/specify`'s step 1 as the proposal seed for the first feature. Subsequent features may diverge per spec. D3.1 does not require this; it composes if /onboard provides it.
- **D3.2 (test pyramid)** reads strategy to determine pyramid shape per spec. The catalog's "Forward to D3.2" rows are stubs; D3.2 fills them.
- **D3.3 (perceptual-AC integration coverage)** reads strategy to determine integration coverage anchor and what counts as perceptual evidence per spec. The catalog's "Forward to D3.3" rows are stubs; D3.3 fills them. The api-boundary and refactor-spike entries pre-stage D3.3's resolution of the "N/A for non-UI" escape hatch — they are two of the legitimate non-perceptual-screenshot strategies, each with its own concrete evidence shape.
- **D3.4 (gate definitions)** composes strategy + D3.2 pyramid + D3.3 coverage anchor into per-stage gate predicates that hook into D2.1 v2's verifier-predicate framework and D2.2's hook surface.

## Open questions for downstream Phase 3 docs

1. **D3.2:** What test-pyramid distribution does each strategy imply, concretely? Pyramids vary materially — walking-skeleton heavy at smoke + perceptual, api-boundary heavy at contract / integration, refactor-spike no-new-tests + invariance-only, capability-cluster heavy at capability-boundary integration. Research step recommended before D3.2 (Cohn-pyramid vs Honeycomb-trophy vs LLM-cost-curve-adjusted shapes in 2026 practice).
2. **D3.3:** What integration-coverage anchor and perceptual-evidence shape does each strategy require? Specifically: api-boundary's "consumer integration transcript at a known path" needs concrete schema (markdown? structured JSON? both?). Refactor-spike's "pre-existing tests are the anchor" needs a verifier predicate replacing the current N/A escape hatch — likely "pre-existing test pass-count at the parent's spec_sealed_at timestamp is preserved at /verify time."
3. **D3.4:** Which gates fire when, as a function of strategy + child shape + parent gate state? Specifically: does walking-skeleton fire perceptual at every child, every milestone, or both? Does refactor-spike skip the perceptual gate entirely, or use an invariance-preservation predicate in its place? How do hybrid parents aggregate per-child gate outcomes?
4. **Founder-level open question (not blocking D3.x):** the "product-level default strategy at /onboard" is mentioned in carry-forward as optional. If we want it required, /onboard needs a strategy-elicitation prompt added — that's a /onboard skill change that should be batched with other Phase 4 cleanup, not slipped into D3.1.
