# 10 — Open Questions for the Founder

> **Pre-v0.1 design history.** Migrated from the Claude.ai meta-project KB on 2026-05-11. References to the old working name `solo-claude-stack` are intentionally preserved as historical record; the current working name is `Solo-Setup` (SOL-1). User-facing v0.1 docs will live in `docs/` (numbered 00–13) and will be drafted *from* these design notes during weeks 2–4.

This file enumerates the decisions blocking the drafting of public docs. Each is named, scoped, given a recommendation, and given a deadline relative to the v0.1 ship target.

The deadlines are tight on purpose. Indecision on these questions is the single most likely cause of v0.1 slipping. The kill criterion from `00_PROJECT_INSTRUCTIONS.md` applies: if more than three of these are unresolved by end of week 1, the project drops to v0.0 README-only scope.

Format for each question: **Q-NNN — short title**, then `Context`, `Options`, `Recommendation`, `Deadline`, `Blocks`.

---

## Q-001 — Final project name

**Context.** The working name `solo-claude-stack` is descriptive but has three weaknesses: (1) it ties the project to Claude specifically, foreclosing future model-agnostic positioning; (2) "stack" is overused in this space; (3) it does not communicate the GSD / opinionated-workflow angle. The name appears in repo URL, README headline, every doc, every skill description, and any external write-up.

**Options.**
- A. Keep `solo-claude-stack`. Descriptive, boring, safe.
- B. Adopt a more evocative name (`vibestack`, `solodev`, `claudeflow`, `shipkit`). Higher upside, naming risk.
- C. Use a neutral noun-phrase (`solo-builder-workflow`, `claude-code-workflow`). Boring but searchable.
- D. Defer naming until first external user lands; ship v0.1 under working name, rename at v1.0.

**Recommendation.** Option D. Naming is a high-context decision that improves with usage data. v0.1 is for the founder; the name does not matter yet. The rename cost at v1.0 is one `git mv`, a redirect, and a README update — small. Premature naming locks in a name selected without the information that matters.

**Deadline.** End of week 4 (v0.1 ship). Until then, every doc references the working name and includes a footer note that the name is provisional.

**Blocks.** README headline, repo URL choice, package name (if any), social handles (if any).

---

## Q-002 — License: MIT vs Apache-2.0

**Context.** The repo will be public and intended for derivative use. Solo founders adopting the workflow will fork or template-copy it. Some will commercialize derivatives. The license choice signals the project's stance on patent grants, attribution, and trademark.

**Options.**
- A. MIT. Permissive, ubiquitous, minimal. No explicit patent grant.
- B. Apache-2.0. Permissive, includes explicit patent grant and contributor license terms. Slightly heavier on attribution.
- C. CC-BY-4.0 for docs + MIT for code (dual license). Cleanest semantically — most of the repo is docs.
- D. Custom or non-standard. Strongly disrecommended; deters adoption.

**Recommendation.** Option B (Apache-2.0). Reasoning: (1) the repo includes opinionated skills and templates that are non-trivial creative output; the patent grant matters more than for typical small-utility MIT projects. (2) Apache-2.0 is the default in the EU AI ecosystem the founder is operating in; it signals seriousness. (3) The CC-BY split (option C) is more correct semantically but adds licensing complexity that deters adoption.

**Deadline.** Week 1. Required before any code is committed to the public repo. Wrong license at commit time is annoying to retroactively change (requires CLA from every later contributor).

**Blocks.** Repo creation, `LICENSE` file, every SKILL.md license header, README.

---

## Q-003 — Case studies in v0.1 or v0.2

**Context.** File 04 reserves `case_studies/` in the target structure. The strongest case study would be SDG itself, retroactively documented. A second strong case study would be the meta-project (this very project) documenting its own bootstrap. Drafting case studies is ~6h each.

**Options.**
- A. Both case studies in v0.1 (SDG retroactive + meta-project self-documentation). Strongest demonstration; ~12h of writing.
- B. Self-documentation only in v0.1; SDG case study in v0.2. Lighter; ~4h of writing.
- C. No case studies in v0.1; both deferred to v0.2. Lightest; v0.1 ships as workflow docs only.
- D. Case studies as a separate sibling repo (`solo-claude-stack-cases`).

