"""Layout DNA picker — structural archetype selection tests.

Mirrors test_dna_industry_affinity.py for the new Layout DNA system.
Locks in the affinity/aversion behavior, creative_direction routing,
seed determinism, and backward-compat guarantees introduced in the
May 2026 structural-variety overhaul.
"""
from __future__ import annotations

import pytest

from pebble.layout_dna import (
    LAYOUT_CARDS,
    build_layout_block,
    pick_layout_by_id,
    pick_layout_for_brief,
)

# ------------------------------------------------------------------ #
# Fixtures                                                             #
# ------------------------------------------------------------------ #

def _brief(business_type: str) -> dict:
    return {"business_type": business_type}


def _rolls(brief: dict, n: int = 500, **kwargs) -> list[str]:
    return [pick_layout_for_brief(brief, **kwargs)["id"] for _ in range(n)]


# ------------------------------------------------------------------ #
# Card schema                                                          #
# ------------------------------------------------------------------ #

REQUIRED_KEYS = {
    "id", "label", "feel", "hero_type", "hero_structure",
    "nav_pattern", "nav_structure", "section_flow",
    "information_density", "reading_mode",
    "use_animated_heading", "use_liquid_glass_nav",
    "use_fade_in_cascade", "use_grain_overlay",
    "industry_affinity", "industry_aversion",
    "keyword_triggers", "forbidden", "signature_moves",
}


def test_layout_cards_count():
    """Exactly 10 layout cards must be registered."""
    assert len(LAYOUT_CARDS) == 10, f"Expected 10 cards, got {len(LAYOUT_CARDS)}"


def test_every_card_has_required_keys():
    for card in LAYOUT_CARDS:
        missing = REQUIRED_KEYS - card.keys()
        assert not missing, f"Card {card.get('id', '?')} missing: {missing}"


def test_every_card_has_unique_id():
    ids = [c["id"] for c in LAYOUT_CARDS]
    assert len(ids) == len(set(ids)), f"Duplicate layout IDs: {ids}"


def test_affinity_and_aversion_are_lists():
    for card in LAYOUT_CARDS:
        assert isinstance(card["industry_affinity"], list), f"{card['id']} affinity not a list"
        assert isinstance(card["industry_aversion"], list), f"{card['id']} aversion not a list"


def test_use_flags_are_bools():
    bool_keys = ["use_animated_heading", "use_liquid_glass_nav", "use_fade_in_cascade", "use_grain_overlay"]
    for card in LAYOUT_CARDS:
        for k in bool_keys:
            assert isinstance(card[k], bool), f"{card['id']}.{k} should be bool"


def test_section_flow_is_list():
    for card in LAYOUT_CARDS:
        assert isinstance(card["section_flow"], list), f"{card['id']}.section_flow not a list"
        assert len(card["section_flow"]) >= 4, f"{card['id']}.section_flow too short"


# ------------------------------------------------------------------ #
# pick_layout_by_id                                                    #
# ------------------------------------------------------------------ #

def test_pick_by_id_returns_correct_card():
    card = pick_layout_by_id("gradient_mesh")
    assert card is not None
    assert card["id"] == "gradient_mesh"


def test_pick_by_id_returns_none_for_unknown():
    assert pick_layout_by_id("does_not_exist") is None


def test_pick_by_id_covers_all_cards():
    for card in LAYOUT_CARDS:
        found = pick_layout_by_id(card["id"])
        assert found is not None
        assert found["id"] == card["id"]


# ------------------------------------------------------------------ #
# Pinning                                                              #
# ------------------------------------------------------------------ #

def test_pinned_layout_dna_id_is_honored():
    """Explicit _layout_dna_id in brief overrides everything."""
    for card in LAYOUT_CARDS:
        brief = {"business_type": "wedding photographer", "_layout_dna_id": card["id"]}
        result = pick_layout_for_brief(brief)
        assert result["id"] == card["id"], (
            f"Pinned {card['id']} was not honored; got {result['id']}"
        )


# ------------------------------------------------------------------ #
# creative_direction routing                                            #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("cd,expected", [
    ("I want a terminal / command line aesthetic", "terminal"),
    ("No images, just bold typography and white space", "manifesto"),
    ("Photography portfolio with masonry gallery", "gallery_first"),
    ("Split screen editorial with half photo", "split_screen"),
    ("Dashboard showing open now status and availability", "weather_report"),
    ("One page simple site, everything compact", "single_screen"),
    ("Friendly conversational Q&A style", "chat_log"),
    ("Cards-based catalogue, no fuss", "index_card"),
    ("Long form essay journal reading experience", "magazine_scroll"),
    ("Modern gradient glow product startup", "gradient_mesh"),
])
def test_creative_direction_keyword_routing(cd, expected):
    brief = _brief("generic business")
    result = pick_layout_for_brief(brief, creative_direction=cd)
    assert result["id"] == expected, (
        f"creative_direction={cd!r} should route to {expected}, got {result['id']}"
    )


