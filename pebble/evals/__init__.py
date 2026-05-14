"""Pebble Engine — build evaluation harness.

Grades a generated site against a battery of checks: does it compile,
does the hero have an h1, was the DNA's display font actually honored,
are there raw <img> tags instead of next/image, etc.

Use:
    python -m pebble.evals <slug>          # single build
    python -m pebble.evals --all           # every build in output/
    python -m pebble.evals --all --json    # machine-readable

API:
    from pebble.evals import run_checks, BuildContext, ALL_CHECKS
    results = run_checks(Path("output/some-slug"))

Each check is a function taking a BuildContext and returning a CheckResult.
Adding a new check: write the function in checks.py, append it to ALL_CHECKS,
add a test in tests/test_evals.py.
"""
from pebble.evals.runner import (
    BuildContext,
    CheckResult,
    list_build_dirs,
    OUTPUT_DIR,
    run_checks,
)
from pebble.evals.checks import ALL_CHECKS, CHECK_BY_NAME, check_file_hints, check_metadata

__all__ = [
    "BuildContext",
    "CheckResult",
    "run_checks",
    "list_build_dirs",
    "ALL_CHECKS",
    "CHECK_BY_NAME",
    "check_file_hints",
    "check_metadata",
    "OUTPUT_DIR",
]
