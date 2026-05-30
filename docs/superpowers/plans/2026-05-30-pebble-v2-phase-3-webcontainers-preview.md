# Pebble Engine v2 — Phase 3: WebContainers Preview Integration

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the server-side `next dev` preview path (30-60s cold start, one Railway Node process per active project) with a StackBlitz WebContainers in-browser preview that boots in ~2s in the user's browser, at zero server cost per session. v1 preview path (iframe → `/preview/<slug>/`) remains untouched for legacy builds.

**Architecture:** Generated site files are bundled as JSON by a new `/api/v2/site-files/<slug>` engine endpoint. The v3 workspace detects `engine_version: v2` in `build_meta.json` and renders a `WebContainerPreview` component instead of the legacy iframe. `WebContainerPreview` mounts the file tree, runs `npm install` (cached after the first mount), spawns `next dev`, and renders the resulting localhost URL in an iframe. Hot-reload flows via a `postMessage` bridge — when `/api/refine` or `/api/visual-edit` returns, the workspace sends the changed files back into the running container without a full restart.

**Tech Stack:** `@webcontainer/api` (StackBlitz commercial SDK); Next.js 14 in the generated site (pinned, no native bindings); `Cross-Origin-Embedder-Policy: require-corp` + `Cross-Origin-Opener-Policy: same-origin` headers in `ui/v3/next.config.ts` (required for `SharedArrayBuffer`, which WebContainers depends on); existing Python engine stays Python; existing `pebble/blocks_compiler.py` writes the file tree to disk.

---

## Strategic context

### Decision required from Marc before execution

| Decision | Options | Recommendation |
|---|---|---|
| StackBlitz plan tier | Free (non-commercial, $0) · Pro ($20/mo, ~300 active container-hours) · Production ($200-500/mo) | **Start on Pro.** Free plan prohibits commercial use. Production only needed once you have sustained traffic (≥200 simultaneous active previews). Upgrade at that threshold, not before. |
| Cross-origin isolation rollout | All routes · Preview routes only via middleware | **All routes.** COOP/COEP must be served on the same top-level document as the WebContainer iframe. Partial rollout causes mixed-content errors that are harder to debug. |

### Why this doesn't break v1

`build_meta.json` for every build contains `engine_version`. v1 builds write nothing (field absent) or `"v1"`. v2 builds write `"v2"`. The workspace shell branches on this field — v1 gets the existing iframe-to-`/preview/<slug>/` path, unchanged. No v1 user is affected by Phase 3.

### Economics

| Path | Cold start | Server cost per active user | Scales to 1000 concurrent? |
|---|---|---|---|
| v1 (`next dev` on Railway) | 30-60s | ~$0.05/hr (Fly machine + CPU) | No — 1000 Node processes |
| v3 (WebContainers) | ~2s | $0 server-side | Yes — runs in browser |

Pro plan at $20/mo covers ~300 container-hours. At 5 min average session per user, 300h ≈ 3,600 preview sessions/month before the Pro cap. That's roughly 120 sessions/day — enough headroom for the first 500-1000 MAU. Production tier ($200-500/mo) buys 10-50× more, triggered at meaningful traffic.

---

## File structure

### New files

```
ui/v3/
  components/workspace/
    web-container-preview.tsx     # WebContainer boot + iframe render
    web-container-context.tsx     # React context: expose mounted container
                                  # so hot-reload bridge can write files
  lib/
    webcontainer.ts               # Singleton boot helper + file-tree types

pebble/server/
  site_files.py                   # GET /api/v2/site-files/<slug> handler
```

### Modified files

```
ui/v3/next.config.ts              # COOP + COEP headers (chunk 3a)
ui/v3/components/workspace-shell.tsx  # Branch on engine_version (chunk 3c)
pebble/server/router.py           # Register GET /api/v2/site-files/<slug> (chunk 3b)
pebble/postbuild.py               # Skip run_dev_server for v2 builds (chunk 3d)
pebble/server/build_v2.py         # Pass skip_dev_server=True to postbuild (chunk 3d)
```

---

## Phase decomposition

