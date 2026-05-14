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
# @check_metadata decorator
# ---------------------------------------------------------------------------

def check_metadata(static_files: tuple[str, ...] = (), details_file_key: str | None = None):
    """Attach repair-time file-hint metadata to a check function.

    A check declares HOW its failures map to source files, right next to the
    check itself. The repair loop reads these attributes via
    :func:`pebble.evals.check_file_hints` — eliminates the mapping-drift bug
    where a new check works in evals but silently degrades repair.

    Parameters
    ----------
    static_files:
        Paths the check inspects regardless of context — written into the
        repair prompt verbatim as "likely-responsible files". Use this when
        the failing file is always at the same location (e.g. ``app/layout.tsx``
        for ``html_lang_attr``).
    details_file_key:
        Name of the key in ``CheckResult.details`` that holds offender paths
        (e.g. ``"files"`` or ``"missing"``). If set, the repair loop reads
        ``details[details_file_key]`` at runtime — for checks where the
        offending paths are discovered during the check itself.

    A check with neither set is "structural" (e.g. ``no_src_directory``);
    repair falls back to a prose-only ACTION clause for those.
    """
    def wrap(fn):
        fn.static_files = tuple(static_files)
        fn.details_file_key = details_file_key
        return fn
    return wrap


# ---------------------------------------------------------------------------
# 1. site_compiles
# ---------------------------------------------------------------------------

@check_metadata(details_file_key="files")
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
    # Also extract just the file paths into details["files"] so repair
    # treats site_compiles uniformly with the other path-flagged checks.
    out = result.stdout + result.stderr
    err_lines = [l for l in out.splitlines() if "error TS" in l]
    files: list[str] = []
    for line in err_lines:
        head = line.split("(", 1)[0].strip()
        if head and head not in files:
            files.append(head)
    return CheckResult(
        "site_compiles",
        "fail",
        f"{len(err_lines)} TypeScript error(s)",
        details={"first_errors": err_lines[:5], "files": files[:10]},
    )


# ---------------------------------------------------------------------------
# 2. no_src_directory
# ---------------------------------------------------------------------------

@check_metadata()  # structural — repair handles via prose
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

@check_metadata(static_files=("app/page.tsx",))
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

@check_metadata(static_files=("app/globals.css", "tailwind.config.ts", "app/layout.tsx"))
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


@check_metadata(details_file_key="files")
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

# Fake-phone detection — two patterns the LLM should recognize and downgrade.
#
# (1) Area code 555:  "555-123-4567" — Hollywood fake style.
# (2) 555 exchange:   "(718) 555-0143" — real area code, but the middle
#                      three digits "555" mark the number as fake.
#                      The North American Numbering Plan reserves the
#                      555 exchange for fictional / test numbers; the
#                      LLM (correctly) recognizes these and downgrades
#                      to the [BUSINESS PHONE] placeholder.
_FAKE_AS_AREA_CODE = re.compile(r"\b555[-.\s]+\d{3}[-.\s]+\d{4}\b")
_FAKE_AS_EXCHANGE  = re.compile(r"\(?\d{3}\)?[-.\s]+555[-.\s]+\d{4}\b")


def _is_fake_phone(s: str) -> bool:
    """True if `s` contains a 555-marker fake phone in either common form."""
    if not s:
        return False
    return bool(_FAKE_AS_AREA_CODE.search(s) or _FAKE_AS_EXCHANGE.search(s))