**Recommendation.** Option B. The meta-project's own bootstrap is the most credible evidence the workflow works — it is happening live, with all artifacts already in place (this very file, the design files 00–09, the eventual repo). It is also the cheapest to write because the artifacts already exist. SDG retroactive is more impressive but more expensive and the artifacts are scattered. Defer it.

**Deadline.** Week 2. Affects the v0.1 docs scope and the draft sequencing for weeks 3–4.

**Blocks.** v0.1 scope cut, `case_studies/` directory inclusion, the worked-example references in files 05/06/08/09.

---

## Q-004 — Examples in the same repo or sibling

**Context.** File 04 lists three worked examples in `/examples/`. Each example is a small project bootstrapped using the workflow, showing the full chain end-to-end. Examples can be large (each ~50 MB of artifacts) and version awkwardly.

**Options.**
- A. Same repo, `/examples/<name>/`. Simplest discovery, heaviest repo.
- B. Sibling repos, linked from main README (`solo-claude-stack-example-pdf-extractor`, etc.). Cleanest separation, harder discovery.
- C. Same repo but with worked examples as text-only walkthroughs (no full project trees). Lightest, less convincing.
- D. Examples live in GitHub Discussions or external blog posts.

**Recommendation.** Option C for v0.1, Option A for v0.2+. Reasoning: a solo founder evaluating the workflow does not clone the examples; they read them. Text walkthroughs in `/examples/<name>.md` carry 90% of the value at 10% of the maintenance cost. Full project trees can be added later in v0.2 if there is signal that users want them.

**Deadline.** Week 1 (affects file 04 update). The current file 04 wording lists three full-project examples; if option C is chosen, the language in file 04 needs amending before week 2 drafting begins.

**Blocks.** File 04 amendment, `/examples/` directory scaffolding, weeks 3–4 drafting sequence.

---

## Q-005 — `quickstart.sh` automation extent

**Context.** The quickstart promise in `00_PROJECT_INSTRUCTIONS.md` is "60 minutes from `git clone` to first session prompt". Achieving this requires automation of (a) prerequisites check, (b) spec-kit install via `uv`, (c) Ralph plugin install, (d) Linear workspace template apply, (e) `CLAUDE.md` generation from prompts. Each automated step is a potential failure point and a maintenance burden.

**Options.**
- A. Full automation. Single `bash quickstart.sh` runs all five steps. Highest user value, highest fragility (breaks when any upstream tool changes).
- B. Partial automation. Script handles (a)–(c) (deterministic installs); (d)–(e) become guided manual checklists.
- C. Minimal automation. Script only does (a). Everything else is checklist-driven.
- D. No script. Pure documentation walkthrough.

**Recommendation.** Option B. The deterministic installs (uv, spec-kit, Ralph) are the most error-prone for new users and benefit most from automation. Linear workspace setup and `CLAUDE.md` generation are inherently project-specific and benefit from the founder being prompted through them by the `project-bootstrap` skill rather than scripted.

**Deadline.** Week 2. Affects the `project-bootstrap` skill design (file 05, currently sketched as monolithic — see Q-007) and the `scripts/` directory contents (file 04).

**Blocks.** `project-bootstrap` skill final design, `scripts/quickstart.sh` shape, README "Getting Started" section length.

---

## Q-006 — Ship `speckit-runner` and `ralph-task-shaper` in v0.1?

**Context.** Both skills are listed in file 05's baseline 12. Both wrap external tools (spec-kit and the Ralph plugin) that have their own documentation. There is a real question whether thin wrappers add value, or whether v0.1 should ship with documentation pointing at the upstream tools and add the wrapper skills in v0.2 once friction patterns are observed.

**Options.**
- A. Ship both in v0.1 as currently sketched. Highest opinionation, most surface for breakage.
- B. Ship `speckit-runner` only; defer `ralph-task-shaper`. Spec-kit is core to the chain; Ralph is optional and well-documented.
- C. Defer both to v0.2. v0.1 ships with chapter docs that walk the founder through the upstream tools manually.
- D. Ship both as `experimental/` skills with explicit warnings.

