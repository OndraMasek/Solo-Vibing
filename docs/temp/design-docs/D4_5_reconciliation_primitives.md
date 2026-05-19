# D4.5 — Reconciliation primitives

**Status:** Design (v1 — authored 2026-05-19).
**Phase:** 4 (Cleanup and concrete fixes).
**Resolves:** F-6 (recovery is nuclear-only — SOL-95) fully.
**Depends on:** D2.1 v2 (manifest provenance, run-state lock — the recovery primitives operate against the manifest chain D2.1 v2 establishes); D3.4 (gate definitions — recovery is triggered by gate halts); D4.0 (`solo-verify` exit code 3 routes here).
**Position in Phase 4 plan:** parallel with D4.1 and D4.2. Independent of both. The most load-bearing of the three Phase 4 design docs because the F-6 finding ("the only sanctioned backward move is `/specify --unseal` which discards the correct work") was named in the v0.1 disaster as a direct contributor to operator-spend.

## Decision

v0.2 introduces five recovery primitives, each targeted at one observed failure class:

1. **`--reconcile`** — across `/build`, `/wrap`, `/specify`, `/plan`. Idempotent diff-and-repair: read all observable state, compute declared-vs-observed diff, repair only the gap.
2. **`--rerun=<stage>`** — across `/specify`, `/review`, `/plan`. Targeted re-run of one cascade stage against the current spec, re-binding provenance, no re-draft of upstream stages.
3. **`--preflight`** — on `/build`. Runs the full precondition set in report-only mode, no spawn, no spend.
4. **Frozen-AC primitive.** A flag at the AC level (`frozen: true`) that prevents re-decomposition. Decomposer halts §frozen-ac-re-decomposed on any attempt to re-decompose a frozen AC.
5. **Halt memoization.** Within a session, identical halts emit a one-line "unchanged since turn N; required action still X" instead of re-deriving the full halt card.

`/specify --unseal` is retained as the explicit nuclear option (destroy + redraft) but is no longer the only sanctioned backward move. Its use becomes rare — escape-hatch for genuine spec rewrites, not routine recovery.

## Why this matters (recap of F-6)

From the F-6 finding: the cascade's recovery surface was designed around "the founder edits the spec mid-cascade" — a low-frequency case. The actually-observed high-frequency cases — stale subagent record, partial completion, label/state desync, missing provenance — had no first-class recovery. `--unseal`'s "destroy + redraft" semantics discarded the correct upstream work. Operator response was to override the unseal recommendation, which compounded the state desync.

The fix is a recovery surface that maps to actual failure classes:

