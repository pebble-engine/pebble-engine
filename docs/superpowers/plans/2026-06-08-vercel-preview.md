# Vercel-Deployments-API Preview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Serve a generated site's in-workspace preview from a real Vercel deployment (built on Vercel's infra with full SSR) instead of a local `next dev`, so previews work on the Node-less Railway engine while preserving Server Actions + image optimization.

**Architecture:** A pure-Python `pebble/vercel_deploy.py` collects a generated site's source files, POSTs them inline to Vercel's `POST /v13/deployments` (Vercel runs `npm install` + `next build`), polls `readyState`, and stores the resulting preview URL at `output/<slug>/.vercel-preview.json`. The engine's `/preview/<slug>/` handler, when `PEBBLE_PREVIEW_BACKEND=vercel`, **proxies** that Vercel URL (fetch + inject the existing visual-edit bridge) so the workspace iframe stays same-origin and click-to-edit keeps working. A deploy is created after a successful build and after LLM refines — NOT per visual-edit (those stay client-side/optimistic and persist to source for the next deploy).

**Tech Stack:** Python stdlib + `httpx` (already a transitive dep), Vercel REST API v13, the engine's existing `_handle_preview` proxy + `PEBBLE_VISUAL_EDIT_BRIDGE` injection.

**Design decisions (locked):**
- **Cadence:** deploy after build + after LLM refine. Visual-edits are client-side optimistic, written to source, reflected on the next deploy. (A Vercel build is ~1–2 min — too slow per keystroke.)
- **Bridge:** engine proxies the Vercel URL (same-origin `/preview/<slug>/`) and injects the bridge — never iframe the raw `*.vercel.app` (cross-origin kills click-to-edit).
- **Secrets:** preview deploys WITHOUT Resend keys; the generated `lib/email.ts` already returns null with no key, so the contact form validates but doesn't send in preview. (Publish handles real secrets separately.)
- **Integrity gate:** never deploy a build whose `build_meta.broken_files` is non-empty (truncation guard) — fail fast with a clear message.
- **Env (the secret channel, `.env`):** `VERCEL_TOKEN` (required), `VERCEL_TEAM_ID` (the Squito LLC team id, required for team-scoped deploys), `PEBBLE_PREVIEW_BACKEND=vercel` (opt-in flag).

**File structure:**
- Create `pebble/vercel_deploy.py` — all Vercel API logic (config, file collection, create, poll, orchestrate, store URL).
- Create `tests/test_vercel_deploy.py` — mocked-HTTP unit tests.
- Modify `pebble_engine.py` `_handle_preview` — add a `vercel` proxy branch (mirror the existing Fly proxy branch).
- Modify `pebble/server/build.py` post-build chain — trigger `deploy_preview` behind the flag, gated on integrity.
- Modify `pebble/server/refine.py` — refresh the Vercel preview after a successful LLM refine (behind the flag).

---

### Task 1: Config + file collection

**Files:**
- Create: `pebble/vercel_deploy.py`
- Test: `tests/test_vercel_deploy.py`

