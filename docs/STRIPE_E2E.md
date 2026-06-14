# Stripe E2E — test mode checklist

## One-time bootstrap

```bash
# .env must have STRIPE_SECRET_KEY=sk_test_...
python -m pebble.stripe_bootstrap
```

Copy printed `PEBBLE_STRIPE_*_PRICE_ID` values into `.env` (local) and Railway (prod).

## Webhook (local dev)

Terminal 1 — engine:

```bash
python pebble_engine.py
```

Terminal 2 — Stripe CLI:

```bash
stripe listen --forward-to http://127.0.0.1:8000/api/internal/stripe-webhook
```

Paste `whsec_...` into `STRIPE_WEBHOOK_SECRET` in `.env`. Restart engine.

## Webhook (production)

1. Stripe Dashboard → Developers → Webhooks → Add endpoint
2. URL: `https://web-production-e5cb0.up.railway.app/api/internal/stripe-webhook`
3. Events: `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`
4. Copy signing secret → Railway `STRIPE_WEBHOOK_SECRET`

## One real payment test

1. Sign in at https://www.pebbleapp.ai
2. Settings → Billing → Upgrade to Starter (test card `4242 4242 4242 4242`)
3. Confirm webhook fires (Stripe CLI or Dashboard → Webhooks → event log)
4. Verify `output/.users/<uid>/subscription.json` on engine (or Settings shows active plan)

## Automated env check

```bash
python scripts/verify_stripe_setup.py
```

Does **not** charge a card — only checks env vars are present and Stripe API responds.
