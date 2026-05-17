"""HTTP endpoints for the new Supabase-Auth-aware account flows.

Distinct from pebble/server/auth.py (the LEGACY scrypt+cookie endpoints
under /api/auth/* that Phase A.5 deprecated). This module is the
forward-looking surface for account operations that need server-side
admin powers — currently just GDPR delete, but profile edits and
session revocation will land here too.

The caller (v3 frontend) must include the visitor's Supabase access
token as ``Authorization: Bearer <jwt>``. The engine validates the
token via GoTrue's /auth/v1/user endpoint before any privileged
action — that's what distinguishes this from the legacy /api/auth/*
flow (which used the engine's own session cookie).

Routes:

- POST /api/account/delete   — GDPR account deletion. Validates the
                                bearer JWT, admin-deletes the user
                                from Supabase Auth (which cascades to
                                public.profiles via FK).
"""
from __future__ import annotations

from pebble.auth_admin import (
    AdminError,
    delete_user,
    is_configured,
    validate_access_token,
)
from pebble.log import log
from pebble.security import RateLimiter, client_ip as _client_ip


# Per-IP rate limit for account deletion. Account-delete is RARE in
# normal use (a user might do it once, ever) — anything more than 3
# attempts in an hour from one IP is abuse or a token-spray oracle.
# NLM round on Track 12 flagged the unbounded endpoint as a side-
# channel for validating stolen tokens via the 401-vs-200 difference.
_delete_rate_limiter = RateLimiter(rate=1/1200.0, burst=3)


def _reset_delete_rate_limiter_for_tests() -> None:
    global _delete_rate_limiter
    _delete_rate_limiter = RateLimiter(rate=1/1200.0, burst=3)


def _bearer_token(handler) -> str:
    """Pull the bearer token out of the Authorization header.
    Returns empty string when missing or malformed (so the caller
    can 401 cleanly)."""
    raw = handler.headers.get("Authorization", "") or ""
    if not raw.lower().startswith("bearer "):
        return ""
    return raw[7:].strip()


def run_delete_account(handler) -> None:
    """POST /api/account/delete — admin-delete the calling user from
    Supabase. Requires `Authorization: Bearer <supabase-access-token>`.

    Flow:
    1. Pull the bearer token. 401 if missing.
    2. Validate via GoTrue's /auth/v1/user. 401 if the token is bad.
    3. Admin-delete the user. 502 if Supabase rejects.
    4. Return 200 + a JSON body the v3 client uses to confirm signout.

    Project files in output/<slug>/ are NOT touched here — see Ch 7.7
    follow-up sweep. Cascade deletes the auth.users row + the FK-bound
    public.profiles row, which is enough to log them out everywhere
    and break their cookies.
    """
    if not is_configured():
        log.warning("account-delete called but PEBBLE_SUPABASE_* env not set")
        handler._json(503, {
            "error": (
                "Account deletion is not configured on this Pebble instance. "
                "Set PEBBLE_SUPABASE_URL, PEBBLE_SUPABASE_SERVICE_ROLE_KEY, "
                "and PEBBLE_SUPABASE_ANON_KEY."
            ),
        })
        return

    # Per-IP rate limit. Closes the "validate-stolen-tokens-in-bulk"
    # oracle NLM flagged on Track 12 — 401-vs-200 differs only when a
    # token is valid, so unbounded calls let an attacker mass-test.
    ip = _client_ip(handler)
    if ip and not _delete_rate_limiter.allow(f"acct-delete:{ip}"):
        handler._json(429, {"error": "too many delete attempts, slow down"})
        return

    token = _bearer_token(handler)
    if not token:
        handler._json(401, {"error": "missing Bearer access token"})
        return

    try:
        user = validate_access_token(token)
    except AdminError as e:
        log.warning("account-delete validate failed: %s", e)
        handler._json(502, {"error": f"could not validate session: {e}"})
        return

    if user is None:
        handler._json(401, {"error": "session is invalid or expired"})
        return

    user_id = user.get("id") or ""
    user_email = user.get("email") or "?"
    try:
        delete_user(user_id)
    except AdminError as e:
        log.warning("account-delete failed for %s: %s", _redact(user_email), e)
        handler._json(502, {"error": f"delete failed: {e}"})
        return

    log.info("account deleted for %s", _redact(user_email))
    # NOTE ON LINGERING JWTs (NLM round on Track 12 flag):
    # Supabase JWTs are self-validating against the project secret
    # with a 1-hour default TTL. Deleting the auth.users row stops
    # REFRESH (the refresh token requires a valid user row), so the
    # blast radius caps at the remaining access-token TTL. The v3
    # frontend's middleware uses supabase.auth.getUser() which hits
    # the database — that immediately returns no-user after delete,
    # so v3 routes redirect to /login on the next page load even
    # within the TTL window. Acceptable posture for now.
    handler._json(200, {
        "ok":      True,
        "deleted": True,
        "user_id": user_id,
        # The v3 client should sign-out + redirect to /landing after this.
        "next":    "/landing",
    })


def _redact(email: str) -> str:
    """`marc@example.com` → `m***@example.com` for safe logging."""
    if "@" not in email:
        return "?"
    local, _, domain = email.partition("@")
    return f"{local[:1]}***@{domain}" if local else f"***@{domain}"
