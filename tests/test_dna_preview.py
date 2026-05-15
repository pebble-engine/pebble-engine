"""Unit tests for pebble.server.dna — the GET /api/dna/preview endpoint.

The handler picks one card from style_dna.DNA_CARDS and returns it.
Tests use a fake handler that captures the (status, body) pair instead
of writing to a socket.
"""
from __future__ import annotations

import pytest

from pebble.server.dna import _slim_card, run_dna_preview
from style_dna import DNA_CARDS


class FakeHandler:
    """Minimal stand-in for PebbleHandler. Records the most recent
    `_json(status, body)` call for assertion."""

    def __init__(self, raw_path: str = "/api/dna/preview"):
        self.path = raw_path.split("?", 1)[0]
        self._raw_path = raw_path
        self.last_status: int | None = None
        self.last_body: dict | None = None

    def _json(self, status: int, body: dict) -> None:
        self.last_status = status
        self.last_body = body


def test_preview_returns_some_card_when_no_query():
    h = FakeHandler("/api/dna/preview")
    run_dna_preview(h)
    assert h.last_status == 200
    assert h.last_body["ok"] is True
    assert h.last_body["card"]["id"] in {c["id"] for c in DNA_CARDS}
    assert h.last_body["total"] == len(DNA_CARDS)


def test_preview_with_id_returns_that_exact_card():
    h = FakeHandler("/api/dna/preview?id=swiss_magazine")
    run_dna_preview(h)
    assert h.last_status == 200
    assert h.last_body["card"]["id"] == "swiss_magazine"
    assert h.last_body["card"]["label"] == "Swiss Magazine"


def test_preview_with_unknown_id_returns_404():
    h = FakeHandler("/api/dna/preview?id=does_not_exist")
    run_dna_preview(h)
    assert h.last_status == 404
    assert "does_not_exist" in h.last_body["error"]


def test_preview_with_seed_is_deterministic():
    """Same seed → same card (so a test or a debug session can pin it)."""
    h1 = FakeHandler("/api/dna/preview?seed=42")
    h2 = FakeHandler("/api/dna/preview?seed=42")
    run_dna_preview(h1)
    run_dna_preview(h2)
    assert h1.last_body["card"]["id"] == h2.last_body["card"]["id"]


def test_preview_excludes_listed_ids():
    """Pass the user's current card id to guarantee a different one
    next time. This is the 'Try another' button's contract."""
    excluded = "swiss_magazine,brutalist_editorial,terminal_operator"
    h = FakeHandler(f"/api/dna/preview?exclude={excluded}")
    run_dna_preview(h)
    assert h.last_status == 200
    assert h.last_body["card"]["id"] not in {"swiss_magazine", "brutalist_editorial", "terminal_operator"}


def test_preview_404_when_every_card_excluded():
    every_id = ",".join(c["id"] for c in DNA_CARDS)
    h = FakeHandler(f"/api/dna/preview?exclude={every_id}")
    run_dna_preview(h)
    assert h.last_status == 404
    assert "every DNA card excluded" in h.last_body["error"]


def test_preview_card_carries_ui_relevant_fields():
    """The chip strip in v3 needs label, palette_posture, and fonts to
    render. Lock the schema so a future style_dna refactor can't
    silently drop a field the UI depends on."""
    h = FakeHandler("/api/dna/preview?id=swiss_magazine")
    run_dna_preview(h)
    card = h.last_body["card"]
    for required in (
        "id", "label", "feel",
        "display_font", "body_font",
        "palette_posture",
        "motion_intensity",
    ):
        assert required in card, f"missing {required} in slim card"


def test_preview_does_not_leak_prompt_guardrails():
    """`signature_moves` and `forbidden` are our prompt guardrails — DO
    NOT emit them on this unauthenticated public endpoint. The 2026-05-15
    NLM pass flagged that exposing them lets anyone scrape the entire
    proprietary style matrix by enumerating card ids."""
    h = FakeHandler("/api/dna/preview?id=swiss_magazine")
    run_dna_preview(h)
    card = h.last_body["card"]
    assert "signature_moves" not in card
    assert "forbidden" not in card
    assert "hero_structure" not in card


def test_slim_card_omits_unknown_fields():
    """Future-proofing: if style_dna adds an internal-only field, the
    public payload shouldn't leak it without an explicit add to
    _PUBLIC_FIELDS."""
    fake = {**DNA_CARDS[0], "_internal_thinking_token_estimate": 9999}
    out = _slim_card(fake)
    assert "_internal_thinking_token_estimate" not in out


@pytest.mark.parametrize("query", [
    "?seed=not_a_number",
    "?id=",
    "?exclude=",
])
def test_preview_handles_garbage_query_params_gracefully(query: str):
    """A garbage seed / empty exclude must NOT 500 — fall back to
    random pick from the full set."""
    h = FakeHandler(f"/api/dna/preview{query}")
    run_dna_preview(h)
    assert h.last_status == 200
    assert h.last_body["card"]["id"]
