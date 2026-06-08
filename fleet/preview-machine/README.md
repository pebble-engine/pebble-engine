# Pebble preview-machine (Fly Machines fleet)

One shared Docker image, cloned into a Fly Machine per active preview. Each
machine runs `next dev` + a tiny receiver that the engine pushes source files
to; Hot Module Replacement repaints the workspace iframe in <0.5s. Deps are
baked into the image, so machines boot with **no npm install**.

See `docs/superpowers/specs/2026-06-08-container-preview-fleet-design.md`.

## One-time setup (Marc, with a Fly account)

1. Install flyctl + log in: `fly auth login`.
2. Create the fleet app (hosts all preview machines):
   ```
   fly apps create pebble-preview-fleet --org <your-org>
   ```
3. Build + push the image from this directory:
   ```
   cd fleet/preview-machine
   fly deploy --app pebble-preview-fleet --dockerfile Dockerfile --image-label pebble-preview --build-only --push
   ```
   Note the pushed image ref (e.g. `registry.fly.io/pebble-preview-fleet:pebble-preview`).
4. Put these in the engine's `.env`:
   ```
   FLY_API_TOKEN=<fly auth token>      # `fly auth token`
   FLY_APP=pebble-preview-fleet
   FLY_PREVIEW_IMAGE=registry.fly.io/pebble-preview-fleet:pebble-preview
   PEBBLE_FLEET_SECRET=<random 32+ char string>   # engine <-> receiver auth
   PEBBLE_PREVIEW_BACKEND=fly-fleet
   ```
5. (Routing) The engine creates one machine per slug in this app. Per-machine
   public reachability is the item to confirm live — either:
   - app-per-slug (`pebble-preview-<slug>.fly.dev`, matches the legacy
     `pebble.fly_preview` scaffold), or
   - one app + the engine proxies to a specific machine via the
     `fly-force-instance-id` header.
   Decide during live verification (needs the Fly token). The engine code
   (`pebble/fly_fleet.py`) isolates this in `machine_public_url()`.

## How it runs
- Engine: `ensure_machine(slug)` → start a machine from the image →
  `sync_files(slug, source)` (POST `/__pebble/sync`, `x-pebble-secret`) →
  poll `/__pebble/healthz` → hand the public URL to the workspace iframe.
- Edit/refine: engine syncs only changed files → next dev HMR.
- Idle: the reaper stops machines unused > `PEBBLE_FLEET_IDLE_MIN` (default 15).

## Security
- Fly Machines are micro-VMs → untrusted generated code is isolated per user.
- `/__pebble/*` requires `PEBBLE_FLEET_SECRET`.
- No real secrets in the machine (the contact form no-ops without
  `RESEND_API_KEY` — correct for a preview).
