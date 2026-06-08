# Container preview fleet (Fly Machines + HMR) — design spec

**Date:** 2026-06-08
**Status:** Approved approach (Marc). Spec for review; build on branch `claude/prod-preview-fixes`. No Fly/prod changes until Marc returns with a Fly token.

## Goal

Replace the broken `next dev`-on-the-engine preview with a **fleet of per-user Fly Machines** that each run the user's site under `next dev`, so:
- Previews work even though the Railway engine has no Node.
- Edits feel **instant** (<0.5s) via Hot Module Replacement — no per-edit rebuild.
- It scales multi-tenant without the Vercel cost/queueing/ToS problems NLM flagged.

**Scale target:** ~50 concurrent active previews (config-extensible).

**Non-goals:** publishing customers' production sites (separate effort — Cloudflare Direct Upload or user-owned-Vercel OAuth); building for hundreds of concurrent users now.

## Key insight (makes it fast + cheap)

Every Pebble site shares the **same foundation dependencies** (next, react, framer-motion, gsap, resend, etc.). So we **pre-bake `node_modules` into the Fly machine image once**. A machine boots with deps already present; the engine only ever ships the **source files** (`app/`, `components/`, `content/`, configs — a few KB). No `npm install` per preview. If a build ever needs an extra dep, the receiver runs a quick `npm install <pkg>` delta (rare).

## Architecture

```
Browser (workspace)
   │  iframe src = https://<machine>.fly.dev   (DIRECT — HMR websocket works natively)
   │  postMessage ↔ parent for click-to-edit (cross-origin, by design)
   ▼
Fly Machine (per slug, micro-VM, isolated)
   ├─ receiver/proxy (public :8080)  ← engine pushes source here; reverse-proxies to next dev;
   │                                    injects the visual-edit bridge into HTML; passes WS through
   └─ next dev (internal :3000)      ← HMR watches the synced files
   ▲
   │  Fly Machines REST API (start/stop/list) + POST /sync (source files, shared-secret auth)
Railway engine (Python)
   └─ pebble/fly_fleet.py: ensure_machine(slug) · sync_files(slug, files) · stop_idle() · registry
```

**Why the iframe points at the machine directly (not proxied through the engine):** `next dev` HMR uses a websocket to the page's origin. The Python `http.server` engine can't cleanly proxy websockets. Pointing the iframe at the machine makes HMR native. The **machine's receiver injects the visual-edit bridge**, so click-to-edit still works; the bridge talks to the parent workspace via cross-origin `postMessage` (which is designed for exactly this).

## Components

### 1. Machine image — `fleet/preview-machine/` (new dir)
- `Dockerfile`: base `node:20-slim`; copy a canonical Pebble site skeleton's `package.json`; `npm ci` so `node_modules` is **baked in**; copy `receiver.mjs`; `CMD` starts the receiver.
- `receiver.mjs` (Node): a small HTTP server on `:8080` that:
  - `POST /sync` (auth: `x-pebble-secret` == `PEBBLE_FLEET_SECRET`): body `{files:[{path,data}]}` → write each into the working dir (`/site`), creating dirs. On first sync, also (re)start `next dev` if not running. Triggers HMR via the file writes.
  - `GET /healthz` → `{ ready: bool }` (next dev compiled + responding on :3000).
  - `* (all other paths)` → reverse-proxy to `http://127.0.0.1:3000` (next dev), **passing websockets through** (HMR), and **injecting `PEBBLE_VISUAL_EDIT_BRIDGE`** into `text/html` responses before `</body>`.
- Entry: launches the receiver; receiver lazily spawns `next dev -p 3000` in `/site` after the first `/sync`.

