#!/usr/bin/env python3
"""
Pebble Engine -- local briefing engine for websites that don't look generated.

USAGE
    python3 pebble_engine.py                # default port 8000
    python3 pebble_engine.py --port 8765    # custom port

OPTIONAL DEPS (for auto-build mode only)
    pip install -r requirements.txt

CONFIG (for auto-build mode only)
    Copy .env.example to .env and fill in your provider + API key.
    Default provider is Gemini (use your Google AI Ultra key).
    Switch to Claude Opus for premium runs: PEBBLE_PROVIDER=anthropic

The quiz, brief generator, anti-slop audit, and prompt download all work
without any of these. The auto-build feature is the only thing that
requires the provider packages and API keys.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from pathlib import Path
from typing import Optional

# Logger — set up early so any module-level code can use it. Independent of
# the rest of the pebble/ package (no circular import risk).
from pebble.log import log

# --------------------------------------------------------------------------
# PATHS
# --------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.resolve()
UIUX_SCRIPTS = PROJECT_ROOT / "skills" / "ui-ux-pro-max" / "scripts"
OUTPUT_DIR = PROJECT_ROOT / "output"
RESEARCH_CACHE_DIR = OUTPUT_DIR / "research_cache"
INDUSTRIES_JSON = PROJECT_ROOT / "industries.json"
sys.path.insert(0, str(UIUX_SCRIPTS))


# --------------------------------------------------------------------------
# .env LOADER (stdlib-only, no python-dotenv dep)
# --------------------------------------------------------------------------

def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        # Override empty-string env vars too — Windows / PowerShell often leaks
        # `KEY=""` into child processes, which would otherwise mask the .env value.
        if key and (key not in os.environ or not os.environ[key].strip()):
            os.environ[key] = val

load_env_file(PROJECT_ROOT / ".env")


# --------------------------------------------------------------------------
# SENTRY ERROR MONITORING (gated on SENTRY_DSN — no-op if unset)
# --------------------------------------------------------------------------
# Runs immediately after .env load so DSN is available, but before optional
# imports so any failure there is captured. Init is cheap and idempotent.
#
# Defaults intentionally tuned for the free Developer tier (5K errors,
# 5M spans, 50 replays / month) and Pebble's PII posture:
#   - send_default_pii=False — overrides Sentry's onboarding default;
#     matches the email-redaction posture set during the 2026-05-22
#     overnight bug hunt (no full emails in engine.err.log either).
#   - traces_sample_rate from env, default 1.0 in dev / 0.1 in prod.
#   - profile_session_sample_rate=0.0 — disabled (24/7 server would
#     produce more profiling data than the free quota allows).
#   - enable_logs=False — Python logging volume from the build pipeline
#     would flood the event quota. Errors still captured via the default
#     exception integration.
#
# before_send hook scrubs known secret patterns (Stripe / Anthropic /
# Supabase / OpenRouter / webhook secrets) and full email addresses from
# event payloads — defense-in-depth on top of send_default_pii=False.

_SENTRY_DSN = os.environ.get("SENTRY_DSN", "").strip()
if _SENTRY_DSN:
    try:
        import re as _re_sentry
        import sentry_sdk as _sentry_sdk

        _SENTRY_ENV = os.environ.get("SENTRY_ENVIRONMENT", "development").strip() or "development"
        _SENTRY_TRACES = float(os.environ.get(
            "SENTRY_TRACES_SAMPLE_RATE",
            "1.0" if _SENTRY_ENV == "development" else "0.1",
        ))

        # Patterns to scrub before anything ships to Sentry. Liberal on
        # purpose — false positives here are cosmetic; false negatives
        # leak secrets. Keep in sync with .env keys that hold secrets.
        _SENTRY_SCRUBBERS = [
            (_re_sentry.compile(r"sk-ant-api\d+-[A-Za-z0-9_-]{40,}"),  "<ANTHROPIC_KEY>"),
            (_re_sentry.compile(r"sk_(test|live)_[A-Za-z0-9]{20,}"),    "<STRIPE_SK>"),
            (_re_sentry.compile(r"rk_(test|live)_[A-Za-z0-9]{20,}"),    "<STRIPE_RK>"),
            (_re_sentry.compile(r"whsec_[A-Za-z0-9]{20,}"),             "<WEBHOOK_SECRET>"),
            # Supabase service-role / user JWTs (3-segment base64url)
            (_re_sentry.compile(r"eyJ[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{20,}"),
                                                                         "<JWT>"),
            (_re_sentry.compile(r"sk-or-v1-[A-Za-z0-9]{40,}"),          "<OPENROUTER_KEY>"),
            # Email redaction — keep first char + domain for triage
            (_re_sentry.compile(r"\b([A-Za-z0-9_.+-])[A-Za-z0-9_.+-]*@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b"),
                                                                         r"\1***@\2"),
        ]

        def _sentry_scrub(value):
            """Recursively walk event dicts/lists/strings, redacting matches."""
            if isinstance(value, str):
                for pattern, replacement in _SENTRY_SCRUBBERS:
                    value = pattern.sub(replacement, value)
                return value
            if isinstance(value, dict):
                return {k: _sentry_scrub(v) for k, v in value.items()}
            if isinstance(value, (list, tuple)):
                return type(value)(_sentry_scrub(v) for v in value)
            return value

        def _sentry_before_send(event, _hint):
            # Wrap in try so a scrubber bug never blocks error reporting.
            try:
                return _sentry_scrub(event)
            except Exception:
                return event

        _sentry_sdk.init(
            dsn=_SENTRY_DSN,
            environment=_SENTRY_ENV,
            release=os.environ.get("SENTRY_RELEASE") or None,
            send_default_pii=False,
            traces_sample_rate=_SENTRY_TRACES,
            profile_session_sample_rate=0.0,
            enable_logs=False,
            before_send=_sentry_before_send,
        )
    except Exception as _sentry_init_err:
        # Sentry being unavailable must NEVER prevent the engine from
        # booting. Log to the engine's own stderr (engine.err.log) and
        # carry on — the worst case is "no error reporting today."
        print(f"[sentry] init skipped (not fatal): {_sentry_init_err}",
              file=sys.stderr)


# --------------------------------------------------------------------------
# OPTIONAL IMPORTS
# --------------------------------------------------------------------------

try:
    from design_system import generate_design_system  # type: ignore
    _ENGINE_OK = True
except Exception:
    generate_design_system = None
    _ENGINE_OK = False

# Style DNA — per-build aesthetic personality picker. Lives at project root.
try:
    from style_dna import pick_random_dna, pick_dna_by_id, build_dna_block  # type: ignore
    _DNA_OK = True
except Exception:
    pick_random_dna = None
    pick_dna_by_id = None
    build_dna_block = None
    _DNA_OK = False

# Layout DNA — structural architecture picker. Lives in pebble/layout_dna.py.
try:
    from pebble.layout_dna import (  # type: ignore
        pick_layout_for_brief,
        pick_layout_by_id,
        build_layout_block,
    )
    _LAYOUT_DNA_OK = True
except Exception:
    pick_layout_for_brief = None  # type: ignore
    pick_layout_by_id = None       # type: ignore
    build_layout_block = None      # type: ignore
    _LAYOUT_DNA_OK = False

# Seed-brief library — hand-curated reference briefs per top industry.
# Injected into the prompt as a STYLE/SPECIFICITY anchor (not a template
# to copy). Highest-leverage first-build accuracy move per NLM review.
try:
    from pebble.seed_briefs import (  # type: ignore
        get_seed_brief,
        build_seed_brief_block,
    )
    _SEED_BRIEFS_OK = True
except Exception:
    get_seed_brief = None             # type: ignore
    build_seed_brief_block = None     # type: ignore
    _SEED_BRIEFS_OK = False

try:
    from anthropic import Anthropic  # type: ignore
    _ANTHROPIC_OK = True
except Exception:
    Anthropic = None  # type: ignore
    _ANTHROPIC_OK = False

try:
    from google import genai as _genai                     # type: ignore
    from google.genai import types as _genai_types         # type: ignore
    _GOOGLE_OK = True
except Exception:
    _genai = None                                          # type: ignore
    _genai_types = None                                    # type: ignore
    _GOOGLE_OK = False


# --------------------------------------------------------------------------
# ANTI-SLOP AUDIT
# Extracted to pebble/audit.py — re-exported here so existing `pe.X`
# accessors in pebble/server/build.py keep working unchanged.
# --------------------------------------------------------------------------

from pebble.audit import (  # noqa: E402
    audit_design_system,
    CONVERGENCE_FONTS,
    ACCEPTABLE_DISPLAY_PAIRS,
    WATCH_STYLES,
    _extract_field,
)


# --------------------------------------------------------------------------
# QUERY SYNTHESIS
# --------------------------------------------------------------------------

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "of", "in", "on", "at",
    "to", "for", "with", "by", "from", "as", "is", "it", "this",
    "that", "be", "are", "was", "were", "feel", "feels", "should",
    "like", "look", "looks", "if", "than", "more", "less",
}


def build_ui_query(answers: dict) -> str:
    parts = [
        answers.get("business_type", "") or answers.get("industry", ""),
        _distill(answers.get("visitor_action", "")),
        _distill(answers.get("extra_context", "")),
    ]
    return " ".join(p for p in parts if p)[:200]


def _distill(sentence: str) -> str:
    words = re.findall(r"[A-Za-z]+", sentence.lower())
    return " ".join(w for w in words if w not in STOP_WORDS and len(w) > 2)


def _slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-") or "untitled"


# --------------------------------------------------------------------------
# REQUEST VALIDATION
# Server-side defense for /api/build and /api/generate. The quiz UI does its
# own client-side checks, but anyone can POST raw to the engine — bound the
# payload, require the slug-driving field, and reject obvious garbage before
# we spend tokens on it.
# --------------------------------------------------------------------------

MAX_REQUEST_BYTES = 30 * 1024 * 1024       # 30 MB request envelope (5 images + headroom)
MAX_ATTACHMENT_BYTES = 20 * 1024 * 1024    # 20 MB total base64 across all uploaded design refs
MAX_ATTACHMENT_COUNT = 5

# Per-field character caps. Generous but bounded. Most fields are short answers
# from the quiz; long free-form ones (extra_context, services_offered) get a wider cap.
_STRING_LIMITS = {
    "business_name":     200,
    "business_type":     200,
    "industry":          200,
    "audience":          500,
    "location":          500,
    "services_offered":  5000,
    "phone":             200,
    "email":             500,
    "address":           1000,
    "brand_position":    200,
    "brand_tone":        200,
    "booking_system":    200,
    "payment_system":    200,
    "figma_url":         1000,
    "reference_url":     1000,
    "reference_url_2":   1000,
    "reference_url_3":   1000,
    "extra_context":        10000,
    "visitor_action":       5000,
    "output_mode":          50,
    # Free-text creative direction — injected at top of prompt with override priority.
    # 500 chars is enough for "make it minimal and photo-heavy, feels like a Kinfolk
    # magazine" without opening an injection vector.
    "creative_direction":   500,
}


def _validation_error(field: str, message: str) -> dict:
    return {"error": message, "field": field}


def validate_build_payload(answers):
    """Validate a /api/build or /api/generate JSON payload.

    Returns ``(cleaned_dict, None)`` on success or ``(None, error_dict)`` on
    failure. Error dicts are JSON-shaped ``{"error": str, "field": str}`` so
    the UI can highlight the offending input.

    Strict on the two fields that drive everything (business_name +
    business_type/industry) and on attachment size. Permissive elsewhere —
    coerces non-string scalars and ignores unknown keys, since the quiz schema
    changes more often than this validator does.
    """
    if not isinstance(answers, dict):
        return None, _validation_error("_root", "payload must be a JSON object")

    name = answers.get("business_name")
    if not isinstance(name, str) or not name.strip():
        return None, _validation_error("business_name", "business_name is required")
    if len(name) > _STRING_LIMITS["business_name"]:
        return None, _validation_error("business_name", f"business_name must be ≤ {_STRING_LIMITS['business_name']} chars")

    btype = answers.get("business_type") or answers.get("industry") or ""
    if not isinstance(btype, str) or not btype.strip():
        # Phase 58b — the welcome-phase fast-path (Phase 56a) skips the
        # questionnaire, so it doesn't collect business_type explicitly.
        # extra_context typically contains enough signal ("thai restaurant
        # in seattle") for the IndustryIntelligence layer to infer the
        # industry downstream. Accept extra_context as the fallback so
        # those builds aren't rejected at the validation gate.
        extra = answers.get("extra_context") or ""
        if isinstance(extra, str) and extra.strip():
            # Promote extra_context to business_type so all downstream
            # consumers (industry lookup, prompt assembly, slug) see a
            # value. The industry inference will produce a snake_case
            # key from this free-text below.
            answers["business_type"] = extra.strip()
        else:
            return None, _validation_error("business_type", "business_type (or industry) is required")

    for field, cap in _STRING_LIMITS.items():
        val = answers.get(field)
        if val is None or val == "":
            continue
        # The v3 questionnaire collects multi-select chips (audience,
        # services_offered, etc.) as arrays. The engine + prompt template
        # both want a single string per field. Coerce here so legacy
        # callers AND the v3 client work without changing either side.
        if isinstance(val, list):
            if not all(isinstance(item, (str, int, float, bool)) for item in val):
                return None, _validation_error(field, f"{field} list items must be strings or numbers")
            val = ", ".join(str(item).strip() for item in val if str(item).strip())
            answers[field] = val
            if not val:
                # Empty after coercion — treat the same as unset.
                continue
        if not isinstance(val, (str, int, float, bool)):
            return None, _validation_error(field, f"{field} must be a string")
        if not isinstance(val, str):
            val = str(val)
            answers[field] = val
        if len(val) > cap:
            return None, _validation_error(field, f"{field} must be ≤ {cap} chars")

    fns = answers.get("site_functions")
    if fns is not None and fns != "":
        if not isinstance(fns, list):
            return None, _validation_error("site_functions", "site_functions must be a list")
        if len(fns) > 50:
            return None, _validation_error("site_functions", "site_functions has too many entries (max 50)")
        for i, item in enumerate(fns):
            if not isinstance(item, str):
                return None, _validation_error("site_functions", f"site_functions[{i}] must be a string")
            if len(item) > 200:
                return None, _validation_error("site_functions", f"site_functions[{i}] too long (max 200)")

    imgs = answers.get("design_reference_images")
    if imgs is not None and imgs != "":
        if not isinstance(imgs, list):
            return None, _validation_error("design_reference_images", "design_reference_images must be a list")
        if len(imgs) > MAX_ATTACHMENT_COUNT:
            return None, _validation_error("design_reference_images", f"too many attachments (max {MAX_ATTACHMENT_COUNT})")
        total_bytes = 0
        for i, img in enumerate(imgs):
            if not isinstance(img, dict):
                return None, _validation_error("design_reference_images", f"image[{i}] must be an object")
            mt = img.get("media_type")
            data = img.get("data")
            if not isinstance(mt, str) or not mt.startswith("image/"):
                return None, _validation_error("design_reference_images", f"image[{i}].media_type must be an image/* MIME type")
            if not isinstance(data, str):
                return None, _validation_error("design_reference_images", f"image[{i}].data must be a base64 string")
            total_bytes += len(data)
            if total_bytes > MAX_ATTACHMENT_BYTES:
                mb = MAX_ATTACHMENT_BYTES // (1024 * 1024)
                return None, _validation_error("design_reference_images", f"image attachments exceed {mb} MB total")

    return answers, None


# --------------------------------------------------------------------------
# GEMINI IMAGEN — AI image generation
# Generates industry-specific images when PEBBLE_USE_IMAGEN=true.
# No faces visible; back-view or no-people compositions only.
# --------------------------------------------------------------------------

# Where each image slot is saved on disk (relative to public/), matching the
# conventions in skills/stack/SKILL.md so LLM-emitted <Image src=...> paths
# line up with the actual files. If you add a slot, add its path here too.
_SLOT_TO_PATH: dict[str, str] = {
    "hero":      "images/hero/hero.jpg",
    "service_1": "images/services/service-1.jpg",
    "service_2": "images/services/service-2.jpg",
    "service_3": "images/services/service-3.jpg",
    "team_1":    "images/about/team-1.jpg",
    "team_2":    "images/about/team-2.jpg",
    "gallery_1": "images/gallery/01.jpg",
    "gallery_2": "images/gallery/02.jpg",
}


def _imagen_prompt(industry: str, slot: str) -> str:
    """Build an industry-aware Imagen prompt for a given image slot."""
    slot_contexts = {
        "hero":      "wide cinematic establishing shot, environmental focus",
        "service_1": "detail shot, tools or workspace, no people visible",
        "service_2": "process or technique close-up, hands-only if any people",
        "service_3": "results or finished work, clean composition",
        "team_1":    "back view of professional at work, no face visible",
        "team_2":    "over-the-shoulder workspace view, no face visible",
        "gallery_1": "before/after or portfolio piece, no people",
        "gallery_2": "atmospheric environment shot, no people",
    }
    context = slot_contexts.get(slot, "professional scene, no people visible")
    return (
        f"{industry} professional scene, {context}, "
        "back view or no people visible, photorealistic, commercial photography style, "
        "soft natural light, 4k, ultra detailed, no text, no logos, no faces"
    )


def generate_imagen_images(industry: str, output_dir: Path, slots: list[str] = None) -> dict[str, str]:
    """Generate industry-aware images via Gemini Imagen and save to output_dir.

    Returns a dict mapping slot name to the local path (relative to site root),
    e.g. {"hero": "/images/hero.jpg"}. Slots that fail are simply omitted.
    """
    if not _GOOGLE_OK:
        log.warning("Imagen: google-genai not installed, skipping")
        return {}
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        log.warning("Imagen: GOOGLE_API_KEY not set, skipping")
        return {}

    slots = slots or ["hero", "service_1", "service_2", "service_3",
                      "team_1", "team_2", "gallery_1", "gallery_2"]
    images_dir = output_dir / "public" / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    try:
        client = _genai.Client(api_key=api_key)
    except Exception as e:
        log.warning("Imagen client init failed: %s", e)
        return {}

    results: dict[str, str] = {}
    for slot in slots:
        prompt = _imagen_prompt(industry, slot)
        try:
            # Imagen 3 — Gemini API
            # Imagen 4 (imagen-3 was retired). Falls back gracefully if quota hits.
            response = client.models.generate_images(
                model="imagen-4.0-generate-001",
                prompt=prompt,
                config=_genai_types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="16:9" if slot in {"hero", "gallery_1", "gallery_2"} else "4:3",
                ),
            )
            if not response.generated_images:
                continue
            img_bytes = response.generated_images[0].image.image_bytes
            # Save at the Stack-Skill-conventional path (subfolder + hyphenated
            # filename) so the LLM-generated <Image src="..."> tags resolve.
            rel_path = _SLOT_TO_PATH.get(slot, f"images/{slot}.jpg")
            dest = output_dir / "public" / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(img_bytes)
            results[slot] = "/" + rel_path
            log.info("Imagen: %s → %s", slot, rel_path)
        except Exception as e:
            # Skip the slot but keep going
            log.warning("Imagen: %s failed (%s: %s)", slot, type(e).__name__, e)
            continue

    return results


def replace_urls_in_site(site_dir: Path, url_map: dict[str, str]) -> int:
    """Replace each (old → new) URL pair in every text file under site_dir.

    Returns the count of file-level replacements made.
    """
    if not url_map or not site_dir.exists():
        return 0
    extensions = {".tsx", ".ts", ".jsx", ".js", ".html", ".css", ".json", ".md", ".mdx"}
    touched_files = 0
    for f in site_dir.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in extensions:
            continue
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue
        original = content
        for old, new in url_map.items():
            if old and old in content:
                content = content.replace(old, new)
        if content != original:
            f.write_text(content, encoding="utf-8")
            touched_files += 1
    return touched_files


def apply_imagen_to_site(industry: str, site_dir: Path) -> tuple[dict[str, str], int]:
    """Generate Imagen images for the standard slots and write them under
    `site_dir/public/images/`.

    Returns (generated_slot_to_path_map, files_touched).
    Gated on PEBBLE_USE_IMAGEN=true (defaults off to avoid surprise costs).
    """
    enabled = os.environ.get("PEBBLE_USE_IMAGEN", "").strip().lower() in {"1", "true", "yes", "on"}
    if not enabled:
        return {}, 0
    if not industry:
        return {}, 0
    slots = ["hero", "service_1", "service_2", "service_3",
             "team_1", "team_2", "gallery_1", "gallery_2"]
    generated = generate_imagen_images(industry, site_dir, slots=slots)
    if not generated:
        return {}, 0
    # Safety net: if the LLM emitted the legacy flat path (`/images/hero.jpg`,
    # `/images/service_1.jpg`) from the old prompt convention, rewrite to the
    # new subfolder path so the image actually loads. Identity entries are
    # skipped so we don't no-op replace correct paths.
    url_map = {}
    for slot, new_path in generated.items():
        legacy = f"/images/{slot}.jpg"
        if legacy != new_path:
            url_map[legacy] = new_path
    touched = replace_urls_in_site(site_dir, url_map)
    return generated, touched


# --------------------------------------------------------------------------
# POST-BUILD AUTOMATION
# After all files are written: npm install → next dev → poll → screenshots.
# Each step is gracefully skipped if the prerequisite isn't available.
# --------------------------------------------------------------------------

# Post-build chain extracted to pebble/postbuild.py (re-exported for back-compat).
from pebble.postbuild import (
    _find_free_port,
    _poll_server,
    post_build_run_dev_server,
    post_build_screenshots,
)


# --------------------------------------------------------------------------
# FIGMA — read a Figma file when the user provides a URL + token in .env
# Extracted to pebble/figma.py; re-exported here for pe.X back-compat.
# --------------------------------------------------------------------------

from pebble.figma import figma_file_summary, _FIGMA_FILE_RE  # noqa: E402


# --------------------------------------------------------------------------
# INDUSTRY RESEARCH SYSTEM
# --------------------------------------------------------------------------

# Industry intelligence + research extracted to pebble/industry.py.
# Re-exported here for back-compat (and so the existing test suite passes).
from pebble.industry import (
    INDUSTRY_RESEARCH_JSON_PROMPT,
    RESEARCH_PROMPT_TEMPLATE,
    _load_industries_intel,
    _industry_key,
    lookup_industry_intel,
    research_new_industry,
    resolve_industry_intel,
    research_industry,
    build_industry_intel_block,
    build_pages_block,
)


# --------------------------------------------------------------------------
# BUSINESS INTELLIGENCE SKILL LOADER
# --------------------------------------------------------------------------

# Skill files loaded into the prompt at import time. If we want a new skill
# in the future, add it to the prompt template AND to this list in the same
# commit so there are no dead loads.
BI_SKILL_PATH    = PROJECT_ROOT / "skills" / "business-intelligence" / "SKILL.md"
STACK_SKILL_PATH = PROJECT_ROOT / "skills" / "stack" / "SKILL.md"
IOS_SKILL_PATH   = PROJECT_ROOT / "skills" / "ios" / "SKILL.md"
NS_SKILL_PATH    = PROJECT_ROOT / "skills" / "no-slop-web" / "SKILL.md"


def _read_skill(path: Path) -> str:
    """Read a skill file if present; return '' if missing.

    Replaces four near-identical loaders (load_business_intelligence,
    load_stack_skill, load_ios_skill, load_no_slop_skill) with one.
    """
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


_BI_SKILL    = _read_skill(BI_SKILL_PATH)
_STACK_SKILL = _read_skill(STACK_SKILL_PATH)
_IOS_SKILL   = _read_skill(IOS_SKILL_PATH)
_NS_SKILL    = _read_skill(NS_SKILL_PATH)


# --------------------------------------------------------------------------
# RESOLVED DESIGN CONTRACT
# Maps quiz answers → concrete, non-negotiable values before any skill fires.
# Visual experience is ALWAYS cinematic — it is no longer a user choice.
# --------------------------------------------------------------------------

_FONT_BY_POSITION = {
    "premium":      ("Fraunces",         "light/thin weight (300–400) — luxury lives in restraint; wide tracking"),
    "professional": ("Fraunces",         "semibold (600) — editorial authority; pairs with Inter body"),
    "accessible":   ("Lora",             "regular/medium — warm humanist serif, approachable and credible"),
    "budget":       ("Manrope",          "extrabold (800) — direct, confident, no subtlety needed"),
}

_PALETTE_BY_POSITION = {
    # (bg, surface, text, dark_default)
    "premium":      ("#0A0A0A", "#1A1A1A", "#F9FAFB", "Yes"),
    "professional": ("#FFFFFF", "#F9FAFB", "#111827", "No"),
    "accessible":   ("#F5EFE6", "#FFFFFF", "#1A1A1A", "No"),
    "budget":       ("#FFFFFF", "#F9FAFB", "#111827", "No"),
}

_TONE_BY_BRAND = {
    "professional_formal":   "Authoritative and specific. Credentials, years, certifications. Declarative sentences. No filler.",
    "friendly_approachable": "Warm and conversational. Empathy before selling. 'We' language. CTAs are invitations: 'Let\\'s talk' not 'GET STARTED'.",
    "technical_expert":      "Data-driven and precise. Numbers, specs, methodology. Prove the claim — don't state it.",
    "creative_confident":    "Bold, opinionated, memorable. Strong verbs. Distinctive voice that sounds like a person, not a template.",
}

_CTA_BY_POSITION = {
    "premium":      "'Inquire' / 'Schedule a consultation' / 'Request access'",
    "professional": "'Book a free consultation' / 'Get a free quote' / 'Call us today'",
    "accessible":   "'Let\\'s talk' / 'Reach out' / 'Get started'",
    "budget":       "'Call now' / 'Get a quote' / 'Save today'",
}

# Visual is always cinematic — easing values hardcoded
_CINEMATIC = ("expo.out", "0.9s", "0.12s", "scroll-pinned sections allowed (`anticipatePin: 1`, `scrub: 1`)")

# Industries that default to dark background regardless of brand_position
_DARK_INDUSTRIES = {
    "luxury", "premium", "yacht", "jewelry", "bar", "nightclub",
    "photography", "auto detail", "car detail", "detailing", "club",
    "lounge", "studio", "agency", "tattoo", "cigar",
}
# Industries that default to warm-light background
_WARM_INDUSTRIES = {
    "yoga", "wellness", "dentist", "therapist", "bakery", "cafe",
    "spa", "massage", "florist", "counseling", "meditation",
}


def build_resolved_contract(answers: dict, industry_intel: Optional[dict] = None) -> str:
    brand_position = answers.get("brand_position", "professional").strip()
    brand_tone     = answers.get("brand_tone", "professional_formal").strip()
    industry       = answers.get("industry", answers.get("business_type", "")).lower()

    heading_font, font_note = _FONT_BY_POSITION.get(brand_position, _FONT_BY_POSITION["professional"])
    bg, surface, text_col, dark_default = _PALETTE_BY_POSITION.get(brand_position, _PALETTE_BY_POSITION["professional"])
    copy_tone    = _TONE_BY_BRAND.get(brand_tone, _TONE_BY_BRAND["professional_formal"])
    cta_examples = _CTA_BY_POSITION.get(brand_position, _CTA_BY_POSITION["professional"])
    easing, duration, stagger, scroll_pin = _CINEMATIC
    accent_col: Optional[str] = None
    intel_source = "quiz answers"

    # Industry overrides (legacy keyword sets)
    if any(w in industry for w in _DARK_INDUSTRIES) and dark_default == "No":
        bg, surface, text_col, dark_default = "#0A0A0A", "#1A1A1A", "#F9FAFB", "Yes"
    elif any(w in industry for w in _WARM_INDUSTRIES) and dark_default == "No":
        bg, surface, text_col = "#F5EFE6", "#FFFFFF", "#1A1A1A"

    # Industry intelligence overrides — colors, hero type, threejs come from industries.json
    intel_hero_type = None
    intel_threejs_type = "none"
    if industry_intel:
        intel_source = "industries.json (overrides quiz palette where present)"
        colors = industry_intel.get("colors", {}) or {}
        if colors.get("background"):
            bg = colors["background"]
            # Dark mode flag follows the chosen background
            try:
                hex_val = colors["background"].lstrip("#")
                r, g, b = int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16)
                luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
                dark_default = "Yes" if luma < 90 else "No"
                # Surface and text adjust to match background luma
                if dark_default == "Yes":
                    surface, text_col = "#1A1A1A", "#F9FAFB"
                else:
                    surface, text_col = "#FFFFFF", "#111827"
            except Exception:
                pass
        if colors.get("accent"):
            accent_col = colors["accent"]
        intel_hero_type = industry_intel.get("hero_type")
        intel_threejs_type = industry_intel.get("threejs_type", "none") or "none"

    # Video hero industries (legacy fallback)
    video_industries = {
        "auto detail", "detailing", "restaurant", "cafe", "fitness", "gym",
        "photography", "events", "wedding", "real estate", "construction",
        "beauty", "salon", "barbershop",
    }
    recommend_video = any(w in industry for w in video_industries)
    if intel_hero_type == "video":
        video_note = "Yes — `<video autoPlay muted loop playsInline>` with Pexels video from Section 8c"
    elif intel_hero_type == "image":
        video_note = "No — use full-bleed `next/image` with parallax (this industry reads as cinematic editorial, not motion)"
    elif recommend_video:
        video_note = "Yes — use `<video autoPlay muted loop playsInline>` with Pexels image poster"
    else:
        video_note = "Optional — use if client has footage; otherwise full-bleed image with parallax"

    threejs_note = "None — skip Three.js entirely; do not import it" if intel_threejs_type == "none" else f"`{intel_threejs_type}` variant — see Three.js Hero Patterns in Section 9"
    intel_primary = (industry_intel or {}).get("colors", {}).get("primary") if industry_intel else None
    primary_row = f"| **Brand primary** | `{intel_primary}` |\n" if intel_primary else ""
    accent_row = f"| **Accent color** | `{accent_col}` |\n" if accent_col else ""

    return f"""| Decision | Resolved Value |
