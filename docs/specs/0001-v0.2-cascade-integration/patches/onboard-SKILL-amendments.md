# `.claude/skills/onboard/SKILL.md` — v0.2 amendments

**Status:** Patch-ready amendment block. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing` which reconciles against v0.1 byte-for-byte before applying.

**Scope:** the v0.1 step 4.5 (project-creation) is replaced with the six-project + Status-doc creation per D1 §Linear product layer + §`/onboard` changes; a new step 7 elicits `workflow.default_strategy` from the founder and writes it to `docs/.solo-config.json` per D3.1 §`/onboard` product-level default; two `onboard.*` gates per D3.4 §Per-stage gate inventory `/onboard` row evaluate at-write. Steps 1, 2, 3, 4, 5, 6, 8 (Project Instructions paste-block render per D2.3 v1.3 §`/onboard` integration point), and 9 (chat-end card render per D2.3 v1.3 §`/Chains` contract Pattern T) carry forward from v0.1 + v1.3 unchanged at the substantive level; this amendment renumbers them around the new step 7.

**v0.1 reconciliation pattern:** the executing session reads v0.1's `.claude/skills/onboard/SKILL.md` and substitutes by purpose ("the project-creation step" → step 2 below; "the north-star seeding subroutine" → step 3 below; "the Project Instructions paste-block render" → step 8 below) rather than by literal step number. v0.1's step numbering may differ from this amendment's — the substitution is structural. Per `decomposition.md` Child 0001-B's row, the substantive deltas are: (a) project-creation expands from three projects to six per D1; (b) Status doc creation lands under the Product project; (c) `docs/.solo-config.json` write gains the `marker`, `linear.project_naming`, and `workflow.default_strategy` keys; (d) the two `onboard.*` gates fire before manifest seal.

**This amendment closes Child 0001-B's design phase for `/onboard`.** After this session: `/onboard` and `/specify` (the prior session's amendment) compose end-to-end on `workflow.default_strategy` — `/onboard` writes the slot (this session, step 7); `/specify` step 1 reads it as the proposal seed (Child 0001-B continuation 0 amendment). The wiring-deferred pattern from parent spec Open Question 4 is fully resolved without further skill amendments.

---

## Naming reconciliation note

D3.4 §Per-stage gate inventory `/onboard` row names two gates: `onboard.linear-projects` and `onboard.config-write`. The parent `spec.md` AC-13 reads: "creates the **six** Linear projects per D1 (Product / Architecture / Design / Milestones / Backlog / Done), creates the Status document under the Product project, writes `docs/.solo-config.json` with `marker` populated, and includes an **optional** product-level default strategy slot (per D3.1 §`/onboard` product-level default — slot is optional, flows through to first `/specify` if set)." AC-13 references D3.4 by behavior and D3.1 by slot semantics; no divergent gate names surface. The amendment uses D3.4's two-gate inventory verbatim — `onboard.linear-projects` covers all six-project + Status-doc creation; `onboard.config-write` covers the `docs/.solo-config.json` write (including the `workflow.default_strategy` slot, populated or empty).

The `workflow.default_strategy` elicitation in step 7 is part of `onboard.config-write`'s predicate set — the gate's predicate accepts both a populated and an empty value (the slot is optional per D3.1; the gate validates structural correctness of the JSON, not the strategy enum value). A founder who selects "skip" at step 7 produces a valid `workflow.default_strategy: ""` write that `onboard.config-write` passes.

---

## /onboard step sequence amendments

The v1.3 §`/onboard` integration point committed an eight-step sequence (step 7 = Project Instructions paste; step 8 = chat-end card render). This amendment inserts a new step 7 — the `workflow.default_strategy` elicitation — between v1.3's step 6 (Initialise Status doc) and v1.3's step 7 (Project Instructions render), pushing the latter two to steps 8 and 9 respectively. The resulting sequence is nine steps.

### v0.2 `/onboard` step sequence (post this amendment)

1. **Determine project-name mode.** Scan the chosen Linear team for existing projects named `Product`, `Architecture`, `Backlog`, `Done`. If any exist, switch to **prefix mode** (write `linear.project_naming = "prefixed"` to the to-be-written `docs/.solo-config.json`; defer the write itself to step 6 + step 7's joint config-write). Per D0.1 §Multi-product Linear teams and D1 §`/onboard` changes step 1.
2. **Create the six projects + Status doc.** Per D1 §Linear product layer:
   - Plain mode: `Product`, `Architecture`, `Design`, `Milestones`, `Backlog`, `Done` + Status under Product.
   - Prefix mode: `[<MARKER>] Product`, `[<MARKER>] Architecture`, `[<MARKER>] Design`, `[<MARKER>] Milestones`, `[<MARKER>] Backlog`, `[<MARKER>] Done` + Status under `[<MARKER>] Product`.

   The marker is from the founder's earlier marker elicitation (v0.1 contract carries forward) or — for amended fork — read from any pre-existing `docs/.solo-config.json`. The product label namespace (`product:<MARKER>` on every cascade-created ticket) is registered with the Linear team at this step. Per D1 §`/onboard` changes step 2.
3. **Seed Product with founder's north-star.** Reuse the **v0.1 north-star seeding subroutine** (formerly v0.1 step 7; the F-Int-5 disposition retires the numeric reference in D1 §`/onboard` changes step 3 in favor of this descriptive one). Interactive flow: founder authors the problem statement, target user, target shape, non-goals, distribution posture; the skill writes the `[<MARKER>-DOC-NNNN] product: north-star` document under the Product project. Per D1 §Linear product layer Product subsection.
4. **Seed Design with founder's design-system if applicable.** Skip for non-UI products. Founder-supplied seed; the skill writes the `[<MARKER>-DOC-NNNN] design: design-system` document under the Design project. Per D1 §Linear product layer Design subsection.
5. **Seed Milestones with placeholder M-1.** One Linear issue under the Milestones project: title `[<MARKER>] M-1: first deliverable`; description: "placeholder — refine at `/discovery` or `/specify`." Per D1 §Linear product layer Milestones subsection.
6. **Initialise Status doc with "no work in progress."** The single Linear document under the Product project, the 30-second read per D1 §Status. Initial content sets `Current milestone: M-1 (placeholder)`, all gates "pending", `What works`, `What's broken`, `What's next` empty. Per D1 §Linear product layer Status subsection.
7. **NEW (this amendment): Elicit `workflow.default_strategy` from the founder.** Present the canonical five strategies plus a "skip" option:

   ```text
   Optional: Pick a default decomposition strategy for this product. /specify
   will use this as its initial proposal for the first feature; you can override
   per spec, and subsequent features may diverge.

     1. walking-skeleton    — one playable increment per milestone
                              (end-user products)
     2. api-boundary        — one API boundary delivered per milestone
                              (libraries, services)
     3. capability-cluster  — one user-visible capability per milestone
                              (apps that ship capabilities, not surfaces)
     4. refactor-spike      — invariance-preservation work
                              (no new functionality)
     5. hybrid              — composes per-child; defer per-feature
     6. skip                — no product-level default

   Selection (1–6):
   ```

   On selection 1–5, write the corresponding enum value to `docs/.solo-config.json`'s `workflow.default_strategy` field (step 7's job is the elicit + populate; step 7 composes with step 6's `docs/.solo-config.json` initial-write into a single joint write). On selection 6 (skip), write the empty string `""`. The empty string is the v0.1-shipped default per Child A's `solo-config-additions.json`; the read-but-tolerate-empty pattern in `/specify` step 1 (amended in Child 0001-B continuation 0) handles this gracefully.

   Per D3.1 §`/onboard` product-level default; parent spec Open Question 4; Child 0001-B continuation 0's `/specify` step 1 amendment.

8. **Render the Project Instructions paste-block and prompt the founder to paste.** Per D2.3 v1.3 §`/onboard` integration point and §Project Instructions block. The skill renders the v1.3-specified paste-block content (the eight-group framing, the chat-start protocol, the recovery paths), prints it inside a fenced code block prefixed with "Paste this into Claude.ai → Project → Instructions:", and waits for the founder's confirmation (a chat message containing a recognised acknowledgment phrase — implementation detail of the wait UX is owned by SOL-58 per D2.3 v1.2 §SOL-58's remaining scope). On confirmation, write the timestamp to `cascade:run-state.project_instructions_pasted_at`. Per D2.3 v1.3 §`/onboard` integration point step 7 (renumbered from v1.3's step 7 to this amendment's step 8).

   **F-Usr-3 disposition note.** F-Usr-3 (Project Instructions step 5 acknowledgment is heavy) targets the Project Instructions block *content*, not the `/onboard` skill's render mechanics. The content is owned by D2.3 v1.3 §Project Instructions block and is read-only at this step; any amendment to the acknowledgment-step text lands in D2.3 v1.3, not in this skill. F-Usr-3 remains queued for v0.2.x per the prior session's amendment classification (lower-priority queue). See §Authoring notes companion doc for full disposition.

9. **Render the chat-end card.** Variant `normal` per the chat-end card template (Child A `chat-end-card.md`). Pattern T, Group A exit. After render, set `cascade:run-state.last_completed_group = "A"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<marker>-onboard.json"`, flush, write `.cascade/handoff/last.md`. Per `child_B_chains_sections.md` `/onboard` Pattern T block (sealed in a prior session; this amendment's gate evaluation lands BEFORE the `/Chains` block's group-exit render).

   This step is the chat-end card render proper; the `/Chains` block from `child_B_chains_sections.md` is the binding spec for its mechanics.

