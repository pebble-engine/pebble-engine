"""Tests for `pebble.forms_autoresponder` — config + dispatch.

HTTP endpoints are exercised in `tests/test_forms.py`. These tests
target the data layer and the `send_autoresponse` integration.
"""
from __future__ import annotations

import json
import sys
import types
from concurrent.futures import Future
from typing import Any

import pytest

from pebble import forms_autoresponder as ar


# ---- Fixture: redirect OUTPUT_DIR + reset rate limiter --------------------

@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    fake = types.ModuleType("pebble_engine")
    fake.OUTPUT_DIR = tmp_path
    monkeypatch.setitem(sys.modules, "pebble_engine", fake)
    ar._reset_rate_limiter_for_tests()
    # Phase 54a — Resend email forms are a Starter+ feature; the
    # autoresponder unit tests don't care about plan gating, they care
    # about the autoresponder ITSELF. Bypass the gate so they keep
    # testing the underlying logic. (The plan-gate behavior gets its
    # own dedicated test in test_forms.py.)
    from pebble import user_plan
    monkeypatch.setattr(user_plan, "project_has_feature", lambda slug, key: True)
    yield tmp_path


# ---- default_config / get_config -----------------------------------------

def test_default_config_is_disabled():
    c = ar.default_config()
    assert c.enabled is False
    assert c.subject == ar.DEFAULT_SUBJECT
    assert c.reply_field == "email"


def test_get_returns_default_when_unconfigured():
    c = ar.get_config("acme")
    assert c.enabled is False
    assert c.subject == ar.DEFAULT_SUBJECT


def test_get_returns_default_on_malformed_file(_isolate):
    path = _isolate / "acme" / "forms_autoresponder.json"
    path.parent.mkdir(parents=True)
    path.write_text("not json", encoding="utf-8")
    c = ar.get_config("acme")
    assert c.enabled is False


# ---- set_config ---------------------------------------------------------

def test_set_persists_minimum_config():
    ar.set_config("acme", enabled=True)
    c = ar.get_config("acme")
    assert c.enabled is True
    # Defaults kept for non-specified fields
    assert c.subject == ar.DEFAULT_SUBJECT
    assert c.body == ar.DEFAULT_BODY


def test_set_updates_subject_and_body():
    ar.set_config(
        "acme",
        enabled=True,
        subject="Thanks!",
        body="We got your message, {{ name }}.",
    )
    c = ar.get_config("acme")
    assert c.subject == "Thanks!"
    assert "{{ name }}" in c.body


def test_set_updates_reply_field():
    ar.set_config("acme", enabled=True, reply_field="contact_email")
    assert ar.get_config("acme").reply_field == "contact_email"


def test_set_rejects_oversized_subject():
    with pytest.raises(ValueError):
        ar.set_config("acme", enabled=True, subject="x" * 1000)


def test_set_rejects_oversized_body():
    with pytest.raises(ValueError):
        ar.set_config("acme", enabled=True, body="x" * 20_000)


def test_set_rejects_invalid_reply_field():
    with pytest.raises(ValueError):
        ar.set_config("acme", enabled=True, reply_field="not a valid identifier")


def test_set_preserves_subject_when_disabled():
    """Toggling enabled off shouldn't blow away the custom subject."""
    ar.set_config("acme", enabled=True, subject="Custom")
    ar.set_config("acme", enabled=False)  # only flips the bool
    assert ar.get_config("acme").subject == "Custom"


# ---- clear_config -------------------------------------------------------

def test_clear_removes():
    ar.set_config("acme", enabled=True)
    assert ar.clear_config("acme") is True
    assert ar.get_config("acme").enabled is False


def test_clear_returns_false_when_nothing_to_clear():
    assert ar.clear_config("acme") is False


# ---- _render placeholder substitution -----------------------------------

def test_render_substitutes_fields():
    out = ar._render("Hi {{ name }}, from {{ where }}", {"name": "Marc", "where": "Pebble"})
    assert out == "Hi Marc, from Pebble"


def test_render_unknown_placeholder_becomes_empty():
    out = ar._render("Hi {{ name }}, ref {{ refnum }}", {"name": "Marc"})
    assert out == "Hi Marc, ref "


