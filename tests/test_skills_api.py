"""P2 T4 — GET /api/skills (public list for the Power moves UI)."""
from __future__ import annotations

from pebble.server import skills_api


class FakeHandler:
    def __init__(self):
        self.status = None
        self.json_body = None

    def _json(self, status, payload):
        self.status = status
        self.json_body = payload


def test_list_skills_returns_the_launch_skills():
    h = FakeHandler()
    skills_api.run_list_skills(h)
    assert h.status == 200
    skills = h.json_body["skills"]
    ids = {s["id"] for s in skills}
    assert {"seo_check", "make_it_accessible", "write_about_page",
            "holiday_sale", "refresh_look"} <= ids


def test_list_skills_is_ui_safe_no_instructions():
    h = FakeHandler()
    skills_api.run_list_skills(h)
    for s in h.json_body["skills"]:
        assert "instruction" not in s
        assert s["label"] and "description" in s
