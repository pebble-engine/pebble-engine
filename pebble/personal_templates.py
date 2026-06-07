"""P4 — personal templates: save a finished project as a reusable starting point.

Mirrors the curated-template pattern in ``pebble/server/templates_api.py`` but
scoped per-account. When an owner "saves a site as a template" we snapshot that
project's ``site/`` directory into a self-contained per-user store, so the
template survives later edits or deletion of the source project.

Storage layout::

    output/.users/<uid>/templates/registry.json
    output/.users/<uid>/templates/<id>/site/...

Registry entry::

    {id, label, source_slug, created_at, file_count, has_content_ts}

``has_content_ts`` records whether the snapshot contains ``content/site.ts``.
Template-instantiated projects do (so reuse can run the cheap content-swap LLM
call); full-generated projects don't (reuse is then a plain structural clone the
owner customises via refine / visual-edit).
"""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

MAX_LABEL = 80
_SKIP = frozenset({"node_modules", ".next", ".turbo", "dist", "build"})
TOKENIZED_FILE = "content/site.ts"


# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #

def _store(output_dir: Path, uid: str) -> Path:
    return Path(output_dir) / ".users" / uid / "templates"


def _registry_path(output_dir: Path, uid: str) -> Path:
    return _store(output_dir, uid) / "registry.json"


def template_site_dir(output_dir: Path, uid: str, template_id: str) -> Path:
    return _store(output_dir, uid) / template_id / "site"


# --------------------------------------------------------------------------- #
# Registry I/O
# --------------------------------------------------------------------------- #

def _read_registry(output_dir: Path, uid: str) -> dict[str, Any]:
    path = _registry_path(output_dir, uid)
    if not path.exists():
        return {"schema_version": "1.0", "templates": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("templates"), list):
            return {"schema_version": "1.0", "templates": []}
        return data
    except Exception:
        return {"schema_version": "1.0", "templates": []}


def _write_registry(output_dir: Path, uid: str, reg: dict[str, Any]) -> None:
    path = _registry_path(output_dir, uid)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(reg, indent=2), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _safe_id(label: str, existing: set[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", (label or "").lower()).strip("-") or "template"
    base = base[:48].strip("-") or "template"
    if base not in existing:
        return base
    n = 2
    while f"{base}-{n}" in existing:
        n += 1
    return f"{base}-{n}"


def _copy_site(src: Path, dst: Path) -> int:
    """Recursive copy excluding build artefacts / deps. Returns file count."""
    written = 0
    for path in src.rglob("*"):
        if any(part in _SKIP for part in path.parts):
            continue
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out)
        written += 1
    return written


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def list_personal_templates(output_dir: Path, uid: str) -> list[dict[str, Any]]:
    if not uid:
        return []
    return list(_read_registry(output_dir, uid).get("templates", []))


def get_personal_template(output_dir: Path, uid: str, template_id: str) -> Optional[dict[str, Any]]:
    for t in list_personal_templates(output_dir, uid):
        if isinstance(t, dict) and t.get("id") == template_id:
            return t
    return None


def save_personal_template(
    output_dir: Path,
    uid: str,
    source_site_dir: Path,
    label: str,
    source_slug: str = "",
) -> dict[str, Any]:
    label = (label or "").strip()
    if not label:
        raise ValueError("label is required")
    label = label[:MAX_LABEL]
    source_site_dir = Path(source_site_dir)
    if not source_site_dir.exists() or not source_site_dir.is_dir():
        raise ValueError("source site directory does not exist")

    reg = _read_registry(output_dir, uid)
    existing = {t.get("id") for t in reg.get("templates", []) if isinstance(t, dict)}
    template_id = _safe_id(label, existing)

    dst = template_site_dir(output_dir, uid, template_id)
    if dst.exists():
        shutil.rmtree(dst, ignore_errors=True)
    file_count = _copy_site(source_site_dir, dst)
    has_content_ts = (dst / TOKENIZED_FILE).exists()

    entry = {
        "id": template_id,
        "label": label,
        "source_slug": source_slug or "",
        "created_at": datetime.now().isoformat(),
        "file_count": file_count,
        "has_content_ts": has_content_ts,
    }
    reg.setdefault("templates", []).append(entry)
    _write_registry(output_dir, uid, reg)
    return entry


def delete_personal_template(output_dir: Path, uid: str, template_id: str) -> bool:
    reg = _read_registry(output_dir, uid)
    templates = reg.get("templates", [])
    kept = [t for t in templates if not (isinstance(t, dict) and t.get("id") == template_id)]
    if len(kept) == len(templates):
        return False
    reg["templates"] = kept
    _write_registry(output_dir, uid, reg)
    shutil.rmtree(_store(output_dir, uid) / template_id, ignore_errors=True)
    return True


__all__ = [
    "MAX_LABEL",
    "list_personal_templates",
    "get_personal_template",
    "save_personal_template",
    "delete_personal_template",
    "template_site_dir",
]
