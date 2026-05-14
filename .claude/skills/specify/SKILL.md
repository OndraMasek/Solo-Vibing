---
name: specify
description: Author a heavyweight spec for a parent feature. Produces a sealed parent ticket (label scope:specified), spec markdown at docs/specs/NNNN-<slug>/spec.md, and an append-only four-hat Linear document. On seal, the cascade auto-fires through /plan → /review → /update-linear; user sees a single summary or halt-card at the end. Next user-invoked step is /build <MARKER>-N-K per child ticket. Fires on "/specify <topic>", "specify <topic>", "spec out <topic>", "write a spec for <topic>". Modes: `--continue` resumes in-progress, `--unseal` archives and rebuilds.
---

# specify

Author parent spec. User-facing entry point of the cascade. On seal, the cascade auto-fires through /plan → /review → /update-linear; the founder sees a single summary or halt-card at cascade end. Next user-invoked step is `/build <MARKER>-N-K` per child ticket.

## Trigger

- User: "/specify <topic>", "specify <topic>", "spec out <topic>", "write a spec for <topic>"
- Resume: "/specify <MARKER>-N --continue" — resumes an in-progress spec
- Unseal: "/specify <MARKER>-N --unseal" — archives the current spec and rebuilds (full re-run)

## Behavior

0. **Preconditions** (any failure halts with `NEEDS_CONTEXT` per `completion-status.md`; halt-card per `docs/templates/halt-messages.md`).
   - `docs/constitution.md` exists. Missing → `NEEDS_CONTEXT` per `§missing-context`: "no constitution; run `/discovery` (approve exit Task-invokes `/constitution`) or `/constitution reseed` if a north-star already exists." /review check j and downstream cascade stages assume a constitution; /specify halts here rather than letting the cascade fail three stages deep.
   - `docs/product/north-star.md` exists. Missing → `NEEDS_CONTEXT`: "no north-star; run `/discovery`."
   - Marker resolvable from `docs/.solo-config.json`. Unset → `NEEDS_CONTEXT`.

1. **Load context.**
   - `docs/product/north-star.md`
   - `docs/constitution.md`
   - `docs/onboarding/codebase-map.md` if present (brownfield context)
   - Scope-relevant ADRs from `docs/decisions/*.md`
   - Top 3 research summaries from /discovery Phase 2 closest to spec topic
   - Framing ticket from /discovery if this spec responds to one

2. **Draft full spec** at `docs/specs/NNNN-<slug>/spec.md` per path conventions in `rules/naming.md`. Use `docs/templates/spec.md.template`. Six sections: Problem statement, Design & UX (or API contract for backend-only), Scope boundary (in/out both explicit), Acceptance criteria (behavior-oriented testable checkboxes), Failing-test seed (Code-Claude scaffolds these as the first commit), Related research findings (verbatim bullets linked to `[<MARKER>-RES-NNN]` summary + deep report).

3. **Four-hat critique.** Invoke four-hat-engineer, four-hat-pm, four-hat-skeptic, four-hat-user agents in parallel via the Task tool. Aggregate findings into a Linear document `[<MARKER>-DOC-NNNN] four-hat: <MARKER>-N <title>` per `rules/naming.md`. The document is append-only — re-runs add new sections, prior sections preserved. Review history is permanent.

4. **Resolve every objection.** For each finding from the four-hat doc:
   - **Incorporate** — edit spec in place.
   - **Defer** — record in Open Questions with rationale.
   - **Reject** — record in spec margin with rationale.

   **Scope-reduction guard:** any "drop AC" suggestion surfaces to the founder explicitly. Founder confirms each drop. Never silent — silent acceptance creates spec drift.

5. **Clarify phase.** Invoke clarify-walker agent. The agent returns applicable clarification surfaces with per-surface questions. Present to founder, record answers in a Clarifications section appended to `docs/specs/NNNN-<slug>/spec.md`. Unanswerable items move to Open Questions with rationale.

