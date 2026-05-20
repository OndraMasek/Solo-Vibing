---
name: retro
description: Retrospective document generator. Task-invoked when a parent feature completes — by /verify on a full acceptance pass, or by /wrap when the last child finishes and /verify is disabled — gated on workflow.auto_retro. Compiles cycle-time, what-went-well, what-went-wrong, patterns, and followups into a Linear retrospective document. Optionally mints followup tickets per workflow.followup_tickets. Reachable via /status drill-down. Not user-invoked in normal operation. Manual override `/retro <MARKER>-N` for debugging or re-generation.
---

# retro

Compiles the retrospective when a parent feature completes. Reflection artifact, not interactive. References rules: `naming.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`.

`/retro` is informational per D3.4 §`/retro` row. The skill produces findings, not predicate evaluations. A single `retro.doc-sealed` gate evaluates at-write — it confirms the retro doc was sealed and the Status doc's lessons-line updated. The retro's value comes from the founder reading the rendered summaries and updating future cascade behavior, not from a runtime predicate that judges correctness.

## Trigger

Task-invoked (per audit decision #9 — explicit Task-tool chaining, not a state-transition hook):
- by `/verify` on a full acceptance pass, when `workflow.auto_retro = true`;
- by `/wrap` when the last child completes AND `workflow.verify = false` AND `workflow.auto_retro = true`.

Manual override: `/retro <MARKER>-N` — re-generate the retrospective, or generate one when `workflow.auto_retro = false`.

## Stage structure

`/retro` is a milestone-level stage. It runs once per milestone seal (after `/verify` has sealed its manifest at `.cascade/manifests/<milestone>-verify.json`) and writes a single manifest at `.cascade/manifests/<milestone>-retro.json` plus the retro doc itself at `docs/specs/<milestone>/retro.md` (or the milestone's equivalent path per `/onboard`'s product-layer mirror).

The skill's output is structured into four sections per `child_B_chains_sections.md` Pattern N (Group H) §Within-group transitions list:

1. **Tag distribution** — count children per strategy (reads `children_gate_outcomes[]`).
2. **Per-gate outcome counts** — count passed vs halted per gate, with halt-code surfacing (reads `children_gate_outcomes[]`).
3. **Session-discipline retrospective** — cost, iteration counts, manual-halt incidents (reads `cascade:run-state` and per-session telemetry).
4. **Next-milestone backlog reflections** — founder-driven; informational; no machinery beyond v0.1's existing prompts.

Each section seal is an advisory PreCompact safe boundary per D2.3 v1.3 §Within-group safe boundaries Group H row. Sections render sequentially in the retro doc; the renderer reads the full `/verify` manifest once and threads the per-child entries through sections 1 and 2.

## Behavior

1. **Load full parent history:** parent ticket, all children, spec markdown, four-hat doc, plan review doc(s), all ADRs filed during the cascade, all /wrap session summaries, and `/verify`'s milestone manifest at `.cascade/manifests/<milestone>-verify.json` (chain-checked per D2.1 v2 §Caller-side verification protocol before Section 1 reads `children_gate_outcomes[]`).

2. **Render Section 1 — Tag distribution** per the schema below.

3. **Render Section 2 — Per-gate outcome counts** per the schema below.

4. **Render Section 3 — Session-discipline retrospective** per the schema below.

5. **Capture Section 4 — Next-milestone backlog reflections** (founder-driven; carries forward from v0.1).

6. **Write the retrospective document** at `docs/specs/<milestone>/retro.md` and mirror to Linear as `[<MARKER>-DOC-NNNN] retro: <MARKER>-N <title>` per `naming.md` — NNNN allocated per `counter-allocation.md` (scan Linear for the next `doc` value). Four sections + a cycle-metrics header. Single write per `write-discipline.md`.

7. **Update the Status doc's lessons-line** — append a new paragraph under the heading `## Lessons from milestone <M-N>` carrying the single-line `lessons_summary_line`.

8. **Link from the parent ticket:** add a line to the parent's Artifacts section — "Retro: [<MARKER>-DOC-NNNN]". Single write, batched same-turn with step 6 where the API allows.

9. **Evaluate the `retro.doc-sealed` gate** — see §Gate evaluation below.

10. **Write the `/retro` manifest** at `.cascade/manifests/<milestone>-retro.json` on all-gates-pass. Set `cascade:run-state.last_completed_stage` and `cascade:run-state.last_completed_group_exit_manifest_path` per the `/Chains` block.

11. **Create followup tickets** — only if `workflow.followup_tickets = true` (see `commands/config.md`). For each item surfaced in Section 4 or in compiled "what went wrong" observations:
    - Create a ticket in the `Backlog` project.
    - Title: `[<MARKER>] followup: <one-line summary>` per `naming.md` ticket-title convention.
    - Label: `type:followup` (a `type:*` label, distinct from the `scope:*` state machine in `scope-labels.md` — followup tickets carry no `scope:*` label).
    - Description: extracted context from the retro + a link to the parent retro doc.
    - `relatedTo`: the parent ticket (<MARKER>-N).

    Batched same-turn per `write-discipline.md`, after the retro doc exists so the links resolve. If `workflow.followup_tickets = false`, the items stay as prose in the retro doc — the founder triages manually.

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

For a milestone with only walking-skeleton children:

```text
## Tag distribution

This milestone shipped 8 children — 8 walking-skeleton.
```

For a milestone where `/verify` halted before sealing (no `children_gate_outcomes[]` present): the section is not rendered; instead, an upstream halt at `retro.doc-sealed`'s Gate 1 (provenance chain to `/verify`) fires.

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

## Section 3 — Session-discipline retrospective rendering

### Read source

Per `child_B_chains_sections.md` Pattern N (Group H) §Within-group transitions row: "session-discipline retrospective (cost, iteration counts, manual-halt incidents from `cascade:run-state` and per-session telemetry)." Per Child 0001-C scope, the per-session telemetry is written by `session-end-telemetry.sh` (a SessionEnd hook); this amendment reads from the telemetry artifacts that Child 0001-C produces.

```text
run_state ← read .cascade/run-state.json
telemetry_file ← .cascade/telemetry/sessions.jsonl
                   (single appended JSONL written by session-end-telemetry.sh
                    per D2.2 §Critical caveat #4 async-only telemetry;
                    per Child C apply-time queue item #3)
sessions ← []
for line in read-lines(telemetry_file):
    record ← json.parse(line)
    # Each record: {session_id, group, started_at, ended_at, tokens_in, tokens_out,
    #               cost_usd, iterations (build only), manual_halt (bool),
    #               halt_code? (if manual_halt), active_milestone}
    if record.active_milestone == <milestone>:
        sessions.append(record)
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

## Section 4 — Next-milestone backlog reflections

Carries forward from v0.1 unchanged. v0.1's `/retro` already prompts the founder for:

- Items to add to the backlog for the next milestone.
- Items to defer to a future product cycle.
- Items to retire entirely.

The amendment does not change this section. The founder authors freely; the skill captures the founder's text into the retro doc verbatim. Auditor-voice still applies per `auditor-stance.md` — items are stated as findings with loci, not as criticism.

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

## Same-turn write rules

Per `write-discipline.md`:
- Retro document creation (filesystem + Linear mirror): single write batch.
- Status doc lessons-line update: single write, batched same-turn with retro doc creation where the API allows.
- Parent description update (Artifacts link): single write, batched same-turn.
- `/retro` manifest write at `.cascade/manifests/<milestone>-retro.json`: single write after gate evaluation passes.
- Followup tickets (if enabled): batched same-turn, after the retro doc exists so links resolve.

## Outputs

| Artifact | Location |
|---|---|
| Retrospective document (filesystem) | `docs/specs/<milestone>/retro.md` |
| Retrospective document (Linear) | `[<MARKER>-DOC-NNNN] retro: <MARKER>-N <title>` |
| `/retro` manifest | `.cascade/manifests/<milestone>-retro.json` |
| Status doc lessons-line | Status doc, under `## Lessons from milestone <M-N>` |
| Followup tickets (if enabled) | `Backlog` project, label `type:followup` |
| Parent description link | Parent ticket, Artifacts section |

## Completion status

Per `completion-status.md`:

- `DONE` — retro doc written; manifest sealed; `retro.doc-sealed` gate passed; parent description linked; followup tickets created (if `workflow.followup_tickets = true`).
- `DONE_WITH_CONCERNS` — retro doc written but with reduced fidelity: missing /wrap session summaries (some children skipped /wrap or commented outside the canonical format); telemetry incomplete (Section 3 banner fired); cycle metrics partial because of missing timestamps. Gate still passes if the four canonical headings are present and the seal sha pair matches.
- `BLOCKED` — `retro.doc-sealed` gate failed (halt `§retro-doc-unsealed`); or upstream `/verify` manifest absent or sha mismatch (halt `§provenance-chain-broken`).
- `NEEDS_CONTEXT` — parent ticket not in Done state at invocation (defensive — the caller should ensure it); parent ticket missing entirely; Linear MCP unreachable for `doc`-counter scan per `counter-allocation.md`.

## /Chains

**Pattern:** N (terminal-no-handoff)
**Group:** H
**Within-group transitions:** per-section seal of the retro doc. `/retro`'s output is structured per D3.4 §retro gates (and its own internal sectioning): tag-distribution section (count children per strategy from `children_gate_outcomes[]` read from `/verify` manifests); per-gate outcome counts (e.g., "11/12 children passed `verify.perceptual-evidence`; 1 halted on `§perceptual-evidence-missing/byte-stability-failed`"); session-discipline retrospective (cost, iteration counts, manual-halt incidents from `cascade:run-state` and per-session telemetry); next-milestone backlog reflections. Each section seal is an advisory PreCompact safe boundary (per D2.3 v1.3 §Within-group safe boundaries Group H row).
**Group exit trigger:** retro seal — all retro sections complete; `/retro`'s manifest at `.cascade/manifests/<milestone>-retro.json` written; the retro doc itself written at `docs/specs/<milestone>/retro.md` (or the milestone's equivalent path per `/onboard`'s product-layer mirror).
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant **`terminal`**. The terminal variant has no handoff-prompt fence (no copy-paste step needed; the cascade has reached its terminal); the "What's next" section reads: "Next: open a new spec via `/specify` in a new chat to begin the next feature." After render, set `cascade:run-state.last_completed_group = "H"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<milestone>-retro.json"`, flush, write `.cascade/handoff/last.md` (for symmetry — D4.6 v1.1's `solo-cascade resume` halts §cascade-state-terminal if invoked at this point, surfacing "start a new feature via `/specify`" as the recovery; the on-disk `last.md` carries the same terminal-variant content for founder reference).
**Next group entry:** **none** (terminal). The milestone is complete; the cascade has reached the end of its v0.2 traversal.
**Auto-fire compact handling:** not applicable. Group H runs in chat-Claude; no live PreCompact hook.
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<milestone>-retro.json`. The retro doc itself at `docs/specs/<milestone>/retro.md` is the perceptual artifact (per D3.3 if Group H's strategy is treated as walking-skeleton-shaped for its own perceptual gate; v0.2 does not gate Group H beyond `/retro`'s own internal section completion).

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
- **Child A `halt-messages-append.md`** — `§retro-doc-unsealed` referenced by Gate 1. If absent from v0.1 `halt-messages.md` or Child A's append, surface as a finding.
- **`verify-SKILL-amendments.md`** (Child 0001-B continuation 1) — the `children_gate_outcomes[]` schema this amendment reads; the contract is binding from the `/verify` side.
- **Child 0001-C** `.claude/hooks/session-end-telemetry.sh` — produces the per-session telemetry Section 3 reads; the telemetry schema and `.cascade/session/` path convention are part of Child 0001-C's design.
- **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-12** — this skill amendment satisfies AC-12 as authored.

## Notes

**Why /retro stays a skill** (audit "Skills that stay skills" list). /retro is a compilation skill with real logic — history load, multi-section rendering, manifest seal with gate evaluation, conditional ticket minting. It is not a thin deterministic action and not a specialist invoked by another skill; it stays a skill that /verify and /wrap Task-invoke.

**Task-invoked, not auto-fired.** Pre-extraction /retro "auto-fires on parent → Done" via a Linear state transition. Per audit decision #9 (no hooks in v0.1; explicit Task-tool chaining), /retro is Task-invoked — by /verify on a full pass, or by /wrap when /verify is disabled. The `workflow.auto_retro` knob gates whether that Task-invocation happens; with it `false`, /retro is manual-only.

**Informational, not predicate-gating.** The single `retro.doc-sealed` gate is at-write and structural — it confirms the seal artifacts exist, not the quality of the retro content. The retro's value comes from the founder reading the rendered summaries and updating future cascade behavior, not from a runtime predicate that judges correctness.

**Cycle metrics are most actionable over time.** After 5–10 features, patterns emerge. v0.1 records; v0.2 may aggregate across retros.

**What-went-wrong is auditable, not blame** — per `auditor-stance.md`. ADR-reversal halts, test failures during /wrap, scope-breach catches all surface here as facts with loci, not as criticism.

**The Followups section is the most likely to be actioned.** TODOs and refactors that emerged during build but didn't fit the spec — captured here, they become future /specify candidates. The `workflow.followup_tickets` knob decides whether they're auto-minted as Backlog tickets or left as prose for manual triage.

**Auto-filed ADRs** (`Status: Accepted-Autonomous`) are listed for retroactive ratification. A v0.2 sweep skill can promote them to `Accepted` after retro review.

## Open questions (deferred to v1.1+)

- **Cross-retro aggregation.** v0.1 records per-feature metrics; v0.2 may aggregate trends across retros (cycle-time drift, recurring halt types).
- **Halt-messages pattern coverage for /retro.** /retro halts only on `§retro-doc-unsealed` (structural seal failure) and `§provenance-chain-broken` (upstream `/verify` manifest absent). Both are standard cascade halt codes; no new template growth needed for v0.2.
- **Followup-ticket dedup.** If /retro runs twice on the same parent (manual re-generation), step 11 would mint duplicate followup tickets. v0.1 leaves this to founder care; v1.1 could check `relatedTo` for existing `type:followup` tickets first.
