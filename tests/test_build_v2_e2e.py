"""End-to-end smoke for POST /api/v2/generate.

Uses the real on-disk bakery library + a mocked LLM client so the test
is deterministic and free. Asserts the contract we promise downstream:
build_meta.json exists with engine_version=v2, page.tsx exists, no
{{...}} leaks in output, brief.json captures the request.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from pebble.server.build_v2 import run_build_v2


def _make_handler(brief: dict) -> MagicMock:
    body = json.dumps(brief).encode("utf-8")
    handler = MagicMock()
    handler.headers = {"Content-Length": str(len(body))}
    handler.rfile.read.return_value = body
    return handler


def _fake_sonnet_response() -> str:
    """A realistic Sonnet response for a Stoneground Loaf brief."""
    return json.dumps({
        "block_picks": [
            {
                "block_id": "bakery/hero_artisan",
                "slot_values": {
                    "eyebrow": "Brooklyn",
                    "headline": "Sourdough, made slowly",
                    "subheadline": "Real bread, milled and baked in Brooklyn.",
                    "cta_primary": "Reserve a loaf",
                    "cta_secondary": "Our story",
                    "hero_image": "[pexels:artisan sourdough bread]",
                },
            },
            {
                "block_id": "bakery/footer_compact",
                "slot_values": {
                    "business_name": "Stoneground Loaf",
                    "tagline": "Naturally leavened sourdough.",
                    "year": "2026",
                    "links": [
                        {"label": "Order", "href": "/order"},
                        {"label": "About", "href": "/about"},
                    ],
                },
            },
        ],
        "palette": {"bg": "stone-50", "fg": "stone-900",
                    "accent": "orange-700", "muted": "stone-200"},
    })


def test_v2_generate_produces_runnable_site(tmp_path, monkeypatch):
    fake_client = MagicMock()
    fake_client.generate.return_value = _fake_sonnet_response()
    fake_client.model = "claude-sonnet-4-6"
    fake_client.provider = "anthropic"

    monkeypatch.setattr(
        "pebble.server.build_v2.get_llm_client",
        lambda: (fake_client, "ok"),
    )
    monkeypatch.setattr(
        "pebble.server.build_v2._output_dir",
        lambda: tmp_path,
    )

    handler = _make_handler({
        "business_name": "Stoneground Loaf",
        "industry": "bakery",
        "extra_context": "Brooklyn sourdough subscription",
    })
    run_build_v2(handler)

    # response contract
    handler._json.assert_called_once()
    status, body = handler._json.call_args[0]
    assert status == 200
    assert body["slug"] == "stoneground-loaf"
    assert body["engine_version"] == "v2"

    # file contract
    project_dir = tmp_path / "stoneground-loaf"
    assert (project_dir / "brief.json").exists()
    saved_brief = json.loads((project_dir / "brief.json").read_text())
    assert saved_brief["business_name"] == "Stoneground Loaf"

    meta = json.loads((project_dir / "build_meta.json").read_text())
    assert meta["engine_version"] == "v2"
    assert meta["model"] == "claude-sonnet-4-6"
    assert meta["provider"] == "anthropic"
    assert "bakery/hero_artisan" in meta["block_picks"]
    assert "built_at" in meta

    page = (project_dir / "site" / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "Sourdough" in page
    assert "Stoneground Loaf" in page
    assert "{{" not in page  # the placeholder-leak guarantee


def test_v2_generate_rejects_empty_body(tmp_path, monkeypatch):
    monkeypatch.setattr("pebble.server.build_v2._output_dir", lambda: tmp_path)
    handler = MagicMock()
    handler.headers = {"Content-Length": "0"}
    run_build_v2(handler)
    status, body = handler._json.call_args[0]
    assert status == 400
    assert "empty" in body["error"].lower()


def test_v2_generate_rejects_invalid_json(tmp_path, monkeypatch):
    monkeypatch.setattr("pebble.server.build_v2._output_dir", lambda: tmp_path)
    handler = MagicMock()
    handler.headers = {"Content-Length": "5"}
    handler.rfile.read.return_value = b"not{ "
    run_build_v2(handler)
    status, body = handler._json.call_args[0]
    assert status == 400
    assert "json" in body["error"].lower()


def test_v2_generate_503s_when_llm_unavailable(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "pebble.server.build_v2.get_llm_client",
        lambda: (None, "ANTHROPIC_API_KEY not set"),
    )
    monkeypatch.setattr("pebble.server.build_v2._output_dir", lambda: tmp_path)
    handler = _make_handler({"business_name": "x", "industry": "bakery"})
    run_build_v2(handler)
    status, body = handler._json.call_args[0]
    assert status == 503
    assert "ANTHROPIC" in body["error"]


def test_v2_generate_400s_on_unknown_industry(tmp_path, monkeypatch):
    fake_client = MagicMock()
    monkeypatch.setattr(
        "pebble.server.build_v2.get_llm_client",
        lambda: (fake_client, "ok"),
    )
    monkeypatch.setattr("pebble.server.build_v2._output_dir", lambda: tmp_path)
    handler = _make_handler({"business_name": "x", "industry": "telepathic-yoga-shamanism"})
    run_build_v2(handler)
    status, body = handler._json.call_args[0]
    assert status == 400
    assert "industry" in body["error"].lower()
