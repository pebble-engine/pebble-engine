"""Individual checks that grade a generated build.

Each check function takes a :class:`BuildContext` and returns a
:class:`CheckResult`. Conventions:

- Function name is the stable check identifier (used in reports + tests).
- Docstring explains what's being verified and *why* — the why matters
  more than the what, because a future maintainer wondering whether to
  delete or relax the check needs the rationale.
- Missing prerequisites (no site dir, no brief) → ``skip``, never crash.
- Add a new check: write it here, append to ``ALL_CHECKS`` at the bottom,
  and add a test in ``tests/test_evals.py``.

The checks are deliberately *cheap* except for ``site_compiles`` (which
shells out to ``npx tsc``). The rest are static reads — running the full
suite (minus tsc) on a build should be milliseconds.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from pebble.evals.runner import BuildContext, CheckResult


# ---------------------------------------------------------------------------
# 1. site_compiles
# ---------------------------------------------------------------------------

def site_compiles(ctx: BuildContext) -> CheckResult:
    """``npx tsc --noEmit`` on the generated site.

    This is the heaviest check (10-30s). It's the only one that catches
    a whole class of LLM bugs — wrong type signatures, missing imports,
    unresolved ``@/`` paths — that look fine to a regex but kill the build.
    Skipped if ``node_modules`` isn't installed (the user can run with
    ``--skip-compile`` to bypass, or install deps first).
    """
    if not ctx.site_dir.exists():
        return CheckResult("site_compiles", "skip", "no site directory")
    if not (ctx.site_dir / "package.json").exists():
        return CheckResult("site_compiles", "skip", "no package.json")
    if not (ctx.site_dir / "node_modules").exists():
        return CheckResult(
            "site_compiles", "skip",
            "node_modules not installed (run `npm install` in the site dir)",
        )

    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit"],
            cwd=ctx.site_dir,
            capture_output=True,
            text=True,
            timeout=180,
            shell=(sys.platform == "win32"),
        )
    except subprocess.TimeoutExpired:
        return CheckResult("site_compiles", "error", "tsc timed out (>180s)")
    except FileNotFoundError:
        return CheckResult("site_compiles", "skip", "npx not on PATH")

    if result.returncode == 0:
        return CheckResult("site_compiles", "pass", "tsc clean")

    # tsc writes errors to stdout. Count the "error TS" lines so the
    # message stays human-readable; stash the first few in details.
    out = result.stdout + result.stderr
    err_lines = [l for l in out.splitlines() if "error TS" in l]
    return CheckResult(
        "site_compiles",
        "fail",
        f"{len(err_lines)} TypeScript error(s)",
        details={"first_errors": err_lines[:5]},
    )


# ---------------------------------------------------------------------------
# 2. no_src_directory
# ---------------------------------------------------------------------------

def no_src_directory(ctx: BuildContext) -> CheckResult:
    """Section 11 of the prompt template forbids ``site/src/``.

    ``tsconfig.json`` has ``"paths": { "@/*": ["./*"] }`` rooted at the
    project. If files live under ``src/``, imports written as
    ``@/components/Foo`` won't resolve and the build dies at compile time.
    The whole 2026-05 prompt rewrite was driven by this regression — keep
    the eval to catch any future drift.
    """
    if not ctx.site_dir.exists():
        return CheckResult("no_src_directory", "skip", "no site directory")
    if (ctx.site_dir / "src").exists():
        return CheckResult(
            "no_src_directory", "fail",
            "site/src/ exists — @/ imports won't resolve",
        )
    return CheckResult("no_src_directory", "pass", "files at project root")


# ---------------------------------------------------------------------------
# 3. hero_has_h1
# ---------------------------------------------------------------------------

def hero_has_h1(ctx: BuildContext) -> CheckResult:
    """The home page must render an ``<h1>``.

    CTAs alone aren't a hero (Stack skill rule). This catches a common
    LLM regression where the brief's headline gets replaced by a smaller
    heading element or a styled ``<div>`` and the page renders without
    a top-level title.
    """
    if not ctx.site_dir.exists():
        return CheckResult("hero_has_h1", "skip", "no site directory")
    page = ctx.site_dir / "app" / "page.tsx"
    if not page.exists():
        return CheckResult("hero_has_h1", "fail", "app/page.tsx missing entirely")

    text = page.read_text(encoding="utf-8", errors="ignore")
    if "<h1" in text:
        return CheckResult("hero_has_h1", "pass", "<h1> in app/page.tsx")

    # Hero usually lives in a component imported by page.tsx. Prefer files
    # whose name suggests "hero" so the report points at the real hero
    # rather than incidentally finding an h1 in a motion utility like
    # SplitText.tsx. Fall back to any *.tsx as a safety net.
    components_dir = ctx.site_dir / "components"
    if not components_dir.exists():
        return CheckResult(
            "hero_has_h1", "fail",
            "no <h1> in app/page.tsx; components/ doesn't exist",
        )

    candidates: list[Path] = []
    fallback: list[Path] = []
    for tsx in components_dir.rglob("*.tsx"):
        name_lc = tsx.name.lower()
        if "hero" in name_lc or "banner" in name_lc:
            candidates.append(tsx)
        else:
            fallback.append(tsx)

    for tsx in candidates + fallback:
        if "<h1" in tsx.read_text(encoding="utf-8", errors="ignore"):
            rel = tsx.relative_to(ctx.site_dir)
            return CheckResult("hero_has_h1", "pass", f"<h1> in {rel}")

    return CheckResult(
        "hero_has_h1", "fail",
        "no <h1> in app/page.tsx or any component",
    )


# ---------------------------------------------------------------------------
# 4. dna_display_font_honored
# ---------------------------------------------------------------------------

def dna_display_font_honored(ctx: BuildContext) -> CheckResult:
    """The DNA card's ``display_font`` must appear in the generated CSS/config.

    The Style DNA system is built on the premise that the LLM honors the
    fonts named in the injected block. When it ignores them and falls back
    to Inter/Fraunces, the build looks fine but the variety system is
    defeated. That's the WORST failure mode — silent regression on the
    project's core differentiator. This check is the only line of defense.
    """
    if not ctx.site_dir.exists():
        return CheckResult("dna_display_font_honored", "skip", "no site directory")
    dna_id = ctx.brief.get("_design_dna")
    if not dna_id:
        return CheckResult("dna_display_font_honored", "skip", "no DNA in brief")

    try:
        # style_dna lives at project root; sys.path is set up by pebble_engine
        # in normal runs. Import lazily so this check doesn't pull style_dna
        # at module-load time (keeps the eval suite importable without it).
        import style_dna  # type: ignore
    except Exception as e:
        return CheckResult(
            "dna_display_font_honored", "error",
            f"style_dna module not importable: {e}",
        )

    dna = style_dna.pick_dna_by_id(dna_id) if hasattr(style_dna, "pick_dna_by_id") else None
    if not dna:
        return CheckResult(
            "dna_display_font_honored", "skip",
            f"DNA id '{dna_id}' not found in style_dna.DNA_CARDS",
        )

    expected = (dna.get("display_font") or "").strip()
    if not expected:
        return CheckResult(
            "dna_display_font_honored", "skip",
            "DNA card has no display_font",
        )

    candidates = [
        ctx.site_dir / "app" / "globals.css",
        ctx.site_dir / "tailwind.config.ts",
        ctx.site_dir / "app" / "layout.tsx",
        ctx.site_dir / "config" / "brand.config.ts",
    ]
    # Match BOTH forms — direct CSS / @import / fontFamily strings use the
    # space-separated name ("Cormorant Garamond"), but `next/font/google`
    # exposes the same font as an underscore-separated import identifier
    # (`Cormorant_Garamond`). Either should satisfy the check.
    needles = {expected.lower(), expected.lower().replace(" ", "_")}
    for path in candidates:
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            for n in needles:
                if n in text:
                    return CheckResult(
                        "dna_display_font_honored", "pass",
                        f"display_font '{expected}' present in {path.relative_to(ctx.site_dir)}",
                    )

    return CheckResult(
        "dna_display_font_honored", "fail",
        f"DNA expected display_font '{expected}', not found in globals.css / tailwind.config.ts / layout.tsx / brand.config.ts",
        details={"expected_font": expected, "dna_id": dna_id},
    )


# ---------------------------------------------------------------------------
# 5. images_use_next_image
# ---------------------------------------------------------------------------

_RAW_IMG_RE = re.compile(r"<img\s")


def images_use_next_image(ctx: BuildContext) -> CheckResult:
    """Every image must go through ``next/image``, never raw ``<img>``.

    Stack skill rule — raw ``<img>`` defeats Next's optimization pipeline,
    breaks lazy-loading, and ships unoptimized bytes. Cheap to grep,
    high signal: this is the slop tell-tale.
    """
    if not ctx.site_dir.exists():
        return CheckResult("images_use_next_image", "skip", "no site directory")

    offenders: list[str] = []
    for tsx in ctx.site_dir.rglob("*.tsx"):
        if "node_modules" in tsx.parts:
            continue
        text = tsx.read_text(encoding="utf-8", errors="ignore")
        if _RAW_IMG_RE.search(text):
            offenders.append(str(tsx.relative_to(ctx.site_dir)))

    if not offenders:
        return CheckResult("images_use_next_image", "pass", "no raw <img> tags")
    return CheckResult(
        "images_use_next_image", "fail",
        f"{len(offenders)} file(s) use raw <img>",
        details={"files": offenders[:10]},
    )


# ---------------------------------------------------------------------------
# 6. no_invented_phone
# ---------------------------------------------------------------------------

_INVENTED_555 = re.compile(r"\b555[-.\s]\d{3}[-.\s]\d{4}\b")


def no_invented_phone(ctx: BuildContext) -> CheckResult:
    """Phone numbers in the output must be either the brief's phone or the
    ``[BUSINESS PHONE]`` placeholder — never a fabricated 555-XXX-XXXX.

    Anti-slop signal: a fabricated phone number is the canonical sign that
    the LLM filled placeholders by inventing instead of carrying through.
    Real businesses have real phones; missing data should stay missing
    (with a clear placeholder) until the owner fills it in.
    """
    if not ctx.site_dir.exists():
        return CheckResult("no_invented_phone", "skip", "no site directory")

    brief_phone = (ctx.brief.get("phone") or "").strip()
    found_brief_phone = False
    found_placeholder = False
    invented_files: list[str] = []

    for ext in ("*.tsx", "*.ts"):
        for f in ctx.site_dir.rglob(ext):
            if "node_modules" in f.parts:
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
            if brief_phone and brief_phone in text:
                found_brief_phone = True
            if "[BUSINESS PHONE]" in text:
                found_placeholder = True
            if _INVENTED_555.search(text):
                invented_files.append(str(f.relative_to(ctx.site_dir)))

    if invented_files:
        return CheckResult(
            "no_invented_phone", "fail",
            f"invented 555-XXX-XXXX number in {len(invented_files)} file(s)",
            details={"files": invented_files[:10]},
        )

    if brief_phone:
        if found_brief_phone:
            return CheckResult(
                "no_invented_phone", "pass",
                f"brief phone '{brief_phone}' present in site",
            )
        return CheckResult(
            "no_invented_phone", "fail",
            f"brief had phone '{brief_phone}' but it's not in any tsx/ts file",
        )

    # No brief phone — placeholder should be visible
    if found_placeholder:
        return CheckResult(
            "no_invented_phone", "pass",
            "[BUSINESS PHONE] placeholder present (no brief phone)",
        )
    return CheckResult(
        "no_invented_phone", "fail",
        "no brief phone AND no [BUSINESS PHONE] placeholder",
    )


# ---------------------------------------------------------------------------
# 7. tsconfig_paths_alias
# ---------------------------------------------------------------------------

# Strip // line comments before json.loads — Next templates sometimes use JSONC.
_JSONC_COMMENT_RE = re.compile(r"//.*?$", re.MULTILINE)


def tsconfig_paths_alias(ctx: BuildContext) -> CheckResult:
    """``compilerOptions.paths`` must be exactly ``{ "@/*": ["./*"] }``.

    Any other value — ``["./src/*"]``, missing entirely, different key —
    breaks ``@/`` imports. The prompt template mandates this exact shape;
    drift here means the LLM ignored Section 11.
    """
    if not ctx.site_dir.exists():
        return CheckResult("tsconfig_paths_alias", "skip", "no site directory")
    path = ctx.site_dir / "tsconfig.json"
    if not path.exists():
        return CheckResult("tsconfig_paths_alias", "fail", "tsconfig.json missing")

    text = path.read_text(encoding="utf-8", errors="ignore")
    clean = _JSONC_COMMENT_RE.sub("", text)
    try:
        config = json.loads(clean)
    except json.JSONDecodeError as e:
        return CheckResult(
            "tsconfig_paths_alias", "fail",
            f"tsconfig.json is invalid JSON: {e}",
        )

    star = config.get("compilerOptions", {}).get("paths", {}).get("@/*")
    if star == ["./*"]:
        return CheckResult("tsconfig_paths_alias", "pass", '"@/*": ["./*"]')
    return CheckResult(
        "tsconfig_paths_alias", "fail",
        f'expected paths["@/*"] == ["./*"], got {star!r}',
        details={"got": star},
    )


# ---------------------------------------------------------------------------
# 8. next_config_is_mjs
# ---------------------------------------------------------------------------

def next_config_is_mjs(ctx: BuildContext) -> CheckResult:
    """``next.config`` must be ``.mjs``, not ``.ts`` or ``.js``.

    Next 14 doesn't support TypeScript config files. The Stack Skill
    locks ``.mjs`` because Next 14 also has subtle CJS/ESM issues with
    ``.js`` configs in some templates. ``.ts`` would prevent ``next dev``
    from starting at all.
    """
    if not ctx.site_dir.exists():
        return CheckResult("next_config_is_mjs", "skip", "no site directory")
    has_mjs = (ctx.site_dir / "next.config.mjs").exists()
    has_ts = (ctx.site_dir / "next.config.ts").exists()
    has_js = (ctx.site_dir / "next.config.js").exists()

    if has_ts:
        return CheckResult(
            "next_config_is_mjs", "fail",
            "next.config.ts exists (Next 14 doesn't support TS config)",
        )
    if has_mjs:
        return CheckResult("next_config_is_mjs", "pass", "next.config.mjs present")
    if has_js:
        return CheckResult(
            "next_config_is_mjs", "fail",
            "next.config.js exists; Stack Skill requires .mjs",
        )
    return CheckResult("next_config_is_mjs", "fail", "no next.config.* file at all")


# ---------------------------------------------------------------------------
# 9. uses_100dvh_not_100vh
# ---------------------------------------------------------------------------

_VH_RE = re.compile(r"\b100vh\b")


def uses_100dvh_not_100vh(ctx: BuildContext) -> CheckResult:
    """No ``100vh`` anywhere — must be ``100dvh``.

    100vh is a known iOS Safari bug magnet (URL bar pushes content off the
    fold). Stack Skill rule. Cheap to grep — checking ``.tsx``, ``.ts``,
    and ``.css`` covers Tailwind arbitrary values like ``h-[100vh]``
    and raw CSS alike.
    """
    if not ctx.site_dir.exists():
        return CheckResult("uses_100dvh_not_100vh", "skip", "no site directory")

    offenders: list[str] = []
    for ext in ("*.tsx", "*.ts", "*.css"):
        for f in ctx.site_dir.rglob(ext):
            if "node_modules" in f.parts:
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
            if _VH_RE.search(text):
                offenders.append(str(f.relative_to(ctx.site_dir)))

    if not offenders:
        return CheckResult("uses_100dvh_not_100vh", "pass", "no 100vh found")
    return CheckResult(
        "uses_100dvh_not_100vh", "fail",
        f"{len(offenders)} file(s) use 100vh (must be 100dvh)",
        details={"files": offenders[:10]},
    )


# ---------------------------------------------------------------------------
# 10. required_files_present
# ---------------------------------------------------------------------------

REQUIRED_FILES = (
    "package.json",
    "tsconfig.json",
    "tailwind.config.ts",
    "postcss.config.js",
    "next.config.mjs",
    "app/layout.tsx",
    "app/page.tsx",
    "app/globals.css",
    ".gitignore",
)


def required_files_present(ctx: BuildContext) -> CheckResult:
    """The minimum set of files a Next 14 + Tailwind project needs to run.

    The 2026-05-14 sentinel-hvac-e2e-2 build was missing ``app/page.tsx``
    entirely — the LLM hit its token cap and silently dropped the page.
    A site without page.tsx is dead on arrival; this check makes that
    failure mode loud instead of silent.
    """
    if not ctx.site_dir.exists():
        return CheckResult("required_files_present", "skip", "no site directory")

    missing = [f for f in REQUIRED_FILES if not (ctx.site_dir / f).exists()]
    if not missing:
        return CheckResult(
            "required_files_present", "pass",
            f"all {len(REQUIRED_FILES)} required files present",
        )
    return CheckResult(
        "required_files_present", "fail",
        f"{len(missing)} required file(s) missing",
        details={"missing": missing},
    )


# ---------------------------------------------------------------------------
# 11. html_lang_attr
# ---------------------------------------------------------------------------

_HTML_LANG_RE = re.compile(r"<html[^>]*\blang\s*=", re.IGNORECASE)


def html_lang_attr(ctx: BuildContext) -> CheckResult:
    """``<html lang="...">`` must be present in ``app/layout.tsx``.

    Accessibility baseline: screen readers and translators rely on the lang
    attribute. Lighthouse flags missing-lang as a critical a11y error.
    The LLM sometimes emits ``<html>`` bare when transcribing the layout —
    a one-character regression with real downstream consequences.
    """
    if not ctx.site_dir.exists():
        return CheckResult("html_lang_attr", "skip", "no site directory")
    layout = ctx.site_dir / "app" / "layout.tsx"
    if not layout.exists():
        return CheckResult("html_lang_attr", "fail", "app/layout.tsx missing")

    text = layout.read_text(encoding="utf-8", errors="ignore")
    if _HTML_LANG_RE.search(text):
        return CheckResult("html_lang_attr", "pass", '<html lang="..."> in app/layout.tsx')
    return CheckResult(
        "html_lang_attr", "fail",
        "<html> tag in app/layout.tsx has no lang attribute",
    )


# ---------------------------------------------------------------------------
# 12. images_have_alt
# ---------------------------------------------------------------------------

# Match an <Image .../> block start through its self-close or `>` so we can
# inspect just the attribute span. Multiline because Image opens often wrap.
_IMAGE_BLOCK_RE = re.compile(r"<Image\b[^>]*?/?>", re.DOTALL)
_ALT_ATTR_RE = re.compile(r"\balt\s*=")


def images_have_alt(ctx: BuildContext) -> CheckResult:
    """Every ``<Image .../>`` must include an ``alt=`` attribute.

    Anti-slop AND a11y signal. The LLM regularly emits next/image blocks
    with width/height/src but no alt — a missing alt is a Lighthouse-flagged
    a11y violation. Empty ``alt=""`` is acceptable (decorative images);
    only blocks with NO alt at all are flagged.
    """
    if not ctx.site_dir.exists():
        return CheckResult("images_have_alt", "skip", "no site directory")

    offenders: list[str] = []
    total_images = 0
    for tsx in ctx.site_dir.rglob("*.tsx"):
        if "node_modules" in tsx.parts:
            continue
        text = tsx.read_text(encoding="utf-8", errors="ignore")
        for block in _IMAGE_BLOCK_RE.findall(text):
            total_images += 1
            if not _ALT_ATTR_RE.search(block):
                offenders.append(str(tsx.relative_to(ctx.site_dir)))
                break  # one offender per file is enough for the report

    if total_images == 0:
        return CheckResult("images_have_alt", "pass", "no <Image> elements to check")
    if not offenders:
        return CheckResult("images_have_alt", "pass", f"all {total_images} <Image> blocks have alt=")
    return CheckResult(
        "images_have_alt", "fail",
        f"{len(offenders)} file(s) have <Image> blocks without alt=",
        details={"files": offenders[:10]},
    )


# ---------------------------------------------------------------------------
# 13. scroll_trigger_ssr_safe
# ---------------------------------------------------------------------------

# These two ScrollTrigger calls touch `window` and crash Next.js SSR if hit at
# module level. Per the build system prompt rule #5 they MUST be inside
# useEffect. We flag any occurrence that isn't preceded by a useEffect on its
# nearest-enclosing call site. Cheap heuristic: walk lines, track whether
# we're inside a useEffect block by counting braces after a `useEffect(` line.
_SSR_DANGEROUS_RE = re.compile(r"ScrollTrigger\.(?:normalizeScroll|config)\s*\(")


def scroll_trigger_ssr_safe(ctx: BuildContext) -> CheckResult:
    """``ScrollTrigger.normalizeScroll(...)`` and ``ScrollTrigger.config(...)``
    must be inside a ``useEffect`` block, never at module level.

    Both touch ``window`` synchronously. Next.js renders components on the
    server first; a module-level call crashes the build with
    ``ReferenceError: window is not defined``. The system prompt explicitly
    calls this out (rule #5) but LLMs still miss it. Cheap to detect:
    walk lines, track whether we're inside a useEffect block by brace depth.
    """
    if not ctx.site_dir.exists():
        return CheckResult("scroll_trigger_ssr_safe", "skip", "no site directory")

    offenders: list[str] = []
    for tsx in ctx.site_dir.rglob("*.tsx"):
        if "node_modules" in tsx.parts:
            continue
        text = tsx.read_text(encoding="utf-8", errors="ignore")
        if not _SSR_DANGEROUS_RE.search(text):
            continue

        # Crude scope tracker: once we see `useEffect(` we count braces until
        # depth returns to 0. The dangerous call is safe if it's hit while
        # depth > 0. Misses some edge cases (callbacks not via useEffect) but
        # the false-positive direction is conservative — we'd rather over-flag
        # a build-failure-class issue than under-flag.
        depth = 0
        in_effect = False
        for line in text.splitlines():
            if "useEffect(" in line:
                in_effect = True
            if in_effect:
                depth += line.count("{") - line.count("}")
                if depth <= 0:
                    in_effect = False
                    depth = 0
                    continue
            if _SSR_DANGEROUS_RE.search(line) and not in_effect:
                offenders.append(str(tsx.relative_to(ctx.site_dir)))
                break

    if not offenders:
        return CheckResult("scroll_trigger_ssr_safe", "pass",
                           "ScrollTrigger SSR-dangerous calls are inside useEffect")
    return CheckResult(
        "scroll_trigger_ssr_safe", "fail",
        f"{len(offenders)} file(s) call ScrollTrigger.normalizeScroll/config at module level",
        details={"files": offenders[:10]},
    )


# ---------------------------------------------------------------------------
# 14. no_css_smooth_scroll
# ---------------------------------------------------------------------------

_SMOOTH_SCROLL_RE = re.compile(r"scroll-behavior\s*:\s*smooth", re.IGNORECASE)


def no_css_smooth_scroll(ctx: BuildContext) -> CheckResult:
    """No ``scroll-behavior: smooth`` in any CSS — Lenis handles smooth scroll.

    Per Stack Skill: native CSS smooth scroll conflicts with Lenis and other
    JS scroll managers, produces janky double-easing on momentum scroll, and
    interacts badly with ScrollTrigger's scrub mode. Lenis is in the standard
    build; mixing native and JS smooth scroll is a regression.
    """
    if not ctx.site_dir.exists():
        return CheckResult("no_css_smooth_scroll", "skip", "no site directory")

    offenders: list[str] = []
    for ext in ("*.css", "*.tsx", "*.ts"):
        for f in ctx.site_dir.rglob(ext):
            if "node_modules" in f.parts:
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
            if _SMOOTH_SCROLL_RE.search(text):
                offenders.append(str(f.relative_to(ctx.site_dir)))

    if not offenders:
        return CheckResult("no_css_smooth_scroll", "pass", "no scroll-behavior: smooth found")
    return CheckResult(
        "no_css_smooth_scroll", "fail",
        f"{len(offenders)} file(s) declare scroll-behavior: smooth",
        details={"files": offenders[:10]},
    )


# ---------------------------------------------------------------------------
# Registry — order matters for report layout; site_compiles last because slow
# ---------------------------------------------------------------------------

ALL_CHECKS = [
    no_src_directory,
    required_files_present,
    tsconfig_paths_alias,
    next_config_is_mjs,
    hero_has_h1,
    dna_display_font_honored,
    images_use_next_image,
    images_have_alt,
    no_invented_phone,
    uses_100dvh_not_100vh,
    html_lang_attr,
    scroll_trigger_ssr_safe,
    no_css_smooth_scroll,
    site_compiles,
]
