# 05 — Skills Catalog Design

> **Pre-v0.1 design history.** Migrated from the Claude.ai meta-project KB on 2026-05-11. References to the old working name `solo-claude-stack` are intentionally preserved as historical record; the current working name is `Solo-Setup` (SOL-1). User-facing v0.1 docs will live in `docs/` (numbered 00–13) and will be drafted *from* these design notes during weeks 2–4.

**File purpose:** Design the baseline ~12 skills that ship in the public repo's `.claude/skills/` directory. Each has a draft SKILL.md sketch with frontmatter and a one-paragraph "what this skill does" plus the acceptance test (how we know it works).
**Last updated:** 2026-05-11

---

## Conventions for this stack's skills

- Every skill is a directory at `.claude/skills/<name>/` with at minimum `SKILL.md`.
- YAML frontmatter has `name` and `description`. `description` must be in the form "Use this skill when …" so Claude Code's auto-routing fires correctly (per Anthropic Skills docs and 2026 community guidance).
- SKILL.md body is concise: state what to do, not why. Keep loaded-into-context cost low.
- Skills that need templates or scripts keep them in the same directory, referenced from the SKILL.md body.
- Skills are designed to be project-scope by default (live in the project repo), promoted to user-scope (`~/.claude/skills/`) only when the founder confirms they apply across all projects.

---

## The 12-skill baseline

| # | Skill name | Trigger phrases | Lives in | Notes |
|---|---|---|---|---|
| 1 | `project-bootstrap` | "bootstrap a new project", "set up a new repo for", "start a new project" | Project | Most important; produces Linear blueprint + CLAUDE.md + checklist |
| 2 | `spec-writer` | "write a spec for", "draft a feature spec", "spec out" | Project | Wraps spec-kit `/speckit.specify` with stack conventions |
| 3 | `adr-writer` | "write an ADR for", "record a decision about", "log this decision" | Project | Applies the strategic-vs-build-time split heuristic |
| 4 | `session-prompt` | "draft the next session prompt", "prep a Claude Code session", "what's the session opener" | Project | The pre-flight checklist + handoff doc generator |
| 5 | `linear-structurer` | "propose Linear structure", "what Linear projects do I need", "design my workspace" | Project | Wrapped by `project-bootstrap`, also callable standalone |
| 6 | `adversarial-reviewer` | "run the adversarial review", "four-hat review", "review this spec" | Project | Executes the four-hat protocol; one message per hat then synthesis |
| 7 | `tdd-cycle` | "write tests for", "implement this with TDD", "red-green-refactor" | Project | Wraps the TDD session loop |
| 8 | `sync-queue-runner` | "process the sync queue", "sync Linear to repo", "any pending syncs" | Project | Code-Claude session-start chore |
| 9 | `token-budget-preflight` | "estimate the session budget", "will this fit", "what's the token cost" | Project | Run at session opener; outputs go/no-go + split plan if needed |
| 10 | `ralph-task-shaper` | "is this a Ralph task", "should I run a Ralph loop", "shape this as a Ralph task" | Project | Decision table + Ralph prompt drafting |
| 11 | `speckit-runner` | "run the spec-kit chain", "speckit specify and plan", "do the full spec workflow" | Project | Walks the founder through `/speckit.constitution` → `/specify` → `/clarify` → review → `/plan` → `/tasks` → `/analyze` → `/implement` |
| 12 | `build-log-writer` | "draft this week's build log", "Friday build log", "weekly summary" | Project | Friday cadence template-filler |

Plus two reserved slots:
- (Reserved) `customer-call-logger` — if the founder's project has a Customers module enabled
- (Reserved) `outreach-message-drafter` — if the founder's project has an Outreach Log module enabled

These two reserved skills are produced by `project-bootstrap` only when the GTM module is enabled.

---

## Skill sketches

### 1. `project-bootstrap`

