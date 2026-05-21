"""Smart-defaults endpoint tests (Phase 39a, 2026-05-21).

Pins the two-tier fallback chain:
  Tier 1: industries.json hints → chip ids (free, deterministic)
  Tier 2: gpt-4o-mini fallback   (mocked here)
  Tier 3: SAFE_FALLBACK shell    (used when both fail)

Plus request validation, taxonomy whitelisting (the endpoint must NEVER
return chip ids outside the v3 idea-phase enumerations), and graceful
LLM-failure paths.
"""
from __future__ import annotations

import io
import json
from unittest.mock import patch

import pytest

from pebble.server import smart_defaults as endpoint_module
from pebble.server.smart_defaults import (
    SAFE_FALLBACK,
    VALID_AUDIENCE,
    VALID_BRAND_TONE,
    VALID_SITE_FUNCTIONS,
    _audience_from_industry,
    _parse_llm_json,
    _site_functions_from_industry_intel,
    _tone_from_industry_intel,
    _try_industries_json,
    _whitelist_list,
)


class _StubHandler:
    """Mirrors the bot_message + brand_extract endpoint test pattern."""
    def __init__(self, body: bytes, content_length: int | None = None):
        self.headers = {"Content-Length": str(content_length if content_length is not None else len(body))}
        self.rfile = io.BytesIO(body)
        self.client_address = ("127.0.0.1", 12345)
        self.response: tuple[int, dict] | None = None
        self.path = "/api/smart-defaults"
        self.command = "POST"

    def _json(self, status: int, payload: dict) -> None:
        self.response = (status, payload)


@pytest.fixture(autouse=True)
def _reset_rate_limit():
    from pebble.security import plan_limiter
    try:
        plan_limiter._calls.clear()  # type: ignore[attr-defined]
    except Exception:
        pass
    yield


# ------------------------------------------------------------------ #
# Taxonomy invariants                                                  #
# ------------------------------------------------------------------ #


def test_valid_audience_matches_v3_idea_phase():
    assert VALID_AUDIENCE == {"locals", "travelers", "professionals", "families", "enthusiasts", "other"}


def test_valid_site_functions_matches_v3_idea_phase():
    assert VALID_SITE_FUNCTIONS == {"presence", "leads", "booking", "ecommerce", "portfolio", "payment"}


def test_valid_brand_tone_matches_v3_idea_phase():
    assert VALID_BRAND_TONE == {"warm", "professional", "bold", "calm", "playful", "premium"}


def test_safe_fallback_has_required_keys_and_marks_fallback():
    expected = {"audience", "site_functions", "brand_tone", "source", "fallback"}
    assert set(SAFE_FALLBACK.keys()) == expected
    assert SAFE_FALLBACK["fallback"] is True
    assert SAFE_FALLBACK["source"] == "fallback"
    assert SAFE_FALLBACK["brand_tone"] in VALID_BRAND_TONE


# ------------------------------------------------------------------ #
# Tier 1 helpers — industries.json mapping                            #
# ------------------------------------------------------------------ #


class TestToneMapping:
    def test_warm_tone_phrase_maps_to_warm_chip(self):
        assert _tone_from_industry_intel("warm, welcoming, local") == "warm"

    def test_premium_overrides_professional(self):
        # "premium" should outrank "professional" per the priority list
        assert _tone_from_industry_intel("premium, professional") == "premium"

    def test_playful_wins_when_present(self):
        assert _tone_from_industry_intel("playful, fun, energetic") == "playful"

    def test_bold_for_cinematic_industries(self):
        assert _tone_from_industry_intel("bold, dramatic, cinematic") == "bold"

    def test_calm_for_editorial(self):
        assert _tone_from_industry_intel("quiet, considered, editorial") == "calm"

    def test_professional_as_last_resort(self):
        assert _tone_from_industry_intel("polished, authoritative") == "professional"

    def test_empty_returns_none(self):
        assert _tone_from_industry_intel("") is None
        assert _tone_from_industry_intel("foo bar baz") is None


class TestSectionMapping:
    def test_booking_section_maps_to_booking_chip(self):
        result = _site_functions_from_industry_intel(["booking", "services"])
        assert "booking" in result

    def test_gallery_section_maps_to_portfolio_chip(self):
        result = _site_functions_from_industry_intel(["hero", "gallery", "contact"])
        assert "portfolio" in result

    def test_about_section_maps_to_presence(self):
        result = _site_functions_from_industry_intel(["hero", "about", "team"])
        assert "presence" in result

    def test_ecommerce_keyword_priority(self):
        result = _site_functions_from_industry_intel(["shop", "products", "checkout"])
        assert "ecommerce" in result

    def test_empty_sections_defaults_to_presence_and_leads(self):
        assert set(_site_functions_from_industry_intel([])) == {"presence", "leads"}

    def test_non_list_input_returns_empty_safe_default(self):
        assert _site_functions_from_industry_intel(None) == []  # type: ignore[arg-type]

    def test_caps_at_4_picks(self):
        # Provide sections that match every category
        many = ["shop", "booking", "gallery", "donate", "contact", "about"]
        result = _site_functions_from_industry_intel(many)
        assert len(result) <= 4


