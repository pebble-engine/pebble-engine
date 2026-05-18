"""Pytest config — make the project root importable as `pebble_engine` and `style_dna`."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def _force_file_email_sender(monkeypatch):
    """Prevent tests from hitting the real Resend API.

    Forces FileSender regardless of PEBBLE_EMAIL_PROVIDER in .env so the test
    suite never sends real emails to test addresses like owner@example.com.
    """
    monkeypatch.setenv("PEBBLE_EMAIL_PROVIDER", "file")
