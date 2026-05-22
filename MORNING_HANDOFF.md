# Morning handoff — 2026-05-22 overnight session

> Marc — here's what shipped while you slept. Read this first, then
> click through localhost. Everything pushed to `pebblewebsite/main`
> so Vercel is already up to date.

## TL;DR — seven phases, all live

| # | Phase | Commit | What |
|---|---|---|---|
| 44 | Instant subdomain publish | `7055e26` | `<slug>.pebbleapp.ai` live in <1s, no Cloudflare wait |
| 45 | Workspace shell | `681c03d` | Base44-style left nav across dashboard/integrations/community |
| 46a | Kill "Your Build Plan" rail | `0eb2e08` | Shared sidebar in /workspace too + B&W mono theme |
| 46b | Plan card restructure | `e11f4be` | Single elegant card with 5 labelled sections + Show less |
| 47 | GDPR + DPA + trust row | `633f03e` | `/dpa` page + honest trust badges on landing |
| 48 | Marketplace pivot critique | `9f0d2b2` | `MARKETPLACE_PIVOT_CRITIQUE.md` at repo root |
| 49 | "Site is live" Ready phase | `eb0da2b` | Draft → Ready → (your click) → Design |
| 50 | Block suggestion chips | `f512f5d` | "Add testimonials/pricing/FAQ" above the refine bar |

**2003 Python tests passing, TypeScript clean, no secrets touched, no
prompts/DNA touched, all changes pushed to pebblewebsite/main.**

## What to click on localhost (60-second tour)

Restart your Next dev server first if it's been running a while:
`cd ui/v3 && npm run dev`. Then in order:

1. **`/dashboard`** — Base44-style left nav. Click around Home /
   All Designs / Templates / Integrations / Community / Favorites /
   Recents. Click Community to expand the sub-nav (Launchpad / Hire a
   Partner / Affiliate Program). The whole surface is mono-themed —
   no blue.

2. **`/integrations`** — Categorized integration cards. Stripe / Resend /
   Plausible / Supabase / Custom webhook show as "Live." Mailchimp /
   Calendly / Slack / Zapier / Stripe Payments show as "Builder plan"
   (gated). Google Analytics shows as "Soon."

3. **`/community/launchpad`**, **`/community/hire-a-partner`**,
   **`/community/affiliate`** — stub pages with mailto CTAs while the
   real plumbing catches up.

4. **`/dpa`** — full DPA-summary page with sub-processor table,
   "request signed copy" mailto, honest "Pebble itself isn't yet
   certified" line on certifications.

5. **`/#pricing`** — scroll past the tier cards to see the new trust
   row (GDPR / Your Data Your Rights / Built on SOC 2 Infrastructure).

6. **Start a new project** from the landing page hero — click through
   to Plan. You should see:
   - No "Your Build Plan" rail anymore — replaced with the shared
     dashboard sidebar
   - Horizontal phase breadcrumb pills at top (Idea > Plan > Draft >
     Design > Publish)
   - The Plan card is now ONE container with 5 labelled sections
     (Intent & Goal / Audience & Roles / Core Flows / Technical
     Requirements / Design Preferences) and a Show less toggle
   - "Start Building" button (renamed from "Generate my draft")
   - Black-and-white throughout, no blue

7. **Let the build complete.** Instead of snapping silently into the
   editor, you should see the new Ready phase: "[Project] is live"
   headline + pages-shipped card + three CTAs (Open editor / Preview
   as visitor / Publish now). Auto-advances in 12s if you don't
   interact — move your mouse to stay.

8. **In the editor**, look at the bottom chip bar — there's a new row
   above the refinement chips: "Add: Testimonials | Pricing | FAQ |
   Stats | Newsletter | Browse all sections →". Click any to insert
   that block.

9. **Click Publish.** The Publish phase still defaults to instant
   subdomain (Phase 44) with confetti + X / LinkedIn / Facebook share
   chips.

## What's deferred to next session

- **Phase 23b** — restore cinematic Code Patterns conditional on Layout DNA
- **Phase 28** — hybrid model routing (cheap chat + smart builder)
- **Phase 30** — cinematic-first DNA rebrand
- **Plan-mode conversational chat entry** — your screenshot showed
  idea-phase chips already serve this role (audience/visitors/tone).
  Could revisit as a free-text alternative if conversion data ever
  suggests chip-friction is the bottleneck. Not blocking.
- **Phase 51 smoke tests** — the new frontend routes don't have
  backend endpoints to e2e-test (they're static client pages, all
  imports verified by `tsc --noEmit`). The existing Python suite of
  2003 tests still passes. Skipped this in favor of shipping more
  visible UX work; can add Playwright route-loads tests later if
  you want belt-and-suspenders.

## What needs your attention

### 1. NotebookLM auth — please run `nlm login` in your terminal

When I tried to fire the Phase 48 critique through NLM, the auth was
expired. `refresh_auth` MCP tool reported success but the next call
still 401'd, which means your token cache on disk is stale. The
critique you'll find in `MARKETPLACE_PIVOT_CRITIQUE.md` is the
written substitute — covers the same ground, but the Windows
scheduled task that's supposed to refresh nlm tokens isn't keeping
up. Worth a quick check of the task scheduler when you wake up.

### 2. Read MARKETPLACE_PIVOT_CRITIQUE.md before committing engineering time to Community

271 lines, ~10-minute read. The headline: marketplace is a **pivot,
not an extension** — year-1 cost is 3-5× what it looks like. Ship
Launchpad as free-supply showcase first (already done in Phase 45).
Don't build Stripe Connect / KYC / payouts / dispute desk until you
observe:

- ≥20 designer submissions in 90 days
- ≥5 "I'd pay for this" customer emails
- Pebble core SaaS at ≥$5K MRR

There's a 90-day decision frame at the bottom and 10 failure modes
with specific mitigations for each.

### 3. Instant publish needs DNS + env to light up in prod

If you're ready for `<slug>.pebbleapp.ai`:

- **Cloudflare DNS**: add wildcard CNAME `*` → your Railway host,
  proxy status **DNS only** (grey cloud, not orange)
- **Railway env**: `PEBBLE_PUBLIC_DOMAIN=pebbleapp.ai` and
  `PEBBLE_PUBLIC_SCHEME=https`
- Without these, `/api/publish/instant` cleanly returns 500 with a
  setup checklist — no silent failures.

## Session metrics

- **Commits**: 8 (across 7 phases)
- **Lines net new**: ~3,200
- **Tests**: 1981 → 2003 (+22 for instant publish)
- **TypeScript errors**: 0 throughout
- **Subagent mistakes caught**: 1 (Phase 47 first attempt — verified before claiming complete)
- **Sleep lost**: arguably some (yours, not mine)

## Order of consequence if you want to react

1. **First** — refresh `/dashboard` and `/workspace` and react to the
   sidebar + mono theme + horizontal phase tracker. This is the
   biggest visual change.
2. **Second** — start a fake build, watch the Plan card and the Ready
   phase fire. Tell me if the section labels / Show less / "[Project]
   is live" copy is hitting right.
3. **Third** — read `MARKETPLACE_PIVOT_CRITIQUE.md` before you decide
   how much to invest in Community.
4. **Fourth** — fix the nlm auth so we can run real NLM critiques
   going forward.

If anything looks off, screenshot + send. The biggest risk in a
multi-phase session like this is one DNA × surface combination I
didn't visually test — the mono theme passed `tsc` but I can't
actually see the rendered output. Your eyes are the test there.

— Claude
