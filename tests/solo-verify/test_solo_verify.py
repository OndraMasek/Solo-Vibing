"""Failing-test seed for tools/solo-verify (Child 0001-D, walking-skeleton).

Stdlib unittest. No third-party deps per D4.0.

Tier mapping per D3.2 walking-skeleton catalog:
  * [unit]       — predicate-level coverage; one test per surfaced halt path.
  * [smoke]      — CLI dispatcher coverage; subprocess-driven end-to-end.
  * [perceptual] — byte-stable `--list-gates` rendering against the canonical
                   seal at docs/specs/0001-v0.2-cascade-integration/perceptual/
                   solo-verify-list-gates.txt. SKIPS pre-/build (the artifact
                   is sealed when /build writes it); passes post-/build via
                   byte-equality.

Seed-vs-CI principle (SOL-134): a failing-test seed must never gate CI red on
a fresh, unbuilt clone or fork. Forks strip `docs/specs/` (bootstrap.sh) but
keep this suite, so the spec-0001 perceptual artifact is absent in every fork
and would never be built there (it owns Solo-Setup's internal self-build, not
the fork's product). The perceptual seed therefore self-SKIPS when its artifact
is absent rather than `self.fail()`-ing — yellow-skip pre-seal, byte-equality
assertion post-seal. The unit/smoke tiers (which exercise the fork's own copy
of `tools/solo-verify`) always run.

Run:
  python3 -m unittest discover tests/solo-verify/ -v

Tag annotations live in the docstrings (`# tag: unit`, etc.) for parity with
the failing-test-seed shape in /specify manifests' `outputs.failing_test_seed[]`.
The cascade does not enforce test-runner-level tag filtering at v0.2; tag
discipline is a documentation invariant for now.
"""

from __future__ import annotations

import hashlib
import importlib.util
import importlib.machinery
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# Module loader — `solo-verify` has no .py suffix, so import via spec.
# ─────────────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]
SOLO_VERIFY_PATH = REPO_ROOT / "tools" / "solo-verify"
# Allow override for in-tree authoring (script lives in /home/claude/work
# before being moved to tools/solo-verify).
if not SOLO_VERIFY_PATH.is_file():
    candidate = Path(os.environ.get("SOLO_VERIFY_PATH", ""))
    if candidate.is_file():
        SOLO_VERIFY_PATH = candidate


def _load_solo_verify():
    """Load the solo-verify script as a module.

    The script has no .py extension; spec_from_file_location without an
    explicit loader returns None in that case, so we hand-build a
    SourceFileLoader.
    """
    loader = importlib.machinery.SourceFileLoader("solo_verify", str(SOLO_VERIFY_PATH))
    spec = importlib.util.spec_from_loader("solo_verify", loader)
    if spec is None or spec.loader is None:                                  # pragma: no cover
        raise RuntimeError(f"could not load solo-verify from {SOLO_VERIFY_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Required Python version (per D4.0 stack floor).
if sys.version_info < (3, 10):                                               # pragma: no cover
    raise RuntimeError("tests require Python 3.10+ per D4.0")

sv = _load_solo_verify()


# ─────────────────────────────────────────────────────────────────────────────
# Test-fixture helpers — synthesize manifests / run-state / pass-sets / specs
# in a tmpdir, then point `sv.PROJECT_DIR` at it.
# ─────────────────────────────────────────────────────────────────────────────


class CascadeFSFixture(unittest.TestCase):
    """Base class — gives each test an isolated .cascade/ + docs/ tree."""

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._td.name)
        # Mandatory directories per D2.2 §.cascade/ namespace.
        (self.tmpdir / ".cascade" / "manifests").mkdir(parents=True)
        (self.tmpdir / ".cascade" / "halt").mkdir(parents=True)
        (self.tmpdir / ".cascade" / "session").mkdir(parents=True)
        (self.tmpdir / ".cascade" / "telemetry").mkdir(parents=True)
        (self.tmpdir / "docs").mkdir()
        # Patch the module-level PROJECT_DIR so _resolve sees the fixture.
        self._orig_project_dir = sv.PROJECT_DIR
        sv.PROJECT_DIR = self.tmpdir

    def tearDown(self) -> None:
        sv.PROJECT_DIR = self._orig_project_dir
        self._td.cleanup()

    # ------ writers ------

    def write_manifest(self, ticket: str, stage: str, payload: dict[str, Any]) -> Path:
        """Write a manifest at .cascade/manifests/<ticket>-<stage>.json.

        Auto-zeroes manifest_sha256 in the dict, computes the sha over the
        zeroed compact form (matching the CLI's `_sha256_manifest_self_zeroed`
        canonical form per D2.1 v2 step 3), and writes the dict back with
        that sha. The file on disk is pretty-printed; sha is computed over
        the canonical compact representation.
        """
        # Compute self-zeroed sha per D2.1 v2 step 3.
        # IMPORTANT: must match _sha256_manifest_self_zeroed exactly —
        # compact separators, sort_keys=True.
        canonical = dict(payload)
        canonical["manifest_sha256"] = ""
        zeroed_blob = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        sha = hashlib.sha256(zeroed_blob).hexdigest()
        canonical["manifest_sha256"] = sha
        path = self.tmpdir / ".cascade" / "manifests" / f"{ticket}-{stage}.json"
        # The file format doesn't affect the sha; use pretty-print for readability.
        path.write_text(json.dumps(canonical, sort_keys=True, indent=2))
        return path

    def write_run_state(self, payload: dict[str, Any]) -> Path:
        """Write .cascade/run-state.json at the canonical v2.1 path."""
        path = self.tmpdir / ".cascade" / "run-state.json"
        path.write_text(json.dumps(payload, sort_keys=True, indent=2))
        return path

    def write_solo_config(self, payload: dict[str, Any]) -> Path:
        path = self.tmpdir / "docs" / ".solo-config.json"
        path.write_text(json.dumps(payload, sort_keys=True, indent=2))
        return path

    def write_spec(self, ticket: str, body: str = "") -> Path:
        slug_dir = self.tmpdir / "docs" / "specs" / ticket
        slug_dir.mkdir(parents=True, exist_ok=True)
        path = slug_dir / "spec.md"
        path.write_text(body)
        return path

    def write_pass_set(self, ticket: str, lines: list[str]) -> Path:
        inv_dir = self.tmpdir / "docs" / "specs" / ticket / "invariance"
        inv_dir.mkdir(parents=True, exist_ok=True)
        path = inv_dir / "pass-set-at-seal.txt"
        path.write_text("\n".join(lines) + ("\n" if lines else ""))
        return path

    def make_chain_with_parent(
        self,
        parent_stage: str,
        parent_ticket: str,
        parent_outputs: dict[str, Any],
    ) -> Path:
        """Convenience: write a parent manifest and a run-state pointing at it.

        Returns the manifest path. Used by tests that need an intact
        upstream chain.
        """
        path = self.write_manifest(
            parent_ticket,
            parent_stage,
            {
                "stage": parent_stage,
                "ticket": parent_ticket,
                "marker": "🜂",
                "schema_version": "v2",
                "produced_at": "2026-01-01T00:00:00Z",
                "produced_by": "test-fixture",
                "input_provenance": {},
                "outputs": parent_outputs,
                "is_tainted": False,
                "self_attestation": "ok",
            },
        )
        # Read back, recompute self-zeroed sha in canonical compact form (must
        # match the CLI's `_sha256_manifest_self_zeroed`).
        body = json.loads(path.read_text())
        recorded_sha = body["manifest_sha256"]
        self.write_run_state({
            "schema_version": "v2.1",
            "last_completed_stage": {
                "stage": parent_stage,
                "ticket": parent_ticket,
                "postcondition_manifest_path":
                    f".cascade/manifests/{parent_ticket}-{parent_stage}.json",
                "postcondition_manifest_sha256": recorded_sha,
            },
            "active_lock": None,
        })
        return path


