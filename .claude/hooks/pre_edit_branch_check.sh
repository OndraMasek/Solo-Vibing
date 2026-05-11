#!/usr/bin/env bash
# PreToolUse hook for Solo-Setup
# Blocks edits on main/master. Warns if branch doesn't match SOL-<id>-<slug>.
set -euo pipefail

BRANCH=$(git branch --show-current 2>/dev/null || echo "")

if [[ "${BRANCH}" == "main" || "${BRANCH}" == "master" ]]; then
  echo "ERROR: editing on ${BRANCH} is blocked. Create a feature branch first." >&2
  echo "Branch naming convention: SOL-<issue-id>-<slug>" >&2
  exit 2
fi

if [[ -n "${BRANCH}" && ! "${BRANCH}" =~ ^SOL-[0-9]+- ]]; then
  echo "WARNING: branch '${BRANCH}' does not match SOL-<id>-<slug> pattern." >&2
  # warning only, do not block
fi

exit 0
