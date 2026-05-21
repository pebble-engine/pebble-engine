"""URL-extracted brand signals block tests (Phase 38d, 2026-05-21).

The `_build_url_extraction_block` helper in pebble_engine.py converts the
brief's `_extracted_*` fields into a focused prompt block. Tests pin:
- Empty-state copy when no extraction happened
- All field-presence permutations render correctly
- Inspire-source-URL paths trigger the strict "don't borrow content" framing
- Brand-mode paths surface the user's existing copy as creative direction
"""
from __future__ import annotations

import pytest

# Import lazily — pebble_engine has heavy side effects on import
import pebble_engine as engine


# ------------------------------------------------------------------ #
# Empty state                                                          #
# ------------------------------------------------------------------ #


def test_empty_brief_returns_no_extraction_message():
    block = engine._build_url_extraction_block({})
    assert "No URL was extracted" in block


def test_all_empty_strings_treated_as_no_extraction():
    block = engine._build_url_extraction_block({
        "_inspire_source_url": "",
        "_extracted_logo_url": "",
        "_extracted_hero_copy": "",
        "_extracted_tagline": "",
        "_brand_palette": [],
        "_design_dna_id": "",
    })
    assert "No URL was extracted" in block


def test_none_values_treated_as_no_extraction():
    block = engine._build_url_extraction_block({
        "_inspire_source_url": None,
        "_brand_palette": None,
    })
    assert "No URL was extracted" in block


# ------------------------------------------------------------------ #
# Inspire mode — strict "don't borrow content" framing                #
# ------------------------------------------------------------------ #


def test_inspire_url_includes_strict_warning():
    block = engine._build_url_extraction_block({
        "_inspire_source_url": "https://kinfolk.com",
    })
    assert "Inspiration source URL" in block
    assert "kinfolk.com" in block
    assert "do NOT borrow" in block or "do not borrow" in block.lower()


def test_inspire_mode_suppresses_existing_copy_blurbs():
    """When _inspire_source_url is set, _extracted_hero_copy / _extracted_tagline
    are about the REFERENCE site, not the user's. We should NOT surface them as
    'your existing copy' — that's misleading."""
    block = engine._build_url_extraction_block({
        "_inspire_source_url":   "https://kinfolk.com",
        "_extracted_hero_copy":  "A new way to live well.",
        "_extracted_tagline":    "Considered objects for everyday rituals.",
    })
    # The strict warning should still appear
    assert "Inspiration source URL" in block
    # But the "existing tagline from the user's site" framing must NOT appear
    assert "existing tagline from the user's site" not in block.lower()
    assert "existing hero copy from the user's site" not in block.lower()


def test_inspire_mode_still_includes_palette_as_signal():
    block = engine._build_url_extraction_block({
        "_inspire_source_url": "https://example.com",
        "_brand_palette":      ["#1a1a1a", "#fef3e2", "#c2410c"],
    })
    assert "#1a1a1a" in block
    assert "#fef3e2" in block
    assert "the inspiration site" in block.lower()


def test_inspire_mode_includes_pinned_dna():
    block = engine._build_url_extraction_block({
        "_inspire_source_url": "https://example.com",
        "_design_dna_id":      "cinematic_imax",
    })
    assert "cinematic_imax" in block
    assert "Pinned Style DNA" in block


# ------------------------------------------------------------------ #
# Brand mode — surface user's existing content as creative direction  #
# ------------------------------------------------------------------ #


def test_brand_mode_existing_hero_copy_framed_as_user_content():
    block = engine._build_url_extraction_block({
        "_extracted_hero_copy": "Sourdough, baked daily.",
        # No _inspire_source_url — so this IS the user's site
    })
    assert "Existing hero copy from the user's site" in block
    assert "Sourdough, baked daily." in block


def test_brand_mode_existing_tagline_framed_as_user_content():
    block = engine._build_url_extraction_block({
        "_extracted_tagline": "Wood-fired in Brooklyn since opening.",
    })
    assert "Existing tagline from the user's site" in block
    assert "Wood-fired" in block


def test_brand_mode_palette_attributes_to_user_site():
    block = engine._build_url_extraction_block({
        "_brand_palette": ["#c2410c", "#fef3e2"],
    })
    assert "the user's existing site" in block.lower()


def test_logo_url_surfaces_as_visual_reference():
    block = engine._build_url_extraction_block({
        "_extracted_logo_url": "https://acme.co/logo.svg",
    })
    assert "acme.co/logo.svg" in block
    # And it must include the don't-embed instruction
    assert "/app/icon.svg" in block


def test_favicon_only_surfaces_when_no_logo():
    """If we have a logo, the favicon is redundant — skip it. If we only
    have a favicon, surface it as visual reference."""
    block_with_logo = engine._build_url_extraction_block({
        "_extracted_logo_url":    "https://acme.co/logo.svg",
        "_extracted_favicon_url": "https://acme.co/favicon.ico",
    })
    assert "favicon.ico" not in block_with_logo  # logo wins

    block_favicon_only = engine._build_url_extraction_block({
        "_extracted_favicon_url": "https://acme.co/favicon.ico",
    })
    assert "favicon.ico" in block_favicon_only


# ------------------------------------------------------------------ #
# Full-rendering smoke check                                          #
# ------------------------------------------------------------------ #


def test_full_inspire_brief_renders_without_error():
    """Realistic inspire-mode brief — all fields populated. Block should
    render without any KeyError / format crash and include each field."""
    block = engine._build_url_extraction_block({
        "_inspire_source_url":     "https://stripe.com",
        "_extracted_logo_url":     "https://stripe.com/logo.svg",
        "_extracted_favicon_url":  "https://stripe.com/favicon.ico",
        "_extracted_hero_copy":    "Financial infrastructure for the internet.",
        "_extracted_tagline":      "Build the business model of tomorrow.",
        "_brand_palette":          ["#635bff", "#0a2540", "#ffffff"],
        "_design_dna_id":          "cinematic_imax",
    })
    assert "stripe.com" in block
    assert "#635bff" in block
    assert "cinematic_imax" in block
    # Inspire mode suppresses the user-site copy framing
    assert "existing hero copy from the user's site" not in block.lower()
    # Multiple paragraphs separated by blank lines
    assert "\n\n" in block
