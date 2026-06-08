"""Engine glue for the Fly fleet preview: source collection + endpoint auth."""
from __future__ import annotations

import pytest

from pebble.server import fleet_preview as fp


class FakeHandler:
    def __init__(self):
        self.status = None
        self.json_body = None
    def _json(self, status, payload):
        self.status = status
        self.json_body = payload


def test_collect_source_includes_bridge(tmp_path, monkeypatch):
    out = tmp_path / "output"
    (out / "s1" / "site" / "app").mkdir(parents=True)
    (out / "s1" / "site" / "app" / "page.tsx").write_text("export default ()=>null", encoding="utf-8")
    monkeypatch.setattr(fp, "_output_dir", lambda: out)
    files = fp.collect_source_with_bridge("s1")
    names = {f["file"] for f in files}
    assert "app/page.tsx" in names
    assert ".pebble-bridge.js" in names  # receiver injects this into HTML


def test_kick_preview_noop_when_disabled(monkeypatch):
    monkeypatch.delenv("PEBBLE_PREVIEW_BACKEND", raising=False)
    # Should not raise and should not spawn anything meaningful.
    fp.kick_preview("s1")  # no exception = pass


def test_preview_url_requires_owner(monkeypatch):
    monkeypatch.setattr(fp, "require_project_owner", lambda h, slug: None)  # unauthorized
    h = FakeHandler()
    fp.run_get_preview_url(h, "s1")
    assert h.status is None  # require_project_owner wrote its own response


def test_preview_url_reports_disabled(monkeypatch):
    monkeypatch.setattr(fp, "require_project_owner", lambda h, slug: "u1")
    monkeypatch.setattr(fp, "fleet_enabled", lambda: False)
    h = FakeHandler()
    fp.run_get_preview_url(h, "s1")
    assert h.status == 200
    assert h.json_body == {"enabled": False}


def test_preview_url_no_machine_yet(monkeypatch):
    monkeypatch.setattr(fp, "require_project_owner", lambda h, slug: "u1")
    monkeypatch.setattr(fp, "fleet_enabled", lambda: True)
    from pebble import fly_fleet
    monkeypatch.setattr(fly_fleet, "_load_registry", lambda: {})
    h = FakeHandler()
    fp.run_get_preview_url(h, "s1")
    assert h.status == 200
    assert h.json_body["enabled"] is True and h.json_body["ready"] is False
