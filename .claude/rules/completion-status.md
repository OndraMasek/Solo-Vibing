# Completion status

Every skill terminates with one of four statuses. The cascade engine, the chat-summary renderer (inside /update-linear), and downstream skill chaining all read this contract.

## Values

- `DONE` — all writes succeeded; preconditions held throughout; no findings worth surfacing to the founder.
- `DONE_WITH_CONCERNS` — writes succeeded, but findings exist below the skill's halt threshold (e.g. build-reviewer flagged a minor concern that didn't trip halt; four-hat surfaced a "consider" finding that doesn't block sealing). Findings are listed in the summary.
- `BLOCKED` — a precondition failed, or a terminal write failed, or a halt threshold was tripped. Nothing chains downstream. Halt-card rendered per `docs/templates/halt-messages.md`.
- `NEEDS_CONTEXT` — the skill cannot proceed without founder input: ambiguous slug, missing artifact the founder must produce, unresolvable clarify question. Returns to founder with a specific question.

## Per-status conditions

Each skill defines its own per-status conditions in the skill file (e.g. /build's `BLOCKED` triggers: spec checksum drift, live PID collision, sandbox not configured). This rule defines only the contract: the four values, their cascade behavior, their rendering convention.

## Cascade chaining

- `DONE` and `DONE_WITH_CONCERNS` chain downstream per the cascade.
- `BLOCKED` and `NEEDS_CONTEXT` halt. The founder sees the halt-card or context-needed prompt; no downstream skill fires.

## Agent contract

Agents (four-hat-*, build-reviewer, clarify-walker, decomposer, diagnoser, research-investigator, codebase-mapper) return structured findings only. The invoking skill maps findings to a status:

- Zero findings → `DONE`.
- Findings exist, all below skill-defined halt threshold → `DONE_WITH_CONCERNS`.
- One or more findings above threshold → `BLOCKED`.

Agents never decide cascade flow. Skills do.
