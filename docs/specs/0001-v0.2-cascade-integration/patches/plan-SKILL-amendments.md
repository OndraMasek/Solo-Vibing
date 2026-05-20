# `.claude/skills/plan/SKILL.md` — v0.2 amendments

**Status:** Patch-ready amendment block. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing` which reconciles against v0.1 byte-for-byte before applying.

**Scope:** add gate-evaluation logic for three `plan.*` gates (pre-flight, decomposer-write, and decomposition.md-seal) and extend the existing decomposer-critique flow with D3.1's decomposition-override finding class. The skill's frontmatter, the `/Chains` block (sealed in `child_B_chains_sections.md` Pattern C Group E intermediate), the decomposer-invoke step itself, and the existing manifest-write step carry forward from v0.1 unchanged at the substantive level.

**v0.1 reconciliation pattern:** the executing session reads v0.1's `.claude/skills/plan/SKILL.md` and substitutes by purpose ("the pre-flight step" / "the decomposer-write step" / "the manifest-seal step") rather than by step number, since v0.1's step numbering for `/plan` is not pinned in any binding spec. If v0.1 already evaluates a subset of these gates under different names, prefer this amendment's naming for `solo-verify` parity and leave a TODO marker in the executing-session commit message.

---

## Naming reconciliation note

D3.4 §Per-stage gate inventory `/plan` row names the three gates `plan.provenance`, `plan.decomposition-shape`, `plan.child-inheritance`. The parent `spec.md` AC-7 and `decomposition.md` Child 0001-B name them `plan.provenance`, `plan.children-have-strategies-for-hybrid`, `plan.decomposition-doc-sealed`. Same three gates by intent, divergent names for two (`decomposition-shape` ↔ `children-have-strategies-for-hybrid`; `child-inheritance` ↔ `decomposition-doc-sealed`).

The amendment below uses **D3.4's names** (`plan.provenance`, `plan.decomposition-shape`, `plan.child-inheritance`) because D3.4 is the binding gate-definition spec, and because D3.4's names cover broader predicate sets than the AC-7 names do — D3.4's `plan.decomposition-shape` includes both the hybrid-without-child-overrides predicate AND the per-child-strategy-populated predicate AND the parent-strategy-inheritance predicate, whereas AC-7's `plan.children-have-strategies-for-hybrid` reads narrowly as only the hybrid case. The narrower names would either need to be widened (returning to D3.4's names) or a new gate added per missing predicate. Cleanest: use D3.4's names; amend `spec.md` AC-7 and `decomposition.md` Child 0001-B as a one-line follow-on. See authoring notes §Surfaced item #1.

---

## Decomposer reading — D3.1 strategy and override-finding flow

The decomposer subagent (`.claude/agents/decomposer.md`) reads `## Decomposition strategy` from the parent spec at invocation, alongside its existing reads (problem statement, AC list, failing-test seed, scope boundary). This is the D3.1 amendment to the decomposer's input set; the strategy value flows through to each per-child block in `decomposition.md` and is referenced by the gate evaluators below.

### Override-finding flow (extends v0.1 critique pattern)

V0.1's `/plan` review pass already supports an `incorporate / defer / reject` triage of decomposer-emitted critique findings. D3.1 adds a new finding class — `decomposition-override` — without changing the triage mechanism:

```text
decomposer-emitted finding shape (per D3.1 §`/plan`'s decomposer reading):

  - **decomposition-override** [child: K] @ {locus in parent spec}:
    this child reads as {strategy}, not parent's {strategy}.
    Rationale: {1-2 sentences citing the AC or scope text that drove the call}.
```

When the founder triages such a finding:

- **`incorporate`** — write the child's block in `decomposition.md` with an explicit `Strategy:` field carrying the override value:

  ```markdown
  ### K. <verb-noun title>

  - Classification: vertical | horizontal
  - Strategy: <override-value>
  - Rationale: <verbatim from the decomposition-override finding>
  - Description: ...
  - AC: ...
  - Failing-test seed: ...
  - Blockers: ...
  ```

- **`defer`** — write the child's block with `Strategy: inherited` and append the override finding text under the child's block as a margin note prefixed with `<!-- deferred: decomposition-override -->`. The founder is signalling that the override is a real signal but not actionable this iteration; the next `/plan` run can re-surface.

