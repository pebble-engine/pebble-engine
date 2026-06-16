"""Onboarding gates — plan-required until N completed builds."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PLAN_REQUIRED_UNTIL_BUILDS = 2


def _output_dir() -> Path:
    import pebble_engine as pe
    return pe.OUTPUT_DIR


def completed_build_count(user_id: str) -> int:
    if not user_id:
        return 0
    root = _output_dir()
    if not root.is_dir():
        return 0
    count = 0
    for project_dir in root.iterdir():
        if not project_dir.is_dir():
            continue
        if not (project_dir / "build_meta.json").is_file():
            continue
        brief_path = project_dir / "brief.json"
        if not brief_path.is_file():
            continue
        try:
            brief = json.loads(brief_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if brief.get("_user_id") == user_id:
            count += 1
    return count


def onboarding_status(user_id: str | None) -> dict[str, Any]:
    builds = completed_build_count(user_id or "")
    return {
        "builds_completed": builds,
        "plan_required": builds < PLAN_REQUIRED_UNTIL_BUILDS,
        "plan_required_until": PLAN_REQUIRED_UNTIL_BUILDS,
    }
