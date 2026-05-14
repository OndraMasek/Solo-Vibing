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

### Quick start (recommended)

In a fresh terminal, create an empty directory and run the bootstrap one-liner:

```bash
mkdir my-project && cd my-project
curl -fsSL https://raw.githubusercontent.com/OndraMasek/Solo-Vibing/main/bootstrap.sh | bash
```

The script (see [`bootstrap.sh`](./bootstrap.sh)) downloads the latest template into the current directory and initializes a fresh git repo on `main`. From there:

```bash
claude         # launch Claude Code in this folder
```

And as the first command inside Claude Code:

```
/onboard
```

`/onboard` walks you through: picking your project marker, verifying Linear + GitHub connectors in your Claude.ai project, creating `.env` for your Linear API key, and seeding the first north-star question. After that the cascade takes over.

Pushing to GitHub is optional and can wait — once you want a remote, run `gh repo create --source=. --push --private` (or use the GitHub web UI).

### Alternative: GitHub "Use this template"

If you'd rather start from GitHub's UI:

1. Click **Use this template → Create a new repository** at the top of [this repo](https://github.com/OndraMasek/Solo-Vibing).
2. `git clone` your new repo locally.
3. Run `claude` in the repo root, then `/onboard`.

## Prereqs

- Claude.ai Pro (or higher) project with Linear + GitHub connectors.
- Claude Code installed in your terminal.
- Linear free tier is sufficient; GitHub free repos are sufficient. The stack assumes a free-tier-first floor; no paid-tool dependency is introduced without a free-tier path.

## License

Apache-2.0. See [LICENSE](./LICENSE).
