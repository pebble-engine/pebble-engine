from pathlib import Path
from pebble.blocks.registry import BlockRegistry

BAKERY_ROOT = Path(__file__).parent.parent / "pebble" / "blocks"

def test_bakery_hero_artisan_loads():
    reg = BlockRegistry.load(BAKERY_ROOT)
    assert "bakery/hero_artisan" in reg
    block = reg["bakery/hero_artisan"]
    assert "{{headline}}" in block.template_source
    assert "{{hero_image}}" in block.template_source
    assert block.metadata.slots["hero_image"].pexels_query is not None
    assert "bread" in block.metadata.slots["hero_image"].pexels_query.lower()
