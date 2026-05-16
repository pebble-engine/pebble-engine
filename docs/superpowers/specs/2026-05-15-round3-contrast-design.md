# Round 3 / Color + Contrast Pass — Design Spec

**Date:** 2026-05-15
**Owner:** Marc (Claude operating autonomously per the round 3 mandate)
**Scope tier:** Targeted WCAG AA fix for accent-text on tinted backgrounds.
Foundation cleanup (border contrast) and dark-mode-specific failures
deferred to round 4.
**Status:** Self-approved 2026-05-15 (autonomous mode).

## Summary

A WCAG AA contrast audit of the v3 palette (via
`scripts/contrast_audit.py`) surfaced 29 failing pairs. The pattern is
consistent: `text-spark` and `text-earth` (warm orange + sage green
brand accents) have luminance values that sit in the middle of the
range — bright enough to read as "warm" or "natural" but not dark
enough for 4.5:1 against light tinted surfaces.

The fix is to introduce two darker, accessibility-focused variants of
each accent — `--color-spark-deep` and `--color-earth-deep` — and use
them anywhere `text-spark` or `text-earth` appears as **text** (not
icon) over a tinted background. The original `--color-spark` and
`--color-earth` stay unchanged for icons (where the WCAG threshold is
3:1, not 4.5:1) and for standalone large-text or decorative usage.

## Goals

- **Eliminate accent-text-on-tinted-pill contrast failures.** Every
  badge / pill / status indicator using `text-spark` or `text-earth`
  reads at ≥4.5:1 against its tinted background.
