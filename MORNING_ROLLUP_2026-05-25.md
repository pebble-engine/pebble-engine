# Morning Rollup — 2026-05-25

> Compiled at end of session before Marc went to bed. **38+ commits pushed to both remotes** (`pebble-engine/pebble-engine` + `squitopest/pebble-engine`). Vercel + Railway rebuilds triggered with each push.

## TL;DR

- Trust-account-surface hardening fully shipped (Phase A + B + D — auth, MFA, sessions, audit log, GDPR export, billing safety)
- 5 new Qwen-sourced templates ported to the gallery (28 → 33 base templates; color variants in flight overnight)
- 36 Next.js console warnings fixed at source
- HIBP leaked-password check shipped (replaces $25/mo Supabase Pro feature for free)
- 3 critical webhook/export bugs fixed
- Sentry test-noise silenced + 3 stale issues marked resolved
- Migrations 007 (RLS perf + waitlist tighten) and 008 (sessions view) applied
- Migration 006 (pending_state) applied; HIBP + MFA + sessions all functional in prod

---

## 1. Action items for you (only these — everything else is done)

### Critical (none)
Nothing blocking.

### Important
- **Rotate the leaked PAT** `ghp_NvG…` at github.com → Settings → Developer settings → Personal access tokens. After regen: `git remote set-url squitopest https://squitopest:<new>@github.com/squitopest/pebble-engine.git`. The token has appeared in this transcript 4+ times tonight.

### Nice-to-have
- **NLM auth expired** — when you next have NotebookLM work, run `nlm login` in your terminal. The MCP auto-detects new credentials. I skipped tonight's adversarial review because of this.
- **Verify the leaked-password protection toggle stayed off** — it's a Supabase Pro feature so the toggle errors when flipped on Free. We replaced it with the HIBP module — same protection, $0/mo. Worth confirming the toggle UI didn't get stuck in a weird half-state.

---

## 2. What shipped — grouped by surface

### Trust + account lifecycle (security floor)

**Phase A** (ship-before-revenue):
- `0094f5f` `22eab05` MFA TOTP enrollment + verification + re-auth-gated disable
- `e2d760c` `0aeb275` Global sign-out (`POST /api/account/global-signout` + button + Supabase signOut scope=global + audit event + email notify)
- `7438475` `7189bc9` Active sessions list (read via new SECURITY DEFINER Postgres funcs in `public.list_user_sessions` + `public.revoke_user_session`)
- `5740371` HIBP leaked-password check on change-password (k-anonymity, fail-OPEN on outage)
- `d75e93d` Export-download Bearer JWT match (no more 24h re-download leak)
- `f9ccd1d` Hard-kill date 2026-05-29 for legacy file-fallback in pending-state lookups
- `64a19f7` Webhook dedupe across user re-subscription (stripe_subscription_id check)
- `345ca6f` Webhook plan metadata whitelist (no silent "enterprise" promotion via stale checkout)
- `3346488` `_safe_uid` wrap on `_exports_dir` + emit `account_delete_executed` audit event
- `002ddc9` `log.warning` on corrupted pending_deletion JSON (no more silent re-arm)

**Phase B** (settings restructure):
- `cbe5c94` `/settings?tab=<id>` deep-linking (Stripe-email links, support replies, internal docs all jump straight to the right tab)
- `374a490` `deletionScheduled` hydrate on mount (the "Cancel deletion" banner now persists across page loads — it was invisible before)
- `5a0e898` Snapshot IDs humanized in history drawer ("2 hours ago · 3 files changed" + raw-ID tooltip)
- `cf0c1b4` Always-visible Help + Contact-support footer in settings
- `7e04e56` Billing-portal Manage button always-visible (disabled tooltip when no sub)
- `ee87c6e` ActivityFeed inline Restore button on dashboard rows
- `46c1e0f` First-visit welcome card on dashboard (3 quick-start CTAs, localStorage-dismissed)
- `b6b92aa` `9ce5c06` Cancel-deletion warning when Stripe sub was lost (loud warning + Resume Pro CTA)

### Billing safety
- `23cab94` Explicit 503 when STRIPE_SECRET_KEY unset + redact exception PII
- `8482954` Pin `stripe>=8.0,<16.0` (SDK-15 compat workarounds documented in code)

### Templates gallery (Qwen 3.6 batch)
- `e93a346` `aura_luxury` — luxury cleaning (temp12, already Next.js)
- `953a986` `ase_garage` — auto repair w/ before-after slider (temp15)
- `ed5751e` `editorial_wedding` — wedding photography sticky horizontal story (temp14)
- `b4a6b30` `seasonal_kitchen` — restaurant, 5-page editorial (temp11, multi-page)
- `5e1a60e` `bright_dental` — dental, 4-page friendly modern (temp13)
- `1c2aba2` Preview screenshots for all 5 + screenshot-script fix for external Unsplash URLs
- Color variants for all 5 are in flight via overnight subagent; check final git log

### Landing page fixes
- `c72e8e9` Killed 36 duplicate-key React warnings + `/mp_.mp4` 404 (two duplicate TEMPLATE_TILES entries under stale `// Honest garage` comment)
- `c9902c4` `45c8128` Brought `/mp_.mp4` + the §2 video back (you wanted it after I removed it; restored from `c0663e0^`)
- `7ee4d55` Two-step confirm on custom-domain Remove button (one click was silently killing live URLs)
- `b959f47` 5s toast-undo on project delete (Gmail-style — optimistic remove, click Undo to cancel)

