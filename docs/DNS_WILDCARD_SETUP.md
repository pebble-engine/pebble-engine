# Wildcard DNS for instant publish (`*.pebbleapp.ai`)

Instant publish (`POST /api/publish/instant`) serves live sites at:

`https://<subdomain>.pebbleapp.ai/`

Code: `pebble/server/publish_instant.py`

## Marc — Cloudflare (recommended)

1. **Cloudflare** → DNS for `pebbleapp.ai`
2. Add record:
   - **Type:** `CNAME`
   - **Name:** `*` (wildcard)
   - **Target:** Railway public hostname, e.g. `web-production-e5cb0.up.railway.app`
   - **Proxy:** DNS only (grey cloud) unless you want Cloudflare in front of Railway
3. Railway → service **web** → Settings → **Custom Domain** → add `*.pebbleapp.ai` if Railway requires it

## Engine env

```env
PEBBLE_PUBLIC_DOMAIN=pebbleapp.ai
PEBBLE_PUBLIC_SCHEME=https
```

## Verify

1. Publish a test slug via workspace publish phase
2. Open `https://<subdomain>.pebbleapp.ai/` on phone (same WiFi not required — public URL)
3. Confirm **no** visual-edit bridge on public subdomain (owner uses `/preview/<slug>/` in workspace)

## Optional: Cloudflare Pages full deploy

Separate from instant publish — `POST /api/publish` uploads to Cloudflare Pages for custom domains.

Requires `CLOUDFLARE_ACCOUNT_ID` + `CLOUDFLARE_API_TOKEN` in Railway `.env`.
