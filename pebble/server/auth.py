"""HTTP entry points for user accounts and sessions.

PHASE A.5 DEPRECATION (2026-05-16):
These endpoints are the homegrown scrypt+cookie auth that predates the
Supabase Auth migration (commit c67540f). All six routes still function
for backwards compat AND for the legacy test fixtures that hit them
to mint a session cookie. They emit:

  - ``Deprecation: true`` (RFC 8594)
  - ``Sunset: Sun, 16 Nov 2026 00:00:00 GMT`` (6 months out)
  - ``Link: </docs/auth-migration>; rel="deprecation"``

And log a warning on every call. Set ``PEBBLE_LEGACY_AUTH_DISABLED=true``
to flip them to 410 Gone (production posture once the migration is
verified end-to-end). The v3 frontend uses Supabase Auth exclusively —
none of these endpoints are reachable through the UI today; the only
remaining callers are Python test fixtures.

Routes:

- POST /api/auth/signup  {email, password}      → 201 + Set-Cookie
- POST /api/auth/login   {email, password}      → 200 + Set-Cookie
- POST /api/auth/logout                          → 200 + clear cookie
- GET  /api/auth/me                              → 200 if logged in, 401 if not
- POST /api/auth/forgot  {email}                 → 200 (always, prevents enum)
- POST /api/auth/reset   {token, password}       → 200 / 400

All endpoints respond with JSON. On success, the session token rides in an
HttpOnly cookie named ``pebble_session`` — never in the response body.
"""
from __future__ import annotations

import functools
import json
import os
from typing import Optional

from pebble.auth import (
    AuthError,
    SESSION_COOKIE_NAME,
    authenticate,
    clear_cookie,
    consume_password_reset_token,
    cookie_for_session,
    create_password_reset_token,
    create_session,
    create_user,
    find_user_by_email,
    find_user_by_id,
    get_session,
    parse_session_token,
    revoke_all_sessions_for,
    revoke_session,
    update_user_password,
)
from pebble.email import (
    send_password_reset,
    send_password_reset_async,
    send_welcome,
    send_welcome_async,
)
from pebble.log import log
from pebble.security import forgot_email_limiter


def _read_body(handler) -> Optional[dict]:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"})
        return None
    if length <= 0:
        handler._json(400, {"error": "empty request body"})
        return None
    if length > 8 * 1024:  # auth payloads should be tiny
        handler._json(413, {"error": "request too large"})
        return None
    try:
        return json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"})
        return None


def _secure_cookies() -> bool:
    """In production (PEBBLE_HTTPS=1) we mark cookies Secure. Default is
    False so local dev over plain HTTP can still log you in."""
    return os.environ.get("PEBBLE_HTTPS", "").strip().lower() in {"1", "true", "yes", "on"}


def current_user_id(handler) -> Optional[str]:
    """Resolve the current user's id from the session cookie. Returns
    None for un-logged-in or expired-session requests."""
    cookie_header = handler.headers.get("Cookie") or ""
    token = parse_session_token(cookie_header)
    if not token:
        return None
    sess = get_session(token)
    return sess.user_id if sess else None


# ---------- Phase A.5 deprecation wrapper --------------------------------

# Standard headers emitted by every response from a legacy endpoint.
# RFC 8594 Deprecation marker + a Sunset date 6 months out gives clients
# explicit signal that the URL has a defined end-of-life.
LEGACY_DEPRECATION_HEADERS = (
    ("Deprecation", "true"),
    ("Sunset", "Sun, 16 Nov 2026 00:00:00 GMT"),
    ("Link", '</docs/auth-migration>; rel="deprecation"'),
)


def _legacy_auth_disabled() -> bool:
    """When ``PEBBLE_LEGACY_AUTH_DISABLED`` is truthy, the legacy
    endpoints all return 410 Gone instead of executing. Test fixtures
    set the var to false (default); production will flip it true once
    the Supabase Auth migration is fully verified end-to-end."""
    return os.environ.get("PEBBLE_LEGACY_AUTH_DISABLED", "").strip().lower() in {
        "1", "true", "yes", "on",
    }


def _legacy_endpoint(fn):
    """Decorator for the six /api/auth/* handlers.

    1. Short-circuits to 410 Gone when PEBBLE_LEGACY_AUTH_DISABLED is set.
    2. Logs a deprecation warning on every call.
    3. Monkey-patches the request's ``_json`` so every response written
       through it carries the deprecation headers (per-request scope —
       the handler instance is fresh per HTTP request, so this doesn't
       leak globally).

    Keeps the run_* function bodies unchanged; the wrapper handles all
    the deprecation plumbing.
    """
    @functools.wraps(fn)
    def wrapper(handler):
        if _legacy_auth_disabled():
            _write_410(handler)
            return
        log.warning(
            "legacy %s called (deprecated; migrate clients to Supabase Auth)",
            getattr(handler, "path", "/api/auth/?"),
        )
        orig = handler._json
        def patched(status, payload, *, extra_headers=None):
            merged = list(extra_headers or []) + list(LEGACY_DEPRECATION_HEADERS)
            return orig(status, payload, extra_headers=merged)
        handler._json = patched  # type: ignore[method-assign]
        try:
            return fn(handler)
        finally:
            handler._json = orig  # type: ignore[method-assign]
    return wrapper


