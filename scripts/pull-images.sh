#!/bin/bash
# Pull Instagram images for all brands via gallery-dl
# Requires being logged into Instagram in Chrome

set -uo pipefail
BASE="$(cd "$(dirname "$0")/.." && pwd)"
GDL=$(which gallery-dl 2>/dev/null || echo "gallery-dl")

BRANDS="dreame roborock dyson samsung xiaomi haier vipp lg hisense gaggenau apple basalte lutron vzug philips"

handle_for() {
  case "$1" in
    dreame)   echo "dreame_tech" ;;
    roborock) echo "roborock" ;;
    dyson)    echo "dyson" ;;
    samsung)  echo "smartthings" ;;
    xiaomi)   echo "mijia_global" ;;
    haier)    echo "haierglobal" ;;
    vipp)     echo "vipp" ;;
    lg)       echo "lg_homeappliances" ;;
    hisense)  echo "hisensehomeappliances" ;;
    gaggenau) echo "gaggenauofficial" ;;
    apple)    echo "apple" ;;
    basalte)  echo "basalte.be" ;;
    lutron)   echo "lutronelectronics" ;;
    vzug)     echo "vzug" ;;
    philips)  echo "philipshomeliving" ;;
  esac
}

RANGE="1-150"
TARGET="${1:-}"

for brand in $BRANDS; do
  [ -n "$TARGET" ] && [ "$brand" != "$TARGET" ] && continue
  handle=$(handle_for "$brand")
  out="$BASE/$brand/instagram"
  mkdir -p "$out"
  echo "=== @$handle → $out ==="
  "$GDL" \
    --cookies-from-browser chrome \
    --write-metadata \
    --range "$RANGE" \
    -d "$out" \
    "https://www.instagram.com/$handle/" || echo "  ⚠ Failed @$handle"
  # Flatten nested subdirs gallery-dl creates
  find "$out" -mindepth 2 \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) -exec mv {} "$out/" \; 2>/dev/null || true
  count=$(find "$out" -maxdepth 1 \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) 2>/dev/null | wc -l | tr -d ' ')
  echo "  → $count images"
done

echo ""
echo "Done. Run: python3 build_data.py && bash scripts/gen-thumbs.sh"