### Step-number rationale

The new step 7 (`workflow.default_strategy` elicit) lands here, not earlier, because:

- Steps 1–6 build the Linear product layer and the Status doc. Pasting Project Instructions (step 8) is only meaningful once that layer exists.
- The `workflow.default_strategy` slot's first downstream consumer is `/specify` step 1, which runs in a subsequent chat after the Project Instructions paste. The `/onboard` chat must write the slot before the Project Instructions paste so that the founder's first `/specify` chat reads a fully-wired `docs/.solo-config.json`.
- Placing the elicit between step 6 (Status doc init) and step 8 (Project Instructions render) keeps all `docs/.solo-config.json` writes adjacent (step 1's `linear.project_naming` decision + step 7's `workflow.default_strategy` write batch into a single `onboard.config-write` gate at the joint config-write moment).

---

## Gate evaluation

Two gates fire at `/onboard` at-write per D3.4 §Per-stage gate inventory `/onboard` row. Gates evaluate just before manifest seal (i.e., after step 8's Project Instructions paste confirmation lands in `cascade:run-state` and before step 9's chat-end card render). Per D3.4 §Aggregation rules: all-gates-evaluate, single-card-aggregate; both gates run regardless of which one fails first.

```text
GATES_AT_ONBOARD_AT_WRITE = ["onboard.linear-projects", "onboard.config-write"]

# At-write
for gate in GATES_AT_ONBOARD_AT_WRITE:
    evaluate; record per-gate result; do NOT short-circuit
if any gate has failing predicates:
    compose aggregate halt card per D3.4 §Aggregation rules
    do NOT write manifest; exit with halt
else:
    write manifest
    seal /onboard
```

