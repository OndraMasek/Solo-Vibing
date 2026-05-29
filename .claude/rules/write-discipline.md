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

## Denylist + reviewer-stance (no allow-list)

Per `0001-v0.2-cascade-integration` AC-21 / SOL-HANDOFF-008 decision 3, write-discipline is **denylist-driven with a reviewer-stance soft-check** — explicitly not a hard allow-list. Two layers:

**1. Hard halt — `PreToolUse` denylist (build-agent-scoped).** Patterns at `.claude/agents/build-write-denylist.txt` (per D4.1 §D4.1.7) name cascade-control files that the **autonomous build agent** must not write. The `pretool-write-denylist.sh` hook enforces them, but **only in build-agent context** — Ralph's `run.sh` exports `SOLO_BUILD_AGENT=1`, which propagates to the build agent's `claude` process and its hooks; the hook soft-passes when that env var is absent. This scoping is load-bearing: the denylisted paths (`docs/.solo-config.json`, `.cascade/run-state.json`, `.cascade/manifests/*`, …) are exactly the files the cascade's own orchestrating stages are *required* to write (`/onboard`, `/config`, `/build --finalize`, every stage's manifest seal). Those stages run in the founder session without the env var and write freely; global enforcement would block the cascade from running itself. In build-agent context the hook inspects **both** Write/Edit/MultiEdit `file_path` **and** Bash write-targets (redirection, `tee`, `cp`/`mv`, `dd of=`, `sed -i`, `truncate`), since the agent runs with `--dangerously-skip-permissions` and a shell redirection would otherwise bypass a tool-only check. The denylist is itself denylisted — a build agent cannot grow its own write surface. Recovery on a block: make the change from the founder session via the responsible orchestration stage (which is the authoritative writer), not from inside the build loop.

**2. Soft-check — reviewer-stance inside `/review`.** `/review` surfaces write-discipline findings as auditor-voice observations per `auditor-stance.md`: state the violation as fact (e.g. "the change writes to `docs/.solo-config.json` from /build context"), name the locus, and do not append LGTM closures. The soft-check does **not** block — it raises a `DONE_WITH_CONCERNS` if the surfaced write is ambiguous (e.g. legitimate cleanup that happens to touch a guarded path). The founder reads the finding and decides whether to address inline, file a v0.2.x issue, or override.

Allow-list semantics — declaring upfront the exhaustive set of paths a skill may touch — are explicitly out. Skills produce artifacts whose paths are spec-determined; an allow-list would freeze that surface at design-time and force allow-list amendments for every legitimate spec evolution. Denylist + reviewer-stance leaves the surface open and protects only what is provably load-bearing.
