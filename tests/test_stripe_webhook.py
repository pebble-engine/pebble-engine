"""Tests for POST /api/internal/stripe-webhook — receives Stripe events,
verifies the HMAC signature, and updates the user's subscription sentinel.

We sign payloads with a REAL HMAC against a test ``whsec_`` value (instead
of mocking ``stripe.Webhook.construct_event``) so the test suite exercises
the actual signature-verify path. This is load-bearing: an earlier
incarnation of this file mocked construct_event to return a dict, which
hid two SDK-15.x compat bugs that 400'd every real event in production
(StripeObject != dict, and verify_header's "%d.%s" formatter mishandling
bytes).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from io import BytesIO
from typing import Any

import pytest

import pebble_engine


WEBHOOK_SECRET = "whsec_test_unit_secret"


def _sign_event(event_dict: dict, secret: str = WEBHOOK_SECRET,
                ts: int | None = None) -> tuple[bytes, str]:
    """Produce the (raw_body_bytes, Stripe-Signature header) pair that a
    legitimately-signed Stripe webhook delivery would carry. ``ts`` lets
    callers control the v1 timestamp for time-tolerance tests; default
    is "now"."""
    if ts is None:
        ts = int(time.time())
    payload = json.dumps(event_dict, separators=(",", ":")).encode("utf-8")
    signed = f"{ts}.".encode("utf-8") + payload
    sig = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    return payload, f"t={ts},v1={sig}"


# ---------- handler + fixtures --------------------------------------------

class FakeHandler:
    def __init__(self, body: dict | bytes | str | None = None,
                 sig_header: str | None = "t=1,v1=fakefakefake"):
        if isinstance(body, dict):
            raw = json.dumps(body).encode("utf-8")
        elif isinstance(body, str):
            raw = body.encode("utf-8")
        elif isinstance(body, bytes):
            raw = body
        else:
            raw = b""
        self.rfile = BytesIO(raw)
        self.headers: dict[str, str] = {"Content-Length": str(len(raw))}
        if sig_header is not None:
            self.headers["Stripe-Signature"] = sig_header
        self.client_address = ("127.0.0.1", 12345)
        self.status: int | None = None
        self.body: dict | None = None

    def _json(self, status: int, payload: dict, extra_headers=None) -> None:  # noqa: ARG002
        self.status = status
        self.body = payload


@pytest.fixture
def with_secret(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", WEBHOOK_SECRET)


@pytest.fixture
def output_root(tmp_path, monkeypatch):
    """Redirect output/.users/... writes into a tmp dir so tests don't
    touch the developer's real output/ directory."""
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    return tmp_path


# Monotonic counter so every _subscription_event() call gets a unique
# (event_id, event_created) pair by default. The webhook now dedups by
# event_id and rejects events with .created older than the stored state,
# so tests that call the handler multiple times need DIFFERENT defaults
# per call. Reset between tests via the _reset_event_counter fixture.
_event_counter = [0]


def _subscription_event(
    event_type: str = "customer.subscription.created",
    *,
    event_id: str | None = None,
    event_created: int | None = None,
    pebble_user_id: str | None = "uuid-marc-abc",
    plan: str | None = "starter",
    status: str = "active",
    period_end: int = 1893456000,  # 2030-01-01
    subscription_id: str = "sub_test_abc",
    customer_id: str | None = "cus_test_abc",
    extra_meta: dict | None = None,
) -> dict:
    """Build a Stripe event dict shaped like the real `customer.subscription.*`
    payloads, with the metadata we stamp in checkout."""
    _event_counter[0] += 1
    if event_id is None:
        event_id = f"evt_test_{_event_counter[0]}"
    if event_created is None:
        # Monotonically increasing default; tests that need a specific
        # order override these explicitly.
        event_created = 1_700_000_000 + _event_counter[0]
    metadata: dict[str, Any] = {}
    if pebble_user_id is not None:
        metadata["pebble_user_id"] = pebble_user_id
    if plan is not None:
        metadata["pebble_plan"] = plan
    if extra_meta:
        metadata.update(extra_meta)
    obj: dict[str, Any] = {
        "id":                  subscription_id,
        "object":              "subscription",
        "status":              status,
        "current_period_end":  period_end,
        "metadata":            metadata,
        "items": {"data": [{"price": {"id": "price_test"}}]},
    }
    if customer_id is not None:
        obj["customer"] = customer_id
    return {
        "id":      event_id,
        "type":    event_type,
        "created": event_created,
        "data":    {"object": obj},
    }


