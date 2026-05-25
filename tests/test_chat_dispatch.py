# tests/test_chat_dispatch.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pebble.server.chat import _build_system, _safe_dispatch, DEFAULT_SITEMAP, DISPATCH_OPS


# ---- _build_system tests ---------------------------------------------------

def test_build_system_no_context_contains_style_rules():
    prompt = _build_system(DEFAULT_SITEMAP)
    assert "navigate_to" in prompt
    assert "confirm_action" in prompt
    assert "dispatch_op" in prompt


def test_build_system_with_context_includes_project_name():
    ctx = {"name": "Acme Plumbing", "industry": "plumbing", "slug": "acme-xyz"}
    prompt = _build_system(DEFAULT_SITEMAP, project_context=ctx)
    assert "Acme Plumbing" in prompt
    assert "plumbing" in prompt
    assert "acme-xyz" not in prompt  # slug is never in the prompt (security)


def test_build_system_without_context_no_project_section():
    prompt = _build_system(DEFAULT_SITEMAP)
    assert "PROJECT CONTEXT" not in prompt


def test_build_system_with_context_has_project_section():
    ctx = {"name": "Surf Shop", "industry": "retail"}
    prompt = _build_system(DEFAULT_SITEMAP, project_context=ctx)
    assert "PROJECT CONTEXT" in prompt


# ---- _safe_dispatch tests --------------------------------------------------

def test_safe_dispatch_valid_font_family():
    raw = {"op": "font-family", "params": {"new_font_family": "Playfair Display"}}
    result = _safe_dispatch(raw, current_slug="my-slug-abc")
    assert result is not None
    assert result["op"] == "font-family"
    assert result["params"]["slug"] == "my-slug-abc"
    assert result["params"]["new_font_family"] == "Playfair Display"


def test_safe_dispatch_valid_palette_swap():
    raw = {"op": "palette-swap", "params": {"primary": "#1a3a6b"}}
    result = _safe_dispatch(raw, current_slug="proj-123")
    assert result is not None
    assert result["params"]["palette"] == {"primary": "#1a3a6b"}
    assert result["params"]["slug"] == "proj-123"


def test_safe_dispatch_unknown_op_returns_none():
    raw = {"op": "delete-all-files", "params": {}}
    result = _safe_dispatch(raw, current_slug="proj-123")
    assert result is None


def test_safe_dispatch_no_slug_returns_none():
    raw = {"op": "font-family", "params": {"new_font_family": "Lora"}}
    result = _safe_dispatch(raw, current_slug=None)
    assert result is None


def test_safe_dispatch_strips_injected_slug_from_llm():
    # LLM tries to put its own slug in params — must be overwritten.
    raw = {
        "op": "font-family",
        "params": {"new_font_family": "Lora", "slug": "evil-other-slug"},
    }
    result = _safe_dispatch(raw, current_slug="real-slug-xyz")
    assert result["params"]["slug"] == "real-slug-xyz"


def test_safe_dispatch_non_dict_returns_none():
    assert _safe_dispatch(None, current_slug="x") is None
    assert _safe_dispatch("font-family", current_slug="x") is None
    assert _safe_dispatch(42, current_slug="x") is None


def test_dispatch_ops_dict_has_expected_keys():
    assert "font-family" in DISPATCH_OPS
    assert "color" in DISPATCH_OPS
    assert "font-size" in DISPATCH_OPS
    assert "palette-swap" in DISPATCH_OPS
    assert "image-swap" in DISPATCH_OPS


def test_safe_dispatch_font_size_delta_zero_is_valid():
    # delta=0 is a valid (no-op) value — must NOT be rejected
    raw = {"op": "font-size", "params": {"delta": 0}}
    result = _safe_dispatch(raw, current_slug="proj-abc")
    assert result is not None
    assert result["params"]["delta"] == 0


def test_safe_dispatch_image_swap_valid():
    raw = {
        "op": "image-swap",
        "params": {"original_src": "https://example.com/old.jpg", "new_src": "https://example.com/new.jpg"},
    }
    result = _safe_dispatch(raw, current_slug="proj-abc")
    assert result is not None
    assert result["params"]["new_src"] == "https://example.com/new.jpg"
    assert result["params"]["slug"] == "proj-abc"


def test_safe_dispatch_image_swap_rejects_javascript_url():
    raw = {
        "op": "image-swap",
        "params": {"original_src": "https://example.com/old.jpg", "new_src": "javascript:alert(1)"},
    }
    result = _safe_dispatch(raw, current_slug="proj-abc")
    assert result is None


def test_safe_dispatch_image_swap_rejects_http_url():
    # We only allow https:// for security
    raw = {
        "op": "image-swap",
        "params": {"original_src": "https://example.com/old.jpg", "new_src": "http://example.com/new.jpg"},
    }
    result = _safe_dispatch(raw, current_slug="proj-abc")
    assert result is None
