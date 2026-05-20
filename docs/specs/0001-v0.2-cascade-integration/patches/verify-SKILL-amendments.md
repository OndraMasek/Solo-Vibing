# `.claude/skills/verify/SKILL.md` — v0.2 amendments

**Status:** Patch-ready amendment block. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing` which reconciles against v0.1 byte-for-byte before applying.

**Scope:** the per-strategy dispatch matrix per D3.4 §`/verify` gate dispatch by strategy, the `children_gate_outcomes[]` manifest schema write per D3.4 §Manifest schema additions, the multi-child halt-card aggregation per D3.4 §Aggregation rules, and the hybrid-children-recurse-one-level cap per D3.4 §hybrid-nesting-too-deep. The skill's frontmatter, the milestone-iteration scaffolding, and the `/Chains` block (sealed in `child_B_chains_sections.md` Pattern G Group G) carry forward from v0.1 unchanged at the substantive level.

**v0.1 reconciliation pattern:** the executing session reads v0.1's `.claude/skills/verify/SKILL.md` and substitutes by purpose ("the pre-flight step" / "the per-child loop" / "the milestone-aggregation step"). Per `decomposition.md` Child 0001-B's row, `/verify`'s amendment is the most substantive of Child 0001-B's nine skills — the v0.1 `/verify` had a flat per-child check (the D2.1 v2 "perceptual gate evidence or N/A for non-UI" pattern); v0.2 replaces that with the five-gate inventory and the per-strategy dispatch matrix.

**This amendment is the largest single change in Child 0001-B.** Implementation difficulty in the executing session is mainly in re-reading evidence per predicate (re-running perceptual tests, re-running invariance capture commands, recomputing per-child sha chains).

---

## Naming reconciliation note

D3.4 §Per-stage gate inventory `/verify` row names five gates: `verify.provenance`, `verify.child-completion`, `verify.perceptual-evidence`, `verify.invariance`, `verify.milestone-aggregation`. The parent `spec.md` AC-11 reads: "dispatches per strategy per D3.4 §verify gate dispatch by strategy: walking-skeleton / api-boundary / capability-cluster → `verify.perceptual-evidence` (D3.3 P1–P4); refactor-spike → `verify.invariance` (D3.3 P5–P9); hybrid → recursive per child (one level of nesting in v0.2; deeper halts `§hybrid-nesting-too-deep`). Multi-child halt-card aggregation per D3.4 §Aggregation rules. Writes `children_gate_outcomes[]` on the `/verify` manifest per the schema in D3.4 §Manifest schema additions."

AC-11 references D3.4 by name; no divergent gate names surface. The amendment uses D3.4's names verbatim.

---

## Stage structure

`/verify` is a milestone-level stage. It runs once per milestone seal, iterating every child of the milestone, and writes a single manifest at `.cascade/manifests/<milestone>-verify.json` per D3.4 §Manifest schema additions.

The amendment introduces three orchestration layers absent from v0.1:

1. **Milestone-level pre-flight** (`verify.provenance`, `verify.child-completion`) — runs once before any per-child evaluation.
2. **Per-child loop with strategy dispatch** — for each child, reads strategy from the child's `/specify` manifest and dispatches to either `verify.perceptual-evidence` or `verify.invariance` (or recurses one level for hybrid children).
3. **Milestone-level aggregation** (`verify.milestone-aggregation`) — runs after every child has been evaluated; composes the milestone halt card if any child halted; seals the manifest if every child passed.

```text
GATES_AT_VERIFY_PREFLIGHT     = ["verify.provenance", "verify.child-completion"]
GATES_AT_VERIFY_PER_CHILD     = ["verify.perceptual-evidence", "verify.invariance"]  # mutually exclusive per child
GATES_AT_VERIFY_AGGREGATION   = ["verify.milestone-aggregation"]

# Phase 1: pre-flight (all gates evaluate; do NOT short-circuit)
for gate in GATES_AT_VERIFY_PREFLIGHT:
    evaluate gate predicates and record per-gate result
if any pre-flight gate has failing predicates:
    compose milestone halt card
    do NOT enter per-child loop
    exit with halt

