"""Load and look up blocks from the on-disk universal library.

The on-disk layout is `<namespace>/<block_id>.{json,tsx}`. The registry
walks the tree at load time, validates each metadata.json, and pairs it
with the sibling .tsx template source. Sonnet's block picker queries
this registry; the blocks_compiler uses it to retrieve template source
for substitution.

Blocks are universal — any block can serve any industry. The ``find``
method filters by ``vibe_tag`` (aesthetic personality) and/or
``block_type`` so Sonnet can assemble a site from the best-fit blocks
regardless of industry.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pebble.blocks.schema import BlockMetadata, BlockType, validate_block_metadata


@dataclass(frozen=True)
class Block:
    metadata: BlockMetadata
    template_source: str  # the raw .tsx file contents with {{slot}} placeholders


class BlockRegistry:
    def __init__(self, blocks: dict[str, Block]) -> None:
        self._blocks = blocks

    @classmethod
    def load(cls, root: Path) -> "BlockRegistry":
        """Walk `root/<namespace>/<name>.{json,tsx}` and build the registry."""
        out: dict[str, Block] = {}
        for namespace_dir in sorted(root.iterdir()):
            if not namespace_dir.is_dir():
                continue
            for json_path in sorted(namespace_dir.glob("*.json")):
                tsx_path = json_path.with_suffix(".tsx")
                if not tsx_path.exists():
                    raise ValueError(
                        f"block {json_path.name}: template file {tsx_path.name} "
                        f"missing in {namespace_dir.name}/"
                    )
                meta = validate_block_metadata(json.loads(json_path.read_text(encoding="utf-8")))
                out[meta.block_id] = Block(
                    metadata=meta,
                    template_source=tsx_path.read_text(encoding="utf-8"),
                )
        return cls(out)

    def __contains__(self, block_id: str) -> bool:
        return block_id in self._blocks

    def __getitem__(self, block_id: str) -> Block:
        return self._blocks[block_id]

    def find(self, *, vibe_tag: str | None = None,
             block_type: BlockType | None = None) -> list[Block]:
        """Return all blocks matching the filter.

        ``vibe_tag`` matches if the tag is in the block's vibe_tags list.
        ``block_type`` is an exact match.
        Both filters are AND-ed; omit either to skip that filter.
        """
        out = []
        for block in self._blocks.values():
            if block_type is not None and block.metadata.block_type != block_type:
                continue
            if vibe_tag is not None and vibe_tag not in block.metadata.vibe_tags:
                continue
            out.append(block)
        return out