|---|---|
| **Heading font** | Defer to the Design DNA block at the top of this prompt. (Legacy hint: {heading_font} — {font_note}. IGNORE this hint if it conflicts with the DNA.) |
| **Body font** | Defer to the Design DNA block. (Legacy default: Inter. IGNORE if DNA names a different body font.) |
| **Font loading** | Both via `next/font/google` in `layout.tsx`; both CSS variables on `<html>` |
| **Background** | `{bg}` |
| **Surface / card** | `{surface}` |
| **Text color** | `{text_col}` |
{primary_row}{accent_row}| **Dark mode** | {dark_default} |
| **Motion** | Defer to the Design DNA block's motion intensity. (Legacy default: cinematic — SplitText, clip-path, parallax. The DNA may downgrade this to subtle or upgrade to aggressive.) |
| **GSAP easing** | `{easing}` |
| **Duration** | `{duration}` per element · Stagger: `{stagger}` |
| **Scroll pinning** | {scroll_pin} |
| **Video hero** | {video_note} |
| **Three.js hero** | {threejs_note} |
| **Copy tone** | {copy_tone} |
| **CTA language** | {cta_examples} |

*Brand: `{brand_position}` · Tone: `{brand_tone}` · Visual: always cinematic · Source: {intel_source}*"""


# --------------------------------------------------------------------------
# PROMPT TEMPLATE  -- 11-section structure
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Helper: URL-extracted brand signals block (Phase 38d, 2026-05-21)
#
# When the v3 welcome-phase ran brand_extract against a URL, the brief gets
# stamped with `_extracted_*` derived fields. They flow indirectly into the
# prompt via the natural-language extra_context blob, but surfacing them
# here as named signals lets the LLM act on them more confidently —
# especially the `_inspire_source_url` case where the URL is reference-only
# and the LLM should NOT borrow business name / copy / pages from it.
# --------------------------------------------------------------------------


def _build_intent_block(answers: dict) -> str:
    """Render the brief's `intent` field as a focused prompt block.

    Phase 34 (2026-05-21). Two modes:

      "business" (default): the user is building a real site for a real
        business. Optimize for conversion: prominent CTAs, trust signals,
        pricing emphasis, SEO-focused metadata, real form wiring. This
        is the existing behavior — the block surfaces it explicitly so
        the LLM treats it as intentional rather than implicit.

      "project": the user is a developer / designer building a sandbox,
        portfolio, or experimental site. Optimize for craft: cleaner code
        with explicit structural comments, less aggressive CTAs, editorial
        layout latitude, Tailwind classes that read like a hand-written
        codebase rather than auto-generated soup. The audience is technical
        — they will read the source.

    Unknown / missing values fall back to "business" so legacy briefs
    don't suddenly shift behavior.
    """
    intent = (answers.get("intent") or "business").strip().lower()
    if intent not in ("business", "project"):
        intent = "business"

    if intent == "project":
        return (
            "**Build intent: PROJECT** (developer / designer sandbox).\n\n"
            "The user is technical — they will READ the source code. "
            "Optimize for craft over conversion:\n\n"
            "- Write components with clear, explicit structure. Add brief "
            "JSDoc-style comments at the top of each non-trivial component "
            "explaining what it does and why.\n"
            "- Keep Tailwind class lists in deliberate, readable groupings "
            "(layout → spacing → color → typography → state). Don't "
            "auto-compress into one giant string.\n"
            "- CTAs are present but understated — don't decorate every "
            "section with conversion bait. One primary CTA per page is "
            "plenty.\n"
            "- Editorial / portfolio / showcase layouts are encouraged. "
            "Skip the standard \"hero → features → social proof → CTA\" "
            "funnel template unless it genuinely fits.\n"
            "- Use the DNA card faithfully — project-mode users care about "
            "design fidelity more than the average SMB owner.\n"
            "- README.md should include a brief \"design notes\" section "
            "explaining the structural choices (DNA, motion intent, color "
            "system) — this audience appreciates the reasoning."
        )

    # business (default)
    return (
        "**Build intent: BUSINESS** (real site for a real business).\n\n"
        "The user is the business owner — non-technical, focused on "
        "outcomes. Optimize for conversion:\n\n"
        "- Every page should have a clear primary CTA above the fold.\n"
        "- Wire the contact form to the existing Resend Server Action — "
        "real working email, not a fake onSubmit.\n"
        "- Include trust-signal sections (testimonials placeholder, "
        "license / credential strip, social proof) where the industry "
        "calls for them.\n"
        "- Metadata: descriptive title, meta description, OG image, "
        "schema.org JSON-LD for the business.\n"
        "- Pricing / services should be specific enough that a visitor "
        "can decide — don't hide pricing behind \"contact for quote\" "
        "unless the industry genuinely requires it (legal, custom B2B).\n"
        "- Keep the source code clean but don't comment every line — the "
        "owner won't read it. Code is for Pebble's future refinements."
    )


def _build_url_extraction_block(answers: dict) -> str:
    """Render the URL-extracted brand signals as a focused prompt block.

    Returns the empty-state string when the brief has no URL extraction
    metadata, so the template's section heading never sits empty.
    """
    inspire_url   = (answers.get("_inspire_source_url") or "").strip()
    logo_url      = (answers.get("_extracted_logo_url") or "").strip()
    favicon_url   = (answers.get("_extracted_favicon_url") or "").strip()
    hero_copy     = (answers.get("_extracted_hero_copy") or "").strip()
    tagline_extr  = (answers.get("_extracted_tagline") or "").strip()
    palette       = answers.get("_brand_palette") or []
    dna_pinned    = (answers.get("_design_dna_id") or "").strip()

    has_any = bool(inspire_url or logo_url or favicon_url or hero_copy
                   or tagline_extr or palette or dna_pinned)
    if not has_any:
        return ("*(No URL was extracted — generate brand identity from the "
                "questionnaire fields alone.)*")

    parts: list[str] = []

    if inspire_url:
        parts.append(
            f"**Inspiration source URL:** `{inspire_url}`\n\n"
            "The user pasted this URL as a STYLE REFERENCE — capture its "
            "visual feel (palette, layout, motion, typography intensity), "
            "but do NOT borrow the business name, copy, services, or page "
            "structure from it. The business identity comes from the "
            "questionnaire fields above. The pinned design DNA below was "
            "matched against this URL's vibe."
        )

    if logo_url:
        parts.append(
            f"**Existing logo URL (visual reference):** `{logo_url}` — "
            "look at the dominant color and shape language as inspiration "
            "for `/app/icon.svg`. Do NOT embed this URL anywhere in the "
            "generated site; produce `/app/icon.svg` locally per the "
            "favicon eval."
        )
    elif favicon_url:
        parts.append(f"**Existing favicon (visual reference only):** `{favicon_url}`")

    if tagline_extr and not inspire_url:
        parts.append(
            f"**Existing tagline from the user's site:** \"{tagline_extr}\" "
            "— adapt and refine for the new build, don't copy verbatim."
        )

    if hero_copy and not inspire_url:
        parts.append(
            f"**Existing hero copy from the user's site:** \"{hero_copy}\" "
            "— use as creative direction for the new h1; rewrite to fit "
            "the DNA's voice if needed."
        )

    if palette:
        palette_str = ", ".join(p for p in palette if isinstance(p, str))
        if palette_str:
            origin = "the inspiration site" if inspire_url else "the user's existing site"
            parts.append(
                f"**Brand palette extracted from {origin}:** {palette_str}. "
                "Use these as the dominant palette unless the chosen Style "
                "DNA card explicitly defines its own (in which case the "
                "DNA wins — this is just signal, not a hard requirement)."
            )

    if dna_pinned:
        parts.append(
            f"**Pinned Style DNA from the extractor:** `{dna_pinned}` — "
            "the inspire-mode matcher chose this DNA card based on the "
            "URL's visual vibe. The Style DNA block earlier in this "
            "prompt is authoritative; this line is the rationale."
        )

    return "\n\n".join(parts)


# --------------------------------------------------------------------------
# PROMPT TEMPLATE  -- 11-section structure
#
# The template body lives in skills/prompt_template.md so it can be edited
# without bouncing Python and so the f-string escapes are reviewable as a
# real Markdown file (preview it in any editor). At runtime we still pass
# it through str.format(), which is why literal braces in code samples are
# doubled — {{ and }} — inside the .md file.
# --------------------------------------------------------------------------

_PROMPT_TEMPLATE_PATH = PROJECT_ROOT / 'skills' / 'prompt_template.md'
if not _PROMPT_TEMPLATE_PATH.exists():
    raise FileNotFoundError(
        f'Pebble Engine cannot start: {_PROMPT_TEMPLATE_PATH} is missing. '
        'This file is the master prompt the engine renders for every build.'
    )
PROMPT_TEMPLATE = _PROMPT_TEMPLATE_PATH.read_text(encoding='utf-8')




def build_prompt(
    answers: dict,
    ds_text: str,
    notes: list[tuple[str, str]],
    research_text: str = "",
    industry_intel: Optional[dict] = None,
    design_reference: Optional[dict] = None,
    design_dna: Optional[dict] = None,
    language: Optional[str] = None,
) -> str:
    # Map quiz fields -> template variables
    industry = answers.get("industry", answers.get("business_type", ""))
    fns = answers.get("site_functions") or []
    fn_labels = {
        "booking":   "online booking / appointments",
        "payment":   "online payment collection",
        "portfolio": "portfolio / gallery of past work",
        "leads":     "lead capture / contact form",
        "ecommerce": "e-commerce / online store",
        "presence":  "business presence (hours, location, contact)",
    }
    visitor_action = "; ".join(fn_labels.get(f, f) for f in fns) if fns else "general presence"

    booking = answers.get("booking_system", "").strip()
    payment = answers.get("payment_system", "").strip()
    systems_parts = []
    if booking and booking.lower() not in {"", "none", "n/a", "none specified"}:
        systems_parts.append(f"Booking: {booking}")
    if payment and payment.lower() not in {"", "none", "n/a", "none specified"}:
        systems_parts.append(f"Payment: {payment}")
    booking_str = " . ".join(systems_parts) if systems_parts else "None yet -- recommend the best option for this business type."

    extra = answers.get("extra_context", "").strip()
    extra_block = extra if extra else "*(No extra context provided — use the Business Intelligence skill to fill in industry best practices.)*"

    # Phase 38d (2026-05-21) — URL-extracted brand signals block.
    # When the user pasted a URL into the v3 welcome-phase, brand_extract
    # stamps the brief with `_extracted_logo_url`, `_extracted_hero_copy`,
    # `_extracted_tagline`, `_brand_palette`, `_inspire_source_url`, and
    # (inspire mode) `_design_dna_id`. They're already smushed into
    # extra_context as a natural-language blob, but surfacing them as
    # named signals here helps the LLM treat them with intent rather than
    # just reading them as user prose.
    url_extraction_block = _build_url_extraction_block(answers)

    # Phase 34 (2026-05-21) — build intent block (Business vs Project).
    # Default is "business"; Project mode is a one-click opt-in for
    # developers/designers building portfolios or sandboxes.
    intent_block = _build_intent_block(answers)

    # Reference URLs / inspiration sites (up to 3)
    _skip = {"", "none", "n/a", "no", "skip"}
    ref_urls = [
        answers.get("reference_url",   "").strip(),
        answers.get("reference_url_2", "").strip(),
        answers.get("reference_url_3", "").strip(),
    ]
    ref_urls = [u for u in ref_urls if u.lower() not in _skip]

    if len(ref_urls) == 1:
        reference_block = f"""A reference site has been provided: **{ref_urls[0]}**

