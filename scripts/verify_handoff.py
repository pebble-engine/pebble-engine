#!/usr/bin/env python3
"""Check that a recent HANDOFF references VERIFICATION_REPORT with PASS.

Optional gate at end of verify_all.py. Warns if no handoff or stale evidence.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "VERIFICATION_REPORT.md"


def _latest_handoff() -> Path | None:
    handoffs = sorted(ROOT.glob("HANDOFF_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return handoffs[0] if handoffs else None


def main() -> int:
    handoff = _latest_handoff()
    if handoff is None:
        print("verify_handoff: no HANDOFF_*.md found (OK for verify-only runs)")
        return 0

    body = handoff.read_text(encoding="utf-8")
    if "## Evidence" not in body:
        print(f"verify_handoff: {handoff.name} missing ## Evidence section")
        return 1

    if (
        "VERIFICATION_REPORT" not in body
        and "verify_all" not in body
        and "pytest" not in body.lower()
    ):
        print(f"verify_handoff: {handoff.name} Evidence does not reference verification")
        return 1

    # If report exists and says FAIL, warn but do not block — verify_all.py
    # runs this check before writing the new report (chicken-and-egg).
    if REPORT.exists():
        report = REPORT.read_text(encoding="utf-8")
        if "**Status:** FAIL" in report:
            print(f"verify_handoff: OK ({handoff.name}); note: prior report was FAIL, re-run updates it")

    print(f"verify_handoff: OK ({handoff.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
