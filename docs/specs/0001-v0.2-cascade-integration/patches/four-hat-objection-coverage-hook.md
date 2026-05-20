# `.claude/hooks/four-hat-objection-coverage.py` — the cascade's single agent-type hook

**Status:** Patch-ready new file. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing`.

**Scope:** the cascade's single agent-type hook per D3.4 §What is a gate and D2.2 §Hook/script surface. Fires on `SubagentStop` events matched on agent type names starting with `four-hat-` (per Child 0001-B continuation 1's `/review` Gate 2 amendment). Validates each four-hat subagent's transcript per the predicate sequence in `review-SKILL-amendments.md` Gate 2.

Per D2.1 v2 §Subagent verification (the F-1 fix): the parent (`/review`) writes each subagent's manifest from an **independently re-read transcript**; the gate's predicate is the parent's recompute, NOT the subagent's self-report. This hook IS the parent's recompute — it reads `agent_transcript_path` from the SubagentStop payload, parses the JSONL, and validates the predicates that the `/review` skill's Gate 2 amendment specifies.

**Output shape: top-level-fields-only.** Per D2.2 §Stop / SubagentStop output schema quirk: SubagentStop emits `{"decision": "block", "reason": "..."}` at the TOP LEVEL — NOT wrapped in `hookSpecificOutput` as other hook events do. Verified on Claude Code v2.0.76 per anthropics/claude-code#15485.

**v0.1 reconciliation:** none. v0.1 has no `.claude/hooks/` per `repo-state-summary.md` Part 2.

---

## Predicate sequence (per `/review` Gate 2 amendment)

For each `four-hat-<hat>` subagent (hats: user, engineer, pm, skeptic):

1. **Priming text present** — the first user-message-content in the transcript matches the expected priming for this hat. (The priming text is hat-specific per v0.1's four-hat subagent prompts; the hook compares against a hat→priming map.)
2. **Structured objections section present** — the final assistant-message-content contains a `## Objections` (or `# Objections`) heading.
3. **Concluding seal line present** — the final assistant-message-content contains a `## Seal` heading (or a line beginning with `Seal:`).
4. **Structured objection entries parseable** — every bullet under `## Objections` parses as `- **<hat>** [<severity>] @ <locus>: <finding>` per the four-hat template.

If any predicate fails for any hat, the hook emits a block decision with the failing-hat's transcript path and a sub-case diagnostic naming which predicate failed.

The full `unresolved_count == 0` aggregation predicate (Predicate 6 in `/review` Gate 2) is **NOT** this hook's job — it fires AFTER all four hats stop, and the `/review` skill's at-write seal evaluates it from the four written manifests. This hook fires per-subagent-stop; aggregation is the skill's responsibility.

---

## Script content

