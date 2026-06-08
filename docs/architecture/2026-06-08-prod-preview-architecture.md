# Prod preview architecture — the proper fix

**Date:** 2026-06-08
**Author:** Claude (autonomous session, for Marc's review)
**Status:** Design + recommendation. Prototype on branch; NOT deployed.

## The problem (found while dogfooding prod)

Opening a generated project's workspace on prod shows **"Preview failed to start — `npm not found in PATH; install Node.js`."** The live preview works by running `npm install` + `next dev` to serve the generated Next.js app. The Railway engine container is **Python-only** — no Node/npm — so it physically cannot start the preview. (It worked on localhost because Marc's machine has Node.)

## Root-cause map (verified in code)

| Path | Needs Node? | Where | Status on Railway |
|---|---|---|---|
| Generated-site preview | **Yes** — `npm install` + `next dev` per project (`preview_warmup.py`, `postbuild.py`) | preview time | ❌ fails (no npm) |
| Template preview | No — serves a **pre-built static export** from `out/` (`_handle_preview_template`) | serve time | ✅ works |
| Publish → Cloudflare | No — **Direct Upload** of files; *prefers `site/out/`* (`publish.py:330-334`) | publish time | ✅ works *if `out/` exists* |
| Static export build (`templates/export.py`) | **Yes** — `npx next build` w/ `output:"export"` + contact-stub | build time, offline | n/a (offline, one-time) |

### The key insight

**Both preview and publish already want the same artifact: a static export `out/`.**
- Template previews serve `out/` statically — no Node at serve time.
- `publish_to_cloudflare` prefers `site/out/` and Direct-Uploads it — no Node at publish time.
- The static export is produced by `templates/export.py` via a transient swap: `next.config.mjs → output:"export" + basePath`, `app/actions/contact.ts → client stub` (Next forbids `"use server"` under `output:"export"`), `next build`, then restore source byte-identically.

So the engine **serves and publishes Node-lessly today** — the *only* Node dependency that matters is **building the `out/` static export**, and we already have battle-tested code that does exactly that (just scoped to templates, not generated sites).

### The hard constraint

Generated sites use a **Server Action** contact form (`app/actions/contact.ts`, `"use server"` + `useActionState` → Resend). Server Actions **cannot** exist under `output:"export"`. So a static-export preview/publish has a **stubbed (client-only) contact form** — it validates but doesn't send. The real form only works under SSR (`@cloudflare/next-on-pages`), which is a separate, larger effort. For **preview** this is fine (you're previewing the design). For **published** sites it's a real limitation to flag.

## The proper fix

**Make the static export `out/` the canonical artifact for generated sites, exactly like templates.** Then preview-serving and publish are both Node-less. Concretely:

1. **`pebble/preview_export.py`** — generalize `templates/export.py` to a generated project: transient-swap `next.config.mjs` (`output:"export"`, `basePath:"/preview/<slug>"`, `images.unoptimized`, ignore TS/eslint) + `app/actions/contact.ts` (the existing universal client stub), `next build`, produce `out/`, restore source byte-identically via try/finally.
2. **Serve `/preview/<slug>/` from `out/`** when present (the engine already has a static fallback + the template-preview URL-rewrite + visual-edit bridge injection to mirror). No `next dev`, no Node at serve time.
3. **Publish** already prefers `site/out/` — same artifact, zero change needed.

This is **infra-agnostic** at the serve/publish layer. The remaining decision is **where the `next build` runs**, since it needs Node.

## Where does the build run? (the real decision — needs Marc)

| Option | How | Pros | Cons |
|---|---|---|---|
| **A. Node on Railway (combined image)** | `nixpacks.toml` adds Node alongside Python; engine runs the export build during the build pipeline (once per generation), then serves `out/` static | One box; no new infra; build is one-time then cheap static serve (avoids the per-preview `next dev` OOM risk) | `next build` is memory-heavy (~1–2 GB); the **trial Railway** box may OOM; build adds ~30–90s to generation |
| **B. Dedicated Node build worker** | Separate Railway/Fly service with Node builds the export, hands `out/` back (shared volume or upload) | Isolates the heavy build; engine stays Python-only; scales | New service to run + pay for + orchestrate |
| **C. Cloudflare builds it (Pages Git/CI)** | Switch publish from Direct-Upload to Pages **Git integration**; Cloudflare CI runs `next build`; preview = the Pages preview deployment, proxied through the engine for the visual-edit bridge | Zero Node in our backend; offloads all build cost/memory to Cloudflare; could even unlock SSR (`next-on-pages`) → **working** contact form | Per-preview CI build latency (~1–2 min); larger rework of the publish path; preview becomes a Cloudflare deploy |
| **D. Fly preview backend (scaffold exists)** | `PEBBLE_PREVIEW_BACKEND=fly` already proxies `/preview` to `pebble-preview-<slug>.fly.dev` (Node container runs `next dev`) | Full live-dev fidelity; the proxy scaffold is already in `_handle_preview` | Per-slug Fly apps = real orchestration + cost; heaviest option |