class TestAudienceMapping:
    def test_daycare_keyword_maps_to_families(self):
        assert _audience_from_industry("daycare", {}) == ["families"]

    def test_law_firm_maps_to_professionals(self):
        assert _audience_from_industry("law_firm", {}) == ["professionals"]

    def test_hotel_maps_to_travelers(self):
        assert _audience_from_industry("boutique_hotel", {}) == ["travelers"]

    def test_yoga_studio_maps_to_enthusiasts(self):
        assert _audience_from_industry("yoga_studio", {}) == ["enthusiasts"]

    def test_bakery_maps_to_locals(self):
        assert _audience_from_industry("bakery", {}) == ["locals"]

    def test_unknown_industry_defaults_to_locals(self):
        assert _audience_from_industry("xyz_widget", {}) == ["locals"]


class TestTryIndustriesJson:
    def test_known_industry_returns_chip_ids(self):
        # bakery is a curated entry in industries.json
        result = _try_industries_json("bakery", "")
        assert result is not None
        assert result["source"] == "industries_json"
        assert result["fallback"] is False
        # All ids must be inside the v3 taxonomy
        for a in result["audience"]:
            assert a in VALID_AUDIENCE
        for sf in result["site_functions"]:
            assert sf in VALID_SITE_FUNCTIONS
        assert result["brand_tone"] in VALID_BRAND_TONE

    def test_empty_inputs_returns_none(self):
        assert _try_industries_json("", "") is None

    def test_falsy_inputs_returns_none(self):
        assert _try_industries_json("   ", "   ") is None


# ------------------------------------------------------------------ #
# _whitelist_list                                                      #
# ------------------------------------------------------------------ #


class TestWhitelistList:
    def test_filters_to_allowed_set(self):
        out = _whitelist_list(["locals", "aliens", "professionals"], VALID_AUDIENCE, default=["other"])
        assert "aliens" not in out
        assert "locals" in out
        assert "professionals" in out

    def test_case_insensitive(self):
        out = _whitelist_list(["LOCALS", "Professionals"], VALID_AUDIENCE, default=["other"])
        assert "locals" in out
        assert "professionals" in out

    def test_dedupes(self):
        out = _whitelist_list(["locals", "locals", "locals"], VALID_AUDIENCE, default=["other"])
        assert out == ["locals"]

    def test_non_list_returns_default(self):
        assert _whitelist_list("not a list", VALID_AUDIENCE, default=["locals"]) == ["locals"]

    def test_all_invalid_returns_default(self):
        assert _whitelist_list(["aliens", "robots"], VALID_AUDIENCE, default=["other"]) == ["other"]


# ------------------------------------------------------------------ #
# LLM JSON parser                                                     #
# ------------------------------------------------------------------ #


class TestParseLlmJson:
    def test_valid_response_parses(self):
        raw = '{"audience": ["locals"], "site_functions": ["presence", "leads"], "brand_tone": "warm"}'
        parsed = _parse_llm_json(raw)
        assert parsed is not None
        assert parsed["audience"] == ["locals"]
        assert parsed["site_functions"] == ["presence", "leads"]
        assert parsed["brand_tone"] == "warm"
        assert parsed["source"] == "llm"
        assert parsed["fallback"] is False

    def test_strips_code_fences(self):
        raw = '```json\n{"audience": ["locals"], "site_functions": ["presence"], "brand_tone": "warm"}\n```'
        parsed = _parse_llm_json(raw)
        assert parsed is not None
        assert parsed["brand_tone"] == "warm"

    def test_tolerates_leading_prose(self):
        raw = 'Here you go:\n\n{"audience": ["professionals"], "site_functions": ["leads"], "brand_tone": "professional"}'
        parsed = _parse_llm_json(raw)
        assert parsed is not None
        assert parsed["audience"] == ["professionals"]

    def test_invented_audience_id_dropped(self):
        raw = '{"audience": ["aliens"], "site_functions": ["presence"], "brand_tone": "warm"}'
        parsed = _parse_llm_json(raw)
        assert parsed is not None
        # "aliens" is invented — falls back to the safe default
        assert parsed["audience"] == ["locals"]

    def test_invented_brand_tone_falls_back_to_professional(self):
        raw = '{"audience": ["locals"], "site_functions": ["presence"], "brand_tone": "mystical"}'
        parsed = _parse_llm_json(raw)
        assert parsed is not None
        assert parsed["brand_tone"] == "professional"

    def test_caps_audience_at_2(self):
        raw = '{"audience": ["locals","travelers","professionals","families","enthusiasts"], "site_functions": ["presence"], "brand_tone": "warm"}'
        parsed = _parse_llm_json(raw)
        assert parsed is not None
        assert len(parsed["audience"]) == 2

    def test_caps_site_functions_at_4(self):
        raw = '{"audience": ["locals"], "site_functions": ["presence","leads","booking","ecommerce","portfolio","payment"], "brand_tone": "warm"}'
        parsed = _parse_llm_json(raw)
        assert parsed is not None
        assert len(parsed["site_functions"]) == 4

    def test_garbage_returns_none(self):
        assert _parse_llm_json("not json") is None
        assert _parse_llm_json("") is None
        assert _parse_llm_json("{broken") is None