```python
#!/usr/bin/env python3
"""
.claude/hooks/four-hat-objection-coverage.py

Cascade's single agent-type hook per D3.4 §What is a gate. Fires on
SubagentStop events matched on agent_type starting with "four-hat-".

Validates each four-hat subagent's transcript per the predicate sequence
in `/review` Gate 2 amendment (Child 0001-B continuation 1):
  P1: priming text present
  P2: ## Objections section present in final assistant message
  P3: ## Seal (or "Seal:") concluding line present
  P4: every objection bullet parseable per the four-hat template

Output shape: top-level-fields-only Stop/SubagentStop quirk per D2.2
§Stop / SubagentStop output schema quirk. NO hookSpecificOutput wrapper.

Halt codes (per D3.4 §`/review` row):
  §four-hat-incomplete/priming-text-missing
  §four-hat-incomplete/objections-section-missing
  §four-hat-incomplete/seal-line-missing
  §four-hat-incomplete/objection-entry-malformed

Exit codes: always 0; halt semantics live in the JSON decision field.
"""

import json
import re
import sys
from pathlib import Path

# Source the shared lib
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import _lib  # noqa: E402


# ---- Hat → priming-text expectations -------------------------------------
#
# Per v0.1's .claude/agents/four-hat-*.md frontmatter, each hat has a priming
# preamble the parent injects when dispatching. The hook validates that the
# first user-message-content in the transcript includes the hat's priming
# marker (a substring unique to that hat).
#
# The PRIMING_MARKERS dict below is the *minimal* substring each hat's
# transcript must contain in its first user message. v0.1 ships longer priming
# prompts; this hook validates the *signature* substring, not the full prompt.
#
# If v0.1's agent frontmatters are amended, update this dict in lockstep.
# **Surfaced item:** validate against v0.1 four-hat agent files at apply time.

PRIMING_MARKERS = {
    "user": "Read this spec from the user's perspective",
    "engineer": "Read this spec from the implementing engineer's perspective",
    "pm": "Read this spec from the product manager's perspective",
    "skeptic": "Read this spec from a skeptical adversarial perspective",
}

# ---- Objection-entry regex ----------------------------------------------
#
# Per the four-hat template shape: every objection bullet matches
#   - **<hat>** [<severity>] @ <locus>: <finding>
# The hat field validates against the dispatching subagent's name.

OBJECTION_PATTERN = re.compile(
    r"""
    ^\s*-\s+                              # bullet prefix
    \*\*(?P<hat>user|engineer|pm|skeptic)\*\*  # hat token in bold
    \s+\[(?P<severity>[^\]]+)\]           # severity in brackets
    \s+@\s+(?P<locus>[^:]+)               # locus after @
    :\s+(?P<finding>.+)$                  # finding after colon
    """,
    re.VERBOSE,
)


def main() -> None:
    payload = _lib.read_hook_payload()
    _lib.trace("four-hat-objection-coverage: fired")

    # Read SubagentStop payload fields per D2.2 §Hook events table.
    # SubagentStop carries: agent_id, agent_type, agent_transcript_path,
    # last_assistant_message, stop_hook_active.
    agent_type = payload.get("agent_type", "")
    agent_id = payload.get("agent_id", "")
    transcript_path_str = payload.get("agent_transcript_path", "")

    if not agent_type.startswith("four-hat-"):
        # Settings.json matcher should have filtered this, but defensive.
        _lib.trace(f"four-hat-objection-coverage: not a four-hat agent (type={agent_type}); exiting clean")
        sys.exit(0)

    hat = agent_type.removeprefix("four-hat-")
    if hat not in PRIMING_MARKERS:
        # Unknown hat — surface as halt rather than silently passing.
        diagnostic = (
            f"§four-hat-incomplete/unknown-hat: agent_type={agent_type!r} produced hat={hat!r}; "
            f"expected one of {sorted(PRIMING_MARKERS)}. "
            "Either the agent type was renamed without updating this hook's PRIMING_MARKERS dict, "
            "or the SubagentStop payload was malformed."
        )
        _lib.log_halt("§four-hat-incomplete/unknown-hat", diagnostic)
        _lib.emit_stop_block(diagnostic)
        sys.exit(0)

    transcript_path = Path(transcript_path_str)
    if not transcript_path.is_file():
        diagnostic = (
            f"§four-hat-incomplete/transcript-absent: agent_id={agent_id} (hat={hat}); "
            f"agent_transcript_path={transcript_path_str!r} does not resolve to a file. "
            "The subagent terminated without producing a readable transcript; the parent /review "
            "cannot recompute objections from the agent's self-report."
        )
        _lib.log_halt("§four-hat-incomplete/transcript-absent", diagnostic)
        _lib.emit_stop_block(diagnostic)
        sys.exit(0)

    # Parse the transcript JSONL
    transcript_entries = _read_transcript(transcript_path)
    if transcript_entries is None:
        diagnostic = (
            f"§four-hat-incomplete/transcript-malformed: agent_id={agent_id} (hat={hat}); "
            f"transcript at {transcript_path} is not valid JSONL or contains no readable entries."
        )
        _lib.log_halt("§four-hat-incomplete/transcript-malformed", diagnostic)
        _lib.emit_stop_block(diagnostic)
        sys.exit(0)

    # ---- Predicate 1: priming text present in first user message ----------
    first_user_msg = _first_user_message_content(transcript_entries)
    expected_marker = PRIMING_MARKERS[hat]
    if first_user_msg is None or expected_marker not in first_user_msg:
        diagnostic = (
            f"§four-hat-incomplete/priming-text-missing: hat={hat}; "
            f"transcript={transcript_path}; "
            f"expected priming marker {expected_marker!r} absent from the first user message. "
            "The subagent was dispatched with an incomplete or malformed priming prompt; "
            "the /review skill should re-dispatch this hat with the correct priming."
        )
        _lib.log_halt("§four-hat-incomplete/priming-text-missing", diagnostic)
        _lib.emit_stop_block(diagnostic)
        sys.exit(0)

    # ---- Predicate 2: ## Objections section in final assistant message ----
    last_assistant_msg = _last_assistant_message_content(transcript_entries)
    if last_assistant_msg is None:
        diagnostic = (
            f"§four-hat-incomplete/no-final-assistant-message: hat={hat}; "
            f"transcript={transcript_path}; "
            "the transcript contains no assistant-role messages, so no objections to verify."
        )
        _lib.log_halt("§four-hat-incomplete/no-final-assistant-message", diagnostic)
        _lib.emit_stop_block(diagnostic)
        sys.exit(0)

    objections_section = _extract_section(last_assistant_msg, "Objections")
    if objections_section is None:
        diagnostic = (
            f"§four-hat-incomplete/objections-section-missing: hat={hat}; "
            f"transcript={transcript_path}; "
            "'## Objections' (or '# Objections') section absent in the final assistant message. "
            "The four-hat template requires every hat to surface a structured objections section "
            "even if the objection list is empty (use '- (no objections)' as the single bullet)."
        )
        _lib.log_halt("§four-hat-incomplete/objections-section-missing", diagnostic)
        _lib.emit_stop_block(diagnostic)
        sys.exit(0)

    # ---- Predicate 3: ## Seal heading or "Seal:" line ---------------------
    seal_section = _extract_section(last_assistant_msg, "Seal")
    seal_line_match = re.search(r"^\s*Seal:\s*.+$", last_assistant_msg, re.MULTILINE)
    if seal_section is None and seal_line_match is None:
        diagnostic = (
            f"§four-hat-incomplete/seal-line-missing: hat={hat}; "
            f"transcript={transcript_path}; "
            "concluding seal absent — expected either a '## Seal' heading or a line beginning 'Seal:'. "
            "The four-hat template requires every hat to seal its review explicitly so the parent "
            "/review can distinguish 'hat ran to completion' from 'hat ran out of context'."
        )
        _lib.log_halt("§four-hat-incomplete/seal-line-missing", diagnostic)
        _lib.emit_stop_block(diagnostic)
        sys.exit(0)

    # ---- Predicate 4: objection entries parseable -------------------------
    malformed_entries = []
    for line_num, line in enumerate(objections_section.splitlines(), start=1):
        # Skip blank lines, section sub-headings, the "no objections" sentinel
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if "no objections" in stripped.lower() and stripped.startswith("-"):
            continue
        # If the line is a bullet, it must parse
        if stripped.startswith("-"):
            match = OBJECTION_PATTERN.match(line)
            if match is None:
                malformed_entries.append((line_num, line.rstrip()))
                continue
            # Cross-check: the bullet's <hat> field must match this subagent's hat
            if match.group("hat") != hat:
                malformed_entries.append(
                    (line_num, f"{line.rstrip()}  [hat field {match.group('hat')!r} does not match subagent hat {hat!r}]")
                )

    if malformed_entries:
        diagnostic_lines = [
            f"§four-hat-incomplete/objection-entry-malformed: hat={hat}; "
            f"transcript={transcript_path}; "
            f"{len(malformed_entries)} malformed objection entries:",
        ]
        for line_num, line in malformed_entries[:10]:  # cap diagnostic at 10
            diagnostic_lines.append(f"  line {line_num}: {line}")
        if len(malformed_entries) > 10:
            diagnostic_lines.append(f"  ...({len(malformed_entries) - 10} more)")
        diagnostic_lines.append(
            "Expected entry shape: '- **<hat>** [<severity>] @ <locus>: <finding>' "
            "where <hat> matches the subagent's hat name."
        )
        diagnostic = "\n".join(diagnostic_lines)
        _lib.log_halt("§four-hat-incomplete/objection-entry-malformed", diagnostic)
        _lib.emit_stop_block(diagnostic)
        sys.exit(0)

    # All four predicates pass for this hat. The aggregate unresolved_count
    # check fires later in /review's at-write seal, NOT in this per-subagent
    # hook. Exit clean with no decision.
    _lib.trace(f"four-hat-objection-coverage: hat={hat} passed all predicates")
    sys.exit(0)


# ---- Transcript parsing helpers ----------------------------------------


def _read_transcript(path: Path) -> list[dict] | None:
    """Read a JSONL transcript file. Returns list of entries or None on error."""
    entries = []
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    # Single malformed line is tolerable if other lines parse;
                    # complete unparseability returns None
                    continue
    except OSError:
        return None
    if not entries:
        return None
    return entries


def _first_user_message_content(entries: list[dict]) -> str | None:
    """Return the content of the first user-role message in the transcript."""
    for entry in entries:
        # Transcript entries may vary by Claude Code version. Try common shapes:
        #   {"role": "user", "content": "..."}
        #   {"type": "user-message", "content": "..."}
        #   {"message": {"role": "user", "content": "..."}}
        role = entry.get("role") or entry.get("message", {}).get("role")
        if role == "user":
            content = entry.get("content") or entry.get("message", {}).get("content")
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                # Content blocks shape — concatenate text blocks
                parts = [
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                return "\n".join(p for p in parts if p) or None
    return None


def _last_assistant_message_content(entries: list[dict]) -> str | None:
    """Return the content of the last assistant-role message."""
    last = None
    for entry in entries:
        role = entry.get("role") or entry.get("message", {}).get("role")
        if role == "assistant":
            content = entry.get("content") or entry.get("message", {}).get("content")
            if isinstance(content, str):
                last = content
            elif isinstance(content, list):
                parts = [
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                joined = "\n".join(p for p in parts if p)
                if joined:
                    last = joined
    return last


def _extract_section(text: str, heading: str) -> str | None:
    """
    Extract the body of a '## <heading>' (or '# <heading>') section from
    markdown text. Returns the section body up to the next heading at the
    same or higher level, or None if the heading is absent.
    """
    pattern = re.compile(
        rf"^\#{{1,3}}\s+{re.escape(heading)}\s*$"
        r"(.*?)"
        r"(?=^\#{1,3}\s+|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(text)
    if match is None:
        return None
    return match.group(1).strip()


if __name__ == "__main__":
    main()
```

