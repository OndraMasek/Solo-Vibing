---
name: discovery
description: Five-phase research-driven discovery flow. Validates a north-star idea before any spec work — Discover (8 fields), Research (5 mandatory areas + tier-2 via research-investigator agent), Challenge (memo + verdict), Improve (on refine), Loop or Exit. State persists in docs/.discovery-state.json across chats. Fires on the first north-star answer (from /onboard), or on "/discovery", "discovery", "validate idea", "explore idea". Iteration cap default 3, extendable at cap turn. Exit branches write docs/product/north-star.md + framing ticket (approve), killed-idea ticket (kill), or auto-start a new Phase 1 (pivot). Task-invokes /constitution on approve exit (always — no longer conditional on a config knob).
---

# discovery

Five-phase discovery. Validates idea before specs. State in `docs/.discovery-state.json` so the flow is resumable across chats. References rules: `naming.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`. Invokes agent: `research-investigator`. Chains to skill via Task tool: `constitution` (on approve exit when config enables).

## Trigger

- Cascade: Task-invoked by /onboard step 7 (handoff after first north-star answer).
- User: "/discovery", "discovery", "validate idea", "explore idea".
- Resume: any /discovery invocation when `docs/.discovery-state.json` exists resumes at the last incomplete phase.

## Behavior

### Phase 1 — Discover (8 fields)

Walk the founder through 8 questions sourced from `docs/product/north-star-questions.md`. Persist answers in `docs/.discovery-state.json` and a new `docs/discovery/idea-brief-v<N>.md` per iteration.

1. **Who is it for?** (primary + secondary segment archetypes)
2. **What's their problem?**
3. **How does it solve the problem?**
4. **What does this?** (high-level description)
5. **Biggest risks?**
6. **Why now?**
7. **Why am I the right person?** (founder-fit)
8. **Skills I have / missing / how to close the gap.** Produce an advisory verdict: **build / pivot / kill**.

For "I don't know" answers, offer:

- **A.** Hear AI recommendation (chat-Claude proposes; founder accepts or edits).
- **B.** Defer to Phase 2 research.
- **C.** Keep open (revisit at end of Phase 1).

Each field is source-tagged in the brief: `(user)`, `(ai-recommended)`, `(research-pending)`, `(open)`.

### Phase 2 — Research

**5 mandatory research prompts** (use `docs/discovery/research-prompt-templates.md`):

1. Problem validation
2. Market sizing
3. Competition
4. Solution viability
5. Technical feasibility

Plus founder-selected tier-2 prompts (regulatory, GTM channels, pricing, etc.).

**Per prompt:**

1. Create tracking ticket in `Backlog` with label `type:research`, title `[<MARKER>] research: <topic>`.
2. Allocate `NNNN` per `counter-allocation.md` — single `doc` allocation per prompt, shared between the Linear summary and the deep-report file; passed to the agent.
3. **Task-invoke `[SOL-AGENT] research-investigator`** with the prompt, slug, and NNNN. The agent runs deep research, writes the deep report to `docs/research/NNNN-<slug>.md`, and returns a structured `## Artifact` block with summary findings.
4. Map agent output to /discovery status per `completion-status.md` §Agent contract. `uncertain:`-prefixed findings (per `auditor-stance.md`) are forwarded to the Linear summary verbatim.
5. Create Linear research-summary document per CF2 (below).

**Canonical research-summary structure (CF2 — required).** Every Phase 2 Linear research document uses this structure. Doc ID format follows `naming.md` (4-digit DOC prefix; type is encoded in the title, not the ID):

~~~
# [<MARKER>-DOC-NNNN] research: <topic>

## Title
<topic, restated>

## Brief Summary
2–4 sentences. What was investigated, what was found. Sourced from the agent's deep-report summary.