- **`reject`** — write the child's block with `Strategy: inherited` and append the rejected finding text as a margin note prefixed with `<!-- rejected: decomposition-override; rationale: <founder's text> -->`. The founder is signalling the override doesn't apply; future runs should not re-surface unless the spec changes.

For hybrid parents, every child MUST carry an explicit non-inherited `Strategy:` field. Children with `Strategy: inherited` under a hybrid parent fail the `plan.decomposition-shape` gate per §Gate 2 below.

For non-hybrid parents, children default to `Strategy: inherited` (meaning "use the parent's strategy") unless an override finding flips them via `incorporate`. The decomposer SHOULD emit a critique recommending parent re-seal as `hybrid` if three or more `decomposition-override` findings accumulate on a non-hybrid parent (per D3.1 §`/plan`'s decomposer reading); the founder retains authority to ignore the recommendation.

### Strategy carry-through to per-child manifests

When `/plan` writes per-child manifests (for heavyweight children) or per-child ticket descriptions (for lightweight children), each child's `outputs.decomposition_strategy` is the resolved per-child value:

```text
resolve_child_strategy(child_block, parent_strategy):
    if child_block.Strategy == "inherited":
        if parent_strategy == "hybrid":
            return "<UNDEFINED>"   # fails plan.decomposition-shape below
        else:
            return parent_strategy
    else:
        return child_block.Strategy   # explicit override value
```

The `<UNDEFINED>` return is the trigger for `plan.decomposition-shape` to halt `§hybrid-without-child-overrides` per §Gate 2.

---

## Gate evaluation

Three gates fire at `/plan`, in firing order per D3.4 §Per-stage gate inventory `/plan` row. All gates evaluate before any halt card is composed (per D3.4 §`/specify` aggregation rules, applied uniformly across stages).

```text
GATES_AT_PLAN = [
  "plan.provenance",          # pre-flight; chain integrity + ac_list_sha256 recompute
  "plan.decomposition-shape", # at-write; D3.1 hybrid-without-child-overrides + per-child strategy populated
  "plan.child-inheritance"    # at-write; seed strict-subset + pyramid_shape inheritance + artifact field propagation
]

for gate in GATES_AT_PLAN:
    evaluate gate predicates and record per-gate result
    # do NOT short-circuit; all gates evaluate

if any gate has at least one failing predicate:
    compose aggregate halt card per D3.4 §Aggregation rules
    do NOT write the manifest
    exit with halt
else:
    write manifest, including decomposition.md (heavyweight) or child-ticket-descriptions (lightweight)
    seal /plan
```

### Gate 1 — `plan.provenance` (pre-flight; chain integrity + AC-hash chain)

```text
read cascade:run-state from docs/.cascade/run-state.json

# Step 1: parent manifest path is /review's seal (or /specify's seal if /review skipped)
expected_parent_path ← cascade:run-state.last_completed_stage.postcondition_manifest_path
if expected_parent_path absent or path doesn't resolve to a file:
    FAIL with §provenance-chain-broken
    diagnostic: "expected parent manifest at <path>; absent"
    continue

# Step 2: recompute manifest sha
recomputed_sha ← sha256 of parent manifest with manifest_sha256 field zeroed
expected_sha   ← cascade:run-state.last_completed_stage.postcondition_manifest_sha256
if recomputed_sha != expected_sha:
    FAIL with §provenance-chain-broken
    diagnostic: f"parent manifest sha mismatch at {expected_parent_path}; expected {expected_sha[:12]}..., got {recomputed_sha[:12]}..."
    continue

# Step 3: AC-hash chain
parent_outputs ← parse parent manifest's outputs
if parent_outputs.stage == "/review":
    # /review's manifest carries four_hat_seal_sha256 chained from the spec's AC list
    spec_path        ← parent_outputs.spec_path
    current_ac_list  ← parse §Acceptance criteria from spec_path
    current_ac_sha   ← sha256 of canonicalized AC list
    sealed_ac_sha    ← parent_outputs.ac_list_sha256
    if current_ac_sha != sealed_ac_sha:
        FAIL with §ac-list-drift
        diagnostic: f"AC list at {spec_path} has changed since /review sealed; sealed sha {sealed_ac_sha[:12]}..., current sha {current_ac_sha[:12]}..."