### Gate 1 — `onboard.linear-projects` (at-write; D2.1 v2 `/onboard` row + D1)

```text
# Read the in-memory record of projects created in step 2
created_projects ← read step-2 invocation record from in-memory state

# Predicate 1: all six expected projects exist
mode ← step-1 decision: "plain" or "prefixed"
marker ← founder's elicited marker (already canonical; verified at step 2)
expected_names ← (
    ["Product", "Architecture", "Design", "Milestones", "Backlog", "Done"]
    if mode == "plain"
    else [f"[{marker}] {n}" for n in ["Product", "Architecture", "Design", "Milestones", "Backlog", "Done"]]
)

for expected in expected_names:
    project ← linear-mcp's read of project by name in the chosen team
    if project absent:
        FAIL with §onboard-linear-init-failed
        diagnostic: f"expected project '{expected}' absent from Linear team '{team_name}'; mode={mode}"
        continue
    if project.archived:
        FAIL with §onboard-linear-init-failed
        diagnostic: f"project '{expected}' exists but is archived; cannot use"
        continue

# Predicate 2: Status doc exists under the Product project and is reachable
product_project_id ← (
    project id for "Product" (plain) or "[<MARKER>] Product" (prefixed)
)
status_doc ← linear-mcp's read of documents under product_project_id
                where doc.title == "Status" or doc.title == f"[{marker}] Product status"
if status_doc absent or unreachable:
    FAIL with §onboard-linear-init-failed
    diagnostic: f"Status doc absent under Product project (id={product_project_id}); /onboard cannot maintain Status without it"

# Predicate 3: product label namespace registered
team_labels ← linear-mcp's read of team's label namespace
expected_label ← f"product:{marker}"
if expected_label not in team_labels:
    FAIL with §onboard-linear-init-failed
    diagnostic: f"product label '{expected_label}' not registered in team; cascade tickets cannot be tagged"
```

