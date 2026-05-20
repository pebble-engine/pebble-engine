"""Prompt diet tests (Phase 14a, 2026-05-20).

Pins the diet's behavior: when PEBBLE_PROMPT_DIET is on (default), the
prompt is dramatically shorter and the 5 skill blocks use compact
replacements instead of full SKILL.md injection.
"""
from __future__ import annotations

import importlib

import pytest


# ------------------------------------------------------------------ #
# Diet toggle                                                          #
# ------------------------------------------------------------------ #

def test_diet_enabled_by_default(monkeypatch):
    monkeypatch.delenv("PEBBLE_PROMPT_DIET", raising=False)
    import pebble.prompt_diet
    importlib.reload(pebble.prompt_diet)
    assert pebble.prompt_diet.diet_enabled() is True


@pytest.mark.parametrize("val", ["true", "1", "yes", "on", "TRUE", "True"])
def test_diet_truthy_values(val, monkeypatch):
    monkeypatch.setenv("PEBBLE_PROMPT_DIET", val)
    import pebble.prompt_diet
    importlib.reload(pebble.prompt_diet)
    assert pebble.prompt_diet.diet_enabled() is True


@pytest.mark.parametrize("val", ["false", "0", "no", "off", "FALSE", ""])
def test_diet_falsy_values(val, monkeypatch):
    """Explicit values that turn diet OFF. Empty string counts as "explicitly
    set to nothing" — treated as OFF, distinct from "not set at all" (default)."""
    monkeypatch.setenv("PEBBLE_PROMPT_DIET", val)
    import pebble.prompt_diet
    importlib.reload(pebble.prompt_diet)
    assert pebble.prompt_diet.diet_enabled() is False


# ------------------------------------------------------------------ #
# Constants exist + non-empty                                          #
# ------------------------------------------------------------------ #

def test_all_diet_constants_present():
    from pebble.prompt_diet import (
        NO_SLOP_DIET, IOS_RULES_DIET, STACK_RULES_DIET,
        BUSINESS_INTEL_DIET, DESIGN_SYSTEM_DIET, IMAGE_RULES_DIET,
    )
    for name, val in [
        ("NO_SLOP_DIET", NO_SLOP_DIET),
        ("IOS_RULES_DIET", IOS_RULES_DIET),
        ("STACK_RULES_DIET", STACK_RULES_DIET),
        ("BUSINESS_INTEL_DIET", BUSINESS_INTEL_DIET),
        ("DESIGN_SYSTEM_DIET", DESIGN_SYSTEM_DIET),
        ("IMAGE_RULES_DIET", IMAGE_RULES_DIET),
    ]:
        assert isinstance(val, str) and val.strip(), f"{name} is empty"


def test_diet_constants_are_short():
    """Each compact replacement should be ~100-300 tokens, NOT 2K+ like
    the full SKILL.md blocks they replace. Pins the size discipline."""
    from pebble.prompt_diet import (
        NO_SLOP_DIET, IOS_RULES_DIET, STACK_RULES_DIET,
        BUSINESS_INTEL_DIET, DESIGN_SYSTEM_DIET, IMAGE_RULES_DIET,
    )
    # Rough heuristic: 4 chars per token → 300 tokens ≈ 1200 chars
    LIMIT = 1500  # generous ceiling
    for name, val in [
        ("NO_SLOP_DIET", NO_SLOP_DIET),
        ("IOS_RULES_DIET", IOS_RULES_DIET),
        ("STACK_RULES_DIET", STACK_RULES_DIET),
        ("BUSINESS_INTEL_DIET", BUSINESS_INTEL_DIET),
        ("DESIGN_SYSTEM_DIET", DESIGN_SYSTEM_DIET),
        ("IMAGE_RULES_DIET", IMAGE_RULES_DIET),
    ]:
        assert len(val) <= LIMIT, f"{name} is {len(val)} chars; should be ≤{LIMIT}"


def test_diet_uses_positive_directives():
    """Qwen research: NEVER-stacking confuses smaller models. The diet's
    rules should be primarily affirmative ('Use X', 'Build per Y') not
    negative ('NEVER do X'). Allow up to ~3 NEVER per block as critical
    guardrails; flag if any block has more."""
    from pebble.prompt_diet import (
        NO_SLOP_DIET, IOS_RULES_DIET, STACK_RULES_DIET,
        BUSINESS_INTEL_DIET, DESIGN_SYSTEM_DIET, IMAGE_RULES_DIET,
    )
    for name, val in [
        ("NO_SLOP_DIET", NO_SLOP_DIET),
        ("IOS_RULES_DIET", IOS_RULES_DIET),
        ("STACK_RULES_DIET", STACK_RULES_DIET),
        ("BUSINESS_INTEL_DIET", BUSINESS_INTEL_DIET),
        ("DESIGN_SYSTEM_DIET", DESIGN_SYSTEM_DIET),
        ("IMAGE_RULES_DIET", IMAGE_RULES_DIET),
    ]:
        lower = val.lower()
        never_count = lower.count("never") + lower.count("do not") + lower.count("don't") + lower.count("forbidden")
        assert never_count <= 5, (
            f"{name} has {never_count} negative directives; "
            f"Qwen prefers positive guidance. Reduce or merge."
        )


# ------------------------------------------------------------------ #
# build_prompt integration — diet ON vs OFF actually differs           #
# ------------------------------------------------------------------ #

def _sample_brief() -> dict:
    return {
        "business_name": "Test Coaching",
        "business_type": "Executive coach",
        "audience": "professionals",
        "site_functions": ["leads"],
        "brand_tone": "professional",
        "_industry_intel_key": "business_consultant",
    }


def test_diet_on_produces_shorter_prompt(monkeypatch):
    """Diet ON should cut at least 30% of the prompt size vs OFF.
    Without this guarantee, the diet did nothing measurable."""
    import pebble_engine

    monkeypatch.delenv("PEBBLE_PROMPT_DIET", raising=False)  # default = on
    import pebble.prompt_diet
    importlib.reload(pebble.prompt_diet)
    prompt_on = pebble_engine.build_prompt(_sample_brief(), ds_text="", notes=[])

    monkeypatch.setenv("PEBBLE_PROMPT_DIET", "false")
    importlib.reload(pebble.prompt_diet)
    prompt_off = pebble_engine.build_prompt(_sample_brief(), ds_text="", notes=[])

    assert len(prompt_on) < len(prompt_off), "diet ON should be shorter"
    pct_cut = 1 - (len(prompt_on) / len(prompt_off))
    assert pct_cut >= 0.30, (
        f"diet only cut {pct_cut:.1%}; expected ≥30%. "
        f"Diet={len(prompt_on)}, Full={len(prompt_off)}"
    )


def test_diet_on_keeps_load_bearing_content(monkeypatch):
    """Diet must NOT cut critical content: business name, industry,
    Layout DNA + Style DNA blocks (when present in brief), iOS rules,
    image-sourcing rules."""
    import pebble_engine

    monkeypatch.delenv("PEBBLE_PROMPT_DIET", raising=False)
    import pebble.prompt_diet
    importlib.reload(pebble.prompt_diet)

    prompt = pebble_engine.build_prompt(_sample_brief(), ds_text="", notes=[])
    must_contain = [
        "Test Coaching",            # business name
        "Executive coach",           # business_type
        "100dvh",                    # ios rule (kept)
        "Unsplash",                  # image-sourcing rule (new in diet)
        "Style DNA",                 # the DNA precedence block
    ]
    for needle in must_contain:
        assert needle in prompt, f"diet dropped critical content: {needle!r}"
