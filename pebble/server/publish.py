"""HTTP endpoints for the publish flow.

Routes:

- POST /api/publish                            — produce/deploy artifact
- GET  /api/projects/<slug>/publish            — last publish state + history
- GET  /dist/<slug>/dist.zip                   — download the most recent zip
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pebble.history import snapshot_site
from pebble.log import log
from pebble.publish import (
    PublishError,
    PublishResult,
    cloudflare_configured,
    cloudflare_setup_checklist,
    package_zip,
    publish_to_cloudflare,
    read_publish_history,
    read_publish_state,
    slug_to_project_name,
    write_publish_state,
)


def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


def _read_body(handler) -> Optional[dict]:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return None
    if length <= 0:
        return {}
    if length > 32 * 1024:
        handler._json(413, {"error": "request too large"}); return None
    try:
        return json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return None


def _safe_slug(slug: str) -> bool:
    """Reject path-traversal-y slugs at the route layer."""
    return bool(slug) and "/" not in slug and "\\" not in slug and ".." not in slug


# --------- POST /api/publish ---------

def run_publish(handler) -> None:
    """Produce a publishable artifact for a project.

    Body::

        { "slug": "...", "dest"?: "auto" | "zip" | "cloudflare" }

    "auto" (default) deploys to Cloudflare when configured, else falls
    back to a ZIP. "cloudflare" forces the live-deploy path (400 if
    creds missing). "zip" always produces ``output/<slug>/dist.zip``.

    Snapshots the site/ tree before publishing so the publish itself
    shows up in version history.
    """
    body = _read_body(handler)
    if body is None: return

    slug = (body or {}).get("slug")
    if not isinstance(slug, str) or not _safe_slug(slug):
        handler._json(400, {"error": "slug is required"}); return

    dest = (body or {}).get("dest") or "auto"
    if dest not in ("auto", "cloudflare", "zip"):
        handler._json(400, {"error": f"unknown dest: {dest}"}); return

    project_dir = _output_dir() / slug
    if not project_dir.exists():
        handler._json(404, {"error": f"project not found: {slug}"}); return

    started = time.time()

    # Snapshot first so publish shows up in version history.
    snap = snapshot_site(slug, reason="publish", source=f"POST /api/publish dest={dest}")
    snapshot_id = snap.name if snap else None

    effective = dest
    if effective == "auto":
        effective = "cloudflare" if cloudflare_configured() else "zip"

    # ---- Cloudflare path ----
    if effective == "cloudflare":
        if not cloudflare_configured():
            handler._json(400, {
                "error": "Cloudflare not configured. Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in .env.",
                "cloudflare_setup_md": cloudflare_setup_checklist(),
            }); return
        try:
            result = publish_to_cloudflare(slug)
        except PublishError as e:
            # Surface the Cloudflare-specific error AND offer the checklist
            # so the user knows what to fix.
            log.warning("cloudflare publish failed for %s: %s", slug, e)
            handler._json(502, {
                "error": str(e),
                "cloudflare_setup_md": cloudflare_setup_checklist(),
            }); return
        except Exception as e:
            log.warning("cloudflare publish errored for %s: %s", slug, e)
            handler._json(500, {"error": f"cloudflare publish failed: {e}"}); return
        result.snapshot_id = snapshot_id
        write_publish_state(slug, result)
        payload = result.to_dict()
        payload["elapsed_seconds"] = round(time.time() - started, 3)
        handler._json(200, payload); return

    # ---- Zip path (always works) ----
    try:
        _zip_path, files_count, bytes_count = package_zip(slug)
    except PublishError as e:
        handler._json(400, {"error": str(e)}); return
    except Exception as e:
        log.warning("publish zip failed for %s: %s", slug, e)
        handler._json(500, {"error": f"zip failed: {e}"}); return

    download_url = f"/dist/{slug}/dist.zip"
    note: Optional[str] = None
    setup_md: Optional[str] = None
    if not cloudflare_configured():
        note = (
            "Cloudflare keys not configured — published as a downloadable ZIP. "
            "Add Cloudflare keys to deploy to a live URL."
        )
        setup_md = cloudflare_setup_checklist()

    result = PublishResult(
        slug=slug,
        kind="zip",
        url=download_url,
        deployed_at=datetime.now(timezone.utc).isoformat(),
        bytes_published=bytes_count,
        files_published=files_count,
        snapshot_id=snapshot_id,
        project_name=slug_to_project_name(slug),
        note=note,
        cloudflare_setup_md=setup_md,
    )
    write_publish_state(slug, result)

    payload = result.to_dict()
    payload["elapsed_seconds"] = round(time.time() - started, 3)
    handler._json(200, payload)


# --------- GET /api/projects/<slug>/publish ---------

def run_get_publish_state(handler, slug: str) -> None:
    """Return the latest publish state + chronological history."""
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    project_dir = _output_dir() / slug
    if not project_dir.exists():
        handler._json(404, {"error": f"project not found: {slug}"}); return
    handler._json(200, {
        "slug":    slug,
        "current": read_publish_state(slug),
        "history": read_publish_history(slug),
    })


# --------- GET /dist/<slug>/dist.zip ---------

def run_serve_dist(handler, slug: str) -> None:
    """Stream the most recent zip artifact back to the client.

    Path-safe: rejects slugs containing slashes, ``..``, or other
    traversal hints before touching disk.
    """
    if not _safe_slug(slug):
        handler.send_response(404); handler.end_headers(); return

    zip_path = _output_dir() / slug / "dist.zip"
    if not zip_path.exists():
        handler.send_response(404); handler.end_headers()
        try: handler.wfile.write(b"Not published yet.")
        except Exception: pass
        return

    data = zip_path.read_bytes()
    handler.send_response(200)
    handler.send_header("Content-Type", "application/zip")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header(
        "Content-Disposition",
        f'attachment; filename="{slug}.zip"',
    )
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(data)
