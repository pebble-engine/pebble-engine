"""Beta invite gate — optional closed beta (2026-06-12).

When ``PEBBLE_BETA_INVITE_ONLY=true``, full builds require header
``X-Pebble-Invite`` matching one of ``PEBBLE_BETA_INVITE_CODES`` (comma-separated).
"""
from __future__ import annotations

import os


def is_enabled() -> bool:
    return os.environ.get("PEBBLE_BETA_INVITE_ONLY", "").strip().lower() in {
        "1", "true", "yes", "on",
    }


def _allowed_codes() -> set[str]:
    raw = os.environ.get("PEBBLE_BETA_INVITE_CODES", "")
    return {c.strip().lower() for c in raw.split(",") if c.strip()}


def check_build_allowed(handler) -> tuple[int, dict] | None:
    """Return (status, body) when blocked; None when allowed."""
    if not is_enabled():
        return None
    codes = _allowed_codes()
    if not codes:
        return 503, {
            "error": "beta invite mode is on but no codes configured",
            "code":  "beta_misconfigured",
        }
    header = (handler.headers.get("X-Pebble-Invite") or "").strip().lower()
    if header and header in codes:
        return None
    return 403, {
        "error": "beta is invite-only — need a valid invite code",
        "code":  "beta_invite_required",
    }


__all__ = ["is_enabled", "check_build_allowed"]
