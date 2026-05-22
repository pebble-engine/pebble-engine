"""Per-project integration settings and HTML snippet rendering.

Each integration is stored in output/<slug>/integrations/<id>.json.
The combined HTML snippet is injected by the preview server (and baked
into the site at publish time) so widgets appear in the live preview
and on the published site.

Supported integrations
----------------------
- whatsapp       — fixed-position WhatsApp chat bubble
- booking        — fixed-position booking link button (Calendly, Cal.com, etc.)
- google-maps    — embedded map iframe for the business address
- social         — fixed vertical social-icon rail (Instagram, Facebook, TikTok, X, LinkedIn)
- cookie-consent — minimal GDPR cookie-consent banner
- custom-code    — raw HTML/JS snippet injected before </body>
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote

import pebble_engine  # for OUTPUT_DIR

# ---------------------------------------------------------------------------
# Catalogue
# ---------------------------------------------------------------------------

INTEGRATION_IDS = frozenset({
    "whatsapp",
    "booking",
    "google-maps",
    "social",
    "cookie-consent",
    "custom-code",
})


# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------

def _dir(slug: str) -> Path:
    return pebble_engine.OUTPUT_DIR / slug / "integrations"


def get_integrations(slug: str) -> dict[str, dict[str, Any]]:
    """Return all integrations for *slug* as ``{id: {enabled, config}}``."""
    d = _dir(slug)
    result: dict[str, dict[str, Any]] = {}
    if not d.exists():
        return result
    for f in sorted(d.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                result[f.stem] = data
        except Exception:
            pass
    return result


def save_integration(
    slug: str,
    integration_id: str,
    enabled: bool,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Persist an integration and return the saved record."""
    if integration_id not in INTEGRATION_IDS:
        raise ValueError(f"Unknown integration: {integration_id!r}")
    d = _dir(slug)
    d.mkdir(parents=True, exist_ok=True)
    data: dict[str, Any] = {"enabled": bool(enabled), "config": dict(config)}
    (d / f"{integration_id}.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return data


def delete_integration(slug: str, integration_id: str) -> bool:
    """Remove an integration file. Returns ``True`` if it existed."""
    p = _dir(slug) / f"{integration_id}.json"
    if p.exists():
        p.unlink()
        return True
    return False


# ---------------------------------------------------------------------------
# Snippet rendering
# ---------------------------------------------------------------------------

_WA_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="white">'
    '<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15'
    "-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475"
    "-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52"
    ".149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207"
    "-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372"
    "-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2"
    " 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085"
    " 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347"
    "m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648"
    "-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0"
    " 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885"
    " 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0"
    " 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448"
    "h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z\"/></svg>"
)

_SOCIAL_ICONS: dict[str, tuple[str, str]] = {
    "instagram": (
        "Instagram",
        "M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069"
        " 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919"
        " 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771"
        "-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149"
        "-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0"
        "-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073"
        " 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058"
        " 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618"
        " 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196"
        "-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0"
        "-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0"
        "-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4"
        " 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441"
        " 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z",
    ),
    "facebook": (
        "Facebook",
        "M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125"
        " 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0"
        " 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532"
        " 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z",
    ),
    "tiktok": (
        "TikTok",
        "M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7"
        " 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01"
        " 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91"
        " 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1"
        "-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48"
        "-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51"
        "-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19"
        "-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z",
    ),
    "x": (
        "X (Twitter)",
        "M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744"
        "l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z",
    ),
    "linkedin": (
        "LinkedIn",
        "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136"
        " 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37"
        "-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926"
        "-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0"
        " 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225"
        " 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2"
        " 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z",
    ),
}


