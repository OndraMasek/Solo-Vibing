# D2.2 — Hook surface research findings

**Status:** Reference doc (research step for D2.2 design, captured now to save a re-derivation cycle next session).
**Phase:** 2.
**Date verified:** 2026-05-18. Sources: Anthropic hooks reference (code.claude.com/docs/en/hooks, April 2026), Anthropic Agent SDK TypeScript reference (platform.claude.com/docs/en/agent-sdk/typescript, April 2026), GitHub issue anthropics/claude-code#15485 (Dec 2025), community guides Feb–May 2026.
**Re-verify before drafting D2.2** — the ecosystem moves fast. Confirm each fact below holds as of D2.2's drafting date.

## Hook events (Claude Code, May 2026)

Lifecycle, in firing order:

| Event | Cadence | Matchers | Notes for trust-model use |
|---|---|---|---|
| `Setup` | CLI flags `--init`, `--init-only`, `--maintenance` | `init`, `maintenance` | v2.1.10+. Repo setup hook — useful for installing cascade scripts on `claude --init`. |
| `SessionStart` | Once per session | `startup`, `resume`, `clear`, `compact` | stdout adds to Claude's context. `source=resume` lets the hook re-load `cascade:run-state` after `/resume`. `source=compact` fires after `/compact` — entry point for context recovery. |
| `UserPromptSubmit` | Per turn | (none) | stdout adds to context. Exit 2 rejects the prompt. |
| `PreToolUse` | Per tool call | tool name regex | Exit 2 blocks the tool. v2.0.10+ can rewrite `tool_input` via `updatedInput` in `hookSpecificOutput`. |
| `PermissionRequest` | When permission prompt would fire | tool name | v2.0.45+. Can auto-approve via `permissionDecision: "allow"`. |
| `PostToolUse` | After tool succeeds | tool name regex | Includes `duration_ms` (v2.1.119+). Cannot undo the tool call but can feed Claude a follow-up via `decision: "block"`. |
| `PostToolUseFailure` | After tool fails | tool name regex | Same payload as PostToolUse plus failure context. |
| `SubagentStart` | Subagent spawns | agent type name | Payload: `agent_id`, `agent_type`. |
| `SubagentStop` | Subagent finishes | agent type name | Payload: `agent_id`, `agent_type`, **`agent_transcript_path`**, `last_assistant_message`, `stop_hook_active`. The `agent_transcript_path` is the F-1 verification surface. |
| `PreCompact` | Before context compaction | `manual`, `auto` | Payload: `trigger`, `custom_instructions: string \| null`. Use `custom_instructions` to persist `cascade:run-state` summary into the compacted output. |
| `Stop` | Claude finishes responding | (none) | Payload: `stop_hook_active`, `last_assistant_message?`. Return `{"decision": "block", "reason": "..."}` to force continuation. |
| `StopFailure` | Claude responds with failure | (none) | Same shape as Stop. |
| `Notification` | Claude notifies user | (none) | Async. Useful for desktop notifications on long Ralph runs. |
| `SessionEnd` | Session terminates | `exit`, `sigint`, `error` | Payload includes exit reason. Last chance to flush state. |
| `Elicitation`, `ElicitationResult` | MCP elicitation | (server-specific) | v2.1.76+. Out of scope for v0.2 trust model. |

## Hook handler types

| Type | Mechanism | Use case |
|---|---|---|
| `command` | Shell command, JSON via stdin, structured JSON or exit code via stdout/stderr | Deterministic verification: shell out to `solo-verify <stage> <ticket>` and propagate exit code. Default choice for D2.1's verifier predicates. |
| `prompt` | LLM single-turn evaluation of a templated prompt | Stop/SubagentStop completion checks where judgment is required. Default timeout 30s. |
| `agent` | Spawns a fresh subagent with Read/Grep/Glob | Deep verification: re-read subagent transcript, validate four-hat objection coverage. Default timeout 60s. Heavier and slower than `command` or `prompt`. |
| `http` | POST JSON to URL, parse JSON response | Out-of-scope for v0.2 (no external service). |
| `mcp_tool` | Invokes a configured MCP tool with hook payload as args | v2.1.118+. Useful if validation logic lives in an MCP server (e.g., Linear MCP for the eventual-consistency sanity check). |

## Stop / SubagentStop output schema quirk

Top-level fields only — **no `hookSpecificOutput` wrapper**. Per anthropics/claude-code#15485, verified on v2.0.76:

```json
{"decision": "block", "reason": "Postcondition predicate failed: spec_sha256 mismatch"}
```

All other event types use:

```json
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", ...}}
```

D2.2's hook scripts must emit the right shape per event. Schema-validate at write time.

## Critical caveats for trust-model enforcement

