"""Community stats templates_count falls back to engine registry."""
from __future__ import annotations

import httpx

from pebble import community_stats as cs


def test_templates_count_uses_registry_when_public_templates_empty(monkeypatch):
    monkeypatch.setattr(cs, "is_configured", lambda: True)
    monkeypatch.setattr(cs, "_read_existing_row", lambda: {"templates_count": 0})
    monkeypatch.setattr(cs, "_count_users", lambda: 5)
    monkeypatch.setattr(
        cs,
        "_count_rows",
        lambda table, filters: 0 if table == "public_templates" else 2,
    )

    captured: dict = {}

    class _Resp:
        status_code = 200

        def json(self):
            return [captured]

    def fake_post(url, **kw):
        captured.update(kw.get("json") or {})
        return _Resp()

    monkeypatch.setattr(httpx, "post", fake_post)
    row = cs.refresh_stats()
    assert row is not None
    assert row["templates_count"] == 39
