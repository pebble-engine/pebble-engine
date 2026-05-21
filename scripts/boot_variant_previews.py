"""Boot dev servers for every variant template + capture screenshots.

After variant agents land + register_variants.py runs, this spins up each
variant's `next dev` on a dedicated port (3070+), waits for ready, takes a
screenshot via Playwright, and (optionally) leaves the server running so
the gallery preview pane works.

Usage:
    python scripts/boot_variant_previews.py [--kill-after]

By default leaves dev servers running. Pass --kill-after to free RAM
(screenshots are saved either way).

Port assignment is deterministic — starts at 3070 and increments in the
same order as `VARIANT_ORDER` below.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = REPO / "pebble" / "templates"
PREVIEW_DIR = REPO / "ui" / "v3" / "public" / "templates-preview"

# Deterministic port assignment — keep this list aligned with
# register_variants.py if anything is added.
VARIANT_ORDER = [
    "service_pro_navy",
    "service_pro_cream",
    "luxe_beauty_rose",
    "luxe_beauty_aubergine",
    "ink_studio_oxblood",
    "ink_studio_steel",
    "artisan_kitchen_navy",
    "artisan_kitchen_olive",
    "instructor_pro_navy",
    "instructor_pro_forest",
    "boutique_brokerage_sage",
    "boutique_brokerage_navy",
    "honest_garage_rust",
    "honest_garage_military",
]
START_PORT = 3070


def boot_one(template_id: str, port: int) -> subprocess.Popen | None:
    """Spawn `npx next dev -p PORT` in the template's directory. Returns
    Popen handle, or None if the template dir doesn't exist."""
    tmpl_dir = TEMPLATES_DIR / template_id
    if not tmpl_dir.exists():
        print(f"  skip: {template_id} (no dir)")
        return None
    log_path = Path(f"/tmp/preview-{template_id}.log")
    log_f = open(log_path, "w", encoding="utf-8")
    # On Windows we run via cmd /c to avoid path issues with npx batch files.
    proc = subprocess.Popen(
        ["cmd", "/c", "npx", "next", "dev", "-p", str(port)],
        cwd=str(tmpl_dir),
        stdout=log_f,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    return proc


def wait_ready(port: int, timeout_s: int = 60) -> bool:
    """Poll until the dev server responds. Returns True on success."""
    import urllib.request
    end = time.time() + timeout_s
    while time.time() < end:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def screenshot_all(ready_ports: dict[str, int]) -> int:
    """Use Playwright to screenshot every ready variant. Returns failure count."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright missing: pip install playwright && playwright install chromium")
        return -1

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    fails = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        for tid, port in ready_ports.items():
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
                print(f"  [ok]   {tid:30s} -> {target.name} ({kb} KB)")
                page.close()
            except Exception as e:
                print(f"  [fail] {tid:30s} fail: {e}")
                fails += 1
        browser.close()
    return fails


def main():
    kill_after = "--kill-after" in sys.argv

    print(f"Booting {len(VARIANT_ORDER)} variants on ports {START_PORT}..{START_PORT + len(VARIANT_ORDER) - 1}")
    procs: dict[str, tuple[subprocess.Popen, int]] = {}
    for i, tid in enumerate(VARIANT_ORDER):
        port = START_PORT + i
        proc = boot_one(tid, port)
        if proc:
            procs[tid] = (proc, port)
            print(f"  boot: {tid:30s} on :{port} (pid {proc.pid})")
        # Stagger ~2s to avoid simultaneous npx startup contention
        time.sleep(2)

    print(f"\nWaiting for {len(procs)} dev servers to be ready...")
    ready: dict[str, int] = {}
    for tid, (proc, port) in procs.items():
        ok = wait_ready(port, timeout_s=120)
        if ok:
            ready[tid] = port
            print(f"  ready: {tid:30s} :{port}")
        else:
            print(f"  TIMEOUT: {tid:30s} :{port}")

    print(f"\n{len(ready)}/{len(procs)} servers ready. Capturing screenshots...")
    fails = screenshot_all(ready)

    if kill_after:
        print("\n--kill-after: terminating dev servers...")
        for tid, (proc, _) in procs.items():
            try:
                if sys.platform == "win32":
                    proc.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    proc.terminate()
            except Exception:
                pass
        time.sleep(2)
        print("  done")
    else:
        print("\nDev servers left running (--kill-after to terminate).")
        print("Ports in use:")
        for tid, port in ready.items():
            print(f"  http://127.0.0.1:{port}  → {tid}")

    sys.exit(0 if fails <= 0 else 3)


if __name__ == "__main__":
    main()
