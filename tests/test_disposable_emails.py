"""Tests for the disposable-email blocklist (2026-05-24)."""
from __future__ import annotations

import pytest

from pebble.disposable_emails import is_disposable, DISPOSABLE_DOMAINS


# ── Happy path ──────────────────────────────────────────────────── #


def test_blocks_known_disposable_domain():
    assert is_disposable("alice@mailinator.com") is True
    assert is_disposable("test@10minutemail.com") is True
    assert is_disposable("anyone@yopmail.com") is True


def test_allows_legit_provider():
    assert is_disposable("alice@gmail.com") is False
    assert is_disposable("bob@yahoo.com") is False
    assert is_disposable("ceo@apple.com") is False


def test_case_insensitive():
    assert is_disposable("Alice@MAILINATOR.com") is True
    assert is_disposable("alice@MailInAtoR.com") is True


def test_subdomain_match_via_suffix():
    """Throwaway services often rotate subdomains
    (foo.mailinator.com, bar.mailinator.com). The parent suffix
    match catches them without us having to enumerate every
    rotation."""
    assert is_disposable("alice@whatever.mailinator.com") is True
    assert is_disposable("test@one.two.10minutemail.com") is True


# ── Safe defaults on garbage input ─────────────────────────────── #


def test_non_string_returns_false():
    # Defensive — bad input shouldn't raise, just return False
    # so the auth path can continue and surface a normal validation
    # error elsewhere.
    assert is_disposable(None) is False  # type: ignore[arg-type]
    assert is_disposable(42) is False    # type: ignore[arg-type]
    assert is_disposable([]) is False    # type: ignore[arg-type]


def test_malformed_email_returns_false():
    assert is_disposable("") is False
    assert is_disposable("no_at_sign_here") is False
    assert is_disposable("trailing@") is False
    assert is_disposable("@leading.com") is False


# ── Blocklist sanity ────────────────────────────────────────────── #


def test_blocklist_is_lowercase():
    """All entries should be lowercase or the case-insensitive match
    would silently miss them."""
    for d in DISPOSABLE_DOMAINS:
        assert d == d.lower(), f"non-lowercase entry: {d}"


def test_blocklist_has_no_leading_at_or_dot():
    """Entries should be bare domains — no leading '@' or '.'."""
    for d in DISPOSABLE_DOMAINS:
        assert not d.startswith("@"), d
        assert not d.startswith("."), d


def test_blocklist_covers_major_providers():
    """Smoke test that at least the obvious top providers are present.
    If someone deletes one accidentally, this catches it."""
    must_have = {"mailinator.com", "10minutemail.com", "guerrillamail.com",
                 "yopmail.com", "tempmail.net", "throwawaymail.com"}
    for d in must_have:
        assert d in DISPOSABLE_DOMAINS, d
