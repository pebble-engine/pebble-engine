"""POST /api/enrich-content — apply build-time chat facts to a generated site.

Phase 58a (2026-05-22). After the main build completes, BuildChatPanel may
have collected up to 3 facts from the user (phone number, featured services,
service area / city). This endpoint applies those facts to the already-written
site files via targeted regex replacements — no LLM call, so it completes
in milliseconds and never adds to the user's wait time.

Strategy per fact type
-----------------------
phone     Replace the first placeholder phone number found in .tsx / .ts / .js
          files matching common placeholder patterns: (555) xxx-xxxx, 555-xxxx,
          generic NANP patterns. We stop after the first successful substitution
          per file so we don't accidentally overwrite real phone numbers that
          the LLM sourced from the brief.

location  Replace generic city placeholders: "Your City", "City, ST",
          "Anywhere, USA". Only in .tsx / .ts / .mdx. Stops after first match
          per file.

services  Not applied via regex (too risky to corrupt structured JSX). Instead,
          we append the fact to a _enriched.json metadata file in the site root
          so future refinement prompts can read it as additional context.
          ("services" still counts toward facts_applied.)

All formats
-----------
Request body::

    { "slug": "<slug>", "facts": [ {"key": "phone", "value": "..."}, ... ] }

Response::

    { "slug": "...", "facts_applied": 2, "files_changed": [...], "snapshot_id": "..." }

Auth: open — called immediately after a successful build. The caller (the
workspace shell) already has the slug from the build response. Ownership
validation is deliberately omitted here because:

  1. The build just succeeded seconds ago (the caller already owns it).
  2. We can't gate on Supabase session here because anonymous builds also
     flow through this path — the user might not be signed in at all.
  3. The endpoint only *adds* personalisation — it doesn't delete or expose data.

If this becomes a concern in Phase 59+, add a short-lived HMAC token (signed
by the engine at build-done time, checked here) so only the build recipient
can enrich their own site.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pebble.log import log


# ---------------------------------------------------------------------------
# Regex patterns for phone placeholder detection
# ---------------------------------------------------------------------------

# US NANP placeholder patterns that the LLM almost always emits when no real
# phone is in the brief. We match the most-common fake-phone shapes:
#   (555) 123-4567   (555) 123 4567   555-123-4567   +1 (555) 123-4567
# We intentionally do NOT match raw 10-digit runs (e.g. 5551234567) to avoid
# clobbering zip codes, IDs, or price tags.
_PHONE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\+?1?\s*\(555\)\s*\d{3}[\-\s]\d{4}"),
    re.compile(r"\(555\)\s*\d{3}[\-\s\.]\d{4}"),
    re.compile(r"555[\-\.]\d{3}[\-\.]\d{4}"),
    # Generic NANP placeholder: any (NXX) NXX-XXXX where NXX starts with 5
    re.compile(r"\(\d{3}\)\s*555[\-\s]\d{4}"),
    re.compile(r"\d{3}[\-\.]\d{3}[\-\.]\d{4}"),   # broad fallback
]

# Location placeholder strings the LLM uses when no city is in the brief.
_LOCATION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bYour City\b",          re.IGNORECASE),
    re.compile(r"\bCity,\s*ST\b",         re.IGNORECASE),
    re.compile(r"\bAnywhere,\s*USA\b",    re.IGNORECASE),
    re.compile(r"\bYour Area\b",          re.IGNORECASE),
    re.compile(r"\bLocal Area\b",         re.IGNORECASE),
    re.compile(r"\bYour Location\b",      re.IGNORECASE),
    re.compile(r"\bYour Town\b",          re.IGNORECASE),
]

# Extensions whose source is safe to search with regex (text files with
# JSX/TSX content). We skip .json to avoid clobbering structured data.
_TEXT_EXTS = ("*.tsx", "*.ts", "*.js", "*.jsx", "*.mdx", "*.md")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _apply_phone(text: str, phone: str) -> str:
    """Replace the first phone-placeholder match in *text* with *phone*.

    Stops after the first match (longest pattern first) so only the most
    prominent placeholder is replaced per file call.
    """
    for pat in _PHONE_PATTERNS:
        new = pat.sub(phone, text, count=1)
        if new != text:
            return new
    return text


def _apply_location(text: str, location: str) -> str:
    """Replace the first location-placeholder match in *text* with *location*."""
    for pat in _LOCATION_PATTERNS:
        new = pat.sub(location, text, count=1)
        if new != text:
            return new
    return text


def _write_enriched_meta(site_dir: Path, facts: list[dict]) -> None:
    """Persist enrichment facts to _enriched.json for future LLM refinements."""
    meta_path = site_dir / "_enriched.json"
    existing: dict = {}
    if meta_path.exists():
        try:
            existing = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
    for f in facts:
        existing[f["key"]] = f["value"]
    existing["enriched_at"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# HTTP entry point
# ---------------------------------------------------------------------------

def run_enrich_content(handler) -> None:
    """POST /api/enrich-content.

    Mutates files inside ``<output>/<slug>/site/`` (phone/location/services
    rewrites + a snapshot for rollback). MUST be owner-gated — without it
    any anon caller could inject phone numbers, addresses, or service text
    into someone else's published site by guessing the slug.

    Phase 58e (2026-05-22) — added require_project_owner. Caught during
    the overnight bug-hunt sweep of slug-taking POST handlers.
    """
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length"}); return
    if length <= 0:
        handler._json(400, {"error": "empty request body"}); return
    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return

    slug: str = (body or {}).get("slug", "").strip()
    raw_facts = (body or {}).get("facts", [])

    if not slug:
        handler._json(400, {"error": "slug is required"}); return
    if not isinstance(raw_facts, list):
        handler._json(400, {"error": "facts must be an array"}); return

    # Auth gate — must come AFTER slug+body validation so we keep the
    # existing 400 responses for malformed payloads, but BEFORE any
    # filesystem touch. require_project_owner returns the validated
    # uid on success and writes 400/401/403/404 on failure.
    from pebble.security import require_project_owner
    if require_project_owner(handler, slug) is None:
        return

    # Validate & normalise facts.
    facts: list[dict] = []
    for f in raw_facts:
        if not isinstance(f, dict):
            continue
        key = str(f.get("key", "")).strip()
        value = str(f.get("value", "")).strip()
        if key and value:
            facts.append({"key": key, "value": value})

    if not facts:
        # Nothing to apply — return a no-op response so the caller doesn't error.
        handler._json(200, {
            "slug": slug, "facts_applied": 0,
            "files_changed": [], "snapshot_id": None,
        })
        return

    # Locate the site directory.
    import sys
    engine = sys.modules.get("pebble_engine") or sys.modules["__main__"]
    site_dir: Path = engine.OUTPUT_DIR / slug / "site"

    if not site_dir.exists():
        handler._json(404, {"error": f"project not found: {slug}"}); return

    # Snapshot before mutating so the user can roll back.
    snapshot_id: Optional[str] = None
    try:
        from pebble.history import snapshot_site
        snap = snapshot_site(slug, reason="enrich-content", source="POST /api/enrich-content")
        snapshot_id = snap.name if snap else None
    except Exception as exc:
        log.warning("enrich-content: snapshot failed for %s: %s", slug, exc)

    # Extract the individual fact values.
    phone    = next((f["value"] for f in facts if f["key"] == "phone"),    None)
    location = next((f["value"] for f in facts if f["key"] == "location"), None)
    services = next((f["value"] for f in facts if f["key"] == "services"), None)

    files_changed: list[str] = []
    facts_applied = 0

    # Apply phone + location via regex across all text source files.
    if phone or location:
        for ext in _TEXT_EXTS:
            for fpath in site_dir.rglob(ext):
                # Skip node_modules and .next
                parts = fpath.parts
                if "node_modules" in parts or ".next" in parts:
                    continue
                try:
                    original = fpath.read_text(encoding="utf-8")
                    text = original

                    if phone:
                        text = _apply_phone(text, phone)
                    if location:
                        text = _apply_location(text, location)

                    if text != original:
                        fpath.write_text(text, encoding="utf-8")
                        rel = str(fpath.relative_to(site_dir))
                        files_changed.append(rel)
                except Exception as exc:
                    log.warning("enrich-content: skipping %s: %s", fpath, exc)

        if phone and any(True for _ in [1]):   # coerce to bool with side effect
            # Count phone as applied if at least one file changed
            facts_applied += (1 if files_changed else 0)
        if location:
            pass  # location counted together with phone above

        # Simpler count: each unique fact type applied.
        applied_types: set[str] = set()
        if phone and files_changed:
            applied_types.add("phone")
        if location and files_changed:
            applied_types.add("location")
        facts_applied = len(applied_types)

    # Services: persist to _enriched.json for future LLM refinement context.
    if services:
        try:
            _write_enriched_meta(site_dir, [f for f in facts if f["key"] == "services"])
            facts_applied += 1
        except Exception as exc:
            log.warning("enrich-content: services meta write failed for %s: %s", slug, exc)

    log.info(
        "enrich-content: slug=%s facts_applied=%d files_changed=%d snapshot=%s",
        slug, facts_applied, len(files_changed), snapshot_id,
    )

    handler._json(200, {
        "slug":          slug,
        "facts_applied": facts_applied,
        "files_changed": files_changed,
        "snapshot_id":   snapshot_id,
    })
