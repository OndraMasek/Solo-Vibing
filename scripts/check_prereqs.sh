#!/usr/bin/env bash
# check_prereqs.sh — /onboard step 1 prereq check.
#
# Verifies that all template and reference files /onboard depends on are
# present in the repo. Halts onboarding with a structured listing of any
# missing files so the founder can re-overlay them rather than abandoning
# the run.
#
# Exit codes:
#   0  — all prereqs present
#   1  — one or more files missing (list emitted to stdout)
#   2  — repo root not found / not a git repo

set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$repo_root" ]]; then
  echo "BLOCKED: not inside a git repository" >&2
  exit 2
fi

cd "$repo_root"

required=(
  "docs/templates/spec.md.template"
  "docs/templates/halt-messages.md"
  "docs/templates/CLAUDE.md.template"
  "docs/templates/.solo-config.json.template"
  "docs/templates/onboarding/chat-kickoff.md.template"
  "docs/templates/onboarding/chat-instructions.md.template"
  "docs/templates/discovery/research-prompt-templates.md"
  "docs/templates/discovery/challenge-checklist.md"
  "docs/product/north-star-questions.md"
)

missing=()
for path in "${required[@]}"; do
  if [[ ! -f "$path" ]]; then
    missing+=("$path")
  fi
done

if (( ${#missing[@]} == 0 )); then
  echo "OK: all 9 prereq files present"
  exit 0
fi

echo "BLOCKED: ${#missing[@]} prereq file(s) missing:"
for path in "${missing[@]}"; do
  echo "  - $path"
done
echo ""
echo "Recovery: re-overlay templates from upstream without losing project state:"
echo "  bash bootstrap.sh --refresh-templates"
echo ""
echo "If --refresh-templates is unavailable, fetch the missing files manually from"
echo "the upstream Solo-Setup repo. Do NOT re-clone — that destroys your .env,"
echo "marker, and any post-onboard work."
exit 1