**Recommendation.** Option B. The spec-kit chain is the structural backbone (DD-009) and benefits from a skill that enforces order, prerequisite checks, and the four-hat wedge — none of which spec-kit itself does. Ralph is a single-command tool with great upstream docs; a wrapper skill would mostly duplicate documentation. If founders report Ralph friction in v0.1 usage, add the wrapper in v0.2.

**Deadline.** Week 2. Affects file 05 final skill count (12 → 11 if Option B), file 06's automation flow examples, and the v0.1 skills directory shape.

**Blocks.** File 05 final scope, file 06 finalization, `.claude/skills/` directory contents in v0.1.

---

## Q-007 — `project-bootstrap` skill: monolithic or split?

**Context.** File 05 currently sketches `project-bootstrap` as one skill that handles repo init, Linear workspace template, CLAUDE.md generation, and the goal/discovery one-pager kickoff. Skills perform better when they have a single clear purpose; a skill that tries to do four things often gets triggered for wrong reasons or fails partway.

**Options.**
- A. Keep monolithic. One skill, one invocation, full bootstrap.
- B. Split into three: `repo-bootstrap` (init + CLAUDE.md), `linear-structurer` (already separate in file 05), `goal-setter`+`discovery-runner` (also separate in file 09). Then `project-bootstrap` is removed and the README sequences the three.
- C. Keep `project-bootstrap` as an orchestrator skill that *invokes* the three sub-skills in sequence. Higher complexity, but preserves single-entry-point UX.
- D. Eliminate `project-bootstrap` entirely; rely on quickstart docs + the sub-skills.

**Recommendation.** Option B. The skill catalog already has `linear-structurer`, `goal-setter`, and `discovery-runner` as separate skills (files 05 and 09). Keeping `project-bootstrap` as a fourth monolithic skill is redundant. The README handles sequencing; this is exactly the README's job. Option C (orchestrator) is tempting but skills-invoking-skills is a fragile pattern in Claude Code as of the version current at v0.1 ship.

**Deadline.** Week 2. Affects file 05 skill count and design.

**Blocks.** File 05 final scope, README "Getting Started" sequencing.

---

## Q-008 — Is `token-budget-preflight` worth the complexity?

**Context.** File 05 sketches `token-budget-preflight` as a skill that estimates session token cost before invocation. As of Claude 4.5+ (the model series in scope for v0.1), Claude Code has built-in context awareness and warns when context utilization is high. The preflight skill duplicates ~70% of this functionality.

**Options.**
- A. Ship the skill. Provides explicit pre-session estimate, useful for planning multi-session features.
- B. Drop the skill. Rely on Claude Code's built-in awareness + the 100k/200k discipline in file 07.
- C. Reduce to a one-page checklist in `docs/13_session_discipline.md`, no skill.
- D. Ship as a `scripts/` shell utility instead of a skill (uses `tiktoken` or similar to count tokens in the session prompt + referenced files).

**Recommendation.** Option D. The skill format is overkill for what is essentially a "count tokens in these files" utility. A shell script (`scripts/token_estimate.sh`) that takes a session prompt path and emits an estimate is more honest about what the tool does, has zero skill-discovery overhead, and integrates cleanly with the existing `make check` pattern. The 100k/200k discipline (DD-008) is enforced by the founder, not by tooling — the tooling just informs.

**Deadline.** Week 2. Affects file 05 skill count (12 → 10 if Options B/C/D, → 11 if A) and `scripts/` directory contents.

**Blocks.** File 05 final scope, file 07 session prompt template (currently references the preflight skill).

---

## Q-009 — Separate Linear workspace for the meta-project itself?

**Context.** The meta-project (this project) is itself a project that the workflow describes. The SDG project uses Linear as its primary doc/issue store. The meta-project could either (a) reuse the SDG Linear workspace with a different team prefix, (b) create its own Linear workspace, or (c) not use Linear at all and rely on the public repo's own issues.

**Options.**
- A. Reuse SDG Linear workspace, new team with prefix `SCS` (or whatever final name). Lowest setup cost, mixes contexts.
- B. New Linear workspace. Clean separation, full context isolation, slight setup cost (~30 min).
- C. No Linear; use GitHub Issues + Projects in the public repo. Most public-friendly, weakest doc store.
- D. Hybrid: GitHub Issues for the public-facing work, Linear for the founder's private strategy notes.

