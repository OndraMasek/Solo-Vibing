# D3.4 — Gate definitions and per-stage composition

**Status:** Design.
**Phase:** 3.
**Resolves:** F-3 (quality topology inversion) in conjunction with D3.1 + D3.2 + D3.3, by composing their predicates into per-stage gates with deterministic firing order and aggregation rules. Closes Phase 3.
**Companion:** D2.1 v2 (trust model) — D3.4 inherits its verifier-predicate-as-evidence-recompute pattern, its caller-side pre-flight sequence, and its manifest-checksum chain; D3.1 (decomposition strategy catalog) — D3.4 dispatches per-strategy at `/verify`; D3.2 (test-pyramid declaration) — D3.4 composes its `/specify`-seal predicates into the spec gate set; D3.3 (perceptual and invariance predicates) — D3.4 composes P1–P9 into the per-strategy `/verify` gate matrix.

**Anchors:** D2.1 v2's caller-side verification protocol (the model: every stage re-evaluates upstream predicates from re-read evidence; manifest existence ≡ all gates passed). The "gate" term has been informal across D2.1 v2, D3.0–D3.3 ("perceptual gate", "four-hat gate", "smoke gate"); D3.4 names the abstraction.

## Problem

D2.1 v2 named verifier predicates per stage but treated them as a flat list. D3.1 named five decomposition strategies. D3.2 added pyramid-shape and tag-enum predicates at `/specify` seal. D3.3 added perceptual and invariance predicates at `/specify` seal and `/verify`. The cumulative predicate set, by D3.3's close, is:

- D2.1 v2's per-stage `outputs` predicates (Stage-specific postcondition fields table).
- D2.1 v2's chain predicates (manifest checksum integrity, AC-hash chain, four-hat seal chain).
- D3.1's strategy predicates (annotation-confirmation at seal; hybrid-without-child-overrides at `/plan`).
- D3.2's seven pyramid predicates (strategy ≡ shape; required tags present; forbidden tags absent; tag in enum; refactor-spike empty seed; hybrid null shape; etc.).
- D3.3's nine P1–P9 strategy-evidence predicates plus seal-time configuration predicates for refactor-spike.

This is roughly 30 named predicates across six stages. Three problems are now visible:

1. **No firing order.** Which predicate evaluates first at `/specify` seal — AC coverage, pyramid shape, or strategy-evidence? D3.2 said §incomplete-failing-test-seed takes recommendation-line precedence over §pyramid-shape-violation when both fire; that is an aggregation rule, not an evaluation order. The cascade needs to decide whether an early failure short-circuits later predicates (cheap signal, less diagnostic content) or whether all predicates evaluate and the halt-card aggregates (richer diagnostic, slightly more work).
2. **No per-strategy dispatch at `/verify`.** D3.3's P1–P9 fire conditionally on the child's strategy. The dispatch logic — "for each child of the milestone, read its strategy from the manifest, fire the matching predicate set" — is not yet specified. Without it, `/verify` is a stage with predicates listed but no orchestration; in practice the dispatch would land inside the `/verify` skill's prompt and be invisible to readers of the design doc.
3. **No record of which gates evaluated.** D2.1 v2's pattern — "manifest existence ≡ all predicates passed" — works for binary decisions but provides no trail for `/retro` to read. A milestone shipping 12 children should leave a record of which gates each child cleared. Without it, `/retro` is reduced to surfacing strategy counts; richer post-mortem patterns (recurring gate failures, perceptual-coverage gaps) cannot be computed.

D3.4 names the gate abstraction, defines per-stage gate inventories, specifies the `/verify` dispatch matrix, formalizes multi-failure aggregation, and records per-child gate outcomes on `/verify`'s manifest for `/retro`'s use.

## Decision

A **gate** is a logical checkpoint at a cascade stage that evaluates a related set of verifier predicates and either passes (the stage proceeds or seals its manifest) or halts (the stage writes a diagnostic and emits a halt card). Each stage carries a small, named set of gates; gates are deterministic in firing order; failures within a gate aggregate; failures across gates produce a precedence-ordered halt card.

The gate abstraction adds no new predicate logic. Every predicate it composes is already defined by D2.1 v2, D3.1, D3.2, or D3.3. What D3.4 adds is the schedule, the dispatch table, and the aggregation rules.

Concretely:

