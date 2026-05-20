# D2.1 v2.1 — Trust model (amendment-only pass)

**Status:** Design (v2.1 — single-path amendment against v2; **not adversarially reviewed** as a unit, but the change it makes is a direct application of F-Eng-1 from `D2_3_v1_2_and_D4_6_four_hat_review.md`, which adopted option (c): canonical path = `.cascade/run-state.json` at repo root).
**Phase:** 2.
**Authored:** 2026-05-19, paired with `D2_3_hybrid_session_boundary_v1_3.md` and `D4_6_cascade_resume_v1_1.md`.
**Predecessor:** `D2_1_trust_model.md` (v2 — the full trust-model document).
**Scope of v2.1:** one path string in §The `cascade:run-state` schema. Everything else in v2 carries forward unchanged.

## Changelog — v2 → v2.1

| # | Section revised | Change | Resolves | Severity |
|---|---|---|---|---|
| 1 | §The `cascade:run-state` schema (schema preamble) | Filesystem-canonical path moves from `docs/.solo-run-state.json` to `.cascade/run-state.json` at repo root. Aligns with D2.2's existing `.cascade/session/`, `.cascade/manifests/`, `.cascade/halt/` namespace. | F-Eng-1 (paired review) | Urgent |

No other field in the schema changes. No semantics change. The mirrored-Linear-document name (`[<MARKER>-DOC-NNN] cascade: run-state`) is unaffected. No new fields, no removed fields, no renamed fields.

## What changes in §The `cascade:run-state` schema

The first paragraph of §The `cascade:run-state` schema in v2 reads:

> A single JSON document per consumer at `docs/.solo-run-state.json` (filesystem-canonical) and mirrored to a Linear document `[<MARKER>-DOC-NNN] cascade: run-state` under the Product project (durable mirror). The document is the multi-stage tracker (F-7) and the postcondition handoff carrier (F-1 / F-2). D2.2 reads and writes it from hooks; this doc defines its shape.

The v2.1 revision reads:

> A single JSON document per consumer at `.cascade/run-state.json` (filesystem-canonical, at repo root — sibling to `.cascade/session/`, `.cascade/manifests/`, `.cascade/halt/` per D2.2's existing namespace) and mirrored to a Linear document `[<MARKER>-DOC-NNN] cascade: run-state` under the Product project (durable mirror). The document is the multi-stage tracker (F-7) and the postcondition handoff carrier (F-1 / F-2). D2.2 reads and writes it from hooks; this doc defines its shape.

Inside the JSON schema example block, the `schema_version` field updates from `"2.1-v2"` to `"2.1-v2.1"` to reflect the amendment. No other JSON field changes.

## Why option (c)

The paired adversarial review surfaced three options for resolving the path mismatch:
- (a) Keep `docs/.solo-run-state.json` and amend D2.3 v1.2 + D4.6 to match.
- (b) Adopt D2.3 v1.2's `docs/.cascade/run-state.json` and amend D2.1 v2 to match.
- (c) Use `.cascade/run-state.json` at repo root, consistent with D2.2's existing `.cascade/` namespace.

Option (c) wins because it minimises namespace fragmentation. D2.2 already commits to `.cascade/session/`, `.cascade/manifests/`, `.cascade/halt/` at repo root (not under `docs/`). Putting run-state under the same root keeps the `.cascade/` directory as the single canonical home for cascade-internal state — one place to look for any cascade-controlled file, one path-fragment to remember, one entry in `.gitignore` patterns. The v0.1 `docs/.solo-*.json` convention was carried over from a pre-D2.2 world that didn't yet have a cascade-namespace directory; v2.1 retires it.

The `.solo-config.json` (workflow knobs) and `docs/.solo-locks/` (sentinel files) keep their existing locations — those serve different concerns and have established v0.1 paths the framework already commits to in `docs/templates/.solo-config.json.template` and `.gitignore`. Only run-state moves.

## Cross-references updated

- **D2.2** — references to `cascade:run-state` are path-agnostic in D2.2 itself, but the `.cascade/` namespace D2.2 introduces is now also the run-state home. No D2.2 amendment required; v2.1 simply confirms alignment.
- **D2.3 v1.3** — lockstep amendment (`D2_3_hybrid_session_boundary_v1_3.md`). Project Instructions block (step 1), §Cross-references, and the chat-end card handoff-prompt fence all reference the new path.
- **D4.6 v1.1** — lockstep amendment (`D4_6_cascade_resume_v1_1.md`). §CLI surface and §Halt conditions reference the new path.

## Migration note (v0.1 → v0.2)

A v0.1 consumer holding state at `docs/.solo-run-state.json` (the pre-v2.1 path) is not a real concern — no production consumers exist yet, and v0.1 itself did not surface `cascade:run-state` as a committed artifact (D2.1 v2 is the first declaration). The path change is therefore a clean break: the v0.2 cascade integration spec (`0001-v0.2-cascade-integration`) lands `.cascade/run-state.json` as the only path the framework ever ships.

`/onboard` step 7 (per D2.3 v1.3 §`/onboard` integration point) writes the initial run-state file at the v2.1 path. Hand-rolled migration for any pre-v0.2 consumer is a one-line `mv` — out of scope for this amendment.

## Cross-doc verification (sanity check)

After v2.1, v1.3, and D4.6 v1.1 land jointly, the following greps should all return zero hits across the design corpus:
- `docs/\.solo-run-state` — retired
- `docs/\.cascade/run-state` — retired (was D2.3 v1.2 and D4.6 v1's mispath)

And the following should be the only canonical reference:
- `\.cascade/run-state\.json` at repo root — the v2.1+ canonical path

The 0001 integration spec's executing session should run these greps as a pre-flight sanity check before authoring any code that touches `cascade:run-state`.
