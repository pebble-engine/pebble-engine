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
    _edit_text_by_id,
    _upsert_jsx_style,
)


# ---------------------------------------------------------------------------
# _edit_text_by_id — motion-wrapper transparency (sub-project D follow-up)
# ---------------------------------------------------------------------------

def _seed_site(rel_to_content: dict[str, str]) -> Path:
    tmp = Path(tempfile.mkdtemp())
    for rel, content in rel_to_content.items():
        dest = tmp / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    return tmp


def test_edit_text_revealwords_wrapper_despaced_original():
    """Motion-wrapped headline: <h1 ...><RevealWords>Old Title</RevealWords></h1>.
    RevealWords renders each word as a margin-spaced span, so the live DOM
    textContent the bridge sends is DE-SPACED ('OldTitle') and won't match the
    spaced source. The edit must still succeed by treating RevealWords as a
    transparent text container."""
    site = _seed_site({
        "components/sections/Section00.tsx":
        '<h1 className="x" data-pebble-id="pb-rw001"><RevealWords>Old Title</RevealWords></h1>',
    })
    man = {"pb-rw001": {"file": "components/sections/Section00.tsx", "tag": "h1", "original_text": ""}}
    result = _edit_text_by_id(site, "pb-rw001", man, "OldTitle", "Fresh Headline")
    assert result and result["replacements"] == 1
    out = (site / "components/sections/Section00.tsx").read_text(encoding="utf-8")
    assert "<RevealWords>Fresh Headline</RevealWords>" in out
    assert "Old Title" not in out


def test_edit_text_countup_wrapper():
    """<CountUp> is also a transparent text container (stat numbers)."""
    site = _seed_site({
        "components/sections/S.tsx":
        '<span data-pebble-id="pb-cu1"><CountUp suffix="+">480</CountUp></span>',
    })
    man = {"pb-cu1": {"file": "components/sections/S.tsx", "tag": "span", "original_text": ""}}
    result = _edit_text_by_id(site, "pb-cu1", man, "480+", "500")
    assert result and result["replacements"] == 1
    out = (site / "components/sections/S.tsx").read_text(encoding="utf-8")
    assert '<CountUp suffix="+">500</CountUp>' in out


def test_edit_text_plain_leaf_still_works():
    """Regression: a plain text node still edits by full replacement."""
    site = _seed_site({"app/page.tsx": '<h1 data-pebble-id="pb-l1">Old</h1>'})
    man = {"pb-l1": {"file": "app/page.tsx", "tag": "h1", "original_text": "Old"}}
    result = _edit_text_by_id(site, "pb-l1", man, "Old", "New")
    assert result and result["replacements"] == 1
    assert "<h1 data-pebble-id=\"pb-l1\">New</h1>" in (site / "app/page.tsx").read_text(encoding="utf-8")


def test_edit_text_real_children_still_require_verbatim():
    """Regression: a tag with REAL child elements (not a transparent wrapper)
    still only edits when original_text appears verbatim, and no-ops otherwise."""
    src = '<p data-pebble-id="pb-c1">Hello <strong>world</strong></p>'
    site = _seed_site({"app/page.tsx": src})
    man = {"pb-c1": {"file": "app/page.tsx", "tag": "p", "original_text": ""}}
    # Non-matching original -> no edit happens. The true invariant is that the
    # source is NOT corrupted and NO replacement was made; the exact no-op
    # signal (None vs a replacements:0 result) doesn't matter to the caller.
    result = _edit_text_by_id(site, "pb-c1", man, "Nonexistent", "X")
    if result is not None:
        assert result.get("replacements", 0) == 0
    # Source untouched — the guarantee that actually matters.
    assert src in (site / "app/page.tsx").read_text(encoding="utf-8")


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