**Recommendation.** Option A for week 1, migrate to Option B if the project lasts beyond v0.1. Reasoning: setting up a new Linear workspace before knowing the project will survive is overhead. Reusing SDG's workspace with a clean team prefix is 5 minutes of work and gives the project a real home. The migration cost in 4 weeks (if the project ships) is ~30 minutes — small price for deferring an irreversible-feeling setup decision.

**Deadline.** Week 1. Affects where the design discussions, drafting tasks, and review findings live for the duration of the project.

**Blocks.** Where this very project's tracking lives, the canonical location for the v0.1 build log, the canonical location for the founder's notes during drafting.

---

## Q-010 — How loud about Anthropic's Ralph plugin?

**Context.** The Anthropic-distributed Ralph plugin (in `anthropics/claude-code` repo's plugin directory) is the recommended path for Ralph integration. Pointing at it is good (official, maintained); over-emphasizing it risks (a) tying v0.1 to a plugin that may evolve, (b) implying endorsement by Anthropic that does not exist.

**Options.**
- A. Make the Anthropic plugin the only documented path. Crisp story, future fragility.
- B. Document the Anthropic plugin as the recommended path, the Geoffrey Huntley original (ghuntley.com/ralph/) as the conceptual reference. Document both.
- C. Document only the Huntley pattern conceptually; let users find the plugin themselves.
- D. Build a custom Ralph wrapper that pins behavior; not recommended (DD-002, compose don't reinvent).

**Recommendation.** Option B. The Anthropic plugin is the production path; the Huntley write-up is the canonical conceptual explanation. Both serve different needs. Crediting Huntley is correct attribution — Ralph as a pattern predates the Anthropic plugin and the public docs should be clear about this lineage.

**Deadline.** Week 3. Affects file 06's automation flow documentation and the eventual `docs/14_automation_loops.md` chapter.

**Blocks.** Final wording in file 06 and downstream user-facing docs.

---

## Summary table

| # | Question | Recommendation | Deadline | Severity if unresolved |
|---|----------|----------------|----------|------------------------|
| Q-001 | Project name | Defer to v1.0 | W4 | Low |
| Q-002 | License | Apache-2.0 | W1 | **High** |
| Q-003 | Case studies | Self-only in v0.1 | W2 | Medium |
| Q-004 | Examples shape | Text walkthroughs in v0.1 | W1 | Medium |
| Q-005 | quickstart.sh | Partial automation | W2 | Medium |
| Q-006 | speckit/ralph wrappers | Ship speckit only | W2 | Medium |
| Q-007 | project-bootstrap split | Split (drop monolithic) | W2 | Low |
| Q-008 | token-budget-preflight | Shell script, not skill | W2 | Low |
| Q-009 | Meta-project Linear | Reuse SDG workspace, SCS team | W1 | Low |
| Q-010 | Ralph plugin emphasis | Both Anthropic + Huntley | W3 | Low |

Three questions are W1-deadline: Q-002 (license), Q-004 (examples shape), Q-009 (Linear setup). All three are cheap to resolve and unlock most downstream work.

---

## How to use this file

1. Read once front-to-back. Mark a `[ACCEPT]`, `[REJECT-RECOMMENDATION, CHOOSE: X]`, or `[NEED-MORE-INFO]` next to each.
2. For each `[ACCEPT]`, propagate the decision into the relevant design files (mostly 03, 04, 05) by amending the corresponding DD or table.
3. For each `[REJECT]`, write the chosen option's rationale inline. The amendment to downstream files follows the chosen option, not the recommendation.
4. For each `[NEED-MORE-INFO]`, name what information would resolve it and a date by which to gather it. Carry the open question into the week 1 Build Log entry.
5. Commit this file with markers in place. It becomes the v0.0 design record — the artifact future-self will use to remember why the v0.1 docs look the way they do.

The file remains in the repo through v0.1. At v0.1 ship, mark each entry resolved with a one-line outcome statement. Unresolved entries become v0.2 inputs.
