"""HTTP route dispatch for PebbleHandler.

Moved here from pebble_engine.py to keep that module under control. The
four route_X functions are the bodies of PebbleHandler.do_X, with
``self`` replaced by ``handler`` (the PebbleHandler instance). Handler
instance methods like ``handler._handle_build()`` and
``handler.send_response()`` continue to work because ``handler`` is
literally the BaseHTTPRequestHandler subclass.

Why a thin module instead of e.g. a route table
-----------------------------------------------
A data-driven route table (path -> callable) would be cleaner in many
respects, but Pebble's routes have idiosyncrasies (slug-suffix matching,
query-string stripping, ``self._raw_path`` stash for the few handlers
that need it) that compress poorly into a uniform schema. An if/elif
chain is honest about that, easy to grep ("where is /api/X handled?"),
and adds zero indirection at request time.

Adding a route
--------------
1. Copy an existing elif branch into the right ``route_*`` function.
2. If the handler lives in pebble/server/, inline-import it so we don't
   pay module-load cost for routes nobody hits in this process.
3. If it lives on PebbleHandler as ``_handle_X``, just call
   ``handler._handle_X(...)``.

The 500 path
------------
Every route function wraps its dispatch in
``try: ... except Exception as exc: handler._handle_500(exc)`` so an
unexpected exception from any handler always lands on the common 500
response (which logs under a correlation id and returns a generic
body). Don't catch broader exceptions inside individual handlers
unless you have a specific 4xx to surface.
"""
from __future__ import annotations


def route_options(handler) -> None:
    """Browser preflight handler.

    ``/api/internal/*`` paths are intentionally excluded — they're
    server-to-server (e.g. the Supabase webhook) and have no reason
    to participate in browser CORS. Refusing to bless those flows
    is defense-in-depth atop the existing bearer-secret gate.
    """
    if handler.path.startswith("/api/internal/"):
        # 405 makes the rejection visible to operators in access
        # logs; the browser will refuse the subsequent POST.
        handler.send_response(405)
        handler.send_header("Allow", "POST")
        handler.end_headers()
        return

    origin, allow_credentials = handler._cors_decision()
    if origin is None:
        # Allowlist configured + Origin not on it → no CORS approval.
        handler.send_response(204)
        handler.end_headers()
        return

    handler.send_response(204)
    handler.send_header("Access-Control-Allow-Origin", origin)
    if origin != "*":
        handler.send_header("Vary", "Origin")
    if allow_credentials:
        handler.send_header("Access-Control-Allow-Credentials", "true")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    handler.send_header("Access-Control-Max-Age", "86400")
    handler.end_headers()


