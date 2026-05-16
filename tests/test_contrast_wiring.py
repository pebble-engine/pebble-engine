"""Regression test for the round 3 commit 3 contrast pass.

Pins the two WCAG-readable accent variants (--color-spark-deep,
--color-earth-deep) that were added to globals.css to remediate the
text-spark / text-earth on tinted-bg contrast failures. Also pins that
the audit script exists and is runnable.

The deep variants only fix the spark/earth tinted-pill text failures.
Border contrast, dark-mode tints, text-destructive failures, and
text-secondary/15 failures are intentionally deferred — see the spec
at docs/superpowers/specs/2026-05-15-round3-contrast-design.md.
"""
from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GLOBALS_CSS = REPO_ROOT / "ui" / "v3" / "app" / "globals.css"
AUDIT_SCRIPT = REPO_ROOT / "scripts" / "contrast_audit.py"
DASHBOARD_PAGE = REPO_ROOT / "ui" / "v3" / "app" / "dashboard" / "page.tsx"


def test_audit_script_exists():
    """The runnable audit tool lives under scripts/. Pin its presence so a
    future cleanup pass doesn't quietly remove the regression baseline."""
    assert AUDIT_SCRIPT.is_file(), f"Missing: {AUDIT_SCRIPT}"


def test_spark_deep_variant_defined():
    """The WCAG-readable spark variant must be declared with the hex value
    that the audit script's contrast calculation depends on. If someone
    changes the hex, the audit numbers in the spec become wrong — this
    pins them together."""
    src = GLOBALS_CSS.read_text(encoding="utf-8")
    assert re.search(
        r"--color-spark-deep:\s*#8b3a14",
        src,
        re.IGNORECASE,
    ), "globals.css must define --color-spark-deep: #8b3a14"


def test_earth_deep_variant_defined():
    """Same as spark — pinned hex so audit numbers stay accurate."""
    src = GLOBALS_CSS.read_text(encoding="utf-8")
    assert re.search(
        r"--color-earth-deep:\s*#455a37",
        src,
        re.IGNORECASE,
    ), "globals.css must define --color-earth-deep: #455a37"


def test_dashboard_uses_deep_variant():
    """At least one tinted-pill consumer (the dashboard's project status
    pills) must use a *-deep utility. Proves the migration was applied;
    the wiring test fails if a future refactor reverts the dashboard to
    the failing text-spark/text-earth pattern."""
    src = DASHBOARD_PAGE.read_text(encoding="utf-8")
    has_spark = "text-spark-deep" in src
    has_earth = "text-earth-deep" in src
    assert has_spark or has_earth, (
        "dashboard/page.tsx must use text-spark-deep or text-earth-deep "
        "(the pill-pattern fix). If you intentionally rolled back the "
        "migration, delete this test."
    )