# Phase 2: per-child loop (every child evaluates; per-child halts accumulate in children_gate_outcomes[])
children_gate_outcomes ← []
for child in milestone.children:
    child_outcome ← evaluate_child_gate(child)
    append child_outcome to children_gate_outcomes
    # do NOT halt the loop on any single child's failure;
    # continue evaluating remaining children for full milestone diagnostic

# Phase 3: aggregation
verify.milestone-aggregation evaluates children_gate_outcomes
if any child_outcome.status == "halted":
    compose multi-child milestone halt card per §Multi-child halt aggregation below
    do NOT seal /verify manifest
    write per-child halt diagnostics to .cascade/halt/<child-ticket>-verify.txt
    exit with halt
else:
    seal /verify manifest with children_gate_outcomes[] populated
    update Linear milestone state
```

---

## Gate 1 — `verify.provenance` (pre-flight; milestone-wide chain)

```text
read cascade:run-state from docs/.cascade/run-state.json

# Step 1: read the parent /plan manifest (the milestone's planning seal)
expected_parent_path ← cascade:run-state.last_completed_stage.postcondition_manifest_path
if expected_parent_path absent:
    FAIL with §provenance-chain-broken
    diagnostic: f"expected parent manifest at {expected_parent_path}; absent"
    continue

recomputed_sha ← sha256 of parent manifest with manifest_sha256 field zeroed
if recomputed_sha != cascade:run-state.last_completed_stage.postcondition_manifest_sha256:
    FAIL with §provenance-chain-broken
    diagnostic: f"parent manifest sha mismatch at {expected_parent_path}"