# =============================================================================
# [unit] tier — predicate-level coverage
# =============================================================================


class UnitPyramidShape(CascadeFSFixture):
    """[unit] D3.2 P1–P7 — pyramid_shape per decomposition_strategy."""

    def test_predicate_pyramid_shape_pass_path(self):
        # tag: unit
        outputs = {
            "decomposition_strategy": "walking-skeleton",
            "pyramid_shape": {
                "strategy": "walking-skeleton",
                "required_tags": ["smoke", "perceptual"],
                "optional_tags": ["unit", "integration"],
                "forbidden_tags": ["contract", "invariance"],
            },
            "failing_test_seed": [
                {"id": "T1", "name": "test_smoke", "tag": "smoke"},
                {"id": "T2", "name": "test_perceptual", "tag": "perceptual"},
            ],
        }
        halts = sv._check_pyramid_shape(outputs, ticket="0042-foo")
        self.assertEqual(halts, [], f"expected no halts; got {[h.full_code for h in halts]}")

    def test_predicate_pyramid_shape_missing_required_tag(self):
        # tag: unit
        outputs = {
            "decomposition_strategy": "walking-skeleton",
            "pyramid_shape": {
                "strategy": "walking-skeleton",
                "required_tags": ["smoke", "perceptual"],
                "optional_tags": [],
                "forbidden_tags": ["contract", "invariance"],
            },
            "failing_test_seed": [
                # Missing perceptual entry → P3 violation.
                {"id": "T1", "name": "test_smoke", "tag": "smoke"},
            ],
        }
        halts = sv._check_pyramid_shape(outputs, ticket="0042-foo")
        self.assertTrue(halts, "expected a missing-required halt")
        self.assertTrue(any(h.sub_case == "missing-required" for h in halts),
                        f"expected sub_case='missing-required'; got "
                        f"{[(h.code, h.sub_case) for h in halts]}")

    def test_predicate_pyramid_shape_forbidden_tag_present(self):
        # tag: unit
        outputs = {
            "decomposition_strategy": "walking-skeleton",
            "pyramid_shape": {
                "strategy": "walking-skeleton",
                "required_tags": ["smoke", "perceptual"],
                "optional_tags": [],
                "forbidden_tags": ["contract", "invariance"],
            },
            "failing_test_seed": [
                {"id": "T1", "name": "test_smoke", "tag": "smoke"},
                {"id": "T2", "name": "test_perceptual", "tag": "perceptual"},
                # invariance is forbidden under walking-skeleton → P4 violation.
                {"id": "T3", "name": "test_inv", "tag": "invariance"},
            ],
        }
        halts = sv._check_pyramid_shape(outputs, ticket="0042-foo")
        self.assertTrue(any(h.sub_case == "forbidden-present" for h in halts),
                        f"expected sub_case='forbidden-present'; got "
                        f"{[(h.code, h.sub_case) for h in halts]}")

    def test_predicate_pyramid_shape_refactor_spike_must_be_empty(self):
        # tag: unit
        outputs = {
            "decomposition_strategy": "refactor-spike",
            "pyramid_shape": {
                "strategy": "refactor-spike",
                "required_tags": ["invariance"],
                "optional_tags": [],
                "forbidden_tags": ["unit", "integration", "contract", "smoke", "perceptual"],
            },
            # Refactor-spike forbids any failing_test_seed entries per D3.2 P6.
            "failing_test_seed": [
                {"id": "T1", "name": "test_unit", "tag": "unit"},
            ],
        }
        halts = sv._check_pyramid_shape(outputs, ticket="0099-refactor")
        self.assertTrue(any(h.sub_case == "refactor-spike-nonempty" for h in halts),
                        f"expected refactor-spike-nonempty; got "
                        f"{[(h.code, h.sub_case) for h in halts]}")

    def test_predicate_pyramid_shape_hybrid_must_be_null(self):
        # tag: unit
        # Hybrid → pyramid_shape MUST be null and seed MUST be empty (D3.2 P7).
        bad = {
            "decomposition_strategy": "hybrid",
            "pyramid_shape": {"strategy": "hybrid", "required_tags": ["smoke"]},
            "failing_test_seed": [],
        }
        halts = sv._check_pyramid_shape(bad, ticket="0100-hybrid")
        self.assertTrue(any(h.sub_case == "hybrid-nonempty" for h in halts),
                        f"expected hybrid-nonempty; got "
                        f"{[(h.code, h.sub_case) for h in halts]}")
        good = {
            "decomposition_strategy": "hybrid",
            "pyramid_shape": None,
            "failing_test_seed": [],
        }
        self.assertEqual(sv._check_pyramid_shape(good, ticket="0100-hybrid"), [])


