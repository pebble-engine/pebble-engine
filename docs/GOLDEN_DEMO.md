# Golden investor demo (5 minutes)

Rehearse this path. Keep a **backup slug** built ahead of time.

## Backup slug (pre-build before demo)

```bash
# Local or prod — build once, star it, never delete
# Suggested slug: demo-dental-austin
```

Prompt to paste if live build needed:

> Modern dental office in Austin — family-friendly, accepts new patients, online booking CTA, trust-focused copy.

## Live script

| Min | Show | Talk track |
|-----|------|------------|
| 0:00 | Landing → type prompt → Sign up | "Non-technical owner describes their business in one sentence." |
| 0:45 | Workspace build SSE stream | "Watch it write a real Next.js site — not a mockup." |
| 2:00 | Design phase — click hero headline, change color | "Canva-style editing — no code." |
| 2:30 | Mention DNA card + eval count | "38 automated quality checks reject AI slop by default." |
| 3:00 | Publish → `slug.pebbleapp.ai` | "One click — live URL." |
| 3:30 | `/community` feed | "Builders see each other's launches — we're not solo like Lovable." |
| 4:00 | Backup | If WiFi/LLM fails: open pre-built `/workspace/demo-dental-austin` |

## If live build fails

1. Open dashboard → starred backup project
2. Say: "I'll show you one we shipped yesterday" (true if you built it earlier)
3. Still demo click-to-edit + publish on backup

## Pre-demo checklist (Marc, 10 min before)

```bash
python scripts/prod_smoke.py
```

- [ ] `/api/health` 200 on pebbleapp.ai
- [ ] Logged-in test account works
- [ ] Backup slug preview loads
- [ ] Phone on LTE can open published URL (DNS wildcard)
