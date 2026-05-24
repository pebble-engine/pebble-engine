# Generator Silent-Failure Audit — 2026-05-23

**Context:** Three consecutive sites rendered as plain HTML with browser defaults (blue
underlined links, no layout). Root cause was the Tailwind directives bug — fixed in
c5d8c6a. This audit searches for the same failure *pattern* (prompt instruction taken
too literally, silently skipping a required line) across the full template and eval suite.

**Scope read:** `skills/prompt_template.md` (full, ~1209 lines), `pebble/evals/checks.py`
(full, ~4553 lines), both `output/indie-bookstore/site/` and
`output/coffee-shop-in-oakland/site/` as ground-truth LLM output.

---

## CRITICAL FINDINGS

These would silently break a build. Severity ordered by how invisible the failure is.

---

### C1 — `tailwind_directives_present` eval exists but is NOT wired into `ALL_CHECKS`

**File:** `pebble/evals/checks.py`, line 1166 (function definition) vs line 4462
(ALL_CHECKS list).

**What happened:** The eval was written and annotated correctly (comment at line 1153
explains the Tailwind directives bug). It was never appended to `ALL_CHECKS`. The
auto-repair loop and the `python -m pebble.evals` report both iterate over
`ALL_CHECKS` exclusively — so `tailwind_directives_present` is dead code. If the
Tailwind bug recurs in a Qwen 3.6 test build today, the eval fires on no site and the
repair loop never triggers.

**Failure mode:** Site renders as plain HTML with browser defaults. Same exact failure
that prompted the emergency fix. The fix is incomplete.

**Concrete fix:**

```python
# In ALL_CHECKS, add after liquid_glass_class_present (line ~4482):
    tailwind_directives_present,
```

Also: add a test to `tests/test_evals.py` (no test exists for this check — confirmed
by searching `tests/` for `tailwind_directives`).

**Recommended new eval check:** Already written — just wire it into ALL_CHECKS.

---

### C2 — `globals.css` import in `layout.tsx` is not eval-verified

**File:** `skills/prompt_template.md` line 267 (`import "./globals.css";` shown in
layout.tsx sample), `pebble/evals/checks.py` (no check for this import exists).

**Why the LLM might skip it:** The prompt says Inter is imported and applied "in
`app/layout.tsx`" but does not pin `import "./globals.css"` as a mandatory standalone
requirement with its own checklist item. Under token pressure, the LLM may emit
`layout.tsx` without the CSS import, treating it as an "obvious" side-effect of the
globals.css file existing.

**Failure mode:** `globals.css` exists and passes all CSS-content checks. Tailwind
directives are present. But `layout.tsx` never imports the file, so the Next.js CSS
pipeline never processes it. Zero styles applied. Identical symptom to the Tailwind
directives bug — plain HTML with browser defaults — but the CSS file itself is fine and
all current evals pass. Completely invisible.

**Concrete fix (eval skeleton):**

```python
@check_metadata(static_files=("app/layout.tsx",))
def globals_css_imported_in_layout(ctx: BuildContext) -> CheckResult:
    """app/layout.tsx must import ./globals.css.

    Without this import, Next.js never processes the globals.css file —
    Tailwind directives, CSS tokens, and .liquid-glass all disappear even
    though the file exists and passes content checks. Same severity as the
    Tailwind directives bug (renders as plain HTML with browser defaults).
    """
    if not ctx.site_dir.exists():
        return CheckResult("globals_css_imported_in_layout", "skip", "no site directory")
    layout = ctx.site_dir / "app" / "layout.tsx"
    if not layout.exists():
        return CheckResult("globals_css_imported_in_layout", "fail", "app/layout.tsx missing")
    text = layout.read_text(encoding="utf-8", errors="ignore")
    if re.search(r"""import\s+['"]\./globals\.css['"]""", text):
        return CheckResult("globals_css_imported_in_layout", "pass",
                           "import './globals.css' found in app/layout.tsx")
    return CheckResult(
        "globals_css_imported_in_layout", "fail",
        "app/layout.tsx is missing `import './globals.css'` — "
        "without it Next.js never processes the CSS file and all styles disappear.",
    )
```

Add to ALL_CHECKS after `tailwind_directives_present`. Add to checklist in
`prompt_template.md` Section 11 required files list with an explicit callout line:
`import "./globals.css";` // MANDATORY — omitting this line removes ALL CSS from the site.

---

