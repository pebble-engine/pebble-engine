"""Pexels resolver swaps [pexels:query] tags with real image URLs."""
import re
from unittest.mock import patch, MagicMock
import pytest

from pebble.pexels_resolver import resolve_pexels_tags, _extract_pexels_tags


# ---- tag extraction ----

def test_extract_simple_tag():
    src = '<img src="[pexels: artisan bread]" alt="">'
    assert _extract_pexels_tags(src) == ["artisan bread"]


def test_extract_multiple_tags():
    src = '''
        <img src="[pexels: bakery interior]" />
        <img src="[pexels: sourdough close up]" />
        <img src="[pexels: baker portrait]" />
    '''
    tags = _extract_pexels_tags(src)
    assert tags == ["bakery interior", "sourdough close up", "baker portrait"]


def test_extract_dedupes_repeated_queries():
    """If the same query appears twice (e.g. shared service image), we
    only call Pexels once."""
    src = '<img src="[pexels: bread]" /><img src="[pexels: bread]" />'
    assert _extract_pexels_tags(src) == ["bread"]


def test_no_tags_returns_empty():
    src = '<img src="https://images.pexels.com/already-a-real-url.jpg" />'
    assert _extract_pexels_tags(src) == []


# ---- whole-file resolution ----

def test_resolve_swaps_tags_with_real_urls():
    src = '<img src="[pexels: bakery interior]" alt="Hero" />'

    fake_fetch = MagicMock(return_value="https://images.pexels.com/photos/123/hero.jpg")

    with patch("pebble.pexels_resolver._fetch_pexels_image_url", fake_fetch):
        out = resolve_pexels_tags(src)

    assert "[pexels:" not in out
    assert "https://images.pexels.com/photos/123/hero.jpg" in out
    fake_fetch.assert_called_once_with("bakery interior")


def test_resolve_handles_multiple_unique_queries():
    src = '''
        <img src="[pexels: hero scene]" />
        <img src="[pexels: services close up]" />
    '''
    fake_fetch = MagicMock(side_effect=lambda q: f"https://pexels.com/{q.replace(' ', '_')}.jpg")

    with patch("pebble.pexels_resolver._fetch_pexels_image_url", fake_fetch):
        out = resolve_pexels_tags(src)

    assert "[pexels:" not in out
    assert "hero_scene.jpg" in out
    assert "services_close_up.jpg" in out
    assert fake_fetch.call_count == 2


def test_resolve_fallback_to_placeholder_on_fetch_fail():
    """If Pexels API fails for a query, swap the tag with a neutral
    placeholder URL — DO NOT leave the [pexels: ...] string in the
    output (would 404 in production). The placeholder should be a
    cheap, always-available image."""
    src = '<img src="[pexels: extremely obscure query nothing matches]" />'
    fake_fetch = MagicMock(return_value=None)  # simulate no results

    with patch("pebble.pexels_resolver._fetch_pexels_image_url", fake_fetch):
        out = resolve_pexels_tags(src)

    assert "[pexels:" not in out
    # We use a Picsum random fallback (always works, never 404s)
    assert "picsum.photos" in out


def test_resolve_caches_repeated_queries_within_a_call():
    """One Pexels API call per unique query, even if the tag appears 5x."""
    src = '<img src="[pexels: same query]" /><img src="[pexels: same query]" /><img src="[pexels: same query]" />'
    fake_fetch = MagicMock(return_value="https://pexels.com/cached.jpg")

    with patch("pebble.pexels_resolver._fetch_pexels_image_url", fake_fetch):
        resolve_pexels_tags(src)

    fake_fetch.assert_called_once_with("same query")
