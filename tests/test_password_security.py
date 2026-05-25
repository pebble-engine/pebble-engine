"""Tests for pebble.password_security — HIBP k-anonymity password check.

Strategy: monkeypatch `pebble.password_security._fetch_range` so no real
network call ever happens. Tests assert the right hash math + the right
fail-OPEN behavior.
"""
from __future__ import annotations

import hashlib

import pytest

from pebble import password_security


# Real SHA-1 of "password" — used to verify the prefix/suffix math is right
# without ever hitting the network.
PASSWORD_SHA1 = hashlib.sha1(b"password").hexdigest().upper()
PASSWORD_PREFIX = PASSWORD_SHA1[:5]   # "5BAA6"
PASSWORD_SUFFIX = PASSWORD_SHA1[5:]   # "1E4C9B93F3F0682250B6CF8331B7EE68FD8"


def test_known_pwned_password_returns_count(monkeypatch):
    """When HIBP returns a body that contains our suffix + count, we
    return the count as an int."""
    body = f"{PASSWORD_SUFFIX}:9876543\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:7\n"

    captured = {}
    def fake_fetch(prefix):
        captured["prefix"] = prefix
        return body
    monkeypatch.setattr(password_security, "_fetch_range", fake_fetch)

    result = password_security.check_pwned("password")
    assert result == 9876543
    # Confirm only the prefix was sent — the suffix stayed local
    assert captured["prefix"] == PASSWORD_PREFIX


def test_clean_password_returns_zero(monkeypatch):
    """When HIBP returns a body that does NOT contain our suffix, return 0."""
    body = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:7\nBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB:2\n"
    monkeypatch.setattr(password_security, "_fetch_range", lambda p: body)

    result = password_security.check_pwned("a-very-unique-passphrase-that-cannot-collide")
    assert result == 0


def test_hibp_outage_returns_none_fail_open(monkeypatch):
    """When HIBP fetch returns None (timeout / network error), we return
    None so the caller can fail-OPEN and accept the password."""
    monkeypatch.setattr(password_security, "_fetch_range", lambda p: None)

    result = password_security.check_pwned("anything")
    assert result is None


def test_empty_password_returns_zero_without_fetching(monkeypatch):
    """Empty-string short-circuit — never call HIBP. Caller handles the
    real min-length check elsewhere."""
    fetched = []
    monkeypatch.setattr(
        password_security,
        "_fetch_range",
        lambda p: fetched.append(p) or "",
    )

    result = password_security.check_pwned("")
    assert result == 0
    assert fetched == []  # never reached the HIBP call


def test_case_insensitive_suffix_match(monkeypatch):
    """HIBP returns uppercase hex; our suffix is uppercase. But if HIBP
    ever changed format, the comparison should still be case-insensitive."""
    body = f"{PASSWORD_SUFFIX.lower()}:12\n"
    monkeypatch.setattr(password_security, "_fetch_range", lambda p: body)

    result = password_security.check_pwned("password")
    assert result == 12


def test_malformed_count_does_not_raise(monkeypatch):
    """If HIBP returns our suffix but the count column is corrupted,
    return 1 (conservative reject) rather than crash."""
    body = f"{PASSWORD_SUFFIX}:not-a-number\n"
    monkeypatch.setattr(password_security, "_fetch_range", lambda p: body)

    result = password_security.check_pwned("password")
    assert result == 1


def test_blank_lines_and_padding_ignored(monkeypatch):
    """HIBP's Add-Padding header response can include padding lines.
    These should be skipped without crashing."""
    body = (
        "\n"
        "\n"
        f"{PASSWORD_SUFFIX}:5\n"
        "\n"
        "AAA\n"   # malformed line without colon — should be skipped
        "\n"
    )
    monkeypatch.setattr(password_security, "_fetch_range", lambda p: body)

    result = password_security.check_pwned("password")
    assert result == 5
