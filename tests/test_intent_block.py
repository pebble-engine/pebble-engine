"""Build intent block tests (Phase 34, 2026-05-21).

Pins the Business vs Project intent block rendered by
`_build_intent_block` in pebble_engine.py.

The intent block is the LLM-visible framing for "is this a real business
site or a developer sandbox?" — it sets conversion-vs-craft priorities
before any other section of the prompt renders.
"""
from __future__ import annotations

import pytest

import pebble_engine as engine


# ------------------------------------------------------------------ #
# Default + unknown-value behavior                                    #
# ------------------------------------------------------------------ #


def test_missing_intent_defaults_to_business():
    block = engine._build_intent_block({})
    assert "BUSINESS" in block
    assert "PROJECT" not in block


def test_empty_string_intent_defaults_to_business():
    block = engine._build_intent_block({"intent": ""})
    assert "BUSINESS" in block


def test_none_intent_defaults_to_business():
    block = engine._build_intent_block({"intent": None})
    assert "BUSINESS" in block


def test_unknown_intent_value_defaults_to_business():
    block = engine._build_intent_block({"intent": "freelancer"})
    assert "BUSINESS" in block


def test_case_insensitive_business():
    block = engine._build_intent_block({"intent": "BUSINESS"})
    assert "BUSINESS" in block


def test_whitespace_trimmed():
    block = engine._build_intent_block({"intent": "  project  "})
    assert "PROJECT" in block


# ------------------------------------------------------------------ #
# Business mode content                                               #
# ------------------------------------------------------------------ #


def test_business_block_emphasizes_conversion():
    block = engine._build_intent_block({"intent": "business"})
    # Must talk about CTAs and conversion priorities
    assert "CTA" in block
    assert "conversion" in block.lower()
    # Real form wiring (Resend) is required for business mode
    assert "Resend" in block


def test_business_block_calls_for_trust_signals():
    block = engine._build_intent_block({"intent": "business"})
    assert "trust" in block.lower()


def test_business_block_calls_for_schema_org():
    block = engine._build_intent_block({"intent": "business"})
    assert "schema.org" in block.lower() or "json-ld" in block.lower()


# ------------------------------------------------------------------ #
# Project mode content                                                #
# ------------------------------------------------------------------ #


def test_project_block_emphasizes_craft_over_conversion():
    block = engine._build_intent_block({"intent": "project"})
    assert "PROJECT" in block
    assert "craft" in block.lower()
    # Project mode should explicitly downplay the conversion pattern
    assert "understated" in block.lower() or "less aggressive" in block.lower() or "one primary CTA" in block.lower()


def test_project_block_calls_for_readable_code():
    block = engine._build_intent_block({"intent": "project"})
    # The developer audience cares about source-level cleanliness
    assert "READ" in block or "source code" in block.lower() or "readable" in block.lower()


def test_project_block_mentions_design_fidelity():
    block = engine._build_intent_block({"intent": "project"})
    assert "DNA" in block or "design fidelity" in block.lower()


def test_project_and_business_blocks_are_different():
    business = engine._build_intent_block({"intent": "business"})
    project  = engine._build_intent_block({"intent": "project"})
    assert business != project


# ------------------------------------------------------------------ #
# Length sanity                                                       #
# ------------------------------------------------------------------ #


def test_blocks_are_focused_not_essays():
    """Intent blocks should be terse — they're framing, not the meat
    of the prompt. Each under 1500 chars."""
    for intent in ("business", "project"):
        block = engine._build_intent_block({"intent": intent})
        assert len(block) < 1500, f"{intent} block is {len(block)} chars — too long"
        assert len(block) > 200, f"{intent} block is {len(block)} chars — too short"
