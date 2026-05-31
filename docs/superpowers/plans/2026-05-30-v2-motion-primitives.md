# v2 Motion Primitives + Block Retrofit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every v2-generated site a curated, edit-safe motion layer — the 10 lab-proven primitives written into each project, then the 49 blocks retrofitted to compose them — without reopening the LLM-freestyle failure mode.

**Architecture:** Motion primitives are pre-built, tested React components stored in `pebble/blocks/motion/` and copied verbatim into every generated site's `components/motion/` by the compiler (same mechanism as scaffolding). Blocks import and wrap their elements in these primitives. The LLM never writes motion code. Builds on the section-files refactor (sub-project A) so blocks can be `"use client"` components with hooks.

**Tech Stack:** Framer Motion (primary, SSR-safe, reduced-motion built in), GSAP (one pinned-scroll primitive only), Next.js 14, Tailwind.

**Scope split:**
- **B1 (this session):** primitives library + compiler wiring + generated-package.json deps. Self-contained, testable.
- **B2 (fresh session, parallel subagents):** retrofit all 49 blocks, one subagent per vibe.
- **B3:** live validation build.

---

## Edit-safety contract (every primitive MUST obey)

From the committed spec (`2026-05-30-pebble-v2-motion-and-layout-variety-design.md`):
1. `"use client"` is line 1.
2. `prefers-reduced-motion` honored via `useReducedMotion()` — falls back to a static render.
3. No hardcoded colors — visual styling comes from children / Tailwind classes passed in.
4. Forward `...rest` props (incl. `data-pebble-id`, `className`) onto the **editable child/root**, never the decorative wrapper, so the click-to-edit manifest still targets real elements.
5. `RevealWords` / `CountUp` take editable content as a **single plain-string child**, so the text-edit verbatim check still matches against source.

## File Structure

- **Create** `pebble/blocks/motion/*.tsx` — the primitive source files (one per primitive).
- **Modify** `pebble/blocks_compiler.py` — add `_write_motion_library(out_dir)`, call it in `_write_scaffolding`; add framer-motion + gsap to `_PACKAGE_JSON`.
- **Create** `tests/test_motion_library.py` — assert the compiler writes the motion library + deps.
- **B2 only:** modify the 49 `pebble/blocks/library/*.tsx` files.

---

### Task B1.1: Create the motion primitives source directory

**Files:**
- Create: `pebble/blocks/motion/FadeUp.tsx`, `Stagger.tsx`, `RevealWords.tsx`, `Parallax.tsx`, `CountUp.tsx`, `Masonry.tsx`, `DragCarousel.tsx`, `Marquee.tsx`, `TiltCard.tsx`, `MagneticButton.tsx`, `StickyStory.tsx`

- [ ] **Step 1: Create `FadeUp.tsx`** (representative edit-safe pattern — note `...rest` spread + reduced-motion)

```tsx
"use client";
import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

export default function FadeUp({ children, className, ...rest }: { children: ReactNode; className?: string; [k: string]: unknown }) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      className={className}
      initial={reduce ? false : { opacity: 0, y: 32 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      {...rest}
    >
      {children}
    </motion.div>
  );
}
```

- [ ] **Step 2: Create `Stagger.tsx`** (parent + item; item forwards rest)

```tsx
"use client";
import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

export function Stagger({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <motion.div
      className={className}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.2 }}
      variants={{ show: { transition: { staggerChildren: 0.12 } } }}
    >
      {children}
    </motion.div>
  );
}

export function StaggerItem({ children, className, ...rest }: { children: ReactNode; className?: string; [k: string]: unknown }) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      className={className}
      variants={reduce ? undefined : {
        hidden: { opacity: 0, y: 40 },
        show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } },
      }}
      {...rest}
    >
      {children}
    </motion.div>
  );
}

export default Stagger;
```

- [ ] **Step 3: Create `RevealWords.tsx`** (edit-safe: single string child, id on root)

