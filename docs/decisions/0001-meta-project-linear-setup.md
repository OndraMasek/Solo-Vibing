# D-0001 — Meta-project Linear setup

**Date:** 2026-05-11
**Status:** Active
**Class:** Strategic
**Linked Linear issue:** SOL-9

## Context

The meta-project (Solo-Setup) needs a working surface for decisions, work tracking, and chat→code propagation. Options were (A) reuse SDG Linear workspace with a new team, (B) create a new Linear workspace, (C) use GitHub Issues only, (D) hybrid.

## Decision

Create a new team `Solo Claude Stack` (prefix `SOL`) within the existing `test-docs-generator` Linear workspace. Three projects in the team:

- `Decisions` — Q-NNN decision register
- `Backlog` — active work items
- `Sync Queue` — chat→code propagation

Upgrade the workspace to Linear Standard plan ($10/month) to accommodate the third team without affecting the existing `omasek` and `SDG` teams (free tier is capped at 2 teams).

## Consequences

- ~$10/month operating cost
- Two remaining team slots in workspace for future general/multi-project use
- The public stack recommendation for solo founders (who won't all upgrade to Standard) needs a different pattern — captured as SOL-14 (Q-D, single-team-multi-project pattern)
- Linear labels `type:decision`, `type:design`, `type:infra`, `type:content`, `scope:sealed`, `scope:living`, `long-lived` created at SOL team scope (workspace-wide creation was blocked by existing omasek team-scoped duplicates — captured as a Linear MCP gotcha for the public docs)

## Alternatives considered

- **A. Reuse SDG team with project prefixing.** Rejected — SDG team is already 7-project-dense; mixing meta-project work creates navigation friction.
- **C. GitHub Issues only.** Rejected — the workflow this project documents IS Linear-spine; using GitHub Issues for the meta-project breaks dogfooding.
- **D. Hybrid.** Rejected as premature optimization.
