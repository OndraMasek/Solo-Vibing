# 08 — Review and QA Design

> **Pre-v0.1 design history.** Migrated from the Claude.ai meta-project KB on 2026-05-11. References to the old working name `solo-claude-stack` are intentionally preserved as historical record; the current working name is `Solo-Setup` (SOL-1). User-facing v0.1 docs will live in `docs/` (numbered 00–13) and will be drafted *from* these design notes during weeks 2–4.

**File purpose:** Layered review process spanning spec-phase (four-hat adversarial), code-phase (pre-PR review, optional dual-model), and ship-phase (release readiness check).
**Last updated:** 2026-05-11

---

## The three layers

| Layer | When it fires | What it checks | Cost | Optional? |
|---|---|---|---|---|
| **Spec-phase: four-hat adversarial review** | After `/speckit.clarify`, before `/speckit.plan` | Spec correctness, kill-or-go, lock-in risk | ~30–60 min chat-Claude | Mandatory for non-trivial features |
| **Code-phase: single-Claude pre-PR review** | Before merging any PR | Code quality, security, test coverage, spec adherence | ~5–10 min code-Claude | Mandatory |
| **Code-phase: dual-model code review** | Before merging high-stakes PRs | Same as above + blind-spot catching | ~10–20 min + OpenAI API cost | Optional, opt-in |
| **Ship-phase: release readiness review** | Before tagging a release | Docs match code, breaking changes flagged, security review | ~30 min chat-Claude | Mandatory for v0.1+, optional for early releases |
| **Run-phase: calibration-first eval** | When introducing any LLM-as-judge | Eval alignment with founder eye | 3–5 dense-feedback cycles | Mandatory before trusting any LLM eval |

This design covers all five.

---

## Layer 1: Spec-phase four-hat adversarial review

**Owned by:** chat-Claude (in the Claude.ai project).
**Inputs:** a spec or major decision that has reached "ready to plan" state.
**Outputs:** a Linear Document titled `<spec> — Adversarial Review v<N>` + an updated `Review status:` field on the spec.

### The protocol document

Lives at `templates/reviews/adversarial_review_protocol.md` in the public repo. Mirrored to each project's Linear as a Standing Protocol document.

The protocol defines:
- Triggers (when chat-Claude proposes the review)
- The four hats (skeptic, implementation, external, future-self) — with hat prompt files
- Severity / effort / lock-in rubric
- Conflict-resolution heuristic
- Output format
- Out-of-scope fencing rules (against locked decisions)

### The four hats — concrete prompts

Each hat is a separate chat-Claude message with a hat-specific system-prompt-equivalent. The hat prompts live at `templates/reviews/hat_<N>_<name>.md`.

#### Hat 1 — Skeptic / kill-or-go

> Reviewing `<spec name>`. You are the skeptical reviewer. Your job is to identify findings that, if true, would kill the project or the feature.
>
> For each finding, output: ID, severity (blocker / high / medium / low), effort to address, lock-in (does fixing this require revisiting a locked decision?), the finding, recommended action.
>
> Areas to probe: assumptions that are stated as fact but not verified, scope creep relative to stated goal, undocumented dependencies on external systems or teams, regulatory or legal exposure, missing alternatives consideration, sunk-cost reasoning.
>
> Out-of-scope: locked decisions DD-NNN and DD-NNN (list per project). Findings that would revisit these become `Open questions for founder`, not findings.

#### Hat 2 — Implementation reviewer

> Reviewing `<spec name>`. You are the implementation reviewer. Your job is to identify findings that affect buildability within the stated timebox and stack.
>
> For each finding, output: ID, severity, effort to address, lock-in, the finding, recommended action.
>
> Areas to probe: testability of each acceptance criterion, library/framework risk (immature, recently changed, license issues), data flow gaps, performance characteristics, infrastructure prerequisites, time-budget realism, missing or implicit dependencies between tasks.

#### Hat 3 — External reviewer

> Reviewing `<spec name>`. You are the external reviewer — a competent member of the target audience (be specific per project: a senior engineer at the target company, a customer in the target persona, an open-source maintainer in the adjacent ecosystem).
>
> For each finding, output: ID, severity, effort, lock-in, the finding, recommended action.
>
> Areas to probe: would the target user adopt this as-is? what objections do they raise? where do the docs / UX assume too much? what trust signals are missing? what alternatives would they compare this to?

#### Hat 4 — Future-self reviewer

> Reviewing `<spec name>`. You are the six-month-future founder looking back at this decision.
>
> For each finding, output: ID, severity, effort, lock-in, the finding, recommended action.
>
> Areas to probe: what surprised future-self? what was the most expensive learning? what would future-self have done differently with present-self's information? what optionality was preserved or destroyed by this spec?

