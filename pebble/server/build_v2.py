"""POST /api/v2/generate (+ /api/v2/generate-stream) — template-first build.

Reads brief → loads the universal block library → calls Sonnet for block
picks + copy → compiles a section-per-file Next.js site (with motion
primitives) → resolves Pexels images → injects data-pebble-id for
click-to-edit → writes build_meta.json with engine_version=v2.

Cost: ~$0.05-0.08 per call. Latency: ~10-30s wall clock.

Two entry points share one handler-free core (``build_v2_core``):
  - ``run_build_v2(handler)``    — synchronous JSON (POST /api/v2/generate)
  - ``build_v2_core(brief, cb)`` — used by the SSE stream generator so the
    v3 workspace's live build feed works the same as it does for v1.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import re

from pebble.blocks.registry import BlockRegistry
from pebble.blocks_compiler import compile_site
from pebble.llm import get_llm_client
from pebble.pexels_resolver import resolve_pexels_tags
from pebble.sonnet_block_picker import pick_blocks_and_copy
from pebble.text import sanitize_business_name
from pebble.visual_ids import inject_pebble_ids


_BLOCK_LIBRARY_ROOT = Path(__file__).parent.parent / "blocks"


class BuildV2Error(Exception):
    """Raised by build_v2_core on a recoverable build failure. Carries the
    HTTP status the synchronous endpoint should return."""

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


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
    text = re.sub(r"[^\w\s-]", "", name.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-") or "untitled"


def _build_menu(registry: BlockRegistry) -> list[dict]:
    """Shape ALL blocks in the registry into the Sonnet picker's menu.

    Industry is not a filter — Sonnet picks blocks that fit the brief's vibe,
    so the engine works for ANY industry the user types.
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


def build_v2_core(brief: dict, progress_cb=None) -> dict:
    """Run a full v2 build. Handler-free so both the JSON endpoint and the
    SSE stream can call it.

    ``progress_cb(event_type, data)`` — optional. Called with the same SSE
    event vocabulary the v1 stream uses, so the v3 workspace feed renders
    identically: started → industry → style → generating → writing →
    preview_ready → done.

    Returns a GenerateResponse-shaped dict. Raises BuildV2Error on a
    recoverable failure (caller maps .status to an HTTP code / error event).
    """
    started = time.monotonic()

    def emit(event_type: str, data: dict) -> None:
        if progress_cb is not None:
            try:
                progress_cb(event_type, data)
            except Exception:
                pass  # progress is best-effort; never fail the build on it

    # Brief normalization
    raw_name = brief.get("business_name", "") or ""
    name = sanitize_business_name(raw_name) or "untitled"
    brief["business_name"] = name
    slug = _slugify(name)
    industry = (brief.get("industry") or "").strip().lower()

    emit("started", {"slug": slug, "business_name": name})

    # LLM client
    client, reason = get_llm_client()
    if reason != "ok" or client is None:
        raise BuildV2Error(503, f"LLM not configured: {reason}")

    emit("industry", {"key": industry or None})

    # Block library + menu
    registry = BlockRegistry.load(_BLOCK_LIBRARY_ROOT)
    menu = _build_menu(registry)
    if not menu:
        raise BuildV2Error(503, "block library is empty — engine misconfigured")

    emit("generating", {"model": getattr(client, "model", "") or "", "max_tokens": 8000})

    # Sonnet pick + copy
    try:
        spec = pick_blocks_and_copy(brief=brief, llm_client=client, block_menu=menu)
    except ValueError as e:
        raise BuildV2Error(502, f"LLM output rejected: {e}")

    # Prefer the clean business name Sonnet extracted from the brief over the
    # raw (possibly conversational) input — e.g. "My wife and I run a mobile
    # dog grooming van called Sudsy Paws…" → "Sudsy Paws". Re-slug to match so
    # the project dir, plan title, and hero all use the real brand name.
    extracted = sanitize_business_name(spec.get("business_name", "") or "")
    if extracted and extracted.lower() != name.lower():
        name = extracted
        brief["business_name"] = name
        slug = _slugify(name)
        emit("started", {"slug": slug, "business_name": name})  # correct the feed

    palette = spec.get("palette", {})
    block_ids = [p["block_id"] for p in spec.get("block_picks", [])]
    emit("style", {
        "dna_label": "Vibe-matched", "dna_id": "v2",
        "palette": [v for v in palette.values()][:5],
        "signature_moves": [],
    })

    # Compile
    project_dir = _output_dir() / slug
    site_dir = project_dir / "site"
    try:
        compile_site(
            registry=registry,
            block_picks=spec["block_picks"],
            palette=palette,
            out_dir=site_dir,
        )
    except ValueError as e:
        raise BuildV2Error(500, f"compile failed: {e}")

    # Pexels resolution across section files
    sections_dir = site_dir / "components" / "sections"
    if sections_dir.exists():
        for sec in sorted(sections_dir.glob("*.tsx")):
            sec.write_text(resolve_pexels_tags(sec.read_text(encoding="utf-8")),
                           encoding="utf-8")

    # data-pebble-id manifest for click-to-edit
    inject_pebble_ids(site_dir)

    # Count files for the feed + response
    files_written = sorted(
        p.relative_to(site_dir).as_posix()
        for p in site_dir.rglob("*")
        if p.is_file() and "node_modules" not in p.parts
    )
    emit("writing", {"file_count": len(files_written)})

    # Persist brief + meta
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "brief.json").write_text(json.dumps(brief, indent=2), encoding="utf-8")
    (project_dir / "build_meta.json").write_text(
        json.dumps({
            "engine_version": "v2",
            "model": getattr(client, "model", None),
            "provider": getattr(client, "provider", None),
            "built_at": datetime.now(timezone.utc).isoformat(),
            "block_picks": block_ids,
            "industry": industry,
        }, indent=2),
        encoding="utf-8",
    )

    preview_url = f"/preview/{slug}/"
    emit("preview_ready", {"slug": slug, "url": preview_url})

    elapsed = round(time.monotonic() - started, 2)
    result = {
        "slug": slug,
        "preview_url": preview_url,
        "saved_to": str(project_dir),
        "files_written": files_written,
        "file_count": len(files_written),
        "elapsed_seconds": elapsed,
        "industry_intel_key": industry or None,
        "engine_version": "v2",
    }
    return result


def run_build_v2(handler) -> None:
    """POST /api/v2/generate — synchronous JSON. Thin wrapper over the core."""
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

    try:
        result = build_v2_core(brief)
    except BuildV2Error as e:
        handler._json(e.status, {"error": e.message}); return

    # Keep the slim historical contract too (slug + engine_version) by merging.
    handler._json(200, result)