```tsx
"use client";
import { motion, useReducedMotion } from "framer-motion";

export default function RevealWords({ children, className, ...rest }: { children: string; className?: string; [k: string]: unknown }) {
  const reduce = useReducedMotion();
  const text = typeof children === "string" ? children : "";
  if (reduce) return <span className={className} {...rest}>{text}</span>;
  return (
    <span className={className} {...rest}>
      {text.split(" ").map((w, i) => (
        <motion.span
          key={i}
          className="mr-[0.25em] inline-block"
          initial={{ opacity: 0, y: 24, filter: "blur(6px)" }}
          whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          viewport={{ once: true }}
          transition={{ delay: 0.06 * i, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        >
          {w}
        </motion.span>
      ))}
    </span>
  );
}
```

- [ ] **Step 4: Create `Parallax.tsx`**

```tsx
"use client";
import { useRef } from "react";
import { motion, useScroll, useTransform, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

export default function Parallax({ children, className, distance = 60 }: { children: ReactNode; className?: string; distance?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], [distance, -distance]);
  return (
    <div ref={ref} className={className}>
      <motion.div style={{ y: reduce ? 0 : y }}>{children}</motion.div>
    </div>
  );
}
```

- [ ] **Step 5: Create `CountUp.tsx`** (edit-safe: plain numeric child)

```tsx
"use client";
import { useEffect, useRef, useState } from "react";
import { useInView, useReducedMotion, animate } from "framer-motion";

export default function CountUp({ children, className, suffix = "", ...rest }: { children: number | string; className?: string; suffix?: string; [k: string]: unknown }) {
  const to = typeof children === "number" ? children : parseInt(String(children).replace(/\D/g, ""), 10) || 0;
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  const reduce = useReducedMotion();
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!inView) return;
    if (reduce) { setVal(to); return; }
    const c = animate(0, to, { duration: 1.6, ease: "easeOut", onUpdate: (v) => setVal(Math.round(v)) });
    return () => c.stop();
  }, [inView, to, reduce]);
  return <span ref={ref} className={className} {...rest}>{val.toLocaleString()}{suffix}</span>;
}
```

- [ ] **Step 6: Create `Masonry.tsx`, `DragCarousel.tsx`, `Marquee.tsx`, `TiltCard.tsx`, `MagneticButton.tsx`**