### Synthesis

After the four hats, one synthesis message:

```
# Synthesis: <spec name>

## Top 3 findings to address before /speckit.plan
1. <finding ID> — <one-line summary>. Owner: founder. Action: <action>.
2. ...
3. ...

## Findings deferred to `Open questions for founder`
- <finding ID> — <reason for deferral>

## Findings dismissed
- <finding ID> — <reason for dismissal>

## Updated `Review status:` for the spec doc
Adversarial review v<N> complete. <N> top findings addressed; <M> deferred; <P> dismissed.
```

### When to run a v2 review

After significant spec revisions (>30% of the spec text changes). The same protocol applies; the title increments to `v2`.

### Out-of-scope fencing

Critical: locked strategic decisions (DD-NNN, ADR-NNN, the wedge framing, current timeboxes, pinned stack choices) are explicitly out of scope. The four hats do not re-litigate them.

Findings that genuinely depend on revisiting a locked decision become `Open questions for founder`, not findings. The founder decides whether to revisit the locked decision (a meta-decision the four-hat review does not own).

---

## Layer 2: Code-phase pre-PR review

**Owned by:** Code-Claude (in the same Claude Code session as the PR-ready commit).
**Inputs:** the final commit on the feature branch.
**Outputs:** a review comment posted to the PR (or to the relevant Linear issue if no PR), plus a go/no-go merge recommendation.

### The review prompt

Lives at `templates/reviews/pre_pr_review_prompt.md`. Founder invokes by typing `Run pre-PR review on this branch.`

The review covers:
- **Spec adherence.** Does the diff implement the acceptance criteria? Mark each criterion as met / partially met / missing.
- **Test coverage.** Are there tests for each acceptance criterion? Any code paths without tests?
- **Code quality.** Naming, function length, dead code, premature optimization.
- **Security.** Hard-coded secrets, unsafe string handling, SQL injection vectors, dependency vulnerabilities (use `npm audit` / `pip-audit` if available).
- **Type safety / linting.** `make check` already passed; this catches style/clarity issues lint misses.
- **Documentation.** Are exported APIs documented? Did `CLAUDE.md` need updates?
- **Performance characteristics.** Anything obviously O(n²) in a hot path? Memory leaks?
- **Regression risk.** Did this touch any code path that's known-fragile per past ADRs?

### Output format

```
# Pre-PR review — <branch / commit hash>

## Spec adherence
- AC 1: met / partial / missing — <evidence: commit hash + test name>
- ...

## Findings (severity-ordered)
1. [blocker] <finding> — file:line — <recommended action>
2. [high] ...
3. [medium] ...

## Merge recommendation
GO / GO with fix-ups / NO-GO

## Required follow-ups (if GO with fix-ups)
- ...
```

If blocker-class findings → NO-GO. Fix and re-review.
If high-class findings only → GO with fix-ups (fix in this PR before merge or file follow-up issues).
If medium / low only → GO.

---

## Layer 3: Optional dual-model code review

