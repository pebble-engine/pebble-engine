"""Brand identity extraction from a URL.

The Phase-1 ingestion entry point. The user pastes `https://acme.co` instead
of writing a brief; this module turns that into a partial brief — business
name, industry guess, tone, palette, logo — that the v3 questionnaire can
pre-fill. The user corrects rather than creates.

Two-pass design:

    1. Deterministic scrape (stdlib only — no requests, no BeautifulSoup):
       fetch HTML with urllib, then regex out the bits that don't need
       interpretation: <title>, OG tags, meta description, h1, favicon,
       apple-touch-icon, and inline color values from <style>/<link>.

    2. LLM inference (single cheap call): hand the LLM the scraped text +
       a 4-KB HTML sample and ask it to infer industry, tone, hero copy
       suggestion, and a 5-color palette consistent with what was scraped.

The output shape maps directly onto the existing brief schema so the
v3 frontend can spread it into the questionnaire state without remapping.

Caching: results are persisted under `output/.brand_cache/<urlhash>.json`
with a 1-hour TTL. A second extraction of the same URL within an hour
returns the cached payload instantly — important during dev iteration and
when the user re-tries after editing the prefilled fields.

Failure mode: if any step fails (DNS, 5xx, parse error, LLM unavailable),
the function returns a partial result with `error` populated. The frontend
should fall back to the free-text path and surface a non-blocking notice.
This module NEVER raises — extraction must never block the user from
reaching the intake form.
"""
from __future__ import annotations

import base64
import hashlib
import html as html_module
import json
import re
import time
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from pebble.log import log


# ---- Paths --------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).parent.parent.resolve()
BRAND_CACHE_DIR = _PROJECT_ROOT / "output" / ".brand_cache"

CACHE_TTL_SECONDS = 60 * 60 * 24 * 7  # 1 week
# Phase 38e (2026-05-21) — bumped from 1h to 1w for matcher consistency.
# The LLM matcher in _match_dna is non-deterministic at provider-default
# temperature (~0.7); two extractions of the same URL within the cache
# window could pick different DNAs (Bon Appétit → swiss_magazine then
# postmodern_max in our live test). Brand identity rarely changes day-
# to-day, so a 1w TTL is safe AND eliminates ~95% of cache misses on
# URLs the user revisits across a build, refinement, or follow-up
# session. Users who genuinely want a re-pick can pass use_cache=false.

# How big a slice of HTML we send to the LLM. ~4 KB keeps the call cheap
# and inside the context budget even for the smallest Qwen model.
_LLM_HTML_BUDGET = 4096

# Browser-like User-Agent. Many sites 403 the default Python UA.
_USER_AGENT = (
    "Mozilla/5.0 (compatible; PebbleEngine/1.0; +https://pebbleapp.ai/bot)"
)

# Hard cap on fetched bytes — we never need more than this and refuse to
# read megabyte pages into memory.
_FETCH_BYTE_LIMIT = 512 * 1024  # 512 KB

_FETCH_TIMEOUT_SECONDS = 8.0


# ---- Public API ---------------------------------------------------------

