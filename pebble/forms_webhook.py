"""Outbound webhook for form-inbox submissions.

When a project owner configures a webhook URL for their project, every
successful form submission to /api/forms/<slug> fires a fire-and-
forget JSON POST to that URL. This is the foundation for Zapier /
Slack / HubSpot / generic-webhook integrations — we don't build a
connector per vendor, we let users point us at the vendor's incoming
webhook URL.

Storage: ``output/<slug>/forms_webhook.json`` holds a single config
object. Absent file = no webhook configured.

Delivery: per-project rate-limited (so one misconfigured URL can't
become an outbound DoS). Failures are logged but never bubble up to
the form submitter — the inbox is the source of truth, the webhook
is best-effort.

Privacy: the payload echoes the inbox record shape:
    {
      "event":      "form.submitted",
      "project":    "<slug>",
      "submission": {
        "id":         "...",
        "created_at": "ISO-8601",
        "fields":     {...},     # the submitted form fields
        "user_agent": "...",     # context (sanitized)
        "referrer":   "...",
      }
    }

The submitter's IP-hash is NOT included; that's strictly for our
internal abuse-trace path. Webhook receivers see the fields the
visitor explicitly typed plus the page they came from.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pebble.log import log
from pebble.security import RateLimiter
from pebble.url_fetch import post_webhook


# Per-project outbound throttle. 30/min burst then 1/2s is generous
# enough that a busy form (e.g. a popular landing page) survives,
# strict enough that a misconfigured webhook URL pointing at a
# rate-limited receiver doesn't lock us out.
_webhook_deliver_limiter = RateLimiter(rate=1/2.0, burst=30)


_MAX_URL_LEN = 2048  # Conservative cap; real webhook URLs are well under this.


@dataclass
class WebhookConfig:
    url: str
    configured_at: str  # ISO-8601 UTC

    def to_dict(self) -> dict:
        return {"url": self.url, "configured_at": self.configured_at}


def _engine_output_dir() -> Path:
    """Resolve OUTPUT_DIR via the live engine module so tests can
    monkeypatch ``pebble_engine.OUTPUT_DIR`` (mirrors pebble.forms)."""
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path(__file__).parent.parent.resolve() / "output"


def _config_path(slug: str) -> Path:
    return _engine_output_dir() / slug / "forms_webhook.json"


def _is_well_formed_url(url: str) -> bool:
    """Cheap input-shape check. Does not validate that the URL is
    reachable — that's the receiver's problem. Rejects obviously bad
    inputs before they reach `post_webhook` and burn a delivery slot."""
    if not isinstance(url, str):
        return False
    url = url.strip()
    if not url or len(url) > _MAX_URL_LEN:
        return False
    return url.lower().startswith(("http://", "https://"))


def get_webhook_config(slug: str) -> Optional[WebhookConfig]:
    """Return the project's webhook config, or None if unconfigured.

    A missing or malformed config file returns None — treat as
    "not configured" rather than raising."""
    path = _config_path(slug)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    url = data.get("url")
    configured_at = data.get("configured_at") or ""
    if not _is_well_formed_url(url or ""):
        return None
    return WebhookConfig(url=url, configured_at=configured_at)


def set_webhook_config(slug: str, url: str) -> WebhookConfig:
    """Persist ``url`` as the project's webhook target. Caller is
    responsible for project-ownership auth — this function trusts the
    slug.

    Raises ``ValueError`` for malformed URLs so the HTTP layer can
    surface a 400 to the user."""
    if not _is_well_formed_url(url):
        raise ValueError("url must start with http:// or https:// and be ≤2048 chars")
    config = WebhookConfig(
        url=url.strip(),
        configured_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    path = _config_path(slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config.to_dict(), indent=2), encoding="utf-8")
    return config


def clear_webhook_config(slug: str) -> bool:
    """Remove the project's webhook config. Returns True if a config
    was deleted, False if nothing was configured."""
    path = _config_path(slug)
    if not path.exists():
        return False
    try:
        path.unlink()
        return True
    except OSError:
        return False


def deliver(slug: str, submission: dict) -> Optional[str]:
    """Fire-and-forget POST of ``submission`` to the project's
    configured webhook. Returns ``None`` on success (or skip), an
    error string on failure.

    Skips silently when:
      - no webhook configured
      - per-project rate limit exhausted

    Never raises — webhook failures must NOT break form intake."""
    config = get_webhook_config(slug)
    if config is None:
        return None  # not configured — silently skip

    if not _webhook_deliver_limiter.allow(f"webhook:{slug}"):
        log.info("webhook delivery throttled for %s", slug)
        return "throttled"

    payload = {
        "event":      "form.submitted",
        "project":    slug,
        "submission": submission,
    }
    try:
        ok, err = post_webhook(config.url, payload, timeout_sec=5.0)
    except Exception as e:
        # post_webhook should already catch everything, but defense in
        # depth: never let an exception out of here.
        log.exception("webhook delivery raised unexpectedly for %s: %s", slug, e)
        return f"{type(e).__name__}: {e}"
    if not ok:
        log.warning("webhook delivery failed for %s: %s", slug, err)
        return err
    return None


def _reset_rate_limiter_for_tests() -> None:
    """Test hook — clear the per-project bucket between tests."""
    global _webhook_deliver_limiter
    _webhook_deliver_limiter = RateLimiter(rate=1/2.0, burst=30)


__all__ = [
    "WebhookConfig",
    "get_webhook_config",
    "set_webhook_config",
    "clear_webhook_config",
    "deliver",
    "_reset_rate_limiter_for_tests",
]
