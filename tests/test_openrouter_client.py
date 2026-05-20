"""OpenRouterClient tests.

Pins the contract for the new 3rd provider added 2026-05-19. OpenRouter
exposes Qwen / DeepSeek / Llama / etc. behind one OpenAI-compatible API
so Pebble can route Free tier builds to a cheap-but-capable model
(default: qwen/qwen3-72b-instruct) while paid tiers stay on Anthropic
Claude Sonnet 4.6.

Marc's hypothesis: if Qwen output quality matches Sonnet on the eval
suite, route everything to Qwen and keep premium pricing.
"""
from __future__ import annotations

import os
from unittest.mock import patch, MagicMock

import pytest

from pebble.llm import (
    LLMError,
    OpenRouterClient,
    get_llm_client,
    _OPENROUTER_DEFAULT_MODEL,
)
from pebble.cost import _RATE_CARD, _rate_for_model


# ------------------------------------------------------------------ #
# OpenRouterClient construction                                        #
# ------------------------------------------------------------------ #

def test_construct_with_empty_key_raises():
    with pytest.raises(LLMError) as exc:
        OpenRouterClient(api_key="", model="qwen/qwen3-72b-instruct")
    assert "OPENROUTER_API_KEY" in str(exc.value)


def test_construct_sets_provider_string():
    client = OpenRouterClient(api_key="sk-or-test", model="qwen/qwen3-72b-instruct")
    assert client.provider == "openrouter"
    assert client.model == "qwen/qwen3-72b-instruct"


def test_default_model_is_qwen_3_6_plus():
    """The default is the EXACT model Marc asked for — qwen3.6-plus —
    pinned to its specific version (qwen/qwen3.6-plus-04-02) NOT a
    moving alias. If we ever swap defaults it should be a deliberate
    edit, not an upstream surprise."""
    assert _OPENROUTER_DEFAULT_MODEL == "qwen/qwen3.6-plus-04-02"


# ------------------------------------------------------------------ #
# get_llm_client provider routing                                       #
# ------------------------------------------------------------------ #

