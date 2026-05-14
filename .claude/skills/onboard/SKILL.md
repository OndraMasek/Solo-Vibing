---
name: onboard
description: First-run interactive setup. Initializes a new Solo-Setup project — brownfield check, prereqs, upstream-content audit, Linear + GitHub MCP connections, GitHub remote, Linear API key, project marker, Linear team pick, config, CLAUDE.md scaffold, and renders the chat-handoff artifacts that move /discovery into chat-Claude. Fires on "/onboard", "onboard", "set up project", "initialize", or on the first chat-Claude turn in an uninitialized repo (no docs/.solo-config.json). Manual override `/onboard --reinit <step>` re-runs a single step. Invokes the codebase-mapper agent at step 0 for brownfield repos; in `code` discovery surface mode (legacy), Task-invokes /discovery at step 7.
---

# onboard

Interactive setup. Run once per new project, after cloning the Solo-Setup template into a fresh repo. Each step waits for founder response before advancing. References rules: `naming.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`. Invokes agent: `codebase-mapper` (step 0). In `chat` discovery-surface mode (default), step 8 hands off to chat-Claude via rendered artifacts; in `code` mode, step 7 Task-invokes `/discovery`.

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
   - `docs/templates/onboarding/chat-kickoff.md.template`
   - `docs/templates/onboarding/chat-instructions.md.template`
   - `docs/templates/discovery/research-prompt-templates.md`
   - `docs/templates/discovery/challenge-checklist.md`
   - `docs/product/north-star-questions.md`

   Missing files → `BLOCKED` per `completion-status.md`, halt-card per `docs/templates/halt-messages.md` §missing-context: name the missing files. The recommended next action is `bash bootstrap.sh --refresh-templates` (re-overlays the templates from upstream without touching project state) rather than a full re-clone, which would lose the founder's `.env`, marker, and any post-onboard work.

1.5. **Upstream content audit.** Detect populated upstream artifacts a fresh fork inherits and that downstream skills could misread as the fork's own state:
   - `docs/constitution.md`
   - `docs/specs/0001-*/` directories
   - `docs/product/north-star.md`
   - `docs/product/north-star-questions.md` (kept by default — it is a template, not a fork-specific artifact)

   For each detected file (except `north-star-questions.md`), prompt the founder via `AskUserQuestion`:
   - **Wipe** (default) — file is re-authored by `/constitution` and `/discovery` in the fork's own voice.
   - **Move to `docs/upstream-examples/`** — keep as reference; the destination is added to `.gitignore` so downstream skills don't read them.
   - **Keep in place** — explicit founder override; log warning that `/specify`, `/review`, and `/verify` may misread upstream content as the fork's own state.

   Skip entirely on `--reinit` runs (the audit is a fresh-fork concern). Skip if the founder ran `/onboard --skip-upstream-audit`. After answers, re-state the founder's authorization in the response immediately before issuing the filesystem writes (per Notes §AskUserQuestion re-statement).

2. **Connectors check.** Confirm both Linear MCP and GitHub MCP are connected in this Claude.ai project. Canonical probes:
   - **Linear MCP**: `list_teams` call. Empty response → unreachable.
   - **GitHub MCP**: `gh auth status` via Bash. The GitHub MCP server's deferred tool surface (`mcp__github__authenticate`, `mcp__github__complete_authentication`) doesn't include a query probe, so `gh auth status` is the canonical fallback. Non-zero exit → unreachable.

   Either missing → `BLOCKED`. Linear absent → halt per `docs/templates/halt-messages.md` §linear-unavailable; instruct the founder to add the Linear connector in Claude.ai settings, then re-run /onboard. GitHub absent → halt per §github-unavailable; instruct the founder to add the GitHub connector in Claude.ai settings (or install `gh` locally and run `gh auth login`), then re-run /onboard.

2.5. **GitHub remote check.** Run `git remote -v | grep -q origin`. If missing, surface the two paths:
   - **Preferred**: `gh repo create --source=. --private --push` (only if `gh` is authed). Bootstrap should have created the remote (see `bootstrap.sh` notes); reaching this branch means the founder declined the prompt during bootstrap or ran `/onboard` in a manually-initialized repo.
   - **Manual**: `git remote add origin <url> && git push -u origin main`.

   Halt `NEEDS_CONTEXT` per §github-remote-missing until the founder confirms the remote is set. After step 6 (canonical files first committed), the skill auto-runs `git push` once. If push fails (most commonly because the remote was pre-created with auto-init and has a divergent history), halt `BLOCKED` per §parallel-history-risk with recovery options.

3. **Linear personal API key.** Ask the founder to paste their Linear personal API key into `.env` as `LINEAR_API_KEY=...`. Run `scripts/verify_linear_key.sh` to confirm it works. **The key never enters chat** — only `.env`. Verify `.env` is gitignored; not gitignored → `BLOCKED`. The key is consumed by `scripts/verify_linear_key.sh` at onboard time and reserved for v0.2 scripts (e.g. /ship); cascade skills themselves use the Linear MCP connector, not this key.

   **Worktree warning.** Detect worktree via `git rev-parse --is-inside-work-tree` and `[ "$(git rev-parse --git-common-dir)" != "$(git rev-parse --git-dir)" ]`. If running in a worktree, warn: "This is a worktree; `.env` written here will not survive worktree removal. After merging this work, copy `.env` to the main repo at `<main-repo-path>`." The verify script resolves `.env` from both worktree-local and `git rev-parse --git-common-dir`-derived paths (first match wins).