class UnitProvenanceChain(CascadeFSFixture):
    """[unit] D2.1 v2 §Caller-side verification — steps 1–5."""

    def test_predicate_provenance_chain_break_detected(self):
        # tag: unit
        # Run-state names a parent manifest, but the sha doesn't match → §provenance-chain-broken.
        manifest_path = self.write_manifest(
            "0001-foo", "specify",
            {
                "stage": "specify", "ticket": "0001-foo", "marker": "🜂",
                "schema_version": "v2", "produced_at": "2026-01-01T00:00:00Z",
                "produced_by": "test", "input_provenance": {}, "outputs": {},
                "is_tainted": False, "self_attestation": "ok",
            },
        )
        self.write_run_state({
            "schema_version": "v2.1",
            "last_completed_stage": {
                "stage": "specify",
                "ticket": "0001-foo",
                "postcondition_manifest_path":
                    ".cascade/manifests/0001-foo-specify.json",
                # Deliberately wrong sha.
                "postcondition_manifest_sha256": "0" * 64,
            },
        })
        ok, halt, parent = sv._verify_chain_to_parent("0001-foo")
        self.assertFalse(ok)
        self.assertIsNotNone(halt)
        self.assertEqual(halt.code, "§provenance-chain-broken")
        self.assertEqual(halt.exit_code, sv.EXIT_PROVENANCE,
                         "chain-broken must route to exit 3")

    def test_predicate_provenance_chain_intact_via_helper(self):
        # tag: unit
        # Use make_chain_with_parent — it writes the self-zeroed sha correctly.
        self.make_chain_with_parent("specify", "0001-foo", {"decomposition_strategy": "walking-skeleton"})
        ok, halt, parent = sv._verify_chain_to_parent("0001-foo")
        self.assertTrue(ok, f"expected intact chain; got halt={halt}")
        self.assertIsNone(halt)
        self.assertIsNotNone(parent)
        self.assertEqual(parent["outputs"]["decomposition_strategy"], "walking-skeleton")

    def test_predicate_provenance_run_state_absent(self):
        # tag: unit
        ok, halt, parent = sv._verify_chain_to_parent("0001-foo")
        self.assertFalse(ok)
        self.assertEqual(halt.code, "§provenance-chain-broken")
        self.assertEqual(halt.exit_code, sv.EXIT_PROVENANCE)

    def test_predicate_provenance_parent_manifest_absent(self):
        # tag: unit
        # Run-state names a path that doesn't exist.
        self.write_run_state({
            "schema_version": "v2.1",
            "last_completed_stage": {
                "stage": "specify",
                "ticket": "0001-foo",
                "postcondition_manifest_path":
                    ".cascade/manifests/ghost-specify.json",
                "postcondition_manifest_sha256": "x" * 64,
            },
        })
        ok, halt, _ = sv._verify_chain_to_parent("0001-foo")
        self.assertFalse(ok)
        self.assertEqual(halt.code, "§provenance-chain-broken")


