#!/usr/bin/env bash
# 把 newest-version/ 里版本号最新的 HTML 同步为 GitHub Pages 首页。
set -euo pipefail
cd "$(dirname "$0")/.."

src="$(ls -1 newest-version/Hiscore_v*.html | grep -E '/Hiscore_v[0-9]+(\.[0-9]+)*\.html$' | sort -V | tail -n 1)"
mkdir -p docs
cp "$src" docs/index.html
: > docs/.nojekyll

echo "已同步：$src -> docs/index.html"
sha256sum "$src" docs/index.html
