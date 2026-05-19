# D0.2 — Findings disposition map

**Status:** Design.
**Phase:** 0 (Foundations).
**Resolves:** Tracking, not architecture. Confirms each F-1 through F-12 from the Bomber critique synthesis (SOL-89) has a home in v0.2 design.

## Disposition table

| Finding | Linear | Disposition | Notes |
|---|---|---|---|
| F-1 — Subagent reports unverified | SOL-90 | Subsumed by **D2.1** (Trust model) | Foundational. Most other dispositions depend on it. |
| F-2 — Gates bypassable; logged not prevented | SOL-91 | Subsumed by **D2.1** + tainted-artifact propagation surfaced in **D1** (Status doc) | Provenance binding makes the four-hat unforgeable; tainted artifacts visibly propagate downstream. |
| F-3 — Quality topology inversion | SOL-92 | Subsumed by **D3.1** (decomposition negotiation) + **D3.2** (test pyramid) + **D3.3** (three-tier gates) | The headline failure class. Three design docs together address it. |
| F-4 — No source of truth | SOL-93 | Partially subsumed by **D0.1** (repo strategy) + **D1** (Linear product layer canonical) | Repo split removes the framework/product confusion. Linear product layer becomes the canonical product-doc store. Per-AC checksums (mentioned in F-4 direction) deferred to v0.2.1 unless they surface as a blocker. |
| F-5 — No supervision / recovery | SOL-94 | Partially subsumed by **D2.2** (session auto-management for the kill-and-resume class) | Process-group kill, orphan reaping, macOS `gtimeout` portability remain as separate work in **D4.1** (template bug batch). |
| F-6 — Recovery nuclear-only | SOL-95 | Net-new design needed: **D4.5** (reconciliation primitives). Added to the Phase 4 plan. | `--reconcile` for /build and /wrap, `--rerun=stage` for /specify, frozen-AC primitive. |
| F-7 — No concurrency control | SOL-96 | Minimal lock primitive in **D2.1** (`cascade:run-state` acts as parent-level lock); full distributed-locking deferred. | For solo founder, lock-and-halt is sufficient. |
| F-8 — Template bugs (no CI) | SOL-97 | Subsumed by **D4.1** (template bug batch). Cheap, parallelizable. | Includes the F-5 portability items not covered by D2.2. |
| F-9 — Identifier model incoherent | SOL-98 | **Dissolved by D0.1** (repo split + one Linear team per consumer). | Once marker = team key, all five identifiers reconcile. |
| F-10 — Feedback log write-only | SOL-99 | Subsumed by **D1** (Status doc + cascade-maintained product docs) + **D3.4** (autonomy escalation makes /retro outputs binding on next /specify). | Two changes together close the loop. |
| F-11 — Ceremony bloat | SOL-100 | Subsumed by **D3.4** (autonomy mode) + **D4.2** (skill splitting). | "Solo mode" implicit in default autonomy. |
| F-12 — Token economics | SOL-101 | Subsumed by **D2.2** (session auto-management) + **D4.2** (skill splitting). | |

## Net-new design docs (added to plan)

One finding produced a design doc not in the originally-presented Phase plan:

- **D4.5 — Reconciliation primitives** (from F-6). `--reconcile`, `--rerun=stage`, frozen-AC flag. Slots into Phase 4.

## Deferred / parked items

- **Per-AC checksums** (F-4 direction item 2). Hash the AC the child covers + shared design sections rather than whole-file `spec_sha256`. Cheap design; downstream change for every spec template. Defer to v0.2.1 if the whole-file checksum continues to cause false BLOCKs after the repo split.
- **Full distributed-locking** (F-7). The `cascade:run-state` lock handles solo-founder concurrency. Multi-session genuine concurrency (rare; intentionally unsupported in v0.2) is v0.3+ work.
- **Linear's eventually-consistent semantics** (F-7 specific evidence). The `completedAt` vs `status` divergence detection is a one-liner; include in D2.1 as a sanity-check item on every Linear read.

## Re-validation step

After all v0.2 design docs land and are approved, walk the disposition table once more to confirm each finding is now actually addressed by the merged design. If a finding's home design doc has shifted scope, update the table.
