"""Unit tests for pebble.inspire — color/font extraction, palette
classification, vibe derivation, DNA matching, SSRF defenses.

The fetch path is monkeypatched away in every test that exercises
`extract_inspiration` so no test reaches the real network. SSRF tests
exercise `_resolve_safely` and `_fetch_url_safe` directly with crafted
inputs.
"""
from __future__ import annotations

import socket

import pytest

import pebble.inspire as inspire
from pebble.inspire import (
    InspirationExtract,
    _classify_palette,
    _derive_vibe,
    _extract_colors,
    _extract_fonts,
    _fetch_url_safe,
    _hex_brightness,
    _is_private_or_loopback,
    _normalize_hex,
    _resolve_safely,
    _suggest_dna,
    extract_inspiration,
)


# ---- Color helpers --------------------------------------------------------

def test_normalize_hex_expands_three_digit_form():
    assert _normalize_hex("#abc") == "#aabbcc"
    assert _normalize_hex("abc") == "#aabbcc"


def test_normalize_hex_lowercases_six_digit_form():
    assert _normalize_hex("#AABBCC") == "#aabbcc"
    assert _normalize_hex("#FaFaFa") == "#fafafa"


def test_normalize_hex_rejects_garbage():
    assert _normalize_hex("xyz") is None
    assert _normalize_hex("#zz") is None
    assert _normalize_hex("#fffff") is None  # 5 chars, neither 3 nor 6


def test_extract_colors_finds_hex_and_rgb():
    css = "color: #abc; background: rgb(255, 100, 50); border: 1px solid rgba(0,0,0,0.5);"
    out = _extract_colors(css)
    assert "#aabbcc" in out
    assert "#ff6432" in out
    assert "#000000" in out


def test_extract_colors_handles_empty_text():
    assert _extract_colors("") == []
    assert _extract_colors("no colors here") == []


def test_hex_brightness_known_values():
    # White ~ 1.0, black 0.0, mid-grey ~0.5
    assert _hex_brightness("#ffffff") == pytest.approx(1.0, abs=0.01)
    assert _hex_brightness("#000000") == pytest.approx(0.0, abs=0.01)
    assert 0.45 < _hex_brightness("#808080") < 0.55


# ---- Palette classification ----------------------------------------------

def test_classify_palette_picks_light_background_dark_primary():
    # A site with one dominant white bg, dark text, and a saturated accent.
    colors = ["#ffffff"] * 10 + ["#0a0a0a"] * 8 + ["#ff5a1f"] * 3
    palette = _classify_palette(colors)
    assert palette["background"] == "#ffffff"
    assert palette["primary"] == "#0a0a0a"
    assert palette["accent"] == "#ff5a1f"


def test_classify_palette_handles_dark_first_design():
    colors = ["#050505"] * 10 + ["#f5f5f5"] * 8 + ["#c4ff00"] * 3
    palette = _classify_palette(colors)
    assert palette["background"] == "#f5f5f5"
    assert palette["primary"] == "#050505"
    assert palette["accent"] == "#c4ff00"


def test_classify_palette_empty_colors_returns_blanks():
    out = _classify_palette([])
    assert out == {"primary": "", "accent": "", "background": "", "all": []}


def test_classify_palette_caps_all_colors_at_twelve():
    colors = [f"#0000{i:02x}" for i in range(20)]
    palette = _classify_palette(colors)
    assert len(palette["all"]) == 12


# ---- Font extraction ------------------------------------------------------

def test_extract_fonts_pulls_first_family_per_declaration():
    css = """
    body { font-family: "Inter", "Helvetica Neue", sans-serif; }
    h1 { font-family: 'Cormorant Garamond', serif; }
    code { font-family: monospace; }
    """
    out = _extract_fonts(css)
    assert "Inter" in out
    assert "Cormorant Garamond" in out
    assert "monospace" in out


def test_extract_fonts_strips_keyword_values():
    out = _extract_fonts("p { font-family: inherit; } a { font-family: Arial; }")
    assert "Arial" in out
    assert "inherit" not in out


# ---- Vibe derivation ------------------------------------------------------

