"""One-shot: wait for boutique_brokerage (:3067) + honest_garage (:3068)
to become ready, then capture screenshots to ui/v3/public/templates-preview/.

The dev servers themselves are booted separately (e.g. via background
`cmd /c npx next dev -p PORT`) and stay running. This script is purely
the poll + Playwright phase.
"""
from __future__ import annotations
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PREVIEW_DIR = REPO / "ui" / "v3" / "public" / "templates-preview"

TARGETS = {
    "boutique_brokerage": 3067,
    "honest_garage": 3068,
}


def wait_ready(port: int, timeout_s: int = 180) -> bool:
    end = time.time() + timeout_s
    while time.time() < end:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def main():
    print("Waiting for boutique_brokerage + honest_garage dev servers...")
    ready = {}
    for tid, port in TARGETS.items():
        if wait_ready(port):
            ready[tid] = port
            print(f"  ready: {tid:25s} :{port}")
        else:
            print(f"  TIMEOUT: {tid:25s} :{port}")

    if not ready:
        print("Nothing ready, bailing.")
        return

    print(f"\nCapturing {len(ready)} screenshots...")
    from playwright.sync_api import sync_playwright

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
        )
        for tid, port in ready.items():
            try:
                page = ctx.new_page()
                page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=20000)
                try:
                    page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                page.wait_for_timeout(1500)
                target = PREVIEW_DIR / f"{tid}.png"
                page.screenshot(path=str(target), full_page=False)
                kb = target.stat().st_size // 1024
                print(f"  [ok]   {tid:25s} -> {target.name} ({kb} KB)")
                page.close()
            except Exception as e:
                print(f"  [fail] {tid:25s} fail: {e}")
        browser.close()


if __name__ == "__main__":
    main()