Browse this URL before writing any code. Extract and apply:
- Dominant colors and color temperature (warm vs cool, light vs dark)
- Typography weight, rhythm, and personality
- Spacing philosophy — how tight or generous the layout feels
- Animation style and intensity
- Layout approach — grid, asymmetric, editorial, etc.
- Overall brand feeling

**Important:** Abstract the FEELING, not the layout. Do not copy structure or content from this site. Use it to calibrate the aesthetic direction only. If this is a Dribbble link, extract the visual composition and color mood."""
    elif len(ref_urls) >= 2:
        url_list = "\n".join(f"- **{u}**" for u in ref_urls)
        reference_block = f"""Multiple reference sites have been provided:

{url_list}

Browse all of them before writing any code. Your job is synthesis, not imitation:
1. Identify what they share — color temperature, spacing density, typography weight, animation pace
2. Note where they differ — these are stylistic choices, not requirements
3. Extract the overlap as the aesthetic baseline; apply it to this business's specific context

Extract and synthesize across all references:
- Dominant color temperature (warm vs cool, saturated vs muted)
- Typography personality (formal vs casual, heavy vs refined)
- Spacing rhythm — how generous or dense
- Animation energy — subtle or expressive
- Layout philosophy — structured grid vs editorial vs asymmetric

**Important:** Abstract the FEELING, not any single layout. Do not copy structure or content from these sites. The goal is a site that feels consistent with this aesthetic family — not a clone of any one reference."""
    else:
        reference_block = "*(No reference sites provided — infer aesthetic direction from the Resolved Design Contract and the Business Intelligence skill.)*"

    # Resolved design contract (pre-computed before any skill fires)
    resolved_contract = build_resolved_contract(answers, industry_intel)

    # Industry intelligence prompt block
    industry_intel_block = build_industry_intel_block(industry, industry_intel)

    # Industry-aware pages block — tells the LLM which pages to generate
    # beyond the 4 foundation pages, based on the industry's `pages` field
    # in industries.json. See pebble.industry.PAGE_CATALOG for the 11 page
    # types + 3 universal extras (FAQ, Privacy, Terms).
    pages_block = build_pages_block(industry_intel)

    # Design reference block (Figma file URL or uploaded screenshot)
    if design_reference and (design_reference.get("figma_url") or design_reference.get("image_count")):
        parts = []
        if design_reference.get("figma_url"):
            parts.append(f"**Figma file:** `{design_reference['figma_url']}` — the engine has access to this via FIGMA_ACCESS_TOKEN. Read the frames for layout, color, type rhythm, and component spacing. Do not copy literally; abstract the system.")
        if design_reference.get("image_count"):
            parts.append(f"**Reference screenshot(s) attached as vision input:** {design_reference['image_count']} image(s). Extract dominant colors, typography weight/personality, layout structure, and spacing rhythm. Match the visual *feeling*, not pixel-perfect layout.")
        design_reference_block = "\n\n".join(parts)
    else:
        design_reference_block = "*(No design reference provided — Industry Intelligence and Resolved Contract govern.)*"

    # Prompt Diet (Phase 14a, 2026-05-20) — gated by PEBBLE_PROMPT_DIET env var (default ON).
    # Per Qwen prompting research + audit findings, full SKILL.md injection adds
    # ~27K tokens of largely-redundant or DNA-contradicting content. Compact diet
    # versions distill each skill to load-bearing rules only.
    from pebble.prompt_diet import (
        diet_enabled,
        NO_SLOP_DIET,
        IOS_RULES_DIET,
        STACK_RULES_DIET,
        BUSINESS_INTEL_DIET,
        DESIGN_SYSTEM_DIET,
    )
    _DIET_ON = diet_enabled()

    # No-slop skill
    if _DIET_ON:
        no_slop_block = NO_SLOP_DIET
    elif _NS_SKILL:
        # The no-slop skill lists "acceptable display fonts" (Fraunces, Syne, etc.)
        # The Design DNA at the top of this prompt overrides that list — use the DNA's fonts
        # even if they're not on the no-slop list, and DO NOT use no-slop fonts if they
        # aren't named by the DNA. The rest of the no-slop rules (no fake testimonials,
        # no convergence Inter/Poppins as display, no "Where X meets Y" copy) still apply.
        no_slop_block = "\n\n*(NOTE: The Design DNA block at the top of this prompt overrides the font list below. Use the DNA's display/body/mono fonts. All other no-slop rules apply.)*\n\n" + _NS_SKILL.strip() + "\n"
    else:
        no_slop_block = "\n*(No-slop skill not loaded — apply general quality rules: no 555 phone numbers, no 'Where X meets Y' subtext, no vague superlatives, hero must have visual element.)*\n"

    # iOS skill
    if _DIET_ON:
        ios_skill_block = IOS_RULES_DIET
    elif _IOS_SKILL:
        ios_skill_block = f"\n\n{_IOS_SKILL.strip()}\n"
    else:
        ios_skill_block = "\n*(iOS skill not loaded -- apply standard iOS Safari fixes: 100dvh, normalizeScroll, muted playsInline video, 16px inputs, safe-area-inset.)*\n"

    # Stack skill
    if _DIET_ON:
        stack_block = STACK_RULES_DIET
    elif _STACK_SKILL:
        stack_block = f"\n\nRead and follow the Stack Skill below for project structure, dependencies, motion components, and handoff files.\n\n{_STACK_SKILL.strip()}\n"
    else:
        stack_block = "\nNext.js 14 + React 18 + TypeScript + Tailwind CSS v3 + GSAP + Lenis. Follow the project structure in the Stack Skill.\n"

    # Business intelligence skill
    if _DIET_ON:
        # Diet also wires the image-sourcing rules in here (no separate
        # placeholder exists, and BI is the conversion-related block).
        # The image rules explicitly PERMIT real Unsplash/Pexels URLs —
        # Pebble's prior prompt accidentally forbade them by saying "no
        # external URLs", which is why Qwen kept emitting broken
        # /images/about/owner.jpg placeholders.
        from pebble.prompt_diet import IMAGE_RULES_DIET
        bi_block = BUSINESS_INTEL_DIET + "\n" + IMAGE_RULES_DIET
    elif _BI_SKILL:
        bi_block = f"\n\n{_BI_SKILL.strip()}\n"
    else:
        bi_block = "\n*(Business intelligence skill not loaded -- apply general conversion best practices.)*\n"

    # Diet ON → skip the giant ds_text block entirely. Style DNA + Industry
    # Intel are authoritative; the ui-ux-pro-max output added ~2.7K tokens of
    # contradictory Satoshi/General Sans guidance that the engine then had
    # to override-notice-its-way-around. Replace with a one-line pointer.
    if _DIET_ON:
        ds_block = DESIGN_SYSTEM_DIET
    elif ds_text:
        # The ui-ux-pro-max engine is deterministic: same query -> same Satoshi/
        # General Sans/glassmorphism/blue+orange output every time. That competes
        # with the Design DNA, which is the authoritative visual source for THIS
        # build. The block below explicitly demotes the style guide to a reference
        # so the LLM doesn't pull Satoshi when the DNA says Cormorant Garamond.
        if design_dna:
            dna_label = design_dna.get("label", "the chosen DNA")
            dna_display = design_dna.get("display_font", "")
            dna_body = design_dna.get("body_font", "")
            ds_override_notice = (
                f"\n> **OVERRIDE NOTICE — the style guide below is REFERENCE ONLY.**  \n"
                f"> The Design DNA at the top of this prompt (**{dna_label}**) is the "
                f"authoritative source for fonts, colors, motion, and layout. The style "
                f"guide below was generated by a deterministic helper that returns the "
                f"same output for every {industry or 'industry'} build — that's why "
                f"recent builds converged on Satoshi/General Sans/glassmorphism. "
                f"For THIS build, use **{dna_display}** for headings and **{dna_body}** "
                f"for body, NOT what the style guide names. Use the style guide only for "
                f"the *Pre-Delivery Checklist* and the *Avoid (Anti-patterns)* list — "
                f"the rest is overridden by the DNA.\n\n"
            )
        else:
            ds_override_notice = (
                "\nThe ui-ux-pro-max engine generated this recommendation. "
                "Use it as supporting detail — it enriches the Resolved Design Contract above. "
                "If any value here contradicts the Contract, the Contract wins.\n\n"
            )
        ds_block = ds_override_notice + f"```\n{ds_text.strip()}\n```\n"
    else:
        # Derive a concrete direction from the quiz answers so the LLM has real guidance
        industry_lower = industry.lower()
        is_dark = any(w in industry_lower for w in [
            "luxury", "premium", "yacht", "jewelry", "tech", "saas", "software",
            "agency", "studio", "bar", "nightclub", "photography",
        ])
        is_warm_light = any(w in industry_lower for w in [
            "yoga", "wellness", "dentist", "therapist", "bakery", "cafe", "spa",
        ])
        if is_dark:
            color_dir = (
                "dominant #0A0A0A, secondary #1A1A1A, accent a precise single color "
                "(gold #C8A96E, electric blue #3B82F6, or brand-specific), text #F9FAFB"
            )
            bg_dir = "dark background"
        elif is_warm_light:
            color_dir = (
                "dominant warm white #F5EFE6 or pale sage, secondary #FFFFFF, "
                "accent soft earth tone (dusty rose #D4899A, warm amber #D97706, muted teal #5EAAA8), "
                "text dark charcoal #1A1A1A"
            )
            bg_dir = "warm light background"
        else:
            # Home services, professional services, real estate, food, retail — default light
            color_dir = (
                "dominant #FFFFFF, secondary #F9FAFB, "
                "accent one clean color (trust blue #2563EB, reliability green #059669, or urgency amber #D97706), "
                "text #111827"
            )
            bg_dir = "clean light background"

        ds_block = (
            f"\n**Design system engine unavailable. Apply this direction derived from the brief:**\n\n"
            f"- **Background:** {bg_dir} — confirmed by the Business Intelligence skill for this industry\n"
            f"- **Colors:** {color_dir}\n"
            f"- **Heading font:** choose a DISTINCTIVE face from the No-Slop acceptable list "
            f"(Oswald, Syne, Fraunces, Playfair Display, Instrument Serif, Manrope, Bebas Neue) "
            f"— match to emotional direction. NOT Inter, Roboto, Poppins, or any convergence font.\n"
            f"- **Body font:** Inter (body only, never headings)\n"
            f"- **Load both fonts in layout.tsx** via next/font/google and pass both variables to <html>\n"
            f"- **Override anything generic** — the goal is a site that looks hand-designed, not generated\n"
        )

    if notes:
        lines = ["\nAnti-slop warnings fired. Resolve in favor of the audit:\n"]
        for severity, note in notes:
            lines.append(f"- **[{severity}]** {note}")
        anti_slop_block = "\n".join(lines)
    else:
        anti_slop_block = "\n*(No conflicts detected. Design rules below still apply.)*"

    # Industry research block
    if research_text:
        research_block = (
            f"\n**Gemini researched the {industry} industry and found:**\n\n"
            f"{research_text.strip()}\n\n"
            "Apply these data-driven insights to every design decision. "
            "This research is based on analysis of top-performing websites in this industry. "
            "When research conflicts with user choices, explain the conflict and recommend the research-backed approach."
        )
    else:
        research_block = "\n*(Industry research unavailable -- rely on Business Intelligence skill defaults above.)*\n"

    # Hero uses a CSS gradient mesh — no external image sourcing needed.
    # Imagen 4 (PEBBLE_USE_IMAGEN=true) generates images at the Stack-Skill
    # paths (subfolders + hyphens) so LLM <Image> tags resolve correctly.
    images_block = (
        "\n*(Hero imagery uses a CSS gradient mesh — no external photo URLs needed. "
        "If PEBBLE_USE_IMAGEN=true, Imagen 4 will generate images at the Stack-Skill paths "
        "(`/images/hero/hero.jpg`, `/images/services/service-1.jpg`, `/images/about/team-1.jpg`, "
        "`/images/gallery/01.jpg`, etc.) after build. Use `next/image` with these exact paths "
        "only when PEBBLE_USE_IMAGEN is active; otherwise skip image elements or use CSS "
        "backgrounds in the hero.)*\n"
    )

    # Real contact info, or visible placeholders when blank
    phone   = (answers.get("phone")   or "[BUSINESS PHONE]").strip() or "[BUSINESS PHONE]"
    email   = (answers.get("email")   or "[EMAIL]").strip()         or "[EMAIL]"
    address = (answers.get("address") or "[ADDRESS]").strip()       or "[ADDRESS]"
    services_offered = (answers.get("services_offered") or "*(infer from industry — list the standard services for this business type)*").strip()

    audience = (answers.get("audience") or "").strip() or "*(Not specified — infer from the industry's typical customer profile.)*"

    rendered = PROMPT_TEMPLATE.format(
        business_name=answers.get("business_name", ""),
        business_type=industry,
        audience=audience,
        location=answers.get("location", ""),
        services_offered=services_offered,
        phone=phone,
        email=email,
        address=address,
        visitor_action=visitor_action,
        booking_system=booking_str,
        industry_intel_block=industry_intel_block,
        pages_block=pages_block,
        resolved_contract=resolved_contract,
        reference_block=reference_block,
        design_reference_block=design_reference_block,
        extra_context=extra_block,
        url_extraction_block=url_extraction_block,
        intent_block=intent_block,
        no_slop_block=no_slop_block,
        ios_skill_block=ios_skill_block,
        stack_block=stack_block,
        business_intelligence_block=bi_block,
        industry_research_block=research_block,
        design_system_block=ds_block,
        images_block=images_block,
        anti_slop_block=anti_slop_block,
    )

    # Language block — non-empty only when the build's target language is
    # non-English. Sits with override priority near the top so the LLM's
    # boilerplate (aria labels, placeholder strings, meta descriptions)
    # gets written in the target language instead of drifting to English.
    try:
        from pebble.language import language_block as _language_block
        lang_prefix = _language_block(language or answers.get("_language") or "en")
    except Exception as e:
        log.warning("language block render failed: %s", e)
        lang_prefix = ""

    # Build the prompt prefix in priority order (highest priority first):
    #   1. creative_direction block — user's own words, absolute top priority
    #   2. Layout DNA block — structural architecture (hero type, nav, section flow)
    #   3. Style DNA block  — visual surface (colors, fonts, motion)
    #   4. Language prefix  — non-English locale override
    # The LLM reads top-down; instructions at line 1 beat buried ones.
    prefix = ""

    creative_direction = (answers.get("creative_direction") or "").strip()
    if creative_direction:
        prefix += (
            "# ============================================================\n"
            "# USER'S OWN WORDS — read first, let this shape every decision\n"
            "# ============================================================\n\n"
            "The business owner wrote this directly. Treat it as the single\n"
            "highest-priority input. If it conflicts with the Layout DNA or\n"
            "Style DNA below, the user's own words win. If they ask for\n"
            "something specific (a certain feel, a particular section, a\n"
            "layout they liked), honor it precisely.\n\n"
            f"> {creative_direction}\n\n"
            "# ============================================================\n"
            "# (end User Direction — Layout DNA follows)\n"
            "# ============================================================\n\n"
        )

    # Seed-brief reference block — hand-curated industry anchor.
    # Picked by the same industry_key used for industries.json lookup
    # (set into the brief as `_industry_intel_key` by the build pipeline).
    # Silent no-op when no seed exists for this industry.
    if _SEED_BRIEFS_OK and get_seed_brief and build_seed_brief_block:
        seed_key = (
            answers.get("_industry_intel_key")
            or answers.get("_industry_key")  # legacy alt
            or ""
        )
        seed = get_seed_brief(seed_key) if seed_key else None
        if seed:
            try:
                prefix += build_seed_brief_block(seed, industry_key=seed_key)
            except Exception as e:
                log.warning("Seed brief block render failed: %s", e)

    if _LAYOUT_DNA_OK and build_layout_block:
        layout_dna_card = answers.get("_layout_dna")
        if layout_dna_card and isinstance(layout_dna_card, dict):
            try:
                prefix += build_layout_block(layout_dna_card)
            except Exception as e:
                log.warning("Layout DNA block render failed: %s", e)

    if design_dna and build_dna_block:
        try:
            prefix += build_dna_block(design_dna)
        except Exception as e:
            log.warning("Style DNA block render failed: %s", e)

    # Phase 15d: when diet is on, strip the verbatim Code Pattern code
    # blocks from `rendered`. They suffocate Qwen with copy-paste templates
    # that contradict Layout DNA for 9/10 layouts. ~5K tokens cut.
    if _DIET_ON:
        from pebble.prompt_diet import strip_verbatim_code_patterns
        rendered = strip_verbatim_code_patterns(rendered)

    return prefix + lang_prefix + rendered


# --------------------------------------------------------------------------
# LLM CLIENT — extracted to pebble/llm.py (re-exported here for back-compat).
# --------------------------------------------------------------------------

from pebble.llm import (
    LLMError,
    GeminiClient,
    AnthropicClient,
    get_llm_client,
    _GEMINI_DEFAULT_MODEL,
    _ANTHROPIC_DEFAULT_MODEL,
)


# --------------------------------------------------------------------------
# FILE OUTPUT PARSER
# --------------------------------------------------------------------------

FILE_OPEN_RE = re.compile(r'<pebble-file\s+path="([^"]+)">\s*\n')
# Strip a trailing close tag — match canonical </pebble-file> AND common LLM
# typos like </peble-file>, </pebblefile>, </pebble file>. Greedy on the inner
# token because we only ever invoke this on the LAST line of a block.
_TRAILING_CLOSE_RE = re.compile(r'\n?\s*</p[a-z]*[\s-]?file>\s*$')

# Self-closing delete tag used by the repair loop. The LLM emits these to
# request file deletion — needed to repair structural failures like
# no_src_directory (files exist in the wrong place) that <pebble-file> alone
# can't address. Accepts both `<pebble-delete path="..."/>` and the slightly
# more permissive `<pebble-delete path="..."></pebble-delete>` forms.
_DELETE_TAG_RE = re.compile(
    r'<pebble-delete\s+path="([^"]+)"\s*(?:/>|></pebble-delete>)'
)

# Boundary detector for parse_files: a <pebble-file> block ends at the next
# <pebble-file> opening OR the next <pebble-delete> tag — both signal that
# the file body has ended.
_FILE_BOUNDARY_RE = re.compile(r'<pebble-(?:file\s+path|delete\s+path)="')


_PEBBLE_FILE_CLOSE_RE = re.compile(r'</p[a-z]*[\s-]?file>')


def detect_truncation(llm_output: str) -> int:
    """Return the count of unmatched `<pebble-file>` opening tags — i.e.
    how many files appear to have been cut off mid-stream by the LLM.

    Zero = the response is structurally balanced.
    Positive = the LLM ran out of output budget mid-write. The build
    has at least N incomplete file(s); the engine should mark the
    result `billable: false` so the user isn't charged for a broken
    site.

    Background: ``parse_files`` keys boundaries off the NEXT opening
    tag rather than requiring a close, so a truncated response with
    N opens / N-1 closes still parses N files — the last with a body
    cut mid-string. This function is the truncation guard the parser
    intentionally lacks. Counted with the same close-tag-typo regex
    the parser uses so Gemini's `</peble-file>` / `</pebblefile>`
    typos don't flag false positives.
    """
    opens = len(FILE_OPEN_RE.findall(llm_output))
    closes = len(_PEBBLE_FILE_CLOSE_RE.findall(llm_output))
    return max(0, opens - closes)


def parse_files(llm_output: str) -> list[tuple[str, str]]:
    """Extract ``<pebble-file path="...">`` blocks from an LLM response.

    Boundary strategy: each block runs from its opening tag until the NEXT
    ``<pebble-file>`` OR ``<pebble-delete>`` tag (or end of input). The
    canonical ``</pebble-file>`` closing tag is stripped off the tail if
    present, but the parser does not REQUIRE it — Gemini has been observed
    to typo the close as ``</peble-file>`` and a strict paired regex would
    silently swallow the next file's body.

    Embedded ``<pebble-delete>`` tags are not addressed by parse_files —
    they're between blocks now thanks to the boundary detector, but a safety
    net strips any that snuck inside.
    """
    out: list[tuple[str, str]] = []
    matches = list(FILE_OPEN_RE.finditer(llm_output))
    for i, m in enumerate(matches):
        path = m.group(1)
        body_start = m.end()
        # Find the next boundary AFTER body_start: another <pebble-file> open
        # OR a <pebble-delete>. Whichever comes first wins.
        next_boundary = _FILE_BOUNDARY_RE.search(llm_output, body_start)
        body_end = next_boundary.start() if next_boundary else len(llm_output)
        body = llm_output[body_start:body_end]
        body = _TRAILING_CLOSE_RE.sub("", body)
        body = _DELETE_TAG_RE.sub("", body)  # defense in depth
        out.append((path, body))
    return out


def parse_deletions(llm_output: str) -> list[str]:
    """Extract ``<pebble-delete path="..."/>`` tags from an LLM response.

    Returns the paths the LLM is requesting to delete. Caller is responsible
    for validating each path against the build's site root (path traversal,
    etc.) — see :func:`pebble.repair._apply_deletions`.
    """
    return [m.group(1) for m in _DELETE_TAG_RE.finditer(llm_output)]


FILE_FORMAT_INSTRUCTION = """

