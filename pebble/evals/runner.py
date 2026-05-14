"""Eval runner — load a build directory, execute checks, return results.

The runner is the only module that knows about the filesystem layout
(``output/<slug>/{brief.json,build_meta.json,site/...}``). Check functions
receive a :class:`BuildContext` and never touch paths directly outside the
context — that keeps them testable with synthetic fixtures.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output"


@dataclass
class CheckResult:
    """One check's verdict.

    ``status`` is the single source of truth — message and details are for
    humans. Statuses:
      - ``pass``  — verified
      - ``fail``  — check ran, condition not met
      - ``skip``  — couldn't run (missing prerequisite, e.g. no site dir)
      - ``error`` — check itself crashed (caught by runner)
    """
    name: str
    status: str
    message: str
    details: dict = field(default_factory=dict)

    @property
    def is_pass(self) -> bool:
        return self.status == "pass"

    @property
    def is_fail(self) -> bool:
        return self.status == "fail"


@dataclass
class BuildContext:
    """Everything a check needs to inspect a build.

    ``brief`` and ``meta`` are pre-parsed so checks don't each re-read JSON.
    ``site_dir`` may not exist (prompt-only builds) — checks should handle
    that by returning ``skip``.
    """
    slug: str
    build_dir: Path
    site_dir: Path
    brief: dict
    meta: dict

    @classmethod
    def load(cls, build_dir: Path) -> "BuildContext":
        slug = build_dir.name
        site_dir = build_dir / "site"
        brief = _load_json(build_dir / "brief.json")
        meta = _load_json(build_dir / "build_meta.json")
        return cls(
            slug=slug,
            build_dir=build_dir,
            site_dir=site_dir,
            brief=brief,
            meta=meta,
        )


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def run_checks(
    build_dir: Path,
    checks: Optional[list[Callable[[BuildContext], CheckResult]]] = None,
) -> list[CheckResult]:
    """Run the eval suite against a build directory.

    A check that raises is caught and recorded as ``error`` — one bad
    check doesn't abort the suite. ``checks`` defaults to :data:`ALL_CHECKS`
    from :mod:`pebble.evals.checks` (imported lazily to avoid an import
    cycle with this module).
    """
    if checks is None:
        from pebble.evals.checks import ALL_CHECKS
        checks = ALL_CHECKS

    ctx = BuildContext.load(build_dir)
    results: list[CheckResult] = []
    for check in checks:
        name = check.__name__
        try:
            results.append(check(ctx))
        except Exception as e:
            results.append(CheckResult(
                name=name,
                status="error",
                message=f"check raised: {type(e).__name__}: {e}",
            ))
    return results


def list_build_dirs() -> list[Path]:
    """All directories under ``output/`` that look like real builds
    (have a ``brief.json``). Sorted lexicographically — stable for reporting."""
    if not OUTPUT_DIR.exists():
        return []
    return sorted(
        d for d in OUTPUT_DIR.iterdir()
        if d.is_dir() and (d / "brief.json").exists()
    )