def test_derive_vibe_marks_dark_when_background_dim():
    palette = {"background": "#050505", "all": ["#050505", "#fff", "#f00"]}
    fonts = {"display": "Tektur"}
    vibe = _derive_vibe(palette, fonts)
    assert vibe["is_dark"] is True
    assert "dark" in vibe["descriptors"]


def test_derive_vibe_marks_light_when_background_bright():
    palette = {"background": "#ffffff", "all": ["#fff", "#000", "#5e7a6e"]}
    fonts = {"display": "Cormorant Garamond"}
    vibe = _derive_vibe(palette, fonts)
    assert vibe["is_dark"] is False
    assert "light" in vibe["descriptors"]
    assert "serif" in vibe["descriptors"]


def test_derive_vibe_sees_mono_display_font():
    vibe = _derive_vibe(
        {"background": "#000", "all": ["#000", "#0f0"]},
        {"display": "IBM Plex Mono"},
    )
    assert "mono" in vibe["descriptors"]


def test_derive_vibe_marks_minimal_when_few_colors():
    vibe = _derive_vibe({"background": "#fff", "all": ["#fff", "#000"]}, {"display": ""})
    assert vibe["is_minimal"] is True
    assert "minimal" in vibe["descriptors"]


def test_derive_vibe_marks_maximal_when_many_colors():
    vibe = _derive_vibe(
        {"background": "#fff", "all": [f"#{i:06x}" for i in range(0, 11)]},
        {"display": ""},
    )
    assert "maximal" in vibe["descriptors"]


# ---- DNA matching ---------------------------------------------------------

def test_suggest_dna_returns_card_id_and_reason():
    """Light page + serif display should lean toward a serif-driven card
    like Swiss Magazine. We don't pin the exact id (DNA cards may be
    rebalanced), just that we get *some* match with a sensible reason."""
    palette = {"background": "#faf8f3", "all": ["#faf8f3", "#0e0e10", "#5e7a6e"]}
    typography = {"display": "Cormorant Garamond", "body": "Inter Tight"}
    vibe = _derive_vibe(palette, typography)
    suggested = _suggest_dna(palette, typography, vibe)
    assert suggested["id"]
    assert suggested["label"]
    assert suggested["score"] > 0
    assert "serif" in suggested["reason"] or "light" in suggested["reason"]


def test_suggest_dna_dark_palette_picks_dark_aesthetic():
    palette = {"background": "#050505", "all": ["#050505", "#f5f5f5", "#ff5a1f"]}
    typography = {"display": "Tektur", "body": "Geist"}
    vibe = _derive_vibe(palette, typography)
    suggested = _suggest_dna(palette, typography, vibe)
    # All current DNA cards are dark — allow any of the 11 remaining cards.
    assert suggested["id"] in {
        "cinematic_imax", "industrial_freight", "velvet_lounge", "tactile_y2k", "marina",
        "swiss_magazine", "architectural_spec", "neue_haas_minimal", "postmodern_max",
        "arthouse_folio", "garden_press",
    }


# ---- SSRF defenses --------------------------------------------------------

@pytest.mark.parametrize("ip", [
    "127.0.0.1", "127.0.0.5",
    "10.0.0.1", "10.255.255.255",
    "172.16.0.1", "172.31.255.255",
    "192.168.1.1",
    "169.254.169.254",          # AWS/GCP/Azure metadata IP
    "169.254.0.1",              # link-local generally
    "224.0.0.1",                # multicast
    "0.0.0.0",                  # unspecified
    "::1",                      # IPv6 loopback
    "fc00::1",                  # IPv6 ULA (private)
    "fe80::1",                  # IPv6 link-local
])
def test_is_private_or_loopback_blocks_dangerous_addresses(ip):
    assert _is_private_or_loopback(ip) is True


@pytest.mark.parametrize("ip", [
    "8.8.8.8", "1.1.1.1", "151.101.1.140",
    "2606:4700:4700::1111",     # Cloudflare DNS over IPv6
])
def test_is_private_or_loopback_passes_public_addresses(ip):
    assert _is_private_or_loopback(ip) is False


def test_is_private_or_loopback_treats_unparseable_as_blocked():
    assert _is_private_or_loopback("not-an-ip") is True
    assert _is_private_or_loopback("") is True


def test_resolve_safely_blocks_localhost_by_name():
    assert _resolve_safely("localhost") is None


