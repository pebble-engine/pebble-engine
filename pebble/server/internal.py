"""Internal engine endpoints — server-to-server only, not browser-facing.

All routes here require ``X-Internal-Key: <PEBBLE_INTERNAL_KEY>`` so they
can't be triggered by arbitrary web requests. The ``/api/internal/*``
prefix is also excluded from CORS in router_options() (see router.py) as
defense-in-depth.

Routes:
  GET /api/internal/process-email-drip  — fire due drip emails, return summary
"""
from __future__ import annotations

import os

from pebble.log import log


def _internal_key() -> str:
    return os.environ.get("PEBBLE_INTERNAL_KEY", "").strip()


def _check_key(handler) -> bool:
    """Return True if the request carries the correct X-Internal-Key header.
    Writes a 401 and returns False otherwise."""
    expected = _internal_key()
    if not expected:
        handler._json(503, {"error": "PEBBLE_INTERNAL_KEY not configured"})
        return False
    provided = (handler.headers.get("X-Internal-Key") or "").strip()
    if not provided or provided != expected:
        handler._json(401, {"error": "unauthorized"})
        return False
    return True


def run_process_email_drip(handler) -> None:
    """GET /api/internal/process-email-drip

    Scan all output/.users/<uid>/email_drip.json files and send any emails
    whose send_at is past and sent_at is null. Returns:
      { "sent": int, "skipped": int, "errors": [...] }

    Gated by X-Internal-Key header matching PEBBLE_INTERNAL_KEY env var.
    Called hourly by a Windows scheduled task:
      schtasks /Run /TN "Pebble Email Drip"
    or by a curl:
      curl -H "X-Internal-Key: <key>" http://localhost:8000/api/internal/process-email-drip
    """
    if not _check_key(handler):
        return
    try:
        from pebble.email_drip import process_due
        result = process_due()
        log.info(
            "drip: processed — sent=%d skipped=%d errors=%d",
            result["sent"], result["skipped"], len(result["errors"]),
        )
        handler._json(200, result)
    except Exception as exc:
        log.error("drip: process_due raised: %s", exc)
        handler._json(500, {"error": "drip processing failed"})
