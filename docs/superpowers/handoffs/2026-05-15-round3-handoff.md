# Round 3 Workspace Polish — Hand-off (2026-05-15)

This document hands round 3 of the premium-polish arc back to Marc. Three
themes shipped this round:

1. **Typography + density extension** — applied the round-2 type scale
   to the eight outside-workspace files (dashboard, admin, six
   standalone components).
2. **Micro-interactions module** — net-new `lib/interactions.ts`
   defining reusable hover/active/focus patterns (button, chip, card,
   iconButton, link, focusRing) and applied across the sixteen
   workspace + dashboard files. Universal focus rings + universal press
   states + universal `motion-reduce:` overrides.
3. **WCAG contrast fix for spark/earth tinted pills** — runnable audit
   script surfaced 29 failing pairs; the worst offenders (text-spark
   / text-earth as text content on tinted backgrounds, worst case
   2.19:1 vs 4.5 needed) are fixed via two new CSS vars
   (`--color-spark-deep`, `--color-earth-deep`). Border and dark-mode
   failures recorded as round-4 backlog.

All wiring tests + plain-Node verifiers pass. Pytest at **854 green**
on the latest commit (was 836 baseline → 844 after round 2 → 850 after
round 3 commits 1+2 → 854 after round 3 commit 3: +10 new structural
assertions across the three new wiring tests).

## TL;DR

```
4389aff v3: round 3 / commit 3 — contrast fix for spark/earth tinted pills
fd49f04 docs+tools: round 3 commit 3 spec + WCAG contrast audit script
462d3ed docs: round 3 hand-off — workspace polish overnight session
161196f v3: round 3 / commit 2 follow-up — review fixes
34cfb86 v3: round 3 / commit 2 — apply interactions to 15 workspace + dashboard files
11551fd v3: round 3 / commit 2 — interactions module
438a5a4 docs: spec for round 3 commit 2 — micro-interactions module
0636ac6 v3: round 3 / commit 1 follow-up — review fixes
b9051c0 v3: round 3 / commit 1 — apply type scale + density to 8 dashboard/standalone files
119e1b0 docs: spec for round 3 commit 1 — dashboard + standalone typography
```

Ten commits on top of round 2's tip (`fee4861`). ~600 lines net
change across 23 files (18 v3 + 1 new lib + 1 new plain-Node test + 3
new Python wiring tests + 2 wiring-test extensions + 3 specs + 1
audit script + 1 audit baseline output + 1 handoff).

## Commits in detail

### Commit 1 spec — `119e1b0` Dashboard + standalone typography spec

Companion spec to round 2's typography pass. Same module, same
heuristic, eight more files. Records per-file judgment calls
(serif-drop on structural data, leave-raw on form inputs and buttons,
ai-prompt-box minimal-import exception).

### Commit 1 — `b9051c0` Apply type scale + density to 8 dashboard/standalone files

~36 typography swaps + 12 density fixes; net +17 lines across:

- `app/dashboard/page.tsx`, `app/admin/page.tsx`
- `components/command-palette.tsx`, `components/dna-preview.tsx`,
  `components/language-picker.tsx`, `components/ui/ai-prompt-box.tsx`,
  `components/block-gallery.tsx`, `components/auth-menu.tsx`

Density rounding: `py-2.5` → `py-2`, `py-1.5` → `py-2`, `mt-0.5` →
`mt-1`. Buttons + form inputs kept raw (no role exists). Wiring test
extended `TYPE_CONSUMER_FILES` from 8 to 16 entries; pytest grew 836 →
844 (+8 parametrized cases).

Notable decisions:

- Cost-telemetry figure → `type.heading.m` (drops serif — structural
  data, not narrative).
- Project card titles → `type.heading.m` (same rationale).
- Empty-state headings → `type.display.m` (rare narrative moments in
  admin surfaces).
- Activity-feed file count → `type.mono` + `text-muted-foreground`
  (preserves code-y feel; 10px → 12px legibility bump).
- Admin H1 → `type.display.m` (one weight downgrade per the role;
  consistent with dashboard-level H1s).

### Commit 1 follow-up — `0636ac6` Review fixes

