#!/usr/bin/env python3
"""Smoke-check Launchpad API on production (or override base URL)."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("PEBBLE_PROD_BASE", "https://www.pebbleapp.ai").rstrip("/")


def _get(path: str) -> tuple[int, dict]:
    req = urllib.request.Request(f"{BASE}{path}", method="GET")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": body[:200]}


def main() -> int:
    print(f"Checking Launchpad API at {BASE} …\n")
    ok = True

    status, body = _get("/api/launchpad/showcase")
    if status == 200 and isinstance(body.get("entries"), list):
        print(f"  [OK] /api/launchpad/showcase -> HTTP {status}, count={body.get('count', '?')}")
    else:
        print(f"  [FAIL] /api/launchpad/showcase -> HTTP {status}, body={body!r}")
        ok = False

    if ok:
        print("\nLaunchpad API reachable.")
        return 0
    print("\nLaunchpad check failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
