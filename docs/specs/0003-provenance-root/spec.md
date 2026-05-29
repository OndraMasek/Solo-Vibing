# 0003 — Establish a legitimate provenance root

**Linear:** SOL-112 (`[SOL] Backlog`, team Solo Claude Stack).
**Repo:** `OndraMasek/Solo-Vibing` (target). This Linear workspace is the meta-project tracking surface.
**Sealed:** 2026-05-29, /specify step-7 (chat-Claude session, Solo Claude Stack design project). `ac_list_sha256 = 1c9c7549b8f600bd`. Four-hat review attached, unresolved_count = 0 (E-2/S-1 resolved into AC-4/AC-5; see four-hat doc).
**Strategy:** declared at /plan; recommended `walking-skeleton` (one end-to-end thread: a real sealed root that `preflight-provenance.sh` reads and passes against).
**Bootstrap exception:** this spec is sealed under the final documented bootstrap exception — it is the feature that creates the first legitimate root, so it has no upstream manifest to chain from. 0004+ chain normally.
**Authored:** 2026-05-29, chat-Claude session (Solo Claude Stack design project).

---

## Problem

Every `/build` since the v0.2 cascade landed has run under a **founder-authorized bootstrap exception**: the provenance chain that v0.2 introduces cannot exist for the very work that introduces it. `preflight-provenance.sh` reads `.cascade/run-state.json` → `last_completed_stage.postcondition_manifest_path` + `_sha256` → a sealed manifest, and re-verifies the sha (with `manifest_sha256` zeroed) before any `/review`, `/plan`, `/update-linear`, `/build`, `/wrap`, `/verify`, `/retro` prompt is admitted. None of that root state exists or is recoverable for 0001/0002:

* `.cascade/run-state.json` was never committed with a populated `last_completed_stage`.
* `.cascade/manifests/` contains only `.gitkeep` — no sealed manifest for 0001 or 0002.

Consequence: the gate cannot fire against real upstream state, so every cascade stage either halts §provenance-chain-broken (if the hook were live) or proceeds only because the founder waived the gate. The cascade **cannot self-enforce** until a real root exists.

## Goal

Produce a legitimately-sealed provenance root — a committed `.cascade/run-state.json` whose `last_completed_stage` points at a committed, sha-verifiable manifest — such that `preflight-provenance.sh` passes (exit 0) for the next cascade stage that runs against it, **without fabricating any hash or manifest content.**

## Non-negotiable constraint (carried from the bootstrap-exception note)

The root MUST be produced by a legitimate sealing operation. Hand-writing a manifest, back-filling a plausible-looking sha256, or copying a sha from a non-corresponding artifact is **explicitly forbidden** — it would defeat the entire trust model (manifest existence ≡ all gates passed). A root that was hand-faked is worse than no root, because the gate would then pass on a lie.

## Design surface — the two candidate mechanisms

Per D2.1 v2.1 / D2.2, `.cascade/run-state.json` is written by exactly two sanctioned paths. The spec must pick one (or define a third) and justify it against the no-fabrication constraint.

1. `/onboard` **(the cascade bootstrap).** Per D2.1 v2.1 §Migration note and D2.3 v1.3 §`/onboard` integration point, `/onboard` step 7 writes the **initial** run-state file. By construction `/onboard`'s own state has `last_completed_stage.postcondition_manifest_path = null` (it is the chain start — `preflight-provenance.sh` lines 91–99 treat null as "no upstream", and `/onboard` is excluded from the matcher entirely). So `/onboard` establishes a *run-state* but **not** a non-null manifest root that downstream stages chain to. It seals `/onboard`'s own manifest, which becomes the first real link.
2. `solo-cascade resume` **(D4.6 v1.1).** Explicitly **read-only** with respect to manifests — it re-derives the chat-end card and handoff prompt by *reading* the last sealed manifest. D4.6 §Halt conditions: it halts §cascade-state-missing if run-state is absent and §cascade-resume-manifest-chain-broken if the named manifest is absent/unparseable, routing to D4.5. `solo-cascade resume` **cannot create a root** — it consumes one. It is therefore disqualified as the root-establishing mechanism, though it is the correct *recovery* tool once a root exists.

