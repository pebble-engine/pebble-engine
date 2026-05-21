"""sanitize_business_name tests (Phase 20a, 2026-05-20).

Triggered by Marc's 2026-05-20 mechanic build that rendered "Mechanic shop
inQueens" as its H1 because brief.business_name was passed to the LLM
verbatim. This module pins the title-case + camelCase-split behavior so
the bug can't return.
"""
from __future__ import annotations

import pytest

from pebble.text import sanitize_business_name


# ------------------------------------------------------------------ #
# The smoking gun — the actual 2026-05-20 mechanic build              #
# ------------------------------------------------------------------ #


def test_the_actual_mechanic_bug():
    """'Mechanic shop inQueens' must become 'Mechanic Shop In Queens'."""
    assert sanitize_business_name("Mechanic shop inQueens") == "Mechanic Shop In Queens"


# ------------------------------------------------------------------ #
# Title-case basics                                                    #
# ------------------------------------------------------------------ #


def test_all_lowercase_is_title_cased():
    assert sanitize_business_name("mechanic shop in queens") == "Mechanic Shop In Queens"


def test_already_title_cased_is_unchanged():
    assert sanitize_business_name("Mechanic Shop In Queens") == "Mechanic Shop In Queens"


def test_mixed_case_words_title_cased():
    assert sanitize_business_name("Joe's plumbing") == "Joe's Plumbing"


# ------------------------------------------------------------------ #
# Brand casing must be preserved                                       #
# ------------------------------------------------------------------ #


def test_iphone_brand_casing_preserved():
    """iPhone has a 1-char lowercase prefix — must NOT split or restyle."""
    assert sanitize_business_name("iPhone Repair") == "iPhone Repair"


def test_ipad_brand_casing_preserved():
    assert sanitize_business_name("iPad Cracked-Screen Pros") == "iPad Cracked-Screen Pros"


def test_ebay_brand_casing_preserved():
    assert sanitize_business_name("eBay Reseller HQ") == "eBay Reseller HQ"


def test_all_caps_brand_preserved():
    """ACME, AT&T, IBM-style names stay as the user typed them."""
    assert sanitize_business_name("ACME Corp") == "ACME Corp"
    assert sanitize_business_name("IBM Consulting") == "IBM Consulting"


def test_mcdonald_internal_cap_preserved():
    """McDonald has an internal capital and should not be retitled."""
    assert sanitize_business_name("McDonald Properties") == "McDonald Properties"


# ------------------------------------------------------------------ #
# camelCase splitter — the Marc autocorrect class                      #
# ------------------------------------------------------------------ #


def test_camelcase_run_is_split():
    assert sanitize_business_name("PebbleEngine Studios") == "Pebble Engine Studios"


def test_lowercase_two_chars_then_uppercase_splits():
    """'inQueens' must split — 'in' is the most common preposition users
    autocorrect-mash into the next word."""
    assert sanitize_business_name("Mike's inQueens Bike Shop") == "Mike's In Queens Bike Shop"


def test_lowercase_one_char_then_uppercase_does_not_split():
    """'iPhone' single-char prefix must NOT split (preserves brand)."""
    assert "i Phone" not in sanitize_business_name("iPhone Mechanic")


# ------------------------------------------------------------------ #
# Whitespace handling                                                  #
# ------------------------------------------------------------------ #


def test_collapses_multiple_spaces():
    assert sanitize_business_name("Mechanic    Shop   In    Queens") == "Mechanic Shop In Queens"


def test_strips_leading_trailing_whitespace():
    assert sanitize_business_name("  Mechanic Shop  ") == "Mechanic Shop"


def test_handles_tabs_and_newlines():
    assert sanitize_business_name("Mechanic\tShop\nIn Queens") == "Mechanic Shop In Queens"


# ------------------------------------------------------------------ #
# Empty / None handling                                                #
# ------------------------------------------------------------------ #


def test_empty_string_returns_empty():
    assert sanitize_business_name("") == ""


def test_whitespace_only_returns_empty():
    assert sanitize_business_name("    ") == ""


def test_none_returns_empty():
    # Permissive: callers may forward None from an absent brief field
    assert sanitize_business_name(None) == ""  # type: ignore[arg-type]


# ------------------------------------------------------------------ #
# Punctuation                                                          #
# ------------------------------------------------------------------ #


def test_apostrophe_preserved():
    assert sanitize_business_name("joe's diner") == "Joe's Diner"


def test_ampersand_preserved():
    assert sanitize_business_name("smith & sons") == "Smith & Sons"


def test_hyphen_preserved():
    assert sanitize_business_name("rock-solid auto") == "Rock-solid Auto"


# ------------------------------------------------------------------ #
# Real-world brief samples                                             #
# ------------------------------------------------------------------ #


@pytest.mark.parametrize("raw,expected", [
    ("blue dog yoga", "Blue Dog Yoga"),
    ("THE Coffee Shop", "THE Coffee Shop"),  # preserves THE
    ("the coffee shop", "The Coffee Shop"),
    ("queens-style pizzeria", "Queens-style Pizzeria"),
    ("Smith&Sons", "Smith&Sons"),  # no space to split on
    ("a", "A"),  # single letter
    ("a b c", "A B C"),
])
def test_real_world_samples(raw: str, expected: str):
    assert sanitize_business_name(raw) == expected
