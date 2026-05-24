"""Phase B1 — tier-gate /api/projects/<slug>/integrations save endpoint.

A free user trying to enable WhatsApp must get a 402 with the
tier-locked envelope. A starter user enabling WhatsApp should succeed;
starter trying Stripe → 402. Pro can do everything."""
import io
import json
import pytest
from unittest.mock import patch

from pebble.server import integrations as endpoint


class FakeHeaders:
    def __init__(self, content_length: int):
        self._cl = content_length
    def get(self, name, default=None):
        if name == "Content-Length":
            return str(self._cl)
        return default


class FakeHandler:
    def __init__(self, body_bytes: bytes):
        self.headers = FakeHeaders(len(body_bytes))
        self.rfile = io.BytesIO(body_bytes)
        self.last_status = None
        self.last_body = None

    def _json(self, status, body):
        self.last_status = status
        self.last_body = body


@pytest.mark.parametrize("plan,integration_id,expected_status", [
    ("free",    "whatsapp",       402),
    ("free",    "stripe",         402),
    ("starter", "whatsapp",       200),
    ("starter", "booking",        200),
    ("starter", "stripe",         402),   # starter can't do Stripe
    ("starter", "custom-code",    402),   # starter can't do custom-code
    ("pro",     "whatsapp",       200),
    ("pro",     "stripe",         200),
    ("pro",     "custom-code",    200),
])
def test_save_tier_gate(plan, integration_id, expected_status):
    body_json = json.dumps({"id": integration_id, "enabled": True, "config": {}})
    handler = FakeHandler(body_json.encode("utf-8"))

    with patch.object(endpoint, "require_project_owner", return_value="user-test-1234567890123456"), \
         patch("pebble.user_plan.get_user_plan",         return_value=plan), \
         patch.object(endpoint, "save_integration",      return_value={"enabled": True, "config": {}}):
        endpoint.run_post_integration(handler, "test-slug")

    assert handler.last_status == expected_status, (
        f"plan={plan} integration={integration_id} expected {expected_status} "
        f"got {handler.last_status}: {handler.last_body}"
    )

    if expected_status == 402:
        assert handler.last_body["code"] == "tier_locked"
        assert handler.last_body["upgrade_url"] == "/pricing"
        assert "integration" in handler.last_body["message"].lower() or \
               handler.last_body["feature"] == integration_id
