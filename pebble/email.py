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
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from email.message import EmailMessage as _StdLibEmailMessage
from pathlib import Path
from typing import Optional, Protocol


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# All outbound API calls need a real User-Agent — vendors fronting their
# APIs with Cloudflare (Resend in particular) block the default
# "Python-urllib/3.x" UA at the WAF and return HTTP 403 / error 1010.
PEBBLE_UA = "PebbleEngine/1.0 (+https://pebbleapp.ai)"


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
                "User-Agent":    PEBBLE_UA,
                "Accept":        "application/json",
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
                "User-Agent":              PEBBLE_UA,
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
                "User-Agent":    PEBBLE_UA,
                "Accept":        "application/json",
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

    The FileSender audit-copy is written regardless of whether the
    primary sender succeeded — if Resend rejects the message, we still
    want the .eml on disk to debug from. The 2026-05-15 NLM pass flagged
    that the previous "audit-copy lives inside the prod-sender try"
    layout caused silent audit-trail loss whenever the prod sender
    raised (which is exactly when the audit trail matters most).
    """
    s = sender or get_sender()
    try:
        result = s.send(message)
    except EmailError as e:
        result = {"ok": False, "provider": getattr(s, "name", "?"), "id": "", "error": str(e)}
    except Exception as e:
        result = {"ok": False, "provider": getattr(s, "name", "?"), "id": "", "error": f"{type(e).__name__}: {e}"}

    # Audit copy ALWAYS, even when the prod sender errored. Skip when
    # the primary sender IS FileSender (would write the same file twice
    # to the same outbox path with the same timestamp prefix — racy and
    # noisy).
    if not isinstance(s, FileSender):
        try:
            FileSender().send(message)
        except Exception:
            pass
    return result


# Shared thread pool for fire-and-forget sends. Two workers is plenty —
# this isn't a high-volume mail server, just decouples HTTP response
# timing from network round-trips. NotebookLM flagged constant-time HTTP
# responses as the right defense against timing-attack account
# enumeration on /api/auth/forgot.
_EMAIL_POOL: Optional[ThreadPoolExecutor] = None


def _email_pool() -> ThreadPoolExecutor:
    global _EMAIL_POOL
    if _EMAIL_POOL is None:
        _EMAIL_POOL = ThreadPoolExecutor(max_workers=2, thread_name_prefix="pebble-mail")
    return _EMAIL_POOL


def send_async(message: EmailMessage, sender: Optional[EmailSender] = None) -> "Future[dict]":
    """Queue ``message`` for delivery on a background worker. The HTTP
    handler returns immediately regardless of how long the actual send
    takes — closes the timing-attack window on /api/auth/forgot.

    Tests can await the future to make synchronous assertions on what
    landed in the outbox.
    """
    return _email_pool().submit(send, message, sender)


# --------- Pebble-specific templates --------------------------------------

def _base_url() -> str:
    """Best-effort guess at the public Pebble URL for links inside emails."""
    return os.environ.get("PEBBLE_PUBLIC_URL", "").strip().rstrip("/") or "http://localhost:3001"


def render_welcome(email: str, first_name: Optional[str] = None) -> EmailMessage:
    """Welcome email after signup. Universal-design framing — never
    references age or skill level. ``first_name`` is pulled from
    ``auth.users.raw_user_meta_data.first_name`` by the Supabase webhook
    handler; for OAuth signups Google/GitHub populates it automatically.
    When absent (rare — webhook fires before profile trigger somehow),
    we fall back to "there" rather than addressing the user as None.

    The HTML uses table layout + inline styles because that's what
    Gmail / Outlook / Apple Mail will reliably render — modern flex/grid
    layouts get stripped or break across clients."""
    name = (first_name or "").strip() or "there"
    base = _base_url()
    start_url = f"{base}/workspace"
    return EmailMessage(
        to=email,
        subject=f"Welcome to Pebble, {name}",
        text=_welcome_text(name, start_url, base),
        html=_welcome_html(name, start_url, base),
    )


def _welcome_text(name: str, start_url: str, base: str) -> str:
    return (
        f"Welcome to Pebble, {name}.\n\n"
        f"Thank you for signing up. We're excited to help you bring your idea "
        f"to life and get your website online — without writing a single line of code.\n\n"
        f"When you're ready, start building here:\n"
        f"  {start_url}\n\n"
        f"What you can do next:\n"
        f"  - Describe your business in plain English — we'll pick the structure\n"
        f"  - Bring an existing site over by pasting its URL\n"
        f"  - Refine colors, fonts, and copy by clicking any element on the preview\n"
        f"  - Publish to a free Pebble URL or your own custom domain\n\n"
        f"— The Pebble Team\n"
        f"Building websites should feel like building anything else you're proud of.\n\n"
        f"You're receiving this because you created a Pebble account.\n"
        f"Visit Pebble: {base}/landing\n"
    )


def _welcome_html(name: str, start_url: str, base: str) -> str:
    name_e = _escape_html(name)
    start_e = _escape_html(start_url)
    base_e = _escape_html(base)
    # The whole template is one big string to keep this file readable —
    # email HTML is awful but deterministic. Notes on the rules:
    #   • Outer table is the centering scaffold (max-width 600px, the
    #     web-mail "safe" width that doesn't get scaled in Gmail mobile).
    #   • Every cell uses inline style — Gmail strips <style> blocks.
    #   • Fonts use system-stack with serif fallback for the wordmark.
    #   • Colours match the Pebble brand: warm-cream surface, charcoal
    #     ink, pebble-grey muted. No accent colour in the body so the
    #     CTA button is the visual anchor.
    return (
        '<!doctype html><html><head>'
        '<meta charset="UTF-8"/>'
        '<meta name="viewport" content="width=device-width,initial-scale=1"/>'
        f'<title>Welcome to Pebble, {name_e}</title>'
        '</head>'
        '<body style="margin:0;padding:0;background:#F7F3EC;'
        'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Helvetica,Arial,sans-serif;'
        'color:#1F1D1A;-webkit-font-smoothing:antialiased;">'
        '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:#F7F3EC;">'
        '<tr><td align="center" style="padding:40px 16px;">'
        '<table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" '
        'style="max-width:600px;width:100%;background:#FFFFFF;border-radius:16px;'
        'overflow:hidden;border:1px solid #ECE6DC;">'
        # Wordmark
        '<tr><td align="center" style="padding:44px 40px 8px 40px;">'
        '<span style="font-family:Georgia,\'Times New Roman\',serif;font-size:34px;'
        'font-weight:700;letter-spacing:-0.02em;color:#1F1D1A;">Pebble.</span>'
        '</td></tr>'
        # Headline
        '<tr><td style="padding:24px 40px 16px 40px;">'
        f'<h1 style="margin:0;font-family:Georgia,serif;font-size:26px;line-height:1.25;'
        f'font-weight:700;color:#1F1D1A;">Welcome to Pebble, {name_e}.</h1>'
        '</td></tr>'
        # Body
        '<tr><td style="padding:0 40px 28px 40px;font-size:16px;line-height:1.6;color:#44423E;">'
        '<p style="margin:0 0 16px 0;">Thank you for signing up. We\'re excited to help you '
        'bring your idea to life and get your website online — without writing a single line of code.</p>'
        '<p style="margin:0;">When you\'re ready, click below and we\'ll walk you through your first build.</p>'
        '</td></tr>'
        # CTA
        '<tr><td align="center" style="padding:8px 40px 40px 40px;">'
        f'<a href="{start_e}" style="display:inline-block;background:#1F1D1A;color:#F7F3EC;'
        f'font-size:15px;font-weight:600;text-decoration:none;padding:14px 30px;'
        f'border-radius:999px;letter-spacing:0.01em;">Start building &rarr;</a>'
        '</td></tr>'
        # "What you can do next"
        '<tr><td style="padding:0 40px 0 40px;border-top:1px solid #ECE6DC;">'
        '<p style="margin:28px 0 14px 0;font-size:11px;font-weight:700;'
        'text-transform:uppercase;letter-spacing:0.1em;color:#757470;">What you can do next</p>'
        '<ul style="margin:0 0 28px 0;padding:0 0 0 18px;font-size:14px;line-height:1.7;color:#44423E;">'
        '<li>Describe your business in plain English &mdash; we\'ll pick the structure</li>'
        '<li>Bring an existing site over by pasting its URL</li>'
        '<li>Refine colors, fonts, and copy by clicking any element on the preview</li>'
        '<li>Publish to a free Pebble URL or your own custom domain</li>'
        '</ul>'
        '</td></tr>'
        # Signature
        '<tr><td style="padding:8px 40px 32px 40px;text-align:center;border-top:1px solid #ECE6DC;">'
        '<p style="margin:24px 0 6px 0;font-family:Georgia,serif;font-size:16px;'
        'font-weight:700;color:#1F1D1A;">The Pebble Team</p>'
        '<p style="margin:0;font-size:13px;color:#757470;font-style:italic;">'
        'Building websites should feel like building anything else you\'re proud of.</p>'
        '</td></tr>'
        '</table>'
        # Outer footer (legal-ish, outside the card)
        '<table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" '
        'style="max-width:600px;width:100%;margin-top:16px;">'
        '<tr><td align="center" style="padding:16px;font-size:11px;line-height:1.6;color:#999895;">'
        'You\'re receiving this because you created a Pebble account.<br/>'
        f'<a href="{base_e}/landing" style="color:#999895;text-decoration:underline;">Visit Pebble</a>'
        '</td></tr>'
        '</table>'
        '</td></tr></table>'
        '</body></html>'
    )


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

def send_welcome(email: str, first_name: Optional[str] = None, sender: Optional[EmailSender] = None) -> dict:
    return send(render_welcome(email, first_name=first_name), sender=sender)


def send_welcome_async(email: str, first_name: Optional[str] = None, sender: Optional[EmailSender] = None) -> "Future[dict]":
    return send_async(render_welcome(email, first_name=first_name), sender=sender)


def send_password_reset(email: str, reset_url: str, sender: Optional[EmailSender] = None) -> dict:
    return send(render_password_reset(email, reset_url), sender=sender)


def send_password_reset_async(email: str, reset_url: str, sender: Optional[EmailSender] = None) -> "Future[dict]":
    return send_async(render_password_reset(email, reset_url), sender=sender)


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
    "send_async",
    "send_welcome",
    "send_welcome_async",
    "send_password_reset",
    "send_password_reset_async",
    "render_welcome",
    "render_password_reset",
    # Shared rendering utilities used by sibling email modules.
    "_engine_output_dir",
    "_base_url",
    "_escape_html",
]
