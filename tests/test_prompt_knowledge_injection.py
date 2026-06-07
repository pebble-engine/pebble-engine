"""P1 Task 2 — business knowledge is injected into the full build prompt."""
from __future__ import annotations

import pebble_engine as pe


def test_template_has_knowledge_slot():
    assert "{knowledge_block}" in pe.PROMPT_TEMPLATE


def test_build_prompt_injects_knowledge():
    out = pe.build_prompt(
        {"industry": "pest control"}, "", [],
        knowledge_block="OWNER SAYS: closed Sundays.",
    )
    assert "closed Sundays" in out


def test_build_prompt_blank_knowledge_renders_clean():
    out = pe.build_prompt({"industry": "pest control"}, "", [])
    # placeholder must be consumed by .format even when empty
    assert "{knowledge_block}" not in out


def test_template_has_brand_kit_slot():
    assert "{brand_kit_block}" in pe.PROMPT_TEMPLATE


def test_build_prompt_injects_brand_kit():
    out = pe.build_prompt(
        {"industry": "pest control"}, "", [],
        brand_kit_block="BRAND: primary #1F6FEB",
    )
    assert "#1F6FEB" in out
    assert "{brand_kit_block}" not in pe.build_prompt({"industry": "x"}, "", [])
