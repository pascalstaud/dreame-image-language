#!/bin/bash
# Pull YouTube thumbnails for all brands via yt-dlp

set -euo pipefail
BASE="$(cd "$(dirname "$0")/.." && pwd)"

declare -A YT_CHANNELS=(
  [dreame]="@DreameTech"
  [roborock]="@RoborockOfficial"
  [dyson]="@dyson"
  [samsung]="@SamsungGlobal"
  [xiaomi]="@XiaomiGlobal"
  [haier]="@HaierGlobal"
  [vipp]="@vippdesign"
  [lg]="@LGUS"
  [dyson]="@dyson"
  [gaggenau]="@GaggenauOfficial"
  [apple]="@Apple"
  [lutron]="@LutronElectronics"
  [vzug]="@VZUGnews"
  [philips]="@PhilipsHomeLiving"
)

LIMIT=30
[ -n "${1:-}" ] && BRAND="$1" || BRAND=""

for brand in "${!YT_CHANNELS[@]}"; do
  [ -n "$BRAND" ] && [ "$brand" != "$BRAND" ] && continue
  channel="${YT_CHANNELS[$brand]}"
  out="$BASE/$brand/youtube"
  mkdir -p "$out"
  echo "=== YouTube @$channel → $out ==="
  yt-dlp \
    --skip-download \
    --write-thumbnail \
    --convert-thumbnails jpg \
    --playlist-end "$LIMIT" \
    -o "$out/%(id)s" \
    "https://www.youtube.com/$channel/videos" 2>/dev/null || echo "  ⚠ Failed for $channel"
  count=$(find "$out" -name "*.jpg" 2>/dev/null | wc -l | tr -d ' ')
  echo "  $count thumbnails"
done

echo "Done."
