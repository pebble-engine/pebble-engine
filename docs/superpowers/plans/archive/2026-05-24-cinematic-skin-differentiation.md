# Cinematic Skin Differentiation + Static Preview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the 6 cinematic_* template gallery cards visually distinct (real industry photos + deep industry copy + occasional module reorder) and serve their previews as pre-built static HTML instead of running 24 dev servers.

**Architecture:** Each template's `next build` runs once with `output: "export"`, producing a static `out/` directory. The engine serves these via `/preview-template/<template_id>/`. The templates registry's `preview_url` field is rewritten to point at this engine path. v3's `<TemplatePreview>` iframe loads from `${ENGINE_BASE}/preview-template/<id>/`. Per-skin differentiation = industry hero + gallery images fetched once from Pexels into the template's `public/` dir + a rewritten `content/site.ts` + (for plumber + dog_groomer) a small reorder of the page.tsx module list.

**REVISED 2026-05-24 (during execution):** Original Tasks 1+2 modified the source `next.config.mjs` and `app/actions/contact.ts` of each template to add `output: "export"` and stub the server action. Code review caught that `templates_api._copy_template` clones those source files verbatim into customer projects — silently breaking their server-side Next.js apps and contact-form email delivery. **New approach: source files stay customer-clean. The static-export CLI (Task 3) does transient mutation at build time only** — backs up `next.config.mjs` + `contact.ts`, writes preview versions, runs `npx next build`, restores originals from backup. Original Tasks 1+2 are obsolete (reverted in commit `d40ae51`); their work is absorbed into Task 3.

**Tech Stack:** Next.js 14 static export, Python image fetch via existing `pebble.image_fallback._fetch_pexels_urls_for_keyword`, engine static-file serve, Pexels Photo API, Chrome MCP for re-screenshotting.

---

## File Structure

**Files this plan touches (created or modified):**

| Path | Purpose |
|---|---|
| `pebble/templates/cinematic_hero/next.config.mjs` | Add `output: "export"`, `images: { unoptimized: true }` |
| `pebble/templates/cinematic_{plumber,hvac,construction,landscaper,dog_groomer}/next.config.mjs` | Same as above (5 files) |
| `pebble/templates/cinematic_*/app/actions/contact.ts` | Add static-build no-op fallback so server actions don't break export |
| `pebble/templates/export.py` | **Create.** CLI `python -m pebble.templates.export [template_id|--all]` that runs `npm install` + `npx next build` per template |
| `pebble/templates/__init__.py` | Make `pebble.templates` an importable package if not already |
| `pebble_engine.py` | Add route handler `/preview-template/<id>/...` → serve from `pebble/templates/<id>/out/` |
| `tests/test_preview_template_route.py` | **Create.** Tests the new engine route |
| `tests/test_template_export_cli.py` | **Create.** Tests the export CLI registers all templates |
| `pebble/templates/registry.json` | Update 6 cinematic_* `preview_url` fields to `/preview-template/<id>/` |
| `ui/v3/app/templates/page.tsx` | Iframe src logic: prefix engine origin to `/preview-template/…` URLs |
| `pebble/templates/cinematic_hero/public/{hero,about,gallery/01-08}.jpg` | Replace generic placeholders with "service business" photos |
| `pebble/templates/cinematic_plumber/public/{hero,about,gallery/01-08}.jpg` | Plumber industry photos (10 total per skin × 5 skins = 50 files) |
| `pebble/templates/cinematic_{hvac,construction,landscaper,dog_groomer}/public/...` | Same as plumber |
| `pebble/templates/cinematic_hero/content/site.ts` | "Generic service business" deep copy |
| `pebble/templates/cinematic_plumber/content/site.ts` | Plumber-specific services + headlines + about |
| `pebble/templates/cinematic_{hvac,construction,landscaper,dog_groomer}/content/site.ts` | Same per industry |
| `pebble/templates/cinematic_plumber/app/page.tsx` | Reorder: emergency CTA band above the fold |
| `pebble/templates/cinematic_dog_groomer/app/page.tsx` | Reorder: gallery promoted above services |
| `ui/v3/public/templates-preview/cinematic_*.png` | Fresh screenshots showing real differentiation (6 files) |
| `scripts/screenshot_templates.py` | **Create.** CLI that uses headless Chrome to screenshot each `/preview-template/<id>/` once |

---

## Phase 1: Static Export Infrastructure

### Task 1: Enable static export in cinematic_hero next.config.mjs

**Files:**
- Modify: `pebble/templates/cinematic_hero/next.config.mjs`
- Modify: `pebble/templates/cinematic_hero/app/actions/contact.ts`

- [ ] **Step 1.1: Inspect the current next.config.mjs**

Run: `cat pebble/templates/cinematic_hero/next.config.mjs`

Confirm the file uses the `/** @type {import('next').NextConfig} */` JSDoc style. If `output` is not set, proceed.

- [ ] **Step 1.2: Add `output: "export"` + `images.unoptimized`**

Edit `pebble/templates/cinematic_hero/next.config.mjs` to look like:

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
};
export default nextConfig;
```

Rationale: `output: "export"` produces a static `out/` directory. `trailingSlash: true` makes every page emit as `out/<route>/index.html` so the engine's directory-resolving serve path works. `images.unoptimized: true` is required because static export can't run the Next.js image optimizer.

- [ ] **Step 1.3: Make contact server action no-op safely**

The `contact.ts` server action will trip the static-export build if it imports server-only modules. Edit `pebble/templates/cinematic_hero/app/actions/contact.ts`:

```ts
"use server";

export async function sendContact(formData: FormData) {
  // Real implementation uses Resend; in static preview builds (no server),
  // this never runs because the form's action attribute is omitted at build time.
  // Keeping the function so the page.tsx import doesn't break.
  const name = formData.get("name");
  const email = formData.get("email");
  console.log("[preview-build contact]", { name, email });
  return { ok: true };
}
```

Note: if the existing file already does something similar, just verify it doesn't import `@/lib/email` or `resend`. If it does, wrap that import in a try/catch or move it behind a `process.env.PEBBLE_PREVIEW_BUILD !== "1"` guard.

- [ ] **Step 1.4: Verify static build succeeds**

Run from `pebble/templates/cinematic_hero/`:
```bash
npx next build
```

Expected: build completes without errors. Output is in `out/` with `out/index.html`, `out/about/index.html`, `out/gallery/index.html`, `out/services/index.html`, etc.

If the build fails on a server-action error, follow Step 1.3 closer — the build error message will name the file/line.

- [ ] **Step 1.5: Commit**

```bash
git add pebble/templates/cinematic_hero/next.config.mjs pebble/templates/cinematic_hero/app/actions/contact.ts
git commit -m "feat(templates): cinematic_hero static export support"
```

---

### Task 2: Repeat static-export config across 5 cinematic skins

**Files:**
- Modify: `pebble/templates/cinematic_plumber/next.config.mjs`
- Modify: `pebble/templates/cinematic_hvac/next.config.mjs`
- Modify: `pebble/templates/cinematic_construction/next.config.mjs`
- Modify: `pebble/templates/cinematic_landscaper/next.config.mjs`
- Modify: `pebble/templates/cinematic_dog_groomer/next.config.mjs`
- Modify each skin's `app/actions/contact.ts` (same change as Task 1.3)

- [ ] **Step 2.1: Apply identical next.config.mjs change to all 5 skins**

For each `SKIN` in `cinematic_plumber, cinematic_hvac, cinematic_construction, cinematic_landscaper, cinematic_dog_groomer`:

Edit `pebble/templates/$SKIN/next.config.mjs` to match Task 1.2.

- [ ] **Step 2.2: Apply contact.ts no-op fallback to all 5 skins**

For each `SKIN` above, edit `pebble/templates/$SKIN/app/actions/contact.ts` to match Task 1.3.

- [ ] **Step 2.3: Verify each skin builds**

```bash
for skin in cinematic_plumber cinematic_hvac cinematic_construction cinematic_landscaper cinematic_dog_groomer; do
  echo "=== $skin ==="
  (cd pebble/templates/$skin && npx next build) || echo "FAIL $skin"
