"""Pins the COPYWRITING CRAFT guidance in the full engine-build prompt
template (2026-06-06).

Background: a hands-on competitive eval of Lovable found the one dimension
where Lovable beat Pebble was COPY — its sites had value-prop headlines,
memorable guarantees, and real expertise signals, while Pebble's read
competent-but-generic. The prompt template now includes positive
copy-craft direction, kept explicitly subordinate to the anti-slop rules
so we get voice WITHOUT inventing facts. This test pins that guidance so a
future edit can't silently delete it, and confirms the str.format render
still works (a stray single brace would crash every build).
"""
from __future__ import annotations

from pathlib import Path

import pytest


PROMPT_PATH = Path(__file__).resolve().parents[1] / "skills" / "prompt_template.md"


@pytest.fixture(scope="module")
def prompt_body() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def test_template_has_copywriting_craft_section(prompt_body):
    assert "COPYWRITING CRAFT" in prompt_body


def test_craft_pushes_value_prop_headline(prompt_body):
    assert "value proposition" in prompt_body.lower()
    # the canonical example we want the LLM to emulate
    assert "respects your home" in prompt_body


def test_craft_pushes_guarantee_and_benefit_voice(prompt_body):
    low = prompt_body.lower()
    assert "guarantee" in low or "promise" in low
    assert "benefit-first" in low
    assert "expertise" in low or "real methods" in low


def test_craft_is_subordinate_to_anti_slop(prompt_body):
    # The craft block must explicitly defer to anti-slop so the LLM never
    # invents facts in the name of voice.
    assert "NEVER override the ANTI-SLOP" in prompt_body


def test_template_still_renders_via_str_format():
    """A stray single brace in the craft addition would make every build
    crash at PROMPT_TEMPLATE.format(...). Render with all expected keys."""
    import pebble_engine as pe

    keys = [
        "business_name", "business_type", "audience", "location",
        "services_offered", "phone", "email", "address", "visitor_action",
        "booking_system", "industry_intel_block", "pages_block",
        "resolved_contract", "reference_block", "design_reference_block",
        "extra_context", "url_extraction_block", "intent_block",
        "no_slop_block", "ios_skill_block", "stack_block",
        "business_intelligence_block", "industry_research_block",
        "design_system_block", "images_block", "anti_slop_block",
        "knowledge_block", "brand_kit_block",
        "universal_design_block", "design_craft_block", "uiux_mobile_block",
    ]
    rendered = pe.PROMPT_TEMPLATE.format(**{k: "" for k in keys})
    assert "COPYWRITING CRAFT" in rendered
