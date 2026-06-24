#!/usr/bin/env python3
"""Production golden-path smoke (no auth build — health + preview backend + brief-infer).

Usage:
  python scripts/golden_path_prod.py
  python scripts/golden_path_prod.py --slug bakery

Exit 0 when core prod APIs respond and optional slug preview is live.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENGINE = "https://web-production-e5cb0.up.railway.app"


def fetch_json(url: str, timeout: float = 30.0) -> tuple[int, dict | str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "pebble-golden-path/1.0", "Content-Type": "application/json"},
    )
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


def post_json(url: str, payload: dict) -> tuple[int, dict | str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"User-Agent": "pebble-golden-path/1.0", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
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
    parser = argparse.ArgumentParser(description="Prod golden-path smoke")
    parser.add_argument("--engine", default=DEFAULT_ENGINE)
    parser.add_argument("--slug", default="", help="Optional: verify /preview/<slug>/ is live")
    args = parser.parse_args()
    base = args.engine.rstrip("/")
    failed = 0

    print("=== Golden path prod smoke ===\n")

    # 1. Health
    st, body = fetch_json(f"{base}/api/health")
    if st != 200 or not isinstance(body, dict):
        print(f"[FAIL] /api/health → {st}")
        failed += 1
    else:
        print(f"[OK] health llm_ready={body.get('llm_ready')} preview_backend={body.get('preview_backend')}")
        if not body.get("preview_prod_ready"):
            print("  [WARN] preview_prod_ready is false — set PEBBLE_PREVIEW_BACKEND=vercel on Railway")
            failed += 1
        vol = body.get("output_volume") or {}
        if not vol.get("writable"):
            print("  [WARN] output/ not writable — attach Railway volume (docs/RAILWAY_VOLUME.md)")
        else:
            print(f"  [OK] output_volume projects={vol.get('project_count')}")

    # 2. Brief infer (onboarding)
    st, body = post_json(f"{base}/api/brief-infer", {"prompt": "bakery in Brooklyn"})
    if st != 200 or not isinstance(body, dict) or not body.get("business_name"):
        print(f"[FAIL] /api/brief-infer → HTTP {st}")
        failed += 1
    else:
        print(f"[OK] brief-infer business_name={body.get('business_name')!r}")

    # 3. Preview verify script bundle
    for script in ("verify_preview_prod.py", "prod_smoke.py"):
        path = ROOT / "scripts" / script
        if path.exists():
            r = subprocess.run([sys.executable, str(path)], cwd=str(ROOT), capture_output=True, text=True)
            if r.returncode != 0:
                print(f"[FAIL] {script}")
                print((r.stdout or r.stderr)[-500:])
                failed += 1
            else:
                print(f"[OK] {script}")

    # 4. Optional slug preview
    if args.slug:
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "verify_preview_slug.py"), args.slug, "--engine", base],
            cwd=str(ROOT),
        )
        if r.returncode != 0:
            failed += 1

    print()
    if failed:
        print(f"FAILED ({failed} check(s))")
        return 1
    print("ALL GOLDEN PATH CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
