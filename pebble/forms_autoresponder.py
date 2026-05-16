"""Auto-responder email for form-inbox submissions.

When the project owner opts in, every form submission that includes an
email address triggers an automatic branded thank-you sent back to the
submitter. Closes the "did my message get through?" anxiety loop every
service-business owner mentions.

Storage: ``output/<slug>/forms_autoresponder.json`` holds the config.
Absent file = autoresponder disabled. Opt-in only — Pebble never sends
email on a customer's behalf without explicit configuration.

Templating: `{{ field_name }}` placeholders in the subject and body are
filled from the submission's fields dict. Unknown fields render as an
empty string (no leaking of `{{name}}` to the visitor). The visitor's
email address is the recipient — pulled from a configurable field name
(default `"email"`, case-insensitive match).

Privacy + abuse posture:
- Disabled by default. The owner must explicitly enable.
- Per-recipient rate limit (1/hour) prevents resubmission floods from
  becoming inbox-spam for the visitor.
- Subject + body are user-content from the project owner; we DO NOT
  scrub HTML/markdown, the visitor sees what the owner wrote. The
  owner is the trust boundary here, not Pebble.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pebble.email import EmailError, EmailMessage, send_async
from pebble.log import log
from pebble.security import RateLimiter


# Per-recipient throttle — at most 1 autoresponse per email per hour.
# Prevents one form-submitter from accidentally (or maliciously) being
# emailed dozens of times by resubmitting.
_autoresponder_limiter = RateLimiter(rate=1/3600.0, burst=1)


# Sane upper bounds — these end up rendered as the visitor's first
# impression of the brand, so we cap rather than truncate silently
# (the HTTP layer surfaces a 400).
_MAX_SUBJECT_LEN = 200
_MAX_BODY_LEN    = 8 * 1024
_PLACEHOLDER_RE  = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")
_EMAIL_RE        = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


DEFAULT_SUBJECT = "Thanks for reaching out"
DEFAULT_BODY = (
    "Hi {{ name }},\n"
    "\n"
    "Thanks for getting in touch! We received your message and will "
    "be back in touch with you shortly.\n"
    "\n"
    "If you need to reach us sooner, just reply to this email.\n"
    "\n"
    "Talk soon.\n"
)
DEFAULT_REPLY_FIELD = "email"


@dataclass
class AutoresponderConfig:
    enabled:        bool
    subject:        str
    body:           str
    reply_field:    str
    configured_at:  str  # ISO-8601 UTC

    def to_dict(self) -> dict:
        return {
            "enabled":       self.enabled,
            "subject":       self.subject,
            "body":          self.body,
            "reply_field":   self.reply_field,
            "configured_at": self.configured_at,
        }


def default_config() -> AutoresponderConfig:
    return AutoresponderConfig(
        enabled=False,
        subject=DEFAULT_SUBJECT,
        body=DEFAULT_BODY,
        reply_field=DEFAULT_REPLY_FIELD,
        configured_at="",
    )


def _engine_output_dir() -> Path:
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path(__file__).parent.parent.resolve() / "output"


def _config_path(slug: str) -> Path:
    return _engine_output_dir() / slug / "forms_autoresponder.json"


def get_config(slug: str) -> AutoresponderConfig:
    """Return the project's autoresponder config, or the default
    (disabled) when unconfigured or malformed."""
    path = _config_path(slug)
    if not path.exists():
        return default_config()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default_config()
    return AutoresponderConfig(
        enabled=bool(data.get("enabled", False)),
        subject=str(data.get("subject") or DEFAULT_SUBJECT)[:_MAX_SUBJECT_LEN],
        body=str(data.get("body") or DEFAULT_BODY)[:_MAX_BODY_LEN],
        reply_field=str(data.get("reply_field") or DEFAULT_REPLY_FIELD),
        configured_at=str(data.get("configured_at") or ""),
    )


def set_config(
    slug: str,
    *,
    enabled: bool,
    subject: Optional[str] = None,
    body: Optional[str] = None,
    reply_field: Optional[str] = None,
) -> AutoresponderConfig:
    """Persist the project's autoresponder config. Any None fields fall
    back to the current value (or the default if unconfigured). Validates
    subject/body length; raises ValueError on overflow."""
    current = get_config(slug)
    if subject is not None and len(subject) > _MAX_SUBJECT_LEN:
        raise ValueError(f"subject exceeds {_MAX_SUBJECT_LEN} chars")
    if body is not None and len(body) > _MAX_BODY_LEN:
        raise ValueError(f"body exceeds {_MAX_BODY_LEN} chars")
    if reply_field is not None and not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", reply_field):
        raise ValueError("reply_field must be a valid identifier (letters/digits/underscores)")

    config = AutoresponderConfig(
        enabled=bool(enabled),
        subject=subject if subject is not None else current.subject,
        body=body if body is not None else current.body,
        reply_field=reply_field if reply_field is not None else current.reply_field,
        configured_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    path = _config_path(slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config.to_dict(), indent=2), encoding="utf-8")
    return config


def clear_config(slug: str) -> bool:
    """Remove the project's autoresponder config. Returns True if a
    config was deleted, False if nothing was configured."""
    path = _config_path(slug)
    if not path.exists():
        return False
    try:
        path.unlink()
        return True
    except OSError:
        return False


def _render(template: str, fields: dict) -> str:
    """Replace `{{ name }}` placeholders. Unknown placeholders become
    the empty string (never leak the template syntax to the visitor)."""
    def replace(match: re.Match) -> str:
        key = match.group(1)
        val = fields.get(key)
        if val is None:
            # Case-insensitive fallback so {{ Email }} also works.
            for k, v in fields.items():
                if isinstance(k, str) and k.lower() == key.lower():
                    val = v
                    break
        if val is None:
            return ""
        return str(val)
    return _PLACEHOLDER_RE.sub(replace, template)


def _lookup_email(fields: dict, reply_field: str) -> Optional[str]:
    """Find the visitor's email in the submission. Exact match on
    reply_field first, then case-insensitive search."""
    if not isinstance(fields, dict):
        return None
    if reply_field in fields:
        v = fields[reply_field]
        return v.strip() if isinstance(v, str) else None
    for k, v in fields.items():
        if isinstance(k, str) and k.lower() == reply_field.lower():
            return v.strip() if isinstance(v, str) else None
    return None


def send_autoresponse(slug: str, submission: dict) -> Optional[str]:
    """Send the configured autoresponse to the visitor. Returns:
      - None on success or deliberate skip (not enabled, no email field)
      - error string on validation/delivery failure

    Never raises — like the webhook deliverer, the inbox is the source
    of truth and a failed autoresponse must not break form intake."""
    config = get_config(slug)
    if not config.enabled:
        return None  # opt-out — silent skip

    fields = submission.get("fields") or {}
    if not isinstance(fields, dict):
        return None

    recipient = _lookup_email(fields, config.reply_field)
    if not recipient or not _EMAIL_RE.match(recipient):
        # No valid email to respond to — skip silently. Owners often
        # have forms WITHOUT an email field (RSVP, satisfaction
        # survey), and triggering an error there would be noise.
        return None

    if not _autoresponder_limiter.allow(f"autoresp:{recipient.lower()}"):
        log.info("autoresponse throttled for %s (recipient cooldown)",
                 _redact(recipient))
        return "throttled"

    subject = _render(config.subject, fields) or DEFAULT_SUBJECT
    body    = _render(config.body, fields)

    try:
        message = EmailMessage(to=recipient, subject=subject, text=body)
    except EmailError as e:
        log.warning("autoresponse refused for %s/%s: %s",
                    slug, _redact(recipient), e)
        return str(e)

    try:
        send_async(message)
    except Exception as e:
        log.exception("autoresponse async enqueue failed for %s: %s", slug, e)
        return f"{type(e).__name__}: {e}"
    return None


def _redact(email: str) -> str:
    """`marc@example.com` → `m***@example.com` for log lines."""
    if "@" not in email:
        return "?"
    local, _, domain = email.partition("@")
    return f"{local[:1]}***@{domain}" if local else f"***@{domain}"


def _reset_rate_limiter_for_tests() -> None:
    global _autoresponder_limiter
    _autoresponder_limiter = RateLimiter(rate=1/3600.0, burst=1)


__all__ = [
    "AutoresponderConfig",
    "DEFAULT_SUBJECT",
    "DEFAULT_BODY",
    "DEFAULT_REPLY_FIELD",
    "default_config",
    "get_config",
    "set_config",
    "clear_config",
    "send_autoresponse",
    "_reset_rate_limiter_for_tests",
]
