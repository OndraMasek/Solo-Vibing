# 06 — Automation Loop Design

> **Pre-v0.1 design history.** Migrated from the Claude.ai meta-project KB on 2026-05-11. References to the old working name `solo-claude-stack` are intentionally preserved as historical record; the current working name is `Solo-Setup` (SOL-1). User-facing v0.1 docs will live in `docs/` (numbered 00–13) and will be drafted *from* these design notes during weeks 2–4.

**File purpose:** Design how Ralph Wiggum (autonomous iteration loops), GitHub spec-kit (spec-driven development chain), and Get-Shit-Done patterns compose in this stack.
**Last updated:** 2026-05-11

---

## The mental model: three orthogonal axes

These three patterns are often described as if they compete. They do not. They cover different axes:

| Axis | Spec-kit | Ralph Wiggum | GSD patterns |
|---|---|---|---|
| **What it owns** | Structure of the work | Execution mode for bounded tasks | Friction reduction across the day |
| **When it fires** | At the start of any non-trivial feature | When the task is bounded + testable + repetitive | Continuously, in small operational moments |
| **Risk** | Over-ceremony | Runaway loops, credential exposure | Skipping the spec phase when you shouldn't |
| **Sweet spot** | Greenfield features, legacy modernization | Bulk refactors, test coverage, doc generation, migrations | Daily standup-equivalent tasks, build-log writing, status comments |

The stack uses all three. Each fires at the right phase of work. None replaces the others.

---

## The composed flow

For any non-trivial feature:

```
1. GSD: founder picks the feature from the backlog (5 min)
       → goal-setting + discovery template completed
2. SPEC-KIT: /speckit.specify
3. SPEC-KIT: /speckit.clarify
4. FOUR-HAT REVIEW: human-in-the-loop wedge (this stack's addition)
5. SPEC-KIT: /speckit.plan
6. SPEC-KIT: /speckit.tasks --tdd
7. SPEC-KIT: /speckit.analyze
8. Decision point: "are these tasks Ralph-shaped?"
   - If yes → wrap /speckit.implement in a /ralph-loop
   - If no  → manual TDD sessions per task
9. TDD session loop (red → green → refactor → commit)
10. Code review (pre-PR Claude review, optional dual-model)
11. Merge
12. GSD: build-log entry on Friday
13. GSD: sync queue resolution at next session start
```

For a trivial change (bug fix, doc edit, one-file refactor):

```
1. GSD: founder describes the change in chat-Claude (1 min)
2. Manual session: skip steps 2–7, go straight to TDD (write failing test reproducing the bug → fix → commit → PR)
3. GSD: build-log entry on Friday includes this in "What landed"
```

For bulk repetitive work (mass refactor, coverage filling, doc gen):

```
1. GSD: founder describes the bulk task in chat-Claude
2. SPEC-KIT: /speckit.specify is often skipped for true bulk work (the criteria are mechanical)
3. RALPH-TASK-SHAPER skill: shape the prompt with completion criteria
4. RALPH: /ralph-loop "<task>" --max-iterations <N> --completion-promise "<phrase>"
5. Founder eye-test on the first 2–3 iterations
6. Let Ralph run (in a sandbox per ghuntley.com/ralph/ — security boundary)
7. Founder reviews final state, merges
8. GSD: build-log entry
```

---

## Spec-kit integration

### Installation (per repo)

```bash
# Once per project repo
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
cd <your-project>
specify init . --integration claude --integration-options="--skills"
```

The `--skills` flag installs spec-kit commands as Claude Code skills rather than slash commands, which composes better with the other skills in this stack.

### Constitution (once per project)

`/speckit.constitution` runs once at project start. The output lives in `specs/<project-name>/constitution.md` per spec-kit convention. **This stack mirrors the constitution to the Linear Strategy project as a Linear Document titled "Constitution".** The Sync Queue keeps them aligned.

The constitution is filled with stack-specific defaults from `project-bootstrap`:
- TDD mandatory
- Token-budget pre-flight required
- Four-hat review wedge between `/clarify` and `/plan`
- `make check` required at session end
- Strategic ADRs to Linear + repo; build-time ADRs to repo only

### Per-feature flow

`/speckit.specify "<feature>"` produces `specs/NNN-<slug>/spec.md`. This stack adds:
- A new Linear issue in the Spec project pointing to the file
- A Sync Queue entry to keep them aligned

`/speckit.plan` and `/speckit.tasks --tdd` produce the rest of the spec-kit artifacts. `/speckit.analyze` is run before `/speckit.implement`.

### Where the four-hat review fits

Between `/speckit.clarify` and `/speckit.plan`. The spec is now structured enough to attack adversarially but not yet committed to a technical implementation. This is the cheapest place to catch problems.

