# Write discipline

Side-effect hygiene for skills that touch Linear, the filesystem, or git. Reduces API thrash, prevents partial-state messes, and codifies the "Same-turn write rules" sections that previously restated across every skill file.

## Same-turn batching

Within a skill, all writes are emitted in a single same-turn batch: file writes grouped (multiple `Write` calls in one turn, not chained across turns), Linear MCP calls grouped (one ticket-update call with all fields combined; one doc-update call; comments grouped within the same turn), git operations grouped (stage + commit in one turn; push as a single command). Writes within a batch run in parallel where the platform allows. A skill never waits for its own write to complete before issuing the next one in the same logical batch.

## No skill-chaining writes

A skill writes its own outputs only. Cascade-downstream skills get their own turns. /specify never writes /plan's artifacts. /plan never writes /build's artifacts. The cascade engine — in-skill explicit chaining via the Task tool, per audit decision #9 — handles the handoff.

## Linear MCP round-trip minimization

- One ticket-update call per skill turn (title + description + labels + parentId + state, combined wherever the API permits).
- One doc-update call per skill turn.
- Comments grouped within the turn; do not split a multi-comment update across turns.

When the API forces separate calls (e.g. document create followed by document update), they still batch within the same turn.

## Read-before-write

When updating an existing Linear artifact, fetch its current state in the same turn as the planned write. If observed state contradicts the skill's precondition (label drifted, content edited since the cascade started), abort the write and surface `BLOCKED` per `completion-status.md`.

## Atomic label transitions

Prior label removed in the same write that adds the new label. See `scope-labels.md` for the state machine; this rule provides the mechanism.

## Partial failure

If a write fails partway through a batch (file writes succeed, Linear API down, etc.), the skill:

1. Records the partial state as a marker file in the relevant workspace (e.g. /build's `.ralph/<TICKET>/linear.sync.pending`).
2. Surfaces `BLOCKED` with a sync-retry hint pointing at the relevant `--sync` command.
3. Does not retry within the same skill turn.

The retry path is always a separate user-invoked skill or command mode.
