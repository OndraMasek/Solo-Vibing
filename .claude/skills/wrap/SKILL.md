---
name: wrap
description: Build-session close ritual. Invoked by /build on build-reviewer-pass (Task tool, finalize phase) — verifies tests green, verifies scope, pushes the branch, transitions child Linear state In Progress → Done, posts a session summary, checks parent completion. If all of the parent's children are Done, transitions the parent and Task-invokes /verify or /retro per workflow knobs. No manual Code-Claude session in the canonical v1 flow. Not user-invoked in normal operation. Manual override `/wrap <MARKER>-N-K` for debugging.
---

# wrap

Build-session close ritual. Verifies child completion, persists state, advances the parent if all children are done. References rules: `naming.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`. Invoked by /build via the Task tool. Chains to skills via Task tool: `verify`, `retro`.

## Trigger

Invoked by `/build` on build-reviewer-pass, in /build's finalize phase, via the Task tool (per audit decision #1). /build has, by this point: spawned Ralph, gotten a `built` exit, run the `build-reviewer` agent, and gotten a clean review. /wrap is the next step — commit, push, wave-merge (if applicable), state transition, parent-completion check.

Manual override: `/wrap <MARKER>-N-K` — debugging only. There is no manual Code-Claude session in the canonical v1 flow; /wrap is not a founder-fired session-end ritual.

Resume-merge: `/wrap <MARKER>-N-K --resume-merge` — re-run step 6 (wave-merge) after the founder has resolved a `§wave-merge-conflict` halt. Skips re-running test/scope verification and re-pushing.

## Behavior

1. **Verify AC green.** Re-run the child's failing-test seed (now expected passing). Any test still red → `BLOCKED` per `completion-status.md`, halt-card per `docs/templates/halt-messages.md`: "<MARKER>-N-K has X failing tests." /build's finalize phase surfaces this; the path back is `/build <MARKER>-N-K --continue`.

2. **Verify scope.** Changed files match the child's expected surface — no files outside scope. Out-of-scope changes → `BLOCKED`, halt-card: "<MARKER>-N-K modified files outside its scope: <list>." auditor-stance per `auditor-stance.md` — state the finding as a fact, list the loci.

3. **Commit + push** per `naming.md` §Branch names:
   - Stage all changes.
   - Commit message: `[<MARKER>] <MARKER>-N-K: <child title> — green`.
   - Push branch `<MARKER>-N-<slug>-K`.

4. **Post session summary on child ticket:**

   ~~~
   /wrap complete. <MARKER>-N-K is green and pushed.

   * Tests: <X>/<X> passing
   * Files changed: <N> (<one-line summary>)
   * Branch: <MARKER>-N-<slug>-K
   * Commits: <count>
   ~~~

