"""Pytest config — make the project root importable as `pebble_engine` and `style_dna`."""
from __future__ import annotations
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# Sentry: prevent tests from firing real events to prod Sentry. The engine's
# init at pebble_engine.py:98 is gated on SENTRY_DSN being set, so unsetting
# it here BEFORE any test-side import of pebble_engine short-circuits init.
# Without this, log.error() calls in test paths (e.g. the monkeypatched
# `AdminError("boom")` in test_account_delete_cancels_stripe.py) reach
# Sentry as real errors — confirmed in the 2026-05-25 Sentry hunt where
# `scheduled deletion failed for [email]: boom` was an unresolved issue.
os.environ.pop("SENTRY_DSN", None)
os.environ.pop("PEBBLE_SENTRY_DSN", None)


@pytest.fixture(autouse=True)
def _force_file_email_sender(monkeypatch):
    """Prevent tests from hitting the real Resend API.

    Forces FileSender regardless of PEBBLE_EMAIL_PROVIDER in .env so the test
    suite never sends real emails to test addresses like owner@example.com.
    """
    monkeypatch.setenv("PEBBLE_EMAIL_PROVIDER", "file")
