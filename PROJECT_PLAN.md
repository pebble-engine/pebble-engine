# Building Pebble — From Founder's Idea to Live SaaS

> The book Marc asked for: every step from now to launch, in plain English.
> Check the boxes as we ship. Read top to bottom.

---

## How to read this

Each chapter is a phase. Each phase has goals + checkboxes. As Claude
ships work, the boxes get checked off. As Marc validates each phase,
he can review and adjust the next one. The order matters — earlier
chapters unblock later ones.

```
[x] = done                              [ ] = not started
[~] = in progress                       [!] = blocked, needs Marc
```

## Where we are now (2026-05-16)

The original plan budgeted 4-6 months for Part II. We're roughly **6 weeks
ahead of schedule**. Here's the snapshot per chapter:

```
Ch 5  Landing page          ━━━━━━━━━━━━━━━━━━━━░  deploy + analytics = Marc
Ch 6  Visual Editor MVP     ━━━━━━━━━━━━━━━━━━━━━  shipped (image swap deferred)
Ch 7  User Accounts         ━━━━━━━━━━━━━━━━━━░░░  profile + GDPR delete open
Ch 8  Dashboard             ━━━━━━━━━━━━━━━━━━━░░  settings page open
Ch 9  Billing (Stripe)      ░░░░░░░░░░░░░░░░░░░░░  BLOCKED on Marc's Stripe pick
Ch 10 Hosting               ━━━━━━━━━━━━━━━━━░░░░  *.pebble.app wildcard open
Ch 11 Customer Onboarding   ━━━━━━━━━━━━━━━━━░░░░  email sequence open
Ch 12 Launch                ░░░░░░░░░░░░░░░░░░░░░  gated on 9 + 10.2
Ch 13 Design breadth        ░░░░░░░░░░░░░░░░░░░░░  MotionSites harvest open
Ch 14 In-app AI chat        ░░░░░░░░░░░░░░░░░░░░░  post-launch
Ch 15 Multi-page sites      ━━━━━━━━━━━━━━━━━━░░░  Schema.org JSON-LD open
```

**Net:** Stripe is the only true MVP blocker. Everything else is either
shipped, blocked on a vendor decision from Marc, or genuinely a Chapter
12+ concern.

---

# PART I — THE FOUNDATION (already in place)

These chapters are DONE. They're the rails everything else rolls on.

## Chapter 1 — The Engine

**Goal:** A working Python engine that generates production Next.js sites.

```
[x] Build pipeline: quiz → DNA → industry intel → assets → LLM → output
[x] 33 quality checks + self-repair loop (was 27; added no_tracking_by_default,
    industry_pages_present, footer_lists_all_pages, a11y_static_audit, +others)
[x] 10 DNA cards (visual personalities per build)
[x] 63-industry intelligence database (was 52; now with LLM fallback for new ones)
[x] VEX-spec foundation hero mandated in every build
[x] AnimatedHeading + FadeIn components (a11y-safe)
[x] Contact form: real Resend Server Action (not fake)
[x] Vercel deploy scaffold (vercel.json + README ## Deploy)
[x] Multi-page generation via PAGE_CATALOG (11 industry-aware page types)
[x] Block library: 6 drop-in DNA-themed sections (testimonials, pricing, FAQ, etc.)
[x] Multi-language: 20-language registry + auto-detect + prompt block
[x] Inspire-from-URL (extract palette/typography from a pasted URL)
[x] Live DNA preview during questionnaire
[x] First-party privacy analytics + forms inbox
[x] ~700 tests passing
```

## Chapter 2 — The Toolchain

**Goal:** Make Claude productive across sessions without re-learning.

```
[x] GitHub Organization: pebble-engine
[x] Repo at github.com/pebble-engine/pebble-engine
[x] CLAUDE.md auto-loads project context every session
[x] Permission allowlist (.claude/settings.json)
[x] Pebble Gmail + Vercel + GitHub identities separated from personal
[x] Cleanup pass: 6,374 lines of dead docs removed
```

## Chapter 3 — The Triangle

