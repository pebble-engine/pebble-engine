"""Tests for the cost-estimation helper."""
from __future__ import annotations

import pytest

from pebble.cost import estimate_tokens, estimate_cost, CostEstimate


def test_estimate_tokens_empty():
    assert estimate_tokens("") == 0
    assert estimate_tokens(None) == 0


def test_estimate_tokens_short_english():
    # "hello world" = 11 chars → 2 tokens (11//4)
    assert estimate_tokens("hello world") == 2


def test_estimate_tokens_long_text():
    text = "a" * 4000
    assert estimate_tokens(text) == 1000


def test_estimate_cost_known_model_exact():
    result = estimate_cost(prompt="x" * 4000, response="y" * 4000, model="gemini-3.1-pro-preview")
    assert result.input_tokens == 1000
    assert result.output_tokens == 1000
    # 1000/1M * 1.25 + 1000/1M * 5.0 = 0.00125 + 0.005 = 0.00625
    assert result.estimated_cost_usd == pytest.approx(0.00625, rel=1e-3)
    assert result.rate_card_used == "gemini-3.1-pro-preview"


def test_estimate_cost_prefix_match():
    """Models with version suffixes should fall back to the prefix entry."""
    result = estimate_cost(prompt="a" * 4000, response="b" * 4000, model="claude-opus-4-7-20260101")
    # claude-opus-4-7: (15.0, 75.0) per M tokens
    expected = (1000 / 1_000_000) * 15.0 + (1000 / 1_000_000) * 75.0
    assert result.estimated_cost_usd == pytest.approx(expected, rel=1e-3)
    assert result.rate_card_used == "claude-opus-4-7"


def test_estimate_cost_unknown_model_falls_back():
    result = estimate_cost(prompt="x" * 4000, response="y" * 4000, model="totally-made-up-model")
    assert result.rate_card_used == "_unknown"
    assert result.estimated_cost_usd > 0


def test_estimate_cost_none_inputs_safe():
    result = estimate_cost(prompt=None, response=None, model=None)
    assert result.input_tokens == 0
    assert result.output_tokens == 0
    assert result.estimated_cost_usd == 0.0


def test_cost_estimate_to_dict_shape():
    result = estimate_cost(prompt="hello", response="world", model="gemini-3.1-pro-preview")
    d = result.to_dict()
    assert set(d.keys()) == {"input_tokens", "output_tokens", "estimated_cost_usd", "rate_card_used"}
    assert isinstance(d["estimated_cost_usd"], float)
