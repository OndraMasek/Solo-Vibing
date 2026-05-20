# Halt-card appends — Child 0001-C scope

**Status:** Patch-ready append-block. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing`.

**Scope:** the four halt codes Child 0001-C's hooks reference that are NOT already covered by v0.1 nor by Child A's `halt-messages-append.md` (per Child 0001-B continuation 1 Surfaced item #4 + this session's surfaced items). The executing apply session folds these stanzas into `docs/templates/halt-messages.md` alongside Child A's batch.

**Stanzas authored here:**

  1. `§kill-received-remote` — surfaced by `stop-orchestrator-hook.md` (this session); referenced in Child 0001-B continuation 1 `/build` amendment §Interaction with sidecar commands.
  2. `§manual-halt-pending` — surfaced by `stop-orchestrator-hook.md` (this session); referenced in Child 0001-B continuation 1 `/build` amendment §Interaction with sidecar commands.
  3. `§compact-deferred-unsafe` — surfaced by `precompact-safe-boundary-hook.md` (this session); novel.
  4. `§pyramid-shape-violation/shape-tampering` (sub-case stanza) — refines the parent `§pyramid-shape-violation` card in Child A's append with the specific `shape-tampering` sub-case the pyramid-tampering hook surfaces.

Other halt codes referenced by Child 0001-C's scripts but NOT requiring new cards (already covered by Child A's append or v0.1):

  - `§provenance-chain-broken` (covered by Child A).
  - `§four-hat-incomplete` and `/objection-entry-malformed`, `/priming-text-missing`, `/objections-section-missing`, `/seal-line-missing`, `/transcript-absent`, `/transcript-malformed`, `/unknown-hat`, `/no-final-assistant-message` (the parent `§four-hat-incomplete` is in Child A; the sub-cases are diagnostic refinements rendered in the existing card's body).
  - `§four-hat-objections-unresolved` (covered by Child A).
  - `§session-reset-required` (covered by Child A per F-2's full halt-card surface).

---

## Append-block content

These stanzas fold into `docs/templates/halt-messages.md` alphabetically per the v0.1 convention (alphabetical by halt code with `§` stripped).

### `§compact-deferred-unsafe`

```markdown
## §compact-deferred-unsafe

**When fired.** PreCompact detected mid-cascade activity — one or more entries
in `cascade:run-state.active_stages[]` with unsealed manifests. The auto-compact
is blocked; the cascade continues; the next safe-boundary check will retry.

**Diagnostic context.** The list of active stages, the trigger (`manual` or
`auto`), the current `compact_cycles` count.

**Recovery.** None required — the deferral is intentional. The compact will
fire automatically when the cascade reaches the next safe boundary (typically
within minutes, at most one Ralph iteration). If the cascade runs out of context
before reaching a safe boundary, a manual `/compact` at a safe boundary will
succeed.

If deferrals stack and `compact_cycles` rises to 2 without ever reaching a safe
boundary, the cascade transitions to `§session-reset-required` per D2.2 §Compact
mechanics's max-2-cycles rule. The transition is intentional; context signal
has degraded enough that re-verifying against filesystem evidence is cheaper
than continuing.
```

### `§kill-received-remote`

```markdown
## §kill-received-remote

**When fired.** A sidecar `/build-kill <ticket>` invocation has set
`cascade:run-state.kill_in_progress = "<ticket>"` AND incremented `queue_version`.
The Group F chat (Claude Code) was running Ralph for the same ticket when the
Stop-hook orchestrator read the flag at the next safe boundary.

**Diagnostic context.** The active ticket, the kill timestamp (from
`cascade:run-state.kill_initiated_at`), the originating chat surface
(`cascade:run-state.kill_initiated_from`, typically `"sidecar"` or `"chat-Claude"`).

**Recovery.** None required for the cascade — the kill was intentional. The
orchestrator clears `cascade:run-state.kill_in_progress`, removes the ticket
from `active_stages[]`, and the founder picks up either by:

  - Opening a new chat for the next queued ticket (the `queue_version` increment
    means the killed ticket is no longer in the queue).
  - Running `/cascade-halt` to halt the cascade entirely (sets `manual_halt`).
  - Running `/build <ticket> --resume` if the kill was a mistake (re-queues
    the ticket; `queue_version` increments again).

The Stop hook itself takes no recovery action beyond clearing `kill_in_progress`
and surfacing this card. The cascade's continuation is the founder's next
deliberate input.
```

### `§manual-halt-pending`

```markdown
## §manual-halt-pending

**When fired.** A `/cascade-halt` invocation (founder-initiated; not
`/build-kill`) has set `cascade:run-state.manual_halt = "<ticket-or-marker>"`.
The Stop-hook orchestrator read the flag at the next safe boundary.

