"""Figma file summary fetcher.

Pulls a lightweight name/colors/first-frames summary of a Figma file
that the user pastes a URL for in the quiz. The summary is fed to the
LLM as additional design context — never as the entire design system
(Figma files in customer hands are too inconsistent for that).

Extracted from pebble_engine.py to keep that module slim. The function
is unchanged from its original implementation. Both ``FIGMA_ACCESS_TOKEN``
in env AND a parseable Figma URL are required; missing either returns
None and the build pipeline silently skips the Figma-derived hints.
"""
from __future__ import annotations

import json
import logging
import os
import re
import urllib.error
import urllib.request
from typing import Optional


log = logging.getLogger("pebble")


# Matches both legacy ``figma.com/file/<id>/...`` and modern
# ``figma.com/design/<id>/...`` URL shapes. The id is the alphanumeric
# capture group; we ignore the slug/path that follows it.
_FIGMA_FILE_RE = re.compile(r"figma\.com/(?:file|design)/([A-Za-z0-9]+)/")


def figma_file_summary(figma_url: str) -> Optional[dict]:
    """Pull a lightweight summary of a Figma file (name, colors, first frames).

    Returns None unless both the URL is valid and ``FIGMA_ACCESS_TOKEN``
    is set. The summary is meant to be fed to the LLM as additional
    design context, not as a substitute for the engine's own design
    system.
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
        log.warning("Figma fetch failed: %s", e)
        return None
    summary = {
        "file_id":       file_id,
        "name":          data.get("name", ""),
        "last_modified": data.get("lastModified", ""),
        "thumbnail_url": data.get("thumbnailUrl", ""),
        "pages":         [p.get("name", "") for p in data.get("document", {}).get("children", [])][:10],
    }
    return summary


__all__ = [
    "figma_file_summary",
    "_FIGMA_FILE_RE",
]
