"""Tests for the shared MFA step-up guard in pebble.security.

The guard implements STEP-UP auth: it only requires AAL2 when the user
has a *verified* MFA factor enrolled. Users who never enrolled MFA have
AAL1 as their maximum assurance, so gating them on AAL2 would lock them
out entirely — the guard must let them pass. See the senior-dev brief
2026-06-01 + the existing per-endpoint guard in pebble/server/account.py.
"""
from pebble.security import require_aal2_if_mfa_enrolled


class FakeHandler:
    def __init__(self):
        self.status = None
        self.json_body = None

    def _json(self, status, payload):
        self.status = status
        self.json_body = payload


def _user(factors=None):
    return {"id": "u1", "email": "a@b.co", "factors": factors or []}


def test_no_mfa_factors_allows_aal1(monkeypatch):
    """A user with no enrolled MFA factor passes regardless of AAL."""
    monkeypatch.setattr("pebble.security.get_aal", lambda t: "aal1")
    h = FakeHandler()
    assert require_aal2_if_mfa_enrolled(h, "tok", _user(factors=[])) is True
    assert h.status is None  # no error written


def test_enrolled_mfa_with_aal2_allows(monkeypatch):
    monkeypatch.setattr("pebble.security.get_aal", lambda t: "aal2")
    h = FakeHandler()
    user = _user(factors=[{"status": "verified", "factor_type": "totp"}])
    assert require_aal2_if_mfa_enrolled(h, "tok", user) is True
    assert h.status is None


def test_enrolled_mfa_with_aal1_rejects_401(monkeypatch):
    """Stolen AAL1 token must not reach the route when MFA is enrolled."""
    monkeypatch.setattr("pebble.security.get_aal", lambda t: "aal1")
    h = FakeHandler()
    user = _user(factors=[{"status": "verified", "factor_type": "totp"}])
    assert require_aal2_if_mfa_enrolled(h, "tok", user) is False
    assert h.status == 401
    assert h.json_body.get("aal_required") == "aal2"


def test_unverified_factor_does_not_trigger_stepup(monkeypatch):
    """An unverified (pending-enrollment) factor must NOT lock out aal1."""
    monkeypatch.setattr("pebble.security.get_aal", lambda t: "aal1")
    h = FakeHandler()
    user = _user(factors=[{"status": "unverified", "factor_type": "totp"}])
    assert require_aal2_if_mfa_enrolled(h, "tok", user) is True
    assert h.status is None


def test_missing_factors_key_allows(monkeypatch):
    """A user dict with no 'factors' key at all is treated as no-MFA."""
    monkeypatch.setattr("pebble.security.get_aal", lambda t: "aal1")
    h = FakeHandler()
    assert require_aal2_if_mfa_enrolled(h, "tok", {"id": "u1"}) is True
    assert h.status is None
