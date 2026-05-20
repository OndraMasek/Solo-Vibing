# D2.3 v1.3 — Hybrid session-boundary mode (amendment-only pass)

**Status:** Design (v1.3 — focused amendments against v1.2; **not adversarially reviewed** as a unit. v1.3 applies the three critical amendments named in `D2_3_v1_2_and_D4_6_four_hat_review.md` plus one inline-absorbed important amendment.)
**Phase:** 2.
**Authored:** 2026-05-19, paired with `D2_1_trust_model_v2_1.md` and `D4_6_cascade_resume_v1_1.md`.
**Predecessor:** `D2_3_hybrid_session_boundary_v1_2.md` (v1.2 — the full amended doc from the v1.1 review). All v1.2 sections not named in this changelog carry forward verbatim into v1.3.
**Scope of v1.3:** four targeted edits surfaced in v1.2-paired review. The eight-group decision, the §Handoff verification predicate's check-set numbering, the §`/Chains` contract pattern partition, the §Execution surface per group commitments, and the chat-end card template structure are all unchanged.

## Changelog — v1.2 → v1.3

| # | Section revised | Change | Resolves | Severity |
|---|---|---|---|---|
| 1 | §Project Instructions block (step 1 path) | `docs/.cascade/run-state.json` → `.cascade/run-state.json`. | F-Eng-1 | Urgent |
| 2 | §Chat-end card template (handoff prompt fence "Read first" line) | Same path change. | F-Eng-1 | Urgent |
| 3 | §Cross-references (D2.1 v2 → D2.1 v2.1 label; path corollary) | Lockstep label update. | F-Eng-1 | Urgent |
| 4 | §Manual halt protocol — new Group D subsection | Specifies behavior when `/cascade-halt` fires mid-four-hat-fan-out. Default: outstanding subagents complete, parent writes their manifests per D2.1 v2.1, chat-end card renders manual-halt variant once all four hat manifests exist (or once the halt is registered if fewer than four hats had even started). | F-Eng-3 | Medium-High |
| 5 | §`/Chains` contract — per-pattern "the group's exit manifest is..." statement | Each of the seven patterns now names which stage's manifest serves as the group's exit manifest (the parent manifest, never a subagent or per-iteration). Inline absorption of F-Int-6. | F-Int-6 (absorbed inline) | Medium |
| 6 | §Handoff verification predicate — schema additions (`last_completed_group_exit_manifest_path`) | New `cascade:run-state` field naming the exit manifest path. Check 7's source is now this field. | F-Int-6 (absorbed inline) | Medium |
| 7 | §Cross-references (D4.5, D4.6) | D4.6 v1 → D4.6 v1.1 label update. | Lockstep with D4.6 v1.1 | Cleanup |

`last_group_artifacts[]` is **not** added to the schema. Per F-Eng-2 / F-Int-1 review disposition, D4.6 v1.1 reads the exit manifest's `outputs` field directly; v1.3's schema stays minimal on that surface.

The five other important amendments (F-Eng-4/F-Int-2 Stop-hook output shape, F-Eng-5 chat-Claude write atomicity, F-Eng-6 chat-Claude predicate failure modes, F-Rev-2 D4.6→D4.5 seam for stages without `--reconcile`, F-Int-3 `/build-kill` from sidecar vs live Group F, F-Usr-3 Project Instructions step 5) are **not** absorbed in v1.3. They remain in the important-amendment queue for the Child B implementation pass to surface inline if they become blockers, or for v0.2.x amendment otherwise. The ten lower-priority amendments (F-Usr-1/2/4/5, F-Rev-1/3/4/5, F-Int-4/5) are queued for v0.2.x without further treatment in v1.3.

---

## §Project Instructions block (v1.3 amended — step 1 path)

