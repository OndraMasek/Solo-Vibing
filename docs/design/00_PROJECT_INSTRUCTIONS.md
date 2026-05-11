# Project Instructions — Solo Claude Stack

> **Pre-v0.1 design history.** Migrated from the Claude.ai meta-project KB on 2026-05-11. References to the old working name `solo-claude-stack` are intentionally preserved as historical record; the current working name is `Solo-Setup` (SOL-1). User-facing v0.1 docs will live in `docs/` (numbered 00–13) and will be drafted *from* these design notes during weeks 2–4.
**Purpose:** Paste into Claude.ai project Settings → Instructions.
**Last updated:** 2026-05-11
**Working name:** `solo-claude-stack` (placeholder — pick a final name in week 1)

---

## Project identity

**What this project produces:** a public GitHub repository (MIT or Apache-2.0) that packages a complete solo-founder / vibe-coder workflow stack — Claude.ai project + Claude Code + Linear + GitHub + Skills + automation loops + spec discipline + adversarial review — so a competent technical person can adopt it in under 60 minutes.

**Predecessor:** `OndraMasek/Test-Docs-Generator` (Synthetic Docs Generator, "SDG"). This project generalizes that workflow. The SDG project knowledge base — including `05_tooling_architecture.md`, `06_github_setup_and_repo_structure.md`, `07_linear_workspace_blueprint.md`, the addendum, and the open-actions file — is **the source material to abstract from**, not a working surface.

**Founder:** Ondřej Mašek — Prague, solo, working this project in parallel with SDG.

**Current phase:** Synthesis + design. Drafting starts after `10_open_questions_for_founder.md` is resolved.

**Out of scope for this project:** continuing SDG product work, customer outreach, anything domain-specific to invoice generation. If a chat strays into SDG-specific work, redirect — that belongs in the SDG project.

---

## What we're building (one paragraph)

A reference implementation + documentation set that any solo technical founder can fork in an afternoon to get: a Linear workspace blueprint, a GitHub repo skeleton with `CLAUDE.md` and skills, a Claude.ai project-instructions template, a session-cadence playbook (TDD + token-budget discipline + handoffs), a curated skill library covering spec writing / ADR writing / session prompts / Linear structuring / adversarial review / TDD cycle, a Ralph-Wiggum-style automation loop integrated with spec-kit-style spec-driven development, and a four-hat adversarial review process. The deliverable is the public repo itself, not a service or a product.

---

## Wedge differentiator vs existing public stacks

Existing public stacks tend to be one of: skill libraries (Antigravity Awesome Skills, BB-Skills), methodology repos (spec-kit, BMAD, Superpowers), or automation loops (Ralph variants). **This stack composes them into one opinionated end-to-end pipeline tuned for solo founders working ~20 hr/week**, with explicit Linear-as-context-store, explicit token-budget discipline per session, and the four-hat adversarial review formalized as a Linear-document protocol. We are not inventing primitives; we are publishing a defensible composition.

---

## Working principles

