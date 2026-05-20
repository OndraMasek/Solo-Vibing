# `.claude/skills/update-linear/SKILL.md` — v0.2 amendments

**Status:** Patch-ready amendment block. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing` which reconciles against v0.1 byte-for-byte before applying.

**Scope:** **Naming-only standardization** of v0.1's `/update-linear` predicate to the canonical `update-linear.diff-applied` gate name per D3.4 §Per-stage gate inventory `/update-linear` row + spec.md AC-13. Behavior is materially unchanged from D2.1 v2 — the predicate this amendment names is a renamed v0.1 predicate, not a new one. The amendment exists so that `solo-verify --list-gates update-linear` and `solo-verify --explain update-linear.diff-applied` return canonical names that match the cascade's other stages.

Per `decomposition.md` Child 0001-B: "`.claude/skills/update-linear/SKILL.md` — evaluate the `update-linear.diff-applied` gate from D3.4." Same shape as `/wrap`'s naming-only amendment from Child 0001-B continuation 1.

**v0.1 reconciliation pattern:** the executing session reads v0.1's `.claude/skills/update-linear/SKILL.md` and substitutes the v0.1 predicate-identifier string with the v0.2 gate name `update-linear.diff-applied`. The predicate logic itself is unchanged. No new code paths; no new halt-card codes (the v0.1 halt-card code `§linear-state-inconsistent` carries forward verbatim under its existing name).

---

## Naming reconciliation note

D3.4 §Per-stage gate inventory `/update-linear` row names one gate: `update-linear.diff-applied`. The parent `spec.md` AC-13 reads: "`.claude/skills/update-linear/SKILL.md` evaluates the `update-linear.diff-applied` gate." AC-13 uses D3.4's gate name verbatim; no divergent naming surface. The amendment uses D3.4's name without further reconciliation.

D3.4 framing: "D2.1 v2 specifies this stage; D3.4 names its single gate for completeness." The amendment is the SKILL.md realisation of D3.4's row.

---

## Stage structure

`/update-linear` is a per-ticket stage that runs after `/plan`'s seal in the auto-fire chain `/plan → /review → /update-linear` (the Group E chain per D2.3 v1.3 §Pattern C). It propagates the spec's resolved AC list and per-child decomposition into Linear ticket descriptions for the parent ticket and every child the `/plan` decomposer emitted. The v0.1 behavior is:

1. Read the `/plan` manifest's `outputs.child_tickets[]` and parent ticket.
2. For each ticket, compose its target Linear description (parent: spec link + decomposition summary; child: per-child block from `decomposition.md` rendered as ticket description).
3. Apply the updates via Linear MCP.
4. Compute `diff_sha256` over the applied diff per D2.1 v2 §`/update-linear` row.
5. Verify each ticket's current Linear state matches the diff.
6. Seal the manifest.

The amendment does not change steps 1–4. It renames step 5's predicate and surfaces it under `update-linear.diff-applied`. Step 6 (manifest seal) carries forward unchanged.

---

## Gate evaluation

One gate fires at `/update-linear` at-write per D3.4 §Per-stage gate inventory `/update-linear` row. The gate evaluates just before manifest seal — after all Linear writes from step 3 have completed and the eventual-consistency window per D2.1 v2 §Linear-sync has been observed (the v0.1 contract carries forward — `/update-linear` waits per the v0.1 backoff before re-reading).

```text
GATES_AT_UPDATE_LINEAR_AT_WRITE = ["update-linear.diff-applied"]

for gate in GATES_AT_UPDATE_LINEAR_AT_WRITE:
    evaluate; record per-gate result
