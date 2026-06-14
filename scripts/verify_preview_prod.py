#!/usr/bin/env python3
"""Smoke-check production preview backend wiring.

Usage:
  python scripts/verify_preview_prod.py
  python scripts/verify_preview_prod.py --engine https://web-production-e5cb0.up.railway.app

Exit 0 when preview_backend=vercel and vercel_configured=true on the engine.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

DEFAULT_ENGINE = "https://web-production-e5cb0.up.railway.app"


def fetch_json(url: str, timeout: float = 30.0) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, headers={"User-Agent": "pebble-verify-preview/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, body
    except Exception as e:
        return 0, str(e)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify prod preview backend config")
    parser.add_argument("--engine", default=DEFAULT_ENGINE, help="Engine origin (Railway URL)")
    args = parser.parse_args()
    base = args.engine.rstrip("/")
    url = f"{base}/api/health"

    print(f"Checking preview config at {url} …\n")
    status, body = fetch_json(url)
    if status != 200 or not isinstance(body, dict):
        print(f"  [FAIL] /api/health -> HTTP {status or 'error'}")
        if body:
            print(f"         {str(body)[:200]}")
        print("\nSee docs/PROD_PREVIEW_SETUP.md")
        return 1

    backend = body.get("preview_backend", "unknown")
    vercel_ok = bool(body.get("vercel_configured"))
    prod_ready = bool(body.get("preview_prod_ready"))

    if backend == "unknown" and "preview_backend" not in body:
        print("  [FAIL] Engine is running stale code (no preview_backend in /api/health)")
        print("         Railway must deploy current squitopest/pebble-engine main first.")
        print("\nSee docs/PROD_PREVIEW_SETUP.md")
        return 1

    print(f"  preview_backend     = {backend}")
    print(f"  vercel_configured   = {vercel_ok}")
    print(f"  preview_prod_ready  = {prod_ready}")

    failed = 0
    if backend != "vercel":
        print(f"\n  [FAIL] Expected preview_backend=vercel (got {backend!r})")
        print("         Railway still uses local preview — npm not available on prod.")
        failed += 1
    if not vercel_ok:
        print("\n  [FAIL] VERCEL_TOKEN not set on Railway engine")
        failed += 1
    if not prod_ready:
        print("\n  [FAIL] preview_prod_ready is false")
        failed += 1

    print()
    if failed:
        print(f"{failed} check(s) failed. Run: python scripts/_railway_fix_preview_once.py")
        print("See docs/PROD_PREVIEW_SETUP.md")
        return 1
    print("Preview backend is configured for production.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