def test_resolve_safely_blocks_when_dns_returns_private(monkeypatch):
    """DNS-rebinding scenario: hostname looks public but resolves to
    private IP. The check must reject it."""
    def fake_getaddrinfo(host, *_a, **_kw):
        return [(socket.AF_INET, None, None, "", ("10.0.0.1", 0))]
    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    assert _resolve_safely("attacker-controlled.example") is None


def test_resolve_safely_returns_ip_for_public_host(monkeypatch):
    """The 2026-05-15 SSRF hardening pass changed _resolve_safely to
    return (ip, family) so callers can pin the connection to the
    validated IP. Was Optional[str] before."""
    monkeypatch.setattr(
        socket, "getaddrinfo",
        lambda host, *_a, **_kw: [(socket.AF_INET, None, None, "", ("93.184.216.34", 0))],
    )
    result = _resolve_safely("example.com")
    assert result is not None
    ip, family = result
    assert ip == "93.184.216.34"
    assert family == socket.AF_INET


def test_resolve_safely_blocks_when_any_record_is_private(monkeypatch):
    """SSRF via multi-A: attacker returns benign IP first, private IP
    second. Old code (infos[0]-only) passed; new code rejects because
    it inspects every record. (NLM 2026-05-15 finding #3.)"""
    def multi(*_a, **_kw):
        return [
            (socket.AF_INET, None, None, "", ("8.8.8.8", 0)),
            (socket.AF_INET, None, None, "", ("169.254.169.254", 0)),  # AWS metadata
        ]
    monkeypatch.setattr(socket, "getaddrinfo", multi)
    assert _resolve_safely("multi-a.example") is None


def test_resolve_safely_blocks_ipv4_mapped_private_ipv6():
    """::ffff:10.0.0.1 maps to 10.0.0.1; ipaddress.is_private catches
    it. Smoke-test the full resolve path."""
    from pebble.url_fetch import _is_private_or_loopback
    assert _is_private_or_loopback("::ffff:10.0.0.1") is True
    assert _is_private_or_loopback("::ffff:169.254.169.254") is True


def test_resolve_safely_returns_none_on_resolution_failure(monkeypatch):
    def boom(*_a, **_kw):
        raise socket.gaierror("nx")
    monkeypatch.setattr(socket, "getaddrinfo", boom)
    assert _resolve_safely("nonexistent.example.invalid") is None


def test_fetch_url_safe_rejects_file_scheme():
    final, body, n, err = _fetch_url_safe("file:///etc/passwd")
    assert err is not None
    assert "scheme" in err.lower() or "private" in err.lower() or "host" in err.lower()


def test_fetch_url_safe_rejects_localhost():
    final, body, n, err = _fetch_url_safe("http://localhost:8080/admin")
    assert err is not None
    assert "private" in err or "blocked" in err


def test_fetch_url_safe_rejects_loopback_ip():
    final, body, n, err = _fetch_url_safe("http://127.0.0.1:9000")
    assert err is not None
    assert body == ""


def test_fetch_url_safe_rejects_metadata_ip():
    """The single most-targeted SSRF endpoint — AWS/GCP/Azure metadata."""
    final, body, n, err = _fetch_url_safe("http://169.254.169.254/latest/meta-data/")
    assert err is not None


def test_fetch_url_safe_rejects_empty_url():
    _, _, _, err = _fetch_url_safe("")
    assert err == "url is required"


def test_fetch_url_safe_rejects_redirect_to_private(monkeypatch):
    """A 30x bouncing us to an internal address must be caught BEFORE
    the engine connects. The 2026-05-15 hardening pass now follows
    redirects manually and re-runs _resolve_safely on each hop, instead
    of relying on urllib's auto-redirect (which would have already
    connected to the private target by the time we got the response).
    """
    import pebble.url_fetch as uf

    # First hop: example.com → 8.8.8.8 (passes), responds with 302 to
    # a host that resolves to a private IP.
    # Second hop: internal-evil.example → 10.0.0.5 → MUST be rejected
    # before we open a socket.
    def fake_resolve(host):
        if "evil" in host:
            return None  # internal-evil.example → blocked
        return ("8.8.8.8", socket.AF_INET)

    sent_calls: list[str] = []

    def fake_send(parsed, ip, family):
        sent_calls.append(parsed.hostname)
        # Pretend example.com returned a 302 to the evil host.
        return (302, {"location": "http://internal-evil.example/"}, b"", "")

    monkeypatch.setattr(uf, "_resolve_safely", fake_resolve)
    monkeypatch.setattr(uf, "_send_one_request", fake_send)

    final, body, n, err = uf.safe_fetch_html("https://example.com")
    assert err is not None
    assert "private" in err or "blocked" in err
    # We must have only opened a socket to example.com, NOT to the
    # evil redirect target.
    assert sent_calls == ["example.com"]


