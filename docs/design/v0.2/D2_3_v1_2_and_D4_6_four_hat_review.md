# D2.3 v1.2 + D4.6 — Paired four-hat adversarial review

**Status:** Review.
**Phase:** 2 (D2.3 v1.2) and 4 (D4.6) — paired because v1.2 and D4.6 were authored in lockstep
and seal each other's recovery contract.
**Reviews:** `D2_3_hybrid_session_boundary_v1_2.md` (the v1.2 amendments-only pass against v1.1,
closing 18 of 24 findings from `D2_3_four_hat_review.md`) and `D4_6_cascade_resume.md` (the new
sibling cascade-resume primitive, authored to discharge F-Eng-3, F-Int-5, F-Rev-4 from the v1.1
review).
**Paired-review framing:** v1.2's verification contract (§Handoff verification predicate) and
D4.6's re-derivation contract (§Composition with §Handoff verification predicate) are mutually
load-bearing — v1.2 names D4.6 as the framework-controlled recovery for three halt codes,
D4.6 satisfies v1.2's predicate by construction. Either doc reviewed in isolation would miss
the seam; this review evaluates both jointly.
**Date:** 2026-05-19.
**Predecessor:** `D2_3_four_hat_review.md` (v1.1 review; recommendation (b) amendments needed —
the inputs to v1.2 and D4.6).

This review tests:
- Whether v1.2's commitment that Group F → Claude Code and Groups A–E, G, H → chat-Claude
  (§Execution surface per group) holds structurally, given that the chat-Claude enforcement
  layer (project-instruction interpretation) is admitted to be best-effort.
- Whether D4.6 as a sibling of D4.5 (rather than a sixth D4.5 primitive) holds up under
  the seam the §cascade-resume-manifest-chain-broken halt creates.
- Whether the six new/revised halts (§handoff-card-corrupted, §handoff-stale-queue,
  §manual-halt-pending, §cascade-state-missing, §cascade-state-terminal,
  §cascade-resume-manifest-chain-broken plus three more in D4.6) coherently tile the
  failure surface.

---

## Engineer hat — what's mechanically wrong, underspecified, or fragile

The amendments are mostly mechanically sound at the level v1.2 specifies. The fragilities
live at the interfaces between v1.2 and the rest of the cascade — especially where v1.2
commits a contract whose enforcement depends on a layer (chat-Claude project instructions,
Stop-hook task-invoke semantics, multi-MCP-call atomicity) that v1.2 cannot fully control.

- **F-Eng-1: Cross-doc path mismatch — `cascade:run-state.json` location is inconsistent
  with D2.1 v2.**
  **Evidence:** D2.1 v2 §The `cascade:run-state` schema states: *"A single JSON document
  per consumer at `docs/.solo-run-state.json` (filesystem-canonical)"*. D2.3 v1.2's Project
  Instructions block (line 487) and §Cross-references both reference
  `docs/.cascade/run-state.json`. D4.6 §CLI surface (line 29) states:
  *"Reads `cascade:run-state.json` from `docs/.cascade/run-state.json` (canonical path per
  D2.1 v2)"* — but the cited canonical path in D2.1 v2 is `docs/.solo-run-state.json`,
  not `docs/.cascade/run-state.json`. Separately, D2.2 uses `.cascade/session/`,
  `.cascade/manifests/`, `.cascade/halt/` at repo root (not under `docs/`).
  **Target:** both. v1.2's Project Instructions block + D4.6's CLI-surface section both
  miscite D2.1 v2.
  **Severity:** Urgent.
  **Suggested resolution:** decide the canonical path and amend the misciting doc. Three
  options: (a) keep D2.1 v2's `docs/.solo-run-state.json` and search-replace v1.2 + D4.6;
  (b) change D2.1 v2 to `docs/.cascade/run-state.json` for consistency with v1.2's
  `.cascade/`-namespaced state; (c) use `.cascade/run-state.json` at repo root for
  consistency with D2.2's `.cascade/session/` and `.cascade/manifests/`. Option (c) is
  closest to D2.2's existing pattern; option (b) is what D4.6 already documents. Either
  way, the implementation pass cannot proceed until one path is canonical across D2.1 v2,
  D2.2, D2.3 v1.2, and D4.6. Amendment lands in v1.3 if (c); in D2.1 v2 if (b); in v1.2 +
  D4.6 if (a).

- **F-Eng-2: D4.6 reads a `cascade:run-state.last_group_artifacts[]` field that v1.2's
  schema additions do not declare.**
  **Evidence:** D4.6 §CLI surface (line 42): *"'What was produced' lists the last group's
  artifacts from `cascade:run-state.last_group_artifacts[]` (a field populated at group
  seal)"*. v1.2 §Handoff verification predicate's schema additions enumerate
  `queue_version`, `last_completed_group`, `last_group_exit_at`, `active_milestone`,
  `parent_feature_name`, `next_chain_step` — six new fields — but not
  `last_group_artifacts[]`. The mechanism *"populated at group seal"* is not specified
  anywhere: which stage's seal populates it, in which group-exit step, what schema each
  artifact entry uses, whether it is bounded in size.
  **Target:** both. v1.2's schema must declare the field; D4.6 must specify the population
  contract (likely as a step in v1.2 §Group-exit mechanics).
  **Severity:** High.
  **Suggested resolution:** either (a) add `last_group_artifacts[]` to v1.2's schema
  additions and add a population step to §Group-exit mechanics (between current step 2
  flush and step 5 card-render), specifying that the field is the union of artifacts
  named in the just-sealed group's manifest's `outputs` plus any per-stage artifacts named
  in earlier stages of the group, OR (b) drop the field from D4.6's re-derivation and have
  D4.6 read the last sealed manifest's `outputs` directly. Option (b) is cleaner — keeps
  v1.2's schema minimal and removes a coordination step. Amendment lands in v1.2 (drop
  the field reference if (b); add the field if (a)) and D4.6.