def render_integration_snippet(integration_id: str, config: dict[str, Any]) -> str:
    """Return the raw HTML widget string for one integration."""

    # ---- WhatsApp ------------------------------------------------------------
    if integration_id == "whatsapp":
        phone = re.sub(r"[^0-9+]", "", str(config.get("phone", "")))
        if not phone:
            return ""
        msg = str(config.get("message", "")).strip()
        href = f"https://wa.me/{phone}"
        if msg:
            href += f"?text={quote(msg)}"
        return (
            f'<a id="pebble-whatsapp" href="{href}" target="_blank"'
            ' rel="noopener noreferrer" aria-label="Chat on WhatsApp"'
            ' style="position:fixed;bottom:24px;right:24px;z-index:9998;'
            "width:56px;height:56px;border-radius:50%;background:#25D366;"
            "display:flex;align-items:center;justify-content:center;"
            'box-shadow:0 4px 16px rgba(0,0,0,.25);text-decoration:none;">'
            + _WA_SVG
            + "</a>"
        )

    # ---- Booking -------------------------------------------------------------
    if integration_id == "booking":
        url = str(config.get("url", "")).strip()
        if not url:
            return ""
        text = str(config.get("button_text", "Book a call")).strip() or "Book a call"
        return (
            f'<a id="pebble-booking" href="{url}" target="_blank"'
            ' rel="noopener noreferrer"'
            ' style="position:fixed;bottom:24px;left:24px;z-index:9998;'
            "display:inline-flex;align-items:center;gap:8px;padding:12px 20px;"
            "background:#1F1D1A;color:#F7F3EC;border-radius:100px;"
            "font-family:inherit;font-size:14px;font-weight:600;"
            'text-decoration:none;box-shadow:0 4px 16px rgba(0,0,0,.25);">'
            f"📅 {text}</a>"
        )

    # ---- Google Maps (no-key embed) -----------------------------------------
    if integration_id == "google-maps":
        address = str(config.get("address", "")).strip()
        if not address:
            return ""
        embed_url = f"https://maps.google.com/maps?q={quote(address)}&output=embed&hl=en"
        return (
            '<div id="pebble-maps"'
            ' style="width:100%;height:320px;margin:0;padding:0;">'
            f'<iframe title="Location map" src="{embed_url}"'
            ' width="100%" height="100%" style="border:0;" allowfullscreen'
            ' loading="lazy" referrerpolicy="no-referrer-when-downgrade">'
            "</iframe></div>"
        )

    # ---- Social icons --------------------------------------------------------
    if integration_id == "social":
        icon_style = (
            "display:inline-flex;align-items:center;justify-content:center;"
            "width:40px;height:40px;border-radius:50%;background:rgba(0,0,0,.08);"
            "color:inherit;text-decoration:none;transition:background .15s;"
        )
        links: list[str] = []
        for platform, (name, path) in _SOCIAL_ICONS.items():
            url = str(config.get(platform, "")).strip()
            if url:
                links.append(
                    f'<a href="{url}" target="_blank" rel="noopener noreferrer"'
                    f' aria-label="{name}" style="{icon_style}">'
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18"'
                    f' viewBox="0 0 24 24" fill="currentColor">'
                    f'<path d="{path}"/></svg></a>'
                )
        if not links:
            return ""
        return (
            '<div id="pebble-social"'
            ' style="position:fixed;top:50%;right:16px;transform:translateY(-50%);'
            'z-index:9997;display:flex;flex-direction:column;gap:8px;">'
            + "".join(links)
            + "</div>"
        )

    # ---- Cookie consent banner -----------------------------------------------
    if integration_id == "cookie-consent":
        privacy_url = str(config.get("privacy_url", "/privacy")).strip() or "/privacy"
        msg = str(config.get("message", "We use cookies to improve your experience.")).strip()
        return (
            "<div id=\"pebble-cookie\""
            ' style="position:fixed;bottom:16px;left:50%;transform:translateX(-50%);"'
            " data-pebble-cookie>"
            '<div style="display:flex;align-items:center;gap:12px;padding:12px 20px;'
            "background:#1F1D1A;color:#F7F3EC;border-radius:100px;"
            "font-family:inherit;font-size:13px;"
            "max-width:min(600px,calc(100vw - 32px));"
            'box-shadow:0 4px 24px rgba(0,0,0,.3);z-index:9999;position:relative;">'
            f'<span>{msg}</span>'
            f'<a href="{privacy_url}"'
            ' style="color:#F7F3EC;text-decoration:underline;white-space:nowrap;">'
            "Privacy</a>"
            '<button onclick="document.querySelector(\'[data-pebble-cookie]\').remove();'
            "localStorage.setItem('pebble-cookie-ok','1')\""
            ' style="background:#F7F3EC;color:#1F1D1A;border:none;border-radius:100px;'
            "padding:6px 16px;font-size:13px;font-weight:700;cursor:pointer;"
            'white-space:nowrap;">OK</button>'
            "</div></div>"
            "<script>(function(){"
            "if(localStorage.getItem('pebble-cookie-ok')){"
            "var e=document.querySelector('[data-pebble-cookie]');"
            "if(e)e.remove()}})()</script>"
        )

    # ---- Custom code ---------------------------------------------------------
    if integration_id == "custom-code":
        return str(config.get("code", ""))

    return ""


def render_all_snippets(slug: str) -> str:
    """Render all enabled integration snippets for a slug into one HTML string."""
    integrations = get_integrations(slug)
    parts: list[str] = []
    for iid, data in integrations.items():
        if data.get("enabled") and isinstance(data.get("config"), dict):
            snippet = render_integration_snippet(iid, data["config"])
            if snippet:
                parts.append(snippet)
    return "\n".join(parts)