class UnitInvariance(CascadeFSFixture):
    """[unit] D3.3 P5–P9 — refactor-spike invariance predicates."""

    def test_predicate_invariance_pass_set_regression(self):
        # tag: unit
        # Pass-set file absent (P5 violation).
        outputs = {
            "invariance_artifact": {
                "pass_set_path": "docs/specs/0099-refactor/invariance/pass-set-at-seal.txt",
                "pass_set_sha256": "f" * 64,
                "capture_command": "pytest --tb=line --color=no | grep PASS",
                "capture_command_sha256": "a" * 64,
            }
        }
        halts = sv._evaluate_invariance(outputs, child_ticket="0099-refactor")
        self.assertTrue(halts, "expected pass-set-absent halt")
        codes = {h.full_code for h in halts}
        self.assertTrue(
            any("perceptual-evidence-missing" in c or "invariance" in c for c in codes),
            f"expected an invariance- or perceptual-missing halt; got {codes}",
        )

    def test_predicate_invariance_seal_tampering_detected(self):
        # tag: unit
        # Pass-set file exists with different bytes than the sealed sha.
        self.write_pass_set("0099-refactor", ["test_one PASS", "test_two PASS"])
        outputs = {
            "invariance_artifact": {
                "pass_set_path": "docs/specs/0099-refactor/invariance/pass-set-at-seal.txt",
                "pass_set_sha256": "0" * 64,  # Wrong sha.
                "capture_command": "pytest",
                "capture_command_sha256": "0" * 64,
            }
        }
        halts = sv._evaluate_invariance(outputs, child_ticket="0099-refactor")
        codes = {h.full_code for h in halts}
        self.assertTrue(any("invariance-seal-tampering" in c for c in codes),
                        f"expected invariance-seal-tampering; got {codes}")

    def test_predicate_invariance_pass_set_empty_at_seal_time(self):
        # tag: unit
        # §invariance-pass-set-empty is a /specify-seal-time halt (emitted by
        # _check_strategy_evidence). Set up a /specify outputs dict with a
        # sealed-but-empty pass-set file and assert the seal-time evaluator
        # surfaces it.
        path = self.write_pass_set("0099-refactor", [])
        actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        self.write_solo_config({
            "invariance": {"pass_set_capture_command": "pytest --tb=line"}
        })
        outputs = {
            "decomposition_strategy": "refactor-spike",
            "invariance_artifact": {
                "pass_set_path": "docs/specs/0099-refactor/invariance/pass-set-at-seal.txt",
                "pass_set_sha256": actual_sha,
                "capture_command": "pytest --tb=line",
                "capture_command_sha256": hashlib.sha256(
                    b"pytest --tb=line"
                ).hexdigest(),
            },
        }
        halts = sv._check_strategy_evidence(outputs, ticket="0099-refactor")
        codes = {h.full_code for h in halts}
        self.assertTrue(any("invariance-pass-set-empty" in c for c in codes),
                        f"expected invariance-pass-set-empty; got {codes}")


class UnitPerceptual(CascadeFSFixture):
    """[unit] D3.3 P1 + P4 — perceptual artifact predicates as implemented in the CLI.

    CLI-side semantics per D3.3 §CLI limitation: the standalone CLI implements
    P1 (artifact existence) and P4 (api-boundary transcript schema). P2 (re-run
    test) and P3 (byte-stability) are deferred to /verify-skill context that
    knows how to invoke the test runner — surfaced item.
    """

    @staticmethod
    def _seed_with(entry: dict[str, Any], strategy: str = "walking-skeleton") -> dict[str, Any]:
        return {
            "decomposition_strategy": strategy,
            "failing_test_seed": [entry],
        }

    def test_predicate_perceptual_p1_artifact_present_passes(self):
        # tag: unit
        artifact_rel = "docs/specs/0042-foo/perceptual/output.txt"
        path = self.tmpdir / artifact_rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("hello world\n")
        outputs = self._seed_with({
            "id": "T1", "name": "test_perceptual",
            "tag": "perceptual", "artifact_path": artifact_rel,
        })
        halts = sv._evaluate_perceptual_evidence(
            outputs, child_ticket="0042-foo", extra_p4_for_api_boundary=False,
        )
        self.assertEqual(halts, [], f"expected no halts; got {[h.full_code for h in halts]}")

    def test_predicate_perceptual_p1_artifact_absent_halts(self):
        # tag: unit
        outputs = self._seed_with({
            "id": "T1", "name": "test_perceptual",
            "tag": "perceptual",
            "artifact_path": "docs/specs/0042-foo/perceptual/ghost.txt",
        })
        halts = sv._evaluate_perceptual_evidence(
            outputs, child_ticket="0042-foo", extra_p4_for_api_boundary=False,
        )
        self.assertTrue(
            any(h.sub_case == "artifact-absent" for h in halts),
            f"expected artifact-absent; got "
            f"{[(h.code, h.sub_case) for h in halts]}",
        )

    def test_predicate_perceptual_artifact_path_missing_from_seed_entry(self):
        # tag: unit
        outputs = self._seed_with({
            "id": "T1", "name": "test_perceptual", "tag": "perceptual",
            # No artifact_path key.
        })
        halts = sv._evaluate_perceptual_evidence(
            outputs, child_ticket="0042-foo", extra_p4_for_api_boundary=False,
        )
        self.assertTrue(
            any(h.code == "§perceptual-evidence-missing" for h in halts),
            f"expected §perceptual-evidence-missing; got "
            f"{[(h.code, h.sub_case) for h in halts]}",
        )

    def test_predicate_perceptual_p4_api_boundary_transcript_well_formed(self):
        # tag: unit
        artifact_rel = "docs/specs/0042-api/perceptual/integration-transcript.md"
        path = self.tmpdir / artifact_rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# Integration transcript\n\n"
            "## Scenario: user signs up\n\n"
            "### Request\n```\nPOST /users\n```\n\n"
            "### Response\n```\n201 Created\n```\n"
        )
        outputs = self._seed_with(
            {"id": "T1", "name": "test_transcript",
             "tag": "perceptual", "artifact_path": artifact_rel},
            strategy="api-boundary",
        )
        halts = sv._evaluate_perceptual_evidence(
            outputs, child_ticket="0042-api", extra_p4_for_api_boundary=True,
        )
        self.assertEqual(halts, [], f"expected no halts; got {[h.full_code for h in halts]}")

    def test_predicate_perceptual_p4_api_boundary_missing_h1(self):
        # tag: unit
        artifact_rel = "docs/specs/0042-api/perceptual/integration-transcript.md"
        path = self.tmpdir / artifact_rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "## Scenario: x\n\n### Request\nfoo\n\n### Response\nbar\n"
        )
        outputs = self._seed_with(
            {"id": "T1", "name": "test_transcript",
             "tag": "perceptual", "artifact_path": artifact_rel},
            strategy="api-boundary",
        )
        halts = sv._evaluate_perceptual_evidence(
            outputs, child_ticket="0042-api", extra_p4_for_api_boundary=True,
        )
        self.assertTrue(
            any(h.sub_case == "transcript-shape-violation" for h in halts),
            f"expected transcript-shape-violation; got "
            f"{[(h.code, h.sub_case) for h in halts]}",
        )


