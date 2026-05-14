---
name: onboard
description: First-run interactive setup. Initializes a new Solo-Setup project — brownfield check, prereqs, Linear + GitHub MCP connections, Linear API key, project marker, config, CLAUDE.md scaffold, and seeds the first north-star question that hands off to /discovery. Fires on "/onboard", "onboard", "set up project", "initialize", or on the first chat-Claude turn in an uninitialized repo (no docs/.solo-config.json). Manual override `/onboard --reinit <step>` re-runs a single step. Invokes the codebase-mapper agent at step 0 for brownfield repos; Task-invokes /discovery at step 7.
---

# onboard

Interactive setup. Run once per new project, after cloning the Solo-Setup template into a fresh repo. Each step waits for founder response before advancing. References rules: `naming.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`. Invokes agent: `codebase-mapper` (step 0). Chains to skill via Task tool: `discovery` (step 7).

## Trigger

- User: "/onboard", "onboard", "set up project", "initialize"
- Auto: first chat-Claude turn in a repo where `docs/.solo-config.json` is missing
- Manual override: `/onboard --reinit <step>` — re-runs one specific step

## Behavior

0. **Brownfield check** *(conditional, runs before step 1).* Detect whether the repo contains source beyond the Solo-Setup template. Heuristic: count files outside `docs/templates/`, `docs/discovery/`, `docs/decisions/`, `docs/product/`, `.git/`, and standard ignore patterns. If non-template source detected → **Task-invoke the `codebase-mapper` agent** per `[SOL-AGENT] codebase-mapper`. The agent scans the repo and writes `docs/onboarding/codebase-map.md`, then returns. Map agent status per `completion-status.md` §Agent contract: agent `NEEDS_CONTEXT` (empty/template-only) → skip to step 1 as if greenfield; agent `BLOCKED` (founder rejected the draft) → surface and let the founder re-run step 0 via `--reinit 0`; agent `DONE` / `DONE_WITH_CONCERNS` → carry the map forward. If the repo is empty/template-only → skip to step 1.

1. **Prereqs check.** Run `scripts/check_prereqs.sh`. Verifies the template/reference files exist:
   - `docs/templates/spec.md.template`
   - `docs/templates/halt-messages.md`
   - `docs/templates/CLAUDE.md.template`
   - `docs/templates/.solo-config.json.template`
   - `docs/product/north-star-questions.md`
   - `docs/discovery/research-prompt-templates.md`
   - `docs/discovery/challenge-checklist.md`

   Missing files → `BLOCKED` per `completion-status.md`, halt-card per `docs/templates/halt-messages.md` §missing-context: name the missing files and tell the founder to clone the template fresh rather than patch by hand.

2. **Connectors check.** Confirm both Linear MCP and GitHub MCP are connected in this Claude.ai project. Test Linear with a no-op `list_teams` call; test GitHub with a no-op `get_me` call. Either missing → `BLOCKED`. Linear absent → halt per `docs/templates/halt-messages.md` §linear-unavailable; instruct the founder to add the Linear connector in Claude.ai settings, then re-run /onboard. GitHub absent → halt per §github-unavailable; instruct the founder to add the GitHub connector in Claude.ai settings, then re-run /onboard.

3. **Linear personal API key.** Ask the founder to paste their Linear personal API key into `.env` as `LINEAR_API_KEY=...`. Run `scripts/verify_linear_key.sh` to confirm it works. **The key never enters chat** — only `.env`. Verify `.env` is gitignored; not gitignored → `BLOCKED`. The key is consumed by `scripts/verify_linear_key.sh` at onboard time and reserved for v0.2 scripts (e.g. /ship); cascade skills themselves use the Linear MCP connector, not this key.

4. **Project marker.** Ask: *"What's the Linear project marker for this repo?"* Default suggestion: `SOL`. Asked every time so forks pick their own marker (`MYA`, `PRJ`, etc.) per `naming.md` §Marker. The chosen marker is recorded in `docs/.solo-config.json` (step 5) and `CLAUDE.md` (step 6) — `naming.md` reads it from `docs/.solo-config.json`; no skill hardcodes a marker.

5. **Config init.** Copy `docs/templates/.solo-config.json.template` to `docs/.solo-config.json` with `<MARKER>` substituted — workflow knobs and the `ralph` caps block; see `commands/config.md` for the schema. No counter file is created; allocation is scan-based per `counter-allocation.md`.

6. **CLAUDE.md scaffold.** Copy `docs/templates/CLAUDE.md.template` to `CLAUDE.md` with `<MARKER>` substituted. `CLAUDE.md` imports the six rules via `@` syntax (per audit amendment A2). **Never overwrite an existing `CLAUDE.md` without explicit founder confirmation** — if one exists, show the diff and ask before writing.

7. **First north-star question.** Ask one of the seeded questions from `docs/product/north-star-questions.md` (e.g. *"In one sentence, what problem does this project solve?"*). If `docs/onboarding/codebase-map.md` exists from step 0, frame the question with codebase context. The founder's answer is the seed for /discovery's Phase 1 — **Task-invoke `/discovery`** with the answer as the Phase 1 seed.

