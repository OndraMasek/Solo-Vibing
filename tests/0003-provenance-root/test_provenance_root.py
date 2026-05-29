"""Failing-test seed for SOL-117 — seal the provenance root (0003, walking-skeleton).

Stdlib unittest. No third-party deps per D4.0. Requires Python 3.10+ (the seed
loads `tools/solo-verify`, which uses `match`); the bash hook subprocesses shell
out to the host `python3` only for the json-canonical sha (no `match`), so they
run on any python3.

Seed mapping to SOL-117 acceptance criteria (parent SOL-112 AC-1..AC-5):

  * (a) AC-3 smoke      — preflight-provenance.sh admits `/review SOL-102` against
                          the committed root: exit 0, empty stdout, empty stderr.
                          Mirrors test_preflight_provenance_passes_on_intact_chain.
  * (b) AC-2 contract   — common.sh `sha256_manifest_self_zeroed` over the sealed
                          manifest equals the sha the run-state carries (and the
                          python CLI helper agrees — the SOL-119 unified serializer).
  * (c) AC-1 smoke      — `.cascade/run-state.json` parses, schema_version is
                          "2.1-v2.1", and common.sh `read_run_state` loads it.
  * (d) AC-4 contract   — `solo-verify specify SOL-102` exits 0 against the sealed
                          root; the self-zeroed recompute is deterministic
                          (recompute-not-fabrication); seal-provenance.md records
                          the exit-0 run.
  * (e) AC-5 smoke      — a deliberately-broken fixture chain drives `solo-verify`
                          non-zero, proving the build path would halt-and-file
                          rather than seal against a broken chain.

Pre-seal: (a)-(d) FAIL (no run-state; manifests dir is .gitkeep-only). (e) is a
guard over existing halt behaviour and passes independently.

Run (host python3 is 3.9; use 3.11/3.12):
  python3.11 -m unittest discover -s tests/0003-provenance-root -v
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

if sys.version_info < (3, 10):  # pragma: no cover
    raise RuntimeError("SOL-117 seed requires Python 3.10+ per D4.0 (solo-verify uses match)")

REPO_ROOT = Path(__file__).resolve().parents[2]
SOLO_VERIFY_PATH = REPO_ROOT / "tools" / "solo-verify"
COMMON_SH = REPO_ROOT / ".claude" / "hooks" / "lib" / "common.sh"
PREFLIGHT = REPO_ROOT / ".claude" / "hooks" / "preflight-provenance.sh"

RUN_STATE = REPO_ROOT / ".cascade" / "run-state.json"
MANIFEST = REPO_ROOT / ".cascade" / "manifests" / "SOL-102-specify.json"
SEAL_NOTE = REPO_ROOT / "docs" / "specs" / "0003-provenance-root" / "authoring-notes" / "seal-provenance.md"

MANIFEST_REL = ".cascade/manifests/SOL-102-specify.json"


def _load_solo_verify():
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
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(REPO_ROOT))
    proc = subprocess.run(
        ["bash", "-c", 'source "$1"; sha256_manifest_self_zeroed "$2"',
         "_", str(COMMON_SH), str(manifest_path)],
        capture_output=True, text=True, env=env,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"bash sha256_manifest_self_zeroed failed (rc={proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def _run_preflight(prompt: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(REPO_ROOT))
    return subprocess.run(
        ["bash", str(PREFLIGHT)],
        input=json.dumps({"prompt": prompt}),
        capture_output=True, text=True, env=env, timeout=30,
    )


def _run_solo_verify(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(cwd))
    return subprocess.run(
        [sys.executable, str(SOLO_VERIFY_PATH), *args],
        cwd=str(cwd), env=env, capture_output=True, text=True, timeout=30,
    )


class AC3PreflightAdmitsReview(unittest.TestCase):
    """(a) AC-3 smoke — preflight-provenance.sh passes on the intact committed root."""

    def test_preflight_provenance_passes_on_intact_chain(self):
        # tag: smoke
        cp = _run_preflight("/review SOL-102")
        self.assertEqual(cp.returncode, 0,
                         f"preflight must admit /review SOL-102; stderr={cp.stderr!r} stdout={cp.stdout!r}")
        self.assertEqual(cp.stdout, "", f"expected empty stdout; got {cp.stdout!r}")
        self.assertEqual(cp.stderr, "", f"expected empty stderr; got {cp.stderr!r}")


class AC2ManifestShaMatchesRunState(unittest.TestCase):
    """(b) AC-2 contract — sealed manifest sha == run-state stored sha."""

    def test_manifest_self_zeroed_sha_matches_run_state(self):
        # tag: contract
        self.assertTrue(MANIFEST.is_file(), f"sealed manifest absent at {MANIFEST}")
        self.assertTrue(RUN_STATE.is_file(), f"run-state absent at {RUN_STATE}")
        run_state = json.loads(RUN_STATE.read_text(encoding="utf-8"))
        stored = run_state["last_completed_stage"]["postcondition_manifest_sha256"]
        # The python CLI helper (the canonical serializer) agrees.
        self.assertEqual(sv._sha256_manifest_self_zeroed(MANIFEST), stored,
                         "CLI self-zeroed sha must equal run-state's stored sha")
        # The bash hook substrate (delegates to python3 per SOL-119) agrees too.
        self.assertEqual(_bash_sha(MANIFEST), stored,
                         "bash hook self-zeroed sha must equal run-state's stored sha")


class AC1RunStateFloor(unittest.TestCase):
    """(c) AC-1 smoke — run-state floor exists, is v2.1, and read_run_state loads it."""

    def test_run_state_schema_version_is_2_1_v2_1(self):
        # tag: smoke
        self.assertTrue(RUN_STATE.is_file(), f"run-state absent at {RUN_STATE}")
        run_state = json.loads(RUN_STATE.read_text(encoding="utf-8"))
        self.assertEqual(run_state.get("schema_version"), "2.1-v2.1")
        last = run_state.get("last_completed_stage") or {}
        self.assertEqual(last.get("postcondition_manifest_path"), MANIFEST_REL,
                         "run-state must chain to the sealed SOL-102-specify manifest")

    def test_common_sh_read_run_state_loads_floor(self):
        # tag: smoke
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(REPO_ROOT))
        proc = subprocess.run(
            ["bash", "-c", 'source "$1"; read_run_state && echo LOADED', "_", str(COMMON_SH)],
            capture_output=True, text=True, env=env, timeout=30,
        )
        self.assertEqual(proc.returncode, 0, f"read_run_state failed: {proc.stderr.strip()}")
        self.assertIn("LOADED", proc.stdout)


class AC4SoloVerifySealAndDeterminism(unittest.TestCase):
    """(d) AC-4 contract+invariance — exit-0 solo-verify run, deterministic re-seal."""

    def test_solo_verify_specify_sol_102_exits_zero(self):
        # tag: contract
        cp = _run_solo_verify(["specify", "SOL-102"], cwd=REPO_ROOT)
        self.assertEqual(cp.returncode, 0,
                         f"solo-verify specify SOL-102 must exit 0; "
                         f"rc={cp.returncode} stdout={cp.stdout!r} stderr={cp.stderr!r}")

    def test_reseal_is_deterministic(self):
        # tag: contract
        # Recompute-not-fabrication: hashing the sealed manifest's own content
        # (manifest_sha256 zeroed) twice yields the same value, and that value
        # is exactly what the manifest carries.
        self.assertTrue(MANIFEST.is_file(), f"sealed manifest absent at {MANIFEST}")
        first = sv._sha256_manifest_self_zeroed(MANIFEST)
        second = sv._sha256_manifest_self_zeroed(MANIFEST)
        self.assertEqual(first, second, "self-zeroed recompute must be deterministic")
        stored = json.loads(MANIFEST.read_text(encoding="utf-8"))["manifest_sha256"]
        self.assertEqual(first, stored,
                         "recomputed sha must equal the manifest's stored manifest_sha256")

    def test_seal_provenance_note_records_exit_zero_run(self):
        # tag: perceptual
        self.assertTrue(SEAL_NOTE.is_file(), f"AC-4 audit note absent at {SEAL_NOTE}")
        text = SEAL_NOTE.read_text(encoding="utf-8")
        self.assertIn("solo-verify specify SOL-102", text,
                      "audit note must record the exact solo-verify command")
        self.assertIn("exit 0", text, "audit note must record the exit-0 result")


class AC5BrokenChainHalts(unittest.TestCase):
    """(e) AC-5 smoke — a broken fixture chain drives solo-verify non-zero.

    A non-zero solo-verify means /build MUST NOT seal — it halts and files a
    finding instead. This guards that the halt path fires on a broken chain
    (here: run-state names a manifest whose stored sha no longer matches the
    manifest's content — the same shape a tampered/absent upstream produces).
    """

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._td.name)
        (self.tmpdir / ".cascade" / "manifests").mkdir(parents=True)

    def tearDown(self) -> None:
        self._td.cleanup()

    def test_broken_chain_drives_solo_verify_nonzero(self):
        # tag: smoke
        manifest = {
            "stage": "/specify", "ticket": "SOL-102",
            "outputs": {"decomposition_strategy": "hybrid", "pyramid_shape": None,
                        "failing_test_seed": []},
            "input_provenance": {"parent_manifest_path": None},
            "manifest_sha256": "",
        }
        mpath = self.tmpdir / ".cascade" / "manifests" / "SOL-102-specify.json"
        mpath.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        run_state = {
            "schema_version": "2.1-v2.1",
            "last_completed_stage": {
                "stage": "/specify", "ticket": "SOL-102",
                "postcondition_manifest_path": MANIFEST_REL,
                # Deliberately wrong sha → §provenance-chain-broken.
                "postcondition_manifest_sha256": "0" * 64,
            },
        }
        (self.tmpdir / ".cascade" / "run-state.json").write_text(
            json.dumps(run_state, indent=2), encoding="utf-8")
        cp = _run_solo_verify(["specify", "SOL-102"], cwd=self.tmpdir)
        self.assertNotEqual(cp.returncode, 0,
                            "broken chain must drive solo-verify non-zero (build must not seal)")
        self.assertIn("§provenance-chain-broken", cp.stdout + cp.stderr,
                      f"expected provenance halt; stdout={cp.stdout!r} stderr={cp.stderr!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
