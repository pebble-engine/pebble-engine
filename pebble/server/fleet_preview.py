"""Glue between the engine and the Fly Machines preview fleet.

- kick_preview(slug): ensure a machine + push the site's source (incl. the
  visual-edit bridge as .pebble-bridge.js so the receiver injects it). Runs in
  a daemon thread; called after build + refine when PEBBLE_PREVIEW_BACKEND=fly-fleet.
- run_get_preview_url(handler, slug): owner-gated endpoint the workspace polls
  to learn the machine URL + readiness.
"""
from __future__ import annotations

import os
import sys
import threading
from pathlib import Path
from typing import Any

from pebble.log import log
from pebble.security import require_project_owner


def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


def fleet_enabled() -> bool:
    if os.environ.get("PEBBLE_PREVIEW_BACKEND", "").strip().lower() != "fly-fleet":
        return False
    from pebble import fly_fleet
    return fly_fleet.fleet_configured()


def collect_source_with_bridge(slug: str) -> list[dict[str, Any]]:
    """Source files for the machine: the site (sans node_modules) + the
    visual-edit bridge written to .pebble-bridge.js (the receiver injects it)."""
    from pebble.vercel_deploy import collect_files  # same skip rules (no node_modules/.next)
    files = collect_files(_output_dir() / slug / "site")
    try:
        from pebble.server.visual_edit import PEBBLE_VISUAL_EDIT_BRIDGE
        files.append({"file": ".pebble-bridge.js", "data": PEBBLE_VISUAL_EDIT_BRIDGE})
    except Exception:
        pass
    return files


def kick_preview(slug: str) -> None:
    """Fire-and-forget: ensure a machine and sync the site to it. No-op unless
    the fleet backend is enabled + configured."""
    if not fleet_enabled():
        return

    def _bg() -> None:
        try:
            from pebble import fly_fleet
            url = fly_fleet.ensure_machine(slug)
            if not url:
                log.warning("[fleet] no machine for %s (cap hit?)", slug)
                return
            files = collect_source_with_bridge(slug)
            # receiver wants {path,data}; collect_files uses {file,data}.
            payload = [{"path": f["file"], "data": f["data"]} for f in files]
            fly_fleet.sync_files(slug, payload)
            log.info("[fleet] synced %d files to %s (%s)", len(payload), slug, url)
        except Exception as e:
            log.warning("[fleet] kick_preview failed for %s: %s", slug, e)

    threading.Thread(target=_bg, daemon=True, name=f"fleet-{slug}").start()


def run_get_preview_url(handler, slug: str) -> None:
    """GET /api/projects/<slug>/preview-url — owner-gated. Returns the machine
    URL + readiness so the workspace can iframe it once live."""
    uid = require_project_owner(handler, slug)
    if not uid:
        return
    if not fleet_enabled():
        handler._json(200, {"enabled": False})
        return
    from pebble import fly_fleet
    reg = fly_fleet._load_registry()
    entry = reg.get(slug)
    if not entry:
        handler._json(200, {"enabled": True, "ready": False, "url": None})
        return
    ready = False
    try:
        import httpx
        r = httpx.get(f"{entry['url']}/__pebble/healthz", timeout=5.0)
        ready = r.status_code == 200 and (r.json() or {}).get("ready", False)
    except Exception:
        ready = False
    handler._json(200, {"enabled": True, "ready": ready, "url": entry.get("url")})


__all__ = ["fleet_enabled", "collect_source_with_bridge", "kick_preview", "run_get_preview_url"]
