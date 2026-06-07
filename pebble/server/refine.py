"""POST /api/refine — targeted refinements applied to an already-generated
build.

Two refinement classes, separated by whether they need the LLM:

1. **Deterministic** (free, no LLM call): pure style swaps that can be done
   by editing CSS/Tailwind config locally. Examples: ``simpler`` (tone the
   palette down), ``colors`` (swap to a different brand DNA palette).

2. **LLM-backed** (one focused turn): copy-tone shifts that need writing.
   Examples: ``friendlier`` (rewrite copy with warmer tone), ``professional``,
   ``booking`` (add a booking section).

Whether deterministic or LLM-backed, EVERY refinement snapshots the
pre-edit state via :mod:`pebble.history` so the user can roll back.

Refinement IDs match the workspace UI's chip set; adding a new chip means
adding a handler here.
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from pebble.engagement import log_event as _log_engagement
from pebble.user_plan import (
    gate_response,
    get_user_plan,
    increment_usage,
    would_exceed_quota,
)
from pebble.history import snapshot_site, diff_against_snapshot
from pebble.log import log
from pebble.security import project_lock, require_project_owner


def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


# -------- Refinement spec ---------------------------------------------------

# Each handler returns a dict like:
#   {"files_changed": ["app/page.tsx", ...], "details": "..."}
# Returning an empty files_changed list is fine — it means "no-op".

# Deterministic refinement: tone the palette down to a quieter variant.
# Implementation: replace bright accent values with quieter neighbors in
# tailwind.config.ts or globals.css. Works against the conventions the
# engine emits.

_TONE_DOWN_RULES = [
    # (regex pattern, replacement) — applied as a substitution against the
    # raw file text. Targeted to common Tailwind/CSS color literals.
    (r"#FF[0-9A-Fa-f]{4}",  "#C8A96E"),  # any saturated red/orange-ish → muted gold
    (r"#[FE][CB][0-9A-Fa-f]{4}", "#D4B896"),  # near-saturated yellow tones → tan
    (r"bg-red-\d{3}\b",   "bg-stone-500"),
    (r"bg-orange-\d{3}\b","bg-amber-700"),
    (r"bg-pink-\d{3}\b",  "bg-rose-700"),
    (r"text-red-\d{3}\b", "text-stone-700"),
]

_TARGET_FILES_FOR_STYLE = (
    "app/globals.css",
    "tailwind.config.ts",
    "tailwind.config.js",
)


def _refine_simpler(site_dir: Path) -> dict:
    """Tone the palette down across CSS/Tailwind config files. Deterministic,
    no LLM. Touches at most ``_TARGET_FILES_FOR_STYLE`` files."""
    files_changed: list[str] = []
    for rel in _TARGET_FILES_FOR_STYLE:
        path = site_dir / rel
        if not path.exists() or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        new_text = text
        for pattern, replacement in _TONE_DOWN_RULES:
            new_text = re.sub(pattern, replacement, new_text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            files_changed.append(rel)
    return {"files_changed": files_changed, "details": "Toned the palette down to quieter neighbors."}


def _refine_colors(site_dir: Path) -> dict:
    """Pick a different brand DNA palette by cycling the primary/accent
    pair through a small set of editorial-safe combinations. Deterministic;
    no LLM. The pattern is to find the LAST emitted palette and shift it.

    Uses a global rotation index stored at ``output/<slug>/.palette-rotation``
    so repeated clicks cycle through options rather than reverting.
    """
    rotation_file = site_dir.parent / ".palette-rotation"
    try:
        idx = int(rotation_file.read_text()) if rotation_file.exists() else 0
    except Exception:
        idx = 0
    palettes = [
        # (primary, accent, background)
        ("#205661", "#C76E3A", "#F7F3EC"),  # river + spark + sand (default Pebble)
        ("#4B6548", "#C8A96E", "#F2EDE3"),  # sage + warm gold
        ("#1F1D1A", "#5A554E", "#ECE6DC"),  # charcoal mono
        ("#5B6F4A", "#C76E3A", "#F7F3EC"),  # earth + spark
        ("#3B6E7A", "#D4B896", "#FFFFFF"),  # blue-grey + tan
    ]
    target = palettes[(idx + 1) % len(palettes)]
    rotation_file.write_text(str(idx + 1), encoding="utf-8")

    primary, accent, bg = target
    files_changed: list[str] = []

    # Strategy: rewrite the first hex color we find in each style file to the
    # new palette member. Crude but safe — leaves structure intact.
    for rel in _TARGET_FILES_FOR_STYLE:
        path = site_dir / rel
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        # Replace the FIRST color in each of three logical positions.
        new_text, count = _swap_first_three_hex(text, [primary, accent, bg])
        if count > 0:
            path.write_text(new_text, encoding="utf-8")
            files_changed.append(rel)
    return {
        "files_changed": files_changed,
        "details": f"Rotated palette → primary {primary}, accent {accent}, background {bg}.",
    }


def _swap_first_three_hex(text: str, replacements: list[str]) -> tuple[str, int]:
    """Replace at most the first three hex color literals in ``text`` with
    the supplied replacements in order. Returns ``(new_text, count_replaced)``.
    """
    hex_re = re.compile(r"#[0-9A-Fa-f]{6}\b")
    out = []
    last = 0
    count = 0
    for m in hex_re.finditer(text):
        if count >= len(replacements):
            break
        out.append(text[last:m.start()])
        out.append(replacements[count])
        last = m.end()
        count += 1
    out.append(text[last:])
    return "".join(out), count


# -------- LLM-backed refinements (lazy, only fire when needed) -------------

_LLM_REFINE_PROMPTS = {
    "friendlier": (
        "Rewrite the copy across this Next.js build to feel warmer and more "
        "conversational. Keep all structural code (imports, components, layout) "
        "unchanged — only edit the visible text strings inside JSX. Do not "
        "change headlines longer than 12 words. Preserve all phone numbers, "
        "emails, addresses, and CTAs verbatim. Output ONLY <pebble-file> "
        "blocks for the files you changed."
    ),
    "professional": (
        "Rewrite the copy across this Next.js build to feel more professional, "
        "confident, and businesslike. Tighten verbose sentences; remove "
        "exclamation points; replace casual phrasing with clear declarative "
        "statements. Keep all structural code unchanged. Output ONLY "
        "<pebble-file> blocks for files you changed."
    ),
    "booking": (
        "Add a simple booking section to the homepage of this Next.js build. "
        "Render a card with 'Book an appointment' headline, a short intro, "
        "and a placeholder Calendly embed (<iframe>) using a comment "
        "explaining the user will paste their own Calendly URL. Append the "
        "section after the existing services/about section. Do NOT touch "
        "other pages. Output ONLY <pebble-file> blocks for the files you changed."
    ),
}


def _run_llm_refinement(slug: str, refinement_id: str) -> dict:
    """Fire a focused single-turn LLM call to apply a copy/structural
    refinement. Reuses the engine's existing parse_files + file-writing
    logic for safety."""
    from pebble.llm import get_llm_client, LLMError

    site_dir = _output_dir() / slug / "site"
    if not site_dir.exists():
        return {"files_changed": [], "error": f"site not found: output/{slug}/site"}

    client, reason = get_llm_client()
    if not client:
        return {"files_changed": [], "error": f"LLM not configured: {reason}"}

    pe = _engine()
    parse_files = pe.parse_files
    FILE_FORMAT_INSTRUCTION = pe.FILE_FORMAT_INSTRUCTION

    # Read the existing files into a single prompt body so the LLM has context.
    existing_files: list[str] = []
    for p in sorted(site_dir.rglob("*.tsx")):
        try:
            content = p.read_text(encoding="utf-8")
        except Exception:
            continue
        rel = p.relative_to(site_dir).as_posix()
        existing_files.append(f"--- {rel} ---\n{content}\n")
    if not existing_files:
        return {"files_changed": [], "error": "no .tsx files in site"}

    instruction = _LLM_REFINE_PROMPTS.get(refinement_id, "")
    if not instruction:
        return {"files_changed": [], "error": f"unknown LLM refinement: {refinement_id}"}

    # P1 — prepend durable "about your business" context so refines respect
    # the owner's standing facts/voice (per-project brief + per-account).
    from pebble import knowledge as _knowledge
    _brief: dict = {}
    _brief_path = site_dir.parent / "brief.json"
    try:
        if _brief_path.exists():
            _brief = json.loads(_brief_path.read_text(encoding="utf-8"))
    except Exception:
        _brief = {}
    _kb = _knowledge.render_knowledge_block(
        _knowledge.project_knowledge(_brief),
        _knowledge.load_account_knowledge(pe.OUTPUT_DIR, (_brief.get("_user_id") or "")),
    )

    user_prompt = (
        (f"{_kb}\n\n" if _kb else "")
        + f"{instruction}\n\n"
        "--- CURRENT FILES ---\n\n"
        + "".join(existing_files)
        + "\n\n"
        + FILE_FORMAT_INSTRUCTION
    )
    system = (
        "You are a senior frontend engineer applying a focused refinement to a "
        "Next.js project. Output ONLY <pebble-file> blocks. No preamble, no "
        "commentary."
    )

    try:
        response = client.generate(system=system, user=user_prompt, max_tokens=12000)
    except LLMError as e:
        return {"files_changed": [], "error": f"LLM error: {e}"}

    files = parse_files(response)
    if not files:
        return {"files_changed": [], "error": "LLM returned no <pebble-file> blocks"}

    files_changed: list[str] = []
    for path, content in files:
        safe = path.lstrip("/\\")
        if ".." in Path(safe).parts or safe.startswith("/"):
            continue
        full = site_dir / safe
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        files_changed.append(safe)

    return {"files_changed": files_changed, "details": f"LLM applied refinement '{refinement_id}'."}


# -------- HTTP entry point --------------------------------------------------

DETERMINISTIC_REFINEMENTS: dict[str, Callable[[Path], dict]] = {
    "simpler":  _refine_simpler,
    "colors":   _refine_colors,
}

LLM_REFINEMENTS = set(_LLM_REFINE_PROMPTS.keys())

# Free-tier refinements — execution is mechanical AND perceived value is low.
# The complement (deterministic-but-NOT-free) is the "Magic Restyle" tier:
# mechanical execution, but the user perceives it as "AI did something visual
# for me," so giving it away devalues the DNA system (NLM 2026-05-19 review).
# Today the only such refinement is "colors" (palette rotation in DNA family).
#
# "simpler" stays free — it's a regex tone-down, perceived as a minor
# adjustment, not a Magic Restyle.
FREE_DETERMINISTIC_REFINEMENTS: frozenset[str] = frozenset({
    "simpler",
})


def run_refine(handler) -> None:
    """POST /api/refine — body: ``{ slug, refinement_id }``.

    Response:
        {
          "slug":             "<slug>",
          "refinement_id":    "...",
          "files_changed":    ["..."],
          "kind":             "deterministic" | "llm",
          "billable":         false | true,   # deterministic refinements are FREE
          "snapshot_id":      "...",          # the pre-refinement snapshot
          "elapsed_seconds":  0.05,
          "details":          "..."
        }
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

    slug = (body or {}).get("slug")
    refinement_id = (body or {}).get("refinement_id")
    if not isinstance(slug, str) or not slug:
        handler._json(400, {"error": "slug is required"}); return
    if not isinstance(refinement_id, str) or not refinement_id:
        handler._json(400, {"error": "refinement_id is required"}); return

    # Auth gate — added in the 2026-05-15 security pass after NLM caught
    # that refine + visual-edit + rollback + history all predated the
    # auth system and let any signed-in user mutate any project by slug.
    caller_uid = require_project_owner(handler, slug)
    if caller_uid is None:
        return

    # MFA step-up: a stolen AAL1 token must not mutate a project even
    # within its ~1h TTL. No-op for callers without enrolled MFA, for
    # cookie/anon auth, and when Supabase auth isn't configured (tests).
    from pebble.security import enforce_step_up
    if not enforce_step_up(handler):
        return  # 401 already written

    site_dir = _output_dir() / slug / "site"
    if not site_dir.exists():
        handler._json(404, {"error": f"project site not found: {slug}"}); return

    # Phase 54a (2026-05-23) — monthly AI refinement quota gate.
    # Predict billable BEFORE running the refinement so we can deny
    # at-the-door instead of burning compute and then 402'ing the user.
    # Deterministic refinements in FREE_DETERMINISTIC_REFINEMENTS bypass
    # the counter entirely; everything else counts against the user's
    # monthly limit (Free: 30, Starter: 150, Pro: 400). Unknown
    # refinement_ids fall through to the existing 400 handler below.
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

    # Per-slug write lock — same NLM pass found a race window where two
    # concurrent refines on one project both snapshot pre-state and both
    # write, so the second snapshot bakes in the first edit.
    with project_lock(slug) as got_lock:
        if not got_lock:
            handler._json(409, {"error": "another refinement is already in progress; try again in a moment"})
            return

        # Snapshot BEFORE applying — guarantees the user can roll back.
        snap = snapshot_site(slug, reason=f"refine-{refinement_id}", source=f"POST /api/refine {refinement_id}")
        snapshot_id = snap.name if snap else None

        t0 = time.time()
        if refinement_id in DETERMINISTIC_REFINEMENTS:
            try:
                result = DETERMINISTIC_REFINEMENTS[refinement_id](site_dir)
            except Exception as e:
                log.warning("deterministic refinement failed: %s", e)
                handler._json(500, {"error": f"refinement failed: {e}"}); return
            kind = "deterministic"
            # Even mechanical refinements can be metered when the user
            # perceives them as a "Magic Restyle." See FREE_DETERMINISTIC_REFINEMENTS
            # docstring for the rationale (NLM 2026-05-19).
            billable = refinement_id not in FREE_DETERMINISTIC_REFINEMENTS
        elif refinement_id in LLM_REFINEMENTS:
            result = _run_llm_refinement(slug, refinement_id)
            if result.get("error"):
                handler._json(502, {"error": result["error"]}); return
            kind = "llm"
            billable = True
        else:
            handler._json(400, {"error": f"unknown refinement_id: {refinement_id}"}); return

        elapsed = time.time() - t0

    # Phase 35 — diff panel. Compute what actually changed vs the snapshot
    # we took above, attach to the response so the workspace can show
    # "Frontend: Updated components/Hero.tsx (3 lines)". Cheap (set-based
    # line diff over a marketing site of 30-100 files). Never raises —
    # diff_against_snapshot returns None on any I/O issue.
    diff_payload = None
    if snapshot_id:
        try:
            ds = diff_against_snapshot(slug, snapshot_id)
            if ds is not None:
                diff_payload = ds.to_dict()
        except Exception as _exc:
            log.warning("diff_against_snapshot failed (refine %s): %s", refinement_id, _exc)

    # Phase 54a — commit the +1 to the monthly counter now that the
    # refinement succeeded. Pre-checked at the top so the user can't
    # exceed their plan here; this is the post-success commit half.
    refinement_count_after = None
    if billable:
        refinement_count_after = increment_usage(caller_uid, "ai_refinements")

    # 2026-05-24 — credit spend. We spend AFTER the refinement runs
    # so a failure doesn't burn the user's credit. Fail-soft: on
    # Supabase error we log but don't fail the request — operationally
    # we'd rather under-bill than break the edit. Audit/reconcile job
    # catches the gap (next session). Free deterministic refinements
    # don't spend; billable ones cost 1 credit.
    if billable:
        try:
            from pebble import credits as _credits
            spent = _credits.spend(
                user_id=caller_uid,
                amount=_credits.COST_REFINEMENT,
                reason=_credits.REASON_REFINEMENT,
                ref_id=slug,
            )
            if not spent:
                log.warning("[credits] refinement spend skipped for user=%s slug=%s (no balance / supabase miss)",
                            caller_uid[:8] if caller_uid else "?", slug)
        except Exception as _exc:
            log.warning("[credits] refinement spend errored: %s", _exc)

    # 2026-05-23 — Task C of Fly.io integration. When the operator opts
    # into the Fly backend, push the post-refine site state to the Fly
    # app so the next /preview hit reflects the edit. deploy_in_background
    # no-ops when PEBBLE_PREVIEW_BACKEND isn't "fly" — safe to call from
    # every refine path.
    try:
        from pebble.fly_preview import deploy_in_background as _fly_bg_deploy
        _fly_bg_deploy(slug, site_dir)
    except Exception as _exc:
        log.info("[fly] background deploy hook errored after refine for %s: %s", slug, _exc)

    handler._json(200, {
        "slug":             slug,
        "refinement_id":    refinement_id,
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
    # Per-user engagement signal (T17). Best-effort — silent on failure.
    # NEVER pass refinement_id or any user content; only the event name.
    _log_engagement(caller_uid, "refine_used")
