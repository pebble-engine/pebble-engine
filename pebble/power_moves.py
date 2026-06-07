"""Curated "power moves" — reusable, trigger-matchable instruction packs the
engine runs through the existing refine path (snapshot → LLM edit → apply →
bill). Each lives as a SKILL.md (frontmatter + markdown body) under
``pebble/power_moves/``.

The frontmatter is the Anthropic Agent-Skills shape (id, label, description,
triggers, billable) so a future "import skills" feature can drop compatible
files in with no loader changes.
"""
from __future__ import annotations

import functools
from pathlib import Path
from typing import Any, Optional

_DIR = Path(__file__).resolve().parent / "power_moves"


def _parse(md: str) -> dict[str, Any]:
    fm: dict[str, Any] = {}
    body = md
    if md.startswith("---"):
        parts = md.split("---", 2)
        if len(parts) == 3:
            _, raw, body = parts
            for line in raw.strip().splitlines():
                if ":" not in line:
                    continue
                k, _, v = line.partition(":")
                k, v = k.strip(), v.strip()
                if k == "triggers":
                    fm[k] = [t.strip().lower() for t in v.split(",") if t.strip()]
                elif k == "billable":
                    fm[k] = v.lower() in ("true", "yes", "1")
                else:
                    fm[k] = v
    fm.setdefault("triggers", [])
    fm.setdefault("billable", True)
    fm["instruction"] = body.strip()
    return fm


@functools.lru_cache(maxsize=1)
def _load_all() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not _DIR.exists():
        return out
    for f in sorted(_DIR.glob("*.md")):
        try:
            d = _parse(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        sid = (d.get("id") or f.stem).strip()
        d["id"] = sid
        out[sid] = d
    return out


def get_skill(skill_id: str) -> Optional[dict[str, Any]]:
    return _load_all().get((skill_id or "").strip())


def list_skills() -> list[dict[str, Any]]:
    """UI-safe list — omits the full instruction body."""
    return [
        {
            "id": s["id"],
            "label": s.get("label", s["id"]),
            "description": s.get("description", ""),
            "billable": s.get("billable", True),
        }
        for s in _load_all().values()
    ]


def match_skill(text: str) -> Optional[dict[str, Any]]:
    low = (text or "").lower()
    for s in _load_all().values():
        if any(t and t in low for t in s.get("triggers", [])):
            return s
    return None


def instructions_by_id() -> dict[str, str]:
    """For refine integration: {skill_id: instruction body}."""
    return {sid: s["instruction"] for sid, s in _load_all().items()}


__all__ = ["get_skill", "list_skills", "match_skill", "instructions_by_id"]
