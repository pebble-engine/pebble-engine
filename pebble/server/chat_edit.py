"""POST /api/chat-edit — natural-language edit routing.

Phase 57 (2026-05-22). Takes a free-text instruction from the user
("make it more professional", "change the colors", etc.) and routes it
to the closest existing /api/refine action. If the instruction doesn't
match any known refinement, returns a 200 with a helpful suggestion
message rather than erroring.

Intentionally simple: no LLM call here. The routing is keyword-based.
A more sophisticated LLM-guided free-text edit is planned for Phase 57b.

Auth: owner-gated (requires Supabase session cookie) — identical to
/api/refine, which this delegates to once a refinement_id is resolved.
"""
from __future__ import annotations

import json
from typing import Optional

from pebble.log import log
from pebble.security import require_project_owner


# ---------------------------------------------------------------------------
# Keyword → refinement_id routing table
# ---------------------------------------------------------------------------

KEYWORD_MAP: dict[str, str] = {
    # tone
    "professional": "professional",
    "formal":       "professional",
    "corporate":    "professional",
    "friendly":     "friendlier",
    "friendlier":   "friendlier",
    "warm":         "friendlier",
    "casual":       "friendlier",
    "simple":       "simpler",
    "simpler":      "simpler",
    "minimal":      "simpler",
    "clean":        "simpler",
    # visual
    "color":        "colors",
    "palette":      "colors",
    "colours":      "colors",
    # booking
    "book":         "booking",
    "calendly":     "booking",
    "schedule":     "booking",
    "appointment":  "booking",
}

_NO_MATCH_SUGGESTION = (
    "I understand text instructions for: professional tone, friendlier tone, "
    "simpler layout, new color palette, or adding a booking button. "
    "Try one of those, or use the style chips below the preview."
)


def _resolve_refinement(message: str) -> Optional[str]:
    """Return the first matching refinement_id for *message*, or None.

    Matching is case-insensitive and word-boundary-free (substring search).
    Longer keywords are checked first so "appointment" beats "book" if both
    are present, providing slightly more specific routing.
    """
    lower = message.lower()
    # Sort by keyword length descending for more-specific-first matching.
    for keyword in sorted(KEYWORD_MAP, key=len, reverse=True):
        if keyword in lower:
            return KEYWORD_MAP[keyword]
    return None


# ---------------------------------------------------------------------------
# HTTP entry point
# ---------------------------------------------------------------------------

def run_chat_edit(handler) -> None:
    """POST /api/chat-edit.

    Request body::

        { "slug": "<slug>", "message": "<free-text instruction>" }

    On a keyword match: delegates to run_refine, which snapshots, applies the
    refinement, and returns the standard refine response shape.

    On no match: returns 200 with ``{ matched: false, suggestion: "...",
    billable: false }``.
    """
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return
    if length <= 0:
        handler._json(400, {"error": "empty request body"}); return
    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return

    slug = (body or {}).get("slug", "")
    message = (body or {}).get("message", "")

    if not isinstance(slug, str) or not slug:
        handler._json(400, {"error": "slug is required"}); return
    if not isinstance(message, str) or not message.strip():
        handler._json(400, {"error": "message is required"}); return

    # Auth gate — same as /api/refine (owner-gated).
    caller_uid = require_project_owner(handler, slug)
    if caller_uid is None:
        return

    refinement_id = _resolve_refinement(message)

    if refinement_id is None:
        log.info("chat-edit no-match for slug=%s message=%r", slug, message[:80])
        handler._json(200, {
            "matched":    False,
            "suggestion": _NO_MATCH_SUGGESTION,
            "billable":   False,
        })
        return

    # Re-inject the resolved refinement_id into the request so run_refine
    # can read it from body as usual.  run_refine re-reads Content-Length and
    # rfile — but rfile is already consumed.  Instead we call the internal
    # helper directly, bypassing the HTTP parsing layer.
    log.info("chat-edit matched slug=%s message=%r -> %s", slug, message[:80], refinement_id)

    # Import run_refine internals to invoke the refinement without going back
    # through HTTP parsing (rfile is already consumed).
    from pebble.server.refine import (
        DETERMINISTIC_REFINEMENTS,
        FREE_DETERMINISTIC_REFINEMENTS,
        LLM_REFINEMENTS,
        _run_llm_refinement,
    )
    import sys
    import time
    from datetime import datetime, timezone
    from pathlib import Path
    from pebble.history import snapshot_site, diff_against_snapshot
    from pebble.security import project_lock
    from pebble.engagement import log_event as _log_engagement
    from pebble.user_plan import (
        gate_response,
        get_user_plan,
        increment_usage,
        would_exceed_quota,
    )

    def _output_dir() -> Path:
        engine = sys.modules.get("pebble_engine") or sys.modules["__main__"]
        return engine.OUTPUT_DIR

    site_dir = _output_dir() / slug / "site"
    if not site_dir.exists():
        handler._json(404, {"error": f"project site not found: {slug}"}); return

    # Quota gate (mirrors run_refine exactly).
    will_bill = (
        refinement_id in LLM_REFINEMENTS or
        (refinement_id in DETERMINISTIC_REFINEMENTS and refinement_id not in FREE_DETERMINISTIC_REFINEMENTS)
    )
    if will_bill:
        exceeds, current, limit = would_exceed_quota(
            caller_uid, "ai_refinements", "ai_refinements_per_month",
        )
        if exceeds:
            handler._json(402, gate_response(
                feature_label="AI refinement",
                required_plan="starter",
                current_plan=get_user_plan(caller_uid),
                current=current,
                limit=limit,
            ))
            return

    with project_lock(slug) as got_lock:
        if not got_lock:
            handler._json(409, {"error": "another edit is already in progress; try again in a moment"})
            return

        snap = snapshot_site(slug, reason=f"chat-edit-{refinement_id}", source=f"POST /api/chat-edit -> {refinement_id}")
        snapshot_id = snap.name if snap else None

        t0 = time.time()
        if refinement_id in DETERMINISTIC_REFINEMENTS:
            try:
                result = DETERMINISTIC_REFINEMENTS[refinement_id](site_dir)
            except Exception as e:
                log.warning("chat-edit deterministic refinement failed: %s", e)
                handler._json(500, {"error": f"refinement failed: {e}"}); return
            kind = "deterministic"
            billable = refinement_id not in FREE_DETERMINISTIC_REFINEMENTS
        else:  # LLM_REFINEMENTS
            result = _run_llm_refinement(slug, refinement_id)
            if result.get("error"):
                handler._json(502, {"error": result["error"]}); return
            kind = "llm"
            billable = True

        elapsed = time.time() - t0

    diff_payload = None
    if snapshot_id:
        try:
            ds = diff_against_snapshot(slug, snapshot_id)
            if ds is not None:
                diff_payload = ds.to_dict()
        except Exception as _exc:
            log.warning("diff_against_snapshot failed (chat-edit %s): %s", refinement_id, _exc)

    refinement_count_after = None
    if billable:
        refinement_count_after = increment_usage(caller_uid, "ai_refinements")

    handler._json(200, {
        "matched":          True,
        "slug":             slug,
        "refinement_id":    refinement_id,
        "message":          message,
        "files_changed":    result.get("files_changed", []),
        "kind":             kind,
        "billable":         billable,
        "snapshot_id":      snapshot_id,
        "diff":             diff_payload,
        "elapsed_seconds":  round(elapsed, 3),
        "details":          result.get("details", ""),
        "applied_at":       datetime.now(timezone.utc).isoformat(),
        "refinement_count": refinement_count_after,
    })
    _log_engagement(caller_uid, "chat_edit_used")
