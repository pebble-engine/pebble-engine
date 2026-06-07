"""Durable per-project + per-account "about your business" context (P1).

Injected into every build / template-instantiation / refine so the AI
respects the owner's standing facts and voice without being re-told each
time. This is owner-provided INSTRUCTIONS/standing facts — it never
licenses fabrication; the engine's anti-slop rules remain authoritative.

Storage:
- per-project: `brief.json["business_knowledge"]` (a string)
- per-account: `output/.users/<uid>/knowledge.txt`
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

MAX_BLOCK_CHARS = 4000  # keep the prompt lean; trim pathological input


def project_knowledge(brief: dict[str, Any]) -> str:
    """Read the per-project knowledge string from a brief dict."""
    v = (brief or {}).get("business_knowledge")
    return v.strip() if isinstance(v, str) else ""


def _account_path(output_dir: Path, uid: str) -> Path:
    return Path(output_dir) / ".users" / uid / "knowledge.txt"


def load_account_knowledge(output_dir: Path, uid: str) -> str:
    """Load the account-wide knowledge default for a user. Fail-soft."""
    if not uid:
        return ""
    p = _account_path(output_dir, uid)
    try:
        return p.read_text(encoding="utf-8").strip() if p.exists() else ""
    except Exception:
        return ""


def save_account_knowledge(output_dir: Path, uid: str, text: str) -> None:
    """Persist the account-wide knowledge default (trimmed to the cap)."""
    if not uid:
        return
    p = _account_path(output_dir, uid)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text((text or "").strip()[:MAX_BLOCK_CHARS], encoding="utf-8")


def _sanitize(s: str) -> str:
    """str.format safety: literal braces in the rendered build template
    would break PROMPT_TEMPLATE.format(...). Neutralize them."""
    return (s or "").replace("{", "(").replace("}", ")")


def render_knowledge_block(project: str, account: str) -> str:
    """Render the injectable knowledge block (or "" when there's none)."""
    project = _sanitize((project or "").strip())[:MAX_BLOCK_CHARS]
    account = _sanitize((account or "").strip())[:MAX_BLOCK_CHARS]
    if not project and not account:
        return ""
    parts = [
        "## ABOUT THIS BUSINESS (owner-provided — honor on every page; never contradict it)"
    ]
    if account:
        parts.append("Account-wide preferences:\n" + account)
    if project:
        parts.append("This project specifically:\n" + project)
    return "\n\n".join(parts)


__all__ = [
    "MAX_BLOCK_CHARS",
    "project_knowledge",
    "load_account_knowledge",
    "save_account_knowledge",
    "render_knowledge_block",
]
