# tests/test_preview_forward_path.py
from pebble.server.preview_paths import preview_forward_path


def test_preserves_next_image_query():
    raw = "/preview/foo/_next/image?url=https%3A%2F%2Fx.jpg&w=1920&q=75"
    assert preview_forward_path(raw, "/preview/foo") == \
        "/_next/image?url=https%3A%2F%2Fx.jpg&w=1920&q=75"


def test_trailing_slash_root():
    assert preview_forward_path("/preview/foo/", "/preview/foo") == "/"


def test_bare_slug_becomes_root():
    assert preview_forward_path("/preview/foo", "/preview/foo") == "/"


def test_sub_route():
    assert preview_forward_path("/preview/foo/about", "/preview/foo") == "/about"


def test_query_on_bare_slug_gets_root_prefix():
    assert preview_forward_path("/preview/foo?t=1", "/preview/foo") == "/?t=1"


def test_prefix_mismatch_returns_input():
    assert preview_forward_path("/other/path", "/preview/foo") == "/other/path"
