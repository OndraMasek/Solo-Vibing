# `.claude/skills/retro/SKILL.md` — v0.2 amendments

**Status:** Patch-ready amendment block. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing` which reconciles against v0.1 byte-for-byte before applying.

**Scope:** add the `children_gate_outcomes[]` reading logic per D3.4 §Manifest schema additions, the tag-distribution and per-gate-outcome rendering schemas per `decomposition.md` Child 0001-B's row + D3.4 §`/retro` row + AC-12, and the session-discipline retrospective rendering per `child_B_chains_sections.md` Pattern N (Group H) §Within-group transitions list. The single `retro.doc-sealed` gate per D3.4 §Per-stage gate inventory `/retro` row evaluates at-write. The skill's frontmatter, the `/retro`-specific section sequencing (already in v0.1 in some form), the founder-driven discussion prompts, and the `/Chains` block (sealed in `child_B_chains_sections.md` Pattern N Group H) carry forward from v0.1 unchanged at the substantive level.

**v0.1 reconciliation pattern:** the executing session reads v0.1's `.claude/skills/retro/SKILL.md` and substitutes by purpose ("the gate-outcomes section" / "the session-discipline section" / "the seal step"). The substantive deltas are: (a) the gate-outcomes reading logic is new in v0.2 (the read source — `children_gate_outcomes[]` on `/verify` manifests — did not exist in v0.1); (b) the rendering schemas are documented verbatim for `solo-verify` parity; (c) the seal step gains the `retro.doc-sealed` gate evaluator (naming-only standardization; v0.1's seal logic carries forward). Per `decomposition.md` Child 0001-B's row: "tag distribution and per-gate outcome counts."

**`/retro` is informational** per D3.4 §`/retro` row. The skill produces findings, not predicate evaluations. The single `retro.doc-sealed` gate at-write confirms the retro doc was sealed and the Status doc's lessons-line updated — the same v0.1 contract under a canonical name. No new predicate-evaluation complexity.

---

## Naming reconciliation note

D3.4 §Per-stage gate inventory `/retro` row names one gate: `retro.doc-sealed`. The parent `spec.md` AC-12 reads: "`.claude/skills/retro/SKILL.md` reads `children_gate_outcomes[]` from `/verify` manifests, surfaces tag distribution (e.g., 'this milestone shipped 12 children — 9 walking-skeleton, 2 capability-cluster, 1 refactor-spike') and per-gate outcome counts." AC-12 specifies behavior, not gate names; no divergent naming surface. The amendment uses D3.4's single-gate inventory verbatim.

D3.4 framing applies: "No hard gates. `/retro` is informational and produces findings, not predicate evaluations." The single `retro.doc-sealed` gate is at-write and structural — it confirms the seal artifacts exist, not the quality of the retro content. The retro's value comes from the founder reading the rendered summaries and updating future cascade behavior, not from a runtime predicate that judges correctness.

---

## Stage structure

`/retro` is a milestone-level stage. It runs once per milestone seal (after `/verify` has sealed its manifest at `.cascade/manifests/<milestone>-verify.json`) and writes a single manifest at `.cascade/manifests/<milestone>-retro.json` plus the retro doc itself at `docs/specs/<milestone>/retro.md` (or the milestone's equivalent path per `/onboard`'s product-layer mirror).

The skill's output is structured into four sections per `child_B_chains_sections.md` Pattern N (Group H) §Within-group transitions list:

1. **Tag distribution** — count children per strategy (reads `children_gate_outcomes[]`).
2. **Per-gate outcome counts** — count passed vs halted per gate, with halt-code surfacing (reads `children_gate_outcomes[]`).
3. **Session-discipline retrospective** — cost, iteration counts, manual-halt incidents (reads `cascade:run-state` and per-session telemetry).
4. **Next-milestone backlog reflections** — founder-driven; informational; no machinery beyond v0.1's existing prompts.

Each section seal is an advisory PreCompact safe boundary per D2.3 v1.3 §Within-group safe boundaries Group H row. Sections render sequentially in the retro doc; the renderer reads the full `/verify` manifest once and threads the per-child entries through sections 1 and 2.

The amendment specifies the rendering schemas for sections 1, 2, and 3 verbatim below. Section 4 carries forward from v0.1 unchanged.

---

## Section 1 — Tag distribution rendering

### Read source

```text
verify_manifest_path ← .cascade/manifests/<milestone>-verify.json
verify_manifest ← read verify_manifest_path; halt §provenance-chain-broken if absent or sha mismatch
gate_outcomes ← verify_manifest.outputs.children_gate_outcomes

