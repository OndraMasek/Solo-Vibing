# Solo-Setup

> An opinionated workflow stack for solo founders / vibe coders using Claude.ai (chat) + Claude Code (terminal) + Linear + GitHub.

**Status:** v0.1 in active development (target ship: end of May / early June 2026).

Solo-Setup packages a complete solo-founder workflow — heavyweight specs, four-hat adversarial review, cascade orchestration, and a Ralph-style automation loop — into a forkable template. The deliverable is the repo itself, not a service: a competent technical person should be able to fork it and adopt the whole pipeline in under an hour.

## What's in here

- [`CLAUDE.md`](./CLAUDE.md) — session instruction layer, loaded by Claude Code at the start of every session in the repo. **Not** shipped to forks; rendered from the `.template` version by /onboard.
- [`docs/templates/onboarding/chat-instructions.md.template`](./docs/templates/onboarding/chat-instructions.md.template) — sister artifact for chat-Claude on claude.ai. Rendered by /onboard step 8 alongside `chat-kickoff.md` so the founder can run /discovery in chat with full context.
- [`.claude/rules/`](./.claude/rules/) — six always-on rules: `naming`, `counter-allocation`, `scope-labels`, `completion-status`, `write-discipline`, `auditor-stance`.
- [`.claude/skills/`](./.claude/skills/) — the cascade skills: `onboard`, `discovery`, `constitution`, `specify`, `plan`, `review`, `update-linear`, `build`, `wrap`, `verify`, `retro`.
- [`.claude/commands/`](./.claude/commands/) — thin founder-fired commands: `start`, `status`, `next`, `config`, `map-codebase`, `audit-self`.
- [`.claude/agents/`](./.claude/agents/) — subagents invoked mid-skill: four-hat panel, `build-reviewer`, `decomposer`, `diagnoser`, `research-investigator`, `codebase-mapper`, `clarify-walker`.
- [`docs/constitution.md`](./docs/constitution.md) — Solo-Setup's own governing principles. **Not** shipped to forks; forks re-author via /constitution.
- [`docs/templates/`](./docs/templates/) — scaffolds used by skills (`spec.md.template`, `halt-messages.md`, Ralph `run.sh`, `AGENTS.md`, `CLAUDE.md`, `PROMPT.md`, plus `discovery/` prereq templates and `onboarding/` chat handoff templates).
- [`scripts/`](./scripts/) — onboard helpers: `check_prereqs.sh` and `verify_linear_key.sh`.
- [`docs/specs/0001-wrap-build-log/`](./docs/specs/0001-wrap-build-log/) — Solo-Setup's own worked-example sealed spec. **Not** shipped to forks.
- [`docs/decisions/`](./docs/decisions/) — append-only ADR log.
- [`docs/.solo-config.json`](./docs/.solo-config.json) — workflow knobs (marker, cascade mode, model profile, Ralph caps, `workflow.discovery_surface`). **Not** shipped to forks; rendered from the `.template` version by /onboard.

## The cascade

```
/onboard ──┐
           ├─→ /discovery (in chat)  ──→ /constitution (seeded in chat)
           │
/specify ──→ /plan → /review → /update-linear
                                      ↓
                       /build (per child) → /wrap → /verify → /retro
```

`/onboard` runs once in Claude Code, then hands off to chat-Claude (claude.ai project) for /discovery + /constitution-seed. /specify and everything downstream runs in Claude Code. The cascade is described in detail in [`CLAUDE.md` §Where work happens](./CLAUDE.md).

## Using this template

### Quick start (recommended)

In a fresh terminal, create an empty directory and run the bootstrap one-liner:

```bash
mkdir my-project && cd my-project
curl -fsSL https://raw.githubusercontent.com/OndraMasek/Solo-Vibing/main/bootstrap.sh | bash
```

> Note: the GitHub-side repo is currently hosted at `OndraMasek/Solo-Vibing`; the canonical name of the workflow stack is "Solo-Setup". The two will be reconciled in a future GitHub rename.

The script (see [`bootstrap.sh`](./bootstrap.sh)) downloads the latest template into the current directory, initializes a fresh git repo on `main`, and offers to create the GitHub remote via `gh repo create` to avoid parallel-history conflicts on first push. From there:

```bash
claude         # launch Claude Code in this folder
```

And as the first command inside Claude Code:

```
/onboard
```

`/onboard` walks you through three substantive interactions:

1. **Marker pick** — your repo-scoped project identifier (`MYA`, `PRJ`, etc.).
2. **Linear API key paste** — into `.env`, never into chat.
3. **First north-star question** — seeds /discovery.

Everything else is yes/no confirmation: connectors, GitHub remote, upstream-content audit, Linear team selection. At the end, /onboard renders `docs/onboarding/chat-kickoff.md` and `docs/onboarding/chat-instructions.md` — open your Claude.ai project, attach the instructions, paste the kickoff message, and /discovery runs there.

### Alternative: GitHub "Use this template" (not recommended)

GitHub's **Use this template → Create a new repository** button bypasses `bootstrap.sh`, which means your fork inherits the upstream's own canonical artifacts as if they were yours:

- `CLAUDE.md` (carries Solo-Setup's marker and project identity)
- `docs/.solo-config.json` (Solo-Setup's config)
- `docs/constitution.md` (Solo-Setup's governing principles)
- `docs/product/north-star.md` (Solo-Setup's north-star)
- `docs/specs/0001-wrap-build-log/` (Solo-Setup's in-flight spec)

Downstream skills (`/specify`, `/review`, `/verify`) will read these as the fork's own state and produce incoherent output. If you used this path anyway, recover by running:

```bash
bash bootstrap.sh --refresh-templates   # re-overlay clean templates
# then delete the inherited upstream identity:
rm -f CLAUDE.md docs/.solo-config.json docs/constitution.md docs/product/north-star.md
rm -rf docs/specs/0001-wrap-build-log
git add -A && git commit -m "chore: clear upstream identity"
```

Then run `claude` and `/onboard` — step 1.5 will catch anything left.

The `curl … | bash` path above is the canonical entry; everything is wired around it.

## Prereqs

- Claude.ai Pro (or higher) project with Linear + GitHub connectors at the project level.
- Claude Code installed in your terminal.
- `gh` CLI installed and authed (recommended; bootstrap uses it to create the GitHub remote without auto-init conflicts).
- Linear free tier is sufficient; GitHub free repos are sufficient. The stack assumes a free-tier-first floor; no paid-tool dependency is introduced without a free-tier path.

## License

Apache-2.0. See [LICENSE](./LICENSE).
