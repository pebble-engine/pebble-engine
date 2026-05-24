"""Tests for pebble.templates.export — the static-export CLI.

The critical invariant: after any export_template() call (success or
failure), the template's source files (next.config.mjs + contact.ts) are
byte-identical to before. This is enforced via try/finally; the tests
mock subprocess.run to avoid actually running npm/next and assert the
files round-trip cleanly."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pebble.templates import export as template_export


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Registry / resolution tests
# ---------------------------------------------------------------------------


def test_list_exportable_template_ids_includes_cinematic_hero():
    ids = template_export.list_exportable_template_ids()
    assert "cinematic_hero" in ids
    assert "cinematic_plumber" in ids
    assert "cinematic_dog_groomer" in ids


def test_list_exportable_template_ids_includes_all_six_cinematic():
    ids = template_export.list_exportable_template_ids()
    cinematic_ids = [i for i in ids if i.startswith("cinematic_")]
    assert len(cinematic_ids) == 6, f"Expected 6 cinematic_* templates, got: {cinematic_ids}"


def test_template_dir_resolves_relative_to_repo_root():
    d = template_export.template_dir("cinematic_hero")
    assert d.is_dir()
    assert (d / "next.config.mjs").is_file()


def test_template_dir_rejects_unknown_id():
    with pytest.raises(KeyError):
        template_export.template_dir("does_not_exist")


# ---------------------------------------------------------------------------
# Source-file safety tests — the non-negotiable part
# ---------------------------------------------------------------------------


def test_source_files_byte_identical_after_successful_export():
    """Critical safety test: source files must not be modified by the CLI."""
    tdir = template_export.template_dir("cinematic_hero")
    config_path = tdir / "next.config.mjs"
    contact_path = tdir / "app" / "actions" / "contact.ts"
    before_config = _sha(config_path)
    before_contact = _sha(contact_path)

    # Mock subprocess.run so we don't actually build; simulate out/ existing by
    # patching the out.is_dir check inside export_template using a targeted mock.
    with patch.object(subprocess, "run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

        # Patch Path.is_dir on the specific `out` path only — we can't blanket-mock
        # all Path.is_dir because template_dir() itself relies on it.
        out_path = tdir / "out"
        original_is_dir = Path.is_dir

        def patched_is_dir(self: Path) -> bool:
            if self == out_path:
                return True
            return original_is_dir(self)

        with patch.object(Path, "is_dir", patched_is_dir):
            template_export.export_template("cinematic_hero", skip_install=True)

    assert _sha(config_path) == before_config, "next.config.mjs was not restored"
    assert _sha(contact_path) == before_contact, "contact.ts was not restored"


def test_source_files_byte_identical_after_failed_export():
    """Even on build failure, the try/finally must restore source files."""
    tdir = template_export.template_dir("cinematic_hero")
    config_path = tdir / "next.config.mjs"
    contact_path = tdir / "app" / "actions" / "contact.ts"
    before_config = _sha(config_path)
    before_contact = _sha(contact_path)

    with patch.object(subprocess, "run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "npx next build")
        with pytest.raises(subprocess.CalledProcessError):
            template_export.export_template("cinematic_hero", skip_install=True)

    assert _sha(config_path) == before_config, "next.config.mjs was not restored after failure"
    assert _sha(contact_path) == before_contact, "contact.ts was not restored after failure"


def test_source_files_byte_identical_after_runtime_error():
    """Even if next build exits 0 but out/ doesn't appear, restoration must happen."""
    tdir = template_export.template_dir("cinematic_hero")
    config_path = tdir / "next.config.mjs"
    contact_path = tdir / "app" / "actions" / "contact.ts"
    before_config = _sha(config_path)
    before_contact = _sha(contact_path)

    out_path = tdir / "out"
    original_is_dir = Path.is_dir

    def patched_is_dir_no_out(self: Path) -> bool:
        if self == out_path:
            return False  # force the "did not produce out/" RuntimeError
        return original_is_dir(self)

    with patch.object(subprocess, "run") as mock_run, \
         patch.object(Path, "is_dir", patched_is_dir_no_out):
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        with pytest.raises(RuntimeError, match="did not produce out/"):
            template_export.export_template("cinematic_hero", skip_install=True)

    assert _sha(config_path) == before_config, "next.config.mjs was not restored after RuntimeError"
    assert _sha(contact_path) == before_contact, "contact.ts was not restored after RuntimeError"


# ---------------------------------------------------------------------------
# --all filter tests — must never touch non-cinematic templates
# ---------------------------------------------------------------------------


def test_main_all_filters_to_cinematic_templates_only():
    """--all must NEVER pick non-cinematic templates. If this regresses,
    a stray invocation could clobber the entire production template fleet."""
    all_ids   = template_export.list_exportable_template_ids()
    cinematic = [i for i in all_ids if i.startswith("cinematic_")]
    other     = [i for i in all_ids if not i.startswith("cinematic_")]
    assert len(cinematic) >= 6,  "Expected at least 6 cinematic_* templates in the registry"
    assert len(other)     >= 1,  "Expected non-cinematic templates to exist (else this test is vacuous)"

    # Mock to avoid actually running builds, then capture which ids _main iterates over.
    seen: list[str] = []
    def _fake_export(tid: str, *, skip_install: bool = False) -> Path:
        seen.append(tid)
        return Path("/tmp/fake")
    with patch.object(template_export, "export_template", side_effect=_fake_export):
        rc = template_export._main(["--all", "--skip-install"])
    assert rc == 0
    assert set(seen) == set(cinematic), \
        f"--all leaked outside cinematic_*: extras={set(seen) - set(cinematic)}"
    for tid in other:
        assert tid not in seen, f"non-cinematic template {tid} was about to be clobbered"
