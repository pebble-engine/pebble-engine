"""Form submissions captured to a per-project inbox.

When a generated site's contact form posts to ``POST /api/forms/<slug>``,
the submission lands at ``output/<slug>/inbox/<id>.json``. The dashboard
inbox view reads these directly. Email notifications, spam filtering,
and webhooks are intentionally simple here so the inbox stays a
reliable, ungated fallback even when third-party providers fail.

Privacy decisions:

- IP addresses are hashed (SHA-256, first 16 hex chars) — we record
  *something* uniquely identifying the submitter for abuse tracing, but
  never the raw IP.
- The honeypot field name is ``_pebble_hp`` — non-empty values cause
  the submission to be silently dropped (200 OK to the bot, no inbox
  entry).
- ``user_agent`` and ``referrer`` are recorded for context but never
  exposed to the public form endpoint response.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


HONEYPOT_FIELD = "_pebble_hp"

# Server-imposed caps — protect against abuse and keep one bad caller
# from spamming GB into a project's inbox.
MAX_PAYLOAD_BYTES   = 16 * 1024    # 16 KB
MAX_FIELDS_PER_FORM = 32
MAX_FIELD_LEN       = 4 * 1024     # 4 KB per value


def _engine_output_dir() -> Path:
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path(__file__).parent.parent.resolve() / "output"


def _inbox_dir(slug: str) -> Path:
    d = _engine_output_dir() / slug / "inbox"
    d.mkdir(parents=True, exist_ok=True)
    return d


class FormError(Exception):
    """Validation error surfaced to the form submitter."""


@dataclass
class Submission:
    id:          str
    slug:        str
    received_at: str
    fields:      dict
    ip_hash:     Optional[str] = None
    user_agent:  Optional[str] = None
    referrer:    Optional[str] = None
    read:        bool = False

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


# --------- Helpers --------------------------------------------------------

_SAFE_ID_RE = re.compile(r"[^a-zA-Z0-9-]+")


def _new_id() -> str:
    """Filesystem-safe, sortable id: microsecond timestamp + 6 hex chars
    of cryptographic random.

    Earlier version derived the suffix from the second-precision timestamp
    — bursts in the same millisecond collided and overwrote prior
    submissions. ``secrets.token_hex`` decouples uniqueness from clock
    granularity.
    """
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")  # microsecond
    return f"{ts}-{secrets.token_hex(3)}"


def _hash_ip(ip: Optional[str]) -> Optional[str]:
    if not ip:
        return None
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()[:16]


def _normalize_fields(raw: dict) -> dict:
    """Strip out the honeypot, clamp lengths, drop excess fields.

    Caller decides whether to silently drop submissions that hit the
    honeypot — this helper only normalizes shape.
    """
    if not isinstance(raw, dict):
        raise FormError("form payload must be an object")
    out: dict = {}
    for i, (k, v) in enumerate(raw.items()):
        if i >= MAX_FIELDS_PER_FORM:
            break
        if not isinstance(k, str) or not k.strip():
            continue
        if k == HONEYPOT_FIELD:
            continue
        if isinstance(v, (list, tuple)):
            v = ", ".join(str(x) for x in v)
        if v is None:
            v = ""
        if not isinstance(v, str):
            v = str(v)
        if len(v) > MAX_FIELD_LEN:
            v = v[:MAX_FIELD_LEN]
        out[k.strip()[:64]] = v
    return out


def is_honeypot_trip(raw: dict) -> bool:
    """True iff the honeypot field was filled — usually means a bot."""
    if not isinstance(raw, dict):
        return False
    val = raw.get(HONEYPOT_FIELD)
    return bool(val and str(val).strip())


# --------- Public API -----------------------------------------------------

def save_submission(
    slug: str,
    fields: dict,
    *,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    referrer: Optional[str] = None,
) -> Submission:
    """Write a submission to the project's inbox and return the record."""
    norm = _normalize_fields(fields)
    rec = Submission(
        id=_new_id(),
        slug=slug,
        received_at=datetime.now(timezone.utc).isoformat(),
        fields=norm,
        ip_hash=_hash_ip(ip),
        user_agent=(user_agent or "")[:512] or None,
        referrer=(referrer or "")[:512] or None,
    )
    (_inbox_dir(slug) / f"{rec.id}.json").write_text(
        json.dumps(rec.to_dict(), indent=2), encoding="utf-8"
    )
    return rec


def list_submissions(slug: str) -> list[dict]:
    """Return every submission for ``slug``, newest first."""
    d = _engine_output_dir() / slug / "inbox"
    if not d.exists():
        return []
    out: list[dict] = []
    for p in d.glob("*.json"):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue
    out.sort(key=lambda r: r.get("received_at") or r.get("id") or "", reverse=True)
    return out


def get_submission(slug: str, submission_id: str) -> Optional[dict]:
    p = _engine_output_dir() / slug / "inbox" / f"{submission_id}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def update_submission(slug: str, submission_id: str, patch: dict) -> Optional[dict]:
    """Merge ``patch`` into an existing submission. Used to flip ``read``."""
    p = _engine_output_dir() / slug / "inbox" / f"{submission_id}.json"
    if not p.exists():
        return None
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    rec.update({k: v for k, v in patch.items() if k in ("read",)})
    p.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return rec


def delete_submission(slug: str, submission_id: str) -> bool:
    p = _engine_output_dir() / slug / "inbox" / f"{submission_id}.json"
    if not p.exists():
        return False
    try:
        p.unlink()
        return True
    except Exception:
        return False


def inbox_summary(slug: str) -> dict:
    rows = list_submissions(slug)
    unread = sum(1 for r in rows if not r.get("read"))
    return {"total": len(rows), "unread": unread}


__all__ = [
    "FormError",
    "Submission",
    "HONEYPOT_FIELD",
    "MAX_PAYLOAD_BYTES",
    "is_honeypot_trip",
    "save_submission",
    "list_submissions",
    "get_submission",
    "update_submission",
    "delete_submission",
    "inbox_summary",
]
