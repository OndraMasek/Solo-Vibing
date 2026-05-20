# Child 0001-D — `tools/solo-verify` authoring notes

**Session:** Child 0001-D of 0001 v0.2 cascade integration spec
**Strategy:** walking-skeleton
**Perceptual artifact (canonical):** `docs/specs/0001-v0.2-cascade-integration/perceptual/solo-verify-list-gates.txt`
**Stack:** Python 3.10+ stdlib only (per D4.0)
**LOC:** ~2900 (script) + ~750 (test seed)

---

## 1 · What shipped

Three deliverables, in the order they layer.

### 1.1 · `tools/solo-verify` — the gate-evaluator CLI

Single-file Python 3.10+ stdlib script. Implements the full D3.4 §`solo-verify` CLI surface plus the four hook-invocation aliases from D2.2 §Hook/script table.

**CLI surface (per stage):**

```
solo-verify onboard       <product>     # 2 gates
solo-verify specify       <ticket>      # 5 gates
solo-verify review        <ticket>      # 3 gates
solo-verify plan          <ticket>      # 3 gates
solo-verify update-linear <ticket>      # 1 gate
solo-verify build         <ticket>      # 4 gates (provenance, pyramid-tampering, test-execution, finalize — AC-9 split)
solo-verify wrap          <ticket>      # 4 gates (provenance, tests-green, mirror-sha-match, linear-state-updated — AC-10 split)
solo-verify verify        <milestone>   # 5 gates incl. per-child dispatch
solo-verify retro         <milestone>   # 1 gate
```

**Flags:**

```
<stage> <id> --gate <name>      # single-gate
<stage> <id> --reconcile [--yes] # F-Rev-2 carry-forward (drift detection, repair deferred to v0.2.x)
<stage> <id> --json              # machine-readable result
--list-gates [stage]             # inventory
--explain <stage>.<gate-name>    # predicate text + halt codes + recovery
```

**Hook aliases:**

```
solo-verify subagent       <agent_id>   # → /review --gate review.four-hat-objection-coverage
solo-verify build-spawn    <ticket>     # → /build --gate build.provenance
solo-verify build-finalize <ticket>     # → /build --gate build.finalize  ← LOAD-BEARING (stop-orchestrator.sh)
solo-verify milestone      <id>         # → /verify
```

**Exit codes (D3.4):**

| Code | Meaning | Triggers |
| ---- | ------- | -------- |
| 0 | All evaluated gates passed | — |
| 1 | Standard halt | Founder-visible halt card |
| 2 | Stage / gate unknown; Python too old; usage error | `argparse` / version gate |
| 3 | Manifest chain broken (provenance halt) | Routes to `--reconcile` per D4.5 |
| 4 | Filesystem / Linear inconsistency that prevents evaluation | `§cascade-fs-inconsistent` (e.g. `.cascade/manifests/` absent) |

### 1.2 · `tests/solo-verify/test_solo_verify.py` — failing-test seed

Stdlib `unittest` only. 45 tests across the tiers per the walking-skeleton catalog:

* **[unit]** — 30 tests covering predicate helpers in isolation: `_check_pyramid_shape` (5), `_verify_chain_to_parent` (4), `_evaluate_invariance` (3 — seal-time + verify-time paths), `_evaluate_perceptual_evidence` (5), `_check_strategy_evidence` invariance-empty-set (1), `_render_halt_card` (2), `StageResult.exit_code` routing (3), manifest self-zeroed sha (1), `GATES` registry invariants (3), `STAGE_ORDER` (1), capability-cluster / hybrid catalog edge cases (handled inside the pyramid-shape tests).
* **[smoke]** — 14 tests covering the CLI dispatcher via `subprocess`: `--list-gates` (2), `--explain` (3), exit-code mapping (5), hook aliases (4), `--reconcile` carry-forward parsability across all 9 stages (2), `/verify` per-strategy dispatch (1).
* **[perceptual]** — 1 test: byte-equality between `--list-gates` rendering and the sealed artifact at `docs/specs/0001-v0.2-cascade-integration/perceptual/solo-verify-list-gates.txt`. **This test fails pre-/build** — that is the walking-skeleton seed contract (D3.2). It passes once /build seals the artifact.

