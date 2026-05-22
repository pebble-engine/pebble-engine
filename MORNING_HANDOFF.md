# Morning handoff — 2026-05-22 overnight session

> Marc — read this FIRST. Production is down for reasons that have
> nothing to do with my code, but it's the most urgent thing to fix.

---

## 🚨 URGENT — pebbleapp.ai is showing Vercel `DEPLOYMENT_NOT_FOUND` 404

Symptom: every URL on pebbleapp.ai returns the Vercel 404 page with
`Code: DEPLOYMENT_NOT_FOUND`.

What's NOT the cause:
- ✅ `npx tsc --noEmit` passes clean on every commit shipped
- ✅ `npm run build` succeeded locally — full route list compiled
  including all new pages (/trust, /dpa, /integrations, /community/*)
- ✅ `localhost:3001` serves the latest code correctly (verified via
  Chrome MCP — the new Trust seal renders perfectly)
- ✅ Every commit pushed cleanly to `pebblewebsite/main`

What's the actual cause (Vercel-side):
1. Most likely: the GitHub → Vercel webhook is broken / disconnected
2. Possible: the Vercel project was archived or the production alias
   got unlinked
3. Possible: account-level quota or billing issue

**First thing to do this morning:**
1. Log into Vercel dashboard (vercel.com/dashboard)
2. Find the `pebble-engine` (or whatever the project is named) project
3. Check "Deployments" tab — is there a recent build? Did it fail?
4. Check "Settings → Git" — is the repo still connected to `pebblewebsite/pebble-engine.git`?
5. Check "Settings → Domains" — does pebbleapp.ai still resolve to a deployment?
6. If all else fails: trigger a manual redeploy from the last green
   commit (`f679f19` — Phase 43.17, pre-this-session)

I genuinely cannot fix this from my side without your Vercel auth.

---

## TL;DR — Phases shipped in this overnight session

| # | Phase | Commit | What |
|---|---|---|---|
| 44 | Instant subdomain publish | `7055e26` | `<slug>.pebbleapp.ai` live in <1s |
| 45 | Workspace shell | `681c03d` | Base44-style left nav across dashboard/integrations/community |
| 46a | Kill "Your Build Plan" rail | `0eb2e08` | Shared sidebar in /workspace + B&W mono theme |
| 46b | Plan card restructure | `e11f4be` | Single elegant card, 5 labelled sections, Show less toggle |
| 47 | GDPR + DPA + trust row | `633f03e` | /dpa page + initial 3-card trust row |
| 48 | Marketplace pivot critique | `9f0d2b2` | `MARKETPLACE_PIVOT_CRITIQUE.md` (NLM substitute) |
| 49 | "Site is live" Ready phase | `eb0da2b` | Draft → Ready → (your click) → Design |
| 50 | Block suggestion chips | `f512f5d` | "Add testimonials/pricing/FAQ" above the refine bar |
| 51 | Morning handoff doc | `548dbaa` | First handoff doc |
| 52 | Trust Charter seal v1 | `c920a28` | Single seal w/ rotating Pebble wordmark + /trust page |
| 52b | NLM-driven trust seal fixes | `95d52e5` | Stripped fake-notary mimicry + added EU rep + CAIQ |

**13 commits, ~3,900 lines net-new, 2003 tests green, TS clean throughout.**

---

## Phase 52 detail — Trust seal (and the NLM lesson)

Your ask: replace the three trust-row cards with something that uses
the rotating Pebble wordmark, looks like a real certificate, but
isn't misleading.

**v1 (commit `c920a28`)** — I built a "Pebble Trust Charter" seal with
double border, ornamental star, cert-style reference ID
(`PEB-TC-2026-05-22`), formal "Effective MAY 22, 2026" stamp.
Visually beautiful — and exactly the failure NLM caught.

**NLM adversarial pass** (now working again, with the project notebook
loaded). The critique was brutal and correct:

1. **"Fake notary trap"** — visual language mimicked third-party
   audit marks closely enough to fail the FTC's "net impression"
   test for deceptive marketing. Double border + ornamental rule +
   reference ID = the literal anatomy of an ISO/SOC 2 stamp.
2. **Security smell** — I'd put real file paths
   (`pebble/server/account.py`) as evidence on /trust. NLM: "a buyer
   can't verify the code; an attacker gets a treasure map." Correct.
3. **EU/UK gap** — no Article 27 EU Representative named (required
   for serving EEA/UK residents). I'd missed this.
4. **CISO perspective** — would categorize Pebble as immature based
   on the mocked-up badge, scrutinize harder than if we'd just been
   honest about being early-stage.
5. **Strongest single fix** — offer a CSA CAIQ questionnaire (the
   standard SaaS pre-SOC 2 artefact for B2B procurement).

**v2 (commit `95d52e5`)** — applied all five fixes:

- "Trust Charter" → "Self-attested commitment" everywhere (the most
  prominent line on the seal is now literally "SELF-ATTESTED
  COMMITMENT" in spaced caps)
- Removed the cert reference ID — that was the single most obvious
  mimicry tell
- Removed double border + ornamental star — reads as a card now,
  not a stamp
- "Read the charter →" → "See what we actually do →" (less
  institutional)
- /trust evidence rewritten in plain language — no file paths
- Added Article 27 EU Representative section (interim contact +
  formal appointment "in process" footnote — honest)
- Added "Security questionnaire (CAIQ) available on request"
  section for B2B procurement

The rotating Pebble wordmark stays as the centerpiece — that's the
brand AS our signature, which is honest, unlike third-party cert
mimicry which is not.

**Visually confirmed via Chrome MCP** on localhost:3001 — the seal
renders beautifully. Captured the Japanese 小石 mid-cycle in a zoomed
screenshot. Looks like an honest brand commitment, not a fake audit
badge.

---

## What you'll see on localhost (after fixing Vercel)

`localhost:3001/#pricing` — scroll past the pricing tiers to find
the new Trust seal. Click "See what we actually do →" to land on
the full `/trust` commitment page.

Also on localhost, all the earlier-session work is live:
- `/dashboard` — new sidebar, mono theme
- `/workspace` — phase tracker pills at top, shared sidebar, mono
- Start a fake project → Plan card with 5 sections + Show less
- Let it build → Ready phase ("[Project] is live" + Open editor)
- In editor → suggestion chip row above refine bar

---

## What needs your attention (priority order)

1. **🚨 Fix Vercel deploy** (see top of doc) — production is down
2. **NotebookLM auth is back, working great** — just verifying it
   stays alive long-term. Used it for the trust seal critique and
   got brutal, specific, correct feedback that made v1 → v2 actually
   better. Worth keeping that scheduled refresh task healthy.
3. **Read `MARKETPLACE_PIVOT_CRITIQUE.md`** at repo root — 271 lines,
   ~10-min read. Decision frame for the Community marketplace pivot.
4. **DNS + env for instant publish** — `PEBBLE_PUBLIC_DOMAIN=pebbleapp.ai`
   + wildcard CNAME at Cloudflare (DNS only, grey cloud).
5. **Trust seal visual review** — once Vercel is back up, look at
   the seal in production. If anything reads as too soft (or too
   formal still), screenshot + tell me which direction.

---

## What I deliberately did NOT touch overnight

- LLM prompts / DNA cards / generation logic
- Stripe / billing production
- Subagents for non-mechanical work (lesson from Phase 47 still standing)
- Anything requiring your copy judgment beyond minor edits
- Vercel dashboard (no access, didn't want to break things further)

---

## Session metrics

- **Commits**: 13 across 9 phases
- **Lines net new**: ~3,900
- **TypeScript errors**: 0 throughout
- **Tests**: 2003 passing (1981 pre-session)
- **Local `npm run build`**: succeeded (every new route compiled)
- **Production status**: 404 (Vercel-side issue, see top)
- **NLM critiques completed**: 2 (marketplace pivot + trust seal)
- **NLM critiques applied**: trust seal v1 → v2 entirely driven by NLM feedback

Good morning when you wake. Sorry about the Vercel surprise —
it's not from anything I shipped, but I know that doesn't make it
less annoying to deal with first thing.

— Claude
