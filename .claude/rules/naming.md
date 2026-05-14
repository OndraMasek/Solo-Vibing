# Naming

Lexicon for IDs, slugs, and file paths across the cascade. Every skill that mints an artifact reads this rule.

## Marker

Read the marker string from `docs/.solo-config.json` → `marker`. No skill hardcodes a marker value. The marker is set once at /onboard; changing it post-onboard requires manual migration of all existing artifacts.

## Ticket IDs

- Parent ticket: `<MARKER>-N`. N is the Linear-assigned auto-increment.
- Child ticket: `<MARKER>-N-K`. K is the child's index in the /plan decomposition order (1-based, monotonic within a parent).

## Ticket titles

Parent ticket title: `[<MARKER>] <verb-noun>`. Example: `[SOL] add cascade orchestration`. Linear shows the identifier (`SOL-12`) separately from the title; the bracket prefix in the title is a human-readability anchor across the marker space.

Child ticket title: convention set by /plan when it drafts children. Leaving open until /plan is redrafted in Batch 3 — likely `<verb-noun>` (no bracket prefix, since the parent context is carried by parentId and Linear's auto-assigned identifier).

## Shared Linear teams

A Linear team belongs to its workspace and has a single team key (`SOL`, `OMA`, etc.). The Solo-Setup marker is repo-scoped and independent of the team key. When two repos with different markers share a team, Linear's UI shows team-keyed ticket IDs for both — a `BOM`-marker ticket in the `SOL` team appears as `SOL-47` in Linear, with `[BOM]` only in the title.

Implications:

- Ticket IDs in Linear's UI follow the team's key prefix; the marker is a title-level discriminator, not an identifier-level one.
- Cross-team workflows (multiple repos, multiple markers) must filter by title-prefix label or by a shared `marker:<MARKER>` label per ticket to disambiguate at scale.
- The cleanest separation is one Linear team per marker. Solo-Setup does not enforce this — onboarding accepts shared teams — but downstream skill queries that filter by marker need this awareness baked in.

`/onboard` surfaces this trade-off at step 4 (marker pick) so founders set expectations before tickets accumulate.

## Branch names

- Parent branch (rare, only if work happens at the parent level): `<MARKER>-N-<slug>`.
- Child branch: `<MARKER>-N-<slug>-K`.

Slug is 2–4 words, kebab-case, founder-confirmed during /specify step 6. The parent slug carries through to all child branches under that parent.

## Linear doc IDs

Format: `[<MARKER>-DOC-NNNN]`. Type prefix follows in the doc title. NNNN is the `doc`-counter value (allocated per `counter-allocation.md`), zero-padded to 4 digits.

Type prefixes currently in use:

- `four-hat: <MARKER>-N <title>` — /specify
- `research: <topic>` — /discovery (Phase 2)
- `audit: <topic>` — /audit-self
- `discovery: state` — /discovery (cross-phase resume anchor; single mutable doc per project)
- `discovery: idea-brief-v<N>` — /discovery (Phase 1, one per iteration, append-only)
- `discovery: challenge-memo-iter<N>` — /discovery (Phase 3, one per iteration)
- `constitution: v<semver>` — /constitution (seed + amendments)
- `retro: <MARKER>-N <title>` — /retro
- `verify: <MARKER>-N <title>` — /verify (when mirroring report to Linear)
- `review: <MARKER>-N <title>` — /review (cascade-stage doc)
- `adr-mirror: NNNN-<slug>` — /review (auto-ADR Linear mirror)

All Solo-Setup-side Linear writes use this convention; deviation breaks the `doc`-counter scan defined in `counter-allocation.md`.

## File paths

- Spec: `docs/specs/NNNN-<slug>/spec.md`. Directory also holds archived prior versions under `archive/spec-v<N>.md`.
- ADR: `docs/decisions/NNNN-<slug>.md`.
- Research deep report: `docs/research/NNNN-<slug>.md`.
- Ralph workspace: `.ralph/<MARKER>-N-K/`. Per-iteration: `.ralph/<MARKER>-N-K/iterations/NNN/`.

NNNN is zero-padded to 4 digits. Allocation protocol is defined in `counter-allocation.md`; this rule defines only the naming surface. Three logical counters exist — `spec`, `adr`, and `doc` — each allocated by scanning its authoritative source:

- `spec` — allocates the `NNNN` in `docs/specs/NNNN-<slug>/`. Source: scan `docs/specs/` for existing `NNNN-*` directories; pick max + 1.
- `adr` — allocates the `NNNN` in `docs/decisions/NNNN-<slug>.md`. Source: scan `docs/decisions/` for existing `NNNN-*.md` files; pick max + 1.
- `doc` — allocates the `NNNN` for every Linear document (`[<MARKER>-DOC-NNNN]` — four-hat, research, audit, retro, review, adr-mirror) **and** the research deep-report file at `docs/research/NNNN-<slug>.md`. Source: query Linear for documents matching the `[<MARKER>-DOC-*]` title pattern; pick max + 1.

A research summary (Linear `[<MARKER>-DOC-NNNN]`) and its deep-report file (`docs/research/NNNN-<slug>.md`) **share a single `doc` value** — one allocation per research prompt, used in both the Linear title and the filename. /discovery is the sole allocator for the pair.

## Collisions

A skill that mints any ID scans the relevant source first per `counter-allocation.md`. If the proposed ID collides with an existing artifact, the skill halts with `BLOCKED` and a diagnostic citing the collision. No auto-increment-on-collision — collisions indicate a state desync that needs manual resolution.
