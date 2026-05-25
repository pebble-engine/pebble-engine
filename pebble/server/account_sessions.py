"""Active-sessions endpoints — list + per-session revoke.

Phase D.2 (2026-05-24). Three endpoints:

  GET    /api/account/sessions               — list the calling user's
                                                active sessions
  DELETE /api/account/sessions/<session_id>  — revoke one session
  (POST  /api/account/global-signout         — handled by
                                                account_signout.py)

Why not call Supabase's admin API directly?

  Supabase Auth's admin REST API does NOT expose a sessions list — the
  /admin/users/{user_id} routes only cover create/read/update/delete on
  the user record itself + factors + passkeys (verified against the
  GoTrue master branch as of 2026-05-24).

  Sessions live in the auth.sessions Postgres table though, and we
  have the service-role key. We expose two SECURITY DEFINER functions
  in the public schema (migration 008_user_sessions_view.sql) so we
  can query and delete by user_id WITHOUT opening auth.* to PostgREST
  at large:

    public.list_user_sessions(target_user uuid)   → table
    public.revoke_user_session(target_user uuid, target_session uuid) → bool

  Both functions are granted to service_role only. The engine passes
  the calling user's id explicitly — the DB function enforces the
  ownership check in its DELETE WHERE clause as defense-in-depth.

Sanitization on read:
  - refresh_token_hmac_key / refresh_token_counter are NEVER returned
  - user_agent → parsed to a short human-readable summary
    ('Safari on macOS', 'Chrome on Windows', etc.)
  - ip → returned as a string (already a string from host() in the SQL
    function), available for the user to spot weird locations
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

from pebble.log import log
from pebble.security import RateLimiter, require_user


# 30 list-requests/min per user. A user reloading their settings page
# wouldn't approach this; a scraper hammering this endpoint to detect
# new sessions WOULD. Tight enough to make scraping noisy in audit logs.
_sessions_limiter = RateLimiter(rate=30 / 60.0, burst=30)

# Looser bucket for revoke ops since each one is intentional. 10/min
# covers "user clicks revoke on 7 sessions then global sign-out" without
# tripping limits.
_revoke_limiter = RateLimiter(rate=10 / 60.0, burst=10)


def _reset_sessions_limiter_for_tests() -> None:
    """Test hook — clear both buckets between tests so rate-limit
    assertions are hermetic. Production callers never reach this."""
    global _sessions_limiter, _revoke_limiter
    _sessions_limiter = RateLimiter(rate=30 / 60.0, burst=30)
    _revoke_limiter = RateLimiter(rate=10 / 60.0, burst=10)


# Permissive but bounded UUID shape. auth.sessions ids are PG UUIDs
# (8-4-4-4-12 hex with optional braces) — the strict regex rejects
# path-traversal / SQL-injection shapes early.
_SESSION_ID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def _env_url() -> str:
    return (os.environ.get("PEBBLE_SUPABASE_URL")
            or os.environ.get("SUPABASE_URL")
            or "").strip().rstrip("/")


def _env_service_role() -> str:
    return (os.environ.get("PEBBLE_SUPABASE_SERVICE_ROLE_KEY")
            or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            or "").strip()


def _fetch_user_sessions(user_id: str) -> list[dict[str, Any]]:
    """Call the SECURITY DEFINER `list_user_sessions` function via PostgREST RPC.
    Returns a list of raw session rows. Raises on network/HTTP errors so the
    caller can return 502."""
    url = f"{_env_url()}/rest/v1/rpc/list_user_sessions"
    body = json.dumps({"target_user": user_id}).encode("utf-8")
    key = _env_service_role()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "apikey":        key,
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
        "User-Agent":    "PebbleEngine/1.0 (+https://pebbleapp.ai)",
    })
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data if isinstance(data, list) else []


def _supabase_revoke_session(user_id: str, session_id: str) -> bool:
    """Call public.revoke_user_session(target_user, target_session). Returns
    True iff a row was deleted (i.e. the session existed AND was owned by
    user_id). Raises only on real network/HTTP errors — a False return is a
    legitimate 'not found / not yours' response.

    Note the DB function double-checks ownership (deletes WHERE user_id =
    target_user) so even if a service-role token leaked, an attacker can't
    use it to torch sessions for users they don't already know the id of.
    """
    url = f"{_env_url()}/rest/v1/rpc/revoke_user_session"
    body = json.dumps({
        "target_user":    user_id,
        "target_session": session_id,
    }).encode("utf-8")
    key = _env_service_role()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "apikey":        key,
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
        "User-Agent":    "PebbleEngine/1.0 (+https://pebbleapp.ai)",
    })
    with urllib.request.urlopen(req, timeout=8) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    # RPC returns the bool directly.
    return bool(result)


# ── User-Agent parsing ──────────────────────────────────────────────────────
#
# We deliberately use a tiny hand-rolled parser instead of a UA library.
# UA parsing is a swamp of edge cases, and the result is shown to the user
# for ID purposes only — perfect accuracy is not the bar. We just need
# "Safari on macOS" vs "Chrome on iPhone" vs "Curl on Linux" so they can
# spot a session they didn't make.

def _summarize_user_agent(ua: str) -> str:
    """Return a short 'Browser on OS' label, falling back to a snippet."""
    if not ua:
        return "Unknown device"
    ua_low = ua.lower()

    # Browser detection — order matters. Edge contains "Chrome"; OPR is
    # Opera-on-Chromium; bots are matched first so we don't claim a
    # health check is "Chrome on Linux".
    browser: Optional[str] = None
    if "curl" in ua_low:
        browser = "Curl"
    elif "wget" in ua_low:
        browser = "Wget"
    elif "python-urllib" in ua_low or "python-requests" in ua_low:
        browser = "Python script"
    elif "postmanruntime" in ua_low:
        browser = "Postman"
    elif "edg/" in ua_low or "edge/" in ua_low:
        browser = "Edge"
    elif "opr/" in ua_low or "opera" in ua_low:
        browser = "Opera"
    elif "firefox" in ua_low:
        browser = "Firefox"
    elif "chrome" in ua_low and "safari" in ua_low and "mobile" not in ua_low:
        browser = "Chrome"
    elif "chrome" in ua_low:
        browser = "Chrome"
    elif "safari" in ua_low and "mobile" in ua_low:
        browser = "Safari"
    elif "safari" in ua_low:
        browser = "Safari"

    # OS detection
    os_name: Optional[str] = None
    if "iphone" in ua_low or "ipod" in ua_low:
        os_name = "iPhone"
    elif "ipad" in ua_low:
        os_name = "iPad"
    elif "android" in ua_low:
        os_name = "Android"
    elif "windows nt" in ua_low or "windows" in ua_low:
        os_name = "Windows"
    elif "mac os x" in ua_low or "macintosh" in ua_low:
        os_name = "macOS"
    elif "cros" in ua_low or "chromebook" in ua_low:
        os_name = "ChromeOS"
    elif "linux" in ua_low:
        os_name = "Linux"

    if browser and os_name:
        return f"{browser} on {os_name}"
    if browser:
        return browser
    if os_name:
        return os_name
    # Fallback: first 40 chars of the raw UA so the user has SOMETHING.
    return ua[:40] + ("…" if len(ua) > 40 else "")


def _is_current_session(
    session_ua: Optional[str], session_ip: Optional[str],
    request_ua: Optional[str], request_ip: Optional[str],
) -> bool:
    """Best-effort match — UA + IP both equal. NOT perfect (two devices
    behind the same NAT with the same UA would tie), but right side of
    'helpful' vs 'misleading'. The frontend uses this only for a 'This
    device' label; it's never load-bearing for security."""
    if not session_ua or not session_ip or not request_ua or not request_ip:
        return False
    return session_ua.strip() == request_ua.strip() and session_ip.strip() == request_ip.strip()


def _sanitize_session(raw: dict[str, Any], request_ua: str, request_ip: str) -> dict[str, Any]:
    """Strip dangerous columns, attach computed fields, normalize types."""
    return {
        "id":                 raw.get("id"),
        "created_at":         raw.get("created_at"),
        "updated_at":         raw.get("updated_at"),
        "refreshed_at":       raw.get("refreshed_at"),
        "not_after":          raw.get("not_after"),
        "user_agent":         raw.get("user_agent") or "",
        "user_agent_summary": _summarize_user_agent(raw.get("user_agent") or ""),
        "ip":                 raw.get("ip") or "",
        "aal":                raw.get("aal"),
        "is_current":         _is_current_session(
            raw.get("user_agent"), raw.get("ip"),
            request_ua, request_ip,
        ),
    }


def _request_ip(handler) -> str:
    """Best-effort client IP — same logic as audit_log helper. X-Forwarded-For
    first (Railway proxy), else direct connection."""
    headers = getattr(handler, "headers", {}) or {}
    xff = (headers.get("X-Forwarded-For", "") or "").strip()
    if xff:
        return xff.split(",")[0].strip()
    ca = getattr(handler, "client_address", ("", 0))
    return (ca[0] if ca else "") or ""


# ── Endpoints ───────────────────────────────────────────────────────────────

def run_list_sessions(handler) -> None:
    """GET /api/account/sessions — return the user's active session list."""
    user = require_user(handler)
    if not user:
        return  # 401 already written

    if not _sessions_limiter.allow(user["id"]):
        handler._json(429, {"error": "Too many requests. Please wait and try again."})
        return

    try:
        rows = _fetch_user_sessions(user["id"])
    except Exception as exc:
        log.warning("[account_sessions] list failed for %s: %s",
                    user["id"][:8] if user.get("id") else "?", exc)
        handler._json(502, {"error": "Couldn't load your active sessions. Please try again."})
        return

    request_ua = (handler.headers.get("User-Agent", "") or "")
    request_ip = _request_ip(handler)
    sanitized = [_sanitize_session(r, request_ua, request_ip) for r in rows]
    handler._json(200, {"sessions": sanitized})


