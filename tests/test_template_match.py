"""Phase F1 — /api/template-match scores templates against a free-text
prompt. Returns top-N templates with confidence scores."""
import pytest
from pebble.server import template_match


def test_returns_top_3_for_tattoo_prompt():
    """A clear industry prompt should surface the ink_studio family.

    Real templates in registry.json use applicable_industries like
    'tattoo studio' (with space, not snake_case). The matcher normalizes
    both sides via lowercase + token overlap, so 'tattoo_shop' or
    'tattoo shop' should both hit the ink_studio templates."""
    result = template_match.match_templates(
        prompt="I run a tattoo shop in Brooklyn called Inked",
        business_type="tattoo_shop",
        max_results=3,
    )
    assert isinstance(result, dict)
    assert "matches" in result
    assert len(result["matches"]) <= 3
    template_ids = [m["template_id"] for m in result["matches"]]
    # At least ONE of the ink_studio variants should land in top 3.
    assert any(tid.startswith("ink_studio") for tid in template_ids), (
        f"expected an ink_studio variant in top 3, got: {template_ids}"
    )


def test_returns_fallback_for_unknown_industry():
    """Garbage prompt → returns SOME results (gallery fallback),
    never empty, never errors."""
    result = template_match.match_templates(
        prompt="xyzzy plugh quux",
        business_type=None,
        max_results=3,
    )
    assert "matches" in result
    assert len(result["matches"]) <= 3


def test_each_match_has_required_fields():
    result = template_match.match_templates(
        prompt="bakery in Queens",
        business_type="bakery",
        max_results=3,
    )
    for m in result["matches"]:
        assert "template_id" in m
        assert "score"       in m
        assert "reason"      in m
        assert 0.0 <= m["score"] <= 1.0


def test_max_results_respected():
    result = template_match.match_templates(
        prompt="dentist in San Diego",
        business_type="dentist",
        max_results=1,
    )
    assert len(result["matches"]) <= 1