elif parent_outputs.stage == "/specify":
    # /review was skipped; chain directly to /specify's seal
    spec_path        ← parent_outputs.spec_path
    current_ac_list  ← parse §Acceptance criteria from spec_path
    current_ac_sha   ← sha256 of canonicalized AC list
    sealed_ac_sha    ← parent_outputs.ac_list_sha256
    if current_ac_sha != sealed_ac_sha:
        FAIL with §ac-list-drift
        diagnostic: f"AC list at {spec_path} has changed since /specify sealed; sealed sha {sealed_ac_sha[:12]}..., current sha {current_ac_sha[:12]}..."
```

Halt codes: `§provenance-chain-broken`, `§ac-list-drift`. The first is the consolidated chain-recovery halt per Child A's halt-messages-append.md (exit code 3 per D3.4 §Exit codes); recovery is `--reconcile` or `--rerun=<stage>`. The second fires when the spec's AC list has been edited between an upstream seal and `/plan`'s read — recovery is `/specify --unseal` to re-seal against the current AC list.

### Gate 2 — `plan.decomposition-shape` (at-write; D3.1 hybrid + per-child strategy)

This gate evaluates the decomposition.md as the decomposer wrote it but before manifest seal. The decomposition.md is in memory at this point, not yet persisted; the gate inspects the in-memory write before commit.

```text
parent_strategy ← read parent spec's §Decomposition strategy value
children        ← parse decomposition.md's per-child blocks

# Predicate 1: per-child decomposition entries valid
for child in children:
    if child.title is empty or child.AC is empty or child.description is empty:
        FAIL with §plan-decomposition-invalid
        diagnostic: f"child K='{child.K}' has malformed block; title='{child.title}', AC='{child.AC}', description='{child.description}'"

# Predicate 2: per-child Strategy field populated
for child in children:
    if child.Strategy is absent:
        FAIL with §plan-decomposition-invalid
        diagnostic: f"child K='{child.K}' missing Strategy: field; must be 'inherited' (non-hybrid parent only) or an explicit value from the canonical enum"
        continue

    if child.Strategy not in {"inherited", "walking-skeleton", "api-boundary", "capability-cluster", "refactor-spike", "hybrid"}:
        FAIL with §plan-decomposition-invalid
        diagnostic: f"child K='{child.K}' Strategy: '{child.Strategy}' invalid; expected 'inherited' or one of {{walking-skeleton, api-boundary, capability-cluster, refactor-spike, hybrid}}"

# Predicate 3: hybrid parent → every child explicit
if parent_strategy == "hybrid":
    children_inheriting = [child for child in children if child.Strategy == "inherited"]
    if children_inheriting:
        FAIL with §hybrid-without-child-overrides
        diagnostic: list of (child.K, child path/block, current Strategy value verbatim)

# Predicate 4: hybrid nesting depth (one level cap per v0.2)
for child in children:
    resolved_strategy ← resolve_child_strategy(child, parent_strategy)
    if resolved_strategy == "hybrid":
        if child is heavyweight (carries its own decomposition.md):
            grandchildren ← parse child's decomposition.md
            for gc in grandchildren:
                gc_strategy ← resolve_child_strategy(gc, "hybrid")
                if gc_strategy == "hybrid":
                    FAIL with §hybrid-nesting-too-deep
                    diagnostic: f"hybrid nesting beyond one level detected at {child.K} > {gc.K}; v0.2 caps at one level per D3.4 §`/verify` dispatch"

# Predicate 5: non-hybrid parent with 3+ override-incorporations → decomposer-emitted critique
# (informational only — not a halt; recorded in decomposition.md margin notes)
if parent_strategy != "hybrid":
    overrides_incorporated = [child for child in children
                              if child.Strategy != "inherited" and child.Strategy != parent_strategy]
    if len(overrides_incorporated) >= 3:
        emit critique: "Three or more decomposition-override findings were incorporated under a non-hybrid parent (parent strategy = '{parent_strategy}'). Consider re-sealing the parent as 'hybrid' under /specify --unseal. v0.2 does not halt this; the recommendation is informational."
```

Halt codes: `§plan-decomposition-invalid`, `§hybrid-without-child-overrides`, `§hybrid-nesting-too-deep`. The second is in Child A's halt-messages-append.md (halt 14 of the appendage); the first and third are pre-existing v0.1 halts or land at apply-time if not yet present (verify against v0.1 `halt-messages.md` at executing-session time; if absent, the executing session adds a minimal card pointing at this gate's diagnostic).

### Gate 3 — `plan.child-inheritance` (at-write; seed subset + pyramid + artifact propagation)

This gate evaluates each child's failing-test seed against the parent's, the per-child pyramid_shape against the per-child strategy, and the propagation of `artifact_path` / `artifact_type` / `invariance_artifact` fields.

```text
parent_outputs    ← parse parent manifest's outputs (the upstream stage's outputs)
parent_seed       ← parent_outputs.failing_test_seed   # may be [] for hybrid or refactor-spike
parent_shape      ← parent_outputs.pyramid_shape       # may be null for hybrid