- [ ] **Step 1: Write failing tests**
```python
from pathlib import Path
from pebble import vercel_deploy as vd

def test_not_configured_without_token(monkeypatch):
    monkeypatch.delenv("VERCEL_TOKEN", raising=False)
    assert vd.vercel_configured() is False

def test_configured_with_token(monkeypatch):
    monkeypatch.setenv("VERCEL_TOKEN", "tok")
    assert vd.vercel_configured() is True

def test_collect_files_skips_artifacts(tmp_path):
    site = tmp_path / "site"
    (site / "app").mkdir(parents=True)
    (site / "node_modules" / "x").mkdir(parents=True)
    (site / ".next").mkdir()
    (site / "app" / "page.tsx").write_text("export default ()=>null", encoding="utf-8")
    (site / "package.json").write_text('{"name":"x"}', encoding="utf-8")
    (site / "node_modules" / "x" / "y.js").write_text("//dep", encoding="utf-8")
    files = vd.collect_files(site)
    paths = {f["file"] for f in files}
    assert "app/page.tsx" in paths and "package.json" in paths
    assert not any("node_modules" in p or ".next" in p for p in paths)
    assert all("data" in f for f in files)  # inline form {file, data}
```
- [ ] **Step 2:** Run `python -m pytest tests/test_vercel_deploy.py -q` → FAIL (module missing).
- [ ] **Step 3: Implement**
```python
"""Deploy a generated site to Vercel via the Deployments REST API (v13).

Lets the Node-less Railway engine produce a fully-built (SSR) preview: we POST
the site's SOURCE files inline; Vercel runs npm install + next build on their
infra and returns a preview URL. No Node needed on our server.
"""
from __future__ import annotations
import os, json, time
from pathlib import Path
from typing import Any, Optional

_SKIP = {"node_modules", ".next", ".turbo", "dist", "out", ".git", ".vercel"}
_API = "https://api.vercel.com"

def vercel_configured() -> bool:
    return bool(os.environ.get("VERCEL_TOKEN", "").strip())

def _team_qs() -> str:
    tid = os.environ.get("VERCEL_TEAM_ID", "").strip()
    return f"?teamId={tid}" if tid else ""

def collect_files(site_dir: Path) -> list[dict[str, Any]]:
    """Inline {file, data} list of the site's source (text files only).
    Binary assets are skipped — generated sites use remote (Pexels) images."""
    site_dir = Path(site_dir)
    out: list[dict[str, Any]] = []
    for p in sorted(site_dir.rglob("*")):
        if p.is_dir() or any(part in _SKIP for part in p.parts):
            continue
        try:
            data = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # skip binary/unreadable for v1
        out.append({"file": p.relative_to(site_dir).as_posix(), "data": data})
    return out
```
- [ ] **Step 4:** Run tests → PASS.
- [ ] **Step 5:** Commit `feat(vercel): config + source file collection`.

### Task 2: Create deployment (mocked HTTP)

**Files:** Modify `pebble/vercel_deploy.py`; Test `tests/test_vercel_deploy.py`

- [ ] **Step 1: Write failing test** (mock httpx so no real network)
```python
def test_create_deployment_posts_files_and_returns_id_url(monkeypatch):
    import pebble.vercel_deploy as vd
    monkeypatch.setenv("VERCEL_TOKEN", "tok")
    captured = {}
    class _Resp:
        status_code = 200
        def json(self): return {"id": "dpl_1", "url": "gen-abc.vercel.app"}
        def raise_for_status(self): pass
    def fake_post(url, **kw):
        captured["url"] = url; captured["json"] = kw.get("json"); captured["headers"] = kw.get("headers")
        return _Resp()
    monkeypatch.setattr(vd.httpx, "post", fake_post)
    res = vd.create_deployment([{"file": "package.json", "data": "{}"}], name="mysite")
    assert res["id"] == "dpl_1"
    assert res["url"].startswith("https://gen-abc.vercel.app")
    assert "/v13/deployments" in captured["url"]
    assert captured["headers"]["Authorization"] == "Bearer tok"
    assert captured["json"]["name"] == "mysite"
    assert captured["json"]["files"][0]["file"] == "package.json"
    assert captured["json"]["projectSettings"]["framework"] == "nextjs"
```
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3: Implement** (add `import httpx` at top)
```python
def create_deployment(files: list[dict], *, name: str, production: bool = False,
                      timeout: float = 60.0) -> dict[str, str]:
    token = os.environ["VERCEL_TOKEN"].strip()
    body = {
        "name": name,
        "files": files,
        "target": "production" if production else None,
        "projectSettings": {"framework": "nextjs"},
    }
    body = {k: v for k, v in body.items() if v is not None}
    resp = httpx.post(
        f"{_API}/v13/deployments{_team_qs()}",
        params={"skipAutoDetectionConfirmation": "1"},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=body, timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    raw = data.get("url") or ""
    url = raw if raw.startswith("http") else f"https://{raw}"
    return {"id": data.get("id", ""), "url": url}
```
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit `feat(vercel): create deployment from inline files`.

### Task 3: Poll deployment state (mocked)

**Files:** Modify `pebble/vercel_deploy.py`; Test same.

