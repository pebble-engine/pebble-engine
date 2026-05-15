"""Regression test that pins ui/v3/lib/view-transitions.ts — same
pattern as test_safe_redirect_wiring.py and test_motion_module_wiring.py.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VT_TS = REPO_ROOT / "ui" / "v3" / "lib" / "view-transitions.ts"


def test_view_transitions_module_exists():
    assert VT_TS.is_file(), f"Missing: {VT_TS}"


def test_view_transitions_exports_capability_check():
    src = VT_TS.read_text(encoding="utf-8")
    assert "export function supportsViewTransitions" in src


def test_view_transitions_exports_safe_wrapper():
    src = VT_TS.read_text(encoding="utf-8")
    assert "export function safeStartViewTransition" in src


def test_view_transitions_falls_back_to_callback():
    """The fallback path must call callback() synchronously — without
    this, unsupported browsers would silently swallow the state change."""
    src = VT_TS.read_text(encoding="utf-8")
    assert re.search(r"else\s*\{\s*callback\(\);?\s*\}", src), (
        "fallback branch must call callback() synchronously"
    )
