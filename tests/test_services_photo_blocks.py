# tests/test_services_photo_blocks.py
from pathlib import Path

from pebble.blocks.registry import BlockRegistry

LIB_ROOT = Path(__file__).resolve().parent.parent / "pebble" / "blocks"

PHOTO_SERVICES = ("library/services_grid_trade", "library/services_photo_grid")


def test_photo_services_blocks_declare_per_item_image():
    reg = BlockRegistry.load(LIB_ROOT)
    for bid in PHOTO_SERVICES:
        blk = reg._blocks[bid]
        # services block type
        assert blk.metadata.block_type == "services", bid
        # the template renders a per-item image
        assert "{{services[].image}}" in blk.template_source, bid


def test_photo_services_palette_parity():
    """Every declared palette_slot must appear in the template (no drift)."""
    reg = BlockRegistry.load(LIB_ROOT)
    for bid in PHOTO_SERVICES:
        blk = reg._blocks[bid]
        for slot in blk.metadata.palette_slots:
            token = "{{" + slot + "}}"
            assert token in blk.template_source, f"{bid}: declared palette slot {slot!r} unused in template"
