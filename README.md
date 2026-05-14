# Solo-Setup

> An opinionated workflow stack for solo founders / vibe coders using Claude.ai (chat) + Claude Code (terminal) + Linear + GitHub.

**Status:** v0.1 in active development (target ship: end of May / early June 2026).

Solo-Setup packages a complete solo-founder workflow — heavyweight specs, four-hat adversarial review, cascade orchestration, and a Ralph-style automation loop — into a forkable template. The deliverable is the repo itself, not a service: a competent technical person should be able to fork it and adopt the whole pipeline in under an hour.

## What's in here

- [`CLAUDE.md`](./CLAUDE.md) — session instruction layer, loaded by Claude Code at the start of every session.
- [`.claude/rules/`](./.claude/rules/) — six always-on rules: `naming`, `counter-allocation`, `scope-labels`, `completion-status`, `write-discipline`, `auditor-stance`.
- [`.claude/skills/`](./.claude/skills/) — the cascade skills: `onboard`, `discovery`, `constitution`, `specify`, `plan`, `review`, `update-linear`, `build`, `wrap`, `verify`, `retro`.
- [`.claude/commands/`](./.claude/commands/) — thin founder-fired commands: `start`, `status`, `next`, `config`, `map-codebase`, `audit-self`.
- [`.claude/agents/`](./.claude/agents/) — subagents invoked mid-skill: four-hat panel, `build-reviewer`, `decomposer`, `diagnoser`, `research-investigator`, `codebase-mapper`, `clarify-walker`.
- [`docs/constitution.md`](./docs/constitution.md) — the project's governing principles, checked against by `/review` and `/verify`.
- [`docs/templates/`](./docs/templates/) — scaffolds used by skills (`spec.md.template`, `halt-messages.md`, Ralph `run.sh`, `AGENTS.md`, `CLAUDE.md`, `PROMPT.md`).
- [`docs/specs/0001-wrap-build-log/`](./docs/specs/0001-wrap-build-log/) — a worked-example sealed spec.
- [`docs/decisions/`](./docs/decisions/) — append-only ADR log.
- [`docs/.solo-config.json`](./docs/.solo-config.json) — workflow knobs (marker, cascade mode, model profile, Ralph caps). Per-fork; edit after `/onboard`.

## The cascade

```
/onboard → /discovery → /constitution → /specify → /plan → /review → /update-linear
                                                                       ↓
                                              /build (per child) → /wrap → /verify → /retro
```

Each stage Task-invokes the next per its own Chains section; the founder fires `/onboard` once, then `/build <MARKER>-N-K` per child ticket. Everything else cascades.

## Using this template

1. Click **Use this template → Create a new repository** on GitHub.
2. Clone your new repo locally.
3. Set up prereqs:
   - Connect **Linear** (workspace-scoped) and **GitHub** (repo read) connectors in your Claude.ai project.
   - Put your Linear personal API key in `.env` (reserved for v0.2 scripts).
4. Run `/onboard` in Claude Code from the repo root. It will: detect brownfield vs greenfield, verify connectors, set your project marker, scaffold `CLAUDE.md`, and seed the first north-star question.
5. From there the cascade takes over.

## Prereqs

- Claude.ai Pro (or higher) project with Linear + GitHub connectors.
- Claude Code installed in your terminal.
- Linear free tier is sufficient; GitHub free repos are sufficient. The stack assumes a free-tier-first floor; no paid-tool dependency is introduced without a free-tier path.

## License

Apache-2.0. See [LICENSE](./LICENSE).
