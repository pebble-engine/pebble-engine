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

# --------------------------------------------------------------------------
# PATHS
# --------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.resolve()
UIUX_SCRIPTS = PROJECT_ROOT / "skills" / "ui-ux-pro-max" / "scripts"
INDEX_HTML = PROJECT_ROOT / "ui" / "index.html"
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
# --------------------------------------------------------------------------

CONVERGENCE_FONTS = {
    "inter", "roboto", "poppins", "geist", "plus jakarta sans",
    "space grotesk", "dm sans",
}
ACCEPTABLE_DISPLAY_PAIRS = {
    "fraunces", "playfair", "instrument serif", "tobias", "migra",
    "pp editorial", "söhne", "sohne", "national 2", "tiempos",
    "gt alpina", "boogy brut", "dm serif", "serif",
}
WATCH_STYLES = {"neumorphism", "claymorphism", "default cyberpunk"}


def audit_design_system(ds_text: str) -> list[tuple[str, str]]:
    notes: list[tuple[str, str]] = []
    text = ds_text.lower()
    heading = _extract_field(ds_text, r"heading[^:\n]*?:\s*([^\n]+)")
    body = _extract_field(ds_text, r"body[^:\n]*?:\s*([^\n]+)")
    has_distinctive = any(d in heading.lower() for d in ACCEPTABLE_DISPLAY_PAIRS)

    for font in CONVERGENCE_FONTS:
        if font in heading.lower():
            notes.append(("TYPOGRAPHY",
                f"Heading uses '{heading.strip()}' (contains '{font}'). "
                f"Swap heading face for Fraunces, Instrument Serif, "
                f"PP Editorial, Migra, or Tobias."))
        if font in body.lower() and not has_distinctive:
            notes.append(("TYPOGRAPHY",
                f"Body is '{body.strip()}' and heading lacks a distinctive "
                f"display face. Pair with serif or swap body to Söhne/Mona Sans."))

    if "purple" in text and ("gradient" in text or "to-blue" in text):
        notes.append(("COLOR",
            "Purple-to-blue gradient detected -- the most recognizable AI tell. "
            "Replace with a flat dominant color + sharp accent."))

    for style in WATCH_STYLES:
        if style in text:
            notes.append(("STYLE",
                f"'{style.title()}' in recommendation -- trends slop-adjacent. "
                "Override unless the direction explicitly calls for it."))

    if "hero + 3 features + cta" in text.replace("-", " "):
        notes.append(("LAYOUT",
            "Default 'Hero -> 3 cards -> CTA' pattern. Break it with asymmetric "
            "grids, full-bleed sections, or numbered lists."))

    return notes


def _extract_field(text: str, pattern: str) -> str:
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else ""


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
# IMAGE SOURCING SYSTEM
# Primary:  Pexels API (keyword-relevant, requires PEXELS_API_KEY in .env)
# Fallback: Picsum Photos (seed-based, no key needed, generic photos)
# --------------------------------------------------------------------------

