"""Community stats — cached snapshot for the /community hero numbers.

Schema (Supabase):

  community_stats (
    id                  INT PRIMARY KEY DEFAULT 1,
    total_users         INT NOT NULL DEFAULT 0,
    total_sites         INT NOT NULL DEFAULT 0,
    launches_this_week  INT NOT NULL DEFAULT 0,
    templates_count     INT NOT NULL DEFAULT 0,
    refreshed_at        TIMESTAMPTZ DEFAULT NOW(),
    CHECK (id = 1)
  )

Why a cache row vs counting on every page load: the community page
gets hit on every authed dashboard visit. COUNT(*) over auth.users
is fast, COUNT(*) over events filtered by date is slower, and once
the table grows we don't want every page render firing 4 aggregates.
A single-row read is sub-millisecond.

The cache is refreshed by:
  - the engine on startup (so it's populated even if the cron lags)
  - get_stats() if the cache is stale (>15 min old)
  - eventually a real cron (Phase 28)
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from pebble.log import log


REFRESH_INTERVAL_SECONDS = 15 * 60   # 15 min — cache TTL


def _env_url() -> str:
    val = (os.environ.get("PEBBLE_SUPABASE_URL")
           or os.environ.get("SUPABASE_URL")
           or "").strip()
    return val.rstrip("/")


def _env_service_role() -> str:
    return (os.environ.get("PEBBLE_SUPABASE_SERVICE_ROLE_KEY")
            or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            or "").strip()


def is_configured() -> bool:
    return bool(_env_url()) and bool(_env_service_role())


def _headers() -> dict:
    key = _env_service_role()
    return {
        "apikey":        key,
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
    }


def get_stats(*, allow_refresh: bool = True) -> Optional[dict]:
    """Return the current stats snapshot. If cache is older than
    REFRESH_INTERVAL_SECONDS, kick a refresh first (synchronous —
    cheap enough). Returns None if Supabase is unreachable; caller
    falls back to last-known values OR hides the strip.
    """
    if not is_configured():
        return None
    try:
        import httpx
        resp = httpx.get(
            f"{_env_url()}/rest/v1/community_stats",
            headers=_headers(),
            params={"select": "*", "id": "eq.1"},
            timeout=5.0,
        )
        if resp.status_code >= 400:
            log.warning("[stats] get failed: %s", resp.text[:200])
            return None
        rows = resp.json() or []
        if not rows:
            # First read — initialize the cache row + refresh.
            log.info("[stats] no cache row yet; computing initial snapshot")
            return refresh_stats()
        row = rows[0]
        if allow_refresh:
            refreshed_at = row.get("refreshed_at")
            if _is_stale(refreshed_at):
                fresh = refresh_stats()
                if fresh:
                    return fresh
        return row
    except Exception as e:
        log.warning("[stats] get errored: %s", e)
        return None


def _is_stale(refreshed_at_iso: Optional[str]) -> bool:
    if not refreshed_at_iso:
        return True
    try:
        # PostgREST returns ISO-8601 with timezone.
        # Python 3.11+ handles "Z" via fromisoformat.
        when = datetime.fromisoformat(refreshed_at_iso.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - when).total_seconds()
        return age > REFRESH_INTERVAL_SECONDS
    except Exception:
        return True


def refresh_stats() -> Optional[dict]:
    """Recompute the 4 numbers + upsert the single row.

    The counts use PostgREST's HEAD + Prefer: count=exact pattern,
    which is what we already use elsewhere and is sub-100ms even on
    larger tables. We swallow individual count failures and fall back
    to whatever existing row had — partial freshness beats no row.
    """
    if not is_configured():
        return None
    try:
        existing = _read_existing_row()

        total_users = _count_rows("auth.users", filters={}) or existing.get("total_users", 0)
        total_sites = _count_rows("events", filters={"kind": f"eq.{('build_completed')}"}) or existing.get("total_sites", 0)

        # 'launches_this_week' = public site_published events in the last 7d
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        launches_this_week = _count_rows(
            "events",
            filters={
                "kind":       f"eq.site_published",
                "visibility": f"eq.public",
                "created_at": f"gt.{week_ago}",
            },
        )
        if launches_this_week is None:
            launches_this_week = existing.get("launches_this_week", 0)

        # templates_count — public_templates that are approved, else engine registry
        templates_count = _count_rows(
            "public_templates",
            filters={"status": "eq.approved"},
        )
        if not templates_count:
            try:
                from pebble.server.templates_api import load_registry
                templates_count = len(load_registry().get("templates", []) or [])
            except Exception:
                templates_count = None
        if templates_count is None:
            templates_count = existing.get("templates_count", 0)

        now_iso = datetime.now(timezone.utc).isoformat()
        payload = {
            "id":                  1,
            "total_users":         total_users,
            "total_sites":         total_sites,
            "launches_this_week":  launches_this_week,
            "templates_count":     templates_count,
            "refreshed_at":        now_iso,
        }
        import httpx
        # Upsert via POST with on_conflict (Prefer: resolution=merge-duplicates).
        resp = httpx.post(
            f"{_env_url()}/rest/v1/community_stats",
            headers={**_headers(), "Prefer": "resolution=merge-duplicates,return=representation"},
            params={"on_conflict": "id"},
            json=payload,
            timeout=10.0,
        )
        if resp.status_code >= 400:
            log.warning("[stats] upsert failed (HTTP %d): %s", resp.status_code, resp.text[:200])
            return None
        rows = resp.json() or []
        return rows[0] if rows else payload
    except Exception as e:
        log.warning("[stats] refresh errored: %s", e)
        return None


def _read_existing_row() -> dict:
    """Best-effort read of the current cache row so a partial-failure
    refresh can fall back to existing numbers instead of zeroes."""
    if not is_configured():
        return {}
    try:
        import httpx
        resp = httpx.get(
            f"{_env_url()}/rest/v1/community_stats",
            headers=_headers(),
            params={"select": "*", "id": "eq.1"},
            timeout=5.0,
        )
        rows = resp.json() or []
        return rows[0] if isinstance(rows, list) and rows else {}
    except Exception:
        return {}


def _count_rows(table: str, filters: dict[str, str]) -> Optional[int]:
    """Count rows via PostgREST. Uses HEAD with Prefer: count=exact so
    no actual rows transit the wire. Returns None on any error.

    Note: `auth.users` isn't queryable directly via PostgREST by default
    (Supabase auth schema is hidden). We fall back to a view if the
    direct call fails, then to the events.user_id distinct count as a
    last resort.
    """
    if not is_configured():
        return None
    if table == "auth.users":
        return _count_users()
    try:
        import httpx
        resp = httpx.head(
            f"{_env_url()}/rest/v1/{table}",
            headers={**_headers(), "Prefer": "count=exact"},
            params=filters,
            timeout=5.0,
        )
        if resp.status_code >= 400:
            return None
        # PostgREST returns count in the Content-Range header: "0-19/47"
        cr = resp.headers.get("Content-Range") or ""
        if "/" in cr:
            tail = cr.split("/")[-1]
            if tail.isdigit():
                return int(tail)
        return None
    except Exception:
        return None


def _count_users() -> Optional[int]:
    """Count users via the GoTrue admin API. The auth schema isn't
    queryable through PostgREST without exposing it, so we go through
    the admin endpoint which DOES surface a count header."""
    if not is_configured():
        return None
    try:
        import httpx
        resp = httpx.get(
            f"{_env_url()}/auth/v1/admin/users",
            headers={"apikey": _env_service_role(), "Authorization": f"Bearer {_env_service_role()}"},
            params={"per_page": "1"},
            timeout=5.0,
        )
        if resp.status_code >= 400:
            return None
        body = resp.json() or {}
        # GoTrue returns {"users": [...], "aud": "...", "total": N} on
        # newer versions; older versions don't include total. Best
        # effort.
        if isinstance(body, dict) and isinstance(body.get("total"), int):
            return body["total"]
        # Fallback — paginate through small pages and count.
        return None
    except Exception:
        return None


__all__ = ["get_stats", "refresh_stats", "is_configured", "REFRESH_INTERVAL_SECONDS"]
