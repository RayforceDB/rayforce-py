#!/bin/bash

# Usage: ./announce-release.sh VERSION [BOT_API_KEY]

VERSION=${1:-"0.1.2"}
BOT_API_KEY=${2:-"YOUR_BOT_API_KEY"}

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
