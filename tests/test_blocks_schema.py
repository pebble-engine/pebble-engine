import pytest
from pebble.blocks.schema import BlockMetadata, validate_block_metadata

def test_minimal_valid_block_passes():
    meta = {
        "block_id": "library/hero_artisan_warm",
        "block_type": "hero",
        "vibe_tags": ["warm", "crafted"],
        "dna_tags": ["swiss_magazine"],
        "slots": {
            "headline": {"kind": "text", "max_chars": 80, "tone": "warm"}
        },
        "palette_slots": ["bg", "fg", "accent"],
    }
    result = validate_block_metadata(meta)
    assert result.block_id == "library/hero_artisan_warm"
    assert result.block_type == "hero"
    assert result.vibe_tags == ["warm", "crafted"]

def test_missing_block_id_raises():
    with pytest.raises(ValueError, match="block_id"):
        validate_block_metadata({"block_type": "hero", "vibe_tags": ["warm"]})

def test_unknown_slot_kind_raises():
    with pytest.raises(ValueError, match="slot kind"):
        validate_block_metadata({
            "block_id": "library/x_y",
            "block_type": "hero",
            "vibe_tags": ["warm"],
            "dna_tags": [],
            "slots": {"foo": {"kind": "video", "max_chars": 80}},
            "palette_slots": [],
        })

def test_empty_vibe_tags_raises():
    with pytest.raises(ValueError, match="vibe_tags"):
        validate_block_metadata({
            "block_id": "library/x_y",
            "block_type": "hero",
            "vibe_tags": [],
            "dna_tags": [],
            "slots": {},
            "palette_slots": [],
        })


def test_gallery_and_scroll_story_block_types_accepted():
    """The two structural-variety block types (sub-project C) must validate."""
    for btype in ("gallery", "scroll-story"):
        meta = {
            "block_id": f"library/x_{btype.replace('-', '_')}",
            "block_type": btype,
            "vibe_tags": ["editorial"],
            "dna_tags": [],
            "slots": {"headline": {"kind": "text"}},
            "palette_slots": ["bg", "fg", "accent"],
        }
        result = validate_block_metadata(meta)
        assert result.block_type == btype