# Maps industry keywords → (main scene query, people/team query)
_PEXELS_QUERIES: dict[str, tuple[str, str]] = {
    # Home services
    "plumbing":          ("plumber pipe repair bathroom",        "plumber technician worker"),
    "electrician":       ("electrical wiring installation",      "electrician worker professional"),
    "electrical":        ("electrical wiring installation",      "electrician worker professional"),
    "hvac":              ("air conditioning heating system",     "hvac technician professional"),
    "roofing":           ("roof shingles construction",          "roofer contractor worker"),
    "landscaping":       ("garden landscape lawn design",        "landscaper gardener worker"),
    "cleaning":          ("clean modern interior spotless",      "cleaning service professional"),
    "painting":          ("interior painting home",              "painter contractor worker"),
    "general contractor":("home renovation construction",        "contractor builder worker"),
    "construction":      ("construction building site",          "construction worker builder"),
    "moving":            ("moving boxes relocation truck",       "movers professional team"),
    "pest control":      ("clean pest free home interior",       "pest control technician"),
    "pool":              ("swimming pool luxury backyard",       "pool technician professional"),
    "fence":             ("fence installation backyard",         "fence contractor worker"),
    "flooring":          ("hardwood floor installation",         "flooring contractor worker"),
    # Health & wellness
    "yoga":              ("yoga studio peaceful zen",            "yoga instructor class"),
    "fitness":           ("gym equipment modern workout",        "personal trainer coaching"),
    "personal trainer":  ("fitness training gym",               "personal trainer athlete"),
    "wellness":          ("spa wellness relaxing retreat",       "wellness therapist professional"),
    "spa":               ("luxury spa interior serene",          "spa therapist massage"),
    "massage":           ("massage therapy room calm",           "massage therapist professional"),
    "chiropractic":      ("chiropractic clinic office",          "chiropractor patient treatment"),
    "physical therapy":  ("physical therapy rehabilitation",     "physical therapist patient"),
    # Medical & dental
    "dentist":           ("dental office clinic modern",         "dentist patient professional"),
    "dental":            ("dental office clinic modern",         "dentist professional"),
    "doctor":            ("medical clinic office modern",        "doctor patient professional"),
    "optometry":         ("eye care clinic optical",             "optometrist professional"),
    "veterinary":        ("veterinary clinic pet care",          "veterinarian pet owner"),
    "vet":               ("veterinary animal clinic",            "veterinarian professional"),
    # Mental health
    "therapist":         ("therapy office calm peaceful",        "therapist counselor professional"),
    "counseling":        ("counseling therapy office serene",    "counselor therapist"),
    "psychology":        ("psychology office calm neutral",      "psychologist professional"),
    # Beauty
    "hair salon":        ("hair salon interior modern",          "hairstylist client beauty"),
    "salon":             ("beauty salon interior modern",        "hairstylist beautician professional"),
    "barbershop":        ("barbershop interior classic",         "barber client professional"),
    "nail":              ("nail salon manicure art",             "nail technician client"),
    "makeup":            ("makeup artist studio beauty",         "makeup artist professional"),
    # Food & beverage
    "restaurant":        ("restaurant interior fine dining",     "chef server professional"),
    "cafe":              ("coffee shop cafe interior cozy",      "barista coffee professional"),
    "coffee":            ("coffee shop cafe cozy interior",      "barista professional"),
    "bakery":            ("bakery fresh bread pastry",           "baker pastry chef"),
    "bar":               ("cocktail bar lounge interior",        "bartender mixologist"),
    "catering":          ("catering food event elegant",         "catering chef professional"),
    # Professional services
    "law":               ("law office modern professional",      "lawyer attorney professional"),
    "attorney":          ("law firm office professional",        "attorney professional"),
    "accounting":        ("accounting office finance modern",    "accountant professional"),
    "financial":         ("financial planning office",           "financial advisor professional"),
    "insurance":         ("professional office business",        "insurance agent professional"),
    "real estate":       ("luxury modern home interior",         "real estate agent professional"),
    # Tech & creative
    "tech":              ("technology startup office modern",    "software developer team"),
    "software":          ("software development modern office",  "developer programmer team"),
    "saas":              ("modern tech office startup",          "software team professional"),
    "agency":            ("creative agency studio modern",       "design team professional"),
    "marketing":         ("marketing creative office",           "marketing team professional"),
    "web design":        ("design studio creative workspace",    "designer professional"),
    "photography":       ("photography studio camera equipment", "photographer professional"),
    # Events & lifestyle
    "wedding":           ("wedding ceremony elegant venue",      "wedding couple celebration"),
    "event":             ("event venue elegant setup",           "event planner professional"),
    # Education & childcare
    "childcare":         ("daycare children bright classroom",   "childcare teacher professional"),
    "education":         ("classroom school learning bright",    "teacher student professional"),
    "tutoring":          ("tutoring study desk learning",        "tutor student"),
    # Pet services
    "pet grooming":      ("pet grooming salon dog",              "pet groomer professional"),
    "dog training":      ("dog training obedience outdoor",      "dog trainer professional"),
    # Auto
    "auto repair":       ("auto repair shop garage clean",       "mechanic car professional"),
    "car wash":          ("car wash clean shiny auto",           "car wash professional"),
}


def _pexels_queries_for_industry(industry: str) -> tuple[str, str]:
    ind = industry.lower()
    for key, queries in _PEXELS_QUERIES.items():
        if key in ind:
            return queries
    safe = re.sub(r"[^a-z0-9 ]", " ", ind).strip()
    return (f"{safe} professional business", f"{safe} professional team")


