# Scope labels

Label state machine for cascade orchestration. Every skill that transitions a Linear ticket reads this rule.

## State machine

Parent ticket (the feature, output of /specify):
`(Backlog) → scope:specified → scope:planned`

Child ticket (a unit of work, output of /plan):
`(Backlog) → scope:sealed → scope:built`

`scope:built` is terminal in v1. `/ship` in v0.2 will introduce `scope:shipped`.

## Transition ownership

- `scope:specified` on parent: set by /specify at seal time.
- `scope:planned` on parent: set by /plan after decomposition completes.
- `scope:sealed` on child: set by /plan during decomposition. /verify-fix is the sole exception — it may set `scope:sealed` on a fix-child it mints.
- `scope:built` on child: set by /build on Ralph-loop success after build-reviewer passes.

No other skill writes these labels. /update-linear (with absorbed renderer) never transitions labels — it only mirrors state already set upstream.

## /build precondition contract

/build refuses to fire unless:
- Parent ticket carries `scope:planned`, AND
- Child ticket carries `scope:sealed`.

Mismatch halts /build with `BLOCKED` and a diagnostic citing observed vs expected. /build never auto-repairs labels — a mismatch indicates upstream cascade failure that needs founder attention.

## Atomic transitions

When transitioning, the prior label is removed in the same Linear write that adds the new label. No dual-state. A ticket is never simultaneously `scope:specified` and `scope:planned`. See `write-discipline.md` for the same-turn batching mechanism that enforces this.

## Refusal protocol on stale labels

If a skill observes a label combination outside the state machine (child with both `scope:sealed` and `scope:built`, parent with no scope label after /specify, etc.), it halts with `BLOCKED` and cites the observed state. Recovery is manual: founder edits the ticket labels in Linear directly, then re-invokes the skill.