1. **Hooks may not fire on `max_turns`.** Session ends before hook execution. Implication: verifier predicates must also be invocable as standalone CLI (`solo-verify ...`) for use after resume. Hooks are the auto-fire path; CLI is the durable path.

2. **`--continue` and `--resume` replay mid-session hook outputs from transcript.** Mid-session hooks (PostToolUse, UserPromptSubmit) do not re-fire on resume; their saved stdout is replayed verbatim. Timestamps, commit SHAs, and other dynamic values become stale. Implication: do not put `cascade:run-state` snapshot logic in PostToolUse. `SessionStart` (which does re-fire on resume) is the correct place to refresh `cascade:run-state`.

3. **CLAUDE.md vs hooks for context loading.** Anthropic's hooks reference explicitly recommends CLAUDE.md for static project conventions ("The deployment target is production") and warns that imperative system instructions in stdout can trigger Claude's prompt-injection defenses. Cascade context should be **factual statements** in stdout, not commands. Phrasing matters.

4. **PostToolUse cannot undo the tool call.** It can feed back via `decision: "block"` but the side effect is already committed. Implication: filesystem-mirror write verification must be a `PreToolUse` predicate on the Linear write tool, not a `PostToolUse` cleanup.

5. **`agent_transcript_path` is a path to a JSONL file the parent can read.** Confirmed by SubagentStopHookInput in the Agent SDK TypeScript reference. The parent does not need to embed itself in the subagent's session — the transcript is durable on disk after the subagent terminates. This is the load-bearing capability for F-1.

## Environment variables available to hooks

- `$CLAUDE_PROJECT_DIR` — project root, present in all hook events.
- `$CLAUDE_PLUGIN_ROOT` — plugin directory (use for portable script paths).
- `$CLAUDE_ENV_FILE` — `SessionStart` only. Write `export FOO=bar` lines; persist into session env.
- `$CLAUDE_TOOL_INPUT_FILE_PATH` — file path argument for Write/Edit tool calls.
- `$CLAUDE_TOOL_INPUT`, `$CLAUDE_TOOL_RESULT`, `$USER_PROMPT` — accessible in `prompt`-type hooks.

## Settings file precedence

1. `~/.claude/settings.json` — user-level, applies to all projects.
2. `.claude/settings.json` — project-level, version-controlled, applies to whoever clones.
3. `.claude/settings.local.json` — project-level, gitignored, machine-local overrides.

Hooks merge across files. Multiple hooks on the same event run in parallel.

## Mapping to D2.1 verifier predicates

For each predicate in D2.1's per-stage table, the natural hook hosts:

| Predicate class | Primary hook | Backup CLI |
|---|---|---|
| Subagent transcript verification (four-hat-user, four-hat-engineer) | `SubagentStop` (command) | `solo-verify subagent <id>` |
| Filesystem-mirror sha matches Linear-mirror sha (/wrap) | `PreToolUse` (matcher: Linear write tool) | `solo-verify wrap <ticket>` |
| Spec checksum matches four-hat seal (/build pre-flight) | `UserPromptSubmit` (matcher: `/build`) → halts via exit 2 | `solo-verify build-preflight <ticket>` |
| Stop-hook completion gate (Ralph fix_plan unchecked == 0) | `Stop` (command) returning `{"decision": "block"}` | Ralph `run.sh` itself checks; redundant safety. |
| `cascade:run-state` lock acquisition | `SessionStart` (command, runs once) | `solo-verify lock-acquire <stage>` |
| Linear eventual-consistency sanity (every Linear read) | `PostToolUse` (matcher: Linear read tools) → logs only; halt via wrapper | `solo-linear-read --sanity-check` |
| `PreCompact` state persistence | `PreCompact` (command, writes `cascade:run-state` summary into `custom_instructions`) | Manual `solo-state snapshot` |
| `SessionStart` state recovery | `SessionStart` (command, source=compact OR resume, re-reads `cascade:run-state`) | Manual `solo-state restore` |

The above is provisional and gets locked in D2.2.

## What's missing / things to verify next session

- **Does `mcp_tool` hook type pass full hook payload to the MCP tool, or just a subset?** Affects whether Linear-sync sanity check can be done as a Linear MCP tool call.
- **Can `Setup` hook with `--init` create files outside `.claude/`?** Affects whether `solo-init` can scaffold `.cascade/manifests/` and `docs/.solo-run-state.json` on first run.
- **What's the exact behavior of multiple `Stop` hooks returning conflicting `decision` values?** Affects how trust-model and Ralph's existing completion check compose.
- **Async hooks (`async: true`) — do they block session end, or fire-and-forget?** Affects whether we can run heavy `agent`-type verification without slowing the cascade.

These are research items for the start of D2.2 drafting, not blockers.