5. **Transition child Linear state** In Progress → Done per `scope-labels.md` (atomic transition per `write-discipline.md`). The child was set to In Progress by `/start`, which /build Task-invokes at its preconditions step — so the canonical-flow source state is always In Progress.

   The off-path Todo case occurs only on **manual `/wrap <MARKER>-N-K`** invocations against a child that was never `/start`-ed (debugging or ad-hoc tracking — never a /build-chained flow, since /build's contract guarantees /start has run). In that case /wrap also flips Todo → Done in one step. This is documented as a graceful path for the manual override; it cannot fire from /build.

   `scope:built` on the child is set by **/build**, not /wrap, per `scope-labels.md` §Transition ownership. /wrap moves the Linear-native state (In Progress → Done); /build moves the `scope:*` label (`scope:sealed → scope:built`). These are distinct and both happen in /build's finalize phase — /build sets the label, then Task-invokes /wrap which sets the state.

6. **Wave-merge** (load-bearing for multi-wave plans). Read `decomposition.md` to identify which wave this child belongs to and whether other siblings in the same wave are also Done.
   - **Wave incomplete** (other siblings in this wave still building) → no merge, no chain. Post wave-progress comment.
   - **Wave complete** (this child finishes its wave, AND a later wave exists) → merge this wave's child branches into the default branch:
     ~~~
     git fetch
     git switch <default-branch>
     git merge --no-ff <MARKER>-N-<slug>-K1 <MARKER>-N-<slug>-K2 ...
     git push
     ~~~
     On `git merge` failure → `BLOCKED` per `§wave-merge-conflict`. The founder resolves the conflict and re-runs `/wrap <MARKER>-N-K --resume-merge`.
   - **Final wave complete** (last wave, all children of this parent Done) → also merge to default (no later wave to enable, but the parent ships through default). Same merge logic, same halt pattern on conflict.

   The merge is non-skippable for multi-wave plans because Wave-(N+1) child branches are created from default; without the Wave-N merge they cannot see Wave-N's code.

7. **Check parent completion.** Query the parent's children:
   - **Not all done** → post on the parent: "<MARKER>-N-K complete. <X> of <Y> children done. Next Wave-eligible: <MARKER>-N-M." No chain. (Wave-merge in step 6 has already run if this child finished its wave.)
   - **All done AND `workflow.verify = true`** → Task-invoke `/verify <MARKER>-N` per audit decision #9. The parent stays In Progress; /verify owns the transition (Done on pass, fix-children on fail).
   - **All done AND `workflow.verify = false`** → transition the parent's Linear state to Done. If `workflow.auto_retro = true`, Task-invoke `/retro <MARKER>-N`.

   Steps 4–7 Linear writes batch same-turn per `write-discipline.md`. The git merge in step 6 is a separate operation that precedes the Linear writes.

## Same-turn write rules

Per `write-discipline.md`:
- Git commit + push: same turn.
- Linear writes (session summary comment + child state transition + parent comment or transition): batched same-turn.

## Outputs

| Artifact | Location |
|---|---|
| Commit + pushed branch | Git remote |
| Session summary | Child ticket comment |
| Child state | In Progress → Done (Todo → Done if /start was skipped) |
| Parent state (if all done) | → Done, or held by /verify |
| Next Wave-eligible hint | Parent ticket comment |

## Completion status

Per `completion-status.md`:

- `DONE` — tests green; committed and pushed; child → Done; parent completion checked and advanced per workflow knobs.
- `DONE_WITH_CONCERNS` — completed, but: the child was Todo (not In Progress) at /wrap start (the /start step was skipped); or next Wave-eligible siblings exist without a parallel-session setup.
- `BLOCKED` — step 1 red tests; step 2 out-of-scope file changes. Halt-card per `docs/templates/halt-messages.md`; /build's finalize phase surfaces it and the path back is `/build <MARKER>-N-K --continue`.
- `NEEDS_CONTEXT` — branch name doesn't match the `<MARKER>-N-<slug>-K` convention per `naming.md`; child ticket missing; parent ticket missing.

## Naming reconciliation note

D3.4 §Per-stage gate inventory `/wrap` row names three gates: `wrap.provenance`, `wrap.product-docs-mirrored`, `wrap.label-transition`. The parent `spec.md` AC-10 names **four** gates: `wrap.provenance`, `wrap.tests-green`, `wrap.mirror-sha-match`, `wrap.linear-state-updated`.

The split lines up partially:

| D3.4 | spec.md AC-10 | Same predicate? |
|---|---|---|
| `wrap.provenance` | `wrap.provenance` | Yes (identical) |
| (part of `wrap.product-docs-mirrored`) | `wrap.tests-green` | Different — AC-10's `wrap.tests-green` is the "red tests block" predicate (carried forward from v0.1's existing tests-green-at-wrap check). D3.4's row composes mirror sha + lock-balance only. AC-10 splits tests-green out as its own gate. |
| `wrap.product-docs-mirrored` | `wrap.mirror-sha-match` | Yes — same predicate (filesystem-Linear mirror sha match). AC-10's name reads more narrowly. |
| `wrap.label-transition` | `wrap.linear-state-updated` | Yes — same predicate (Linear ticket label transition to `scope:built` + status to `Done`). AC-10's name reads more broadly. |

This skill uses **AC-10's four names** (`wrap.provenance`, `wrap.tests-green`, `wrap.mirror-sha-match`, `wrap.linear-state-updated`) because AC-10 explicitly enumerates four gates and the parent spec is the binding for this skill's acceptance criterion. The split of tests-green out from mirror-sha-match is an AC-10 refinement over D3.4's row and is more granular for `solo-verify` parity (a tests-green failure surfaces a different halt than a mirror-sha failure; surfacing them as separate gates is clearer at `solo-verify --list-gates` and `solo-verify --explain` time).

