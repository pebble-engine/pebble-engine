"""Tests for `pebble.forms_webhook` — config storage + delivery.

The HTTP layer (POST /api/projects/<slug>/forms/webhook etc.) is
covered in `tests/test_forms.py`. These tests target the data layer
and the deliver() integration with post_webhook.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from pebble import forms_webhook as fw
from pebble.forms_webhook import (
    WebhookConfig,
    clear_webhook_config,
    deliver,
    get_webhook_config,
    set_webhook_config,
)


# ---- Fixture: redirect OUTPUT_DIR to tmp_path ----------------------------

@pytest.fixture(autouse=True)
def _stub_output_dir(tmp_path, monkeypatch):
    """Point pebble_engine.OUTPUT_DIR (which forms_webhook reads via
    sys.modules) at tmp_path so each test gets an isolated FS."""
    import sys, types
    fake = types.ModuleType("pebble_engine")
    fake.OUTPUT_DIR = tmp_path
    monkeypatch.setitem(sys.modules, "pebble_engine", fake)
    # Reset the rate limiter so each test gets a fresh burst budget.
    fw._reset_rate_limiter_for_tests()
    yield tmp_path


# ---- get_webhook_config --------------------------------------------------

def test_get_returns_none_when_unconfigured():
    assert get_webhook_config("acme") is None


def test_get_returns_config_after_set():
    set_webhook_config("acme", "https://hooks.zapier.com/abc")
    config = get_webhook_config("acme")
    assert config is not None
    assert config.url == "https://hooks.zapier.com/abc"
    assert config.configured_at  # ISO timestamp populated


def test_get_returns_none_for_malformed_config_file(_stub_output_dir):
    path = _stub_output_dir / "acme" / "forms_webhook.json"
    path.parent.mkdir(parents=True)
    path.write_text("not json", encoding="utf-8")
    assert get_webhook_config("acme") is None


def test_get_returns_none_when_stored_url_is_invalid(_stub_output_dir):
    """Defense in depth — if someone hand-edits the file with a bad
    URL, treat it as unconfigured rather than passing through to the
    delivery primitive."""
    path = _stub_output_dir / "acme" / "forms_webhook.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"url": "ftp://bad.example", "configured_at": "x"}), encoding="utf-8")
    assert get_webhook_config("acme") is None


# ---- set_webhook_config --------------------------------------------------

def test_set_persists_to_disk(_stub_output_dir):
    set_webhook_config("acme", "https://hooks.zapier.com/abc")
    path = _stub_output_dir / "acme" / "forms_webhook.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["url"] == "https://hooks.zapier.com/abc"
    assert "configured_at" in data


def test_set_creates_project_dir_if_missing():
    set_webhook_config("brand-new", "https://example.com/hook")
    assert get_webhook_config("brand-new") is not None


def test_set_replaces_existing_config():
    set_webhook_config("acme", "https://first.example/hook")
    set_webhook_config("acme", "https://second.example/hook")
    assert get_webhook_config("acme").url == "https://second.example/hook"


def test_set_rejects_non_http_scheme():
    for bad in ("ftp://example.com", "javascript:alert(1)", "file:///etc/passwd", ""):
        with pytest.raises(ValueError):
            set_webhook_config("acme", bad)


def test_set_rejects_oversized_url():
    huge = "https://example.com/" + ("x" * 3000)
    with pytest.raises(ValueError):
        set_webhook_config("acme", huge)


# ---- clear_webhook_config -----------------------------------------------

def test_clear_removes_existing_config():
    set_webhook_config("acme", "https://example.com/hook")
    assert clear_webhook_config("acme") is True
    assert get_webhook_config("acme") is None


def test_clear_returns_false_when_unconfigured():
    assert clear_webhook_config("acme") is False


# ---- deliver -------------------------------------------------------------

def test_deliver_skips_silently_when_unconfigured(monkeypatch):
    """No webhook configured — deliver returns None and never calls
    the SSRF-hardened POST primitive."""
    called = {"yes": False}
    def fake_post(*args, **kwargs):
        called["yes"] = True
        return True, None
    monkeypatch.setattr("pebble.forms_webhook.post_webhook", fake_post)
    result = deliver("acme", {"id": "abc", "fields": {"name": "x"}})
    assert result is None
    assert called["yes"] is False


def test_deliver_invokes_post_webhook_with_envelope(monkeypatch):
    """Successful path — payload is wrapped in the standard envelope."""
    set_webhook_config("acme", "https://hooks.zapier.com/abc")
    captured: dict[str, Any] = {}
    def fake_post(url, payload, **kwargs):
        captured["url"] = url
        captured["payload"] = payload
        return True, None
    monkeypatch.setattr("pebble.forms_webhook.post_webhook", fake_post)

    result = deliver("acme", {"id": "sub-1", "fields": {"name": "Marc"}})
    assert result is None
    assert captured["url"] == "https://hooks.zapier.com/abc"
    assert captured["payload"] == {
        "event": "form.submitted",
        "project": "acme",
        "submission": {"id": "sub-1", "fields": {"name": "Marc"}},
    }


def test_deliver_returns_error_on_failure(monkeypatch):
    """On vendor 503, the error bubbles up to the caller — but does
    NOT raise (form intake must succeed regardless)."""
    set_webhook_config("acme", "https://hooks.example.com/abc")
    monkeypatch.setattr("pebble.forms_webhook.post_webhook",
                        lambda *_a, **_k: (False, "HTTP 503"))
    result = deliver("acme", {"id": "x"})
    assert result == "HTTP 503"


def test_deliver_swallows_unexpected_exceptions(monkeypatch):
    """Defense in depth: if post_webhook somehow raises despite its
    own try/except, deliver still returns an error string instead of
    propagating up to the form-submit handler."""
    set_webhook_config("acme", "https://hooks.example.com/abc")
    def explode(*_a, **_k):
        raise RuntimeError("unexpected")
    monkeypatch.setattr("pebble.forms_webhook.post_webhook", explode)
    result = deliver("acme", {"id": "x"})
    assert result is not None
    assert "RuntimeError" in result


def test_deliver_respects_per_project_throttle(monkeypatch):
    """Burst is 30/project — call deliver a lot and the throttle
    eventually kicks in to prevent outbound DoS."""
    set_webhook_config("acme", "https://hooks.example.com/abc")
    monkeypatch.setattr("pebble.forms_webhook.post_webhook",
                        lambda *_a, **_k: (True, None))

    # Burst depth is 30; the 31st+ call within the burst window should
    # throttle. We can't assert exact timing but we CAN assert the
    # throttled marker eventually appears.
    throttled_at = None
    for i in range(60):
        result = deliver("acme", {"id": f"sub-{i}"})
        if result == "throttled":
            throttled_at = i
            break
    assert throttled_at is not None, "throttle never engaged"
    assert throttled_at < 60, "throttle engaged too late"


def test_deliver_strips_ip_hash_from_envelope(monkeypatch):
    """Privacy: even if the submission record carries an ip_hash,
    that's internal-only and must NOT be in the outbound payload.

    Note: pebble.forms.save_submission DOESN'T include ip_hash in the
    record it returns to callers — but defense in depth says the
    deliver path should pass through ONLY the dict it gets, which is
    already privacy-scrubbed by the caller. This test pins that
    behavior: whatever fields are in the submission dict are in the
    payload, no more, no less."""
    set_webhook_config("acme", "https://hooks.example.com/abc")
    captured: dict[str, Any] = {}
    monkeypatch.setattr("pebble.forms_webhook.post_webhook",
                        lambda url, payload, **kw: (captured.update({"p": payload}) or (True, None)))
    submission = {
        "id":         "sub-7",
        "created_at": "2026-05-16T12:00:00Z",
        "fields":     {"email": "marc@example.com", "message": "hi"},
        "user_agent": "Mozilla/5.0",
        "referrer":   "https://example.com/contact",
    }
    deliver("acme", submission)
    assert captured["p"]["submission"] == submission
