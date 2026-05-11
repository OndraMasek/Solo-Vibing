# 09 — Spec, Goal-Setting, and Discovery Design

> **Pre-v0.1 design history.** Migrated from the Claude.ai meta-project KB on 2026-05-11. References to the old working name `solo-claude-stack` are intentionally preserved as historical record; the current working name is `Solo-Setup` (SOL-1). User-facing v0.1 docs will live in `docs/` (numbered 00–13) and will be drafted *from* these design notes during weeks 2–4.

This file specifies how `solo-claude-stack` users move from a vague intention ("I want to build X") to an implementation-ready spec. It addresses **improvement #7** in the project scope.

It is paired with file `08_review_qa_design.md` — the four-hat review (Layer L1 in file 08) is wedged inside the chain defined here.

---

## Problem being solved

Solo founders skip discovery. The default failure mode is: open Claude Code, type "build me a synthetic invoice generator", get 2,000 lines of code, discover three days later that the wrong thing was built. The cost is not the wasted three days — it is that the founder no longer knows whether the spec was wrong, the implementation was wrong, or the goal was wrong.

The remedy in mature engineering orgs is heavyweight: PRDs, design docs, architecture review boards. None of that fits a 20-hour-per-week solo operator. The remedy here is **a structured chain that takes ~3 hours total and is enforced by skills**, not by discipline.

The chain has three properties the public docs must defend:

1. **It is gated.** You cannot skip from "I want to build X" to `/implement` without producing the artifacts the next stage requires. Skills refuse to run if their prerequisites are missing.
2. **It is incremental.** Each stage produces a one-page or short-document artifact. No 30-page PRDs.
3. **It is reversible.** Every stage explicitly invites going back. Discovery findings can invalidate the goal. Spec clarification can invalidate the discovery. Plan analysis can invalidate the spec. The founder is expected to go back; the chain makes it cheap.

---

## The chain: 13 steps

The backbone is the GitHub spec-kit chain (`/speckit.constitution` → `/specify` → `/clarify` → `/plan` → `/tasks` → `/analyze` → `/implement`), with four-hat review wedged in and discovery prepended. The full 13-step composed flow:

| # | Step | Artifact produced | Skill | Time | Gate |
|---|------|-------------------|-------|------|------|
| 1 | Goal one-pager | `goals/<goal-slug>.md` | `goal-setter` | 20 min | Founder signs off |
| 2 | Discovery one-pager | `discovery/<goal-slug>.md` | `discovery-runner` | 30 min | Findings dated; assumptions explicit |
| 3 | Goal revision (if 2 invalidates 1) | Updated `goals/<goal-slug>.md` | `goal-setter` | 10 min | Optional; loop back to 2 if major |
| 4 | `/speckit.constitution` | `.specify/memory/constitution.md` | `speckit-runner` | 15 min, once per project | Constitution committed |
| 5 | `/specify <feature>` | `specs/<NNN-feature>/spec.md` | `speckit-runner` | 20 min | Spec contains acceptance criteria |
| 6 | `/clarify` | Updates to `spec.md` (Q&A appended) | `speckit-runner` | 15 min | All ambiguities flagged or resolved |
| 7 | **Four-hat review of spec** | `reviews/<NNN-feature>/four_hat_synthesis.md` | `adversarial-reviewer` | 45 min | Synthesis committed; spec amended |
| 8 | `/plan` | `specs/<NNN-feature>/plan.md` | `speckit-runner` | 20 min | Plan references spec by section |
| 9 | `/tasks --tdd` | `specs/<NNN-feature>/tasks.md` | `speckit-runner` | 10 min | Every task has a test-first marker |
| 10 | `/analyze` | Updates to `plan.md` (risks appended) | `speckit-runner` | 10 min | High-risk items routed to ADR |
| 11 | Session prompt drafting | `sessions/<session-slug>.md` | `session-prompt` | 10 min | Token budget pre-flight passes |
| 12 | `/implement` (via Claude Code) | Code + tests + commits | `tdd-cycle` enforces | 2–4h per session | `make check` green |
| 13 | Post-merge review | PR review pass | `adversarial-reviewer` (single-Claude mode) | 20 min | Findings filed as issues |

