"""Capture gallery preview screenshots for templates.

Run after instantiating templates + booting their next dev servers. Saves
to `ui/v3/public/templates-preview/<id>.png` so the /templates gallery
shows real previews instead of swatch placeholders.

Usage:
    python scripts/capture_template_previews.py service_pro=3062 luxe_beauty=3063 ink_studio=3064 ...

Each arg is `<template_id>=<port>`. Hits http://127.0.0.1:<port>/ and saves
the rendered viewport at 1440x900 @ 2x DPI.

Requires Playwright (already in the engine's deps; `playwright install chromium`
if missing).
"""
from __future__ import annotations

import sys
from pathlib import Path


def main(args: list[str]) -> int:
    if not args:
        print("Usage: python scripts/capture_template_previews.py <id>=<port> [...]")
        return 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed. Run: pip install playwright && playwright install chromium")
        return 2

    repo_root = Path(__file__).resolve().parents[1]
    out_dir = repo_root / "ui" / "v3" / "public" / "templates-preview"
    out_dir.mkdir(parents=True, exist_ok=True)

    shots: list[tuple[str, str]] = []
    for raw in args:
        if "=" not in raw:
            print(f"skip: {raw!r} (expected id=port)")
            continue
        tid, port = raw.split("=", 1)
        shots.append((tid.strip(), f"http://127.0.0.1:{port.strip()}/"))

    if not shots:
        print("no valid id=port args")
        return 1

    failures = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        for tid, url in shots:
            try:
                page = ctx.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                try:
                    page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                page.wait_for_timeout(1500)
                target = out_dir / f"{tid}.png"
                page.screenshot(path=str(target), full_page=False)
                size_kb = target.stat().st_size // 1024
                print(f"OK   {tid:20s} -> {target.name} ({size_kb} KB)")
                page.close()
            except Exception as e:
                print(f"FAIL {tid:20s}: {e}")
                failures += 1
        browser.close()
    return 0 if failures == 0 else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