## Key Findings
- Finding 1 (one line, specific, citable; copied verbatim from agent's `## Artifact` block)
- Finding 2
- Finding 3
- uncertain: hypothesis — what would resolve it
- ...

## Link to deep report
docs/research/NNNN-<slug>.md
~~~

No deviations. /specify reads research summaries by this structure when loading top-3 relevant research; deviation breaks downstream parsing.

### Phase 3 — Challenge

Load `docs/discovery/challenge-checklist.md`. Run each check against the idea brief + Phase 2 findings. Produce `docs/discovery/challenge-memo-iter<N>.md` with one of four verdicts. Auditor-stance per `auditor-stance.md` — state findings as facts, no LGTM closures.

- **approve** → Phase 5 approve branch.
- **refine** → Phase 4.
- **kill** → Phase 5 kill branch.
- **pivot** → Phase 5 pivot branch.

### Phase 4 — Improve (only on `refine`)

Propose specific edits to the idea brief based on the challenge memo. Founder accepts or rejects each edit. Write `docs/discovery/idea-brief-v<N+1>.md`. Increment iteration counter. Return to Phase 3 with the new brief.

### Phase 5 — Loop or Exit

Iteration cap default **3**. Founder can extend at the cap turn.

- **approve**: write `docs/product/north-star.md` (canonical) + create framing ticket in `Active` with label `type:framing` (per `scope-labels.md` — note: `type:*` labels are separate from `scope:*` labels in the state machine; framing tickets do not carry scope labels, only type labels). Task-invoke `/constitution` per audit decision #9 (seed mode writes v1.0.0 from north-star + idea-brief). The constitution is non-optional: /specify hard-requires it as a precondition. Cascade ends from /discovery's perspective; /specify becomes available.
- **kill**: write killed-idea ticket in `Backlog` with label `killed-idea:<slug>`. Archive `docs/.discovery-state.json` to `docs/discovery/archive/<timestamp>-kill/`.
- **pivot**: archive current discovery artifacts (`idea-brief-v*.md`, `challenge-memo-iter*.md`, `docs/.discovery-state.json`) to `docs/discovery/archive/<timestamp>-pivot/` before clearing; auto-start a new Phase 1 with pivot context as seed.
- **refine at cap with no extension**: forced exit; verdict converts to `kill` with note "iteration cap reached without convergence."

All Phase 5 writes batched same-turn per `write-discipline.md`.

## Outputs

| Artifact | Location |
|---|---|
| Idea briefs (per iteration) | `docs/discovery/idea-brief-v<N>.md` |
| Research deep reports | `docs/research/NNNN-<slug>.md` |
| Research summaries (Linear) | `[<MARKER>-DOC-NNNN] research: <topic>` per `naming.md` |
| Challenge memos | `docs/discovery/challenge-memo-iter<N>.md` |
| State | `docs/.discovery-state.json` |
| North-star (approve exit) | `docs/product/north-star.md` + framing ticket |
| Killed-idea record (kill exit) | Ticket with `killed-idea:<slug>` label |
| Pivot history (pivot exit) | `docs/discovery/archive/<timestamp>-pivot/` + new Phase 1 seeded |

## Completion status

Per `completion-status.md`. /discovery is multi-phase and resumable — emit per chat session, not per full discovery run.

- `DONE` — Phase 5 exit reached (approve/kill/pivot); final artifact written. For approve: north-star.md exists; framing ticket created; /constitution Task-invoked if config enables.
- `DONE_WITH_CONCERNS` — exit reached but with notable conditions: approve exit while 3+ Phase 1 fields remain `(research-pending)`; iteration cap reached and founder extended past cap; refine-at-cap forced conversion to kill; research-investigator returned `uncertain:` findings on a load-bearing prompt.
- `BLOCKED` — `docs/.discovery-state.json` is corrupted or unreadable; research-investigator failed on a mandatory prompt (no deep report produced).
- `NEEDS_CONTEXT` — missing `docs/discovery/research-prompt-templates.md`, `docs/discovery/challenge-checklist.md`, or `docs/product/north-star-questions.md` (/onboard step 1 should have caught these; re-run /onboard if reached); Linear MCP unreachable for `doc`-counter scan per `counter-allocation.md`.

For partial runs (founder ended the chat mid-Phase): emit `DONE` for that chat session with a note that the state file holds the resume point. Pausing is by design, not failure.

## Chains

- **approve exit**: Task-invoke /constitution per audit decision #9. /constitution writes v1.0.0; then /specify becomes available to the founder. No auto-chain from /constitution to /specify — sit-time on the north-star is healthy. The constitution is non-optional: /specify hard-requires it.
- **kill exit**: terminal.
- **pivot exit**: auto-restarts Phase 1 with pivot context internal to /discovery (not a Task-invocation chain — same skill re-entry).
- **mid-flow**: resumable across chats; re-invoke /discovery and the state file is the anchor.

## Notes

**Five phases, not five turns.** Each phase spans multiple chat exchanges. The state file is what makes /discovery resumable.

**Phase 1 source-tagging matters downstream.** `(ai-recommended)` answers carry less weight in Phase 3 challenge than `(user)` answers. The Skeptic pass should scrutinize AI-recommended fields harder.

**Phase 2 CF2 structure is non-negotiable.** It's the formatter for every subsequent skill that reads research — /specify pulls top-3 by title/keyword similarity and quotes Key Findings verbatim into spec markdown. Deviation breaks downstream parsing.

**Why DOC prefix for research summaries.** Per `naming.md`, all Linear doc IDs use `[<MARKER>-DOC-NNNN]` regardless of type; type is encoded in the title (`research: <topic>`, `four-hat: <title>`, `constitution: v<semver>`). The pre-extraction body used `[<MARKER>-RES-NNNN]` (RES prefix); migrated to canonical form in this revision. Existing pre-extraction research summaries with RES prefix remain valid (their slugs are stable Linear identifiers); only new summaries follow the DOC convention.

**Deep research runs are time-bounded** — typical Phase 2 takes 1–3 days wall-clock per prompt (research, draft, review). Don't sprint Phase 2; the depth is the point. The research-investigator agent's freshness rule (6 months for ecosystem-velocity topics) is enforced at the agent layer.

**Challenge memo is adversarial by design.** If every iteration approves, the checklist is too soft — review `docs/discovery/challenge-checklist.md` and add sharper checks.

**Iteration cap is 3** because most ideas either converge or reveal terminal flaws within 3 cycles. Extending past the cap is fine but should be deliberate — repeated `refine` verdicts at cap usually mean the founder is attached to a flawed premise.

**Pivot is the most expensive exit** because it discards Phase 1+2 work. Use when the challenge memo surfaces a fundamentally different problem the founder should pursue. Cosmetic changes are `refine`, not `pivot`.

## Open questions (deferred to v1.1+)

- **Migration of pre-extraction RES-prefix research summaries.** Existing `[<MARKER>-RES-NNNN]` summaries from pre-extraction discovery runs remain valid by slug; a rename pass would break cross-references. Defer to a coordinated rename pass when slug churn is acceptable.
- **Cross-prompt deduplication.** The research-investigator runs each prompt independently; overlapping findings across the 5 mandatory prompts aren't auto-deduplicated. v1.1 candidate.
- **Skill → command transformation.** /discovery is multi-phase orchestration; unlike most skills it probably stays a skill rather than becoming a command. Out of scope for Batch 3.
- **Auto-iteration of Phase 3 challenge memo.** v0.1 produces one challenge memo per iteration; multi-perspective challenges (e.g. running four-hat critique against the idea brief inside Phase 3) is v1.1.
