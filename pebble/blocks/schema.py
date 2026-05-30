"""Block metadata schema + validation.

A block is a (template.tsx, metadata.json) pair. The metadata describes
what slots the template exposes, what kind of content each slot accepts,
and which DNA cards the block is visually compatible with. The Sonnet
picker reads metadata to assemble copy briefs; the compiler reads
metadata to substitute slot values into the template.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SlotKind = Literal["text", "image", "list", "url"]
BlockType = Literal[
    "hero", "services", "about", "testimonials",
    "contact", "pricing", "footer", "gallery", "faq",
]

_VALID_SLOT_KINDS = {"text", "image", "list", "url"}


@dataclass(frozen=True)
class SlotSpec:
    kind: SlotKind
    max_chars: int | None = None
    tone: str | None = None
    pexels_query: str | None = None
    aspect: str | None = None


@dataclass(frozen=True)
class BlockMetadata:
    block_id: str         # "bakery/hero_artisan"
    block_type: BlockType
    industry: str         # "bakery"
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
    for required in ("block_id", "block_type", "industry", "dna_tags",
                     "slots", "palette_slots"):
        if required not in raw:
            raise ValueError(f"block metadata missing required field: {required}")
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
            pexels_query=spec.get("pexels_query"),
            aspect=spec.get("aspect"),
        )
    return BlockMetadata(
        block_id=raw["block_id"],
        block_type=raw["block_type"],
        industry=raw["industry"],
        dna_tags=list(raw["dna_tags"]),
        slots=slots,
        palette_slots=list(raw["palette_slots"]),
        preview_image=raw.get("preview_image"),
    )