---

## OUTPUT FORMAT -- START BUILDING NOW

Do not write a plan. Do not ask questions. Your entire response must be working project files starting immediately with the first `<pebble-file>` tag.

Return every file the project needs using this exact format:

<pebble-file path="package.json">
[complete file contents]
</pebble-file>

<pebble-file path="app/layout.tsx">
[complete file contents]
</pebble-file>

Strict rules:
- One <pebble-file> block per file. The `path` is the relative path from the project root.
- Nothing outside the <pebble-file> blocks. No commentary. No plan. The first character of your response MUST be `<`.
- Output EVERY file the project needs: package.json, all config files, app/globals.css, app/layout.tsx, app/page.tsx, all additional pages, all components referenced in code.
- Include README.md with the media drop-in guide from the Stack Skill.
- Include a `.gitignore` at the project root with at minimum:
  ```
  node_modules/
  .next/
  .env*.local
  .DS_Store
  *.log
  ```
- Create placeholder `.gitkeep` files in every media folder so the directory structure exists on disk when the client clones the project:
  - `public/images/hero/.gitkeep`
  - `public/images/about/.gitkeep`
  - `public/images/services/.gitkeep`
  - `public/images/gallery/.gitkeep`
  - `public/images/logos/.gitkeep`
  - `public/images/og/.gitkeep`
  - `public/videos/.gitkeep`
  - `public/fonts/.gitkeep`