```markdown
---
name: project-bootstrap
description: Use this skill when the user is starting a new project and asks to bootstrap, set up, scaffold, or initialize a project. Produces a Linear workspace blueprint, initial CLAUDE.md, initial README, label taxonomy, and a manual bootstrap checklist. Asks the user one short question to gather the project's nature (OSS / SaaS / consulting / research) and one question to determine whether GTM modules are needed.
---

# Project bootstrap

Given a one-paragraph project description, produce:

## 1. Project profile
- Working name
- Project type (OSS library / SaaS / consulting / research / other)
- Commercial: yes/no (drives GTM module inclusion)
- Solo or small team
- Time budget (hours/week)
- First milestone (≤ 4 weeks out)

## 2. Recommended Linear workspace
Always include: Strategy, Spec, Sync Queue, Build Log.
Include GTM + Customers + Outreach Log if commercial == yes.
Include Research project if project type == research.

For each project, output:
- Name + emoji
- Purpose (one sentence)
- Document templates needed
- Issue templates needed
- Labels (from `templates/linear/label_taxonomy.md`, plus 0–3 project-specific labels suggested)

## 3. Recommended initial CLAUDE.md
Use `templates/github/repo_skeleton/CLAUDE.md.template` and fill in:
- Project identity
- Source-of-truth rules
- Locked architectural decisions (none yet — placeholder)
- Hard constraints (language pin, framework pin if known)
- "What you're not doing" (out-of-scope list — first guess from description)

## 4. Recommended initial README.md
Project pitch in ≤200 words. Roadmap as a checklist with 3 milestones.

## 5. Bootstrap checklist for the founder
A numbered list, ≤15 steps, each ≤2 minutes. Covers:
- Create Linear workspace + projects
- Create labels
- Create initial issues (Strategy ADR-001 — "Initial project decisions" + Sync Queue first entry + Build Log W1)
- Create GitHub repo + push initial skeleton
- Connect MCPs (Linear in chat-Claude + Claude Code, GitHub in Claude Code)
- Paste CLAUDE.md into project Settings → Instructions
- Run `verify_setup.sh`

Output as a single markdown document the founder can save to their KB.
```

**Acceptance test.** Given the prompt "Bootstrap a new project: a Rust CLI for converting WebVTT subtitles to SRT, solo, ~10 hours/week, MIT license, ship to crates.io", the skill produces a Linear blueprint without GTM/Customers/Outreach, with Strategy/Spec/Sync Queue/Build Log only, with one Rust-specific label, and the bootstrap checklist completes in <60 minutes for a competent founder.

---

### 2. `spec-writer`

```markdown
---
name: spec-writer
description: Use this skill when the user asks to write a spec, draft a feature spec, spec out a feature, or write a Product/Spec project document. Wraps the spec-kit /speckit.specify pattern with this stack's conventions (out-of-scope fencing, review status header, named provenance section).
---

# Spec writing

Produce a Linear Document in the `Spec` (or `Product`) project with the following structure:

```
# <Spec name>

**Status:** Draft | In Review | Approved | Superseded
**Review status:** Not started | Adversarial review v1 in progress | Adversarial review v1 complete
**Linked ADRs:** D-NNN, D-NNN
**Date opened:** YYYY-MM-DD
**Date last revised:** YYYY-MM-DD

## Problem
<one paragraph>

## Goal
<one paragraph; the desired end state>

## Out of scope
<bullet list; what this spec is NOT trying to do>

## Acceptance criteria
<numbered list, testable each>

## Open questions
<bullet list; resolved before /speckit.plan>

## Provenance
<who proposed this, what triggered it, links to relevant chats/issues>
```

After producing the doc, also create the Linear issue in Spec project pointing to it, and propose the four-hat adversarial review using the `adversarial-reviewer` skill.
```

**Acceptance test.** Given "Spec out the spec-writer skill", produces a Linear-document-shaped spec with all sections filled, no empty placeholders, fits one screen.