| Observed failure class | Pre-v0.2 response | v0.2 response |
|---|---|---|
| Stale subagent record (four-hat outcomes file present but invocation didn't actually complete) | Operator manually re-invoked the subagent; provenance broken | `/specify SOL-N --rerun=four-hat` rebinds provenance, no spec redraft |
| Partial `/wrap` (Linear write succeeded, filesystem mirror failed) | No primitive; manual filesystem catch-up; provenance broken | `/wrap SOL-N --reconcile` reads Linear, computes filesystem diff, writes the gap |
| Partial `/build` (Ralph spawned but `cascade:run-state` not updated) | Operator manually edited run-state; or killed and respawned (full re-spend) | `/build SOL-N --reconcile` reads filesystem state, repairs run-state, attaches existing Ralph run if PGID still alive |
| Founder edits a frozen AC mid-cascade | Decomposer silently re-decomposed against the new AC; produced inconsistent children | Decomposer halts §frozen-ac-re-decomposed; founder must explicitly unfreeze or unseal |
| Same halt re-emitted across 5+ turns | Halt card re-rendered in full each time, ~2-3k tokens per turn | Halt memoization renders one-liner reference to the first emission |

## Primitive 1: `--reconcile`

**Available on:** `/build`, `/wrap`, `/specify`, `/plan`.

**Semantics:** read all observable state (filesystem manifests, Linear state via MCP, git state via `git status`), compute the declared-vs-observed diff against `cascade:run-state`'s expectations for the named stage, repair only the gap. Idempotent — running `--reconcile` twice in a row produces the same final state as running it once.

**Required behavior on any partial-completion fingerprint:** the cascade's hook surface (per D2.2) detects partial-completion patterns and surfaces a §partial-completion halt with `--reconcile` as the named recovery action.

### `/build <ticket> --reconcile`

Reads:

- `.cascade/manifests/<ticket>-build.json` (declared state from the spawn)
- `<worktree>/.ralph/` (actual Ralph state — pgid, iter counter, fix_plan, claude.jsonl files)
- `cascade:run-state.json` (whether this build is registered as live)
- Linear via MCP (current ticket status, comments since last cascade write)

Diff cases:

- **Manifest says Ralph live, run-state says live, but no PGID alive:** Ralph died. Write the completion comment with `result: killed-externally`, update Linear state, release the run-state lock. No new spawn.
- **Manifest says Ralph live, run-state says live, PGID alive but fix_plan unchanged across last 3 iter:** Ralph is wedged. Surface to founder for kill decision (don't auto-kill; F-7's full distributed-locking is deferred and we don't want to false-positive).
- **Manifest says built, Linear says still in-progress:** Linear write didn't land. Re-attempt the Linear state transition; if it succeeds, complete reconciliation; if it fails repeatedly, halt §linear-unreachable.
- **Filesystem state says built but no `/wrap` ran:** clean state for `/wrap` to pick up. Reconciliation logs the discrepancy and exits clean.

### `/wrap <ticket> --reconcile`

Reads:

- `.cascade/manifests/<ticket>-wrap.json`
- Linear ticket state via MCP
- `docs/product/*.md` (filesystem mirror per D0.1 §Product-doc outline pattern)
- `.cascade/manifests/<ticket>-build.json` (the upstream manifest)

Diff cases (high frequency, the main motivator):

- **Linear updated, filesystem mirror not synced:** write the missing filesystem outline updates.
- **Filesystem mirror written, Linear ticket not transitioned:** transition the Linear state, attach the completion comment.
- **Both writes attempted but ADR-mirror missing from Architecture project:** emit the missing ADR if the cascade's record shows one should exist.

### `/specify <ticket> --reconcile`

Reads:

- `.cascade/manifests/<ticket>-specify.json`
- The spec file at its declared path
- The four-hat outcomes files

Diff cases:

- **Manifest says four-hat complete, outcomes file missing:** provenance broken. Caller-side per D2.1 v2 should have caught this. `--reconcile` here verifies and surfaces; doesn't automatically re-run (use `--rerun=four-hat` instead).
- **Spec file `spec_sha256` doesn't match manifest's `ac_list_sha256`:** founder edited the spec after seal. Halt §spec-edit-after-seal with recovery options: `--rerun=four-hat` if the edit was a four-hat finding application, or `--unseal` if a full redraft is intended.

### `/plan <ticket> --reconcile`

Reads:

- `.cascade/manifests/<ticket>-plan.json`
- All child manifests for the plan's children
- Linear states for each child

Diff cases:

- **Plan declared N children, M exist in Linear:** identify the missing children, emit them; or identify the orphan children, halt §plan-orphan-children.
- **Child manifests have stale upstream sha:** parent spec was edited after plan was sealed. Halt §plan-stale; recovery is `/plan --rerun=decompose` if the new spec is compatible.

### Exit semantics

`--reconcile` exits zero if the state was already consistent (no-op), zero if reconciliation succeeded (state now consistent), non-zero if reconciliation found a state it can't safely repair (halt card emitted; founder action required). It doesn't infinite-loop and doesn't autonomously re-invoke upstream stages — that's `--rerun=<stage>`'s job.

## Primitive 2: `--rerun=<stage>`

**Available on:** `/specify`, `/review`, `/plan`.

**Semantics:** re-run one cascade stage against the current spec, re-bind its provenance record, recompute checksum, **no re-draft of upstream stages**. The stage's prior outputs are replaced; downstream stages are invalidated and must be re-run separately.

### Stage list

```
/specify <ticket> --rerun=clarify        # re-run clarify-walker; no spec re-draft
/specify <ticket> --rerun=four-hat       # re-run four-hat panel; no spec re-draft
/specify <ticket> --rerun=decompose      # re-run decomposer; no spec re-draft (decomposition is a /plan input but lives in /specify per D3.1)
/review <ticket> --rerun                 # re-run /review's check set; no spec or plan change
/plan <ticket> --rerun=decompose         # re-decompose; halts on frozen ACs (see Primitive 4)
```

### Provenance binding

After `--rerun`, the new stage manifest binds to the unchanged upstream parent manifest. The downstream chain is invalidated:

- `--rerun=four-hat` invalidates `/review`, `/plan`, all child manifests below.
- `--rerun=decompose` (on `/plan`) invalidates all child manifests.
- `--rerun=clarify` invalidates four-hat and below.

Invalidation surfaces as §provenance-stale halts on the next access of any downstream stage; the founder explicitly runs those stages again.

### Halt conditions

- **§rerun-target-not-found:** the named stage doesn't exist on this ticket.
- **§rerun-spec-edited:** the spec was edited between seal and `--rerun`; `--rerun` operates on the sealed spec only. Recovery is `--reconcile` or `--unseal`.
- **§rerun-target-currently-active:** the named stage is currently running (live subagent, live Ralph). Wait or `--kill` first.

## Primitive 3: `--preflight`

**Available on:** `/build`.

**Semantics:** runs the full `/build` precondition set in report-only mode. No spawn, no Linear writes, no spend. Emits a structured report of every precondition: pass, halted (with halt card), or skipped (with reason).

### Why it exists

F-6 evidence: at least 5 preconditions failed serially on a cold SOL-65 after three full cascades of investment. Each failure surfaced after the prior precondition completed, requiring multiple cycles of fix-and-retry. `--preflight` runs the whole set in one pass before any spend.

### Precondition set (cited from `/build` SKILL.md)

The exact precondition list lives in the post-D4.2 spawn-skill (`.claude/skills/build/SKILL.md`); D4.5 doesn't enumerate them in full. The shape is:

- Spec sealed (`spec_sha256` present and matches)
- Plan complete (child manifests exist per `cascade:run-state`)
- Four-hat outcomes recorded (per D2.1 v2 provenance binding)
- Stack autodetect resolves (Makefile or AGENTS file or stack-explicit fallback per D4.1.3)
- `claude` binary available and responds (the smoke check per D4.1.2)
- `timeout` or `gtimeout` available per D4.1.11
- Worktree path available; no prior worktree conflicting
- Run-state lock available (no live Ralph for this parent per D2.1 v2)
- Denylist file present per D4.1.7

### Output

```
Preflight: SOL-42 (parent ticket)
  ✓ Spec sealed (spec_sha256 matches manifest)
  ✓ Plan complete (3 children: SOL-43, SOL-44, SOL-45)
  ✗ Four-hat outcomes missing for SOL-44 (manifest binding broken)
    → Recovery: /specify SOL-44 --rerun=four-hat
  ✓ Stack autodetect: python (Makefile detected)
  ✓ claude smoke: OK
  ✗ timeout: not available
    → Recovery: brew install coreutils (macOS) or apt install coreutils (Linux)
  ✓ Worktree clean
  ✓ Run-state lock available
  ✓ Denylist file present

2 preconditions halted; /build will not spawn until these are resolved.
```

Exit code zero if all preconditions pass, non-zero (count of halts) if any fail.

## Primitive 4: Frozen-AC primitive

**Available on:** spec AC declarations.

**Semantics:** an AC declared `frozen: true` cannot be re-decomposed. Decomposer halts §frozen-ac-re-decomposed on any attempt. The founder must explicitly unfreeze (`/specify --unfreeze-ac SOL-N AC-3`) before re-decomposition is allowed.

### Why it exists

F-6 evidence: "Children covering frozen ACs MUST NOT be re-decomposed" was operator prose during unseal. With no first-class flag, the decomposer treated every `/plan --rerun=decompose` as a clean slate and produced re-decompositions that broke downstream provenance.

### Spec syntax

```markdown
## Acceptance criteria

### AC-1: Hostile mob targets the player within 5m
- **Frozen:** true (SOL-67 child built and verified; do not re-decompose)
- **Verifies via:** smoke

### AC-2: Hit-pause renders exactly 3 frames
- **Frozen:** false
- **Verifies via:** perceptual
```

The `Frozen` line defaults to `false`. The cascade auto-freezes an AC when its covering child reaches `scope:built` and `scope:verified`; the founder can also manually freeze.

### Halt cards

- **§frozen-ac-re-decomposed:** the decomposer attempted to re-decompose a frozen AC. Halt card includes the AC ID, the child that currently covers it, and the unfreeze command.
- **§frozen-ac-not-found:** unfreeze attempted on an AC that isn't frozen. No-op halt; warns and exits clean.

## Primitive 5: Halt memoization

**Available on:** every halt-card-emitting code path.

**Semantics:** within a single session, the cascade tracks every halt card it emits. Re-emission of an identical halt (same code, same ticket, same diagnostic context hash) renders as a one-line reference instead of a full halt card.

### Format

First emission (full card):

```
§spec-edit-after-seal: SOL-42

The spec at docs/specs/SOL-42-arena/spec.md was edited after seal.
Manifest spec_sha256 = abc123…; current file sha256 = def456…

Recovery options:
  /specify SOL-42 --reconcile     (if the edit was a finding application)
  /specify SOL-42 --rerun=four-hat (re-run four-hat against new spec)
  /specify SOL-42 --unseal         (full re-draft; discards downstream)
```

Subsequent emissions in the same session:

```
§spec-edit-after-seal: SOL-42 (unchanged since turn 17; recovery still as previously listed)
```

### Why it exists

F-12 evidence: per-turn static instruction reinjection compounds across long sessions. Halt cards are part of that overhead — a 2-3k token card emitted 5 times across 5 turns adds up to ~12k tokens, most of it identical.

### Bounds

- Memoization is per-session (resets when `cascade:run-state` resets, per D2.2).
- Session-end summaries (e.g. `/retro`) re-emit full cards even for memoized halts, so the historical record stays complete.
- Different `<diagnostic context hash>` → different halts → not memoized together. Specifically: a halt for SOL-42 and the same halt for SOL-43 don't deduplicate.

## What v0.2 does not ship

1. **Auto-recovery.** All five primitives surface options; none auto-execute. The cascade reports "here are your recovery paths" and waits for the founder. Auto-recovery is a v0.3+ conversation tied to D3.4's autonomy mode escalation.
2. **`--reconcile --dry-run`.** Dry-run reports the diff without writing. Useful, but adds a flag matrix. Defer to v0.2.x; the first ship is `--reconcile` always writing.
3. **`--rerun=four-hat=engineer-only`.** Re-running only one of the four hats. F-6 evidence didn't surface this need; v0.2 re-runs the whole panel. Defer to v0.2.x if observed.
4. **Frozen-AC granularity beyond per-AC.** Per-section freeze (freeze a `## Architecture` section but not the ACs) is a generalization not warranted by current evidence. Defer.
5. **Cross-session halt memoization.** Memoization across sessions would require persisting the halt registry. v0.2 memoizes within a session only; the registry resets each new session.

## Files this introduces

New files:

- `.claude/skills/reconcile/SKILL.md` (the reconcile-shared logic, `@`-imported by `/build`, `/wrap`, `/specify`, `/plan`)
- `.claude/skills/rerun/SKILL.md` (the rerun-shared logic, `@`-imported by `/specify`, `/review`, `/plan`)
- `.claude/skills/preflight/SKILL.md` (the preflight, `@`-imported by `/build`)
- `.claude/rules/halt-memoization.md` (the memoization protocol, `@`-imported by every skill that emits halt cards)
- `docs/templates/halt-messages.md` updates (six new halt codes: §partial-completion, §frozen-ac-re-decomposed, §frozen-ac-not-found, §rerun-target-not-found, §rerun-spec-edited, §rerun-target-currently-active)

Updated files:

- `/build` SKILL.md (post-D4.2): adds `--reconcile`, `--preflight` flag handlers; cites the reconcile and preflight shared skills.
- `/wrap` SKILL.md: adds `--reconcile` flag handler.
- `/specify` SKILL.md: adds `--reconcile` and `--rerun=<stage>` flag handlers, plus the AC `Frozen` field parser.
- `/plan` SKILL.md: adds `--reconcile` and `--rerun=decompose` flag handlers; decomposer reads the AC `Frozen` field.
- `/review` SKILL.md: adds `--rerun` flag handler.

`solo-verify` updates:

- `solo-verify reconcile <stage> <ticket>` is **not** a thing. `--reconcile` is a cascade operation, not a gate evaluation. Gate evaluation (via `solo-verify`) is what *triggers* reconciliation by returning exit code 3 (provenance halt) per D4.0; the founder runs `--reconcile` in response.

## Implementation order

The primitives are largely independent but share infrastructure. Suggested order for one or two Code sessions:

1. **Halt memoization first.** Smallest, lowest risk, immediate token savings. One rule file, citations across all halt-emitting skills.
2. **`--preflight` second.** Read-only; testable against existing manifest fixtures. Doesn't touch state.
3. **Frozen-AC primitive third.** AC syntax change + decomposer-side halt. Backward-compatible (default `frozen: false` preserves current behavior).
4. **`--reconcile` fourth, one stage at a time.** Start with `/wrap` (highest-frequency need per F-6 evidence). Then `/build`, then `/specify`, then `/plan`.
5. **`--rerun=<stage>` fifth.** Most complex (provenance invalidation propagation). Land after `--reconcile` so the surrounding machinery is in place.

Estimated effort: 2 short Code sessions or 1 medium one.

## Open items

- **`--reconcile` and `solo-verify`'s exit code 3.** D4.0 says exit code 3 (provenance halt) "routes to `--reconcile`". This means the cascade's hook surface, on receiving an exit-3 from `solo-verify`, surfaces the §partial-completion halt with `--reconcile` as the named recovery. Confirm the hook routing in D2.2's implementation pass.
- **Manifest schema additions.** `cascade:run-state` may need a `halts_memoized[]` field for cross-stage halt deduplication. Or memoization can be entirely in-session memory. Decide during implementation; in-memory is simpler if hooks allow.
- **AC `Frozen` parser location.** The spec template's AC structure is owned by `/specify`'s SKILL.md. Confirm with the `/specify` template surface (D3.1 reference) before adding the `Frozen` field; may need a small spec-template version bump.

## Cross-references

- **D2.1 v2** — provenance binding is the foundation. `--reconcile` operates on the manifest chain D2.1 v2 establishes. The halt-memoization rule is independent of D2.1 v2 but cites it for halt-card structure.
- **D2.2** — hook surface invokes `--reconcile` on detected partial-completion patterns. Halt memoization lives in the in-session state D2.2 manages.
- **D3.4** — gate halts surface recovery options; D4.5 names what those recovery options are.
- **D4.0** — `solo-verify` exit code 3 → `--reconcile` routing.
- **D4.2** — `/build-status` could surface the memoized halt summary cheaply.

## Note on naming

`--reconcile` is overloaded in some software conventions to mean "force-pull and merge." Here it means "diff observable state against declared state and repair the gap." If the verbal collision causes confusion in practice, rename to `--repair-state` or `--sync-state` in v0.2.x. The semantics are what matters; the flag name is the surface.
