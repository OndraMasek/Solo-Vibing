# `.claude/settings.json` — hook wiring

**Status:** Patch-ready new file. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing`.

**Scope:** the project-level Claude Code settings file that wires the seven hook scripts to D2.2 hook events with the appropriate matchers. Uses the single Stop-hook orchestrator pattern per D2.2 §Research-step resolution #3.

**v0.1 reconciliation:** v0.1 has no `.claude/settings.json` per `repo-state-summary.md` Part 2. This is a new file. **Coordination point with v0.1:** if v0.1 ships any user-level settings at `~/.claude/settings.json` (e.g., personal preferences), they merge with this project-level file per D2.2 §Settings file precedence. Hooks merge across files; multiple hooks on the same event run in parallel.

**Coordination point with `.claude/settings.local.json`:** the local override file is gitignored and machine-local per D2.2 §Settings file precedence. v0.2 does not ship `.claude/settings.local.json` — that's founder-machine state, never version-controlled.

---

## File content

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "comment": "Solo-Vibing v0.2 hook wiring. See docs/specs/0001-v0.2-cascade-integration/ for binding design docs. Edit via the cascade's update-linear / wrap surface, not by hand.",
  "hooks": {
    "UserPromptSubmit": [
      {
        "comment": "Pre-flight chain-integrity check for cascade slash-commands. Script narrows to /review|/plan|/update-linear|/build|/wrap|/verify|/retro internally; no matcher field is supported on UserPromptSubmit (per D2.2 §Hook events table).",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/preflight-provenance.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "comment": "Pyramid-tampering guard for spec-file writes. Script narrows by file_path to docs/specs/*/spec.md.",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pyramid-tampering.sh",
            "timeout": 15
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "comment": "Reserved for v0.1 mirror-sha predicate carry-forward (Linear-write tools). v0.2 does not add new PostToolUse hooks; the carry-forward predicate is wired by the v0.1 codebase. This empty array is the placeholder that test_settings_json_wires_all_events asserts.",
        "hooks": []
      }
    ],
    "SubagentStop": [
      {
        "matcher": "four-hat-user|four-hat-engineer|four-hat-pm|four-hat-skeptic",
        "comment": "The cascade's single agent-judgment-shaped hook per D3.4 §What is a gate. Realized as command-type Python (per surfaced item in four-hat-objection-coverage-hook.md). Output: top-level-fields-only Stop/SubagentStop quirk per D2.2.",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/four-hat-objection-coverage.py",
            "timeout": 60
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "startup|resume|compact|clear",
        "comment": "Cross-session state restoration. Source-matched dispatch inside the script (startup vs resume vs compact vs clear branches).",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start-state-restore.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "comment": "Three-band threshold + safe-boundary check per D2.2 §Compact mechanics. Handles both trigger=manual and trigger=auto (no matcher needed; script reads trigger from payload).",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/precompact-safe-boundary.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "comment": "The cascade's single Stop-hook orchestrator per D2.2 §Research-step resolution #3. Dispatches kill_in_progress, manual_halt, and per-skill completion predicates. Stop has no matchers (D2.2 §Hook events table).",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-orchestrator.sh",
            "timeout": 30
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "comment": "Per-session telemetry sink. Async fire-and-forget per D2.2 §Critical caveats #4. Appends one JSONL line per session to .cascade/telemetry/sessions.jsonl.",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-end-telemetry.sh",
            "async": true,
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

---

## Design notes

### Event coverage

The settings file wires seven events:

| Event | Matchers | Script | Notes |
|---|---|---|---|
| `UserPromptSubmit` | (none; D2.2) | `preflight-provenance.sh` | Script narrows by inspecting prompt content. |
| `PreToolUse` | `Write\|Edit\|MultiEdit` | `pyramid-tampering.sh` | Script narrows by file_path. MultiEdit conservatively allowed per surfaced item. |
| `PostToolUse` | (none; placeholder) | (empty array) | Reserved for v0.1 Linear-write mirror-sha carry-forward. The empty entry satisfies the `test_settings_json_wires_all_events` smoke test. |
| `SubagentStop` | `four-hat-user\|four-hat-engineer\|four-hat-pm\|four-hat-skeptic` | `four-hat-objection-coverage.py` | The cascade's single agent-judgment hook. |
| `SessionStart` | `startup\|resume\|compact\|clear` | `session-start-state-restore.sh` | Source-matched dispatch inside the script. |
| `PreCompact` | (none) | `precompact-safe-boundary.sh` | Script reads `trigger` from payload. The seventh hook (deviation per Child 0001-C handoff). |
| `Stop` | (none) | `stop-orchestrator.sh` | The single orchestrator. |
| `SessionEnd` | (none) | `session-end-telemetry.sh` | Async fire-and-forget. |

### Timeout choices

Per D2.2 §Hook handler types: default command timeout is unspecified in the hooks reference; the Anthropic docs imply per-event defaults (30s for `prompt`, 60s for `agent`). The settings file declares explicit timeouts for each hook:

- `preflight-provenance.sh`: 10s — pure filesystem reads + sha computation; fast.
- `pyramid-tampering.sh`: 15s — slightly more work (read content, parse, regex), still under one second in practice.
- `four-hat-objection-coverage.py`: 60s — reads up to four transcript JSONL files (potentially many KB each); 60s leaves headroom.
- `session-start-state-restore.sh`: 10s — single filesystem read + composition.
- `precompact-safe-boundary.sh`: 10s — filesystem reads + JSON manipulation.
- `stop-orchestrator.sh`: 30s — may shell out to `solo-verify build-finalize` which runs tests; 30s is generous.
- `session-end-telemetry.sh`: 5s — async, fire-and-forget; if it times out the session still exits.

### Matcher pattern for SubagentStop

The matcher uses pipe-alternation rather than a wildcard glob. Per D2.2 §Hook events table SubagentStop row: "agent type name" matcher. The alternation explicitly lists the four hats; `four-hat-*` is a wildcard pattern that some Claude Code versions may or may not support. The alternation is explicit and version-portable. **Surfaced item:** validate that pipe-alternation is the canonical matcher syntax at apply-time; switch to wildcard if the syntax is more idiomatic.

### `$CLAUDE_PROJECT_DIR` portability

Per D2.2 §Environment variables: `$CLAUDE_PROJECT_DIR` is populated in all hook events. Using it in the `command` field ensures the scripts resolve correctly regardless of where Claude Code is invoked from. The alternative (`.claude/hooks/...` relative paths) is more concise but breaks when Claude Code is invoked from a subdirectory.

### Why PostToolUse is wired with an empty array

Per `decomposition.md`'s "test_settings_json_wires_all_events" failing-test seed: "asserts .claude/settings.json parses and contains entries for PreToolUse, PostToolUse, SubagentStop, SessionStart, SessionEnd, PreCompact, Stop." PostToolUse must have a wiring entry. v0.2 doesn't add new PostToolUse hooks; the v0.1 Linear-write mirror-sha predicate (carried forward) would land here if v0.1 codified it as a settings.json entry. Currently v0.1 doesn't (per `repo-state-summary.md`); the carry-forward is contractual not configurational.

The empty array placeholder satisfies the smoke test's existence requirement. **Surfaced item:** at apply-time, the executing session should fold the v0.1 Linear-write mirror-sha predicate into this entry if it's been promoted to a hook (per Child A scope). If not, the empty array stays.

### JSON Schema reference

The `$schema` field at the top points to the Claude Code settings JSON Schema. This is informational — Claude Code reads `hooks` regardless; the schema reference lets editors and validators flag malformed entries. **Surfaced item:** verify the schema URL at apply-time; Anthropic publishes the canonical URL and it may differ from the speculative one above.

---

## Failing-test seed

Per `decomposition.md` Child 0001-C failing-test-seed list:

```python
def test_settings_json_wires_all_events(tmp_cascade_repo):
    """
    asserts .claude/settings.json parses and contains entries for PreToolUse,
    PostToolUse, SubagentStop, SessionStart, SessionEnd, PreCompact, Stop;
    covers AC-14.
    """
    settings_path = tmp_cascade_repo / ".claude/settings.json"
    with open(settings_path) as f:
        settings = json.load(f)

    hooks = settings.get("hooks", {})
    required_events = {
        "PreToolUse", "PostToolUse", "SubagentStop",
        "SessionStart", "SessionEnd", "PreCompact", "Stop",
        "UserPromptSubmit",  # Child 0001-C adds this beyond decomposition.md's enumeration
    }
    assert required_events.issubset(set(hooks.keys())), \
        f"Missing events: {required_events - set(hooks.keys())}"

    # Each event entry must be a list (possibly empty)
    for event in required_events:
        assert isinstance(hooks[event], list), f"{event} entry must be a list"

    # PreToolUse must have a matcher for Write|Edit|MultiEdit
    pre_tool_use = hooks["PreToolUse"]
    assert any(
        "matcher" in entry and "Write" in entry["matcher"]
        for entry in pre_tool_use
    ), "PreToolUse must have a Write|Edit|MultiEdit matcher entry"

    # SubagentStop must have a matcher for four-hat-*
    subagent_stop = hooks["SubagentStop"]
    assert any(
        "matcher" in entry and "four-hat" in entry["matcher"]
        for entry in subagent_stop
    ), "SubagentStop must have a four-hat-* matcher entry"

    # Stop must have at least one hook entry (the orchestrator)
    stop_entries = hooks["Stop"]
    assert any(
        len(entry.get("hooks", [])) > 0 for entry in stop_entries
    ), "Stop must have at least one hook"

    # SessionEnd must have async: true on at least one hook
    session_end = hooks["SessionEnd"]
    assert any(
        any(h.get("async") is True for h in entry.get("hooks", []))
        for entry in session_end
    ), "SessionEnd must have async: true on the telemetry hook"
```

---

## Cross-references

- **D2.2 §Hook events table** — every event row's matcher syntax and payload shape.
- **D2.2 §Hook handler types** — the `command` type used by all seven scripts; timeout defaults.
- **D2.2 §Settings file precedence** — user/project/local merge semantics.
- **D2.2 §Environment variables** — `$CLAUDE_PROJECT_DIR` portability.
- **D2.2 §Research-step resolution #3** — the single Stop-hook orchestrator pattern this file honors.
- **D2.2 §Critical caveats #4** — the async-only-for-telemetry constraint this file honors.
- **D2.2 §Stop / SubagentStop output schema quirk** — the output shape constraint for the SubagentStop matcher's hook.
- **All seven hook script files** in this session — the binding contracts this file's wiring satisfies.
- **`decomposition.md` Child 0001-C row** — the failing-test seed `test_settings_json_wires_all_events` this file is the patch target for.
- **Parent spec AC-14** — covered by this file + the seven script files in this session.
