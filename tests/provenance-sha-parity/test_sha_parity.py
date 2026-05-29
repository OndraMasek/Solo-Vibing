"""Parity test for the D2.1 v2 step-3 manifest self-zeroed sha (SOL-119).

The cascade has two implementations of the "recompute manifest sha with
`manifest_sha256` zeroed" predicate:

  * bash  — `.claude/hooks/lib/common.sh` `sha256_manifest_self_zeroed`,
            called by `preflight-provenance.sh` (the UserPromptSubmit gate).
  * python — `tools/solo-verify` `_sha256_manifest_self_zeroed`, called by
            every `solo-verify <stage>` provenance gate.

If they disagree, no single `run-state.last_completed_stage.postcondition_
manifest_sha256` can satisfy both the hook and the CLI — a provenance root is
incoherent (the bug SOL-119 fixes; surfaced by SOL-117). This test asserts
byte-level parity across edge cases that `jq` cannot reproduce against python's
`json.dumps` (float formatting, non-ASCII escaping, whitespace).

  # tag: contract

Run:
  python3 -m unittest discover tests/provenance-sha-parity/ -v
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SOLO_VERIFY_PATH = REPO_ROOT / "tools" / "solo-verify"
COMMON_SH = REPO_ROOT / ".claude" / "hooks" / "lib" / "common.sh"


def _load_solo_verify():
    """Load the extensionless `solo-verify` script as a module (per the
    test_solo_verify.py loader pattern)."""
    loader = importlib.machinery.SourceFileLoader("solo_verify", str(SOLO_VERIFY_PATH))
    spec = importlib.util.spec_from_loader("solo_verify", loader)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"could not load solo-verify from {SOLO_VERIFY_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sv = _load_solo_verify()


def _bash_sha(manifest_path: Path) -> str:
    """Invoke the real bash `sha256_manifest_self_zeroed` from common.sh."""
    # CLAUDE_PROJECT_DIR is set so common.sh skips its walk-up resolution; the
    # value is irrelevant to the hashing function itself.
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(manifest_path.parent))
    proc = subprocess.run(
        ["bash", "-c",
         'source "$1"; sha256_manifest_self_zeroed "$2"',
         "_", str(COMMON_SH), str(manifest_path)],
        capture_output=True, text=True, env=env,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"bash sha256_manifest_self_zeroed failed (rc={proc.returncode}): "
            f"{proc.stderr.strip()}"
        )
    return proc.stdout.strip()


# Fixtures chosen to exercise the formatting axes where jq and python diverge.
FIXTURES: dict[str, dict[str, Any]] = {
    "plain": {
        "stage": "/specify",
        "ticket": "SOL-102",
        "manifest_sha256": "deadbeef",
        "outputs": {"b": 2, "a": 1},
    },
    "float": {  # jq prints 50.0 as 50; python keeps 50.0
        "stage": "/build",
        "ticket": "SOL-1-1",
        "manifest_sha256": "",
        "outputs": {"cost_usd": 50.0, "iteration_count": 3},
    },
    "non_ascii": {  # jq emits raw UTF-8; python json.dumps escapes to \uXXXX
        "stage": "/onboard",
        "marker": "SOL",
        "manifest_sha256": "x",
        "outputs": {"author": "Ondřej Mašek", "summary": "naïve café"},
    },
    "nested_specify": {  # resembles the SOL-102-specify root SOL-117 will seal
        "stage": "/specify",
        "ticket": "SOL-102",
        "spec_sealed_at": "2026-05-20T00:00:00Z",
        "outputs": {
            "spec_path": "docs/specs/0002-v0.2-release-wrap-up/spec.md",
            "decomposition_strategy": "hybrid",
            "pyramid_shape": None,
            "failing_test_seed": [],
            "acceptance_criteria": ["AC-1", "AC-2", "AC-8"],
        },
        "input_provenance": {"parent_manifest_path": None},
        "manifest_sha256": "tobereplaced",
    },
}


class ManifestShaParity(unittest.TestCase):
    """The bash hook and the python CLI must agree on the self-zeroed sha."""

    def _write(self, name: str, payload: dict[str, Any]) -> Path:
        # Real manifests are pretty-printed on disk; the sha is computed over
        # the canonical (compact) form, not the file bytes. Write pretty to
        # prove the recompute canonicalizes rather than hashing file bytes.
        td = tempfile.mkdtemp()
        path = Path(td) / f"{name}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def test_bash_and_python_self_zeroed_sha_agree(self) -> None:
        for name, payload in FIXTURES.items():
            with self.subTest(fixture=name):
                path = self._write(name, payload)
                py = sv._sha256_manifest_self_zeroed(path)
                sh = _bash_sha(path)
                self.assertEqual(
                    sh, py,
                    f"manifest sha divergence on fixture '{name}': "
                    f"bash={sh} python={py}",
                )

    def test_recompute_ignores_stored_manifest_sha256(self) -> None:
        # Two manifests identical except for the stored manifest_sha256 value
        # must hash the same (the field is zeroed before hashing).
        base = {"stage": "/specify", "ticket": "SOL-102", "outputs": {"a": 1}}
        p1 = self._write("zeroed_a", {**base, "manifest_sha256": ""})
        p2 = self._write("zeroed_b", {**base, "manifest_sha256": "ffffffff"})
        self.assertEqual(sv._sha256_manifest_self_zeroed(p1),
                         sv._sha256_manifest_self_zeroed(p2))
        self.assertEqual(_bash_sha(p1), _bash_sha(p2))


if __name__ == "__main__":
    unittest.main()