@pytest.fixture(autouse=True)
def _reset_event_counter():
    """Reset the event counter between tests so default ids/timestamps are
    deterministic per-test."""
    _event_counter[0] = 0
    yield
    _event_counter[0] = 0


@pytest.fixture
def verified_event():
    """Build a FakeHandler shaped like the request a real Stripe-signed
    delivery would produce. Returns the handler so callers can pass it
    straight to ``run_stripe_webhook``."""

    def _build(event_dict: dict, *, secret: str = WEBHOOK_SECRET,
               ts: int | None = None) -> "FakeHandler":
        payload, sig_header = _sign_event(event_dict, secret=secret, ts=ts)
        return FakeHandler(body=payload, sig_header=sig_header)
    return _build


# ---------- config / auth gates --------------------------------------------

def test_returns_503_when_webhook_secret_not_configured(monkeypatch):
    """No STRIPE_WEBHOOK_SECRET set → 503 — visible misconfiguration, not
    a silent accept-everything."""
    from pebble.server import stripe_webhook

    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
    h = FakeHandler({"id": "evt"})
    stripe_webhook.run_stripe_webhook(h)
    assert h.status == 503


def test_returns_400_when_signature_header_missing(with_secret):
    """No Stripe-Signature header → 400. Not 401 — Stripe's docs are clear
    this is a malformed request, not an auth challenge."""
    from pebble.server import stripe_webhook

    h = FakeHandler({"id": "evt"}, sig_header=None)
    stripe_webhook.run_stripe_webhook(h)
    assert h.status == 400


def test_returns_400_when_signature_invalid(with_secret):
    """SignatureVerificationError → 400. Critical defense: never act on
    an event whose HMAC didn't verify, even if the payload 'looks' valid.

    No fixture mocking — the FakeHandler's default sig_header is junk,
    so the real ``stripe.WebhookSignature.verify_header`` rejects it.
    That's exactly the path real bad-signature deliveries exercise."""
    from pebble.server import stripe_webhook

    h = FakeHandler({"id": "evt"})  # default sig_header = "t=1,v1=fakefakefake"
    stripe_webhook.run_stripe_webhook(h)
    assert h.status == 400


# ---------- body parsing ---------------------------------------------------

def test_returns_400_on_huge_body(with_secret):
    """Stripe webhook payloads are small (~few KB). 1 MB is abuse."""
    from pebble.server import stripe_webhook

    huge = b"x" * (1024 * 1024)
    h = FakeHandler(huge)
    stripe_webhook.run_stripe_webhook(h)
    assert h.status == 400


# ---------- subscription side-effects --------------------------------------

def test_subscription_created_writes_sentinel(
    with_secret, output_root, verified_event,
):
    """Verified subscription.created event → output/.users/<uid>/subscription.json
    populated with status, plan, period_end, subscription_id."""
    from pebble.server import stripe_webhook

    h = verified_event(_subscription_event(
        event_type="customer.subscription.created",
        pebble_user_id="uuid-marc-abc",
        plan="starter",
        status="active",
        period_end=1893456000,
        subscription_id="sub_starter_one",
    ))
    stripe_webhook.run_stripe_webhook(h)

    assert h.status == 200
    sentinel = output_root / ".users" / "uuid-marc-abc" / "subscription.json"
    assert sentinel.exists()
    data = json.loads(sentinel.read_text(encoding="utf-8"))
    assert data["status"] == "active"
    assert data["plan"] == "starter"
    assert data["stripe_subscription_id"] == "sub_starter_one"
    assert data["current_period_end"] == 1893456000


