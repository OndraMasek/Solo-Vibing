# Decomposition: SOL-112 — Establish a legitimate provenance root

> Parent: SOL-112
> Children: 2
> Plan run: 2026-05-29 (iteration 1)
> Parent strategy: walking-skeleton (declared at /plan per the spec's §Strategy line; four-hat-ratified)

## Chunking rationale

A walking-skeleton: one end-to-end thread that turns `preflight-provenance.sh` from a waived/dead gate into a live one. The legitimacy-critical core (run-state floor + sealed manifest links + an executed exit-0 `solo-verify` seal + the halt-and-file discipline) is inseparable — splitting it further would break AC-3 (which needs the run-state and the manifest co-present to pass) and AC-4 (the seal *is* the executed-verify-with-audit-note operation that produces the manifests). So the core is one vertical child (SOL-117, AC-1–5). Retiring the bootstrap exception (AC-6) is a thin perceptual coda that only becomes true once the root exists, so it is a separate horizontal child (SOL-118) that strictly depends on SOL-117.

## Children
- **SOL-117** (logical SOL-112-1) — Seal the provenance root from real merged 0001/0002 evidence. Vertical. Covers AC: AC-1, AC-2, AC-3, AC-4, AC-5. Strategy: inherited (walking-skeleton).
- **SOL-118** (logical SOL-112-2) — Retire the bootstrap exception. Horizontal (provenance breadcrumb; no independent logic). Covers AC: AC-6. Strategy: inherited (walking-skeleton).

## Dependency graph
```
SOL-117 ──> SOL-118
```
(`SOL-118` blocked by `[SOL-117]` — the exception can only be retired once a verifying root exists.)

## Parallelization map
- Wave 1: SOL-117
- Wave 2 (after Wave 1): SOL-118

Sequential — no parallel-eligible siblings, so no worktree fan-out.

## Per-child blocks

### 1. Seal the provenance root from real merged 0001/0002 evidence  (SOL-117)

- Classification: vertical
- Strategy: inherited
- Description: Run real `/onboard` to write the committed `.cascade/run-state.json` floor and seal the onboard manifest from observable outputs (AC-1); seal the `/specify`-stage 0002 manifest the next `/review <0002-ticket>` chains to, recomputed from real merged evidence (PRs #5–#8, on-disk paths, Linear ids) with `manifest_sha256` self-zeroed (AC-2); confirm `preflight-provenance.sh` exits 0 against the committed root (AC-3). Each manifest is written from evidence then confirmed by an executed exit-0 `solo-verify <stage> <ticket>` run, with a per-manifest audit note in `authoring-notes/seal-provenance.md` (AC-4). Any `solo-verify` halt stops the build and files a finding — never a faked seal (AC-5).
- AC: AC-1, AC-2, AC-3, AC-4, AC-5
- Failing-test seed: AC-derived (parent spec carries no §Failing-test seed) — (a) AC-3 smoke (preflight passes against root, starts RED); (b) AC-2 contract (`sha256_manifest_self_zeroed` matches chain sha); (c) AC-1 smoke (`read_run_state` parses `"2.1-v2.1"` schema); (d) AC-4 contract+invariance (recorded exit-0 `solo-verify` per manifest; deterministic re-seal); (e) AC-5 smoke (broken fixture chain → `solo-verify` non-zero → halt-and-file, not seal).
- Blockers: none

### 2. Retire the bootstrap exception  (SOL-118)

- Classification: horizontal
- Strategy: inherited
- Description: Update `docs/specs/0002-v0.2-release-wrap-up/authoring-notes/bootstrap-exception.md` (or a 0003 successor note) to record that the root exists, naming the 0003 PR and sealed manifest path(s); future `/build` runs no longer carry a bootstrap exception.
- AC: AC-6
- Failing-test seed: perceptual-only (AC-6 verifies via perceptual) — no executable seed; asserted at /verify by inspection of the updated note.
- Blockers: SOL-117

## Bootstrap-exception waiver (this /plan run)

SOL-112 is sealed under the final documented bootstrap exception (it is the feature that creates the first legitimate root — no upstream manifest exists). Accordingly, this `/plan` run was executed with the `plan.provenance` gate **waived** (`.cascade/run-state.json` is absent → `§provenance-chain-broken`), and it deliberately **did not** seal a `/plan` manifest or write `.cascade/run-state.json`. Writing run-state now would preempt AC-1 (SOL-117's `/onboard` legitimately creates the floor) and AC-2 (the manifest links). The cascade's own provenance for SOL-112's stages is bootstrap-exempt; the exception is retired by SOL-118 once SOL-117's root verifies.

## Decomposition findings (forwarded — DONE_WITH_CONCERNS, none halt-threshold)

- **med:** `solo-verify` evaluates but does not seal manifests (no `--rerun`; `--reconcile` is drift-detection-only in v0.2). AC-4's "seal" = write the manifest from evidence, then confirm via exit-0 `solo-verify <stage> <ticket>`. Baked into SOL-117's description so `/build` does not look for a non-existent CLI seal command.
- **med:** Parent spec has no `## Failing-test seed` / `## Decomposition strategy` section (chat-authored). Strategy declared here at /plan (walking-skeleton); seeds reverse-derived from each AC's "Verifies via:" clause. Parent has no seed, so the seed-subset gate (`plan.child-inheritance` P1) is skipped.
- **low:** AC-5's halt-and-file requires a Linear write from `/build` context; route through the sanctioned (non-denylisted) path and surface `BLOCKED`, not a silent skip.

## ac_list_sha256 note

The parent spec's sealed `ac_list_sha256 = 1c9c7549b8f600bd` is not reproducible by `solo-verify`'s canonical `_ac_list_sha256_from_spec` (which yields the empty-string hash for `**AC-N**`-formatted specs — the SOL-111 regex gap) nor by ~31 alternative canonicalizations. Per founder decision (2026-05-29) the value is treated as documentary for this cycle; SOL-111 is the tracked fix. See SOL-111.