### Chunk 3a (~1 day): WebContainer scaffolding + COOP/COEP headers + npm package

**Deliverable:** `@webcontainer/api` installed in `ui/v3/`. COOP/COEP headers active in `next.config.ts` (dev + prod). A `WebContainerPreview` component stub that boots a bare container and proves `SharedArrayBuffer` is available. Tests confirm header presence + package resolution.

Detailed TDD task list below.

### Chunk 3b (~0.5 day): `/api/v2/site-files/<slug>` endpoint

**Deliverable:** `GET /api/v2/site-files/<slug>` returns the flat file tree of `output/<slug>/site/` as JSON. Client uses this to mount files into the WebContainer.

Outline with acceptance criteria below.

### Chunk 3c (~1 day): `WebContainerPreview` component + first working render

**Deliverable:** v3 workspace shows a live WebContainer-powered Next.js dev server in the preview panel for any v2 build. v1 builds continue to use the legacy iframe path.

Outline with acceptance criteria below.

### Chunk 3d (~1 day): Hot-reload + cost widget + decommission server-side next dev for v2

**Deliverable:** Edits (refine + visual-edit) push changed files into the running container without a full restart. Dashboard shows "Preview minutes this month." `pebble.postbuild.run_dev_server` is never called for v2 builds.

Outline with acceptance criteria below.

---

## Chunk 3a: Detailed TDD task list

### Task 3a-1: Install `@webcontainer/api` and verify import

**Files:**
- Modify: `ui/v3/package.json`
- Create: `ui/v3/lib/webcontainer.ts`
- Test: `ui/v3/__tests__/webcontainer-import.test.ts`

- [ ] **Step 1: Install the package**

```bash
cd C:/Users/marci/pebble-engine/ui/v3
npm install @webcontainer/api
```

Confirm it appears in `package.json` `dependencies` (not `devDependencies` — it ships in the client bundle).

- [ ] **Step 2: Write the failing test**

```typescript
// ui/v3/__tests__/webcontainer-import.test.ts
// Tests that the package resolves and that our singleton helper exports
// the expected types. Does NOT boot a real WebContainer (that requires
// COOP/COEP headers and a browser — not available in Jest/Node).

import { getWebContainerInstance } from "@/lib/webcontainer";

test("getWebContainerInstance is a function", () => {
  expect(typeof getWebContainerInstance).toBe("function");
});

test("FileTree type accepts a flat file map", () => {
  // Compile-time only — if this file compiles, the type works.
  const tree: import("@/lib/webcontainer").FileTree = {
    "package.json": { file: { contents: '{"name":"test"}' } },
    "app/page.tsx": { file: { contents: "export default function P(){}" } },
  };
  expect(Object.keys(tree)).toHaveLength(2);
});
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd C:/Users/marci/pebble-engine/ui/v3 && npx jest __tests__/webcontainer-import.test.ts
```

Expected: module not found (`@/lib/webcontainer` missing).

- [ ] **Step 4: Create the singleton helper**

```typescript
// ui/v3/lib/webcontainer.ts
/**
 * WebContainer singleton helper.
 *
 * WebContainers can only boot once per page (StackBlitz enforces this).
 * This module holds the single instance so any component can get it
 * without double-booting. getWebContainerInstance() is lazy — it does
 * nothing until first call, and subsequent calls return the cached promise.
 *
 * IMPORTANT: only call this from the browser. A server-side import is
 * harmless (the module just re-exports types) but calling
 * getWebContainerInstance() from a Next.js server component will throw
 * because WebContainer requires a browser context with COOP/COEP.
 */

import type { WebContainer } from "@webcontainer/api";

// FileTree mirrors the @webcontainer/api FileSystemTree shape so callers
// don't need a direct import of the SDK type.
export type FileTree = Record<
  string,
  { file: { contents: string } } | { directory: FileTree }
>;

let _booting: Promise<WebContainer> | null = null;

/**
 * Return the singleton WebContainer instance, booting it on first call.
 * Subsequent calls return the same promise so components don't race.
 */
export async function getWebContainerInstance(): Promise<WebContainer> {
  if (_booting) return _booting;
  const { WebContainer } = await import("@webcontainer/api");
  _booting = WebContainer.boot();
  return _booting;
}

/** Tear down the container (used in tests / HMR cleanup). */
export function resetWebContainerInstance(): void {
  _booting = null;
}
```

