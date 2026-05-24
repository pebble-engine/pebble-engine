"""Download industry-specific photos from Pexels into a template's public/ dir.

Usage:
    python scripts/fetch_template_images.py cinematic_plumber \\
        --hero "plumber pipe wrench" \\
        --gallery "plumbing service" \\
        --count 8

Files written:
    pebble/templates/<template_id>/public/hero.jpg     (1st hero-keyword result)
    pebble/templates/<template_id>/public/about.jpg    (2nd hero-keyword result)
    pebble/templates/<template_id>/public/gallery/01.jpg .. NN.jpg

Requires PEXELS_API_KEY in the environment (already in repo .env).

Used by Tasks 7-12 of the cinematic-skin-differentiation plan to fetch
industry-specific photo packs per skin.
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.request
from pathlib import Path

# Ensure repo root is on sys.path so pebble package resolves even when the
# script is run from any working directory.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv  # noqa: E402  (after sys.path fixup)

load_dotenv(REPO_ROOT / ".env")

from pebble.image_fallback import _fetch_pexels_urls_for_keyword  # noqa: E402

_DOWNLOAD_TIMEOUT_S = 30


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "PebbleTemplateBuilder/1.0"})
    with urllib.request.urlopen(req, timeout=_DOWNLOAD_TIMEOUT_S) as resp, open(dest, "wb") as out:
        out.write(resp.read())
    print(f"  wrote {dest.relative_to(REPO_ROOT)} ({dest.stat().st_size:,} bytes)")


def fetch_images(template_id: str, hero_kw: str, gallery_kw: str, gallery_count: int = 8) -> None:
    """Fetch and save the full image set for one template."""
    pub = REPO_ROOT / "pebble" / "templates" / template_id / "public"
    if not pub.exists():
        raise FileNotFoundError(f"{pub} — template's public dir doesn't exist")

    print(f"[{template_id}] fetching hero ({hero_kw!r})")
    hero_urls = _fetch_pexels_urls_for_keyword(hero_kw, count=4)
    if not hero_urls:
        raise RuntimeError(f"no Pexels results for hero keyword {hero_kw!r}")
    _download(hero_urls[0], pub / "hero.jpg")
    _download(hero_urls[1] if len(hero_urls) > 1 else hero_urls[0], pub / "about.jpg")

    print(f"[{template_id}] fetching {gallery_count} gallery images ({gallery_kw!r})")
    gallery_urls = _fetch_pexels_urls_for_keyword(gallery_kw, count=gallery_count + 4)
    if len(gallery_urls) < gallery_count:
        print(
            f"  warning: only {len(gallery_urls)} gallery results — padding from hero pool",
            file=sys.stderr,
        )
        gallery_urls = (gallery_urls + hero_urls)[:gallery_count]
    for i, url in enumerate(gallery_urls[:gallery_count], 1):
        _download(url, pub / "gallery" / f"{i:02d}.jpg")


def _main() -> int:
    p = argparse.ArgumentParser(description="Fetch Pexels images into a template's public/ dir")
    p.add_argument("template_id", help="e.g. cinematic_plumber")
    p.add_argument("--hero", required=True, help="Pexels search keyword for the hero + about photos")
    p.add_argument("--gallery", required=True, help="Pexels search keyword for the gallery photos")
    p.add_argument("--count", type=int, default=8, help="number of gallery images to fetch (default: 8)")
    args = p.parse_args()
    if not os.environ.get("PEXELS_API_KEY", "").strip():
        print(
            "ERROR: PEXELS_API_KEY not set in environment. Run `python scripts/sync_env.py` first.",
            file=sys.stderr,
        )
        return 2
    try:
        fetch_images(args.template_id, args.hero, args.gallery, gallery_count=args.count)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(_main())
