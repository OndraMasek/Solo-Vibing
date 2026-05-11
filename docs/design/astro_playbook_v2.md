# The Linear-first Claude Code workflow

> **Pre-v0.1 design history.** Migrated from the Claude.ai meta-project KB on 2026-05-11. References to the old working name `solo-claude-stack` are intentionally preserved as historical record; the current working name is `Solo-Setup` (SOL-1). User-facing v0.1 docs will live in `docs/` (numbered 00–13) and will be drafted *from* these design notes during weeks 2–4.

**A practical playbook for solo developers using Claude (chat) and Claude Code (terminal) on the same project — without copy-pasting prompts between them.**

This document distills lessons from adapting the workflow to a real project (a bilingual Astro consulting site). It's the v2 of an earlier blueprint, updated with the failure modes we hit and the rules we wrote to prevent them.

If you only read one paragraph: the leverage is one trick — **Linear is the shared workspace where chat-Claude writes specs and Claude Code reads them**. You stop being a courier between two AIs. Everything else in this document is the discipline that makes that one trick stick.

---

## The problem

The default Claude workflow has two AIs that don't talk to each other:

- **Chat Claude** — good at planning, writing specs, thinking through tradeoffs
- **Claude Code** — good at executing in your terminal, editing files, opening PRs

Most people bridge them by copy-pasting prompts. That's slow, loses context, and forces you to be the messenger. After a few weeks you have stale instructions, lost decisions, and branches piling up.

This workflow replaces all of that with a Linear ticket queue and a few hooks.

---

## The mental model: three actors, one bridge

| Actor | Role |
|-------|------|
| **You** | Direct the work, review PRs, merge |
| **Chat-me** | Plans, writes specs, makes strategic decisions, writes them into Linear in the same turn |
| **Code-me** | Reads specs from Linear, executes, opens PRs, stops at PR open |
| **Linear** | Shared source of truth — the bridge |

Three rules govern this:

1. **Same-turn writes.** When chat-me agrees to something with you, it writes it into Linear *in the same message*. No "I'll note that."
2. **No prompt handoffs.** Anything you'd put in a "paste this into Claude Code" instruction belongs in a Linear ticket. You don't carry text between windows.
3. **Code-me stops at PR open.** You eyeball the diff and merge. This is the only human gate on `main` for a solo dev.

If you internalize these three rules, the rest is bookkeeping.

---

## Linear setup (15 minutes)

Create one Linear team with a short prefix (e.g. `ABC`). Inside it, create two projects:

| Project | Purpose |
|---------|---------|
| **Backlog** | Real work items: features, bugs, infra, ADRs |
| **Sync Queue** | Chat→code propagation tickets only. The bridge. |

Create these team labels:

| Label group | Members |
|-------------|---------|
| Type | `type:feature`, `type:bug`, `type:content`, `type:infra`, `type:decision`, `type:copy` |
| Sync lifecycle | `sync:pending` → `sync:synced` |
| Scope (Sync Queue tickets) | `scope:sealed` (default), `scope:living` |
| Lifecycle | `long-lived` (used on ADRs) |
| Tracks | `track:<area>` — created on demand for parallel work |

Long-form prose (site spec, compliance briefs, the residual-risks watchlist) lives as team-level **Linear Documents**. Documents are durable, prose-friendly, and chat-me reads them at session start.

---

## The sync mechanism

When you and chat-me agree on something that needs code action, this happens:

1. **Chat-me writes a Sync Queue ticket** in Linear, same message as the agreement. Body contains the full spec — what, where, acceptance criteria. Labels: `sync:pending`, `scope:sealed`.
2. **You** start Code-me in your terminal.
3. **Code-me** queries Linear at session start, finds `sync:pending`, reads the matching ticket.
4. **Code-me** creates a branch named `<PREFIX>-<ID>-<slug>`, does the work, opens a PR, comments the PR URL on the ticket.
5. **Code-me stops at PR open.** Posts a comment "ready for review."
6. **You** merge via `gh pr merge --squash --delete-branch`.
7. **Post-merge close-out** — next Code-me session, or a GitHub Action, flips `sync:pending` → `sync:synced` and closes the ticket.

You never paste a prompt between windows. Code-me reads from Linear at step 3.

