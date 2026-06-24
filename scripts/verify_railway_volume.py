#!/usr/bin/env python3
"""Check whether the prod engine has a writable, persistent output/ directory.

Usage:
  python scripts/verify_railway_volume.py
  python scripts/verify_railway_volume.py --engine https://web-production-e5cb0.up.railway.app

Writes a sentinel via a public health-adjacent probe is NOT possible without auth;
this script checks owner-visible signals only:

  1. /api/health includes output_volume_probe when engine runs current code
  2. Fallback: GET /api/admin/projects (requires session) — not run here

For Marc: run twice — once before redeploy, once after. If project slugs disappear
from the dashboard after redeploy, the volume is not mounted correctly.

Exit 0 when health reports volume probe fields (engine on current main).
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

DEFAULT_ENGINE = "https://web-production-e5cb0.up.railway.app"


def fetch_json(url: str, timeout: float = 30.0) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, headers={"User-Agent": "pebble-verify-volume/1.0"})
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
    parser = argparse.ArgumentParser(description="Verify Railway output volume probe on /api/health")
    parser.add_argument("--engine", default=DEFAULT_ENGINE, help="Engine origin")
    args = parser.parse_args()
    base = args.engine.rstrip("/")
    status, body = fetch_json(f"{base}/api/health")

    print(f"GET {base}/api/health → HTTP {status or 'error'}\n")
    if status != 200 or not isinstance(body, dict):
        print(f"  [FAIL] {str(body)[:300]}")
        print("\nSee docs/RAILWAY_VOLUME.md")
        return 1

    probe = body.get("output_volume")
    if not isinstance(probe, dict):
        print("  [WARN] Engine missing output_volume in /api/health — deploy current main first.")
        print("         Marc: still attach volume per docs/RAILWAY_VOLUME.md")
        return 1

    writable = bool(probe.get("writable"))
    path = probe.get("path", "")
    project_count = probe.get("project_count")

    print(f"  output.path          = {path}")
    print(f"  output.writable      = {writable}")
    print(f"  output.project_count = {project_count}")

    if not writable:
        print("\n  [FAIL] output/ is not writable — check volume mount permissions.")
        return 1

    print("\n  Volume probe OK. Marc: redeploy once and confirm project_count stable.")
    print("  See docs/RAILWAY_VOLUME.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
