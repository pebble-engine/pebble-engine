from pathlib import Path

from pebble.blocks.registry import BlockRegistry

LIB_ROOT = Path(__file__).resolve().parent.parent / "pebble" / "blocks"


def test_trade_pro_has_every_essential_section():
    reg = BlockRegistry.load(LIB_ROOT)
    by_type: dict[str, list[str]] = {}
    for block in reg._blocks.values():
        if "trade-pro" in block.metadata.vibe_tags:
            by_type.setdefault(block.metadata.block_type, []).append(
                block.metadata.block_id
            )
    essential = (
        "hero", "trust", "services", "coverage",
        "gallery", "contact", "about", "testimonials", "footer",
    )
    for section in essential:
        assert by_type.get(section), (
            f"no trade-pro block for essential section: {section!r}; "
            f"trade-pro coverage map: {by_type}"
        )
