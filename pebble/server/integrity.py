"""Build Integrity endpoint — Phase 36 (2026-05-21).

GET  /api/projects/<slug>/integrity   → run the curated 10-check suite,
                                         return list of {id, label, status,
                                         message, must_pass} + a publishable
                                         flag.

Owner-gated like other /api/projects/<slug>/* routes. Read-only — never
mutates state; just runs the existing eval functions and returns results.
"""
from __future__ import annotations

from pebble.integrity import is_publishable, run_integrity
from pebble.log import log
from pebble.security import require_project_owner


def run_integrity_check(handler, slug: str) -> None:
    """GET /api/projects/<slug>/integrity"""
    if not require_project_owner(handler, slug):
        # require_project_owner has already written the 401/403/404 response.
        return

    try:
        results = run_integrity(slug)
    except Exception as e:
        log.error("[integrity] %s: unexpected: %s", slug, e)
        handler._json(500, {"error": "integrity check failed unexpectedly"})
        return

    if results is None:
        handler._json(404, {"error": f"build not found: {slug}"})
        return

    handler._json(200, {
        "slug":        slug,
        "results":     [r.to_dict() for r in results],
        "publishable": is_publishable(results),
        "passed":      sum(1 for r in results if r.status == "pass"),
        "total":       len(results),
    })
