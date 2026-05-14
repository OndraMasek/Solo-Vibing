#!/usr/bin/env bash
# verify_linear_key.sh — /onboard step 3 Linear API key validation.
#
# Resolves .env from both the worktree-local repo root and the main repo
# (git-common-dir) so /onboard runs cleanly inside a worktree. Loads
# LINEAR_API_KEY and tests it against Linear's GraphQL viewer endpoint.
#
# Exit codes:
#   0  — key valid; viewer returned
#   1  — key missing, malformed, or rejected by Linear
#   2  — .env not found in any candidate location
#   3  — curl missing

set -euo pipefail

if ! command -v curl >/dev/null 2>&1; then
  echo "BLOCKED: curl not installed" >&2
  exit 3
fi

# Resolve candidate .env locations: worktree-local first, then main repo.
worktree_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
common_dir="$(git rev-parse --git-common-dir 2>/dev/null || true)"

candidates=()
[[ -n "$worktree_root" ]] && candidates+=("$worktree_root/.env")
if [[ -n "$common_dir" ]]; then
  # git-common-dir returns the .git path of the main repo; its parent is the
  # main worktree root.
  main_root="$(cd "$common_dir/.." && pwd)"
  [[ "$main_root" != "$worktree_root" ]] && candidates+=("$main_root/.env")
fi

env_file=""
for path in "${candidates[@]}"; do
  if [[ -f "$path" ]]; then
    env_file="$path"
    break
  fi
done

if [[ -z "$env_file" ]]; then
  echo "BLOCKED: .env not found. Searched:" >&2
  for path in "${candidates[@]}"; do
    echo "  - $path" >&2
  done
  exit 2
fi

# Load LINEAR_API_KEY from the .env file without sourcing the whole file.
linear_key="$(grep -E '^LINEAR_API_KEY=' "$env_file" | head -n1 | cut -d= -f2- | tr -d '"' | tr -d "'" | tr -d '[:space:]')"

if [[ -z "$linear_key" ]]; then
  echo "BLOCKED: LINEAR_API_KEY not set in $env_file" >&2
  exit 1
fi

# Probe Linear's viewer endpoint with a minimal GraphQL query.
response="$(curl -sS -o /dev/null -w '%{http_code}' \
  -X POST https://api.linear.app/graphql \
  -H "Authorization: $linear_key" \
  -H "Content-Type: application/json" \
  -d '{"query":"query { viewer { id email } }"}' )"

if [[ "$response" == "200" ]]; then
  echo "OK: Linear API key valid (resolved from $env_file)"
  exit 0
fi

echo "BLOCKED: Linear API rejected the key (HTTP $response, resolved from $env_file)" >&2
echo "Recovery: rotate the key at https://linear.app/settings/api and re-run /onboard --reinit 3" >&2
exit 1