# Step 2: per-child chain integrity
# Each child has its own /wrap manifest chained from /specify; /verify must read every chain.
for child in milestone.children (from parent /plan manifest's outputs.child_tickets[]):
    child_wrap_manifest_path ← .cascade/manifests/<child>-wrap.json
    if child_wrap_manifest_path doesn't resolve:
        FAIL with §provenance-chain-broken
        diagnostic: f"child {child}'s /wrap manifest absent at {child_wrap_manifest_path}; cannot verify"
        continue

    child_wrap_manifest ← read child_wrap_manifest_path
    child_wrap_recomputed_sha ← sha256 of child_wrap_manifest with manifest_sha256 field zeroed
    expected_child_wrap_sha ← (read from child's /wrap's pointer in cascade:run-state.last_per_ticket_states[child])
    if child_wrap_recomputed_sha != expected_child_wrap_sha:
        FAIL with §provenance-chain-broken
        diagnostic: f"child {child}'s /wrap manifest sha mismatch; chain integrity broken"
```

Halt code: `§provenance-chain-broken`. Recovery: `--reconcile` per D2.1 v2.1's chain-recovery pattern, OR `--rerun=<stage>` per D4.5 for absent-manifest cases (the consolidated rule per D4.6 v1.1 §Halt conditions widens to cover absent-exit-manifest cases routed to D4.5 `--rerun=<exit-stage>`).

## Gate 2 — `verify.child-completion` (pre-flight; D2.1 v2 `/verify` row)

```text
for child in milestone.children:
    # Predicate 1: Linear state is scope:built
    ticket_labels ← linear-mcp's read of child ticket's labels
    if "scope:built" not in ticket_labels:
        FAIL with §verify-child-not-built
        diagnostic: f"child {child} missing 'scope:built' label; current labels: {ticket_labels}"

    # Predicate 2: Linear ticket status is Done
    ticket_status ← linear-mcp's read of child ticket's status
    if ticket_status != "Done":
        FAIL with §verify-child-not-built
        diagnostic: f"child {child} status is '{ticket_status}'; expected 'Done'"

    # Predicate 3: /wrap manifest exists (chain integrity covered in Gate 1; this checks shape)
    child_wrap_outputs ← parse child_wrap_manifest's outputs
    if child_wrap_outputs.stage != "/wrap":
        FAIL with §verify-child-not-built
        diagnostic: f"child {child}'s manifest stage is '{child_wrap_outputs.stage}'; expected '/wrap'"
```

Halt code: `§verify-child-not-built`. Recovery: founder ensures every child of the milestone has completed `/wrap`; re-runs `/verify` for the milestone.

## Per-child loop with strategy dispatch

```text
def evaluate_child_gate(child, recursion_depth=0):
    """
    Returns ChildGateOutcome:
      .child_id, .strategy, .gate, .status, .predicates_evaluated[],
      .evidence_paths[], .evaluated_at, .halt_code? (if halted), .halt_diagnostic? (if halted)
    """
    # Read the child's /specify manifest (chained via input_provenance from /wrap)
    child_wrap_manifest ← read .cascade/manifests/<child>-wrap.json
    child_specify_path ← child_wrap_manifest.input_provenance.spec_manifest_path
                          (transitively: /wrap → /build → /update-linear or /plan → /review → /specify)
    child_specify_manifest ← read child_specify_path
    strategy ← child_specify_manifest.outputs.decomposition_strategy

    # Dispatch per strategy per D3.4 §`/verify` gate dispatch by strategy
    if strategy == "walking-skeleton":
        return evaluate_perceptual_evidence(child, strategy, P_set={P1, P2, P3})
    elif strategy == "api-boundary":
        return evaluate_perceptual_evidence(child, strategy, P_set={P1, P2, P3, P4})
    elif strategy == "capability-cluster":
        return evaluate_perceptual_evidence(child, strategy, P_set={P1, P2, P3})
    elif strategy == "refactor-spike":
        return evaluate_invariance(child, P_set={P5, P6, P7, P8, P9})
    elif strategy == "hybrid":
        # Hybrid parents have no parent-level child entry; recurse into grandchildren
        if recursion_depth >= 1:
            return ChildGateOutcome(
                child_id=child, strategy="hybrid", gate="(recursion)",
                status="halted",
                halt_code="§hybrid-nesting-too-deep",
                halt_diagnostic=f"child {child} is hybrid at recursion depth {recursion_depth}; v0.2 caps hybrid nesting at one level per D3.4 §hybrid-nesting-too-deep"
            )

        # Recurse into the hybrid child's own children
        grandchildren_outcomes ← []
        for grandchild in child's /plan manifest's outputs.child_tickets[]:
            outcome ← evaluate_child_gate(grandchild, recursion_depth=recursion_depth + 1)
            append outcome to grandchildren_outcomes

        # Roll up grandchild outcomes into a single parent-child outcome
        if any grandchild_outcome.status == "halted":
            return ChildGateOutcome(
                child_id=child, strategy="hybrid", gate="(recursive)",
                status="halted",
                halt_code="(see grandchildren)",
                halt_diagnostic=f"hybrid parent {child}: {count_halted}/{count_total} grandchildren halted"
            )
        else:
            return ChildGateOutcome(
                child_id=child, strategy="hybrid", gate="(recursive)",
                status="passed",
                grandchildren_count=len(grandchildren_outcomes)
            )
    else:
        # Strategy not in canonical enum — caught upstream by spec.strategy-annotation; defensive halt here
        return ChildGateOutcome(
            child_id=child, strategy=strategy, gate="(dispatch)",
            status="halted",
            halt_code="§verify-strategy-unrecognized",
            halt_diagnostic=f"child {child}'s strategy '{strategy}' not in canonical enum; upstream /specify should have caught this"
        )
```

### `evaluate_perceptual_evidence(child, strategy, P_set)` — `verify.perceptual-evidence`

Evaluates D3.3 P1–P4 per the strategy's required subset. For walking-skeleton and capability-cluster: P1–P3 per `[perceptual]` entry in `failing_test_seed[]`. For api-boundary: P1–P4 (P4 is the transcript-shape check).

```text
def evaluate_perceptual_evidence(child, strategy, P_set):
    spec_seed ← child_specify_manifest.outputs.failing_test_seed
    perceptual_entries ← [entry for entry in spec_seed if entry.tag == "perceptual"]

    # No [perceptual] entries → strategy is misapplied (caught upstream by spec.pyramid-shape);
    # /verify still reports the absence as defensive
    if perceptual_entries is empty:
        return ChildGateOutcome(
            child_id=child, strategy=strategy, gate="verify.perceptual-evidence",
            status="halted",
            halt_code="§perceptual-evidence-missing/no-perceptual-entry",
            halt_diagnostic=f"child {child}'s strategy={strategy} requires [perceptual] entries; none found in failing_test_seed[]"
        )

    failures ← []
    evidence_paths ← []

    for entry in perceptual_entries:
        artifact_path ← entry.artifact_path
        append artifact_path to evidence_paths

        # P1: artifact present on filesystem
        if P1 in P_set:
            if not filesystem_exists(artifact_path):
                append (entry.name, "P1", "§perceptual-evidence-missing/artifact-absent",
                        f"artifact at {artifact_path} absent on filesystem") to failures
                continue   # P1 failure blocks P2/P3 for this entry

        # P2: re-run the test, exit zero
        if P2 in P_set:
            test_exit_code ← shell-execute "<runner> <test_name>"
                              (runner inferred from .solo-config.json or the existing v0.1 wiring)
            if test_exit_code != 0:
                append (entry.name, "P2", "§perceptual-evidence-missing/regeneration-failed",
                        f"test '{entry.name}' exited non-zero at /verify re-run; exit code {test_exit_code}") to failures
                continue

        # P3: byte-stability between checked-in and freshly-regenerated artifact
        if P3 in P_set:
            sha_before  ← sha256 of artifact_path at /verify start (filesystem-canonical)
            sha_after   ← sha256 of artifact_path after test re-run
            if sha_before != sha_after:
                append (entry.name, "P3", "§perceptual-evidence-missing/byte-stability-failed",
                        f"artifact at {artifact_path} regenerated to different bytes; sha_before={sha_before[:12]}..., sha_after={sha_after[:12]}...") to failures

        # P4: api-boundary only — transcript-shape check
        if P4 in P_set and strategy == "api-boundary":
            transcript_content ← read artifact_path  # the integration-transcript.md
            if not transcript_parses_to_h2_h3_schema(transcript_content):
                append (entry.name, "P4", "§perceptual-evidence-missing/transcript-shape-violation",
                        f"integration transcript at {artifact_path} does not parse to minimum H2/H3 schema per D3.3") to failures

    if failures is non-empty:
        # Aggregate per D3.4 §Multi-failure aggregation within a gate
        primary_failure ← failures[0]  # earliest predicate per D3.4 §Within a gate
        return ChildGateOutcome(
            child_id=child, strategy=strategy, gate="verify.perceptual-evidence",
            status="halted",
            predicates_evaluated=[p for p in P_set],
            evidence_paths=evidence_paths,
            halt_code=primary_failure.halt_code,
            halt_diagnostic=primary_failure.diagnostic,
            other_failures=failures[1:]  # listed in diagnostic context
        )

    return ChildGateOutcome(
        child_id=child, strategy=strategy, gate="verify.perceptual-evidence",
        status="passed",
        predicates_evaluated=[p for p in P_set],
        evidence_paths=evidence_paths,
        evaluated_at=now()
    )
```

Halt codes per D3.3 §Halt conditions: `§perceptual-evidence-missing` with sub-cases `artifact-absent`, `regeneration-failed`, `byte-stability-failed`, `transcript-shape-violation`, `no-perceptual-entry` (last is defensive).

### `evaluate_invariance(child, P_set)` — `verify.invariance`

Evaluates D3.3 P5–P9 for refactor-spike children.

```text
def evaluate_invariance(child, P_set):
    invariance_artifact ← child_specify_manifest.outputs.invariance_artifact
    if invariance_artifact is None:
        return ChildGateOutcome(
            child_id=child, strategy="refactor-spike", gate="verify.invariance",
            status="halted",
            halt_code="§perceptual-evidence-missing/artifact-absent",
            halt_diagnostic=f"refactor-spike child {child}'s outputs.invariance_artifact is null; upstream /specify should have populated it"
        )

    failures ← []

    # P5: pass-set-at-seal.txt exists at the documented path
    if P5 in P_set:
        pass_set_path ← invariance_artifact.pass_set_path
        if not filesystem_exists(pass_set_path):
            append ("P5", "§perceptual-evidence-missing/artifact-absent",
                    f"pass-set-at-seal at {pass_set_path} absent; strategy=refactor-spike") to failures

    # P6: file's current sha256 equals manifest's pass_set_sha256
    if P6 in P_set and P5-passed:
        current_sha ← sha256 of pass_set_path file content
        if current_sha != invariance_artifact.pass_set_sha256:
            append ("P6", "§invariance-seal-tampering",
                    f"pass-set-at-seal sha mismatch; manifest sha={invariance_artifact.pass_set_sha256[:12]}..., current={current_sha[:12]}...; file edited post-seal") to failures

    # P7: configured invariance.pass_set_capture_command hashes to capture_command_sha256
    if P7 in P_set:
        config ← read docs/.solo-config.json
        if config absent or invariance.pass_set_capture_command absent:
            append ("P7", "§invariance-config-missing",
                    f"docs/.solo-config.json or invariance.pass_set_capture_command absent at /verify time") to failures
        else:
            current_cmd_sha ← sha256 of config.invariance.pass_set_capture_command string
            if current_cmd_sha != invariance_artifact.capture_command_sha256:
                append ("P7", "§invariance-config-changed",
                        f"capture command sha mismatch; manifest sha={invariance_artifact.capture_command_sha256[:12]}..., current={current_cmd_sha[:12]}...; command edited post-seal") to failures

    # P8: re-run the capture command
    if P8 in P_set and P7-passed:
        stdout, exit_code ← shell-execute config.invariance.pass_set_capture_command from repo root
        if exit_code != 0:
            append ("P8", "§invariance-config-missing/capture-failed",
                    f"capture command exited with code {exit_code} at /verify re-run") to failures
        elif stdout is empty after filtering:
            append ("P8", "§invariance-config-missing/capture-failed",
                    f"capture command produced no pass-set output at /verify re-run") to failures
        else:
            # Write pass-set-at-verify.txt (NOT committed; .gitignore-d per Child A)
            verify_pass_set ← filter stdout (blank lines and '#'-prefixed lines removed)
            write verify_pass_set to docs/specs/<child-slug>/invariance/pass-set-at-verify.txt

    # P9: set-membership — every line in pass-set-at-seal.txt appears in pass-set-at-verify.txt
    if P9 in P_set and P8-passed:
        seal_pass_set   ← read pass_set_path lines as set
        verify_pass_set ← read pass-set-at-verify.txt lines as set
        missing ← seal_pass_set - verify_pass_set
        if missing is non-empty:
            sample_missing ← sorted(missing)[:5]
            append ("P9", "§invariance-pass-set-regression",
                    f"{len(missing)} tests in pass-set-at-seal absent from pass-set-at-verify; sample: {sample_missing}") to failures

    seal_count   ← len(read pass_set_path lines)
    verify_count ← len(read pass-set-at-verify.txt lines if P8-passed else 0)

    if failures is non-empty:
        primary_failure ← failures[0]
        return ChildGateOutcome(
            child_id=child, strategy="refactor-spike", gate="verify.invariance",
            status="halted",
            predicates_evaluated=[p for p in P_set],
            evidence_paths=[pass_set_path],
            halt_code=primary_failure.halt_code,
            halt_diagnostic=primary_failure.diagnostic,
            other_failures=failures[1:],
            seal_pass_set_count=seal_count,
            verify_pass_set_count=verify_count
        )

    return ChildGateOutcome(
        child_id=child, strategy="refactor-spike", gate="verify.invariance",
        status="passed",
        predicates_evaluated=[p for p in P_set],
        evidence_paths=[pass_set_path],
        evaluated_at=now(),
        seal_pass_set_count=seal_count,
        verify_pass_set_count=verify_count
    )
```

Halt codes per D3.3 §Halt conditions: `§perceptual-evidence-missing/artifact-absent` (P5; same card handles both perceptual and invariance file-absence per D3.3 with strategy annotation in diagnostic), `§invariance-seal-tampering` (P6), `§invariance-config-changed` (P7), `§invariance-config-missing` and `§invariance-config-missing/capture-failed` (P7/P8), `§invariance-pass-set-regression` (P9).

## Gate 5 — `verify.milestone-aggregation` (at-write; aggregate children_gate_outcomes)

After the per-child loop completes:

```text
halted_children ← [o for o in children_gate_outcomes if o.status == "halted"]

if halted_children is non-empty:
    # Compose milestone halt card per §Multi-child halt aggregation below
    compose_milestone_halt_card(halted_children, passed_children, milestone_id)
    write per-child halt diagnostic for each halted child to .cascade/halt/<child-ticket>-verify.txt
    release any held locks
    remove /verify from cascade:run-state.active_stages[]
    FAIL with §verify-milestone-aggregation-failed
    diagnostic: f"milestone {milestone_id}: {len(halted_children)}/{len(children_gate_outcomes)} children halted"
else:
    # All children passed; proceed to manifest write
    pass
```

Halt code: `§verify-milestone-aggregation-failed` (authored in Child A's halt-messages-append.md halt 11 of the D3.4 set). Recovery: per-child — the founder reviews each halted child's diagnostic, fixes the child (re-runs `/build <child> --continue`, or `/specify <child> --unseal` for structural defects), then re-runs `/verify` for the milestone.

---

## Multi-child halt aggregation

Per D3.4 §Aggregation rules across children at `/verify`: each child stands alone in the milestone roll-up. No precedence selection across children — every halted child reports its own halt card; the milestone halt card aggregates without compressing.

### Milestone halt card shape

Per D3.4 §Across children at /verify example:

```text
HALT at /verify for milestone <M-N>

Children that halted at /verify:
  <child-id> (<strategy>):
    <halt-code>
    <one-line diagnostic>
  <child-id> (<strategy>):
    <halt-code>
    <one-line diagnostic>
  ...

Children that passed:
  <child-id-1>, <child-id-2>, ...

Recommendation per child:
  <child-id>: <recovery path per the halt code's recommendation>
  <child-id>: <recovery path per the halt code's recommendation>
  ...

Diagnostic context:
  Milestone: <M-N>
  Children evaluated: <total>
  Children passed: <count_passed>
  Children halted: <count_halted>
  See child manifests and halt diagnostics under:
    .cascade/halt/<child-1>-verify.txt
    .cascade/halt/<child-2>-verify.txt
    ...
```

Per D3.4: this is the canonical multi-child halt-card shape; `/verify`'s `solo-verify` parity emits the same structure when invoked via `solo-verify verify <milestone>`.

---

## Manifest write (on all-children-pass)

Write the `/verify` manifest at `.cascade/manifests/<milestone>-verify.json` per D3.4 §Manifest schema additions:

```json
{
  "stage": "/verify",
  "milestone_id": "<M-N>",
  "verify_sealed_at": "<ISO-8601 timestamp>",
  "outputs": {
    "milestone_id":                     "<M-N>",
    "all_children_completed":           true,
    "journeys_doc_post_ship_sha256":    "<sha>",
    "children_gate_outcomes":           [
      {
        "child_id":              "SOL-117",
        "strategy":              "walking-skeleton",
        "gate":                  "verify.perceptual-evidence",
        "status":                "passed",
        "predicates_evaluated":  ["P1", "P2", "P3"],
        "evidence_paths":        ["docs/specs/0042-login/perceptual/post-login.png"],
        "evaluated_at":          "2026-05-19T14:23:11Z"
      },
      {
        "child_id":               "SOL-122",
        "strategy":               "refactor-spike",
        "gate":                   "verify.invariance",
        "status":                 "passed",
        "predicates_evaluated":   ["P5", "P6", "P7", "P8", "P9"],
        "evidence_paths":         ["docs/specs/0048-billing-cleanup/invariance/pass-set-at-seal.txt"],
        "evaluated_at":           "2026-05-19T14:25:47Z",
        "seal_pass_set_count":    247,
        "verify_pass_set_count":  252
      }
    ]
  },
  "input_provenance": {
    "parent_manifest_path":      ".cascade/manifests/<parent>-plan.json",
    "parent_manifest_sha256":    "<sha>",
    "per_child_wrap_manifest_shas": {
      "SOL-117": "<sha>",
      "SOL-122": "<sha>",
      ...
    }
  },
  "manifest_sha256": "<recomputed-zero-self-field>"
}
```

Schema rules per D3.4 §Manifest schema additions:

- `children_gate_outcomes[]` is present on every successfully-sealed `/verify` manifest.
- `status` is `"passed"` only on sealed manifests (halted children produce no manifest; failures live in `.cascade/halt/<child>-verify.txt`).
- For refactor-spike children, `seal_pass_set_count` and `verify_pass_set_count` are included for cheap delta reporting at `/retro`.
- For hybrid children that recursed, the parent-child outcome entry carries `gate: "(recursive)"` and `grandchildren_count` per the recursion roll-up logic above.

After write, update `cascade:run-state.json`'s `last_completed_stage` to point at this manifest path and sha. Update the milestone's Linear state per D2.1 v2 `/verify` row.

---

## Cross-references

- **D2.1 v2 §`/verify` row** — the upstream manifest schema baseline (milestone_id, all_children_completed, journeys_doc_post_ship_sha256); D3.4's `children_gate_outcomes[]` is additive.
- **D2.1 v2 §Caller-side verification protocol** — the per-child manifest re-read pattern Gates 1 and 2 implement.
- **D3.3 §Walking-skeleton / Api-boundary / Capability-cluster perceptual predicate** — P1–P4 binding text for `verify.perceptual-evidence`.
- **D3.3 §Refactor-spike invariance predicate** — P5–P9 binding text for `verify.invariance`.
- **D3.3 §Halt conditions** — `§perceptual-evidence-missing` (with sub-cases), `§invariance-pass-set-regression`, `§invariance-seal-tampering`, `§invariance-config-changed`, `§invariance-config-missing` — referenced by halt-code.
- **D3.4 §Per-stage gate inventory `/verify` row** — the five-gate inventory this amendment implements.
- **D3.4 §`/verify` gate dispatch by strategy** — the binding dispatch matrix this amendment's per-child loop implements.
- **D3.4 §Dispatch sequence at `/verify`** — the 7-step orchestration this amendment's `evaluate_child_gate` follows.
- **D3.4 §Per-strategy gate-run cost notes** — the v0.2.x `--trust-build` flag deferral (re-run-every-time is v0.2's stance).
- **D3.4 §Multi-failure aggregation** — both within-a-gate (earliest predicate primary) and across-children-at-/verify (each child stands alone) rules.
- **D3.4 §Manifest schema additions** — the `children_gate_outcomes[]` schema this amendment writes.
- **D3.4 §Halt conditions** — `§verify-milestone-aggregation-failed` (Gate 5's halt code) authored in Child A's halt-messages-append.md.
- **D3.4 §hybrid-nesting-too-deep** — the one-level cap this amendment enforces in `evaluate_child_gate`'s recursion guard.
- **Child A `solo-config.json`** + **Child A `solo-config.example.json`** — `invariance.pass_set_capture_command` read at P7/P8.
- **Child A `.gitignore`** — `docs/specs/*/invariance/pass-set-at-verify.txt` excluded from git; this skill writes it freshly every run.
- **Child A `halt-messages-append.md`** — fourteen new halts authored; this amendment references all the D3.3 and D3.4 halts by code.
- **`child_B_chains_sections.md`** Pattern G Group G (`/verify`) — the `/Chains` block for `/verify` was sealed in a prior session; this amendment's gates land BEFORE the `/Chains` block's group-exit rendering of the chat-end card (variant `normal`, since milestone-aggregation halts halt the chat-end-card render entirely per D2.3 v1.3).
- **`plan-SKILL-amendments.md`** (prior session of Child 0001-B) — the `child_strategies[]` array on `/plan`'s manifest that this amendment's Gate 2 reads to know each child's strategy without re-parsing `decomposition.md`.
- **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-11** — this skill amendment satisfies AC-11 as authored.
