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
    # 2026-05-24 — top-10 service industries added per funnel restructure.
    # These are the highest-volume signup industries that previously fell
    # to the generic "modern business" fallback.
    "plumber":               "plumber pipes",
    "plumbing":              "plumber pipes",
    "hvac":                  "hvac air conditioning",
    "electrician":           "electrician wiring",
    "landscaper":            "landscaping garden",
    "landscaping":           "landscaping garden",
    "dog_groomer":           "dog grooming",
    "dog_grooming":          "dog grooming",
    "dentist":               "dental office",
    "photographer":          "photographer camera",
    "pest_control":          "pest control",
    "lawn_care":             "lawn care mowing",
    "tree_service":          "tree service arborist",
    "carpet_cleaning":       "carpet cleaning",
    "house_cleaning":        "house cleaning",
    "pressure_washing":      "pressure washing",
    "solar_installer":       "solar panels installation",
    "junk_removal":          "junk removal truck",
    "moving_company":        "moving company truck",
    "home_inspection":       "home inspection inspector",
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
# Multi-source image providers (2026-05-24 reliability upgrade)
#
# Pre-2026-05-24 this module only knew how to fetch from Pexels. When
# Pexels had an outage (which happened twice in the same week — Marc
# flagged 2 generations shipped without images) the whole repair path
# silently fell back to "leave broken URLs in place." Disaster.
#
# Now we fan out to THREE sources in parallel with a shared budget:
#   1. Pixabay  — 6,000 req/hr free, no attribution required, primary
#   2. Pexels   — 200 req/hr free, attribution requested, secondary
#   3. Unsplash — 50/hr demo / 5,000/hr prod, attribution required, tertiary
#
# Race-to-first-success: whichever returns a non-empty result first wins.
# Failures from one source never block the others. If all three fail
# (no keys configured, or all three outages at once), we return [] and
# the caller leaves the original URL in place — same fail-soft behaviour
# as before, but the probability of three simultaneous outages is
# effectively zero.
#
# Per-keyword cache shared across providers so a successful Pixabay
# result for "plumber" won't trigger redundant Pexels/Unsplash calls
# on subsequent broken-URL repairs in the same build.
# ---------------------------------------------------------------------------

_pool_cache: dict[str, list[str]] = {}
_pool_cache_lock = threading.Lock()


def _fetch_pexels_urls_for_keyword(keyword: str, count: int = 12) -> list[str]:
    """Pexels API client. Returns [] on any failure (missing key, 4xx, timeout)."""
    api_key = os.environ.get("PEXELS_API_KEY", "").strip()
    if not api_key:
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
                return []
            payload = json.loads(r.read().decode("utf-8"))
    except Exception as exc:
        log.warning("[image-fallback] pexels failed for %r: %s", keyword, exc)
        return []
    photos = payload.get("photos") or []
    urls: list[str] = []
    for p in photos:
        src = p.get("src") or {}
        u = src.get("large2x") or src.get("large") or src.get("original") or src.get("medium")
        if isinstance(u, str) and u:
            urls.append(u)
    return urls


def _fetch_pixabay_urls_for_keyword(keyword: str, count: int = 12) -> list[str]:
    """Pixabay API client. Returns [] on any failure.

    Pixabay returns `webformatURL` (~640px) and `largeImageURL` (1280px+);
    we prefer largeImageURL for hero placement quality. Free tier: 6,000
    req/hr, no attribution required for our use.
    """
    api_key = os.environ.get("PIXABAY_API_KEY", "").strip()
    if not api_key:
        return []
    qs = urllib.parse.urlencode({
        "key":         api_key,
        "q":           keyword,
        "per_page":    max(3, min(count, 200)),  # Pixabay min 3, max 200
        "orientation": "horizontal",
        "image_type":  "photo",
        "safesearch":  "true",
    })
    url = f"https://pixabay.com/api/?{qs}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PebbleEngine/1.0"})
        with urllib.request.urlopen(req, timeout=_PEXELS_TIMEOUT_S) as r:
            if r.status != 200:
                return []
            payload = json.loads(r.read().decode("utf-8"))
    except Exception as exc:
        log.warning("[image-fallback] pixabay failed for %r: %s", keyword, exc)
        return []
    hits = payload.get("hits") or []
    urls: list[str] = []
    for h in hits:
        u = h.get("largeImageURL") or h.get("webformatURL")
        if isinstance(u, str) and u:
            urls.append(u)
    return urls


