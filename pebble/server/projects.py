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
from pebble.history import list_history, restore_snapshot
from pebble.log import log


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

    - Logged-in users see their own projects (by ``_user_id``) plus unclaimed
      projects (no ``_user_id``). Unclaimed = anything built before auth was
      added; they remain visible so the user doesn't lose access on first
      login.
    - Logged-out users see all projects (legacy behavior).
    """
    # Resolve current user once. Failure to import auth is tolerated so the
    # endpoint stays usable in environments without the auth module loaded.
    current_uid: Optional[str] = None
    try:
        from pebble.server.auth import current_user_id
        current_uid = current_user_id(handler)
    except Exception:
        current_uid = None

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


# --------- GET /api/projects/<slug>/history ---------

def run_get_history(handler, slug: str) -> None:
    """List every snapshot for a project, newest first. 404 if the project
    doesn't exist; empty list (with 200) if it exists but has no snapshots."""
    project_dir = _output_dir() / slug
    if not project_dir.exists():
        handler._json(404, {"error": f"project not found: {slug}"})
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
    the rollback itself is undoable. Body: ``{ slug, snapshot_id }``."""
    body = _read_body(handler)
    if body is None:
        return
    slug = (body or {}).get("slug")
    snapshot_id = (body or {}).get("snapshot_id")
    if not isinstance(slug, str) or not slug:
        handler._json(400, {"error": "slug is required"}); return
    if not isinstance(snapshot_id, str) or not snapshot_id:
        handler._json(400, {"error": "snapshot_id is required"}); return

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
    requested state if the body specifies one."""
    body = _read_body(handler) or {}
    project_dir = _output_dir() / slug
    if not project_dir.exists():
        handler._json(404, {"error": f"project not found: {slug}"}); return
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


# --------- GET /api/usage ---------

def run_usage_summary(handler) -> None:
    """Aggregate cost telemetry across every project for a dashboard
    "this period: $X" indicator.

    Sums tokens_used and estimated_cost_usd from build_meta.json across
    every project directory. Refinement and visual-edit calls don't
    yet write their own meta files (they only update billable in their
    HTTP response), so this is generation-only for now.

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
    calling. If the project doesn't exist, returns 404 so the UI can
    update its state to match reality.
    """
    project_dir = _output_dir() / slug
    if not project_dir.exists() or not project_dir.is_dir():
        handler._json(404, {"error": f"project not found: {slug}"}); return
    # Path safety — the slug came from the URL, defensively reject parent
    # traversal even though the router should have neutralized it.
    if ".." in slug or "/" in slug or "\\" in slug:
        handler._json(400, {"error": "invalid slug"}); return
    try:
        shutil.rmtree(project_dir)
    except Exception as e:
        log.warning("delete failed: %s", e)
        handler._json(500, {"error": f"delete failed: {e}"}); return
    handler._json(200, {"slug": slug, "deleted": True})
