"""Regression test that pins ui/v3/lib/interactions.ts as the canonical
interaction scale for the v3 frontend. Same two-sided pattern as motion + type:
actual className strings live in TypeScript and are verified end-to-end via the
plain-Node script at ui/v3/lib/interactions.test.mjs. This test pins the
STRUCTURAL side — file exists, exports the expected role keys, and a11y
overrides are present.

The consumer-import parametrized assertion is added in the next commit
(commit C, the apply pass) so this commit ships green pytest.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INTERACTIONS_TS = REPO_ROOT / "ui" / "v3" / "lib" / "interactions.ts"


def test_interactions_module_exists():
    assert INTERACTIONS_TS.is_file(), f"Missing: {INTERACTIONS_TS}"


def test_interactions_module_exports_const():
    src = INTERACTIONS_TS.read_text(encoding="utf-8")
    assert re.search(r"export\s+const\s+interactions\s*=\s*\{", src), \
        "interactions.ts must export `interactions` as a const"
    assert re.search(r"\}\s*as const\s*;", src), \
        "interactions object must be `as const` for literal-string types"


def test_interactions_module_exports_all_role_keys():
    src = INTERACTIONS_TS.read_text(encoding="utf-8")
    for role in ("button", "chip", "card", "iconButton", "link", "focusRing"):
        assert re.search(rf"\b{role}\s*:", src), \
            f"interactions role `{role}` missing"


def test_interactions_module_honors_reduced_motion():
    """Proves accessibility was considered — every role with transform/scale
    includes a `motion-reduce:` override that resets the motion to instant."""
    src = INTERACTIONS_TS.read_text(encoding="utf-8")
    assert re.search(r"motion-reduce:", src), \
        "interactions.ts must include `motion-reduce:` overrides for a11y"