done
```

Expected: each one prints "Generating static pages" and exits 0. Each `pebble/templates/<skin>/out/` directory exists.

- [ ] **Step 2.4: Commit**

```bash
git add pebble/templates/cinematic_plumber pebble/templates/cinematic_hvac pebble/templates/cinematic_construction pebble/templates/cinematic_landscaper pebble/templates/cinematic_dog_groomer
git commit -m "feat(templates): static export config for 5 cinematic skins"
```

---

### Task 3: Build `pebble.templates.export` CLI

**Files:**
- Create: `pebble/templates/export.py`
- Create: `tests/test_template_export_cli.py`

- [ ] **Step 3.1: Write the failing test**

Create `tests/test_template_export_cli.py`:

```python
"""CLI test for the static-export tool."""
from __future__ import annotations

import json
from pathlib import Path

from pebble.templates import export as template_export


def test_list_exportable_templates_includes_cinematic_hero():
    """Lister should surface every cinematic_* registry entry."""
    ids = template_export.list_exportable_template_ids()
    assert "cinematic_hero" in ids
    assert "cinematic_plumber" in ids
    assert "cinematic_dog_groomer" in ids


def test_template_dir_resolves_relative_to_repo_root():
    """The path resolver must point at the on-disk directory."""
    d = template_export.template_dir("cinematic_hero")
    assert d.is_dir()
    assert (d / "next.config.mjs").is_file()


def test_template_dir_rejects_unknown_id():
    """Unknown id raises rather than silently returning a missing path."""
    import pytest
    with pytest.raises(KeyError):
        template_export.template_dir("does_not_exist")
