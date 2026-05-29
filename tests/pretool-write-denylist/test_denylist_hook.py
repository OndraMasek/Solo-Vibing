#!/usr/bin/env python3
"""Tests for .claude/hooks/pretool-write-denylist.sh — build-agent-scoped
cascade-control write guard (SOL fix: hook blocked the cascade's own authoring
stages).

Verifies the three acceptance criteria:
  1. Founder context (no SOLO_BUILD_AGENT): denylisted writes via Write AND Bash
     soft-pass — /onboard et al. can write docs/.solo-config.json,
     .cascade/run-state.json, .cascade/manifests/* with no workaround.
  2. Build-agent context (SOLO_BUILD_AGENT=1): denylisted writes are blocked via
     Write/Edit/MultiEdit AND via Bash redirection/tee/cp (bypass closed). Reads
     and non-denylisted writes still pass.
  3. The block reason describes a real recovery mechanism (founder-session
     orchestration stage), not the old dead-end "use the responsible skill".

Runnable with the standard library alone:

    python3 tests/pretool-write-denylist/test_denylist_hook.py

Requires: bash + python3 on PATH (documented repo prereqs).
"""
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "pretool-write-denylist.sh"
DENYLIST = ROOT / ".claude" / "agents" / "build-write-denylist.txt"

OLD_DEAD_END = "use the responsible skill that has authority to write it"


class _Skip(Exception):
    pass


def _run(tool_name, tool_input, build_agent):
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(ROOT)
    env.pop("SOLO_BUILD_AGENT", None)
    if build_agent:
        env["SOLO_BUILD_AGENT"] = "1"
    payload = json.dumps({"tool_name": tool_name, "tool_input": tool_input})
    p = subprocess.run(
        ["bash", str(HOOK)],
        input=payload, env=env, capture_output=True, text=True, timeout=20,
    )
    assert p.returncode == 0, f"hook exited {p.returncode}; stderr={p.stderr!r}"
    out = p.stdout.strip()
    decision = None
    if out:
        decision = json.loads(out)  # must be valid JSON when present
    return decision


def _blocked(decision):
    return bool(decision) and decision.get("decision") == "block"


def _reason(decision):
    return (decision or {}).get("reason", "")


# --- preconditions ----------------------------------------------------------

def test_hook_and_denylist_exist():
    assert HOOK.is_file(), HOOK
    assert DENYLIST.is_file(), DENYLIST
    pats = [l.strip() for l in DENYLIST.read_text().splitlines()
            if l.strip() and not l.strip().startswith("#")]
    for required in ("docs/.solo-config.json", ".cascade/run-state.json",
                     ".cascade/manifests/*"):
        assert required in pats, f"expected denylist pattern {required!r}"


# --- AC1: founder context soft-passes (the bug) -----------------------------

def test_founder_write_config_softpasses():
    assert _run("Write", {"file_path": "docs/.solo-config.json"}, build_agent=False) is None


def test_founder_write_runstate_softpasses():
    assert _run("Write", {"file_path": ".cascade/run-state.json"}, build_agent=False) is None


def test_founder_write_onboard_manifest_softpasses():
    d = _run("Write", {"file_path": ".cascade/manifests/SOL-onboard.json"}, build_agent=False)
    assert d is None


def test_founder_bash_redirect_to_config_softpasses():
    d = _run("Bash", {"command": "cat > docs/.solo-config.json <<'EOF'\n{}\nEOF"}, build_agent=False)
    assert d is None


# --- AC2: build-agent context blocks (Write/Edit/MultiEdit) ------------------

def test_build_write_config_blocks():
    d = _run("Write", {"file_path": "docs/.solo-config.json"}, build_agent=True)
    assert _blocked(d)
    assert "§cascade-control-write-blocked" in _reason(d)


def test_build_write_config_absolute_path_blocks():
    d = _run("Write", {"file_path": str(ROOT / "docs/.solo-config.json")}, build_agent=True)
    assert _blocked(d)


def test_build_write_manifest_glob_blocks():
    d = _run("Write", {"file_path": ".cascade/manifests/SOL-12-3-build.json"}, build_agent=True)
    assert _blocked(d)


def test_build_edit_rule_glob_blocks():
    d = _run("Edit", {"file_path": ".claude/rules/write-discipline.md"}, build_agent=True)
    assert _blocked(d)


def test_build_multiedit_halt_messages_blocks():
    d = _run("MultiEdit", {"file_path": "docs/templates/halt-messages.md"}, build_agent=True)
    assert _blocked(d)


def test_build_write_nondenylisted_softpasses():
    assert _run("Write", {"file_path": "src/app.py"}, build_agent=True) is None
    assert _run("Write", {"file_path": "docs/specs/0009-x/spec.md"}, build_agent=True) is None


# --- AC2: build-agent context closes the Bash bypass ------------------------

def test_build_bash_heredoc_redirect_blocks():
    d = _run("Bash", {"command": "cat > docs/.solo-config.json <<'EOF'\n{}\nEOF"}, build_agent=True)
    assert _blocked(d), "heredoc redirection bypass must be blocked in build context"


def test_build_bash_append_runstate_blocks():
    d = _run("Bash", {"command": "echo '{}' >> .cascade/run-state.json"}, build_agent=True)
    assert _blocked(d)


def test_build_bash_tee_rule_blocks():
    d = _run("Bash", {"command": "echo x | tee .claude/rules/naming.md"}, build_agent=True)
    assert _blocked(d)


def test_build_bash_cp_dest_lock_blocks():
    d = _run("Bash", {"command": "cp /tmp/x .solo-locks/resource.lock"}, build_agent=True)
    assert _blocked(d)


def test_build_bash_mv_dest_denylist_blocks():
    d = _run("Bash", {"command": "mv /tmp/cfg docs/.solo-config.json"}, build_agent=True)
    assert _blocked(d)


def test_build_bash_read_config_softpasses():
    # Reading a denylisted file is fine — only writes are guarded.
    assert _run("Bash", {"command": "cat docs/.solo-config.json | jq .marker"}, build_agent=True) is None


def test_build_bash_nondenylisted_redirect_softpasses():
    assert _run("Bash", {"command": "echo hi > /tmp/out.txt"}, build_agent=True) is None


def test_build_bash_run_tests_softpasses():
    assert _run("Bash", {"command": "python3 -m pytest -q"}, build_agent=True) is None


# --- AC3: recovery copy describes a real mechanism --------------------------

def test_recovery_copy_is_not_a_dead_end():
    d = _run("Write", {"file_path": "docs/.solo-config.json"}, build_agent=True)
    reason = _reason(d)
    assert OLD_DEAD_END not in reason, "block reason still uses the dead-end recovery phrasing"
    assert "founder session" in reason
    assert "orchestration stage" in reason


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