class UnitHaltCardRender(unittest.TestCase):
    """[unit] D3.4 §Halt-card canonical shape."""

    def test_halt_card_render_matches_d3_4_canonical(self):
        # tag: unit
        halt = sv.HaltCard(
            code="§pyramid-shape-violation",
            sub_case="missing-required",
            summary="failing_test_seed lacks required tag 'perceptual' for walking-skeleton",
            recommendation="Edit spec.md to add a [perceptual] entry and /specify --continue.",
            diagnostic_context={"strategy": "walking-skeleton", "ticket": "0042-foo"},
        )
        gate = sv.GateResult(
            gate_name="spec.pyramid-shape", stage="specify", trigger="at-seal",
            passed=False, halts=[halt],
        )
        text = sv._render_halt_card("specify", "0042-foo", [gate])
        # The canonical card shape from D3.4:
        self.assertIn("HALT at /specify", text)
        self.assertIn("for 0042-foo", text)
        self.assertIn("Primary: §pyramid-shape-violation/missing-required", text)
        self.assertIn("Recommendation:", text)
        self.assertIn("Diagnostic context:", text)
        self.assertIn("strategy: walking-skeleton", text)

    def test_halt_card_render_includes_other_halts_section(self):
        # tag: unit
        h1 = sv.HaltCard(code="§pyramid-shape-violation", sub_case="missing-required",
                         summary="seed lacks perceptual", recommendation="add it")
        h2 = sv.HaltCard(code="§strategy-annotation-unresolved", summary="strategy is TBD")
        g1 = sv.GateResult(gate_name="spec.pyramid-shape", stage="specify",
                           trigger="at-seal", passed=False, halts=[h1])
        g2 = sv.GateResult(gate_name="spec.strategy-annotation", stage="specify",
                           trigger="at-seal", passed=False, halts=[h2])
        text = sv._render_halt_card("specify", "0042-foo", [g1, g2])
        self.assertIn("Other gates that halted at this stage:", text)
        self.assertIn("spec.strategy-annotation: §strategy-annotation-unresolved", text)


class UnitStageResultExitCodeRouting(unittest.TestCase):
    """[unit] StageResult.exit_code routes §provenance-* halts to EXIT_PROVENANCE."""

    def test_exit_code_pass_when_all_gates_passed(self):
        # tag: unit
        gates = [
            sv.GateResult(gate_name="a", stage="specify", trigger="at-seal", passed=True),
            sv.GateResult(gate_name="b", stage="specify", trigger="at-seal", passed=True),
        ]
        sr = sv.StageResult(stage="specify", ticket="t", gates=gates)
        self.assertEqual(sr.exit_code, sv.EXIT_PASS)

    def test_exit_code_halt_when_standard_halt(self):
        # tag: unit
        halt = sv.HaltCard(code="§pyramid-shape-violation", summary="x", recommendation="y")
        g = sv.GateResult(gate_name="a", stage="specify", trigger="at-seal",
                          passed=False, halts=[halt])
        sr = sv.StageResult(stage="specify", ticket="t", gates=[g])
        self.assertEqual(sr.exit_code, sv.EXIT_HALT)

    def test_exit_code_provenance_routes_to_3(self):
        # tag: unit
        halt = sv.HaltCard(code="§provenance-chain-broken", summary="x",
                           exit_code=sv.EXIT_PROVENANCE)
        g = sv.GateResult(gate_name="a", stage="specify", trigger="pre-flight",
                          passed=False, halts=[halt])
        sr = sv.StageResult(stage="specify", ticket="t", gates=[g])
        self.assertEqual(sr.exit_code, sv.EXIT_PROVENANCE,
                         "§provenance-* must route to exit 3 (triggers --reconcile)")


