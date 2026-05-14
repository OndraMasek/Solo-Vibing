# Solo-Setup — Constitution

> Version: 1.0.0
> Created: 2026-05-14
> North-star: [docs/product/north-star.md](product/north-star.md)
> Idea brief (source): [docs/discovery/idea-brief-v1.md](discovery/idea-brief-v1.md)

## Mission

Solo-Setup packages a complete solo-founder AI workflow stack — Claude.ai project conventions, Claude Code skills/commands, Linear MCP integration, GitHub conventions, a Ralph automation loop, spec-discipline templates, and four-hat adversarial review — as a fork-and-adopt reference repository. A competent technical person can fork the repo and adopt the entire pipeline in under an hour. The deliverable is the repo, not a service. The workflow's value is measured by how much agent-driven drift it removes before code ships.

## Core principles

* **TDD by default.** Every build session opens with failing tests, not code. The failing-test seed in each spec is the backpressure `/build` runs against.
* **Vertical slices over horizontal layers.** Each child ticket produces user-visible behavior unless infrastructure-only is explicitly justified (see decomposer agent's classification rubric).
* **Spec-driven.** Code-Claude refuses tickets without `scope:sealed` per `.claude/rules/scope-labels.md`. Only `/plan` sets this label (and `/verify-fix` as the sole exception).
* **Halt over guess.** When the cascade can't converge, halt with options — never improvise spec changes. `.claude/rules/auditor-stance.md` governs the voice of halts.
* **Self-application is the test.** This repo is built with the workflow it documents. If the stack cannot be used to build the stack, the stack is broken — treat that as a finding, not an inconvenience.
* **Free-tier-first.** The stack assumes Linear free tier, GitHub free repos, and Claude.ai Pro at minimum. No paid-tool dependency is introduced without a free-tier path.
* **Append-only artifacts.** Specs, four-hat docs, build-logs, constitutions, ADRs — prior versions are archived, never overwritten in place. Read history is permanent; rewriting it is forbidden by `.claude/rules/write-discipline.md`.
* **Language-agnostic by design.** The workflow imposes discipline, not stack choice. Concrete examples may pick a language; the cascade itself does not.

## Process rules

The authoritative process rules live in `.claude/rules/`. This constitution surfaces them as pointers — when a rule changes, the rule file is canonical and this section needs no amendment.

* `.claude/rules/naming.md` — IDs, slugs, file paths, marker resolution from `docs/.solo-config.json`.
* `.claude/rules/counter-allocation.md` — NNNN allocation protocol (scan-then-claim against authoritative sources).
* `.claude/rules/scope-labels.md` — label state machine (`scope:specified → scope:planned` on parent; `scope:sealed → scope:built` on child), transition ownership, refusal protocol.
* `.claude/rules/completion-status.md` — `DONE` / `DONE_WITH_CONCERNS` / `BLOCKED` / `NEEDS_CONTEXT` contract.
* `.claude/rules/write-discipline.md` — same-turn batching, no skill-chaining writes, partial-failure handling.
* `.claude/rules/auditor-stance.md` — finding voice (state-as-fact, no preamble, no LGTM closures, one finding per `{type, locus}`, `uncertain:` prefix for hypotheses).

When the constitution and a rule disagree, **the rule wins**. The constitution's process-rules pointers exist for context-loading, not for re-stating the rules.

## Architectural constraints

* **Stack:** language-agnostic. The repo is documentation, templates, and `.claude/` configuration — not an application. The Ralph loop, `AGENTS.md` autodetect, and `docs/onboarding/sandbox.md` concerns apply to *adopting* repos, not to this one.
* **Tooling baseline:** Claude Code CLI; Linear MCP server (`mcp__f779be30-*`); GitHub free repos; Anthropic SDK / Claude API at Opus 4.6+ or 4.7 for cascade work. Sonnet 4.6 is acceptable for agent fan-out (four-hat, build-reviewer) where speed > depth.
* **Free-tier obligation:** every documented adopter path must run on free-tier resources. Paid alternatives may be documented as optional optimizations, never as required steps.
* **Branch + path naming:** strictly per `.claude/rules/naming.md`. The marker (`SOL` for this repo) is canonical from `docs/.solo-config.json`; the convenience copy in `CLAUDE.md` is human-readable only.
* **Same-turn batching:** every skill's writes (filesystem + Linear MCP + git) batch within one turn per `.claude/rules/write-discipline.md`. Cross-turn write chains are forbidden — they create partial-state messes the cascade can't recover from cleanly.
* **Append-only history:** spec markdown archives under `docs/specs/NNNN-<slug>/archive/spec-v<N>.md`; constitution archives under `docs/constitution/archive/v<semver>-<date>.md`; four-hat docs and build-logs are append-only by skill contract.
* **Per-feature directory layout:** `docs/specs/NNNN-<slug>/` holds `spec.md`, `decomposition.md`, `build-log.md` (post-SOL-42), `verify-report.md`, and `archive/`. No other layout in v0.1.
* **Performance and accessibility floors:** N/A for this repo (no UI, no runtime). Apply to *adopting* repos per their own constitution.

This section is the most volatile — fills out as ADRs accumulate. v1.0.0 has no project-specific architectural ADRs filed yet; expect MINOR amendments over the first 5–10 ADRs.

## Decision-making

* **File an ADR when:** introducing a new dep, choosing between architectural options, changing a previously-recorded decision, recording a non-obvious trade-off that future readers would otherwise re-litigate.
* **Halt to founder when:** ADR-reversal detected; dep fails the four-condition low-stakes test; parent undecomposable (decomposer agent flagged); failing-test seed incomplete; constitution-check fails; spec is incomplete; Linear MCP unreachable mid-write; spec checksum drift detected at `/build` time.
* **Auto-file ADR when:** `/review`'s check h (new-dep scan) passes the four-condition test — language-ecosystem standard utility, no runtime architectural lock-in, not a peer-competitor to an existing dep, project has ≥1 prior ADR.
* **Founder confirmation required for:** every Core-principle amendment, every Process-rule change classified MAJOR by the amendment rubric, every `/specify --unseal`, every `/build --reset --confirm`, every destructive Linear or git operation.

## Out of scope

* **Not a SaaS.** No hosted service, no accounts, no billing.
* **Not a coding assistant replacement.** Sits on top of Claude Code; doesn't compete with it.
* **Not multi-tenant team workflows in v0.1.** Solo founder is the canonical user; team patterns are v0.2+ territory.
* **Not framework-prescriptive.** Language-agnostic; the workflow imposes discipline, not stack choice.
* **Not autonomous shipping.** `/build` requires explicit founder go-ahead — Ralph runs cost real money and produce real commits.
* **Not retroactive.** Constitutional amendments are not applied to past specs or ADRs; existing artifacts remain valid against the constitution they were sealed under.

## Amendment process

* **Never edit `docs/constitution.md` in place.** Use `/constitution amend <topic>` — produces a new semver-versioned file, archives the previous version under `docs/constitution/archive/v<semver>-<date>.md`.
* Each amendment requires founder confirmation before write.
* Amendments are not retroactive — past specs and ADRs are not re-evaluated against new principles.
* Bump classification per `/constitution` skill's versioning rubric: MAJOR (removes a principle, reverses a rule, changes a state-machine), MINOR (adds a principle, adds a constraint, adds a section), PATCH (clarifies wording, fixes typos, expands examples).

## Amendment log

* **v1.0.0 (2026-05-14):** initial seed from north-star + idea-brief-v1.md via shortcut /discovery exit. Architectural constraints section stubbed with tooling baseline + free-tier obligation; expects MINOR amendments as the first ADRs land.
