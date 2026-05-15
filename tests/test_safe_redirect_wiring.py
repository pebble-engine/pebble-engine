"""Regression test that pins the v3 `/login` page through `safeRedirect`.

The actual function lives in TypeScript (no JS test runner is installed
in v3), so this test verifies the WIRING from Python — i.e. that the
login page imports `safeRedirect` and that the raw `redirect` query
param never reaches `router.push` directly. A `node ui/v3/lib/safe-
redirect.test.mjs` script alongside the source covers the function's
own behavior end-to-end.

Background: the 2026-05-16 NLM pass surfaced an open-redirect in
`app/login/page.tsx` — `router.push(params.get("redirect") || "/workspace")`
will do a full off-origin navigation when the redirect is e.g.
`https://evil.com`. The fix routes the param through `safeRedirect()`
which falls back to /workspace for any non-relative-path input.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SAFE_REDIRECT = REPO_ROOT / "ui" / "v3" / "lib" / "safe-redirect.ts"
LOGIN_PAGE = REPO_ROOT / "ui" / "v3" / "app" / "login" / "page.tsx"


def test_safe_redirect_helper_exists():
    """The helper module must exist with an exported `safeRedirect`."""
    assert SAFE_REDIRECT.is_file(), f"Missing: {SAFE_REDIRECT}"
    src = SAFE_REDIRECT.read_text(encoding="utf-8")
    assert "export function safeRedirect" in src, (
        "safeRedirect export missing — login page wiring is broken"
    )


def test_login_page_imports_safe_redirect():
    """The login page MUST import safeRedirect; without the import any
    use of the function would be a TS error caught at build time, but
    pin it from Python too so the wiring is impossible to silently
    remove."""
    src = LOGIN_PAGE.read_text(encoding="utf-8")
    assert re.search(
        r"import\s*\{\s*safeRedirect\s*\}\s*from\s*['\"]@/lib/safe-redirect['\"]",
        src,
    ), "login/page.tsx no longer imports safeRedirect from @/lib/safe-redirect"


def test_login_page_does_not_consume_raw_redirect_param():
    """The raw query param must NEVER reach router.push directly. If
    someone refactors to `router.push(params.get('redirect') || …)` the
    open-redirect comes back."""
    src = LOGIN_PAGE.read_text(encoding="utf-8")
    # The legal pattern: the redirect variable is set via safeRedirect(...).
    legal = re.search(
        r"const\s+redirect\s*=\s*safeRedirect\s*\(",
        src,
    )
    assert legal, "login/page.tsx should compute `redirect` via safeRedirect(...)"
    # The illegal pattern: redirect computed directly from params.get without
    # safeRedirect involvement on the SAME line. We tolerate references to
    # `params.get("redirect")` inside the safeRedirect call itself.
    illegal_lines = [
        line for line in src.splitlines()
        if "params.get(\"redirect\")" in line
        and "safeRedirect(" not in line
    ]
    assert not illegal_lines, (
        "login/page.tsx still references params.get(\"redirect\") "
        f"outside a safeRedirect(...) wrapper: {illegal_lines!r}"
    )