```

- [ ] **Step 3.2: Run the test, watch it fail**

```bash
python -m pytest tests/test_template_export_cli.py -v
```

Expected: ImportError — `pebble.templates.export` does not exist yet.

- [ ] **Step 3.3: Create the export module**

Create `pebble/templates/export.py`:

```python
"""Static-export CLI for the template gallery.

For each template in pebble/templates/registry.json, runs
`npx next build` inside its directory. With `output: "export"` set in
the template's next.config.mjs, this produces a static `out/` directory
that the engine serves at /preview-template/<id>/.

Run from repo root:
    python -m pebble.templates.export cinematic_hero
    python -m pebble.templates.export --all
    python -m pebble.templates.export --all --skip-install   # node_modules already in place

The CLI is idempotent: re-running rebuilds out/ from scratch.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "pebble" / "templates" / "registry.json"


def _load_registry() -> dict:
    with REGISTRY_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def list_exportable_template_ids() -> list[str]:
    """Every template_id that has an on-disk directory."""
    reg = _load_registry()
    return [t["id"] for t in reg.get("templates", []) if "id" in t]


def template_dir(template_id: str) -> Path:
    """Resolve <template_id> to its on-disk directory. Raises KeyError if unknown."""
    reg = _load_registry()
    for t in reg.get("templates", []):
        if t.get("id") == template_id:
            d = REPO_ROOT / t["directory"]
            if not d.is_dir():
                raise FileNotFoundError(f"registry says {template_id} lives at {d} but the directory is missing")
            return d
    raise KeyError(template_id)


def export_template(template_id: str, *, skip_install: bool = False) -> Path:
    """Run npm install (unless skipped) then npx next build for one template.
    Returns the path to the produced out/ directory."""
    d = template_dir(template_id)
    if not skip_install and not (d / "node_modules").exists():
        print(f"[{template_id}] npm install...", flush=True)
        subprocess.run(["npm", "install", "--no-audit", "--no-fund"], cwd=d, check=True)
    print(f"[{template_id}] npx next build...", flush=True)
    env = os.environ.copy()
    env["PEBBLE_PREVIEW_BUILD"] = "1"
    subprocess.run(["npx", "next", "build"], cwd=d, check=True, env=env)
    out = d / "out"
    if not out.is_dir():
        raise RuntimeError(f"next build for {template_id} did not produce out/ — check next.config.mjs has output: 'export'")
    return out


def _main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build static previews of cinematic_* templates")
    p.add_argument("template_id", nargs="?", help="Single template_id (omit when using --all)")
    p.add_argument("--all", action="store_true", help="Export every registry entry whose id starts with cinematic_")
    p.add_argument("--skip-install", action="store_true", help="Skip npm install (assumes node_modules already present)")
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
```

- [ ] **Step 3.4: Verify package importability**

Check `pebble/templates/__init__.py` exists. If not, create it as an empty file:

```bash
test -f pebble/templates/__init__.py || touch pebble/templates/__init__.py
```

- [ ] **Step 3.5: Re-run the test, watch it pass**

```bash
python -m pytest tests/test_template_export_cli.py -v
```

Expected: 3 PASS.

- [ ] **Step 3.6: Smoke-run the CLI on cinematic_hero**

```bash
python -m pebble.templates.export cinematic_hero --skip-install
```

Expected output ends with `[cinematic_hero] OK\nExported 1 template(s)`. `pebble/templates/cinematic_hero/out/` exists with `index.html`.

- [ ] **Step 3.7: Commit**

```bash
git add pebble/templates/export.py pebble/templates/__init__.py tests/test_template_export_cli.py
git commit -m "feat(templates): static-export CLI"
```

---

### Task 4: Engine route `/preview-template/<id>/...`

**Files:**
- Modify: `pebble_engine.py` (add route handler)
- Create: `tests/test_preview_template_route.py`

- [ ] **Step 4.1: Write the failing test**

Create `tests/test_preview_template_route.py`:

```python
"""Engine route /preview-template/<id>/... serves files from
pebble/templates/<id>/out/ (the static export output)."""
from __future__ import annotations

import http.client
import os
import threading
from pathlib import Path

import pytest

from pebble_engine import run_server  # noqa


REPO_ROOT = Path(__file__).resolve().parents[1]
HOST = "127.0.0.1"
PORT = 9134  # arbitrary, must not clash with main engine


@pytest.fixture(scope="module")
def engine_thread(tmp_path_factory):
    server_thread = threading.Thread(
        target=run_server, kwargs={"port": PORT, "host": HOST}, daemon=True,
    )
    server_thread.start()
    # Give it a moment to bind
    import time; time.sleep(1.0)
    yield


def _get(path: str) -> tuple[int, bytes, dict]:
    conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
    conn.request("GET", path)
    r = conn.getresponse()
    body = r.read()
    headers = dict(r.getheaders())
    conn.close()
    return r.status, body, headers


def test_preview_template_serves_index_when_path_is_directory(engine_thread):
    """A bare /preview-template/<id>/ resolves to out/index.html."""
    out_index = REPO_ROOT / "pebble/templates/cinematic_hero/out/index.html"
    if not out_index.is_file():
        pytest.skip("Run `python -m pebble.templates.export cinematic_hero` first")
    status, body, headers = _get("/preview-template/cinematic_hero/")
    assert status == 200
    assert b"<html" in body.lower() or b"<!doctype" in body.lower()
    assert headers.get("Content-Type", "").startswith("text/html")


def test_preview_template_404s_unknown_template(engine_thread):
    status, _, _ = _get("/preview-template/no_such_template/")
    assert status == 404


def test_preview_template_rejects_path_traversal(engine_thread):
    """Walking out of the template dir must 403, not leak filesystem."""
    status, _, _ = _get("/preview-template/cinematic_hero/../../../secrets.env")
    assert status in (400, 403, 404)
```

- [ ] **Step 4.2: Run the test, watch it fail**

```bash
python -m pytest tests/test_preview_template_route.py -v
```

Expected: 404 on the index test (route not registered) or all three skip/fail because the handler doesn't exist.

- [ ] **Step 4.3: Add the route to pebble_engine.py**

Find where existing `/preview/<slug>/` is handled in `pebble_engine.py`. Just above (or beside) that block, add:

```python
elif path.startswith("/preview-template/"):
    # Static-export gallery preview. Serves files from
    # pebble/templates/<template_id>/out/ (built by
    # `python -m pebble.templates.export`).
    from pebble.templates.export import template_dir
    rel = path[len("/preview-template/"):]
    template_id, _, file_rel = rel.partition("/")
    if not template_id or not re.fullmatch(r"[a-z0-9_]+", template_id):
        self._json(400, {"error": "invalid template_id"}); return
    try:
        tdir = template_dir(template_id)
    except (KeyError, FileNotFoundError):
        self._json(404, {"error": "template not found"}); return
    out_root = (tdir / "out").resolve()
    if not out_root.is_dir():
        self._json(404, {"error": "template not yet exported; run pebble.templates.export"}); return

    file_rel = file_rel or "index.html"
    candidate = (out_root / file_rel).resolve()

    # Path-traversal guard — the resolved file MUST stay inside out_root.
    try:
        candidate.relative_to(out_root)
    except ValueError:
        self._json(403, {"error": "path outside template root"}); return

    if candidate.is_dir():
        candidate = candidate / "index.html"

    if not candidate.is_file():
        self.send_response(404); self.end_headers(); return

    self._serve_static_file(candidate)
    return
```

If `self._serve_static_file` does not exist, use the same static-file serving helper that the existing `/preview/<slug>/` route uses; copy its body inline if needed.

- [ ] **Step 4.4: Re-run tests**

```bash
# First, build the static export if you haven't already:
python -m pebble.templates.export cinematic_hero --skip-install
# Then:
python -m pytest tests/test_preview_template_route.py -v
```

Expected: 3 PASS.

- [ ] **Step 4.5: Smoke via curl**

Start the engine from the worktree:
```bash
python pebble_engine.py --port 8000 &
sleep 3
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/preview-template/cinematic_hero/
```

Expected: `200`.

- [ ] **Step 4.6: Commit**

```bash
git add pebble_engine.py tests/test_preview_template_route.py
git commit -m "feat(engine): serve static template previews at /preview-template/<id>/"
```

---

### Task 5: Update registry `preview_url` + v3 iframe logic

**Files:**
- Modify: `pebble/templates/registry.json`
- Modify: `ui/v3/app/templates/page.tsx`

- [ ] **Step 5.1: Update registry preview_url for all 6 cinematic_* entries**

Open `pebble/templates/registry.json`. For each entry whose `id` starts with `cinematic_`, change:
```diff
-      "preview_url": "http://localhost:3199/cinematic_plumber",
+      "preview_url": "/preview-template/cinematic_plumber/",
```

Apply identical pattern to: `cinematic_hero`, `cinematic_plumber`, `cinematic_hvac`, `cinematic_construction`, `cinematic_landscaper`, `cinematic_dog_groomer`.

- [ ] **Step 5.2: Update v3 iframe src construction**

Find the iframe src line in `ui/v3/app/templates/page.tsx` (around line 354 — `const iframeSrc = ...`). Replace with logic that prepends the engine origin when the URL is relative:

```tsx
// Templates with absolute preview URLs (legacy localhost:3199 entries) load as-is.
// Engine-served static-export URLs (/preview-template/<id>/...) need the engine base prefixed.
const ENGINE_BASE =
  process.env.NEXT_PUBLIC_PEBBLE_ENGINE_URL ||
  (typeof window !== "undefined" && window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "");
const previewUrl = current.preview_url ?? "";
const iframeSrc = previewUrl.startsWith("/")
  ? `${ENGINE_BASE}${previewUrl}${active.path}`
  : `${previewUrl}${active.path}`;
```

- [ ] **Step 5.3: Verify the iframe loads in v3 dev**

Make sure the engine is running with at least cinematic_hero exported (Task 3.6 + 4.5).

Start v3 dev: `cd ui/v3 && npx next dev -p 3001`.

Visit `http://localhost:3001/templates`. Click the **Cinematic Hero** card. The preview pane should now load the actual exported HTML in the iframe (no longer the "sad mug" error).

- [ ] **Step 5.4: Commit**

```bash
git add pebble/templates/registry.json ui/v3/app/templates/page.tsx
git commit -m "feat(templates): wire cinematic_* preview_url to engine static-export route"
```

---

## Phase 2: Per-skin Industry Differentiation

Each Task in this phase produces ONE distinct skin: 8 industry-specific images downloaded from Pexels into `public/`, a rewritten `content/site.ts` with industry-deep copy, and (where flagged) a small reorder of the page.tsx module list. Subagents must not invent business names or fake addresses — keep placeholders in `[…]` brackets for customer fill-in, but make the SERVICE copy industry-real.

The 6 industry image-sets to use:

| Template | Pexels keyword (hero) | Pexels keyword (gallery — broader) |
|---|---|---|
| cinematic_hero       | `professional service business`   | `service team at work` |
| cinematic_plumber    | `plumber pipe wrench`             | `plumbing service` |
| cinematic_hvac       | `hvac technician installing`      | `air conditioning unit` |
| cinematic_construction | `construction worker site`      | `construction crew` |
| cinematic_landscaper | `landscaper mowing lawn`          | `landscaping garden` |
| cinematic_dog_groomer | `dog grooming bath`              | `happy clean dog` |

Each skin gets 1 hero + 1 about + 8 gallery = 10 images total.

### Task 6: Build the per-skin image-fetch helper

**Files:**
- Create: `scripts/fetch_template_images.py`
- Test: smoke-only (one image, manual verification)

- [ ] **Step 6.1: Create the fetcher script**

Create `scripts/fetch_template_images.py`:

```python
"""Download industry-specific photos from Pexels into a template's public/ dir.

Usage:
    python scripts/fetch_template_images.py cinematic_plumber \
        --hero "plumber pipe wrench" \
        --gallery "plumbing service" \
        --count 8

