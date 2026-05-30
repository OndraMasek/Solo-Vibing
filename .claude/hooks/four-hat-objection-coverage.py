#!/usr/bin/env python3
"""
.claude/hooks/four-hat-objection-coverage.py

Cascade's single agent-type hook per D3.4 §What is a gate. Fires on
SubagentStop events matched on agent_type starting with "four-hat-".

Validates each four-hat subagent's transcript per the predicate sequence:
  P1: priming text present ("You are the <hat> hat" — the real preamble
      the agents emit per .claude/agents/four-hat-*.md)
  P2: ## Findings section present in final assistant message
  P3: every Findings bullet parseable per the four-hat template

Output shape: top-level-fields-only Stop/SubagentStop quirk per D2.2
§Stop / SubagentStop output schema quirk. NO hookSpecificOutput wrapper.

SOL-132 fix — advisory, never-hangs contract:
  This is a SubagentStop hook. For SubagentStop, a {"decision":"block"} output
  means "do NOT stop; feed the reason back and continue", which loops the
  subagent. The prior version hard-`block`ed on every predicate miss AND
  validated a transcript shape the agents never emit (it expected
  "Read this spec from …" priming and `## Objections`/`## Seal` sections, but
  the real agents say "You are the <hat> hat" and emit `## Findings`), so P1
  failed for every hat and the subagent never terminated (runs hung 2h+/7h).
  Two changes break the loop universally:
    1. A `stop_hook_active` guard at the top of main(): if the runtime is
       already re-invoking us because of a prior block, exit 0 immediately.
    2. On any non-matching / incomplete state we exit CLEAN (advisory, exit 0)
       and record the diagnostic via log_halt for triage — we never emit a
       `block` decision, so a format miss can never hang a session. The hook
       cannot tell from the SubagentStop payload whether it fired in /specify
       or /review (no stage field exists), so it stays advisory in all stages.

Diagnostic codes (recorded via log_halt for triage; NOT block decisions):
  §four-hat-incomplete/priming-text-missing
  §four-hat-incomplete/findings-section-missing
  §four-hat-incomplete/finding-entry-malformed

Exit codes: always 0. This hook is advisory only; it never blocks termination.
"""

from __future__ import annotations

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
# SOL-132 reconciliation: the real agents at .claude/agents/four-hat-*.md open
# their system prompt with "You are the <Hat> hat in /specify's four-hat
# review." (capitalized hat noun). They do NOT carry the old
# "Read this spec from …" priming the prior version of this hook expected — so
# Predicate 1 used to fail for every hat and hang the session. We now validate
# against the actual preamble. The marker is the case-insensitive signature
# substring "You are the <hat> hat" (matched against the transcript's first
# message), not the full prompt.
#
# If the agent files are renamed/reworded, update this dict in lockstep.

PRIMING_MARKERS = {
    "user": "you are the user hat",
    "engineer": "you are the engineer hat",
    "pm": "you are the pm hat",
    "skeptic": "you are the skeptic hat",
}

# ---- Finding-entry regex -------------------------------------------------
#
# SOL-132 reconciliation: the agents emit a `## Findings` section per
# rules/auditor-stance.md (one finding per {type, locus}), not a `## Objections`
# section with the old `- **<hat>** [<severity>] @ <locus>: <finding>` shape.
# auditor-stance does not pin a single bullet grammar; a finding is a bullet
# carrying a type, a locus and a severity. We validate the *loose* shape every
# auditor-stance finding shares — a bullet that names a severity token
# (low/med/high) somewhere — and treat anything else in the section (prose,
# sub-headings, the empty-section case) as advisory-pass. This is deliberately
# permissive: a malformed bullet is recorded for triage, never blocked.

FINDING_PATTERN = re.compile(
    r"""
    ^\s*[-*]\s+        # bullet prefix
    .*\b(?:low|med|high)\b   # a severity token somewhere in the bullet
    """,
    re.VERBOSE | re.IGNORECASE,
)


def _advisory_exit(code: str, diagnostic: str) -> None:
    """Record a diagnostic for triage and exit CLEAN (exit 0, no decision).

    SOL-132: every non-matching / incomplete state takes this path. We record
    the diagnostic via log_halt so a founder can triage a real format drift,
    but we NEVER emit a {"decision":"block"} output — for a SubagentStop hook a
    block means "do not stop", which loops the subagent forever. Advisory-only.
    """
    _lib.log_halt(code, diagnostic)
    _lib.trace(f"four-hat-objection-coverage: advisory ({code}); exiting clean")
    sys.exit(0)


