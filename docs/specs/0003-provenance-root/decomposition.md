# 0003 — Decomposition sketch

**Status:** Re-sealed into repo (SOL-126) — reconstructed from the 2026-05-29 chat-Claude `/plan` run recorded on SOL-112 (the `/plan complete` comment) and the two sealed child tickets SOL-117 / SOL-118. The cascade's decomposer did not write this to disk at /plan time (the bootstrap-exception /plan ran without sealing a `/plan` manifest — doing so would have preempted AC-1/AC-2). Structured to match what `/plan` would produce so a Code session can consume it as-is.

**Parent:** `0003-provenance-root` (SOL-112).
**Parent strategy:** `walking-skeleton` — declared at /plan. One end-to-end thread: a real sealed root that `preflight-provenance.sh` reads and passes against. Both children inherit `walking-skeleton`.

---

## Children at a glance

| Child | Logical id | Linear | Classification | Strategy | Scope |
|---|---|---|---|---|---|
| 0003-1 | SOL-112-1 | SOL-117 | vertical | `walking-skeleton` (inherited) | Seal the provenance root from real merged 0001/0002 evidence. Covers AC-1–5. `scope:sealed`. |
| 0003-2 | SOL-112-2 | SOL-118 | horizontal | `walking-skeleton` (inherited) | Retire the bootstrap exception. Covers AC-6. `scope:sealed`. **blockedBy SOL-117.** |

Two children, sequential. No nested hybrid; the parent strategy is `walking-skeleton`, so children inherit it directly (no per-child override negotiation as a `hybrid` parent would require).

## Parallelization

- **Wave 1:** SOL-117.
- **Wave 2 (after Wave 1):** SOL-118.

Sequential — no parallel-eligible siblings, so no worktree fan-out. SOL-118 is a documentation/provenance breadcrumb that is meaningful only once SOL-117's root exists and `preflight-provenance.sh` verifies against it.

---

## Child 0003-1 — Seal the provenance root (SOL-117)

**Strategy:** `walking-skeleton` (inherited).
**Classification:** vertical.
**Blockers:** none.
**Covers:** parent AC-1, AC-2, AC-3, AC-4, AC-5.

**Rationale.** The end-to-end thread that makes `preflight-provenance.sh` a live gate. The thin vertical slice runs `/onboard` to write the committed run-state floor, seals the manifest link the next cascade stage chains to from real merged evidence, and proves the hook exits 0 against the committed root.

**What this child delivers:**

