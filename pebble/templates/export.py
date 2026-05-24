"""Static-export CLI for the cinematic_* template gallery.

The CLI does transient mutation at build time only. Source files
(`next.config.mjs`, `app/actions/contact.ts`) are backed up before
`next build`, replaced with preview-compatible versions, built, then
restored from backup via try/finally. After a successful or failed
run, source files are byte-identical to before.

This invariant is critical: pebble/server/templates_api.py:_copy_template
clones template source verbatim into customer projects. Any modification
left in source = silently broken customer apps (next build produces a
static site instead of a server-side app; contact form silently doesn't
send email).

Run from repo root:
    python -m pebble.templates.export cinematic_hero
    python -m pebble.templates.export --all
    python -m pebble.templates.export --all --skip-install
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# On Windows, .cmd shims (npm.cmd, npx.cmd) are not picked up unless we
# use shell=True or resolve the full path. This helper returns kwargs that
# make subprocess.run work cross-platform for Node tools.
_WIN = sys.platform == "win32"
_SHELL = _WIN

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "pebble" / "templates" / "registry.json"


_PREVIEW_NEXT_CONFIG = """/** @type {import('next').NextConfig} */
// Pebble preview-build config — written by pebble.templates.export.
// The committed next.config.mjs is restored after the build completes.
const nextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
};
export default nextConfig;
"""


_PREVIEW_CONTACT_STUB = """// Pebble preview-build stub — written by pebble.templates.export.
// The committed contact.ts (real "use server" action) is restored after
// the build completes. Next.js 14 forbids "use server" under output:"export".

type Result = { ok: true } | { ok: false; error: string };

const EMAIL_RE = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;

export async function submitContact(formData: FormData): Promise<Result> {
  const name    = (formData.get("name")    as string | null)?.trim() ?? "";
  const email   = (formData.get("email")   as string | null)?.trim() ?? "";
  const message = (formData.get("message") as string | null)?.trim() ?? "";

  if (!name)                  return { ok: false, error: "Name is required." };
  if (!email)                 return { ok: false, error: "Email is required." };
  if (!EMAIL_RE.test(email))  return { ok: false, error: "Please enter a valid email address." };
  if (!message)               return { ok: false, error: "Message is required." };

  // Static preview build — no email send. Customer instantiations restore the real action.
  return { ok: true };
}
"""


def _load_registry() -> dict:
    with REGISTRY_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def list_exportable_template_ids() -> list[str]:
    """Every template_id from the registry."""
    return [t["id"] for t in _load_registry().get("templates", []) if "id" in t]


def template_dir(template_id: str) -> Path:
    """Resolve <template_id> to its on-disk directory. Raises KeyError if unknown."""
    for t in _load_registry().get("templates", []):
        if t.get("id") == template_id:
            d = REPO_ROOT / t["directory"]
            if not d.is_dir():
                raise FileNotFoundError(
                    f"registry says {template_id} lives at {d} but the directory is missing"
                )
            return d
    raise KeyError(template_id)


def _paths_to_swap(tdir: Path) -> list[tuple[Path, str]]:
    """The (path, preview_content) pairs swapped during a preview build.
    Each path's pre-existing content is restored via try/finally."""
    return [
        (tdir / "next.config.mjs", _PREVIEW_NEXT_CONFIG),
        (tdir / "app" / "actions" / "contact.ts", _PREVIEW_CONTACT_STUB),
    ]


def export_template(template_id: str, *, skip_install: bool = False) -> Path:
    """Run a static-export build for one template. Returns the path to out/.
    Source files are byte-identical before and after this call (try/finally)."""
    tdir = template_dir(template_id)
    swaps = _paths_to_swap(tdir)

    # Capture original contents (None if file doesn't exist).
    originals: list[tuple[Path, str | None]] = []
    for path, _preview in swaps:
        if path.is_file():
            originals.append((path, path.read_text(encoding="utf-8")))
        else:
            originals.append((path, None))

    try:
        # Write previews.
        for (path, preview_content), (_, original) in zip(swaps, originals):
            if original is not None:
                # Only swap files that exist — don't create new ones that
                # the source didn't have.
                path.write_text(preview_content, encoding="utf-8")

        # Install if needed.
        if not skip_install and not (tdir / "node_modules").exists():
            print(f"[{template_id}] npm install...", flush=True)
            subprocess.run(
                ["npm", "install", "--no-audit", "--no-fund"],
                cwd=tdir,
                check=True,
                shell=_SHELL,
            )

        # Build.
        print(f"[{template_id}] npx next build...", flush=True)
        subprocess.run(["npx", "next", "build"], cwd=tdir, check=True, shell=_SHELL)

        out = tdir / "out"
        if not out.is_dir():
            raise RuntimeError(f"next build for {template_id} did not produce out/")
        return out
    finally:
        # ALWAYS restore originals — even if build failed.
        for path, original in originals:
            if original is not None:
                path.write_text(original, encoding="utf-8")


def _main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Build static previews of cinematic_* templates"
    )
    p.add_argument("template_id", nargs="?")
    p.add_argument("--all", action="store_true")
    p.add_argument("--skip-install", action="store_true")
    args = p.parse_args(argv)

    if args.all:
        ids = [i for i in list_exportable_template_ids() if i.startswith("cinematic_")]
    elif args.template_id:
        ids = [args.template_id]
    else:
        p.error("pass a template_id or --all")
        return 2

    failures: list[str] = []
    for tid in ids:
        try:
            export_template(tid, skip_install=args.skip_install)
            print(f"[{tid}] OK")
        except Exception as e:
            print(f"[{tid}] FAIL: {e}", file=sys.stderr)
            failures.append(tid)

    if failures:
        print(f"\n{len(failures)} failed: {', '.join(failures)}", file=sys.stderr)
        return 1
    print(f"\nExported {len(ids)} template(s)")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
