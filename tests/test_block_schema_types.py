from pebble.blocks.schema import validate_block_metadata


def _meta(block_type):
    return {
        "block_id": f"library/x_{block_type}",
        "block_type": block_type,
        "vibe_tags": ["trade-pro"],
        "dna_tags": ["terminal_operator"],
        "slots": {"headline": {"kind": "text", "max_chars": 80}},
        "palette_slots": ["bg", "fg", "accent", "accent_fg", "muted"],
    }


def test_trust_and_coverage_types_accepted():
    for t in ("trust", "coverage"):
        m = validate_block_metadata(_meta(t))
        assert m.block_type == t


def test_existing_types_still_accepted():
    for t in ("hero", "services", "about", "testimonials", "contact", "footer", "gallery"):
        assert validate_block_metadata(_meta(t)).block_type == t


def test_unknown_block_type_rejected():
    import pytest
    with pytest.raises(ValueError, match="bogus_never_a_type"):
        validate_block_metadata(_meta("bogus_never_a_type"))
