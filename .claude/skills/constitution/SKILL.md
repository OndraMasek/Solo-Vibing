---
name: constitution
description: Authors and amends docs/constitution.md — the project's governing principles document loaded as context by /specify, /plan, and /review. Task-invoked by /discovery on approve exit (always, no config knob) — seed mode writes v1.0.0 from north-star + idea-brief. The constitution is non-optional: /specify hard-requires it as a precondition. Manual invocations: "/constitution" shows current; "/constitution amend <topic>" proposes a section edit (semver-bumped per the classification rubric); "/constitution reseed" rewrites from current north-star (MAJOR bump). Semantically versioned (MAJOR.MINOR.PATCH). Current at docs/constitution.md, prior versions append-only at docs/constitution/archive/v<semver>-<date>.md. Never edits in place.
---

# constitution

Authors and amends `docs/constitution.md`. Semantically versioned, append-only history. Read as context by every downstream cascade stage. References rules: `naming.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`. No agent invocation — read-and-amend work.

## Trigger

- Cascade: Task-invoked by /discovery on approve exit per audit decision #9 (chaining via Task tool, not labels). Runs seed mode. Non-optional — no config knob gates this.
- User: "/constitution", "constitution show" — render current. No writes.
- User: "/constitution amend <topic>" — propose section edit; produces a semver-bumped version.
- User: "/constitution reseed" — rewrite from current north-star (rare; MAJOR bump by definition).

## Behavior

### Seed mode (Task-invoked by /discovery approve exit)

Non-optional in v0.1 — no config knob gates this. The constitution is a hard precondition for /specify; /discovery's approve exit always Task-invokes /constitution.