### Recommended approach (for /plan to ratify or reject)

`/onboard` **establishes the run-state floor; a targeted re-seal of the already-merged 0001 + 0002 work establishes the manifest links.** Concretely, the legitimate operations available are:

* `/onboard` writes `.cascade/run-state.json` with `last_completed_stage = null` and seals `.cascade/manifests/<onboard>.json` from its own observable outputs (Linear projects exist, config written) — real evidence, real seal.
* `--reconcile` **/** `--rerun=<stage>` **(D4.5)** are the idempotent diff-and-repair primitives. `--reconcile` reads *observable* state and repairs the manifest/run-state gap. For 0001/0002, the observable state is real and durable: merged PRs (#5–#8), the sealed spec files on disk (`docs/specs/0001-*`, `0002-*`), the Linear tickets in their terminal states, and the actual built artifacts (28 gates, 8 hooks, `solo-verify`). A `--reconcile`-style re-seal recomputes manifest checksums **from that real merged state** — it is recompute-from-evidence, not fabrication.

The spec's job is to define **which legitimate operation seals the 0001 and 0002 manifests from the real merged evidence**, and in what order, so that after this feature `preflight-provenance.sh` chains cleanly: `run-state.last_completed_stage` → 0002's terminal-stage manifest → … → 0001's chain → `/onboard`'s root.

### The fabrication boundary (must be explicit in the built artifact)

A manifest sha computed by hashing the manifest's own real `outputs` (paths, linear_ids, doc_ids that actually exist post-merge) with `manifest_sha256` zeroed, per `sha256_manifest_self_zeroed`, is **legitimate** — it is a checksum of real, present evidence. What is forbidden is asserting a manifest whose `outputs` claim gates passed that were never evaluated, or whose sha was chosen to satisfy the verifier rather than computed from content. The distinction the spec must encode: **recompute over evidence that exists = legitimate; assert a value to make the gate pass = fabrication.**

## Acceptance criteria

**AC-1 —** `/onboard` **writes a committed run-state floor.**
After this feature, `.cascade/run-state.json` exists, is committed, parses against the D2.1 v2.1 schema (`schema_version` = `"2.1-v2.1"`), and is reachable by `read_run_state` in `preflight-provenance.sh`. Verifies via: smoke.

**AC-2 — A sealed root manifest exists and sha-verifies.**
At least one manifest exists under `.cascade/manifests/` whose recomputed sha (via `sha256_manifest_self_zeroed`, `manifest_sha256` field zeroed) equals the value `run-state.last_completed_stage.postcondition_manifest_sha256` carries (or, for the `/onboard` floor, `last_completed_stage` is legitimately `null` and the manifest is the onboard manifest the next link chains from). Verifies via: smoke + contract (sha recompute matches).

**AC-3 —** `preflight-provenance.sh` **passes against the root.**
Running `preflight-provenance.sh` with a payload `{"prompt": "/review <a-real-0002-ticket>"}` (or the appropriate next stage) against the committed root exits 0 with empty stderr and empty stdout — i.e. the chain is intact, no §provenance-chain-broken. Verifies via: smoke (hook invocation harness, mirrors `test_preflight_provenance_passes_on_intact_chain`).

**AC-4 — Each sealed manifest is produced by an executed, passing** `solo-verify` **run (no asserted passes).**
Every manifest that becomes part of the root chain MUST be sealed by an actual `solo-verify <stage> <ticket>` invocation that **exited 0** over the merged 0001/0002 state. The seal asserts only what a verifier actually evaluated — "manifest existence ≡ all gates passed" holds because the gates were *run now*, against the real merged artifacts, not back-asserted. A short audit note committed under `docs/specs/0003-provenance-root/authoring-notes/seal-provenance.md` records, for each sealed manifest: the exact `solo-verify` command, its exit code (must be 0), the real merged artifact each `outputs` entry maps to (PR number, on-disk path, or Linear id), and the command that computed each sha. No sha or `outputs` entry may lack a real-evidence source, and no manifest may be sealed without a recorded exit-0 verifier run. Verifies via: contract (every manifest has a recorded exit-0 `solo-verify` run) + perceptual (the note exists, every manifest entry is accounted for) + invariance (re-running the seal computation over the same merged state reproduces the same shas — determinism proves recompute-not-fabrication). **This AC depends on** SOL-113 **(hook-sourcing fix) being merged first**, because the seal/verify path exercises the hook substrate, and on SOL-115 (Python 3.10+) so `solo-verify` can run.

**AC-5 — A halt during root-seal surfaces a finding; it never produces a faked seal.**
If any `solo-verify <stage>` invocation during root-seal **halts** (non-zero exit — e.g. a perceptual artifact a gate expects was never produced by 0001/0002, or a pyramid-shape mismatch), `/build` MUST stop and surface the specific gate gap as a new Linear finding (a `type:infra`/`type:design` ticket citing the halting gate and the missing evidence). It MUST NOT fabricate a passing seal, hand-edit the manifest, or waive the gate to proceed. A halt here is the trust model working correctly: it means 0001/0002 shipped with a real gap that must be fixed (or explicitly, separately, accepted by the founder) before a root can legitimately exist. Verifies via: smoke (a deliberately-broken fixture chain causes `/build` to halt-and-file rather than seal).

**AC-6 — Bootstrap exception is formally retired.**
`docs/specs/0002-v0.2-release-wrap-up/authoring-notes/bootstrap-exception.md` (or a successor note under 0003) is updated to record that the root now exists, naming the 0003 PR and the sealed manifest path(s). Future `/build` runs no longer carry a bootstrap exception. Verifies via: perceptual.

## Out of scope

* Implementing `solo-cascade resume` changes (it is correct as designed; this spec only confirms it is the wrong tool for *creating* a root).
* SOL-113 (hook-sourcing `_lib.sh` defect) — separate ticket, **prerequisite** to AC-3/AC-4 actually executing, but its own spec/build.
* SOL-114 (`/onboard --dry-run`) — separate capability; this spec uses real `/onboard`, not the dry-run preview.
* SOL-115 (Python 3.10+ pin) — prerequisite for `solo-verify` to *run* during seal/verify, but doc-and-guard scope of its own.
* Retroactively sealing manifests for any work prior to 0001.

## Dependencies and sequencing

* **Hard prerequisite:** SOL-113 (hooks must source the real `common.sh`, else the seal/verify path errors under `set -u`).
* **Soft prerequisite:** SOL-115 (`solo-verify` must parse under the env Python, else the seal command can't run).
* **Unblocks:** removal of the standing bootstrap exception for all future cascade work; makes `preflight-provenance.sh` a live gate rather than a waived one.

## Cascade artifacts

* spec.md: `docs/specs/0003-provenance-root/spec.md` (transcribe this description to disk at /build, per the SOL-107 re-seal pattern)
* four-hat doc: full text in the first comment on this ticket — `[SOL-DOC] Four-hat review — 0003 provenance root`
* decomposition.md: authored at /plan
* authoring-notes/seal-provenance.md: the AC-4 audit (authored at /build)

## Provenance

* This spec's `ac_list_sha256`: `1c9c7549b8f600bd` (computed over §Acceptance criteria at step-7 seal, per D2.1 v2.1 §`input_provenance.ac_list_sha256`).
* Parent manifest: **none yet — this is the feature that creates one.** The spec is sealed under a final, documented bootstrap exception; once 0003 builds, the exception is retired and 0004+ chain normally.
* Sealed by: chat-Claude session, 2026-05-29.

---

## Handoff to Code

This ticket is sealed (`scope:specified`). Code picks up directly: transcribe this description verbatim to `docs/specs/0003-provenance-root/spec.md` and the first-comment four-hat doc to `docs/specs/0003-provenance-root/four-hat-review.md` (SOL-107 re-seal pattern), then run `/plan`. **Do not start** `/build` **until** SOL-113 **is merged** (hard prerequisite) and SOL-115 is addressed (soft prerequisite).