---

### 3. `adr-writer`

```markdown
---
name: adr-writer
description: Use this skill any time the user wants to record an architectural decision, write an ADR, log a decision, or capture "we're going with X over Y" choices. Applies the strategic-vs-build-time split heuristic: strategic ADRs go to Linear AND repo, build-time ADRs go only to repo.
---

# ADR writing

Apply the classification heuristic first:
- **Strategic** if: business model, scope, regulatory posture, GTM, pricing, customer commitments, hiring, capital. → Linear issue (Strategy project, `type:long-lived`, status Done) + Sync Queue → `docs/decisions/NNNN-*.md`.
- **Build-time** if: library choice, encoding pattern, parser conformance, file format, internal API, test infrastructure, dependency pin. → `docs/decisions/NNNN-*.md` only, with one-line cross-reference in the parent build issue's session-end comment.
- **Borderline** → default to strategic.

ADR template:
```
# D-NNN — <decision in one line>

**Date:** YYYY-MM-DD
**Status:** Active | Superseded by D-MMM | Deprecated
**Class:** Strategic | Build-time
**Linked Linear issue:** SDG-NN (if strategic)

## Context
<one paragraph>

## Decision
<one paragraph>

## Consequences
<bullet list>

## Alternatives considered
<bullet list with one-line dismissal of each>
```
```

**Acceptance test.** Given "Record the decision to use uv over poetry for Python dependency management", produces a build-time ADR (correctly classified), repo-only, with a clean one-paragraph context section.

---

### 4. `session-prompt`

```markdown
---
name: session-prompt
description: Use this skill when the user asks to draft a Claude Code session prompt, prep the next session, or write a session opener. Produces the full session opener including pre-flight checklist, goal, acceptance criteria, TDD instructions, token-budget estimate, and handoff section.
---

# Session prompt

Output a markdown block the user can paste as the first message to a fresh Claude Code session:

```
# Session goal
<one sentence>

# Acceptance criteria
1. <testable>
2. <testable>
3. <testable>

# Pre-flight (do first, in order)
1. Read `CLAUDE.md` at repo root
2. Read Linear Sync Queue for `sync:pending` issues — process before doing anything else
3. Read Linear Spec doc: <link>
4. Read last session's status comment: <link>
5. Confirm token-budget pre-flight: estimated <NN>k effective tokens (using token-budget-preflight skill)

# Work plan
- Step 1: <action>
- Step 2: <action>
- ...

# Rules in force this session
- TDD: write failing test, verify red, implement, verify green, refactor, commit
- Commit on green only
- Three strikes stop: if a unit fails 3 consecutive attempts, stop and surface
- 4-hour cap: if elapsed wall time hits 4 hours, hand off
- `make check` against final commit before declaring complete

# Handoff (fill on session end)
- What landed (commits, files, tests)
- What did NOT land (reason)
- Next session opener: <link to new session-prompt doc>
- Status comment posted to: <Linear issue link>
```
```

**Acceptance test.** Given "Draft the next session prompt for implementing the project-bootstrap skill", produces a complete prompt with non-placeholder content in every section.

---

### 5. `linear-structurer`

```markdown
---
name: linear-structurer
description: Use this skill when the user asks to design or propose a Linear workspace, decide which projects to enable, or what labels they need. Outputs the workspace blueprint (projects + labels + workflow states) for the given project type.
---

# Linear structurer

Inputs:
- Project type (OSS library / SaaS / consulting / research / other)
- Commercial (yes/no)
- Solo or small team
- Specific concerns (regulated industry, customer-facing, etc.)

Output the workspace blueprint covering:
- Team name + issue prefix (3 letters)
- Projects list (core + optional, justified per project)
- Per-project document templates needed
- Label taxonomy: `sync:*`, `type:*` always; `vertical:*`, `country:*` if relevant; project-specific labels suggested
- Workflow state mapping per project (Backlog, Todo, In Progress, In Review, Done, Canceled)
- Capacity planning (estimated issue burn rate; when to upgrade past free tier)
```

