# North-star: Solo-Setup

> The canonical statement of what this project is. Read as context by `/specify`, `/constitution`, `/plan`, `/review`.
> Source: shortcut promotion from `docs/discovery/idea-brief-v1.md` after /discovery Phase 1 — Phase 2 research skipped (idea is already articulated in CLAUDE.md and 7+ prior Linear meta-project docs; framework fit is poor for a meta-project / known-idea case).
> Verdict: **build** (advisory, Phase 1) — promoted to canonical via founder shortcut.
> Sealed: 2026-05-14.

## What this is

A fork-and-adopt **reference repository** that bundles a complete solo-founder AI workflow stack: Claude.ai project conventions + Claude Code skills/commands + Linear MCP integration + GitHub conventions + a Ralph automation loop + spec-discipline templates + four-hat review agents. A competent technical person can fork it and adopt the entire pipeline in under an hour. The deliverable is the repo, not a service.

Tagline candidate: **"The workflow stack for solo founders who ship with Claude Code. Fork it. Run it. Stop drifting."**

## Who it's for

**Primary segment:** Solo technical founders building AI-assisted software at ~10–20 hr/week. Comfortable with CLI tooling, git, and Claude Code. Have used "vibes-based" agent coding (Cursor, Claude Code, Aider) and gotten burned by scope drift, lost context across sessions, and missing acceptance criteria.

**Secondary segment:** Small startup engineering teams (2–5 people) adopting agentic coding workflows who need shared discipline that survives across team members and sessions.

## The problem

AI coding agents (Claude Code, Cursor, etc.) work great for an hour and drift after that. No spec → no acceptance criteria → no objective "done." Reviews are vibes-based. AI-generated code accumulates without architectural coherence. The promised AI speedup is partly recouped as rework, scope creep, and lost context across sessions. Current alternatives — ad-hoc prompts, README TODOs, willpower-driven discipline — erode under time pressure.

## The mechanism

Impose spec discipline + cascade orchestration **before any code is written**. Every feature gets a sealed parent spec with explicit AC + a failing-test seed. The cascade engine auto-decomposes into child tickets, each scope-labeled and dependency-wired. A Ralph-style automation loop runs the build against the failing tests as backpressure — code can't "complete" until the tests it was specced against pass. Four-hat adversarial review (engineer / pm / skeptic / user) catches scope drift, feasibility risks, unstated assumptions, and silent failure modes before code lands. Discipline is enforced by skills/commands (machine-checked rules in `.claude/rules/`), not founder willpower.

## Why now

- Claude Code matured through 2025 — skills, plugins, MCP servers, the Agent SDK landed.
- Linear shipped a first-class MCP server.
- The Ralph-loop pattern was published and validated.
- Anthropic released Opus 4.6 / 4.7 with 1M-context windows.
- AI coding agents crossed the "competent solo collaborator" reliability threshold — but they produce drift faster than humans alone.

The need for disciplined orchestration is acute exactly when agent autonomy is highest. The window is open today.

## Founder fit

Founder is dogfooding the workflow — this repo is built using its own discipline (self-application principle in CLAUDE.md). Has the technical depth to author skills, commands, agents, and spec templates. Lived experience of the exact failure modes the workflow addresses. Public-repo + limited-founder-time posture matches the target segment one-for-one.

## Risks

- **R1 — Adoption friction.** Steep concepts (cascade, scope labels, four-hat, write-discipline rules). Solo founders may bounce off vs. ad-hoc Claude Code where the on-ramp is "type a prompt."
- **R2 — Tooling churn.** Claude Code, Linear MCP, Anthropic SDK evolve fast. Reference templates rot; maintenance burden on the founder.
- **R3 — "Who needs another workflow."** Solopreneur space is saturated with opinionated takes. Differentiation isn't obvious without seeing the workflow run end-to-end.
- **R4 — Self-application paradox.** If the stack can't build itself, it's broken. Risk of the founder bypassing their own rules under time pressure — would invalidate the reference value.

## Mitigations

- R1: ship onboarding (`/onboard`) that's interactive and forgiving; visible cascade summary cards reduce cognitive load.
- R2: pin to specific tool versions in `docs/.solo-config.json`; structure rules so updates are local edits, not architectural rewrites.
- R3: build the workflow's first public demo on this repo itself — every spec, every build-log is a working example.
- R4: every halt-card is a forcing function; the cascade refuses to proceed on shortcut moves. The founder gets stopped before bypass becomes a habit.

## Distribution posture

Free-tier-first (Linear free tier, GitHub free repos, Claude.ai Pro minimum). No paid-tool dependencies without a free-tier path. Distribution channel: word-of-mouth in solo-founder communities (HN, Indie Hackers, AI-dev twitter, dev.to). Adoption telemetry deferred — gather feedback via GitHub issues + community engagement.

## Explicit non-goals

- **Not a SaaS.** No hosted service, no accounts, no billing.
- **Not a coding assistant replacement.** Sits on top of Claude Code; doesn't compete with it.
- **Not multi-tenant team workflows in v0.1.** Solo founder is the canonical user; team patterns are v0.2+.
- **Not framework-prescriptive.** Language-agnostic; the workflow imposes discipline, not stack choice.
- **Not autonomous shipping.** `/build` requires explicit founder go-ahead — Ralph runs cost real money and produce real commits.

## Status

Sealed 2026-05-14 via shortcut from `docs/discovery/idea-brief-v1.md` (Phase 1). Phase 2 research deliberately skipped — framework fit is poor for an already-articulated meta-project. Recorded as a /discovery framework finding: needs a "known-idea / meta-project" path that bypasses Phase 2 + 3 when the idea is already documented.
