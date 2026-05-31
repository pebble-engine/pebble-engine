"""Tests for the v2 SSE build stream (POST /api/v2/generate-stream).

Exercises build_stream_v2_generator with build_v2_core monkeypatched, so we
verify the SSE framing + event ordering without a real LLM call.
"""
from __future__ import annotations

import json

import pebble.server.build_stream_v2 as bs2
from pebble.server.build_v2 import BuildV2Error


def _parse_frames(frames: list[str]) -> list[tuple[str, dict]]:
    out = []
    for f in frames:
        etype = ""
        data = {}
        for line in f.strip().split("\n"):
            if line.startswith("event: "):
                etype = line[7:].strip()
            elif line.startswith("data: "):
                data = json.loads(line[6:].strip())
        if etype:
            out.append((etype, data))
    return out


def test_stream_emits_progress_then_done(monkeypatch):
    def fake_core(brief, progress_cb=None):
        progress_cb("started", {"slug": "acme", "business_name": "Acme"})
        progress_cb("generating", {"model": "claude-sonnet-4-6", "max_tokens": 8000})
        progress_cb("preview_ready", {"slug": "acme", "url": "/preview/acme/"})
        return {"slug": "acme", "preview_url": "/preview/acme/", "file_count": 12,
                "files_written": [], "elapsed_seconds": 5.0, "saved_to": "/x",
                "industry_intel_key": "bakery", "engine_version": "v2"}

    monkeypatch.setattr(bs2, "build_v2_core", fake_core)
    frames = _parse_frames(list(bs2.build_stream_v2_generator(
        json.dumps({"business_name": "Acme", "industry": "bakery"}).encode("utf-8")
    )))
    types = [t for t, _ in frames]
    assert types[0] == "started"
    assert "generating" in types
    assert "preview_ready" in types
    assert types[-1] == "done"
    done_data = frames[-1][1]
    assert done_data["slug"] == "acme"
    assert done_data["engine_version"] == "v2"


def test_stream_emits_error_on_build_v2_error(monkeypatch):
    def fake_core(brief, progress_cb=None):
        raise BuildV2Error(503, "LLM not configured: no key")

    monkeypatch.setattr(bs2, "build_v2_core", fake_core)
    frames = _parse_frames(list(bs2.build_stream_v2_generator(b'{"business_name":"x"}')))
    assert frames[-1][0] == "error"
    assert "LLM not configured" in frames[-1][1]["error"]
    assert frames[-1][1]["status"] == 503


def test_stream_rejects_invalid_json():
    frames = _parse_frames(list(bs2.build_stream_v2_generator(b"not json{")))
    assert frames[-1][0] == "error"
    assert "invalid json" in frames[-1][1]["error"].lower()
