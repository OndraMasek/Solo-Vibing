# 03 — Design Principles and Improvements

> **Pre-v0.1 design history.** Migrated from the Claude.ai meta-project KB on 2026-05-11. References to the old working name `solo-claude-stack` are intentionally preserved as historical record; the current working name is `Solo-Setup` (SOL-1). User-facing v0.1 docs will live in `docs/` (numbered 00–13) and will be drafted *from* these design notes during weeks 2–4.

**File purpose:** Numbered design decisions (DD-N) for this meta-project. The equivalent of SDG's ADRs but for the public stack itself.
**Last updated:** 2026-05-11

---

## Conventions

- Each design decision has a number (DD-001, DD-002, …), status, date, and a one-paragraph rationale.
- Status values: `Active`, `Superseded by DD-N`, `Open`.
- When a DD changes, append a new DD that supersedes the old one. Do not rewrite history.

---

## DD-001 — Public deliverable is a single GitHub repository, not a CLI or service

**Status:** Active
**Date:** 2026-05-11

**Decision:** v0.1 ships as a single GitHub repository containing docs, templates, and skill files. No CLI installer, no hosted service, no template-generator app.

**Rationale:** Lowest possible ship cost. A repo can be forked, starred, or referenced in a tweet. A CLI requires installation paths, version management, testing on multiple OSes, distribution channels. v0.2+ can layer a CLI on top once the docs+templates have validated demand.

---

## DD-002 — Compose external primitives, do not reinvent

**Status:** Active
**Date:** 2026-05-11

