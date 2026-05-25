"""POST /api/account/global-signout — sign out every session for the
calling user.

Phase D.3 (2026-05-24). Forwards the user's JWT to Supabase's
``POST /auth/v1/logout?scope=global`` which revokes every refresh token
for that user — including the current one. After Supabase confirms,
writes an audit_log row + sends a defensive-notify email so a real
customer who DIDN'T initiate the sign-out finds out fast.

Why route through the engine instead of letting v3 call
``supabase.auth.signOut({scope:'global'})`` directly:

  - The audit_log row attaches IP + User-Agent that Supabase wouldn't
    know about. Forensic value: "what device hit the sign-out button".
  - The notification email needs a server-side trigger anyway (the v3
    frontend doesn't know the Resend key).
  - Single endpoint means the frontend just calls one place + clears its
    local session storage. No race between two parallel calls (audit
    row vs sign-out) leaving the user signed-out without an audit row.

The Supabase global sign-out invalidates the JWT the engine just used —
that's by design. The frontend gracefully handles the now-invalid token
by clearing its local Supabase client state + redirecting to /login.

Rate-limited 3/hour per user: tight because every call sends an email
and triggers a security-relevant state change. A user clicking it twice
by mistake is fine; a flood is abuse.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from pebble.auth_admin import _env_anon, _env_url
from pebble.log import log
from pebble.security import RateLimiter, require_user


# 3 sign-outs/hour per user. Each call sends an email and revokes every
# session, so it's a heavy hammer — but a real user shouldn't be hitting
# this more than once per session.
_global_signout_limiter = RateLimiter(rate=3 / 3600.0, burst=3)


def _reset_global_signout_limiter_for_tests() -> None:
    """Test hook — clear the bucket between tests so rate-limit assertions
    are hermetic. Production callers never reach this."""
    global _global_signout_limiter
    _global_signout_limiter = RateLimiter(rate=3 / 3600.0, burst=3)


def _bearer_token(handler) -> str:
    """Extract the raw JWT from the Authorization header. Returns "" if
    missing or malformed. Used to forward to Supabase verbatim."""
    raw = (handler.headers.get("Authorization", "") or "").strip()
    if not raw.lower().startswith("bearer "):
        return ""
    return raw[7:].strip()


def _supabase_global_signout(user_jwt: str) -> bool:
    """Call Supabase's POST /auth/v1/logout?scope=global with the user's
    JWT. Returns True on 2xx, False on any failure.

    The endpoint takes the user JWT in the Authorization header (NOT the
    service-role key — this is a user-scoped action and Supabase needs
    to know whose sessions to nuke). On success, every refresh token for
    the user is invalidated; the access token in the request is also
    revoked.

    Note: Supabase's GoTrue accepts both 'global' and 'others' here.
    We always use 'global' — the frontend redirects to /login regardless,
    so leaving the current session valid would be confusing UX.
    """
    if not user_jwt:
        return False
    url = f"{_env_url()}/auth/v1/logout?scope=global"
    req = urllib.request.Request(url, method="POST", headers={
        "apikey":        _env_anon(),
        "Authorization": f"Bearer {user_jwt}",
        "User-Agent":    "PebbleEngine/1.0 (+https://pebbleapp.ai)",
    })
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as e:
        log.warning("[account_signout] Supabase logout HTTP %s for user", e.code)
        return False
    except urllib.error.URLError as e:
        log.warning("[account_signout] Supabase unreachable: %s", e.reason)
        return False
    except Exception as exc:
        log.warning("[account_signout] unexpected error: %s", exc)
        return False


def run_global_signout(handler) -> None:
    """POST /api/account/global-signout — sign out every session for the
    calling user. Returns {ok: true} on success, 502 on Supabase failure.

    Audit row + notification email are written ONLY after Supabase confirms
    — otherwise we'd be telling the user "we signed you out" when we didn't.
    """
    user = require_user(handler)
    if not user:
        return  # 401 already written

    if not _global_signout_limiter.allow(user["id"]):
        handler._json(429, {"error": "Too many sign-out attempts. Please wait and try again."})
        return

    user_jwt = _bearer_token(handler)
    if not user_jwt:
        # require_user passed but bearer somehow missing — shouldn't
        # happen in practice but defends against future refactors.
        handler._json(401, {"error": "missing bearer token"})
        return

    if not _supabase_global_signout(user_jwt):
        handler._json(502, {
            "error": "Couldn't sign out other sessions. Please try again in a moment.",
        })
        return

    # Supabase confirmed — write audit row + send email. Both best-effort
    # but the user is ALREADY signed out at this point. Failures here don't
    # roll back the sign-out (can't un-revoke a JWT once GoTrue burns it).
    try:
        from pebble.audit_log import log_event_for_handler
        log_event_for_handler(
            handler=handler,
            user_id=user["id"],
            event_type="global_signout",
            metadata={},
        )
    except Exception as exc:
        log.warning("[account_signout] audit log write failed: %s", exc)

    try:
        from pebble.email import send_global_signout_notification
        send_global_signout_notification(user["email"])
    except Exception as exc:
        log.warning("[account_signout] notification email failed: %s", exc)

    handler._json(200, {
        "ok": True,
        "message": "Every session has been signed out. Sign in again to continue.",
    })


__all__ = [
    "run_global_signout",
    "_reset_global_signout_limiter_for_tests",
    "_supabase_global_signout",
]
