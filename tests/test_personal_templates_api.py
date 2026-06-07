"""P4 — /api/account/templates endpoints (list/save/use/delete)."""
from __future__ import annotations

import json
from io import BytesIO

import pytest

from pebble.server import personal_templates_api as api
from pebble import personal_templates as pt


class FakeHandler:
    def __init__(self, body=None):
        raw = json.dumps(body).encode("utf-8") if body is not None else b""
        self.rfile = BytesIO(raw)
        self.headers = {"Content-Length": str(len(raw))}
        self.status = None
        self.json_body = None

    def _json(self, status, payload):
        self.status = status
        self.json_body = payload


def _make_project(out, slug, *, with_content_ts=True):
    site = out / slug / "site"
    (site / "app").mkdir(parents=True)
    (site / "app" / "page.tsx").write_text("export default ()=>null", encoding="utf-8")
    if with_content_ts:
        (site / "content").mkdir()
        (site / "content" / "site.ts").write_text("export const NAME='X'", encoding="utf-8")
    return site


@pytest.fixture
def env(tmp_path, monkeypatch):
    out = tmp_path / "output"; out.mkdir()
    monkeypatch.setattr(api, "_output_dir", lambda: out)
    monkeypatch.setattr(api, "resolve_user_id", lambda h: "u1")
    # require_project_owner: succeed as u1 for any existing slug
    monkeypatch.setattr(api, "require_project_owner", lambda h, slug: "u1")
    return out


def test_list_unauthed_401(env, monkeypatch):
    monkeypatch.setattr(api, "resolve_user_id", lambda h: None)
    h = FakeHandler()
    api.run_list_personal_templates(h)
    assert h.status == 401


def test_save_unauthed_401(env, monkeypatch):
    monkeypatch.setattr(api, "require_project_owner", lambda h, slug: (h._json(401, {"error": "x"}), None)[1])
    h = FakeHandler({"slug": "acme", "label": "Acme"})
    api.run_save_personal_template(h)
    assert h.status == 401


def test_save_happy_then_list(env):
    _make_project(env, "acme")
    h = FakeHandler({"slug": "acme", "label": "Acme Co"})
    api.run_save_personal_template(h)
    assert h.status == 200
    assert h.json_body["template"]["label"] == "Acme Co"
    # now list shows it
    lh = FakeHandler()
    api.run_list_personal_templates(lh)
    assert lh.status == 200
    assert [t["label"] for t in lh.json_body["templates"]] == ["Acme Co"]


def test_save_blank_label_400(env):
    _make_project(env, "acme")
    h = FakeHandler({"slug": "acme", "label": "  "})
    api.run_save_personal_template(h)
    assert h.status == 400


def test_save_missing_site_404(env):
    # project dir without site/
    (env / "empty").mkdir()
    h = FakeHandler({"slug": "empty", "label": "Empty"})
    api.run_save_personal_template(h)
    assert h.status == 404


def test_use_unknown_id_404(env):
    h = FakeHandler({"brief": {"business_name": "New Biz"}})
    api.run_use_personal_template(h, "ghost")
    assert h.status == 404


def test_use_unauthed_401(env, monkeypatch):
    monkeypatch.setattr(api, "resolve_user_id", lambda h: None)
    h = FakeHandler({"brief": {"business_name": "x"}})
    api.run_use_personal_template(h, "anything")
    assert h.status == 401


def test_use_plain_clone_happy_path(env, monkeypatch):
    """A saved template without content/site.ts → plain clone into a new slug,
    swap skipped, brief + build_meta stamped, owned by caller."""
    # Save a generated-style project (no content/site.ts).
    _make_project(env, "src-proj", with_content_ts=False)
    save = FakeHandler({"slug": "src-proj", "label": "Source"})
    api.run_save_personal_template(save)
    tid = save.json_body["template"]["id"]

    # Stub the engine surface the use path needs.
    class _PE:
        _slugify = staticmethod(lambda s: (s or "untitled").lower().replace(" ", "-"))
    monkeypatch.setattr(api, "_engine", lambda: _PE())

    h = FakeHandler({"brief": {"business_name": "New Biz"}})
    api.run_use_personal_template(h, tid)
    assert h.status == 200
    assert h.json_body["ok"] is True
    assert h.json_body["swap_ok"] is False  # no content/site.ts → swap skipped
    slug = h.json_body["slug"]
    # Cloned files + stamps exist; new project owned by caller.
    assert (env / slug / "site" / "app" / "page.tsx").exists()
    brief = json.loads((env / slug / "brief.json").read_text(encoding="utf-8"))
    assert brief["_user_id"] == "u1"
    assert brief["_personal_template_id"] == tid
    assert (env / slug / "build_meta.json").exists()


def test_delete(env):
    _make_project(env, "acme")
    save = FakeHandler({"slug": "acme", "label": "Acme"})
    api.run_save_personal_template(save)
    tid = save.json_body["template"]["id"]
    dh = FakeHandler()
    api.run_delete_personal_template(dh, tid)
    assert dh.status == 200
    assert pt.list_personal_templates(env, "u1") == []


def test_delete_unauthed_401(env, monkeypatch):
    monkeypatch.setattr(api, "resolve_user_id", lambda h: None)
    h = FakeHandler()
    api.run_delete_personal_template(h, "x")
    assert h.status == 401