- **Preserve the brand palette.** `--color-spark` (#c76e3a) and
  `--color-earth` (#5b6f4a) keep their canonical values for non-text
  uses (icons, fills, decorative).
- **Introduce only two new CSS vars.** Minimum-viable readability
  variants. No semantic re-architecture this round.
- **Document the deferred failures.** Border contrast (1.22-1.37:1 vs
  3:1 threshold), dark-mode spark/earth failures, text-destructive
  failures (razor-thin 4.07-4.45) all get backlog entries — not fixed
  this round.
- **Pin the fix with a test.** A pytest assertion that the two new
  CSS vars exist + a runnable audit script that can be re-executed any
  time the palette changes.

## Non-goals (deferred to round 4+)

- **Border contrast.** `--color-border` (pebble #d8d1c5) at 1.22-1.37
  against sand/stone fails the 3:1 UI threshold. Fixing this requires
  a brand-judgment call about how visible borders should be — a
  significantly darker pebble shifts the entire app's visual character
  toward "more defined / structural" and away from the current
  "calm, soft outlines." Defer until Marc weighs in.
- **Dark mode accent-on-tinted pills.** `text-spark` on
  `bg-spark/10-over-dark-card` is 4.06:1 (and gets worse at higher
  alphas: 3.80, 3.53, 3.04). Same fix pattern would work — add
  `--color-spark-light` for dark-mode use. Defer until dark mode has
  real users.
- **text-destructive failures.** Range from 3.16:1 (worst) to 4.45:1
  (closest to passing). The current red is already lighter than most
  destructive colors. Backlog: choose between a darker destructive or
  switching to neutral text in destructive pills.
- **text-spark standalone on bg-background** (3.32:1 — fails normal
  text, passes large/UI). Used in admin "+ domain" inline span, help
  page strong text, draft phase. Acceptable for now per the "large
  text 3:1" path; flag in handoff.
- **`text-earth` standalone on bg-card** (4.43:1 — narrowly fails).
  Used in admin "Published" inline span. Replaceable with
  text-earth-deep in round 4 cleanup. Not fixed this commit to keep
  scope tight.
- **Color/contrast for the generated marketing sites** (output/). Out of
  scope — separate codebase.

## Architecture

### Updated file

- `ui/v3/app/globals.css` — adds two new CSS vars to the `@theme` block:
  - `--color-spark-deep: #8b3a14` — luminance ≈ 0.086, contrast 7.0:1
    on sand and 6.2:1 on stone.
  - `--color-earth-deep: #455a37` — luminance ≈ 0.089, contrast 6.1:1
    on stone, 6.8:1 on sand.

Tailwind v4 auto-generates `text-spark-deep`, `bg-spark-deep`, and
`border-spark-deep` utilities from the new var (same as the existing
`text-spark` from `--color-spark`).

### New test

- `tests/test_contrast_wiring.py` — pins:
  - `--color-spark-deep` exists with value `#8b3a14`.
  - `--color-earth-deep` exists with value `#455a37`.
  - `scripts/contrast_audit.py` exists and is runnable.
  - The deep-variant utility names appear in at least the dashboard
    file (proves the migration was applied).

### Files modified — apply pass

The same migration pattern as the typography + interactions passes:
find every `text-spark` and `text-earth` usage that operates over a
tinted background, replace with `text-spark-deep` / `text-earth-deep`.
Leave icon and decorative usage unchanged.

- `ui/v3/app/dashboard/page.tsx` — live status pill, published pill.
- `ui/v3/app/admin/page.tsx` — "Published" + "+ domain" inline spans.
- `ui/v3/app/help/page.tsx` — Live / Earth / Spark explanatory text.
- `ui/v3/components/phases/edit-phase.tsx` — refine badges, visual-edit
  reason badge, restored badge.
- `ui/v3/components/phases/plan-phase.tsx` — selected indicator pill,
  visual-edit + restored badges.
- `ui/v3/components/phases/draft-phase.tsx` — active-step text-spark
  in macro checklist.
- `ui/v3/components/phases/publish-phase.tsx` — `Live` callout.
- `ui/v3/components/ui/ai-prompt-box.tsx` — Brand mode toggle.

### What does NOT change

- The `--color-spark` and `--color-earth` canonical values. Brand
  palette untouched.
- The motion + type + interactions modules. Independent surfaces.
- The dashboard `ProjectCard` star icon (`fill-spark text-spark`) —
  it's an icon (3:1 threshold, passes).
- The pebble droplet decoration uses `bg-sage` — unrelated.
- Backend Python code (except the new wiring test + the audit script).

### Blast radius

1 globals.css edit + 1 new audit script (already created) + 1 new
pytest + ~8 v3 files modified for the className swap. Estimated ~25-40
lines net change in v3 files, +50 lines for the audit script (already
landed).

## Migration heuristic

| Was | Becomes |
|---|---|
| `text-spark` on a tinted bg (bg-spark/10, bg-spark/15, etc.) | `text-spark-deep` |
| `text-spark` on a plain bg (text used as label/heading) | `text-spark-deep` if normal text size, leave raw if large/decorative |
| `text-spark` on an icon (`<Icon className="text-spark">` or `fill-spark text-spark`) | leave raw — icons use 3:1 threshold, spark passes |
| `text-earth` on a tinted bg | `text-earth-deep` |
| `text-earth` on a plain bg (e.g., admin status span) | `text-earth-deep` for normal text, raw for large |

Rule of thumb: **if the spark/earth color is carrying text content**,
use the deep variant. **If it's carrying iconography or decoration**,
the canonical color stays.

## Testing strategy

### Automated

- `scripts/contrast_audit.py` — runnable any time. Reports passing /
  failing pairs. Returns exit 1 if any failures remain. This commit
  intentionally KEEPS the failures around the deferred items
  (border, dark-mode tints, text-destructive); only the spark/earth
  tinted-pill failures are eliminated.

- `tests/test_contrast_wiring.py`:
  - `--color-spark-deep: #8b3a14` present in globals.css.
  - `--color-earth-deep: #455a37` present in globals.css.
  - `scripts/contrast_audit.py` is present and importable.
  - At least one consumer file uses `text-spark-deep` or
    `text-earth-deep` (proves the migration was applied — the
    dashboard is the canonical anchor).

### Manual smoke (handoff doc)

- Open `/dashboard`. Star a project — the star icon stays orange.
  Hover the star — the orange darkens slightly (unchanged).
- View a project card with a Cloudflare publish — "Live" pill text is
  darker / more saturated. Tinted background is unchanged.
- View an Earth/free publish pill — "Published (ZIP)" text is a
  deeper green. Background unchanged.
- Open the design phase. Refine controls with the spark accent state
  read darker.
- Open the help page. Spark/Earth callout text is darker.

## Risk mitigation

- **Two new CSS vars only.** Nothing about the existing palette
  changes. The deep variants are additive; if any spot reads "too
  dark" after the migration, the fix is one-line: revert to the
  original `text-spark` or `text-earth`.
- **Audit script + pytest pin.** A regression that drops the vars or
  introduces a new failing pair surfaces immediately on the next
  audit run.
- **Subset coverage.** Only spark/earth tinted-pill text-content
  failures fixed. Everything else (border, dark mode, destructive,
  secondary on /15 and /20 tints) recorded as backlog.
- **Reversible.** Same role-module pattern — every change is a
  className edit. No structural changes, no logic changes.

## Honest scoping notes

What this commit does NOT close:

1. **Border contrast.** The biggest visible WCAG failure (1.22-1.37:1
   vs 3:1 needed). Requires a brand judgment about how visible borders
   should be. Backlog.
2. **Dark mode accent pills.** Same fix pattern; defer until dark mode
   has actual usage to validate the lighter variants visually.
3. **text-destructive on tinted backgrounds.** Falls just under 4.5:1
   in most cases. Worth fixing in round 4 if the patterns proliferate.
4. **text-secondary on bg-secondary/15 and /20.** Falls 4.28 and 3.98.
   Same fix pattern (introduce `--color-secondary-deep`) — defer.
5. **The audit script is not run automatically.** It's a manual tool
   today. Round 4 candidate: wire it into the pytest suite as a
   "soft" check (fails surface as warnings, not red).

Estimated impact of this commit alone: eliminates the worst
spark/earth tinted-pill failures (worst case 2.19:1 in light theme).
~12 failing pairs become passing. Closes the most visible accessibility
gap without a brand-palette shift.

## References

- Script: `scripts/contrast_audit.py` — the audit tool. Run with
  `python scripts/contrast_audit.py`.
- Output: `scripts/contrast_audit_output.txt` — captured audit
  baseline before this commit's fixes.
- Code: `ui/v3/app/globals.css` — palette source.
- WCAG: WCAG 2.1 SC 1.4.3 (Contrast Minimum) — 4.5:1 normal text, 3:1
  large text. WCAG 2.1 SC 1.4.11 (Non-Text Contrast) — 3:1 for UI
  components and graphical objects.
- Spec: `2026-05-15-workspace-typography-density-design.md` — round 2
  pattern for module-then-apply commits.
