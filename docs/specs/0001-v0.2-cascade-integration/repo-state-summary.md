# Repo-state summary — Solo-Vibing v0.1 inventory and v0.1 → v0.2 delta

**Authored:** 2026-05-19. **Inventoried via:** `web_fetch` on https://github.com/OndraMasek/Solo-Vibing root README and `CLAUDE.md` (the only files reachable; GitHub `robots.txt` blocks subdir tree listings and individual file URLs in this session). **Scope:** the surface needed to compute the v0.1 → v0.2 integration spec at `docs/specs/0001-v0.2-cascade-integration/`.

---

## Part 1 — Inventory (what's there in v0.1)

### Top-level structure

Per the README's "What's in here" section + the repo root view:

```
Solo-Vibing/
├── .claude/
│   ├── rules/        (6 always-on rules)
│   ├── skills/       (11 cascade skills)
│   ├── commands/     (6 founder-fired commands)
│   └── agents/       (7 subagents)
├── docs/
│   ├── templates/    (spec.md.template, halt-messages.md, run.sh, AGENTS.md, CLAUDE.md, PROMPT.md, discovery/, onboarding/)
│   ├── decisions/    (append-only ADR log)
│   ├── specs/0001-wrap-build-log/  (worked-example sealed spec; not shipped to forks)
│   ├── constitution.md  (Solo-Setup's own governing principles; not shipped to forks)
│   └── .solo-config.json  (workflow knobs; not shipped to forks)
├── scripts/   (check_prereqs.sh, verify_linear_key.sh)
├── .gitignore
├── .mcp.json
├── CLAUDE.md
├── LICENSE   (Apache-2.0)
├── README.md
└── bootstrap.sh
```

### CLAUDE.md (read verbatim)

Confirmed truths about the framework as it stands today:

- CLAUDE.md is the **session instruction layer**, not the law. Governing principles live in `docs/constitution.md`, authored by `/constitution`.
- @-imports the six `.claude/rules/*.md` files explicitly (and Claude Code auto-loads anything else in there).
- Marker: `SOL`. Canonical source: `docs/.solo-config.json`, `marker` key.
- **Workflow cascade (v0.1, current):**
  ```
  /onboard → /discovery → /constitution → /specify → /plan → /review →
  /update-linear → /build (per child) → /wrap → /verify → /retro
  ```
  Eleven stages, of which `/build` is the only one that does not auto-fire (Ralph go-signal stays explicit, also splits into spawn turn and `--finalize` turn).
- Founder-fired commands (thin, deterministic): `/start`, `/status`, `/next`, `/config`, `/map-codebase`, `/audit-self`.
- Cascade behavior knobs live in `docs/.solo-config.json`: `cascade-only` / `interactive` / `yolo`.
- Halt-card rendering centralized in `docs/templates/halt-messages.md`; skills compose against named patterns rather than inlining structure.
- **Explicit v0.1 statement: "no hooks in v0.1; each stage Task-invokes the next per its own Chains section."**
- Constitution at `docs/constitution.md` is the source of truth for `/review` and `/verify` checks; **it has not been authored for this repo yet** ("It does not exist for this repo yet. It is on the near-term path").
- Session discipline target: 100–200k effective tokens; TDD default cadence; one ticket per `/build` run.

### What's *not* there (in v0.1)

Inferred from the README + CLAUDE.md absence-of-mention:

- No `.claude/hooks/` directory — CLAUDE.md says so explicitly.
- No `.claude/settings.json` — would have appeared in the file tree.
- No `tools/` directory — only `scripts/` for the two onboard helpers.
- No `solo-verify` CLI of any form.
- No `.cascade/` directory — the manifest store from D2.1 v2 is not yet committed.
- No `.solo-locks/`, no `.ralph/`, no `docs/product/` — directory skeletons all missing.
- No `docs/templates/capability-artifact-types.md`.
- No `docs/.solo-config.example.json`.
- Spec template (`docs/templates/spec.md.template`) does not carry the Pyramid shape preamble or per-test `[tag]` notation (inferred — the README does not call out a recent template update, and D3.0's analysis notes that the existing example at `docs/specs/0001-wrap-build-log/spec.md` uses `[unit]` inline at per-test grain but the template itself has not been formalized).
- Halt-messages does not carry the eleven Phase 3 halts.
- `/onboard` does not create the six D1 Linear projects (still on the current v0.1 Active/Backlog/Decisions/Sync Queue shape per D1 §Decision).

### Notes on what could not be inventoried

- GitHub's `robots.txt` blocks tree views and direct file fetches in this session. Inventory below the top-level is **inferred from the README's structural inventory, the v0.1 CLAUDE.md text, the Phase 3 design docs' references to the existing layout, and the carry-forward thread**. The executing session can use `Bash(git clone)` directly and read the files verbatim to confirm or correct any inference.

The Open Questions section in the parent spec flags inventory gaps that need verification at execution time — notably the `.claude/agents/` layout (which the SubagentStop hook predicate depends on).

---

## Part 2 — Delta computation (v0.1 → v0.2)

Cross-reference of inventory with Phase 3 design. Tabular form:

| File / directory | v0.1 state | v0.2 delta | Source | Child |
|---|---|---|---|---|
| `docs/templates/spec.md.template` | exists; no pyramid line | Add Pyramid shape preamble + `[tag]` per-test + three rendering variants | D3.2 §Spec template addition | A |
| `docs/templates/halt-messages.md` | exists; v0.1 halts | Append 11 new halts (2 D3.2 + 6 D3.3 + 3 D3.4) | D3.2 §Halt conditions, D3.3 §Halt conditions, D3.4 §Halt conditions | A |
| `docs/templates/.solo-config.json.template` | exists with v0.1 keys | Add `invariance.pass_set_capture_command` + optional `workflow.default_strategy` | D3.3 §Refactor-spike invariance + D3.1 §`/onboard` product-level default | A |
| `docs/.solo-config.json` | exists with v0.1 keys | Same additions as template | D3.3 + D3.1 | A |
| `docs/.solo-config.example.json` | absent | New; per-runner commented examples (pytest/vitest/jest/go/cargo) | D3.3 §Refactor-spike invariance | A |
| `docs/templates/capability-artifact-types.md` | absent | New; 7-row canonical table from D3.3 | D3.3 §Capability-cluster perceptual predicate | A |
| `.gitignore` | exists | Append `docs/specs/*/invariance/pass-set-at-verify.txt` | D3.3 §Refactor-spike invariance | A |
| `.cascade/manifests/.gitkeep` | absent | New; committed-empty | D2.1 v2 manifest store; D3.4 §`solo-verify` CLI | A |
| `.cascade/halt/.gitkeep` | absent | New; committed-empty | D2.1 v2 halt-card persistence | A |
| `.solo-locks/.gitkeep` | absent | New; committed-empty | D2.1 v2 per-resource locks | A |
| `.ralph/.gitkeep` | absent | New; committed-empty | Ralph loop state convention | A |
| `docs/product/.gitkeep` | absent | New; committed-empty | D1 product-layer filesystem mirror | A |
| `.claude/skills/specify/SKILL.md` | exists (v0.1) | Step 3: pyramid populator + `[tag]` resolution + `artifact_path` + `artifact_type`. Step 7: five `spec.*` gates. Strategy annotation cycle. | D3.1 §Step 1, D3.2 §Step 3, D3.3 §all, D3.4 §spec gates | B |
| `.claude/skills/plan/SKILL.md` | exists | `plan.*` gates; D3.1 override findings handling | D3.1 §Catalog override flow, D3.4 §plan gates | B |
| `.claude/skills/review/SKILL.md` | exists | `review.*` gates; SubagentStop wired | D2.2 §Stop / SubagentStop, D3.4 §review gates | B |
| `.claude/skills/build/SKILL.md` | exists | `build.*` gates: provenance, pyramid-tampering. Seed-as-backpressure unchanged | D3.2 §Downstream consumer touch-points, D3.4 §build gates | B |
| `.claude/skills/wrap/SKILL.md` | exists | `wrap.*` gates — naming-only changes from D2.1 v2 | D3.4 §wrap gates | B |
| `.claude/skills/verify/SKILL.md` | exists | Per-strategy dispatch matrix; multi-child halt aggregation; `children_gate_outcomes[]` write | D3.3 §all, D3.4 §verify dispatch | B |
| `.claude/skills/retro/SKILL.md` | exists | Read `children_gate_outcomes[]`; surface tag distribution / per-gate counts | D3.4 §retro gates, §children_gate_outcomes schema | B |
| `.claude/skills/onboard/SKILL.md` | exists | Six D1 projects + Status doc + marker write + optional `workflow.default_strategy` | D1 §`/onboard` changes, D3.1 §`/onboard` product-level default | B |
| `.claude/skills/update-linear/SKILL.md` | exists | `update-linear.diff-applied` gate | D3.4 §update-linear gates | B |
| `.claude/hooks/preflight-provenance.sh` | absent | New | D2.1 v2 §Caller-side verification, D2.2 §command hook type | C |
| `.claude/hooks/pyramid-tampering.sh` | absent | New | D3.2 §Downstream consumer, D2.2 §PreToolUse | C |
| `.claude/hooks/four-hat-objection-coverage.py` | absent | New (cascade's single agent-type hook) | D3.4 §What is a gate, D2.2 §Stop schema quirk | C |
| `.claude/hooks/stop-orchestrator.sh` | absent | New (single Stop-hook pattern) | D2.2 §Research-step resolution #3 | C |
| `.claude/hooks/session-start-state-restore.sh` | absent | New (resume/compact recovery) | D2.2 §SessionStart, D2.1 v2 §Cross-compact state | C |
| `.claude/hooks/session-end-telemetry.sh` | absent | New (async-only telemetry) | D2.2 §Critical caveat #4 | C |
| `.claude/settings.json` | absent | New; wires hooks to events | D2.2 §Settings file precedence | C |
| `tools/solo-verify` | absent | New Python stdlib script; full D3.4 CLI surface | D3.4 §`solo-verify` CLI surface | D |
| `tools/solo-verify-tests/` | absent | New; stdlib `unittest` suite, one class per gate | D3.2 §unit tag, walking-skeleton optional | D |
| `CLAUDE.md` (root) | exists; says "no hooks in v0.1" | Drop the no-hooks sentence; add §Cascade gates, §Strategy enum, §Hooks subsections | D3.1, D3.4, D2.2 | E |
| `docs/templates/CLAUDE.md` | exists | Lockstep with root for shared sections | Same as above | E |
| `README.md` | exists; v0.1 status | Update §Status to v0.2; add §What's new in v0.2 bullets | Phase 3 collectively | E |

**Total touched:** 12 files modified + 19 files / directories created + 5 committed-empty skeletons = **36 distinct paths**. Five children carry them.

---

## Part 3 — Surprises and flagged items

These are items the inventory surfaced that warrant founder attention before the executing session begins.

### 1. The v0.1 framework is more developed than the carry-forward suggested

The carry-forward handoff described the integration as a "bootstrap step" into a near-empty repo. The inventory shows v0.1 already has 11 cascade skills, 6 commands, 7 subagents, 6 always-on rules, a worked-example sealed spec, centralized `halt-messages.md`, a `spec.md.template`, a `bootstrap.sh` entry path with `--refresh-templates` and "GitHub Use this template" recovery paths, and even a `.mcp.json`. The integration is genuinely an **amendment + addition**, not a from-scratch build.

This changes the scope shape but not the AC list. It does change Child 0001-B's risk profile: nine skill amendments against an actively-developed v0.1 codebase carries higher merge-conflict risk than authoring nine skills from scratch. The executing session should be ready to handle "the skill already says X, the v0.2 amendment changes it to Y" diffs cleanly.

### 2. Spec number collision

`docs/specs/0001-wrap-build-log/` is the v0.1 worked-example spec. Counter discipline (per `.claude/rules/counter-allocation.md`) would allocate `0002-...` to the next spec. The handoff suggested `0001-v0.2-cascade-integration`. This spec lives at `0001-...` per the handoff but flags the collision in `spec.md` §Open questions with a recommendation to retire `0001-wrap-build-log` to `docs/examples/` (freeing `0001` for v0.2 use).

### 3. CLAUDE.md is the framework's own, not a template

The carry-forward thread implied CLAUDE.md should be amended as a generic file. The inventory shows CLAUDE.md at the repo root is **the framework's own session-instruction layer**, with a separate template at `docs/templates/CLAUDE.md` for forks. v0.2 amendments must update both in lockstep. Child 0001-E owns this; the `test_template_claude_md_matches_root_for_shared_sections` smoke test enforces it.

### 4. The constitution does not yet exist

CLAUDE.md says outright: "docs/constitution.md has not been authored for this repo yet. It is on the near-term path." Phase 3 design docs (especially D3.4 gate definitions) assume `/review` and `/verify` can check work against a constitution. This is **not blocking the v0.2 cascade integration** — gates evaluate against design predicates, not against constitution checks — but it is blocking the framework's own self-application beyond integration. Flag for v0.2 follow-up: author `docs/constitution.md` via `/constitution` before the dogfood test session.

### 5. The skill chain in v0.1 has `/discovery` and `/constitution` between `/onboard` and `/specify`

Per the CLAUDE.md cascade diagram. Phase 3 design docs (D3.4 §Per-stage gate inventory) name only 8 formal-gate stages: `/onboard`, `/specify`, `/review`, `/plan`, `/update-linear`, `/build`, `/wrap`, `/verify`, `/retro`. `/discovery` and `/constitution` are not gated in D3.4. This is **fine for v0.2** — these two stages are chat-side, not Claude-Code-side, and they fall under D2.2's "informational stages" framing — but the executing session should not add gates to them speculatively.

### 6. Robots-blocked subdir inventory

GitHub's `robots.txt` blocked tree views and most file fetches in this session. The inventory below the root level is inferred from the README, the CLAUDE.md text, and Phase 3 design references. The executing session should `git clone https://github.com/OndraMasek/Solo-Vibing` (or use the existing user-data uploads area if it carries a local copy) and read every file in `.claude/skills/` and `.claude/agents/` before amending — particularly the `four-hat-panel` agent's frontmatter, which the SubagentStop hook predicate's matcher depends on.

### 7. `four-hat-build-SKILL.md` etc. in the carry-forward thread are stale naming

The carry-forward thread named flat-file skill references ("build-SKILL.md", "specify-SKILL.md", "four-hat-build-SKILL.md"). The actual repo layout uses `.claude/skills/<stage>/SKILL.md` per the standard Claude Code skill convention. Spec uses the correct paths; carry-forward names retired in the spec's Open Questions.

### 8. Hook script language choice is a real decision, not a default

D2.2 didn't lock bash-vs-Python for hook scripts. The inventory shows `scripts/` is bash-only in v0.1 (`check_prereqs.sh`, `verify_linear_key.sh`). The spec recommends bash for trivial predicates and Python for structured-data work (matching the `tools/solo-verify` stack). This is flagged in the parent spec's Open Questions; the executing session can run with the recommendation or revise.

### 9. `bootstrap.sh` recovery surface is mature

The README documents `bootstrap.sh --refresh-templates` plus a "Use this template" recovery path. The v0.2 integration **must not break either path** — adopters who fork from a v0.2 upstream and run `bootstrap.sh` should still get a clean v0.2-shaped scaffold, and the "Use this template" recovery instructions should still work after `bootstrap.sh --refresh-templates`. This is a smoke test the executing session should add to child 0001-A: a fresh `bootstrap.sh` run into a tmpdir should produce a working v0.2 scaffold.

### 10. The framework's own `docs/.solo-config.json` is "not shipped to forks"

The README explicitly excludes it from the forked artifacts. This means amendments to the **framework's own** config are different from amendments to the **template** at `docs/templates/.solo-config.json.template` (or wherever the template lives — the inventory could not confirm the template's exact path; child 0001-A's first action is to view the templates directory and confirm). Both files need the v0.2 keys, in lockstep.

---

## What the executing session should do first

In order:

1. **Clone the repo locally** to bypass `robots.txt` and read every file under `.claude/` verbatim. Confirm or correct the inferred inventory above.
2. **Verify the four-hat-panel agent's frontmatter** in `.claude/agents/` — child 0001-C's `four-hat-objection-coverage.py` SubagentStop matcher depends on the agent's exact type name.
3. **Resolve the spec-number 0001 collision** (founder confirm: retire `0001-wrap-build-log` and use `0001` for v0.2, or rename this spec to `0002`).
4. **Confirm or revise the per-child strategy assignments** in `decomposition.md`. The five children's strategies are recommended, not locked — the executing session may revise based on the verbatim repo inventory.
5. **Execute children in the recommended order** from `decomposition.md` §Build order — A → D in parallel → C → B → E.
6. **Land each child's failing-test seed first** (TDD discipline per CLAUDE.md §Session discipline). Each child's `[smoke]`, `[unit]`, and `[perceptual]` entries are sketched in `decomposition.md`; the executing session may add or refine them at /specify time per child.
7. **Author `docs/constitution.md` separately** — not blocking this milestone but blocking the v0.2 self-application dogfood test that follows it.
