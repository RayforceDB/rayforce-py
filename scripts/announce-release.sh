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

CONTENT="**Rayforce-Py v${VERSION} Released!**

🔗 **PyPI:** https://pypi.org/project/rayforce-py/${VERSION}/
"

curl -X POST https://rayforcedb.zulipchat.com/api/v1/messages \
  -u releases-bot@rayforcedb.zulipchat.com:${BOT_API_KEY} \
  -d type=stream \
  -d "to=Announcements" \
  -d topic="Rayforce-Py" \
  -d "content=${CONTENT}"

echo ""
echo "✅ Announcement sent to Zulip!"
