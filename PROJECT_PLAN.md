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

---

# PART I — THE FOUNDATION (already in place)

These chapters are DONE. They're the rails everything else rolls on.

## Chapter 1 — The Engine

**Goal:** A working Python engine that generates production Next.js sites.

```
[x] Build pipeline: quiz → DNA → industry intel → assets → LLM → output
[x] 27 quality checks + self-repair loop
[x] 10 DNA cards (visual personalities per build)
[x] 52-industry intelligence database (curated)
[x] VEX-spec foundation hero mandated in every build
[x] AnimatedHeading + FadeIn components (a11y-safe)
[x] Contact form: real Resend Server Action (not fake)
[x] Vercel deploy scaffold (vercel.json + README ## Deploy)
[x] 206 tests passing
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

**Goal:** One public page at pebble.app that explains Pebble + captures emails.

This is the FIRST thing potential customers see. Must be exceptional.

```
[ ] 5.1  Use Pebble itself to generate the base (eat our own dog food)
[ ] 5.2  Customize the prompt for B2B SaaS framing (not local-business)
[ ] 5.3  Sections in order:
            • Hero: the story (50+ small business owner who's nervous about AI)
            • The problem (Squarespace is bland, Wix is dated, Lovable is too technical)
            • The promise (8 questions, world-class site, full ownership)
            • How it works (3-step visual: quiz → preview → deploy)
            • Pricing teaser (Free trial → $29 → $59 + setup call)
            • Trust signals (DNA examples, generated-site gallery)
[ ] 5.4  "Join the waitlist" email-capture (Resend Server Action — we built this)
[ ] 5.5  Deploy to Vercel under pebble.app (Marc registers domain)
[ ] 5.6  Set up Google Analytics + Plausible (privacy-friendly traffic measurement)
```

## Chapter 6 — Visual Editor MVP (Weeks 2-7, hardest piece)

**Goal:** Users edit text + colors without writing code or prompts.

**Why this matters:** A 55-year-old real estate agent will NOT type prompts
to change "Welcome to Joe's Plumbing" to "Welcome to Joe & Sons Plumbing."
They want to click the text and type. Without this, the whole product fails.

```
[ ] 6.1  Iframe-based preview pane showing the generated site
[ ] 6.2  Click any text element → inline editor opens → save updates the file
[ ] 6.3  Click background or hero → color picker → save updates Tailwind config
[ ] 6.4  Image swap from a curated gallery (no upload UI yet — defer)
[ ] 6.5  Save triggers a fast re-render (no full rebuild)
[ ] 6.6  Undo / redo stack (10-step history)
[ ] 6.7  Mobile preview toggle (phone / tablet / desktop)
[ ] 6.8  Publish button → triggers a Vercel re-deploy
```

## Chapter 7 — User Accounts (Week 8, ~1 week)

**Goal:** Sign up, sign in, password reset, profile.

```
[ ] 7.1  Supabase project set up (Marc creates account)
[ ] 7.2  Email + password sign-in
[ ] 7.3  Google OAuth (for non-technical users who'd rather click than type)
[ ] 7.4  Email verification flow (Resend-powered)
[ ] 7.5  Password reset flow
[ ] 7.6  User profile page (name, avatar, time zone)
[ ] 7.7  Account-deletion flow (GDPR compliance from day 1)
```

## Chapter 8 — The Dashboard (Weeks 9-10)

**Goal:** "My Sites" view where users land after signing in.

```
[ ] 8.1  Authenticated /dashboard route (redirects to /signin if not logged in)
[ ] 8.2  Sites list: each card shows thumbnail, name, status, last edited
[ ] 8.3  "Create New Site" button → leads into the quiz flow
[ ] 8.4  Site detail page: preview + edit + delete + deploy buttons
[ ] 8.5  Empty state for first-time users (welcoming, not confusing)
[ ] 8.6  Settings page (account, password, plan, billing portal link)
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

## Chapter 10 — Hosting Generated Sites (Weeks 12-13)

**Goal:** Each customer's site lives at their.pebble.app and works.

```
[ ] 10.1  Auto-create Vercel project per generated site (Vercel API)
[ ] 10.2  Sub-domain routing: <slug>.pebble.app (DNS wildcard)
[ ] 10.3  Custom-domain wiring for Pro tier (joe-plumbing.com → their.pebble.app)
[ ] 10.4  SSL automatic (Vercel handles)
[ ] 10.5  Contact-form emails delivered via shared Resend account
[ ] 10.6  Generated sites stop working when subscription lapses (graceful warning)
```

## Chapter 11 — Customer Onboarding (Week 14)

**Goal:** First-build experience flawless. Customers should think "wow."

```
[ ] 11.1  Welcome email after sign-up (warm, no jargon, "here's how to start")
[ ] 11.2  Guided first build: 8 questions, no skips, ~5 min start to finish
[ ] 11.3  Loading screen during generation (story-driven, not a spinner)
[ ] 11.4  First-build success screen with preview + clear next steps
[ ] 11.5  In-app help drawer (plain-language FAQs, no support tickets needed)
[ ] 11.6  Email sequence after first build (day 1, 3, 7 — gentle nudges)
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