def route_get(handler) -> None:
    # Strip query string for route matching (e.g. /?t=12345 should still serve index.html).
    # Stash raw_path so handlers that legitimately need the query string (e.g.
    # /api/dna/preview?id=...) can recover it via handler._raw_path. Most handlers
    # don't care, so the strip stays the default.
    raw_path = handler.path
    path_only = raw_path.split("?", 1)[0]
    handler.path = path_only
    handler._raw_path = raw_path
    try:
        if path_only in ("/", "/index.html"):
            handler._handle_engine_root()
        elif handler.path == "/api/health":
            handler._handle_health()
        elif handler.path == "/api/dna/preview":
            from pebble.server.dna import run_dna_preview
            run_dna_preview(handler)
        elif handler.path == "/api/blocks":
            from pebble.server.blocks import run_list_blocks
            run_list_blocks(handler)
        elif handler.path == "/api/templates":
            from pebble.server.templates_api import run_list_templates
            run_list_templates(handler)
        elif handler.path == "/api/industries":
            handler._handle_list_industries()
        elif handler.path == "/api/briefs":
            handler._handle_list_briefs()
        elif handler.path.startswith("/api/briefs/"):
            slug = handler.path.split("/api/briefs/", 1)[1]
            handler._handle_get_brief(slug)
        elif handler.path == "/api/auth/me":
            from pebble.server.auth import run_me
            run_me(handler)
        elif handler.path == "/api/projects":
            handler._handle_list_projects()
        elif handler.path == "/api/usage":
            handler._handle_usage_summary()
        elif handler.path == "/api/activity":
            handler._handle_activity_feed()
        elif handler.path == "/api/admin/users":
            from pebble.server.admin import run_list_users
            run_list_users(handler)
        elif handler.path == "/api/admin/projects":
            from pebble.server.admin import run_list_all_projects
            run_list_all_projects(handler)
        elif handler.path == "/api/admin/errors":
            from pebble.server.admin import run_recent_errors
            run_recent_errors(handler)
        elif handler.path == "/api/admin/engagement":
            from pebble.server.admin import run_engagement_summary
            run_engagement_summary(handler)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/integrations"):
            slug = handler.path[len("/api/projects/"):-len("/integrations")]
            from pebble.server.integrations import run_get_integrations
            run_get_integrations(handler, slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/history"):
            slug = handler.path[len("/api/projects/"):-len("/history")]
            handler._handle_get_history(slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/publish"):
            slug = handler.path[len("/api/projects/"):-len("/publish")]
            handler._handle_get_publish_state(slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/domain"):
            slug = handler.path[len("/api/projects/"):-len("/domain")]
            handler._handle_get_domain(slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/forms/webhook"):
            slug = handler.path[len("/api/projects/"):-len("/forms/webhook")]
            from pebble.server.forms import run_get_webhook_config
            run_get_webhook_config(handler, slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/forms/autoresponder"):
            slug = handler.path[len("/api/projects/"):-len("/forms/autoresponder")]
            from pebble.server.forms import run_get_autoresponder_config
            run_get_autoresponder_config(handler, slug)
        elif handler.path.startswith("/api/projects/") and "/inbox" in handler.path:
            handler._handle_inbox_get()
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/analytics"):
            slug = handler.path[len("/api/projects/"):-len("/analytics")]
            from pebble.server.analytics import run_get_summary
            run_get_summary(handler, slug)
        elif handler.path == "/api/account/profile":
            from pebble.server.account import run_get_profile
            run_get_profile(handler)
        elif handler.path == "/api/billing/subscription":
            from pebble.server.billing_subscription import run_get_subscription
            run_get_subscription(handler)
        elif handler.path == "/api/internal/process-email-drip":
            from pebble.server.internal import run_process_email_drip
            run_process_email_drip(handler)
        elif handler.path.startswith("/dist/"):
            handler._handle_serve_dist()
        elif handler.path.startswith("/preview/"):
            handler._handle_preview()
        else:
            handler.send_response(404); handler.end_headers()
            handler.wfile.write(b"Not found")
    except Exception as exc:
        handler._handle_500(exc)


def route_post(handler) -> None:
    try:
        if handler.path == "/api/instantiate-template":
            from pebble.server.templates_api import run_instantiate_template
            run_instantiate_template(handler)
        elif handler.path == "/api/build":
            handler._handle_build(generate=False)
        elif handler.path == "/api/generate":
            handler._handle_build(generate=True)
        elif handler.path == "/api/plan":
            handler._handle_plan()
        elif handler.path == "/api/setup":
            handler._handle_setup()
        elif handler.path == "/api/rollback":
            handler._handle_rollback()
        elif handler.path == "/api/refine":
            handler._handle_refine()
        elif handler.path == "/api/visual-edit":
            handler._handle_visual_edit()
        elif handler.path == "/api/migrate":
            handler._handle_migrate()
        elif handler.path == "/api/inspire":
            handler._handle_inspire()
        elif handler.path == "/api/brand-extract":
            from pebble.server.brand_extract import run_brand_extract
            run_brand_extract(handler)
        elif handler.path == "/api/publish":
            handler._handle_publish()
        elif handler.path.startswith("/api/forms/") and handler.path.endswith("/upload"):
            slug = handler.path[len("/api/forms/"):-len("/upload")]
            from pebble.server.forms import run_upload_attachment
            run_upload_attachment(handler, slug)
        elif handler.path.startswith("/api/forms/"):
            slug = handler.path[len("/api/forms/"):]
            handler._handle_form_submit(slug)
        elif handler.path.startswith("/api/track/"):
            slug = handler.path[len("/api/track/"):]
            from pebble.server.analytics import run_track
            run_track(handler, slug)
        elif handler.path.startswith("/api/projects/") and "/inbox/" in handler.path and handler.path.endswith("/read"):
            handler._handle_inbox_mark_read()
        elif handler.path == "/api/auth/signup":
            from pebble.server.auth import run_signup
            run_signup(handler)
        elif handler.path == "/api/auth/login":
            from pebble.server.auth import run_login
            run_login(handler)
        elif handler.path == "/api/auth/logout":
            from pebble.server.auth import run_logout
            run_logout(handler)
        elif handler.path == "/api/auth/forgot":
            from pebble.server.auth import run_forgot
            run_forgot(handler)
        elif handler.path == "/api/auth/reset":
            from pebble.server.auth import run_reset
            run_reset(handler)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/integrations"):
            slug = handler.path[len("/api/projects/"):-len("/integrations")]
            from pebble.server.integrations import run_post_integration
            run_post_integration(handler, slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/star"):
            slug = handler.path[len("/api/projects/"):-len("/star")]
            handler._handle_toggle_star(slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/claim"):
            slug = handler.path[len("/api/projects/"):-len("/claim")]
            from pebble.server.projects import run_claim_project
            run_claim_project(handler, slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/domain"):
            slug = handler.path[len("/api/projects/"):-len("/domain")]
            handler._handle_set_domain(slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/blocks/insert"):
            slug = handler.path[len("/api/projects/"):-len("/blocks/insert")]
            from pebble.server.blocks import run_insert_block
            run_insert_block(handler, slug)
        elif handler.path == "/api/internal/supabase-webhook":
            from pebble.server.supabase_webhook import run_supabase_webhook
            run_supabase_webhook(handler)
        elif handler.path == "/api/internal/stripe-webhook":
            from pebble.server.stripe_webhook import run_stripe_webhook
            run_stripe_webhook(handler)
        elif handler.path == "/api/checkout/create-session":
            from pebble.server.stripe_checkout import run_create_session
            run_create_session(handler)
        elif handler.path == "/api/billing/portal":
            from pebble.server.billing_portal import run_billing_portal
            run_billing_portal(handler)
        elif handler.path == "/api/account/delete":
            from pebble.server.account import run_delete_account
            run_delete_account(handler)
        elif handler.path == "/api/account/cancel-deletion":
            from pebble.server.account import run_cancel_deletion
            run_cancel_deletion(handler)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/forms/attachment-url"):
            slug = handler.path[len("/api/projects/"):-len("/forms/attachment-url")]
            from pebble.server.forms import run_get_attachment_signed_url
            run_get_attachment_signed_url(handler, slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/forms/webhook"):
            slug = handler.path[len("/api/projects/"):-len("/forms/webhook")]
            from pebble.server.forms import run_set_webhook_config
            run_set_webhook_config(handler, slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/forms/autoresponder"):
            slug = handler.path[len("/api/projects/"):-len("/forms/autoresponder")]
            from pebble.server.forms import run_set_autoresponder_config
            run_set_autoresponder_config(handler, slug)
        else:
            handler.send_response(404); handler.end_headers()
    except Exception as exc:
        handler._handle_500(exc)


def route_delete(handler) -> None:
    """The HTTP DELETE verb. Only one route uses it today —
    DELETE /api/projects/<slug>          → hard delete project
    DELETE /api/projects/<slug>/domain   → detach custom domain"""
    try:
        if handler.path.startswith("/api/projects/") and handler.path.endswith("/domain"):
            slug = handler.path[len("/api/projects/"):-len("/domain")]
            handler._handle_delete_domain(slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/forms/webhook"):
            slug = handler.path[len("/api/projects/"):-len("/forms/webhook")]
            from pebble.server.forms import run_delete_webhook_config
            run_delete_webhook_config(handler, slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/forms/autoresponder"):
            slug = handler.path[len("/api/projects/"):-len("/forms/autoresponder")]
            from pebble.server.forms import run_delete_autoresponder_config
            run_delete_autoresponder_config(handler, slug)
        elif handler.path.startswith("/api/projects/") and "/integrations/" in handler.path:
            # DELETE /api/projects/<slug>/integrations/<id>
            rest = handler.path[len("/api/projects/"):]
            parts = rest.split("/integrations/", 1)
            if len(parts) == 2 and parts[1]:
                slug, integration_id = parts[0], parts[1]
                from pebble.server.integrations import run_delete_integration
                run_delete_integration(handler, slug, integration_id)
            else:
                handler.send_response(404); handler.end_headers()
        elif handler.path.startswith("/api/projects/") and "/inbox/" in handler.path:
            handler._handle_inbox_delete()
        elif handler.path.startswith("/api/projects/"):
            slug = handler.path[len("/api/projects/"):]
            # Reject paths with subroutes (e.g. /history, /star) — those
            # belong to the GET/POST handlers, not DELETE.
            if "/" in slug:
                handler.send_response(404); handler.end_headers(); return
            handler._handle_delete_project(slug)
        else:
            handler.send_response(404); handler.end_headers()
    except Exception as exc:
        handler._handle_500(exc)


def route_patch(handler) -> None:
    """PATCH is only used for profile updates today."""
    handler.path = handler.path.split("?", 1)[0]
    try:
        if handler.path == "/api/account/profile":
            from pebble.server.account import run_patch_profile
            run_patch_profile(handler)
        else:
            handler.send_response(405)
            handler.send_header("Allow", "GET, POST, DELETE, OPTIONS")
            handler.end_headers()
    except Exception as exc:
        handler._handle_500(exc)
