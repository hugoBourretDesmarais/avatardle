#!/usr/bin/env python3
"""Generate the tileable surface textures used by the wordmark and panels.

Procedural rather than stock art: it stays tiny, tiles seamlessly, and can be
re-tuned without re-sourcing anything.
"""
import numpy as np
from PIL import Image, ImageFilter
from pathlib import Path

OUT = Path(__file__).parent.parent / "public" / "textures"
OUT.mkdir(parents=True, exist_ok=True)
SIZE = 512
rng = np.random.default_rng(20260907)


def octave(size, freq):
    """One octave of value noise, wrapped so the tile is seamless."""
    small = rng.random((freq, freq))
    tile = np.tile(small, (2, 2))  # wrap by sampling from a doubled field
    img = Image.fromarray((tile * 255).astype(np.uint8)).resize(
        (size * 2, size * 2), Image.BICUBIC)
    return np.asarray(img, dtype=np.float32)[:size, :size] / 255.0


def fractal(size, octaves=5, base=4):
    out = np.zeros((size, size), np.float32)
    amp, total = 1.0, 0.0
    for i in range(octaves):
        out += octave(size, base * 2 ** i) * amp
        total += amp
        amp *= 0.55
    return out / total


def scratches(size, count=90):
    """Fine directional wear, the thing that reads as 'used' at small sizes."""
    layer = np.zeros((size, size), np.float32)
    for _ in range(count):
        x0, y0 = rng.integers(0, size, 2)
        length = rng.integers(size // 8, size // 2)
        ang = rng.normal(0.35, 0.5)
        dx, dy = np.cos(ang), np.sin(ang)
        strength = rng.uniform(0.25, 1.0)
        for t in range(int(length)):
            x = int(x0 + dx * t) % size
            y = int(y0 + dy * t) % size
            layer[y, x] = max(layer[y, x], strength * (1 - t / length))
    return layer


def to_img(arr):
    return Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8), "L")


def main():
    # --- weathered paint: mottled, scratched, speckled -------------------
    base = fractal(SIZE, octaves=6, base=3)
    base = (base - base.min()) / (base.max() - base.min())
    blotch = fractal(SIZE, octaves=3, base=2)
    speck = rng.random((SIZE, SIZE)).astype(np.float32)
    speck = np.asarray(to_img(speck).filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255

    # Keep the low-frequency term small: broad blotches read as dirt on a
    # letterform, while fine grain plus scratches reads as wear.
    paint = 0.30 * base + 0.10 * blotch + 0.60 * speck
    paint = np.clip(paint, 0, 1)
    scr = np.asarray(to_img(scratches(SIZE, 130)).filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255
    paint = np.clip(paint + scr * 0.40, 0, 1)
    # centre on mid-grey with a gentle stretch so it modulates rather than stains
    paint = np.clip((paint - paint.mean()) * 1.5 + 0.5, 0, 1)
    # RGBA version: black where worn, white where scuffed, alpha by strength.
    # Straight alpha compositing keeps this predictable — mix-blend-mode inside
    # an isolated SVG group blends against nothing and washes colour to grey.
    signed = (paint - 0.5) * 2.0
    rgb = np.where(signed[..., None] > 0, 255, 0).repeat(3, axis=2).astype(np.uint8)
    alpha = np.clip(np.abs(signed) * 0.85, 0, 1)
    a8 = (alpha * 255).astype(np.uint8)
    a8 = (a8 // 24) * 24          # coarse alpha steps compress far better
    rgba = np.dstack([rgb, a8])
    Image.fromarray(rgba, "RGBA").resize((256, 256), Image.LANCZOS).save(
        OUT / "wear.png", optimize=True, compress_level=9)

    for f in ("wear.png",):
        print(f"{f}: {(OUT / f).stat().st_size // 1024}KB")


if __name__ == "__main__":
    main()
