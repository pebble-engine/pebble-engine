# Railway persistent volume for `output/`

**Why:** Pebble stores every customer project under `output/<slug>/` on the engine filesystem ([`pebble_engine.py`](../pebble_engine.py) `OUTPUT_DIR`). Railway’s default container disk is **ephemeral** — each redeploy can wipe all projects. Beta is not safe until `output/` is on a persistent volume.

## Marc — one-time setup (~30 min)

1. Open [Railway](https://railway.app) → project **magnificent-simplicity** → service **web**
2. **Volumes** → **Add volume**
   - **Mount path:** `/app/output` (Railway’s default working dir for this repo is `/app`)
   - **Size:** start with 5–10 GB for beta
3. **Redeploy** the service after attaching the volume
4. Confirm the mount:

```bash
python scripts/verify_railway_volume.py
```

Expect `output_writable: true` and `output_persists_hint: true` after you run the script twice across a redeploy (see script help).

If the mount path is wrong (projects still vanish), check Railway deploy logs for `WORKDIR` / startup cwd and remount at `<cwd>/output`.

## What lives on the volume

| Path | Purpose |
|------|---------|
| `output/<slug>/site/` | Generated Next.js source |
| `output/<slug>/brief.json` | Project brief |
| `output/<slug>/.vercel-preview.json` | Vercel preview URL + bypass secret |
| `output/<slug>/published.json` | Instant publish sentinel |
| `output/.users/` | Subscription + credits metadata |

## Verify after beta invite

1. Build a test project on pebbleapp.ai
2. Trigger a Railway redeploy (empty commit or manual redeploy)
3. Open the same project — preview and publish must still work

## Rollback

Detach the volume in Railway (data on the volume is retained but unmounted). Do **not** do this during beta without migrating data.
