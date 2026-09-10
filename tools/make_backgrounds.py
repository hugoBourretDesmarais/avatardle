#!/usr/bin/env python3
"""Paint the six rotating backdrops procedurally.

The Avatar wiki has no widescreen stills large enough for a full-screen backdrop,
so each scene is layered gradients, ridge silhouettes and grain: an impression
of a place rather than a screenshot. Written as JPEG plus WebP, like the
original pipeline, and listed in src/data/backgrounds.json.
"""
import json
import math
import random
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).parent
DEST = HERE.parent / "public" / "backgrounds"
DEST.mkdir(parents=True, exist_ok=True)
W, H = 1920, 1080


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky(stops):
    """Vertical gradient through (position, colour) stops."""
    img = np.zeros((H, W, 3), np.float32)
    ys = np.linspace(0, 1, H)
    for c in range(3):
        img[:, :, c] = np.interp(ys, [s[0] for s in stops], [s[1][c] for s in stops])[:, None]
    return img


def glow(img, cx, cy, radius, colour, strength=1.0):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / radius
    a = np.clip(1 - d, 0, 1) ** 2 * strength
    for c in range(3):
        img[:, :, c] = img[:, :, c] * (1 - a) + colour[c] * a
    return img


def ridge(rng, base, amp, freqs, phase=0.0):
    xs = np.arange(W)
    y = np.full(W, float(base))
    for i, f in enumerate(freqs):
        y += amp / (i + 1) * np.sin(xs / W * math.tau * f + phase + rng.uniform(0, math.tau))
    return y


def fill_ridge(img, y, colour, blur=0):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = [(x, int(y[x])) for x in range(0, W, 4)] + [(W, H), (0, H)]
    d.polygon(pts, fill=colour + (255,))
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(img, layer)


def to_pil(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")


def stars(img, rng, n, alpha=200):
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H * 0.55)
        r = rng.choice([0.6, 0.8, 1.2, 1.6])
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 250, 235, int(alpha * rng.uniform(0.4, 1))))
    return img


def spires(d, rng, base_y, xs, colour, scale=1.0):
    """Tiered pagoda-like towers rising from a ridge line."""
    for x in xs:
        h = rng.uniform(90, 210) * scale
        w = rng.uniform(30, 60) * scale
        y0 = base_y[int(min(max(x, 0), W - 1))]
        d.rectangle((x - w / 2, y0 - h * 0.55, x + w / 2, y0 + 10), fill=colour)
        tiers = 3
        for t in range(tiers):
            ty = y0 - h * 0.55 - t * h * 0.16
            tw = w * (1.5 - t * 0.3)
            d.polygon([(x - tw / 2, ty), (x + tw / 2, ty), (x, ty - h * 0.14)], fill=colour)
        d.polygon([(x - w * 0.18, y0 - h), (x + w * 0.18, y0 - h), (x, y0 - h - h * 0.35)], fill=colour)


def grain(img, rng, amount=10):
    arr = np.asarray(img.convert("RGB")).astype(np.float32)
    noise = rng.normal(0, amount, arr.shape[:2])[:, :, None]
    return Image.fromarray(np.clip(arr + noise, 0, 255).astype(np.uint8)).convert("RGBA")


def vignette(img):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    a = np.clip((d - 0.55) / 0.9, 0, 1) ** 1.6 * 0.55
    arr = np.asarray(img.convert("RGB")).astype(np.float32) * (1 - a[:, :, None])
    return Image.fromarray(arr.astype(np.uint8)).convert("RGBA")


def scene_air(rng):
    img = sky([(0, (250, 190, 110)), (0.45, (240, 150, 100)), (0.75, (170, 110, 120)), (1, (70, 50, 80))])
    img = glow(img, W * 0.72, H * 0.42, 520, (255, 235, 190), 0.9)
    img = glow(img, W * 0.72, H * 0.42, 130, (255, 255, 240), 1.0)
    pil = to_pil(img)
    pil = fill_ridge(pil, ridge(rng, H * 0.62, 70, [1.2, 3, 7]), (150, 90, 120), 6)
    pil = fill_ridge(pil, ridge(rng, H * 0.72, 90, [0.8, 2.4, 6]), (95, 55, 95), 3)
    peak = ridge(rng, H * 0.95, 40, [0.6, 2]) - np.clip(300 - np.abs(np.arange(W) - W * 0.34) * 0.9, 0, 300)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.polygon([(x, int(peak[x])) for x in range(0, W, 4)] + [(W, H), (0, H)], fill=(40, 24, 50, 255))
    spires(d, rng, peak, [W * 0.30, W * 0.345, W * 0.38, W * 0.27], (40, 24, 50), 1.1)
    pil = Image.alpha_composite(pil, layer)
    return pil


