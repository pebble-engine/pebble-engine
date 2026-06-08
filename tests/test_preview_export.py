"""Static-export-for-generated-sites: config + byte-identical source restore.

The real `next build` is mocked (slow + needs node_modules). We verify:
  - the transient preview config is correct,
  - source files ARE the preview versions *during* the build,
  - source files are restored byte-identically AFTER the build (success),
  - restore also happens when the build FAILS,
  - absent files are never created.
"""
from __future__ import annotations

import subprocess

import pytest

from pebble import preview_export as pe


def _make_site(tmp_path):
    site = tmp_path / "site"
    (site / "app" / "actions").mkdir(parents=True)
    cfg = site / "next.config.mjs"
    contact = site / "app" / "actions" / "contact.ts"
    cfg.write_text("export default { reactStrictMode: true };\n", encoding="utf-8")
    contact.write_text('"use server";\nexport async function submitContactForm(){}\n', encoding="utf-8")
    (site / "node_modules").mkdir()  # so install is skipped
    return site, cfg, contact


def test_preview_config_has_export_and_basepath():
    cfg = pe.preview_next_config("my-slug")
    assert 'output: "export"' in cfg
    assert 'basePath: "/preview/my-slug"' in cfg
    assert "unoptimized: true" in cfg


def test_build_swaps_then_restores_byte_identically(tmp_path, monkeypatch):
    site, cfg, contact = _make_site(tmp_path)
    cfg_before = cfg.read_bytes()
    contact_before = contact.read_bytes()

    seen = {}

    def fake_run(cmd, **kw):
        # Capture what the build tool would see, and fake the out/ dir.
        seen["cfg"] = cfg.read_text(encoding="utf-8")
        seen["contact"] = contact.read_text(encoding="utf-8")
        (site / "out").mkdir(exist_ok=True)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(pe.subprocess, "run", fake_run)

    out = pe.export_generated_site(site, "my-slug", skip_install=True)
    assert out == site / "out"
    # During the build, the swapped-in preview versions were present:
    assert 'output: "export"' in seen["cfg"]
    # The stub must NOT carry the "use server" DIRECTIVE (first statement);
    # it may mention the string in a comment. Static export forbids the directive.
    assert not seen["contact"].lstrip().startswith('"use server"')
    assert "submitContactForm" in seen["contact"]  # stub still exports the name
    # After the build, originals restored byte-for-byte:
    assert cfg.read_bytes() == cfg_before
    assert contact.read_bytes() == contact_before


def test_restore_happens_on_build_failure(tmp_path, monkeypatch):
    site, cfg, contact = _make_site(tmp_path)
    cfg_before = cfg.read_bytes()
    contact_before = contact.read_bytes()

    def boom(cmd, **kw):
        raise subprocess.CalledProcessError(1, cmd)

    monkeypatch.setattr(pe.subprocess, "run", boom)

    with pytest.raises(subprocess.CalledProcessError):
        pe.export_generated_site(site, "my-slug", skip_install=True)
    # Source still restored despite the failure:
    assert cfg.read_bytes() == cfg_before
    assert contact.read_bytes() == contact_before


def test_absent_contact_file_not_created(tmp_path, monkeypatch):
    site, cfg, contact = _make_site(tmp_path)
    contact.unlink()  # no contact action in this site

    def fake_run(cmd, **kw):
        (site / "out").mkdir(exist_ok=True)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(pe.subprocess, "run", fake_run)
    pe.export_generated_site(site, "my-slug", skip_install=True)
    assert not contact.exists()  # never created a file the source lacked


def test_missing_site_dir_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        pe.export_generated_site(tmp_path / "nope", "x", skip_install=True)
