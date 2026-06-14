#!/usr/bin/env python3
"""Smoke-check production pebbleapp.ai ↔ engine connectivity.

Usage:
  python scripts/verify_prod.py
  python scripts/verify_prod.py --base https://www.pebbleapp.ai

Exit 0 if all checks pass; 1 if any fail.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

DEFAULT_BASE = "https://www.pebbleapp.ai"

CHECKS = (
    ("/api/health", "Engine health"),
    ("/api/templates", "Templates catalog"),
    ("/api/examples", "Examples catalog"),
    ("/api/community/stats", "Community stats"),
    ("/api/community/feed", "Community feed"),
    ("/api/launchpad/showcase", "Launchpad showcase"),
)


def fetch(url: str, timeout: float = 30.0) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "pebble-verify-prod/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body[:500]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
        return e.code, body[:500]
    except Exception as e:
        return 0, str(e)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify prod API connectivity")
    parser.add_argument("--base", default=DEFAULT_BASE, help="Frontend origin (default: pebbleapp.ai)")
    args = parser.parse_args()
    base = args.base.rstrip("/")

    print(f"Checking {base} …\n")
    failed = 0
    for path, label in CHECKS:
        url = f"{base}{path}"
        status, body = fetch(url)
        ok = status == 200
        if ok and path == "/api/health":
            try:
                json.loads(body)
            except json.JSONDecodeError:
                ok = False
        if "DNS_HOSTNAME_RESOLVED_PRIVATE" in body:
            ok = False
        mark = "OK" if ok else "FAIL"
        print(f"  [{mark}] {label}: {path} -> HTTP {status or 'error'}")
        if not ok:
            failed += 1
            snippet = body.replace("\n", " ")[:120]
            if snippet:
                print(f"         {snippet}")

    print()
    if failed:
        print(f"{failed} check(s) failed. See docs/PROD_ENGINE_SETUP.md")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