4. **Project marker.** Ask: *"What's the Linear project marker for this repo?"* Default suggestion: `SOL`. Asked every time so forks pick their own marker (`MYA`, `PRJ`, etc.) per `naming.md` §Marker. The chosen marker is recorded in `docs/.solo-config.json` (step 5) and `CLAUDE.md` (step 6).

   After the marker is picked, surface a one-line clarification: *"Linear team keys (e.g. `SOL`, `OMA`) are separate from your repo marker. Your marker `<MARKER>` is repo-scoped; Linear ticket IDs in the UI will use the team's key prefix. See `.claude/rules/naming.md` §Shared Linear teams."* This avoids the conflation observed in fresh-fork runs.

4.5. **Linear team pick.** Call `list_teams` via Linear MCP.
   - **Exactly one team** → pick it silently and record the team name in `docs/.solo-config.json` as `linear.team_name`.
   - **Multiple teams** → prompt via `AskUserQuestion` with team names + keys as options. After founder picks, re-state the authorization in the response before the next privileged Linear call.
   - **Default-project collision check.** In the chosen team, list projects. If a project named `Backlog`, `Decisions`, or `Active` already exists with content unrelated to this fork (founder's judgment), offer rename-or-new-team. The default behavior is to reuse the existing projects idempotently — this gate only fires when the founder flags a conflict during the prompt.

5. **Config init.** Copy `docs/templates/.solo-config.json.template` to `docs/.solo-config.json` with `<MARKER>` substituted and the team name from step 4.5 written under `linear.team_name`. Workflow knobs include `discovery_surface` (`chat` default; see `commands/config.md`). No counter file is created; allocation is scan-based per `counter-allocation.md`.

6. **CLAUDE.md scaffold.** Copy `docs/templates/CLAUDE.md.template` to `CLAUDE.md` with `<MARKER>` substituted. `CLAUDE.md` imports the six rules via `@` syntax (per audit amendment A2). **The upstream repo's own `CLAUDE.md` is gitignored** per `.gitignore` (it is the Solo-Setup repo's local session instructions, not the template a fork starts with) — fresh forks therefore never inherit a populated `CLAUDE.md`. If a `CLAUDE.md` already exists at this step (re-run, or founder created it manually), show the diff and ask before overwriting.

7. **First north-star question.** Ask one of the seeded questions from `docs/product/north-star-questions.md` (e.g. *"In one sentence, what problem does this project solve?"*). If `docs/onboarding/codebase-map.md` exists from step 0, frame the question with codebase context. The founder's answer is the seed for /discovery's Phase 1 — captured for use in step 8.

   **No auto-chain to /discovery in the default `chat` discovery surface mode.** Read `workflow.discovery_surface` from `docs/.solo-config.json`:
   - `chat` (default) — capture the answer and proceed to step 8 (chat handoff). Do not Task-invoke /discovery.
   - `code` (legacy, used for self-testing the Solo-Setup repo itself) — Task-invoke `/discovery` with the answer as the Phase 1 seed and skip step 8.

8. **Chat handoff render.** *(`chat` discovery surface mode only.)* Render two templates with founder-specific substitutions:
   - `docs/templates/onboarding/chat-kickoff.md.template` → `docs/onboarding/chat-kickoff.md`. Substitutions: `<MARKER>`, `<REPO_URL>` (from `git remote get-url origin`), `<LINEAR_TEAM_NAME>` (from `docs/.solo-config.json`), `<NORTH_STAR_Q1_ANSWER>` (captured in step 7).
   - `docs/templates/onboarding/chat-instructions.md.template` → `docs/onboarding/chat-instructions.md`. Substitution: `<MARKER>`.

   Both writes batched same-turn per `write-discipline.md`. After write, `git add` both files + step 6's `CLAUDE.md` + step 5's `docs/.solo-config.json`, commit (`chore: onboard <MARKER>`), and push to origin per step 2.5's auto-push contract.

   Terminate `DONE` with a summary card pointing the founder at `docs/onboarding/chat-kickoff.md` and the next action: open claude.ai, create a project, attach the connectors, paste the kickoff message. The kickoff template is committed (not gitignored), so chat-Claude can read it via the GitHub connector on its first invocation.

**Linear projects auto-created** (idempotent — only if absent in the team picked at step 4.5): `Decisions`, `Backlog`, `Active`. Bare names; team membership establishes context, no marker prefix on project names. Batched same-turn per `write-discipline.md`.

## Same-turn write rules