Total pre-implementation time: ~3 hours. Total per-feature including implementation and review: ~5–8 hours of active work.

Steps 1–3 are **discovery** (new). Steps 4–10 are **spec** (spec-kit chain + four-hat wedge). Steps 11–13 are **execute** (covered in files 06 and 07). This file owns 1–10.

---

## Step 1 — Goal one-pager

**Skill: `goal-setter`**

The goal one-pager is the smallest unit that answers "why are we building this?" It is the document the founder reads at the start of every session to recalibrate.

Template (the skill emits this with placeholders):

```markdown
# Goal: <slug>

**Date opened:** YYYY-MM-DD
**Status:** active | paused | shipped | abandoned
**Time budget:** <hours> over <weeks>
**Linked Linear project:** <name or none>

## The one-line outcome

<One sentence. If you cannot, the goal is not ready.>

## Why now

<2–4 sentences. What changed externally or internally that makes this the right time. If "I just felt like it", say so honestly.>

## What success looks like in 30 days

<3–5 bullets, each observable. "X works" is not observable. "I can generate Y in <Z seconds on my laptop, reviewed by myself, no manual fixes" is observable.>

## What this is NOT

<2–4 bullets. Common adjacent goals you are explicitly NOT pursuing in this round. This is the most-skipped section and the one that prevents the most scope creep.>

## Known unknowns

<Bullet list. Things you know you do not know. Feed into discovery step.>

## Kill criteria

<2–3 bullets. Observable conditions under which you will abandon this goal. "If by week 3 I do not have X, I stop." Without this, projects rot for months.>
```

Length cap: **one page rendered**, roughly 400 words. The skill refuses to emit longer drafts.

The skill's eval (from file 05): given three SDG-style prompts, produces three goal pages that each fit on one screen, each have non-empty "What this is NOT" sections, and each have at least two kill criteria.

---

## Step 2 — Discovery one-pager

**Skill: `discovery-runner`**

Discovery is the step everyone skips. The reason they skip it: it feels like "research" and research has no clear endpoint. The remedy is to bound it explicitly: discovery has **five questions**, each answered in 2–5 sentences with at least one cited source or one explicit "I asked Claude and the answer was X, dated Y."

Template:

```markdown
# Discovery: <goal-slug>

**Date:** YYYY-MM-DD
**Goal:** <link to goal one-pager>
**Time spent:** <hours>

## Q1. What exists already that solves part of this?

<Cited list of existing tools, libraries, services, papers. For each, one sentence on why it does or does not fit. If you find a tool that fully solves the goal, stop and update the goal.>

## Q2. What is the hardest technical unknown?

<One specific thing. Not "AI is hard." Specific: "I do not know whether Augraphy's perspective transform supports the angle range needed for mobile-photo realism without artifacts." Include how you would test it cheaply.>

## Q3. What does the operating environment require?

<Compliance, residency, performance, integration, cost. For each that applies, one sentence. If none apply, say so explicitly. EU residency, HIPAA, SOC2, on-prem, mobile-only, offline — each is one line.>

## Q4. Who is the first user, and how do you reach them?

<One named person or one named segment. If "myself", say so — that is a valid answer. If a customer, name them and state the channel you will reach them through. No "developers" or "small businesses" — too vague.>

## Q5. What did you learn that changes the goal?

<This is the loopback. If Q1–Q4 invalidated something in the goal one-pager, name it here, and go update the goal. If nothing changed, write "no goal changes" — but write it deliberately.>
```

Length cap: one page rendered, ~500 words.

The discovery runner skill's job is to *prompt* the founder through the questions, not to answer them. It can use web search and project-knowledge search to populate Q1 with candidates. It cannot decide which candidates are good fits — that is judgment work.

