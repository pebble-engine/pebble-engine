"""Pin the v3 middleware's protected-route allowlist.

The middleware in `ui/v3/lib/supabase/middleware.ts` is the only thing
standing between an unauthenticated visitor and the workspace, dashboard,
admin, and inbox pages. If someone adds a new protected page (e.g.
/settings) and forgets to update PROTECTED_PREFIXES, the page becomes
publicly readable — the original 2026-05-16 NLM pass called this the
"fail-open" pattern.

These tests don't fix the fail-open posture (that would require deny-
by-default plus a public allowlist). They pin the current posture so
any future change is visible in PR review.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MIDDLEWARE = REPO_ROOT / "ui" / "v3" / "lib" / "supabase" / "middleware.ts"


def _src() -> str:
    return MIDDLEWARE.read_text(encoding="utf-8")


def test_middleware_exists():
    assert MIDDLEWARE.is_file(), f"Missing: {MIDDLEWARE}"


def test_protected_prefixes_constant_is_declared():
    """The list must be a named constant so it's easy to find, easy to
    review, and impossible to add a one-off `startsWith(...)` ad-hoc."""
    src = _src()
    assert re.search(
        r"const\s+PROTECTED_PREFIXES\s*=\s*\[",
        src,
    ), "middleware.ts should declare a PROTECTED_PREFIXES array"


def test_protected_prefixes_contains_known_gated_routes():
    """The four known protected routes — adding a fifth requires this
    test to be updated, which is the point."""
    src = _src()
    expected = ["/workspace", "/dashboard", "/admin", "/inbox"]
    for path in expected:
        assert f'"{path}"' in src, (
            f"PROTECTED_PREFIXES is missing {path!r}; new protected "
            f"routes must be added here AND in this test."
        )


def test_middleware_uses_strict_prefix_match():
    """The match must use `path === prefix || path.startsWith(prefix + "/")`
    so `/workspaces` (or `/workspace-public`) does NOT accidentally
    get auth-gated. The old `path.startsWith("/workspace")` form was
    over-broad."""
    src = _src()
    # Look for the strict pattern. The exact whitespace can vary so we
    # search loosely for the conceptual shape.
    assert re.search(
        r"path\s*===\s*prefix\s*\|\|\s*path\.startsWith\(\s*prefix\s*\+\s*['\"]\/['\"]\s*\)",
        src,
    ), (
        "middleware.ts should match with `path === prefix || "
        "path.startsWith(prefix + \"/\")` — anything looser allows "
        "/workspaces to accidentally inherit /workspace's gate."
    )


def test_middleware_documents_route_audit():
    """Future maintainers should be able to grep the file and find the
    intent. The audit comment lists each protected route with reasoning."""
    src = _src()
    assert "ROUTE AUDIT" in src, (
        "middleware.ts should carry a ROUTE AUDIT comment block listing "
        "each protected route and the public ones (so the fail-open "
        "trade-off is at least visible)."
    )


def test_middleware_does_not_use_loose_startswith_for_known_routes():
    """Regression guard: the old loose form must not return."""
    src = _src()
    # The legacy pattern looked like:
    #   path.startsWith("/workspace") || path.startsWith("/dashboard")
    # Both are now bundled inside PROTECTED_PREFIXES iteration.
    legacy = re.search(
        r"path\.startsWith\(['\"]\/workspace['\"]\)\s*\|\|\s*path\.startsWith\(['\"]\/dashboard['\"]\)",
        src,
    )
    assert not legacy, (
        "middleware.ts still uses the legacy loose `path.startsWith('/workspace') "
        "|| path.startsWith('/dashboard')` form — replace with PROTECTED_PREFIXES "
        "iteration."
    )