**Decision:** The stack composes three external primitives that already exist and are actively maintained:
1. **Ralph Wiggum** (Anthropic plugin `claude-code/plugins/ralph-wiggum`, originally Geoffrey Huntley's pattern at `ghuntley.com/ralph/`)
2. **GitHub spec-kit** (`github/spec-kit`, v0.8.6 as of May 2026)
3. **Claude Code Skills** (Anthropic standard, documented at `code.claude.com/docs/en/skills`)

We do not write our own loop runner, our own spec language, or our own skills format.

**Rationale:** Maintenance cost is the dominant risk for a public solo-founder project. Wrapping existing primitives means our maintenance burden is mostly documentation drift, not code drift. Each primitive has a community larger than ours will ever be; betting on them is correct.

**Consequences:** The stack is opinionated about which primitives to use. We do not provide a "pick your own loop runner" abstraction. People who want BMAD or agent-OS or another stack are welcome to fork.

---

## DD-003 — Two-Claude architecture is mandatory in the recommended stack

**Status:** Active
**Date:** 2026-05-11

**Decision:** The stack recommends Claude.ai (web/desktop/mobile) for chat-Claude and Claude Code (terminal) for code-Claude. Both are required.

**Rationale:** Removing chat-Claude breaks the strategy/spec-drafting workflow and forces the founder to think in terminal. Removing code-Claude breaks the build workflow. The two-Claude split is the architectural choice that makes everything else possible.

**Consequences:** Stack assumes Claude Pro or higher subscription (chat) plus Claude Code (terminal). We do not provide a Cursor-only path. Documented as a hard prerequisite in the README.

---

## DD-004 — Linear recommended, alternatives documented

**Status:** Active
**Date:** 2026-05-11

**Decision:** Linear (free tier) is the recommended context store. The stack provides a full Linear workspace blueprint. Alternatives (Notion, Obsidian + git, GitHub Projects, plain markdown) are listed in a single alternatives table with the trade-offs documented.

**Rationale:** Linear's combination of: mobile capture, OAuth-DCR-based MCP (works in both Claude.ai and Claude Code), documents as first-class citizens, free tier with 250-issue capacity is uniquely the right shape for solo founders. We do not claim it is the only shape; we claim it is the best for the primary use case.

**Consequences:** Founders on a different stack pay a translation cost (one-page table tells them what to substitute). Acceptable.

---

## DD-005 — Linear workspace structure is modular, bootstrap by project type

**Status:** Active
**Date:** 2026-05-11

**Decision:** The recommended Linear workspace has core projects and optional projects.
- **Core (always present):** Strategy, Spec, Sync Queue, Build Log
- **Optional, GTM-heavy projects:** GTM, Customers, Outreach Log
- **Optional, research-heavy projects:** Research (analogue to SDG's Project KB R1 files)

The `project-bootstrap` skill proposes the right module set from the project's one-paragraph description.

**Rationale:** SDG had GTM and Customers because it was a commercial project. A pure OSS project would not. The stack should not force unused projects on the founder.

**Consequences:** The Linear blueprint in the public stack documents both core and optional, with clear "when to enable" triggers per optional project.

---

## DD-006 — Skill-driven bootstrap

**Status:** Active
**Date:** 2026-05-11

**Decision:** New-project bootstrap is driven by a skill (`project-bootstrap`) rather than a CLI tool. The founder types `/project-bootstrap <one-line description>` in Claude Code and the skill produces:
- Recommended Linear workspace structure (which optional projects to enable)
- Recommended GitHub repo skeleton
- Initial `CLAUDE.md` content
- Initial set of project-specific labels
- A bootstrap checklist for the founder

**Rationale:** Skills are the right abstraction. They are version-controlled inside the public repo, they run natively in Claude Code, and they do not require a separate runtime. A CLI for the same purpose would need a Python/Node runtime, install path, etc.

**Consequences:** The skill ships as part of the public repo under `.claude/skills/project-bootstrap/SKILL.md`. Founders fork the repo, then run the skill in their local copy.

---

## DD-007 — TDD is the default build cadence, enforced via session prompt

**Status:** Active
**Date:** 2026-05-11

**Decision:** The default Claude Code session prompt template enforces:
1. Read the spec
2. Write failing tests for the next acceptance criterion (or the next user story from spec-kit `tasks.md`)
3. Verify tests fail for the right reason
4. Write the minimum code to make tests pass
5. Run `make check` (or equivalent)
6. Commit on green
7. Repeat until session boundary or feature complete

**Rationale:** SDG validated commit-on-green and three-strikes-stop. Layering TDD on top is the natural next discipline. Spec-kit's `/speckit.tasks` already produces test-ordered task lists when TDD is requested, so the pipeline naturally produces test-first work.

**Consequences:** Session prompt template references TDD explicitly. Founders who do not want TDD remove that line. Default is TDD.

---

## DD-008 — Token budget per session: target 100k, hard ceiling 200k

**Status:** Active
**Date:** 2026-05-11

**Decision:** Every Claude Code build session targets <100k effective tokens, with 200k as the hard ceiling. The session prompt template includes a token-budget pre-flight section: estimated files touched × estimated tokens per file, plus fixed overhead (CLAUDE.md, MCP schemas, etc.).

If a session would exceed 100k, it gets split into a multi-session plan with explicit handoff artifacts.

The session opener includes `/cost` invocation; at 60–70% utilization the session compacts or hands off.

**Rationale:** Claude Code 200k context window. The "Lost in the Middle" effect degrades recall after ~60% utilization. SDG observed this empirically (SDG-37 carries the context discipline rules). Putting numbers on it gives the founder a concrete budget to respect.

**Consequences:** Long features must be split. Handoff artifacts (session prompt for next session, status comment summarizing what landed) are mandatory. Token budgets are estimates, not guarantees — the budget protocol is a forcing function, not a contract.

---

## DD-009 — Spec-kit chain as the structural backbone, four-hat review wedged between spec and plan

**Status:** Active
**Date:** 2026-05-11

**Decision:** The default workflow for new features is:
1. **Goal-setting** (one-page template, founder + chat-Claude)
2. **Discovery** (one-page template, founder + chat-Claude)
3. **/speckit.constitution** (project-wide non-negotiables, done once per project)
4. **/speckit.specify** (feature spec)
5. **/speckit.clarify** (resolves ambiguities)
6. **Four-hat adversarial review** (Linear Document, the wedge point — this is the chat-Claude human-in-the-loop checkpoint)
7. **/speckit.plan** (technical plan, only after the spec is review-cleared)
8. **/speckit.tasks** (task breakdown, TDD-ordered)
9. **/speckit.analyze** (cross-artifact consistency check)
10. **/speckit.implement** (Claude Code executes; this is where Ralph Wiggum can wrap autonomous iteration if appropriate)
11. **TDD session loop** (per DD-007)
12. **Code review** (single Claude pre-PR; optional dual-model at PR)
13. **Merge → Build Log entry → Sync Queue updates**

**Rationale:** Spec-kit provides 80% of the structure. Discovery + goal-setting + four-hat review are the additions that make it work for solo founders. The placement of the four-hat review is critical: after `/specify` is detailed enough to attack, before `/plan` locks technical choices.

**Consequences:** The public stack documents this 13-step flow as the recommended path. Shortcuts are documented for trivial features (bug fixes, doc edits, one-file changes — skip to step 10 or 11). For non-trivial features, the full chain is the default.

---

## DD-010 — Ralph Wiggum only for bounded, deterministic-success tasks

**Status:** Active
**Date:** 2026-05-11

**Decision:** Ralph Wiggum loops are documented as the right tool for:
- Bulk refactoring with clear completion criteria
- Test coverage gap filling
- Documentation generation from code
- Failing-test-to-green loops on well-defined units

Ralph is documented as the wrong tool for:
- Strategy work
- Spec drafting
- Customer-facing artifacts
- Anything judgment-heavy
- Anything where the success criterion is "subjectively good"

**Rationale:** Ralph's "deterministically bad in an undeterministic world" property is a feature for bounded tasks and a bug for judgment-heavy ones. Geoffrey Huntley's own writing emphasizes the boundedness requirement.

**Consequences:** The automation loop design doc gives a concrete decision table: "is this task ralph-shaped?" with examples.

---

## DD-011 — Four-hat adversarial review is non-negotiable for the stack's public docs

**Status:** Active
**Date:** 2026-05-11

**Decision:** Every public doc in the deliverable repo gets a four-hat review before v0.1 ships. Review is performed in this Claude.ai meta-project. Findings are reconciled before the doc is finalized.

**Rationale:** Solo founder + public artifact = highest scrutiny demand. The pattern that worked for SDG specs applies even harder to docs that other people will judge the founder by.

**Consequences:** Drafting timeline includes a review step for each major doc. Week 3 is dedicated to review across the most important four (README, Linear blueprint, GitHub blueprint, session playbook).

---

## DD-012 — License: deferred to founder, default Apache-2.0

**Status:** Open (decision deferred)
**Date:** 2026-05-11

**Decision:** Apache-2.0 by default unless founder picks MIT. The choice is in `10_open_questions_for_founder.md`.

**Rationale:** MIT is simpler. Apache-2.0 has explicit patent grant which is valuable for an opinionated stack that might overlap with patented workflow patents. Both are widely accepted in the open-source community.

---

## DD-013 — Self-application is the acceptance test

**Status:** Active
**Date:** 2026-05-11

**Decision:** The meta-project uses its own emerging stack to build itself. The public repo is built using the workflow it documents (Claude.ai project + Claude Code + Linear if enabled + Sync Queue + four-hat review). If the stack does not work to build itself, the stack is broken.

**Rationale:** Strongest available eat-your-own-dogfood validation. Any pain point we hit while building this is a pain point we must address in the docs.

**Consequences:** When a stack feature does not exist yet, we work around it explicitly, document the workaround, and feed the gap back into the design.

---

## DD-014 — Naming: `solo-claude-stack` is the working name

**Status:** Open (final name decision in `10_open_questions_for_founder.md`)
**Date:** 2026-05-11

**Decision:** `solo-claude-stack` is used in all draft material. Final name is one of the candidates in the open-questions doc. When the final name is picked, a single find-and-replace pass updates all draft material.

**Rationale:** Naming is bikeshed-bait. Lock a placeholder, ship the content, rename at the end. Avoids stalling design on naming.

---

## DD-015 — Six-plus-one improvements scope, no scope creep until v0.1 ships

**Status:** Active
**Date:** 2026-05-11

**Decision:** v0.1 covers exactly the seven improvements named in `00_PROJECT_INSTRUCTIONS.md`:
1. Skills catalog (with `project-bootstrap` skill)
2. TDD-based build process
3. Ralph + spec-kit + GSD integration
4. Context-structuring skill (subsumed by `project-bootstrap`)
5. Token-budget discipline
6. Review + QA process
7. Spec / goal / discovery process improvement

Any seventh+ improvement requires a v0.2 milestone and explicit founder approval.

**Rationale:** Solo founder + ~4–8 hr/week + parallel SDG work = hard ceiling on what fits in 4 weeks. Lock scope to ship.

---

## DD-016 — Skills are inside the public repo, not external dependencies

**Status:** Active
**Date:** 2026-05-11

**Decision:** All curated skills ship as files in `.claude/skills/<name>/SKILL.md` inside the public repo. Founders who fork get the skills immediately. We do not depend on Antigravity Awesome Skills, BB-Skills, or other external skill libraries for the recommended set.

We provide a sidebar that points to those libraries for further skills, but the recommended baseline is self-contained.

**Rationale:** External skill libraries change. Vendor-pin the baseline; recommend rather than require external sources. Forking the repo should give a working stack with no further `npx` installs.

**Consequences:** ~12 SKILL.md files in the public repo. Each one stays small (Skills docs recommend keeping them concise — see `code.claude.com/docs/en/skills`).

---

## DD-017 — `make check` (or language-equivalent) is the mandatory session-end gate

**Status:** Active
**Date:** 2026-05-11

**Decision:** Every Claude Code build session ends with a `make check` (or `npm run check`, or `cargo check`, or whatever the language idiom is) against the final commit. If the check fails, the session is not complete; the failure goes into a fix-or-revert decision before handoff.

**Rationale:** SDG validated this. The "looks done but doesn't pass tests" failure mode is the most common Claude Code session failure. `make check` against the final commit (not against intermediate commits) catches it.

**Consequences:** The CLAUDE.md template includes a `make check` section with language-specific guidance. The session-prompt template ends with "run `make check` against the final commit before declaring complete".

---

## DD-018 — Discovery + goal-setting templates are one-page each

**Status:** Active
**Date:** 2026-05-11

**Decision:** The discovery template fits on one page. The goal-setting template fits on one page. Combined into one Linear Document for the project, they form the "Constitution" of the project (in spec-kit terms).

**Rationale:** Solo founders have low tolerance for ceremony. One-page templates with explicit "what to skip" guidance get filled in; long templates do not.

**Consequences:** Templates are tight. Sections that some projects do not need are explicitly labeled "skip if not commercial" or "skip if no external stakeholders".

---

## Open design questions

See `10_open_questions_for_founder.md`.
