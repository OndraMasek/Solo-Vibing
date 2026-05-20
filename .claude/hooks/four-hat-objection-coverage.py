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