def test_current_period_end_falls_back_to_subscription_item(
    with_secret, output_root, verified_event,
):
    """Stripe API 2026-04-22.dahlia moved current_period_end from the
    Subscription root onto SubscriptionItem. Newer events have
    items.data[0].current_period_end populated and the root field
    missing/null. The webhook must read both shapes; without the
    fallback Marc's first live subscription wrote a sentinel with
    current_period_end: null and the v3 badge degraded to "Pebble
    Starter" instead of "Pebble Starter — renews <date>".
    """
    from pebble.server import stripe_webhook
    import json as _json

    event = _subscription_event()
    # Strip the root field, populate items[0] like Stripe's new shape
    event["data"]["object"]["current_period_end"] = None
    event["data"]["object"]["items"] = {
        "data": [{"id": "si_test", "current_period_end": 1781712163}]
    }
    h = verified_event(event)
    stripe_webhook.run_stripe_webhook(h)

    sentinel = output_root / ".users" / "uuid-marc-abc" / "subscription.json"
    data = _json.loads(sentinel.read_text(encoding="utf-8"))
    assert data["current_period_end"] == 1781712163


def test_subscription_created_stamps_customer_id(
    with_secret, output_root, verified_event,
):
    """The Stripe customer_id MUST land in the sentinel — the billing
    portal endpoint reads it to mint a customer-portal session, and we
    don't want to call Stripe to resolve the customer per portal hit."""
    from pebble.server import stripe_webhook

    h = verified_event(_subscription_event(
        event_type="customer.subscription.created",
        customer_id="cus_marc_real",
    ))
    stripe_webhook.run_stripe_webhook(h)

    sentinel = output_root / ".users" / "uuid-marc-abc" / "subscription.json"
    data = json.loads(sentinel.read_text(encoding="utf-8"))
    assert data["stripe_customer_id"] == "cus_marc_real"


def test_subscription_updated_overwrites_sentinel(
    with_secret, output_root, verified_event,
):
    """Same user, second event → file overwritten with latest state."""
    from pebble.server import stripe_webhook

    # First event: status active
    h = verified_event(_subscription_event(
        event_type="customer.subscription.created",
        plan="starter", status="active", subscription_id="sub_one",
    ))
    stripe_webhook.run_stripe_webhook(h)

    # Second event: same user, plan upgraded to pro
    h = verified_event(_subscription_event(
        event_type="customer.subscription.updated",
        plan="pro", status="active", subscription_id="sub_one",
    ))
    stripe_webhook.run_stripe_webhook(h)

    sentinel = output_root / ".users" / "uuid-marc-abc" / "subscription.json"
    data = json.loads(sentinel.read_text(encoding="utf-8"))
    assert data["plan"] == "pro"


def test_subscription_deleted_marks_canceled(
    with_secret, output_root, verified_event,
):
    """customer.subscription.deleted → status: canceled."""
    from pebble.server import stripe_webhook

    h = verified_event(_subscription_event(
        event_type="customer.subscription.deleted",
        status="canceled",
        subscription_id="sub_one",
    ))
    stripe_webhook.run_stripe_webhook(h)

    sentinel = output_root / ".users" / "uuid-marc-abc" / "subscription.json"
    data = json.loads(sentinel.read_text(encoding="utf-8"))
    assert data["status"] == "canceled"


def test_event_without_pebble_user_id_is_200_and_skipped(
    with_secret, output_root, verified_event,
):
    """Older subscriptions (or test-mode noise) without our metadata
    must NOT crash — return 200 so Stripe stops retrying, no write."""
    from pebble.server import stripe_webhook

    h = verified_event(_subscription_event(pebble_user_id=None))
    stripe_webhook.run_stripe_webhook(h)
    assert h.status == 200
    # No file created anywhere — there's no user to attribute it to.
    assert list(output_root.glob(".users/*/subscription.json")) == []


