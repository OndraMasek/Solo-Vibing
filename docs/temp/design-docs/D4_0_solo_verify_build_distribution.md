# D4.0 — solo-verify build and distribution

**Status:** Design (v1 — authored 2026-05-19).
**Phase:** 4 (Cleanup and concrete fixes).
**Resolves:** Carry-forward thread from D3.4 §solo-verify CLI surface ("Build/distribution lives in D4.x. D3.4 specifies the CLI surface; D4.x decides single-binary vs Python tree vs Bun. The decision cannot drift past Phase 4."); inventory finding from SOL-v2-D session (no committed Python runtime, no `pyproject.toml`, no `requirements.txt` in existing repo).
**Depends on:** D3.4 (CLI surface — commands, flags, exit codes), D2.2 (hook/script invocation table — when and how the cascade calls `solo-verify`).
**Position in Phase 4 plan:** first deliverable. D4.1 (template bug batch), D4.2 (skill splitting), and D4.5 (reconciliation primitives) can run in parallel after D4.0 lands.

## Decision

`solo-verify` ships as a **single-file Python script** at `tools/solo-verify`, written against the **Python 3.10+ standard library only**, with **no third-party dependencies**. Distribution is by copying the file into the consumer's repo at `/onboard` time; invocation is `python3 tools/solo-verify <stage> <ticket>` or `./tools/solo-verify <stage> <ticket>` after `chmod +x`.

Build is a no-op: there is no compilation, bundling, or packaging step for v0.2. CI verifies the script by running its unit-test suite on every push.

## Rationale (four pieces)

1. **Python** because the predicate logic involves JSON manifest parsing, sha256 verification, set-diff between pass-sets, and structured halt-card emission — none of which are pleasant in bash. The existing `scripts/` directory uses bash for trivial checks (`check_prereqs.sh`, `verify_linear_key.sh`); `solo-verify` is a heavier tool and uses a heavier language.

2. **Standard library only** because adding a dependency manager (`pip install`, `poetry`, `uv`) adds a step to every consumer onboarding and a maintenance surface for the framework. The predicate logic genuinely does not need anything beyond `json`, `hashlib`, `pathlib`, `argparse`, `dataclasses`, `subprocess`, `sys`. Discipline: if a future predicate seems to require a third-party library, push back and find a stdlib path first.

3. **Single file** because the consumer adoption surface is one copy operation. No `tools/solo-verify/` directory with `__init__.py` and submodules; one self-contained executable script. Estimated size at v0.2: ~800-1200 lines, demarcated by section comments. Manageable.

4. **3.10+** because `match` statements, structural pattern matching, and `ParamSpec` make the predicate dispatch and halt-card-shape code significantly cleaner. 3.10 was released October 2021 and is the default on Ubuntu 22.04 (April 2022) and macOS via Homebrew. The version floor is realistic in 2026.

## What it does (recap from D3.4)

The CLI surface from D3.4 §`solo-verify` CLI surface, in full:

```
solo-verify onboard <product>          # evaluates onboard.linear-projects + onboard.config-write
solo-verify specify <ticket>           # evaluates spec.* gates against the current spec file
solo-verify review <ticket>            # evaluates review.* gates
solo-verify plan <ticket>              # evaluates plan.* gates
solo-verify update-linear <ticket>     # evaluates update-linear.diff-applied
solo-verify build <ticket>             # evaluates build.* gates against the latest build state
solo-verify wrap <ticket>              # evaluates wrap.* gates
solo-verify verify <milestone>         # evaluates verify.* gates including per-child dispatch
solo-verify retro <milestone>          # evaluates retro.doc-sealed
```

Plus per-gate evaluation and documentation:

```
solo-verify <stage> <ticket> --gate <gate-name>     # single-gate
solo-verify --list-gates                            # all gates across all stages
solo-verify --list-gates <stage>                    # gates for one stage
solo-verify --explain <stage>.<gate-name>           # predicate text, halt codes, recovery
```

Plus the hook-invocation forms from D2.2's hook/script table:

```
solo-verify subagent <agent_id>             # SubagentStop on four-hat agents
solo-verify build-spawn <ticket>            # PostToolUse on Ralph spawn
solo-verify build-finalize <ticket>         # Stop on /build orchestrator
solo-verify milestone <id>                  # /verify post-completion
```

Five exit codes (D3.4):

| Code | Meaning |
|---|---|
| 0 | All gates evaluated, all passed. |
| 1 | One or more gates halted (standard halt). |
| 2 | Stage not found or gate name unknown; also: Python version too old; also: usage error. |
| 3 | Manifest chain broken (provenance halt). Triggers `--reconcile` routing per D2.1 v2. |
| 4 | Filesystem or Linear inconsistency that prevents evaluation (e.g., `.cascade/manifests/` missing entirely). |