if any gate has failing predicates:
    compose halt card per D3.4 §Aggregation rules (single-gate stage; aggregation degenerates to the single gate's halt)
    do NOT write manifest; exit with halt
else:
    write manifest
    seal /update-linear
```

### Gate 1 — `update-linear.diff-applied` (at-write; D2.1 v2 `/update-linear` row + §Linear-sync — v0.1 carry-forward)

V0.1's `/update-linear` already evaluates this predicate. The amendment renames it.

```text
# Read the in-memory record of writes applied in step 3
applied_diff ← read step-3 write log: list of (ticket_id, field, before_value, after_value)
diff_sha256 ← sha256 over the canonical-serialised applied_diff

# Predicate 1: each ticket's current Linear state matches the applied diff
for entry in applied_diff:
    current ← linear-mcp's read of entry.ticket_id's entry.field
    if current != entry.after_value:
        FAIL with §linear-state-inconsistent
        diagnostic: (
            f"ticket {entry.ticket_id}'s field '{entry.field}' currently '{truncate(current, 80)}'; "
            f"expected '{truncate(entry.after_value, 80)}' per applied diff"
        )
        continue

# Predicate 2: Linear-sync sanity check per D2.1 v2 §Linear-sync
# Eventually-consistent reads: the v0.1 contract reads twice with the v0.1-specified backoff
# between reads; if both reads return the expected value, the sync is sane.
for entry in applied_diff:
    first_read ← linear-mcp's read of entry.ticket_id's entry.field
    sleep(v0.1-specified backoff window)   # e.g., 750ms; v0.1 owns the constant
    second_read ← linear-mcp's read of entry.ticket_id's entry.field
    if first_read != second_read:
        FAIL with §linear-state-inconsistent
        diagnostic: (
            f"ticket {entry.ticket_id}'s field '{entry.field}' is unstable across the Linear-sync window: "
            f"first read '{truncate(first_read, 80)}', second read '{truncate(second_read, 80)}'; "
            f"Linear is still propagating the write or another writer is racing"
        )
        continue
    if first_read != entry.after_value:
        FAIL with §linear-state-inconsistent
        diagnostic: (
            f"ticket {entry.ticket_id}'s field '{entry.field}' stable but value '{truncate(first_read, 80)}' "
            f"differs from expected '{truncate(entry.after_value, 80)}'; the write did not land"
        )
```

Halt code: `§linear-state-inconsistent` (v0.1 carry-forward). Recovery options surfaced in the halt card:

- **Founder edits Linear manually** — for cases where the discrepancy is because a human (or another tool) wrote concurrently. Founder reconciles Linear to match `decomposition.md`'s view, then re-runs `/update-linear` or skips to `/build` directly (the auto-fire chain pauses at the halt).
- **`/update-linear --continue`** — retry after the eventual-consistency window. v0.1's `--continue` flag re-runs the diff-apply step with the same target state; if Linear was still propagating the original write, the retry usually clears the halt. v0.1's contract for `--continue` carries forward verbatim.

Per D3.4 §`/update-linear` row: "Each ticket's current Linear state matches `diff_sha256`; Linear-sync sanity check passes per D2.1 v2 §Linear-sync."

---

## Manifest write (on all-gates-pass)

Write the `/update-linear` manifest at `.cascade/manifests/<ticket>-update-linear.json` per D2.1 v2 `/update-linear` row. The v0.1 schema carries forward; no v0.2 additive fields specifically for `/update-linear`:

```json
{
  "stage": "/update-linear",
  "ticket": "<MARKER>-<N>",
  "update_linear_sealed_at": "<ISO-8601 timestamp>",
  "outputs": {
    "summary":            "/update-linear propagated parent <MARKER>-<N> and <count> child tickets' descriptions from sealed decomposition.md to Linear; diff_sha256=<sha-short>.",
    "tickets_updated":    [
      {"ticket_id": "<MARKER>-<N>", "fields_changed": ["description", "labels"]},
      {"ticket_id": "<MARKER>-<N+1>", "fields_changed": ["description"]},
      ...
    ],
    "diff_sha256":        "<sha>",
    "linear_sync_observed_at": "<ISO-8601 timestamp>"
  },
  "input_provenance": {
    "parent_manifest_path":     ".cascade/manifests/<ticket>-plan.json",
    "parent_manifest_sha256":   "<sha>",
    "ac_list_sha256":           "<sha>",
    "four_hat_seal_sha256":     "<sha>"
  },
  "manifest_sha256": "<recomputed-zero-self-field>"
}
```

Schema rules carry forward from v0.1 with one addition:

- `outputs.summary` is the single-sentence description D4.6 v1.1 reads per D2.1 v2.1 common-manifest-fields. Per D2.3 v1.3 §`/Chains` contract Pattern C (Group E) row: `/update-linear`'s manifest is Group E's exit manifest (Group E's chain ends at `/update-linear`).

After write, update `cascade:run-state.json`'s `last_completed_stage` to point at this manifest path and sha. The chat-end card render at the `/Chains` block's Group E exit (per `child_B_chains_sections.md` Pattern C Group E variant) sets `cascade:run-state.last_completed_group = "E"`.

---

## Cross-references

- **D2.1 v2 §`/update-linear` row** — the upstream manifest schema and verifier-predicate baseline; this amendment renames the predicate per AC-13 + D3.4 with no behavior change.
- **D2.1 v2 §Linear-sync** — the eventual-consistency sanity check Gate 1 Predicate 2 evaluates; the v0.1 backoff constant is owned by v0.1's `/update-linear` SKILL.md and carries forward.
- **D2.2 §Hook/script surface** — `/update-linear`'s PreToolUse matcher on Linear write tool (the existing v0.1 wiring carries forward).
- **D2.3 v1.3 §`/Chains` contract Pattern C (Group E)** — `/update-linear`'s manifest is the Group E exit manifest; this amendment writes the schema D4.6 v1.1 re-derives from.
- **D3.4 §Per-stage gate inventory `/update-linear` row** — the one-gate inventory this amendment implements.
- **D3.4 §Aggregation rules** — degenerates to the single gate's halt for `/update-linear`'s single-gate stage.
- **D4.5 §`/update-linear` reconciliation** — not present in D4.5 per F-Rev-2's queued disposition; v0.2 ships no `--reconcile` for `/update-linear`. The recovery surfaces in the halt card are `--continue` (v0.1 carry-forward) and founder-manual Linear edit. F-Rev-2 amends D4.5 in v0.2.x to add `--reconcile` for the four uncovered stages (`/onboard`, `/update-linear`, `/review`, `/verify`, `/retro`); Child 0001-D's design session is the implementation surface.
- **Child A `halt-messages-append.md`** — `§linear-state-inconsistent` is a v0.1 carry-forward; the executing session verifies this exists in v0.1 `halt-messages.md` (it should, as part of v0.1's existing `/update-linear` contract). If absent, the executing session adds at apply time — same reconciliation pattern as `/wrap`.
- **`child_B_chains_sections.md`** Pattern C (Group E) block for `/update-linear` — sealed in a prior session; this amendment's gate evaluation lands BEFORE the `/Chains` block's Group E group-exit render.
- **`plan-SKILL-amendments.md`** (Child 0001-B continuation 0) — `/plan`'s manifest is the upstream this stage reads; the `child_tickets[]` and `decomposition_strategy` fields are read at step 2.
- **`wrap-SKILL-amendments.md`** (Child 0001-B continuation 1) — same naming-only-amendment shape; this amendment matches the pattern.
- **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-13** — this skill amendment (combined with `onboard-SKILL-amendments.md`) satisfies AC-13 as authored.