### Migration / SQL
- `007_security_perf_quick_fixes.sql` — applied (waitlist email-shape check + audit_log RLS init-plan)
- `006_pending_state.sql` — applied (email_change_pending + data_export_manifests tables)
- `008_user_sessions_view.sql` — applied (SECURITY DEFINER funcs that bypass auth.* RLS for engine reads)
- `2f98d6d` Trimmed audit_log event vocab + struck setup_call from CLAUDE.md + PROJECT_PLAN.md

### Tooling
- `b19afec` Pop `SENTRY_DSN` in `tests/conftest.py` — tests no longer fire real events to prod Sentry
- `5740371` New module `pebble/password_security.py` (HIBP k-anonymity check, 7 tests)

---

## 3. Test status

**Last full run was clean for everything tonight shipped.** Pre-existing failures (~14) live in `tests/test_brand_extract_endpoint.py` (9) + `tests/test_repair*.py` (5). Confirmed by isolating those files; they reproduce on commits from before this session. **None of tonight's commits introduced new failures.**

- 42 account-suite tests pass
- 22 Phase D tests pass (D.1 MFA + D.2 sessions + D.3 global sign-out)
- 7 HIBP tests pass
- 23 stripe_webhook tests pass

Pytest re-run was kicked off at session end; check `MORNING_TEST_RESULTS.md` if present (or the agent transcript) for the final numbers.

---

## 4. Sentry status (after tonight's triage)

Resolved with comments explaining the fix:
- **PYTHON-G** "scheduled deletion failed: boom" — test noise (`AdminError("boom")` from monkeypatch). Root cause `SENTRY_DSN` leaked to test env; conftest fix in `b19afec`.
- **PYTHON-F** HTTPError 400 in pending_state — missing 006 tables; you applied them.
- **PYTHON-E** create_email_change_pending getaddrinfo — same dual root cause as F+G.

Left unresolved (intentional — let Sentry's regression detection prove they're really fixed):
- **PYTHON-B/C/D** — Hydration errors on `/dashboard`. Probably fixed by `374a490` + `c72e8e9` but I can't verify without a real browser. If they re-fire, Sentry'll mark as regression.

---

## 5. Deferred (real architectural items, not skipped lightly)

- **Multi-instance rate limiters** — `_password_change_limiter` + `_data_export_limiter` + `_email_change_request_limiter` are all in-process. Cap weakens proportionally at scale. Needs shared Redis-style store. Tied to **Phase 44b** (managed invisible hosting) plan at [docs/superpowers/plans/2026-05-25-managed-invisible-hosting.md](docs/superpowers/plans/2026-05-25-managed-invisible-hosting.md).
- **ZIP-file storage for data export** — manifest lives in Supabase now (✓), but the actual ZIP file is still on local disk under `output/.exports/<uid>/`. Single-instance limitation, documented in `_build_export_zip` docstring. S3/R2 migration is its own phase.
- **Stripe `subscription.delete()` → `cancel_at_period_end`** — NLM flagged; you deferred. Search account.py for the call site when you revisit billing UX.
- **Signup-side HIBP check** — Today HIBP only enforces on password CHANGE. Signup goes through Supabase Auth directly in v3 (bypassing the engine), so a new account CAN be created with a leaked password. Closing this requires either Supabase Auth Hooks (beta) or routing signup through the engine.
- **`setup_call` ($99 calendar)** — Struck from active docs tonight. PROJECT_PLAN.md 9.7 is now `[ ]` with the implementation sketch preserved for when you decide to build it.
- **Notification system** — `events` + `notification_reads` tables exist with stale 1-row seed data. Bell uses localStorage. Decision deferred (no UX wins from killing OR wiring right now).

---

## 6. Open strategic decisions when you wake up

1. **Which big phase next?** Three plans on disk, all written, none started:
   - [Phase 44b — managed invisible hosting](docs/superpowers/plans/2026-05-25-managed-invisible-hosting.md) (NLM's #1 strategic finding, ~3-5 days)
   - [Phase D — MFA + sessions](docs/superpowers/plans/2026-05-25-mfa-sessions-list.md) — **DONE tonight, can archive**
   - [Trust + account surface](docs/superpowers/plans/2026-05-24-trust-account-surface.md) — **DONE tonight, can archive**
   - Phase 27 (Cloud sandbox preview), Phase 28 (Hybrid model routing), Phase 30 (Cinematic-first DNA rebrand) are pending in the task list
2. **Marketing push?** Trust surface is now mature enough to start onboarding real customers. The 14-day account-delete cooling-off, MFA, audit log, sessions list, HIBP — all the things small-business owners associate with "this is a real company" are live.
3. **Designer marketplace?** Originally Phase C of the trust plan; NLM said "stick to manual curating for now." Worth revisiting after first 3-5 paying customers — they'll surface what's missing.

---

## 7. Recipe reference (for future agents)

Tonight's session demonstrated several patterns worth preserving for future sessions:

- **Parallel subagents** are productive when scoped to non-overlapping file trees. Backend agent + frontend agent + template-port agent + Phase D agent + color-variants agent all ran simultaneously without overlap.
- **Git race conditions** happen when two agents commit to the same branch in the same worktree. The frontend polish agent had its Fix 3 commit silently consumed by a parallel commit; the recovery was to re-commit. Future mitigation: serialize commits or use isolation worktrees.
- **Mid-stream config races** also happen (e.g., my `c72e8e9` removed the video, then you wanted it back; recovery was `git checkout c0663e0^ -- <file>` to restore from history). Worth documenting in CLAUDE.md if it recurs.
- **Sentry-in-test silencing** is a one-line fix at `tests/conftest.py` module level (`os.environ.pop("SENTRY_DSN", None)`). Add to any new pytest project that uses Sentry.

Sleep well. Everything that matters is pushed.
