"""Post-build image-URL validator + Pexels-backed replacement.

Phase 58c (2026-05-22). The LLM is instructed to use real Pexels/Unsplash
URLs in generated sites, but Qwen 3.6 Plus (and other LLMs) sometimes
hallucinate photo IDs that don't exist — those URLs return HTTP 404
when Next.js's image loader fetches them, leaving placeholder gray
boxes (or, in dark layouts, a fully-black hero).

This module is the safety net:

  1. Walk site_dir recursively for source files (.tsx/.ts/.jsx/.js/.mdx).
  2. Extract every Pexels/Unsplash image URL the LLM emitted.
  3. HEAD-request each in parallel (8 workers, 4s timeout).
  4. For 404s/timeouts/network errors: query the Pexels API with an
     industry-derived keyword and pick a real photo. Substitute the
     URL in the file. Preserves the query string so width/quality
     params survive.

Failure modes are silent — if Pexels API is unreachable, we log a
warning and leave the original URL in place (the visit will still
404 but the build process won't crash). The exact same behaviour
that shipped before this module, just with a chance of recovery
when the network cooperates.

Public entry point: ``validate_and_repair_images(site_dir, industry)``.
"""
from __future__ import annotations

import os
import re
import threading
import urllib.error
import urllib.request
import urllib.parse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable, Optional

from pebble.log import log


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Source file extensions we scan for image URLs.
_TEXT_EXTS = ("*.tsx", "*.ts", "*.jsx", "*.js", "*.mdx", "*.md")

# Image-URL patterns we care about. The capture group is the full URL.
# Pexels:   https://images.pexels.com/photos/<id>/pexels-photo-<id>.jpeg?...
#           https://images.pexels.com/photos/<id>.jpeg?...
# Unsplash: https://images.unsplash.com/photo-<hash>?...
_PEXELS_URL_RE = re.compile(
    r"https?://images\.pexels\.com/photos/[\w\-./]+\.(?:jpe?g|png|webp)(?:\?[^\s\"'`]*)?",
    re.IGNORECASE,
)
_UNSPLASH_URL_RE = re.compile(
    r"https?://images\.unsplash\.com/photo-[\w\-]+(?:\?[^\s\"'`]*)?",
    re.IGNORECASE,
)

# Network knobs.
_HEAD_TIMEOUT_S = 4.0
_PEXELS_TIMEOUT_S = 6.0
_PARALLEL_WORKERS = 8

# How many URLs to repair before we give up. Some builds emit dozens of
# images; repairing all of them sequentially could push us past the SSE
# timeout. Cap at 30; the rest stay as-is.
_MAX_REPAIRS = 30


# ---------------------------------------------------------------------------
# Industry → Pexels search-keyword mapping
# ---------------------------------------------------------------------------
#
# When an image 404s, we need a Pexels search keyword to fetch a real
# replacement. The industry key is usually snake_case ("coffee_shop",
# "wedding_photographer") — we map common ones to human-readable phrases
# Pexels search responds well to. Unknown industries fall back to the
# industry key itself (split on underscore).

_INDUSTRY_KEYWORDS: dict[str, str] = {
    "coffee_shop":           "coffee shop interior",
    "restaurant":            "restaurant food",
    "bakery":                "bakery bread",
    "auto_repair":           "auto repair shop",
    "yoga_studio":           "yoga studio",
    "florist":               "florist bouquet",
    "bookstore":             "bookstore shelves",
    "tattoo_studio":         "tattoo studio",
    "barber":                "barber shop",
    "salon":                 "hair salon",
    "spa":                   "spa wellness",
    "gym":                   "modern gym",
    "law_firm":              "law office",
    "consulting":            "business consulting",
    "real_estate":           "modern home",
    "construction":          "construction site",
    "wedding_photographer":  "wedding photography",
    "music_studio":          "music studio",
    "art_gallery":           "art gallery",
    "ceramics_studio":       "ceramics pottery",
}