```markdown
This project uses the Solo-Vibing cascade in hybrid session-boundary mode.
The cascade runs across eight chat groups. Groups A–E, G, H run in
Claude.ai project chats (this surface). Group F (build + wrap) runs in
Claude Code. At every group boundary, you will see a chat-end card with a
handoff prompt — copy the fenced block and paste it into a new chat to
advance.

At chat start, before producing any output, do the following in order:
  1. Read `.cascade/run-state.json` from the repository (filesystem MCP).
  2. Read `.cascade/handoff/last.md` if it exists.
  3. Verify the user-pasted handoff context against run-state per the
     predicate schema in D2.3 v1.3 §Handoff verification predicate (checks 1–9).
  4. On any check failure, halt with the named halt code
     (§handoff-card-corrupted / §handoff-state-mismatch / §handoff-stale-queue
     / §handoff-missing) and surface recovery options. Do not advance the
     cascade on a failed predicate.
  5. On predicate pass, emit a short "Resuming cascade at <next-stage>"
     acknowledgment naming Marker, Product, Parent feature, Active ticket,
     Active milestone — for founder verification — and proceed.

If you receive no paste at chat start, halt §handoff-missing and surface
the three recovery paths: (a) prior chat sidebar history, (b) read
`.cascade/handoff/last.md`, (c) run `solo-cascade resume <group-letter>`
per D4.6 v1.1.

If at any point the founder invokes `/cascade-halt`, finish the current
within-group safe boundary, then render the chat-end card with the
manual-halt framing. Do not continue past the safe boundary.
```

Step 1's path change is the only step-1 edit. Steps 2 through 5, and the §handoff-missing / `/cascade-halt` paragraphs, are unchanged from v1.2 modulo the D4.6 → D4.6 v1.1 label update in the §handoff-missing paragraph.

---

## §Chat-end card template (v1.3 amended — handoff prompt fence)

The "Read first" line in the handoff-prompt fence updates:

```markdown
## ▼ HANDOFF PROMPT — copy everything between the fences ▼

```
Resume cascade at <next-stage>.

Marker: <MARKER>
Product: <product>
Parent feature: <parent_feature_name>
Group entry: <next-group-letter>
Active ticket: <ticket-id-or-N/A>
Active milestone: <milestone-id-or-N/A>
Queue version: <N>
Prior group exit: <this-group> sealed at <timestamp>
Read first:
  - cascade:run-state from .cascade/run-state.json
  - <next-stage>'s primary input: <path or linear-id>

Continue per the cascade's autonomy mode in .solo-config.json.
```

## ▲ END HANDOFF PROMPT ▲
```

The §Cascade state section's `Last sealed manifest` line keeps its v1.2 format but now derives from the new schema field `last_completed_group_exit_manifest_path` per the §Handoff verification predicate amendment below.

---

## §Manual halt protocol — Group D subsection (v1.3 — new)

This section adds a Group D subsection to the v1.2 manual-halt protocol. v1.2 specified manual-halt semantics for Group E (auto-fire chain in chat-Claude) and Group F (auto-fire chain in Claude Code). Group D's four-hat fan-out is neither — it is a parallel-subagent dispatch (Pattern F per §`/Chains` contract). The v1.3 amendment commits Group D's behavior.

**Inside Group D (parallel four-hat fan-out in chat-Claude):**

- If the founder invokes `/cascade-halt` while the four-hat fan-out is in flight (some hats complete, some still running as subagents), v1.3 commits the following default:
  - **Outstanding subagents complete.** Each subagent is a single Task-invoke that is naturally bounded in turn-budget (the subagent runs to its own completion or refusal; the parent does not interrupt mid-Task). The parent waits for each subagent's SubagentStop before reading its transcript.
  - **The parent writes each completed hat's manifest** per D2.1 v2.1's §Caller-side verification protocol — the same writer path that runs in the normal (non-halt) case. A subagent's transcript is durable on disk regardless of halt state; the manifest write reflects the verified transcript.
  - **The chat-end card renders the manual-halt variant** once all four hat manifests exist on disk (the parent has written them and verified their content per D2.1 v2.1's structural-verification protocol). Render is gated on the count: zero, one, two, three, or four hats may have started before the halt, and the card renders only after the started-count's manifests are all sealed.
  - **No spec seal occurs.** The `/specify` stage's own manifest is *not* written, because the spec-merge step (Pattern F's merge transition per §`/Chains` contract) requires all four hat manifests to evaluate the four-hat coverage gate; on a manual halt, the merge step is skipped and no spec.md is sealed. The chat-end card carries the framing: "Group D halted mid-fan-out; <N> of 4 hats' manifests sealed; no spec seal occurred. Downstream `/review` can see four-hat objection coverage was harvested but no spec exists to critique."
  - **`cascade:run-state` records the partial state.** Specifically: `cascade:run-state.last_completed_group` does **not** advance to D — Group D is not complete. A new field `partial_group_state.D.hat_manifests_sealed[]` lists the hat names whose manifests were written. The handoff prompt's `Group entry:` value is still D (resumption restarts Group D from a fresh chat); the new chat's verification predicate sees the partial-state field and surfaces a confirmation: *"Group D was previously halted with <N> of 4 hats sealed. Resume continues from a fresh four-hat fan-out (the prior hat manifests remain on disk for evidence; the new run produces a fresh set). Confirm to proceed."*