def scene_water(rng):
    img = sky([(0, (8, 18, 48)), (0.5, (18, 50, 100)), (0.8, (40, 95, 150)), (1, (90, 150, 190))])
    img = glow(img, W * 0.3, H * 0.28, 420, (170, 200, 240), 0.55)
    img = glow(img, W * 0.3, H * 0.28, 95, (245, 250, 255), 1.0)
    pil = stars(to_pil(img), rng, 260)
    pil = fill_ridge(pil, ridge(rng, H * 0.6, 40, [1.5, 4, 9]), (60, 110, 160), 8)
    y = ridge(rng, H * 0.78, 12, [3, 9])
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.polygon([(x, int(y[x])) for x in range(0, W, 4)] + [(W, H), (0, H)], fill=(120, 170, 210, 255))
    # tiered ice city
    for tier, (yy, hgt) in enumerate([(H * 0.78, 120), (H * 0.70, 90), (H * 0.64, 70)]):
        x0 = W * (0.36 + tier * 0.05)
        x1 = W * (0.64 - tier * 0.05)
        d.rectangle((x0, yy - hgt, x1, yy + 6), fill=(150 - tier * 12, 195 - tier * 12, 230 - tier * 8, 255))
        for bx in np.arange(x0 + 20, x1 - 20, 46):
            d.rectangle((bx, yy - hgt - rng.uniform(14, 44), bx + 22, yy - hgt + 4), fill=(170 - tier * 12, 210 - tier * 12, 240, 255))
    spires(d, rng, np.full(W, H * 0.64 - 70.0), [W * 0.5], (185, 220, 245), 0.9)
    layer = layer.filter(ImageFilter.GaussianBlur(1.2))
    pil = Image.alpha_composite(pil, layer)
    # reflection band
    pil = fill_ridge(pil, ridge(rng, H * 0.9, 6, [5, 13]), (60, 120, 170), 4)
    return pil


def scene_earth(rng):
    img = sky([(0, (120, 175, 215)), (0.4, (200, 210, 190)), (0.75, (215, 195, 140)), (1, (120, 100, 60))])
    img = glow(img, W * 0.2, H * 0.2, 400, (255, 250, 220), 0.5)
    pil = to_pil(img)
    pil = fill_ridge(pil, ridge(rng, H * 0.58, 40, [1, 3, 8]), (140, 150, 110), 8)
    pil = fill_ridge(pil, ridge(rng, H * 0.66, 30, [1.6, 5]), (105, 120, 75), 4)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # the great wall
    d.rectangle((0, H * 0.74, W, H * 0.86), fill=(85, 90, 60, 255))
    d.rectangle((0, H * 0.72, W, H * 0.745), fill=(110, 115, 80, 255))
    for bx in np.arange(0, W, 96):
        d.rectangle((bx, H * 0.70, bx + 48, H * 0.725), fill=(110, 115, 80, 255))
    # tiered city behind it
    for bx in np.arange(60, W - 60, 70):
        h = rng.uniform(30, 150)
        d.rectangle((bx, H * 0.72 - h, bx + rng.uniform(30, 60), H * 0.73), fill=(70, 85, 55, 255))
    spires(d, rng, np.full(W, H * 0.62), [W * 0.5, W * 0.54, W * 0.46], (60, 75, 48), 1.2)
    pil = Image.alpha_composite(pil, layer.filter(ImageFilter.GaussianBlur(0.8)))
    pil = fill_ridge(pil, ridge(rng, H * 0.9, 10, [2, 6]), (60, 70, 40), 0)
    return pil


def scene_fire(rng):
    img = sky([(0, (40, 10, 30)), (0.35, (150, 40, 40)), (0.65, (235, 110, 60)), (1, (60, 20, 20))])
    img = glow(img, W * 0.62, H * 0.6, 700, (255, 140, 70), 0.6)
    pil = to_pil(img)
    # comet streak
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(18):
        t = i / 18
        d.line([(W * 0.05 + t * W * 0.7, H * 0.08 + t * H * 0.22), (W * 0.05 + (t + 0.06) * W * 0.7, H * 0.08 + (t + 0.06) * H * 0.22)],
               fill=(255, 220, 170, int(40 + 180 * t)), width=int(3 + 14 * t))
    d.ellipse((W * 0.79 - 26, H * 0.31 - 26, W * 0.79 + 26, H * 0.31 + 26), fill=(255, 250, 230, 255))
    pil = Image.alpha_composite(pil, layer.filter(ImageFilter.GaussianBlur(3)))
    pil = fill_ridge(pil, ridge(rng, H * 0.62, 50, [1, 2.5, 6]), (110, 30, 35), 6)
    # crater rim with the capital's spires inside
    rim = ridge(rng, H * 0.74, 20, [2, 5]) - np.clip(160 - np.abs(np.arange(W) - W * 0.5) * 0.35, 0, 160) * -1
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.polygon([(x, int(rim[x])) for x in range(0, W, 4)] + [(W, H), (0, H)], fill=(45, 12, 20, 255))
    spires(d, rng, rim, [W * 0.5, W * 0.44, W * 0.56, W * 0.38, W * 0.62], (45, 12, 20), 1.15)
    pil = Image.alpha_composite(pil, layer)
    return pil