### Recommendation

**Short term (unblock dogfooding):** Option **A** — add Node to Railway and switch preview from per-request `next dev` to a **one-time static export served statically**. It reuses the proven export code, removes the persistent-dev-server OOM risk, and fixes publish (`out/`) for free. Guard the build with a memory ceiling and fall back to the "still warming up" splash if the box can't build.

**Medium term (the durable answer):** Option **C** — let Cloudflare own the Next build. It takes all build memory/cost off our backend, and is the only path to a **working** (SSR) contact form on published *and* previewed sites. This pairs naturally with the Railway trial expiring — if the engine moves or slims down, C means it never needs Node at all.

**Avoid** D unless live-HMR preview becomes a hard product requirement — it's the most infra to operate.

## What I prototyped this session (branch only, not deployed)

- `pebble/preview_export.py` — static export for a *generated* project (generalized from `templates/export.py`), with byte-identical source restore + tests.
- Wiring so `/preview/<slug>/` serves `out/` when present, with the visual-edit bridge.
- Verified locally (this machine has Node) by building + serving a real generated site.

See the session report for prototype results + the prod bug list.

## ⚠️ NLM adversarial review changed the recommendation (2026-06-08)

I ran this design past the project NotebookLM. It **rejected the static-export-everywhere approach** and it's right:

- **Static export silently kills the Server-Action contact form.** That form (Resend) was Pebble's single most-cited competitive gap vs. Base44/Lovable — and we just closed it. A plumber whose published site silently swallows emergency-call form submissions churns *and* charges back. Static export also forces `images.unoptimized` (4 MB JPGs to mobile) and breaks any non-`generateStaticParams` dynamic route. **So static export is wrong for publish, and lossy for preview.**
- **On the build-location options:** A → `next build` (CPU/RAM-heavy, 3–6 min) on the single-process `ThreadingHTTPServer` box = OOM that takes down the whole SaaS. C (Cloudflare CI) → 2–4 min per build = "UX black hole" vs. the millisecond visual-edit loop. D (Fly) → cross-provider file-sync hell.

**Revised recommendation:**

1. **Quick unblock (do now):** stop using a Python-only image. Switch the Railway build to a **combined Python+Node image** (e.g. base `nikolaik/python-nodejs`, or a `nixpacks.toml` adding Node). Previews then run exactly as they do locally — **SSR + Server Actions + image optimization all intact.** The "npm not found in PATH" error is *literally* a missing runtime, not an architecture flaw. (Caveat: still per-preview `next dev` on one box — fine for beta traffic; revisit if concurrency grows.)
2. **Proper fix (the real answer — Option E): Vercel Deployments REST API.** From the Python engine: zip `output/<slug>/site/`, POST to Vercel's Deployments API, Vercel runs `npm install` + `next build` **on their infra with full SSR**, returns a live preview/prod URL we embed in the iframe. Zero Node on Railway, build cost offloaded, Server Actions + `next/image` preserved, and it doubles as the publish path (we already ship a `vercel.json` scaffold). This supersedes the Cloudflare-static publish for SSR sites.

**The static-export prototype below is retained as a negative result** — it proved the mechanism runs, but NLM is right that it's the wrong direction for a product whose value includes a *working* backend form. Its real payoff was surfacing the truncation bug (next section).

## 🔴 Critical finding surfaced while prototyping: generated sites can ship broken

Running `next build` on two real generated sites (the only way to validate them — `next dev` is lazy/lenient and never compiles unvisited routes) **both failed on real defects the engine reported as successful builds**:

- **`aa-craft-bakery` (fresh Sonnet build, `build_meta` says 38 files, success):** `components/sections/CtaMinimal.tsx` is **truncated mid-string** — ends at `href="tel:[BUSINESS` with no closing tag/brace/export. The LLM stream was cut (max_tokens / stream boundary) and the engine wrote the partial file and declared success.
- **`maple-page-books`:** `privacy/page.tsx` + `faq/page.tsx` fail to parse under `next build`.

**Impact:** these sites **cannot be published** (the Cloudflare path needs a real build; the Vercel path will fail the same way) and the user has no idea — they saw a lenient `next dev` preview. This is a silent, ship-blocking quality hole independent of the preview-infra choice.

**Recommended guard (Node-less, shippable now):** validate every generated `.ts/.tsx` for gross truncation (delimiter balance + unterminated trailing string) right after generation; flag/repair before reporting success. Prototyped this session as `pebble/codegen_validate.py` (+ tests). The durable version is to actually run a build (via the Vercel API in Option E, which fails loudly on broken code).

## Open decisions for Marc

1. **Build location: A, B, or C?** (My lean: A now, C as the real fix.)
2. **Railway trial** expires ~10 days — does prod infra change anyway? (Affects whether A is worth wiring.)
3. **Static-publish contact form** is stubbed (no email) until SSR — acceptable for now, or prioritize `next-on-pages`?
