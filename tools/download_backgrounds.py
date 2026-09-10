#!/usr/bin/env python3
"""Fetch the real backdrop artwork from the Avatar wiki and encode it for the web.

The wiki has almost no widescreen stills large enough for a full-screen backdrop;
the world map is the exception, so it is the everyday background. Written as WebP
with a JPEG fallback and put first in src/data/backgrounds.json, ahead of the
painted scenes from make_backgrounds.py.
"""
import io
import json
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
DEST = HERE.parent / "public" / "backgrounds"
MANIFEST = HERE.parent / "src" / "data" / "backgrounds.json"
DEST.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "AvatarDleFanProject/1.0 (personal, low-volume)"}

# slug -> (wiki file, credit label)
SOURCES = {
    "world-map": ("Avatar world map.jpeg", "World map · Avatar Wiki"),
}

TARGET_W = 1920
TARGET_RATIO = 16 / 9


def api(params):
    q = urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request("https://avatar.fandom.com/api.php?" + q, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=60))


def main():
    from PIL import Image

    d = api({"action": "query", "titles": "|".join(f"File:{v[0]}" for v in SOURCES.values()),
             "prop": "imageinfo", "iiprop": "url"})
    urls = {p["title"][5:]: p["imageinfo"][0]["url"] for p in d["query"]["pages"].values() if p.get("imageinfo")}

    real = []
    for slug, (file, label) in SOURCES.items():
        url = urls.get(file)
        if not url:
            print(f"SKIP {slug}: no url for {file}")
            continue
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180).read()
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        w, h = im.size
        if w / h > TARGET_RATIO:
            new_w = int(h * TARGET_RATIO)
            im = im.crop(((w - new_w) // 2, 0, (w - new_w) // 2 + new_w, h))
        else:
            new_h = int(w / TARGET_RATIO)
            top = (h - new_h) // 2
            im = im.crop((0, top, w, top + new_h))
        im = im.resize((TARGET_W, int(TARGET_W / TARGET_RATIO)), Image.LANCZOS)
        jpg = DEST / f"{slug}.jpg"
        im.save(jpg, "JPEG", quality=84, optimize=True, progressive=True)
        webp = DEST / f"{slug}.webp"
        subprocess.run(["cwebp", "-q", "78", "-quiet", str(jpg), "-o", str(webp)], check=True)
        real.append({"slug": slug, "label": label, "file": file})
        print(f"{slug:12} jpg {jpg.stat().st_size // 1024:4d}KB   webp {webp.stat().st_size // 1024:4d}KB")

    painted = [b for b in json.loads(MANIFEST.read_text()) if b["slug"] not in SOURCES] if MANIFEST.exists() else []
    MANIFEST.write_text(json.dumps(real + painted, indent=1))
    print(f"{len(real)} real + {len(painted)} painted backdrops")


if __name__ == "__main__":
    main()
