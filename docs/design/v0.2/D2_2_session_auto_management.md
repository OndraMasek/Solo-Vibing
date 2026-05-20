# D2.2 — Session auto-management

**Status:** Design.
**Phase:** 2.
**Resolves:** F-3 (no auto-handoff — sessions tear at the context boundary), F-4 (token budget — no enforcement), F-5 (compact churn — no escape ramp).
**Companion:** D2.1 v2 (trust model) defines the verification contract; this doc defines the enforcement layer that runs it. Shares the `cascade:run-state` schema.

## Research-step resolutions

Four hook-surface items were parked in `D2_2_hook_surface_research.md`. Resolved here before drafting:

| # | Question | Resolution | Source |
|---|---|---|---|
| 1 | Does `mcp_tool` hook type pass full hook payload to the MCP tool, or just a subset? | Full hook payload (tool name, tool input, session context) is passed as the MCP tool's arguments. So `mcp_tool` is viable for predicates that have a corresponding MCP server tool. **Practical default still `command`** for v0.2 because no available MCP server exposes a "validate cascade predicate" tool out of the box — Linear MCP doesn't ship a consistency-check tool; we'd write the predicate inside our own command script either way. `mcp_tool` is a v0.3+ pull-forward candidate if we ship a `solo-mcp` server. | Anthropic hooks reference, April 2026; community guides Feb–May 2026. |
| 2 | Can `Setup` hook with `--init` create files outside `.claude/`? | Yes — Setup hooks have full project-relative filesystem reach. Used in the wild for dependency install, DB init, env scaffolding outside `.claude/`. **Caveat:** Setup only fires on `claude --init`, `--init-only`, or `--maintenance` (in `-p` print mode); it does NOT fire on normal startup. So `solo-init` scaffolding lives in Setup for the explicit init pipeline AND is duplicated idempotently in `SessionStart` source=startup for the more common path. | Anthropic hooks reference; claudefa.st Setup-hooks guide, Feb 2026. |
| 3 | Multiple `Stop` hooks returning conflicting `decision` values — exact behavior? | When multiple hooks return conflicting decisions, the most restrictive wins (`deny` beats `defer` beats `ask` beats `allow`); top-level `continue: false` overrides any `decision: "block"`. **However:** an open bug (anthropics/claude-code#10412) reports Stop hooks installed via the plugin system don't re-fire continuation correctly even when their decision is valid. **Design choice:** v0.2 uses a single Stop hook in `.claude/hooks/` (not via plugin) that orchestrates all completion checks internally and returns one consolidated decision. Avoids the conflict-resolution surface entirely. | Hooks reference; community guides; anthropics/claude-code#10412. |
| 4 | `async: true` hooks — block session end or fire-and-forget? | Fire-and-forget. "Async hooks cannot block actions since the triggering action has already completed; results delivered on next conversation turn." **Implication:** verification predicates that need their result to gate progression CANNOT be async. They eat the latency. Async is reserved for telemetry, logging, and post-hoc analytics that don't gate the cascade. | Hooks reference; morphllm.com Feb 2026; claudefa.st Mar 2026. |

These resolutions are reflected in the design below. Where uncertainty remains, the conservative default is taken and flagged.

## Problem

In Bomber, the dogfood session crossed the context horizon mid-build. Claude Code's auto-compact fired during a Ralph iteration. The compacted summary preserved the wrong things — surface phrasing of "what we were doing" but not the cascade's actual state (which manifest had sealed, which tickets were active, which locks were held). When the next stage tried to run, it inherited a poisoned context that looked plausible. Three `scope:built` tickets later, no rendered output existed.

Five distinct session-management failures collapse to one root cause: **session boundaries are negotiated by token count, but the cascade's safe handoff points are negotiated by stage state. The two are unrelated, and Claude Code's defaults choose the former.**

F-3 (no auto-handoff) is "we don't know how to leave gracefully." F-4 (no token budget) is "we don't know when we're approaching the edge." F-5 (compact churn) is "we don't have an exit ramp when compacting stops working." All three are the same gap: the cascade lacks an enforcement layer that knows the difference between a safe boundary and any other moment.

## Three-band threshold model

User-facing mental model is token bands; enforcement signal is the compact-cycle counter (which the system can observe reliably). The bands correlate roughly:

| Band | Approx tokens | Action |
|---|---|---|
| **Normal** | 0–200k | No intervention. Cascade runs unmodified. |
| **Opportunistic** | 200–300k effective (post-first-compact) | Allow next auto-compact, but **only at the next safe boundary**. PreCompact hook blocks mid-task compaction with a deferral reason; permits at boundary. |
| **Mandatory reset** | 300k+ effective (post-multiple-compact, signal-degraded) | At the next safe boundary, trigger full session reset instead of a third compact. Linear-mediated resume hydrates the new session. |

**Why cycles not tokens.** Claude Code's `/status` reports the current context size, but the hook surface does not give programmatic token counts in the payload as of May 2026. The compact-cycle counter is what the hooks can actually test — it increments deterministically on every PreCompact firing. The token bands above are the descriptive mental model; cycle count is the operational test:

- `compact_cycle == 0` (pre-first-compact) → normal
- `compact_cycle == 1` (post-first-compact, PreCompact fires again) → still allowed, but at safe boundary
- `compact_cycle >= 2` (PreCompact fires for the third time) → force full reset instead

The counter lives in `.cascade/session/<session_id>.json`, separate from `cascade:run-state` because session state is per-session and `cascade:run-state` is per-product. Schema:

```json
{
  "session_id": "claude-cli-9f2a...",
  "started_at": "2026-05-18T14:00:00Z",
  "compact_cycles": 1,
  "last_compact_at": "2026-05-18T15:42:11Z",
  "last_safe_boundary": {
    "stage": "wrap",
    "ticket": "SOL-117",
    "manifest_path": ".cascade/manifests/SOL-117-wrap.json",
    "at": "2026-05-18T15:40:02Z"
  },
  "reset_due": false
}
```

`reset_due` is set to `true` by the PreCompact hook when `compact_cycles >= 2`. The SessionStart-source=compact hook reads it; if true, instead of restoring it triggers a clean exit via stdout signaling and writes a halt diagnostic naming `.cascade/halt/session-reset-required.txt`. The founder picks up with `claude --resume <session_id>` after that, which fires SessionStart-source=resume to fully rehydrate.

## Safe-boundary list

A "safe boundary" is any cascade state where compacting or resetting will not lose work-in-progress. Definitionally: a state where the most recent stage has sealed its manifest, all verifier predicates have passed, and no subagent is mid-run.

**Safe:**

- After `/wrap` completes (manifest sealed, locks released, Linear label transitioned)
- After `/review` seals the four-hat doc (AC-list checksum recorded; objections_resolved complete)
- After `/verify` completes (perceptual gate satisfied; milestone closed)
- After `/retro` writes its retro doc with sealed sha
- Between subagent invocations within a stage, provided the parent has captured the prior subagent's `agent_transcript_path` and written its manifest
- After `/onboard` completes (rare — only happens once per product)
- After `/plan`'s child tickets are all reachable and labeled

**Not safe:**

- Mid-Ralph-iteration (Ralph's `run.sh` runs as one unit; compacting between fix-plan items mangles in-memory state)
- Mid-tool-call (PostToolUse hasn't fired yet)
- During a four-hat in progress (some hats run; some don't; compacting loses the asymmetry)
- During a build that hasn't sealed (`/build` finalize hasn't written its manifest with `commit_sha` and `lock_releases`)
- During `/update-linear` writes (locks held on Linear docs)
- During any stage whose verifier predicates have not yet been recomputed by the next stage's pre-flight (the manifest exists but hasn't been verified — handoff is incomplete)

The safe-boundary list is a function the hook can compute: read `cascade:run-state.active_stages[]` and check whether any entry refers to a stage that is not in the "completed and verified" state. If zero unsafe stages, boundary is safe. If non-zero, boundary is unsafe.

## Compact mechanics

The compact flow has three actors: Claude Code's internal compaction, the PreCompact hook, and the SessionStart-source=compact hook.

**PreCompact** (fires before compaction):

1. Read `.cascade/session/<session_id>.json`. Increment `compact_cycles` in a temp copy.
2. If new `compact_cycles >= 2`: set `reset_due: true`, write the session file, return `{"decision": "block", "reason": "Session reset required — too many compact cycles. Halt at next safe boundary."}`. This blocks the compact; the cascade continues; the next safe-boundary check triggers the full reset.
3. Else (cycle 0 → 1, or 1 → 2): check safe-boundary function. If at a safe boundary, write session file with incremented counter, snapshot `cascade:run-state` summary to `.cascade/session/precompact-<session_id>-<timestamp>.json` (this is the side-channel that survives compaction), allow the compact by exiting 0 with no decision.
4. If NOT at a safe boundary: write deferral marker (`.cascade/session/compact-deferred.json`) and return `{"decision": "block", "reason": "Compact deferred — mid-task. Will retry at next safe boundary."}`.

The deferral path means a token-band-2 session can run a long Ralph iteration to completion before compacting. Trade: the session may exceed comfortable token budgets briefly. Bound: Ralph iterations are typically minutes, not hours. The trade-off is acceptable.

**SessionStart source=compact** (fires after compaction completes, session_id preserved):

1. Read `.cascade/session/<session_id>.json`. If `reset_due == true`: return additionalContext signaling "session reset required" and write a halt diagnostic. The founder is told via the next conversational turn to exit and resume.
2. Else: read the most recent `precompact-<session_id>-*.json` snapshot. Emit a concise additionalContext block via `hookSpecificOutput.additionalContext` — the cascade:run-state pointer, last completed stage, last sealed manifest, active stages (if any persisted). This is factual phrasing per the hooks-reference guidance ("The deployment target is production"), not imperative instructions.

**PostCompact** (v2.1.76+, optional): used as a redundant safety to log the compact event for retro. Not load-bearing; SessionStart-source=compact carries the recovery work.

**Max 2 cycles, why.** Compaction is lossy by design. After cycle 1, the working context is a summary of the original signal. After cycle 2, it's a summary of a summary, and the cascade has empirically drifted past the point where re-verifying against filesystem evidence is cheaper than continuing. The reset is cheaper than fighting a degraded context.

## Full session reset via Linear-mediated resume

When the threshold model triggers a reset (`reset_due == true` and a safe boundary is reached), the sequence is:

1. **Flush** `cascade:run-state` to filesystem; mirror to Linear (durable backup per D2.1 v2 decision 2). The Linear mirror handles the "what if the local file is lost between exit and resume" case — a working-machine crash, an accidental delete, a `rm -rf` mistake.
2. **Flush** `.cascade/session/<session_id>.json` with a `reset_completed_at` timestamp.
3. **Surface a halt card** to the founder: "Session reset at safe boundary after stage X. Resume with `claude --resume <session_id>`."
4. **Exit** the current Claude Code session via `SessionEnd` (the hook can write final telemetry but cannot block this exit usefully — async would not block the exit; sync just adds latency).
5. **Founder runs `claude --resume <session_id>`** (or its automated equivalent — see Zero-touch handoff).
6. **SessionStart source=resume** fires. The hook reads filesystem `cascade:run-state` first (canonical per D2.1 v2 decision 2). If the file is intact, hydrate directly. If missing or sha-mismatched, fall through to Linear-mirror read via Linear MCP. The Linear mirror is the durability backstop, not the primary path.
7. The hook emits hydrated context via `hookSpecificOutput.additionalContext`: cascade marker, current product, last completed stage and manifest path, active stages remaining (typically none, since reset only happens at safe boundary), next recommended action. Factual phrasing, no imperatives.
8. New session continues at the boundary the prior session left.

**Linear-mediated, not Linear-canonical.** The phrase "Linear-mediated resume" means Linear is the durability layer that makes resume robust across machine moves or local-file loss. It does not mean Linear writes precede filesystem writes (decision 2). The mediation is read-fallback: filesystem first, Linear as backup.

## Hook/script surface

D2.1 v2's open question 3 was: which predicates earn an `agent` hook, which stay `command`? Resolution per decision 6: `command` default; `agent` reserved for predicates requiring genuine LLM judgment. The cut list per predicate:

| Predicate (from D2.1 v2 stage table) | Hook event | Hook type | CLI fallback (max_turns gap) |
|---|---|---|---|
| `/onboard`: Linear projects + Status doc + config exist | `UserPromptSubmit` matcher `/onboard` (pre-flight) | command | `solo-verify onboard` |
| `/specify`: file + `ac_list_sha256` + test seeds | `UserPromptSubmit` matcher `/specify` (post-completion) | command | `solo-verify specify <ticket>` |
| Four-hat-user / four-hat-engineer transcript parse (priming + objections) | `SubagentStop` matcher agent type | command | `solo-verify subagent <agent_id>` |
| `/review`: chain check + unresolved count + AC-list seal | `UserPromptSubmit` matcher `/review` (post-completion) | command | `solo-verify review <ticket>` |
| `/review`: **did the four hats actually cover the user-journey edge cases?** | `SubagentStop` matcher `four-hat-*` | **agent** | manual founder review |
| `/plan`: child reachability + labels + count | `UserPromptSubmit` matcher `/plan` (post-completion) | command | `solo-verify plan <ticket>` |
| `/update-linear`: diff vs Linear state | `PreToolUse` matcher Linear write tool | command | `solo-verify update-linear <ticket>` |
| `/build` spawn: pid alive + branch + lockfile | `PostToolUse` matcher Bash (matching Ralph spawn) | command | `solo-verify build-spawn <ticket>` |
| `/build` finalize: commit + fix-plan-zero + tests passing | `Stop` (single orchestrator, see resolution #3) | command | `solo-verify build-finalize <ticket>` |
| `/wrap`: label + doc updates + fs/Linear mirror sha match | `PreToolUse` matcher Linear write tool | command | `solo-verify wrap <ticket>` |
| `/verify`: children built + perceptual evidence present | `UserPromptSubmit` matcher `/verify` (post-completion) | command | `solo-verify milestone <id>` |
| `/retro`: doc sealed + lessons line updated | `UserPromptSubmit` matcher `/retro` (post-completion) | command | `solo-verify retro <id>` |
| Linear-sync sanity check (every Linear read) | `PostToolUse` matcher Linear read tools | command | `solo-linear-read --sanity-check` |
| `cascade:run-state` hydration on session start | `SessionStart` source matchers | command | `solo-state restore --source <source>` |
| Compact threshold + safe-boundary check | `PreCompact` | command | n/a (only fires at compact time) |
| `cascade:run-state` post-compact context inject | `SessionStart` source=compact | command | manual reload |

**One agent hook in the whole cascade.** The four-hat objection-coverage predicate is the only one that genuinely needs LLM judgment — checking whether a list of objections covers the user-journey edge cases for a given spec is a reading task with no deterministic regex. Everything else parses, checks a hash, or queries an API.

**The Stop-hook orchestrator pattern.** Per resolution #3: one Stop hook, not several. The single hook orchestrates: Ralph's `fix_plan_unchecked_count == 0` check, the build manifest's verifier predicates, and any session-level discipline checks. One decision out. This is the cleanest way to avoid the multi-hook conflict surface and dodges anthropics/claude-code#10412 (the plugin Stop-hook bug) by installing in `.claude/hooks/` directly.

**Standalone CLI for the `max_turns` gap.** Per the hook-surface research: hooks do not fire when a session ends at `max_turns`. Every verification predicate above must also be invocable as a `solo-verify <stage> <ticket>` CLI, which the cascade calls explicitly at recovery time. This is non-negotiable for resilience.

**Async usage** (per resolution #4): the only async hook in the design is on `SessionEnd` for emitting telemetry — a fire-and-forget log of session duration, cycles, halt count. No verification predicate uses async; the latency cost of sync agent hooks is accepted for the one agent predicate (timeout 60s default; 120s for four-hat coverage).

## Zero-touch handoff sequence

Combining the threshold model, safe-boundary discipline, and reset mechanics into one end-to-end flow:

```
[normal operation, compact_cycle = 0]
        ↓
auto-compact triggers (Claude Code internal)
        ↓
PreCompact hook fires
        ↓
read .cascade/session/<id>.json → cycle would become 1
        ↓
check safe-boundary
        ↓
safe? ─yes→ snapshot precompact-*.json, ext 0, compact proceeds
        │        ↓
        │   SessionStart source=compact → restore via additionalContext
        │        ↓
        │   cascade resumes at same product, same boundary
        │
        no→ return decision:block "compact deferred", cascade continues
                ↓
              next safe boundary → cascade triggers explicit /compact (or auto retries)
                ↓
              PreCompact fires again → safe now → compact proceeds

[compact_cycle = 1, second auto-compact triggers]
        ↓
PreCompact hook fires
        ↓
cycle would become 2 → set reset_due:true, decision:block "session reset required"
        ↓
cascade reaches next safe boundary
        ↓
flush cascade:run-state to fs + Linear mirror
flush session file with reset_completed_at
surface halt card to founder
SessionEnd fires → async telemetry log
        ↓
founder runs claude --resume <session_id>
        ↓
SessionStart source=resume fires
        ↓
read fs cascade:run-state (canonical); fall back to Linear mirror if needed
        ↓
emit additionalContext: marker, product, last completed stage, active stages
        ↓
new session continues from the boundary

[zero founder touch except `claude --resume` invocation]
```

The "zero-touch" is approximate: the founder still types `claude --resume`. v0.3+ could automate this further (a wrapping shell loop that exits and re-launches on `reset_due`), but the v0.2 boundary is the manual resume invocation. The cascade should never silently start a new Claude Code session without the founder's awareness — that's a surveillance-vs-tool boundary worth keeping.

## What this doc does not cover

- **Programmatic token-count reading.** The hook surface as of May 2026 does not expose live token count in the payload. `/status` shows it interactively. The cycle-counter proxy is sufficient for v0.2; live token reads are a v0.3+ pull-forward if `/status` becomes scriptable or a hook payload field is added.
- **Multi-host session migration.** Resume across machines requires the Linear mirror to be the read source, plus filesystem reconstruction. v0.2 assumes single machine. Multi-host is v0.3+.
- **Cross-product session handoff.** A single session working two cascades in two products is not modeled. v0.2 assumes one product per session. The handoff mechanic could extend but the safe-boundary list complicates.
- **Real-time context streaming during reset.** When a reset happens mid-Ralph (which is unsafe and should never trigger), the in-flight Ralph state is lost. The reset only triggers at safe boundaries by design.
- **Hook installation packaging.** The on-disk layout of hook scripts, settings.json templates, and `solo-init` wiring — that's a packaging concern for D4.x and the published repo skeleton.
- **Backpressure on PreCompact deferrals.** If PreCompact returns `decision: block` repeatedly because the cascade never reaches a safe boundary, Claude Code's behavior is implementation-defined (likely it eventually compacts anyway when the context limit hits hard). v0.2 accepts this; v0.3+ could add a "force compact after N deferrals" escape valve.
- **Compact custom_instructions write-side.** The `custom_instructions` field on PreCompact's payload is the user's `/compact <text>` input — readable by the hook, not writable. State persistence across compact uses the side-channel snapshot file under `.cascade/session/`, not custom_instructions.

## Open questions for D2.3+ and D4.x

1. **Recovery from a missing precompact snapshot.** If PreCompact crashes after incrementing the cycle counter but before writing the snapshot, SessionStart-source=compact has nothing to restore from. Fallback: re-read `cascade:run-state` directly. Cost: slight context loss vs the curated summary. Acceptable for v0.2; tighten in D4.x.
2. **What additionalContext content actually helps Claude after compact.** The summary should be terse (per Anthropic's prompt-injection-defense guidance — factual not imperative) and short (per the 10,000-char additionalContext limit). The exact template is D2.3 or the publication-pass work, not this design doc.
3. **Linear-mirror write retry semantics.** Decision 2 says Linear is durable mirror, filesystem canonical. If the Linear mirror write fails during reset flush, the resume path can still recover from filesystem. Open: should the cascade surface the missed Linear sync as a taint, or silently retry via `--reconcile`? Defaults to taint per D2.1 v2's "log + observable" principle, but this is D4.5 territory.
4. **Session-end stamping for Linear ticket telemetry.** `SessionEnd` async hook is the natural place to record per-session cost, iteration count, and cycle count back to Linear as a comment on active tickets. Detail in D4.x.

## Composition citation

Three-band threshold pattern is original to this design — Claude Code's hooks reference does not prescribe a band model, only the PreCompact/SessionStart mechanism. The safe-boundary discipline is adapted from spec-kit's stage-gating principle (operations between stages, not within) applied to session boundaries. The cycle-counter proxy for token estimation is a workaround for the missing payload field; community precedent in the claudefa.st ContextRecoveryHook uses status-line monitoring for the same gap, which v0.2 chose not to depend on for portability. The single-Stop-hook orchestrator pattern is a defensive response to anthropics/claude-code#10412 — the bug forces convergence on one hook anyway. Subagent-stop / agent_transcript_path mechanics come straight from the Anthropic hooks reference (April 2026), as does PreCompact's `custom_instructions` payload field and SessionStart's source matchers. The Linear-mediated resume pattern is the natural extension of D2.1 v2 decision 2 (filesystem canonical, Linear durable mirror) into the cross-session case; no external precedent claimed.
