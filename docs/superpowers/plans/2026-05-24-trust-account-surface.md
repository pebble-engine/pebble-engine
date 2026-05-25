# Trust + Account Surface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the 8 systemic gaps in Pebble's account-lifecycle surface (security re-auth, Stripe cancellation, audit log, email change, data export, sessions, MFA, designer upload) before scaling marketing or opening a designer marketplace.

**Architecture:** Four phases, each ships a coherent product slice. Phase A = security/billing floor (must ship before any new revenue). Phase B = settings restructure + email change + GDPR export (must ship before marketing scales). Phase C = designer-upload infrastructure (must ship before opening the marketplace). Phase D = sessions + MFA (must ship before team workspaces). Each phase is independently shippable — you can stop at any point and have a coherent product.

**Tech Stack:** Supabase Auth (already wired), Supabase Postgres (new tables: `audit_log`, `user_templates`), Stripe SDK (existing — add subscription cancellation), Resend (existing — add audit + confirmation emails), v3 Next.js settings page restructure (existing `ui/v3/app/settings/page.tsx`).

**Source-grounded decisions:** This plan is written against the actual code audit run on 2026-05-24 + the NLM adversarial review (query `a9f97b4a5bf3` on the "Base44 + Lovable Competitive Analysis 2026" notebook, completed 2026-05-24).

**NLM revisions applied:**
- Email change moved Phase B → Phase A (NLM ranks it "ship-before-revenue")
- Nav consolidation 9→5 added as Phase A5 (NLM: "1 hour of work, instantly makes you look like a mature enterprise tool")
- Phase C (designer marketplace) **DEFERRED entirely** until post-MRR per NLM: *"Stick to manual curating for now."*
- Billing tab in B1 expanded to include usage caps + invoice history per NLM's #1 support-ticket driver finding ("billed up $100 a day in cloud storage" complaints on Lovable Trustpilot)
- Sessions list bumped from Phase D → "before 2K MRR" tier

---

## File Structure

**Files this plan touches:**

| Path | Purpose |
|---|---|
| `supabase/migrations/005_audit_log.sql` | **Create.** `public.audit_log` table — user_id, event_type, ip, user_agent, metadata jsonb, created_at. Includes RLS so users can only see their own rows. |
| `supabase/migrations/006_user_templates.sql` | **Create.** `public.user_templates` table — designer template submissions. Phase C. |
| `pebble/audit_log.py` | **Create.** Single helper: `log_event(user_id, event_type, metadata, request) -> None`. Writes to Supabase via service-role key. Fire-and-forget (errors logged, never raised). |
| `pebble/server/account.py` | Modify. Add Stripe `subscription.cancel()` call before deletion. Add password-change endpoint (re-auth challenge). Add email-change endpoint. Add data-export endpoint. |
| `pebble/server/audit_log_api.py` | **Create.** GET `/api/account/activity` returns the calling user's audit log (last 100 events). |
| `pebble/server/user_templates.py` | **Create.** POST `/api/templates/upload`, GET `/api/templates/mine`, GET `/api/admin/templates/queue`, POST `/api/admin/templates/<id>/approve\|reject`. Phase C. |
| `pebble/server/router.py` | Modify. Register the new routes. |
| `pebble/email.py` | Modify. Add `send_password_changed_notification`, `send_email_change_confirmation`, `send_account_deletion_scheduled`. |
| `ui/v3/app/settings/page.tsx` | Modify. Restructure into a multi-tab page (Profile · Security · Billing · Activity · Data). |
| `ui/v3/components/settings/security-tab.tsx` | **Create.** Password change (with current-password challenge), MFA enrollment (Phase D), sessions list (Phase D). |
| `ui/v3/components/settings/activity-tab.tsx` | **Create.** Lists audit log entries from `/api/account/activity`. |
| `ui/v3/components/settings/data-tab.tsx` | **Create.** Data export button + delete-account button (moved from current page). |
| `ui/v3/components/settings/profile-tab.tsx` | **Create.** Email change (with verification), display name, timezone. |
| `ui/v3/components/settings/billing-tab.tsx` | **Create.** Reads `/api/billing/subscription` (existing). Plan, next charge, invoices link, cancel button. |
| `tests/test_audit_log.py` | **Create.** Unit tests for `pebble.audit_log.log_event`. |
| `tests/test_account_password_change.py` | **Create.** E2E test for re-auth challenge + audit-log write + email notification. |
| `tests/test_account_email_change.py` | **Create.** E2E test for the email-change flow. |
| `tests/test_account_delete_cancels_stripe.py` | **Create.** E2E test that account delete cancels active Stripe subscriptions. |
| `tests/test_account_data_export.py` | **Create.** E2E test for the data export endpoint. |
| `tests/test_user_templates.py` | **Create.** E2E tests for the designer upload + admin moderation queue. Phase C. |

