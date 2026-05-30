import json
from unittest.mock import MagicMock
import pytest

from pebble.sonnet_block_picker import pick_blocks_and_copy


def test_returns_parsed_block_picks_and_palette():
    """Happy path: Sonnet returns valid JSON, picker returns it parsed."""
    fake_response = json.dumps({
        "block_picks": [
            {
                "block_id": "bakery/hero_artisan",
                "slot_values": {
                    "eyebrow": "Brooklyn",
                    "headline": "Sourdough, every morning",
                    "subheadline": "Real bread.",
                    "cta_primary": "Reserve",
                    "cta_secondary": "About",
                    "hero_image": "[pexels:sourdough]",
                },
            }
        ],
        "palette": {"bg": "stone-50", "fg": "stone-900", "accent": "orange-700"},
    })
    fake_client = MagicMock()
    fake_client.generate.return_value = fake_response

    result = pick_blocks_and_copy(
        brief={"business_name": "Stoneground Loaf", "industry": "bakery",
               "extra_context": "Brooklyn sourdough subscription"},
        llm_client=fake_client,
        block_menu=[{
            "block_id": "bakery/hero_artisan", "block_type": "hero",
            "slots": {"headline": {"max_chars": 80, "kind": "text"}},
        }],
    )

    assert len(result["block_picks"]) == 1
    assert result["block_picks"][0]["block_id"] == "bakery/hero_artisan"
    assert result["palette"]["bg"] == "stone-50"


def test_prompt_includes_brief_and_block_menu():
    """The prompt must give Sonnet: business brief, full block menu,
    vibe-matching guidance, and Pexels query resolution instructions."""
    fake_client = MagicMock()
    fake_client.generate.return_value = '{"block_picks":[], "palette":{}}'

    pick_blocks_and_copy(
        brief={"business_name": "Stoneground Loaf", "industry": "bakery",
               "extra_context": "Brooklyn sourdough"},
        llm_client=fake_client,
        block_menu=[{
            "block_id": "library/hero_artisan_warm",
            "block_type": "hero",
            "vibe_tags": ["warm", "crafted"],
            "slots": {"headline": {"max_chars": 80, "kind": "text", "pexels_query_template": None}},
            "palette_slots": ["bg", "fg", "accent"],
        }],
    )

    prompt = fake_client.generate.call_args.kwargs.get("user", "") or fake_client.generate.call_args[0][0]
    # Brief is included
    assert "Stoneground Loaf" in prompt
    assert "Brooklyn sourdough" in prompt
    # Block menu is included
    assert "library/hero_artisan_warm" in prompt
    # Vibe-matching guidance is present (new in R3)
    assert "vibe_tags" in prompt
    # Pexels guidance is present (new in R3)
    assert "pexels" in prompt.lower()


def test_handles_json_wrapped_in_prose():
    """Sonnet sometimes wraps JSON in 'Here's the spec:' style preamble.
    The picker must extract the first {...} block regardless."""
    fake_client = MagicMock()
    fake_client.generate.return_value = (
        "Sure! Here's the spec for Stoneground Loaf:\n\n"
        '{"block_picks": [{"block_id": "bakery/hero_artisan", "slot_values": {"headline": "x"}}], '
        '"palette": {"bg": "stone-50"}}\n\n'
        "Let me know if you'd like any changes."
    )

    result = pick_blocks_and_copy(
        brief={"business_name": "x", "industry": "bakery"},
        llm_client=fake_client,
        block_menu=[],
    )
    assert result["block_picks"][0]["block_id"] == "bakery/hero_artisan"


def test_rejects_no_json_in_response():
    fake_client = MagicMock()
    fake_client.generate.return_value = "I cannot help with that request."

    with pytest.raises(ValueError, match="no JSON"):
        pick_blocks_and_copy(
            brief={"business_name": "x", "industry": "bakery"},
            llm_client=fake_client,
            block_menu=[],
        )


def test_rejects_malformed_json():
    fake_client = MagicMock()
    fake_client.generate.return_value = '{this is not real json, malformed}'

    with pytest.raises(ValueError, match="invalid JSON"):
        pick_blocks_and_copy(
            brief={"business_name": "x", "industry": "bakery"},
            llm_client=fake_client,
            block_menu=[],
        )


def test_rejects_invented_block_id():
    """Sonnet must only pick from the menu. Inventing a block_id is a
    fatal error — the compiler can't render an unknown block."""
    fake_client = MagicMock()
    fake_client.generate.return_value = json.dumps({
        "block_picks": [
            {"block_id": "bakery/imaginary_block", "slot_values": {}}
        ],
        "palette": {"bg": "stone-50"},
    })

    with pytest.raises(ValueError, match="invented|unknown block_id"):
        pick_blocks_and_copy(
            brief={"business_name": "x", "industry": "bakery"},
            llm_client=fake_client,
            block_menu=[{"block_id": "bakery/hero_artisan", "block_type": "hero", "slots": {}}],
        )


def test_picker_passes_through_resolved_pexels_queries():
    """When Sonnet writes a real Pexels query for an image slot, the
    picker passes it through unchanged — no template processing needed."""
    fake_client = MagicMock()
    fake_client.generate.return_value = json.dumps({
        "block_picks": [{
            "block_id": "library/hero_artisan_warm",
            "slot_values": {
                "headline": "Real bread",
                "hero_image": "artisan sourdough bakery interior warm sunlight",
            },
        }],
        "palette": {"bg": "stone-50"},
    })

    result = pick_blocks_and_copy(
        brief={"business_name": "x", "industry": "bakery"},
        llm_client=fake_client,
        block_menu=[{"block_id": "library/hero_artisan_warm", "block_type": "hero", "vibe_tags": ["warm"], "slots": {}, "palette_slots": []}],
    )

    assert result["block_picks"][0]["slot_values"]["hero_image"] == \
        "artisan sourdough bakery interior warm sunlight"
