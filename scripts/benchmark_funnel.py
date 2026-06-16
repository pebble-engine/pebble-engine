#!/usr/bin/env python3
"""Measure Pebble API milestones for speed benchmarking (no browser required).

Usage:
  python scripts/benchmark_funnel.py
  python scripts/benchmark_funnel.py --engine http://127.0.0.1:8000 --prompt "I own a bakery in Brooklyn"

Prints JSON to stdout; append results to docs/SPEED_BENCHMARK.md manually or via CI.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

DEFAULT_PROMPT = (
    "I own a bakery in Brooklyn — need a site where locals can find us and get in touch."
)


def _post(url: str, body: dict, timeout: float = 120.0) -> tuple[float, dict]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    elapsed = time.perf_counter() - t0
    return elapsed, json.loads(raw)


def _get(url: str, timeout: float = 30.0) -> tuple[float, dict]:
    req = urllib.request.Request(url, method="GET")
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    elapsed = time.perf_counter() - t0
    return elapsed, json.loads(raw)


def main() -> int:
    ap = argparse.ArgumentParser(description="Benchmark Pebble funnel API timings")
    ap.add_argument("--engine", default="http://127.0.0.1:8000", help="Engine base URL")
    ap.add_argument("--prompt", default=DEFAULT_PROMPT, help="Standard test prompt")
    args = ap.parse_args()
    base = args.engine.rstrip("/")

    out: dict = {"prompt": args.prompt, "engine": base, "milestones": {}}

    try:
        t, health = _get(f"{base}/api/health")
        out["milestones"]["health_s"] = round(t, 3)
        out["llm_ready"] = health.get("llm_ready")
    except urllib.error.URLError as e:
        print(json.dumps({"error": f"engine unreachable: {e}"}, indent=2))
        return 1

    try:
        t, infer = _post(f"{base}/api/brief-infer", {"raw_prompt": args.prompt})
        out["milestones"]["brief_infer_s"] = round(t, 3)
        out["infer_ok"] = infer.get("ok")
        if infer.get("ok"):
            out["inferred"] = {
                k: infer.get(k)
                for k in ("business_name", "business_type", "location", "site_functions")
            }
    except Exception as e:
        out["infer_error"] = str(e)

    brief_fields = {
        "_raw_prompt": args.prompt,
        "business_name": out.get("inferred", {}).get("business_name") or "Brooklyn Bakery",
        "business_type": out.get("inferred", {}).get("business_type") or "bakery",
        "location": out.get("inferred", {}).get("location") or "Brooklyn",
        "audience": ["locals"],
        "site_functions": out.get("inferred", {}).get("site_functions") or ["leads", "presence"],
        "brand_tone": "warm",
        "intent": "business",
    }
    plan_brief = dict(brief_fields)

    try:
        t, composed = _post(f"{base}/api/brief-compose", brief_fields)
        out["milestones"]["brief_compose_s"] = round(t, 3)
        out["compose_ok"] = composed.get("ok")
        if composed.get("ok"):
            patch = composed.get("brief_patch") or {}
            plan_brief.update(patch)
    except Exception as e:
        out["compose_error"] = str(e)

    try:
        t, plan_resp = _post(f"{base}/api/plan", plan_brief)
        out["milestones"]["plan_s"] = round(t, 3)
        out["plan_ok"] = "plan" in plan_resp
    except Exception as e:
        out["plan_error"] = str(e)

    total = sum(v for k, v in out["milestones"].items() if k.endswith("_s"))
    out["milestones"]["api_total_before_generate_s"] = round(total, 3)

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