def extract_brand(url: str, *, mode: str = "brand", use_cache: bool = True,
                  inspiration_images: "list[bytes] | None" = None) -> dict:
    """Extract a partial brief from a URL.

    Two modes:
      - "brand"   (default): the URL is the user's own business. Extract
                  business FACTS — name, tagline, industry, tone, palette,
                  logo. Pre-fills the questionnaire with what we found.
                  When inspiration_images are provided in this mode, they
                  are treated as the business's own assets (logo, photos of
                  their space, product shots) and are passed to the LLM as
                  additional visual evidence alongside the scraped HTML.
      - "inspire": the URL is a reference site the user admires. Extract
                  STYLE attributes only — palette, font hints, vibe keywords,
                  motion intensity, layout density — then match the result
                  to one of Pebble's 11 DNA cards so the build picks up the
                  inspired aesthetic. We do NOT borrow business name /
                  industry / tagline in this mode (the inspiration site is
                  about how the user's site should FEEL, not who they are).
                  When inspiration_images are provided in this mode, they
                  are treated as palette and layout cues — visual references
                  the user wants the generated site to evoke.

    Optional arg:
      inspiration_images: raw bytes of up to 5 images. Caller is responsible
        for MIME validation and size caps. Each image is base64-encoded and
        passed to the LLM as a vision message block. When None (default),
        the LLM call is text-only (existing behavior).

    Returns a dict with all keys always present (see _empty_result for the
    shape — every BrandExtractResult field is set in both modes; fields
    that don't apply to the selected mode are null / empty list / etc.):

        Common:
          url, ok, error, palette, logo_url, favicon_url, raw_text_sample,
          source, mode

        Brand-mode populated:
          business_name, tagline, industry, tone, hero_copy

        Inspire-mode populated:
          vibe_keywords, font_hints, motion_intensity, layout_density,
          matched_dna  ({id, label, feel, confidence} | None)

    Never raises. On error, returns an `ok: False` shell that the caller
    can still pass through to the frontend.
    """
    mode = mode if mode in ("brand", "inspire") else "brand"

    normalized = _normalize_url(url)
    if not normalized:
        return _empty_result(url, "Invalid URL. Provide a full https:// address.", mode=mode)

    # Cache key includes mode so a site that's been brand-extracted before
    # still gets a fresh inspire pass when the user toggles modes.
    cache_key = _cache_key(f"{mode}:{normalized}")
    if use_cache:
        cached = _load_cache(cache_key)
        if cached:
            cached["source"] = "cache"
            return cached

    try:
        html, final_url = _fetch_html(normalized)
    except _FetchError as e:
        return _empty_result(normalized, f"Couldn't reach the site: {e}", mode=mode)

    try:
        scraped = _scrape_html(html, final_url)
    except Exception as e:  # pragma: no cover — pure regex
        log.error("[brand_extract] scrape failed: %s", e)
        return _empty_result(normalized, "Couldn't parse the page.", mode=mode)

    # Convert raw bytes → [{"data": b64str, "media_type": "image/png"}] blocks
    # for the LLM vision layer. The caller already validated MIME + size.
    image_blocks: list[dict] = []
    if inspiration_images:
        for img_bytes in inspiration_images[:5]:
            image_blocks.append({
                "data": base64.b64encode(img_bytes).decode("ascii"),
                "media_type": "image/png",  # caller validated; PNG is the safe fallback
            })

    if mode == "inspire":
        style = _llm_infer_style(scraped, images=image_blocks if image_blocks else None)
        matched = _match_dna(scraped, style) if style else None
        result = {
            "url":              final_url,
            "ok":               True,
            "error":            None,
            "mode":             "inspire",
            # Brand-mode fields stay nulled — inspire URL is about FEEL,
            # not about who the user is.
            "business_name":    None,
            "tagline":          None,
            "industry":         None,
            "tone":             None,
            "hero_copy":        None,
            # Style-only fields (populated)
            "palette":          scraped["palette"] or style.get("palette") or [],
            "logo_url":         scraped["logo_url"],
            "favicon_url":      scraped["favicon_url"],
            "vibe_keywords":    style.get("vibe_keywords", []),
            "font_hints":       style.get("font_hints", []),
            "motion_intensity": style.get("motion_intensity"),
            "layout_density":   style.get("layout_density"),
            "matched_dna":      matched,
            "raw_text_sample":  scraped["text_sample"],
            "source":           "fresh",
        }
    else:
        inferred = _llm_infer(scraped, images=image_blocks if image_blocks else None)
        result = {
            "url":              final_url,
            "ok":               True,
            "error":            None,
            "mode":             "brand",
            "business_name":    scraped["business_name"] or inferred.get("business_name"),
            "tagline":          scraped["tagline"] or inferred.get("tagline"),
            "industry":         inferred.get("industry"),
            "tone":             inferred.get("tone"),
            "palette":          scraped["palette"] or inferred.get("palette") or [],
            "logo_url":         scraped["logo_url"],
            "favicon_url":      scraped["favicon_url"],
            "hero_copy":        scraped["hero_copy"] or inferred.get("hero_copy"),
            # Inspire-only fields nulled
            "vibe_keywords":    [],
            "font_hints":       [],
            "motion_intensity": None,
            "layout_density":   None,
            "matched_dna":      None,
            "raw_text_sample":  scraped["text_sample"],
            "source":           "fresh",
        }

    if use_cache:
        _save_cache(cache_key, result)
    return result


