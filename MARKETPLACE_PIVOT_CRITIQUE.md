# Marketplace pivot — adversarial critique (2026-05-22)

> **Context.** Marc is considering opening Pebble's Community section to
> third-party designers who can sell premium templates and offer paid
> build services to small businesses. Pebble would take a percentage.
> This document is the adversarial pressure-test before we commit
> engineering time. NLM auth was expired during this session
> (re-run `nlm login` to restore the automated critique path); this is
> the written substitute.

## TL;DR

The marketplace pivot is a **pivot, not an extension**. It changes
Pebble from a SaaS into a two-sided marketplace, which has 3–5× the
operational load of SaaS at the same revenue level. The product
intuition is sound — Lovable and Webflow both monetize this surface —
but the year-1 cost is much higher than it looks, and the supply side
is the hard part, not the demand side.

**Recommendation:** ship Community as a free-supply showcase first
(designers submit, no payments). Validate that designers actually want
to be on Pebble before building Stripe Connect, KYC, payouts, and the
dispute desk that comes with paid templates.

---

## Top 10 failure modes (ordered by likelihood)

### 1. Supply-side chicken/egg — most likely killer

You can't sell templates if no designers list. Designers won't list
without buyers. Webflow solved this by paying their initial 50
designers to populate the catalog; Themeforest solved it via SEO and
existing freelancer community.

**Pebble's starting position:** zero designer mindshare. The pool of
"designers who know Pebble exists" is roughly Marc + close contacts.
The Lovable/Base44/Webflow designer community already has stickier
homes.

**What this looks like at 90 days:** 3 templates listed (Marc made 2,
one designer friend made 1), 0 sales, designers don't return because
nobody's buying.

**Mitigation:** seed the catalog yourself with 20 high-quality
templates BEFORE opening to third-party submissions. Pay 3-5 designers
$500-1500 each to build the first batch. Treat their submissions as
brand assets, not user content.

### 2. Stripe Connect complexity is non-trivial

Standard Connect onboarding:
- KYC verification per designer (tax ID, government ID, address)
- Bank account verification
- Payout schedule configuration
- 1099-K reporting at year-end for US designers (≥$600 threshold)
- VAT collection for EU designers (designer is liable, but you facilitate)
- Currency handling (designer in EUR, buyer in USD)
- Reverse-charge mechanics for B2B EU sales
- Stripe Connect monthly platform fees (1% of volume + per-account fees)

This is 3–4 weeks of pure backend + accounting setup, on top of the
existing Stripe subscription work. Customer support gets a new category:
"my payout didn't arrive."

**Mitigation:** skip Connect. Designers post templates for free, Pebble
keeps Stripe one-sided. Pivot to Connect when you have ≥10 designers
generating ≥$5K/month in template demand — at that point the work is
justified.

### 3. Refund + dispute handling

When a buyer says "this template doesn't work," who pays the refund?
- Pebble eats the cost → moral hazard, designers don't care about quality
- Designer eats the cost → designers won't sell on a platform that auto-refunds
- Pebble mediates → you now run a customer support team

**Real-world numbers:** Themeforest has a 14-day refund policy, ~3-5%
refund rate on digital products, and a full-time dispute team. Gumroad
has similar.

**Mitigation:** "no refunds, all sales final" is legally fine for
digital goods in most US states but kills conversion. The right answer
is auto-refund within 7 days at Pebble's expense for the first 6 months
(treat as customer acquisition cost), then transition to designer-funded
refunds once supply is established. Budget $500-1500/month for
year-1 refund losses.

### 4. Moderation load grows linearly with submissions

Every uploaded template is potential:
- Copyright infringement (stolen designs, unlicensed fonts/images)
- Trademark infringement (uses Apple/Coke/Nike imagery)
- Inappropriate content (adult, hate, illegal)
- Broken/malicious code (XSS payloads in template HTML, prompt-injection
  attacks if templates feed back into the LLM pipeline)
- Quality issues (looks-like-a-toddler-made-it)

You can defer (1)-(3) with a Terms-acceptance click and DMCA process,
but (4) and (5) hurt your brand on every page view. Pebble's pitch is
"sites that don't lie about your business" — that pitch dies if your
template catalog has fabricated stats on every other listing.

**Mitigation:** human review of every submission for the first 1000.
Budget 15-20 min per template. At 50 submissions/week that's 12-15
hours/week — basically a part-time job. Plan for it or don't open
submissions.

### 5. Brand dilution from low-quality templates

Pebble's current positioning ("the site builder that doesn't lie")
depends on visible quality. A marketplace with 200 templates of varying
quality dilutes that signal, even if each individual template meets a
bar. Themeforest has this problem at scale — the marketplace average
quality is mediocre, which makes Themeforest itself feel mediocre.

**Mitigation:** "Pebble Picks" curated tier. Only ~10% of submitted
templates show in the default browse. The other 90% are findable but
require explicit search. Lets the catalog grow without trashing the
front door.

### 6. Customer support multiplies — by category, not just volume

SaaS support is: "billing question," "feature request," "bug." Marketplace
support adds:
- "the designer I hired isn't responding"
- "the template I bought broke after I edited it"
- "I want a refund for X reason"
- "another designer copied my template"
- "I can't find a designer for my industry"
- "designer wants more money than agreed"

Each new category is 30 min/week of human attention, easily 3-5
hours/week additional load.

