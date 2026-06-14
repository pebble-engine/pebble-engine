#!/usr/bin/env python3
"""Production smoke suite — automated checks from the senior plan.

Runs all verify_* scripts plus documents manual steps.

Usage:
  python scripts/prod_smoke.py
  python scripts/prod_smoke.py --skip-manual

Exit 0 when all automated checks pass.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

AUTOMATED = [
    ("verify_prod.py", "Core API (health, templates, examples, community)"),
    ("verify_preview_prod.py", "Preview backend (Railway /api/health)"),
    ("verify_community_prod.py", "Community feed + stats"),
    ("verify_launchpad_prod.py", "Launchpad showcase"),
    ("verify_stripe_setup.py", "Stripe env (local .env only)"),
]

MANUAL_CHECKLIST = """
Manual smoke (Marc or Builder with browser) — after automated passes:

  [ ] Signup at https://www.pebbleapp.ai/signup (or login)
  [ ] Workspace: submit prompt → SSE build completes
  [ ] Design phase: preview iframe loads
  [ ] Click-to-edit: change hero text or color
  [ ] Publish: instant subdomain or preview URL live
  [ ] /templates and /examples galleries load
  [ ] /community shows real stats (not stuck on seed)
  [ ] /community/launchpad gallery + submit (if published)

See docs/GOLDEN_DEMO.md for investor rehearsal path.
"""


def run_script(name: str) -> int:
    path = ROOT / "scripts" / name
    print(f"\n--- {name} ---")
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(ROOT),
        capture_output=False,
    )
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Prod smoke suite")
    parser.add_argument("--skip-manual", action="store_true", help="Do not print manual checklist")
    args = parser.parse_args()

    print("Pebble production smoke suite\n")
    failed = 0
    for script, label in AUTOMATED:
        print(f"▶ {label}")
        code = run_script(script)
        if code != 0:
            failed += 1

    print()
    if failed:
        print(f"{failed} automated check(s) failed.")
    else:
        print("All automated checks passed.")

    if not args.skip_manual:
        print(MANUAL_CHECKLIST)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