- **Per-stage gate inventory.** Each stage has 2–5 named gates. Gates within a stage fire in a fixed order (most-upstream / cheapest-signal first). A gate passes when all its predicates pass; a gate halts when at least one predicate fails. The first failing gate at a stage may still allow later gates to evaluate (D3.4 picks per stage; default is **all-gates-evaluate, single-card-aggregate**).
- **Per-strategy `/verify` dispatch.** The milestone-level `/verify` gate iterates each child; per child, dispatches to the strategy-specific evidence gate (perceptual for walking-skeleton / api-boundary / capability-cluster; invariance for refactor-spike; recursive dispatch for hybrid).
- **Aggregation rules.** A halt card surfaces every failing gate at the stage; the recommendation line picks the most upstream gate's recommendation; the diagnostic context lists every failing predicate with its sub-case.
- **Gate outcomes recorded on `/verify` outputs.** A new `children_gate_outcomes[]` field captures per-child gate results so `/retro` can read them; format below.
- **`solo-verify` CLI parity** for every stage's gate set, plus `--gate <name>` for single-gate evaluation and `--explain <gate>` for the gate's predicate text.

The framing aligns with D2.1 v2: a gate is a presentation layer over predicates; manifest existence still ≡ all gates passed. The additional bookkeeping is a single per-stage record of which gates were evaluated, surfaced to humans and to `/retro`.

## What is a gate

A gate has four properties:

1. **Name** — `kebab-case`, stage-scoped (e.g., `spec.pyramid-shape`, `verify.perceptual-evidence`, `build.test-execution`). Stage prefix is the cascade stage; suffix names the gate's concern.
2. **Predicate set** — the verifier predicates the gate evaluates, by reference (e.g., D3.2 predicates 1–5, D3.3 P1–P3).
3. **Firing trigger** — pre-flight (before stage work), at-write (just before manifest seal), or post-seal (informational, after the manifest is written).
4. **Halt card** — the §halt-message a failure surfaces. A single gate may surface one of several halt cards depending on which predicate failed (e.g., `spec.pyramid-shape` surfaces `§pyramid-shape-violation` or `§pyramid-tag-invalid`); D3.4 specifies the mapping.

