---
name: onboard
description: First-run interactive setup. Initializes a new Solo-Setup project — brownfield check, prereqs, upstream-content audit, Linear + GitHub MCP connections, GitHub remote, Linear API key, project marker, Linear team pick, six-project + Status-doc Linear product layer, north-star + design-system + placeholder-milestone seeding, Project Instructions paste-block render, and Group A chat-end card. Fires on "/onboard", "onboard", "set up project", "initialize", or on the first chat-Claude turn in an uninitialized repo (no docs/.solo-config.json). Manual override `/onboard --reinit <step>` re-runs a single step. Invokes the codebase-mapper agent at step 0 for brownfield repos.
---

# onboard

Interactive setup. Run once per new project, after cloning the Solo-Setup template into a fresh repo. Each step waits for founder response before advancing. References rules: `naming.md`, `scope-labels.md`, `completion-status.md`, `write-discipline.md`, `auditor-stance.md`. Invokes agent: `codebase-mapper` (step 0). Step 8 renders the Project Instructions paste-block per D2.3 v1.3 §`/onboard` integration point; step 9 renders the Group A chat-end card per the `/Chains` Pattern T contract.

## Trigger

- User: "/onboard", "onboard", "set up project", "initialize"
- Auto: first chat-Claude turn in a repo where `docs/.solo-config.json` is missing
- Manual override: `/onboard --reinit <step>` — re-runs one specific step

## Behavior

The pre-step gates (brownfield check, prereqs, connectors, GitHub remote, Linear API key, marker pick, team pick) run before step 1 below. They are unchanged from v0.1 at the substantive level and remain founder-confirmation-gated:

- **Brownfield check.** Detect non-template source; if present, Task-invoke `codebase-mapper` agent. Map written to `docs/onboarding/codebase-map.md`. Agent statuses per `completion-status.md` §Agent contract.
- **Prereqs check.** Run `scripts/check_prereqs.sh`; verify the template/reference files exist. Missing → `BLOCKED` per §missing-context.
- **Upstream content audit.** Detect populated upstream artifacts (constitution, prior specs, north-star). Prompt the founder per file: wipe / move-to-`docs/upstream-examples/` / keep. Skipped on `--reinit` and `--skip-upstream-audit`. Re-state authorization in the response before filesystem writes per Notes §AskUserQuestion re-statement.
- **Connectors check.** Linear MCP (`list_teams`); GitHub MCP (`gh auth status`). Either missing → `BLOCKED` per §linear-unavailable / §github-unavailable.
- **GitHub remote check.** `git remote -v | grep -q origin`. Missing → halt `NEEDS_CONTEXT` per §github-remote-missing. After step 6's first commits, the skill auto-runs `git push`; divergent-history failures halt `BLOCKED` per §parallel-history-risk.
- **Linear personal API key.** Founder pastes `LINEAR_API_KEY=...` into `.env`. Verify with `scripts/verify_linear_key.sh`. The key never enters chat. Verify `.env` is gitignored. Worktree warning surfaced if applicable.
- **Project marker.** Ask the founder for the Linear project marker (default `SOL`); record under `marker` in the to-be-written `docs/.solo-config.json`. Surface the shared-Linear-teams clarification per `naming.md` §Shared Linear teams.
- **Linear team pick.** Call `list_teams`. Single team → silent pick; multiple → `AskUserQuestion`. Record `linear.team_name` in the to-be-written config.

### v0.2 `/onboard` step sequence

