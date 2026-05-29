# 0002 — Decomposition sketch

**Status:** Re-sealed into repo (hand-authored mirror of the 2026-05-20 chat-Claude /plan; the cascade's decomposer did not write this to disk because hooks were not firing — see `spec.md` §Dogfood execution caveat). Structured to match what `/plan` would produce so a Code session can consume it as-is.

**Parent:** `0002-v0.2-release-wrap-up`.
**Parent strategy:** `hybrid` — per D3.1, every child carries an explicit non-inherited strategy. `/plan` halts `§hybrid-without-child-overrides` if any child lands without one.

---

## Children at a glance

| Child | Slug | Strategy | Scope |
|---|---|---|---|
| 0002-A | `v0.2-docs-lockstep` | `walking-skeleton` | Three founder-facing docs amended in lockstep (`CLAUDE.md`, `README.md`, `docs/templates/CLAUDE.md`). End-to-end demoable as: a fresh fork runs `/onboard --dry-run` and gets a v0.2-shaped scaffold. SOL-103. |
| 0002-B | `v0.2.x-followup-tickets` | `capability-cluster` | Four independent v0.2.x Linear tickets created in `[SOL] Backlog`. Each is a self-contained capability shipping in its own future spec. SOL-104. |

Two children. No nested hybrid; each carries one strategy and `/plan` halts if any subsequent finding pushes a child to need its own hybrid split. v0.2 caps hybrid nesting at one level per D3.4 §`/verify` dispatch.

---

## Child 0002-A — `v0.2-docs-lockstep`

**Strategy:** `walking-skeleton`.
**Linear:** SOL-103.

**Rationale.** The three docs are a single vertical slice: the end-to-end signal is "a fork operator clones the repo, runs `/onboard --dry-run` against a fresh tmpdir, and the rendered `CLAUDE.md` carries the v0.2 sections — the fork can teach itself v0.2 from the docs it ships with." That clone → onboard → rendered-scaffold path is the thin slice through every layer, exactly the walking-skeleton signal from D3.1. The amendments are purely structural (headings + cross-references + cited path strings; no timestamps, no version strings) so byte-stability holds per four-hat objection #15 resolution (path b).

**Files in scope (full paths):**

- `CLAUDE.md` (repo root) — per AC-1. Drop the v0.1 "no hooks in v0.1" sentence (false post-PR-5). Add six subsections: §Cascade gates (→ `docs/templates/halt-messages.md` + `python3 tools/solo-verify --list-gates`); §Strategy enum (→ `/specify` step 1 + the five D3.1 strategies); §Hooks (→ `.claude/settings.json` + the eight hook scripts `preflight-provenance.sh`, `pyramid-tampering.sh`, `four-hat-objection-coverage.py`, `stop-orchestrator.sh`, `session-start-state-restore.sh`, `session-end-telemetry.sh`, `precompact-safe-boundary.sh`, `pretool-write-denylist.sh`); §Tainted state (→ 0001 AC-18 `is_tainted` / `taint_reason` + `--reconcile-only` clearing); §Code markers (→ `.claude/rules/code-markers.md` for 🤔/📝/☣️); §CI (→ `.github/workflows/ci.yml`).
- `README.md` (repo root) — per AC-2. Status block carries the verbatim line "v0.2 cascade primitives integrated and self-applied; v0.2.x cycle open". Add §"What's new in v0.2" listing the cascade primitives now in scope.
- `docs/templates/CLAUDE.md` — per AC-3, lockstep with AC-1. Same six §sections, parameterized for fresh forks, cross-referencing D2.1 v2.1's `.cascade/run-state.json` canonical path at repo root. (Confirm on-disk filename: may be `CLAUDE.md.template` — Code reconciles at build.)
- `docs/specs/0002-v0.2-release-wrap-up/perceptual/onboard-dry-run.txt` — per AC-4. Sealed at /build's at-write trigger. Captured via two consecutive `/onboard --dry-run` invocations against the D0.1 CI fixture tmpdir. Byte-stability predicate: strip lines matching `^.*Last updated.*\d{4}-\d{2}-\d{2}` and `^[A-Z_]+_RUN_ID=`; sha256 compare; equality required. **Not fabricated at re-seal time.**

**Pyramid shape:** `walking-skeleton`-shaped — required: `smoke`, `perceptual`. Optional: `unit`, `integration`. Forbidden: `contract`, `invariance`.

**Failing-test seed (12 smoke + 1 perceptual):**

- `test_claude_md_drops_no_hooks_sentence` — `[smoke]` — asserts `CLAUDE.md` does not contain the literal string "no hooks in v0.1"; covers AC-1.
- `test_claude_md_has_cascade_gates_subsection` — `[smoke]` — asserts `CLAUDE.md` contains the §Cascade gates subsection; covers AC-1.
- `test_claude_md_has_hooks_subsection` — `[smoke]` — asserts `CLAUDE.md` contains the §Hooks subsection naming `.claude/settings.json`; covers AC-1.
- `test_claude_md_has_strategy_enum_subsection` — `[smoke]` — asserts `CLAUDE.md` contains the §Strategy enum subsection; covers AC-1.
- `test_claude_md_has_tainted_state_subsection` — `[smoke]` — asserts `CLAUDE.md` contains the §Tainted state subsection; covers AC-1.
- `test_claude_md_has_code_markers_subsection` — `[smoke]` — asserts `CLAUDE.md` contains the §Code markers subsection; covers AC-1.
- `test_claude_md_has_ci_subsection` — `[smoke]` — asserts `CLAUDE.md` contains the §CI subsection; covers AC-1.
- `test_claude_md_hooks_subsection_names_eight_scripts` — `[smoke]` — asserts the §Hooks subsection names all eight hook scripts; covers AC-1.
- `test_readme_status_block_reads_v0_2` — `[smoke]` — asserts `README.md` Status block contains the verbatim v0.2 line; covers AC-2.
- `test_readme_has_whats_new_section` — `[smoke]` — asserts `README.md` contains the §"What's new in v0.2" heading; covers AC-2.
- `test_template_matches_root_for_shared_sections` — `[smoke]` — asserts the six shared §sections in the CLAUDE.md template are textually equivalent to the root `CLAUDE.md` (modulo template-specific variant blocks); covers AC-3.
- `test_template_references_run_state_canonical_path` — `[smoke]` — asserts the template cross-references `.cascade/run-state.json`; covers AC-3.
- `test_onboard_dry_run_byte_stable` — `[perceptual]` — asserts two consecutive `/onboard --dry-run` renders are byte-identical after the AC-4 strip rules; covers AC-4. Per D3.3 §Walking-skeleton perceptual predicate.

Twelve smoke + one perceptual; required tags `smoke` and `perceptual` both present; forbidden `contract`, `invariance` absent.

**Notes for the executing /build session:**

- Read current post-PR-5 byte-for-byte content of all three files before amending. Reconcile in place; preserve all v0.1 content the amendments don't touch.
- The §Hooks subsection enumerates eight scripts (seven from Child 0001-C + `pretool-write-denylist.sh` from 0001 AC-21). Verify all eight exist in `.claude/hooks/` post-PR-5.
- §Tainted state references `--reconcile-only`. Verify the flag name against `tools/solo-verify --help` post-PR-5.
- Strand A `/specify` defines the `/onboard --dry-run` determinism contract before sealing AC-4's perceptual artifact (per skeptic-hat #17 deferred-to-child resolution).

---

## Child 0002-B — `v0.2.x-followup-tickets`

**Strategy:** `capability-cluster`.
**Linear:** SOL-104.

**Rationale.** Four Linear issues, each a self-contained capability with its own halt-code or schema-field surface, each shipping independently in a future v0.2.x spec. No shared vertical slice — the canonical capability-cluster shape per D3.1 §capability-cluster. The "v0.2.x backlog seeded" cluster is the bounded deliverable.

**Files in scope:** writes to Linear, not the filesystem.

- `[SOL] Backlog` Linear project — receives four new issues per AC-5 / AC-6 / AC-7 / AC-8.
- `v0.2.x` Linear label — auto-created on first `save_issue` via the `labels[]` parameter (no `create_issue_label` call needed).
- `docs/specs/0002-v0.2-release-wrap-up/perceptual/linear-tickets-created.json` — sealed at /build's at-write trigger. Captures the Linear API response JSON for the four creations (id, identifier, title, URL, labels, project ID), canonicalized via key-sort + stable-field-only filter. Per D3.3 §Capability-cluster perceptual predicate, `api-response` artifact-type, `.json` extension. **Not fabricated at re-seal time.**

**The four tickets (full scope statements live in `spec.md` AC-5..AC-8):**

- **AC-5** — PreCompact output shape validation against Claude Code v2.0.76+ (`precompact-safe-boundary.sh` emitter; `lib/common.sh` carries both emitters). Citation: Child 0001-C §Surfaced items #5.
- **AC-6** — PRIMING_MARKERS validation against /review priming text (`four-hat-objection-coverage.py` dict vs the four `four-hat-*` agent files). Citation: Child 0001-C §Surfaced items #6.
- **AC-7** — MultiEdit handling in `pyramid-tampering.sh` (replay-via-Python-helper vs block-all-MultiEdit). Citation: Child 0001-C §Surfaced items #7.
- **AC-8** — D2.1 v2 AC-hash regex permissiveness confirmation (`_ac_list_sha256_from_spec` H1/H2/H3 accept vs documented H2-only). Citation: Child 0001-D §4 reconciliation queue item #5.

**Pyramid shape:** `capability-cluster`-shaped — required: `integration`, `perceptual`. Forbidden: `smoke`, `contract`, `invariance`.

**Failing-test seed (4 integration + 1 perceptual):**

- `test_precompact_ticket_created_with_required_fields` — `[integration]` — covers AC-5.
- `test_priming_markers_ticket_created_with_required_fields` — `[integration]` — covers AC-6.
- `test_multiedit_ticket_created_with_required_fields` — `[integration]` — covers AC-7.
- `test_ac_hash_regex_ticket_created_with_required_fields` — `[integration]` — covers AC-8.
- `test_linear_tickets_api_response_byte_stable` — `[perceptual]` — covers AC-5 through AC-8. Per D3.3 §Capability-cluster perceptual predicate, `api-response` artifact-type.

Four integration + one perceptual; required tags `integration` and `perceptual` both present; forbidden `smoke`, `contract`, `invariance` absent.

**Notes for the executing /build session:**

- The `v0.2.x` label is auto-created on first `save_issue`. No `create_issue_label` call needed.
- Each issue's `description` carries the full scope statement from `spec.md` AC-5/6/7/8, in markdown (literal newlines, no escape sequences per `save_issue` schema).
- Capture the perceptual JSON AFTER all four `save_issue` calls succeed, via a single `list_issues` query filtered by the four IDs — one consolidated capture, not four ordering-sensitive per-ticket JSONs.
- Title canonicalization: em-dash (`—`, U+2014) is the separator; Linear MCP `save_issue` preserves it verbatim.

---

## Build order (recommended)

1. **0002-A** first — docs lockstep is the higher-value, lower-risk slice and exercises the perceptual gate end-to-end. Read post-PR-5 content, amend three files, seal `onboard-dry-run.txt`.
2. **0002-B** second — four `save_issue` calls + one consolidated `list_issues` capture for the perceptual JSON. Independent of 0002-A; can run in parallel if budget allows.

Ralph budget per child (rough): 0002-A short-to-medium (~2–3 iterations, the lockstep diff is the fiddly part); 0002-B short (~1–2, four ticket creations + one capture).

---

## Open questions deferred to per-child `/specify`

- 0002-A: exact textual-equivalence definition for `test_template_matches_root_for_shared_sections` — whole-section string match vs heading-set match modulo variant blocks? (Recommend: normalized-section-body match excluding HTML-comment variant markers.)
- 0002-B: should the four tickets carry `blockedBy` relations to a v0.2.x milestone, or land bare in Backlog? (Recommend: bare; the v0.2.x cycle planner groups them.)
- Parent: `decomposition.md.template` — resolved in `spec.md` §Open spec question as **defer to v0.2.x backlog** (not Child 0002-C unless founder overrides).