---

## Step 3 — Goal revision

Mechanically trivial: re-open the goal one-pager, edit, re-commit. The chain treats this as a first-class step rather than a footnote because in practice ~40% of discoveries trigger a goal revision. If the docs do not name this step, founders feel they have "failed" when they revise, when in fact a discovery that does *not* trigger revision is suspicious (it suggests discovery was performative).

---

## Steps 4–6 — `/speckit.constitution`, `/specify`, `/clarify`

These wrap the GitHub spec-kit commands as-is. The `speckit-runner` skill's job is to:

1. Ensure spec-kit is installed (`uv tool install specify-cli` is offered by the skill if absent).
2. Ensure the chain is run in order; refuse `/specify` if no constitution exists, refuse `/clarify` if no spec exists.
3. Tag every artifact with the goal slug it traces back to.

The constitution is per-project, not per-feature. It is the place where the founder pins decisions like "Python 3.11", "no diffusion models", "EU residency", "Apache-2.0", "single-repo deliverable". It is roughly the project's equivalent of `CLAUDE.md` plus the strategy doc — and in fact the `speckit-runner` skill emits the constitution by composing the founder's existing CLAUDE.md plus strategy ADRs if they exist.

The `/clarify` step produces appended Q&A in `spec.md`. Each Q is the spec-kit's own ambiguity question; each A is the founder's answer. The skill enforces: every ambiguity must either have an A, or be marked `DEFERRED: <reason>`. A spec with un-marked ambiguities cannot proceed to step 7.

---

## Step 7 — Four-hat review (the wedge)

This is the most important addition to the spec-kit chain and the one differentiator most likely to be questioned in PRs to the public repo. The argument for keeping it:

Spec-kit's `/clarify` is **expansive** (asks "what did you miss?") but not **adversarial** (does not ask "what is wrong with what you wrote?"). The four-hat review supplies the adversarial pass, exactly once, after `/clarify` and before `/plan`. The placement matters: doing it before `/clarify` is premature (the spec is too vague to attack); doing it after `/plan` is too late (the plan has already locked in assumptions from the un-attacked spec).

The mechanics are fully covered in file 08 (Layer L1). The chain integration:

- The `adversarial-reviewer` skill in spec-review mode reads `specs/<NNN-feature>/spec.md` and produces `reviews/<NNN-feature>/four_hat_synthesis.md`.
- The synthesis classifies findings by severity × effort × lock-in (file 08 rubric).
- Severity ≥ 3 findings that are also lock-in ≥ 2 must be addressed in `spec.md` before step 8. Lower-severity findings are filed as Backlog issues.
- The spec is **amended in place** with a footer noting the review date and the findings IDs addressed. No new spec version is created.

Cost: ~45 minutes founder time for review + spec amendment. The skill itself runs in ~3 minutes; the time is in reading and deciding.

---

## Steps 8–10 — `/plan`, `/tasks --tdd`, `/analyze`

`/plan` consumes the (now amended) spec and produces the technical plan. The `speckit-runner` skill enforces: plan references spec by section number, not by paraphrase. If the plan paraphrases the spec, the skill flags it and asks for explicit references — paraphrase is the single highest-risk drift vector in this chain.

`/tasks --tdd` is the spec-kit task generator with the TDD flag. Every emitted task has a test-first marker (`[T]` prefix in the task list, per spec-kit convention). The `tdd-cycle` skill in file 05 enforces this at implementation time: a task without `[T]` cannot be picked up.

`/analyze` runs spec-kit's own risk analysis pass. Its findings append to `plan.md`. The chain rule: any finding rated `HIGH` by `/analyze` is routed to an ADR (per file 02 pattern), not silently accepted. The `adr-writer` skill picks up the routed findings and prompts the founder through ADR drafting before step 11.

---

## When to use the full 13-step chain vs. shortcuts

