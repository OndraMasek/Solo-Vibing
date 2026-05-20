# `.claude/skills/review/SKILL.md` — v0.2 amendments

**Status:** Patch-ready amendment block. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing` which reconciles against v0.1 byte-for-byte before applying.

**Scope:** add gate-evaluation logic for three `review.*` gates and wire the four-hat objection-coverage check as the cascade's single agent-type hook on `SubagentStop`. The skill's frontmatter, the `/Chains` block (sealed in `child_B_chains_sections.md`'s `/review` Pattern C Group E intermediate row), the four-hat subagent dispatch logic, and the existing manifest-write step carry forward from v0.1 unchanged at the substantive level.

**v0.1 reconciliation pattern:** the executing session reads v0.1's `.claude/skills/review/SKILL.md` and substitutes by purpose ("the pre-flight step" / "the subagent-dispatch step" / "the seal step") rather than by step number. The SubagentStop wiring lands in `.claude/settings.json` (Child 0001-C scope), not in this SKILL — this amendment specifies the predicate the hook script evaluates and the output schema the hook script emits.

---

## Naming reconciliation note

D3.4 §Per-stage gate inventory `/review` row names the three gates `review.provenance`, `review.four-hat-objection-coverage`, `review.ac-list-seal`. The parent `spec.md` AC-8 reads: "evaluates the `review.*` gates per D3.4; the four-hat objection-coverage check fires as the cascade's **single** agent-type hook on `SubagentStop` per D2.2 §Stop / SubagentStop output schema quirk." AC-8 references D3.4 by name; no divergent gate names surface here. The amendment uses D3.4's names verbatim.

---

## Gate evaluation

Three gates fire at `/review`, in firing order per D3.4 §Per-stage gate inventory `/review` row. All gates evaluate before any halt card is composed per D3.4 §Aggregation rules.

```text
GATES_AT_REVIEW = [
  "review.provenance",                  # pre-flight; manifest chain to /specify
  "review.four-hat-objection-coverage", # at-write; SubagentStop hook predicate
  "review.ac-list-seal"                 # at-write; seal_sha256 recomputes
]

for gate in GATES_AT_REVIEW:
    evaluate gate predicates and record per-gate result
    # do NOT short-circuit; all gates evaluate

if any gate has at least one failing predicate:
    compose aggregate halt card per D3.4 §Aggregation rules
    do NOT write the manifest
    exit with halt
else:
    write manifest, including four_hat_doc_id and seal_sha256 fields
    seal /review
```

### Gate 1 — `review.provenance` (pre-flight; manifest chain to `/specify`)

```text
read cascade:run-state from docs/.cascade/run-state.json

# Step 1: parent manifest must be /specify's seal
expected_parent_path ← cascade:run-state.last_completed_stage.postcondition_manifest_path
if expected_parent_path absent or path doesn't resolve to a file:
    FAIL with §provenance-chain-broken
    diagnostic: "expected /specify manifest at <path>; absent"
    continue

# Step 2: recompute manifest sha
recomputed_sha ← sha256 of parent manifest with manifest_sha256 field zeroed
expected_sha   ← cascade:run-state.last_completed_stage.postcondition_manifest_sha256
if recomputed_sha != expected_sha:
    FAIL with §provenance-chain-broken
    diagnostic: f"parent manifest sha mismatch at {expected_parent_path}; expected {expected_sha[:12]}..., got {recomputed_sha[:12]}..."
    continue

# Step 3: parent must be /specify (not /plan or another stage)
parent_outputs ← parse parent manifest's outputs
if parent_outputs.stage != "/specify":
    FAIL with §provenance-chain-broken
    diagnostic: f"/review's upstream must be /specify; got stage='{parent_outputs.stage}' at {expected_parent_path}"
