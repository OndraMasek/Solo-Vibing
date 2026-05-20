# `.claude/hooks/preflight-provenance.sh` — caller-side verification gate

**Status:** Patch-ready new file. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing`.

**Scope:** wraps the D2.1 v2 §Caller-side verification protocol's chain-integrity check as a `UserPromptSubmit` hook. Fires before every cascade-stage slash-command (`/review`, `/plan`, `/update-linear`, `/build`, `/wrap`, `/verify`, `/retro`). Validates that the upstream manifest exists, that its sha256 recomputes (with `manifest_sha256` field zeroed) to the value `cascade:run-state.last_completed_stage.postcondition_manifest_sha256` carries. On mismatch, halts the prompt with exit 2.

**v0.1 reconciliation:** none. v0.1 has no `.claude/hooks/` per `repo-state-summary.md` Part 2.

---

## Event choice rationale

Per D2.2 §Mapping table: pre-flight checks fire on `UserPromptSubmit` matched on the cascade slash-command. This is the cleanest event surface — it runs *before* the prompt reaches the model, so a chain-break halts immediately without spending any context on stage work.

**Output shape.** UserPromptSubmit uses **exit 2** to block, not the Stop/SubagentStop top-level-fields-only quirk. Per D2.2 §Hook events table: `UserPromptSubmit | Per turn | (none) | stdout adds to context. Exit 2 rejects the prompt.` So this script writes the diagnostic to stderr and exits 2 on failure; on success, exits 0 silently.

This is a divergence from `decomposition.md`'s "exits 2 on chain-broken with `{"decision":"block","reason":"…"}` to stdout per D2.2 §Stop / SubagentStop output schema quirk" — `decomposition.md` conflated two different output shapes. **Surfaced item.** The corrected shape is exit-2-with-stderr-diagnostic for UserPromptSubmit.

**Matcher.** UserPromptSubmit has no matchers per D2.2 §Hook events table. The script itself inspects the prompt content and acts only on cascade slash-commands.

---

## Script content

```bash
#!/usr/bin/env bash
# .claude/hooks/preflight-provenance.sh
#
# Caller-side chain-integrity check per D2.1 v2 §Caller-side verification.
# Fires on UserPromptSubmit; inspects the prompt for a cascade slash-command;
# validates the manifest chain to the prompt's expected upstream stage.
#
# Cascade slash-commands handled:
#   /review, /plan, /update-linear, /build, /wrap, /verify, /retro
# (Excluded: /specify, /onboard, /discovery, /constitution — these are entry
#  points or chain-starts without strict upstream manifest requirements.)
#
# Output: exit 2 with stderr diagnostic on chain-break; exit 0 silent on pass.
# UserPromptSubmit uses exit codes, not the Stop-hook JSON quirk.

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
. "$SCRIPT_DIR/_lib.sh"

trace "preflight-provenance: fired"

read_hook_payload

# Extract the user prompt from the payload. UserPromptSubmit's payload shape:
#   {"prompt": "...", "session_id": "...", ...}
prompt="$(jq_field '.prompt')"
if [ -z "$prompt" ]; then
  trace "preflight-provenance: no prompt; exiting clean"
  exit 0
fi

# Match cascade slash-commands. The prompt begins with the command at top of
# string (possibly preceded by whitespace) followed by a ticket/milestone arg.
stage=""
case "$prompt" in
  '/review '*|'/review')               stage="/review" ;;
  '/plan '*|'/plan')                   stage="/plan" ;;
  '/update-linear '*|'/update-linear') stage="/update-linear" ;;
  '/build '*|'/build')                 stage="/build" ;;
  '/wrap '*|'/wrap')                   stage="/wrap" ;;
  '/verify '*|'/verify')               stage="/verify" ;;
  '/retro '*|'/retro')                 stage="/retro" ;;
  *)                                   stage="" ;;
esac

if [ -z "$stage" ]; then
  trace "preflight-provenance: prompt is not a cascade stage command; exiting clean"
  exit 0
fi

trace "preflight-provenance: matched stage=$stage"

# Cascade-state read
if ! read_run_state; then
  echo "preflight-provenance: $stage invocation requires .cascade/run-state.json; " \
       "the file is absent or unreadable. Run /onboard first if this is a fresh repo, " \
       "or solo-cascade resume per D4.6 v1.1 if the file was lost." >&2
  exit 2