**Goal:** Claude + Hermes + NotebookLM operating together.

```
[x] Hermes installed (NousResearch open-source agent framework)
[x] Telegram gateway running, authorized to chat ID 7766344149 only
[x] OpenRouter wired (claude-haiku-4.5 — cheap + capable)
[x] NotebookLM accessible via MCP
[x] 5 scheduled crons (nightly, hourly health, Friday review, Sunday backup, daily uncommitted)
[x] Live log streaming into Claude Code window
[x] Hermes auto-starts on Windows logon (scheduled task)
```

## Chapter 4 — The Safety Net

**Goal:** Nothing important ever gets lost. Recovery from total loss in ~30 min.

```
[x] Layer 1: GitHub canonical source (every commit pushed)
[x] Layer 2: OneDrive backup of .env + strategic docs + Hermes state
[x] Layer 3: Hourly auto-backup (Windows scheduled task)
[x] Layer 4: Hermes auto-restart on logon (Windows scheduled task)
[x] Layer 5: Daily uncommitted-changes alert via Telegram
[x] RECOVERY.md saved in OneDrive — step-by-step rebuild guide
```

---

# PART II — THE PRODUCT (next 4-6 months)

Where we are now. Each chapter ships something visible to customers.

## Chapter 5 — The Landing Page (Week 1, ~3 days)

**Goal:** One public page at getpebble.net that explains Pebble + captures emails.

```
[x] 5.1  Built manually instead of via Pebble engine
         (engine is tuned for local-business sites, not SaaS marketing —
          revisit when engine adds SaaS-landing-page personality)
[x] 5.2  Customized for B2B SaaS framing (inclusive 50+ angle)
[x] 5.3  Six sections shipped:
            • Hero with animated headline, brand-mono tag, waitlist form,
              editorial accent line, AND the soul-line "If you can dream
              it, you can hold it"
            • Problem (three competitors and why each fails this audience)
            • Promise (three differentiators)
            • HowItWorks (3 steps in ~10 minutes)
            • Pricing (Free trial / $29 / $59 + $99 setup call)
            • Footer
[x] 5.4  Waitlist email-capture via Resend Server Action
[x] 5.5  Brand-tuned: amber primary CTAs, 18px+ body, WCAG AAA contrast,
         "no thin font weights" mandate. Soul-line in hero.
[ ] 5.6  Deploy to Vercel under getpebble.net   ← MARC's next move
[ ] 5.7  Plausible analytics                    ← next session
[ ] 5.8  Verify existing dark/cinematic getpebble.net vs new
         warm/inclusive direction — Marc's brand call            ← OPEN
```

## Chapter 6 — Visual Editor MVP (Weeks 2-7, hardest piece) — SHIPPED

**Goal:** Users edit text + colors without writing code or prompts.

**Why this matters:** A 55-year-old real estate agent will NOT type prompts
to change "Welcome to Joe's Plumbing" to "Welcome to Joe & Sons Plumbing."
They want to click the text and type. Without this, the whole product fails.

```
[x] 6.1  Iframe-based preview pane showing the generated site
[x] 6.2  Click any text element → inline editor opens → save updates the file
[x] 6.3  Click background or hero → color picker → save updates Tailwind config
[ ] 6.4  Image swap from a curated gallery (no upload UI yet — defer)
         ← deliberately deferred per original spec
[x] 6.5  Save triggers a fast re-render (no full rebuild)
         — visual-edit endpoint surgically edits files via data-pebble-id manifest
[x] 6.6  Undo / redo stack — implemented as per-mutation snapshots
         (not a 10-step ring buffer; the history drawer lists every mutation)
[x] 6.7  Mobile preview toggle (phone / tablet / desktop) — commit 20fba7f
[x] 6.8  Publish button → triggers re-deploy
         — Cloudflare Pages Direct Upload instead of Vercel (vendor change)
```

## Chapter 7 — User Accounts (Week 8, ~1 week) — MOSTLY SHIPPED

**Goal:** Sign up, sign in, password reset, profile.

