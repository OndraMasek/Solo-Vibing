# `.claude/skills/build/SKILL.md` — v0.2 amendments

**Status:** Patch-ready amendment block. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing` which reconciles against v0.1 byte-for-byte before applying.

**Scope:** add gate-evaluation logic for three `build.*` gates (provenance pre-flight, pyramid-tampering pre-flight + at-iteration check, test-execution + finalize). Preserve the Ralph backpressure contract from v0.1 verbatim. Append a small "Interaction with sidecar commands" subsection to the existing `/Chains` block for F-Int-3 disposition (the `/cascade-halt` after `/build-kill` flow). The skill's frontmatter, the Ralph iteration loop itself, the `fix_plan` machinery, the lock-acquisition step, the manifest-write step, and the `/Chains` block's Pattern C Group F structure (sealed in `child_B_chains_sections.md`) carry forward from v0.1 unchanged at the substantive level.

**v0.1 reconciliation pattern:** the executing session reads v0.1's `.claude/skills/build/SKILL.md` and substitutes by purpose ("the pre-flight step" / "the Ralph iteration loop" / "the finalize step"). Per `decomposition.md` Child 0001-B's row, "`build.test-execution` is the existing Ralph backpressure contract preserved unchanged" — the executing session does NOT rewrite the loop; the amendment adds the pre-flight and pyramid-tampering gates around the loop and the finalize gate after it.

---

## Naming reconciliation note

D3.4 §Per-stage gate inventory `/build` row names three gates: `build.provenance`, `build.test-execution`, `build.finalize`. The parent `spec.md` AC-9 lists three gates: `build.provenance`, `build.pyramid-tampering`, `build.test-execution`. Same three gates by intent with one rename: D3.4's `build.finalize` covers AC-9's `build.test-execution`-at-finalize semantics, while AC-9 separates `build.pyramid-tampering` as its own gate name (D3.4 folds pyramid-tampering into `build.provenance`'s predicate set per the row text "`pyramid_shape` and per-entry `tag` from the spec markdown match the sealed manifest (no post-seal drift)").

The amendment below treats pyramid-tampering as a **distinct named gate** (`build.pyramid-tampering`) for `solo-verify` parity and per-AC-9-naming, while preserving D3.4's predicate composition. Concretely, this session names four `build.*` gates: `build.provenance`, `build.pyramid-tampering`, `build.test-execution`, `build.finalize`. The split lets `solo-verify --explain build.pyramid-tampering` surface the D3.2 §Downstream consumer touch-points predicate text directly. **Surfaced item in authoring notes.**

---

## Gate evaluation

Four gates fire at `/build` across pre-flight, per-iteration, and finalize triggers per D3.4 §Per-stage gate inventory `/build` row + AC-9 split. Pre-flight gates evaluate before the Ralph loop starts; `build.test-execution` is the loop itself (one evaluation per iteration); `build.finalize` runs after the loop terminates and before manifest seal.

```text
GATES_AT_BUILD_PREFLIGHT = ["build.provenance", "build.pyramid-tampering"]
GATES_AT_BUILD_ITERATION = ["build.test-execution"]
GATES_AT_BUILD_FINALIZE  = ["build.finalize"]

# Pre-flight
for gate in GATES_AT_BUILD_PREFLIGHT:
    evaluate; record per-gate result; do NOT short-circuit
if any pre-flight gate has failing predicates:
    compose aggregate halt card per D3.4 §Aggregation rules
    do NOT enter the Ralph loop
    exit with halt

# Ralph loop (v0.1 contract preserved)
loop:
    invoke build.test-execution evaluation (the existing v0.1 per-iteration check)
    if build.test-execution halts (drift detection):
        write iteration-level diagnostic
        halt the loop
    if fix_plan_unchecked_count == 0 AND failing_test_seed_status all "passing":
        break  # loop terminates normally

# Finalize
for gate in GATES_AT_BUILD_FINALIZE:
    evaluate; record per-gate result; do NOT short-circuit