def _keyword_for_industry(industry: Optional[str]) -> str:
    if not industry:
        return "modern business"
    key = industry.strip().lower()
    if key in _INDUSTRY_KEYWORDS:
        return _INDUSTRY_KEYWORDS[key]
    # Fall back to humanised version of the snake_case key.
    return key.replace("_", " ").strip() or "modern business"


# ---------------------------------------------------------------------------
# URL extraction
# ---------------------------------------------------------------------------

def _extract_image_urls_from_text(text: str) -> set[str]:
    """Return every Pexels / Unsplash image URL found in *text*."""
    urls: set[str] = set()
    urls.update(_PEXELS_URL_RE.findall(text))
    urls.update(_UNSPLASH_URL_RE.findall(text))
    return urls


def _iter_source_files(site_dir: Path) -> Iterable[Path]:
    for ext in _TEXT_EXTS:
        for fpath in site_dir.rglob(ext):
            parts = fpath.parts
            if "node_modules" in parts or ".next" in parts:
                continue
            yield fpath


# ---------------------------------------------------------------------------
# Network checks
# ---------------------------------------------------------------------------

def _url_ok(url: str) -> bool:
    """HEAD-check *url*. True if it returns 2xx. False on 4xx/5xx/timeout/err.

    Some image CDNs (notably Pexels) reject HEAD with 403/405; in that case
    we fall back to a Range-byte GET so we don't waste bandwidth but still
    confirm the URL resolves.
    """
    try:
        req = urllib.request.Request(url, method="HEAD",
            headers={"User-Agent": "PebbleEngine/1.0 (image-validator)"})
        with urllib.request.urlopen(req, timeout=_HEAD_TIMEOUT_S) as r:
            if 200 <= r.status < 300:
                return True
            if r.status in (403, 405):
                return _url_ok_via_range(url)
            return False
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):
            return _url_ok_via_range(url)
        return False
    except Exception:
        return False


def _url_ok_via_range(url: str) -> bool:
    try:
        req = urllib.request.Request(url, method="GET",
            headers={"User-Agent": "PebbleEngine/1.0", "Range": "bytes=0-127"})
        with urllib.request.urlopen(req, timeout=_HEAD_TIMEOUT_S) as r:
            return 200 <= r.status < 300
    except Exception:
        return False


def _check_urls_parallel(urls: Iterable[str]) -> dict[str, bool]:
    """Return {url: is_ok} for every url in *urls*, checked in parallel."""
    result: dict[str, bool] = {}
    urls_list = list(urls)
    if not urls_list:
        return result
    with ThreadPoolExecutor(max_workers=_PARALLEL_WORKERS) as pool:
        futures = {pool.submit(_url_ok, u): u for u in urls_list}
        for fut in as_completed(futures):
            url = futures[fut]
            try:
                result[url] = fut.result()
            except Exception:
                result[url] = False
    return result


# ---------------------------------------------------------------------------
# Pexels API
# ---------------------------------------------------------------------------

_pexels_cache: dict[str, list[str]] = {}
_pexels_cache_lock = threading.Lock()


