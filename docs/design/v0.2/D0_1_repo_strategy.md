# D0.1 — Repo strategy

**Status:** Design (v2 — updated 2026-05-18 per founder feedback; reconstructed 2026-05-19 from chat history after the original output filesystem expired).
**Phase:** 0 (Foundations).
**Supersedes:** Implicit current state in `01_LOAD_FIRST_project_overview.md` (framework + Bomber dogfood co-mingled).
**Resolves:** F-4 (partially), F-9 (partially — see §Multi-product Linear teams).

## Decision

The Solo Claude Stack framework lives in **its own GitHub repo**, framework-only and public. Consumer products built with the framework live in their own repos. **No public example repo ships with v0.2** — the framework's CI uses a synthetic spec in its own test fixtures to validate self-application.

Bomber, which served as the v0.1 dogfood, remains as a private testing repo. It is not promoted to a public example; the workflow-critique synthesis (SOL-89 et al.) is sufficient evidence of the v0.1 → v0.2 redesign rationale without exposing half-built Godot code.

## What stays in the framework repo

- `.claude/skills/` — all skill definitions (SKILL.md per skill)
- `.claude/rules/` — the always-on rules (naming, counter-allocation, scope-labels, completion-status, write-discipline, auditor-stance, code-markers)
- `.claude/commands/` — founder-fired commands (`/status`, `/next`, `/config`, etc.)
- `.claude/hooks/` — Claude Code hooks (SessionStart, UserPromptSubmit, PostToolUse, etc. — exact set defined in D2.2 once hook surface is verified)
- `.claude/agents/` — subagent definitions (build-reviewer, four-hat-engineer, four-hat-pm, four-hat-skeptic, four-hat-user, clarify-walker, decomposer, diagnoser)
- `docs/templates/` — all templates the cascade renders into a consumer repo
- `docs/design/v0.2/` — design records for v0.2 (this document and its siblings)
- `docs/design/v0.1/` — archived design records from v0.1 (the pre-dogfood `03_*` through `09_*` files)
- `docs/decisions/` — framework-level ADRs
- `docs/product/` — **outline-only product documentation** synced from Linear (see §Product-doc outline pattern below)
- `tools/solo-verify` — the gate-evaluation CLI (see D4.0 for build/distribution)
- `bootstrap.sh`, `scripts/` — installation and verification scripts
- `CLAUDE.md` (template) — the session-instruction template rendered into consumer repos at `/onboard`
- `docs/onboarding/` — onboarding handoff templates
- `LICENSE`, `README.md` — public-facing

The framework repo's own working `CLAUDE.md` (for working *on* the framework) stays gitignored per the existing rule.

## Product-doc outline pattern

`docs/product/` mirrors the Linear product-layer structure (per D1) as outline-only documents in the filesystem. The intent:

- **Browseable on GitHub.** Visitors can read the framework's product structure without Linear access. The outline shows what each Linear document contains and its current state at a glance.
- **Linear is canonical for content.** The filesystem version is a sync'd browsing-friendly mirror, not a second source of truth.
- **Synced on merge.** Whenever `/wrap` updates Linear product docs (per the canonical rule in D1), it also writes the corresponding filesystem outline file in the same commit. By the time work merges to `main`, the outline is current.

Files in `docs/product/`:

- `README.md` — explains the pattern, points contributors at Linear for canonical content, documents the sync discipline.
- `north-star.md` — outline of Linear's `product: north-star` doc.
- `architecture.md` — outline of Linear's `arch: technical-architecture` doc.
- `data-model.md` — outline of Linear's `arch: data-model` doc.
- `user-journeys.md` — outline of Linear's `design: user-journeys` doc.
- `status.md` — outline of Linear's Status document (see D1 §Status).
- `milestones.md` — outline of Linear's Milestones project; one section per milestone.

Each file contains:

- Section headers matching the Linear document's structure
- A short summary of current content (for at-a-glance reading; not a full reproduction)
- A link to the Linear doc for full content
- A `last_synced:` timestamp

`/wrap`'s extended responsibility (per D1) covers the sync. No separate `/sync-product-docs` command — sync is a side effect of the work that updated Linear in the first place. If a consumer reads the filesystem version and finds it stale (e.g. a `/wrap` failed mid-sync), they fall back to Linear, which is canonical.