**Diagnostic context.** The active ticket or marker, the halt timestamp (from
`cascade:run-state.manual_halt_at`), the halt reason if the founder supplied
one via `/cascade-halt --reason="<text>"` (`cascade:run-state.manual_halt_reason`).

**Recovery.** The halt is intentional. To resume the cascade:

  - Run `/cascade-resume` (or `solo-cascade resume` per D4.6 v1.1) to re-derive
    the chat-end card and continue.
  - Clear the flag manually via direct edit to `.cascade/run-state.json` if
    the halt should be retired without resumption (advanced; rarely needed).

The Stop hook itself takes no recovery action beyond surfacing this card and
preserving the `manual_halt` flag. The flag persists until the founder runs
`/cascade-resume` or clears it manually; the next chat opened detects it
during paste-verification (per D2.3 v1.3 §Handoff verification predicate)
and re-surfaces this card.

**Interaction with `kill_in_progress`.** The two flags are mutually exclusive
by convention; `/cascade-halt` errors out if `kill_in_progress` is non-null
(founder must `/build-kill` first or wait for the kill to complete). v0.2 ships
two-step; v0.2.x may chain per F-Usr-2's queued amendment.
```

### `§pyramid-shape-violation/shape-tampering` (sub-case stanza)

This is a sub-case refinement of `§pyramid-shape-violation` (the parent card lives in Child A's `halt-messages-append.md` per the F-2 fix's full halt-card surface). The refinement adds the specific tampering sub-case diagnostic, appended below the parent card's body.

```markdown
### Sub-case: `/shape-tampering`

**When fired.** A `Write` or `Edit` tool call attempted to mutate the spec's
`Strategy:` field or `Failing-test seed` tag set in a way that violates the
sealed parent manifest's `pyramid_shape`. The PreToolUse `pyramid-tampering.sh`
hook detected the mismatch and denied the tool call.

**Diagnostic context.** The file path of the spec under write, the parent
manifest path, the proposed strategy vs sealed strategy, the violating tag
set (`forbidden tag <X> present`, `required tag <Y> missing`, or
`tag <Z> not in required/optional set`).

**Recovery.** Two paths depending on intent:

  - **Re-tag the seed entries to match the sealed shape.** If the tampering was
    unintentional (e.g., the model proposed a `[contract]` test for a
    walking-skeleton strategy where `contract` is forbidden), re-tag the
    failing-test seed entries to use tags from the sealed `required` or
    `optional` sets.
  - **Unseal and re-seal under a new strategy.** If the strategy itself needs
    to change (e.g., the work has shifted from walking-skeleton to
    capability-cluster), run `/specify <MARKER>-N --unseal` to re-run the
    four-hat panel under the new strategy. The pyramid_shape will regenerate
    from the strategy → shape catalog in D3.2.

The hook is a pre-flight defense; the at-write gate inside `/specify` (Gate 1
per D3.2 §Downstream consumer touch-points) is the authoritative shape-check.
If the hook missed (e.g., MultiEdit conservatively allowed), the at-write gate
catches the violation at seal time.
```

---

## Apply-time placement

Per Child A's `halt-messages-append.md` apply convention (alphabetical by halt code with `§` stripped), the stanzas land in `docs/templates/halt-messages.md` at these alphabetical positions:

  - `§compact-deferred-unsafe` — between `§compact-*` and `§four-*` (likely between two existing entries from Child A).
  - `§kill-received-remote` — between `§hybrid-*` (if any) and `§linear-*`.
  - `§manual-halt-pending` — between `§linear-*` and `§pyramid-*`.
  - `§pyramid-shape-violation/shape-tampering` — sub-case of `§pyramid-shape-violation`, appended below the parent card's body.

The executing apply session reconciles exact placement against Child A's authored set.

---

## Cross-references

- **`stop-orchestrator-hook.md`** (this session) — `§kill-received-remote` and `§manual-halt-pending` source.
- **`precompact-safe-boundary-hook.md`** (this session) — `§compact-deferred-unsafe` source.
- **`pyramid-tampering-hook.md`** (this session) — `§pyramid-shape-violation/shape-tampering` source.
- **Child A `halt-messages-append.md`** — the batch this append-block folds into; contains parent `§pyramid-shape-violation`, `§provenance-chain-broken`, `§four-hat-incomplete`, `§four-hat-objections-unresolved`, `§session-reset-required` cards.
- **D2.3 v1.2 §Group F per-skill semantics** + four-hat review §F-Int-3 — the binding for `§kill-received-remote` mechanics.
- **D2.3 v1.2 §Manual halt protocol** — the binding for `§manual-halt-pending` mechanics.
- **D2.2 §Compact mechanics §PreCompact** — the binding for `§compact-deferred-unsafe`.
- **D3.2 §Downstream consumer touch-points** + §Halt conditions — the binding for `§pyramid-shape-violation/shape-tampering`.
