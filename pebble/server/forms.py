"""HTTP endpoints for the form-inbox flow.

Public (form submitter facing):

- POST /api/forms/<slug>                          — accept a submission

User-scoped (dashboard inbox):

- GET    /api/projects/<slug>/inbox               — list submissions
- GET    /api/projects/<slug>/inbox/<id>          — read one submission
- PATCH  /api/projects/<slug>/inbox/<id>          — mark read/unread
- DELETE /api/projects/<slug>/inbox/<id>          — delete a submission

User-scoped (webhook delivery config):

- GET    /api/projects/<slug>/forms/webhook       — current config (or null)
- POST   /api/projects/<slug>/forms/webhook       — set webhook URL
- DELETE /api/projects/<slug>/forms/webhook       — remove webhook
"""
from __future__ import annotations

import json
import sys
import threading
from pathlib import Path
from typing import Optional

from pebble.forms import (
    HONEYPOT_FIELD,
    MAX_PAYLOAD_BYTES,
    FormError,
    delete_submission,
    get_submission,
    is_honeypot_trip,
    list_submissions,
    save_submission,
    update_submission,
)
from pebble import forms_autoresponder, forms_webhook
from pebble.log import log
from pebble.security import (
    client_ip as _client_ip,
    forms_submit_limiter,
    require_project_owner,
)


def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


def _safe_slug(slug: str) -> bool:
    return bool(slug) and "/" not in slug and "\\" not in slug and ".." not in slug


def _read_body(handler, *, max_bytes: int) -> Optional[dict]:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return None
    if length <= 0:
        return {}
    if length > max_bytes:
        handler._json(413, {"error": "request too large"}); return None
    try:
        return json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return None


# --------- POST /api/forms/<slug> (public) -------------------------------

def run_submit(handler, slug: str) -> None:
    """Accept a form submission for ``slug``. Honeypot trips return 200
    so bots don't learn the trick. Per-IP rate limited (10/min burst,
    decays back at ~1/6s) to keep one bad caller from filling an inbox.
    """
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    project_dir = _output_dir() / slug
    if not project_dir.exists():
        handler._json(404, {"error": "project not found"}); return

    ip = _client_ip(handler)
    if ip and not forms_submit_limiter.allow(f"forms:{ip}"):
        # 429 instead of 200 so callers see backpressure. Generated sites
        # can retry; legitimate humans hit the burst limit only under abuse.
        handler._json(429, {"error": "too many submissions, slow down"}); return

    body = _read_body(handler, max_bytes=MAX_PAYLOAD_BYTES)
    if body is None:
        return

    # Honeypot — silently accept (200 ok, but nothing recorded)
    if is_honeypot_trip(body):
        handler._json(200, {"ok": True}); return

    ua = handler.headers.get("User-Agent")
    ref = handler.headers.get("Referer")
    try:
        rec = save_submission(slug, body, ip=ip, user_agent=ua, referrer=ref)
    except FormError as e:
        handler._json(400, {"error": str(e)}); return
    except Exception as e:
        log.warning("form submit failed for %s: %s", slug, e)
        handler._json(500, {"error": "submit failed"}); return

    # Always echo a stable shape — the form template doesn't care about
    # the inbox id but knowing the submission was accepted is enough.
    handler._json(200, {"ok": True, "id": rec.id})

    # Fire-and-forget side effects (webhook + autoresponder). Runs
    # AFTER we've responded to the form submitter so the visitor's
    # experience never waits on a third-party endpoint. Both deliver
    # functions swallow their own exceptions so the response is safe.
    _fire_async_followups(slug, rec)


def _fire_async_followups(slug: str, rec) -> None:
    """Spawn a daemon thread that runs the configured outbound side
    effects: webhook delivery + visitor autoresponse email.

    A single thread covers both so we don't pay 2x thread-spawn cost
    on every form submission. The payload shape is the public-form
    record — id, received_at, fields, user_agent, referrer; ip_hash
    and other internal fields are deliberately omitted."""
    payload = {
        "id":          rec.id,
        "received_at": rec.received_at,
        "fields":      rec.fields,
        "user_agent":  getattr(rec, "user_agent", None),
        "referrer":    getattr(rec, "referrer", None),
    }
    def _run():
        try:
            forms_webhook.deliver(slug, payload)
        except Exception as e:  # pragma: no cover — deliver() already swallows
            log.exception("webhook thread crashed for %s: %s", slug, e)
        try:
            forms_autoresponder.send_autoresponse(slug, payload)
        except Exception as e:  # pragma: no cover — send_autoresponse already swallows
            log.exception("autoresponder thread crashed for %s: %s", slug, e)
    threading.Thread(target=_run, daemon=True, name=f"forms-followup-{slug}").start()


# --------- GET /api/projects/<slug>/inbox -------------------------------

def run_list_inbox(handler, slug: str) -> None:
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    if require_project_owner(handler, slug) is None:
        return
    items = list_submissions(slug)
    unread = sum(1 for r in items if not r.get("read"))
    handler._json(200, {
        "slug":         slug,
        "submissions":  items,
        "count":        len(items),
        "unread":       unread,
    })