if any finalize gate has failing predicates:
    compose aggregate halt card; do NOT write manifest; exit with halt
else:
    write manifest with the v0.2 outputs schema additions
    seal /build
```

### Gate 1 — `build.provenance` (pre-flight; manifest chain to `/plan`)

```text
read cascade:run-state from docs/.cascade/run-state.json

# Step 1: parent manifest must be /plan (or /update-linear; both seal the plan chain)
expected_parent_path ← cascade:run-state.last_completed_stage.postcondition_manifest_path
if expected_parent_path absent or path doesn't resolve to a file:
    FAIL with §provenance-chain-broken
    diagnostic: f"expected parent manifest at {expected_parent_path}; absent"
    continue

# Step 2: recompute manifest sha
recomputed_sha ← sha256 of parent manifest with manifest_sha256 field zeroed
expected_sha   ← cascade:run-state.last_completed_stage.postcondition_manifest_sha256
if recomputed_sha != expected_sha:
    FAIL with §provenance-chain-broken
    diagnostic: f"parent manifest sha mismatch at {expected_parent_path}"
    continue

# Step 3: parent must be /update-linear or /plan (the auto-fire chain's last step is /update-linear)
parent_outputs ← parse parent manifest's outputs
if parent_outputs.stage not in {"/plan", "/update-linear"}:
    FAIL with §provenance-chain-broken
    diagnostic: f"/build's upstream must be /plan or /update-linear; got stage='{parent_outputs.stage}'"
    continue

