---
name: retro
description: Retrospective document generator. Task-invoked when a parent feature completes — by /verify on a full acceptance pass, or by /wrap when the last child finishes and /verify is disabled — gated on workflow.auto_retro. Compiles cycle-time, what-went-well, what-went-wrong, patterns, and followups into a Linear retrospective document. Optionally mints followup tickets per workflow.followup_tickets. Reachable via /status drill-down. Not user-invoked in normal operation. Manual override `/retro <MARKER>-N` for debugging or re-generation.
---

# retro

Compiles the retrospective when a parent feature completes. Reflection artifact, not interactive. References rules: `naming.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`.

## Trigger

Task-invoked (per audit decision #9 — explicit Task-tool chaining, not a state-transition hook):
- by `/verify` on a full acceptance pass, when `workflow.auto_retro = true`;
- by `/wrap` when the last child completes AND `workflow.verify = false` AND `workflow.auto_retro = true`.

Manual override: `/retro <MARKER>-N` — re-generate the retrospective, or generate one when `workflow.auto_retro = false`.

## Behavior

1. **Load full parent history:** parent ticket, all children, spec markdown, four-hat doc, plan review doc(s), all ADRs filed during the cascade, all /wrap session summaries.

2. **Compute cycle metrics:**
   - Time from /specify (ticket creation) to parent Done.
   - Time from cascade-complete to first child start.
   - Time per child from start → Done.
   - Wave overlap (parallel Wave 1 wall-clock vs sum-of-children).
   - Total review iterations.
   - Halt count during the /specify → build chain.

3. **Compile sections** in auditor voice per `auditor-stance.md` — what-went-wrong is auditable, not blame; state findings as facts:
   - **What went well:** ACs passing first try (per /wrap summaries); autonomous fixes that held (per the /review doc); ADRs auto-filed and not subsequently reversed.
   - **What went wrong:** spec-halts surfaced (per halt-cards); iteration loops at cap or stability; manual interventions during build (per /wrap halts, /build halt-cards).
   - **Patterns:** novel decisions (ADRs); architectural choices forced by the build that should propagate to the next spec.
   - **Followups:** TODOs surfaced during build that didn't make it back into the spec; refactor candidates noted in commits.

4. **Write the retrospective document** `[<MARKER>-DOC-NNNN] retro: <MARKER>-N <title>` per `naming.md` — NNNN allocated per `counter-allocation.md` (scan Linear for the next `doc` value). Four sections + a cycle-metrics header. Single write per `write-discipline.md`.

5. **Link from the parent ticket:** add a line to the parent's Artifacts section — "Retro: [<MARKER>-DOC-NNNN]". Single write, batched same-turn with step 4 where the API allows.

6. **Create followup tickets** — only if `workflow.followup_tickets = true` (see `commands/config.md`). For each item in the Followups section:
   - Create a ticket in the `Backlog` project.
   - Title: `[<MARKER>] followup: <one-line summary>` per `naming.md` ticket-title convention.
   - Label: `type:followup` (a `type:*` label, distinct from the `scope:*` state machine in `scope-labels.md` — followup tickets carry no `scope:*` label).
   - Description: extracted context from the retro + a link to the parent retro doc.
   - `relatedTo`: the parent ticket (<MARKER>-N).

   Batched same-turn per `write-discipline.md`, after the retro doc exists so the links resolve. If `workflow.followup_tickets = false`, the Followups section stays as prose in the retro doc — the founder triages manually.

## Same-turn write rules

Per `write-discipline.md`:
- Retro document creation: single write.
- Parent description update (Artifacts link): single write.
- Followup tickets (if enabled): batched same-turn, after the retro doc exists so links resolve.

## Outputs

| Artifact | Location |
|---|---|
| Retrospective document | `[<MARKER>-DOC-NNNN] retro: <MARKER>-N <title>` |
| Followup tickets (if enabled) | `Backlog` project, label `type:followup` |
| Parent description link | Parent ticket, Artifacts section |

## Completion status

Per `completion-status.md`:

- `DONE` — retro doc written; parent description linked; followup tickets created (if `workflow.followup_tickets = true`).
- `DONE_WITH_CONCERNS` — retro doc written but with reduced fidelity: missing /wrap session summaries (some children skipped /wrap or commented outside the canonical format); no halt-cards or autonomous-fix records to compile from; cycle metrics partial because of missing timestamps.
- `BLOCKED` — does not block. /retro is best-effort compilation; missing data fills with "—" in the retro sections rather than halting.
- `NEEDS_CONTEXT` — parent ticket not in Done state at invocation (defensive — the caller should ensure it); parent ticket missing entirely; Linear MCP unreachable for `doc`-counter scan per `counter-allocation.md`.

## Chains

None. Terminal. Reachable via /status drill-down.

## Notes

**Why /retro stays a skill** (audit "Skills that stay skills" list). /retro is a compilation skill with real logic — history load, metric computation, section synthesis, conditional ticket minting. It is not a thin deterministic action and not a specialist invoked by another skill; it stays a skill that /verify and /wrap Task-invoke.

**Task-invoked, not auto-fired.** Pre-extraction /retro "auto-fires on parent → Done" via a Linear state transition. Per audit decision #9 (no hooks in v0.1; explicit Task-tool chaining), /retro is Task-invoked — by /verify on a full pass, or by /wrap when /verify is disabled. The `workflow.auto_retro` knob gates whether that Task-invocation happens; with it `false`, /retro is manual-only.

**Cycle metrics are most actionable over time.** After 5–10 features, patterns emerge. v0.1 records; v0.2 may aggregate across retros.

**What-went-wrong is auditable, not blame** — per `auditor-stance.md`. ADR-reversal halts, test failures during /wrap, scope-breach catches all surface here as facts with loci, not as criticism.

**The Followups section is the most likely to be actioned.** TODOs and refactors that emerged during build but didn't fit the spec — captured here, they become future /specify candidates. The `workflow.followup_tickets` knob decides whether they're auto-minted as Backlog tickets or left as prose for manual triage.

**Auto-filed ADRs** (`Status: Accepted-Autonomous`) are listed for retroactive ratification. A v0.2 sweep skill can promote them to `Accepted` after retro review.

## Open questions (deferred to v1.1+)

- **Cross-retro aggregation.** v0.1 records per-feature metrics; v0.2 may aggregate trends across retros (cycle-time drift, recurring halt types).
- **Halt-messages pattern coverage for /retro.** /retro does not halt (best-effort compilation), so it owes no halt-card patterns to `[SOL-TPL] halt-messages.md`. Its only non-`DONE` exits are `DONE_WITH_CONCERNS` (reduced fidelity, surfaced in the retro doc itself) and `NEEDS_CONTEXT` (caller-side defensive). No template growth needed.
- **Followup-ticket dedup.** If /retro runs twice on the same parent (manual re-generation), step 6 would mint duplicate followup tickets. v0.1 leaves this to founder care; v1.1 could check `relatedTo` for existing `type:followup` tickets first.
