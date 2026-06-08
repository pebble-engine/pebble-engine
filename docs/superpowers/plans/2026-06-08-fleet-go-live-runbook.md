# Container preview fleet — build status + go-live runbook

Companion to `docs/superpowers/specs/2026-06-08-container-preview-fleet-design.md`.
Built autonomously on branch `claude/prod-preview-fixes`. **Nothing deployed.**

## ✅ Built + tested (no Fly access needed)

| Piece | File | Tests |
|---|---|---|
| Machine image (deps pre-baked) | `fleet/preview-machine/Dockerfile`, `package.json` | — |
| In-container receiver (sync + HMR-WS passthrough + bridge injection) | `fleet/preview-machine/receiver.mjs` | `node --check` ✓ |
| Fly Machines client (create/start/stop/destroy, registry, ensure, sync, reap, cap) | `pebble/fly_fleet.py` | `tests/test_fly_fleet.py` (8) |
| Engine glue (kick_preview, preview-url endpoint, source+bridge collection) | `pebble/server/fleet_preview.py` | `tests/test_fleet_preview.py` (5) |
| Triggers after build + refine (flag-gated, integrity-gated) | `build.py`, `refine.py` | covered |
| `GET /api/projects/<slug>/preview-url` route | `router.py` | covered |

All behind `PEBBLE_PREVIEW_BACKEND=fly-fleet` (default off → safe no-op). Full suite: 2640 pass / same 25 pre-existing network failures.

## ⏳ Remaining (needs Marc's Fly token / live)

1. **Fly setup** — `fleet/preview-machine/README.md`: create the app, push the image, set `.env` (`FLY_API_TOKEN`, `FLY_APP`, `FLY_PREVIEW_IMAGE`, `PEBBLE_FLEET_SECRET`).
2. **Resolve per-machine public routing** — the one live-validation item. `fly_fleet.machine_public_url()` currently returns the app domain (only correct with 1 machine). Decide:
   - **app-per-slug** (`pebble-preview-<slug>.fly.dev`) — clean per-slug URLs, matches the legacy scaffold; change `create_machine`/`machine_public_url` to create an app per slug, or
   - **one app + `fly-force-instance-id`** header (engine would proxy — reintroduces the websocket-proxy problem; avoid).
   → Recommend app-per-slug. ~1 focused change in `fly_fleet.py` once we can test a boot.
3. **Idle reaper loop** — call `fly_fleet.reap_idle()` on a timer (a daemon thread in `pebble_engine.serve`, every ~5 min). ~10 lines; add during live verify.
4. **v3 frontend** — workspace polls `GET /api/projects/<slug>/preview-url`; show "Building your preview…" until `ready`, then iframe `url`. Click-to-edit bridge already arrives via cross-origin `postMessage`. Best built once a real machine URL exists to test against.

## Live verification checklist (with the Fly token)
- [ ] `fly apps create` + `fly deploy` the image; set `.env`.
- [ ] `PEBBLE_PREVIEW_BACKEND=fly-fleet python -c "from pebble.fly_fleet import ensure_machine, sync_files, wait_ready; ..."` on a real slug → machine boots, source syncs, `/__pebble/healthz` ready.
- [ ] Open the machine URL → site renders (SSR, real images, contact form present).
- [ ] Edit a file → `sync_files` delta → confirm HMR repaint <0.5s.
- [ ] Confirm the visual-edit bridge injected (click-to-edit posts to parent).
- [ ] Resolve routing (#2) + add reaper (#3) + build the v3 state (#4).
- [ ] Decide rollout: keep `fly-fleet` for the beta; measure cost.

## Notes
- Publish is still separate (Cloudflare Direct Upload exists; user-owned-Vercel OAuth is the on-brand option) — out of scope here.
- The earlier Vercel-Deployments preview code stays on the branch but is superseded by this for preview (NLM: Vercel-per-preview doesn't scale / ToS).
