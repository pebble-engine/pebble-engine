#!/usr/bin/env python3
"""Promote a built example from output/ to pebble/examples/ + register it.

Usage:
    python scripts/promote_example.py <slug> --vibe trade-pro

Mechanics:
  1. Copy output/<slug>/site → pebble/examples/<slug>/site (excludes
     node_modules/.next/.turbo/dist/build — same set as the runtime
     example cloner in pebble/server/examples.py).
  2. Copy brief.json + build_meta.json across (used for hero_image and
     section counts).
  3. Capture a Playwright homepage screenshot → ui/v3/public/templates-preview/<slug>.png
     (degrades gracefully if Playwright unavailable).
  4. Append/replace an entry in pebble/example_gallery.json:
     {slug, name, industry, vibe, hero_image, sections, source_dir, kind}.

billable: false — this is operator tooling.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parent.parent

# Module-level so tests can monkeypatch them.
OUTPUT_DIR = _REPO_ROOT / "output"
EXAMPLES_DIR = _REPO_ROOT / "pebble" / "examples"
MANIFEST = _REPO_ROOT / "pebble" / "example_gallery.json"
THUMB_DIR = _REPO_ROOT / "ui" / "v3" / "public" / "templates-preview"

_SKIP_NAMES = frozenset({"node_modules", ".next", ".turbo", "dist", "build"})


def _copy_site(src_dir: Path, dst_dir: Path) -> int:
    """Copy site/ verbatim, skipping build artifacts. Mirror examples.py."""
    written = 0
    for src in src_dir.rglob("*"):
        if any(part in _SKIP_NAMES for part in src.parts):
            continue
        if src.is_dir():
            continue
        rel = src.relative_to(src_dir)
        dst = dst_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        written += 1
    return written


def capture_thumbnail(slug: str, site_dir: Path) -> str:
    """Capture homepage Playwright screenshot. Returns the relative path under
    ui/v3/public/ for embedding in the manifest. Degrades to '' on any error.
    """
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        return ""
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    out = THUMB_DIR / f"{slug}.png"
    url = f"http://127.0.0.1:8000/preview/{slug}/"
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True)
            pg = b.new_page(viewport={"width": 1440, "height": 900})
            pg.goto(url, wait_until="networkidle", timeout=90000)
            time.sleep(2)
            pg.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": 1440, "height": 900})
            b.close()
        return f"templates-preview/{slug}.png"
    except Exception as exc:
        print(f"[promote] thumbnail capture failed: {exc}", file=sys.stderr)
        return ""


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _resolve_hero_image(site_dir: Path, brief: dict, thumb_rel: str) -> str:
    """Prefer thumbnail; otherwise dig the first pexels URL out of Section00.tsx."""
    if thumb_rel:
        return thumb_rel
    sec0 = site_dir / "components" / "sections" / "Section00.tsx"
    if sec0.exists():
        import re
        m = re.search(r'https://images\.pexels\.com/[^"\'\s]+', sec0.read_text(encoding="utf-8"))
        if m:
            return m.group(0)
    return brief.get("hero_image", "") or ""


def _count_sections(meta: dict, site_dir: Path) -> int:
    picks = meta.get("block_picks") or []
    if picks:
        return len(picks)
    sections_dir = site_dir / "components" / "sections"
    if sections_dir.exists():
        return sum(1 for _ in sections_dir.glob("Section*.tsx"))
    return 0


def promote(slug: str, *, vibe: str) -> dict:
    """Promote output/<slug>/ into pebble/examples/<slug>/ + register.

    Idempotent: re-promoting the same slug replaces the existing entry
    rather than appending a duplicate.
    """
    out_dir = OUTPUT_DIR / slug
    src_site = out_dir / "site"
    if not src_site.is_dir():
        raise FileNotFoundError(f"no built site to promote: {src_site}")

    dst_dir = EXAMPLES_DIR / slug
    dst_site = dst_dir / "site"
    # Clear stale copy if any (idempotency).
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    dst_dir.mkdir(parents=True)

    file_count = _copy_site(src_site, dst_site)

    brief = _read_json(out_dir / "brief.json", {})
    meta = _read_json(out_dir / "build_meta.json", {})

    if brief:
        (dst_dir / "brief.json").write_text(json.dumps(brief, indent=2), encoding="utf-8")
    if meta:
        (dst_dir / "build_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    thumb_rel = capture_thumbnail(slug, dst_site)
    hero_image = _resolve_hero_image(dst_site, brief, thumb_rel)
    sections = _count_sections(meta, dst_site)
    source_dir = f"pebble/examples/{slug}"

    entry = {
        "slug": slug,
        "name": brief.get("business_name") or slug,
        "industry": brief.get("industry") or "",
        "vibe": vibe,
        "hero_image": hero_image,
        "sections": sections,
        "source_dir": source_dir,
        "kind": "example_build",
    }

    manifest = _read_json(MANIFEST, {"schema_version": "1.0", "examples": []})
    examples = [e for e in manifest.get("examples", []) if e.get("slug") != slug]
    examples.append(entry)
    manifest["examples"] = examples
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    return {"slug": slug, "file_count": file_count, "thumbnail": thumb_rel, "entry": entry}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug", help="build slug under output/")
    ap.add_argument("--vibe", required=True, help="vibe label for the gallery (e.g. trade-pro)")
    args = ap.parse_args(argv)

    try:
        result = promote(args.slug, vibe=args.vibe)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
