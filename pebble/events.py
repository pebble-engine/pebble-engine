"""Events — single source of truth for notifications + community feed.

Schema (in Supabase, see migrations/2026-05-24_events_credits_marketplace.sql):

  events (
    id          UUID PRIMARY KEY,
    user_id     UUID REFERENCES auth.users(id),
    kind        TEXT NOT NULL,    -- 'build_completed', 'site_published', etc.
    visibility  TEXT NOT NULL,    -- 'private' (bell only) / 'public' (community feed)
    title       TEXT NOT NULL,
    body        TEXT,
    meta        JSONB,
    created_at  TIMESTAMPTZ DEFAULT NOW()
  )

  notification_reads (
    user_id   UUID,
    event_id  UUID,
    read_at   TIMESTAMPTZ,
    PRIMARY KEY (user_id, event_id)
  )

Why a single events table for two use-cases (notifications + community
feed): the data is identical in shape (who did what when), the only
difference is who should see it. Splitting into two tables would mean
duplicate writes whenever a public-facing action also triggers a
personal notification (most of them).

This module is fail-soft: every helper returns None / [] on any
Supabase / network error, so a Supabase outage degrades to a quiet
notification bell rather than a 500 on every page. Errors are logged
but never raised at the caller.
"""
from __future__ import annotations

import json
import os
from typing import Any, Optional

from pebble.log import log


# ─── Env + base config ────────────────────────────────────────────── #

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
        # Tell PostgREST to return the inserted row (or row count).
        "Prefer":        "return=representation",
    }


# ─── Valid kinds + visibility ─────────────────────────────────────── #
#
# Pinning these as Python constants gives the engine + the test suite
# a single place to look when something asks "what events can fire".

KIND_BUILD_COMPLETED   = "build_completed"
KIND_SITE_PUBLISHED    = "site_published"
KIND_TEMPLATE_USED     = "template_used"
KIND_TEMPLATE_SUBMITTED = "template_submitted"
KIND_JOINED_PEBBLE     = "joined_pebble"
KIND_REFINEMENT_MADE   = "refinement_made"
KIND_TIP               = "tip"
KIND_WELCOME           = "welcome"

VALID_KINDS = {
    KIND_BUILD_COMPLETED, KIND_SITE_PUBLISHED, KIND_TEMPLATE_USED,
    KIND_TEMPLATE_SUBMITTED, KIND_JOINED_PEBBLE, KIND_REFINEMENT_MADE,
    KIND_TIP, KIND_WELCOME,
}

VISIBILITY_PRIVATE = "private"   # bell only — the user that owns it
VISIBILITY_PUBLIC  = "public"    # community feed — everyone


# ─── Core helpers ─────────────────────────────────────────────────── #


def record(
    user_id: Optional[str],
    kind: str,
    *,
    title: str,
    body: Optional[str] = None,
    visibility: str = VISIBILITY_PRIVATE,
    meta: Optional[dict[str, Any]] = None,
) -> Optional[dict]:
    """Insert one row into the events table.

    Args:
      user_id:    Supabase auth.users.id. May be None for system-wide
                  events (e.g. a 'tip' that's public for everyone).
                  Required for any private notification.
      kind:       One of VALID_KINDS. Logged + skipped if unrecognized.
      title:      Short human label shown in the bell or feed row.
      body:       Optional longer body (1-2 sentences).
      visibility: 'private' (default, bell only) or 'public' (community feed).
      meta:       Optional JSONB metadata (slug, template_id, etc.).

    Returns the inserted row dict on success, or None on any failure.
    Never raises — this is fire-and-forget from build / publish flows.
    """
    if not is_configured():
        log.info("[events] Supabase not configured; skipping record()")
        return None
    if kind not in VALID_KINDS:
        log.warning("[events] unknown kind %r — skipping", kind)
        return None
    if visibility not in (VISIBILITY_PRIVATE, VISIBILITY_PUBLIC):
        log.warning("[events] invalid visibility %r — skipping", visibility)
        return None
    if visibility == VISIBILITY_PRIVATE and not user_id:
        log.warning("[events] private event needs user_id — skipping kind=%s", kind)
        return None

    payload = {
        "user_id":    user_id,
        "kind":       kind,
        "visibility": visibility,
        "title":      title[:200],          # column is TEXT but keep sensible
        "body":       (body or "")[:1000] or None,
        "meta":       meta or None,
    }

    try:
        import httpx
        resp = httpx.post(
            f"{_env_url()}/rest/v1/events",
            headers=_headers(),
            json=payload,
            timeout=5.0,
        )
        if resp.status_code >= 400:
            log.warning("[events] insert failed (HTTP %d): %s", resp.status_code, resp.text[:200])
            return None
        rows = resp.json()
        return rows[0] if isinstance(rows, list) and rows else None
    except Exception as e:
        log.warning("[events] insert errored: %s", e)
        return None


