"""GET /preview/<slug>/ — proxy, Vercel/Fly backends, static fallback."""
from __future__ import annotations

import json
import os

from pebble.log import log
from pebble.server.preview_paths import preview_forward_path


def run_preview(handler) -> None:
    import pebble_engine as pe
    OUTPUT_DIR = pe.OUTPUT_DIR
    _slugify = pe._slugify

    rest = handler.path[len("/preview/"):]
    if not rest:
        handler.send_response(404); handler.end_headers(); return
    parts = rest.split("/", 1)
    slug = _slugify(parts[0])
    rel = parts[1] if len(parts) > 1 and parts[1] else "index.html"
    if ".." in rel.split("/"):
        handler.send_response(403); handler.end_headers(); return

    # Phase 44 — flag set by the router when this request came in via
    # ``<slug>.pebbleapp.ai`` instead of the workspace iframe. Public
    # visitors must NOT see the visual-edit bridge (it leaks workspace
    # internals + spawns hover outlines on the live site) and SHOULD
    # get cache headers because the bytes are stable between edits.
    public_mode = bool(getattr(handler, "_public_subdomain_mode", False))

    # Block preview if the project owner's subscription has lapsed.
    # Unclaimed projects and free-tier users (no subscription.json) pass
    # through. Only fired when a sentinel file is present with a
    # non-active/trialing status — fail-open on any read error.
    if handler._subscription_lapsed(slug):
        handler._serve_subscription_lapse_page()
        return

    # 2026-05-23 — Fly.io backend (env-gated, falls back to local).
    # When PEBBLE_PREVIEW_BACKEND=fly, route /preview/<slug>/... to
    # https://pebble-preview-<slug>.fly.dev/. Public_mode skips this
    # because public subdomain visitors should always see the published
    # site (Cloudflare Pages), never a workspace dev preview.
    #
    # No app-exists pre-check — that would add a 1-3s flyctl roundtrip
    # per request. Instead, try the proxy with a generous timeout (Fly
    # cold-wake takes ~50s). If the app doesn't exist, _proxy_to_dev
    # returns False (DNS fail or connection refused) and we fall through
    # to local dev_registry / static-file handling. This keeps the env
    # toggle SAFE — flipping to "fly" never breaks projects that haven't
    # been deployed to Fly yet.
    preview_backend = os.environ.get("PEBBLE_PREVIEW_BACKEND", "local").strip().lower()
    vercel_proxy_headers: dict[str, str] = {}
    if preview_backend == "vercel":
        try:
            from pebble.vercel_deploy import preview_proxy_headers as _vercel_hdrs
            vercel_proxy_headers = _vercel_hdrs(slug)
        except Exception:
            vercel_proxy_headers = {}

    if preview_backend == "fly" and not public_mode:
        try:
            from pebble.fly_preview import preview_url as _fly_preview_url
            fly_url = _fly_preview_url(slug)
            slug_prefix = "/preview/" + parts[0]
            forward_path = preview_forward_path(
                getattr(handler, "_raw_path", handler.path), slug_prefix
            )
            # 20s timeout, NOT 90s. Originally tried 90s to cover cold
            # wakes, but that made EVERY request wait 90s before falling
            # back to local — terrible UX. With 20s we get:
            #   - Warm Fly (2-7s typical) → proxy succeeds quickly
            #   - Cold Fly (50-90s) → timeout at 20s, fall back to local
            #     immediately. The keep-alive ping in the workspace hits
            #     Fly DIRECTLY (cross-origin) to wake it without blocking
            #     user-facing requests on the wake-up window.
            if handler._proxy_to_dev(fly_url, forward_path, remote_timeout=20,
                                  base_prefix=slug_prefix):
                return
            # Proxy failed — fall through to local path so we don't break
            # workspaces for projects that haven't been Fly-provisioned.
            log.info("[fly] proxy returned False for %s, falling back to local", slug)
        except Exception as exc:
            log.info("[fly] proxy errored for %s, falling back to local: %s", slug, exc)

    # When PEBBLE_PREVIEW_BACKEND=vercel, route /preview/<slug>/... to the
    # site's Vercel deployment (built with full SSR on Vercel's infra — see
    # pebble.vercel_deploy). We PROXY it through the engine (rather than
    # iframing the raw *.vercel.app) so the response stays same-origin and
    # the visual-edit bridge can be injected, keeping click-to-edit working.
    # If no .vercel-preview.json exists yet (build still deploying), fall
    # through to the on-demand splash ("Still warming up…").
    if preview_backend == "vercel" and not public_mode:
        try:
            state_path = OUTPUT_DIR / slug / ".vercel-preview.json"
            vurl = ""
            if state_path.exists():
                vurl = (json.loads(state_path.read_text(encoding="utf-8")) or {}).get("url", "").rstrip("/")
            if vurl:
                slug_prefix = "/preview/" + parts[0]
                forward_path = preview_forward_path(
                    getattr(handler, "_raw_path", handler.path), slug_prefix
                )
                if handler._proxy_to_dev(vurl, forward_path, remote_timeout=20,
                                      base_prefix=slug_prefix,
                                      extra_headers=vercel_proxy_headers):
                    return
                log.info("[vercel] proxy returned False for %s; showing splash", slug)
            # No deployment yet (build still deploying) OR a transient proxy
            # miss: serve the auto-refreshing splash and DO NOT fall through
            # to the local npm warmup (Railway has no Node). The next splash
            # refresh re-attempts the proxy once .vercel-preview.json lands.
            from pebble.server.preview_ondemand import render_splash_html
            body = render_splash_html(slug, "starting").encode("utf-8")
            handler.send_response(200)
            handler.send_header("Content-Type", "text/html; charset=utf-8")
            handler.send_header("Content-Length", str(len(body)))
            handler.end_headers()
            handler.wfile.write(body)
            return
        except Exception as exc:
            log.info("[vercel] errored for %s, falling back: %s", slug, exc)

    # If a live `next dev` process is registered for this slug, proxy to
    # it so SSR routes work (Next.js apps have no compiled index.html on
    # disk — static-file serving would 404). Falls through to static
    # files when no dev server is alive (engine restart, old build, etc.).
    try:
        from pebble.server.dev_registry import get_url as _get_dev_url
        dev_url = _get_dev_url(slug)
        if dev_url:
            # Strip /preview/<raw-slug> so next dev sees the real route.
            slug_prefix = "/preview/" + parts[0]
            forward_path = preview_forward_path(
                getattr(handler, "_raw_path", handler.path), slug_prefix
            )
            if handler._proxy_to_dev(dev_url, forward_path, base_prefix=slug_prefix):
                return
    except Exception:
        pass  # fall through to static files

    # On-demand warmup (2026-05-23): if no dev URL is registered AND this
    # is a Next.js project (has package.json), kick off `next dev` in a
    # background thread and return a handler-refreshing splash so the user
    # doesn't see a broken-image 404 in the workspace iframe. The first
    # /preview hit after an engine restart triggers warmup; subsequent
    # /preview hits proxy normally once the splash auto-refreshes.
    # Skipped in public_mode — public visitors should see live content
    # or nothing, never a workspace-internal splash.
    if not public_mode:
        project_dir = OUTPUT_DIR / slug
        site_dir    = project_dir / "site"
        if (site_dir / "package.json").exists():
            try:
                from pebble.server.preview_ondemand import (
                    render_splash_html,
                    start_or_get,
                )
                status = start_or_get(slug, site_dir)
                if status == "ready":
                    # Race: registry just got populated while we were
                    # checking. Tell the iframe to retry — the next hit
                    # will land on the proxy path above.
                    handler.send_response(503)
                    handler.send_header("Retry-After", "1")
                    handler.send_header("Content-Type", "text/plain; charset=utf-8")
                    handler.end_headers()
                    handler.wfile.write(b"Preview just became ready - reload"); return
                html = render_splash_html(slug, status).encode("utf-8")
                handler.send_response(200)
                handler.send_header("Content-Type", "text/html; charset=utf-8")
                handler.send_header("Content-Length", str(len(html)))
                handler.send_header("Cache-Control", "no-store")
                handler.end_headers()
                handler.wfile.write(html); return
            except Exception:
                # Fall through to the original 404 path on any unexpected
                # error so the engine never crashes the preview path.
                pass

    site_file = OUTPUT_DIR / slug / "site" / rel
    if not site_file.exists() or not site_file.is_file():
        handler.send_response(404); handler.end_headers()
        handler.wfile.write(f"Preview file not found: {rel}".encode()); return
    ext = site_file.suffix.lstrip(".").lower()
    ct_map = {
        "html": "text/html", "htm": "text/html",
        "css": "text/css", "js": "application/javascript",
        "json": "application/json", "svg": "image/svg+xml",
        "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "gif": "image/gif", "ico": "image/x-icon",
        "woff": "font/woff", "woff2": "font/woff2",
    }
    ct = ct_map.get(ext, "text/plain")
    if ct.startswith("text/") or ct in ("application/javascript", "application/json", "image/svg+xml"):
        ct += "; charset=utf-8"

    # Inject the visual-edit bridge into HTML responses ONLY when the
    # request comes from the engine itself (i.e. the workspace iframe).
    # The bridge highlights elements on hover and posts a "selected"
    # message back to the parent window for click-to-edit. Bridge is
    # safe to ship: it's pure DOM event listeners, no network.
    #
    # Phase 44 — when serving via a public subdomain (public_mode=True)
    # we skip the bridge entirely (visitors don't get a click-to-edit
    # overlay) AND swap the no-store cache header for a short public
    # cache so the CDN/browser can reuse responses across visitors.
    if ext in ("html", "htm"):
        try:
            from pebble.integrations import render_all_snippets as _render_integrations
            raw = site_file.read_text(encoding="utf-8")
            # Phase 56a — inject active integration widgets (WhatsApp, booking,
            # Google Maps, social rail, cookie-consent, custom code) into every
            # HTML response. Integrations are live for both workspace preview
            # (non-public) AND public subdomain visitors so the published site
            # includes them. The injection is idempotent (snippets use stable IDs).
            integration_html = _render_integrations(slug)
            if integration_html:
                raw = handler._inject_html(raw, integration_html)
            if public_mode:
                data = raw.encode("utf-8")
                cache_header = "public, max-age=60"
            else:
                from pebble.server.visual_edit import PEBBLE_VISUAL_EDIT_BRIDGE
                injected = handler._inject_bridge(raw, PEBBLE_VISUAL_EDIT_BRIDGE)
                data = injected.encode("utf-8")
                cache_header = "no-store, no-cache, must-revalidate, max-age=0"
            handler.send_response(200)
            handler.send_header("Content-Type", ct)
            handler.send_header("Content-Length", str(len(data)))
            handler.send_header("Cache-Control", cache_header)
            handler.send_header("Access-Control-Allow-Origin", "*")
            handler.end_headers()
            handler.wfile.write(data)
            return
        except Exception:
            pass  # fall through to plain serve
    handler._serve_file(site_file, ct)


__all__ = ["run_preview"]
