# spec: extend /wrap to append docs/specs/NNNN-<slug>/build-log.md

> Spec ID: 0001-wrap-build-log
> Parent ticket: SOL-42
> Four-hat doc: [SOL-DOC-0003] four-hat: SOL-42 extend /wrap to append build-log
> spec_sha256: 730cac5eddf38235
> Status: sealed
> Last updated: 2026-05-14

## Problem statement

`/wrap` posts a session summary as a Linear comment, transitions the child to Done, and ends. The spec directory `docs/specs/NNNN-<slug>/` accumulates `spec.md`, `decomposition.md`, `verify-report.md` — but nothing that records what each child actually built. `/retro` reconstructs "what was built" from comments scattered across N child tickets at parent close — this is the present-day primary motivator. `/specify --continue` and `/diagnoser` are secondary consumers that benefit as their traffic grows.

By the time `/retro` runs, the implementation evidence is spread across Linear comments, git log, and the founder's memory. There is no single per-parent ground-truth artifact for "what was built."

This spec adds that artifact: an append-only `docs/specs/NNNN-<slug>/build-log.md` written by `/wrap` and read by `/specify`, `/diagnoser`, and `/retro`. Workflow-internal change; no user-visible surface.

## API contract

(Backend-only — per template, replaces Design & UX.)

### Write contract — `/wrap` step 4 output

`/wrap` step 4 — currently "Post session summary on child ticket" — extends to **two writes** within the existing same-turn batch:

1. The existing Linear comment (unchanged).
2. A filesystem write appending one section to `docs/specs/NNNN-<slug>/build-log.md`, where `NNNN-<slug>` is the parent's spec directory (resolved from the parent ticket's spec-path field or from `decomposition.md`).

Both writes batch same-turn with the step 5 Linear state transition and the step 7 parent-completion writes, per `.claude/rules/write-discipline.md` §Same-turn batching. The filesystem write is **same-turn, read-precedes-write** — not literally parallel with the Linear MCP call. The platform permits within-turn ordering; "same-turn" is the contract that matters.

**Implementation rule (pinned).** On every `/wrap` invocation:

1. `Read` `docs/specs/NNNN-<slug>/build-log.md` if it exists; otherwise treat content as empty.
2. Compose the new section per the template below.
3. `Write` the full content (prior + new section) back, OR — for a fresh file — `Write` header + new section.

`Append-only` (AC-5) is a **semantic invariant**: prior section bytes are preserved byte-identical across the write. The tool-call is a `Read` + `Write` (full-file replacement) — not an `Edit` against a fragile anchor that founder hand-edits could break. `Write` chosen over `Edit` so manual-edit corruption between wraps does not halt /wrap.

**File creation.** If `docs/specs/NNNN-<slug>/build-log.md` does not exist (first child wrap for this parent), the first `Write` includes both the header (below) and the first section. The exists-check + `Write` batch same-turn.

**Parent-slug resolution.** /wrap is invoked with a child ID `<MARKER>-N-K`. The parent spec path `docs/specs/NNNN-<slug>/` is resolved as follows (first match wins):
1. Read `docs/specs/*/decomposition.md` for the file whose body contains `<MARKER>-N` as a parent reference.
2. Fall back to: parse the parent ticket's branch name (`<MARKER>-N-<slug>`) and look up `docs/specs/*-<slug>/`.
3. If neither resolves → `BLOCKED` per AC-7 with halt-pattern `§missing-context`.

**Section template** (stable shape, AC-2 contract):

```markdown
## <MARKER>-N-K — <child title>[ — (re-wrap, supersedes prior)]

- **date:** YYYY-MM-DDTHH:MM:SSZ   <!-- commit-timestamp of /wrap's commit -->
- **tests:** <X>/<X> passing | not re-run (resume-merge)
- **commits:** <count> (<short-sha-1>, ..., <short-sha-N>) | 0 (no new commits)
- **branch:** <MARKER>-N-<slug>-K
- **files changed:**
  - `path/to/foo.ext`
  - `path/to/bar.ext`
  - ... <!-- cap at 20 entries; if more, append: "  - ... and N more files (see git diff <base>..HEAD)" -->
- **build-reviewer decisions:**
  - <decision text from .ralph/<MARKER>-N-K/reviewer-findings.json> | none | n/a (manual /wrap)
- **deferred follow-ups:**
  - <item from .ralph/<MARKER>-N-K/fix_plan.md flagged [defer]> | none
```

