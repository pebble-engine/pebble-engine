"""GET /api/projects/<slug>/preview-status — Vercel preview deploy state.

Owner-gated. The workspace edit phase polls this while the iframe shows the
Vercel warmup splash so users see deploy progress/errors instead of an
infinite spinner.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from pebble.security import require_project_owner


def _output_dir() -> Path:
    import pebble_engine as pe
    return pe.OUTPUT_DIR


def build_preview_status(slug: str, *, kick: bool = True) -> dict[str, Any]:
    """Pure status snapshot for *slug* (no HTTP)."""
    preview_backend = os.environ.get("PEBBLE_PREVIEW_BACKEND", "local").strip().lower()
    out = _output_dir() / slug
    site_dir = out / "site"
    has_source = (site_dir / "package.json").exists()
    site_files = 0
    if site_dir.exists():
        site_files = sum(1 for p in site_dir.rglob("*") if p.is_file())

    state: dict[str, Any] = {}
    state_path = out / ".vercel-preview.json"
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8")) or {}
        except Exception:
            state = {}

    vercel_url = str(state.get("url") or "").rstrip("/") or None
    error = state.get("error")
    deployed_at = state.get("deployed_at")
    deployment_id = state.get("deployment_id")

    deploying = False
    status = "idle"
    if preview_backend == "vercel":
        from pebble.server.preview_vercel_kick import deploy_status as _deploy_status
        status = _deploy_status(slug)
        deploying = status == "deploying"
        if kick and not vercel_url and has_source and status in ("idle", "failed"):
            status = _kick(slug, proxy_failed=False)
            deploying = status == "deploying"
        if not error:
            from pebble.server.preview_vercel_kick import last_deploy_error
            error = last_deploy_error(slug)

    ready = bool(vercel_url) and not error
    return {
        "slug": slug,
        "backend": preview_backend,
        "ready": ready,
        "deploying": deploying,
        "status": status if preview_backend == "vercel" else ("ready" if has_source else "idle"),
        "preview_url": f"/preview/{slug}/",
        "vercel_url": vercel_url,
        "error": error,
        "deployed_at": deployed_at,
        "deployment_id": deployment_id,
        "has_source": has_source,
        "site_files": site_files,
    }


def _kick(slug: str, *, proxy_failed: bool) -> str:
    from pebble.server.preview_vercel_kick import kick_if_needed
    return kick_if_needed(slug, proxy_failed=proxy_failed)


def run_get_preview_status(handler, slug: str) -> None:
    uid = require_project_owner(handler, slug)
    if not uid:
        return
    handler._json(200, build_preview_status(slug, kick=True))


__all__ = ["build_preview_status", "run_get_preview_status"]
