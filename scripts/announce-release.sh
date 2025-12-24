#!/bin/bash

# Usage: ./announce-release.sh VERSION [BOT_API_KEY]

VERSION=${1}
BOT_API_KEY=${2}

if [ -z "$VERSION" ]; then
  echo "Error: VERSION is required"
  echo "Usage: $0 VERSION [BOT_API_KEY]"
  exit 1
fi

if [ -z "$BOT_API_KEY" ]; then
  echo "Error: BOT_API_KEY is required"
  echo "Usage: $0 VERSION BOT_API_KEY"
  exit 1
fi

# Get the script directory to find CHANGELOG
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
# Try docs location first, then project root
CHANGELOG="${PROJECT_ROOT}/docs/docs/content/CHANGELOG.md"
if [ ! -f "${CHANGELOG}" ]; then
  CHANGELOG="${PROJECT_ROOT}/CHANGELOG.md"
fi
if [ ! -f "${CHANGELOG}" ]; then
  CHANGELOG="${PROJECT_ROOT}/CHANGELOG"
fi

if [ ! -f "${CHANGELOG}" ]; then
  echo "Warning: CHANGELOG not found at ${CHANGELOG}"
  CHANGELOG_CONTENT=""
else
  ESCAPED_VERSION=$(echo "${VERSION}" | sed 's/\./\\./g')

  CHANGELOG_CONTENT=$(awk -v version="${ESCAPED_VERSION}" '
    BEGIN { collecting=0; found_version=0 }
    {
      # Start collecting when we find the version line
      # Pattern: ## **`VERSION`**
      if ($0 ~ "^## \\*\\*`" version "`\\*\\*") {
        collecting=1
        found_version=1
        print
        next
      }
      # Stop collecting at next version entry
      if (collecting && /^## \*\*\`/) {
        exit
      }
      # Collect lines while we are in the version section
      if (collecting) {
        print
      }
    }
    END {
      if (!found_version) {
        exit 1
      }
    }
  ' "${CHANGELOG}")

  if [ $? -ne 0 ] || [ -z "${CHANGELOG_CONTENT}" ]; then
    echo "Warning: No changelog entry found for version ${VERSION}"
    CHANGELOG_CONTENT=""
  fi
fi

CONTENT="**Rayforce-Py ${VERSION} Released!**"

if [ -n "${CHANGELOG_CONTENT}" ]; then
  CONTENT="${CONTENT}

${CHANGELOG_CONTENT}"
fi

curl -X POST https://rayforcedb.zulipchat.com/api/v1/messages \
  -u releases-bot@rayforcedb.zulipchat.com:${BOT_API_KEY} \
  -d type=stream \
  -d "to=Announcements" \
  -d topic="Rayforce-Py" \
  -d "content=${CONTENT}"

echo ""
echo "✅ Announcement sent to Zulip!"
