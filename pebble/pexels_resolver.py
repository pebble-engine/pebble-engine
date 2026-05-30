"""Pexels tag resolver.

After blocks_compiler runs, the generated page.tsx contains string tags
like `[pexels: artisan sourdough bread]` in image src attributes —
that's how the Sonnet picker writes per-block Pexels queries. This
module scans the rendered source, calls the Pexels API once per
unique query, and substitutes real image URLs.

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
_PEXELS_API = "https://api.pexels.com/v1/search"


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
    """Scan source for [pexels:query] tags, swap each with a real image URL.

    Each unique query is fetched once. Failed fetches fall back to a
    Picsum placeholder so the user never sees a broken site.
    """
    queries = _extract_pexels_tags(source)
    url_map: dict[str, str] = {}
    for q in queries:
        url = _fetch_pexels_image_url(q) or _placeholder_url(q)
        url_map[q] = url

    def _replace(match: re.Match) -> str:
        q = match.group(1).strip()
        return url_map.get(q, _placeholder_url(q))

    return _TAG_RX.sub(_replace, source)