# children_gate_outcomes[] schema per D3.4 §Manifest schema additions:
# each entry has: child_id, strategy, gate, status, predicates_evaluated[],
#                 evidence_paths[], evaluated_at; refactor-spike entries also have
#                 seal_pass_set_count, verify_pass_set_count; hybrid recursed entries
#                 carry gate="(recursive)" with grandchildren_count.
```

### Render logic

```text
# Bucket entries by strategy
by_strategy ← defaultdict(int)
for entry in gate_outcomes:
    by_strategy[entry.strategy] += 1

# Strategy order is the canonical D3.1 ordering for deterministic rendering
STRATEGY_ORDER = [
    "walking-skeleton", "api-boundary", "capability-cluster",
    "refactor-spike", "hybrid"
]

# Render in canonical order, omitting zero-count strategies
parts ← []
total ← sum(by_strategy.values())
for strategy in STRATEGY_ORDER:
    if by_strategy[strategy] > 0:
        parts.append(f"{by_strategy[strategy]} {strategy}")

# Composition
if not parts:
    section_body ← "No children evaluated for this milestone."
elif len(parts) == 1:
    section_body ← f"This milestone shipped {total} children — {parts[0]}."
else:
    # Oxford-comma-style join
    section_body ← f"This milestone shipped {total} children — {', '.join(parts[:-1])}, {parts[-1]}."
```

### Example output

For a milestone with 9 walking-skeleton children, 2 capability-cluster, 1 refactor-spike:

```text
## Tag distribution

This milestone shipped 12 children — 9 walking-skeleton, 2 capability-cluster, 1 refactor-spike.
```

The phrasing matches the AC-12 example verbatim per parent spec.

For a milestone with only walking-skeleton children:

```text
## Tag distribution

This milestone shipped 8 children — 8 walking-skeleton.
```

For a milestone where `/verify` halted before sealing (no `children_gate_outcomes[]` present): the section is not rendered; instead, an upstream halt at `retro.doc-sealed`'s Gate 1 (provenance chain to `/verify`) fires.

---

## Section 2 — Per-gate outcome counts rendering

### Read source

Same `gate_outcomes` array from Section 1. Section 2 buckets by `gate` rather than by `strategy`.

### Render logic

```text
# Bucket entries by gate name; track per-gate pass/halt counts
by_gate ← defaultdict(lambda: {"passed": 0, "halted": [], "evidence_sample": None})
for entry in gate_outcomes:
    if entry.status == "passed":
        by_gate[entry.gate]["passed"] += 1
        if by_gate[entry.gate]["evidence_sample"] is None and entry.evidence_paths:
            by_gate[entry.gate]["evidence_sample"] = entry.evidence_paths[0]
    elif entry.status == "halted":
        by_gate[entry.gate]["halted"].append({
            "child_id":      entry.child_id,
            "halt_code":     entry.halt_code,
            "halt_diagnostic": entry.halt_diagnostic
        })
    # Note: in v0.2, only "passed" entries appear on a sealed /verify manifest per
    # D3.4 §Manifest schema additions (halted children produce no manifest entry; failures
    # live in .cascade/halt/<child>-verify.txt). The "halted" branch above is a v0.2.x
    # forward-compat; in v0.2 it never fires from /verify-manifest data.

# Gate-name order: canonical D3.4 ordering, then any v0.2.x additions trailing
GATE_ORDER = [
    "verify.perceptual-evidence", "verify.invariance"
]
# Append any unknown gate names from the data in alphabetical order (forward-compat)
extra_gates ← sorted(set(by_gate.keys()) - set(GATE_ORDER))

# Render per-gate lines
lines ← []
for gate in GATE_ORDER + extra_gates:
    if gate not in by_gate:
        continue
    counts ← by_gate[gate]
    total_for_gate ← counts["passed"] + len(counts["halted"])
    passed ← counts["passed"]
    if len(counts["halted"]) == 0:
        line ← f"- {passed}/{total_for_gate} children passed `{gate}`."
    else:
        line ← f"- {passed}/{total_for_gate} children passed `{gate}`; "
        line += f"{len(counts['halted'])} halted "
        # halt-code aggregation: deduplicate by halt-code, list one per code
        halt_codes_seen ← []
        for halt in counts["halted"]:
            if halt["halt_code"] not in halt_codes_seen:
                halt_codes_seen.append(halt["halt_code"])
        if len(halt_codes_seen) == 1:
            line += f"on `{halt_codes_seen[0]}`."
        else:
            line += f"on " + ", ".join(f"`{hc}`" for hc in halt_codes_seen[:-1])
            line += f", and `{halt_codes_seen[-1]}`."
    lines.append(line)