- [ ] **Step 1: Failing test** — sequence BUILDING→READY; asserts it returns "READY" and the final URL.
```python
def test_poll_returns_ready(monkeypatch):
    import pebble.vercel_deploy as vd
    monkeypatch.setenv("VERCEL_TOKEN", "tok")
    states = iter(["BUILDING", "READY"])
    class _Resp:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return {"readyState": next(states), "url": "gen-abc.vercel.app"}
    monkeypatch.setattr(vd.httpx, "get", lambda url, **kw: _Resp())
    monkeypatch.setattr(vd.time, "sleep", lambda *_: None)
    state = vd.poll_deployment("dpl_1", interval=0, timeout=10)
    assert state["readyState"] == "READY"
```
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3: Implement**
```python
def poll_deployment(deployment_id: str, *, interval: float = 3.0,
                    timeout: float = 240.0) -> dict[str, Any]:
    token = os.environ["VERCEL_TOKEN"].strip()
    deadline = time.time() + timeout
    last: dict[str, Any] = {}
    while time.time() < deadline:
        resp = httpx.get(
            f"{_API}/v13/deployments/{deployment_id}{_team_qs()}",
            headers={"Authorization": f"Bearer {token}"}, timeout=30.0,
        )
        resp.raise_for_status()
        last = resp.json()
        rs = last.get("readyState") or last.get("status")
        if rs in ("READY", "ERROR", "CANCELED"):
            return last
        time.sleep(interval)
    return {**last, "readyState": last.get("readyState") or "TIMEOUT"}
```
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit `feat(vercel): poll deployment readyState`.

### Task 4: Orchestrate `deploy_preview(slug)` + persist URL

**Files:** Modify `pebble/vercel_deploy.py`; Test same.

- [ ] **Step 1: Failing test** — monkeypatch `collect_files`/`create_deployment`/`poll_deployment`; assert it writes `output/<slug>/.vercel-preview.json` with the URL and returns it; assert a `broken_files`-flagged build raises/returns error without deploying.
```python
def test_deploy_preview_writes_state(tmp_path, monkeypatch):
    import pebble.vercel_deploy as vd
    out = tmp_path / "output"; (out / "s1" / "site" / "app").mkdir(parents=True)
    (out / "s1" / "site" / "app" / "page.tsx").write_text("export default ()=>null", encoding="utf-8")
    (out / "s1" / "build_meta.json").write_text(json.dumps({"broken_files": []}), encoding="utf-8")
    monkeypatch.setattr(vd, "_output_dir", lambda: out)
    monkeypatch.setattr(vd, "create_deployment", lambda files, **k: {"id": "dpl_1", "url": "https://x.vercel.app"})
    monkeypatch.setattr(vd, "poll_deployment", lambda i, **k: {"readyState": "READY", "url": "x.vercel.app"})
    res = vd.deploy_preview("s1")
    assert res["url"] == "https://x.vercel.app"
    saved = json.loads((out / "s1" / ".vercel-preview.json").read_text())
    assert saved["url"] == "https://x.vercel.app"

def test_deploy_preview_refuses_broken_build(tmp_path, monkeypatch):
    import pebble.vercel_deploy as vd
    out = tmp_path / "output"; (out / "s1" / "site").mkdir(parents=True)
    (out / "s1" / "build_meta.json").write_text(json.dumps({"broken_files": [{"file": "a.tsx"}]}), encoding="utf-8")
    monkeypatch.setattr(vd, "_output_dir", lambda: out)
    res = vd.deploy_preview("s1")
    assert res.get("error")
```
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3: Implement** (`_output_dir` reads the engine module like other pebble.server modules; `deploy_preview` slugifies a Vercel-safe `name`, gates on integrity, creates+polls, writes `.vercel-preview.json`)
```python
import re, sys
def _output_dir() -> Path:
    eng = sys.modules.get("pebble_engine") or sys.modules["__main__"]
    return eng.OUTPUT_DIR

def _vercel_name(slug: str) -> str:
    n = re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-")[:90] or "pebble-site"
    return n

def deploy_preview(slug: str) -> dict[str, Any]:
    if not vercel_configured():
        return {"error": "VERCEL_TOKEN not configured"}
    out = _output_dir() / slug
    meta = {}
    mp = out / "build_meta.json"
    if mp.exists():
        try: meta = json.loads(mp.read_text(encoding="utf-8"))
        except Exception: meta = {}
    if meta.get("broken_files"):
        return {"error": "build has incomplete files — fix before previewing"}
    files = collect_files(out / "site")
    if not files:
        return {"error": "no source files to deploy"}
    created = create_deployment(files, name=_vercel_name(slug))
    final = poll_deployment(created["id"])
    if final.get("readyState") != "READY":
        return {"error": f"vercel build {final.get('readyState')}", "id": created["id"]}
    url = created["url"]
    (out / ".vercel-preview.json").write_text(
        json.dumps({"url": url, "deployment_id": created["id"],
                    "deployed_at": _now_iso()}, indent=2), encoding="utf-8")
    return {"url": url, "deployment_id": created["id"]}
```
(Define `_now_iso()` with `from datetime import datetime, timezone` — `datetime.now(timezone.utc).isoformat()`.)
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit `feat(vercel): deploy_preview orchestration + state file`.

