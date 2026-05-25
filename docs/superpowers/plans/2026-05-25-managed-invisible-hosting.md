# Phase 44b — Managed Invisible Hosting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `<slug>.pebbleapp.ai` the default destination for every customer's generated site so Pebble's API keys (Resend, Stripe price IDs, Pexels, etc.) never leave Pebble's servers. Customer downloads + custom-domain hosting become opt-in upgrades that include a "your own keys" provisioning flow.

**Why this matters now (NLM finding from 2026-05-24 critique):** Pebble currently injects its own API keys into customer-bound `.env.example` files. A motivated customer can read the env, copy our Stripe `sk_test_` / Anthropic `sk-ant-` / Resend `re_` keys, and reuse them against their own product → we eat the bill. With even 50 paying customers this becomes a multi-thousand-dollar leak per month. The fix is architectural, not policy.

**Tech Stack:** Cloudflare Pages or Railway for subdomain hosting (Phase 44 already deployed the routing via wildcard DNS + `pebbleapp.ai` proxy), Cloudflare Workers for server-side key injection, Stripe Express Connect for designer payouts (deferred until C-phase), existing `output/<slug>/site/` build artifact as input.

**Architectural shift:**

| Today (broken) | Phase 44b (target) |
|---|---|
| Customer's site = Next.js bundle deployed to their own infra | Customer's site = static build served from Pebble's edge |
| `.env.example` has Pebble's real keys as placeholders | `.env.example` has empty placeholders; runtime keys injected by Pebble's edge router |
| Form submissions hit customer's Resend account | Form submissions hit Pebble's `/api/forms/<slug>` (already exists from Phase 36) — we relay to customer-provided forward address |
| Stripe checkout uses customer's keys (or doesn't work) | Stripe checkout uses Pebble's keys + a per-customer payout via Express Connect |
| Custom domain = customer adds CNAME to their Vercel | Custom domain = Pebble's edge proxies their domain to our subdomain (already Phase 44 work) |
| Download as ZIP = customer gets working site WITH our keys | Download as ZIP = customer gets working site WITH empty `.env.example` + "here's how to provision your own keys" guide |

---

## File Structure

| Path | Purpose |
|---|---|
| `pebble/server/edge_key_injection.py` | **Create.** Per-slug runtime key map — maps slug → which Pebble keys to inject (e.g. `slug:bakery-co.kr` → `{RESEND_API_KEY: <ours>, CONTACT_TO_EMAIL: <customer's forward>}`) |
| `pebble/server/customer_keys.py` | **Create.** Customer "provision your own keys" flow. Stores customer-provided keys encrypted at rest, swaps Pebble's keys for the customer's at request time |
| `pebble/server/publish.py` | Modify. Default publish target = managed hosting (subdomain). Add explicit upgrade flow for custom domain / ZIP download. |
| `pebble/server/forms.py` | Modify. Always relay through Pebble (already does this — verify after audit). |
| `pebble/postbuild.py` | Modify. Strip Pebble's real keys from the customer's `.env.example` before any download/publish — replace with empty placeholders + a comment block explaining how to fill them. |
| `ui/v3/components/phases/publish-phase.tsx` | Modify. Default flow = "we'll publish to bakery-co.pebbleapp.ai for free, instantly". Custom domain + download = secondary CTAs requiring upgrade. |
| `ui/v3/components/dialogs/provision-keys.tsx` | **Create.** Modal that walks customer through providing their own Stripe / Resend / Pexels keys when they upgrade to custom domain or download. |
| `supabase/migrations/006_customer_keys.sql` | **Create.** `public.customer_keys` table — encrypted per-slug key storage. |
| `tests/test_edge_key_injection.py` | **Create.** Verify that subdomain serves include keys, ZIP downloads don't. |
| `tests/test_customer_keys.py` | **Create.** Encryption + decryption + rotation. |

---

## Phase 44b.1 — Audit: which Pebble keys leak into customer projects today

**Goal:** Catalog every Pebble-owned secret currently injected into customer-bound files. Without this list we can't fix it.

