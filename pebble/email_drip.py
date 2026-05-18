"""Post-first-build email drip — Chapter 11.6.

Sends 3 emails to authenticated users after their first Pebble build:

  Day +1  tips_next    "Your site is ready — here's what to do first"
  Day +3  tips_refine  "3 quick wins for your Pebble site"
  Day +7  tips_live    "Ready to take your site live?"

Storage per user:
  output/.users/<uid>/email_drip.json
  {
    "email": "...", "first_name": "...", "slug": "...",
    "scheduled_at": "<ISO>",
    "scheduled": [
      {"day": 1, "type": "tips_next",   "send_at": "<ISO>", "sent_at": null},
      {"day": 3, "type": "tips_refine", "send_at": "<ISO>", "sent_at": null},
      {"day": 7, "type": "tips_live",   "send_at": "<ISO>", "sent_at": null}
    ]
  }

schedule_drip() is idempotent — if the file already exists the call is a
no-op. This guarantees only the FIRST successful build schedules the drip;
rebuilds and repairs do not reset the clock.

process_due() scans every output/.users/<uid>/email_drip.json, fires any
email whose send_at is in the past and sent_at is null, then updates the
file atomically. Called by GET /api/internal/process-email-drip (gated by
PEBBLE_INTERNAL_KEY) which a Windows scheduled task hits hourly.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import uuid
from pathlib import Path
from typing import Optional

from pebble.email import EmailMessage, _base_url, _engine_output_dir, _escape_html, send
from pebble.log import log
from pebble.security import safe_user_id


def _atomic_write(path: Path, data: dict) -> None:
    tmp = path.parent / f"_{uuid.uuid4().hex}.tmp"
    try:
        tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        tmp.replace(path)
    except Exception:
        try:
            tmp.unlink(missing_ok=True)
        except Exception:
            pass
        raise


def _drip_delays() -> tuple[int, int, int]:
    """Day offsets. Override via PEBBLE_DRIP_DAYS_1/_3/_7 for testing."""
    d1 = int(os.environ.get("PEBBLE_DRIP_DAYS_1", "1"))
    d3 = int(os.environ.get("PEBBLE_DRIP_DAYS_3", "3"))
    d7 = int(os.environ.get("PEBBLE_DRIP_DAYS_7", "7"))
    return d1, d3, d7


# ---------------------------------------------------------------------------
# schedule_drip — call once at the end of a successful /api/generate
# ---------------------------------------------------------------------------

def schedule_drip(
    user_id: str,
    email: str,
    *,
    first_name: Optional[str] = None,
    slug: str = "",
    output_dir: Optional[Path] = None,
) -> bool:
    """Schedule the post-first-build drip for user_id.

    Returns True if the drip was newly written, False if it already existed
    (idempotent — only the first build schedules the drip).
    """
    uid = safe_user_id(user_id)
    if not uid:
        return False
    if not email or "@" not in email:
        return False

    out = output_dir or _engine_output_dir()
    user_dir = out / ".users" / uid
    drip_file = user_dir / "email_drip.json"

    if drip_file.exists():
        return False

    user_dir.mkdir(parents=True, exist_ok=True)

    now = _dt.datetime.now(_dt.timezone.utc)
    d1, d3, d7 = _drip_delays()
    data = {
        "email": email,
        "first_name": (first_name or "").strip(),
        "slug": slug,
        "scheduled_at": now.isoformat(),
        "scheduled": [
            {
                "day": d1,
                "type": "tips_next",
                "send_at": (now + _dt.timedelta(days=d1)).isoformat(),
                "sent_at": None,
            },
            {
                "day": d3,
                "type": "tips_refine",
                "send_at": (now + _dt.timedelta(days=d3)).isoformat(),
                "sent_at": None,
            },
            {
                "day": d7,
                "type": "tips_live",
                "send_at": (now + _dt.timedelta(days=d7)).isoformat(),
                "sent_at": None,
            },
        ],
    }
    _atomic_write(drip_file, data)
    log.info("drip: scheduled 3 emails for %s (slug=%s)", uid, slug or "(none)")
    return True


# ---------------------------------------------------------------------------
# process_due — call hourly from /api/internal/process-email-drip
# ---------------------------------------------------------------------------

def process_due(output_dir: Optional[Path] = None) -> dict:
    """Scan all output/.users/<uid>/email_drip.json files and send any
    emails whose send_at is in the past and sent_at is null.

    Returns {"sent": int, "skipped": int, "errors": list[str]}.
    """
    out = output_dir or _engine_output_dir()
    users_dir = out / ".users"
    if not users_dir.exists():
        return {"sent": 0, "skipped": 0, "errors": []}

    sent = 0
    skipped = 0
    errors: list[str] = []
    now = _dt.datetime.now(_dt.timezone.utc)

    for uid_dir in users_dir.iterdir():
        if not uid_dir.is_dir():
            continue
        drip_file = uid_dir / "email_drip.json"
        if not drip_file.exists():
            continue

        try:
            data = json.loads(drip_file.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{uid_dir.name}: read error: {exc}")
            continue

        email = (data.get("email") or "").strip()
        if not email or "@" not in email:
            continue

        first_name = (data.get("first_name") or "").strip() or None
        slug = (data.get("slug") or "").strip()
        modified = False

        for item in data.get("scheduled", []):
            if item.get("sent_at"):
                skipped += 1
                continue
            send_at_str = item.get("send_at", "")
            if not send_at_str:
                continue
            try:
                send_at = _dt.datetime.fromisoformat(send_at_str)
                if send_at.tzinfo is None:
                    send_at = send_at.replace(tzinfo=_dt.timezone.utc)
            except ValueError:
                continue
            if now < send_at:
                skipped += 1
                continue

            # Due — fire the email.
            try:
                msg = _render(item["type"], email, first_name, slug)
                result = send(msg)
                if result.get("ok"):
                    item["sent_at"] = now.isoformat()
                    modified = True
                    sent += 1
                    log.info(
                        "drip: sent %s to %s... (provider=%s)",
                        item["type"], email[:4], result.get("provider"),
                    )
                else:
                    errors.append(
                        f"{uid_dir.name}/{item['type']}: send failed: {result.get('error')}"
                    )
            except Exception as exc:
                errors.append(f"{uid_dir.name}/{item['type']}: {type(exc).__name__}: {exc}")

        if modified:
            try:
                _atomic_write(drip_file, data)
            except Exception as exc:
                errors.append(f"{uid_dir.name}: write failed: {exc}")

    return {"sent": sent, "skipped": skipped, "errors": errors}


# ---------------------------------------------------------------------------
# Email renderers
# ---------------------------------------------------------------------------

def _render(
    email_type: str,
    email: str,
    first_name: Optional[str],
    slug: str,
) -> EmailMessage:
    name = (first_name or "").strip() or "there"
    base = _base_url()
    workspace_url = f"{base}/workspace" + (f"?slug={slug}" if slug else "")
    if email_type == "tips_next":
        return _render_tips_next(email, name, workspace_url, base)
    if email_type == "tips_refine":
        return _render_tips_refine(email, name, workspace_url, base)
    if email_type == "tips_live":
        return _render_tips_live(email, name, workspace_url, base)
    raise ValueError(f"unknown drip email type: {email_type!r}")


# ---- Day +1 ----------------------------------------------------------------

def _render_tips_next(email: str, name: str, workspace_url: str, base: str) -> EmailMessage:
    subject = "Your Pebble site is ready — here's what to do first"
    text = (
        f"Hi {name},\n\n"
        f"Your site is live in your Pebble workspace — great work getting that first build done.\n\n"
        f"Three things worth doing in the next few minutes:\n\n"
        f"  1. Share it with someone you trust.\n"
        f"     Send them the preview link and ask: does this look like my business?\n\n"
        f"  2. Click any text on the preview to edit it.\n"
        f"     Your headline, tagline, contact details — all clickable, all editable.\n\n"
        f"  3. Check that your phone number and address are right.\n"
        f"     Visitors will call and navigate by whatever's on the site.\n\n"
        f"Open your site here:\n"
        f"  {workspace_url}\n\n"
        f"— The Pebble Team\n"
        f"Questions? Reply to this email and we'll help.\n"
    )
    html = _drip_html(
        to=email,
        name=name,
        subject=subject,
        headline=f"Your site is ready, {_escape_html(name)}.",
        body_html=(
            "<p>Your site is live in your Pebble workspace — great work getting "
            "that first build done.</p>"
            "<p style='margin:0 0 8px 0;font-weight:700;'>Three things worth doing now:</p>"
            "<ol style='margin:0 0 20px 0;padding:0 0 0 18px;font-size:15px;line-height:1.7;color:#44423E;'>"
            "<li><strong>Share it with someone you trust</strong> — send them the preview link "
            "and ask: does this look like my business?</li>"
            "<li><strong>Click any text to edit it</strong> — your headline, tagline, and "
            "contact details are all clickable.</li>"
            "<li><strong>Check your phone number and address</strong> — visitors will call "
            "and navigate by whatever's on the site.</li>"
            "</ol>"
        ),
        cta_url=workspace_url,
        cta_label="Open your site &rarr;",
        base=base,
    )
    return EmailMessage(to=email, subject=subject, text=text, html=html)


# ---- Day +3 ----------------------------------------------------------------

def _render_tips_refine(email: str, name: str, workspace_url: str, base: str) -> EmailMessage:
    subject = "3 quick wins for your Pebble site"
    text = (
        f"Hi {name},\n\n"
        f"A few easy ways to make your site feel more like you:\n\n"
        f"  1. Swap the color palette.\n"
        f"     Hit Refine → Colors in the editor — takes one click.\n\n"
        f"  2. Make the headline sound like you.\n"
        f"     Click the big text at the top of your site and retype it\n"
        f"     in your own words.\n\n"
        f"  3. Add a booking link or menu.\n"
        f"     If you take appointments or have a menu/price list, paste\n"
        f"     the link into your contact section.\n\n"
        f"Open your site here:\n"
        f"  {workspace_url}\n\n"
        f"— The Pebble Team\n"
    )
    html = _drip_html(
        to=email,
        name=name,
        subject=subject,
        headline="3 quick wins for your site.",
        body_html=(
            "<p>A few easy ways to make your site feel more like you:</p>"
            "<ol style='margin:0 0 20px 0;padding:0 0 0 18px;font-size:15px;line-height:1.7;color:#44423E;'>"
            "<li><strong>Swap the color palette</strong> — hit Refine &rarr; Colors in the "
            "editor. Takes one click.</li>"
            "<li><strong>Make the headline sound like you</strong> — click the big text at "
            "the top of your site and retype it in your own words.</li>"
            "<li><strong>Add a booking link or menu</strong> — if you take appointments "
            "or have a price list, paste the link into your contact section.</li>"
            "</ol>"
        ),
        cta_url=workspace_url,
        cta_label="Polish your site &rarr;",
        base=base,
    )
    return EmailMessage(to=email, subject=subject, text=text, html=html)


# ---- Day +7 ----------------------------------------------------------------

def _render_tips_live(email: str, name: str, workspace_url: str, base: str) -> EmailMessage:
    subject = "Ready to take your Pebble site live?"
    text = (
        f"Hi {name},\n\n"
        f"Your site has been in your workspace for a week. If you're happy with it,\n"
        f"now is a great time to take it live.\n\n"
        f"What going live means:\n\n"
        f"  • Your site gets a free Pebble address (yourname.pebble.app)\n"
        f"  • You can also connect a domain you already own — like yourname.com\n"
        f"  • Setup takes about 5 minutes\n\n"
        f"When you're ready, open your workspace and hit Publish:\n"
        f"  {workspace_url}\n\n"
        f"Not ready yet? No rush — your site stays safely saved in your account.\n\n"
        f"— The Pebble Team\n"
    )
    html = _drip_html(
        to=email,
        name=name,
        subject=subject,
        headline="Ready to go live?",
        body_html=(
            "<p>Your site has been in your workspace for a week. If you're happy with it, "
            "now's a great time to take it live.</p>"
            "<ul style='margin:0 0 20px 0;padding:0 0 0 18px;font-size:15px;line-height:1.7;color:#44423E;'>"
            "<li>Your site gets a <strong>free Pebble address</strong> (yourname.pebble.app)</li>"
            "<li>You can also <strong>connect a domain you already own</strong> — like yourname.com</li>"
            "<li>Setup takes about <strong>5 minutes</strong></li>"
            "</ul>"
            "<p style='font-size:14px;color:#757470;'>Not ready yet? No rush — your site stays safely "
            "saved in your account.</p>"
        ),
        cta_url=workspace_url,
        cta_label="Publish my site &rarr;",
        base=base,
    )
    return EmailMessage(to=email, subject=subject, text=text, html=html)


# ---------------------------------------------------------------------------
# Shared HTML scaffold (matches welcome email brand: cream/charcoal/serif)
# ---------------------------------------------------------------------------

def _drip_html(
    *,
    to: str,
    name: str,
    subject: str,
    headline: str,
    body_html: str,
    cta_url: str,
    cta_label: str,
    base: str,
) -> str:
    name_e = _escape_html(name)
    headline_e = _escape_html(headline)
    cta_e = _escape_html(cta_url)
    base_e = _escape_html(base)
    return (
        "<!doctype html><html><head>"
        '<meta charset="UTF-8"/>'
        '<meta name="viewport" content="width=device-width,initial-scale=1"/>'
        f"<title>{_escape_html(subject)}</title>"
        "</head>"
        '<body style="margin:0;padding:0;background:#F7F3EC;'
        "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;"
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
        "</td></tr>"
        # Headline
        '<tr><td style="padding:24px 40px 16px 40px;">'
        f'<h1 style="margin:0;font-family:Georgia,serif;font-size:26px;line-height:1.25;'
        f'font-weight:700;color:#1F1D1A;">{headline_e}</h1>'
        "</td></tr>"
        # Body HTML
        f'<tr><td style="padding:0 40px 28px 40px;font-size:15px;line-height:1.6;color:#44423E;">'
        f"{body_html}"
        "</td></tr>"
        # CTA
        '<tr><td align="center" style="padding:8px 40px 40px 40px;">'
        f'<a href="{cta_e}" style="display:inline-block;background:#1F1D1A;color:#F7F3EC;'
        f"font-size:15px;font-weight:600;text-decoration:none;padding:14px 30px;"
        f'border-radius:999px;letter-spacing:0.01em;">{cta_label}</a>'
        "</td></tr>"
        # Footer
        '<tr><td style="padding:8px 40px 32px 40px;text-align:center;border-top:1px solid #ECE6DC;">'
        '<p style="margin:24px 0 6px 0;font-family:Georgia,serif;font-size:16px;'
        'font-weight:700;color:#1F1D1A;">The Pebble Team</p>'
        '<p style="margin:0;font-size:13px;color:#757470;font-style:italic;">'
        "Questions? Reply to this email — we read every one.</p>"
        "</td></tr>"
        "</table>"
        # Outer footer
        '<table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" '
        'style="max-width:600px;width:100%;margin-top:16px;">'
        '<tr><td align="center" style="padding:16px;font-size:11px;line-height:1.6;color:#999895;">'
        f"You're receiving this because you built a site with Pebble.<br/>"
        f'<a href="{base_e}" style="color:#999895;text-decoration:underline;">Visit Pebble</a>'
        "</td></tr>"
        "</table>"
        "</td></tr></table>"
        "</body></html>"
    )


__all__ = [
    "schedule_drip",
    "process_due",
]
