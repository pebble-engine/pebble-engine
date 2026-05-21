"""Bot persona endpoint tests (Phase 25b, 2026-05-20).

Pins the API contract + the safe fallback behavior. Doesn't hit the LLM
in tests — the runtime safety net (return canned fallbacks instead of
500ing) is the most important behavior to lock in, because it's what
keeps the workspace UI feeling alive when OpenRouter has a hiccup.
"""
from __future__ import annotations

import json

import pytest

from pebble.server import bot_message


# ------------------------------------------------------------------ #
# Intent → system prompt mapping                                       #
# ------------------------------------------------------------------ #


def test_system_prompts_exist_for_all_intents():
    for intent in ("greeting", "status", "chips"):
        prompt = bot_message._system_for(intent)
        assert isinstance(prompt, str) and len(prompt) > 30
        assert "Pebble" in prompt or "assistant" in prompt.lower()


def test_unknown_intent_returns_safe_fallback_prompt():
    prompt = bot_message._system_for("unknown_xyz")
    assert isinstance(prompt, str) and len(prompt) > 0


def test_greeting_prompt_mentions_business_context():
    prompt = bot_message._system_for("greeting")
    assert "business_name" in prompt
    assert "business_type" in prompt


def test_status_prompt_anchors_on_phase():
    prompt = bot_message._system_for("status")
    assert "phase" in prompt
    assert "1 short sentence" in prompt or "1 sentence" in prompt or "under 90 chars" in prompt


def test_chips_prompt_requests_json_array_of_3():
    prompt = bot_message._system_for("chips")
    assert "JSON array" in prompt
    assert "3" in prompt


# ------------------------------------------------------------------ #
# User message construction                                            #
# ------------------------------------------------------------------ #


def test_user_message_greeting_includes_business_name():
    msg = bot_message._user_message_for("greeting", {
        "business_name": "Joe's Plumbing", "business_type": "plumber",
    })
    assert "Joe's Plumbing" in msg
    assert "plumber" in msg


def test_user_message_status_includes_phase():
    msg = bot_message._user_message_for("status", {
        "business_name": "T", "phase": "writing pages",
    })
    assert "writing pages" in msg


def test_user_message_chips_includes_business_type():
    msg = bot_message._user_message_for("chips", {
        "business_name": "T", "business_type": "bakery",
    })
    assert "bakery" in msg


def test_user_message_handles_missing_business_name():
    """Empty business_name should fall back to 'Untitled' instead of crashing."""
    msg = bot_message._user_message_for("greeting", {})
    assert "Untitled" in msg


# ------------------------------------------------------------------ #
# Chips array extraction from LLM raw text                             #
# ------------------------------------------------------------------ #


def test_extract_chips_from_clean_json():
    raw = '["Refine Hero", "Add Trust Section", "Change Palette"]'
    assert bot_message._extract_chips_array(raw) == [
        "Refine Hero", "Add Trust Section", "Change Palette",
    ]


def test_extract_chips_from_markdown_fenced():
    raw = "Sure! Here are 3 ideas:\n\n```json\n" \
          '["A", "B", "C"]\n```'
    assert bot_message._extract_chips_array(raw) == ["A", "B", "C"]


def test_extract_chips_from_prose_wrapped():
    raw = "I think you should: [\"Strengthen Hero\", \"Add CTA\", \"Tweak Colors\"]. Hope that helps!"
    chips = bot_message._extract_chips_array(raw)
    assert "Strengthen Hero" in chips
    assert "Add CTA" in chips


def test_extract_chips_caps_at_3():
    raw = '["a", "b", "c", "d", "e"]'
    assert bot_message._extract_chips_array(raw) == ["a", "b", "c"]


def test_extract_chips_returns_empty_on_garbage():
    raw = "I cannot do that."
    assert bot_message._extract_chips_array(raw) == []


def test_extract_chips_returns_empty_on_invalid_json():
    raw = "[abc, def, ghi]"
    assert bot_message._extract_chips_array(raw) == []


# ------------------------------------------------------------------ #
# Module constants                                                     #
# ------------------------------------------------------------------ #


def test_bot_chat_model_is_set():
    assert bot_message.BOT_CHAT_MODEL
    # It should be a cheap chat model — anything but the expensive defaults.
    assert "sonnet" not in bot_message.BOT_CHAT_MODEL.lower()
    assert "opus" not in bot_message.BOT_CHAT_MODEL.lower()
    assert "plus" not in bot_message.BOT_CHAT_MODEL.lower()
