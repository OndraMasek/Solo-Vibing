---
name: status
description: User-invoked read-only dashboard. Renders current state across all active parents (in cascade or building), recent halts, recent completions, blockers. Pulls live from Linear; no writes. Manual only; not part of any cascade. Fires on "/status", "status", "where am I", "what's active", "summary", "/s". For the single-decisive-action variant, see /next.
---

# status

User-invoked dashboard. "Where am I." Compact status card across active and recently-completed work. Read-only. References rules: `scope-labels.md`, `completion-status.md`, `naming.md`.

## Trigger

- User: "/status", "status", "where am I", "what's active", "summary", "/s"

Not part of any cascade. For the single-line decisive-action variant, use `/next` (`[SOL-CMD] next`).

## Behavior

1. **Query Linear:**
   - All parents with label `scope:specified` or `scope:planned` per `scope-labels.md` (active cascade or ready-to-build).
   - All children with Linear state In Progress (set by `/start`).
   - All parents transitioned to Done in the last 7 days.
   - All halt-cards in the last 7 days (search comments for the `## Halt:` pattern rendered per `docs/templates/halt-messages.md`).

2. **Per-parent stage classification:**
   - "Specifying" — `scope:specified`, /plan not yet run.
   - "Cascading" — between /plan and /update-linear (rare in steady state).
   - "Ready to build" — `scope:planned`, no children In Progress.
   - "Building (Wave N)" — children In Progress.
   - "Halted: <reason>" — recent unresolved halt-card.
   - "Awaiting verify" — all children Done, /verify not yet run (only if `workflow.verify = true`).

3. **Render compact status card:**

   ~~~
   Active

   * AI-7: <title> — Building (Wave 1: AI-7-1 in progress)
   * AI-9: <title> — Ready to build (no children started)
   * AI-12: <title> — Halted: incomplete test seed (re-run /specify AI-12)

   Recently done (last 7 days)

   * AI-5: <title> — Done <date>. Retro: [<MARKER>-DOC-NNNN]

   Blocked

   * (none, or list with one-line reason)
   ~~~

   Empty case: "No active work. Last completed: AI-5 on <date>. Start with /specify <topic>."

4. Render in chat. No writes.

## Same-turn write rules

Read-only across Linear. No writes — `write-discipline.md` does not apply.

## Outputs

| Artifact | Location |
|---|---|
| Status card | Chat message |

## Completion status

Per `completion-status.md`:

- `DONE` — status card rendered.
- `DONE_WITH_CONCERNS` — n/a (read-only, no internal state).
- `BLOCKED` — n/a (no halt conditions; read-only).
- `NEEDS_CONTEXT` — Linear MCP disconnected (cannot query), or Linear query returns errors.

## Chains

None. Read-only, terminal.

## Notes

**Why a command, not a skill.** Per audit decision #2, /status is a thin deterministic read — query, classify, render. No orchestration, no writes.

**/status vs /next.** /status renders the full active landscape with multi-parent context. /next picks one decisive action. Use /status when scanning; use /next when you've just opened the laptop and want the single highest-leverage thing to do. They were one skill pre-extraction; the audit splits them into two command files because they answer different questions.

**"Building (Wave N)" depends on /start.** The classification reads Linear's In Progress state, which is set by `/start <MARKER>-N-K`. Without /start, active sessions read as "Ready to build." `CLAUDE.md` prompts the founder to invoke /start at session open.

**Drill-down via natural language.** "Tell me more about AI-7's halt" → chat-Claude reads the linked halt-card. "Show me AI-5's retro" → reads the retro doc. No special syntax.

**Time window** for "Recently done" is the last 7 days. Configurable in v0.2.

**Performance:** O(N active parents). Solo-founder workload (3–10 active parents) handled in one query batch.