Files written:
    pebble/templates/<template_id>/public/hero.jpg
    pebble/templates/<template_id>/public/about.jpg
    pebble/templates/<template_id>/public/gallery/01.jpg .. 08.jpg

Requires PEBBLE_PEXELS_API_KEY in the environment (already in .env).
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.request
from pathlib import Path

from pebble.image_fallback import _fetch_pexels_urls_for_keyword

REPO_ROOT = Path(__file__).resolve().parents[1]


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "PebbleTemplateBuilder/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp, open(dest, "wb") as out:
        out.write(resp.read())
    print(f"  wrote {dest.relative_to(REPO_ROOT)} ({dest.stat().st_size:,} bytes)")


def fetch_images(template_id: str, hero_kw: str, gallery_kw: str, gallery_count: int = 8) -> None:
    pub = REPO_ROOT / "pebble" / "templates" / template_id / "public"
    if not pub.exists():
        raise FileNotFoundError(f"{pub} — template's public dir doesn't exist")

    print(f"[{template_id}] fetching hero ({hero_kw!r})")
    hero_urls = _fetch_pexels_urls_for_keyword(hero_kw, count=4)
    if not hero_urls:
        raise RuntimeError(f"no Pexels results for {hero_kw!r}")
    _download(hero_urls[0], pub / "hero.jpg")
    _download(hero_urls[1] if len(hero_urls) > 1 else hero_urls[0], pub / "about.jpg")

    print(f"[{template_id}] fetching {gallery_count} gallery images ({gallery_kw!r})")
    gallery_urls = _fetch_pexels_urls_for_keyword(gallery_kw, count=gallery_count + 4)
    if len(gallery_urls) < gallery_count:
        print(f"  warning: only {len(gallery_urls)} results, padding with hero pool", file=sys.stderr)
        gallery_urls = (gallery_urls + hero_urls)[:gallery_count]
    for i, url in enumerate(gallery_urls[:gallery_count], 1):
        _download(url, pub / "gallery" / f"{i:02d}.jpg")


def _main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("template_id")
    p.add_argument("--hero", required=True)
    p.add_argument("--gallery", required=True)
    p.add_argument("--count", type=int, default=8)
    args = p.parse_args()
    fetch_images(args.template_id, args.hero, args.gallery, gallery_count=args.count)
    return 0


if __name__ == "__main__":
    sys.exit(_main())
```

- [ ] **Step 6.2: Verify Pexels env key is loaded**

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('KEY' if os.environ.get('PEBBLE_PEXELS_API_KEY') else 'MISSING')"
```

Expected: `KEY`. If `MISSING`, stop and tell Marc — the .env sync probably needs to run (`python scripts/sync_env.py`).

- [ ] **Step 6.3: Smoke-test with a one-off fetch**

```bash
python scripts/fetch_template_images.py cinematic_hero \
  --hero "professional service business" \
  --gallery "service team at work" \
  --count 2
```

Expected: 4 files written under `pebble/templates/cinematic_hero/public/` (hero.jpg, about.jpg, gallery/01.jpg, gallery/02.jpg). Verify by `ls pebble/templates/cinematic_hero/public/`.

- [ ] **Step 6.4: Commit**

```bash
git add scripts/fetch_template_images.py
git commit -m "feat(templates): industry-image fetcher CLI"
```

