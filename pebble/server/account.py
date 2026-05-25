"""HTTP endpoints for Supabase-Auth-aware account operations.

Distinct from pebble/server/auth.py (the LEGACY scrypt+cookie endpoints
deprecated in Phase A.5). All routes here validate the caller's Supabase
access token via the Bearer JWT before any privileged action.

Routes:
- GET  /api/account/profile              — fetch profile (name, timezone, deletion status)
- POST /api/account/profile              — update profile fields (first_name, display_name, timezone)
- POST /api/account/delete               — schedule GDPR deletion (14-day soft-delete)
- POST /api/account/cancel-deletion      — cancel a pending soft-delete
- POST /api/account/change-password      — re-auth + password update with audit log + notification
- POST /api/account/change-email-request — re-auth + write pending token + send confirm email
- GET  /api/account/change-email-confirm — single-use token confirm → Supabase admin updateUser
"""
from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import sys
import threading
import urllib.error
import urllib.request
import zipfile
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
from pebble.security import (
    RateLimiter,
    client_ip as _client_ip,
    require_user,
    safe_user_id as _safe_uid,
)


_delete_rate_limiter = RateLimiter(rate=1 / 1200.0, burst=3)

# Per-user rate limit on the change-password endpoint. 5 attempts/hour
# is generous for a real user (most type the new password correctly the
# first time) but tight enough to thwart brute-forcing the current-password
# challenge in a stolen-session attack.
_password_change_limiter = RateLimiter(rate=5 / 3600.0, burst=5)

# Rate limit: 1 export per user per 24h (zipping is expensive + an email
# floods inbox if hammered).
_data_export_limiter = RateLimiter(rate=1 / 86400.0, burst=1)

# Module-level OUTPUT_DIR for testability — tests monkeypatch this attribute.
# The private _output_dir() helper remains for the older functions that were
# written before this attribute existed.
OUTPUT_DIR: Path = Path(__file__).parent.parent.parent.resolve() / "output"


def _reset_delete_rate_limiter_for_tests() -> None:
    global _delete_rate_limiter
    _delete_rate_limiter = RateLimiter(rate=1 / 1200.0, burst=3)


def _reset_password_change_limiter_for_tests() -> None:
    """Test hook — clear the bucket between tests so rate-limit assertions
    are hermetic. Production callers never reach this."""
    global _password_change_limiter
    _password_change_limiter = RateLimiter(rate=5 / 3600.0, burst=5)


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

    # Cancel any active Stripe subscription FIRST so we stop billing the
    # user immediately. If this fails (Stripe down, sub already gone), we
    # log the failure but proceed — the user pressed delete and deserves
    # the account-scrub regardless.
    from pebble.audit_log import log_event_for_handler

    sub_path = _output_dir() / ".users" / user_id / "subscription.json"
    if sub_path.is_file():
        try:
            sub_data = json.loads(sub_path.read_text(encoding="utf-8"))
            sub_id  = sub_data.get("stripe_subscription_id")
            status  = sub_data.get("status")
            if sub_id and status in ("active", "trialing", "past_due"):
                ok = _cancel_stripe_subscription(sub_id)
                log_event_for_handler(
                    handler=handler, user_id=user_id,
                    event_type="stripe_subscription_canceled" if ok else "stripe_subscription_cancel_failed",
                    metadata={"subscription_id": sub_id, "prior_status": status},
                )
        except Exception as e:
            log.warning("[account] could not parse subscription.json for %s: %s", user_id, e)

    scheduled_for = _write_pending_deletion(user_id, user_email)
    days = _cooling_days()
    log.info("account deletion scheduled for %s (in %d days)", _redact(user_email), days)

    # Audit log + scheduled-deletion email (both best-effort)
    log_event_for_handler(
        handler=handler, user_id=user_id,
        event_type="account_delete_requested",
        metadata={"cooling_off_ends": scheduled_for},
    )
    try:
        from pebble.email import send_account_deletion_scheduled
        send_account_deletion_scheduled(user_email, cooling_off_ends=scheduled_for)
    except Exception as e:
        log.warning("[account] deletion-scheduled email failed for %s: %s",
                    _redact(user_email), e)

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