Per `write-discipline.md`:
- Filesystem writes (`docs/.solo-config.json`, `CLAUDE.md`, the two `docs/onboarding/*.md` files in step 8): grouped per step, after founder confirmation.
- Linear writes (project creation, team selection if step 4.5 wrote anything): batched same-turn when missing.
- Git operations (step 8's add/commit/push): single command sequence.
- `.env` is written by the founder, never by the skill.

## Outputs

| Artifact | Location |
| -- | -- |
| Codebase map (brownfield only) | `docs/onboarding/codebase-map.md` (written by the `codebase-mapper` agent) |
| Workflow config | `docs/.solo-config.json` |
| Project session instructions | `CLAUDE.md` (gitignored at upstream; tracked at fork) |
| Chat-side handoff (chat surface mode) | `docs/onboarding/chat-kickoff.md`, `docs/onboarding/chat-instructions.md` |
| Linear projects (if absent) | Selected Linear team: `Decisions`, `Backlog`, `Active` |
| First north-star seed | Embedded in `chat-kickoff.md` (chat mode) or Task-handed to /discovery (code mode) |

## Completion status

Per `completion-status.md`:

- `DONE` — all steps confirmed by the founder; in chat surface mode, step 8 rendered both handoff files and pushed; in code surface mode, /discovery Task-invoked with the north-star seed.
- `DONE_WITH_CONCERNS` — onboard completed but: step 6 preserved an existing `CLAUDE.md` instead of writing the scaffold; step 1.5 left upstream content in place per founder override; step 0 brownfield map returned `DONE_WITH_CONCERNS`.
- `BLOCKED` — step 1 missing template files; step 2 Linear or GitHub MCP disconnected; step 2.5 GitHub push failed against a divergent-history remote; step 3 `.env` not gitignored; step 0 agent returned `BLOCKED` and the founder hasn't re-run. Halt-card per `docs/templates/halt-messages.md`.
- `NEEDS_CONTEXT` — `.env` missing entirely; Linear API key invalid or revoked; founder aborted at a confirmation gate without resolution; step 2.5 GitHub remote missing and founder hasn't confirmed remote setup.

## Chains

- **`workflow.discovery_surface: chat` (default)** — terminal. The founder moves to chat-Claude using the rendered `docs/onboarding/chat-kickoff.md`. `/discovery` runs there, not via Task tool. See `commands/config.md` for the knob.
- **`workflow.discovery_surface: code`** — On step 7 completion, **Task-invoke /discovery** with the founder's north-star answer as the Phase 1 seed. Preserved for self-testing the Solo-Setup repo itself, which doesn't have a chat-side counterpart.

Step 0's brownfield path invokes the `codebase-mapper` agent inline and returns to step 1; that is an agent invocation, not a skill chain.

## Notes

**Interactive by design.** Each step waits for founder confirmation because onboard is high-stakes: it writes the filesystem, creates Linear projects, and (in code mode) triggers a multi-day discovery flow. No silent advancement.

**Re-running `/onboard` after initial setup is safe** — projects already created are skipped, `CLAUDE.md` is never overwritten without confirmation, and step 1.5 is skipped on `--reinit`. Use `/onboard --reinit <step>` to redo one step (rotated Linear API key, marker change, re-render chat handoff after editing the kickoff template).

**Step 0 invokes the agent, not the command.** Per audit decision #7, the brownfield analysis is the `codebase-mapper` agent. /onboard Task-invokes the agent directly; the founder's manual re-run surface is the separate `/map-codebase` command. /onboard does not call `/map-codebase`.

**Three-touch goal.** The chat-surface flow is engineered so the founder makes only three substantive interactions: marker pick (step 4), Linear API key paste (step 3), north-star Q1 answer (step 7). Everything else is either skill-internal (steps 0, 1, 5, 6, 8) or a yes/no confirmation gate (steps 1.5, 2, 2.5, 4.5).

**AskUserQuestion re-statement convention** *(per the Bomber-test permission-classifier finding)*. When a step uses `AskUserQuestion` followed by a privileged tool call (e.g. Linear write, filesystem write outside the templates directory), the skill emits a one-line text output re-stating the founder's authorization in the response immediately before the tool call. The classifier reads recent context; re-stating the answer in-line ensures the authorization is visible at decision time. Applies to step 1.5 (upstream content wipe), step 4.5 (team pick), step 7 (north-star answer commit).

**CLAUDE.md scaffold is the template version, not the locked production version.** The founder edits it after onboard — project-specific principles, tool constraints, naming conventions. Constitution rules (including "Only /plan sets `scope:sealed`") live in `docs/constitution.md`, authored by `/constitution`, not in `CLAUDE.md`.

**The steps are the minimum viable setup.** Steps that look optional (connectors verify, gitignore check, upstream content audit, GitHub remote check, worktree warning) exist because they're the most common silent-failure modes in fresh forks. Each maps to a specific failure observed in the Bomber-test report.

## Open questions (deferred to v1.1+)

- **Brownfield heuristic precision.** The "count files outside known dirs" detector is coarse. AST-level or manifest-aware detection is v1.1+ (shared concern with the `codebase-mapper` agent).
- **`interactive` cascade mode** in `docs/.solo-config.json` is parsed but not implemented in v0.1; reserved for a future per-stage confirmation surface.