### 2. Engine fleet client — `pebble/fly_fleet.py` (new)
- `fleet_configured()` → `FLY_API_TOKEN` + `FLY_APP` + `PEBBLE_FLEET_SECRET` present.
- `ensure_machine(slug)` → if a machine is registered+alive for slug, return its URL; else create/start a machine from the image (Fly Machines API `POST /v1/apps/<app>/machines`), register `slug → {machine_id, url, last_seen}`, return URL.
- `sync_files(slug, files)` → POST the source files to the machine's `/sync` with the shared secret.
- `touch(slug)` / `stop_idle(max_idle_s)` → idle reaper (stop machines unused > N min; Fly bills stopped machines minimally). Concurrency cap (`PEBBLE_FLEET_MAX`, default 50).
- Registry persisted at `output/.fleet/registry.json` (survive engine restarts; re-validate liveness like dev_registry).

### 3. Engine wiring
- New backend value `PEBBLE_PREVIEW_BACKEND=fly-fleet`.
- On workspace open / build complete / refine: `ensure_machine(slug)` + `sync_files(slug, collect_source(slug))` (full sync on open/build; **delta** sync on refine/visual-edit — just changed files).
- Expose the machine URL to the frontend: a small `GET /api/projects/<slug>/preview-url` (owner-gated) returns `{url, ready}`; the workspace iframes it once ready (and shows the "building…" splash until `/healthz` is ready).
- `collect_source(slug)` reuses `vercel_deploy.collect_files` (same skip rules), minus `node_modules` (baked in image).

### 4. Frontend (v3)
- Workspace preview: instead of `/preview/<slug>/` (engine-served), poll `GET /api/projects/<slug>/preview-url`; show "Building your preview…" until `ready`, then iframe the machine URL. Click-to-edit bridge messages already arrive via `postMessage` (cross-origin-safe).

## Data flow
1. User opens workspace → engine `ensure_machine(slug)` (boot ~1–3s warm image, no npm install) → `sync_files` full source → machine starts `next dev` → `/healthz` flips ready (~3–10s first compile).
2. Frontend polls preview-url → ready → iframes machine URL → site renders (SSR, real contact form, real images).
3. User refines / click-to-edits → engine writes source + `sync_files` delta → next dev HMR → iframe repaints **<0.5s**.
4. Idle > N min → reaper stops the machine (scale-to-zero). Next open restarts it.

## Security
- Fly Machines are micro-VMs → generated (untrusted) code is isolated per user.
- Receiver `/sync` requires `PEBBLE_FLEET_SECRET` (engine↔machine shared secret) so only the engine can push files.
- Machine URLs are unguessable; previews carry **no real secrets** (no `RESEND_API_KEY` in the machine → the contact form validates but doesn't send, which is correct for a preview).
- Per-slug ownership enforced at the `preview-url` endpoint (`require_project_owner`).

## Cost guardrails (~50 concurrent)
- Scale-to-zero: stopped machines cost ~nothing; only active previews bill.
- `PEBBLE_FLEET_MAX` concurrency cap; idle reaper (default 15 min).
- One shared image (no per-build image builds). Source sync is KB-scale.
- Rough: ~50 small shared-CPU machines active ≈ low-tens of $/mo; far under Vercel Enterprise.

## Prerequisites (Marc, when back)
- `FLY_API_TOKEN`, `FLY_APP` (a Fly app to host the fleet), `PEBBLE_FLEET_SECRET` (random) → `.env`.
- Deploy the machine image once (`fly deploy` from `fleet/preview-machine/`) so machines can be cloned from it.

## What gets built now (no Fly access needed)
- `pebble/fly_fleet.py` + mocked tests (Fly API + sync mocked).
- `fleet/preview-machine/` (Dockerfile + receiver.mjs) — code, deployed later.
- Engine wiring + `preview-url` endpoint (behind the flag, default off).
- Frontend building-state + iframe-machine-url.
**Live verification (boot a real machine, HMR timing) waits for Marc's Fly token.**

## Open questions (defaults chosen; revisit on review)
- Warm-pool of pre-started machines for instant first-open? Deferred (start-on-demand is fine at ~50 concurrent; revisit if cold-start feels slow).
- Delta vs full sync threshold — full on open/build, delta on edits.
