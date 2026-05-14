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

def _find_free_port() -> int:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _poll_server(url: str, timeout_seconds: int = 90) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if 200 <= r.status < 500:
                    return True
        except Exception:
            time.sleep(1.5)
    return False


def post_build_run_dev_server(site_dir: Path) -> dict:
    """npm install + next dev on a free port, in the background.

    Returns {"port": int, "pid": int, "url": str, "errors": [str]}.
    Caller is responsible for the lifetime of the spawned process.
    """
    import shutil, subprocess
    result = {"port": None, "pid": None, "url": None, "errors": []}

    if not site_dir.exists() or not (site_dir / "package.json").exists():
        result["errors"].append("no package.json in site_dir; skip dev server")
        return result

    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm:
        result["errors"].append("npm not found in PATH; install Node.js")
        return result

    # 1. npm install — bounded timeout, captured
    print(f"  Running `npm install` in {site_dir.name}...")
    try:
        subprocess.run(
            [npm, "install", "--no-audit", "--no-fund", "--loglevel=error"],
            cwd=str(site_dir),
            check=True,
            timeout=600,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode("utf-8", "ignore") if e.stderr else ""
        result["errors"].append(f"npm install failed: {stderr[:500]}")
        return result
    except subprocess.TimeoutExpired:
        result["errors"].append("npm install timed out after 600s")
        return result

    # 2. Start dev server on a free port in the background
    port = _find_free_port()
    url = f"http://127.0.0.1:{port}"
    print(f"  Starting `next dev` on port {port}...")
    try:
        # Windows requires shell=True for npm.cmd resolution; use creationflags for detached
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        proc = subprocess.Popen(
            [npm, "run", "dev", "--", "-p", str(port)],
            cwd=str(site_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags if sys.platform == "win32" else 0,
        )
    except Exception as e:
        result["errors"].append(f"failed to start dev server: {e}")
        return result

    # 3. Poll until server responds
    # 240s — first build does npm install + initial Next compile, often 2-3 min.
    if not _poll_server(url, timeout_seconds=240):
        result["errors"].append("dev server did not respond within 240s")
        try:
            proc.terminate()
        except Exception:
            pass
        return result

    result["port"] = port
    result["pid"] = proc.pid
    result["url"] = url
    return result


def post_build_screenshots(server_url: str, out_dir: Path) -> dict:
    """Use Playwright to capture hero/trust-bar/services/footer screenshots.

    Gracefully degrades if Playwright is not installed.
    Returns {"screenshots": [relative paths], "errors": [str]}.
    """
    result = {"screenshots": [], "errors": []}
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        result["errors"].append("playwright not installed (pip install playwright && playwright install chromium)")
        return result

    shots_dir = out_dir / "screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()
            page.goto(server_url, wait_until="domcontentloaded", timeout=15000)
            try:
                page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass

            shots = [
                ("01-hero.png",       0),
                ("02-trust-bar.png",  900),
                ("03-services.png",   1800),
                ("04-footer.png",     "bottom"),
            ]
            for filename, scroll in shots:
                try:
                    if scroll == "bottom":
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    else:
                        page.evaluate(f"window.scrollTo(0, {scroll})")
                    page.wait_for_timeout(900)
                    target = shots_dir / filename
                    page.screenshot(path=str(target), full_page=False)
                    result["screenshots"].append(str(target.relative_to(out_dir)))
                except Exception as e:
                    result["errors"].append(f"{filename}: {e}")

            browser.close()
    except Exception as e:
        result["errors"].append(f"playwright run failed: {e}")
    return result


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

RESEARCH_PROMPT_TEMPLATE = """You are a web design researcher conducting industry analysis.

**Your task:** Research the {industry} industry to provide data-driven design recommendations.

**What to research:**
1. Analyze 3-5 top-performing websites in the {industry} industry
2. Identify visual patterns:
   - Light vs dark backgrounds (which converts better for this industry?)
   - Common color palettes and accent colors
   - Typography choices (serif vs sans, formal vs friendly)
   - Motion/animation intensity (minimal, smooth, cinematic?)
3. Customer psychology:
   - What drives purchasing decisions in this industry?
   - What builds trust? (Reviews, credentials, photos, certifications?)
   - What are the typical pain points or anxieties?
4. Conversion elements:
   - Primary CTA patterns (call, book, buy, browse?)
   - Trust signals that work (licenses, awards, testimonials?)
   - Page structure patterns
5. Industry-specific warnings:
   - What looks cheap or unprofessional in this industry?
   - Common mistakes to avoid

**Output format (markdown):**
## Industry Research: {industry}

### Visual Aesthetic Patterns
[What you observed about colors, backgrounds, typography from top sites]

### Motion & Interaction
[Animation intensity, scroll effects, interactivity patterns]

### Customer Psychology
[What drives decisions, what builds trust, what creates anxiety]

### Trust Signals
[Specific elements that build credibility in this industry]

### Industry-Specific Warnings
[What NOT to do - mistakes that hurt conversion in this industry]

### Recommended Approach
[Your data-driven recommendation for: aesthetic, motion, tone, structure]

**Rules:**
- Be specific. Cite patterns from actual top sites.
- Focus on CONVERSION, not just aesthetics.
- If dark backgrounds work for this industry, say so. If they hurt conversion, say so.
- Call out industry-specific quirks (e.g., "luxury real estate can use dark mode; residential real estate cannot")
- Keep it under 800 words. Concise and actionable.

Begin your research now for: {industry}"""


def research_industry(business_type: str, industry_category: str = "") -> str:
    """
    Research an industry using Gemini to provide data-driven design recommendations.
    Results are cached per industry to avoid redundant research.

    Args:
        business_type: The specific business type (e.g., "plumbing", "boat sales")
        industry_category: Optional broader category (e.g., "home services", "luxury")

    Returns:
        Research markdown text or empty string if research fails
    """
    # Normalize industry slug for caching
    industry_slug = _slugify(business_type)
    cache_file = RESEARCH_CACHE_DIR / f"{industry_slug}.md"

    # Check cache first
    if cache_file.exists():
        try:
            cached = cache_file.read_text(encoding="utf-8")
            if cached and len(cached) > 100:  # Basic validation
                return cached
        except Exception:
            pass  # Cache read failed, proceed to research

    # Get LLM client for research
    client, reason = get_llm_client()
    if not client or reason != "ok":
        return ""  # No LLM available, skip research

    # Build research prompt
    research_prompt = RESEARCH_PROMPT_TEMPLATE.format(
        industry=business_type,
    )

    # Call Gemini to research
    try:
        system_instruction = (
            "You are an expert web design researcher. You analyze successful websites "
            "and extract data-driven design patterns. You provide specific, actionable "
            "recommendations based on what actually converts in each industry."
        )

        research_result = client.generate(
            system=system_instruction,
            user=research_prompt,
            max_tokens=2000  # Research should be concise
        )

        # Validate result
        if not research_result or len(research_result) < 100:
            return ""

        # Cache the result
        RESEARCH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(research_result, encoding="utf-8")

        return research_result

    except Exception as e:
        # Research failed, return empty (prompt will work without it)
        print(f"Industry research failed: {e}")
        return ""


# --------------------------------------------------------------------------
# INDUSTRY INTELLIGENCE LAYER
# Structured JSON database of industry-specific design DNA.
# Drives color palette, hero type, Three.js variant, copy tone,
# section order, trust signals, and what to avoid.
#
# Layer 1: static JSON (industries.json)
# Layer 2: LLM fallback that researches a new industry and writes
#          a structured entry back into industries.json
# --------------------------------------------------------------------------

INDUSTRY_RESEARCH_JSON_PROMPT = """You are a web design researcher. Output a single JSON object for the "{industry}" industry that matches this exact schema (no commentary, no markdown fences, no preamble):

{{
  "emotion": "2-4 emotional drivers customers feel (e.g. 'safety, relief, trust')",
  "visual_style": "one short phrase describing the visual aesthetic (e.g. 'dark cinematic, photo-forward')",
  "hero_type": "one of: video | image",
  "video_keyword": "2-6 word Pexels search query for a relevant looping hero video",
  "threejs_type": "one of: none | particles | aurora_mesh | wireframe_geometry | ripple_plane",
  "colors": {{
    "primary": "#RRGGBB hex (brand-ownable, not a generic blue)",
    "accent": "#RRGGBB hex (CTA color)",
    "background": "#RRGGBB hex (page background)"
  }},
  "tone": "2-4 adjective tone (e.g. 'urgent, reassuring, local')",
  "key_sections": ["array of 4-6 section keys in homepage order"],
  "trust_signals": ["array of 3-6 trust signals that work in this industry"],
  "avoid": ["array of 3-5 patterns to never use (must include 'horizontal_scroll')"]
}}

Rules:
- Choose colors that fit the industry psychology — not random tasteful values.
- hero_type is "video" if real-world footage drives the emotion; "image" if minimal editorial is the move.
- threejs_type is "none" unless the industry is abstract/tech/wellness/clean — never decorative.
- "avoid" MUST include "horizontal_scroll" as the first entry.
- Output JSON only. First character must be `{{`. No trailing commentary."""


def _load_industries_intel() -> dict:
    if not INDUSTRIES_JSON.exists():
        return {}
    try:
        return json.loads(INDUSTRIES_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  industries.json load failed: {e}")
        return {}


def _industry_key(text: str) -> str:
    """Normalize 'Pest Control' / 'pest-control' / 'pest_control' to 'pest_control'."""
    text = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return text or "untitled"


def lookup_industry_intel(business_type: str) -> tuple[Optional[str], Optional[dict]]:
    """Find a matching industry entry. Returns (matched_key, entry) or (None, None).

    Match priority: exact key → fuzzy substring → partial word overlap.
    """
    intel = _load_industries_intel()
    if not intel:
        return None, None

    key = _industry_key(business_type)
    if key in intel:
        return key, intel[key]

    # Fuzzy substring — either direction
    bt_lower = business_type.lower()
    for industry_key, entry in intel.items():
        ik_words = industry_key.replace("_", " ")
        if ik_words in bt_lower or any(w in bt_lower for w in ik_words.split() if len(w) > 3):
            return industry_key, entry
        if any(w in ik_words for w in bt_lower.split() if len(w) > 3):
            return industry_key, entry

    return None, None


def research_new_industry(business_type: str) -> Optional[dict]:
    """LLM fallback for industries not in industries.json. Returns a structured
    entry and writes it back into industries.json so the next build is instant."""
    client, reason = get_llm_client()
    if not client or reason != "ok":
        return None

    prompt = INDUSTRY_RESEARCH_JSON_PROMPT.format(industry=business_type)
    system = (
        "You are an industry research engine. You output ONLY a single JSON object "
        "matching the schema in the user message. No prose. No fences. No preamble."
    )
    try:
        raw = client.generate(system=system, user=prompt, max_tokens=1200)
    except Exception as e:
        print(f"  industry intel research failed: {e}")
        return None

    # Strip possible markdown fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```\s*$", "", raw)
    # Take from first { to last } to handle trailing whitespace / commentary
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        print(f"  industry intel: LLM did not return JSON")
        return None
    try:
        entry = json.loads(raw[start : end + 1])
    except Exception as e:
        print(f"  industry intel: JSON parse failed: {e}")
        return None

    # Validate minimum shape
    required = {"emotion", "visual_style", "hero_type", "video_keyword",
                "threejs_type", "colors", "tone", "key_sections",
                "trust_signals", "avoid"}
    if not required.issubset(entry.keys()):
        print(f"  industry intel: missing required keys")
        return None

    # Cache back to industries.json
    try:
        intel = _load_industries_intel()
        intel[_industry_key(business_type)] = entry
        INDUSTRIES_JSON.write_text(
            json.dumps(intel, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"  industry intel: cached new entry for '{business_type}'")
    except Exception as e:
        print(f"  industry intel: cache write failed: {e}")

    return entry


def resolve_industry_intel(business_type: str) -> tuple[Optional[str], Optional[dict]]:
    """One-call API: look up, fall back to LLM, return (key, entry) or (None, None)."""
    if not business_type:
        return None, None
    matched_key, entry = lookup_industry_intel(business_type)
    if entry:
        return matched_key, entry
    # Fallback: research and cache
    print(f"  industry intel: '{business_type}' not in JSON, researching...")
    entry = research_new_industry(business_type)
    if entry:
        return _industry_key(business_type), entry
    return None, None


def build_industry_intel_block(business_type: str, entry: Optional[dict]) -> str:
    """Format an industry intelligence entry as a markdown prompt block."""
    if not entry:
        return "*(No industry intelligence available — Business Intelligence skill governs.)*"

    colors = entry.get("colors", {}) or {}
    key_sections = entry.get("key_sections", []) or []
    trust_signals = entry.get("trust_signals", []) or []
    avoid = entry.get("avoid", []) or []

    return f"""**Industry:** `{business_type}`

This entry was sourced from `industries.json` (or researched + cached on first use). Apply every value below verbatim — they are the design DNA of this industry. The Resolved Design Contract derives from these values, not the other way around.

| Decision | Value |
|---|---|
| **Emotional drivers** | {entry.get("emotion", "")} |
| **Visual style** | {entry.get("visual_style", "")} |
| **Hero type** | `{entry.get("hero_type", "")}` |
| **Pexels video keyword** | `{entry.get("video_keyword", "")}` |
| **Three.js hero variant** | `{entry.get("threejs_type", "none")}` |
| **Primary color** | `{colors.get("primary", "")}` |
| **Accent color** | `{colors.get("accent", "")}` |
| **Background color** | `{colors.get("background", "")}` |
| **Copy tone** | {entry.get("tone", "")} |

**Required homepage sections (in this exact order):**
{chr(10).join(f"- {s}" for s in key_sections)}

**Industry trust signals to surface:**
{chr(10).join(f"- {s}" for s in trust_signals)}

**Never do — automatic build failures:**
{chr(10).join(f"- {a}" for a in avoid)}"""


# --------------------------------------------------------------------------
# BUSINESS INTELLIGENCE SKILL LOADER
# --------------------------------------------------------------------------

BI_SKILL_PATH    = PROJECT_ROOT / "skills" / "business-intelligence" / "SKILL.md"
STACK_SKILL_PATH = PROJECT_ROOT / "skills" / "stack" / "SKILL.md"
IOS_SKILL_PATH   = PROJECT_ROOT / "skills" / "ios" / "SKILL.md"
VX_SKILL_PATH    = PROJECT_ROOT / "skills" / "visitor-experience" / "SKILL.md"
NS_SKILL_PATH    = PROJECT_ROOT / "skills" / "no-slop-web" / "SKILL.md"

def load_business_intelligence() -> str:
    if BI_SKILL_PATH.exists(): return BI_SKILL_PATH.read_text(encoding="utf-8")
    return ""

def load_stack_skill() -> str:
    if STACK_SKILL_PATH.exists(): return STACK_SKILL_PATH.read_text(encoding="utf-8")
    return ""

def load_ios_skill() -> str:
    if IOS_SKILL_PATH.exists(): return IOS_SKILL_PATH.read_text(encoding="utf-8")
    return ""

def load_visitor_experience_skill() -> str:
    if VX_SKILL_PATH.exists(): return VX_SKILL_PATH.read_text(encoding="utf-8")
    return ""

def load_no_slop_skill() -> str:
    if NS_SKILL_PATH.exists(): return NS_SKILL_PATH.read_text(encoding="utf-8")
    return ""

_BI_SKILL    = load_business_intelligence()
_STACK_SKILL = load_stack_skill()
_IOS_SKILL   = load_ios_skill()
_VX_SKILL    = load_visitor_experience_skill()
_NS_SKILL    = load_no_slop_skill()


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

PROMPT_TEMPLATE = """\
# Website Build Brief -- {business_name}

You are building a complete, production-quality website. Read every section of this brief before writing a single line of code. The skills embedded in this brief contain thousands of words of specific, researched direction. Apply all of it.

---

## INDUSTRY INTELLIGENCE — Design DNA For This Industry

This block is sourced from `industries.json` (a curated database of 50+ industries) or researched + cached on first use. Every value below is industry-specific and non-negotiable. The Resolved Design Contract that follows derives its palette, hero type, and Three.js variant from these values.

{industry_intel_block}

---

## RESOLVED DESIGN CONTRACT — Read This First

These values were computed from the Industry Intelligence above + the quiz answers before any skill content was loaded. Skills in later sections are implementation guides — they do not override these values. When any skill content seems to suggest a different choice, the contract wins. Concrete beats ambiguous.

{resolved_contract}

---

## 1. Project Overview

- **Business name:** {business_name}
- **Type of business:** {business_type}
- **Location / service area:** {location}
- **Services offered:** {services_offered}
- **Phone:** {phone}
- **Email:** {email}
- **Address:** {address}
- **Primary visitor action:** {visitor_action}
- **Booking or payment system:** {booking_system}

**Contact info usage:** When a value above is set, use it directly in `<a href="tel:...">`, `<a href="mailto:...">`, and address blocks. When a value is the literal placeholder (`[BUSINESS PHONE]`, `[EMAIL]`, `[ADDRESS]`) or empty, keep the placeholder verbatim — never invent a number, email, or street.

---

## 2. MANDATORY OUTPUT STRUCTURE

The Design DNA block at the top of this prompt names this build's aesthetic identity (Swiss Magazine, Brutalist Editorial, Terminal Operator, Cinematic IMAX, etc.). The structure below is a **fallback default** — when the DNA describes a different hero structure, motion intensity, or section pattern, the DNA wins. The constants below (page list, full pages, no card grids, headline presence) still apply.

### Required Pages

1. **Homepage** (`app/page.tsx`) — landing page, full of life, follows the DNA's posture
2. **Services** (`app/services/page.tsx`) — full-bleed alternating layout, NOT a generic card grid
3. **About** (`app/about/page.tsx`) — editorial story
4. **Contact** (`app/contact/page.tsx`) — working form with success state, map embed

### Homepage — Default Section Structure (override per DNA)

**Section 1: Hero — Full Viewport** (default; DNA may redefine the hero entirely)
- `min-h-[100dvh]` always — never `min-h-screen`
- The Design DNA's `Hero structure` section is authoritative. The defaults below apply only if the DNA's hero is silent on a detail.
- **Default video hero** (when DNA permits and Resolved Contract says video): `<video autoPlay muted loop playsInline>` — use the hero Pexels URL as `poster` attribute
- **Default image hero** (when DNA permits and no video): full-bleed `next/image` with `priority` and a `className="parallax-bg"` wrapper
- **Default content layout** (DNA may rearrange or replace):
  1. `<p className="hero-eyebrow">` — location · industry tagline
  2. `<h1 className="hero-heading">` — the main headline, set in the DNA's display font at the size the DNA specifies. **THIS MUST BE PRESENT AND VISIBLE. No hero without a large headline.**
  3. `<p className="hero-sub">` — supporting sentence naming the outcome
  4. `<div className="hero-cta flex gap-4">` — primary + secondary CTA
  5. `<div className="hero-badge">` — floating trust signal (years · certified · insured)
- DO NOT (regardless of DNA): plain white centered hero with only CTA buttons and no headline, dead links, placeholder Lorem ipsum
- The DNA may legitimately call for: a typographic-only hero (no image/video), a split-screen asymmetric hero, a centered editorial hero, a boot-sequence terminal hero, a layered chaotic hero. Follow the DNA.

**Section 2: Trust Bar — Counting Stats**
- Dark or brand-accent background strip — NOT white
- 3–4 numbers that count up on scroll: years in business, jobs completed, rating, insured/certified
- Each number uses `data-target` attribute + GSAP textContent counter (see Code Patterns)
- Single horizontal row — NOT cards, NOT icons in a grid

**Section 3: Services — Full-Bleed Alternating Sections**
Stack services as full-width vertical sections — a 3-column card grid is forbidden, and horizontal scroll is forbidden. Each service is a full-width section. Image fills one half, text the other. Alternate: image-left/text-right, text-left/image-right. Every image uses clip-path reveal (see Code Patterns). For 4+ services, stack all of them — vertical rhythm is the point, no carousels.

**Section 4: Social Proof — Dark Editorial**
- Dark background
- ONE large quote, 3–4rem font size, centered — not a carousel of small cards
- Stars above the quote, attribution below (name + specific result: "saved $3,200" / "back in 2 days")
- If no testimonials: bold credibility statement with a striking number ("Over 1,200 vehicles restored")

**Section 5: About / Story — Parallax Editorial**
- Full-bleed parallax background image (see Code Patterns)
- Owner story: specific, first-person, human — NOT "we are committed to excellence"
- Credentials woven into narrative — not a badge row
- Link to full About page

**Section 6: FAQ or Feature Callout**
- FAQ: 4–6 accordion questions, industry-specific, genuinely useful answers
- Alternative if few questions: a "Why us" section with 2–3 bold differentiating claims

**Section 7: Final CTA — Full Bleed, One Action**
- Full-width section, brand dark or strong accent color
- ONE headline + ONE large centered CTA button
- Phone number as secondary option beneath it
- NO competing buttons

**Section 8: Footer**
- tel: links, mailto: links, address, hours, social icons, copyright

### Navigation — Animated Header

- Fixed position, `className="navbar"` on `<header>` (required for animation below)
- Logo left · nav links center · phone CTA right
- Mobile: hamburger → fullscreen overlay with staggered link reveals
- CTA button: `<a href="tel:[BUSINESS PHONE]">` — never a dead link

---

### REQUIRED TECH STACK

```json
{{
  "dependencies": {{
    "next": "^15.0.0",
    "react": "^19.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "gsap": "^3.12.0",
    "@gsap/react": "^2.1.0",
    "lenis": "^1.1.0",
    "framer-motion": "^11.0.0"
  }}
}}
```

**Performance non-negotiables:**
- `next/image` for ALL images — never raw `<img>` tags. Use `fill` + `object-cover` for full-bleed, explicit `width`/`height` for fixed-size. `priority` on hero image only.
- `next/font/google` for both fonts — zero layout shift
- `gsap.registerPlugin(ScrollTrigger, SplitText)` at module level — never inside useEffect
- `dynamic()` with `{{ ssr: false }}` for any component using `window` or `document`
- `will-change: transform` only during active animation — remove after with `gsap.set(el, {{ clearProps: "willChange" }})`
- `@media (prefers-reduced-motion: reduce) {{ * {{ animation-duration: 0.01ms !important }} }}` in globals.css

---

### CINEMATIC CODE PATTERNS — Implement Verbatim

#### 1. Hero Entrance — Vanilla Word Splitter (NO SplitText)

**DO NOT import `gsap/SplitText`.** SplitText is a paid Club GSAP plugin — importing it crashes with `Module not found: gsap/SplitText` on any project without a Club license. Use this vanilla splitter instead. It's free, lightweight, and produces the same staggered word reveal.

```tsx
"use client"
import {{ useGSAP }} from "@gsap/react"
import gsap from "gsap"

// Vanilla word splitter — wraps each word in nested spans so we can clip + translate
function splitWords(el: HTMLElement): HTMLElement[] {{
  const text = (el.textContent ?? "").trim()
  el.innerHTML = text
    .split(/\\s+/)
    .filter(Boolean)
    .map(w => `<span class="word" style="display:inline-block;overflow:hidden"><span class="word-inner" style="display:inline-block">${{w}}</span></span>`)
    .join(" ")
  return Array.from(el.querySelectorAll<HTMLElement>(".word-inner"))
}}

useGSAP(() => {{
  const heading = document.querySelector<HTMLElement>(".hero-heading")
  const words = heading ? splitWords(heading) : []

  const tl = gsap.timeline({{ delay: 0.1, defaults: {{ ease: "expo.out" }} }})
  tl.from(".hero-eyebrow", {{ opacity: 0, y: 16, duration: 0.6 }})
    .from(words,           {{ opacity: 0, y: 52, stagger: 0.06, duration: 0.85 }}, "-=0.3")
    .from(".hero-sub",     {{ opacity: 0, y: 20, duration: 0.7 }}, "-=0.5")
    .from(".hero-cta",     {{ opacity: 0, y: 20, stagger: 0.1, duration: 0.6 }}, "-=0.4")
    .from(".hero-badge",   {{ opacity: 0, scale: 0.9, duration: 0.5 }}, "-=0.3")
}})
```

Apply: `className="hero-eyebrow"`, `"hero-heading"`, `"hero-sub"`, `"hero-cta"` (on each CTA), `"hero-badge"`.

#### 2. Navbar — Hide/Show + Background Fill (No Flicker On Load)

**Initialize the navbar with an opaque background on first paint** — never transparent. A transparent navbar above a dark hero looks fine, but the moment the loading screen dismisses you get an ugly flicker because GSAP hasn't read scroll position yet. The fix: read `window.scrollY` synchronously on mount and apply the right state before the first paint.

```tsx
"use client"
import {{ useEffect, useRef }} from "react"
import {{ useGSAP }} from "@gsap/react"
import gsap from "gsap"
import {{ ScrollTrigger }} from "gsap/ScrollTrigger"

export function Header() {{
  const ref = useRef<HTMLElement>(null)

  // Set the initial bg state synchronously after mount so the navbar
  // never appears unstyled — even for one frame.
  useEffect(() => {{
    const el = ref.current
    if (!el) return
    const darkSite = document.body.dataset.theme === "dark"
    const atTop = window.scrollY <= 60
    el.style.backgroundColor = atTop ? "transparent" : (darkSite ? "rgba(10,10,10,0.92)" : "rgba(255,255,255,0.92)")
    el.style.backdropFilter  = atTop ? "blur(0px)" : "blur(14px)"
    el.style.boxShadow       = atTop ? "none"      : "0 1px 0 rgba(0,0,0,0.08)"
  }}, [])

  useGSAP(() => {{
    let lastY = 0
    const darkSite = document.body.dataset.theme === "dark"

    ScrollTrigger.create({{
      onUpdate: () => {{
        const y = window.scrollY
        const scrollingDown = y > lastY && y > 80
        gsap.to(ref.current, {{
          yPercent: scrollingDown ? -100 : 0,
          duration: 0.35,
          ease: "power2.out",
          overwrite: "auto",
        }})

        const bg = darkSite ? "rgba(10,10,10,0.92)" : "rgba(255,255,255,0.92)"
        gsap.to(ref.current, {{
          backgroundColor: y > 60 ? bg : "transparent",
          backdropFilter:  y > 60 ? "blur(14px)" : "blur(0px)",
          boxShadow:       y > 60 ? "0 1px 0 rgba(0,0,0,0.08)" : "none",
          duration: 0.3,
          overwrite: "auto",
        }})
        lastY = y
      }},
    }})
  }})

  // Header must NOT be a child of any `overflow:hidden` container — iOS will break the fixed positioning.
  return <header ref={{ref}} className="navbar fixed top-0 inset-x-0 z-50">{{/* ... */}}</header>
}}
```

#### 3. Clip-Path Image Reveal

```tsx
useGSAP(() => {{
  gsap.utils.toArray<HTMLElement>(".reveal-image").forEach((img) => {{
    gsap.fromTo(img,
      {{ clipPath: "inset(0 100% 0 0)" }},
      {{
        clipPath: "inset(0 0% 0 0)",
        duration: 1.1,
        ease: "expo.out",
        scrollTrigger: {{ trigger: img, start: "top 78%" }},
      }}
    )
  }})
}})
```

Add `className="reveal-image"` to every `<Image>` that should reveal on scroll.

#### 4. Counting Stats

```tsx
useGSAP(() => {{
  gsap.utils.toArray<HTMLElement>(".stat-number").forEach((el) => {{
    const target = parseInt(el.dataset.target ?? "0", 10)
    gsap.fromTo(el,
      {{ textContent: 0 }},
      {{
        textContent: target,
        duration: 2,
        ease: "power2.out",
        snap: {{ textContent: 1 }},
        scrollTrigger: {{ trigger: el, start: "top 85%" }},
      }}
    )
  }})
}})
```

JSX: `<span className="stat-number" data-target={{500}}>0</span>`

#### 5. Parallax Background — Wrap `<Image>` In A `<div ref>`

**CRITICAL: `next/image` does NOT forward refs.** Attaching a `ref` directly to `<Image>` throws `Function components cannot be given refs` at runtime. The fix is always the same: wrap the `<Image>` in a `<div ref={{...}}>` and animate the wrapper.

```tsx
"use client"
import {{ useRef }} from "react"
import Image from "next/image"
import {{ useGSAP }} from "@gsap/react"
import gsap from "gsap"
import {{ ScrollTrigger }} from "gsap/ScrollTrigger"

export function ParallaxHero() {{
  const sectionRef = useRef<HTMLElement>(null)
  const bgRef      = useRef<HTMLDivElement>(null)   // ← ref goes on the DIV, never the <Image>

  useGSAP(() => {{
    if (!bgRef.current) return
    gsap.to(bgRef.current, {{
      yPercent: -25,
      ease: "none",
      scrollTrigger: {{
        trigger: sectionRef.current,
        start: "top top",
        end: "bottom top",
        scrub: 1,
      }},
    }})
  }}, {{ scope: sectionRef }})

  return (
    <section ref={{sectionRef}} className="relative overflow-hidden min-h-[100dvh]">
      <div ref={{bgRef}} className="absolute inset-0 parallax-bg">
        <Image src="..." alt="..." fill className="object-cover" priority />
      </div>
      {{/* content above the parallax bg */}}
    </section>
  )
}}
```

Same rule applies anywhere you animate an image: **the ref goes on a wrapping div, never on `<Image>`**. This includes clip-path reveals — `className="reveal-image"` should be applied to a `<div>` wrapper, not the `<Image>` itself.

Apply `className="parallax-bg"` to the wrapper div, not the `<Image>`.

#### 6. FAQ Accordion — Use `transitionend`, NOT `setTimeout`

When an accordion opens, `ScrollTrigger.refresh()` must fire AFTER the layout actually settles. Using `setTimeout(refresh, 300)` is fragile — if the CSS transition is interrupted or slower than expected, trigger positions are stale. Always listen for `transitionend` on the panel.

```tsx
"use client"
import {{ useRef, useState }} from "react"
import {{ ScrollTrigger }} from "gsap/ScrollTrigger"

export function FAQItem({{ question, answer }}: {{ question: string; answer: string }}) {{
  const panelRef = useRef<HTMLDivElement>(null)
  const [open, setOpen] = useState(false)

  const toggle = () => {{
    const next = !open
    setOpen(next)
    const panel = panelRef.current
    if (!panel) return

    // Wait for the CSS height/maxHeight transition to finish, then refresh ScrollTrigger.
    const onTransitionEnd = (e: TransitionEvent) => {{
      if (e.target !== panel) return
      ScrollTrigger.refresh()
      panel.removeEventListener("transitionend", onTransitionEnd)
    }}
    panel.addEventListener("transitionend", onTransitionEnd)
  }}

  return (
    <div className="border-b border-white/10">
      <button onClick={{toggle}} className="w-full flex justify-between py-6">
        <span>{{question}}</span>
        <span className={{`transition-transform ${{open ? "rotate-180" : ""}}`}}>↓</span>
      </button>
      <div
        ref={{panelRef}}
        className="overflow-hidden transition-[max-height] duration-300 ease-out"
        style={{{{ maxHeight: open ? "500px" : "0px" }}}}
      >
        <p className="pb-6 text-on-surface-variant">{{answer}}</p>
      </div>
    </div>
  )
}}
```

Never call `ScrollTrigger.refresh()` inside a bare `setTimeout` after an animation. Always wait for the actual `transitionend` (or `animationend`).

---

#### 7. Three.js Hero Background (when industry intel says so)

Only include Three.js if Section "INDUSTRY INTELLIGENCE" → `threejs_type` is **not** `none`. Use dynamic import with `ssr: false`. The hero `<video>` and Three.js canvas are mutually exclusive — pick the one the contract names.

Variants (drive the renderer choice from `threejs_type`):
- `particles` — tech, services, security, IT: drifting particle field, slow camera dolly
- `aurora_mesh` — beauty, wellness, med-spa: soft gradient mesh, slow undulation
- `wireframe_geometry` — architecture, marketing-agency: rotating wireframe forms, low-poly
- `ripple_plane` — pools, cleaning, plumbing: subtle water-ripple shader plane, scroll-reactive

Performance rules (iOS-safe):
```tsx
const Hero3D = dynamic(() => import("@/components/three/Hero3D"), {{ ssr: false }})

<Canvas
  gl={{ antialias: false, powerPreference: "high-performance" }}
  dpr={{[1, 2]}}
  camera={{ position: [0, 0, 5], fov: 45 }}
>
  {{/* variant geometry */}}
</Canvas>
```

Mandatory: context-lost handler, dispose geometries/materials on unmount, cap DPR at 2.

---

### Working CTAs — Zero Dead Links

| CTA | Implementation |
|---|---|
| Phone | `<a href="tel:[BUSINESS PHONE]">` |
| Email | `<a href="mailto:[EMAIL]">` |
| Book | External booking URL or `onClick` scroll to `#contact` |
| Form submit | `onSubmit` with `e.preventDefault()` + success state — never just `href="#"` |
| Page nav | `<Link href="/services">` — real Next.js routes only |

---

### Image Usage

Section 8b provides Pexels photo URLs. Use `next/image` — never raw `<img>`:

```tsx
import Image from "next/image"

<div className="relative overflow-hidden">
  <Image
    src="https://images.pexels.com/photos/..."
    alt="descriptive alt text"
    fill
    className="object-cover reveal-image"
    priority={{false}}
  />
</div>
```

Hero image only: add `priority` prop. All others: lazy load (default).

### Delivery Checklist

- [ ] Hero: video OR full-bleed image with overlay — no flat backgrounds
- [ ] Hero headline: `<h1 className="hero-heading">` present, visible, and large (min text-6xl) — a hero with only CTA buttons is incomplete
- [ ] Hero entrance: SplitText word-by-word headline on mount
- [ ] Navbar: hides scroll-down, returns scroll-up, fills blur at 60px
- [ ] Trust bar: counting stats with `data-target` + GSAP textContent
- [ ] Services: full-bleed vertical alternating sections — NEVER 3-column card grid, NEVER horizontal scroll
- [ ] Social proof: dark section, one large quote
- [ ] All section images: `next/image` + clip-path reveal on scroll
- [ ] All phone CTAs: `href="tel:..."` — zero `href="#"` links
- [ ] Contact form: `onSubmit` + success state
- [ ] `prefers-reduced-motion` in globals.css
- [ ] 4 pages: Homepage, Services, About, Contact
- [ ] All docs: README, HANDOFF, TODO_ASSETS, STYLE_GUIDE

---

## 3. Visual Reference & Inspiration

{reference_block}

### Design Reference (Figma / Screenshot)

{design_reference_block}

---

## 4. Additional Context

{extra_context}

---

## 5. No-Slop Rules
{no_slop_block}

---

## 6. Business Intelligence
{business_intelligence_block}

---

## 6b. Industry Research — Data-Driven Insights

{industry_research_block}

---

## 7. iOS / iPhone Compatibility
{ios_skill_block}

---

## 8. Recommended Design System
{design_system_block}

---

## 8b. Placeholder Images (Pexels / Picsum)

{images_block}

---

## 8c. Hero Video (Pexels Video API)

{hero_video_block}

---

## 9. Stack, Motion System, and Build Instructions
{stack_block}

### Self-audit before delivering

| Check | Required |
|---|---|
| Phone number | `[BUSINESS PHONE]` — NEVER a 555 number or invented number |
| Heading font | NOT Inter / Geist / Poppins / DM Sans / Space Grotesk — named distinctive face from Contract |
| Subtext | No "Where X meets Y" — specific claim, number, or location |
| Headline | No "Unrivaled / World-class / Unleash" — specific and arguable |
| Hero | Full-bleed image or video with overlay — NEVER flat color behind text |
| Hero headline | `<h1 className="hero-heading">` PRESENT and LARGE (min text-6xl) — CTAs alone are not a hero |
| Hero height | `min-h-[100dvh]` — never `min-h-screen` |
| Hero animation | Vanilla word-splitter (NOT `gsap/SplitText`) + 5-element staggered timeline on mount |
| **GSAP SplitText** | **NEVER import `gsap/SplitText`** — it's a paid Club plugin and crashes on free GSAP. Use the `splitWords()` helper in Code Pattern 1. |
| **`next/image` refs** | **NEVER attach a `ref` directly to `<Image>`** — Next's Image component does not forward refs. Always wrap in a `<div ref={{...}}>` and animate the wrapper. |
| Navbar | Hides scroll-down, returns scroll-up, blur fill at 60px |
| Navbar initial paint | Synchronously set background in `useEffect` based on `window.scrollY` — never start transparent and let GSAP fill it later (flicker on load) |
| Images | `next/image` everywhere — never raw `<img>` |
| Services layout | Full-bleed vertical alternating sections — NEVER 3-column card grid, NEVER horizontal scroll |
| Stats | GSAP counting numbers — never static text |
| Social proof | Dark section, large single quote — never a carousel of small cards |
| Section images | Clip-path reveal on scroll (wrapper div, not on `<Image>`) |
| Video | `autoPlay muted loop playsInline` — always all four attributes |
| Hero video src | Use `/videos/hero.mp4` (local) when provided — Pexels CDN URLs only as fallback |
| CTAs | `href="tel:..."` for phone — zero dead `href="#"` links |
| Form | `onSubmit` handler with success state |
| Input font | Minimum `font-size: 16px` — prevents iOS zoom |
| Safe area | `env(safe-area-inset-*)` in globals.css |
| SSR safety | `normalizeScroll` + `ScrollTrigger.config` inside `useEffect` — NEVER at module level |
| FAQ accordion | `ScrollTrigger.refresh()` triggered by `transitionend` — NEVER a bare `setTimeout` |
| **Lenis config** | Only Lenis 1.1.x options: `duration`, `easing`, `smoothWheel`, `syncTouch`, `touchMultiplier`, `infinite`. `smoothTouch` and `overscroll` are REMOVED in 1.1.x. |
| Overscroll | Use CSS `overscroll-behavior-y: none` on `html, body` — not the Lenis option |
| reduced-motion | `prefers-reduced-motion` media query in globals.css |
| `.gitignore` | Present at project root with `node_modules/`, `.next/`, `.env*.local`, `.DS_Store`, `*.log` |
| Booking tool | Matches industry — Booksy ONLY for beauty/wellness |
| Testimonials | Real only or omitted — never fabricated |

---

## 10. Anti-Slop Audit
{anti_slop_block}

---

## 11. Output -- NO QUESTIONS, BUILD IMMEDIATELY

**Do not write a plan. Do not ask questions. Build now.**

Output every file the project needs. Follow the Stack Skill project structure.

Required files (paths are PROJECT-ROOT relative — match the Stack Skill's tsconfig
`"paths": { "@/*": ["./*"] }`. DO NOT prefix with `src/` — imports written as
`@/components/...` would not resolve if files lived under `src/`, and the build
would fail at compile time):

- `README.md`, `HANDOFF.md`, `TODO_ASSETS.md`, `STYLE_GUIDE.md`, `CLIENT_ANSWERS.md`
- `content/site.ts`, `content/sections.ts`, `content/services.ts`, `content/faqs.ts`, `content/testimonials.ts`
- `lib/motion.ts`, `components/motion/Reveal.tsx`, `components/motion/Parallax.tsx`, `components/motion/SplitText.tsx`, `components/motion/SmoothScroll.tsx`
- `config/brand.config.ts`, `config/motion.config.ts`
- `next.config.mjs` (NOT `.ts` — Next 14 does not support TypeScript config files)
- `tailwind.config.ts`, `postcss.config.js`, `tsconfig.json`, `package.json`, `.gitignore`

Every import statement uses the `@/` alias rooted at the project. Examples:
`import { Reveal } from "@/components/motion/Reveal"`,
`import { SITE_TITLE } from "@/content/site"`,
`import { cn } from "@/lib/utils"`.

Where contact info is missing: use `[BUSINESS PHONE]`, `[EMAIL]`, `[ADDRESS]`. Never invent.
"""




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
# LLM CLIENT (Anthropic; abstracted so Gemini drops in later)
# --------------------------------------------------------------------------

class LLMError(Exception):
    pass


# ---------- Gemini 3.1 Pro client (default) --------------------------------

class GeminiClient:
    """Wraps google-genai for Gemini 3.1 Pro (and any future Gemini model).
    Interface: generate(system, user, max_tokens, images) -> str -- same as AnthropicClient."""

    def __init__(self, api_key: str, model: str):
        if not _GOOGLE_OK:
            raise LLMError("google-genai package not installed. Run: pip install google-genai")
        self.client = _genai.Client(api_key=api_key)
        self.model = model
        self.provider = "gemini"

    def generate(self, system: str, user: str, max_tokens: int = 16000,
                 images: Optional[list[dict]] = None) -> str:
        try:
            config = _genai_types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=max_tokens,
                temperature=0.7,
            )
            # Multimodal content if images present, else plain text
            if images:
                import base64 as _b64
                parts: list = [user]
                for img in images:
                    raw = img.get("data", "")
                    if not raw:
                        continue
                    try:
                        img_bytes = _b64.b64decode(raw)
                    except Exception:
                        continue
                    parts.append(_genai_types.Part.from_bytes(
                        data=img_bytes,
                        mime_type=img.get("media_type", "image/png"),
                    ))
                contents = parts
            else:
                contents = user
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )
            return response.text
        except Exception as e:
            raise LLMError(f"Gemini API call failed: {e}")


# ---------- Anthropic Claude client (premium / second-opinion option) -------

class AnthropicClient:
    """Wraps anthropic for Claude Sonnet/Opus.
    Interface: generate(system, user, max_tokens, images) -> str -- same as GeminiClient."""

    def __init__(self, api_key: str, model: str):
        if not _ANTHROPIC_OK:
            raise LLMError("anthropic package not installed. Run: pip install anthropic")
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.provider = "anthropic"

    def generate(self, system: str, user: str, max_tokens: int = 16000,
                 images: Optional[list[dict]] = None) -> str:
        try:
            if images:
                # Multimodal content blocks — image first, then text
                content_blocks: list = []
                for img in images:
                    raw = img.get("data", "")
                    if not raw:
                        continue
                    content_blocks.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": img.get("media_type", "image/png"),
                            "data": raw,
                        },
                    })
                content_blocks.append({"type": "text", "text": user})
                messages = [{"role": "user", "content": content_blocks}]
            else:
                messages = [{"role": "user", "content": user}]
            # Streaming required for any request that could exceed 10 minutes —
            # our prompt + 32k max_tokens triggers Anthropic's safety check, so
            # we collect the stream into a single string and return as before.
            parts: list[str] = []
            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            ) as stream:
                for chunk in stream.text_stream:
                    parts.append(chunk)
            return "".join(parts)
        except Exception as e:
            raise LLMError(f"Anthropic API call failed: {e}")


