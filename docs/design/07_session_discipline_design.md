# 07 — Session Discipline Design

> **Pre-v0.1 design history.** Migrated from the Claude.ai meta-project KB on 2026-05-11. References to the old working name `solo-claude-stack` are intentionally preserved as historical record; the current working name is `Solo-Setup` (SOL-1). User-facing v0.1 docs will live in `docs/` (numbered 00–13) and will be drafted *from* these design notes during weeks 2–4.

**File purpose:** Combined design for TDD-first build sessions, 100–200k token-budget discipline, and explicit handoff artifacts. Where SDG's session cadence and the new improvements meet.
**Last updated:** 2026-05-11

---

## The session lifecycle

Every Claude Code build session in this stack follows the same shape:

```
[pre-flight] → [goal lock] → [token-budget gate] → [TDD loop] → [session-end gate] → [handoff]
```

Each phase has explicit artifacts and explicit go/no-go decisions. The session prompt template (`templates/specs/session_prompt_template.md`) encodes the lifecycle.

---

## Phase 1 — Pre-flight (~5 minutes)

**Mandatory steps:**
1. Read `CLAUDE.md` at repo root (Claude Code does this automatically; verify it loaded by reading the date at the top).
2. Run `sync-queue-runner` skill. Process any `sync:pending` issues. Surface conflicts.
3. Read the Linear Spec doc relevant to this session. Link it in the session prompt for traceability.
4. Read last session's status comment (if this is a continuation).
5. Confirm there's no in-flight Ralph loop the founder forgot about.

**Pre-flight artifact:** a one-line confirmation in chat: "Pre-flight clean: synced N items, read spec <link>, no conflicts."

If any step fails:
- Sync conflict → resolve in chat before proceeding
- Spec not present → start in chat-Claude, not Code-Claude
- Previous session left work uncommitted → recover or `git reset --hard` (explicit founder decision)

---

## Phase 2 — Goal lock (~2 minutes)

The session opener template (drafted by `session-prompt` skill) has a `# Session goal` section.

**Rules for the goal:**
- One sentence
- Testable acceptance criteria (numbered list)
- Explicit out-of-scope (what we will NOT do in this session even if tempted)
- Estimated duration (optimistic + realistic)

**Goal-lock artifact:** the session opener message itself, pasted into the Claude Code terminal as the first user message.

If the goal cannot be expressed in one sentence with testable criteria, the session is not ready to start. Go back to chat-Claude and `/speckit.tasks` first.

---

## Phase 3 — Token-budget gate (~3 minutes)

The `token-budget-preflight` skill runs.

**Estimation:**
- Fixed overhead (CLAUDE.md, MCP schemas, system prompt): rough 20–40k for a typical setup.
- Per-file load: ~1k tokens per 200 LOC, plus headers and metadata.
- Spec docs to be referenced: ~1–5k each.
- Conversation overhead: ~30k for a typical hour-long session.

**Decision rule:**
- Estimated peak <100k → **GO**.
- Estimated peak 100–150k → **GO, /compact at 70%**. Plan the compaction point in the session prompt.
- Estimated peak >150k → **SPLIT.** Produce a multi-session plan. Each sub-session targets <100k.

**Token-budget artifact:** a line in the session prompt: "Estimated peak: NNk. Plan: GO / GO with compact at MM%/ SPLIT into N sessions."

**Note on Claude 4.5+ context awareness.** As of 2026, Sonnet 4.5+, Sonnet 4.6, Haiku 4.5, and Opus models have built-in context awareness (per `platform.claude.com/docs/en/build-with-claude/context-windows`). The model itself tracks remaining context and adjusts. This does NOT replace pre-flight estimation — pre-flight is the founder's decision tool ("should I do this now or split it?"), not the model's runtime adjustment. Keep both.

---

## Phase 4 — TDD loop (the bulk of the session)

For each acceptance criterion in the goal:

```
RED:
  1. Write the failing test for the next acceptance criterion
  2. Run the test
  3. Confirm it fails for the right reason (assertion mismatch, NOT import error or syntax error)

GREEN:
  4. Write the minimum code to make the test pass
  5. Run the full test suite (or affected module + integration tests)
  6. Confirm green

REFACTOR (optional, only if needed):
  7. Clean up. Run tests after each cleanup step.

COMMIT:
  8. Commit with Conventional Commits format: feat: / fix: / test: / refactor:
  9. Message names the acceptance criterion just satisfied

LOOP:
  10. Next criterion. Repeat.
```