```
[x] 7.1  Supabase project set up (Marc has account; migrations 001 + 002 run)
[x] 7.2  Email + password sign-in — Supabase Auth (commit c67540f, 2026-05-16)
[x] 7.3  Google OAuth — plus GitHub OAuth as a bonus
[x] 7.4  Email verification flow — Supabase + welcome-email webhook (98e055b)
[x] 7.5  Password reset flow — /forgot + /reset pages (0697ab3)
[ ] 7.6  User profile page (name, avatar, time zone)
         ← OPEN. No /profile or /settings page exists yet.
[ ] 7.7  Account-deletion flow (GDPR compliance from day 1)
         ← OPEN. Auth handles "dangling session if account deleted"
            but there is no actual delete endpoint or UI.
```

## Chapter 8 — The Dashboard (Weeks 9-10) — MOSTLY SHIPPED

**Goal:** "My Sites" view where users land after signing in.

```
[x] 8.1  Authenticated /dashboard route (proxy.ts gates it via Supabase session)
[x] 8.2  Sites list: each card shows name, type, file count, star, preview link
[x] 8.3  "Create New Site" button → leads into the quiz flow
[x] 8.4  Site detail: preview + edit + delete + publish via /workspace
[x] 8.5  Empty state for first-time users (EmptyState component, line ~516)
[ ] 8.6  Settings page (account, password, plan, billing portal link)
         ← OPEN. No /settings route. Billing portal blocks on Stripe anyway.
```

## Chapter 9 — Billing (Week 11, ~1 week)

**Goal:** Stripe Checkout for $29 Starter and $59 Pro tiers.

```
[ ] 9.1  Stripe products + prices set up in Stripe Dashboard (Marc handles)
[ ] 9.2  Checkout flow (redirects to Stripe-hosted page — simple + secure)
[ ] 9.3  Webhook listener for subscription events (paid / canceled / failed)
[ ] 9.4  Customer portal link (so users manage their own billing — no support load)
[ ] 9.5  7-day free trial logic (no card required for trial start)
[ ] 9.6  Tier swap: upgrade Starter → Pro mid-cycle handled gracefully
[ ] 9.7  $99 one-time setup-call product (Calendly integration)
```

## Chapter 10 — Hosting Generated Sites (Weeks 12-13) — MOSTLY SHIPPED

**Goal:** Each customer's site lives at their.pebble.app and works.

> **Vendor change from the original plan:** Vercel → Cloudflare Pages (Direct
> Upload). Same functional outcome (auto-create project, custom domains, SSL),
> different vendor. Decision was driven by Pebble owning more of the stack
> versus depending on Vercel's GitHub-OAuth flow. ZIP fallback ships always.

```
[x] 10.1  Auto-create deployment per generated site
          → Cloudflare Pages Direct Upload (POST /api/publish, commit a3e9bda)
[ ] 10.2  Sub-domain routing: <slug>.pebble.app (DNS wildcard)
          ← OPEN. Today uses .pages.dev. Needs DNS wildcard decision.
[x] 10.3  Custom-domain wiring (POST/DELETE /api/projects/<slug>/domain)
[x] 10.4  SSL automatic (Cloudflare handles)
[x] 10.5  Contact-form emails delivered via Resend
[ ] 10.6  Generated sites stop working when subscription lapses (graceful warning)
          ← BLOCKED. Depends on Stripe (Chapter 9).
```

## Chapter 11 — Customer Onboarding (Week 14) — HALF SHIPPED

**Goal:** First-build experience flawless. Customers should think "wow."

```
[x] 11.1  Welcome email after sign-up (98e055b, 2026-05-16)
[x] 11.2  Guided first build: 8-question questionnaire
[x] 11.3  Loading screen during generation
          → draft-phase.tsx ("narrated build") in unified workspace
[x] 11.4  First-build success screen with preview + clear next steps
          → edit-phase.tsx (workspace lands here after draft completes)
[x] 11.5  In-app help drawer (a8ca39e — /help with topic sections + intake tooltips)
[ ] 11.6  Email sequence after first build (day 1, 3, 7 — gentle nudges)
          ← OPEN. Needs scheduling infra decision: cron-via-Hermes vs Resend Sequences.
```