# ---------- Provider selector -----------------------------------------------

_GEMINI_DEFAULT_MODEL    = "gemini-2.5-flash"
_ANTHROPIC_DEFAULT_MODEL = "claude-sonnet-4-6"


def get_llm_client() -> tuple[Optional[object], str]:
    """Return (client, reason). Client is None if unavailable; reason explains why.

    Provider priority:
        PEBBLE_PROVIDER=gemini     -> GeminiClient (default if key present)
        PEBBLE_PROVIDER=anthropic  -> AnthropicClient
        (unset)                    -> try Gemini first, fall back to Anthropic
    """
    provider = os.environ.get("PEBBLE_PROVIDER", "").strip().lower()

    # -- Explicit Anthropic request --
    if provider == "anthropic":
        if not _ANTHROPIC_OK:
            return None, "anthropic package not installed (run: pip install anthropic)"
        key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not key:
            return None, "ANTHROPIC_API_KEY not set (PEBBLE_PROVIDER=anthropic)"
        model = os.environ.get("PEBBLE_MODEL", _ANTHROPIC_DEFAULT_MODEL).strip() or _ANTHROPIC_DEFAULT_MODEL
        try:
            return AnthropicClient(api_key=key, model=model), "ok"
        except LLMError as e:
            return None, str(e)

    # -- Gemini (explicit or default) --
    gemini_key = os.environ.get("GOOGLE_API_KEY", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()
    if gemini_key and _GOOGLE_OK:
        model = os.environ.get("PEBBLE_MODEL", _GEMINI_DEFAULT_MODEL).strip() or _GEMINI_DEFAULT_MODEL
        try:
            return GeminiClient(api_key=gemini_key, model=model), "ok"
        except LLMError as e:
            return None, str(e)

    # -- Fall back to Anthropic if Gemini key isn't set --
    if provider != "gemini":
        if _ANTHROPIC_OK:
            key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
            if key:
                model = os.environ.get("PEBBLE_MODEL", _ANTHROPIC_DEFAULT_MODEL).strip() or _ANTHROPIC_DEFAULT_MODEL
                try:
                    return AnthropicClient(api_key=key, model=model), "ok"
                except LLMError as e:
                    return None, str(e)

    # -- Nothing configured --
    if not _GOOGLE_OK and not _ANTHROPIC_OK:
        return None, "no LLM package installed (run: pip install -r requirements.txt)"
    if not gemini_key:
        return None, "GOOGLE_API_KEY not set -- add it to .env (or set PEBBLE_PROVIDER=anthropic)"
    return None, "auto-build not configured"


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