- All files must be complete. No TODOs. No stubs.
- Follow the Stack Skill's media path conventions exactly -- `/images/hero/hero.jpg`, `/images/about/owner.jpg`, etc.
- Testimonials: only include real ones. If none provided, omit the section. Never write fake reviews.
- Missing contact info: use `[BUSINESS PHONE]`, `[EMAIL]`, `[ADDRESS]` -- do not invent.
"""


LITE_FILE_FORMAT_INSTRUCTION = r"""

---

## OUTPUT FORMAT — SINGLE HTML FILE, BUILD NOW

Do not write a plan. Do not ask questions. Your entire response must be one working file starting immediately with the first `<pebble-file>` tag.

Return ONE complete, self-contained `index.html`. No framework. No build step. No npm. No separate files.

**CDN libraries — include in `<head>` in this exact order:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,300&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/lenis@1.1.14/dist/lenis.min.js"></script>
```

**SplitText replacement (Club GSAP not available via CDN — use this instead):**
```js
function splitWords(el) {
  const words = el.textContent.trim().split(/\s+/);
  el.innerHTML = words
    .map(w => `<span class="sw" style="display:inline-block;overflow:hidden"><span class="swi" style="display:inline-block">${w}</span></span>`)
    .join(' ');
  return el.querySelectorAll('.swi');
}
```
Use `splitWords(el)` wherever the full brief specifies `SplitText`. Animate `.swi` elements with GSAP exactly as you would split words.

**Strict rules:**
- One `<pebble-file path="index.html">` block. Nothing else.
- All CSS in `<style>` in `<head>`. All JS in `<script>` before `</body>`.
- Hero uses a CSS gradient mesh background — no external image URLs needed unless PEBBLE_USE_IMAGEN is active.
- Every section from the brief's homepage structure must be present and complete.
- Complete. No TODOs. No stubs. No placeholder comments like `// add animation here`.
- Hero must have a large `<h1>` visible on load — never a blank hero.
- All phone CTAs: `href="tel:..."`. All form inputs: `font-size: 16px` minimum.
- `gsap.registerPlugin(ScrollTrigger)` at the top of your script block.
- Lenis init: `const lenis = new Lenis(); lenis.on('scroll', ScrollTrigger.update); gsap.ticker.add(t => lenis.raf(t * 1000)); gsap.ticker.lagSmoothing(0);`

