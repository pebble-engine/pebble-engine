# WebContainers Feasibility for Pebble — 2026-05-23

## Executive Summary

**Verdict: Do not migrate now. Consider a hybrid approach at 500+ concurrent users.**

WebContainers (StackBlitz) eliminate the 60-120s cold-start problem by running Node.js inside the user's browser via WebAssembly. Bolt.new uses this and gets sub-5s preview boot times. But the technology carries three blockers for Pebble's current stage: (1) it requires COOP/COEP security headers that break every third-party embed your generated sites contain (Google Maps, Stripe, WhatsApp, booking widgets — all of which Pebble's integration layer injects); (2) commercial pricing is opaque and quote-only, almost certainly in the $2,000-10,000+/month range for commercial production use; (3) it is Chromium-first — Safari is beta, Firefox is alpha — which is a real market coverage issue for small-business owners. Pebble's current `next dev` pipeline with the on-demand warmup (just shipped) is the right answer for launch. The honest 6-month trigger to revisit is hitting concurrent-user scale that overloads the single Python process, not preview latency.

---

## Current Architecture

Pebble's preview pipeline today:

1. LLM generates site files into `output/<slug>/site/` (Next.js 14/15 project)
2. `pebble.postbuild` runs `npm install` (60-120s cold, ~5s warm) then `next dev` on a randomly-assigned localhost port
3. `pebble.server.dev_registry` tracks `slug -> http://127.0.0.1:<port>` in memory
4. `pebble_engine._handle_preview` proxies `/preview/<slug>/` requests to the live dev server, injecting the visual-edit bridge into HTML responses
5. `pebble.server.preview_ondemand` (just shipped 2026-05-23) handles the post-restart case: first `/preview/<slug>/` hit with no dev URL registered spawns `next dev` in a background thread and returns a self-refreshing splash

**Cold-start reality:** npm install = 60-120s first run, ~5s with cached node_modules. Next.js Turbopack first compile = 10-30s. Total user wait: 30-90s warm, 90-240s cold.

**Cost:** $0/build. All compute is local (Windows machine + Vercel for published sites).

**Concurrent capacity:** Effectively 1 active build at a time (single-process Python HTTP server). Multiple users would queue or stomp each other.

---

## WebContainers in 60 Seconds

WebContainers is StackBlitz's technology that runs a full Node.js runtime inside the user's browser tab via WebAssembly. npm installs, `next dev`, file watchers — all happen client-side. The browser tab IS the dev server.

**What works:**
- Full Node.js runtime (v18-equivalent) in-browser
- npm install from registry (with StackBlitz CDN caching popular packages — often <500ms)
- `next dev`, React, Express, Vite, and most pure-JS frameworks
- File system API: `readFile`, `writeFile`, `mkdir`, `watch` — full POSIX-style FS in memory
- HMR / hot reload works normally
- Each browser tab is isolated — infinite horizontal scaling (the browser does the work)

**What does not work:**
- **Native modules** — anything with C++ bindings (better-sqlite3, sharp, canvas, bcrypt compiled) will not build. The browser has no C++ compiler. `sqlite3` has experimental WebAssembly polyfill support but `better-sqlite3` is a hard no.
- **Pebble's integration snippets (Google Maps, Stripe.js, WhatsApp)** — WebContainers require COOP/COEP headers (`Cross-Origin-Opener-Policy: same-origin`, `Cross-Origin-Embedder-Policy: require-corp`). These headers block loading cross-origin iframes and scripts that do not set `Cross-Origin-Resource-Policy`. Every third-party embed Pebble injects breaks.
- **Safari (pre-16.4)** — no `Atomics.waitAsync`, no lookbehind regex. Hard requirement. Safari 16.4 is "beta" support; full production-ready is Chromium only.
- **Firefox** — "alpha" support, preview-in-iframe mode does not work correctly due to incomplete credentialless cross-origin isolation

**Browser support reality:**
| Browser | Status |
|---|---|
| Chrome / Edge / Brave | Full support |
| Safari 16.4+ | Beta (issues remain) |
| Safari < 16.4 | Not supported |
| Firefox | Alpha (preview-in-frame broken) |
| iOS Safari | Not supported |

Small-business owners disproportionately use Safari and Firefox. Chromium-only means ~35-40% of your target audience cannot use the workspace.

---

## Cost Analysis

| | Pebble Today | WebContainers | Hybrid (WC for preview only) |
|---|---|---|---|
| **Preview infra cost** | $0 (local compute) | Quote-only (sales contact required). Community reports suggest $2k-10k+/month for commercial production use at any real scale | Quote-only, same dependency |
| **Per-build marginal cost** | $0 | Unknown (no public per-build or per-session rate published) | $0 (LLM + eval loop stay on Python engine) |
| **Concurrent users** | ~1 practical (single Python process) | Unlimited (browser-native) | Unlimited for preview, ~1 for builds |
| **Third-party dependency** | None (runs locally) | StackBlitz as critical infrastructure vendor | StackBlitz for preview layer only |
| **Migration engineering cost** | — | Estimated 3-4 sprint weeks: WC iframe integration, file-sync protocol, COOP/COEP header audit, browser-compat fallback | Estimated 1-2 sprint weeks |

**Key finding on pricing:** StackBlitz does not publish commercial WebContainer API pricing. Their license page says production commercial use requires a license, and all quotes are via sales contact. Multiple community forum posts confirm even sales outreach in early 2025 went unanswered. Assuming Bolt.new pays something in the $5k-15k/month range (consistent with their ARR and headcount) — this cost is not viable for Pebble pre-revenue.

---

## Migration Scope

If a full WebContainers migration were attempted:

**What changes:**
- `pebble.postbuild` — no longer spawns `npm install` or `next dev` locally. Instead, sends the generated file tree to the browser's WebContainer instance via a new JS bridge (POST to a WebSocket or postMessage channel)
- `pebble.server.dev_registry` — entire module deleted (no server-side dev process tracking needed)
- `pebble.server.preview_ondemand` — entire module deleted
- `pebble_engine._handle_preview` — the Python proxy path disappears. The browser tab talks directly to its own WebContainer
- `ui/v3/components/workspace-shell.tsx` — must instantiate and manage a `WebContainer` instance, mount files, run `npm install` + `next dev`, listen for the `server-ready` event, render the preview URL in the iframe
- **COOP/COEP headers** — `next.config.ts` in `ui/v3/` must emit COOP/COEP headers. This breaks all cross-origin resources loaded by the Pebble workspace shell itself (Stripe.js for billing, Supabase auth, Google fonts from CDN unless self-hosted)
- **Integration bridge** — `pebble.server.visual_edit`'s `PEBBLE_VISUAL_EDIT_BRIDGE` JS payload currently injected server-side must be delivered through the WebContainer FS instead

**What stays the same:**
- The entire LLM call, eval suite, auto-repair loop
- `pebble.industry`, `pebble.plan`, `pebble.cost`, `pebble.history`
- All backend API routes (`/api/generate`, `/api/refine`, `/api/blocks`, `/api/forms/*`, etc.)
- The Cloudflare Pages publish flow (generated files still exist on disk for deployment)
- All authentication, billing, Stripe webhook handling

**Bottom line on scope:** About 60% of `pebble_engine.py`'s preview plumbing disappears. The frontend workspace shell gains 200-400 lines of WebContainer lifecycle management. The COOP/COEP header requirement is the hardest part — it requires auditing every cross-origin dependency of both the Pebble workspace app AND the generated site previews.

---

## Performance Comparison

| Metric | Pebble today (warm) | Pebble today (cold restart) | WebContainers |
|---|---|---|---|
| **First preview boot** | 10-30s (node_modules cached) | 60-240s (npm install + compile) | 5-15s typical, 30s+ on slow connections or large projects |
| **Hot reload after edit** | 200-800ms (Turbopack HMR) | Same | 100-500ms (similar HMR, browser-native) |
| **Concurrent user capacity** | 1-3 practical (single process, per-port dev servers) | Same | Unlimited (each browser tab independent) |
| **Engine restart impact** | Preview goes dark until on-demand warmup fires (30-90s) | Same | Zero impact (no server-side state) |
| **Mobile / Safari support** | Full (static proxy, no browser requirements) | Same | Chromium only in practice |

WebContainers win on cold-start latency and infinite horizontal scaling. Pebble wins on browser compatibility and the ability to serve previews to any device.

One important nuance: Pebble's "cold" case (post-engine-restart) just got meaningfully better with the on-demand warmup that shipped today. The UX gap between Pebble and WebContainers for the primary use case (Marc is the only user, building one at a time) has narrowed substantially.

---

## Alternatives Table

| Option | Cold Start | Cost | Browser Coverage | Concurrent Users | Engineering Effort |
|---|---|---|---|---|---|
| **Current + on-demand warmup** (shipped) | 30-90s | $0 | 100% | 1-3 | 0 (done) |
| **WebContainers (full migration)** | 5-15s | Unknown/high (vendor quote, likely $2k-10k+/mo) | ~65% (Chromium + maybe Safari) | Unlimited | 3-4 sprints + COOP/COEP audit |
| **Hybrid: Python engine + WC for preview only** | 5-15s preview | Same unknown cost | ~65% | Unlimited preview, 1-3 builds | 1-2 sprints |
| **Fly.io Machines per-user** | 2-10s (pre-warmed), sub-1s (pre-created) | ~$0.003/hr per machine + egress | 100% | One machine/user, scales horizontally | 2-3 sprints |
| **Vercel Preview Deployments per-build** | 30-90s (full Next.js deploy) | $20/month Vercel Pro (included), +$0.40/GB bandwidth | 100% | Unlimited (CDN) | 1 sprint |
| **Static export + service worker** | 0ms (cached) | $0 | 100% | Unlimited | 2 sprints; loses SSR routes |

**Fly.io Machines** deserves a call-out as the most credible future path: spin up a containerized `next dev` process per user session on Fly, pre-pull the node_modules image layer. 2-10s cold start, full browser support, costs less than $0.01/session, and does not require COOP/COEP headers. This is what a future "move off local" migration should target, not WebContainers.

**Vercel Preview Deployments** are the simplest answer once Pebble is generating static-exportable sites — every build triggers a Vercel deploy via API, the preview URL is ready in 30-90s with no local machinery at all. This is already how the final publish flow works.

---

## Recommendation

**For launch (now, <100 users): stay the course.** The on-demand warmup shipped today is the right fix. The preview cold-start from restart is now 30-90s with a tasteful splash instead of a broken 404. Users who expect instant preview have been trained by Bolt.new and Lovable, which have invested heavily in WebContainers (Bolt) or separate cloud preview infra (Lovable). Pebble is not yet in that competitive position — charging for generation quality first, then premium preview UX second.

**At 500+ concurrent builders (roughly $15k-30k MRR):** revisit Fly.io Machines, not WebContainers. Fly gives you full browser support, no COOP/COEP header hell, and predictable per-session compute costs. The engineering investment is comparable (2-3 sprints) but the result is a universally-accessible preview with no Safari caveats.

**WebContainers is the right answer if and only if:** Pebble pivots to a fully browser-native development environment (like Bolt.new) where the Python engine is eliminated entirely and all editing happens in the browser. That is a 6+ month platform rewrite, not a sprint.

---

## Open Questions for Marc

1. **What is the actual Safari/Firefox split of your target users?** Small-business owners over 40 use Safari disproportionately. If that's 40%+ of your audience, WebContainers is a non-starter on browser support alone — not a performance decision.

2. **Are your integration widgets (Google Maps, WhatsApp, booking tools) negotiable in the workspace preview?** COOP/COEP headers break them. WebContainers would require showing a "preview integrations are disabled" state in the workspace, or proxying every third-party script through Pebble's server. That's a significant product regression.

3. **What's your preview SLA target?** <10s would require WebContainers or Fly Machines. <30s is achievable today with the on-demand warmup. If 30s is acceptable for launch, no migration is needed.

4. **Is local (Windows machine) the permanent engine home?** If you're moving the engine to Railway or Fly.io anyway (which the production deployment notes suggest), the concurrent-user problem and the cold-start problem both become cloud-infrastructure problems, not WebContainers problems. Solve the hosting first.

5. **Do you want the preview to be publicly shareable at a stable URL before publishing?** If yes, the answer is Vercel Preview Deployments (which Pebble already knows how to use), not WebContainers. WebContainer previews live only in the browser tab that opened them — no shareable URL.