def test_provider_openrouter_returns_openrouter_client(monkeypatch):
    monkeypatch.setenv("PEBBLE_PROVIDER", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    monkeypatch.delenv("PEBBLE_MODEL", raising=False)

    client, reason = get_llm_client()
    assert reason == "ok"
    assert client is not None
    assert client.provider == "openrouter"
    assert client.model == _OPENROUTER_DEFAULT_MODEL


def test_provider_openrouter_honors_pebble_model(monkeypatch):
    monkeypatch.setenv("PEBBLE_PROVIDER", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    monkeypatch.setenv("PEBBLE_MODEL", "qwen/qwen3-235b-a22b")

    client, _ = get_llm_client()
    assert client.model == "qwen/qwen3-235b-a22b"


def test_provider_openrouter_missing_key_returns_error(monkeypatch):
    monkeypatch.setenv("PEBBLE_PROVIDER", "openrouter")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    client, reason = get_llm_client()
    assert client is None
    assert "OPENROUTER_API_KEY" in reason


# ------------------------------------------------------------------ #
# httpx call shape — verify we send what OpenRouter expects             #
# ------------------------------------------------------------------ #

def _mock_resp(content: str = "<pebble-file>ok</pebble-file>", status: int = 200):
    """Build a mock httpx.Response that resp.json() returns the OpenAI shape."""
    mock_response = MagicMock()
    mock_response.status_code = status
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "id": "gen-123",
        "model": "qwen/qwen3-72b-instruct",
        "choices": [{"message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},
    }
    return mock_response


def test_generate_sends_openai_shaped_request():
    client = OpenRouterClient(api_key="sk-or-test", model="qwen/qwen3-72b-instruct")

    with patch("httpx.post") as mock_post:
        mock_post.return_value = _mock_resp("response text")
        result = client.generate(system="You are a builder.", user="Build a site.", max_tokens=500)

    assert result == "response text"
    assert mock_post.call_count == 1
    call = mock_post.call_args
    # Endpoint
    assert call.args[0] == "https://openrouter.ai/api/v1/chat/completions"
    # Headers
    headers = call.kwargs["headers"]
    assert headers["Authorization"] == "Bearer sk-or-test"
    assert headers["Content-Type"] == "application/json"
    assert "HTTP-Referer" in headers  # OpenRouter ranking metadata
    assert "X-Title" in headers
    # Body
    body = call.kwargs["json"]
    assert body["model"] == "qwen/qwen3-72b-instruct"
    assert body["max_tokens"] == 500
    # Messages: system + user in OpenAI shape
    msgs = body["messages"]
    assert msgs[0] == {"role": "system", "content": "You are a builder."}
    assert msgs[1] == {"role": "user", "content": "Build a site."}


def test_generate_with_no_system_omits_system_message():
    """When system='' the system message should be omitted, not sent empty."""
    client = OpenRouterClient(api_key="sk-or-test", model="qwen/qwen3-72b-instruct")

    with patch("httpx.post") as mock_post:
        mock_post.return_value = _mock_resp("ok")
        client.generate(system="", user="hello", max_tokens=100)

    msgs = mock_post.call_args.kwargs["json"]["messages"]
    assert len(msgs) == 1
    assert msgs[0]["role"] == "user"


def test_generate_with_images_emits_openai_content_array():
    """Vision inputs use OpenAI's multi-part content array shape."""
    client = OpenRouterClient(api_key="sk-or-test", model="qwen/qwen3-72b-instruct")

    images = [{"media_type": "image/png", "data": "iVBORw0KGgo="}]
    with patch("httpx.post") as mock_post:
        mock_post.return_value = _mock_resp("got the image")
        client.generate(system="x", user="describe", max_tokens=100, images=images)

    user_msg = mock_post.call_args.kwargs["json"]["messages"][1]
    assert user_msg["role"] == "user"
    assert isinstance(user_msg["content"], list)
    assert user_msg["content"][0] == {"type": "text", "text": "describe"}
    assert user_msg["content"][1]["type"] == "image_url"
    assert "data:image/png;base64," in user_msg["content"][1]["image_url"]["url"]


# ------------------------------------------------------------------ #
# Error handling                                                       #
# ------------------------------------------------------------------ #

def test_http_error_wrapped_as_llmerror():
    """OpenRouter returns 402 when the user is out of credits — make sure
    that surfaces as a clean LLMError, NOT a raw httpx exception."""
    import httpx

    client = OpenRouterClient(api_key="sk-or-test", model="qwen/qwen3-72b-instruct")

    err_response = MagicMock()
    err_response.status_code = 402
    err_response.json.return_value = {
        "error": {"message": "Insufficient credits", "code": 402}
    }
    http_err = httpx.HTTPStatusError("402", request=MagicMock(), response=err_response)

    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = http_err

    with patch("httpx.post", return_value=mock_resp):
        with pytest.raises(LLMError) as exc:
            client.generate(system="s", user="u")
    assert "OpenRouter" in str(exc.value)
    assert "402" in str(exc.value) or "Insufficient credits" in str(exc.value)


def test_malformed_response_wrapped_as_llmerror():
    """A response missing `choices` should fail loudly with LLMError,
    not propagate a KeyError up to the engine."""
    client = OpenRouterClient(api_key="sk-or-test", model="qwen/qwen3-72b-instruct")

    bad_resp = MagicMock()
    bad_resp.status_code = 200
    bad_resp.raise_for_status = MagicMock()
    bad_resp.json.return_value = {"id": "x", "model": "y"}  # no `choices`

    with patch("httpx.post", return_value=bad_resp):
        with pytest.raises(LLMError) as exc:
            client.generate(system="s", user="u")
    assert "shape unexpected" in str(exc.value).lower() or "openrouter" in str(exc.value).lower()


# ------------------------------------------------------------------ #
# Cost rate cards                                                      #
# ------------------------------------------------------------------ #

def test_qwen_default_in_rate_card():
    """The DEFAULT model must always have a rate card so cost telemetry
    doesn't silently fall through to the _unknown bucket."""
    assert _OPENROUTER_DEFAULT_MODEL in _RATE_CARD


def test_qwen_rates_cheaper_than_sonnet():
    """The whole business case for Qwen is the cost advantage. Pin it
    against the CURRENT default, not a frozen historical model id."""
    q_in, q_out = _RATE_CARD[_OPENROUTER_DEFAULT_MODEL]
    s_in, s_out = _RATE_CARD["claude-sonnet-4-6"]
    assert q_in < s_in, f"Qwen input ({q_in}) must be cheaper than Sonnet ({s_in})"
    assert q_out < s_out, f"Qwen output ({q_out}) must be cheaper than Sonnet ({s_out})"
    # Pin the order-of-magnitude advantage so a future "small adjustment"
    # doesn't accidentally erase the business case (5x is the floor; today
    # we're closer to 9x in / 7.7x out — Marc's business plan to charge
    # Sonnet prices for Qwen output depends on this gap staying healthy).
    assert q_in <= s_in / 5, "Qwen should be at least 5x cheaper on input"
    assert q_out <= s_out / 5, "Qwen should be at least 5x cheaper on output"


def test_rate_for_model_resolves_qwen_3_6_plus():
    (i, o), _ = _rate_for_model("qwen/qwen3.6-plus-04-02")
    assert i == 0.325
    assert o == 1.95


def test_rate_for_model_unknown_qwen_variant_falls_back():
    """An unknown Qwen variant should fall back to the _unknown rate
    rather than crashing. Just-in-case insurance."""
    (i, o), _ = _rate_for_model("qwen/qwen-99-experimental")
    # _unknown rates are conservative high estimates
    assert i > 0
    assert o > 0
