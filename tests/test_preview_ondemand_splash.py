"""Preview on-demand splash: must auto-refresh in BOTH starting and failed
states so a transient warmup failure recovers without a manual reload."""
from __future__ import annotations

import re

from pebble.server import preview_ondemand as od


def _refresh_seconds(html: str):
    m = re.search(r'http-equiv="refresh"\s+content="(\d+)"', html)
    return int(m.group(1)) if m else None


def test_starting_splash_auto_refreshes():
    html = od.render_splash_html("some-slug", "starting")
    assert _refresh_seconds(html) is not None
    assert "Starting preview" in html


def test_failed_splash_still_auto_refreshes():
    """Regression: a failed splash used to have NO refresh meta, leaving the
    user on a dead screen even though the warmup recovers after the cooldown."""
    html = od.render_splash_html("some-slug", "failed")
    secs = _refresh_seconds(html)
    assert secs is not None, "failed splash must auto-refresh to recover"
    # Refresh must outlast the failure cooldown so the next load respawns.
    assert secs >= od._FAILURE_TTL_SEC, (
        f"failed-refresh {secs}s should be >= cooldown {od._FAILURE_TTL_SEC}s "
        "so the auto-reload actually re-triggers a warmup"
    )


def test_failed_splash_signals_retry_to_user():
    html = od.render_splash_html("some-slug", "failed")
    assert "etry" in html  # "Retrying" / "retry" — user knows it's not dead