def test_render_case_insensitive_fallback():
    """Forms often emit Title-Cased field names. The substitution
    should still find them when the template uses lowercase."""
    out = ar._render("Hi {{ name }}", {"Name": "Marc"})
    assert out == "Hi Marc"


def test_render_preserves_text_with_no_placeholders():
    out = ar._render("Plain text only", {"name": "X"})
    assert out == "Plain text only"


# ---- send_autoresponse: skip paths --------------------------------------

def test_send_skips_when_disabled(monkeypatch):
    """Default config has enabled=False — must not call the email API."""
    called = {"yes": False}
    def trip(*_a, **_kw):
        called["yes"] = True
        return Future()
    monkeypatch.setattr("pebble.forms_autoresponder.send_async", trip)
    err = ar.send_autoresponse("acme", {"fields": {"email": "x@example.com"}})
    assert err is None
    assert called["yes"] is False


def test_send_skips_when_no_email_field(monkeypatch):
    ar.set_config("acme", enabled=True)
    called = {"yes": False}
    monkeypatch.setattr("pebble.forms_autoresponder.send_async",
                        lambda *_a, **_k: called.update({"yes": True}) or Future())
    err = ar.send_autoresponse("acme", {"fields": {"name": "Marc"}})
    assert err is None
    assert called["yes"] is False


def test_send_skips_when_email_field_is_malformed(monkeypatch):
    ar.set_config("acme", enabled=True)
    called = {"yes": False}
    monkeypatch.setattr("pebble.forms_autoresponder.send_async",
                        lambda *_a, **_k: called.update({"yes": True}) or Future())
    err = ar.send_autoresponse("acme", {"fields": {"email": "not-an-email"}})
    assert err is None
    assert called["yes"] is False


def test_send_skips_when_fields_not_dict(monkeypatch):
    ar.set_config("acme", enabled=True)
    called = {"yes": False}
    monkeypatch.setattr("pebble.forms_autoresponder.send_async",
                        lambda *_a, **_k: called.update({"yes": True}) or Future())
    err = ar.send_autoresponse("acme", {"fields": "not-a-dict"})
    assert err is None
    assert called["yes"] is False


# ---- send_autoresponse: success path ------------------------------------

def test_send_uses_configured_subject_and_body(monkeypatch):
    ar.set_config("acme", enabled=True,
                  subject="Got your note, {{ name }}",
                  body="Hello {{ name }}!\n\nWe'll be in touch.")
    captured: dict[str, Any] = {}
    def fake_send(message, *_args, **_kw):
        captured["to"] = message.to
        captured["subject"] = message.subject
        captured["text"] = message.text
        return Future()
    monkeypatch.setattr("pebble.forms_autoresponder.send_async", fake_send)
    err = ar.send_autoresponse("acme", {
        "fields": {"name": "Marc", "email": "marc@example.com"},
    })
    assert err is None
    assert captured["to"] == "marc@example.com"
    assert captured["subject"] == "Got your note, Marc"
    assert "Hello Marc" in captured["text"]


def test_send_uses_custom_reply_field(monkeypatch):
    ar.set_config("acme", enabled=True, reply_field="contact_email")
    captured: dict[str, Any] = {}
    monkeypatch.setattr("pebble.forms_autoresponder.send_async",
                        lambda m, *_a, **_k: captured.update({"to": m.to}) or Future())
    ar.send_autoresponse("acme", {
        "fields": {"name": "Marc", "contact_email": "marc@example.com"},
    })
    assert captured["to"] == "marc@example.com"


def test_send_respects_per_recipient_throttle(monkeypatch):
    """Same recipient within the cooldown window → throttled."""
    ar.set_config("acme", enabled=True)
    monkeypatch.setattr("pebble.forms_autoresponder.send_async",
                        lambda *_a, **_k: Future())
    # First send: ok
    err1 = ar.send_autoresponse("acme", {"fields": {"email": "spam@example.com"}})
    assert err1 is None
    # Second send within the window: throttled
    err2 = ar.send_autoresponse("acme", {"fields": {"email": "spam@example.com"}})
    assert err2 == "throttled"
    # Different recipient: NOT throttled (per-address budget)
    err3 = ar.send_autoresponse("acme", {"fields": {"email": "other@example.com"}})
    assert err3 is None


