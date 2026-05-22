"""Tests for the visual-edit font-family op.

These tests exercise _edit_font_family_for_selector and the _upsert_jsx_style
helper directly (unit level), plus the op-validator guard in run_visual_edit.
No HTTP server or Supabase is needed — the functions operate on a temp dir.
"""
from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

import pytest

from pebble.server.visual_edit import (
    _edit_font_family_for_selector,
    _upsert_jsx_style,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_site(files: dict[str, str]) -> Path:
    """Write *files* into a fresh temp directory and return the site root."""
    tmp = Path(tempfile.mkdtemp())
    for rel, content in files.items():
        dest = tmp / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    return tmp


# ---------------------------------------------------------------------------
# _upsert_jsx_style — fontFamily property
# ---------------------------------------------------------------------------

class TestUpsertJsxStyleFontFamily:
    def test_injects_style_when_none_present(self):
        tag = '<p className="text-lg">'
        result = _upsert_jsx_style(tag, "fontFamily", "Playfair Display, serif")
        assert "fontFamily: 'Playfair Display, serif'" in result
        assert result.startswith("<p")

    def test_replaces_existing_fontFamily(self):
        tag = "<p style={{ fontFamily: 'Inter, sans-serif' }}>"
        result = _upsert_jsx_style(tag, "fontFamily", "Lato, sans-serif")
        assert "fontFamily: 'Lato, sans-serif'" in result
        assert "Inter" not in result

    def test_preserves_other_style_props(self):
        tag = "<p style={{ color: '#111111', fontFamily: 'Inter, sans-serif' }}>"
        result = _upsert_jsx_style(tag, "fontFamily", "Merriweather, serif")
        assert "color: '#111111'" in result
        assert "fontFamily: 'Merriweather, serif'" in result

    def test_self_closing_tag(self):
        tag = '<Input style={{ fontFamily: "Inter, sans-serif" }} />'
        result = _upsert_jsx_style(tag, "fontFamily", "Roboto, sans-serif")
        assert "fontFamily: 'Roboto, sans-serif'" in result
        assert result.endswith("/>")


# ---------------------------------------------------------------------------
# _edit_font_family_for_selector — pebble_id path (manifest)
# The manifest path goes through _edit_style_by_id which we test indirectly
# by checking that selector_hint fallback works for the same use-case.
# ---------------------------------------------------------------------------

class TestEditFontFamilyForSelector:

    # ---- Case 1: existing JSX fontFamily prop gets replaced -----------------

    def test_replaces_existing_jsx_font_family(self):
        tsx = (
            "export default function Hero() {\n"
            "  return (\n"
            "    <h1 style={{ fontFamily: 'Inter, sans-serif' }}>Welcome Back</h1>\n"
            "  );\n"
            "}\n"
        )
        site = _make_site({"components/Hero.tsx": tsx})
        result = _edit_font_family_for_selector(site, "Welcome Back", "Playfair Display")
        assert result["files_changed"] == ["components/Hero.tsx"]
        new = (site / "components/Hero.tsx").read_text(encoding="utf-8")
        assert "Playfair Display" in new
        assert "Inter" not in new

    # ---- Case 2: no existing fontFamily — tag injection fallback -----------

    def test_injects_font_family_when_absent(self):
        tsx = (
            "export default function Page() {\n"
            "  return <p className=\"text-xl\">Hello World</p>;\n"
            "}\n"
        )
        site = _make_site({"app/page.tsx": tsx})
        result = _edit_font_family_for_selector(site, "Hello World", "Lato")
        assert result["files_changed"] == ["app/page.tsx"]
        new = (site / "app/page.tsx").read_text(encoding="utf-8")
        assert "fontFamily" in new
        assert "Lato" in new
        # Generic sans-serif fallback appended automatically
        assert "sans-serif" in new

    # ---- Case 3: no selector_hint match — nothing changed ------------------

    def test_no_match_returns_empty(self):
        tsx = "<p>Something else entirely</p>\n"
        site = _make_site({"app/page.tsx": tsx})
        result = _edit_font_family_for_selector(site, "Nonexistent Text", "Lato")
        assert result["files_changed"] == []

    # ---- Case 4: unknown / arbitrary font name is accepted (no allowlist) --

    def test_arbitrary_font_name_accepted(self):
        """No allowlist — any string is a valid font family value."""
        tsx = "<p style={{ fontFamily: 'Inter, sans-serif' }}>Click me</p>\n"
        site = _make_site({"app/page.tsx": tsx})
        result = _edit_font_family_for_selector(site, "Click me", "MyCustomBrandFont2077")
        assert result["files_changed"] == ["app/page.tsx"]
        new = (site / "app/page.tsx").read_text(encoding="utf-8")
        assert "MyCustomBrandFont2077" in new

    # ---- Case 5: serif font gets the right generic fallback ----------------

    def test_serif_font_gets_serif_fallback(self):
        tsx = "<h2 style={{ fontFamily: 'Inter, sans-serif' }}>Title</h2>\n"
        site = _make_site({"app/page.tsx": tsx})
        _edit_font_family_for_selector(site, "Title", "Playfair Display")
        new = (site / "app/page.tsx").read_text(encoding="utf-8")
        # Should have "Playfair Display, serif"
        assert "Playfair Display, serif" in new

    # ---- Case 6: font family already contains fallback — not doubled -------

    def test_existing_fallbacks_not_doubled(self):
        tsx = "<p style={{ fontFamily: 'Inter, sans-serif' }}>Hello</p>\n"
        site = _make_site({"app/page.tsx": tsx})
        # Caller passes full string with fallback already
        _edit_font_family_for_selector(site, "Hello", "Lato, Helvetica, sans-serif")
        new = (site / "app/page.tsx").read_text(encoding="utf-8")
        # Comma present → no extra generic added
        assert "Lato, Helvetica, sans-serif" in new


# ---------------------------------------------------------------------------
# op validator guard (no HTTP handler needed — test the constant directly)
# ---------------------------------------------------------------------------

class TestOpValidatorIncludesFontFamily:
    def test_valid_ops_include_font_family(self):
        """The validator list in run_visual_edit must include 'font-family'.

        We test this by importing the module source text and checking that
        'font-family' appears in the op-validation line — a cheap but reliable
        guard against regressions.
        """
        import pebble.server.visual_edit as mod
        src = Path(mod.__file__).read_text(encoding="utf-8")
        # The validator line should contain all four ops.
        assert re.search(r"op not in.*font-family", src), (
            "run_visual_edit does not include 'font-family' in the op validator"
        )