(No tests committed — the only meaningful test is "did Pexels respond with a usable photo", which is a network test we don't run in CI.)

---

### Task 7: Differentiate cinematic_hero (generic service-business)

**Files:**
- Modify: `pebble/templates/cinematic_hero/public/{hero,about}.jpg` + `gallery/01-08.jpg`
- Modify: `pebble/templates/cinematic_hero/content/site.ts`

- [ ] **Step 7.1: Fetch the image set**

```bash
python scripts/fetch_template_images.py cinematic_hero \
  --hero "professional service business" \
  --gallery "service team at work" \
  --count 8
```

Verify: `ls pebble/templates/cinematic_hero/public/` shows hero.jpg + about.jpg, and `ls pebble/templates/cinematic_hero/public/gallery/` shows 01.jpg..08.jpg.

- [ ] **Step 7.2: Rewrite content/site.ts with generic-but-real service copy**

Replace `pebble/templates/cinematic_hero/content/site.ts` with:

```ts
export const SITE_TITLE       = "[Your Service Co.]";
export const SITE_DESCRIPTION = "Local service business. Licensed, insured, and built on a reputation for showing up.";
export const TAGLINE          = "Honest work. Done right.";
export const PHONE   = "[(555) 555-0100]";
export const EMAIL   = "[hello@example.com]";
export const ADDRESS = "[123 Main St, City, ST 00000]";

export const HERO_BG_IMAGE          = "/hero.jpg";
export const HERO_PILL              = "BOOKING THIS WEEK";
export const HERO_HEADLINE          = "Work you can trust.";
export const HERO_SUBLINE           = "Local crew. Same-day quotes. Written guarantees. No surprises on the bill — just the job done the way it should be.";
export const HERO_CTA_PRIMARY       = "Get a free quote";
export const HERO_CTA_PRIMARY_HREF  = "/contact";
export const HERO_CTA_SECONDARY     = "See our work";
export const HERO_CTA_SECONDARY_HREF = "/services";

export type Service = { id: string; title: string; description: string; icon: string };
export const SERVICES: Service[] = [
  { id: "svc-1", title: "Free Estimates",      description: "On-site assessment, written quote in your inbox the same day. Fixed pricing before any work begins.", icon: "FileText" },
  { id: "svc-2", title: "Licensed & Insured",  description: "Fully licensed in [your state] and insured up to $[amount]. Bonded for your protection on every job.",  icon: "ShieldCheck" },
  { id: "svc-3", title: "Workmanship Guarantee", description: "Every job backed by our [N]-year guarantee. If something isn't right, we come back and fix it.",      icon: "BadgeCheck" },
];

export const ABOUT_PHOTO_IMAGE = "/about.jpg";
export const ABOUT_HEADLINE    = "Local crew. Built on referrals.";
export const ABOUT_BODY        = "[Two paragraphs about your story — how you got started, what makes you different. Keep it human and specific. Avoid corporate-speak.]";

export type Trust = { label: string; sub: string };
export const TRUST_BADGES: Trust[] = [
  { label: "LICENSED",     sub: "[State license #]"               },
  { label: "INSURED",      sub: "Up to $[amount]"                 },
  { label: "5-STAR RATED", sub: "[N]+ Google reviews"             },
  { label: "LOCAL",        sub: "Serving [city] since [year]"     },
];

export const TESTIMONIAL_QUOTE  = "[A 1-2 sentence testimonial in your customer's voice. Specific results > generic praise. Include a real first name and last initial.]";
export const TESTIMONIAL_AUTHOR = "[Maria T.], [City]";

export const CONTACT_HEADLINE = "Ready to get started?";
export const CONTACT_BODY     = "Tell us what you need. We respond within an hour during business hours.";
export const CONTACT_HOURS    = "[Mon–Fri 7am–6pm · Sat 8am–2pm]";

export const CTA_BAND_HEADLINE = "This week's calendar is filling up.";
export const CTA_BAND_BODY     = "Same-day quotes available — call now or fill out the form below.";
export const CTA_BAND_LABEL    = "Schedule today";
export const CTA_BAND_HREF     = "/contact";

export const FOOTER_TAGLINE = "Local. Licensed. Honest work.";

// --- Gallery page ---
export const GALLERY_HEADLINE = "Recent work.";
export const GALLERY_SUBLINE  = "Real jobs, real customers. Tap any photo to see the details.";
export const GALLERY_IMAGES: Array<{ src: string; alt: string; caption?: string }> = [
  { src: "/gallery/01.jpg", alt: "[Job 1 description]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/02.jpg", alt: "[Job 2 description]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/03.jpg", alt: "[Job 3 description]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/04.jpg", alt: "[Job 4 description]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/05.jpg", alt: "[Job 5 description]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/06.jpg", alt: "[Job 6 description]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/07.jpg", alt: "[Job 7 description]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/08.jpg", alt: "[Job 8 description]",  caption: "[Optional 1-line caption]" },
];

// --- Process page ---
export const PROCESS_HEADLINE = "How it works.";
export const PROCESS_SUBLINE  = "From your first call to job-done, here's exactly what to expect — no mystery, no surprises.";
export type ProcessStep = { number: string; title: string; description: string };
export const PROCESS_STEPS: ProcessStep[] = [
  { number: "01", title: "Tell us what you need",  description: "Call, text, or fill out the form. We respond within an hour during business hours. Free, no commitment." },
  { number: "02", title: "We come look + quote",   description: "On-site assessment with you, then a written quote in your inbox same day. Pricing is fixed before work starts." },
  { number: "03", title: "We do the work",         description: "Scheduled at your convenience. We arrive when we say we will, with the parts and tools to get it done in one trip." },
];

// --- FAQ page ---
export const FAQ_HEADLINE = "Common questions.";
export const FAQ_SUBLINE  = "If your question isn't here, just ask — we usually reply within the hour.";
export type FAQItem = { q: string; a: string };
export const FAQ_ITEMS: FAQItem[] = [
  { q: "Do you charge for estimates?",       a: "[No — every estimate is free, in writing, with no obligation. We come look, you decide.]" },
  { q: "Are you licensed and insured?",      a: "[Yes — fully licensed (#[license number]) and insured up to $[amount] for your protection.]" },
  { q: "How fast can you come out?",         a: "[Same-day in most cases for emergencies. Standard appointments usually 1-3 business days out.]" },
  { q: "What forms of payment do you take?", a: "[Cash, check, all major cards, and we offer financing on jobs over $[amount].]" },
  { q: "Do you offer a guarantee?",          a: "[Yes — [N]-year workmanship guarantee on all installations, [N] days on repairs.]" },
  { q: "What areas do you serve?",           a: "[See our service area page for the full list of cities. Generally [region] within [N] miles of [city].]" },
];

// --- Service area page ---
export const SERVICE_AREA_HEADLINE = "Where we work.";
export const SERVICE_AREA_SUBLINE  = "Local, family-owned, and proud of it. If your town isn't listed, give us a call — we may still be able to help.";
export const SERVICE_AREA_MAP_EMBED = "";
export const SERVICE_AREA_CITIES: string[] = [];

export const NAV_LINKS = [
  { label: "Services",     href: "/services"     },
  { label: "Gallery",      href: "/gallery"      },
  { label: "Process",      href: "/process"      },
  { label: "Service Area", href: "/service-area" },
  { label: "FAQ",          href: "/faq"          },
  { label: "About",        href: "/about"        },
  { label: "Contact",      href: "/contact"      },
];
```

- [ ] **Step 7.3: Re-export the static build**

```bash
python -m pebble.templates.export cinematic_hero --skip-install
```

Expected: exits 0; the new images appear in `pebble/templates/cinematic_hero/out/`.

- [ ] **Step 7.4: Commit**

```bash
git add pebble/templates/cinematic_hero/content/site.ts pebble/templates/cinematic_hero/public
git commit -m "feat(templates): cinematic_hero — generic service-business industry pack"
```

---

### Task 8: Differentiate cinematic_plumber (with reorder)

**Files:**
- Modify: `pebble/templates/cinematic_plumber/public/{hero,about}.jpg` + `gallery/01-08.jpg`
- Modify: `pebble/templates/cinematic_plumber/content/site.ts`
- Modify: `pebble/templates/cinematic_plumber/app/page.tsx` (emergency CTA before About)

- [ ] **Step 8.1: Fetch the plumber image set**

```bash
python scripts/fetch_template_images.py cinematic_plumber \
  --hero "plumber pipe wrench" \
  --gallery "plumbing service" \
  --count 8
```

- [ ] **Step 8.2: Rewrite content/site.ts with plumber-deep copy**

Replace `pebble/templates/cinematic_plumber/content/site.ts` with:

```ts
export const SITE_TITLE       = "[Your Plumbing Co.]";
export const SITE_DESCRIPTION = "Licensed local plumbers. Same-day emergency response. Up-front pricing on every job.";
export const TAGLINE          = "Pipes fixed. Right. Today.";
export const PHONE   = "[(555) 555-0100]";
export const EMAIL   = "[hello@example.com]";
export const ADDRESS = "[123 Main St, City, ST 00000]";

export const HERO_BG_IMAGE          = "/hero.jpg";
export const HERO_PILL              = "24/7 EMERGENCY SERVICE";
export const HERO_HEADLINE          = "Pipes fixed. Right. Today.";
export const HERO_SUBLINE           = "Burst pipes, slow drains, water heater out — call any time. Licensed plumber dispatched within the hour. Up-front pricing before any work starts.";
export const HERO_CTA_PRIMARY       = "Call now";
export const HERO_CTA_PRIMARY_HREF  = "tel:[(555) 555-0100]";
export const HERO_CTA_SECONDARY     = "Book online";
export const HERO_CTA_SECONDARY_HREF = "/contact";

export type Service = { id: string; title: string; description: string; icon: string };
export const SERVICES: Service[] = [
  { id: "svc-1", title: "Emergency Repairs",     description: "Burst pipes, no hot water, sewer backups. 24/7 dispatch, technician on-site within the hour in most of [city].", icon: "Siren"   },
  { id: "svc-2", title: "Drain & Sewer",         description: "Clogged drains, slow toilets, sewer-line camera inspection + hydro-jetting. We find the cause, not just the symptom.", icon: "Pipette" },
  { id: "svc-3", title: "Water Heater Service",  description: "Tank or tankless, install or repair. Same-day water-heater replacement available. Most major brands stocked on the truck.", icon: "Flame"   },
  { id: "svc-4", title: "Repipe & Remodel",      description: "Full or partial repipe. Bathroom + kitchen remodel plumbing. Licensed for new-construction permits in [city].", icon: "Wrench"  },
];

export const ABOUT_PHOTO_IMAGE = "/about.jpg";
export const ABOUT_HEADLINE    = "Master plumber. [N]+ years in [city].";
export const ABOUT_BODY        = "[Two paragraphs about your story — how you got started, what makes you different. Mention your license #, the neighborhoods you've worked in, the kind of jobs you take pride in. Keep it human.]";

export type Trust = { label: string; sub: string };
export const TRUST_BADGES: Trust[] = [
  { label: "MASTER PLUMBER", sub: "License #[number]"          },
  { label: "INSURED",        sub: "Up to $[amount]"            },
  { label: "5-STAR RATED",   sub: "[N]+ Google reviews"        },
  { label: "24/7 EMERGENCY", sub: "Same-day in most of [city]" },
];

export const TESTIMONIAL_QUOTE  = "[Pipe burst at 11pm on a Sunday — they were here in 40 minutes, fixed it, and the price was exactly what they quoted on the phone. Best plumber we've ever called.]";
export const TESTIMONIAL_AUTHOR = "[Maria T.], [City]";

export const CONTACT_HEADLINE = "Need a plumber now?";
export const CONTACT_BODY     = "Call [(555) 555-0100] for emergencies. Otherwise drop us a line — we respond within the hour during business hours.";
export const CONTACT_HOURS    = "[24/7 emergency · Office Mon–Fri 7am–6pm]";

export const CTA_BAND_HEADLINE = "Got a leak right now?";
export const CTA_BAND_BODY     = "Don't let a small drip flood your home. Same-day appointments still open this week.";
export const CTA_BAND_LABEL    = "Call now: [(555) 555-0100]";
export const CTA_BAND_HREF     = "tel:[(555) 555-0100]";

export const FOOTER_TAGLINE = "Licensed plumbers. 24/7 in [city].";

// --- Gallery page ---
export const GALLERY_HEADLINE = "Recent work.";
export const GALLERY_SUBLINE  = "Pipe repairs, water-heater swaps, repipes — real jobs in [city].";
export const GALLERY_IMAGES: Array<{ src: string; alt: string; caption?: string }> = [
  { src: "/gallery/01.jpg", alt: "[Plumbing job 1]",  caption: "[Optional caption]" },
  { src: "/gallery/02.jpg", alt: "[Plumbing job 2]",  caption: "[Optional caption]" },
  { src: "/gallery/03.jpg", alt: "[Plumbing job 3]",  caption: "[Optional caption]" },
  { src: "/gallery/04.jpg", alt: "[Plumbing job 4]",  caption: "[Optional caption]" },
  { src: "/gallery/05.jpg", alt: "[Plumbing job 5]",  caption: "[Optional caption]" },
  { src: "/gallery/06.jpg", alt: "[Plumbing job 6]",  caption: "[Optional caption]" },
  { src: "/gallery/07.jpg", alt: "[Plumbing job 7]",  caption: "[Optional caption]" },
  { src: "/gallery/08.jpg", alt: "[Plumbing job 8]",  caption: "[Optional caption]" },
];

// --- Process page ---
export const PROCESS_HEADLINE = "How a service call works.";
export const PROCESS_SUBLINE  = "From your first call to job-done. Up-front pricing, no surprises.";
export type ProcessStep = { number: string; title: string; description: string };
export const PROCESS_STEPS: ProcessStep[] = [
  { number: "01", title: "Call or book online",   description: "Tell us what's going on. We give a rough quote on the phone so you know what to expect." },
  { number: "02", title: "We diagnose on-site",   description: "Licensed plumber arrives in marked truck. We diagnose the real problem and quote the fix before we touch a wrench." },
  { number: "03", title: "We fix it. Guaranteed.", description: "Most repairs done same visit. Backed by our [N]-year workmanship guarantee — if it leaks again, we come back free." },
];

// --- FAQ page ---
export const FAQ_HEADLINE = "Common plumbing questions.";
export const FAQ_SUBLINE  = "If your question isn't here, just ask — we usually reply within the hour.";
export type FAQItem = { q: string; a: string };
export const FAQ_ITEMS: FAQItem[] = [
  { q: "Do you charge for estimates?",       a: "[Diagnostic visit is $[amount], waived if you book the repair. Phone estimates are always free for common jobs.]" },
  { q: "Are you licensed and insured?",      a: "[Yes — master plumber license #[license number], insured up to $[amount].]" },
  { q: "How fast can you respond?",          a: "[Most of [city] within 60 minutes for true emergencies (burst pipe, no water, sewer backup). Standard calls 1-2 business days.]" },
  { q: "What about after-hours rates?",      a: "[Nights, weekends, and holidays carry a $[amount] dispatch fee on top of the labor rate. Quoted up front.]" },
  { q: "Do you do tankless water heaters?",  a: "[Yes — install, repair, descale. Most major brands. Same-day swap usually possible.]" },
  { q: "What areas do you serve?",           a: "[See our service area page for the full list. Generally within [N] miles of [city].]" },
];

// --- Service area page ---
export const SERVICE_AREA_HEADLINE = "Where we serve.";
export const SERVICE_AREA_SUBLINE  = "Local, family-owned. If your town isn't listed, call — we may still come out.";
export const SERVICE_AREA_MAP_EMBED = "";
export const SERVICE_AREA_CITIES: string[] = [];

export const NAV_LINKS = [
  { label: "Services",     href: "/services"     },
  { label: "Gallery",      href: "/gallery"      },
  { label: "Process",      href: "/process"      },
  { label: "Service Area", href: "/service-area" },
  { label: "FAQ",          href: "/faq"          },
  { label: "About",        href: "/about"        },
  { label: "Contact",      href: "/contact"      },
];
```

- [ ] **Step 8.3: Reorder app/page.tsx to promote emergency CTA**

Open `pebble/templates/cinematic_plumber/app/page.tsx`. Move the `<CTABand>` import so it renders immediately after `<Hero>` and before `<Services>`. Concretely, find the section JSX (it'll look something like):

```tsx
<Hero />
<Services />
<About />
<Testimonials />
<CTABand />
<Footer />
```

And rewrite to:

```tsx
<Hero />
<CTABand />
<Services />
<About />
<Testimonials />
<Footer />
```

If the original page.tsx has additional sections (Trust badges, etc.) preserve them; just promote `<CTABand>` to be the second child after `<Hero>`. The intent is: anyone landing on a plumber's site in an emergency sees the "Call now" band immediately.

- [ ] **Step 8.4: Re-export the plumber static build**

```bash
python -m pebble.templates.export cinematic_plumber --skip-install
```

Expected: exits 0.

- [ ] **Step 8.5: Commit**

```bash
git add pebble/templates/cinematic_plumber/content/site.ts pebble/templates/cinematic_plumber/public pebble/templates/cinematic_plumber/app/page.tsx
git commit -m "feat(templates): cinematic_plumber — real plumber image pack + emergency CTA promotion"
```

---

### Task 9: Differentiate cinematic_hvac

**Files:**
- Modify: `pebble/templates/cinematic_hvac/public/...` (10 images)
- Modify: `pebble/templates/cinematic_hvac/content/site.ts`

- [ ] **Step 9.1: Fetch the HVAC image set**

```bash
python scripts/fetch_template_images.py cinematic_hvac \
  --hero "hvac technician installing" \
  --gallery "air conditioning unit" \
  --count 8
```

- [ ] **Step 9.2: Rewrite content/site.ts with HVAC-deep copy**

Replace `pebble/templates/cinematic_hvac/content/site.ts` with the same structure as Task 8.2 but with HVAC-real content:

- SITE_TITLE: `"[Your HVAC Co.]"`
- TAGLINE: `"Cool air. On demand."`
- HERO_PILL: `"FINANCING AVAILABLE"`
- HERO_HEADLINE: `"Cool air. On demand."`
- HERO_SUBLINE: `"Same-day AC repair, full system installs, and maintenance plans that catch problems before they cost you. Up-front pricing on every visit."`
- HERO_CTA_PRIMARY: `"Get a free quote"` href `"/contact"`
- HERO_CTA_SECONDARY: `"24/7 service"` href `"tel:..."`

SERVICES (4 items):
- AC Repair — `"Same-day diagnostics, parts on the truck for most major brands. Honest quote before we start the wrench."`
- Heating & Furnace — `"Gas, electric, heat pumps. Annual tune-ups + emergency repair when winter hits at the worst time."`
- New System Installation — `"High-efficiency systems sized for your home, with rebate paperwork handled for you. Financing available."`
- Maintenance Plans — `"Two visits a year, priority dispatch, no overtime fees. Catch the $200 fix before it's a $5,000 replacement."`

CTA_BAND_HEADLINE: `"AC running hot this summer?"`
CTA_BAND_BODY: `"Same-day diagnostic visits available. Don't wait for it to fully die."`
CTA_BAND_LABEL: `"Schedule a tune-up"` href `"/contact"`

FAQ items should include: financing, rebates, brand expertise (Trane, Carrier, Lennox placeholder), warranty terms.

Use Task 8.2 as the structural template. Keep all `[…]` placeholders intact for customer fill-in.

- [ ] **Step 9.3: Re-export**

```bash
python -m pebble.templates.export cinematic_hvac --skip-install
```

- [ ] **Step 9.4: Commit**

```bash
git add pebble/templates/cinematic_hvac/content/site.ts pebble/templates/cinematic_hvac/public
git commit -m "feat(templates): cinematic_hvac — real HVAC image pack + industry-deep copy"
```

---

### Task 10: Differentiate cinematic_construction

**Files:**
- Modify: `pebble/templates/cinematic_construction/public/...`
- Modify: `pebble/templates/cinematic_construction/content/site.ts`

- [ ] **Step 10.1: Fetch the construction image set**

```bash
python scripts/fetch_template_images.py cinematic_construction \
  --hero "construction worker site" \
  --gallery "construction crew" \
  --count 8
```

- [ ] **Step 10.2: Rewrite content/site.ts**

Apply the structure from Task 8.2 with these key fields:

- TAGLINE / HERO_HEADLINE: `"Built right. On time."`
- HERO_PILL: `"NOW BOOKING [SEASON] PROJECTS"`
- HERO_SUBLINE: `"General contractor for additions, remodels, and new builds. Licensed, bonded, and on a 4-week max response window for every active site."`
- HERO_CTA_PRIMARY: `"Request a bid"` href `"/contact"`
- HERO_CTA_SECONDARY: `"See past projects"` href `"/gallery"`

SERVICES (4):
- Additions & Remodels
- New Construction
- Commercial Build-Outs
- Project Management & Permits

CTA_BAND about "Free site assessment". TRUST_BADGES include "BONDED", "GENERAL CONTRACTOR LIC #[…]", "INSURED".

FAQ should cover: bid timelines, change orders, financing, lien releases, typical project length.

- [ ] **Step 10.3: Re-export**

```bash
python -m pebble.templates.export cinematic_construction --skip-install
```

- [ ] **Step 10.4: Commit**

```bash
git add pebble/templates/cinematic_construction/content/site.ts pebble/templates/cinematic_construction/public
git commit -m "feat(templates): cinematic_construction — real construction image pack + GC-deep copy"
```

---

### Task 11: Differentiate cinematic_landscaper

**Files:**
- Modify: `pebble/templates/cinematic_landscaper/public/...`
- Modify: `pebble/templates/cinematic_landscaper/content/site.ts`

- [ ] **Step 11.1: Fetch the landscaper image set**

```bash
python scripts/fetch_template_images.py cinematic_landscaper \
  --hero "landscaper mowing lawn" \
  --gallery "landscaping garden" \
  --count 8
```

- [ ] **Step 11.2: Rewrite content/site.ts**

The current landscaper site.ts (read in `pebble/templates/cinematic_landscaper/content/site.ts`) is already decent — it has weekly maintenance language. Deepen it:

- Add a 4th SERVICES item: `"Irrigation & Drainage"` description `"Sprinkler install + repair, French-drain installation, water-wise upgrades that pay for themselves in the first summer."`
- TRUST_BADGES: add `"WATER-WISE CERTIFIED"` placeholder
- FAQ items add: 1) "Do you handle HOA approvals?" 2) "What's your weekly route schedule?"