@check_metadata(details_file_key="files")
def no_invented_phone(ctx: BuildContext) -> CheckResult:
    """Phone numbers in the output must be either the brief's phone or the
    ``[BUSINESS PHONE]`` placeholder — never a fabricated 555-style number.

    Anti-slop signal: a fabricated phone number is the canonical sign that
    the LLM filled placeholders by inventing instead of carrying through.
    Real businesses have real phones; missing data should stay missing
    (with a clear placeholder) until the owner fills it in.

    Edge case (fixed 2026-05-14): when the brief ITSELF contains a fake
    555-style phone (e.g. a tester pasted in "(718) 555-0143"), the LLM
    correctly recognizes the marker and downgrades to ``[BUSINESS PHONE]``.
    That's the right behavior — and now the check agrees.
    """
    if not ctx.site_dir.exists():
        return CheckResult("no_invented_phone", "skip", "no site directory")

    brief_phone = (ctx.brief.get("phone") or "").strip()
    brief_phone_is_fake = _is_fake_phone(brief_phone)
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
            # A 555-marker phone in the site is invented UNLESS it's literally
            # the brief's own (fake) phone passing through verbatim.
            if _is_fake_phone(text):
                if brief_phone and brief_phone in text:
                    continue  # brief's own fake phone passing through, not invented
                invented_files.append(str(f.relative_to(ctx.site_dir)))

    if invented_files:
        return CheckResult(
            "no_invented_phone", "fail",
            f"invented 555-style number in {len(invented_files)} file(s)",
            details={"files": invented_files[:10]},
        )

    if brief_phone:
        if found_brief_phone:
            return CheckResult(
                "no_invented_phone", "pass",
                f"brief phone '{brief_phone}' present in site",
            )
        # Fix for the false-positive that bit Bridgewater + Heron builds:
        # if the brief phone is itself fake (555 marker), the LLM is right
        # to downgrade to the placeholder.
        if brief_phone_is_fake and found_placeholder:
            return CheckResult(
                "no_invented_phone", "pass",
                f"brief phone '{brief_phone}' was fake (555 marker); "
                f"LLM correctly used [BUSINESS PHONE] placeholder",
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


@check_metadata(static_files=("tsconfig.json",))
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

@check_metadata(static_files=("next.config.mjs",))
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


@check_metadata(details_file_key="files")
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


@check_metadata(details_file_key="missing")
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


@check_metadata(static_files=("app/layout.tsx",))
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


@check_metadata(details_file_key="files")
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


@check_metadata(details_file_key="files")
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
# Strip comments BEFORE checking the body: LLMs commonly leave a comment in
# globals.css explaining the rule (e.g. "/* Never set scroll-behavior: smooth
# — Lenis handles scroll */"), and matching the comment text would be a
# self-defeating false positive. /* */ covers CSS and JSDoc; // covers JS line
# comments (harmless to strip from CSS since it's not valid CSS syntax).
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_COMMENT_RE = re.compile(r"//[^\n]*")


@check_metadata(details_file_key="files")
def no_css_smooth_scroll(ctx: BuildContext) -> CheckResult:
    """No actual ``scroll-behavior: smooth`` declaration — Lenis handles smooth scroll.

    Per Stack Skill: native CSS smooth scroll conflicts with Lenis and other
    JS scroll managers, produces janky double-easing on momentum scroll, and
    interacts badly with ScrollTrigger's scrub mode. Lenis is in the standard
    build; mixing native and JS smooth scroll is a regression.

    Comments are stripped before matching — see _BLOCK_COMMENT_RE rationale.
    Skips ``.next/`` build artifacts (next.js compiles globals.css there;
    if the source is clean the artifact will be too).
    """
    if not ctx.site_dir.exists():
        return CheckResult("no_css_smooth_scroll", "skip", "no site directory")

    offenders: list[str] = []
    for ext in ("*.css", "*.tsx", "*.ts"):
        for f in ctx.site_dir.rglob(ext):
            if "node_modules" in f.parts or ".next" in f.parts:
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
            stripped = _LINE_COMMENT_RE.sub("", _BLOCK_COMMENT_RE.sub("", text))
            if _SMOOTH_SCROLL_RE.search(stripped):
                offenders.append(str(f.relative_to(ctx.site_dir)))

    if not offenders:
        return CheckResult("no_css_smooth_scroll", "pass",
                           "no scroll-behavior: smooth declarations (comments ignored)")
    return CheckResult(
        "no_css_smooth_scroll", "fail",
        f"{len(offenders)} file(s) declare scroll-behavior: smooth",
        details={"files": offenders[:10]},
    )


# ---------------------------------------------------------------------------
# 15. hero_uses_background_video — FOUNDATION (May 2026 overhaul)
# ---------------------------------------------------------------------------

_VIDEO_TAG_RE = re.compile(
    r"<video\b[^>]*\bautoplay\b", re.IGNORECASE | re.DOTALL
)


@check_metadata(static_files=("components/sections/Hero.tsx", "app/page.tsx"))
def hero_uses_background_video(ctx: BuildContext) -> CheckResult:
    """The foundation hero MUST use a background `<video>` with autoplay.

    Every build matches the universal hero foundation — full-bleed video
    background, no overlay. A static-image hero is no longer accepted. The
    check looks for any `<video … autoPlay …>` in either app/page.tsx or
    components/sections/Hero.tsx.
    """
    if not ctx.site_dir.exists():
        return CheckResult("hero_uses_background_video", "skip", "no site directory")

    candidates = [
        ctx.site_dir / "app" / "page.tsx",
        ctx.site_dir / "components" / "sections" / "Hero.tsx",
    ]
    for path in candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if _VIDEO_TAG_RE.search(text):
            return CheckResult(
                "hero_uses_background_video", "pass",
                f"<video> with autoplay found in {path.relative_to(ctx.site_dir)}",
            )
    return CheckResult(
        "hero_uses_background_video", "fail",
        "no <video autoPlay> in app/page.tsx or components/sections/Hero.tsx",
    )


# ---------------------------------------------------------------------------
# 16. no_dark_overlay_on_hero_video — FOUNDATION
# ---------------------------------------------------------------------------

_DARK_OVERLAY_RE = re.compile(
    r"bg-black/\d|bg-gradient-to-\w+\s+from-black|mix-blend-(?:multiply|darken)|"
    r"bg-\[rgba\(0,?\s*0,?\s*0,?\s*0?\.[0-9]+\)\]",
    re.IGNORECASE,
)


@check_metadata(static_files=("components/sections/Hero.tsx", "app/page.tsx"))
def no_dark_overlay_on_hero_video(ctx: BuildContext) -> CheckResult:
    """The hero `<video>` must play raw — NO dark overlay layer above it.

    The foundation explicitly forbids `bg-black/40`, `bg-gradient-to-b from-black/...`,
    `mix-blend-multiply`, or `bg-[rgba(0,0,0,0.5)]` over the hero video. The
    Pexels video is expected to have inherent darkness/contrast where text sits.
    Comments stripped before matching — the LLM may explain the rule in prose.
    """
    if not ctx.site_dir.exists():
        return CheckResult("no_dark_overlay_on_hero_video", "skip", "no site directory")

    candidates = [
        ctx.site_dir / "app" / "page.tsx",
        ctx.site_dir / "components" / "sections" / "Hero.tsx",
    ]
    hero_text = ""
    found_in: Path | None = None
    for path in candidates:
        if path.exists() and _VIDEO_TAG_RE.search(path.read_text(encoding="utf-8", errors="ignore")):
            hero_text = path.read_text(encoding="utf-8", errors="ignore")
            found_in = path
            break

    if not hero_text:
        return CheckResult("no_dark_overlay_on_hero_video", "skip", "no hero video to inspect")

    stripped = _LINE_COMMENT_RE.sub("", _BLOCK_COMMENT_RE.sub("", hero_text))
    m = _DARK_OVERLAY_RE.search(stripped)
    if m:
        return CheckResult(
            "no_dark_overlay_on_hero_video", "fail",
            f"dark overlay pattern '{m.group(0)}' in {found_in.relative_to(ctx.site_dir)}",
            details={"files": [str(found_in.relative_to(ctx.site_dir))]},
        )
    return CheckResult(
        "no_dark_overlay_on_hero_video", "pass",
        "no dark overlay patterns over the hero video",
    )


# ---------------------------------------------------------------------------
# 17. inter_font_global — FOUNDATION
# ---------------------------------------------------------------------------

_INTER_FROM_NEXT_FONT_RE = re.compile(
    r"import\s*\{[^}]*\bInter\b[^}]*\}\s*from\s*['\"]next/font/google['\"]"
)


@check_metadata(static_files=("app/layout.tsx",))
def inter_font_global(ctx: BuildContext) -> CheckResult:
    """`Inter` must be imported from `next/font/google` in app/layout.tsx.

    The foundation mandates Inter as the universal sans-serif. The DNA's
    display_font is reserved for ACCENT/decorative use — never the hero h1.
    """
    if not ctx.site_dir.exists():
        return CheckResult("inter_font_global", "skip", "no site directory")
    layout = ctx.site_dir / "app" / "layout.tsx"
    if not layout.exists():
        return CheckResult("inter_font_global", "fail", "app/layout.tsx missing")

    text = layout.read_text(encoding="utf-8", errors="ignore")
    if not _INTER_FROM_NEXT_FONT_RE.search(text):
        return CheckResult(
            "inter_font_global", "fail",
            "Inter not imported from next/font/google in app/layout.tsx",
        )
    if "inter" not in text.lower() or ("classname" not in text.lower() and "variable" not in text.lower()):
        return CheckResult(
            "inter_font_global", "fail",
            "Inter imported but not applied via className/variable in app/layout.tsx",
        )
    return CheckResult("inter_font_global", "pass",
                       "Inter imported and applied in app/layout.tsx")


# ---------------------------------------------------------------------------
# 18. liquid_glass_class_present — FOUNDATION
# ---------------------------------------------------------------------------

_LIQUID_GLASS_CLASS_RE = re.compile(
    r"\.liquid-glass\s*\{[^}]*backdrop-filter\s*:\s*blur",
    re.IGNORECASE | re.DOTALL,
)


@check_metadata(static_files=("app/globals.css",))
def liquid_glass_class_present(ctx: BuildContext) -> CheckResult:
    """`.liquid-glass` class with `backdrop-filter: blur(...)` must exist in
    `app/globals.css`. The class is used by the navbar chip, the hero's
    right-column tag, the secondary CTA, and other premium-glass surfaces.
    """
    if not ctx.site_dir.exists():
        return CheckResult("liquid_glass_class_present", "skip", "no site directory")
    css_path = ctx.site_dir / "app" / "globals.css"
    if not css_path.exists():
        return CheckResult("liquid_glass_class_present", "fail", "app/globals.css missing")

    text = css_path.read_text(encoding="utf-8", errors="ignore")
    if _LIQUID_GLASS_CLASS_RE.search(text):
        return CheckResult("liquid_glass_class_present", "pass",
                           ".liquid-glass with backdrop-filter found in globals.css")
    return CheckResult(
        "liquid_glass_class_present", "fail",
        ".liquid-glass with backdrop-filter blur(...) not found in app/globals.css",
    )


# ---------------------------------------------------------------------------
# 19. animation_components_present — FOUNDATION
# ---------------------------------------------------------------------------

@check_metadata(static_files=("components/ui/AnimatedHeading.tsx", "components/ui/FadeIn.tsx"))
def animation_components_present(ctx: BuildContext) -> CheckResult:
    """Both `components/ui/AnimatedHeading.tsx` and `components/ui/FadeIn.tsx`
    must exist. They're the foundation's hero entrance primitives — the
    hero h1 uses AnimatedHeading; the subhead/CTAs/right-tag each wrap in FadeIn.
    """
    if not ctx.site_dir.exists():
        return CheckResult("animation_components_present", "skip", "no site directory")

    expected = (
        "components/ui/AnimatedHeading.tsx",
        "components/ui/FadeIn.tsx",
    )
    missing = [p for p in expected if not (ctx.site_dir / p).exists()]
    if not missing:
        return CheckResult("animation_components_present", "pass",
                           "AnimatedHeading + FadeIn components present")
    return CheckResult(
        "animation_components_present", "fail",
        f"missing foundation component(s): {', '.join(missing)}",
        details={"missing": list(missing)},
    )


# ---------------------------------------------------------------------------
# 20. prefers_reduced_motion_respected — FOUNDATION
# ---------------------------------------------------------------------------

_PREFERS_REDUCED_MOTION_RE = re.compile(
    r"@media\s*\([^)]*prefers-reduced-motion\s*:\s*reduce", re.IGNORECASE
)


@check_metadata(static_files=("app/globals.css",))
def prefers_reduced_motion_respected(ctx: BuildContext) -> CheckResult:
    """`app/globals.css` must contain a `@media (prefers-reduced-motion: reduce)`
    rule that disables transitions/animations. Accessibility baseline — the
    foundation's AnimatedHeading + FadeIn handle reduced-motion in JS too,
    but the CSS rule is the catch-all for all other animated elements.
    """
    if not ctx.site_dir.exists():
        return CheckResult("prefers_reduced_motion_respected", "skip", "no site directory")
    css_path = ctx.site_dir / "app" / "globals.css"
    if not css_path.exists():
        return CheckResult("prefers_reduced_motion_respected", "fail", "app/globals.css missing")

    text = css_path.read_text(encoding="utf-8", errors="ignore")
    if _PREFERS_REDUCED_MOTION_RE.search(text):
        return CheckResult("prefers_reduced_motion_respected", "pass",
                           "prefers-reduced-motion media query found in globals.css")
    return CheckResult(
        "prefers_reduced_motion_respected", "fail",
        "no @media (prefers-reduced-motion: reduce) rule in app/globals.css",
    )


# ---------------------------------------------------------------------------
# 21. animated_heading_screen_reader_safe — FOUNDATION
# ---------------------------------------------------------------------------

_SR_ONLY_RE = re.compile(r'className\s*=\s*["\']sr-only["\']')
_ARIA_HIDDEN_TRUE_RE = re.compile(r'aria-hidden\s*=\s*(?:\{?\s*["\']?true["\']?\s*\}?|"true"|\'true\')')


@check_metadata(static_files=("components/ui/AnimatedHeading.tsx",))
def animated_heading_screen_reader_safe(ctx: BuildContext) -> CheckResult:
    """`AnimatedHeading.tsx` must split semantics from decoration.

    The per-character animation pollutes the accessibility tree — without an
    explicit split, screen readers announce "Design" as "D... e... s... i...
    g... n", which is the canonical a11y antipattern for headline animations.

    Foundation contract: inside the `<h1>`, render the full text once in a
    `<span className="sr-only">` (semantic content for assistive technologies)
    and put the per-character animation in a sibling `<span aria-hidden="true">`
    so it does not contribute to the AT tree. Both markers must be present
    in this file.
    """
    if not ctx.site_dir.exists():
        return CheckResult("animated_heading_screen_reader_safe", "skip", "no site directory")
    path = ctx.site_dir / "components" / "ui" / "AnimatedHeading.tsx"
    if not path.exists():
        return CheckResult(
            "animated_heading_screen_reader_safe", "fail",
            "components/ui/AnimatedHeading.tsx is missing",
        )

    text = path.read_text(encoding="utf-8", errors="ignore")
    # Strip comments so explanatory prose doesn't false-positive the markers.
    stripped = _LINE_COMMENT_RE.sub("", _BLOCK_COMMENT_RE.sub("", text))
    has_sr_only = bool(_SR_ONLY_RE.search(stripped))
    has_aria_hidden = bool(_ARIA_HIDDEN_TRUE_RE.search(stripped))

    if has_sr_only and has_aria_hidden:
        return CheckResult(
            "animated_heading_screen_reader_safe", "pass",
            "AnimatedHeading wraps decoration in aria-hidden + exposes sr-only semantic text",
        )

    missing = []
    if not has_sr_only:
        missing.append("sr-only span for screen-reader text")
    if not has_aria_hidden:
        missing.append('aria-hidden="true" wrapper for animated chars')
    return CheckResult(
        "animated_heading_screen_reader_safe", "fail",
        f"AnimatedHeading missing: {'; '.join(missing)}",
        details={"missing_markers": missing},
    )


# ---------------------------------------------------------------------------
# 22. interactive_elements_have_focus_visible — FOUNDATION
# ---------------------------------------------------------------------------

# Open-tag span for <a> and <button>. Skips closing tags (</a>) because the
# `\b` after `a`/`button` won't match the `/` of `</`. Skips fragments and
# unrelated tags. DOTALL so multi-line opening tags (className wrapped across
# lines) are still captured as a single match.
_INTERACTIVE_OPEN_RE = re.compile(
    r"<(a|button)\b([^>]*?)>",
    re.DOTALL | re.IGNORECASE,
)
_HAS_CLASSNAME_RE = re.compile(r"\bclassName\s*=")
_FOCUS_UTIL_RE = re.compile(r"\bfocus(?:-visible)?:")


@check_metadata(details_file_key="files")
def interactive_elements_have_focus_visible(ctx: BuildContext) -> CheckResult:
    """Hero CTAs, navbar links, and the Call Us pill MUST have a visible
    keyboard focus ring.

    A `<a className="bg-white text-black ...">` without a `focus-visible:`
    utility either ships the default browser outline (often invisible against
    the liquid-glass / video background) or actively suppresses it via
    `outline-none` elsewhere — either way, keyboard users can't see where
    they are. Foundation rule for surfaces over the hero video where the
    contrast is unpredictable.

    Scope: scans the hero (`app/page.tsx`, `components/sections/Hero.tsx`)
    and navbar files (`components/layout/Nav*.tsx`, `components/ui/Nav*.tsx`).
    Skips elements with no `className=` at all — those use browser defaults,
    which are still visible. Only flags elements where `className` is set
    (the LLM's typical shape) but has no `focus-visible:` / `focus:` utility.
    """
    if not ctx.site_dir.exists():
        return CheckResult("interactive_elements_have_focus_visible", "skip", "no site directory")

    targets: list[Path] = []
    for rel in ("app/page.tsx", "components/sections/Hero.tsx"):
        p = ctx.site_dir / rel
        if p.exists():
            targets.append(p)
    for sub in ("components/layout", "components/ui"):
        d = ctx.site_dir / sub
        if d.exists():
            for nav in d.glob("Nav*.tsx"):
                targets.append(nav)

    if not targets:
        return CheckResult(
            "interactive_elements_have_focus_visible", "skip",
            "no hero/navbar files to inspect",
        )

    offenders: list[str] = []
    for path in targets:
        text = path.read_text(encoding="utf-8", errors="ignore")
        stripped = _LINE_COMMENT_RE.sub("", _BLOCK_COMMENT_RE.sub("", text))
        file_offended = False
        for m in _INTERACTIVE_OPEN_RE.finditer(stripped):
            attrs = m.group(2) or ""
            if not _HAS_CLASSNAME_RE.search(attrs):
                continue  # no className → browser default focus → skip
            if not _FOCUS_UTIL_RE.search(attrs):
                file_offended = True
                break
        if file_offended:
            offenders.append(str(path.relative_to(ctx.site_dir)))

    if not offenders:
        return CheckResult(
            "interactive_elements_have_focus_visible", "pass",
            "all interactive elements in hero/navbar carry focus-visible utilities",
        )
    return CheckResult(
        "interactive_elements_have_focus_visible", "fail",
        f"{len(offenders)} hero/navbar file(s) have <a>/<button> with className but no focus-visible: utility",
        details={"files": offenders[:10]},
    )


# ---------------------------------------------------------------------------
# 23. hero_text_has_legibility_safeguard — FOUNDATION
# ---------------------------------------------------------------------------

_LEGIBILITY_RE = re.compile(
    r"(?:textShadow|text-shadow|drop-shadow-(?:none|sm|md|lg|xl|2xl|\[)|drop-shadow\b)",
    re.IGNORECASE,
)


@check_metadata(static_files=("components/sections/Hero.tsx", "components/ui/AnimatedHeading.tsx", "app/page.tsx"))
def hero_text_has_legibility_safeguard(ctx: BuildContext) -> CheckResult:
    """Hero text must carry its own legibility scaffolding.

    The foundation forbids a dark overlay above the hero video. Without an
    overlay, hero text relies on a per-element legibility safeguard so it
    reads against any video frame: an inline `textShadow` style or a Tailwind
    `drop-shadow-*` utility. The `AnimatedHeading` component bakes the
    shadow into its `<h1>` so the headline is always covered — but the
    subhead `<p>` in `Hero.tsx` / `page.tsx` must add its own.

    The check passes if at least ONE of {Hero.tsx, app/page.tsx, AnimatedHeading.tsx}
    contains a `textShadow` / `text-shadow` / `drop-shadow` reference. It is
    a coarse safety net — not enforcing per-element shadowing, but ensuring
    the project hasn't forgotten the pattern entirely. Combined with the
    foundation `AnimatedHeading.tsx` baked-in shadow, this is sufficient
    coverage for the common case.
    """
    if not ctx.site_dir.exists():
        return CheckResult("hero_text_has_legibility_safeguard", "skip", "no site directory")

    candidates = [
        ctx.site_dir / "components" / "ui" / "AnimatedHeading.tsx",
        ctx.site_dir / "components" / "sections" / "Hero.tsx",
        ctx.site_dir / "app" / "page.tsx",
    ]
    for path in candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        stripped = _LINE_COMMENT_RE.sub("", _BLOCK_COMMENT_RE.sub("", text))
        if _LEGIBILITY_RE.search(stripped):
            return CheckResult(
                "hero_text_has_legibility_safeguard", "pass",
                f"legibility safeguard (textShadow / drop-shadow) found in {path.relative_to(ctx.site_dir)}",
            )

    return CheckResult(
        "hero_text_has_legibility_safeguard", "fail",
        "no textShadow / text-shadow / drop-shadow found in AnimatedHeading.tsx, Hero.tsx, or app/page.tsx",
    )


# ---------------------------------------------------------------------------
# 24. hero_video_has_poster — FOUNDATION
# ---------------------------------------------------------------------------

# Match a <video ...> opening tag containing both autoplay (case-insensitive)
# and a poster= attribute. DOTALL so multi-line video tags still match.
_VIDEO_OPEN_RE = re.compile(r"<video\b([^>]*)>", re.DOTALL | re.IGNORECASE)
_AUTOPLAY_ATTR_RE = re.compile(r"\bautoplay\b", re.IGNORECASE)
_POSTER_ATTR_RE = re.compile(r"\bposter\s*=", re.IGNORECASE)


@check_metadata(static_files=("components/sections/Hero.tsx", "app/page.tsx"))
def hero_video_has_poster(ctx: BuildContext) -> CheckResult:
    """The hero `<video>` MUST declare a `poster=` attribute.

    Without a poster, the browser shows a black rectangle while the video
    is loading — on slow connections this can be 200-1000ms of visible
    emptiness during the most-photographed moment of the page. The poster
    gives the LLM-chosen Pexels still (or Imagen-generated image) a job:
    paint instantly while the video downloads, then the video takes over.

    Combined with `prefers-reduced-data` (future), the poster is also the
    fallback for users who opt out of autoplay video entirely. Mandatory
    foundation rule; check passes when any `<video … autoplay …>` in the
    hero file (`Hero.tsx` or `app/page.tsx`) has `poster=` in the same tag.
    """
    if not ctx.site_dir.exists():
        return CheckResult("hero_video_has_poster", "skip", "no site directory")

    candidates = [
        ctx.site_dir / "components" / "sections" / "Hero.tsx",
        ctx.site_dir / "app" / "page.tsx",
    ]
    saw_video = False
    for path in candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in _VIDEO_OPEN_RE.finditer(text):
            attrs = m.group(1) or ""
            if not _AUTOPLAY_ATTR_RE.search(attrs):
                continue
            saw_video = True
            if _POSTER_ATTR_RE.search(attrs):
                return CheckResult(
                    "hero_video_has_poster", "pass",
                    f"<video autoplay … poster=…> found in {path.relative_to(ctx.site_dir)}",
                )

    if not saw_video:
        # `hero_uses_background_video` covers this; don't double-fail.
        return CheckResult(
            "hero_video_has_poster", "skip",
            "no hero <video autoplay> to inspect (see hero_uses_background_video)",
        )
    return CheckResult(
        "hero_video_has_poster", "fail",
        "hero <video autoplay> exists but has no poster= attribute",
    )


# ---------------------------------------------------------------------------
# 25. contact_form_uses_server_action — FOUNDATION
# ---------------------------------------------------------------------------

_USE_SERVER_DIRECTIVE_RE = re.compile(r'["\']use server["\']')


@check_metadata(static_files=("app/actions/contact.ts", "components/forms/ContactForm.tsx", "app/contact/page.tsx"))
def contact_form_uses_server_action(ctx: BuildContext) -> CheckResult:
    """The contact form must be a real Next.js Server Action.

    Every Pebble build emits a contact page — but historically the form was
    fake (an `onSubmit` handler with a hardcoded success state). Visitors
    filling it sent NOTHING, anywhere. That's the most visible functionality
    gap in the engine, and this check closes it.

    Pass criteria:
    1. `app/actions/contact.ts` exists AND contains a `"use server"` directive.
    2. `components/forms/ContactForm.tsx` exists AND references the action
       (either imports from `@/app/actions/contact` or uses `useActionState`).

    Anything less means the form is decorative. The eval will fail and the
    repair loop will re-emit the Code Pattern 8 scaffold.
    """
    if not ctx.site_dir.exists():
        return CheckResult("contact_form_uses_server_action", "skip", "no site directory")

    action_path = ctx.site_dir / "app" / "actions" / "contact.ts"
    form_path = ctx.site_dir / "components" / "forms" / "ContactForm.tsx"
    missing: list[str] = []
    if not action_path.exists():
        missing.append("app/actions/contact.ts")
    if not form_path.exists():
        missing.append("components/forms/ContactForm.tsx")
    if missing:
        return CheckResult(
            "contact_form_uses_server_action", "fail",
            f"contact form scaffold missing: {', '.join(missing)}",
            details={"missing": missing},
        )

    action_text = action_path.read_text(encoding="utf-8", errors="ignore")
    if not _USE_SERVER_DIRECTIVE_RE.search(action_text):
        return CheckResult(
            "contact_form_uses_server_action", "fail",
            'app/actions/contact.ts has no "use server" directive',
        )

    form_text = form_path.read_text(encoding="utf-8", errors="ignore")
    references_action = (
        "@/app/actions/contact" in form_text
        or "useActionState" in form_text
    )
    if not references_action:
        return CheckResult(
            "contact_form_uses_server_action", "fail",
            "ContactForm.tsx does not reference the Server Action "
            "(expected import from '@/app/actions/contact' or useActionState)",
        )

    return CheckResult(
        "contact_form_uses_server_action", "pass",
        "contact form wired to Next.js Server Action",
    )


# ---------------------------------------------------------------------------
# 26. resend_in_dependencies — FOUNDATION
# ---------------------------------------------------------------------------

@check_metadata(static_files=("package.json",))
def resend_in_dependencies(ctx: BuildContext) -> CheckResult:
    """`package.json` must declare `resend` in `dependencies`.

    The contact form's Server Action imports the Resend SDK; if the package
    isn't declared, `npm install` won't pull it and the build crashes at
    the first import. This is the same class of regression the Ironwood
    incident (react-icons not declared) exposed in May 2026.
    """
    if not ctx.site_dir.exists():
        return CheckResult("resend_in_dependencies", "skip", "no site directory")
    pkg = ctx.site_dir / "package.json"
    if not pkg.exists():
        return CheckResult("resend_in_dependencies", "fail", "package.json missing")

    text = pkg.read_text(encoding="utf-8", errors="ignore")
    clean = _JSONC_COMMENT_RE.sub("", text)
    try:
        data = json.loads(clean)
    except json.JSONDecodeError as e:
        return CheckResult(
            "resend_in_dependencies", "fail",
            f"package.json is invalid JSON: {e}",
        )

    deps = data.get("dependencies") or {}
    if "resend" in deps:
        return CheckResult(
            "resend_in_dependencies", "pass",
            f"resend declared in dependencies ({deps['resend']})",
        )
    return CheckResult(
        "resend_in_dependencies", "fail",
        "package.json dependencies missing 'resend' (Server Action needs it)",
    )


# ---------------------------------------------------------------------------
# 27. imports_resolve_to_dependencies — FOUNDATION (general regression guard)
# ---------------------------------------------------------------------------

# Match `from "..."` and `from '...'` import specifiers.
_IMPORT_FROM_RE = re.compile(r"""from\s+['"]([^'"]+)['"]""")

# Packages provided by the framework that don't need to be in package.json.
# Next.js bundles these; "server-only" / "client-only" are zero-runtime
# markers Next includes by default.
_FRAMEWORK_BUILTINS = {
    "react",
    "react-dom",
    "react/jsx-runtime",
    "react/jsx-dev-runtime",
    "next",
    "server-only",
    "client-only",
}


def _import_root(spec: str) -> str | None:
    """Return the package root from an import specifier, or None if it's
    a path / alias that shouldn't be checked against package.json.

    Examples:
        "react"                 -> "react"
        "react-dom/client"      -> "react-dom"
        "@radix-ui/react-dialog"-> "@radix-ui/react-dialog"
        "@scope/pkg/sub/path"   -> "@scope/pkg"
        "./foo"                 -> None   (relative)
        "../bar"                -> None   (relative)
        "@/components/x"        -> None   (project path alias)
    """
    if spec.startswith(".") or spec.startswith("/") or spec.startswith("@/"):
        return None
    parts = spec.split("/")
    if spec.startswith("@"):
        if len(parts) < 2:
            return None
        return "/".join(parts[:2])
    return parts[0]


@check_metadata(static_files=("package.json",), details_file_key="files")
def imports_resolve_to_dependencies(ctx: BuildContext) -> CheckResult:
    """Every `from "package-name"` import must resolve to a declared
    dependency in package.json.

    Catches the regression class that bit Ironwood Coffee Roasters in
    May 2026: the LLM imported `react-icons/fa6` without adding
    `react-icons` to dependencies, so `npm install` succeeded but
    `next dev` died at the first runtime import.

    Built-in framework packages (react, next/*, server-only, client-only)
    are exempt. Relative imports (`./foo`) and `@/` alias imports are
    skipped — those are project-local and resolved by tsconfig paths.
    """
    if not ctx.site_dir.exists():
        return CheckResult("imports_resolve_to_dependencies", "skip", "no site directory")

    pkg_path = ctx.site_dir / "package.json"
    if not pkg_path.exists():
        return CheckResult("imports_resolve_to_dependencies", "fail", "package.json missing")

    try:
        text = pkg_path.read_text(encoding="utf-8", errors="ignore")
        pkg = json.loads(_JSONC_COMMENT_RE.sub("", text))
    except json.JSONDecodeError as e:
        return CheckResult(
            "imports_resolve_to_dependencies", "fail",
            f"package.json invalid JSON: {e}",
        )

    declared: set[str] = set()
    declared.update((pkg.get("dependencies") or {}).keys())
    declared.update((pkg.get("devDependencies") or {}).keys())
    declared.update((pkg.get("peerDependencies") or {}).keys())

    # Walk every tsx/ts file, collect undeclared imports.
    undeclared: dict[str, list[str]] = {}  # pkg-name -> [files using it]
    for ext in ("*.tsx", "*.ts"):
        for f in ctx.site_dir.rglob(ext):
            if "node_modules" in f.parts or ".next" in f.parts:
                continue
            file_text = f.read_text(encoding="utf-8", errors="ignore")
            for m in _IMPORT_FROM_RE.finditer(file_text):
                spec = m.group(1)
                # next/* sub-paths (next/font/google, next/image, etc.) are
                # always bundled with `next` itself.
                if spec == "next" or spec.startswith("next/"):
                    continue
                root = _import_root(spec)
                if root is None:
                    continue  # relative or path alias — fine
                if root in _FRAMEWORK_BUILTINS:
                    continue
                if root not in declared:
                    undeclared.setdefault(root, []).append(
                        str(f.relative_to(ctx.site_dir))
                    )

    if not undeclared:
        return CheckResult(
            "imports_resolve_to_dependencies", "pass",
            f"all imports resolve to declared dependencies "
            f"({len(declared)} package(s) declared)",
        )

    offending: list[str] = []
    for pkg_name, files in undeclared.items():
        offending.append(f"{pkg_name} (used in {files[0]})")

    return CheckResult(
        "imports_resolve_to_dependencies", "fail",
        f"{len(undeclared)} import(s) not declared in package.json: "
        f"{', '.join(undeclared.keys())}",
        details={
            "undeclared": list(undeclared.keys()),
            "files": offending[:10],
        },
    )


# ---------------------------------------------------------------------------
# 28. industry_pages_present — FOUNDATION (May 2026 page expansion)
# ---------------------------------------------------------------------------

# Universal extra pages every build adds (in addition to the 4 foundation
# pages: home, services, about, contact). Routes are fixed.
_UNIVERSAL_EXTRA_ROUTES = {
    "faq":     "app/faq/page.tsx",
    "privacy": "app/privacy/page.tsx",
    "terms":   "app/terms/page.tsx",
}


@check_metadata(details_file_key="missing")
def industry_pages_present(ctx: BuildContext) -> CheckResult:
    """Industry-aware pages from the build's industry must all be generated.

    Every build must include:
      - The 4 foundation pages (covered by required_files_present)
      - The 3 universal extras: FAQ, Privacy, Terms
      - The N industry-specific pages declared in industries.json under
        the build's industry key, e.g. yoga_studio → [events_schedule,
        team, pricing]

    Maps each page ID to its expected file path via PAGE_CATALOG.
    Reports any missing pages so the repair loop can re-emit them.
    """
    if not ctx.site_dir.exists():
        return CheckResult("industry_pages_present", "skip", "no site directory")

    industry_key = ctx.brief.get("_industry_intel_key")
    if not industry_key:
        return CheckResult(
            "industry_pages_present", "skip",
            "no _industry_intel_key in brief — can't determine required pages",
        )

    # Lazy import to avoid hard dependency on style_dna / industry modules
    # at eval-suite import time (matches the pattern in dna_display_font_honored).
    try:
        from pebble.industry import (
            PAGE_CATALOG,
            UNIVERSAL_EXTRA_PAGES,
            _load_industries_intel,
        )
    except Exception as e:
        return CheckResult(
            "industry_pages_present", "error",
            f"pebble.industry not importable: {e}",
        )

    industries = _load_industries_intel()
    entry = industries.get(industry_key) or {}
    industry_pages = entry.get("pages") or []

    # Build the full set of required EXTRA pages (foundation pages are
    # covered by required_files_present; we only check the additions).
    expected_paths: list[str] = []
    for pid in UNIVERSAL_EXTRA_PAGES:
        if pid in _UNIVERSAL_EXTRA_ROUTES:
            expected_paths.append(_UNIVERSAL_EXTRA_ROUTES[pid])

    for pid in industry_pages:
        if pid in PAGE_CATALOG:
            route = PAGE_CATALOG[pid]["route_segment"]
            expected_paths.append(f"app/{route}/page.tsx")

    missing = [p for p in expected_paths if not (ctx.site_dir / p).exists()]

    if not missing:
        return CheckResult(
            "industry_pages_present", "pass",
            f"all {len(expected_paths)} industry-aware pages present "
            f"({len(industry_pages)} industry + {len(UNIVERSAL_EXTRA_PAGES)} universal)",
        )

    return CheckResult(
        "industry_pages_present", "fail",
        f"{len(missing)} industry-aware page(s) missing: {', '.join(missing)}",
        details={"missing": missing, "industry_key": industry_key},
    )


# ---------------------------------------------------------------------------
# 29. plan_present — FOUNDATION (May 2026 Codex-spec product vision)
# ---------------------------------------------------------------------------

# Required top-level fields in plan.json. Keep this aligned with
# pebble.plan.PLAN_SCHEMA_VERSION 1.0.
_PLAN_REQUIRED_KEYS = {
    "schema_version", "audience", "goal", "pages", "features",
    "style", "setup_needs", "next_steps", "meta",
}


@check_metadata(details_file_key="missing_keys")
def plan_present(ctx: BuildContext) -> CheckResult:
    """Every build must emit plan.json alongside brief.json.

    The Pebble Plan is the user-facing "here's what I'll build" summary
    that the upcoming workspace UI shows before/after generation. The
    engine writes it deterministically from the brief + industry intel
    + DNA; failure here means ``run_build`` short-circuited before the
    plan-write step.
    """
    plan_path = ctx.build_dir / "plan.json"
    if not plan_path.exists():
        return CheckResult(
            "plan_present", "fail",
            "plan.json missing from build directory",
            details={"expected": "plan.json"},
        )

    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except Exception as e:
        return CheckResult(
            "plan_present", "fail",
            f"plan.json present but unparseable: {e}",
        )

    if not isinstance(plan, dict):
        return CheckResult("plan_present", "fail", "plan.json is not a JSON object")

    missing_keys = sorted(_PLAN_REQUIRED_KEYS - set(plan.keys()))
    if missing_keys:
        return CheckResult(
            "plan_present", "fail",
            f"plan.json missing required keys: {', '.join(missing_keys)}",
            details={"missing_keys": missing_keys},
        )

    return CheckResult(
        "plan_present", "pass",
        f"plan.json present (schema {plan.get('schema_version', '?')}, "
        f"{len(plan.get('pages', []))} pages, "
        f"{len(plan.get('features', []))} features)",
    )


# ---------------------------------------------------------------------------
# 30. no_duplicate_inline_forms — FOUNDATION (May 2026 competitor-fix batch)
# ---------------------------------------------------------------------------

# Matches an HTML/JSX <form ...> opening tag. Excludes self-closing.
_FORM_OPEN_RE = re.compile(r"<form\b[^>]*>", re.IGNORECASE)


@check_metadata(details_file_key="files")
def no_duplicate_inline_forms(ctx: BuildContext) -> CheckResult:
    """Shared UI primitives must live in ``components/`` and be imported,
    never duplicated inline across pages.

    The specific smell this catches: a brand-new form defined directly in
    ``app/contact/page.tsx`` or another page file, rather than importing
    ``ContactForm`` from ``components/forms/``. When a competing tool (and
    a junior LLM) does this, the same form ends up with two implementations
    that drift out of sync as the user iterates. The build looks correct
    today and breaks tomorrow.

    Heuristic: the literal ``<form>`` opening tag may appear in at most
    ONE file under ``app/`` or ``components/``. Other surfaces import the
    canonical form component instead. ``components/forms/ContactForm.tsx``
    is the expected home; anything else is treated as a duplication smell.
    """
    if not ctx.site_dir.exists():
        return CheckResult("no_duplicate_inline_forms", "skip", "no site directory")

    offenders: list[str] = []
    for tsx in list(ctx.site_dir.glob("app/**/*.tsx")) + list(ctx.site_dir.glob("components/**/*.tsx")):
        try:
            text = tsx.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if _FORM_OPEN_RE.search(text):
            offenders.append(str(tsx.relative_to(ctx.site_dir)).replace("\\", "/"))

    # Exactly one canonical form file is the healthy state.
    if len(offenders) <= 1:
        loc = offenders[0] if offenders else "(no inline <form> anywhere)"
        return CheckResult(
            "no_duplicate_inline_forms", "pass",
            f"forms centralized: <form> appears in {loc}",
        )

    return CheckResult(
        "no_duplicate_inline_forms", "fail",
        f"<form> tag appears in {len(offenders)} files: {', '.join(offenders)}. "
        "Move the canonical form into components/forms/ and import it from each page.",
        details={"files": offenders},
    )


# ---------------------------------------------------------------------------
# 31. limitations_disclosed_in_readme — FOUNDATION (May 2026 competitor-fix batch)
# ---------------------------------------------------------------------------

_LIMITS_HEADING_RE = re.compile(
    r"^#{1,3}\s*(What This Site Does NOT Include|Limitations|What Pebble Did Not Build|Out of Scope)\b",
    re.IGNORECASE | re.MULTILINE,
)


@check_metadata(static_files=("README.md",))
def limitations_disclosed_in_readme(ctx: BuildContext) -> CheckResult:
    """Every README must own what the build does NOT include.

    Honesty as a feature. Industries like therapy, healthcare, finance, and
    real estate carry expectations the build cannot legally or technically
    meet (HIPAA forms, regulated disclosures, payment processing). Surfacing
    those gaps in the README — with recommended third-party workarounds —
    keeps the user from learning the hard way later that the contact form
    is not the same thing as a HIPAA-compliant intake.

    Accepted heading variants: "What This Site Does NOT Include",
    "Limitations", "What Pebble Did Not Build", "Out of Scope".
    """
    if not ctx.site_dir.exists():
        return CheckResult("limitations_disclosed_in_readme", "skip", "no site directory")

    readme = ctx.site_dir / "README.md"
    if not readme.exists():
        return CheckResult(
            "limitations_disclosed_in_readme", "fail",
            "README.md missing — can't verify limitations disclosure",
        )

    try:
        text = readme.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return CheckResult(
            "limitations_disclosed_in_readme", "fail",
            f"README.md unreadable: {e}",
        )

    if not _LIMITS_HEADING_RE.search(text):
        return CheckResult(
            "limitations_disclosed_in_readme", "fail",
            "README.md has no honesty heading "
            "(expected one of: 'What This Site Does NOT Include', 'Limitations', "
            "'What Pebble Did Not Build', 'Out of Scope')",
        )

    return CheckResult(
        "limitations_disclosed_in_readme", "pass",
        "README discloses what the build does NOT include",
    )


# ---------------------------------------------------------------------------
# 32. deploy_to_vercel_scaffold — FOUNDATION
# ---------------------------------------------------------------------------

_DEPLOY_HEADING_RE = re.compile(r"^#{1,3}\s*Deploy\b", re.IGNORECASE | re.MULTILINE)


@check_metadata(static_files=("README.md", "vercel.json"))
def deploy_to_vercel_scaffold(ctx: BuildContext) -> CheckResult:
    """Every build must ship with a deploy story.

    Two artifacts: `vercel.json` at the project root (so Vercel auto-detects
    the Next.js framework when the user imports the repo) AND a `Deploy`
    section in the README explaining the GitHub-push-then-Vercel-import flow.
    The user owns the deployed site — Pebble produces the bundle, the user
    pushes to their own GitHub + Vercel.

    Closes the "I built this, how do I ship it?" loop without requiring
    Pebble to host or manage anything. Lighter-touch than the Base44 /
    Lovable managed deploy path, but preserves full code ownership.
    """
    if not ctx.site_dir.exists():
        return CheckResult("deploy_to_vercel_scaffold", "skip", "no site directory")

    missing: list[str] = []
    vercel = ctx.site_dir / "vercel.json"
    if not vercel.exists():
        missing.append("vercel.json")

    readme = ctx.site_dir / "README.md"
    if not readme.exists():
        missing.append("README.md")
    else:
        text = readme.read_text(encoding="utf-8", errors="ignore")
        if not _DEPLOY_HEADING_RE.search(text):
            return CheckResult(
                "deploy_to_vercel_scaffold", "fail",
                "README.md has no '## Deploy' / '# Deploy' / '### Deploy' heading",
            )

    if missing:
        return CheckResult(
            "deploy_to_vercel_scaffold", "fail",
            f"deploy scaffold missing: {', '.join(missing)}",
            details={"missing": missing},
        )

    return CheckResult(
        "deploy_to_vercel_scaffold", "pass",
        "vercel.json + README Deploy section present",
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
    # FOUNDATION checks (May 2026 overhaul — VEX-spec hero pattern)
    hero_uses_background_video,
    no_dark_overlay_on_hero_video,
    inter_font_global,
    liquid_glass_class_present,
    animation_components_present,
    prefers_reduced_motion_respected,
    # FOUNDATION a11y / legibility (May 2026 NLM cross-check addendum)
    animated_heading_screen_reader_safe,
    interactive_elements_have_focus_visible,
    hero_text_has_legibility_safeguard,
    hero_video_has_poster,
    # FOUNDATION functionality (May 2026 Base44/Lovable competitive addendum)
    contact_form_uses_server_action,
    resend_in_dependencies,
    imports_resolve_to_dependencies,
    deploy_to_vercel_scaffold,
    industry_pages_present,
    plan_present,
    no_duplicate_inline_forms,
    limitations_disclosed_in_readme,
    site_compiles,
]


# Quick lookup by name — used by pebble.repair to read a check's file hints.
CHECK_BY_NAME = {c.__name__: c for c in ALL_CHECKS}


def check_file_hints(check_name: str, details: dict | None = None) -> list[str]:
    """Resolve a check's file hints into a concrete list of paths.

    Used by :mod:`pebble.repair` to figure out which files to embed in the
    repair prompt for a failing check. Reads the metadata attached by
    :func:`check_metadata` — no separate mapping table to drift.

    Returns an empty list for "structural" checks (no metadata declared).
    """
    fn = CHECK_BY_NAME.get(check_name)
    if fn is None:
        return []
    if fn.details_file_key:
        return list((details or {}).get(fn.details_file_key) or [])
    return list(fn.static_files)
