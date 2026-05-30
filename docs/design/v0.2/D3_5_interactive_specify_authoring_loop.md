# D3.5 — Interactive `/specify` authoring loop

**Status:** Design (v1 — 2026-05-30). Drives a follow-on `specify/SKILL.md` amendment; not yet wired.
**Phase:** 3 (Specification).
**Resolves:** SOL-133 (grill-me elaboration before four-hat) and SOL-132 **part B** (orchestrator + human-in-the-loop gates around four-hat). The two were filed against the same `/specify` region and SOL-133 records "Relationship to SOL-132 … Sequence/merge intentionally"; this record designs them as one loop.
**Builds on:** SOL-132 **part A** (landed: `four-hat-objection-coverage.py` is now advisory-only and guards `stop_hook_active`, so four-hat subagents reliably terminate). This record assumes that fix is in place.
**Relates:** D2.3 (four-hat review semantics), D3.1 (decomposition negotiation), D3.4 (`spec.*` gates), `.claude/skills/specify/SKILL.md`, `.claude/agents/four-hat-*.md`, `.claude/agents/clarify-walker.md`.

## Problem

`/specify` today drafts the spec almost entirely from discovery + research outputs and runs four-hat on that thin draft, with the only deep human input arriving *after* four-hat via a light clarify-walker pass. Two consequences, one per ticket:

- **SOL-133.** Four-hat critiques a sketch, not a real spec; user journeys, per-feature behaviour, and design/UX detail are thin at seal. Specs look complete but lack buildable detail.
- **SOL-132 part B.** Four-hat completion was enforced by a termination-blocking `SubagentStop` hook (the cause of the multi-hour hangs; part A removed the block). Even with termination fixed, the founder has no say over *which* findings get incorporated and never sees the synthesized critique before it is written.

Both changes inject human-in-the-loop interaction into the same `draft → four-hat → seal` stretch. Designing them separately risks two incompatible HITL structures in one file. This record defines a single loop.

## Decision — the target flow

The `/specify` body becomes the following sequence. Steps marked **(new)** are introduced here; the rest are the current steps, repositioned.

| # | Step | Change |
|---|------|--------|
| 1 | Load context (north-star, constitution, codebase-map, ADRs, research summaries, framing ticket) | unchanged |
| 2 | Draft **v1 spec — the end state** at `docs/specs/NNNN-<slug>/spec.md` | reframed: an explicit first full pass, not the sealed draft |
| 3 | **Grill-me elaboration phase** | **(new)** — §A |
| 4 | **Progressive presentation + founder confirmation** (Gate E0) | **(new)** — §B |
| 5 | Failing-test seed authoring (the current §3.1–§3.7 machinery) | repositioned after elaboration so the seed is authored against the *elaborated* AC list |
| 6 | **Orchestrated four-hat dispatch** + completion confirmation | four-hat redesigned — §C |
| 7 | **HITL Gate 1 — pre-synthesis finding selection** | **(new)** — §D |
| 8 | **Synthesis** of the founder-confirmed finding set (orchestrator-side) | **(new)** — §E |
| 9 | **HITL Gate 2 — post-synthesis review** | **(new)** — §F |
| 10 | Resolve objections (Incorporate / Defer / Reject) over the confirmed, synthesized set | repositioned; consumes Gate-1/Gate-2 output |
| 11 | Clarify-walker — **residual-gap pass only** | reconciled — §G |
| 12 | Slug derivation | unchanged |
| 13 | Seal-time gate evaluation + manifest write (current §8.1–§8.7) | unchanged logic; renumbered |

The load-bearing reorder: **deep human elicitation moves ahead of four-hat** (steps 3–4), and **founder control over four-hat output moves into the loop** (steps 7 and 9). Four-hat now critiques a detailed, founder-confirmed spec, and the founder curates the critique before it is resolved.

## A. Grill-me elaboration phase (step 3)

After the v1 draft, `/specify` enters a relentless interview to raise the spec to buildable feature- and design-level detail. The engine is the `grill-me` pattern, with these operative mechanics (all are SOL-133 acceptance criteria):

- **One question at a time.** No multi-question dumps.
- **Recommend an answer for every question.** The founder confirms or overrides; they are not authoring from a blank page.
- **Walk the decision tree dependency-ordered.** Resolve upstream decisions before the ones that depend on them. Each answer may open or prune downstream branches.
- **Explore before asking.** If a question is answerable from the codebase, existing specs, ADRs, or discovery/research outputs, resolve it from those sources instead of spending a founder question.
- **Relentless until shared understanding.** The loop terminates when the spec carries buildable feature- and design-level detail — not after a fixed question count.