def _cancel_stripe_subscription(subscription_id: str) -> bool:
    """Cancel a Stripe subscription immediately (no period-end prorate).
    Returns True on success, False on any failure (logs but never raises).

    Immediate cancel rather than at-period-end because the user is
    leaving — they shouldn't pay for unused time after clicking delete.

    Called only when subscription.json shows status in (active, trialing,
    past_due) so we don't try to re-cancel an already-canceled sub.
    """
    try:
        import stripe
        stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
        stripe.Subscription.delete(subscription_id)
        return True
    except KeyError:
        log.warning("[account] STRIPE_SECRET_KEY not set — skipping cancel")
        return False
    except Exception as e:
        log.warning("[account] stripe cancel failed for %s: %s", subscription_id, e)
        return False


def _redact(email: str) -> str:
    if "@" not in email:
        return "?"
    local, _, domain = email.partition("@")
    return f"{local[:1]}***@{domain}" if local else f"***@{domain}"


# ─── POST /api/account/change-password ───────────────────────────────────────

def _reauth_user(email: str, password: str) -> tuple[bool, Optional[str]]:
    """Re-authenticate via Supabase's signInWithPassword. Returns
    (success, error_message). Never raises — network errors return
    (False, '<reason>'). Used by run_change_password to prove the
    user knows their current password before letting them change it."""
    try:
        from pebble.auth_admin import _env_url, _env_anon
        url = f"{_env_url()}/auth/v1/token?grant_type=password"
        data = json.dumps({"email": email, "password": password}).encode()
        req = urllib.request.Request(url, data=data, headers={
            "apikey": _env_anon(),
            "Content-Type": "application/json",
            "User-Agent": "PebbleEngine/1.0 (+https://pebbleapp.ai)",
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            return (resp.status == 200, None)
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read()).get("error_description") or "invalid credentials"
        except Exception:
            err = "invalid credentials"
        return (False, err)
    except Exception as exc:
        return (False, f"reauth service unavailable: {exc}")


def _update_password(user_id: str, new_password: str) -> bool:
    """Use Supabase service-role admin API to update the user's password.
    Returns True on success. Logs but doesn't raise on failure."""
    try:
        from pebble.auth_admin import _env_url, _env_anon, _env_service_role
        import urllib.parse
        url = f"{_env_url()}/auth/v1/admin/users/{urllib.parse.quote(user_id)}"
        data = json.dumps({"password": new_password}).encode()
        key = _env_service_role()
        req = urllib.request.Request(url, data=data, method="PUT", headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "PebbleEngine/1.0 (+https://pebbleapp.ai)",
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status in (200, 201, 204)
    except Exception as exc:
        log.warning("[account] _update_password failed for %s: %s",
                    user_id[:8] if user_id else "?", exc)
        return False


def run_change_password(handler) -> None:
    """POST /api/account/change-password — { current_password, new_password }.

    Requires bearer JWT. Re-authenticates with current_password against
    Supabase before issuing the admin-API password update. Writes
    audit_log + sends notification email on success. Per-user
    rate-limited to 5/hour to thwart brute-force on the current-password
    challenge.
    """
    from pebble.security import require_user
    user = require_user(handler)
    if not user:
        return  # require_user already responded 401/503

    # Per-user rate limit — applies BEFORE we parse the body so an
    # attacker can't waste cycles trying invalid payloads.
    if not _password_change_limiter.allow(user["id"]):
        handler._json(429, {"error": "Too many attempts. Please wait and try again."})
        return

    try:
        length = int(handler.headers.get("Content-Length", "0") or "0")
        body = json.loads(handler.rfile.read(min(length, 8192)).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid JSON body"})
        return

    if not isinstance(body, dict):
        handler._json(400, {"error": "invalid body"})
        return

    current = (body.get("current_password") or "").strip()
    new = (body.get("new_password") or "").strip()
    if not current or not new:
        handler._json(400, {"error": "current_password and new_password are required"})
        return
    if len(new) < 8:
        handler._json(400, {"error": "new password must be at least 8 characters"})
        return
    if current == new:
        handler._json(400, {"error": "new password must differ from current password"})
        return

    ok, err = _reauth_user(user["email"], current)
    if not ok:
        # Log the failed attempt for security forensics — a wave of these
        # against one user_id is a stolen-session indicator.
        from pebble.audit_log import log_event_for_handler
        log_event_for_handler(handler=handler, user_id=user["id"],
                              event_type="password_change_failed",
                              metadata={"reason": "wrong_current_password"})
        handler._json(401, {"error": "current password is incorrect"})
        return

    if not _update_password(user["id"], new):
        handler._json(500, {"error": "could not update password — try again in a moment"})
        return

    # Success: audit log + notification email (both best-effort)
    from pebble.audit_log import log_event_for_handler
    log_event_for_handler(handler=handler, user_id=user["id"],
                          event_type="password_change", metadata={})
    try:
        from pebble.email import send_password_changed_notification
        send_password_changed_notification(user["email"])
    except Exception as exc:
        log.warning("[account] notification email failed for %s: %s",
                    _redact(user.get("email") or "?"), exc)

    handler._json(200, {
        "ok": True,
        "message": "Password updated. Other sessions have been signed out.",
    })


# ─── POST /api/account/change-email-request ──────────────────────────────────
# ─── GET  /api/account/change-email-confirm  ─────────────────────────────────

# Per-user rate limit: 3 email-change requests / 24h. Tight because each
# request sends an email and writes a pending file; abuse pattern is a
# stolen-session attacker burning through addresses looking for one
# whose mailbox they control.
_email_change_request_limiter = RateLimiter(rate=3 / 86400.0, burst=3)

_EMAIL_CHANGE_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PENDING_EMAIL_CHANGE_TTL = timedelta(hours=24)


def _reset_email_change_limiter_for_tests() -> None:
    """Test hook — clear the bucket between tests so rate-limit assertions
    are hermetic. Production callers never reach this."""
    global _email_change_request_limiter
    _email_change_request_limiter = RateLimiter(rate=3 / 86400.0, burst=3)


def _pending_email_change_path(user_id: str) -> Path:
    safe = _safe_uid(user_id)
    if not safe:
        raise ValueError(f"invalid user_id: {user_id!r}")
    return _output_dir() / ".users" / safe / "email_change_pending.json"


def _update_user_email(user_id: str, new_email: str) -> bool:
    """Use Supabase service-role admin API to update the user's email.
    Sets email_confirm=true so the user doesn't have to re-verify on
    Supabase's side (we already verified by token). Returns True on
    success. Logs but never raises on failure."""
    try:
        from pebble.auth_admin import _env_url, _env_service_role
        import urllib.parse as _up
        url = f"{_env_url()}/auth/v1/admin/users/{_up.quote(user_id)}"
        data = json.dumps({"email": new_email, "email_confirm": True}).encode()
        key = _env_service_role()
        req = urllib.request.Request(url, data=data, method="PUT", headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "PebbleEngine/1.0 (+https://pebbleapp.ai)",
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status in (200, 201, 204)
    except Exception as exc:
        log.warning("[account] _update_user_email failed for %s: %s",
                    user_id[:8] if user_id else "?", exc)
        return False


def _get_user_email_from_supabase(user_id: str) -> Optional[str]:
    """Fetch the current email for a user via Supabase admin GET.
    Returns None if unavailable (network failure, missing key, etc.)."""
    try:
        from pebble.auth_admin import _env_url, _env_service_role
        import urllib.parse as _up
        url = f"{_env_url()}/auth/v1/admin/users/{_up.quote(user_id)}"
        key = _env_service_role()
        req = urllib.request.Request(url, headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "User-Agent": "PebbleEngine/1.0 (+https://pebbleapp.ai)",
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace"))
            return body.get("email") or None
    except Exception as exc:
        log.warning("[account] _get_user_email_from_supabase failed for %s: %s",
                    user_id[:8] if user_id else "?", exc)
        return None


def _send_email_change_confirmation_safe(*, new_email: str, token: str,
                                         current_email: str) -> None:
    """Best-effort wrapper — logs warning on failure, never raises."""
    try:
        from pebble.email import send_email_change_confirmation
        send_email_change_confirmation(new_email=new_email, token=token,
                                       current_email=current_email)
    except Exception as exc:
        log.warning("[account] confirmation email failed: %s", exc)


def _send_email_change_completed_safe(*, old_email: str, new_email: str) -> None:
    """Best-effort wrapper — logs warning on failure, never raises."""
    try:
        from pebble.email import send_email_change_completed
        send_email_change_completed(old_email=old_email, new_email=new_email)
    except Exception as exc:
        log.warning("[account] old-email notification failed: %s", exc)


def run_request_email_change(handler) -> None:
    """POST /api/account/change-email-request — { current_password, new_email }.

    Re-authenticates the user, writes a pending token in Supabase (was local
    file pre-migration-006), sends confirmation email to the NEW address.
    Per-user rate-limited 3/24h."""
    from pebble.security import require_user
    user = require_user(handler)
    if not user:
        return  # require_user already responded

    if not _email_change_request_limiter.allow(user["id"]):
        handler._json(429, {"error": "Too many email-change requests. Try again tomorrow."})
        return

    try:
        length = int(handler.headers.get("Content-Length", "0") or "0")
        body = json.loads(handler.rfile.read(min(length, 8192)).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid JSON body"})
        return

    if not isinstance(body, dict):
        handler._json(400, {"error": "invalid body"})
        return

    current_pw = (body.get("current_password") or "").strip()
    new_email = (body.get("new_email") or "").strip().lower()
    if not current_pw or not new_email:
        handler._json(400, {"error": "current_password and new_email required"})
        return
    if not _EMAIL_CHANGE_RE.match(new_email):
        handler._json(400, {"error": "new_email is not a valid address"})
        return
    if new_email == (user.get("email") or "").lower():
        handler._json(400, {"error": "new_email is the same as current email"})
        return

    ok, err = _reauth_user(user["email"], current_pw)
    if not ok:
        from pebble.audit_log import log_event_for_handler
        log_event_for_handler(handler=handler, user_id=user["id"],
                              event_type="email_change_request_failed",
                              metadata={"reason": "wrong_current_password"})
        handler._json(401, {"error": "current password is incorrect"})
        return

    # Write pending token to Supabase (single-use, 24h TTL).
    # Migration 006 moved this from output/.users/<uid>/email_change_pending.json
    # to the public.email_change_pending table so it works across instances.
    from pebble.pending_state import create_email_change_pending
    try:
        result = create_email_change_pending(user["id"], new_email, ttl_hours=24)
        token = result["token"]
    except Exception as exc:
        log.error("[account] create_email_change_pending failed for %s: %s",
                  _redact(user.get("email") or ""), exc)
        handler._json(500, {"error": "could not create email-change request — try again in a moment"})
        return

    # Audit log + confirmation email to NEW address (both best-effort).
    from pebble.audit_log import log_event_for_handler
    log_event_for_handler(handler=handler, user_id=user["id"],
                          event_type="email_change_requested",
                          metadata={"new_email_redacted": _redact(new_email)})

    _send_email_change_confirmation_safe(
        new_email=new_email,
        token=token,
        current_email=user["email"],
    )

    handler._json(200, {
        "ok": True,
        "message": (
            f"We sent a confirmation link to {new_email}. "
            "Open it within 24 hours to complete the change."
        ),
    })


def run_confirm_email_change(handler) -> None:
    """GET /api/account/change-email-confirm?token=… — single-use token
    lookup, calls Supabase admin to update email, sends notification to
    OLD address, deletes pending token.

    Lookup order (backward-compat for in-flight tokens on first deploy):
      1. Supabase public.email_change_pending table (migration 006).
      2. Fallback: scan output/.users/**/email_change_pending.json (legacy).
    Remove the fallback after Pebble has been live >24h with migration 006
    deployed (longest token TTL — no in-flight tokens can survive longer).
    """
    from urllib.parse import urlparse, parse_qs
    raw_path = getattr(handler, "_raw_path", handler.path)
    qs = parse_qs(urlparse(raw_path).query)
    token = (qs.get("token", [""])[0] or "").strip()
    if not token:
        handler._json(400, {"error": "token required"})
        return

    # ── 1. Primary lookup: Supabase ──────────────────────────────────────────
    matched_data: Optional[dict] = None
    _legacy_path: Optional[Path] = None  # set only when fallback matched

    from pebble.pending_state import lookup_email_change_pending, delete_email_change_pending
    try:
        row = lookup_email_change_pending(token)
        if row is not None:
            matched_data = row
        # None means: unknown token OR expired — fall through to legacy check
        # so we don't break tokens written before migration 006 deployed.
    except Exception as exc:
        log.warning("[account] Supabase lookup_email_change_pending failed: %s — "
                    "falling back to local files", exc)
        # Supabase unavailable: fall through to legacy scan so a DB outage
        # doesn't lock users out of confirming in-flight email changes.

    # ── 2. Legacy fallback: local filesystem ─────────────────────────────────
    # Remove this block once Pebble has been live >24h with migration 006
    # (i.e., all pre-migration tokens have expired or been consumed).
    if matched_data is None:
        users_root = _output_dir() / ".users"
        if users_root.is_dir():
            for sub in users_root.iterdir():
                if not sub.is_dir():
                    continue
                candidate = sub / "email_change_pending.json"
                if not candidate.is_file():
                    continue
                try:
                    data = json.loads(candidate.read_text(encoding="utf-8"))
                    if data.get("token") == token:
                        # Honour the expiry check that lookup_email_change_pending
                        # would have applied in the primary path.
                        try:
                            expires = datetime.fromisoformat(data["expires_at"])
                            if datetime.now(timezone.utc) > expires:
                                candidate.unlink(missing_ok=True)
                                handler._json(400, {"error": "token expired — request a new email-change"})
                                return
                        except Exception:
                            handler._json(400, {"error": "invalid pending token"})
                            return
                        matched_data = data
                        _legacy_path = candidate
                        break
                except Exception:
                    continue

    if matched_data is None:
        handler._json(404, {"error": "token not found or already used"})
        return

    new_email = matched_data["new_email"]
    user_id   = matched_data["user_id"]

    # Fetch the OLD email so we can send the 'wasn't you?' notification.
    old_email = _get_user_email_from_supabase(user_id) or ""

    if not _update_user_email(user_id, new_email):
        handler._json(500, {"error": "could not update email — try again in a moment"})
        return

    # Consume the token (delete from whichever store it came from).
    if _legacy_path is not None:
        _legacy_path.unlink(missing_ok=True)
    else:
        try:
            delete_email_change_pending(token)
        except Exception as exc:
            log.warning("[account] delete_email_change_pending failed (token consumed): %s", exc)
            # Non-fatal: the email was already updated. Token will expire naturally.

    # Audit log + notification to OLD address (both best-effort).
    from pebble.audit_log import log_event_for_handler
    log_event_for_handler(handler=handler, user_id=user_id,
                          event_type="email_change_confirmed",
                          metadata={
                              "old_email_redacted": _redact(old_email) if old_email else None,
                              "new_email_redacted": _redact(new_email),
                          })

    if old_email:
        _send_email_change_completed_safe(old_email=old_email, new_email=new_email)

    handler._json(200, {
        "ok": True,
        "message": "Email updated. Sign in again with your new address.",
    })


# ─── POST /api/account/export-request ────────────────────────────────────────
# ─── GET  /api/account/export-download  ──────────────────────────────────────


def _reset_data_export_limiter_for_tests() -> None:
    """Test hook — clear the bucket between tests so rate-limit assertions
    are hermetic. Production callers never reach this."""
    global _data_export_limiter
    _data_export_limiter = RateLimiter(rate=1 / 86400.0, burst=1)


def _exports_dir(user_id: str) -> Path:
    """Return the per-user exports directory under OUTPUT_DIR/.exports/."""
    return OUTPUT_DIR / ".exports" / user_id


def _build_export_zip(user_id: str, user_email: str,
                      handler_ua: str, handler_ip: str) -> None:
    """Background-thread worker: walk OUTPUT_DIR for the user's projects,
    zip + write a manifest + send the download email + write audit log.

    Runs in a daemon thread; never raises (exceptions are caught + logged).
    """
    try:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        exports = _exports_dir(user_id)
        exports.mkdir(parents=True, exist_ok=True)
        zip_path = exports / f"pebble-export-{ts}.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add user's projects (walk OUTPUT_DIR top-level dirs).
            for proj_dir in OUTPUT_DIR.iterdir():
                if not proj_dir.is_dir() or proj_dir.name.startswith("."):
                    continue
                brief = proj_dir / "brief.json"
                if not brief.is_file():
                    continue
                try:
                    data = json.loads(brief.read_text(encoding="utf-8"))
                    if data.get("_user_id") != user_id:
                        continue
                except Exception:
                    continue
                # Add every file under this project (exclude rebuild artifacts).
                for fp in proj_dir.rglob("*"):
                    if not fp.is_file():
                        continue
                    rel = fp.relative_to(OUTPUT_DIR)
                    parts = rel.parts
                    if any(p in ("node_modules", ".next", "out", ".turbo") for p in parts):
                        continue
                    try:
                        zf.write(fp, arcname=str(rel))
                    except Exception:
                        pass  # one bad file shouldn't kill the export

            # Add the user's .users/<id>/ directory (subscription, profile).
            user_root = OUTPUT_DIR / ".users" / user_id
            if user_root.is_dir():
                for fp in user_root.rglob("*"):
                    if fp.is_file():
                        rel = fp.relative_to(OUTPUT_DIR)
                        try:
                            zf.write(fp, arcname=str(rel))
                        except Exception:
                            pass

        # Generate single-use token + store manifest in Supabase (24h expiry).
        # Migration 006 moved manifest storage from local .manifest.json files
        # to the public.data_export_manifests table so it works across instances.
        #
        # SINGLE-INSTANCE ZIP LIMITATION: the ZIP file itself still lives on
        # local disk (output/.exports/<uid>/<ts>.zip). The download endpoint
        # must therefore run on the same engine instance that created the ZIP.
        # Multi-instance ZIP storage (S3/R2 upload after zip_path.stat()) is
        # future work — tracked as a follow-up to the NLM 2026-05-25 critique.
        from pebble.pending_state import create_data_export_manifest
        manifest_result = create_data_export_manifest(user_id, str(zip_path), ttl_hours=24)
        token = manifest_result["token"]

        # Send email with download link.
        download_url = (
            f"https://www.pebbleapp.ai/api/account/export-download?token={token}"
        )
        try:
            from pebble.email import send_data_export_ready
            send_data_export_ready(user_email, download_url)
        except Exception as email_exc:
            log.warning("[account] export email failed for %s: %s",
                        _redact(user_email), email_exc)

        # Audit log (no handler context in this thread — use log_event).
        from pebble.audit_log import log_event
        log_event(
            user_id=user_id,
            event_type="data_export_delivered",
            ip=handler_ip or None,
            user_agent=handler_ua or None,
            metadata={"zip_size_bytes": zip_path.stat().st_size},
        )
    except Exception as exc:
        log.exception("[account] export-zip worker failed for %s: %s",
                      user_id, exc)
        from pebble.audit_log import log_event
        log_event(
            user_id=user_id,
            event_type="data_export_failed",
            ip=handler_ip or None,
            user_agent=handler_ua or None,
            metadata={"error": str(exc)[:200]},
        )
        try:
            from pebble.email import send_data_export_failed
            send_data_export_failed(user_email)
        except Exception:
            pass


def run_request_data_export(handler) -> None:
    """POST /api/account/export-request — kicks off the background zip
    + emails the user a download link. Rate-limited 1/24h per user."""
    user = require_user(handler)
    if not user:
        return  # require_user already responded 401/503

    if not _data_export_limiter.allow(user["id"]):
        handler._json(429, {
            "error": "Already requested an export in the last 24 hours. Check your email."
        })
        return

    # Immediate audit log (synchronous — we have the handler here).
    from pebble.audit_log import log_event_for_handler
    log_event_for_handler(
        handler=handler, user_id=user["id"],
        event_type="data_export_requested", metadata={},
    )

    # Capture handler context BEFORE the thread starts (the handler is
    # gone once we return; the thread needs the IP/UA frozen at request time).
    handler_ua = (handler.headers.get("User-Agent") or "")[:512]
    xff = handler.headers.get("X-Forwarded-For", "") or ""
    handler_ip = xff.split(",")[0].strip() if xff else handler.client_address[0]

    t = threading.Thread(
        target=_build_export_zip,
        args=(user["id"], user["email"], handler_ua, handler_ip),
        daemon=True,
    )
    t.start()

    handler._json(200, {
        "ok": True,
        "message": (
            "Your data export is being prepared. "
            "We'll email you a download link in a few minutes."
        ),
    })


def run_download_export(handler) -> None:
    """GET /api/account/export-download?token=<token> — streams the zip.

    Auth (Fix 3, 2026-05-24): requires Bearer JWT match against the
    manifest's user_id. The token alone is NOT a capability link —
    before this fix, anyone with the URL could re-download for 24h
    (browser history, email-forward, employer mail-scanning proxy,
    shoulder-surf, etc.). The token is what makes the URL discoverable;
    the JWT is what makes the download authorized.

    The token is still NOT consumed on first download — legit retries
    (mid-download network blip, second device) need to work for the
    24h window. The auth check is what protects re-use by an attacker.

    Lookup order (backward-compat for in-flight tokens on first deploy):
      1. Supabase public.data_export_manifests table (migration 006).
      2. Fallback: scan output/.exports/**/*.manifest.json (legacy).
    Remove the fallback after Pebble has been live >24h with migration 006
    deployed (longest token TTL — no in-flight manifest can survive longer).

    NOTE: The ZIP file itself lives on local disk. The download therefore
    requires the same engine instance that created the ZIP to serve it.
    Multi-instance ZIP storage is future work (S3/R2). See _build_export_zip.
    """
    # Fix 3 (2026-05-24): require Bearer JWT BEFORE any lookup. require_user
    # writes 401/503 and returns None on auth failure; we just need to bail.
    user = require_user(handler)
    if not user:
        return

    from urllib.parse import urlparse, parse_qs
    qs = parse_qs(urlparse(handler.path).query)
    token = (qs.get("token", [""])[0] or "").strip()
    if not token:
        handler._json(400, {"error": "token required"})
        return

    # ── 1. Primary lookup: Supabase ──────────────────────────────────────────
    matched_data: Optional[dict] = None

    from pebble.pending_state import lookup_data_export_manifest
    try:
        row = lookup_data_export_manifest(token)
        if row is not None:
            matched_data = row
        # None: unknown or expired — fall through to legacy scan
    except Exception as exc:
        log.warning("[account] Supabase lookup_data_export_manifest failed: %s — "
                    "falling back to local files", exc)

    # ── 2. Legacy fallback: local .manifest.json files ───────────────────────
    # Remove this block once Pebble has been live >24h with migration 006
    # (i.e., all pre-migration tokens have expired or been consumed).
    if matched_data is None:
        exports_root = OUTPUT_DIR / ".exports"
        if exports_root.is_dir():
            for user_dir in exports_root.iterdir():
                if not user_dir.is_dir():
                    continue
                for mp in user_dir.glob("*.manifest.json"):
                    try:
                        data = json.loads(mp.read_text(encoding="utf-8"))
                        if data.get("token") == token:
                            # Apply expiry check (mirrors lookup_data_export_manifest).
                            try:
                                expires = datetime.fromisoformat(data["expires_at"])
                                if datetime.now(timezone.utc) > expires:
                                    handler._json(410, {
                                        "error": "Download link has expired. Request a new export."
                                    })
                                    return
                            except Exception:
                                handler._json(400, {"error": "invalid manifest"})
                                return
                            matched_data = data
                            break
                    except Exception:
                        continue
                if matched_data:
                    break

    if matched_data is None:
        handler._json(404, {"error": "token not found"})
        return

    # Fix 3 (2026-05-24): the authed user's id MUST match the manifest's
    # user_id. If they don't, this is a leaked-URL replay attempt: someone
    # got the link out-of-band (browser history, mail scan, screenshot)
    # and is trying to download another user's export. Return 403 (NOT
    # 404 — the mismatch IS an auth failure, and 403 lets server-side
    # detection spot the leak in logs) and audit-log the event.
    manifest_user_id = matched_data.get("user_id") or ""
    if user["id"] != manifest_user_id:
        try:
            from pebble.audit_log import log_event_for_handler
            log_event_for_handler(
                handler=handler, user_id=user["id"],
                event_type="data_export_download_denied",
                metadata={
                    "reason": "user_id mismatch",
                    "manifest_user_id_suffix": manifest_user_id[-8:] if manifest_user_id else None,
                },
            )
        except Exception:  # pragma: no cover — audit is fire-and-forget
            pass
        log.warning(
            "[account] export-download denied: user=%s requested manifest "
            "owned by user=...%s",
            user["id"], manifest_user_id[-8:] if manifest_user_id else "?",
        )
        handler._json(403, {"error": "this export does not belong to your account"})
        return

    # Expiry check for the Supabase path (lookup_data_export_manifest already
    # filters expired rows, but double-check with explicit error messaging).
    try:
        expires = datetime.fromisoformat(matched_data["expires_at"])
        if datetime.now(timezone.utc) > expires:
            handler._json(410, {
                "error": "Download link has expired. Request a new export."
            })
            return
    except Exception:
        handler._json(400, {"error": "invalid manifest"})
        return

    zip_path = Path(matched_data["zip_path"])
    if not zip_path.is_file():
        handler._json(404, {"error": "export file is no longer available"})
        return

    # Stream the zip with proper download headers.
    # Token is NOT deleted on download — the user has a 24h re-download window.
    size = zip_path.stat().st_size
    handler.send_response(200)
    handler.send_header("Content-Type", "application/zip")
    handler.send_header(
        "Content-Disposition",
        f'attachment; filename="{zip_path.name}"',
    )
    handler.send_header("Content-Length", str(size))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    with zip_path.open("rb") as f:
        while True:
            chunk = f.read(64 * 1024)
            if not chunk:
                break
            handler.wfile.write(chunk)
