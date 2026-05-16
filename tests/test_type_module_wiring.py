"""Regression test that pins ui/v3/lib/type.ts as the canonical typography
scale for the v3 frontend. Same two-sided pattern as motion: actual
className strings live in TypeScript and are verified end-to-end via the
plain-Node script at ui/v3/lib/type.test.mjs. This test pins the
STRUCTURAL side — file exists, exports the expected role keys, and the
eight workspace-critical files import from `@/lib/type`.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TYPE_TS = REPO_ROOT / "ui" / "v3" / "lib" / "type.ts"


def test_type_module_exists():
    assert TYPE_TS.is_file(), f"Missing: {TYPE_TS}"


def test_type_module_exports_const():
    src = TYPE_TS.read_text(encoding="utf-8")
    assert re.search(r"export\s+const\s+type\s*=\s*\{", src), \
        "type.ts must export `type` as a const"
    assert re.search(r"\}\s*as const\s*;", src), \
        "type object must be `as const` for literal-string types"


def test_type_module_exports_display_roles():
    src = TYPE_TS.read_text(encoding="utf-8")
    block = re.search(r"display\s*:\s*\{(.*?)\},", src, re.DOTALL)
    assert block, "display role group not found"
    body = block.group(1)
    for size in ("xl", "l", "m"):
        assert re.search(rf"\b{size}\s*:", body), \
            f"display.{size} missing"


def test_type_module_exports_heading_roles():
    src = TYPE_TS.read_text(encoding="utf-8")
    block = re.search(r"heading\s*:\s*\{(.*?)\},", src, re.DOTALL)
    assert block, "heading role group not found"
    body = block.group(1)
    for size in ("l", "m", "s"):
        assert re.search(rf"\b{size}\s*:", body), \
            f"heading.{size} missing"


def test_type_module_exports_body_roles():
    src = TYPE_TS.read_text(encoding="utf-8")
    block = re.search(r"body\s*:\s*\{(.*?)\},", src, re.DOTALL)
    assert block, "body role group not found"
    body = block.group(1)
    for size in ("l", "m", "s"):
        assert re.search(rf"\b{size}\s*:", body), \
            f"body.{size} missing"


def test_type_module_exports_flat_roles():
    src = TYPE_TS.read_text(encoding="utf-8")
    for role in ("label", "caption", "eyebrow", "mono"):
        assert re.search(rf"\b{role}\s*:\s*\"", src), \
            f"flat role `{role}` missing"


def test_eyebrow_uses_arbitrary_size_and_tracking():
    """eyebrow is the one role with non-Tailwind-default sizing.
    Pin its arbitrary values so a refactor can't quietly drop them."""
    src = TYPE_TS.read_text(encoding="utf-8")
    eyebrow = re.search(r"eyebrow\s*:\s*\"([^\"]*)\"", src)
    assert eyebrow, "eyebrow role string not found"
    value = eyebrow.group(1)
    assert "text-[11px]" in value, "eyebrow must use text-[11px]"
    assert "uppercase" in value, "eyebrow must be uppercase"
    assert "tracking-[0.08em]" in value, "eyebrow must use tracking-[0.08em]"


# Eight workspace-critical files. Anything outside this list is round 3.
TYPE_CONSUMER_FILES = [
    REPO_ROOT / "ui" / "v3" / "components" / "workspace-shell.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "top-nav.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "welcome-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "idea-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "plan-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "draft-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "edit-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "publish-phase.tsx",
    # round 3 commit 1:
    REPO_ROOT / "ui" / "v3" / "app" / "dashboard" / "page.tsx",
    REPO_ROOT / "ui" / "v3" / "app" / "admin" / "page.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "command-palette.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "dna-preview.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "language-picker.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "ui" / "ai-prompt-box.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "block-gallery.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "auth-menu.tsx",
]


@pytest.mark.parametrize("consumer", TYPE_CONSUMER_FILES, ids=lambda p: p.name)
def test_workspace_critical_file_imports_from_type_module(consumer):
    """The eight workspace-critical files must import from `@/lib/type`."""
    src = consumer.read_text(encoding="utf-8")
    assert re.search(
        r"from\s+['\"]@/lib/type['\"]",
        src,
    ), f"{consumer.name} should import from @/lib/type"