Scope of the interview: *what* features exist, *how* each should behave, edge/error cases, and the **design/UX** dimension. Design/UX answers populate the spec's **Design & UX** section (primary flow, key screens, customer journey, edge/error states) with real founder-sourced content — never placeholders.

After each answer (or a small batch), `/specify` edits `spec.md` in place so the spec is always the live state of the interview.

`grill-me` is not installed as a skill in this repo; its mechanics are inlined into `/specify` per the verbatim definition on SOL-133. The closest installed analog, `superpowers:brainstorming`, is a sibling pattern, not a substitute — the elaboration phase is `/specify`-owned.

## B. Progressive presentation + founder confirmation — Gate E0 (step 4)

Once elaboration reaches shared understanding, `/specify` presents the improved spec back **progressively**, never as one wall of spec:

1. **High-level scope** first (Problem statement + Scope boundary).
2. **Each feature** (or, for non-feature shapes, the end-solution shape) in turn.
3. **Each iteration / slice** in detail.

Chunking is keyed off the decomposition strategy confirmed at step 1: `walking-skeleton` → slices; `capability-cluster` → capabilities; `api-boundary` → contract surfaces; `refactor-spike` → the invariance target; `hybrid` → per-child shape. The founder reviews and refines each part in turn.

**Gate E0** is the founder's explicit confirmation that the elaborated spec is correct. Four-hat (step 6) does not run until E0 passes. E0 is a conversational gate, not a `spec.*` seal gate — it has no manifest predicate; it controls flow only.

## C. Orchestrated four-hat dispatch (step 6)

`/specify` (the orchestrator) fires the four `four-hat-*` subagents in parallel via the Task tool, exactly as today, then **confirms completion orchestrator-side**:

- The orchestrator waits for all four subagents to terminate and reads each subagent's `## Findings` transcript / manifest.
- **Objection/finding completeness is verified by the orchestrator** reading the transcripts — *not* by a termination-blocking `SubagentStop` hook. Per SOL-132 part A, `four-hat-objection-coverage.py` is advisory-only: it records a triage note on a malformed transcript and exits clean; it can never veto termination. Completeness enforcement that previously (incorrectly) lived in the hook now lives here, where it belongs.
- If a hat's transcript is unreadable or empty, the orchestrator re-dispatches that single hat (bounded retry) rather than hanging.

This is the design intent behind SOL-132's "completion control lives in the orchestrator, not in a stop hook that vetoes termination."

## D. HITL Gate 1 — pre-synthesis finding selection (step 7)

Before any synthesis, the orchestrator shows the founder a **per-subagent summary** — each hat's findings in `auditor-stance` form (one finding per `{type, locus}`). The founder **selects which findings to address vs. skip**. Skipped findings are recorded with the founder's skip rationale (they are not silently dropped). Synthesis runs only over the founder-confirmed set.

The existing **scope-reduction guard** still applies: any finding that proposes dropping an AC is surfaced explicitly and confirmed one-by-one — a "skip" at Gate 1 may not silently drop an AC.

## E. Synthesis (step 8)

The orchestrator (the `/specify` skill itself) synthesizes the confirmed finding set into the four-hat document `[<MARKER>-DOC-NNNN] four-hat: <MARKER>-N <title>` (append-only, per `rules/naming.md`). Synthesis is "synergy" across hats: deduplicate overlapping findings, order by locus, and attach each to the AC/section it touches. Only confirmed findings enter; skipped findings are listed in a "Skipped (founder-confirmed)" subsection with rationale.

## F. HITL Gate 2 — post-synthesis review (step 9)

The founder is shown the **final synthesized report** and may request changes before it is written/sealed. Gate 2 loops back to step 8 (re-synthesize) or step 7 (re-select) on founder request; it proceeds to resolution (step 10) on founder approval. Like E0, Gate 2 is a conversational gate, not a manifest predicate.

## G. Clarify-walker reconciliation (step 11)

The grill-me phase (step 3) subsumes the *deep* elicitation that clarify-walker used to carry. **Decision: clarify-walker is retained as a residual-gap pass after four-hat, not removed.** Its job narrows to:

- gaps introduced *by* four-hat resolution (an Incorporate edit that opens a new question), and
- the strategy-conflict clarify question (the load-bearing step-3↔step-4 bridge in the current doc, per D3.1 §Negotiation protocol).

To avoid double-questioning, clarify-walker **skips any surface already resolved during step-3 elaboration.** The elaboration phase records resolved surfaces in the spec's Clarifications section; clarify-walker reads that section and only raises surfaces not already covered. This satisfies SOL-133's "no redundant double-questioning" AC.

## Resumability

The elaboration loop and the two HITL gates can span multiple turns, so `/specify --continue` must resume mid-loop. State persists in two places already owned by the cascade:

- **Spec body.** Because step 3 edits `spec.md` in place after each answer, the partial spec *is* the resumable state for elaboration.
- **`discovery: state`-style phase marker.** `/specify` records its current phase and gate in the run-state side-channel (`.cascade/run-state.json` plus the per-session snapshot used by PreCompact), so `--continue` re-enters at the right step (`elaborating` / `awaiting-E0` / `four-hat-dispatched` / `awaiting-gate-1` / `awaiting-gate-2`) rather than restarting. The four-hat document's append-only structure already preserves prior iterations.

<!-- 🤔 The exact field name/shape for the /specify mid-loop phase marker in run-state is left to the SKILL.md amendment; it should mirror the discovery: state research_depth pattern (SOL-131) rather than invent a new persistence mechanism. Founder to confirm the run-state schema addition. -->

## Implementation impact on `specify/SKILL.md`

This record is the design; the SKILL.md wiring is a **separate follow-on edit** (deliberately not bundled, because it is a fragile renumber of a 588-line, heavily cross-referenced file):

- Insert steps 3–4 (elaboration + E0) between the current step 2 (draft) and the current step 3 (failing-test seed); renumber the seed block §3.1–§3.7 accordingly.
- Replace the current step 4 (four-hat) with steps 6–9 (orchestrated dispatch + Gate 1 + synthesis + Gate 2).
- Narrow the current step 6 (clarify) to the residual-gap pass per §G.
- Renumber the seal block (current §8.1–§8.7) and reconcile every internal "step N" reference — note the file *already* carries stale "step 4 (clarify-walker)" references that this amendment should fix in the same pass.
- Update the `/Chains` section: the Group-D within-group transition narrative gains the elaboration and HITL gates; the four-hat fan-out description gains the orchestrator-side completion check (replacing any reliance on the `SubagentStop` hook for completeness).
- Update the frontmatter `description` to mention the interactive elaboration loop.

No `rules/*.md` change is required. No new gate is added to the `spec.*` seal set — E0, Gate 1, and Gate 2 are conversational HITL gates, not manifest predicates.

## Acceptance-criteria mapping

**SOL-133:**
- v1 draft then grill-me elaboration → steps 2–3.
- one question at a time + recommended answer each → §A.
- decision-tree dependency-ordered → §A.
- explore-instead-of-ask when answerable → §A.
- relentless until shared understanding → §A.
- progressive presentation (scope → features → slices) → §B.
- explicit founder confirmation before four-hat → Gate E0 (§B).
- four-hat runs on the confirmed detailed spec → step 6 gated on E0.
- clarify-walker interaction reconciled, no double-questioning → §G.
- mid-elaboration resumable via `--continue` → §Resumability.

**SOL-132 part B:**
- four hats dispatched in parallel and all reliably terminate → §C (relies on part A, landed).
- completeness verified orchestrator-side, not via a termination-blocking hook → §C.
- pre-synthesis per-subagent summary; founder selects address/skip → Gate 1 (§D).
- synthesis over only confirmed findings → §E.
- founder sees final synthesized report and can request changes before seal → Gate 2 (§F).
- no Stop/SubagentStop hook can cause non-termination → satisfied by part A (guard added to `four-hat-objection-coverage.py` and `stop-orchestrator.sh`).

## Open questions

- Run-state schema for the `/specify` mid-loop phase marker (see 🤔 above) — resolve at SKILL.md amendment time.
- Bounded-retry policy for a hat whose transcript is unreadable (§C): retry count and fallback. Proposed default: one re-dispatch, then surface the hat as "incomplete" at Gate 1 for founder decision. Founder to confirm.
- Whether Gate 1 and Gate 2 should be collapsible into a single review for small specs (e.g. walking-skeleton with < N findings) to reduce founder friction. Deferred to post-first-use.
