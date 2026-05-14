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

## Branch names

- Parent branch (rare, only if work happens at the parent level): `<MARKER>-N-<slug>`.
- Child branch: `<MARKER>-N-<slug>-K`.

Slug is 2–4 words, kebab-case, founder-confirmed during /specify step 6. The parent slug carries through to all child branches under that parent.

## Linear doc IDs

Format: `[<MARKER>-DOC-NNNN]`. Type prefix follows in the doc title: `[<MARKER>-DOC-NNNN] four-hat: <MARKER>-N <title>`, `[<MARKER>-DOC-NNNN] research: <topic>`, `[<MARKER>-DOC-NNNN] audit: <topic>`. NNNN is the `doc`-counter value (allocated per `counter-allocation.md`), zero-padded to 4 digits.

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