The rest stays as-is — landscaper copy was the best of the 5 already.

- [ ] **Step 11.3: Re-export**

```bash
python -m pebble.templates.export cinematic_landscaper --skip-install
```

- [ ] **Step 11.4: Commit**

```bash
git add pebble/templates/cinematic_landscaper/content/site.ts pebble/templates/cinematic_landscaper/public
git commit -m "feat(templates): cinematic_landscaper — real landscape image pack + deeper services"
```

---

### Task 12: Differentiate cinematic_dog_groomer (with reorder)

**Files:**
- Modify: `pebble/templates/cinematic_dog_groomer/public/...`
- Modify: `pebble/templates/cinematic_dog_groomer/content/site.ts`
- Modify: `pebble/templates/cinematic_dog_groomer/app/page.tsx` (gallery before services)

- [ ] **Step 12.1: Fetch the dog-groomer image set**

```bash
python scripts/fetch_template_images.py cinematic_dog_groomer \
  --hero "dog grooming bath" \
  --gallery "happy clean dog" \
  --count 8
```

- [ ] **Step 12.2: Rewrite content/site.ts with photo-led copy**

Apply structure from Task 8.2 with these key fields:

- TAGLINE / HERO_HEADLINE: `"Grooms your dog loves."`
- HERO_PILL: `"BOOK YOUR FIRST GROOM"`
- HERO_SUBLINE: `"Stress-free baths, breed-specific cuts, and a calm one-on-one room — no kennel anxiety, no rushed groomers. Just a happy dog when you pick them up."`
- HERO_CTA_PRIMARY: `"Book a groom"` href `"/contact"`
- HERO_CTA_SECONDARY: `"See our pups"` href `"/gallery"`

