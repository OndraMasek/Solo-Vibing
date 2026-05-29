#!/usr/bin/env python3
"""Failing-test seed for Child 0002-A — v0.2 docs lockstep (SOL-103).

Pyramid shape: walking-skeleton (required: smoke, perceptual; forbidden:
contract, invariance). 12 [smoke] + 1 [perceptual].

Runnable with the standard library alone (pytest is not installed in this
environment); also collectable by pytest if present:

    python3 tests/0002-docs-lockstep/test_docs_lockstep.py

The single [perceptual] test (AC-4) is SKIPPED, not faked: its evidence
requires two byte-stable `/onboard --dry-run` renders, and `/onboard` has no
--dry-run mode yet. Sealing a fabricated artifact would defeat the gate. See
docs/specs/0002-v0.2-release-wrap-up/authoring-notes/bootstrap-exception.md.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLAUDE = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
TEMPLATE = (ROOT / "docs" / "templates" / "CLAUDE.md.template").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")

EIGHT_HOOKS = [
    "preflight-provenance.sh",
    "pyramid-tampering.sh",
    "four-hat-objection-coverage.py",
    "stop-orchestrator.sh",
    "session-start-state-restore.sh",
    "session-end-telemetry.sh",
    "precompact-safe-boundary.sh",
    "pretool-write-denylist.sh",
]

SIX_SUBSECTIONS = [
    "### Cascade gates",
    "### Strategy enum",
    "### Hooks",
    "### Tainted state",
    "### Code markers",
    "### CI",
]


class _Skip(Exception):
    """Raised by a test to signal a skip (AC blocked, not failed)."""


def _v0_2_block(text: str) -> str:
    """Extract the '## v0.2 cascade primitives' section up to the next H2."""
    start = text.index("## v0.2 cascade primitives")
    rest = text[start + len("## v0.2 cascade primitives"):]
    nxt = rest.find("\n## ")
    return text[start:] if nxt == -1 else text[start:start + len("## v0.2 cascade primitives") + nxt]


# --- AC-1: root CLAUDE.md ---------------------------------------------------

def test_claude_md_drops_no_hooks_sentence():  # [smoke]
    assert "no hooks in v0.1" not in CLAUDE


def test_claude_md_has_cascade_gates_subsection():  # [smoke]
    assert "### Cascade gates" in CLAUDE
    assert "tools/solo-verify --list-gates" in CLAUDE


def test_claude_md_has_hooks_subsection():  # [smoke]
    assert "### Hooks" in CLAUDE
    assert ".claude/settings.json" in CLAUDE


def test_claude_md_has_strategy_enum_subsection():  # [smoke]
    assert "### Strategy enum" in CLAUDE
    for strat in ("walking-skeleton", "api-boundary", "capability-cluster",
                  "refactor-spike", "hybrid"):
        assert strat in CLAUDE, strat


def test_claude_md_has_tainted_state_subsection():  # [smoke]
    assert "### Tainted state" in CLAUDE
    assert "is_tainted" in CLAUDE and "taint_reason" in CLAUDE


def test_claude_md_has_code_markers_subsection():  # [smoke]
    assert "### Code markers" in CLAUDE
    assert ".claude/rules/code-markers.md" in CLAUDE


def test_claude_md_has_ci_subsection():  # [smoke]
    assert "### CI" in CLAUDE
    assert ".github/workflows/ci.yml" in CLAUDE


def test_claude_md_hooks_subsection_names_eight_scripts():  # [smoke]
    for hook in EIGHT_HOOKS:
        assert hook in CLAUDE, hook


# --- AC-2: README.md --------------------------------------------------------

def test_readme_status_block_reads_v0_2():  # [smoke]
    assert "v0.2 cascade primitives integrated and self-applied; v0.2.x cycle open" in README


def test_readme_has_whats_new_section():  # [smoke]
    assert "## What's new in v0.2" in README


# --- AC-3: docs/templates/CLAUDE.md.template lockstep -----------------------

def test_template_matches_root_for_shared_sections():  # [smoke]
    # The v0.2 block is authored identically in both files (lockstep).
    assert _v0_2_block(TEMPLATE) == _v0_2_block(CLAUDE)
    for sub in SIX_SUBSECTIONS:
        assert sub in TEMPLATE, sub
    for hook in EIGHT_HOOKS:
        assert hook in TEMPLATE, hook


def test_template_references_run_state_canonical_path():  # [smoke]
    assert ".cascade/run-state.json" in TEMPLATE


# --- AC-4: perceptual (DEFERRED — see module docstring) ---------------------

def test_onboard_dry_run_byte_stable():  # [perceptual]
    raise _Skip(
        "AC-4 blocked: `/onboard --dry-run` capability is not implemented, so "
        "the byte-stable perceptual artifact cannot be sealed. Not fabricated. "
        "Tracked in bootstrap-exception.md / follow-up ticket."
    )


def _main() -> int:
    g = dict(globals())
    tests = sorted(n for n in g if n.startswith("test_"))
    passed = skipped = failed = 0
    for n in tests:
        try:
            g[n]()
        except _Skip as e:
            skipped += 1
            print(f"SKIP {n}: {e}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {n}: {e!r}")
        else:
            passed += 1
            print(f"PASS {n}")
    print(f"\n{passed} passed, {skipped} skipped, {failed} failed (of {len(tests)})")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_main())