Run: `python3 -m unittest discover tests/solo-verify/ -v`

Current state: **44/45 pass**, 1 [perceptual] failing-by-design.

### 1.3 · F-Rev-2 carry-forward

`--reconcile` is now valid on all 9 stages (v0.1 shipped it on /specify, /plan, /build, /wrap only; v0.2 adds /onboard, /update-linear, /review, /verify, /retro). The v0.2 semantic is **drift detection only**: report what differs between the stage's expected state (re-derived from the upstream manifest's `outputs`) and the on-disk state, with `--yes` short-circuiting any interactive prompts. **Repair-on-confirm is deferred to v0.2.x** per D4.5 §What v0.2 does not ship.

---

## 2 · Gate inventory — 28 gates across 9 stages

The handoff prompt said "~22 gates"; the actual ship count is **28**. The delta is from the AC-9 (/build) and AC-10 (/wrap) splits that were finalized in Child 0001-B continuation 0:

* **/build** has 4 gates: `provenance`, `pyramid-tampering`, `test-execution`, `finalize` — formerly a single `/build` gate in pre-v0.2 drafts.
* **/wrap** has 4 gates: `provenance`, `tests-green`, `mirror-sha-match`, `linear-state-updated`.

This is **not** a deviation from the spec — D3.4's gate table also lists 28 — it's a delta from D4.0's prose count, which is informational. The `--list-gates` rendering is the canonical inventory.

Full list (matches `solo-verify --list-gates` output byte-for-byte once sealed):

```
/onboard         onboard.linear-projects, onboard.config-write
/specify         spec.provenance, spec.ac-coverage, spec.pyramid-shape,
                 spec.strategy-evidence, spec.strategy-annotation
/review          review.provenance, review.four-hat-objection-coverage, review.ac-list-seal
/plan            plan.provenance, plan.decomposition-shape, plan.child-inheritance
/update-linear   update-linear.diff-applied
/build           build.provenance, build.pyramid-tampering,
                 build.test-execution, build.finalize
/wrap            wrap.provenance, wrap.tests-green,
                 wrap.mirror-sha-match, wrap.linear-state-updated
/verify          verify.provenance, verify.child-completion,
                 verify.perceptual-evidence, verify.invariance,
                 verify.milestone-aggregation
/retro           retro.doc-sealed
```

---

## 3 · Surfaced items

### 3.1 · CLI-side P2/P3 deferral (D3.3 §CLI limitation)

D3.3's perceptual predicate set is `{P1 artifact-exists, P2 re-run-exits-zero, P3 byte-stable, P4 transcript-schema (api-boundary only)}`. The standalone CLI cannot generically re-run arbitrary test runners (it doesn't know the project's test command), so:

* **The CLI implements P1 and P4 in `_evaluate_perceptual_evidence`.**
* **P2 and P3 are deferred to /verify-skill context**, which has the project's test command in scope. The CLI records the pre-test sha as evidence; the /verify skill supplies the post-test sha and compares.

This is consistent with how D3.3 §Verify-time procedure §3 is worded (the skill orchestrates the rerun; the CLI provides the gating shape). It is **not** consistent with D4.5's §Reconciliation table line for `perceptual-evidence-missing/byte-stability-failed`, which assumes the CLI does the comparison. **Reconciliation-queue item.**

### 3.2 · Invariance P8 timeout

`_evaluate_invariance` re-runs the configured `pass_set_capture_command` via `subprocess.run(..., timeout=300)`. The 300-second timeout is a load-bearing default that suits a typical pytest invocation but may be too small for slow test suites. **Surfaced for v0.2.x:** a `docs/.solo-config.json` field `invariance.pass_set_capture_timeout_seconds` to make this configurable per-product.

### 3.3 · `solo-verify build-finalize` is load-bearing

