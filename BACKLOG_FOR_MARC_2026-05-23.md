# Pebble backlog — handoff for Marc (2026-05-23 EOD)

You asked for "things that need to be done" if I run out of safe-autonomous
work. Here it is, prioritized by where you can move things forward fastest.

I went through PROJECT_PLAN.md, the memory files, the morning brief output,
the OVERNIGHT_BUG_HUNT doc, and grepped for TODOs across the codebase.
Below is everything I found, triaged.

## What I shipped today (recap, so it doesn't get lost)

20 commits on `phase56a-for-squitopest` since last night, all pushed to
`origin` + `squitopest`. Highlights:

**Security (overnight + morning):**
- 7 auth gates closed on engine APIs (`/api/projects`, `/api/usage`,
  `/api/admin/*`, `/api/projects/<slug>/integrations` GET,
  `/api/enrich-content`, `/api/migrate`, log PII redaction)
- 6 Supabase advisor findings fixed via paste-ready SQL migration
- 5 v3 frontend bugs from the parallel-agent code review

**Observability:**
- Sentry wired across the engine (Python) + v3 (Next.js) with PII scrubber
  + cost-disciplined sample rates
- Sentry MCP wired into Claude Code (OAuth-authed, 23 tools available)
- Supabase MCP wired (read-only, project-scoped)

**Tier-2 autonomy v1:**
- `pebble/morning_brief.py` — runnable Python module that gathers data
  from 7 sources (engine logs, git, build_meta, engagement, subscriptions,
  Sentry, Supabase) and renders a Markdown brief with severity rollup.
  16 tests pinning the contract.
- `docs/MORNING_BRIEF.md` — design doc + v2/v3 roadmap
- `MORNING_BRIEF_SAMPLE_2026-05-23.md` — today's enriched sample

---

## 🟡 TEED UP — needs YOU, ~30 sec each

These are paste-and-go. The hard work's done; just kick them off:

1. **Supabase perf migration** — `SUPABASE_PERF_MIGRATION_2026-05-23.md`.
   Resolves 2 WARN findings the morning brief surfaced (`auth_rls_initplan`
   on `public.profiles`). One transaction, idempotent. Paste into Supabase
   SQL Editor → Run.

2. **Generate `SENTRY_PAT`** (5 min): https://pebble-6q.sentry.io/settings/account/api/auth-tokens/
   Name it `morning-brief`, scopes `org:read` + `project:read` + `event:read`.
   Add to `.env` as `SENTRY_PAT=<token>`. Then the morning brief pulls
   live Sentry data instead of saying "skipped".

3. **Generate `PEBBLE_SUPABASE_PAT`** (5 min): https://supabase.com/dashboard/account/tokens
   Add to `.env`. Same effect for Supabase advisor section.

4. **Apply Stripe bootstrap** (PROJECT_PLAN Ch 9 outstanding):
   - Fix `STRIPE_WEBHOOK_SECRET` in `.env` — currently has an `rk_test_`
     pasted into the slot. Should be `whsec_...` from `stripe listen` or
     Dashboard webhook config.
   - Run `python -m pebble.stripe_bootstrap`, paste the three
     `PEBBLE_STRIPE_*_PRICE_ID` values into `.env`.
   - Install Stripe CLI: `scoop install stripe`.
   - E2E test: `stripe listen --forward-to localhost:8000/api/internal/stripe-webhook`,
     then v3 `/settings` → "Manage billing" → card `4242 4242 4242 4242`.

5. **`*.pebbleapp.ai` DNS wildcard** (Ch 10.2):
   Cloudflare DNS → add `*.pebbleapp.ai` CNAME → `pages.dev`.
   Then set `PEBBLE_APP_DOMAIN=pebbleapp.ai` in `.env`. This is the LAST
   true MVP blocker per PROJECT_PLAN's launch math.

---

## 🔵 CLAUDE-OWNED — safe to tackle next session (no tokens needed)

Prioritized by impact:

### Tier 1 (high impact, ~1-3 hrs each)

1. **Multi-project URL** — Lovable-parity backlog T1.1.
   Today `/workspace` reads `localStorage.pebble.lastBuild`. Shared URLs,
   bookmarks, multi-tab don't work. Move to `/workspace/<slug>` dynamic
   route. Touches: workspace-shell, sidebar, dashboard, middleware,
   several hard-coded `/workspace` strings. Medium-large refactor;
   significant UX win once you have 3+ projects.

2. **Morning brief Hermes wiring** — once you've generated the PATs.
   Add a Hermes cron entry that runs `python -m pebble.morning_brief
   --json` at 8am, pipes through Telegram. ~30 min once the tokens are
   in place. Per docs/MORNING_BRIEF.md design.

3. **Editable Pebble Plan from design phase** — Lovable-parity T1.4.
   Today the plan is locked once generated. Add an "Edit plan"
   affordance from design phase that lets users tweak audience/goal
   without re-running the whole build. ~3 hrs (UI + state plumbing,
   plan re-emit on save).

