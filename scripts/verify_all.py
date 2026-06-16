#!/usr/bin/env python3
"""Full verification gate — pytest + prod smoke + VERIFICATION_REPORT.md.

Usage:
  python scripts/verify_all.py
  python scripts/verify_all.py --ci
  python scripts/verify_all.py --no-handoff-check

Marc: open VERIFICATION_REPORT.md — Status PASS or FAIL at top.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "VERIFICATION_REPORT.md"


def _git_sha() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return "unknown"


def _run_pytest(*, ci: bool) -> dict:
    cmd = [sys.executable, "-m", "pytest", "-q", "--tb=no"]
    if ci:
        cmd.extend(["-m", "not integration"])
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = (result.stdout or "") + (result.stderr or "")
    passed = failed = 0
    m = re.search(r"(\d+)\s+failed", out)
    if m:
        failed = int(m.group(1))
    m2 = re.search(r"(\d+)\s+passed", out)
    if m2:
        passed = int(m2.group(1))
    if failed == 0 and passed == 0 and result.returncode == 0:
        m3 = re.search(r"(\d+)\s+passed", out)
        if m3:
            passed = int(m3.group(1))
    return {
        "name": "pytest",
        "ok": result.returncode == 0,
        "exit_code": result.returncode,
        "passed": passed,
        "failed": failed,
        "detail": out.strip().splitlines()[-1] if out.strip() else "",
        "ci_mode": ci,
    }


def _run_prod_smoke(*, ci: bool) -> dict:
    cmd = [sys.executable, str(ROOT / "scripts" / "prod_smoke.py"), "--json", "--skip-manual"]
    if ci:
        cmd.append("--no-stripe")
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {"ok": False, "failed_count": 1, "checks": []}
    return {
        "name": "prod_smoke",
        "ok": result.returncode == 0 and data.get("ok", False),
        "exit_code": result.returncode,
        "failed_count": data.get("failed_count", 0),
        "total": data.get("total", 0),
        "checks": data.get("checks", []),
    }


def _run_handoff_check() -> dict:
    script = ROOT / "scripts" / "verify_handoff.py"
    if not script.exists():
        return {"name": "handoff", "ok": True, "exit_code": 0, "detail": "skipped"}
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {
        "name": "handoff",
        "ok": result.returncode == 0,
        "exit_code": result.returncode,
        "detail": (result.stdout or result.stderr or "").strip()[-500:],
    }


def _write_report(payload: dict) -> None:
    status = "PASS" if payload["ok"] else "FAIL"
    lines = [
        "# Verification report",
        "",
        f"**Status:** {status}",
        f"**When:** {payload['timestamp']}",
        f"**Commit:** {payload['commit']}",
        "",
        "## Summary for Marc",
        "",
    ]
    if payload["ok"]:
        lines.append("All automated checks passed. Safe to trust this batch.")
    else:
        lines.append("One or more checks failed. Do not treat this batch as complete.")
        lines.append("Tell the agent: fix failures below and re-run verify_all.")

    lines.extend(["", "## Details", "", "| Check | Result | Exit |", "|-------|--------|------|"])

    py = payload["pytest"]
    py_result = f"{py.get('passed', 0)} passed, {py.get('failed', 0)} failed"
    if py.get("ci_mode"):
        py_result += " (CI: not integration)"
    lines.append(f"| pytest | {py_result} | {py['exit_code']} |")

    ps = payload["prod_smoke"]
    ps_result = f"{ps['total'] - ps.get('failed_count', 0)}/{ps['total']} scripts OK"
    lines.append(f"| prod_smoke | {ps_result} | {ps['exit_code']} |")

    if payload.get("handoff"):
        h = payload["handoff"]
        h_result = "OK" if h["ok"] else h.get("detail", "FAIL")[:80]
        lines.append(f"| handoff | {h_result} | {h['exit_code']} |")

    lines.extend(["", "## Raw pytest tail", "", "```", py.get("detail", ""), "```", ""])

    if not ps.get("ok"):
        lines.append("## Prod smoke failures\n")
        for c in ps.get("checks", []):
            if not c.get("ok"):
                lines.append(f"- **{c['label']}** (`{c['script']}`): exit {c['exit_code']}")
                lines.append(f"  ```\n  {c.get('output_tail', '')[-400:]}\n  ```\n")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Full verification gate")
    parser.add_argument("--ci", action="store_true", help="CI mode: skip Stripe, exclude integration tests")
    parser.add_argument("--no-handoff-check", action="store_true", help="Skip HANDOFF evidence check")
    args = parser.parse_args()

    payload = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": _git_sha(),
        "pytest": _run_pytest(ci=args.ci),
        "prod_smoke": _run_prod_smoke(ci=args.ci),
    }
    if not args.no_handoff_check:
        payload["handoff"] = _run_handoff_check()

    payload["ok"] = payload["pytest"]["ok"] and payload["prod_smoke"]["ok"]
    if payload.get("handoff"):
        payload["ok"] = payload["ok"] and payload["handoff"]["ok"]

    _write_report(payload)

    print(f"Wrote {REPORT_PATH}")
    print(f"Status: {'PASS' if payload['ok'] else 'FAIL'}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