Four findings from a Sonnet review of commit b9051c0:

- **Dashboard `ProjectCard` business_type line:** subagent had applied
  `type.caption` to a `font-mono uppercase` line, stripping the mono
  styling. Switched to `type.mono + text-muted-foreground`.
- **Dashboard activity-feed business_name:** subagent had applied
  `type.heading.s` (text-base bump) to a list-row item title — out of
  spec for list rows. Reverted to raw `text-sm font-semibold`.
- **Auth-menu trigger button:** subagent rounded `py-1` (already on
  the 4px grid) → `py-2`, doubling the chip height. Reverted per the
  spec rule "py-1 is on grid; do not touch."
- **ai-prompt-box textarea:** `type.body.m` had been applied which
  adds `leading-relaxed` to a form-input baseline. Reverted; the
  `import { type }` stays per the spec's ai-prompt-box exception
  (wiring test asserts presence of the import, not breadth of use).

### Commit 2 spec — `438a5a4` Interactions module spec

Defines a reusable hover/active/focus pattern module with six roles
(button, chip, card, iconButton, link, focusRing). Lifts existing v3
patterns (`hover:opacity-90` on primary, `hover:bg-accent` on outline,
`whileHover y:-3` on cards) and adds the missing pieces: focus rings
universally, press states (`active:scale-[0.98]` on buttons, `scale-95`
on icon buttons), `motion-reduce:` overrides everywhere transform/scale
appears.

The framer-motion → CSS migration on cards is intentional: spring
physics gives way to ease-out tweens, fitting Pebble's "calm premium"
brand better than playful spring overshoot.

### Commit 2 — `11551fd` Interactions module

Net-new `ui/v3/lib/interactions.ts` + plain-Node verifier + Python
wiring test. Zero behavior change at this commit point. Six roles per
spec:

- `button` — 150ms transition-all + `hover:opacity-90` +
  `active:scale-[0.98]` + focus ring + motion-reduce.
- `chip` — 100ms transition-colors + `hover:bg-accent` +
  `active:bg-accent/80` + focus ring.
- `card` — 200ms transition-all + `hover:-translate-y-0.5` +
  `hover:shadow-md` + focus ring + motion-reduce.
- `iconButton` — 150ms transition-all + `hover:bg-accent` +
  `active:scale-95` + focus ring + motion-reduce.
- `link` — 100ms transition-colors + `hover:text-foreground` +
  focus underline.
- `focusRing` — standalone focus ring utility.

