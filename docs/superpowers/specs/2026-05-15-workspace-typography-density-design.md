# Workspace Typography + Density Pass — Round 2 Design Spec

**Date:** 2026-05-15
**Owner:** Marc (Claude operating autonomously per the round 2 mandate)
**Scope tier:** Foundation pass — define the scale, apply it to the workspace-critical files, leave dashboard/admin for round 3.
**Status:** Self-approved 2026-05-15 (autonomous mode), ready for implementation.

## Summary

The workspace shell + phase files use ad-hoc Tailwind type utilities — twenty different combinations of `text-xs`/`text-sm`/`text-base` × `font-medium`/`font-semibold`/`font-bold` × occasional `tracking-*`/`leading-*`. The result is rhythmic noise: similar UI in different files reads at slightly different sizes / weights / line heights.

This round defines a typography scale module and applies it across the workspace shell + the seven phase files (welcome, idea, plan, draft, edit, publish, top-nav). It also rounds spacing to the 4px/8px grid in the same files. Dashboard, admin, and the standalone-page surfaces are explicitly deferred to round 3.

The point of the scale is the *rhythm*, not the styling — a designer should be able to say "use heading.l" without rethinking weight + line-height + tracking each time.

## Goals

- **One source of truth for type.** A `ui/v3/lib/type.ts` module exporting a flat set of Tailwind className strings keyed by role (display.xl, display.l, display.m, heading.l, heading.m, heading.s, body.l, body, body.s, label, caption, eyebrow, mono). Consumers import + spread.
- **Single typeface family per role.** Inter Variable carries body and most headings. Literata (font-display) is reserved for the few "narrative" moments — section openers, hero copy, the welcome headline. JetBrains Mono only for code/build-feed text.
- **Workspace-critical file coverage.** workspace-shell, top-nav, welcome-phase, idea-phase, plan-phase, draft-phase, edit-phase, publish-phase. Eight files. Anything else is round 3.
- **Density on the 4px grid.** All padding / gap / margin in the same eight files round to multiples of 4 (8, 12, 16, 24, 32 …). 2px is allowed only as a tweak inside a component (icon centering, optical adjustments).
- **No visible regressions on the typical paths.** Welcome → idea → plan → draft → design happy path should look tighter and more rhythmic but should not lose any information density.

## Non-goals (deferred to round 3+)

- Component-level micro-interactions (hover/active/focus polish on every clickable element). Round 3.
- Full color / palette refinement. Out of scope.
- Dashboard, admin, command-palette, dna-preview, language-picker, ai-prompt-box, the-infinite-grid, block-gallery, auth-menu — typography in those files keeps working, just isn't standardized this pass. Round 3.
- The generated marketing sites (output/) — that's a separate codebase with its own constraints.
- Migration of every `text-xs` to `caption` even when the existing value is correct — only files in the eight-file scope get the consumer-side change.
- Density audit on tab triggers, modals, popovers — only on the workspace shell + phases.

## Architecture

### New file

- `ui/v3/lib/type.ts` — exports the typography scale. The module is a pure object literal of `as const` strings; no runtime work.

### New test

- `tests/test_type_module_wiring.py` — pins:
  - `lib/type.ts` exists.
  - The expected role keys are present (display.{xl,l,m}, heading.{l,m,s}, body.{l,m,s}, label, caption, eyebrow, mono).
  - The eight workspace-critical files import from `@/lib/type` (via parametrized assertion). This catches regressions where someone copy-pastes a raw Tailwind size into a workspace file instead of using the module.

### Files modified

- `ui/v3/components/workspace-shell.tsx`
- `ui/v3/components/top-nav.tsx`
- `ui/v3/components/phases/welcome-phase.tsx`
- `ui/v3/components/phases/idea-phase.tsx`
- `ui/v3/components/phases/plan-phase.tsx`
- `ui/v3/components/phases/draft-phase.tsx`
- `ui/v3/components/phases/edit-phase.tsx`
- `ui/v3/components/phases/publish-phase.tsx`

### What does NOT change

- The font import chain in `app/layout.tsx`. Inter, Literata, and JetBrains Mono all stay as-is.
- The `font-display` Tailwind utility (already wired in globals.css).
- Existing color tokens — we're not retoning anything this pass.
- Any backend code.
- The dashboard, admin, and standalone components — touch later.

### Blast radius

8 v3 files modified + 1 new lib + 1 new wiring test. ~150-250 lines net change. No backend impact.

## The typography scale

```ts
// ui/v3/lib/type.ts
export const type = {
  display: {
    xl: "font-display text-5xl md:text-6xl font-bold tracking-tight leading-[1.05]",
    l:  "font-display text-4xl md:text-5xl font-bold tracking-tight leading-[1.1]",
    m:  "font-display text-2xl md:text-3xl font-semibold tracking-tight leading-[1.2]",
  },
  heading: {
    l: "text-xl md:text-2xl font-semibold tracking-tight leading-snug",
    m: "text-lg font-semibold leading-snug",
    s: "text-base font-semibold leading-snug",
  },
  body: {
    l: "text-lg leading-relaxed",
    m: "text-base leading-relaxed",
    s: "text-sm leading-normal",
  },
  label:   "text-sm font-medium leading-snug",
  caption: "text-xs leading-normal text-muted-foreground",
  eyebrow: "text-[11px] font-semibold uppercase tracking-[0.08em] text-muted-foreground",
  mono:    "font-mono text-xs uppercase tracking-widest",
} as const;
```

Notes on the choices:

