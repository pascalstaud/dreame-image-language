import os, json, re
from pathlib import Path

BASE = Path(__file__).parent
THUMBS = BASE / "thumbs"

BRANDS = {
    "dreame":   {"color": "#0057FF", "label": "Dreame",   "group": "primary"},
    "roborock": {"color": "#CC0000", "label": "Roborock", "group": "robot-vacuum"},
    "dyson":    {"color": "#DC6B00", "label": "Dyson",    "group": "premium-tech"},
    "samsung":  {"color": "#1428A0", "label": "Samsung",  "group": "smart-home"},
    "xiaomi":   {"color": "#FF6900", "label": "Xiaomi",   "group": "robot-vacuum"},
    "haier":    {"color": "#003087", "label": "Haier",    "group": "appliances"},
    "vipp":     {"color": "#2C2C2C", "label": "VIPP",     "group": "premium-design"},
    "lg":       {"color": "#A50034", "label": "LG",       "group": "appliances"},
    "hisense":  {"color": "#003DA5", "label": "Hisense",  "group": "appliances"},
    "gaggenau": {"color": "#1A1A1A", "label": "Gaggenau", "group": "premium-design"},
    "apple":    {"color": "#555555", "label": "Apple",    "group": "premium-design"},
    "basalte":  {"color": "#8A7E72", "label": "Basalte",  "group": "smart-home"},
    "lutron":   {"color": "#D4A017", "label": "Lutron",   "group": "smart-home"},
    "vzug":     {"color": "#C8102E", "label": "V-ZUG",    "group": "premium-design"},
    "philips":  {"color": "#0050A0", "label": "Philips",  "group": "appliances"},
}

CHANNELS = ["website", "press", "instagram", "youtube", "facebook", "ads"]

# Dreame product model detection
MODEL_MAP = {
    "dreame": [
        # Robot Vacuums — X Series (most specific first)
        ("X60 Max Ultra", r"x60.?max.?ultra|x60maxultra"),
        ("X60 Max",       r"x60.?max(?!.ultra)"),
        ("X60",           r"\bx60\b"),
        ("X40 Ultra",     r"x40.?ultra"),
        ("X40",           r"\bx40\b"),
        ("X30 Ultra",     r"x30.?ultra"),
        ("X30",           r"\bx30\b"),
        # Robot Vacuums — L Series
        ("L50 Ultra",     r"l50.?ultra"),
        ("L50",           r"\bl50\b"),
        ("L40 Ultra",     r"l40.?ultra"),
        ("L40s",          r"\bl40s\b"),
        ("L40",           r"\bl40\b"),
        ("L20 Ultra",     r"l20.?ultra"),
        ("L20",           r"\bl20\b"),
        ("L10s Ultra",    r"l10s.?ultra"),
        ("L10s",          r"\bl10s\b"),
        # Robot Vacuums — D Series
        ("D30 Ultra",     r"d30.?ultra"),
        ("D30",           r"\bd30\b"),
        ("D20 Pro Plus",  r"d20.?pro.?plus"),
        ("D20 Plus",      r"d20.?plus"),
        ("D20",           r"\bd20\b"),
        ("D10 Plus",      r"d10.?plus"),
        ("D10",           r"\bd10\b"),
        ("D9",            r"\bd9\b"),
        # Special series
        ("Aqua10",        r"aqua.?10"),
        ("Matrix10",      r"matrix.?10"),
        ("Cyber10",       r"cyber.?10"),
        ("Cyber X",       r"cyber.?x"),
        # Cordless / Wet-Dry
        ("H15 Pro",       r"h15.?pro"),
        ("H15",           r"\bh15\b"),
        ("H14 Pro",       r"h14.?pro"),
        ("H14",           r"\bh14\b"),
        ("H13 Pro",       r"h13.?pro"),
        ("H13",           r"\bh13\b"),
        ("Z30",           r"\bz30\b"),
        ("Z20",           r"\bz20\b"),
        # Hair care
        ("Hair Gleam",    r"hair.?gleam"),
        ("Hair Artist",   r"hair.?artist"),
        ("FantasyFlux",   r"fantasyflux|fantasy.?flux"),
    ],
    "roborock": [
        ("S8 MaxV Ultra", r"s8.?maxv.?ultra"),
        ("S8 Pro Ultra",  r"s8.?pro.?ultra"),
        ("S8 Ultra",      r"s8.?ultra"),
        ("S8",            r"\bs8\b"),
        ("Q Revo MaxV",   r"q.?revo.?maxv"),
        ("Q Revo",        r"q.?revo"),
        ("P10 Pro Ultra", r"p10.?pro.?ultra"),
        ("Saros Z70",     r"saros.?z70"),
        ("Saros 10",      r"saros.?10"),
        ("Saros",         r"\bsaros\b"),
    ],
    "dyson": [
        ("Gen5 Detect",   r"gen5.?detect"),
        ("V15 Detect",    r"v15.?detect"),
        ("V12 Detect",    r"v12.?detect"),
        ("V8",            r"\bv8\b"),
        ("360 Vis Nav",   r"360.?vis.?nav"),
        ("Airsense",      r"airsense"),
        ("Airwrap",       r"airwrap"),
        ("Supersonic",    r"supersonic"),
        ("Airstrait",     r"airstrait"),
    ],
}

