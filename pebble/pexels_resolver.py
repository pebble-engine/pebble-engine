"""Pexels tag resolver.

After blocks_compiler runs, the generated page.tsx may contain image
queries in two forms:

1. Tagged:   src="[pexels: artisan sourdough bread]"
   The legacy format — the [pexels:...] tag is replaced with a real URL.

2. Plain-text query:   src="artisan sourdough bakery interior warm sunlight"
   What Sonnet actually writes when filling image slots (the picker prompt
   instructs it to produce search-ready query strings, not tagged values).
   Detected by the absence of https:// or / prefixes in the src value.

Both forms are resolved to a real Pexels URL (or Picsum fallback) so the
generated site never has broken images.

Designed to be called by build_v2 right after compile_site.

Failure mode: if Pexels returns no results for a query (very rare —
queries are descriptive), we fall back to a Picsum random placeholder
(always available, never 404s). That way the user always sees A site,
even if not the ideal one.
"""
from __future__ import annotations

import os
import re
from typing import Optional

import httpx

_TAG_RX = re.compile(r"\[pexels:\s*([^\]]+?)\s*\]")

# Matches src="<value>" where <value> does NOT look like a URL.
# A real URL starts with https://, http://, /, or ./ — anything else is
# treated as a plain-text Pexels search query written by Sonnet.
_PLAIN_SRC_RX = re.compile(r'src="([^"]+)"')
_URL_PREFIXES = ("https://", "http://", "/", "./", "../", "{")

_PEXELS_API = "https://api.pexels.com/v1/search"


def _is_url(value: str) -> bool:
    """Return True if value looks like a real URL, JSX expression, or [pexels:...] tag.

    Values that start with [pexels: are handled by the tag resolver path —
    exclude them from the plain-text path to avoid double-processing.
    """
    if value.startswith("[pexels:"):
        return True  # handled by the tag resolver, not the plain-text path
    return any(value.startswith(p) for p in _URL_PREFIXES)


def _extract_pexels_tags(source: str) -> list[str]:
    """Return unique [pexels:query] queries in source, preserving order."""
    seen = set()
    out = []
    for match in _TAG_RX.finditer(source):
        query = match.group(1).strip()
        if query not in seen:
            seen.add(query)
            out.append(query)
    return out


def _extract_plain_queries(source: str) -> list[str]:
    """Return unique plain-text src values that look like search queries."""
    seen = set()
    out = []
    for match in _PLAIN_SRC_RX.finditer(source):
        value = match.group(1).strip()
        if not _is_url(value) and value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _fetch_pexels_image_urls(query: str, n: int = 15) -> list[str]:
    """Hit the Pexels API for `query`, return up to `n` photo large URLs.

    Returns an empty list on API error, missing key, or no results. The
    caller is responsible for picking the best unused candidate from the list.
    """
    key = (os.environ.get("PEXELS_API_KEY") or "").strip()
    if not key:
        return []
    try:
        r = httpx.get(
            _PEXELS_API,
            params={"query": query, "per_page": n, "orientation": "landscape"},
            headers={"Authorization": key},
            timeout=10.0,
        )
        if r.status_code != 200:
            return []
        photos = r.json().get("photos") or []
        return [p["src"]["large"] for p in photos if p.get("src", {}).get("large")]
    except Exception:
        return []


def _fetch_pexels_image_url(query: str) -> Optional[str]:
    """Hit the Pexels API for `query`, return the first photo's large URL.
    Returns None on API error or no results (caller falls back to placeholder).

    Kept for backwards compatibility with existing callers and tests.
    """
    candidates = _fetch_pexels_image_urls(query, n=1)
    return candidates[0] if candidates else None


def _placeholder_url(query: str) -> str:
    """Deterministic Picsum URL keyed on the query string (so the same
    query always falls back to the same image — stable across rebuilds)."""
    # Picsum supports a seed for stability; abs(hash) avoids negatives
    seed = abs(hash(query)) % 10000
    return f"https://picsum.photos/seed/{seed}/1200/800"


def _resolve_query(query: str, used: set[str]) -> str:
    """Return the best unused Pexels URL for *query*, updating *used* in-place.

    Resolution order:
    1. Fetch up to 15 candidate URLs from Pexels.
    2. Return the first candidate not already in *used*.
    3. If every candidate is already used, fall back to the first candidate
       (a repeat is better than a placeholder).
    4. If no candidates at all, return a Picsum placeholder.
    """
    candidates = _fetch_pexels_image_urls(query)
    chosen: str
    if not candidates:
        chosen = _placeholder_url(query)
    else:
        # Pick the first candidate not yet claimed by another query.
        for url in candidates:
            if url not in used:
                chosen = url
                break
        else:
            # All candidates already used — prefer a photo repeat over picsum.
            chosen = candidates[0]
    used.add(chosen)
    return chosen


def resolve_pexels_tags(source: str, used: Optional[set] = None) -> str:
    """Scan source for image queries and swap each with a real image URL.

    Handles two patterns:
    - ``[pexels: query]`` tags in src attributes (legacy format)
    - Plain-text src values that look like search queries (what Sonnet
      writes when filling image slots directly)

    Each unique query is fetched once. Failed fetches fall back to a
    Picsum placeholder so the user never sees a broken site.

    Args:
        source: The source text (e.g. a .tsx file) to scan.
        used:   Optional shared set of already-claimed URLs. Pass the same
                set across multiple ``resolve_pexels_tags`` calls (e.g. for
                all section files in a build) to prevent the same photo from
                appearing in two different sections. When *None* a fresh local
                set is created so single-call behaviour still dedups within
                the source file.
    """
    if used is None:
        used = set()

    # Build a combined url_map for both formats.
    # Each query is resolved exactly once; a repeated query in the same source
    # maps to the same URL (consistent card grid behaviour).
    url_map: dict[str, str] = {}

    for q in _extract_pexels_tags(source):
        if q not in url_map:
            url_map[q] = _resolve_query(q, used)

    for q in _extract_plain_queries(source):
        if q not in url_map:
            url_map[q] = _resolve_query(q, used)

    if not url_map:
        return source

    # Replace [pexels:...] tags first
    def _replace_tag(match: re.Match) -> str:
        q = match.group(1).strip()
        return url_map.get(q, _placeholder_url(q))

    result = _TAG_RX.sub(_replace_tag, source)

    # Replace plain-text src="<query>" with src="<real URL>"
    def _replace_plain_src(match: re.Match) -> str:
        value = match.group(1).strip()
        if value in url_map:
            return f'src="{url_map[value]}"'
        return match.group(0)

    result = _PLAIN_SRC_RX.sub(_replace_plain_src, result)

    return result
