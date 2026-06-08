"""Static-export a GENERATED site so its preview can be served without Node.

This generalizes ``pebble/templates/export.py`` (which only handled the
cinematic_* template gallery) to any generated project under
``output/<slug>/site/``.

Why this exists
---------------
The live preview today runs ``next dev`` per project. That needs Node/npm on
the server — which the prod Railway engine (Python-only) does not have, so
previews fail with "npm not found in PATH". The fix is to build a static
export (``out/``) once and serve those files statically (no dev server, no
Node at serve time). The same ``out/`` is also what ``publish_to_cloudflare``
prefers, so one artifact covers preview + publish.

Hard constraint
---------------
Next.js forbids Server Actions (``"use server"``) under ``output:"export"``.
Generated sites use a Server-Action contact form, so during the export build
we transiently swap ``app/actions/contact.ts`` for a client-side validation
stub (the same one the template exporter uses). Source files are restored
**byte-identically** via try/finally — the generated source on disk (and what
gets published with the real action, if/when SSR publish lands) is never left
mutated.

This module is build-environment-agnostic: it just needs Node available
wherever it runs (locally, a Node-enabled Railway image, or a build worker).
It does NOT decide where the build runs — see
docs/architecture/2026-06-08-prod-preview-architecture.md.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Optional

# Reuse the battle-tested universal contact stub from the template exporter
# rather than maintaining a second copy.
from pebble.templates.export import _PREVIEW_CONTACT_STUB

_WIN = sys.platform == "win32"
_SHELL = _WIN  # Windows needs shell=True to resolve npm.cmd/npx.cmd


def preview_next_config(slug: str) -> str:
    """The transient next.config.mjs used for a generated-site preview build.

    basePath makes assets resolve under the engine's /preview/<slug>/ route.
    images.unoptimized is required under output:"export" (no image
    optimization server). TS/eslint errors are ignored because preview builds
    only need to render the marketing surface, and the stubbed contact action
    can introduce shape mismatches the dev server tolerates."""
    return f"""/** @type {{import('next').NextConfig}} */
// Pebble preview-build config — written by pebble.preview_export.
// The generated next.config.mjs is restored byte-identically after the build.
const nextConfig = {{
  output: "export",
  trailingSlash: true,
  basePath: "/preview/{slug}",
  images: {{ unoptimized: true }},
  typescript: {{ ignoreBuildErrors: true }},
  eslint: {{ ignoreDuringBuilds: true }},
}};
export default nextConfig;
"""


def _paths_to_swap(site_dir: Path, slug: str) -> list[tuple[Path, str]]:
    """(path, preview_content) pairs to swap during the export build.

    Only files that already exist are swapped (we never create files the
    generated source didn't have). Each original is restored via try/finally.
    """
    swaps: list[tuple[Path, str]] = [
        (site_dir / "next.config.mjs", preview_next_config(slug)),
        (site_dir / "app" / "actions" / "contact.ts", _PREVIEW_CONTACT_STUB),
    ]
    return swaps


def static_export_dir(site_dir: Path) -> Path:
    """Where `next build` (output:export) writes the static site."""
    return Path(site_dir) / "out"


def export_generated_site(
    site_dir: Path,
    slug: str,
    *,
    skip_install: bool = False,
    build_timeout: float = 600.0,
) -> Path:
    """Run a static-export build for one generated site at *site_dir*.

    Returns the path to ``out/``. Source files (next.config.mjs,
    app/actions/contact.ts) are byte-identical before and after this call,
    even on failure (try/finally). Raises on build failure or if ``out/`` is
    not produced; the caller decides whether to fall back to the warmup splash.
    """
    site_dir = Path(site_dir)
    if not site_dir.is_dir():
        raise FileNotFoundError(f"site dir not found: {site_dir}")

    swaps = _paths_to_swap(site_dir, slug)

    # Capture originals as raw bytes (None = file absent → don't create it).
    originals: list[tuple[Path, Optional[bytes]]] = []
    for path, _preview in swaps:
        originals.append((path, path.read_bytes() if path.is_file() else None))

    try:
        for (path, preview_content), (_, original) in zip(swaps, originals):
            if original is not None:
                # newline="" avoids Windows \r\n translation so restore byte-
                # comparison stays meaningful; Next tolerates LF.
                path.write_text(preview_content, encoding="utf-8", newline="")

        if not skip_install and not (site_dir / "node_modules").exists():
            subprocess.run(
                ["npm", "install", "--no-audit", "--no-fund", "--loglevel=error"],
                cwd=site_dir, check=True, shell=_SHELL, timeout=build_timeout,
            )

        subprocess.run(
            ["npx", "next", "build"],
            cwd=site_dir, check=True, shell=_SHELL, timeout=build_timeout,
        )

        out = static_export_dir(site_dir)
        if not out.is_dir():
            raise RuntimeError(f"next build for {slug} did not produce out/")
        return out
    finally:
        restore_errors: list[tuple[Path, OSError]] = []
        for path, original in originals:
            if original is not None:
                try:
                    path.write_bytes(original)  # exact bytes — no newline drift
                except OSError as e:
                    restore_errors.append((path, e))
        if restore_errors:
            pretty = "\n  ".join(f"{p}: {e}" for p, e in restore_errors)
            raise RuntimeError(
                "RESTORE FAILED — generated source may be left in preview-build "
                f"state:\n  {pretty}\nRevert via `git`/snapshot before publish."
            )


__all__ = [
    "preview_next_config",
    "static_export_dir",
    "export_generated_site",
]
