"""Industry-aware DNA picker.

Random `pick_random_dna()` produced catastrophic mismatches like Terminal
Operator on a wedding photographer's site (marlowe-bay-weddings, 2026-05-17).
This suite locks in the affinity (10× boost) and aversion (hard exclude)
behavior of the new `pick_dna_for_brief` function. See
`feedback_dna_fonts_must_be_google.md` for the broader DNA-quality work.
"""
from __future__ import annotations

from style_dna import DNA_CARDS, pick_dna_for_brief, pick_random_dna


def _wedding_brief():
    return {"business_type": "wedding photographer"}


def _software_brief():
    return {"business_type": "software consultancy"}


def _plumbing_brief():
    return {"business_type": "plumbing contractor"}


def _law_brief():
    return {"business_type": "boutique law firm"}


def _coffee_brief():
    return {"business_type": "coffee roaster and cafe"}


def test_pick_dna_for_brief_exists():
    assert callable(pick_dna_for_brief)


def test_every_card_has_affinity_and_aversion_lists():
    for card in DNA_CARDS:
        assert "industry_affinity" in card, f"{card['id']} missing industry_affinity"
        assert "industry_aversion" in card, f"{card['id']} missing industry_aversion"
        assert isinstance(card["industry_affinity"], list)
        assert isinstance(card["industry_aversion"], list)


def test_wedding_brief_never_picks_terminal_operator():
    """The smoking gun from 2026-05-17 5-build convergence study:
    terminal_operator landed on marlowe-bay-weddings and produced a
    green CRT terminal overlay on a wedding ceremony photo."""
    rolls = [pick_dna_for_brief(_wedding_brief())["id"] for _ in range(500)]
    assert "terminal_operator" not in rolls


def test_wedding_brief_never_picks_brutalist_or_industrial():
    rolls = [pick_dna_for_brief(_wedding_brief())["id"] for _ in range(500)]
    assert "brutalist_editorial" not in rolls
    assert "industrial_freight" not in rolls


def test_wedding_brief_prefers_editorial_or_lifestyle():
    rolls = [pick_dna_for_brief(_wedding_brief())["id"] for _ in range(500)]
    suitable = {"arthouse_folio", "garden_press", "tactile_y2k", "marina", "velvet_lounge"}
    suitable_count = sum(1 for r in rolls if r in suitable)
    assert suitable_count >= 350, (
        f"Wedding picks should favor editorial/lifestyle; got {suitable_count}/500"
    )


def test_software_brief_prefers_tech_dnas():
    """Mean is ~351/500; threshold 320 = mean - 3 SD allows statistical noise."""
    rolls = [pick_dna_for_brief(_software_brief())["id"] for _ in range(500)]
    suitable = {"brutalist_editorial", "terminal_operator", "neue_haas_minimal"}
    suitable_count = sum(1 for r in rolls if r in suitable)
    assert suitable_count >= 320, (
        f"tech DNAs should dominate software briefs; got {suitable_count}/500"
    )


def test_software_brief_never_picks_tactile_y2k():
    """Soft Y2K aesthetic doesn't sell distributed-systems consulting."""
    rolls = [pick_dna_for_brief(_software_brief())["id"] for _ in range(500)]
    assert "tactile_y2k" not in rolls


def test_plumbing_brief_prefers_industrial_freight():
    rolls = [pick_dna_for_brief(_plumbing_brief())["id"] for _ in range(500)]
    industrial_count = sum(1 for r in rolls if r == "industrial_freight")
    assert industrial_count >= 150, (
        f"Plumbing should heavily favor industrial_freight; got {industrial_count}/500"
    )


def test_plumbing_brief_never_picks_velvet_or_y2k():
    rolls = [pick_dna_for_brief(_plumbing_brief())["id"] for _ in range(500)]
    assert "velvet_lounge" not in rolls
    assert "tactile_y2k" not in rolls
    assert "garden_press" not in rolls


def test_law_firm_prefers_editorial_or_minimal():
    rolls = [pick_dna_for_brief(_law_brief())["id"] for _ in range(500)]
    suitable = {"swiss_magazine", "neue_haas_minimal", "arthouse_folio"}
    suitable_count = sum(1 for r in rolls if r in suitable)
    assert suitable_count >= 350


def test_law_firm_never_picks_postmodern_or_terminal():
    rolls = [pick_dna_for_brief(_law_brief())["id"] for _ in range(500)]
    assert "postmodern_max" not in rolls
    assert "terminal_operator" not in rolls


def test_coffee_roaster_picks_diverse_but_not_industrial():
    """Coffee roasters can be edgy (postmodern), warm (garden_press), or
    moody (velvet_lounge). All three are acceptable. What we DON'T want
    is freight-aesthetics or terminal."""
    rolls = [pick_dna_for_brief(_coffee_brief())["id"] for _ in range(500)]
    assert "terminal_operator" not in rolls
    assert "industrial_freight" not in rolls
    # And the good fits should dominate:
    suitable = {"postmodern_max", "garden_press", "velvet_lounge", "tactile_y2k"}
    suitable_count = sum(1 for r in rolls if r in suitable)
    assert suitable_count >= 350


def test_unmatched_brief_falls_back_to_diverse_distribution():
    brief = {"business_type": "miscellaneous goods exchange"}
    rolls = {pick_dna_for_brief(brief)["id"] for _ in range(200)}
    assert len(rolls) >= 8, (
        f"Unmatched briefs should still produce variety; got {len(rolls)} distinct"
    )


def test_seed_determinism():
    """Same seed + same brief = same pick. Needed for snapshot tests."""
    brief = _wedding_brief()
    a = pick_dna_for_brief(brief, seed=42)
    b = pick_dna_for_brief(brief, seed=42)
    assert a["id"] == b["id"]


def test_empty_brief_does_not_crash():
    card = pick_dna_for_brief({})
    assert card is not None
    assert "id" in card


def test_missing_business_type_does_not_crash():
    card = pick_dna_for_brief({"location": "Boston"})
    assert card is not None
    assert "id" in card


def test_business_type_matching_is_case_insensitive():
    """The picker lowercases business_type before substring matching,
    so a user typing 'WEDDING PHOTOGRAPHER' or 'Wedding Photographer'
    routes the same as 'wedding photographer'. Locks the behavior the
    intake form depends on."""
    lower = {"business_type": "wedding photographer"}
    upper = {"business_type": "WEDDING PHOTOGRAPHER"}
    title = {"business_type": "Wedding Photographer"}
    # All three should hard-exclude terminal_operator
    for brief in (lower, upper, title):
        rolls = [pick_dna_for_brief(brief)["id"] for _ in range(200)]
        assert "terminal_operator" not in rolls, (
            f"case variant {brief['business_type']!r} should still exclude terminal_operator"
        )


def test_extra_whitespace_in_business_type_does_not_break_matching():
    """Real intake forms sometimes ship trailing/leading whitespace."""
    brief = {"business_type": "  wedding photographer  "}
    rolls = [pick_dna_for_brief(brief)["id"] for _ in range(200)]
    assert "terminal_operator" not in rolls


def test_pick_random_dna_still_works_unchanged():
    """Backward compat: existing tests + callers using pick_random_dna
    must continue to see uniform-random behavior across all 13 cards."""
    rolls = {pick_random_dna()["id"] for _ in range(200)}
    assert len(rolls) >= 10, (
        f"pick_random_dna should remain uniform-random; got {len(rolls)} distinct"
    )