def list_user_unread(user_id: str, limit: int = 20) -> list[dict]:
    """All UNREAD private events for the user, newest first.

    PostgREST query: SELECT * FROM events WHERE user_id = X
                     AND visibility = 'private'
                     AND id NOT IN (SELECT event_id FROM notification_reads WHERE user_id = X)
                     ORDER BY created_at DESC LIMIT N

    PostgREST doesn't support NOT IN with a subquery directly, so we
    do two queries and filter client-side. Cheap for small N.
    """
    if not is_configured() or not user_id:
        return []
    try:
        import httpx
        # 1) All recent events for the user (private only). Cap at 100
        #    so a heavy-read account doesn't pull megabytes.
        events_resp = httpx.get(
            f"{_env_url()}/rest/v1/events",
            headers=_headers(),
            params={
                "select":      "id,kind,title,body,meta,created_at,visibility",
                "user_id":     f"eq.{user_id}",
                "visibility":  f"eq.{VISIBILITY_PRIVATE}",
                "order":       "created_at.desc",
                "limit":       "100",
            },
            timeout=5.0,
        )
        if events_resp.status_code >= 400:
            log.warning("[events] list user events failed: %s", events_resp.text[:200])
            return []
        events = events_resp.json() or []
        if not events:
            return []

        # 2) Which of those have a read row?
        event_ids = [e["id"] for e in events if isinstance(e, dict) and e.get("id")]
        if not event_ids:
            return []
        ids_filter = "(" + ",".join(event_ids) + ")"
        reads_resp = httpx.get(
            f"{_env_url()}/rest/v1/notification_reads",
            headers=_headers(),
            params={
                "select":   "event_id",
                "user_id":  f"eq.{user_id}",
                "event_id": f"in.{ids_filter}",
            },
            timeout=5.0,
        )
        read_ids: set[str] = set()
        if reads_resp.status_code < 400:
            for row in reads_resp.json() or []:
                if isinstance(row, dict) and row.get("event_id"):
                    read_ids.add(row["event_id"])

        unread = [e for e in events if e.get("id") not in read_ids]
        return unread[:limit]
    except Exception as e:
        log.warning("[events] list_user_unread errored: %s", e)
        return []


def list_user_all(user_id: str, limit: int = 20) -> list[dict]:
    """All private events for the user (read + unread), newest first.
    Used by the notification dropdown which shows both states.
    Returned rows have an extra `is_read` bool merged in."""
    if not is_configured() or not user_id:
        return []
    try:
        import httpx
        events_resp = httpx.get(
            f"{_env_url()}/rest/v1/events",
            headers=_headers(),
            params={
                "select":      "id,kind,title,body,meta,created_at,visibility",
                "user_id":     f"eq.{user_id}",
                "visibility":  f"eq.{VISIBILITY_PRIVATE}",
                "order":       "created_at.desc",
                "limit":       str(limit),
            },
            timeout=5.0,
        )
        if events_resp.status_code >= 400:
            return []
        events = events_resp.json() or []
        if not events:
            return []
        event_ids = [e["id"] for e in events if isinstance(e, dict) and e.get("id")]
        ids_filter = "(" + ",".join(event_ids) + ")"
        reads_resp = httpx.get(
            f"{_env_url()}/rest/v1/notification_reads",
            headers=_headers(),
            params={
                "select":   "event_id",
                "user_id":  f"eq.{user_id}",
                "event_id": f"in.{ids_filter}",
            },
            timeout=5.0,
        )
        read_ids: set[str] = set()
        if reads_resp.status_code < 400:
            for row in reads_resp.json() or []:
                if isinstance(row, dict) and row.get("event_id"):
                    read_ids.add(row["event_id"])
        for e in events:
            e["is_read"] = e.get("id") in read_ids
        return events
    except Exception as e:
        log.warning("[events] list_user_all errored: %s", e)
        return []


def list_public_recent(limit: int = 20, days: int = 7) -> list[dict]:
    """Recent public events for the community feed. Newest first.

    PostgREST: SELECT * FROM events WHERE visibility = 'public'
               AND created_at > NOW() - INTERVAL 'N days'
               ORDER BY created_at DESC LIMIT N
    """
    if not is_configured():
        return []
    try:
        from datetime import datetime, timedelta, timezone
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        import httpx
        resp = httpx.get(
            f"{_env_url()}/rest/v1/events",
            headers=_headers(),
            params={
                "select":      "id,kind,title,body,meta,created_at,user_id",
                "visibility":  f"eq.{VISIBILITY_PUBLIC}",
                "created_at":  f"gt.{cutoff}",
                "order":       "created_at.desc",
                "limit":       str(limit),
            },
            timeout=5.0,
        )
        if resp.status_code >= 400:
            log.warning("[events] list_public_recent failed: %s", resp.text[:200])
            return []
        return resp.json() or []
    except Exception as e:
        log.warning("[events] list_public_recent errored: %s", e)
        return []


def mark_read(user_id: str, event_id: str) -> bool:
    """Insert into notification_reads. Idempotent — duplicate inserts
    silently no-op via the table's PK (user_id, event_id)."""
    if not is_configured() or not user_id or not event_id:
        return False
    try:
        import httpx
        resp = httpx.post(
            f"{_env_url()}/rest/v1/notification_reads",
            headers={**_headers(), "Prefer": "resolution=ignore-duplicates"},
            json={"user_id": user_id, "event_id": event_id},
            timeout=5.0,
        )
        # 201 = inserted; 409 = already there (treat as success).
        return resp.status_code in (200, 201, 204, 409)
    except Exception as e:
        log.warning("[events] mark_read errored: %s", e)
        return False


def mark_all_read(user_id: str) -> int:
    """Mark every currently-unread event for the user as read.
    Returns the number of rows inserted (best-effort count)."""
    if not is_configured() or not user_id:
        return 0
    unread = list_user_unread(user_id, limit=100)
    count = 0
    for e in unread:
        if mark_read(user_id, e["id"]):
            count += 1
    return count


__all__ = [
    "record",
    "list_user_unread",
    "list_user_all",
    "list_public_recent",
    "mark_read",
    "mark_all_read",
    "is_configured",
    "VALID_KINDS",
    "VISIBILITY_PRIVATE",
    "VISIBILITY_PUBLIC",
    # Kind constants for callers
    "KIND_BUILD_COMPLETED",
    "KIND_SITE_PUBLISHED",
    "KIND_TEMPLATE_USED",
    "KIND_TEMPLATE_SUBMITTED",
    "KIND_JOINED_PEBBLE",
    "KIND_REFINEMENT_MADE",
    "KIND_TIP",
    "KIND_WELCOME",
]
