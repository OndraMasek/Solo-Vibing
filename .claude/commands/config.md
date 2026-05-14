---
name: config
description: Read and write project workflow configuration in docs/.solo-config.json. Knobs control cascade mode (cascade-only / yolo), model profile, parallelization, the Ralph caps, and which auto-fires are enabled (verify, retro, followup tickets). Foundational — other skills read this file directly at every cascade stage to adapt behavior. Fires on "/config", "config", "config show", "config get <key>", "config set <key> <value>", "configure". Default values shipped in docs/templates/.solo-config.json.template; founder edits via this command or directly.
---

# config

Reads and writes `docs/.solo-config.json`. Single source of truth for workflow knobs. References rules: `completion-status.md`, `naming.md`. The file's canonical schema is `docs/templates/.solo-config.json.template` — this command and that template must stay in sync.

## Trigger

- User: "/config", "config", "/config show", "config get <key>", "config set <key> <value>", "configure"
- Auto: read silently by every cascade stage that has a configurable knob — those stages read `docs/.solo-config.json` directly, no command invocation needed.

## Behavior

### Show mode (default)

`/config` or `/config show` → render the current config as a table, current value beside default:

~~~
Workflow configuration (docs/.solo-config.json)

marker                            SOL             (default: <MARKER>)
mode                              cascade-only    (default: cascade-only)
model_profile                     balanced        (default: balanced)
parallelization.enabled           true            (default: true)
workflow.verify                   true            (default: true)
workflow.auto_retro               true            (default: true)
workflow.followup_tickets         true            (default: true)
ralph.max_iterations              30              (default: 30)
ralph.max_wall_hours              4               (default: 4)
ralph.max_usd_cost                50              (default: 50)
~~~

### Get mode

`/config get <key>` → render a single value. Dotted keys supported (`workflow.verify`, `ralph.max_usd_cost`).

### Set mode

`/config set <key> <value>` → validate against the schema, write `docs/.solo-config.json` in place, confirm to the founder. Unknown keys and invalid values are rejected with the allowed-values list.

## Schema

```json
{
  "marker": "<2-4 uppercase chars>",
  "mode": "cascade-only" | "yolo",
  "model_profile": "quality" | "balanced" | "budget",
  "parallelization": { "enabled": true | false },
  "workflow": {
    "verify": true | false,
    "auto_retro": true | false,
    "followup_tickets": true | false
  },
  "ralph": {
    "max_iterations": <integer > 0>,
    "max_wall_hours": <number > 0>,
    "max_usd_cost": <number > 0>
  }
}
```

## Knob semantics

| Key | Effect |
| -- | -- |
| `marker` | Project marker (`SOL`, `MYA`, etc.). Determines ticket IDs, branch names, Linear doc IDs per `naming.md`. Set during /onboard; changing it post-onboard requires manual migration of all artifacts. |
| `mode` | `cascade-only` (default): /specify auto-fires the cascade through to the summary card with no intermediate prompts. `yolo`: skips human-in-loop gates only — /verify's interactive AC walkthrough is auto-passed. All mechanical gates remain enforced: /wrap scope-verify, build-reviewer, test re-verification, drift guard. Setting `interactive` is reserved for v0.2 (founder-per-stage confirmation) and currently behaves identically to `cascade-only`. |
| `model_profile` | Advisory only in v0.1 — no per-stage model swap yet. v0.2 will route /plan to budget, /review to quality, etc. The knob exists so v0.2 has a stable surface to bind against. |
| `parallelization.enabled` | When `false`, /plan renders the wave structure but suppresses the git-worktree block — sequential build is the founder's chosen mode. |
| `workflow.verify` | When `true`, /wrap's last-child completion invokes /verify before transitioning the parent to Done. When `false`, the parent transitions directly to Done after the last /wrap. |
| `workflow.auto_retro` | When `true`, parent → Done auto-fires /retro. When `false`, /retro is manual-only. |
| `workflow.followup_tickets` | When `true`, /retro auto-creates Backlog tickets for each Followups-section item. When `false`, followups stay as text in the retro doc. |
| `ralph.max_iterations` | Hard cap on Ralph loop iterations per /build run. Default 30. Checked post-iteration in `run.sh` — the count can reach the cap, not exceed it. |
| `ralph.max_wall_hours` | Hard cap on wall-clock hours per /build run. Default 4. Checked post-iteration. |
| `ralph.max_usd_cost` | Hard cap on cumulative USD cost per /build run. Default 50. Checked post-iteration, so actual spend can exceed the cap by up to one iteration's worth. Cumulative across `--continue` runs. |