- **F-Eng-3: Manual halt protocol is silent on Group D's four-hat fan-out mid-flight.**
  **Evidence:** v1.2 §Manual halt protocol specifies the protocol for *"Inside Group E
  (auto-fire chain in chat-Claude)"* and *"Inside Group F (auto-fire chain in Claude Code)"*.
  Group D's four-hat fan-out is neither — it is a parallel-subagent dispatch (Pattern F per
  §`/Chains` contract). If the founder invokes `/cascade-halt` while hats 1 and 2 have
  completed but hats 3 and 4 are still running as subagents, v1.2 does not specify whether
  hats 3 and 4 are killed, allowed to complete, or have their transcripts written but their
  manifests withheld. The per-subagent safe-boundary granularity from §Within-group safe
  boundaries (Group D row) implies a halt-fires-at-next-SubagentStop semantics, but that
  is not commited explicitly.
  **Target:** D2.3 v1.2.
  **Severity:** Medium-High.
  **Suggested resolution:** add a Group D subsection to §Manual halt protocol. The
  defensible default for v0.2: outstanding subagents complete (each is a single Task-invoke
  that is naturally bounded in turn-budget); their manifests are written by the parent per
  D2.1 v2; the chat-end card renders the manual-halt variant once all four hat manifests
  exist (or once the founder's `/cascade-halt` is registered if fewer than four hats had
  even started). Records that Group D ran with a manual halt mid-fan-out, so that
  downstream `/review` can see four-hat objection coverage was harvested but no spec-seal
  occurred. Amendment lands in v1.2 (one paragraph in §Manual halt protocol).

- **F-Eng-4: `next_chain_step` Task-invoke mechanism is underspecified at the Stop hook
  contract level, and risks D2.2's prompt-injection-defense caveat.**
  **Evidence:** v1.2 §Auto-fire compact behaviour step 6: *"The Stop hook's first execution
  after the compact reads `cascade:run-state.next_chain_step` and, if non-null, Task-invokes
  the named stage rather than running its normal 'is this within-group or group-exit'
  decision logic."* The Stop hook does not directly invoke Task — it can only return
  `{"decision": "block", "reason": "..."}` to force Claude to continue; the continuation
  surface is the `reason` string injected into Claude's context. D2.2 §Research-step
  resolutions item 3 + the hooks-reference guidance cited in D2.2 *"imperative system
  instructions in stdout can trigger Claude's prompt-injection defenses"* suggests an
  imperative reason string ("Task-invoke /wrap SOL-N") may not behave reliably as a
  next-step trigger. The "factual phrasing" pattern D2.2 uses elsewhere
  (*"The next stage is `/wrap`"*) is the safer surface, but then the model has to choose
  to Task-invoke — the auto-fire's mechanical claim weakens to a strong nudge.
  **Target:** D2.3 v1.2 (with cross-reference into D2.2).
  **Severity:** Medium.
  **Suggested resolution:** specify the exact Stop-hook return shape (the JSON object the
  hook emits) and the exact `reason` string template, and confirm it is factual phrasing
  per D2.2 §Research-step resolutions item 3. If factual phrasing is used, demote
  "Task-invoke" language to "the next stage is X; continue per the `/Chains` contract" —
  which makes the chain-pointer a hint not a forcing function, and the chain resumes
  reliably for compliant models but degrades to a halt for the model that fails to
  recognise the hint. v0.2 ships the hint form; v0.2.x measures the chain-resumption
  reliability rate.

