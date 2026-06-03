# tests/test_showcase_blocks.py
from pathlib import Path

from pebble.blocks.registry import BlockRegistry

LIB_ROOT = Path(__file__).resolve().parent.parent / "pebble" / "blocks"


def test_showcase_has_every_essential_section():
    reg = BlockRegistry.load(LIB_ROOT)
    by_type: dict[str, list[str]] = {}
    for blk in reg._blocks.values():
        if "showcase" in blk.metadata.vibe_tags:
            by_type.setdefault(blk.metadata.block_type, []).append(blk.metadata.block_id)
    # The showcase menu must cover every section its template uses.
    for section in ("hero", "services", "gallery", "contact", "footer"):
        assert by_type.get(section), f"no showcase block for essential section: {section}"


def test_showcase_new_blocks_use_next_image():
    """The 3 new showcase blocks are image-forward — they must use next/image,
    not raw <img> (Core Web Vitals + the images_use_next_image eval)."""
    reg = BlockRegistry.load(LIB_ROOT)
    for bid in ("library/hero_showcase", "library/gallery_showcase", "library/cta_banner_showcase"):
        src = reg._blocks[bid].template_source
        assert "next/image" in src, f"{bid} must import next/image"
        assert "<img" not in src, f"{bid} must not use raw <img>"
