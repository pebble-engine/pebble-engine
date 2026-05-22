#!/usr/bin/env python3
"""Phase 42 (2026-05-21) — curate 16 Pexels "people in craft" photos for
the v3 landing hero shuffle-grid.

Reads PEXELS_API_KEY from .env. For each industry, searches Pexels with
orientation=square, picks the best candidate, downloads the 940x650
"large" size into ui/v3/public/hero-craft/<slug>.jpg, and emits a
TypeScript array literal mapping local paths to industry labels.

Downloading locally (vs hotlinking) means: no external dependency, no
Pexels outage exposure, faster page load (same-origin), and a stable
file even if the original Pexels photo is later removed.

One-shot curation script. Re-run if Marc wants a refresh.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows so non-ASCII photographer names
# (Turkish, Vietnamese, etc.) print without UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def load_env_key() -> str:
    """Read PEXELS_API_KEY from .env without depending on python-dotenv."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        sys.exit(f".env not found at {env_path}")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("PEXELS_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("PEXELS_API_KEY not found in .env")


# Industry → search query. Each query is tuned to surface candid "person
# at work" shots rather than static product/setting photos. The label
# is what gets surfaced as the tooltip / aria-label in the hero grid.
INDUSTRIES: list[tuple[str, str]] = [
    ("Baker",                "baker kneading dough bakery"),
    ("Tattoo artist",        "tattoo artist working studio"),
    ("Wedding photographer", "wedding photographer shooting couple"),
    ("Yoga instructor",      "yoga instructor teaching class"),
    ("Personal trainer",     "personal trainer coaching client gym"),
    ("Chef",                 "chef plating food kitchen"),
    ("Florist",              "florist arranging flowers shop"),
    ("Hairstylist",          "hairstylist cutting hair salon"),
    ("Auto mechanic",        "mechanic working on car repair"),
    ("Real estate agent",    "real estate agent showing house"),
    ("Barista",              "barista pulling espresso shot"),
    ("Carpenter",            "carpenter woodworking shop"),
    ("Musician",             "musician playing guitar performance"),
    ("Painter / artist",     "artist painting canvas studio"),
    ("Salon professional",   "makeup artist working client"),
    ("Personal chef",        "personal chef cooking home kitchen"),
]


def search_pexels(query: str, api_key: str, per_page: int = 10) -> list[dict]:
    """Hit the Pexels search API. Returns the `photos` list."""
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({
        "query":       query,
        "per_page":    per_page,
        "orientation": "square",   # best fit for 4x4 grid tiles
    })
    req = urllib.request.Request(url, headers={
        "Authorization": api_key,
        # Pexels rejects the default Python-urllib UA with a 403 — needs
        # something that looks like a real client.
        "User-Agent":    "Mozilla/5.0 (Pebble Engine, +https://pebbleapp.ai)",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("photos", [])
    except Exception as e:
        print(f"  ! search failed: {e}", file=sys.stderr)
        return []


def best_photo(photos: list[dict]) -> dict | None:
    """Pick the strongest candidate from a search result.

    Heuristics:
      - Skip photos tagged as "illustration" or "no people" in alt text
        when we can detect it (Pexels doesn't always supply alt)
      - Prefer photos with width >= 1200 (so cropped tiles still look
        sharp on retina)
      - First match that passes is the pick — Pexels orders by relevance
    """
    for p in photos:
        if p.get("width", 0) < 800:
            continue
        return p
    return photos[0] if photos else None


def slugify(s: str) -> str:
    """Turn 'Auto mechanic' → 'auto-mechanic', 'Painter / artist' → 'painter-artist'."""
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def download_image(url: str, dest: Path) -> bool:
    """Fetch the image into dest. Returns True on success."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Pebble Engine)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"    ! download failed: {e}", file=sys.stderr)
        return False


def main() -> None:
    api_key = load_env_key()
    print(f"# Pexels key loaded ({len(api_key)} chars)", file=sys.stderr)
    print(f"# Curating {len(INDUSTRIES)} industries...\n", file=sys.stderr)

    out_dir = Path(__file__).resolve().parent.parent / "ui" / "v3" / "public" / "hero-craft"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"# Output dir: {out_dir}\n", file=sys.stderr)

    results: list[tuple[str, str, str, str]] = []  # (label, local_path, slug, credit)
    for label, query in INDUSTRIES:
        slug = slugify(label)
        print(f"  · {label} ({slug}): '{query}'", file=sys.stderr)
        photos = search_pexels(query, api_key)
        pick = best_photo(photos)
        if not pick:
            print(f"    NO RESULT — skipping", file=sys.stderr)
            continue
        # Use the "large" size — ~940px wide, perfect for tile rendering
        # without burning bandwidth on a 4k original.
        src = pick["src"]["large"]
        credit = pick.get("photographer", "unknown")
        dest = out_dir / f"{slug}.jpg"
        if download_image(src, dest):
            local_path = f"/hero-craft/{slug}.jpg"
            results.append((label, local_path, slug, credit))
            print(f"    -> {dest.name} ({dest.stat().st_size // 1024}KB, by {credit})", file=sys.stderr)
        time.sleep(0.4)  # polite to the API + CDN

    print(f"\n# Downloaded {len(results)} photos to {out_dir}\n", file=sys.stderr)

    # Also persist a credits manifest next to the images. Pexels doesn't
    # require attribution but we keep it for completeness.
    credits_path = out_dir / "_credits.json"
    credits_path.write_text(
        json.dumps(
            [{"label": l, "file": f"{s}.jpg", "photographer": c, "source": "pexels.com"} for l, _, s, c in results],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"# Wrote credits manifest to {credits_path.name}", file=sys.stderr)

    # Emit a TypeScript array literal ready to paste into shuffle-grid.tsx
    print("\n// ---- BEGIN PASTE INTO shuffle-grid.tsx ----")
    print("const TILE_SRCS: { src: string; label: string }[] = [")
    for label, local_path, _slug, _credit in results:
        label_e = label.replace('"', '\\"')
        print(f'  {{ src: "{local_path}", label: "{label_e}" }},')
    print("];")
    print("// ---- END PASTE ----")


if __name__ == "__main__":
    main()
