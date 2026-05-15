"""HTTP entry points for user accounts and sessions.

Routes:

- POST /api/auth/signup  {email, password}      → 201 + Set-Cookie
- POST /api/auth/login   {email, password}      → 200 + Set-Cookie
- POST /api/auth/logout                          → 200 + clear cookie
- GET  /api/auth/me                              → 200 if logged in, 401 if not

All endpoints respond with JSON. On success, the session token rides in an
HttpOnly cookie named ``pebble_session`` — never in the response body.
"""
from __future__ import annotations

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
from pebble.email import send_password_reset, send_welcome
from pebble.log import log


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
    # Fire-and-forget welcome email. Never block signup on mail send.
    try:
        send_welcome(user.email)
    except Exception as e:
        log.warning("welcome email failed for %s: %s", user.email, e)
    handler._json(
        201,
        {"user": user.to_public()},
        extra_headers=[("Set-Cookie", cookie_for_session(sess.token, secure=_secure_cookies()))],
    )


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


def run_forgot(handler) -> None:
    """POST /api/auth/forgot — request a password reset link.

    Always responds 200 even if the email isn't on file — this prevents
    account-enumeration attacks. The body has ``{ok: true, sent: bool}``
    so test code can see what actually happened while production users
    just see a generic "if your email is on file, we sent a link" UX.
    """
    body = _read_body(handler)
    if body is None:
        return
    email = (body.get("email") or "").strip()
    sent = False
    if email:
        user = find_user_by_email(email)
        if user:
            token = create_password_reset_token(user.id)
            reset_url = _reset_url_for(token.token)
            try:
                send_password_reset(user.email, reset_url)
                sent = True
            except Exception as e:
                log.warning("password reset email failed for %s: %s", user.email, e)
    handler._json(200, {"ok": True, "sent": sent})


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
