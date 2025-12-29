#!/bin/bash

# Usage: ./announce-release.sh VERSION [BOT_API_KEY]

VERSION=${1}
BOT_API_KEY=${2}
DEBUG=${3}

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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CHANGELOG="${PROJECT_ROOT}/docs/docs/content/CHANGELOG.md"

if [ ! -f "${CHANGELOG}" ]; then
  echo "Warning: CHANGELOG not found at ${CHANGELOG}"
  CHANGELOG_CONTENT=""
else
  CHANGELOG_CONTENT=$(awk -v version="${VERSION}" '
    BEGIN {
      collecting=0
      found_version=0
      # Escape dots in version for regex matching
      escaped_version = version
      gsub(/\./, "\\.", escaped_version)
    }
    {
      # Stop collecting at next version entry (check this first to avoid including it)
      if (collecting && $0 ~ /^## \*\*`/) {
        exit 0
      }
      # Start collecting when we find the version line
      # Pattern: ## **`VERSION`**
      if ($0 ~ "^## \\*\\*`" escaped_version "`\\*\\*") {
        collecting=1
        found_version=1
        print
        next
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
    echo "Exit: No changelog entry found for version ${VERSION}"
    exit 1
  fi
fi

CONTENT="**New Rayforce-Py Version is Released!**"

if [ -n "${CHANGELOG_CONTENT}" ]; then
  CONTENT="${CONTENT}

${CHANGELOG_CONTENT}"
fi

if [ "$DEBUG" == 1 ]; then
  echo "${CONTENT}"
  exit 0
fi

curl -X POST https://rayforcedb.zulipchat.com/api/v1/messages \
  -u releases-bot@rayforcedb.zulipchat.com:${BOT_API_KEY} \
  -d type=stream \
  -d "to=Announcements" \
  -d topic="Rayforce-Py" \
  -d "content=${CONTENT}"

echo ""
echo "✅ Announcement sent to Zulip!"
