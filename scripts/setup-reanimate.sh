#!/usr/bin/env bash
# Install reanimate's script dependencies, then make its Playwright match the Chromium already on
# this machine instead of downloading another (~250 MB). Upstream pins playwright 1.64.1; cloud
# sessions here ship Chromium for the globally installed Playwright (1.63.0 at the time of writing).
# The submodule's package.json and bun.lock are restored afterwards, so the submodule stays clean.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIR="$ROOT/tools/reanimate/skills/reanimate/scripts"
command -v bun >/dev/null || { echo "bun is required (https://bun.sh)"; exit 1; }
[ -f "$DIR/package.json" ] || { echo "run: git submodule update --init"; exit 1; }
cd "$DIR"
bun install --silent
if bun -e 'const {chromium}=await import("playwright"); const b=await chromium.launch(); await b.close()' 2>/dev/null; then
  echo "ready: Chromium works with the pinned Playwright"; exit 0
fi
GLOBAL=$(cd / && node -p 'require("playwright/package.json").version' 2>/dev/null || true)  # resolved outside the project
[ -n "$GLOBAL" ] || { echo "no pre-installed Playwright found; run upstream's setup.sh instead (downloads Chromium)"; exit 1; }
BAK=$(mktemp -d); cp package.json bun.lock "$BAK/"
bun add --silent "playwright@$GLOBAL"
cp "$BAK/package.json" "$BAK/bun.lock" .; rm -rf "$BAK"
bun -e 'const {chromium}=await import("playwright"); const b=await chromium.launch(); console.log("ready: chromium", b.version()); await b.close()'