children          ← parse decomposition.md per-child blocks

for child in children:
    resolved_strategy ← resolve_child_strategy(child, parent_strategy)
    child_shape       ← PYRAMID_CATALOG[resolved_strategy]   # may be null for hybrid sub-children

    # Predicate 1: child seed is a strict subset of parent seed (existing /plan-SKILL contract)
    # — only when parent has a non-empty seed (walking-skeleton / api-boundary / capability-cluster parents)
    if parent_seed:
        child_seed_names ← {entry.name for entry in child.failing_test_seed}
        parent_seed_names ← {entry.name for entry in parent_seed}
        if not child_seed_names.issubset(parent_seed_names):
            extra ← child_seed_names - parent_seed_names
            FAIL with §child-seed-not-subset
            diagnostic: f"child K='{child.K}' seed contains tests not in parent seed: {sorted(extra)}; per existing /plan contract, child seeds must be strict subsets of parent seeds"

    # Predicate 2: per-child pyramid_shape consistent with resolved strategy
    if resolved_strategy != "hybrid" and child.pyramid_shape is not None:
        expected_shape ← PYRAMID_CATALOG[resolved_strategy]
        if (set(child.pyramid_shape.required_tags)  != set(expected_shape.required_tags) or
            set(child.pyramid_shape.optional_tags)  != set(expected_shape.optional_tags) or
            set(child.pyramid_shape.forbidden_tags) != set(expected_shape.forbidden_tags)):
            FAIL with §child-shape-inheritance-broken
            diagnostic: f"child K='{child.K}' resolved_strategy='{resolved_strategy}' but pyramid_shape doesn't match catalog; expected {expected_shape}, got {child.pyramid_shape}"

    # Predicate 3: artifact_path / artifact_type propagation for [perceptual] entries
    # — child's [perceptual] entries either carry their own (capability-cluster, founder-chosen)
    #   or inherit the parent's by name match
    for entry in child.failing_test_seed where entry.tag == "perceptual":
        if entry.artifact_path is absent:
            # may be inheritable from parent by name match
            parent_match ← lookup entry.name in parent_seed
            if parent_match and parent_match.tag == "perceptual" and parent_match.artifact_path:
                entry.artifact_path ← parent_match.artifact_path
                if resolved_strategy == "capability-cluster" and parent_match.artifact_type:
                    entry.artifact_type ← parent_match.artifact_type
            else:
                FAIL with §child-shape-inheritance-broken
                diagnostic: f"child K='{child.K}' [perceptual] entry '{entry.name}' missing artifact_path and not inheritable from parent"

    # Predicate 4: invariance_artifact propagation for refactor-spike children
    if resolved_strategy == "refactor-spike":
        # refactor-spike children inherit the parent's invariance_artifact if parent is also refactor-spike;
        # for hybrid parents with a refactor-spike child, the child re-captures at its own /specify seal
        if parent_strategy == "refactor-spike" and parent_outputs.invariance_artifact:
            child.invariance_artifact ← parent_outputs.invariance_artifact   # inherited
        else:
            # child must capture at its own /specify seal; not /plan's responsibility
            # /plan records the gap; child /specify re-runs §spec.strategy-evidence Part B
            pass
```

Halt codes: `§child-seed-not-subset`, `§child-shape-inheritance-broken`. These are pre-existing v0.1 halts or land at apply-time if not yet present (same reconciliation pattern as Gate 2).

---

## decomposition.md write (on all-gates-pass)

If every gate passes, write `decomposition.md` at `docs/specs/<NNNN>-<slug>/decomposition.md` per D2.1 v2 §`/plan` row and the heavyweight/lightweight per-child machinery from v0.1 `/plan` SKILL.md (unchanged). The amendment ensures every per-child block carries the new `Strategy:` field per the resolved value.

### Per-child block shape (heavyweight children)

```markdown
### K. <verb-noun title>