**Linear projects auto-created** (idempotent — only if absent in the team): `Decisions`, `Backlog`, `Active`. Bare names; team membership establishes context, no marker prefix on project names. Batched same-turn per `write-discipline.md`.

## Same-turn write rules

Per `write-discipline.md`:
- Filesystem writes (`docs/.solo-config.json`, `CLAUDE.md`): grouped per step, after founder confirmation.
- Linear writes (project creation): batched same-turn when missing.
- `.env` is written by the founder, never by the skill.

## Outputs

| Artifact | Location |
| -- | -- |
| Codebase map (brownfield only) | `docs/onboarding/codebase-map.md` (written by the `codebase-mapper` agent) |
| Workflow config | `docs/.solo-config.json` |
| Project constitution scaffold | `CLAUDE.md` |
| Linear projects (if absent) | Linear team: `Decisions`, `Backlog`, `Active` |
| First north-star seed | Task-handed to /discovery |

## Completion status

Per `completion-status.md`:

- `DONE` — all steps confirmed by the founder; /discovery Task-invoked with the north-star seed.
- `DONE_WITH_CONCERNS` — onboard completed but: step 6 preserved an existing `CLAUDE.md` instead of writing the scaffold; or the step-0 brownfield map returned `DONE_WITH_CONCERNS` (heuristic-uncertainty concerns surfaced in the map's Risks section).
- `BLOCKED` — step 1 missing template files; step 2 Linear MCP disconnected or GitHub MCP disconnected; step 3 `.env` not gitignored; step 0 agent returned `BLOCKED` and the founder hasn't re-run. Halt-card per `docs/templates/halt-messages.md`.
- `NEEDS_CONTEXT` — `.env` missing entirely; Linear API key invalid or revoked; founder aborted at a confirmation gate without resolution.

## Chains

On step 7 completion → **Task-invoke /discovery** with the founder's north-star answer as the Phase 1 seed (per audit decision #9 — chaining via the Task tool, not label/state triggers). Step 0's brownfield path invokes the `codebase-mapper` agent inline and returns to step 1; that is an agent invocation, not a skill chain.

## Notes

**Interactive by design.** Each step waits for founder confirmation because onboard is high-stakes: it writes the filesystem, creates Linear projects, and triggers a multi-day discovery flow. No silent advancement.

**Re-running `/onboard` after initial setup is safe** — projects already created are skipped and `CLAUDE.md` is never overwritten without confirmation. Use `/onboard --reinit <step>` to redo one step (rotated Linear API key, marker change).

**Step 0 invokes the agent, not the command.** Per audit decision #7, the brownfield analysis is the `codebase-mapper` agent. /onboard Task-invokes the agent directly; the founder's manual re-run surface is the separate `/map-codebase` command. /onboard does not call `/map-codebase`.

**Prereq list reconciled.** The pre-extraction body listed two template files that turned out to be phantoms, and both have been removed from the step-1 check:
- `docs/discovery/discover-questions.md` — verified a phantom in chat 6 (`[SOL-SKILL] discovery` references only `north-star-questions.md`). Removed in the chat-7 revision.
- `docs/templates/kill-switch.md` — verified a phantom in chat 8. `kill-switch.md` was a relic of the pre-reversal discovery design (kill-switch-questions-first); the founder reversed /discovery to discover-first-then-challenge, and the kill function moved into Phase 3's `challenge-checklist.md` (four-verdict rubric: approve / refine / kill / pivot). No live skill references `kill-switch.md`. Removed in the chat-8 revision.

The remaining step-1 list is the actually-extracted artifact set: `spec.md.template`, `halt-messages.md`, `CLAUDE.md.template`, `.solo-config.json.template`, `north-star-questions.md`, `research-prompt-templates.md`, `challenge-checklist.md`. The `.doc-counter.json.template` was removed in the counter-allocation refactor — counters are scan-based per `counter-allocation.md`.

**The default marker `SOL`** matches the upstream Solo-Setup repo. Forks pick their own so cross-references stay unambiguous when several repos coexist in one Linear workspace. The marker lives in `docs/.solo-config.json`; `naming.md` reads it from there.

**CLAUDE.md scaffold is the template version, not the locked production version.** The founder edits it after onboard — project-specific principles, tool constraints, naming conventions. Constitution rules (including "Only /plan sets `scope:sealed`") live in `docs/constitution.md`, authored by `/constitution`, not in `CLAUDE.md`.

**The steps are the minimum viable setup.** Steps that look optional (connectors verify, gitignore check) exist because they're the most common silent-failure modes in fresh forks.

## Open questions (deferred to v1.1+)

- **`scripts/check_prereqs.sh` and `scripts/verify_linear_key.sh`** are referenced but not themselves canonical Linear docs. They're shell scripts that ship in the template repo; whether they need `[SOL-FILE]` mirrors is a v1.1 question.
- **Brownfield heuristic precision.** The "count files outside known dirs" detector is coarse. AST-level or manifest-aware detection is v1.1+ (shared concern with the `codebase-mapper` agent).