def test_unknown_event_type_is_200_and_skipped(
    with_secret, output_root, verified_event,
):
    """Stripe sends many event types; we only care about the four we
    subscribed to. Anything else → 200 + skip so we don't get retried."""
    from pebble.server import stripe_webhook

    h = verified_event({"id": "evt", "type": "charge.dispute.created", "data": {"object": {}}})
    stripe_webhook.run_stripe_webhook(h)
    assert h.status == 200
    assert list(output_root.glob(".users/*/subscription.json")) == []


# ---------- privacy regressions --------------------------------------------

def test_sentinel_never_contains_card_data(
    with_secret, output_root, verified_event,
):
    """Even if Stripe attaches a payment_method object with last4/etc to
    the event payload (real-world events do), our sentinel file must NOT
    contain it — we only persist the subscription state we need."""
    from pebble.server import stripe_webhook

    event = _subscription_event()
    event["data"]["object"]["default_payment_method"] = {
        "id": "pm_test",
        "card": {"last4": "4242", "brand": "visa", "exp_year": 2030, "exp_month": 12},
    }
    h = verified_event(event)
    stripe_webhook.run_stripe_webhook(h)

    sentinel = output_root / ".users" / "uuid-marc-abc" / "subscription.json"
    text = sentinel.read_text(encoding="utf-8")
    assert "4242" not in text
    assert "last4" not in text
    assert "pm_test" not in text
    assert "visa" not in text


def test_does_not_log_card_data(with_secret, output_root, verified_event, caplog):
    """Card data must NOT appear in engine logs at INFO+ either."""
    import logging
    from pebble.server import stripe_webhook

    event = _subscription_event()
    event["data"]["object"]["default_payment_method"] = {
        "card": {"last4": "4242", "brand": "visa"},
    }
    verified_event(event)
    caplog.set_level(logging.INFO, logger="pebble")
    stripe_webhook.run_stripe_webhook(FakeHandler({}))
    assert "4242" not in caplog.text


# ---- NLM round 1: race conditions / out-of-order delivery -----------------

def test_webhook_dedups_by_event_id(with_secret, output_root, verified_event):
    """Stripe retries deliver the SAME event.id when our 200 was lost in
    transit. Apply once, no-op the second time. Defends against both
    Stripe-side retries (legitimate) and replay attacks within the 5-min
    construct_event tolerance window (attacker who captured ciphertext)."""
    from pebble.server import stripe_webhook

    # First delivery
    h = verified_event(_subscription_event(
        event_id="evt_pinned", event_created=2_000_000,
        plan="starter", status="active",
    ))
    stripe_webhook.run_stripe_webhook(h)

    sentinel = output_root / ".users" / "uuid-marc-abc" / "subscription.json"
    first = json.loads(sentinel.read_text(encoding="utf-8"))

    # Same event.id again — Stripe's retry from a dropped ACK. The body
    # arrives byte-identical so the dedup must trigger before any
    # filesystem write.
    h = verified_event(_subscription_event(
        event_id="evt_pinned", event_created=2_000_000,
        plan="starter", status="active",
    ))
    stripe_webhook.run_stripe_webhook(h)

    second = json.loads(sentinel.read_text(encoding="utf-8"))
    # No rewrite — updated_at is exactly preserved.
    assert second["updated_at"] == first["updated_at"]


def test_webhook_rejects_out_of_order_events(with_secret, output_root, verified_event):
    """NLM Finding #1 — Stripe webhooks can arrive out of order. If a user
    cancels Starter then immediately buys Pro, the .deleted event for the
    old subscription might land AFTER the .created event for the new one.
    The OLDER event must NOT overwrite the newer state."""
    from pebble.server import stripe_webhook

    # Newer event lands first: Pro subscription created at t=2000
    h = verified_event(_subscription_event(
        event_type="customer.subscription.created",
        event_id="evt_new", event_created=2000,
        plan="pro", status="active", subscription_id="sub_pro_new",
    ))
    stripe_webhook.run_stripe_webhook(h)

    # Older event arrives second: Starter cancel at t=1000 (stale)
    h = verified_event(_subscription_event(
        event_type="customer.subscription.deleted",
        event_id="evt_old", event_created=1000,
        plan="starter", status="canceled", subscription_id="sub_starter_old",
    ))
    stripe_webhook.run_stripe_webhook(h)

    sentinel = output_root / ".users" / "uuid-marc-abc" / "subscription.json"
    data = json.loads(sentinel.read_text(encoding="utf-8"))
    # The stale "deleted" did NOT win — the Pro subscription remains active.
    assert data["plan"] == "pro"
    assert data["status"] == "active"
    assert data["stripe_subscription_id"] == "sub_pro_new"