The full chain is the default for features that take more than one Claude Code session (~4h+ wall time) or touch architecture.

Shortcuts:

| Scope | Use | Steps used |
|-------|-----|------------|
| Bug fix, single file | Shortcut | 11–13 (session prompt → implement → review) |
| Small feature, single session | Mini-chain | 5, 8, 11–13 (spec → plan → execute) |
| Cross-cutting feature, multi-session | Full chain | 1–13 |
| New project bootstrap | Full chain + extras | 1–4, then `project-bootstrap` skill |
| Experiment / spike | Skip chain entirely | Free-form session, results documented in build log |

The `speckit-runner` skill asks the founder which scope at invocation and skips inapplicable steps. The full chain is offered as the default; the shortcut is offered with a one-line rationale prompt ("why is the full chain not needed here?") to prevent unconscious shortcut creep.

---

## Anti-patterns to call out in the public docs

- **Treating discovery as research.** Discovery has a one-page output and a 30-minute budget. If it takes longer, the questions were wrong; revise the questions, do not extend the time.
- **Skipping the loopback (step 3).** Founders who answer "no goal changes" on every discovery are not doing discovery; they are confirming. If every project has no loopback, the goal one-pager is too vague.
- **Treating the constitution as documentation.** The constitution is a *constraint*. It exists to tell future-Claude what NOT to do. A constitution that does not contain negative statements ("does NOT use diffusion models", "is NOT shipped as a service") is not constraining anything.
- **Letting the spec-kit chain produce paraphrase chains.** Spec → plan → tasks each have their own language by default. The skill enforces explicit references back to spec sections. Without this enforcement, the chain becomes telephone.
- **Running the four-hat review on bug fixes or trivial specs.** Over-ceremony. The chain shortcut table above is the protection; the docs must make it visible and prominent.
- **Producing more than one page per artifact.** The cap is enforced by skill, but founders will sometimes hand-edit past the cap. The docs call this out: longer is not better; longer is unread.

---

## Templates to ship in `templates/specs/`

- `goal_one_pager.md` — the template from step 1.
- `discovery_one_pager.md` — the template from step 2.
- `constitution_template.md` — composes from CLAUDE.md + strategy ADRs.
- `spec_template.md` — spec-kit default, lightly annotated.
- `plan_template.md` — spec-kit default, lightly annotated.
- `tasks_tdd_template.md` — spec-kit default with TDD marker examples.
- `four_hat_synthesis_template.md` — the template from file 08 L1.

All templates are one page. The annotations are inline as HTML comments so they render cleanly but stay visible in the source.

---

## Forward references

- The chain runner skill: `.claude/skills/speckit-runner/SKILL.md` (file 05).
- The discovery and goal skills: `.claude/skills/discovery-runner/SKILL.md`, `.claude/skills/goal-setter/SKILL.md` (file 05).
- The user-facing chapter: `docs/12_spec_and_discovery.md` (to be drafted in week 2).
- The case study showing the chain applied to SDG retroactively: `case_studies/sdg/chain_applied_retroactively.md` (week 3, contingent on DD-022 in file 10).

---

## What this design does NOT cover

- **Customer discovery in the GTM sense.** Q4 of the discovery one-pager is the founder-facing minimum; full customer-discovery process (Mom test, deep interviews, segmentation) is out of scope for v0.1. It is a candidate for v0.2 and may live in a separate `gtm/` directory if added (see DD-021 in file 10).
- **Cost modeling.** Whether the feature is economically worth building is the founder's call, informed by the goal one-pager's "time budget" field. No CAC/LTV templates ship in v0.1.
- **Roadmap planning across goals.** The chain operates within one goal at a time. Cross-goal sequencing is left to the founder + Linear. The `linear-structurer` skill (file 05) handles the workspace layout but does not prescribe sequencing.

These exclusions are deliberate. Scope discipline is the project's biggest risk (DD-015); spec-and-discovery is exactly the area where over-design would kill v0.1.
