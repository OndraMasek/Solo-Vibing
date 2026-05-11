# 04 — Target Public Repository Structure

> **Pre-v0.1 design history.** Migrated from the Claude.ai meta-project KB on 2026-05-11. References to the old working name `solo-claude-stack` are intentionally preserved as historical record; the current working name is `Solo-Setup` (SOL-1). User-facing v0.1 docs will live in `docs/` (numbered 00–13) and will be drafted *from* these design notes during weeks 2–4.

**File purpose:** Layout of the deliverable repository. Drafted before construction. Names ending in `*.md.template` are user-fillable; names without are stack-canonical.
**Last updated:** 2026-05-11

---

## Top-level

```
solo-claude-stack/
│
├── README.md                                  ← project pitch, 30-min quickstart, prerequisites
├── LICENSE                                    ← Apache-2.0 (default) or MIT
├── CONTRIBUTING.md                            ← how to propose changes
├── CHANGELOG.md                               ← versioned changes
├── CLAUDE.md.template                         ← copy → your-repo/CLAUDE.md and fill in
├── .gitignore.template                        ← standard exclusions
│
├── docs/
│   ├── 00_quickstart.md                       ← 30-minute setup, in order
│   ├── 01_philosophy.md                       ← principles, trade-offs, what this isn't
│   ├── 02_tool_architecture.md                ← two-Claude + Linear + GitHub spine
│   ├── 03_linear_setup.md                     ← workspace blueprint, projects, labels
│   ├── 04_github_setup.md                     ← repo structure, MCP setup, PAT discipline
│   ├── 05_claude_project_setup.md             ← Claude.ai project config, MCPs, knowledge base
│   ├── 06_claude_code_setup.md                ← Claude Code install, MCPs, CLAUDE.md
│   ├── 07_session_workflow.md                 ← per-session cadence, TDD, handoffs
│   ├── 08_spec_discipline.md                  ← discovery → goals → spec-kit chain
│   ├── 09_token_budget.md                     ← 100k–200k discipline, /compact, /clear
│   ├── 10_review_qa.md                        ← four-hat review, single + dual model code review
│   ├── 11_automation_loops.md                 ← Ralph Wiggum, when to use, when not to
│   ├── 12_alternative_tools.md                ← Notion vs Linear, Cursor vs Claude Code, etc.
│   └── 13_faq_and_pitfalls.md                 ← common founder mistakes
│
├── templates/
│   ├── claude_project_instructions.md.template
│   ├── linear/
│   │   ├── workspace_blueprint.md
│   │   ├── label_taxonomy.md
│   │   ├── issue_template_adr.md
│   │   ├── issue_template_customer.md
│   │   ├── issue_template_outreach.md
│   │   ├── issue_template_build_log.md
│   │   ├── issue_template_sync_queue.md
│   │   └── document_template_strategy.md
│   ├── github/
│   │   ├── repo_skeleton/                     ← copy-paste skeleton (filed under repo_skeleton/)
│   │   │   ├── README.md.template
│   │   │   ├── CLAUDE.md.template
│   │   │   ├── .gitignore
│   │   │   ├── pyproject.toml.template
│   │   │   └── Makefile.template
│   │   ├── pull_request_template.md
│   │   └── issue_templates/
│   │       ├── bug_report.md
│   │       └── feature_request.md
│   ├── specs/
│   │   ├── adr_template.md
│   │   ├── adr_classification_heuristic.md    ← strategic vs build-time, with examples
│   │   ├── spec_template.md                   ← simpler than spec-kit, for non-feature work
│   │   ├── session_prompt_template.md         ← the Claude Code session opener
│   │   ├── goal_setting_template.md           ← one page
│   │   └── discovery_template.md              ← one page
│   ├── reviews/
│   │   ├── adversarial_review_protocol.md     ← the standing protocol doc
│   │   ├── adversarial_review_template.md     ← the per-review document
│   │   ├── hat_1_skeptic.md                   ← prompt for hat 1
│   │   ├── hat_2_implementation.md
│   │   ├── hat_3_external.md
│   │   └── hat_4_future_self.md
│   └── build_log/
│       └── weekly_template.md                 ← Friday cadence template
│
├── .claude/
│   ├── skills/
│   │   ├── project-bootstrap/SKILL.md
│   │   ├── spec-writer/SKILL.md
│   │   ├── adr-writer/SKILL.md
│   │   ├── session-prompt/SKILL.md
│   │   ├── linear-structurer/SKILL.md
│   │   ├── adversarial-reviewer/SKILL.md
│   │   ├── tdd-cycle/SKILL.md
│   │   ├── sync-queue-runner/SKILL.md
│   │   ├── token-budget-preflight/SKILL.md
│   │   ├── ralph-task-shaper/SKILL.md
│   │   ├── speckit-runner/SKILL.md
│   │   └── build-log-writer/SKILL.md
│   └── commands/
│       └── (optional slash commands; same SKILL.md format)
│
├── examples/
│   ├── README.md                              ← what's in here, what each example demonstrates
│   ├── greenfield_oss_library/                ← bootstrapping a pure OSS project
│   │   ├── linear_workspace_export.md
│   │   ├── README.md.example
│   │   └── CLAUDE.md.example
│   ├── solo_saas_v0/                          ← bootstrapping a one-founder SaaS
│   │   ├── linear_workspace_export.md
│   │   ├── README.md.example
│   │   └── CLAUDE.md.example
│   └── consulting_engagement/                 ← bootstrapping a short-term client project
│       └── ...
│
├── case_studies/
│   ├── README.md                              ← what a case study contains
│   └── sdg_synthetic_docs_generator.md        ← anonymized SDG retrospective; cite as origin
│
└── scripts/
    ├── README.md                              ← what scripts are here, in what order
    ├── verify_setup.sh                        ← post-bootstrap sanity check
    └── (others tbd)
```