<pebble-file path="index.html">
[complete self-contained HTML]
</pebble-file>
"""


# --------------------------------------------------------------------------
# HTTP SERVER
# --------------------------------------------------------------------------

class PebbleHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    # ---- CORS helpers ----
    def _allowed_origins(self) -> list[str]:
        """Parse ``PEBBLE_ALLOWED_ORIGINS`` (comma-separated list).
        Empty/unset = "no allowlist configured", and the engine falls
        back to ``*`` for backwards-compat with dev flows that hit it
        from arbitrary localhost ports."""
        raw = os.environ.get("PEBBLE_ALLOWED_ORIGINS", "") or ""
        return [s.strip() for s in raw.split(",") if s.strip()]

    def _cors_decision(self) -> tuple[Optional[str], bool]:
        """Resolve the right ``Access-Control-Allow-Origin`` value for
        the incoming request, and whether ``Allow-Credentials: true`` is
        spec-valid to emit alongside it.

        - Allowlist set + request Origin matches: echo that origin and
          allow credentials. (Caches need ``Vary: Origin`` too.)
        - Allowlist set + Origin doesn't match: return ``(None, False)``
          so the caller emits no CORS headers — the browser blocks the
          response, which is exactly what we want for off-list origins.
        - Allowlist unset (default): wildcard, no credentials. Drops the
          ``* + Allow-Credentials`` footgun the 2026-05-16 NLM pass
          flagged: today it's silently ignored by browsers, but if
          anyone refactors ``*`` into origin reflection the credentialed
          CORS would light up for every origin.
        """
        allow = self._allowed_origins()
        try:
            request_origin = self.headers.get("Origin")
        except Exception:
            request_origin = None
        if allow:
            if request_origin and request_origin in allow:
                return request_origin, True
            return None, False
        return "*", False

    def _write_cors_headers(self) -> None:
        """Emit Access-Control-* headers consistent with ``_cors_decision``.
        Safe to call from any handler that has already called
        ``send_response`` but not yet ``end_headers``."""
        origin, allow_credentials = self._cors_decision()
        if origin is None:
            return
        self.send_header("Access-Control-Allow-Origin", origin)
        if origin != "*":
            self.send_header("Vary", "Origin")
        if allow_credentials:
            self.send_header("Access-Control-Allow-Credentials", "true")

    # ---- OPTIONS (CORS preflight) ----
    def do_OPTIONS(self):
        # Body extracted to pebble/server/router.py. Lazy import keeps
        # engine startup fast (router only loads on first request).
        from pebble.server.router import route_options
        route_options(self)

    # ---- GET ----
    def do_GET(self):
        from pebble.server.router import route_get
        route_get(self)

    # ---- POST ----
    def do_POST(self):
        from pebble.server.router import route_post
        route_post(self)

    # ---- DELETE ----
    def do_DELETE(self):
        from pebble.server.router import route_delete
        route_delete(self)

    # ---- PATCH ----
    def do_PATCH(self):
        from pebble.server.router import route_patch
        route_patch(self)

    def _handle_500(self, exc: BaseException) -> None:
        """Common 500 path. Logs the full traceback under a short
        correlation id and returns a generic JSON body so the client
        never receives ``str(exc)`` (which can embed paths, env keys,
        or library traceback fragments). Operators grep engine.log for
        ``error_id=...`` to find the original failure."""
        import secrets
        error_id = secrets.token_hex(4)  # 8 hex chars
        try:
            log.exception("handler raised on %s %s (error_id=%s): %r",
                          self.command, self.path, error_id, exc)
        except Exception:
            pass
        try:
            self._json(500, {"error": "Internal server error", "error_id": error_id})
        except Exception:
            pass

    def _handle_health(self):
        client, reason = get_llm_client()
        provider = getattr(client, "provider", None) if client else None
        model = getattr(client, "model", None) if client else None
        self._json(200, {
            "engine_ok": _ENGINE_OK,
            "google_installed": _GOOGLE_OK,
            "anthropic_installed": _ANTHROPIC_OK,
            "google_key_set": bool(
                os.environ.get("GOOGLE_API_KEY", "").strip() or
                os.environ.get("GEMINI_API_KEY", "").strip()
            ),
            "anthropic_key_set": bool(os.environ.get("ANTHROPIC_API_KEY", "").strip()),
            "llm_ready": reason == "ok",
            "llm_reason": reason,
            "provider": provider,
            "model": model,
        })

    def _handle_list_industries(self):
        """Expose the curated industries.json as a flat list for UI autocomplete.

        Returns key + display name + category-ish hint derived from
        visual_style/emotion so the typeahead can show a subtitle.
        """
        try:
            raw = json.loads(INDUSTRIES_JSON.read_text(encoding="utf-8")) if INDUSTRIES_JSON.exists() else {}
        except Exception:
            raw = {}
        items = []
        for key, entry in raw.items():
            if not isinstance(entry, dict):
                continue
            label = key.replace("_", " ")
            # Derive a short category line — prefer visual_style words, fall back to emotion
            hint = (entry.get("visual_style") or entry.get("emotion") or "").strip()
            if hint:
                hint = hint.split(",")[0].strip()
            items.append({
                "key": key,
                "label": label,
                "hint": hint,
                "hero_type": entry.get("hero_type", ""),
            })
        items.sort(key=lambda x: x["label"])
        self._json(200, {"industries": items, "count": len(items)})

    def _handle_list_briefs(self):
        briefs = []
        if OUTPUT_DIR.exists():
            for d in sorted(OUTPUT_DIR.iterdir()):
                bp = d / "brief.json"
                if not bp.exists():
                    continue
                try:
                    b = json.loads(bp.read_text(encoding="utf-8"))
                    briefs.append({
                        "slug": d.name,
                        "business_name": b.get("business_name", "?"),
                        "industry": b.get("industry", ""),
                        "aesthetic_direction": b.get("visual_aesthetic", b.get("emotional_direction", "")),
                        "created_at": b.get("_created_at", ""),
                        "has_site": (d / "site").exists(),
                    })
                except Exception:
                    pass
        briefs.sort(key=lambda b: b["created_at"], reverse=True)
        self._json(200, {"briefs": briefs})

    def _handle_get_brief(self, slug: str):
        slug = _slugify(slug)
        d = OUTPUT_DIR / slug
        if not d.exists() or not (d / "brief.json").exists():
            self._json(404, {"error": "brief not found"}); return
        brief = json.loads((d / "brief.json").read_text(encoding="utf-8"))
        prompt = (d / "PROMPT.md").read_text(encoding="utf-8") if (d / "PROMPT.md").exists() else ""
        files = []
        site_dir = d / "site"
        if site_dir.exists():
            for f in sorted(site_dir.rglob("*")):
                if f.is_file():
                    files.append(str(f.relative_to(site_dir)))
        self._json(200, {
            "brief": brief, "prompt": prompt,
            "files": files, "has_site": site_dir.exists(),
            "slug": slug,
        })

    def _handle_setup(self):
        """Save API key + provider to .env, reload env, return new health state."""
        length = int(self.headers.get("Content-Length", "0"))
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            self._json(400, {"error": "invalid json"}); return

        provider = data.get("provider", "gemini").strip().lower()
        api_key  = data.get("api_key", "").strip()

        if not api_key:
            self._json(400, {"error": "API key cannot be empty"}); return

        if provider == "gemini":
            key_name = "GOOGLE_API_KEY"
        elif provider == "anthropic":
            key_name = "ANTHROPIC_API_KEY"
        else:
            self._json(400, {"error": f"unknown provider: {provider}"}); return

        # Read existing .env, remove old entries for this key + provider
        env_path = PROJECT_ROOT / ".env"
        lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
        lines = [l for l in lines
                 if not l.startswith(f"{key_name}=") and not l.startswith("PEBBLE_PROVIDER=")]
        lines.append(f"PEBBLE_PROVIDER={provider}")
        lines.append(f"{key_name}={api_key}")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        # Reload into current process
        os.environ[key_name]       = api_key
        os.environ["PEBBLE_PROVIDER"] = provider

        # Return new health state
        client, reason = get_llm_client()
        self._json(200, {
            "ok": reason == "ok",
            "reason": reason,
            "provider": getattr(client, "provider", None),
            "model": getattr(client, "model", None),
        })

    def _handle_engine_root(self):
        """GET / and /index.html — backend liveness landing.

        The engine is API-only; the customer-facing app is the v3 Next.js
        frontend at http://localhost:3000 (proxies /api/* and /preview/*
        to this engine). Hitting / in a browser used to render a fancy
        dark landing page; that surface was unused and has been removed.
        """
        body = b"Pebble Engine - backend only. App runs at http://localhost:3000.\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_preview(self):
        rest = self.path[len("/preview/"):]
        if not rest:
            self.send_response(404); self.end_headers(); return
        parts = rest.split("/", 1)
        slug = _slugify(parts[0])
        rel = parts[1] if len(parts) > 1 and parts[1] else "index.html"
        if ".." in rel.split("/"):
            self.send_response(403); self.end_headers(); return

        # Phase 44 — flag set by the router when this request came in via
        # ``<slug>.pebbleapp.ai`` instead of the workspace iframe. Public
        # visitors must NOT see the visual-edit bridge (it leaks workspace
        # internals + spawns hover outlines on the live site) and SHOULD
        # get cache headers because the bytes are stable between edits.
        public_mode = bool(getattr(self, "_public_subdomain_mode", False))

        # Block preview if the project owner's subscription has lapsed.
        # Unclaimed projects and free-tier users (no subscription.json) pass
        # through. Only fired when a sentinel file is present with a
        # non-active/trialing status — fail-open on any read error.
        if self._subscription_lapsed(slug):
            self._serve_subscription_lapse_page()
            return

        # 2026-05-23 — Fly.io backend (env-gated, falls back to local).
        # When PEBBLE_PREVIEW_BACKEND=fly, route /preview/<slug>/... to
        # https://pebble-preview-<slug>.fly.dev/. Public_mode skips this
        # because public subdomain visitors should always see the published
        # site (Cloudflare Pages), never a workspace dev preview.
        #
        # No app-exists pre-check — that would add a 1-3s flyctl roundtrip
        # per request. Instead, try the proxy with a generous timeout (Fly
        # cold-wake takes ~50s). If the app doesn't exist, _proxy_to_dev
        # returns False (DNS fail or connection refused) and we fall through
        # to local dev_registry / static-file handling. This keeps the env
        # toggle SAFE — flipping to "fly" never breaks projects that haven't
        # been deployed to Fly yet.
        preview_backend = os.environ.get("PEBBLE_PREVIEW_BACKEND", "local").strip().lower()
        if preview_backend == "fly" and not public_mode:
            try:
                from pebble.fly_preview import preview_url as _fly_preview_url
                fly_url = _fly_preview_url(slug)
                slug_prefix = "/preview/" + parts[0]
                forward_path = self.path[len(slug_prefix):] or "/"
                # 20s timeout, NOT 90s. Originally tried 90s to cover cold
                # wakes, but that made EVERY request wait 90s before falling
                # back to local — terrible UX. With 20s we get:
                #   - Warm Fly (2-7s typical) → proxy succeeds quickly
                #   - Cold Fly (50-90s) → timeout at 20s, fall back to local
                #     immediately. The keep-alive ping in the workspace hits
                #     Fly DIRECTLY (cross-origin) to wake it without blocking
                #     user-facing requests on the wake-up window.
                if self._proxy_to_dev(fly_url, forward_path, remote_timeout=20):
                    return
                # Proxy failed — fall through to local path so we don't break
                # workspaces for projects that haven't been Fly-provisioned.
                log.info("[fly] proxy returned False for %s, falling back to local", slug)
            except Exception as exc:
                log.info("[fly] proxy errored for %s, falling back to local: %s", slug, exc)

        # If a live `next dev` process is registered for this slug, proxy to
        # it so SSR routes work (Next.js apps have no compiled index.html on
        # disk — static-file serving would 404). Falls through to static
        # files when no dev server is alive (engine restart, old build, etc.).
        try:
            from pebble.server.dev_registry import get_url as _get_dev_url
            dev_url = _get_dev_url(slug)
            if dev_url:
                # Strip /preview/<raw-slug> so next dev sees the real route.
                slug_prefix = "/preview/" + parts[0]
                forward_path = self.path[len(slug_prefix):] or "/"
                if self._proxy_to_dev(dev_url, forward_path):
                    return
        except Exception:
            pass  # fall through to static files

        # On-demand warmup (2026-05-23): if no dev URL is registered AND this
        # is a Next.js project (has package.json), kick off `next dev` in a
        # background thread and return a self-refreshing splash so the user
        # doesn't see a broken-image 404 in the workspace iframe. The first
        # /preview hit after an engine restart triggers warmup; subsequent
        # /preview hits proxy normally once the splash auto-refreshes.
        # Skipped in public_mode — public visitors should see live content
        # or nothing, never a workspace-internal splash.
        if not public_mode:
            project_dir = OUTPUT_DIR / slug
            site_dir    = project_dir / "site"
            if (site_dir / "package.json").exists():
                try:
                    from pebble.server.preview_ondemand import (
                        render_splash_html,
                        start_or_get,
                    )
                    status = start_or_get(slug, site_dir)
                    if status == "ready":
                        # Race: registry just got populated while we were
                        # checking. Tell the iframe to retry — the next hit
                        # will land on the proxy path above.
                        self.send_response(503)
                        self.send_header("Retry-After", "1")
                        self.send_header("Content-Type", "text/plain; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(b"Preview just became ready - reload"); return
                    html = render_splash_html(slug, status).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(html)))
                    self.send_header("Cache-Control", "no-store")
                    self.end_headers()
                    self.wfile.write(html); return
                except Exception:
                    # Fall through to the original 404 path on any unexpected
                    # error so the engine never crashes the preview path.
                    pass

        site_file = OUTPUT_DIR / slug / "site" / rel
        if not site_file.exists() or not site_file.is_file():
            self.send_response(404); self.end_headers()
            self.wfile.write(f"Preview file not found: {rel}".encode()); return
        ext = site_file.suffix.lstrip(".").lower()
        ct_map = {
            "html": "text/html", "htm": "text/html",
            "css": "text/css", "js": "application/javascript",
            "json": "application/json", "svg": "image/svg+xml",
            "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif", "ico": "image/x-icon",
            "woff": "font/woff", "woff2": "font/woff2",
        }
        ct = ct_map.get(ext, "text/plain")
        if ct.startswith("text/") or ct in ("application/javascript", "application/json", "image/svg+xml"):
            ct += "; charset=utf-8"

        # Inject the visual-edit bridge into HTML responses ONLY when the
        # request comes from the engine itself (i.e. the workspace iframe).
        # The bridge highlights elements on hover and posts a "selected"
        # message back to the parent window for click-to-edit. Bridge is
        # safe to ship: it's pure DOM event listeners, no network.
        #
        # Phase 44 — when serving via a public subdomain (public_mode=True)
        # we skip the bridge entirely (visitors don't get a click-to-edit
        # overlay) AND swap the no-store cache header for a short public
        # cache so the CDN/browser can reuse responses across visitors.
        if ext in ("html", "htm"):
            try:
                from pebble.integrations import render_all_snippets as _render_integrations
                raw = site_file.read_text(encoding="utf-8")
                # Phase 56a — inject active integration widgets (WhatsApp, booking,
                # Google Maps, social rail, cookie-consent, custom code) into every
                # HTML response. Integrations are live for both workspace preview
                # (non-public) AND public subdomain visitors so the published site
                # includes them. The injection is idempotent (snippets use stable IDs).
                integration_html = _render_integrations(slug)
                if integration_html:
                    raw = self._inject_html(raw, integration_html)
                if public_mode:
                    data = raw.encode("utf-8")
                    cache_header = "public, max-age=60"
                else:
                    from pebble.server.visual_edit import PEBBLE_VISUAL_EDIT_BRIDGE
                    injected = self._inject_bridge(raw, PEBBLE_VISUAL_EDIT_BRIDGE)
                    data = injected.encode("utf-8")
                    cache_header = "no-store, no-cache, must-revalidate, max-age=0"
                self.send_response(200)
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", cache_header)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception:
                pass  # fall through to plain serve
        self._serve_file(site_file, ct)

    def _handle_preview_template(self):
        """Serve pre-built static template previews from pebble/templates/<id>/out/.

        Path shape: /preview-template/<template_id>/<rel-path>
        - Bare /preview-template/<id>/ resolves to out/index.html.
        - Directory paths resolve to <dir>/index.html (matches next.js
          trailingSlash: true output).
        - Files are served with content-type by extension (same map as
          _handle_preview).
        - Path-traversal attempts are rejected: the resolved file MUST stay
          inside out/.

        Built by `python -m pebble.templates.export <template_id>`. If out/
        doesn't exist (export never run, or template just added), returns 404
        with an operator-facing message.
        """
        rest = self.path[len("/preview-template/"):]
        if not rest:
            self.send_response(404); self.end_headers(); return
        template_id, _, rel = rest.partition("/")
        if not re.fullmatch(r"[a-z0-9_]{1,64}", template_id or ""):
            self._json(400, {"error": "invalid template_id"}); return

        try:
            from pebble.templates.export import template_dir
            tdir = template_dir(template_id)
        except (KeyError, FileNotFoundError):
            self._json(404, {"error": "template not found"}); return

        out_root = (tdir / "out").resolve()
        if not out_root.is_dir():
            self._json(404, {
                "error": "template not yet exported",
                "hint":  f"run: python -m pebble.templates.export {template_id}",
            }); return

        # Strip any leading slashes so `rel` is always relative. Without this,
        # a double-slash URL ("/preview-template/<id>//") gives rel="/" which
        # Path treats as ABSOLUTE — (out_root / "/").resolve() jumps to the
        # filesystem root and the traversal guard then 403's a legitimate
        # request. v3 sometimes concatenates preview_url (trailing /) with
        # active.path (leading /) and produces exactly that double-slash.
        rel = rel.lstrip("/") or "index.html"
        candidate = (out_root / rel).resolve()

        # Path-traversal guard — the resolved file MUST stay inside out_root.
        try:
            candidate.relative_to(out_root)
        except ValueError:
            self._json(403, {"error": "path outside template root"}); return

        if candidate.is_dir():
            candidate = candidate / "index.html"
        if not candidate.is_file():
            self.send_response(404); self.end_headers(); return

        ext = candidate.suffix.lstrip(".").lower()
        ct_map = {
            "html": "text/html", "htm": "text/html",
            "css": "text/css", "js": "application/javascript",
            "json": "application/json", "svg": "image/svg+xml",
            "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif", "ico": "image/x-icon", "webp": "image/webp",
            "woff": "font/woff", "woff2": "font/woff2",
            "txt": "text/plain", "xml": "application/xml",
        }
        ct = ct_map.get(ext, "application/octet-stream")
        if ct.startswith("text/") or ct in ("application/javascript", "application/json", "image/svg+xml", "application/xml"):
            ct += "; charset=utf-8"

        # HTML responses: rewrite root-relative href/src/action attributes
        # to be prefixed with the basePath. Next.js's `basePath` correctly
        # prefixes <Link> hrefs and _next/static asset URLs, but it does
        # NOT prefix raw <a href="/about">, <img src={SITE_HERO}>, or
        # <form action="/contact">. Without this rewrite, clicking a nav
        # link inside the iframe navigates to http://localhost:8000/about
        # (404) instead of http://localhost:8000/preview-template/<id>/about.
        # The regex only matches root-relative URLs (start with "/")
        # that don't already begin with the basePath — idempotent.
        if ext in ("html", "htm"):
            try:
                raw = candidate.read_text(encoding="utf-8")
                base = f"/preview-template/{template_id}"
                # Match href=, src=, action= where the value starts with "/"
                # but not "/preview-template/..." (already prefixed) and not
                # "//..." (protocol-relative) and not "/_next/..." (already
                # basePath'd by Next.js).
                rewritten = re.sub(
                    r'(href|src|action)="/(?!preview-template/|_next/|/)',
                    rf'\1="{base}/',
                    raw,
                )
                data = rewritten.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception as e:
                log.warning("[preview-template] HTML rewrite failed for %s: %s", template_id, e)
                # Fall through to plain serve below

        self._serve_file(candidate, ct)

    @staticmethod
    def _inject_html(html: str, snippet: str) -> str:
        """Insert *snippet* (raw HTML) just before </body>.
        If </body> is absent, append at the end."""
        lower = html.lower()
        idx = lower.rfind("</body>")
        if idx == -1:
            return html + snippet
        return html[:idx] + snippet + html[idx:]

    @staticmethod
    def _inject_bridge(html: str, script_body: str) -> str:
        """Insert the visual-edit bridge script just before </body>. If
        </body> is missing, append it at the end."""
        tag = f'<script id="pebble-bridge">{script_body}</script>'
        lower = html.lower()
        idx = lower.rfind("</body>")
        if idx == -1:
            return html + tag
        return html[:idx] + tag + html[idx:]

    def _proxy_to_dev(self, dev_url: str, forward_path: str, remote_timeout: int = 10) -> bool:
        """Forward GET *forward_path* to the running next dev server at *dev_url*.

        Injects the visual-edit bridge into HTML responses (workspace iframe
        path); skips injection when the caller set _public_subdomain_mode
        (Phase 44 — public subdomain visitors shouldn't see the editor
        overlay). Returns True on success. The caller must not write any
        HTTP response on False — the connection state is clean (no bytes
        sent).

        2026-05-23: added scheme detection so the same path can proxy to
        Fly.io's HTTPS preview machines (e.g. pebble-preview-<slug>.fly.dev).
        ``remote_timeout`` extends the default 10s for cold-wake scenarios —
        Fly hallpass can hold the connection up to ~60s while the machine
        boots + next dev compiles the first page.
        """
        import http.client
        from urllib.parse import urlsplit
        public_mode = bool(getattr(self, "_public_subdomain_mode", False))
        parsed = urlsplit(dev_url)
        conn: http.client.HTTPConnection | http.client.HTTPSConnection | None = None
        try:
            if parsed.scheme == "https":
                conn = http.client.HTTPSConnection(parsed.netloc, timeout=remote_timeout)
            else:
                conn = http.client.HTTPConnection(parsed.netloc, timeout=remote_timeout)
            conn.request("GET", forward_path)
            resp = conn.getresponse()
            data = resp.read()
            ct = resp.getheader("Content-Type", "application/octet-stream")
            if "text/html" in ct and not public_mode:
                try:
                    from pebble.server.visual_edit import PEBBLE_VISUAL_EDIT_BRIDGE
                    html = data.decode("utf-8", errors="replace")
                    data = self._inject_bridge(html, PEBBLE_VISUAL_EDIT_BRIDGE).encode("utf-8")
                    ct = "text/html; charset=utf-8"
                except Exception:
                    pass
            elif "text/html" in ct and public_mode:
                ct = "text/html; charset=utf-8"
            cache_header = (
                "public, max-age=60" if public_mode
                else "no-store, no-cache, must-revalidate, max-age=0"
            )
            self.send_response(resp.status)
            self.send_header("Content-Type", ct)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", cache_header)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
            return True
        except Exception as exc:
            log.warning("dev proxy %s → %s failed: %s", forward_path, dev_url, exc)
            return False
        finally:
            if conn:
                conn.close()

    def _subscription_lapsed(self, slug: str) -> bool:
        """Return True only when a project owner has a subscription sentinel
        file AND its status is neither active nor trialing.  Fail-open on
        any read error so unclaimed / free-tier sites are never blocked."""
        try:
            brief_file = OUTPUT_DIR / slug / "brief.json"
            if not brief_file.exists():
                return False
            brief = json.loads(brief_file.read_text(encoding="utf-8"))
            user_id = brief.get("_user_id")
            if not user_id:
                return False
            sub_file = OUTPUT_DIR / ".users" / user_id / "subscription.json"
            if not sub_file.exists():
                return False
            sub = json.loads(sub_file.read_text(encoding="utf-8"))
            status = sub.get("status") or ""
            return status not in ("active", "trialing")
        except Exception:
            return False

    def _serve_subscription_lapse_page(self) -> None:
        """Serve a simple HTML notice when a project's subscription has lapsed."""
        html = (
            "<!DOCTYPE html><html lang='en'><head>"
            "<meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>Site unavailable — Pebble</title>"
            "<style>"
            "body{font-family:system-ui,sans-serif;display:flex;align-items:center;"
            "justify-content:center;min-height:100vh;margin:0;background:#f8f8f7;}"
            ".card{background:#fff;border-radius:16px;padding:48px;max-width:480px;"
            "text-align:center;box-shadow:0 4px 24px rgba(0,0,0,.07);}"
            "h1{font-size:1.5rem;margin:0 0 12px;color:#1a1a1a;}"
            "p{color:#6b7280;line-height:1.6;margin:0 0 24px;}"
            "a{display:inline-block;background:#f59e0b;color:#fff;padding:10px 24px;"
            "border-radius:999px;text-decoration:none;font-weight:600;}"
            "</style></head><body>"
            "<div class='card'>"
            "<h1>This site is temporarily unavailable</h1>"
            "<p>The Pebble subscription for this site has lapsed. "
            "The site owner can reactivate it from their billing settings.</p>"
            "<a href='/settings'>Reactivate subscription</a>"
            "</div></body></html>"
        )
        data = html.encode("utf-8")
        self.send_response(402)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _handle_build(self, generate: bool):
        """Build pipeline route. Body lives in :mod:`pebble.server.build` so
        the handler class stays focused on dispatch."""
        from pebble.server.build import run_build
        run_build(self, generate)

    def _handle_plan(self):
        """Plan-preview route. Returns a Pebble Plan dict for the given
        brief WITHOUT running the LLM build. Body lives in
        :mod:`pebble.server.build`.
        """
        from pebble.server.build import run_plan
        run_plan(self)

    # --------- History / rollback / refine / visual-edit / projects ---------

    def _handle_list_projects(self):
        """GET /api/projects — list every project in output/ with summary
        metadata for the dashboard sidebar (Recents + Starred)."""
        from pebble.server.projects import run_list_projects
        run_list_projects(self)

    def _handle_usage_summary(self):
        """GET /api/usage — aggregate cost telemetry across every project."""
        from pebble.server.projects import run_usage_summary
        run_usage_summary(self)

    def _handle_activity_feed(self):
        """GET /api/activity — chronological feed of snapshots across all
        of the current user's projects (the dashboard "Recently changed"
        widget)."""
        from pebble.server.projects import run_activity_feed
        run_activity_feed(self)

    def _handle_delete_project(self, slug: str):
        """DELETE /api/projects/<slug> — hard delete."""
        from pebble.server.projects import run_delete_project
        run_delete_project(self, slug)

    def _handle_get_history(self, slug: str):
        """GET /api/projects/<slug>/history — list every snapshot for one
        project, newest first."""
        from pebble.server.projects import run_get_history
        run_get_history(self, slug)

    def _handle_rollback(self):
        """POST /api/rollback — restore a previous snapshot to site/.
        Body: ``{ slug, snapshot_id }``."""
        from pebble.server.projects import run_rollback
        run_rollback(self)

    def _handle_toggle_star(self, slug: str):
        """POST /api/projects/<slug>/star — toggle starred state."""
        from pebble.server.projects import run_toggle_star
        run_toggle_star(self, slug)

    def _handle_refine(self):
        """POST /api/refine — apply a targeted refinement to an existing
        build without re-running the full LLM generation. Body lives in
        :mod:`pebble.server.refine`."""
        from pebble.server.refine import run_refine
        run_refine(self)

    def _handle_visual_edit(self):
        """POST /api/visual-edit — deterministic in-place edit (text,
        color, font size) from a click on the preview iframe. Body lives
        in :mod:`pebble.server.visual_edit`."""
        from pebble.server.visual_edit import run_visual_edit
        run_visual_edit(self)

    def _handle_migrate(self):
        """POST /api/migrate — pull semantic facts from an existing
        public URL so users switching from another platform can
        pre-fill the intake without re-typing everything. Body lives
        in :mod:`pebble.server.migrate`."""
        from pebble.server.migrate import run_migrate
        run_migrate(self)

    def _handle_inspire(self):
        """POST /api/inspire — extract design DNA (palette, typography,
        vibe + suggested DNA card) from a user-pasted URL. Pre-seeds
        the questionnaire's style direction. Body lives in
        :mod:`pebble.server.inspire`."""
        from pebble.server.inspire import run_inspire
        run_inspire(self)

    def _handle_publish(self):
        """POST /api/publish — package a project for hosting (Cloudflare
        Pages live deploy if configured, else downloadable ZIP)."""
        from pebble.server.publish import run_publish
        run_publish(self)

    def _handle_get_publish_state(self, slug: str):
        """GET /api/projects/<slug>/publish — last publish + history."""
        from pebble.server.publish import run_get_publish_state
        run_get_publish_state(self, slug)

    def _handle_serve_dist(self):
        """GET /dist/<slug>/dist.zip — download the most recent zip."""
        # Path shape: /dist/<slug>/dist.zip
        parts = self.path.split("/")
        # ["", "dist", "<slug>", "dist.zip"]
        if len(parts) < 4 or parts[1] != "dist" or parts[3] != "dist.zip":
            self.send_response(404); self.end_headers(); return
        slug = parts[2]
        from pebble.server.publish import run_serve_dist
        run_serve_dist(self, slug)

    def _handle_get_domain(self, slug: str):
        """GET /api/projects/<slug>/domain — current domain + status."""
        from pebble.server.domain import run_get_domain
        run_get_domain(self, slug)

    def _handle_form_submit(self, slug: str):
        """POST /api/forms/<slug> — accept a form submission."""
        from pebble.server.forms import run_submit
        run_submit(self, slug)

    def _handle_inbox_get(self):
        """GET /api/projects/<slug>/inbox[/<id>] — inbox listing or one item."""
        rest = self.path[len("/api/projects/"):]
        # rest is "<slug>/inbox" or "<slug>/inbox/<id>"
        parts = rest.split("/")
        if len(parts) == 2 and parts[1] == "inbox":
            from pebble.server.forms import run_list_inbox
            run_list_inbox(self, parts[0])
        elif len(parts) == 3 and parts[1] == "inbox":
            from pebble.server.forms import run_get_inbox_item
            run_get_inbox_item(self, parts[0], parts[2])
        else:
            self.send_response(404); self.end_headers()

    def _handle_inbox_mark_read(self):
        """POST /api/projects/<slug>/inbox/<id>/read — toggle read flag."""
        rest = self.path[len("/api/projects/"):]
        parts = rest.split("/")
        # parts: ["<slug>", "inbox", "<id>", "read"]
        if len(parts) == 4 and parts[1] == "inbox" and parts[3] == "read":
            from pebble.server.forms import run_mark_read
            run_mark_read(self, parts[0], parts[2])
        else:
            self.send_response(404); self.end_headers()

    def _handle_inbox_delete(self):
        """DELETE /api/projects/<slug>/inbox/<id>."""
        rest = self.path[len("/api/projects/"):]
        parts = rest.split("/")
        if len(parts) == 3 and parts[1] == "inbox":
            from pebble.server.forms import run_delete_inbox_item
            run_delete_inbox_item(self, parts[0], parts[2])
        else:
            self.send_response(404); self.end_headers()

    def _handle_set_domain(self, slug: str):
        """POST /api/projects/<slug>/domain — attach a custom domain."""
        from pebble.server.domain import run_set_domain
        run_set_domain(self, slug)

    def _handle_delete_domain(self, slug: str):
        """DELETE /api/projects/<slug>/domain — detach the custom domain."""
        from pebble.server.domain import run_delete_domain
        run_delete_domain(self, slug)

    def _serve_file(self, path: Path, content_type: str):
        if not path.exists():
            self.send_response(404); self.end_headers()
            self.wfile.write(f"{path} not found".encode()); return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        # Aggressive no-store so the browser refetches every navigation/refresh —
        # prevents stale UI when we iterate on ui/index.html
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma",        "no-cache")
        self.send_header("Expires",       "0")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, status: int, payload: dict, extra_headers: list | None = None):
        """Write a JSON response. ``extra_headers`` is an optional list of
        ``(name, value)`` tuples — used by auth handlers to attach a
        Set-Cookie."""
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        # Resolve CORS based on PEBBLE_ALLOWED_ORIGINS — wildcard mode
        # drops the spec-invalid `* + Allow-Credentials: true` combo
        # the 2026-05-16 NLM pass flagged.
        self._write_cors_headers()
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        for name, value in (extra_headers or []):
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _banner():
    client, reason = get_llm_client()
    engine_status = "loaded" if _ENGINE_OK else "degraded (no design_system.py)"
    print()
    print("  " + "-" * 56)
    print(f"   Pebble Engine")
    print(f"   ui-ux-pro-max engine: {engine_status}")
    if reason == "ok":
        provider = getattr(client, "provider", "?")
        model    = getattr(client, "model", "?")
        print(f"   auto-build mode:      ready")
        print(f"   provider:             {provider}")
        print(f"   model:                {model}")
    else:
        print(f"   auto-build mode:      unavailable")
        print(f"     reason: {reason}")
    print("  " + "-" * 56)


def serve(port: int = 8000, open_browser: bool = True) -> None:
    _banner()
    # Bind to 0.0.0.0 on hosted platforms (Railway etc. set PORT); stay on
    # 127.0.0.1 locally so the engine isn't exposed on the local network.
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    url = f"http://localhost:{port}"
    print(f"   running at {url}\n")

    if open_browser:
        try: webbrowser.open(url)
        except Exception: pass

    try:
        import uvicorn
        # pebble.app is imported here (not at module level) so pebble_engine
        # is already in sys.modules when HandlerShim looks up PebbleHandler.
        from pebble.app import app as _fastapi_app
        uvicorn.run(_fastapi_app, host=host, port=port, log_level="warning")
    except ImportError:
        # uvicorn not installed — fall back to the stdlib ThreadingHTTPServer.
        # All functionality works; SSE streaming is unavailable.
        server = ThreadingHTTPServer((host, port), PebbleHandler)
        server.daemon_threads = True
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n  Stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pebble Engine -- visual website briefing.")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)))
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    serve(port=args.port, open_browser=not args.no_browser)