# Add an evidence-sample appendix if any passed entries had evidence
evidence_lines ← []
for gate in GATE_ORDER + extra_gates:
    if gate not in by_gate: continue
    sample ← by_gate[gate]["evidence_sample"]
    if sample:
        evidence_lines.append(f"  - `{gate}` sample evidence: `{sample}`")
```

### Example output

For a milestone with 11 walking-skeleton children all passed, 1 halted on `§perceptual-evidence-missing/byte-stability-failed`:

```text
## Per-gate outcome counts

- 11/12 children passed `verify.perceptual-evidence`; 1 halted on `§perceptual-evidence-missing/byte-stability-failed`.

Evidence samples:
  - `verify.perceptual-evidence` sample evidence: `docs/specs/0042-login/perceptual/post-login.png`
```

The phrasing matches the AC-12 example verbatim per parent spec.

For a milestone with mixed strategies (perceptual + invariance gates):

```text
## Per-gate outcome counts

- 8/8 children passed `verify.perceptual-evidence`.
- 3/3 children passed `verify.invariance`.

Evidence samples:
  - `verify.perceptual-evidence` sample evidence: `docs/specs/0050-checkout/perceptual/order-success.png`
  - `verify.invariance` sample evidence: `docs/specs/0048-billing-cleanup/invariance/pass-set-at-seal.txt`