**Acceptance test.** For an OSS Rust CLI: outputs Strategy + Spec + Sync Queue + Build Log; no GTM/Customers/Outreach; labels `sync:*`, `type:long-lived`, plus `area:cli` and `area:docs` as Rust-CLI-shaped suggestions; estimated issue count stays under free tier.

---

### 6. `adversarial-reviewer`

```markdown
---
name: adversarial-reviewer
description: Use this skill when the user asks to run an adversarial review, four-hat review, or kill-or-go review on a spec or major decision. Executes one message per hat then a synthesis. Out-of-scope-fenced against locked decisions.
---

# Adversarial reviewer

Confirm gate first: "Run the four-hat review on <spec name>? (yes/no)".

On yes, run all four hats. One message per hat. Each hat outputs findings as:

| ID | Severity | Effort | Lock-in | Finding | Recommended action |
|---|---|---|---|---|---|

- **Severity:** blocker / high / medium / low
- **Effort:** to address — XS / S / M / L
- **Lock-in:** does addressing this require revisiting a locked decision? yes/no

Hats:
1. **Skeptic / kill-or-go.** Would this kill the project if wrong? What's the worst-case unfolding?
2. **Implementation.** Can this be built within the timebox by this founder with this stack?
3. **External.** What does a competent member of the target audience say? What objections do they raise?
4. **Future-self.** What does the 6-month-future founder say about this choice?

After four hats, output the synthesis:
- Top 3 findings to address before moving on
- Findings deferred to `Open questions for founder`
- Findings dismissed with rationale
- Updated `Review status:` for the spec doc

Save the review as a Linear Document titled `<Spec name> — Adversarial Review v<N>` in the same project as the spec.
```

**Acceptance test.** Given a draft spec, produces four hat reports with concrete findings (not "looks good"), severity/effort/lock-in marked, synthesis identifies the top 3.

---

### 7. `tdd-cycle`

```markdown
---
name: tdd-cycle
description: Use this skill when the user asks to implement a feature with TDD, write tests first, run a red-green-refactor cycle, or use test-driven development. Enforces the red-green-refactor discipline per acceptance criterion.
---

# TDD cycle

For each acceptance criterion in the current task:

1. **Red.** Write the failing test. Run it. Confirm it fails for the right reason (not a syntax error or import issue).
2. **Green.** Write the minimum code to make the test pass. No more.
3. **Verify green.** Run the full test suite (or at minimum the affected module + integration tests).
4. **Refactor.** Clean up if needed. Re-run tests after each refactor step.
5. **Commit.** Conventional Commit format (`feat:`, `fix:`, `test:`, etc.). Commit message names the acceptance criterion just satisfied.
6. **Next criterion.** Loop.

If a test fails 3 consecutive attempts in the green phase, stop and surface to the user.
If the test was never red, that test is broken — fix the test, then loop.
```

**Acceptance test.** Given a feature spec with 3 acceptance criteria, the skill produces 3 commits, one per criterion, each with the test written first (verifiable via `git log`).

---

### 8. `sync-queue-runner`

```markdown
---
name: sync-queue-runner
description: Use this skill at the start of every Claude Code session, or any time the user asks to process the sync queue, sync Linear to the repo, or check pending syncs. Reads Linear Sync Queue, processes pending items, commits to repo, marks issues synced.
---

# Sync queue runner

Steps:
1. Query Linear `Sync Queue` for issues with label `sync:pending`.
2. For each, read the source content from Linear, write or update the corresponding markdown file in repo, commit with message `[sync] Linear→docs: <issue title>`, change label to `sync:synced` and status to `Done`.
3. Compare repo `docs/` files against the corresponding Linear documents (modified-time check). If divergence found beyond the Sync Queue, create a new Sync Queue issue with label `sync:conflict` and surface to user; do NOT auto-resolve.
4. Report what was synced + any conflicts found.
```