def _fetch_pexels_urls_for_keyword(keyword: str, count: int = 12) -> list[str]:
    """Return a list of real Pexels image URLs for the keyword, via the
    Pexels API. Cached per-keyword for the lifetime of the process to
    keep multi-repair builds cheap.

    Returns empty list if PEXELS_API_KEY is missing or the request fails.
    """
    with _pexels_cache_lock:
        if keyword in _pexels_cache:
            return _pexels_cache[keyword]

    api_key = os.environ.get("PEXELS_API_KEY", "").strip()
    if not api_key:
        log.warning("[image-fallback] PEXELS_API_KEY not set — can't repair 404s")
        return []

    qs = urllib.parse.urlencode({"query": keyword, "per_page": count, "orientation": "landscape"})
    url = f"https://api.pexels.com/v1/search?{qs}"
    try:
        req = urllib.request.Request(url, headers={
            "Authorization": api_key,
            "User-Agent": "PebbleEngine/1.0",
        })
        with urllib.request.urlopen(req, timeout=_PEXELS_TIMEOUT_S) as r:
            if r.status != 200:
                log.warning("[image-fallback] pexels search returned %s for %r", r.status, keyword)
                return []
            payload = json.loads(r.read().decode("utf-8"))
    except Exception as exc:
        log.warning("[image-fallback] pexels search failed for %r: %s", keyword, exc)
        return []

    photos = payload.get("photos") or []
    # Prefer the "large" size; fall back to "original" or "medium" if missing.
    urls: list[str] = []
    for p in photos:
        src = p.get("src") or {}
        u = src.get("large2x") or src.get("large") or src.get("original") or src.get("medium")
        if isinstance(u, str) and u:
            urls.append(u)

    with _pexels_cache_lock:
        _pexels_cache[keyword] = urls
    return urls


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def validate_and_repair_images(site_dir: Path, industry: Optional[str]) -> dict:
    """Validate Pexels/Unsplash URLs in *site_dir*; replace 404s with real
    Pexels photos for the *industry* keyword.

    Returns a small report dict::

        {
            "scanned_files":  int,
            "urls_found":     int,
            "urls_broken":    int,
            "urls_repaired":  int,
            "urls_unrepaired": int,
            "files_modified": list[str],
        }

    Failure-tolerant: any exception during validation/repair is caught
    and logged. The caller can ignore the return value if they just want
    "do your best" semantics.
    """
    report = {
        "scanned_files":   0,
        "urls_found":      0,
        "urls_broken":     0,
        "urls_repaired":   0,
        "urls_unrepaired": 0,
        "files_modified":  [],
    }

    # 1. Walk + collect distinct image URLs across the whole site.
    file_contents: dict[Path, str] = {}
    all_urls: set[str] = set()
    for fpath in _iter_source_files(site_dir):
        try:
            text = fpath.read_text(encoding="utf-8")
        except Exception:
            continue
        report["scanned_files"] += 1
        urls = _extract_image_urls_from_text(text)
        if urls:
            file_contents[fpath] = text
            all_urls.update(urls)

    report["urls_found"] = len(all_urls)
    if not all_urls:
        return report

    # 2. Validate in parallel.
    status = _check_urls_parallel(all_urls)
    broken = [u for u, ok in status.items() if not ok]
    report["urls_broken"] = len(broken)
    if not broken:
        log.info("[image-fallback] all %d image URLs OK — nothing to repair", len(all_urls))
        return report

    log.warning("[image-fallback] %d of %d image URLs failed validation; attempting repair",
                len(broken), len(all_urls))

    # 3. Fetch replacement pool from Pexels.
    keyword = _keyword_for_industry(industry)
    pool = _fetch_pexels_urls_for_keyword(keyword, count=max(12, len(broken)))
    if not pool:
        log.warning("[image-fallback] no replacement pool available — leaving %d broken URLs in place", len(broken))
        report["urls_unrepaired"] = len(broken)
        return report

    # 4. Map each broken URL to a replacement (round-robin so different
    #    occurrences of the same broken URL stay in sync — same broken
    #    URL → same replacement). Cap at _MAX_REPAIRS.
    replacements: dict[str, str] = {}
    for i, bad_url in enumerate(broken[:_MAX_REPAIRS]):
        replacements[bad_url] = pool[i % len(pool)]

    # 5. Substitute in every file that contained any broken URL.
    for fpath, text in file_contents.items():
        new_text = text
        touched = False
        for bad_url, good_url in replacements.items():
            if bad_url in new_text:
                new_text = new_text.replace(bad_url, good_url)
                touched = True
        if touched:
            try:
                fpath.write_text(new_text, encoding="utf-8")
                report["files_modified"].append(str(fpath.relative_to(site_dir)))
            except Exception as exc:
                log.warning("[image-fallback] write failed for %s: %s", fpath, exc)

    report["urls_repaired"] = len(replacements)
    report["urls_unrepaired"] = max(0, len(broken) - _MAX_REPAIRS)

    log.info("[image-fallback] repaired %d URLs across %d files (industry=%r)",
             report["urls_repaired"], len(report["files_modified"]), keyword)
    return report