Render rules:
- Heading suffix `— (re-wrap, supersedes prior)` is appended when this is at least the second wrap of the same `<MARKER>-N-K`. Consumers read the latest section per child ID as authoritative; this annotation is the human-visible signal.
- Each bullet renders the explicit empty-state token (`none`, `n/a`, `0 (no new commits)`, `not re-run (resume-merge)`) rather than collapsing the field. AC-2's "all eight fields populated" is enforced.
- `commits` lists short-SHAs from the Ralph child branch in chronological order (`<base>..HEAD` on `<MARKER>-N-<slug>-K`). Per `/wrap` SKILL.md step 3, /wrap commits + pushes the branch; the SHA list captures the Ralph-iteration commits + the final /wrap commit.
- `files changed` lists git-diffed file paths only — no per-file semantic summary. (Drops scope drift; per-file summary was unbounded.)
- `date` is the commit-timestamp of `/wrap`'s step-3 commit (`git show -s --format=%cI HEAD`), not wall-clock — git-reproducible and skew-resistant.

**File header** (written on first create, never rewritten):

```markdown
# Build log: <parent title> (<MARKER>-N)

> One section per child build, newest at bottom. Written by `/wrap`; read by `/specify`, `/diagnoser`, `/retro`.
> Append-only and machine-managed — do not hand-edit. Founder edits are not detected and are not merged; /wrap appends at EOF unconditionally.
```

**Carrier files (input contracts for /wrap step 4).**

| Field | Source | Path | When |
|---|---|---|---|
| `build-reviewer decisions` | `/build` finalize phase writes the build-reviewer agent's structured findings | `.ralph/<MARKER>-N-K/reviewer-findings.json` | After `/build`'s reviewer pass, before `/build` Task-invokes `/wrap` |
| `deferred follow-ups` | `/build` step that drafts `fix_plan.md` | `.ralph/<MARKER>-N-K/fix_plan.md` | At Ralph workspace prep |
| `commits` | git | `git log <base>..HEAD --format=%h` on child branch | At /wrap step 1 |
| `files changed` | git | `git diff --name-only <base>..HEAD` on child branch | At /wrap step 2 (already done for scope verification) |
| `date` | git | `git show -s --format=%cI HEAD` on child branch | At /wrap step 3 (post-commit) |
| `tests` | /wrap step 1 re-run output | (in-memory) | At /wrap step 1 |

Both `.ralph/` files must persist through `/build`'s finalize phase (not cleaned before /wrap fires). The `/build` skill is responsible for the persistence guarantee; /wrap reads them.

**Partial-failure recovery.** If the filesystem `Write` succeeds but the Linear MCP comment/state-transition fails (or vice versa) within the same-turn batch, `write-discipline.md` §Partial failure prescribes dropping a marker file and halting `BLOCKED` with a sync-retry hint. For this contract:

