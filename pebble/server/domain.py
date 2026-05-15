"""HTTP endpoints for custom domain wiring.

Routes:

- GET    /api/projects/<slug>/domain   — current state + CNAME instructions
- POST   /api/projects/<slug>/domain   — attach (body: {host}); idempotent
- DELETE /api/projects/<slug>/domain   — detach

Status values returned: ``pending`` (DNS not yet propagated), ``active``
(Cloudflare verified the CNAME), ``error`` (attach failed — see ``error``).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from pebble.domain import (
    DomainError,
    read_domain,
    refresh_domain,
    remove_domain,
    set_domain,
)
from pebble.log import log
from pebble.publish import cloudflare_configured, cloudflare_setup_checklist
from pebble.security import require_project_owner


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
    if length > 4 * 1024:
        handler._json(413, {"error": "request too large"}); return None
    try:
        return json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return None


def _safe_slug(slug: str) -> bool:
    return bool(slug) and "/" not in slug and "\\" not in slug and ".." not in slug


def _project_exists(slug: str) -> bool:
    return (_output_dir() / slug).exists()


def run_get_domain(handler, slug: str) -> None:
    """Return the current domain record (or `null`) plus a refreshed
    status from Cloudflare when configured.

    Auth: gated through require_project_owner. The 2026-05-15 evening
    NLM pass flagged this as cross-user leak (custom domains are
    private business info).
    """
    if require_project_owner(handler, slug) is None:
        return

    if cloudflare_configured():
        try:
            rec = refresh_domain(slug)
            domain = rec.to_dict() if rec else None
        except Exception as e:
            log.warning("domain refresh failed for %s: %s", slug, e)
            domain = read_domain(slug)
    else:
        domain = read_domain(slug)

    handler._json(200, {
        "slug":                  slug,
        "domain":                domain,
        "cloudflare_configured": cloudflare_configured(),
        "cloudflare_setup_md":   None if cloudflare_configured() else cloudflare_setup_checklist(),
    })


def run_set_domain(handler, slug: str) -> None:
    """Attach a custom domain. Body: ``{ host: "example.com" }``."""
    if require_project_owner(handler, slug) is None:
        return

    body = _read_body(handler)
    if body is None: return
    host = (body or {}).get("host", "")

    try:
        rec = set_domain(slug, host)
    except DomainError as e:
        handler._json(400, {"error": str(e)}); return
    except Exception as e:
        log.warning("domain set failed for %s: %s", slug, e)
        handler._json(500, {"error": f"domain set failed: {e}"}); return

    handler._json(200, {
        "slug":                  slug,
        "domain":                rec.to_dict(),
        "cloudflare_configured": cloudflare_configured(),
        "cloudflare_setup_md":   None if cloudflare_configured() else cloudflare_setup_checklist(),
    })


def run_delete_domain(handler, slug: str) -> None:
    """Detach the custom domain. Idempotent — 404 if nothing attached."""
    if require_project_owner(handler, slug) is None:
        return

    prev = remove_domain(slug)
    if not prev:
        handler._json(404, {"error": "no domain attached"}); return

    handler._json(200, {"slug": slug, "removed": prev})
