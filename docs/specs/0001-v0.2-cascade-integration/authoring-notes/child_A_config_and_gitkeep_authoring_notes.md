# Child 0001-A continuation — `solo-config.*`, `capability-artifact-types.md`, `.gitignore`, `.gitkeep` files — authoring notes

**Authored:** 2026-05-19, paired with the deliverables in this session's output directory.
**Predecessor session:** "0001 integration spec Child A continuation — `spec.md.template` + `halt-messages.md` authoring" (see `child_A_spec_template_and_halts_authoring_notes.md`).
**Parent spec:** `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-3, AC-4, AC-5.
**Binding-source map:** `decomposition.md` Child 0001-A files-in-scope (the canonical Child A scope); D3.3 §Capability-cluster perceptual predicate (table for `capability-artifact-types.md`); D3.3 §Refactor-spike invariance predicate (semantics for `invariance.pass_set_capture_command`); D3.1 §`/onboard` product-level default (semantics for `workflow.default_strategy`); D2.1 v2.1 §`cascade:run-state` schema (path conventions).

After this session, **Child A's design pass is complete**. The executing Claude Code session against `OndraMasek/Solo-Vibing` can run with all three Child A design sessions' deliverables (chat-end-card.md from session N-2; `spec.md.template` + `halt-messages-append.md` from session N-1; this session's five-artifact set) applied as a single coherent patch.

## Deliverables (this session)

| Deliverable | Form | Target framework path | Source |
|---|---|---|---|
| `solo-config-additions.json` | JSON merge-patch (two new top-level keys) | applied to both `docs/templates/.solo-config.json.template` AND `docs/.solo-config.json` | decomposition.md Child 0001-A; D3.3; D3.1 |
| `solo-config.example.json` | full new file | `docs/.solo-config.example.json` | decomposition.md Child 0001-A; D3.3 §Refactor-spike invariance predicate |
| `capability-artifact-types.md` | full new file | `docs/templates/capability-artifact-types.md` | D3.3 §Capability-cluster perceptual predicate |
| `gitignore-amendment.patch` | append-block diff | applied to existing v0.1 `.gitignore` | decomposition.md Child 0001-A; D3.3; D2.3 v1.3 |
| `framework-paths/.cascade/manifests/.gitkeep` | committed-empty (1-line `#`-comment) | `.cascade/manifests/.gitkeep` | decomposition.md Child 0001-A |
| `framework-paths/.cascade/halt/.gitkeep` | committed-empty | `.cascade/halt/.gitkeep` | decomposition.md Child 0001-A |
| `framework-paths/.solo-locks/.gitkeep` | committed-empty | `.solo-locks/.gitkeep` *(path divergence — see §Surfaced items #2)* | decomposition.md Child 0001-A |
| `framework-paths/.ralph/.gitkeep` | committed-empty | `.ralph/.gitkeep` | decomposition.md Child 0001-A |
| `framework-paths/docs/product/.gitkeep` | committed-empty | `docs/product/.gitkeep` | decomposition.md Child 0001-A; D1 |

## Decisions made (non-surfacing)

### 1. JSON-comments convention: `_comment_*` sibling keys

The handoff named two candidates: sibling `_comment_*` keys OR `// …` annotation lines stripped by `/onboard`'s renderer. The v0.1 convention is not visible in this Claude.ai project's KB (the framework's actual `docs/templates/.solo-config.json.template` lives only in `OndraMasek/Solo-Vibing`).

**Chosen:** `_comment_*` sibling keys.

**Rationale:**
- Pure JSON. Parses with every standard library (`json.load`, `JSON.parse`, `serde_json`) without preprocessing. The framework reads its own config via `json.loads` in v0.1 (per the `marker` knob's documented use); a JSONC pre-stripper is an extra dependency the framework explicitly does not carry.
- Skill consumers (`/specify`, `/plan`, `/verify`) iterate over config keys filtering by prefix; `key.startswith('_')` is a trivial guard.
- The convention scales: every block can carry its own `_comment_<blockname>` neighbor without escaping or syntax fragility. The example file in this session uses both top-level `_format`/`_caveat` keys and per-block `_<runner>_comment` keys; both shapes parse cleanly.
- v0.1's actual convention may differ. If v0.1 uses `// …` annotation lines + a renderer-side stripper, the executing Claude Code session has two paths: (a) convert the additions to `// …` style at apply time to preserve v0.1 convention consistency, or (b) merge the additions as-is and accept dual conventions on the same file. **Recommendation:** path (a) if v0.1 carries a stripper; path (b) if v0.1 already uses sibling-key comments. Verified at apply time.

### 2. Example-file shape: cargo-cult-ready, single-object

`docs/.solo-config.example.json` is shaped as a single JSON object containing:
- `_format` — top-level explainer (what this file is for).
- `_caveat` — top-level warning about the example commands' production-readiness.
- `_examples_per_runner` — nested object with one key per runner (pytest, vitest, jest, go_test, cargo_test) and a `_<runner>_comment` neighbor for each.
- `_target_config_shape` — explainer for the `invariance` + `workflow` blocks that follow.
- `invariance` + `workflow` — the actual config shape, populated with one concrete example (pytest with `--json-report` — the D3.3 runner-agnostic-mechanism version, not the decomposition.md simpler version; see §Surfaced items #1 for rationale).

The `invariance.pass_set_capture_command` value at the bottom is intentionally the **D3.3 §Runner-agnostic capture mechanism** version (`pytest --json-report --json-report-file=/dev/stdout --quiet 2>/dev/null | jq -r '.tests[] | select(.outcome == "passed") | .nodeid'`), not the decomposition.md simpler version (`pytest -q --tb=no | grep PASSED | sort`). The simpler versions live in `_examples_per_runner` as decomposition.md specifies; the populated `invariance.pass_set_capture_command` shows the production-quality target. This is a stylistic deviation surfaced in §Surfaced items #1.

### 3. `capability-artifact-types.md` columns: four, not three

D3.3 §Capability-cluster perceptual predicate's table has three columns (Capability artifact | Extension | Path example). The handoff's task-instructions section called for "artifact-type | extension | example | inspection-predicate" — four columns, last one wrong.

**Chosen:** four columns — `artifact_type` (manifest value) | Description | Extension | Path example.

**Rationale:**
- The file's job is to be read by `/specify` skill step 3 to resolve the `artifact_type` field that gets written to the manifest. The manifest field's value is lowercase-hyphenated (`rendered-document`, `scheduled-event`, etc.), distinct from the human-readable description.
- D3.3 §Manifest representation specifies the lowercase-hyphenated values explicitly. Surfacing them in their own column makes the file maximally useful to the consumer.
- The handoff's "inspection-predicate" column was a misremember (no such column in D3.3); dropped without further comment.

### 4. `workflow.default_strategy` empty-default rationale

Per the parent spec at `spec.md` Open Question 4 and D3.1 §`/onboard` product-level default: the slot ships in v0.2 with an empty-string default ("no default"). Behavioral wiring is deferred to Child 0001-B (`/onboard` step 7 elicits and writes; `/specify` step 1 reads as the proposal seed). The empty slot harms nothing in the v0.2 interim — `/specify` step 1's fallback (first-principles proposal) is unchanged.

This is documented in-line in both `solo-config-additions.json` (`_comment_workflow` key) and `solo-config.example.json` (`workflow._default_strategy_comment` key). The executing Claude Code session does not need to wire any behavior; just landing the keys completes AC-3's `workflow.default_strategy` row.

### 5. `.gitignore` v0.1 reconciliation pattern

Same pattern as the predecessor session: the executing Claude Code session reads v0.1 `.gitignore` first, then appends only the patterns from `gitignore-amendment.patch` that are not already present. None of the three patterns in the patch is expected to be in v0.1 (invariance, atomicity, lock-sentinels were all Phase 3 design and didn't exist in v0.1) but the deduplication guard is cheap.

Three patterns in `gitignore-amendment.patch`:
- `docs/specs/*/invariance/pass-set-at-verify.txt` — required per AC-5.
- `.cascade/handoff/*.tmp` — atomicity-write half-files per D2.3 v1.3 §Group-exit mechanics atomicity.
- `.solo-locks/*.lock` — per-resource lock sentinels per D2.1 v2 §Per-resource lock semantics. Path-divergence surfaced in §Surfaced items #2.

## Surfaced items for founder ratification

Three items surfaced; **none blocks the executing Claude Code session for Child A** but #2 in particular benefits from resolution before that session runs to avoid a same-day correction.

### 1. `solo-config.example.json` — D3.3 vs decomposition.md per-runner commands

**Discrepancy:** decomposition.md's per-runner examples are simpler shell-pipe constructions; D3.3 §Runner-agnostic capture mechanism's are more complex JSON-output + `jq` constructions. Three of decomposition.md's five commands have correctness issues:

| Runner | decomposition.md command | Issue |
|---|---|---|
| pytest | `pytest -q --tb=no \| grep PASSED \| sort` | `-q` mode does not emit per-test PASSED markers; output is dots/F/E only. The command produces empty output on a clean run. |
| jest | `jest --listTests --testPathPattern=passed \| sort` | `--listTests` lists test FILES, not test names; `--testPathPattern=passed` filters by path-substring "passed", not by outcome. The command lists files that happen to have "passed" in their name. |
| cargo_test | `cargo test --quiet 2>&1 \| grep 'test result' \| sort` | Produces summary lines ("test result: ok. X passed; Y failed"), not per-test IDs. |

The vitest and go_test commands are correct.

**Resolution this session (provisional):** rendered decomposition.md's commands verbatim in `_examples_per_runner` per the handoff's explicit instruction ("Per-runner examples per `decomposition.md`"); rendered D3.3's pytest variant as the populated `invariance.pass_set_capture_command` value at the file's bottom so the file demonstrates a working command alongside the illustrative ones; added a `_caveat` field surfacing the divergence and pointing at D3.3 §Runner-agnostic capture mechanism for production-quality variants.

**Recommendation for founder ratification:** swap the three buggy `_examples_per_runner` entries (pytest, jest, cargo_test) for D3.3's working versions before sealing. This is a 5-minute amendment to `decomposition.md` and `solo-config.example.json`. Vitest and go_test stay as-is.

**If founder ratifies the swap:** the executing Claude Code session reads `solo-config.example.json` from this project, swaps the three commands to D3.3's versions, then applies. If founder ratifies "leave decomposition.md's versions" the file ships as-rendered.

### 2. `.solo-locks/` (root) vs `docs/.solo-locks/` — path discrepancy

**Discrepancy:** two binding sources disagree on the canonical lock-sentinel directory:

- **decomposition.md** Child 0001-A files-in-scope row: `.solo-locks/.gitkeep` (root).
- **`spec.md` AC-5:** `.solo-locks/.gitkeep` (root). Aligns with decomposition.md.
- **`repo-state-summary.md` Part 2 delta-computation row:** `.solo-locks/.gitkeep` (root). Aligns with decomposition.md.
- **D2.1 v2.1** §Why option (c), final paragraph: *"The `.solo-config.json` (workflow knobs) and `docs/.solo-locks/` (sentinel files) keep their existing locations — those serve different concerns and have established v0.1 paths."*
- **D2.1 v2** §Per-resource lock semantics — example data: `"sentinel_path": "docs/.solo-locks/Status.md.lock"`.

D2.1 v2.1 is the most recent binding-spec amendment; it explicitly asserts `docs/.solo-locks/` is the canonical path. But three downstream documents (decomposition.md, spec.md, repo-state-summary.md) commit to `.solo-locks/` at the root.

**Best read of the conflict:** D2.1 v2.1 was authored after decomposition.md / spec.md; the v2.1 amendment recommends keeping `docs/.solo-locks/` for the existing-v0.1-path reason, but v0.1 does not actually carry a `docs/.solo-locks/` directory (per `repo-state-summary.md` Part 1's v0.1 inventory). The "existing path" argument is forward-looking, not historical.

There are two coherent resolutions:

| Option | Path | Update needed |
|---|---|---|
| (a) Accept D2.1 v2.1's recommendation | `docs/.solo-locks/.gitkeep` | Amend `decomposition.md`, `spec.md`, `repo-state-summary.md` to match; update sentinel-path samples in D2.1 v2 to `docs/.solo-locks/`. |
| (b) Override D2.1 v2.1 in favor of the .cascade-namespace-consistency argument | `.solo-locks/.gitkeep` (root) — current draft | Amend D2.1 v2.1's paragraph + D2.1 v2's sentinel-path samples to `.solo-locks/`. |

**Resolution this session (provisional):** path (b) — `.solo-locks/.gitkeep` at the root — per decomposition.md, since decomposition.md is the binding spec for *this* child's files-in-scope. The framework's other root-level cascade namespaces (`.cascade/`, `.ralph/`) put the namespace consistency argument on (b)'s side.

**Recommendation for founder ratification:** path (b) — accept the .gitkeep at root, amend D2.1 v2.1 and D2.1 v2 in a follow-up amendment-only pass (the same pattern that produced D2.1 v2.1 itself). The .gitignore line `.solo-locks/*.lock` in `gitignore-amendment.patch` aligns with (b); if (a) is chosen, change to `docs/.solo-locks/*.lock` and move the `.gitkeep` file in the apply-pass.

### 3. Solo-config block placement in v0.1 file

**Open detail:** the JSON merge-patch in `solo-config-additions.json` shows the two new top-level blocks (`invariance`, `workflow`) but doesn't position them relative to v0.1's existing keys (`marker`, `cascade-only`/`interactive`/`yolo`).

**Recommendation:** the executing Claude Code session places the new blocks after the v0.1 `cascade-*` knobs block and before any v0.1 closing-brace footer. JSON key-order is not semantically significant for parsers; this is purely human-readability. No founder ratification needed; calling it out for the apply-pass author.

## Failing-test seeds

Six tests, copied verbatim from `decomposition.md` Child 0001-A failing-test seed. These cover AC-3 (config), AC-4 (capability-artifact-types), and AC-5 (gitignore + gitkeep) collectively; together with the prior session's tests for AC-1/AC-2, Child A's complete `[smoke]`/`[unit]` coverage is established.

- `test_solo_config_template_has_invariance_block` — `[smoke]` — asserts `docs/templates/.solo-config.json.template` parses as JSON and contains `invariance.pass_set_capture_command` as a string key. Covers AC-3 (first half).
- `test_solo_config_template_has_workflow_default_strategy` — `[smoke]` — asserts the file contains `workflow.default_strategy` as a string key. Covers AC-3 (second half — the D3.1 `/onboard` product-level default slot).
- `test_solo_config_example_parses_with_runner_keys` — `[unit]` — asserts `docs/.solo-config.example.json` parses as JSON AND contains substring matches for at least five runner names (`pytest`, `vitest`, `jest`, `go`, `cargo`). Substring match tolerates the `go_test` / `cargo_test` naming used in `_examples_per_runner`. Covers AC-3 (example-file population).
- `test_capability_artifact_types_md_lists_seven_rows` — `[smoke]` — asserts `docs/templates/capability-artifact-types.md` markdown table has at least seven data rows (rows with three `|` separators, excluding header and `|---|` separator row). Covers AC-4.
- `test_gitignore_excludes_verify_pass_set` — `[smoke]` — asserts `.gitignore` contains the literal line `docs/specs/*/invariance/pass-set-at-verify.txt`. Covers AC-5 (gitignore half).
- `test_committed_empty_directories_exist` — `[smoke]` — asserts five paths exist: `.cascade/manifests/.gitkeep`, `.cascade/halt/.gitkeep`, `.solo-locks/.gitkeep` (or `docs/.solo-locks/.gitkeep` per §Surfaced items #2 resolution), `.ralph/.gitkeep`, `docs/product/.gitkeep`. Covers AC-5 (gitkeep half).

A seventh `[perceptual]` test seed sketched in `decomposition.md` covers AC-1 through AC-5 collectively as the end-to-end scaffold demonstration:

- `test_v0_2_scaffold_perceptual` — `[perceptual]` — asserts the byte-stable PNG at `docs/specs/0001-v0.2-cascade-integration/perceptual/0001-A-scaffold-tree.png` regenerates from a `tree -a .cascade docs/templates docs/.solo-config* | rsvg-convert` (or equivalent — founder picks the renderer at /build time). Per D3.3 walking-skeleton perceptual predicate.

This belongs to Child A but is not authored in this design session — it's a `/build`-time renderer choice. Surfaced for the executing Claude Code session to wire (the renderer command and the byte-stable PNG path are the only details needed).

## Forward references and lockstep amendments queued

### Same-session amendment to `spec.md` AC-2 still queued from predecessor

Per `child_A_continuation_handoff.md`'s "Follow-on action item for the parent spec edit pass": **`spec.md` AC-2 currently reads "the eleven new Phase 3 halts" — needs amendment to "the fourteen new halts, including the three D3.1 halts that enforce the §Decomposition strategy section's surface."** Predecessor session's three D3.1 halts (§strategy-missing, §strategy-conflict-unresolved, §hybrid-without-child-overrides) were folded into `halt-messages-append.md` (halts 12–14) per option (a) ratification.

This amendment is a parent-spec edit, not a Child A authoring item. **Recommendation:** absorb into the small one-line `spec.md` edit pass before the executing Claude Code session runs — the same one that handles §Surfaced items #1 and #2 of this session if ratified.

### Subsequent design sessions

- **Child 0001-B** — `.claude/skills/*/SKILL.md` amendments. Capability-cluster strategy per decomposition.md. **Count question:** decomposition.md Child 0001-B's files-in-scope row names six skills explicitly (`specify`, `plan`, `review`, `build`, `wrap`, `verify`) plus `retro`, `onboard`, `update-linear` referenced elsewhere — so nine total. `/discovery` and `/constitution` are not in the gate-firing inventory (per `repo-state-summary.md` Part 3 item 5) and likely not in Child 0001-B scope — but verify when starting B. Likely 2–3 design sessions split per-skill or per-skill-cluster.
- **Child 0001-C** — `.claude/hooks/` infrastructure + `.claude/settings.json` wiring. Walking-skeleton strategy. One session likely sufficient. Includes Stop-hook output shape (F-Eng-4 / F-Int-2 disposition) and chat-Claude atomicity-write contract (F-Eng-5 if it surfaced concretely in Child B).
- **Child 0001-D** — `tools/solo-verify` Python stdlib script implementing D3.4's CLI surface. Walking-skeleton with heavy `[unit]` coverage. One to two sessions. Includes per-stage `--reconcile` flag-set disposition (F-Rev-2 carry-forward).
- **Child 0001-E** — `CLAUDE.md` and `README.md` amendments + lockstep update to `docs/templates/CLAUDE.md`. Walking-skeleton (rendered markdown is the perceptual artifact). One session.

Total Phase-2-design sessions remaining: ~6–8 after this one.

## Cross-references

- **decomposition.md** Child 0001-A files-in-scope — canonical scope source for this session; the row that names these five artifacts and their exact paths + content sketches.
- **D3.3** §Capability-cluster perceptual predicate — binding spec for the seven-row table.
- **D3.3** §Refactor-spike invariance predicate — binding spec for `invariance.pass_set_capture_command` semantics; §Runner-agnostic capture mechanism for the production-quality per-runner commands.
- **D3.1** §`/onboard` product-level default — binding spec for `workflow.default_strategy`.
- **D2.1 v2.1** — path conventions for `.cascade/` and `docs/.solo-locks/`. §Surfaced items #2 documents the path-divergence with this session's deliverables.
- **D2.1 v2** §Per-resource lock semantics — lock-sentinel atomic-create protocol; informs `.gitignore` lock-sentinel pattern.
- **D2.3 v1.3** §Group-exit mechanics atomicity — atomicity-write `.tmp` protocol; informs `.gitignore` `.cascade/handoff/*.tmp` pattern.
- **`spec.md`** AC-3, AC-4, AC-5 — the acceptance criteria these five artifacts collectively satisfy.
- **`spec.md`** Open Question 4 — `workflow.default_strategy` v0.2-vs-v0.2.x recommendation that this session's empty-default ships.
- **`repo-state-summary.md`** Part 1 — v0.1 inventory; confirms `.solo-config.json.template` and `.gitignore` exist in-place, the example file and capability-artifact-types.md and the five `.gitkeep` files are new.
- **`child_A_spec_template_and_halts_authoring_notes.md`** — predecessor session's notes; the v0.1 byte-for-byte reconciliation pattern documented there applies here too.
- **`child_A_continuation_handoff.md`** — predecessor session's handoff (this session's task spec).
