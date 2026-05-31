"""Tests for the motion-primitives library wiring (sub-project B1).

The compiler must copy the curated motion primitives into every generated
site's components/motion/ directory and declare framer-motion as a dependency.
"""
import json
from pathlib import Path

from pebble.blocks_compiler import _write_scaffolding


def test_scaffolding_writes_motion_library(tmp_path: Path):
    _write_scaffolding(tmp_path)
    motion_dir = tmp_path / "components" / "motion"
    assert (motion_dir / "FadeUp.tsx").exists()
    assert (motion_dir / "RevealWords.tsx").exists()
    assert (motion_dir / "Parallax.tsx").exists()
    # primitives are client components — directive on line 1
    assert (motion_dir / "FadeUp.tsx").read_text(encoding="utf-8").splitlines()[0] == '"use client";'


def test_motion_primitives_are_edit_safe_and_reduced_motion_aware(tmp_path: Path):
    _write_scaffolding(tmp_path)
    motion_dir = tmp_path / "components" / "motion"
    fade = (motion_dir / "FadeUp.tsx").read_text(encoding="utf-8")
    reveal = (motion_dir / "RevealWords.tsx").read_text(encoding="utf-8")
    # reduced-motion honored
    assert "useReducedMotion" in fade
    # edit-safe: forwards arbitrary props (data-pebble-id) onto the element
    assert "...rest" in fade
    assert "...rest" in reveal


def test_scaffolding_package_json_includes_framer_motion(tmp_path: Path):
    _write_scaffolding(tmp_path)
    pkg = json.loads((tmp_path / "package.json").read_text(encoding="utf-8"))
    assert "framer-motion" in pkg["dependencies"]


def test_tailwind_content_scans_components_dir(tmp_path: Path):
    """REGRESSION: after the section-files refactor, all rendered markup lives
    in components/sections/ + components/motion/ — not app/. The Tailwind
    content glob MUST scan components/ or the generated CSS ships nearly empty
    and every site renders unstyled (mashed text, no layout, no colors)."""
    _write_scaffolding(tmp_path)
    tw = (tmp_path / "tailwind.config.ts").read_text(encoding="utf-8")
    assert "./components/**/*.{ts,tsx}" in tw, \
        "Tailwind must scan components/ — section + motion files live there"
    assert "./app/**/*.{ts,tsx}" in tw
