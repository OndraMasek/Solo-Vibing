# CLAUDE.md

> Project instructions for Claude Code. Auto-loaded at the start of every session in this repo.
>
> This file is the **session instruction layer** — it imports the always-on rules, states project context, and records tool constraints. It is **not** the law. Governing principles — Core principles, Process rules, Architectural constraints, Decision-making triggers — live in `docs/constitution.md`, authored and amended by `/constitution`. CLAUDE.md points at the constitution; it does not duplicate it.

## Rules (always-loaded)

The six always-on conventions are imported below. Claude Code also auto-loads every `.md` file in `.claude/rules/` at session start; the explicit `@`-imports here make the dependency visible and reviewable in one place.

@.claude/rules/naming.md
@.claude/rules/counter-allocation.md
@.claude/rules/scope-labels.md
@.claude/rules/completion-status.md
@.claude/rules/write-discipline.md
@.claude/rules/auditor-stance.md

## Project

- **Marker:** `SOL` — the canonical value is read from `docs/.solo-config.json` (`marker` key) by every skill that mints an artifact. The value here is a convenience copy for human readers; `docs/.solo-config.json` wins on conflict. See `.claude/commands/config.md`.
- **What this repo is:** the Solo-Setup — a public reference repository that packages a complete solo-founder workflow stack (Claude.ai project + Claude Code + Linear + GitHub + Skills + a Ralph-style automation loop + spec discipline + four-hat adversarial review) so a competent technical person can fork it and adopt the whole pipeline in under an hour. The deliverable is the repo itself, not a service.
- **Stack / language:** language-agnostic. The repo is documentation, templates, and `.claude/` configuration — not an application. Concrete examples in the docs may pick a single language, but the stack imposes none.

## Prereqs

- **Claude.ai project connectors required:** Linear (workspace-scoped) and GitHub (repo read access for this repository). Both must be connected at the Claude.ai project level before /onboard runs. The repo-level declaration lives in `.mcp.json`; /onboard step 2 verifies the connection.
- **Linear personal API key in `.env`** (set during /onboard step 3, reserved for v0.2 scripts).

## Workflow — the Solo-Setup cascade

Skill chain (each stage Task-invokes the next per its own Chains section; v0.2 wires hook-fired gates — see §v0.2 cascade primitives):

`/onboard` → `/discovery` → `/constitution` → `/specify` → `/plan` → `/review` → `/update-linear` → `/build` (per child ticket) → `/wrap` → `/verify` → `/retro`

Founder-fired commands (thin, deterministic): `/start`, `/status`, `/next`, `/config`, `/map-codebase`, `/audit-self`.

- **Cascade behavior** (`cascade-only` / `interactive` / `yolo`) and every workflow knob live in `docs/.solo-config.json` — see `.claude/commands/config.md`.
- **`/build` is the one stage that does not auto-fire** — Ralph runs cost real money and produce real commits, so the go signal stays explicit. It also splits into a spawn turn and a `--finalize` turn.
- **Halt-card rendering** is centralized in `docs/templates/halt-messages.md`. Skills compose against its named patterns; they do not inline halt-card structure.
- **The constitution at `docs/constitution.md`** governs specs and code. `/review` (check j) and `/verify` check against it. It does not exist for this repo yet — author it via `/constitution` before the first `/specify`.

## v0.2 cascade primitives

v0.2 adds hook-fired gates and a verification CLI on top of the v0.1 skill chain. The pieces below are wired and self-applied in this repo.

### Cascade gates

Named halt-gates fire at each stage's at-write boundary. Gate definitions and halt-card copy live in `docs/templates/halt-messages.md`; the full gate inventory is enumerable at any time with `python3 tools/solo-verify --list-gates`. Skills compose against named gates; they never inline gate logic.

### Strategy enum

`/specify` step 1 proposes a decomposition strategy (founder-confirmed at step 5) from the five-value enum per D3.1: `walking-skeleton`, `api-boundary`, `capability-cluster`, `refactor-spike`, and `hybrid`. The strategy populates the test-pyramid shape, the perceptual-evidence requirement, and the per-stage gate composition.

### Hooks

Hook wiring lives in `.claude/settings.json`. Eight scripts back the cascade events: `preflight-provenance.sh`, `pyramid-tampering.sh`, `four-hat-objection-coverage.py`, `stop-orchestrator.sh`, `session-start-state-restore.sh`, `session-end-telemetry.sh`, `precompact-safe-boundary.sh`, and `pretool-write-denylist.sh`. Shared helpers live in `.claude/hooks/lib/`.

### Tainted state

A manifest may be marked `is_tainted: true` with a `taint_reason` (per 0001 AC-18) when its provenance breaks. Downstream work written against a tainted manifest is suspect until reconciled. Cascade run-state is persisted at the canonical path `.cascade/run-state.json`; clearing taint is a `--reconcile-only` pass over the responsible stage.

### Code markers

In-code attention markers are defined in `.claude/rules/code-markers.md`: `🤔` (clarify question — proceeded on a best-guess assumption), `📝` (copy pending), and `☣️` (tainted code region). `/retro` scans the worktree for these and reports counts.

### CI

Continuous integration runs via GitHub Actions at `.github/workflows/ci.yml` (per 0001 AC-20).

## Session discipline

- **Token budget:** target 100–200k effective tokens per Claude Code session. Estimate before committing; split sessions that will not fit.
- **TDD is the default build cadence** — `/build` opens against the failing-test seed, not code.
- **One ticket per `/build` run** in v0.1. One highest-priority unchecked item per Ralph iteration.
- **Short, focused sessions** that end with a concrete artifact. No "explore the space" sessions without a written output. Founder time on this repo is limited and split with other work — sessions are sized accordingly.
- **Self-application is the test.** This repo is built with the workflow it documents. If the stack cannot be used to build the stack, the stack is broken — treat that as a finding, not an inconvenience.

## Tool constraints

- This repo is documentation + templates, not an application — there is no test suite to run and no autonomous `/build` sandbox to configure for the repo itself. The Ralph loop, `AGENTS.md` autodetect, and `docs/onboarding/sandbox.md` concerns apply to repos that *adopt* the stack, not to this one.
- Free-tier-first: the stack assumes Linear free tier, GitHub free repos, and Claude.ai Pro at minimum. Do not introduce a paid-tool dependency without a free-tier path.
- Source-of-truth convention: the canonical content for every repo file lives in Linear documents (test-docs-generator workspace, Decisions project). This repo is **generated from Linear** by Claude Code. Edit the Linear doc, not the local file.

## Notes

- This file is the session instruction layer. **Governing principles do not go here** — they belong in `docs/constitution.md` via `/constitution`, so `/review` and `/verify` can check work against a stable, versioned document.
- `docs/constitution.md` has not been authored for this repo yet. It is on the near-term path (the project's six-improvement scope includes the four-hat review process, which the constitution anchors).
- `/onboard` never overwrites an existing `CLAUDE.md` without explicit founder confirmation.