- **Filesystem succeeded + Linear failed:** the filesystem build-log entry is canonical. On `/wrap --resume-merge`, /wrap **skips** the filesystem append (detect by reading the last section heading; if it matches the current child ID + commit-timestamp, treat as already-written) and retries the Linear writes only. No duplicate section.
- **Filesystem failed + Linear succeeded:** rare (filesystem writes don't normally fail post-Read). On retry, the section is composed fresh and written; Linear retries are no-ops.
- **Both failed:** retry the full batch fresh.

### Read contract — consumers

| Skill / agent | When | What it loads | Surface to founder |
|---|---|---|---|
| `/specify` (step 1, context load) | `--continue` against a parent with prior wrapped children, OR a fresh `/specify` for a later spec under the same parent | Entire `build-log.md` for the same parent | Included in the four-hat critique input set; mentioned in the step-1 context-load summary printed to founder |
| `/diagnoser` agent | Invoked by `/verify` on an AC failure | Entire `build-log.md` for the parent (path derived from the parent spec path that /diagnoser already receives as input — no new input parameter) | Surfaces in the diagnoser's structured findings as a `## Build history` block |
| `/retro` (step 1, history load) | Parent close (all children Done) | Entire `build-log.md` | Verbatim quotes per child entry in the retro doc |

Read scope is **same-parent only** in v0.1. Cross-parent aggregation is out of scope.

**Malformed / present-but-empty file.** Consumers treat `build-log.md` as **opaque text** in v0.1. No header validation, no section-shape parsing, no halt on malformed content. A present-but-empty file behaves the same as an absent file. Founder-introduced corruption is the founder's problem; consumers degrade gracefully (the value of having the file is monotonic — partial content is still useful context).

### DX section

- **Format stability.** Section template is the contract. Adding fields is non-breaking (consumers tolerate unknown fields). Removing or renaming fields is breaking and requires a coordinated edit across consumers + a migration note in the build-log header.
- **Idempotency on re-wrap.** Re-invocations append a new section with `— (re-wrap, supersedes prior)` annotation in the heading. Consumers (humans + future machine parsers) see the most-recent entry per child ID as authoritative. The append-only invariant takes precedence — never overwrite a prior section.
- **No machine parser in v0.1.** Consumers read the markdown as text. A structured parser (TOML frontmatter, JSON sidecar) is deferred.
- **Template touch.** `docs/templates/spec.md.template` gains a one-line note under §Output artifacts pointing at the build-log location, so spec authors know the artifact exists in the directory layout.
- **Missing-parent precondition.** Manual `/wrap <MARKER>-N-K` invocations against a child whose parent has no resolvable spec directory halt `BLOCKED` per `.claude/rules/completion-status.md`, using existing halt-pattern `§missing-context` from `docs/templates/halt-messages.md` with the diagnostic "missing parent spec directory for child `<MARKER>-N-K` — neither decomposition.md nor branch-name lookup resolved a parent slug." No new halt-pattern invented.
- **Concurrent /wrap (v0.1 acknowledged failure mode).** v0.1 assumes one `/wrap` at a time per CLAUDE.md §Session discipline. Manual `/wrap` invocations are not mutex-bounded. If a founder runs two manual `/wrap` invocations against siblings concurrently and they race the Read-Write of the same `build-log.md`, the second-to-Write wins and the first's section is lost. Founder responsibility in v0.1; advisory file lock is a v0.2 follow-up (see §Open Questions).

## Scope boundary

### In scope

- Extend `/wrap` step 4 to append a per-child section to `docs/specs/NNNN-<slug>/build-log.md` (new file, semantically append-only, same-turn-batched with the existing Linear writes per `write-discipline.md`).
- Define the build-log section template (header + per-child template + render rules) and the carrier-file input contracts (`.ralph/<MARKER>-N-K/reviewer-findings.json`, `.ralph/<MARKER>-N-K/fix_plan.md`, git inputs).
- Update `docs/templates/spec.md.template` to reference the build-log file in the spec-directory layout.
- Extend `/specify` step 1 context-load to include `build-log.md` when present for the same parent.
- Extend `/diagnoser` agent to load `build-log.md` for the parent (path derived from the parent spec path the agent already receives — no new input parameter).
- Extend `/retro` step 1 history-load to consume `build-log.md` as the primary source for "what was built" summaries.
- First-create semantics + partial-failure recovery via `/wrap --resume-merge`.
- Halt-card behavior for missing parent spec directory on manual `/wrap` invocations (reuses `§missing-context`).
- Update `/build` finalize phase to persist `.ralph/<MARKER>-N-K/reviewer-findings.json` for /wrap to consume.

### Out of scope

- **README / changelog / API-doc generation** — separate product-documentation skill; deferred per founder direction.
- **Build-log compaction / archival policy** — v1.1+.
- **Cross-parent build-log aggregation** — v1.1+; "what shipped this week" view is a separate feature.
- **Structured (JSON / TOML) build-log format** — markdown only in v0.1.
- **`/wrap` behavior changes outside step 4** — steps 1, 2, 3, 5, 6, 7 are untouched. The build-log append rides on step 4's existing batch.
- **Manual founder edits to `build-log.md`** — file is machine-managed; founder edits are not detected or merged. `/wrap` appends at EOF unconditionally; manual edits don't halt /wrap.
- **`/verify-fix` child special-case shape** — fix-children produced by `/verify` pass through `/build → /wrap` normally; their wraps append to the parent's `build-log.md` per the normal flow. Optional template fields for fix-child traceability (`fix-of`, `retries-AC`) are a v1.1 follow-up.
- **Tamper detection** — header is a comment, not a guard. v1.1.
- **Advisory file-lock for concurrent /wrap** — v0.2 (concurrency support arrives with subagent parallelism per `/wrap` SKILL.md §Open questions).
- **Historical reconstruction** — parents that wrapped before SOL-42 ships have no `build-log.md`. Consumers tolerate absence (AC-3). A reconstruction tool from Linear comments + git log is a v1.1 candidate.
- **Per-file semantic summaries in `files changed`** — file list only in v0.1. Per-file summaries were unbounded scope (per-file LLM call latency + cost not budgeted).
- **Outline-navigable date-in-heading** — v1.1 polish; date stays in the bullet block.

## Acceptance criteria

- [ ] **AC-1:** `/wrap` writes a new section to `docs/specs/NNNN-<slug>/build-log.md` per child completion. The filesystem write batches same-turn (read-precedes-write) with the step 4 Linear comment, the step 5 state transition, and the step 7 parent comment/transition, per `write-discipline.md`. (Covered by `test_wrap_appends_build_log`.)
- [ ] **AC-2:** Each build-log section contains, in the template order defined in §API contract: child ID + title heading (optionally suffixed `(re-wrap, supersedes prior)`), ISO-8601 commit-timestamp date, test pass/fail counts (with explicit empty-state token), commit count + short-SHA list (with explicit empty-state token), branch name, files-changed list capped at 20 with overflow line, build-reviewer decisions list (with explicit empty-state token), deferred follow-ups list (with explicit empty-state token). (Covered by `test_wrap_appends_build_log` and `test_wrap_renders_empty_states`.)
- [ ] **AC-3:** `/specify` (step 1 context-load) and `/diagnoser` (on `/verify` FAIL) load the parent's `build-log.md` when present. Absence is not an error — both proceed with empty build-log context. Present-but-malformed is treated as opaque text — no halt, no validation. (Covered by `test_specify_loads_build_log` and `test_diagnoser_loads_build_log`.)
- [ ] **AC-4:** `/retro` (step 1 history-load) consumes `build-log.md` as the primary source for "what was built" summaries. The retro doc cites at least one build-log entry verbatim per child. (Covered by `test_retro_consumes_build_log`.)
- [ ] **AC-5:** `docs/specs/NNNN-<slug>/build-log.md` is **semantically** append-only — every `/wrap` Read-then-Write preserves prior section bytes byte-identical. `/wrap` never rewrites prior sections, never reorders, never removes. A re-invocation for the same child ID appends a new section with `(re-wrap, supersedes prior)` annotation rather than amending the prior one. (Covered by `test_build_log_is_append_only`.)
- [ ] **AC-6:** `docs/templates/spec.md.template` is updated to reference the build-log file in the spec-directory layout (one-line addition under output artifacts, no structural change). (Covered by `test_template_references_build_log`.)
- [ ] **AC-7:** Manual `/wrap <MARKER>-N-K` invocation against a child whose parent has no resolvable spec directory (decomposition.md lookup fails AND branch-name lookup fails) halts `BLOCKED` with the diagnostic "missing parent spec directory for child `<MARKER>-N-K`" using halt-pattern `§missing-context`. (Covered by `test_wrap_halts_on_missing_parent_dir`.)
- [ ] **AC-8:** `/build` finalize phase writes `.ralph/<MARKER>-N-K/reviewer-findings.json` (structured findings from the build-reviewer agent) before Task-invoking `/wrap`. The file persists through `/wrap`'s read. (Covered by `test_build_persists_reviewer_findings`.)
- [ ] **AC-9:** Partial-failure recovery: when filesystem-write succeeds and Linear MCP fails within the same-turn batch, `/wrap --resume-merge` skips the filesystem append (idempotency check by child ID + commit timestamp of last section) and retries Linear writes only. No duplicate section. (Covered by `test_wrap_resume_merge_no_duplicate`.)

## Failing-test seed

Each test is a `[unit]` test against the skill's same-turn-batch contract. Tests assert against rendered output of `/wrap`'s write batch using a synthetic-fixture harness; no e2e tier needed (no user-facing AC; SOL-46 covers Playwright E2E for user-facing AC).

- `test_wrap_appends_build_log` — `[unit]` — invokes `/wrap` against a synthetic child fixture; asserts `docs/specs/<fixture-slug>/build-log.md` exists post-wrap and contains a section with the expected heading shape and all 8 template fields. Covers AC-1, AC-2 (happy path).
- `test_wrap_renders_empty_states` — `[unit]` — invokes `/wrap` against a fixture where reviewer-findings.json contains zero findings, fix_plan.md has no `[defer]` lines, and the child branch has 0 new commits; asserts each affected field renders its explicit empty-state token (`none`, `none`, `0 (no new commits)`). Covers AC-2 (empty-state contract).
- `test_build_log_is_append_only` — `[unit]` — runs `/wrap` against the same fixture twice with different child IDs; asserts the first section is byte-identical post-second-run and the second is appended after it. Then runs a third time with the **same** child ID as run 1; asserts the first section is still byte-identical, the third section is appended at EOF, and its heading carries `(re-wrap, supersedes prior)`. Covers AC-5.
- `test_specify_loads_build_log` — `[unit]` — invokes `/specify --continue` against a parent fixture whose spec directory contains a pre-seeded `build-log.md`; asserts the build-log content appears in `/specify`'s step-1 context-load surface (probed via the four-hat critique input set). Covers AC-3 (specify half).
- `test_diagnoser_loads_build_log` — `[unit]` — invokes the `/diagnoser` agent against a parent fixture with a pre-seeded `build-log.md` and a synthetic AC-failure input; asserts the agent's structured output contains a `## Build history` block citing the build-log. Covers AC-3 (diagnoser half).
- `test_retro_consumes_build_log` — `[unit]` — invokes `/retro` against a parent fixture with a pre-seeded `build-log.md` containing two child entries; asserts the rendered retro doc contains verbatim quotes from at least one section per child. Covers AC-4.
- `test_template_references_build_log` — `[unit]` — asserts `docs/templates/spec.md.template` contains a line referencing `build-log.md` under the spec-directory layout section. Covers AC-6.
- `test_wrap_halts_on_missing_parent_dir` — `[unit]` — invokes `/wrap <MARKER>-N-K` with a child ID whose parent spec directory cannot be resolved; asserts `/wrap` returns `BLOCKED` with halt-pattern `§missing-context` and the canonical diagnostic. Covers AC-7.
- `test_build_persists_reviewer_findings` — `[unit]` — invokes `/build` finalize phase against a fixture; asserts `.ralph/<MARKER>-N-K/reviewer-findings.json` exists with valid JSON containing the reviewer agent's structured findings. Covers AC-8.
- `test_wrap_resume_merge_no_duplicate` — `[unit]` — simulates a partial-failure (filesystem-write succeeded, Linear-write failed); invokes `/wrap <MARKER>-N-K --resume-merge`; asserts no second build-log section is appended for the same child ID + commit timestamp, and Linear writes retry. Covers AC-9.

**Fixture-harness shape** (defining minimum for `/plan` decomposer to route tests):
- A `tests/fixtures/wrap-child/` directory containing: a fake `docs/specs/NNNN-<slug>/` parent dir, a fake `.ralph/<MARKER>-N-K/` with `reviewer-findings.json` and `fix_plan.md`, a fake git branch range (or commit-list mock), and a Linear MCP mock that returns canned responses. The exact harness layout is a `/plan` decomposer concern; this spec commits only to the **inputs** the harness must provide (per the carrier-files table) and the **outputs** each test asserts against.

## Related research findings

None — workflow-internal change minted from `~/.claude/plans/i-have-questions-regarding-fluttering-meerkat.md`. `/discovery` Phase 2 was skipped via the documented shortcut at v1.0.0 constitution-seed time.

## Clarifications

Appended by /specify step 5 after the clarify-walker pass. Surfaces and resolutions:

### Edge cases — empty-field rendering
**Q:** What does each section field render when the source data is absent / not-applicable?
**A:** Explicit empty-state tokens per the §API contract render rules: `tests:` → `not re-run (resume-merge)`; `commits:` → `0 (no new commits)`; `build-reviewer decisions:` → `none` (clean review) or `n/a (manual /wrap)` (no /build ran); `deferred follow-ups:` → `none`. AC-2's "all eight fields populated" is enforced via these tokens.

### Edge cases — re-wrap heading disambiguation
**Q:** When `/wrap` is re-invoked for the same child ID, both sections sit in the file with identical headings. How do consumers (and humans) tell them apart?
**A:** The re-wrap heading carries a suffix `— (re-wrap, supersedes prior)`. Consumers (per the read contract) treat the latest section per child ID as authoritative. The annotation is the human-visible signal; machine consumers parse latest-by-position.

### Edge cases — first-create vs subsequent-append dispatch
**Q:** Does the same-turn batch use `Write` (full file replace) on first wrap and `Edit` on subsequent wraps? AC-5 append-only invariant turns on this.
**A:** Always `Read` (if exists) + `Write` (full prior content + new section). Never `Edit`. Append-only is a semantic invariant (prior bytes preserved byte-identical), not a tool-call shape.

### Edge cases — founder hand-edit between wraps
**Q:** If a founder hand-edits `build-log.md` (modifies a prior section, deletes a section, breaks the header), what does the next `/wrap` do?
**A:** `/wrap` reads the current content, composes a new section, writes the concatenation. Manual edits are preserved as-is in the prior content; the new section is appended at EOF. /wrap does not validate, halt on, or merge manual edits. Founder owns the consequences.

### Edge cases — present-but-malformed file on consumer read
**Q:** What do `/specify`, `/diagnoser`, `/retro` do when `build-log.md` is present but malformed?
**A:** Treat as opaque text. No header validation, no section-shape parsing, no halt. Partial content is still useful; consumers degrade gracefully.

### Migration — historical reconstruction
**Q:** Parents that wrapped children before SOL-42 ships have no `build-log.md`. How are they backfilled?
**A:** They aren't, in v0.1. Consumers tolerate absence per AC-3 ("absence is not an error"). A reconstruction tool from Linear comments + git log is a v1.1 follow-up tracked in §Open Questions.

## Open Questions

Deferred items with rationale. /build mirrors these into `fix_plan.md` marked `[defer]` for the relevant child where applicable.

- **Tamper detection** — header is a comment, not a guard. v1.1: trailing checksum or signed-section marker so /wrap can detect founder corruption and halt instead of appending into a corrupted file. Rationale: low-frequency event in v0.1 (founder respects the "do not hand-edit" header most of the time); the deferred cost is "rare silent corruption" which the founder can fix by hand-cleanup.
- **Advisory file-lock for concurrent /wrap** — v0.2 (concurrency support arrives with subagent parallelism). Rationale: v0.1 single-wrap-at-a-time per CLAUDE.md §Session discipline; the failure mode is documented as founder-responsibility (§DX section).
- **Outline-navigable date-in-heading** — date stays in the bullet block in v0.1. v1.1 polish: `## <MARKER>-N-K — <child title> — YYYY-MM-DD` makes the outline view chronologically navigable. Rationale: re-ordering bullets to heading-form changes the contract surface; non-trivial to migrate older sections; defer.
- **Fix-child traceability fields** — fix-children produced by `/verify` pass through normal `/wrap` and append per the v0.1 template. Optional fields `fix-of: <original child ID>` and `retries-AC: <list>` would make /retro's narrative cleaner. Rationale: no /verify-fix traffic yet in v0.1; defer until /verify ships and the need is evidenced.
- **Structured (JSON / TOML) build-log format** — markdown-only in v0.1. v1.1 candidate if consumer parsing volume warrants. Rationale: no machine parser in v0.1 makes structured format premature; markdown is human-skim-friendly.
- **Cross-parent aggregation view** — v1.1. Rationale: same-parent read scope is sufficient for v0.1 consumers; a "what shipped this week" view requires query infrastructure (or a tool) not yet justified.
- **Per-file summaries in `files changed`** — file list only in v0.1. v1.1 candidate if /retro's "what was built" narrative is insufficient without summaries. Rationale: per-file summaries require an LLM call per file or build-reviewer-derived synthesis; unbounded scope in v0.1.

<!-- Rejected four-hat findings (recorded inline, not in Open Questions per spec template convention):
- four-hat-pm #4 ("merge AC-7 into AC-1"): rejected — halt-card behavior deserves a standalone testable AC because the test surface (BLOCKED + halt-pattern) is materially different from AC-1's happy-path write surface. Keeping AC-7 separate clarifies the failure-mode contract.
- four-hat-user #6 ("rename build-log.md to something more grep-distinctive"): rejected — path-qualified greps (`rg build-log docs/specs/`) are the realistic founder behavior; bare `rg build-log` collisions across a polyglot adopter repo are tolerable.
- four-hat-pm #2 ("split AC-3 into /specify and /diagnoser halves"): rejected — adding `test_diagnoser_loads_build_log` (alongside `test_specify_loads_build_log`) covers the diagnoser half without splitting the AC; both consumers share the same load contract (path derivation + opaque-text tolerance), so one AC reads cleaner than two parallel ones.
- four-hat-pm #8 ("rename §API contract to less-heavyweight vocabulary"): rejected — the section heading is template-driven (per `docs/templates/spec.md.template`'s backend-only variant); changing it here breaks the spec-author cognitive pattern across the cascade. Vocabulary is consistent across specs by design.
-->
