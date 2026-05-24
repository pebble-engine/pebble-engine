"""Crop the Peblet mascot PNG to a circle around his head/face.

Marc 2026-05-24: "circle crop that image of Peblet and just have his
face in the image. the square border and white background is throwing
me off."

Strategy:
  1. Open the source PNG (full-body mascot on white background).
  2. Replace near-white pixels with transparency. (Pebble brand
     assets are saved on solid white; threshold > 240 catches
     anti-aliased edges without eating the dark-grey body.)
  3. Find the bounding box of the dark pebble body (ignore the
     stick-figure arms/legs which are thin black lines that throw
     off naive bbox math). We use a connected-component-ish
     approximation: the body is the largest blob of solid dark
     pixels in the upper-center region.
  4. Apply a circular alpha mask centered on the body, sized to
     match it. Anything outside the circle goes transparent.
  5. Save out as peblet-face.png (preserve the original so we
     can always re-derive).

Run: python scripts/crop_peblet.py
Reads:  ui/v3/public/brand/peblet.png
Writes: ui/v3/public/brand/peblet-face.png
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


WORKTREE = Path(__file__).resolve().parents[1]
SRC = WORKTREE / "ui" / "v3" / "public" / "brand" / "peblet.png"
DST = WORKTREE / "ui" / "v3" / "public" / "brand" / "peblet-face.png"


def near_white(px: tuple[int, int, int, int], threshold: int = 240) -> bool:
    r, g, b, _ = px
    return r >= threshold and g >= threshold and b >= threshold


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: source not found: {SRC}", file=sys.stderr)
        return 1

    img = Image.open(SRC).convert("RGBA")
    w, h = img.size
    print(f"source: {w}x{h}")

    # 1) Background -> transparent
    pixels = img.load()
    for y in range(h):
        for x in range(w):
            if near_white(pixels[x, y]):
                pixels[x, y] = (255, 255, 255, 0)

    # 2) Find bounds of dark pixels only (the body), ignoring the
    #    thin arms/legs by requiring a minimum alpha AND a "darkness"
    #    threshold (avg RGB < 100). The arms are pure black thin
    #    lines so they DO show up, but using a minimum-density check
    #    excludes single-pixel lines.
    #
    #    Trick: count dark pixels per row + per column. Body rows
    #    have many dark pixels; arm/leg lines have very few. We pick
    #    the inner range where dark-pixel density > 5% of the image
    #    width (rows) / height (cols).
    is_dark = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a > 0 and (r + g + b) / 3 < 100:
                is_dark[y][x] = True

    row_density = [sum(is_dark[y]) for y in range(h)]
    col_density = [sum(is_dark[y][x] for y in range(h)) for x in range(w)]

    min_row_dark = max(w * 0.05, 5)   # row counts as "body" if >5% dark
    min_col_dark = max(h * 0.05, 5)

    body_rows = [y for y, d in enumerate(row_density) if d > min_row_dark]
    body_cols = [x for x, d in enumerate(col_density) if d > min_col_dark]

    if not body_rows or not body_cols:
        print("ERROR: could not detect body bounds", file=sys.stderr)
        return 1

    top, bottom = body_rows[0], body_rows[-1]
    left, right = body_cols[0], body_cols[-1]
    body_w = right - left
    body_h = bottom - top
    cx = (left + right) // 2
    # Center the circle on the FACE, not the body's geometric center.
    # The face sits in the upper ~35% of the pebble body. Centering
    # here + a tighter radius below crops out the arms / legs and
    # leaves just the head-with-face inside the circle.
    cy = top + int(body_h * 0.35)
    print(f"body bbox: ({left},{top})->({right},{bottom})  size {body_w}x{body_h}  face_center=({cx},{cy})")

    # 3) Square crop centered on the face. Radius set so the circle
    #    encloses the rounded top of the pebble + the cheeks but
    #    clips the arms/legs. 42% of body width gives a tight portrait
    #    framing — like a profile picture, not the full character.
    radius = int(body_w * 0.42)
    crop_left   = max(cx - radius, 0)
    crop_top    = max(cy - radius, 0)
    crop_right  = min(cx + radius, w)
    crop_bottom = min(cy + radius, h)
    # Keep it square — if we hit an edge, shrink radius rather than
    # stretch.
    side = min(crop_right - crop_left, crop_bottom - crop_top)
    crop_left   = cx - side // 2
    crop_top    = cy - side // 2
    crop_right  = crop_left + side
    crop_bottom = crop_top + side
    print(f"square crop: ({crop_left},{crop_top})->({crop_right},{crop_bottom})  side={side}")

    cropped = img.crop((crop_left, crop_top, crop_right, crop_bottom))

    # 4) Circular alpha mask. Anything outside the inscribed circle
    #    goes fully transparent.
    mask = Image.new("L", cropped.size, 0)
    from PIL import ImageDraw
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, side - 1, side - 1), fill=255)

    # Compose: keep existing alpha (from background removal) AND the
    # circular mask. Multiply the two so a pixel that was transparent
    # before stays transparent, and a pixel inside the circle keeps
    # whatever alpha it had.
    r, g, b, a = cropped.split()
    new_alpha = Image.new("L", cropped.size, 0)
    for y in range(cropped.size[1]):
        for x in range(cropped.size[0]):
            new_alpha.putpixel((x, y), min(a.getpixel((x, y)), mask.getpixel((x, y))))
    cropped.putalpha(new_alpha)

    # 5) Save
    DST.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(DST, format="PNG", optimize=True)
    out_size = DST.stat().st_size
    print(f"wrote: {DST}  ({cropped.size[0]}x{cropped.size[1]}, {out_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