def test_fetch_url_safe_caps_redirect_chain(monkeypatch):
    """Endless 30x ping-pong should bail out, not loop forever."""
    import pebble.url_fetch as uf

    monkeypatch.setattr(uf, "_resolve_safely",
                        lambda host: ("8.8.8.8", socket.AF_INET))
    seq = iter([f"https://hop{i}.example/" for i in range(20)])

    def fake_send(parsed, ip, family):
        return (302, {"location": next(seq)}, b"", "")

    monkeypatch.setattr(uf, "_send_one_request", fake_send)
    _, _, _, err = uf.safe_fetch_html("https://start.example")
    assert err is not None
    assert "redirects" in err.lower() or "loop" in err.lower()


# ---- extract_inspiration end-to-end ---------------------------------------

def test_extract_inspiration_returns_error_on_fetch_failure(monkeypatch):
    monkeypatch.setattr(inspire, "_fetch_url_safe",
                        lambda url: (url, "", 0, "host resolves to a private or blocked address"))
    out = extract_inspiration("http://localhost/")
    assert isinstance(out, InspirationExtract)
    assert out.error is not None
    assert out.palette == {}


def test_extract_inspiration_pulls_palette_and_headline(monkeypatch):
    html = """
    <!doctype html>
    <html><head>
      <title>Sage Studio</title>
      <style>
        body { background-color: #faf8f3; color: #0e0e10; font-family: 'Cormorant Garamond', serif; }
        h1 { color: #5e7a6e; font-family: 'Cormorant Garamond', serif; }
        p { font-family: 'Inter Tight', sans-serif; }
      </style>
    </head>
    <body>
      <h1>Quiet authority for considered work.</h1>
      <p>We design with intent.</p>
    </body></html>
    """
    monkeypatch.setattr(inspire, "_fetch_url_safe",
                        lambda url: ("https://sage.example", html, len(html), None))
    out = extract_inspiration("https://sage.example")
    assert out.error is None
    assert out.title == "Sage Studio"
    assert out.headline.startswith("Quiet authority")
    assert out.palette["background"] == "#faf8f3"
    assert "#0e0e10" == out.palette["primary"]
    assert out.suggested_dna["id"]
    bp = out.to_brief_partial()
    assert "https://sage.example" in bp["_inspired_by"]
    assert bp["_inspire_dna_hint"]


def test_extract_inspiration_keeps_to_brief_partial_minimal(monkeypatch):
    """The partial brief MUST NOT carry business facts (name, type,
    phone). Those are migrate.py's job; conflating the two leads to
    inspire pre-filling a real-but-wrong business profile."""
    html = "<html><head><title>Acme Plumbing</title></head><body>" \
           "<h1>24/7 Service</h1></body></html>"
    monkeypatch.setattr(inspire, "_fetch_url_safe",
                        lambda url: ("https://acme.example", html, len(html), None))
    out = extract_inspiration("https://acme.example")
    bp = out.to_brief_partial()
    assert "business_name" not in bp
    assert "business_type" not in bp
    assert "phone" not in bp


def test_extract_inspiration_handles_parse_exception(monkeypatch):
    """A malformed page that crashes the parser must NOT crash the call."""
    monkeypatch.setattr(inspire, "_fetch_url_safe",
                        lambda url: ("https://example", "<html>", 6, None))

    class _Boom:
        def feed(self, _): raise RuntimeError("kaboom")
        def all_css_text(self): return ""

    monkeypatch.setattr(inspire, "_Extractor", lambda: _Boom())
    out = extract_inspiration("https://example")
    assert out.error is not None
    assert "parse error" in out.error
