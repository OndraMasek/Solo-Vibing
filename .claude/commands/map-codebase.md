---
name: map-codebase
description: User-invoked frontend that runs brownfield codebase analysis by invoking the codebase-mapper agent. The agent scans the repo and writes docs/onboarding/codebase-map.md — stack, architecture sketch, conventions, entry points, test setup, build commands, deployment hints, risks. /onboard step 0 invokes the codebase-mapper agent directly; this command is the manual re-run surface (e.g. after a major refactor). The map is read as context by /discovery, /specify, and /constitution. Fires on "/map-codebase", "map-codebase", "analyze codebase", "map the repo".
---

# map-codebase

Brownfield codebase analysis — manual re-run surface. Thin frontend: its job is to invoke the `codebase-mapper` agent and relay the result. References rules: `completion-status.md`, `naming.md`.

## Trigger

- User: "/map-codebase", "map-codebase", "analyze codebase", "map the repo"

Not part of any cascade. /onboard step 0 invokes the `codebase-mapper` agent directly (not this command) on brownfield-detect — see `[SOL-SKILL] onboard`.

## Behavior

1. **Task-invoke the `codebase-mapper` agent** per `[SOL-AGENT] codebase-mapper`. The agent owns the entire analysis: repo-structure scan, stack detection, entry-point sampling, convention detection, risk identification, and composition of `docs/onboarding/codebase-map.md`. This command passes no parameters beyond the repo context — the agent's behavior is self-contained.

2. **Map agent output to command status** per `completion-status.md` §Agent contract:
   - Agent returns `DONE` (map written, founder confirmed) → command returns `DONE`.
   - Agent returns `DONE_WITH_CONCERNS` (map written, but with significant heuristic uncertainty — mixed-paradigm signals, no detectable framework, sparse test directory — surfaced in the map's Risks section) → command returns `DONE_WITH_CONCERNS`, forwarding the concern summary.
   - Agent returns `BLOCKED` (founder rejected the draft and asked for re-analysis) → command returns `BLOCKED`; the founder re-invokes `/map-codebase` to retry.
   - Agent returns `NEEDS_CONTEXT` (repo is empty or template-only; package manifests unreadable) → command returns `NEEDS_CONTEXT`.

3. **Relay the agent's chat-facing summary.** The agent shows the founder its findings summary and handles the confirm/correct loop itself. This command does not re-render — it relays the agent's output and its status.

## Same-turn write rules

No writes by the command itself. The `codebase-mapper` agent writes `docs/onboarding/codebase-map.md` (single write after founder confirmation, filesystem-only, no Linear writes) per its own contract.

## Outputs

| Artifact | Location |
| -- | -- |
| Codebase map | `docs/onboarding/codebase-map.md` (written by the `codebase-mapper` agent) |

## Completion status

Per `completion-status.md` — mapped 1:1 from the agent's return per §Agent contract:

- `DONE` — agent wrote the map and the founder confirmed accuracy.
- `DONE_WITH_CONCERNS` — map written, but with heuristic-uncertainty concerns surfaced in its Risks section.
- `BLOCKED` — founder rejected the draft; re-invoke `/map-codebase` to retry.
- `NEEDS_CONTEXT` — repo is empty / template-only (no map needed), or package manifests unreadable.

## Chains

None. Terminal when user-invoked. (The agent it invokes is also terminal — it returns to this command, which relays and ends.)

The map the agent produces is read downstream by:
- `[SOL-SKILL] discovery` — Phase 1 questions adapt to existing-codebase context.
- `[SOL-SKILL] specify` — architectural-constraints context pulls deprecated-version warnings and stack notes.
- `[SOL-SKILL] constitution` — seeds the architectural-constraints section.
- `[SOL-SKILL] onboard` — step 0 invokes the agent directly on brownfield-detect.

## Notes

**Why a command, not a skill.** Per audit decision #7, `/map-codebase` is a thin user-facing frontend; the analysis is an agent (`codebase-mapper`). The command exists only to give the founder a manual re-run surface — the heuristic-heavy work is the agent's, in its own focused context.

**The command holds no analysis logic.** Everything — the repo scan, the stack-detection heuristics, the risk list, the map template — lives in `[SOL-AGENT] codebase-mapper`. If the analysis behavior needs to change, the agent doc is the place; this command doc should stay this short.

**Manual re-run is the use case.** /onboard's step 0 invokes the agent directly on first setup. This command is for re-running after a major refactor, a dependency overhaul, or a stack migration — any time `docs/onboarding/codebase-map.md` has gone stale. The agent overwrites the map in place; git history is the version control.

**Detection is read-only** (the agent's contract): no `npm install`, no build execution, no test runs. Safe to invoke on any repo at any time.

**Empty repos.** If the repo is template-only, the agent returns `NEEDS_CONTEXT` and no map is written — there is nothing to map. /onboard's step 0 skips the agent entirely in that case.
