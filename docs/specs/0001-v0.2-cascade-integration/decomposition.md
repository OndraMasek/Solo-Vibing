# 0001 — Decomposition sketch

**Status:** Hand-authored sketch (the cascade is not yet running in v0.2 form; `/plan`'s decomposer will normally write this document). The sketch is structured to match what `/plan` would produce so the executing session can either consume it as-is or hand it to `/plan` for re-derivation once the cascade is bootstrapped.

**Parent:** `0001-v0.2-cascade-integration`.
**Parent strategy:** `hybrid` — per D3.1, every child carries an explicit non-inherited strategy. `/plan` halts `§hybrid-without-child-overrides` if any child lands without one.

---

## Children at a glance

| Child | Slug | Strategy | Scope |
|---|---|---|---|
| 0001-A | `v0.2-templates-and-config` | `walking-skeleton` | Template files, config schema, gitignore, directory skeletons. End-to-end demoable as: `/onboard` on a fresh fork produces a v0.2-shaped scaffold. |
| 0001-B | `v0.2-skill-amendments` | `capability-cluster` | Nine `.claude/skills/*/SKILL.md` files. Each skill is a capability with a documented surface (frontmatter + decision-table). |
| 0001-C | `v0.2-hook-infrastructure` | `walking-skeleton` | `.claude/hooks/` directory + `.claude/settings.json` wiring. End-to-end demoable as: a SubagentStop event invokes the four-hat coverage check and a PreToolUse event blocks a malformed manifest write. |
| 0001-D | `v0.2-solo-verify-cli` | `walking-skeleton` (with heavy `[unit]` coverage) | `tools/solo-verify` Python stdlib script implementing the full D3.4 CLI surface. End-to-end demoable as: `python3 tools/solo-verify --list-gates` prints all 22 gates. |
| 0001-E | `v0.2-docs-update` | `walking-skeleton` | `CLAUDE.md` and `README.md` amendments + lockstep update to `docs/templates/CLAUDE.md`. Rendered markdown is the perceptual artifact. |

Five children. No nested hybrid; each child carries one strategy and `/plan` halts if any subsequent finding pushes a child to need its own hybrid split — at which point the child re-seals under hybrid and gains its own decomposition.md sub-tree. v0.2 caps hybrid nesting at one level per D3.4 §`/verify` dispatch.

---

## Child 0001-A — `v0.2-templates-and-config`

**Strategy:** `walking-skeleton`.

**Rationale.** Templates, config, gitignore, and committed-empty directory skeletons are the scaffold a fresh fork inherits. The end-to-end vertical slice is: `bootstrap.sh` clones → user runs `/onboard` → the v0.2-shaped scaffold is in place and the user can run `/specify` against a v0.2 spec template. "Does the scaffold actually work end-to-end" is the load-bearing question, exactly the walking-skeleton signal from D3.1.

**Files in scope (full paths):**

- `docs/templates/spec.md.template` — amend `## Failing-test seed` section per D3.2 §Spec template addition: add `**Pyramid shape:**` preamble line with `<strategy>`-shaped + required/optional/forbidden placeholders; add per-test `— [tag] —` notation in the **Tests.** subsection; provide three rendering variants as comments-or-conditional-text (regular for walking-skeleton/api-boundary/capability-cluster; refactor-spike no-tests-with-anchor-language; hybrid no-parent-shape with deferral-to-children language).
- `docs/templates/halt-messages.md` — append the eleven new halts. Use the existing halt-card structure (When / Recommendation / Rationale / Alternatives / Diagnostic context). Order: §pyramid-shape-violation, §pyramid-tag-invalid (D3.2); §perceptual-evidence-missing, §invariance-pass-set-regression, §invariance-config-missing, §invariance-pass-set-empty, §invariance-seal-tampering, §invariance-config-changed (D3.3); §strategy-annotation-unresolved, §verify-milestone-aggregation-failed, §provenance-chain-broken (D3.4). Sub-cases listed inside Diagnostic context per D3.2's existing pattern.
- `docs/templates/.solo-config.json.template` (the rendered-by-/onboard version) — add `"invariance": {"pass_set_capture_command": ""}` block at top level. Add `"workflow"."default_strategy": ""` slot (optional, empty default; behavioral wiring deferred per Open Question 4 of the parent spec).
- `docs/.solo-config.json` (the framework's own) — same additions; populate `invariance.pass_set_capture_command` empty (the framework itself does not run refactor-spike on itself in v0.2).
- `docs/.solo-config.example.json` — new file. Show populated examples for each runner: `"pytest -q --tb=no | grep PASSED | sort"`, `"pnpm vitest run --reporter=json | jq -r '.testResults[].assertionResults[] | select(.status==\"passed\") | .fullName' | sort"`, `"jest --listTests --testPathPattern=passed | sort"`, `"go test -v ./... 2>&1 | grep -E '^--- PASS' | sort"`, `"cargo test --quiet 2>&1 | grep 'test result' | sort"`. Each commented with the runner name. The framework reads neither this nor the example file at runtime — `.solo-config.json` is canonical. The example exists for founder cargo-culting.
- `docs/templates/capability-artifact-types.md` — new file. Render the seven-row canonical table from D3.3 §Capability-cluster perceptual predicate verbatim. Add a header note: "Read by `/specify` skill step 3 to resolve `artifact_type` and validate `artifact_path` extension for capability-cluster `[perceptual]` entries. Novel artifact types not in this table use founder-declared extensions recorded on the manifest." Add a footer note: "Versioned implicitly by D3.3's schema_version; v0.2.x can add rows without breaking sealed manifests." (Per D3.3 §Single canonical table vs per-spec discretion.)
- `.gitignore` — append `docs/specs/*/invariance/pass-set-at-verify.txt` and a one-line comment naming the rule it implements (D3.3 §Refactor-spike invariance predicate). Keep existing entries unchanged.
- `.cascade/manifests/.gitkeep` — new committed-empty file with a one-line comment: "Cascade manifest store; populated by /specify, /plan, /review, /update-linear, /build, /wrap, /verify, /retro. Filesystem-canonical per D2.1 v2."
- `.cascade/halt/.gitkeep` — new committed-empty; comment: "Halt-card diagnostics; one file per halt event, written by the halting skill, read by /retro."
- `.solo-locks/.gitkeep` — new committed-empty; comment: "Per-resource write locks per D2.1 v2; concurrent same-product stages first-class."
- `.ralph/.gitkeep` — new committed-empty; comment: "Ralph loop state for /build; iteration counts, fix_plan checkpoints. v0.1 may or may not have used this path; v0.2 standardizes."
- `docs/product/.gitkeep` — new committed-empty; comment: "Filesystem mirror of Linear Product project documents per D1; written by /onboard and amended by /constitution."
- `.claude/rules/code-markers.md` — new file. Declares the `🤔` (clarify question), `📝` (copy pending), and `☣️` (tainted code region — requires `--reconcile`) marker convention. Per AC-19, finalizes the glyph deferred in D4.2 §D4.4. Surfaced in CLAUDE.md amendment (Child E).
- `.claude/rules/write-discipline.md` — amend with denylist + reviewer-stance soft-check section per AC-21. Names `.claude/agents/build-write-denylist.txt` as the hard-halt denylist source; describes the reviewer-stance soft-check inside `/review` per `.claude/rules/auditor-stance.md`. Explicitly out: hard allow-list semantics.
- `.claude/agents/build-write-denylist.txt` — new file. Initial denylist contents per D4.1.7: `docs/.solo-config.json`, `.claude/rules/*.md`, `docs/templates/halt-messages.md`, `.cascade/*`, `.solo-locks/*`. One pattern per line; `#` comments allowed.
- `.github/workflows/ci.yml` — new file per AC-20. GitHub Actions workflow firing on `pull_request` and `push` to `main`. Job runs (1) `python3 tools/solo-verify --list-gates` smoke and (2) `python3 -m unittest discover tests/solo-verify/`. Python 3.10. Free tier, public repo. No secrets needed.

**Pyramid shape:** `walking-skeleton`-shaped — required: `smoke`, `perceptual`. Optional: `unit`, `integration`. Forbidden: `contract`, `invariance`.

**Failing-test seed (per-child, will be populated at /specify time):**

- `test_spec_template_carries_pyramid_shape_line` — `[smoke]` — asserts the rendered `spec.md.template` contains the literal string `**Pyramid shape:**` in the `## Failing-test seed` section; covers AC-1.
- `test_halt_messages_carries_eleven_new_halts` — `[smoke]` — asserts each of the eleven §-prefixed halt identifiers appears at least once in `halt-messages.md`; covers AC-2.
- `test_solo_config_template_has_invariance_block` — `[smoke]` — asserts `.solo-config.json.template` parses as JSON and contains `invariance.pass_set_capture_command`; covers AC-3.
- `test_capability_artifact_types_md_lists_seven_rows` — `[smoke]` — asserts the markdown table at `docs/templates/capability-artifact-types.md` has at least seven data rows; covers AC-4.
- `test_gitignore_excludes_verify_pass_set` — `[smoke]` — asserts `.gitignore` contains the line `docs/specs/*/invariance/pass-set-at-verify.txt`; covers AC-5.
- `test_committed_empty_directories_exist` — `[smoke]` — asserts `.cascade/manifests/.gitkeep`, `.cascade/halt/.gitkeep`, `.solo-locks/.gitkeep`, `.ralph/.gitkeep`, `docs/product/.gitkeep` all exist; covers AC-5.
- `test_solo_config_example_parses_with_runner_keys` — `[unit]` — asserts the JSON parses and contains commented-out examples for at least pytest, vitest, jest, go-test, cargo-test runners (matched by substring); covers AC-3.
- `test_v0_2_scaffold_perceptual` — `[perceptual]` — asserts the byte-stable PNG at `docs/specs/0001-v0.2-cascade-integration/perceptual/0001-A-scaffold-tree.png` regenerates from a `tree -a .cascade docs/templates docs/.solo-config* | rsvg-convert` (or equivalent — founder picks the renderer at /build time); covers AC-1 through AC-5 collectively as the end-to-end scaffold demonstration. Per D3.3 walking-skeleton perceptual predicate.

**Notes for the executing session:**

- The spec.md.template variant rendering is conditional text in markdown, not Jinja or similar. Three alternative `## Failing-test seed` blocks live in the same file, each preceded by an HTML comment `<!-- variant: walking-skeleton -->` etc. The `/specify` skill at step 3 selects the variant by reading the declared strategy.
- The `.gitkeep` files carry their purpose as a single-line `#`-comment to survive future "what's this empty directory" reviews.

---

## Child 0001-B — `v0.2-skill-amendments`

**Strategy:** `capability-cluster`.

**Rationale.** Each of the nine cascade skills is a discrete capability with its own input contract (the upstream stage's manifest), its own output contract (the manifest it seals), and its own surface for founder interaction (step prompts, halt cards). Per D3.1 §capability-cluster, this is the canonical shape: "each child delivers one bounded capability." Multiple capabilities, each independently testable, no end-to-end vertical slice across all nine — the parent (this spec) plus child A's scaffold is what provides end-to-end-ness; this child provides the nine capabilities the scaffold hosts.

**Files in scope (full paths):**

- `.claude/skills/specify/SKILL.md` — step 3 amendments per AC-6 (pyramid populator from D3.2 catalog cached as a const block in the skill; per-test `[tag]` resolution rules; `artifact_path` drafting per D3.3 per strategy; `artifact_type` recording for capability-cluster reading from `docs/templates/capability-artifact-types.md`); step 7 evaluates the five `spec.*` gates from D3.4 (`spec.strategy-annotation` clears step-1 annotation, `spec.pyramid-shape`, `spec.failing-test-seed`, `spec.perceptual-artifact-path`, `spec.provenance`).
- `.claude/skills/plan/SKILL.md` — evaluate the `plan.*` gates from D3.4 (`plan.provenance`, `plan.children-have-strategies-for-hybrid` which fires §hybrid-without-child-overrides if any hybrid-parent child lacks an explicit strategy, `plan.decomposition-doc-sealed`); D3.1 decomposition-override findings flow through the existing incorporate/defer/reject critique pattern and write to `decomposition.md` under each child's block as a `Strategy:` field with override-rationale.
- `.claude/skills/review/SKILL.md` — evaluate the `review.*` gates from D3.4; the four-hat objection-coverage check fires as the cascade's single agent-type hook on `SubagentStop` per D2.2 §Stop / SubagentStop output schema quirk (top-level fields only, no `hookSpecificOutput` wrapper, `{"decision": "block", "reason": "..."}` shape).
- `.claude/skills/build/SKILL.md` — evaluate the `build.*` gates from D3.4 (`build.provenance` pre-flight reads parent manifest sha and verifies chain integrity, `build.pyramid-tampering` reads `pyramid_shape` from parent manifest and rejects a seed file that mutates tags from sealed version per D3.2 §Downstream consumer touch-points, `build.test-execution` is the existing Ralph backpressure contract preserved unchanged).
- `.claude/skills/wrap/SKILL.md` — evaluate the `wrap.*` gates from D3.4 (`wrap.provenance`, `wrap.tests-green` is the existing red-tests-block predicate renamed, `wrap.mirror-sha-match` is the existing filesystem-Linear sha match predicate renamed, `wrap.linear-state-updated` is the existing Linear-state-write predicate renamed). Behavior unchanged from D2.1 v2; naming standardized for `solo-verify` parity.
- `.claude/skills/verify/SKILL.md` — implement the per-strategy dispatch matrix from D3.4 §`/verify` gate dispatch by strategy: walking-skeleton / api-boundary / capability-cluster children dispatch to `verify.perceptual-evidence` (evaluates D3.3 P1–P4 per strategy); refactor-spike children dispatch to `verify.invariance` (evaluates D3.3 P5–P9); hybrid children recurse one level per D3.4 §hybrid-nesting-too-deep. Multi-child halt-card aggregation per D3.4 §Aggregation rules: within a gate, earliest-firing predicate's halt is primary; across children, each stands alone in the milestone roll-up. Writes `children_gate_outcomes[]` on the `/verify` manifest per D3.4 §Manifest schema additions; refactor-spike children also record `seal_pass_set_count` and `verify_pass_set_count`.
- `.claude/skills/retro/SKILL.md` — read `children_gate_outcomes[]` from `/verify` manifests; surface tag distribution (count children per strategy) and per-gate outcome counts (e.g., "11/12 children passed `verify.perceptual-evidence`; 1 halted on `§perceptual-evidence-missing/byte-stability-failed`").
- `.claude/skills/onboard/SKILL.md` — create the six Linear projects per D1 (Product / Architecture / Design / Milestones / Backlog / Done), with marker-prefixed names if `linear.project_naming = "prefixed"` (set by step 1 scan); create the Status document under the Product project; write `docs/.solo-config.json` with `marker`; include the **optional** product-level default strategy slot (per D3.1 §`/onboard` product-level default — `workflow.default_strategy` key, empty string by default, prompt at /onboard step 7 with a "skip" option). Evaluate `onboard.linear-projects` and `onboard.config-write` gates from D3.4.
- `.claude/skills/update-linear/SKILL.md` — evaluate the `update-linear.diff-applied` gate from D3.4.

**Pyramid shape:** `capability-cluster`-shaped — required: `integration`, `perceptual`. Optional: `unit`. Forbidden: `smoke`, `contract`, `invariance`.

**Failing-test seed (per-child, populated at /specify time — sketch):**

- `test_specify_skill_step3_uses_pyramid_catalog` — `[integration]` — asserts that invoking `/specify` step 3 (or its predicate-evaluator equivalent in `solo-verify`) with a `walking-skeleton` strategy produces a failing-test seed whose Pyramid shape line matches the catalog exactly; covers AC-6.
- `test_plan_skill_halts_hybrid_without_overrides` — `[integration]` — asserts `/plan` on a hybrid parent with one child lacking a `Strategy:` field halts with §hybrid-without-child-overrides; covers AC-7.
- `test_review_skill_subagent_stop_hook_fires` — `[integration]` — asserts the SubagentStop hook predicate evaluates the four-hat transcript and emits the correct top-level Stop / SubagentStop output shape; covers AC-8.
- `test_build_skill_rejects_tampered_pyramid` — `[integration]` — asserts `/build`'s pre-flight halts §pyramid-shape-violation on a seed file whose tag set differs from the sealed parent's pyramid_shape; covers AC-9.
- `test_verify_skill_dispatches_per_strategy` — `[integration]` — asserts each of the five strategies routes to the documented gate set; covers AC-11.
- `test_verify_skill_writes_children_gate_outcomes` — `[integration]` — asserts the sealed `/verify` manifest contains the documented `children_gate_outcomes[]` schema; covers AC-11.
- `test_retro_skill_reads_children_gate_outcomes` — `[integration]` — asserts `/retro` surfaces tag distribution and per-gate outcome counts from a sample `/verify` manifest; covers AC-12.
- `test_onboard_skill_creates_six_linear_projects` — `[integration]` — asserts `/onboard` on a fresh Linear team creates the six D1 projects + Status doc + writes `docs/.solo-config.json` with `marker`; covers AC-13.
- `test_specify_skill_perceptual_artifact` — `[perceptual]` — asserts the skill's frontmatter + decision-table rendered to `docs/specs/0001-v0.2-cascade-integration/perceptual/specify-skill-surface.md` is byte-stable across renders; covers AC-6.
- `test_verify_skill_perceptual_artifact` — `[perceptual]` — asserts the skill's per-strategy dispatch matrix rendered to `docs/specs/0001-v0.2-cascade-integration/perceptual/verify-skill-dispatch.md` is byte-stable; covers AC-11. (One `[perceptual]` artifact per skill is the v0.2 floor; the executing session may consolidate to fewer if budget is tight.)
- `test_pyramid_catalog_const_block_matches_d3_2` — `[unit]` — asserts the catalog const block in the `/specify` skill matches the JSON in D3.2 §Catalog summary verbatim; covers AC-6.

**Notes for the executing session:**

- The `four-hat-panel` agent layout could not be verified in the inventory (robots-blocked subdir listings). Child B's first action is to view `.claude/agents/` and confirm the agent's frontmatter shape before amending the SubagentStop hook predicate; if the layout differs from D2.2's assumption, raise a §strategy-annotation-unresolved-equivalent question and confirm with the founder before editing.
- The `update-linear` skill amendment is the lightest of the nine. Bundle it with `wrap` and `retro` into a single capability-cluster pass if Ralph budget is tight.

---

## Child 0001-C — `v0.2-hook-infrastructure`

**Strategy:** `walking-skeleton`.

**Rationale.** v0.1 has no hooks. v0.2's hook infrastructure is the first end-to-end wiring of `.claude/hooks/` + `.claude/settings.json` + event-to-predicate mapping. The vertical slice is: an event fires → settings.json routes to a script → the script reads JSON from stdin → the script evaluates a predicate → the script emits the right output shape per event type → Claude Code consumes it. This is a thin slice through every layer (event dispatch → file IO → predicate evaluation → IPC contract) — walking-skeleton shape per D3.1.

**Files in scope (full paths):**

- `.claude/hooks/preflight-provenance.sh` — bash script. Stdin: hook JSON payload. Reads the named upstream manifest from `.cascade/manifests/`, validates sha chain per D2.1 v2 §Caller-side verification step 5, exits 0 on chain-intact, exits 2 on chain-broken with `{"decision":"block","reason":"§provenance-chain-broken: …"}` to stdout per D2.2 §Stop / SubagentStop output schema quirk. Used by every cascade-stage skill's pre-flight.
- `.claude/hooks/pyramid-tampering.sh` — bash script. Fired by PreToolUse with matcher on the seed-file Write tool. Reads sealed parent manifest's `pyramid_shape`, reads the seed file under-write, compares tag set, exits 2 on mismatch with `§pyramid-shape-violation/shape-tampering`. Used by `/build`.
- `.claude/hooks/four-hat-objection-coverage.py` — Python script (structured-data manipulation across the four hat-agent transcripts). Stdin: SubagentStop JSON payload including `agent_transcript_path`. Reads each hat's transcript per D2.2 §Critical caveats #5, validates that every objection raised at hat-N has a recorded resolution in hat-(N+1)'s transcript, exits with the correct top-level Stop / SubagentStop shape (no `hookSpecificOutput` wrapper). This is the cascade's single agent-type hook per D3.4 §What is a gate. Fired only by `/review`.
- `.claude/hooks/stop-orchestrator.sh` — bash script implementing the single Stop-hook orchestrator pattern per D2.2 research-step resolution #3. Dispatches to per-skill completion predicates by reading `cascade:run-state.active_stages[]` to determine which skill is finishing.
- `.claude/hooks/session-start-state-restore.sh` — bash script. Fired on SessionStart with source `startup`, `resume`, or `compact`. For `resume` and `compact`, restores `cascade:run-state` from `.cascade/run-state.json` (repo-root canonical path per D2.1 v2.1; filesystem-first) with Linear-mirror read-fallback per D2.1 v2 §Cross-compact state persistence. Writes restored summary to `hookSpecificOutput.additionalContext` per D2.2.
- `.claude/hooks/precompact-safe-boundary.sh` — bash script. Fired by PreCompact (no matchers; script reads `trigger` from payload). Implements three-band threshold model per D2.2 §Compact mechanics §PreCompact: increments `compact_cycles` in `.cascade/session/<session_id>.json`; if ≥ 2 emits `§session-reset-required` and sets `reset_due: true`; else checks safe-boundary and emits `§compact-deferred-unsafe` (unsafe) or writes precompact snapshot to `.cascade/session/precompact-<id>-<ts>.json` and exits 0 (safe). Used by Group F auto-fire compact recovery. (Per Child C apply-time queue item #1.)
- `.claude/hooks/session-end-telemetry.sh` — bash script. Fired on SessionEnd. `async: true` per D2.2 critical caveat #4 (telemetry never gates progression). Appends a JSONL line to `.cascade/telemetry/sessions.jsonl` with session duration, stages touched, halts emitted.
- `.claude/hooks/pretool-write-denylist.sh` — bash script per AC-21. Fired on `PreToolUse` with matcher on Write/Edit/MultiEdit tools. Reads `.claude/agents/build-write-denylist.txt`; if the target path matches any pattern, exits 2 with `{"decision":"block","reason":"§cascade-control-write-blocked: ..."}` per D4.1.7. Per D2.2 §Stop / SubagentStop output schema.
- `.claude/settings.json` — wires the above to events. Single Stop hook (`.claude/hooks/stop-orchestrator.sh`). PreToolUse matchers: seed-file Write tool → pyramid-tampering.sh; Linear write tool → existing-from-v0.1 mirror-sha predicate (carried forward). SubagentStop matcher: `four-hat-*` agent type names → four-hat-objection-coverage.py. SessionStart, SessionEnd, PreCompact wired per D2.2 §Hook events table.

**Pyramid shape:** `walking-skeleton`-shaped — required: `smoke`, `perceptual`. Optional: `unit`, `integration`. Forbidden: `contract`, `invariance`.

**Failing-test seed (per-child, populated at /specify time — sketch):**

- `test_preflight_provenance_blocks_broken_chain` — `[smoke]` — asserts the script exits 2 when given a stub manifest with a deliberately-wrong parent sha; covers AC-14.
- `test_pyramid_tampering_blocks_mutated_seed` — `[smoke]` — asserts the script exits 2 when given a seed file whose tags don't match the sealed parent; covers AC-14.
- `test_four_hat_objection_coverage_emits_correct_shape` — `[smoke]` — asserts the script emits top-level `{"decision":"block","reason":"..."}` without `hookSpecificOutput` wrapper on objection-uncovered; covers AC-14.
- `test_stop_orchestrator_dispatches_correctly` — `[smoke]` — asserts the orchestrator routes to the right per-skill predicate based on `cascade:run-state` state; covers AC-14.
- `test_session_start_state_restore_writes_additional_context` — `[smoke]` — asserts the script writes a non-empty `hookSpecificOutput.additionalContext` field on resume / compact; covers AC-14.
- `test_settings_json_wires_all_events` — `[smoke]` — asserts `.claude/settings.json` parses and contains entries for PreToolUse, PostToolUse, SubagentStop, SessionStart, SessionEnd, PreCompact, Stop; covers AC-14.
- `test_hook_infrastructure_perceptual` — `[perceptual]` — asserts the byte-stable PNG at `docs/specs/0001-v0.2-cascade-integration/perceptual/0001-C-hooks-flow.png` (a rendered event-to-hook-to-skill diagram) regenerates from a `mermaid` source committed at `docs/specs/0001-v0.2-cascade-integration/perceptual/0001-C-hooks-flow.mmd`; covers AC-14.

**Notes for the executing session:**

- The hook scripts share a common JSON-stdin-handling preamble. Factor that into a `.claude/hooks/_lib.sh` (bash) and `.claude/hooks/_lib.py` (Python) so each script is roughly 20–40 lines of predicate logic instead of 60–80 lines of stdin / event-shape handling.
- The PreCompact hook is intentionally omitted from this child's failing-test seed because D2.2 §Critical caveats #2 documents that `--continue` / `--resume` replays mid-session hook outputs from transcript, and PreCompact's `custom_instructions` payload is read-only at session-start. Wiring it costs nothing once `session-start-state-restore.sh` is in place; testing it is high-effort for v0.2. Carry to v0.2.x test coverage if PreCompact behavior surfaces a defect.

---

## Child 0001-D — `v0.2-solo-verify-cli`

**Strategy:** `walking-skeleton` (with heavy `[unit]` coverage).

**Rationale.** `solo-verify` is the standalone-CLI parity surface for every gate's hook-side predicate, ensuring that the `max_turns` / `--resume` gap from D2.2 §Critical caveats #1 has a durable path. It is end-to-end-shaped — input is a `<stage> <ticket>` invocation, output is exit code 0–4 + a halt-card or pass message — and walking-skeleton fits per D3.1 (one vertical slice exercising arg-parsing → manifest read → predicate evaluation → halt-card render → exit). It is also algorithmically dense in the predicate-evaluator logic per the carry-forward thread, so `[unit]` is a heavy optional tag per D3.2 §walking-skeleton (unit is optional, encouraged where dense).

**Files in scope (full paths):**

- `tools/solo-verify` — Python 3.10+ stdlib single-file script with a `#!/usr/bin/env python3` shebang and `chmod +x`. Implements the full D3.4 CLI surface. Module-internal structure:
  - `_argparse_setup()` — defines the subcommand structure (`onboard`, `specify`, `review`, `plan`, `update-linear`, `build`, `wrap`, `verify`, `retro`) and the global flags (`--gate <name>`, `--list-gates [stage]`, `--explain <stage>.<gate-name>`).
  - `_read_manifest(ticket, stage)` — reads `.cascade/manifests/<ticket>-<stage>.json`; raises on absent / unparseable.
  - `_evaluate_gate(stage, gate_name, ticket)` — dispatches to per-gate predicate function.
  - `_predicate_<gate-name>(...)` — one function per of the 22 gates from D3.4 §Per-stage gate inventory. Each function returns `(passed: bool, halt_card: dict | None)`.
  - `_render_halt_card(halt: dict)` — emits the canonical halt-card shape from D3.4 §Multi-failure aggregation examples.
  - `_exit_code(result)` — maps result to 0/1/2/3/4 per D3.4 §Exit codes.
  - `_list_gates(stage: str | None)` / `_explain_gate(stage_dot_gate: str)` — read from an inline `GATES` const dict mirroring D3.4's tables.
- `tools/solo-verify-tests/` — unit-test suite using stdlib `unittest`. Roughly one test class per gate, exercising both pass and halt paths with synthetic manifests written into a tmpdir. Coverage target: every `_predicate_<gate-name>` function exercised on at least one pass case and one halt case.

**Pyramid shape:** `walking-skeleton`-shaped — required: `smoke`, `perceptual`. Optional: `unit`, `integration`. Forbidden: `contract`, `invariance`.

**Failing-test seed (per-child, populated at /specify time — sketch):**

- `test_solo_verify_list_gates_prints_22` — `[smoke]` — asserts `python3 tools/solo-verify --list-gates` exits 0 and prints at least 22 gate names; covers AC-15.
- `test_solo_verify_explain_returns_d3_4_content` — `[smoke]` — asserts `python3 tools/solo-verify --explain verify.perceptual-evidence` prints the predicate text and halt-card mapping documented in D3.4; covers AC-15.
- `test_solo_verify_exit_codes_per_d3_4` — `[smoke]` — asserts pass → 0, standard halt → 1, unknown stage → 2, provenance halt → 3, missing `.cascade/manifests/` → 4; covers AC-15.
- `test_solo_verify_verify_per_strategy_dispatch` — `[smoke]` — asserts `solo-verify verify M-N` with a synthetic milestone manifest containing children of each strategy routes correctly to the documented gate set; covers AC-15.
- `test_predicate_pyramid_shape_pass_path` — `[unit]` — synthetic manifest, walking-skeleton, required tags present, forbidden absent → predicate returns `(True, None)`; covers AC-15.
- `test_predicate_pyramid_shape_missing_required_tag` — `[unit]` — synthetic manifest, walking-skeleton, no `[perceptual]` entry → predicate returns `(False, {"code": "§pyramid-shape-violation/missing-required", ...})`; covers AC-15.
- `test_predicate_invariance_pass_set_regression` — `[unit]` — synthetic seal manifest, synthetic verify-time pass set with one fewer entry → predicate returns the regression halt-card per D3.3 §Refactor-spike invariance predicate; covers AC-15.
- `test_predicate_provenance_chain_break_detected` — `[unit]` — synthetic broken manifest chain → predicate emits §provenance-chain-broken, `_exit_code` returns 3; covers AC-15.
- `test_predicate_perceptual_byte_stability_passes_on_equal_bytes` — `[unit]` — two synthetic identical PNGs → predicate returns `(True, None)`; covers AC-15.
- `test_predicate_perceptual_byte_stability_fails_on_drift` — `[unit]` — two synthetic PNGs differing by one byte → predicate emits §perceptual-evidence-missing/byte-stability-failed; covers AC-15.
- `test_halt_card_render_matches_d3_4_canonical` — `[unit]` — render output diffed against a fixture file extracted verbatim from D3.4 §Multi-failure aggregation examples; covers AC-15.
- `test_solo_verify_cli_help_output_perceptual` — `[perceptual]` — asserts the byte-stable `.txt` capture at `docs/specs/0001-v0.2-cascade-integration/perceptual/solo-verify-help.txt` regenerates from `python3 tools/solo-verify --help 2>&1`; covers AC-15.

**Notes for the executing session:**

- Python 3.10+ is required for the standard-library-only constraint to hold (uses `match`/`case`, `dict | None` syntax). The script's first line after the shebang asserts the version with a clear error message.
- Use `argparse` (stdlib) for subcommands; do not pull `click` or `typer`.
- The `GATES` const dict can be machine-generated from D3.4's tables; do it once at script-author time and commit the static dict. D4.x may move this to a versioned `docs/.cascade/gates.json` per D3.4 §Documentation invocations.
- The unit-test suite uses stdlib `unittest`, not `pytest`. Run via `python3 -m unittest discover tools/solo-verify-tests/`. Adopters who don't run unit tests at all can skip; the suite is for the framework's own dogfood.

---

## Child 0001-E — `v0.2-docs-update`

**Strategy:** `walking-skeleton`.

**Rationale.** The framework's two outward-facing docs (`CLAUDE.md` and `README.md`) must reflect v0.2 truth. The lockstep update to `docs/templates/CLAUDE.md` (the version `/onboard` renders for forks) is part of the same end-to-end concern: a new fork reading `README.md` should see v0.2 quickstart language, and when `/onboard` runs it should render a v0.2-shaped `CLAUDE.md` into the fork. Vertical slice: edit source → render → adopter reads. Walking-skeleton.

**Files in scope (full paths):**

- `CLAUDE.md` (repo root, the framework's own session-instruction layer per the existing file's own §Notes block) — amendments per AC-16:
  - Drop the v0.1 sentence "no hooks in v0.1" from §Workflow.
  - Add §Cascade gates as a new subsection under §Workflow, pointing at `docs/templates/halt-messages.md` for halt-card structure and `python3 tools/solo-verify --list-gates` for the gate inventory.
  - Add §Strategy enum as a one-paragraph note under §Workflow naming the five strategies from D3.1 and referencing `/specify` step 1 for the proposal-and-confirm cycle.
  - Add §Hooks as a new subsection under §Workflow, referencing `.claude/settings.json` and the four hook script families (provenance, pyramid-tampering, four-hat objection-coverage, session lifecycle).
- `docs/templates/CLAUDE.md` (the version `/onboard` renders for forks) — lockstep with the above. Any v0.2-only sentence in the root CLAUDE.md that is also true for forks gets carried into the template. The framework's own §Workflow assertions about not-shipping-to-forks are template-specific and stay in the template's own variant block.
- `README.md` — amendments per AC-17:
  - Update §Status to read "v0.2 cascade primitives integrated; v0.2 self-application underway".
  - Add §What's new in v0.2 as a short bulleted section listing: gate composition (22 named gates × 8 stages), hook infrastructure (deterministic command hooks + the single agent-type SubagentStop check), `solo-verify` CLI for hook-parity / `max_turns` recovery, per-strategy pyramid shape declaration, perceptual-evidence and invariance predicates with per-strategy semantics, six-Linear-project product layer at `/onboard`. Each bullet links to the relevant Phase 3 design doc once those docs are published (until then, links are TODO comments).

**Pyramid shape:** `walking-skeleton`-shaped — required: `smoke`, `perceptual`. Optional: `unit`, `integration`. Forbidden: `contract`, `invariance`.

**Failing-test seed (per-child, populated at /specify time — sketch):**

- `test_root_claude_md_drops_no_hooks_sentence` — `[smoke]` — asserts `CLAUDE.md` does not contain the literal string "no hooks in v0.1"; covers AC-16.
- `test_root_claude_md_has_gates_subsection` — `[smoke]` — asserts `CLAUDE.md` contains the literal heading or subheading naming Cascade gates; covers AC-16.
- `test_template_claude_md_matches_root_for_shared_sections` — `[smoke]` — asserts the §Cascade gates / §Strategy enum / §Hooks sections in `docs/templates/CLAUDE.md` are textually equivalent to the corresponding sections in `CLAUDE.md` (modulo template-specific variant blocks); covers AC-16.
- `test_readme_status_block_reads_v0_2` — `[smoke]` — asserts `README.md` §Status block contains the substring "v0.2"; covers AC-17.
- `test_readme_has_whats_new_section` — `[smoke]` — asserts `README.md` contains the §What's new in v0.2 heading; covers AC-17.
- `test_docs_render_perceptual` — `[perceptual]` — asserts the byte-stable rendered HTML at `docs/specs/0001-v0.2-cascade-integration/perceptual/0001-E-docs-render.html` regenerates from a `pandoc CLAUDE.md README.md -o ...` pipeline; covers AC-16, AC-17. Per D3.3 walking-skeleton perceptual predicate.

**Notes for the executing session:**

- The template-vs-root CLAUDE.md split is the most error-prone in this child. Use a diff tool (e.g., `diff -u`) to confirm the shared sections match after each edit; the `test_template_claude_md_matches_root_for_shared_sections` smoke test enforces this at /build time.
- Cross-links to Phase 3 design docs in README's §What's new in v0.2 are TODO comments until those docs are public. If the founder publishes the Phase 3 docs as part of this milestone (e.g., to `docs/research/` or `docs/design/`), the TODOs resolve to real intra-repo links; otherwise they resolve in a v0.2.1 docs-link follow-up.

---

## Build order (recommended)

Children are partially independent. A sensible order for the executing session:

1. **0001-A** first — templates and config are the substrate every other child consumes (the spec template, the halt-messages.md, the `.solo-config.json` schema, the directory skeletons).
2. **0001-D** in parallel with 0001-A — `solo-verify` development can start as soon as D3.4's gate tables are in code; no dependency on 0001-A's templates beyond shape conventions.
3. **0001-C** after 0001-A — hooks consume the `.cascade/manifests/` directory and the halt-card structure landed in 0001-A.
4. **0001-B** after 0001-A and 0001-C — skill amendments reference the new template variants, the halt codes, and the hook event wiring.
5. **0001-E** last — docs reflect everything else; lockstep-updating CLAUDE.md before the underlying behavior exists creates "advertised but not shipped" drift.

Ralph budget per child (rough): 0001-A and 0001-E are short (~1–2 Ralph iterations each); 0001-C and 0001-D are medium (~3–5); 0001-B is the longest (~8–12 because nine skills × per-skill amendment surface).

---

## Open questions deferred to per-child `/specify`

Each child's `/specify` may surface additional Open Questions specific to its files. The parent's Open Questions (see `spec.md` §Open questions) are the inventory-level ones that span multiple children; per-child Open Questions are file-level.

Examples likely to surface:

- 0001-A: exact tag-comparison logic for `test_solo_config_template_has_invariance_block` — string substring match vs JSON deep-equality?
- 0001-B: should `update-linear` skill amendments be folded into `wrap`'s child block to avoid a one-line per-skill amendment? (Founder's call; current sketch keeps it separate for `solo-verify update-linear <ticket>` CLI parity.)
- 0001-C: PreCompact hook test coverage — surface in this child or carry to v0.2.x?
- 0001-D: `tools/solo-verify` execution path — bare script invocation `python3 tools/solo-verify` vs a thin `scripts/solo-verify` bash wrapper that activates a venv (if any)?
- 0001-E: should the Phase 3 design docs themselves be published as part of this milestone (under `docs/research/` or `docs/design/`)?
