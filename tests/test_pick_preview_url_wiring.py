"""Regression test that pins v3's iframe URL resolution through
``pickPreviewUrl``.

Background: ``/preview/<slug>/`` 404s for generated Next.js sites because
the engine's preview handler serves static files from
``output/<slug>/site/`` and Next.js apps have no compiled ``index.html``
on disk. ``next dev`` renders pages live on a free port returned to v3
as ``dev_server.url`` in the ``/api/generate`` response.

The fix is purely v3-side: the iframe should prefer ``dev_server.url``
when present, and fall back to the static preview path otherwise. This
test pins the wiring so a future refactor can't silently regress to the
broken-by-default behavior.

The helper's own input/output behavior is verified separately by
``ui/v3/lib/pick-preview-url.test.mjs`` (run via plain ``node``).
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
API_TS = REPO_ROOT / "ui" / "v3" / "lib" / "api.ts"
EDIT_PHASE = REPO_ROOT / "ui" / "v3" / "components" / "phases" / "edit-phase.tsx"
PUBLISH_PHASE = REPO_ROOT / "ui" / "v3" / "components" / "phases" / "publish-phase.tsx"
WORKSPACE_SHELL = REPO_ROOT / "ui" / "v3" / "components" / "workspace-shell.tsx"


def test_pick_preview_url_helper_exists():
    """The helper module must exist with an exported ``pickPreviewUrl``."""
    assert API_TS.is_file(), f"Missing: {API_TS}"
    src = API_TS.read_text(encoding="utf-8")
    assert "export function pickPreviewUrl" in src, (
        "pickPreviewUrl export missing from lib/api.ts — iframe wiring is broken"
    )


def test_generate_response_type_includes_dev_server():
    """The TypeScript type for ``/api/generate`` must declare ``dev_server``
    so consumers can read it without a cast. The engine has been returning
    this field since auto-run shipped."""
    src = API_TS.read_text(encoding="utf-8")
    # Type-side declaration in GenerateResponse.
    assert re.search(
        r"export type GenerateResponse\s*=\s*\{[^}]*\bdev_server\?\s*:",
        src,
        re.DOTALL,
    ), "GenerateResponse type no longer declares the optional dev_server field"


def test_edit_phase_uses_pick_preview_url():
    """The edit-phase iframe is the canonical click-to-edit surface. It
    MUST resolve the preview URL via ``pickPreviewUrl`` — not by reading
    ``build.preview_url`` directly. Direct reads regress the Next.js
    404 bug."""
    src = EDIT_PHASE.read_text(encoding="utf-8")
    assert re.search(
        r"import\s*\{[^}]*\bpickPreviewUrl\b[^}]*\}\s*from\s*['\"]@/lib/api['\"]",
        src,
        re.DOTALL,
    ), "edit-phase.tsx no longer imports pickPreviewUrl"
    assert "pickPreviewUrl(build)" in src, (
        "edit-phase.tsx no longer calls pickPreviewUrl(build) — "
        "iframe will 404 for Next.js sites again"
    )
    # The old direct read must be gone (other than inside the helper).
    illegal_lines = [
        line for line in src.splitlines()
        if "build?.preview_url" in line
        and "pickPreviewUrl" not in line
    ]
    assert not illegal_lines, (
        "edit-phase.tsx still reads build.preview_url directly "
        f"outside pickPreviewUrl(): {illegal_lines!r}"
    )


def test_publish_phase_uses_pick_preview_url():
    """Same wiring guard for the publish-phase preview tile."""
    src = PUBLISH_PHASE.read_text(encoding="utf-8")
    assert re.search(
        r"import\s*\{[^}]*\bpickPreviewUrl\b[^}]*\}\s*from\s*['\"]@/lib/api['\"]",
        src,
        re.DOTALL,
    ), "publish-phase.tsx no longer imports pickPreviewUrl"
    assert "pickPreviewUrl(build)" in src, (
        "publish-phase.tsx no longer calls pickPreviewUrl(build)"
    )


def test_workspace_shell_passes_through_dev_server():
    """The shell hydrates the ``build`` object from ``/api/generate``'s
    response. Without ``dev_server`` propagated here the helper above has
    nothing to prefer, and the fix is a no-op."""
    src = WORKSPACE_SHELL.read_text(encoding="utf-8")
    # The propagation lives inside the kickOff().then() block. Just pin
    # the literal — easy to grep for, hard to silently regress.
    assert "dev_server: response.dev_server" in src, (
        "workspace-shell.tsx no longer forwards response.dev_server into "
        "the built state object — pickPreviewUrl will always fall back to "
        "preview_url, defeating the fix"
    )