### C3 — `required_files_present` checks for `postcss.config.js`, prompt mandates `postcss.config.mjs`

**File:** `pebble/evals/checks.py` line 715 (`"postcss.config.js"` in `REQUIRED_FILES`).
**Prompt:** `skills/prompt_template.md` line 1189 explicitly states `postcss.config.mjs`
is **required** and `.js` will silently fail.

**Ground truth:** `output/indie-bookstore/site/postcss.config.mjs` exists (correct).
`output/coffee-shop-in-oakland/site/postcss.config.mjs` exists but uses
`module.exports` (CJS syntax in an `.mjs` file — broken at runtime). Neither build has
`postcss.config.js`.

**What this means:**
1. `required_files_present` reports `postcss.config.js` as missing on EVERY build
   (because the correct file is `.mjs`, not `.js`). This eval is permanently broken.
2. The coffee-shop build has a live bug: `postcss.config.mjs` with `module.exports`
   instead of `export default`. Node treats `.mjs` as ESM; `module.exports` is CJS.
   PostCSS will crash with "Your custom PostCSS configuration must export a `plugins`
   key" because the file exports nothing. Tailwind never runs. Plain HTML again.
3. No eval catches CJS-in-MJS content.

**Failure mode:** Tailwind utilities silently absent. Site renders as plain HTML.
The eval that should catch the missing file is permanently reporting a false positive
(checks wrong filename), so repair never runs.

**Concrete fix (two parts):**

Part 1 — fix `REQUIRED_FILES` in `checks.py`:
```python
# Change line 715 from:
    "postcss.config.js",
# To:
    "postcss.config.mjs",
```

Part 2 — add content check for PostCSS MJS shape:
```python
@check_metadata(static_files=("postcss.config.mjs",))
def postcss_config_is_esm(ctx: BuildContext) -> CheckResult:
    """postcss.config.mjs must use ESM export syntax, not CommonJS.

    Node treats .mjs as ESM. `module.exports = ...` in an .mjs file is a
    syntax error at runtime — PostCSS fails silently and Tailwind generates
    no utility classes. The correct shape is `export default { plugins: {...} }`.
    """
    if not ctx.site_dir.exists():
        return CheckResult("postcss_config_is_esm", "skip", "no site directory")
    mjs = ctx.site_dir / "postcss.config.mjs"
    if not mjs.exists():
        return CheckResult("postcss_config_is_esm", "fail",
                           "postcss.config.mjs missing")
    text = mjs.read_text(encoding="utf-8", errors="ignore")
    if re.search(r"\bmodule\.exports\s*=", text):
        return CheckResult(
            "postcss_config_is_esm", "fail",
            "postcss.config.mjs uses CommonJS `module.exports` — must use ESM "
            "`export default { plugins: { tailwindcss: {}, autoprefixer: {} } }`. "
            "Node throws on CommonJS in .mjs files.",
        )
    if "export default" not in text:
        return CheckResult(
            "postcss_config_is_esm", "fail",
            "postcss.config.mjs has no `export default` — PostCSS won't load it",
        )
    return CheckResult("postcss_config_is_esm", "pass",
                       "postcss.config.mjs uses ESM export default")
```

---

### C4 — `AnimatedHeading` aria-hidden structural bug evades the eval

**File:** `output/indie-bookstore/site/components/ui/AnimatedHeading.tsx` (ground-truth
LLM output, confirmed in this audit). `pebble/evals/checks.py` line 1306 eval
`animated_heading_screen_reader_safe`.

**The bug:** In the animated code path, the outer `<h1>` element carries
`aria-hidden="true"`. The `sr-only` span is nested *inside* that `aria-hidden="true"`
`<h1>`. The ARIA spec says `aria-hidden` hides the element AND its entire subtree from
the accessibility tree. Screen readers skip the `<h1>` entirely — no heading announced,
page has no perceivable title for AT users.

Confirmed from actual file (lines 24 and 44):
```tsx
<h1 className={className} aria-hidden="true">   // <-- hides EVERYTHING inside
  {/* ... animated chars ... */}
  <span className="sr-only">{text}</span>        // <-- never read by AT
</h1>
```

The correct pattern (from the prompt template spec):
```tsx
<h1 className={className}>
  <span className="sr-only">{text}</span>         // semantic text for AT
  <span aria-hidden="true">                        // decorative animation
    {/* ... per-char spans ... */}
  </span>
</h1>
```