**Acceptance test.** Given a Linear workspace with 3 pending sync issues, the skill commits the 3 files, marks the issues, reports the outcome in one message.

---

### 9. `token-budget-preflight`

```markdown
---
name: token-budget-preflight
description: Use this skill when starting a Claude Code session, or when the user asks to estimate the session budget, check if a task will fit, or pre-flight the token cost. Outputs a go / no-go / split-plan decision.
---

# Token-budget pre-flight

Inputs:
- Planned files to touch (count + rough size)
- Tools enabled (MCP servers; their schemas have fixed cost)
- CLAUDE.md size

Estimation rules of thumb (verify against `code.claude.com/docs` if changed):
- Fixed overhead: CLAUDE.md (~3–5k tokens for a typical project), MCP schemas (~5–15k each loaded), system tooling.
- Per-file: rough heuristic 1k tokens per 200 lines of code.
- Conversation overhead: assume 30k for a typical 30-message session.

Outputs:
- Estimated peak tokens for this session
- Compared to 100k target and 200k ceiling
- Decision: **GO** (<100k), **GO with /compact at 70%** (100–150k), **SPLIT** (>150k expected)
- If SPLIT, propose a session-by-session plan with handoff artifacts.
```

**Acceptance test.** Given "I want to refactor the entire `src/render/` directory (8 files, ~1500 LOC total)", outputs an estimate, marks it GO or SPLIT, and if SPLIT proposes ≥2 sessions.

---

### 10. `ralph-task-shaper`

```markdown
---
name: ralph-task-shaper
description: Use this skill when the user asks whether a task is suitable for a Ralph loop, how to shape a task for autonomous iteration, or to draft a Ralph prompt. Applies the "is this Ralph-shaped" decision table and produces a Ralph-compatible prompt with completion criteria.
---

# Ralph task shaper

Apply the decision table:

| Task property | Ralph-shaped? |
|---|---|
| Bounded success criterion (testable) | ✅ |
| Bulk repetitive work (migrations, refactors, coverage filling) | ✅ |
| Strategy or judgment-heavy | ❌ |
| Customer-facing artifacts | ❌ |
| Spec drafting | ❌ |
| Subjective "good" without test | ❌ |

If NOT Ralph-shaped: tell the user, propose alternative (manual session, single-pass Code-Claude task).

If Ralph-shaped: produce the Ralph prompt template:
```
/ralph-loop "<task description>

Requirements:
- <bullet>
- <bullet>

Success criteria:
- All tests passing
- <other testable criterion>
- No linter errors
- Output: <promise>COMPLETE</promise> when done." --max-iterations <NN> --completion-promise "COMPLETE"
```

Always include `--max-iterations`. Default to 30 for medium tasks, 50 for large refactors. Recommend running in a sandbox (Docker or sandbox-environment per `ghuntley.com/ralph/`).
```

**Acceptance test.** Given "Convert all unittest tests to pytest", classifies Ralph-shaped, outputs a complete `/ralph-loop` command. Given "Decide whether to pivot to a different vertical", classifies NOT Ralph-shaped, refuses and explains.

---

### 11. `speckit-runner`

```markdown
---
name: speckit-runner
description: Use this skill when the user asks to run the spec-kit chain, run /speckit.specify, do the full spec-driven workflow, or step through the spec → plan → tasks → implement flow. Walks the founder through each phase with the stack's four-hat review wedged between /clarify and /plan.
---

# Spec-kit runner

Requires spec-kit installed in the project (`uv tool install specify-cli --from git+https://github.com/github/spec-kit.git`).

