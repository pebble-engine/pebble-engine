"""Regression library — every PR touching pebble.evals or pebble.repair must
prove it still produces the expected lift on each canonical broken-build case.

Each case in ``tests/repair_corpus/`` declares its failing-checks baseline and
a canned LLM response. The test runs the full repair loop with a FakeClient
returning the canned response, so the regression library never costs LLM tokens.

See ``tests/repair_corpus/README.md`` for the per-case file layout.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from pebble.repair import repair_build


CORPUS_DIR = Path(__file__).parent / "repair_corpus"


class FakeClient:
    """Returns the canned response verbatim — same shape as the real LLM client."""
    def __init__(self, response: str):
        self.response = response
        self.calls: list[dict] = []
        self.model = "fake-corpus-client"
        self.provider = "fake"

    def generate(self, system: str, user: str, max_tokens: int = 16000, **_) -> str:
        self.calls.append({"system": system, "user": user})
        return self.response


def _corpus_cases() -> list[Path]:
    if not CORPUS_DIR.exists():
        return []
    return sorted(
        p for p in CORPUS_DIR.iterdir()
        if p.is_dir() and (p / "brief.json").exists()
    )


@pytest.mark.parametrize("case_dir", _corpus_cases(), ids=lambda p: p.name)
@pytest.mark.integration
def test_repair_corpus_case(tmp_path, case_dir):
    """Run a corpus case through repair_build and assert the expected outcome.

    The case directory is copied into tmp_path so the test never mutates the
    source corpus — the canonical broken state stays preserved on disk.
    """
    # Copy the case into tmp (slug = case directory name)
    slug = case_dir.name
    target = tmp_path / slug
    shutil.copytree(case_dir, target)
    # Strip the metadata files the runner uses but the engine doesn't expect
    for meta in ("expected_failures.json", "canned_response.txt", "expected_repair.json"):
        meta_path = target / meta
        if meta_path.exists():
            meta_path.unlink()

    expected_failures = json.loads((case_dir / "expected_failures.json").read_text())
    expected_repair = json.loads((case_dir / "expected_repair.json").read_text())
    canned_response = (case_dir / "canned_response.txt").read_text()

    client = FakeClient(canned_response)
    report = repair_build(
        slug=slug,
        max_rounds=2,
        client=client,
        output_dir=tmp_path,
    )

    # Baseline matches what the case declared
    expected_failing = set(expected_failures["failing_checks"])
    round1 = report.rounds[0]
    assert set(round1.failed_checks) == expected_failing, (
        f"{slug}: baseline failures mismatch — expected {expected_failing}, "
        f"got {set(round1.failed_checks)}"
    )

    # The repair was kept
    assert round1.kept == expected_repair["kept"], (
        f"{slug}: expected kept={expected_repair['kept']}, got {round1.kept}"
    )

    # The files written match
    if expected_repair.get("files_written"):
        expected_files = set(expected_repair["files_written"])
        assert set(round1.files_written) == expected_files, (
            f"{slug}: files_written mismatch — expected {expected_files}, "
            f"got {set(round1.files_written)}"
        )


def test_corpus_dir_exists():
    """Smoke test — at least one canonical case is present in the corpus.
    If the directory is empty, the regression library has been deleted."""
    cases = _corpus_cases()
    assert len(cases) >= 1, (
        f"No cases under {CORPUS_DIR}; the regression library is empty. "
        "Restore at least the missing-page case."
    )
