"""GET /api/account/activity — return the calling user's audit_log rows.

Uses the USER's JWT (not the service role) so Supabase RLS naturally
scopes to their rows. The audit_log table has:

    create policy "users can view own audit log"
      on public.audit_log for select
      using (auth.uid() = user_id);

so any SELECT made with the user's session token returns only their rows.

The route is registered in pebble/server/router.py as a GET.
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs
from typing import Any

from pebble.log import log
from pebble.security import require_user

_DEFAULT_LIMIT = 50
_MAX_LIMIT = 100


def _fetch_user_audit_log(user_jwt: str, user_id: str, limit: int) -> list[dict[str, Any]]:
    """Query public.audit_log via Supabase REST as the authenticated user.
    RLS restricts the result to rows where user_id = auth.uid().

    Returns a list of dicts ordered most-recent-first."""
    supabase_url = (
        os.environ.get("PEBBLE_SUPABASE_URL")
        or os.environ.get("SUPABASE_URL")
        or ""
    ).rstrip("/")
    anon_key = (
        os.environ.get("PEBBLE_SUPABASE_ANON_KEY")
        or os.environ.get("SUPABASE_ANON_KEY")
        or ""
    )
    url = (
        f"{supabase_url}/rest/v1/audit_log"
        f"?select=id,event_type,ip,user_agent,metadata,created_at"
        f"&order=created_at.desc"
        f"&limit={int(limit)}"
    )
    req = urllib.request.Request(url, headers={
        "apikey":        anon_key,
        "Authorization": f"Bearer {user_jwt}",
        "Accept":        "application/json",
    })
    with urllib.request.urlopen(req, timeout=8) as resp:
        return json.loads(resp.read())


def _extract_bearer(handler) -> str:
    """Pull the raw JWT from the Authorization header."""
    header = handler.headers.get("Authorization", "") or ""
    if header.startswith("Bearer "):
        return header[len("Bearer "):].strip()
    # Case-insensitive fallback (RFC 6750)
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return ""


def run_get_activity(handler) -> None:
    """GET /api/account/activity[?limit=N] — last N audit_log rows (RLS-scoped)."""
    user = require_user(handler)
    if not user:
        return  # require_user already responded 401

    # Parse limit from query string. Clamp to [1, 100].
    try:
        qs = parse_qs(urlparse(handler.path).query)
        limit_raw = qs.get("limit", [str(_DEFAULT_LIMIT)])[0]
        limit = int(limit_raw)
        limit = max(1, min(_MAX_LIMIT, limit))
    except Exception:
        limit = _DEFAULT_LIMIT

    user_jwt = _extract_bearer(handler)
    if not user_jwt:
        # require_user passed, but bearer was somehow missing. Shouldn't happen.
        handler._json(401, {"error": "missing bearer token"})
        return

    try:
        rows = _fetch_user_audit_log(user_jwt, user["id"], limit)
    except Exception as e:
        log.warning("[audit_log_api] fetch failed for %s: %s", user["id"], e)
        handler._json(500, {"error": "Couldn't load your activity log. Please try again."})
        return

    handler._json(200, {"events": rows, "count": len(rows)})