Wiring test pins structure (file exists, exports const, all six role
keys present, `motion-reduce:` appears in source). Pytest 844 → 848
(+4 structural assertions). The consumer-import parametrized assertion
was deliberately deferred to the apply commit so this commit stayed
green (Marc's "pytest green every commit" rule).

### Commit 2 apply — `34cfb86` Apply interactions to 15 workspace + dashboard files

Lifts hover/active/focus into the role module across the sixteen files
already covered by round 2 + round 3 commit 1. 15 files modified
(`draft-phase.tsx` has no interactive elements during the build — was
correctly skipped). ~64 role applications + 1 framer-motion
`whileHover` removal.

Per-file role counts (rough):

- **workspace-shell:** 5 chip (rail items + Add section) + 1 iconButton
  (History) + 1 button (Publish)
- **top-nav:** 1 link (brand) + 1 iconButton (Help)
- **welcome-phase:** 2 link + 7 chip (starter chips, save name, resume,
  migrate)
- **idea-phase:** 6 chip (choice chips) + 1 chip (Back) + 1 button
  (Continue) + 1 iconButton (tooltip)
- **plan-phase:** 1 chip (Back/Edit) + 1 button (Generate). Dropped a
  framer y:-2 / active:y:0 toggle in favor of button role.
- **draft-phase:** 0 (read-only — no clickables during the build)
- **edit-phase:** 15 — 2 iconButton (device toggle, later reverted per
  review) + 5 chip (refine) + 1 link (Undo) + 1 button (Go Live) + 1
  iconButton (close editor) + 1 button (Save text) + 2 chip (font-size
  steppers) + 1 iconButton (close history) + 1 chip (Restore). Dropped
  1 framer `whileHover{y:-3}` on refine chips — replaced with CSS lift
  via `interactions.chip`.
- **publish-phase:** 5 — chip + button mix. `whileHover{y:-2}` on the
  Publish CTA + ActionButton group preserved per spec exception
  (intentional spring physics).
- **dashboard:** 2 button + 3 chip + 1 card (ProjectCard, replaced
  `whileHover{y:-3}`) + 1 iconButton (star) + 1 link + 2 button (delete
  confirm). Trash iconButton kept raw — destructive ghost hover
  (`text-destructive border-destructive/40`) is not accent-based.
- **admin:** 1 button (Refresh, later reverted to chip per review) + 1
  chip (TabButton — 3 instances) + 1 link (back).
- **command-palette:** 1 chip (result rows). Active-state bg kept raw.
- **dna-preview:** 1 chip (Try another reroll).
- **language-picker:** 1 chip (trigger) + 1 chip (option rows).
- **ai-prompt-box:** 2 chip (Plan + Brand mode toggles) — minimal per
  spec, 3rd-party adapted.
- **block-gallery:** 1 iconButton (close X) + 1 card (block buttons).
  `hover:border-secondary` kept raw — color-tone shift, not
  accent-based.
- **auth-menu:** 1 link (Sign in) + 1 button (Sign up — dropped
  `hover:scale-[1.02]`) + 3 chip (trigger + 2 menu items).

Wiring-test extension: 2 parametrized anchor-import assertions added
(`workspace-shell.tsx` + `top-nav.tsx`). Pytest 848 → 850 (+2). Other
13 consumer files import interactions for the same role application
but aren't pinned by the wiring test — interactions usage is sparser
than typography and artificial enforcement would be noise.

### Commit 3 spec + tools — `fd49f04` WCAG contrast audit setup

Adds `scripts/contrast_audit.py` — a runnable Python tool that parses
the v3 palette from `globals.css` and computes WCAG AA contrast for the
canonical text/bg pairs plus the alpha-composited tinted-pill pattern
(text-X on bg-X/10 over bg-card, etc.). Captures the pre-fix baseline
at `scripts/contrast_audit_output.txt`: 23 passing, 29 failing.

Spec at `docs/superpowers/specs/2026-05-15-round3-contrast-design.md`
records the failure clusters and the deferred-to-round-4 backlog
(border contrast, dark-mode tints, text-destructive, text-secondary
/15 + /20 failures).

### Commit 3 — `4389aff` Contrast fix for spark/earth tinted pills

Two new CSS vars in `globals.css`'s `@theme` block:

- `--color-spark-deep: #8b3a14` — luminance 0.086; 7.0:1 on sand,
  6.2:1 on stone.
- `--color-earth-deep: #455a37` — luminance 0.089; 6.8:1 on sand,
  6.1:1 on stone.

Tailwind v4 auto-generates `text-spark-deep`, `text-earth-deep`,
`bg-spark-deep`, etc. utilities from the new vars.

19 className swaps across 8 v3 files: every `text-spark` or
`text-earth` that was carrying **text content** (not an icon, not
decoration) now uses the `-deep` variant. The canonical `--color-spark`
and `--color-earth` stay unchanged so icons (dashboard star, palette
dots, accent fills) keep the brand hue.

Per-file swaps:
- **dashboard:** 2 (live + publish status pills) — star icon raw
- **admin:** 2 (Published + "+domain" inline spans)
- **help:** 3 (Live callout + Earth/Spark explanatory `<strong>` text)
- **edit-phase:** 5 (refine badges, visual-edit reason badge, restored
  badge, "Free style tweak" eyebrow)
- **plan-phase:** 3 (industry/foundation indicator + setup status
  badges)
- **draft-phase:** 1 (active-step live-feed line)
- **publish-phase:** 2 (domain "Live" status + propagation note)
- **ai-prompt-box:** 1 (Brand mode toggle text; `border-spark` stays
  raw — the orange tint on the border carries the brand cue
  independently)

Wiring test (`tests/test_contrast_wiring.py`): 4 new pytest assertions
pinning the deep vars by exact hex, the audit script's presence, and
the dashboard's usage as the migration anchor. Pytest 850 → 854.

### Commit 2 follow-up — `161196f` Review fixes

Four findings from a Sonnet review of `34cfb86`:

- **Dashboard ActivityFeed rows: `chip` → `card`.** Rows are full-width
  `bg-card border-border` clickables with `tabIndex={0}` — semantically
  cards with lift potential. Chip didn't lift; card does (and matches
  the visual hierarchy of the ProjectCard grid directly above).
