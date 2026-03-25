#!/usr/bin/env python3
"""
Auto-trim white borders from Gaggenau product thumbnails.
Only trims if white margin is significant (>3% on any side).
Overwrites thumbs in-place.
"""
import sys
from pathlib import Path
from PIL import Image, ImageChops
import argparse

BASE = Path(__file__).parent.parent

def trim_white(img, threshold=240, min_margin_pct=0.03):
    """Return cropped image if white margins are significant, else original."""
    # Convert to RGB
    rgb = img.convert("RGB")
    w, h = rgb.size

    # Build a mask: pixels NOT white (i.e., content)
    bg = Image.new("RGB", rgb.size, (255, 255, 255))
    diff = ImageChops.difference(rgb, bg)

    # Threshold: any channel > threshold means content
    r, g, b = diff.split()
    mask = r.point(lambda x: 255 if x > (255 - threshold) else 0)

    bbox = mask.getbbox()
    if bbox is None:
        return img  # fully white — skip

    left, top, right, bottom = bbox
    crop_w = right - left
    crop_h = bottom - top

    # Skip if cropped result is too small (thin strips, icons)
    if crop_w < 80 or crop_h < 80:
        return img

    # Check margins as fraction of image size
    margin_left   = left / w
    margin_top    = top / h
    margin_right  = (w - right) / w
    margin_bottom = (h - bottom) / h

    max_margin = max(margin_left, margin_top, margin_right, margin_bottom)
    if max_margin < min_margin_pct:
        return img  # margins too small, not worth cropping

    return img.crop(bbox)


def process(thumb_dir, dry_run=False):
    thumb_dir = Path(thumb_dir)
    files = sorted(thumb_dir.glob("*.jpg")) + sorted(thumb_dir.glob("*.png"))
    trimmed = 0
    skipped = 0

    for f in files:
        img = Image.open(f)
        orig_size = img.size
        trimmed_img = trim_white(img)

        if trimmed_img.size == orig_size:
            skipped += 1
            continue

        w_orig, h_orig = orig_size
        w_new, h_new = trimmed_img.size
        print(f"  {f.name}: {w_orig}x{h_orig} → {w_new}x{h_new}")

        if not dry_run:
            # Resize to 400px wide after trimming
            aspect = h_new / w_new
            new_w = 400
            new_h = int(new_w * aspect)
            resized = trimmed_img.resize((new_w, new_h), Image.LANCZOS)
            resized.save(f, quality=88, optimize=True)
            trimmed += 1
        else:
            trimmed += 1

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Trimmed: {trimmed}  Skipped (no margin): {skipped}")
    return trimmed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("brand", help="brand folder name, e.g. gaggenau")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    thumb_dir = BASE / "thumbs" / args.brand
    if not thumb_dir.exists():
        print(f"Not found: {thumb_dir}")
        sys.exit(1)

    print(f"Scanning {thumb_dir} ...")
    process(thumb_dir, dry_run=args.dry_run)
