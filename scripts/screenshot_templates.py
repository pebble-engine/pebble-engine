"""Take a 1280x800 @2x screenshot of each exported cinematic_* template
served from the live engine at /preview-template/<id>/. Writes PNGs into
ui/v3/public/templates-preview/<id>.png — the gallery card images.

Engine must be running at ENGINE_BASE (default http://127.0.0.1:8000)
and each template must have been built via `python -m pebble.templates.export`.

Usage:
    python scripts/screenshot_templates.py cinematic_hero
    python scripts/screenshot_templates.py --all
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

from pebble.templates.export import list_exportable_template_ids

REPO_ROOT     = Path(__file__).resolve().parents[1]
PREVIEWS_DIR  = REPO_ROOT / "ui" / "v3" / "public" / "templates-preview"
ENGINE_BASE   = os.environ.get("PEBBLE_ENGINE_BASE", "http://127.0.0.1:8000").rstrip("/")


def screenshot(template_id: str) -> Path:
    url         = f"{ENGINE_BASE}/preview-template/{template_id}/"
    base_prefix = f"/preview-template/{template_id}"
    dest        = PREVIEWS_DIR / f"{template_id}.png"
    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

    def handle_route(route):
        """Reroute root-relative asset requests (e.g. /hero.jpg) to the
        correct sub-path (/preview-template/<id>/hero.jpg) so images load.

        The Next.js static export uses absolute-root paths for public/
        assets, which are 404 when served under a sub-path on the engine.
        We intercept and fix them without touching the engine code.
        """
        req_url = route.request.url
        parsed  = urlparse(req_url)
        path    = parsed.path

        # Only intercept root-level non-Next-internal paths
        if (
            not path.startswith("/preview-template/")
            and not path.startswith("/_next/")
            and path not in ("/", "")
        ):
            new_url = f"{ENGINE_BASE}{base_prefix}{path}"
            route.continue_(url=new_url)
        else:
            route.continue_()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=2,
        )
        page = ctx.new_page()
        page.route("**/*", handle_route)

        print(f"[{template_id}] navigating {url}", flush=True)
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        try:
            page.wait_for_load_state("networkidle", timeout=8_000)
        except Exception:
            pass
        # Framer Motion entrance animations + hero image fade-in settle in ~600ms.
        page.wait_for_timeout(800)
        page.screenshot(path=str(dest), full_page=False)
        browser.close()

    size = dest.stat().st_size
    print(f"[{template_id}] wrote {dest.relative_to(REPO_ROOT)} ({size:,} bytes)")
    if size < 50_000:
        print(
            f"  WARNING: {dest.name} is suspiciously small — preview may have failed to load",
            file=sys.stderr,
        )
    return dest


def _main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("template_id", nargs="?")
    p.add_argument(
        "--all",
        action="store_true",
        help="Screenshot every cinematic_* registry entry",
    )
    args = p.parse_args()
    if args.all:
        ids = [i for i in list_exportable_template_ids() if i.startswith("cinematic_")]
    elif args.template_id:
        ids = [args.template_id]
    else:
        p.error("pass a template_id or --all")
        return 2

    failures: list[str] = []
    for tid in ids:
        try:
            screenshot(tid)
        except Exception as e:
            print(f"[{tid}] FAIL: {e}", file=sys.stderr)
            failures.append(tid)

    if failures:
        print(f"\n{len(failures)} failed: {', '.join(failures)}", file=sys.stderr)
        return 1
    print(f"\nScreenshotted {len(ids)} template(s)")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
