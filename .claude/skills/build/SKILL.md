---
name: build
description: Execute a sealed child ticket via a fresh-context Ralph loop, then invoke build-reviewer and chain to /wrap on green. Preconditions enforce parent scope:planned + child scope:sealed + spec checksum + no live collision. Produces PROMPT.md + AGENTS.md + fix_plan.md + run.sh under .ralph/<MARKER>-N-K/; spawns bash loop with fresh Claude Code context per iteration until acceptance criteria flip green and the failing-test seed passes. On Ralph success, invokes build-reviewer agent (halt-on-any-finding in v0.1); on build-reviewer DONE flips AC checkboxes + scope:built label and chains to /wrap. User-invoked, not auto-fired. Linux / macOS / WSL only. Fires on "/build <MARKER>-N-K", "build <MARKER>-N-K", "ralph <MARKER>-N-K". Modes: --continue (resume), --reset --confirm (archive + force-with-lease), --dry-run (artifacts only), --status (read-only), --finalize (invoke reviewer + chain), --kill (SIGTERM + cleanup), --sync (retry Linear write).
---

# build

Execute a sealed child ticket via a fresh-context Ralph loop. Re-entry into the cascade — Ralph runs cost real money and produce real commits, so the go signal is always explicit. References rules: `naming.md`, `scope-labels.md`, `write-discipline.md`, `completion-status.md`, `auditor-stance.md`. Invokes agent: `build-reviewer`. Chains to skills via Task tool: `start` (at preconditions), `wrap` (on success after build-reviewer DONE).

## Trigger

- User: "/build <MARKER>-N-K", "build <MARKER>-N-K", "ralph <MARKER>-N-K"
- Resume: "/build <MARKER>-N-K --continue" — resume from current `.ralph/<MARKER>-N-K/fix_plan.md` state; re-verifies spec checksum before resuming
- Reset: "/build <MARKER>-N-K --reset --confirm" — archives current `.ralph/<MARKER>-N-K/` and force-with-leases the branch back to default HEAD; the `--confirm` flag is mandatory because force-push is destructive
- Dry-run: "/build <MARKER>-N-K --dry-run" — generates all artifacts and halts before spawning the loop
- Status: "/build <MARKER>-N-K --status" — read-only state query (PID alive? iteration count? wall-clock? cumulative cost?); on detected exit, recommends `--finalize`
- Finalize: "/build <MARKER>-N-K --finalize" — post-exit: invokes build-reviewer, on DONE writes scope:built label + AC flips + completion comment, then chains to /wrap
- Kill: "/build <MARKER>-N-K --kill" — SIGTERM the loop, clean up lockfile and PID file
- Sync: "/build <MARKER>-N-K --sync" — retry Linear write if `--finalize` succeeded locally but the Linear API call failed

## Behavior — spawn phase

### Preconditions (any failure halts with `BLOCKED` per `completion-status.md`, halt-card rendered per `docs/templates/halt-messages.md`)

