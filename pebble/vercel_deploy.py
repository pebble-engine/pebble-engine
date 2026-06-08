"""Deploy a generated site to Vercel via the Deployments REST API (v13).

Lets the Node-less Railway engine produce a fully-built (SSR) preview: we POST
the site's SOURCE files inline; Vercel runs `npm install` + `next build` on
their infra and returns a preview URL. No Node needed on our server, and
Server Actions + image optimization are preserved (unlike a static export).

The engine's `/preview/<slug>/` handler proxies the resulting URL (and injects
the visual-edit bridge) so the workspace iframe stays same-origin.

See docs/superpowers/plans/2026-06-08-vercel-preview.md.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

_SKIP = {"node_modules", ".next", ".turbo", "dist", "out", ".git", ".vercel"}
_API = "https://api.vercel.com"


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #

def vercel_configured() -> bool:
    return bool(os.environ.get("VERCEL_TOKEN", "").strip())


def _token() -> str:
    return os.environ["VERCEL_TOKEN"].strip()


def _team_qs() -> str:
    tid = os.environ.get("VERCEL_TEAM_ID", "").strip()
    return f"?teamId={tid}" if tid else ""


def _output_dir() -> Path:
    eng = sys.modules.get("pebble_engine") or sys.modules["__main__"]
    return eng.OUTPUT_DIR


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------- #
# File collection
# --------------------------------------------------------------------------- #

# Tolerant preview config: generated sites often have TS/eslint nits that
# `next dev` ignores but `next build` (which Vercel runs) rejects. A preview
# only needs to RENDER, so we ignore those. SSR is preserved (no output:export),
# so Server Actions + the contact form still work. images.unoptimized avoids
# needing to whitelist every remote image host for the preview.
_PREVIEW_NEXT_CONFIG = """/** @type {import('next').NextConfig} */
// Pebble preview build (Vercel) — written by pebble.vercel_deploy.
const nextConfig = {
  typescript: { ignoreBuildErrors: true },
  eslint: { ignoreDuringBuilds: true },
  images: { unoptimized: true },
};
export default nextConfig;
"""

def apply_preview_config(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Replace the site's next.config.mjs with a tolerant preview config so the
    Vercel build renders even with TS/lint nits (Pebble sites are always .mjs —
    a hard rule). Drops any stray .js/.ts config to avoid a multi-config error.
    Mutates + returns *files*."""
    kept: list[dict[str, Any]] = []
    found = False
    for f in files:
        if f["file"] in ("next.config.js", "next.config.ts"):
            continue  # drop — only .mjs is canonical
        if f["file"] == "next.config.mjs":
            f["data"] = _PREVIEW_NEXT_CONFIG
            found = True
        kept.append(f)
    if not found:
        kept.append({"file": "next.config.mjs", "data": _PREVIEW_NEXT_CONFIG})
    return kept


def collect_files(site_dir: Path) -> list[dict[str, Any]]:
    """Inline {file, data} list of the site's source (text files only).

    Binary assets are skipped — generated sites use remote (Pexels/Unsplash)
    images, so /public is typically empty. node_modules/.next/etc are excluded;
    Vercel installs + builds from the source."""
    site_dir = Path(site_dir)
    out: list[dict[str, Any]] = []
    for p in sorted(site_dir.rglob("*")):
        if p.is_dir() or any(part in _SKIP for part in p.parts):
            continue
        try:
            data = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # skip binary/unreadable for v1 (flagged in plan)
        out.append({"file": p.relative_to(site_dir).as_posix(), "data": data})
    return out


# --------------------------------------------------------------------------- #
# Vercel API
# --------------------------------------------------------------------------- #

def create_deployment(files: list[dict[str, Any]], *, name: str,
                      production: bool = False, timeout: float = 60.0) -> dict[str, str]:
    """POST /v13/deployments with inline files. Returns {id, url}."""
    body: dict[str, Any] = {
        "name": name,
        "files": files,
        "projectSettings": {"framework": "nextjs"},
    }
    if production:
        body["target"] = "production"
    resp = httpx.post(
        f"{_API}/v13/deployments{_team_qs()}"
        + ("&" if _team_qs() else "?") + "skipAutoDetectionConfirmation=1",
        headers={"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"},
        json=body, timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    raw = data.get("url") or ""
    url = raw if raw.startswith("http") else f"https://{raw}"
    return {"id": data.get("id", ""), "url": url}


def poll_deployment(deployment_id: str, *, interval: float = 3.0,
                    timeout: float = 300.0) -> dict[str, Any]:
    """Poll GET /v13/deployments/<id> until READY/ERROR/CANCELED or timeout."""
    deadline = time.time() + timeout
    last: dict[str, Any] = {}
    while time.time() < deadline:
        resp = httpx.get(
            f"{_API}/v13/deployments/{deployment_id}{_team_qs()}",
            headers={"Authorization": f"Bearer {_token()}"}, timeout=30.0,
        )
        resp.raise_for_status()
        last = resp.json()
        rs = last.get("readyState") or last.get("status")
        if rs in ("READY", "ERROR", "CANCELED"):
            return last
        time.sleep(interval)
    return {**last, "readyState": last.get("readyState") or "TIMEOUT"}


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

def _vercel_name(slug: str) -> str:
    n = re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-")[:90]
    return n or "pebble-site"


def deploy_preview(slug: str) -> dict[str, Any]:
    """Build a Vercel preview for output/<slug>/site and persist the URL to
    output/<slug>/.vercel-preview.json. Returns {url, deployment_id} or {error}."""
    if not vercel_configured():
        return {"error": "VERCEL_TOKEN not configured"}
    out = _output_dir() / slug
    meta: dict[str, Any] = {}
    mp = out / "build_meta.json"
    if mp.exists():
        try:
            meta = json.loads(mp.read_text(encoding="utf-8"))
        except Exception:
            meta = {}
    if meta.get("broken_files"):
        return {"error": "build has incomplete files — fix before previewing"}
    files = collect_files(out / "site")
    if not files:
        return {"error": "no source files to deploy"}
    files = apply_preview_config(files)
    created = create_deployment(files, name=_vercel_name(slug))
    final = poll_deployment(created["id"])
    if final.get("readyState") != "READY":
        return {"error": f"vercel build {final.get('readyState')}", "id": created.get("id")}
    url = created["url"]
    (out / ".vercel-preview.json").write_text(
        json.dumps({"url": url, "deployment_id": created["id"], "deployed_at": _now_iso()},
                   indent=2), encoding="utf-8")
    # Best-effort dashboard thumbnail: screenshot the live preview into the
    # path the ProjectCard already reads (output/<slug>/screenshots/01-hero.png).
    try:
        from pebble import screenshot as _ss
        _ss.screenshot_project(_output_dir(), slug, url)
    except Exception:
        pass
    return {"url": url, "deployment_id": created["id"]}


__all__ = [
    "vercel_configured", "collect_files", "create_deployment",
    "poll_deployment", "deploy_preview",
]