- **F-Eng-5: Group-exit mechanics atomicity in chat-Claude has weaker atomicity guarantees
  than the written write protocol implies.**
  **Evidence:** v1.2 §Group-exit mechanics atomicity step 5: *"`rename`
  `.cascade/handoff/last.md.tmp` → `.cascade/handoff/last.md` (POSIX atomic rename on the
  same filesystem)"*. In Claude Code (Group F) the rename runs inside the Stop hook
  orchestrator (shell or Python). In chat-Claude, *"steps 1–5 are done via the filesystem
  MCP. The model computes the sha (via a bash MCP call or by emitting the content and
  asking for a sha back from a tool), then writes the tmp file, then renames. This is a
  multi-MCP-call sequence; the model is instructed via the §`/Chains` contract to perform
  it in the specified order."* Multi-MCP-call sequences in chat-Claude are not atomic —
  a chat that is closed (by the founder or by Claude.ai's own context-management) between
  steps 3 and 5 leaves `.cascade/handoff/last.md.tmp` orphaned and `.cascade/handoff/last.md`
  unmodified. The §handoff-card-corrupted halt's predicate (paste-sha vs file-sha) would
  flag this on the next chat — but the cause would surface as corruption rather than as
  "previous chat was killed mid-write."
  **Target:** D2.3 v1.2.
  **Severity:** Medium.
  **Suggested resolution:** add to §Group-exit mechanics atomicity a chat-Claude-specific
  guarantee: the model is instructed (in the §`/Chains` contract) to perform the write
  sequence as a single message turn (no intermediate user interactions), and to surface
  the card render only after the rename completes (so a closed chat after step 3 will not
  have shown the card to the founder either). A leftover `last.md.tmp` is detected by D4.6
  at next read (a new halt §cascade-resume-stale-tmp or by extending
  §cascade-state-unparseable's recovery to clean up `.tmp` files). Amendment lands in v1.2
  (one paragraph) and D4.6 (one halt code or extended recovery).

- **F-Eng-6: The 9-check verification predicate's compatibility with chat-Claude's
  weak enforcement is asserted but the actual failure mode catalog is empty.**
  **Evidence:** v1.2 §Execution surface per group: *"Chat-Claude verification is best-effort,
  not enforced. In chat-Claude, 'halt with §handoff-state-mismatch' is a model-behaviour
  halt — the model is instructed to refuse to advance — not a hook-level halt."* The
  §Handoff verification predicate then specifies nine sequential checks each producing a
  named halt. v1.2 acknowledges the weakness in §Execution surface per group but does not
  enumerate the failure modes of best-effort verification: a model that incorrectly
  evaluates check 5 (group entry computation against `last_completed_group + 1`); a model
  that skips check 8 (timestamp comparison); a model that conflates check 6 and check 7
  (ticket vs milestone). For Group F these are hook-enforced; for chat-Claude they are
  model-cognition-enforced. The acknowledgment-naming-five-fields step (step 5 of the
  Project Instructions block) is the only founder-facing failsafe.
  **Target:** D2.3 v1.2.
  **Severity:** Medium (acknowledged structurally, but the diagnostic-when-it-fails
  pathway is absent).
  **Suggested resolution:** add a §Chat-Claude verification failure modes subsection
  enumerating: silent skip (model didn't run the predicate), partial run (model ran some
  checks but not others), wrong-halt-code (model surfaced a different code than the failure
  warranted), false-positive halt (model halted on a valid card). For each mode, name the
  founder-facing signal (the acknowledgment line names the 5 fields; if the acknowledgment
  is missing or wrong, the founder catches it). Measurement M-5 is added: count of
  founder-corrected resumption attempts per milestone (the founder noticed a mismatch
  between the acknowledgment and what they pasted). v0.2.x uses this to validate that
  best-effort enforcement is good enough. Amendment lands in v1.2 (one new subsection)
  and a new measurement row in §Deferred measurement.

## User hat — what's friction-prone or surprising for the solo founder

The amendments lean toward correctness over UX-friendliness in several places, and the
9-check predicate is the most visible cost. None of these block v0.2; several are
candidates for v0.2.x once dogfood data exists.

- **F-Usr-1: Nine schema checks surface as nine distinct halt codes; one consolidated
  "card-vs-state mismatch" message would be friendlier for the common case.**
  **Evidence:** v1.2 §Handoff verification predicate enumerates checks 1–9 each with a
  named halt code (§handoff-card-corrupted, §handoff-state-mismatch (marker / group /
  ticket / milestone / stale-group), §handoff-stale-queue). The founder seeing a halt for
  "ticket mismatch" vs "milestone mismatch" vs "stale-group" is being asked to distinguish
  failure modes whose recovery is identical (paste a fresh card or run `solo-cascade resume`).
  D4.6's `--explain` flag suggests the design recognises this distinction is for tooling.
  **Target:** D2.3 v1.2.
  **Severity:** Low-Medium.
  **Suggested resolution:** keep the 9-code internal distinction (D4.6's `--explain` and
  the halt diagnostic context both benefit from the granularity), but render a single
  founder-facing message that lists every failing check in a compact form: *"This handoff
  card doesn't match your cascade state. The cascade is at group E (queue version 8);
  your card was for group D (queue version 7). Recovery: `solo-cascade resume E`."* The
  founder doesn't need to learn nine halt codes; the recovery is the same in 8 of the 9.
  Amendment lands in `docs/templates/halt-messages.md` (the consolidated render) — which
  is outside v1.2's authored scope but reachable from v1.2 with one paragraph naming the
  consolidation contract.

- **F-Usr-2: `/cascade-halt` + `/build-kill` two-step in Group F is friction at exactly
  the moment the founder needs to act fast.**
  **Evidence:** v1.2 §Manual halt protocol Group F: *"If `/cascade-halt` is invoked without
  a prior `/build-kill` and Ralph is live, `/cascade-halt` errors out and instructs the
  founder to `/build-kill` first. (A future v0.2.x could chain these; v0.2 keeps them
  separate to surface the kill explicitly.)"* The cited rationale ("surface the kill
  explicitly") has merit, but the timing — the founder is invoking `/cascade-halt` because
  something is wrong, often urgently — argues for the convenience path. Two-step is also
  harder to remember (which one first?).
  **Target:** D2.3 v1.2 (with potential cross-reference into D4.2).
  **Severity:** Low.
  **Suggested resolution:** keep v0.2's two-step for the explicit-kill-surfacing rationale
  but commit the v0.2.x amendment shape: `/cascade-halt` in Group F detects live Ralph,
  emits a confirmation prompt (*"Ralph is live on SOL-N. Kill Ralph and halt cascade? [y/n]"*)
  and on confirmation chains `/build-kill` then sets the manual-halt flag. v0.2 ships
  two-step; v0.2.x ships confirm-and-chain. Amendment lands in v1.2 (one sentence noting
  the v0.2.x path) and in §Deferred measurement / open items.

- **F-Usr-3: Project-Instructions 5-step chat-start protocol is heavy for the
  project-instruction layer to follow reliably.**
  **Evidence:** v1.2 Project Instructions block: at chat start, *"before producing any
  output"*, the model performs: (1) read run-state, (2) read handoff/last.md if present,
  (3) verify 9-check predicate, (4) on failure halt with one of four named codes,
  (5) on success emit acknowledgment naming 5 specific fields. Per chat boundary, that
  is a 5-step protocol with 9-internal-check substep, performed across 7 boundaries per
  feature (eight groups minus one terminal). The model has natural compulsion to respond
  to the user's pasted message before running this protocol — and project-instruction
  compliance is observed to degrade in long-context Claude.ai sessions.
  **Target:** D2.3 v1.2.
  **Severity:** Medium.
  **Suggested resolution:** the step 5 acknowledgment is the founder-facing safety net
  (per F-Eng-6's note); strengthen it to be the load-bearing observable: rename the
  acknowledgment step to "verification surface" and instruct the model to emit it even if
  some checks were skipped, naming which checks ran and which did not. This makes the
  acknowledgment the founder's read-out of whether the predicate fired — a missing or
  partial acknowledgment is itself a signal. Amendment lands in v1.2 Project Instructions
  block, one revised step.

- **F-Usr-4: D4.6 `--rewrite-file` should be the default in the recovery context.**
  **Evidence:** D4.6 §CLI surface: *"Without `--rewrite-file`, the primitive is purely
  read-only. The flag exists for the case where `.cascade/handoff/last.md` is missing or
  corrupted and the founder wants both the stdout output (to paste) and a restored file
  (for path b to work again next time)."* The named-use-case is precisely the case where
  D4.6 is invoked — D2.3 v1.2 §Lost-card recovery names D4.6 as path (c), invoked when
  (a) sidebar and (b) `.cascade/handoff/last.md` have failed. If both have failed, the
  founder almost always wants the file rewritten so path (b) works next time.
  **Target:** D4.6.
  **Severity:** Low.
  **Suggested resolution:** flip the default — `--rewrite-file` becomes the default
  behavior; a new flag `--no-rewrite` is the read-only escape hatch for inspection-only
  use (the D4.6 §Composition with chat-Claude vs Claude Code "I forgot what state I'm
  in" case). The §Composition with D2.3 v1.2 §Handoff verification predicate section
  becomes simpler: checks 2 and 3 trivially pass for the common case. Amendment lands in
  D4.6 §CLI surface (one flag flip; the rest of the doc holds).

- **F-Usr-5: Eight-group cascade with seven `/Chains` patterns asks the founder to learn
  a vocabulary that has no plain-language anchor.**
  **Evidence:** v1.2 §`/Chains` contract names seven patterns by single-letter codes
  (T / P / M / F / C / G / N). Five of the seven appear only once across the eleven skills
  (T → /onboard; P → /discovery; M → /constitution; F → /specify; G → /verify; N → /retro).
  Only C is shared across stages (E-chain and F-chain). The pattern names neither describe
  the pattern nor map mnemonically — "T-pattern terminal-render" and "N-pattern
  terminal-no-handoff" both contain "terminal" but use different letters.
  **Target:** D2.3 v1.2.
  **Severity:** Low.
  **Suggested resolution:** rename the patterns to descriptive identifiers in the SKILL.md
  `/Chains` section: `single-stage-render` (T), `phase-chain` (P), `amendment-loop` (M),
  `fan-out-then-seal` (F), `auto-chain` (C), `fan-out-aggregate` (G), `terminal-no-card` (N).
  Slightly longer but self-documenting; the SKILL.md author and the founder both benefit
  from descriptive names. Amendment lands in v1.2 §`/Chains` contract (the pattern-name
  table) — small wording change, no semantics shift.

## Reviewer hat — what does v1.2 + D4.6 assert without evidence

Three of v1.2's framing claims and one of D4.6's seam claims need either evidence-citation
or wording softening. Two more are minor language tightenings.

- **F-Rev-1: Chat-Claude project-instruction layer is sufficient for the verification
  predicate — claim is honest but lands without a baseline for what "sufficient" means.**
  **Evidence:** v1.2 §Execution surface per group: *"Chat-Claude verification is best-effort,
  not enforced [...] This is a weaker enforcement than Claude Code's hook surface but it
  is the enforcement actually available in chat-Claude as of May 2026."* No empirical
  evidence for the failure rate is provided. v1.2 §Deferred measurement adds M-1 (paste
  time), M-2 (reset card count), M-3 (per-group time/token), M-4 (B+C unified vs split) —
  but no measurement for the project-instruction compliance rate that the entire chat-
  Claude enforcement strategy depends on.
  **Target:** D2.3 v1.2.
  **Severity:** Medium.
  **Suggested resolution:** add measurement M-5 to §Deferred measurement: count of
  acknowledgment-line presence vs absence at chat-start across all chat-Claude groups in
  v0.2.x dogfood. If the acknowledgment is missing or wrong on more than ~5% of group
  entries, the project-instruction layer is failing too often and the chat-Claude
  enforcement strategy needs to be revisited (probably by moving more groups to Claude
  Code, or by adding a manual "verify" command the founder runs before pasting). M-5
  composes with the F-Eng-6 strengthening of step 5 of the Project Instructions block.

- **F-Rev-2: D4.6's seam to D4.5 (the §cascade-resume-manifest-chain-broken halt) names
  "D4.5's `--reconcile` against the named stage" — but D4.5 does not cover four of the
  eleven stages.**
  **Evidence:** D4.5 §Decision: *"`--reconcile` — across `/build`, `/wrap`, `/specify`,
  `/plan`"*. The stages `/onboard`, `/update-linear`, `/review`, `/verify`, `/retro` have
  no `--reconcile` primitive in D4.5; `--rerun` covers `/specify`, `/review`, `/plan`.
  D4.6 §Halt conditions row for §cascade-resume-manifest-chain-broken: *"Recovery: D4.5's
  `--reconcile` against the named stage."* If the manifest chain breaks at `/onboard`'s
  manifest, `/update-linear`'s manifest, `/verify`'s manifest, or `/retro`'s manifest,
  D4.5 has no primitive to invoke. The recovery pointer is dangling for four of the
  eleven stages.
  **Target:** D4.6 (with cross-reference into D4.5).
  **Severity:** Medium-High.
  **Suggested resolution:** two options. (a) Extend D4.5 to add `--reconcile` for the
  four uncovered stages; modest design work because each stage's manifest content is
  already specified. (b) Acknowledge the gap explicitly in D4.6's halt-condition row:
  *"For stages without `--reconcile`, the recovery is `--unseal` plus re-run of the
  affected stage."* — and add a §cascade-resume-manifest-chain-broken halt-card variant
  for the no-reconcile case. Option (b) is the v0.2 ship; option (a) is the v0.2.x
  expansion when measurement shows the gap actually bites. v1.2 lands in D4.6 §Halt
  conditions (one row revision) plus a one-line D4.5 cross-reference note.

- **F-Rev-3: Per-tool-call sub-millisecond hook overhead is asserted but not cited.**
  **Evidence:** v1.2 §Within-group safe boundaries Group F row revision: *"Per-tool-call
  grain costs sub-millisecond hook overhead per tool call (per Claude Code's hooks
  reference)"*. D2.2's hook-surface research (`D2_2_hook_surface_research.md`) catalogs
  the hook surface but does not benchmark per-hook latency. Sub-millisecond is a specific
  claim; the actual cost is likely 5–50 ms for a `command`-type hook (subprocess fork +
  script startup + I/O). A 100-tool-call Ralph iteration with a 20 ms per-hook overhead
  adds 2 seconds of latency, which is acceptable; with a 100 ms overhead, 10 seconds,
  which is visible but not breaking.
  **Target:** D2.3 v1.2.
  **Severity:** Low.
  **Suggested resolution:** soften the claim to "low single-digit ms" or "imperceptible
  in practice on a fast filesystem"; add measurement M-6 to §Deferred measurement: median
  per-hook latency for the per-tool-call safe-boundary check, measured across one Ralph
  iteration in v0.2.x dogfood. The deferral validates the claim post-ship rather than
  pre-committing without evidence.

- **F-Rev-4: The seven-pattern `/Chains` partition oversells the abstraction.**
  **Evidence:** v1.2 §`/Chains` contract introduces seven named patterns; six are used
  exactly once across the eleven skills (each pattern is essentially a per-group definition).
  Only Pattern C — auto-fire-chain — is reused, across Group E (chat-Claude) and Group F
  (Claude Code), and its mechanics are different in each (project-instruction continuation
  vs Stop-hook Task-invoke). The named patterns are pedagogically useful per-skill but the
  framing as "patterns" suggests reusability that is not present.
  **Target:** D2.3 v1.2.
  **Severity:** Low.
  **Suggested resolution:** keep the per-skill SKILL.md `/Chains` section template — that
  is what Child B implements — but reframe the introductory prose: *"The eleven SKILL.md
  files have seven distinct `/Chains` shapes; we name them so Child B can implement them
  consistently."* The naming becomes a vocabulary aid for the implementation pass, not a
  load-bearing abstraction. Alternative: collapse to five shapes by merging T+N (both
  single-card-emit terminal variants) and merging P+F+G (all multi-step internal with
  card at end), keeping M, C, and the merged-T+N as distinct. Either form lands in v1.2
  §`/Chains` contract (one-paragraph framing change).

- **F-Rev-5: Halt set has one tiling gap — cross-product replay with same marker.**
  **Evidence:** v1.2 §Handoff verification predicate check 4: *"Pasted `Marker` equals
  `cascade:run-state.marker`"*. This catches the case where the founder pastes a card from
  a different product (different marker). It does not catch the case where two products
  share a marker (unlikely but possible per D0.1's multi-product Linear teams — the marker
  is a project-name prefix, not a globally-unique identifier; two consumers in different
  projects could choose the same three-letter marker). The product field is in the card
  body but not in the check list.
  **Target:** D2.3 v1.2.
  **Severity:** Low.
  **Suggested resolution:** add a check 4a: *"Pasted `Product` equals
  `cascade:run-state.product`"*. Marker is the namespace prefix; product is the canonical
  consumer identity. Both should match. Amendment lands in v1.2 §Handoff verification
  predicate (one new check row and one updated halt-code row).

## Integrator hat — cross-doc seams

The integrator-hat findings are the most consequential — they're where v1.2's neat
contracts hit the rest of the cascade's existing surface. Two of these (F-Int-1, F-Int-2)
are blockers; the rest are amendments-needed.

- **F-Int-1: D4.6's read of `cascade:run-state.last_group_artifacts[]` violates
  v1.2's schema additions (the field is not declared).**
  **Evidence:** See F-Eng-2 above; reproduced here under Integrator-hat lens because the
  failure is at the schema seam between v1.2 and D4.6 — v1.2 owns the schema, D4.6 reads
  from it. v1.2 §Handoff verification predicate's schema block declares six new fields;
  `last_group_artifacts[]` is not one of them. D4.6's re-derivation reads from a field
  v1.2 has not promised to populate.
  **Target:** both.
  **Severity:** High.
  **Suggested resolution:** see F-Eng-2 — drop the field reference in D4.6 (re-derive
  "What was produced" from the last sealed manifest's `outputs` directly), or add the
  field to v1.2's schema additions with a clear population mechanic in §Group-exit
  mechanics. The drop option is structurally cleaner.

- **F-Int-2: D2.2's "factual phrasing, not imperative" pattern composes awkwardly with
  v1.2's auto-fire compact recovery — and the integration is implicit.**
  **Evidence:** D2.2 §SessionStart source=compact: *"Emit a concise additionalContext
  block via `hookSpecificOutput.additionalContext` — the cascade:run-state pointer, last
  completed stage, last sealed manifest, active stages (if any persisted). This is factual
  phrasing per the hooks-reference guidance ('The deployment target is production'), not
  imperative instructions."* v1.2 §Auto-fire compact behaviour step 6: *"The Stop hook's
  first execution after the compact reads `cascade:run-state.next_chain_step` and, if
  non-null, Task-invokes the named stage rather than running its normal 'is this within-
  group or group-exit' decision logic."* The Stop hook's mechanism for "Task-invoke the
  named stage" is implicit — likely via `{"decision": "block", "reason": "..."}` — and the
  `reason` string risks the very imperative-instruction-in-stdout pattern D2.2 warns
  against. F-Eng-4 above flags this from the Engineer hat; here it is the seam to D2.2.
  **Target:** both D2.3 v1.2 and (lighter-touch) D2.2.
  **Severity:** Medium.
  **Suggested resolution:** v1.2 commits the exact Stop-hook output shape (the JSON the
  hook emits), names whether `reason` is factual or imperative, and cites D2.2's
  factual-phrasing pattern explicitly. If imperative phrasing is unavoidable, the hook
  uses a different output mechanism (SessionStart's `additionalContext` post-compact is
  factual; the Stop hook's actual force is the model's compliance with the post-compact
  context, not the Stop hook's `reason` itself). v0.2 ships factual-phrasing + model-
  compliant continuation; the chain becomes a hint not a forcing function. Amendment
  lands in v1.2 §Auto-fire compact behaviour (one paragraph) and a one-line D2.2
  cross-reference.

- **F-Int-3: `/build-kill` from sidecar chat mutates `cascade:run-state.queue_version`
  while the Group F chat is potentially live — interaction is unspecified.**
  **Evidence:** v1.2 §Group F per-skill semantics for `/build-kill`: *"Writes to manifests
  and Linear per D4.2's spec; sets `cascade:run-state.queue_version++` (drops the ticket
  from the queue if `/wrap` is not pending)."* If the founder runs `/build-kill SOL-N`
  from a sidecar chat while the Group F chat for SOL-N is mid-Ralph (not yet at `/wrap`),
  the run-state's queue_version increments while the Group F chat continues to operate
  against the old queue_version. v1.2 §Manual halt protocol's note *"If the founder does
  not return to the Group F chat at all, the next chat opened detects the flag during
  paste-verification and surfaces §manual-halt-pending"* covers the founder-doesn't-return
  case but not the founder-returns-mid-Ralph case.
  **Target:** D2.3 v1.2 (with D4.2 cross-reference).
  **Severity:** Medium.
  **Suggested resolution:** specify that `/build-kill` writes a `kill_in_progress: <ticket>`
  flag to `cascade:run-state` in addition to incrementing `queue_version`. The Group F
  chat's Stop hook (per the PreCompact/Stop orchestrator pattern) reads the flag at every
  Ralph-iteration safe boundary; if set for the active ticket, halts the chat with a
  chat-end card framed as "remote kill received." Amendment lands in v1.2 §Group F
  per-skill semantics (one paragraph) and one new halt §kill-received-remote.

- **F-Int-4: D3.4's "all gates evaluate before halt card composed" rule and v1.2's
  "If any gate halts" wording compose ambiguously.**
  **Evidence:** D3.4 §`/specify`: *"All gates evaluate before the halt card is composed;
  a `spec.ac-coverage` failure does not short-circuit `spec.pyramid-shape` evaluation.
  Rationale: the founder benefits from seeing every issue in one pass."* v1.2 §Gate-then-
  safe-boundary ordering step 2: *"If any gate halts, the cascade halts and no compact
  runs. Halt card surfaces. No manifest is written."* The "any gate halts" wording can
  be read as either "if the gate set's evaluation produced any halts" (D3.4 semantics) or
  "as soon as a gate halts" (short-circuit semantics). v1.2 likely means the former (it
  cites no override of D3.4) but the wording is ambiguous.
  **Target:** D2.3 v1.2.
  **Severity:** Low.
  **Suggested resolution:** revise step 2 to: *"All gates evaluate per D3.4. If the gate
  set produces any failing predicates, the cascade halts and no compact runs. The halt
  card aggregates failures per D3.4's aggregation rules. No manifest is written."*
  Amendment lands in v1.2 §Gate-then-safe-boundary ordering (one sentence revision).

- **F-Int-5: D1's `/onboard` step 3 ("reuse existing /onboard step 7") references a step
  number that v1.2 now reuses for a different new step.**
  **Evidence:** D1 §`/onboard` changes step 3: *"Seed Product with founder's north-star
  (interactive flow; reuse existing /onboard step 7)."* The "existing /onboard step 7"
  refers to a step in the v0.1 `.claude/skills/onboard/SKILL.md` file. v1.2 §`/onboard`
  integration point introduces a new step 7 (Render Project Instructions paste-block).
  Anyone reading D1 + v1.2 together encounters two different things called "step 7": D1's
  reference to v0.1 SKILL.md step 7, v1.2's reference to the new D1-post + v1.2-amended
  sequence step 7. The implementation pass for Child B / SOL-58 has to disambiguate.
  **Target:** D1 (housekeeping) — not v1.2's core scope but flagged at this seam.
  **Severity:** Low.
  **Suggested resolution:** when Child B amends `.claude/skills/onboard/SKILL.md`, update
  D1's "reuse existing /onboard step 7" reference to "reuse existing v0.1 north-star
  seeding subroutine" (descriptive, not numeric). Amendment lands in D1 during the
  implementation pass, not in v1.2.

- **F-Int-6: D4.6 reads sealed manifests for the "Last sealed manifest" field but the
  selection mechanic ("which manifest is *the* last sealed manifest at group exit?") is
  unspecified for groups whose internal patterns produce multiple manifests.**
  **Evidence:** D4.6 §CLI surface: *"`Last sealed manifest` and its sha ← from the manifest
  chain in `.cascade/manifests/`"*. v1.2 §`/Chains` contract Pattern F (Group D /specify):
  Group D writes a manifest per subagent (four-hat-user, four-hat-engineer, four-hat-pm,
  four-hat-skeptic) plus a `/specify` parent manifest. Group E (Pattern C): writes `/plan`,
  `/review`, `/update-linear` manifests in sequence; the chain pointer presumably names
  `/update-linear`'s as the group-exit manifest. Group F (Pattern C): writes per-iteration
  Ralph manifests plus `/build`'s aggregate plus `/wrap`'s. Group G (Pattern G): writes per-
  child plus aggregate. The "last sealed manifest" is the manifest *most-recently* sealed
  before chat-end — but whether that's the parent's or the last subagent's varies by
  pattern. D4.6's re-derivation could surface the wrong one.
  **Target:** both. v1.2's §Group-exit mechanics needs a per-pattern "the group's exit
  manifest is..." statement; D4.6's §CLI surface needs to read from that statement.
  **Severity:** Medium.
  **Suggested resolution:** add to v1.2 §`/Chains` contract per-pattern: the group's exit
  manifest is the parent manifest (the `/specify`, `/update-linear`, `/wrap`, `/verify`,
  `/retro` manifest respectively) — never a subagent or per-iteration manifest. D4.6 reads
  `cascade:run-state.last_sealed_parent_manifest_path` (a new schema field — replaces or
  supplements the existing `last_sealed_manifest_sha256`). Amendment lands in v1.2
  §`/Chains` contract (per-pattern naming) and §Handoff verification predicate schema
  (one new field), plus D4.6 §CLI surface (read from the new field).

---

## Recommendation

**(b) v1.2 + D4.6 need amendments — name them.**

The eight-group decision, the §Handoff verification predicate's check set, the §`/Chains`
contract's pattern partition, D4.6's separation from D4.5, and the chat-Claude / Claude
Code execution surface split are all structurally sound and survive adversarial review.
v1.2 closes 18 of 24 v1.1 findings as advertised, and D4.6 closes the three v1.1 findings
it was authored to close. The recommendation is not (c) — neither doc needs a redraft.

What v1.2 + D4.6 need before the implementation pass can begin:

Critical amendments (block implementation):

1. **Resolve the `docs/.solo-run-state.json` vs `docs/.cascade/run-state.json` path
   mismatch** (F-Eng-1). Either amend D2.1 v2 to the v1.2 path, or amend v1.2 + D4.6 to
   D2.1 v2's path. The 0001 integration spec cannot proceed against a contradictory
   canonical-path declaration.
2. **Resolve the `last_group_artifacts[]` schema vs D4.6 read** (F-Eng-2 / F-Int-1).
   Drop the field reference in D4.6 (read from the last sealed manifest's `outputs`
   directly) or add the field to v1.2's schema with a population mechanic.
3. **Specify Group D's behavior under `/cascade-halt` mid-fan-out** (F-Eng-3). One
   paragraph addition to v1.2 §Manual halt protocol.

Important amendments (recommended before implementation; non-blocking):

4. **Specify the Stop-hook output shape for `next_chain_step` Task-invoke** (F-Eng-4 /
   F-Int-2). One paragraph in v1.2 §Auto-fire compact behaviour naming the JSON shape
   and the factual-phrasing pattern.
5. **Specify chat-Claude multi-MCP-call atomicity for `.cascade/handoff/last.md` write**
   (F-Eng-5). One paragraph addition to v1.2 §Group-exit mechanics atomicity plus a
   minor extension in D4.6 to clean up `.tmp` files.
6. **Specify the §cascade-resume-manifest-chain-broken handoff for stages without
   `--reconcile`** (F-Rev-2). One row revision in D4.6 §Halt conditions.
7. **Specify the group's exit manifest per pattern** (F-Int-6). One sentence per pattern
   in v1.2 §`/Chains` contract plus a schema field rename in v1.2 §Handoff verification
   predicate plus a D4.6 §CLI-surface read amendment.
8. **Specify `/build-kill`-from-sidecar interaction with live Group F chat** (F-Int-3).
   One paragraph in v1.2 §Group F per-skill semantics plus one new halt code.

Lower-priority amendments (defer to implementation pass or v0.2.x):

9. Add cross-product check 4a to §Handoff verification predicate (F-Rev-5).
10. Strengthen the Project Instructions step 5 acknowledgment to be the load-bearing
    observable (F-Usr-3 / F-Eng-6).
11. Soften per-tool-call sub-millisecond claim and add M-6 measurement (F-Rev-3).
12. Add M-5 measurement for chat-Claude predicate-compliance rate (F-Rev-1).
13. Add consolidated founder-facing halt message for handoff-mismatch cases (F-Usr-1).
14. Reframe §`/Chains` contract pattern naming as a vocabulary aid (F-Rev-4 / F-Usr-5).
15. Flip D4.6 `--rewrite-file` default (F-Usr-4).
16. v0.2.x note: `/cascade-halt` auto-detects Ralph (F-Usr-2).
17. Tighten v1.2 §Gate-then-safe-boundary ordering wording (F-Int-4).
18. Update D1's "reuse existing step 7" reference at implementation time (F-Int-5).

Amendments 1–3 are the only ones that block the implementation pass starting on the
eleven `/Chains` rewrites. Amendments 4–8 can be absorbed into the implementation pass
inline (the SKILL.md author surfaces the gaps and the design owner resolves in the same
session). Amendments 9–18 can be queued as v0.2.x amendments without blocking v0.2 ship.

---

## Disposition table

| # | Finding | Target | Severity | Proposed lands-in section |
|---|---|---|---|---|
| F-Eng-1 | Path mismatch — `docs/.solo-run-state.json` vs `docs/.cascade/run-state.json` | both (and D2.1 v2) | Urgent | v1.2 §Project Instructions block + §Cross-references; D4.6 §CLI surface; D2.1 v2 §The `cascade:run-state` schema |
| F-Eng-2 | D4.6 reads `last_group_artifacts[]` not in v1.2 schema | both | High | v1.2 §Handoff verification predicate schema OR D4.6 §CLI surface (drop the field) |
| F-Eng-3 | Manual halt silent on Group D fan-out mid-flight | D2.3 v1.2 | Medium-High | v1.2 §Manual halt protocol (new Group D subsection) |
| F-Eng-4 | `next_chain_step` Stop-hook Task-invoke mechanism underspecified | D2.3 v1.2 | Medium | v1.2 §Auto-fire compact behaviour (one paragraph) |
| F-Eng-5 | Chat-Claude multi-MCP-call atomicity gap | D2.3 v1.2 | Medium | v1.2 §Group-exit mechanics atomicity (one paragraph); D4.6 §Halt conditions (extend recovery) |
| F-Eng-6 | 9-check predicate's chat-Claude failure modes uncatalogued | D2.3 v1.2 | Medium | v1.2 §Execution surface per group (new subsection); §Deferred measurement (new row M-5) |
| F-Usr-1 | Nine halt codes → one consolidated founder message | D2.3 v1.2 | Low-Medium | v1.2 §Handoff verification predicate (one-paragraph render-contract note) |
| F-Usr-2 | `/cascade-halt` + `/build-kill` two-step friction | D2.3 v1.2 | Low | v1.2 §Manual halt protocol (v0.2.x note); §Deferred measurement (open item) |
| F-Usr-3 | 5-step chat-start protocol heavy for project-instruction layer | D2.3 v1.2 | Medium | v1.2 Project Instructions block (revised step 5) |
| F-Usr-4 | D4.6 `--rewrite-file` should be default | D4.6 | Low | D4.6 §CLI surface (flag default flip) |
| F-Usr-5 | Seven-pattern `/Chains` naming non-mnemonic | D2.3 v1.2 | Low | v1.2 §`/Chains` contract (rename patterns) |
| F-Rev-1 | Chat-Claude sufficiency claim — no measurement | D2.3 v1.2 | Medium | v1.2 §Deferred measurement (new row M-5; same as F-Eng-6's deferral) |
| F-Rev-2 | D4.6 → D4.5 seam dangles for 4 stages without `--reconcile` | D4.6 | Medium-High | D4.6 §Halt conditions (row revision); D4.5 (one-line cross-reference note) |
| F-Rev-3 | Sub-millisecond per-tool-call overhead claim uncited | D2.3 v1.2 | Low | v1.2 §Within-group safe boundaries (claim softening); §Deferred measurement (new row M-6) |
| F-Rev-4 | Seven-pattern partition oversells abstraction | D2.3 v1.2 | Low | v1.2 §`/Chains` contract (framing-paragraph revision); same surface as F-Usr-5 |
| F-Rev-5 | Cross-product replay tiling gap (same marker, different product) | D2.3 v1.2 | Low | v1.2 §Handoff verification predicate (new check 4a) |
| F-Int-1 | (= F-Eng-2) Schema/read seam | both | High | Same as F-Eng-2 |
| F-Int-2 | (= F-Eng-4 from D2.2 seam lens) Factual phrasing vs imperative | D2.3 v1.2 (D2.2 cross-ref) | Medium | Same as F-Eng-4; one-line D2.2 cross-reference |
| F-Int-3 | `/build-kill` from sidecar vs live Group F chat unspecified | D2.3 v1.2 | Medium | v1.2 §Group F per-skill semantics (one paragraph); new halt §kill-received-remote |
| F-Int-4 | D3.4 "all gates evaluate" vs v1.2 "If any gate halts" wording | D2.3 v1.2 | Low | v1.2 §Gate-then-safe-boundary ordering (step 2 wording revision) |
| F-Int-5 | D1's "reuse existing /onboard step 7" collides with v1.2's new step 7 | D1 (implementation-pass housekeeping) | Low | D1 §`/onboard` changes (at implementation time, not in v1.2) |
| F-Int-6 | Group's exit manifest selection unspecified per pattern | both | Medium | v1.2 §`/Chains` contract (per-pattern note); v1.2 §Handoff verification predicate (schema field rename); D4.6 §CLI surface (read amendment) |

Critical amendments (urgent + high severity): F-Eng-1, F-Eng-2/F-Int-1, F-Eng-3 — block
implementation.
Important amendments (medium-high + medium severity): F-Eng-4/F-Int-2, F-Eng-5, F-Eng-6,
F-Rev-2, F-Int-3, F-Int-6, F-Usr-3, F-Rev-1 — can be absorbed in the implementation pass.
Lower-priority amendments: the remainder — queue for v0.2.x.
