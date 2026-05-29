# 0003 — Provenance-root seal audit (AC-4)

**Sealed by:** code-claude `/build SOL-117`, 2026-05-29 (direct seal; the framework
repo has no Ralph sandbox per `CLAUDE.md` §Tool constraints — `/build` is direct
implementation here, as for SOL-113/115/116/119).
**Approach:** seal a `/specify` chain-start root from the real merged 0001/0002
evidence (founder-confirmed). Not an `/onboard` manifest — the Linear team uses a
bespoke Active/Sync-Queue/Backlog/Decisions layout, so the six canonical `/onboard`
projects do not exist and `onboard.linear-projects` (≥6 real project IDs) cannot be
satisfied honestly. AC-1/2/3 do not require the onboard floor (AC-2's onboard clause
is an "or"); the `/specify` root needs no Linear writes.

This note is the AC-4 audit: for the one sealed manifest, it records the exact
`solo-verify` command, its exit code, the real merged artifact every `outputs`
entry maps to, the sha-compute command, and the determinism proof.

---

## Sealed manifest

`.cascade/manifests/SOL-102-specify.json` — the `/specify`-stage manifest for the
0002 epic (parent ticket SOL-102). `.cascade/run-state.json`'s
`last_completed_stage.postcondition_manifest_path` / `_sha256` point at it; this is
the non-null root the next cascade stage (`/review SOL-102`) chains to (resolves
four-hat objection E-1: the root is a non-null 0002 manifest, not the onboard floor).

### Executed verifier run (the seal confirmation)

```
$ CLAUDE_PROJECT_DIR="$(pwd)" python3.11 tools/solo-verify specify SOL-102
PASS at /specify for SOL-102 — gates evaluated: 5
exit 0
```

Per-gate (each `--gate <name>` run also exit 0):

| Gate | Trigger | Result | Why it passes against real evidence |
|---|---|---|---|
| `spec.provenance` | pre-flight | exit 0 | run-state chains to this manifest; recomputed self-zeroed sha == stored sha (non-vacuous, matches) |
| `spec.ac-coverage` | at-seal | exit 0 | skipped for `hybrid` parents (D3.2 / `_check_ac_coverage`) |
| `spec.pyramid-shape` | at-seal | exit 0 | `hybrid` → `pyramid_shape: null` AND `failing_test_seed: []` (P7) |
| `spec.strategy-evidence` | at-seal | exit 0 | `hybrid` is neither walking/api/capability nor refactor-spike → no evidence required |
| `spec.strategy-annotation` | at-seal | exit 0 | the forbidden step-1 annotation `proposed by /specify; founder to confirm` is absent from the 0002 spec's §Decomposition strategy (cleared at the 2026-05-20 step-5 confirm; see spec.md line 46) |

`solo-verify` **evaluates, does not seal** (no `--rerun`; `--reconcile` is
drift-detection-only in v0.2). The seal = this build wrote the manifest from real
evidence, then confirmed it with the exit-0 run above. The run did not halt, so
AC-5's halt-and-file path was not triggered.

### `outputs` provenance — every entry maps to real merged evidence

| `outputs` entry | Value | Real-evidence source |
|---|---|---|
| `spec_path` | `docs/specs/0002-v0.2-release-wrap-up/spec.md` | On disk; landed via PR #7 (`ce8187f`, SOL-103) / re-sealed PR #6 (`c7cc48e`, SOL-107) |
| `decomposition_strategy` | `hybrid` | spec.md line 5 / §Decomposition strategy (declared `hybrid`) |
| `pyramid_shape` | `null` | spec.md §Failing-test seed line 52 (`null` — hybrid) |
| `failing_test_seed` | `[]` | spec.md §Failing-test seed ("Tests at parent grain. None.") |
| `acceptance_criteria` | AC-1..AC-8 (verbatim bullet text) | spec.md §Acceptance criteria lines 28–35 (the 8 `- **AC-N.**` bullets) |
| `ac_list_sha256` | `34b089d9eb18367589f847e481cf853b6e6b94b6dc7c936bb7fe2135423e7383` | recomputed over the 8 AC bullets (see below); **matches the value documented in spec.md line 85** |
| `input_provenance.parent_manifest_path` | `null` | 0003 is the chain start under the final bootstrap exception — no upstream manifest |