**Surfaced item:** D3.4's `/wrap` row carries three gates; spec.md AC-10 carries four. The split here uses AC-10's four. **Recommendation:** amend D3.4's `/wrap` row to match — split `wrap.product-docs-mirrored` into `wrap.tests-green` + `wrap.mirror-sha-match`. One-line edit.

## Gate evaluation

Four gates fire at `/wrap`, in firing order per AC-10 + D3.4 §Aggregation rules. All gates evaluate before any halt card is composed.

```text
GATES_AT_WRAP = [
  "wrap.provenance",          # pre-flight; manifest chain to /build
  "wrap.tests-green",         # at-write; red tests block (v0.1 carry-forward)
  "wrap.mirror-sha-match",    # at-write; filesystem-Linear mirror sha match (v0.1 carry-forward)
  "wrap.linear-state-updated" # at-write; Linear label + status transition (v0.1 carry-forward)
]

for gate in GATES_AT_WRAP:
    evaluate gate predicates and record per-gate result
    # do NOT short-circuit; all gates evaluate

if any gate has at least one failing predicate:
    compose aggregate halt card per D3.4 §Aggregation rules
    do NOT write the manifest
    exit with halt
else:
    write manifest with the v0.2 outputs schema (additive per D3.3)
    seal /wrap
```

### Gate 1 — `wrap.provenance` (pre-flight; manifest chain to `/build`)

V0.1's `/wrap` already evaluates this predicate; v0.2 renames it to `wrap.provenance`.

```text
read cascade:run-state from .cascade/run-state.json

# Step 1: parent manifest must be /build's finalize seal
expected_parent_path ← cascade:run-state.last_completed_stage.postcondition_manifest_path
if expected_parent_path absent or path doesn't resolve to a file:
    FAIL with §provenance-chain-broken
    diagnostic: f"expected /build manifest at {expected_parent_path}; absent"
    continue

# Step 2: recompute manifest sha
recomputed_sha ← sha256 of parent manifest with manifest_sha256 field zeroed
expected_sha   ← cascade:run-state.last_completed_stage.postcondition_manifest_sha256
if recomputed_sha != expected_sha:
    FAIL with §provenance-chain-broken
    diagnostic: f"parent manifest sha mismatch at {expected_parent_path}"
    continue

# Step 3: parent must be /build (finalize)
parent_outputs ← parse parent manifest's outputs
if parent_outputs.stage != "/build":
    FAIL with §provenance-chain-broken
    diagnostic: f"/wrap's upstream must be /build; got stage='{parent_outputs.stage}'"
```

