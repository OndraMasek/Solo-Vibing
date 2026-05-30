#!/usr/bin/env python3
"""Tests for .claude/hooks/four-hat-objection-coverage.py — the SubagentStop
hook that hung /specify (SOL-132).

The hook is the cascade's four-hat coverage check. The bug: it validated a
transcript shape the agents never emit (it expected "Read this spec from …"
priming and `## Objections`/`## Seal` sections; the real agents say
"You are the <hat> hat" and emit `## Findings`), and on every miss it emitted
a {"decision":"block"} output. For a SubagentStop hook "block" means "do NOT
stop" — so the subagent looped forever (runs hung 2h+/7h). It also ignored the
`stop_hook_active` loop-break flag.

These tests prove the SOL-132 contract:
  1. stop_hook_active=true  -> exit 0, NO output (universal loop break).
  2. A transcript that does NOT match the expected format -> exit 0, NO block
     decision (advisory only, can never hang a session).
  3. The advisory contract holds whether the transcript is absent, malformed,
     missing priming, or missing the Findings section.
  4. A well-formed four-hat transcript (real "You are the <hat> hat" priming +
     `## Findings`) passes clean with no output.

Runnable with the standard library alone:

    python3 tests/four-hat-objection-coverage/test_four_hat_hook.py

Requires: python3 on PATH (documented repo prereq).
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "four-hat-objection-coverage.py"


class _Skip(Exception):
    pass


def _write_transcript(lines):
    """Write a JSONL transcript to a temp file; return its path string."""
    fd, path = tempfile.mkstemp(suffix=".jsonl", prefix="four-hat-")
    with os.fdopen(fd, "w") as f:
        for entry in lines:
            f.write(json.dumps(entry) + "\n")
    return path


def _run(payload):
    env = dict(os.environ)
    # Redirect CLAUDE_PROJECT_DIR to a throwaway dir so the hook's advisory
    # log_halt writes land in a temp location, not the real repo .cascade/halt.
    # The hook reads its transcript from the payload's absolute path and imports
    # _lib from its own dir, so it needs nothing from the real project root.
    with tempfile.TemporaryDirectory(prefix="four-hat-projdir-") as projdir:
        env["CLAUDE_PROJECT_DIR"] = projdir
        p = subprocess.run(
            ["python3", str(HOOK)],
            input=json.dumps(payload),
            env=env,
            capture_output=True,
            text=True,
            timeout=20,
        )
    return p


def _decision(p):
    out = p.stdout.strip()
    if not out:
        return None
    return json.loads(out)


def _is_block(p):
    d = _decision(p)
    return bool(d) and d.get("decision") == "block"


# --- precondition -----------------------------------------------------------

def test_hook_exists():
    assert HOOK.is_file(), HOOK


# --- AC1: stop_hook_active guard breaks the loop universally -----------------

def test_stop_hook_active_exits_clean():
    # Even with a totally malformed/absent transcript, the guard wins first.
    p = _run({
        "agent_type": "four-hat-engineer",
        "agent_id": "a1",
        "agent_transcript_path": "/nonexistent/path.jsonl",
        "stop_hook_active": True,
    })
    assert p.returncode == 0, f"exit={p.returncode} stderr={p.stderr!r}"
    assert _decision(p) is None, "stop_hook_active must yield NO output (no block)"


# --- AC2: format mismatch is advisory, never a block ------------------------

def test_mismatched_format_does_not_block():
    # A transcript with the OLD/wrong shape: no "You are the X hat" priming,
    # an `## Objections` section instead of `## Findings`. The old hook would
    # have hard-blocked here (priming-text-missing) and hung the session.
    transcript = _write_transcript([
        {"role": "user", "content": "Read this spec from the engineer's perspective"},
        {"role": "assistant", "content": "## Objections\n\n- something\n\n## Seal\nSealed."},
    ])
    try:
        p = _run({
            "agent_type": "four-hat-engineer",
            "agent_id": "a2",
            "agent_transcript_path": transcript,
            "stop_hook_active": False,
        })
    finally:
        os.unlink(transcript)
    assert p.returncode == 0, f"exit={p.returncode} stderr={p.stderr!r}"
    assert not _is_block(p), f"format mismatch must NOT block; got {p.stdout!r}"
    assert _decision(p) is None


def test_absent_transcript_does_not_block():
    p = _run({
        "agent_type": "four-hat-pm",
        "agent_id": "a3",
        "agent_transcript_path": "/nonexistent/path.jsonl",
        "stop_hook_active": False,
    })
    assert p.returncode == 0
    assert not _is_block(p)


def test_missing_findings_section_does_not_block():
    # Correct priming, but the assistant message has no `## Findings` section.
    transcript = _write_transcript([
        {"role": "system", "content": "You are the Skeptic hat in /specify's four-hat review."},
        {"role": "assistant", "content": "I looked at the spec and have nothing structured."},
    ])
    try:
        p = _run({
            "agent_type": "four-hat-skeptic",
            "agent_id": "a4",
            "agent_transcript_path": transcript,
            "stop_hook_active": False,
        })
    finally:
        os.unlink(transcript)
    assert p.returncode == 0
    assert not _is_block(p)


# --- AC3: a well-formed real-shape transcript passes clean ------------------

def test_wellformed_findings_transcript_passes_clean():
    transcript = _write_transcript([
        {"role": "system", "content": "You are the Engineer hat in /specify's four-hat review."},
        {"role": "assistant", "content": (
            "## Findings\n\n"
            "- missing-edge-case @ AC-3: no timeout path described [high]\n"
            "- assumption-unstated @ section 2: rate-limit scope unclear [med]\n"
        )},
    ])
    try:
        p = _run({
            "agent_type": "four-hat-engineer",
            "agent_id": "a5",
            "agent_transcript_path": transcript,
            "stop_hook_active": False,
        })
    finally:
        os.unlink(transcript)
    assert p.returncode == 0, f"exit={p.returncode} stderr={p.stderr!r}"
    assert _decision(p) is None, f"well-formed transcript must pass clean; got {p.stdout!r}"


def test_empty_findings_section_passes_clean():
    # Zero findings -> empty `## Findings` section is valid (DONE case).
    transcript = _write_transcript([
        {"role": "system", "content": "You are the User hat in /specify's four-hat review."},
        {"role": "assistant", "content": "## Findings\n\n"},
    ])
    try:
        p = _run({
            "agent_type": "four-hat-user",
            "agent_id": "a6",
            "agent_transcript_path": transcript,
            "stop_hook_active": False,
        })
    finally:
        os.unlink(transcript)
    assert p.returncode == 0
    assert _decision(p) is None


# --- never-block invariant: no input shape produces a block decision --------

def test_no_input_ever_produces_block():
    cases = [
        {"agent_type": "four-hat-engineer", "agent_transcript_path": "/nope", "stop_hook_active": False},
        {"agent_type": "four-hat-zzz", "agent_transcript_path": "/nope", "stop_hook_active": False},
        {"agent_type": "four-hat-pm", "agent_transcript_path": "/nope", "stop_hook_active": True},
    ]
    for payload in cases:
        p = _run(payload)
        assert p.returncode == 0, f"{payload}: exit={p.returncode} stderr={p.stderr!r}"
        assert not _is_block(p), f"{payload}: produced a block decision {p.stdout!r}"


def _main():
    g = dict(globals())
    tests = sorted(n for n in g if n.startswith("test_"))
    passed = skipped = failed = 0
    for name in tests:
        try:
            g[name]()
            print(f"PASS {name}")
            passed += 1
        except _Skip as e:
            print(f"SKIP {name}: {e}")
            skipped += 1
        except Exception as e:  # noqa: BLE001
            print(f"FAIL {name}: {e}")
            failed += 1
    total = len(tests)
    print(f"\n{passed} passed, {skipped} skipped, {failed} failed (of {total})")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_main())
