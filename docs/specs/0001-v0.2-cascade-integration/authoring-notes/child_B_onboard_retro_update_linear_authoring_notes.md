# Child 0001-B continuation 2 — `/onboard` + `/retro` + `/update-linear` SKILL.md amendments — authoring notes

**Authored:** 2026-05-19, end of "0001 integration spec Child 0001-B continuation 2 — setup + terminal + mirror cluster design session."

**Session deliverables (four files):**

  1. `onboard-SKILL-amendments.md` — two `onboard.*` gates per AC-13; nine-step `/onboard` sequence (v1.3's eight steps plus a new step 7 for `workflow.default_strategy` elicitation); F-Int-5 dispositioned descriptively; manifest schema extended per D2.1 v2 + D3.1.
  2. `retro-SKILL-amendments.md` — single `retro.doc-sealed` gate per AC-12; four rendered sections (tag distribution, per-gate outcome counts, session-discipline retrospective, next-milestone backlog reflections); reads `children_gate_outcomes[]` from `/verify`'s manifest per D3.4 §Manifest schema additions; halt-case rendering reads from `.cascade/halt/<milestone>-*-verify.txt` per v0.2 schema limitation.
  3. `update-linear-SKILL-amendments.md` — single `update-linear.diff-applied` gate per AC-13; naming-only standardization; D2.1 v2 carry-forward behavior; same pattern shape as `/wrap`'s naming-only amendment.
  4. This notes doc.

Three amendment files use the patch-ready amendment pattern Child 0001-B continuation 0 established (substitute-by-purpose-not-by-line, v0.1 reconciliation deferred to executing Claude Code session).

**After this session: Child 0001-B's design phase is complete.** All 9 of Child 0001-B's skills are designed across three sessions:

- **Continuation 0:** `/specify`, `/plan` (Child 0001-B continuation 0).
- **Continuation 1:** `/review`, `/build`, `/wrap`, `/verify` (Child 0001-B continuation 1).
- **Continuation 2 (this session):** `/onboard`, `/retro`, `/update-linear` (Child 0001-B continuation 2).

Remaining Phase-2 design sessions: Child 0001-C (hooks + settings.json), Child 0001-D (solo-verify CLI), Child 0001-E (CLAUDE.md + README). Estimated 4 sessions to complete Phase 2 design.

---

## Authoring decisions

### `/onboard` — `workflow.default_strategy` wiring closure

The handoff named this session as "the session that closes the `workflow.default_strategy` loop." The prior `/specify` step 1 amendment (Child 0001-B continuation 0) reads `docs/.solo-config.json`'s `workflow.default_strategy` and tolerates an empty string. This amendment ships the write side: step 7 elicits a strategy from the founder (five canonical options + skip), writes the selected value to `docs/.solo-config.json` (or empty string on skip).

After this session, the slot is fully wired end-to-end without further skill amendments:

- **Write side (this amendment):** `/onboard` step 7 elicits and writes; the empty string is a valid value the founder explicitly chooses ("skip").
- **Read side (continuation 0):** `/specify` step 1 reads-and-tolerates-empty; falls through to the first-principles proposal flow if empty; uses the slot value as the proposal seed otherwise.
- **Founder UX:** founder confirms at `/specify` step 5 regardless of where the proposal came from. The `workflow.default_strategy` slot is advisory, not binding — `/specify` proposes; the founder confirms.

Per parent spec Open Question 4: "the `workflow.default_strategy` slot ships in v0.2 but behavioral wiring is deferred." That deferral is now resolved. v0.2's seal of this skill closes Open Question 4.

### `/onboard` — step-7 insertion vs v1.3's eight-step sequence

D2.3 v1.3 §`/onboard` integration point committed an eight-step sequence (step 7 = Project Instructions paste; step 8 = chat-end card render). This amendment inserts a new step 7 — the `workflow.default_strategy` elicitation — between v1.3's step 6 (Initialise Status doc) and v1.3's step 7 (Project Instructions render), pushing the latter two to steps 8 and 9. The resulting sequence is nine steps.

**Rationale for placement between steps 6 and 7:**

- Steps 1–6 build the Linear product layer and the Status doc. The `workflow.default_strategy` write to `docs/.solo-config.json` is a config-write, sibling to step 1's `linear.project_naming` decision. Placing them adjacent batches the config-side work.
- The Project Instructions paste (step 8 in this amendment) is only meaningful once `docs/.solo-config.json` is in its final v0.2 shape — the founder pastes the block once and doesn't re-paste later. Step 7's write must complete before step 8.
- The chat-end card render (step 9) is the Group A exit; it must come last.

The insertion produces a numeric drift between v1.3's eight-step sequence and this amendment's nine-step sequence. D2.3 v1.3 §`/onboard` integration point should be amended at apply time to reflect the nine-step sequence. **Surfaced item in §Surfaced items #1.**

### `/onboard` — F-Int-5 disposition (D1's "step 7" reference)

D2.3 v1.2 four-hat review F-Int-5 flagged: D1's `/onboard` step 3 says "Seed Product with founder's north-star (interactive flow; reuse existing /onboard step 7)." That "step 7" referred to v0.1's step 7 (the north-star seeding subroutine). v1.2 inserted a NEW step 7 (Project Instructions paste), creating a numeric collision.

This session's amendment to `/onboard` retires the numeric reference: D1's step 3 should read "reuse existing v0.1 north-star seeding subroutine" — descriptive, not numeric. The amendment lands in D1 at apply time, not in this skill (D1 is a design doc, not a SKILL.md). The TRIGGER is this session because the v0.2 `/onboard` sequence with the new step 7 inserted produces a yet-further numeric collision (now step 7 is `workflow.default_strategy` elicit; v1.3's "step 7" is renumbered to 8; v0.1's "step 7" is now step 3 conceptually).

The skill amendment itself uses descriptive language consistently — "reuse the v0.1 north-star seeding subroutine" — to insulate the SKILL.md from future step-number drift. **Surfaced item in §Surfaced items #2** for the D1 apply-time edit.

### `/onboard` — F-Usr-3 disposition (Project Instructions step 5 acknowledgment)

The handoff said: "If the `/onboard` step amendments include rendering the Project Instructions block, F-Usr-3's resolution lives in this skill." The amendment does include a step 8 that renders the Project Instructions paste-block — but the BLOCK CONTENT is owned by D2.3 v1.3 §Project Instructions block, not by the `/onboard` SKILL.md. The skill reads the v1.3 template literally and renders it; it does not author the content.

F-Usr-3's concern is the step 5 acknowledgment text inside the Project Instructions block ("emit a short 'Resuming cascade at <next-stage>' acknowledgment naming Marker, Product, Parent feature, Active ticket, Active milestone"). That text is in D2.3 v1.3, not in this skill.

**Disposition: F-Usr-3 remains queued for v0.2.x.** The amendment landing in this skill would either:

- (a) Have the skill rewrite the block content before rendering — which violates the "block is owned by D2.3" contract and creates a maintenance fork.
- (b) Amend D2.3 v1.3 §Project Instructions block directly — which is a design-doc amendment, not a SKILL.md amendment, and out of scope for this session per `decomposition.md` Child 0001-B's row.

The cleanest path is (b), scheduled as an amendment to D2.3 v1.3 in v0.2.x. F-Usr-3 stays in the v0.2.x lower-priority amendment queue. The skill's step 8 renders D2.3 v1.3's text as authored; when v0.2.x amends the text, the skill picks up the change automatically (since it reads the template, not a copy).

Same disposition as the prior `child_A_chat_end_card_authoring_notes.md` §F-Usr-3 carry-forward and the `child_A_spec_template_and_halts_authoring_notes.md` §F-Usr-3 disposition: F-Usr-3 lives in D2.3 v1.3's Project Instructions block content, not in any SKILL.md's render mechanics.

### `/onboard` — Gate 2 widened predicate set vs D3.4's row

D3.4 §`/onboard` row's `onboard.config-write` predicate set names three items: "`docs/.solo-config.json` written; parses; contains `marker`." The amendment widens to eight predicates:

1. File exists at path.
2. Parses as JSON.
3. Contains `marker`.
4. `marker` matches elicited value.
5. `linear.project_naming` matches step 1 decision.
6. `workflow.default_strategy` slot structurally present (key exists).
7. `workflow.default_strategy` value either empty or in canonical enum.
8. `invariance` top-level key present (Child A ships it).

Rationale for widening: D3.4's row was authored before Child A landed the `invariance` slot and before Child 0001-B continuation 0's `/specify` step 1 amendment made `workflow.default_strategy` load-bearing. The widened predicate set catches structural issues at `/onboard` time rather than letting them surface as `KeyError` or `§invariance-config-missing` at downstream stages. The widening is consistent with D3.4's design philosophy ("gates compose predicates; D3.4 specifies which predicates compose into which gates; widening a gate's predicate set within a single stage is a v0.2 patch decision").

**Surfaced item in §Surfaced items #3.** D3.4 §`/onboard` row should be amended at apply time to enumerate the eight predicates explicitly for `solo-verify --explain onboard.config-write` parity.

### `/retro` — informational stance preserved

D3.4 §`/retro` row: "No hard gates. `/retro` is informational and produces findings, not predicate evaluations." The single `retro.doc-sealed` gate at-write is structural (does the seal artifact exist?), not judgmental (is the content correct?). The amendment honors this: Sections 1–4 render content; Gate 1 confirms the rendered content sealed properly; nothing evaluates whether the content is correct.

This is intentional. `/retro` is the founder's reflection surface; the cascade's role is to surface the data the founder needs (gate outcomes, telemetry) and capture the founder's authored content (Section 4). Judging "did the founder learn the right lesson?" is out of scope.

### `/retro` — Section 2 halt-case rendering reads from `.cascade/halt/`, not `children_gate_outcomes[]`

Per D3.4 §Manifest schema additions: "halted children produce no manifest entry; failures live in `.cascade/halt/<child>-verify.txt`." v0.2's `/verify` manifest's `children_gate_outcomes[]` contains only passed children. So to surface halt cases at `/retro` time (per the failing-test seed `test_retro_skill_surfaces_per_gate_outcomes`'s halt-case assertion), the amendment specifies that Section 2 ALSO walks `.cascade/halt/<milestone>-*-verify.txt` files for per-child halt artifacts.

This is a v0.2 schema limitation, not a v0.2 design choice. v0.2.x should extend `children_gate_outcomes[]` to carry halted entries directly (with `status: "halted"`, the `halt_code`, the `halt_diagnostic`), eliminating the dual-source read. The amendment's rendering logic already handles both cases (the "halted" branch in the bucketing loop never fires from manifest data in v0.2 but is structurally ready for v0.2.x).

**Surfaced item in §Surfaced items #4.** D3.4 §Manifest schema additions should be amended in v0.2.x to allow halted entries on `children_gate_outcomes[]`.

### `/retro` — Section 3 telemetry-completeness banner

Per D2.2 §Critical caveat #4: telemetry writes are async. Sessions ending in a hard halt or a crashed Claude Code process may not flush their telemetry before `/retro` reads. The amendment specifies a §Failure modes "telemetry incomplete" rendering: a banner notes that N sessions enumerated; expected M per `cascade:run-state.group_completion_count[]`; numbers are lower bounds.

This is the right disposition for informational `/retro` — partial data beats no data. v0.2.x measurement M-3 (per-group time/token) per D2.3 v1.2 §Deferred measurement may move some session-end work synchronous to reduce the incompleteness rate; v0.2 ships with async + banner.

### `/update-linear` — naming-only amendment shape

Same pattern as `/wrap`'s amendment from Child 0001-B continuation 1: D3.4's `update-linear.diff-applied` is the v0.1 predicate under a canonical name. The amendment renames; the executing Claude Code session substitutes the identifier string only. No new code paths, no new halt codes.

The two-predicate structure (Predicate 1 = applied-diff match; Predicate 2 = Linear-sync sanity per the v0.1 backoff) is the v0.1 contract. The amendment makes the predicate set explicit in pseudocode for `solo-verify --explain update-linear.diff-applied` parity but doesn't change behavior.

### `/update-linear` — v0.1 backoff constant ownership

The amendment references `v0.1-specified backoff window` without naming a number. The constant is in v0.1's `/update-linear` SKILL.md (likely the existing `LINEAR_SYNC_BACKOFF_MS` or equivalent — v0.1 owns the actual value). The executing Claude Code session preserves whatever v0.1 carries.

**Surfaced item in §Surfaced items #5** for v0.1-state verification: if v0.1's `/update-linear` does NOT explicitly carry a backoff constant (e.g., if v0.1 just retries without an explicit window), the executing session adds one. The amendment specifies the structural shape but defers the value to v0.1.

---

## Surfaced items for the founder

Numbered list of items needing explicit confirmation before this session's deliverables are sealed:

  1. **D2.3 v1.3 §`/onboard` integration point should be amended at apply time** to reflect the nine-step sequence (was eight). The new step 7 is the `workflow.default_strategy` elicitation; v1.3's step 7 (Project Instructions render) becomes step 8; v1.3's step 8 (chat-end card render) becomes step 9. One-paragraph edit in D2.3 v1.3 §`/onboard` integration point. **Recommendation:** absorb into the small amendment-pass queued for before the Child A executing Claude Code session runs.

  2. **D1 §`/onboard` changes step 3** should be amended at apply time to use descriptive language ("reuse existing v0.1 north-star seeding subroutine") rather than numeric ("reuse existing /onboard step 7"). F-Int-5's disposition. One-line edit in D1. **Recommendation:** absorb into the same amendment-pass as item #1.

  3. **D3.4 §`/onboard` row should be amended at apply time** to enumerate the eight predicates `onboard.config-write` evaluates per this session's widened predicate set. The current row names three predicates ("`docs/.solo-config.json` written; parses; contains `marker`"); the amendment widens to eight (add: marker matches elicited; `linear.project_naming` consistent; `workflow.default_strategy` slot structurally present; `workflow.default_strategy` value valid; `invariance` slot present). Two-line edit in D3.4. **Recommendation:** absorb into the amendment-pass.

  4. **D3.4 §Manifest schema additions should be amended in v0.2.x** to allow halted entries on `children_gate_outcomes[]` (carrying `status: "halted"`, `halt_code`, `halt_diagnostic`). v0.2 limits `children_gate_outcomes[]` to passed entries; halt cases live in `.cascade/halt/<child>-verify.txt`. This session's `/retro` Section 2 reads both sources to render halt cases; v0.2.x consolidation would eliminate the dual read. **Recommendation:** queue for v0.2.x; no v0.2 action required.

  5. **v0.1 backoff constant in `/update-linear`** is referenced by the amendment without a numeric value. The executing Claude Code session preserves whatever v0.1 carries. If v0.1 doesn't explicitly carry the constant (e.g., retries without a configured window), the executing session adds one. **Recommendation:** verify-at-apply-time; the executing session adds a sensible default (e.g., 750ms) if absent.

---

## Failing-test seeds

Per the failing-test seed list in `decomposition.md` Child 0001-B's row, this session's amendments are covered by five tests. Authored as pytest-flavored stubs (matching prior sessions' seeds; runner selection deferred to the per-skill `/specify` calls of `OndraMasek/Solo-Vibing` consumers).

### `test_onboard_skill_creates_six_linear_projects` — `[integration]`

**Assertion.** `/onboard` creates Product, Architecture, Design, Milestones, Backlog, and Done projects with marker-prefixed names when `linear.project_naming = "prefixed"`. Covers AC-13.

**Why.** The most diagnostic check of the v0.2 D1 §Linear product layer realisation; if six projects don't land, every downstream stage's Linear-side write fails.

**Test sketch:**
```python
def test_onboard_skill_creates_six_linear_projects(linear_team_with_collision, tmp_repo):
    # linear_team_with_collision fixture: a Linear team with an existing project
    # named "Product" — triggers prefix mode at step 1.
    invoke_onboard(marker="TST", team=linear_team_with_collision, repo=tmp_repo)
    expected = {"[TST] Product", "[TST] Architecture", "[TST] Design",
                "[TST] Milestones", "[TST] Backlog", "[TST] Done"}
    actual_project_names = {p.name for p in linear_team_with_collision.projects}
    assert expected.issubset(actual_project_names), \
        f"missing projects: {expected - actual_project_names}"

    # Status doc under [TST] Product
    product_project = next(p for p in linear_team_with_collision.projects
                           if p.name == "[TST] Product")
    status_docs = [d for d in product_project.documents
                   if "Status" in d.title or "Product status" in d.title]
    assert len(status_docs) == 1, f"expected one Status doc, got {len(status_docs)}"

    # docs/.solo-config.json reflects prefix mode
    config_path = tmp_repo / "docs" / ".solo-config.json"
    config = json.loads(config_path.read_text())
    assert config["linear"]["project_naming"] == "prefixed"
    assert config["marker"] == "TST"
```

### `test_onboard_skill_writes_workflow_default_strategy_when_set` — `[integration]`

**Assertion.** `/onboard` step 7 elicits a strategy choice with a skip option and writes the selected value (or empty string on skip) to `docs/.solo-config.json`'s `workflow.default_strategy` field. Covers AC-13.

**Why.** Closes the `workflow.default_strategy` wiring loop; asserts the contract `/specify` step 1's amendment relies on.

**Test sketch:**
```python
def test_onboard_skill_writes_workflow_default_strategy_when_set(tmp_repo):
    # Strategy-selected case
    invoke_onboard(marker="TST", team=fresh_team(), repo=tmp_repo,
                   step_7_response="walking-skeleton")
    config = json.loads((tmp_repo / "docs" / ".solo-config.json").read_text())
    assert config["workflow"]["default_strategy"] == "walking-skeleton"

def test_onboard_skill_writes_workflow_default_strategy_when_skipped(tmp_repo):
    # Skip case
    invoke_onboard(marker="TST", team=fresh_team(), repo=tmp_repo,
                   step_7_response="skip")
    config = json.loads((tmp_repo / "docs" / ".solo-config.json").read_text())
    assert config["workflow"]["default_strategy"] == ""
```

The handoff named one test name; the test as authored splits into two for the two branches. The split is a minor refinement and noted here; surface in §Surfaced items if the founder prefers the single-test consolidated form.

### `test_retro_skill_surfaces_tag_distribution` — `[integration]`

**Assertion.** `/retro` reads `children_gate_outcomes[]` from a mocked `/verify` manifest with three strategies represented and renders the documented "shipped N children — A walking-skeleton, B api-boundary, C capability-cluster" summary. Covers AC-12.

**Why.** Asserts Section 1's rendering matches the AC-12 prose contract verbatim; if the bucketing or the ordering changes, the output drifts from the founder-facing spec.

**Test sketch:**
```python
def test_retro_skill_surfaces_tag_distribution(tmp_repo, mock_verify_manifest):
    # mock_verify_manifest fixture: a /verify manifest with 12 children:
    #   9 walking-skeleton, 2 capability-cluster, 1 refactor-spike
    invoke_retro(milestone_id="M-23", repo=tmp_repo,
                 verify_manifest=mock_verify_manifest)

    retro_doc_path = tmp_repo / "docs" / "specs" / "M-23" / "retro.md"
    content = retro_doc_path.read_text()

    expected_line = ("This milestone shipped 12 children — "
                     "9 walking-skeleton, 2 capability-cluster, 1 refactor-spike.")
    assert expected_line in content, \
        f"tag distribution rendering does not match AC-12 example; got:\n{content}"
```

### `test_retro_skill_surfaces_per_gate_outcomes` — `[integration]`

**Assertion.** `/retro` renders per-gate outcome counts including a halt case (e.g., "11/12 passed verify.perceptual-evidence; 1 halted on §perceptual-evidence-missing/byte-stability-failed"). Covers AC-12.

**Why.** Asserts Section 2's rendering AND the dual-source halt-case read (from `children_gate_outcomes[]` for passed entries + from `.cascade/halt/<milestone>-*-verify.txt` for halted entries).

**Test sketch:**
```python
def test_retro_skill_surfaces_per_gate_outcomes(tmp_repo,
                                                  mock_verify_manifest_with_halt,
                                                  mock_halt_artifacts):
    # mock_verify_manifest_with_halt: 11 passed children
    # mock_halt_artifacts: writes .cascade/halt/M-23-SOL-128-verify.txt
    #                      with halt_code=§perceptual-evidence-missing/byte-stability-failed
    invoke_retro(milestone_id="M-23", repo=tmp_repo,
                 verify_manifest=mock_verify_manifest_with_halt)

    retro_doc_path = tmp_repo / "docs" / "specs" / "M-23" / "retro.md"
    content = retro_doc_path.read_text()

    assert "11/12 children passed `verify.perceptual-evidence`" in content
    assert "1 halted on `§perceptual-evidence-missing/byte-stability-failed`" in content
```

### `test_update_linear_skill_evaluates_diff_applied_gate` — `[integration]`

**Assertion.** `/update-linear` halts `§linear-state-inconsistent` when a ticket's current Linear state diverges from `diff_sha256`. Covers AC-13.

**Why.** Asserts Gate 1's behavior — the renamed v0.1 predicate fires under the canonical gate name.

**Test sketch:**
```python
def test_update_linear_skill_evaluates_diff_applied_gate(tmp_repo,
                                                          linear_team_with_drift):
    # linear_team_with_drift: a Linear team where the parent ticket's description
    # has been manually edited between /plan's seal and /update-linear's read,
    # so step 3's write attempts to apply a diff that won't fully land.
    with pytest.raises(CascadeHalt) as exc_info:
        invoke_update_linear(ticket="TST-42", repo=tmp_repo,
                             team=linear_team_with_drift)
    assert exc_info.value.halt_code == "§linear-state-inconsistent"
    assert "ticket TST-42" in exc_info.value.diagnostic
    assert "differs from expected" in exc_info.value.diagnostic
```

---

## Carried-forward queued items not absorbed in this session

Per the prior session's notes; none block continuation 2's seal. All carry forward.

- **F-Rev-2** — D4.5 per-stage `--reconcile` flag-set disposition for `/onboard`, `/update-linear`, `/review`, `/verify`, `/retro`. Surfaces in Child 0001-D.
- **F-Eng-4 / F-Int-2** — Stop-hook output shape for `next_chain_step` Task-invoke. Surfaces in Child 0001-C.
- **F-Eng-5** — chat-Claude multi-MCP-call atomicity for `.cascade/handoff/last.md` write. v0.2.x.
- **F-Eng-6** — chat-Claude 9-check predicate failure modes uncatalogued. v0.2.x measurement deferral (M-5).
- **F-Usr-3** — Project Instructions step 5 acknowledgment. **Disposition this session:** owned by D2.3 v1.3 §Project Instructions block content, not by `/onboard` skill render mechanics. Queued for v0.2.x amendment of D2.3 v1.3.
- **F-Int-5** — D1 step-7 housekeeping. **Disposition this session:** descriptive language in skill; D1 numeric reference fix lands at apply-time per §Surfaced items #2.
- **Ten lower-priority amendments queued for v0.2.x:** F-Usr-1 (consolidated halt message), F-Usr-2 (`/cascade-halt` auto-detect), F-Usr-4 (D4.6 `--rewrite-file` default), F-Usr-5 (pattern names), F-Rev-1 (M-5 measurement), F-Rev-3 (M-6 measurement), F-Rev-4 (pattern framing), F-Rev-5 (check 4a), F-Int-4 (gate-ordering wording).

## Important amendments queued for apply-time (consolidated list)

Per prior sessions' running queue plus this session's surfaced items. All are amendment-pass items; none block apply-time as long as the executing Claude Code session applies the amendments in a single coherent pass.

  1. **Parent spec `spec.md` AC-2:** "eleven new Phase 3 halts" → "fourteen new halts" *(Child A predecessor)*.
  2. **D3.3-vs-decomposition.md per-runner command divergence:** swap three buggy commands in `solo-config.example.json` *(Child A continuation)*.
  3. **`.solo-locks/` path discrepancy:** root-level path accepted; D2.1 v2 v2.1 amended *(Child A continuation)*.
  4. **`spec.md` AC-6 + AC-7 + `decomposition.md` Child 0001-B gate-name reconciliation:** five-name swap to D3.4's names *(Child 0001-B continuation 0)*.
  5. **D3.4 §`/build` row + `spec.md` AC-9:** split D3.4 row to four gates; amend AC-9 to enumerate four *(Child 0001-B continuation 1)*.
  6. **D3.4 §`/wrap` row + `spec.md` AC-10:** split D3.4 row to four gates matching AC-10 *(Child 0001-B continuation 1)*.
  7. **D2.3 v1.3 §`/onboard` integration point:** amend to reflect nine-step sequence *(this session §Surfaced items #1)*.
  8. **D1 §`/onboard` changes step 3:** retire "step 7" numeric reference; use descriptive language *(this session §Surfaced items #2)*.
  9. **D3.4 §`/onboard` row:** enumerate eight predicates for `onboard.config-write` *(this session §Surfaced items #3)*.

Estimated total amendment-pass scope: ~30–35 minutes of edits across `spec.md`, `decomposition.md`, `D3.4_gate_definitions.md`, `D2.1_trust_model.md` v2 + v2.1, `D2.3_hybrid_session_boundary_v1_3.md`, and `D1_linear_product_layer.md`. Absorb in a single pass before the Child A executing Claude Code session runs (or into the Child 0001-B-closing apply-session if the founder prefers later).

---

## Subsequent design sessions after this one

  - **Child 0001-C** — `.claude/hooks/` infrastructure (six hook scripts: preflight-provenance, pyramid-tampering, four-hat-objection-coverage, stop-orchestrator, session-start-state-restore, session-end-telemetry) + `.claude/settings.json` wiring. Walking-skeleton strategy. One session likely sufficient. Includes Stop-hook output shape for `next_chain_step` Task-invoke (F-Eng-4 / F-Int-2). Includes `§kill-received-remote` and `§manual-halt-pending` halt-card authoring (per Child 0001-B continuation 1 Surfaced item #4). The `session-end-telemetry.sh` hook produces the per-session telemetry `/retro` Section 3 reads.

  - **Child 0001-D** — `tools/solo-verify` Python stdlib script implementing D3.4's CLI surface. Walking-skeleton with heavy `[unit]` coverage. One to two sessions. Includes per-stage `--reconcile` flag-set disposition (F-Rev-2 carry-forward: extend `--reconcile` to `/onboard`, `/update-linear`, `/review`, `/verify`, `/retro`).

  - **Child 0001-E** — `CLAUDE.md` and `README.md` amendments + lockstep update to `docs/templates/CLAUDE.md`. Walking-skeleton. One session.

Total Phase-2-design sessions remaining after this one: ~4 (Child 0001-C, two Child 0001-D, Child 0001-E).

---

## Handoff prompt for next session

> **Title:** 0001 integration spec Child 0001-C — `.claude/hooks/` infrastructure + `.claude/settings.json` wiring.
>
> **Task:** Author the six hook scripts (`preflight-provenance.sh`, `pyramid-tampering.sh`, `four-hat-objection-coverage.py`, `stop-orchestrator.sh`, `session-start-state-restore.sh`, `session-end-telemetry.sh`) and the `.claude/settings.json` file that wires them to the D2.2 hook events (PreToolUse, PostToolUse, SubagentStop, SessionStart source=startup/resume/compact, SessionEnd, Stop). Walking-skeleton strategy.
>
> **Should fit in one session.** Six hook scripts are small (most are deterministic shell predicates per D2.2 §command hook type; the four-hat one is Python per D2.2 §What goes where in Python). The `.claude/settings.json` file is one file with the hook-event wiring per D2.2 §Settings file precedence.
>
> **Three concrete deliverable clusters:**
>
>   1. **The five command-type hook scripts** (bash):
>      - `preflight-provenance.sh` — wraps the caller-side verification predicate from D2.1 v2 §Caller-side verification protocol; fires PreToolUse on each cascade-spawn tool call.
>      - `pyramid-tampering.sh` — wraps `/build` Gate 2's PreToolUse predicate per the Child 0001-B continuation 1 `/build` amendment.
>      - `stop-orchestrator.sh` — the single Stop-hook orchestrator per D2.2 §Research-step resolution #3; reads `cascade:run-state.kill_in_progress` and `cascade:run-state.manual_halt`; halts `§kill-received-remote` or `§manual-halt-pending` per Child 0001-B continuation 1 Surfaced item #4.
>      - `session-start-state-restore.sh` — fires SessionStart=startup|resume|compact; restores `cascade:run-state` from disk; per D2.2 §SessionStart + D2.1 v2 §Cross-compact state.
>      - `session-end-telemetry.sh` — fires SessionEnd; writes per-session telemetry to `.cascade/session/<milestone>-*.jsonl` per D2.2 §Critical caveat #4 async-only; consumed by `/retro` Section 3 per this session's `retro-SKILL-amendments.md`.
>
>   2. **The single agent-type hook script** (Python):
>      - `four-hat-objection-coverage.py` — wraps `/review` Gate 2's SubagentStop predicate per Child 0001-B continuation 1 `/review` amendment. Output shape: top-level `{"decision": "block", "reason": "..."}` per D2.2 §Stop / SubagentStop output schema quirk. The cascade's single agent-type hook.
>
>   3. **`.claude/settings.json`** — wires the six scripts to their D2.2 hook events with the appropriate matchers; uses the single Stop-hook orchestrator pattern per D2.2 §Research-step resolution #3.
>
> **F-Eng-4 / F-Int-2 disposition (Stop-hook output shape for `next_chain_step` Task-invoke):** the stop-orchestrator's output emits the standard hook-output shape for Task-invoke of the next chain step per D2.2 §Hook events; carry forward the factual-phrasing pattern from F-Int-2. The hook output is not where the chain-pointer dispatch logic lives — that's in the skill's `/Chains` block. The hook just halts (or doesn't) per the orchestration predicate.
>
> **`§kill-received-remote` and `§manual-halt-pending` halt-card authoring:** these two halt codes are referenced in Child 0001-B continuation 1's `/build` amendment §Interaction with sidecar commands subsection but were not in v0.1 nor in Child A's `halt-messages-append.md`. Author them here alongside `stop-orchestrator.sh`'s scope; the hook script's diagnostic text becomes the halt-card content.
>
> **Read first (use `project_knowledge_search`):**
>
>   - `00_PROJECT_INSTRUCTIONS.md`
>   - All Child 0001-B deliverables — `specify-SKILL-amendments.md`, `plan-SKILL-amendments.md` (continuation 0); `review-SKILL-amendments.md`, `build-SKILL-amendments.md`, `wrap-SKILL-amendments.md`, `verify-SKILL-amendments.md` (continuation 1); `onboard-SKILL-amendments.md`, `retro-SKILL-amendments.md`, `update-linear-SKILL-amendments.md` (continuation 2). The hooks compose against the gates these skills evaluate.
>   - `D2.2_session_auto_management.md` §all (the hook surface; D2.2 is the canonical source).
>   - `D2.2_session_auto_management.md` §Stop / SubagentStop output schema quirk (the agent-type hook output shape).
>   - `D2.2_session_auto_management.md` §Research-step resolution #3 (the single Stop-hook orchestrator pattern).
>   - `D2.2_session_auto_management.md` §Settings file precedence (`.claude/settings.json` semantics).
>   - `D2.1_trust_model.md` v2 §Caller-side verification protocol (the preflight-provenance predicate logic).
>   - `D2.1_trust_model.md` v2 §Cross-compact state (the session-start-state-restore restoration logic).
>   - `D2.3_hybrid_session_boundary_v1_3.md` §Group-exit mechanics atomicity (the chat-Claude write protocol; informs which hook fires on which event in Group F).
>   - `decomposition.md` Child 0001-C files-in-scope row.
>   - `repo-state-summary.md` Part 2 (verify the six hook scripts are absent in v0.1).
>   - `spec.md` AC-14.
>
> **Phase:** Child 0001-C (walking-skeleton strategy — perceptual artifact = working Claude Code session that triggers each hook).
>
> **Deliverables:**
>
>   - `.claude/hooks/preflight-provenance.sh` — patch-ready script.
>   - `.claude/hooks/pyramid-tampering.sh` — patch-ready script.
>   - `.claude/hooks/stop-orchestrator.sh` — patch-ready script with `§kill-received-remote` and `§manual-halt-pending` halt-card text embedded.
>   - `.claude/hooks/session-start-state-restore.sh` — patch-ready script.
>   - `.claude/hooks/session-end-telemetry.sh` — patch-ready script with the telemetry JSONL schema specified.
>   - `.claude/hooks/four-hat-objection-coverage.py` — patch-ready script emitting the D2.2 §Stop / SubagentStop output schema quirk shape.
>   - `.claude/settings.json` — patch-ready file wiring the six scripts to D2.2 events.
>   - `child_C_hooks_and_settings_authoring_notes.md` — notes doc covering: hook firing order semantics, the `§kill-received-remote` and `§manual-halt-pending` halt-card disposition, the telemetry JSONL schema, and any newly surfaced items.
>   - Handoff prompt for the next session: "Child 0001-D — `tools/solo-verify` Python stdlib script implementing D3.4's CLI surface. Walking-skeleton with heavy `[unit]` coverage. Includes per-stage `--reconcile` flag-set disposition (F-Rev-2 carry-forward)."

---

## What lands in the framework repo (not in this project)

This session's three SKILL.md amendments are *design deliverables* in this Claude.ai project, *implementation deliverables* in Claude Code against `OndraMasek/Solo-Vibing`.

**After this session: Child 0001-B's design phase is complete.** All ~9 cascade skills are designed across three sessions (continuation 0: `/specify`, `/plan`; continuation 1: `/review`, `/build`, `/wrap`, `/verify`; continuation 2: `/onboard`, `/retro`, `/update-linear`). The executing Claude Code session for Child 0001-B can run, taking all three sessions' deliverables and applying them as a coherent patch against the framework repo.

The executing session's order:

  1. Apply the queued amendment pass (the nine items in §Important amendments queued for apply-time) against the design docs and parent spec.
  2. Read v0.1 SKILL.md files for `/specify`, `/plan`, `/review`, `/build`, `/wrap`, `/verify`, `/onboard`, `/retro`, `/update-linear`.
  3. Apply each amendment block to the corresponding SKILL.md, preserving the existing `/Chains` block from `child_B_chains_sections.md`.
  4. Run the failing-test seeds from §Failing-test seeds (this session) plus the prior sessions' seeds.
  5. Commit one-skill-at-a-time so a partial pass leaves a coherent intermediate state.

Subsequent Phase-2 design sessions: Child 0001-C, Child 0001-D, Child 0001-E. After all four executing Claude Code sessions run, the v0.2 integration spec is complete and `OndraMasek/Solo-Vibing` v0.2 can be tagged.

---

## Cross-references

- **D1 §`/onboard` changes** — binding for `/onboard`'s step sequence; F-Int-5 disposition lands here at apply time.
- **D2.1 v2 §`/onboard`, `/retro`, `/update-linear` rows** — manifest schema baselines for the three amendments.
- **D2.1 v2.1 §common-manifest-fields** — the `outputs.summary` field convention all three amendments include.
- **D2.2 §Hook events** — the hook surface the next session (Child 0001-C) realizes.
- **D2.3 v1.3 §`/onboard` integration point** — eight-step sequence amended to nine in this session (apply-time per §Surfaced items #1).
- **D2.3 v1.3 §`/Chains` contract** — Pattern T (`/onboard`), Pattern C (`/update-linear`), Pattern N (`/retro`) — per-pattern statements binding for each amendment's manifest's role as Group exit manifest.
- **D2.3 v1.3 §Project Instructions block** — content owned by D2.3; this session's `/onboard` skill step 8 reads-and-renders, doesn't author.
- **D3.1 §`/onboard` product-level default** — binding for `workflow.default_strategy` slot semantics; loop closed this session.
- **D3.1 §Decomposition strategy catalog** — the five canonical strategies `/retro` Section 1 buckets by.
- **D3.4 §Per-stage gate inventory `/onboard`, `/retro`, `/update-linear` rows** — gate firing order and predicate references; row text widened at apply-time per §Surfaced items #3.
- **D3.4 §Manifest schema additions** — `children_gate_outcomes[]` schema `/retro` Section 2 reads; v0.2.x extension queued per §Surfaced items #4.
- **D4.5 §Decision** — F-Rev-2 carry-forward: `--reconcile` not present for `/onboard`, `/update-linear`, `/retro` in v0.2; Child 0001-D's design surface.
- **D4.6 v1.1 §CLI surface** — re-derivation contract reading each amendment's manifest's `outputs.summary` for Groups A, E, H.
- **Child A `solo-config-additions.json`** + **Child A `solo-config.example.json`** — config schema this session's `/onboard` Gate 2 validates.
- **Child A `halt-messages-append.md`** — halt codes referenced by each amendment.
- **Child A `chat-end-card.md`** — template each amendment's group-exit render reads.
- **`child_B_chains_sections.md`** — `/Chains` blocks for `/onboard` (Pattern T Group A), `/retro` (Pattern N Group H), `/update-linear` (Pattern C Group E); this session's amendments land BEFORE the `/Chains` blocks.
- **`specify-SKILL-amendments.md`** + **`plan-SKILL-amendments.md`** (Child 0001-B continuation 0) — `/specify` step 1's read pattern that this session's `/onboard` step 7 write satisfies; the `child_strategies[]` array on `/plan`'s manifest read by `/update-linear` step 2.
- **`review-SKILL-amendments.md`** + **`build-SKILL-amendments.md`** + **`wrap-SKILL-amendments.md`** + **`verify-SKILL-amendments.md`** (Child 0001-B continuation 1) — amendment-pattern shape and gate-evaluator structure this session matches.
- **Child 0001-C** `.claude/hooks/four-hat-objection-coverage.py` — wraps `/review` Gate 2; not in this session's scope.
- **Child 0001-C** `.claude/hooks/session-end-telemetry.sh` — produces the telemetry `/retro` Section 3 reads; not in this session's scope.
- **Child 0001-D** `tools/solo-verify` — implements D3.4's CLI surface; the `--reconcile` extension for `/onboard`, `/update-linear`, `/retro` per F-Rev-2 lands here.
- **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md`** AC-12, AC-13 — this session's three amendments satisfy these two ACs as authored, modulo the row-widening reconciliation per §Surfaced items #3.