# ---- URL normalization + safety ----------------------------------------

def _normalize_url(raw: str) -> Optional[str]:
    """Trim whitespace, default to https://, validate scheme + host.

    Returns None for clearly-broken or unsafe URLs (file://, localhost,
    private IPs, etc.). We never fetch private network targets — extraction
    is a tool the user points at public sites.
    """
    if not raw or not isinstance(raw, str):
        return None
    raw = raw.strip()
    if not raw:
        return None

    # Allow bare domains: "acme.co" → "https://acme.co"
    if "://" not in raw:
        raw = "https://" + raw

    try:
        parsed = urlparse(raw)
    except Exception:
        return None

    if parsed.scheme not in ("http", "https"):
        return None
    if not parsed.netloc:
        return None

    host = parsed.hostname or ""
    if not host:
        return None

    # SSRF guards — refuse private network and loopback targets.
    lowered = host.lower()
    if lowered in {"localhost", "0.0.0.0", "::1", "127.0.0.1"}:
        return None
    if lowered.endswith(".local") or lowered.endswith(".internal"):
        return None
    # Common private ranges (heuristic — full RFC1918 check would need ipaddress).
    if lowered.startswith(("10.", "192.168.", "172.16.", "172.17.", "172.18.",
                           "172.19.", "172.20.", "172.21.", "172.22.",
                           "172.23.", "172.24.", "172.25.", "172.26.",
                           "172.27.", "172.28.", "172.29.", "172.30.",
                           "172.31.", "169.254.")):
        return None

    return raw


# ---- HTTP fetch ---------------------------------------------------------

class _FetchError(Exception):
    pass