def main() -> None:
    payload = _lib.read_hook_payload()
    _lib.trace("four-hat-objection-coverage: fired")

    # ---- SOL-132 loop-breaker: stop_hook_active guard ---------------------
    # If the runtime is re-invoking this Stop/SubagentStop hook because a prior
    # invocation returned a block decision, stop_hook_active is true. Exit 0
    # immediately so we can never participate in an unbounded continuation loop.
    # This is the universal break: it holds regardless of transcript shape.
    if payload.get("stop_hook_active"):
        _lib.trace("four-hat-objection-coverage: stop_hook_active set; exiting clean to break loop")
        sys.exit(0)

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
        diagnostic = (
            f"§four-hat-incomplete/unknown-hat: agent_type={agent_type!r} produced hat={hat!r}; "
            f"expected one of {sorted(PRIMING_MARKERS)}. "
            "Either the agent type was renamed without updating this hook's PRIMING_MARKERS dict, "
            "or the SubagentStop payload was malformed. Recorded for triage; not blocking."
        )
        _advisory_exit("§four-hat-incomplete/unknown-hat", diagnostic)

    transcript_path = Path(transcript_path_str)
    if not transcript_path.is_file():
        diagnostic = (
            f"§four-hat-incomplete/transcript-absent: agent_id={agent_id} (hat={hat}); "
            f"agent_transcript_path={transcript_path_str!r} does not resolve to a file. "
            "The subagent terminated without a readable transcript; coverage cannot be recomputed. "
            "Recorded for triage; not blocking."
        )
        _advisory_exit("§four-hat-incomplete/transcript-absent", diagnostic)

    # Parse the transcript JSONL
    transcript_entries = _read_transcript(transcript_path)
    if transcript_entries is None:
        diagnostic = (
            f"§four-hat-incomplete/transcript-malformed: agent_id={agent_id} (hat={hat}); "
            f"transcript at {transcript_path} is not valid JSONL or contains no readable entries. "
            "Recorded for triage; not blocking."
        )
        _advisory_exit("§four-hat-incomplete/transcript-malformed", diagnostic)

    # ---- Predicate 1: priming text present in first message ---------------
    first_msg = _first_message_content(transcript_entries)
    expected_marker = PRIMING_MARKERS[hat]
    if first_msg is None or expected_marker not in first_msg.lower():
        diagnostic = (
            f"§four-hat-incomplete/priming-text-missing: hat={hat}; "
            f"transcript={transcript_path}; "
            f"expected priming marker {expected_marker!r} absent from the first message. "
            "The agent's preamble did not match the expected 'You are the <hat> hat' signature; "
            "either the agent file was reworded or this was not a real four-hat dispatch. "
            "Recorded for triage; not blocking."
        )
        _advisory_exit("§four-hat-incomplete/priming-text-missing", diagnostic)

    # ---- Predicate 2: ## Findings section in final assistant message ------
    last_assistant_msg = _last_assistant_message_content(transcript_entries)
    if last_assistant_msg is None:
        diagnostic = (
            f"§four-hat-incomplete/no-final-assistant-message: hat={hat}; "
            f"transcript={transcript_path}; "
            "the transcript contains no assistant-role messages. Recorded for triage; not blocking."
        )
        _advisory_exit("§four-hat-incomplete/no-final-assistant-message", diagnostic)

    findings_section = _extract_section(last_assistant_msg, "Findings")
    if findings_section is None:
        diagnostic = (
            f"§four-hat-incomplete/findings-section-missing: hat={hat}; "
            f"transcript={transcript_path}; "
            "'## Findings' section absent in the final assistant message. "
            "The four-hat agents emit a `## Findings` section per rules/auditor-stance.md "
            "(empty section when there are no findings). Recorded for triage; not blocking."
        )
        _advisory_exit("§four-hat-incomplete/findings-section-missing", diagnostic)

    # ---- Predicate 3: finding entries loosely parseable -------------------
    # An empty Findings section is the zero-findings -> DONE case and is valid.
    malformed_entries = []
    for line_num, line in enumerate(findings_section.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        # Only bullets are candidate findings; non-bullet prose is allowed.
        if stripped.startswith(("-", "*")):
            if FINDING_PATTERN.match(line) is None:
                malformed_entries.append((line_num, line.rstrip()))

    if malformed_entries:
        diagnostic_lines = [
            f"§four-hat-incomplete/finding-entry-malformed: hat={hat}; "
            f"transcript={transcript_path}; "
            f"{len(malformed_entries)} finding bullets without a recognizable severity token:",
        ]
        for line_num, line in malformed_entries[:10]:  # cap diagnostic at 10
            diagnostic_lines.append(f"  line {line_num}: {line}")
        if len(malformed_entries) > 10:
            diagnostic_lines.append(f"  ...({len(malformed_entries) - 10} more)")
        diagnostic_lines.append(
            "Each finding bullet is expected to carry a severity token (low/med/high) "
            "per rules/auditor-stance.md. Recorded for triage; not blocking."
        )
        diagnostic = "\n".join(diagnostic_lines)
        _advisory_exit("§four-hat-incomplete/finding-entry-malformed", diagnostic)

    # All predicates pass for this hat. Exit clean with no decision.
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


def _first_message_content(entries: list[dict]) -> str | None:
    """Return the content of the first message carrying the agent's priming.

    SOL-132: the four-hat agents' "You are the <hat> hat" preamble is the
    agent definition's system prompt — depending on the Claude Code version it
    surfaces as the first system- or user-role transcript entry. We therefore
    return the first entry of either role that carries readable text, rather
    than requiring it to be a user-role message.
    """
    for entry in entries:
        # Transcript entries may vary by Claude Code version. Try common shapes:
        #   {"role": "system"|"user", "content": "..."}
        #   {"message": {"role": ..., "content": "..."}}
        role = entry.get("role") or entry.get("message", {}).get("role")
        if role in ("system", "user"):
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
                joined = "\n".join(p for p in parts if p)
                if joined:
                    return joined
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
