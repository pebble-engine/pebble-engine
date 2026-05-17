"""Admin support tooling.

Read-only diagnostic endpoints for the support persona. Every endpoint
requires the caller's session to belong to an email listed in the
``PEBBLE_ADMIN_EMAIL`` env var (comma-separated). Unauthenticated callers
get 401; non-admin authenticated callers get 403.

Routes:

- GET /api/admin/users     — list every user with their project count
- GET /api/admin/projects  — list every project across all users
- GET /api/admin/errors    — tail of recent error lines from engine.err.log
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pebble.log import log


# --------- Path helpers ----------------------------------------------------

def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


def _project_root() -> Path:
    eng = _engine()
    if hasattr(eng, "PROJECT_ROOT"):
        return Path(getattr(eng, "PROJECT_ROOT"))
    return Path(__file__).parent.parent.parent.resolve()


# --------- Authorization ---------------------------------------------------

def admin_emails() -> set[str]:
    """Resolve the admin allow-list from env. Empty set = admin disabled."""
    raw = os.environ.get("PEBBLE_ADMIN_EMAIL", "") or ""
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


def _require_admin(handler) -> Optional[str]:
    """Return the admin's email on success; respond + return None on failure.

    401 for un-signed-in callers, 403 for signed-in non-admins, 503 when
    no admins are configured (so the support surface defaults closed).
    """
    allow = admin_emails()
    if not allow:
        handler._json(503, {"error": "Admin tools disabled. Set PEBBLE_ADMIN_EMAIL in .env."})
        return None
    try:
        from pebble.server.auth import current_user_id
        from pebble.auth import find_user_by_id
    except Exception:
        handler._json(500, {"error": "auth subsystem unavailable"}); return None

    uid = current_user_id(handler)
    if not uid:
        handler._json(401, {"error": "sign in required"}); return None
    user = find_user_by_id(uid)
    if not user:
        handler._json(401, {"error": "sign in required"}); return None
    if user.email.lower() not in allow:
        handler._json(403, {"error": "not authorized"}); return None
    return user.email


# --------- GET /api/admin/users -------------------------------------------

def run_list_users(handler) -> None:
    if _require_admin(handler) is None:
        return

    users_dir = _output_dir() / ".users"
    if not users_dir.exists():
        handler._json(200, {"users": [], "count": 0})
        return

    # Pre-count projects per user_id
    project_counts: dict[str, int] = {}
    out = _output_dir()
    if out.exists():
        for project_dir in out.iterdir():
            if not project_dir.is_dir():
                continue
            brief_path = project_dir / "brief.json"
            if not brief_path.exists():
                continue
            try:
                brief = json.loads(brief_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            uid = brief.get("_user_id")
            if uid:
                project_counts[uid] = project_counts.get(uid, 0) + 1

    rows: list[dict] = []
    for user_file in users_dir.glob("*.json"):
        if user_file.name == "_email_index.json":
            continue
        try:
            data = json.loads(user_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        rows.append({
            "id":            data.get("id"),
            "email":         data.get("email"),
            "created_at":    data.get("created_at"),
            "project_count": project_counts.get(data.get("id", ""), 0),
        })
    rows.sort(key=lambda r: r.get("created_at") or "", reverse=True)
    handler._json(200, {"users": rows, "count": len(rows)})


# --------- GET /api/admin/projects ----------------------------------------

def run_list_all_projects(handler) -> None:
    if _require_admin(handler) is None:
        return

    out = _output_dir()
    if not out.exists():
        handler._json(200, {"projects": [], "count": 0})
        return

    # user_id → email lookup (for joins)
    uid_to_email: dict[str, str] = {}
    users_dir = out / ".users"
    if users_dir.exists():
        for f in users_dir.glob("*.json"):
            if f.name == "_email_index.json":
                continue
            try:
                u = json.loads(f.read_text(encoding="utf-8"))
                uid_to_email[u.get("id", "")] = u.get("email", "")
            except Exception:
                continue

    rows: list[dict] = []
    for project_dir in out.iterdir():
        if not project_dir.is_dir():
            continue
        brief_path = project_dir / "brief.json"
        site_dir = project_dir / "site"
        if not brief_path.exists() and not site_dir.exists():
            continue

        brief: dict = {}
        if brief_path.exists():
            try:
                brief = json.loads(brief_path.read_text(encoding="utf-8"))
            except Exception:
                brief = {}

        user_id = brief.get("_user_id", "")

        # Latest build_meta gives cost / built_at
        built_at = None
        cost = 0.0
        meta_path = project_dir / "build_meta.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                built_at = meta.get("built_at")
                cost = float(meta.get("estimated_cost_usd", 0) or 0)
            except Exception:
                pass

        # Publish state
        publish = None
        pub_path = project_dir / "publish.json"
        if pub_path.exists():
            try:
                publish = json.loads(pub_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Domain state
        domain = None
        dom_path = project_dir / "domain.json"
        if dom_path.exists():
            try:
                domain = json.loads(dom_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        rows.append({
            "slug":               project_dir.name,
            "business_name":      brief.get("business_name", project_dir.name),
            "business_type":      brief.get("business_type"),
            "user_id":            user_id,
            "user_email":         uid_to_email.get(user_id, ""),
            "built_at":           built_at,
            "estimated_cost_usd": round(cost, 6),
            "publish":            publish,
            "domain":             domain,
        })
    rows.sort(key=lambda r: r.get("built_at") or "", reverse=True)
    handler._json(200, {"projects": rows, "count": len(rows)})


# --------- GET /api/admin/errors ------------------------------------------

def _read_tail(path: Path, max_lines: int = 200) -> list[str]:
    """Return the last ``max_lines`` lines of ``path``."""
    if not path.exists():
        return []
    try:
        with path.open("rb") as f:
            # Read up to 256KB from the end — plenty for 200 lines.
            try:
                f.seek(0, 2)
                size = f.tell()
                read_from = max(0, size - 256 * 1024)
                f.seek(read_from)
                data = f.read().decode("utf-8", errors="replace")
            except Exception:
                f.seek(0)
                data = f.read().decode("utf-8", errors="replace")
    except Exception:
        return []
    lines = data.splitlines()
    return lines[-max_lines:]


def run_recent_errors(handler) -> None:
    if _require_admin(handler) is None:
        return

    root = _project_root()
    candidates = [
        root / "engine.err.log",
        root / "engine.log",
    ]
    seen: list[dict] = []
    for path in candidates:
        if not path.exists():
            continue
        tail = _read_tail(path, max_lines=200)
        # Trim to lines that look like errors/warnings — heuristic, defensive.
        for line in tail:
            up = line.upper()
            if any(k in up for k in ("ERROR", "WARN", "TRACEBACK", "EXCEPTION", "FAIL")):
                seen.append({"file": path.name, "line": line})
    # Newest at the end of the file → reverse so freshest first; cap total.
    seen.reverse()
    handler._json(200, {
        "errors":  seen[:120],
        "count":   len(seen[:120]),
        "checked": [p.name for p in candidates if p.exists()],
        "now":     datetime.now(timezone.utc).isoformat(),
    })


# --------- GET /api/admin/engagement --------------------------------------

def run_engagement_summary(handler) -> None:
    """User-engagement bucket summary (T17, 2026-05-17).

    Joins ``pebble.engagement.engagement_summary()`` with the users index
    so the admin UI shows email + score + activity counts in one shot.
    Returns ``power`` → ``active`` → ``at_risk`` ordering.

    Response::

        {
          "users": [
            {
              "user_id": "...", "email": "...", "score": "power",
              "distinct_events": 7, "total_events": 42
            }
          ],
          "count": N,
          "now": "2026-05-17T..."
        }
    """
    if _require_admin(handler) is None:
        return

    try:
        from pebble.engagement import engagement_summary
    except Exception as e:
        handler._json(500, {"error": f"engagement module unavailable: {e}"}); return

    # Build the uid → email map the same way run_list_all_projects does.
    uid_to_email: dict[str, str] = {}
    users_dir = _output_dir() / ".users"
    if users_dir.exists():
        for f in users_dir.glob("*.json"):
            if f.name == "_email_index.json":
                continue
            try:
                u = json.loads(f.read_text(encoding="utf-8"))
                uid_to_email[u.get("id", "")] = u.get("email", "")
            except Exception:
                continue

    rows = engagement_summary()
    for row in rows:
        row["email"] = uid_to_email.get(row["user_id"], "")
    handler._json(200, {
        "users":   rows,
        "count":   len(rows),
        "now":     datetime.now(timezone.utc).isoformat(),
    })