SERVICES (3 only — keeps focus on a small studio):
- Full Groom (Bath, Cut, Nails)
- Bath & Brush
- De-Shedding & Express Tidy

CTA_BAND: `"Open spots this week."` body `"First-time groom? We'll text you a confirmation + a 'how it went' photo afterward."`

FAQ: anxiety-prone dogs, breed expertise, vaccination requirements, drop-off vs. wait, pricing for matted coats.

TRUST_BADGES: `"CERTIFIED GROOMER"`, `"FEAR-FREE TRAINED"`, `"5-STAR RATED"`, `"LOCAL"`.

- [ ] **Step 12.3: Reorder app/page.tsx to promote gallery**

Open `pebble/templates/cinematic_dog_groomer/app/page.tsx`. Find the section ordering and move the gallery component (or a gallery preview strip if one isn't already on the home page — if not, just leave services first and skip this substep; gallery is its own page). Concretely, if you see:

```tsx
<Hero />
<Services />
<About />
<Testimonials />
<CTABand />
```

Rewrite as:

```tsx
<Hero />
<About />        {/* Build trust on the human story first */}
<Services />
<Testimonials />
<CTABand />
```

Dog-groomer customers buy on trust + photos, not feature lists. About before Services performs better.

- [ ] **Step 12.4: Re-export**

```bash
python -m pebble.templates.export cinematic_dog_groomer --skip-install
```

- [ ] **Step 12.5: Commit**

```bash
git add pebble/templates/cinematic_dog_groomer/content/site.ts pebble/templates/cinematic_dog_groomer/public pebble/templates/cinematic_dog_groomer/app/page.tsx
git commit -m "feat(templates): cinematic_dog_groomer — real groomer image pack + about-before-services reorder"
```

---

## Phase 3: Re-screenshot gallery cards

### Task 13: Build `scripts/screenshot_templates.py`

**Files:**
- Create: `scripts/screenshot_templates.py`

- [ ] **Step 13.1: Verify Chrome / Playwright is available**

```bash
python -c "from playwright.sync_api import sync_playwright; print('ok')"
```

If this fails with `ModuleNotFoundError`, install:
```bash
pip install playwright
python -m playwright install chromium
```

(Playwright is already a dev-dep in the repo per CLAUDE.md — `PEBBLE_AUTO_RUN=true` uses it.)

- [ ] **Step 13.2: Create the screenshot script**

Create `scripts/screenshot_templates.py`:

```python
"""Take a 1280x800 gallery-card screenshot of each exported template.

Requires:
  - The engine running locally (default http://127.0.0.1:8000)
  - Each template exported via `python -m pebble.templates.export <id>`

Usage:
  python scripts/screenshot_templates.py cinematic_plumber
  python scripts/screenshot_templates.py --all
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from pebble.templates.export import list_exportable_template_ids

REPO_ROOT = Path(__file__).resolve().parents[1]
PREVIEWS_DIR = REPO_ROOT / "ui" / "v3" / "public" / "templates-preview"
ENGINE_BASE = "http://127.0.0.1:8000"


def screenshot(template_id: str) -> Path:
    url = f"{ENGINE_BASE}/preview-template/{template_id}/"
    dest = PREVIEWS_DIR / f"{template_id}.png"
    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=2)
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle", timeout=30_000)
        # Give Framer Motion entrance animations a beat to settle
        page.wait_for_timeout(800)
        page.screenshot(path=str(dest), full_page=False)
        browser.close()
    print(f"  wrote {dest.relative_to(REPO_ROOT)}")
    return dest


def _main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("template_id", nargs="?")
    p.add_argument("--all", action="store_true")
    args = p.parse_args()
    if args.all:
        ids = [i for i in list_exportable_template_ids() if i.startswith("cinematic_")]
    elif args.template_id:
        ids = [args.template_id]
    else:
        p.error("pass a template_id or --all")
        return 2
    for tid in ids:
        try:
            screenshot(tid)
        except Exception as e:
            print(f"[{tid}] FAIL: {e}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
```

- [ ] **Step 13.3: Smoke-run on cinematic_hero**

Engine must be running. Then:
```bash
python scripts/screenshot_templates.py cinematic_hero
```

Expected: writes `ui/v3/public/templates-preview/cinematic_hero.png`. Open it — it should now show the new generic-service hero image, not the old dark blurry one.

- [ ] **Step 13.4: Run on all 6**

```bash
python scripts/screenshot_templates.py --all
```

Expected: 6 PNGs replaced. Spot-check that cinematic_plumber.png shows pipes/wrench, cinematic_dog_groomer.png shows a dog, etc. If any are still wrong, debug per-skin first before continuing.

- [ ] **Step 13.5: Commit**

```bash
git add scripts/screenshot_templates.py ui/v3/public/templates-preview/cinematic_*.png
git commit -m "feat(templates): re-screenshot 6 cinematic_* gallery cards with industry differentiation"
```

---

## Phase 4: End-to-end Validation

### Task 14: Verify the gallery + previews work end-to-end

**Files:** None modified — pure verification.

- [ ] **Step 14.1: Restart engine fresh**

Kill any running engine, then from the worktree:
```bash
python pebble_engine.py --port 8000 &
sleep 3
curl -s http://127.0.0.1:8000/api/health | head -c 200
```

Expected: JSON with `"ok": true` (or similar).

- [ ] **Step 14.2: Start v3 dev**

```bash
cd ui/v3 && npx next dev -p 3001 &
sleep 8
```

- [ ] **Step 14.3: Sanity-check the gallery cards in the browser**

Marc will need to open `http://localhost:3001/templates` himself and confirm:
- Each cinematic_* card shows a clearly different hero image
- Clicking each card opens the preview pane WITHOUT the sad-mug icon
- The preview iframe shows the actual exported template

Subagent: report this step as "needs Marc verification" — do not falsely report a pass.

- [ ] **Step 14.4: Run the full Python test suite to confirm no regression**

```bash
python -m pytest -q
```

Expected: full suite passes, including the two new tests added in Tasks 3 and 4.

- [ ] **Step 14.5: Final commit (if anything was missed)**

If `git status` is clean, skip. Otherwise:
```bash
git add -A
git commit -m "chore(templates): final cleanup after cinematic differentiation"
```

---

## Self-Review

**1. Spec coverage:**
- ✅ "Real industry differentiation" — Tasks 7–12 cover all 6 templates with image fetch + copy rewrite + (where flagged) module reorder
- ✅ "Static export instead of 24 dev servers" — Tasks 1–4 build the export infra + engine route
- ✅ "Iframe loads correctly" — Task 5 + 14
- ✅ "Re-screenshot the gallery cards" — Task 13
- ✅ "Easier way to have the live preview ready to fire" — static export = $0 + instant, no dev server needed

**2. Placeholder scan:**
- One soft hedge in Task 11.2 ("the current landscaper site.ts is already decent — deepen it") — but the actual deltas (4th service, FAQ items, badges) are spelled out concretely. Acceptable.
- No "TBD" / "TODO" / "fill in details" anywhere.
- Tasks 9 and 10 reference Task 8.2 as the "structural template" but spell out every distinguishing field — that's fine because a subagent reading Task 9 in isolation will look up Task 8.2 once.

**3. Type consistency:**
- `template_id` is the consistent term across export.py, the engine route, and the screenshot script.
- `preview_url` (registry) → `/preview-template/<id>/` (engine path) → `iframeSrc` prefix logic in v3 — all aligned.
- `out/` is the consistent next-build output directory.

**4. Risk callouts to flag for the executor:**
- The first time Task 2.3 runs, `npm install` will need to run for each of the 5 skins (since the cloned skins inherited the cinematic_hero `node_modules` if it existed at clone time — if not, they need install). Budget extra time on the first run.
- Server actions + `output: "export"` is the most likely failure mode. If Task 1.4 fails with a server-action error, the fix is in the contact.ts replacement (Task 1.3) — make sure no real email-sending code is imported in that file.
- The screenshot step (Task 13.4) requires the engine to be running AND every skin exported. Run Tasks 7–12 fully before Task 13.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-24-cinematic-skin-differentiation.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Estimated ~6-8 hours of wall-clock for 14 tasks.

**2. Inline Execution** — Execute tasks in this session, batched with checkpoints. Slower because tasks share context.

Which approach?
