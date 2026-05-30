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


def _fetch_pexels_image_url(query: str) -> Optional[str]:
    """Hit the Pexels API for `query`, return the first photo's large URL.
    Returns None on API error or no results (caller falls back to placeholder)."""
    key = (os.environ.get("PEXELS_API_KEY") or "").strip()
    if not key:
        return None
    try:
        r = httpx.get(
            _PEXELS_API,
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            headers={"Authorization": key},
            timeout=10.0,
        )
        if r.status_code != 200:
            return None
        photos = r.json().get("photos") or []
        if not photos:
            return None
        return photos[0]["src"]["large"]
    except Exception:
        return None


def _placeholder_url(query: str) -> str:
    """Deterministic Picsum URL keyed on the query string (so the same
    query always falls back to the same image — stable across rebuilds)."""
    # Picsum supports a seed for stability; abs(hash) avoids negatives
    seed = abs(hash(query)) % 10000
    return f"https://picsum.photos/seed/{seed}/1200/800"


def resolve_pexels_tags(source: str) -> str:
    """Scan source for image queries and swap each with a real image URL.

    Handles two patterns:
    - ``[pexels: query]`` tags in src attributes (legacy format)
    - Plain-text src values that look like search queries (what Sonnet
      writes when filling image slots directly)

    Each unique query is fetched once. Failed fetches fall back to a
    Picsum placeholder so the user never sees a broken site.
    """
    # Build a combined url_map for both formats
    url_map: dict[str, str] = {}

    for q in _extract_pexels_tags(source):
        url_map[q] = _fetch_pexels_image_url(q) or _placeholder_url(q)

    for q in _extract_plain_queries(source):
        if q not in url_map:
            url_map[q] = _fetch_pexels_image_url(q) or _placeholder_url(q)

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