Gates are deterministic command hooks per D2.1 v2's "Deterministic command hooks default; agent hooks reserved for genuine LLM judgment" framing. The cascade's single LLM-judgment-shaped predicate — the four-hat objection-coverage check on `SubagentStop` per the carry-forward thread — is realized as deterministic Python (`.claude/hooks/four-hat-objection-coverage.py`) per the Child 0001-C apply-time disposition (option (b) of `child_C_hooks_and_settings_authoring_notes.md` §Surfaced item #4). The predicate's *shape* is LLM-judgment (objection coverage across hats); the *realization* is a command-type hook that re-reads the four hat transcripts deterministically. D3.4 does not introduce additional LLM-judgment-shaped predicates; the four-hat check is the sole instance.

## Per-stage gate inventory

Six stages with formal gates (`/specify`, `/plan`, `/build`, `/wrap`, `/verify`, `/retro`) plus the `/onboard` and `/review` boundary stages. Gates listed in firing order; the order is deterministic and not founder-configurable in v0.2.

### `/onboard`

| Gate | Trigger | Predicate set | Halt card on failure |
|---|---|---|---|
| `onboard.linear-projects` | at-write | All six Linear projects exist; Status doc created; product label namespace registered. (D2.1 v2 `/onboard` row.) | §onboard-linear-init-failed |
| `onboard.config-write` | at-write | `docs/.solo-config.json` written; parses; contains `marker`. | §onboard-config-write-failed |

`/onboard` is structurally simple; D3.4 names its gates for completeness but adds nothing beyond D2.1 v2.

### `/specify`

| Gate | Trigger | Predicate set | Halt card on failure |
|---|---|---|---|
| `spec.provenance` | pre-flight | Upstream-chain check on `--continue` / `--unseal`; manifest sha integrity per D2.1 v2 §Caller-side verification step 5. | §provenance-chain-broken |
| `spec.ac-coverage` | at-seal | Every AC has at least one named test in `failing_test_seed[]`. (D2.1 v2 `/specify` row.) | §incomplete-failing-test-seed |
| `spec.pyramid-shape` | at-seal | D3.2 predicates 1–7: shape strategy ≡ decomposition strategy; catalog match; required tags present; forbidden tags absent; tag in enum; refactor-spike empty seed; hybrid null shape. | §pyramid-shape-violation \| §pyramid-tag-invalid |
| `spec.strategy-evidence` | at-seal | D3.3 seal-time predicates: `artifact_path` shape per strategy (PNG / fixed transcript path / capability-type extension); for refactor-spike: config present, capture command exits zero, pass-set non-empty, `invariance_artifact` populated. | §pyramid-shape-violation/artifact-path-invalid \| §invariance-config-missing \| §invariance-pass-set-empty |
| `spec.strategy-annotation` | at-seal | D3.1: strategy step-1 annotation "proposed by /specify; founder to confirm" is resolved (the founder explicitly accepted or revised the proposal before seal). | §strategy-annotation-unresolved |

Firing order is fixed: provenance → ac-coverage → pyramid-shape → strategy-evidence → strategy-annotation. Rationale: provenance must hold before any other check is meaningful; AC coverage is the most upstream content predicate; pyramid-shape and strategy-evidence build on the seed AC coverage shapes; strategy-annotation is last because it depends on the strategy being settled across the prior gates.

All gates evaluate before the halt card is composed; a `spec.ac-coverage` failure does not short-circuit `spec.pyramid-shape` evaluation. Rationale: the founder benefits from seeing every issue in one pass.

### `/review` (four-hat coordinator)

| Gate | Trigger | Predicate set | Halt card on failure |
|---|---|---|---|
| `review.provenance` | pre-flight | Manifest chain to `/specify`'s seal. | §provenance-chain-broken |
| `review.four-hat-objection-coverage` | at-write (SubagentStop hook) | Per-hat subagent transcripts each contain priming text + structured objections + concluding seal line; `unresolved_count == 0` after merge. (D2.1 v2 `/review` row.) | §four-hat-incomplete \| §four-hat-objections-unresolved |
| `review.ac-list-seal` | at-write | `seal_sha256` recomputes against the spec's current AC list. | §four-hat-ac-list-drift |

The cascade's single LLM-judgment-shaped predicate lives inside `review.four-hat-objection-coverage`. It is realized as a deterministic command-type Python hook on `SubagentStop` per Child 0001-C apply-time disposition (not an `agent`-type subagent spawn). Per D2.1 v2, the parent writes the subagent manifest from an independently re-read transcript; the gate's predicate is the parent's recompute, not the subagent's self-report.

### `/plan`

| Gate | Trigger | Predicate set | Halt card on failure |
|---|---|---|---|
| `plan.provenance` | pre-flight | Manifest chain to `/review` (or to `/specify` when `/review` is skipped); `ac_list_sha256` recomputes against `four_hat_seal_sha256`. | §provenance-chain-broken \| §ac-list-drift |
| `plan.decomposition-shape` | at-write | D3.1: per-child decomposition entries valid; per-child strategy field populated; non-hybrid parent's children inherit parent strategy unless an override finding flips them; hybrid parent's children carry explicit non-inherited strategies. | §hybrid-without-child-overrides \| §plan-decomposition-invalid |
| `plan.child-inheritance` | at-write | Per-child `failing_test_seed[]` is a strict subset of parent's (existing /plan-SKILL contract); per-child `pyramid_shape` is inherited from parent or overridden cleanly per D3.2; per-child `artifact_path` / `artifact_type` / `invariance_artifact` fields propagate per D3.3. | §child-seed-not-subset \| §child-shape-inheritance-broken |

Firing order: provenance → decomposition-shape → child-inheritance.

### `/update-linear`

D2.1 v2 specifies this stage; D3.4 names its single gate for completeness:

| Gate | Trigger | Predicate set | Halt card on failure |
|---|---|---|---|
| `update-linear.diff-applied` | at-write | Each ticket's current Linear state matches `diff_sha256`; Linear-sync sanity check passes per D2.1 v2 §Linear-sync. | §linear-state-inconsistent |

### `/build`

| Gate | Trigger | Predicate set | Halt card on failure |
|---|---|---|---|
| `build.provenance` | pre-flight | Manifest chain to `/plan`'s child decomposition; `pyramid_shape` and per-entry `tag` from the spec markdown match the sealed manifest (no post-seal drift). | §provenance-chain-broken \| §pyramid-tampering-detected |
| `build.test-execution` | per-iteration (Ralph loop) | Tests in `failing_test_seed[]` run; outcomes captured to `backpressure_log`; first-FAIL hash detects drift per D2.1 v2. | §build-test-drift |
| `build.finalize` | at-write | `fix_plan_unchecked_count == 0`; every test in `failing_test_seed_status[]` recomputes to `passing`; commit exists in git; lock releases match acquisitions per D2.1 v2 `/build` finalize row. | §build-finalize-incomplete |

The build gate set is unchanged from D2.1 v2 + D3.2 in substance; D3.4 names them for `solo-verify` parity and `/retro` reporting.

### `/wrap`

| Gate | Trigger | Predicate set | Halt card on failure |
|---|---|---|---|
| `wrap.provenance` | pre-flight | Manifest chain to `/build` finalize. | §provenance-chain-broken |
| `wrap.product-docs-mirrored` | at-write | Filesystem `docs/product/*.md` sha matches Linear doc sha; per-resource lock acquisitions match releases per D2.1 v2 `/wrap` row. | §product-doc-mirror-drift \| §wrap-lock-imbalance |
| `wrap.label-transition` | at-write | Linear ticket label is `scope:built`; Linear ticket status is `Done`; Linear-sync sanity passes. | §wrap-label-transition-failed |

Firing order: provenance → product-docs-mirrored → label-transition. Label transition is last because rolling back a Linear label change is more expensive than rolling back a filesystem write.

### `/verify`

The milestone-level stage where D3.3's perceptual and invariance gates fire. The structure is unique to `/verify`: the milestone-level outer gate iterates children and dispatches to per-strategy child gates.

| Gate | Trigger | Predicate set | Halt card on failure |
|---|---|---|---|
| `verify.provenance` | pre-flight (milestone) | Manifest chains to every child's `/wrap`; each child manifest readable. | §provenance-chain-broken |
| `verify.child-completion` | pre-flight (milestone) | All children of the milestone have `scope:built` in Linear and a complete `/wrap` manifest. (D2.1 v2 `/verify` row.) | §verify-child-not-built |
| `verify.perceptual-evidence` | per-child (dispatched) | Walking-skeleton / api-boundary / capability-cluster children: D3.3 P1–P3 (plus P4 for api-boundary). | §perceptual-evidence-missing |
| `verify.invariance` | per-child (dispatched) | Refactor-spike children: D3.3 P5–P9. | §invariance-pass-set-regression \| §invariance-config-missing \| §invariance-seal-tampering \| §invariance-config-changed |
| `verify.milestone-aggregation` | at-write (milestone) | Every child evaluated; per-child outcomes recorded to `children_gate_outcomes[]`; no per-child gate halted. | §verify-milestone-aggregation-failed |

The per-strategy dispatch matrix is the next section.

### `/retro`

No hard gates. `/retro` is informational and produces findings, not predicate evaluations.

| Gate | Trigger | Predicate set | Halt card on failure |
|---|---|---|---|
| `retro.doc-sealed` | at-write | Linear retro doc exists with a sealed sha; Status doc lessons-line updated. (D2.1 v2 `/retro` row.) | §retro-doc-unsealed |

## `/verify` gate dispatch by strategy

The `verify.perceptual-evidence` and `verify.invariance` gates are mutually exclusive per child: a child carries exactly one strategy, and that strategy selects exactly one of the two gates. The dispatch table:

| Child strategy | Gate dispatched | Predicates evaluated |
|---|---|---|
| `walking-skeleton` | `verify.perceptual-evidence` | P1 (artifact present), P2 (regeneration zero-exit), P3 (byte-stability) for each `[perceptual]` test in the child's `failing_test_seed[]`. Typically 1–3 perceptual tests per child. |
| `api-boundary` | `verify.perceptual-evidence` | P1, P2, P3, P4 (transcript-shape) for the single integration-transcript test. Exactly one `[perceptual]` test per child by D3.3 contract. |
| `capability-cluster` | `verify.perceptual-evidence` | P1, P2, P3 for each `[perceptual]` test. Multiple perceptual tests per child are common (one per artifact in the capability's output set). |
| `refactor-spike` | `verify.invariance` | P5–P9: pass-set file present, sha integrity, command integrity, re-capture, set-membership comparison. |
| `hybrid` | recursive | Hybrid parents have no parent-level child entry; per-child dispatch uses each child's own strategy. |

### Dispatch sequence at `/verify`

The milestone-level `/verify` runs `verify.provenance` → `verify.child-completion`, then iterates `children[]` from the parent's `/plan` manifest:

1. Read each child's `/wrap` manifest.
2. Read each child's `/specify` manifest (chained via `input_provenance`).
3. From the `/specify` manifest's `outputs.decomposition_strategy`, dispatch to the matching gate (`verify.perceptual-evidence` or `verify.invariance`).
4. Evaluate the gate's predicates against re-read evidence (filesystem artifacts; re-run tests; re-run pass-set capture).
5. Record the per-child outcome to a running `children_gate_outcomes[]` list.

After all children are evaluated, `verify.milestone-aggregation` runs:

6. If any child's gate halted, surface a milestone halt card (next section) and write no `/verify` manifest.
7. If all children passed, seal the `/verify` manifest with `children_gate_outcomes[]` populated.

### Per-strategy gate-run cost notes

- **Walking-skeleton, capability-cluster:** P1 is cheap (filesystem stat); P2 requires re-running the perceptual test (browser launch, render, screenshot); P3 is cheap (byte diff). The bottleneck is P2's test runtime, dominated by browser startup. Typical: 5–30 seconds per perceptual test.
- **Api-boundary:** P1, P3, P4 are cheap; P2 requires re-running the integration test, which exercises the API surface. Typical: 1–10 seconds.
- **Refactor-spike:** P5–P7 are cheap (file stat + sha compare). P8 re-runs the configured pass-set capture command — full test suite execution. This is the most expensive `/verify` gate. Typical: 30 seconds – many minutes depending on codebase size. P9 is cheap (set comparison).

The cost analysis informs the deferred `--trust-build` flag (D3.3 open question 2): if `/verify` milestone runtime becomes the cascade's bottleneck, v0.2.x may allow `/verify` to read `/build`'s test-output manifest instead of re-running for P2 and P8. v0.2 always re-runs. The trust-model principle ("don't trust, verify") wins at v0.2; cost pragmatism may win at v0.2.x.

## Multi-failure aggregation

### Within a gate

A gate evaluates all its predicates and reports every failure. The gate's halt card surfaces:

- A primary halt code (one of the gate's §halt-messages). Selection rule: the **earliest-firing predicate's halt-code** is primary. E.g., a `spec.pyramid-shape` failure with both `tag-invalid` (predicate 5) and `missing-required` (predicate 3) reports `§pyramid-shape-violation/missing-required` as primary because predicate 3 fires before predicate 5.
- Every other failing predicate listed in the diagnostic context, with sub-cases.
- A single recommendation line drawn from the primary halt's recommendation.

### Across gates at a stage

When multiple gates at one stage halt (e.g., both `spec.ac-coverage` and `spec.pyramid-shape` at `/specify` seal), the halt card aggregates:

- A primary gate (the most-upstream halted gate per the stage's firing order).
- Every other halted gate listed under "Other gates that halted at this stage:".
- A single recommendation line drawn from the primary gate's halt. Rationale per D3.2: the primary gate's recommendation typically resolves the others, because the gates are ordered most-upstream-first and upstream resolutions cascade.

Example: at `/specify` seal, both `spec.ac-coverage` (an AC has no test) and `spec.pyramid-shape` (the missing test would have been required-`smoke`) fail simultaneously. The card:

```
HALT at /specify seal for SOL-117

Primary: §incomplete-failing-test-seed
  AC-3 has no named test in failing_test_seed[].

Other gates that halted at this stage:
  spec.pyramid-shape: §pyramid-shape-violation/missing-required
    pyramid_shape requires `smoke`; no [smoke]-tagged entry in the seed.

Recommendation:
  /specify SOL-117 --continue
  Add a named test covering AC-3. Tag it `[smoke]` to also satisfy the
  pyramid shape; both halts clear together.

Diagnostic context:
  Strategy: walking-skeleton
  Required pyramid tags: smoke, perceptual
  Tags in current seed: perceptual
  AC entries: AC-1 (covered: test_login_form_mounts), AC-2 (covered:
    test_login_redirect_screenshot), AC-3 (covered: <none>)
```

### Across children at `/verify`

When multiple children of a milestone halt at `/verify`, each child's halt is reported separately in the milestone halt card. There is no precedence selection across children — each child stands on its own. The milestone aggregation halt is:

```
HALT at /verify for milestone M-23

Children that halted at /verify:
  SOL-117 (walking-skeleton):
    §perceptual-evidence-missing/regeneration-failed
    test_login_redirect_screenshot exited non-zero at /verify re-run.

  SOL-122 (refactor-spike):
    §invariance-pass-set-regression
    3 tests in pass-set-at-seal.txt are missing from pass-set-at-verify.txt:
      - tests/billing/test_invoice_tax_calc.py::test_eu_vat_round_half_up
      - tests/billing/test_invoice_tax_calc.py::test_vat_exempt_clients
      - tests/billing/test_invoice_layout.py::test_pdf_a4_margins

Children that passed:
  SOL-118, SOL-119, SOL-120, SOL-121, SOL-123, SOL-124

Recommendation per child:
  SOL-117: /build SOL-117 to fix test_login_redirect_screenshot;
    once green, /verify M-23 retries.
  SOL-122: diff pass-set-at-seal.txt and pass-set-at-verify.txt; restore
    regressed tests or /specify SOL-122 --unseal if the regression is
    intentional behavior change.

Diagnostic context:
  Milestone: M-23
  Children evaluated: 8
  Children passed: 6
  Children halted: 2
  See child manifests and halt diagnostics under:
    .cascade/halt/SOL-117-verify.txt
    .cascade/halt/SOL-122-verify.txt
```

This is the canonical multi-child halt-card shape; `/verify`'s `solo-verify` parity emits the same structure.

## Manifest schema additions

### `/verify` outputs gains `children_gate_outcomes[]`

```json
"outputs": {
  "milestone_id": "M-23",
  "all_children_completed": true,
  "journeys_doc_post_ship_sha256": "…",
  "children_gate_outcomes": [
    {
      "child_id": "SOL-117",
      "strategy": "walking-skeleton",
      "gate": "verify.perceptual-evidence",
      "status": "passed",
      "predicates_evaluated": ["P1", "P2", "P3"],
      "evidence_paths": ["docs/specs/0042-login/perceptual/post-login.png"],
      "evaluated_at": "2026-05-19T14:23:11Z"
    },
    {
      "child_id": "SOL-122",
      "strategy": "refactor-spike",
      "gate": "verify.invariance",
      "status": "passed",
      "predicates_evaluated": ["P5", "P6", "P7", "P8", "P9"],
      "evidence_paths": [
        "docs/specs/0048-billing-cleanup/invariance/pass-set-at-seal.txt"
      ],
      "evaluated_at": "2026-05-19T14:25:47Z",
      "seal_pass_set_count": 247,
      "verify_pass_set_count": 252
    }
  ]
}
```

Schema rules:

- `children_gate_outcomes[]` is present on every successfully-sealed `/verify` manifest.
- Each entry corresponds to one child and one gate.
- `status` is `"passed"` only when present on a sealed manifest (a halted `/verify` writes no manifest per D2.1 v2; failures are surfaced in the halt diagnostic, not on the manifest).
- `predicates_evaluated[]` lists the predicate IDs that fired (D3.3 P1–P9 by reference; D3.2 predicates by ordinal).
- `evidence_paths[]` lists filesystem paths the gate re-read; `/retro` can re-walk these.
- `evaluated_at` is wall-clock timestamp; used by `/retro` for run-time trend reporting.
- For refactor-spike children, `seal_pass_set_count` and `verify_pass_set_count` are included for cheap delta reporting at `/retro`.

The field is additive to D2.1 v2 + D3.2 + D3.3. Manifests sealed under earlier schemas have no `children_gate_outcomes[]` and are not retroactively populated.

### Other stages

No other stage gains a similar field. Single-child stages (`/specify` through `/wrap`) implicitly record gate outcomes via manifest existence per D2.1 v2's pattern. The asymmetry is intentional: `/verify` is the only milestone-level stage with per-child fan-out, and only fan-out justifies explicit outcome recording.

If `/retro` needs per-stage gate-trace data for non-`/verify` stages in v0.2.x or v0.3, the additive pattern is the same: a `gates_evaluated[]` field on the stage's outputs block. v0.2 ships only the `/verify` slot.

## `/verify` mechanics — full sequence

Building on D3.3's predicate texts, the complete `/verify` mechanics for v0.2:

1. **Pre-flight: `verify.provenance`.** Walk every child's `/wrap` → `/build` → … → `/specify` manifest chain. Halt on any chain break or sha mismatch.
2. **Pre-flight: `verify.child-completion`.** For each child in the parent's `/plan` `child_tickets[]`, confirm Linear state `scope:built` AND Linear `Done` AND `/wrap` manifest exists. Halt on any incomplete child with `§verify-child-not-built`.
3. **Per-child dispatch.** For each child:
   a. Read the child's `/specify` manifest. Extract `decomposition_strategy`.
   b. If `walking-skeleton` / `capability-cluster`: for every `[perceptual]` entry in `failing_test_seed[]`, evaluate P1, P2, P3.
   c. If `api-boundary`: for the single `[perceptual]` entry, evaluate P1, P2, P3, P4.
   d. If `refactor-spike`: evaluate P5, P6, P7, P8, P9 against `outputs.invariance_artifact`.
   e. If `hybrid`: hybrid parents have no parent-level child entry. Hybrid means the child *is* the parent of further children; recurse into the child's children (D3.4 supports one level of hybrid nesting in v0.2; deeper nesting is a v0.2.x edge case).
   f. Record outcome to in-memory `children_gate_outcomes[]`. If gate halted, record the halt-code; the loop continues evaluating remaining children (so the halt card surfaces all failures).
4. **`verify.milestone-aggregation`.** If `children_gate_outcomes[]` contains any halted entry, do not seal the `/verify` manifest. Compose the multi-child halt card per "Across children at /verify" above; write per-child halt diagnostics to `.cascade/halt/<child-ticket>-verify.txt`; release any held resource locks; remove `/verify` from `active_stages[]`; emit the halt card.
5. **Seal.** If all children passed, seal the `/verify` manifest with `outputs.children_gate_outcomes[]` populated and `outputs.all_children_completed = true`. Update the milestone's Linear state per D2.1 v2 `/verify` row.

Step 3 is parallelizable per child within `/verify`'s execution. v0.2 does not require parallelism; v0.2.x may add a `--parallel <N>` flag if milestone runtimes are problematic. Per-child evaluation is independent (no shared state across child evaluations besides the milestone's `children_gate_outcomes[]` accumulator, which is written once at the end).

## `solo-verify` CLI surface

The CLI parity contract from the carry-forward thread: every gate has a `solo-verify` invocation. D3.4 enumerates the full surface for v0.2. (Build/distribution is D4.x.)

### Per-stage invocations

```
solo-verify onboard <product>          # evaluates onboard.linear-projects + onboard.config-write
solo-verify specify <ticket>           # evaluates spec.* gates against the current spec file
solo-verify review <ticket>            # evaluates review.* gates
solo-verify plan <ticket>              # evaluates plan.* gates
solo-verify update-linear <ticket>     # evaluates update-linear.diff-applied
solo-verify build <ticket>             # evaluates build.* gates against the latest build state
solo-verify wrap <ticket>              # evaluates wrap.* gates
solo-verify verify <milestone>         # evaluates verify.* gates including per-child dispatch
solo-verify retro <milestone>          # evaluates retro.doc-sealed
```

Each invocation:

- Reads the stage's expected upstream manifest from `.cascade/manifests/<ticket>-<upstream>.json`.
- Runs the same predicate logic the cascade hook would run.
- Emits a passed/halted result with the same halt-card format the cascade would emit.
- Exits zero on pass, non-zero on halt.

### Per-gate invocations

```
solo-verify <stage> <ticket> --gate <gate-name>
```

Evaluates a single named gate; useful for debugging which predicate is failing. Example:

```
solo-verify verify M-23 --gate verify.invariance
```

evaluates only the invariance gate for refactor-spike children of M-23, skipping perceptual-evidence and provenance.

### Documentation invocations

```
solo-verify --list-gates                                  # all gates across all stages
solo-verify --list-gates <stage>                          # gates for one stage
solo-verify --explain <stage>.<gate-name>                 # gate's predicate text, halt codes, recovery
```

`--explain` outputs the same content the design doc carries for the gate's predicate set and halt cards. Single canonical source of truth: D3.4's tables. v0.2.x may move this content to a versioned `gates.json` file that both the cascade and `solo-verify --explain` read; v0.2 inlines.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | All gates evaluated, all passed. |
| 1 | One or more gates halted (standard halt). |
| 2 | Stage not found or gate name unknown. |
| 3 | Manifest chain broken (provenance halt). |
| 4 | Filesystem or Linear inconsistency that prevents evaluation (e.g., `.cascade/manifests/` missing entirely). |

Exit code 3 is split from exit code 1 because provenance halts indicate cascade-level state corruption and require different recovery (`--reconcile` per D2.1 v2's pattern); standard halts are typically recoverable via stage retry.

## Halt conditions

D3.4 introduces three new halt conditions to `docs/templates/halt-messages.md`. All others are referenced from D2.1 v2, D3.1, D3.2, or D3.3.

### §strategy-annotation-unresolved

- **When:** `/specify` seal detected that the strategy field at `## Decomposition strategy` still carries the step-1 annotation "proposed by /specify; founder to confirm" — the founder did not explicitly accept or revise the proposal before seal.
- **Recommendation:** Re-run `/specify <ticket> --continue`. At step 5, either accept the proposed strategy verbatim (which clears the annotation) or revise it to a different strategy.
- **Rationale:** Per D3.1, the strategy is the populator for the pyramid shape, the perceptual evidence shape, and the verify-time gate. A strategy that the founder did not affirmatively confirm is not load-bearing; sealing with the annotation in place would let a /specify default cascade downstream unchallenged.
- **Alternatives:** None — the annotation must clear before seal.
- **Diagnostic context:** Verbatim contents of the `## Decomposition strategy` section; the annotation line being detected; the spec markdown's `spec_path`.

### §verify-milestone-aggregation-failed

- **When:** `/verify`'s milestone-aggregation gate found one or more per-child gates halted. This is not a separate failure mode; it is the aggregation halt card itself, surfaced as a milestone-level §halt for `/retro` and human readability.
- **Recommendation:** Address each per-child halt independently per its sub-card's recommendation; re-run `/verify <milestone>` once children are fixed.
- **Rationale:** A milestone cannot ship while any child gate has halted. Per-child halts have their own recovery paths; the milestone halt is a roll-up, not an additional defect.
- **Alternatives:** If a child's halt is unrecoverable in the milestone's timeframe, `/plan <milestone> --drop-child <ticket>` removes the child from the milestone (D4.x decides whether this is supported in v0.2; D3.4 names the gap).
- **Diagnostic context:** List of halted children with their sub-cards; list of passed children; total counts; milestone ID; paths to per-child halt diagnostics.

### §provenance-chain-broken

A consolidation of D2.1 v2's manifest-chain halt patterns under a single named halt code, for cleaner `solo-verify` reporting. The underlying predicate is unchanged from D2.1 v2 §Caller-side verification step 5: "Verify the manifest's named parent matches what `cascade:run-state` says the parent should be. Halt on chain break."

- **When:** Any stage's `<stage>.provenance` gate found a manifest chain break: missing manifest file, sha mismatch, or named-parent mismatch.
- **Recommendation:** `--reconcile` per D2.1 v2's chain-recovery pattern; manual diff of `.cascade/manifests/` against `cascade:run-state.active_stages[]` to identify the break point.
- **Rationale:** A broken provenance chain means the cascade cannot trust any downstream evidence; halting prevents tainted artifacts from propagating.
- **Alternatives:** None — chain integrity must be restored before downstream stages can resume.
- **Diagnostic context:** Stage attempting to read; manifest path expected; manifest path found (or absent); sha expected; sha found; parent name expected; parent name found.

## Carry-forward and forward-references

- **Phase 3 closes with D3.4.** The strategy catalog (D3.1), the test-pyramid declaration (D3.2), the perceptual and invariance predicates (D3.3), and the gate composition layer (D3.4) jointly resolve F-3 by giving the cascade per-stage gates that compose to a verifiable end-to-end quality topology. Phase 4 begins with cleanup items deferred from Phases 1–3.
- **`solo-verify` build and distribution lives in D4.x.** D3.4 specifies the CLI surface (commands, flags, exit codes); D4.x decides single-binary vs Python tree vs Bun. The decision cannot drift past Phase 4 per the carry-forward thread.
- **`/plan --drop-child <ticket>`** is named here as a gap but not specified. If a milestone has a child whose halt is unrecoverable in the milestone's timeframe, the founder needs a sanctioned escape. v0.2 does not ship the operation; founders manually delete the child ticket and re-run `/plan`. D4.x may formalize.
- **`--trust-build` at `/verify`** (skip P2 and P8 re-runs by reading `/build`'s test-output manifest) is parked for v0.2.x. v0.2 always re-runs perceptual tests and pass-set captures at `/verify` per D3.3's open question 2 and D3.4's cost analysis.
- **Per-stage `gates_evaluated[]`** for non-`/verify` stages is parked for v0.2.x. v0.2 records gate outcomes only at `/verify` (where fan-out justifies the field); other stages rely on manifest-existence-as-pass per D2.1 v2.
- **Hybrid nesting beyond one level** is a v0.2.x edge case. D3.4 supports a hybrid parent with refactor-spike + walking-skeleton + capability-cluster children; a hybrid parent of hybrid children is unspecified. Real-world milestones rarely require deeper nesting; v0.2 declares the constraint and halts §hybrid-nesting-too-deep if encountered.
- **Mutation-testing parity as an alternative invariance predicate** stays parked per D3.0 and D3.3. The 2026 tooling is mature; the install-and-CI surface is non-trivial; v0.2 ships pass-set parity.
- **Versioned `gates.json` for `solo-verify --explain` content** is a v0.2.x consideration. v0.2 inlines the content per stage; a structured catalog file would let the cascade and the CLI share a single source of truth. The trade is a small additional file in the repo template vs duplication risk between the docs and the CLI.

## Open questions for Phase 4

1. **D4.0 — solo-verify build/distribution.** Named in the carry-forward thread. Single binary (Go, Rust, Bun's compiled output)? Python script tree with a thin shell wrapper? Bun script? Decision drives v0.2's distribution shape; the design doc for it should be the first Phase 4 deliverable.
2. **D4.x — onboard product-level default strategy.** D3.1 left this optional; D3.3's open question 1 (renumbered as D3.4 open question, also surfaces here). If `/onboard` should require a product-level default strategy that flows through `/specify` step 1's proposal seed, the `/onboard` skill needs a strategy question added. Batches with D4.x.
3. **D4.x — `/plan --drop-child` operation.** Whether the cascade supports formally dropping a child from a milestone, or whether the founder is expected to handle this manually. Named above; D4.x decides.
4. **D4.x — `--reconcile` formalization.** Referenced across D2.1 v2 and D3.4 as the chain-recovery escape hatch but not fully specified anywhere. D4.x should give it its own design doc.
5. **D4.x — `pyramid_catalog_version` and structured `gates.json`.** Two related v0.2.x questions: should the pyramid catalog (D3.2 §4) and the gate catalog (D3.4 §solo-verify) live in versioned JSON files in the repo template, or stay inlined in design docs? Decision touches both repo-template shape and CLI implementation.
6. **D4.x — telemetry on gate outcomes.** `children_gate_outcomes[]` lets `/retro` read per-milestone gate-pass-rates, perceptual-coverage breadth, and invariance-stability trends. v0.2 surfaces this in `/retro` doc generation only; v0.2.x or v0.3 may add a `solo-stats` query layer. Not load-bearing for Phase 4 launch.
7. **D4.x — D3.2 §3 capability-cluster `[smoke]` promotion UX.** D3.2 named the rule (a `[smoke]` test on a capability-cluster spec is a /specify defect; the recommendation is to promote the concern to the underlying walking-skeleton spec). Whether `/specify` supports "promote this test concern to a different spec" as an operation, or stays manual. Bundles with D4.x cleanup.
