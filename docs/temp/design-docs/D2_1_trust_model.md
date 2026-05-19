# D2.1 — Trust model (v2)

**Status:** Design.
**Phase:** 2.
**Resolves:** F-1 (subagent reports unverified — foundational), F-2 (gates bypassable; logged not prevented), F-7 (no concurrency control — per-resource lock primitive).
**Companion:** D2.2 (session auto-management) implements the enforcement layer; this doc defines the contract layer. The `cascade:run-state` schema introduced here is shared with D2.2.

## Changelog — v1 → v2 (applied 2026-05-18)

Founder verification round produced seven decisions (`D2_1_revision_decisions.md`). Applied to this revision:

| # | Topic | v1 → v2 | Where |
|---|---|---|---|
| 1 | Subagent manifest authorship | Confirmed: parent writes from independently re-read transcript. | Caller-side verification → Subagent verification. No edit. |
| 2 | `cascade:run-state` canonicality | Confirmed: filesystem canonical, Linear mirror. | Schema preamble. No edit. |
| 3 | Lock grain | **Rewritten.** Doc-level halt-and-lock → per-resource write locks. `current_stage` (singular) → `active_stages[]`. New `resource_locks[]` array. Concurrent same-product stages first-class. | `cascade:run-state` schema + Lock semantics subsection. |
| 4 | Spec checksum grain | **Rewritten.** `spec_sha256` (whole-file) → `ac_list_sha256` (bulleted AC entries only). Pulled forward from v0.2.1 deferral. | `input_provenance` field, /specify and /review verifier predicates, Provenance binding section. |
| 5 | `/accept-taint` waiver | **Removed.** No waiver. Taints clear only via `--reconcile` re-run (per D4.5). | Tainted-artifact propagation section. |
| 6 | Subagent verifier hook type | Confirmed default: deterministic `command` hook; agent hook reserved for predicates requiring genuine LLM judgment. D2.2 owns the per-predicate cut. | Open questions to D2.2 — Q3 reframed. |
| 7 | Tainted-artifact tracking topology | **Rewritten.** Centralized `cascade:run-state.tainted_artifacts[]` → distributed `is_tainted: bool` + `taint_reason` on each manifest. `cascade:run-state` retains only a derived count. Status doc renders "What's broken" by scanning manifests. | Common manifest fields + Tainted-artifact propagation section. |

**Knock-on, not in this doc:** D4.5 simplifies (no waived-not-cleared state). D1's Status doc render path changes (scan manifests, not read central list). `build-SKILL.md`'s "Spec checksum (load-bearing)" precondition needs an update to AC-list grain — flagged as a v0.2 publication-pass follow-up.

## Problem

The Bomber dogfood produced three back-to-back `scope:built` tickets on a game with no rendered output. The cascade trusted each stage's self-report — "AC checkboxes flipped, smoke gate green, four-hat sealed" — because nothing forced the parent to verify the claim against an observable artifact. Five distinct failure modes collapse to one root cause: **the cascade is built on trust where it needs to be built on verification.**

Wang's January 2026 critique put it bluntly: a process that records every fact about its own success while shipping a broken artifact is performing verification theater. The fix is not more logging. The fix is a contract that says: **no stage proceeds until the next stage has independently verified the previous stage's postconditions against observable evidence.**

F-1 is the headline. F-2 (a gate logging-not-preventing bypass) is the same failure expressed at the gate level. F-7 (concurrency) is the same failure under a different load — two stages racing to write the same shared product doc produces the same "I said it was done" pathology.

## Core principle

**Don't trust, verify. Bind everything that claims completion to evidence the parent can re-examine.**

Three pillars:

1. **Structured postconditions.** Every cascade stage emits a machine-checkable manifest of what it produced. Not prose. Not "completed successfully." Field-by-field, hashable, parseable.
2. **Caller-side verification.** The next stage refuses to start until it has loaded the previous stage's manifest, recomputed the evidence, and confirmed match. The producer's claim is necessary but never sufficient.
3. **Provenance binding.** Every artifact carries a chain of `who-sealed-it / against-what-input / at-what-checksum`. A tampered or replaced input invalidates the chain and visibly taints every downstream artifact derived from it.

The contract is independent of the enforcement mechanism. D2.2 picks the hooks. D2.1 defines what they must check.

