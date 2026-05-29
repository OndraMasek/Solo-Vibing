# 0002 — v0.2 release wrap-up

**Status:** Sealed (re-seal into repo; hand-authored bootstrap mirror of the 2026-05-20 chat-Claude /specify + /plan that did not commit to disk).
**Type:** Framework self-application — closes the v0.2 cascade integration epic (0001 / PR #5) by landing docs lockstep and seeding the v0.2.x backlog.
**Strategy:** `hybrid` — parent flag; per-child strategies declared in `decomposition.md`.
**Marker:** `SOL` (per the framework's own `docs/.solo-config.json`).
**Date authored:** 2026-05-20. **Re-sealed into repo:** 2026-05-20.

---

## Motivation

PR #5 (commit `93faf5d`, "land v0.2 cascade integration spec + Children A–D") landed the v0.2 cascade primitives into `OndraMasek/Solo-Vibing`: the gate composition layer, eight wired hook events, and the `solo-verify` CLI with its test suite green. Two follow-on threads from epic 0001 were deferred and re-homed under this epic (SOL-102):

- **Strand A — docs lockstep (Child 0002-A, SOL-103, `walking-skeleton`).** Child 0001-E's deferred work: amend `CLAUDE.md`, `README.md`, and `docs/templates/CLAUDE.md` in lockstep so the v0.2 §Cascade gates / §Strategy enum / §Hooks / §Tainted state / §Code markers / §CI sections ship with the framework. A fresh fork running `/onboard --dry-run` gets a v0.2-shaped scaffold and can teach itself v0.2 from the docs it carries.
- **Strand B — v0.2.x backlog (Child 0002-B, SOL-104, `capability-cluster`).** Four v0.2.x followup tickets for items surfaced during Child 0001-C / Child 0001-D apply-time queue processing: PreCompact output shape validation, PRIMING_MARKERS reconciliation, MultiEdit handling in `pyramid-tampering.sh`, and D2.1 v2 AC-hash regex permissiveness.

This spec is the bootstrap that lets a Code `/build` session execute those two strands without halting at `preflight-provenance.sh` for want of an on-disk sealed spec. The 2026-05-20 /specify + /plan ran in chat-Claude with hooks not firing (see §Dogfood execution caveat); the sealed spec was never committed. This document re-seals it from the authoritative Linear content (SOL-102 / SOL-103 / SOL-104).

Related research: `D3_1_decomposition_negotiation.md`, `D3_2_test_pyramid_declaration.md`, `D3_3_perceptual_and_invariance_predicates.md`, `D3_4_gate_definitions.md`, `D2_1_trust_model.md` (v2 / v2.1), `D2_2_hook_surface_research.md`, `D2_2_session_auto_management.md`, `D1_linear_product_layer.md`.

---

## Acceptance criteria

Every AC below is covered by at least one child in `decomposition.md`. The parent has no failing-test seed at this grain (hybrid). AC-1 through AC-4 are Child 0002-A (SOL-103, docs lockstep); AC-5 through AC-8 are Child 0002-B (SOL-104, four v0.2.x followup tickets).

- **AC-1.** `CLAUDE.md` (repo root) is amended in lockstep: the v0.1 "no hooks in v0.1" sentence is dropped (false post-PR-5), and six subsections are added — §Cascade gates (→ `docs/templates/halt-messages.md` + `python3 tools/solo-verify --list-gates`), §Strategy enum (→ `/specify` step 1 + the five D3.1 strategies), §Hooks (→ `.claude/settings.json` + the eight hook scripts: `preflight-provenance.sh`, `pyramid-tampering.sh`, `four-hat-objection-coverage.py`, `stop-orchestrator.sh`, `session-start-state-restore.sh`, `session-end-telemetry.sh`, `precompact-safe-boundary.sh`, `pretool-write-denylist.sh`), §Tainted state (→ 0001 AC-18 `is_tainted` / `taint_reason` + `--reconcile-only` clearing), §Code markers (→ `.claude/rules/code-markers.md` for 🤔/📝/☣️), and §CI (→ `.github/workflows/ci.yml`). Purely structural: no timestamps, no version strings, no environment-dependent content. Per SOL-103.
- **AC-2.** `README.md` (repo root) is amended: the Status block carries the verbatim line "v0.2 cascade primitives integrated and self-applied; v0.2.x cycle open", and a §"What's new in v0.2" section lists the cascade primitives now in scope. Purely structural. Per SOL-103.
- **AC-3.** `docs/templates/CLAUDE.md` is amended in lockstep with AC-1: the same six §sections (Cascade gates, Strategy enum, Hooks, Tainted state, Code markers, CI), parameterized for fresh forks, cross-referencing D2.1 v2.1's `.cascade/run-state.json` canonical path at repo root. The shared sections are textually equivalent to the root `CLAUDE.md` modulo template-specific variant blocks. Per SOL-103.
- **AC-4.** A round-trip perceptual predicate holds: two consecutive `/onboard --dry-run` invocations against the D0.1 CI fixture tmpdir produce byte-identical rendered output after stripping lines matching `^.*Last updated.*\d{4}-\d{2}-\d{2}` and `^[A-Z_]+_RUN_ID=`; sha256 compare; equality required. The evidence artifact is sealed by Code at /build's at-write trigger to `docs/specs/0002-v0.2-release-wrap-up/perceptual/onboard-dry-run.txt`. Per SOL-103, D3.3 §Walking-skeleton perceptual predicate.
- **AC-5.** A Linear issue is created in `[SOL] Backlog` with the `v0.2.x` label for "PreCompact output shape validation against Claude Code v2.0.76+": validate whether `precompact-safe-boundary.sh` requires the `hookSpecificOutput` wrapper rather than Stop-shape top-level fields, and switch the `lib/common.sh` emitter call accordingly. Citation: Child 0001-C §Surfaced items #5. Per SOL-104.
- **AC-6.** A Linear issue is created in `[SOL] Backlog` with the `v0.2.x` label for "PRIMING_MARKERS validation against /review priming text": reconcile the substrings in `four-hat-objection-coverage.py`'s `PRIMING_MARKERS` dict against the v0.1 `.claude/agents/four-hat-{user,engineer,pm,skeptic}.md` priming text, by updating either the agent files or the hook dict. Citation: Child 0001-C §Surfaced items #6. Per SOL-104.
- **AC-7.** A Linear issue is created in `[SOL] Backlog` with the `v0.2.x` label for "MultiEdit handling in pyramid-tampering.sh": resolve the conservative-allow of `MultiEdit` PreToolUse calls, either by replaying the edit sequence via a Python helper that re-emits a Write-equivalent for inspection, or by blocking all MultiEdit writes to spec files. Citation: Child 0001-C §Surfaced items #7. Per SOL-104.
- **AC-8.** A Linear issue is created in `[SOL] Backlog` with the `v0.2.x` label for "D2.1 v2 AC-hash regex permissiveness confirmation": decide whether `solo-verify`'s `_ac_list_sha256_from_spec` regex `^#{1,3}\s+acceptance\s+criteria\s*$` (case-insensitive, H1/H2/H3) is intentional — and if so document the permissiveness in D2.1 v2 — or tighten it to the documented H2-only form. Citation: Child 0001-D §4 reconciliation queue item #5. Per SOL-104.

---

## Decomposition strategy

**Declared strategy:** `hybrid`. Per D3.1 §hybrid, this parent strategy is a flag, not a guide — every child carries an explicit non-inherited strategy in `decomposition.md`. Per D3.2, the parent's `pyramid_shape` is `null` and the parent's `failing_test_seed[]` is empty; per-child shapes and seeds live in each child's block.

- **Step 1 — proposal.** `hybrid`, because the two strands are qualitatively different: Strand A is a docs-lockstep vertical slice whose end-to-end signal is "a fresh fork renders a v0.2 scaffold" (walking-skeleton), while Strand B is four independent Linear-ticket capabilities with no shared vertical slice (capability-cluster). Forcing one strategy on both would lose one of the two signals. The two-strategies-or-more test from D3.1 is met.
- **Step 5 — founder-confirm.** Confirmed 2026-05-20 at the chat-Claude /specify step-5 (recorded in SOL-102). This re-seal carries that confirmation forward unchanged.

_The strategy annotation required by D3.4 §spec.strategy-annotation is cleared by the affirmative step-5 confirm above._

---

## Failing-test seed

**Pyramid shape:** `null` (hybrid).

_Per D3.2 §hybrid, hybrid parents carry no parent-level pyramid shape and no parent-level failing-test seed. Per-child pyramid shapes and seeds are declared in `decomposition.md`. `/plan`'s decomposer halts `§hybrid-without-child-overrides` if any child lands without an explicit strategy._

**Tests at parent grain.** None.

---

## Out of scope

Carried verbatim-in-substance from SOL-102:

- **Implementation of the four v0.2.x followups.** AC-5 through AC-8 deliver the *tickets*; the implementation of each lands in a separate v0.2.x spec.
- **Gate-naming divergence** (D3.4 gate names vs the AC-6 / AC-7 references inside the `/specify` and `/plan` SKILLs). Flagged in PR #5 as v0.2.x reconciliation; the v0.2.x cycle planner picks it up from PR #5 authoring-notes. Accepted in limbo per four-hat objection #12 resolution (path b).
- **v0.3 design surface.**
- **`0001-wrap-build-log` retirement decision.** Independent of this epic.

---

## .cascade manifest expectation

The 0002 child-chain manifests are generated by **Code at /build** (the `/specify` and `/plan` manifests for 0002 were never written to disk because the 2026-05-20 chat run did not fire hooks). This re-seal commits the spec artifacts only; it does **not** seed `.cascade/manifests/` entries.

`preflight-provenance.sh` requires a parent manifest to verify the input-provenance chain. The parent manifest reference is `.cascade/manifests/SOL-1-update-linear.json` — **or the most recent sealed manifest of 0001's child chain; the executing Code session verifies the exact path at apply time** (SOL-102 §Provenance carries this as a verify-at-apply item). If no on-disk 0001 manifest exists post-PR-5 (the same chat-not-firing-hooks gap may have left 0001's manifests uncommitted), the Code session's first `/build` step is to reconstruct or seed the parent manifest before the provenance gate can pass — flag to the founder if so.

The `ac_list_sha256` recorded in §Provenance is what `/build` verifies against. It is computed over the §Acceptance criteria bulleted entries per D2.1 v2 §`input_provenance.ac_list_sha256` (parse the `## Acceptance Criteria` section, take top-level bulleted lines, strip the leading bullet marker and surrounding whitespace per line, normalize line endings to `\n`, concatenate with single `\n`, sha256). It **must** match the committed AC text byte-for-byte.

---

## Provenance

- **Sealed date:** 2026-05-20.
- **Sealed by:** chat-Claude session (Solo Claude Stack design project), re-sealed into repo 2026-05-20.
- **ac_list_sha256:** `34b089d9eb18367589f847e481cf853b6e6b94b6dc7c936bb7fe2135423e7383`
  _Computed over the eight §Acceptance criteria entries above via the D2.1 v2 extraction algorithm. If any AC text is edited, recompute and update this value, or `/build` halts `§provenance-chain-broken` / AC-hash mismatch._
- **Parent manifest:** `.cascade/manifests/SOL-1-update-linear.json` (or most recent sealed 0001 child-chain manifest — verify at apply time).
- **Four-hat seal:** Linear document `[SOL-DOC] Four-hat review — 0002 v0.2 release wrap-up` (id `1f4d1364-ad0d-4b89-b00a-01f581a561b0`), parented to SOL-102, sealed 2026-05-20 with `unresolved_count = 0` after founder ratified objections #12 (gate-naming limbo, path b) and #15 (byte-stability for purely-structural amendments, path b). See §Dogfood execution caveat for the F-1 limitation on the chat-side four-hat run.

---

## Dogfood execution caveat

The 2026-05-20 /specify, /plan, /review, and /update-linear for this epic ran in chat-Claude. The cascade primitives (Stop-hook orchestrator, SubagentStop hook validation, PreToolUse pyramid-tampering) were **not firing** in that environment — the cascade contract was honored only at the spec / document level. The four-hat panel ran as a single-model inline simulation, which structurally bypasses the F-1 fix from D2.1 v2 (the parent's independent recompute from per-subagent transcripts). This is acceptable for a design-pass dogfood. **Full F-1 compliance is satisfied at Code /build time**, not at this re-seal: the executing Code session against `OndraMasek/Solo-Vibing` with `.claude/hooks/*` active is where the hook-fired four-hat coverage check (`four-hat-objection-coverage.py` on SubagentStop) actually runs.

---

## Open spec question — decomposition.md.template

`docs/templates/` ships `spec.md.template` but **no** `decomposition.md.template`. (The `spec.md.template` correctly carries no "Pyramid shape" field — pyramid shape is a decomposition-level concept per `halt-messages.md` §Decomposition strategy.) This was the one recon gap not covered by any sealed spec.

**Decision (recorded here):** a `decomposition.md.template` is **out of scope for 0002** and is filed as a v0.2.x backlog candidate rather than added to this epic. Rationale: decomposition structure is currently authored by the `/plan` skill from first principles (the skill carries the child-block shape inline), and 0002's own `decomposition.md` is hand-authored against the 0001 precedent, so no template is load-bearing for this epic. Promoting it to a template is a cheap-but-non-urgent DX improvement that belongs with the other v0.2.x DX items, not wedged into a release-wrap-up. If the founder prefers it in-scope, it becomes Child 0002-C (`walking-skeleton`, single template file + one smoke test) — but the default is **defer**.

---

## Notes for the executing session

- **Read current post-PR-5 content first.** For Child 0002-A, read byte-for-byte the current `CLAUDE.md`, `README.md`, and `docs/templates/CLAUDE.md` from the repo before amending. Reconcile in place; preserve all v0.1 content the amendments don't touch.
- **Filename drift on the template.** SOL-103 says `docs/templates/CLAUDE.md`, but the on-disk file may be `CLAUDE.md.template` (the recon flagged this). Code confirms the actual filename at build and amends whichever exists.
- **Verify the eight hook scripts exist.** The §Hooks subsection (AC-1 / AC-3) enumerates eight scripts (seven from Child 0001-C + `pretool-write-denylist.sh` from 0001 AC-21). Confirm all eight are in `.claude/hooks/` post-PR-5 before citing them.
- **Verify the `--reconcile-only` flag name.** §Tainted state references it; confirm against `tools/solo-verify --help` post-PR-5 that the flag didn't drift.
- **Perceptual artifacts are sealed by Code, not now.** `perceptual/` ships as a directory with a `.gitkeep` only. `onboard-dry-run.txt` (0002-A) and `linear-tickets-created.json` (0002-B) are written at /build's at-write trigger. Fabricated perceptual evidence defeats the gate.
