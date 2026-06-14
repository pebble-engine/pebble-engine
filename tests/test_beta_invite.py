"""Tests for beta invite gate."""
from __future__ import annotations

from pebble import beta_invite as bi


class _Hdr:
    def __init__(self, invite: str = ""):
        self.headers = {"X-Pebble-Invite": invite} if invite else {}


def test_disabled_allows_all(monkeypatch):
    monkeypatch.delenv("PEBBLE_BETA_INVITE_ONLY", raising=False)
    assert bi.check_build_allowed(_Hdr()) is None


def test_enabled_blocks_without_code(monkeypatch):
    monkeypatch.setenv("PEBBLE_BETA_INVITE_ONLY", "true")
    monkeypatch.setenv("PEBBLE_BETA_INVITE_CODES", "secret01")
    blocked = bi.check_build_allowed(_Hdr())
    assert blocked is not None
    assert blocked[0] == 403


def test_enabled_allows_valid_code(monkeypatch):
    monkeypatch.setenv("PEBBLE_BETA_INVITE_ONLY", "true")
    monkeypatch.setenv("PEBBLE_BETA_INVITE_CODES", "secret01,other")
    assert bi.check_build_allowed(_Hdr("SECRET01")) is None
