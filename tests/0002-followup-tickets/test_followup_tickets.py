#!/usr/bin/env python3
"""Failing-test seed for Child 0002-B — v0.2.x followup tickets (SOL-104).

Pyramid shape: capability-cluster (required: integration, perceptual;
forbidden: smoke, contract, invariance). 4 [integration] + 1 [perceptual].

Runnable with the standard library alone (pytest is not installed in this
environment); also collectable by pytest if present:

    python3 tests/0002-followup-tickets/test_followup_tickets.py

The four [integration] tests assert against the SEALED perceptual artifact
(docs/specs/0002-v0.2-release-wrap-up/perceptual/linear-tickets-created.json),
not against live Linear — the stdlib runner cannot call the Linear MCP. The
artifact is the consolidated `list_issues` capture of the four creations,
canonicalized (key-sorted, stable-field-only, list sorted by identifier). The
[perceptual] test asserts that canonical form is byte-stable (idempotent).

See docs/specs/0002-v0.2-release-wrap-up/spec.md AC-5..AC-8 and
decomposition.md Child 0002-B.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = (
    ROOT
    / "docs"
    / "specs"
    / "0002-v0.2-release-wrap-up"
    / "perceptual"
    / "linear-tickets-created.json"
)

# The "[SOL] Backlog" project all four followups land in.
BACKLOG_PROJECT_ID = "028e28f9-8e4b-4834-84f7-9488f4502f53"
REQUIRED_LABEL = "v0.2.x"

# Stable fields the canonical artifact carries per ticket (key-sorted).
STABLE_FIELDS = {"id", "identifier", "labels", "projectId", "title", "url"}


def _load_tickets():
    """Parse the sealed artifact; return the list of ticket dicts."""
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert isinstance(data, list), "artifact root must be a JSON array"
    return data


def _canonical(data) -> str:
    """The canonical byte-form: sort_keys, 2-space indent, trailing newline."""
    return json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def _one_matching(substr: str):
    """Return the single ticket whose title contains substr (assert exactly one)."""
    tickets = _load_tickets()
    matches = [t for t in tickets if substr in t.get("title", "")]
    assert len(matches) == 1, f"expected exactly one ticket matching {substr!r}, got {len(matches)}"
    return matches[0]


def _assert_required_fields(t: dict):
    assert STABLE_FIELDS.issubset(t.keys()), f"missing stable fields: {STABLE_FIELDS - t.keys()}"
    assert REQUIRED_LABEL in t["labels"], f"ticket {t.get('identifier')} lacks {REQUIRED_LABEL} label"
    assert t["projectId"] == BACKLOG_PROJECT_ID, "ticket not in [SOL] Backlog project"
    assert t["id"], "empty id"
    assert t["identifier"], "empty identifier"
    assert t["url"], "empty url"


# --- AC-5..AC-8: one integration test per capability ------------------------

def test_precompact_ticket_created_with_required_fields():  # [integration]
    _assert_required_fields(_one_matching("PreCompact"))


def test_priming_markers_ticket_created_with_required_fields():  # [integration]
    _assert_required_fields(_one_matching("PRIMING_MARKERS"))


def test_multiedit_ticket_created_with_required_fields():  # [integration]
    _assert_required_fields(_one_matching("MultiEdit"))


def test_ac_hash_regex_ticket_created_with_required_fields():  # [integration]
    _assert_required_fields(_one_matching("AC-hash regex"))


# --- perceptual: the consolidated capture is byte-stable --------------------

def test_linear_tickets_api_response_byte_stable():  # [perceptual]
    raw = ARTIFACT.read_text(encoding="utf-8")
    data = json.loads(raw)
    # Exactly the four followups, no more.
    assert len(data) == 4, f"expected 4 tickets, got {len(data)}"
    # Each entry carries only the stable fields (no ordering-sensitive noise).
    for t in data:
        assert set(t.keys()) == STABLE_FIELDS, f"unexpected fields: {set(t.keys()) ^ STABLE_FIELDS}"
    # Canonical form is idempotent: re-canonicalizing reproduces the bytes.
    assert raw == _canonical(data), "artifact is not in canonical byte-stable form"


def _main() -> int:
    g = dict(globals())
    tests = sorted(n for n in g if n.startswith("test_"))
    passed = failed = 0
    for n in tests:
        try:
            g[n]()
        except AssertionError as e:
            failed += 1
            print(f"FAIL {n}: {e}")
        except Exception as e:  # noqa: BLE001 — surface missing-artifact etc. as failures
            failed += 1
            print(f"FAIL {n}: {e!r}")
        else:
            passed += 1
            print(f"PASS {n}")
    print(f"\n{passed} passed, {failed} failed (of {len(tests)})")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_main())
