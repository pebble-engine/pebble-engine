import json
from pathlib import Path

from pebble.blocks.registry import BlockRegistry
from pebble.server.build_v2 import _build_block_menu


def _make_registry(tmp_path: Path) -> BlockRegistry:
    """Block library with:
    - All 4 essential types (hero, services, contact, footer) tagged trade-pro
    - One extra hero tagged clean only

    This ensures the trade-pro vibe filter can engage (all essential types
    present) while the clean block gets excluded.
    """
    lib = tmp_path / "library"
    lib.mkdir(parents=True)
    # trade-pro blocks covering all 4 essential types
    trade_pro_blocks = [
        ("hero_trade_pro", "hero"),
        ("services_trade_pro", "services"),
        ("contact_trade_pro", "contact"),
        ("footer_trade_pro", "footer"),
    ]
    for bid, block_type in trade_pro_blocks:
        (lib / f"{bid}.json").write_text(json.dumps({
            "block_id": f"library/{bid}",
            "block_type": block_type,
            "vibe_tags": ["trade-pro"],
            "dna_tags": ["x"],
            "slots": {"headline": {"kind": "text", "max_chars": 80}},
            "palette_slots": ["bg", "fg", "accent", "accent_fg", "muted"],
        }), encoding="utf-8")
        (lib / f"{bid}.tsx").write_text("export default function X(){return null;}", encoding="utf-8")
    # clean-only block (different vibe, should be excluded when vibe=trade-pro)
    (lib / "hero_focused_clean.json").write_text(json.dumps({
        "block_id": "library/hero_focused_clean",
        "block_type": "hero",
        "vibe_tags": ["clean"],
        "dna_tags": ["x"],
        "slots": {"headline": {"kind": "text", "max_chars": 80}},
        "palette_slots": ["bg", "fg", "accent", "accent_fg", "muted"],
    }), encoding="utf-8")
    (lib / "hero_focused_clean.tsx").write_text("export default function X(){return null;}", encoding="utf-8")
    return BlockRegistry.load(tmp_path)


def test_vibe_pin_filters_menu(tmp_path):
    reg = _make_registry(tmp_path)
    menu = _build_block_menu(reg, vibe="trade-pro")
    ids = {b["block_id"] for b in menu}
    assert "library/hero_trade_pro" in ids
    assert "library/hero_focused_clean" not in ids
    assert len(menu) == 4  # 4 trade-pro blocks in the fixture


def test_no_vibe_returns_all(tmp_path):
    reg = _make_registry(tmp_path)
    menu = _build_block_menu(reg, vibe=None)
    ids = {b["block_id"] for b in menu}
    assert {"library/hero_trade_pro", "library/hero_focused_clean"} <= ids


def test_vibe_pin_falls_back_when_essential_section_missing(tmp_path):
    """If the vibe filter would leave the menu without an essential
    block_type (hero/services/contact/footer), return the unfiltered menu
    so a build never fails for lack of blocks. Verify by passing an unknown
    vibe — every essential type would be missing, so we get the full menu."""
    reg = _make_registry(tmp_path)
    menu = _build_block_menu(reg, vibe="nonexistent-vibe")
    ids = {b["block_id"] for b in menu}
    assert {"library/hero_trade_pro", "library/hero_focused_clean"} <= ids
