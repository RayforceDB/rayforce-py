#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# --- Files containing version strings ---
PYPROJECT="${PROJECT_ROOT}/pyproject.toml"
SETUP_PY="${PROJECT_ROOT}/setup.py"
INIT_PY="${PROJECT_ROOT}/rayforce/__init__.py"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# --- Helpers ---
info()  { echo -e "${CYAN}${BOLD}::${NC} $1"; }
ok()    { echo -e "${GREEN}${BOLD}✓${NC}  $1"; }
warn()  { echo -e "${YELLOW}${BOLD}!${NC}  $1"; }
err()   { echo -e "${RED}${BOLD}✗${NC}  $1" >&2; }
die()   { err "$1"; exit 1; }

# --- Validate input ---
VERSION="$1"

if [ -z "$VERSION" ]; then
  echo ""
  echo -e "  ${BOLD}Usage:${NC} ./scripts/release.sh <version>"
  echo ""
  echo "  Example: ./scripts/release.sh 0.6.0"
  echo ""
  exit 1
fi

if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  die "Invalid version format: '${VERSION}' (expected X.Y.Z)"
fi

# --- Pre-flight checks ---
cd "$PROJECT_ROOT"

CURRENT_VERSION=$(grep -m1 '^version' "$PYPROJECT" | sed 's/.*"\(.*\)"/\1/')
info "Current version: ${BOLD}${CURRENT_VERSION}${NC}"
info "New version:     ${BOLD}${VERSION}${NC}"
echo ""

if [ "$CURRENT_VERSION" = "$VERSION" ]; then
  die "Version ${VERSION} is already the current version"
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  die "Working tree is dirty. Commit or stash changes first."
fi

if git rev-parse "$VERSION" >/dev/null 2>&1; then
  die "Git tag '${VERSION}' already exists"
fi

# --- Update version in all files ---
info "Updating version strings..."

# pyproject.toml: version = "X.Y.Z"
sed -i '' "s/^version = \"${CURRENT_VERSION}\"/version = \"${VERSION}\"/" "$PYPROJECT"
ok "pyproject.toml"

# setup.py: version="X.Y.Z"
sed -i '' "s/version=\"${CURRENT_VERSION}\"/version=\"${VERSION}\"/" "$SETUP_PY"
ok "setup.py"

# rayforce/__init__.py: version = "X.Y.Z"
sed -i '' "s/^version = \"${CURRENT_VERSION}\"/version = \"${VERSION}\"/" "$INIT_PY"
ok "rayforce/__init__.py"

echo ""

# --- Summary ---
info "Changes to be committed:"
echo ""
git diff --stat
echo ""

read -r -p "$(echo -e "${CYAN}${BOLD}::${NC} Commit and tag as ${BOLD}${VERSION}${NC}? [Y/n] ")" CONFIRM
CONFIRM=${CONFIRM:-y}

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  warn "Aborted. Version files have been updated but not committed."
  warn "Run 'git checkout -- .' to revert."
  exit 1
fi

# --- Git commit & tag ---
git add "$PYPROJECT" "$SETUP_PY" "$INIT_PY"
git commit -m "release: ${VERSION}"
git tag "$VERSION"

ok "Committed and tagged ${BOLD}${VERSION}${NC}"
echo ""

# --- Push ---
read -r -p "$(echo -e "${CYAN}${BOLD}::${NC} Push to origin? [Y/n] ")" PUSH
PUSH=${PUSH:-y}

if [[ "$PUSH" =~ ^[Yy]$ ]]; then
  git push && git push --tags
  ok "Pushed to origin"
else
  echo ""
  warn "Remember to push manually:"
  echo "  git push && git push --tags"
fi

echo ""
echo -e "${GREEN}${BOLD}Release ${VERSION} complete!${NC}"