# Step 4: ac_list_sha256 recomputes against current spec
spec_path        ← parent_outputs.spec_path (transitively from /plan's input_provenance)
current_ac_sha   ← sha256 of canonicalized AC list from spec_path's §Acceptance criteria
sealed_ac_sha    ← parent_outputs.ac_list_sha256
if current_ac_sha != sealed_ac_sha:
    FAIL with §ac-list-drift
    diagnostic: f"AC list at {spec_path} has changed since upstream sealed; sealed sha {sealed_ac_sha[:12]}..., current {current_ac_sha[:12]}..."

# Step 5: four_hat_seal_sha256 binding (if /review ran)
if parent_outputs.four_hat_seal_sha256 is present:
    if current_ac_sha != parent_outputs.four_hat_seal_sha256:
        FAIL with §four-hat-seal-broken
        diagnostic: f"AC list differs from /review's four_hat_seal_sha256; spec edited between /review and /build without re-sealing"
```

Halt codes: `§provenance-chain-broken`, `§ac-list-drift`, `§four-hat-seal-broken`. The first is in Child A's halt-messages-append.md; the second and third are pre-existing v0.1 halts (the F-2 fix per D2.1 v2 §Provenance binding ships them in v0.1).

### Gate 2 — `build.pyramid-tampering` (pre-flight; D3.2 §Downstream consumer touch-points)

This gate fires at `/build`'s pre-flight AND fires again as a PreToolUse hook on every seed-file Write tool invocation during the Ralph loop. The pre-flight check catches drift between the sealed parent manifest and the current spec's §Failing-test seed; the PreToolUse hook catches mid-iteration tampering (a Ralph iteration that tries to edit the seed file mid-loop).

#### Pre-flight check

```text
# Step 1: read pyramid_shape and per-entry tag set from parent manifest
parent_pyramid_shape ← parent_outputs.pyramid_shape   # may be null for hybrid child
parent_seed_tags     ← {entry.tag for entry in parent_outputs.failing_test_seed}

# Step 2: parse the current spec markdown
spec_path     ← parent_outputs.spec_path
current_seed  ← parse §Failing-test seed from spec_path
current_tags  ← {entry.tag for entry in current_seed}

# Step 3: tag set must match
if parent_pyramid_shape is not None and current_tags != parent_seed_tags:
    FAIL with §pyramid-tampering-detected
    diagnostic: f"§Failing-test seed tag set has drifted since /specify seal; sealed tags={sorted(parent_seed_tags)}; current tags={sorted(current_tags)}; the seed is the backpressure contract and cannot mutate between /specify seal and /build start"

# Step 4: per-entry name + tag must match sealed entries
for sealed_entry in parent_outputs.failing_test_seed:
    current_entry ← lookup sealed_entry.name in current_seed
    if current_entry is absent:
        FAIL with §pyramid-tampering-detected
        diagnostic: f"sealed test '{sealed_entry.name}' has been removed from §Failing-test seed since /specify seal"
        continue
    if current_entry.tag != sealed_entry.tag:
        FAIL with §pyramid-tampering-detected
        diagnostic: f"sealed test '{sealed_entry.name}' tag has changed: sealed='[{sealed_entry.tag}]', current='[{current_entry.tag}]'"
```

Halt code: `§pyramid-shape-violation/shape-tampering` (the sub-case authored in Child A's halt-messages-append.md). Recovery: `/specify <MARKER>-N --unseal`, re-seal under the corrected seed.

#### PreToolUse hook predicate

The pre-flight check runs once at `/build`'s start; the PreToolUse hook fires for every Write tool invocation targeting the spec's §Failing-test seed section during the Ralph loop. The hook script is `.claude/hooks/pyramid-tampering.sh` (authored in Child 0001-C); the predicate is identical to the pre-flight Step 3–4 logic above, applied to the in-flight Write's intended content.

On hook failure, the hook emits PreToolUse's `hookSpecificOutput` shape (this is NOT a Stop/SubagentStop event — the normal nested-output shape applies):

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "§pyramid-shape-violation/shape-tampering: tag set drift between sealed seed and in-flight Write; <one-line diagnostic>"
  }
}
```

Note the shape divergence from Gate 2 of `/review` (SubagentStop event = top-level-fields-only) — PreToolUse uses the `hookSpecificOutput` wrapper per D2.2 §Stop / SubagentStop output schema quirk. Both shapes are correct for their respective events; the hook script must emit the right shape per event type.

### Gate 3 — `build.test-execution` (per-iteration; Ralph backpressure)

**This gate is the v0.1 Ralph loop verbatim.** Per `decomposition.md` Child 0001-B: "`build.test-execution` is the existing Ralph backpressure contract preserved unchanged." The amendment renames the v0.1 per-iteration check from whatever ad-hoc identifier it carried to `build.test-execution` for `solo-verify` parity; the predicate logic is unchanged.

```text
per_iteration_check (Ralph loop body, v0.1 contract):
    # Run tests in failing_test_seed[] using the configured runner
    test_outcomes ← run failing_test_seed against the current commit
    append outcomes to backpressure_log at .ralph/<ticket>/backpressure.jsonl

    # First-FAIL hash drift detection per D2.1 v2
    first_fail_hash ← sha256 of (first failing test name + first failing test output stderr)
    if first_fail_hash matches the prior iteration's first_fail_hash:
        # Drift: the same test is failing identically iteration-after-iteration
        # The model is stuck on this failure
        FAIL with §build-test-drift
        diagnostic: f"first-FAIL hash unchanged across last <N> iterations; test '{first_failing_test}' produces identical stderr each run; manual intervention required"
```

Halt code: `§build-test-drift`. Recovery: founder reviews `.ralph/<ticket>/backpressure.jsonl` and either fixes the stuck test manually OR `/cascade-halt`s the build per the §Interaction with sidecar commands subsection below.

The fix_plan machinery (v0.1 `.ralph/<ticket>/fix_plan.md` with `[x]`/`[ ]` checkboxes) drives the Ralph loop's termination. When `fix_plan_unchecked_count == 0` AND every entry in `failing_test_seed_status[]` recomputes to `passing`, the loop exits normally.

### Gate 4 — `build.finalize` (at-write; D2.1 v2 `/build` finalize row)

After the Ralph loop terminates, `build.finalize` evaluates the manifest-write preconditions per D2.1 v2 `/build` finalize row.

```text
# Predicate 1: fix_plan_unchecked_count == 0
fix_plan ← read .ralph/<ticket>/fix_plan.md
unchecked ← count of "[ ]" entries in fix_plan
if unchecked > 0:
    FAIL with §build-finalize-incomplete
    diagnostic: f"fix_plan has {unchecked} unchecked entries; Ralph loop terminated without resolving every item"

# Predicate 2: every test in failing_test_seed_status[] recomputes to "passing"
test_outcomes ← run failing_test_seed one final time
for entry in failing_test_seed_status:
    if entry.status != "passing":
        FAIL with §build-finalize-incomplete
        diagnostic: f"test '{entry.name}' status is '{entry.status}'; expected 'passing' at finalize"

# Predicate 3: commit_sha exists in git
commit_sha ← current HEAD's sha
git_log ← git rev-list --max-count=1 HEAD
if commit_sha not in git_log:
    FAIL with §build-finalize-incomplete
    diagnostic: f"commit {commit_sha[:12]}... not present in git; the build did not commit its work"

# Predicate 4: branch checked out matches /build spawn manifest's branch
branch ← current git branch
spawn_branch ← .ralph/<ticket>/spawn-manifest.json's branch
if branch != spawn_branch:
    FAIL with §build-finalize-incomplete
    diagnostic: f"branch drift: spawned on '{spawn_branch}', currently on '{branch}'"

# Predicate 5: lock releases match acquisitions per D2.1 v2 §lock_releases[]
acquired ← read .solo-locks/ for locks acquired by this build session
released ← parse lock_releases[] from in-memory finalize state
if set(acquired) != set(released):
    FAIL with §build-finalize-incomplete/lock-imbalance
    diagnostic: f"lock imbalance: acquired={sorted(acquired)}, released={sorted(released)}"
```

Halt code: `§build-finalize-incomplete`. Recovery: founder reviews the failing predicate's diagnostic and either runs `/build <MARKER>-N --continue` (resumes the Ralph loop) or `/cascade-halt` to terminate the build.

---

## Manifest write (on all-gates-pass)

Write the `/build` finalize manifest at `.cascade/manifests/<ticket>-build.json` per D2.1 v2 `/build` finalize row:

```json
{
  "stage": "/build",
  "ticket": "<MARKER>-<N>",
  "build_sealed_at": "<ISO-8601 timestamp>",
  "outputs": {
    "branch":                  "<branch name>",
    "commit_sha":              "<sha>",
    "iteration_count":         <N>,
    "cost_usd":                <float>,
    "backpressure_log_paths":  [".ralph/<ticket>/backpressure.jsonl"],
    "fix_plan_unchecked_count": 0,
    "failing_test_seed_status": [
      {"name": "...", "tag": "...", "status": "passing", "artifact_path": "..."},
      ...
    ],
    "lock_releases":           [...]
  },
  "input_provenance": {
    "spec_path":                  "...",
    "ac_list_sha256":             "...",
    "four_hat_seal_sha256":       "...",
    "parent_manifest_path":       ".cascade/manifests/<ticket>-update-linear.json (or -plan.json)",
    "parent_manifest_sha256":     "..."
  },
  "manifest_sha256": "<recomputed-zero-self-field>"
}
```

The v0.2 schema additions per D3.3 §Manifest schema additions — `failing_test_seed_status[].artifact_path` for `[perceptual]` entries — propagate from the parent's `failing_test_seed[]` `artifact_path` field. After the Ralph loop terminates, the artifact at `artifact_path` SHOULD exist on the filesystem; `/verify` re-reads it for the byte-stability predicate (P3).

After write, update `cascade:run-state.json`'s `last_completed_stage` to point at this manifest path and sha.

---

## Append to `/Chains` block — F-Int-3 disposition

The existing `/Chains` block (sealed in `child_B_chains_sections.md` as Pattern C Group F variant) describes the per-ticket build+wrap cycle. Append the following subsection at the end of that block for F-Int-3 (per D2.3 v1.2 four-hat review):

```markdown
### Interaction with sidecar commands

`/build-kill <ticket>` (per D4.2 spec) may fire from a sidecar chat while the Group F chat is mid-Ralph. Per F-Int-3 resolution (D2.3 v1.2 amendment landed in §Group F per-skill semantics):

- `/build-kill` writes `cascade:run-state.kill_in_progress = "<ticket>"` AND increments `cascade:run-state.queue_version` in a single write.
- The Group F chat's Stop hook (per the single-orchestrator pattern in D2.2 §Stop hook orchestrator) reads `kill_in_progress` at every Ralph-iteration safe boundary. If set for the active ticket, the orchestrator halts the chat with the chat-end card framed as "remote kill received" per halt §kill-received-remote (authored in v1.2 §Group F per-skill semantics).
- After surfacing the halt card, the Stop hook clears `cascade:run-state.kill_in_progress` and removes the ticket from `active_stages[]`. The next chat opened detects the cleared flag and the queue_version increment.
- **`/cascade-halt`** (founder-initiated, not `/build-kill`) is the alternative recovery path for a stuck Ralph loop where `§build-test-drift` has fired and manual intervention is required. `/cascade-halt` writes `cascade:run-state.manual_halt = "<ticket>"` (without kill_in_progress); the Stop hook respects the same orchestrator logic but the halt-card framing is "manual halt requested" per §manual-halt-pending. After founder review, the founder either re-runs `/build <ticket> --continue` (resuming the loop) or `/cascade-halt --abandon <ticket>` (formal abandon path; v0.2.x consideration per the prior session's queued items).

The two flags (`kill_in_progress` for remote kill, `manual_halt` for founder halt) are mutually exclusive; setting one clears the other. The Stop hook orchestrator's dispatch logic per Child 0001-C handles both flags.
```

---

## Cross-references

- **D2.1 v2 §`/build` (spawn) and `/build` (finalize) rows** — the upstream manifest schema and verifier-predicate baseline; D3.4's four gates layer on top.
- **D2.1 v2 §Provenance binding (F-2 fix)** — the AC-list-hash chain and `four_hat_seal_sha256` binding enforced by Gate 1 Steps 4–5.
- **D2.2 §Stop / SubagentStop output schema quirk** — the PreToolUse `hookSpecificOutput` wrapper shape (distinct from SubagentStop's top-level shape); Gate 2's hook script emits this correctly.
- **D2.2 §Hook/script surface** — the PreToolUse matcher on seed-file Write tool; pyramid-tampering.sh wires here.
- **D2.3 v1.2 four-hat review §F-Int-3** — the binding for the Interaction-with-sidecar-commands subsection; this amendment lands the disposition.
- **D3.2 §Downstream consumer touch-points** — the binding for `build.pyramid-tampering`'s pre-flight predicate.
- **D3.3 §Manifest schema additions** — the `artifact_path` field propagation through `failing_test_seed_status[]`.
- **D3.4 §Per-stage gate inventory `/build` row** — the gate firing order and predicate references.
- **D3.4 §Aggregation rules** — all-gates-evaluate, single-card-aggregate semantics applied to /build's pre-flight, iteration, and finalize halts.
- **Child A `halt-messages-append.md`** — fourteen new halts; this amendment references `§pyramid-shape-violation/shape-tampering`, `§provenance-chain-broken` by halt-code.
- **`child_B_chains_sections.md`** Pattern C Group F variant (`/build` + `/wrap`) — the `/Chains` block this amendment appends a subsection to.
- **Child 0001-C** `.claude/hooks/pyramid-tampering.sh` — the PreToolUse hook script wrapping Gate 2's predicate.
- **Child 0001-C** `.claude/hooks/stop-orchestrator.sh` — the single Stop hook orchestrator that reads `kill_in_progress` and `manual_halt` per the Interaction-with-sidecar-commands subsection.
- **D4.2** `/build-kill` spec — referenced in the Interaction-with-sidecar-commands subsection; the v1.2 amendment is the binding source.
- **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-9** — this skill amendment satisfies AC-9 as authored, modulo the four-vs-three gate split surfaced as Item #2 in the authoring notes.