The `adversarial-reviewer` skill is invoked. Output is a Linear Document titled `<feature> — Adversarial Review v1` in the Spec project. The spec doc's `Review status:` header is updated.

### Where TDD fits

`/speckit.tasks --tdd` produces test-first task ordering. `/speckit.implement` walks through the tasks. The `tdd-cycle` skill enforces red → green → refactor per task.

---

## Ralph Wiggum integration

### When to use Ralph (the decision table)

Ralph fires when ALL of:
- The task is testable (clear pass/fail per iteration)
- The task is bounded (a defined "done" state)
- The work is mostly mechanical (no creative judgment per iteration)
- The cost of a bad attempt is recoverable (sandbox, branch, `git reset --hard`)

Examples:
- ✅ Migrate all `unittest` tests to `pytest`
- ✅ Add type hints to every public function in `src/`
- ✅ Generate one-page docs for every module in `src/`
- ✅ Fix all failing tests in `tests/integration/`
- ✅ Refactor every callsite of deprecated API X to use API Y
- ❌ Decide whether to pivot from invoices to receipts
- ❌ Draft the README for v0.1
- ❌ Write the customer outreach message
- ❌ Design the database schema (until the schema decision is made; then migration code is Ralph-shaped)

### The Ralph prompt structure

This stack uses the Anthropic plugin (`anthropics/claude-code/plugins/ralph-wiggum`). The `ralph-task-shaper` skill produces prompts in this shape:

```
/ralph-loop "<task description>

Requirements:
- <numbered, testable>

Success criteria:
- All affected tests passing
- No linter errors
- <other specific criteria>
- <how to verify completion>

If stuck after N iterations, write a STUCK.md explaining what was tried and what's blocking.
Output: <promise>COMPLETE</promise> when done." --max-iterations 30 --completion-promise "COMPLETE"
```

### Security boundary

Ralph requires `--dangerously-skip-permissions` to run autonomously. This bypasses Claude Code's per-tool permission system. Per `ghuntley.com/ralph/` and the Anthropic plugin README, the only safe mitigation is to run Ralph in a sandbox:
- **Local Docker container** with the project mounted and only the API keys needed for the task
- **Remote sandbox** (E2B, Fly Sprites, or similar)

This stack's `docs/11_automation_loops.md` documents the Docker option as the recommended path for solo founders. A `Dockerfile.ralph` template lives in `templates/github/repo_skeleton/`.

### The two prompts: PLANNING vs BUILDING

Per the deep-dive in `github.com/ghuntley/how-to-ralph-wiggum`, Ralph works best when split:
- **PLANNING prompt** does gap analysis (specs vs. code) and outputs a prioritized TODO. No implementation. No commits.
- **BUILDING prompt** assumes the plan exists, picks tasks, implements, tests, commits.

This stack adopts the split. `ralph-task-shaper` produces both prompts when the task is large. For small tasks (single TODO), the prompts merge.

### Memory between iterations

Ralph iterations are fresh-context. Persistence happens via:
- Git history (which Ralph reads at the start of each iteration via `git log`)
- A `progress.txt` or `STATE.md` file Ralph maintains
- Updated `AGENTS.md` or `CLAUDE.md` entries (Ralph appends learnings)

This stack standardizes on:
- `CLAUDE.md` for stable rules (Ralph reads but does not write)
- `RALPH_STATE.md` for per-loop state (Ralph reads and writes; gitignored or branch-local)
- Git history for completed work record (Ralph reads via `git log`)

### Cost discipline

A Ralph loop that runs unchecked can burn meaningful API tokens. The stack recommends:
- Always set `--max-iterations` (default 30; 50 only for known-large refactors)
- Use the Stop-hook completion gate (`--completion-promise`) — exact string matching, no fancy parsing
- Eye-test the first 2–3 iterations before walking away
- Run overnight only after the pattern is established on shorter loops

---

## GSD (Get-Shit-Done) patterns

GSD is the daily friction-reduction layer. It is not a specific tool; it is a set of patterns this stack documents:

### Pattern G1: Build log on Friday

The `build-log-writer` skill makes this a 5-minute Friday task. Removes the perpetual "what did I do this week?" friction.

### Pattern G2: Sync queue at session start

The `sync-queue-runner` skill is invoked at the start of every Claude Code session. Founders never manually copy between systems.

### Pattern G3: Status comment on every multi-session task

Per SDG-37 pattern: every Linear issue covering >1 Claude Code session gets a status comment at session end summarizing what landed, what's next, and the session prompt for the next session. Removes the "where was I?" friction.

### Pattern G4: Calendar block for chat-Claude sessions