Extract the cleaned, reduced-motion-guarded versions from the proven lab at
`output/_motion_lab/site/app/page.tsx` (sections #5, #6, #7, #8, #10). Apply the same edit-safety
contract: `"use client"` line 1, `useReducedMotion()` fallback, `...rest` spread onto the editable
root, no hardcoded colors (accept `className`).

- [ ] **Step 7: Create `StickyStory.tsx`** (the ONE GSAP-or-Framer pinned primitive)

Use the Framer `useScroll`-progress version from lab section #4 (no GSAP needed — keeps deps lighter).
GSAP stays out of B1 unless a later block genuinely needs ScrollTrigger pinning; if added, follow
CLAUDE.md rules (register in `useEffect`, `gsap/dist/ScrollTrigger`, never `SplitText`).

- [ ] **Step 8: Commit**

```bash
git add pebble/blocks/motion/
git commit -m "feat(motion): add edit-safe motion primitives library source"
```

---

### Task B1.2: Compiler writes the motion library + framer-motion dep

**Files:**
- Modify: `pebble/blocks_compiler.py`
- Test: `tests/test_motion_library.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_motion_library.py
import json
from pathlib import Path
from pebble.blocks_compiler import _write_scaffolding


def test_scaffolding_writes_motion_library(tmp_path: Path):
    _write_scaffolding(tmp_path)
    motion_dir = tmp_path / "components" / "motion"
    assert (motion_dir / "FadeUp.tsx").exists()
    assert (motion_dir / "RevealWords.tsx").exists()
    assert (motion_dir / "Parallax.tsx").exists()
    # primitives are client components
    assert (motion_dir / "FadeUp.tsx").read_text(encoding="utf-8").splitlines()[0] == '"use client";'


def test_scaffolding_package_json_includes_framer_motion(tmp_path: Path):
    _write_scaffolding(tmp_path)
    pkg = json.loads((tmp_path / "package.json").read_text(encoding="utf-8"))
    assert "framer-motion" in pkg["dependencies"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_motion_library.py -q`
Expected: FAIL — no `components/motion/` written; `framer-motion` not in deps.

- [ ] **Step 3: Add `framer-motion` to `_PACKAGE_JSON`** in `pebble/blocks_compiler.py`

In the `_PACKAGE_JSON` `"dependencies"` block, add `"framer-motion": "^11.3.8"` after `react-dom`.

- [ ] **Step 4: Add `_write_motion_library` and call it from `_write_scaffolding`**

```python
# pebble/blocks_compiler.py  (near _write_scaffolding)
_MOTION_SRC_DIR = Path(__file__).parent / "blocks" / "motion"


def _write_motion_library(out_dir: Path) -> None:
    """Copy the curated motion primitives into the generated site's
    components/motion/ directory (verbatim, like scaffolding)."""
    dest = out_dir / "components" / "motion"
    dest.mkdir(parents=True, exist_ok=True)
    for src in sorted(_MOTION_SRC_DIR.glob("*.tsx")):
        dest_file = dest / src.name
        dest_file.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
```

Then add `_write_motion_library(out_dir)` at the end of `_write_scaffolding`.

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_motion_library.py -q`
Expected: PASS (2 passed)

- [ ] **Step 6: Run compiler suite (no regressions)**

Run: `python -m pytest tests/test_blocks_compiler.py tests/test_blocks_compiler_sections.py tests/test_build_v2_e2e.py -q`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add pebble/blocks_compiler.py tests/test_motion_library.py
git commit -m "feat(compiler): write motion library + framer-motion dep into every site"
```

---

### Task B2: Retrofit the 49 blocks (FRESH SESSION — parallel subagents)

**Approach:** one subagent per vibe (warm-craft, clean-trust, bold-energetic, editorial-minimal,
appetizing-rich, luxurious-spa, playful-illustrated). Each retrofits its ~7 blocks to import from
`@/components/motion/*` and wrap key elements, obeying the edit-safety contract.

**The wrapping pattern (worked example — hero):**

```tsx
// before
<h1 className="text-{{fg}} text-6xl font-bold">{{headline}}</h1>
<Image src="{{hero_image}}" fill className="object-cover" />

// after
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";
// ...
<h1 className="text-{{fg}} text-6xl font-bold"><RevealWords>{{headline}}</RevealWords></h1>
<Parallax className="absolute inset-0"><Image src="{{hero_image}}" fill className="object-cover" /></Parallax>
```

Per-vibe subagent instructions: wrap headlines in `RevealWords`, service/feature grids in
`Stagger`+`StaggerItem`, stat numbers in `CountUp`, primary CTAs in `MagneticButton`, gallery images
in `Masonry`/`DragCarousel`, hero images in `Parallax`. Add `"use client";` to each retrofitted
block (compiler hoists it). Keep every `{{slot}}` exactly as-is — motion wraps, never replaces, slots.

**Verification per vibe:** `python -m pytest tests/test_blocks_<vibe>.py -q` still green (slots intact),
then compile one site of that vibe and confirm no `{{...}}` leaks.

---

### Task B3: Live validation build

- [ ] Compile one motion site per vibe via the real registry, `npm install`, `next dev`, curl 200,
      confirm no `Module not found` (motion imports resolve), no `{{...}}` leaks, and — critically —
      a click-to-edit text op on a `RevealWords` headline still succeeds (edit-safety regression).

---

## Self-Review

**Spec coverage:** primitives library (B1.1) ✅; compiler writes them (B1.2) ✅; framer-motion dep (B1.2) ✅;
blocks compose primitives (B2) ✅; edit-safety contract stated + enforced in every primitive ✅;
GSAP contained to at most one primitive ✅. New block types (gallery/scroll-story) are a *separate*
plan — not here (this plan is motion-on-existing-blocks).

**Placeholder scan:** B1 tasks carry full component source or a precise extraction pointer
(`output/_motion_lab/site/app/page.tsx` sections) — no vague "add animation" steps. B2 gives the exact
wrapping pattern + a worked hero example; remaining blocks follow the same mechanical pattern.

**Type consistency:** every primitive default-exports (except `Stagger` which also named-exports
`StaggerItem`); all accept `className` + `...rest`; `RevealWords`/`CountUp` take a single child.
Compiler helper `_write_motion_library(out_dir: Path) -> None` matches `_write_scaffolding` style.