- **Platform.** Linux, macOS, or WSL. Bash, `jq`, `git`, `claude` CLI, `bc` required. Windows native not supported.
- **Ticket.** Child <MARKER>-N-K exists in Linear and carries label `scope:sealed` per `scope-labels.md`. Mismatch → `BLOCKED` citing observed vs expected per `scope-labels.md` §Refusal protocol on stale labels.
- **Parent.** Parent ticket <MARKER>-N exists, carries label `scope:planned` per `scope-labels.md`, and links to a spec at `docs/specs/NNNN-<slug>/spec.md` per `naming.md`.
- **Four-hat clearance** (load-bearing). The parent's four-hat Linear document `[<MARKER>-DOC-NNNN] four-hat: <MARKER>-N <title>` per `naming.md` exists, and every finding in its most recent iteration has a recorded resolution (Incorporate / Defer / Reject). Unresolved findings → `BLOCKED`.
- **Spec checksum** (load-bearing). The four-hat document records `spec_sha256` (16-char prefix) at seal time per `[SOL-SKILL] specify` step 7. Current `sha256(docs/specs/NNNN-<slug>/spec.md)` must match the sealed value. Mismatch → `BLOCKED` with "spec drift, re-seal four-hat via `/specify <MARKER>-N --unseal` or revert spec".
- **Ticket-AC text matches spec** (load-bearing). The ticket's AC checkbox text must match the spec's Acceptance criteria section verbatim (text only — checkbox state is allowed to differ; /build flips it). Mismatch → `BLOCKED` per `§ticket-ac-drift`: "Ticket AC text was edited away from spec.md. Edit `spec.md` (the canonical source), then `/specify <MARKER>-N --continue` to re-mirror the ticket. Direct edits to ticket AC text are not supported."
- **Failing-test seed.** Parses to at least one named test function for which a runner command exists in repo config.
- **Git.** Working tree clean. Current branch is project default OR target branch `<MARKER>-N-<slug>-K` per `naming.md` already exists.
- **No live collision.** If `.ralph/<MARKER>-N-K/run.pid` exists AND that PID is alive → `BLOCKED`: "Ralph already running for this ticket. Use `--status`, `--kill`, or wait."
- **Config.** `docs/.solo-config.json` declares a `ralph` block with `max_iterations`, `max_wall_hours`, `max_usd_cost` (defaults: 30 / 4 / 50). Auto-created with defaults if absent.
- **Sandbox.** Isolation boundary in place (devcontainer / Docker / VM / worktree). The skill does not provide isolation — assumes `docs/onboarding/sandbox.md` documents the chosen pattern. Missing → `NEEDS_CONTEXT`.
- **`.gitignore`.** If `.ralph/` is not listed, auto-add it on first /build invocation in this repo.

### Task-invoke /start

Per audit decision #1, /build owns the Todo → In Progress transition by invoking /start at the preconditions step (via Task tool per audit decision #9). Pass <MARKER>-N-K. /start transitions child Linear state Todo → In Progress and posts a session-start comment.

If /start returns `BLOCKED` or `NEEDS_CONTEXT` (e.g. child already In Progress, or label mismatch /start independently detects), surface its status verbatim and halt /build at the same status. No Ralph spawn.

### Load context

- Child ticket description + AC checkboxes
- Parent spec markdown
- Failing-test seed (source-of-truth for backpressure)
- `docs/constitution.md` (passed to PROMPT.md stack-allocation)
- `docs/onboarding/codebase-map.md` if it exists
- ADRs filtered by ticket scope
- `docs/.solo-config.json` ralph block

### Create branch and ralph directory

- Branch: `<MARKER>-N-<slug>-K` per `naming.md` §Branch names (created from default branch if absent; checked out either way).
- Directory: `.ralph/<MARKER>-N-K/` per `naming.md` §File paths (created clean; on `--reset --confirm`, existing contents move to `.ralph/<MARKER>-N-K/archive/run-v<N>/` first).
- Record the sealed-commit SHA (the commit Ralph started from) to `.ralph/<MARKER>-N-K/sealed.sha` — passed to build-reviewer at finalize time.

### Generate Ralph artifacts (single same-turn batch write per `write-discipline.md`)

