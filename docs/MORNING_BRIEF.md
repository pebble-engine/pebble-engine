# Morning Brief — design doc

Marc's vision (2026-05-23): *"Boot up the computer in the morning and get
complete breakdowns of what happened in plain language."*

This doc captures what v1 does, what v2/v3 will add, and the autonomy
boundary that keeps it safe.

## Tier-2 autonomy boundary

The brief **reads everything, writes nothing.** It surfaces signal —
sometimes with prose recommendations — but never takes action. Marc
reviews and decides.

Why not Tier-3 (auto-fix)? Even Claude makes mistakes. A bad auto-merge
during sleep takes down a paying-customer site. The morning brief is
the diagnostic; the merge is the human gate. We can revisit once
there's a track record of zero false-positive auto-recommendations
across N months.

## What v1 ships (today)

A single Python module: `pebble/morning_brief.py`. Runnable on demand
right now; can be wired to a cron/scheduler later.

```
# Print today's brief to stdout
python -m pebble.morning_brief

# 7-day window instead of 24h
python -m pebble.morning_brief --hours 168

# Write to a file
python -m pebble.morning_brief --out tomorrow_morning.md

# JSON for programmatic consumers (Hermes pipeline, dashboard)
python -m pebble.morning_brief --json

# Run from a worktree but report on the base repo
python -m pebble.morning_brief --root C:/Users/marci/pebble-engine
```

### Sections (in display order)

| # | Section | Source | Needs PAT? |
|---|---|---|---|
| 1 | Engine errors | `engine.err.log` tail | No (local file) |
| 2 | Sentry errors | `us.sentry.io/api/0/.../issues` | Yes — `SENTRY_PAT` |
| 3 | Supabase advisors | `api.supabase.com/v1/.../advisors/{security,performance}` | Yes — `PEBBLE_SUPABASE_PAT` |
| 4 | Code activity | `git log`, `git status`, `git rev-list ahead` | No (local git) |
| 5 | Build activity | `output/<slug>/build_meta.json` walk | No (local files) |
| 6 | User engagement | `output/.engagement/<uid>.jsonl` walk | No (local files) |
| 7 | Subscriptions | `output/.users/<uid>/subscription.json` walk | No (local files) |

The PAT-gated sections gracefully no-op when the env var is missing —
the section appears with `_skipped — <VAR> not set in .env_` and exact
instructions for generating the token. No silent failure.

### Severity rollup

Each section gets a severity: `ok` / `info` / `warn` / `critical`. The
brief header shows the worst-case rollup so a glance at the title bar
tells Marc whether to read carefully or skim.

- 🟢 **ok** — no signal worth attention
- 🔵 **info** — informational only (build count, engagement, subscriptions)
- 🟡 **warn** — needs attention soon (uncommitted work, advisor warnings, recurring errors)
- 🔴 **critical** — needs attention NOW (user-affecting errors, security findings at ERROR level)

## What v2 adds (next iteration)

| Feature | Why | Effort |
|---|---|---|
| **Snapshot diffing** | "3 NEW Supabase findings since yesterday" beats "2 findings total" — diff against previous run | ~1h |
| **Engine.err.log timestamping** | Honest per-line time filtering instead of "last 5MB" heuristic | ~2h (engine-side change) |
| **HTTP probes for external deps** | Stripe webhook last-delivery, Supabase auth uptime — surface degradations | ~1h |
| **Top users by spend / activity** | Once paying customers exist, "who's making us money this week" is the morning question | ~30min |
| **Scheduled delivery via Hermes** | Telegram push at 8am every weekday | ~30min (already have Hermes wired) |

## What v3 dreams of

- **LLM prose pass** — pipe the structured brief through Claude API to turn bullets into natural-language paragraphs. Use prompt caching so it's cheap.
- **Auto-PR for clear-cut patterns** — "5 errors all stem from `parse_iso` returning None for empty strings. Draft PR at `<branch>`. Merge?"
- **Cross-source correlation** — "v3 build deploy at 14:32, error spike on /workspace at 14:35 — likely cause: deploy `<sha>`"
- **Customer-impact rollup** — "47 visitors hit the contact form yesterday, 3 form submissions failed. Affected users: <list>"

## Delivery channel options

Once the brief is generated, where does it go?

| Channel | Pros | Cons | When to use |
|---|---|---|---|
| File at repo root (`MORNING_BRIEF.md`) | Persisted, version-controlled with the day | You have to remember to look | Solo dev, low frequency |
| Hermes → Telegram | Pushed, scannable on phone | Truncates long content | When daily reads matter |
| Email via Resend | Rich formatting, archived in inbox | More friction to set up | Team scaling phase |
| Slack webhook | Same as Telegram + threading | Need a Slack workspace | If team uses Slack |

v1 just writes to a file. Wiring delivery is a v2 task.

## Scheduling options

Three ways to run on a schedule:

1. **Hermes cron** — `~/.hermes/jobs.yml` entry pointing at `python -m pebble.morning_brief`. Marc already has Hermes set up.
2. **scheduled-tasks MCP** — uses Claude Code's own scheduler. Could even pipe through Claude for prose summarization in the same step.
3. **OS-level cron / Task Scheduler** — boring, reliable, no extra deps.

Recommendation: **Hermes**, because Marc already trusts it and uses it for Telegram, so the brief→Telegram flow becomes a one-step wire.

## Token generation steps

### SENTRY_PAT
1. Open https://pebble-6q.sentry.io/settings/account/api/auth-tokens/
2. Click **"Create New Token"**
3. Name: `morning-brief`
4. Scopes (READ ONLY): `org:read`, `project:read`, `event:read`
5. Generate, copy
6. Add to `.env` (base repo): `SENTRY_PAT=<value>`

### PEBBLE_SUPABASE_PAT
1. Open https://supabase.com/dashboard/account/tokens
2. Click **"Generate new token"**
3. Name: `pebble-morning-brief`
4. (No scope picker — PATs are account-scoped)
5. Generate, copy
6. Add to `.env` (base repo): `PEBBLE_SUPABASE_PAT=<value>`

Both PATs can be revoked at any time from the same pages.

## File layout

```
pebble/morning_brief.py            # the module
docs/MORNING_BRIEF.md              # this doc
MORNING_BRIEF_SAMPLE_2026-05-23.md # today's sample at repo root
```

Sample brief is committed once as a reference. Future briefs aren't
committed — they'd be regenerated on demand or by the scheduler.

## Why "morning brief" not "incident report"

This intentionally isn't an incident response tool. Sentry alerts +
PagerDuty cover the "wake up at 3am" path. The morning brief is the
"with coffee at 8am" path — context to help start the day informed,
not to interrupt sleep.