**Owned by:** founder, invoked via a `scripts/dual_review.sh` script.
**Inputs:** the same final commit + the pre-PR review output.
**Outputs:** a second review from a different model (typically OpenAI's gpt-4.1 or similar), compared against Claude's review.

### When to use it

- Commercial code paths
- Customer-data handling
- Regulatory-relevant code
- Code that interacts with external APIs in non-trivial ways
- Cryptographic or signing logic
- Dependency pin changes (the SDG worked example: Albumentations 2.0.8 → 2.0.9 silent AGPL switch)

### When to skip it

- Documentation-only changes
- Trivial bug fixes
- Internal-only tooling
- Prototype branches

### The data-residency caveat (from SDG D-013 amendment)

If the founder's project has data-residency requirements (EU residency, customer-data residency), routing code through OpenAI's API may violate those requirements. The SDG D-013 amendment identified two paths:
- Route OpenAI calls through an EU-resident proxy
- Limit dual-model review to non-customer code paths only

This stack documents both paths and recommends the second for solo founders (operationally simpler).

### Reconciling Claude vs other-model findings

If both agree → trust the finding.
If only Claude raises a finding → trust it (Claude has the full session context).
If only other-model raises a finding → investigate; this is the blind-spot catch.
If they conflict → manual founder judgment.

---

## Layer 4: Release readiness review

**Owned by:** chat-Claude.
**When it fires:** before tagging any public release (v0.1, v0.2, etc.) in the public repo.
**Outputs:** a release readiness checklist filled in + a go/no-go decision.

### The checklist (lives at `templates/reviews/release_readiness_checklist.md`)

- All docs in `docs/00` through `docs/13` are present and reviewed
- README's quickstart works (verified by founder eye-test or external reviewer)
- All skills in `.claude/skills/` have descriptive frontmatter and a body
- All templates in `templates/` have at least one example use
- `CHANGELOG.md` has an entry for this version
- `LICENSE` is present and matches `package.json`/`pyproject.toml`/equivalent if present
- No domain-specific SDG content has leaked into public docs
- No customer or prospect names appear anywhere
- Four-hat review status on the four most important docs (README, `01_philosophy`, `02_tool_architecture`, `07_session_workflow`) is `complete`
- No `TODO` or `FIXME` comments in public docs
- `verify_setup.sh` script runs cleanly on a fresh clone

If any item fails → NO-GO. Fix and re-check.

---

## Layer 5: Calibration-first evals (when introducing any LLM-as-judge)

**Pattern from SDG (Pattern 10 in `02_source_workflow_distilled.md`).**

Whenever this stack introduces any LLM evaluator (e.g. a scoring skill, a rubric-based reviewer, an auto-grader for generated content), apply the calibration-first protocol:

1. **Dense feedback cycles:** for 3–5 cycles, the founder reviews the same items the evaluator scores. Outputs are compared.
2. **Alignment computation:** Spearman correlation or simple agreement-rate.
3. **Graduated trust:** only after alignment is acceptable does the evaluator get autonomous use.
4. **Periodic recalibration:** monthly spot-check the evaluator against fresh founder eye.

For this stack specifically:
- The `adversarial-reviewer` skill IS an LLM-as-judge. Founders are advised to run 3–5 dense-feedback adversarial reviews on early specs and compare hat findings to their own concerns before trusting the four-hat review autonomously.
- Future skills that score outputs (e.g. a hypothetical `code-quality-scorer`) inherit the calibration protocol.

The `docs/10_review_qa.md` user-facing doc covers this. The protocol template lives at `templates/reviews/calibration_protocol.md`.

---

## How the layers compose: a worked example

**Scenario:** founder ships a new feature, "multi-tenant support", to the project.

1. **Spec phase.** `/speckit.specify`, `/speckit.clarify`, then four-hat adversarial review (Layer 1). Hat 1 (skeptic) flags: "no migration plan for existing single-tenant users." Hat 2 (implementation) flags: "row-level security in the database needs a separate spec." Synthesis: address both before plan; one in this spec, one as a separate spec.

2. **Plan + tasks + implement.** Per `06_automation_loop_design.md`.

3. **Pre-PR.** Code-Claude in the final session runs Layer 2. Finds: AC 4 (audit log) has no test for the rollback path. NO-GO. Founder adds the test in a follow-up commit. Re-review. GO.

4. **Dual-model (optional, this case yes).** Commercial code, customer-data handling. `scripts/dual_review.sh` runs. OpenAI catches a hard-coded admin email in a default config. Claude missed it because of where it was in a large config block. Founder fixes, re-runs, both clean.

5. **Merge.** PR merged. Build Log updated. Sync Queue updated.

6. **Release readiness (later).** When v1.2 is tagged for the founder's project, the release readiness checklist is run.

**Total review time across the feature: ~2 hours.** Distributed across the feature's 4 working days, this is ~30 min/day average. Acceptable for a solo founder.

---

## What the review layers do NOT do

- They do NOT replace founder judgment. The hats produce findings; the founder decides what to act on. The reviewer makes recommendations; the founder approves merges.
- They do NOT execute fixes. They surface findings; subsequent sessions (TDD cycles) address them.
- They do NOT cross-check each other automatically. The founder runs the appropriate layer for the work in front of them. No nested review-of-reviews.

---

## Anti-patterns to call out in the public docs

- **Reviewer-as-implementer.** Letting the same Claude session that reviewed the PR also fix the findings → context entanglement, missed issues. Spin a fresh session for fixes.
- **Reviewing your own session output without an eye-test first.** Always founder eye-test before invoking the reviewer (per GSD pattern G6).
- **Adversarial review on every spec, including trivial ones.** Over-ceremony. The protocol explicitly defines triggers; bug fixes and one-file changes do not trigger.
- **Skipping the calibration cycles for a new evaluator.** Trusting the eval before validating its alignment with the founder eye produces silent drift.
- **Treating reviewer findings as orders.** Findings are advisory. The founder rejects findings (with rationale) routinely. The "dismissed" section in the synthesis is for this.

---

## Forward references

- The hat prompt files: `templates/reviews/hat_<N>_<name>.md` (to be drafted in week 2).
- The release readiness checklist: `templates/reviews/release_readiness_checklist.md` (to be drafted in week 3).
- The calibration protocol: `templates/reviews/calibration_protocol.md` (to be drafted in week 3).
- The user-facing docs: `docs/10_review_qa.md` (to be drafted in week 2).
