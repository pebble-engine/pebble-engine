"""Project listing, version history, rollback, and star endpoints.

Tiny handlers — most of the work is in :mod:`pebble.history`. This module
is responsible for I/O shape (JSON in/out, validation, error mapping).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import shutil
from pebble.engagement import log_event as _log_engagement
from pebble.history import list_history, restore_snapshot
from pebble.log import log
from pebble.security import (
    project_lock,
    require_project_owner,
    resolve_user_id,
    validate_snapshot_id,
)


def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


def _read_body(handler) -> Optional[dict]:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return None
    if length <= 0:
        return {}
    try:
        return json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return None


# --------- GET /api/projects ---------

def run_list_projects(handler) -> None:
    """List every project in output/ that the current user can see.

    - Signed-in users see their own projects (by ``_user_id``) plus
      unclaimed projects (no ``_user_id``). Unclaimed = anything built
      before auth was added; they remain visible so the user doesn't
      lose access on first login.
    - Signed-out users → 401.

    Phase 58e (2026-05-22) — previously fell back to "show all projects"
    when no user could be resolved. That was a leak in two ways: anon
    callers saw every project's slug + business_name + inbox counts,
    AND signed-in v3 users (Bearer JWT) were also treated as anon
    because the resolver only checked legacy cookies. Now uses the
    shared ``resolve_user_id`` (Bearer-first, cookie-fallback) and
    fails closed.
    """
    current_uid = resolve_user_id(handler)
    if not current_uid:
        handler._json(401, {"error": "sign in required"})
        return

    out = _output_dir()
    if not out.exists():
        handler._json(200, {"projects": [], "count": 0})
        return

    projects = []
    for project_dir in out.iterdir():
        if not project_dir.is_dir():
            continue
        # Skip non-project directories (research_cache, repair_history, etc.)
        # Heuristic: a project has a brief.json or site/ dir.
        brief_path = project_dir / "brief.json"
        site_dir = project_dir / "site"
        if not brief_path.exists() and not site_dir.exists():
            continue

        brief = {}
        if brief_path.exists():
            try:
                brief = json.loads(brief_path.read_text(encoding="utf-8"))
            except Exception:
                brief = {}

        # User-scope filter: when logged in, drop projects owned by someone
        # else. Unclaimed (no _user_id) stay visible.
        if current_uid:
            owner = brief.get("_user_id")
            if owner and owner != current_uid:
                continue

        meta_path = project_dir / "build_meta.json"
        built_at = None
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                built_at = meta.get("built_at")
            except Exception:
                pass

        # Starred state is a single zero-byte sentinel file. Simple, durable.
        starred = (project_dir / ".starred").exists()

        # File count under site/ — gives the UI something to show even
        # before a build_meta is written.
        file_count = 0
        if site_dir.exists():
            file_count = sum(1 for p in site_dir.rglob("*") if p.is_file())

        # Latest publish (zip or cloudflare) — drives the dashboard
        # "Published" badge. Tiny file, cheap to read per row.
        publish_summary = None
        pub_path = project_dir / "publish.json"
        if pub_path.exists():
            try:
                pub = json.loads(pub_path.read_text(encoding="utf-8"))
                publish_summary = {
                    "kind":         pub.get("kind"),
                    "url":          pub.get("url"),
                    "deployed_at":  pub.get("deployed_at"),
                }
            except Exception:
                pass

        # Custom domain — set when /api/projects/<slug>/domain has been
        # called and the domain has activated.
        domain = None
        domain_path = project_dir / "domain.json"
        if domain_path.exists():
            try:
                domain = json.loads(domain_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Inbox counts — small, useful for the dashboard card.
        inbox = None
        inbox_dir = project_dir / "inbox"
        if inbox_dir.exists():
            try:
                files = list(inbox_dir.glob("*.json"))
                unread = 0
                for p in files:
                    try:
                        rec = json.loads(p.read_text(encoding="utf-8"))
                        if not rec.get("read"):
                            unread += 1
                    except Exception:
                        unread += 1
                inbox = {"total": len(files), "unread": unread}
            except Exception:
                inbox = None

        projects.append({
            "slug":          project_dir.name,
            "business_name": brief.get("business_name", project_dir.name),
            "business_type": brief.get("business_type") or brief.get("industry"),
            "built_at":      built_at or _project_mtime(project_dir),
            "file_count":    file_count,
            "starred":       starred,
            "preview_url":   f"/preview/{project_dir.name}/",
            "design_dna":    brief.get("_design_dna"),
            "publish":       publish_summary,
            "domain":        domain,
            "inbox":         inbox,
        })

    # Newest first
    projects.sort(key=lambda p: p.get("built_at") or "", reverse=True)
    handler._json(200, {"projects": projects, "count": len(projects)})


def _project_mtime(project_dir: Path) -> str:
    """Fall back to filesystem mtime when build_meta is missing."""
    try:
        return datetime.fromtimestamp(project_dir.stat().st_mtime, tz=timezone.utc).isoformat()
    except Exception:
        return ""


# --------- GET /api/activity ---------

def run_activity_feed(handler) -> None:
    """Aggregate recent snapshots across every project visible to the
    current user. Powers the dashboard "Recently changed" widget.

    Each row: ``{slug, business_name, snapshot_id, reason, source,
    written_at, files_count}``. Newest first, capped at 30 entries.

    Auth: signed-in only. Returns 401 when no session is present —
    the dashboard widget only loads for logged-in users, and we don't
    want to leak global activity to anonymous callers.
    """
    # Resolve current user. Signed-out callers get 401 — fall-through
    # to "all projects" was a leak NotebookLM caught in review.
    # Phase 58e (2026-05-22) — switched from current_user_id (legacy
    # cookie only) to resolve_user_id (Bearer JWT first, then cookie)
    # so v3 Supabase-authed callers actually get their own activity
    # instead of being treated as anon.
    current_uid = resolve_user_id(handler)
    if not current_uid:
        handler._json(401, {"error": "sign in required"})
        return

    out = _output_dir()
    if not out.exists():
        handler._json(200, {"activity": [], "count": 0})
        return

    rows: list[dict] = []
    for project_dir in out.iterdir():
        if not project_dir.is_dir():
            continue
        # Skip non-project directories
        brief_path = project_dir / "brief.json"
        if not brief_path.exists() and not (project_dir / "site").exists():
            continue

        brief = {}
        if brief_path.exists():
            try:
                brief = json.loads(brief_path.read_text(encoding="utf-8"))
            except Exception:
                brief = {}

        # User-scope filter — owner must match; unclaimed projects are
        # visible to any signed-in user (consistent with list_projects).
        owner = brief.get("_user_id")
        if owner and owner != current_uid:
            continue

        business_name = brief.get("business_name", project_dir.name)

        for entry in list_history(project_dir.name):
            rows.append({
                "slug":          project_dir.name,
                "business_name": business_name,
                "snapshot_id":   entry.snapshot_id,
                "reason":        entry.reason,
                "source":        entry.source,
                "written_at":    entry.written_at,
                "files_count":   entry.files_count,
            })

    rows.sort(key=lambda r: r.get("written_at") or "", reverse=True)
    rows = rows[:30]
    handler._json(200, {"activity": rows, "count": len(rows)})


# --------- GET /api/projects/<slug>/history ---------

def run_get_history(handler, slug: str) -> None:
    """List every snapshot for a project, newest first. 404 if the project
    doesn't exist; empty list (with 200) if it exists but has no snapshots.

    Auth: gated through require_project_owner since the snapshot reasons
    can leak which refinements / visual-edits another user has run. The
    2026-05-15 evening NLM pass flagged this alongside refine/visual-edit
    as cross-user information leaks.
    """
    if require_project_owner(handler, slug) is None:
        return
    entries = list_history(slug)
    handler._json(200, {
        "slug":      slug,
        "snapshots": [e.to_dict() for e in entries],
        "count":     len(entries),
    })


# --------- POST /api/rollback ---------

def run_rollback(handler) -> None:
    """Restore a snapshot. The pre-rollback state is also snapshotted so
    the rollback itself is undoable. Body: ``{ slug, snapshot_id }``.

    Auth: gated through require_project_owner. Rolling back another
    user's project was a Tier-1 finding in the 2026-05-15 evening NLM
    pass — it lets a malicious peer revert someone's recent edits.
    """
    body = _read_body(handler)
    if body is None:
        return
    slug = (body or {}).get("slug")
    snapshot_id = (body or {}).get("snapshot_id")
    if not isinstance(slug, str) or not slug:
        handler._json(400, {"error": "slug is required"}); return
    if not isinstance(snapshot_id, str) or not snapshot_id:
        handler._json(400, {"error": "snapshot_id is required"}); return

    if require_project_owner(handler, slug) is None:
        return

    # snapshot_id reaches the filesystem via restore_snapshot — pin its
    # shape so it can't contain path-traversal segments either.
    if not validate_snapshot_id(handler, snapshot_id):
        return

    with project_lock(slug) as got_lock:
        if not got_lock:
            handler._json(409, {"error": "another change is in progress; try again in a moment"})
            return

        try:
            files = restore_snapshot(slug, snapshot_id)
        except FileNotFoundError as e:
            handler._json(404, {"error": str(e)}); return
        except Exception as e:
            log.warning("rollback failed: %s", e)
            handler._json(500, {"error": f"rollback failed: {e}"}); return

    handler._json(200, {
        "slug":        slug,
        "snapshot_id": snapshot_id,
        "files_restored": files,
    })


# --------- POST /api/projects/<slug>/star ---------

def run_toggle_star(handler, slug: str) -> None:
    """Toggle the starred sentinel file for a project. Idempotent on the
    requested state if the body specifies one.

    Auth: gated through require_project_owner so a user can't star/unstar
    another user's project to leak ownership signals via timing.
    """
    caller_uid = require_project_owner(handler, slug)
    if caller_uid is None:
        return
    body = _read_body(handler) or {}
    project_dir = _output_dir() / slug
    star_file = project_dir / ".starred"

    # Allow caller to force a state via {"starred": true/false}; if absent, toggle.
    requested = body.get("starred")
    if isinstance(requested, bool):
        new_state = requested
    else:
        new_state = not star_file.exists()

    if new_state:
        try: star_file.touch()
        except Exception as e:
            handler._json(500, {"error": f"could not star: {e}"}); return
    else:
        try: star_file.unlink()
        except FileNotFoundError: pass
        except Exception as e:
            handler._json(500, {"error": f"could not unstar: {e}"}); return

    handler._json(200, {"slug": slug, "starred": new_state})
    # Per-user engagement signal (T17). Single event for both star + unstar —
    # the bucketing cares about variety not direction.
    _log_engagement(caller_uid, "project_starred")


# --------- GET /api/usage ---------

def run_usage_summary(handler) -> None:
    """Aggregate cost telemetry across the caller's projects for a
    dashboard "this period: $X" indicator.

    Sums tokens_used and estimated_cost_usd from build_meta.json across
    the caller's project directories. Refinement and visual-edit calls
    don't yet write their own meta files (they only update billable in
    their HTTP response), so this is generation-only for now.

    Auth (Phase 58e, 2026-05-22): the endpoint used to aggregate every
    project in output/ regardless of caller — anyone hitting /api/usage
    saw every user's slugs + token counts + cost. Now requires a valid
    user (Bearer JWT or legacy cookie) and scopes the aggregation to
    that user's own + unclaimed projects (matching the dashboard
    listing rules).

    Response::

        {
          "projects":              N,
          "total_input_tokens":    int,
          "total_output_tokens":   int,
          "total_estimated_cost_usd": float,
          "by_project": [
            { slug, built_at, input_tokens, output_tokens, estimated_cost_usd, billable }
          ]
        }
    """
    current_uid = resolve_user_id(handler)
    if not current_uid:
        handler._json(401, {"error": "sign in required"})
        return

    out = _output_dir()
    if not out.exists():
        handler._json(200, {
            "projects": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_estimated_cost_usd": 0.0,
            "by_project": [],
        }); return

    total_in = 0
    total_out = 0
    total_cost = 0.0
    rows: list[dict] = []
    for project_dir in out.iterdir():
        if not project_dir.is_dir():
            continue
        # User-scope filter — owner must match or be unclaimed
        # (consistent with list_projects + activity_feed).
        brief_path = project_dir / "brief.json"
        if brief_path.exists():
            try:
                brief = json.loads(brief_path.read_text(encoding="utf-8"))
            except Exception:
                brief = {}
            owner = brief.get("_user_id")
            if owner and owner != current_uid:
                continue
        meta_path = project_dir / "build_meta.json"
        if not meta_path.exists():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        tokens = meta.get("tokens_used") or {}
        in_tok = int(tokens.get("input", 0) or 0)
        out_tok = int(tokens.get("output", 0) or 0)
        cost = float(meta.get("estimated_cost_usd", 0) or 0)
        billable = bool(meta.get("billable", True))
        total_in += in_tok
        total_out += out_tok
        total_cost += cost
        rows.append({
            "slug":               project_dir.name,
            "built_at":           meta.get("built_at"),
            "input_tokens":       in_tok,
            "output_tokens":      out_tok,
            "estimated_cost_usd": round(cost, 6),
            "billable":           billable,
            "model":              meta.get("model"),
        })
    rows.sort(key=lambda r: r.get("built_at") or "", reverse=True)
    handler._json(200, {
        "projects":                  len(rows),
        "total_input_tokens":        total_in,
        "total_output_tokens":       total_out,
        "total_estimated_cost_usd":  round(total_cost, 6),
        "by_project":                rows,
    })


# --------- DELETE /api/projects/<slug> ---------

def run_delete_project(handler, slug: str) -> None:
    """Permanently delete a project directory (and its full history).

    Hard delete — no undo, no trash. Frontend should confirm before
    calling. Auth: gated through require_project_owner so a user can't
    delete another user's project by guessing the slug.
    """
    # require_project_owner now validates the slug shape AND checks
    # ownership; the explicit traversal check below is preserved as a
    # belt-and-braces defense in case the gate is ever bypassed.
    caller_uid = require_project_owner(handler, slug)
    if caller_uid is None:
        return
    project_dir = _output_dir() / slug
    if not project_dir.exists() or not project_dir.is_dir():
        handler._json(404, {"error": f"project not found: {slug}"}); return
    if ".." in slug or "/" in slug or "\\" in slug:
        handler._json(400, {"error": "invalid slug"}); return
    try:
        shutil.rmtree(project_dir)
    except Exception as e:
        log.warning("delete failed: %s", e)
        handler._json(500, {"error": f"delete failed: {e}"}); return
    handler._json(200, {"slug": slug, "deleted": True})
    # Per-user engagement signal (T17).
    _log_engagement(caller_uid, "project_deleted")


# --------- POST /api/projects/<slug>/claim ---------

def run_claim_project(handler, slug: str) -> None:
    """Attach an anonymous build to the caller's user account.

    Inverted-onboarding pattern (#3 of the Onboarding Pattern Cheat
    Sheet): a visitor can run the questionnaire and see a generated site
    without signing up. When they decide to keep it, signup happens; the
    UI then calls this endpoint with the build's slug. The endpoint
    stamps ``_user_id`` onto the build's ``brief.json`` so it appears in
    the user's dashboard.

    Auth gates (via ``require_project_owner``):
    - 400 if slug fails shape validation (path-traversal guard)
    - 401 if not signed in
    - 404 if project doesn't exist
    - 403 if project is already owned by someone else
    - 200 if project is unowned (claimable) OR already owned by caller
      (idempotent — re-claim is a no-op).

    Side effects: rewrites ``brief.json`` atomically (write to tmp, then
    ``os.replace``) so a crash mid-claim leaves the file readable in
    either the old or new state, never half-written. Preserves every
    other field in the brief.
    """
    import os
    import tempfile

    caller_uid = require_project_owner(handler, slug)
    if caller_uid is None:
        return  # require_project_owner already wrote the response

    brief_path = _output_dir() / slug / "brief.json"
    if not brief_path.exists():
        # Project dir exists (require_project_owner checked) but no brief.json.
        # Unusual state; treat as not-claimable.
        handler._json(404, {"error": "brief.json missing — cannot claim"}); return

    try:
        brief = json.loads(brief_path.read_text(encoding="utf-8"))
    except Exception as e:
        log.warning("claim: brief.json parse failed for %s: %s", slug, e)
        handler._json(500, {"error": "could not read brief.json"}); return
    if not isinstance(brief, dict):
        handler._json(500, {"error": "brief.json is not a JSON object"}); return

    already_owned = brief.get("_user_id") == caller_uid
    brief["_user_id"] = caller_uid

    # Atomic write — tmp in same directory (same filesystem) then replace.
    # Prevents readers from ever seeing a half-written brief.json.
    tmp_fd, tmp_name = tempfile.mkstemp(
        prefix=".brief.", suffix=".tmp", dir=str(brief_path.parent)
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(brief, f, indent=2)
        os.replace(tmp_name, brief_path)
    except Exception as e:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        log.warning("claim: atomic write failed for %s: %s", slug, e)
        handler._json(500, {"error": "claim write failed"}); return

    handler._json(200, {
        "slug":            slug,
        "claimed":         True,
        "already_owned":   already_owned,
    })
    if not already_owned:
        _log_engagement(caller_uid, "project_claimed")