def _fetch_html(url: str) -> tuple[str, str]:
    """Fetch the URL, return (html, final_url) after following redirects.

    Reads at most _FETCH_BYTE_LIMIT bytes. Decodes as UTF-8 with errors
    replaced; HTML extraction is regex-based so encoding edge cases don't
    crash us.
    """
    req = Request(url, headers={
        "User-Agent":      _USER_AGENT,
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urlopen(req, timeout=_FETCH_TIMEOUT_SECONDS) as resp:
            final_url = resp.geturl()
            data = resp.read(_FETCH_BYTE_LIMIT + 1)
    except HTTPError as e:
        raise _FetchError(f"HTTP {e.code}") from e
    except URLError as e:
        reason = getattr(e, "reason", str(e))
        raise _FetchError(str(reason)) from e
    except Exception as e:
        raise _FetchError(str(e)) from e

    if len(data) > _FETCH_BYTE_LIMIT:
        data = data[:_FETCH_BYTE_LIMIT]

    return data.decode("utf-8", errors="replace"), final_url


# ---- Deterministic HTML scrape -----------------------------------------

# Tight, forgiving regexes. We don't need a real parser — we need ~10
# specific things, and DIY regex is faster than pulling in BeautifulSoup
# for what's effectively `grep` over an HTML string.
_RX_TITLE        = re.compile(r"<title[^>]*>\s*(.*?)\s*</title>", re.IGNORECASE | re.DOTALL)
_RX_META_NAME    = re.compile(r"<meta\s+[^>]*name=[\"']([^\"']+)[\"'][^>]*content=[\"']([^\"']*)[\"']", re.IGNORECASE)
_RX_META_PROP    = re.compile(r"<meta\s+[^>]*property=[\"']([^\"']+)[\"'][^>]*content=[\"']([^\"']*)[\"']", re.IGNORECASE)
_RX_H1           = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
_RX_LINK_ICON    = re.compile(r"<link[^>]+rel=[\"']([^\"']+)[\"'][^>]*href=[\"']([^\"']+)[\"']", re.IGNORECASE)
_RX_STRIP_TAGS   = re.compile(r"<[^>]+>")
_RX_HEX_COLOR    = re.compile(r"#[0-9a-fA-F]{6}\b")
_RX_HEX_SHORT    = re.compile(r"#[0-9a-fA-F]{3}\b(?![0-9a-fA-F])")
_RX_INLINE_STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
_RX_WS           = re.compile(r"\s+")

# Colors to drop from "brand palette" candidates — they're almost always
# defaults, browser-reset values, or neutrals that don't carry signal.
_PALETTE_EXCLUDE_HEX = {
    "#000000", "#ffffff", "#fff", "#000",
    "#222222", "#333333", "#444444", "#555555",
    "#cccccc", "#dddddd", "#eeeeee", "#f5f5f5",
}


def _scrape_html(html: str, base_url: str) -> dict:
    """Extract structured signals from the raw HTML.

    Returns a dict with every key always present so the caller can spread
    it freely. Missing values are None or empty list / empty string.
    """
    title = _first_match(_RX_TITLE, html)

    # OG / Twitter / meta lookups → flat dict
    meta: dict[str, str] = {}
    for name, content in _RX_META_NAME.findall(html):
        meta.setdefault(name.lower(), content)
    for prop, content in _RX_META_PROP.findall(html):
        meta.setdefault(prop.lower(), content)

    # Business name: prefer OG site_name, then title, then domain.
    business_name = (
        meta.get("og:site_name")
        or _trim_title(title)
        or _domain_label(base_url)
    )

    # Tagline: OG description / meta description / twitter:description
    tagline = (
        meta.get("og:description")
        or meta.get("description")
        or meta.get("twitter:description")
        or None
    )
    tagline = _clean_text(tagline) if tagline else None

    # Hero copy: first non-empty h1, falling back to tagline
    hero_copy: Optional[str] = None
    for raw_h1 in _RX_H1.findall(html):
        cleaned = _clean_text(_RX_STRIP_TAGS.sub("", raw_h1))
        if cleaned and len(cleaned) >= 4:
            hero_copy = cleaned[:200]
            break
    if not hero_copy and tagline:
        hero_copy = tagline

    # Icons / logo candidates
    favicon_url: Optional[str] = None
    logo_url: Optional[str] = meta.get("og:image") or None
    if logo_url:
        logo_url = urljoin(base_url, logo_url)

    for rels, href in _RX_LINK_ICON.findall(html):
        rels_lower = rels.lower()
        if "icon" in rels_lower and not favicon_url:
            favicon_url = urljoin(base_url, href)
        if ("apple-touch-icon" in rels_lower or "mask-icon" in rels_lower) and not logo_url:
            logo_url = urljoin(base_url, href)
    if not favicon_url:
        favicon_url = urljoin(base_url, "/favicon.ico")

    # Palette: pull hex colors from <style> blocks + style="" attrs +
    # OG theme-color meta. Drop blacks/whites/grays. Return top 5 by
    # appearance order (deduplicated).
    palette = _extract_palette(html, theme_color=meta.get("theme-color"))

    # Body text sample for LLM context — strip tags, collapse whitespace,
    # take first ~500 chars.
    body_text = _RX_STRIP_TAGS.sub(" ", html)
    body_text = html_module.unescape(body_text)
    body_text = _RX_WS.sub(" ", body_text).strip()
    text_sample = body_text[:500]

    return {
        "business_name": _clean_text(business_name) if business_name else None,
        "tagline":       tagline,
        "hero_copy":     hero_copy,
        "favicon_url":   favicon_url,
        "logo_url":      logo_url,
        "palette":       palette,
        "text_sample":   text_sample,
    }


def _first_match(rx: re.Pattern, text: str) -> Optional[str]:
    m = rx.search(text)
    if not m:
        return None
    raw = m.group(1)
    return _clean_text(_RX_STRIP_TAGS.sub("", raw))


def _trim_title(title: Optional[str]) -> Optional[str]:
    """Trim common suffixes like ' | Acme Co' or ' - Acme'."""
    if not title:
        return None
    for sep in (" | ", " — ", " – ", " - ", " :: "):
        if sep in title:
            head, _, _tail = title.partition(sep)
            head = head.strip()
            if head:
                return head
    return title.strip()


def _domain_label(url: str) -> str:
    host = urlparse(url).hostname or ""
    host = host.lstrip("www.")
    return host.split(".")[0].title() if host else "Untitled"


def _clean_text(s: Optional[str]) -> str:
    if not s:
        return ""
    return html_module.unescape(_RX_WS.sub(" ", s)).strip()


def _extract_palette(html: str, *, theme_color: Optional[str]) -> list[str]:
    """Return up to 5 brand-color candidates as lowercased hex strings.

    Strategy: pool every hex color found in inline <style> blocks and
    style="" attrs, plus theme-color meta. Drop neutrals. Dedupe while
    preserving first-seen order. Take top 5.
    """
    candidates: list[str] = []

    if theme_color and theme_color.startswith("#"):
        candidates.append(theme_color)

    for style_block in _RX_INLINE_STYLE.findall(html):
        candidates.extend(_RX_HEX_COLOR.findall(style_block))
        candidates.extend(_expand_short(c) for c in _RX_HEX_SHORT.findall(style_block))

    # Style attributes outside <style> blocks (e.g. inline color="#...").
    candidates.extend(_RX_HEX_COLOR.findall(html))

    seen: set[str] = set()
    out: list[str] = []
    for c in candidates:
        norm = c.lower()
        if norm in _PALETTE_EXCLUDE_HEX:
            continue
        if norm in seen:
            continue
        seen.add(norm)
        out.append(norm)
        if len(out) >= 5:
            break
    return out


def _expand_short(hex3: str) -> str:
    """Expand `#abc` → `#aabbcc`."""
    h = hex3.lstrip("#")
    return "#" + "".join(c * 2 for c in h)


# ---- LLM inference layer -----------------------------------------------

_INFER_PROMPT = """You are analyzing a website to extract its brand identity.

The user pasted this URL into a website-builder intake form. We've already
scraped what we can deterministically:

  Business name (from title/OG): {business_name}
  Tagline (from meta description): {tagline}
  Hero copy (from h1): {hero_copy}
  Palette (from inline styles): {palette}
  Body text sample: {text_sample}

Your job: infer the missing pieces. Output a single JSON object with this
exact schema (no commentary, no markdown fences):

{{
  "business_name": "the brand name (correct if scrape was noisy)",
  "tagline": "one-line tagline (12 words max) — only suggest if missing",
  "industry": "industry key in snake_case (e.g. coffee_shop, family_law, web3_devtool)",
  "tone": "2-4 adjective tone (e.g. 'warm, professional, witty')",
  "hero_copy": "single short headline a website-builder could use as h1 (max 8 words)",
  "palette": ["#hex", "#hex", "#hex"]
}}

Rules:
- If the scrape already populated a field, refine or keep it — don't
  invent something different unless the scrape value is obvious noise.
- Industry should be specific (e.g. "wedding_photographer" not "creative").
- Palette: if the scrape returned 3+ colors, reuse them. If 0-2, suggest
  colors that fit the inferred industry. Always return exactly 3 hex
  strings (lowercase, 7 chars including #).
- Output JSON only. First character must be `{{`."""


def _llm_infer(scraped: dict, images: "list[dict] | None" = None) -> dict:
    """Call the configured LLM to infer industry/tone/palette.

    images: optional list of {"data": b64str, "media_type": str} dicts.
      In brand mode these are the business's own assets (logo, space photos).
      When provided, the LLM sees them alongside the scraped text signals.

    Returns {} on any failure — caller treats inference as optional.
    """
    try:
        from pebble.llm import get_llm_client
    except Exception:
        return {}

    try:
        # get_llm_client() returns (client, reason). Unpack — passing the
        # bare tuple downstream silently fails with "tuple has no attribute
        # 'generate'" and the LLM-inferred fields end up None even though
        # the call site thinks the call succeeded.
        client, _reason = get_llm_client()
    except Exception:
        return {}
    if client is None:
        return {}

    prompt = _INFER_PROMPT.format(
        business_name=scraped["business_name"] or "(unknown)",
        tagline=scraped["tagline"] or "(none)",
        hero_copy=scraped["hero_copy"] or "(none)",
        palette=", ".join(scraped["palette"]) or "(none)",
        text_sample=scraped["text_sample"][:_LLM_HTML_BUDGET] or "(no body text extracted)",
    )

    image_note = ""
    if images:
        image_note = (
            "\n\nThe user also uploaded images of their business (logo, photos of their "
            "space, product shots, signage). These are the business's own visual assets — "
            "treat them as authoritative brand evidence. Use any palette colors, logo style, "
            "or visual mood visible in the images to refine your inferences."
        )

    try:
        raw = client.generate(
            system="You analyze websites and output strict JSON describing their brand identity.",
            user=prompt + image_note,
            max_tokens=400,
            images=images or None,
        )
    except Exception as e:
        log.warning("[brand_extract] LLM call failed: %s", e)
        return {}

    return _parse_llm_json(raw)


# ---- Inspire-mode style extraction (Phase 38a) -------------------------

# Different prompt — we want STYLE vocabulary, not business facts. Tight
# constraints on vibe_keywords and font_hints because we feed them to the
# DNA matcher next and need consistent shape.
_STYLE_PROMPT = """You are analyzing a website as a VISUAL INSPIRATION REFERENCE — not
as the user's own business. The user wants Pebble to build something with
this site's AESTHETIC FEEL, not to clone its business identity.

Scraped signals (deterministic):
  Tagline-ish copy (meta description): {tagline}
  Hero copy (h1): {hero_copy}
  Palette (from inline styles): {palette}
  Body text sample: {text_sample}

Your job: describe this site's VISUAL STYLE in a vocabulary Pebble's design
system can consume. Output a single JSON object with this exact shape (no
commentary, no markdown fences):

{{
  "vibe_keywords": ["3-6 short adjective phrases like 'dark editorial', 'cinematic widescreen', 'soft botanical', 'industrial brutalist', 'late-night intimate'"],
  "font_hints": ["1-3 short type descriptors like 'serif display headings', 'geometric sans body', 'condensed grotesque', 'editorial italic'"],
  "motion_intensity": "minimal | moderate | high",
  "layout_density": "spacious | dense",
  "palette": ["#hex", "#hex", "#hex"]
}}

Rules:
- vibe_keywords: emotion + style + weight (e.g. "dark cinematic" not just "dark"). Lowercase.
- motion_intensity: "minimal" if static-feeling, "moderate" if scroll fades + simple
  parallax, "high" if scroll-driven Three.js or major reveal animations.
- layout_density: "spacious" = generous margins, lots of whitespace, editorial. "dense" = card grids, sidebars, info-rich.
- palette: prefer the scraped values if present (3-5 hex strings, 7 chars each, lowercase). If scrape gave 0-2 colors, fill in with colors that fit the vibe.
- DO NOT include business_name, tagline, industry, tone — this is a STYLE reference, not the user's business.
- Output JSON only. First character must be `{{`."""


def _llm_infer_style(scraped: dict, images: "list[dict] | None" = None) -> dict:
    """Inspire-mode counterpart to _llm_infer. Returns style vocabulary
    instead of business facts.

    images: optional list of {"data": b64str, "media_type": str} dicts.
      In inspire mode these are palette and layout cues — visual references
      the user wants the generated site to evoke. The LLM treats them as
      style signals rather than business facts.

    Returns {} on any failure — caller falls back to deterministic
    palette + a "minimal" motion intensity heuristic, but the matched_dna
    field will be None.
    """
    try:
        from pebble.llm import get_llm_client
    except Exception:
        return {}

    try:
        client, _reason = get_llm_client()  # tuple — see _llm_infer for context
    except Exception:
        return {}
    if client is None:
        return {}

    prompt = _STYLE_PROMPT.format(
        tagline=scraped["tagline"] or "(none)",
        hero_copy=scraped["hero_copy"] or "(none)",
        palette=", ".join(scraped["palette"]) or "(none)",
        text_sample=scraped["text_sample"][:_LLM_HTML_BUDGET] or "(no body text extracted)",
    )

    image_note = ""
    if images:
        image_note = (
            "\n\nThe user also uploaded reference images as palette and layout cues — "
            "screenshots, mood-board images, or visual references that capture the aesthetic "
            "feel they want. Let the visual mood, color usage, and layout density of these "
            "images inform your vibe_keywords, font_hints, motion_intensity, and palette."
        )

    try:
        raw = client.generate(
            system="You analyze websites and output strict JSON describing their visual style.",
            user=prompt + image_note,
            max_tokens=400,
            images=images or None,
        )
    except Exception as e:
        log.warning("[brand_extract] style LLM call failed: %s", e)
        return {}

    parsed = _parse_llm_json(raw)
    if not parsed:
        return {}

    # Normalize: enforce shape + clamp vocabularies
    motion = parsed.get("motion_intensity")
    if motion not in ("minimal", "moderate", "high"):
        motion = None
    density = parsed.get("layout_density")
    if density not in ("spacious", "dense"):
        density = None

    vibe = parsed.get("vibe_keywords")
    if not isinstance(vibe, list):
        vibe = []
    vibe = [str(v).strip().lower() for v in vibe if isinstance(v, (str, int))][:6]

    fonts = parsed.get("font_hints")
    if not isinstance(fonts, list):
        fonts = []
    fonts = [str(f).strip() for f in fonts if isinstance(f, (str, int))][:3]

    return {
        "vibe_keywords":    vibe,
        "font_hints":       fonts,
        "motion_intensity": motion,
        "layout_density":   density,
        "palette":          parsed.get("palette", []),
    }


# ---- Vibe → DNA matcher (Phase 38b) ------------------------------------
#
# Single cheap LLM call. Given the extracted style attrs + a compact
# description of each DNA card, returns the best-match dna_id + confidence
# + rationale. The build pipeline already supports `_design_dna_id` pinning
# so the caller just stamps it on the brief and the random pick is skipped.


def _build_dna_catalog() -> list[dict]:
    """Build a slim, prompt-friendly version of each DNA card.

    We only send the LLM the discriminating fields — label, feel, motion,
    palette posture, industry affinity — not the full 60-line cards. Keeps
    the prompt under 2K tokens.
    """
    from style_dna import DNA_CARDS
    catalog = []
    for c in DNA_CARDS:
        catalog.append({
            "id":               c["id"],
            "label":            c["label"],
            "feel":             c.get("feel", ""),
            "motion_intensity": c.get("motion_intensity", ""),
            "palette_posture":  c.get("palette_posture", ""),
            "industry_affinity": c.get("industry_affinity", [])[:6],
        })
    return catalog


_DNA_MATCH_PROMPT = """You match an extracted visual style to one of Pebble's design
system cards. Read the extracted style + the catalog, pick the SINGLE best
match, and return strict JSON.

Extracted style from the reference URL:
  Vibe keywords:    {vibe_keywords}
  Font hints:       {font_hints}
  Motion intensity: {motion_intensity}
  Layout density:   {layout_density}
  Palette:          {palette}
  Hero copy sample: {hero_copy}

Pebble's DNA catalog (pick exactly one id from this list):
{catalog}

Output ONLY this JSON (no commentary, no fences):

{{
  "id": "<one of the catalog ids>",
  "confidence": 0.0-1.0,
  "rationale": "one sentence explaining why this match (under 25 words)"
}}

Rules:
- "id" MUST be one of the catalog ids exactly — never invent.
- Confidence: 0.9+ = strong match (vibe + motion both align), 0.6-0.9 = good fit, 0.3-0.6 = closest-of-imperfect, <0.3 = essentially a guess (still pick one).
- Prefer cards whose `motion_intensity` matches the extracted motion_intensity. A "high" motion reference should NOT map to "swiss_magazine" (subtle motion only).
- Prefer cards whose `feel` overlaps with the extracted vibe_keywords.
- First character of output must be `{{`."""


def _match_dna(scraped: dict, style: dict) -> Optional[dict]:
    """Match the extracted style to a DNA card via one cheap LLM call.

    Returns {id, label, feel, confidence} on success, None on any failure.
    The caller treats this as optional — the build still works without a
    matched DNA (falls back to industry-affinity random pick).
    """
    if not style:
        return None
    try:
        from pebble.llm import get_llm_client
    except Exception:
        return None
    try:
        client, _reason = get_llm_client()  # tuple — see _llm_infer for context
    except Exception:
        return None
    if client is None:
        return None

    catalog = _build_dna_catalog()
    # Render catalog as a numbered text block — easier for the LLM than JSON.
    catalog_lines = []
    for c in catalog:
        catalog_lines.append(
            f"- id: {c['id']}\n"
            f"  label: {c['label']}\n"
            f"  feel: {c['feel']}\n"
            f"  motion: {c['motion_intensity']}\n"
            f"  palette: {c['palette_posture']}\n"
            f"  works for: {', '.join(c['industry_affinity']) or '(general)'}"
        )
    catalog_text = "\n".join(catalog_lines)

    prompt = _DNA_MATCH_PROMPT.format(
        vibe_keywords=", ".join(style.get("vibe_keywords", [])) or "(none)",
        font_hints=", ".join(style.get("font_hints", [])) or "(none)",
        motion_intensity=style.get("motion_intensity") or "(unknown)",
        layout_density=style.get("layout_density") or "(unknown)",
        palette=", ".join(scraped.get("palette", []) or style.get("palette", []) or []) or "(none)",
        hero_copy=scraped.get("hero_copy") or "(none)",
        catalog=catalog_text,
    )

    try:
        raw = client.generate(
            system="You match website visual styles to Pebble's design system cards. Output strict JSON.",
            user=prompt,
            max_tokens=200,
        )
    except Exception as e:
        log.warning("[brand_extract] DNA match LLM call failed: %s", e)
        return None

    parsed = _parse_llm_json(raw)
    if not parsed:
        return None

    chosen_id = parsed.get("id")
    if not isinstance(chosen_id, str):
        return None
    # Validate against the catalog — refuse invented ids.
    catalog_index = {c["id"]: c for c in catalog}
    card = catalog_index.get(chosen_id)
    if not card:
        log.warning("[brand_extract] DNA matcher returned invalid id: %r", chosen_id)
        return None

    conf_raw = parsed.get("confidence")
    try:
        confidence = float(conf_raw) if conf_raw is not None else 0.5
    except (TypeError, ValueError):
        confidence = 0.5
    confidence = max(0.0, min(1.0, confidence))

    return {
        "id":         card["id"],
        "label":      card["label"],
        "feel":       card["feel"],
        "confidence": confidence,
    }


def _parse_llm_json(raw: str) -> dict:
    """Robust JSON parse that tolerates leading prose / code fences."""
    if not raw:
        return {}
    # Strip markdown code fences if present.
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    # Find the outermost {...} block.
    start = text.find("{")
    end   = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {}
    try:
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    # Normalize palette → list of 7-char hex strings.
    if "palette" in data and isinstance(data["palette"], list):
        data["palette"] = [
            p.lower() if isinstance(p, str) and p.startswith("#") and len(p) == 7 else None
            for p in data["palette"]
        ]
        data["palette"] = [p for p in data["palette"] if p]
    return data


# ---- Cache --------------------------------------------------------------

def _cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def _cache_path(key: str) -> Path:
    BRAND_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return BRAND_CACHE_DIR / f"{key}.json"


def _load_cache(key: str) -> Optional[dict]:
    path = _cache_path(key)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    if "_cached_at" not in payload:
        return None
    if time.time() - payload["_cached_at"] > CACHE_TTL_SECONDS:
        return None
    payload.pop("_cached_at", None)
    return payload


def _save_cache(key: str, payload: dict) -> None:
    path = _cache_path(key)
    body = dict(payload)
    body["_cached_at"] = time.time()
    try:
        path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:  # pragma: no cover
        log.warning("[brand_extract] cache save failed: %s", e)


# ---- Empty / failure result --------------------------------------------

def _empty_result(url: str, error: str, *, mode: str = "brand") -> dict:
    """Return an `ok: False` shell with every BrandExtractResult key present.

    Keeping all keys present (just nulled) means the frontend can spread
    the result freely without TypeScript narrowing for failure paths.
    """
    return {
        "url":              url,
        "ok":               False,
        "error":            error,
        "mode":             mode if mode in ("brand", "inspire") else "brand",
        "business_name":    None,
        "tagline":          None,
        "industry":         None,
        "tone":             None,
        "palette":          [],
        "logo_url":         None,
        "favicon_url":      None,
        "hero_copy":        None,
        "vibe_keywords":    [],
        "font_hints":       [],
        "motion_intensity": None,
        "layout_density":   None,
        "matched_dna":      None,
        "raw_text_sample":  "",
        "source":           "fresh",
    }
