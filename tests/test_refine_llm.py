"""End-to-end tests for the LLM-backed refinements in ``pebble.server.refine``.

The deterministic refinements (``simpler``, ``colors``) are covered in
``test_projects_api.py``. This file fills the gap: the LLM-backed paths
(``friendlier``, ``professional``, ``booking``) — exercised with a
FakeClient that returns canned pebble-file blocks, so no real LLM call
is made.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import pebble.engagement as engagement_mod
import pebble.history as history_mod
import pebble.security as security_mod
import pebble.server.refine as refine_mod


class FakeLLMClient:
    """Stand-in for the real LLM client used by ``_run_llm_refinement``.

    Returns a canned response and records every call. The response is the
    raw text the engine's ``parse_files`` will see, so it must include
    pebble-file blocks.
    """
    def __init__(self, response: str = "", *, raise_with: Exception | None = None):
        self.response = response
        self.raise_with = raise_with
        self.calls: list[dict] = []
        self.model = "fake-llm-model"
        self.provider = "fake"

    def generate(self, system: str, user: str, max_tokens: int = 16000, **_kw) -> str:
        self.calls.append({"system": system, "user": user, "max_tokens": max_tokens})
        if self.raise_with:
            raise self.raise_with
        return self.response


@pytest.fixture
def fake_engine(tmp_path, monkeypatch):
    """Wire pebble.server.refine to a tmp output dir + a fake LLM.

    Bypasses ``require_project_owner`` so the existing tests (which don't
    seed a session cookie) still exercise the JSON contract. The auth gate
    itself is covered in tests/test_security.py + tests/test_http_e2e.py.
    """
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(history_mod, "OUTPUT_DIR", out)
    monkeypatch.setattr(security_mod, "_output_dir", lambda: out)
    def bypass(handler, slug):
        if not security_mod.is_valid_slug(slug):
            handler._json(400, {"error": "invalid project slug"})
            return None
        if not (out / slug).exists():
            handler._json(404, {"error": f"project not found: {slug}"})
            return None
        return "test-user"
    monkeypatch.setattr(refine_mod, "require_project_owner", bypass)
    # Isolate engagement storage per test (T17).
    monkeypatch.setattr(engagement_mod, "_engagement_dir", lambda: out / ".engagement")

    fake_pe_module = type("FakeModule", (), {
        "OUTPUT_DIR":              out,
        "parse_files":             _parse_files_for_tests,
        "FILE_FORMAT_INSTRUCTION": "\n\n[FILE FORMAT INSTRUCTION SENTINEL]\n",
    })
    monkeypatch.setattr(refine_mod, "_engine", lambda: fake_pe_module)

    # Patch get_llm_client so we control the response. The fixture writes
    # the FakeLLMClient to a slot the test can read.
    holder = {"client": None}

    def fake_get_client():
        return (holder["client"], "ok")

    # The refine module imports get_llm_client inside _run_llm_refinement,
    # so we patch at the module level it actually pulls from.
    import pebble.llm as llm_mod
    monkeypatch.setattr(llm_mod, "get_llm_client", fake_get_client)

    return {"output": out, "client_holder": holder}


def _parse_files_for_tests(response: str) -> list[tuple[str, str]]:
    """Minimal pebble-file block parser — same shape as the real one in
    pebble_engine.py. We don't depend on the real one because importing
    pebble_engine in tests is a heavier operation than this needs to be.
    """
    import re
    pattern = re.compile(
        r'<pebble-file\s+path="([^"]+)">\s*(.*?)\s*</pebble-file>',
        re.DOTALL,
    )
    return [(m.group(1), m.group(2)) for m in pattern.finditer(response)]


def _seed_site(output: Path, slug: str, files: dict[str, str]):
    site = output / slug / "site"
    site.mkdir(parents=True, exist_ok=True)
    for rel, content in files.items():
        p = site / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


class FakeHandler:
    """Same minimal handler stand-in as test_projects_api uses."""
    def __init__(self, body):
        from io import BytesIO
        raw = json.dumps(body).encode("utf-8")
        self.rfile = BytesIO(raw)
        self.headers = {"Content-Length": str(len(raw))}
        self.status = None
        self.json_body = None

    def _json(self, status, payload):
        self.status = status
        self.json_body = payload


# ---- friendlier ----------------------------------------------------------

def test_friendlier_uses_llm_and_writes_returned_files(fake_engine):
    _seed_site(fake_engine["output"], "p1", {
        "app/page.tsx": (
            'export default function P() {\n'
            '  return <main><h1>Welcome</h1></main>;\n'
            '}'
        ),
    })
    fake_engine["client_holder"]["client"] = FakeLLMClient(
        response='<pebble-file path="app/page.tsx">\n'
                 'export default function P() {\n'
                 '  return <main><h1>Hey, welcome 👋</h1></main>;\n'
                 '}\n'
                 '</pebble-file>'
    )
    h = FakeHandler({"slug": "p1", "refinement_id": "friendlier"})
    refine_mod.run_refine(h)
    assert h.status == 200
    body = h.json_body
    assert body["kind"] == "llm"
    assert body["billable"] is True
    assert "app/page.tsx" in body["files_changed"]
    assert body["snapshot_id"]  # snapshotted before applying
    content = (fake_engine["output"] / "p1" / "site" / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "Hey, welcome 👋" in content


def test_friendlier_records_call_details(fake_engine):
    _seed_site(fake_engine["output"], "p1", {
        "app/page.tsx": "export default function P() { return <main>Hi</main>; }",
    })
    client = FakeLLMClient(
        response='<pebble-file path="app/page.tsx">export default function P() { return <main>Howdy</main>; }</pebble-file>'
    )
    fake_engine["client_holder"]["client"] = client
    h = FakeHandler({"slug": "p1", "refinement_id": "friendlier"})
    refine_mod.run_refine(h)
    # Sanity: the LLM was actually called once
    assert len(client.calls) == 1
    # The prompt should include both the focused instruction and the file content
    user_prompt = client.calls[0]["user"]
    assert "warmer" in user_prompt.lower() or "friendl" in user_prompt.lower() or "conversational" in user_prompt.lower()
    assert "app/page.tsx" in user_prompt  # the existing file was included as context


def test_professional_uses_llm(fake_engine):
    _seed_site(fake_engine["output"], "p1", {
        "app/page.tsx": "export default function P() { return <main>Yo!</main>; }",
    })
    fake_engine["client_holder"]["client"] = FakeLLMClient(
        response='<pebble-file path="app/page.tsx">export default function P() { return <main>Welcome to our practice.</main>; }</pebble-file>'
    )
    h = FakeHandler({"slug": "p1", "refinement_id": "professional"})
    refine_mod.run_refine(h)
    assert h.status == 200
    assert h.json_body["billable"] is True
    assert h.json_body["kind"] == "llm"


def test_booking_uses_llm(fake_engine):
    _seed_site(fake_engine["output"], "p1", {
        "app/page.tsx": "export default function P() { return <main><h1>Hi</h1></main>; }",
    })
    fake_engine["client_holder"]["client"] = FakeLLMClient(
        response='<pebble-file path="app/page.tsx">export default function P() { return <main><h1>Hi</h1><section>Book an appointment</section></main>; }</pebble-file>'
    )
    h = FakeHandler({"slug": "p1", "refinement_id": "booking"})
    refine_mod.run_refine(h)
    assert h.status == 200
    assert h.json_body["billable"] is True


# ---- error handling ------------------------------------------------------

def test_llm_no_files_returned_is_502(fake_engine):
    _seed_site(fake_engine["output"], "p1", {
        "app/page.tsx": "export default function P() { return <main>Hi</main>; }",
    })
    fake_engine["client_holder"]["client"] = FakeLLMClient(
        response="Sorry, I couldn't do that.",  # no <pebble-file> blocks
    )
    h = FakeHandler({"slug": "p1", "refinement_id": "friendlier"})
    refine_mod.run_refine(h)
    assert h.status == 502
    assert "no <pebble-file> blocks" in (h.json_body.get("error") or "").lower()


def test_llm_error_propagated(fake_engine):
    _seed_site(fake_engine["output"], "p1", {
        "app/page.tsx": "x",
    })
    from pebble.llm import LLMError
    fake_engine["client_holder"]["client"] = FakeLLMClient(raise_with=LLMError("rate limited"))
    h = FakeHandler({"slug": "p1", "refinement_id": "friendlier"})
    refine_mod.run_refine(h)
    assert h.status == 502
    assert "rate limited" in (h.json_body.get("error") or "")


def test_llm_with_no_tsx_files_returns_error(fake_engine):
    """The LLM context-builder requires at least one .tsx file. If a project
    has no .tsx files yet, the refinement returns a 502 with a clear error."""
    _seed_site(fake_engine["output"], "p1", {
        "package.json": "{}",  # no .tsx files
    })
    fake_engine["client_holder"]["client"] = FakeLLMClient(response="should-not-be-called")
    h = FakeHandler({"slug": "p1", "refinement_id": "friendlier"})
    refine_mod.run_refine(h)
    assert h.status == 502
    assert "no .tsx files" in (h.json_body.get("error") or "")


def test_llm_snapshotted_before_call_so_failures_are_reversible(fake_engine):
    """If the LLM fails mid-refinement, the pre-refinement snapshot
    should still exist so the user can roll back."""
    _seed_site(fake_engine["output"], "p1", {
        "app/page.tsx": "ORIGINAL",
    })
    from pebble.llm import LLMError
    fake_engine["client_holder"]["client"] = FakeLLMClient(raise_with=LLMError("oops"))
    h = FakeHandler({"slug": "p1", "refinement_id": "friendlier"})
    refine_mod.run_refine(h)
    # A snapshot exists even though the refinement failed
    snaps = history_mod.list_history("p1")
    assert len(snaps) >= 1
    assert any("friendlier" in s.reason for s in snaps)


# ---- T17: engagement wiring + privacy regression --------------------------

def test_refine_logs_engagement_event_on_success(fake_engine):
    _seed_site(fake_engine["output"], "p1", {
        "app/page.tsx": "export default function P() { return <main>Yo</main>; }",
    })
    fake_engine["client_holder"]["client"] = FakeLLMClient(
        response='<pebble-file path="app/page.tsx">export default function P() { return <main>Howdy</main>; }</pebble-file>'
    )
    h = FakeHandler({"slug": "p1", "refinement_id": "friendlier"})
    refine_mod.run_refine(h)
    assert h.status == 200
    events = engagement_mod.read_user_events("test-user")
    assert len(events) == 1
    assert events[0]["event"] == "refine_used"


def test_refine_does_not_log_on_502_llm_error(fake_engine):
    """LLM-error refinement (no <pebble-file> returned) must NOT log
    an event. Engagement counts successful actions."""
    _seed_site(fake_engine["output"], "p1", {
        "app/page.tsx": "export default function P() { return <main>Hi</main>; }",
    })
    fake_engine["client_holder"]["client"] = FakeLLMClient(response="sorry")
    h = FakeHandler({"slug": "p1", "refinement_id": "friendlier"})
    refine_mod.run_refine(h)
    assert h.status == 502
    assert engagement_mod.read_user_events("test-user") == []


def test_refine_engagement_never_contains_refinement_id(fake_engine):
    """PRIVACY REGRESSION — the engagement log must NEVER record which
    refinement chip was clicked. Only the generic 'refine_used' event."""
    _seed_site(fake_engine["output"], "p1", {
        "app/page.tsx": "export default function P() { return <main>Hi</main>; }",
    })
    fake_engine["client_holder"]["client"] = FakeLLMClient(
        response='<pebble-file path="app/page.tsx">export default function P() { return <main>Howdy</main>; }</pebble-file>'
    )
    h = FakeHandler({"slug": "p1", "refinement_id": "booking"})
    refine_mod.run_refine(h)
    log_file = fake_engine["output"] / ".engagement" / "test-user.jsonl"
    text = log_file.read_text(encoding="utf-8")
    assert "booking" not in text
    assert "friendlier" not in text
    assert "professional" not in text
    assert "p1" not in text  # slug must not leak either
