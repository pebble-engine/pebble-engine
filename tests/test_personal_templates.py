"""P4 — per-account "save a finished site as a personal template" store."""
from __future__ import annotations

import pytest

from pebble import personal_templates as pt


def _make_site(root, *, with_content_ts=True, extra_junk=True):
    """Create a fake project site/ dir under root and return it."""
    site = root / "site"
    (site / "app").mkdir(parents=True)
    (site / "app" / "page.tsx").write_text("export default function Page(){return null}", encoding="utf-8")
    (site / "package.json").write_text('{"name":"x"}', encoding="utf-8")
    if with_content_ts:
        (site / "content").mkdir()
        (site / "content" / "site.ts").write_text("export const NAME = 'X'", encoding="utf-8")
    if extra_junk:
        (site / "node_modules" / "dep").mkdir(parents=True)
        (site / "node_modules" / "dep" / "index.js").write_text("//junk", encoding="utf-8")
        (site / ".next").mkdir()
        (site / ".next" / "build.json").write_text("{}", encoding="utf-8")
    return site


def test_save_copies_files_and_returns_entry(tmp_path):
    out = tmp_path / "output"; out.mkdir()
    site = _make_site(tmp_path / "proj")
    entry = pt.save_personal_template(out, "u1", site, "My Cool Site")
    assert entry["label"] == "My Cool Site"
    assert entry["id"]
    assert entry["has_content_ts"] is True
    assert entry["file_count"] >= 3
    # copied files exist, junk excluded
    dst = pt.template_site_dir(out, "u1", entry["id"])
    assert (dst / "app" / "page.tsx").exists()
    assert (dst / "content" / "site.ts").exists()
    assert not (dst / "node_modules").exists()
    assert not (dst / ".next").exists()


def test_has_content_ts_false_when_absent(tmp_path):
    out = tmp_path / "output"; out.mkdir()
    site = _make_site(tmp_path / "proj", with_content_ts=False)
    entry = pt.save_personal_template(out, "u1", site, "Generated Site")
    assert entry["has_content_ts"] is False


def test_id_is_slugified_and_collision_suffixed(tmp_path):
    out = tmp_path / "output"; out.mkdir()
    s1 = _make_site(tmp_path / "a"); s2 = _make_site(tmp_path / "b")
    e1 = pt.save_personal_template(out, "u1", s1, "Same Name!")
    e2 = pt.save_personal_template(out, "u1", s2, "Same Name!")
    assert e1["id"] == "same-name"
    assert e2["id"] == "same-name-2"


def test_list_get_delete(tmp_path):
    out = tmp_path / "output"; out.mkdir()
    site = _make_site(tmp_path / "proj")
    entry = pt.save_personal_template(out, "u1", site, "Alpha")
    assert [t["id"] for t in pt.list_personal_templates(out, "u1")] == [entry["id"]]
    assert pt.get_personal_template(out, "u1", entry["id"])["label"] == "Alpha"
    assert pt.get_personal_template(out, "u1", "nope") is None
    assert pt.delete_personal_template(out, "u1", entry["id"]) is True
    assert pt.list_personal_templates(out, "u1") == []
    assert not pt.template_site_dir(out, "u1", entry["id"]).exists()
    assert pt.delete_personal_template(out, "u1", entry["id"]) is False


def test_list_empty_for_unknown_user(tmp_path):
    out = tmp_path / "output"; out.mkdir()
    assert pt.list_personal_templates(out, "ghost") == []


def test_blank_label_rejected(tmp_path):
    out = tmp_path / "output"; out.mkdir()
    site = _make_site(tmp_path / "proj")
    with pytest.raises(ValueError):
        pt.save_personal_template(out, "u1", site, "   ")


def test_label_capped(tmp_path):
    out = tmp_path / "output"; out.mkdir()
    site = _make_site(tmp_path / "proj")
    entry = pt.save_personal_template(out, "u1", site, "z" * 500)
    assert len(entry["label"]) <= pt.MAX_LABEL


def test_users_isolated(tmp_path):
    out = tmp_path / "output"; out.mkdir()
    s1 = _make_site(tmp_path / "a"); s2 = _make_site(tmp_path / "b")
    pt.save_personal_template(out, "u1", s1, "Mine")
    pt.save_personal_template(out, "u2", s2, "Theirs")
    assert [t["label"] for t in pt.list_personal_templates(out, "u1")] == ["Mine"]
    assert [t["label"] for t in pt.list_personal_templates(out, "u2")] == ["Theirs"]
