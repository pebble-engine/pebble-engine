"""Block metadata schema + validation.

A block is a (template.tsx, metadata.json) pair. The metadata describes
what slots the template exposes, what kind of content each slot accepts,
and which DNA cards the block is visually compatible with. The Sonnet
picker reads metadata to assemble copy briefs; the compiler reads
metadata to substitute slot values into the template.

Blocks are universal — a full-bleed hero, 3-col service grid, or
pull-quote testimonial layout works for any industry. The ``vibe_tags``
field describes the block's *aesthetic personality* (warm, minimal,
editorial…) so Sonnet can match a block to a brief by feel, not by
a hard industry filter.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SlotKind = Literal["text", "image", "list", "url"]
BlockType = Literal[
    "hero", "services", "about", "testimonials",
    "contact", "pricing", "footer", "gallery", "faq",
    "scroll-story", "trust", "coverage",
]

_VALID_SLOT_KINDS = {"text", "image", "list", "url"}
# keep in sync with BlockType
_ALLOWED_TYPES = {
    "hero", "services", "about", "testimonials", "contact",
    "pricing", "footer", "gallery", "faq", "scroll-story",
    "trust", "coverage",
}


@dataclass(frozen=True)
class SlotSpec:
    kind: SlotKind
    max_chars: int | None = None
    tone: str | None = None
    pexels_query_template: str | None = None   # templated with {industry_scene}, {mood}, etc.
    aspect: str | None = None


@dataclass(frozen=True)
class BlockMetadata:
    block_id: str           # "library/hero_artisan_warm"
    block_type: BlockType
    vibe_tags: list[str]    # e.g. ["warm", "crafted", "sensory", "small-batch"]
    dna_tags: list[str]
    slots: dict[str, SlotSpec]
    palette_slots: list[str]
    preview_image: str | None = None


def validate_block_metadata(raw: dict) -> BlockMetadata:
    """Validate a metadata.json dict and return a typed BlockMetadata.

    Raises ValueError on any structural issue. Keep error messages
    actionable — block authors will read them when their .json is
    rejected during library load.
    """
    for required in ("block_id", "block_type", "vibe_tags", "dna_tags",
                     "slots", "palette_slots"):
        if required not in raw:
            raise ValueError(f"block metadata missing required field: {required}")
    if raw["block_type"] not in _ALLOWED_TYPES:
        raise ValueError(
            f"block {raw.get('block_id', '?')!r}: unknown block_type {raw['block_type']!r}; "
            f"must be one of {sorted(_ALLOWED_TYPES)}"
        )
    vibe_tags = raw["vibe_tags"]
    if not isinstance(vibe_tags, list) or not vibe_tags:
        raise ValueError(
            f"block {raw.get('block_id', '?')!r}: vibe_tags must be a non-empty list of strings"
        )
    for tag in vibe_tags:
        if not isinstance(tag, str):
            raise ValueError(
                f"block {raw.get('block_id', '?')!r}: every vibe_tag must be a string, got {tag!r}"
            )
    slots = {}
    for slot_name, spec in raw["slots"].items():
        if spec.get("kind") not in _VALID_SLOT_KINDS:
            raise ValueError(
                f"slot kind {spec.get('kind')!r} invalid for slot {slot_name!r}; "
                f"must be one of {sorted(_VALID_SLOT_KINDS)}"
            )
        slots[slot_name] = SlotSpec(
            kind=spec["kind"],
            max_chars=spec.get("max_chars"),
            tone=spec.get("tone"),
            pexels_query_template=spec.get("pexels_query_template"),
            aspect=spec.get("aspect"),
        )
    return BlockMetadata(
        block_id=raw["block_id"],
        block_type=raw["block_type"],
        vibe_tags=list(raw["vibe_tags"]),
        dna_tags=list(raw["dna_tags"]),
        slots=slots,
        palette_slots=list(raw["palette_slots"]),
        preview_image=raw.get("preview_image"),
    )