SEGMENT_KEYWORDS = {
    "robot-vacuum": ["robot", "vacuum", "robovac", "x60", "x40", "x30", "l50", "l40", "l20", "l10", "d30", "d20", "d10", "d9", "aqua", "matrix", "cyber", "saros", "360"],
    "cordless":     ["cordless", "stick", "z30", "z20", "h15", "h14", "h13", "v15", "v12", "v8", "gen5"],
    "hair-care":    ["hair", "airwrap", "supersonic", "airstrait", "gleam", "artist", "fantasyflux"],
    "smart-home":   ["smart", "home", "ecosystem", "iot", "hub", "control", "app", "automation"],
    "kitchen":      ["kitchen", "cooking", "oven", "fridge", "washer", "dishwasher", "appliance"],
    "lifestyle":    ["lifestyle", "family", "home", "living", "interior", "room", "clean"],
}

CONTENT_KEYWORDS = {
    "product-studio": ["studio", "packshot", "white", "clean", "product", "360"],
    "product-lifestyle": ["lifestyle", "room", "home", "living", "interior", "kitchen", "floor"],
    "action":    ["action", "cleaning", "working", "mop", "suction", "dynamic"],
    "detail":    ["detail", "close", "macro", "feature", "sensor", "brush"],
    "campaign":  ["campaign", "hero", "banner", "cover", "key-visual", "kv"],
    "social":    ["instagram", "facebook", "tiktok", "reel", "story"],
}

def detect_models(brand, text):
    found = []
    if brand not in MODEL_MAP:
        return found
    text = text.lower()
    for name, pattern in MODEL_MAP[brand]:
        if re.search(pattern, text):
            found.append(name)
    return found

def classify_segment(filename):
    fn = filename.lower()
    for seg, kws in SEGMENT_KEYWORDS.items():
        for kw in kws:
            if kw in fn:
                return seg
    return "general"

def classify_content(filename):
    fn = filename.lower()
    for ct, kws in CONTENT_KEYWORDS.items():
        for kw in kws:
            if kw in fn:
                return ct
    return "product"

def build_instagram_meta_lookup(brand_dir, brand):
    """Read gallery-dl .json sidecar files for metadata enrichment."""
    meta = {}
    skip = {'data.json'}
    for jf in Path(brand_dir).rglob("*.json"):
        if jf.name in skip:
            continue
        try:
            d = json.loads(jf.read_text(encoding='utf-8', errors='ignore'))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        caption = str(d.get('description') or d.get('caption') or '')
        tags = ' '.join(d.get('tags') or [])
        text = (caption + ' ' + tags).lower().replace('#', '')
        models = detect_models(brand, text)
        likes = int(d.get('likes') or d.get('like_count') or 0)
        date = str(d.get('post_date') or d.get('taken_at') or d.get('date') or '')[:10]
        stem = jf.stem  # filename without .json
        meta[stem] = {'models': models, 'likes': likes, 'date': date}
    return meta

data = []
valid_ext = {'.jpg', '.jpeg', '.png', '.webp'}

for brand in BRANDS:
    brand_dir = BASE / brand
    if not brand_dir.is_dir():
        continue
    ig_meta = build_instagram_meta_lookup(brand_dir, brand)
    for root, dirs, files in os.walk(brand_dir):
        rel = Path(root).relative_to(BASE)
        parts = rel.parts
        channel = parts[1] if len(parts) > 1 else "website"
        for f in sorted(files):
            ext = Path(f).suffix.lower()
            if ext not in valid_ext:
                continue
            full = Path(root) / f
            sz = full.stat().st_size
            if sz < 8000:
                continue
            thumb_rel = f"thumbs/{brand}/{f}"
            thumb_exists = (BASE / thumb_rel).exists()
            entry = {
                "brand": brand,
                "channel": channel,
                "segment": classify_segment(f),
                "content_type": classify_content(f),
                "file": str(full.relative_to(BASE)),
                "thumb": thumb_rel if thumb_exists else str(full.relative_to(BASE)),
                "filename": f,
                "likes": 0,
                "date": "",
                "is_video": False,
            }
            # Enrich from Instagram metadata
            stem = Path(f).stem
            if stem in ig_meta:
                m = ig_meta[stem]
                if m['models']:
                    entry['models'] = m['models']
                if m['likes'] > 0:
                    entry['likes'] = m['likes']
                if m['date']:
                    entry['date'] = m['date']
            # Filename-based model detection
            models_fn = detect_models(brand, f)
            if models_fn:
                existing = set(entry.get('models') or [])
                existing.update(models_fn)
                entry['models'] = list(existing)
            # Strip empty optional fields
            for k in ['models', 'likes', 'date']:
                v = entry.get(k)
                if not v:
                    entry.pop(k, None)
            data.append(entry)

out_path = BASE / "data.json"
with open(out_path, 'w') as fh:
    json.dump(data, fh, separators=(',', ':'))

# Stats
stats = {}
for brand in BRANDS:
    imgs = [d for d in data if d['brand'] == brand]
    ch_counts = {}
    for d in imgs:
        ch_counts[d['channel']] = ch_counts.get(d['channel'], 0) + 1
    stats[brand] = {'total': len(imgs), 'channels': ch_counts}

print(f"Total images: {len(data)}")
for brand, s in stats.items():
    if s['total'] > 0:
        print(f"  {BRANDS[brand]['label']:12s} {s['total']:4d}  {s['channels']}")
print(f"Written to {out_path}")
