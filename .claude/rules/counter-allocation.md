# Counter allocation

Protocol for allocating `NNNN` values across the three logical counters defined in `naming.md`. Every skill that mints an NNNN-bearing artifact (spec, ADR, Linear doc, research deep report) reads this rule.

No counter file exists in v0.1. Allocation is by **scan-then-claim** against the authoritative source. The pre-v0.1 `docs/.doc-counter.json` cache is removed because it duplicated state already legible from the filesystem and Linear.

## Authoritative sources

| Counter | Source | Scan |
|---|---|---|
| `spec` | `docs/specs/` | `ls docs/specs/` and extract leading `NNNN` from each `NNNN-<slug>` directory. |
| `adr`  | `docs/decisions/` | `ls docs/decisions/` and extract leading `NNNN` from each `NNNN-<slug>.md`. |
| `doc`  | Linear documents | Query Linear for documents whose title matches `[<MARKER>-DOC-NNNN] ...` and extract NNNN. |

## Allocation protocol

For every NNNN-bearing artifact a skill mints:

1. **Scan** the authoritative source for existing NNNN values. Treat zero-padding as decoration only; compare as integers.
2. **Compute** `next = max(existing) + 1` (or `0001` when no artifacts exist).
3. **Format** as zero-padded 4-digit string (`0001`, `0042`, `1024`).
4. **Claim** by writing the new artifact (filesystem path or Linear document) in the same same-turn write batch per `write-discipline.md`. The artifact's existence IS the claim — no separate counter file is updated.
5. **Verify on write success.** If the write fails (race, filesystem error, Linear API error), surface `BLOCKED` per `write-discipline.md` §Partial failure. Do not retry within the same turn.

## Collision handling

A collision means another artifact already exists at the proposed NNNN. Because the scan-then-claim sequence is single-turn and the Solo-Setup workflow is single-founder, true races are rare. Collisions usually indicate one of:

- Manual filesystem or Linear edits between scan and write.
- A previously-aborted skill run that left a partial artifact behind.
- A counter desync from a manual rename.

Per `naming.md` §Collisions: halt with `BLOCKED`, cite the collision, do not auto-increment. Recovery is manual.

## Shared allocations

A research deep report (`docs/research/NNNN-<slug>.md`) and its Linear summary (`[<MARKER>-DOC-NNNN] research: <topic>`) **share one `doc` allocation**. /discovery scans the `doc` source once per prompt, allocates one NNNN, then writes both the filesystem deep report and the Linear summary using that same NNNN. The two writes batch same-turn per `write-discipline.md`.

No other counter has shared allocations in v0.1.

## Counter ownership by skill

| Counter | Allocating skills |
|---|---|
| `spec` | /specify (on seal) |
| `adr`  | /review (auto-ADR on check h), founder (manual ADR authoring) |
| `doc`  | /specify (four-hat doc), /review (review doc, auto-ADR Linear mirror), /discovery (research summary + deep report — shared; **discovery state doc**; **idea-brief docs per iteration**; **challenge-memo docs per iteration**), /verify (verify-report Linear mirror, when applicable), /retro (retro doc), /constitution (constitution doc) |

Every other skill must reference this rule rather than allocate inline.

## Notes

**Why scan-then-claim and not a counter file.** The counter file was a cache. Caches drift. The filesystem and Linear are the actual sources of truth; reading them directly is race-free for a solo founder and self-healing if a manual edit happens.

**Linear scan cost.** Every `doc` allocation now performs a Linear query. Per-call cost is bounded; halts cleanly per `halt-messages.md` §linear-unavailable if MCP is offline.

**No retry on collision.** Collisions are a state-desync signal. Auto-incrementing past them masks the underlying problem (concurrent edits, partial writes, manual rename). Halt and surface.