def test_creative_direction_in_brief_also_routes():
    """creative_direction stored inside the brief dict is also respected."""
    brief = {"business_type": "generic", "creative_direction": "terminal hacker cli"}
    result = pick_layout_for_brief(brief)
    assert result["id"] == "terminal"


# ------------------------------------------------------------------ #
# Industry affinity / aversion                                         #
# ------------------------------------------------------------------ #

def test_mechanic_shop_prefers_weather_report():
    """Mechanic shops need dense utility layout, not ambient product-site vibes."""
    rolls = _rolls(_brief("auto mechanic repair shop"))
    weather = sum(1 for r in rolls if r == "weather_report")
    assert weather >= 150, f"Mechanic should heavily favor weather_report; got {weather}/500"


def test_mechanic_never_picks_gradient_mesh():
    """Gradient mesh is listed in weather_report aversion — should never land
    on an auto repair brief."""
    rolls = _rolls(_brief("auto mechanic repair shop"))
    assert "gradient_mesh" not in rolls, (
        "gradient_mesh must be hard-excluded for mechanic brief"
    )


# ------------------------------------------------------------------ #
# Phase 23a (2026-05-20) — picker haystack regression                  #
# ------------------------------------------------------------------ #
# Triggered by Marc's 2026-05-20 mechanic build that rendered as
# Terminal DNA. Root cause: v3 intake set business_type="small_business"
# (not "auto_repair"), so the keyword "mechanic" lived only in
# business_name. The old picker haystack ignored business_name +
# extra_context, so Weather Report's affinity never matched and Terminal
# won safe-random by elimination.
# After this fix:
#   - haystack includes business_name, extra_context, notes_freeform
#   - Terminal has "small_business"/"local business"/"mechanic"/"plumb"/
#     etc. in its aversion → can't safe-random-pick onto a trades brief

def test_business_name_keywords_drive_picker():
    """When business_type is generic ('small_business') but business_name
    mentions the trade, the picker MUST still recognize it. This is the
    exact failure from 2026-05-20 morning. Both weather_report AND
    single_screen legitimately list 'mechanic' in affinity, so we assert
    the union covers virtually every pick."""
    brief = {
        "business_type": "small_business",
        "business_name": "Mechanic shop in Queens",
    }
    rolls = [pick_layout_for_brief(brief)["id"] for _ in range(200)]
    trades_friendly = sum(1 for r in rolls if r in ("weather_report", "single_screen"))
    assert trades_friendly >= 180, (
        f"Mechanic-in-business_name should drive Weather Report OR Single Screen; "
        f"got {trades_friendly}/200 (picks: {set(rolls)})"
    )
    # AND terminal must never appear
    assert "terminal" not in rolls, f"terminal must NEVER pick for mechanic; saw: {set(rolls)}"


def test_extra_context_keywords_drive_picker():
    """Same fix path via extra_context — the original idea text."""
    brief = {
        "business_type": "small_business",
        "extra_context": "I want to build a website for my plumbing company",
    }
    rolls = [pick_layout_for_brief(brief)["id"] for _ in range(200)]
    trades_friendly = sum(1 for r in rolls if r in ("weather_report", "single_screen"))
    assert trades_friendly >= 180, (
        f"plumbing-in-extra_context should drive trades-friendly layouts; "
        f"got {trades_friendly}/200 (picks: {set(rolls)})"
    )


def test_terminal_excluded_from_small_business():
    """Terminal must never safe-random onto a vague 'small_business' brief.
    Used to be the failure mode: 9 of 10 layouts had aversion-exclude,
    Terminal didn't, so it won by lottery."""
    brief = {"business_type": "small_business", "business_name": "Joe's Auto"}
    rolls = [pick_layout_for_brief(brief)["id"] for _ in range(200)]
    assert "terminal" not in rolls, (
        f"terminal must be excluded for small-business / trades briefs; "
        f"saw: {set(rolls)}"
    )


def test_terminal_still_picks_for_cybersecurity():
    """Sanity — narrowing Terminal's aversion must not break its core use."""
    brief = {"business_type": "cybersecurity firm"}
    rolls = [pick_layout_for_brief(brief)["id"] for _ in range(200)]
    terminal = sum(1 for r in rolls if r == "terminal")
    assert terminal >= 50, f"Terminal should still pick for cybersecurity; got {terminal}/200"


def test_plumbing_never_picks_gradient_mesh():
    rolls = _rolls(_brief("plumbing contractor"))
    assert "gradient_mesh" not in rolls


def test_tech_startup_prefers_gradient_mesh():
    rolls = _rolls(_brief("saas startup"))
    gradient = sum(1 for r in rolls if r == "gradient_mesh")
    assert gradient >= 100, f"Tech startup should favor gradient_mesh; got {gradient}/500"