**Why the eval misses it:** `animated_heading_screen_reader_safe` checks for the
PRESENCE of both strings (`sr-only` and `aria-hidden="true"`) in the file — but not
their structural relationship (which is a child of which). A file with
`aria-hidden="true"` on the `<h1>` and `sr-only` inside it passes the current eval.

**Failure mode:** Screen readers (VoiceOver, NVDA, JAWS) announce no page heading.
Keyboard and AT users perceive a blank page header. Lighthouse accessibility score
drops. Not a visual regression — completely invisible in visual testing.

**Concrete fix (eval update):**

```python
@check_metadata(static_files=("components/ui/AnimatedHeading.tsx",))
def animated_heading_screen_reader_safe(ctx: BuildContext) -> CheckResult:
    """AnimatedHeading must NOT put aria-hidden on the <h1> itself.

    The correct pattern: sr-only span is a SIBLING of the aria-hidden span,
    both children of the <h1>. The wrong pattern: aria-hidden on the <h1>
    hides everything inside including the sr-only text.

    Check: verify <h1> opening tag does NOT contain aria-hidden.
    """
    # ... existing boilerplate ...
    text = path.read_text(encoding="utf-8", errors="ignore")

    # Check: h1 must not carry aria-hidden itself
    H1_OPEN_RE = re.compile(r"<h1\b([^>]*)>", re.DOTALL)
    for m in H1_OPEN_RE.finditer(text):
        if "aria-hidden" in (m.group(1) or ""):
            return CheckResult(
                "animated_heading_screen_reader_safe", "fail",
                "AnimatedHeading has aria-hidden on the <h1> itself — this hides "
                "the sr-only text too. Put aria-hidden='true' on the inner char-span "
                "wrapper, not on the h1.",
            )
    # Then check that both markers exist (existing logic) ...
```

The prompt template should also add an explicit prohibition:
`<h1> itself must NEVER carry aria-hidden="true" — that hides its entire subtree including the sr-only text`.

---

## MEDIUM FINDINGS

---

### M1 — `hero_uses_background_video`, `no_dark_overlay_on_hero_video`, `hero_video_has_poster` are defined but not in ALL_CHECKS

**File:** `pebble/evals/checks.py` lines 985, 1027, 1506. NOT in ALL_CHECKS (confirmed
by exhaustive extraction of ALL_CHECKS list).

**Why it matters:** The prompt template (Section 2 / checklist) explicitly says NO
`<video>` in the hero for `gradient_mesh` layout, but these three evals *enforce the
opposite* — they fail a build that has no `<video autoPlay>`. These evals were written
for the old VEX-spec foundation where video was mandatory. They're now dead code (the
current template mandates CSS gradient mesh heroes with no video). Having them in dead
code is not an active problem. BUT: if someone wires them back into ALL_CHECKS without
reading the template, every build will permanently fail `hero_uses_background_video`.

The real medium risk: if a Layout DNA does specify a video-type hero (some non-gradient
DNA cards might), there's no eval to enforce that the video has a `poster` attribute
or `preload` attribute. `perf_budget_or_lighter` sub-check 4 catches the missing
`preload`, but only if `_VIDEO_OPEN_RE` finds a video in the hero files — which it
won't for gradient-mesh builds. This is a gap for video-based DNA layouts.

