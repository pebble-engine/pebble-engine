"""Tests for the Pebble Plan generator.

The Plan is the user-facing "here's what I'll build" summary the UI
shows between the questionnaire and the actual generation. These tests
nail down the schema so the UI can rely on its shape, and verify the
three real-world data sources (brief, industry intel, DNA) flow through
to the right Plan fields.
"""
from __future__ import annotations

import json

import pytest

from pebble.plan import PLAN_SCHEMA_VERSION, build_pebble_plan


def _minimal_brief() -> dict:
    return {
        "business_name": "Corpus HVAC",
        "business_type": "hvac",
    }


def _hvac_intel() -> dict:
    """Mirror of the industries.json hvac entry — kept inline so the test
    doesn't depend on industries.json staying byte-for-byte stable."""
    return {
        "emotion":       "comfort, urgency, trust",
        "visual_style":  "clean professional, technical-but-friendly",
        "hero_type":     "video",
        "tone":          "urgent, reassuring, expert",
        "key_sections":  ["hero", "emergency_service", "services", "financing", "maintenance_plans", "reviews"],
        "trust_signals": ["24/7 emergency", "NATE certified", "EPA certified"],
        "colors":        {"primary": "#1E40AF", "accent": "#DC2626", "background": "#FFFFFF"},
        "pages":         ["service_area", "guarantee", "pricing"],
    }


def _sample_dna() -> dict:
    return {
        "id":           "swiss_magazine",
        "label":        "Swiss Magazine",
        "posture":      "editorial, restrained",
        "display_font": "Inter Display",
        "body_font":    "Inter",
    }


# ---------- Schema ---------------------------------------------------------

def test_schema_version_is_1_0():
    plan = build_pebble_plan(_minimal_brief())
    assert plan["schema_version"] == PLAN_SCHEMA_VERSION == "1.0"


def test_plan_has_all_seven_fields_plus_meta():
    plan = build_pebble_plan(_minimal_brief())
    expected = {"schema_version", "audience", "goal", "pages", "features",
                "style", "setup_needs", "next_steps", "language", "meta"}
    assert set(plan.keys()) == expected


def test_plan_includes_language_block_with_html_lang():
    """The Plan must expose the target language so the UI can show
    'Site will be in: Español' before generation."""
    plan = build_pebble_plan(_minimal_brief())
    assert plan["language"]["code"] == "en"
    assert plan["language"]["html_lang"] == "en"


def test_plan_picks_up_explicit_language_override():
    brief = _minimal_brief()
    brief["_language"] = "es"
    plan = build_pebble_plan(brief)
    assert plan["language"]["code"] == "es"
    assert plan["language"]["native_name"] == "Español"


def test_plan_is_json_serializable():
    plan = build_pebble_plan(_minimal_brief(), _hvac_intel(), _sample_dna())
    # Will raise if any value isn't JSON-serializable.
    json.dumps(plan)


# ---------- Pages ----------------------------------------------------------

def test_foundation_pages_always_present():
    plan = build_pebble_plan(_minimal_brief())
    ids = [p["id"] for p in plan["pages"]]
    for required in ("homepage", "services", "about", "contact"):
        assert required in ids


def test_foundation_pages_marked_foundation_true():
    plan = build_pebble_plan(_minimal_brief())
    foundations = [p for p in plan["pages"] if p["foundation"]]
    assert {p["id"] for p in foundations} == {"homepage", "services", "about", "contact"}


def test_universal_extras_always_present():
    plan = build_pebble_plan(_minimal_brief())
    ids = [p["id"] for p in plan["pages"]]
    for ext in ("faq", "privacy", "terms"):
        assert ext in ids


def test_industry_pages_included_when_industry_intel_present():
    plan = build_pebble_plan(_minimal_brief(), _hvac_intel())
    ids = [p["id"] for p in plan["pages"]]
    for ip in ("service_area", "guarantee", "pricing"):
        assert ip in ids


def test_no_industry_intel_yields_seven_pages():
    """4 foundation + 3 universal extras = 7."""
    plan = build_pebble_plan(_minimal_brief())
    assert len(plan["pages"]) == 7


def test_hvac_intel_yields_ten_pages():
    """4 foundation + 3 universal + 3 industry (service_area, guarantee, pricing)."""
    plan = build_pebble_plan(_minimal_brief(), _hvac_intel())
    assert len(plan["pages"]) == 10


# ---------- Audience -------------------------------------------------------

def test_explicit_audience_in_brief_wins():
    brief = {**_minimal_brief(), "audience": "Homeowners 35-65 in Brooklyn"}
    plan = build_pebble_plan(brief)
    assert plan["audience"] == "Homeowners 35-65 in Brooklyn"


def test_audience_falls_back_to_industry_tone_when_brief_silent():
    plan = build_pebble_plan(_minimal_brief(), _hvac_intel())
    assert "comfort" in plan["audience"].lower() or "urgent" in plan["audience"].lower()