**Why this default.** The four-hat fan-out is the cascade's longest-spanning subagent dispatch and is the canonical case where mid-flight halt matters. Other options considered:
- *Kill outstanding subagents on halt.* Rejected — chat-Claude does not expose a programmatic subagent-kill primitive as of May 2026; the parent cannot reliably terminate a Task-invoke mid-flight from chat-Claude. The hook surface (SubagentStop) only fires on natural completion.
- *Render the chat-end card immediately on `/cascade-halt`, treating outstanding subagents as orphaned.* Rejected — produces orphaned manifests that downstream `/review` cannot rely on (some hats wrote their manifests after the halt; others did not). The "wait for all started subagents to complete naturally" rule keeps manifest-existence as a reliable signal.
- *Re-fire the four-hat fan-out from scratch on resume.* Rejected as the default — wastes the four-hat token budget for hats whose evidence is already on disk. Reserved as a `/cascade-halt --restart-from-scratch` flag for v0.2.x if dogfood reveals the discard-and-restart shape is sometimes desired.

The v1.3 default is "naturally complete, manifest, halt at the merge gate." The new chat's resumption then runs a fresh four-hat fan-out per the standard Group D Pattern F protocol; the prior hat manifests exist on disk as historical evidence but are not consumed by the resumed run.

**Records that Group D ran with a manual halt mid-fan-out** so that downstream `/review` can see four-hat objection coverage was harvested but no spec-seal occurred. This is the `partial_group_state.D.hat_manifests_sealed[]` field above; `/review`'s pre-flight reads it and adjusts its critique scope accordingly (no critique fires until a fresh Group D produces a sealed `/specify` manifest).

---

## §`/Chains` contract (v1.3 amended — per-pattern exit-manifest statement)

The v1.2 contract specified seven patterns. v1.3 adds one sentence per pattern naming the group's exit manifest. This resolves F-Int-6 inline; D4.6 v1.1 reads from the named manifest's `outputs` field directly.

The seven-pattern partition and the structured per-skill `/Chains` template remain unchanged from v1.2. Only the per-pattern exit-manifest sentence is new.

**Pattern T — terminal-render (Group A: `/onboard`).**
- *Within-group transitions:* none (single stage).
- *Group exit:* render the chat-end card; write `.cascade/handoff/last.md`; do not Task-invoke anything. Next-group entry: B.
- ***Group's exit manifest:*** `.cascade/manifests/<onboard-marker>-onboard.json` — `/onboard`'s own manifest. `cascade:run-state.last_completed_group_exit_manifest_path` records this path on Group A exit.

**Pattern P — phase-internal (Group B: `/discovery`).**
- *Within-group transitions:* Phase 1 → Phase 2 → Phase 3 (each a safe boundary for advisory PreCompact). Continuation is project-instruction-driven (chat-Claude).
- *Group exit:* at idea-brief seal (Phase 3 output), render the chat-end card; write `.cascade/handoff/last.md`. Next-group entry: C.
- ***Group's exit manifest:*** `.cascade/manifests/<idea-brief-id>-discovery.json` — `/discovery`'s own manifest, sealing the idea-brief output of Phase 3.

