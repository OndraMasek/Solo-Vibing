# D1 — Linear product layer

**Status:** Design (v2 — updated 2026-05-18 per founder feedback).
**Phase:** 1.
**Resolves:** F-10 (partially), founder's structural request from May 2026 design discussion ("technical architecture, data model, design, user journeys").
**Replaces:** Current Active / Backlog / Decisions / Sync Queue structure for consumer products. Framework's own Linear stays as-is — the framework is not a consumer product.

## Decision

Each consumer product (that the framework deploys to) uses a seven-element Linear structure:

| Element | Type | What it holds |
|---|---|---|
| **Product** | Linear project | North-star doc, target shape, end-state vision. Founder-authored at `/onboard`; cascade reads but doesn't write. **Status doc lives here as a document under Product.** |
| **Architecture** | Linear project | Technical-architecture doc, data-model doc, key ADRs. Cascade-maintained. |
| **Design** | Linear project | Design-system doc, user-journeys doc, UI asset references. Cascade-maintained for journeys/system; founder-supplied for asset uploads. |
| **Milestones** | Linear project | One issue per milestone. Each milestone is a `/plan`-able parent. Milestones map to "playable increments" (end-user products) or "API-boundary deliverables" (libraries) per the decomposition strategy. |
| **Status** | Linear document under Product project | "What works now / what's broken / next milestone." Updated at every cascade stage transition. The 30-second read. |
| **Backlog** | Linear project | Next-up tickets for the currently-active milestone. Not yet sealed. |
| **Done** | Linear project | Terminal `scope:built` tickets (children, fix-children). Append-only. |

The current Active / Backlog / Decisions / Sync Queue conflates work-tracking with product-tracking. The new shape separates them: Product / Architecture / Design / Milestones / Status are **product layer**; Backlog / Done are **work-tracking**.

In multi-product Linear teams (the common case per D0.1 — 5-team subscription limit), project names carry the marker prefix: `[BOM] Product`, `[BOM] Architecture`, etc. See D0.1 §Multi-product Linear teams.

## Project contents in detail

### Product

One Linear project per consumer. Documents:

- `[<MARKER>-DOC-NNNN] product: north-star` — founder-authored at `/onboard`, amended only with explicit `/constitution`-style versioning. Contains: problem statement, target user, target shape, non-goals, distribution posture.
- `[<MARKER>-DOC-NNNN] product: vision-v<N>` — append-only iterations if the north-star is meaningfully revised. v1 at `/onboard`.
- **Status document** (single, living — described in §Status).

