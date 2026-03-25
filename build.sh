#!/bin/bash
# Build script for Cloudflare Pages / GitHub Pages deployment
set -euo pipefail

DIST="dist"
rm -rf "$DIST"
mkdir -p "$DIST"

# HTML pages and data
cp *.html "$DIST/"
cp data.json "$DIST/" 2>/dev/null || echo "No data.json yet"

# Thumbnails
if [ -d "thumbs" ]; then
  cp -r thumbs "$DIST/thumbs"
fi

echo "Build complete: $(find $DIST -type f | wc -l) files in $DIST/"
du -sh "$DIST"
