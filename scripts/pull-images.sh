#!/bin/bash
# Pull Instagram images for all brands via gallery-dl
# Requires Chrome login to Instagram

set -euo pipefail
BASE="$(cd "$(dirname "$0")/.." && pwd)"
GDL=$(which gallery-dl 2>/dev/null || echo "/usr/local/bin/gallery-dl")

declare -A HANDLES=(
  [dreame]="dreame_tech"
  [roborock]="roborock"
  [dyson]="dyson"
  [samsung]="smartthings"
  [xiaomi]="mijia_global"
  [haier]="haierglobal"
  [vipp]="vipp"
  [lg]="lg_homeappliances"
  [hisense]="hisensehomeappliances"
  [gaggenau]="gaggenauofficial"
  [apple]="apple"
  [basalte]="basalte.be"
  [lutron]="lutronelectronics"
  [vzug]="vzug"
  [philips]="philipshomeliving"
)

RANGE="1-150"
[ -n "${1:-}" ] && BRAND="$1" || BRAND=""

for brand in "${!HANDLES[@]}"; do
  [ -n "$BRAND" ] && [ "$brand" != "$BRAND" ] && continue
  handle="${HANDLES[$brand]}"
  out="$BASE/$brand/instagram"
  mkdir -p "$out"
  echo "=== Downloading @$handle → $out ==="
  "$GDL" \
    --cookies-from-browser chrome \
    --write-metadata \
    --range "$RANGE" \
    -d "$out" \
    "https://www.instagram.com/$handle/" || echo "  ⚠ Failed for @$handle"
  # Flatten nested subdirectory gallery-dl creates
  find "$out" -mindepth 2 \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) -exec mv {} "$out/" \; 2>/dev/null || true
  count=$(find "$out" -maxdepth 1 -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
  echo "  $count images in $out"
done

echo ""
echo "Done. Run: python3 build_data.py && bash scripts/gen-thumbs.sh"