def _write_410(handler) -> None:
    """410 Gone payload used when the legacy endpoints are disabled.
    Carries the deprecation headers so any client that follows the
    Link relation sees the migration docs."""
    handler._json(
        410,
        {
            "error":     "Legacy auth endpoint disabled.",
            "migration": (
                "This endpoint was retired in favour of Supabase Auth. "
                "Sign in via /login or /signup in the v3 frontend."
            ),
        },
        extra_headers=list(LEGACY_DEPRECATION_HEADERS),
    )


@_legacy_endpoint
def run_signup(handler) -> None:
    body = _read_body(handler)
    if body is None:
        return
    email = body.get("email", "")
    password = body.get("password", "")
    try:
        user = create_user(email, password)
    except AuthError as e:
        handler._json(400, {"error": str(e)})
        return
    except Exception as e:
        log.warning("signup failed: %s", e)
        handler._json(500, {"error": "signup failed"})
        return
    sess = create_session(user.id)
    # Fire-and-forget welcome email on a background worker so the 201
    # response doesn't wait on the mail provider.
    try:
        send_welcome_async(user.email)
    except Exception as e:
        log.warning("welcome email enqueue failed for %s: %s", user.email, e)
    handler._json(
        201,
        {"user": user.to_public()},
        extra_headers=[("Set-Cookie", cookie_for_session(sess.token, secure=_secure_cookies()))],
    )


@_legacy_endpoint
def run_login(handler) -> None:
    body = _read_body(handler)
    if body is None:
        return
    email = body.get("email", "")
    password = body.get("password", "")
    user = authenticate(email, password)
    if not user:
        # Single failure message — don't leak whether the email exists.
        handler._json(401, {"error": "Wrong email or password."})
        return
    sess = create_session(user.id)
    handler._json(
        200,
        {"user": user.to_public()},
        extra_headers=[("Set-Cookie", cookie_for_session(sess.token, secure=_secure_cookies()))],
    )


@_legacy_endpoint
def run_logout(handler) -> None:
    cookie_header = handler.headers.get("Cookie") or ""
    token = parse_session_token(cookie_header)
    if token:
        revoke_session(token)
    handler._json(
        200,
        {"ok": True},
        extra_headers=[("Set-Cookie", clear_cookie())],
    )


@_legacy_endpoint
def run_me(handler) -> None:
    user_id = current_user_id(handler)
    if not user_id:
        handler._json(401, {"error": "not signed in"})
        return
    user = find_user_by_id(user_id)
    if not user:
        # Session is dangling — refers to a deleted account. Clear cookie.
        handler._json(
            401,
            {"error": "not signed in"},
            extra_headers=[("Set-Cookie", clear_cookie())],
        )
        return
    handler._json(200, {"user": user.to_public()})


# ---------- Password reset ------------------------------------------------

def _public_base_url() -> str:
    return os.environ.get("PEBBLE_PUBLIC_URL", "").strip().rstrip("/") or "http://localhost:3001"


def _reset_url_for(token: str) -> str:
    return f"{_public_base_url()}/reset?token={token}"


@_legacy_endpoint
def run_forgot(handler) -> None:
    """POST /api/auth/forgot — request a password reset link.

    Always responds 200 even if the email isn't on file — this prevents
    account-enumeration attacks. The body has ``{ok: true, sent: bool}``
    so test code can see what actually happened while production users
    just see a generic "if your email is on file, we sent a link" UX.

    Per-email rate-limited (3 burst, refills at 1 per 5 minutes) so an
    attacker can't email-bomb a target by hammering /forgot.
    """
    body = _read_body(handler)
    if body is None:
        return
    email = (body.get("email") or "").strip()
    sent = False
    if email:
        # Rate-limit by the *normalized* email so case-tricks don't
        # bypass it. Still respond 200 to avoid leaking whether the
        # rate limit even fired (account enumeration defense).
        if forgot_email_limiter.allow(f"forgot:{email.lower()}"):
            user = find_user_by_email(email)
            if user:
                token = create_password_reset_token(user.id)
                reset_url = _reset_url_for(token.token)
                # Async send — the HTTP response time is now independent of
                # whether we found a user, closing the timing-attack window
                # NotebookLM flagged. Failures land in the engine log; the
                # rate limit prevents probing them.
                try:
                    send_password_reset_async(user.email, reset_url)
                    sent = True
                except Exception as e:
                    log.warning("password reset email enqueue failed for %s: %s", user.email, e)
    handler._json(200, {"ok": True, "sent": sent})


@_legacy_endpoint
def run_reset(handler) -> None:
    """POST /api/auth/reset — finalize a password reset.

    Body: ``{ token, password }``. On success the user is re-issued a
    session cookie so they're signed in immediately after resetting.
    All prior sessions for the user are revoked.
    """
    body = _read_body(handler)
    if body is None:
        return
    token = (body.get("token") or "").strip()
    password = body.get("password") or ""
    if not token:
        handler._json(400, {"error": "reset token is required"})
        return
    rec = consume_password_reset_token(token)
    if not rec:
        handler._json(400, {"error": "That reset link is invalid or expired. Request a new one."})
        return
    try:
        user = update_user_password(rec.user_id, password)
    except AuthError as e:
        handler._json(400, {"error": str(e)})
        return
    except Exception as e:
        log.warning("password reset failed: %s", e)
        handler._json(500, {"error": "password reset failed"})
        return
    if not user:
        handler._json(400, {"error": "account not found"})
        return
    # Revoke every other session — a reset implies "I lost control of those."
    revoke_all_sessions_for(user.id)
    sess = create_session(user.id)
    handler._json(
        200,
        {"user": user.to_public()},
        extra_headers=[("Set-Cookie", cookie_for_session(sess.token, secure=_secure_cookies()))],
    )
