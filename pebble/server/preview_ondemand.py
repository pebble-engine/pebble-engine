"""On-demand preview warmup — start `next dev` for a project the first time
a workspace user opens it after an engine restart.

The problem this solves (2026-05-23):
  - `pebble.server.dev_registry` holds the URL of running `next dev` processes.
  - Those processes are normally started by `pebble.postbuild` right after a
    build completes (when PEBBLE_AUTO_RUN=true).
  - On engine restart, the registry is empty and the spawned processes are
    gone. Existing projects' previews 404 with "Preview file not found:
    index.html" because Next.js apps don't have a compiled index.html on disk.
  - User opens /workspace/<slug>, the iframe loads /preview/<slug>/, gets a
    404, shows a broken-image icon. Total UX failure.

The fix:
  - When /preview/<slug>/ is hit and no dev URL is registered AND the project
    is a Next.js app (has package.json), kick off `start_next_dev_after_install`
    in a background thread and return a small "warming up" splash that
    auto-refreshes every 2s.
  - Once the thread succeeds, dev_registry.register() is called and the next
    splash refresh proxies to the real dev server.
  - Per-slug lock ensures we never spawn two warmups for the same slug.

Design notes:
  - The warmup thread is daemon so engine shutdown kills it cleanly.
  - Cold first-build cost: ~60-120s (npm install) + ~10s (next dev startup).
  - Warm cost (node_modules already exists): ~10-20s.
  - Failures are sticky for 60s — we don't infinite-loop spawn on a broken
    package.json. After 60s the splash gives up and shows the error.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional


Status = Literal["ready", "starting", "failed"]


@dataclass
class _WarmupState:
    """Per-slug warmup tracking. One instance per slug."""
    started_at:     float = field(default_factory=time.time)
    finished_at:    Optional[float] = None
    last_error:     Optional[str] = None
    thread:         Optional[threading.Thread] = None


_STATES: dict[str, _WarmupState] = {}
_LOCK = threading.Lock()

# How long a "failed" state sticks before we'll retry. Prevents the splash
# from infinite-looping spawn attempts when package.json is genuinely broken,
# but short enough that a transient timeout (e.g. Next.js 16 first compile
# took longer than the poll allowed) doesn't lock the user out for long.
_FAILURE_TTL_SEC = 15.0


def start_or_get(slug: str, site_dir: Path) -> Status:
    """Kick off (or join) the warmup for *slug*.

    Returns:
      - "ready"    — dev_registry already has a URL; caller should retry the proxy
      - "starting" — warmup is in progress; caller should serve the splash
      - "failed"   — last attempt failed and we're inside the failure window

    Idempotent. Multiple concurrent calls for the same slug only spawn one thread.
    """
    # Fast path — dev already registered, no work needed.
    from pebble.server.dev_registry import get_url
    if get_url(slug):
        return "ready"

    with _LOCK:
        state = _STATES.get(slug)

        # Inside the failure cooldown window — don't respawn, just report.
        if state and state.last_error and state.finished_at:
            if (time.time() - state.finished_at) < _FAILURE_TTL_SEC:
                return "failed"
            # Cooldown elapsed; clear and try again
            _STATES.pop(slug, None)
            state = None

        # Active thread still running — share its state.
        if state and state.thread and state.thread.is_alive():
            return "starting"

        # Spawn a new warmup.
        state = _WarmupState()
        state.thread = threading.Thread(
            target=_run_warmup,
            args=(slug, site_dir, state),
            daemon=True,
            name=f"preview-ondemand-{slug}",
        )
        _STATES[slug] = state
        state.thread.start()
        return "starting"


def last_error(slug: str) -> Optional[str]:
    """Return the most recent error message for *slug*, or None if no failure
    is recorded. Used by the splash page to show a useful message."""
    with _LOCK:
        state = _STATES.get(slug)
        return state.last_error if state else None


def _run_warmup(slug: str, site_dir: Path, state: _WarmupState) -> None:
    """Background thread body — runs npm install + next dev, then registers
    the URL with dev_registry. Errors are captured into state.last_error so
    the splash can show them.

    Imports done inside the function so this module loads cleanly even on a
    Python interpreter that doesn't have postbuild's deps available."""
    try:
        from pebble.log import log
        from pebble.server.dev_registry import register
        from pebble.server.preview_warmup import (
            PreviewWarmup,
            start_next_dev_after_install,
        )

        log.info("[ondemand] warming up preview for %s", slug)

        warmup = PreviewWarmup(site_dir)
        # Even if node_modules already exists, calling start_install is cheap —
        # PreviewWarmup is idempotent and npm install is a fast no-op when
        # everything is already in place. Skipping the install means we have
        # nothing to wait on; calling it makes the start_next_dev_after_install
        # helper's wait_for_install() resolve quickly.
        warmup.start_install()

        # server_poll_timeout=180 (was 60) because Next.js 16 with Turbopack
        # frequently takes 60-120s on a cold cache for the first / route to
        # compile and respond. A shorter timeout was killing the dev process
        # right when it was almost ready, then the failure cooldown locked
        # the user out from retrying for another minute.
        result = start_next_dev_after_install(
            site_dir,
            warmup,
            install_wait_timeout=300.0,
            server_poll_timeout=180,
        )
        if result.get("errors"):
            state.last_error = "; ".join(result["errors"])
            log.warning("[ondemand] warmup failed for %s: %s", slug, state.last_error)
            return

        url = result.get("url")
        if not url:
            state.last_error = "next dev started but no URL returned"
            log.warning("[ondemand] %s: %s", slug, state.last_error)
            return

        register(slug, url)
        log.info("[ondemand] warmup complete for %s → %s", slug, url)
    except Exception as exc:
        state.last_error = f"unexpected warmup error: {exc}"
        try:
            from pebble.log import log
            log.warning("[ondemand] %s: %s", slug, state.last_error)
        except Exception:
            pass
    finally:
        state.finished_at = time.time()


def render_splash_html(slug: str, status: Status) -> str:
    """HTML splash page shown to the workspace iframe while warmup runs.

    Auto-refreshes every 2 seconds. Once next dev is registered and ready,
    the next refresh hits the proxy path and the real preview replaces this
    splash with zero user action required.
    """
    err = last_error(slug) if status == "failed" else None
    err_block = ""
    if err:
        # Escape HTML defensively — the error string can contain whatever
        # npm/next put in stderr. We display it in <pre> so newlines render.
        from html import escape
        err_block = f"""
        <details class=\"err\">
          <summary>Preview failed to start (click to see details)</summary>
          <pre>{escape(err)}</pre>
        </details>
        """

    title = "Starting preview…" if status == "starting" else "Preview failed"
    body_msg = (
        "Warming up your project's dev server. First load can take 30-90 seconds."
        if status == "starting"
        else "Could not start the preview server. Showing the last error below."
    )

    # 2s refresh while starting; 5s when failed (gives user time to read).
    # The page is intentionally minimal so it looks tasteful inside the
    # workspace iframe — no Pebble branding (the parent shell already brands
    # the surrounding chrome).
    refresh_meta = '<meta http-equiv="refresh" content="2">' if status == "starting" else ""

    return f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<title>{title}</title>
{refresh_meta}
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
  <div class=\"card\">
    {"<div class='spinner'></div>" if status == "starting" else ""}
    <h1>{title}</h1>
    <p>{body_msg}</p>
    {err_block}
  </div>
</body>
</html>
"""


__all__ = ["start_or_get", "render_splash_html", "last_error", "Status"]
