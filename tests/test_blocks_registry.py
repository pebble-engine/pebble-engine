import json
import pytest
from pathlib import Path

from pebble.blocks.registry import BlockRegistry

def test_load_from_directory(tmp_path):
    lib = tmp_path / "library"
    lib.mkdir()
    (lib / "hero_artisan_warm.json").write_text(json.dumps({
        "block_id": "library/hero_artisan_warm",
        "block_type": "hero",
        "vibe_tags": ["warm", "crafted"],
        "dna_tags": ["swiss_magazine"],
        "slots": {"headline": {"kind": "text", "max_chars": 80}},
        "palette_slots": ["bg", "fg"],
    }))
    (lib / "hero_artisan_warm.tsx").write_text("<section>{{headline}}</section>")

    reg = BlockRegistry.load(tmp_path)

    assert "library/hero_artisan_warm" in reg
    block = reg["library/hero_artisan_warm"]
    assert block.metadata.block_type == "hero"
    assert "{{headline}}" in block.template_source

def test_lookup_by_vibe_tag_and_type(tmp_path):
    (tmp_path / "library").mkdir()
    for name, vibe in (("hero_artisan_warm", "warm"), ("hero_clean_minimal", "minimal")):
        (tmp_path / "library" / f"{name}.json").write_text(json.dumps({
            "block_id": f"library/{name}",
            "block_type": "hero",
            "vibe_tags": [vibe],
            "dna_tags": ["swiss_magazine"],
            "slots": {"headline": {"kind": "text"}},
            "palette_slots": [],
        }))
        (tmp_path / "library" / f"{name}.tsx").write_text("x")

    reg = BlockRegistry.load(tmp_path)
    warm_heroes = reg.find(vibe_tag="warm", block_type="hero")
    assert len(warm_heroes) == 1
    assert warm_heroes[0].metadata.block_id == "library/hero_artisan_warm"

def test_missing_template_file_raises(tmp_path):
    (tmp_path / "library").mkdir()
    (tmp_path / "library" / "orphan.json").write_text(json.dumps({
        "block_id": "library/orphan",
        "block_type": "hero",
        "vibe_tags": ["warm"],
        "dna_tags": [],
        "slots": {},
        "palette_slots": [],
    }))
    # no orphan.tsx
    with pytest.raises(ValueError, match="template file"):
        BlockRegistry.load(tmp_path)
