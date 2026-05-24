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
        # Phase 44 (2026-05-22) — instant subdomain publish. Before any
        # other route matching, check whether the Host header is a
        # <slug>.pebbleapp.ai address. If yes, route to the preview
        # handler with public_mode=True (no bridge injection, no auth).
        # /api/* and /preview/* paths on a subdomain pass through to the
        # workspace iframe behaviour — useful when the workspace runs
        # under a custom domain that's ALSO wildcard-pointed.
        if _route_subdomain_get(handler):
            return
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
            # Phase 31 (2026-05-20) — template gallery list. Powers the
            # v3 /templates route and the workspace's "Start from template"
            # picker. Public; no auth needed.
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
        elif handler.path == "/api/notifications":
            # 2026-05-24 — bell badge feed. Auth-gated. Reads private
            # events for the user from Supabase.
            from pebble.server.notifications import run_list_notifications
            run_list_notifications(handler)
        elif handler.path == "/api/credits":
            # 2026-05-24 — credits balance + ledger + pack catalog.
            # Lazy-inits the user's credits row on first read so a
            # brand-new signup sees their plan's grant immediately.
            from pebble.server.credits_api import run_get_credits
            run_get_credits(handler)
        elif handler.path == "/api/community/feed":
            # 2026-05-24 — public events list for the /community page.
            # Public read (no auth) — visibility filter on the table
            # is what enforces privacy.
            from pebble.server.community_feed import run_community_feed
            run_community_feed(handler)
        elif handler.path == "/api/community/stats":
            # 2026-05-24 — single-row cached snapshot of community
            # numbers (total users, sites, launches this week,
            # template count). 15-min refresh-on-stale.
            from pebble.server.community_feed import run_community_stats
            run_community_stats(handler)
        elif (handler.path.startswith("/api/projects/")
              and "/" not in handler.path[len("/api/projects/"):]):
            slug = handler.path[len("/api/projects/"):]
            from pebble.server.projects import run_get_project_state
            run_get_project_state(handler, slug)
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
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/history"):
            slug = handler.path[len("/api/projects/"):-len("/history")]
            handler._handle_get_history(slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/publish"):
            slug = handler.path[len("/api/projects/"):-len("/publish")]
            handler._handle_get_publish_state(slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/published"):
            # Phase 44 — instant publish state for this project (owner-gated).
            slug = handler.path[len("/api/projects/"):-len("/published")]
            from pebble.server.publish_instant import run_get_instant_state
            run_get_instant_state(handler, slug)
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
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/screenshot"):
            # 2026-05-23 — serve the project's hero screenshot for the
            # dashboard project cards. Owner-gated. PNG content-type.
            slug = handler.path[len("/api/projects/"):-len("/screenshot")]
            from pebble.server.projects import run_get_screenshot
            run_get_screenshot(handler, slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/integrity"):
            # Phase 36 (2026-05-21) — curated 10-check pre-launch checklist
            # for the workspace's publish gate. Owner-gated. Read-only.
            slug = handler.path[len("/api/projects/"):-len("/integrity")]
            from pebble.server.integrity import run_integrity_check
            run_integrity_check(handler, slug)
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/integrations"):
            # Phase 56a (2026-05-22) — list all saved integrations for a project.
            slug = handler.path[len("/api/projects/"):-len("/integrations")]
            from pebble.server.integrations import run_get_integrations
            run_get_integrations(handler, slug)
        elif handler.path == "/api/account/profile":
            from pebble.server.account import run_get_profile
            run_get_profile(handler)
        elif handler.path.startswith("/api/account/activity"):
            from pebble.server.audit_log_api import run_get_activity
            run_get_activity(handler)
        elif handler.path.startswith("/api/account/change-email-confirm"):
            # Single-use token confirm — no auth required (user clicks from email).
            from pebble.server.account import run_confirm_email_change
            run_confirm_email_change(handler)
        elif handler.path == "/api/billing/subscription":
            from pebble.server.billing_subscription import run_get_subscription
            run_get_subscription(handler)
        elif handler.path == "/api/internal/process-email-drip":
            from pebble.server.internal import run_process_email_drip
            run_process_email_drip(handler)
        elif handler.path.startswith("/dist/"):
            handler._handle_serve_dist()
        elif handler.path.startswith("/preview-template/"):
            handler._handle_preview_template()
        elif handler.path.startswith("/preview/"):
            handler._handle_preview()
        else:
            handler.send_response(404); handler.end_headers()
            handler.wfile.write(b"Not found")
    except Exception as exc:
        handler._handle_500(exc)


def route_post(handler) -> None:
    try:
        if handler.path == "/api/build":
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
        elif handler.path == "/api/chat-edit":
            from pebble.server.chat_edit import run_chat_edit
            run_chat_edit(handler)
        elif handler.path == "/api/enrich-content":
            # Phase 58a — apply build-time chat facts (phone / location /
            # services) to an already-generated site. No LLM call — pure
            # regex substitution. Always billable: false.
            from pebble.server.enrich import run_enrich_content
            run_enrich_content(handler)
        elif handler.path == "/api/visual-edit":
            handler._handle_visual_edit()
        elif handler.path == "/api/migrate":
            handler._handle_migrate()
        elif handler.path == "/api/inspire":
            handler._handle_inspire()
        elif handler.path == "/api/instantiate-template":
            # Phase 31 (2026-05-20) — cheap-fast alternative to /api/generate.
            # Copies a pre-built designer-curated template + runs a focused
            # content-swap LLM call (~$0.005 on Qwen Flash) to inject the
            # customer's business name/services. Free-tier-friendly.
            from pebble.server.templates_api import run_instantiate_template
            run_instantiate_template(handler)
        elif handler.path == "/api/template-match":
            # Phase F1 (2026-05-24) — deterministic top-N template ranking.
            # Scores every template against (prompt, business_type) via cheap
            # token-overlap signals. No LLM, ~5ms. Public endpoint (no auth).
            # The funnel uses this after signup to surface 3 templates instead
            # of dumping the user into the full gallery — reduces bounce.
            from pebble.server.template_match import run_template_match
            run_template_match(handler)
        elif handler.path == "/api/chat":
            # 2026-05-23 — Pebble assistant multi-turn chat for the
            # Control Center side-panel. GPT-4o-mini via OpenRouter.
            # Returns strict JSON with reply + optional navigate_to +
            # confirm_action so the frontend acts on intent rather
            # than parsing free text.
            from pebble.server.chat import run_chat
            run_chat(handler)
        elif handler.path == "/api/credits/purchase":
            # 2026-05-24 — credit-pack Stripe Checkout. Pre-validates
            # cap BEFORE creating the session so a user near the 400
            # ceiling never pays for credits that wouldn't fit.
            from pebble.server.credits_api import run_purchase_pack
            run_purchase_pack(handler)
        elif handler.path == "/api/notifications/read-all":
            # 2026-05-24 — must come BEFORE the /<id>/read pattern
            # below or "/read-all" gets mis-parsed as an event id.
            from pebble.server.notifications import run_mark_all_read
            run_mark_all_read(handler)
        elif handler.path.startswith("/api/notifications/") and handler.path.endswith("/read"):
            from pebble.server.notifications import run_mark_read
            event_id = handler.path[len("/api/notifications/"):-len("/read")]
            run_mark_read(handler, event_id)
        elif handler.path == "/api/bot-message":
            # Phase 25b (2026-05-20) — bot persona narration. Cheap GPT-4o-mini
            # call returning short text (greeting / status / suggested chips)
            # for the workspace to display alongside the build. Webild parity
            # — closes the "silent spinner" perception gap with warm copy.
            from pebble.server.bot_message import run_bot_message
            run_bot_message(handler)
        elif handler.path == "/api/brand-extract":
            # Phase 33a/b (2026-05-21) — URL ingestion. Pre-auth endpoint that
            # turns a pasted URL into a partial brief (business name, industry
            # guess, palette, logo, hero copy) so the questionnaire can be
            # pre-filled. Removes the biggest friction step in the funnel —
            # "describe your business" — by extracting answers instead of
            # asking for them. Cached 1h per URL.
            from pebble.server.brand_extract import run_brand_extract
            run_brand_extract(handler)
        elif handler.path == "/api/smart-defaults":
            # Phase 39a (2026-05-21) — auto-infer audience + site_functions +
            # brand_tone from industry. Collapses the v3 idea-phase 3-step
            # questionnaire into a single confirmation card. Two-tier: tries
            # industries.json hints first (free), falls back to gpt-4o-mini.
            from pebble.server.smart_defaults import run_smart_defaults
            run_smart_defaults(handler)
        elif handler.path == "/api/publish":
            handler._handle_publish()
        elif handler.path == "/api/publish/instant":
            # Phase 44 — instant subdomain publish (no external deploy).
            from pebble.server.publish_instant import run_publish_instant
            run_publish_instant(handler)
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
        elif handler.path.startswith("/api/projects/") and handler.path.endswith("/integrations"):
            # Phase 56a (2026-05-22) — save/update one integration.
            slug = handler.path[len("/api/projects/"):-len("/integrations")]
            from pebble.server.integrations import run_post_integration
            run_post_integration(handler, slug)
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
        elif handler.path == "/api/account/select-plan":
            # Phase 54b — clears the needs_plan_selection flag after the
            # user explicitly picks Free / Starter / Pro / Enterprise.
            from pebble.server.account import run_select_plan
            run_select_plan(handler)
        elif handler.path == "/api/account/change-password":
            # Re-auth challenge + admin-API password update + audit log +
            # notification email. Per-user rate-limited to 5/hour.
            from pebble.server.account import run_change_password
            run_change_password(handler)
        elif handler.path == "/api/account/change-email-request":
            # Re-auth challenge + single-use pending token + confirmation
            # email to NEW address. Per-user rate-limited 3/24h.
            from pebble.server.account import run_request_email_change
            run_request_email_change(handler)
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
    """The HTTP DELETE verb. Used for:
    DELETE /api/projects/<slug>          → hard delete project
    DELETE /api/projects/<slug>/domain   → detach custom domain
    DELETE /api/publish/instant          → remove instant-publish sentinel
    """
    try:
        if handler.path == "/api/publish/instant":
            # Phase 44 — body carries {slug}. Owner-gated inside the handler.
            from pebble.server.publish_instant import run_unpublish_instant
            run_unpublish_instant(handler)
            return
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
            # Phase 56a (2026-05-22) — DELETE /api/projects/<slug>/integrations/<id>
            parts = handler.path[len("/api/projects/"):].split("/integrations/")
            if len(parts) == 2:
                slug, integration_id = parts
                from pebble.server.integrations import run_delete_integration
                run_delete_integration(handler, slug, integration_id)
            else:
                handler._send_json({"error": "Invalid integrations path"}, 400)
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


# --------- Phase 44 — subdomain routing -----------------------------------
#
# Two requirements:
#   1. https://bakery.pebbleapp.ai/             → serve preview of bakery
#   2. https://bakery.pebbleapp.ai/about        → serve preview/bakery/about.html
#
# Everything else (API calls, /preview/<other-slug>, /dist/...) must keep
# working on the same wildcard cert when the workspace runs at
# https://app.pebbleapp.ai — we just don't intercept those paths.
#
# The host check is cheap (1 env read + 1 string suffix check). It fires
# on EVERY GET, so keep this tight.

def _route_subdomain_get(handler) -> bool:
    """Return True when this GET was satisfied by subdomain routing.

    Behaviour:
      * Resolve ``Host`` header → published-project slug (or None).
      * If slug found AND the request path is "site-shaped" (root or a
        path that isn't ``/api/...``/``/preview/``/``/dist/``), rewrite
        ``handler.path`` to ``/preview/<slug>/<rest>`` and delegate to
        the existing preview handler with ``public_mode=True`` (skips
        the visual-edit bridge + sets caching headers).
      * If slug found but path is ``/api/*``/``/preview/*``/``/dist/*``,
        fall through to normal routing so the workspace API still works
        on app.pebbleapp.ai-style sub-domains.

    Returns False on any other condition (no env config, host doesn't
    match, subdomain unknown, etc.) so the caller continues with the
    regular if/elif chain.
    """
    host = handler.headers.get("Host", "") if hasattr(handler, "headers") else ""
    if not host:
        return False
    try:
        from pebble.server.publish_instant import lookup_published_slug_by_subdomain
    except Exception:
        return False

    slug = lookup_published_slug_by_subdomain(host)
    if not slug:
        return False

    path = handler.path
    # Don't hijack API or other system routes — they're called from inside
    # the published site too (form submit, analytics tracker).
    if path.startswith("/api/") or path.startswith("/preview/") or path.startswith("/dist/"):
        return False

    # Rewrite the path so the existing preview handler does the heavy
    # lifting (next-dev proxy, static fallback, etc.). The rest of the
    # path is preserved verbatim — ``/about`` becomes
    # ``/preview/<slug>/about``.
    rest = path.lstrip("/")
    handler.path = f"/preview/{slug}/{rest}" if rest else f"/preview/{slug}/"
    # Tell the preview handler this is a public visitor, not a workspace
    # iframe — affects bridge injection + cache headers.
    handler._public_subdomain_mode = True
    handler._public_subdomain_slug = slug
    handler._handle_preview()
    return True


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