Halt code: `§provenance-chain-broken` (consolidated chain-recovery halt per Child A's halt-messages-append.md). Recovery: `--reconcile`.

### Gate 2 — `wrap.tests-green` (at-write; red tests block — v0.1 carry-forward)

V0.1's `/wrap` already evaluates this predicate (step 1 of §Behavior). The amendment renames it.

```text
# Read /build's finalize manifest
test_seed_status ← parent_outputs.failing_test_seed_status

# Predicate: every entry's status is "passing"
red_tests ← [entry for entry in test_seed_status if entry.status != "passing"]
if red_tests is non-empty:
    FAIL with §wrap-tests-red
    diagnostic: f"{len(red_tests)} test(s) in failing_test_seed_status[] are not 'passing': {[entry.name for entry in red_tests]}; /wrap requires the seed to be fully green per the existing v0.1 contract"
```

Halt code: `§wrap-tests-red` (v0.1 carry-forward; the existing halt-card text describes red tests blocking /wrap). Recovery: run `/build <MARKER>-N --continue` until the seed is green, then re-run `/wrap`.

### Gate 3 — `wrap.mirror-sha-match` (at-write; filesystem-Linear mirror sha match — v0.1 carry-forward)

V0.1's `/wrap` already evaluates this predicate. The amendment renames it.

```text
# Read the docs that this wrap is asked to mirror to Linear
# Per D2.1 v2 §`/wrap` row: arch_doc, data_model_doc, journeys_doc are the canonical three;
# additional docs (e.g., the spec's §Open Questions) per v0.1 contract.

fs_docs ← {
  "arch":        "docs/product/architecture.md",
  "data_model":  "docs/product/data-model.md",
  "journeys":    "docs/product/journeys.md"
}

linear_doc_ids ← {
  "arch":        linear-doc-id for the arch doc per /onboard manifest,
  "data_model":  linear-doc-id for the data-model doc per /onboard manifest,
  "journeys":    linear-doc-id for the journeys doc per /onboard manifest
}

# Predicate: filesystem sha matches Linear sha per doc
for doc_key in fs_docs:
    fs_sha     ← sha256 of fs_docs[doc_key] file content
    linear_sha ← sha256 of the linear-doc-mcp's read of linear_doc_ids[doc_key]
    if fs_sha != linear_sha:
        FAIL with §product-doc-mirror-drift
        diagnostic: f"doc '{doc_key}': filesystem at {fs_docs[doc_key]} differs from Linear doc {linear_doc_ids[doc_key]}; fs_sha={fs_sha[:12]}..., linear_sha={linear_sha[:12]}..."

# Lock-balance check (v0.1 carry-forward; D2.1 v2 §`/wrap` row's lock_releases[] predicate)
acquired ← read .solo-locks/ for locks acquired during this /wrap session
released ← parse lock_releases[] from in-memory state
if set(acquired) != set(released):
    FAIL with §wrap-lock-imbalance
    diagnostic: f"lock imbalance: acquired={sorted(acquired)}, released={sorted(released)}"
```

Halt codes: `§product-doc-mirror-drift`, `§wrap-lock-imbalance` (both v0.1 carry-forward). Recovery: the founder edits whichever side (fs or Linear) is wrong; re-runs `/wrap`. Locks are released forcibly via `/cascade-halt` if a stuck `/wrap` cannot release them.

### Gate 4 — `wrap.linear-state-updated` (at-write; Linear label + status transition — v0.1 carry-forward)

V0.1's `/wrap` already evaluates this predicate (steps 5 and 7 of §Behavior). The amendment renames it.

```text
# Predicate 1: Linear ticket label transitioned to scope:built
ticket_labels ← linear-mcp's read of ticket labels
if "scope:built" not in ticket_labels:
    FAIL with §wrap-label-transition-failed
    diagnostic: f"ticket {ticket} missing 'scope:built' label; current labels: {ticket_labels}"

# Predicate 2: Linear ticket status transitioned to Done
ticket_status ← linear-mcp's read of ticket status
if ticket_status != "Done":
    FAIL with §wrap-label-transition-failed
    diagnostic: f"ticket {ticket} status is '{ticket_status}'; expected 'Done'"

# Predicate 3: Done-project membership per D1 §Linear product layer
ticket_project ← linear-mcp's read of ticket project assignment
done_project_id ← from /onboard manifest's outputs.linear_projects_created[].id where name=="Done"
if ticket_project != done_project_id:
    FAIL with §wrap-label-transition-failed
    diagnostic: f"ticket {ticket} project is '{ticket_project}'; expected Done project id '{done_project_id}'"

# Linear-sync sanity check per D2.1 v2 §Linear-sync
linear_sync_sanity ← solo-verify linear-sync-sanity-check
if linear_sync_sanity exits non-zero:
    FAIL with §linear-state-inconsistent
    diagnostic: f"Linear-sync sanity check failed; eventual-consistency window may be live, re-run /wrap after 30s"
```

Halt codes: `§wrap-label-transition-failed`, `§linear-state-inconsistent` (both v0.1 carry-forward). Recovery: the founder either fixes the Linear state manually (rare; Linear MCP eventual-consistency window usually self-corrects within 30s) or `/cascade-halt`s the wrap and `--reconcile`s.

Per D3.4 §Per-stage gate inventory `/wrap` row: "Label transition is last because rolling back a Linear label change is more expensive than rolling back a filesystem write." This ordering rationale carries verbatim — the gate firing order positions `wrap.linear-state-updated` last so that fs-side failures (tests-red, mirror-drift) are caught before any Linear-side state change.

## Manifest write (on all-gates-pass)

Write the `/wrap` manifest at `.cascade/manifests/<ticket>-wrap.json` per D2.1 v2 `/wrap` row. The v0.1 schema carries forward; no v0.2 additive fields specifically for `/wrap` (the `failing_test_seed_status[].artifact_path` propagation is already on `/build`'s manifest, which `/wrap` reads but doesn't extend).

```json
{
  "stage": "/wrap",
  "ticket": "<MARKER>-<N>",
  "wrap_sealed_at": "<ISO-8601 timestamp>",
  "outputs": {
    "linear_label_transition":      {"from": "scope:built-by-build", "to": "scope:built"},
    "done_project_id":              "<id>",
    "arch_doc_updated":             true,
    "data_model_doc_updated":       true,
    "journeys_doc_updated":         true,
    "fs_mirror_sha256":             "<sha>",
    "linear_mirror_sha256":         "<sha>",
    "lock_releases":                [...]
  },
  "input_provenance": {
    "parent_manifest_path":         ".cascade/manifests/<ticket>-build.json",
    "parent_manifest_sha256":       "<sha>",
    "ac_list_sha256":               "<sha>",
    "four_hat_seal_sha256":         "<sha>"
  },
  "manifest_sha256": "<recomputed-zero-self-field>"
}
```

After write, update `cascade:run-state.json`'s `last_completed_stage` to point at this manifest path and sha.

## /Chains

**Pattern:** C (auto-fire-chain, Group F variant — chain's last stage; runs in Claude Code)
**Group:** F
**Within-group transitions:** this skill is the chain's last stage; no further intra-Group-F transitions after seal. The chain `/build` → `/wrap` terminates here per ticket; the next Group F chat (a fresh `/build SOL-<next-ticket>`) is a new chat-hard boundary, not a within-group transition. Wrap-internal safe boundaries: before `/wrap`'s Linear-write step (per D2.3 v1.3 §Within-group safe boundaries Group F row).
**Group exit trigger:** `/wrap` manifest seal at `.cascade/manifests/<ticket>-wrap.json` after the `wrap.provenance`, `wrap.tests-green`, `wrap.mirror-sha-match`, `wrap.linear-state-updated` gates per D3.4 §wrap gates pass.
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant `normal` on standard exit; variant `reset-triggered` if D2.2 band 3 triggered the exit (Group F is the only group with live D2.2 enforcement, so the reset-triggered variant is Group-F-exclusive); variant `manual-halt` if `cascade:run-state.manual_halt = true` was set by a sidecar `/cascade-halt` per D2.3 v1.3 §Manual halt protocol Group F subsection. After render, set `cascade:run-state.last_completed_group = "F"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<ticket>-wrap.json"`, flush, write `.cascade/handoff/last.md`. The Stop hook then fires SessionEnd for async telemetry per D2.2 (Group F is the only group with a live SessionEnd event).
**Next group entry:** **F[next-ticket]** if the queue contains more tickets (the chat-end card's handoff prompt names the next ticket: `Active ticket: SOL-<next-ticket>`, `Group entry: F`; the founder opens a new Claude Code session and pastes — auto-renders next-ticket per D2.3 v1.2's v1.1-resolved open-question 2). **G** if this was the last ticket in the queue (the queue is empty: `cascade:run-state.next_ticket == null`; the handoff prompt names `Group entry: G`, `Active milestone: <milestone-id>` for the per-child `/verify` fan-out).
**Auto-fire compact handling:** **applies, edge case.** Per D2.3 v1.3 §Auto-fire compact behaviour edge case, `/wrap` is the chain's last stage; if PreCompact fires at `/wrap`'s last safe boundary (just before group exit), `cascade:run-state.next_chain_step` is set to `null` (no further chain stage). The post-compact Stop hook proceeds with its normal group-exit decision (render the chat-end card, no further Task-invoke). If PreCompact fires earlier in `/wrap` (before the last safe boundary), `next_chain_step` is set to `"wrap"` so the post-compact Stop hook resumes from the chain's current position.
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<ticket>-wrap.json`. `/build`'s manifest is the chain intermediate (per `/build`'s `/Chains` section). D4.6 v1.1 reads `/wrap`'s manifest's `outputs` field to populate the chat-end card's "What was produced" section for Group F re-derivation. Each per-ticket Group F chat has its own exit manifest (one `<ticket>-wrap.json` per chat); F→F[next-ticket] re-derivation in D4.6 v1.1 reads the *previous* ticket's `/wrap` manifest (the just-completed chat's), not the next ticket's pending state.

## Cross-references

- **D2.1 v2 §`/wrap` row** — the upstream manifest schema and verifier-predicate baseline; this amendment renames the predicates per AC-10 + D3.4 with no behavior change.
- **D2.1 v2 §Linear-sync** — the eventual-consistency sanity check Gate 4 Predicate 4 evaluates.
- **D2.2 §Hook/script surface** — `/wrap`'s PreToolUse matcher on Linear write tool (the existing v0.1 wiring carries forward).
- **D3.4 §Per-stage gate inventory `/wrap` row** — the three-gate inventory this amendment splits to four per AC-10; surfaced as Item #3 in authoring notes.
- **D3.4 §Aggregation rules** — all-gates-evaluate, single-card-aggregate semantics applied to /wrap's seal halt.
- **D1 §Linear product layer** — the six Linear projects and the Done project membership predicate Gate 4 evaluates.
- **Child A `halt-messages-append.md`** — `§provenance-chain-broken` referenced by Gate 1. Other halts referenced (`§wrap-tests-red`, `§product-doc-mirror-drift`, `§wrap-lock-imbalance`, `§wrap-label-transition-failed`, `§linear-state-inconsistent`) are v0.1 carry-forwards; the executing session verifies these exist in v0.1 `halt-messages.md` (they should, as part of the F-2 fix shipped in v0.1).
- **`child_B_chains_sections.md`** Pattern C Group F variant (`/build` + `/wrap`) — the `/Chains` block for `/wrap` was sealed in a prior session; this amendment's gates land BEFORE the `/Chains` block's group-exit rendering of the chat-end card.
- **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-10** — this skill amendment satisfies AC-10 as authored.

## Notes

**Trigger rewiring (audit "Trigger rewiring" §).** Pre-extraction /wrap was "Code-Claude session-end ritual. Internal: Code-Claude invokes at end of build session." The canonical v1 flow has no manual Code-Claude session — /build runs Ralph as a blackbox, and on build-reviewer-pass /build Task-invokes /wrap. /wrap's trigger is now "invoked by /build on build-reviewer-pass." The manual `/wrap <MARKER>-N-K` override is kept for debugging only.

**Why /wrap stays a skill** (audit decision #1, "Skills that stay skills" list). The founder explicitly rejected absorbing /wrap into /build — "wrap is quite complex, merging makes /build a monster." /wrap carries real logic: test re-verification, scope verification, the parent-completion check, and the /verify-vs-/retro routing. It stays a separate skill that /build Task-invokes.

**Label vs state — distinct, both in /build's finalize phase.** `scope:built` is a `scope:*` label set by /build per `scope-labels.md`. `In Progress → Done` is a Linear-native state set by /wrap. /build's finalize phase sets the label, then Task-invokes /wrap which sets the state. /wrap never touches `scope:*` labels.

**Test verification (step 1) is non-negotiable.** Red tests = no /wrap completion = no commit. The TDD gate is enforced here even though the `build-reviewer` agent already passed — the agent reviews the diff against the spec; /wrap re-runs the actual tests. Belt and suspenders.

**Scope verification (step 2)** catches a Ralph run that drifted. A child for "email validation" that modified the auth flow halts the wrap. Cheap insurance — the `build-reviewer` agent has a scope-boundary axis too, but /wrap's check is on the actual changed-file set.

**Pairs with `/start`** (now `[SOL-CMD] start`). /start opens the build-session window (Todo → In Progress); /wrap closes it (In Progress → Done + commit + push + parent check). Both are Task-invoked by /build — /start at preconditions, /wrap at finalize.

## Open questions (deferred to v1.1+)

- **v0.2 subagent parallelism.** v0.1 wraps one child per /build run. With subagent parallelism, /wrap fires per child completing and the parent-completion check converges asynchronously.
- **Next-Wave auto-start.** Currently "not all done" posts a hint and stops. v0.2 subagent mode picks the next Wave child automatically.
