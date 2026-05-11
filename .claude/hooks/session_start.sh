#!/usr/bin/env bash
# SessionStart hook for Solo-Setup
# Reports current branch state and reminds of session-start protocol.
set -euo pipefail

BRANCH=$(git branch --show-current 2>/dev/null || echo "(no branch)")
echo "── Solo-Setup session start ──────────────────────"
echo "Current branch: ${BRANCH}"

# Infer SOL issue ID from branch name if present
if [[ "${BRANCH}" =~ ^SOL-([0-9]+) ]]; then
  echo "Linear issue: SOL-${BASH_REMATCH[1]}"
fi

# Warn on main
if [[ "${BRANCH}" == "main" || "${BRANCH}" == "master" ]]; then
  echo "WARNING: you are on ${BRANCH}. Create a feature branch before editing (unless this is the SOL-17 bootstrap)."
fi

# List stale merged-but-not-deleted branches
STALE=$(git branch --merged main 2>/dev/null | grep -v "^\*" | grep -v " main$" | head -5 || true)
if [[ -n "${STALE}" ]]; then
  echo ""
  echo "Stale merged branches (consider deleting):"
  echo "${STALE}"
fi

echo ""
echo "Reminder: check Linear SOL/Sync Queue for sync:pending tickets before starting work."
echo "──────────────────────────────────────────────────"