D4.0 does not change any of the above. D4.0 specifies how that surface is implemented and delivered.

## Distribution options considered

| Option | Cost | Benefit | Choice for v0.2 |
|---|---|---|---|
| **A. Single-file Python script committed to framework repo, copied into consumer at `/onboard`** | Requires Python 3.10+ on consumer's machine. | Zero install. No build step. Easy to audit (one file). Easy to patch in flight (edit and re-run). | **Chosen.** |
| B. Single binary via PyInstaller / Nuitka / `shiv` | CI build matrix (macOS arm64, macOS x86_64, Linux x86_64, Linux arm64). Binary ~5–10 MB per platform. Consumer downloads correct binary at `/onboard`. | Removes Python prereq. Larger initial download per consumer. | Deferred to v0.3 if Python-prereq friction is real. |
| C. Bun / Deno script | Removes Python prereq, but adds Bun/Deno prereq. Rewrites the predicate code in TypeScript. | Single-binary distribution from a single source via `bun build --compile`. | Deferred. No v0.2 advantage over A; significant rewrite cost. |
| D. Rust / Go binary | Best runtime perf; no runtime prereq once binary is installed. | Cross-compilation pipeline, ~2–4 MB binary per platform. Major rewrite. | Deferred. v0.2 has no perf bottleneck that justifies the cost. |

Option A is the right v0.2 floor. Options B–D are revisited at v0.3 if and only if Python-prereq friction surfaces in adoption signals.

## Installation flow

`bootstrap.sh` (top-level framework installer, run once per consumer at adoption time) copies `tools/solo-verify` into the consumer's repo at `tools/solo-verify` and `chmod +x` it. `bootstrap.sh` also checks for Python 3.10+ availability and prints a clear warning if not found:

```
$ ./bootstrap.sh
Checking prerequisites...
  ✓ git
  ✓ python3 (3.11.4)
  ✓ Claude Code (1.x)
Copying framework files...
  ✓ .claude/skills/ (12 skills)
  ✓ .claude/rules/ (7 rules)
  ✓ .claude/commands/ (5 commands)
  ✓ .claude/hooks/ (TBD per D2.2)
  ✓ .claude/agents/ (8 agents)
  ✓ docs/templates/
  ✓ tools/solo-verify
Done. Run `claude` to begin and use `/onboard` to initialize this product.
```

The Python-version check inside `bootstrap.sh` is a separate concern from the runtime check inside `solo-verify` itself (see §Python version requirement below).

`solo-verify` invocation from the consumer:

```
python3 tools/solo-verify build SOL-42
```

or, after `chmod +x` (which `bootstrap.sh` performs):

```
./tools/solo-verify build SOL-42
```

The shebang line is `#!/usr/bin/env python3`. On macOS this resolves to whichever `python3` is on PATH (system at 3.9, Homebrew at 3.11+, or pyenv); on Linux to `/usr/bin/python3` typically. Both Ubuntu 22.04+ and macOS Sonoma+ ship a usable Python 3.10+ by default or via standard package manager.

## Python version requirement

Python 3.10+. The version is enforced at the top of `solo-verify`:

```python
#!/usr/bin/env python3
import sys
if sys.version_info < (3, 10):
    sys.exit(
        "solo-verify requires Python 3.10 or newer "
        "(found {}). Install Python 3.10+ from python.org or via your "
        "package manager.".format(".".join(map(str, sys.version_info[:3])))
    )
```

The exit code on version-too-old is 2 (per the §Exit codes table — "usage error"). This is intentional: a too-old Python is a setup error, not a cascade halt. The error message names the version found and points at remediation.

The hook-side (D2.2) `bootstrap.sh` version check is the early-warning. The script-side version check is defense-in-depth in case a consumer's environment changes after onboarding.

## Internal code structure

Single file, ~800–1200 lines, three layers separated by section comments:

```python
#!/usr/bin/env python3
"""solo-verify — gate evaluator for the Solo Claude Stack cascade.

Reads cascade manifests and evaluates gates per D3.4. No external dependencies.
"""

# ─────────────────────────────────────────────────────────
# §1 Imports + Python version gate
# §2 Constants (manifest paths, halt codes, exit codes)
# §3 Halt card data class + serializer
# §4 Manifest loader (with provenance-chain verification)
# §5 Predicate functions (one per gate, ~22 per D3.4)
# §6 Gate registry (dict: gate_name → predicate function)
# §7 Per-stage dispatch (including the per-child fan-out at /verify)
# §8 --explain content (inlined per D3.4; future: read gates.json)
# §9 main() + argparse
# ─────────────────────────────────────────────────────────
```

Layer 1: **Predicate functions.** Pure functions: take manifest dict(s) and return `PredicateResult(passed: bool, halt: Optional[HaltCard], evidence: dict)`. One function per gate name in D3.4 (≈22 gates). Easily unit-testable in isolation.

