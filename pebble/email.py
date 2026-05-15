"""Transactional email — pluggable sender behind a single ``send`` API.

Default in dev: ``FileSender`` writes each outgoing email as an .eml file
under ``output/.email_outbox/`` so you can read what Pebble would have
sent without standing up a mail provider. Switch via env::

    PEBBLE_EMAIL_PROVIDER=resend
    PEBBLE_EMAIL_RESEND_KEY=re_...
    PEBBLE_EMAIL_FROM=Pebble <hello@your-domain.com>

Senders share a tiny interface: a ``name`` string and ``send(message)``
returning a dict with at least ``{"ok": bool, "provider": "...", "id": "..."}``.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass, field
from email.message import EmailMessage as _StdLibEmailMessage
from pathlib import Path
from typing import Optional, Protocol


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _engine_output_dir() -> Path:
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path(__file__).parent.parent.resolve() / "output"


def _email_outbox_dir() -> Path:
    d = _engine_output_dir() / ".email_outbox"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _default_from() -> str:
    """Resolve the From address. Provider-default falls back to a Resend
    sandbox address that always works in dev."""
    return os.environ.get("PEBBLE_EMAIL_FROM", "").strip() or "Pebble <onboarding@resend.dev>"


@dataclass
class EmailMessage:
    to:        str
    subject:   str
    text:      str
    html:      Optional[str] = None
    from_addr: Optional[str] = None

    def __post_init__(self):
        if not _EMAIL_RE.match((self.to or "").strip()):
            raise EmailError(f"Invalid recipient: {self.to!r}")
        if not self.subject or not isinstance(self.subject, str):
            raise EmailError("Subject is required.")
        if not self.text or not isinstance(self.text, str):
            raise EmailError("Plain-text body is required.")
        if not self.from_addr:
            self.from_addr = _default_from()


class EmailError(Exception):
    """Validation or delivery failure."""


class EmailSender(Protocol):
    name: str
    def send(self, message: EmailMessage) -> dict: ...


# --------- FileSender (dev) -----------------------------------------------

class FileSender:
    """Persist each message as an RFC-822 .eml under ``output/.email_outbox``.

    Filename pattern: ``<UTC-timestamp>-<sanitized-to>-<sanitized-subject>.eml``.
    Returns ``{"ok": True, "provider": "log", "id": <filename>}``.
    """
    name = "log"

    def __init__(self, outbox: Optional[Path] = None) -> None:
        self._outbox = outbox

    def _outbox_dir(self) -> Path:
        return self._outbox or _email_outbox_dir()

    def send(self, message: EmailMessage) -> dict:
        ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
        slug = re.sub(r"[^a-z0-9]+", "-", f"{message.to}-{message.subject}".lower()).strip("-")[:64]
        fname = f"{ts}-{slug or 'msg'}.eml"
        msg = _StdLibEmailMessage()
        msg["From"]    = message.from_addr or _default_from()
        msg["To"]      = message.to
        msg["Subject"] = message.subject
        msg.set_content(message.text)
        if message.html:
            msg.add_alternative(message.html, subtype="html")

        path = self._outbox_dir() / fname
        path.write_bytes(bytes(msg))
        return {"ok": True, "provider": self.name, "id": fname}


# --------- ResendSender ---------------------------------------------------

class ResendSender:
    """Production sender via the Resend HTTP API.

    Reads the API key from ``PEBBLE_EMAIL_RESEND_KEY`` (preferred) or
    ``RESEND_API_KEY`` (the env var Marc's generated sites use for
    contact forms — convenient to share).
    """
    name = "resend"
    api_url = "https://api.resend.com/emails"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.environ.get("PEBBLE_EMAIL_RESEND_KEY", "").strip() \
            or os.environ.get("RESEND_API_KEY", "").strip()

    def send(self, message: EmailMessage) -> dict:
        if not self._api_key:
            raise EmailError("Resend API key missing. Set PEBBLE_EMAIL_RESEND_KEY.")
        body = {
            "from":    message.from_addr or _default_from(),
            "to":      [message.to],
            "subject": message.subject,
            "text":    message.text,
        }
        if message.html:
            body["html"] = message.html
        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type":  "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                payload = json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            raise EmailError(f"Resend HTTP {e.code}: {raw[:200]}")
        except Exception as e:
            raise EmailError(f"Resend unreachable: {e}")
        return {"ok": True, "provider": self.name, "id": payload.get("id", "")}


# --------- PostmarkSender -------------------------------------------------

class PostmarkSender:
    """Production sender via Postmark."""
    name = "postmark"
    api_url = "https://api.postmarkapp.com/email"

    def __init__(self, token: Optional[str] = None) -> None:
        self._token = token or os.environ.get("PEBBLE_EMAIL_POSTMARK_TOKEN", "").strip()

    def send(self, message: EmailMessage) -> dict:
        if not self._token:
            raise EmailError("Postmark server token missing. Set PEBBLE_EMAIL_POSTMARK_TOKEN.")
        body = {
            "From":     message.from_addr or _default_from(),
            "To":       message.to,
            "Subject":  message.subject,
            "TextBody": message.text,
        }
        if message.html:
            body["HtmlBody"] = message.html
        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Accept":                  "application/json",
                "Content-Type":            "application/json",
                "X-Postmark-Server-Token": self._token,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                payload = json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            raise EmailError(f"Postmark HTTP {e.code}: {raw[:200]}")
        except Exception as e:
            raise EmailError(f"Postmark unreachable: {e}")
        return {"ok": True, "provider": self.name, "id": payload.get("MessageID", "")}


# --------- SendgridSender -------------------------------------------------

class SendgridSender:
    """Production sender via SendGrid."""
    name = "sendgrid"
    api_url = "https://api.sendgrid.com/v3/mail/send"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.environ.get("PEBBLE_EMAIL_SENDGRID_KEY", "").strip()

    def send(self, message: EmailMessage) -> dict:
        if not self._api_key:
            raise EmailError("SendGrid API key missing. Set PEBBLE_EMAIL_SENDGRID_KEY.")
        body = {
            "personalizations": [{"to": [{"email": message.to}]}],
            "from":             {"email": _parse_addr(message.from_addr or _default_from())},
            "subject":          message.subject,
            "content":          [{"type": "text/plain", "value": message.text}],
        }
        if message.html:
            body["content"].append({"type": "text/html", "value": message.html})
        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type":  "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                # SendGrid returns 202 with empty body on success; use the
                # X-Message-Id header as the message id.
                msg_id = resp.headers.get("X-Message-Id", "")
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            raise EmailError(f"SendGrid HTTP {e.code}: {raw[:200]}")
        except Exception as e:
            raise EmailError(f"SendGrid unreachable: {e}")
        return {"ok": True, "provider": self.name, "id": msg_id}


def _parse_addr(addr: str) -> str:
    """Return the bare email from `Name <email@x>` or just `email@x`."""
    m = re.search(r"<([^>]+)>", addr)
    return m.group(1) if m else addr.strip()


# --------- Sender resolution + send() -------------------------------------

_SENDER_REGISTRY: dict[str, type] = {
    "log":      FileSender,
    "file":     FileSender,
    "resend":   ResendSender,
    "postmark": PostmarkSender,
    "sendgrid": SendgridSender,
}


def get_sender() -> EmailSender:
    """Resolve the current sender from ``PEBBLE_EMAIL_PROVIDER``.

    Unknown values fall back to ``log`` (dev sender) so a misconfigured
    prod doesn't suddenly silently drop mail — instead, files land in
    ``output/.email_outbox/`` where you can inspect them.
    """
    name = os.environ.get("PEBBLE_EMAIL_PROVIDER", "").strip().lower() or "log"
    cls = _SENDER_REGISTRY.get(name, FileSender)
    return cls()  # type: ignore[return-value]


def send(message: EmailMessage, sender: Optional[EmailSender] = None) -> dict:
    """Top-level entry point. Catches sender-level errors so callers
    don't have to. Returns ``{"ok": bool, "provider": "...", "id": "...", "error"?: "..."}``.
    """
    s = sender or get_sender()
    try:
        result = s.send(message)
        # Append a copy to the outbox even in prod so we have an audit trail.
        try:
            FileSender().send(message)
        except Exception:
            pass
        return result
    except EmailError as e:
        return {"ok": False, "provider": getattr(s, "name", "?"), "id": "", "error": str(e)}
    except Exception as e:
        return {"ok": False, "provider": getattr(s, "name", "?"), "id": "", "error": f"{type(e).__name__}: {e}"}


# --------- Pebble-specific templates --------------------------------------

def _base_url() -> str:
    """Best-effort guess at the public Pebble URL for links inside emails."""
    return os.environ.get("PEBBLE_PUBLIC_URL", "").strip().rstrip("/") or "http://localhost:3001"


def render_welcome(email: str) -> EmailMessage:
    """Welcome email after signup. Universal-design framing — never
    references age or skill level."""
    text = (
        f"Welcome to Pebble.\n\n"
        f"You're signed in as {email}. From here you can:\n\n"
        f"  • Start a site from scratch — answer 10 questions, we'll build it.\n"
        f"  • Bring an existing site over — paste the URL on the home page.\n"
        f"  • Edit anything live — click any element on the preview to change text, colors, or size.\n"
        f"  • Publish when you're ready — to Cloudflare Pages or a downloadable ZIP.\n\n"
        f"Everything is editable later. You don't have to be done.\n\n"
        f"Pebble\n"
        f"{_base_url()}\n"
    )
    html = (
        f"<p>Welcome to Pebble.</p>"
        f"<p>You're signed in as <strong>{_escape_html(email)}</strong>. From here you can:</p>"
        f"<ul>"
        f"<li>Start a site from scratch — answer 10 questions, we'll build it.</li>"
        f"<li>Bring an existing site over — paste the URL on the home page.</li>"
        f"<li>Edit anything live — click any element on the preview to change text, colors, or size.</li>"
        f"<li>Publish when you're ready — to Cloudflare Pages or a downloadable ZIP.</li>"
        f"</ul>"
        f"<p>Everything is editable later. You don't have to be done.</p>"
        f"<p>— Pebble · <a href=\"{_escape_html(_base_url())}\">{_escape_html(_base_url())}</a></p>"
    )
    return EmailMessage(to=email, subject="Welcome to Pebble", text=text, html=html)


def render_password_reset(email: str, reset_url: str) -> EmailMessage:
    """One-time reset link. Clear, no marketing."""
    text = (
        f"Someone (hopefully you) asked to reset the password for your Pebble account.\n\n"
        f"Click this link to set a new password:\n"
        f"  {reset_url}\n\n"
        f"The link is good for 1 hour. If you didn't request this, you can\n"
        f"safely ignore this email — your password won't change.\n\n"
        f"Pebble\n"
    )
    html = (
        f"<p>Someone (hopefully you) asked to reset the password for your Pebble account.</p>"
        f"<p><a href=\"{_escape_html(reset_url)}\" style=\"background:#1F1D1A;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:600\">Set a new password</a></p>"
        f"<p style=\"font-size:13px;color:#666\">Or paste this link into your browser: <code>{_escape_html(reset_url)}</code></p>"
        f"<p style=\"font-size:13px;color:#666\">The link is good for 1 hour. If you didn't request this, you can safely ignore this email — your password won't change.</p>"
        f"<p>— Pebble</p>"
    )
    return EmailMessage(to=email, subject="Reset your Pebble password", text=text, html=html)


def _escape_html(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# --------- Convenience wrappers -------------------------------------------

def send_welcome(email: str, sender: Optional[EmailSender] = None) -> dict:
    return send(render_welcome(email), sender=sender)


def send_password_reset(email: str, reset_url: str, sender: Optional[EmailSender] = None) -> dict:
    return send(render_password_reset(email, reset_url), sender=sender)


__all__ = [
    "EmailError",
    "EmailMessage",
    "EmailSender",
    "FileSender",
    "ResendSender",
    "PostmarkSender",
    "SendgridSender",
    "get_sender",
    "send",
    "send_welcome",
    "send_password_reset",
    "render_welcome",
    "render_password_reset",
]