def test_webhook_accepts_strictly_newer_events(with_secret, output_root, verified_event):
    """The dedup must NOT block legitimate in-order updates. Same sub_id,
    older event first, newer event second — newer should overwrite."""
    from pebble.server import stripe_webhook

    h = verified_event(_subscription_event(
        event_id="evt_a", event_created=1000,
        plan="starter", status="active", subscription_id="sub_same",
    ))
    stripe_webhook.run_stripe_webhook(h)

    h = verified_event(_subscription_event(
        event_type="customer.subscription.updated",
        event_id="evt_b", event_created=2000,
        plan="pro", status="active", subscription_id="sub_same",
    ))
    stripe_webhook.run_stripe_webhook(h)

    sentinel = output_root / ".users" / "uuid-marc-abc" / "subscription.json"
    data = json.loads(sentinel.read_text(encoding="utf-8"))
    assert data["plan"] == "pro"


def test_webhook_warns_on_non_whsec_secret(monkeypatch, caplog):
    """NLM round 3 R3.D1 — catch the misconfig where someone pastes an
    rk_test_ / sk_test_ / arbitrary token into STRIPE_WEBHOOK_SECRET
    instead of the whsec_ value from `stripe listen`. The HMAC verifier
    would 400 anyway, but a clearer log line saves debugging time.

    Note: pebble's root logger has ``propagate=False`` to avoid
    double-logging via the root handler, so caplog must attach DIRECTLY
    to the module's logger (``pebble.stripe_webhook``) to see WARN
    lines emitted from it.
    """
    import logging
    from pebble.server import stripe_webhook

    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "rk_test_pasted_by_mistake")
    # pebble's logger has propagate=False (see pebble/log.py) which blocks
    # caplog's root handler from seeing emitted records. Restore propagation
    # for this test only — monkeypatch auto-reverts at teardown.
    monkeypatch.setattr(logging.getLogger("pebble"), "propagate", True)
    caplog.set_level(logging.WARNING)

    h = FakeHandler({}, sig_header="t=1,v1=invalid")
    stripe_webhook.run_stripe_webhook(h)

    assert "whsec_" in caplog.text
    assert "rk_tes" in caplog.text  # first 6 chars of the wrong value


def test_webhook_does_not_warn_on_valid_whsec(monkeypatch, caplog):
    """The whsec_ prefix check must NOT fire when the secret is correctly
    formatted — keep the log signal-to-noise high."""
    import logging
    from pebble.server import stripe_webhook

    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_legitimate_test_value")
    # pebble's logger has propagate=False (see pebble/log.py) which blocks
    # caplog's root handler from seeing emitted records. Restore propagation
    # for this test only — monkeypatch auto-reverts at teardown.
    monkeypatch.setattr(logging.getLogger("pebble"), "propagate", True)
    caplog.set_level(logging.WARNING)

    h = FakeHandler({}, sig_header="t=1,v1=bad")
    stripe_webhook.run_stripe_webhook(h)

    assert "does not match expected 'whsec_'" not in caplog.text


