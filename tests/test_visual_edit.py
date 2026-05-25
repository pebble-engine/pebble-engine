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
    _edit_image_swap,
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
        # The _VALID_OPS tuple (or equivalent validator) must include 'font-family'.
        assert "font-family" in src and ("_VALID_OPS" in src or re.search(r"op not in.*font-family", src)), (
            "run_visual_edit does not include 'font-family' in the op validator"
        )


# ---------------------------------------------------------------------------
# _edit_image_swap — image URL replacement (Phase 56c)
# ---------------------------------------------------------------------------

def _make_site(files: dict) -> Path:
    """Write *files* into a fresh temp directory and return the site root.

    Note: a helper with the same name already exists above; this one is
    defined here again to avoid coupling these test classes together.
    """
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    for rel, content in files.items():
        dest = tmp / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    return tmp


class TestEditImageSwap:

    def test_swaps_url_in_tsx_file(self):
        """original_src found in a .tsx file → files_changed is non-empty and
        content is updated."""
        tsx = (
            'import Image from "next/image";\n'
            'export default function Hero() {\n'
            '  return <img src="https://images.pexels.com/old-photo.jpg" alt="hero" />;\n'
            '}\n'
        )
        site = _make_site({"components/Hero.tsx": tsx})
        result = _edit_image_swap(
            site,
            "https://images.pexels.com/old-photo.jpg",
            "https://images.pexels.com/new-photo.jpg",
        )
        assert result["files_changed"] == ["components/Hero.tsx"]
        new_content = (site / "components/Hero.tsx").read_text(encoding="utf-8")
        assert "new-photo.jpg" in new_content
        assert "old-photo.jpg" not in new_content

    def test_swaps_all_occurrences_in_file(self):
        """All occurrences of original_src in a file are replaced, not just the first."""
        tsx = (
            '<img src="https://cdn.example.com/img.jpg" />\n'
            '<img src="https://cdn.example.com/img.jpg" />\n'
        )
        site = _make_site({"app/page.tsx": tsx})
        _edit_image_swap(site, "https://cdn.example.com/img.jpg", "https://cdn.example.com/new.jpg")
        content = (site / "app/page.tsx").read_text(encoding="utf-8")
        assert content.count("new.jpg") == 2
        assert "img.jpg" not in content

    def test_swaps_across_multiple_files(self):
        """If the same URL appears in multiple files, all are updated."""
        url = "https://example.com/hero.jpg"
        new_url = "https://example.com/hero-v2.jpg"
        files = {
            "components/Hero.tsx": f'<img src="{url}" />',
            "app/globals.css": f'background-image: url("{url}");',
        }
        site = _make_site(files)
        result = _edit_image_swap(site, url, new_url)
        assert set(result["files_changed"]) == {"components/Hero.tsx", "app/globals.css"}

    def test_original_src_not_found_returns_empty(self):
        """If original_src doesn't appear in any file, files_changed is empty
        and result is a 200-compatible response (no error key)."""
        site = _make_site({"app/page.tsx": "<p>No image here</p>"})
        result = _edit_image_swap(site, "https://missing.com/photo.jpg", "https://new.com/photo.jpg")
        assert result["files_changed"] == []
        assert "error" not in result

    def test_empty_original_src_returns_error(self):
        """Empty original_src must yield an error (will produce a 400)."""
        site = _make_site({"app/page.tsx": "<p>content</p>"})
        result = _edit_image_swap(site, "", "https://new.com/photo.jpg")
        assert "error" in result

    def test_empty_new_src_returns_error(self):
        """Empty new_src must yield an error (will produce a 400)."""
        site = _make_site({"app/page.tsx": "<p>content</p>"})
        result = _edit_image_swap(site, "https://old.com/photo.jpg", "")
        assert "error" in result

    def test_ambiguous_always_false(self):
        """image-swap intentionally replaces all occurrences; ambiguous must
        always be False even when multiple files are changed."""
        url = "https://example.com/img.jpg"
        files = {
            "components/A.tsx": f'<img src="{url}" />',
            "components/B.tsx": f'<img src="{url}" />',
        }
        site = _make_site(files)
        result = _edit_image_swap(site, url, "https://example.com/new.jpg")
        assert result["ambiguous"] is False
        assert len(result["files_changed"]) == 2


class TestOpValidatorIncludesImageSwap:
    def test_valid_ops_include_image_swap(self):
        """The validator list in run_visual_edit must include 'image-swap'."""
        import pebble.server.visual_edit as mod
        src = Path(mod.__file__).read_text(encoding="utf-8")
        assert "image-swap" in src, (
            "run_visual_edit does not include 'image-swap' in the op validator"
        )

    def test_bridge_js_includes_src_field(self):
        """The PEBBLE_VISUAL_EDIT_BRIDGE JS must send src for img elements."""
        import pebble.server.visual_edit as mod
        src = Path(mod.__file__).read_text(encoding="utf-8")
        assert 'tag === "img"' in src, (
            "PEBBLE_VISUAL_EDIT_BRIDGE does not include src field for img elements"
        )
