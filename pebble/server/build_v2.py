"""POST /api/v2/generate — the template-first build path.

Reads brief → loads block library for the matched industry → calls
Sonnet for block picks + copy → compiles site → writes build_meta.json
with engine_version=v2 → returns slug.

Cost: ~$0.05-0.08 per call. Latency: ~10-20s wall clock.
Replaces the multi-minute v1 pipeline in pebble/server/build.py
for new builds once Phase 4 cutover lands.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import re

from pebble.blocks.registry import BlockRegistry
from pebble.blocks_compiler import compile_site
from pebble.llm import get_llm_client
from pebble.sonnet_block_picker import pick_blocks_and_copy
from pebble.text import sanitize_business_name


_BLOCK_LIBRARY_ROOT = Path(__file__).parent.parent / "blocks"


def _output_dir() -> Path:
    engine = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if engine is not None and hasattr(engine, "OUTPUT_DIR"):
        return engine.OUTPUT_DIR
    return Path(__file__).parent.parent.parent / "output"


def _slugify(name: str) -> str:
    """Slug helper — delegates to pebble_engine when loaded (production),
    falls back to a local implementation under pytest / direct import."""
    engine = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if engine is not None and hasattr(engine, "_slugify"):
        return engine._slugify(name)
    # Local fallback — identical logic to pebble_engine._slugify
    text = re.sub(r"[^\w\s-]", "", name.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-") or "untitled"


def _build_menu(registry: BlockRegistry) -> list[dict]:
    """Shape ALL blocks in the registry into the Sonnet picker's menu.

    Industry is no longer a filter — Sonnet picks blocks that fit the
    brief's vibe regardless of which ``vibe_tags`` they carry. This makes
    the engine work for ANY industry the user types, not just the 7
    we initially seeded blocks for.
    """
    menu = []
    for block in registry._blocks.values():
        menu.append({
            "block_id": block.metadata.block_id,
            "block_type": block.metadata.block_type,
            "vibe_tags": list(block.metadata.vibe_tags),
            "slots": {
                name: {
                    "kind": s.kind,
                    "max_chars": s.max_chars,
                    "tone": s.tone,
                    "pexels_query_template": s.pexels_query_template,
                }
                for name, s in block.metadata.slots.items()
            },
            "palette_slots": list(block.metadata.palette_slots),
        })
    return menu


def run_build_v2(handler) -> None:
    # Body parse
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except (ValueError, TypeError):
        handler._json(400, {"error": "invalid Content-Length header"}); return
    if length <= 0:
        handler._json(400, {"error": "empty request body"}); return

    try:
        brief = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json body"}); return

    # Brief normalization
    raw_name = brief.get("business_name", "") or ""
    name = sanitize_business_name(raw_name) or "untitled"
    brief["business_name"] = name
    slug = _slugify(name)
    industry = (brief.get("industry") or "").strip().lower()

    # LLM client resolution — fail loud if env isn't configured
    client, reason = get_llm_client()
    if reason != "ok" or client is None:
        handler._json(503, {"error": f"LLM not configured: {reason}"}); return

    # Block library load + menu shaping
    registry = BlockRegistry.load(_BLOCK_LIBRARY_ROOT)
    menu = _build_menu(registry)
    if not menu:
        handler._json(503, {"error": "block library is empty — engine misconfigured"})
        return

    # Sonnet pick + copy
    try:
        spec = pick_blocks_and_copy(
            brief=brief, llm_client=client, block_menu=menu,
        )
    except ValueError as e:
        handler._json(502, {"error": f"LLM output rejected: {e}"}); return

    # Compile to disk
    project_dir = _output_dir() / slug
    site_dir = project_dir / "site"
    try:
        compile_site(
            registry=registry,
            block_picks=spec["block_picks"],
            palette=spec["palette"],
            out_dir=site_dir,
        )
    except ValueError as e:
        handler._json(500, {"error": f"compile failed: {e}"}); return

    # Persist brief + meta alongside the site
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "brief.json").write_text(
        json.dumps(brief, indent=2), encoding="utf-8"
    )
    (project_dir / "build_meta.json").write_text(
        json.dumps({
            "engine_version": "v2",
            "model": getattr(client, "model", None),
            "provider": getattr(client, "provider", None),
            "built_at": datetime.now(timezone.utc).isoformat(),
            "block_picks": [p["block_id"] for p in spec["block_picks"]],
            "industry": industry,
        }, indent=2),
        encoding="utf-8",
    )

    handler._json(200, {"slug": slug, "engine_version": "v2"})