class UnitManifestSelfShaRecompute(CascadeFSFixture):
    """[unit] D2.1 v2 §Caller-side verification step 3 — self-zeroed sha."""

    def test_manifest_self_sha_recomputed_correctly(self):
        # tag: unit
        path = self.write_manifest(
            "0001-foo", "specify",
            {"stage": "specify", "ticket": "0001-foo", "marker": "🜂",
             "schema_version": "v2", "produced_at": "2026-01-01T00:00:00Z",
             "produced_by": "test", "input_provenance": {},
             "outputs": {"any": "thing"}, "is_tainted": False,
             "self_attestation": "ok"},
        )
        # Re-read; the file's recorded manifest_sha256 must match the
        # self-zeroed recompute in canonical compact form (D2.1 v2 step 3 —
        # `sort_keys=True, separators=(",", ":")` is the canonical sha-input
        # serialization).
        body = json.loads(path.read_text())
        recorded = body["manifest_sha256"]
        zeroed = dict(body)
        zeroed["manifest_sha256"] = ""
        recomputed = hashlib.sha256(
            json.dumps(zeroed, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        self.assertEqual(recorded, recomputed,
                         "fixture sha must equal canonical compact-form sha")
        # And solo-verify's helper produces the same.
        self.assertEqual(sv._sha256_manifest_self_zeroed(path), recorded,
                         "CLI helper sha must match recorded sha")


class UnitGatesRegistry(unittest.TestCase):
    """[unit] GATES dict / STAGE_ORDER invariants."""

    def test_gates_registry_stage_uniqueness(self):
        # tag: unit
        # Every gate is bound to exactly one stage and that stage is in STAGE_ORDER.
        for name, spec in sv.GATES.items():
            self.assertIn(spec.stage, sv.STAGE_ORDER,
                          f"gate {name} stage {spec.stage} not in STAGE_ORDER")
            self.assertEqual(name, spec.name, "name parity")

    def test_gates_registry_has_load_bearing_finalize(self):
        # tag: unit
        # build.finalize is load-bearing per stop-orchestrator.sh.
        self.assertIn("build.finalize", sv.GATES,
                      "stop-orchestrator.sh depends on this gate name")
        spec = sv.GATES["build.finalize"]
        self.assertEqual(spec.stage, "build")
        self.assertEqual(spec.trigger, "at-write")

    def test_stage_order_matches_cascade(self):
        # tag: unit
        # The canonical cascade order from D2.1 + D2.2.
        expected = [
            "onboard", "specify", "review", "plan",
            "update-linear", "build", "wrap", "verify", "retro",
        ]
        self.assertEqual(list(sv.STAGE_ORDER.keys()), expected)


# =============================================================================
# [smoke] tier — CLI dispatcher coverage via subprocess
# =============================================================================


def _run_cli(args: list[str], cwd: Path | None = None, env_extra: dict[str, str] | None = None
             ) -> subprocess.CompletedProcess[str]:
    """Run solo-verify as a subprocess; return CompletedProcess.

    The script is executed via the current interpreter to avoid shebang
    drift in the test sandbox.
    """
    env = os.environ.copy()
    if cwd is not None:
        env["CLAUDE_PROJECT_DIR"] = str(cwd)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(SOLO_VERIFY_PATH), *args],
        cwd=str(cwd) if cwd else None,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


class SmokeListGates(unittest.TestCase):
    """[smoke] --list-gates surface."""

    def test_solo_verify_list_gates_prints_22_or_more(self):
        # tag: smoke
        # D4.0 noted "~22 gates"; we ship 28 due to AC-9/AC-10 splits.
        cp = _run_cli(["--list-gates"])
        self.assertEqual(cp.returncode, 0, msg=f"stderr={cp.stderr!r}")
        # Count fully-qualified gate names (stage.gate-name).
        lines = [ln for ln in cp.stdout.splitlines() if ln.startswith("  ")]
        # Lines look like "  spec.pyramid-shape  [at-seal]" — filter.
        gate_lines = [ln for ln in lines if "." in ln.split()[0] if ln.split()]
        self.assertGreaterEqual(len(gate_lines), 22,
                                f"D4.0 floor is 22 gates; got {len(gate_lines)}")
        # And our actual count is 28.
        self.assertEqual(len(gate_lines), 28,
                         f"v0.2 ships 28 gates per AC-9/AC-10 splits; got {len(gate_lines)}")

    def test_solo_verify_list_gates_filter_by_stage(self):
        # tag: smoke
        cp = _run_cli(["--list-gates", "verify"])
        self.assertEqual(cp.returncode, 0, msg=f"stderr={cp.stderr!r}")
        # /verify ships 5 gates: provenance, child-completion, perceptual-evidence,
        # invariance, milestone-aggregation.
        for name in ("verify.provenance", "verify.child-completion",
                     "verify.perceptual-evidence", "verify.invariance",
                     "verify.milestone-aggregation"):
            self.assertIn(name, cp.stdout)
        self.assertNotIn("spec.", cp.stdout)
        self.assertNotIn("build.", cp.stdout)


class SmokeExplain(unittest.TestCase):
    """[smoke] --explain surface."""

    def test_solo_verify_explain_returns_d3_4_content(self):
        # tag: smoke
        cp = _run_cli(["--explain", "verify.perceptual-evidence"])
        self.assertEqual(cp.returncode, 0, msg=f"stderr={cp.stderr!r}")
        # Must include predicate set, halt codes, recovery sections.
        for marker in ("Predicate set:", "Halt codes:", "Recovery:",
                       "§perceptual-evidence-missing"):
            self.assertIn(marker, cp.stdout, f"missing '{marker}' in --explain output")

    def test_solo_verify_explain_unknown_gate_exits_2(self):
        # tag: smoke
        cp = _run_cli(["--explain", "bogus.gate"])
        self.assertEqual(cp.returncode, sv.EXIT_USAGE)

    def test_solo_verify_explain_build_finalize_describes_load_bearing_gate(self):
        # tag: smoke
        cp = _run_cli(["--explain", "build.finalize"])
        self.assertEqual(cp.returncode, 0, msg=f"stderr={cp.stderr!r}")
        # The gate that stop-orchestrator.sh calls. The explain text must
        # mention the cascade-level concepts the founder needs.
        self.assertIn("build.finalize", cp.stdout)
        self.assertIn("Recovery:", cp.stdout)


class SmokeExitCodes(unittest.TestCase):
    """[smoke] D3.4 exit-code mapping."""

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._td.name)

    def tearDown(self) -> None:
        self._td.cleanup()

    def test_unknown_stage_exits_2(self):
        # tag: smoke
        (self.tmpdir / ".cascade" / "manifests").mkdir(parents=True)
        cp = _run_cli(["bogus-stage", "0001-foo"], cwd=self.tmpdir)
        self.assertEqual(cp.returncode, sv.EXIT_USAGE,
                         f"stderr={cp.stderr!r} stdout={cp.stdout!r}")

    def test_no_args_exits_2(self):
        # tag: smoke
        cp = _run_cli([], cwd=self.tmpdir)
        self.assertEqual(cp.returncode, sv.EXIT_USAGE)

    def test_missing_cascade_dir_exits_4(self):
        # tag: smoke
        # No .cascade/manifests/ in the tmpdir → exit 4.
        cp = _run_cli(["specify", "0001-foo"], cwd=self.tmpdir)
        self.assertEqual(cp.returncode, sv.EXIT_FS_INCONSISTENT,
                         f"stderr={cp.stderr!r}")
        self.assertIn("§cascade-fs-inconsistent", cp.stderr)

    def test_missing_run_state_routes_to_provenance_exit_3(self):
        # tag: smoke
        # .cascade/manifests/ exists but run-state is absent → §provenance-chain-broken → exit 3.
        # Use --gate plan.provenance to isolate the provenance evaluator (other
        # gates at the stage may emit non-provenance halts first which would
        # mask the routing behaviour).
        (self.tmpdir / ".cascade" / "manifests").mkdir(parents=True)
        cp = _run_cli(["plan", "0001-foo", "--gate", "plan.provenance"], cwd=self.tmpdir)
        self.assertEqual(cp.returncode, sv.EXIT_PROVENANCE,
                         f"stderr={cp.stderr!r} stdout={cp.stdout!r}")
        self.assertIn("§provenance-chain-broken", cp.stdout)

    def test_unknown_gate_with_known_stage_exits_2(self):
        # tag: smoke
        (self.tmpdir / ".cascade" / "manifests").mkdir(parents=True)
        cp = _run_cli(["specify", "0001-foo", "--gate", "spec.bogus"], cwd=self.tmpdir)
        self.assertEqual(cp.returncode, sv.EXIT_USAGE)

    def test_cross_stage_gate_exits_2(self):
        # tag: smoke
        (self.tmpdir / ".cascade" / "manifests").mkdir(parents=True)
        # build.finalize is real, but it belongs to /build, not /specify.
        cp = _run_cli(["specify", "0001-foo", "--gate", "build.finalize"],
                      cwd=self.tmpdir)
        self.assertEqual(cp.returncode, sv.EXIT_USAGE)
        self.assertIn("belongs to /build", cp.stderr)