- **`.ralph/<MARKER>-N-K/PROMPT.md`** — BUILDING prompt, generated from `docs/templates/PROMPT.md.template`. Stack-allocated identically every iteration. Variables: ticket id/title, paths to `fix_plan.md`, parent spec, `AGENTS.md`, `docs/constitution.md`. Hard-codes "pick the highest-priority unchecked item and implement only that one" (one-item-per-loop) and "no stubs satisfying test text only" (Goodhart on TDD — programmatic enforcement comes via build-reviewer's stub-detection axis at finalize time).

- **`.ralph/<MARKER>-N-K/AGENTS.md`** — concrete project commands, autodetected with precedence:
  1. `package.json` `scripts.{test,typecheck,lint,build,format}`
  2. `Makefile` targets `{test, typecheck, lint, build, format}`
  3. `pyproject.toml` `[tool.poetry.scripts]` / `Cargo.toml` `[package.metadata.scripts]`
  4. Repo-root README sniff for command blocks tagged `## Commands` / `## Development`
  5. `NEEDS_CONTEXT`: "fill in `AGENTS.md` manually, persist defaults to `docs/.solo-config.json` for reuse"
  Generated from `docs/templates/AGENTS.md.template`. Includes "hermetic commands only" guidance (commands must not hit external APIs or leave non-test-scoped artifacts).

- **`.ralph/<MARKER>-N-K/fix_plan.md`** — initial living TODO:
  - Ticket AC checkboxes (one entry per AC, in order)
  - Failing-test seed (one entry per named test that must turn green)
  - Spec's Open Questions section (deferred items, marked `[defer]`, not active)

- **`.ralph/<MARKER>-N-K/run.sh`** — bash loop, generated from `docs/templates/run.sh.template`. Each iteration:
  1. Increment `iteration.counter`; check caps (iteration / wall / cumulative cost).
  2. Spawn `claude --dangerously-skip-permissions --output-format stream-json -p "$(cat PROMPT.md)"` to `iterations/NNN/claude.jsonl`. `run.sh` exports `SOLO_BUILD_AGENT=1` before this spawn, so the build agent (and the PreToolUse hooks of the `claude` it runs) execute in **build-agent context** — the signal `pretool-write-denylist.sh` keys on to enforce the cascade-control denylist against the autonomous loop (incl. shell-redirection writes) while leaving founder-session orchestration stages unblocked. Per spec AC-21 / D4.1 §D4.1.7.
  3. Extract `total_cost_usd` from the final `result` message; accumulate into `cost.usd`.
  4. Grep assistant message blocks for `<promise>BUILT</promise>`.
  5. Run backpressure commands from `AGENTS.md` in declared order; first failure halts backpressure for this iteration; output to `iterations/NNN/backpressure.log`.
  6. Commit if working tree dirty: `[<MARKER>-N-K] iter NNN: <first line of fix_plan diff>`.
  7. **Exit `built`** if completion-promise emitted AND zero unchecked items in `fix_plan.md` AND backpressure all green.
  8. **Exit `iteration_cap` / `wall_cap` / `cost_cap`** if respective cap tripped.
  9. **Drift check.** `drift_hash = sha256(first FAIL|Error|×|✗ line in backpressure.log)[:12]`. Rolling window of last 3 hashes. If 3 identical → `exit.status=drift`.
  Lockfile `.ralph/<MARKER>-N-K/RUNNING` touched on start (surfaces "do not edit fix_plan.md" banner). PID written to `run.pid`. Signal traps on EXIT / INT / TERM release both and write `exit.status=interrupted`.

### Spawn the loop (skipped on `--dry-run`)

- Run `bash .ralph/<MARKER>-N-K/run.sh` detached. PID to `.ralph/<MARKER>-N-K/run.pid`.
- Surface "Ralph running" card:
  - PID, ticket id, sealed-commit SHA
  - Tail one-liner: `tail -f .ralph/<MARKER>-N-K/iterations/$(cat .ralph/<MARKER>-N-K/iteration.counter)/log.txt`
  - "Do not edit `fix_plan.md` while running" banner
  - Hint: `/build <MARKER>-N-K --status` (poll) / `--kill` (cancel)
- Return `DONE` for the spawn phase (Ralph started; finalization happens on a later user-invoked turn).

## Behavior — finalize phase (`--finalize`)

Triggered manually by the founder after `--status` reports Ralph exited. /build does not auto-finalize — per audit decision #9 (no hooks in v0.1) and decision #1 (explicit Task-tool chaining), the founder runs `--finalize` on a separate turn.

1. **Read `exit.status`.** Required: one of `built | iteration_cap | wall_cap | cost_cap | drift | backpressure_unresolved | interrupted`. Empty or missing → `BLOCKED`: "Ralph has not exited; run `--status`".

2. **Halt branches.** If `exit.status` is anything other than `built`:
   - No Linear writes. No build-reviewer invocation. No /wrap.
   - Surface opinionated halt-card per `docs/templates/halt-messages.md`: single recommended next action with one-line rationale, alternatives listed below. Recommendation logic:
     - `iteration_cap` or `wall_cap` with progress in the last 3 iterations → recommend `--continue`
     - `cost_cap` → recommend `--continue` after raising the cap in `docs/.solo-config.json`
     - `drift` → recommend unsealing the parent (`/specify <MARKER>-N --unseal`); a stable failing test means the spec is wrong, and `--reset` won't help
     - `backpressure_unresolved` after 5+ iterations on the same item → recommend `--reset --confirm`
     - `interrupted` → recommend `--continue`
   - Diagnostic comment posted to ticket: exit reason, current `fix_plan.md` snapshot, last three commit SHAs, last failing backpressure output, this-run + cumulative cost.
   - Return `BLOCKED`.

3. **`exit.status=built` branch.** Task-invoke `build-reviewer` agent per `[SOL-AGENT] build-reviewer`. Inputs: child ticket ID + AC list, path to parent spec, sealed-commit SHA from `.ralph/<MARKER>-N-K/sealed.sha`. The agent reads `docs/constitution.md` itself.

4. **Map build-reviewer status to /build status** per `completion-status.md` §Agent contract:
   - Agent returns `DONE` (zero findings) → continue to step 5.
   - Agent returns `DONE_WITH_CONCERNS` — **not reachable in v0.1**: build-reviewer's halt threshold is "any finding". Documented for the v1.1 path (severity-based threshold; see build-reviewer's v0.1 → v1.1 evolution).
   - Agent returns `BLOCKED` (any finding) → halt /build. No Linear writes. Surface findings to founder per halt-messages template (full critique inline, axis-by-axis). Recommend the founder amends `fix_plan.md` manually and runs `/build <MARKER>-N-K --continue`. Return `BLOCKED`.