Layer 2: **Gate dispatch.** Given `(stage, gate_name, ticket)`, locates the right manifest file(s) under `.cascade/manifests/`, runs the appropriate predicate(s) in order (provenance check first per D3.4 §Per-stage gate inventories), aggregates results into a halt card if any predicate fails.

Layer 3: **CLI layer.** `argparse` with subcommand-per-stage. Routes `--gate`, `--list-gates`, `--explain` flags. Maps internal `PredicateResult` outcomes to the five exit codes from D3.4.

The choice to inline everything in one file rather than split into a package: at ~1000 lines, single-file is still readable, and copy-into-consumer becomes trivial (one `cp` instead of `cp -r tools/solo-verify/`). If the file grows past 2000 lines, revisit and split — but at that point the framework probably also wants a proper package, which is a v0.3 conversation.

## Testing strategy

The framework repo's own CI runs `solo-verify` against synthetic test fixtures. No live Linear, no live consumer repo, no live cascade — just manifest fixtures that exercise each predicate.

Fixture layout:

```
tests/
  fixtures/
    manifests/
      passing/                # manifest sets that should pass each gate
        spec-001.json
        review-001.json
        ...
      halting/                # per-gate halt cases
        spec.ac-list-sealed/
          manifest.json       # missing ac_list_sha256
          expected-halt.json  # the halt card we expect to be emitted
        build.test-output-present/
          manifest.json
          expected-halt.json
        ...
      chain-broken/           # provenance break cases
        case-1-missing-parent.json
        case-2-sha-mismatch.json
        ...
  test_solo_verify.py         # unittest runner
```

Test runner: Python standard library `unittest`, invoked as `python3 -m unittest discover tests/`. No pytest, no fixtures library, no third-party dependencies. Discipline: every halt code named in D3.4 has at least one fixture in `halting/` that exercises it.

Assertions per fixture:

- `passing/`: exit code 0, no halt cards emitted, stderr empty.
- `halting/<gate>/`: exit code 1, halt card emitted matches `expected-halt.json` shape (named halt code, named ticket, structured diagnostic context).
- `chain-broken/`: exit code 3, `§provenance-chain-broken` halt card.

CI workflow (GitHub Actions, conditional on D0.1 confirming GHA as the v0.2 CI provider):

```yaml
# .github/workflows/solo-verify-tests.yml
name: solo-verify tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: python3 -m unittest discover tests/
```

Matrix runs 6 combinations per push. Adds ~2 min to CI per push; acceptable for a v0.2 floor.

## Hook integration (recap from D2.2)

D2.2's hook/script table calls `solo-verify` from Claude Code hooks. The integration shape:

| Hook | When | Invocation |
|---|---|---|
| `UserPromptSubmit` matcher `/onboard` (pre-flight) | Before `/onboard` runs | `solo-verify onboard <product>` |
| `UserPromptSubmit` matcher `/specify` (post-completion) | After `/specify` completes | `solo-verify specify <ticket>` |
| `SubagentStop` matcher four-hat agents | After four-hat agent completes | `solo-verify subagent <agent_id>` |
| `UserPromptSubmit` matcher `/review` (post-completion) | After `/review` completes | `solo-verify review <ticket>` |
| `UserPromptSubmit` matcher `/plan` (post-completion) | After `/plan` completes | `solo-verify plan <ticket>` |
| `PreToolUse` matcher Linear write | Before `/update-linear` writes | `solo-verify update-linear <ticket>` |
| `PostToolUse` matcher Bash (Ralph spawn) | After `/build` spawns | `solo-verify build-spawn <ticket>` |
| `Stop` (single orchestrator) | After `/build` finalizes | `solo-verify build-finalize <ticket>` |
| `PreToolUse` matcher Linear write | Before `/wrap` writes | `solo-verify wrap <ticket>` |
| `UserPromptSubmit` matcher `/verify` (post-completion) | After `/verify` completes | `solo-verify milestone <id>` |
| `UserPromptSubmit` matcher `/retro` (post-completion) | After `/retro` completes | `solo-verify retro <id>` |

Each hook is a thin Python or bash wrapper at `.claude/hooks/<hook-name>.{py,sh}` that:

