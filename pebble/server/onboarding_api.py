"""GET /api/onboarding/status — plan_required until 2 completed builds."""
from __future__ import annotations

from pebble.onboarding import onboarding_status
from pebble.security import resolve_user_id


def run_onboarding_status(handler) -> None:
    uid = resolve_user_id(handler)
    if not uid:
        handler._json(401, {"error": "sign in required"})
        return
    handler._json(200, onboarding_status(uid))