- Classification: vertical | horizontal
- Strategy: <inherited | walking-skeleton | api-boundary | capability-cluster | refactor-spike | hybrid>
- Description: ...
- AC: ...
- Failing-test seed: ...
- Blockers: ...
```

For children with `Strategy: inherited`, downstream stages (`/specify` if the child later re-specs, `/build`, `/wrap`, `/verify`) resolve to the parent strategy via `resolve_child_strategy()` semantics.

For children with `Strategy: <override-value>`, the override-rationale is written under the child's block as the `Rationale:` line per the incorporate-flow above.

### Per-child block shape (lightweight children)

Lightweight children live as Linear ticket descriptions, not as separate spec files. The decomposition.md still carries the block above; the ticket description carries the same fields in Linear's surface format. The `Strategy:` field appears in both places.

---

## Manifest write (on all-gates-pass + decomposition.md written)

Write the `/plan` manifest at `.cascade/manifests/<ticket>-plan.json` per D2.1 v2 §`/plan` row, extending to D3.1's strategy carry-through:

```json
{
  "stage": "/plan",
  "ticket": "<MARKER>-<N>",
  "plan_sealed_at": "<ISO-8601 timestamp>",
  "outputs": {
    "parent_ticket":       "<MARKER>-<N>",
    "child_tickets":       ["<MARKER>-<N+1>", "<MARKER>-<N+2>", ...],
    "total_children":      <count>,
    "dag_path":            "docs/specs/<NNNN>-<slug>/decomposition.md",
    "decomposition_strategy_parent": "<parent strategy>",
    "child_strategies":    [
      {"ticket": "<MARKER>-<N+1>", "resolved_strategy": "<value>", "inherited_or_override": "inherited" | "override"},
      ...
    ]
  },
  "input_provenance": {
    "parent_manifest_path":   "...",
    "parent_manifest_sha256": "...",
    "ac_list_sha256":         "..."
  },
  "manifest_sha256": "<recomputed-zero-self-field>"
}
```

The `child_strategies[]` array is a v0.2 addition over v0.1's `child_tickets[]`-only outputs; it gives `/build`, `/verify`, and `/retro` a flat per-child strategy roll-up without re-parsing decomposition.md. After write, update `cascade:run-state.json`'s `last_completed_stage` to point at this manifest path and sha.

---

## Cross-references

- **D3.1 §`/plan`'s decomposer reading** — the decomposition-override finding class and the incorporate/defer/reject flow, consumed in the §Decomposer reading section.
- **D3.1 §Halt conditions §hybrid-without-child-overrides** — the binding halt card for Gate 2 Predicate 3.
- **D3.2 §Downstream consumer touch-points `/plan`'s decomposer** — the child seed strict-subset contract that Gate 3 Predicate 1 enforces.
- **D3.3 §`/plan`'s decomposer copies artifact_path and artifact_type to children's manifests** — the inheritance contract that Gate 3 Predicate 3 enforces.
- **D3.4 §Per-stage gate inventory `/plan`** — the three gates' firing order and predicate references.
- **D3.4 §Aggregation rules** — all-gates-evaluate + single-card-aggregate semantics for the plan halt.
- **D3.4 §Halt conditions §hybrid-nesting-too-deep** — the v0.2 one-level cap on hybrid nesting, enforced by Gate 2 Predicate 4.
- **D2.1 v2 §`/plan` row** — the upstream manifest schema (`child_tickets[]`, `parent_ticket`, `total_children`, `dag_path`) and verifier-predicate baseline; D3.4's three gates layer on top.
- **D2.1 v2.1** — the chain integrity machinery Gate 1 evaluates (manifest sha + parent name + ac_list_sha256 recompute).
- **Child A `spec.md.template`** — the spec template `/plan`'s decomposer reads to find `## Decomposition strategy`; without that section present and resolved, Gate 2 cannot evaluate parent strategy.
- **Child A `halt-messages-append.md`** halts 12–14 — `§strategy-missing` (fires from `/specify` not `/plan`; `/plan`'s pre-flight inherits the spec sealed under valid §Decomposition strategy by chain construction), `§strategy-conflict-unresolved` (same), `§hybrid-without-child-overrides` (this card is the binding for Gate 2 Predicate 3).
- **`child_B_chains_sections.md`** Pattern C Group E intermediate — the `/Chains` block for `/plan` written in a prior session; this amendment's gates land BEFORE the `/Chains` block's Task-invoke-to-`/review`.
- **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-7** — this skill amendment satisfies AC-7 as authored, modulo the gate-name reconciliation surfaced as Item #1 in the authoring notes.
