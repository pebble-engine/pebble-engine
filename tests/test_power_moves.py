"""P2 — curated 'power moves' (skills) registry + loader."""
from __future__ import annotations

from pebble import power_moves as pm


def test_lists_at_least_one_skill():
    assert any(s["id"] == "seo_check" for s in pm.list_skills())


def test_get_skill_returns_frontmatter_and_body():
    s = pm.get_skill("seo_check")
    assert s and s["label"] and s["description"]
    assert isinstance(s["triggers"], list) and s["triggers"]
    assert "instruction" in s and len(s["instruction"]) > 50
    assert isinstance(s["billable"], bool)


def test_get_unknown_returns_none():
    assert pm.get_skill("nope") is None


def test_match_skill_by_trigger_phrase():
    assert pm.match_skill("can you check my SEO please") is not None
    assert pm.match_skill("xyzzy nothing matches here") is None


def test_list_skills_is_ui_safe():
    # the list payload must NOT leak the full instruction body
    s = next(x for x in pm.list_skills() if x["id"] == "seo_check")
    assert "instruction" not in s
    assert {"id", "label", "description"} <= set(s)


def test_instructions_by_id_maps_id_to_body():
    m = pm.instructions_by_id()
    assert "seo_check" in m and "pebble-file" in m["seo_check"]


EXPECTED_SKILLS = {
    "seo_check", "make_it_accessible", "write_about_page",
    "holiday_sale", "refresh_look",
}


def test_all_five_launch_skills_load():
    ids = {s["id"] for s in pm.list_skills()}
    assert EXPECTED_SKILLS <= ids


def test_every_skill_ends_with_pebble_file_contract_and_has_triggers():
    for sid in EXPECTED_SKILLS:
        s = pm.get_skill(sid)
        assert s, f"missing skill {sid}"
        assert "pebble-file" in s["instruction"], f"{sid} missing output contract"
        assert s["triggers"], f"{sid} has no triggers"
        assert len(s["instruction"]) > 80, f"{sid} instruction too thin"