def test_send_swallows_email_errors(monkeypatch):
    """If EmailMessage construction raises, we return the error string
    and never propagate up to the form submit handler."""
    from pebble.email import EmailError
    ar.set_config("acme", enabled=True, subject="")  # empty subject after render
    def explode(*_a, **_kw):
        raise EmailError("subject required")
    monkeypatch.setattr("pebble.forms_autoresponder.send_async", explode)
    err = ar.send_autoresponse("acme", {"fields": {"email": "x@example.com"}})
    # EmailMessage with empty rendered subject raises BEFORE send_async,
    # but the construction itself uses DEFAULT_SUBJECT fallback. Test
    # the explicit send_async raise instead.
    # Re-test with a config that DOES reach send_async:
    ar.set_config("acme", enabled=True, subject="Hi")
    err = ar.send_autoresponse("acme", {"fields": {"email": "y@example.com"}})
    assert err is not None
    assert "EmailError" in err or "subject" in err.lower()


def test_send_falls_back_to_default_when_subject_renders_empty(monkeypatch):
    """If the subject template renders to an empty string (all unknown
    placeholders), use DEFAULT_SUBJECT so we don't fail EmailMessage's
    validation."""
    ar.set_config("acme", enabled=True, subject="{{ missing_field }}")
    captured: dict[str, Any] = {}
    monkeypatch.setattr("pebble.forms_autoresponder.send_async",
                        lambda m, *_a, **_k: captured.update({"subject": m.subject}) or Future())
    err = ar.send_autoresponse("acme", {"fields": {"email": "z@example.com"}})
    assert err is None
    assert captured["subject"] == ar.DEFAULT_SUBJECT


# ---- NLM round on Tracks 4–7: spam-cannon + HTML-escape fixes -----------

def test_render_strips_html_from_field_values():
    """Visitor-submitted HTML tags must not survive into the email
    body. Owner's template structure stays as-is; only the values
    pulled from form fields get scrubbed."""
    out = ar._render(
        "Thanks for the message, {{ name }}!",
        {"name": "<script>alert(1)</script>Bob<b>X</b>"},
    )
    # The script tag is gone; the surrounding text remains.
    assert "<script>" not in out
    assert "<b>" not in out
    assert "Bob" in out
    # Owner's literal "!" is preserved.
    assert out == "Thanks for the message, alert(1)BobX!"


def test_render_preserves_owner_template_structure():
    """The HTML strip only applies to substituted values, not to the
    template body the OWNER wrote (owner is the trust boundary)."""
    out = ar._render(
        "Owner has <strong>{{ name }}</strong> here",
        {"name": "Bob"},
    )
    # Owner's <strong> tag preserved; substitution is bare.
    assert "<strong>" in out
    assert "Bob" in out


def test_send_respects_per_project_daily_cap(monkeypatch):
    """Spam-cannon protection: the per-recipient throttle won't stop a
    bot that uses many different victim addresses. The per-project cap
    bounds total outbound regardless of recipient diversity.

    Burst is 50 — submit 60 different recipients and the project cap
    should fire on at least one (in practice many)."""
    ar.set_config("acme", enabled=True)
    monkeypatch.setattr("pebble.forms_autoresponder.send_async",
                        lambda *_a, **_k: Future())

    throttled = 0
    for i in range(60):
        err = ar.send_autoresponse(
            "acme",
            {"fields": {"email": f"victim{i}@example.com"}},
        )
        if err == "throttled-project":
            throttled += 1
    assert throttled > 0, "per-project cap never fired"
    # Reasonable margin — we don't want flaky timing tests, just
    # confirm the cap engages well before exhausting the 60 inputs.
    assert throttled >= 5


def test_per_project_cap_does_not_affect_other_projects(monkeypatch):
    """Project A burning its cap MUST NOT affect Project B."""
    ar.set_config("acme", enabled=True)
    ar.set_config("widgets", enabled=True)
    monkeypatch.setattr("pebble.forms_autoresponder.send_async",
                        lambda *_a, **_k: Future())

    # Burn most of acme's burst budget.
    for i in range(55):
        ar.send_autoresponse("acme", {"fields": {"email": f"u{i}@example.com"}})

    # widgets should still be able to send.
    err = ar.send_autoresponse("widgets", {"fields": {"email": "first@example.com"}})
    assert err is None, f"widgets project unfairly throttled: {err}"
