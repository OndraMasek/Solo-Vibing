#!/usr/bin/env bash
# .claude/hooks/pretool-write-denylist.sh
#
# Cascade-control write denylist guard per spec AC-21 / D4.1 §D4.1.7.
#
# THREAT MODEL (D4.1 §D4.1.7): an autonomous BUILD AGENT — the Ralph loop — must
# not mutate cascade-control files (config, rules, run-state, manifests, locks,
# the denylist itself). The enforcement is therefore SCOPED to that context, not
# global: the cascade's own orchestrating stages (/onboard, /specify, /plan,
# /review, /update-linear, /verify, /retro, /config, /build --finalize) run in
# the founder's interactive session and are the AUTHORITATIVE writers of these
# files — blocking them is a self-application failure (they cannot complete the
# cascade). The original global enforcement blocked /onboard from writing
# docs/.solo-config.json, a file it is the authoritative writer of.
#
# IDENTITY SIGNAL: Ralph runs the build agent in a SEPARATE `claude` process
# launched by .ralph/<TICKET>/run.sh (see docs/templates/run.sh.template), which
# exports SOLO_BUILD_AGENT=1. That env var propagates to the spawned `claude`
# and to the PreToolUse hook subprocesses it launches. Founder sessions have no
# such var. This guard ENFORCES ONLY when SOLO_BUILD_AGENT=1 and soft-passes
# otherwise. The signal is process-scoped: it vanishes when run.sh exits, so a
# crashed loop cannot leave a stale flag that blocks later founder stages (the
# failure mode a run-state flag would carry).
#
# BASH BYPASS CLOSURE: the build agent runs with --dangerously-skip-permissions,
# so a Write-tool block alone is theater — a `cat > docs/.solo-config.json`
# heredoc would slip through. In build-agent context this hook therefore also
# inspects Bash commands for WRITE targets (redirection, tee, cp/mv, dd of=,
# sed -i, truncate) hitting denylisted paths. Reads (e.g. `cat config`) are not
# blocked — only writes. This hook must be wired for matcher Write|Edit|MultiEdit|Bash
# in .claude/settings.json for the Bash arm to receive events.
#
# Output: explicit-deny JSON {"decision":"block","reason":"..."} on stdout,
# exit 0. Halt code: §cascade-control-write-blocked.
#
# Per SOL-HANDOFF-008 decision 3: denylist (hard halt, build-agent-scoped) +
# reviewer-stance soft-check inside /review. Stays denylist-based, not allow-list.

set -euo pipefail

# 1. Identity gate FIRST. Outside build-agent context this is a one-test
#    soft-pass — the founder session (and every orchestration stage) writes
#    cascade-control files via the normal tools, unimpeded. Cheap on every
#    Write/Edit/MultiEdit/Bash call.
[ "${SOLO_BUILD_AGENT:-}" = "1" ] || exit 0

# 2. From here we are in build-agent context. Resolve inputs; soft-pass if any
#    are unavailable (defense-in-depth, not the only safety net).
[ -n "${CLAUDE_PROJECT_DIR:-}" ] || exit 0
DENYLIST="$CLAUDE_PROJECT_DIR/.claude/agents/build-write-denylist.txt"
[ -f "$DENYLIST" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0   # python3 is a documented prereq

EVAL="$CLAUDE_PROJECT_DIR/.claude/hooks/lib/denylist_eval.py"
[ -f "$EVAL" ] || exit 0

PAYLOAD="$(cat)"

# 3. Evaluate in python3 (robust Bash write-target parsing + fnmatch globbing,
#    matching the original bash `[[ == ]]` glob semantics). The evaluator prints
#    the block JSON on a match, nothing on a pass, and always exits 0 — so `|| true`
#    plus the empty-string check keep `set -e` safe.
DECISION="$(
  CLAUDE_PROJECT_DIR="$CLAUDE_PROJECT_DIR" \
  DENYLIST="$DENYLIST" \
  HOOK_PAYLOAD_RAW="$PAYLOAD" \
  python3 "$EVAL"
)" || true

# 4. Emit the block decision if the evaluator produced one; else silent pass.
[ -n "$DECISION" ] && printf '%s\n' "$DECISION"
exit 0
