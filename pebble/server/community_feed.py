"""Community feed + stats endpoints — backs /community page (2026-05-24).

  GET /api/community/feed   → recent public events (the "This week in Pebble" list)
  GET /api/community/stats  → cached snapshot of community-wide numbers

Both are PUBLIC reads (no auth gate). The community page should load
for anyone, signed-in or not. Visibility of individual rows is enforced
at the events.visibility = 'public' filter; private events never escape.

Fail-soft: any Supabase error returns empty list / null stats, never
500s. The page falls back to a "Loading..." or hides the section.
"""
from __future__ import annotations

from pebble import events, community_stats
from pebble.security import client_ip, plan_limiter


def run_community_feed(handler) -> None:
    """GET /api/community/feed → list of recent public events.

    Public read — no auth required. Rate-limited by IP so a scraper
    can't hammer the endpoint.
    """
    ip = client_ip(handler)
    if not plan_limiter.allow(ip or ""):
        handler._json(429, {"error": "slow down"}); return

    rows = events.list_public_recent(limit=20, days=14)
    handler._json(200, {"events": rows, "count": len(rows)})


def run_community_stats(handler) -> None:
    """GET /api/community/stats → cached snapshot of community numbers.

    Single-row read from community_stats. Refresh-on-stale (15 min) is
    handled inside the helper so the endpoint stays trivially cheap.
    """
    ip = client_ip(handler)
    if not plan_limiter.allow(ip or ""):
        handler._json(429, {"error": "slow down"}); return

    stats = community_stats.get_stats()
    if not stats:
        handler._json(200, {
            "stats": None,
            "fallback": True,
            "message": "Stats unavailable — using cached values upstream.",
        })
        return
    handler._json(200, {"stats": stats})


__all__ = ["run_community_feed", "run_community_stats"]
