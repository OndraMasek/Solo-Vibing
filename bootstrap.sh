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
# Modes:
#   (no args)              fresh install (default)
#   --refresh-templates    re-overlay docs/templates/, scripts/, .claude/ from
#                          upstream without touching project state. Used by
#                          /onboard step 1 recovery and by /map-codebase.
#                          Refuses to run unless a Solo-Setup repo already
#                          exists at the current directory.
#
# Then in the same directory:
#   claude
#   /onboard

set -euo pipefail

TEMPLATE_REPO="https://github.com/OndraMasek/Solo-Vibing.git"
TEMPLATE_BRANCH="main"

mode="install"
if [[ "${1:-}" == "--refresh-templates" ]]; then
  mode="refresh"
fi

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

if [[ "$mode" == "install" ]]; then
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

  if [ -d .git ]; then
    echo "ERROR: current directory already contains a .git directory." >&2
    echo "  bootstrap.sh refuses to touch an existing repo. Use --refresh-templates" >&2
    echo "  if you want to re-overlay templates into an existing Solo-Setup repo." >&2
    exit 1
  fi
else
  # refresh mode — must be inside a git repo that looks like a Solo-Setup install.
  if [ ! -d .git ]; then
    echo "ERROR: --refresh-templates requires an existing git repository." >&2
    exit 1
  fi
  if [ ! -d docs/templates ]; then
    echo "ERROR: --refresh-templates refuses to run; docs/templates/ not found." >&2
    echo "  This does not look like a Solo-Setup repo." >&2
    exit 1
  fi
fi

# --- fetch -------------------------------------------------------------------

tmp="$(mktemp -d -t solo-setup-XXXXXX)"
trap 'rm -rf "$tmp"' EXIT

echo "→ Fetching template from $TEMPLATE_REPO ($TEMPLATE_BRANCH branch)..."
git clone --depth 1 --branch "$TEMPLATE_BRANCH" --quiet "$TEMPLATE_REPO" "$tmp/template"

# --- overlay -----------------------------------------------------------------

# In install mode, copy template into the current directory. Excluded:
#   .git                          we want fresh history, not the template's
#   bootstrap.sh                  no need to ship the bootstrapper into every fork
#   CLAUDE.md                     upstream's session instructions; fork renders from .template
#   docs/.solo-config.json        upstream's config; fork renders from .template
#   docs/constitution.md          upstream's governing principles; fork re-authors via /constitution
#   docs/specs/0001-*             upstream's worked-example spec; fork re-authors via /specify
#   docs/product/north-star.md    upstream's north-star; fork re-authors via /discovery
#   docs/discovery/               founder-instance state — empty in fresh forks
#   docs/research/                founder-instance state
#   docs/decisions/0*-*.md        upstream's ADRs; fork-specific decisions only
#
# In refresh mode, restrict to the template-bearing directories so we never
# clobber founder-authored files.

excludes=(
  '--exclude=.git'
  '--exclude=bootstrap.sh'
  '--exclude=CLAUDE.md'
  '--exclude=docs/.solo-config.json'
  '--exclude=docs/constitution.md'
  '--exclude=docs/specs'
  '--exclude=docs/product/north-star.md'
  '--exclude=docs/discovery'
  '--exclude=docs/research'
  '--exclude=docs/decisions/0*-*.md'
)

if [[ "$mode" == "refresh" ]]; then
  echo "→ Refreshing templates in $(pwd)..."
  ( cd "$tmp/template" && tar -cf - "${excludes[@]}" \
      docs/templates \
      scripts \
      .claude \
      docs/product/north-star-questions.md \
      .gitignore \
      .mcp.json \
    ) | tar -xf -
  echo "✓ Templates refreshed."
  echo "  Re-run /onboard step 1 to verify, then continue the cascade."
  exit 0
fi

echo "→ Installing template into $(pwd)..."
( cd "$tmp/template" && tar -cf - "${excludes[@]}" . ) | tar -xf -

# Render the two canonical files from their templates. Substitution happens
# during /onboard (marker pick); bootstrap copies the templates as-is.
if [ -f docs/templates/CLAUDE.md.template ]; then
  cp docs/templates/CLAUDE.md.template CLAUDE.md.template
fi
if [ -f docs/templates/.solo-config.json.template ]; then
  cp docs/templates/.solo-config.json.template docs/.solo-config.json.template
fi

# --- fresh git history -------------------------------------------------------

if git init --quiet --initial-branch=main 2>/dev/null; then
  :
else
  git init --quiet
  git symbolic-ref HEAD refs/heads/main 2>/dev/null || true
fi

git add -A

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

# --- optional GitHub remote --------------------------------------------------

# Offer to create the GitHub repo right now, before any other process can
# auto-init a parallel history on the remote side. This is the canonical
# happy path; declining is fine but the founder should not pre-create the
# remote via GitHub's web UI (which auto-inits a README/license commit).

create_remote() {
  if ! command -v gh >/dev/null 2>&1; then
    return 1
  fi
  if ! gh auth status >/dev/null 2>&1; then
    return 1
  fi
  local default_name
  default_name="$(basename "$(pwd)")"
  echo ""
  echo "GitHub repo not yet created. Recommended: create it now via gh CLI."
  echo "Avoids parallel-history conflicts on first push."
  printf "Create private repo '%s' on GitHub and push? [Y/n] " "$default_name"
  read -r answer </dev/tty || answer=""
  case "${answer:-Y}" in
    [Yy]*|"")
      gh repo create "$default_name" --source=. --private --push --remote=origin
      return $?
      ;;
    *) return 2 ;;  # user declined
  esac
}

remote_status="skipped"
if create_remote; then
  remote_status="created"
else
  rc=$?
  if [[ $rc -eq 2 ]]; then
    remote_status="declined"
  else
    remote_status="unavailable"
  fi
fi

# --- next steps --------------------------------------------------------------

case "$remote_status" in
  created)
    cat <<EOS

────────────────────────────────────────────────────────────
✓ Solo-Setup is ready, and the GitHub remote is live.

Next:
  1.  claude        # launch Claude Code from this folder
  2.  /onboard      # the first command in the session
────────────────────────────────────────────────────────────
EOS
    ;;
  declined)
    cat <<'EOS'

────────────────────────────────────────────────────────────
✓ Solo-Setup is ready. GitHub remote skipped at your request.

WARNING: do NOT pre-create the GitHub repo via the web UI with the
"Initialize this repository with a README" box checked — that creates a
parallel-history conflict on first push.

When you want a remote later, run:
  gh repo create <name> --source=. --private --push

Next:
  1.  claude        # launch Claude Code from this folder
  2.  /onboard      # the first command in the session
────────────────────────────────────────────────────────────
EOS
    ;;
  unavailable|*)
    cat <<'EOS'

────────────────────────────────────────────────────────────
✓ Solo-Setup is ready. gh CLI not available; remote not created.

When you have gh installed and authed, run:
  gh repo create <name> --source=. --private --push

Avoid creating the GitHub repo via the web UI with auto-init enabled —
that produces a parallel-history conflict on first push.

Next:
  1.  claude        # launch Claude Code from this folder
  2.  /onboard      # the first command in the session
────────────────────────────────────────────────────────────
EOS
    ;;
esac