Halt code: `§onboard-linear-init-failed`. Recovery: re-run `/onboard` after manual Linear cleanup (deleting partially-created projects, re-attempting label creation). The skill does not auto-retry; founder confirms cleanup before re-invocation.

Per D3.4 §`/onboard` row: "All six Linear projects exist; Status doc created; product label namespace registered. (D2.1 v2 `/onboard` row.)"

### Gate 2 — `onboard.config-write` (at-write; D2.1 v2 `/onboard` row + D3.1 §`/onboard` product-level default)

```text
config_path ← "docs/.solo-config.json"

# Predicate 1: config file exists at the canonical path
if not file-exists(config_path):
    FAIL with §onboard-config-write-failed
    diagnostic: f"expected config at {config_path}; absent"
    continue

# Predicate 2: file parses as JSON
try:
    config ← json.parse(read(config_path))
except json.ParseError as e:
    FAIL with §onboard-config-write-failed
    diagnostic: f"config at {config_path} does not parse as JSON: {e}"
    continue

# Predicate 3: contains marker
if "marker" not in config or config.marker is empty or config.marker is not a string:
    FAIL with §onboard-config-write-failed
    diagnostic: f"config at {config_path} missing or empty 'marker' field; got {repr(config.get('marker'))}"
    continue

# Predicate 4: marker matches the elicited value
if config.marker != elicited_marker:
    FAIL with §onboard-config-write-failed
    diagnostic: f"config marker '{config.marker}' differs from elicited marker '{elicited_marker}'"
    continue

# Predicate 5: linear.project_naming consistent with step 1's decision
expected_naming_mode ← "prefixed" if step-1 detected collision else "plain"
config_naming ← config.get("linear", {}).get("project_naming", "plain")
if config_naming != expected_naming_mode:
    FAIL with §onboard-config-write-failed
    diagnostic: f"config linear.project_naming='{config_naming}' but step 1 decided '{expected_naming_mode}'"
    continue

# Predicate 6: workflow.default_strategy slot is structurally present
# (Optional slot per D3.1 §/onboard product-level default; empty string accepted.)
if "workflow" not in config:
    FAIL with §onboard-config-write-failed
    diagnostic: f"config missing 'workflow' top-level key; step 7 should have written it (empty string if founder skipped)"
    continue

slot ← config.workflow.get("default_strategy")
if slot is None:
    FAIL with §onboard-config-write-failed
    diagnostic: f"config workflow.default_strategy absent; step 7 should have written it (empty string if founder skipped)"
    continue

# Predicate 7: workflow.default_strategy value is either empty or in the canonical enum
CANONICAL_STRATEGIES = {
    "walking-skeleton", "api-boundary", "capability-cluster",
    "refactor-spike", "hybrid"
}
if slot != "" and slot not in CANONICAL_STRATEGIES:
    FAIL with §onboard-config-write-failed
    diagnostic: f"config workflow.default_strategy='{slot}' is not empty and not in canonical enum {sorted(CANONICAL_STRATEGIES)}; step 7's writer corrupted the value"
    continue

# Predicate 8: invariance slot exists (Child A solo-config-additions.json ships this with
# empty default; /onboard does not elicit at v0.2 but must verify the slot's presence so
# refactor-spike specs surface §invariance-config-missing rather than KeyError)
if "invariance" not in config:
    FAIL with §onboard-config-write-failed
    diagnostic: f"config missing 'invariance' top-level key; v0.2 template ships it (see Child A solo-config-additions.json)"
```

