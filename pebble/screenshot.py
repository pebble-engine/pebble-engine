"""Capture a card thumbnail via Cloudflare Browser Rendering.

The dashboard ProjectCard shows ``output/<slug>/screenshots/01-hero.png`` when
present (else a DNA-color gradient). Playwright can't run on the Node-less
Railway engine, so prod cards are always gradients. Once a build has a live URL
(its Vercel preview), Cloudflare Browser Rendering screenshots it server-side
(REST, pure Python) and we write the PNG to that existing path — the card lights
up with no card-side changes.

Reuses the Cloudflare creds already used for publish. NOTE: the API token needs
the **Browser Rendering – Edit** permission (one-time, in the token's settings).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import httpx

_CF = "https://api.cloudflare.com/client/v4"


def configured() -> bool:
    return bool(
        os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
        and os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    )


def capture_to_png(url: str, *, timeout: float = 60.0) -> bytes:
    """POST the URL to Cloudflare Browser Rendering; return PNG bytes."""
    acc = os.environ["CLOUDFLARE_ACCOUNT_ID"].strip()
    tok = os.environ["CLOUDFLARE_API_TOKEN"].strip()
    resp = httpx.post(
        f"{_CF}/accounts/{acc}/browser-rendering/screenshot",
        headers={"Authorization": f"Bearer {tok}"},
        json={
            "url": url,
            "viewport": {"width": 1280, "height": 800},
            "gotoOptions": {"waitUntil": "networkidle0"},
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.content


def screenshot_project(output_dir: Path, slug: str, url: str) -> Optional[Path]:
    """Best-effort: screenshot *url* and write it to the project's hero path.
    Returns the written path, or None if unconfigured/failed (never raises)."""
    if not configured():
        return None
    try:
        png = capture_to_png(url)
    except Exception:
        return None
    if not png:
        return None
    dest = Path(output_dir) / slug / "screenshots" / "01-hero.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        dest.write_bytes(png)
    except OSError:
        return None
    return dest


__all__ = ["configured", "capture_to_png", "screenshot_project"]
