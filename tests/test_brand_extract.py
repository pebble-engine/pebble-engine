"""Brand-extract module tests (Phase 33a, 2026-05-21).

Covers:
- URL normalization + SSRF guards (no localhost / private IPs)
- Deterministic HTML scrape (title, OG tags, h1, favicon, palette)
- Title trimming heuristics ("Acme | Home" → "Acme")
- Palette extraction + neutral-color exclusion
- LLM JSON parser robustness (code fences, leading prose, malformed)
- Cache TTL behavior

Does NOT hit the network or any LLM — every test mocks the boundary.
This is the safety net: if extraction can't gracefully degrade when
DNS is down or the LLM is unavailable, the entire intake funnel breaks.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from pebble import brand_extract
from pebble.brand_extract import (
    _build_dna_catalog,
    _cache_key,
    _empty_result,
    _expand_short,
    _extract_palette,
    _llm_infer_style,
    _match_dna,
    _normalize_url,
    _parse_llm_json,
    _scrape_html,
    _trim_title,
    extract_brand,
)


# ------------------------------------------------------------------ #
# URL normalization                                                   #
# ------------------------------------------------------------------ #


class TestNormalizeUrl:
    def test_bare_domain_defaults_to_https(self):
        assert _normalize_url("acme.co") == "https://acme.co"

    def test_https_url_passes_through(self):
        assert _normalize_url("https://example.com/foo") == "https://example.com/foo"

    def test_http_url_passes_through(self):
        assert _normalize_url("http://example.com") == "http://example.com"

    def test_whitespace_is_trimmed(self):
        assert _normalize_url("  example.com  ") == "https://example.com"

    def test_empty_string_is_rejected(self):
        assert _normalize_url("") is None
        assert _normalize_url("   ") is None

    def test_none_is_rejected(self):
        assert _normalize_url(None) is None  # type: ignore[arg-type]

    def test_non_string_is_rejected(self):
        assert _normalize_url(123) is None  # type: ignore[arg-type]

    def test_file_scheme_is_rejected(self):
        assert _normalize_url("file:///etc/passwd") is None

    def test_ftp_scheme_is_rejected(self):
        assert _normalize_url("ftp://example.com") is None

    def test_localhost_is_rejected(self):
        assert _normalize_url("http://localhost") is None
        assert _normalize_url("http://127.0.0.1") is None
        assert _normalize_url("http://0.0.0.0") is None

    def test_private_ipv4_ranges_rejected(self):
        assert _normalize_url("http://10.0.0.1") is None
        assert _normalize_url("http://192.168.1.1") is None
        assert _normalize_url("http://172.16.0.1") is None
        assert _normalize_url("http://172.31.255.255") is None
        assert _normalize_url("http://169.254.0.1") is None  # link-local

    def test_local_internal_tlds_rejected(self):
        assert _normalize_url("http://myserver.local") is None
        assert _normalize_url("http://api.internal") is None


# ------------------------------------------------------------------ #
# Title trimming                                                      #
# ------------------------------------------------------------------ #


class TestTrimTitle:
    def test_pipe_separator(self):
        assert _trim_title("Acme | Home") == "Acme"

    def test_dash_separator(self):
        assert _trim_title("Acme - Home") == "Acme"

    def test_em_dash_separator(self):
        assert _trim_title("Acme — Home") == "Acme"

    def test_no_separator_returns_full(self):
        assert _trim_title("Acme Inc") == "Acme Inc"

    def test_none_returns_none(self):
        assert _trim_title(None) is None

    def test_empty_returns_none(self):
        assert _trim_title("") is None

    def test_leading_separator_returns_full(self):
        # Edge case: " | Acme" — head is empty, should fall through to .strip()
        result = _trim_title(" | Acme")
        # We return the original title rather than ""; current impl returns " | Acme".strip()
        assert result is not None


# ------------------------------------------------------------------ #
# Palette extraction                                                  #
# ------------------------------------------------------------------ #


class TestPaletteExtraction:
    def test_extracts_hex_from_style_block(self):
        html = """
        <html><head><style>
            body { background: #ff6b35; color: #2a4d69; }
            .accent { border-color: #c9d6df; }
        </style></head></html>
        """
        colors = _extract_palette(html, theme_color=None)
        assert "#ff6b35" in colors
        assert "#2a4d69" in colors
        assert "#c9d6df" in colors

    def test_excludes_neutral_colors(self):
        html = "<style>body { background: #ffffff; color: #000000; }</style>"
        colors = _extract_palette(html, theme_color=None)
        assert "#ffffff" not in colors
        assert "#000000" not in colors

    def test_theme_color_meta_included_first(self):
        html = "<style>body { color: #abc123; }</style>"
        colors = _extract_palette(html, theme_color="#5b2c6f")
        assert colors[0] == "#5b2c6f"

    def test_deduplicates_colors(self):
        html = "<style>a { color: #ff0000; } b { color: #ff0000; } c { color: #ff0000; }</style>"
        colors = _extract_palette(html, theme_color=None)
        assert colors.count("#ff0000") == 1

    def test_caps_at_five_colors(self):
        css = " ".join(f".c{i} {{ color: #{i:06x}; }}" for i in range(1, 20))
        html = f"<style>{css}</style>"
        colors = _extract_palette(html, theme_color=None)
        assert len(colors) <= 5

    def test_empty_html_returns_empty(self):
        assert _extract_palette("<html></html>", theme_color=None) == []


class TestExpandShort:
    def test_short_hex_expands_correctly(self):
        assert _expand_short("#abc") == "#aabbcc"
        assert _expand_short("#f00") == "#ff0000"
        assert _expand_short("#fff") == "#ffffff"


# ------------------------------------------------------------------ #
# Full scrape                                                         #
# ------------------------------------------------------------------ #


_SAMPLE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Brooklyn Bakery | Artisan bread & pastries</title>
    <meta name="description" content="Sourdough, croissants, and seasonal pies from our wood-fired oven in Park Slope.">
    <meta property="og:site_name" content="Brooklyn Bakery">
    <meta property="og:description" content="Sourdough, croissants, and seasonal pies.">
    <meta property="og:image" content="/images/og-cover.jpg">
    <meta name="theme-color" content="#c2410c">
    <link rel="icon" href="/favicon.ico">
    <link rel="apple-touch-icon" href="/apple-icon.png">
    <style>
        body { background: #fef3e2; color: #4a2c14; }
        .cta { background: #c2410c; }
    </style>
</head>
<body>
    <h1>Fresh-baked, every morning.</h1>
    <p>We've been baking sourdough in our wood-fired oven since opening.</p>
</body>
</html>
"""


class TestScrapeHtml:
    def test_extracts_business_name_from_og_site_name(self):
        result = _scrape_html(_SAMPLE_HTML, "https://brooklynbakery.com")
        assert result["business_name"] == "Brooklyn Bakery"

    def test_extracts_tagline_from_meta_description(self):
        result = _scrape_html(_SAMPLE_HTML, "https://brooklynbakery.com")
        assert "Sourdough" in result["tagline"]

    def test_extracts_h1_as_hero_copy(self):
        result = _scrape_html(_SAMPLE_HTML, "https://brooklynbakery.com")
        assert result["hero_copy"] == "Fresh-baked, every morning."

    def test_extracts_favicon(self):
        result = _scrape_html(_SAMPLE_HTML, "https://brooklynbakery.com")
        assert result["favicon_url"] == "https://brooklynbakery.com/favicon.ico"

    def test_extracts_og_image_as_logo(self):
        result = _scrape_html(_SAMPLE_HTML, "https://brooklynbakery.com")
        assert result["logo_url"] == "https://brooklynbakery.com/images/og-cover.jpg"

    def test_extracts_palette_with_theme_color_first(self):
        result = _scrape_html(_SAMPLE_HTML, "https://brooklynbakery.com")
        assert result["palette"][0] == "#c2410c"
        assert "#fef3e2" in result["palette"]

    def test_body_text_sample_is_clean(self):
        result = _scrape_html(_SAMPLE_HTML, "https://brooklynbakery.com")
        assert "<" not in result["text_sample"]
        assert "Fresh-baked" in result["text_sample"]

    def test_missing_og_falls_back_to_title(self):
        html = "<html><head><title>Acme Co | Home</title></head><body></body></html>"
        result = _scrape_html(html, "https://acme.co")
        assert result["business_name"] == "Acme Co"

    def test_missing_title_falls_back_to_domain(self):
        html = "<html><head></head><body></body></html>"
        result = _scrape_html(html, "https://acme.co")
        # Domain label is best-effort; should at least produce something non-empty
        assert result["business_name"]


# ------------------------------------------------------------------ #
# LLM JSON parser                                                     #
# ------------------------------------------------------------------ #


class TestParseLlmJson:
    def test_clean_json_parses(self):
        raw = '{"industry": "coffee_shop", "tone": "warm"}'
        assert _parse_llm_json(raw)["industry"] == "coffee_shop"

    def test_strips_markdown_code_fences(self):
        raw = '```json\n{"industry": "coffee_shop"}\n```'
        assert _parse_llm_json(raw)["industry"] == "coffee_shop"

    def test_strips_plain_code_fences(self):
        raw = '```\n{"industry": "coffee_shop"}\n```'
        assert _parse_llm_json(raw)["industry"] == "coffee_shop"

    def test_tolerates_leading_prose(self):
        raw = 'Sure, here you go:\n\n{"industry": "coffee_shop"}'
        assert _parse_llm_json(raw)["industry"] == "coffee_shop"

    def test_empty_returns_empty_dict(self):
        assert _parse_llm_json("") == {}
        assert _parse_llm_json("   ") == {}

    def test_malformed_returns_empty_dict(self):
        assert _parse_llm_json("not json at all") == {}
        assert _parse_llm_json("{broken json") == {}

    def test_normalizes_palette_to_lowercase_hex(self):
        raw = '{"palette": ["#FF6B35", "#2A4D69"]}'
        result = _parse_llm_json(raw)
        assert result["palette"] == ["#ff6b35", "#2a4d69"]

    def test_drops_malformed_palette_entries(self):
        raw = '{"palette": ["#ff0000", "not-a-color", "#f00", "#abcdef"]}'
        result = _parse_llm_json(raw)
        # "#f00" is 4 chars not 7 → dropped. "not-a-color" → dropped.
        assert "#ff0000" in result["palette"]
        assert "#abcdef" in result["palette"]
        assert "not-a-color" not in result["palette"]


# ------------------------------------------------------------------ #
# Empty / failure result shape                                        #
# ------------------------------------------------------------------ #


class TestEmptyResult:
    def test_has_all_keys(self):
        result = _empty_result("https://acme.co", "Network down")
        expected_keys = {
            "url", "ok", "error", "business_name", "tagline",
            "industry", "tone", "palette", "logo_url", "favicon_url",
            "hero_copy", "raw_text_sample", "source",
            # inspire-mode fields — always present (nulled in brand mode)
            "mode", "vibe_keywords", "font_hints", "motion_intensity",
            "layout_density", "matched_dna",
        }
        assert set(result.keys()) == expected_keys

    def test_ok_is_false(self):
        assert _empty_result("https://x.com", "fail")["ok"] is False

    def test_error_is_populated(self):
        assert _empty_result("https://x.com", "DNS error")["error"] == "DNS error"

    def test_palette_is_empty_list(self):
        assert _empty_result("https://x.com", "fail")["palette"] == []


# ------------------------------------------------------------------ #
# Full extract_brand flow (mocked network + LLM)                      #
# ------------------------------------------------------------------ #


class TestExtractBrandFlow:
    def test_invalid_url_returns_empty_with_error(self):
        result = extract_brand("not a url at all !!!", use_cache=False)
        # "not a url at all !!!" → has spaces, urlparse may still produce
        # something with empty netloc → rejected → empty result
        assert result["ok"] is False
        assert result["error"]

    def test_localhost_url_returns_empty(self):
        result = extract_brand("http://localhost:8000", use_cache=False)
        assert result["ok"] is False

    def test_fetch_error_returns_partial_with_error(self):
        with patch.object(brand_extract, "_fetch_html", side_effect=brand_extract._FetchError("DNS lookup failed")):
            result = extract_brand("https://acme.co", use_cache=False)
        assert result["ok"] is False
        assert "DNS lookup failed" in result["error"]
        assert result["url"] == "https://acme.co"

    def test_successful_scrape_without_llm(self):
        # Mock the fetch + the LLM (LLM returns nothing → no inference)
        with patch.object(brand_extract, "_fetch_html", return_value=(_SAMPLE_HTML, "https://brooklynbakery.com")):
            with patch.object(brand_extract, "_llm_infer", return_value={}):
                result = extract_brand("brooklynbakery.com", use_cache=False)
        assert result["ok"] is True
        assert result["business_name"] == "Brooklyn Bakery"
        assert result["palette"][0] == "#c2410c"
        assert result["hero_copy"] == "Fresh-baked, every morning."

    def test_llm_fills_missing_fields(self):
        # Scrape returns sparse data; LLM fills industry/tone/palette
        sparse_html = "<html><head><title>Acme</title></head><body></body></html>"
        with patch.object(brand_extract, "_fetch_html", return_value=(sparse_html, "https://acme.co")):
            with patch.object(brand_extract, "_llm_infer", return_value={
                "industry": "coffee_shop",
                "tone": "warm, professional",
                "palette": ["#c2410c", "#fef3e2", "#4a2c14"],
            }):
                result = extract_brand("acme.co", use_cache=False)
        assert result["industry"] == "coffee_shop"
        assert result["tone"] == "warm, professional"
        # Palette comes from LLM since scrape returned empty list
        assert result["palette"] == ["#c2410c", "#fef3e2", "#4a2c14"]


# ------------------------------------------------------------------ #
# Cache behavior                                                      #
# ------------------------------------------------------------------ #


class TestCache:
    def test_cache_key_is_stable_for_same_url(self):
        assert _cache_key("https://acme.co") == _cache_key("https://acme.co")

    def test_cache_key_differs_for_different_urls(self):
        assert _cache_key("https://acme.co") != _cache_key("https://other.co")

    def test_cache_hit_skips_network_and_llm(self, tmp_path, monkeypatch):
        monkeypatch.setattr(brand_extract, "BRAND_CACHE_DIR", tmp_path)
        # Seed the cache
        with patch.object(brand_extract, "_fetch_html", return_value=(_SAMPLE_HTML, "https://brooklynbakery.com")):
            with patch.object(brand_extract, "_llm_infer", return_value={}):
                first = extract_brand("brooklynbakery.com")
        # Second call should not touch the network
        with patch.object(brand_extract, "_fetch_html", side_effect=AssertionError("network was called")):
            second = extract_brand("brooklynbakery.com")
        assert second["business_name"] == first["business_name"]
        assert second["source"] == "cache"

    def test_expired_cache_refetches(self, tmp_path, monkeypatch):
        monkeypatch.setattr(brand_extract, "BRAND_CACHE_DIR", tmp_path)
        monkeypatch.setattr(brand_extract, "CACHE_TTL_SECONDS", 0)  # immediate expiry
        with patch.object(brand_extract, "_fetch_html", return_value=(_SAMPLE_HTML, "https://brooklynbakery.com")):
            with patch.object(brand_extract, "_llm_infer", return_value={}):
                extract_brand("brooklynbakery.com")
                time.sleep(0.01)  # ensure clock moves past TTL
                # Second call should refetch (cache expired)
                with patch.object(brand_extract, "_fetch_html", return_value=(_SAMPLE_HTML, "https://brooklynbakery.com")) as refetch:
                    result = extract_brand("brooklynbakery.com")
                    assert refetch.called
                    assert result["source"] == "fresh"

    def test_use_cache_false_always_refetches(self, tmp_path, monkeypatch):
        monkeypatch.setattr(brand_extract, "BRAND_CACHE_DIR", tmp_path)
        with patch.object(brand_extract, "_fetch_html", return_value=(_SAMPLE_HTML, "https://brooklynbakery.com")):
            with patch.object(brand_extract, "_llm_infer", return_value={}):
                extract_brand("brooklynbakery.com", use_cache=True)
                # Even though cache is now populated, use_cache=False bypasses it
                with patch.object(brand_extract, "_fetch_html", return_value=(_SAMPLE_HTML, "https://brooklynbakery.com")) as refetch:
                    result = extract_brand("brooklynbakery.com", use_cache=False)
                    assert refetch.called
                    assert result["source"] == "fresh"


# ------------------------------------------------------------------ #
# Inspire mode — extract_brand(mode="inspire")                        #
# ------------------------------------------------------------------ #

_FAKE_STYLE = {
    "vibe_keywords":    ["dark cinematic", "editorial", "moody"],
    "font_hints":       ["serif display headings", "geometric sans body"],
    "motion_intensity": "high",
    "layout_density":   "spacious",
    "palette":          ["#1a1a2e", "#e94560"],
}

_FAKE_MATCHED_DNA = {
    "id":         "cinematic_imax",
    "label":      "Cinematic IMAX",
    "feel":       "Widescreen drama, hero imagery, massive typography",
    "confidence": 0.87,
}


class TestInspireMode:
    def _make_inspire_result(self):
        """Helper: patch fetch + llm_infer_style + match_dna, run inspire extraction."""
        with patch.object(brand_extract, "_fetch_html", return_value=(_SAMPLE_HTML, "https://ref-site.com")):
            with patch.object(brand_extract, "_llm_infer_style", return_value=_FAKE_STYLE):
                with patch.object(brand_extract, "_match_dna", return_value=_FAKE_MATCHED_DNA):
                    return extract_brand("https://ref-site.com", mode="inspire", use_cache=False)

    def test_extract_brand_inspire_mode_returns_inspire_mode_in_response(self):
        result = self._make_inspire_result()
        assert result["mode"] == "inspire"

    def test_extract_brand_inspire_does_NOT_populate_business_fields(self):
        result = self._make_inspire_result()
        assert result["business_name"] is None
        assert result["tagline"] is None
        assert result["industry"] is None
        assert result["tone"] is None
        assert result["hero_copy"] is None

    def test_extract_brand_inspire_populates_style_fields(self):
        result = self._make_inspire_result()
        assert result["vibe_keywords"] == _FAKE_STYLE["vibe_keywords"]
        assert result["font_hints"] == _FAKE_STYLE["font_hints"]
        assert result["motion_intensity"] == "high"
        assert result["layout_density"] == "spacious"

    def test_extract_brand_inspire_attaches_matched_dna(self):
        result = self._make_inspire_result()
        dna = result["matched_dna"]
        assert isinstance(dna, dict)
        assert dna["id"] == "cinematic_imax"
        assert dna["label"]
        assert dna["feel"]
        assert "confidence" in dna

    def test_extract_brand_inspire_matched_dna_is_none_when_matcher_fails(self):
        """When _match_dna returns None, other style fields are still populated."""
        with patch.object(brand_extract, "_fetch_html", return_value=(_SAMPLE_HTML, "https://ref-site.com")):
            with patch.object(brand_extract, "_llm_infer_style", return_value=_FAKE_STYLE):
                with patch.object(brand_extract, "_match_dna", return_value=None):
                    result = extract_brand("https://ref-site.com", mode="inspire", use_cache=False)
        assert result["matched_dna"] is None
        assert result["vibe_keywords"] == _FAKE_STYLE["vibe_keywords"]
        assert result["ok"] is True

    def test_extract_brand_brand_mode_clears_inspire_fields(self):
        """In brand mode the inspire-only fields must all be empty/None."""
        with patch.object(brand_extract, "_fetch_html", return_value=(_SAMPLE_HTML, "https://brooklynbakery.com")):
            with patch.object(brand_extract, "_llm_infer", return_value={}):
                result = extract_brand("https://brooklynbakery.com", mode="brand", use_cache=False)
        assert result["vibe_keywords"] == []
        assert result["font_hints"] == []
        assert result["motion_intensity"] is None
        assert result["layout_density"] is None
        assert result["matched_dna"] is None

    def test_extract_brand_default_mode_is_brand(self):
        """Calling without mode arg must default to brand mode."""
        with patch.object(brand_extract, "_fetch_html", return_value=(_SAMPLE_HTML, "https://brooklynbakery.com")):
            with patch.object(brand_extract, "_llm_infer", return_value={}):
                result = extract_brand("https://brooklynbakery.com", use_cache=False)
        assert result["mode"] == "brand"

    def test_extract_brand_invalid_mode_falls_back_to_brand(self):
        """Unknown mode strings and non-string values silently become brand."""
        with patch.object(brand_extract, "_fetch_html", return_value=(_SAMPLE_HTML, "https://brooklynbakery.com")):
            with patch.object(brand_extract, "_llm_infer", return_value={}):
                result_str = extract_brand("https://brooklynbakery.com", mode="foo", use_cache=False)
        assert result_str["mode"] == "brand"

        # Non-string mode — _normalize silently maps it to "brand" as well
        with patch.object(brand_extract, "_fetch_html", return_value=(_SAMPLE_HTML, "https://brooklynbakery.com")):
            with patch.object(brand_extract, "_llm_infer", return_value={}):
                result_int = extract_brand("https://brooklynbakery.com", mode=42, use_cache=False)  # type: ignore[arg-type]
        assert result_int["mode"] == "brand"

    def test_extract_brand_inspire_cache_key_differs_from_brand(self, tmp_path, monkeypatch):
        """Same URL in brand vs inspire mode must produce two separate cache files."""
        monkeypatch.setattr(brand_extract, "BRAND_CACHE_DIR", tmp_path)

        with patch.object(brand_extract, "_fetch_html", return_value=(_SAMPLE_HTML, "https://ref-site.com")):
            with patch.object(brand_extract, "_llm_infer", return_value={}):
                extract_brand("https://ref-site.com", mode="brand", use_cache=True)
            with patch.object(brand_extract, "_llm_infer_style", return_value=_FAKE_STYLE):
                with patch.object(brand_extract, "_match_dna", return_value=_FAKE_MATCHED_DNA):
                    extract_brand("https://ref-site.com", mode="inspire", use_cache=True)

        cache_files = list(tmp_path.glob("*.json"))
        assert len(cache_files) == 2, f"Expected 2 cache files, got {len(cache_files)}: {cache_files}"

    def test_empty_result_inspire_mode_has_all_keys(self):
        """_empty_result in inspire mode must return the same key set as a success result."""
        result = _empty_result("https://ref-site.com", "fail", mode="inspire")
        # Verify mode is set correctly
        assert result["mode"] == "inspire"
        # All inspire-only keys must be present
        assert "vibe_keywords" in result
        assert "font_hints" in result
        assert "motion_intensity" in result
        assert "layout_density" in result
        assert "matched_dna" in result
        # Common keys
        assert "ok" in result
        assert result["ok"] is False
        assert "error" in result
        assert "palette" in result
        # Business keys present (nulled)
        assert "business_name" in result
        assert "industry" in result


# ------------------------------------------------------------------ #
# _llm_infer_style                                                    #
# ------------------------------------------------------------------ #


class TestLlmInferStyle:
    """Unit tests for _llm_infer_style — never makes real LLM calls."""

    _SCRAPE = {
        "tagline":    "Dark. Editorial. Fearless.",
        "hero_copy":  "Stories that matter.",
        "palette":    ["#1a1a2e", "#e94560"],
        "text_sample": "Welcome to the magazine.",
    }

    def test_llm_infer_style_returns_empty_dict_on_no_client(self):
        with patch("pebble.llm.get_llm_client", side_effect=RuntimeError("no client")):
            result = _llm_infer_style(self._SCRAPE)
        assert result == {}

    def test_llm_infer_style_returns_empty_dict_when_client_is_none(self):
        with patch("pebble.llm.get_llm_client", return_value=None):
            result = _llm_infer_style(self._SCRAPE)
        assert result == {}

    def test_llm_infer_style_returns_empty_dict_when_generate_raises(self):
        class _Raises:
            def generate(self, **kw):
                raise RuntimeError("oops")
        with patch("pebble.llm.get_llm_client", return_value=(_Raises(), "ok")):
            result = _llm_infer_style(self._SCRAPE)
        assert result == {}

    def test_llm_infer_style_clamps_motion_intensity_to_known_values(self):
        """Any motion value not in (minimal, moderate, high) becomes None."""
        raw_json = '{"vibe_keywords":["dark"],"font_hints":[],"motion_intensity":"extreme","layout_density":"spacious","palette":[]}'
        class _Client:
            def generate(self, **kw): return raw_json
        with patch("pebble.llm.get_llm_client", return_value=(_Client(), "ok")):
            result = _llm_infer_style(self._SCRAPE)
        assert result["motion_intensity"] is None

    def test_llm_infer_style_clamps_layout_density_to_known_values(self):
        """Any layout_density value not in (spacious, dense) becomes None."""
        raw_json = '{"vibe_keywords":["light"],"font_hints":[],"motion_intensity":"minimal","layout_density":"chaotic","palette":[]}'
        class _Client:
            def generate(self, **kw): return raw_json
        with patch("pebble.llm.get_llm_client", return_value=(_Client(), "ok")):
            result = _llm_infer_style(self._SCRAPE)
        assert result["layout_density"] is None

    def test_llm_infer_style_limits_vibe_keywords_to_6(self):
        """Even if the LLM returns 10 keywords, only the first 6 are kept."""
        kws = ["dark", "editorial", "cinematic", "bold", "moody", "night", "gritty", "raw", "intense", "deep"]
        raw_json = f'{{"vibe_keywords":{json.dumps(kws)},"font_hints":[],"motion_intensity":"high","layout_density":"dense","palette":[]}}'
        class _Client:
            def generate(self, **kw): return raw_json
        with patch("pebble.llm.get_llm_client", return_value=(_Client(), "ok")):
            result = _llm_infer_style(self._SCRAPE)
        assert len(result["vibe_keywords"]) == 6

    def test_llm_infer_style_limits_font_hints_to_3(self):
        """Even if the LLM returns 5 font hints, only the first 3 are kept."""
        fonts = ["serif display", "geometric sans", "condensed grotesque", "italic editorial", "mono code"]
        raw_json = f'{{"vibe_keywords":["a"],"font_hints":{json.dumps(fonts)},"motion_intensity":"minimal","layout_density":"spacious","palette":[]}}'
        class _Client:
            def generate(self, **kw): return raw_json
        with patch("pebble.llm.get_llm_client", return_value=(_Client(), "ok")):
            result = _llm_infer_style(self._SCRAPE)
        assert len(result["font_hints"]) == 3

    def test_llm_infer_style_lowercases_vibe_keywords(self):
        """Keywords are lowercased regardless of what the LLM returns."""
        raw_json = '{"vibe_keywords":["Dark Cinematic","EDITORIAL"],"font_hints":[],"motion_intensity":"high","layout_density":"spacious","palette":[]}'
        class _Client:
            def generate(self, **kw): return raw_json
        with patch("pebble.llm.get_llm_client", return_value=(_Client(), "ok")):
            result = _llm_infer_style(self._SCRAPE)
        assert "dark cinematic" in result["vibe_keywords"]
        assert "editorial" in result["vibe_keywords"]
        # None of the originals should appear
        assert "Dark Cinematic" not in result["vibe_keywords"]
        assert "EDITORIAL" not in result["vibe_keywords"]


# ------------------------------------------------------------------ #
# _match_dna                                                          #
# ------------------------------------------------------------------ #


class TestMatchDna:
    """Unit tests for _match_dna — never makes real LLM calls."""

    _SCRAPE = {
        "palette":   ["#1a1a2e", "#e94560"],
        "hero_copy": "Stories that matter.",
    }

    _STYLE = {
        "vibe_keywords":    ["dark cinematic", "editorial"],
        "font_hints":       ["serif display"],
        "motion_intensity": "high",
        "layout_density":   "spacious",
        "palette":          ["#1a1a2e"],
    }

    def test_match_dna_returns_none_when_style_is_empty(self):
        result = _match_dna(self._SCRAPE, {})
        assert result is None

    def test_match_dna_returns_none_when_client_is_none(self):
        with patch("pebble.llm.get_llm_client", return_value=None):
            result = _match_dna(self._SCRAPE, self._STYLE)
        assert result is None

    def test_match_dna_returns_none_when_llm_raises(self):
        class _Raises:
            def generate(self, **kw):
                raise RuntimeError("oops")
        with patch("pebble.llm.get_llm_client", return_value=(_Raises(), "ok")):
            result = _match_dna(self._SCRAPE, self._STYLE)
        assert result is None

    def test_match_dna_returns_none_for_invented_dna_id(self):
        """The matcher must refuse ids not present in the DNA catalog."""
        raw_json = '{"id":"made_up_card","confidence":0.9,"rationale":"looks right"}'
        class _Client:
            def generate(self, **kw): return raw_json
        with patch("pebble.llm.get_llm_client", return_value=(_Client(), "ok")):
            result = _match_dna(self._SCRAPE, self._STYLE)
        assert result is None

    def test_match_dna_clamps_confidence_above_1(self):
        """Confidence 1.5 must be clamped to 1.0."""
        raw_json = '{"id":"cinematic_imax","confidence":1.5,"rationale":"great match"}'
        class _Client:
            def generate(self, **kw): return raw_json
        with patch("pebble.llm.get_llm_client", return_value=(_Client(), "ok")):
            result = _match_dna(self._SCRAPE, self._STYLE)
        assert result is not None
        assert result["confidence"] == 1.0

    def test_match_dna_clamps_confidence_below_0(self):
        """Confidence -0.3 must be clamped to 0.0."""
        raw_json = '{"id":"cinematic_imax","confidence":-0.3,"rationale":"poor match"}'
        class _Client:
            def generate(self, **kw): return raw_json
        with patch("pebble.llm.get_llm_client", return_value=(_Client(), "ok")):
            result = _match_dna(self._SCRAPE, self._STYLE)
        assert result is not None
        assert result["confidence"] == 0.0

    def test_match_dna_defaults_confidence_to_0_5_when_missing(self):
        """If the LLM omits the confidence key, it defaults to 0.5."""
        raw_json = '{"id":"cinematic_imax","rationale":"fine match"}'
        class _Client:
            def generate(self, **kw): return raw_json
        with patch("pebble.llm.get_llm_client", return_value=(_Client(), "ok")):
            result = _match_dna(self._SCRAPE, self._STYLE)
        assert result is not None
        assert result["confidence"] == 0.5

    def test_match_dna_returns_correct_card_fields(self):
        """A valid match must return {id, label, feel, confidence}."""
        raw_json = '{"id":"cinematic_imax","confidence":0.87,"rationale":"strong match"}'
        class _Client:
            def generate(self, **kw): return raw_json
        with patch("pebble.llm.get_llm_client", return_value=(_Client(), "ok")):
            result = _match_dna(self._SCRAPE, self._STYLE)
        assert result is not None
        assert result["id"] == "cinematic_imax"
        assert result["label"]          # non-empty string
        assert result["feel"]           # non-empty string
        assert isinstance(result["confidence"], float)


# ------------------------------------------------------------------ #
# _build_dna_catalog                                                  #
# ------------------------------------------------------------------ #


class TestBuildDnaCatalog:
    def test_build_dna_catalog_returns_11_cards(self):
        catalog = _build_dna_catalog()
        assert len(catalog) == 11

    def test_build_dna_catalog_entries_have_required_keys(self):
        catalog = _build_dna_catalog()
        required = {"id", "label", "feel", "motion_intensity", "palette_posture", "industry_affinity"}
        for entry in catalog:
            missing = required - set(entry.keys())
            assert not missing, f"Card {entry.get('id')} missing keys: {missing}"

    def test_build_dna_catalog_contains_known_ids(self):
        ids = {c["id"] for c in _build_dna_catalog()}
        expected_subset = {
            "swiss_magazine", "cinematic_imax", "architectural_spec",
            "tactile_y2k", "neue_haas_minimal", "postmodern_max",
            "arthouse_folio", "industrial_freight", "garden_press",
            "velvet_lounge", "marina",
        }
        assert expected_subset == ids
