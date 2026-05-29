# 0002 build — bootstrap exception (founder-authorized)

**Status:** Active exception, scoped to the 0002 child builds (SOL-103, SOL-104).
**Authorized by:** Ondra (founder), 2026-05-29, in the Code build session.
**Precedent:** SOL-17 §Pre-flight ("direct commit to main is allowed per CLAUDE.md only for this commit") — the same "allowed just this once, for the bootstrap" shape.

## Why an exception is needed

The 0002 children are gated by the v0.2 cascade machinery that 0001 introduced. But that machinery cannot yet enforce a chain for the very work that creates it — a genuine chicken-and-egg bootstrap. Three interlocking facts, verified on `main` at commit `0968471`:

1. **No provenance root exists, and none is recoverable.** `preflight-provenance.sh` / `tools/solo-verify` root the chain in `.cascade/run-state.json` → `last_completed_stage.postcondition_manifest_path` + `…_sha256` → a sealed upstream manifest. `.cascade/run-state.json` is absent and was never committed in any branch; no manifest JSON was ever committed (`.cascade/manifests/` has only `.gitkeep`). 0001 itself was built before its own hooks existed, so no authentic manifest was ever produced. Reconstructing one would mean inventing hashes — explicitly forbidden.

2. **The hook substrate is non-functional as committed.** Six of seven shell hooks (including `preflight-provenance.sh`) `source "$SCRIPT_DIR/_lib.sh"`, but `_lib.sh` does not exist — only `.claude/hooks/lib/common.sh` does. Under `set -u` these error on the source line. Only `pretool-write-denylist.sh` sources the correct path.

3. **`tools/solo-verify` needs Python 3.10+** (`match` statements); the environment `python3` is 3.9.6, so the CLI fails to parse. (Environment prerequisite, not a code bug.)

4. **Linear labels were off the `/build` state machine.** `scope-labels.md` requires parent `scope:planned` + child `scope:sealed`. Pre-exception state: SOL-102 `scope:specified`; SOL-103 / SOL-104 `scope:planned`.

## What the exception authorizes

For the 0002 child builds only:

- Build SOL-103 / SOL-104 **without** an enforced provenance chain (it cannot exist for this work). No manifest is fabricated; `.cascade/run-state.json` is not synthesized with invented hashes.
- Correct the Linear labels by hand to satisfy the `/build` precondition: SOL-102 → `scope:planned`; SOL-103, SOL-104 → `scope:sealed`. (Done in this session via Linear MCP.)
- Proceed with TDD discipline preserved: the failing-test seed is authored and run before/with the implementation.

## Explicitly NOT bypassed

- **No fabricated perceptual evidence.** SOL-103 AC-4 (`/onboard --dry-run` byte-stability) is **deferred**, not faked: `/onboard` has no `--dry-run` mode, so the artifact cannot be sealed. The seed's `test_onboard_dry_run_byte_stable` is SKIPPED with that reason. SOL-103 ships AC-1/AC-2/AC-3 complete; AC-4 remains open.
- **No fabricated manifests or hashes.**

## Follow-ups this exception leaves open (file as v0.2.x)

1. Fix the `_lib.sh` vs `.claude/hooks/lib/common.sh` hook-sourcing defect (6 hooks broken as committed).
2. Pin / document the Python 3.10+ requirement for `tools/solo-verify` (and the four-hat `.py` hook).
3. Establish a legitimate provenance root (e.g. via `/onboard` or `solo-cascade resume`) and seal the 0001 + 0002 manifests so the chain enforces going forward.
4. Build the `/onboard --dry-run` capability so SOL-103 AC-4's perceptual artifact can be sealed.
