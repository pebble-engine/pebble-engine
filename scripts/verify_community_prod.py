#!/usr/bin/env python3
"""Smoke-check production community feed + stats."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

DEFAULT_BASE = "https://www.pebbleapp.ai"


def fetch(url: str) -> tuple[int, dict]:
    req = urllib.request.Request(url, headers={"User-Agent": "pebble-verify-community/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else "{}"
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"error": body[:200]}


def main() -> int:
    base = (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE).rstrip("/")
    print(f"Checking community APIs at {base} …\n")
    failed = 0

    status, feed = fetch(f"{base}/api/community/feed")
    ok = status == 200 and isinstance(feed.get("events"), list)
    print(f"  [{'OK' if ok else 'FAIL'}] /api/community/feed -> HTTP {status}, count={feed.get('count', '?')}")
    if not ok:
        failed += 1

    status, stats_body = fetch(f"{base}/api/community/stats")
    stats = stats_body.get("stats")
    ok = status == 200 and (stats is not None or stats_body.get("fallback"))
    tpl = stats.get("templates_count") if stats else "?"
    print(f"  [{'OK' if ok else 'FAIL'}] /api/community/stats -> HTTP {status}, templates={tpl}")
    if not ok:
        failed += 1

    print()
    if failed:
        return 1
    print("Community APIs reachable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
