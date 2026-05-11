# CLAUDE.md — Solo-Setup

**Last updated:** 2026-05-11

## Project identity

- **Name (working):** Solo-Setup (final v1.0 name deferred per SOL-1)
- **GitHub:** OndraMasek/Solo-Setup
- **License:** Apache-2.0 (per SOL-2)
- **Phase:** v0.1 in active development (target: end of W4, week of 2026-06-01)

## Linear context

- **Workspace:** test-docs-generator
- **Team:** Solo Claude Stack (prefix `SOL`)
- **Linear projects:**
  - `Decisions` — Q-NNN decision register (https://linear.app/test-docs-generator/project/decisions-6f8f08e0728f)
  - `Backlog` — active work items (https://linear.app/test-docs-generator/project/backlog-1eb252b957b8)
  - `Sync Queue` — chat→code propagation (https://linear.app/test-docs-generator/project/sync-queue-ac6b97e59a69)
- **Branch pattern:** `SOL-<id>-<slug>` (e.g. `SOL-18-some-task`)
- **Note on this bootstrap commit:** the `main` branch direct-commit is acceptable ONLY for SOL-17 (this ticket). Every subsequent change goes via feature branch + PR.

## Source-of-truth rules

- Code, tests, scripts, `docs/`, `.claude/skills/`, `templates/` → **git is canonical**
- Linear issues → Linear is canonical; never duplicate issue bodies into git
- Linear Documents (if any) → temporary migration vehicles only; archive after mirror to git
- ADRs in `docs/decisions/` → git is canonical; resolved Linear decision issues (`Q-NNN`/`SOL-N`) are back-references

## Sync Queue protocol

### At session start
1. Read this file (`CLAUDE.md`)
2. List Linear issues in `Sync Queue` project with label `sync:pending`
3. For each pending ticket, read body, snapshot the body content (for pre-PR re-read check)
4. Process in priority order

### Pre-PR re-read (the Astro `scope:sealed` rule)
Before `gh pr create`:
- Re-fetch the ticket body via Linear MCP
- Compare to the session-start snapshot
- `scope:sealed` ticket changed → halt and comment on the ticket asking for confirmation
- `scope:living` ticket changed additively → continue silently; subtractively → halt

### After PR merge (or after direct-to-main commit for SOL-17 bootstrap)
1. Comment on the Linear ticket with the commit SHA + PR URL (or commit SHA only if direct-to-main)
2. Flip label `sync:pending` → `sync:synced`
3. Move ticket status to Done

## ADR conventions (per design doc 03 / SDG D-019)

- **Strategic decisions** (business model, scope, regulatory, GTM, customer commitments): Linear Decisions issue first → mirror to `docs/decisions/NNNN-*.md` via Sync Queue ticket
- **Build-time decisions** (library choice, encoding, file format, internal API): `docs/decisions/NNNN-*.md` only, with one-line back-reference in the parent build issue's session-end comment
- **ID space:** continuous `D-NNN` across both classes. Linear back-references use `SOL-N` issue IDs where applicable.
- **Never delete or rewrite resolved ADRs.** Amendments add a footer line; supersessions create a new ADR with the old one's Status changed to "Superseded by D-NNN".

## Locked decisions (do not re-litigate without raising a new Decision issue)

- **D-0001 (SOL-9):** Meta-project Linear hosted in SOL team within test-docs-generator workspace
- **D-0002 (SOL-2):** License is Apache-2.0
- **D-0003 (SOL-1):** Working name is `Solo-Setup`; final v1.0 name deferred
- (More to follow as additional Q-NNN issues resolve)

## Build conventions

- Commit messages: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`)
- Direct commits to `main` are PROHIBITED except for SOL-17 bootstrap. After SOL-17, all changes via PR.
- One PR per Sync Queue ticket. Code-Claude stops at `gh pr create` and waits for human merge.
- `make check` (or equivalent) against the final commit before declaring complete (to be added when project has a build target)

## What you're not doing

- Continuing SDG product work (different repo, different domain)
- Domain-specific implementation (Czech invoices, named EU prospects, etc.)
- Building a CLI tool to install the stack (docs + templates + skills only in v0.1)
- Recording demo videos or building a marketing landing page
- Adding a second methodology (BMAD, agent-OS, etc.) until v0.1 is published

## Hard constraints

- **License:** Apache-2.0. All SKILL.md files include `SPDX-License-Identifier: Apache-2.0` in their frontmatter or top comment.
- **Knowledge cutoff:** January 2026. Current date during v0.1 development: May 2026. **Verify versions of external dependencies (Ralph plugin, spec-kit, Skills standard) via web search before citing.**

## Operational hooks (in `.claude/hooks/`)

- `session_start.sh` — runs at session start; reports branch, scans Sync Queue for `sync:pending`, reminds of read order
- `pre_edit_branch_check.sh` — runs before `Edit`/`Write`/`MultiEdit`; blocks edits on `main`/`master` with exit 2; warns if branch doesn't match `SOL-<id>-<slug>`

Hook configuration in `.claude/settings.json`.

## Design history (pre-v0.1)

The `docs/design/` directory contains 12 design notes developed in the Claude.ai meta-project before v0.1 drafting began (files numbered 00–10 plus the Astro consulting-site playbook). These are historical artifacts; the user-facing v0.1 docs in `docs/00_*.md` through `docs/13_*.md` will be drafted FROM these design notes in weeks 2–4. The design files reference the working name `solo-claude-stack` in many places — this was renamed to `Solo-Setup` per SOL-1 on 2026-05-11; references in the design files are intentionally left alone as historical record.

## References

- Linear workspace: https://linear.app/test-docs-generator
- SOL team: https://linear.app/test-docs-generator/team/SOL
- Decisions register: https://linear.app/test-docs-generator/project/decisions-6f8f08e0728f
- Repo: https://github.com/OndraMasek/Solo-Setup