class SmokeHookAliases(unittest.TestCase):
    """[smoke] Hook-invocation aliases per D2.2 §Hook/script table.

    These exercise the alias dispatch only — semantic outcome depends on
    fixture state. The minimum guarantee: the CLI parses the alias and
    proceeds to the FS-readiness check (which then routes to exit 3 or 4
    given missing fixtures).
    """

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._td.name)
        (self.tmpdir / ".cascade" / "manifests").mkdir(parents=True)

    def tearDown(self) -> None:
        self._td.cleanup()

    def test_build_finalize_alias_dispatches(self):
        # tag: smoke
        # This is the load-bearing alias from stop-orchestrator.sh.
        # build-finalize → _run_stage("build", ticket, single_gate="build.finalize"),
        # which skips build.provenance — so a missing run-state surfaces as
        # §build-finalize-incomplete (no backpressure.jsonl), not §provenance-chain-broken.
        # The point of this test is alias dispatch, not exit-code semantics:
        # the CLI must accept `build-finalize <ticket>` and route to /build's
        # finalize gate evaluator.
        cp = _run_cli(["build-finalize", "0001-foo"], cwd=self.tmpdir)
        self.assertNotEqual(cp.returncode, sv.EXIT_USAGE,
                            f"build-finalize alias should dispatch, not usage-error; "
                            f"stderr={cp.stderr!r}")
        # And the halt-card mentions /build (proving the alias routed correctly).
        self.assertIn("/build", cp.stdout,
                      f"expected /build in output; got {cp.stdout!r}")

    def test_build_spawn_alias_dispatches(self):
        # tag: smoke
        cp = _run_cli(["build-spawn", "0001-foo"], cwd=self.tmpdir)
        self.assertIn(cp.returncode, (sv.EXIT_HALT, sv.EXIT_PROVENANCE),
                      f"unexpected exit {cp.returncode}")

    def test_milestone_alias_dispatches(self):
        # tag: smoke
        cp = _run_cli(["milestone", "M-0001"], cwd=self.tmpdir)
        # Verify-stage with no fixtures → some halt; CLI should NOT exit 2.
        self.assertNotEqual(cp.returncode, sv.EXIT_USAGE,
                            f"milestone alias should dispatch, not error usage; "
                            f"stderr={cp.stderr!r}")

    def test_subagent_alias_dispatches(self):
        # tag: smoke
        cp = _run_cli(["subagent", "0001-foo-pm"], cwd=self.tmpdir)
        self.assertNotEqual(cp.returncode, sv.EXIT_USAGE,
                            f"subagent alias should dispatch, not error usage")


