# Child B deliverable — eleven SKILL.md `/Chains` sections (v1.3 contract)

**Authored:** 2026-05-19, against `D2_3_hybrid_session_boundary_v1_3.md` §`/Chains` contract.
**Authoritative source:** v1.3's §`/Chains` contract pattern partition and per-pattern exit-manifest statement.
**Target:** the eleven `.claude/skills/*/SKILL.md` files in the framework repo. Each section below is a complete drop-in `/Chains` block that replaces (or, if v0.1 had no `/Chains` section, adds) the section in the named SKILL.md.

## How to use this deliverable

For each of the eleven skills:
1. Open `.claude/skills/<skill-name>/SKILL.md` in the framework repo.
2. Locate the existing `## /Chains` section (v0.1 had a free-form "stage X Task-invokes stage Y" form per CLAUDE.md's "each stage Task-invokes the next per its own Chains section" commitment).
3. Replace the existing section with the v1.3-shape block below, anchored on the same `## /Chains` heading.
4. Run a sanity grep: every SKILL.md should have exactly one `## /Chains` heading after the replacement, and every block should declare `Pattern:`, `Group:`, `Within-group transitions:`, `Group exit trigger:`, `Group exit render:`, `Next group entry:`, `Auto-fire compact handling:`, `Group's exit manifest:` — eight required lines.

The block format is identical across all eleven skills (per the v1.3 contract). Only the field values vary.

The drop-in blocks are written in the second person ("this skill Task-invokes...") because the SKILL.md surface is read by the executing model at runtime, and second-person address matches the v0.1 convention in those files.

---

## 1. `.claude/skills/onboard/SKILL.md` — Pattern T (Group A)

```markdown
## /Chains

**Pattern:** T (terminal-render)
**Group:** A
**Within-group transitions:** none. `/onboard` is a single-stage group; its eight internal steps (per D2.3 v1.3 §`/onboard` integration point) are intra-stage progression, not within-group transitions in the contract sense. Each internal step is an advisory PreCompact safe boundary (per D2.3 v1.3 §Within-group safe boundaries Group A row) but no Task-invoke fires between them.
**Group exit trigger:** completion of step 8 in `/onboard`'s internal sequence, i.e., immediately after step 7 (founder confirms the Project Instructions paste-block was pasted into Claude.ai → Project → Instructions; `cascade:run-state.project_instructions_pasted_at` is timestamp-set) and the `onboard.linear-projects` and `onboard.config-write` gates per D3.4 §onboard gates have passed and `/onboard`'s manifest at `.cascade/manifests/<marker>-onboard.json` has been written.
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant `normal`. Render is the eighth and final step of `/onboard`'s internal sequence. After render, set `cascade:run-state.last_completed_group = "A"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<marker>-onboard.json"`, flush `cascade:run-state` per D2.3 v1.3 §Group-exit mechanics step 2, write `.cascade/handoff/last.md` per §Group-exit mechanics atomicity. Do not Task-invoke anything.
**Next group entry:** B (`/discovery`). The founder copies the handoff prompt from the chat-end card and pastes it into a new chat to advance.
**Auto-fire compact handling:** not applicable. Group A runs in chat-Claude (per D2.3 v1.3 §Execution surface per group), which has no live PreCompact hook; auto-fire compact behaviour applies only in Group F.
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<marker>-onboard.json`. No subagents; no chain intermediates.
```

---

## 2. `.claude/skills/discovery/SKILL.md` — Pattern P (Group B)

```markdown
## /Chains

**Pattern:** P (phase-internal)
**Group:** B
**Within-group transitions:** Phase 1 → Phase 2 → Phase 3 (per `/discovery`'s three-phase internal protocol). Each phase's seal is an advisory PreCompact safe boundary (per D2.3 v1.3 §Within-group safe boundaries Group B row). Continuation is project-instruction-driven: after Phase N's output seals (Phase 1's domain map; Phase 2's drill-down notes; Phase 3's idea-brief), this skill instructs the model in-chat to begin Phase N+1's flow. No Task-invoke between phases (chat-Claude has no Task surface for intra-skill chaining; the model continues the narrative within the same chat).
**Group exit trigger:** idea-brief seal at Phase 3's completion. The idea-brief is the load-bearing output `/constitution` consumes; its seal is gated on `/discovery`'s own manifest at `.cascade/manifests/<idea-brief-id>-discovery.json` being written with the `discovery.idea-brief-sealed` gate evaluation passing (per D3.4, if defined; otherwise the standard provenance gate suffices).
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant `normal`. After render, set `cascade:run-state.last_completed_group = "B"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<idea-brief-id>-discovery.json"`, flush, write `.cascade/handoff/last.md`. Do not Task-invoke anything.
**Next group entry:** C (`/constitution`). The founder pastes the handoff prompt into a new chat.
**Auto-fire compact handling:** not applicable. Group B runs in chat-Claude; no live PreCompact hook.
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<idea-brief-id>-discovery.json`. No chain intermediates (Phase 1 and Phase 2 outputs are intra-skill artifacts; only the idea-brief at Phase 3 produces a sealed manifest).
```

---

## 3. `.claude/skills/constitution/SKILL.md` — Pattern M (Group C)

```markdown
## /Chains

**Pattern:** M (amendment-internal)
**Group:** C
**Within-group transitions:** per-amendment vote-equivalent cycle. Each amendment proposal → founder confirmation → constitution edit → cycle is a within-group transition (an advisory PreCompact safe boundary per D2.3 v1.3 §Within-group safe boundaries Group C row). Continuation is founder-driven: after each amendment's founder confirmation, this skill cycles back to "any further amendments proposed?" and proceeds when the founder confirms no more.
**Group exit trigger:** constitution seal — founder confirms all proposed amendments resolved and the `/constitution` manifest at `.cascade/manifests/<marker>-constitution.json` has been written (sealing the post-amendment `docs/constitution.md` state).
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant `normal`. After render, set `cascade:run-state.last_completed_group = "C"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<marker>-constitution.json"`, flush, write `.cascade/handoff/last.md`. Do not Task-invoke anything.
**Next group entry:** D (`/specify`). The founder pastes the handoff prompt into a new chat.
**Auto-fire compact handling:** not applicable. Group C runs in chat-Claude; no live PreCompact hook.
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<marker>-constitution.json`. The marker-scoped (not ticket-scoped) path reflects that the constitution governs all features within a marker, not a single feature.
```

---

## 4. `.claude/skills/specify/SKILL.md` — Pattern F (Group D)

```markdown
## /Chains

**Pattern:** F (fan-out-internal)
**Group:** D
**Within-group transitions:** step 1 (strategy proposal — `spec.strategy-annotation` gate per D3.4 fires here; founder explicitly accepts or revises) → step 2 (AC drafting per `/specify` step 2) → four-hat fan-out (parallel four subagents: `user`, `engineer`, `pm`, `skeptic` per `.claude/agents/four-hat-panel/`) → merge (parent reads each subagent transcript and writes the subagent's manifest per D2.1 v2.1 §Caller-side verification) → seal. Each subagent's SubagentStop is an advisory PreCompact safe boundary (per D2.3 v1.3 §Within-group safe boundaries Group D row — four discrete safe boundaries, one per hat). Continuation between steps is project-instruction-driven (chat-Claude); the four-hat fan-out is dispatched via parallel Task-invokes to the named subagents.
**Group exit trigger:** spec seal — all four hat manifests at `.cascade/manifests/<ticket>-{user,engineer,pm,skeptic}.json` exist and pass structural verification; the merged outputs are written into `/specify`'s parent manifest at `.cascade/manifests/<ticket>-specify.json`; and the five `spec.*` gates (`spec.strategy-annotation`, `spec.pyramid-shape`, `spec.failing-test-seed`, `spec.perceptual-artifact-path`, `spec.provenance`) per D3.4 §spec gates evaluate and pass. SOL-62's `spec.md` inline render fires immediately before the chat-end card (`docs/specs/<ticket>/spec.md` is rendered inline in chat).
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant `normal`. After render, set `cascade:run-state.last_completed_group = "D"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<ticket>-specify.json"`, flush, write `.cascade/handoff/last.md`. Do not Task-invoke anything.

**Manual-halt branch:** if `/cascade-halt` fires mid-fan-out, follow D2.3 v1.3 §Manual halt protocol Group D subsection: wait for outstanding subagents to complete naturally, write each completed hat's manifest per D2.1 v2.1, then render the chat-end card with the manual-halt variant (the second `<optional>` block of the template). No spec seal occurs in this branch — the `/specify` manifest is *not* written, and `cascade:run-state.last_completed_group` does *not* advance to D. Instead, `cascade:run-state.partial_group_state.D.hat_manifests_sealed[]` records which hats sealed before halt. The handoff prompt's `Group entry:` value remains D so resumption restarts Group D from a fresh chat (the prior hat manifests remain on disk as historical evidence; the new run produces a fresh set).

**Next group entry:** E (`/plan` → `/review` → `/update-linear` auto-fire chain) on normal exit; D (re-entry) on manual-halt exit.
**Auto-fire compact handling:** not applicable. Group D runs in chat-Claude; no live PreCompact hook. The per-subagent safe boundaries in §Within-group safe boundaries Group D row are advisory in v0.2 (PreCompact deferral semantics fire only in Group F).
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<ticket>-specify.json` — containing the merged four-hat outputs in its `outputs` field. The four `<ticket>-<hat>.json` subagent manifests are *inputs* to `/specify`'s seal, not the exit manifest. D4.6 v1.1's re-derivation reads `<ticket>-specify.json` to populate the chat-end card's "What was produced" section; the subagent manifests are not consulted by D4.6.
```

---

## 5. `.claude/skills/plan/SKILL.md` — Pattern C, Group E intermediate

```markdown
## /Chains

**Pattern:** C (auto-fire-chain, Group E variant)
**Group:** E
**Within-group transitions:** this skill is the first stage in the Group E chain (`/plan` → `/review` → `/update-linear`). On `/plan` manifest seal at `.cascade/manifests/<ticket>-plan.json` (after the `plan.provenance`, `plan.children-have-strategies-for-hybrid`, `plan.decomposition-doc-sealed` gates per D3.4 §plan gates pass), this skill Task-invokes `/review` to advance the chain. In chat-Claude (per D2.3 v1.3 §Execution surface per group Group E row), "Task-invoke" is realised as project-instruction-driven narrative continuation — this skill instructs the model in-chat to begin `/review`'s flow immediately after sealing `/plan`'s manifest, citing the §`/Chains` contract's Group E auto-fire-chain commitment. Plan-internal safe boundaries (after decomposition seal per D2.3 v1.3 §Within-group safe boundaries Group E row) are advisory.
**Group exit trigger:** not this skill. `/plan` is a Group E chain intermediate; the chain's exit fires on `/update-linear`'s seal.
**Group exit render:** not this skill. Chain-intermediate stages never render the chat-end card. After `/plan`'s manifest seals, this skill continues to `/review` without rendering.
**Next group entry:** not this skill. The chain advances internally: `/plan` → `/review` → `/update-linear`; `/update-linear`'s `/Chains` section names Group E's next-group entry as F.
**Auto-fire compact handling:** not applicable for chat-Claude. Group E runs in chat-Claude; no live PreCompact hook. If a hypothetical future v0.3+ moves Group E to Claude Code (per D2.3 v1.3 §Within-group safe boundaries Group E row's "advisory" framing leaving the door open), auto-fire compact handling would apply with `next_chain_step` set to `"review"` on /plan's safe boundary; v0.2 does not implement this.
**Group's exit manifest:** not-this-skill — see `/update-linear`. `/plan`'s manifest at `.cascade/manifests/<ticket>-plan.json` is a chain intermediate, durable on disk per D2.1 v2.1 but not the Group E exit manifest. D4.6 v1.1 reads `/update-linear`'s manifest for Group E re-derivation, not `/plan`'s.
```

---

## 6. `.claude/skills/review/SKILL.md` — Pattern C, Group E intermediate

```markdown
## /Chains

**Pattern:** C (auto-fire-chain, Group E variant)
**Group:** E
**Within-group transitions:** this skill is the middle stage in the Group E chain. On `/review` manifest seal at `.cascade/manifests/<ticket>-review.json` (after the four-hat objection-coverage check fires as SubagentStop in Claude Code — or as the chat-Claude advisory analog in Group E — per D3.4 §review gates, and after the other `review.*` gates pass), this skill Task-invokes `/update-linear` to advance the chain. In chat-Claude, "Task-invoke" is project-instruction-driven continuation as in `/plan`. Review-internal safe boundaries: after the four-hat panel completes (per D2.3 v1.3 §Within-group safe boundaries Group E row, advisory in chat-Claude); after `/review`'s critique consolidation.
**Group exit trigger:** not this skill. `/review` is a Group E chain intermediate.
**Group exit render:** not this skill. Chain-intermediate; after `/review`'s manifest seals, this skill continues to `/update-linear` without rendering.
**Next group entry:** not this skill. See `/update-linear`'s `/Chains` section for the Group E exit transition.
**Auto-fire compact handling:** not applicable for chat-Claude. Same disposition as `/plan`'s row.
**Group's exit manifest:** not-this-skill — see `/update-linear`. `/review`'s manifest at `.cascade/manifests/<ticket>-review.json` is a chain intermediate. The four-hat-panel agent's per-hat outputs (if Group E's `/review` also runs a four-hat fan-out, distinct from Group D's `/specify` fan-out) are inputs to `/review`'s seal, not the exit manifest.
```

---

## 7. `.claude/skills/update-linear/SKILL.md` — Pattern C, Group E exit

```markdown
## /Chains

**Pattern:** C (auto-fire-chain, Group E variant — chain's last stage)
**Group:** E
**Within-group transitions:** this skill is the chain's last stage; no further intra-Group-E transitions after seal. The chain `/plan` → `/review` → `/update-linear` terminates here.
**Group exit trigger:** `/update-linear` manifest seal at `.cascade/manifests/<ticket>-update-linear.json` after the `update-linear.diff-applied` gate per D3.4 §update-linear gates passes (Linear writes for Backlog tickets, decomposition.md diff applied, parent manifest's `outputs` reflects the new child tickets).
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant `normal`. After render, set `cascade:run-state.last_completed_group = "E"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<ticket>-update-linear.json"`, also increment `cascade:run-state.queue_version` (the Group E exit is the canonical queue-write event — `/plan`'s decomposition initially assigns the queue and `/update-linear` makes it Linear-canonical; `queue_version++` here defeats stale-card replay across the E→F boundary). Flush, write `.cascade/handoff/last.md`. Do not Task-invoke anything.
**Next group entry:** F (the first Group F chat: `/build SOL-<first-ticket>` where `<first-ticket>` is the first ticket in the decomposition's queue order). The founder pastes the handoff prompt into a new Claude Code session (Group F runs in Claude Code per §Execution surface per group; the handoff card includes the surface-shift framing).
**Auto-fire compact handling:** not applicable for chat-Claude. Group E lives in chat-Claude; the auto-fire compact behaviour applies only in Group F (per D2.3 v1.3 §Auto-fire compact behaviour scope).
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<ticket>-update-linear.json`. `/plan`'s and `/review`'s manifests are inputs (durable per D2.1 v2.1 but not the exit manifest). D4.6 v1.1 reads `/update-linear`'s manifest's `outputs` field to populate the chat-end card's "What was produced" section for Group E re-derivation.
```

---

## 8. `.claude/skills/build/SKILL.md` — Pattern C, Group F intermediate

```markdown
## /Chains

**Pattern:** C (auto-fire-chain, Group F variant — chain's first stage; runs in Claude Code per §Execution surface per group)
**Group:** F
**Within-group transitions:** this skill is the first stage in the Group F chain (`/build` → `/wrap`). On `/build` manifest seal at `.cascade/manifests/<ticket>-build.json` (after Ralph completes its iteration cycle, `/build --finalize` runs, and the `build.provenance`, `build.pyramid-tampering`, `build.test-execution` gates per D3.4 §build gates pass), this skill Task-invokes `/wrap` to advance the chain. In Claude Code (per §Execution surface per group), "Task-invoke" is hook-driven: the Stop hook's orchestrator (per D2.2 §Hook resolution #3 single-Stop-hook pattern) reads `/build`'s sealed manifest and dispatches `/wrap`. Build-internal safe boundaries: **per-tool-call grain inside Ralph's iteration** (per D2.3 v1.3 §Within-group safe boundaries Group F row — every `Write` / `Edit` / `Bash` tool call inside Ralph is a hook-enforced PreCompact safe boundary); between Ralph iterations; at `/build --finalize`.
**Group exit trigger:** not this skill. `/build` is a Group F chain intermediate; the chain's exit fires on `/wrap`'s seal.
**Group exit render:** not this skill. Chain-intermediate; after `/build`'s manifest seals, the Stop hook Task-invokes `/wrap` without rendering.
**Next group entry:** not this skill. See `/wrap`'s `/Chains` section for the Group F exit transition (F→F[next-ticket] or F→G).
**Auto-fire compact handling:** **applies.** Per D2.3 v1.3 §Auto-fire compact behaviour, if PreCompact fires at a within-build safe boundary (e.g., between Ralph iterations or after a tool call), the cascade sets `cascade:run-state.next_chain_step = "wrap"` if `/build` is at its final safe boundary (post `/build --finalize`), or to `"build"` if compact fires mid-build (chain-pointer ensures resumption to the same stage). The side-channel snapshot `cascade:run-state.next_chain_step` is also written to `.cascade/session/precompact-<session_id>-<timestamp>.json` per D2.2's side-channel snapshot mechanism. After compact, SessionStart=compact emits the factual block including `next_chain_step`; the first post-compact Stop-hook execution reads `cascade:run-state.next_chain_step` and Task-invokes accordingly (clearing the field after Task-invoke fires).
**Group's exit manifest:** not-this-skill — see `/wrap`. `/build`'s manifest at `.cascade/manifests/<ticket>-build.json` is a chain intermediate, the bridge between the Ralph-iteration-loop's evidence and `/wrap`'s seal. D4.6 v1.1 reads `/wrap`'s manifest for Group F re-derivation, not `/build`'s.

**Interaction with sidecar commands.** Per D2.3 v1.3 §Group F per-skill semantics, `/build-status <ticket>` and `/build-kill <ticket>` are sidecar chats outside Group F's chat-hard boundary. A `/build-kill` from a sidecar invalidates this Group F chat's `/build` run; on returning to this chat, the founder may invoke `/build SOL-N --continue` (per D4.2) or close the chat without further action. If `/cascade-halt` was also invoked from the sidecar (after the kill), `cascade:run-state.manual_halt = true` is set; this chat detects it on its next within-group safe boundary and renders the manual-halt chat-end card (via `/wrap` if the chain continued, or directly if `/build` halted before chaining).
```

---

## 9. `.claude/skills/wrap/SKILL.md` — Pattern C, Group F exit

```markdown
## /Chains

**Pattern:** C (auto-fire-chain, Group F variant — chain's last stage; runs in Claude Code)
**Group:** F
**Within-group transitions:** this skill is the chain's last stage; no further intra-Group-F transitions after seal. The chain `/build` → `/wrap` terminates here per ticket; the next Group F chat (a fresh `/build SOL-<next-ticket>`) is a new chat-hard boundary, not a within-group transition. Wrap-internal safe boundaries: before `/wrap`'s Linear-write step (per D2.3 v1.3 §Within-group safe boundaries Group F row).
**Group exit trigger:** `/wrap` manifest seal at `.cascade/manifests/<ticket>-wrap.json` after the `wrap.provenance`, `wrap.tests-green`, `wrap.mirror-sha-match`, `wrap.linear-state-updated` gates per D3.4 §wrap gates pass.
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant `normal` on standard exit; variant `reset-triggered` if D2.2 band 3 triggered the exit (Group F is the only group with live D2.2 enforcement, so the reset-triggered variant is Group-F-exclusive); variant `manual-halt` if `cascade:run-state.manual_halt = true` was set by a sidecar `/cascade-halt` per D2.3 v1.3 §Manual halt protocol Group F subsection. After render, set `cascade:run-state.last_completed_group = "F"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<ticket>-wrap.json"`, flush, write `.cascade/handoff/last.md`. The Stop hook then fires SessionEnd for async telemetry per D2.2 (Group F is the only group with a live SessionEnd event).
**Next group entry:** **F[next-ticket]** if the queue contains more tickets (the chat-end card's handoff prompt names the next ticket: `Active ticket: SOL-<next-ticket>`, `Group entry: F`; the founder opens a new Claude Code session and pastes — auto-renders next-ticket per D2.3 v1.2's v1.1-resolved open-question 2). **G** if this was the last ticket in the queue (the queue is empty: `cascade:run-state.next_ticket == null`; the handoff prompt names `Group entry: G`, `Active milestone: <milestone-id>` for the per-child `/verify` fan-out).
**Auto-fire compact handling:** **applies, edge case.** Per D2.3 v1.3 §Auto-fire compact behaviour edge case, `/wrap` is the chain's last stage; if PreCompact fires at `/wrap`'s last safe boundary (just before group exit), `cascade:run-state.next_chain_step` is set to `null` (no further chain stage). The post-compact Stop hook proceeds with its normal group-exit decision (render the chat-end card, no further Task-invoke). If PreCompact fires earlier in `/wrap` (before the last safe boundary), `next_chain_step` is set to `"wrap"` so the post-compact Stop hook resumes from the chain's current position.
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<ticket>-wrap.json`. `/build`'s manifest is the chain intermediate (per `/build`'s `/Chains` section). D4.6 v1.1 reads `/wrap`'s manifest's `outputs` field to populate the chat-end card's "What was produced" section for Group F re-derivation. Each per-ticket Group F chat has its own exit manifest (one `<ticket>-wrap.json` per chat); F→F[next-ticket] re-derivation in D4.6 v1.1 reads the *previous* ticket's `/wrap` manifest (the just-completed chat's), not the next ticket's pending state.
```

---

## 10. `.claude/skills/verify/SKILL.md` — Pattern G (Group G)

```markdown
## /Chains

**Pattern:** G (fan-out-aggregate)
**Group:** G
**Within-group transitions:** per-child dispatch per D3.4 §`/verify` gate dispatch by strategy. Each child in the milestone's `children[]` list is dispatched in sequence: walking-skeleton / api-boundary / capability-cluster children route to `verify.perceptual-evidence` (D3.3 P1–P4 per strategy); refactor-spike children route to `verify.invariance` (D3.3 P5–P9); hybrid children recurse one level per D3.4 §hybrid-nesting-too-deep. Each child's gate evaluation is an advisory PreCompact safe boundary (per D2.3 v1.3 §Within-group safe boundaries Group G row). Continuation is project-instruction-driven (chat-Claude): after one child's gate evaluation seals, this skill instructs the model in-chat to dispatch the next child. The fan-out is *sequential* (not parallel like Group D's four-hat) because per-child gate evaluation may depend on cross-child evidence aggregation; v0.3+ may parallelize after measurement.
**Group exit trigger:** milestone-level aggregation. After all children's gates have been evaluated, this skill writes `children_gate_outcomes[]` per D3.4 §Manifest schema additions into `/verify`'s manifest at `.cascade/manifests/<milestone>-verify.json` (refactor-spike children also record `seal_pass_set_count` and `verify_pass_set_count`). Multi-child halt-card aggregation per D3.4 §Aggregation rules applies: within a gate, earliest-firing predicate's halt is primary; across children, each stands alone in the milestone roll-up.
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant `normal`. After render, set `cascade:run-state.last_completed_group = "G"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<milestone>-verify.json"`, flush, write `.cascade/handoff/last.md`. Do not Task-invoke anything.
**Next group entry:** H (`/retro`). The founder pastes the handoff prompt into a new chat.
**Auto-fire compact handling:** not applicable. Group G runs in chat-Claude; no live PreCompact hook.
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<milestone>-verify.json`, scoped by milestone (not ticket) because `/verify` aggregates across all children in the milestone. Per-child intermediate manifests (if any are written separately from `children_gate_outcomes[]`) are inputs to `/verify`'s seal, not the exit manifest. D4.6 v1.1 reads `/verify`'s manifest's `outputs` field to populate the chat-end card's "What was produced" section for Group G re-derivation; the per-child gate outcomes are surfaced as a structured summary.
```

---

## 11. `.claude/skills/retro/SKILL.md` — Pattern N (Group H, terminal)

```markdown
## /Chains

**Pattern:** N (terminal-no-handoff)
**Group:** H
**Within-group transitions:** per-section seal of the retro doc. `/retro`'s output is structured per D3.4 §retro gates (and its own internal sectioning): tag-distribution section (count children per strategy from `children_gate_outcomes[]` read from `/verify` manifests); per-gate outcome counts (e.g., "11/12 children passed `verify.perceptual-evidence`; 1 halted on `§perceptual-evidence-missing/byte-stability-failed`"); session-discipline retrospective (cost, iteration counts, manual-halt incidents from `cascade:run-state` and per-session telemetry); next-milestone backlog reflections. Each section seal is an advisory PreCompact safe boundary (per D2.3 v1.3 §Within-group safe boundaries Group H row).
**Group exit trigger:** retro seal — all retro sections complete; `/retro`'s manifest at `.cascade/manifests/<milestone>-retro.json` written; the retro doc itself written at `docs/specs/<milestone>/retro.md` (or the milestone's equivalent path per `/onboard`'s product-layer mirror).
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant **`terminal`**. The terminal variant has no handoff-prompt fence (no copy-paste step needed; the cascade has reached its terminal); the "What's next" section reads: "Next: open a new spec via `/specify` in a new chat to begin the next feature." After render, set `cascade:run-state.last_completed_group = "H"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<milestone>-retro.json"`, flush, write `.cascade/handoff/last.md` (for symmetry — D4.6 v1.1's `solo-cascade resume` halts §cascade-state-terminal if invoked at this point, surfacing "start a new feature via `/specify`" as the recovery; the on-disk `last.md` carries the same terminal-variant content for founder reference).
**Next group entry:** **none** (terminal). The milestone is complete; the cascade has reached the end of its v0.2 traversal.
**Auto-fire compact handling:** not applicable. Group H runs in chat-Claude; no live PreCompact hook.
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<milestone>-retro.json`. The retro doc itself at `docs/specs/<milestone>/retro.md` is the perceptual artifact (per D3.3 if Group H's strategy is treated as walking-skeleton-shaped for its own perceptual gate; v0.2 does not gate Group H beyond `/retro`'s own internal section completion).
```

---

## Notes for the executing session (Child B implementation pass)

**Pre-flight before editing the SKILL.md files.** Confirm the v0.1 SKILL.md files exist at the paths listed above (`.claude/skills/{onboard,discovery,constitution,specify,plan,review,update-linear,build,wrap,verify,retro}/SKILL.md`). Per `repo-state-summary.md`, all eleven existed in v0.1. The integration is amendment, not creation.

**Per-skill edit sequence.** For each skill: (1) read the existing `## /Chains` section; (2) replace it with the v1.3-shape block above; (3) verify the surrounding sections (frontmatter, decision-table, step prompts) are unchanged; (4) commit one-skill-at-a-time so a partial pass leaves a coherent intermediate state.

**Cross-skill consistency check.** After all eleven are updated, run:
```bash
grep -L "Pattern: T\|Pattern: P\|Pattern: M\|Pattern: F\|Pattern: C\|Pattern: G\|Pattern: N" .claude/skills/*/SKILL.md
```
Should return zero hits — every SKILL.md should declare exactly one of the seven patterns.

```bash
grep -c "## /Chains" .claude/skills/*/SKILL.md
```
Should return `1` for every file — no skill should have two `/Chains` sections (a partial edit would produce this).

```bash
grep "last_completed_group_exit_manifest_path" .claude/skills/*/SKILL.md | wc -l
```
Should return at least 11 (each /Chains block references this field at the group exit; intermediate skills reference it via "see `<exit-skill>`" rather than directly, so the count could vary 11–17).

**Frontmatter `name` field — sanity check.** Each SKILL.md's frontmatter `name` field should match the skill filename (`name: onboard` for `onboard/SKILL.md`, etc.). The v0.1 framework reportedly follows this convention; verify before pasting in case of drift.

**Important amendments to surface during the pass.** The five remaining important amendments from `D2_3_v1_2_and_D4_6_four_hat_review.md` (F-Eng-4 Stop-hook output shape; F-Eng-5 chat-Claude write atomicity; F-Eng-6 predicate failure modes; F-Rev-2 D4.6→D4.5 seam wider; F-Int-3 `/build-kill` from sidecar) may surface as blockers during specific skills' edits. F-Eng-5 is most likely to surface in Groups A–E and G–H SKILL.md edits (chat-Claude write atomicity matters for the chat-end card render step). F-Int-3 is most likely to surface in `/build`'s edit (the sidecar interaction text is part of the proposed `/build/SKILL.md` block above). If any blocks the edit, surface to the design owner for inline v1.3 / D4.6 v1.1 amendment in the same session.

**Handoff to the next session.** If Child B does not finish in this session, the handoff is "continue Child B at the next skill in the order above (interrupted-at-skill recorded in `cascade:run-state.partial_child_state.B.skills_completed[]`)." If Child B finishes, the handoff is "begin Child A — author `docs/templates/chat-end-card.md` per D2.3 v1.3 §Chat-end card template."
