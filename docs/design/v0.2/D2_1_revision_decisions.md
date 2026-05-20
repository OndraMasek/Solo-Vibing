# D2.1 — Revision decisions (2026-05-18)

**Status:** Founder decisions on the seven verification questions raised against D2.1. Apply at the top of the next session before drafting D2.2.

## Decisions

| # | Question | Decision | D2.1 impact |
|---|---|---|---|
| 1 | Who writes a subagent's manifest? | **Parent writes from independently re-read transcript.** Strict structural verification; subagent's self-report is ignored. | None — D2.1 already specifies this. Confirmation. |
| 2 | Filesystem-canonical or Linear-canonical for `cascade:run-state`? | **Filesystem canonical; Linear is durable mirror.** | None — D2.1 already specifies this. Confirmation. |
| 3 | Lock grain: product-level halt vs queue vs other? | **Per-resource write locks.** `current_stage` → `active_stages[]`. Locks land on shared product docs (Status, architecture, data-model, journeys) with brief hold times. Same-product concurrent stages are first-class. | Significant rewrite. `cascade:run-state` schema, lock semantics subsection. |
| 4 | Whole-file vs per-AC vs AC-list spec checksums? | **AC-list-only hash.** Hash the bulleted AC entries, not the surrounding prose. Pulls forward from the v0.2.1 deferral. | Moderate rewrite. `spec_sha256` → `ac_list_sha256` in `input_provenance` and across the verifier-predicate table. Build pre-flight predicate updates. |
| 5 | Does `/accept-taint` exist? | **No. No button.** Taints are cleared only by re-running the responsible stage with `--reconcile` (D4.5). The cascade re-verifies properly; the founder never waives. | Delete the `/accept-taint` mention in the tainted-artifact section. "Cleared, not erased" mechanic stays — but only via `--reconcile`. |
| 6 | Deterministic command hooks or LLM agent hooks for subagent verification? | **Deterministic command hooks by default.** Agent hooks reserved for predicates that genuinely need LLM judgment. D2.2 decides the per-predicate cut. | None — D2.1 already states this provisional rule. Confirmation. |
| 7 | Tainted-artifact tracking: centralized in `cascade:run-state` or distributed across manifests? | **Distributed.** Each manifest carries `is_tainted: bool` and `taint_reason`. `cascade:run-state` carries only a derived count. Status doc renders "What's broken" by reading manifests. | Bigger rewrite. The `cascade:run-state.tainted_artifacts[]` field dissolves. Manifest schema gains the taint fields. Reconcile mechanics simplify in D4.5. |

## Sequencing for next session

1. **Open by revising D2.1 → D2.1 v2** with decisions 3, 4, 5, 7 applied. Decisions 1, 2, 6 were already aligned with the draft — no edit needed, but mention in the v2 changelog header that they're confirmed.
2. **Draft D2.2** (session auto-management) against v2.
3. Both artifacts land in `v0.2/`.

## Knock-on effects worth noting

- **D4.5 (reconcile primitives)** gets simpler because of decision 7 (manifest-resident taints) and decision 5 (no waiver — every clear is a real re-verification). The D4.5 design doesn't need to handle "waived but not cleared" as a separate state.
- **D1's Status doc rendering** is unchanged in spec (it still shows "What's broken") but the read path changes — render-time scan of all manifests for `is_tainted: true` instead of reading the central `tainted_artifacts[]` list. Cheap, since manifests are local files.
- **D3.x (decomposition / test pyramid / gates)** is not affected by these decisions. Trust model is independent of the build-quality stack.