1. Run real `/onboard` to write the committed `.cascade/run-state.json` floor (`schema_version "2.1-v2.1"`, reachable by `read_run_state`) and seal `.cascade/manifests/<marker>-onboard.json` from `/onboard`'s own observable outputs (six Linear projects, Status doc, config). **AC-1.**
2. Seal the manifest link the next cascade stage chains to: produce the `/specify`-stage 0002 manifest the immediate upstream `/review <0002-ticket>` validates, recomputing each `outputs` entry from **real merged evidence** (PRs #5–#8, on-disk spec/artifact paths, Linear ids) with `manifest_sha256` self-zeroed via `sha256_manifest_self_zeroed`; point `run-state.last_completed_stage.postcondition_manifest_path/_sha256` at it. **AC-2.**
3. `preflight-provenance.sh` with payload `{"prompt":"/review <a-real-0002-ticket>"}` against the committed root exits 0, empty stdout/stderr. **AC-3.**

**Critical build constraints (from /plan decomposition findings):**

* `solo-verify` **evaluates; it does not seal.** There is no `--rerun` flag and `--reconcile` is drift-detection-only in v0.2. So AC-4's "seal" = the build agent **writes** the manifest JSON from real evidence, then **confirms** it by running `solo-verify <stage> <ticket>` and keeping the manifest only if it **exits 0**. No asserted passes, no hand-written shas.
* **AC-4 audit note:** record in `docs/specs/0003-provenance-root/authoring-notes/seal-provenance.md`, per sealed manifest: exact `solo-verify` command, exit code (0), the real merged artifact each `outputs` entry maps to (PR #, on-disk path, or Linear id), and the sha-compute command. Re-running the seal over the same merged state must reproduce identical shas (determinism = recompute-not-fabrication).
* **AC-5 halt-and-file:** if any `solo-verify` invocation **halts** (non-zero), STOP — do not write/keep the manifest, do not edit a sha to force green, do not waive. File a `type:infra`/`type:design` Linear finding ticket citing the halting gate + missing evidence, and surface `BLOCKED`. Route the finding write through the sanctioned path (confirm `.claude/agents/build-write-denylist.txt` does not block it). A halt means 0001/0002 shipped a real gap.

**Pyramid shape:** `walking-skeleton`-shaped. The parent spec has no `## Failing-test seed` section (chat-authored); seeds are AC-derived from each "Verifies via:" clause (carried as a sub-threshold concern at /review check b, documentary/bootstrap disposition — not halted).

**Failing-test seed (AC-derived):**

- (a) **AC-3 smoke** — hook-invocation harness mirroring `test_preflight_provenance_passes_on_intact_chain`: feed `preflight-provenance.sh` the `{"prompt":"/review <real-0002-ticket>"}` payload against the committed root; assert exit 0, empty stdout, empty stderr. Starts RED (no run-state; manifests dir is `.gitkeep`-only).
- (b) **AC-2 contract** — `sha256_manifest_self_zeroed` over each sealed manifest equals the sha the run-state/chain carries.
- (c) **AC-1 smoke** — `read_run_state` loads `.cascade/run-state.json`; parses against the `"2.1-v2.1"` schema.
- (d) **AC-4 contract+invariance** — every chain manifest has a recorded exit-0 `solo-verify <stage> <ticket>` run in `seal-provenance.md`; re-running the seal reproduces identical shas.
- (e) **AC-5 smoke** — a deliberately-broken fixture chain (e.g. a manifest naming a perceptual artifact 0001/0002 never produced) drives `solo-verify` non-zero and the build path halts-and-files rather than sealing.

**Notes for the executing /build session:**

- Sealed under the final documented bootstrap exception (no upstream manifest; SOL-112 is the feature that creates the first legitimate root).
- SOL-113 (hooks), SOL-115 (Python 3.10+), and SOL-116 (four-hat `_lib`) are all merged, so the hook substrate loads and `solo-verify` runs under 3.10+.

---

## Child 0003-2 — Retire the bootstrap exception (SOL-118)

**Strategy:** `walking-skeleton` (inherited).
**Classification:** horizontal.
**Blockers:** SOL-117 (child 1).
**Covers:** parent AC-6.

**Rationale.** Documentation/provenance breadcrumb only — no legitimacy logic of its own; meaningful only once SOL-117's root exists and `preflight-provenance.sh` verifies against it.

**What this child delivers.** Update `docs/specs/0002-v0.2-release-wrap-up/authoring-notes/bootstrap-exception.md` (or a successor note under `docs/specs/0003-provenance-root/`) to state the root is established, naming the 0003 PR and the sealed manifest path(s) produced by SOL-117. After this, future `/build` runs no longer carry a bootstrap exception — `preflight-provenance.sh` is a live gate, not a waived one.

**Pyramid shape:** AC-6 verifies via **perceptual** only — no executable seed.

**Failing-test seed.** None executable. Perceptual check (asserted at /verify by inspection): the bootstrap-exception note (or successor) records the root's existence, names the 0003 PR and sealed manifest path(s), and no longer authorizes a standing exception.

---

## Build order (recommended)

1. **0003-1 (SOL-117)** first — the delicate AC-4/AC-5 work: executed exit-0 `solo-verify` seals over real merged 0001/0002 state, halt-and-file on any verify failure. Explicit founder go required per the constitution's "Not autonomous shipping" + CLAUDE.md.
2. **0003-2 (SOL-118)** second, after SOL-117's root verifies — the one-line provenance breadcrumb retiring the exception.

---

## /plan run disposition (bootstrap-exception waiver)

Per the spec's final documented bootstrap exception, this `/plan` ran with the `plan.provenance` gate **waived** (`.cascade/run-state.json` absent → `§provenance-chain-broken`) and **did not** seal a `/plan` manifest or write run-state — doing so would preempt AC-1/AC-2 (SOL-117's `/onboard` legitimately creates the floor + manifest links). The exception is retired by SOL-118 once SOL-117's root verifies. Parent transitioned `scope:specified` → `scope:planned`.

## Build-critical notes carried from /plan

- `solo-verify` **evaluates, doesn't seal**: AC-4's "seal" = write manifest from real evidence, then confirm via an exit-0 `solo-verify <stage> <ticket>` (no `--rerun`; `--reconcile` is drift-detection-only in v0.2).
- AC-5 halt-and-file must route the finding-ticket write through the sanctioned (non-denylisted) path and surface `BLOCKED`.
- Parent `ac_list_sha256` treated as documentary this cycle (SOL-111 — the canonical recompute yields the empty-string hash for `**AC-N**` specs).
