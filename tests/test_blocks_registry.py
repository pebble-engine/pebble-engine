import json
import pytest
from pathlib import Path

from pebble.blocks.registry import BlockRegistry

def test_load_from_directory(tmp_path):
    bakery = tmp_path / "bakery"
    bakery.mkdir()
    (bakery / "hero_artisan.json").write_text(json.dumps({
        "block_id": "bakery/hero_artisan",
        "block_type": "hero",
        "industry": "bakery",
        "dna_tags": ["swiss_magazine"],
        "slots": {"headline": {"kind": "text", "max_chars": 80}},
        "palette_slots": ["bg", "fg"],
    }))
    (bakery / "hero_artisan.tsx").write_text("<section>{{headline}}</section>")

    reg = BlockRegistry.load(tmp_path)

    assert "bakery/hero_artisan" in reg
    block = reg["bakery/hero_artisan"]
    assert block.metadata.block_type == "hero"
    assert "{{headline}}" in block.template_source

def test_lookup_by_industry_and_type(tmp_path):
    (tmp_path / "bakery").mkdir()
    for name in ("hero_artisan", "hero_clean"):
        (tmp_path / "bakery" / f"{name}.json").write_text(json.dumps({
            "block_id": f"bakery/{name}",
            "block_type": "hero",
            "industry": "bakery",
            "dna_tags": ["swiss_magazine"],
            "slots": {"headline": {"kind": "text"}},
            "palette_slots": [],
        }))
        (tmp_path / "bakery" / f"{name}.tsx").write_text("x")

    reg = BlockRegistry.load(tmp_path)
    heroes = reg.find(industry="bakery", block_type="hero")
    assert len(heroes) == 2
    assert {h.metadata.block_id for h in heroes} == {"bakery/hero_artisan", "bakery/hero_clean"}

def test_missing_template_file_raises(tmp_path):
    (tmp_path / "bakery").mkdir()
    (tmp_path / "bakery" / "orphan.json").write_text(json.dumps({
        "block_id": "bakery/orphan",
        "block_type": "hero",
        "industry": "bakery",
        "dna_tags": [],
        "slots": {},
        "palette_slots": [],
    }))
    # no orphan.tsx
    with pytest.raises(ValueError, match="template file"):
        BlockRegistry.load(tmp_path)