# ------------------------------------------------------------------ #
# Endpoint — request validation                                       #
# ------------------------------------------------------------------ #


def test_missing_body_returns_400():
    h = _StubHandler(b"", content_length=0)
    endpoint_module.run_smart_defaults(h)
    assert h.response[0] == 400


def test_oversized_body_returns_400():
    huge = b'{"industry":"' + (b"x" * 5000) + b'"}'
    h = _StubHandler(huge)
    endpoint_module.run_smart_defaults(h)
    assert h.response[0] == 400


def test_invalid_json_returns_400():
    h = _StubHandler(b"{not valid json")
    endpoint_module.run_smart_defaults(h)
    assert h.response[0] == 400


def test_non_object_body_returns_400():
    h = _StubHandler(b'"just a string"')
    endpoint_module.run_smart_defaults(h)
    assert h.response[0] == 400


def test_no_industry_or_business_type_returns_400():
    h = _StubHandler(b'{"business_name":"Joe"}')
    endpoint_module.run_smart_defaults(h)
    status, payload = h.response
    assert status == 400
    assert "industry" in payload["error"].lower()


# ------------------------------------------------------------------ #
# Endpoint — tier dispatching                                         #
# ------------------------------------------------------------------ #


def test_tier1_industries_json_match_returns_200():
    """Known industry — should be served from industries.json without
    hitting the LLM."""
    h = _StubHandler(b'{"industry":"bakery"}')
    with patch.object(endpoint_module, "_call_llm", side_effect=AssertionError("LLM should not be called for tier 1 hit")):
        endpoint_module.run_smart_defaults(h)
    status, payload = h.response
    assert status == 200
    assert payload["source"] == "industries_json"


def test_tier2_llm_fallback_when_tier1_misses():
    """Unknown industry — tier 1 misses, LLM tier 2 succeeds."""
    h = _StubHandler(b'{"industry":"holographic_widgets"}')
    llm_response = {
        "audience": ["professionals"], "site_functions": ["leads"],
        "brand_tone": "bold", "source": "llm", "fallback": False,
    }
    with patch.object(endpoint_module, "_try_industries_json", return_value=None):
        with patch.object(endpoint_module, "_call_llm", return_value=llm_response):
            endpoint_module.run_smart_defaults(h)
    status, payload = h.response
    assert status == 200
    assert payload["source"] == "llm"
    assert payload["brand_tone"] == "bold"


def test_safe_fallback_when_both_tiers_fail():
    """Both layers fail — caller still gets a usable 200 with fallback=true."""
    h = _StubHandler(b'{"industry":"holographic_widgets"}')
    with patch.object(endpoint_module, "_try_industries_json", return_value=None):
        with patch.object(endpoint_module, "_call_llm", return_value=None):
            endpoint_module.run_smart_defaults(h)
    status, payload = h.response
    assert status == 200
    assert payload["source"] == "fallback"
    assert payload["fallback"] is True
    # Even the fallback must obey the taxonomy
    for a in payload["audience"]:
        assert a in VALID_AUDIENCE
    for sf in payload["site_functions"]:
        assert sf in VALID_SITE_FUNCTIONS
    assert payload["brand_tone"] in VALID_BRAND_TONE


def test_business_type_alone_is_enough_to_dispatch():
    """A user who provided only business_type (no separate industry) still
    gets a response."""
    h = _StubHandler(b'{"business_type":"law_firm"}')
    endpoint_module.run_smart_defaults(h)
    status, _ = h.response
    assert status == 200
