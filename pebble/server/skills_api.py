"""P2 — GET /api/skills: the public list of curated "power moves" for the UI.

Returns UI-safe metadata only (id/label/description/billable) — the full
instruction bodies stay server-side.
"""
from __future__ import annotations

from pebble import power_moves


def run_list_skills(handler) -> None:
    handler._json(200, {"skills": power_moves.list_skills()})
