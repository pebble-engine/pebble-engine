import pytest
from pebble.blocks.schema import BlockMetadata, validate_block_metadata

def test_minimal_valid_block_passes():
    meta = {
        "block_id": "bakery/hero_artisan",
        "block_type": "hero",
        "industry": "bakery",
        "dna_tags": ["swiss_magazine"],
        "slots": {
            "headline": {"kind": "text", "max_chars": 80, "tone": "warm"}
        },
        "palette_slots": ["bg", "fg", "accent"],
    }
    result = validate_block_metadata(meta)
    assert result.block_id == "bakery/hero_artisan"
    assert result.block_type == "hero"

def test_missing_block_id_raises():
    with pytest.raises(ValueError, match="block_id"):
        validate_block_metadata({"block_type": "hero", "industry": "bakery"})

def test_unknown_slot_kind_raises():
    with pytest.raises(ValueError, match="slot kind"):
        validate_block_metadata({
            "block_id": "x/y",
            "block_type": "hero",
            "industry": "bakery",
            "dna_tags": [],
            "slots": {"foo": {"kind": "video", "max_chars": 80}},
            "palette_slots": [],
        })
