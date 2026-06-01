"""Tests for the shared MFA step-up guard in pebble.security.

The guard implements STEP-UP auth: it only requires AAL2 when the user
has a *verified* MFA factor enrolled. Users who never enrolled MFA have
AAL1 as their maximum assurance, so gating them on AAL2 would lock them
out entirely — the guard must let them pass. See the senior-dev brief
2026-06-01 + the existing per-endpoint guard in pebble/server/account.py.
"""
from pebble.security import require_aal2_if_mfa_enrolled, enforce_step_up


class FakeHandler:
    def __init__(self, headers=None):
        self.headers = headers or {}
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


# ---- enforce_step_up (the drop-in wrapper) — fail-open semantics ----------

def test_enforce_step_up_no_bearer_allows():
    """No Authorization header (cookie/anon) → allow; ownership gate stands."""
    h = FakeHandler(headers={})
    assert enforce_step_up(h) is True
    assert h.status is None


def test_enforce_step_up_auth_unconfigured_allows(monkeypatch):
    """Supabase not configured (e.g. test env) → fail open, no behavior change."""
    import pebble.auth_admin as aa
    monkeypatch.setattr(aa, "is_configured", lambda: False)
    h = FakeHandler(headers={"Authorization": "Bearer sometoken"})
    assert enforce_step_up(h) is True
    assert h.status is None


def test_enforce_step_up_blocks_enrolled_aal1(monkeypatch):
    """Validated AAL1 token from an MFA-enrolled user → 401 (the attack)."""
    import pebble.auth_admin as aa
    monkeypatch.setattr(aa, "is_configured", lambda: True)
    monkeypatch.setattr(
        aa, "validate_access_token",
        lambda tok, **kw: {"id": "u1", "factors": [{"status": "verified"}]},
    )
    monkeypatch.setattr("pebble.security.get_aal", lambda t: "aal1")
    h = FakeHandler(headers={"Authorization": "Bearer sometoken"})
    assert enforce_step_up(h) is False
    assert h.status == 401
    assert h.json_body.get("aal_required") == "aal2"


def test_enforce_step_up_allows_enrolled_aal2(monkeypatch):
    import pebble.auth_admin as aa
    monkeypatch.setattr(aa, "is_configured", lambda: True)
    monkeypatch.setattr(
        aa, "validate_access_token",
        lambda tok, **kw: {"id": "u1", "factors": [{"status": "verified"}]},
    )
    monkeypatch.setattr("pebble.security.get_aal", lambda t: "aal2")
    h = FakeHandler(headers={"Authorization": "Bearer sometoken"})
    assert enforce_step_up(h) is True
    assert h.status is None


def test_enforce_step_up_validation_error_fails_open(monkeypatch):
    """If GoTrue validation raises, don't block — ownership gate already ran."""
    import pebble.auth_admin as aa
    monkeypatch.setattr(aa, "is_configured", lambda: True)
    def _boom(tok, **kw):
        raise aa.AdminError("unreachable")
    monkeypatch.setattr(aa, "validate_access_token", _boom)
    h = FakeHandler(headers={"Authorization": "Bearer sometoken"})
    assert enforce_step_up(h) is True
    assert h.status is None
