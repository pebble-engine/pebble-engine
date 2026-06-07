"""P3 — GET/POST /api/account/brand-kit (auth-gated, per-account)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from pebble.security import resolve_user_id
from pebble import brand_kit as _bk


def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


def _read_body(handler) -> Optional[dict]:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return None
    if length <= 0:
        return {}
    try:
        return json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return None


def run_get_brand_kit(handler) -> None:
    uid = resolve_user_id(handler)
    if not uid:
        handler._json(401, {"error": "authentication required"}); return
    handler._json(200, {"brand_kit": _bk.load_account_brand_kit(_output_dir(), uid)})


def run_put_brand_kit(handler) -> None:
    uid = resolve_user_id(handler)
    if not uid:
        handler._json(401, {"error": "authentication required"}); return
    body = _read_body(handler)
    if body is None:
        return
    kit_in = body.get("brand_kit") if isinstance(body.get("brand_kit"), dict) else body
    kit = _bk.save_account_brand_kit(_output_dir(), uid, kit_in)
    handler._json(200, {"brand_kit": kit, "ok": True})