### Tier 2 (medium impact, smaller scope)

4. **`unused_index` cleanup** (~5 min Supabase). The performance advisor
   also flagged `idx_waitlist_email` as never used. Drop it via:
   ```sql
   DROP INDEX IF EXISTS public.idx_waitlist_email;
   ```
   Marginal storage savings; mostly to keep the advisor feed clean.

5. **Re-enable engine.err.log per-line timestamping** — morning-brief v2
   work. Right now I scan the last 5MB and report "what's there" rather
   than "what's in the last 24h" because lines aren't timestamped.
   Adding a `[YYYY-MM-DD HH:MM:SS]` prefix to every `log.info` /
   `log.warning` call (or just switching the logger format string) would
   make the brief honest about the window. ~1 hr.

6. **Smooth rail slide-in transition** — Lovable-parity T3.10. When
   phase flips from welcome → idea, the left rail appears abruptly.
   Add opacity+x slide-in for the rail mount. ~30 min cosmetic polish.

### Tier 3 (longer-horizon, needs design discussion)

7. **Phase 23b: Restore cinematic Code Patterns (conditional on Layout DNA)**.
   Some cinematic prompt patterns were cut in earlier work; restore them
   in a Layout-DNA-conditional way. Needs your design taste call on which
   patterns to bring back and how.

8. **Phase 27: Cloud sandbox preview (per-project shareable URL)**.
   Big infra work — would let users send "preview my site" links to
   friends without publishing. Skipped in earlier rounds.

9. **Phase 28: Hybrid model routing (cheap chat + smart builder)**.
   Routing decision (cost vs quality trade-off) needs your input.

10. **Phase 30: Cinematic-first DNA rebrand**. Per memory
    `project_2026-05-18_cinematic_pivot.md` — directional change in DNA
    feel; needs your design call.

---

## 🟢 LAUNCH BLOCKERS — Marc-side, PROJECT_PLAN Ch 12

The truly-final items before doors open:

- [ ] **12.1**: Visual QA pass on landing page (you + me, side-by-side)
- [ ] **12.3**: Lawyer review of `/privacy` + `/terms` (drafts shipped)
- [ ] **12.4**: ProductHunt launch prep — story, assets, day-of plan
- [ ] **12.5**: Beta-tester recruitment (10-20 friends, agents, small biz)
- [ ] **12.6**: BetterStack monitor pointing at `/api/health` (engine returns `engine_ok:true`)
- [ ] **12.7**: Support inbox routing (`help@pebbleapp.ai` → you, escalate to Claude)
- [ ] **12.8**: First $1 of MRR 🚀

---

## 🚫 INTENTIONALLY DEFERRED — don't touch without discussion

These are real ideas that aren't yet aligned with the product principles
or are intentionally waiting:

- **Supabase Pro upgrade ($25/mo)** — defer until first paying users.
  Unlocks leaked-password protection + point-in-time recovery + more
  bandwidth. Per OVERNIGHT_BUG_HUNT doc.

- **Persistent chat panel in workspace** — Lovable-parity T1.3 (intentional diff).
  Pebble's refine chips are deliberate per "more options, less overwhelm."

- **Mid-build Plan Mode toggle** — Lovable-parity T2.9 (intentional diff).
  Same — plan phase IS Pebble's plan mode, just gated to pre-generation.

- **Code mode in workspace** — Lovable-parity T2.8 (intentional diff).
  Pebble's universal-design framing explicitly avoids exposing code editing.

- **Prompt Queue** — Lovable-parity T2.6 (intentional diff).
  Pebble generates whole sites from a structured plan, not prompts.

- **Auto-merge agent (Tier-3 autonomy)** — per the Jarvis discussion.
  Hold at Tier-2 (recommend + open PR for human review) for now.

---

## What I'd pick if YOU asked me to keep going

If you came back and said "just keep working, surprise me," I'd pick
**#1 Multi-project URL** from Tier 1. It's the highest-impact UX win
that doesn't need any external decision from you — you have multiple
projects today (4 visible in your dashboard) and the lack of a working
shared URL is a real friction. ~2-3 hrs of careful refactoring with a
clear test plan. Wouldn't touch anything risky.

If you wanted something faster, **#2 Hermes wiring for the morning brief**
once you've generated the two PATs — that's the visible payoff of all
today's setup work, and it crosses the line from "thing exists" to
"thing happens automatically."

---

## State of the branch

```
phase56a-for-squitopest  (20 commits ahead of last night's push)
                         pushed to origin + squitopest
                         pebblewebsite remote is stale (404 — separate cleanup)
                         no Vercel rebuild triggered (feature branch only)
```

Test suite: **2136 passing**, zero regressions. TypeScript clean.

Engine on port 8000 still running from the worktree (booted earlier with
Sentry wired). Safe to leave running — it's logging to Sentry and won't
crash on your absence.

Take your time. Nothing's on fire.