**Rules in force during the loop:**

- **Commit on green only.** Never commit code that does not pass the test suite. If something must be partially landed (e.g. WIP for handoff), commit to a WIP branch or use `git stash`.
- **Three strikes stop.** If the same unit fails 3 consecutive attempts in the green phase, STOP. Surface to the founder. Do not "try harder" with bigger context dumps; that pattern leads to context-rot and worse outcomes.
- **4-hour wall-time cap.** If elapsed time hits 4 hours, hand off. Continued sessions past 4 hours have empirically poor outcomes (across SDG sessions and Claude Code community reports). Take a break.
- **Status comment on every >1-session task.** Before handoff, post a status comment to the relevant Linear issue (per SDG-37 pattern).

**During the loop:**
- `/cost` periodically to monitor token usage.
- At 60–70% utilization, decide: keep going to 80% then `/compact`, or hand off now.
- Never push past 80% utilization without active compaction. The "Lost in the Middle" effect degrades recall and increases hallucination.

---

## Phase 5 — Session-end gate (mandatory)

Before declaring the session complete, ALL of:

1. **`make check` (or equivalent) against the final commit.** Not against intermediate commits. The final commit must pass linting + type-checking + test suite.
2. **Verify git state is clean.** `git status` shows no uncommitted changes (except intentionally `.gitignore`d files).
3. **Verify the session goal is met or partial.** If met: declare success. If partial: record what was done + what's left.
4. **Run pre-PR Claude code review** if a PR is the next step (via dedicated reviewer skill OR `claude` command in the same session).

If `make check` fails on the final commit, the session is NOT complete. Two options:
- **Fix-forward:** new TDD cycle to address the failure. May extend session past 4h cap if close; otherwise hand off.
- **Revert:** `git reset --hard` to the last green commit. Document what got reverted and why in the status comment.

---

## Phase 6 — Handoff (~5 minutes)

Mandatory artifacts at handoff:

1. **Status comment** on the relevant Linear issue:
   - What landed (commits, files, tests)
   - What did NOT land (reason)
   - Open issues filed (link)
   - Next session opener (link to the new session-prompt doc)
2. **Next session prompt** (if work continues) — saved as a Linear Document or as `next-session-prompt.md` in the repo.
3. **Sync Queue updates** if specs or ADRs changed.
4. **Build Log placeholder update** — append to the in-progress weekly Build Log issue.

The `session-prompt` skill produces the next session opener. The `build-log-writer` skill consolidates on Friday.

---

## Why TDD is enforced by default

SDG validated commit-on-green and three-strikes-stop empirically. Layering TDD adds:

- **Catches "looks done but doesn't actually do what was asked".** The test is the spec, mechanically checked.
- **Reduces context rot.** With tests in place, later sessions can re-confirm correctness without re-loading the full spec.
- **Fits spec-kit's `--tdd` output.** `/speckit.tasks --tdd` produces test-ordered tasks; TDD-cycle skill picks up where spec-kit leaves off.
- **Aligns with Ralph's "deterministic success criterion" requirement.** Ralph loops on TDD-task-shaped work converge cleanly because the test is the completion signal.

**When TDD is too heavy:**
- Throwaway prototypes (one-shot scripts with no test infrastructure)
- Pure documentation work (no tests for docs)
- Bug investigation before fix (write the regression test only once the bug is understood)

For these, the session prompt template has a `# TDD mode: off` line. Default is `# TDD mode: on`.

---

## Why 100k / 200k targets

The Claude Code context window is 200k tokens on standard plans (1M on Max/Team/Enterprise via Opus 4.6, per `claudefa.st/blog/guide/mechanics/1m-context-ga`).

Empirical observations across SDG and broader community (`thesciencetalk.com`, `mindstudio.ai`):
- At 60–70% utilization, recall starts to degrade ("Lost in the Middle").
- At 80%+, auto-compaction kicks in. Compaction summarizes; fidelity drops.
- The 100k target leaves 50% headroom for free conversation growth.
- The 200k ceiling is a hard not-to-exceed; closer to 150k expected peak is the practical operating range.

For founders on Claude Max / Team / Enterprise with 1M context (Opus 4.6):
- Same discipline applies, scaled. 500k effective is the sustainable working range; 800k hard ceiling.
- The pre-flight skill detects the plan and adjusts the budgets.

