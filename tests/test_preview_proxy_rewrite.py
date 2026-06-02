"""Tests for the project-preview asset-URL rewrite.

Root cause (2026-06-01 live test): the workspace project preview proxies
to `next dev`, but the generated next.config has NO basePath, so the HTML
references root-absolute `/_next/static/...` (and `/about`, `/images/...`)
URLs. Served under `/preview/<slug>/`, the browser requests those at the
engine ROOT → 404 → completely unstyled render.

Fix: rewrite root-absolute href/src/action URLs in the proxied HTML to
include the `/preview/<slug>` prefix so they route back through
`_handle_preview` (which strips the prefix and forwards to next dev).
"""
import pebble_engine

_rewrite = pebble_engine.PebbleHandler._rewrite_root_absolute_urls


def test_prefixes_next_static_assets():
    html = '<link rel="stylesheet" href="/_next/static/css/app.css">'
    out = _rewrite(html, "/preview/mechanic")
    assert 'href="/preview/mechanic/_next/static/css/app.css"' in out


def test_prefixes_script_src():
    html = '<script src="/_next/static/chunks/main.js"></script>'
    out = _rewrite(html, "/preview/mechanic")
    assert 'src="/preview/mechanic/_next/static/chunks/main.js"' in out


def test_prefixes_plain_nav_and_images():
    html = '<a href="/about">About</a><img src="/images/hero/hero.jpg">'
    out = _rewrite(html, "/preview/mechanic")
    assert 'href="/preview/mechanic/about"' in out
    assert 'src="/preview/mechanic/images/hero/hero.jpg"' in out


def test_prefixes_form_action():
    html = '<form action="/contact" method="post">'
    out = _rewrite(html, "/preview/mechanic")
    assert 'action="/preview/mechanic/contact"' in out


def test_idempotent_already_prefixed():
    """Running twice (or on already-prefixed URLs) must not double-prefix."""
    html = '<link href="/preview/mechanic/_next/static/css/app.css">'
    out = _rewrite(html, "/preview/mechanic")
    assert out == html  # unchanged
    # And a fresh rewrite followed by a second pass is stable:
    once = _rewrite('<link href="/_next/x.css">', "/preview/mechanic")
    twice = _rewrite(once, "/preview/mechanic")
    assert once == twice


def test_leaves_absolute_and_protocol_relative_urls():
    html = (
        '<a href="https://example.com/x">x</a>'
        '<img src="//cdn.example.com/y.png">'
        '<a href="#section">jump</a>'
    )
    out = _rewrite(html, "/preview/mechanic")
    assert out == html  # nothing root-absolute → untouched


def test_handles_single_quotes_too():
    html = "<link href='/_next/static/css/app.css'>"
    out = _rewrite(html, "/preview/mechanic")
    assert "href='/preview/mechanic/_next/static/css/app.css'" in out


def test_prefixes_every_srcset_candidate():
    """next/image srcSet lists multiple URLs — ALL must be prefixed, else a
    browser picks an unprefixed candidate that 404s without falling back."""
    html = (
        '<img src="/_next/image?url=%2Fa.jpg&w=3840&q=75" '
        'srcSet="/_next/image?url=%2Fa.jpg&w=640&q=75 640w, '
        '/_next/image?url=%2Fa.jpg&w=1200&q=75 1200w">'
    )
    out = _rewrite(html, "/preview/mechanic")
    # The fallback src is prefixed:
    assert 'src="/preview/mechanic/_next/image?url=%2Fa.jpg&w=3840&q=75"' in out
    # AND both srcset candidates are prefixed (no bare "/_next" left):
    assert ' /_next/image' not in out and '"/_next/image' not in out
    assert out.count("/preview/mechanic/_next/image") == 3  # src + 2 srcset


def test_prefixes_image_preload_imagesrcset():
    """next/image with priority emits a <link rel=preload as=image
    imageSrcSet="..."> in <head>. That attribute (NOT srcset) must also be
    prefixed, else the high-res hero preload 404s at the engine root."""
    html = (
        '<link rel="preload" as="image" '
        'imageSrcSet="/_next/image?url=%2Fhero.jpg&w=640&q=75 640w, '
        '/_next/image?url=%2Fhero.jpg&w=1920&q=75 1920w" '
        'imageSizes="100vw">'
    )
    out = _rewrite(html, "/preview/mechanic")
    assert ' /_next/image' not in out and '"/_next/image' not in out
    assert out.count("/preview/mechanic/_next/image") == 2  # both candidates


def test_prefixes_lowercase_imagesrcset():
    """Browsers/SSR may emit the attribute lowercased (imagesrcset)."""
    html = (
        '<link rel=preload as=image '
        'imagesrcset="/_next/image?url=%2Fh.jpg&w=750&q=75 750w">'
    )
    out = _rewrite(html, "/preview/mechanic")
    assert "/preview/mechanic/_next/image?url=%2Fh.jpg&w=750&q=75" in out
    assert ' /_next/image' not in out
