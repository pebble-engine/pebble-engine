"""HTTP endpoints for Supabase-Auth-aware account operations.

Distinct from pebble/server/auth.py (the LEGACY scrypt+cookie endpoints
deprecated in Phase A.5). All routes here validate the caller's Supabase
access token via the Bearer JWT before any privileged action.

Routes:
- GET  /api/account/profile         — fetch profile (name, timezone, deletion status)
- POST /api/account/profile         — update profile fields (first_name, display_name, timezone)
- POST /api/account/delete          — schedule GDPR deletion (14-day soft-delete)
- POST /api/account/cancel-deletion — cancel a pending soft-delete
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from pebble.auth_admin import (
    AdminError,
    delete_user,
    get_profile,
    is_configured,
    update_profile,
    validate_access_token,
)
from pebble.log import log
from pebble.security import RateLimiter, client_ip as _client_ip, safe_user_id as _safe_uid


_delete_rate_limiter = RateLimiter(rate=1 / 1200.0, burst=3)


def _reset_delete_rate_limiter_for_tests() -> None:
    global _delete_rate_limiter
    _delete_rate_limiter = RateLimiter(rate=1 / 1200.0, burst=3)


def _bearer_token(handler) -> str:
    raw = handler.headers.get("Authorization", "") or ""
    if not raw.lower().startswith("bearer "):
        return ""
    return raw[7:].strip()


def _output_dir() -> Path:
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path(__file__).parent.parent.parent.resolve() / "output"


def _pending_deletion_path(user_id: str) -> Path:
    safe = _safe_uid(user_id)
    if not safe:
        raise ValueError(f"invalid user_id: {user_id!r}")
    return _output_dir() / ".users" / safe / "pending_deletion.json"


def _cooling_days() -> int:
    try:
        return max(1, int(os.environ.get("PEBBLE_DELETION_COOLING_DAYS", "14")))
    except (ValueError, TypeError):
        return 14


def _read_pending_deletion(user_id: str) -> Optional[dict]:
    p = _pending_deletion_path(user_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_pending_deletion(user_id: str, email: str) -> str:
    """Write pending_deletion.json. Returns the ISO scheduled_for string."""
    scheduled = datetime.now(timezone.utc) + timedelta(days=_cooling_days())
    scheduled_str = scheduled.isoformat()
    payload = {
        "user_id": user_id,
        "email": email,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "scheduled_for": scheduled_str,
    }
    p = _pending_deletion_path(user_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write — swap via rename so readers never see a partial file.
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(p)
    return scheduled_str


def _cancel_pending_deletion(user_id: str) -> bool:
    """Delete pending_deletion.json. Returns True if it existed."""
    p = _pending_deletion_path(user_id)
    if not p.exists():
        return False
    try:
        p.unlink()
        return True
    except OSError:
        return False


def _scrub_user_projects(user_id: str) -> int:
    """Remove all project directories owned by user_id.

    Iterates output/<slug>/brief.json files and deletes any slug directory
    where brief["_user_id"] == user_id. Returns the count of directories
    removed. Called after the Supabase hard-delete so local files don't
    outlive the account (Ch 7.7 GDPR follow-up).

    Also removes output/.users/<user_id>/ (drip state, subscription sentinel,
    pending deletion marker).
    """
    out = _output_dir()
    removed = 0
    for brief_path in out.glob("*/brief.json"):
        try:
            brief = json.loads(brief_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if brief.get("_user_id") == user_id:
            slug_dir = brief_path.parent
            try:
                shutil.rmtree(slug_dir)
                removed += 1
                log.info("gdpr scrub: removed project dir %s", slug_dir.name)
            except OSError as exc:
                log.warning("gdpr scrub: could not remove %s: %s", slug_dir.name, exc)
    user_dir = out / ".users" / user_id
    if user_dir.exists():
        try:
            shutil.rmtree(user_dir)
        except OSError as exc:
            log.warning("gdpr scrub: could not remove user dir %s: %s", user_id, exc)
    return removed


def _execute_deletion_if_due(user_id: str, email: str) -> bool:
    """If a pending deletion exists and is past its scheduled_for date,
    execute the hard delete now. Returns True if deletion was executed."""
    pd = _read_pending_deletion(user_id)
    if not pd:
        return False
    scheduled_str = pd.get("scheduled_for", "")
    if not scheduled_str:
        return False
    try:
        scheduled = datetime.fromisoformat(scheduled_str)
    except (ValueError, TypeError):
        return False
    if datetime.now(timezone.utc) < scheduled:
        return False
    # Past the cooling-off period — execute now.
    log.info("executing scheduled deletion for %s", _redact(email))
    try:
        delete_user(user_id)
    except AdminError as e:
        log.error("scheduled deletion failed for %s: %s", _redact(email), e)
        return False
    scrubbed = _scrub_user_projects(user_id)
    log.info("gdpr scrub: %d project(s) removed for %s", scrubbed, _redact(email))
    _cancel_pending_deletion(user_id)
    return True


# ─── GET /api/account/profile ────────────────────────────────────────────────

def run_select_plan(handler) -> None:
    """POST /api/account/select-plan — Phase 54b (2026-05-23).

    Clears the ``needs_plan_selection`` flag for the caller. Used by the
    post-signup plan picker (Phase 54c) when the user explicitly picks
    Free / Starter / Pro / Enterprise.

    Body::

        { "plan": "free" | "starter" | "pro" | "enterprise" }

    For Free: just clears the flag. The user gets all default Free
    benefits (1 site, 30 refinements/mo, etc.) without us needing to
    write a subscription.json — absence of subscription IS the Free
    plan in our resolution logic.

    For paid plans: clears the flag AND returns the Stripe checkout
    URL — the v3 frontend redirects there. The flag stays cleared even
    if the user abandons checkout, because they've still made an
    intentional pick (they CHOSE paid, just didn't pay yet). The plan
    they actually get is still "free" until Stripe webhook confirms
    payment.

    Auth: Bearer Supabase access token (same pattern as the rest of
    /api/account/*). 401 if missing/invalid.
    """
    if not is_configured():
        handler._json(503, {"error": "Account service not configured"})
        return
    token = _bearer_token(handler)
    if not token:
        handler._json(401, {"error": "missing Bearer access token"})
        return
    try:
        user = validate_access_token(token)
    except AdminError as e:
        handler._json(502, {"error": f"could not validate session: {e}"})
        return
    if user is None:
        handler._json(401, {"error": "session is invalid or expired"})
        return

    user_id = user.get("id") or ""
    if not user_id:
        handler._json(401, {"error": "session lacks user id"})
        return

    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length"})
        return
    if length <= 0 or length > 1024:
        handler._json(400, {"error": "invalid request body length"})
        return
    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        handler._json(400, {"error": "invalid JSON body"})
        return

    plan = (body or {}).get("plan")
    if plan not in ("free", "starter", "pro", "enterprise"):
        handler._json(400, {"error": "plan must be one of: free, starter, pro, enterprise"})
        return

    from pebble.user_plan import set_needs_plan_selection
    ok = set_needs_plan_selection(user_id, False)
    if not ok:
        handler._json(500, {"error": "failed to record plan selection"})
        return

    log.info("user picked %s plan (user_id=%s)", plan, _redact(user.get("email") or ""))

    # For paid plans, the frontend should follow up with POST /api/checkout/
    # create-session to get the Stripe URL. We don't auto-call it here
    # because returning a redirect URL inside a JSON response is awkward
    # and the existing checkout endpoint already handles the pricing-tier
    # lookup. Return the picked plan so the frontend knows which next
    # step to take.
    handler._json(200, {
        "ok":            True,
        "plan_selected": plan,
        "next":          "build" if plan == "free" else "checkout",
    })


def run_get_profile(handler) -> None:
    """Return the caller's profile row plus any pending deletion info."""
    if not is_configured():
        handler._json(503, {"error": "Account service not configured"})
        return
    token = _bearer_token(handler)
    if not token:
        handler._json(401, {"error": "missing Bearer access token"})
        return
    try:
        user = validate_access_token(token)
    except AdminError as e:
        handler._json(502, {"error": f"could not validate session: {e}"})
        return
    if user is None:
        handler._json(401, {"error": "session is invalid or expired"})
        return

    user_id = user.get("id") or ""
    user_email = user.get("email") or ""

    # Single read — used for both past-due cleanup and response payload.
    pending = _read_pending_deletion(user_id)
    if pending:
        scheduled_str = pending.get("scheduled_for", "")
        try:
            if scheduled_str and datetime.now(timezone.utc) >= datetime.fromisoformat(scheduled_str):
                log.info("executing scheduled deletion for %s", _redact(user_email))
                try:
                    delete_user(user_id)
                    scrubbed = _scrub_user_projects(user_id)
                    log.info("gdpr scrub: %d project(s) removed for %s", scrubbed, _redact(user_email))
                    _cancel_pending_deletion(user_id)
                    handler._json(410, {"error": "account deleted", "deleted": True})
                    return
                except AdminError as e:
                    log.error("scheduled deletion failed for %s: %s", _redact(user_email), e)
                    pending = None
        except (ValueError, TypeError):
            pass

    try:
        profile = get_profile(user_id) or {}
    except AdminError as e:
        log.warning("get_profile failed for %s: %s", _redact(user_email), e)
        profile = {}

    handler._json(200, {
        "id":           user_id,
        "email":        user_email,
        "first_name":   profile.get("first_name"),
        "display_name": profile.get("display_name"),
        "timezone":     profile.get("timezone") or "UTC",
        "plan_tier":    profile.get("plan_tier") or "free",
        "deletion_scheduled_for": pending.get("scheduled_for") if pending else None,
    })


# ─── POST /api/account/profile ───────────────────────────────────────────────

try:
    from zoneinfo import available_timezones as _load_timezones
    _ALLOWED_TIMEZONES: frozenset[str] = frozenset(_load_timezones())
except Exception:
    _ALLOWED_TIMEZONES = frozenset()


def _is_valid_timezone(tz: str) -> bool:
    if _ALLOWED_TIMEZONES:
        return tz in _ALLOWED_TIMEZONES
    return bool(tz) and len(tz) <= 64 and "\n" not in tz


def run_patch_profile(handler) -> None:
    """Update first_name, display_name, and/or timezone for the caller."""
    if not is_configured():
        handler._json(503, {"error": "Account service not configured"})
        return
    token = _bearer_token(handler)
    if not token:
        handler._json(401, {"error": "missing Bearer access token"})
        return
    try:
        user = validate_access_token(token)
    except AdminError as e:
        handler._json(502, {"error": f"could not validate session: {e}"})
        return
    if user is None:
        handler._json(401, {"error": "session is invalid or expired"})
        return

    try:
        length = int(handler.headers.get("Content-Length", 0) or 0)
        body = json.loads(handler.rfile.read(min(length, 8192)).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid JSON body"})
        return

    updates: dict = {}
    for field in ("first_name", "display_name"):
        if field in body:
            val = body[field]
            if val is not None and not isinstance(val, str):
                handler._json(400, {"error": f"{field} must be a string or null"})
                return
            updates[field] = val.strip() if isinstance(val, str) else val

    if "timezone" in body:
        tz = body["timezone"]
        if not isinstance(tz, str) or not _is_valid_timezone(tz):
            handler._json(400, {"error": "timezone must be a valid IANA timezone string"})
            return
        updates["timezone"] = tz

    if not updates:
        handler._json(400, {"error": "nothing to update — send first_name, display_name, or timezone"})
        return

    user_id = user.get("id") or ""
    try:
        updated = update_profile(user_id, updates) or {}
    except AdminError as e:
        log.warning("update_profile failed for user %s: %s", user_id[:8], e)
        handler._json(502, {"error": f"profile update failed: {e}"})
        return

    handler._json(200, {
        "ok": True,
        "first_name":   updated.get("first_name"),
        "display_name": updated.get("display_name"),
        "timezone":     updated.get("timezone") or "UTC",
    })


# ─── POST /api/account/delete ────────────────────────────────────────────────

def run_delete_account(handler) -> None:
    """Schedule GDPR account deletion with a 14-day cooling-off period.

    Flow:
    1. Validate the bearer JWT.
    2. Rate-limit per IP to prevent token-oracle abuse.
    3. If a pending deletion is already scheduled and past due → execute now.
    4. If a pending deletion is in-progress → return its scheduled_for date
       (idempotent — caller can display "your account will be deleted on ...").
    5. Otherwise: write pending_deletion.json and return 200 with scheduled_for.

    The actual hard delete (delete_user) fires on the next GET /api/account/profile
    call after the cooling-off period, or when the user explicitly confirms by
    hitting this endpoint again once scheduled_for has passed.

    Project files in output/<slug>/ are NOT touched here — see Ch 7.7 note.
    """
    if not is_configured():
        handler._json(503, {"error": "Account deletion is not configured on this Pebble instance."})
        return

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

    # Past-due lazy cleanup.
    if _execute_deletion_if_due(user_id, user_email):
        handler._json(200, {
            "ok": True, "deleted": True, "user_id": user_id, "next": "/landing",
        })
        return

    # Already scheduled and within cooling-off — return existing schedule.
    pd = _read_pending_deletion(user_id)
    if pd:
        handler._json(200, {
            "ok": True,
            "scheduled": True,
            "scheduled_for": pd.get("scheduled_for"),
            "message": (
                f"Your account is already scheduled for deletion on "
                f"{pd.get('scheduled_for', '?')[:10]}. "
                "Use POST /api/account/cancel-deletion to undo."
            ),
        })
        return

    # New deletion request — enter cooling-off period.
    scheduled_for = _write_pending_deletion(user_id, user_email)
    days = _cooling_days()
    log.info("account deletion scheduled for %s (in %d days)", _redact(user_email), days)
    handler._json(200, {
        "ok": True,
        "scheduled": True,
        "scheduled_for": scheduled_for,
        "cooling_days": days,
        "message": (
            f"Your account is scheduled for deletion on {scheduled_for[:10]}. "
            "You can cancel this within the cooling-off period."
        ),
        "next": "/settings",
    })


# ─── POST /api/account/cancel-deletion ───────────────────────────────────────

def run_cancel_deletion(handler) -> None:
    """Cancel a pending soft-delete within the cooling-off window."""
    if not is_configured():
        handler._json(503, {"error": "Account service not configured"})
        return

    token = _bearer_token(handler)
    if not token:
        handler._json(401, {"error": "missing Bearer access token"})
        return

    try:
        user = validate_access_token(token)
    except AdminError as e:
        handler._json(502, {"error": f"could not validate session: {e}"})
        return
    if user is None:
        handler._json(401, {"error": "session is invalid or expired"})
        return

    user_id = user.get("id") or ""
    user_email = user.get("email") or "?"

    if _execute_deletion_if_due(user_id, user_email):
        # Past due — it's already gone.
        handler._json(410, {
            "error": "account already deleted (cooling-off period expired)",
            "deleted": True,
        })
        return

    cancelled = _cancel_pending_deletion(user_id)
    if cancelled:
        log.info("account deletion cancelled for %s", _redact(user_email))
    handler._json(200, {
        "ok": True,
        "cancelled": cancelled,
        "message": (
            "Deletion cancelled. Your account is safe."
            if cancelled
            else "No pending deletion to cancel."
        ),
    })


def _redact(email: str) -> str:
    if "@" not in email:
        return "?"
    local, _, domain = email.partition("@")
    return f"{local[:1]}***@{domain}" if local else f"***@{domain}"