6. **Slug derivation.** Propose 2–4 word kebab-case slug; founder confirms. Branch name follows `rules/naming.md`.

7. **Seal parent ticket and four-hat doc.**
   - Compute spec checksum: `sha256(docs/specs/NNNN-<slug>/spec.md)` truncated to 16 chars. Record in the four-hat doc's metadata header as `spec_sha256: <hash>` in the same write that appends the iteration's resolution summary. /build's drift guard reads this value.
   - Ticket title: `[<MARKER>] <verb-noun>`.
   - Parent ticket transition: set `scope:specified` per `rules/scope-labels.md` (atomic, in the same write as title + description + parentId).
   - Description: brief problem statement + AC checkboxes (mirrored verbatim from spec.md's Acceptance criteria section — text canonical, ticket is read-only mirror) + links to spec markdown + four-hat doc + declared branch name.

   The `scope:specified` label triggers the cascade engine. No further user action needed — /plan auto-fires through the cascade.

All writes follow `rules/write-discipline.md`. Status semantics per `rules/completion-status.md`.

## Unseal-and-respec mode

`/specify <MARKER>-N --unseal`:

1. Archive current `docs/specs/NNNN-<slug>/spec.md` → `docs/specs/NNNN-<slug>/archive/spec-v<N>.md`.
2. Post previous spec content as a comment on the four-hat document (preserves history outside markdown).
3. Re-run the full flow from step 1.
4. Four-hat document is the same one (append-only). Re-computed `spec_sha256` lands in the new iteration's metadata header; prior checksums stay in prior sections.
5. Cascade re-fires on completion.

Use when fundamental rework is needed — adding /plan guidance won't get there.

## Outputs

| Artifact | Location |
|---|---|
| Spec markdown | `docs/specs/NNNN-<slug>/spec.md` |
| Four-hat review document | `[<MARKER>-DOC-NNNN] four-hat: <MARKER>-N <title>` (metadata includes `spec_sha256`) |
| Parent ticket | `[<MARKER>] <verb-noun>`, label `scope:specified` |
| Branch name (declared) | `<MARKER>-N-<slug>` |

## Chains

On `DONE` / `DONE_WITH_CONCERNS`: `scope:specified` triggers the cascade engine. Cascade mode is controlled by `mode` in `docs/.solo-config.json`; see `commands/config.md` for semantics. /plan auto-fires; downstream skills follow. The founder sees a single summary card (or halt-card) at cascade end. The summary includes a `next step: /build <MARKER>-N-K` hint for each child ticket with `scope:sealed`.

On `BLOCKED` or `NEEDS_CONTEXT` mid-flow (precondition fails, founder abandons during Clarify, etc.): spec markdown remains as draft, ticket not sealed, no cascade fires. Founder sees the halt-card or context prompt directly.

No user-facing close message from /specify itself. The next user-visible chat output is the cascade-end summary rendered by /update-linear (renderer absorbed per audit decision #3).

## Notes

**Research-finding drill-down.** If the founder asks "tell me more about finding X" during or after /specify, read `docs/research/NNNN-<slug>.md` (the deep report linked from the relevant Phase 2 summary) and surface the section. The Related Research Findings section in the spec is intentionally terse — verbatim bullets only — so chat-based drill-down is the discovery path.

**spec.md is the sole canonical source of AC text.** The ticket's AC checkboxes are a read-only mirror written by /update-linear (or /specify at seal) and flipped (state only) by /build on completion. **Do not edit AC text directly on the Linear ticket** — edits get overwritten on the next /update-linear pass. To change an AC, edit `spec.md` and re-run `/specify --continue`. /build's preconditions include a `ticket_ac_text == spec_ac_text` check that halts on drift (`§ticket-ac-drift`).

**Failing-test seed is the contract /plan reads from.** Incomplete seeds halt the cascade at /plan — an incomplete failing-test seed is a /specify defect, never iterated on inside /plan. Author seeds carefully.
