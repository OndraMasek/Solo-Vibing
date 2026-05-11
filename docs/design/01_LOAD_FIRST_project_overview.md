# 01 — Load First: Project Overview

> **Pre-v0.1 design history.** Migrated from the Claude.ai meta-project KB on 2026-05-11. References to the old working name `solo-claude-stack` are intentionally preserved as historical record; the current working name is `Solo-Setup` (SOL-1). User-facing v0.1 docs will live in `docs/` (numbered 00–13) and will be drafted *from* these design notes during weeks 2–4.

**File purpose:** First doc to read in any new chat in this project. Captures current state, file map, and "where do I go next" decision tree.
**Last updated:** 2026-05-11

---

## What this project is

A meta-project to produce a public GitHub repository that generalizes the workflow developed for the Synthetic Docs Generator (SDG) project so that any competent solo technical founder ("vibe coder") can adopt it in under an hour.

**Deliverable:** a single public GitHub repo (working name `solo-claude-stack`) under MIT or Apache-2.0 license.

**Not the deliverable:** a service, a SaaS, a CLI, a hosted starter generator. Just docs + templates + skills.

---

## Anchored decisions (locked, do not re-litigate)

1. **Generalize from SDG, do not copy.** Strip every domain specific (Czech invoices, Article 50, named EU prospects). Keep the patterns.
2. **Compose three external primitives.** Ralph Wiggum (Anthropic plugin), GitHub spec-kit, Claude Code Skills. Do not invent replacements.
3. **Linear is in the recommended stack.** Free tier. The SDG result was that Linear's combination of issue tracker + document store + mobile capture + Linear MCP genuinely works. We recommend it; we provide an alternative-tools section for people on different stacks.
4. **GitHub is in the recommended stack.** Private or public repos. Fine-grained PAT for GitHub MCP in Claude Code (the path SDG verified works).
5. **Two-Claude architecture is in the recommended stack.** Claude.ai (chat) for strategy and writing, Claude Code (terminal) for build. They sync through Linear.
6. **Bootstrap with Skills.** A `project-bootstrap` skill that proposes file structure + Linear workspace given a one-paragraph project description.
7. **TDD by default.** Build sessions open with failing tests, not code.
8. **Token-budget per session: 100–200k effective.** Pre-flight estimation is mandatory in the session prompt template.
9. **Four-hat adversarial review on every public-facing doc** before it ships, plus on every spec in the stack's user-facing workflow.
10. **License: MIT or Apache-2.0.** Decision deferred to `10_open_questions_for_founder.md`. Default Apache-2.0 if no founder preference.

---

## Current state (as of 2026-05-11)

- This KB is seeded with 11 files (this one + 10 design docs + 1 open-questions doc).
- Public repo: **not yet created.** Pending name + license decision.
- External patterns verified current as of 2026-05-11:
  - Ralph Wiggum plugin: official Anthropic plugin, exists at `anthropics/claude-code` under `plugins/ralph-wiggum/`. Geoffrey Huntley's original writeup at `ghuntley.com/ralph/`.
  - GitHub spec-kit: at `github/spec-kit`, version 0.8.6 (May 2026), supports Claude Code via Skills-mode integration (`--integration-options="--skills"`).
  - Claude Code Skills: documented at `code.claude.com/docs/en/skills`. SKILL.md + YAML frontmatter is the spec.
- SDG project KB referenced as source material; specific files referenced are listed in `02_source_workflow_distilled.md`.

---

## Quick "where do I go" decision tree

| If you want to … | Read |
|---|---|
| Understand the meta-project rules | `00_PROJECT_INSTRUCTIONS.md` |
| See the SDG patterns we're generalizing from | `02_source_workflow_distilled.md` |
| Understand what we're improving vs the SDG baseline | `03_design_principles_and_improvements.md` |
| See what the public repo will look like | `04_target_public_repo_structure.md` |
| Work on the skills catalog | `05_skills_catalog_design.md` |
| Work on Ralph / spec-kit / GSD integration | `06_automation_loop_design.md` |
| Work on session discipline (TDD, token budget) | `07_session_discipline_design.md` |
| Work on the review + QA process | `08_review_qa_design.md` |
| Work on spec writing / discovery | `09_spec_and_discovery_design.md` |
| Find a question that's blocking us | `10_open_questions_for_founder.md` |

---

## How a typical chat session in this project should go

**Opener** (founder): "Let's work on the skills catalog — draft the `session-prompt` skill."

**Claude opener** (in this project):
1. Acknowledge the target file: `05_skills_catalog_design.md`.
2. Search this KB for prior thinking on that skill.
3. Web search for `Claude Code skills SKILL.md frontmatter 2026` if version-sensitive details are needed.
4. Propose: rough SKILL.md content + acceptance test (what would prove this skill works).
5. Wait for founder feedback before producing the final artifact.

**End of session:**
1. Save the artifact into the right KB file (or, once the public repo exists, into the right repo path).
2. Update this `01_LOAD_FIRST` if a state change occurred (new doc finalized, new section unblocked).
3. If a strategic decision was made, append to `03_design_principles_and_improvements.md` as a numbered design decision (DD-N).

---

## What chat-Claude can do in this project

Read+write to this project's KB via `project_knowledge_search` (read) and by producing downloadable files for the founder to upload (write).

If a Linear workspace is set up for this meta-project, chat-Claude can also use Linear MCP to manage issues and documents — but **a separate Linear workspace for the meta-project is optional in v0**. Until weeks 3–4 (when volume justifies it), this project lives entirely in the Claude.ai KB and the public repo. The SDG Linear workspace stays SDG-only.

---

## Source-of-truth rule for this project

1. If `00_PROJECT_INSTRUCTIONS.md` and a design doc disagree → `00_*` wins.
2. If a design doc and the SDG distillation disagree → design doc wins (we are diverging on purpose).
3. If two design docs disagree → surface the conflict, do not guess. Resolve in chat.
4. Once the public repo is live, the repo's `docs/` becomes canonical for shipped content; KB design docs become archived design history.