def test_audience_safe_when_no_intel_and_no_brief_field():
    plan = build_pebble_plan(_minimal_brief())
    assert isinstance(plan["audience"], str)
    assert plan["audience"]  # non-empty


# ---------- Goal -----------------------------------------------------------

def test_goal_derives_from_site_functions():
    brief = {**_minimal_brief(), "site_functions": ["booking", "leads"]}
    plan = build_pebble_plan(brief)
    assert "book" in plan["goal"].lower()
    assert "lead" in plan["goal"].lower() or "contact" in plan["goal"].lower()


def test_goal_has_safe_default_when_no_site_functions():
    plan = build_pebble_plan(_minimal_brief())
    assert plan["goal"]
    assert "presence" in plan["goal"].lower() or "convert" in plan["goal"].lower()


# ---------- Features -------------------------------------------------------

def test_features_include_brief_site_functions():
    brief = {**_minimal_brief(), "site_functions": ["booking", "ecommerce"]}
    plan = build_pebble_plan(brief)
    ids = {f["id"] for f in plan["features"]}
    assert "booking" in ids
    assert "ecommerce" in ids


def test_features_include_industry_key_sections():
    plan = build_pebble_plan(_minimal_brief(), _hvac_intel())
    ids = {f["id"] for f in plan["features"]}
    assert "emergency_service" in ids
    assert "financing" in ids


def test_features_always_include_contact_form_universal():
    plan = build_pebble_plan(_minimal_brief())
    ids = {f["id"] for f in plan["features"]}
    assert "contact_form" in ids


def test_features_have_source_tag():
    plan = build_pebble_plan(_minimal_brief(), _hvac_intel())
    for f in plan["features"]:
        assert f["source"] in ("brief", "industry", "universal")


# ---------- Style ----------------------------------------------------------

def test_style_uses_dna_when_provided():
    plan = build_pebble_plan(_minimal_brief(), _hvac_intel(), _sample_dna())
    assert plan["style"]["dna_id"] == "swiss_magazine"
    assert plan["style"]["label"] == "Swiss Magazine"
    assert plan["style"]["fonts"]["display"] == "Inter Display"


def test_style_falls_back_when_no_dna():
    plan = build_pebble_plan(_minimal_brief(), _hvac_intel())
    assert plan["style"]["dna_id"] is None
    assert plan["style"]["label"]  # still has a friendly label


def test_style_palette_pulled_from_industry_intel():
    plan = build_pebble_plan(_minimal_brief(), _hvac_intel())
    assert plan["style"]["palette"]["primary"] == "#1E40AF"
    assert plan["style"]["palette"]["accent"] == "#DC2626"


# ---------- Setup needs ----------------------------------------------------

def test_setup_needs_has_all_fourteen_items():
    plan = build_pebble_plan(_minimal_brief())
    assert len(plan["setup_needs"]) == 14


def test_setup_needs_statuses_are_honest():
    """Every entry has a status — and no entry is marked 'auto' unless
    the infra is actually wired today. If you flip something to 'auto'
    in the future, update this set to keep the contract explicit."""
    plan = build_pebble_plan(_minimal_brief())
    by_id = {item["id"]: item["status"] for item in plan["setup_needs"]}
    # Things that ARE wired today:
    assert by_id["project_name"]   == "auto"
    assert by_id["pages"]          == "auto"
    assert by_id["forms"]          == "auto"
    assert by_id["seo_basics"]     == "auto"
    assert by_id["accessibility"]  == "auto"
    # Things that are NOT yet wired — must NOT be "auto":
    for not_yet in ("website_address", "hosting", "business_email",
                    "booking", "payments", "analytics",
                    "language_region", "publish"):
        assert by_id[not_yet] != "auto", f"{not_yet} marked auto without infra"


# ---------- Meta -----------------------------------------------------------

def test_meta_captures_business_name_and_industry_key():
    brief = {**_minimal_brief(), "_industry_intel_key": "hvac"}
    plan = build_pebble_plan(brief, _hvac_intel())
    assert plan["meta"]["business_name"] == "Corpus HVAC"
    assert plan["meta"]["industry_key"] == "hvac"


def test_meta_has_iso_timestamp():
    plan = build_pebble_plan(_minimal_brief())
    # Will raise if not parseable as ISO.
    from datetime import datetime
    datetime.fromisoformat(plan["meta"]["generated_at"])


# ---------- Next steps -----------------------------------------------------

def test_next_steps_has_at_least_three():
    plan = build_pebble_plan(_minimal_brief())
    assert len(plan["next_steps"]) >= 3


def test_next_steps_warns_when_phone_missing():
    plan = build_pebble_plan(_minimal_brief())
    assert any("phone" in s.lower() for s in plan["next_steps"])


def test_next_steps_does_not_warn_when_phone_present():
    brief = {**_minimal_brief(), "phone": "(212) 555-0100"}
    plan = build_pebble_plan(brief)
    assert not any("phone" in s.lower() for s in plan["next_steps"])