fi

# Expected upstream manifest path
expected_path="$(run_state_field '.last_completed_stage.postcondition_manifest_path')"
expected_sha="$(run_state_field '.last_completed_stage.postcondition_manifest_sha256')"

if [ -z "$expected_path" ] || [ "$expected_path" = "null" ]; then
  # No upstream stage. /onboard is the only stage where this is normal; the
  # other cascade stages require an upstream. Reject.
  echo "preflight-provenance: $stage requires an upstream stage manifest, but " \
       "cascade:run-state.last_completed_stage.postcondition_manifest_path is null. " \
       "The cascade may be at /onboard's terminal (no work in progress); " \
       "/specify is the typical entry point for a new feature." >&2
  exit 2
fi

abs_path="$CLAUDE_PROJECT_DIR/$expected_path"
if [ ! -f "$abs_path" ]; then
  echo "§provenance-chain-broken: expected upstream manifest at $expected_path " \
       "(absolute: $abs_path), but the file is absent. The manifest chain to $stage " \
       "is broken. Recovery: --reconcile per D2.1 v2.1's chain-recovery pattern, OR " \
       "--rerun=<stage> per D4.5 for absent-manifest cases." >&2
  log_halt "§provenance-chain-broken" \
    "$stage pre-flight detected upstream manifest absent at $expected_path"
  exit 2
fi

# Recompute manifest sha (manifest_sha256 field zeroed)
recomputed_sha="$(sha256_manifest_self_zeroed "$abs_path")"
if [ "$recomputed_sha" != "$expected_sha" ]; then
  echo "§provenance-chain-broken: parent manifest sha mismatch at $expected_path; " \
       "expected ${expected_sha:0:12}..., got ${recomputed_sha:0:12}.... " \
       "The upstream manifest has been modified post-seal, or the run-state's " \
       "sha pointer is stale. Recovery: --reconcile per D2.1 v2.1's chain-recovery pattern." >&2
  log_halt "§provenance-chain-broken" \
    "$stage pre-flight: manifest at $expected_path recomputes to $recomputed_sha but run-state expected $expected_sha"
  exit 2
fi

# Chain intact for this stage's upstream. Skill's at-write predicates will
# validate the deeper provenance chains (e.g., ac_list_sha256, four_hat_seal_sha256).
trace "preflight-provenance: chain intact for $stage; exit 0"
exit 0
```

---

## Design notes

### Why UserPromptSubmit, not PreToolUse

PreToolUse fires per-tool-call, after the model has decided to invoke a tool. UserPromptSubmit fires before the model sees the prompt — it's the earliest enforcement surface. A chain-broken cascade stage should halt before context spend, which means UserPromptSubmit.

The alternative (matching PreToolUse on the Task tool) would let the model spend turns proposing tool calls before discovering the upstream is broken. The exit-2-from-UserPromptSubmit pattern halts the prompt itself.

### Why this script doesn't check ac_list_sha256 or four_hat_seal_sha256

D2.1 v2's §Caller-side verification protocol enumerates six steps; step 6 is "Run stage-specific verifier predicates against the manifest's outputs." Steps 1–5 are the chain-integrity check — that's what this hook does. Step 6's per-stage predicates fire inside the skill's gate evaluation (per Child 0001-B continuation 1's amendments), not at the hook level.

This split is intentional: the hook is a fast pre-flight that catches the gross chain-break case (manifest absent, sha mismatch); the skill's at-write gates do the deep predicate work. Splitting them means a deep-predicate failure surfaces *after* the model has loaded context for the stage, which is the right place for the diagnostic (the model can author a recovery prompt).

### Why /specify, /onboard, /discovery, /constitution are excluded from the matcher

These are entry-point stages without strict upstream manifest requirements:

- **/onboard** is the cascade's bootstrap; no upstream exists.
- **/discovery** and **/constitution** are chat-Claude reflective stages without formal gate inventories per D3.4 (per `repo-state-summary.md` Part 3 item 5).
- **/specify** is the cascade's per-feature entry point; per D3.4 §`/specify` row, its provenance check is structural (the spec file exists and is parseable), not a manifest-chain check. The skill's Gate 1 handles it.

The exclusion list is fixed; if v0.2.x adds a new entry-point stage, this script's case statement needs updating. **Surfaced item:** flag this in v0.2.x design surface if more entry-point stages emerge.

### Diagnostic output goes to stderr, not stdout

Per D2.2 §Hook events table: UserPromptSubmit's stdout is added to Claude's context. If the hook fails, stdout would feed the failure message INTO the model's next turn — which is the opposite of what we want (we want the founder to see the diagnostic and decide how to recover; the model should never see the chain-break diagnostic as if it were normal context).

stderr is the right channel: Claude Code surfaces stderr to the user but doesn't inject it as context.

---

## Failing-test seed

Per `decomposition.md` Child 0001-C failing-test-seed list:

```python
def test_preflight_provenance_blocks_broken_chain(tmp_cascade_repo):
    """
    asserts the script exits 2 when given a stub manifest with a deliberately-wrong
    parent sha; covers AC-14.
    """
    # Set up run-state with a sha pointer that won't match the stub manifest
    write_run_state(tmp_cascade_repo, {
        "last_completed_stage": {
            "name": "specify",
            "ticket": "TST-42",
            "postcondition_manifest_path": ".cascade/manifests/TST-42-specify.json",
            "postcondition_manifest_sha256": "deadbeef" * 8,  # 64 chars
        }
    })
    # Write a real manifest with a different sha
    write_manifest(tmp_cascade_repo, "TST-42-specify.json", {
        "stage": "/specify",
        "manifest_sha256": "",  # canonical zeroed form will hash to something else
    })

    result = run_hook(
        "preflight-provenance.sh",
        payload={"prompt": "/review TST-42"},
        project_dir=tmp_cascade_repo,
    )
    assert result.exit_code == 2
    assert "§provenance-chain-broken" in result.stderr
    assert "TST-42-specify.json" in result.stderr
    # Stdout is empty — diagnostic goes to stderr only
    assert result.stdout == ""

