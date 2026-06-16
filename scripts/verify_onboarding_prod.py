#!/usr/bin/env python3
"""Verify onboarding funnel APIs on production.

Checks:
  POST /api/brief-infer  -> 200 + business_name
  GET  /api/onboarding/status -> 401 without auth (route exists)

Usage:
  python scripts/verify_onboarding_prod.py
  python scripts/verify_onboarding_prod.py --base https://www.pebbleapp.ai
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

DEFAULT_BASE = "https://www.pebbleapp.ai"


def post_json(url: str, payload: dict, timeout: float = 30.0) -> tuple[int, dict | str]:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "pebble-verify-onboarding/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, body
    except Exception as e:
        return 0, str(e)


def get(url: str, timeout: float = 15.0) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "pebble-verify-onboarding/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")[:300]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
        return e.code, body[:300]
    except Exception as e:
        return 0, str(e)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify prod onboarding APIs")
    parser.add_argument("--base", default=DEFAULT_BASE)
    args = parser.parse_args()
    base = args.base.rstrip("/")

    print(f"Checking onboarding APIs at {base} …\n")
    failed = 0

    status, body = post_json(
        f"{base}/api/brief-infer",
        {"prompt": "family bakery in Brooklyn"},
    )
    ok = status == 200 and isinstance(body, dict) and body.get("business_name")
    mark = "OK" if ok else "FAIL"
    print(f"  [{mark}] POST /api/brief-infer -> HTTP {status}")
    if ok:
        print(f"         business_name={body.get('business_name')!r} source={body.get('source')}")
    else:
        failed += 1
        print(f"         {body}")

    status, body = get(f"{base}/api/onboarding/status")
    ok = status == 401
    mark = "OK" if ok else "FAIL"
    print(f"  [{mark}] GET /api/onboarding/status (no auth) -> HTTP {status}")
    if not ok:
        failed += 1
        print(f"         {body}")

    print()
    if failed:
        print(f"{failed} check(s) failed.")
        return 1
    print("Onboarding APIs reachable on prod.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
