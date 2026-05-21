# 2026-05-20 night wrap — strategic pivot

_Late-night session. Started with mechanic-build refinement, ended with strategic clarity on the right 1-2 weeks of work._

## What actually landed (real shipped work)

1. **Phase 23a — Layout DNA picker fix.** Trades briefs now correctly route to Weather Report / single_screen instead of falling through to Terminal. The hero of every future mechanic / plumber / HVAC / contractor brief will be appropriate to the trade. Code + 4 regression tests on disk, 1716 tests passing.

2. **Phase 25a — Plan Reveal in v3 workspace.** The Webild-parity perceived-speed UX: project name + palette + section structure + design chips animate in over the first ~15 seconds while the real build runs for 2-3 minutes. Engine emits 3 new SSE event shapes (`started.business_name`, `style.palette`, new `plan` event), v3 draft-phase renders them in a Plan Reveal card. TypeScript clean, end-to-end working.

3. **Phase 24 — Webild teardown.** Full strategic dissection of webild.io. Confirmed they're Next.js+Vercel+Clerk on Vercel, AI proxied through api.webild.io, customer previews run in per-project cloud sandboxes (`3000-<id>.sandbox.webild.io`). Pricing: $0/$16/$24/$49 tiered by credits. Premium templates are human-designed, not AI-generated. **Their AI gen is comparable to Pebble's. Their template gallery is the differentiator.**

## Tonight's diagnostic — Claude vs Qwen on identical brief

Ran the same mechanic brief on both. Both correctly picked Weather Report DNA (Phase 23a working consistently). What differed:

| | Qwen Flash | Claude Sonnet 4.5 |
|---|---|---|
| Cost | $0.02 | $0.58 (28×) |
| Time | 187s | 437s |
| Followed AnimatedHeading instruction | No | **Yes** |
| Followed MagneticButton instruction | No | **Yes** |
| Added gradient mesh blobs | No | **Yes** |
| Layout shape | Weather Report dashboard | Same Weather Report dashboard |

**Conclusion:** model swap moves execution polish, not layout shape. **DNA controls the structural feel, model controls the execution quality.** Both Qwen and Claude on Weather Report produced trades dashboards — functionally correct for a mechanic, but not the "premium landing page" Marc actually wants for the product positioning.

The slop verdict on the Qwen mechanic build was correct. The fix isn't "prompt better" — it's "different DNA shape" + "better source material for templates".

## The strategic pivot (the real outcome of tonight)

**Stop chasing the LLM ceiling. Templates are the answer, and Marc has the source material.**

Two new phases added:

### Phase 31 — Ingest Marc's HTMLs as the template gallery foundation (1-2 weeks)
Marc has 10-20 existing playground HTMLs he considers his best output. Those become the gallery starting points:
1. Marc shares the HTMLs (paste / folder path)
2. Convert each to a Next.js project skeleton with tokenized content (business_name, services, colors, copy)
3. Screenshot each
4. Build `/templates` route in v3 with grid + click-to-instantiate
5. `/api/instantiate-template` runs a focused ~3K-token content-swap LLM call (10-100× cheaper than full gen)
6. Free tier defaults to template-pick. Custom AI gen becomes paid.

**Tomorrow's first move: Marc shares the HTMLs.** Easiest format is a folder path on the machine + a one-line list of which 10-20 are his picks. I'll convert one as a proof-of-concept first build, we look at it together, then crank through the rest.

### Phase 30 — Cinematic-first DNA rebrand (2-3 weeks, in parallel with templates)
Refactor the DNA system: every Layout DNA produces a cinematic landing page by default. Demote trades-utility patterns (OPEN/CLOSED indicator, today's availability) to optional INNER-page sections, not hero. Cull or merge niche DNAs (Terminal, Chat Log, Index Card, Manifesto) that don't fit the cinematic-first shape. Every hero gets real photographic atmosphere + bold typography + clear visual hierarchy.

This is the longer play. Templates ship first; DNA rebrand happens in parallel and lands later.

## What's running for you tomorrow

| Port | What | Status |
|---|---|---|
| 8000 | Engine on Claude Sonnet 4.5 (env override) | alive |
| 3060 | OLD Terminal mechanic (this morning's bad render) | alive |
| 3061 | Weather Report mechanic w/ photo overlay (tonight's "still slop" Qwen run) | alive |
| 3001 | (was running v3 earlier; may have died) | check before use |
| — | Claude Sonnet build at `output/queens-premier-auto/` | not yet served; boot if you want to see |

To see the Claude build: `cd output/queens-premier-auto/site && npx next dev -p 3062`

## What's NOT done — still pending

- Phase 23b: Restore cut cinematic Code Patterns conditionally — deferred, may become moot if Phase 30 DNA rebrand subsumes it
- Phase 25b: Bot persona ("Pebble" greeting via cheap LLM) — still queued
- Phase 26: Template gallery — SUPERSEDED by Phase 31 (Marc's HTMLs)
- Phase 27: Cloud sandbox preview — still queued (the architectural one)
- Phase 28: Hybrid model routing — VALIDATED tonight (Claude IS measurably better for execution polish at 28× cost — worth wiring for paid tier)
- Phase 29: Extend next_js_static_check to catch `document` SSR refs — minor
- Phase 30: Cinematic-first DNA rebrand — NEW, 2-3 weeks
- Phase 31: Ingest Marc's HTMLs as templates — NEW, 1-2 weeks, starts tomorrow

## Working tree status

Branch `main`, **nothing committed today**. Tomorrow Marc reviews `git status` and decides what to keep / commit / push. The morning and evening hand-off docs are at:
- `MORNING_RESULTS.md` (today's morning)
- `END_OF_DAY_RESULTS.md` (today's afternoon)
- `TONIGHT_CHECKPOINT.md` (early evening)
- `NIGHT_WRAP.md` (this file — the strategic pivot)

Sleep well. The product is genuinely more clearly positioned tonight than it was 4 hours ago — the templates path is the right one, you correctly intuited it, and you already have the source material. That's a good place to wake up to.

— Claude
