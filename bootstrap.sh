#!/usr/bin/env bash
#
# Solo-Setup bootstrap
# Downloads the Solo-Setup template into the current directory and
# initializes a fresh git repo, ready for Claude Code + /onboard.
#
# Usage (run inside a fresh empty directory):
#   mkdir my-project && cd my-project
#   curl -fsSL https://raw.githubusercontent.com/OndraMasek/Solo-Vibing/main/bootstrap.sh | bash
#
# Then in the same directory:
#   claude
#   /onboard

set -euo pipefail

TEMPLATE_REPO="https://github.com/OndraMasek/Solo-Vibing.git"
TEMPLATE_BRANCH="main"

# --- preflight ---------------------------------------------------------------

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git is not installed." >&2
  echo "  macOS:   xcode-select --install" >&2
  echo "  Windows: https://git-scm.com/download/win" >&2
  echo "  Linux:   use your package manager (apt/dnf/pacman) to install git" >&2
  exit 1
fi

if ! command -v tar >/dev/null 2>&1; then
  echo "ERROR: tar is not installed." >&2
  exit 1
fi

# Empty-directory guard. Allow only harmless noise.
shopt -s nullglob dotglob
unexpected=()
for item in *; do
  case "$item" in
    .DS_Store|Thumbs.db|bootstrap.sh) ;;
    *) unexpected+=("$item") ;;
  esac
done
shopt -u nullglob dotglob

if [ "${#unexpected[@]}" -gt 0 ]; then
  echo "ERROR: current directory is not empty." >&2
  echo "  Found: ${unexpected[*]}" >&2
  echo "  Run bootstrap.sh inside a fresh, empty directory." >&2
  exit 1
fi

# Refuse to overwrite an existing git repo.
if [ -d .git ]; then
  echo "ERROR: current directory already contains a .git directory." >&2
  echo "  bootstrap.sh refuses to touch an existing repo." >&2
  exit 1
fi

# --- fetch -------------------------------------------------------------------

tmp="$(mktemp -d -t solo-setup-XXXXXX)"
trap 'rm -rf "$tmp"' EXIT

echo "→ Fetching template from $TEMPLATE_REPO ($TEMPLATE_BRANCH branch)..."
git clone --depth 1 --branch "$TEMPLATE_BRANCH" --quiet "$TEMPLATE_REPO" "$tmp/template"

# --- overlay -----------------------------------------------------------------

# Copy everything from the template into the current directory, except:
#   .git (we want fresh history, not the template's)
#   bootstrap.sh (no need to ship the bootstrapper into every fork)
echo "→ Installing template into $(pwd)..."
( cd "$tmp/template" && tar -cf - --exclude='.git' --exclude='bootstrap.sh' . ) | tar -xf -

# --- fresh git history -------------------------------------------------------

# Try new-style --initial-branch first, fall back for older git.
if git init --quiet --initial-branch=main 2>/dev/null; then
  :
else
  git init --quiet
  git symbolic-ref HEAD refs/heads/main 2>/dev/null || true
fi

git add -A

# If git user.{name,email} aren't configured, the commit will fail. Detect and
# tell the user how to fix it, but don't make it our problem to set globally.
if ! git config --get user.email >/dev/null 2>&1 \
   || ! git config --get user.name  >/dev/null 2>&1; then
  echo "" >&2
  echo "ERROR: git user.name and user.email are not configured." >&2
  echo "  Set them globally with:" >&2
  echo "    git config --global user.name  \"Your Name\"" >&2
  echo "    git config --global user.email \"you@example.com\"" >&2
  echo "  Then re-run bootstrap.sh in a fresh directory." >&2
  exit 1
fi

git commit --quiet \
  -m "chore: bootstrap from Solo-Setup template" \
  -m "Source: $TEMPLATE_REPO@$TEMPLATE_BRANCH"

# --- next steps --------------------------------------------------------------

cat <<'EOS'

────────────────────────────────────────────────────────────
✓ Solo-Setup is ready in this directory.

Next:
  1.  claude        # launch Claude Code from this folder
  2.  /onboard      # the first command in the session

/onboard will walk you through:
  • picking your project marker
  • verifying Linear + GitHub connectors in your Claude.ai project
  • creating .env for your Linear API key
  • seeding the first north-star question

Optional, do later when /onboard reminds you:
  • Create a remote repo on GitHub:
      gh repo create --source=. --push --private
────────────────────────────────────────────────────────────
EOS