The **ticket body is the contract.** Not the chat conversation, not your memory, not chat-me's summary. If it's not in the Linear ticket body, it doesn't get built. This single rule eliminates 90% of spec-drift problems.

---

## ADRs: the durable knowledge layer

Decisions deserve to survive across sessions and not get re-litigated. Mark them in writing.

**Strategic ADRs** (compliance, vendor, hosting, content policy, major architecture):
- Linear issue, labels `type:decision` + `long-lived`, status Done
- Mirrored to `docs/decisions/00NN-<slug>.md` in the repo via a Sync Queue ticket
- Linear is canonical; the repo file is the mirror

**Build-time ADRs** (library version pins, file structure, test setup, formatter config):
- `docs/decisions/00NN-<slug>.md` only — no Linear issue
- One-line back-reference comment on the parent Backlog issue

**ID space:** `D-001`, `D-002`, … shared across both kinds. Non-contiguous IDs in Linear are expected (build-time ADRs don't get Linear IDs).

When an ADR needs an update:
- **Amendment** — small change to the same decision. Add "Amended: `<date> — <reason>`" header line, edit in place.
- **Supersession** — decision genuinely changes. Create a new ADR, point old → new with "Superseded by D-NNN" in the old Status line.
- **Deprecation** — no longer applies, no replacement. Change Status to "Deprecated `<date>` — `<reason>`".

**Never delete or rewrite history.** ADR IDs are referenced from many places. Permanence is the point.

---

## Hooks (the enforcement layer)

Two `.claude/hooks/` scripts handle the discipline:

**`session-start-linear.sh`** (SessionStart hook) — runs every time Code-me starts. Reports current branch, infers Linear issue ID from branch name, lists stale merged-but-not-deleted branches, reminds Code-me to query the Sync Queue.

**`pre-edit-branch-check.sh`** (PreToolUse hook, matching `Edit|Write|MultiEdit`) — blocks edits on `main`/`master` with `exit 2`. Warns (non-blocking) if branch doesn't match `<PREFIX>-<ID>-<slug>`.

Both are short bash scripts. The PreToolUse blocker is what physically prevents the "I forgot to branch" mistake. Without it, you'll do that mistake more than once.

---

## Parallel work without sync incidents

The trickiest part of multi-actor workflows is when chat-me and Code-me are working at the same time. Without rules:

- Chat-me edits a ticket while Code-me is executing it → safety system halts ("scope creep")
- Two Sync Queue tickets touch the same file → PRs conflict at merge
- Two chat sessions create overlapping work → silent duplication

The rules that handle this:

**Default scope is sealed.** Every Sync Queue ticket is `scope:sealed` unless explicitly labeled `scope:living`. Code-me snapshots the ticket body at session start; that snapshot is the contract for the run.

**Pre-PR re-read.** Before `gh pr create`, Code-me re-fetches its ticket body and compares to the snapshot:
- `scope:sealed` → halt and ask if changed
- `scope:living` → continue silently if additive, halt if subtractive
- Also check `docs/decisions/` for any ADR newer than session start that contradicts the work

**Chat-me discipline.** Chat-me does NOT edit the body of an in-flight `scope:sealed` ticket. If a substantive scope change is needed, open a follow-up ticket. For small additive clarifications: flip to `scope:living`, leave a comment ("editing now — `<change>`"), then edit.

**Multi-chat hygiene.** Every chat session boots by reading: Sync Queue tickets updated in the last 24h, recent ADRs. Edits to recently-touched tickets are announced via comment first. Soft lock by convention, not enforced.

**Parallel tracks use worktrees, not branch-switching.** When you genuinely need to work on two things at once: `git worktree add ../project-feature-a ABC-12-feature-a`. Each worktree gets its own Code-me session. They physically can't collide.

**Merge conflicts are git's job.** Don't try to preempt file-level conflicts in Linear — git is the merge oracle, and re-implementing conflict detection in Linear adds friction without reducing risk.

---

## Merge policy

**Code-me stops after opening the PR. You merge.**

This is the only human gate on `main`. For a solo dev with no peer reviewer, it's also the only safety net. Don't skip it.

A ticket body can include the explicit string `"auto-merge OK"` to authorize Code-me to merge after CI passes. Reserved for typo fixes and dependency bumps. Use sparingly.

Resist the temptation to auto-merge everything. CI catches type errors and linter violations but not "I just rewrote your hook system and the new version blocks every edit." The eyeball check matters.

---

## Automation roadmap

Three tiers, in order:

**Tier 0 (current): manual workflow.** You start Code-me in a terminal. Chat-me writes specs. You merge. Prove the workflow end-to-end with several real PRs before automating.

**Tier 1: post-merge close-out GitHub Action.** On `pull_request.closed` with `merged == true`, parse the PR for Linear issue references, comment the PR URL on each, flip `sync:pending` → `sync:synced`, set state Done. ~2-3 hours to build. Also serves as your GitHub Actions + Linear API training wheels.

**Tier 2: Linear webhook → workflow_dispatch → headless Claude Code.** Linear fires a webhook when a Sync Queue ticket is created → a small endpoint (Cloudflare Worker or Vercel Function) triggers GitHub Actions `workflow_dispatch` → the workflow runs `claude -p` (headless mode) with a prompt template that reads the ticket and executes per CLAUDE.md. Result: chat creates a ticket → PR appears in minutes. No terminal. ~1-2 days.

**Explicitly skip: `@claude` GitHub mentions.** They replace "type a prompt in the terminal" with "type @claude in a GitHub comment" — same manual trigger, different surface. Building `@claude` as a stepping-stone is wasted effort once webhooks are live. (Keep `@claude` in mind for ad-hoc PR review or one-off questions — a different workflow.)

---

## The residual-risks watchlist

The workflow handles common cases well, but some risks remain. Track them in a Linear Document (team-level) titled "Workflow residual risks — watchlist." Each entry pairs:

- **The tell** — what it looks like when the risk bites (a detection signal)
- **What to do** — the recovery procedure

The five risks worth tracking from day one:

1. **Two tickets editing the same file in different sections** — the parallel-work area-level overlap check doesn't catch this
2. **Worktree branched from stale `main`** — Code-me builds PRs on outdated bases
3. **Old branches piling up** — SessionStart hook reports them; deletion is manual
4. **Tier 2 webhook race** (when it ships) — two PRs from near-simultaneous dispatches
5. **Worktree not removed after a track ends** — discipline, not enforced

When a risk bites *twice*, graduate it: open a Backlog fix ticket and possibly a new ADR. Mark the entry resolved.

---

## Mistakes I made (so you don't have to)

These are real. Each cost me 10-30 minutes.

### Hardcoded team prefix in the spec before the team was created

Linear auto-derives the team prefix from the team name. I wrote scaffolding assuming prefix `OMK` (from "omasek.com"); Linear gave us `OMA` (from "omasek"). Had to find-replace across seven files. **Fix:** create the team first, then write the prefix into specs.

### Promised a "bundle directory" that didn't exist on the user's machine

I prepared files in my sandbox and put them in a Sync Queue ticket referencing `~/Downloads/bundle/`. The user opened Claude Code and found nothing — the files only existed on my server. **Fix:** Sync Queue ticket bodies must be **self-sufficient.** File contents inline in code blocks. ADR mirrors fetched via Linear MCP. No external references to my sandbox.

### Referenced an ID before Linear assigned it

I wrote D-005's "Related" section referencing "OMA-10 — Tier 2 work ticket" before creating the Tier 2 ticket. Linear assigned OMA-10 to the ADR itself. **Fix:** create the dependent tickets first, *then* reference them. Or use placeholder language until the ID is real.

### Code-me shipped a partial PR

The first attempt at OMA-2 specified five files. Code-me shipped only the simplest one in the PR (the ADR mirror), then stopped. The other four files never landed. We had to split into a partial-completion + follow-up ticket. **Fix:** the scope:sealed default + pre-PR re-read is the protocol-level cure. The principle: if Code-me can't complete the full scope of a ticket in one run, it should halt and ask, not ship a partial PR.

### Two Sync Queue tickets that both edited CLAUDE.md

Different subsections, same file. Running them in parallel would conflict at merge. Caught manually. **Fix:** bundle related edits into one ticket. Risk R-001 on the watchlist.

### Designed automation without verifying CI exists

I wrote automation specs assuming Biome + vitest + `tsc --noEmit` run on every PR. Never asked whether they actually do. **Fix:** before specifying anything that depends on CI, send a read-only Sync Queue ticket asking Code-me to audit `.github/workflows/` and report back via comment.

### Workspace-wide vs team-scoped labels

Tried to create `sync:pending` as a team label; Linear rejected it because the label already existed at the workspace level (from another team). **Fix:** check `list_issue_labels` before `create_issue_label`. Workspace labels can be reused across teams.

---

## Adaptation checklist

For your next project:

- [ ] Create one Linear team with a short prefix (3-4 letters)
- [ ] Create two projects: `Backlog` and `Sync Queue`
- [ ] Create labels: `type:*`, `sync:*`, `scope:*`, `long-lived`
- [ ] Connect Linear MCP to claude.ai via OAuth
- [ ] Set up the GitHub repo with `CLAUDE.md` at root (start with the operational rules section)
- [ ] Add two hook scripts in `.claude/hooks/`: SessionStart + PreToolUse
- [ ] Write D-001 (ADR classification rule) as the seed ADR
- [ ] Paste chat-side custom instructions into the claude.ai project (same-turn writes, no prompt handoffs)
- [ ] Run your first real Sync Queue ticket end-to-end before automating anything

---

## What's load-bearing vs cosmetic

**Load-bearing — don't drop:**

- Linear MCP wired to claude.ai with write access
- Sync Queue as the chat→code propagation channel
- ADR ID space shared across strategic + build-time
- The PreToolUse hook blocking `main` edits
- The "Code-me stops at PR open" rule
- The chat-me discipline rules around in-flight tickets
- Same-turn Linear writes (chat-me writes in the same message as the agreement)
- The "ticket body is the contract" principle

**Cosmetic — adapt freely:**

- Two-project structure (could be more — separate `Customers`, `Outreach`, etc. for sales-touching projects)
- Specific label names
- Branch naming pattern (any convention works as long as the hook matches)
- Whether you use worktrees vs branch-switching for parallel work
- Specific automation tier sequencing (could skip Tier 1 if you're confident)
- Adversarial review protocols (some projects benefit; many don't)

---

## Anti-patterns

Things I had to actively unlearn:

- **"Paste this into Claude Code."** Anything you'd put in a paste-this-prompt instruction belongs in a Linear ticket. If you find yourself drafting a prompt for the terminal in chat, stop — write a ticket instead.
- **Editing CLAUDE.md without a ticket.** Every change to operational rules routes through the Sync Queue.
- **Marking a partially-completed ticket as Done.** Split into "completed portion via PR-NN" + follow-up ticket for the rest.
- **Deleting or rewriting ADRs.** Supersede or deprecate; never delete. ADR IDs are referenced from many places; rewriting them creates phantom references.
- **Skipping the manual workflow phase.** Building automation against an unproven workflow means debugging two things at once.
- **Asking chat-me to "remember" something instead of writing it down.** Memory is unreliable. Linear is durable.

---

## Final advice

The workflow is more discipline than tooling: two hooks, two Linear projects, ten labels, a `CLAUDE.md`, half a dozen ADRs. That's it.

The leverage comes from same-turn writes — chat-me writes to Linear in the same message as the agreement, never "I'll note that" — and the no-copy-paste rule — Code-me reads from Linear, never from a pasted prompt.

If you find yourself pasting prompts between chat and terminal, you've left the workflow. Stop, write the ticket, and try again.

---

## Appendix: Linear MCP gotchas

Specific quirks worth knowing before you build:

- `save_comment` needs `issueId` as the **identifier string** (`"ABC-42"`), not the UUID. Silent failures often succeed on retry without changes.
- `save_issue` accepts `parentId` and `relatedTo` as identifier strings or arrays of identifier strings.
- `save_document` requires **full content replacement** — partial updates aren't supported. Treat each update as a versioned rewrite.
- `get_document` uses the slug from the document URL, not the full URL.
- `project` parameter on `save_issue` accepts the project name string directly.
- Labels with `:` separators (`type:foo`, `sync:bar`) are workspace-wide if they exist anywhere in the workspace; you can't recreate them per-team.
- Linear auto-injects `<issue id="...">ABC-N</issue>` autolink wrappers when you write `ABC-N` in a ticket body. When mirroring to repo files, strip these wrappers and leave plain `ABC-N`.

---

*This playbook was distilled from the experience of setting up the workflow on one real project (a bilingual consulting site). Your mileage may vary; the load-bearing parts should travel.*