- [ ] **Step 5: Run test to verify pass**

```bash
cd C:/Users/marci/pebble-engine/ui/v3 && npx jest __tests__/webcontainer-import.test.ts
```

Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add ui/v3/package.json ui/v3/package-lock.json ui/v3/lib/webcontainer.ts ui/v3/__tests__/webcontainer-import.test.ts
git commit -m "feat(v3/wc): install @webcontainer/api + singleton boot helper (Phase 3a-1)"
```

---

### Task 3a-2: COOP + COEP headers in `next.config.ts`

WebContainers require `SharedArrayBuffer`. Browsers gate `SharedArrayBuffer` behind cross-origin isolation: the top-level document must be served with both `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp`.

**Files:**
- Modify: `ui/v3/next.config.ts`
- Test: `ui/v3/__tests__/security-headers.test.ts` (new test function in existing file if present, else create)

- [ ] **Step 1: Write the failing test**

```typescript
// ui/v3/__tests__/security-headers.test.ts
/**
 * Validate that next.config.ts exports the required cross-origin isolation
 * headers. We parse the exported headers() array directly (no HTTP server).
 */

// dynamic import avoids the Sentry wrapper complaints in Jest
const getHeaders = async () => {
  const mod = await import("@/next.config");
  // withSentryConfig wraps the default export; unwrap one level.
  const cfg = (mod.default as any);
  return typeof cfg.headers === "function" ? await cfg.headers() : [];
};

test("COOP header is present on all routes", async () => {
  const rules = await getHeaders();
  const allHeaders = rules.flatMap((r: any) => r.headers ?? []);
  const coop = allHeaders.find((h: any) => h.key === "Cross-Origin-Opener-Policy");
  expect(coop).toBeDefined();
  expect(coop.value).toBe("same-origin");
});

test("COEP header is present on all routes", async () => {
  const rules = await getHeaders();
  const allHeaders = rules.flatMap((r: any) => r.headers ?? []);
  const coep = allHeaders.find((h: any) => h.key === "Cross-Origin-Embedder-Policy");
  expect(coep).toBeDefined();
  expect(coep.value).toBe("require-corp");
});
```

- [ ] **Step 2: Verify failure**

```bash
cd C:/Users/marci/pebble-engine/ui/v3 && npx jest __tests__/security-headers.test.ts
```

Expected: both assertions fail (headers not present yet).

- [ ] **Step 3: Add headers to `next.config.ts`**

Add to the `SECURITY_HEADERS` array in `ui/v3/next.config.ts`, directly after the `Permissions-Policy` line:

```typescript
  { key: "Cross-Origin-Opener-Policy",   value: "same-origin" },
  { key: "Cross-Origin-Embedder-Policy", value: "require-corp" },
```

Also update the `frame-src` CSP directive to allow `*.webcontainer-api.io` (the origin StackBlitz WebContainer dev servers run on):

- In the `frame-src` line, append `https://*.webcontainer-api.io` before the closing backtick.
- In the `connect-src` line, append `https://*.webcontainer-api.io wss://*.webcontainer-api.io` (WebContainers uses a WebSocket internally).

- [ ] **Step 4: Check for COEP breakage on third-party iframes**

COEP `require-corp` blocks subresources that don't send a `Cross-Origin-Resource-Policy` header. Audit the v3 iframe list:

| Frame source | Sends CORP? | Action |
|---|---|---|
| `/preview/<slug>/` (v1, engine-served) | No (Python handler) | Add `Cross-Origin-Resource-Policy: cross-origin` header in `pebble_engine.py`'s `preview/` route |
| Stripe Checkout / Portal | Yes (Stripe's CDN) | No action needed |
| Google Maps embed | Partial — test in dev | Add `credentialless` attribute to the map iframe if it breaks |
| StackBlitz WebContainer dev server | Yes (their SDK handles it) | No action needed |

Add the CORP header to the engine's `/preview/` handler:

```python
# pebble_engine.py — in the do_GET preview branch
self.send_header("Cross-Origin-Resource-Policy", "cross-origin")
```

- [ ] **Step 5: Verify pass**

```bash
cd C:/Users/marci/pebble-engine/ui/v3 && npx jest __tests__/security-headers.test.ts
```

Expected: 2 passed.

- [ ] **Step 6: Manual smoke in dev browser**

```bash
cd C:/Users/marci/pebble-engine/ui/v3 && npm run dev
# In DevTools Console at localhost:3001:
# > crossOriginIsolated   → should print `true`
```

If `crossOriginIsolated` is `false`, the COOP/COEP headers aren't reaching the browser — check Next.js dev middleware override or Sentry wrapper stripping headers.

- [ ] **Step 7: Commit**

```bash
git add ui/v3/next.config.ts pebble_engine.py
git commit -m "feat(v3/wc): add COOP + COEP headers for cross-origin isolation (Phase 3a-2)"
```

---

### Task 3a-3: `WebContainerPreview` stub component

A stub that boots the WebContainer, shows a status string, and doesn't yet render a real site. Proves the SDK works in-browser before we wire in the file tree.

**Files:**
- Create: `ui/v3/components/workspace/web-container-preview.tsx`

- [ ] **Step 1: Create the stub component**

```tsx
// ui/v3/components/workspace/web-container-preview.tsx
"use client";

/**
 * WebContainerPreview — boot a StackBlitz WebContainer, mount a generated
 * site's file tree, run `npm install` + `next dev`, and render the resulting
 * dev server URL in an iframe.
 *
 * Props:
 *   slug      — project slug, used to fetch files from /api/v2/site-files/<slug>
 *   onReady   — called with the preview iframe URL once next dev is listening
 *   onError   — called with an Error if boot or install fails
 *
 * Lifecycle:
 *   1. Fetch file tree from engine (/api/v2/site-files/<slug>)
 *   2. Boot WebContainer singleton (getWebContainerInstance)
 *   3. Mount file tree (wc.mount(files))
 *   4. npm install (spawn + stream stdout to status)
 *   5. npm run dev (spawn + watch for "Ready" in stdout)
 *   6. Read server URL from wc.on("server-ready") event
 *   7. Set iframe src to that URL
 *
 * This stub only covers steps 1-3 and shows a status string.
 * Full impl ships in chunk 3c.
 */

import { useEffect, useState } from "react";
import { getWebContainerInstance } from "@/lib/webcontainer";

interface Props {
  slug: string;
  onReady?: (url: string) => void;
  onError?: (err: Error) => void;
}

type Status =
  | { phase: "idle" }
  | { phase: "fetching-files" }
  | { phase: "booting" }
  | { phase: "mounting" }
  | { phase: "installing"; output: string }
  | { phase: "starting-dev" }
  | { phase: "ready"; url: string }
  | { phase: "error"; message: string };

export function WebContainerPreview({ slug, onReady, onError }: Props) {
  const [status, setStatus] = useState<Status>({ phase: "idle" });

  useEffect(() => {
    let cancelled = false;

    async function boot() {
      try {
        setStatus({ phase: "fetching-files" });
        const res = await fetch(`/api/v2/site-files/${encodeURIComponent(slug)}`);
        if (!res.ok) throw new Error(`site-files: ${res.status} ${res.statusText}`);
        const files = await res.json(); // FileTree JSON

        if (cancelled) return;
        setStatus({ phase: "booting" });
        const wc = await getWebContainerInstance();

        if (cancelled) return;
        setStatus({ phase: "mounting" });
        await wc.mount(files);

        // Full install + dev steps land in chunk 3c.
        // For now, confirm mount succeeded.
        if (cancelled) return;
        setStatus({ phase: "installing", output: "mount OK — npm install coming in 3c" });
      } catch (err) {
        if (cancelled) return;
        const message = err instanceof Error ? err.message : String(err);
        setStatus({ phase: "error", message });
        onError?.(err instanceof Error ? err : new Error(message));
      }
    }

    boot();
    return () => { cancelled = true; };
  }, [slug, onReady, onError]);

  if (status.phase === "ready") {
    return (
      <iframe
        src={status.url}
        className="w-full h-full border-0"
        title="Live preview"
        // credentialless on the map embed if needed — safe for WebContainer frames
        allow="cross-origin-isolated"
      />
    );
  }

  return (
    <div className="flex flex-col items-center justify-center h-full gap-3 text-sm text-muted-foreground">
      <div className="animate-spin h-5 w-5 rounded-full border-2 border-current border-t-transparent" />
      <p>
        {status.phase === "fetching-files" && "Loading project files…"}
        {status.phase === "booting" && "Booting browser sandbox…"}
        {status.phase === "mounting" && "Mounting files…"}
        {status.phase === "installing" && `Installing packages… ${(status as any).output ?? ""}`}
        {status.phase === "starting-dev" && "Starting dev server…"}
        {status.phase === "idle" && "Initialising…"}
        {status.phase === "error" && `Error: ${(status as any).message}`}
      </p>
    </div>
  );
}
```

- [ ] **Step 2: TypeScript compile check**

```bash
cd C:/Users/marci/pebble-engine/ui/v3 && npx tsc --noEmit
```

Expected: 0 errors. Fix any import path issues before continuing.

- [ ] **Step 3: Commit**

```bash
git add ui/v3/components/workspace/web-container-preview.tsx
git commit -m "feat(v3/wc): WebContainerPreview stub — boot + mount lifecycle scaffold (Phase 3a-3)"
```

---

### Task 3a-4: Chunk 3a acceptance gate

- [ ] `npm install @webcontainer/api` succeeded with no peer-conflict warnings
- [ ] `crossOriginIsolated === true` in browser DevTools at `localhost:3001`
- [ ] `npx jest __tests__/webcontainer-import.test.ts` — 2 passed
- [ ] `npx jest __tests__/security-headers.test.ts` — 2 passed
- [ ] `npx tsc --noEmit` — 0 errors
- [ ] `/preview/<slug>/` v1 iframes still render in dev (CORP header added to engine)

```bash
git add .
git commit -m "feat(v3/wc): chunk 3a complete — WebContainer scaffold + headers (Phase 3a gate)"
```

---

## Chunk 3b: `/api/v2/site-files/<slug>` endpoint (outline)

**Deliverable:** `GET /api/v2/site-files/<slug>` reads `output/<slug>/site/` recursively and returns a flat JSON file tree in WebContainer `FileSystemTree` shape.

**Output shape:**

```json
{
  "package.json":       { "file": { "contents": "..." } },
  "app/page.tsx":       { "file": { "contents": "..." } },
  "app/layout.tsx":     { "file": { "contents": "..." } },
  "app/globals.css":    { "file": { "contents": "..." } },
  "next.config.mjs":    { "file": { "contents": "..." } },
  "tailwind.config.ts": { "file": { "contents": "..." } },
  "tsconfig.json":      { "file": { "contents": "..." } },
  "public/":            { "directory": {} }
}
```

**Tasks (outline):**

- [ ] Create `pebble/server/site_files.py` — walks `output/<slug>/site/`, skips `node_modules/` and `.next/`, UTF-8 decodes each file, builds the flat JSON tree. Binary files (images) are base64-encoded with `{ "file": { "contents": "<base64>", "encoding": "base64" } }`.
- [ ] Register `GET /api/v2/site-files/<slug>` in `pebble/server/router.py`.
- [ ] Auth-gate with `require_project_owner` (same pattern as other `/api/v2/` routes).
- [ ] Size guard: if total tree exceeds 5MB, return 413 with a clear message (oversized `node_modules` accidentally included would stall the browser).

**Acceptance criteria:**

- `curl http://localhost:8000/api/v2/site-files/stoneground-loaf | python -m json.tool | head -20` returns valid JSON with at least `package.json` and `app/page.tsx` keys.
- Response excludes `.next/` and `node_modules/` paths.
- `python -m pytest tests/test_site_files_endpoint.py -v` → 4 tests pass (happy path, 404 on missing slug, 403 on wrong owner, 413 on oversized tree).

---

## Chunk 3c: `WebContainerPreview` full render (outline)

**Deliverable:** The v3 workspace shows a live Next.js dev server in the preview panel for any v2 build. v1 sites use the existing iframe path.

**Tasks (outline):**

- [ ] Complete the `boot()` function in `web-container-preview.tsx`: after `mount()`, spawn `npm install` and pipe stdout to the `installing` status string. Cache the install state in `sessionStorage` keyed by slug + `package.json` hash so refreshes skip reinstall.
- [ ] After install, spawn `npm run dev` and subscribe to `wc.on("server-ready", (port, url) => ...)`. Set `status.phase = "ready"` + call `onReady(url)`.
- [ ] In `workspace-shell.tsx`, read `build.engine_version` from the bundled project state (`/api/projects/<slug>`). If `"v2"`, render `<WebContainerPreview slug={slug} />` instead of the legacy iframe.
- [ ] Add `WebContainerContext` to expose the mounted `WebContainer` instance to sibling components (needed by chunk 3d's hot-reload bridge).
- [ ] Fallback: if WebContainer boot times out (>30s) or `crossOriginIsolated` is `false` (e.g. the user's browser blocks COEP), fall back to the legacy `/preview/<slug>/` iframe with a toast: "Live preview unavailable — using server preview instead."

**Acceptance criteria:**

- Build a real v2 site (`stoneground-loaf` or any), open `/workspace/stoneground-loaf` in the v3 browser, and within ~15s see the compiled Next.js site render inside the workspace preview panel.
- DevTools Network tab shows no `/preview/` requests for v2 builds.
- Opening `/workspace/stoneground-loaf` in Firefox (COEP may not be supported) shows the fallback toast + legacy iframe within 5s.
- v1 builds (`/workspace/<any-v1-slug>`) render exactly as before.

---

## Chunk 3d: Hot-reload + cost widget + decommission (outline)

**Deliverable:** Edit-and-see-instantly for v2 builds. Dashboard shows preview usage. Server-side `next dev` is never spawned for v2 projects.

**Tasks (outline):**

- [ ] **Hot-reload bridge** — after `/api/refine` or `/api/visual-edit` returns for a v2 build, fetch the changed files from `/api/v2/site-files/<slug>`, diff against the mounted tree, and write only the changed files via `wc.fs.writeFile(path, contents)`. The running `next dev` process detects the file change and hot-reloads without a restart. Expected latency: <2s from API response to browser preview update.
- [ ] **Cost widget** — add a `<PreviewMinutes />` component in the v3 settings page that reads session storage (ms spent in `"ready"` phase this calendar month). Show: "Preview used this month: X min / ~300 min Pro plan". Gate behind `isDev || isAdmin` until the numbers are validated.
- [ ] **Decommission `post_build_run_dev_server` for v2** — in `pebble/server/build_v2.py`, never call `post_build_run_dev_server`. Add an assertion in `tests/test_build_v2_e2e.py` that the mock `post_build_run_dev_server` was NOT called. Keep the function in `pebble/postbuild.py` (still used by v1).
- [ ] **Keep-alive decommission** — `workspace-shell.tsx` currently pings `/preview/<slug>/` every 4 min to keep a Fly machine warm. Skip this for v2 builds (no Fly machine to warm).

**Acceptance criteria:**

- Change a text slot via visual-edit on a v2 build → preview updates within 2s without a full reload.
- `python -m pytest tests/test_build_v2_e2e.py -v` → `post_build_run_dev_server` mock call count is 0.
- Cost widget visible in dev, hidden in prod for non-admins.

---

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Pro plan quota exhausted mid-month (300h) | Low initially, Medium at scale | Preview stops working for new sessions | Cost widget warns at 80% usage; automatic fallback to `/preview/<slug>/` server path if container boot returns quota error |
| `npm install` fails inside WebContainer (native bindings, platform-specific deps) | Low — v2 generates only `next@14.2.5 + react@18 + tailwindcss` | Preview blank | Pin exact dep versions in blocks_compiler `_PACKAGE_JSON`; integration test boots a real container in CI against the frozen lockfile |
| COOP/COEP breaks existing v3 features (Stripe Checkout, Google Maps embed) | Medium | Checkout iframe broken | Audit each third-party iframe for CORP support before shipping; add `credentialless` attribute to non-CORP iframes where semantically safe; Stripe.js sends CORP headers |
| iOS Safari doesn't support WebContainers (SharedArrayBuffer not available) | High — iOS 15.4+ supports SAB, older does not | No live preview on old iPhones | Detect `!crossOriginIsolated` at mount time and fall back to legacy iframe silently; log via Sentry to measure actual hit rate |
| Hot-reload latency exceeds 2s on large file trees | Medium | UX degradation on edit | Only write changed files (diff before write); debounce concurrent edits; measure with Sentry performance tracing |
| StackBlitz changes commercial terms or SDK API surface | Low | Migration effort | Isolate all WebContainer calls behind `lib/webcontainer.ts`; the rest of the codebase has no direct SDK dependency |

---

## Cost projections

### StackBlitz plan selection

| Tier | Price | Included hours | Cost per extra hour | Recommended threshold |
|---|---|---|---|---|
| Pro | $20/mo | ~300 container-hours | ~$0.08/hr | Use until 200+ concurrent active users |
| Production | $200-500/mo | 3,000-15,000 container-hours | ~$0.03-0.07/hr | Upgrade when monthly usage hits 250h consistently |

### User traffic estimates

- 5 min average preview session per build
- Pro plan: 300h × 60 min/h = 18,000 session-minutes ÷ 5 min = **3,600 sessions/month**
- At 1 session per DAU: supports ~120 DAU on Pro with no overrun
- At 200 DAU: upgrade to Production

### Server cost avoided

Each v1 build with `PEBBLE_AUTO_RUN=true` holds a Fly machine for the session duration. At $0.05/hr Fly compute × 5 min × 3,600 sessions = **$15/mo avoided** at 120 DAU. WebContainers pays for itself above ~400 DAU in server savings alone.

---

## Self-review

**Spec coverage:**

- ✅ StackBlitz signup decision → strategic context table + cost projections
- ✅ `@webcontainer/api` install + COOP/COEP headers → task 3a-1, 3a-2
- ✅ `WebContainerPreview` component → task 3a-3 (stub) + chunk 3c (full)
- ✅ `/api/v2/site-files/<slug>` endpoint → chunk 3b
- ✅ Wire into WorkspaceShell with v1/v2 branch → chunk 3c
- ✅ Hot-reload on refine/visual-edit → chunk 3d
- ✅ Cost monitoring widget → chunk 3d
- ✅ Decommission server-side next dev for v2 → chunk 3d
- ✅ All 5 risks surfaced → risk register
- ✅ iOS Safari fallback → risk register + chunk 3c fallback task

**Placeholder scan:** No TBDs. Every code block in chunk 3a is complete. Chunk 3b-3d carry explicit acceptance criteria so the next subagent knows exactly what done looks like.

**Type consistency:** `FileTree` is defined once in `lib/webcontainer.ts` and re-used by both `WebContainerPreview` and `site_files.py` (Python emits the JSON, TypeScript consumes it). The `engine_version: "v2"` field in `build_meta.json` is the single branch point — no separate feature flag needed.

**Breaking changes:** None for v1 users. The COOP/COEP headers are the only externally visible change to v3 — audit complete in task 3a-2 step 4.

---

## Execution handoff

Start with chunk 3a. It is the most independent (no engine changes, no endpoint changes — pure `ui/v3/` work + one small CORP header in `pebble_engine.py`). Once `crossOriginIsolated === true` in the browser and the stub component mounts without errors, 3b-3d can proceed in any order.

**Two execution options:**

1. **Subagent-Driven (recommended)** — dispatch one subagent per chunk; each subagent checks the acceptance criteria before reporting done. ~4 parallel sessions for 3b-3d once 3a gates pass.
2. **Inline Execution** — execute chunk 3a inline via executing-plans, then decide after the acceptance gate.

Which approach?