The pattern applies to every consumer repo, not just the framework. The framework establishes the discipline; every onboarded consumer adopts it.

## Bomber's disposition

Bomber, the v0.1 dogfood project, has artifacts in two places:

- **Filesystem:** `scripts/`, `scenes/`, `levels/`, `.tres` resources, `project.godot` (if it exists), `docs/specs/0002-bomber-core-bomb-grid/`, `.ralph/SOL-*/` workspaces, `addons/gut` submodule.
- **Linear:** SOL-52 through SOL-88 (Bomber product issues), `[BOM-DOC-*]` documents, plus the workflow-critique synthesis SOL-89 through SOL-101.

**Filesystem disposition:**

- Bomber filesystem moves out of the public framework repo to a **private testing repo** (founder's own, not public). Continuity of Godot work happens there.
- The current Solo Claude Stack repo is reset to framework-only.

**Linear disposition:**

- The 5-team Linear-subscription limit means **no new team for Bomber**.
- Bomber projects live in the **existing Solo Claude Stack Linear team** alongside framework projects. Project names disambiguate via marker prefix — see §Multi-product Linear teams.
- SOL-52 through SOL-88 (Bomber product work) is **archived** rather than migrated: these tickets recorded the v0.1 dogfood and are workflow-feedback evidence, not work that continues. Bomber in v0.2 starts fresh under the new product-layer structure.
- SOL-89 through SOL-101 (workflow-critique synthesis) stays where it is — these are framework feedback and belong with framework work.
- `[BOM-DOC-0009]` (Bomber constitution) and `[BOM-DOC-0010]` (latest spec) are kept as historical context but not consumed by the v0.2 cascade.

## Multi-product Linear teams

The 5-team subscription limit forces multiple products to share Linear teams. v0.2 supports this via project-name prefixing:

- **Single-product team:** project names are plain — `Product`, `Architecture`, `Design`, `Milestones`, `Backlog`, `Done`.
- **Multi-product team:** each product's projects carry the marker as a prefix — `[BOM] Product`, `[BOM] Architecture`, `[BOM] Backlog`, etc.

`/onboard` detects collisions at project-creation time. If a standard-named project already exists in the chosen team, the new product gets prefix-mode projects automatically. The detection is one-shot — once a product is onboarded in prefix mode, it stays that way (recorded in `docs/.solo-config.json` as `linear.project_naming = "prefixed"`).

For the Solo Claude Stack team specifically:

- Framework work continues using current projects (Active, Backlog, Decisions, Sync Queue) without renaming. The framework's own product-layer adoption is deferred to v0.2.1.
- Bomber, when re-onboarded under v0.2, gets `[BOM] Product`, `[BOM] Architecture`, `[BOM] Design`, `[BOM] Milestones`, `[BOM] Backlog`, `[BOM] Done`. Status doc under `[BOM] Product`.

F-9 (identifier model incoherence) is **partially resolved**: project names are now unambiguous within the team and across products, but marker (BOM) and Linear team key (SOL) still don't match in shared teams. The cascade always reads marker from `docs/.solo-config.json` and never assumes marker = team key. The earlier proposed full resolution (one team per product) is unachievable under the subscription limit; the prefix pattern is the practical fix.

## Self-application test, redesigned

Previous design (in the dogfood era): "self-application is the test — if the stack cannot be used to build the stack, the stack is broken." Implementation was co-mingled and produced the v0.1 disaster (per SOL-89).

New design: **the framework's CI runs the cascade against a synthetic minimal spec in its own test fixtures.**

CI workflow:

1. Check out the framework at HEAD.
2. Spin up a fresh consumer environment (clean directory).
3. Run `bootstrap.sh` to install the framework into the consumer.
4. Run `/onboard` with a known marker (e.g. `TST`) pointed at a Linear sandbox team or a mock Linear API.
5. Apply a fixed spec from `tests/fixtures/synthetic-spec/` (a small AC, e.g. "the project compiles and outputs version string").
6. Run the cascade through `/verify`.
7. Assert exit conditions: `scope:built`, tests green, smoke check passed.

The synthetic spec is small (one AC, no external dependencies) and lives in the framework repo. No public example repo is required — the framework validates itself against its own test fixtures.

## Why no public example is fine for v0.2

- **For framework adoption:** examples help but aren't essential at v0.2. The framework's README + a screencast or terminal recording of the workflow running can demonstrate the experience without a maintained example repo. Many developer tools launch with documentation alone.
- **For self-application testing:** the synthetic-spec CI test provides honest validation without an external dependency. An example repo would be a more complex test, not a more useful one.
- **For credibility:** the framework's own development demonstrates it. The SOL-89 critique synthesis and v0.2 redesign show the framework being used on itself with public artifacts.
- **Maintenance cost:** an example repo rots if not maintained alongside framework changes. Skipping it removes that burden.

Confirmed: no public example for v0.2. Revisit at v0.3 if adoption signals demand it.

## Migration steps from current state

1. **Move Bomber filesystem out of the framework repo:**
   - Create a private repo (founder's own — not public) for Bomber Godot work.
   - Move `scripts/`, `scenes/`, `levels/`, `.tres` resources, `project.godot`, `Makefile`, `addons/gut`, etc.
   - Move `docs/specs/0002-bomber-core-bomb-grid/` and archived spec versions.
   - Delete `.ralph/SOL-*/` workspaces (build artifacts, no archival value).

2. **Archive Bomber Linear artifacts in place:**
   - SOL-52 through SOL-88 — move to a "Bomber v0.1 archive" project (created within Solo Claude Stack team) or apply an `archive:v0.1` label.
   - SOL-89 through SOL-101 stay where they are.
   - `[BOM-DOC-*]` documents stay; they're historical record.

3. **Provision Bomber v0.2 projects in Solo Claude Stack team:**
   - Create `[BOM] Product`, `[BOM] Architecture`, `[BOM] Design`, `[BOM] Milestones`, `[BOM] Backlog`, `[BOM] Done`.
   - Status doc under `[BOM] Product`.
   - Bomber's v0.2 work re-onboards into this structure. Note: Linear assigns identifiers from the team's counter, so new tickets will continue from `SOL-102`+ even though they belong to Bomber's `BOM` marker. That's the cost of the team-limit constraint.

4. **Clean framework repo of Bomber references:**
   - Remove Bomber-specific entries from `decomposition.md` workflow-feedback log; archive the log as `docs/design/v0.1/workflow-feedback-archive.md`.
   - Remove Bomber-specific examples from skill files.

5. **Add Hooks and Subagents trees:**
   - Create `.claude/hooks/` with stubs (populated per D2.2 once hook surface is verified).
   - Create `.claude/agents/` and ensure all existing subagent definitions live here.

6. **Add `docs/product/` outline tree:**
   - Create the template files (`north-star.md`, `architecture.md`, etc.) with empty outlines.
   - Create `docs/product/README.md` documenting the sync discipline.

7. **Re-onboard the framework against itself:**
   - The framework repo's own `/onboard` should now produce a clean state with no Bomber residue.
   - Verify by running `/audit-self`.

8. **Update top-level README** of the framework repo to describe v0.2 shape.

Migration order: step 1 (filesystem move) before step 2 (Linear archive), so file paths referenced in Linear comments still resolve during the move. Step 8 last so users discovering the framework don't see broken links during the transition.

## Open items (not blocking)

- **Hook surface verification** for D2.2 — needed before D0.1 can fully specify `.claude/hooks/` contents.
- **CI provider choice** for the synthetic-spec test (GitHub Actions assumed; confirm).
- **Bomber filesystem archive location** — the founder's own private repo, name TBD.

## Reconstruction note

This file was reconstructed on 2026-05-19 from past-conversation history because the original `/mnt/user-data/outputs/v0.2/D0.1_repo_strategy.md` from the 2026-05-18 session was in an ephemeral session filesystem that did not persist. Content is faithful to the v2 the founder reviewed on 2026-05-18, with the following minor reconciliations:

- Added explicit `tools/solo-verify` line item to "What stays in the framework repo" (was implicit; D4.0 makes it explicit).
- Removed bare opening sentence "Confirmed: no public example for v0.2…" formatting (was a chat-direct line; here it's regular prose).

No substantive change. If a future search of past-session outputs surfaces the original byte-exact file, prefer that over this reconstruction.
