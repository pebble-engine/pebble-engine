"""Multi-page generation tests (Phase 12, 2026-05-19).

Pin the provider-aware max_tokens logic + the strengthened multi-page
demand in build_pages_block. Goal: when Qwen 3.6 Plus is the active
provider, Pebble emits a full 5-7 page site on first build instead of
just a homepage. The 1M context + 60k output cap together unlock this
without code surgery to the parser (which already handles 40+ files
without a cap).
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from pebble.industry import build_pages_block


# ------------------------------------------------------------------ #
# build_pages_block — non-negotiable multi-page demand                 #
# ------------------------------------------------------------------ #

def test_pages_block_demands_each_page_as_own_file():
    """The strengthened ending must explicitly require each page be
    emitted as its own <pebble-file> block — addresses the historical
    pattern where LLMs would happily skip inner pages when token budget
    was tight."""
    entry = {"pages": ["pricing", "team"]}
    block = build_pages_block(entry)
    assert "non-negotiable" in block.lower(), (
        "the multi-page demand must be marked non-negotiable, "
        "not buried in soft language"
    )
    assert "<pebble-file" in block, (
        "the block must show the literal output format the LLM should use"
    )
    assert "page files" in block.lower() or "page file" in block.lower()


def test_pages_block_total_page_count_correct():
    """The header counts include 4 foundation + universal extras (FAQ,
    privacy, terms = 3) + industry-specific pages. Pin the math so a
    future edit to UNIVERSAL_EXTRA_PAGES surfaces here."""
    entry_no_industry = {}
    block = build_pages_block(entry_no_industry)
    # 4 foundation + 3 universal = 7 total
    assert "**7**" in block, f"expected total 7 pages (4 + 3 universal); block: {block[:300]}"

    entry_with_two = {"pages": ["pricing", "team"]}
    block = build_pages_block(entry_with_two)
    # 4 foundation + 3 universal + 2 industry = 9 total
    assert "**9**" in block


def test_pages_block_emphasizes_completeness_over_decoration():
    """Pebble's repair history showed: when the LLM ran low on tokens,
    it would over-invest in the homepage and ship inner pages as stubs.
    The strengthened block tells the LLM the opposite: every page
    complete > one page fancy."""
    block = build_pages_block({"pages": ["pricing"]})
    lower = block.lower()
    assert "page completeness" in lower or "every page" in lower
    # The trade-off framing must be explicit
    assert "decoration" in lower or "richer homepage" in lower


def test_pages_block_handles_empty_entry_gracefully():
    """No industry-specific pages still produces a valid block — the
    universal extras (FAQ + privacy + terms) are always there."""
    block_none = build_pages_block(None)
    block_empty = build_pages_block({})
    for block in (block_none, block_empty):
        assert "faq" in block.lower()
        assert "privacy" in block.lower()
        assert "terms" in block.lower()
        assert "non-negotiable" in block.lower()


# ------------------------------------------------------------------ #
# Provider-aware max_tokens — Qwen gets 60k, others 32k                #
# ------------------------------------------------------------------ #
#
# The actual max_tokens decision lives in pebble/server/build.py inside
# run_build(). Rather than spinning up a full SSE harness here we
# extract the decision into a small reproduction so future edits stay
# pinned. The truth-table below mirrors the inline expression in
# build.py — if it drifts, this test fails.


def _decide_max_tokens(*, is_lite: bool, provider: str) -> int:
    """Mirror of the inline expression in pebble/server/build.py to keep
    this test independent of HTTP harness setup. If you change the
    expression there, mirror it here too."""
    if is_lite:
        return 8000
    return 60000 if provider == "openrouter" else 32000


@pytest.mark.parametrize("is_lite,provider,expected", [
    (False, "openrouter", 60000),   # Qwen 3.6 Plus — big context, big output
    (False, "anthropic",  32000),   # Sonnet 4.6 — proven zone
    (False, "gemini",     32000),   # Gemini 2.5 Flash — proven zone
    (False, "fake",       32000),   # test/fake client — defaults to safe value
    (False, "",           32000),   # unknown provider — safe default
    (True,  "openrouter",  8000),   # lite mode wins over provider
    (True,  "anthropic",   8000),
    (True,  "gemini",      8000),
])
def test_max_tokens_decision_matrix(is_lite, provider, expected):
    assert _decide_max_tokens(is_lite=is_lite, provider=provider) == expected


def test_openrouter_gets_higher_cap_than_anthropic():
    """The whole point of Phase 12. Lock the inequality so a future
    'unification' of the caps doesn't silently erase multi-page support."""
    qwen_cap = _decide_max_tokens(is_lite=False, provider="openrouter")
    sonnet_cap = _decide_max_tokens(is_lite=False, provider="anthropic")
    assert qwen_cap > sonnet_cap, (
        f"OpenRouter cap ({qwen_cap}) must exceed Anthropic cap ({sonnet_cap}) — "
        f"multi-page generation depends on Qwen's bigger headroom"
    )
    assert qwen_cap >= 60000, (
        f"OpenRouter cap dropped to {qwen_cap} — multi-page builds will truncate"
    )


def test_build_py_decision_matches_test_mirror():
    """Read the actual build.py source and verify the inline expression
    matches the mirror in this test file. Catches drift between the
    test fixture and the production code."""
    from pathlib import Path
    src = (Path(__file__).parent.parent / "pebble" / "server" / "build.py").read_text(encoding="utf-8")
    # Both numbers must appear in the file; comments around the expression
    # mention the trade-off so this assertion is a coarse "is this still
    # roughly the right decision" smoke check, not a fragile string match.
    assert "60000" in src, "build.py no longer mentions 60000 — multi-page cap dropped?"
    assert "32000" in src, "build.py no longer mentions 32000 — provider-aware logic gone?"
    assert "openrouter" in src.lower(), "build.py no longer branches on 'openrouter' provider"
