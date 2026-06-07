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
from pebble.security import project_lock, require_project_owner, safe_user_id, user_publish_lock
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

FREE_PUBLISH_LIMIT = 2


def _subscription_active(user_id: str) -> bool:
    """Return True when the user has an active Stripe subscription."""
    safe_uid = safe_user_id(user_id)
    if not safe_uid:
        return False
    sentinel = _output_dir() / ".users" / safe_uid / "subscription.json"
    if not sentinel.exists():
        return False
    try:
        data = json.loads(sentinel.read_text(encoding="utf-8"))
        return data.get("status") == "active"
    except Exception:
        return False


def _count_published_sites(user_id: str, exclude_slug: str) -> int:
    """Count how many OTHER sites this user has published (or is publishing).

    Counts both completed publish.json and in-flight .publish_intent sentinels
    so that concurrent publish requests are reflected in the limit check even
    before the slow upload completes.
    """
    out = _output_dir()
    count = 0
    for brief_path in out.glob("*/brief.json"):
        slug = brief_path.parent.name
        if slug == exclude_slug:
            continue
        try:
            brief = json.loads(brief_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if brief.get("_user_id") != user_id:
            continue
        proj = brief_path.parent
        if (proj / "publish.json").exists() or (proj / ".publish_intent").exists():
            count += 1
    return count


def _write_publish_intent(slug: str) -> None:
    """Write a sentinel so concurrent limit checks see this publish as claimed."""
    try:
        (_output_dir() / slug / ".publish_intent").touch()
    except Exception:
        pass


def _clear_publish_intent(slug: str) -> None:
    """Remove the intent sentinel (called on publish success or failure)."""
    try:
        (_output_dir() / slug / ".publish_intent").unlink(missing_ok=True)
    except Exception:
        pass


def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


def _placeholder_check(slug: str) -> dict:
    """Run the publish-time transparency guard for ``slug``. Fail-open:
    any error returns a ready=True sentinel so we never block or noise up
    a publish because of our own scan failure."""
    try:
        from pebble.publish_check import publish_readiness
        return publish_readiness(_output_dir() / slug / "site")
    except Exception as e:  # pragma: no cover — defensive
        log.warning("placeholder check failed for %s: %s", slug, e)
        return {"ready": True, "count": 0, "items": [], "message": ""}


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

    # Auth gate — publish is the most consequential mutation (writes to a
    # public deploy target). The 2026-05-15 evening NLM pass flagged that
    # any signed-in user could publish another user's project by slug.
    uid = require_project_owner(handler, slug)
    if uid is None:
        return

    # MFA step-up: publish is the most consequential mutation (live deploy).
    # A stolen AAL1 token must not push a site live within its TTL. No-op
    # for callers without enrolled MFA / cookie / anon / unconfigured auth.
    from pebble.security import enforce_step_up
    if not enforce_step_up(handler):
        return  # 401 already written

    # Free-plan site limit. Active subscribers are unlimited. Free users
    # cap at FREE_PUBLISH_LIMIT published sites.
    #
    # A per-user lock + intent sentinel prevents the TOCTOU race where two
    # concurrent publishes (different slugs, same user) both pass the count
    # check before either writes publish.json. The lock window is tiny:
    # check + touch .publish_intent. The slow upload happens outside the lock.
    if not _subscription_active(uid):
        with user_publish_lock(uid) as acquired:
            if not acquired:
                handler._json(503, {"error": "another publish is in progress; try again shortly"})
                return
            already = _count_published_sites(uid, exclude_slug=slug)
            if already >= FREE_PUBLISH_LIMIT:
                handler._json(402, {
                    "error": (
                        f"Free plan allows {FREE_PUBLISH_LIMIT} published sites. "
                        "Upgrade to Starter or Pro to publish unlimited sites."
                    ),
                    "upgrade_url": "/pricing",
                    "published_count": already,
                    "limit": FREE_PUBLISH_LIMIT,
                })
                return
            # Claim the slot before releasing the lock so concurrent requests
            # for OTHER slugs see this one as in-flight.
            _write_publish_intent(slug)

    project_dir = _output_dir() / slug
    if not project_dir.exists():
        _clear_publish_intent(slug)
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
            _clear_publish_intent(slug)
            handler._json(400, {
                "error": "Cloudflare not configured. Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in .env.",
                "cloudflare_setup_md": cloudflare_setup_checklist(),
            }); return
        try:
            result = publish_to_cloudflare(slug)
        except PublishError as e:
            _clear_publish_intent(slug)
            log.warning("cloudflare publish failed for %s: %s", slug, e)
            handler._json(502, {
                "error": str(e),
                "cloudflare_setup_md": cloudflare_setup_checklist(),
            }); return
        except Exception as e:
            _clear_publish_intent(slug)
            log.warning("cloudflare publish errored for %s: %s", slug, e)
            handler._json(500, {"error": f"cloudflare publish failed: {e}"}); return
        _clear_publish_intent(slug)
        result.snapshot_id = snapshot_id
        write_publish_state(slug, result)
        payload = result.to_dict()
        payload["elapsed_seconds"] = round(time.time() - started, 3)
        payload["placeholder_check"] = _placeholder_check(slug)
        handler._json(200, payload); return

    # ---- Zip path (always works) ----
    try:
        _zip_path, files_count, bytes_count = package_zip(slug)
    except PublishError as e:
        _clear_publish_intent(slug)
        handler._json(400, {"error": str(e)}); return
    except Exception as e:
        _clear_publish_intent(slug)
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
    _clear_publish_intent(slug)
    write_publish_state(slug, result)

    payload = result.to_dict()
    payload["elapsed_seconds"] = round(time.time() - started, 3)
    payload["placeholder_check"] = _placeholder_check(slug)
    handler._json(200, payload)


# --------- GET /api/projects/<slug>/publish-check ---------

def run_publish_check(handler, slug: str) -> None:
    """Read-only pre-publish transparency check. Returns publish_readiness
    so the UI can warn 'you still have N placeholders' BEFORE the owner
    goes live. Owner-gated (same as publish). Purely additive — never
    mutates or blocks."""
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    if require_project_owner(handler, slug) is None:
        return  # 401/403 already written
    project_dir = _output_dir() / slug
    if not project_dir.exists():
        handler._json(404, {"error": f"project not found: {slug}"}); return
    handler._json(200, _placeholder_check(slug))


# --------- GET /api/projects/<slug>/publish ---------

def run_get_publish_state(handler, slug: str) -> None:
    """Return the latest publish state + chronological history.

    Auth: gated through require_project_owner — the publish history
    leaks deploy URLs and timestamps that aren't another user's
    business.
    """
    if require_project_owner(handler, slug) is None:
        return
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