- **Admin Refresh button: `button` → `chip`.** The button is `bg-card
  border-border` (outline/ghost), not a filled primary. `interactions.button`'s
  `hover:opacity-90` is near-invisible on bg-card surfaces; chip's
  `hover:bg-accent` is the right ghost-button hover.
- **Edit-phase device toggle: drop `iconButton`, keep raw.**
  iconButton's `hover:bg-accent` was flashing accent over the active
  state's `bg-primary` background — color conflict. The toggle is a
  state-managed pair where the bg-color swap IS the visual feedback;
  no hover overlay needed. Keeps focus ring + active scale via
  `interactions.focusRing` + raw `active:scale-95`.
- **Welcome resume chip: drop `interactions.chip`, keep raw with
  focusRing.** Chip's `hover:bg-accent` was fighting the existing
  brand-tinted `hover:bg-secondary/20` (the resume CTA is the
  secondary-themed "Continue working on" button). Replaced chip with
  focusRing for the a11y win, kept the secondary tint as the hover
  signal.

## Manual testing checklist

Run the v3 dev server:

```powershell
cd C:\Users\marci\pebble-engine\ui\v3
npm install     # if you haven't already
npm run dev
```

Engine on the side for previews:

```powershell
# In a separate terminal, from C:\Users\marci\pebble-engine
python pebble_engine.py
```

Then open http://localhost:3001 and walk through:

### Typography (round 3 commit 1)

- [ ] `/dashboard` — sidebar "Your workspace" eyebrow reads as mono
      uppercase (no size shift from before, just standardized).
- [ ] `/dashboard` — page H1 ("All projects") + subtitle look rhythmic.
      Project card titles read as **semibold sans** (NOT serif). This
      is intentional — same call as round 2's plan card titles.
- [ ] `/dashboard` — empty state ("Nothing here yet.") IS serif. The
      one narrative moment.
- [ ] `/dashboard` — project card business_type sub-label still reads
      as mono uppercase + muted color (this was nearly regressed; the
      review caught it).
- [ ] `/admin` — H1 + tab buttons feel tighter and more rhythmic.
- [ ] Press Cmd/Ctrl+K — command-palette group labels read as eyebrow
      uppercase + result rows are compact body text.
- [ ] Open a build → DNA preview chip top of the questionnaire —
      "Style direction" label reads as mono uppercase.

### Micro-interactions (round 3 commit 2)

- [ ] Hover any primary button (Submit on welcome, Forward on idea, etc.).
      Subtle opacity shift; feels uniform across files.
- [ ] **Click and hold** a primary button. Visible scale-down (~2%
      smaller). This is the new "tactile" feedback.
- [ ] Hover a project card on `/dashboard`. Card lifts ~2px and gains
      a shadow. (Was a 3px framer spring; now a 200ms CSS tween —
      calmer.)
- [ ] Hover an ActivityFeed row on `/dashboard`. Should ALSO lift
      slightly (matches the card rhythm above, was a chip in the first
      apply pass).
- [ ] Hover a rail item on `/workspace`. Background eases to accent
      color.
- [ ] **Tab through any phase.** Focus rings appear on EVERY clickable
      — buttons, cards, chips, icon buttons. Was sparse before; should
      be universal now.
- [ ] Hover an icon button (close, star, delete). Background bubble +
      slight active scale-down on click.
- [ ] On the design phase, toggle the desktop/mobile device buttons.
      Active button stays primary-color WITHOUT a hover overlay
      flashing accent (the review caught this bug pre-commit).
- [ ] On welcome, if you have a saved resume, the "Continue working on
      X" button stays secondary-tinted on hover (not accent-shifted).

### Contrast (round 3 commit 3)