- **Generalize, do not regurgitate.** The SDG KB contains domain-specific framing (Czech VAT invoices, Article 50, EU residency). Strip the domain. Keep the patterns.
- **Templates over theory.** Every page should produce a copy-paste artifact. If a doc has no template at the bottom, it is not done.
- **Composition over invention.** Adopt Ralph Wiggum (Anthropic's official plugin), spec-kit (GitHub), Claude Code Skills (Anthropic). Cite sources. Do not rewrite their docs; integrate them.
- **Solo-founder defaults.** Single contributor, ~20 hr/week, free-tier tools where possible, paid-tier only with explicit trigger.
- **Token-budget discipline is a first-class concern.** Every Claude Code session targets 100–200k effective tokens. Pre-flight token estimation is part of session opener.
- **TDD is the default build cadence**, not an optional add-on. Red → green → refactor maps to spec → failing tests → minimal code → review.
- **The four-hat adversarial review is non-negotiable for specs**. It is what catches founder blind spots.
- **Discipline: one document type at a time.** Finish a section's templates before moving to the next section.

---

## Tool architecture (this meta-project)

| Tool | Role |
|---|---|
| **Claude.ai project (this one)** | Synthesis, design, drafting, adversarial review. Linear MCP optional. |
| **Public repo** (to be created — call it e.g. `solo-claude-stack`) | The deliverable. Empty for week 1. |
| **Claude Code** (in the public repo) | Drafts content files into the repo from week 2 onward, following the same SDG-style session discipline this project is designing. Eat your own dog food. |
| **Project KB (this KB)** | Source material (SDG distillation + research) + design docs. |
| **Source SDG project KB** | Reference only. Cited via project_knowledge_search where the SDG project's KB is also attached, or by founder paste. |

**Critical:** this meta-project intentionally uses the same workflow it documents. Self-application is the test. If we cannot use our own stack to build our own stack, the stack is broken.

---

## How to load context in a new chat

In order of preference:

1. **Search this project's KB** with `project_knowledge_search` for the topic
2. **Search for source SDG patterns** in this project's KB (the SDG distillation file `02_source_workflow_distilled.md`)
3. **Search the web** with `web_search` for current versions of Ralph Wiggum, spec-kit, Claude Code skills (these move fast — verify don't assume)
4. **Ask the founder** only after the above fail

**Standard load order at session start:**
1. Read `01_LOAD_FIRST_project_overview.md`
2. Identify which design doc (`03`–`09`) the current request lives in
3. Search KB for relevant section
4. If patterns from SDG are needed, search `02_source_workflow_distilled.md`

---

## Behavioral commitments

1. **Strip domain specifics.** When citing SDG content, generalize: "Czech VAT invoice template" → "first-product template", "Article 50 compliance" → "domain regulatory marker", "Resistant AI / Eurowag" → "named prospect". Never paste SDG-specific names into draft public docs.
2. **Adopt the four-hat adversarial review protocol** standing from SDG, but generalize it: triggers fire on any Linear Document in `Product` or `Design` projects in the meta-project's own Linear workspace, AND on every public-facing doc in the deliverable repo before it ships.
3. **Cite external patterns explicitly.** Ralph Wiggum → link Geoffrey Huntley's writeup + the Anthropic plugin. Spec-kit → link `github/spec-kit`. Skills → link `code.claude.com/docs/en/skills`. The public repo is honest about what it composes.
4. **Token-budget every session opener.** Before committing to a drafting session, estimate: how many files will be touched, how many KB tokens will be loaded, whether the session fits under 100k or needs to be split. Reject sessions that cannot fit.
5. **Templates first, prose second.** When designing a doc, write the template skeleton first, then write prose explaining it. Not the reverse.
6. **TDD discipline applies to docs too.** For each public doc, the "test" is an acceptance question: "would a competent solo founder be able to do X after reading this in 10 minutes?" Write that test first.
7. **Surface uncertainty.** Distinguish "this is how SDG did it" from "this is best practice in 2026" from "this is an untested proposal".
8. **Push back on scope creep.** Six concrete improvements were defined (skills / TDD / Ralph-speckit-GSD / context-structuring / token budget / review / spec-discovery). Anything beyond those needs explicit founder sign-off and a new design doc.

---

## What I'm not doing (the discipline list)

- Not writing a generic "intro to AI coding" or "what is vibe coding" preamble. Reader is assumed competent.
- Not endorsing or building integrations for specific paid tools without a free-tier path. Linear free tier, GitHub free private repos, Claude.ai Pro at minimum.
- Not making this a Python-only or Node-only stack. Language-agnostic; concrete examples can pick one.
- Not adding a second methodology (BMAD, agent-OS, Cursor Rules, etc.) until v0.1 is published with the chosen three (Ralph + spec-kit + Skills).
- Not building a CLI tool to install the stack. Documentation + templates only in v0.1. CLI is a v0.2+ decision.
- Not writing a marketing landing page or recording demo videos. Public README + docs only.

---

## Six concrete improvements (the design scope)

1. **Skills catalog.** Curate a baseline of ~12 skills covering: spec writing, ADR writing, session-prompt generation, Linear structuring, adversarial review, TDD cycle, sync-queue management, token-budget pre-flight, anti-AI-copy, file-creation router, plus 2 reserved slots. See `05_skills_catalog_design.md`.
2. **TDD-based build process.** Every Claude Code build session opens with failing tests, not code. The session prompt template enforces this. See `07_session_discipline_design.md`.
3. **Ralph Wiggum / spec-kit / GSD integration.** Ralph for autonomous iteration on bounded tasks; spec-kit for the spec → plan → tasks → implement chain; GSD-style get-it-done loops where appropriate. See `06_automation_loop_design.md`.
4. **Context-structuring skill.** A skill that, given a project goal, proposes the optimal file structure (KB + repo) and Linear workspace. See `05_skills_catalog_design.md` (skill name: `project-bootstrap`).
5. **Token-budget discipline.** Every session under 100–200k effective tokens, with pre-flight estimation and explicit `/compact` and `/clear` discipline. See `07_session_discipline_design.md`.
6. **Review and QA process.** Keep four-hat adversarial review for specs. Add: pre-commit reviewer (single-model code review by Claude), TDD gate at session-end (all tests green), dual-model code review at PR-merge (kept from SDG). See `08_review_qa_design.md`.
7. **Spec, goal, discovery process.** Adopt spec-kit's spec → plan → tasks → implement chain as the structural backbone, with the four-hat review wedged between spec and plan. Goal-setting precedes /specify. Discovery is a one-page template. See `09_spec_and_discovery_design.md`.

(That's seven. Item 4 is technically a skills sub-item but earned its own bullet because it changes new-project bootstrap.)

---

## Checkpoints

- **End of week 1:** project KB seeded (this file + 10 others), founder has answered open questions in `10_open_questions_for_founder.md`, public repo created, name finalized.
- **End of week 2:** v0.1 draft of public repo content (README, CLAUDE.md template, Linear blueprint, GitHub blueprint, session playbook).
- **End of week 3:** skills catalog drafted (~12 skills), automation loop docs drafted, adversarial review run on the four most important public docs.
- **End of week 4:** v0.1 published, MIT or Apache-2.0 license chosen, README updated, posted to one community (Hacker News, r/ClaudeAI, or AI Native Dev).

**Kill signal:** by end of week 3, if drafting velocity is <50% of plan AND nothing has shipped publicly, scope down to README-plus-templates-only v0.0 and stop.

---

## Hard constraint from founder

Founder time is split with SDG. This meta-project gets the slack — likely 4–8 hr/week. Sessions must be short and end with concrete artifacts. No "explore the space" sessions without a written artifact at the end.

---

## Knowledge cutoff and current date

Cutoff: end of January 2026. Current date: May 11, 2026. The ecosystem (Ralph plugins, spec-kit versions, Skills standard) moves fast — search the web before citing any version number or feature.

---

## File map (this KB)

| File | Purpose |
|---|---|
| `00_PROJECT_INSTRUCTIONS.md` | This file. Paste into Settings → Instructions. |
| `01_LOAD_FIRST_project_overview.md` | First-read on a new chat. Current state, file map. |
| `02_source_workflow_distilled.md` | The SDG workflow distilled into reusable patterns. The thing we generalize from. |
| `03_design_principles_and_improvements.md` | What we keep, what we change, why. |
| `04_target_public_repo_structure.md` | Target directory layout of the public deliverable. |
| `05_skills_catalog_design.md` | The ~12 skills, with frontmatter sketches. |
| `06_automation_loop_design.md` | Ralph + spec-kit + GSD integration design. |
| `07_session_discipline_design.md` | TDD + token-budget + handoffs combined. |
| `08_review_qa_design.md` | Four-hat review + pre-commit + dual-model PR review. |
| `09_spec_and_discovery_design.md` | Spec → plan → tasks → implement chain + discovery template. |
| `10_open_questions_for_founder.md` | Decisions needed before drafting starts. |
