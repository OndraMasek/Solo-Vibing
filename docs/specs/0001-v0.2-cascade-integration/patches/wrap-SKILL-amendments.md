# `.claude/skills/wrap/SKILL.md` — v0.2 amendments

**Status:** Patch-ready amendment block. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing` which reconciles against v0.1 byte-for-byte before applying.

**Scope:** **Naming-only standardization** of the v0.1 `/wrap` predicates to the canonical `wrap.*` gate names per D3.4 §Per-stage gate inventory `/wrap` row + spec.md AC-10. Behavior is materially unchanged from D2.1 v2 — every predicate this amendment names is a renamed v0.1 predicate, not a new one. The amendment exists so that `solo-verify --list-gates wrap` and `solo-verify --explain wrap.<gate>` return canonical names that match the cascade's other stages.

Per `decomposition.md` Child 0001-B: "Behavior unchanged from D2.1 v2; naming standardized for `solo-verify` parity."

**v0.1 reconciliation pattern:** the executing session reads v0.1's `.claude/skills/wrap/SKILL.md` and substitutes the v0.1 predicate-identifier strings with the v0.2 gate names below. The predicate logic itself is unchanged. No new code paths; no new halt-card codes (the v0.1 halt-card codes carry forward verbatim under their existing names).

---

## Naming reconciliation note

D3.4 §Per-stage gate inventory `/wrap` row names three gates: `wrap.provenance`, `wrap.product-docs-mirrored`, `wrap.label-transition`. The parent `spec.md` AC-10 names **four** gates: `wrap.provenance`, `wrap.tests-green`, `wrap.mirror-sha-match`, `wrap.linear-state-updated`.

The split lines up partially:

| D3.4 | spec.md AC-10 | Same predicate? |
|---|---|---|
| `wrap.provenance` | `wrap.provenance` | Yes (identical) |
| (part of `wrap.product-docs-mirrored`) | `wrap.tests-green` | Different — AC-10's `wrap.tests-green` is the "red tests block" predicate (carried forward from v0.1's existing tests-green-at-wrap check). D3.4's row composes mirror sha + lock-balance only. AC-10 splits tests-green out as its own gate. |
| `wrap.product-docs-mirrored` | `wrap.mirror-sha-match` | Yes — same predicate (filesystem-Linear mirror sha match). AC-10's name reads more narrowly. |
| `wrap.label-transition` | `wrap.linear-state-updated` | Yes — same predicate (Linear ticket label transition to `scope:built` + status to `Done`). AC-10's name reads more broadly. |

The amendment below uses **AC-10's four names** (`wrap.provenance`, `wrap.tests-green`, `wrap.mirror-sha-match`, `wrap.linear-state-updated`) because AC-10 explicitly enumerates four gates and the parent spec is the binding for this skill's acceptance criterion. The split of tests-green out from mirror-sha-match is an AC-10 refinement over D3.4's row and is more granular for `solo-verify` parity (a tests-green failure surfaces a different halt than a mirror-sha failure; surfacing them as separate gates is clearer at `solo-verify --list-gates` and `solo-verify --explain` time).

**Surfaced item:** D3.4's `/wrap` row carries three gates; spec.md AC-10 carries four. The split here uses AC-10's four. **Recommendation:** amend D3.4's `/wrap` row to match — split `wrap.product-docs-mirrored` into `wrap.tests-green` + `wrap.mirror-sha-match`. One-line edit. See authoring notes Surfaced item #3.

---

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
read cascade:run-state from docs/.cascade/run-state.json

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

V0.1's `/wrap` already evaluates this predicate. The amendment renames it.

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

V0.1's `/wrap` already evaluates this predicate. The amendment renames it.

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

---

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

---

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