def scene_swamp(rng):
    img = sky([(0, (150, 175, 120)), (0.4, (120, 150, 100)), (0.75, (70, 100, 70)), (1, (30, 50, 40))])
    img = glow(img, W * 0.5, H * 0.35, 800, (200, 220, 160), 0.35)
    pil = to_pil(img)
    for depth, (base, colour, blur) in enumerate([(H * 0.55, (95, 125, 90), 10), (H * 0.62, (60, 90, 65), 5), (H * 0.7, (35, 60, 45), 1)]):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for x in np.arange(-100, W + 100, rng.uniform(140, 220)):
            tw = rng.uniform(26, 60) * (1 + depth * 0.4)
            th = rng.uniform(220, 420) * (1 + depth * 0.25)
            d.rectangle((x - tw / 2, base - th, x + tw / 2, base + 40), fill=colour + (255,))
            for k in range(4):
                ang = rng.uniform(-1.2, 1.2)
                ln = rng.uniform(80, 200)
                y0 = base - th + k * th * 0.18
                d.line([(x, y0), (x + math.sin(ang) * ln, y0 - abs(math.cos(ang)) * ln * 0.5)], fill=colour + (255,), width=int(tw * 0.25))
            d.ellipse((x - tw * 2.2, base - th - tw * 1.6, x + tw * 2.2, base - th + tw * 0.6), fill=colour + (255,))
        pil = Image.alpha_composite(pil, layer.filter(ImageFilter.GaussianBlur(blur)))
    pil = fill_ridge(pil, ridge(rng, H * 0.8, 5, [4, 11]), (45, 75, 60), 2)
    return pil


def scene_spirit(rng):
    img = sky([(0, (30, 15, 60)), (0.4, (80, 40, 120)), (0.7, (40, 110, 120)), (1, (15, 40, 55))])
    img = glow(img, W * 0.5, H * 0.45, 500, (160, 230, 220), 0.5)
    pil = stars(to_pil(img), rng, 180, 160)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(9):
        x, y = rng.uniform(100, W - 100), rng.uniform(H * 0.2, H * 0.6)
        w = rng.uniform(120, 340)
        d.ellipse((x - w / 2, y - w * 0.12, x + w / 2, y + w * 0.12), fill=(30, 20, 60, 255))
        d.polygon([(x - w * 0.35, y + w * 0.05), (x + w * 0.35, y + w * 0.05), (x, y + w * 0.5)], fill=(25, 15, 50, 255))
        for k in range(3):
            tx = x + rng.uniform(-w * 0.3, w * 0.3)
            d.line([(tx, y - w * 0.08), (tx, y - w * 0.08 - rng.uniform(40, 110))], fill=(30, 20, 60, 255), width=6)
    pil = Image.alpha_composite(pil, layer.filter(ImageFilter.GaussianBlur(1.5)))
    for _ in range(40):
        x, y = rng.uniform(0, W), rng.uniform(H * 0.3, H * 0.95)
        r = rng.uniform(3, 9)
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse((x - r, y - r, x + r, y + r), fill=(190, 255, 230, 200))
        pil = Image.alpha_composite(pil, g.filter(ImageFilter.GaussianBlur(r * 0.8)))
    pil = fill_ridge(pil, ridge(rng, H * 0.82, 30, [1, 3, 7]), (20, 30, 45), 6)
    return pil


SCENES = [
    ("southern-air-temple", "Southern Air Temple", scene_air),
    ("northern-water-tribe", "Northern Water Tribe", scene_water),
    ("ba-sing-se", "Ba Sing Se", scene_earth),
    ("fire-nation-capital", "Fire Nation Capital", scene_fire),
    ("foggy-swamp", "Foggy Swamp", scene_swamp),
    ("spirit-world", "Spirit World", scene_spirit),
]


def main():
    manifest = []
    for i, (slug, label, fn) in enumerate(SCENES):
        rng = random.Random(1000 + i)
        img = fn(rng)
        img = vignette(grain(img, np.random.default_rng(i), 7))
        jpg = DEST / f"{slug}.jpg"
        img.convert("RGB").save(jpg, "JPEG", quality=82, optimize=True, progressive=True)
        webp = DEST / f"{slug}.webp"
        subprocess.run(["cwebp", "-q", "76", "-quiet", str(jpg), "-o", str(webp)], check=True)
        manifest.append({"slug": slug, "label": label})
        print(f"{slug:22} jpg {jpg.stat().st_size // 1024:4d}KB   webp {webp.stat().st_size // 1024:4d}KB")
    (HERE.parent / "src" / "data" / "backgrounds.json").write_text(json.dumps(manifest, indent=1))


if __name__ == "__main__":
    main()