**Why discipline matters even with 1M context:**
- API cost. Larger context = more tokens per turn = more $ per session.
- Wall-time. Larger context = slower response.
- The "Lost in the Middle" effect does not disappear at 1M; it just moves the inflection point.
- Founder cognitive load. Long sessions burn human attention even when the model can carry the context.

---

## Conflict cases and how the discipline resolves them

### Case 1: Founder wants to push past 4h cap to ship.

Discipline says: hand off. The 4h cap is empirically validated. Founder can start a fresh session immediately after a 30-minute break with a clean context — usually faster than pushing through.

Exception: the very-last-step case (single test, single commit needed) is acceptable to extend. Mark in the status comment.

### Case 2: TDD is slowing down a known-easy fix.

Discipline says: still write the test first. The test is the regression guard, even for "obvious" fixes. SDG D-013 noted that the dual-model review caught what the founder did not — same principle: the mechanism is the check.

Exception: trivial doc edits, README typos, comment changes. Mark as `--no-test` in the commit message reason.

### Case 3: Three-strikes-stop hit but the founder believes the next attempt will work.

Discipline says: still stop. Hand off to chat-Claude with the three failed attempts. Chat-Claude (with fresh context) re-strategizes. The next session opens with a better prompt.

The pattern that fails three times under three-strikes was probably under-specified at the spec phase. Chat-Claude session triages the spec, not the code.

### Case 4: Token budget says SPLIT but the founder thinks it'll fit.

Discipline says: trust the budget. The estimate is conservative; the cost of being wrong is mid-session compaction or session abort. Splitting upfront is cheap.

Exception: founder has a strong prior the estimate is high (e.g. most files are <50 LOC). Re-run the pre-flight with corrected file sizes.

### Case 5: Spec is ambiguous mid-session and TDD can't proceed.

Discipline says: STOP. Open chat-Claude, run `/speckit.clarify` on the ambiguous part, update the spec, then resume Code-Claude session. Do NOT have Code-Claude guess; that's the failure mode this stack is designed to prevent.

---

## Session metrics worth tracking (informally)

For the founder's own learning (not required, but recommended):

- **Sessions per feature.** A feature taking >3 sessions consistently → spec was too big; rework spec-kit splitting.
- **`make check` failure rate at session end.** >20% → TDD discipline is slipping somewhere; review which acceptance criteria are passing in CI but failing locally.
- **Three-strikes-stop frequency.** >1 per week → specs are under-clarified or stack mismatch.
- **Average peak token utilization.** Trending up over weeks → CLAUDE.md or MCP schemas are bloating; trim.

The `build-log-writer` skill prompts for these on Friday. Founder can fill in or skip.

---

## The session prompt template (full sketch — to be moved to `templates/specs/session_prompt_template.md`)

```markdown
# Claude Code session opener — <date>

## Session goal
<one sentence>

## Acceptance criteria
1. <testable>
2. <testable>
3. <testable>

## Out of scope this session
- <bullet>
- <bullet>

## Estimated duration
- Optimistic: <NN min>
- Realistic: <NN min>
- Hard cap: 4 hours

## Pre-flight (do first, in this order)
1. Read `CLAUDE.md` at repo root.
2. Run `sync-queue-runner`. Process pending. Surface conflicts.
3. Read Linear Spec: <link>
4. Read last session's status comment: <link or "first session">

## Token-budget pre-flight
- Files expected to be touched: <list>
- Estimated peak tokens: <NN>k
- Plan: GO / GO with /compact at <MM>% / SPLIT (see split plan below)

(Split plan, if SPLIT)
Session A: <goal, <100k>
Session B: <goal, <100k>
...

## Work plan
- Step 1: <action>
- Step 2: <action>
- ...

## TDD mode: on (default) | off (justify)

## Rules in force this session
- Commit on green only
- Three strikes stop
- 4-hour cap
- `make check` against final commit before declaring complete
- Status comment to <Linear issue link> before handoff

## Handoff (fill on session end)
- What landed:
- What did NOT land:
- Next session opener: <link>
- Sync Queue entries created: <links>
- Build Log placeholder updated: yes / no
```

---

## What is NOT in scope for this design doc

- Specific language tooling (`pytest` vs `vitest` vs `cargo test`) — covered in `docs/06_claude_code_setup.md` with per-language sections.
- CI/CD integration — covered in `docs/13_faq_and_pitfalls.md` since solo founders often defer CI.
- Performance profiling sessions — these are not standard build sessions; documented separately if a founder needs them.
