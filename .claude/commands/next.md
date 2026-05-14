---
name: next
description: User-invoked single decisive action. Queries the active landscape and renders one line — the single highest-leverage thing to do right now — with one-line reasoning. No alternatives, no table. Read-only; no writes; not part of any cascade. Fires on "/next", "/n", "what's next", "next step", "what should I do". For the full multi-parent landscape, see /status.
---

# next

Single decisive action. One line. The highest-leverage thing to do right now. Read-only. References rules: `scope-labels.md`, `completion-status.md`, `naming.md`.

## Trigger

- User: "/next", "/n", "what's next", "next step", "what should I do"

Not part of any cascade. For the full active landscape with alternatives, use `/status` (`[SOL-CMD] status`).

## Behavior

1. **Query Linear** — the same set as `/status`: parents with `scope:specified` / `scope:planned` per `scope-labels.md`, children In Progress, parents Done in the last 7 days, unresolved halt-cards (the `## Halt:` pattern per `docs/templates/halt-messages.md`).

2. **Apply next-action priority — first match wins:**
   1. **Unresolved halt-card** → resolve the halt: "Resolve halt on <MARKER>-N: <halt summary>. Suggested: <recommended next action from the halt-card>."
   2. **Child In Progress** → continue the current session: "Continue the build session on <MARKER>-N-K."
   3. **Awaiting verify** (all children Done, /verify not run, `workflow.verify = true`) → "Run /verify <MARKER>-N — all children green, manual acceptance pending."
   4. **Parent `scope:planned` with Wave-1-ready children not started** → start a child: "Run /build <MARKER>-N-K to start the next child. <If parallel Wave 1: 'or open a second session for <MARKER>-N-L.'>"
   5. **Parent `scope:specified`** (cascade still running or stalled mid-cascade) → "<MARKER>-N cascade may be stalled — re-invoke /plan <MARKER>-N to resume."
   6. **Discovery state file present, not at `approve` exit** → "Resume /discovery — Phase <N> incomplete."
   7. **Clean slate** → "No active work. Start with /specify <topic>."

3. **Render a single-line next action:**

   ~~~
   Next: <action> — <one-line reasoning>.
   ~~~

   No table, no alternatives. One line. For alternatives, the founder invokes `/status`.

## Same-turn write rules

Read-only across Linear. No writes — `write-discipline.md` does not apply.

## Outputs

| Artifact | Location |
|---|---|
| Single-line next action | Chat message |

## Completion status

Per `completion-status.md`:

- `DONE` — next-action line rendered.
- `DONE_WITH_CONCERNS` — n/a (read-only, no internal state).
- `BLOCKED` — n/a (read-only).
- `NEEDS_CONTEXT` — Linear MCP disconnected, or Linear query returns errors.

## Chains

None. Read-only, terminal.

## Notes

**Why split from /status.** Pre-extraction these were two modes of one skill. They answer different questions: /status is "show me everything," /next is "tell me the one thing." The audit's "Slash commands (8 files)" list gives each its own command file so the trigger surfaces stay distinct and each doc stays single-purpose.

**Priority 4 recommends `/build`, not `/start`.** In the pre-extraction model the recommendation was "run /start <MARKER>-N-K then open Code-Claude." Post-extraction, /build owns the build entry point and Task-invokes /start itself at its preconditions step (per audit decision #1) — so the single decisive action for a ready child is `/build <MARKER>-N-K`, not a manual /start. /start remains available for out-of-band tracking but is not the cascade's build trigger.

**First-match-wins ordering** is deliberate: a halt always outranks new work, an in-flight session outranks starting another, verification outranks starting the next feature. The founder gets the one thing that most needs doing, not a menu.
