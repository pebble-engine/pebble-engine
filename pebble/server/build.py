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
from pebble.visual_ids import inject_pebble_ids


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

    answers["_slug"] = _slugify(answers.get("business_name", "untitled"))

    business_type = answers.get("business_type", answers.get("industry", ""))
    industry_key, industry_intel = (None, None)
    if business_type:
        try:
            industry_key, industry_intel = resolve_industry_intel(business_type)
            if industry_intel:
                answers["_industry_intel_key"] = industry_key
        except Exception as e:
            log.warning("industry intel resolution failed: %s", e)

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
        "plan":         plan,
        "industry_key": industry_key,
        "dna_id":       design_dna.get("id") if design_dna else None,
    })


def run_build(handler, generate: bool) -> None:
    """Handle a build request. ``handler`` is a ``PebbleHandler`` instance;
    the JSON response is written via its ``_json`` helper."""
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

    slug = _slugify(answers.get("business_name", "untitled"))
    answers["_slug"] = slug
    if "_created_at" not in answers:
        answers["_created_at"] = datetime.now().isoformat()

    # Stamp the owner if the request carries a session cookie. Anonymous
    # generation still works (current MVP behavior); auth-enabled users
    # get their projects scoped on the dashboard.
    try:
        from pebble.server.auth import current_user_id
        owner = current_user_id(handler)
        if owner:
            answers["_user_id"] = owner
    except Exception as e:
        log.warning("user id resolution failed: %s", e)

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

    # Style DNA — random per-build aesthetic personality. Same business +
    # same industry generates a different-looking site each time because the
    # DNA dictates fonts, hero structure, motion, and layout posture.
    # Honors `_design_dna_id` in the brief when the Plan-review UI has
    # already locked in a style.
    design_dna = None
    if _DNA_OK:
        design_dna = _select_dna(answers, pick_random_dna, pe.pick_dna_by_id)
        if design_dna:
            answers["_design_dna"] = design_dna["id"]
            log.info("Design DNA: %s (%s)", design_dna['label'], design_dna['id'])

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

    try:
        is_lite = answers.get("output_mode") == "lite"
        format_instruction = LITE_FILE_FORMAT_INSTRUCTION if is_lite else FILE_FORMAT_INSTRUCTION
        full_user = prompt + format_instruction

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

                "If you are uncertain about any detail not in the brief, make the best decision and build. "
                "The owner reviews the output. You are not the reviewer."
            )
        t0 = time.time()
        _max_tok = 8000 if answers.get("output_mode") == "lite" else 32000
        vision_images = (design_reference or {}).get("_raw_attachments") if design_reference else None
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

    site_dir = out_dir / "site"
    # Snapshot the previous build BEFORE overwriting — gives the user a
    # rollback target even on full regenerations. snapshot_site() is a no-op
    # when site/ doesn't exist or is empty, so first-time builds skip cleanly.
    try:
        snapshot_site(slug, reason="generate", source="POST /api/generate (pre-overwrite)")
    except Exception as e:
        log.warning("history snapshot failed: %s", e)
    site_dir.mkdir(exist_ok=True)
    written: list[str] = []
    for path, content in files:
        safe = path.lstrip("/\\")
        if ".." in Path(safe).parts or safe.startswith("/"):
            continue
        full = site_dir / safe
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        written.append(safe)

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
            server_info.update(post_build_run_dev_server(site_dir))
        except Exception as e:
            server_info["errors"].append(f"dev server crashed: {e}")
        if server_info.get("url"):
            try:
                from pebble.server.dev_registry import register as _reg_dev
                _reg_dev(slug, server_info["url"])
            except Exception:
                pass
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

    handler._json(200, {
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
    })
    # Per-user engagement signal (T17). Only fires on successful generation
    # (above this point any error short-circuits with a non-200 + return).
    # NEVER pass slug / business_type / industry / DNA — just the event name.
    _log_engagement(answers.get("_user_id"), "build_completed")