```

Halt code: `§provenance-chain-broken`. Recovery: `--reconcile` per D2.1 v2.1's chain-recovery pattern.

### Gate 2 — `review.four-hat-objection-coverage` (at-write; SubagentStop hook predicate)

This is the cascade's **single agent-type hook** per D3.4 §What is a gate and D2.2 §Hook/script surface. Per D2.1 v2 §Subagent verification, the parent (`/review`) writes each subagent's manifest from an independently re-read transcript; the gate's predicate is the parent's recompute, **not** the subagent's self-report.

#### Predicate sequence

Four hat subagents are dispatched in parallel via Task-invoke per the v0.1 `/review` skill's subagent-dispatch step: `four-hat-user`, `four-hat-engineer`, `four-hat-pm`, `four-hat-skeptic`. Each subagent terminates with a `SubagentStop` event, at which point this gate's hook script (`.claude/hooks/four-hat-objection-coverage.py`, authored in Child 0001-C) fires per `agent_transcript_path`:

```text
for each hat ∈ {user, engineer, pm, skeptic}:
    transcript_path ← SubagentStop payload's agent_transcript_path for this hat
    transcript      ← read JSONL from transcript_path

    # Predicate 1: priming text present
    priming_text ← parse the first user-message-content from the transcript
    if priming_text does not match the expected four-hat priming for this hat:
        FAIL with §four-hat-incomplete/priming-text-missing
        diagnostic: f"hat={hat}; transcript={transcript_path}; expected priming text missing or malformed"
        continue

    # Predicate 2: structured objections section present
    last_assistant_message ← parse the final assistant-message-content from transcript
    objections_section ← extract block matching "^##? Objections" through next "^##? "
    if objections_section is absent:
        FAIL with §four-hat-incomplete/objections-section-missing
        diagnostic: f"hat={hat}; transcript={transcript_path}; '## Objections' section absent in final assistant message"
        continue

    # Predicate 3: concluding seal line present
    seal_line ← extract block matching "^##? Seal" or final line beginning with "Seal:"
    if seal_line is absent:
        FAIL with §four-hat-incomplete/seal-line-missing
        diagnostic: f"hat={hat}; transcript={transcript_path}; concluding seal line ('## Seal' or 'Seal:') absent"
        continue

    # Predicate 4: structured objection entries parseable
    objections ← parse objections_section per the four-hat-template shape (bullet entries with hat, locus, severity, finding)
    if any objection entry is malformed:
        FAIL with §four-hat-incomplete/objection-entry-malformed
        diagnostic: f"hat={hat}; objection N at line M malformed; expected '- **{{user|engineer|pm|skeptic}}** [{{severity}}] @ {{locus}}: {{finding}}'"
        continue

    # Predicate 5: write subagent manifest from parent's recompute
    write .cascade/manifests/<ticket>-<hat>.json with:
        outputs.objections[] ← parsed objections (the parent's recompute, not the subagent's claim)
        outputs.hat_id ← hat
        outputs.concluded_at ← transcript's final-message timestamp
        input_provenance.transcript_path ← transcript_path
```

After all four hat manifests are written, the gate's at-write predicate evaluates the merged unresolved count:

```text
# Predicate 6: unresolved_count == 0 across all four hats
all_objections ← union of objections[] across the four hat manifests
unresolved ← [obj for obj in all_objections if obj.resolution is absent or obj.resolution == "pending"]

if unresolved is non-empty:
    FAIL with §four-hat-objections-unresolved
    diagnostic: f"{len(unresolved)} unresolved objections across four hats; per-hat counts: user={count_user}, engineer={count_engineer}, pm={count_pm}, skeptic={count_skeptic}; objections listed under §Open Questions in {spec_path}"
