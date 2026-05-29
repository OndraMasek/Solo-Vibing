---
name: plan
description: Decompose a sealed parent spec into child tickets with dependency graph and parallelization plan. Invokes the decomposer agent to draft children, then mints them as scope:sealed Linear tickets with blockedBy wiring, writes decomposition.md, transitions parent scope:specified → scope:planned, and Task-invokes /review. Internal cascade stage between /specify and /review — auto-fired by /specify via Task tool, not founder-invoked under the hidden-cascade model. Manual override `/plan <MARKER>-N` available for re-decomposition or debugging. Undecomposable parents halt back to /specify --unseal — no in-skill escape hatch.
---

# plan

Decompose specified parent into child tickets. Internal cascade stage. References rules: `naming.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`. Invokes agent: `decomposer`. Chains to skill via Task tool: `review` (on DONE / DONE_WITH_CONCERNS).

Definitions for `<N>`, `<K>`, `<MARKER>-N-K`, branch names, Linear doc IDs, and file paths: per `naming.md`. This skill does not redefine them.

## Trigger

- Cascade: Task-invoked by /specify on seal (parent label = `scope:specified`).
- Manual override: `/plan <MARKER>-N`, `plan <MARKER>-N`, `decompose <MARKER>-N`, `split <MARKER>-N` — re-decomposition or debugging. Not founder-documented. Manual fire against a parent already at `scope:planned` requires archived children (founder's responsibility) before re-decomposition.
<!-- accept-oversize mode removed: undecomposable parents halt to /specify --unseal per halt-messages §undecomposable-parent. -->

## Gate naming reconciliation (v0.2)

D3.4 §Per-stage gate inventory `/plan` row names this skill's three gates `plan.provenance`, `plan.decomposition-shape`, `plan.child-inheritance`. The parent `spec.md` AC-7 and `decomposition.md` Child 0001-B name two of them differently (`plan.children-have-strategies-for-hybrid`, `plan.decomposition-doc-sealed`). Same gates by intent. This skill uses **D3.4's names** because D3.4 is the binding gate-definition spec and its names cover broader predicate sets. AC-7 and Child 0001-B are amended as a one-line follow-on; if this skill is read before that amendment lands, treat the D3.4 names below as authoritative.

## Behavior

1. **Pre-flight preconditions and `plan.provenance` gate evaluation** (any failure halts with `BLOCKED` per `completion-status.md`; halt-card per `docs/templates/halt-messages.md`).

   **Project-level preconditions** (carry from v0.1):
   - Parent ticket <MARKER>-N exists and carries label `scope:specified` per `scope-labels.md`.
     - `scope:planned` observed without manual override → `BLOCKED`: "<MARKER>-N already planned. Use manual override only after archiving prior children, or iterate via /review guidance."
     - No scope label → `BLOCKED`: "<MARKER>-N isn't specified yet. Run /specify first."
   - Spec markdown exists at `docs/specs/NNNN-<slug>/spec.md` per `naming.md`. Missing → `NEEDS_CONTEXT`.
   - Four-hat document `[<MARKER>-DOC-NNNN] four-hat: <MARKER>-N <title>` per `naming.md` exists, and every finding in its most recent iteration has a recorded resolution (Incorporate / Defer / Reject). Unresolved findings → `BLOCKED`. (Normally enforced by /specify at seal time; checked here as defense in depth.)
   - Marker resolvable from `docs/.solo-config.json`. Unset → `NEEDS_CONTEXT`.

   **Gate `plan.provenance`** (pre-flight; chain integrity + AC-hash chain). Per D3.4 §Per-stage gate inventory `/plan` row. Evaluates BEFORE the decomposer invoke and before any halt card is composed (per D3.4 §Aggregation rules — all gates evaluate, none short-circuit, single aggregate halt card):

   ```text
   read cascade:run-state from .cascade/run-state.json

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

2. **Task-invoke decomposer** per `[SOL-AGENT] decomposer`. Inputs: path to parent spec, marker, parent ticket ID (for K-numbering context). The agent reads the spec end-to-end (including `## Decomposition strategy` per D3.1 — see §Decomposer reading below), classifies each draft child as vertical or horizontal, and surfaces chunking concerns as findings.

   Returns two blocks:
   - `## Children` — per-child draft in proposed build order. Each child carries: title, classification (vertical | horizontal, with one-line justification when horizontal), description, AC subset (by parent-spec position), failing-test seed subset, blockers (sibling K-numbers or "none"), and the per-child Strategy value per the D3.1 override-finding flow below.
   - `## Findings` — optional. Chunking concerns, missing-AC-coverage flags, scope-resistance signals, and the new `decomposition-override` finding class per D3.1. Auditor-stance per `auditor-stance.md`.

   ### Decomposer reading — D3.1 strategy and override-finding flow

   The decomposer subagent (`.claude/agents/decomposer.md`) reads `## Decomposition strategy` from the parent spec at invocation, alongside its existing reads (problem statement, AC list, failing-test seed, scope boundary). This is the D3.1 amendment to the decomposer's input set; the strategy value flows through to each per-child block in `decomposition.md` and is referenced by the gate evaluators below.

   #### Override-finding flow (extends v0.1 critique pattern)

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

   #### Strategy carry-through to per-child manifests

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

3. **Map decomposer findings to /plan status** per `completion-status.md` §Agent contract. The `decomposition-override` finding class flows through the same triage rails as v0.1 critique findings; the founder's `incorporate`/`defer`/`reject` decision is recorded per §Decomposer reading above and does not by itself halt /plan.
   - Zero findings (after override-triage applied) → proceed to step 4.
   - All findings below halt threshold (no `high` severity; no `missing-edge-case` against AC coverage; no scope-resistance markers) → proceed to step 4; findings forwarded to the summary on `DONE_WITH_CONCERNS`.
   - Any finding at or above halt threshold → `BLOCKED`. No Linear writes. Halt-card per `docs/templates/halt-messages.md` with a single recommended next action and alternatives. Recommendation logic:
     - **Incomplete failing-test seed** (decomposer flagged AC-X not covered by parent's seed) → recommend `/specify <MARKER>-N --continue` (expand seed). Alternative: `/specify <MARKER>-N --unseal` if multiple AC have seed gaps (systemic spec issue). Last resort: remove AC-X from spec (defer feature).
     - **Undecomposable parent** (decomposer flagged scope-resistance: AC resists chunking into Code-Claude-sized vertical or horizontal slices) → recommend `/specify <MARKER>-N --unseal` to split the parent into two parent specs. No in-skill escape hatch — undecomposability is a spec defect.
     - **Scope-out-of-bounds chunking** (decomposer's draft child would touch surfaces explicitly listed as out-of-scope in the spec) → recommend `/specify <MARKER>-N --unseal` to expand scope explicitly, or trim AC.

4. **Wire dependencies and detect parallelization waves.**
   - For each draft child K, parse the decomposer's `Blockers` field; map to Linear `blockedBy` relationships among siblings.
   - Pair-wise wave detection: two children are parallel-eligible unless (a) a `blockedBy` relation exists between them, or (b) they likely touch overlapping target surfaces (heuristic from decomposer description + spec scope). Group into waves. When in doubt, mark sequential — false parallelism causes merge conflicts; missed parallelism just costs wall-clock time.

5. **At-write gate evaluation, then same-turn write batch.** Two gates evaluate against the in-memory decomposition.md before manifest seal. All gates evaluate; no short-circuit (per D3.4 §Aggregation rules). If any gate fails, compose an aggregate halt card per D3.4 §Aggregation rules and do NOT write the manifest. If every gate passes, write decomposition.md + per-child ticket artifacts + manifest + parent label transition in one same-turn batch per `write-discipline.md`.

   ```text
   GATES_AT_PLAN_WRITE = [
     "plan.decomposition-shape", # D3.1 hybrid-without-child-overrides + per-child strategy populated
     "plan.child-inheritance"    # seed strict-subset + pyramid_shape inheritance + artifact field propagation
   ]

   for gate in GATES_AT_PLAN_WRITE:
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

   ### Same-turn write batch (on all-gates-pass)

   When every gate passes, emit one same-turn write batch per `write-discipline.md`:

   - Linear: batch-create all children with `scope:sealed` per `scope-labels.md`, parentId set, blockedBy wired, title and description from the decomposer draft, branch name `<MARKER>-N-<slug>-K` per `naming.md`. Each child's Linear-side description carries the `Strategy:` field (`inherited` or an explicit override value); for heavyweight children whose own decomposition.md will follow at a later `/specify`, the field captures the resolved value at this seal time.
   - Linear: post parallelization-plan comment on parent (wave list). Append the worktree-pattern block when Wave 1 has ≥2 parallel-eligible children AND `parallelization.enabled = true` in `docs/.solo-config.json` (see `commands/config.md` for config semantics, pending Batch 3 — currently inlined defaults):

     ~~~
     To run Wave 1 in parallel:
       git worktree add ../<repo>-<MARKER>-N-1 <MARKER>-N-<slug>-1
       git worktree add ../<repo>-<MARKER>-N-2 <MARKER>-N-<slug>-2
     Open one Code-Claude session per worktree. Serializing in one worktree is also fine.
     ~~~

     If `parallelization.enabled = false`, render the wave structure but suppress the worktree block — sequential build is the founder's chosen mode.

   - Linear: atomic parent label transition `scope:specified` → `scope:planned` per `scope-labels.md` (prior label removed in the same write).
   - Filesystem: write `docs/specs/NNNN-<slug>/decomposition.md` (template below). Every per-child block carries the resolved `Strategy:` field per the D3.1 flow above.
   - Filesystem: write `/plan` manifest at `.cascade/manifests/<ticket>-plan.json` per the schema in §Manifest write below. After write, update `cascade:run-state.json`'s `last_completed_stage` to point at this manifest path and sha.
   - All writes batched same-turn per `write-discipline.md`. Partial-failure handling per `write-discipline.md` §Partial failure: marker file at `docs/specs/NNNN-<slug>/.plan.sync.pending`; surface `BLOCKED` with a sync-retry hint pointing at manual re-fire of /plan.

6. **Heavyweight-child-spec hint** (Q2 conditional offer). For any child whose decomposer-draft description exceeds 250 words OR contains an "API contract" / "UX flow" section, append to the parallelization comment: "<MARKER>-N-K has substantial design surface — `/specify <MARKER>-N-K` will produce a heavyweight child spec before /build."

7. **Chain to /review.** Continuation per the §/Chains contract below — this skill is the first stage in the Group E chain (`/plan` → `/review` → `/update-linear`).

## Decomposition.md template

Written at `docs/specs/NNNN-<slug>/decomposition.md` alongside `spec.md`. Single same-turn write per step 5. Re-written in place on iteration (no archive; iteration tracking lives on the /review document). Every per-child block carries the `Strategy:` field per §Decomposer reading above.

~~~markdown
# Decomposition: <MARKER>-N <title>

> Parent: <MARKER>-N
> Children: <count>
> Plan run: YYYY-MM-DD (iteration <N> if not first)

## Chunking rationale
<1–2 paragraphs from the decomposer's output, explaining why these N children, why this granularity. Surface the journey segments / user-outcome units that drove the split.>

## Children
- **<MARKER>-N-1** — <title>. Vertical / horizontal (one-line justification if horizontal). Covers AC: <list>.
- **<MARKER>-N-2** — ...
- ...

## Dependency graph
```

<MARKER>-N-1 ──┬──> <MARKER>-N-3
<MARKER>-N-2 ──┘

```
(or text equivalent: `<MARKER>-N-3 blocked by [<MARKER>-N-1, <MARKER>-N-2]`)

## Parallelization map
- Wave 1 (parallel): <MARKER>-N-1, <MARKER>-N-2
- Wave 2 (after Wave 1): <MARKER>-N-3

## Rejected alternatives (optional)
- <only when the decomposer surfaced a near-miss worth recording>
~~~

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

For children with `Strategy: <override-value>`, the override-rationale is written under the child's block as the `Rationale:` line per the incorporate-flow in §Decomposer reading above.

### Per-child block shape (lightweight children)

Lightweight children live as Linear ticket descriptions, not as separate spec files. The decomposition.md still carries the block above; the ticket description carries the same fields in Linear's surface format. The `Strategy:` field appears in both places.

## Manifest write

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

## Iteration mode (when invoked with guidance from /review)

Invoked when /review surfaces findings that require re-decomposition. Guidance shape: `[{type, locus, suggestion}, ...]` per `auditor-stance.md`.

1. Load existing children for parent.
2. Re-invoke decomposer with the same spec PLUS the /review guidance as additional context. The agent re-emits Children + Findings, taking guidance into account.
3. Diff old children vs new children: identify merged-away siblings, redrafted siblings, new siblings, downgraded-to-sequential pairs.
4. Re-derive dependencies + parallelization waves on the new set.
5. Update affected child tickets in place per `write-discipline.md` — don't re-batch-create. Linear `update` for changed children; `delete` for merged-away; `create` for new. All same-turn.
6. Re-write `decomposition.md` in place.
7. Task-invoke /review again. If /review returns `DONE`, terminate; otherwise iterate (bounded by /review's iteration cap).

## Outputs

| Artifact | Location |
|---|---|
| Child tickets | scope:sealed, parentId set, blockedBy wired, Strategy field per child |
| Decomposition rationale | `docs/specs/NNNN-<slug>/decomposition.md` |
| Parallelization plan | Comment on parent ticket |
| Updated parent label | scope:specified → scope:planned |
| `/plan` manifest | `.cascade/manifests/<ticket>-plan.json` |

## Completion status

Per `completion-status.md`. v0.2 mappings:

- `DONE` — decomposer returned zero findings (after override-triage); children created with `scope:sealed` and resolved Strategy fields; decomposition.md written; parallelization comment posted; parent transitioned to `scope:planned`; manifest sealed; `/review` Task-invocation returned `DONE`.
- `DONE_WITH_CONCERNS` — completed end-to-end, but: decomposer surfaced sub-threshold concerns (forwarded to summary); horizontal-slice fallback used because vertical was infeasible; iteration mode applied /review guidance and converged; non-hybrid parent accumulated 3+ override-incorporations (informational critique per Gate 2 Predicate 5).
- `BLOCKED` — preconditions failed; `plan.provenance` gate failed (`§provenance-chain-broken` or `§ac-list-drift`); `plan.decomposition-shape` gate failed (`§plan-decomposition-invalid`, `§hybrid-without-child-overrides`, or `§hybrid-nesting-too-deep`); `plan.child-inheritance` gate failed (`§child-seed-not-subset` or `§child-shape-inheritance-broken`); decomposer surfaced halt-threshold findings (incomplete failing-test seed, undecomposable parent, scope-resistance); Linear write failed (partial-failure marker dropped per `write-discipline.md`); /review returned `BLOCKED`.
- `NEEDS_CONTEXT` — spec markdown missing at expected path; `docs/.solo-config.json` `marker` unset; decomposer surfaced a question requiring founder input the skill cannot resolve.

## /Chains

**Pattern:** C (auto-fire-chain, Group E variant)
**Group:** E
**Within-group transitions:** this skill is the first stage in the Group E chain (`/plan` → `/review` → `/update-linear`). On `/plan` manifest seal at `.cascade/manifests/<ticket>-plan.json` (after the `plan.provenance`, `plan.decomposition-shape`, `plan.child-inheritance` gates per D3.4 §plan gates pass), this skill Task-invokes `/review` to advance the chain. In chat-Claude (per D2.3 v1.3 §Execution surface per group Group E row), "Task-invoke" is realised as project-instruction-driven narrative continuation — this skill instructs the model in-chat to begin `/review`'s flow immediately after sealing `/plan`'s manifest, citing the §`/Chains` contract's Group E auto-fire-chain commitment. Plan-internal safe boundaries (after decomposition seal per D2.3 v1.3 §Within-group safe boundaries Group E row) are advisory.
**Group exit trigger:** not this skill. `/plan` is a Group E chain intermediate; the chain's exit fires on `/update-linear`'s seal.
**Group exit render:** not this skill. Chain-intermediate stages never render the chat-end card. After `/plan`'s manifest seals, this skill continues to `/review` without rendering.
**Next group entry:** not this skill. The chain advances internally: `/plan` → `/review` → `/update-linear`; `/update-linear`'s `/Chains` section names Group E's next-group entry as F.
**Auto-fire compact handling:** not applicable for chat-Claude. Group E runs in chat-Claude; no live PreCompact hook. If a hypothetical future v0.3+ moves Group E to Claude Code (per D2.3 v1.3 §Within-group safe boundaries Group E row's "advisory" framing leaving the door open), auto-fire compact handling would apply with `next_chain_step` set to `"review"` on /plan's safe boundary; v0.2 does not implement this.
**Group's exit manifest:** not-this-skill — see `/update-linear`. `/plan`'s manifest at `.cascade/manifests/<ticket>-plan.json` is a chain intermediate, durable on disk per D2.1 v2.1 but not the Group E exit manifest. D4.6 v1.1 reads `/update-linear`'s manifest for Group E re-derivation, not `/plan`'s.

## Notes

**State machine.** Parent: `scope:specified → scope:planned` (this skill). Child: `(Backlog) → scope:sealed` (this skill). `scope:built` is /build's terminal label. See `scope-labels.md` for full state machine, transition ownership, and refusal protocol on stale labels.

**Why decomposer-then-mint, not inline.** The chunking decision is judgment-heavy and shape-stable (per `[SOL-AGENT] decomposer` model recommendation: opus). The minting decision is mechanical Linear-API plumbing. Keeping them in separate primitives lets the agent run on a heavier model for judgment while the skill stays cheap.

**Conservative parallelization.** When in doubt about whether two children can run in parallel, mark sequential. /review's parallelization audit is the safety net for misses, and merge conflicts are far more expensive than serial wall-clock time.

**Parallel Wave 1 is opportunity, not obligation.** v0.1 CLAUDE.md line: "/plan identifies parallel-eligible children; opening multiple Code-Claude sessions is manual. Serializing is fine. v0.2 will spawn subagents automatically."

**Heavyweight child specs (Q2 conditional).** Default no. The 250-word OR API/UX heuristic is applied to the decomposer's draft description, not founder perception of complexity. Surface a /specify offer only when the threshold trips.

**Children's failing-test seeds are strict subsets of the parent's seed.** No fabrication inside /plan. Gap detection (AC-X not covered by parent's seed) is a /specify defect surfaced by the decomposer as a finding; /plan halts with `BLOCKED` pointing back to /specify. Never iterate on the seed inside /plan. Enforced at-write by Gate 3 Predicate 1.

**Vertical preference biases /plan toward shorter dependency chains.** Vertical slices share less internal state than horizontal layers. Parallelization opportunities often increase as a side effect — don't engineer for this; let it emerge from the decomposer's classification rubric.

**Mixed-mode parents.** A parent spec with some user-visible AC and some pure-infrastructure AC gets a mixed-mode plan: vertical children for user-visible AC, horizontal children for infra AC, dependencies wired so infrastructure precedes vertical work. The decomposer handles classification; /plan handles dependency wiring. Hybrid-strategy parents formalize the mixed-mode case via D3.1 — every child carries an explicit per-child Strategy.

**No oversize escape hatch in v0.1/v0.2.** The pre-v0.1 `--accept-oversize` mode minted a `scope:sealed-oversize` child that was never in the state machine; /build refused to fire on it. The mode is removed. Undecomposable parents halt to `/specify <MARKER>-N --unseal` per halt-messages §undecomposable-parent — splitting the parent into two parents is the correct fix.

## Cross-references

- **D3.1 §`/plan`'s decomposer reading** — the decomposition-override finding class and the incorporate/defer/reject flow, consumed in §Decomposer reading.
- **D3.1 §Halt conditions §hybrid-without-child-overrides** — the binding halt card for Gate 2 Predicate 3.
- **D3.2 §Downstream consumer touch-points `/plan`'s decomposer** — the child seed strict-subset contract that Gate 3 Predicate 1 enforces.
- **D3.3 §`/plan`'s decomposer copies artifact_path and artifact_type to children's manifests** — the inheritance contract that Gate 3 Predicate 3 enforces.
- **D3.4 §Per-stage gate inventory `/plan`** — the three gates' firing order and predicate references.
- **D3.4 §Aggregation rules** — all-gates-evaluate + single-card-aggregate semantics for the plan halt.
- **D3.4 §Halt conditions §hybrid-nesting-too-deep** — the v0.2 one-level cap on hybrid nesting, enforced by Gate 2 Predicate 4.
- **D2.1 v2 §`/plan` row** — the upstream manifest schema (`child_tickets[]`, `parent_ticket`, `total_children`, `dag_path`) and verifier-predicate baseline; D3.4's three gates layer on top.
- **D2.1 v2.1** — the chain integrity machinery Gate 1 evaluates (manifest sha + parent name + ac_list_sha256 recompute).
- **Child A `spec.md.template`** — the spec template `/plan`'s decomposer reads to find `## Decomposition strategy`; without that section present and resolved, Gate 2 cannot evaluate parent strategy.
- **Child A `halt-messages-append.md`** halts 12–14 — `§strategy-missing` (fires from `/specify` not `/plan`; `/plan`'s pre-flight inherits the spec sealed under valid §Decomposition strategy by chain construction), `§strategy-conflict-unresolved` (same), `§hybrid-without-child-overrides` (the binding for Gate 2 Predicate 3).
- **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-7** — this skill amendment satisfies AC-7 as authored, modulo the gate-name reconciliation noted in §Gate naming reconciliation above.

## Open questions (deferred to v1.1+)

<!-- scope:sealed-oversize label entry removed: --accept-oversize mode dropped in v0.1 audit. -->
- **Manual override semantics formalization.** Manual /plan <MARKER>-N against `scope:planned` parent currently requires founder to archive children out-of-band. A formal `--archive-children` flag is v1.1 territory.
- **Parallelization heuristic precision.** Pair-wise overlap detection is heuristic (decomposer description + spec scope). AST-level file-prediction is v1.1+ work.
- **Auto-iteration cap from /plan side.** v0.1 caps iteration via /review's halt protocol; /plan doesn't impose its own cap. Revisit if cascades thrash.
- **Skill → command transformation.** Like the rest of the internal-only cascade, /plan may end up as a command in a future refactor if internal-only auto-fire makes "skill" semantics overkill. Not v0.1.