Real merged evidence backing the 0002 epic: PR #5 (`93faf5d`, 0001 cascade
integration), PR #6 (`c7cc48e`, SOL-107 re-seal), PR #7 (`ce8187f`, SOL-103 docs
lockstep), PR #8 (`7b41625`, SOL-104 followup tickets). Four-hat doc
`1f4d1364-ad0d-4b89-b00a-01f581a561b0` (`unresolved_count = 0`).

### sha-compute commands

```
# ac_list_sha256 — solo-verify's _ac_list_sha256_from_spec algorithm over the
# §Acceptance criteria bullets, normalized "\n".join, sha256:
sha256( "\n".join(<8 AC bullet texts from 0002 spec.md>) )
  = 34b089d9eb18367589f847e481cf853b6e6b94b6dc7c936bb7fe2135423e7383

# manifest_sha256 — D2.1 v2.1 step-3 self-zeroed, unified serializer (SOL-119):
data["manifest_sha256"] = ""
sha256( json.dumps(data, sort_keys=True, separators=(",",":")) )  # ensure_ascii=True
  = d5651001d97172691b52dc86c72e2cb7205a6b8b583019648dcbd0e8cc396e0c
```

### Determinism proof (recompute-not-fabrication)

Re-hashing the sealed manifest's own content (with `manifest_sha256` zeroed) is
deterministic and reproduces the stored value — proving the sha is computed from
present evidence, not chosen to satisfy the verifier:

```
$ python3.11 -c 'import json,hashlib; d=json.load(open(".cascade/manifests/SOL-102-specify.json")); \
  d["manifest_sha256"]=""; \
  print(hashlib.sha256(json.dumps(d,sort_keys=True,separators=(",",":")).encode()).hexdigest())'
d5651001d97172691b52dc86c72e2cb7205a6b8b583019648dcbd0e8cc396e0c   # == stored
```

Both the python CLI (`tools/solo-verify _sha256_manifest_self_zeroed`) and the bash
hook (`.claude/hooks/lib/common.sh sha256_manifest_self_zeroed`, which delegates to
python3 post-SOL-119) recompute this identical value — verified by the
`tests/0003-provenance-root` (b) contract test and `tests/provenance-sha-parity`.

---

## AC-3 — preflight gate is now live

```
$ printf '%s' '{"prompt":"/review SOL-102"}' | CLAUDE_PROJECT_DIR="$(pwd)" \
    bash .claude/hooks/preflight-provenance.sh ; echo "exit $?"
exit 0     # empty stdout, empty stderr
```

The chain is intact: `preflight-provenance.sh` admits `/review SOL-102` against the
committed root. The gate is live, not waived.

---

## Note on `ac_list_sha256` (SOL-111)

The build brief anticipated that `solo-verify`'s bullet-only regex would yield the
empty-string hash `e3b0c442…` because the 0002 spec uses `**AC-N**` bold format.
That is **stale**: the current on-disk 0002 spec writes its ACs as `- **AC-N.**`
markdown bullets (lines 28–35), which the regex `^\s*[-*+]\s+(.+)$` *does* match, so
the recompute yields the 8-bullet hash `34b089d9…` — identical to the value
documented in spec.md line 85. No `/specify` gate checks `ac_list_sha256` (it gates
at `/review`/`/plan`/`/build` against the parent's stored value), so it is not
load-bearing for this seal; the recomputed-and-matching value is stored per SOL-111
(sealed ac_list values are documentary this cycle — not reproduced by hand, not
edited).
