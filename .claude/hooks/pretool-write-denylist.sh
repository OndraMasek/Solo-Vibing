#!/usr/bin/env bash
# .claude/hooks/pretool-write-denylist.sh
#
# Cascade-control write denylist guard per spec AC-21 / D4.1 §D4.1.7.
# Fires on PreToolUse with matcher Write|Edit|MultiEdit. Reads patterns from
# .claude/agents/build-write-denylist.txt; halts if the target file path
# matches any pattern. Halt code: §cascade-control-write-blocked.
#
# Per SOL-HANDOFF-008 decision 3: denylist (hard halt) + reviewer-stance
# soft-check inside /review. This script is the hard-halt layer; the
# reviewer-stance layer lives inside the /review skill.
#
# Output shape per D2.2 §Hook events table: PreToolUse uses {"decision":
# "block", "reason": "..."} via stdout for explicit deny (exit 0), or exit 2
# with stderr diagnostic. We use the explicit-deny JSON shape for clarity.

set -euo pipefail

# Source shared helpers (jq fallback, run-state read, etc.). Optional; if the
# lib is missing, fall through with a soft pass — denylist enforcement is
# defense-in-depth, not the only safety net.
LIB="$CLAUDE_PROJECT_DIR/.claude/hooks/lib/common.sh"
[ -f "$LIB" ] && source "$LIB" || true

DENYLIST="$CLAUDE_PROJECT_DIR/.claude/agents/build-write-denylist.txt"

# If the denylist file is missing, soft-pass (the denylist mechanism is
# AC-21 — its absence on a fresh fork is not a halt condition).
if [ ! -f "$DENYLIST" ]; then
  exit 0
fi

# Read the tool input JSON from stdin.
PAYLOAD="$(cat)"

# Extract the target file path. PreToolUse payload shape per Claude Code docs:
#   {"tool_name": "Write|Edit|MultiEdit", "tool_input": {"file_path": "...", ...}}
# Use jq if available, else python.
if command -v jq >/dev/null 2>&1; then
  TARGET="$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.file_path // empty')"
else
  TARGET="$(printf '%s' "$PAYLOAD" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("tool_input",{}).get("file_path",""))')"
fi

# Empty target → soft-pass (some tool variants may use a different field).
[ -z "$TARGET" ] && exit 0

# Normalize: make path relative to repo root for pattern matching.
REPO_ROOT="$CLAUDE_PROJECT_DIR"
case "$TARGET" in
  "$REPO_ROOT"/*) RELPATH="${TARGET#$REPO_ROOT/}" ;;
  /*)             RELPATH="$TARGET" ;;
  *)              RELPATH="$TARGET" ;;
esac

# Walk the denylist; first match wins.
MATCH=""
while IFS= read -r LINE || [ -n "$LINE" ]; do
  # Strip comments and blanks
  case "$LINE" in
    \#*|"") continue ;;
  esac
  # Glob match using bash's [[ pattern ]]
  # shellcheck disable=SC2053
  if [[ "$RELPATH" == $LINE ]]; then
    MATCH="$LINE"
    break
  fi
done < "$DENYLIST"

if [ -n "$MATCH" ]; then
  # Emit the explicit-deny JSON shape via stdout, exit 0.
  REASON="§cascade-control-write-blocked: write to '$RELPATH' matches denylist pattern '$MATCH' in .claude/agents/build-write-denylist.txt (per D4.1.7 / spec AC-21). Recovery: edit the file manually outside the cascade, or use the responsible skill that has authority to write it."
  if command -v jq >/dev/null 2>&1; then
    jq -n --arg r "$REASON" '{decision: "block", reason: $r}'
  else
    python3 -c "import json,sys; print(json.dumps({'decision':'block','reason':sys.argv[1]}))" "$REASON"
  fi
  exit 0
fi

# No match — silent pass.
exit 0
