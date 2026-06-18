"""Lazy Vercel preview deploy — kick off deploy_preview when /preview/ is hit.

Post-build deploy runs in a daemon thread; if it fails or never ran (engine
restart, truncated build, stale state), the workspace iframe loops on the
"Starting preview…" splash forever. This module retries deploy on demand with
per-slug deduplication and surfaces errors in the splash HTML.
"""
from __future__ import annotations

import json
import threading
import time
from html import escape
from pathlib import Path
from typing import Literal, Optional

from pebble.log import log

Status = Literal["ready", "deploying", "failed", "idle"]

_THREADS: dict[str, threading.Thread] = {}
_STATES: dict[str, dict] = {}
_LOCK = threading.Lock()

# Don't hammer Vercel if proxy keeps failing on a stale URL.
_RETRY_COOLDOWN_SEC = 90.0


def _output_dir() -> Path:
    import pebble_engine as pe
    return pe.OUTPUT_DIR


def _state_path(slug: str) -> Path:
    return _output_dir() / slug / ".vercel-preview.json"


def read_vercel_url(slug: str) -> str:
    path = _state_path(slug)
    if not path.exists():
        return ""
    try:
        data = json.loads(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return ""
    return str(data.get("url") or "").rstrip("/")


def last_deploy_error(slug: str) -> Optional[str]:
    with _LOCK:
        if slug in _STATES and _STATES[slug].get("error"):
            return str(_STATES[slug]["error"])
    path = _state_path(slug)
    if path.exists():
        try:
            err = (json.loads(path.read_text(encoding="utf-8")) or {}).get("error")
            if err:
                return str(err)
        except Exception:
            pass
    return None


def deploy_status(slug: str) -> Status:
    if read_vercel_url(slug):
        return "ready"
    with _LOCK:
        st = _STATES.get(slug)
        if st and st.get("thread") and st["thread"].is_alive():
            return "deploying"
        if st and st.get("error"):
            finished = st.get("finished_at") or 0
            if time.time() - finished < _RETRY_COOLDOWN_SEC:
                return "failed"
    return "idle"


def _write_error(slug: str, message: str) -> None:
    out = _output_dir() / slug
    out.mkdir(parents=True, exist_ok=True)
    path = _state_path(slug)
    payload: dict = {"url": None, "error": message, "deployed_at": None}
    if path.exists():
        try:
            payload.update(json.loads(path.read_text(encoding="utf-8")) or {})
        except Exception:
            pass
    payload["url"] = None
    payload["error"] = message
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _run_deploy(slug: str) -> None:
    try:
        from pebble.vercel_deploy import deploy_preview
        res = deploy_preview(slug)
        if res.get("error"):
            msg = str(res["error"])
            log.warning("[vercel] lazy deploy failed for %s: %s", slug, msg)
            with _LOCK:
                _STATES[slug] = {
                    "error": msg,
                    "finished_at": time.time(),
                    "thread": _THREADS.get(slug),
                }
            _write_error(slug, msg)
            return
        log.info("[vercel] lazy deploy ready for %s: %s", slug, res.get("url"))
        with _LOCK:
            _STATES.pop(slug, None)
    except Exception as exc:
        msg = f"deploy crashed: {exc}"
        log.warning("[vercel] lazy deploy errored for %s: %s", slug, exc)
        with _LOCK:
            _STATES[slug] = {
                "error": msg,
                "finished_at": time.time(),
                "thread": _THREADS.get(slug),
            }
        _write_error(slug, msg)


def kick_if_needed(slug: str, *, proxy_failed: bool = False) -> Status:
    """Start a background Vercel deploy when preview has no working URL.

    Returns the coarse status after this call (may have just spawned a thread).
    """
    if read_vercel_url(slug) and not proxy_failed:
        return "ready"

    site_dir = _output_dir() / slug / "site"
    if not (site_dir / "package.json").exists():
        msg = "project source not found on the engine — rebuild this project"
        with _LOCK:
            _STATES[slug] = {"error": msg, "finished_at": time.time()}
        _write_error(slug, msg)
        return "failed"

    with _LOCK:
        st = _STATES.get(slug)
        if st and st.get("thread") and st["thread"].is_alive():
            return "deploying"
        if proxy_failed:
            last = st.get("finished_at") if st else 0
            if last and time.time() - last < _RETRY_COOLDOWN_SEC:
                return "failed" if st and st.get("error") else "deploying"
        elif st and st.get("error"):
            finished = st.get("finished_at") or 0
            if time.time() - finished < _RETRY_COOLDOWN_SEC:
                return "failed"

        t = threading.Thread(
            target=_run_deploy,
            args=(slug,),
            daemon=True,
            name=f"vercel-kick-{slug}",
        )
        _THREADS[slug] = t
        _STATES[slug] = {"thread": t, "started_at": time.time()}
        t.start()
        return "deploying"


def render_vercel_splash_html(slug: str, status: Status) -> str:
    """Splash for PEBBLE_PREVIEW_BACKEND=vercel (not local npm warmup)."""
    err = last_deploy_error(slug) if status == "failed" else None
    err_block = ""
    if err:
        err_block = f"""
        <details class="err">
          <summary>Preview deploy failed (click for details)</summary>
          <pre>{escape(err)}</pre>
        </details>
        """

    if status == "deploying":
        title = "Building your preview…"
        body_msg = (
            "Pebble is compiling your site on Vercel. The first preview usually "
            "takes 1–2 minutes — this page refreshes automatically when it's ready."
        )
    elif status == "failed":
        title = "Preview needs another try…"
        body_msg = (
            "The last deploy attempt didn't finish. We'll retry automatically in a "
            "moment — you don't need to reload."
        )
    else:
        title = "Starting preview…"
        body_msg = (
            "Warming up your preview. This page updates itself when the site is ready."
        )

    refresh_secs = 2 if status != "failed" else int(_RETRY_COOLDOWN_SEC) + 2
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta http-equiv="refresh" content="{refresh_secs}">
<style>
  html, body {{ margin: 0; height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif; background: #0a0a0a; color: #fafafa; }}
  body {{ display: flex; align-items: center; justify-content: center; padding: 24px; }}
  .card {{ max-width: 520px; text-align: center; }}
  h1 {{ font-size: 18px; font-weight: 500; margin: 0 0 8px; letter-spacing: -0.01em; }}
  p {{ color: #a3a3a3; font-size: 14px; line-height: 1.5; margin: 0 0 16px; }}
  .spinner {{ width: 28px; height: 28px; border-radius: 50%; border: 2px solid #262626; border-top-color: #fafafa; margin: 0 auto 16px; animation: spin 0.8s linear infinite; }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  .err {{ margin-top: 24px; text-align: left; background: #18181b; border: 1px solid #27272a; border-radius: 8px; padding: 12px; }}
  .err summary {{ cursor: pointer; color: #fafafa; font-size: 13px; }}
  .err pre {{ font-family: ui-monospace, SFMono-Regular, monospace; font-size: 12px; color: #ef4444; white-space: pre-wrap; word-break: break-word; margin: 8px 0 0; }}
</style>
</head>
<body>
  <div class="card">
    <div class='spinner'></div>
    <h1>{title}</h1>
    <p>{body_msg}</p>
    {err_block}
  </div>
</body>
</html>
"""


__all__ = [
    "deploy_status",
    "kick_if_needed",
    "last_deploy_error",
    "read_vercel_url",
    "render_vercel_splash_html",
    "Status",
]
