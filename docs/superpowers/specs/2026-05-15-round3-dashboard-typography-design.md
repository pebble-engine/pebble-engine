# Round 3 / Dashboard + Standalone Typography — Design Spec

**Date:** 2026-05-15
**Owner:** Marc (Claude operating autonomously per the round 3 mandate)
**Scope tier:** Companion pass to round 2 — extend the type scale + 4px density to the eight outside-workspace files.
**Status:** Self-approved 2026-05-15 (autonomous mode).

## Summary

Round 2 standardized typography + density across the workspace shell and six
phase files. Round 3 commit 1 closes the parallel gap on the outside-workspace
files that Marc sees most often: dashboard, admin, and the six standalone
components that float across surfaces.

The migration heuristic, the spec, and the wiring-test pattern are all
**unchanged** from round 2 — see
`docs/superpowers/specs/2026-05-15-workspace-typography-density-design.md`.
This doc just extends the file list, calls out a few per-file nuances, and
records the wiring-test extension.

## Goals

- **Same type scale, eight more files.** No new roles, no scale changes.
  Apply `@/lib/type` consumer-side; let raw className utilities for color,
  layout, and component-specific quirks stay where they are.
- **Same 4px density rules.** Round any `py-1.5` / `py-2.5` / `mt-0.5` /
  `gap-1.5` etc. inside these eight files. Optical 2px tweaks
  (`p-0.5` on a tiny count badge) stay.
- **Extend the wiring test.** `TYPE_CONSUMER_FILES` grows from 8 to 16. The
  test pins import-presence — if one of the round-3 files quietly slips
  back to raw Tailwind on a later refactor, pytest catches it.
- **No behavioral changes.** No event-handler rewiring, no markup
  restructuring, no new components.

## Non-goals (deferred to round 3+ later commits)

- Component-level micro-interactions (hover/active/focus polish). That is a
  separate commit later this round if there's time.
- Color / contrast pass.
- The generated marketing sites (output/) — separate codebase.
- /landing, /help, /inbox, /migrate, /thinking, /forgot, /reset, /login,
  /signup, /intake, /publish, /plan-review, /workspace standalone page
  files (the main `/workspace` chrome is already standardized via
  `workspace-shell.tsx`).

## Files modified

The eight round-3 files:

- `ui/v3/app/dashboard/page.tsx`
- `ui/v3/app/admin/page.tsx`
- `ui/v3/components/command-palette.tsx`
- `ui/v3/components/dna-preview.tsx`
- `ui/v3/components/language-picker.tsx`
- `ui/v3/components/ui/ai-prompt-box.tsx`
- `ui/v3/components/block-gallery.tsx`
- `ui/v3/components/auth-menu.tsx`

### What does NOT change

- `ui/v3/lib/type.ts` itself — the scale is final.
- The 8 round-2 files already standardized.
- Anything under `output/` (generated sites).
- Backend Python code.

### Blast radius

8 v3 files modified + 1 wiring-test extension (+8 parametrized cases).
Estimated ~120–180 lines net change.

## Per-file nuances

These are the judgment calls that need explicit recording so the reviewer
and any future bisector understand the *why* behind a swap.

### `app/dashboard/page.tsx`

- **Cost-telemetry number** (`Estimated cost` block): the figure
  `${usage.total_estimated_cost_usd.toFixed(4)}` is structural data, not
  a narrative moment. Drop the serif — use `type.heading.m`. Same rule
  as round 2's "plan card titles → heading.m" call.
- **Project card title** (`<h3>` in `ProjectCard`): same logic — drop the
  serif, use `type.heading.m`. Cards are structural, not narrative.
- **`text-[10px]` text-muted-foreground spots** (cost subtext, activity
  file count, project card "files" line): these are below the scale.
  `text-xs` (12px) via `type.caption` is the correct widen-up; the 2px
  bump improves legibility per the round-2 accessibility note (body sizes
  lean ≥16px ideal; metadata ≥12px floor).
- **Sidebar `Your workspace` eyebrow** (`text-xs font-mono uppercase
  tracking-widest text-muted-foreground`): exact-match for `type.mono`.
- **Cost `ESTIMATED COST` label** (`text-[10px] font-bold uppercase
  tracking-widest`): semantic match for `type.eyebrow`. The size shift
  (10 → 11) and the weight shift (bold → semibold) are both intentional
  unification — that's the entire point of the role module.
- **Buttons** ("Start something new", "Keep it", "Delete"): keep raw
  `text-sm font-semibold` — buttons have no role in the type module.
  Density-only fix: `py-2.5` → `py-2`, `py-1.5` → `py-2`.
