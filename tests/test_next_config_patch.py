"""ensure_allowed_dev_origins tests (Phase 20c, 2026-05-20).

Triggered by Marc's 2026-05-20 mechanic preview that emitted a cross-origin
warning for every /_next/* dev request because the generated next.config.mjs
was the minimal empty config. This module pins the patch behavior.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from pebble.next_config_patch import ensure_allowed_dev_origins


# ------------------------------------------------------------------ #
# Smoking-gun fixture                                                 #
# ------------------------------------------------------------------ #


def test_patches_minimal_empty_config(tmp_path: Path):
    """The exact config Qwen produced on 2026-05-20."""
    cfg = tmp_path / "next.config.mjs"
    cfg.write_text(
        "/** @type {import('next').NextConfig} */\n"
        "const nextConfig = {};\n"
        "\n"
        "export default nextConfig;\n",
        encoding="utf-8",
    )
    changed = ensure_allowed_dev_origins(cfg)
    assert changed is True
    out = cfg.read_text(encoding="utf-8")
    assert "allowedDevOrigins" in out
    assert "127.0.0.1" in out
    assert "localhost" in out


# ------------------------------------------------------------------ #
# Idempotency — second call must not double-inject                     #
# ------------------------------------------------------------------ #


def test_idempotent_when_already_present(tmp_path: Path):
    cfg = tmp_path / "next.config.mjs"
    cfg.write_text(
        "const nextConfig = {\n"
        "  allowedDevOrigins: ['127.0.0.1'],\n"
        "};\n",
        encoding="utf-8",
    )
    changed = ensure_allowed_dev_origins(cfg)
    assert changed is False  # already present, no change


def test_repeat_call_after_patch_is_noop(tmp_path: Path):
    cfg = tmp_path / "next.config.mjs"
    cfg.write_text("const nextConfig = {};\n", encoding="utf-8")
    assert ensure_allowed_dev_origins(cfg) is True
    text_after_first = cfg.read_text(encoding="utf-8")
    # Second call must report no change AND leave file content identical
    assert ensure_allowed_dev_origins(cfg) is False
    assert cfg.read_text(encoding="utf-8") == text_after_first
    # And content has exactly ONE allowedDevOrigins line
    assert text_after_first.count("allowedDevOrigins") == 1


# ------------------------------------------------------------------ #
# Existing config content is preserved                                 #
# ------------------------------------------------------------------ #


def test_preserves_other_config_fields(tmp_path: Path):
    cfg = tmp_path / "next.config.mjs"
    cfg.write_text(
        "/** @type {import('next').NextConfig} */\n"
        "const nextConfig = {\n"
        "  reactStrictMode: true,\n"
        "  images: { unoptimized: true },\n"
        "};\n"
        "export default nextConfig;\n",
        encoding="utf-8",
    )
    ensure_allowed_dev_origins(cfg)
    out = cfg.read_text(encoding="utf-8")
    assert "reactStrictMode: true" in out
    assert "images: { unoptimized: true }" in out
    assert "allowedDevOrigins" in out
    assert "export default nextConfig" in out


def test_preserves_jsdoc_type_comment(tmp_path: Path):
    cfg = tmp_path / "next.config.mjs"
    body = (
        "/** @type {import('next').NextConfig} */\n"
        "const nextConfig = {};\n"
    )
    cfg.write_text(body, encoding="utf-8")
    ensure_allowed_dev_origins(cfg)
    out = cfg.read_text(encoding="utf-8")
    assert "/** @type {import('next').NextConfig} */" in out


# ------------------------------------------------------------------ #
# Edge cases — missing file, unrecognized format                       #
# ------------------------------------------------------------------ #


def test_no_op_when_file_missing(tmp_path: Path):
    cfg = tmp_path / "missing.mjs"
    assert ensure_allowed_dev_origins(cfg) is False
    assert not cfg.exists()


def test_no_op_on_commonjs_style_config(tmp_path: Path):
    """A `module.exports = {...}` config has no `const nextConfig` opener.
    The patcher should leave it alone — that's not a Pebble-emitted file."""
    cfg = tmp_path / "next.config.mjs"
    cfg.write_text(
        "module.exports = {\n"
        "  reactStrictMode: true,\n"
        "};\n",
        encoding="utf-8",
    )
    assert ensure_allowed_dev_origins(cfg) is False
    # Original content unchanged
    assert "module.exports" in cfg.read_text(encoding="utf-8")


def test_handles_multiline_opener(tmp_path: Path):
    """Some generated configs split the opener across lines."""
    cfg = tmp_path / "next.config.mjs"
    cfg.write_text(
        "const nextConfig\n"
        "  = {\n"
        "  reactStrictMode: true,\n"
        "};\n",
        encoding="utf-8",
    )
    assert ensure_allowed_dev_origins(cfg) is True
    assert "allowedDevOrigins" in cfg.read_text(encoding="utf-8")


# ------------------------------------------------------------------ #
# Patched config is valid (sanity)                                     #
# ------------------------------------------------------------------ #


def test_patched_file_has_balanced_braces(tmp_path: Path):
    """Quick syntactic sanity check — the patch shouldn't break brace pairing."""
    cfg = tmp_path / "next.config.mjs"
    cfg.write_text("const nextConfig = {};\n", encoding="utf-8")
    ensure_allowed_dev_origins(cfg)
    out = cfg.read_text(encoding="utf-8")
    assert out.count("{") == out.count("}")


def test_patched_file_includes_three_canonical_origins(tmp_path: Path):
    """We currently inject ['127.0.0.1', 'localhost', '*.local'] — the three
    most common local-dev surfaces. Pin this so future widening is intentional."""
    cfg = tmp_path / "next.config.mjs"
    cfg.write_text("const nextConfig = {};\n", encoding="utf-8")
    ensure_allowed_dev_origins(cfg)
    out = cfg.read_text(encoding="utf-8")
    assert "'127.0.0.1'" in out
    assert "'localhost'" in out
    assert "'*.local'" in out
