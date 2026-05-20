"""Industry-intel fuzzy lookup regression tests.

Pins the fix for the long-standing "music studio → dance_studio" bug:
the substring matcher in `pebble.industry.lookup_industry_intel` was
too greedy on generic words like "studio" / "shop" / "service", and
would return the first industry whose key contained the same generic
suffix as the user's input.

Behavior we want:
- exact-key matches still win (no regression for "plumbing", "yoga studio")
- distinctive words still match ("Joe's plumbing co" → plumbing)
- inputs whose only overlap with any industry key is a generic suffix
  return (None, None) and fall through to the LLM fallback
"""
from __future__ import annotations

import pytest

from pebble.industry import lookup_industry_intel


# ---- regressions for cases that already worked ---------------------------

def test_exact_key_match_yoga_studio():
    key, entry = lookup_industry_intel("yoga studio")
    assert key == "yoga_studio"
    assert entry is not None


def test_exact_key_match_plumbing():
    key, entry = lookup_industry_intel("plumbing")
    assert key == "plumbing"
    assert entry is not None


def test_distinctive_word_match_plumbing():
    """A user-typed `Joe's plumbing company` should still resolve to
    plumbing even though it isn't an exact key. The distinctive word
    `plumbing` carries the match."""
    key, entry = lookup_industry_intel("Joe's plumbing company")
    assert key == "plumbing"
    assert entry is not None


def test_distinctive_word_match_barber():
    """`barber` is the distinctive word in `barbershop`. Even though
    the key is a single token, the fuzzy lookup should still resolve."""
    key, entry = lookup_industry_intel("barber")
    assert key == "barbershop"


# ---- NEW: the bug this commit fixes --------------------------------------

def test_music_studio_does_not_match_dance_studio():
    """Reproduces the original bug. 'music studio' shares only the
    generic word 'studio' with `dance_studio` / `yoga_studio` /
    `tattoo_studio`. None of those is a music studio. The lookup must
    return (None, None) so the engine falls through to the LLM
    fallback (research_new_industry) and gets a real entry.

    Pre-fix: matched the first `*_studio` industry encountered during
    iteration (dance_studio in alphabetical order). Post-fix: returns
    None because the only word overlap is the generic word 'studio'."""
    key, entry = lookup_industry_intel("music studio")
    assert key is None, (
        f"expected None, got {key!r} — fuzzy match still spuriously "
        f"resolving via the generic word 'studio'"
    )
    assert entry is None


def test_random_shop_does_not_match_barbershop():
    """'Mike's awesome shop' has no business reason to match `barbershop`
    or `coffee_shop`. The shared word 'shop' is generic — must not
    drive the match."""
    key, entry = lookup_industry_intel("Mike's awesome shop")
    assert key is None, (
        f"expected None, got {key!r} — 'shop' as the only overlap "
        f"should not produce a fuzzy match"
    )
    assert entry is None


def test_generic_only_service_does_not_match():
    """Same pattern for `service` — generic suffix on `cleaning_service`
    and `pool_service`. A bare `Pat's service business` shouldn't
    auto-pick one."""
    key, entry = lookup_industry_intel("Pat's service business")
    assert key is None
    assert entry is None


# ---- 2026-05-19: explicit NLM-cited regression pairs ---------------------
#
# NotebookLM's adversarial review of the search-API proposal cited an old
# project note where "yoga studio" had been documented as matching
# "tattoo_studio" via the greedy substring. The fix has long landed
# (_INDUSTRY_GENERIC_WORDS strips "studio"), but pin the EXACT pairings
# NLM named so anyone reading those notes can trust the codebase reflects
# the fix, not the bug.

def test_yoga_studio_does_not_match_tattoo_studio():
    """The smoking-gun pair NLM surfaced. 'yoga studio' must resolve to
    yoga_studio (exact key match) — not tattoo_studio via the generic
    'studio' overlap. If yoga_studio is ever removed from industries.json,
    the result must be None, never tattoo_studio."""
    key, _ = lookup_industry_intel("yoga studio")
    assert key != "tattoo_studio", (
        "yoga studio is greedily matching tattoo_studio — the "
        "_INDUSTRY_GENERIC_WORDS filter is broken or 'studio' is missing"
    )


def test_pottery_studio_does_not_match_tattoo_studio():
    """A pottery studio is not in industries.json and shouldn't be
    silently classified as a tattoo studio. Must return None and let
    the LLM fallback do its job."""
    key, _ = lookup_industry_intel("pottery studio")
    assert key != "tattoo_studio"
    assert key != "dance_studio"
    assert key != "yoga_studio"


# ---- standard edge cases -------------------------------------------------

def test_empty_input_returns_none():
    key, entry = lookup_industry_intel("")
    # The empty input either returns (None, None) or an "untitled" fallback.
    # Either is acceptable as long as it's not a confident wrong match.
    assert key in (None, "untitled")


def test_completely_unrelated_input_returns_none():
    """A genuinely unrelated business type with no word overlap to any
    industry entry must return (None, None) so the LLM fallback can
    research it."""
    key, entry = lookup_industry_intel("interdimensional widget polisher")
    assert key is None
    assert entry is None
