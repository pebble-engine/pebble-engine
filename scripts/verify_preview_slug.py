#!/usr/bin/env python3
"""Check one project's prod preview (splash vs live HTML).

Usage:
  python scripts/verify_preview_slug.py bakery
  python scripts/verify_preview_slug.py bakery --engine https://web-production-e5cb0.up.railway.app

Exit 0 when /preview/<slug>/ returns HTML with pebble-bridge (live proxy).
Exit 1 on splash, auth wall, or HTTP error.
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request

DEFAULT_ENGINE = "https://web-production-e5cb0.up.railway.app"


def fetch(url: str, timeout: float = 60.0) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "pebble-verify-preview-slug/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, body
    except Exception as e:
        return 0, str(e)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify prod preview for one slug")
    parser.add_argument("slug", help="Project slug")
    parser.add_argument("--engine", default=DEFAULT_ENGINE)
    args = parser.parse_args()
    base = args.engine.rstrip("/")
    url = f"{base}/preview/{args.slug}/"
    print(f"GET {url}\n")
    status, body = fetch(url)
    print(f"  HTTP {status or 'error'}  len={len(body)}")

    if status != 200:
        print(f"  [FAIL] {body[:300]}")
        return 1
    if "Authentication Required" in body or "Vercel Authentication" in body:
        print("  [FAIL] Vercel deployment protection auth wall (bypass not working)")
        return 1
    if "pebble-bridge" in body:
        print("  [OK] Live preview HTML with visual-edit bridge")
        return 0
    if "Building your preview" in body or "Starting preview" in body:
        err = re.search(r"<pre>(.*?)</pre>", body, re.DOTALL)
        detail = err.group(1).strip() if err else "(no error detail — Vercel deploy still running?)"
        print(f"  [FAIL] Warmup splash — {detail}")
        return 1
    if "Preview deploy failed" in body or "Preview needs another try" in body:
        err = re.search(r"<pre>(.*?)</pre>", body, re.DOTALL)
        print(f"  [FAIL] {err.group(1).strip() if err else 'deploy error splash'}")
        return 1
    print("  [FAIL] Unexpected HTML (not splash, not live preview)")
    print(body[:400])
    return 1


if __name__ == "__main__":
    sys.exit(main())
