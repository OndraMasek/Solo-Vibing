---
name: start
description: Mark a child ticket as actively being built — transitions child Linear state Todo → In Progress, posts a session-start comment, surfaces the branch name as a copy-paste anchor. Invoked by /build at its preconditions step (Task tool). Also user-invokable manually for tracking work done outside /build (ad-hoc debugging). Counterpart to /wrap which closes the session. Fires on "/start <MARKER>-N-K", "start <MARKER>-N-K", "starting <MARKER>-N-K", "/s <MARKER>-N-K".
---

# start

Mark a child as actively building. Single-purpose. Pairs with /wrap to bookend the build-session window. References rules: `scope-labels.md`, `write-discipline.md`, `completion-status.md`, `naming.md`.

## Trigger

- Invoked by /build at its preconditions step via the Task tool (Todo → In Progress before Ralph spawns).
- User: "/start <MARKER>-N-K", "start <MARKER>-N-K", "starting <MARKER>-N-K", "/s <MARKER>-N-K" — manual, for tracking work done outside /build.

## Behavior

1. **Resolve child ticket from <MARKER>-N-K** per `naming.md` ticket-ID convention. Look up by Linear short identifier. Not found → `NEEDS_CONTEXT`: "<MARKER>-N-K not found in Linear. Check the identifier and retry."

2. **Validate child label and state** per `scope-labels.md`:
   - Label must be `scope:sealed` (set by /plan). Any other label → `BLOCKED` per `scope-labels.md` §Refusal protocol, citing observed vs expected: "<MARKER>-N-K is labeled `<observed>`, not `scope:sealed`. Only /plan-produced children can be started."
   - Linear state must be `Todo`. Non-Todo states get soft-warn paths, no write:
     - **In Progress** → "<MARKER>-N-K is already In Progress. Resume the existing session, or run /wrap first if abandoned." Return `DONE` (no-op is a valid completion).
     - **Done** → "<MARKER>-N-K is Done. Re-run /verify <MARKER>-N to re-evaluate, or /specify <MARKER>-N --unseal if scope changed." Return `DONE`.
     - **Cancelled / Backlog / Triage** → `BLOCKED`: "<MARKER>-N-K is in state `<observed>`. Move to Todo first or pick a different child."

3. **Transition Linear state** `Todo` → `In Progress`. Single Linear write per `write-discipline.md`.

4. **Post session-start comment on child ticket** (batched same-turn with step 3 per `write-discipline.md`):

   ~~~
   /start invoked. Session opening.

   * Branch: `<MARKER>-N-<slug>-K`
   * Parent: <MARKER>-N
   * AC count: <N>
   * Spec: `docs/specs/NNNN-<slug>/spec.md`
   ~~~

   Branch name follows `naming.md` §Branch names.

5. **Render confirmation in chat:**

   ~~~
   Started <MARKER>-N-K — `<MARKER>-N-<slug>-K`

   Spec: `docs/specs/NNNN-<slug>/spec.md`
   AC: <count> | Failing-test seed: <count>
   ~~~

   Branch name surfaced as a code-fence string for fast copy.

## Same-turn write rules

Per `write-discipline.md`: Linear state transition + session-start comment in a single same-turn batch.

## Outputs

| Artifact | Location |
|---|---|
| Child state | Todo → In Progress |
| Session-start comment | Child ticket comment |
| Branch name + spec path | Chat confirmation |

## Completion status

Per `completion-status.md`:

- `DONE` — child transitioned Todo → In Progress and session-start comment posted; OR child was already In Progress / Done and the no-op soft-warn was surfaced.
- `DONE_WITH_CONCERNS` — n/a (single-purpose; success or halt).
- `BLOCKED` — label is not `scope:sealed`; state is Cancelled / Backlog / Triage; Linear write failed (marker + sync-retry hint per `write-discipline.md` §Partial failure).
- `NEEDS_CONTEXT` — <MARKER>-N-K not found in Linear.

## Chains

None when user-invoked — terminal; the next action is the build session itself. When Task-invoked by /build, control returns to /build's preconditions step; a `BLOCKED` or `NEEDS_CONTEXT` from /start halts /build at the same status (no Ralph spawn) per `[SOL-SKILL] build`'s Task-invoke /start contract.

## Notes

**Why /start exists.** /status's "Building" view, /next's priority logic, and the cascade summary card all assume `In Progress` is a populated state. Before /start, that state was orphan — /wrap moved children Todo → Done in one step, skipping In Progress. /start is the missing transition.

**Why a command, not a skill.** Per audit decision #2, /start is a thin deterministic action — one state transition, one comment, one chat render. It is invoked by /build (Task tool) and occasionally by the founder; it carries no orchestration logic of its own.

**Single-purpose by design.** Does not start the build session, does not switch branches, does not run /map-codebase. Only marks Linear state and surfaces the branch as a copy-anchor.

**Soft-warn paths avoid double-writes.** Re-running /start on an already-In-Progress child is benign — remind the founder and return `DONE`. Re-running on Done redirects to /verify or unseal.

**Pairs with /wrap.** /start marks the window open; /wrap closes it (commit + push + state transition + parent-completion check). If the founder skips /start, /wrap still works — it accepts In Progress or Todo as source state — but /status's "Building" view stays empty during the session.

**v0.2 candidates:** optional `git checkout <branch>` in a repo context; batch-start a wave (`/start <MARKER>-N-1 <MARKER>-N-2`) for parallel sessions. v0.1 keeps it minimal — one child per invocation, no shell side-effects.