---

## Design notes

### Why this hook is `agent`-type per D2.2 vs `command`-type

D2.2's `agent` hook type "spawns a fresh subagent with Read/Grep/Glob" — heavier and slower than `command`, default timeout 60s. The "objection coverage" predicate genuinely requires reading and parsing the transcript (a JSONL file, multiple kilobytes per hat), validating the four-hat template shape, and cross-referencing hat names. This is structured-data work — Python is the right tool per `decomposition.md`'s "Python for any structured-data manipulation."

**But this script runs as `command`-type, not `agent`-type.** The `agent` hook type spawns a fresh Claude subagent that reads files with Read/Grep/Glob; this script reads the transcript file directly via stdlib and parses it without a Claude turn. The `command` shape with a Python interpreter is much faster (milliseconds vs seconds) and more deterministic than spawning a Claude subagent for what is fundamentally a regex-and-shape-check task.

This is the cleaner interpretation of D3.4 §What is a gate's "the only agent-type hook in the cascade — the four-hat objection-coverage check on SubagentStop": the hook embodies the *agent-level judgment* (which the original hook-type taxonomy reserves for LLM judgment) but does so via deterministic Python rather than spawning a Claude subagent. The judgment lives in the Python regex; the parse + comparison are deterministic.

**Surfaced item:** D3.4 §What is a gate's claim that this is "the only agent-type hook" is technically inaccurate post-this-session — the predicate's *intent* matches the agent-type framing (LLM-judgment-shaped) but its *realization* is command-type Python. v0.2 ships this as `command`-type for performance + determinism reasons; D3.4 §What is a gate should be amended at apply-time to either (a) drop the "agent-type" claim, (b) reframe as "the cascade's single LLM-judgment-shaped predicate, realized as deterministic Python," or (c) accept the framing-vs-implementation gap explicitly.