Halt code: `§onboard-config-write-failed`. Recovery: founder manually fixes `docs/.solo-config.json` and re-runs `/onboard` (which is idempotent on Linear-side per Gate 1's reach-the-team-and-find-projects semantics) OR `/onboard --reconcile` if a v0.2.x reconcile primitive for `/onboard` lands (out of scope for v0.2 per F-Rev-2's queued disposition for Child 0001-D).

Per D3.4 §`/onboard` row: "`docs/.solo-config.json` written; parses; contains `marker`." The amendment widens the predicate set to cover the structural slots (`linear.project_naming`, `workflow.default_strategy`, `invariance.pass_set_capture_command`) that Child A shipped in v0.2.

---

## Manifest write (on all-gates-pass)

Write the `/onboard` manifest at `.cascade/manifests/<marker>-onboard.json` per D2.1 v2 §`/onboard` row, extending the v0.1 schema with the `workflow_default_strategy` outputs field per D3.1 §`/onboard` product-level default. The manifest is scoped by marker (not by ticket — `/onboard` is the cascade-bootstrap stage and has no parent ticket):

```json
{
  "stage": "/onboard",
  "marker": "<MARKER>",
  "product": "<product name>",
  "onboard_sealed_at": "<ISO-8601 timestamp>",
  "outputs": {
    "summary":                          "/onboard initialised the <product> Linear product layer (six projects + Status doc), populated docs/.solo-config.json with marker '<MARKER>' and workflow.default_strategy '<value or empty>', and seeded Product / Design / Milestones / Status with founder-supplied content.",
    "linear_projects_created":          [
      {"name": "<Product or [<MARKER>] Product>",       "id": "<linear-project-id>"},
      {"name": "<Architecture or [<MARKER>] Architecture>", "id": "<id>"},
      {"name": "<Design or [<MARKER>] Design>",         "id": "<id>"},
      {"name": "<Milestones or [<MARKER>] Milestones>", "id": "<id>"},
      {"name": "<Backlog or [<MARKER>] Backlog>",       "id": "<id>"},
      {"name": "<Done or [<MARKER>] Done>",             "id": "<id>"}
    ],
    "status_doc_id":                    "<linear-doc-id>",
    "marker":                           "<MARKER>",
    "linear_project_naming":            "plain" | "prefixed",
    "config_path":                      "docs/.solo-config.json",
    "workflow_default_strategy":        "<enum value or empty string>",
    "north_star_doc_id":                "<linear-doc-id>",
    "design_system_doc_id":             "<linear-doc-id or null if non-UI product>",
    "placeholder_milestone_id":         "<linear-issue-id>",
    "project_instructions_pasted_at":   "<ISO-8601 timestamp from step 8>"
  },
  "input_provenance": {
    "parent_manifest_path":             null,
    "parent_manifest_sha256":           null
  },
  "manifest_sha256": "<recomputed-zero-self-field>"
}
```

Schema rules per D2.1 v2 + D3.1 + this amendment:

- `outputs.summary` is the single-sentence description D4.6 v1.1 reads to populate the chat-end card's "What just happened" section per D2.3 v1.3 §`/Chains` contract per-pattern statement (Pattern T row: `/onboard`'s manifest is the Group A exit manifest).
- `outputs.linear_projects_created[]` is the six-element list; order matches the canonical D1 ordering (Product, Architecture, Design, Milestones, Backlog, Done) for downstream deterministic indexing.
- `outputs.workflow_default_strategy` is the empty string `""` if the founder selected "skip" at step 7, or one of the canonical five strategies otherwise. The empty string is a valid v0.2 value per the read-but-tolerate-empty contract from Child 0001-B continuation 0's `/specify` step 1 amendment.
- `outputs.project_instructions_pasted_at` mirrors `cascade:run-state.project_instructions_pasted_at` (the step 8 confirmation timestamp); included on the manifest for D4.6 v1.1's re-derivation and for diagnostic clarity in `/retro` reports.
- `input_provenance` carries null parent fields because `/onboard` is the cascade's bootstrap stage — there is no upstream manifest to chain to.
- `manifest_sha256` recomputes with the self-field zeroed per D2.1 v2's manifest-checksum protocol.