**Mitigation:** hire/contract a part-time support person at the
$100K ARR milestone. Don't open marketplace until you can afford it.

### 7. Tax compliance — quietly devastating if ignored

US sales tax: Pebble probably has nexus in 2-3 states already
(home state + remote employee states). With marketplace, the marketplace
facilitator laws in 45+ states require Pebble (not the designer) to
collect and remit sales tax on every template sale. This is a real,
significant compliance burden.

EU: VAT MOSS / OSS for digital goods. Designer is liable for VAT
unless Pebble is "platform of record" — likely yes for marketplace.

**Mitigation:** Stripe Tax handles ~80% of this for $40-200/month. Build
in from day 1, NOT after the IRS letter arrives.

### 8. Pricing tension — 30% is industry standard, but bites

App Store: 30%. Themeforest: 25-30%. Gumroad: 9%. Webflow Templates:
20%. Substack: 10%.

Higher cut → lower designer willingness to list. Lower cut → can't
fund the customer support + moderation + Stripe fees. Math at 30% cut
on a $29 template = $8.70 to Pebble. Minus Stripe fees (~$1.50), minus
refund risk (~$0.40), minus moderation (~$1) → ~$5.80 contribution.
You need 50 sales/month per designer just to cover their share of
fixed overhead.

**Mitigation:** start at 15% to attract supply. Document the path to
30% as the catalog matures + tooling improves. Don't quietly raise it
later — designers will revolt.

### 9. Legal exposure scales with marketplace size

You become a publisher (or close to it) under DMCA. You need:
- DMCA agent registered with US Copyright Office ($6/yr)
- Takedown notice process
- Counter-notice process
- Repeat infringer policy

You also become more attractive to copyright trolls. Themeforest gets
~5 takedown notices/week — most are bogus but each requires response
within 14 days.

**Mitigation:** spend $500-1500 on a one-time legal review BEFORE
opening submissions. The DMCA + ToS + designer agreement template
is reusable and cheap once. Fighting a lawsuit later is not.

### 10. Two-sided products fail their first audit (and don't recover)

The biggest failure mode is not any single item above — it's that
Marc spends 3 months building marketplace infrastructure while neglecting
the core SaaS, the SaaS growth stalls (because no shipping for 3 months),
the marketplace launches to crickets, and you're now stuck with two
half-working things instead of one good one.

**Mitigation:** put marketplace on a strict time-box. If it's not
generating ≥$500/month within 90 days post-launch, kill it and refund
designers their listing time as account credit.

---

## Pre-conditions before committing engineering time

Don't start building marketplace until ALL of these are true:

1. **Pebble core SaaS is generating ≥$5K/month MRR.** Otherwise
   marketplace work cannibalizes core growth.
2. **Marc has personally sourced 10 designers** who say they would list
   on Pebble if it launched tomorrow. (Email outreach validates this in
   1 week.)
3. **Marc has personally sourced 10 customers** who say they would buy
   templates from Pebble if there were good ones. (Same.)
4. **DMCA + ToS + designer agreement legal review is complete** ($1500
   investment, 1 week).
5. **Stripe Tax is wired up** ($40-200/month, 1 week of integration).
6. **There's budget for a part-time support contractor** at ~$1500/month.
7. **The "Pebble Picks" curation rubric is written down** — what makes
   a template ship-ready.

If any of these are false, the right move is to wait. The opportunity
isn't going anywhere — Webflow's marketplace launched 8 years after
their core builder. Lovable doesn't even have one yet.

---

## What to ship NOW instead

The current Community stubs (Launchpad / Hire a Partner / Affiliate)
are exactly the right MVP — they validate the demand side without any
marketplace mechanics:

1. **Launchpad** = free showcase. Designers submit, Pebble reviews,
   feature on the page. Zero payments. Zero KYC. Tests whether designers
   *want* to be on Pebble.
2. **Hire a Partner** = mailto-driven matching. You match buyer to
   designer manually for the first 10 deals. Tests whether customers
   *want* to hire from Pebble.
3. **Affiliate** = referral with account credit. Tests whether anyone
   refers Pebble at all.

Run those for 90 days. The data you collect (submissions volume,
template quality, match conversion, referral rate) is exactly what you
need to scope the marketplace properly when you build it.

---

## Decision frame

| If you observe (in 90 days) | Then ship |
|---|---|
| 20+ designer submissions to Launchpad, 5+ "I'd pay for this" emails | Marketplace v1 (free → paid path) |
| <5 submissions, <2 "hire a partner" emails | Kill Community section, focus on core SaaS |
| Mixed signal (10-20 submissions, no demand) | Pebble pays 5 designers to build templates yourself, list as Pebble Studio premium add-on, defer marketplace 6 more months |

---

## What was NOT covered in this critique

- Engineering-time estimates for marketplace v1 (3-4 months minimum,
  including Stripe Connect + KYC + Tax + dispute desk + admin UI)
- Pricing strategy for the cut rate (separate analysis needed)
- Designer onboarding flow design (UX work)
- Search + discovery (the actual marketplace UI is its own project)

These belong in a follow-up document if/when the pre-conditions above
are met.

---

*Written by Claude Opus 4.7 (1M context), 2026-05-22, in lieu of
NotebookLM adversarial pass which was blocked by expired auth tokens.
To restore NLM: re-run `nlm login` in terminal, then call the
`refresh_auth` MCP tool. Marc's Windows scheduled task that normally
refreshes this appears to be failing — worth verifying.*