```

Halt codes per D3.4 §Per-stage gate inventory `/review` row: `§four-hat-incomplete` (with sub-case in diagnostic — `priming-text-missing`, `objections-section-missing`, `seal-line-missing`, `objection-entry-malformed`), `§four-hat-objections-unresolved`. Pre-existing v0.1 halts where present; apply-time additions where absent (see authoring notes Surfaced item #1).

#### Hook output shape — top-level fields only

The hook script emits the Stop/SubagentStop top-level-fields-only output per D2.2 §Stop / SubagentStop output schema quirk. **No `hookSpecificOutput` wrapper.** Verified on Claude Code v2.0.76 per anthropics/claude-code#15485:

On per-hat failure (any of predicates 1–5):

```json
{
  "decision": "block",
  "reason": "§four-hat-incomplete/<sub-case>: hat=<hat>; transcript=<path>; <one-line diagnostic>. Run /review --continue after addressing."
}
```

On all-hats-pass + unresolved-count zero:

```json
{
  "decision": "approve"
}
```

(`"approve"` is also a top-level field; the hook signals continuation rather than blocking.)

On all-hats-pass but unresolved-count > 0 (predicate 6):

```json
{
  "decision": "block",
  "reason": "§four-hat-objections-unresolved: <N> unresolved objections across four hats; resolve under §Open Questions in <spec_path> and run /review --continue."
}
```

The hook script is `.claude/hooks/four-hat-objection-coverage.py` and lives in Child 0001-C's scope; this SKILL.md amendment specifies what the hook checks and what it returns, not the hook script's filesystem-and-IO scaffolding.

#### Imperative-phrasing carry-forward (F-Int-2 context)

The `reason` field above uses present-tense factual statements with a recovery action ("Run /review --continue after addressing"), per D2.2's "factual phrasing per the hooks-reference guidance, not imperative instructions" pattern. The forcing function is the `decision: block` itself — not the prose of `reason`. The prose's job is to make the halt diagnostic readable; the prose does NOT command the model to do anything. F-Int-2 (per D2.3 v1.2 four-hat review) flagged the ambiguity for Stop hooks generally; SubagentStop here follows the same shape resolution.

### Gate 3 — `review.ac-list-seal` (at-write; `seal_sha256` recomputes)

```text
spec_path        ← parent_outputs.spec_path (the /specify manifest's spec_path)
current_ac_list  ← parse §Acceptance criteria from spec_path
current_ac_sha   ← sha256 of canonicalized AC list per D2.1 v2 §input_provenance.ac_list_sha256

# The /review skill is about to write four_hat_seal_sha256 ← current_ac_sha
# Predicate 1: AC list matches /specify's sealed ac_list_sha256
specify_ac_sha ← parent_outputs.ac_list_sha256
if current_ac_sha != specify_ac_sha:
    FAIL with §four-hat-ac-list-drift
    diagnostic: f"AC list at {spec_path} has changed since /specify sealed; /specify ac_list_sha256={specify_ac_sha[:12]}..., current={current_ac_sha[:12]}...; /review's seal cannot proceed against a moving AC list"

# Predicate 2: every objection's covered_ac references resolve to AC IDs in the current list
all_covered_acs ← union of obj.covered_ac for obj in all_objections
ac_ids ← {ac.id for ac in current_ac_list}
unresolved_refs ← all_covered_acs - ac_ids
if unresolved_refs is non-empty:
    FAIL with §four-hat-ac-list-drift/objection-refs-stale
    diagnostic: f"objections reference AC IDs not in spec's current AC list: {sorted(unresolved_refs)}; spec AC IDs: {sorted(ac_ids)}"
```

Halt code: `§four-hat-ac-list-drift`. Recovery: re-run `/specify <MARKER>-N --unseal` to re-seal against the changed AC list; then re-run `/review`.

---

## Manifest write (on all-gates-pass)

Write the `/review` manifest at `.cascade/manifests/<ticket>-review.json` per D2.1 v2 §`/review` row:

```json
{
  "stage": "/review",
  "ticket": "<MARKER>-<N>",
  "review_sealed_at": "<ISO-8601 timestamp>",
  "outputs": {
    "four_hat_doc_id": "<Linear doc ID>",
    "seal_sha256": "<current_ac_sha — the AC-list hash at review seal time>",
    "objections_resolved": [
      {"hat": "...", "locus": "...", "severity": "...", "finding": "...", "resolution": "...", "covered_ac": ["AC-N"]},
      ...
    ],
    "unresolved_count": 0,
    "subagent_manifest_paths": [
      ".cascade/manifests/<ticket>-user.json",
      ".cascade/manifests/<ticket>-engineer.json",
      ".cascade/manifests/<ticket>-pm.json",
      ".cascade/manifests/<ticket>-skeptic.json"
    ]
  },
  "input_provenance": {
    "spec_path":                 "docs/specs/<NNNN>-<slug>/spec.md",
    "ac_list_sha256":            "<sha>",
    "parent_manifest_path":      ".cascade/manifests/<ticket>-specify.json",
    "parent_manifest_sha256":    "<sha>"
  },
  "manifest_sha256": "<recomputed-zero-self-field>"
}
```

The four subagent manifests at `.cascade/manifests/<ticket>-{user,engineer,pm,skeptic}.json` are inputs to `/review`'s seal (written by the parent during Gate 2 evaluation), not outputs in the chain sense; they remain on disk as audit history per D2.1 v2 §Subagent verification.

After write, update `cascade:run-state.json`'s `last_completed_stage` to point at this manifest path and sha.

---

## Cross-references

- **D2.1 v2 §`/review` row** — the upstream manifest schema (`four_hat_doc_id`, `seal_sha256`, `objections_resolved[]`, `unresolved_count`) and verifier-predicate baseline; D3.4's three gates layer on top.
- **D2.1 v2 §Subagent verification (F-1 fix)** — the parent-writes-subagent-manifest pattern this skill's Gate 2 implements verbatim.
- **D2.1 v2 §Provenance binding (F-2 fix)** — `seal_sha256` as the AC-list-hash-at-seal-time that downstream stages chain against; Gate 3 establishes this.
- **D2.2 §Stop / SubagentStop output schema quirk** — top-level-fields-only `{"decision": "block", "reason": "..."}` shape; Gate 2's hook script emits this verbatim.
- **D2.2 §Hook/script surface** — the agent-hook reservation for the four-hat coverage check; this amendment is the binding consumer.
- **D2.3 v1.2 four-hat review §F-Int-2** — the factual-phrasing-not-imperative pattern for Stop-hook `reason` strings; Gate 2's hook output shape follows the resolution.
- **D3.4 §Per-stage gate inventory `/review`** — the three gates' firing order and predicate references.
- **D3.4 §What is a gate** — the agent-vs-command hook taxonomy; this skill's Gate 2 is the cascade's single agent-type gate.
- **D3.4 §Aggregation rules** — all-gates-evaluate, single-card-aggregate semantics applied to /review's seal halt.
- **Child A `spec.md.template`** — the §Acceptance criteria and §Open Questions sections this skill reads.
- **Child A `halt-messages-append.md`** — fourteen new halts; this amendment references by halt-code where present and surfaces three new halt codes as Surfaced item #1.
- **`child_B_chains_sections.md`** Pattern C Group E intermediate (`/review`) — the `/Chains` block for `/review` sealed in a prior session; this amendment's gates land BEFORE the `/Chains` block's Task-invoke-to-`/update-linear`.
- **Child 0001-C** `.claude/hooks/four-hat-objection-coverage.py` — the hook script that wraps Gate 2's predicate as a SubagentStop hook; this amendment specifies what the script checks, the script's IO scaffolding is Child 0001-C's scope.
- **Child 0001-C** `.claude/settings.json` — wires `four-hat-objection-coverage.py` to SubagentStop with matcher on `four-hat-*` agent type names.
- **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-8** — this skill amendment satisfies AC-8 as authored.