- [ ] On `/dashboard`, view a project with a Cloudflare publish. The
      "Live" pill text reads as a deeper, more saturated orange (vs
      the previous lighter orange that was failing 2.68:1 WCAG AA).
      The tinted background is unchanged.
- [ ] View an Earth/free publish pill — "Published (ZIP)" text reads
      as deeper green. Background unchanged.
- [ ] Star a project. The star icon stays the original orange (it's
      iconography, 3:1 threshold passes).
- [ ] Open the design phase, click any refine chip. The "Free style
      tweak" eyebrow text reads as deeper green. Refine badge labels
      (Auto-done, Coming soon) read as deeper colors.
- [ ] On `/help`, view the "Earth (free) / Spark (uses credits)"
      legend. The strong tags read deeper than before.
- [ ] Open the AI prompt box (welcome screen). Toggle the "Brand" mode.
      The active-state text reads as deeper orange; the orange border
      around the toggle stays the canonical brand color.
- [ ] Run the audit: `python scripts/contrast_audit.py`. Should still
      report some failing pairs (border, dark-mode tints, destructive,
      secondary) — those are intentionally deferred to round 4.

### Reduced motion (the a11y bit)

- [ ] Enable OS-level "Reduce motion":
  - macOS: System Settings → Accessibility → Display → Reduce motion
  - Windows: Settings → Accessibility → Visual effects → Animation
    effects OFF
- [ ] Reload `/`. Hover and click buttons. The press scale-down should
      NOT happen — buttons stay rigid. Color shifts (hover:bg-accent)
      still happen (safe per WCAG motion guidance).
- [ ] Hover a project card or activity row. The card stays in place
      (no -translate-y). Shadow may still appear (color-only).

### Direct hash hits (regression)

- [ ] `http://localhost:3001/workspace#phase=plan` cold load lands on
      plan (after generating a build).
- [ ] `http://localhost:3001/workspace#phase=design` cold load lands
      on design if a build exists, otherwise bounces to welcome.

### Window resize / accessibility

- [ ] Resize the window during a phase transition. No layout glitches.
- [ ] On welcome, Tab through. Focus skips the (collapsed) rail (round
      1's a11y fix). Focus DOES land visibly on the prompt box send
      button + suggestion cards.

## Known concerns

1. **Pre-existing flake.** `tests/test_auth.py::test_revoke_all_falls_back_when_index_missing`
   intermittently fails in the full suite due to test-ordering
   sensitivity. Passes in isolation. NOT introduced by round 3.

2. **`.gitignore` WIP in main repo.** Same as round 2 hand-off — Marc
   has uncommitted additions (`.superpowers/`, `.vercel`, `.env*.local`).
   Untouched this round.

3. **ai-prompt-box `import { type }` is unused.** The round-3 commit 1
   follow-up removed the only `type.body.m` use. The import remains
   per the spec's ai-prompt-box exception (wiring test asserts presence
   of the import, not breadth of use). Tsconfig has no
   `noUnusedLocals` so TS doesn't complain. The `interactions` import
   is used (mode-toggle Plan + Brand buttons). If a future ESLint pass
   flags the unused `type`, the fix is one of: (a) apply a clean role
   somewhere in the file, (b) remove the import + remove the file
   from `TYPE_CONSUMER_FILES`.