---

## What each top-level directory exists for

### `/docs/`
Numbered narrative docs. The reader walks `00` → `13` for full understanding. Each one ends with a checklist of "templates this section uses" linking into `/templates/`.

### `/templates/`
Copy-paste artifacts. Every doc references one or more templates. The convention is: docs explain, templates do.

The convention for files:
- `*.md` is canonical content, used as-is.
- `*.md.template` is meant to be copied, renamed, and filled in.

### `/.claude/skills/`
The curated baseline of ~12 skills (see `05_skills_catalog_design.md`). Per Anthropic Skills standard, each is a directory with `SKILL.md`. They are version-controlled inside the repo. Forking the repo gets them automatically.

### `/.claude/commands/`
Slash-command equivalents for the skills that benefit from being explicitly invokable (e.g. `/project-bootstrap`). Same SKILL.md format per Claude Code 2026 convention.

### `/examples/`
Three worked examples showing the stack applied to different project shapes: an OSS library, a one-founder SaaS, a consulting engagement. Each example contains the `.md.example` files filled in for that shape, plus a notional Linear-workspace export. Examples are read-only references, not templates.

### `/case_studies/`
Retrospectives. `sdg_synthetic_docs_generator.md` is the origin story — what worked, what did not, what lessons drove which design decision in this stack. Anonymized of company-specific details but explicit about the problem domain.

### `/scripts/`
Convenience scripts. `verify_setup.sh` runs after the founder follows the quickstart to confirm Linear MCP is reachable, GitHub MCP is reachable, the skills folder is present, etc. Light scripting only — DD-001 says no CLI tool.

---

## Naming and casing conventions

- All file names lowercase with underscores (`session_workflow.md`, not `SessionWorkflow.md`).
- Numbered docs: two-digit prefix (`00_*`, `01_*`).
- Templates end with `.template` only if they are meant to be copied; canonical content does not.
- `CLAUDE.md` and `README.md` keep their capitalization (community conventions).

---

## What is NOT in the repo

- No code (the stack is documentation + templates + skills, not a library)
- No CI/CD workflows (.github/workflows/) in v0.1 — we add them only when contributors arrive
- No translations — English only in v0.1
- No video assets — link to external videos if relevant, do not host them
- No tracking pixels, analytics, or telemetry of any kind

---

## Versioning

- Semantic-ish. `v0.1` = first public release. `v0.2`, `v0.3`, … for documentation additions and new skills. `v1.0` when the stack has been used by ≥5 external founders and the README rewrite reflects that.
- Tagged on git. Each tag has a CHANGELOG entry.

---

## Bootstrapping a new project from this repo

The README's quickstart section (`docs/00_quickstart.md`) walks through:

1. **Fork** this repo (or clone-and-rename for private projects).
2. **Rename** the fork to your project name.
3. **Run** `/project-bootstrap <one-line description>` in Claude Code from the fork. This skill produces:
   - Recommended Linear workspace blueprint (which optional projects to enable)
   - Recommended initial `CLAUDE.md` content
   - Recommended initial `README.md` content
   - Recommended initial label taxonomy
   - A bootstrap checklist
4. **Create** the Linear workspace per the recommendation (manually — Linear does not have a "create workspace from blueprint" API; the skill outputs a checklist).
5. **Connect** Linear MCP (Claude.ai + Claude Code) and GitHub MCP (Claude Code only) per `docs/03` and `docs/04`.
6. **Paste** the recommended `00_PROJECT_INSTRUCTIONS.md` into the Claude.ai project Settings.
7. **Verify** with `./scripts/verify_setup.sh`.
8. **Start working.**

Target: 60 minutes for a competent founder. 30 minutes if they already use Claude Code.

---

## Open structural questions (forward-referenced in `10_open_questions_for_founder.md`)

- Should `/case_studies/` ship with v0.1 or be deferred to v0.2?
- Should examples be in this repo or in a sibling repo (`solo-claude-stack-examples`)?
- Should there be a `quickstart.sh` script that automates parts of the bootstrap (clones, prompts, sets up `.env`)?