## Chapter 12 — Launch (Weeks 15-16)

**Goal:** Open the doors to real paying customers.

```
[ ] 12.1  Final landing page polish (Marc + Claude QA together)
[ ] 12.2  Pricing page live with comparison table
[ ] 12.3  Privacy policy + Terms of Service (Marc handles + a lawyer)
[ ] 12.4  ProductHunt launch prep (assets, story, day-of plan)
[ ] 12.5  Beta-tester recruitment (10-20 friends, agents, small biz owners)
[ ] 12.6  Status page at status.pebble.app (UptimeRobot or BetterStack)
[ ] 12.7  Support inbox routing setup (help@pebble.app → Marc, escalate to Claude)
[ ] 12.8  First $1 of MRR
```

---

# PART III — POST-LAUNCH (Month 5+)

The work that compounds Pebble's lead AFTER the doors open.

## Chapter 13 — Design Breadth

**Goal:** Pebble outputs feel infinite, not "10 templates."

```
[ ] 13.1  MotionSites pattern harvest (100+ premium prompts → style_patterns/)
[ ] 13.2  DNA system restructured: compose pattern + accent (not pick from 10)
[ ] 13.3  User can preview the visual range before committing
[ ] 13.4  10 → 50+ effective visual identities
```

## Chapter 14 — In-app AI Chat

**Goal:** Visitors to a Pebble-built site can chat with the business.

```
[ ] 14.1  Floating chat widget on generated sites (opt-in per customer)
[ ] 14.2  RAG over the site's own content (FAQs, services, about)
[ ] 14.3  Customer brings their own OpenAI key (no platform credits drama)
[ ] 14.4  Conversation history saved per visitor (Supabase)
```

## Chapter 15 — Multi-page Sites (Pro+)

**Goal:** Generate full multi-page apps, not just one-pagers.

```
[ ] 15.1  Quiz extension for multi-page intent (services, projects, blog)
[ ] 15.2  Sitemap.xml + robots.txt auto-managed
[ ] 15.3  Internal linking + navigation structure handled by engine
[ ] 15.4  Schema.org JSON-LD throughout (SEO + AI-agent discoverability)
```

## Chapter 16 — Team Scaling

**Goal:** Hire when the work demands it, not before.

```
[ ] 16.1  First backend engineer (around 500-1000 paying users)
[ ] 16.2  First designer (when design system needs human curation)
[ ] 16.3  SOC 2 Type I prep (when enterprise asks)
[ ] 16.4  Roadmap public + community feedback channel
```

---

# PART IV — DIVISION OF LABOR

What Marc does. What Claude does. No overlap.

## Marc owns

```
- Customer conversations + sales
- Pricing decisions
- Brand voice + messaging
- Legal (Terms of Service, Privacy Policy, vendor contracts)
- Stripe / Domain / Vendor accounts (all credentials)
- Support tickets and customer triage
- Beta-tester outreach
- Demo calls, founder content (Twitter, blog)
- Hermes integration prompts (when expanding Hermes's role)
- Strategic decisions (escalated from Claude or NotebookLM)
```

## Claude owns

```
- 100% of code (engine, dashboard, editor, integrations)
- Architecture decisions (with NotebookLM critique for big ones)
- Testing + quality + repair loops
- Operating across the triangle (Claude / Hermes / NotebookLM)
- Memory + context across sessions
- Engine improvements (DNA system, eval suite, repair patterns)
- Documentation that survives session turnover
```

---

# THE LAST PAGE — What we're working toward

```
[ ] First customer signs up
[ ] First customer makes a payment
[ ] First customer keeps Pebble for 30 days (proves it sticks)
[ ] First customer refers a friend (proves it's loved)
[ ] $1,000 MRR (Pebble pays for itself)
[ ] $10,000 MRR (Pebble pays Marc's salary)
[ ] First hire (Pebble becomes a team)
[ ] Pebble becomes the answer when a 50-something asks
    "how do I get a website?"
```

The book ends here. Read again from Chapter 5 when ready to start work.
