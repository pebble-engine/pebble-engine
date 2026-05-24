"""Tests for the Pebble assistant chat endpoint (pebble.server.chat).

Pure-function tests — no LLM call, no auth, no HTTP. The endpoint
itself is auth-gated and verified via curl in the smoke loop; the
real risk lives in the JSON parsing + sitemap filtering, which is
what protects users from a runaway model that invents routes or
suggests unsupported destructive actions. Those are unit-testable
without spinning up the server.
"""
from __future__ import annotations

import json

import pytest

from pebble.server import chat


# ------------------------------------------------------------------ #
# _extract_json_object — happy path + the gnarly LLM output shapes    #
# ------------------------------------------------------------------ #


def test_extract_returns_dict_for_clean_json_object():
    raw = '{"reply": "hi", "navigate_to": null, "confirm_action": null}'
    parsed = chat._extract_json_object(raw)
    assert parsed == {"reply": "hi", "navigate_to": None, "confirm_action": None}


def test_extract_returns_dict_when_wrapped_in_markdown_fence():
    raw = '```json\n{"reply": "hi", "navigate_to": null, "confirm_action": null}\n```'
    parsed = chat._extract_json_object(raw)
    assert parsed is not None
    assert parsed["reply"] == "hi"


def test_extract_returns_dict_when_prose_precedes_object():
    raw = 'Sure! Here is the JSON:\n{"reply": "hi", "navigate_to": null, "confirm_action": null}'
    parsed = chat._extract_json_object(raw)
    assert parsed is not None
    assert parsed["reply"] == "hi"


def test_extract_returns_none_for_non_json():
    assert chat._extract_json_object("hello world") is None
    assert chat._extract_json_object("") is None


def test_extract_returns_none_for_array_only():
    # Caller expects a dict response — bare arrays are not a valid reply.
    assert chat._extract_json_object('["a", "b"]') is None


# ------------------------------------------------------------------ #
# _safe_navigate — the route allowlist                                #
# ------------------------------------------------------------------ #
# The reason a sitemap exists at all: the LLM occasionally invents
# plausible-looking routes ("/account/cancel", "/billing"). The
# allowlist drops anything not in the sitemap so the UI never
# router.push() to a 404.


def test_safe_navigate_accepts_path_in_sitemap():
    sitemap = [{"path": "/dashboard", "label": "Dashboard"}]
    assert chat._safe_navigate("/dashboard", sitemap) == "/dashboard"


def test_safe_navigate_rejects_path_not_in_sitemap():
    sitemap = [{"path": "/dashboard", "label": "Dashboard"}]
    assert chat._safe_navigate("/account/cancel", sitemap) is None


def test_safe_navigate_rejects_external_url():
    sitemap = [{"path": "/dashboard", "label": "Dashboard"}]
    # Belt + suspenders — even if somehow allowed by sitemap, external
    # URLs should never satisfy the leading-slash check.
    assert chat._safe_navigate("https://evil.example.com", sitemap) is None


def test_safe_navigate_rejects_protocol_relative_url():
    sitemap = [{"path": "/dashboard", "label": "Dashboard"}]
    # Protocol-relative URLs ("//evil.com/x") start with / and would
    # otherwise pass a naive check. They don't pass the allowlist.
    assert chat._safe_navigate("//evil.example.com", sitemap) is None


def test_safe_navigate_rejects_none_and_non_string():
    sitemap = [{"path": "/dashboard", "label": "Dashboard"}]
    assert chat._safe_navigate(None, sitemap) is None
    assert chat._safe_navigate(42, sitemap) is None
    assert chat._safe_navigate({"path": "/dashboard"}, sitemap) is None


def test_safe_navigate_rejects_path_without_leading_slash():
    sitemap = [{"path": "/dashboard", "label": "Dashboard"}]
    assert chat._safe_navigate("dashboard", sitemap) is None


# ------------------------------------------------------------------ #
# _safe_confirm — destructive action allowlist                        #
# ------------------------------------------------------------------ #
# Same protection pattern as navigation: the LLM can SUGGEST a known
# destructive intent (open_billing_portal, delete_account) but cannot
# invent new ones. Unknown action keys are silently dropped so a
# hallucinated "wipe_database" never makes it to the UI.


def test_safe_confirm_accepts_known_action():
    assert chat._safe_confirm("open_billing_portal") == "open_billing_portal"
    assert chat._safe_confirm("delete_account") == "delete_account"


def test_safe_confirm_rejects_unknown_action():
    assert chat._safe_confirm("wipe_database") is None
    assert chat._safe_confirm("transfer_funds") is None
    assert chat._safe_confirm("") is None


def test_safe_confirm_rejects_non_string():
    assert chat._safe_confirm(None) is None
    assert chat._safe_confirm(42) is None
    assert chat._safe_confirm({"key": "open_billing_portal"}) is None


def test_safe_confirm_actions_all_have_label_and_intent():
    # Each entry in CONFIRM_ACTIONS feeds the system prompt and the UI
    # confirmation panel. Both need label + intent or the model
    # doesn't know when to use it and the UI can't render it.
    for key, meta in chat.CONFIRM_ACTIONS.items():
        assert isinstance(key, str) and key
        assert "label" in meta and isinstance(meta["label"], str)
        assert "intent" in meta and isinstance(meta["intent"], str)


# ------------------------------------------------------------------ #
# _build_system — system prompt assembly                              #
# ------------------------------------------------------------------ #


def test_system_prompt_lists_each_sitemap_path():
    sitemap = [
        {"path": "/dashboard", "label": "Dashboard"},
        {"path": "/settings",  "label": "Account settings"},
    ]
    system = chat._build_system(sitemap)
    assert "/dashboard" in system
    assert "/settings" in system
    assert "Dashboard" in system
    assert "Account settings" in system


def test_system_prompt_lists_all_confirm_action_keys():
    system = chat._build_system(chat.DEFAULT_SITEMAP)
    for key in chat.CONFIRM_ACTIONS:
        assert key in system


def test_system_prompt_mentions_strict_json_output():
    system = chat._build_system(chat.DEFAULT_SITEMAP)
    # The model needs an unambiguous instruction to emit JSON only.
    assert "JSON" in system
    assert '"reply"' in system
    assert '"navigate_to"' in system
    assert '"confirm_action"' in system


def test_system_prompt_warns_against_inventing_routes():
    system = chat._build_system(chat.DEFAULT_SITEMAP)
    # The phrase doesn't have to match exactly — just verify intent
    # is communicated.
    lowered = system.lower()
    assert "never invent" in lowered or "only these" in lowered or "exact path" in lowered


# ------------------------------------------------------------------ #
# DEFAULT_SITEMAP — the routes the UI actually has                    #
# ------------------------------------------------------------------ #
# Pinning prevents the case where someone deletes a route from the
# UI but forgets to drop it here — then Peblet keeps sending users
# to a 404 page.


def test_default_sitemap_contains_dashboard_and_settings():
    paths = {row["path"] for row in chat.DEFAULT_SITEMAP}
    assert "/dashboard" in paths
    assert "/settings" in paths
    assert "/templates" in paths
    assert "/integrations" in paths
    assert "/community" in paths


def test_default_sitemap_entries_have_path_and_label():
    for row in chat.DEFAULT_SITEMAP:
        assert isinstance(row.get("path"), str) and row["path"].startswith("/")
        assert isinstance(row.get("label"), str) and row["label"]
