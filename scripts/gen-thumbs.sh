#!/bin/bash
# Generate 400px thumbnails for all brands
# - .jpg/.jpeg/.png → sips resample (preserves format)
# - .webp → sips convert to .jpg (sips can't write webp natively)

set -uo pipefail
BASE="$(cd "$(dirname "$0")/.." && pwd)"

BRANDS="dreame roborock dyson samsung xiaomi haier vipp lg hisense gaggenau apple basalte lutron vzug philips"
new=0

for brand in $BRANDS; do
  src="$BASE/$brand"
  dst="$BASE/thumbs/$brand"
  [ -d "$src" ] || continue
  mkdir -p "$dst"

  # Standard formats (jpg, png)
  find "$src" -maxdepth 3 \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) | while read -r f; do
    fname="$(basename "$f")"
    out="$dst/$fname"
    [ -f "$out" ] && continue
    sips --resampleWidth 400 "$f" --out "$out" 2>/dev/null && echo "  + $brand/$fname"
  done

  # WebP → jpg (sips can't write webp, must convert format)
  find "$src" -maxdepth 3 -name "*.webp" | while read -r f; do
    fname="$(basename "${f%.webp}").jpg"
    out="$dst/$fname"
    [ -f "$out" ] && continue
    sips --resampleWidth 400 --setProperty format jpeg "$f" --out "$out" 2>/dev/null && echo "  + $brand/$fname (webp→jpg)"
  done

  count=$(find "$dst" -type f | wc -l | tr -d ' ')
  echo "$brand: $count thumbnails"
done

echo ""
echo "Done."