The stack recommends two calendar blocks per week for chat-Claude strategic sessions: Monday morning (week planning, ~2 hours) and Friday afternoon (build log + reflection, ~1 hour). Removes the "when do I do strategy?" friction.

### Pattern G5: Mobile capture as the default for customer / discovery moments

Linear's mobile app for capturing customer call notes, outreach replies, random ideas. Removes the "I'll write it up later" friction (which always becomes "I forgot the details").

### Pattern G6: Eye-test before review

Every Claude Code session output gets a founder eye-test (open the files, look at the diff, run the code if visual) BEFORE invoking the reviewer skills. Removes the "review missed the obvious thing" friction.

### Pattern G7: One slash command per common action

Skills are exposed as slash commands where the action is repeated:
- `/sync-queue-runner` — at session start
- `/session-prompt` — when drafting handoff
- `/build-log-writer` — Friday
- `/adversarial-reviewer` — after a major spec lands

Founders type these instead of describing the task each time.

---

## How the three compose: a worked example

**Goal:** ship a new feature, "add multi-currency support" to a hypothetical invoice tool.

**Day 1, Monday morning (chat-Claude, ~1 hour).** GSD pattern G4 fires. Founder opens chat-Claude, says "Goal-set + discovery for multi-currency support." Chat-Claude walks through goal-setting and discovery templates. Output: a Linear Document `Goal — Multi-currency support`.

**Day 1, Monday afternoon (chat-Claude, ~1 hour).** Chat-Claude invokes `speckit-runner` skill. Runs `/speckit.specify "Add multi-currency support…"` and `/speckit.clarify`. Output: `specs/004-multi-currency/spec.md`. Linear issue + Sync Queue entry created.

**Day 1, evening (chat-Claude, ~30 min).** Chat-Claude invokes `adversarial-reviewer` skill. Four hats run. Top 3 findings: (1) decimal precision policy unspecified, (2) FX rate source unclear, (3) historical-rate persistence not addressed. Founder addresses findings → spec revised → `Review status:` updated.

**Day 2, Tuesday morning (chat-Claude, ~30 min).** Chat-Claude invokes `speckit-runner` again, runs `/speckit.plan`, `/speckit.tasks --tdd`, `/speckit.analyze`. Output: `plan.md`, `tasks.md` (TDD-ordered), `data-model.md`.

**Day 2, Tuesday afternoon (Claude Code, ~3 hours).** Code-Claude session 1. `sync-queue-runner` runs. `session-prompt` produces the opener. Founder invokes `ralph-task-shaper` on the bulk refactor sub-tasks ("update every Invoice model to include currency_code"). Shaper classifies it Ralph-shaped, produces a `/ralph-loop` prompt. Founder runs it in Docker sandbox. ~20 iterations later, the refactor is done; the founder reviews, merges. The remaining tasks (UI, settings page, persistence) are not Ralph-shaped — `tdd-cycle` skill drives them.

**Day 3, Wednesday afternoon (Claude Code, ~2 hours).** Code-Claude session 2. TDD cycle continues. `make check` green. Commit. PR opened. Single-Claude review fires automatically.

**Day 4, Thursday (Claude Code, ~1 hour).** Final TDD cycle. PR merged. Sync Queue updated.

**Day 5, Friday afternoon (chat-Claude, ~30 min).** `build-log-writer` skill produces the Build Log entry. Sync Queue updated.

**Total founder time: ~9 hours across 5 days.** No copy-paste between tools. Spec-kit provided the structure. Ralph handled the bulk refactor. GSD patterns kept friction down at every step.

---

## What this design does NOT include

- **No autonomous full-feature loops.** Even with Ralph + spec-kit, the human-in-the-loop wedge (four-hat review) is mandatory for non-trivial features. We do not endorse pipelines that ship code to users without explicit founder review of the spec.
- **No multi-agent orchestration (Gas Town, Loom, agent swarms).** Per DD-002, the stack composes existing primitives. Multi-agent orchestration is an emerging space (Steve Yegge's Gas Town, Geoffrey Huntley's Loom) — we recommend revisiting in v0.3 once the patterns stabilize.
- **No "evolutionary software" patterns.** Ralph loops that mutate prompts based on outcomes are out of scope for v0.1.

---

## Forward references

- The Ralph sandbox / Docker setup is in `docs/11_automation_loops.md` (to be drafted).
- The spec-kit installation flow is in `docs/06_claude_code_setup.md` (to be drafted).
- The exact session prompt templates are in `templates/specs/session_prompt_template.md` (to be drafted).
- Per-pattern skills (skill #10 `ralph-task-shaper`, skill #11 `speckit-runner`) are designed in `05_skills_catalog_design.md`.
