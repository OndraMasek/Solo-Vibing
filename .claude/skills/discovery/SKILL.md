---
name: discovery
description: Five-phase research-driven discovery flow. Validates a north-star idea before any spec work — Discover (8 fields), Research (5 mandatory areas + tier-2 via research-investigator agent), Challenge (memo + verdict), Improve (on refine), Loop or Exit. State persists in Linear documents (`[<MARKER>-DOC-NNNN] discovery: state`) so the flow is resumable across chats and surfaces (chat-Claude or Claude Code). Fires on the first north-star answer (from /onboard's chat-handoff or, in legacy code mode, a Task-invoke), or on "/discovery", "discovery", "validate idea", "explore idea". Iteration cap default 3, extendable at cap turn. Exit branches write docs/product/north-star.md + framing ticket (approve), killed-idea ticket (kill), or auto-start a new Phase 1 (pivot). Task-invokes /constitution on approve exit (always — no longer conditional on a config knob).
---

# discovery

Five phases. Validates idea before specs. State lives in Linear (`[<MARKER>-DOC-NNNN] discovery: state`) so the flow is resumable across chats and surfaces — chat-Claude can resume what Claude Code started, and vice versa. References rules: `naming.md`, `counter-allocation.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`. Invokes agent: `research-investigator`. Chains to skill via Task tool: `constitution` (on approve exit; always).

## Trigger

- Cascade: invoked by /onboard's chat handoff (in default `chat` surface mode) when the founder pastes the kickoff message in their Claude.ai project, or Task-invoked by /onboard step 7 in legacy `code` surface mode.
- User: "/discovery", "discovery", "validate idea", "explore idea".
- Resume: any /discovery invocation while a `[<MARKER>-DOC-NNNN] discovery: state` document exists resumes at the last incomplete phase.

## Behavior

### Phase 1 — Discover (8 fields)

Walk the founder through 8 questions sourced from `docs/product/north-star-questions.md` (in chat: retrieve via Project-knowledge search; in code: read from the working tree). Persist answers to a new `[<MARKER>-DOC-NNNN] discovery: idea-brief-v<N>` Linear document per iteration. Update the `[<MARKER>-DOC-NNNN] discovery: state` document with `{phase, iteration, current_brief_doc_id, status, research_depth}` at each phase transition (`research_depth` is `null` until Phase 2's depth gate sets it to `light` or `deep`).

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

**Step 0 — Research-depth gate (ask first, before running any research).** Phase 2 never silently picks a research depth. The first action on entering Phase 2 is to ask the founder which mode to run, present both, and wait for the choice:

<!-- 🤔 The `via: chat-claude-stand-in` tag is named by SOL-131 but not yet defined in any rule (no `chat-claude-stand-in` convention doc exists in the repo). Treating this SKILL.md section as the convention's definition: it tags findings chat-Claude produced inline while standing in for the un-invokable research-investigator agent. If a shared convention doc is wanted, lift this into a rule and reference it. -->
- **Light** — chat-Claude runs moderate-depth inline web research now (the current behavior). Findings are tagged `via: chat-claude-stand-in` because chat-Claude is standing in for the `research-investigator` agent it cannot Task-invoke. Use when the founder wants a fast read and accepts shallower depth.
- **Deep** — chat-Claude does **not** run the research itself. It emits each research prompt as a ready-to-run artifact (filled-in prompt text, placeholders substituted from the current idea brief), then **pauses** Phase 2. The founder runs the prompts in parallel sessions or separate deep-research runs and pastes each result back; /discovery then writes the CF2 summaries from the pasted artifacts. Use when the depth is the point (the default expectation per §Deep research runs are time-bounded).

Record the choice in the `discovery: state` doc (`research_depth: light | deep`) **before** running any prompt, so a resuming session — chat or code — knows which mode is in flight and does not re-ask or switch modes mid-Phase. A resume with `research_depth: deep` and unfilled CF2 summaries re-enters the paste-back wait, not the prompt-emit step.

**5 mandatory research prompts** (use `docs/templates/discovery/research-prompt-templates.md` — in chat: retrieve via Project-knowledge search; in code: read from the working tree):

1. Problem validation
2. Market sizing
3. Competition
4. Solution viability
5. Technical feasibility

Plus founder-selected tier-2 prompts (regulatory, GTM channels, pricing, etc.).

Both depth modes cover the same 5 mandatory prompts (plus selected tier-2). They differ only in **who runs the research** and **when the summaries are written** — see the two per-prompt branches below. Either way, each prompt's `## Artifact` block flows into the CF2 Linear summary; the source of that block differs by mode.

**Light mode — per prompt (chat-Claude inline, the current default in `chat` surface):**

1. Create tracking ticket in `Backlog` with label `type:research`, title `[<MARKER>] research: <topic>`.
2. Allocate `NNNN` per `counter-allocation.md` — single `doc` allocation per prompt, shared between the Linear summary and the deep-report file.
3. **chat-Claude runs moderate-depth inline web research itself** against the filled-in prompt (placeholders substituted per the deep-mode substitution rule below). It does not Task-invoke `research-investigator` — that agent has no chat surface; chat-Claude stands in for it. The findings it produces are tagged `via: chat-claude-stand-in` so downstream readers know the depth is inline, not a deep-research run. In `code` surface, this step is instead a **Task-invoke of `[SOL-AGENT] research-investigator`** with the prompt, slug, and NNNN — the agent runs deep research, writes the deep report to `docs/research/NNNN-<slug>.md`, and returns the `## Artifact` block; no `chat-claude-stand-in` tag applies.
4. Map the resulting findings to /discovery status per `completion-status.md` §Agent contract. `uncertain:`-prefixed findings (per `auditor-stance.md`) are forwarded to the Linear summary verbatim.
5. Create Linear research-summary document per CF2 (below).

**Deep mode — per prompt (founder runs the research out-of-band):**

1. **Substitute placeholders.** For each mandatory prompt (and each founder-selected tier-2 prompt), fill the template's `{{SEGMENT}}` / `{{PROBLEM}}` / `{{SOLUTION}}` / `{{RISKS}}` (and `{{WHY_NOW}}` for the timing tier-2) from the current idea brief — segment from field 1, problem from field 2, solution from field 3, risks from field 5, why-now from field 6.
2. **Emit each filled-in prompt as a ready-to-run artifact**, one `## Artifact` block per prompt (per `research-prompt-templates.md` §Output contract — each prompt is meant to be passed to a research run). chat-Claude does **not** run the research itself in this mode. Each artifact carries the prompt's `<topic>`, its allocated `NNNN`/slug, and the full substituted prompt text the founder can paste straight into a parallel session or a separate deep-research run.
3. **Pause Phase 2.** Record `research_depth: deep` and the emitted-prompt set in the `discovery: state` doc, then wait. The founder runs the prompts and pastes back each result as a `## Artifact` block.
4. **On paste-back, write the CF2 summary** for each returned artifact: map its findings to status per `completion-status.md` §Agent contract, forward `uncertain:` findings verbatim, and create the Linear research-summary per CF2 (below) using the prompt's allocated `NNNN`. The deep report at `docs/research/NNNN-<slug>.md` is committed by Claude Code on its next code-side session (per §Deep reports are filesystem artifacts). Findings from a founder-run deep-research session are **not** tagged `via: chat-claude-stand-in` — they came from a real deep run, not an inline stand-in.

Phase 2 seals only once every mandatory prompt has a CF2 summary, regardless of mode. A mandatory prompt left without a summary (deep mode: founder has not pasted it back yet) keeps Phase 2 open per §Completion status.

**Canonical research-summary structure (CF2 — required).** Every Phase 2 Linear research document uses this structure. Doc ID format follows `naming.md` (4-digit DOC prefix; type is encoded in the title, not the ID):

~~~
# [<MARKER>-DOC-NNNN] research: <topic>

## Title
<topic, restated>

## Brief Summary
2–4 sentences. What was investigated, what was found. Sourced from the `## Artifact` summary (agent deep report in code/deep mode; chat-Claude's inline run in light mode).

## Key Findings
- Finding 1 (one line, specific, citable; copied verbatim from the `## Artifact` block)
- Finding 2
- Finding 3
- uncertain: hypothesis — what would resolve it
- ...

## Link to deep report
docs/research/NNNN-<slug>.md
~~~

No deviations. /specify reads research summaries by this structure when loading top-3 relevant research; deviation breaks downstream parsing.

### Phase 3 — Challenge

Load `docs/templates/discovery/challenge-checklist.md` (in chat: retrieve via Project-knowledge search; in code: read from the working tree). Run each check against the idea brief + Phase 2 findings. Produce a new `[<MARKER>-DOC-NNNN] discovery: challenge-memo-iter<N>` Linear document with one of four verdicts. Auditor-stance per `auditor-stance.md` — state findings as facts, no LGTM closures.

- **approve** → Phase 5 approve branch.
- **refine** → Phase 4.
- **kill** → Phase 5 kill branch.
- **pivot** → Phase 5 pivot branch.

### Phase 4 — Improve (only on `refine`)

Propose specific edits to the idea brief based on the challenge memo. Founder accepts or rejects each edit. Write `[<MARKER>-DOC-NNNN] discovery: idea-brief-v<N+1>`. Increment iteration counter in the `discovery: state` doc. Return to Phase 3 with the new brief.

### Phase 5 — Loop or Exit

Iteration cap default **3**. Founder can extend at the cap turn.

- **approve**: write `docs/product/north-star.md` (canonical — committed by Claude Code on the next code-side session) + create framing ticket in `Active` with label `type:framing` (per `scope-labels.md` — note: `type:*` labels are separate from `scope:*` labels in the state machine; framing tickets do not carry scope labels, only type labels). Mark the `discovery: state` doc with `status: approved` and freeze it. Task-invoke `/constitution` per audit decision #9 (seed mode writes v1.0.0 from north-star + idea-brief). The constitution is non-optional: /specify hard-requires it as a precondition. Cascade ends from /discovery's perspective; /specify becomes available.
- **kill**: write killed-idea ticket in `Backlog` with label `killed-idea:<slug>`. Mark the `discovery: state` doc with `status: killed` and freeze it.
- **pivot**: mark the current `discovery: state` doc with `status: pivoted` and freeze it. Allocate a new `[<MARKER>-DOC-NNNN] discovery: state` doc seeded with the pivot context, then auto-start a new Phase 1.
- **refine at cap with no extension**: forced exit; verdict converts to `kill` with note "iteration cap reached without convergence."

All Phase 5 writes batched same-turn per `write-discipline.md`.

## Outputs

| Artifact | Location |
|---|---|
| State | `[<MARKER>-DOC-NNNN] discovery: state` (Linear, single mutable doc per project) |
| Idea briefs (per iteration) | `[<MARKER>-DOC-NNNN] discovery: idea-brief-v<N>` (Linear) |
| Challenge memos (per iteration) | `[<MARKER>-DOC-NNNN] discovery: challenge-memo-iter<N>` (Linear) |
| Research deep reports | `docs/research/NNNN-<slug>.md` (filesystem; written by `research-investigator` agent, committed by Claude Code) |
| Research summaries (Linear) | `[<MARKER>-DOC-NNNN] research: <topic>` per `naming.md` |
| North-star (approve exit) | `docs/product/north-star.md` + framing ticket |
| Killed-idea record (kill exit) | Ticket with `killed-idea:<slug>` label |
| Pivot record (pivot exit) | Old `discovery: state` doc frozen with `status: pivoted`; new state doc seeded with pivot context |

## Completion status

Per `completion-status.md`. /discovery is multi-phase and resumable — emit per chat session, not per full discovery run.

- `DONE` — Phase 5 exit reached (approve/kill/pivot); final artifact written. For approve: north-star.md write queued (executed on next code-side session); framing ticket created; /constitution Task-invoked.
- `DONE_WITH_CONCERNS` — exit reached but with notable conditions: approve exit while 3+ Phase 1 fields remain `(research-pending)`; iteration cap reached and founder extended past cap; refine-at-cap forced conversion to kill; research-investigator returned `uncertain:` findings on a load-bearing prompt.
- `BLOCKED` — `[<MARKER>-DOC-NNNN] discovery: state` cannot be located or read (Linear MCP error, doc deleted); research-investigator failed on a mandatory prompt (no deep report produced).
- `NEEDS_CONTEXT` — missing `docs/templates/discovery/research-prompt-templates.md`, `docs/templates/discovery/challenge-checklist.md`, or `docs/product/north-star-questions.md` (in chat this usually means the repo is not synced into the Project's knowledge base — not a dead connector and not a deleted file; re-run /onboard, whose preflight probes the KB sync per §repo-not-synced, or attach the repo via Project knowledge → GitHub → Add); Linear MCP unreachable for `doc`-counter scan per `counter-allocation.md`.

For partial runs (founder ended the chat mid-Phase): emit `DONE` for that chat session with a note that the `discovery: state` Linear doc holds the resume point. Pausing is by design, not failure. The Phase 2 **deep-mode** paste-back wait is the same shape: after emitting the filled-in prompt artifacts, /discovery has nothing more to do until the founder pastes results back, so it emits `DONE` (or `NEEDS_CONTEXT` if it surfaced the wait as an open request) with `research_depth: deep` recorded in state as the resume anchor.

## /Chains

**Pattern:** P (phase-internal)
**Group:** B
**Within-group transitions:** Phase 1 → Phase 2 → Phase 3 (per `/discovery`'s three-phase internal protocol). Each phase's seal is an advisory PreCompact safe boundary (per D2.3 v1.3 §Within-group safe boundaries Group B row). Continuation is project-instruction-driven: after Phase N's output seals (Phase 1's domain map; Phase 2's drill-down notes; Phase 3's idea-brief), this skill instructs the model in-chat to begin Phase N+1's flow. No Task-invoke between phases (chat-Claude has no Task surface for intra-skill chaining; the model continues the narrative within the same chat).

**Within-group fresh-session nudges (per SOL-130).** Phase 1 (Discover) and Phase 2 (Research) are individually heavy. After Phase 1 seals (idea-brief-v<N> written + `discovery: state` updated) and again after Phase 2 seals (research summaries written + state updated), proactively offer the founder a choice — "continue here, or resume in a fresh chat" — without being asked. Tie the nudge to actual context pressure where detectable (long transcript, many tool round-trips) rather than firing it blanket every run, to avoid nagging. The handoff is cheap because the `[<MARKER>-DOC-NNNN] discovery: state` doc already supports resume; surface a ready-to-paste prompt:

```
Resume /discovery at Phase <N+1>.
Marker: <MARKER>
Read first: [<MARKER>-DOC-NNNN] discovery: state (holds phase, iteration, current_brief_doc_id).
Continue from the last sealed phase.
```

This is a lighter prompt than the Group-exit chat-end card; the full card still renders only at the Group B exit (Phase 3 idea-brief seal).
**Group exit trigger:** idea-brief seal at Phase 3's completion. The idea-brief is the load-bearing output `/constitution` consumes; its seal is gated on `/discovery`'s own manifest at `.cascade/manifests/<idea-brief-id>-discovery.json` being written with the `discovery.idea-brief-sealed` gate evaluation passing (per D3.4, if defined; otherwise the standard provenance gate suffices).
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant `normal`. Render it proactively at the Group B exit — before any next-group (`/constitution`) output; continuing inline into Group C is a defect per SOL-130 and the template's §Enforcement. After render, set `cascade:run-state.last_completed_group = "B"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<idea-brief-id>-discovery.json"`, flush, write `.cascade/handoff/last.md`. Do not Task-invoke anything.
**Next group entry:** C (`/constitution`). The founder pastes the handoff prompt into a new chat.
**Auto-fire compact handling:** not applicable. Group B runs in chat-Claude; no live PreCompact hook.
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<idea-brief-id>-discovery.json`. No chain intermediates (Phase 1 and Phase 2 outputs are intra-skill artifacts; only the idea-brief at Phase 3 produces a sealed manifest).

### v0.1 carry-forward (non-approve exits)

- **kill exit**: terminal. No chat-end card; the killed-idea ticket is the artifact.
- **pivot exit**: auto-restarts Phase 1 with pivot context internal to /discovery (not a Task-invocation chain — same skill re-entry). No group exit; cascade does not advance.
- **mid-flow**: resumable across chats and surfaces; re-invoke /discovery and the `discovery: state` Linear doc is the anchor.

## Notes

**Linear is canonical for /discovery state, not the filesystem.** Per the project's source-of-truth convention (see `CLAUDE.md` §Where work happens), all /discovery artifacts except deep-report files live in Linear. This matters because /discovery runs in chat-Claude by default (`workflow.discovery_surface: chat`), and chat-Claude reads the repo from Project knowledge (the repo is synced in once via the GitHub Integration and retrieved at runtime via Project-knowledge search — there is no callable GitHub file-read tool in chat) — local filesystem writes would be invisible to it without an intermediate commit + push. Linear documents are read directly via the Linear connector with no commit step.

**Resume contract across surfaces.** Each phase transition updates the `discovery: state` Linear doc with `{phase, iteration, status, last_action, timestamp, research_depth}`. Any /discovery invocation (chat or code) reads this doc first, then resumes at the indicated phase. `research_depth` (`null` | `light` | `deep`) tells a resuming session which Phase 2 mode is in flight, so it neither re-asks the depth gate nor switches modes mid-Phase: a `deep`-mode resume with mandatory prompts still missing CF2 summaries re-enters the paste-back wait, not the prompt-emit step. If both surfaces invoke /discovery concurrently, the last write wins — single-founder workflow, so true races are rare; defensive locking is v1.1.

**Five phases, not five turns.** Each phase spans multiple chat exchanges. The state document is what makes /discovery resumable.

**Phase 1 source-tagging matters downstream.** `(ai-recommended)` answers carry less weight in Phase 3 challenge than `(user)` answers. The Skeptic pass should scrutinize AI-recommended fields harder.

**Phase 2 CF2 structure is non-negotiable.** It's the formatter for every subsequent skill that reads research — /specify pulls top-3 by title/keyword similarity and quotes Key Findings verbatim into spec markdown. Deviation breaks downstream parsing.

**Why DOC prefix for research summaries.** Per `naming.md`, all Linear doc IDs use `[<MARKER>-DOC-NNNN]` regardless of type; type is encoded in the title (`research: <topic>`, `four-hat: <title>`, `constitution: v<semver>`, `discovery: state`, `discovery: idea-brief-v<N>`, `discovery: challenge-memo-iter<N>`).

**Deep research runs are time-bounded** — typical Phase 2 takes 1–3 days wall-clock per prompt (research, draft, review). Don't sprint Phase 2; the depth is the point. The research-investigator agent's freshness rule (6 months for ecosystem-velocity topics) is enforced at the agent layer.

**Deep reports are filesystem artifacts.** They are committed by Claude Code on its next code-side session — typically when /specify reads the top-3 research summaries to draft a parent spec. Chat-Claude does not write to the filesystem; it instructs the founder to run a code-side session to commit deep reports if they are not yet in the repo.

**Challenge memo is adversarial by design.** If every iteration approves, the checklist is too soft — review `docs/templates/discovery/challenge-checklist.md` and add sharper checks.

**Iteration cap is 3** because most ideas either converge or reveal terminal flaws within 3 cycles. Extending past the cap is fine but should be deliberate — repeated `refine` verdicts at cap usually mean the founder is attached to a flawed premise.

**Pivot is the most expensive exit** because it discards Phase 1+2 work. Use when the challenge memo surfaces a fundamentally different problem the founder should pursue. Cosmetic changes are `refine`, not `pivot`.

## Open questions (deferred to v1.1+)

- **Migration of pre-extraction RES-prefix research summaries.** Existing `[<MARKER>-RES-NNNN]` summaries from pre-extraction discovery runs remain valid by slug; a rename pass would break cross-references. Defer to a coordinated rename pass when slug churn is acceptable.
- **Cross-prompt deduplication.** The research-investigator runs each prompt independently; overlapping findings across the 5 mandatory prompts aren't auto-deduplicated. v1.1 candidate.
- **Concurrent-edit locking on `discovery: state`.** Solo-founder workflow makes true races rare, but adding a `lock_token` field plus check-and-set semantics is a v1.1 hardening pass.
- **Auto-iteration of Phase 3 challenge memo.** v0.1 produces one challenge memo per iteration; multi-perspective challenges (e.g. running four-hat critique against the idea brief inside Phase 3) is v1.1.