1. Receives Claude Code's hook JSON payload on stdin.
2. Extracts the relevant identifier (`ticket`, `agent_id`, `milestone_id`) from the payload.
3. Invokes `subprocess.run(["python3", "tools/solo-verify", <stage>, <ticket>], capture_output=True, text=True)`.
4. Maps `solo-verify`'s exit code to Claude Code's hook protocol:
   - 0 → hook returns success (cascade continues).
   - 1, 2, 3, 4 → hook returns blocking error (cascade halts; halt card from `solo-verify`'s stdout is surfaced to the founder).

D2.2 specifies the hook surface in detail; D4.0 only commits to `solo-verify` being shaped such that the hook integration is straightforward (clean exit codes, clean stdout for halt cards, no interactive prompts).

**Critical: the `max_turns` resilience case.** Per D2.2, hooks do not fire when a Claude Code session ends at `max_turns`. The cascade must invoke `solo-verify` explicitly as a recovery step in that case (e.g. on resume after auto-management). `solo-verify` being available as a plain CLI — not only as a hook callee — is what makes this work. D4.0 confirms this shape.

## What v0.2 does not ship

Explicitly deferred:

1. **Single-binary distribution** (PyInstaller / Nuitka / `shiv`). Considered above; deferred to v0.3 conditional on adoption signals.
2. **Bun / Deno port.** Considered; no v0.2 advantage.
3. **`gates.json` externalized catalog** for `--explain` content. v0.2 inlines the explanations in `solo-verify` itself; v0.2.x may move them to a versioned JSON file that both the cascade and `solo-verify --explain` read. Trade-off per D3.4 §Carry-forward: duplication-risk vs additional repo-template file. v0.2 accepts duplication; the inlined content is stable enough that drift in one minor version is unlikely.
4. **Telemetry on `children_gate_outcomes[]`** (the `solo-stats` query surface from D3.4 §Carry-forward).
5. **Versioned `pyramid_catalog_version`** for backward-compatible reading of older manifests. Manifest schema is frozen for v0.2; v0.2.x can introduce the version field if a schema change becomes necessary.
6. **`/plan --drop-child` operation** and **`--reconcile` formalization.** Both are referenced by `solo-verify`'s exit code 3 routing (per D2.1 v2 / D3.4) but are not implemented as `solo-verify` subcommands. D4.5 (reconciliation primitives) covers `--reconcile`; `--drop-child` is named in D3.4 §Carry-forward as D4.x.

All deferrals share a common rationale: the v0.2 floor (single-file Python script, no install step beyond Python presence, full predicate coverage of D3.4's 22 gates) is functional. Shipping advanced packaging or telemetry adds CI complexity without clear v0.2 user benefit.

## Files this introduces in the framework repo

New files:

- `tools/solo-verify` (single Python script, executable, ~1000 lines)
- `tests/fixtures/manifests/passing/*.json` (synthetic passing manifests, one per stage at minimum)
- `tests/fixtures/manifests/halting/<gate_name>/manifest.json` + `expected-halt.json` (one directory per gate in D3.4, ~22 directories)
- `tests/fixtures/manifests/chain-broken/*.json` (provenance break cases, ≥3 cases)
- `tests/test_solo_verify.py` (unittest-based test runner, ~200–400 lines)
- `.github/workflows/solo-verify-tests.yml` (CI workflow; conditional on D0.1 §Open items confirmation of GHA)

Updated files:

- `bootstrap.sh` (Python 3.10+ pre-check; copy `tools/solo-verify` into consumer's `tools/` directory; `chmod +x`)
- Framework repo `README.md` (adds "Python 3.10+ required for `solo-verify`" to prerequisites)
- `CLAUDE.md` template (notes that `solo-verify` is the gate-evaluation CLI; points at `solo-verify --list-gates` and `solo-verify --explain <gate>` for self-documentation)

## Open items

- **`bootstrap.sh` Python detection on Windows.** v0.2 assumes Unix-like environments (macOS + Linux). Windows users need WSL or a Python.org installer. Document in framework `README.md`; do not engineer for native Windows in v0.2.
- **GitHub Actions confirmed as the CI provider** (carried from D0.1 §Open items). The CI workflow file in this doc assumes GHA; revise if D0.1 settles on a different choice.
- **`pyenv` / `asdf` / `mise` interaction.** If a consumer has multiple Python versions managed by pyenv/asdf/mise, the `#!/usr/bin/env python3` shebang picks whichever is shimmed first. Documented; not engineered around.
- **Inlined `--explain` content size.** D3.4 has ~22 gates, each with ~5–15 lines of explanation. Inlined content totals ~200–400 lines. If this becomes unwieldy in the single-file structure, the v0.2.x `gates.json` externalization is the escape hatch.

## Cross-references

- **D3.4 §`solo-verify` CLI surface** — the contract this doc implements.
- **D2.2 §Hook/script table** — when and how the cascade calls `solo-verify`.
- **D2.1 v2 §Caller-side verification** — the provenance-chain verification logic that `solo-verify`'s §provenance gate implements; exit code 3 routes to `--reconcile` per this pattern.
- **D0.1 §What stays in the framework repo** — `tools/solo-verify` placement.
- **D0.1 §Open items** — GHA CI confirmation gates the `.github/workflows/solo-verify-tests.yml` decision.
- **D4.5 (planned)** — `--reconcile` primitive that consumers run after a `solo-verify` exit-3 halt.
