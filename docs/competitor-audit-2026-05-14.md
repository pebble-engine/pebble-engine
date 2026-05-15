# Competitor UX Audit — Lovable + Base44

**Date:** 2026-05-14
**Auditor:** Claude (live browser exploration of both products in Marc's authenticated session)
**Goal:** Understand the UX patterns, copy, and structure so Pebble feels familiar to users switching from either tool — without cloning anything proprietary.

---

## 1. Site Map / Product Map

### Lovable (`lovable.dev`)

```
/                                       Landing (anonymous)
/dashboard                              Personalized home (post-login)
  /dashboard/projects                   All projects grid
  /dashboard/starred                    Starred projects
  /dashboard/created-by-me              Personal projects
  /dashboard/shared-with-me             Shared projects
  /dashboard/resources                  Template gallery ("Resources")
/projects/<uuid>                        Editor (two-panel: chat + preview)
  /projects/<uuid>/settings/billing     Per-project billing
/settings/billing                       Account billing
/seo-aeo                                "Better SEO" product spotlight
```

Sidebar surfaces: **Home · Search (Ctrl+K) · Resources · Connectors · Projects (All, Starred, Created, Shared) · Recents**
Sidebar footer: **Share Lovable (referral CTA) · Upgrade to Pro**

### Base44 (`app.base44.com`)

```
/                                       Personalized home
/apps                                   All apps grid
/app-templates                          Community template marketplace
/integrations-catalog                   Pre-built integrations directory
/plan?id=<id>                           Plan-mode clarification questionnaire
/billing                                Billing
```

Sidebar: **Apps / Superagents (top toggle) · Search · Home · All apps · Integrations · Community · Templates · Favorites · Recents**
Sidebar footer: **Upgrade your plan**

---

## 2. Main Navigation Patterns

| Pattern | Lovable | Base44 |
|---|---|---|
| Primary nav | Left sidebar, dark | Left sidebar, light |
| Workspace switcher | Top of sidebar, dropdown | Top center of header, dropdown |
| Search | Sidebar with `Ctrl+K` keyboard hint shown | Sidebar item |
| Notifications | Bell in sidebar footer | Bell top-right |
| Account menu | Avatar in sidebar footer | Avatar top-right |
| Top-level dichotomy | Single product (build sites/apps) | **Apps vs Superagents** segmented control |
| Recents | Sidebar section | Sidebar section (collapsible) |
| Starred/Favorites | Dedicated section | Dedicated section (collapsible) |

---

## 3. Core User Flows

### Lovable — first-time build

1. Land on `/dashboard` → personalized greeting with first name: **"What's on your mind, marc?"**
2. Type idea in single prompt box (or pick a template from below)
3. Press **Send** → opens editor at `/projects/<id>`
4. **Editor**:
   - Left panel: threaded chat with thinking time ("Thought for 12s"), AI summary cards, undo/feedback buttons
   - Right panel: live iframe of generated site
5. AI suggests next prompts as chips after each response
6. Click any change to refine; **"Visual Edits"** option for free cosmetic tweaks
7. Click **Publish** → modal with auto-generated subdomain `<name>.lovable.app`, edit pencil, "+ Add custom domain [Pro]"

### Base44 — first-time build

1. Land on `/` → headline: **"What will you build next?"**
2. Type idea OR click a **category chip** (Tasks & Workflows / CRM & Sales / Content & Sites / Finance / Booking / More)
3. Press Send → routes to `/plan?id=<id>` (Plan Mode)
4. **Plan Mode questionnaire** — 3 AI-generated multiple-choice questions:
   - Q1/3 — radio buttons (single answer) + "Something else" inline text input
   - Q2/3 — checkboxes (multi-select) + "Something else" + Back button appears
   - Q3/3 — emoji-labeled radio options + button changes to "Send ↑"
   - Persistent free-form field at bottom: *"This space is optional - but powerful. Add ideas, constraints, pivots, or anything the questions missed."*
5. After Q3 → build kicks off

---

## 4. Button / CTA Inventory

### Lovable
- **Build** dropdown next to prompt (toggles Plan vs Build mode)
- **`+`** in prompt → command palette: Attach / Design / Connectors / Databases (each with sub-menu)
- **Mic** for voice input
- **White circular `↑`** to send
- **Publish** (top-right, gradient blue→purple)
- **Share** (top-right)
- **GitHub** (top-right icon button — connects to repo)
- Per-message buttons: Revert to this version · Helpful · Not helpful · Copy · More · Edit · Bookmark in history · Undo latest edit
- Sidebar footer: **Share Lovable** (referral) + **Upgrade to Pro**

### Base44
- **`+`** attach: Upload from computer · Upload from Google Drive · Start from URL · **Migrate from another platform** · Import from Figma · Connectors
- **Tune icon** opens AI Model selector ("Automatic ✓" free, "Upgrade to select an AI model" Pro)
- **Plan** switch (toggle) right of prompt
- **Mic** for voice
- **Black square `→`** to send
- Plan-mode questionnaire: Back · Skip · Next (or Send ↑ on last)
- Sidebar footer: **Upgrade your plan**

---

## 5. Modal / Dialog Patterns

**Lovable Publish modal** (popover anchored to nav button):
- Title row with **"? Docs"** link in the same row — contextual help right where you need it
- Single editable input pre-filled with auto-generated `<adjective>-<noun>-<verb>.lovable.app` subdomain
- Pencil icon to edit subdomain
- Disabled-looking "+ Add custom domain [Pro]" row
- Continue button

**Base44 dialog patterns**: Mostly inline (no modals seen on the surfaces explored). Plan-mode is a full screen instead of a modal — more committed UX.

**Lovable feature-pin menu** ("..."): tile grid of features (Analytics, Cloud, Code, Files, Payments, Security, SEO) each with a 📌 toggle to pin to the top toolbar.

---

## 6. Empty / Loading / Error States

| State | Lovable | Base44 |
|---|---|---|
| Empty Favorites | n/a | "No favorites yet — Add your apps for quick access" |
| Empty Files | "You haven't generated any files yet. Once you create one, it will appear here." | n/a |
| Loading | Aurora gradient placeholder | Subtle skeleton |
| Error (404) | **Giant faded "404" + "This page doesn't exist yet. Want to build it?"** | (not observed) |
| AI thinking | "Thought for 12s" pill above response | Plan-mode questionnaire (proactive, not reactive) |

---

## 7. Editor / Builder Patterns

### Lovable editor
- **Two-panel** layout: chat thread left (variable width), iframe preview right
- Each AI response card has:
  - Bold summary line ("Switched site to black and white")
  - **Bookmark icon** to mark version in history
  - Details/Preview toggle
  - Educational nudge: *"Heads up: simple visual tweaks like colors, text, and fonts are free with Visual Edits — faster than chatting."* with "Read more about Visual Edits" link
  - Feedback row: undo, 👍, 👎, copy, more
- Below: **suggested next-prompt chips** ("Add high-contrast typography", "Regen...")
- Top bar tabs (pinned by user): Files / Code / Cloud / Analytics / Payments / Security / SEO & AI search — accessed via "..." pinnable menu
- Path/URL textbox shows current preview route (`/`)
- Version history panel: linear list grouped by publish status ("Unpublished"), each entry showing the AI's commit-summary + timestamp

### Base44 editor
- Plan-mode comes *before* the editor (proactive clarification)
- (Editor surface not opened — would have required burning credits, declined)

---

## 8. AI Interaction Patterns

| Pattern | Lovable | Base44 |
|---|---|---|
| Where AI lives | Persistent left chat panel in editor | Plan-mode questionnaire upfront; editor unseen |
| Thinking signal | "Thought for 12s" badge | Multi-step Q&A is the thinking signal itself |
| Free vs paid tweaks | Visual Edits = free; chat prompts = credits | Plan-mode = free; build = credits |
| Suggested next-step | Chip strip after each response | n/a (covered by Plan mode) |
| Model transparency | None visible | Selector in prompt header (Pro feature) |
| Voice | Always-visible mic | Always-visible mic |
| Image input | "+" → Attach | "+" → Upload from computer / Drive / Figma |
| Multi-modal source | Figma, drag-drop images | Figma, URL, "Migrate from another platform" |

---

## 9. Template / Gallery Patterns

### Lovable Resources
- Title: "Resources" + tagline "Start from a template to build your next project"
- 2-column tile grid
- Each tile: large empty thumbnail area, bold name, one-line tagline
- Examples: *Lovable slides · AssetWise · EventSpark · CommCalc · Architect Portfolio · Continuum*
- No prices — all templates are free/curated by Lovable

### Base44 App Templates
- Title: **"App Templates"** + tagline "Explore a curated collection of applications built by our community"
- Search bar + Language dropdown + "All Templates" filter dropdown
- Horizontal scroll of category pills: All · Marketing & Sales · Operations · Data & Analytics · Content Generation · HR & Le...
- 3-column grid of template cards with:
  - **Rich thumbnail screenshot** (full preview)
  - Bold name + **price** (`$29.99`, `$35`, `$24.99`, `Free`) — yes, templates are **sold by the community**!
  - Creator name · install count badge (📁 21038)
  - Category tags
- Mix of free (Base44-made) and paid (community-made) — marketplace dynamic

---

## 10. Onboarding Patterns

- **Lovable**: minimal-to-none — drops user directly into the prompt
- **Base44**: minimal home + **Plan-mode questionnaire** acts as just-in-time onboarding the moment the user describes their idea
- Both: zero "tutorial overlay" or "do this first" wizard
- Both: starter chips/categories below the prompt to fight the blank-canvas paralysis

---

## 11. Account / Settings / Billing Patterns

- **Lovable**: settings nested per-project (`/projects/<id>/settings/billing`) AND global (`/settings/billing`)
- **Lovable** referral: "Share Lovable / 100 credits per paid referral" sidebar card with gift icon
- **Lovable** Pro gate examples: Custom domain on Publish modal, model selection (not observed but mentioned in docs)
- **Base44** Pro gates: AI model selector ("Upgrade to select an AI model")
- **Base44** urgency: **countdown timer banner** on home — "Limited time welcome offer / Get 40% off select yearly plans / 47:50:52"

---

## 12. Visual Design Observations

| Aspect | Lovable | Base44 |
|---|---|---|
| Theme | Dark default | Light default |
| Hero ambience | Aurora gradient (pink→purple→orange→blue) | Peach/sunset gradient |
| Logo | Heart-pebble icon, gradient | Orange sun |
| Typography | Modern sans (Inter-feel) | Modern sans, slightly bolder |
| Card style | Dark rounded with subtle border | White rounded with soft shadow |
| Accent colors | Vibrant gradients, purple/orange | Orange primary, plenty of white |
| Iconography | Custom + Lucide-style line icons | Lucide-style line icons |
| Spacing | Generous, editorial | Generous, generous-er — more whitespace |
| Density | Medium (lots of sidebar items visible) | Lower (fewer items, larger touch targets) |

---

## 13. Copywriting / Tone

### Lovable voice
- Personal & informal: *"What's on your mind, marc?"*
- Educational nudges: *"Heads up: simple visual tweaks like colors, text, and fonts are free with Visual Edits — faster than chatting."*
- Encouraging on errors: *"This page doesn't exist yet. Want to build it?"*
- Slight technical undertone (Connectors, Databases, etc. surfaced top-level)

### Base44 voice
- Action-focused & welcoming: *"What will you build next?"*
- Empowering for non-techs: *"This space is optional - but powerful. Add ideas, constraints, pivots, or anything the questions missed."*
- Marketplace-feel in templates: *"Explore a curated collection of applications built by our community"*
- Clearer for beginners (fewer dev terms)

---

## 14. Friction Points

### Lovable
- "Connectors" and "Databases" in the prompt's `+` menu are intimidating for non-technical users
- Dark theme + vibrant gradients can feel "developer-y" — not warm
- Pricing tier gating is everywhere (custom domain, model selection) — feels paywalled-by-default

### Base44
- Countdown timer banner on home felt slightly anxiety-inducing
- "Plan mode" questionnaire is great but no preview of *what* the AI knows yet — the user can't see the AI's draft plan until after Q3 ships
- Apps/Superagents toggle could confuse a first-timer ("which one do I want?")
- Pricing on community templates (`$35`) breaks the "free to try" momentum

---

## 15. Delightful Moments

- **Lovable's personalized greeting** (`What's on your mind, marc?`) — small touch, big warmth
- **Lovable's 404 page** — turns an error into a build prompt
- **Lovable's auto-generated subdomain** (`pebble-shine-sparkle.lovable.app`) — fun, memorable, instantly shareable
- **Lovable's "Visual Edits are free"** education nudge — directly addresses the "credit slot machine" complaint we saw on Reddit
- **Lovable's bookmark-the-AI-response → history** — version control feels human
- **Base44's Plan Mode questionnaire** — multiple-choice format is a brilliant compromise between "blank canvas" and "long form" — feels like a friend helping you scope
- **Base44's emoji-labeled vibe options** (🎮 🚀 🧙) — disarming, fun
- **Base44's "anything the questions missed" field** — humble, generous
- **Base44's "Migrate from another platform"** affordance — explicit acquisition path

---

## 16. Ideas Pebble Should Borrow (Conceptually, Not Verbatim)

| # | Concept | Source | Why it matters |
|---|---|---|---|
| 1 | **Personalized first-name greeting on home** | Lovable | Instant warmth; tiny effort, big return |
| 2 | **Multiple-choice clarification questions before building** | Base44 Plan mode | The single best UX I saw — keeps "magic" feel while gathering structured intent |
| 3 | **Educational nudges inside the chat** ("this is free with Visual Edits") | Lovable | Counters the credit-slot-machine complaint our users have about competitors |
| 4 | **Auto-generated readable subdomain** | Lovable | Branded, sharable; only flip to custom domain when user wants |
| 5 | **Bookmarkable AI responses → version history** | Lovable | Feels like a friend taking notes, not a Git log |
| 6 | **Suggested next-prompt chips after each response** | Lovable | Reduces "what do I type next?" paralysis |
| 7 | **Persistent free-form "anything we missed" field** | Base44 | Generous escape hatch from the structured flow |
| 8 | **Category chips** (not just template names) | Base44 | Functional grouping is more useful than aesthetic grouping for non-technical users |
| 9 | **"Migrate from another platform"** entry point | Base44 | Explicit acquisition surface for Lovable/Base44 switchers |
| 10 | **Sidebar recents + starred** | Both | Standard SaaS pattern; missing from our v3 sidebar |
| 11 | **Search with `Ctrl+K` shortcut** | Lovable | Power-user signal — feels established |
| 12 | **Linear publish history grouped by state** ("Unpublished / Live") | Lovable | Honest visibility into what's actually live |
| 13 | **Workspace switcher in nav** | Both | Future-proofing for team plans |
| 14 | **Empty-state copy with a re-engagement CTA** ("No favorites yet — Add your apps...") | Base44 | Friendlier than just hiding the section |
| 15 | **Pebble-style 404** ("This page doesn't exist yet. Want to build it?") | Lovable | Brand-on moment when something goes wrong |

---

## 17. Things Pebble Should AVOID

| # | Don't do | Why |
|---|---|---|
| 1 | Countdown urgency banners | Anxiety-inducing, reads as "discount-store" not "established company" |
| 2 | A separate "Superagents" segmented control on day one | Adds confusion without clear value |
| 3 | "Connectors" and "Databases" as top-level menu items for our audience | Too technical — keep them inside Setup |
| 4 | Templates as paid marketplace | Splits attention between "build" and "shop"; not our business model |
| 5 | Dark theme as the default | We've committed to universal design; dark = optional toggle |
| 6 | AI Model selector at prompt level | We don't need to expose this — Pebble picks the right model |
| 7 | "Upgrade to Pro" CTA always visible in sidebar | Until billing exists, this would be a hollow promise |

---

## 18. Risks Where Copying Would Be Inappropriate

- **Subdomain word-list** — Lovable's `<adjective>-<noun>-<verb>.lovable.app` algorithm: build our own word lists. Don't reuse Lovable's.
- **Plan-mode question structure** — Base44 generates 3 questions with mixed input types. Concept is fair game; specific phrasings or example options ("Young kids (5-7)", "Colorful & Cartoonish 🎮") must be original to Pebble.
- **404 copy** — Reword in Pebble voice; don't lift "Want to build it?" verbatim.
- **Educational nudge phrasing** — "free with Visual Edits — faster than chatting" is Lovable copy; we'd write our own.
- **Template gallery layout** — Both use a card grid with thumbnail + title + tagline. That's a generic pattern, fine to use. Don't lift specific template names.
- **Visual gradients** — Both products use multi-stop aurora/sunset gradients. Generic; our brand uses Sand/Stone/River instead. Don't try to mimic Lovable's pink-purple or Base44's orange — be Pebble.

---

## 19. Pebble Implementation Plan

### Quick wins (≤ 1 hour each)

| # | Change | Source pattern | Codebase location | Risk |
|---|---|---|---|---|
| QW-1 | Personalized greeting using stored first name | Lovable | `ui/v3/app/page.tsx` headline | None — we already have brief data |
| QW-2 | "Anything we missed?" free-form field on intake step 3 | Base44 | `ui/v3/app/intake/page.tsx` | None |
| QW-3 | Suggested next-prompt chips on the workspace's refinement bar — currently dummy strings, populate from `plan.next_steps` | Lovable | `ui/v3/app/workspace/page.tsx` | None |
| QW-4 | Show "Plan x of 3" progress in the AI Logic Feed on intake | Base44 | `ui/v3/app/intake/page.tsx` | None |
| QW-5 | Pebble-flavored 404 page ("We haven't built this corner yet — want to add it to your plan?") | Lovable | `ui/v3/app/not-found.tsx` (new) | None |
| QW-6 | Auto-generated readable subdomain on publish screen | Lovable | `ui/v3/app/publish/page.tsx` | None |
| QW-7 | "Free with Plan tweaks" educational nudge on the refinement chip bar | Lovable | `ui/v3/app/workspace/page.tsx` | None — addresses credit-slot-machine fear |

### Medium UX improvements (1-3 hours)

| # | Change | Source | Location | Risk |
|---|---|---|---|---|
| MED-1 | Make intake's chip stage feel like Base44 Plan-mode: each "question" is rendered as a card with Q1/Q3 badge, Back/Skip/Next, and a persistent "anything we missed" textarea at the bottom of the screen | Base44 | `ui/v3/app/intake/page.tsx` (full refactor) | Low — improves the page we already have |
| MED-2 | Sidebar shell with Recents + Starred (post-MVP, when multi-project state exists) | Both | New `app/dashboard/*` routes | Medium — needs project listing API |
| MED-3 | Linear version-history panel grouped by Published/Unpublished, with bookmark-the-AI-summary affordance | Lovable | New `app/workspace/history/page.tsx` and engine endpoint `/api/history` | Medium — needs backend snapshot work |
| MED-4 | Workspace iframe gets a faux browser chrome with editable URL + device toggle (Desktop/Tablet/Mobile) | Lovable | `ui/v3/app/workspace/page.tsx` | Low |
| MED-5 | Suggested-prompt chips after each generation, sourced from industry intel | Lovable | `pebble/plan.py` (extend `next_steps` to include refinements) + workspace renders them | Low |

### Larger product/design improvements (> 3 hours)

| # | Change | Source | Location | Risk |
|---|---|---|---|---|
| LRG-1 | "Migrate from another site" entry point: take a URL, scrape the existing site, propose a refresh | Base44 | New `/migrate` route + engine endpoint | High — needs scraping infra |
| LRG-2 | Pinnable feature tiles in workspace (Analytics / SEO / Payments) hidden behind "..." with 📌 toggles — but each tile shows our honest status (Auto / Soon / Manual), not just a feature panel | Lovable | Workspace toolbar refactor | Medium — UX is intricate |
| LRG-3 | Template gallery (Pebble-curated only, all free; no marketplace) with category chips | Base44 | New `/templates` route | Medium |
| LRG-4 | Workspace search with `Ctrl+K` palette: find a page, jump to a section, run a refinement | Lovable | New `<CommandPalette>` component | Medium — needs page indexing |
| LRG-5 | Visual Edits surface: click any element on the preview iframe to edit text/color/spacing **without spending generation credits** | Lovable | Workspace `postMessage` wiring + a side editor panel | High but high-value — addresses the #1 cost complaint |

---

## 20. Tone of Voice — What "Established Company" Means For Pebble

Marc asked: *"Our website needs to look like a fully established and professional company with many employees."*

Both Lovable and Base44 achieve "established" through:
1. **Confidence in copy** — no apologies, no caveats, no hedging
2. **Cohesive visual system** — every screen feels like the same company made it
3. **Multiple product surfaces** that hang together (templates, integrations, community, billing)
4. **"Quiet" details** like keyboard shortcuts, contextual help links, breadcrumbs
5. **Generosity** — Lovable's "free with Visual Edits" feels like a real company that respects your time

**Pebble's existing assets that already say "established":**
- The brand palette (Sand/Stone/River/Sage) — confident, not trendy
- Literata + Inter — editorial, considered typography
- The honest setup-needs system — feels like a real company that doesn't lie

**What we should add to feel even more established:**
- A docs link in dialog headers (Lovable's "? Docs" pattern) — even if docs are stubbed
- Keyboard shortcuts surfaced (Ctrl+K for search, Cmd+K for command palette)
- Workspace switcher in nav (even if there's only one workspace today — signals team-readiness)
- A footer on the welcome page listing: Templates · Pricing · Docs · Status · Privacy · Terms (each a real route, even if some are placeholder pages)
- The 404 page with on-brand copy

**End of audit.**
