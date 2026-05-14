---
name: audit-self
description: Verifies the repository is bootstrapped through its own Solo-Setup workflow — config, constitution, north-star, and at least one spec exist. Halts with a diagnostic listing each missing artifact. Read-only; no writes. Fires on "/audit-self", "audit-self", "self-audit", "check setup". Enforces the self-application principle stated in CLAUDE.md.
---

# audit-self

Self-application audit. Confirms the repository has been bootstrapped through its own cascade. References rules: `completion-status.md`, `naming.md`. No agent invocation, no writes.

## Trigger

- User: "/audit-self", "audit-self", "self-audit", "check setup"

Not part of any cascade. Read-only.

## Behavior

1. **Check artifacts** — verify each of the following exists and is non-empty:

   | Artifact | Path | Required source |
   |---|---|---|
   | Workflow config | `docs/.solo-config.json` | /onboard step 5 |
   | North-star | `docs/product/north-star.md` | /discovery approve exit |
   | Constitution | `docs/constitution.md` | /constitution seed mode |
   | At least one spec | `docs/specs/NNNN-*/spec.md` (any) | /specify seal |

2. **Optional warnings (not halt-triggering):**
   - `docs/onboarding/codebase-map.md` missing on a brownfield repo (heuristic: > 50 non-template files in the working tree).
   - `docs/discovery/idea-brief-v*.md` missing — /discovery's idea-brief is the constitution's authoring source; missing means /constitution reseed cannot run cleanly.

3. **Render report** in chat. No writes.

   On full pass:

   ~~~
   Self-audit: DONE.

   * Config: docs/.solo-config.json (marker=<MARKER>)
   * North-star: docs/product/north-star.md
   * Constitution: docs/constitution.md v<semver>
   * Specs: <count>
   ~~~

   On any required artifact missing — render a `BLOCKED` halt-card per `docs/templates/halt-messages.md` §missing-context, listing each missing artifact and the skill that creates it:

   ~~~
   ## Halt: /audit-self BLOCKED

   **Reason:** Self-application broken — required artifacts missing.

   **Recommended next action:**
   /onboard

   /onboard cascades through /discovery → /constitution and produces the missing artifacts.

   **Alternatives:**
   1. If onboard already ran but a single artifact was deleted, restore it via the responsible skill: /constitution reseed (restore constitution); /discovery (restore north-star + idea-brief); /specify <topic> (mint first spec).

   **Diagnostic context:**
   - Missing: <list of missing paths and responsible skill>
   - This repository is the Solo-Setup itself; CLAUDE.md states "Self-application is the test." Missing artifacts mean the cascade cannot run against the repo that documents it.
   ~~~

## Same-turn write rules

Read-only. `write-discipline.md` does not apply.

## Outputs

| Artifact | Location |
|---|---|
| Audit report | Chat message |

## Completion status

Per `completion-status.md`:

- `DONE` — all four required artifacts exist and are non-empty.
- `DONE_WITH_CONCERNS` — all required artifacts exist, but an optional warning fires (codebase-map missing on a brownfield repo, idea-brief missing).
- `BLOCKED` — one or more required artifacts missing. Halt-card rendered.
- `NEEDS_CONTEXT` — not applicable for a read-only audit.

## Chains

None. Terminal. /audit-self is a verification surface, not a cascade stage.

## Notes

**Why this command exists.** CLAUDE.md states *"Self-application is the test. This repo is built with the workflow it documents. If the stack cannot be used to build the stack, the stack is broken."* /audit-self makes that principle mechanically checkable. Without it, the principle is aspirational; with it, drift is a halt.

**Why not extend /status.** /status is read-only and renders a Linear dashboard. /audit-self verifies the local repository's bootstrap state. They answer different questions: /status is "what work is active," /audit-self is "is this repo correctly bootstrapped."

**Why not auto-fire.** /audit-self runs only when the founder invokes it. Auto-firing on every session would noisy-halt on fresh forks; running it as a CI check is a v0.2 candidate.

**Recovery is incremental.** A repo missing the constitution but having a north-star runs `/constitution reseed`, not a full re-onboard. The halt-card's Alternatives section names the targeted skill per missing artifact.