def _fetch_unsplash_urls_for_keyword(keyword: str, count: int = 12) -> list[str]:
    """Unsplash API client. Returns [] on any failure.

    Demo tier: 50 req/hr. Production tier (after free approval): 5,000/hr.
    Attribution requested but not enforced. We pull the `regular` size
    (~1080px) which is plenty for hero placement.
    """
    access_key = os.environ.get("UNSPLASH_ACCESS_KEY", "").strip()
    if not access_key:
        return []
    qs = urllib.parse.urlencode({
        "query":       keyword,
        "per_page":    max(1, min(count, 30)),  # Unsplash max 30
        "orientation": "landscape",
        "content_filter": "high",
    })
    url = f"https://api.unsplash.com/search/photos?{qs}"
    try:
        req = urllib.request.Request(url, headers={
            "Authorization": f"Client-ID {access_key}",
            "Accept-Version": "v1",
            "User-Agent": "PebbleEngine/1.0",
        })
        with urllib.request.urlopen(req, timeout=_PEXELS_TIMEOUT_S) as r:
            if r.status != 200:
                return []
            payload = json.loads(r.read().decode("utf-8"))
    except Exception as exc:
        log.warning("[image-fallback] unsplash failed for %r: %s", keyword, exc)
        return []
    results = payload.get("results") or []
    urls: list[str] = []
    for p in results:
        urls_obj = p.get("urls") or {}
        u = urls_obj.get("regular") or urls_obj.get("full") or urls_obj.get("small")
        if isinstance(u, str) and u:
            urls.append(u)
    return urls


# Source order: Pixabay first because it's the most generous free tier
# and the most reliable in our recent outages. Pexels second (current
# primary, but rate-limited). Unsplash third (highest quality but
# tightest free tier).
#
# Stored as (name, function_attr_name) instead of (name, function_ref) so
# that test code can monkeypatch the providers via patch.object(ifb, ...)
# and have the patches actually take effect inside _fetch_replacement_pool.
# A direct reference would be captured at import time and survive patching.
_PROVIDER_NAMES = (
    ("pixabay",  "_fetch_pixabay_urls_for_keyword"),
    ("pexels",   "_fetch_pexels_urls_for_keyword"),
    ("unsplash", "_fetch_unsplash_urls_for_keyword"),
)


def _fetch_replacement_pool(keyword: str, count: int = 12) -> list[str]:
    """Fan out across all configured image providers in parallel, return
    the first non-empty result. Per-keyword cached so subsequent
    repairs in the same build don't re-hit the network.

    If every provider returns empty (no keys configured, or all three
    outages at once), returns []. Caller treats this as "leave URL in
    place" — same fail-soft semantics as the pre-2026-05-24 module.
    """
    with _pool_cache_lock:
        if keyword in _pool_cache:
            return _pool_cache[keyword]

    # Resolve provider callables at call time (NOT import time) so that
    # monkeypatch.setattr(ifb, "_fetch_pixabay_urls_for_keyword", ...)
    # in tests actually reroutes the call.
    import sys as _sys
    _mod = _sys.modules[__name__]
    providers = [(name, getattr(_mod, attr)) for (name, attr) in _PROVIDER_NAMES]

    # All three providers run concurrently. as_completed yields whichever
    # finishes first — if it returned a non-empty list, we take it and
    # cancel the rest. This minimizes latency: one slow provider can't
    # block a fast one.
    pool: list[str] = []
    winning_source = "none"
    with ThreadPoolExecutor(max_workers=len(providers)) as ex:
        futures = {ex.submit(fn, keyword, count): name for (name, fn) in providers}
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                urls = fut.result(timeout=_PEXELS_TIMEOUT_S + 1)
            except Exception as exc:
                log.warning("[image-fallback] %s provider raised: %s", name, exc)
                urls = []
            if urls:
                pool = urls
                winning_source = name
                # Cancel the still-running providers — we have what we need.
                for other_fut in futures:
                    if other_fut is not fut:
                        other_fut.cancel()
                break

    log.info("[image-fallback] pool for %r from %s: %d urls", keyword, winning_source, len(pool))
    with _pool_cache_lock:
        _pool_cache[keyword] = pool
    return pool


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

    # 3. Fetch replacement pool. Fans out to Pixabay + Pexels + Unsplash
    #    in parallel; whichever returns first wins. See _fetch_replacement_pool.
    keyword = _keyword_for_industry(industry)
    pool = _fetch_replacement_pool(keyword, count=max(12, len(broken)))
    if not pool:
        log.warning("[image-fallback] all 3 image providers returned empty — leaving %d broken URLs in place", len(broken))
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