def run_revoke_session(handler, session_id: str) -> None:
    """DELETE /api/account/sessions/<id> — revoke one session by id."""
    user = require_user(handler)
    if not user:
        return  # 401 already written

    # Validate session id shape BEFORE rate-limit so a path-traversal probe
    # doesn't consume the bucket.
    sid = (session_id or "").strip()
    if not _SESSION_ID_RE.fullmatch(sid):
        handler._json(400, {"error": "invalid session id"})
        return

    if not _revoke_limiter.allow(user["id"]):
        handler._json(429, {"error": "Too many revoke attempts. Please wait and try again."})
        return

    try:
        deleted = _supabase_revoke_session(user["id"], sid)
    except Exception as exc:
        log.warning("[account_sessions] revoke failed for %s/%s: %s",
                    user["id"][:8], sid[:8], exc)
        handler._json(502, {"error": "Couldn't revoke that session. Please try again."})
        return

    if not deleted:
        # Either the session doesn't exist or it belongs to another user
        # (the DB function won't delete cross-user). Return 404 either way
        # — leaking the difference would let an attacker probe for session
        # ids belonging to other users.
        handler._json(404, {"error": "Session not found."})
        return

    # Audit log — best-effort.
    try:
        from pebble.audit_log import log_event_for_handler
        log_event_for_handler(
            handler=handler,
            user_id=user["id"],
            event_type="session_revoked",
            metadata={"session_id": sid},
        )
    except Exception as exc:
        log.warning("[account_sessions] audit log write failed: %s", exc)

    handler._json(200, {"ok": True})


__all__ = [
    "run_list_sessions",
    "run_revoke_session",
    "_reset_sessions_limiter_for_tests",
    "_fetch_user_sessions",
    "_supabase_revoke_session",
    "_summarize_user_agent",
]
