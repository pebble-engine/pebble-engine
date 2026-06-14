"""Launchpad v1 — submit published sites + public showcase grid (Batch D).

  GET  /api/launchpad/showcase              → approved gallery (public)
  GET  /api/launchpad/screenshot/<slug>     → hero PNG when approved (public)
  GET  /api/projects/<slug>/launchpad       → owner submission state
  POST /api/projects/<slug>/launchpad       → submit / update showcase row
  DELETE /api/projects/<slug>/launchpad     → withdraw from gallery
"""
from __future__ import annotations

import json
from pathlib import Path

from pebble import launchpad, events
from pebble.log import log
from pebble.security import (
    client_ip,
    plan_limiter,
    require_project_owner,
    validate_slug,
)
from pebble.server.publish_instant import is_published, read_instant_state


def _output_dir() -> Path:
    from pebble.server.build import _engine
    return _engine().OUTPUT_DIR


def _read_body(handler) -> dict | None:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"})
        return None
    if length <= 0 or length > 64_000:
        handler._json(400, {"error": "missing or oversized body"})
        return None
    try:
        return json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid JSON body"})
        return None


def _brief_for_slug(slug: str) -> dict:
    brief_path = _output_dir() / slug / "brief.json"
    if not brief_path.exists():
        return {}
    try:
        data = json.loads(brief_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _published_url(slug: str) -> str | None:
    state = read_instant_state(slug)
    if not state:
        return None
    sub = state.get("subdomain", "")
    if not sub:
        return None
    try:
        from pebble.server.publish_instant import _public_url, is_valid_subdomain
        if is_valid_subdomain(sub):
            return _public_url(sub)
    except Exception:
        pass
    return None


def _public_entry(row: dict) -> dict:
    slug = row.get("slug", "")
    has_shot = (_output_dir() / slug / "screenshots" / "01-hero.png").is_file()
    return {
        "slug":          slug,
        "business_name": row.get("business_name") or slug,
        "industry":      row.get("industry"),
        "tagline":       row.get("tagline"),
        "url":           row.get("url"),
        "submitted_at":  row.get("submitted_at"),
        "preview_url":   f"/preview/{slug}/",
        "screenshot_url": f"/api/launchpad/screenshot/{slug}" if has_shot else None,
        "meta":          row.get("meta"),
    }


def _live_approved_rows(limit: int = 24) -> list[dict]:
    rows = launchpad.list_approved(limit=limit)
    live = [r for r in rows if is_published(r.get("slug", ""))]
    return live


def run_list_showcase(handler) -> None:
    """GET /api/launchpad/showcase — public gallery."""
    ip = client_ip(handler)
    if not plan_limiter.allow(ip or ""):
        handler._json(429, {"error": "slow down"})
        return

    rows = [_public_entry(r) for r in _live_approved_rows(limit=24)]
    handler._json(200, {"entries": rows, "count": len(rows)})


def run_get_launchpad_screenshot(handler, slug: str) -> None:
    """GET /api/launchpad/screenshot/<slug> — PNG only when showcase-approved."""
    if not validate_slug(handler, slug):
        return

    row = launchpad.get_by_slug(slug)
    if not row or row.get("status") != launchpad.STATUS_APPROVED:
        handler._json(404, {"error": "not in showcase"})
        return
    if not is_published(slug):
        handler._json(404, {"error": "site not published"})
        return

    shot_path = _output_dir() / slug / "screenshots" / "01-hero.png"
    if not shot_path.is_file():
        handler._json(404, {"error": "screenshot not available"})
        return

    try:
        data = shot_path.read_bytes()
    except Exception as e:
        log.warning("launchpad screenshot read failed slug=%s: %s", slug, e)
        handler._json(500, {"error": "screenshot read failed"})
        return

    handler.send_response(200)
    handler.send_header("Content-Type", "image/png")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "public, max-age=600")
    handler.end_headers()
    handler.wfile.write(data)


def run_get_project_launchpad(handler, slug: str) -> None:
    """GET /api/projects/<slug>/launchpad — owner submission state."""
    if not validate_slug(handler, slug):
        return
    uid = require_project_owner(handler, slug)
    if uid is None:
        return

    row = launchpad.get_by_slug(slug)
    submitted = bool(row and row.get("status") == launchpad.STATUS_APPROVED)
    handler._json(200, {
        "slug":       slug,
        "published":  is_published(slug),
        "submitted":  submitted,
        "entry":      _public_entry(row) if submitted else None,
        "url":        _published_url(slug),
    })


def run_submit_launchpad(handler, slug: str) -> None:
    """POST /api/projects/<slug>/launchpad — submit to public gallery."""
    if not validate_slug(handler, slug):
        return
    uid = require_project_owner(handler, slug)
    if uid is None:
        return

    if not is_published(slug):
        handler._json(400, {"error": "publish your site first, then submit to Launchpad"})
        return

    body = _read_body(handler) or {}
    tagline = body.get("tagline") if isinstance(body.get("tagline"), str) else None

    brief = _brief_for_slug(slug)
    business_name = (
        brief.get("business_name")
        or brief.get("business_type")
        or slug
    )
    industry = brief.get("business_type") or brief.get("industry")
    url = _published_url(slug)

    row = launchpad.submit(
        uid,
        slug,
        business_name=str(business_name),
        industry=str(industry) if industry else None,
        tagline=tagline,
        url=url,
        meta={"design_dna": brief.get("_design_dna_id") or brief.get("_design_dna")},
    )
    if not row:
        handler._json(503, {"error": "showcase unavailable — try again shortly"})
        return

    try:
        events.record(
            user_id=uid,
            kind=events.KIND_TEMPLATE_SUBMITTED,
            title=f"{business_name} joined the Launchpad",
            body="A builder shared their site in the public gallery.",
            visibility=events.VISIBILITY_PUBLIC,
            meta={"slug": slug, "url": url},
        )
    except Exception as e:
        log.warning("launchpad submit event failed: %s", e)

    handler._json(200, {
        "ok":    True,
        "entry": _public_entry(row),
    })


def run_withdraw_launchpad(handler, slug: str) -> None:
    """DELETE /api/projects/<slug>/launchpad — remove from gallery."""
    if not validate_slug(handler, slug):
        return
    uid = require_project_owner(handler, slug)
    if uid is None:
        return

    removed = launchpad.withdraw(uid, slug)
    handler._json(200, {"ok": True, "removed": removed})


__all__ = [
    "run_list_showcase",
    "run_get_launchpad_screenshot",
    "run_get_project_launchpad",
    "run_submit_launchpad",
    "run_withdraw_launchpad",
]