# --------- GET /api/projects/<slug>/inbox/<id> --------------------------

def run_get_inbox_item(handler, slug: str, sub_id: str) -> None:
    if not _safe_slug(slug) or not _safe_slug(sub_id):
        handler._json(400, {"error": "invalid"}); return
    if require_project_owner(handler, slug) is None:
        return
    rec = get_submission(slug, sub_id)
    if not rec:
        handler._json(404, {"error": "submission not found"}); return
    handler._json(200, rec)


# --------- POST /api/projects/<slug>/inbox/<id>/read -------------------

def run_mark_read(handler, slug: str, sub_id: str) -> None:
    """Idempotent mark-as-read. Body: `{ read: bool }` (default true)."""
    if not _safe_slug(slug) or not _safe_slug(sub_id):
        handler._json(400, {"error": "invalid"}); return
    if require_project_owner(handler, slug) is None:
        return
    body = _read_body(handler, max_bytes=1024) or {}
    requested = body.get("read")
    flag = bool(requested) if isinstance(requested, bool) else True
    rec = update_submission(slug, sub_id, {"read": flag})
    if not rec:
        handler._json(404, {"error": "submission not found"}); return
    handler._json(200, rec)


# --------- DELETE /api/projects/<slug>/inbox/<id> ----------------------

def run_delete_inbox_item(handler, slug: str, sub_id: str) -> None:
    if not _safe_slug(slug) or not _safe_slug(sub_id):
        handler._json(400, {"error": "invalid"}); return
    if require_project_owner(handler, slug) is None:
        return
    if not delete_submission(slug, sub_id):
        handler._json(404, {"error": "submission not found"}); return
    handler._json(200, {"slug": slug, "id": sub_id, "deleted": True})


# --------- /api/projects/<slug>/forms/webhook --------------------------

def run_get_webhook_config(handler, slug: str) -> None:
    """GET — return the configured webhook URL, or null."""
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    if require_project_owner(handler, slug) is None:
        return
    config = forms_webhook.get_webhook_config(slug)
    if config is None:
        handler._json(200, {"slug": slug, "configured": False, "webhook": None})
        return
    handler._json(200, {
        "slug":       slug,
        "configured": True,
        "webhook":    config.to_dict(),
    })


def run_set_webhook_config(handler, slug: str) -> None:
    """POST — set the webhook URL. Body: { "url": "https://..." }."""
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    if require_project_owner(handler, slug) is None:
        return
    body = _read_body(handler, max_bytes=4 * 1024) or {}
    url = body.get("url")
    if not isinstance(url, str):
        handler._json(400, {"error": "body must include a 'url' string"}); return
    try:
        config = forms_webhook.set_webhook_config(slug, url)
    except ValueError as e:
        handler._json(400, {"error": str(e)}); return
    handler._json(200, {"slug": slug, "configured": True, "webhook": config.to_dict()})


def run_delete_webhook_config(handler, slug: str) -> None:
    """DELETE — remove the configured webhook."""
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    if require_project_owner(handler, slug) is None:
        return
    removed = forms_webhook.clear_webhook_config(slug)
    handler._json(200, {"slug": slug, "removed": removed, "configured": False})


# --------- /api/projects/<slug>/forms/autoresponder --------------------

def run_get_autoresponder_config(handler, slug: str) -> None:
    """GET — return the current autoresponder config (or defaults)."""
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    if require_project_owner(handler, slug) is None:
        return
    config = forms_autoresponder.get_config(slug)
    handler._json(200, {"slug": slug, "autoresponder": config.to_dict()})


def run_set_autoresponder_config(handler, slug: str) -> None:
    """POST — update the autoresponder. Body fields:
        enabled:     bool (required)
        subject?:    str
        body?:       str
        reply_field?: str (identifier — defaults to "email")
    """
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    if require_project_owner(handler, slug) is None:
        return
    body = _read_body(handler, max_bytes=16 * 1024) or {}
    if "enabled" not in body or not isinstance(body["enabled"], bool):
        handler._json(400, {"error": "'enabled' (bool) is required"}); return
    subject = body.get("subject")
    body_text = body.get("body")
    reply_field = body.get("reply_field")
    # Type-check the optional fields so a JSON 42 doesn't make it into
    # the persisted config.
    for name, val in (("subject", subject), ("body", body_text), ("reply_field", reply_field)):
        if val is not None and not isinstance(val, str):
            handler._json(400, {"error": f"'{name}' must be a string when provided"}); return
    try:
        config = forms_autoresponder.set_config(
            slug,
            enabled=body["enabled"],
            subject=subject,
            body=body_text,
            reply_field=reply_field,
        )
    except ValueError as e:
        handler._json(400, {"error": str(e)}); return
    handler._json(200, {"slug": slug, "autoresponder": config.to_dict()})


def run_delete_autoresponder_config(handler, slug: str) -> None:
    """DELETE — remove the autoresponder config (reverts to defaults/off)."""
    if not _safe_slug(slug):
        handler._json(400, {"error": "invalid slug"}); return
    if require_project_owner(handler, slug) is None:
        return
    removed = forms_autoresponder.clear_config(slug)
    handler._json(200, {"slug": slug, "removed": removed})