### Why PRIMING_MARKERS is a hardcoded dict

The four-hat priming prompts live in `v0.1/.claude/agents/four-hat-*.md` frontmatter. The hook needs a substring marker to validate Predicate 1 against. Options:

- **(a) Hardcode the markers** — what this script does. Fast; simple; tightly coupled to v0.1's agent prompts (any frontmatter change breaks the hook).
- **(b) Read agent frontmatter at runtime** — would require parsing the v0.1 agent files on every SubagentStop. Slower; introduces a new failure mode if the agent file path changes.
- **(c) Validate structurally only (no priming-text check)** — relaxes Predicate 1 entirely. Loses signal: a hat dispatched without priming still produces an objections section if the model improvises.

The hardcoded dict is the cleanest v0.2 choice. **Surfaced item:** validate the markers against v0.1's four-hat agent frontmatter at apply-time; if any marker doesn't match, the executing session updates the dict.

### Why exit 0 unconditionally

Same reasoning as `stop-orchestrator.sh`: halt semantics live in the JSON's `decision: block` field per D2.2 §Stop / SubagentStop output schema quirk. Exit 0 means "the hook ran"; the JSON tells Claude Code whether to continue or block.

### Why the script does NOT write the subagent manifest

The `/review` Gate 2 amendment specifies that after the four predicate checks pass, the parent writes `.cascade/manifests/<ticket>-<hat>.json` with the parsed objections. That manifest write is the SKILL's responsibility, not this hook's. The hook only validates; the skill (running in the parent's context after SubagentStop) reads the same transcript and writes the manifest.

**Why this split:** SubagentStop hooks are best-effort enforcement; the skill is the durable writer. If the hook misses (e.g., timeout) the skill still writes; if the hook fires but the skill doesn't reach the manifest-write step (e.g., the chat ends), there's no orphan manifest.

### Transcript shape tolerance

The transcript-parsing helpers (`_first_user_message_content`, `_last_assistant_message_content`) try multiple shapes to accommodate Claude Code version drift in the JSONL format. v2.0.76 (the verified version per anthropics/claude-code#15485) uses `{"role": ..., "content": ...}`; some versions wrap inside `{"message": {...}}`; some use content-block arrays. The helpers try each shape; if all fail, the helpers return None and the hook surfaces `§four-hat-incomplete/no-final-assistant-message` (predicate-shaped diagnostic, not a parser-error).

---

## Failing-test seed

Per `decomposition.md` Child 0001-C failing-test-seed list:

```python
def test_four_hat_objection_coverage_emits_correct_shape(tmp_cascade_repo, mock_transcript):
    """
    asserts the script emits top-level {"decision":"block","reason":"..."} without
    hookSpecificOutput wrapper on objection-uncovered; covers AC-14.
    """
    transcript_path = mock_transcript(
        hat="user",
        priming_present=True,
        objections_section_present=False,  # forces Predicate 2 failure
        seal_present=True,
    )
    result = run_hook(
        "four-hat-objection-coverage.py",
        payload={
            "agent_type": "four-hat-user",
            "agent_id": "agent-001",
            "agent_transcript_path": str(transcript_path),
        },
        project_dir=tmp_cascade_repo,
    )
    # Output must be top-level, not wrapped in hookSpecificOutput
    output = json.loads(result.stdout)
    assert "hookSpecificOutput" not in output  # the quirk
    assert output["decision"] == "block"
    assert "§four-hat-incomplete/objections-section-missing" in output["reason"]
    assert "hat=user" in output["reason"]
    assert result.exit_code == 0
```

---

## Cross-references

- **D2.1 v2 §Subagent verification (F-1 fix)** — the parent-writes-from-re-read-transcript pattern this hook is the parent's recompute mechanism for.
- **D2.2 §Hook events table** — `SubagentStop` event semantics and payload shape (`agent_id`, `agent_type`, `agent_transcript_path`, `last_assistant_message`, `stop_hook_active`).
- **D2.2 §Hook handler types** — `agent` vs `command` taxonomy; this script realizes an agent-judgment-shaped predicate as command-type Python (surfaced item).
- **D2.2 §Stop / SubagentStop output schema quirk** — top-level-fields-only output shape this script emits.
- **D2.2 §Critical caveats #5** — the `agent_transcript_path` JSONL semantics.
- **D3.4 §`/review` row** — the gate's predicate set this script evaluates.
- **D3.4 §What is a gate** — the "single agent-type hook" claim that needs apply-time amending per surfaced item above.
- **`review-SKILL-amendments.md`** (Child 0001-B continuation 1) Gate 2 — the predicate-by-predicate spec this script implements.
- **`.claude/hooks/_lib.py`** — imported for IO and emitter helpers.
- **v0.1 `.claude/agents/four-hat-*.md`** — the hat-priming text this script validates against (PRIMING_MARKERS dict).
- **Parent spec AC-14** — covered by this script + the other six in this session.