- **Empty-state headings** (`font-display text-2xl text-foreground`):
  serif gravitas, the rare narrative moment in an admin surface. Use
  `type.display.m` (semibold via the role; one weight bump from the
  original's default-normal).

### `app/admin/page.tsx`

- **Page H1** (`font-display text-3xl font-bold`): `type.display.m`. One
  weight downgrade (bold → semibold) per the role; consistent with how
  round 2 handled dashboard-level H1s.
- **Subtitle** (`text-sm text-muted-foreground mt-1`): `type.body.s` +
  `text-muted-foreground` + `mt-1`.
- **Tab labels** (`flex … text-sm font-semibold border-b-2`): button-like
  tabs; keep raw — no role fits. No density issue.
- **Table contents** (`text-sm`, `text-xs`, `font-mono text-xs`, etc.):
  data display. Use `type.body.s` for the `text-sm` cells where it's a
  clear semantic match; leave the `text-xs font-mono` spans raw because
  `type.mono` adds `uppercase` and `tracking-widest` which are wrong for
  email/slug display.
- **Inline `<code>` tags** in the description: keep raw `font-mono
  text-xs` — code-style runs aren't `type.mono` (no uppercase).

### `components/command-palette.tsx`

- **Group section labels** (`text-[10px] font-bold uppercase tracking-widest
  text-muted-foreground`): `type.eyebrow`. Same upgrade as dashboard.
- **Result row label** (`text-sm text-foreground`): `type.body.s` +
  `text-foreground`. body.s adds `leading-normal` which is harmless on
  a single-line result row.
- **Input** (`text-base text-foreground`): keep raw — form input.
- **Hint chip** (`text-[11px] text-muted-foreground font-mono`): close to
  `type.eyebrow` (text-[11px] + tracking) but lacks `uppercase`. Leave raw;
  it's a value-display chip, not a label.
- **Footer hint row** (`text-[11px] text-muted-foreground`): leave raw;
  no role fits a 11px-non-uppercase body run.

### `components/dna-preview.tsx`

- **Style direction label** (`font-mono text-[10px] uppercase tracking-widest`):
  exact-match-with-size-upgrade for `type.mono`. Size goes 10 → 12.
- **Card label** (`font-display text-sm md:text-base font-semibold`):
  `type.heading.s` is `text-base font-semibold leading-snug` — close
  match but no `md:` step-down. The original ramps `text-sm md:text-base`;
  judgment call: use `type.heading.s` (always text-base). Loses the
  small-screen step-down, gains rhythm.
- **Reroll button** (`text-xs font-semibold text-muted-foreground …`):
  keep raw; buttons have no role.
- **Body font + display font sub-label** (`text-xs text-muted-foreground`):
  `type.caption` (exact match).

### `components/language-picker.tsx`

- **Wrapper label** ("Site language:"): `text-xs text-muted-foreground`
  → `type.caption`.
- **Option labels** inside the menu (`text-sm`, `font-semibold` native
  name, `text-[10px]` english name): native = `type.label`-ish but uses
  semibold not medium; leave the option raw (it's a clickable button
  with form semantics). English name `text-[10px]` → keep raw (no role
  for 10px non-uppercase body). Density `py-2` already on grid.
- **Trigger button** (`text-foreground font-semibold … px-2 py-1`):
  keep raw.

### `components/ui/ai-prompt-box.tsx`

- This is a 3rd-party adapted component (see comment at top). Keep the
  migration *minimal*: only swap obvious mappings, no restructuring.
- **`text-base` textarea** classes: form-input — leave raw.
- **`text-sm`/`text-base` tooltip and dialog title**: leave raw
  (component-internal styling defined by the adapted library).
- **`text-xs` mode-toggle labels** (Plan / Brand): leave raw — they
  exist inside animated width-collapse spans, swapping risks visual
  regression.
- **`font-mono text-sm` voice-recorder timer**: leave raw — close to
  `type.mono` but uses text-sm not text-xs and isn't uppercase.

The migration policy here is: **import `@/lib/type` for the file's wiring
test to pass, but only use a role where the swap is an unambiguous match.**
For this file, that means importing the module and using `type.body.m` on
the one or two places where the role precisely fits, OR adding a single
`type.caption` use somewhere we have an exact match.

If no exact match exists, this file is the **one acceptable exception**:
add the import but use it sparingly. The wiring test asserts presence of
the import, not breadth of use.

### `components/block-gallery.tsx`

- **Modal h2** (`font-display text-2xl font-semibold text-foreground`):
  `type.display.m`. Modal title is the rare narrative moment.
- **Description below** (`text-sm text-muted-foreground mt-1`):
  `type.body.s` + `text-muted-foreground`.
- **Category section labels** (`font-mono text-xs uppercase tracking-widest
  text-muted-foreground mb-3`): exact-match for `type.mono`.
- **Block label** (`font-semibold text-sm text-foreground`):
  `type.label` is `text-sm font-medium`; this is semibold. Leave raw
  (button-like card title).
- **Block description** (`text-xs text-muted-foreground leading-snug`):
  `type.caption` is `text-xs leading-normal text-muted-foreground`;
  original uses `leading-snug` which is tighter. Judgment: use
  `type.caption` — the small leading difference (1.25 vs 1.5) is
  acceptable in a card body and gains rhythm.

### `components/auth-menu.tsx`

- **Sign in / Sign up links** (`text-sm font-medium text-muted-foreground
  …`): `type.label` is exact (`text-sm font-medium leading-snug`) — apply.
- **Signed-in trigger button** (`text-sm font-medium text-foreground`):
  `type.label` + override.
- **Initial avatar** (`font-semibold text-xs`): keep raw; that's
  inside-the-avatar layout, not a role-fit.
- **Email truncate span** (no size class — inherits from parent button):
  no change.
- **Menu items** ("Signed in as" / `text-sm text-foreground` / etc.):
  apply where exact-fit:
  - "Signed in as" + email name: `text-xs` → `type.caption`, email line
    `text-sm font-medium` → `type.label`.
  - Menu links `text-sm text-foreground`: body.s + override.
- **Density:** `py-1.5` → `py-2` on the Sign in/Sign up chips and the
  trigger button; `py-2.5` → `py-2` on the menu header divider.

## Wiring-test extension

`tests/test_type_module_wiring.py` already declares
`TYPE_CONSUMER_FILES`. Extend the list with the eight round-3 files:

```python
TYPE_CONSUMER_FILES = [
    # round 2 (unchanged):
    REPO_ROOT / "ui" / "v3" / "components" / "workspace-shell.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "top-nav.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "welcome-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "idea-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "plan-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "draft-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "edit-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "publish-phase.tsx",
    # round 3 commit 1:
    REPO_ROOT / "ui" / "v3" / "app" / "dashboard" / "page.tsx",
    REPO_ROOT / "ui" / "v3" / "app" / "admin" / "page.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "command-palette.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "dna-preview.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "language-picker.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "ui" / "ai-prompt-box.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "block-gallery.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "auth-menu.tsx",
]
```

No new assertions needed — the existing parametrized test does the work.
After the migration, pytest grows from 836 to 844 (8 new parametrized
cases).

## Risk mitigation

- **Round-2 precedent.** This is the exact same operation done on a
  different file set. The risk profile is identical: visual regressions
  invisible to pytest, plus the structural sanity that the wiring test
  enforces. Manual smoke is on Marc when he checks back.
- **Subset-only.** Eight files. Anything else (other app pages, ui/*
  subcomponents, generated sites) is out of scope.
- **Reversible.** Every change is a className edit. If a specific spot
  reads wrong, the fix is a one-line override or a back-out to raw.
- **No backend impact.** Pure v3 frontend. No Python source changes
  except the wiring-test extension.

## Honest scoping notes

What this commit does NOT close:

1. **Component-level micro-interactions.** Hover / active / focus polish
   on every clickable element. Round 3 / commit 2-N if time allows; round
   4 otherwise.
2. **Color / contrast pass.** Out of scope.
3. **Standalone page files** outside the dashboard/admin/component-8.
   `/help`, `/inbox`, `/migrate`, `/intake`, `/publish`, etc. all still
   use ad-hoc Tailwind type. They will get this same treatment if there's
   time later in the round, otherwise round 4.

Estimated impact of this commit alone: closes the visible
typography-rhythm gap on the dashboard and admin surfaces (the screens
Marc visits between builds). The workspace was already rhythmic from
round 2; this brings the bookend pages to parity.

## References

- Spec: `2026-05-15-workspace-typography-density-design.md` — the round 2
  spec with the full heuristic table.
- Code: `ui/v3/lib/type.ts` — the typography scale module.
- Code: `tests/test_type_module_wiring.py` — wiring test to extend.
- Commit: `266d868` — round 2 / commit 5, the precedent for this commit's
  swap pattern.
