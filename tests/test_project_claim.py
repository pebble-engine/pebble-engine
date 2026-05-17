"""POST /api/projects/<slug>/claim — attach an anonymous build to the
caller's user account.

Inverted-onboarding pattern (#3 from the Onboarding Pattern Cheat Sheet):
visitors can run the questionnaire and see a built site without signing
up. When they decide to keep it, signup happens; the claim endpoint
stamps `_user_id` onto the build's brief.json so it appears in their
dashboard.

Auth model (already enforced by `require_project_owner`):
- 401 if not signed in
- 404 if project doesn't exist
- 403 if project is owned by someone else
- 200 if project is unowned (claimable) OR already owned by caller (idempotent)
"""
from __future__ import annotations

import json
from io import BytesIO
from typing import Optional

import pytest

import pebble_engine
from pebble.server import projects as projects_mod


class FakeHandler:
    def __init__(self, body: dict | None = None, user_id: Optional[str] = "uuid-caller"):
        raw = json.dumps(body or {}).encode("utf-8") if body is not None else b""
        self.rfile = BytesIO(raw)
        self.headers = {"Content-Length": str(len(raw))}
        self._user_id = user_id
        self.status: int | None = None
        self.body: dict | None = None

    def _json(self, status: int, payload: dict, extra_headers=None) -> None:  # noqa: ARG002
        self.status = status
        self.body = payload


@pytest.fixture
def output_root(tmp_path, monkeypatch):
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", tmp_path)
    return tmp_path


@pytest.fixture
def patch_auth(monkeypatch):
    """Patch `current_user_id` to return whatever the handler carries.
    The real `_project_owner` reads brief.json from tmp_path (via
    OUTPUT_DIR monkeypatch in `output_root`) so we don't patch it."""
    def fake_current_user_id(handler):
        return getattr(handler, "_user_id", None)
    from pebble.server import auth as auth_mod
    monkeypatch.setattr(auth_mod, "current_user_id", fake_current_user_id)


def _seed_project(output_root, slug: str, user_id: Optional[str]) -> None:
    project_dir = output_root / slug
    project_dir.mkdir(parents=True)
    brief = {"business_name": slug, "business_type": "café"}
    if user_id is not None:
        brief["_user_id"] = user_id
    (project_dir / "brief.json").write_text(json.dumps(brief), encoding="utf-8")


# --------- 401/404/403/400 gates ------------------------------------------

def test_claim_returns_401_when_not_signed_in(output_root, patch_auth):
    _seed_project(output_root, "cafe-slug", user_id=None)
    h = FakeHandler(user_id=None)
    projects_mod.run_claim_project(h, "cafe-slug")
    assert h.status == 401


def test_claim_returns_404_when_project_missing(output_root, patch_auth):
    h = FakeHandler(user_id="uuid-caller")
    projects_mod.run_claim_project(h, "nonexistent")
    assert h.status == 404


def test_claim_returns_403_when_owned_by_other(output_root, patch_auth):
    _seed_project(output_root, "owned-by-other", user_id="uuid-someone-else")
    h = FakeHandler(user_id="uuid-caller")
    projects_mod.run_claim_project(h, "owned-by-other")
    assert h.status == 403


def test_claim_rejects_path_traversal_slug(output_root, patch_auth):
    h = FakeHandler(user_id="uuid-caller")
    projects_mod.run_claim_project(h, "../etc/passwd")
    assert h.status == 400


# --------- happy path -----------------------------------------------------

def test_claim_stamps_user_id_on_unowned_project(output_root, patch_auth):
    _seed_project(output_root, "anon-build", user_id=None)
    h = FakeHandler(user_id="uuid-caller")
    projects_mod.run_claim_project(h, "anon-build")
    assert h.status == 200
    brief = json.loads((output_root / "anon-build" / "brief.json").read_text())
    assert brief["_user_id"] == "uuid-caller"


def test_claim_is_idempotent_when_already_owner(output_root, patch_auth):
    _seed_project(output_root, "already-mine", user_id="uuid-caller")
    h = FakeHandler(user_id="uuid-caller")
    projects_mod.run_claim_project(h, "already-mine")
    assert h.status == 200
    brief = json.loads((output_root / "already-mine" / "brief.json").read_text())
    assert brief["_user_id"] == "uuid-caller"


def test_claim_response_includes_slug(output_root, patch_auth):
    _seed_project(output_root, "anon-build", user_id=None)
    h = FakeHandler(user_id="uuid-caller")
    projects_mod.run_claim_project(h, "anon-build")
    assert h.body is not None
    assert h.body.get("slug") == "anon-build"


def test_claim_preserves_other_brief_fields(output_root, patch_auth):
    """The endpoint must NOT clobber the rest of brief.json."""
    project_dir = output_root / "preserve-me"
    project_dir.mkdir()
    original = {
        "business_name": "Test Bakery",
        "business_type": "bakery",
        "phone": "(555) 555-0101",
        "_design_dna": "tactile_y2k",
    }
    (project_dir / "brief.json").write_text(json.dumps(original), encoding="utf-8")

    h = FakeHandler(user_id="uuid-caller")
    projects_mod.run_claim_project(h, "preserve-me")
    assert h.status == 200

    after = json.loads((project_dir / "brief.json").read_text())
    assert after["_user_id"] == "uuid-caller"
    assert after["business_name"] == "Test Bakery"
    assert after["business_type"] == "bakery"
    assert after["phone"] == "(555) 555-0101"
    assert after["_design_dna"] == "tactile_y2k"


def test_claim_writes_atomically(output_root, patch_auth):
    """Sanity: a successful claim leaves brief.json with valid JSON,
    not a half-written file."""
    _seed_project(output_root, "atomic-test", user_id=None)
    h = FakeHandler(user_id="uuid-caller")
    projects_mod.run_claim_project(h, "atomic-test")
    assert h.status == 200
    # Re-read; should still parse cleanly.
    text = (output_root / "atomic-test" / "brief.json").read_text()
    parsed = json.loads(text)
    assert isinstance(parsed, dict)