1. **Determine project-name mode.** Scan the chosen Linear team for existing projects named `Product`, `Architecture`, `Backlog`, `Done`. If any exist, switch to **prefix mode** (write `linear.project_naming = "prefixed"` to the to-be-written `docs/.solo-config.json`; defer the write itself to step 6 + step 7's joint config-write). Per D0.1 §Multi-product Linear teams and D1 §`/onboard` changes step 1.

2. **Create the six projects + Status doc.** Per D1 §Linear product layer:
   - Plain mode: `Product`, `Architecture`, `Design`, `Milestones`, `Backlog`, `Done` + Status under Product.
   - Prefix mode: `[<MARKER>] Product`, `[<MARKER>] Architecture`, `[<MARKER>] Design`, `[<MARKER>] Milestones`, `[<MARKER>] Backlog`, `[<MARKER>] Done` + Status under `[<MARKER>] Product`.

   The marker is from the founder's earlier marker elicitation (v0.1 contract carries forward) or — for amended fork — read from any pre-existing `docs/.solo-config.json`. The product label namespace (`product:<MARKER>` on every cascade-created ticket) is registered with the Linear team at this step. Per D1 §`/onboard` changes step 2.

3. **Seed Product with founder's north-star.** Reuse the **v0.1 north-star seeding subroutine** (formerly v0.1 step 7; the F-Int-5 disposition retires the numeric reference in D1 §`/onboard` changes step 3 in favor of this descriptive one). Interactive flow: founder authors the problem statement, target user, target shape, non-goals, distribution posture; the skill writes the `[<MARKER>-DOC-NNNN] product: north-star` document under the Product project. Per D1 §Linear product layer Product subsection.

4. **Seed Design with founder's design-system if applicable.** Skip for non-UI products. Founder-supplied seed; the skill writes the `[<MARKER>-DOC-NNNN] design: design-system` document under the Design project. Per D1 §Linear product layer Design subsection.

5. **Seed Milestones with placeholder M-1.** One Linear issue under the Milestones project: title `[<MARKER>] M-1: first deliverable`; description: "placeholder — refine at `/discovery` or `/specify`." Per D1 §Linear product layer Milestones subsection.

6. **Initialise Status doc with "no work in progress."** The single Linear document under the Product project, the 30-second read per D1 §Status. Initial content sets `Current milestone: M-1 (placeholder)`, all gates "pending", `What works`, `What's broken`, `What's next` empty. Per D1 §Linear product layer Status subsection.

7. **Write the joint config. Do NOT elicit a decomposition strategy here.** Compose step 1's `linear.project_naming` decision with the rest of the initial `docs/.solo-config.json` into a single write. `workflow.default_strategy` is written as the empty string `""` — **onboarding does not ask the founder to pick a decomposition strategy.**

   **Why the strategy is not elicited at onboard.** The decomposition strategy is a per-feature decision made during `/specify`: step 1 proposes a strategy from the five-strategy catalog (`walking-skeleton`, `api-boundary`, `capability-cluster`, `refactor-spike`, `hybrid`) and the founder confirms it at step 5. The strategy must be set there because `/specify` step 3 derives the spec's test-pyramid shape from it and the `spec.pyramid-shape` / `spec.strategy-evidence` gates check against it. A founder at onboarding has no feature to reason about yet, so choosing a strategy at setup time is premature and out of place. The empty `""` slot satisfies the `onboard.config-write` gate's slot-presence predicate and `/specify` step 1's read-but-tolerate-empty contract — `/specify` proposes from first principles when the default is empty.

   The `workflow.default_strategy` slot is retained (empty) as a forward-compatible, optional product-level *hint*: a founder may hand-set it later to seed `/specify`'s proposal, but the cascade never sets it at onboarding and never treats it as the decision. Per D3.1 §`/onboard` product-level default — **amended**: the v0.2 onboard elicitation is removed; `/specify` step 1's read-but-tolerate-empty wiring is unchanged. (Parent spec Open Question 4; Child 0001-B continuation 0's `/specify` step 1 amendment.)

   The joint config write at this step also produces `CLAUDE.md` from `docs/templates/CLAUDE.md.template` with `<MARKER>` substituted (the v0.1 CLAUDE.md scaffold step folds into the joint config-write turn). If a `CLAUDE.md` already exists (re-run, or founder created it manually), show the diff and ask before overwriting.

8. **Render the Project Instructions paste-block and prompt the founder to paste.** Per D2.3 v1.3 §`/onboard` integration point and §Project Instructions block. The skill renders the v1.3-specified paste-block content (the eight-group framing, the chat-start protocol, the recovery paths), prints it inside a fenced code block prefixed with "Paste this into Claude.ai → Project → Instructions:", and waits for the founder's confirmation (a chat message containing a recognised acknowledgment phrase — implementation detail of the wait UX is owned by SOL-58 per D2.3 v1.2 §SOL-58's remaining scope). On confirmation, write the timestamp to `cascade:run-state.project_instructions_pasted_at`. Per D2.3 v1.3 §`/onboard` integration point step 7 (renumbered from v1.3's step 7 to this amendment's step 8).

   **F-Usr-3 disposition note.** F-Usr-3 (Project Instructions step 5 acknowledgment is heavy) targets the Project Instructions block *content*, not the `/onboard` skill's render mechanics. The content is owned by D2.3 v1.3 §Project Instructions block and is read-only at this step; any amendment to the acknowledgment-step text lands in D2.3 v1.3, not in this skill. F-Usr-3 remains queued for v0.2.x per the prior session's amendment classification (lower-priority queue). See §Authoring notes companion doc for full disposition.

9. **Render the chat-end card.** Variant `normal` per the chat-end card template (Child A `chat-end-card.md`). Pattern T, Group A exit. After render, set `cascade:run-state.last_completed_group = "A"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<marker>-onboard.json"`, flush, write `.cascade/handoff/last.md`. Per `child_B_chains_sections.md` `/onboard` Pattern T block (sealed in a prior session; this amendment's gate evaluation lands BEFORE the `/Chains` block's group-exit render).

   This step is the chat-end card render proper; the `/Chains` block from `child_B_chains_sections.md` is the binding spec for its mechanics.

### Step-number rationale

Step 7 writes the joint `docs/.solo-config.json` (it does not elicit a strategy — see step 7). It lands here, not earlier, because:

- Steps 1–6 build the Linear product layer and the Status doc. Pasting Project Instructions (step 8) is only meaningful once that layer exists.
- The `workflow.default_strategy` slot is consumed by `/specify` step 1 in a subsequent chat. The `/onboard` chat must write the slot (empty) before the Project Instructions paste so the founder's first `/specify` chat reads a fully-wired `docs/.solo-config.json`.
- Placing the joint config write between step 6 (Status doc init) and step 8 (Project Instructions render) keeps all `docs/.solo-config.json` writes adjacent (step 1's `linear.project_naming` decision + step 7's slot write batch into a single `onboard.config-write` gate at the joint config-write moment).

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
    diagnostic: f"config missing 'workflow' top-level key; step 7 writes it (workflow.default_strategy is empty in v0.2 — onboarding does not elicit a strategy)"
    continue

slot ← config.workflow.get("default_strategy")
if slot is None:
    FAIL with §onboard-config-write-failed
    diagnostic: f"config workflow.default_strategy absent; step 7 writes it as empty string (onboarding does not elicit a strategy; /specify chooses it)"
    continue

# Predicate 7: workflow.default_strategy value is either empty or in the canonical enum
CANONICAL_STRATEGIES = {
    "walking-skeleton", "api-boundary", "capability-cluster",
    "refactor-spike", "hybrid"
}
if slot != "" and slot not in CANONICAL_STRATEGIES:
    FAIL with §onboard-config-write-failed
    diagnostic: f"config workflow.default_strategy='{slot}' is not empty and not in canonical enum {sorted(CANONICAL_STRATEGIES)}; onboard writes '' — a non-empty value came from a manual hand-set and must be a valid enum member"
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

## Manifest write (on all-gates-pass)

Write the `/onboard` manifest at `.cascade/manifests/<marker>-onboard.json` per D2.1 v2 §`/onboard` row, extending the v0.1 schema with the `workflow_default_strategy` outputs field per D3.1 §`/onboard` product-level default. The manifest is scoped by marker (not by ticket — `/onboard` is the cascade-bootstrap stage and has no parent ticket):

```json
{
  "stage": "/onboard",
  "marker": "<MARKER>",
  "product": "<product name>",
  "onboard_sealed_at": "<ISO-8601 timestamp>",
  "outputs": {
    "summary":                          "/onboard initialised the <product> Linear product layer (six projects + Status doc), populated docs/.solo-config.json with marker '<MARKER>' (workflow.default_strategy left empty — chosen per-feature at /specify), and seeded Product / Design / Milestones / Status with founder-supplied content.",
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
    "workflow_default_strategy":        "",
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
- `outputs.workflow_default_strategy` is the empty string `""` in v0.2 — onboarding does not elicit a decomposition strategy (it is chosen per-feature at `/specify`, proposed step 1 / confirmed step 5). The field is retained for forward compatibility; a non-empty value can only arise from a founder hand-setting the slot later. The empty string is valid per the read-but-tolerate-empty contract from Child 0001-B continuation 0's `/specify` step 1 amendment.
- `outputs.project_instructions_pasted_at` mirrors `cascade:run-state.project_instructions_pasted_at` (the step 8 confirmation timestamp); included on the manifest for D4.6 v1.1's re-derivation and for diagnostic clarity in `/retro` reports.
- `input_provenance` carries null parent fields because `/onboard` is the cascade's bootstrap stage — there is no upstream manifest to chain to.
- `manifest_sha256` recomputes with the self-field zeroed per D2.1 v2's manifest-checksum protocol.

After write, set `cascade:run-state.last_completed_stage` to point at this manifest path and sha; initialise `cascade:run-state.marker`, `cascade:run-state.product`, `cascade:run-state.queue_version = 1`. The `last_completed_group = "A"` field is set by step 9's chat-end card render per the `/Chains` block.

## Same-turn write rules

Per `write-discipline.md`:
- Filesystem writes (`docs/.solo-config.json`, `CLAUDE.md`, the chat-end card render at step 9): grouped per step, after founder confirmation.
- Linear writes (project creation, doc seeding, milestone placeholder, label namespace registration): batched same-turn when missing.
- Git operations (the step 6 / step 7 first-commit sequence and any subsequent pushes): single command sequence.
- `.env` is written by the founder, never by the skill.

## Outputs

| Artifact | Location |
| -- | -- |
| Codebase map (brownfield only) | `docs/onboarding/codebase-map.md` (written by the `codebase-mapper` agent) |
| Workflow config | `docs/.solo-config.json` (with `marker`, `linear.team_name`, `linear.project_naming`, `workflow.default_strategy`, `invariance.*`) |
| Project session instructions | `CLAUDE.md` (gitignored at upstream; tracked at fork) |
| Linear product layer | Six projects (`Product`, `Architecture`, `Design`, `Milestones`, `Backlog`, `Done`) in plain or prefix mode |
| Status doc | Single Linear document under the Product project |
| North-star doc | `[<MARKER>-DOC-NNNN] product: north-star` under Product |
| Design-system doc (UI products only) | `[<MARKER>-DOC-NNNN] design: design-system` under Design |
| Placeholder milestone | `[<MARKER>] M-1: first deliverable` under Milestones |
| Product label namespace | `product:<MARKER>` registered on the Linear team |
| Cascade manifest | `.cascade/manifests/<marker>-onboard.json` |
| Group A chat-end card | Rendered in chat at step 9; on-disk handoff at `.cascade/handoff/last.md` |

## Completion status

Per `completion-status.md`:

- `DONE` — all steps confirmed by the founder; step 8 confirmed Project Instructions paste; both gates passed; step 9 rendered the chat-end card.
- `DONE_WITH_CONCERNS` — onboard completed but: step 7 CLAUDE.md write preserved an existing `CLAUDE.md` instead of writing the scaffold; upstream-content audit left content in place per founder override; brownfield map returned `DONE_WITH_CONCERNS`.
- `BLOCKED` — pre-step prereqs missing; connectors disconnected; GitHub push failed against divergent-history remote; `.env` not gitignored; brownfield agent returned `BLOCKED`; either at-write gate failed (halt-card per the gate's named halt-code: `§onboard-linear-init-failed` or `§onboard-config-write-failed`).
- `NEEDS_CONTEXT` — `.env` missing entirely; Linear API key invalid or revoked; founder aborted at a confirmation gate without resolution; GitHub remote missing and founder hasn't confirmed remote setup.

## /Chains

**Pattern:** T (terminal-render)
**Group:** A
**Within-group transitions:** none. `/onboard` is a single-stage group; its eight internal steps (per D2.3 v1.3 §`/onboard` integration point) are intra-stage progression, not within-group transitions in the contract sense. Each internal step is an advisory PreCompact safe boundary (per D2.3 v1.3 §Within-group safe boundaries Group A row) but no Task-invoke fires between them.
**Group exit trigger:** completion of step 8 in `/onboard`'s internal sequence, i.e., immediately after step 7 (founder confirms the Project Instructions paste-block was pasted into Claude.ai → Project → Instructions; `cascade:run-state.project_instructions_pasted_at` is timestamp-set) and the `onboard.linear-projects` and `onboard.config-write` gates per D3.4 §onboard gates have passed and `/onboard`'s manifest at `.cascade/manifests/<marker>-onboard.json` has been written.
**Group exit render:** chat-end card per `docs/templates/chat-end-card.md`, variant `normal`. Render is the eighth and final step of `/onboard`'s internal sequence. After render, set `cascade:run-state.last_completed_group = "A"`, write `cascade:run-state.last_completed_group_exit_manifest_path = ".cascade/manifests/<marker>-onboard.json"`, flush `cascade:run-state` per D2.3 v1.3 §Group-exit mechanics step 2, write `.cascade/handoff/last.md` per §Group-exit mechanics atomicity. Do not Task-invoke anything.
**Next group entry:** B (`/discovery`). The founder copies the handoff prompt from the chat-end card and pastes it into a new chat to advance.
**Auto-fire compact handling:** not applicable. Group A runs in chat-Claude (per D2.3 v1.3 §Execution surface per group), which has no live PreCompact hook; auto-fire compact behaviour applies only in Group F.
**Group's exit manifest:** this skill's own manifest at `.cascade/manifests/<marker>-onboard.json`. No subagents; no chain intermediates.

Step 0's brownfield path invokes the `codebase-mapper` agent inline and returns to step 1; that is an agent invocation, not a skill chain.

## Cross-references

- **D2.1 v2 §`/onboard` row** — the upstream manifest schema baseline (linear_projects_created[], status_doc_id, marker, config_path); this amendment extends with `workflow_default_strategy`, `linear_project_naming`, `placeholder_milestone_id`, `project_instructions_pasted_at`, and the `summary` field per D2.1 v2.1 common-manifest-fields.
- **D2.1 v2 §Caller-side verification protocol** — `/onboard` has no upstream stage, so steps 1–5 of the protocol return immediately on null `last_completed_stage`; step 6's stage-specific verifier predicates are this amendment's two gates.
- **D2.3 v1.3 §`/onboard` integration point** — the eight-step sequence v1.3 specified; this amendment renumbers v1.3's steps 7 and 8 to 8 and 9 to insert the new step 7 (the joint `docs/.solo-config.json` write; `workflow.default_strategy` written empty, not elicited).
- **D2.3 v1.3 §Project Instructions block** — the literal paste-block content step 8 renders.
- **D3.1 §`/onboard` product-level default** — the optional-slot semantics for `workflow.default_strategy` and the read-but-tolerate-empty contract that composes with `/specify` step 1. **Amended in this skill:** the v0.2 onboard founder-facing strategy elicitation is removed — onboard writes the slot empty and the decomposition strategy is chosen per-feature at `/specify` (proposed step 1, confirmed step 5). The slot remains as an optional hint a founder may hand-set later; the strategy catalog and confirm flow live in `/specify`, not here.
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

## Notes

**Interactive by design.** Each step waits for founder confirmation because onboard is high-stakes: it writes the filesystem, creates Linear projects, and triggers a multi-day discovery flow downstream. No silent advancement.

**Re-running `/onboard` after initial setup is safe** — projects already created are skipped (Gate 1's predicate evaluates against the Linear state and tolerates idempotent re-creation), `CLAUDE.md` is never overwritten without confirmation, and the upstream-content audit is skipped on `--reinit`. Use `/onboard --reinit <step>` to redo one step (rotated Linear API key, marker change, re-render chat-end card after editing the template).

**Brownfield step invokes the agent, not the command.** Per audit decision #7, the brownfield analysis is the `codebase-mapper` agent. /onboard Task-invokes the agent directly; the founder's manual re-run surface is the separate `/map-codebase` command. /onboard does not call `/map-codebase`.

**AskUserQuestion re-statement convention** *(per the Bomber-test permission-classifier finding)*. When a step uses `AskUserQuestion` followed by a privileged tool call (e.g. Linear write, filesystem write outside the templates directory), the skill emits a one-line text output re-stating the founder's authorization in the response immediately before the tool call. The classifier reads recent context; re-stating the answer in-line ensures the authorization is visible at decision time. Applies to the upstream-content wipe gate, the team-pick prompt, the north-star seeding writes (step 3), and the design-system seeding writes (step 4). (Step 7 no longer prompts the founder for a strategy, so it has no AskUserQuestion to re-state.)

**CLAUDE.md scaffold is the template version, not the locked production version.** The founder edits it after onboard — project-specific principles, tool constraints, naming conventions. Constitution rules (including "Only /plan sets `scope:sealed`") live in `docs/constitution.md`, authored by `/constitution`, not in `CLAUDE.md`.

**The steps are the minimum viable setup.** Steps that look optional (connectors verify, gitignore check, upstream content audit, GitHub remote check, worktree warning) exist because they're the most common silent-failure modes in fresh forks. Each maps to a specific failure observed in the Bomber-test report.

## Open questions (deferred to v1.1+)

- **Brownfield heuristic precision.** The "count files outside known dirs" detector is coarse. AST-level or manifest-aware detection is v1.1+ (shared concern with the `codebase-mapper` agent).
- **`interactive` cascade mode** in `docs/.solo-config.json` is parsed but not implemented in v0.1; reserved for a future per-stage confirmation surface.