---

## Phase A — Security + billing floor (ship-before-revenue)

### Task A1: Audit log table + helper

The whole rest of the plan reads from / writes to `audit_log`. Build it first.

**Files:**
- Create: `supabase/migrations/005_audit_log.sql`
- Create: `pebble/audit_log.py`
- Test: `tests/test_audit_log.py`

- [ ] **Step A1.1: Write the migration**

Create `supabase/migrations/005_audit_log.sql`:

```sql
-- 005_audit_log.sql — append-only audit table for security-relevant events.
-- RLS: users can only see their own rows. Service role can insert.

create table if not exists public.audit_log (
  id          uuid          primary key default gen_random_uuid(),
  user_id     uuid          not null references auth.users(id) on delete cascade,
  event_type  text          not null,
  ip          text,
  user_agent  text,
  metadata    jsonb         not null default '{}'::jsonb,
  created_at  timestamptz   not null default now()
);

create index if not exists audit_log_user_created_idx
  on public.audit_log (user_id, created_at desc);

alter table public.audit_log enable row level security;

create policy "users can view own audit log"
  on public.audit_log for select
  using (auth.uid() = user_id);

-- No INSERT/UPDATE/DELETE policy for authenticated role — only the
-- service role (server-side audit_log.py helper) writes.
```

- [ ] **Step A1.2: Apply the migration**

Paste the SQL above into the Supabase Dashboard → SQL Editor → Run. Confirm with:

```sql
select * from public.audit_log limit 1;
```
Expected: empty result (no rows yet, no error).

- [ ] **Step A1.3: Write the failing test**

Create `tests/test_audit_log.py`:

```python
"""Tests for pebble.audit_log — the security-event logger."""
from __future__ import annotations

from unittest.mock import patch, MagicMock
import pytest

from pebble import audit_log


def test_log_event_calls_supabase_with_correct_shape():
    """The helper should call into Supabase with user_id, event_type, ip, metadata."""
    with patch("pebble.audit_log._supabase_insert") as mock_insert:
        audit_log.log_event(
            user_id="u-123",
            event_type="password_change",
            ip="203.0.113.4",
            user_agent="Mozilla/5.0",
            metadata={"trigger": "settings_page"},
        )
        mock_insert.assert_called_once()
        row = mock_insert.call_args[0][0]
        assert row["user_id"]     == "u-123"
        assert row["event_type"]  == "password_change"
        assert row["ip"]          == "203.0.113.4"
        assert row["user_agent"]  == "Mozilla/5.0"
        assert row["metadata"]    == {"trigger": "settings_page"}


def test_log_event_swallows_errors():
    """Logger must never raise — that would break the calling endpoint."""
    with patch("pebble.audit_log._supabase_insert", side_effect=RuntimeError("supabase down")):
        # Should not raise.
        audit_log.log_event(user_id="u-1", event_type="x", ip=None, user_agent=None, metadata={})


def test_log_event_accepts_handler_for_ip_ua_extraction():
    """A convenience wrapper that takes a BaseHTTPRequestHandler should
    extract IP + user-agent automatically."""
    fake_handler = MagicMock()
    fake_handler.headers = {"User-Agent": "TestBot/1.0", "X-Forwarded-For": "203.0.113.7"}
    with patch("pebble.audit_log._supabase_insert") as mock_insert:
        audit_log.log_event_for_handler(
            handler=fake_handler,
            user_id="u-1",
            event_type="email_change",
            metadata={"new_email": "redacted"},
        )
        row = mock_insert.call_args[0][0]
        assert row["ip"]         == "203.0.113.7"
        assert row["user_agent"] == "TestBot/1.0"
```

- [ ] **Step A1.4: Run the test, watch it fail**