1. **Preconditions** (any failure halts with `NEEDS_CONTEXT` per `completion-status.md`; halt-card per `docs/templates/halt-messages.md`).
   - `docs/product/north-star.md` exists.
   - Latest `docs/discovery/idea-brief-v<N>.md` exists.
   - Linear MCP is reachable for `doc`-counter scan per `counter-allocation.md` (used to allocate the constitution doc's NNNN).

2. **Load** north-star + latest idea-brief.

3. **Draft `docs/constitution.md` v1.0.0** with these sections, populated from north-star + idea-brief content:

   ~~~
   # <Project name> — Constitution

   > Version: 1.0.0
   > Created: YYYY-MM-DD
   > North-star: docs/product/north-star.md

   ## Mission

   <one-paragraph project vision derived from north-star>

   ## Core principles

   * **TDD by default.** Every build session opens with failing tests, not code.
   * **Vertical slices over horizontal layers.** Each child ticket produces user-visible behavior unless infrastructure-only justified (see decomposer agent's classification rubric).
   * **Spec-driven.** Code-Claude refuses tickets without `scope:sealed` per `scope-labels.md`. Only /plan sets this label (and /verify-fix as the sole exception).
   * **Halt over guess.** When the cascade can't converge, halt with options — never improvise spec changes. `auditor-stance.md` governs the voice of halts.

   <project-specific principles inferred from idea-brief — augment with 2–4>

   ## Process rules

   The authoritative process rules live in `.claude/rules/`. The constitution does not duplicate their content — when a rule changes, the rule file is canonical and this section needs no amendment. Pointers:

   * `.claude/rules/naming.md` — IDs, slugs, file paths, marker resolution.
   * `.claude/rules/counter-allocation.md` — NNNN allocation protocol (scan-then-claim).
   * `.claude/rules/scope-labels.md` — label state machine, transition ownership, refusal protocol.
   * `.claude/rules/completion-status.md` — `DONE` / `DONE_WITH_CONCERNS` / `BLOCKED` / `NEEDS_CONTEXT` contract.
   * `.claude/rules/write-discipline.md` — same-turn batching, partial-failure handling.
   * `.claude/rules/auditor-stance.md` — finding voice, locus, severity, hypothesis marking.

   ## Architectural constraints

   <derived from idea-brief tech stack + risks — e.g. allowed runtimes, banned patterns, performance budgets, accessibility floors. If idea-brief lacks specifics: stub with "<TBD — populate as ADRs accumulate>".>

   ## Decision-making

   * **File an ADR when:** introducing a new dep, choosing between architectural options, changing a previously-recorded decision.
   * **Halt to founder when:** ADR-reversal detected; dep fails the four-condition low-stakes test; parent undecomposable (decomposer agent flagged); failing-test seed incomplete; constitution-check fails; spec is incomplete.
   * **Auto-file ADR when:** /review's check h (new-dep scan) passes the four-condition test — language-ecosystem standard utility, no runtime architectural lock-in, not a peer-competitor to an existing dep, project has ≥1 prior ADR.

   ## Out of scope

   <from idea-brief — explicit non-goals>

   ## Amendment process

   * **Never edit `docs/constitution.md` in place.** Use `/constitution amend <topic>` — produces a new semver-versioned file, archives previous.
   * Each amendment requires founder confirmation before write.
   * Amendments are not retroactive — past specs and ADRs are not re-evaluated against new principles.

   ## Amendment log

   * v1.0.0 (<date>): initial seed from north-star + idea-brief.
   ~~~

4. **Same-turn write batch** per `write-discipline.md`:
   - Filesystem: `docs/constitution.md`.
   - Filesystem: archive copy at `docs/constitution/archive/v1.0.0-<YYYY-MM-DD>.md` (first version archived alongside writing — symmetrical with amend mode's archive-before-write).
   - Linear: create document `[<MARKER>-DOC-NNNN] constitution: v1.0.0` per `naming.md` (4-digit DOC prefix; type encoded in title) linking to the markdown.

### Amend mode

`/constitution amend <topic>`:

1. **Preconditions.** `docs/constitution.md` exists. Missing → `NEEDS_CONTEXT`: "no constitution to amend; run seed mode (auto from /discovery approve, or `/constitution reseed`)."
2. **Load** current `docs/constitution.md`. Read current semver from version header.
3. **Identify target section** based on `<topic>` (Core principles, Process rules, Architectural constraints, etc.). If unclear → `NEEDS_CONTEXT`: "which section should this amendment target?"
4. **Propose edit:** show current section content + proposed change. Wait for founder confirmation. Decline → `BLOCKED` (no write).
5. **Classify the bump** per §Versioning below. If classification is ambiguous (an edit that clarifies wording but also subtly changes a threshold), surface the ambiguity and ask the founder to confirm. Ambiguous-then-confirmed → `DONE_WITH_CONCERNS`.
6. **Same-turn write batch** per `write-discipline.md` on confirmation:
   - Archive current → `docs/constitution/archive/v<current-semver>-<YYYY-MM-DD>.md`.
   - Write new `docs/constitution.md` with bumped semver and edit applied; update version header and "Last amended" date.
   - Append amendment-log line at bottom: `- v<new-semver> (<date>): <bump-type> — <topic> — <one-line summary>`.
   - Update Linear constitution document title and content to reflect new semver. New title: `[<MARKER>-DOC-NNNN] constitution: v<new-semver>` per `naming.md` (same doc; title updated, NNNN preserved).

### Versioning

Semantic versioning (MAJOR.MINOR.PATCH). Amend mode classifies the bump from the nature of the edit:

- **MAJOR (X.0.0):** removes a Core principle, reverses a Process rule, changes the label state machine, alters the iteration cap, or changes decision-making thresholds. Anything that invalidates downstream specs, ADRs, or established conventions. Reseed mode is MAJOR by definition.
- **MINOR (Y.Z.0 → Y.(Z+1).0):** adds a new Core principle, adds an Architectural constraint, expands "Halt to founder when" or "Auto-file ADR when" triggers, adds a new top-level section. Purely additive; existing specs and ADRs remain valid.
- **PATCH (Y.Z.W → Y.Z.(W+1)):** clarifies wording, fixes typos, expands examples, splits one rule into two equivalent ones, repairs broken links. No semantic change to any rule, principle, or threshold.

The bump determines downstream impact. MAJOR amendments deserve a /retro line during the next cycle so the project notices the policy shift. MINOR and PATCH are silent.

### Show mode

`/constitution` or `/constitution show` → render current `docs/constitution.md` in chat. No writes. `DONE`.

### Reseed mode

`/constitution reseed` (rare — used when north-star has drifted significantly):

1. Confirm with founder: "This will rewrite the constitution from current north-star. Current v<current-semver> archives; new version will be v<MAJOR+1>.0.0. Continue?" Decline → `BLOCKED`.
2. On confirmation, run Seed mode against current `docs/product/north-star.md`, writing v<MAJOR+1>.0.0. Same-turn write batch per Seed mode step 4.

## Outputs

| Artifact | Location |
|---|---|
| Current constitution | `docs/constitution.md` |
| Historical versions | `docs/constitution/archive/v<semver>-<date>.md` |
| Linear document | `[<MARKER>-DOC-NNNN] constitution: v<semver>` per `naming.md` |
| Amendment log | Bottom of current `docs/constitution.md` |

## Completion status

Per `completion-status.md`. v0.1 mappings:

- `DONE` — seed wrote v1.0.0; amend/reseed wrote new version with confirmed bump and unambiguous classification; show rendered.
- `DONE_WITH_CONCERNS` — new version written but architectural-constraints section still has `<TBD>` stubs (seed); amend bump classification was ambiguous and founder confirmed under uncertainty.
- `BLOCKED` — founder declined the proposed edit at the confirmation gate (no write performed); reseed declined; partial-failure on the same-turn batch (filesystem succeeded, Linear API down → marker file dropped per `write-discipline.md` §Partial failure with sync-retry hint).
- `NEEDS_CONTEXT` — `docs/product/north-star.md` missing for seed/reseed mode; `docs/constitution.md` missing for amend mode; idea-brief missing for seed mode; ambiguous `<topic>` in amend mode without resolvable section target; Linear MCP unreachable for `doc`-counter scan per `counter-allocation.md`.

## Chains

- **Seed mode** is Task-invoked by /discovery's approve exit per audit decision #9. /constitution is terminal (no further cascade) — sit-time on the v1.0.0 constitution is healthy.
- **Amend / reseed / show**: terminal. No chain.

## Notes

**Constitution is *read* by the cascade.** /specify (step 1 context load), /plan (decomposition principles), /review (check thresholds and routing rules, including check j constitution-check), /retro (what-went-well includes constitution adherence). Without it, downstream skills fall back to defaults — they don't halt.

**Versioning pattern mirrors ADRs:** never edit in place; always write a new version and archive the prior. Semver makes downstream impact legible — MAJOR tells future readers something load-bearing changed; PATCH tells them nothing important did.

**Amendment process is intentionally heavy** (founder confirmation, semver classification) because the constitution is load-bearing. Easy amendments cause silent drift; high friction enforces deliberateness.

**Why Task-invoke from /discovery, not config-only auto-fire.** Per audit decision #9, chaining is explicit via the Task tool — labels and state transitions are not triggers in v0.1 (no hooks). The constitution-seed Task-invocation from /discovery's approve exit is unconditional in v0.1 — no config knob gates it, because /specify hard-requires the constitution and skipping the seed step would only push the same halt downstream.

**Process rules section overlaps `scope-labels.md` and other rules.** This is deliberate: the constitution surfaces rules for downstream context (skill reads `docs/constitution.md` at start; rules at `.claude/rules/` also auto-load). When the constitution and a rule disagree, **the rule wins** — the constitution's process-rules section must be re-synced via amend mode when a rule changes. This is a known v1.1 polish item.

**Architectural constraints section is the most volatile** — fills out as ADRs accumulate. v1.0.0 typically stubs this with `<TBD>` and gets fleshed out by MINOR amendments over the first 5–10 ADRs.

**Constitution is not project-specific deep technical content** (that's spec markdown). It's principles + non-negotiables that apply to every spec.

**Read order at /specify start:** north-star → constitution → ADRs filtered by scope relevance → top-3 research summaries. Constitution shapes how the spec is structured; ADRs constrain technical choices within it.

## Open questions (deferred to v1.1+)

- **Constitution-vs-rule drift detection.** When `.claude/rules/` content updates, the constitution's Process rules section can drift out of sync. v1.1: a constitution-check helper that diffs the surfaced summaries against current rule content and proposes a PATCH amendment when drift is detected.
- **Per-section amendment audit trail.** Amendment log records bump + topic + summary but not the actual diff. v1.1: per-amendment diff snapshots under `docs/constitution/archive/`.
- **Multi-stakeholder amendments.** v0.1 is solo-founder; multi-contributor amendment workflow (proposal → review → vote/approval) is v0.2+ territory.
- **Cascade-wide read-rule for constitution version mismatch.** When a downstream skill loads a constitution at a version newer than the spec it's working on, surface as a `DONE_WITH_CONCERNS`. Currently silent. v1.1.
