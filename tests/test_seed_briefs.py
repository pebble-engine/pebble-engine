"""Seed-brief library tests.

Pins the contract for `pebble.seed_briefs`: hand-curated reference briefs
per industry that the LLM sees as a STYLE/SPECIFICITY anchor in the build
prompt. NLM-prioritized as the highest-leverage first-build accuracy
lever (2026-05-19 adversarial review of the search-API proposal).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pebble.seed_briefs import (
    SEED_BRIEFS_PATH,
    build_seed_brief_block,
    get_seed_brief,
    list_seeded_industries,
    _clear_cache,
)


# ------------------------------------------------------------------ #
# JSON loads + schema                                                  #
# ------------------------------------------------------------------ #

def test_seed_briefs_json_exists():
    assert SEED_BRIEFS_PATH.exists(), f"seed_briefs.json missing at {SEED_BRIEFS_PATH}"


def test_seed_briefs_json_parses():
    raw = json.loads(SEED_BRIEFS_PATH.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)


def test_seed_briefs_has_meta():
    raw = json.loads(SEED_BRIEFS_PATH.read_text(encoding="utf-8"))
    assert "_meta" in raw, "_meta block missing — explain purpose for future editors"
    assert "purpose" in raw["_meta"]


def test_top_industries_have_seeds():
    """The 10 NLM-prioritized industries must have seed briefs."""
    required = {
        "plumbing",
        "wedding_photography",
        "coffee_shop",
        "law_firm",
        "yoga_studio",
        "auto_mechanic",
        "restaurant",
        "real_estate",
        "business_consultant",
        "barbershop",
    }
    seeded = set(list_seeded_industries())
    missing = required - seeded
    assert not missing, f"top industries missing seed briefs: {missing}"


REQUIRED_SEED_FIELDS = {
    "business_name",
    "business_type",
    "audience",
    "services_offered",
    "brand_position",
    "brand_tone",
    "trust_signals",
    "copy_voice_notes",
    "cta_hierarchy",
}


def test_every_seed_has_all_fields():
    for key in list_seeded_industries():
        seed = get_seed_brief(key)
        assert seed is not None
        missing = REQUIRED_SEED_FIELDS - seed.keys()
        assert not missing, f"seed {key!r} missing fields: {missing}"


def test_seed_fields_are_nonempty_strings():
    for key in list_seeded_industries():
        seed = get_seed_brief(key)
        for field in REQUIRED_SEED_FIELDS:
            val = seed.get(field)
            assert isinstance(val, str), f"{key}.{field} is not a string"
            assert val.strip(), f"{key}.{field} is empty"


# ------------------------------------------------------------------ #
# get_seed_brief                                                       #
# ------------------------------------------------------------------ #

def test_get_seed_brief_known_industry():
    seed = get_seed_brief("plumbing")
    assert seed is not None
    assert "Northridge" in seed["business_name"] or seed["business_name"]
    assert "plumbing" in seed["services_offered"].lower()


def test_get_seed_brief_unknown_returns_none():
    assert get_seed_brief("interdimensional_widget_polisher") is None


def test_get_seed_brief_empty_returns_none():
    assert get_seed_brief("") is None
    assert get_seed_brief(None) is None


def test_meta_key_not_returned_as_industry():
    """The _meta block must never show up in list_seeded_industries."""
    assert "_meta" not in list_seeded_industries()
    assert get_seed_brief("_meta") is None


# ------------------------------------------------------------------ #
# build_seed_brief_block                                               #
# ------------------------------------------------------------------ #

def test_block_contains_industry_label():
    seed = get_seed_brief("plumbing")
    block = build_seed_brief_block(seed, industry_key="plumbing")
    assert "plumbing" in block.lower()


def test_block_marks_reference_not_template():
    """The block must explicitly tell the LLM this is a REFERENCE for
    tone/style, not text to copy verbatim. Without this framing, the LLM
    will lift the reference business name + services into the user's site."""
    seed = get_seed_brief("plumbing")
    block = build_seed_brief_block(seed, industry_key="plumbing")
    lower = block.lower()
    assert "reference" in lower, (
        "block must frame the seed as REFERENCE — otherwise the LLM will copy it"
    )
    # The user's own brief must remain authoritative for facts
    assert "user's actual brief" in lower or "user's brief" in lower