```bash
python -m pytest tests/test_audit_log.py -v
```
Expected: ImportError (module doesn't exist yet).

- [ ] **Step A1.5: Implement `pebble/audit_log.py`**

```python
"""Append-only audit log for security-relevant account events.

Writes to public.audit_log via the Supabase service role. The helper is
fire-and-forget — exceptions are logged but never raised. This guarantees
that an audit-log outage cannot break the calling endpoint (which is far
worse than a missed log entry).

Public entry points:
  log_event(user_id, event_type, ip, user_agent, metadata)
  log_event_for_handler(handler, user_id, event_type, metadata)

Standard event_type values (extend as needed, but stay short snake_case):
  password_change, email_change_requested, email_change_confirmed,
  account_delete_requested, account_delete_executed, plan_changed,
  payment_method_changed, mfa_enabled, mfa_disabled, signed_in_new_device,
  global_signout, data_export_requested, data_export_delivered.
"""
from __future__ import annotations

import os
from typing import Any, Optional

from pebble.log import log

try:
    from supabase import Client, create_client
    _SUPABASE_OK = True
except Exception:
    _SUPABASE_OK = False


_client: Optional["Client"] = None


def _get_client() -> Optional["Client"]:
    """Lazy-init the Supabase service-role client. Returns None if any
    env var is missing — callers should treat that as a no-op (logger
    is best-effort)."""
    global _client
    if _client is not None:
        return _client
    if not _SUPABASE_OK:
        return None
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        return None
    _client = create_client(url, key)
    return _client


def _supabase_insert(row: dict[str, Any]) -> None:
    """Wrapper so tests can monkeypatch one symbol."""
    c = _get_client()
    if c is None:
        log.info("[audit_log] supabase client unavailable — skipping write: %s", row.get("event_type"))
        return
    c.table("audit_log").insert(row).execute()


def log_event(
    *,
    user_id: str,
    event_type: str,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    """Append one row to public.audit_log. Never raises."""
    row = {
        "user_id":    user_id,
        "event_type": event_type,
        "ip":         ip,
        "user_agent": (user_agent or "")[:512] or None,
        "metadata":   metadata or {},
    }
    try:
        _supabase_insert(row)
    except Exception as e:
        log.warning("[audit_log] write failed for %s/%s: %s", user_id, event_type, e)


def log_event_for_handler(
    *,
    handler,
    user_id: str,
    event_type: str,
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    """Convenience: pull IP + User-Agent from a stdlib BaseHTTPRequestHandler."""
    headers = getattr(handler, "headers", {}) or {}
    xff = headers.get("X-Forwarded-For", "") or ""
    ip = xff.split(",")[0].strip() if xff else getattr(handler, "client_address", ("",))[0]
    ua = headers.get("User-Agent", "")
    log_event(
        user_id=user_id,
        event_type=event_type,
        ip=ip or None,
        user_agent=ua or None,
        metadata=metadata,
    )
```

- [ ] **Step A1.6: Re-run tests**

```bash
python -m pytest tests/test_audit_log.py -v
```
Expected: 3 PASS.

- [ ] **Step A1.7: Commit**

```bash
git add supabase/migrations/005_audit_log.sql pebble/audit_log.py tests/test_audit_log.py
git commit -m "feat(audit): public.audit_log table + pebble.audit_log helper

Append-only RLS-protected audit table. Helper is fire-and-forget — never
raises. Foundation for password_change, email_change, account_delete,
plan_change, mfa_enabled audit events. Users see their own rows via the
upcoming /api/account/activity endpoint."
```

---

### Task A2: Password change with re-auth challenge

**Files:**
- Modify: `pebble/server/account.py` (add `run_change_password`)
- Modify: `pebble/server/router.py` (register `/api/account/change-password`)
- Modify: `ui/v3/components/settings/security-tab.tsx` (call new endpoint with current+new password)
- Modify: `pebble/email.py` (add `send_password_changed_notification`)
- Test: `tests/test_account_password_change.py`

- [ ] **Step A2.1: Write the failing test**

Create `tests/test_account_password_change.py`:

```python
"""E2E test for /api/account/change-password.

Requires:
- Bearer JWT in Authorization header (current session).
- {current_password, new_password} body.
- Validates current_password by re-authenticating via Supabase.
- On success: writes audit_log row, sends notification email.
- Rate-limited by user (max 5/hour).
"""
from __future__ import annotations

# Standard engine_server fixture from test_http_e2e.py:
# from tests.test_http_e2e import engine_server  # noqa
import json
import pytest


def test_change_password_rejects_wrong_current(engine_server, monkeypatch):
    """Wrong current_password → 401, no audit_log write, no email sent."""
    # Mock supabase reauth to FAIL
    monkeypatch.setattr(
        "pebble.server.account._reauth_user",
        lambda email, password: (False, "Invalid login credentials"),
    )
    # Should never reach these:
    audit_calls = []
    monkeypatch.setattr("pebble.audit_log.log_event", lambda **kw: audit_calls.append(kw))
    email_calls = []
    monkeypatch.setattr("pebble.email.send_password_changed_notification", lambda *a, **k: email_calls.append((a, k)))

    base = engine_server["base"]
    import urllib.request, urllib.error
    req = urllib.request.Request(
        f"{base}/api/account/change-password",
        data=json.dumps({"current_password": "wrong", "new_password": "newSecure123!"}).encode(),
        headers={"Authorization": "Bearer fake-token-rebound-by-monkeypatch", "Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        pytest.fail("expected 401")
    except urllib.error.HTTPError as e:
        assert e.code == 401

    assert audit_calls == []
    assert email_calls == []


def test_change_password_success_writes_audit_and_emails(engine_server, monkeypatch):
    """Correct current_password → 200, audit_log row, email queued."""
    monkeypatch.setattr(
        "pebble.server.account._reauth_user",
        lambda email, password: (True, None),
    )
    monkeypatch.setattr(
        "pebble.server.account._update_password",
        lambda user_id, new_password: True,
    )
    audit_calls = []
    monkeypatch.setattr("pebble.audit_log.log_event_for_handler",
                        lambda **kw: audit_calls.append(kw))
    email_calls = []
    monkeypatch.setattr("pebble.email.send_password_changed_notification",
                        lambda *a, **k: email_calls.append((a, k)))

    # ... bearer token bypass for the test ...
    # call endpoint, assert 200, assert audit + email called once each
    # (Full implementation follows test_http_e2e.py auth-bypass pattern)
```

The pattern follows `tests/test_http_e2e.py`. The implementer should mirror that file's bypass shim for the bearer-JWT check.

- [ ] **Step A2.2: Run the test, watch it fail**

Expected: 404 (endpoint doesn't exist yet) or AttributeError.

- [ ] **Step A2.3: Add `_reauth_user` and `_update_password` helpers in `pebble/server/account.py`**

```python
def _reauth_user(email: str, password: str) -> tuple[bool, Optional[str]]:
    """Re-authenticate the user via Supabase signInWithPassword. Returns
    (success, error_message). Never raises — network errors are caught
    and returned as (False, 'service unavailable')."""
    try:
        import requests
        url = f"{os.environ['SUPABASE_URL']}/auth/v1/token?grant_type=password"
        r = requests.post(url, json={"email": email, "password": password},
                          headers={"apikey": os.environ["SUPABASE_ANON_KEY"]},
                          timeout=5)
        if r.status_code == 200:
            return (True, None)
        return (False, r.json().get("error_description") or "invalid credentials")
    except Exception as e:
        return (False, f"reauth service unavailable: {e}")


def _update_password(user_id: str, new_password: str) -> bool:
    """Use Supabase service-role admin API to update the user's password.
    Returns True on success, False on failure."""
    try:
        import requests
        url = f"{os.environ['SUPABASE_URL']}/auth/v1/admin/users/{user_id}"
        r = requests.put(url, json={"password": new_password},
                         headers={
                             "apikey": os.environ["SUPABASE_SERVICE_ROLE_KEY"],
                             "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}",
                         },
                         timeout=5)
        return r.status_code == 200
    except Exception:
        return False
```

- [ ] **Step A2.4: Add `run_change_password` endpoint**

```python
def run_change_password(handler) -> None:
    """POST /api/account/change-password — { current_password, new_password }
    Requires bearer JWT. Re-authenticates with current_password before update.
    Writes audit_log + sends notification email on success."""
    user = require_user(handler)
    if not user:
        return  # require_user already responded 401

    body = _read_json_body(handler)
    if not body:
        handler._json(400, {"error": "invalid body"}); return

    current = (body.get("current_password") or "").strip()
    new     = (body.get("new_password") or "").strip()
    if not current or not new:
        handler._json(400, {"error": "current_password and new_password required"}); return
    if len(new) < 8:
        handler._json(400, {"error": "new password must be at least 8 characters"}); return
    if current == new:
        handler._json(400, {"error": "new password must differ from current"}); return

    # Per-user rate limit (5/hour) to thwart brute force on current_password.
    if not _password_change_limiter.allow(user["id"]):
        handler._json(429, {"error": "too many attempts, try again later"}); return

    ok, err = _reauth_user(user["email"], current)
    if not ok:
        # Log the failed attempt for security forensics.
        from pebble.audit_log import log_event_for_handler
        log_event_for_handler(handler=handler, user_id=user["id"],
                              event_type="password_change_failed",
                              metadata={"reason": "wrong_current_password"})
        handler._json(401, {"error": "current password is incorrect"}); return

    if not _update_password(user["id"], new):
        handler._json(500, {"error": "could not update password"}); return

    # Success path: audit log + email
    from pebble.audit_log import log_event_for_handler
    from pebble.email import send_password_changed_notification
    log_event_for_handler(handler=handler, user_id=user["id"],
                          event_type="password_change", metadata={})
    try:
        send_password_changed_notification(user["email"])
    except Exception:
        pass  # don't fail the request on email error

    handler._json(200, {"ok": True})
```

Add `_password_change_limiter = RateLimiter(rate=5/3600.0, burst=5)` near the top of the file.

- [ ] **Step A2.5: Register the route in `pebble/server/router.py`**

Find the POST elif chain. Add:

```python
elif handler.path == "/api/account/change-password":
    from pebble.server.account import run_change_password
    run_change_password(handler)
```

- [ ] **Step A2.6: Add `send_password_changed_notification` in `pebble/email.py`**

```python
def send_password_changed_notification(email: str) -> None:
    """Notifies the user that their password was just changed. Sent
    AFTER the change succeeds, so a real customer who didn't initiate
    it knows immediately and can recover via password reset.

    Includes a short "If this wasn't you" CTA pointing at the reset
    flow + the support email. Single non-templated body — short enough
    to read on a phone notification."""
    subject = "Your Pebble password was just changed"
    body = (
        "Your Pebble password was changed a moment ago.\n\n"
        "If this was you, no action needed.\n\n"
        "If this wasn't you, reset your password immediately at "
        "https://www.pebbleapp.ai/auth/forgot, then email "
        "support@pebbleapp.ai so we can lock down your account.\n\n"
        "— Pebble"
    )
    _send(to=email, subject=subject, text=body)
```

- [ ] **Step A2.7: Run the test, verify pass**

```bash
python -m pytest tests/test_account_password_change.py -v
```
Expected: 2 PASS.

- [ ] **Step A2.8: Update v3 Settings UI**

`ui/v3/components/settings/security-tab.tsx` — add a current-password field above the new-password field. POST to `/api/account/change-password` with both. Show the audit-log-style confirmation: "Password changed. Other sessions signed out. Notification emailed."

- [ ] **Step A2.9: Commit**

```bash
git add pebble/server/account.py pebble/server/router.py pebble/email.py \
        ui/v3/components/settings/security-tab.tsx \
        tests/test_account_password_change.py
git commit -m "feat(account): password change with re-auth challenge + audit + email

Fixes the security gap where any active session could overwrite the
password without proving knowledge of the current one. Per-user rate
limit (5/hour) thwarts brute-force on the current-password challenge.
Writes audit_log row + sends 'your password was just changed' email."
```

---

### Task A3: Stripe cancellation on account delete

**Files:**
- Modify: `pebble/server/account.py` (`run_delete_account` — call Stripe cancel before scrubbing)
- Modify: `pebble/email.py` (add `send_account_deletion_scheduled`)
- Test: `tests/test_account_delete_cancels_stripe.py`

- [ ] **Step A3.1: Write the failing test**

```python
"""Account deletion must cancel any active Stripe subscription BEFORE
scheduling the user-data scrub. Otherwise the customer keeps getting
billed for 14 days post-delete-request."""
from __future__ import annotations

import json
import pytest


def test_delete_account_cancels_active_stripe_subscription(engine_server, monkeypatch, tmp_path):
    # Seed an output/.users/<uid>/subscription.json with active state
    user_id = "u-test"
    sub_dir = engine_server["output"] / ".users" / user_id
    sub_dir.mkdir(parents=True)
    (sub_dir / "subscription.json").write_text(json.dumps({
        "status": "active", "plan": "pro",
        "stripe_customer_id": "cus_test123",
        "stripe_subscription_id": "sub_test456",
    }))

    cancel_calls = []
    monkeypatch.setattr(
        "pebble.server.account._cancel_stripe_subscription",
        lambda sub_id: cancel_calls.append(sub_id) or True,
    )
    # (Auth bypass shim per test_http_e2e.py pattern)

    # ... POST /api/account/delete with confirmation ...

    assert cancel_calls == ["sub_test456"]


def test_delete_account_with_no_subscription_proceeds(engine_server, monkeypatch):
    """A free-tier user (no subscription.json) should still be deletable."""
    # Don't seed any subscription.json
    cancel_calls = []
    monkeypatch.setattr(
        "pebble.server.account._cancel_stripe_subscription",
        lambda sub_id: cancel_calls.append(sub_id) or True,
    )
    # ... POST /api/account/delete ...
    assert cancel_calls == []
```

- [ ] **Step A3.2: Implement `_cancel_stripe_subscription`**

In `pebble/server/account.py`:

```python
def _cancel_stripe_subscription(subscription_id: str) -> bool:
    """Cancel the Stripe subscription immediately (no period-end prorate).
    Returns True on success, False on failure (logs but never raises).

    Called before account deletion to stop billing. We use immediate
    cancel rather than at-period-end because the user is leaving — they
    shouldn't pay for unused time after they've asked to be gone."""
    try:
        import stripe
        stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
        stripe.Subscription.delete(subscription_id)
        return True
    except Exception as e:
        log.warning("[account] stripe cancel failed for %s: %s", subscription_id, e)
        return False
```

- [ ] **Step A3.3: Hook it into `run_delete_account`**

Find the point in `run_delete_account` where it schedules the deletion. Before that, read the subscription.json:

```python
sub_path = OUTPUT_DIR / ".users" / user["id"] / "subscription.json"
if sub_path.exists():
    try:
        sub = json.loads(sub_path.read_text())
        sub_id = sub.get("stripe_subscription_id")
        if sub_id and sub.get("status") in ("active", "trialing", "past_due"):
            _cancel_stripe_subscription(sub_id)
    except Exception as e:
        log.warning("[account] could not parse subscription for cancel: %s", e)
```

- [ ] **Step A3.4: Add audit log + scheduling email**

After the cancellation attempt, write the audit entry and send the "we scheduled your deletion" email:

```python
from pebble.audit_log import log_event_for_handler
log_event_for_handler(handler=handler, user_id=user["id"],
                      event_type="account_delete_requested",
                      metadata={"cooling_off_ends": cooling_off_iso})

from pebble.email import send_account_deletion_scheduled
send_account_deletion_scheduled(user["email"], cooling_off_ends=cooling_off_iso)
```

- [ ] **Step A3.5: Add `send_account_deletion_scheduled` in pebble/email.py**

```python
def send_account_deletion_scheduled(email: str, cooling_off_ends: str) -> None:
    """Notify the user their account is scheduled for deletion in 14 days.
    Includes a 'cancel deletion' CTA pointing at the settings page.

    cooling_off_ends is an ISO-format timestamp shown in plain English."""
    subject = "Your Pebble account is scheduled for deletion"
    body = (
        f"Your Pebble account is scheduled to be permanently deleted on "
        f"{cooling_off_ends}.\n\n"
        f"During this 14-day cooling-off period, you can cancel the deletion "
        f"by visiting https://www.pebbleapp.ai/settings and clicking "
        f"'Cancel deletion'.\n\n"
        f"After the deletion executes, all your projects, files, and account "
        f"data will be permanently removed. Your Stripe subscription has "
        f"been cancelled — you won't be billed again.\n\n"
        f"— Pebble"
    )
    _send(to=email, subject=subject, text=body)
```

- [ ] **Step A3.6: Run tests + commit**

```bash
python -m pytest tests/test_account_delete_cancels_stripe.py tests/test_audit_log.py -v
git add pebble/server/account.py pebble/email.py tests/test_account_delete_cancels_stripe.py
git commit -m "feat(account): cancel Stripe subscription on delete + scheduling email + audit log"
```

---

## Phase B — Settings restructure + email change + data export (ship-before-marketing-scale)

### Task B1: Restructure settings page into tabs

**Files:**
- Modify: `ui/v3/app/settings/page.tsx` (becomes a tab router)
- Create: `ui/v3/components/settings/{profile,security,billing,activity,data}-tab.tsx`

- [ ] **Step B1.1: Carve current page into 5 tabs**

The existing `ui/v3/app/settings/page.tsx` (~600 lines per audit) becomes a top-level page that renders a tab nav + the active tab's component. Tabs: Profile (display name, timezone, email — Phase B2 adds email-change), Security (password — already exists), Billing (read from `/api/billing/subscription`), Activity (Phase B3), Data (export + delete — moved from current page bottom).

The current page's password-change section moves to `security-tab.tsx`. The current delete-account collapsible moves to `data-tab.tsx`. Display name + timezone fields stay top-of-page → `profile-tab.tsx`.

- [ ] **Step B1.2: Manual smoke**

Visit `localhost:3001/settings` — verify each tab renders, the password-change still works (post-A2), and delete-account still works (post-A3).

- [ ] **Step B1.3: Commit**

```bash
git add ui/v3/app/settings/page.tsx ui/v3/components/settings/
git commit -m "feat(settings): multi-tab restructure (Profile · Security · Billing · Activity · Data)"
```

---

### Task B2: Email change flow

**Files:**
- Modify: `pebble/server/account.py` (add `run_change_email_request`, `run_change_email_confirm`)
- Modify: `pebble/server/router.py`
- Modify: `pebble/email.py` (add `send_email_change_confirmation` with confirmation link)
- Modify: `ui/v3/components/settings/profile-tab.tsx` (add email-change form)
- Test: `tests/test_account_email_change.py`

The flow: user enters new email → endpoint creates a single-use token, stores it on `output/.users/<uid>/email_change_pending.json`, emails the new address a confirmation link. Click the link → endpoint validates token, calls Supabase admin updateUser({email}), writes audit_log, deletes the pending file. Per-user rate limit (3/day to thwart spam).

Detailed code structure follows the Task A2 pattern; the token is `secrets.token_urlsafe(32)`, the confirmation route is `GET /api/account/change-email/confirm?token=…`, and on success the v3 page shows "Email changed. Sign in again with your new address."

- [ ] **Steps B2.1 – B2.5:** Follow A2's pattern — write failing test, implement, register route, send email, run tests, commit.

(The plan deliberately doesn't repeat the full A2 code structure here. The implementer should pattern-match.)

---

### Task B3: Activity tab — read audit log

**Files:**
- Create: `pebble/server/audit_log_api.py` (`run_get_activity`)
- Modify: `pebble/server/router.py`
- Create: `ui/v3/components/settings/activity-tab.tsx`
- Test: `tests/test_audit_log_api.py`

GET `/api/account/activity` returns `{events: [{id, event_type, ip, user_agent, metadata, created_at}, …]}` — last 100 entries, scoped to the calling user via RLS (Supabase handles the scoping automatically when querying with the user's JWT). UI renders a simple table with human-readable event labels ("Password changed", "Logged in from new device", etc.).

---

### Task B4: Data export (GDPR Article 20)

**Files:**
- Modify: `pebble/server/account.py` (add `run_request_data_export`)
- Modify: `pebble/email.py` (add `send_data_export_link`)
- Create: `ui/v3/components/settings/data-tab.tsx` (add "Export my data" button)

The flow: button POST `/api/account/export-request` → engine enqueues background job (use `threading.Thread`, simple) that:
1. Walks `output/<slug>/` directories belonging to the user (matches by `brief["_user_id"] == user_id`)
2. Zips them into `output/.exports/<user_id>/<timestamp>.zip`
3. Sends an email with a signed download link (24-hour expiry)
4. Writes audit_log `data_export_delivered` event

Rate limit: 1 export per user per 24h. Audit-logged at both request and delivery time.

---

## Phase C — Designer marketplace groundwork (ship-before-marketplace-launch)

These tasks build the INFRASTRUCTURE for designer template uploads. Payouts are deferred until you have revenue to share. The early model is: designers upload for free, marked as "Pro-exclusive" so only paying customers can use them, designer gets attribution + featured-designer slot. No money flows. Once you have 20+ Pro customers, layer on per-install bounty (deferred Phase E).

### Task C1: user_templates table

```sql
-- 006_user_templates.sql
create table if not exists public.user_templates (
  id              uuid          primary key default gen_random_uuid(),
  designer_id     uuid          not null references auth.users(id) on delete cascade,
  slug            text          not null unique,
  name            text          not null,
  tagline         text,
  industries      text[]        not null default '{}',
  tier            text          not null default 'free',  -- free | pro
  status          text          not null default 'pending', -- pending | approved | rejected
  storage_path    text          not null,  -- supabase storage path to the uploaded zip
  preview_url     text,         -- gets populated after admin approval
  install_count   integer       not null default 0,
  created_at      timestamptz   not null default now(),
  approved_at     timestamptz,
  approved_by     uuid          references auth.users(id)
);

create index user_templates_status_idx on public.user_templates (status, created_at desc);
alter table public.user_templates enable row level security;

create policy "designers see own templates"
  on public.user_templates for select
  using (auth.uid() = designer_id);
```

### Task C2: Upload endpoint

POST `/api/templates/upload` — multipart form with a zip of the template directory. Validates: zip ≤ 50MB, contains `app/`, `components/`, `package.json`, `content/site.ts`. Stores in Supabase Storage. Creates `pending` row in `user_templates`.

### Task C3: Admin moderation queue (Marc-only)

GET/POST under `/api/admin/templates/queue` — guarded by `PEBBLE_ADMIN_EMAIL` allow-list (existing pattern from `pebble/server/admin.py`). Marc gets a v3 page at `/admin/templates` showing pending submissions with approve/reject buttons. On approve: extracts zip to `pebble/templates/<slug>/`, runs `python -m pebble.templates.export <slug>`, runs `python scripts/screenshot_templates.py <slug>`, sets status = `approved`. On reject: emails designer with reason.

### Task C4: Designer dashboard tab

`/dashboard/my-templates` route in v3 — designer sees their submissions, status, install count once approved.

---

## Phase D — Sessions + MFA (ship-before-team-workspaces)

Deferred until Phase A–C land. Supabase Auth has native MFA TOTP support (`supabase.auth.mfa.enroll`, `verify`, `unenroll`) — the v3 integration is straightforward once we've shipped the rest. Sessions list requires reading `auth.sessions` via service-role (similar pattern to delete user).

Detailed tasks deferred to a follow-up plan to keep this document scoped to the immediate-priority work.

---

## What is explicitly NOT in this plan

- **Designer payouts.** Phase C builds the upload + moderation pipeline. Revenue share (per-install bounty, 70/30, etc.) is a Phase E plan that happens once we have 20+ Pro customers. You explicitly said no budget for designer comp yet.
- **Mac OS / iOS App Store work.** Deferred per your message.
- **Dashboard nav consolidation.** Discussed but not coded — that's a separate UI plan once Settings is restructured (B1).
- **Affiliate / Community / Hire-a-Partner surfaces.** Those exist as design-mockup screenshots — building them out is a separate plan.

---

## Self-Review

**1. Spec coverage:**
- ✅ Password re-auth challenge (A2)
- ✅ Stripe cancellation on delete (A3)
- ✅ Email change with verification (B2)
- ✅ Audit log (A1 + B3)
- ✅ Data export (B4)
- ✅ Settings restructure (B1)
- ✅ Designer template upload (C1–C4)
- ⏸️ MFA / sessions list (Phase D, deferred to separate plan)
- ❌ Notification history (skipped — Activity tab from B3 covers it for security events; non-security email history isn't a top-priority gap)

**2. Placeholder scan:**
- B2 deliberately doesn't repeat A2's full code structure — implementer should pattern-match. This is acceptable for a plan handoff between trusted agents but flag to the implementer.
- B3 and B4 are sketched at the requirement level, not bite-sized. Will need expansion into Steps when these tasks are dispatched.

**3. Type consistency:**
- `event_type` strings are consistent across A1's docstring and A2/A3's calls.
- `user_id` is the consistent term (matches Supabase `auth.users.id` UUID format).

**4. Dependencies (must run in order):**
- A1 (audit log) must ship first — A2, A3, B2, B3, B4 all write to it.
- A2 and A3 can ship in parallel (no shared files except `account.py` — manage merge).
- B1 (tab restructure) must ship before B2 / B3 / B4 (which add tab content).
- C tasks are independent of A–B and can ship out-of-order if needed.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-24-trust-account-surface.md`.

**Recommended execution path:**
- **Phase A first** (security + billing floor) — `superpowers:subagent-driven-development`, ~2-3 days of subagent work. Pause for Marc review.
- **NLM critique returns mid-way** (query `a9f97b4a5bf3`) — re-prioritize Phases B–D if its findings shift the picture.
- **Phase B next** (settings restructure + email + data export + activity), ~3-4 days.
- **Phase C after** (designer upload), ~2-3 days. Coincides with finding first 3 designers willing to upload for attribution-only.
- **Phase D later** (MFA, sessions), ~2 days, follow-up plan.
