#!/bin/bash
# Pull YouTube thumbnails for all brands via yt-dlp

set -uo pipefail
BASE="$(cd "$(dirname "$0")/.." && pwd)"

channel_for() {
  case "$1" in
    dreame)   echo "@DreameTech" ;;
    roborock) echo "@RoborockOfficial" ;;
    dyson)    echo "@dyson" ;;
    samsung)  echo "@SamsungGlobal" ;;
    xiaomi)   echo "@XiaomiGlobal" ;;
    haier)    echo "@HaierGlobal" ;;
    vipp)     echo "@vippdesign" ;;
    lg)       echo "@LGUS" ;;
    hisense)  echo "@HisenseGlobal" ;;
    gaggenau) echo "@GaggenauOfficial" ;;
    apple)    echo "@Apple" ;;
    lutron)   echo "@LutronElectronics" ;;
    vzug)     echo "@VZUGnews" ;;
    philips)  echo "@PhilipsHomeLiving" ;;
    basalte)  echo "@BasalteDesign" ;;
  esac
}

BRANDS="dreame roborock dyson samsung xiaomi haier vipp lg hisense gaggenau apple basalte lutron vzug philips"
LIMIT=30
TARGET="${1:-}"

for brand in $BRANDS; do
  [ -n "$TARGET" ] && [ "$brand" != "$TARGET" ] && continue
  channel=$(channel_for "$brand")
  out="$BASE/$brand/youtube"
  mkdir -p "$out"
  echo "=== YouTube $channel → $out ==="
  yt-dlp \
    --skip-download \
    --write-thumbnail \
    --convert-thumbnails jpg \
    --playlist-end "$LIMIT" \
    -o "$out/%(id)s" \
    "https://www.youtube.com/$channel/videos" 2>&1 | grep -v "^\[debug\]" || echo "  ⚠ Failed $channel"
  count=$(find "$out" -name "*.jpg" 2>/dev/null | wc -l | tr -d ' ')
  echo "  → $count thumbnails"
done

echo "Done."