- `font-display` is the existing Literata wiring. We keep it — but only for `display.*`. Heading and body roles use Inter (the default sans).
- Sizes anchor to Tailwind defaults so we don't introduce bespoke px values: `text-xs`=12, `text-sm`=14, `text-base`=16, `text-lg`=18, `text-xl`=20, `text-2xl`=24, `text-3xl`=30, `text-4xl`=36, `text-5xl`=48, `text-6xl`=60. Only the eyebrow uses an arbitrary value (`text-[11px]`) because there's no Tailwind utility for it and 11px is the conventional uppercase-label size.
- Line heights match weight: tighter for display (1.05–1.2), loose for body (`leading-relaxed` = 1.625), in-between for headings (`leading-snug` = 1.375).
- Letter spacing tightens display (`tracking-tight` = -0.025em) and loosens uppercase (`tracking-[0.08em]`).

### Migration heuristic

When migrating an existing className, the swap is roughly:

| Was (common patterns) | Becomes |
|---|---|
| `font-display text-5xl md:text-6xl font-bold tracking-tight` | `type.display.xl` |
| `font-display text-3xl font-bold` | `type.display.m` |
| `font-display text-2xl font-semibold` | `type.display.m` (sometimes `type.heading.l`) |
| `text-2xl font-bold` | `type.heading.l` |
| `text-xl font-semibold` | `type.heading.m` |
| `text-lg font-semibold` | `type.heading.s` (or `type.heading.m` if it's a card title) |
| `text-base font-semibold` | `type.heading.s` |
| `text-sm font-medium` | `type.label` |
| `text-sm` | `type.body.s` |
| `text-base` | `type.body.m` |
| `text-xs text-muted-foreground` | `type.caption` |
| `text-[11px] font-semibold uppercase tracking-widest` | `type.eyebrow` |
| `text-xs font-mono uppercase tracking-widest` | `type.mono` |

Color, background, layout utilities stay on the element — `type.X` only governs size/weight/leading/tracking/family. Consumer composes:

```tsx
<h1 className={`${type.display.l} text-foreground drop-shadow-sm`}>{headline}</h1>
```

## Density rules

The 4px grid is the rhythm; 8px is the dominant interval. Rules:

- **Section / vertical layout spacing:** multiples of 8 (`gap-2`, `gap-3`, `gap-4`, `gap-6`, `gap-8`, `gap-12`, `gap-16`).
- **Within-section spacing:** multiples of 4 (`p-1`, `p-2`, `p-3`, `p-4`, `p-6`).
- **Inside a single component (icon align, optical centering):** 2px tweaks allowed (`p-0.5`, `gap-0.5`).
- **Forbidden in the eight files this round:** `p-2.5`, `py-1.5`, `gap-1.5`, `mt-0.5` (use `gap-1` or `gap-2` instead — pick the one that visually works).
- Existing `px-3 py-1.5` button padding pattern → `px-3 py-2` (12 horizontal × 8 vertical, more breathing room).
- Existing `p-2.5` card padding → `p-3` (12px) when small, `p-4` (16px) when comfortable.

The migration is judgment-driven per element — extract the intent ("this is a tight chip" vs "this is a comfortable card") and snap to the nearest correct multiple.

## Testing strategy

### Automated

- `tests/test_type_module_wiring.py`:
  - `type.ts` exists.
  - Module exports `type` as the named export.
  - Source contains the expected role keys.
  - Each of the eight workspace-critical files imports from `@/lib/type`.
- (Optional) `ui/v3/lib/type.test.mjs` — plain-Node verifier mirroring the Python pins. Same pattern as `motion.test.mjs`.

### Manual smoke (manual checklist in handoff doc)

- Navigate welcome → idea → plan → draft → design and look for any text that suddenly feels too small or too large vs adjacent elements.
- Confirm the welcome H1 still reads as the dominant element on the screen.
- Confirm the build feed code text still feels "code" (mono, small, uppercase-label header).
- Confirm card padding feels deliberate, not cramped.
- Confirm no text overflows or wraps awkwardly at common breakpoints (400, 768, 1024, 1440).

## Risk mitigation

- **Plain-text + Python wiring tests** cover the structural side. The visual side genuinely cannot be regression-tested without screenshots, so we explicitly accept that the visual shift is intentional.
- **Subset-only.** Touching only eight files limits the blast radius. Dashboard / admin / standalone components keep their existing typography until round 3.
- **Reversible.** The migration is a series of className swaps. If a specific spot looks wrong after the change, the fix is a one-line edit to override the role with a longer-form className.
- **No backend impact.** No Python source changes except the new wiring test.

## Honest scoping notes

What this spec does NOT close:

1. **Component-level micro-interactions.** Hover / active / focus polish on every clickable element. Linear has obsessive transition timing on every button — Pebble does not. Round 3.
2. **Color / contrast pass.** The current palette works; this round is structural rhythm only.
3. **Dashboard / admin standardization.** They use the same Tailwind utilities but live outside the workspace shell. They look fine for now and will get this same scale + density pass in round 3.
4. **Generated-site typography.** Output sites have their own type system inside `output/<slug>/site/`. Not touched.

Estimated impact of this spec alone: closes ~50–60% of the "feels noisy and unrhythmic" complaint when scrolling through the workspace shell. Round 3 (component micro-interactions + dashboard pass + color refinement) closes the rest.

## References

- Reference: Linear's design system (loaded via `linear-design` skill) — single typeface, 4px grid, restrained accent. Used as a *rhythm and discipline* reference, not a verbatim brand copy.
- Code: `ui/v3/lib/motion.ts` — pattern for new `ui/v3/lib/type.ts`.
- Code: `tests/test_motion_module_wiring.py` — pattern for new wiring test.
- Memory: `feedback_universal_design_not_senior.md` — typography must read for everyone, including older eyes; body sizes lean ≥16px.
- Spec: `2026-05-15-workspace-motion-polish-design.md` — round 1 spec for context on the broader premium-polish arc.
