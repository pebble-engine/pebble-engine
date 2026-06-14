"""Launchpad — public showcase submissions in Supabase.

Table: ``public_templates`` (see ``supabase/migrations/010_launchpad.sql``).

v1 auto-approves on submit so the gallery fills without a moderation
queue. Fail-soft like ``pebble.events`` — callers get None / [] on outage.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Optional

from pebble.log import log

STATUS_APPROVED = "approved"
STATUS_PENDING = "pending"
STATUS_REJECTED = "rejected"


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


def _headers(*, prefer: str = "return=representation") -> dict:
    key = _env_service_role()
    return {
        "apikey":        key,
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
        "Prefer":        prefer,
    }


def list_approved(*, limit: int = 24) -> list[dict]:
    """Approved showcase rows, newest first."""
    if not is_configured():
        return []
    try:
        import httpx
        resp = httpx.get(
            f"{_env_url()}/rest/v1/public_templates",
            headers=_headers(),
            params={
                "select":       "id,slug,business_name,industry,tagline,url,submitted_at,meta",
                "status":       f"eq.{STATUS_APPROVED}",
                "order":        "submitted_at.desc",
                "limit":        str(limit),
            },
            timeout=5.0,
        )
        if resp.status_code >= 400:
            log.warning("[launchpad] list failed: %s", resp.text[:200])
            return []
        rows = resp.json() or []
        return [r for r in rows if isinstance(r, dict)]
    except Exception as e:
        log.warning("[launchpad] list errored: %s", e)
        return []


def get_by_slug(slug: str) -> Optional[dict]:
    if not is_configured() or not slug:
        return None
    try:
        import httpx
        resp = httpx.get(
            f"{_env_url()}/rest/v1/public_templates",
            headers=_headers(),
            params={
                "select": "*",
                "slug":   f"eq.{slug}",
                "limit":  "1",
            },
            timeout=5.0,
        )
        if resp.status_code >= 400:
            return None
        rows = resp.json() or []
        return rows[0] if rows else None
    except Exception as e:
        log.warning("[launchpad] get_by_slug errored: %s", e)
        return None


def submit(
    user_id: str,
    slug: str,
    *,
    business_name: str,
    industry: Optional[str] = None,
    tagline: Optional[str] = None,
    url: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
) -> Optional[dict]:
    """Upsert a showcase row. v1 auto-approves immediately."""
    if not is_configured() or not user_id or not slug:
        return None
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "user_id":       user_id,
        "slug":          slug,
        "business_name": business_name[:200],
        "industry":      (industry or "")[:120] or None,
        "tagline":       (tagline or "")[:280] or None,
        "url":           (url or "")[:500] or None,
        "status":        STATUS_APPROVED,
        "submitted_at":  now,
        "approved_at":   now,
        "meta":          meta or None,
    }
    try:
        import httpx
        resp = httpx.post(
            f"{_env_url()}/rest/v1/public_templates",
            headers=_headers(prefer="resolution=merge-duplicates,return=representation"),
            params={"on_conflict": "slug"},
            json=payload,
            timeout=8.0,
        )
        if resp.status_code >= 400:
            log.warning("[launchpad] submit failed (HTTP %d): %s", resp.status_code, resp.text[:200])
            return None
        rows = resp.json() or []
        return rows[0] if rows else payload
    except Exception as e:
        log.warning("[launchpad] submit errored: %s", e)
        return None


def withdraw(user_id: str, slug: str) -> bool:
    """Remove a submission. Only the owner row is deleted."""
    if not is_configured() or not user_id or not slug:
        return False
    try:
        import httpx
        resp = httpx.delete(
            f"{_env_url()}/rest/v1/public_templates",
            headers=_headers(prefer="return=minimal"),
            params={
                "slug":    f"eq.{slug}",
                "user_id": f"eq.{user_id}",
            },
            timeout=5.0,
        )
        return resp.status_code in (200, 204)
    except Exception as e:
        log.warning("[launchpad] withdraw errored: %s", e)
        return False


__all__ = [
    "is_configured",
    "list_approved",
    "get_by_slug",
    "submit",
    "withdraw",
    "STATUS_APPROVED",
]
