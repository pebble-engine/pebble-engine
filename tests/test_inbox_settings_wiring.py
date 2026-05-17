"""Pin the v3 inbox settings UI panel — Python-side wiring guard.

The actual component is TypeScript (no JS test runner installed in v3),
so these tests verify the WIRING from Python: the component file
exists, the inbox page imports it, and the API client exposes the
five functions the panel needs.

The functional behavior is exercised by the existing HTTP tests in
tests/test_forms.py + tests/test_forms_webhook.py +
tests/test_forms_autoresponder.py.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INBOX_SETTINGS = REPO_ROOT / "ui" / "v3" / "components" / "inbox-settings.tsx"
INBOX_PAGE = REPO_ROOT / "ui" / "v3" / "app" / "inbox" / "page.tsx"
API_TS = REPO_ROOT / "ui" / "v3" / "lib" / "api.ts"


def test_inbox_settings_component_exists():
    assert INBOX_SETTINGS.is_file(), f"Missing: {INBOX_SETTINGS}"


def test_inbox_settings_exports_named_component():
    """The InboxSettings export is what the inbox page imports."""
    src = INBOX_SETTINGS.read_text(encoding="utf-8")
    assert re.search(r"export\s+function\s+InboxSettings\b", src), \
        "InboxSettings export not found"


def test_inbox_page_imports_settings():
    src = INBOX_PAGE.read_text(encoding="utf-8")
    assert re.search(
        r"import\s*\{\s*InboxSettings\s*\}\s*from\s*['\"]@/components/inbox-settings['\"]",
        src,
    ), "inbox/page.tsx does not import InboxSettings"


def test_inbox_page_has_view_toggle():
    """The inbox page must toggle between submissions and settings."""
    src = INBOX_PAGE.read_text(encoding="utf-8")
    # The view state declaration is the load-bearing piece.
    assert "view, setView" in src or 'setView("settings")' in src or "setView('settings')" in src, \
        "inbox/page.tsx missing the settings/submissions view toggle"
    # And the InboxSettings component is actually rendered.
    assert "<InboxSettings" in src, \
        "inbox/page.tsx does not render <InboxSettings />"


def test_api_module_exports_webhook_functions():
    """The five API client functions the panel calls."""
    src = API_TS.read_text(encoding="utf-8")
    for fn in (
        "fetchWebhookConfig",
        "setWebhookConfig",
        "clearWebhookConfig",
    ):
        assert re.search(rf"export\s+async\s+function\s+{fn}\b", src), \
            f"api.ts missing webhook function: {fn}"


def test_api_module_exports_autoresponder_functions():
    src = API_TS.read_text(encoding="utf-8")
    for fn in (
        "fetchAutoresponder",
        "saveAutoresponder",
        "clearAutoresponder",
    ):
        assert re.search(rf"export\s+async\s+function\s+{fn}\b", src), \
            f"api.ts missing autoresponder function: {fn}"


def test_settings_panel_calls_documented_endpoints():
    """The panel hits both engine surfaces — sanity-check the imports."""
    src = INBOX_SETTINGS.read_text(encoding="utf-8")
    # We import via @/lib/api so the calls are typed; verify the
    # import list has the right names.
    assert "fetchWebhookConfig" in src
    assert "setWebhookConfig" in src
    assert "clearWebhookConfig" in src
    assert "fetchAutoresponder" in src
    assert "saveAutoresponder" in src
    assert "clearAutoresponder" in src


# ---- Track 13 wiring: file-upload Phase 2 (inbox attachment display) ----

INBOX_PAGE_FILE = REPO_ROOT / "ui" / "v3" / "app" / "inbox" / "page.tsx"


def test_api_exports_fetch_attachment_signed_url():
    """The function the inbox page calls to convert a stored
    attachment path into a short-lived download URL."""
    src = API_TS.read_text(encoding="utf-8")
    assert re.search(r"export\s+async\s+function\s+fetchAttachmentSignedUrl\b", src), \
        "api.ts missing fetchAttachmentSignedUrl"
    # Hits the right endpoint shape.
    assert "/forms/attachment-url" in src
    # Sends the path in the body, not the URL.
    assert re.search(r"path\s*[,}]", src), "must include path in request body"


def test_inbox_page_renders_attachment_links():
    """When a submission field looks like a stored Supabase Storage
    attachment, the inbox UI must render a Download button (not raw
    text) that fetches a signed URL on click."""
    src = INBOX_PAGE_FILE.read_text(encoding="utf-8")
    assert "fetchAttachmentSignedUrl" in src, \
        "inbox/page.tsx must import the signed-URL fetcher"
    # Renders via a sub-component so the detection logic is testable
    # (and so the JSX stays readable).
    assert "FieldValue" in src and "AttachmentLink" in src, \
        "inbox/page.tsx should split rendering into FieldValue + AttachmentLink"
    # Opens the signed URL in a new tab safely.
    assert 'noopener' in src and 'noreferrer' in src, \
        "AttachmentLink should open with noopener+noreferrer"


def test_inbox_page_attachment_detection_uses_slug_namespace():
    """Defense in depth: the client-side detection ONLY treats values
    as attachments when the path/URL is scoped to the current slug.
    A raw URL from a different project shouldn't be rendered as a
    download button."""
    src = INBOX_PAGE_FILE.read_text(encoding="utf-8")
    # Detection logic must reference the slug parameter so cross-
    # project URLs in submitted field values render as plain text,
    # not buttons.
    assert "value.startsWith" in src or "startsWith(`${slug}/`)" in src, \
        "FieldValue should check value.startsWith(`${slug}/`)"
    assert "includes(`/${slug}/`)" in src, \
        "URL-shape detection should require the slug in the path"


# ---- Track 12 wiring: GDPR account deletion (Ch 7.7) -------------------

def test_api_exports_delete_account():
    """The deleteAccount function the panel calls must be exported."""
    src = API_TS.read_text(encoding="utf-8")
    assert re.search(r"export\s+async\s+function\s+deleteAccount\b", src), \
        "api.ts missing deleteAccount export"
    # Must read the Supabase access token client-side via getSession.
    assert "supabase.auth.getSession" in src, \
        "deleteAccount must read the Supabase access token client-side"
    # Must POST with Bearer header (server validates the token).
    assert re.search(r"Authorization.*Bearer", src), \
        "deleteAccount must send Authorization: Bearer <token>"


def test_settings_panel_renders_danger_zone():
    """The inbox settings panel must render the delete-account
    section — typed-email confirmation + button + supabase signOut
    on success.

    NLM round on Track 12 upgraded the typed confirmation from
    literal "DELETE" to the user's email address. Unattended-
    computer attackers can guess "DELETE"; they're far less likely
    to know the victim's email AND remember to spell it right."""
    src = INBOX_SETTINGS.read_text(encoding="utf-8")
    assert "deleteAccount" in src, "must import + call deleteAccount"
    # The typed-EMAIL guard (replaces the old literal-DELETE check).
    assert "user?.email" in src or "user.email" in src, \
        "must reference user.email for the typed confirmation"
    assert "confirmText" in src and ".toLowerCase()" in src, \
        "confirmation should be case-insensitive email match"
    # Client-side signOut after server-side delete succeeds.
    assert "supabase.auth.signOut" in src, \
        "must call supabase.auth.signOut to clear v3-side cookies"
    # Routes to /landing (or whatever the engine returns as `next`).
    assert "/landing" in src or "result.next" in src