## The `cascade:run-state` schema

A single JSON document per consumer at `docs/.solo-run-state.json` (filesystem-canonical) and mirrored to a Linear document `[<MARKER>-DOC-NNN] cascade: run-state` under the Product project (durable mirror). The document is the multi-stage tracker (F-7) and the postcondition handoff carrier (F-1 / F-2). D2.2 reads and writes it from hooks; this doc defines its shape.

```json
{
  "schema_version": "2.1-v2",
  "marker": "BOM",
  "active_stages": [
    {
      "name": "build",
      "ticket": "SOL-117",
      "started_at": "2026-05-18T14:32:11Z",
      "pid": 48213,
      "owner_session_id": "claude-cli-9f2a...",
      "owner_host": "ondrej-mbp"
    },
    {
      "name": "specify",
      "ticket": "SOL-118",
      "started_at": "2026-05-18T15:01:02Z",
      "pid": 48999,
      "owner_session_id": "claude-cli-7b1e...",
      "owner_host": "ondrej-mbp"
    }
  ],
  "last_completed_stage": {
    "name": "review",
    "ticket": "SOL-115",
    "completed_at": "2026-05-18T13:08:44Z",
    "postcondition_manifest_path": ".cascade/manifests/SOL-115-review.json",
    "postcondition_manifest_sha256": "a3f8...e2"
  },
  "resource_locks": [
    {
      "resource": "docs/product/Status.md",
      "held_by": "wrap:SOL-117",
      "acquired_at": "2026-05-18T15:42:00Z",
      "expires_at": "2026-05-18T15:42:30Z",
      "sentinel_path": "docs/.solo-locks/Status.md.lock"
    }
  ],
  "tainted_artifact_count": 0,
  "linear_sync": {
    "last_read_at": "2026-05-18T14:32:09Z",
    "ticket_cache": {
      "SOL-117": { "last_known_completedAt": null, "last_known_status": "In Progress" }
    }
  }
}
```

The top-level fields are not optional. Every stage entry writes the full document. Partial writes are detected by recomputing the doc-level sha256 on read.

`active_stages[]` is unordered. A stage appends its entry on start and removes it on exit (including failure exit). An entry persisting past its owner's PID indicates an orphaned stage and is collected by the recovery path described below.

`tainted_artifact_count` is **derived**, not authoritative. It is recomputed on every `cascade:run-state` write by scanning all manifests for `is_tainted: true` (see Tainted-artifact propagation). The authoritative state lives on the manifests themselves; the count is a cheap pointer for the Status doc renderer and for the founder's 30-second read.

**Per-resource lock semantics (F-7).** Locks are per shared product doc, acquired at write time, released on write completion. The locked resources are the shared product mirrors per D1 (Status, architecture, data-model, journeys) plus the `cascade:run-state` document itself. Acquisition is atomic via O_CREAT|O_EXCL on a sentinel file in `docs/.solo-locks/`. A stage that fails to acquire halts the write with a diagnostic naming the current holder and the lock's age; the stage itself does not exit, it retries with exponential backoff up to a configured ceiling (default: 5 attempts over 30 seconds). Release writes the release into the producing manifest's `outputs.lock_releases[]` field. Expiry default 30 seconds; past expiry the lock is treated as orphaned and may be broken by the next requester after re-reading filesystem state.

**Concurrent same-product stages are first-class.** A `/build` of SOL-117 running for 90 minutes does not block a `/specify` of SOL-118 starting in the same product; both appear in `active_stages[]` simultaneously. The conflict surface is at the write-of-a-shared-doc level, not the stage level. The motivating case: founder running a long Ralph build in one terminal while drafting a new spec in another, both targeting the same product. v1's product-level halt-and-lock treated this as a mistake; v2 treats it as the supported workflow.

**Files private to a stage** (spec.md owned by /specify for that ticket; four-hat doc owned by /review for that ticket; `.cascade/manifests/<TICKET>-<stage>.json` owned by the producing stage) require no lock — only one stage writes them.

