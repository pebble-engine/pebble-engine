#!/usr/bin/env python3
"""Production smoke suite — automated checks.

Usage:
  python scripts/prod_smoke.py
  python scripts/prod_smoke.py --skip-manual
  python scripts/prod_smoke.py --json

Exit 0 when all checks pass. JSON mode for verify_all.py.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

AUTOMATED = [
    ("verify_prod.py", "Core API"),
    ("verify_preview_prod.py", "Preview backend"),
    ("verify_community_prod.py", "Community"),
    ("verify_launchpad_prod.py", "Launchpad"),
]


def run_script(name: str) -> tuple[int, str]:
    path = ROOT / "scripts" / name
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = (result.stdout or "") + (result.stderr or "")
    return result.returncode, out.strip()[-2000:]


def run_prod_smoke(*, include_stripe: bool = True, skip_manual: bool = True) -> dict:
    scripts = list(AUTOMATED)
    if include_stripe:
        scripts.append(("verify_stripe_setup.py", "Stripe env"))

    checks = []
    failed = 0
    for script, label in scripts:
        code, tail = run_script(script)
        ok = code == 0
        if not ok:
            failed += 1
        checks.append({
            "script": script,
            "label": label,
            "exit_code": code,
            "ok": ok,
            "output_tail": tail,
        })

    return {
        "ok": failed == 0,
        "failed_count": failed,
        "total": len(checks),
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prod smoke suite")
    parser.add_argument("--skip-manual", action="store_true", help="Do not print manual checklist")
    parser.add_argument("--json", action="store_true", help="Emit JSON result on stdout")
    parser.add_argument("--no-stripe", action="store_true", help="Skip Stripe env check")
    args = parser.parse_args()

    result = run_prod_smoke(include_stripe=not args.no_stripe, skip_manual=args.skip_manual)

    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1

    print("Pebble production smoke suite\n")
    for c in result["checks"]:
        mark = "OK" if c["ok"] else "FAIL"
        print(f"  [{mark}] {c['label']} ({c['script']}) exit={c['exit_code']}")

    print()
    if result["ok"]:
        print("All automated checks passed.")
    else:
        print(f"{result['failed_count']} check(s) failed.")

    if not args.skip_manual:
        print("""
Manual browser smoke (optional):
  signup -> build -> preview -> publish -> /community
See docs/GOLDEN_DEMO.md
""")

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
