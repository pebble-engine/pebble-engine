"""HTTP handlers for the block library.

Routes:

- ``GET  /api/blocks``                       — list available block specs
- ``POST /api/projects/<slug>/blocks/insert`` — insert one into a site

Insertion is deterministic + free (``billable: false``) — same posture
as the visual editor. Every insert snapshots the site first so the
user can undo via the existing rollback flow.

Ownership is enforced via :func:`pebble.security.require_project_owner`.
The insert route is the FIRST mutating project endpoint in the codebase
that's behind that gate from day one — refine/visual-edit/rollback
predate the auth system and don't yet check (separate cleanup).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from pebble.blocks import (
    BLOCK_REGISTRY,
    derive_theme_from_dna,
    insert_block_into_site,
    list_blocks,
    render_block,
)
from pebble.blocks.insert import load_brief, load_dna_for_site
from pebble.engagement import log_event as _log_engagement
from pebble.history import snapshot_site
from pebble.log import log
from pebble.security import project_lock, require_project_owner


def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


# ---- GET /api/blocks -----------------------------------------------------

def run_list_blocks(handler) -> None:
    """Return the public block catalog. No auth required — the catalog
    is the same for every user and contains no private data."""
    handler._json(200, {
        "blocks":  list_blocks(),
        "count":   len(BLOCK_REGISTRY),
    })


# ---- POST /api/projects/<slug>/blocks/insert -----------------------------

def run_insert_block(handler, slug: str) -> None:
    """Insert a block into the project at ``slug``.

    Body: ``{ "block_id": "<id>" }``.

    Response 200:
        {
          "slug":            "...",
          "block_id":        "...",
          "component_name":  "Testimonials",
          "files_written":   ["components/sections/Testimonials.tsx"],
          "files_modified":  ["app/page.tsx"],
          "snapshot_id":     "20260515T...-insert-block-testimonials_trio",
          "position":        "before-footer" | "before-main-close" | ...,
          "billable":        false,
          "dna_id":          "swiss_magazine",
          "applied_at":      "2026-05-15T..."
        }

    Errors:
        400 — invalid body / unknown block_id
        404 — project or site dir not found
        401/403 — not signed in / not authorized (via require_project_owner)
        500 — unexpected
    """
    # Auth gate FIRST — never read the body for a project we don't own.
    caller_uid = require_project_owner(handler, slug)
    if caller_uid is None:
        return

    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return
    if length <= 0:
        handler._json(400, {"error": "empty request body"}); return
    if length > 4096:
        # Body is just { block_id }; nothing legitimate is over 4 KB.
        handler._json(400, {"error": "request body too large"}); return
    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return

    block_id = (body or {}).get("block_id")
    if not isinstance(block_id, str) or block_id not in BLOCK_REGISTRY:
        handler._json(400, {
            "error":      f"unknown block_id: {block_id!r}",
            "available":  sorted(BLOCK_REGISTRY.keys()),
        })
        return

    spec = BLOCK_REGISTRY[block_id]
    project_dir = _output_dir() / slug
    site_dir = project_dir / "site"
    brief_path = project_dir / "brief.json"

    if not site_dir.exists():
        handler._json(404, {"error": f"project site not found: {slug}"})
        return

    brief = load_brief(brief_path)
    dna_card = load_dna_for_site(brief_path)
    tokens = derive_theme_from_dna(dna_card)

    # Per-slug write lock — without it two concurrent inserts can both
    # snapshot the same pre-state, both write, and the second snapshot
    # bakes in the first edit. Same gate the refine/visual-edit handlers
    # acquired in the 2026-05-15 evening security pass.
    with project_lock(slug) as got_lock:
        if not got_lock:
            handler._json(409, {"error": "another change is already in progress; try again in a moment"})
            return

        # Snapshot BEFORE mutating so the user can undo. Reason string maps
        # onto the dashboard's "Recently changed" feed verbatim.
        snap = snapshot_site(
            slug,
            reason=f"insert-block-{block_id}",
            source=f"POST /api/projects/{slug}/blocks/insert",
        )
        snapshot_id = snap.name if snap else None

        try:
            rendered = render_block(block_id, tokens, brief)
        except Exception as e:
            log.warning("block render failed (%s on %s): %s", block_id, slug, e)
            handler._json(500, {"error": f"block render failed: {e}"})
            return

        try:
            result = insert_block_into_site(
                site_dir=site_dir,
                block_id=block_id,
                component_name=spec.component_name,
                rendered_tsx=rendered,
                snapshot_id=snapshot_id,
            )
        except FileNotFoundError as e:
            handler._json(404, {"error": str(e)})
            return
        except Exception as e:
            log.warning("block insert failed (%s on %s): %s", block_id, slug, e)
            handler._json(500, {"error": f"block insert failed: {e}"})
            return

    handler._json(200, {
        "slug":            slug,
        "billable":        False,
        "dna_id":          tokens.dna_id,
        "dna_label":       tokens.dna_label,
        "applied_at":      datetime.now(timezone.utc).isoformat(),
        **result.to_dict(),
    })
    # Per-user engagement signal (T17). NEVER pass block_id or rendered content.
    _log_engagement(caller_uid, "block_inserted")