def test_preflight_provenance_passes_on_intact_chain(tmp_cascade_repo):
    """asserts exit 0 silent when the chain is intact."""
    manifest_content = {"stage": "/specify", "manifest_sha256": ""}
    expected_sha = sha256_manifest_self_zeroed(manifest_content)
    write_run_state(tmp_cascade_repo, {
        "last_completed_stage": {
            "postcondition_manifest_path": ".cascade/manifests/TST-42-specify.json",
            "postcondition_manifest_sha256": expected_sha,
        }
    })
    write_manifest(tmp_cascade_repo, "TST-42-specify.json", manifest_content)

    result = run_hook("preflight-provenance.sh",
                      payload={"prompt": "/review TST-42"},
                      project_dir=tmp_cascade_repo)
    assert result.exit_code == 0
    assert result.stderr == ""
    assert result.stdout == ""

def test_preflight_provenance_ignores_non_cascade_prompts(tmp_cascade_repo):
    """asserts exit 0 silent when the prompt is not a cascade slash-command."""
    result = run_hook("preflight-provenance.sh",
                      payload={"prompt": "tell me about Python decorators"},
                      project_dir=tmp_cascade_repo)
    assert result.exit_code == 0
```

---

## Cross-references

- **D2.1 v2 §Caller-side verification protocol** — the binding for steps 1–5 this hook implements.
- **D2.1 v2.1** — canonical `.cascade/run-state.json` path the script reads.
- **D2.2 §Hook events table** — `UserPromptSubmit` event semantics + exit-2-rejects-prompt mechanic.
- **D2.2 §Mapping table** — the recommendation to use UserPromptSubmit for stage-specific pre-flight.
- **D2.2 §Critical caveats #2** — "do not put cascade:run-state snapshot logic in PostToolUse"; this hook reads (doesn't write) run-state, so the caveat doesn't apply here.
- **D3.4 §Per-stage gate inventory** — every cascade stage's first gate is `<stage>.provenance` with this same chain-integrity predicate; this hook is the unified hook-level enforcement for all of them.
- **D4.5 §Decision** — `--reconcile` for /build, /wrap, /specify, /plan; `--rerun` for /specify, /review, /plan. F-Rev-2's queued amendment extends to the other stages in v0.2.x.
- **`.claude/hooks/_lib.sh`** — sourced for IO and emitter helpers.
- **Parent spec AC-14** — covered by this script + the other six in this session.