def test_wedding_photographer_never_picks_weather_report():
    """Dense utility/dashboard layout is wrong for a wedding photographer."""
    rolls = _rolls(_brief("wedding photographer"))
    assert "weather_report" not in rolls, (
        "weather_report must be excluded for wedding photographer"
    )


def test_gallery_first_appears_for_photography_brief():
    """gallery_first should be a valid and regularly-picked layout for a
    photography studio brief. Multiple layouts legitimately match (manifesto,
    split_screen, magazine_scroll also have photo/studio affinity), so we
    only verify gallery_first isn't excluded — not that it dominates."""
    rolls = _rolls(_brief("photography studio portrait gallery"))
    gallery = sum(1 for r in rolls if r == "gallery_first")
    assert gallery >= 30, (
        f"gallery_first should be picked regularly for photo briefs; got {gallery}/500"
    )


# ------------------------------------------------------------------ #
# Seed determinism                                                      #
# ------------------------------------------------------------------ #

def test_seed_determinism():
    brief = _brief("wedding photographer")
    a = pick_layout_for_brief(brief, seed=42)
    b = pick_layout_for_brief(brief, seed=42)
    assert a["id"] == b["id"], "Same seed + same brief must produce same layout"


def test_different_seeds_produce_some_variety():
    # Use a brief that doesn't match any layout's affinity keywords — it falls
    # through to safe-random, which should produce wide variety across all 10
    # layouts for different seeds. "community theater group" produces ~10 distinct.
    brief = _brief("community theater group")
    ids = {pick_layout_for_brief(brief, seed=i)["id"] for i in range(50)}
    assert len(ids) >= 5, f"50 different seeds should produce variety; got {len(ids)} distinct"


# ------------------------------------------------------------------ #
# Edge cases                                                           #
# ------------------------------------------------------------------ #

def test_empty_brief_does_not_crash():
    card = pick_layout_for_brief({})
    assert card is not None
    assert "id" in card


def test_missing_business_type_does_not_crash():
    card = pick_layout_for_brief({"location": "Denver"})
    assert card is not None


def test_unknown_business_type_falls_back_to_variety():
    brief = _brief("miscellaneous ephemera exchange")
    ids = {pick_layout_for_brief(brief, seed=i)["id"] for i in range(50)}
    assert len(ids) >= 4, f"Unknown industry should produce layout variety; got {len(ids)} distinct"


def test_creative_direction_beats_industry_affinity():
    """creative_direction is priority 2, industry affinity is priority 3.
    A mechanic asking for 'manifesto typography' should get manifesto,
    not weather_report."""
    brief = _brief("auto mechanic repair shop")
    result = pick_layout_for_brief(brief, creative_direction="manifesto bold typography")
    assert result["id"] == "manifesto", (
        f"creative_direction should override industry affinity; got {result['id']}"
    )


# ------------------------------------------------------------------ #
# build_layout_block                                                   #
# ------------------------------------------------------------------ #

def test_build_layout_block_returns_string():
    for card in LAYOUT_CARDS:
        block = build_layout_block(card)
        assert isinstance(block, str), f"build_layout_block({card['id']}) did not return str"
        assert len(block) > 200, f"build_layout_block({card['id']}) looks too short"


def test_build_layout_block_mentions_layout_id():
    for card in LAYOUT_CARDS:
        block = build_layout_block(card)
        assert card["id"] in block, (
            f"build_layout_block should mention the layout id; {card['id']} not found"
        )


def test_build_layout_block_component_table_yes_for_gradient_mesh():
    card = pick_layout_by_id("gradient_mesh")
    block = build_layout_block(card)
    assert "AnimatedHeading" in block
    assert "✅ YES" in block


def test_build_layout_block_component_table_no_for_weather_report():
    """weather_report doesn't use AnimatedHeading or liquid-glass nav."""
    card = pick_layout_by_id("weather_report")
    block = build_layout_block(card)
    assert "❌ NO" in block  # at least one NO present


def test_build_layout_block_includes_section_flow():
    for card in LAYOUT_CARDS:
        block = build_layout_block(card)
        # Section flow items are rendered as title-case human labels:
        # "hero_split" → "Hero Split". Check the rendered form.
        first_section_rendered = card["section_flow"][0].replace("_", " ").title()
        assert first_section_rendered in block, (
            f"{card['id']} section_flow[0] rendered as {first_section_rendered!r} "
            f"not found in layout block"
        )


def test_build_layout_block_includes_signature_moves():
    for card in LAYOUT_CARDS:
        if card["signature_moves"]:
            block = build_layout_block(card)
            assert card["signature_moves"][0][:30] in block, (
                f"{card['id']} first signature move not found in layout block"
            )


def test_build_layout_block_mentions_layout_dna_header():
    """All blocks must contain the LAYOUT DNA header so the LLM can
    clearly distinguish it from the Style DNA block."""
    for card in LAYOUT_CARDS:
        block = build_layout_block(card)
        assert "LAYOUT DNA" in block, f"{card['id']} block missing LAYOUT DNA header"
