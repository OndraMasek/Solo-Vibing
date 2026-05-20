# Child 0001-C — `.claude/hooks/` infrastructure + `.claude/settings.json` wiring — authoring notes

**Authored:** 2026-05-19, end of "0001 integration spec Child 0001-C — `.claude/hooks/` + settings wiring design session."

**Session deliverables (10 files):**

  1. `hooks-lib.md` — shared `_lib.sh` (bash) + `_lib.py` (Python) helpers; ~370 LOC each across both languages.
  2. `preflight-provenance-hook.md` — UserPromptSubmit hook; ~150 LOC bash.
  3. `pyramid-tampering-hook.md` — PreToolUse hook for Write/Edit on spec files; ~180 LOC bash.
  4. `four-hat-objection-coverage-hook.md` — SubagentStop hook on `four-hat-*` agents; ~260 LOC Python.
  5. `stop-orchestrator-hook.md` — single Stop-hook orchestrator + embedded halt-card text for `§kill-received-remote` and `§manual-halt-pending`; ~190 LOC bash.
  6. `session-start-state-restore-hook.md` — SessionStart hook with `startup|resume|compact|clear` source dispatch; ~210 LOC bash.
  7. `session-end-telemetry-hook.md` — SessionEnd async hook with JSONL telemetry schema; ~140 LOC bash.
  8. `precompact-safe-boundary-hook.md` — **NEW seventh script** (deviation from handoff; rationale in §Surfaced items #1 below); ~170 LOC bash.
  9. `settings-json.md` — `.claude/settings.json` wiring all seven scripts to D2.2 events; ~80 LOC JSON.
  10. `halt-messages-append-childC.md` — four halt-card stanzas for Child A's append-batch fold-in: `§compact-deferred-unsafe`, `§kill-received-remote`, `§manual-halt-pending`, `§pyramid-shape-violation/shape-tampering`.
  11. This notes doc.

This is the **only Child 0001-C session.** Walking-skeleton strategy fits in one session per the handoff's prediction. After this session: 7 of ~9 skills' design done + the hook/settings infrastructure complete. Remaining Phase-2-design sessions: Child 0001-D (`tools/solo-verify` Python stdlib CLI), Child 0001-E (`CLAUDE.md` + `README.md` amendments).

---

## Authoring decisions

### Seven hook scripts, not six (deviation from handoff)

Both the Child 0001-B continuation 2 handoff prompt and the `decomposition.md` "Files in scope" enumeration name **six** hook scripts:

  - `preflight-provenance.sh`
  - `pyramid-tampering.sh`
  - `four-hat-objection-coverage.py`
  - `stop-orchestrator.sh`
  - `session-start-state-restore.sh`
  - `session-end-telemetry.sh`

But:

  1. **D2.2 §Compact mechanics §PreCompact** specifies substantive PreCompact logic (increment `compact_cycles`, check safe-boundary, snapshot or defer/reset) that must run in a hook.
  2. The failing-test seed `test_settings_json_wires_all_events` (per `decomposition.md`) asserts `.claude/settings.json` contains entries for **PreToolUse, PostToolUse, SubagentStop, SessionStart, SessionEnd, PreCompact, Stop** — PreCompact explicitly enumerated.
  3. `decomposition.md` settings.json description states "SessionStart, SessionEnd, PreCompact wired per D2.2 §Hook events table" — but no script is named for PreCompact.

The cleanest disposition: author the seventh script (`precompact-safe-boundary.sh`) so v0.2's hook infrastructure is complete end-to-end. The handoff/decomposition row's omission of the script is an authoring oversight (the row enumerates six but the contract requires seven).

**Apply-time amendment:** `decomposition.md` Child 0001-C "Files in scope" needs a seventh row for `.claude/hooks/precompact-safe-boundary.sh`. See §Surfaced items #1 below.

### `.cascade/run-state.json` (v2.1 canonical), NOT `.cascade/manifests/run-state.json` (decomposition.md inaccuracy)

`decomposition.md` describes `session-start-state-restore.sh` as "restores cascade:run-state from `.cascade/manifests/run-state.json`" — but D2.1 v2.1 canonicalized the path as `.cascade/run-state.json` at repo root (sibling to `.cascade/manifests/`, `.cascade/session/`, `.cascade/halt/`). The hook scripts use the v2.1 canonical path. `decomposition.md` predates v2.1 and carries a small path-error.

**Apply-time amendment:** see §Surfaced items #2.

### Telemetry path: `.cascade/telemetry/sessions.jsonl` (single appended file), reconcile retro skill at apply-time

`decomposition.md` (canonical for Child 0001-C scope): `.cascade/telemetry/sessions.jsonl` — single appended JSONL file.
`retro-SKILL-amendments.md` (Child 0001-B continuation 2): `.cascade/session/<milestone>-*.jsonl` — per-milestone files.

The single-file pattern wins on cross-milestone aggregation queries and is simpler to manage; `/retro` filters by `active_milestone` field at read-time. **Apply-time amendment:** `retro-SKILL-amendments.md` Section 3 needs revision to read from `.cascade/telemetry/sessions.jsonl` and filter by milestone. See §Surfaced items #3.

### Shared `_lib.sh` + `_lib.py` per `decomposition.md` notes

Per `decomposition.md` Child 0001-C "Notes for the executing session": "Factor that into a `.claude/hooks/_lib.sh` (bash) and `.claude/hooks/_lib.py` (Python) so each script is roughly 20–40 lines of predicate logic instead of 60–80 lines of stdin / event-shape handling." Authored verbatim in `hooks-lib.md`.

Shared helpers:

  - `read_hook_payload` / `_read_hook_payload` — stdin JSON parsing.
  - `sha256_file` / `sha256_string` / `sha256_manifest_self_zeroed` — D2.1 v2 recomputation predicate.
  - `read_run_state` / `read_manifest` — `.cascade/` file IO.
  - `emit_hook_specific_output` — standard wrapper for non-Stop events.
  - `emit_stop_block` — Stop / SubagentStop top-level-fields-only quirk per D2.2.
  - `emit_additional_context` — SessionStart-specific factual-phrasing emitter.
  - `log_halt` — append to `.cascade/halt/<code>.txt`.
  - `project_dir` (Python) / `$CLAUDE_PROJECT_DIR` fallback (bash) — walk-up-from-PWD for standalone CLI use.
  - `trace` — env-gated stderr logging (`SOLO_HOOK_TRACE=1`).

Each hook script is now ~20-40 LOC of predicate logic (per the spec), plus a 5-10 LOC source/import preamble. Total per-script LOC is ~70-200 depending on complexity (the four-hat Python script is the largest at ~260 LOC; the rest are bash and shorter).

### Stop / SubagentStop output schema quirk handling

Per D2.2 §Stop / SubagentStop output schema quirk: top-level-fields-only output for Stop, SubagentStop, StopFailure events. The `emit_stop_block` helper emits the right shape:

```json
{"decision": "block", "reason": "<factual diagnostic>"}
```

All other events use `emit_hook_specific_output` which emits the standard wrapper. The split is exhaustively-tested via the lib's emitter functions; hook scripts never compose the JSON by hand.

**PreCompact output shape ambiguity:** D2.2 §Compact mechanics §PreCompact's code blocks use the top-level-fields shape, but D2.2 §Stop / SubagentStop output schema quirk explicitly names Stop, SubagentStop, StopFailure — not PreCompact. The cleanest interpretation: PreCompact follows the same quirk pattern (block decisions are structurally similar). The `precompact-safe-boundary.sh` script uses the top-level shape; the executing apply session should validate against Claude Code v2.0.76+ at script-test-time. See §Surfaced items #5.

### Factual phrasing for `reason` strings (F-Int-2 disposition)

Per D2.2 §Critical caveats #3 + D2.3 v1.2 four-hat review §F-Int-2: hook `reason` strings are factual diagnostics, NOT imperative commands. The forcing function is the `decision: block` itself + the model's compliance with the post-block context. The prose describes the failure ("expected X, got Y; recovery: --reconcile"), the structural enforcement is the JSON's `decision` field.

This is applied across all six bash + Python hooks. The `next_chain_step` continuation in `stop-orchestrator.sh` and `session-start-state-restore.sh` is the load-bearing test case: the hook says "the next stage is X per cascade:run-state.next_chain_step," NOT "Task-invoke X." The `/Chains` contract in the relevant skill carries the actual continuation logic.

### Halt-card authoring for `§kill-received-remote` + `§manual-halt-pending`

Per Child 0001-B continuation 1 Surfaced item #4 + the handoff prompt: these two halt codes are referenced in Child 0001-B continuation 1's `/build` amendment §Interaction with sidecar commands subsection but were not in v0.1 nor in Child A's `halt-messages-append.md`. This session authors them.

The halt-card text is embedded inline in `stop-orchestrator-hook.md` (the script's diagnostic text becomes the card content) AND separately in `halt-messages-append-childC.md` (the append-block format for fold-in to `docs/templates/halt-messages.md` at apply-time).

The fold-in pattern matches Child A's `halt-messages-append.md` apply convention: alphabetical placement, sub-cases as refinements of parent cards.

### `§compact-deferred-unsafe` is novel

This halt code is introduced by `precompact-safe-boundary-hook.md` (the new seventh script). Not in v0.1, not in Child A's append. Authored in `halt-messages-append-childC.md` alongside `§kill-received-remote` and `§manual-halt-pending`.

### `§pyramid-shape-violation/shape-tampering` is a refinement, not a new card

`§pyramid-shape-violation` parent card lives in Child A's `halt-messages-append.md` per the F-2 fix's full halt-card surface. The `pyramid-tampering.sh` hook surfaces the `/shape-tampering` sub-case. The refinement is authored in `halt-messages-append-childC.md` as a sub-case stanza appended below the parent card's body at apply-time.

### Four-hat objection-coverage as `command`-type Python, not `agent`-type Claude subagent

D3.4 §What is a gate names this hook as "the only agent-type hook in the cascade." D2.2 §Hook handler types defines `agent` type as "spawns a fresh subagent with Read/Grep/Glob" — heavier and slower than `command`.

This session realizes the four-hat-objection-coverage predicate as **command-type Python** (`.py` script invoked synchronously) rather than agent-type (Claude subagent spawn). The predicate's *intent* is agent-judgment-shaped (read transcripts, validate four-hat template, check coverage); its *realization* is deterministic Python regex + JSONL parsing. The trade: faster (milliseconds vs seconds), deterministic (no Claude turn), simpler.

**Apply-time amendment:** D3.4 §What is a gate's "single agent-type hook" claim needs reframing. See §Surfaced items #4.

### Defensive `project_dir` fallback for standalone CLI

Per D2.2 §Critical caveats #1: hooks may not fire on `max_turns`, so every predicate must also be invocable as a standalone `solo-verify` CLI. The lib's `project_dir` (Python) and bash `$CLAUDE_PROJECT_DIR` fallback walk up from `$PWD` looking for `.cascade/`. This makes the hook scripts trivially callable from any subdirectory of a Solo-Vibing-bootstrapped repo, with or without the Claude Code env vars set.

The fallback also means the hooks compose cleanly with `solo-verify` (Child 0001-D scope) — `solo-verify` can shell out to the same hook scripts as a CLI surface.

---

## Surfaced items (deferred amendments queued for apply-time pass)

These are amendments to *prior-session deliverables* and *binding design docs* surfaced during Child 0001-C authoring. They cannot land in this session's output; they need an apply-time amendment pass after Child 0001-D and Child 0001-E complete.

### 1. `decomposition.md` Child 0001-C row: enumerate seven hook scripts, not six

**Surface.** `decomposition.md`'s "Files in scope (full paths):" for Child 0001-C lists six hook scripts + `.claude/settings.json`. The seventh script (`.claude/hooks/precompact-safe-boundary.sh`) is necessary for D2.2 §Compact mechanics §PreCompact to be implemented and for `test_settings_json_wires_all_events` to pass.

**Amendment needed.** Add a seventh bullet to the "Files in scope" list:
> `.claude/hooks/precompact-safe-boundary.sh` — bash script. Fired by PreCompact (no matchers; script reads `trigger` from payload). Implements three-band threshold model per D2.2 §Compact mechanics §PreCompact: increments compact_cycles in `.cascade/session/<session_id>.json`; if ≥ 2 emits `§session-reset-required` and sets `reset_due: true`; else checks safe-boundary and emits `§compact-deferred-unsafe` (unsafe) or writes precompact snapshot to `.cascade/session/precompact-<id>-<ts>.json` and exits 0 (safe). Used by Group F auto-fire compact recovery.

**Failing-test seed addition (optional, for v0.2.x coverage):**
> `test_precompact_safe_boundary_blocks_on_cycle_2` — `[smoke]` — asserts cycle 1→2 transition sets reset_due:true and emits block decision; covers AC-14.
> `test_precompact_safe_boundary_snapshots_on_safe` — `[smoke]` — asserts safe-boundary case writes a precompact snapshot file and exits 0; covers AC-14.

**Target landing:** apply-time amendment to `decomposition.md`.

### 2. `decomposition.md` `session-start-state-restore.sh` path-reference correction

**Surface.** `decomposition.md` says `session-start-state-restore.sh` "restores `cascade:run-state` from `.cascade/manifests/run-state.json`." The canonical path per D2.1 v2.1 is `.cascade/run-state.json` (repo root), NOT `.cascade/manifests/run-state.json`.

**Amendment needed.** Substitute the path in `decomposition.md`'s `session-start-state-restore.sh` description.

**Target landing:** apply-time amendment to `decomposition.md`.

### 3. `retro-SKILL-amendments.md` Section 3 telemetry path reconciliation

**Surface.** `retro-SKILL-amendments.md` (Child 0001-B continuation 2) Section 3 reads per-session telemetry from `.cascade/session/<milestone>-*.jsonl`. This session's `session-end-telemetry.sh` writes to `.cascade/telemetry/sessions.jsonl` (single appended file) per `decomposition.md`. The retro skill amendment needs a path correction and read-strategy update.

**Amendment needed.** In `retro-SKILL-amendments.md` Section 3:

  - Change the path reference from `.cascade/session/<milestone>-*.jsonl` to `.cascade/telemetry/sessions.jsonl`.
  - Update the read-strategy from "list files matching the milestone glob" to "read the single JSONL and filter records where `active_milestone == <milestone>`."

**Target landing:** apply-time amendment to `retro-SKILL-amendments.md`.

### 4. D3.4 §What is a gate: reframe "single agent-type hook"

**Surface.** D3.4 §What is a gate names the four-hat objection-coverage check as "the cascade's single agent-type hook on SubagentStop." The hook is realized as `command`-type Python in this session, not `agent`-type Claude subagent spawn. The framing-vs-implementation gap should be made explicit.

**Amendment needed.** Two options for D3.4 §What is a gate:

  - **(a) Drop the "agent-type" claim.** Reword to "the cascade's single hook that wraps an LLM-judgment-shaped predicate" without specifying realization-type.
  - **(b) Reframe as command-type with agent-intent.** Reword to "the cascade's single LLM-judgment-shaped predicate, realized as deterministic Python for performance and determinism (per the Child 0001-C apply-time disposition)."

Option (b) is more honest about the trade-off; option (a) is simpler. Either works; founder picks.

**Target landing:** apply-time amendment to `D3_4_gate_definitions.md`.

### 5. Validate PreCompact output shape against Claude Code v2.0.76+

**Surface.** D2.2 §Stop / SubagentStop output schema quirk explicitly names Stop, SubagentStop, StopFailure as the events with the top-level-fields-only output. PreCompact is not in that list. D2.2 §Compact mechanics §PreCompact's code blocks use the top-level-fields shape. The cleanest interpretation is that PreCompact follows the same convention (since blocking a compact is structurally similar to blocking a Stop), but this is interpretation, not direct verification.

**Amendment needed.** At apply-time, validate `precompact-safe-boundary.sh`'s output against Claude Code v2.0.76 (the version cited in D2.2 §Stop / SubagentStop output schema quirk). If PreCompact in fact uses the standard `hookSpecificOutput` wrapper, switch the script to emit that shape via `emit_hook_specific_output`. The lib has both emitters; only the script-level call changes.

**Target landing:** apply-time validation + (if needed) `precompact-safe-boundary.sh` patch.

### 6. PRIMING_MARKERS validation against v0.1 four-hat agent frontmatter

**Surface.** `four-hat-objection-coverage.py` hardcodes a `PRIMING_MARKERS` dict mapping hat names to expected priming-text substrings. These substrings must match what v0.1's `.claude/agents/four-hat-*.md` agent frontmatters dispatch. If any marker doesn't match, Predicate 1 will false-fire.

**Amendment needed.** At apply-time, the executing Claude Code session reads each v0.1 four-hat agent file's frontmatter and validates that the `PRIMING_MARKERS` substring is present in the dispatched priming prompt. If any marker is absent or different, update the dict.

**Target landing:** apply-time validation against `.claude/agents/four-hat-{user,engineer,pm,skeptic}.md`.

### 7. MultiEdit conservative-allow in pyramid-tampering.sh

**Surface.** `pyramid-tampering.sh` handles `Write` and `Edit` tool calls; `MultiEdit` is conservatively allowed without inspection (the replay logic for MultiEdit's edit sequence is fragile in bash). The at-write gate inside `/specify` catches MultiEdit shape violations at seal time, so the v0.2 conservative-allow is safe — but MultiEdit-mediated tampering would escape the pre-flight defense.

**Amendment needed.** v0.2.x: add MultiEdit handling either by:

  - Shelling out to a Python helper that uses str.replace semantics to replay the edit sequence.
  - Or: blocking all MultiEdit writes to spec files (conservative; over-restrictive).

**Target landing:** v0.2.x design queue; flag in `D3_2_test_pyramid_declaration.md` §Future work.

### 8. PostToolUse empty array satisfies smoke test (carry-forward placeholder)

**Surface.** `decomposition.md`'s `test_settings_json_wires_all_events` failing-test seed asserts PostToolUse is wired in `.claude/settings.json`. v0.2 doesn't add new PostToolUse hooks; the v0.1 Linear-write mirror-sha predicate (carried forward) would land here if v0.1 codified it as a settings.json entry.

**Amendment needed.** At apply-time, the executing session should fold the v0.1 Linear-write mirror-sha predicate into the PostToolUse entry if it's been promoted to a hook (per Child A scope). If not, the empty array stays as a placeholder.

**Target landing:** apply-time decision; update `settings-json.md` PostToolUse entry per Child A's resolution.

### 9. Pipe-alternation vs wildcard for SubagentStop matcher syntax

**Surface.** `.claude/settings.json` uses pipe-alternation (`four-hat-user|four-hat-engineer|four-hat-pm|four-hat-skeptic`) for the SubagentStop matcher. Some Claude Code versions support glob wildcards (`four-hat-*`); some require regex; some accept both. The pipe-alternation is explicit and version-portable but may be more verbose than necessary.

**Amendment needed.** At apply-time, validate that pipe-alternation is the canonical matcher syntax for Claude Code v2.0.76+ SubagentStop. If wildcard is more idiomatic, switch to `four-hat-*`.

**Target landing:** apply-time validation.

### 10. `$schema` URL verification

**Surface.** `settings-json.md` declares a `$schema` field pointing to `https://json.schemastore.org/claude-code-settings.json` (speculative). Anthropic publishes the canonical Claude Code settings JSON Schema URL somewhere; the speculative URL may not match.

**Amendment needed.** At apply-time, look up the canonical schema URL from Anthropic's docs (`code.claude.com/docs/en/hooks` or the SDK reference) and substitute.

**Target landing:** apply-time URL lookup.

---

## Reconciliation summary (apply-time queue)

The full apply-time reconciliation pass after Children 0001-A through 0001-E complete needs to:

  1. Add seventh hook script row to `decomposition.md` Child 0001-C ("Files in scope") + two failing-test seeds *(this session §Surfaced items #1)*.
  2. Correct path reference in `decomposition.md` `session-start-state-restore.sh` description *(this session §Surfaced items #2)*.
  3. Reconcile telemetry path in `retro-SKILL-amendments.md` Section 3 *(this session §Surfaced items #3)*.
  4. Reframe D3.4 §What is a gate's "single agent-type hook" claim *(this session §Surfaced items #4)*.
  5. Validate PreCompact output shape; patch `precompact-safe-boundary.sh` if v2.0.76 uses `hookSpecificOutput` wrapper *(this session §Surfaced items #5)*.
  6. Validate `PRIMING_MARKERS` dict against v0.1 four-hat agent frontmatter *(this session §Surfaced items #6)*.
  7. Defer MultiEdit handling in `pyramid-tampering.sh` to v0.2.x; flag in D3.2 §Future work *(this session §Surfaced items #7)*.
  8. Decide PostToolUse placeholder fate per Child A's resolution *(this session §Surfaced items #8)*.
  9. Validate SubagentStop matcher syntax (pipe-alternation vs wildcard) *(this session §Surfaced items #9)*.
  10. Verify `$schema` URL in `.claude/settings.json` *(this session §Surfaced items #10)*.

Carry-forward items from prior Child 0001-B sessions (continuations 0, 1, 2) remain in the apply-time queue. Total expected amendment-pass scope after Child 0001-C: ~10 lines net new edits to `decomposition.md`, ~5 lines to `retro-SKILL-amendments.md`, ~2 lines to `D3_4_gate_definitions.md`, plus apply-time validations.

---

## Subsequent design sessions after this one

  - **Child 0001-D** — `tools/solo-verify` Python stdlib script implementing D3.4's CLI surface (`solo-verify onboard|specify|review|plan|update-linear|build|wrap|verify|retro <id>`, `--gate <name>`, `--list-gates`, `--explain <stage>.<gate-name>`, exit codes per spec AC-15). Walking-skeleton strategy with heavy `[unit]` coverage. One to two sessions likely. Includes F-Rev-2 carry-forward (extend `--reconcile` to `/onboard`, `/update-linear`, `/review`, `/verify`, `/retro`).

  - **Child 0001-E** — `CLAUDE.md` + `README.md` amendments + lockstep update to `docs/templates/CLAUDE.md`. Walking-skeleton strategy. One session.

Total Phase-2-design sessions remaining after this one: 2–3 (Child 0001-D one-to-two sessions, Child 0001-E one session).

---

## Handoff prompt for next session

> **Title:** 0001 integration spec Child 0001-D — `tools/solo-verify` Python stdlib CLI.
>
> **Task:** Author `tools/solo-verify` — a Python stdlib script (Python 3.10+, no third-party deps per D4.0) implementing the full CLI surface from D3.4 §`solo-verify` CLI surface + spec AC-15: per-stage invocations (`solo-verify onboard|specify|review|plan|update-linear|build|wrap|verify|retro <id>`), `--gate <name>`, `--list-gates [stage]`, `--explain <stage>.<gate-name>`, and the standardized exit codes (0 all passed; 1 standard halt; 2 stage/gate unknown; 3 manifest chain broken / provenance halt; 4 filesystem-or-Linear inconsistency that prevents evaluation). Walking-skeleton strategy with heavy `[unit]` coverage.
>
> **Should fit in one to two sessions.** The CLI is the durable backbone behind the cascade: hooks call it on the auto-fire path; the founder calls it on the resume path; tests call it on the smoke path. Each per-stage subcommand evaluates the gates from Child 0001-B's amendments (which this session's hooks compose against). Most predicates are short (sha recompute, JSON field-existence check, regex parse) but the CLI surface aggregates them; the script is ~600-1200 LOC depending on shared-helper factoring.
>
> **Three concrete deliverable clusters:**
>
>   1. **The `tools/solo-verify` Python script.** Single file, stdlib-only per D4.0. Per-stage `verify_<stage>` functions that compose gate predicates; a top-level CLI dispatcher; the exit-code mapping.
>   2. **`--reconcile` carry-forward** per F-Rev-2's queued amendment: extend `--reconcile` to `/onboard`, `/update-linear`, `/review`, `/verify`, `/retro` (v0.1 ships it on `/specify`, `/plan`, `/build`, `/wrap` only). Per-stage reconciliation semantics: re-derive the stage's expected state from the upstream manifest's outputs; report drift; offer interactive or `--yes`-batch repair.
>   3. **Per-stage failing-test seed `[unit]` coverage.** Each per-stage gate predicate is exercised via a `[unit]` test with a stub manifest + expected pass/fail. The smoke tier covers the CLI dispatcher; the unit tier covers predicates.
>
> **Coordination with Child 0001-C hooks.** Each hook in `.claude/hooks/` calls `solo-verify` as its durable backup CLI per D2.2 §Critical caveats #1 (the `max_turns` gap). The hooks call `solo-verify <stage> <ticket>`; the CLI must accept the same arg-shape and produce the same exit codes. The `stop-orchestrator.sh` script's `solo-verify build-finalize <ticket>` dispatch is the load-bearing test case.
>
> **Read first (use `project_knowledge_search`):**
>
>   - `00_PROJECT_INSTRUCTIONS.md`
>   - All Child 0001-B deliverables (continuations 0, 1, 2) — the gate predicates the CLI evaluates.
>   - All Child 0001-C deliverables (this session) — the hook contracts the CLI composes with.
>   - `D3.4_gate_definitions.md` §`solo-verify` CLI surface (the binding spec).
>   - `D2.1_trust_model.md` v2 §Caller-side verification protocol (the predicate framing).
>   - `D2.1_trust_model.md` v2.1 (the canonical run-state path).
>   - `D4.0_solo_verify_build_distribution.md` (Python 3.10+ floor; stdlib-only constraint).
>   - `D4.5_reconciliation_primitives.md` (the `--reconcile` semantic).
>   - `decomposition.md` Child 0001-D row.
>   - `spec.md` AC-15.
>
> **Phase:** Child 0001-D (walking-skeleton strategy — perceptual artifact = a working `solo-verify --list-gates` rendering against a real cascade).
>
> **Deliverables:**
>
>   - `tools/solo-verify` — patch-ready Python script.
>   - `tests/solo-verify/` — per-stage `[unit]` tests; `[smoke]` CLI tests.
>   - `child_D_solo_verify_authoring_notes.md` — surfaced items, reconciliation queue additions, handoff prompt for Child 0001-E.
>
> **Surfaced items to address in Child 0001-D's session (from Child 0001-C):**
>
>   - **F-Rev-2 carry-forward:** extend `--reconcile` to `/onboard`, `/update-linear`, `/review`, `/verify`, `/retro` per the v0.1 queued amendment.
>   - **`solo-verify build-finalize` contract:** stop-orchestrator.sh calls this; CLI must support it.
>   - **Verify Python 3.10+ floor:** D4.0's stack-floor decision; use `match` statements, type hints with PEP 604 union syntax, etc.