def test_webhook_redacts_subscription_ids_in_multi_sub_log(
    with_secret, output_root, verified_event, caplog, monkeypatch,
):
    """NLM round 3 R3.C1 — full sub_xxx identifiers shouldn't appear in
    WARN logs; only the last 4 chars + the user_id (which an operator
    can look up in Stripe Dashboard if needed)."""
    import logging
    from pebble.server import stripe_webhook

    # First event establishes a subscription_id
    h = verified_event(_subscription_event(
        event_id="evt_one", event_created=1000,
        subscription_id="sub_legit_full_value_AAAA",
    ))
    stripe_webhook.run_stripe_webhook(h)

    # pebble's logger has propagate=False (see pebble/log.py) which blocks
    # caplog's root handler from seeing emitted records. Restore propagation
    # for this test only — monkeypatch auto-reverts at teardown.
    monkeypatch.setattr(logging.getLogger("pebble"), "propagate", True)
    caplog.set_level(logging.WARNING)
    caplog.clear()  # discard the INFO-level applied-event line above

    # Second event with a DIFFERENT sub_id — triggers the multi-sub WARN
    h = verified_event(_subscription_event(
        event_id="evt_two", event_created=2000,
        subscription_id="sub_other_full_value_BBBB",
    ))
    stripe_webhook.run_stripe_webhook(h)

    # The full IDs MUST NOT appear; only the last-4 redaction should.
    assert "sub_legit_full_value_AAAA" not in caplog.text
    assert "sub_other_full_value_BBBB" not in caplog.text
    # Last-4 markers should appear so an operator can correlate
    assert "AAAA" in caplog.text
    assert "BBBB" in caplog.text


def test_webhook_uses_unique_tmp_filenames(with_secret, output_root, verified_event, monkeypatch):
    """NLM round 2 Finding #R2.1 — pebble_engine runs on
    ThreadingHTTPServer, so two webhook calls for the same user can land
    in parallel. A fixed `subscription.json.tmp` would race; both threads
    open + truncate + write the same file, producing interleaved JSON
    garbage or FileNotFoundError on rename. Each write must use a unique
    tmp filename."""
    import os
    from pebble.server import stripe_webhook

    real_replace = os.replace
    tmp_sources: list[str] = []

    def spy_replace(src, dst):
        tmp_sources.append(str(src))
        return real_replace(src, dst)

    monkeypatch.setattr("pebble.server.stripe_webhook.os.replace", spy_replace)

    # Two distinct webhooks for the same user
    h = verified_event(_subscription_event(event_id="evt_a", event_created=1000))
    stripe_webhook.run_stripe_webhook(h)
    h = verified_event(_subscription_event(event_id="evt_b", event_created=2000))
    stripe_webhook.run_stripe_webhook(h)

    assert len(tmp_sources) == 2
    # Both must end in .tmp (still under the atomic-rename pattern)
    assert all(p.endswith(".tmp") for p in tmp_sources)
    # ...but must be DIFFERENT filenames so concurrent writers don't stomp.
    assert tmp_sources[0] != tmp_sources[1]


def test_webhook_writes_atomically(with_secret, output_root, verified_event, monkeypatch):
    """NLM Finding #4 — Path.write_text truncates before write. A reader
    racing the write sees an empty file -> JSONDecodeError -> 404 for a
    valid subscriber. Switch to tmp+os.replace so the destination file is
    never visible as a partial write."""
    import os
    from pebble.server import stripe_webhook

    h = verified_event(_subscription_event())

    # Capture the real os.replace BEFORE patching, so the spy can call
    # through without recursing into itself (monkeypatch on the module's
    # `os.replace` attribute mutates the shared os module).
    real_replace = os.replace
    seen: list[tuple[str, str]] = []

    def spy_replace(src, dst):
        seen.append((str(src), str(dst)))
        return real_replace(src, dst)

    monkeypatch.setattr("pebble.server.stripe_webhook.os.replace", spy_replace)
    stripe_webhook.run_stripe_webhook(h)

    # Confirm an atomic rename happened with a tmp file source.
    assert len(seen) >= 1, "expected an os.replace call from tmp -> subscription.json"
    src, dst = seen[-1]
    assert src.endswith(".tmp")
    assert dst.endswith("subscription.json")