Cascade reads at: `/specify` (every feature), four-hat-user (every spec review), `/retro` (for "did this feature actually advance the north-star?" check).
Cascade writes: never (Status is the exception, by Status's own write rules).

### Architecture

- `[<MARKER>-DOC-NNNN] arch: technical-architecture` — single living document. Sections: system shape, key components, integration points, deployment posture, security considerations. Updated by `/wrap` and `/retro` when changes warrant.
- `[<MARKER>-DOC-NNNN] arch: data-model` — single living document. Schemas, entities, relationships, key invariants. Updated by `/wrap` per child when the child changes a data shape.
- `[<MARKER>-DOC-NNNN] adr-mirror: NNNN-<slug>` — one per architectural decision, mirrored from `docs/decisions/`. Existing pattern from `naming.md`.

Cascade reads at: `/specify` (especially four-hat-engineer), `/plan` (decomposition consults data-model for entity boundaries), `/build` (PROMPT.md includes architecture for context).
Cascade writes: `/wrap` updates technical-architecture and data-model when the just-completed child changed either. `/retro` proposes broader updates after the feature is verified. `/build` emits ADR-mirror documents per significant decision.

### Design

- `[<MARKER>-DOC-NNNN] design: design-system` — for products with UI. Color tokens, typography, spacing scale, component conventions. Founder-supplied seed at `/onboard` for end-user products; cascade refines through `/retro`.
- `[<MARKER>-DOC-NNNN] design: user-journeys` — single living document. End-to-end flows the user takes through the product. For Bomber: "open game → see arena → move → drop bomb → see explosion → die / win." For a backend service: "client authenticates → submits request → polls for status → downloads result." Cascade-maintained.
- UI assets (mockups, screenshots, brand): linked from the Design project as Linear attachments where possible, or external links.

Cascade reads at: `/specify` (four-hat-user reads user-journeys; perceptual ACs validate against journey steps).
Cascade writes: `/verify` updates user-journeys after each milestone with the as-shipped flow; `/retro` proposes design-system updates.

### Milestones

One Linear project. One issue per milestone. Each milestone:

- Title: `[<MARKER>] M-N: <name>` (e.g. `[BOM] M-1: First playable level`)
- Description: target shape ("at the end of this milestone, the user can X"), acceptance criteria at the milestone level (not feature level), perceptibility check at the milestone level
- Status: Linear workflow status (Backlog → In Progress → Done)
- Children: each `/plan`-ed parent (feature) is a child issue of the milestone

Milestones map to the **decomposition strategy** chosen for the product (per D3.1):

- Walking-skeleton products: each milestone = one playable increment
- API-boundary products: each milestone = one API boundary delivered
- Capability-cluster products: each milestone = one user-visible capability

Cascade reads at: `/onboard` (lists milestones in initial planning conversation), `/specify` (a new feature always lives under a milestone parent), `/verify` (perceptual walkthrough fires at milestone completion).
Cascade writes: `/verify` marks a milestone Done when all children are `scope:built` AND the perceptual walkthrough passes.

### Status

A **single Linear document per consumer, parented under the Product project**. The 30-second read. Living. Updated at every cascade stage transition.

Document shape (example):

```
# [<MARKER>] Product status — updated 2026-05-18 14:32

## Current milestone
M-2: First playable level
Progress: 4 of 6 children scope:built, 1 in build, 1 backlog
Smoke gate: green (last verified 2026-05-18 14:32)
Integration gate: green (last verified 2026-05-18 14:33)
Perceptual gate: pending — fires at milestone completion

## What works
- Grid loads from .tres resources (BOM-12, BOM-13)
- Player renders and accepts WASD input (BOM-15)
- Bombs drop and tick down 3s before explosion (BOM-17)

## What's broken
- (none currently)

## What's next
- BOM-19: Bomb detonates in cardinal cross
- BOM-20: Soft walls destroy on detonation
- M-3 (planned): Player death + win condition

## Recent decisions
- 2026-05-17: chose iterative chain detonation (vs recursive) — see [BOM-DOC-0014] (ADR)
- 2026-05-15: tween easing = cubic-out for screen-shake — see BOM-15 build comment

## Open markers in code
- 7 🤔 markers across 3 files (run `grep -rn 🤔` to surface)
- 12 📝 markers pending copy (run `grep -rn 📝` to surface)
```

Status is the **fabrication detector**. Any disagreement between Status ("WASD works") and a smoke check ("scene doesn't load") is observable and halts the cascade. Compare to the Bomber dogfood: nothing summarized "this is what is and isn't working," so a renderless game shipped scope:built three times.

Cascade reads at: every stage start, `/audit-self`, founder via `/status` command.
Cascade writes: every cascade stage transition. `/specify` writes "M-N-K being specified"; `/plan` writes "M-N-K planned, J children"; `/build` writes "M-N-K-J in build"; `/wrap` writes "M-N-K-J complete, moved to Done"; `/verify` writes "M-N-K verified" or "M-N-K perceptual gate failed: <reason>".

Writes are append-only at the section level but the document itself is overwritten with the current snapshot — readers always see the latest state. Historical state lives in Linear's per-document edit history.

The filesystem mirror at `docs/product/status.md` (per D0.1) is updated by `/wrap` in the same commit as the Linear write, so GitHub viewers see current state.

### Backlog

Linear project. One issue per next-up ticket for the currently-active milestone:

- Created by `/plan` as children of a milestone parent
- Status: Backlog (Linear workflow)
- Scope label: `scope:planned`
- Lifecycle: enter at `/plan` completion, exit when `/build` picks them up (transition to In Progress + `scope:sealed`)

Once a ticket transitions to `scope:built` and `/wrap` completes, it moves to the Done project.

### Done

Linear project. Terminal `scope:built` children. Append-only — issues that land here don't transition out except by explicit founder action (e.g. mark superseded by a later fix-child).

Why a separate project rather than a label or filter: visual separation. Backlog should show what's actively coming up; finished work shouldn't visually compete with planning work.

## Cascade-maintained vs founder-authored discipline

Documents fall into one of three classes:

| Class | Founder writes | Cascade writes | Examples |
|---|---|---|---|
| **Founder-authored** | At onboard or explicit amendment | Never | product: north-star, design: design-system (seed) |
| **Cascade-maintained** | Reviews / signs off | Every relevant stage | Status, arch: technical-architecture, arch: data-model, design: user-journeys, milestone status |
| **Cascade-emitted, founder-reviewed** | Reviews & approves at `/verify` | Writes initial content | ADRs, four-hat docs, retro docs, child ticket descriptions |

**The discipline that prevents a documentation cathedral that rots:** the founder is never asked to author a status document from scratch. The cascade keeps Status, Architecture, Data-Model, and User-Journeys current as a side-effect of doing work. The founder reviews at `/verify` (sign-off) and `/retro` (course correction), but doesn't maintain.

If a doc would otherwise require founder authoring on every update, the cascade is wrong-shaped — the doc either belongs in the founder-authored class (rare, evergreen content like north-star) or the discipline needs adjustment.

## Write responsibility per cascade stage

| Stage | Writes to |
|---|---|
| `/onboard` | Creates all elements (6 projects + Status doc under Product). Seeds Product / Design with founder content. Status starts at "no milestone yet". Detects existing-team project-name collisions and switches to prefix mode if needed (per D0.1 §Multi-product Linear teams). |
| `/specify` | Status (current feature being specified). Creates a backlog issue for the feature under its milestone. |
| `/plan` | Status (feature planned, N children). Creates child tickets in Backlog. |
| `/review` | No product-layer writes. Writes review doc; if findings produce architectural decisions, emits ADR-mirror in Architecture. |
| `/update-linear` | Same — no product-layer writes; ticket descriptions consolidated. |
| `/build` (spawn) | Status (child in build). |
| `/build` (finalize) | Status (child built, smoke/integration gate green). |
| `/wrap` | Status (child complete, moved to Done). Moves ticket Backlog → Done. **Updates Architecture / Data-Model / User-Journeys if the work changed any of them — the canonical update point per the founder's design decision.** Emits ADR-mirror if the child included an architectural decision. **Syncs filesystem mirror** at `docs/product/*.md` in the same commit. |
| `/verify` | Status (milestone complete or perceptual gate failed). Updates User-Journeys with the as-shipped flow. Marks milestone Done. |
| `/retro` | Updates Architecture and Data-Model with retrospective findings. Status updated with lessons-learned summary line. |

## Migration from current state

The framework's own Linear team (Solo Claude Stack) keeps current projects (Active, Backlog, Decisions, Sync Queue) for framework work. The framework's own product-layer adoption is deferred to v0.2.1.

For Bomber, which shares the Solo Claude Stack team (per D0.1 — the 5-team subscription limit forbids a separate team):

1. **Archive Bomber v0.1 Linear artifacts:** SOL-52 through SOL-88 move to a "Bomber v0.1 archive" project (or get an `archive:v0.1` label). `[BOM-DOC-*]` documents stay as historical record. SOL-89 through SOL-101 (workflow-critique) stay where they are — they're framework feedback.
2. **Provision Bomber v0.2 projects with marker prefix:**
   - `[BOM] Product` (with the Status doc under it)
   - `[BOM] Architecture`
   - `[BOM] Design`
   - `[BOM] Milestones`
   - `[BOM] Backlog`
   - `[BOM] Done`
3. **Re-onboard Bomber** under v0.2:
   - Founder seeds Product (north-star), Design (design-system) at `/onboard`.
   - Cascade creates initial milestones (placeholder M-1: First playable level).
   - Cascade initializes Status doc with "no work in progress."

Note: Linear assigns identifiers from the team's counter, so new Bomber tickets continue from `SOL-102`+ rather than starting fresh at `BOM-1`. That's the cost of the shared-team constraint. The marker `BOM` lives in titles and doc IDs; the identifier prefix `SOL` lives in URLs and references. Cascade reads marker from `docs/.solo-config.json` throughout.

## `/onboard` changes

`/onboard` step 4.5 currently creates `Decisions`, `Backlog`, `Active` projects. The new sequence:

1. Determine project-name mode: scan the chosen Linear team for existing projects named `Product`, `Architecture`, `Backlog`, `Done`. If any exist, switch to **prefix mode** (write `linear.project_naming = "prefixed"` to `docs/.solo-config.json`).
2. Create the six projects + Status doc:
   - Plain mode: `Product`, `Architecture`, `Design`, `Milestones`, `Backlog`, `Done` + Status under Product.
   - Prefix mode: `[<MARKER>] Product`, `[<MARKER>] Architecture`, `[<MARKER>] Design`, `[<MARKER>] Milestones`, `[<MARKER>] Backlog`, `[<MARKER>] Done` + Status under `[<MARKER>] Product`.
3. Seed Product with founder's north-star (interactive flow; reuse existing /onboard step 7).
4. Seed Design with founder's design-system if applicable (skip for non-UI products).
5. Seed Milestones with at least one placeholder milestone "M-1: first deliverable" — founder refines during `/discovery` / `/specify`.
6. Initialize Status doc with "no work in progress."

The current `Decisions` project is absorbed into Architecture (as ADR-mirror documents) — no separate Decisions project. Sync Queue is unchanged from current spec since the chat-Claude → Code-Claude handoff still exists.

## Open items

- **Sync Queue placement.** Currently a separate project per consumer. Could fold into Backlog with a `sync:pending` label, since the projects now distinguish work-tracking elements cleanly. Defer the consolidation to v0.2.1 unless it surfaces as a friction point. **Confirmed deferred.**
- **Done project archival.** Append-only is fine for a year or two; eventually Done will accumulate hundreds of tickets. Add `archive:` prefix at year boundaries and Linear's project search will continue to surface old work without dominating the active view. Defer until count > 200.
- **Filesystem mirror conflict resolution.** If `/wrap` writes the Linear update successfully but the filesystem write fails (or vice versa), the mirror goes stale. D2.1 (trust model, postcondition verification) covers detection; recovery is `--reconcile` per D4.5.