**Concrete fix:** Mark the three orphaned functions with a deprecation comment and
confirm they should never be wired into ALL_CHECKS for the current template. Then
conditionally add `hero_video_has_poster` to ALL_CHECKS with a layout-DNA awareness
skip (similar to `liquid_glass_class_present`'s `_NO_LIQUID_GLASS_LAYOUTS` pattern).

---

### M2 — `sitemap.ts` copy-pastes the template's fixed 7-route array instead of the build's actual pages

**File:** `skills/prompt_template.md` line 430 (example routes array), confirmed in
`output/indie-bookstore/site/app/sitemap.ts` (identical 7 hardcoded routes).

**The bug:** The template shows:
```ts
const routes = ["", "/about", "/services", "/contact", "/faq", "/privacy", "/terms"];
```
The instruction says "Replace the placeholder `routes` array with the actual pages the
build emits." But the LLM copies the example verbatim instead of expanding it for the
build's industry-specific pages (e.g. `/menu`, `/team`, `/booking`, `/gallery`). A
bookstore build with no `/menu` route still gets `/menu` in its sitemap (404s submitted
to Google), and its actual `/books` or `/events` page doesn't appear in the sitemap
(never indexed by Google/Perplexity/ClaudeBot).

**Why the LLM ignores the instruction:** The instruction appears inline in a comment
AFTER the code block: "Replace the placeholder routes array with the actual pages the
build emits." The LLM reads the code block literally and the comment disappears under
the context limit by the time it reaches sitemap.ts generation.

**Failure mode:** Wrong pages indexed, real industry pages invisible to search engines
and AI agents. `sitemap_and_robots_present` eval passes because it only checks for the
`export default function` presence, not route correctness.

**Recommended eval addition:**

```python
@check_metadata(static_files=("app/sitemap.ts",))
def sitemap_routes_match_plan(ctx: BuildContext) -> CheckResult:
    """app/sitemap.ts must include every route in plan.json.

    The LLM copies the template's 7-route example verbatim. Missing industry
    pages (e.g. /menu, /team, /booking) are never submitted to crawlers.
    """
    # Load plan.json, extract all routes, check each appears as a string
    # literal in sitemap.ts (same permissive approach as footer_lists_all_pages).
```

**Prompt fix:** Move the replace instruction BEFORE the code block and bold it:
`**IMPORTANT: the routes array below is an example — replace it with the actual routes
this build generates, matching the pages listed in INDUSTRY-AWARE PAGES above.**`

---

### M3 — GSAP `registerPlugin(ScrollTrigger)` at module scope in `lib/motion.ts` is safe, but the pattern is ambiguous

**File:** `skills/prompt_template.md` line 237. CLAUDE.md rule #3.

**What happens in practice:** The LLM correctly puts `ScrollTrigger.normalizeScroll`
and `.config` inside a function (confirmed: `output/indie-bookstore/site/lib/motion.ts`
lines 6-9 wrap them in `initScrollAnimations()`). BUT `gsap.registerPlugin(ScrollTrigger)`
is at module scope in `lib/motion.ts` — imported by client components.

The prompt says "at module scope". The CLAUDE.md rule says normalizeScroll and config
MUST be inside useEffect. The eval `scroll_trigger_ssr_safe` and `next_js_static_check`
only flag `.normalizeScroll` and `.config` — not `registerPlugin`.

Module-level `gsap.registerPlugin()` in a file imported only by `"use client"` components
is actually safe (no `window` access). But the LLM sometimes puts it directly in
component files that are NOT `"use client"`, which would crash SSR. The eval would
catch that case via `next_js_static_check`'s browser-global check, but only if GSAP's
`registerPlugin` accesses `window` — it might not during import.

**Risk:** Medium. The current eval coverage is adequate for the known failure mode. But
the prompt instruction creates a magnet for the LLM to write module-level calls in files
that aren't always client-only.

**Suggested prompt clarification:** Add: "Call `gsap.registerPlugin(ScrollTrigger)` at
module scope ONLY in files that have `"use client"` or are imported exclusively from
`"use client"` components (e.g. `lib/motion.ts`). Never call it in Server Components."

---

## LOW FINDINGS

---

### L1 — `animation_components_present` only verifies `AnimatedHeading` and `FadeIn`, not the other 4 mandatory UI components

**File:** `pebble/evals/checks.py` line 1205-1208.

The prompt's mandatory component list (Section 11) includes: `AnimatedHeading`,
`FadeIn`, `ScrollReveal`, `GlassCard`, `MagneticButton`, `SectionHeader`, and
`GrainOverlay`. The eval only checks `AnimatedHeading` and `FadeIn`. `ScrollReveal`,
`GlassCard`, `MagneticButton`, and `SectionHeader` have no presence check. If the LLM
drops any of them under token pressure, imports in other components will fail TypeScript
compile, but only `site_compiles` (which requires `node_modules` and `npx`) catches
that — it's skipped in most CI runs.

**Failure mode:** TypeScript compile errors. `site_compiles` catches this, but `site_compiles`
is the heaviest check and often skipped.

**Recommended eval extension:**

```python
expected = (
    "components/ui/AnimatedHeading.tsx",
    "components/ui/FadeIn.tsx",
    "components/ui/ScrollReveal.tsx",
    "components/ui/GlassCard.tsx",
    "components/ui/MagneticButton.tsx",
    "components/layout/Navbar.tsx",
    "components/layout/Footer.tsx",
    "components/sections/Hero.tsx",
    "components/forms/ContactForm.tsx",
)
```

---

### L2 — `sitemap.ts` example code copies placeholder URL `https://example.com`

**File:** `skills/prompt_template.md` line 427.

The template example has:
```ts
const base = process.env.NEXT_PUBLIC_SITE_URL || "https://example.com";
```

In practice, `NEXT_PUBLIC_SITE_URL` is almost never set in Pebble builds. Sitemap.xml
will contain `https://example.com/about` etc. for most production sites. Not a build-
breaking error (the site renders fine), but Google Search Console will reject the sitemap.

**Fix:** Change the fallback to something more obviously wrong:
```ts
const base = process.env.NEXT_PUBLIC_SITE_URL ?? (() => { throw new Error("Set NEXT_PUBLIC_SITE_URL in .env.local") })();
```
Or accept it as a known gap and add it to the README's `## What This Site Does NOT Include` section.

---

### L3 — `ScrollReveal.tsx` is in `client_components_have_directive` scope gap

**File:** `pebble/evals/checks.py` line 1230-1233.

`_REQUIRED_CLIENT_COMPONENTS` only checks: `AnimatedHeading.tsx`, `FadeIn.tsx`,
`ContactForm.tsx`. `ScrollReveal.tsx` and `MagneticButton.tsx` both use Framer Motion
hooks (`useInView`, `useSpring`) and need `"use client"`. If either is missing the
directive, Next.js crashes at runtime with "hooks cannot be called from a Server
Component". These are not in the current eval scope.

**Concrete fix:** Add to `_REQUIRED_CLIENT_COMPONENTS`:
```python
_REQUIRED_CLIENT_COMPONENTS = (
    "components/ui/AnimatedHeading.tsx",
    "components/ui/FadeIn.tsx",
    "components/ui/ScrollReveal.tsx",
    "components/ui/MagneticButton.tsx",
    "components/forms/ContactForm.tsx",
)
```

---

## WHAT IS WELL-PINNED

These instructions the LLM cannot reasonably misread, or are already caught by multiple
defense layers:

- **Tailwind directives ORDER**: The newly-fixed prompt now lists directives BEFORE the
  `:root {}` block. The wording is clear and unambiguous. (Once C1 is fixed — wiring
  the eval into ALL_CHECKS — this is fully protected.)
- **`next.config.mjs` as plain JS**: The prompt is explicit, `next_config_is_mjs` eval
  checks for it, CLAUDE.md rule #5 pins it. Three layers.
- **`tsconfig.json` paths**: `tsconfig_paths_alias` eval is specific and leaves no
  wiggle room.
- **`"use server"` in contact action**: `contact_form_uses_server_action` checks both
  file presence and directive. Well-protected.
- **`resend` in package.json**: `resend_in_dependencies` eval is specific.
- **`Inter` via next/font/google**: `inter_font_global` + `inter_font_applied` — two
  separate checks.
- **No 555 phones**: `no_invented_phone` is comprehensive and handles edge cases.
- **No invented time markers**: `no_invented_time_markers` is unusually thorough with
  5 regex patterns and both keyword-before and keyword-after forms.
- **`aria-label` on form inputs**: The eval `a11y_static_audit` checks `_input_label_violations`.
- **GSAP SplitText forbidden**: `no_gsap_split_text` eval is specific and correct.

---

## SUMMARY TABLE

| ID | Severity | File(s) | Fix size |
|----|----------|---------|----------|
| C1 | Critical | `checks.py` ALL_CHECKS + tests | 1 line + 1 test |
| C2 | Critical | `checks.py` new check + `prompt_template.md` | 20 lines + 1 prompt line |
| C3 | Critical | `checks.py` REQUIRED_FILES + new check | 2 lines + 20 lines |
| C4 | Critical | `checks.py` eval logic update + prompt note | 10 lines + 1 prompt line |
| M1 | Medium | `checks.py` dead-code comments | 3 lines comment |
| M2 | Medium | `prompt_template.md` + new eval | 3 prompt words + 15 lines |
| M3 | Medium | `prompt_template.md` clarification | 2 lines |
| L1 | Low | `checks.py` expand expected list | 7 lines |
| L2 | Low | `prompt_template.md` fallback URL | 1 line |
| L3 | Low | `checks.py` expand _REQUIRED_CLIENT_COMPONENTS | 2 lines |

---

*Audit by Claude Sonnet 4.6 · 2026-05-23 · worktree bold-hopper-c3631f*