### Task 5: Serve `/preview/<slug>/` by proxying the Vercel URL (+ bridge)

**Files:** Modify `pebble_engine.py` `_handle_preview` (the Fly proxy branch is the template).

- [ ] **Step 1:** Read `_handle_preview` and the existing `PEBBLE_PREVIEW_BACKEND=fly` proxy branch (it fetches a remote URL and serves the body). Note how `PEBBLE_VISUAL_EDIT_BRIDGE` is injected before `</body>` for HTML responses in workspace (non-public) mode.
- [ ] **Step 2:** Add a branch: when `os.environ.get("PEBBLE_PREVIEW_BACKEND") == "vercel"` and `output/<slug>/.vercel-preview.json` exists, read its `url`, fetch `<url>/<rel-path>` with httpx, and serve the response — injecting the visual-edit bridge into HTML exactly as the local path does. If the state file is missing, fall back to the existing on-demand splash ("Still warming up…") which now means "Vercel build in progress".
- [ ] **Step 3:** Manual check: with a hand-written `.vercel-preview.json` pointing at any public URL, hit `/preview/<slug>/` and confirm the engine proxies + injects the bridge.
- [ ] **Step 4:** Commit `feat(preview): vercel proxy branch in _handle_preview`.

### Task 6: Trigger deploy after build + refine (behind the flag, integrity-gated)

**Files:** Modify `pebble/server/build.py` (post-build chain), `pebble/server/refine.py` (after successful LLM refine).

- [ ] **Step 1:** In `run_build`'s post-build chain, after `build_meta` is written, if `PEBBLE_PREVIEW_BACKEND == "vercel"` and `not integrity["broken_files"]`, call `vercel_deploy.deploy_preview(slug)` in a daemon thread (don't block the build response); emit a `preview_building` SSE event, then `preview_ready` with the URL when done. Mirror the existing dev-server warmup threading.
- [ ] **Step 2:** In `_run_llm_refinement`, after a successful (non-reverted) refine, if the flag is on, kick the same `deploy_preview` refresh in a daemon thread.
- [ ] **Step 3:** Tests: assert `run_build`/refine call `deploy_preview` when the flag is set and skip it when `broken_files` is non-empty (monkeypatch `vercel_deploy.deploy_preview` to record calls).
- [ ] **Step 4:** Commit `feat(preview): deploy to vercel after build + refine`.

### Task 7: Live verification (requires `VERCEL_TOKEN` + `VERCEL_TEAM_ID`)

- [ ] **Step 1:** Marc adds `VERCEL_TOKEN` + `VERCEL_TEAM_ID` to `.env` (secret channel).
- [ ] **Step 2:** Locally: `PEBBLE_PREVIEW_BACKEND=vercel python -c "from pebble.vercel_deploy import deploy_preview; print(deploy_preview('<an existing slug>'))"` → confirm it returns a READY `*.vercel.app` URL that loads the real site (SSR, contact form present).
- [ ] **Step 3:** Open `/preview/<slug>/` through the engine and confirm the proxied preview renders + the visual-edit bridge works (click-to-edit).
- [ ] **Step 4:** Note Vercel build time + any quota/cost in the session log.

### Task 8: v3 "preview building on Vercel" state

**Files:** Modify the workspace preview iframe wrapper to show a "Building your preview… (~1–2 min)" state while `.vercel-preview.json` is absent / the `preview_building` SSE event is active, swapping to the iframe on `preview_ready`.

