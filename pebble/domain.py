"""Custom domain wiring for published Pebble sites.

A single domain per project for the MVP. Persists state at
``output/<slug>/domain.json`` and (when Cloudflare is configured)
registers the domain against the Cloudflare Pages project so the
deploy gets a TLS cert and traffic routing.

The Cloudflare API is the canonical source of truth for ``active``
status; the local state file mirrors what we last saw plus the CNAME
instructions for the user.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pebble.publish import (
    CF_API_BASE,
    PublishError,
    _cf_request,
    cloudflare_configured,
    slug_to_project_name,
)


# RFC-1035-ish host validation. Each label is 1-63 chars, allows letters,
# digits, hyphens (no leading/trailing hyphen). Total ≤ 253. We deliberately
# don't accept underscores even though some legacy DNS allows them.
_HOST_RE = re.compile(
    r"^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"
)


def _engine_output_dir() -> Path:
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path(__file__).parent.parent.resolve() / "output"


def _domain_path(slug: str) -> Path:
    return _engine_output_dir() / slug / "domain.json"


class DomainError(Exception):
    """User-visible domain failure."""


@dataclass
class DomainRecord:
    host:         str
    status:       str             # "pending" | "active" | "error"
    set_at:       str
    cname_target: str             # e.g. pebble-good-co.pages.dev
    cname_record: str             # paste-ready DNS instruction
    error:        Optional[str] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


def normalize_host(host: str) -> str:
    """Lowercase, strip scheme/trailing slash, strip leading ``www.``-prefix
    only if the user explicitly typed `www.foo.com` (we keep it — they may
    legitimately want www to be the primary)."""
    if not isinstance(host, str):
        raise DomainError("Domain is required.")
    h = host.strip().lower()
    # Strip scheme if pasted from a browser
    for prefix in ("https://", "http://"):
        if h.startswith(prefix):
            h = h[len(prefix):]
    # Strip path / port
    h = h.split("/", 1)[0]
    h = h.split(":", 1)[0]
    if not h:
        raise DomainError("Domain is required.")
    if not _HOST_RE.match(h):
        raise DomainError(
            f"That doesn't look like a domain. Try something like example.com."
        )
    return h


def cname_target_for(slug: str) -> str:
    """The CNAME a user must point their domain at."""
    return f"{slug_to_project_name(slug)}.pages.dev"


def cname_instructions(host: str, cname_target: str) -> str:
    """One-liner DNS record the user can paste into their DNS host."""
    return f"{host} CNAME {cname_target}"


# --------- State I/O ------------------------------------------------------

def read_domain(slug: str) -> Optional[dict]:
    p = _domain_path(slug)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_domain(slug: str, record: DomainRecord) -> None:
    p = _domain_path(slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")


def clear_domain(slug: str) -> None:
    p = _domain_path(slug)
    if p.exists():
        try: p.unlink()
        except Exception: pass


# --------- Cloudflare-backed operations -----------------------------------

def _cf_creds() -> tuple[str, str]:
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    token      = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if not account_id or not token:
        raise DomainError("Cloudflare not configured. See the Cloudflare setup checklist.")
    return account_id, token


def attach_cloudflare_domain(slug: str, host: str) -> dict:
    """Register ``host`` as a custom domain on the project's Cloudflare
    Pages project. Idempotent: if the domain already exists, returns
    its current record.
    """
    account_id, token = _cf_creds()
    project = slug_to_project_name(slug)
    url = f"{CF_API_BASE}/accounts/{account_id}/pages/projects/{project}/domains"
    try:
        return _cf_request("POST", url, token=token, body={"name": host})
    except PublishError as e:
        msg = str(e)
        # Cloudflare returns 409 if the domain is already attached;
        # treat that as a soft success so the user can re-run safely.
        if "409" in msg or "already" in msg.lower() or "duplicate" in msg.lower():
            return _cf_request(
                "GET",
                f"{url}/{host}",
                token=token,
            )
        raise DomainError(f"Cloudflare domain attach failed: {e}")


def detach_cloudflare_domain(slug: str, host: str) -> None:
    """Remove a custom domain from the project. Tolerant of 404."""
    account_id, token = _cf_creds()
    project = slug_to_project_name(slug)
    url = f"{CF_API_BASE}/accounts/{account_id}/pages/projects/{project}/domains/{host}"
    try:
        _cf_request("DELETE", url, token=token)
    except PublishError as e:
        if "404" in str(e):
            return  # already gone — treat as success
        raise DomainError(f"Cloudflare domain detach failed: {e}")


def refresh_cloudflare_status(slug: str, host: str) -> str:
    """Poll Cloudflare for the latest domain status. Returns ``"pending"``,
    ``"active"``, or ``"error"``.
    """
    account_id, token = _cf_creds()
    project = slug_to_project_name(slug)
    url = f"{CF_API_BASE}/accounts/{account_id}/pages/projects/{project}/domains/{host}"
    try:
        resp = _cf_request("GET", url, token=token)
    except PublishError:
        return "error"
    result = resp.get("result") or {}
    status = (result.get("status") or "").lower()
    if status in ("active", "live", "verified"):
        return "active"
    if status in ("pending", "initializing", "verifying", "deploying", "removed"):
        return "pending"
    return "error"


# --------- Public surface --------------------------------------------------

def set_domain(slug: str, host_raw: str) -> DomainRecord:
    """Attach (or re-attach) a custom domain to a project.

    If Cloudflare is configured, registers with Cloudflare Pages and
    captures the live status. Otherwise stores the record locally with
    ``status="pending"`` and surfaces the CNAME instructions so the user
    can wire it once Cloudflare is configured.
    """
    host = normalize_host(host_raw)
    cname_target = cname_target_for(slug)
    cname_rec    = cname_instructions(host, cname_target)
    now = datetime.now(timezone.utc).isoformat()

    if not cloudflare_configured():
        rec = DomainRecord(
            host=host,
            status="pending",
            set_at=now,
            cname_target=cname_target,
            cname_record=cname_rec,
            error=None,
        )
        write_domain(slug, rec)
        return rec

    try:
        attach_cloudflare_domain(slug, host)
    except DomainError as e:
        rec = DomainRecord(
            host=host,
            status="error",
            set_at=now,
            cname_target=cname_target,
            cname_record=cname_rec,
            error=str(e),
        )
        write_domain(slug, rec)
        raise

    status = refresh_cloudflare_status(slug, host)
    rec = DomainRecord(
        host=host,
        status=status,
        set_at=now,
        cname_target=cname_target,
        cname_record=cname_rec,
    )
    write_domain(slug, rec)
    return rec


def remove_domain(slug: str) -> Optional[dict]:
    """Detach the project's custom domain. Returns the previous record
    (or None if no domain was set)."""
    prev = read_domain(slug)
    if not prev:
        return None
    if cloudflare_configured():
        try:
            detach_cloudflare_domain(slug, prev["host"])
        except DomainError:
            # We still clear local state — the user can re-attach if
            # Cloudflare gets unstuck.
            pass
    clear_domain(slug)
    return prev


def refresh_domain(slug: str) -> Optional[DomainRecord]:
    """Re-poll Cloudflare for the latest status of the domain we last set."""
    prev = read_domain(slug)
    if not prev:
        return None
    host = prev.get("host", "")
    cname_target = prev.get("cname_target") or cname_target_for(slug)
    cname_rec    = prev.get("cname_record") or cname_instructions(host, cname_target)

    status = "pending"
    if cloudflare_configured() and host:
        status = refresh_cloudflare_status(slug, host)

    rec = DomainRecord(
        host=host,
        status=status,
        set_at=prev.get("set_at") or datetime.now(timezone.utc).isoformat(),
        cname_target=cname_target,
        cname_record=cname_rec,
        error=prev.get("error"),
    )
    write_domain(slug, rec)
    return rec


__all__ = [
    "DomainError",
    "DomainRecord",
    "normalize_host",
    "cname_target_for",
    "cname_instructions",
    "read_domain",
    "write_domain",
    "clear_domain",
    "set_domain",
    "remove_domain",
    "refresh_domain",
    "attach_cloudflare_domain",
    "detach_cloudflare_domain",
    "refresh_cloudflare_status",
]
