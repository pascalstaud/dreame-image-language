#!/bin/bash
# Generate 400px thumbnails for all brands
# Uses sips (built-in macOS) — preserves aspect ratio

set -euo pipefail
BASE="$(cd "$(dirname "$0")/.." && pwd)"

BRANDS="dreame roborock dyson samsung xiaomi haier vipp lg hisense gaggenau apple basalte lutron vzug philips"

for brand in $BRANDS; do
  src="$BASE/$brand"
  dst="$BASE/thumbs/$brand"
  [ -d "$src" ] || continue
  mkdir -p "$dst"
  count=0
  find "$src" -maxdepth 3 \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.webp" \) | while read -r f; do
    fname="$(basename "$f")"
    out="$dst/$fname"
    [ -f "$out" ] && continue  # skip existing
    sips --resampleWidth 400 "$f" --out "$out" 2>/dev/null && count=$((count+1))
  done
  echo "$brand: thumbnails done → $dst"
done

echo "All thumbnails generated."