- [ ] **Step 1:** Reuse the existing draft-phase/preview-ready event handling; add the building copy.
- [ ] **Step 2:** `npx tsc --noEmit` + `npm run build` clean.
- [ ] **Step 3:** Commit `feat(v3): vercel preview-building state`.

### Task 9: Card thumbnail — screenshot the deployed preview (Cloudflare Browser Rendering)

**Why:** dashboard `ProjectCard` already shows `output/<slug>/screenshots/01-hero.png` when present (else a DNA-color gradient). Playwright can't run on Railway, so prod cards are always gradients. Once a build has a live Vercel URL, screenshot it with Cloudflare Browser Rendering (Marc already has `CLOUDFLARE_ACCOUNT_ID` + `CLOUDFLARE_API_TOKEN`) and write that PNG to the existing path — the card lights up with zero card changes.

**Files:** Create `pebble/screenshot.py`; Test `tests/test_screenshot.py`; call it from `deploy_preview` after READY.

- [ ] **Step 1: Failing test** (mock httpx) — `capture_to_png(url)` POSTs to the CF endpoint with the URL + bearer token and returns PNG bytes; `screenshot_project(slug, url)` writes `output/<slug>/screenshots/01-hero.png`.
```python
def test_capture_posts_to_cf(monkeypatch):
    import pebble.screenshot as ss
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "acc"); monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    seen = {}
    class _R:
        status_code = 200; content = b"\x89PNG..."
        def raise_for_status(self): pass
    def fake_post(url, **kw): seen["url"]=url; seen["json"]=kw.get("json"); seen["headers"]=kw.get("headers"); return _R()
    monkeypatch.setattr(ss.httpx, "post", fake_post)
    png = ss.capture_to_png("https://x.vercel.app")
    assert png.startswith(b"\x89PNG")
    assert "/browser-rendering/screenshot" in seen["url"] and "acc" in seen["url"]
    assert seen["json"]["url"] == "https://x.vercel.app"
    assert seen["headers"]["Authorization"] == "Bearer tok"
```
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3: Implement** `pebble/screenshot.py`:
```python
import os, httpx
from pathlib import Path
_CF = "https://api.cloudflare.com/client/v4"
def configured() -> bool:
    return bool(os.environ.get("CLOUDFLARE_ACCOUNT_ID") and os.environ.get("CLOUDFLARE_API_TOKEN"))
def capture_to_png(url: str, *, timeout: float = 60.0) -> bytes:
    acc = os.environ["CLOUDFLARE_ACCOUNT_ID"].strip(); tok = os.environ["CLOUDFLARE_API_TOKEN"].strip()
    r = httpx.post(f"{_CF}/accounts/{acc}/browser-rendering/screenshot",
                   headers={"Authorization": f"Bearer {tok}"},
                   json={"url": url, "viewport": {"width": 1280, "height": 800},
                         "gotoOptions": {"waitUntil": "networkidle0"}},
                   timeout=timeout)
    r.raise_for_status()
    return r.content
def screenshot_project(output_dir: Path, slug: str, url: str) -> Path | None:
    if not configured(): return None
    try: png = capture_to_png(url)
    except Exception: return None
    dest = Path(output_dir) / slug / "screenshots" / "01-hero.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(png)
    return dest
```
- [ ] **Step 4:** Run → PASS. In `vercel_deploy.deploy_preview`, after READY, best-effort `screenshot.screenshot_project(_output_dir(), slug, url)` in the same daemon thread.
- [ ] **Step 5:** Note: the existing `CLOUDFLARE_API_TOKEN` may need the **Browser Rendering – Edit** permission added (Marc, one-time in the Cloudflare token settings). Commit `feat(preview): card thumbnail via Cloudflare Browser Rendering`.

---

## Self-review notes
- **Binary assets:** v1 skips non-utf-8 files (generated sites use remote images). If a build ever ships local binary assets, add base64 `{file, data, encoding:"base64"}` support — flagged, not silently dropped.
- **Cost/quota:** every build + refine = a Vercel deployment. For beta volume this is fine; revisit if it grows. The integrity gate prevents wasting builds on broken sites.
- **Publish:** this same module is the natural basis for SSR publish (`production=True`) later — supersedes the static Cloudflare path for SSR sites. Out of scope here.