- [ ] **Step 1.1: Grep customer-bound files for Pebble-owned secret patterns**

Run from repo root:
```bash
for slug in $(ls output/ 2>/dev/null | head -20); do
  echo "=== $slug ==="
  if [ -d "output/$slug/site" ]; then
    grep -rE 'sk_test_|sk_live_|sk-ant-|re_|whsec_|PEBBLE_PEXELS_API_KEY|RESEND_API_KEY|STRIPE_SECRET|ANTHROPIC_API_KEY' "output/$slug/site" 2>/dev/null | grep -v node_modules | head -10
  fi
done
```

- [ ] **Step 1.2: Audit `pebble/postbuild.py` + `pebble/server/publish.py` for which keys get written**

Find every place these modules write to `.env`, `.env.example`, `.env.local`, or `config.json` in customer-bound directories.

- [ ] **Step 1.3: Write the catalog**

Create `docs/architecture/customer-key-leakage-audit.md` with:
- Each leaked key (name + prefix)
- Where it gets written (file + line)
- What customer feature requires it
- Whether the customer NEEDS to know about it (form-relay-only keys can stay server-side; Stripe price IDs may need to be visible if customers do their own checkout)

- [ ] **Step 1.4: Commit audit + categorize**

Tag each leaked key in the audit doc:
- 🟢 **Remove entirely** (only Pebble's runtime needs it — e.g. Pexels for image search)
- 🟡 **Move to runtime injection** (customer's site uses it but only at request time — e.g. Resend for form submission can go through Pebble's `/api/forms/<slug>`)
- 🔴 **Required in customer copy** (customer must control it for their own product — e.g. their own Stripe account for payments)

---

## Phase 44b.2 — Server-side key injection at request time

**Goal:** For 🟡-category keys, eliminate them from customer's static bundle. Pebble's edge injects them at request time.

- [ ] **Step 2.1: `pebble/server/edge_key_injection.py` — per-slug key map**

```python
"""Maps slug → which keys to inject at request time.

Customer's static bundle contains NO secrets. When their site makes an
API call (form submit, payment intent, etc), the call hits Pebble's
edge first (/api/forms/<slug>, /api/checkout/<slug>) and we add the
right Pebble-owned secret + customer-specific routing before forwarding.

For customers on the FREE tier: Pebble's keys, Pebble takes platform
fee from form notifications / checkout.
For Pro / Pro+ tier: customer's keys can be substituted via
customer_keys.py — they keep 100% of revenue, eat their own API costs.
"""
from __future__ import annotations
import os
from typing import Optional

from pebble.server.customer_keys import get_customer_key, KeyKind


def resolve_resend_key(slug: str) -> Optional[str]:
    """Customer's own Resend key if provisioned, else Pebble's shared key."""
    return get_customer_key(slug, KeyKind.RESEND) or os.environ.get("PEBBLE_DEFAULT_RESEND_KEY")


def resolve_stripe_secret(slug: str) -> Optional[str]:
    """Customer's own Stripe key if provisioned (Pro+ only), else None.
    Free tier doesn't get Stripe checkout — they must upgrade for payments."""
    return get_customer_key(slug, KeyKind.STRIPE_SECRET)


# ... etc for each 🟡 / 🔴 key category from the audit
```

- [ ] **Step 2.2: Refactor `pebble/server/forms.py` to use the injection layer**

Existing `run_forms_submit(handler)` already lives in `pebble/server/forms.py` (Phase 36 work). Verify it doesn't pass customer-bound `RESEND_API_KEY` through — instead, it should call `resolve_resend_key(slug)` and use Pebble's shared key on Free tier.

- [ ] **Step 2.3: Engine-side proxy for any non-relayed call**

If a customer site needs a Pebble-owned API (e.g. weather data, Pexels search), the call goes through a `/api/edge-proxy/<slug>/<target>` endpoint. The target is on an allowlist; the proxy adds the secret server-side and returns the response. Generated site code calls `/api/edge-proxy/...` instead of the third-party API directly.

- [ ] **Step 2.4: Tests + commit**

Test: a fresh `output/<slug>/site/` directory contains ZERO Pebble-secret-pattern strings (sk_test_, re_, sk-ant-, etc.). Use the audit's grep pattern as a regression test.

---

## Phase 44b.3 — Default publish flow = managed hosting

**Goal:** When the customer hits "Publish", the default outcome is `<slug>.pebbleapp.ai` going live in seconds. Custom domain + ZIP become explicit upgrades.

- [ ] **Step 3.1: Modify `ui/v3/components/phases/publish-phase.tsx`**

Currently the publish phase offers all 3 paths flat. Restructure to:
- **Primary CTA: "Publish to bakery-co.pebbleapp.ai" — Free + instant + 1 click**
- Secondary: "Use your own domain" → opens upgrade flow (Pro plan + provision-keys modal)
- Secondary: "Download as ZIP" → opens upgrade flow (Pro+ plan + provision-keys modal + "your site won't work until you fill in your own keys" warning)

- [ ] **Step 3.2: Wire `provision-keys.tsx` modal**

A modal that:
- Lists the keys the customer needs to provide (from audit's 🔴 category)
- For each: link to where to get one (e.g. "Get a Stripe key at dashboard.stripe.com/test/apikeys"), paste input, "verify" button that test-pings the API
- Stores keys via `POST /api/customer-keys/<slug>` (encrypted server-side per `customer_keys.py`)

- [ ] **Step 3.3: Tests**

E2E test: free-tier customer hits Publish → site goes live at `<slug>.pebbleapp.ai` within 30 seconds without any key prompt.
Pro-tier customer chooses "Use your own domain" → modal opens → fills Stripe + Resend → DNS instructions shown.

- [ ] **Step 3.4: Commit + smoke-test in v3 + push**

---

## Phase 44b.4 — Customer keys storage (encrypted at rest)

**Goal:** Per-slug encrypted key vault so Pro customers can BYO keys.

- [ ] **Step 4.1: Supabase migration**

```sql
-- 006_customer_keys.sql
create table if not exists public.customer_keys (
  slug             text          primary key,
  user_id          uuid          not null references auth.users(id) on delete cascade,
  encrypted_blob   text          not null,  -- AES-256-GCM
  iv               text          not null,
  key_kinds        text[]        not null,  -- which kinds are stored: ['resend','stripe_secret',...]
  created_at       timestamptz   not null default now(),
  updated_at       timestamptz   not null default now()
);
alter table public.customer_keys enable row level security;
create policy "users see own keys metadata only"
  on public.customer_keys for select
  using (auth.uid() = user_id);
-- No INSERT/UPDATE policy for authenticated role — service role only writes via pebble.customer_keys
```

Marc applies via Dashboard (paste-ready SQL block in commit message).

- [ ] **Step 4.2: `pebble/server/customer_keys.py`**

```python
"""Per-slug encrypted key vault. AES-256-GCM with the encryption key in
PEBBLE_CUSTOMER_KEYS_MASTER (32-byte env var). Plaintext keys never
touch disk or logs; only encrypted blobs persist in Supabase.

Public:
  set_customer_keys(slug, user_id, {KeyKind.RESEND: '...', ...})
  get_customer_key(slug, KeyKind.STRIPE_SECRET) -> Optional[str]
  delete_customer_keys(slug)  # on account delete / domain disconnect
"""
# Full implementation TBD; ~150 lines
```

- [ ] **Step 4.3: Rotation flow**

When a Pro customer downgrades to Free OR disconnects their custom domain, automatically wipe their customer_keys row. Audit-log the event (`customer_keys_revoked` with reason).

---

## Phase 44b.5 — Download-as-ZIP without leaking Pebble's keys

**Goal:** Customer can still self-host (Pro+ tier), but the ZIP they get contains empty placeholder envs + a clear how-to-fill-them guide. No Pebble keys.

- [ ] **Step 5.1: Modify `pebble/postbuild.py`**

Find where `.env.example` is written into `output/<slug>/site/`. Replace with a SANITIZED version: every key has an empty value + a comment explaining what it's for + a link to where to get one.

```
# Pebble customer-bound .env.example — fill in your own keys before deploying.
# Get a Resend key:    https://resend.com/api-keys
RESEND_API_KEY=
# Get a Stripe key:    https://dashboard.stripe.com/test/apikeys
STRIPE_SECRET_KEY=
# etc.
```

- [ ] **Step 5.2: ZIP generation: add a `SELF_HOST.md`**

Brief guide:
- "Your site won't work until you fill in `.env.example` (rename to `.env.local`) with your own keys."
- For each key: 1 paragraph explaining what it does + where to get one + what happens if it's missing.
- Link to Pebble's "Help me self-host" form (paid setup-call upsell — $99 one-time, already exists in Stripe).

- [ ] **Step 5.3: Regression test**

```python
def test_zip_export_contains_no_pebble_keys():
    """A self-host ZIP must NEVER ship a Pebble-owned secret."""
    slug = 'test-export'
    # Build a fake project with the customer site
    # Run the ZIP export
    # Unzip + grep for sk_test_, sk-ant-, re_, whsec_, etc.
    # Assert ZERO matches
```

---

## Out of scope (explicitly NOT in this plan)

- **Designer marketplace upload** — deferred per NLM until 20+ paying Pro customers.
- **MFA / TOTP / sessions list** — separate Phase D plan.
- **Stripe Express Connect for designer payouts** — separate plan when marketplace ships.
- **Multi-region edge deployment** — overkill at current scale; single Pebble edge suffices.

---

## Self-Review

**1. Spec coverage:**
- ✅ NLM's #1 strategic finding (key-leak cost-burn) addressed by Phase 44b.1 + 44b.2
- ✅ Managed hosting as default addressed by 44b.3
- ✅ Encrypted at-rest key vault for Pro tier (44b.4)
- ✅ Self-host download without leaking Pebble keys (44b.5)
- ⏸️ Per-customer Stripe Connect for taking payments → deferred (depends on marketplace design)

**2. Dependencies:**
- 44b.1 must ship first — without the audit, the other steps don't know what to protect
- 44b.4 (vault) and 44b.2 (injection) need each other — recommend pairing as 44b.2+4 combined work
- 44b.3 (publish UX) needs 44b.4 done first (UX walks user through provisioning)
- 44b.5 (ZIP) is independent — could ship before or after the other 4

**3. Risks:**
- Encryption key rotation is hard. If `PEBBLE_CUSTOMER_KEYS_MASTER` is rotated, all encrypted blobs become unreadable until re-encrypted with the new master. Plan must include a one-time re-key migration tool.
- A customer-keys leak via our own breach would be catastrophic (every customer's Stripe key compromised). The encryption-at-rest is necessary but not sufficient — we also need: HSM-backed master key (AWS KMS / Cloudflare Secret Store), strict access logging, eventual rotation policy.
- Performance: every customer-bound API call (form submit, etc.) now passes through Pebble's edge. At 10K customers each submitting 1 form/day, that's 10K calls/day = trivial. At 100K customers with 100 calls each, it's 10M/day — needs CDN-level caching for static paths and Workers for dynamic.

**4. Operational footprint:**
- New env var: `PEBBLE_CUSTOMER_KEYS_MASTER` (32 bytes, randomized once, never changes — or rotated with the migration tool from 44b.4)
- New env var: `PEBBLE_DEFAULT_RESEND_KEY` (Pebble's shared Resend key for free-tier form relays)
- New Supabase table: `public.customer_keys`
- New audit_log event types: `customer_keys_provisioned`, `customer_keys_revoked`, `key_injection_failed`

---

## Execution Handoff

Plan complete and saved. Two execution options:

**1. Subagent-Driven (recommended for this work)** — I dispatch a fresh subagent per phase (44b.1, 44b.2, etc.) with two-stage review (spec + code quality). Estimated 3-5 days of subagent wall-clock.

**2. Inline execution** — Bigger commits, checkpoints between phases. Slower but you see every command.

I'd recommend Phase 44b.1 (the audit) be done FIRST and independently, since its output dictates the rest. Then 44b.2+4 paired, then 44b.3, then 44b.5.