`stop-orchestrator.sh` (Child 0001-C deliverable) dispatches `solo-verify build-finalize <ticket>` on the Stop hook when the orchestrating Claude reaches its turn limit (D2.2 §Critical caveats #1, the `max_turns` gap). This alias maps to `_run_stage("build", ticket, single_gate="build.finalize")` — it deliberately bypasses `build.provenance` because the orchestrator may have been interrupted mid-iteration with the chain still intact upstream of /build.

Predicates for `build.finalize` (per AC-9):
* `fix_plan_unchecked_count == 0` in the latest `.ralph/<ticket>/backpressure.jsonl` entry.
* Every entry in `failing_test_seed[]` is in the passing set.
* The wrap-commit exists (`git cat-file -e <sha>`).

The CLI checks all three. The first surfaces `§build-finalize-incomplete` (no backpressure log yet); the second surfaces `§build-test-drift`; the third is `§build-finalize-incomplete/commit-absent`. **Confirm against Child 0001-B amendment** (build-SKILL-amendments.md §AC-9 split).

### 3.4 · Python 3.10+ floor verified (D4.0)

Uses:
* `match`/`case` (3.10) — see `main()` for command dispatch.
* PEP 604 union syntax `dict | None`, `int | str` — throughout.
* `dataclasses` with `frozen=True` for `HaltCard` and `GateSpec`.
* `pathlib.Path` with structural type hints.
* Version gate at module load: `sys.version_info < (3, 10)` exits with code 2 and an actionable message.

No third-party deps. No `pip install`. The script is single-file and executable (`chmod +x`).

### 3.5 · `§evaluator-internal-error` and `§cascade-fs-inconsistent` — novel halt codes

Two halt forms emitted by the CLI that do **not** appear in `halt-messages.md` (Child A) or `halt-messages-append-childC.md`:

* `§evaluator-internal-error` — emitted when a per-gate evaluator raises an unexpected exception. Routed to EXIT_HALT (1); the halt card includes the exception class and the traceback's first line.
* `§cascade-fs-inconsistent` — emitted to stderr (not as a halt card) when `.cascade/manifests/` is absent at any stage command. Routes to EXIT_FS_INCONSISTENT (4).

**Reconciliation-queue item:** add a `halt-messages-append-childD.md` adjunct in Child 0001-E so these become first-class halt-card entries with the canonical §recovery text. The CLI emits them today with sensible defaults; the spec needs to canonicalize them.

### 3.6 · Halt-card aggregation ordering

`_render_halt_card` uses **first-by-firing-order** as the "primary halt" gate. The gates fire in the order declared in `STAGE_ORDER[stage]` (which is the same order they appear in `--list-gates <stage>`). D3.4 §Aggregation rules says "most-upstream gate's first halt" — these two are equivalent given `STAGE_ORDER` is the trigger ordering. **Confirmation item, not a discrepancy.**

### 3.7 · `solo-verify subagent <agent_id>` heuristic

The `subagent` alias derives the parent ticket from the agent_id by matching `^(.+)-(user|engineer|pm|skeptic)$`. If the agent_id doesn't match the convention, the CLI falls back to treating the whole agent_id as the ticket. **Surfaced item:** D2.2 §Hook/script table does not strictly specify the agent_id format. If the four-hat skill (Child 0001-B continuation 1) names agents differently, this regex will misroute. Confirm against `review-SKILL-amendments.md` §agent naming convention before sealing v0.2.

### 3.8 · `--reconcile` is drift-detection only in v0.2

Per D4.5 §What v0.2 does not ship, repair-on-confirm is v0.2.x. The CLI's `_reconcile_stage` therefore:

1. Re-runs the stage's gates with `single_gate=None`.
2. For each gate that halted, emits a "proposed repair" line summarizing what change to the on-disk state would resolve the halt.
3. With `--yes`, the CLI does NOT apply repairs; it logs that repair-application is v0.2.x.
4. Returns the halt's exit code (1 or 3) — `--reconcile` is a diagnostic operation, not a state-mutating one.

If Child 0001-E surfaces a desire for v0.2 to ship even rudimentary repair (e.g. "rewrite run-state.json from the latest manifest's sha"), that requires explicit ratification by F-Rev-2 — the v0.1 carry-forward did not authorize it.

### 3.9 · Walking-skeleton perceptual artifact contract

The single [perceptual] failing-test in the seed is intentionally failing pre-/build. The artifact `docs/specs/0001-v0.2-cascade-integration/perceptual/solo-verify-list-gates.txt` must be sealed at /build's at-write trigger with:

```bash
solo-verify --list-gates > docs/specs/0001-v0.2-cascade-integration/perceptual/solo-verify-list-gates.txt
```

That command's output is the byte-stable perceptual evidence. Post-/build, the [perceptual] test compares re-captured stdout to sealed bytes and passes on byte-equality. The capture command itself goes in the /specify manifest's `outputs.perceptual_artifact.capture_command` field for D3.3 §P2-P3 chain-tracking.

### 3.10 · 4-hat objection-coverage gate is a *command-type* hook (D3.4 reframing)

The handoff prompt named `four-hat-objection-coverage` as a SubagentStop *agent-type* hook. In practice it is a **command-type Python script** at `.claude/hooks/four-hat-objection-coverage.py` (Child 0001-C delivered it as such), invoked by `solo-verify subagent <agent_id>` after the four-hat skill seals. The CLI dispatches the gate; the Python script implements the predicate. This is a non-breaking framing change, but worth flagging for the Child 0001-E §README pass.

---

## 4 · Reconciliation-queue additions

Carry forward to the project-level reconciliation queue (per D4.5 §Reconciliation primitives):

1. **Add `§evaluator-internal-error` and `§cascade-fs-inconsistent` to `halt-messages.md`** with canonical recovery text. Owner: Child 0001-E.
2. **`docs/.solo-config.json` schema addition: `invariance.pass_set_capture_timeout_seconds: int` (default 300).** Owner: Child 0001-E (config schema sealing).
3. **Confirm four-hat agent_id naming convention** against Child 0001-B review-SKILL-amendments.md §agent naming. If the convention diverges from `<ticket>-{user|engineer|pm|skeptic}`, update the `solo-verify subagent` regex in §12 main() match block. Owner: Child 0001-E.
4. **D4.5 §Reconciliation table edit**: clarify that the `perceptual-evidence-missing/byte-stability-failed` row's "CLI behavior" column is "deferred to /verify skill" rather than "CLI re-runs the test" (per §3.1 above). Owner: Child 0001-E.
5. **D2.1 v2 §AC-hash chain** — the CLI's `_ac_list_sha256_from_spec` regex `^#{1,3}\s+acceptance\s+criteria\s*$` accepts H1/H2/H3 headings case-insensitively. D2.1 v2 only shows `## Acceptance Criteria` (H2). The CLI is permissive by design; **confirm permissiveness is intentional** in Child 0001-E's spec-template pass.
6. **D4.0 §Gate count** — change "~22 gates" prose to "28 gates" or note the AC-9/AC-10 split as the source of the higher count. Owner: Child 0001-E.

---

## 5 · Handoff prompt for Child 0001-E

> **Title:** 0001 integration spec Child 0001-E — `CLAUDE.md` + `README.md` + `docs/templates/CLAUDE.md` lockstep update + reconciliation-queue close.
>
> **Task:** Per spec AC-16 (the lockstep-update invariant for the founder-facing docs), edit:
>
> * `CLAUDE.md` (repo root) — add §"v0.2 cascade integration" with the 9-stage flow, the 28-gate inventory, the 4 hook-invocation aliases, and the exit-code table. Cross-reference D3.4 §`solo-verify` CLI surface.
> * `README.md` — add §"Verify gates" with a one-paragraph summary and a link to `tools/solo-verify --list-gates`. Don't duplicate D3.4's content; link to it.
> * `docs/templates/CLAUDE.md` — the per-product CLAUDE template. Add the v0.2-specific §"How the cascade fires" boilerplate that downstream products copy when they `/onboard`. Cross-reference D2.1 v2.1's `.cascade/run-state.json` path.
>
> Then process the reconciliation-queue items from Child 0001-D §4 — close them in halt-messages.md, D4.5, D4.0, or as new docs under `docs/templates/`. The reconciliation-queue is the source of truth for "what Child 0001-D surfaced but did not finalize."
>
> **Phase:** Child 0001-E (capability-cluster strategy — the perceptual artifacts are the lockstep-updated CLAUDE.md, README.md, and docs/templates/CLAUDE.md files themselves, byte-stable against their seal).
>
> **Deliverables:**
>
> * `CLAUDE.md`, `README.md`, `docs/templates/CLAUDE.md` — patched, in-tree.
> * `halt-messages-append-childE.md` — the §evaluator-internal-error and §cascade-fs-inconsistent entries.
> * `child_E_lockstep_update_notes.md` — surfaced items, queued items for v0.2.x.
>
> **Read first** (use `project_knowledge_search`):
>
> * `00_PROJECT_INSTRUCTIONS.md`
> * All Child 0001-D deliverables (this session) — the CLI surface, the test seed, this notes file.
> * All Child 0001-C deliverables — the hook contracts referenced from CLAUDE.md.
> * All Child 0001-B deliverables — the per-stage skill amendments that CLAUDE.md must summarize.
> * `D3.4_gate_definitions.md` — the gate-table source.
> * `D4.5_reconciliation_primitives.md` — the carry-forward semantic.
> * `D4.0_solo_verify_build_distribution.md` — Python 3.10+ floor disclosure.
> * `spec.md` AC-16 (lockstep-update invariant).
>
> **Surfaced items to address in Child 0001-E's session** (from Child 0001-D §4):
>
> 1. Add `§evaluator-internal-error` and `§cascade-fs-inconsistent` to halt-messages.md.
> 2. Add `invariance.pass_set_capture_timeout_seconds` to docs/.solo-config.json schema.
> 3. Confirm four-hat agent_id naming convention; patch `solo-verify subagent` regex if it diverges.
> 4. Clarify D4.5 §Reconciliation table re: CLI-side P2/P3 deferral.
> 5. Reconcile D4.0's prose gate count ("~22") with the actual 28.
> 6. Confirm `_ac_list_sha256_from_spec`'s permissive heading regex matches D2.1 v2's intent.

---

## 6 · Quick verification

```bash
# Sanity-check the script.
python3 tools/solo-verify --list-gates
python3 tools/solo-verify --explain build.finalize
python3 tools/solo-verify --explain verify.perceptual-evidence

# Run the failing-test seed.
python3 -m unittest discover tests/solo-verify/ -v

# Seal the walking-skeleton perceptual artifact (done by /build).
mkdir -p docs/specs/0001-v0.2-cascade-integration/perceptual
python3 tools/solo-verify --list-gates \
  > docs/specs/0001-v0.2-cascade-integration/perceptual/solo-verify-list-gates.txt

# Re-run the seed — now the [perceptual] entry passes.
python3 -m unittest discover tests/solo-verify/ -v
```

---

## 7 · Notes on shape, not just substance

A few things I tightened that may matter for downstream readers:

* **The script is one file, intentionally.** D4.0 prescribes single-file distribution. Splitting helpers into a `solo_verify_lib/` package would be cleaner but would force a `python -m solo_verify_lib` invocation pattern, breaking the hook contracts in Child 0001-C which all `exec` `solo-verify` directly.
* **`GateSpec.evaluator` is a `Callable` field on a frozen dataclass.** This works because Python's `dataclasses.field(default=None, repr=False)` lets the dataclass be frozen-and-hashable for the immutable text fields while still attaching the callable. The cleaner alternative — a separate `_EVALUATORS: dict[str, Callable]` lookup — was rejected because it splits the gate's declaration across two locations and makes the `GATES` registry hard to read. The `repr=False` keeps the evaluator out of `--explain`'s output.
* **`StageResult.exit_code` is a `@property`, not a stored field.** The routing logic (provenance halts → 3, fs-inconsistent → 4, else 1 if any halt, else 0) is derived from the halt cards. Storing it would require updating it on every halt append; deriving it is cheap and impossible to desync.
* **Halt-card rendering doesn't import `textwrap`.** A 20-line `_wrap` helper does the job. This keeps the import surface narrow and means a Python install without `textwrap` (rare but possible in some distroless containers) still runs the script.
* **No `argparse.BooleanOptionalAction`.** That's a Python 3.9+ feature but renders awkwardly in `--help`. Plain `store_true` actions for `--reconcile` / `--yes` / `--json` are clearer.

---

End of Child 0001-D notes.
