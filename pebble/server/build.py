"""POST /api/build (prompt only) and POST /api/generate (full build).

This is the engine's main pipeline: validate the brief, resolve industry intel,
pick a DNA, fetch images and a hero video, render PROMPT.md, call the LLM,
parse the response into files, run the optional post-build chain (Imagen +
`next dev` + Playwright screenshots), then return a JSON summary.

The function is extracted as a free `run_build(handler, generate)` so the
handler class stays focused on dispatch and the (lengthy) build pipeline lives
on its own. It reaches back into the `pebble_engine` module for shared
helpers via :func:`_engine`, which tolerates both ``python pebble_engine.py``
(module is at ``__main__``) and ``import pebble_engine`` (loaded as a module
in tests).
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from pebble.log import log
from pebble.engagement import log_event as _log_engagement
from pebble.industry import resolve_industry_intel, research_industry
from pebble.llm import get_llm_client, LLMError
from pebble.plan import build_pebble_plan
from pebble.history import snapshot_site
from pebble.cost import estimate_cost
from pebble.text import sanitize_business_name
from pebble.next_config_patch import ensure_allowed_dev_origins
from pebble.visual_ids import inject_pebble_ids
from pebble.security import client_ip, generate_limiter, plan_limiter


def _engine():
    """Resolve the pebble_engine module regardless of how it was launched.

    - ``python pebble_engine.py`` → module is at ``sys.modules['__main__']``.
    - ``import pebble_engine`` (tests) → module is at ``sys.modules['pebble_engine']``.

    Using ``import pebble_engine`` here would re-execute the file under the
    ``pebble_engine`` name when run as the main script, producing a second
    parallel copy of every constant and function. The sys.modules lookup
    avoids that and keeps a single source of truth.
    """
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _select_dna(answers: dict, pick_random_dna, pick_dna_by_id):
    """Resolve the build's design DNA.

    If the brief carries a pinned ``_design_dna_id`` (e.g. from the
    Plan-review UI: "user approved this style, lock it in"), look that
    card up and use it. Otherwise route through ``pick_dna_for_brief``
    which weights DNA cards by industry affinity (10×) and hard-excludes
    cards with conflicting industry aversion — replaces the prior pure-
    random pick that produced catastrophic mismatches (e.g. terminal_operator
    on a wedding photographer). Returns the DNA dict or ``None`` if the
    DNA module isn't loaded.
    """
    if not pick_random_dna:
        return None
    pinned_id = (answers.get("_design_dna_id") or "").strip()
    if pinned_id and pick_dna_by_id:
        card = pick_dna_by_id(pinned_id)
        if card:
            return card
        log.warning("pinned DNA id %r not found — falling back to industry-weighted pick", pinned_id)
    try:
        from style_dna import pick_dna_for_brief
        return pick_dna_for_brief(answers)
    except ImportError:
        try:
            return pick_random_dna()
        except Exception as e:
            log.warning("DNA picker failed: %s", e)
            return None
    except Exception as e:
        log.warning("industry-weighted DNA picker failed: %s — falling back to random", e)
        try:
            return pick_random_dna()
        except Exception:
            return None


def run_plan(handler) -> None:
    """Handle ``POST /api/plan``: return a Pebble Plan without running
    the full build pipeline. Cheap (no LLM call), deterministic given
    the same brief + pinned DNA id, intended for the UI's pre-build
    review screen.

    The Plan includes the DNA's id; the UI should pass that id back into
    ``/api/generate`` as ``_design_dna_id`` to lock the style in for the
    actual build.
    """
    pe = _engine()
    MAX_REQUEST_BYTES   = pe.MAX_REQUEST_BYTES
    _slugify            = pe._slugify
    validate_build_payload = pe.validate_build_payload
    pick_random_dna     = pe.pick_random_dna
    pick_dna_by_id      = pe.pick_dna_by_id
    _LAYOUT_DNA_OK      = getattr(pe, "_LAYOUT_DNA_OK", False)
    _pick_layout        = getattr(pe, "pick_layout_for_brief", None)

    ip = client_ip(handler)
    if not plan_limiter.allow(ip or ""):
        handler._json(429, {"error": "too many plan requests, slow down"}); return

    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return
    if length <= 0:
        handler._json(400, {"error": "empty request body"}); return
    if length > MAX_REQUEST_BYTES:
        mb = MAX_REQUEST_BYTES // (1024 * 1024)
        handler._json(413, {"error": f"request too large (max {mb} MB)"}); return

    try:
        answers = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return

    answers, err = validate_build_payload(answers)
    if err:
        handler._json(400, err); return

    # Phase 20a (2026-05-20): normalize business_name BEFORE slug + LLM so the
    # rendered hero doesn't echo user typos like "Mechanic shop inQueens".
    raw_name = answers.get("business_name", "")
    cleaned = sanitize_business_name(raw_name)
    if cleaned and cleaned != raw_name:
        log.info("[plan] business_name sanitized: %r -> %r", raw_name, cleaned)
        answers["business_name"] = cleaned
    answers["_slug"] = _slugify(cleaned or "untitled")

    business_type = answers.get("business_type", answers.get("industry", ""))
    industry_key, industry_intel = (None, None)
    if business_type:
        try:
            industry_key, industry_intel = resolve_industry_intel(business_type)
            if industry_intel:
                answers["_industry_intel_key"] = industry_key
        except Exception as e:
            log.warning("industry intel resolution failed: %s", e)

    # Layout DNA for plan preview
    if _LAYOUT_DNA_OK and _pick_layout:
        try:
            creative_direction = (answers.get("creative_direction") or "").strip()
            layout_dna = _pick_layout(answers, creative_direction=creative_direction)
            if layout_dna:
                answers["_layout_dna_id"] = layout_dna["id"]
        except Exception as e:
            log.warning("Layout DNA selection (plan) failed: %s", e)

    design_dna = _select_dna(answers, pick_random_dna, pick_dna_by_id)
    if design_dna:
        answers["_design_dna"] = design_dna.get("id")

    # Language detection — pinned on the brief so /api/generate sees the
    # same answer the Plan preview shows. Honors an explicit _language
    # override; falls back to script/word-based detection.
    try:
        from pebble.language import detect_language
        answers["_language"] = detect_language(answers)
    except Exception as e:
        log.warning("language detection failed: %s", e)
        answers.setdefault("_language", "en")

    plan = build_pebble_plan(answers, industry_intel, design_dna)
    handler._json(200, {
        "plan":           plan,
        "industry_key":   industry_key,
        "dna_id":         design_dna.get("id") if design_dna else None,
        "layout_dna_id":  answers.get("_layout_dna_id"),
    })


def run_build(handler, generate: bool, progress_cb=None) -> None:
    """Handle a build request. ``handler`` is a ``PebbleHandler`` instance;
    the JSON response is written via its ``_json`` helper.

    ``progress_cb``, if provided, is called as ``progress_cb(event_type, data)``
    at key pipeline milestones so callers can emit SSE frames without polling.
    Failures inside the callback are silently swallowed.
    """
    def _emit(event_type: str, data: dict) -> None:
        if progress_cb is not None:
            try:
                progress_cb(event_type, data)
            except Exception:
                pass

    pe = _engine()

    # Hoist module symbols to locals so the body below reads like the original
    # _handle_build did. These are all defined at the top level of pebble_engine.
    MAX_REQUEST_BYTES = pe.MAX_REQUEST_BYTES
    OUTPUT_DIR = pe.OUTPUT_DIR
    _DNA_OK = pe._DNA_OK
    FILE_FORMAT_INSTRUCTION = pe.FILE_FORMAT_INSTRUCTION
    LITE_FILE_FORMAT_INSTRUCTION = pe.LITE_FILE_FORMAT_INSTRUCTION
    _slugify = pe._slugify
    validate_build_payload = pe.validate_build_payload
    build_ui_query = pe.build_ui_query
    build_prompt = pe.build_prompt
    audit_design_system = pe.audit_design_system
    figma_file_summary = pe.figma_file_summary
    parse_files = pe.parse_files
    apply_imagen_to_site = pe.apply_imagen_to_site
    post_build_run_dev_server = pe.post_build_run_dev_server
    post_build_screenshots = pe.post_build_screenshots
    generate_design_system = pe.generate_design_system  # None when degraded
    pick_random_dna = pe.pick_random_dna                # None when DNA module missing
    _LAYOUT_DNA_OK  = getattr(pe, "_LAYOUT_DNA_OK", False)
    _pick_layout    = getattr(pe, "pick_layout_for_brief", None)

    ip = client_ip(handler)
    if generate and not generate_limiter.allow(ip or ""):
        handler._json(429, {"error": "too many build requests — max 5 per 10 min per IP"}); return

    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return
    if length <= 0:
        handler._json(400, {"error": "empty request body"}); return
    if length > MAX_REQUEST_BYTES:
        mb = MAX_REQUEST_BYTES // (1024 * 1024)
        handler._json(413, {"error": f"request too large (max {mb} MB)"}); return

    try:
        answers = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return

    answers, err = validate_build_payload(answers)
    if err:
        handler._json(400, err); return

    # Phase 20a (2026-05-20): normalize business_name BEFORE slug + LLM so the
    # rendered hero doesn't echo user typos like "Mechanic shop inQueens".
    raw_name = answers.get("business_name", "")
    cleaned = sanitize_business_name(raw_name)
    if cleaned and cleaned != raw_name:
        log.info("[build] business_name sanitized: %r -> %r", raw_name, cleaned)
        answers["business_name"] = cleaned
    slug = _slugify(cleaned or "untitled")
    # Phase 15f (2026-05-20): if a next dev is actively serving this slug,
    # auto-suffix the rebuild so the previous preview keeps running on its
    # current port and the new build gets its own directory + dev server.
    # Prevents the "mid-overwrite kills the running preview" failure mode
    # Marc hit when rebuilding the same brief.
    try:
        from pebble.server.dev_registry import get_url as _get_dev_url
        if _get_dev_url(slug):
            base = slug
            n = 2
            while _get_dev_url(f"{base}-{n}"):
                n += 1
            slug = f"{base}-{n}"
            log.info("[build] auto-suffix: %r is already serving; using %r", base, slug)
    except Exception:
        # If dev_registry is unavailable, fall back to raw slug behavior
        # (overwrite — same as before Phase 15f). Soft-fail.
        pass
    answers["_slug"] = slug
    # Phase 25a (2026-05-20): emit business_name in started so the workspace
    # Plan Reveal can show the project title immediately. The user sees their
    # name pop in within 1-2 seconds of submit — the perceived-speed payoff.
    _emit("started", {"slug": slug, "business_name": cleaned or slug.replace("-", " ").title()})
    if "_created_at" not in answers:
        answers["_created_at"] = datetime.now().isoformat()

    # Resolve caller identity — v3 (Supabase Bearer JWT) takes priority
    # because it also carries the email needed for the drip sequence.
    # Legacy cookie session is the fallback for dev/test paths.
    user_email: str = ""
    try:
        raw_auth = (handler.headers.get("Authorization") or "").strip()
        if raw_auth.lower().startswith("bearer "):
            from pebble import auth_admin
            token = raw_auth[7:].strip()
            if token and auth_admin.is_configured():
                user_data = auth_admin.validate_access_token(token)
                if isinstance(user_data, dict) and user_data.get("id"):
                    answers["_user_id"] = user_data["id"]
                    user_email = (user_data.get("email") or "").strip()
        if not answers.get("_user_id"):
            from pebble.server.auth import current_user_id
            owner = current_user_id(handler)
            if owner:
                answers["_user_id"] = owner
    except Exception as e:
        log.warning("user id resolution failed: %s", e)

    # Phase 54b — intentional Free signup gate. If the caller signed up
    # but hasn't explicitly picked a plan yet, deny the build with a 402
    # pointing them to the plan picker. The v3 frontend responds by
    # showing the plan-picker modal (with the offer-wall + background-
    # build trick in Phase 54c). Anonymous callers (no _user_id) pass
    # through — they hit the auth gate elsewhere and we don't double-up.
    caller_uid = answers.get("_user_id")
    if generate and caller_uid:
        try:
            from pebble.user_plan import needs_plan_selection, gate_response, get_user_plan
            if needs_plan_selection(caller_uid):
                handler._json(402, {
                    **gate_response(
                        feature_label="Site generation",
                        required_plan="free",  # Free is enough — they just need to ACTIVELY pick it
                        current_plan=get_user_plan(caller_uid),
                    ),
                    "needs_plan_selection": True,
                    "error": "Pick a plan to start your first build.",
                })
                return
        except Exception as e:
            # Fail-open: never let the plan-selection gate break builds
            # because of a sentinel read error.
            log.warning("plan-selection gate check failed: %s", e)

    ds_text = ""
    if generate_design_system:
        try:
            query = build_ui_query(answers)
            ds_text = generate_design_system(query, answers["business_name"], output_format="markdown")
        except Exception as e:
            ds_text = f"*(Design system generation failed: {e})*"

    # Resolve industry intelligence (industries.json → LLM fallback → cache)
    business_type = answers.get("business_type", answers.get("industry", ""))
    industry_key, industry_intel = (None, None)
    if business_type:
        try:
            industry_key, industry_intel = resolve_industry_intel(business_type)
            if industry_intel:
                answers["_industry_intel_key"] = industry_key
        except Exception as e:
            log.warning("industry intel resolution failed: %s", e)
    _emit("industry", {"key": industry_key})

    # Research industry for data-driven recommendations (the long-form text block)
    research_text = ""
    if business_type:
        try:
            research_text = research_industry(business_type)
        except Exception as e:
            log.warning("Industry research failed: %s", e)
            research_text = ""

    # Design reference (Figma URL — uploaded image attachments come via the payload)
    design_reference: dict = {}
    figma_url = (answers.get("figma_url") or "").strip()
    if figma_url:
        summary = figma_file_summary(figma_url)
        if summary:
            design_reference["figma_url"] = figma_url
            design_reference["figma_summary"] = summary
    attachments = answers.get("design_reference_images") or []
    if attachments:
        design_reference["image_count"] = len(attachments)
        design_reference["_raw_attachments"] = attachments

    # Layout DNA — structural architecture (hero type, nav, section flow).
    # Picked first so the style DNA can be chosen knowing the layout context.
    # Honors `_layout_dna_id` pinned in the brief (e.g. from Plan-review UI).
    layout_dna = None
    if _LAYOUT_DNA_OK and _pick_layout:
        try:
            creative_direction = (answers.get("creative_direction") or "").strip()
            layout_dna = _pick_layout(answers, creative_direction=creative_direction)
            if layout_dna:
                answers["_layout_dna"]    = layout_dna          # full card — used by build_prompt
                answers["_layout_dna_id"] = layout_dna["id"]
                log.info("Layout DNA: %s (%s)", layout_dna["label"], layout_dna["id"])
        except Exception as e:
            log.warning("Layout DNA selection failed: %s", e)
    _emit("layout", {
        "layout_id":    layout_dna.get("id", "")    if layout_dna else "gradient_mesh",
        "layout_label": layout_dna.get("label", "") if layout_dna else "Gradient Mesh",
    })

    # Style DNA — visual surface (colors, fonts, motion, signature moves).
    # Honors `_design_dna_id` in the brief when the Plan-review UI has
    # already locked in a style.
    design_dna = None
    if _DNA_OK:
        design_dna = _select_dna(answers, pick_random_dna, pe.pick_dna_by_id)
        if design_dna:
            answers["_design_dna"] = design_dna["id"]
            log.info("Style DNA: %s (%s)", design_dna['label'], design_dna['id'])
    # Phase 25a (2026-05-20): include palette + design summary so the
    # workspace Plan Reveal can paint color swatches + style chips
    # immediately as the style event arrives. Webild-parity UX move.
    _style_palette: list[str] = []
    _style_signature: list[str] = []
    if design_dna:
        _pal = design_dna.get("palette") or {}
        if isinstance(_pal, dict):
            for k in ("bg", "fg", "accent", "muted", "border"):
                v = _pal.get(k)
                if v and isinstance(v, str):
                    _style_palette.append(v)
        sigs = design_dna.get("signature_moves") or []
        if isinstance(sigs, list):
            _style_signature = [str(s) for s in sigs[:3] if s]
    _emit("style", {
        "dna_label": design_dna.get("label", "") if design_dna else "",
        "dna_id":    design_dna.get("id", "")    if design_dna else "",
        "palette":   _style_palette,
        "signature_moves": _style_signature,
    })

    # Language — same flow as run_plan. Detected once + persisted so the
    # generated brief.json carries the canonical code through repairs,
    # refinements, and visual edits.
    try:
        from pebble.language import detect_language
        answers["_language"] = detect_language(answers)
        if answers["_language"] != "en":
            log.info("Build language: %s", answers["_language"])
    except Exception as e:
        log.warning("language detection failed: %s", e)
        answers.setdefault("_language", "en")

    notes = audit_design_system(ds_text) if ds_text else []
    prompt = build_prompt(
        answers, ds_text, notes, research_text,
        industry_intel=industry_intel,
        design_reference=design_reference or None,
        design_dna=design_dna,
        language=answers.get("_language", "en"),
    )

    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    # Sanitize: strip base64 image data from saved brief (keep metadata only)
    saved_answers = dict(answers)
    if saved_answers.get("design_reference_images"):
        saved_answers["design_reference_images"] = [
            {k: v for k, v in img.items() if k != "data"}
            for img in saved_answers["design_reference_images"] if isinstance(img, dict)
        ]
    (out_dir / "brief.json").write_text(json.dumps(saved_answers, indent=2), encoding="utf-8")
    # Pebble Plan — the user-facing "here's what I'll build" summary the UI
    # shows before/after generation. Pure derivation of brief + intel + DNA;
    # safe to regenerate from those three inputs at any point.
    try:
        plan = build_pebble_plan(saved_answers, industry_intel, design_dna)
        (out_dir / "plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
        # Phase 25a (2026-05-20): emit a compact plan summary as an SSE event
        # so the workspace Plan Reveal can paint the section list immediately.
        # We avoid sending the full plan to keep frame size small — just the
        # name + page summaries the UI needs to render its checklist.
        try:
            _emit("plan", {
                "name": saved_answers.get("business_name", "") or "Untitled",
                "audience": plan.get("audience", "") if isinstance(plan, dict) else "",
                "goal": plan.get("goal", "") if isinstance(plan, dict) else "",
                "pages": [
                    {
                        "id": p.get("id", ""),
                        "title": p.get("title", ""),
                        "route": p.get("route", ""),
                        "foundation": bool(p.get("foundation", False)),
                    }
                    for p in (plan.get("pages") or [])
                    if isinstance(p, dict)
                ],
            })
        except Exception as e:
            log.warning("plan SSE emit failed: %s", e)
    except Exception as e:
        log.warning("Pebble Plan generation failed: %s", e)
    (out_dir / "PROMPT.md").write_text(prompt, encoding="utf-8")

    if not generate:
        handler._json(200, {
            "prompt": prompt,
            "warning_count": len(notes),
            "slug": slug,
            "saved_to": f"output/{slug}/",
        })
        return

    client, reason = get_llm_client()
    if not client:
        handler._json(503, {
            "error": f"LLM not configured: {reason}",
            "prompt": prompt, "warning_count": len(notes),
            "slug": slug, "saved_to": f"output/{slug}/",
        })
        return

    # Tier-aware model override (Phase 13c, 2026-05-19).
    # Free tier → Qwen Flash (fast + cheap). Paid → Qwen Plus (1M ctx,
    # better quality). Only applies when the active provider is
    # OpenRouter; Anthropic/Gemini honour PEBBLE_MODEL unchanged so
    # manual testing isn't disrupted. PEBBLE_MODEL=auto opts INTO the
    # tier mapping; any other explicit value still wins (lets ops force
    # a specific Qwen variant for debugging).
    if getattr(client, "provider", "") == "openrouter":
        from pebble.server.model_for_plan import (
            resolve_user_plan, model_for_plan, MODEL_FOR_PAID_TIER, MODEL_FOR_FREE_TIER,
        )
        # Treat the default Plus id as "no manual override" so we tier-shift.
        # Any other PEBBLE_MODEL value (max-preview, flash, deepseek, etc.)
        # is treated as deliberate and respected.
        current_model = getattr(client, "model", "")
        is_default_model = current_model in (MODEL_FOR_PAID_TIER, MODEL_FOR_FREE_TIER)
        if is_default_model:
            plan = resolve_user_plan(answers.get("_user_id"))
            picked = model_for_plan(plan)
            if picked != current_model:
                log.info("[build] tier-shifting model: plan=%s, model=%s → %s",
                         plan, current_model, picked)
                client.model = picked

    try:
        is_lite = answers.get("output_mode") == "lite"
        format_instruction = LITE_FILE_FORMAT_INSTRUCTION if is_lite else FILE_FORMAT_INSTRUCTION
        full_user = prompt + format_instruction
        # Provider-aware max_tokens — Qwen 3.6 Plus (OpenRouter default) has
        # 1M context + comfortable 60k+ output capacity, so we bump the cap
        # to let multi-page builds (5-7 industry pages + foundation + universal
        # pages) finish without truncating mid-stream. Anthropic/Gemini stay
        # at the proven 32k zone for our prompt size — Sonnet's hard ceiling
        # is ~64k but 32k is where we've validated stability.
        if is_lite:
            _max_tok = 8000
        else:
            _provider = getattr(client, "provider", "")
            _max_tok = 60000 if _provider == "openrouter" else 32000
        _emit("generating", {"model": client.model, "max_tokens": _max_tok})

        if is_lite:
            system = (
                "You are a senior frontend engineer building a single self-contained HTML file. "
                "No framework. No build step. Vanilla HTML, CSS, and JavaScript only — plus CDN libraries.\n\n"

                "NON-NEGOTIABLE RULES:\n"
                "1. Output ONLY one <pebble-file path=\"index.html\"> block. First character is `<`. No preamble.\n"
                "2. The file must be complete and run in a browser with no other files. Zero TODOs. Zero stubs.\n"
                "3. Hero must have a large visible <h1>. No blank hero.\n"
                "4. All animations use GSAP + ScrollTrigger from CDN. Lenis for smooth scroll.\n"
                "5. Use splitWords() helper (defined in the brief) instead of SplitText.\n"
                "6. `gsap.registerPlugin(ScrollTrigger)` at top of <script>.\n"
                "7. Hero uses a CSS gradient mesh background — no external image URLs needed unless PEBBLE_USE_IMAGEN=true.\n"
                "8. All phone CTAs: href=\"tel:...\". All inputs: font-size minimum 16px.\n"
                "9. No scroll-behavior: smooth in CSS.\n"
                "10. No fake testimonials. No invented contact info — use [BUSINESS PHONE] etc.\n\n"

                "Build now. The owner reviews the output. You are not the reviewer."
            )
        else:
            system = (
                "You are a senior web engineer executing a precise build specification. "
                "You do not have opinions. You do not ask questions. You do not present alternatives. "
                "You read the brief, you read every skill file, and you build exactly what is specified.\n\n"

                "VISUAL AUTHORITY: The brief begins with a `DESIGN DNA — TOP-PRIORITY DIRECTIVE` block. "
                "That block is the single highest authority on visual choices (fonts, hero structure, motion, "
                "color posture, layout grid, image treatment). When the DNA block contradicts anything else "
                "in the brief — including the Resolved Design Contract's font suggestions or the Code Patterns "
                "section's hero structure — the DNA block wins. The skill files (iOS, Stack, No-Slop, BI) still "
                "govern code correctness and conversion patterns; the DNA only governs the visual surface, but "
                "on the visual surface its word is final. Two builds with different DNAs should look like two "
                "different studios made them.\n\n"

                "NON-NEGOTIABLE RULES -- violating any of these is a build failure:\n"
                "1. Output ONLY <pebble-file> blocks. No preamble. No plan. No commentary. First character is `<`.\n"
                "2. Every file must be complete. Zero TODOs. Zero stubs. Zero placeholder functions.\n"
                "3. Apply the iOS Skill rules to every animation, scroll effect, and layout. Not optional.\n"
                "4. `100dvh` not `100vh` or `h-screen` on any full-height element.\n"
                "5. SSR SAFETY: `ScrollTrigger.normalizeScroll(true)` and `ScrollTrigger.config({ ignoreMobileResize: true })` MUST be inside `useEffect` -- NEVER at module level. They access `window` and crash Next.js SSR if called outside the browser. `gsap.registerPlugin()` is safe at module level; these two calls are not.\n"
                "6. All autoplay video: `autoPlay muted loop playsInline` -- all four attributes, always.\n"
                "7. All form inputs: minimum `font-size: 16px` -- without exception.\n"
                "8. No fake testimonials. No invented phone numbers or addresses. Use `[BUSINESS PHONE]` etc.\n"
                "9. No `scroll-behavior: smooth` in CSS anywhere.\n"
                "10. Three.js: dynamic import with `ssr: false`, `dpr={[1, 2]}`, context-lost handler, dispose on unmount.\n"
                "11. Honor the Design DNA's font list. The fonts listed there are the ONLY fonts allowed for this build. Do not substitute Fraunces, Inter, or any other default unless the DNA explicitly names it.\n"
                "12. Implement at least 3 of the DNA's `signature moves` — these are what make the build feel like its DNA, not a generic site with new fonts.\n\n"

                "LINK HANDLING -- one rule, no ambiguity (added 2026-05-19 to fix unstyled nav anchors):\n"
                "- Page navigation (nav menu, footer sitemap, in-content links to other pages): "
                "import Link from \"next/link\" and use <Link href=\"/services\" className=\"...\">. NEVER bare <a href=\"/services\">.\n"
                "- Phone/email: <a href=\"tel:[BUSINESS PHONE]\" className=\"...\"> and "
                "<a href=\"mailto:[EMAIL]\" className=\"...\">. NEVER use Link for tel: or mailto:.\n"
                "- External links: <a href=\"https://...\" target=\"_blank\" rel=\"noopener noreferrer\" className=\"...\">.\n"
                "- EVERY anchor and Link MUST have explicit Tailwind className with at minimum: text color, "
                "hover state, and font weight. NEVER emit a className-less <a> or <Link> — that produces "
                "unstyled browser-default blue underlined links.\n\n"

                "If you are uncertain about any detail not in the brief, make the best decision and build. "
                "The owner reviews the output. You are not the reviewer."
            )
        t0 = time.time()
        vision_images = (design_reference or {}).get("_raw_attachments") if design_reference else None

        # Phase A.5 (2026-05-19): Incremental file writes during stream.
        # Files land on disk AS Qwen finishes each <pebble-file> block,
        # not at the end of the response. Once foundation files
        # (layout.tsx + page.tsx + globals.css + package.json + next.config.mjs)
        # exist, we emit a `preview_ready` event so the frontend can
        # surface a "View live →" button at ~60-90s instead of ~8-10 min.
        #
        # We snapshot BEFORE writing anything (preserves rollback target)
        # and create site_dir up front so the streaming loop can write
        # without an extra mkdir per file.
        site_dir = out_dir / "site"
        try:
            snapshot_site(slug, reason="generate", source="POST /api/generate (pre-overwrite)")
        except Exception as snap_err:
            log.warning("history snapshot failed: %s", snap_err)
        site_dir.mkdir(exist_ok=True)

        written_incrementally: set[str] = set()
        preview_emitted = False
        PREVIEW_REQUIRED = (
            "app/layout.tsx", "app/page.tsx", "app/globals.css",
            "package.json", "next.config.mjs",
        )

        # Phase 13f: preview warmup. As soon as package.json lands on disk,
        # we kick off `npm install` in a background thread. By the time
        # the LLM stream finishes (~5-8 min), install is usually already
        # done — so the post-stream next-dev startup only takes ~10-20s
        # instead of ~90-120s. Total time to preview drops dramatically.
        from pebble.server.preview_warmup import PreviewWarmup
        warmup = PreviewWarmup(site_dir)

        def _safe_relative(p: str) -> Optional[str]:
            """Return the path lstripped + traversal-checked, or None if
            it would escape site_dir."""
            s = p.lstrip("/\\")
            if ".." in Path(s).parts or s.startswith("/"):
                return None
            return s

        def _write_one(path: str, content: str) -> None:
            """Write a single streamed file to disk. Silent on filesystem
            failure (logged) so a bad path doesn't kill the entire stream.

            Side-effect: kicks off the npm install warmup the moment
            package.json lands. Idempotent — only the first call starts
            the install thread."""
            safe = _safe_relative(path)
            if safe is None:
                return
            full = site_dir / safe
            try:
                full.parent.mkdir(parents=True, exist_ok=True)
                full.write_text(content, encoding="utf-8")
                written_incrementally.add(safe)
            except OSError as fs_err:
                log.warning("incremental write failed for %s: %s", safe, fs_err)
                return
            # Trigger early warmup once package.json is on disk.
            if safe == "package.json" and not warmup.started:
                warmup.start_install()

        def _check_preview_ready() -> bool:
            return all((site_dir / f).exists() for f in PREVIEW_REQUIRED)

        # Phase 13f.2 (2026-05-21) — Early-start `next dev` thread.
        # Foundation files + warmed-up node_modules is enough to start the
        # dev server. We fire this in a SECOND background thread (in
        # parallel with both the LLM stream AND the npm-install warmup)
        # so the preview becomes clickable while the LLM is still writing
        # the inner pages. Idempotent — only the first call to
        # _try_start_dev_ready_thread spawns the worker.
        #
        # The worker:
        #   1. Calls start_next_dev_after_install which waits for warmup
        #      install to finish, then spawns `next dev` + polls until it
        #      responds.
        #   2. Registers the URL in dev_registry on success.
        #
        # The streaming-loop heartbeat checks dev_registry.get_url(slug)
        # AFTER calling this; once the URL is registered, preview_ready
        # fires honestly (dev server is actually up, not just files on disk).
        _dev_ready_thread: Optional[threading.Thread] = None
        _dev_ready_lock = threading.Lock()

        def _try_start_dev_ready_thread() -> None:
            """Kick off the dev-server startup in a background thread.
            Idempotent (only starts once per build). Silent on failure —
            errors bubble through the existing post-build error path."""
            nonlocal _dev_ready_thread
            with _dev_ready_lock:
                if _dev_ready_thread is not None:
                    return
                if not _check_preview_ready():
                    return
                # Capture the slug + site_dir + warmup by closure
                def _runner() -> None:
                    try:
                        from pebble.server.preview_warmup import start_next_dev_after_install
                        from pebble.server.dev_registry import register as _reg_dev
                        result = start_next_dev_after_install(site_dir, warmup)
                        if result.get("url") and not result.get("errors"):
                            _reg_dev(slug, result["url"])
                            log.info("[preview-ready] dev server up at %s (early-start, install was %.1fs)",
                                     result["url"], result.get("install_seconds") or 0)
                        elif result.get("errors"):
                            log.warning("[preview-ready] early-start failed: %s", result["errors"])
                    except Exception as exc:
                        log.warning("[preview-ready] early-start thread crashed: %s", exc)

                t = threading.Thread(
                    target=_runner,
                    daemon=True,
                    name=f"dev-ready-{slug}",
                )
                t.start()
                _dev_ready_thread = t

        # Streaming path — emit a `file` SSE event per complete <pebble-file>
        # block as it arrives + write to disk + flag preview_ready as soon
        # as the foundation set is on disk. Falls back to single-shot
        # generate() if the client doesn't support streaming OR if vision
        # images are attached.
        if hasattr(client, "generate_stream") and progress_cb and not vision_images:
            try:
                from pebble.streaming_parser import StreamingFileParser
            except Exception:
                StreamingFileParser = None  # type: ignore
            if StreamingFileParser is not None:
                parser = StreamingFileParser()
                response_parts: list[str] = []
                file_index = 0
                # Phase 15e: heartbeat events. The SSE outer timeout
                # (900s) resets every time ANY event reaches the queue,
                # but if the LLM "warms up" for >900s before emitting
                # its first <pebble-file> block, the timeout fires
                # spuriously. Emit a `heartbeat` event every ~5 seconds
                # of actual streaming so the queue is never silent.
                # Counts toward `chars_streamed` so the heartbeat carries
                # real progress info, not just a ping.
                import time as _t
                last_heartbeat_at = _t.time()
                chars_streamed = 0
                HEARTBEAT_INTERVAL_S = 5.0
                for chunk in client.generate_stream(
                    system=system,
                    user=full_user,
                    max_tokens=_max_tok,
                ):
                    response_parts.append(chunk)
                    chars_streamed += len(chunk)
                    parser.feed(chunk)
                    for path, content in parser.drain():
                        _write_one(path, content)
                        file_index += 1
                        _emit("file", {"name": path, "index": file_index})
                    # Heartbeat (cheap rate-limited check)
                    now = _t.time()
                    if now - last_heartbeat_at >= HEARTBEAT_INTERVAL_S:
                        last_heartbeat_at = now
                        _emit("heartbeat", {
                            "chars_streamed": chars_streamed,
                            "files_so_far": file_index,
                        })
                        # Phase 13f.2 (2026-05-21) — preview_ready emission
                        # re-enabled with the proper gate. Two stages now:
                        #   (1) Foundation files on disk → kick off the
                        #       background dev-start thread (idempotent).
                        #   (2) dev_registry has the URL → emit
                        #       preview_ready honestly. Frontend's iframe
                        #       will actually render.
                        # End result: clickable preview at ~LLM-start + 30s
                        # (foundation lands quickly, warmup runs in parallel,
                        # next dev boots in ~10-20s on warmed cache).
                        if not preview_emitted and _check_preview_ready():
                            _try_start_dev_ready_thread()
                            from pebble.server.dev_registry import get_url as _get_dev_url
                            if _get_dev_url(slug):
                                preview_emitted = True
                                _emit("preview_ready", {
                                    "slug": slug,
                                    "url": f"/preview/{slug}/",
                                })
                # Best-effort recovery of an unterminated trailing block
                for path, content in parser.flush_remaining():
                    _write_one(path, content)
                    file_index += 1
                    _emit("file", {"name": path, "index": file_index})
                    # Same gate as the heartbeat path — files on disk are
                    # necessary but not sufficient. Wait for dev_registry.
                    if not preview_emitted and _check_preview_ready():
                        _try_start_dev_ready_thread()
                        from pebble.server.dev_registry import get_url as _get_dev_url
                        if _get_dev_url(slug):
                            preview_emitted = True
                            _emit("preview_ready", {
                                "slug": slug,
                                "url": f"/preview/{slug}/",
                            })
                response = "".join(response_parts)
            else:
                response = client.generate(
                    system=system,
                    user=full_user,
                    max_tokens=_max_tok,
                    images=vision_images,
                )
        else:
            response = client.generate(
                system=system,
                user=full_user,
                max_tokens=_max_tok,
                images=vision_images,
            )
        elapsed = time.time() - t0
    except LLMError as e:
        handler._json(500, {
            "error": str(e),
            "prompt": prompt, "warning_count": len(notes),
            "slug": slug, "saved_to": f"output/{slug}/",
        })
        return

    files = parse_files(response)
    (out_dir / "llm_response_raw.txt").write_text(response, encoding="utf-8")

    # Truncation guard: if the LLM's response has more <pebble-file>
    # opens than closes, the last file(s) were cut mid-stream. Parser
    # is permissive about this (it boundaries off the next opening tag,
    # not closing) so a 32-open/31-close response yields 32 "files"
    # with the last one truncated. We don't fail the build — the partial
    # output is still usable for diagnostics — but we set billable: false
    # so the user isn't charged for a broken site.
    truncated_count = pe.detect_truncation(response) if hasattr(pe, "detect_truncation") else 0
    if truncated_count:
        log.warning(
            "LLM response truncated: %d unmatched <pebble-file> opens. "
            "Build will be flagged non-billable.",
            truncated_count,
        )

    if not files:
        handler._json(500, {
            "error": "LLM response had no <pebble-file> blocks. Raw response saved to llm_response_raw.txt.",
            "prompt": prompt, "warning_count": len(notes),
            "slug": slug, "saved_to": f"output/{slug}/",
            "raw_preview": response[:1500],
        })
        return

    # site_dir + snapshot already happen above (before streaming) so we
    # could write incrementally. This loop now only handles files the
    # streaming parser didn't catch (non-streaming providers, or files
    # recovered by parse_files but not by StreamingFileParser).
    site_dir = out_dir / "site"
    # If we never streamed (e.g. Gemini/Anthropic path) site_dir still
    # needs to exist + snapshot still needs to fire.
    if not written_incrementally:
        try:
            snapshot_site(slug, reason="generate", source="POST /api/generate (pre-overwrite)")
        except Exception as e:
            log.warning("history snapshot failed: %s", e)
        site_dir.mkdir(exist_ok=True)

    written: list[str] = list(written_incrementally)  # start from streamed set
    for path, content in files:
        safe = path.lstrip("/\\")
        if ".." in Path(safe).parts or safe.startswith("/"):
            continue
        if safe in written_incrementally:
            continue  # already on disk from the streaming loop
        full = site_dir / safe
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        written.append(safe)

    _emit("writing", {"file_count": len(written)})

    # Inject data-pebble-id on every text-bearing tag so /api/visual-edit can
    # do surgical lookups via the manifest at <site>/.pebble-ids.json instead
    # of the old "find original_text across all files" heuristic.
    try:
        inject_pebble_ids(site_dir)
    except Exception as e:
        log.warning("pebble-id injection failed: %s", e)

    # Cost telemetry — honest token + cost estimate so the build leaves
    # behind an audit trail of how expensive this generation was. The
    # billable flag is true here (full /api/generate is a paid action);
    # /api/refine and /api/visual-edit set their own billable flags.
    cost = estimate_cost(prompt=full_user, response=response, model=client.model)
    (out_dir / "build_meta.json").write_text(json.dumps({
        "model":            client.model,
        "provider":         getattr(client, "provider", None),
        "elapsed_seconds":  round(elapsed, 1),
        "file_count":       len(written),
        "built_at":         datetime.now().isoformat(),
        # Truncated responses produce broken sites — flag non-billable
        # so the user isn't charged. truncated_count surfaces the
        # severity (1 = last file cut, 2+ = multiple files cut).
        "billable":         truncated_count == 0,
        "truncated":        bool(truncated_count),
        "truncated_count":  truncated_count,
        "tokens_used":      {"input": cost.input_tokens, "output": cost.output_tokens},
        "estimated_cost_usd": round(cost.estimated_cost_usd, 6),
        "rate_card_used":   cost.rate_card_used,
        "retry_count":      0,   # incremented by auto-repair when enabled
    }, indent=2))

    # ---- POST-BUILD CHAIN ----
    # Each step degrades gracefully: failure does not block the response.

    # Phase 20c (2026-05-20): patch the generated next.config.mjs so its
    # `allowedDevOrigins` accepts 127.0.0.1/localhost. Without this, Next.js
    # 15.5+ logs a cross-origin warning for every /_next/* dev request, and
    # a future major version will block them outright. Idempotent — skips if
    # the LLM already added the field.
    try:
        patched = ensure_allowed_dev_origins(site_dir / "next.config.mjs")
        if patched:
            log.info("[postbuild] patched next.config.mjs with allowedDevOrigins")
    except Exception as e:
        log.warning("[postbuild] next.config.mjs patch failed: %s", e)

    imagen_results: dict = {"generated": {}, "files_touched": 0, "enabled": False}
    try:
        imagen_enabled = os.environ.get("PEBBLE_USE_IMAGEN", "").strip().lower() in {"1", "true", "yes", "on"}
        imagen_results["enabled"] = imagen_enabled
        if imagen_enabled and business_type:
            generated, touched = apply_imagen_to_site(business_type, site_dir)
            imagen_results["generated"] = generated
            imagen_results["files_touched"] = touched
    except Exception as e:
        imagen_results["error"] = str(e)

    # Auto-run (npm install + next dev) gated on PEBBLE_AUTO_RUN=true
    auto_run_enabled = os.environ.get("PEBBLE_AUTO_RUN", "").strip().lower() in {"1", "true", "yes", "on"}
    server_info: dict = {"enabled": auto_run_enabled, "port": None, "url": None, "errors": []}
    screenshot_info: dict = {"screenshots": [], "errors": []}
    if auto_run_enabled and answers.get("output_mode") != "lite":
        try:
            # Phase 13f.2 (2026-05-21) — if the streaming-loop's early-start
            # thread already brought next dev up + registered it in
            # dev_registry, don't start a SECOND dev server (would compete
            # for the slug, register a second port, leave a zombie process).
            # The early-start thread is daemon + already wired the URL.
            from pebble.server.dev_registry import get_url as _get_dev_url
            existing_url = _get_dev_url(slug)
            if existing_url:
                server_info["url"] = existing_url
                _warmup = locals().get("warmup")
                if _warmup and _warmup.elapsed_seconds is not None:
                    log.info("[postbuild] dev server already running at %s (early-start) — install was %.1fs",
                             existing_url, _warmup.elapsed_seconds)
                else:
                    log.info("[postbuild] dev server already running at %s (early-start)", existing_url)
            else:
                # Phase 13f: prefer the warmup-aware path when we have a warmup
                # instance (set by the streaming loop earlier). Falls back to
                # the cold-start path when streaming wasn't used (Gemini /
                # Anthropic non-streaming).
                _warmup = locals().get("warmup")
                if _warmup is not None and _warmup.started:
                    from pebble.server.preview_warmup import start_next_dev_after_install
                    server_info.update(start_next_dev_after_install(site_dir, _warmup))
                    if _warmup.elapsed_seconds is not None:
                        log.info("[postbuild] npm install was %.1fs (parallel with LLM stream)",
                                 _warmup.elapsed_seconds)
                else:
                    server_info.update(post_build_run_dev_server(site_dir))
        except Exception as e:
            server_info["errors"].append(f"dev server crashed: {e}")
        if server_info.get("url"):
            try:
                from pebble.server.dev_registry import register as _reg_dev
                _reg_dev(slug, server_info["url"])
            except Exception:
                pass
            # Phase A.5: now that next dev is up + registered, surface
            # preview_ready as the HONEST event the frontend was waiting
            # for. Frontend hides the button until this fires.
            _emit("preview_ready", {
                "slug": slug,
                "url": f"/preview/{slug}/",
            })
            try:
                screenshot_info = post_build_screenshots(server_info["url"], out_dir)
            except Exception as e:
                screenshot_info["errors"].append(f"screenshot crashed: {e}")

    # Auto-repair (eval + critique-and-fix loop) gated on PEBBLE_AUTO_REPAIR=true.
    # Off by default — repair costs another LLM round-trip per failed build,
    # which the engine should not charge for unless the operator opts in.
    auto_repair_enabled = os.environ.get("PEBBLE_AUTO_REPAIR", "").strip().lower() in {"1", "true", "yes", "on"}
    repair_info: dict = {"enabled": auto_repair_enabled}
    if auto_repair_enabled and answers.get("output_mode") != "lite" and written:
        _emit("evaluating", {})
        try:
            from pebble.repair import repair_build as _repair_build
            rep = _repair_build(slug=slug, max_rounds=2, client=client, skip_compile=True)
            repair_info.update({
                "baseline_score": rep.baseline_score,
                "final_score": rep.final_score,
                "rounds": [
                    {
                        "round": r.round,
                        "score_before": r.score_before,
                        "score_after": r.score_after,
                        "kept": r.kept,
                        "failed_checks": r.failed_checks,
                        "files_written": r.files_written,
                    }
                    for r in rep.rounds
                ],
            })
        except Exception as e:
            repair_info["error"] = f"{type(e).__name__}: {e}"

    _response_payload = {
        "prompt": prompt, "warning_count": len(notes),
        "slug": slug, "saved_to": f"output/{slug}/",
        "files_written": written, "file_count": len(written),
        "site_path": f"output/{slug}/site/",
        "preview_url": f"/preview/{slug}/",
        "elapsed_seconds": round(elapsed, 1),
        "model": client.model,
        "industry_intel_key": industry_key,
        "imagen": imagen_results,
        "dev_server": server_info,
        "screenshots": screenshot_info,
        "repair": repair_info,
    }
    _emit("done", _response_payload)
    handler._json(200, _response_payload)
    # Per-user engagement signal (T17). Only fires on successful generation
    # (above this point any error short-circuits with a non-200 + return).
    # NEVER pass slug / business_type / industry / DNA — just the event name.
    _log_engagement(answers.get("_user_id"), "build_completed")

    # Post-first-build email drip (Ch 11.6). schedule_drip() is idempotent —
    # it no-ops if the drip file already exists, so rebuilds don't reset the
    # clock. Only fires for authenticated users whose email we resolved above.
    if answers.get("_user_id") and user_email:
        try:
            from pebble.email_drip import schedule_drip
            schedule_drip(
                user_id=answers["_user_id"],
                email=user_email,
                slug=slug,
            )
        except Exception as e:
            log.warning("email drip schedule failed: %s", e)
