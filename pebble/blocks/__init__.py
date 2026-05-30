"""Block library — DNA-themed drop-in sections.

Pebble's structural differentiator over Lovable/Base44-style template
galleries is the **Style DNA** system: 13 over-specified personalities
that govern palette, typography, motion, and signature moves. The block
library leverages that.

Each block (testimonial trio, pricing tiers, FAQ accordion, feature
grid, CTA banner, stats strip) ships as a *skeleton* with placeholder
copy + themable tokens. When the user inserts one, we look up the
site's active DNA card, derive a :class:`ThemeTokens` palette/fonts/
posture bundle, and render the block's JSX against those tokens.

Because everything is deterministic (no LLM call), block insertion is
**free** (``billable: false``) — same philosophy as the visual editor.

Entry points:

- :data:`BLOCK_REGISTRY` — dict of ``{block_id: BlockSpec}``
- :func:`render_block` — given a spec + theme + brief, return JSX
- :func:`insert_block_into_site` — write the component file + update
  ``app/page.tsx`` imports & render
"""
from __future__ import annotations

from pebble.blocks.base import (
    BlockSpec,
    ThemeTokens,
    derive_theme_from_dna,
    extract_palette_hexes,
)
from pebble.blocks.insert import insert_block_into_site
from pebble.blocks.catalog import BLOCK_REGISTRY, list_blocks, render_block

__all__ = [
    "BLOCK_REGISTRY",
    "BlockSpec",
    "ThemeTokens",
    "derive_theme_from_dna",
    "extract_palette_hexes",
    "insert_block_into_site",
    "list_blocks",
    "render_block",
]