## Defaults

Shipped as `docs/templates/.solo-config.json.template`:

```json
{
  "marker": "<MARKER>",
  "mode": "cascade-only",
  "model_profile": "balanced",
  "parallelization": { "enabled": true },
  "workflow": {
    "verify": true,
    "auto_retro": true,
    "followup_tickets": true
  },
  "ralph": {
    "max_iterations": 30,
    "max_wall_hours": 4,
    "max_usd_cost": 50
  }
}
```

/onboard step 5 copies this template to `docs/.solo-config.json` with the chosen marker substituted.

## Same-turn write rules

Per `write-discipline.md`: `docs/.solo-config.json` — single write per set operation. No Linear writes.

## Outputs

| Artifact | Location |
| -- | -- |
| Config file | `docs/.solo-config.json` |

## Completion status

Per `completion-status.md`:

* `DONE` — show/get rendered a result; set validated and wrote `docs/.solo-config.json`.
* `DONE_WITH_CONCERNS` — n/a (config surface is small and binary; success or failure).
* `BLOCKED` — set rejected an invalid value (schema mismatch, unknown key); founder must re-issue with a valid key/value pair.
* `NEEDS_CONTEXT` — `docs/.solo-config.json` missing entirely. Defaults apply silently to cascade stages, but show mode warns; /config can write the file fresh from `docs/templates/.solo-config.json.template` if the founder confirms.

## Chains

None. Terminal.

## Notes

**Why a command, not a skill.** Per audit decision #2, /config is a thin deterministic surface — show / get / set over a JSON file. No orchestration.

**Config is read silently by other skills, not invoked through skill-chaining.** Each cascade stage reads `docs/.solo-config.json` at start; if absent, the shipped defaults apply. No halt on missing config.

**Cascade-mode semantics live here** (audit decision #4) — no separate `rules/cascade-modes.md`. `cascade-only` and `yolo` are defined in the `mode` row above. `yolo` skips only human-in-loop gates (currently just /verify's interactive AC walkthrough); every mechanical gate (/wrap scope-verify, build-reviewer, test re-verification, Ralph drift guard) remains enforced. The `interactive` value is parsed but reserved for v0.2 — it currently behaves identically to `cascade-only`.

**The** `ralph` **block.** Added in this Batch 3 transformation. The pre-extraction `[SOL-SKILL] config` omitted it, but `[SOL-SKILL] build` requires `docs/.solo-config.json` to declare `ralph.max_iterations` / `max_wall_hours` / `max_usd_cost`, and `[SOL-TPL] .solo-config.json.template` (chat 6, canonical union) ships it. This command now matches the template — the chat-6 open delta is closed.

`model_profile` **is advisory in v0.1** because the public stack doesn't ship per-stage model routing yet. The knob exists so v0.2 has a stable surface to bind against without breaking v0.1 configs.

**Schema validation is strict:** unknown keys rejected, type mismatches rejected. Forward-compatible additions go through a v0.2 release that bumps a schema-version field — not in v0.1; the schema stays flat.

**Config is single-project.** Multi-project workflows in one Linear workspace each have their own `docs/.solo-config.json`. The shared concern is `marker`, which determines Linear cross-project lookup keys per `naming.md`.
