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
    cookie_for_session,
    create_session,
    create_user,
    find_user_by_id,
    get_session,
    parse_session_token,
    revoke_session,
)
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
