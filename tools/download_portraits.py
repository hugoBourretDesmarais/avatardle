#!/usr/bin/env python3
"""Download character portraits (280px-wide thumbnails) into public/portraits/."""
import json
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
DEST = HERE.parent / "public" / "portraits"
DEST.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "AvatarDleFanProject/1.0 (personal, low-volume)"}


def slugify(name):
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()


def thumb_url(url, width=280):
    # .../X.png/revision/latest?cb=... -> .../X.png/revision/latest/scale-to-width-down/280?cb=...
    if "/revision/latest" in url:
        return url.replace("/revision/latest", f"/revision/latest/scale-to-width-down/{width}")
    return url


def main():
    recs = json.loads((HERE / "out" / "characters.draft.json").read_text())
    mapping = {}
    failed = []
    for r in recs:
        name = r["requested"]
        url = r.get("image")
        slug = slugify(name)
        if not url:
            failed.append(name)
            continue
        ext = ".png" if ".png" in url.lower() else ".jpg"
        out = DEST / f"{slug}{ext}"
        mapping[name] = out.name
        if out.exists() and out.stat().st_size > 500:
            continue
        data = None
        # the thumbnailer 503s now and then; the original is always there
        for attempt, u in enumerate((thumb_url(url), thumb_url(url), url)):
            try:
                with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as resp:
                    data = resp.read()
                break
            except Exception as e:
                time.sleep(1.5 * (attempt + 1))
                err = e
        if data is None:
            print(f"FAIL {name}: {err}")
            failed.append(name)
            continue
        out.write_bytes(data)
        time.sleep(0.25)
    (HERE / "out" / "portraits.json").write_text(json.dumps(mapping, indent=1, ensure_ascii=False))
    print(f"{len(mapping)} portraits, {len(failed)} failed: {failed}")


if __name__ == "__main__":
    main()
