"""GET + POST + DELETE /api/projects/<slug>/integrations[/<id>]

GET  /api/projects/<slug>/integrations
    Returns all integration configs (id → {enabled, config}).

POST /api/projects/<slug>/integrations
    Body: { "id": str, "enabled": bool, "config": {...} }
    Saves or updates an integration. Owner-gated.

DELETE /api/projects/<slug>/integrations/<id>
    Removes an integration. Owner-gated.
"""
from __future__ import annotations

import json

from pebble.integrations import (
    INTEGRATION_IDS,
    delete_integration,
    get_integrations,
    save_integration,
)
from pebble.security import require_project_owner


def run_get_integrations(handler, slug: str) -> None:
    """GET /api/projects/<slug>/integrations — owner-gated.

    Returns ``{id: {enabled, config}}`` for every integration on the
    project. Config values can include phone numbers (WhatsApp),
    addresses + emails (booking links), or arbitrary HTML/JS snippets
    (custom-code) — all things a competitor shouldn't be able to peek
    at by guessing slugs. Found during the 2026-05-22 overnight bug
    hunt: the POST + DELETE handlers below were owner-gated but GET
    was wide open.
    """
    if require_project_owner(handler, slug) is None:
        return  # require_project_owner already wrote 400/401/403/404
    data = get_integrations(slug)
    handler._json(200, data)


def run_post_integration(handler, slug: str) -> None:
    """POST /api/projects/<slug>/integrations"""
    owner = require_project_owner(handler, slug)
    if owner is None:
        return  # require_project_owner already sent 401/403

    # Read body
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length"}); return
    if length <= 0:
        handler._json(400, {"error": "empty body"}); return

    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid JSON"}); return

    if not isinstance(body, dict):
        handler._json(400, {"error": "body must be a JSON object"}); return

    integration_id = str(body.get("id") or "")
    if integration_id not in INTEGRATION_IDS:
        handler._json(400, {
            "error": f"unknown integration {integration_id!r}",
            "valid": sorted(INTEGRATION_IDS),
        }); return

    enabled = bool(body.get("enabled", True))
    config = body.get("config", {})
    if not isinstance(config, dict):
        handler._json(400, {"error": "config must be an object"}); return

    try:
        saved = save_integration(slug, integration_id, enabled, config)
    except Exception as exc:
        handler._json(500, {"error": str(exc)}); return

    handler._json(200, {"id": integration_id, **saved})


def run_delete_integration(handler, slug: str, integration_id: str) -> None:
    """DELETE /api/projects/<slug>/integrations/<id>"""
    owner = require_project_owner(handler, slug)
    if owner is None:
        return

    if integration_id not in INTEGRATION_IDS:
        handler._json(400, {"error": f"unknown integration {integration_id!r}"}); return

    existed = delete_integration(slug, integration_id)
    handler._json(200, {"deleted": existed, "id": integration_id})