**Pattern M — amendment-internal (Group C: `/constitution`).**
- *Within-group transitions:* per-amendment vote-equivalent cycle (each a safe boundary). Continuation is founder-driven.
- *Group exit:* when the constitution is sealed (all proposed amendments resolved), render the chat-end card; write `.cascade/handoff/last.md`. Next-group entry: D.
- ***Group's exit manifest:*** `.cascade/manifests/<marker>-constitution.json` — `/constitution`'s own manifest, sealing the post-amendment constitution.md state.

**Pattern F — fan-out-internal (Group D: `/specify`).**
- *Within-group transitions:* step 1 → step 2 → four-hat fan-out (parallel four subagents) → merge → seal. Each subagent's SubagentStop is a safe boundary (advisory in chat-Claude); the parent reads each transcript and writes the subagent's manifest per D2.1 v2.1.
- *Group exit:* at spec seal (after all four hat manifests written and merged into `/specify`'s manifest), render the chat-end card; write `.cascade/handoff/last.md`. Next-group entry: E. SOL-62's spec.md inline render fires immediately before the chat-end card.
- ***Group's exit manifest:*** `.cascade/manifests/<ticket>-specify.json` — `/specify`'s parent manifest, containing the merged four-hat outputs. The four individual `<ticket>-<hat>.json` subagent manifests are *not* the exit manifest — they are inputs to `/specify`'s seal. On manual halt mid-fan-out per §Manual halt protocol Group D subsection, no exit manifest is written; recovery goes through `partial_group_state.D.hat_manifests_sealed[]`.

**Pattern C — auto-fire-chain (Group E: `/plan` → `/review` → `/update-linear`; also Group F-internal: `/build` → `/wrap`).**
- *Within-group transitions:* each stage Task-invokes the next via the `/Chains` section. In Claude Code (Group F) this is hook-driven Task-invoke; in chat-Claude (Group E) this is project-instruction-driven continuation.
- *Group exit:* the last stage in the chain (`/update-linear` for E; `/wrap` for F) renders the chat-end card; writes `.cascade/handoff/last.md`. Earlier stages in the chain never render the card.
- *Auto-fire compact behaviour:* applies in Group F per §Auto-fire compact behaviour; chain-pointer `next_chain_step` ensures resumption after compact.
- *Per-ticket variant for Group F:* the chain runs once per ticket. F→F[next-ticket] auto-renders the next ticket's handoff card per the v1.1 resolution of open-question 2.
- ***Group's exit manifest:***
  - For Group E: `.cascade/manifests/<ticket>-update-linear.json` — `/update-linear`'s own manifest, the chain's last stage's seal. `/plan` and `/review` manifests are intermediates; they are durable on disk per D2.1 v2.1 but are not the exit manifest.
  - For Group F: `.cascade/manifests/<ticket>-wrap.json` — `/wrap`'s own manifest, sealing the per-ticket build+wrap cycle. `/build`'s manifest is the intermediate; `/wrap` is the exit. F→F[next-ticket]: each ticket's Group F chat has its own exit manifest (one `<ticket>-wrap.json` per chat); the F→F handoff card derives from the current ticket's `/wrap` manifest.

**Pattern G — fan-out-aggregate (Group G: `/verify M-N`).**
- *Within-group transitions:* per-child dispatch (per D3.4's strategy dispatch matrix). Each child's verification is a safe boundary (advisory).
- *Group exit:* at milestone-level aggregation (after all children's gates evaluated and `children_gate_outcomes[]` written to `/verify`'s manifest), render the chat-end card; write `.cascade/handoff/last.md`. Next-group entry: H.
- ***Group's exit manifest:*** `.cascade/manifests/<milestone>-verify.json` — `/verify`'s own manifest, containing `children_gate_outcomes[]` aggregated across all children. Per-child intermediate manifests (if any are written) are inputs to `/verify`'s seal, not the exit manifest.

**Pattern N — terminal-no-handoff (Group H: `/retro`).**
- *Within-group transitions:* per-section seal of the retro doc (each a safe boundary, advisory).
- *Group exit:* at retro seal, render the chat-end card in the **terminal variant** (no handoff prompt; "What's next" reads "Next: open a new spec via `/specify` in a new chat to begin the next feature."). Write `.cascade/handoff/last.md` (for symmetry — D4.6 v1.1 still reads it if the founder needs to start a new feature with cascade state confirmation). No next-group entry.
- ***Group's exit manifest:*** `.cascade/manifests/<milestone>-retro.json` — `/retro`'s own manifest, sealing the milestone retrospective. D4.6 v1.1 reading this manifest is the path for "I forgot what state I'm in, where should I start the next feature" inspection.

**Implementation contract for the 0001 integration spec Child B (unchanged from v1.2).** Each of the eleven SKILL.md files gets a `/Chains` section structured as:

```markdown
## /Chains

**Pattern:** <T / P / M / F / C / G / N — one of the seven above>
**Group:** <A / B / C / D / E / F / G / H>
**Within-group transitions:** <list, or "none" for T-pattern terminal>
**Group exit trigger:** <named event — manifest seal, idea-brief seal, etc.>
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant <normal / reset-triggered / terminal>
**Next group entry:** <letter or "none" for N-pattern terminal>
**Auto-fire compact handling:** <applicable for C-pattern in Group F only; cite §Auto-fire compact behaviour>
**Group's exit manifest:** <path or "this skill's own manifest if exit stage, or 'not-this-skill — see <other-skill>' if a chain intermediate">
```

A new line is added in v1.3: **`Group's exit manifest`** identifies which skill seals the exit manifest. For the exit skill (e.g., `/wrap` in Group F, `/update-linear` in Group E), the line reads "this skill's own manifest." For chain-intermediate skills (`/plan`, `/review`, `/build`), the line reads "not-this-skill — see `<exit-skill>`," making it explicit which manifest D4.6 v1.1 reads.

The eleven skills map to patterns and exit-manifest roles as documented per the per-pattern statements above.

---

## §Handoff verification predicate — schema additions (v1.3 amended)

The v1.2 schema additions are carried forward verbatim. v1.3 adds one new field:

```json
{
  ...existing v1.2 fields...,
  "last_completed_group_exit_manifest_path": ".cascade/manifests/SOL-117-wrap.json"
}
```

- **`last_completed_group_exit_manifest_path`** is the path to the group's exit manifest, as defined per pattern in §`/Chains` contract. Set on every group-exit seal by the exit skill (Pattern T's skill itself; Pattern P/M/F/G/N's parent stage; Pattern C's chain-last stage). D4.6 v1.1 reads this field to locate the manifest whose `outputs` populates the re-derived card's "What just happened" and "What was produced" sections.

The check-7 source of `Last sealed manifest` (the card's `<ticket-stage>.json` line) is now this field. Check 7 itself is unchanged in semantics — it asserts the pasted card's `Last sealed manifest` value matches the on-disk `cascade:run-state.last_completed_group_exit_manifest_path` (and the file's sha256 matches `last_sealed_manifest_sha256`).

The other v1.2 schema fields (`queue_version`, `last_completed_group`, `last_group_exit_at`, `active_milestone`, `parent_feature_name`, `next_chain_step`) are unchanged. The schema example block in the source-of-truth file (`docs/.solo-config.json.template` per Child A) gains one new line; the field is required for v1.3+, optional during the v1.2-to-v1.3 transition (D4.6 v1.1 falls back to inferring the path from `last_completed_group` if the field is absent).

---

## §Cross-references (v1.3 amended — D2.1 v2.1 / D4.6 v1.1 labels)

- **D2.1 v2.1** — manifest chain and provenance binding are invariant under hybrid. The canonical run-state path moves to `.cascade/run-state.json` at repo root per v2.1's path amendment, aligning with D2.2's existing `.cascade/` namespace.
- **D2.2** — threshold model and PreCompact are unchanged at their core; the safe-boundary list narrows to within-group and only Group F is hook-enforced. D2.2 stays the authoritative source for the hook surface; v1.3's §Auto-fire compact behaviour adds the `next_chain_step` field to D2.2's side-channel snapshot schema (unchanged from v1.2).
- **D3.4** — gate firing order is unchanged at the named-gate level. Within a stage, gates evaluate before any safe boundary becomes PreCompact-eligible (per §Gate-then-safe-boundary ordering, unchanged from v1.2).
- **D4.1** — template bug batch is independent of D2.3's chat-boundary mechanics. Note that `docs/templates/chat-end-card.md` is *not* a D4.1 item (per §What this doc does not cover, unchanged from v1.2).
- **D4.2** — `/build-status` and `/build-kill` run as sidecar chats outside Group F's chat-hard boundary (per §Group F per-skill semantics, unchanged from v1.2). The chat-hard boundary applies only to `/build SOL-N → /wrap SOL-N`.
- **D4.5** — `--reconcile` and `--rerun` primitives are unchanged; they operate on the manifest chain D2.1 v2.1 establishes. **D4.5 no longer owns handoff recovery** — that role moves to D4.6 v1.1.
- **D4.6 v1.1** — `solo-cascade resume [<group-letter>]` is the framework-controlled recovery for §handoff-missing, §handoff-card-corrupted, and §handoff-state-mismatch. v1.1 drops the `last_group_artifacts[]` indirection; reads from the named exit manifest's `outputs` directly per §`/Chains` contract per-pattern statement.
- **D1** — Linear product layer's `/onboard` step sequence is amended by §`/onboard` integration point (new step 7 inserted between step 6 and the Group A chat-end card; unchanged from v1.2).
- **0001 integration spec** — Child A authors `docs/templates/chat-end-card.md`; Child B writes the eleven SKILL.md `/Chains` sections per the §`/Chains` contract. v1.3 is the binding spec for both children.

---

## What's not changing in v1.3

These v1.2 sections carry forward verbatim and are not re-stated in v1.3:

- §Decision (the eight-group decision and three auto-fire chain shapes).
- §Execution surface per group (the per-group surface/enforcement/hook/filesystem/recovery table).
- §Why this split, concretely (with confidence annotation) — the eight-boundary rationale table with evidence grades.
- §What narrows from D2.2 — the framing of D2.2's cross-stage role narrowing.
- §Within-group safe boundaries — the per-group safe-boundary table.
- §Gate-then-safe-boundary ordering — the four-step at-seal sequence.
- §Group-exit mechanics — the six-step group-exit sequence.
- §Group-exit mechanics atomicity — the `.cascade/handoff/last.md` write protocol with sha-embedded card.
- §Lost-card recovery — the three recovery paths.
- §Handoff verification predicate — the nine predicate checks (only the schema additions table gets one new field per the v1.3 amendment above; the check-set itself is unchanged).
- §Auto-fire compact behaviour — the seven-step PreCompact-fire sequence.
- §Manual halt protocol — the Group E and Group F subsections are unchanged from v1.2; the new Group D subsection is added per v1.3 amendment 4.
- §Group F per-skill semantics — the `/build`, `/build-status`, `/build-kill` sidecar split.
- §Chat-end card template — the template body and three render variants are unchanged; only the handoff-prompt fence's "Read first" line gets the path update per v1.3 amendment 2.
- §`/onboard` integration point — the eight-step `/onboard` sequence with step 7 (Project Instructions paste).
- §What changes vs SOL-63 as filed — the carry-forward sentence list.
- §What changes vs D2.2 as filed — the narrowing-then-extension framing.
- §Effect on the SOL-55..63 batch — the per-ticket disposition.
- §Open questions — all six resolved with their v1.2 annotations.
- §Deferred measurement — M-1 through M-4 measurement deferrals (M-5 / M-6 from the v1.2-paired review remain queued for v0.2.x per the lower-priority amendment list).
- §What this doc does not cover — per-skill `/Chains` rewrites (owned by Child B), chat-end-card template authorship (owned by Child A), `solo-cascade resume` CLI implementation (owned by D4.6 v1.1's implementation pass), backwards compat (v0.3 decision), CLI escape hatch (v0.3 candidate), chat-Claude compact behaviour (opaque, tolerated).

v1.3 is a focused amendment doc. v1.2 remains the authoritative source for all sections above; v1.3 is canonical only for the four sections it amends.
