"""Regression test that pins ui/v3/lib/motion.ts as the canonical motion
language for the v3 frontend. The actual variant values live in
TypeScript and are verified end-to-end via the plain-Node script at
ui/v3/lib/motion.test.mjs. This test pins the STRUCTURAL side — file
exists, exports the expected tokens, and (in Task 7) is imported by
the phase files.

Two-sided verification keeps the contract honest from both directions
without requiring a JS test runner inside the Python suite.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MOTION_TS = REPO_ROOT / "ui" / "v3" / "lib" / "motion.ts"


def test_motion_module_exists():
    assert MOTION_TS.is_file(), f"Missing: {MOTION_TS}"


def test_motion_exports_durations():
    src = MOTION_TS.read_text(encoding="utf-8")
    for name in ("MICRO", "SHORT", "STANDARD", "SLOW"):
        assert re.search(
            rf"export\s+const\s+{name}\s*=",
            src,
        ), f"motion.ts missing duration export: {name}"


def test_motion_exports_easings():
    src = MOTION_TS.read_text(encoding="utf-8")
    for name in ("EASE_CINEMATIC", "EASE_QUIET"):
        assert re.search(
            rf"export\s+const\s+{name}\s*:",
            src,
        ), f"motion.ts missing easing export: {name}"


def test_motion_exports_variants():
    src = MOTION_TS.read_text(encoding="utf-8")
    for name in ("fadeUp", "phaseEnter", "phaseExit", "railStep",
                 "chipDeck", "cardHover", "dropletPulse"):
        assert re.search(
            rf"export\s+const\s+{name}\s*:",
            src,
        ), f"motion.ts missing variant export: {name}"


def test_motion_exports_reduced_motion_helper():
    src = MOTION_TS.read_text(encoding="utf-8")
    assert "export function prefersReducedMotion" in src
    assert "export function withReducedMotion" in src
