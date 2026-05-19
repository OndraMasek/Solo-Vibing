# D4.2 — Skill splitting

**Status:** Design (v1 — authored 2026-05-19).
**Phase:** 4 (Cleanup and concrete fixes).
**Resolves:** F-12 (token economics — read-only calls cost full skill bodies, SOL-101) fully; F-11 (ceremony bloat, SOL-100) partially (the operator-facing-skill-surface piece).
**Depends on:** D3.4 (autonomy mode — `/build` skill's invocation contract); D2.2 (session auto-management — token-budget telemetry that motivates the split).
**Position in Phase 4 plan:** parallel with D4.1 and D4.5. Independent of both.

## Decision

`/build` splits into three commands sharing a small common preamble:

- **`/build <ticket>`** — spawn a Ralph run (the heavyweight mode). Contains the spawn machinery, prompt rendering, fix_plan setup, four-hat invocation logic, finalize path.
- **`/build-status [<ticket>]`** — read-only inspection. Reports current Ralph state, recent iterations, cost so far, wall-clock, fix_plan check status. No write paths. No spawn machinery.
- **`/build-kill <ticket>`** — terminate a live Ralph run. Contains the kill protocol (process-group kill, orphan reaping, manifest update). No spawn machinery, no review machinery.

Three separate skill files at `.claude/skills/build/SKILL.md`, `.claude/skills/build-status/SKILL.md`, `.claude/skills/build-kill/SKILL.md`. Each fully self-contained, each invoked independently. The shared content (constants, the cascade-state-machine map, the cross-cutting safety invariants) lives in `.claude/rules/build-shared.md` and is `@`-imported by all three.

Lazy-loading deferred to v0.2.x; v0.2 ships the split as straight separation.

## Rationale

F-12 evidence: `/build` SKILL.md is ~6,000 words / ~250 lines, re-injected on every invocation regardless of mode. `--status` (a read-only operation that should cost <1k tokens of skill body) pays the same skill-injection cost as a full spawn. Across a long session this compounds.

The fix is mechanical: don't load the spawn skill when you're not spawning. Skills are loaded by command name, and Claude Code's skill resolver finds the SKILL.md adjacent to the command name. Three command names → three skill files → only one loads per invocation.

Why split rather than internally branch on a mode flag: the flag approach (`/build <ticket> --mode=status`) still injects the full skill body on every invocation. The Claude Code skill loader cannot do conditional partial loads inside a single SKILL.md. Three skill files is the only way to actually save the tokens.

Why three rather than two or four: spawn, status, kill are the three distinct verbs the founder issues. `--finalize` and `--continue` are spawn-mode subverbs and stay inside `/build`. `--reconcile` (per D4.5) is conceptually status-adjacent (reads state, computes diff, writes targeted fixes) but is named separately as `/build --reconcile` to keep it ringfenced from routine status reads. v0.2 ships three skills; if `/build --reconcile` proves heavyweight enough to warrant its own skill in v0.2.x, it gets one then.

## What each skill contains

### `/build <ticket>` (the spawn skill)

Roughly two-thirds the content of the current `/build` SKILL.md. Includes:

- Preconditions check (spec sealed, plan complete, four-hat outcomes recorded, no live Ralph for this ticket — last via the run-state lock from D2.1 v2)
- Stack autodetect (Makefile detection, AGENTS file detection, fallback to skill-defined defaults)
- `PROMPT.md`, `fix_plan.md`, `run.sh` rendering from templates
- Ralph spawn (`setsid claude -p ...` per D4.1.9)
- Pre-flight smoke (`claude -p "reply OK"` per D4.1.2)
- Four-hat invocation (cited from D3.4)
- Iteration loop monitoring (cost cap, wall cap, iter cap, drift detection)
- `--continue` (resume after halt)
- `--finalize` (post-iteration completion handling, wall-clock read per D4.1.5, commit, fix_plan freeze)

Estimated size: ~3,500–4,500 words. Still substantial — Ralph is intrinsically complex — but markedly smaller than the current monolith.

### `/build-status [<ticket>]` (the read-only skill)

Net-new tiny skill. Includes:

- If `<ticket>` omitted: list all active Ralph runs (one per cascade-active ticket per D2.1 v2's run-state lock).
- If `<ticket>` provided: show that ticket's current state — iteration N of M, cost-to-date, wall-elapsed, fix_plan unchecked count, latest claude.jsonl status, any halt cards emitted but not resolved.
- Pull data exclusively from `.cascade/manifests/<ticket>-build.json`, `.cascade/run-state.json`, and `<worktree>/.ralph/wall_clock_seconds.txt`. No writes.
- Format: structured text. Optional `--json` flag for machine consumption.

Estimated size: ~500–800 words. The skill is small because the work is small — read three files, render a status block.

### `/build-kill <ticket>` (the terminate skill)

Net-new small skill. Includes:

- Resolve the PGID from `<worktree>/.ralph/pgid` (per D4.1.9).
- Send SIGTERM to the process group, wait 2s, send SIGKILL.
- Invoke the orphan reaper (per D4.1.10).
- Update `.cascade/manifests/<ticket>-build.json` to record the kill (timestamp, who-killed, reason if provided).
- Update `.cascade/run-state.json` to release the parent-level lock.
- Move the ticket's Linear state if a kill should imply state transition (the v0.2 default: no automatic state move; the founder may want to `/build --continue` later. `/wrap` or explicit founder action moves state.).

Estimated size: ~700–1000 words.

### Shared rule: `.claude/rules/build-shared.md`

The handful of constants and invariants all three skills reference, plus cross-skill safety properties:

- Run-state lock semantics (per D2.1 v2)
- Worktree layout convention (`.claude/worktrees/<ticket>/`)
- Manifest paths and field names
- The "no two Ralphs on one parent" invariant
- Denylist cross-reference (per D4.1.7)
- Halt-card emission protocol (per D2.1 v2 + D3.4)

Estimated size: ~400–600 words. Each of the three skills `@`-imports this at its top.

## Token math (back-of-envelope)

Current state:
- `/build` SKILL.md: ~6,000 words ≈ ~8,000 tokens
- Re-injected on every `/build *` invocation
- Plus per-turn static preamble: ~3,000–5,000 tokens
- Read-only `--status` cost: ~11,000–13,000 tokens of fixed overhead

Post-split state:
- `/build-status` SKILL.md: ~700 words ≈ ~950 tokens
- `.claude/rules/build-shared.md` import: ~500 words ≈ ~700 tokens
- Per-turn static preamble unchanged
- Read-only `/build-status` cost: ~4,650–6,650 tokens of fixed overhead

Net savings on a single `/build-status` invocation: ~6,000–7,000 tokens. Multiplied across a long session with dozens of status polls, the savings compound.

`/build-kill` math is comparable. `/build <ticket>` (the spawn) is roughly unchanged or slightly larger after the shared rule is imported — the spawn skill keeps most of its content because Ralph genuinely is complex.

This is back-of-envelope, not measured. The implementation pass should measure actual per-invocation token cost before and after the split to confirm the math.

## Lazy-loading (v0.2.x, not v0.2)

The F-12 root-cause direction included a lazy-loading option: "Skill body is loaded only when its content is needed — the mode flag is inspected first, and only the relevant section is included."

Claude Code as of May 2026 (per D2.2's hook-surface research) does not natively support partial-skill-loading. There is no `@import-conditional-on` directive; SKILL.md files are loaded in their entirety when the command name resolves.

Two paths to actual lazy loading are visible:

- **(a)** Wait for Anthropic to ship partial-load primitives in Claude Code. Track the changelog; revisit when available.
- **(b)** Implement the split using sub-skills inside one canonical `/build` namespace (e.g. `.claude/skills/build/status/SKILL.md`, `.claude/skills/build/kill/SKILL.md`) and have `/build status <ticket>` and `/build kill <ticket>` resolve to those. This mirrors the three-skill split semantically but presents as one command verb to the founder.

v0.2 chooses (b)'s flatter form — three top-level skills, three top-level command names — because it's simpler to implement and to document. v0.2.x can rename to the nested form if Anthropic ships native nesting and the namespacing becomes valuable for organizational reasons. The semantics don't change.

## F-11 partial coverage

D4.2's contribution to F-11 (ceremony bloat) is the operator-facing-skill surface: the founder's `/build-status` poll no longer feels like a full ceremony invocation. That's part of F-11's resolution, not all of it. The full F-11 resolution is:

- **D3.4 (autonomy mode)** — single-command UX where the cascade self-orchestrates instead of requiring per-stage founder approval. This is the bulk of F-11.
- **D4.2 (this doc)** — the read-only skill split, so polling is cheap.
- **D4.4 (deferred)** — code-markers convention (`🤔`, `📝`) for skipping mid-build clarification cycles. Out of scope for D4.2.

## What v0.2 does not ship

1. **Lazy/partial skill loading.** Deferred per above; mechanically not available in Claude Code yet.
2. **A `/build --reconcile` separate skill.** Folded into D4.5. If implementation shows it's heavyweight enough to be a fourth split-out skill, raise in v0.2.x.
3. **A `/build --preflight` separate skill.** Pre-flight is a step inside `/build <ticket>` (per D4.1.2), not a standalone surface. The founder doesn't invoke pre-flight directly; the cascade invokes it.
4. **Per-turn context-budget telemetry.** F-12 direction item 5 ("`--status` reports the per-turn token cost"). Requires hooks into Claude Code's token-counting; deferred until D2.2's `cascade:run-state` schema includes a token-spend field, which is v0.2.x.

## Files this introduces

New files:

- `.claude/skills/build/SKILL.md` (the spawn skill — renamed/refactored from current `/build` SKILL.md, content reduced)
- `.claude/skills/build-status/SKILL.md` (new)
- `.claude/skills/build-kill/SKILL.md` (new)
- `.claude/rules/build-shared.md` (new — extracted shared content)

Updated files:

- `CLAUDE.md` template (mentions all three commands instead of one; `@`-imports the new shared rule)
- `docs/templates/halt-messages.md` (no new halt codes from D4.2; existing build halts still apply across all three)
- Any other skill that currently references `/build <ticket> --status` or `/build <ticket> --kill` — rewrite to `/build-status <ticket>` and `/build-kill <ticket>` (likely `/wrap`, `/verify`, `/retro`)

Deleted files:

- The current monolithic `.claude/skills/build/SKILL.md` (replaced by the split)

## Implementation order

1. Extract `build-shared.md` from the current `/build` SKILL.md (the shared content).
2. Author `/build-status` SKILL.md.
3. Author `/build-kill` SKILL.md.
4. Rewrite `/build` SKILL.md to the reduced spawn-only form.
5. Search-replace `/build *--status*` → `/build-status` and `/build *--kill*` → `/build-kill` across all other skill files.
6. Test all three on a synthetic ticket (from D0.1's CI fixture).

Estimated effort: one short Code session.

## Open items

- **Measure-before-shipping.** The token-savings math is back-of-envelope. Implementation pass should measure actual per-invocation context cost before vs after; if savings are <2k tokens per status invocation, the split is still worth doing for the readability and modularity benefit but the F-12 framing is overstated.
- **Command naming.** `/build-status` vs `/status build <ticket>` vs `/cascade-status build <ticket>`. v0.2 chooses `/build-status` (verb-prefixed) for symmetry with `/build` and `/build-kill`; revisit if the convention conflicts with anything in D3.4's command catalog.
- **`--continue` and `--finalize` retain dash-flag form.** They stay inside `/build <ticket>` as flags. Confirm in implementation that the spawn skill renders these correctly as a flag-handler section. Founders who use the cascade often will continue using `/build SOL-42 --continue` rather than learning a fourth top-level command.

## Cross-references

- **D2.1 v2** — run-state lock; the shared rule cites it as the cross-skill safety invariant.
- **D2.2** — session-management hook surface; `/build-status` is the read-only surface the cascade exposes for `solo-verify` and the founder.
- **D3.4** — autonomy mode is the larger F-11 resolution; D4.2 is the read-side complement.
- **D4.0** — `solo-verify build <ticket>` is the predicate-evaluation analog to `/build-status` (they both read the same manifests; `/build-status` formats for humans, `solo-verify` formats for the gate evaluator).
- **D4.1.7** — denylist enforcement spans all three skills via the shared rule.
- **D4.1.9** — `/build-kill` uses the process-group kill protocol authored in D4.1.

## Note on rollout

The three-skill split is a breaking change for any cascade state that references `/build SOL-N --status`. v0.1 saved skill references aren't in this scenario, but Linear comments and Bomber-era `[BOM-DOC-*]` documents may be — they're historical record per D0.1 §Bomber's disposition, no migration needed. New cascade work in v0.2 uses the new command names from day one.
