"""CLI entry point for the eval harness.

Usage:
    python -m pebble.evals <slug>
    python -m pebble.evals --all
    python -m pebble.evals --all --json
    python -m pebble.evals <slug> --skip-compile
"""
from __future__ import annotations

import argparse
import json
import sys

from pebble.evals.report import format_summary, format_text, to_json
from pebble.evals.runner import OUTPUT_DIR, BuildContext, list_build_dirs, run_checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m pebble.evals",
        description="Grade a Pebble Engine build against the eval suite.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("slug", nargs="?", help="single build slug to grade")
    group.add_argument("--all", action="store_true", help="grade every build in output/")
    parser.add_argument(
        "--json", action="store_true",
        help="emit JSON for machine consumption (one object per build)",
    )
    parser.add_argument(
        "--skip-compile", action="store_true",
        help="skip the heaviest check (site_compiles, tsc --noEmit) for fast iteration",
    )
    args = parser.parse_args(argv)

    if args.all:
        build_dirs = list_build_dirs()
        if not build_dirs:
            print("no builds found in output/", file=sys.stderr)
            return 2
    else:
        d = OUTPUT_DIR / args.slug
        if not d.exists() or not (d / "brief.json").exists():
            print(f"build not found: {args.slug}", file=sys.stderr)
            return 2
        build_dirs = [d]

    checks = None
    if args.skip_compile:
        from pebble.evals.checks import ALL_CHECKS, site_compiles
        checks = [c for c in ALL_CHECKS if c is not site_compiles]

    json_blobs: list[dict] = []
    summary_rows: list[dict] = []
    any_failures = False

    for build_dir in build_dirs:
        ctx = BuildContext.load(build_dir)
        results = run_checks(build_dir, checks=checks)

        if args.json:
            json_blobs.append(to_json(results, ctx.slug, ctx.brief))
        else:
            print(format_text(ctx.slug, ctx.brief, results))
            print()

        # Aggregate for summary
        counts = {"pass": 0, "fail": 0, "skip": 0, "error": 0}
        for r in results:
            counts[r.status] = counts.get(r.status, 0) + 1
        if counts["fail"] or counts["error"]:
            any_failures = True
        summary_rows.append({
            "slug": ctx.slug,
            "dna": ctx.brief.get("_design_dna"),
            **counts,
        })

    if args.json:
        print(json.dumps(json_blobs, indent=2))
    elif len(build_dirs) > 1:
        print(format_summary(summary_rows))

    # Non-zero exit so CI scripts can detect failures from `--all`.
    return 1 if any_failures else 0


if __name__ == "__main__":
    sys.exit(main())