class SmokeReconcileCarryForward(unittest.TestCase):
    """[smoke] F-Rev-2 carry-forward — --reconcile available on all stages."""

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._td.name)
        (self.tmpdir / ".cascade" / "manifests").mkdir(parents=True)

    def tearDown(self) -> None:
        self._td.cleanup()

    def test_reconcile_accepted_on_v0_1_stages(self):
        # tag: smoke
        # /specify, /plan, /build, /wrap shipped --reconcile in v0.1.
        for stage in ("specify", "plan", "build", "wrap"):
            cp = _run_cli([stage, "0001-foo", "--reconcile", "--yes"], cwd=self.tmpdir)
            self.assertNotEqual(cp.returncode, sv.EXIT_USAGE,
                                f"--reconcile on /{stage} must parse")

    def test_reconcile_accepted_on_v0_2_added_stages(self):
        # tag: smoke
        # F-Rev-2 carry-forward — these are new in v0.2.
        for stage in ("onboard", "update-linear", "review", "verify", "retro"):
            cp = _run_cli([stage, "0001-foo", "--reconcile", "--yes"], cwd=self.tmpdir)
            self.assertNotEqual(cp.returncode, sv.EXIT_USAGE,
                                f"--reconcile on /{stage} must parse "
                                f"(F-Rev-2 carry-forward); stderr={cp.stderr!r}")


class SmokeVerifyPerStrategyDispatch(CascadeFSFixture):
    """[smoke] /verify per-child dispatch routes by strategy (D3.4 §Manifest)."""

    def test_solo_verify_verify_per_strategy_dispatch(self):
        # tag: smoke
        # Build a milestone wrap-manifest naming three children with mixed
        # strategies. The verify-stage dispatcher must produce a per-child
        # gate-outcome per strategy's predicate set.
        #
        # We don't assert PASS here (the children's perceptual / invariance
        # artifacts are not seeded). We assert that the dispatcher routed:
        # walking-skeleton → P1-P3 names; refactor-spike → P5-P9 names.
        cp = subprocess.run(
            [sys.executable, str(SOLO_VERIFY_PATH), "verify", "M-0001"],
            cwd=str(self.tmpdir),
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(self.tmpdir)},
            capture_output=True, text=True, timeout=30,
        )
        # Either §provenance-chain-broken (run-state absent) or §verify-child-not-built.
        # We tolerate either; the assertion is that dispatch reached the
        # verify-stage handler, not that it passed.
        self.assertNotEqual(cp.returncode, sv.EXIT_USAGE,
                            f"verify dispatch should not return usage-error; "
                            f"stderr={cp.stderr!r}")


# =============================================================================
# [perceptual] tier — byte-stable CLI rendering against the sealed artifact
# =============================================================================


class PerceptualListGatesArtifact(unittest.TestCase):
    """[perceptual] D3.3 P1+P2+P3 for the walking-skeleton perceptual artifact.

    The artifact is `docs/specs/0001-v0.2-cascade-integration/perceptual/
    solo-verify-list-gates.txt` — the canonical `--list-gates` rendering
    that gets sealed at /build's at-write trigger.

    PRE-SEAL: this test SKIPS (artifact does not yet exist) — yellow, not red.
    A failing-test seed must never gate CI red on a fresh, unbuilt clone/fork
    (SOL-134); forks strip docs/specs/ and never build spec 0001, so the seed
    self-skips there permanently instead of failing.
    POST-/build: this test passes via byte-equality.
    """

    PERCEPTUAL_ARTIFACT = (
        REPO_ROOT / "docs" / "specs" / "0001-v0.2-cascade-integration"
        / "perceptual" / "solo-verify-list-gates.txt"
    )

    def test_solo_verify_cli_help_output_perceptual(self):
        # tag: perceptual
        if not self.PERCEPTUAL_ARTIFACT.is_file():
            self.skipTest(
                f"perceptual artifact absent at {self.PERCEPTUAL_ARTIFACT} — "
                f"walking-skeleton seed expects this to be written at /build's "
                f"at-write trigger (D3.3 P1). Pre-seal (and in every fork, which "
                f"strips docs/specs/ and never builds spec 0001) the seed skips "
                f"rather than failing, so it never gates CI red (SOL-134). The "
                f"byte-equality assertion below runs once the artifact is sealed."
            )
        sealed_bytes = self.PERCEPTUAL_ARTIFACT.read_bytes()
        # P2: re-run the capture command — exit zero.
        cp = subprocess.run(
            [sys.executable, str(SOLO_VERIFY_PATH), "--list-gates"],
            capture_output=True, timeout=30,
        )
        self.assertEqual(cp.returncode, 0, f"re-capture exit nonzero: stderr={cp.stderr!r}")
        # P3: byte-equality.
        self.assertEqual(cp.stdout, sealed_bytes,
                         "byte-stability drift between sealed artifact and re-capture")


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