def get_placeholder_images(industry: str, image_count: int = 8) -> dict[str, str]:
    """Picsum Photos fallback — seed-based, no API key, generic photos."""
    slug = _slugify(industry)
    return {
        "hero":      f"https://picsum.photos/seed/{slug}-hero/1600/900",
        "service_1": f"https://picsum.photos/seed/{slug}-svc1/800/600",
        "service_2": f"https://picsum.photos/seed/{slug}-svc2/800/600",
        "service_3": f"https://picsum.photos/seed/{slug}-svc3/800/600",
        "team_1":    f"https://picsum.photos/seed/{slug}-team1/600/600",
        "team_2":    f"https://picsum.photos/seed/{slug}-team2/600/600",
        "gallery_1": f"https://picsum.photos/seed/{slug}-gal1/800/600",
        "gallery_2": f"https://picsum.photos/seed/{slug}-gal2/800/600",
    }


def get_pexels_images(industry: str, api_key: str) -> dict[str, str]:
    """
    Fetch industry-relevant images from Pexels API.
    Makes 2 requests: one landscape query for scenes, one portrait for team.
    Falls back to Picsum per-slot on any individual failure.
    """
    fallback = get_placeholder_images(industry)
    main_q, people_q = _pexels_queries_for_industry(industry)

    def _fetch(query: str, orientation: str, count: int) -> list[str]:
        params = urllib.parse.urlencode({
            "query": query,
            "per_page": max(count + 5, 15),
            "orientation": orientation,
        })
        req = urllib.request.Request(
            f"https://api.pexels.com/v1/search?{params}",
            headers={"Authorization": api_key, "User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
        urls, seen = [], set()
        for photo in data.get("photos", []):
            pid = photo["id"]
            if pid in seen:
                continue
            seen.add(pid)
            src = photo["src"]
            urls.append(src.get("large2x") or src.get("large") or src["original"])
            if len(urls) >= count:
                break
        return urls

    images: dict[str, str] = {}

    try:
        scene = _fetch(main_q, "landscape", 6)
        keys = ["hero", "service_1", "service_2", "service_3", "gallery_1", "gallery_2"]
        for i, key in enumerate(keys):
            images[key] = scene[i] if i < len(scene) else fallback[key]
    except Exception as e:
        print(f"  Pexels scene query failed ({e!r}) — using Picsum fallback for scene slots")
        for key in ["hero", "service_1", "service_2", "service_3", "gallery_1", "gallery_2"]:
            images[key] = fallback[key]

    try:
        people = _fetch(people_q, "portrait", 2)
        images["team_1"] = people[0] if len(people) > 0 else fallback["team_1"]
        images["team_2"] = people[1] if len(people) > 1 else fallback["team_2"]
    except Exception as e:
        print(f"  Pexels people query failed ({e!r}) — using Picsum fallback for team slots")
        images["team_1"] = fallback["team_1"]
        images["team_2"] = fallback["team_2"]

    return images


# Keep old name as alias so any external callers don't break
get_unsplash_images = get_placeholder_images


# --------------------------------------------------------------------------
# PEXELS VIDEO API — hero looping video backgrounds
# --------------------------------------------------------------------------

def localize_pexels_video(site_dir: Path, pexels_url: str, max_bytes: int = 40 * 1024 * 1024) -> dict:
    """Download a Pexels CDN video to `site_dir/public/videos/hero.mp4`, then
    replace every occurrence of the original URL with `/videos/hero.mp4` across
    all generated files. Eliminates the CORS/playback issue that hits some
    browsers when `<video>` streams cross-origin from videos.pexels.com.

    Returns {"downloaded": bool, "files_touched": int, "size_bytes": int, "error": str?}.
    Soft-fails: any exception is captured and reported, no crash.
    """
    result = {"downloaded": False, "files_touched": 0, "size_bytes": 0}
    if not pexels_url or "pexels.com" not in pexels_url:
        return result

    dest = site_dir / "public" / "videos" / "hero.mp4"
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(pexels_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read(max_bytes + 1)
        if len(data) > max_bytes:
            result["error"] = f"video > {max_bytes // (1024*1024)}MB, keeping CDN URL"
            return result
        dest.write_bytes(data)
        result["downloaded"] = True
        result["size_bytes"] = len(data)
        size_mb = len(data) / (1024 * 1024)
        print(f"  Pexels video → {dest.relative_to(site_dir)} ({size_mb:.1f}MB)")
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
        return result

    # Replace the Pexels URL with the local path across every generated file
    try:
        result["files_touched"] = replace_urls_in_site(site_dir, {pexels_url: "/videos/hero.mp4"})
    except Exception as e:
        result["error"] = f"URL replace: {type(e).__name__}: {e}"
    return result


def get_pexels_hero_video(video_keyword: str, api_key: str) -> Optional[str]:
    """Fetch a single landscape hero video URL from Pexels Video API.

    Returns the best-fit MP4 URL or None on any failure. Prefers HD landscape
    at 1920x1080 if available, else falls back to the largest landscape file.
    """
    if not video_keyword or not api_key:
        return None

    params = urllib.parse.urlencode({
        "query": video_keyword,
        "per_page": 10,
        "orientation": "landscape",
        "size": "medium",
    })
    req = urllib.request.Request(
        f"https://api.pexels.com/videos/search?{params}",
        headers={"Authorization": api_key, "User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"  Pexels video query failed ({e!r})")
        return None

    videos = data.get("videos", []) or []
    if not videos:
        return None

    # Pick the first video, then choose the best HD landscape file
    for vid in videos:
        files = vid.get("video_files", []) or []
        # Prefer 1920x1080 mp4
        for f in files:
            if (f.get("file_type") == "video/mp4"
                    and f.get("width") == 1920
                    and f.get("height") == 1080):
                return f.get("link")
        # Else: largest landscape mp4 under 4MB-equivalent quality
        landscape = [
            f for f in files
            if f.get("file_type") == "video/mp4"
            and (f.get("width") or 0) >= (f.get("height") or 0)
        ]
        if landscape:
            landscape.sort(key=lambda f: f.get("width", 0), reverse=True)
            return landscape[0].get("link")

    return None


# --------------------------------------------------------------------------
# GEMINI IMAGEN — AI image generation
# Replaces Pexels placeholders with industry-specific generated images.
# No faces visible; back-view or no-people compositions only.
# --------------------------------------------------------------------------

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
        print("  Imagen: google-genai not installed, skipping")
        return {}
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("  Imagen: GOOGLE_API_KEY not set, skipping")
        return {}

    slots = slots or ["hero", "service_1", "service_2", "service_3",
                      "team_1", "team_2", "gallery_1", "gallery_2"]
    images_dir = output_dir / "public" / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    try:
        client = _genai.Client(api_key=api_key)
    except Exception as e:
        print(f"  Imagen client init failed: {e}")
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
            slot_filename = f"{slot}.jpg"
            (images_dir / slot_filename).write_bytes(img_bytes)
            results[slot] = f"/images/{slot_filename}"
            print(f"  Imagen: {slot} → {slot_filename}")
        except Exception as e:
            # Skip the slot but keep going
            print(f"  Imagen: {slot} failed ({type(e).__name__}: {e})")
            continue

    return results


# --------------------------------------------------------------------------
# FIGMA — read a Figma file when the user provides a URL + token in .env
# --------------------------------------------------------------------------

_FIGMA_FILE_RE = re.compile(r"figma\.com/(?:file|design)/([A-Za-z0-9]+)/")


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


def apply_imagen_to_site(industry: str, site_dir: Path, pexels_images: dict[str, str]) -> tuple[dict[str, str], int]:
    """Generate Imagen images for the standard slots, write them under
    `site_dir/public/images/`, then replace the matching Pexels URLs across
    all generated files with the new local paths.

    Returns (generated_slot_to_path_map, files_touched).
    Gated on PEBBLE_USE_IMAGEN=true (defaults off to avoid surprise costs).
    """
    enabled = os.environ.get("PEBBLE_USE_IMAGEN", "").strip().lower() in {"1", "true", "yes", "on"}
    if not enabled:
        return {}, 0
    if not industry:
        return {}, 0
    slots = list(pexels_images.keys()) if pexels_images else [
        "hero", "service_1", "service_2", "service_3",
        "team_1", "team_2", "gallery_1", "gallery_2",
    ]
    generated = generate_imagen_images(industry, site_dir, slots=slots)
    if not generated:
        return {}, 0
    url_map: dict[str, str] = {}
    for slot, pexels_url in (pexels_images or {}).items():
        local = generated.get(slot)
        if pexels_url and local:
            url_map[pexels_url] = local
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
# --------------------------------------------------------------------------

def figma_file_summary(figma_url: str) -> Optional[dict]:
    """Pull a lightweight summary of a Figma file (name, colors, first frames).

    Returns None unless both the URL is valid and FIGMA_ACCESS_TOKEN is set.
    The summary is meant to be fed to the LLM as additional design context.
    """
    if not figma_url:
        return None
    token = os.environ.get("FIGMA_ACCESS_TOKEN", "").strip()
    if not token:
        return None
    m = _FIGMA_FILE_RE.search(figma_url)
    if not m:
        return None
    file_id = m.group(1)
    req = urllib.request.Request(
        f"https://api.figma.com/v1/files/{file_id}?depth=2",
        headers={"X-Figma-Token": token, "User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"  Figma fetch failed: {e}")
        return None
    summary = {
        "file_id": file_id,
        "name": data.get("name", ""),
        "last_modified": data.get("lastModified", ""),
        "thumbnail_url": data.get("thumbnailUrl", ""),
        "pages": [p.get("name", "") for p in data.get("document", {}).get("children", [])][:10],
    }
    return summary


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
)


# --------------------------------------------------------------------------
# BUSINESS INTELLIGENCE SKILL LOADER
# --------------------------------------------------------------------------

# Skill files loaded into the prompt at import time. The visitor-experience
# skill was loaded but never referenced — removed in this audit. If we want
# it back in the future, add it to the prompt template AND to this list in
# the same commit so there are no dead loads.
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
    images: dict[str, str] = None,
    industry_intel: Optional[dict] = None,
    hero_video_url: Optional[str] = None,
    design_reference: Optional[dict] = None,
    design_dna: Optional[dict] = None,
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

    # Hero video block (Pexels Video API, when industry intel says hero_type=video)
    if hero_video_url:
        hero_video_block = (
            f"\n**Pexels hero video URL (drop-in for `<video src=...>`):**\n\n"
            f"`{hero_video_url}`\n\n"
            "Use this exact URL in the hero `<video autoPlay muted loop playsInline>` element. "
            "Add a still-frame poster from the Pexels image set in Section 8b. "
            "Add `video: { remotePatterns: [{ protocol: 'https', hostname: 'videos.pexels.com' }] }` is NOT needed — "
            "the URL is served directly by the `<video>` element, not `next/image`. "
            "Just allow `videos.pexels.com` in any CSP if you set one."
        )
    else:
        hero_video_block = "\n*(No Pexels hero video resolved. If Industry Intelligence specifies `hero_type: video`, fall back to a full-bleed Pexels image with `parallax-bg`.)*\n"

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

    # No-slop skill
    if _NS_SKILL:
        # The no-slop skill lists "acceptable display fonts" (Fraunces, Syne, etc.)
        # The Design DNA at the top of this prompt overrides that list — use the DNA's fonts
        # even if they're not on the no-slop list, and DO NOT use no-slop fonts if they
        # aren't named by the DNA. The rest of the no-slop rules (no fake testimonials,
        # no convergence Inter/Poppins as display, no "Where X meets Y" copy) still apply.
        no_slop_block = "\n\n*(NOTE: The Design DNA block at the top of this prompt overrides the font list below. Use the DNA's display/body/mono fonts. All other no-slop rules apply.)*\n\n" + _NS_SKILL.strip() + "\n"
    else:
        no_slop_block = "\n*(No-slop skill not loaded — apply general quality rules: no 555 phone numbers, no 'Where X meets Y' subtext, no vague superlatives, hero must have visual element.)*\n"

    # iOS skill
    if _IOS_SKILL:
        ios_skill_block = f"\n\n{_IOS_SKILL.strip()}\n"
    else:
        ios_skill_block = "\n*(iOS skill not loaded -- apply standard iOS Safari fixes: 100dvh, normalizeScroll, muted playsInline video, 16px inputs, safe-area-inset.)*\n"

    # Stack skill
    if _STACK_SKILL:
        stack_block = f"\n\nRead and follow the Stack Skill below for project structure, dependencies, motion components, and handoff files.\n\n{_STACK_SKILL.strip()}\n"
    else:
        stack_block = "\nNext.js 14 + React 18 + TypeScript + Tailwind CSS v3 + GSAP + Lenis. Follow the project structure in the Stack Skill.\n"

    # Business intelligence skill
    if _BI_SKILL:
        bi_block = f"\n\n{_BI_SKILL.strip()}\n"
    else:
        bi_block = "\n*(Business intelligence skill not loaded -- apply general conversion best practices.)*\n"

    if ds_text:
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

    # Images block
    if images:
        uses_pexels = any("pexels.com" in url for url in images.values())
        source_label = "Pexels industry-relevant photos" if uses_pexels else "Picsum Photos"
        image_lines = [f"**Use these {source_label} as placeholder images in your build:**\n"]
        for label, url in images.items():
            clean_label = label.replace("_", " ").title()
            image_lines.append(f"- **{clean_label}:** `{url}`")
        image_lines.append("\n**Important:**")
        image_lines.append("- Use these exact URLs in `next/image` `src` props — never raw `<img>` tags")
        image_lines.append("- Do NOT use local paths like `/images/hero.jpg`")
        image_lines.append("- Add `priority` only to the hero image; all others lazy-load by default")
        image_lines.append("- Document all images in TODO_ASSETS.md so client knows to replace with real photos")
        image_lines.append("- Add descriptive alt text for each image")
        if uses_pexels:
            image_lines.append("- **next.config.ts**: `images.pexels.com` MUST be in `remotePatterns` or `next/image` will throw — see Stack skill for the complete config")
        images_block = "\n".join(image_lines)
    else:
        images_block = "\n*(No placeholder images available -- use descriptive alt text with empty src, or use Unsplash source URLs.)*\n"

    # Real contact info, or visible placeholders when blank
    phone   = (answers.get("phone")   or "[BUSINESS PHONE]").strip() or "[BUSINESS PHONE]"
    email   = (answers.get("email")   or "[EMAIL]").strip()         or "[EMAIL]"
    address = (answers.get("address") or "[ADDRESS]").strip()       or "[ADDRESS]"
    services_offered = (answers.get("services_offered") or "*(infer from industry — list the standard services for this business type)*").strip()

    rendered = PROMPT_TEMPLATE.format(
        business_name=answers.get("business_name", ""),
        business_type=industry,
        location=answers.get("location", ""),
        services_offered=services_offered,
        phone=phone,
        email=email,
        address=address,
        visitor_action=visitor_action,
        booking_system=booking_str,
        industry_intel_block=industry_intel_block,
        resolved_contract=resolved_contract,
        reference_block=reference_block,
        design_reference_block=design_reference_block,
        extra_context=extra_block,
        no_slop_block=no_slop_block,
        ios_skill_block=ios_skill_block,
        stack_block=stack_block,
        business_intelligence_block=bi_block,
        industry_research_block=research_block,
        design_system_block=ds_block,
        images_block=images_block,
        hero_video_block=hero_video_block,
        anti_slop_block=anti_slop_block,
    )

    # Prepend the Design DNA block (if any) so it sits at the very top of the
    # prompt with override priority. The LLM reads top-down; an OVERRIDE-framed
    # block at line 1 beats Fraunces/Inter mentions buried 1000 lines deeper.
    if design_dna and build_dna_block:
        try:
            return build_dna_block(design_dna) + rendered
        except Exception as e:
            print(f"  DNA block render failed: {e}")
    return rendered


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

FILE_BLOCK_RE = re.compile(
    r'<pebble-file\s+path="([^"]+)">\s*\n(.*?)\n?\s*</pebble-file>',
    re.DOTALL,
)


def parse_files(llm_output: str) -> list[tuple[str, str]]:
    return FILE_BLOCK_RE.findall(llm_output)


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
- No local file references — use the Pexels/Picsum URLs from Section 8b directly in `src` and `style="background-image:url(...)"`.
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

    # ---- GET ----
    def do_GET(self):
        # Strip query string for route matching (e.g. /?t=12345 should still serve index.html)
        raw_path = self.path
        path_only = raw_path.split("?", 1)[0]
        self.path = path_only
        try:
            if path_only in ("/", "/index.html"):
                self._serve_file(INDEX_HTML, "text/html; charset=utf-8")
            elif self.path == "/api/health":
                self._handle_health()
            elif self.path == "/api/industries":
                self._handle_list_industries()
            elif self.path == "/api/briefs":
                self._handle_list_briefs()
            elif self.path.startswith("/api/briefs/"):
                slug = self.path.split("/api/briefs/", 1)[1]
                self._handle_get_brief(slug)
            elif self.path.startswith("/preview/"):
                self._handle_preview()
            elif self.path.startswith("/static/"):
                self._handle_static()
            else:
                self.send_response(404); self.end_headers()
                self.wfile.write(b"Not found")
        except Exception as exc:
            try:
                self._json(500, {"error": f"Server error: {exc}"})
            except Exception:
                pass

    # ---- POST ----
    def do_POST(self):
        try:
            if self.path == "/api/build":
                self._handle_build(generate=False)
            elif self.path == "/api/generate":
                self._handle_build(generate=True)
            elif self.path == "/api/setup":
                self._handle_setup()
            else:
                self.send_response(404); self.end_headers()
        except Exception as exc:
            try:
                self._json(500, {"error": f"Server error: {exc}"})
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

    def _handle_static(self):
        """Serve any file under `ui/` at the URL `/static/<relative-path>`.
        Used for the loading-screen video, future image assets, etc."""
        rel = self.path[len("/static/"):]
        if not rel or ".." in rel.split("/") or rel.startswith("/"):
            self.send_response(403); self.end_headers(); return
        file = PROJECT_ROOT / "ui" / rel
        if not file.exists() or not file.is_file():
            self.send_response(404); self.end_headers()
            self.wfile.write(f"Static asset not found: {rel}".encode()); return
        ext = file.suffix.lstrip(".").lower()
        ct_map = {
            "mp4":  "video/mp4",
            "webm": "video/webm",
            "mov":  "video/quicktime",
            "png":  "image/png",
            "jpg":  "image/jpeg",
            "jpeg": "image/jpeg",
            "gif":  "image/gif",
            "svg":  "image/svg+xml",
            "css":  "text/css; charset=utf-8",
            "js":   "application/javascript; charset=utf-8",
            "ico":  "image/x-icon",
            "woff": "font/woff",
            "woff2":"font/woff2",
        }
        ct = ct_map.get(ext, "application/octet-stream")
        self._serve_file(file, ct)

    def _handle_preview(self):
        rest = self.path[len("/preview/"):]
        if not rest:
            self.send_response(404); self.end_headers(); return
        parts = rest.split("/", 1)
        slug = _slugify(parts[0])
        rel = parts[1] if len(parts) > 1 and parts[1] else "index.html"
        if ".." in rel.split("/"):
            self.send_response(403); self.end_headers(); return
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
        self._serve_file(site_file, ct)

    def _handle_build(self, generate: bool):
        length = int(self.headers.get("Content-Length", "0"))
        try:
            answers = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            self._json(400, {"error": "invalid json"}); return

        slug = _slugify(answers.get("business_name", "untitled"))
        answers["_slug"] = slug
        if "_created_at" not in answers:
            answers["_created_at"] = datetime.now().isoformat()

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
                print(f"  industry intel resolution failed: {e}")

        # Research industry for data-driven recommendations (the long-form text block)
        research_text = ""
        if business_type:
            try:
                research_text = research_industry(business_type)
            except Exception as e:
                print(f"Industry research failed: {e}")
                research_text = ""  # Continue without research

        # Fetch placeholder images (Pexels if key present, else Picsum)
        images = {}
        if business_type:
            try:
                _pexels_key = os.environ.get("PEXELS_API_KEY", "").strip()
                if _pexels_key:
                    print("  Fetching industry photos from Pexels...")
                    images = get_pexels_images(business_type, _pexels_key)
                else:
                    images = get_placeholder_images(business_type)
            except Exception as e:
                print(f"Image fetching failed: {e}")
                images = get_placeholder_images(business_type)

        # Hero video (Pexels Video API) — only when industry intel says hero_type=video
        hero_video_url: Optional[str] = None
        if industry_intel and industry_intel.get("hero_type") == "video":
            _pexels_key = os.environ.get("PEXELS_API_KEY", "").strip()
            video_keyword = industry_intel.get("video_keyword", "") or business_type
            if _pexels_key and video_keyword:
                try:
                    print(f"  Fetching Pexels hero video for '{video_keyword}'...")
                    hero_video_url = get_pexels_hero_video(video_keyword, _pexels_key)
                    if hero_video_url:
                        print(f"  Pexels video resolved: {hero_video_url[:80]}...")
                except Exception as e:
                    print(f"  Pexels video fetch failed: {e}")

        # Design reference (Figma URL — uploaded image attachments come via the API payload)
        design_reference: dict = {}
        figma_url = (answers.get("figma_url") or "").strip()
        if figma_url:
            summary = figma_file_summary(figma_url)
            if summary:
                design_reference["figma_url"] = figma_url
                design_reference["figma_summary"] = summary
        # Image attachments (base64 list — added by quiz upload field)
        attachments = answers.get("design_reference_images") or []
        if attachments:
            design_reference["image_count"] = len(attachments)
            design_reference["_raw_attachments"] = attachments

        # Style DNA — random per-build aesthetic personality. Same business +
        # same industry generates a different-looking site each time because
        # the DNA dictates fonts, hero structure, motion, and layout posture.
        design_dna = None
        if _DNA_OK and pick_random_dna:
            try:
                design_dna = pick_random_dna()
                answers["_design_dna"] = design_dna["id"]
                print(f"  Design DNA: {design_dna['label']} ({design_dna['id']})")
            except Exception as e:
                print(f"  DNA picker failed: {e}")

        notes = audit_design_system(ds_text) if ds_text else []
        prompt = build_prompt(
            answers, ds_text, notes, research_text, images,
            industry_intel=industry_intel,
            hero_video_url=hero_video_url,
            design_reference=design_reference or None,
            design_dna=design_dna,
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
        (out_dir / "PROMPT.md").write_text(prompt, encoding="utf-8")

        if not generate:
            self._json(200, {
                "prompt": prompt,
                "warning_count": len(notes),
                "slug": slug,
                "saved_to": f"output/{slug}/",
            }); return

        client, reason = get_llm_client()
        if not client:
            self._json(503, {
                "error": f"LLM not configured: {reason}",
                "prompt": prompt, "warning_count": len(notes),
                "slug": slug, "saved_to": f"output/{slug}/",
            }); return

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
                    "7. All image src values: use the Pexels/Picsum URLs from the brief — never local paths.\n"
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
            # Vision attachments — design reference screenshots uploaded in the quiz
            vision_images = (design_reference or {}).get("_raw_attachments") if design_reference else None
            response = client.generate(
                system=system,
                user=full_user,
                max_tokens=_max_tok,
                images=vision_images,
            )
            elapsed = time.time() - t0
        except LLMError as e:
            self._json(500, {
                "error": str(e),
                "prompt": prompt, "warning_count": len(notes),
                "slug": slug, "saved_to": f"output/{slug}/",
            }); return

        files = parse_files(response)
        (out_dir / "llm_response_raw.txt").write_text(response, encoding="utf-8")

        if not files:
            self._json(500, {
                "error": "LLM response had no <pebble-file> blocks. Raw response saved to llm_response_raw.txt.",
                "prompt": prompt, "warning_count": len(notes),
                "slug": slug, "saved_to": f"output/{slug}/",
                "raw_preview": response[:1500],
            }); return

        site_dir = out_dir / "site"
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

        (out_dir / "build_meta.json").write_text(json.dumps({
            "model": client.model,
            "elapsed_seconds": round(elapsed, 1),
            "file_count": len(written),
            "built_at": datetime.now().isoformat(),
        }, indent=2))

        # ---- POST-BUILD CHAIN ----
        # Each step degrades gracefully: failure does not block the response.

        # Pexels video → local /public/videos/hero.mp4
        # Eliminates CORS/playback issues with cross-origin <video> from videos.pexels.com.
        pexels_video_results: dict = {"downloaded": False, "files_touched": 0}
        if hero_video_url and "pexels.com" in hero_video_url:
            try:
                pexels_video_results = localize_pexels_video(site_dir, hero_video_url)
            except Exception as e:
                pexels_video_results["error"] = f"{type(e).__name__}: {e}"

        imagen_results: dict = {"generated": {}, "files_touched": 0, "enabled": False}
        try:
            imagen_enabled = os.environ.get("PEBBLE_USE_IMAGEN", "").strip().lower() in {"1", "true", "yes", "on"}
            imagen_results["enabled"] = imagen_enabled
            if imagen_enabled and business_type:
                generated, touched = apply_imagen_to_site(business_type, site_dir, images or {})
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
                    screenshot_info = post_build_screenshots(server_info["url"], out_dir)
                except Exception as e:
                    screenshot_info["errors"].append(f"screenshot crashed: {e}")

        self._json(200, {
            "prompt": prompt, "warning_count": len(notes),
            "slug": slug, "saved_to": f"output/{slug}/",
            "files_written": written, "file_count": len(written),
            "site_path": f"output/{slug}/site/",
            "preview_url": f"/preview/{slug}/",
            "elapsed_seconds": round(elapsed, 1),
            "model": client.model,
            "industry_intel_key": industry_key,
            "hero_video_url": hero_video_url,
            "pexels_video":  pexels_video_results,
            "imagen": imagen_results,
            "dev_server": server_info,
            "screenshots": screenshot_info,
        })

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

    def _json(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
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
    url = f"http://localhost:{port}"
    print(f"   running at {url}\n")
    # ThreadingHTTPServer so a slow LLM build doesn't block other requests
    # (e.g. the browser's keep-alive socket, /api/health, /api/industries).
    server = ThreadingHTTPServer(("127.0.0.1", port), PebbleHandler)
    server.daemon_threads = True
    if open_browser:
        try: webbrowser.open(url)
        except Exception: pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pebble Engine -- visual website briefing.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    serve(port=args.port, open_browser=not args.no_browser)