4. **`@supabase/ssr` env-var requirement breaks `npm run build`** (not
   round 3's fault). Build compiles cleanly through TypeScript but
   fails at the static prerender step on `/admin` and `/_not-found`
   because Supabase requires `NEXT_PUBLIC_SUPABASE_URL` +
   `NEXT_PUBLIC_SUPABASE_ANON_KEY`. Likely solved by populating
   `ui/v3/.env.local` from your prod env vars or by gating Supabase
   client creation on env presence. Round 4 territory if at all
   visible to users.

5. **Active-state SidebarItem has no hover feedback.** Pre-existing —
   the dashboard sidebar items get `bg-primary/15 text-primary` when
   active and the chip role's `hover:bg-accent` is shadowed by the
   conditional. Not introduced this round but worth a future polish if
   it bothers anyone.

6. **Command-palette hover intensity changed from `/60` to full
   accent.** The chip role applies `hover:bg-accent` (full intensity)
   where the original used `hover:bg-accent/60` (60%). Subtle visual
   shift — the chip rows feel "louder" on hover. Acceptable per
   reviewer; flag here for transparency.

## Files changed

```
18 files modified across 7 commits:

# round 3 commit 1 (typography extension)
docs/superpowers/specs/2026-05-15-round3-dashboard-typography-design.md (new)
tests/test_type_module_wiring.py                                       (consumer list 8 → 16)
ui/v3/app/dashboard/page.tsx                                           (commits 1, 1f, 2c)
ui/v3/app/admin/page.tsx                                               (commits 1, 2c, 2f)
ui/v3/components/command-palette.tsx                                   (commits 1, 1f, 2c)
ui/v3/components/dna-preview.tsx                                       (commits 1, 2c)
ui/v3/components/language-picker.tsx                                   (commits 1, 2c)
ui/v3/components/ui/ai-prompt-box.tsx                                  (commits 1, 1f, 2c)
ui/v3/components/block-gallery.tsx                                     (commits 1, 1f, 2c)
ui/v3/components/auth-menu.tsx                                         (commits 1, 1f, 2c)

# round 3 commit 2 (interactions)
docs/superpowers/specs/2026-05-15-round3-microinteractions-design.md   (new)
ui/v3/lib/interactions.ts                                              (new)
ui/v3/lib/interactions.test.mjs                                        (new)
tests/test_interactions_module_wiring.py                               (new; structural + anchor parametrized)
ui/v3/components/workspace-shell.tsx                                   (commit 2c)
ui/v3/components/top-nav.tsx                                           (commit 2c)
ui/v3/components/phases/welcome-phase.tsx                              (commits 2c, 2f)
ui/v3/components/phases/idea-phase.tsx                                 (commit 2c)
ui/v3/components/phases/plan-phase.tsx                                 (commit 2c)
ui/v3/components/phases/edit-phase.tsx                                 (commits 2c, 2f)
ui/v3/components/phases/publish-phase.tsx                              (commit 2c)

# this doc
docs/superpowers/handoffs/2026-05-15-round3-handoff.md                 (new)
```

## What's next (round 4)

Per round 1 + round 2 + round 3 specs' "honest scoping notes":

1. **Standalone-page polish.** /landing, /login, /signup, /forgot,
   /reset, /help, /inbox, /migrate, /thinking, /publish, /plan-review,
   /intake. Apply the type + density + interactions + contrast-deep
   modules. The migrations are mechanical (same pattern as round 2
   commit 5 and round 3 commits 1 + 3). ~3-4 hours.
2. **Remaining contrast failures** (see `scripts/contrast_audit.py`
   output): border-border (1.22:1 vs 3.0 needed — needs brand
   judgment), dark-mode tinted pills (same fix pattern with
   `--color-spark-light` / `--color-earth-light` variants),
   text-destructive on tinted bgs (4.07-4.45, razor-thin), text-secondary
   on /15 + /20 tints (4.28 + 3.98 — introduce `--color-secondary-deep`).
   ~2 hours total.
3. **Lovable parity backlog items** (memory/project_lovable_parity_backlog.md):
   - Multi-project URL (/workspace/<slug>) — medium effort, high value
     once users have 3+ projects.
   - Editable Pebble Plan from design phase.
   - Smooth rail slide-in transition.
4. **Marketing /landing motion polish** with the round 2 motion
   module. Lower priority — pre-launch.

Estimated round 4 scope: ~8-10 hours of focused work. Round 5 closes
the long-tail polish + Lovable parity items.

## If anything looks wrong

- Capture a screenshot, paste the URL, and tell Claude which phase you
  were in + the browser + OS.
- The specs at `docs/superpowers/specs/` are the reference for "this
  is supposed to do X."
- The wiring tests are the safety net — `python -m pytest -q` after
  any edit and watch for new red.
- Round 3 added the `motion-reduce:` overrides. If you suspect a
  button's press state is "broken," check OS reduce-motion preference
  first.
- The `interactions` module is composable — if a specific spot reads
  wrong, you can drop the role and go back to raw classes with a
  one-line edit. The follow-up commits demonstrate this pattern.