```

### Halt-case rendering note

Since v0.2's `/verify` writes no manifest entry for halted children (per D3.4 §Manifest schema additions: "halted children produce no manifest entry; failures live in `.cascade/halt/<child>-verify.txt`"), Section 2 rendering in v0.2 operates on a fully-passed `children_gate_outcomes[]`. To surface halt cases at `/retro` time, the skill additionally walks `.cascade/halt/<milestone>-*-verify.txt` files (where the wildcard covers per-child halt artifacts) and composes a separate "Halted children" subsection per child halt diagnostic. Per the failing-test seed `test_retro_skill_surfaces_per_gate_outcomes`, the test asserts the rendering for the halt case includes the halt code; the implementation reads from both the sealed manifest's children-outcomes array (for passed children) and the per-child halt files (for halted children). Forward-compat: when v0.2.x extends `children_gate_outcomes[]` to include halted entries, the rendering logic above already handles that case.

---

## Section 3 — Session-discipline retrospective rendering

### Read source

Per `child_B_chains_sections.md` Pattern N (Group H) §Within-group transitions row: "session-discipline retrospective (cost, iteration counts, manual-halt incidents from `cascade:run-state` and per-session telemetry)." Per Child 0001-C scope, the per-session telemetry is written by `session-end-telemetry.sh` (a SessionEnd hook); this amendment reads from the telemetry artifacts that Child 0001-C produces.

```text
run_state ← read .cascade/run-state.json
telemetry_glob ← .cascade/session/<milestone>-*.jsonl
                   (per-session telemetry written by session-end-telemetry.sh
                    per D2.2 §Critical caveat #4 async-only telemetry)
sessions ← []
for path in glob(telemetry_glob):
    for line in read-lines(path):
        sessions.append(json.parse(line))
        # Each entry: {session_id, group, started_at, ended_at, tokens_in, tokens_out,
        #              cost_usd, iterations (build only), manual_halt (bool),
        #              halt_code? (if manual_halt)}
```

### Render logic

```text
# Aggregate across all sessions for this milestone
total_cost_usd     ← sum(s.cost_usd for s in sessions)
total_tokens_in    ← sum(s.tokens_in for s in sessions)
total_tokens_out   ← sum(s.tokens_out for s in sessions)
group_counts       ← Counter(s.group for s in sessions)
iteration_total    ← sum(s.iterations for s in sessions if s.group == "F" and s.iterations)
manual_halts       ← [s for s in sessions if s.manual_halt]

# Per-group cost roll-up
per_group_cost ← defaultdict(float)
per_group_tokens_in ← defaultdict(int)
for s in sessions:
    per_group_cost[s.group] += s.cost_usd
    per_group_tokens_in[s.group] += s.tokens_in

# Manual-halt incident rendering
halt_incident_lines ← []
for h in manual_halts:
    halt_incident_lines.append(
        f"  - {h.started_at[:10]} group {h.group}: `{h.halt_code or '§cascade-halt'}`"
    )
```

### Example output

```text
## Session-discipline retrospective

This milestone consumed 18 chat sessions across 8 groups.

Cost summary:
  - Total: $11.42 (412k tokens in, 38k tokens out)
  - Group F (build + wrap) accounted for 67% of spend ($7.65) and 84% of input tokens.
  - Group D (specify + four-hat) accounted for 18% of spend ($2.05).

Iteration counts (Group F):
  - 47 Ralph iterations across 12 children — 3.9 iter/child average.
  - High: SOL-127 (8 iter, refactor-spike).
  - Low: SOL-119 (1 iter, walking-skeleton smoke-only).

Manual-halt incidents:
  - 2026-05-19 group F: `§kill-received-remote` (SOL-124 wedged Ralph; founder /build-kill)
  - 2026-05-20 group D: `§cascade-halt` (founder paused after four-hat surfaced an unresolvable AC conflict)

No manual halts: (this line replaces the bulleted list above if `manual_halts` is empty)
  - The milestone ran without manual intervention.
```

### Failure modes

- **Telemetry artifacts absent.** The Child 0001-C `session-end-telemetry.sh` is async; some sessions' telemetry may not have flushed before `/retro` reads. Render section 3 with a banner: "Session telemetry incomplete — N sessions enumerated; expected M per `cascade:run-state.group_completion_count[]`. Numbers below are lower bounds."
- **Cost telemetry malformed.** If a single telemetry entry fails to parse, skip it; record skipped-entry count in a footer note. Do not halt — `/retro` is informational and partial data is better than no data.

This section's rendering is the closest /retro comes to a perceptual gate. Per `child_B_chains_sections.md` Pattern N footer: "v0.2 does not gate Group H beyond `/retro`'s own internal section completion." Numbers in this section are advisory for founder course-correction, not enforcement.

---

## Section 4 — Next-milestone backlog reflections

Carries forward from v0.1 unchanged. v0.1's `/retro` already prompts the founder for:

- Items to add to the backlog for the next milestone.
- Items to defer to a future product cycle.
- Items to retire entirely.

The amendment does not change this section. The founder authors freely; the skill captures the founder's text into the retro doc verbatim.

---

## Gate evaluation

One gate fires at `/retro` at-write per D3.4 §Per-stage gate inventory `/retro` row. Gate evaluates just before manifest seal — after Section 4's founder-authored content is captured and the retro doc has been finalised at `docs/specs/<milestone>/retro.md` (or the milestone's product-layer-mirrored path).

```text
GATES_AT_RETRO_AT_WRITE = ["retro.doc-sealed"]

for gate in GATES_AT_RETRO_AT_WRITE:
    evaluate; record per-gate result; do NOT short-circuit
if any gate has failing predicates:
    compose aggregate halt card per D3.4 §Aggregation rules
    do NOT write manifest; exit with halt
else:
    write manifest
    seal /retro
```

### Gate 1 — `retro.doc-sealed` (at-write; D2.1 v2 `/retro` row)

```text
retro_doc_path ← docs/specs/<milestone>/retro.md
# OR the product-layer-mirrored equivalent if /onboard's product layer overrides the path

# Predicate 1: retro doc exists at the expected path and is non-empty
if not file-exists(retro_doc_path):
    FAIL with §retro-doc-unsealed
    diagnostic: f"retro doc absent at {retro_doc_path}; expected after section 4 sealed"
    continue

retro_doc_content ← read(retro_doc_path)
if len(retro_doc_content.strip()) == 0:
    FAIL with §retro-doc-unsealed
    diagnostic: f"retro doc at {retro_doc_path} is empty; sections 1–4 produced no content"
    continue

# Predicate 2: retro doc's four canonical sections are present
expected_section_headings ← [
    "## Tag distribution",
    "## Per-gate outcome counts",
    "## Session-discipline retrospective",
    "## Next-milestone backlog reflections"
]
for heading in expected_section_headings:
    if heading not in retro_doc_content:
        FAIL with §retro-doc-unsealed
        diagnostic: f"retro doc at {retro_doc_path} missing section heading '{heading}'; sections must be rendered before seal"

# Predicate 3: Linear retro doc exists with sealed sha
linear_retro_doc_id ← (created during retro section rendering; tracked in in-memory state)
if linear_retro_doc_id absent:
    FAIL with §retro-doc-unsealed
    diagnostic: f"Linear retro doc id absent from in-memory state; sections must seal the Linear doc"

linear_retro_doc ← linear-mcp's read of doc by linear_retro_doc_id
if linear_retro_doc absent or unreachable:
    FAIL with §retro-doc-unsealed
    diagnostic: f"Linear retro doc id={linear_retro_doc_id} unreachable; cannot verify seal"

linear_retro_sha ← sha256(linear_retro_doc.content)
fs_retro_sha ← sha256(retro_doc_content)
if linear_retro_sha != fs_retro_sha:
    FAIL with §retro-doc-unsealed
    diagnostic: f"filesystem retro doc sha differs from Linear retro doc sha; fs={fs_retro_sha[:12]}..., linear={linear_retro_sha[:12]}..."

# Predicate 4: Status doc lessons-line updated
status_doc_id ← read /onboard's manifest's outputs.status_doc_id
status_doc ← linear-mcp's read of doc by status_doc_id
# The lessons-summary-line is the new summary line that /retro writes per D2.1 v2 §/retro row:
# "Status doc lessons-line updated."
# Expected pattern: a line beginning "## Lessons from milestone <M-N>" or similar marker.
expected_lessons_marker ← f"## Lessons from milestone {milestone_id}"
if expected_lessons_marker not in status_doc.content:
    FAIL with §retro-doc-unsealed
    diagnostic: f"Status doc (id={status_doc_id}) missing '{expected_lessons_marker}'; /retro must update Status before seal"
```

Halt code: `§retro-doc-unsealed`. Recovery: founder ensures sections render fully, the Linear retro doc receives the rendered content, and the Status doc's lessons-summary line is appended; re-runs `/retro` (which is idempotent — re-running renders the same content if the input `/verify` manifest is unchanged).

Per D3.4 §`/retro` row: "Linear retro doc exists with a sealed sha; Status doc lessons-line updated. (D2.1 v2 `/retro` row.)"

---

## Manifest write (on all-gates-pass)

Write the `/retro` manifest at `.cascade/manifests/<milestone>-retro.json` per D2.1 v2 §`/retro` row, extending with the rendered-sections summary fields for D4.6 v1.1's re-derivation per D2.3 v1.3 §`/Chains` contract per-pattern statement (Pattern N row: `/retro`'s manifest is the Group H exit manifest):

```json
{
  "stage": "/retro",
  "milestone_id": "<M-N>",
  "retro_sealed_at": "<ISO-8601 timestamp>",
  "outputs": {
    "summary":                        "/retro for milestone <M-N> aggregated <N> children's gate outcomes across <M> strategies, surfaced <K> session-discipline observations, and produced <L> next-milestone backlog reflections.",
    "findings":                       [
      {"category": "tag-distribution", "content": "<rendered section 1 text>"},
      {"category": "per-gate-outcomes", "content": "<rendered section 2 text>"},
      {"category": "session-discipline", "content": "<rendered section 3 text>"},
      {"category": "next-milestone",    "content": "<rendered section 4 text>"}
    ],
    "arch_updates_proposed":          [
      /* zero or more entries; founder-driven in section 4 */
    ],
    "lessons_summary_line":           "<one-line summary written to Status doc>",
    "retro_doc_path":                 "docs/specs/<milestone>/retro.md",
    "linear_retro_doc_id":            "<linear-doc-id>",
    "fs_retro_sha256":                "<sha>",
    "linear_retro_sha256":            "<sha>",
    "status_doc_lessons_updated_at":  "<ISO-8601 timestamp>",
    "verify_manifest_consumed":       {
      "path":   ".cascade/manifests/<milestone>-verify.json",
      "sha256": "<sha>"
    },
    "telemetry_completeness":         {
      "sessions_enumerated":         <int>,
      "expected_from_run_state":     <int>,
      "complete":                    <bool>
    }
  },
  "input_provenance": {
    "parent_manifest_path":      ".cascade/manifests/<milestone>-verify.json",
    "parent_manifest_sha256":    "<sha>"
  },
  "manifest_sha256": "<recomputed-zero-self-field>"
}
```

Schema rules:

- `outputs.summary` is the single-sentence description D4.6 v1.1 reads for Group H's chat-end card "What just happened" section. Per D2.3 v1.3 §`/Chains` contract Pattern N row: `/retro`'s manifest is the Group H exit manifest.
- `outputs.findings[]` contains four entries, one per section, in canonical order. Each entry's `content` is the rendered section text verbatim (not the underlying data; the rendered prose is what the retro doc carries).
- `outputs.lessons_summary_line` is the single-line summary written to the Status doc per D2.1 v2 §`/retro` row. The Status doc receives this as a new paragraph under a heading like `## Lessons from milestone <M-N>`.
- `outputs.telemetry_completeness` records whether Section 3 rendered from a complete telemetry set or partial; informational for v0.2.x measurement (composes with M-5 from F-Rev-1's deferral).
- `input_provenance.parent_manifest_path` points to `/verify`'s milestone manifest; `parent_manifest_sha256` chains the milestone's exit-manifest sequence.

After write, set `cascade:run-state.last_completed_stage` to point at this manifest path and sha. The chat-end card render at the `/Chains` block's Group H exit (variant `terminal` per `child_B_chains_sections.md` Pattern N block) sets `cascade:run-state.last_completed_group = "H"` and writes `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<milestone>-retro.json"`.

---

## Cross-references

- **D2.1 v2 §`/retro` row** — the upstream manifest schema baseline (findings[], arch_updates_proposed[], lessons_summary_line); this amendment extends with the per-section rendered content, the telemetry-completeness record, and the seal-evidence sha pair.
- **D2.1 v2 §Caller-side verification protocol** — chain-checks on `/verify`'s milestone manifest before Section 1 reads `children_gate_outcomes[]`.
- **D2.2 §Critical caveat #4** — async-only telemetry semantics; informs the §Failure modes "telemetry incomplete" rendering.
- **D2.3 v1.3 §`/Chains` contract Pattern N (Group H)** — the `/retro` manifest is the Group H exit manifest; this amendment writes the schema D4.6 v1.1 re-derives from.
- **D2.3 v1.3 §Within-group safe boundaries Group H row** — the per-section seal advisory PreCompact safe boundary; this amendment specifies the four sections that seal between safe boundaries.
- **D3.1 §Decomposition strategy catalog** — the five canonical strategies Section 1 buckets by.
- **D3.3 §Halt conditions** — `§perceptual-evidence-missing` sub-cases; `§invariance-pass-set-regression`, `§invariance-seal-tampering`, etc., referenced by Section 2's halt-case rendering.
- **D3.4 §Per-stage gate inventory `/retro` row** — the one-gate inventory this amendment implements.
- **D3.4 §Manifest schema additions** — the `children_gate_outcomes[]` schema this amendment reads in Sections 1 and 2.
- **D3.4 §Aggregation rules** — informational only at `/retro`; Sections 1 and 2 aggregate per-child outcomes without precedence ordering (each child stands alone, matching the milestone-level aggregation of `/verify`).
- **D4.6 v1.1 §CLI surface** — reads this amendment's manifest's `outputs.summary` field for Group H re-derivation; halts `§cascade-state-terminal` if invoked at Group H (no next group beyond H).
- **D4.5 §`/retro` reconciliation** — not present in D4.5 per F-Rev-2's queued disposition; `/retro` has no `--reconcile` primitive in v0.2. The recovery is to re-run `/retro` directly (idempotent if the input `/verify` manifest is unchanged) or to manually edit the retro doc + Status doc and re-seal.
- **Child A `solo-config-additions.json`** — no slots `/retro` reads (telemetry config is in `cascade:run-state` per D2.2, not `docs/.solo-config.json`).
- **Child A `halt-messages-append.md`** — `§retro-doc-unsealed` referenced by Gate 1. **Surfaced item:** verify this halt code exists in v0.1 `halt-messages.md` (it should, as part of v0.1's existing `/retro`-seal contract) or in Child A's `halt-messages-append.md`. If absent, the executing Claude Code session adds at apply time.
- **`child_B_chains_sections.md`** Pattern N (Group H) block for `/retro` — sealed in a prior session; this amendment's gate evaluation lands BEFORE the `/Chains` block's group-exit render (chat-end card variant `terminal`).
- **`verify-SKILL-amendments.md`** (Child 0001-B continuation 1) — the `children_gate_outcomes[]` schema this amendment reads; the contract is binding from the `/verify` side.
- **Child 0001-C** `.claude/hooks/session-end-telemetry.sh` — produces the per-session telemetry Section 3 reads; the telemetry schema and `.cascade/session/` path convention are part of Child 0001-C's design.
- **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-12** — this skill amendment satisfies AC-12 as authored.