5. **Build-reviewer passed. /build writes its outputs** per `scope-labels.md` (label ownership) + `write-discipline.md` (same-turn batching):
   - Linear ticket, single batched write: flip all AC checkboxes + atomic label transition `scope:sealed` → `scope:built` (prior label removed in the same write) + post completion comment with iteration count, wall-clock, this-run cost, ticket-cumulative cost (sum across initial + all `--continue` runs), files changed, branch link.
   - Partial-failure handling per `write-discipline.md` §Partial failure: on Linear write failure, drop `.ralph/<MARKER>-N-K/linear.sync.pending`; surface "Linear write failed — run `/build <MARKER>-N-K --sync` to retry". Return `BLOCKED`.

6. **Chain to /wrap via Task tool.** /wrap owns: re-verify AC green, scope verification, final commit + push (green-marker commit on top of Ralph's iteration commits), Linear state transition In Progress → Done, parent-completion check, optional chain to /verify or /retro per workflow knobs.

7. **Return status.** Map /wrap's status to /build's terminal status per `completion-status.md`:
   - /wrap `DONE` → /build `DONE`.
   - /wrap `DONE_WITH_CONCERNS` → /build `DONE_WITH_CONCERNS` with findings forwarded.
   - /wrap `BLOCKED` or `NEEDS_CONTEXT` → /build returns the same status with /wrap's diagnostic forwarded.

Surface success card: iteration count / this-run cost / cumulative cost / wall-clock / final commit SHA / branch link / /wrap's chain result (verify queued? retro fired? next Wave-eligible hint?).

## Reset mode

`/build <MARKER>-N-K --reset --confirm`:

1. List commits on `<MARKER>-N-<slug>-K` not in default branch. Surface to founder as a confirmation card. The `--confirm` flag is mandatory because `git push --force-with-lease` is destructive — the card lists commits about to be discarded so the founder can recover unrecorded work first.
2. Archive current `.ralph/<MARKER>-N-K/` → `.ralph/<MARKER>-N-K/archive/run-v<N>/`.
3. `git push --force-with-lease` to reset branch to default branch HEAD.
4. Re-run preconditions through spawn (no /start invocation — child already In Progress from the initial run; transitioning again would double-write).

Use when Ralph thrashes and `--continue` won't get there.

## Continue mode

`/build <MARKER>-N-K --continue`:

1. Skip artifact generation. Re-validate preconditions — especially spec checksum. If the spec was unsealed and re-sealed since the last run (checksum mismatch), force `--reset --confirm` instead per the four-hat clearance + spec-checksum preconditions.
2. Re-touch `.ralph/<MARKER>-N-K/RUNNING` lockfile; check no live collision.
3. Restart the loop with existing `fix_plan.md` as-is. Iteration counter continues from `.ralph/<MARKER>-N-K/iteration.counter`.
4. Caps apply to the *combined* run (initial + continue). Cumulative cost continues accumulating in `cost.usd`.

Use after an `iteration_cap` or `wall_cap` halt where the diagnostic looks recoverable. Do not use after `drift` — that's reset territory (or, more likely, a re-seal of the parent).

## Status / Kill / Sync modes

- `/build <MARKER>-N-K --status`: read `run.pid`, check liveness, read `iteration.counter`, `cost.usd`, wall-clock. If PID dead AND `exit.status` set, surface "Ralph exited with `<status>`. Run `/build <MARKER>-N-K --finalize` to invoke build-reviewer and complete the cascade." Returns `DONE` (read-only completes successfully).
- `/build <MARKER>-N-K --kill`: SIGTERM the PID. Signal trap writes `exit.status=interrupted`, releases lockfile, cleans up PID file. Returns `DONE`.
- `/build <MARKER>-N-K --sync`: if `linear.sync.pending` exists, retry the Linear update (AC flips + label transition + completion comment); on success remove the marker and, if `--finalize` had not yet reached the /wrap chain, Task-invoke /wrap now. Otherwise no-op. Returns `DONE` on success, `BLOCKED` on continued Linear failure.

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
read cascade:run-state from .cascade/run-state.json

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

## Same-turn write rules

Per `write-discipline.md`:

- Spawn phase: all generated artifacts (PROMPT.md / AGENTS.md / fix_plan.md / run.sh / sealed.sha) in a single batch write. Lockfile and PID file are written by run.sh on its first turn.
- Finalize phase: Linear ticket writes (AC flips + label transition + completion comment) in a single batched call.
- `fix_plan.md` is iteratively updated **by the Ralph loop itself**, not by this skill. The skill writes the initial version once.
- No skill-chaining writes — /build does not write /start's or /wrap's artifacts; chaining is via Task-invocation per audit decision #9.

## Outputs

| Artifact | Location |
|---|---|
| Building prompt | `.ralph/<MARKER>-N-K/PROMPT.md` |
| Project commands | `.ralph/<MARKER>-N-K/AGENTS.md` |
| Living TODO | `.ralph/<MARKER>-N-K/fix_plan.md` |
| Loop script | `.ralph/<MARKER>-N-K/run.sh` |
| Sealed-commit SHA | `.ralph/<MARKER>-N-K/sealed.sha` |
| Iteration counter | `.ralph/<MARKER>-N-K/iteration.counter` |
| Cumulative cost (USD) | `.ralph/<MARKER>-N-K/cost.usd` |
| Live PID | `.ralph/<MARKER>-N-K/run.pid` |
| Running lockfile | `.ralph/<MARKER>-N-K/RUNNING` |
| Exit reason | `.ralph/<MARKER>-N-K/exit.status` |
| Per-iteration logs | `.ralph/<MARKER>-N-K/iterations/NNN/` |
| Linear-sync-pending marker | `.ralph/<MARKER>-N-K/linear.sync.pending` (only on Linear failure) |
| Branch | `<MARKER>-N-<slug>-K` |
| Linear ticket label | `scope:sealed` → `scope:built` (set by /build on build-reviewer DONE) |
| Linear ticket state | In Progress → Done (set by chained /wrap, not by /build) |

## Completion status

Per `completion-status.md`. v0.1 mappings:

- `DONE` — spawn phase: Ralph started, "Ralph running" card surfaced. Finalize phase: build-reviewer DONE, Linear writes succeeded, /wrap returned DONE.
- `DONE_WITH_CONCERNS` — finalize phase: /wrap returned DONE_WITH_CONCERNS (e.g. next-Wave-eligible siblings exist without parallel-session setup). Build-reviewer DONE_WITH_CONCERNS is not v0.1-reachable (halt-on-any-finding); reserved for v1.1.
- `BLOCKED` — preconditions failed; /start halted; Ralph exited non-`built`; build-reviewer findings; Linear write failed; /wrap returned BLOCKED. Halt-card per `docs/templates/halt-messages.md`.
- `NEEDS_CONTEXT` — sandbox boundary missing; AGENTS.md autodetect exhausted; founder must provide context before re-invocation.

## /Chains

**Pattern:** C (auto-fire-chain, Group F variant — chain's first stage; runs in Claude Code per §Execution surface per group)
**Group:** F
**Within-group transitions:** this skill is the first stage in the Group F chain (`/build` → `/wrap`). On `/build` manifest seal at `.cascade/manifests/<ticket>-build.json` (after Ralph completes its iteration cycle, `/build --finalize` runs, and the `build.provenance`, `build.pyramid-tampering`, `build.test-execution` gates per D3.4 §build gates pass), this skill Task-invokes `/wrap` to advance the chain. In Claude Code (per §Execution surface per group), "Task-invoke" is hook-driven: the Stop hook's orchestrator (per D2.2 §Hook resolution #3 single-Stop-hook pattern) reads `/build`'s sealed manifest and dispatches `/wrap`. Build-internal safe boundaries: **per-tool-call grain inside Ralph's iteration** (per D2.3 v1.3 §Within-group safe boundaries Group F row — every `Write` / `Edit` / `Bash` tool call inside Ralph is a hook-enforced PreCompact safe boundary); between Ralph iterations; at `/build --finalize`.
**Group exit trigger:** not this skill. `/build` is a Group F chain intermediate; the chain's exit fires on `/wrap`'s seal.
**Group exit render:** not this skill. Chain-intermediate; after `/build`'s manifest seals, the Stop hook Task-invokes `/wrap` without rendering.
**Next group entry:** not this skill. See `/wrap`'s `/Chains` section for the Group F exit transition (F→F[next-ticket] or F→G).
**Auto-fire compact handling:** **applies.** Per D2.3 v1.3 §Auto-fire compact behaviour, if PreCompact fires at a within-build safe boundary (e.g., between Ralph iterations or after a tool call), the cascade sets `cascade:run-state.next_chain_step = "wrap"` if `/build` is at its final safe boundary (post `/build --finalize`), or to `"build"` if compact fires mid-build (chain-pointer ensures resumption to the same stage). The side-channel snapshot `cascade:run-state.next_chain_step` is also written to `.cascade/session/precompact-<session_id>-<timestamp>.json` per D2.2's side-channel snapshot mechanism. After compact, SessionStart=compact emits the factual block including `next_chain_step`; the first post-compact Stop-hook execution reads `cascade:run-state.next_chain_step` and Task-invokes accordingly (clearing the field after Task-invoke fires).
**Group's exit manifest:** not-this-skill — see `/wrap`. `/build`'s manifest at `.cascade/manifests/<ticket>-build.json` is a chain intermediate, the bridge between the Ralph-iteration-loop's evidence and `/wrap`'s seal. D4.6 v1.1 reads `/wrap`'s manifest for Group F re-derivation, not `/build`'s.

### Interaction with sidecar commands

`/build-kill <ticket>` (per D4.2 spec) may fire from a sidecar chat while the Group F chat is mid-Ralph. Per F-Int-3 resolution (D2.3 v1.2 amendment landed in §Group F per-skill semantics):

- `/build-kill` writes `cascade:run-state.kill_in_progress = "<ticket>"` AND increments `cascade:run-state.queue_version` in a single write.
- The Group F chat's Stop hook (per the single-orchestrator pattern in D2.2 §Stop hook orchestrator) reads `kill_in_progress` at every Ralph-iteration safe boundary. If set for the active ticket, the orchestrator halts the chat with the chat-end card framed as "remote kill received" per halt §kill-received-remote (authored in v1.2 §Group F per-skill semantics).
- After surfacing the halt card, the Stop hook clears `cascade:run-state.kill_in_progress` and removes the ticket from `active_stages[]`. The next chat opened detects the cleared flag and the queue_version increment.
- **`/cascade-halt`** (founder-initiated, not `/build-kill`) is the alternative recovery path for a stuck Ralph loop where `§build-test-drift` has fired and manual intervention is required. `/cascade-halt` writes `cascade:run-state.manual_halt = "<ticket>"` (without kill_in_progress); the Stop hook respects the same orchestrator logic but the halt-card framing is "manual halt requested" per §manual-halt-pending. After founder review, the founder either re-runs `/build <ticket> --continue` (resuming the loop) or `/cascade-halt --abandon <ticket>` (formal abandon path; v0.2.x consideration per the prior session's queued items).

The two flags (`kill_in_progress` for remote kill, `manual_halt` for founder halt) are mutually exclusive; setting one clears the other. The Stop hook orchestrator's dispatch logic per Child 0001-C handles both flags.

## Notes

**Why bash-loop and not the official stop-hook plugin.** Community consensus through Q4 2025 / Q1 2026 (Paddo, HumanLayer, ZeroSync, Arnaldi) is that fresh context per iteration is the durable pattern. The official Anthropic `ralph-loop` plugin keeps Ralph in one session, causing context bleed past ~150k tokens, with documented Docker / jq / Windows issues. Bash-loop with `claude -p` per iteration is what Huntley actually runs to build CURSED.

**Why per-ticket `fix_plan.md`.** Cross-ticket state invites Ralph to drift across feature boundaries. Per-ticket isolation enforces the scope boundary set by /plan and lets parallel /build runs on sibling tickets (v1.1+) share nothing but the codebase.

**Why the four-hat precondition is load-bearing.** Wang's January 2026 critique collapses to: Ralph amplifies bad specs into bad code, fast. The four-hat document is exactly the artifact that catches founder blind spots before code gets written. Not configurable.

**Sandbox responsibility.** `--dangerously-skip-permissions` is required for autonomous operation; tool calls execute without prompts. The skill assumes the founder has an isolation boundary configured per `docs/onboarding/sandbox.md`.

**One-item-per-loop is non-negotiable.** Huntley repeats this three times. The PROMPT.md template hard-codes "pick the highest-priority unchecked item and implement only that one." Relax only after 5+ tickets have run cleanly.

**Cost discipline.** Defaults: 30 iterations, 4 wall-hours, $50 USD per run. Cap is post-iteration, so actual spend can exceed cap by up to one iteration's worth. Cumulative cost across `--continue` runs surfaced in every card.

**Drift detection.** Hash = `sha256(first FAIL line in backpressure.log)[:12]`. Three identical hashes in a row → halt. Usually means the failing-test seed is wrong, which means the spec is wrong, which means `--reset --confirm` won't help — unseal the parent (`/specify <MARKER>-N --unseal`).

**`--dry-run` is the design-review path.** Reading PROMPT.md and fix_plan.md before spawning catches roughly 80% of bad runs. Use it on every first /build against a new ticket type.

**Why `--reset` requires `--confirm`.** `git push --force-with-lease` is destructive. The confirmation card lists commits about to be discarded so the founder can recover unrecorded work first.

**Spec drift guard.** /specify records `spec_sha256` in the four-hat doc at seal time. /build verifies the current spec matches at every spawn and `--continue`. Catches the "edited spec after four-hat sealed it" failure mode.

**Linear sync retry.** `.ralph/<MARKER>-N-K/exit.status` is the source of truth for run state. If the Linear API is down at `--finalize`'s Linear write step, the marker file `linear.sync.pending` is dropped; `/build <MARKER>-N-K --sync` retries on demand per `write-discipline.md` §Partial failure.

**No-stubs prohibition (belt + suspenders).** PROMPT.md template includes the prohibition language ("stubs that satisfy test text without satisfying the AC do not count as complete"). Programmatic enforcement is the build-reviewer agent's stub-detection axis at finalize time. The prompt prevents most stubs; the reviewer catches the rest.

**Why finalize is a separate user-invoked turn.** Ralph loops run hours; chat-Claude cannot block on Ralph completion. Per audit decision #9 (no hooks in v0.1), the chaining mechanism is explicit Task-tool invocation within a skill turn. /build therefore splits into two skill turns: **spawn** (returns immediately with "Ralph running" card) and **finalize** (separate turn invoked by founder after `--status` reports exit). v0.2 may introduce auto-finalize via Stop-hook once the audit-decision-9 constraint is revisited.

**Composition citation.** This skill composes prior art and does not invent: Huntley's Ralph pattern (`ghuntley/how-to-ralph-wiggum`, `ghuntley.com/ralph`); the bash-loop fresh-context variant (Paddo, HumanLayer, ZeroSync writeups, Dec 2025–Jan 2026); the spec-kit + Ralph integration shape (`merllinsbeard/speckit-ralph`, `tzachbon/smart-ralph`); the cascade conventions defined in `[SOL-SKILL] specify` and the post-extraction rules/agents. The contribution here is the integration into a four-hat-gated, Linear-anchored cascade with an explicit build-reviewer gate between Ralph success and /wrap.

## Open questions (deferred to v1.1+)

- **Auto-finalize via Stop-hook.** Revisit audit decision #9 once Claude Code's Stop-hook semantics stabilize. v0.2 candidate.
- **Split into `/build` + `/build-status`.** Skill is monolithic. v1.1 refactor candidate if the spawn/finalize split makes this awkward in practice.
- **Multi-repo support.** v1 is single-repo only. Features spanning multiple repos need a different pattern.
- **Ticket dependency awareness.** Use Linear's "Blocks / Blocked by" relationships as a precondition (refuse to build a ticket whose blockers aren't `scope:built`).
- **`/build --init`.** Interactive bootstrap for first-run config. v1 ships with sane defaults.
- **First-time `--dry-run` prompt.** Heuristic: prompt founder to dry-run when /build fires on a ticket type not yet seen in this repo.
- **`/build-clean`.** Sweep archived runs older than N days from `.ralph/<MARKER>-N-K/archive/`. Repo-hygiene concern.
- **Fan-out: `/build-all-children <MARKER>-N`.** Parallel Ralph across git worktrees, one per unblocked child. Cron-friendly. Deserves dedicated design — sandbox isolation per worktree is non-trivial.
- **Severity-based build-reviewer halt threshold.** Currently /build halts on any build-reviewer finding. v1.1 may relax to halt-on-high, surface low/med as DONE_WITH_CONCERNS. See `[SOL-AGENT] build-reviewer` §v0.1 → v1.1 evolution.