def test_block_includes_all_seed_fields():
    seed = get_seed_brief("wedding_photography")
    block = build_seed_brief_block(seed, industry_key="wedding_photography")
    # Each required field's label should appear in the rendered block
    for label in ["Business name", "Audience", "Services", "Brand position",
                  "Brand tone", "Trust signals", "Copy voice notes", "CTA hierarchy"]:
        assert label in block, f"label {label!r} missing from rendered seed block"


def test_block_empty_seed_returns_empty_string():
    assert build_seed_brief_block({}) == ""
    assert build_seed_brief_block(None) == ""  # type: ignore[arg-type]


def test_block_does_not_leak_meta():
    """Even if a seed accidentally carries an internal field like
    `_internal_note`, the renderer should only emit the curated field
    list. Future-proofing the contract."""
    seed = {
        "business_name": "Acme",
        "business_type": "plumbing",
        "audience": "homeowners",
        "services_offered": "leaks",
        "brand_position": "trusted",
        "brand_tone": "warm",
        "trust_signals": "licensed",
        "copy_voice_notes": "clear",
        "cta_hierarchy": "call now",
        "_secret_internal_note": "DO NOT LEAK THIS TO THE LLM",
    }
    block = build_seed_brief_block(seed, industry_key="plumbing")
    assert "_secret_internal_note" not in block
    assert "DO NOT LEAK" not in block


# ------------------------------------------------------------------ #
# Cache + resilience                                                   #
# ------------------------------------------------------------------ #

def test_cache_clear_round_trip():
    _clear_cache()
    a = list_seeded_industries()
    b = list_seeded_industries()
    assert a == b


def test_missing_file_does_not_crash(monkeypatch, tmp_path):
    """If seed_briefs.json is missing, the loader must return empty
    rather than crashing the build pipeline."""
    fake_path = tmp_path / "definitely_not_there.json"
    monkeypatch.setattr("pebble.seed_briefs.SEED_BRIEFS_PATH", fake_path)
    _clear_cache()
    try:
        assert list_seeded_industries() == []
        assert get_seed_brief("plumbing") is None
    finally:
        # Restore real cache for downstream tests
        _clear_cache()


def test_malformed_json_does_not_crash(monkeypatch, tmp_path):
    """If seed_briefs.json is malformed, the loader must return empty
    rather than crashing the build pipeline."""
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    monkeypatch.setattr("pebble.seed_briefs.SEED_BRIEFS_PATH", bad)
    _clear_cache()
    try:
        assert list_seeded_industries() == []
    finally:
        _clear_cache()


# ------------------------------------------------------------------ #
# build_prompt integration                                             #
# ------------------------------------------------------------------ #

def test_build_prompt_injects_seed_when_industry_key_set():
    """When _industry_intel_key resolves to a seeded industry, the
    rendered prompt MUST contain the seed-brief block. Locks the wiring
    in pebble_engine.build_prompt."""
    import pebble_engine

    answers = {
        "business_name": "Bay Area Plumbing",
        "business_type": "Plumbing contractor",
        "audience": "locals",
        "site_functions": ["leads"],
        "brand_tone": "professional",
        "_industry_intel_key": "plumbing",
    }
    prompt = pebble_engine.build_prompt(answers, ds_text="", notes=[])
    assert "REFERENCE" in prompt, "seed brief block not present in rendered prompt"
    assert "plumbing" in prompt.lower()


def test_build_prompt_no_seed_when_industry_key_missing():
    """No seed = no block, no crash. The prompt should still render."""
    import pebble_engine

    answers = {
        "business_name": "Acme Widgets",
        "business_type": "widget manufacturer",
        "audience": "professionals",
        "site_functions": ["leads"],
        "brand_tone": "professional",
        # NO _industry_intel_key — unmatched industry
    }
    prompt = pebble_engine.build_prompt(answers, ds_text="", notes=[])
    # No reference block should be present
    assert "REFERENCE: how a great brief" not in prompt