**Linear-sync sanity check.** Every read of a Linear ticket compares the just-read `status` against the just-read `completedAt`. If `completedAt != null` AND `status != "Done"`, OR `completedAt == null` AND `status == "Done"`, the read is stale (Linear's eventual consistency). The stage re-reads after a 2s backoff (up to 3 attempts) or halts with "Linear state inconsistent — manual reconcile". Detection is a one-liner; recovery is `--reconcile` per D4.5.

## Per-stage postcondition manifests

Every cascade stage produces a manifest at `.cascade/manifests/<TICKET>-<stage>.json`. The next stage refuses to start until the manifest exists, the manifest sha256 matches what the parent recorded in `cascade:run-state.last_completed_stage`, and every field in the manifest passes the stage-specific verification predicates below.

Manifests are append-only. Re-running a stage writes a new manifest at `<TICKET>-<stage>-v2.json` and updates the pointer; the old manifest stays as audit history. Re-runs via `--reconcile` (per D4.5) also write a new manifest, with `is_tainted: false` and `taint_reason: null` on the new version; the old manifest retains its tainted state for audit.

### Common manifest fields (all stages)

```json
{
  "stage": "build",
  "ticket": "SOL-117",
  "marker": "BOM",
  "schema_version": "2.1-v2",
  "produced_at": "2026-05-18T15:08:33Z",
  "produced_by": {
    "session_id": "claude-cli-9f2a...",
    "agent_type": "main" | "subagent:<type>",
    "transcript_path": ".claude/transcripts/9f2a.../session.jsonl"
  },
  "input_provenance": {
    "spec_path": "docs/specs/0042-bomb-detonation/spec.md",
    "ac_list_sha256": "7c1a...4b",
    "four_hat_doc_id": "[BOM-DOC-0023]",
    "four_hat_seal_sha256": "9d3e...22",
    "parent_manifest_sha256": "a3f8...e2"
  },
  "outputs": { /* stage-specific, defined below */ },
  "is_tainted": false,
  "taint_reason": null,
  "self_attestation": "BUILT" | "PLANNED" | "SPECIFIED" | "...",
  "manifest_sha256": "<sha256 of this manifest with manifest_sha256 field empty>"
}
```

**`produced_by.transcript_path` is load-bearing.** For subagent stages (four-hat-user, four-hat-engineer, agent-spawned validators), this is the `agent_transcript_path` surfaced by Claude Code's `SubagentStop` hook — a filesystem path to the full JSONL of the subagent's session. The parent can independently re-read it to verify the subagent did what it claimed. The subagent's `last_assistant_message` ("✓ all four hats run, no objections") is treated as a hint, never as evidence.

**`input_provenance.ac_list_sha256`** is the sha256 of the spec's bulleted acceptance-criteria entries, not the whole spec file. Extraction: parse the spec's `## Acceptance Criteria` section, take all top-level bulleted lines, strip the leading bullet marker and surrounding whitespace per line, normalize line endings to `\n`, concatenate with single `\n`, sha256. This binds the contract that matters (testable claims) without invalidating the chain on every prose edit to motivation, glossary, or commentary sections. Per-AC hashing (one hash per entry) remains deferred to v0.2.1+.

**`input_provenance.four_hat_seal_sha256`** is also an AC-list hash — what the four-hat sealed at review time. The build-time verifier predicate is: recomputed `ac_list_sha256` of the current spec == `four_hat_seal_sha256` loaded from `/review`'s manifest. Mismatch halts.

**`input_provenance` chains backward.** Every manifest names the manifest sha256 of the stage it consumed. A tampered upstream manifest produces a checksum mismatch at the next stage's pre-flight, halting the cascade.

**`is_tainted` / `taint_reason`.** A manifest is born with `is_tainted: false, taint_reason: null`. Either field is updated only by:
- The producing stage itself, if its own verifier predicate failed but it wrote a manifest anyway for audit (rare — halts usually prevent manifest writes).
- A downstream stage that detects an `input_provenance` chain crossing an already-tainted manifest. The downstream stage's manifest is written with `is_tainted: true` and `taint_reason` naming the upstream offender.
- A `--reconcile` re-run, which writes a new manifest with `is_tainted: false`; the prior tainted manifest is preserved as audit history (append-only).

**`self_attestation`** is the only field the producing stage gets to assert without evidence. Everything else is recomputable by the verifier.

### Stage-specific postcondition fields

| Stage | `outputs` field | Verifier predicates |
|---|---|---|
| `/onboard` | `linear_projects_created[]`, `status_doc_id`, `marker`, `config_path` | All six projects + Status doc reachable via Linear API; `docs/.solo-config.json` parses and contains `marker`. |
| `/specify` | `spec_path`, `ac_list_sha256`, `failing_test_seed[]`, `acceptance_criteria[]`, `decomposition_strategy` | Spec file exists; recomputed `ac_list_sha256` matches; each AC has at least one named test in `failing_test_seed`; strategy is one of {walking-skeleton, api-boundary, capability-cluster, refactor-spike, hybrid}. |
| `four-hat-user` (subagent of `/specify`) | `objections[]`, `hat_id="user"`, `concluded_at` | Subagent transcript contains the priming text and either an explicit "no objections" line or `objections[].len > 0`. Recompute from `transcript_path`. |
| `four-hat-engineer` (subagent of `/specify`) | as above with `hat_id="engineer"` | as above |
| `/review` (four-hat coordinator) | `four_hat_doc_id`, `seal_sha256`, `objections_resolved[]`, `unresolved_count` | All four hat manifests exist and chain to this one; `unresolved_count == 0`; Linear doc has the sealed AC-list checksum recorded; `seal_sha256` recomputes against the spec's current AC list. |
| `/plan` | `child_tickets[]`, `parent_ticket`, `total_children`, `dag_path` | Every ticket in `child_tickets[]` is reachable in Linear and has `scope:planned`; parent is `scope:specified`; child count > 0. |
| `/update-linear` | `tickets_updated[]`, `diff_sha256` | Each ticket's current Linear state matches the diff; Linear-sync sanity check passes for each. |
| `/build` (spawn) | `branch`, `ralph_dir`, `pid`, `pid_alive_at` | `.ralph/<TICKET>/run.pid` exists, points to a live process; branch checked out; lockfile present. |
| `/build` (finalize) | `commit_sha`, `iteration_count`, `cost_usd`, `backpressure_log_paths[]`, `fix_plan_unchecked_count`, `failing_test_seed_status[]`, `lock_releases[]` | `commit_sha` exists in git; `fix_plan_unchecked_count == 0`; every test in `failing_test_seed_status[]` recomputes to `passing`; backpressure log latest entry shows zero failures; every entry in `lock_releases[]` is a resource that was held by this stage and is now released. |
| `/wrap` | `linear_label_transition`, `done_project_id`, `arch_doc_updated`, `data_model_doc_updated`, `journeys_doc_updated`, `fs_mirror_sha256`, `linear_mirror_sha256`, `lock_releases[]` | Label is `scope:built` in Linear; ticket moved to Done; each "updated" claim recomputes to a hash that differs from pre-wrap; filesystem `docs/product/*.md` sha matches Linear doc sha; lock releases match acquisitions. |
| `/verify` | `milestone_id`, `perceptual_gate_status`, `journeys_doc_post_ship_sha256` | All children of milestone are `scope:built`; perceptual gate evidence (screenshot, screencast path, or N/A for non-UI) present and re-readable. |
| `/retro` | `findings[]`, `arch_updates_proposed[]`, `lessons_summary_line` | Linear retro doc exists with sealed sha; Status doc lessons-line updated. |

For every stage above, the **verifier predicates run before the next stage starts**, not at the same stage as production. The producer cannot mark itself verified.

## Caller-side verification protocol

Pre-flight for every cascade stage:

1. **Read `cascade:run-state`.** Confirm the document parses and its top-level sha is consistent.
2. **Load the previous stage's manifest** from `last_completed_stage.postcondition_manifest_path`. Halt if the file is missing.
3. **Recompute manifest sha256** with `manifest_sha256` field zeroed. Halt on mismatch with `last_completed_stage.postcondition_manifest_sha256`.
4. **Check upstream taint.** If the loaded manifest has `is_tainted: true`, this stage's manifest will inherit the taint (see Tainted-artifact propagation). Proceed under taint — do not halt — but the inheritance is recorded.
5. **Walk `input_provenance` backward one step.** Verify the manifest's named parent matches what `cascade:run-state` says the parent should be. Halt on chain break.
6. **Run stage-specific verifier predicates** against the manifest's `outputs`. Each predicate is independent and recomputed from observable evidence (filesystem, Linear, git, transcript). Halt with the failing predicate named.
7. **Linear-sync sanity check** on every Linear read this stage performs (not just at pre-flight).
8. **Append to `active_stages[]`,** acquire any required resource locks at the write moment (not at pre-flight), proceed.

On halt at any step, the stage writes a diagnostic to `.cascade/halt/<TICKET>-<stage>.txt`, removes its `active_stages[]` entry, releases any held resource locks, and surfaces a halt card naming the predicate that failed. No partial progress is recorded.

**Subagent verification (the F-1 fix in concrete terms).** When a stage spawns a subagent (four-hat-user, four-hat-engineer, an agent-type hook), the parent stage:

1. Captures `agent_transcript_path` from `SubagentStop` (Claude Code's hook payload field).
2. Reads the transcript independently — not via `last_assistant_message`.
3. Runs the subagent-stage's verifier predicates against the transcript content. For a four-hat run, that means parsing the transcript for the priming text, the structured objections section, and the concluding seal line.
4. Writes the subagent's manifest from the parent's verified read, not from the subagent's claim.

The subagent never writes its own manifest. The parent writes it on the subagent's behalf, populated only from independently-re-read evidence. A subagent that lies in `last_assistant_message` produces no manifest and the parent halts.

This is **structural verification**, not a stamp step. The parent's authorship of the manifest is what gives the manifest its trust — there is no separate "verified by parent" flag to be forged. If the manifest exists at `.cascade/manifests/<TICKET>-<subagent>.json`, it was written by the parent against re-read transcript evidence by construction.

## Provenance binding (F-2)

The four-hat gate failed in Bomber because nothing prevented the cascade from continuing past an un-sealed four-hat. The gate logged the absence and proceeded. Fix:

- **Every manifest names its input provenance.** `/build`'s pre-flight refuses to fire if `input_provenance.four_hat_doc_id` is empty OR if the Linear four-hat doc's `seal_sha256` field is missing OR if the recomputed `ac_list_sha256` of the linked spec differs from what the four-hat sealed.
- **Provenance is checked, not logged.** "AC-list sha differs from sealed value" is a halt condition, not a warning line. This is the difference between F-2 as written (gate bypassable; logged not prevented) and F-2 as resolved.
- **The four-hat seal is the seam.** `/review` writes `four_hat_doc_id` and `seal_sha256` (the AC-list hash at seal time) to its own manifest. `/build`'s verifier predicate insists the recomputed `ac_list_sha256` at build time matches `seal_sha256`. Edit an AC after the four-hat without re-sealing? The build halts. Edit motivation prose? The build proceeds — that was not what the four-hat sealed.

The existing `build-SKILL.md` already implements this pattern for the four-hat → build edge at whole-spec grain (`Spec checksum (load-bearing)` precondition). Aligning that to AC-list grain is a follow-up flagged at the top of this changelog.

## Tainted-artifact propagation (F-2 continued)

When a stage halts on a failed predicate, the cascade does not silently retry from clean state. Taint state is recorded on the manifest of the affected stage — not in a central list — and propagates downstream via the `input_provenance` chain.

**Where taint lives.** Each manifest carries:

```json
"is_tainted": true,
"taint_reason": {
  "type": "predicate_failure" | "upstream_inherited",
  "predicate": "fs_mirror_sha256 != linear_mirror_sha256",
  "detected_at": "2026-05-18T15:42:11Z",
  "upstream_tainted_manifest": null
}
```

For `type: "upstream_inherited"`, `upstream_tainted_manifest` names the manifest path of the offending ancestor. `predicate` is omitted. The detecting stage walks `input_provenance` until it finds the originating `predicate_failure` and records the chain length in `taint_reason.inheritance_depth` for diagnostics.

**Propagation rule.** Any cascade stage whose `input_provenance` chain crosses a tainted manifest writes its own manifest with `is_tainted: true` and `taint_reason.type: "upstream_inherited"`. Downstream stages do not halt on inherited taint — they continue, but the taint follows the artifact chain.

**Visibility.** The Status doc renders a "What's broken" entry for every active taint by scanning `.cascade/manifests/` for files with `is_tainted: true` and grouping by originating predicate. The 30-second read tells the founder before they ask. Per D1, Status is the fabrication detector — a taint that doesn't appear there is itself a taint. The render path is a filesystem scan, not a central-list lookup; the `cascade:run-state.tainted_artifact_count` field is a cached aggregate, validated by recompute at render time.

**Clearing.** A taint is cleared by re-running the responsible stage with `--reconcile` (per D4.5). The re-run writes a new manifest with `is_tainted: false`, properly verified end-to-end. The prior tainted manifest is preserved at its versioned path (e.g., `SOL-117-wrap.json` retained alongside the new `SOL-117-wrap-v2.json`) as append-only audit history. There is no waiver. There is no `/accept-taint`. Every clear is a real re-verification.

**No exceptions.** The Bomber dogfood's failure mode was a cascade that logged its own brokenness and proceeded. v2 preserves the audit log, removes every "but accept it anyway" path, and forces the only clear-path through a real re-run of the responsible stage.

## What this doc does not cover

- **Content-addressed storage of artifacts.** Hashing references files at known paths. A more rigorous design would store artifacts in a CAS keyed by sha. Deferred to v0.3+ unless a path-rewriting failure mode surfaces.
- **Cryptographic attestation.** sha256 + filesystem provenance is the trust boundary. Public-key signing, third-party notarization, supply-chain attestation — none of that is in v0.2. The threat model is "the cascade lies to itself," not "an external attacker forges Linear documents."
- **Per-AC checksums** (per D0.2 deferral; partial pull-forward in v2). AC-list hashing — sha256 of the concatenated bulleted AC entries — is the v0.2 grain. Per-AC hashing (one hash per individual AC, enabling granular invalidation when one AC changes) remains v0.2.1+ deferred. The AC-list grain catches the failure mode that motivated the pull-forward (whole-file too coarse: prose edits invalidating the seal) without the implementation burden of per-AC tracking.
- **Full distributed locking** (per D0.2 deferral). Per-resource O_CREAT|O_EXCL sentinels are sufficient for a solo founder on one machine. Multi-host locking is v0.3+.
- **Hook configuration to enforce all of the above.** That is D2.2's entire scope. This doc says *what* must be checked; D2.2 says *which hook event runs the check*.

## Open questions handed to D2.2

These are implementation decisions that depend on the May 2026 hook surface (see `D2_2_hook_surface_research.md`). Listed here so D2.2 does not re-derive them.

1. **Which hook event runs each stage's verifier predicates.** Candidates: `SubagentStop` for subagent verification, `PostToolUse` for filesystem/Linear writes, `Stop` (with `decision: block`) for parent-stage gates. The constraint is that hooks may not fire at `max_turns` (per hook-surface research), so verifier predicates must also be invocable as a standalone CLI for resume scenarios.
2. **Where `cascade:run-state` lives during a session.** Filesystem-canonical (decision 2). The hook that writes both filesystem and Linear has to handle "Linear write fails" — default per the `build-SKILL.md` `--sync` pattern: commit locally, mark pending, allow `--reconcile` to reconcile later. D2.2 confirms or revises.
3. **Per-predicate hook-type cut.** Default is deterministic `command` hooks (decision 6); `agent` hooks reserved for predicates genuinely requiring LLM judgment (e.g., "does the four-hat objection list cover the user-journey edge cases?"). D2.2 produces the per-predicate cut list — which predicates earn an agent hook, which stay command.
4. **`PreCompact.custom_instructions` persistence.** Use the field to persist `cascade:run-state` summary into the compacted context, so a `SessionStart` with `source=compact` can re-load without re-reading from disk. Detailed mechanics in D2.2.
5. **Stop/SubagentStop schema quirk.** Output is top-level `{"decision": "block", "reason": "..."}` — not `hookSpecificOutput` (per Anthropic issue #15485, confirmed in hook-surface research). D2.2's hook scripts must emit the correct shape; spelling it out here to save a debugging cycle.

## Composition citation

Pattern adopted from Wang's January 2026 critique of self-attesting agentic systems (the "verification theater" framing). Manifest-chain pattern adopted from Sigstore / in-toto layouts, simplified to single-party. Subagent-transcript-as-evidence pattern is enabled by Claude Code's `SubagentStop` hook surface (Anthropic, hooks reference April 2026, surfaces `agent_transcript_path` in the hook input). The contribution here is the integration into the cascade — the trust contract as a per-edge predicate set anchored in observable artifacts — not the hashing or manifest mechanics.