After write, set `cascade:run-state.last_completed_stage` to point at this manifest path and sha; initialise `cascade:run-state.marker`, `cascade:run-state.product`, `cascade:run-state.queue_version = 1`. The `last_completed_group = "A"` field is set by step 9's chat-end card render per the `/Chains` block.

---

## Cross-references

- **D2.1 v2 §`/onboard` row** — the upstream manifest schema baseline (linear_projects_created[], status_doc_id, marker, config_path); this amendment extends with `workflow_default_strategy`, `linear_project_naming`, `placeholder_milestone_id`, `project_instructions_pasted_at`, and the `summary` field per D2.1 v2.1 common-manifest-fields.
- **D2.1 v2 §Caller-side verification protocol** — `/onboard` has no upstream stage, so steps 1–5 of the protocol return immediately on null `last_completed_stage`; step 6's stage-specific verifier predicates are this amendment's two gates.
- **D2.3 v1.3 §`/onboard` integration point** — the eight-step sequence v1.3 specified; this amendment renumbers v1.3's steps 7 and 8 to 8 and 9 to insert the new step 7 (workflow.default_strategy elicit).
- **D2.3 v1.3 §Project Instructions block** — the literal paste-block content step 8 renders.
- **D3.1 §`/onboard` product-level default** — the optional-slot semantics for `workflow.default_strategy`; the catalog of five canonical strategies + skip option; the read-but-tolerate-empty contract that composes with `/specify` step 1.
- **D3.4 §Per-stage gate inventory `/onboard` row** — the two-gate inventory this amendment implements.
- **D3.4 §Aggregation rules** — all-gates-evaluate, single-card-aggregate semantics applied to /onboard's at-write halt.
- **D1 §Linear product layer** — the six-project structure, the Status doc semantics, the prefix-mode convention.
- **D1 §`/onboard` changes** — the step-sequence binding; this amendment is the SKILL.md realisation of D1's changes. The F-Int-5 disposition retires D1's "reuse existing /onboard step 7" reference (which collides with v1.3's step 7) in favor of the descriptive "reuse existing v0.1 north-star seeding subroutine" — amendment lands in D1 at apply time per Surfaced items #1.
- **D0.1 §Multi-product Linear teams** — the prefix-mode trigger semantics.
- **Child A `solo-config-additions.json`** — the `workflow.default_strategy` and `invariance.pass_set_capture_command` empty-defaults this amendment's step 6 + step 7 write produces.
- **Child A `solo-config.example.json`** — the per-runner reference content; not read at runtime per Child A continuation-handoff §`.solo-config.example.json` is a NEW file.
- **Child A `chat-end-card.md`** — the template step 9 renders.
- **Child A `halt-messages-append.md`** — `§onboard-linear-init-failed` and `§onboard-config-write-failed` referenced by Gates 1 and 2. **Surfaced item:** verify these halt codes exist in v0.1 `halt-messages.md` (likely as part of the F-2 fix shipped in v0.1) or in Child A's `halt-messages-append.md`. If absent, the executing Claude Code session adds them at apply time.
- **`child_B_chains_sections.md`** Pattern T (Group A) block for `/onboard` — sealed in a prior session; this amendment's gate evaluation lands BEFORE the `/Chains` block's step 9 chat-end card render.
- **`specify-SKILL-amendments.md`** (Child 0001-B continuation 0) §Step 1 small amendment — the `/specify` step 1 read of `docs/.solo-config.json`'s `workflow.default_strategy` that this amendment's step 7 write satisfies. After this session: the slot is fully wired end-to-end.
- **D4.6 v1.1 §CLI surface** — reads this amendment's manifest's `outputs.summary` field and `outputs[]` entries to re-derive the Group A chat-end card on `solo-cascade resume`.
- **Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-13** — this skill amendment (combined with `update-linear-SKILL-amendments.md`) satisfies AC-13 as authored.
- **Parent spec Open Question 4** — `workflow.default_strategy` wiring closure resolved after this session.
