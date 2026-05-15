"""Tests for the site-migration extractor.

Most tests feed HTML directly into the parser (no network) — only a
couple touch the fetch path, and they go through monkeypatch so no
real outbound request happens.
"""
from __future__ import annotations

from unittest.mock import patch

import pebble.migrate as migrate
from pebble.migrate import MigrationExtract, _Extractor


def _parse(html: str, url: str = "https://example.com/") -> MigrationExtract:
    p = _Extractor(base_url=url)
    p.feed(html)
    p.finalize()
    p.out.final_url = url
    return p.out


# ---- Title + meta extraction ----------------------------------------------

def test_extract_title_and_meta_description():
    html = """
    <!doctype html><html><head>
      <title>Wildflower Bakery — Brooklyn's freshest sourdough</title>
      <meta name="description" content="Hand-kneaded loaves daily in Park Slope.">
    </head><body><h1>Welcome</h1></body></html>
    """
    out = _parse(html)
    assert out.title.startswith("Wildflower Bakery")
    assert "Park Slope" in out.meta_description


def test_extract_og_overrides_meta():
    html = """
    <html><head>
      <title>Generic Title</title>
      <meta name="description" content="generic">
      <meta property="og:title" content="Wildflower Bakery">
      <meta property="og:description" content="Sourdough in Brooklyn.">
      <meta property="og:site_name" content="Wildflower">
    </head></html>
    """
    out = _parse(html)
    assert out.og_title == "Wildflower Bakery"
    assert out.og_description == "Sourdough in Brooklyn."
    # og:site_name should pre-fill the business name guess
    assert out.business_name_guess == "Wildflower"


# ---- Business name guess via title separator ------------------------------

def test_business_name_split_on_separator():
    html = "<html><head><title>The Crust & Crumb | Artisanal Bakery</title></head></html>"
    out = _parse(html)
    assert out.business_name_guess == "The Crust & Crumb"


def test_business_name_with_dash_em():
    html = "<html><head><title>Pebble Studio — Considered Websites</title></head></html>"
    out = _parse(html)
    assert out.business_name_guess == "Pebble Studio"


# ---- Industry inference ---------------------------------------------------

def test_industry_guess_from_title():
    html = "<html><head><title>Smith Plumbing Co.</title></head><body><h1>24/7 plumbing</h1></body></html>"
    out = _parse(html)
    assert out.business_type_guess == "plumbing"


def test_industry_guess_from_body_text():
    html = """
    <html><head><title>Smith Co.</title></head><body>
      <h1>Welcome</h1>
      <p>We are a real estate brokerage serving the Bay Area.</p>
    </body></html>
    """
    out = _parse(html)
    assert out.business_type_guess == "real_estate"


def test_industry_guess_empty_when_no_match():
    html = "<html><head><title>Random Page</title></head><body><p>nothing relevant</p></body></html>"
    out = _parse(html)
    assert out.business_type_guess == ""


# ---- Headings collected (h1-h3, deduped) ----------------------------------

def test_headings_deduped_and_capped():
    html = "<html><body>" + "<h1>Welcome</h1>" * 3 + "<h2>About</h2><h3>Services</h3></body></html>"
    out = _parse(html)
    # "Welcome" should only appear once
    assert out.headings.count("Welcome") == 1
    assert "About" in out.headings
    assert "Services" in out.headings


# ---- Nav links ------------------------------------------------------------

def test_nav_links_captured_only_inside_nav():
    html = """
    <html><body>
      <nav>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
      </nav>
      <a href="/random">Random elsewhere</a>
    </body></html>
    """
    out = _parse(html)
    assert "About" in out.nav_links
    assert "Contact" in out.nav_links
    assert "Random elsewhere" not in out.nav_links


# ---- Contact info ---------------------------------------------------------

def test_phone_extracted_from_text():
    html = "<html><body><p>Call us at (212) 555-7777 anytime.</p></body></html>"
    out = _parse(html)
    assert "555-7777" in out.phone


def test_email_extracted_from_mailto():
    html = '<html><body><a href="mailto:hello@bakery.com">Email us</a></body></html>'
    out = _parse(html)
    assert "hello@bakery.com" in out.emails


def test_email_dedup_and_cap():
    html = (
        "<html><body>"
        + "".join(f'<a href="mailto:user{i}@bakery.com">x</a>' for i in range(8))
        + "</body></html>"
    )
    out = _parse(html)
    assert len(out.emails) <= 5


# ---- Images ---------------------------------------------------------------

def test_image_count_and_hosts():
    html = """
    <html><body>
      <img src="https://images.pexels.com/photos/1.jpg">
      <img src="https://cdn.shopify.com/files/x.jpg">
      <img src="/local/relative.jpg">
    </body></html>
    """
    out = _parse(html)
    assert out.image_count == 3
    assert "images.pexels.com" in out.image_hosts
    assert "cdn.shopify.com" in out.image_hosts


# ---- Color hints ----------------------------------------------------------

def test_inline_color_hex_hints_collected():
    html = '<html><body><div style="background: #205661; color: #F7F3EC">x</div></body></html>'
    out = _parse(html)
    assert "#205661" in out.color_hints
    assert "#f7f3ec" in out.color_hints   # lowercased


# ---- Script/style content excluded from text body -------------------------

def test_script_and_style_text_excluded():
    html = """
    <html><head>
      <style>body { color: red; }</style>
      <script>var secret = 'do-not-leak';</script>
    </head><body>
      <p>Visible text.</p>
    </body></html>
    """
    out = _parse(html)
    assert "do-not-leak" not in out.text_sample
    assert "color: red" not in out.text_sample
    assert "Visible text." in out.text_sample


# ---- to_brief_partial mapping ---------------------------------------------

def test_to_brief_partial_assembles_extra_context():
    html = """
    <html><head>
      <title>Crust Bakery</title>
      <meta name="description" content="Sourdough in Brooklyn.">
    </head><body>
      <h1>Welcome to Crust</h1>
      <p>Phone (212) 555-0100</p>
      <a href="mailto:hi@crust.com">x</a>
    </body></html>
    """
    out = _parse(html)
    brief = out.to_brief_partial()
    assert brief["business_name"] == "Crust Bakery"
    assert brief["business_type"] == "bakery"
    ctx = brief["extra_context"]
    assert "Crust Bakery" in ctx
    assert "Sourdough in Brooklyn" in ctx
    assert "(212) 555-0100" in ctx
    assert "hi@crust.com" in ctx


# ---- Fetch path errors (no real network) ----------------------------------

def test_extract_from_url_returns_error_on_empty_url():
    out = migrate.extract_from_url("")
    assert out.error == "url is required"


def test_extract_from_url_returns_error_on_http_error():
    """Patch the fetch step to simulate a server error."""
    with patch.object(migrate, "_fetch_url", return_value=("https://example.com", "", 0, "HTTP 503")):
        out = migrate.extract_from_url("https://example.com")
    assert out.error == "HTTP 503"
    assert out.title == ""


def test_extract_from_url_succeeds_when_fetch_returns_html():
    html = "<html><head><title>Hi</title></head></html>"
    with patch.object(migrate, "_fetch_url", return_value=("https://example.com", html, len(html), None)):
        out = migrate.extract_from_url("https://example.com")
    assert out.error is None
    assert out.title == "Hi"
    assert out.raw_bytes == len(html)
