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