Walk through:
1. `/speckit.constitution` — done once per project. If not yet done, do it first.
2. `/speckit.specify <feature description>` — feature spec.
3. `/speckit.clarify` — resolves ambiguities (optional but recommended).
4. **Four-hat adversarial review** — using `adversarial-reviewer` skill. This is the human-in-the-loop wedge point.
5. Apply review findings → revise spec.
6. `/speckit.plan` — technical plan.
7. `/speckit.tasks` — task breakdown, TDD-ordered (`--tdd` flag).
8. `/speckit.analyze` — cross-artifact consistency check.
9. `/speckit.implement` — execution. Optionally wrap in Ralph if the tasks are Ralph-shaped (use `ralph-task-shaper`).
10. TDD session loop per task (use `tdd-cycle`).
11. Code review (single-Claude pre-PR; optional dual-model at PR).
12. Merge.
13. Update Build Log (use `build-log-writer`).
14. Update Sync Queue if specs changed.

At each step, output the actual command to run and a one-line description of what to expect.
```

**Acceptance test.** Given a feature description, the skill walks through all 14 steps in order, pausing at the four-hat review for confirm gate, completing in <2 hours wall time for a small feature.

---

### 12. `build-log-writer`

```markdown
---
name: build-log-writer
description: Use this skill on Friday afternoons or any time the user asks to write the weekly build log, draft the Friday summary, or fill in this week's build log. Produces the Linear Build Log issue body for the current ISO week.
---

# Build log writer

Inputs (offered as questions if not provided):
- Current ISO week (default = computed from today)
- What landed (commits + Linear updates + decisions)
- What did NOT land (carryover)
- Customer signals (if commercial project)
- Mood / energy / risks

Output:
```
# Week YYYY-WNN (date range) — <one-line theme>

## What landed
### Strategic decisions
- ...

### Build
- ...

### Operations
- ...

## What did NOT land (carryover)
- ...

## Next week plan
- ...

## Customer signals this week
- ...

## Mood / energy / risks
- ...

## Synced to GitHub
- Sync Queue: SDG-NN, SDG-NN
```

Then create a Linear issue in Build Log project with this body.
Then create a Sync Queue entry to mirror the issue body to `build-log/YYYY-WNN.md` in the repo.
```

**Acceptance test.** On a Friday, given a chat history of the week, the skill drafts a Build Log issue body covering all sections without leaving any section empty (uses "none this week" for empty sections), and creates both the Linear issue and the Sync Queue entry.

---

## Reserved skills (produced by `project-bootstrap` only when GTM module enabled)

### R1. `customer-call-logger`
Drafts the comment to add to a Customers issue after a call. Structured per SDG pattern: Pain / Quotes / Objections / Budget signal / Next step / My read.

### R2. `outreach-message-drafter`
Drafts the outreach message body + Linear Outreach Log issue. References the GTM Outreach Templates document.

---

## Skill design open questions

→ `10_open_questions_for_founder.md`

- Should `speckit-runner` and `ralph-task-shaper` ship in v0.1 or v0.2 (spec-kit may not yet support Claude Code skill-mode for all subcommands)?
- Should `project-bootstrap` ship as a single monolithic skill or split into 3 (`linear-structurer` + `claude-md-writer` + `bootstrap-checklist`)?
- Is `token-budget-preflight` worth the complexity given Claude 4.5+ has context-awareness built in (per `platform.claude.com/docs/en/build-with-claude/context-windows`)?

---

## Maintenance commitments for the v0.1 skill set

- Monthly skill audit: any skill not triggered in 30 days is reviewed for description quality. If the trigger is unclear, the description is rewritten. If the skill is genuinely unused, it is moved to `examples/skills/` rather than the baseline.
- Cross-agent portability check quarterly: are the skill descriptions still triggering correctly on Claude Code latest, plus do they survive the SKILL.md standard if portable to Codex/Gemini.
- Token cost per skill check: aim for <2k tokens per SKILL.md body. Larger skills move logic to supporting files referenced from the body.
