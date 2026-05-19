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
from typing import Optional

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


# Directories to skip when scanning generated site source files.
# node_modules: third-party packages  |  .next: compiled build artifacts
_SKIP_DIRS: frozenset[str] = frozenset({"node_modules", ".next"})


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
        if _SKIP_DIRS.intersection(tsx.parts):
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
            if _SKIP_DIRS.intersection(f.parts):
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
            if _SKIP_DIRS.intersection(f.parts):
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
# 12. layout_is_server_component
# ---------------------------------------------------------------------------

_USE_CLIENT_DIRECTIVE_RE = re.compile(r"""^\s*['"]use client['"]""", re.MULTILINE)


@check_metadata(static_files=("app/layout.tsx",))
def layout_is_server_component(ctx: BuildContext) -> CheckResult:
    """``app/layout.tsx`` must NOT have a ``"use client"`` directive.

    Next.js App Router only allows ``export const metadata = {...}`` and
    ``export const viewport = {...}`` in Server Components. If the LLM adds
    ``"use client"`` to the layout file, the metadata export is silently
    ignored: OG tags, JSON-LD, viewport meta — all disappear. The build
    won't error, but the site ships invisible to social crawlers and SEO.
    """
    if not ctx.site_dir.exists():
        return CheckResult("layout_is_server_component", "skip", "no site directory")
    layout = ctx.site_dir / "app" / "layout.tsx"
    if not layout.exists():
        return CheckResult("layout_is_server_component", "fail", "app/layout.tsx missing")
    text = layout.read_text(encoding="utf-8", errors="ignore")
    if _USE_CLIENT_DIRECTIVE_RE.search(text):
        return CheckResult(
            "layout_is_server_component", "fail",
            'app/layout.tsx has "use client" directive — remove it. '
            "layout.tsx must be a Server Component so that `export const metadata` and "
            "`export const viewport` work. Move any client-side logic to a child component.",
        )
    return CheckResult(
        "layout_is_server_component", "pass",
        "app/layout.tsx has no \"use client\" directive (Server Component)",
    )


# ---------------------------------------------------------------------------
# 12b. images_have_alt
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
        if _SKIP_DIRS.intersection(tsx.parts):
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
        if _SKIP_DIRS.intersection(tsx.parts):
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
            if _SKIP_DIRS.intersection(f.parts):
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
    `app/globals.css` for layouts that use the liquid-glass chip navbar.

    LAYOUT DNA AWARENESS: layouts that explicitly use a different nav pattern
    (fixed_top, sticky_chapter, terminal_prompt_nav, etc.) do not require the
    .liquid-glass class. When one of these layouts is active, the check skips.
    """
    if not ctx.site_dir.exists():
        return CheckResult("liquid_glass_class_present", "skip", "no site directory")

    # Layouts that deliberately don't use liquid-glass
    _NO_LIQUID_GLASS_LAYOUTS = {
        "split_screen", "magazine_scroll", "manifesto", "terminal",
        "weather_report", "chat_log", "index_card", "gallery_first",
    }
    layout_id = (ctx.brief.get("_layout_dna_id") or "gradient_mesh").strip()
    if layout_id in _NO_LIQUID_GLASS_LAYOUTS:
        return CheckResult(
            "liquid_glass_class_present", "skip",
            f"layout DNA '{layout_id}' uses a different nav pattern — .liquid-glass not required",
        )

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
# 19b. client_components_have_directive — FOUNDATION
# ---------------------------------------------------------------------------

# Components that use React hooks (useState, useEffect, useActionState,
# useFormStatus) MUST have "use client" at the top. Without it, Next.js App
# Router throws at render time: "Error: hooks cannot be called from a Server
# Component". This is the opposite failure mode from layout_is_server_component.
_CLIENT_DIRECTIVE_RE = re.compile(r"""^\s*['"]use client['"]""", re.MULTILINE)

_REQUIRED_CLIENT_COMPONENTS = (
    "components/ui/AnimatedHeading.tsx",
    "components/ui/FadeIn.tsx",
    "components/forms/ContactForm.tsx",
)


@check_metadata(details_file_key="missing_directive")
def client_components_have_directive(ctx: BuildContext) -> CheckResult:
    """Foundation hook-using components must have ``"use client"`` directives.

    ``AnimatedHeading`` and ``FadeIn`` use ``useEffect``/``useState``;
    ``ContactForm`` uses ``useActionState`` and ``useFormStatus``. Without
    ``"use client"`` at the top of each file, Next.js App Router throws a
    runtime error ("hooks cannot be called from a Server Component") — the
    site is completely broken. This check catches the LLM forgetting the
    directive on components it otherwise generates correctly.
    """
    if not ctx.site_dir.exists():
        return CheckResult("client_components_have_directive", "skip", "no site directory")

    missing_directive: list[str] = []
    for rel in _REQUIRED_CLIENT_COMPONENTS:
        path = ctx.site_dir / rel
        if not path.exists():
            continue  # animation_components_present / contact_form_uses_server_action catch missing files
        text = path.read_text(encoding="utf-8", errors="ignore")
        if not _CLIENT_DIRECTIVE_RE.search(text):
            missing_directive.append(rel)

    if not missing_directive:
        return CheckResult(
            "client_components_have_directive", "pass",
            f"all {len(_REQUIRED_CLIENT_COMPONENTS)} hook-using components have \"use client\"",
        )
    return CheckResult(
        "client_components_have_directive", "fail",
        f"{len(missing_directive)} component(s) missing \"use client\" directive — "
        f"will crash in Next.js App Router: {', '.join(missing_directive)}",
        details={"missing_directive": missing_directive},
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
            if _SKIP_DIRS.intersection(f.parts):
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
# 30. footer_lists_all_pages — FOUNDATION (May 2026 multi-page discoverability)
# ---------------------------------------------------------------------------

# Where the footer can plausibly live. The prompt template requires
# components/layout/Footer.tsx, but tolerate a couple of fallback locations
# so a slightly off-template build doesn't fail the check spuriously — what
# matters is that the routes are linked SOMEWHERE in a layout-level file
# the user sees on every page.
_FOOTER_CANDIDATES = (
    "components/layout/Footer.tsx",
    "components/Footer.tsx",
    "app/layout.tsx",
)

# Routes that are foundation pages (always present, navbar already links
# them). The eval doesn't care if they're in the footer because the user
# can already reach them — it only cares about discoverability of the
# extras the navbar doesn't surface.
_FOUNDATION_ROUTES = {"/", "/services", "/about", "/contact"}


@check_metadata(static_files=("components/layout/Footer.tsx",))
def footer_lists_all_pages(ctx: BuildContext) -> CheckResult:
    """Every non-foundation page must be linked from the footer.

    Industry-aware builds emit 9-10 pages, but the navbar only surfaces
    Services / About / Contact. Without a footer sitemap, the FAQ /
    Privacy / Terms / Menu / Team / Booking / etc. pages are unreachable
    by a user (and uncrawlable by a search engine) once they leave the
    homepage. The footer sitemap is the discoverability mechanism.

    Reads ``plan.json`` to determine the expected route set, finds the
    footer file, and checks that each non-foundation route appears as a
    string in that file. The match is intentionally permissive — the
    LLM may write ``href="/faq"`` or ``Link href={'/faq'}`` or use a
    ROUTES constant; we just verify the route literal is present.
    """
    if not ctx.site_dir.exists():
        return CheckResult("footer_lists_all_pages", "skip", "no site directory")

    plan_path = ctx.build_dir / "plan.json"
    if not plan_path.exists():
        return CheckResult(
            "footer_lists_all_pages", "skip",
            "no plan.json — can't determine expected routes",
        )

    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except Exception as e:
        return CheckResult(
            "footer_lists_all_pages", "skip",
            f"plan.json unparseable: {e}",
        )

    pages = plan.get("pages") or []
    if not isinstance(pages, list):
        return CheckResult(
            "footer_lists_all_pages", "skip",
            "plan.json 'pages' is not a list",
        )

    # Routes that should appear in the footer sitemap.
    expected_routes = []
    seen = set()
    for page in pages:
        if not isinstance(page, dict):
            continue
        route = page.get("route")
        if not isinstance(route, str) or not route.startswith("/"):
            continue
        if route in _FOUNDATION_ROUTES:
            continue
        if route in seen:
            continue
        seen.add(route)
        expected_routes.append(route)

    if not expected_routes:
        return CheckResult(
            "footer_lists_all_pages", "pass",
            "no non-foundation pages in plan — nothing to link",
        )

    footer_path = None
    for candidate in _FOOTER_CANDIDATES:
        if (ctx.site_dir / candidate).exists():
            footer_path = ctx.site_dir / candidate
            break

    if footer_path is None:
        return CheckResult(
            "footer_lists_all_pages", "fail",
            f"no footer file found at any of: {', '.join(_FOOTER_CANDIDATES)}",
            details={"missing": list(_FOOTER_CANDIDATES)},
        )

    try:
        footer_text = footer_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return CheckResult(
            "footer_lists_all_pages", "error",
            f"could not read {footer_path.name}: {e}",
        )

    # Look for the route as a quoted href value. Both `"/faq"` and
    # `'/faq'` count; bare `/faq` in a comment doesn't (would be a
    # false positive for a "see /faq for details" doc string).
    missing = []
    for route in expected_routes:
        if (f'"{route}"' not in footer_text) and (f"'{route}'" not in footer_text):
            missing.append(route)

    if not missing:
        return CheckResult(
            "footer_lists_all_pages", "pass",
            f"footer at {footer_path.relative_to(ctx.site_dir).as_posix()} "
            f"links all {len(expected_routes)} non-foundation page(s)",
        )

    return CheckResult(
        "footer_lists_all_pages", "fail",
        f"{len(missing)} page(s) missing from footer sitemap: {', '.join(missing)}",
        details={
            "missing_routes": missing,
            "footer_file":    footer_path.relative_to(ctx.site_dir).as_posix(),
            "files":          [footer_path.relative_to(ctx.site_dir).as_posix()],
        },
    )


# ---------------------------------------------------------------------------
# 31. no_duplicate_inline_forms — FOUNDATION (May 2026 competitor-fix batch)
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
# 32. no_tracking_by_default — FOUNDATION (May 2026 privacy-compliance)
# ---------------------------------------------------------------------------

# Patterns that signal the user has explicitly opted into tracking. If a
# build slips one of these in without the user asking, the check fails so
# we don't silently break CAN/EU privacy law for them. Pebble's promise:
# you ship a CAN/EU-compliant site by default — tracking is opt-in.
_TRACKING_PATTERNS = [
    # Google Analytics (gtag.js, ga.js, analytics.js)
    (re.compile(r"googletagmanager\.com|google-analytics\.com|gtag\(", re.IGNORECASE), "Google Analytics / GTM"),
    # Meta Pixel
    (re.compile(r"connect\.facebook\.net|fbq\(", re.IGNORECASE), "Meta (Facebook) Pixel"),
    # Hotjar
    (re.compile(r"static\.hotjar\.com|hjsv\s*=", re.IGNORECASE), "Hotjar"),
    # Microsoft Clarity
    (re.compile(r"clarity\.ms", re.IGNORECASE), "Microsoft Clarity"),
    # LinkedIn Insight
    (re.compile(r"snap\.licdn\.com", re.IGNORECASE), "LinkedIn Insight"),
    # TikTok Pixel
    (re.compile(r"analytics\.tiktok\.com", re.IGNORECASE), "TikTok Pixel"),
    # Mixpanel / Amplitude (bundled SDKs)
    (re.compile(r"cdn\.mxpnl\.com|amplitude\.com/libs", re.IGNORECASE), "Mixpanel / Amplitude"),
    # Generic Segment
    (re.compile(r"cdn\.segment\.com/analytics", re.IGNORECASE), "Segment"),
]


@check_metadata(details_file_key="files")
def no_tracking_by_default(ctx: BuildContext) -> CheckResult:
    """Generated sites must NOT silently embed third-party trackers.

    Pebble's privacy promise: sites generated by the engine are CAN/EU
    privacy-compliant out of the box. If a user wants analytics, they
    add it explicitly via Setup → Analytics (not yet wired). Until then,
    leaking visitor data to GA/Meta/Hotjar/etc. by default would expose
    our users to legal risk.

    This check scans every JS/TS/HTML file for known tracker fingerprints
    and fails if any are found. The eval suite catches accidental
    additions during generation; the prompt template should keep them
    out in the first place.
    """
    if not ctx.site_dir.exists():
        return CheckResult("no_tracking_by_default", "skip", "no site directory")

    offenders: list[str] = []
    found_names: set[str] = set()
    targets: list[Path] = []
    for pattern in ("**/*.tsx", "**/*.ts", "**/*.jsx", "**/*.js", "**/*.html", "**/*.css", "**/*.mjs"):
        targets.extend(ctx.site_dir.glob(pattern))

    for f in targets:
        # Skip dependency code — we only care about what the engine emitted.
        rel = f.relative_to(ctx.site_dir).as_posix()
        if rel.startswith("node_modules/") or rel.startswith(".next/"):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for regex, name in _TRACKING_PATTERNS:
            if regex.search(text):
                offenders.append(rel)
                found_names.add(name)
                break  # one offense per file is enough

    if not offenders:
        return CheckResult(
            "no_tracking_by_default", "pass",
            "no third-party trackers embedded — site is privacy-clean by default",
        )

    return CheckResult(
        "no_tracking_by_default", "fail",
        f"third-party trackers found ({', '.join(sorted(found_names))}) in: {', '.join(offenders[:5])}"
        + (f" and {len(offenders) - 5} more" if len(offenders) > 5 else ""),
        details={"files": offenders, "trackers": sorted(found_names)},
    )


# ---------------------------------------------------------------------------
# 33. deploy_to_vercel_scaffold — FOUNDATION
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
    else:
        try:
            json.loads(vercel.read_text(encoding="utf-8", errors="ignore"))
        except json.JSONDecodeError as exc:
            return CheckResult(
                "deploy_to_vercel_scaffold", "fail",
                f"vercel.json is not valid JSON: {exc}",
            )

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
# 33. a11y_static_audit — top axe-core categories without a browser
# ---------------------------------------------------------------------------

# Catches the categories of axe-core findings that are statically
# detectable in JSX. Real axe-core needs a headless browser (heavy new
# dep + 20-60s per page); this check covers the highest-volume rule
# categories at static-analysis cost. Pebble can claim "every build
# passes static a11y checks" honestly; for full WCAG 2.1 AA the user
# still needs to run axe-core in CI against the live site.
#
# Rule categories implemented here (each maps to one or more axe rules):
# - icon_button_missing_label: <button> with only an icon child needs
#   aria-label or sr-only span (axe: button-name)
# - icon_link_missing_label:   <Link>/<a> with only an icon child needs
#   aria-label (axe: link-name)
# - input_without_label:       <input>/<textarea>/<select> needs an
#   associated <label> or aria-label (axe: label, label-title-only)
# - heading_skip:              h1 → h3 with no h2 between violates the
#   document outline (axe: heading-order)
#
# Existing checks already cover other axe rules, so we don't duplicate:
#   image-alt   → images_have_alt
#   region      → industry_pages_present (every page has a <main>)
#   focus-order → interactive_elements_have_focus_visible

# JSX is too irregular for a clean regex (e.g. `onClick={() => x}` has a
# `>` inside the attribute), so we walk the text with a brace-aware
# scanner for the open-tag attrs. The child-content between
# <button>...</button> is checked for the "icon-only" shape (one or
# more self-closing PascalCase tags + only whitespace).

_HAS_ARIA_LABEL_RE = re.compile(r'\baria-label\s*=\s*["\']', re.IGNORECASE)
_HAS_TITLE_ATTR_RE = re.compile(r'\btitle\s*=\s*["\']', re.IGNORECASE)
_INPUT_TAG_RE = re.compile(
    r'<(?:input|textarea|select)\b([^>]*)/?>',
    re.IGNORECASE,
)
_HAS_ID_ATTR_RE = re.compile(r'\bid\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
_TYPE_HIDDEN_RE = re.compile(r'\btype\s*=\s*["\']hidden["\']', re.IGNORECASE)
_TYPE_SUBMIT_RE = re.compile(r'\btype\s*=\s*["\'](?:submit|button|reset)["\']', re.IGNORECASE)
_LABEL_FOR_RE = re.compile(r'<label\b[^>]*\bhtmlFor\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
_HEADING_TAG_RE = re.compile(r"<h([1-6])\b", re.IGNORECASE)
# An icon-only child is one or more self-closing PascalCase JSX
# components (e.g. `<X />`, `<Twitter className="..." />`) with only
# whitespace between them. Plain text or lowercase tags break the match.
_ICON_ONLY_CHILDREN_RE = re.compile(
    r"^\s*(?:<[A-Z][A-Za-z0-9]*\b[^>]*/>\s*)+$",
    re.DOTALL,
)


def _find_close_of_open_tag(text: str, start: int) -> int:
    """Given an index into a `<tagname...` opening, return the index of
    the `>` that closes the OPEN tag (not the close tag). Returns -1
    if unmatched.

    JSX is irregular enough that a single brace counter doesn't work;
    NLM 2026-05-15 flagged template-literal interpolations (`${...}`)
    as a case the prior counter mishandled. The scanner now maintains
    a stack of modes:

    - ``jsx_attrs`` — top of stack at start; ``>`` here closes the tag.
    - ``expr`` — inside ``{...}`` (JSX expression OR template
      interpolation). ``{`` pushes another ``expr``; ``}`` pops; ``>``
      is harmless because we're inside braces.
    - ``tmpl`` — inside `` `...` `` template literal. Most chars are
      literal; ``${`` pushes an ``expr`` (and stays in tmpl mode
      conceptually, recovered when the expr pops); the closing
      backtick pops the ``tmpl``.

    Quoted strings (``'...'`` and ``"..."``) are tracked separately so
    a ``data-x="{}"`` attribute doesn't add to the brace depth.
    """
    modes: list[str] = ["jsx_attrs"]
    quote: Optional[str] = None
    i = start
    n = len(text)
    while i < n:
        c = text[i]
        cur = modes[-1]
        if quote:
            if c == "\\" and i + 1 < n:
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
            continue
        if cur == "tmpl":
            if c == "\\" and i + 1 < n:
                i += 2
                continue
            if c == "`":
                modes.pop()
                i += 1
                continue
            if c == "$" and i + 1 < n and text[i + 1] == "{":
                modes.append("expr")
                i += 2
                continue
            i += 1
            continue
        # cur is "jsx_attrs" or "expr"
        if c in ("'", '"'):
            quote = c
        elif c == "`":
            modes.append("tmpl")
        elif c == "{":
            modes.append("expr")
        elif c == "}":
            if cur == "expr":
                modes.pop()
            # spurious } at jsx_attrs level — ignore (malformed JSX
            # but we don't want to crash on it)
        elif c == ">" and cur == "jsx_attrs":
            return i
        i += 1
    return -1


def _find_matching_close(text: str, after: int, tag: str) -> int:
    """Locate the closing `</tag>` after index `after`, ignoring nested
    same-named tags (best-effort — JSX rarely nests `<button>` inside
    `<button>`, but handle one level just in case)."""
    open_re  = re.compile(rf"<{re.escape(tag)}\b", re.IGNORECASE)
    close_re = re.compile(rf"</{re.escape(tag)}\s*>", re.IGNORECASE)
    depth = 1
    i = after
    while i < len(text):
        m_open = open_re.search(text, i)
        m_close = close_re.search(text, i)
        if not m_close:
            return -1
        if m_open and m_open.start() < m_close.start():
            depth += 1
            i = m_open.end()
            continue
        depth -= 1
        if depth == 0:
            return m_close.start()
        i = m_close.end()
    return -1


def _scan_icon_only_violations(text: str, tag: str) -> int:
    """Count `<tag>` elements whose ONLY children are icon components
    and whose attrs lack aria-label/title. Brace-aware so JSX
    expressions in attrs don't break the match."""
    open_re = re.compile(rf"<{re.escape(tag)}\b", re.IGNORECASE)
    n = 0
    pos = 0
    while True:
        m = open_re.search(text, pos)
        if not m:
            return n
        attrs_start = m.end()
        gt = _find_close_of_open_tag(text, attrs_start)
        if gt == -1:
            return n
        attrs = text[attrs_start:gt]
        # Self-closing tag — no children to check, skip.
        if attrs.rstrip().endswith("/"):
            pos = gt + 1
            continue
        close_idx = _find_matching_close(text, gt + 1, tag)
        if close_idx == -1:
            return n
        children = text[gt + 1:close_idx]
        if _ICON_ONLY_CHILDREN_RE.match(children):
            if not _HAS_ARIA_LABEL_RE.search(attrs) and not _HAS_TITLE_ATTR_RE.search(attrs):
                n += 1
        pos = close_idx
    # unreachable


def _icon_button_violations(text: str) -> int:
    return _scan_icon_only_violations(text, "button")


def _icon_link_violations(text: str) -> int:
    return _scan_icon_only_violations(text, "Link") + _scan_icon_only_violations(text, "a")


def _input_label_violations(text: str) -> int:
    """Count form inputs that lack EITHER aria-label OR an associated
    <label htmlFor=>. Ignores hidden + submit-style inputs."""
    label_targets = set(_LABEL_FOR_RE.findall(text))
    n = 0
    for m in _INPUT_TAG_RE.finditer(text):
        attrs = m.group(1) or ""
        if _TYPE_HIDDEN_RE.search(attrs) or _TYPE_SUBMIT_RE.search(attrs):
            continue
        if _HAS_ARIA_LABEL_RE.search(attrs):
            continue
        id_match = _HAS_ID_ATTR_RE.search(attrs)
        if id_match and id_match.group(1) in label_targets:
            continue
        n += 1
    return n


def _heading_skip_violations(text: str) -> list[str]:
    """Return human-readable descriptions of heading-skip violations
    (e.g. 'h1 → h3 with no h2 between'). Each violation is one entry
    so the eval message can list them precisely."""
    levels = [int(m.group(1)) for m in _HEADING_TAG_RE.finditer(text)]
    out: list[str] = []
    prev = 0
    for cur in levels:
        if prev and cur > prev + 1:
            out.append(f"h{prev} → h{cur}")
        prev = cur
    return out


@check_metadata(details_file_key="files")
def a11y_static_audit(ctx: BuildContext) -> CheckResult:
    """Static accessibility audit — covers the axe-core rule categories
    we can detect without launching a browser.

    Rules:
    - **button-name**: ``<button>`` with only an icon child needs
      ``aria-label`` (or ``title``) so screen readers can announce it.
    - **link-name**: ``<Link>`` / ``<a>`` with only an icon child same
      thing.
    - **label**: ``<input>`` / ``<textarea>`` / ``<select>`` need either
      ``aria-label`` or an associated ``<label htmlFor=>``.
    - **heading-order**: levels skip (``h1`` directly to ``h3``) breaks
      assistive-tech document outlines.

    Reports the file paths so repair can re-emit them. For full WCAG 2.1
    AA the user still wants to run actual axe-core in CI — this check
    is the cheap default-on baseline.
    """
    if not ctx.site_dir.exists():
        return CheckResult("a11y_static_audit", "skip", "no site directory")

    offenders: dict[str, list[str]] = {}
    files_to_scan = (
        list(ctx.site_dir.glob("app/**/*.tsx"))
        + list(ctx.site_dir.glob("components/**/*.tsx"))
    )

    for tsx in files_to_scan:
        try:
            text = tsx.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        problems: list[str] = []

        ib = _icon_button_violations(text)
        if ib:
            problems.append(f"{ib} icon-only button(s) without aria-label/title")

        il = _icon_link_violations(text)
        if il:
            problems.append(f"{il} icon-only link(s) without aria-label/title")

        iv = _input_label_violations(text)
        if iv:
            problems.append(f"{iv} input(s) without label or aria-label")

        skips = _heading_skip_violations(text)
        if skips:
            problems.append(f"heading-order skips: {', '.join(skips)}")

        if problems:
            rel = tsx.relative_to(ctx.site_dir).as_posix()
            offenders[rel] = problems

    if not offenders:
        return CheckResult(
            "a11y_static_audit", "pass",
            f"{len(files_to_scan)} file(s) scanned, no static a11y issues",
        )

    total_files = len(offenders)
    summary = "; ".join(
        f"{path} ({', '.join(probs)})"
        for path, probs in list(offenders.items())[:3]
    )
    suffix = f" (+{total_files - 3} more)" if total_files > 3 else ""
    return CheckResult(
        "a11y_static_audit", "fail",
        f"{total_files} file(s) with static a11y issues: {summary}{suffix}",
        details={
            "files":      list(offenders.keys()),
            "violations": offenders,
        },
    )


# ---------------------------------------------------------------------------
# 34. schema_org_jsonld_present — FOUNDATION (SEO + AI agent discoverability)
# ---------------------------------------------------------------------------

# Match a <script type="application/ld+json"> tag — JSX-form. The src
# may be `dangerouslySetInnerHTML={{ __html: JSON.stringify({...}) }}`
# (the canonical Next.js way) OR a plain text body. Either is fine for
# search engines and AI agents that parse the served HTML.
_LDJSON_SCRIPT_RE = re.compile(
    r"""<script[^>]*?type=\s*['"]application/ld\+json['"]""",
    re.IGNORECASE,
)
# Schema.org JSON-LD must declare its vocabulary. Both forms accepted —
# string-key ("@context": "https://schema.org") OR property-shorthand
# without quotes (rare but legal in JS object literals when key is a
# valid identifier, which @context is NOT — but we accept both forms
# to avoid false-negatives on creative future codegen).
_SCHEMA_ORG_CONTEXT_RE = re.compile(
    r"""['"]?@context['"]?\s*:\s*['"]https?://schema\.org['"]""",
    re.IGNORECASE,
)


@check_metadata(static_files=("app/layout.tsx",))
def schema_org_jsonld_present(ctx: BuildContext) -> CheckResult:
    """`app/layout.tsx` must include a `<script type="application/ld+json">`
    block with a Schema.org context, so every page emits structured data
    for SEO and AI-agent discoverability.

    The check is shape-only — it does NOT validate the JSON-LD body's
    @type or property completeness, because the right type varies per
    industry (LocalBusiness for plumber, Organization for SaaS, etc.).
    Future tightening can pin @type per industry once industries.json
    carries the mapping.

    Why layout.tsx specifically: it's the single point that wraps every
    route, so structured data set there is inherited by every page.
    Pages that need extra type-specific markup (e.g. /menu using
    Restaurant + MenuItem) can add their own <script> tag on top — but
    the foundation Organization/LocalBusiness block belongs in layout.
    """
    if not ctx.site_dir.exists():
        return CheckResult("schema_org_jsonld_present", "skip", "no site directory")

    layout = ctx.site_dir / "app" / "layout.tsx"
    if not layout.exists():
        return CheckResult(
            "schema_org_jsonld_present", "fail",
            "app/layout.tsx is missing",
        )

    text = layout.read_text(encoding="utf-8", errors="ignore")
    if not _LDJSON_SCRIPT_RE.search(text):
        return CheckResult(
            "schema_org_jsonld_present", "fail",
            "app/layout.tsx has no <script type=\"application/ld+json\"> tag — "
            "add a Schema.org JSON-LD block (LocalBusiness or Organization) "
            "inside the <head> so search engines and AI agents can identify "
            "the business",
        )

    if not _SCHEMA_ORG_CONTEXT_RE.search(text):
        return CheckResult(
            "schema_org_jsonld_present", "fail",
            "app/layout.tsx has a JSON-LD script tag but no `@context: https://schema.org` "
            "declaration — without the vocabulary, the structured data won't be "
            "interpreted as Schema.org",
        )

    return CheckResult(
        "schema_org_jsonld_present", "pass",
        "Schema.org JSON-LD present in app/layout.tsx",
    )


# ---------------------------------------------------------------------------
# 35. sitemap_and_robots_present — FOUNDATION (crawler discoverability)
# ---------------------------------------------------------------------------

# Next.js 14 generates sitemap.xml / robots.txt from these two files via
# convention. Both expect a default export, but the SHAPE varies:
# sitemap returns an array, robots returns an object. The check is
# "is there a default export at all?" — Next.js will pin the shape at
# build time. Loose pattern accepts all legitimate forms:
#   export default function ...
#   export default async function ...
#   export default () => ...
#   export default { ... }            (object literal — robots.ts default)
#   export default class ...
#   const x = ...; export default x;  (named const, then exported)
#   export { default } from './x';    (re-export)
# Same regex for both files; the file path distinguishes their purpose.
# NLM round on Tracks 4–7 flagged the original regex (`function\b` OR
# `(` only) as too rigid — it would false-fail the named-const and
# re-export forms.
_DEFAULT_EXPORT_RE = re.compile(
    r"export\s+default\s+\S"
    r"|export\s*\{\s*default\s*[\},]",
)


@check_metadata(static_files=("app/sitemap.ts", "app/robots.ts"))
def sitemap_and_robots_present(ctx: BuildContext) -> CheckResult:
    """Every build must ship Next.js 14 convention files that emit
    `sitemap.xml` and `robots.txt`.

    Why both: search engines and modern AI agents (GPTBot, ClaudeBot,
    PerplexityBot, Google-Extended, etc.) consume robots.txt to decide
    crawling AND sitemap.xml to discover routes. Together they make
    every page in the build findable. Without them, only the homepage
    gets indexed reliably.

    The check is shape-only. We don't validate the route list against
    plan.json (that's drift-prone — the Footer eval covers it from a
    different angle). We just verify both files exist and export a
    default function — the Next.js convention requirement.
    """
    if not ctx.site_dir.exists():
        return CheckResult("sitemap_and_robots_present", "skip", "no site directory")

    sitemap = ctx.site_dir / "app" / "sitemap.ts"
    robots  = ctx.site_dir / "app" / "robots.ts"

    missing: list[str] = []
    if not sitemap.exists():
        missing.append("app/sitemap.ts")
    if not robots.exists():
        missing.append("app/robots.ts")
    if missing:
        return CheckResult(
            "sitemap_and_robots_present", "fail",
            f"crawler discoverability files missing: {', '.join(missing)}",
            details={"files": missing},
        )

    sitemap_src = sitemap.read_text(encoding="utf-8", errors="ignore")
    if not _DEFAULT_EXPORT_RE.search(sitemap_src):
        return CheckResult(
            "sitemap_and_robots_present", "fail",
            "app/sitemap.ts has no default export — Next.js convention "
            "requires a default-exported function (or arrow / object / "
            "re-export) returning a MetadataRoute.Sitemap array",
        )

    robots_src = robots.read_text(encoding="utf-8", errors="ignore")
    if not _DEFAULT_EXPORT_RE.search(robots_src):
        return CheckResult(
            "sitemap_and_robots_present", "fail",
            "app/robots.ts has no default export — Next.js convention "
            "requires a default-exported function (or arrow / object / "
            "re-export) returning a MetadataRoute.Robots object",
        )

    return CheckResult(
        "sitemap_and_robots_present", "pass",
        "app/sitemap.ts + app/robots.ts present with default exports",
    )


# ---------------------------------------------------------------------------
# 36. perf_budget_or_lighter — FOUNDATION (Core Web Vitals static heuristics)
# ---------------------------------------------------------------------------

# (T14, 2026-05-17) Five sub-checks, all static — no Lighthouse, no browser.
# Catches the regressions that turn a "looks fine in dev" build into a
# "loses 7% of conversions per second of LCP" production site.

# CLS: raw <img> without width AND height attrs. images_use_next_image
# already forbids raw <img>; this is defense-in-depth for the case where
# that check is skipped or the LLM slips a raw <img> past it.
_RAW_IMG_OPEN_RE = re.compile(r"<img\b([^>]*?)/?>", re.IGNORECASE | re.DOTALL)
_HAS_WIDTH_ATTR_RE  = re.compile(r"\bwidth\s*=")
_HAS_HEIGHT_ATTR_RE = re.compile(r"\bheight\s*=")

# FOIT: hand-rolled @font-face block must declare font-display with a
# non-blocking value. Browser default ("auto" / "block") hides text up to
# 3s on slow connections. Acceptable: swap | optional | fallback.
_FONT_FACE_BLOCK_RE = re.compile(r"@font-face\s*\{([^}]*)\}", re.IGNORECASE | re.DOTALL)
_FONT_DISPLAY_OK_RE = re.compile(
    r"\bfont-display\s*:\s*(?:swap|optional|fallback)\b",
    re.IGNORECASE,
)

# TBT: heavy 3D libs static-imported in app/page.tsx block first paint.
# `three` is ~700kb, `@react-three/*` builds on it. Must be loaded via
# next/dynamic({ ssr: false }) so they defer to after first paint.
#
# NLM round 2026-05-17: the negative lookahead `(?!type\s)` excludes
# `import type { Mesh } from 'three'` — type-only imports are erased at
# compile time and have zero bundle cost.
_HEAVY_LIB_IMPORT_RE = re.compile(
    r"""^[ \t]*import\s+(?!type\s)[^;]*?from\s*['"](three|@react-three/[^'"]+)['"]""",
    re.MULTILINE,
)

# LCP: hero <video> must declare preload= explicitly. Any value (metadata,
# auto, none) is acceptable — the point is the attribute documents intent
# rather than relying on inconsistent browser defaults.
_VIDEO_OPEN_RE = re.compile(r"<video\b([^>]*?)>", re.IGNORECASE | re.DOTALL)
_HAS_PRELOAD_ATTR_RE = re.compile(r"\bpreload\s*=")

# LCP: preload link OR <Image priority>. Either satisfies the "primary hero
# asset paints before JS hydrates" rule — <Image priority> auto-generates
# the preload link via Next.js's image pipeline.
#
# NLM round 2026-05-17: the negative lookahead after `priority` rejects
# `<Image priority={false}>` (explicit disable) while still accepting:
#   - bare `priority` (followed by space, `/`, or `>`)
#   - `priority={true}`, `priority="..."`, or any non-false expression
_PRELOAD_LINK_RE = re.compile(
    r"""<link\b[^>]*?\brel\s*=\s*['"]preload['"]""",
    re.IGNORECASE | re.DOTALL,
)
_IMAGE_PRIORITY_RE = re.compile(
    r"<Image\b[^>]*?\bpriority(?!\s*=\s*\{?\s*false\b)",
    re.IGNORECASE | re.DOTALL,
)


@check_metadata(static_files=(
    "app/layout.tsx", "app/page.tsx",
    "components/sections/Hero.tsx", "app/globals.css",
))
def perf_budget_or_lighter(ctx: BuildContext) -> CheckResult:
    """Static Core Web Vitals heuristics — no Lighthouse, no browser.

    Five rules covering the four user-facing metrics:

    1. **CLS** — every raw `<img>` must declare `width` AND `height` attrs.
       `images_use_next_image` forbids raw `<img>` entirely; this is the
       defense-in-depth backstop.
    2. **FOIT** — every `@font-face` in any CSS must declare
       `font-display: swap | optional | fallback`. Browser default (auto/
       block) hides text up to 3s on slow connections.
    3. **TBT** — `three` and `@react-three/*` MUST be loaded via
       `next/dynamic({ ssr: false })` in `app/page.tsx`. Static imports of
       these ~700kb libs block first paint.
    4. **LCP** — hero `<video>` MUST declare a `preload=` attribute
       explicitly. The value (metadata / auto / none) is up to the author;
       the absence is the regression.
    5. **LCP** — a `<link rel="preload">` OR `<Image priority>` MUST exist
       somewhere across layout / page / hero. Without it, the above-the-fold
       asset waits for JS hydration before the browser discovers it.

    Why this matters (NotebookLM source — 2026-05-17 research):
    - 1s slower load = 7% fewer conversions
    - 53% of mobile users bounce on sites > 3s
    - 0.05s = time to first impression
    """
    if not ctx.site_dir.exists():
        return CheckResult("perf_budget_or_lighter", "skip", "no site directory")

    failures: list[str] = []
    offender_files: list[str] = []

    # 1. CLS — raw <img> without width AND height
    img_offenders: list[str] = []
    for tsx in ctx.site_dir.rglob("*.tsx"):
        if _SKIP_DIRS.intersection(tsx.parts):
            continue
        text = tsx.read_text(encoding="utf-8", errors="ignore")
        for m in _RAW_IMG_OPEN_RE.finditer(text):
            attrs = m.group(1) or ""
            if not (_HAS_WIDTH_ATTR_RE.search(attrs) and _HAS_HEIGHT_ATTR_RE.search(attrs)):
                img_offenders.append(str(tsx.relative_to(ctx.site_dir)))
                break
    if img_offenders:
        failures.append(
            f"{len(img_offenders)} file(s) with raw <img> missing width/height (CLS risk)"
        )
        offender_files.extend(img_offenders[:5])

    # 2. FOIT — @font-face without font-display: swap|optional|fallback
    # NLM round 2026-05-17:
    #   (a) strip CSS comments first so `/* font-display: swap */` doesn't
    #       falsely satisfy the requirement.
    #   (b) blocks with ONLY `src: local(...)` (system fonts) have no
    #       network fetch and therefore no FOIT risk — skip them.
    font_offenders: list[str] = []
    for css in ctx.site_dir.rglob("*.css"):
        if _SKIP_DIRS.intersection(css.parts):
            continue
        text = css.read_text(encoding="utf-8", errors="ignore")
        stripped = _BLOCK_COMMENT_RE.sub("", text)
        for block in _FONT_FACE_BLOCK_RE.finditer(stripped):
            body = block.group(1) or ""
            # Skip local-only blocks — no url() means no network fetch.
            if "url(" not in body.lower():
                continue
            if not _FONT_DISPLAY_OK_RE.search(body):
                font_offenders.append(str(css.relative_to(ctx.site_dir)))
                break
    if font_offenders:
        failures.append(
            f"{len(font_offenders)} CSS file(s) with @font-face missing "
            "font-display: swap|optional|fallback (FOIT risk)"
        )
        offender_files.extend(font_offenders[:5])

    # 3. TBT — heavy 3D libs static-imported in app/page.tsx
    page = ctx.site_dir / "app" / "page.tsx"
    if page.exists():
        page_text = page.read_text(encoding="utf-8", errors="ignore")
        static_heavy = _HEAVY_LIB_IMPORT_RE.findall(page_text)
        if static_heavy:
            uniq = sorted(set(static_heavy))
            failures.append(
                f"app/page.tsx statically imports {', '.join(uniq)} — wrap "
                "in next/dynamic({ ssr: false }) so it loads after first paint"
            )
            offender_files.append("app/page.tsx")

    # 4. LCP — hero <video> without explicit preload= attribute
    video_preload_missing: list[str] = []
    hero_files = [
        ctx.site_dir / "app" / "page.tsx",
        ctx.site_dir / "components" / "sections" / "Hero.tsx",
    ]
    for path in hero_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in _VIDEO_OPEN_RE.finditer(text):
            attrs = m.group(1) or ""
            if not _HAS_PRELOAD_ATTR_RE.search(attrs):
                video_preload_missing.append(str(path.relative_to(ctx.site_dir)))
                break
    if video_preload_missing:
        failures.append(
            f"{len(video_preload_missing)} hero file(s) with <video> missing "
            "explicit preload= attribute (LCP risk — browser defaults vary)"
        )
        offender_files.extend(video_preload_missing[:5])

    # 5. LCP — preload link OR <Image priority> somewhere
    preload_evidence = False
    candidates = [
        ctx.site_dir / "app" / "layout.tsx",
        ctx.site_dir / "app" / "page.tsx",
        ctx.site_dir / "components" / "sections" / "Hero.tsx",
    ]
    for path in candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if _PRELOAD_LINK_RE.search(text) or _IMAGE_PRIORITY_RE.search(text):
            preload_evidence = True
            break
    if not preload_evidence:
        failures.append(
            "no <link rel=\"preload\"> or <Image priority> for the hero asset "
            "(LCP risk — first paint waits for JS to discover the asset)"
        )

    if failures:
        return CheckResult(
            "perf_budget_or_lighter", "fail",
            "; ".join(failures),
            details={"files": list(dict.fromkeys(offender_files))[:10]} if offender_files else None,
        )
    return CheckResult(
        "perf_budget_or_lighter", "pass",
        "CLS / FOIT / TBT / LCP heuristics clean",
    )


# ---------------------------------------------------------------------------
# 37. hero_cta_above_fold — FOUNDATION (conversion driver)
# ---------------------------------------------------------------------------

# (T15, 2026-05-17) The hero MUST contain at least one clear CTA. 70% of
# small-biz sites lack one (NLM source). Without a CTA above the fold the
# landing user has nothing to do — scroll past or bounce.

# Action verbs — first word of the CTA text. Common patterns lifted from
# Pebble's prompt template + general CTA copy norms. Case-insensitive.
_ACTION_VERBS = {
    "get", "start", "try", "book", "contact", "schedule", "learn",
    "call", "discover", "explore", "find", "reserve", "buy", "order",
    "shop", "join", "subscribe", "sign", "see", "view", "request",
    "claim", "download", "watch", "build", "create", "make", "talk",
    "chat", "speak", "meet", "visit", "browse", "read", "ask", "send",
    "tell", "let", "save", "grab", "pick", "choose", "open", "tap",
}

# CTA tag — capture tag, attrs, inner content. IGNORECASE so <a>/<A>/<Link>
# all match; back-ref \1 with IGNORECASE matches case-insensitively too.
_CTA_TAG_RE = re.compile(
    r"<(a|button|Link)\b([^>]*?)>((?:.|\n)*?)</\1>",
    re.IGNORECASE,
)
# Visually-prominent bg utility — solid color or arbitrary value.
_PROMINENT_BG_RE = re.compile(
    r"\bbg-(?:white|black|primary|secondary|accent|[a-z]+-\d{2,3}|\[[^]]+\])",
    re.IGNORECASE,
)
# href= attr extractor — both single- and double-quoted forms.
_HREF_RE = re.compile(r"""\bhref\s*=\s*['"]([^'"]*)['"]""")
# Variable href — `href={CONTACT_ROUTE}` or `href={`/${slug}`}` etc.
# NLM round 2026-05-17: dynamic-routing forms must be accepted because
# we can't introspect the variable's value at static-analysis time.
_HREF_EXPR_RE = re.compile(r"\bhref\s*=\s*\{[^}]+\}")


@check_metadata(static_files=("app/page.tsx", "components/sections/Hero.tsx"))
def hero_cta_above_fold(ctx: BuildContext) -> CheckResult:
    """The hero section MUST contain at least one clear CTA above the fold.

    A qualifying CTA has THREE properties:

    1. **Action verb in text** — 'Get a quote', 'Book a call', 'Start your
       trial'. First word of the link text matches the verb whitelist.
       Rejects 'About us', 'Click here', bare business names.
    2. **Recognizable href** — `/path`, `tel:`, `mailto:`, `#section`,
       `https://...`. Reject `href="#"` alone (the canonical dead link).
       `<button>` is exempt from href validation.
    3. **Visually prominent className** — `bg-white`, `bg-primary`,
       `bg-blue-500`, `bg-[#abc]`, etc. Distinguishes the primary CTA from
       inline links in body copy.

    Scope: `app/page.tsx` + `components/sections/Hero.tsx`. ONE qualifying
    CTA across both files satisfies the check.

    Why: 70% of small-business sites lack a clear homepage CTA (NLM source),
    and a 0.05s first-impression window means the CTA must land above the
    fold or it doesn't exist for most visitors.
    """
    if not ctx.site_dir.exists():
        return CheckResult("hero_cta_above_fold", "skip", "no site directory")

    files: list[Path] = []
    for rel in ("app/page.tsx", "components/sections/Hero.tsx"):
        p = ctx.site_dir / rel
        if p.exists():
            files.append(p)
    if not files:
        return CheckResult(
            "hero_cta_above_fold", "fail",
            "no hero files — neither app/page.tsx nor components/sections/Hero.tsx exist",
        )

    found_any_cta = False
    diagnostic: list[str] = []

    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        stripped = _LINE_COMMENT_RE.sub("", _BLOCK_COMMENT_RE.sub("", text))
        for m in _CTA_TAG_RE.finditer(stripped):
            tag = m.group(1).lower()
            attrs = m.group(2) or ""
            inner_raw = m.group(3) or ""
            inner = re.sub(r"<[^>]+>", " ", inner_raw)
            inner = re.sub(r"\s+", " ", inner).strip()
            if not inner:
                continue  # icon-only — covered by a11y_static_audit, not a CTA
            found_any_cta = True

            # 1. Action verb (first word, stripped of punctuation)
            first_word = inner.split()[0].lower().strip(",.!?;:'\"-")
            has_verb = first_word in _ACTION_VERBS

            # 2. Valid href (button exempt). String forms (`href="..."`)
            # get the dead-`#` check; expression forms (`href={CONTACT}`)
            # are accepted unconditionally — we can't introspect the value.
            if tag == "button":
                href_ok = True
                href = ""
            else:
                href_match = _HREF_RE.search(attrs)
                if href_match:
                    href = href_match.group(1).strip()
                    href_ok = bool(href) and href != "#"
                elif _HREF_EXPR_RE.search(attrs):
                    href = "(expression)"
                    href_ok = True
                else:
                    href = ""
                    href_ok = False

            # 3. Prominent className
            prominent = bool(_PROMINENT_BG_RE.search(attrs))

            if has_verb and href_ok and prominent:
                return CheckResult(
                    "hero_cta_above_fold", "pass",
                    f"hero contains qualifying CTA in {path.relative_to(ctx.site_dir)}",
                )

            missing: list[str] = []
            if not has_verb:
                missing.append(f"action verb (first word: '{first_word}')")
            if not href_ok:
                missing.append(f"valid href (got '{href}')")
            if not prominent:
                missing.append("prominent bg utility")
            diagnostic.append(f"<{tag}> '{inner[:40]}' missing: {', '.join(missing)}")

    if not found_any_cta:
        return CheckResult(
            "hero_cta_above_fold", "fail",
            "hero has no <a>/<button> CTA — add one with an action verb "
            "(Get/Start/Book/Call/Schedule etc.) and a real href",
            details={"files": [str(p.relative_to(ctx.site_dir)) for p in files]},
        )

    return CheckResult(
        "hero_cta_above_fold", "fail",
        f"hero CTAs exist but none qualify — {'; '.join(diagnostic[:3])}",
        details={"files": [str(p.relative_to(ctx.site_dir)) for p in files]},
    )


# ---------------------------------------------------------------------------
# 38. mobile_optimized_responsive — FOUNDATION (58% of traffic is mobile)
# ---------------------------------------------------------------------------

# (T16, 2026-05-17) Four checks. 58% of traffic is mobile, only 22% of
# small-biz sites are mobile-optimized (NLM source).

# Viewport meta — raw <meta name="viewport"> OR Next.js `export const viewport`.
_VIEWPORT_META_RE = re.compile(
    r"""<meta\b[^>]*?\bname\s*=\s*['"]viewport['"]""",
    re.IGNORECASE,
)
_EXPORT_VIEWPORT_RE = re.compile(r"export\s+const\s+viewport\s*[:=]")

# Responsive prefix usage in hero
_RESPONSIVE_PREFIX_RE = re.compile(r"\b(?:sm|md|lg|xl|2xl):")

# Tailwind config `screens` key — if explicitly defined, must include
# at least one of sm/md/lg. Default config (no `screens:` override) keeps
# sm/md/lg/xl/2xl intact.
_TAILWIND_SCREENS_RE = re.compile(r"\bscreens\s*:\s*\{([^}]*)\}", re.DOTALL)

# Touch target ≥44px. NLM round 2026-05-17 surfaced two bugs in the
# original regex-only approach:
#   (a) `px-12 py-0` matched `px-12` and passed — but px-only padding
#       gives zero vertical lift. Touch targets need VERTICAL height.
#   (b) `min-h-[3rem]` (48px) was rejected because the arbitrary-value
#       branch only accepted integer pixel values ≥40.
#
# Replaced the omnibus regex with a small inspector function that:
#   - Accepts ONLY axis-vertical utilities (p-N, py-N, min-h-*, h-*)
#   - Parses arbitrary values [Npx] / [Nrem] / [N.NNrem] / [Nem] / [N]
#     numerically and compares to ≥44px (≥2.75rem at 16px root).
#
# `px-N` is no longer accepted as a touch-target signal.
_NUMERIC_UTIL_RE = re.compile(
    r"\b(p|py|min-h|h)-(\d{1,3})\b"
)
_ARBITRARY_UTIL_RE = re.compile(
    r"\b(min-h|h)-\[(\d+(?:\.\d+)?)(px|rem|em)?\]"
)


def _has_acceptable_touch_target(cls: str) -> bool:
    """Does this className declare a Tailwind utility that guarantees
    ≥44px vertical touch target?

    Accepts:
    - ``p-3+`` / ``py-3+`` (both axes / vertical only) — Tailwind scale
      where N ≥ 3 gives 12px+ padding → 44px+ button.
    - ``min-h-11+`` / ``h-11+`` — 44px+ in default scale (×4).
    - ``min-h-[<value>]`` / ``h-[<value>]`` where the value resolves
      to ≥44px (px) or ≥2.75rem/em (at 16px root). Decimals supported.
    """
    # 1. Numeric Tailwind utilities — p-N, py-N, min-h-N, h-N where N maps
    #    to ≥44px (×4 in default scale → N ≥ 11 for min-h/h; ≥3 for
    #    padding which gives 12px each side around 16px text → ~40px,
    #    rounded as acceptable per Apple HIG threshold).
    for m in _NUMERIC_UTIL_RE.finditer(cls):
        util, n_str = m.group(1), m.group(2)
        n = int(n_str)
        if util in ("p", "py") and n >= 3:
            return True
        if util in ("min-h", "h") and n >= 11:
            return True
    # 2. Arbitrary values — min-h-[44px], h-[3rem], min-h-[2.75rem], etc.
    for m in _ARBITRARY_UTIL_RE.finditer(cls):
        val_str, unit = m.group(2), (m.group(3) or "px")
        try:
            val = float(val_str)
        except ValueError:
            continue
        if unit == "px" and val >= 44:
            return True
        if unit in ("rem", "em") and val >= 2.75:
            return True
    return False
# className value extractor — handles three common shapes:
#   className="bg-white px-6"
#   className={`bg-white px-6`}
#   className={"bg-white px-6"}
_CLASSNAME_VAL_RE = re.compile(
    r"""className\s*=\s*(?:['"]([^'"]*)['"]|\{`([^`]*)`\}|\{['"]([^'"]*)['"]\})"""
)


@check_metadata(static_files=(
    "app/layout.tsx", "components/sections/Hero.tsx",
    "app/page.tsx", "tailwind.config.ts",
))
def mobile_optimized_responsive(ctx: BuildContext) -> CheckResult:
    """Mobile-first responsive design checks.

    Four heuristics:

    1. **Viewport meta** — `<meta name="viewport">` OR Next.js
       `export const viewport`. Without it, mobile renders the page at
       desktop width and forces user-zoom.
    2. **Tailwind breakpoints intact** — if `tailwind.config.ts` explicitly
       sets `screens: {}` (or omits sm/md/lg from a custom screens object),
       `sm:`/`md:`/`lg:` utilities become no-ops on every page.
    3. **Hero uses responsive prefixes** — at least one `sm:`/`md:`/`lg:`
       (etc) prefix in the hero file. Desktop-only classes hit mobile at
       desktop scale.
    4. **Hero CTA touch target ≥44px** — interactive elements in hero
       need vertical-axis padding/height. Accepted utilities: ``p-3+``
       (both axes), ``py-3+`` (vertical), ``min-h-11+`` / ``min-h-[44px]``
       (decimals and rem/em supported). ``px-N`` alone is NOT accepted
       (horizontal-only padding doesn't lift the tap target). WCAG 2.5.5 /
       Apple HIG / Material all converge on 44px minimum.

    Hero-CTA scope note: the touch-target sub-check + hero_cta_above_fold
    both scan ``app/page.tsx`` + ``components/sections/Hero.tsx``. A CTA
    defined in a sub-imported component (e.g. ``components/ui/HeroCTA.tsx``
    rendered as ``<HeroCTA />`` in Hero.tsx) is invisible to both. Pebble's
    prompt template inlines the hero CTAs so this is rarely hit in practice;
    flagged in NLM round 2026-05-17 as a deferred enhancement.

    Why: 58% of traffic is mobile, 53% of mobile users bounce on sites >3s,
    only 22% of small-business sites are mobile-optimized (NLM source).
    """
    if not ctx.site_dir.exists():
        return CheckResult("mobile_optimized_responsive", "skip", "no site directory")

    failures: list[str] = []
    files_touched: list[str] = []

    # 1. Viewport meta
    layout = ctx.site_dir / "app" / "layout.tsx"
    if not layout.exists():
        failures.append("app/layout.tsx is missing — can't verify viewport meta")
        files_touched.append("app/layout.tsx")
    else:
        text = layout.read_text(encoding="utf-8", errors="ignore")
        if not (_VIEWPORT_META_RE.search(text) or _EXPORT_VIEWPORT_RE.search(text)):
            failures.append(
                "no viewport meta in app/layout.tsx — add `<meta name=\"viewport\" "
                "content=\"width=device-width, initial-scale=1\">` or "
                "`export const viewport = { width: \"device-width\", initialScale: 1 }`"
            )
            files_touched.append("app/layout.tsx")

    # 2. Tailwind config breakpoints
    tw_config = ctx.site_dir / "tailwind.config.ts"
    if tw_config.exists():
        text = tw_config.read_text(encoding="utf-8", errors="ignore")
        screens_match = _TAILWIND_SCREENS_RE.search(text)
        if screens_match:
            screens_body = screens_match.group(1) or ""
            if not re.search(r"\b(?:sm|md|lg)\s*:", screens_body):
                failures.append(
                    "tailwind.config.ts has explicit `screens: {}` (or screens "
                    "without sm/md/lg keys) — responsive utilities will no-op"
                )
                files_touched.append("tailwind.config.ts")

    # 3. Responsive prefix usage in hero file(s)
    hero_files: list[Path] = []
    for rel in ("components/sections/Hero.tsx", "app/page.tsx"):
        p = ctx.site_dir / rel
        if p.exists():
            hero_files.append(p)
    if hero_files:
        any_responsive = any(
            _RESPONSIVE_PREFIX_RE.search(p.read_text(encoding="utf-8", errors="ignore"))
            for p in hero_files
        )
        if not any_responsive:
            failures.append(
                "hero files have no responsive prefix (sm:/md:/lg:) — "
                "desktop classes hit mobile at desktop scale"
            )
            files_touched.extend(str(p.relative_to(ctx.site_dir)) for p in hero_files)

    # 4. Hero CTA touch target — interactives with className must meet 44px
    if hero_files:
        small_offenders: list[str] = []
        for path in hero_files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            stripped = _LINE_COMMENT_RE.sub("", _BLOCK_COMMENT_RE.sub("", text))
            file_offended = False
            for m in _INTERACTIVE_OPEN_RE.finditer(stripped):
                attrs = m.group(2) or ""
                if not _HAS_CLASSNAME_RE.search(attrs):
                    continue
                cls_match = _CLASSNAME_VAL_RE.search(attrs)
                cls = ""
                if cls_match:
                    cls = cls_match.group(1) or cls_match.group(2) or cls_match.group(3) or ""
                if not _has_acceptable_touch_target(cls):
                    file_offended = True
                    break
            if file_offended:
                small_offenders.append(str(path.relative_to(ctx.site_dir)))
        if small_offenders:
            failures.append(
                f"{len(small_offenders)} hero file(s) have interactive elements "
                "with <44px touch target — use p-3+ / py-3+ / min-h-11 / min-h-[44px]"
            )
            files_touched.extend(small_offenders)

    if failures:
        return CheckResult(
            "mobile_optimized_responsive", "fail",
            "; ".join(failures),
            details={"files": list(dict.fromkeys(files_touched))[:10]} if files_touched else None,
        )
    return CheckResult(
        "mobile_optimized_responsive", "pass",
        "viewport + Tailwind breakpoints + responsive prefixes + 44px touch targets",
    )


# ---------------------------------------------------------------------------
# 36. og_social_meta_present — FOUNDATION (social sharing discoverability)
# ---------------------------------------------------------------------------

# Next.js Metadata API form: openGraph: { ... }
_OG_API_RE = re.compile(r"\bopenGraph\s*:", re.IGNORECASE)
# Raw HTML form: <meta property="og:...">
_OG_RAW_RE = re.compile(r"""property\s*=\s*['"]og:""", re.IGNORECASE)

# Next.js Metadata API form: twitter: { ... } (any twitter metadata object)
_TWITTER_API_RE = re.compile(r"\btwitter\s*:\s*\{", re.IGNORECASE)
# Raw HTML form: <meta name="twitter:card">
_TWITTER_RAW_RE = re.compile(r"""name\s*=\s*['"]twitter:card['"]""", re.IGNORECASE)


@check_metadata(static_files=("app/layout.tsx",))
def og_social_meta_present(ctx: BuildContext) -> CheckResult:
    """`app/layout.tsx` must include Open Graph + Twitter Card metadata so
    shared links on LinkedIn, Facebook, Twitter/X, and Slack render with a
    title, description, and image instead of a bare URL.

    Accepted approaches (either is fine — the check is not prescriptive):
    1. **Next.js Metadata API** — `export const metadata: Metadata = { openGraph: {...}, twitter: { card: ... } }`
    2. **Raw meta tags** — `<meta property="og:title" ...>` + `<meta name="twitter:card" ...>`

    Both are checked in `app/layout.tsx` because that file wraps every route.
    Page-level overrides are fine but the foundation meta must live here.

    Why this matters: NLM research cross-check (2026-05-17) found that 92% of
    small-business sites generated without explicit OG meta produce blank social
    cards, causing link-share CTR to drop ~40% vs. sites with rich previews.
    """
    if not ctx.site_dir.exists():
        return CheckResult("og_social_meta_present", "skip", "no site directory")

    layout = ctx.site_dir / "app" / "layout.tsx"
    if not layout.exists():
        return CheckResult(
            "og_social_meta_present", "fail",
            "app/layout.tsx is missing",
        )

    text = layout.read_text(encoding="utf-8", errors="ignore")

    has_og = _OG_API_RE.search(text) or _OG_RAW_RE.search(text)
    if not has_og:
        return CheckResult(
            "og_social_meta_present", "fail",
            "app/layout.tsx has no Open Graph meta — add `openGraph: { title, description, type }` "
            "to `export const metadata` (Next.js Metadata API) so shared links on LinkedIn, "
            "Facebook, and Slack render a rich preview instead of a bare URL",
        )

    has_twitter = _TWITTER_API_RE.search(text) or _TWITTER_RAW_RE.search(text)
    if not has_twitter:
        return CheckResult(
            "og_social_meta_present", "fail",
            "app/layout.tsx has Open Graph meta but no Twitter Card — add "
            "`twitter: { card: 'summary_large_image' }` to `export const metadata` "
            "so links on Twitter/X render with a large image preview",
        )

    return CheckResult(
        "og_social_meta_present", "pass",
        "Open Graph + Twitter Card meta present in app/layout.tsx",
    )


# ---------------------------------------------------------------------------
# 37. favicon_defined — FOUNDATION (browser tab + bookmark identity)
# ---------------------------------------------------------------------------

# Next.js metadata API: icons: { ... } or icons: "..."
_METADATA_ICONS_RE = re.compile(r"\bicons\s*:", re.IGNORECASE)


@check_metadata(static_files=("app/favicon.ico", "app/icon.svg", "app/icon.png", "app/layout.tsx"))
def favicon_defined(ctx: BuildContext) -> CheckResult:
    """Every generated site must have a favicon so browser tabs and bookmarks
    show the business identity instead of the browser's generic blank-page icon.

    Accepted approaches (any one suffices):
    1. `app/favicon.ico` — Next.js App Router serves it automatically as /favicon.ico
    2. `app/icon.svg` or `app/icon.png` — App Router convention for non-ico formats
    3. `icons:` field in `export const metadata` inside `app/layout.tsx`

    Why this matters: a blank favicon signals "work in progress" to every visitor
    who opens the tab or bookmarks the page. It's the lowest-effort polish that
    makes the difference between a prototype and a shipped product.
    """
    if not ctx.site_dir.exists():
        return CheckResult("favicon_defined", "skip", "no site directory")

    app_dir = ctx.site_dir / "app"
    for filename in ("favicon.ico", "icon.svg", "icon.png"):
        if (app_dir / filename).exists():
            return CheckResult(
                "favicon_defined", "pass",
                f"favicon defined via app/{filename}",
            )

    layout = ctx.site_dir / "app" / "layout.tsx"
    if layout.exists():
        text = layout.read_text(encoding="utf-8", errors="ignore")
        if _METADATA_ICONS_RE.search(text):
            return CheckResult(
                "favicon_defined", "pass",
                "favicon defined via metadata.icons in app/layout.tsx",
            )

    return CheckResult(
        "favicon_defined", "fail",
        "no favicon defined — add `icons: { icon: '/icon.svg' }` to `export const metadata` "
        "in app/layout.tsx, OR place `app/favicon.ico` / `app/icon.svg` in the site directory. "
        "Without a favicon, every browser tab shows a blank icon instead of the business logo.",
    )


# ---------------------------------------------------------------------------
# 38. env_example_present — FOUNDATION (deployment developer experience)
# ---------------------------------------------------------------------------

_ENV_RESEND_RE = re.compile(r"RESEND_API_KEY", re.IGNORECASE)


@check_metadata(static_files=(".env.example",))
def env_example_present(ctx: BuildContext) -> CheckResult:
    """Every build must ship `.env.example` at the site root with the
    required secret names so users can deploy without hunting through the
    README and source code to discover which environment variables are needed.

    The mandatory variables are: `RESEND_API_KEY`, `CONTACT_FROM_EMAIL`,
    `CONTACT_TO_EMAIL`. The check verifies that at least `RESEND_API_KEY`
    is named — if that's present, the others are almost certainly there too.

    Why layout.tsx is NOT the right place for this: `.env.example` is
    a convention understood by Vercel, Netlify, Railway, and every hosting
    guide. It makes the deploy story self-contained: push repo, see
    .env.example, copy to .env, fill in keys, ship.
    """
    if not ctx.site_dir.exists():
        return CheckResult("env_example_present", "skip", "no site directory")

    env_example = ctx.site_dir / ".env.example"
    if not env_example.exists():
        return CheckResult(
            "env_example_present", "fail",
            ".env.example is missing — create it at the project root with "
            "`RESEND_API_KEY=`, `CONTACT_FROM_EMAIL=`, `CONTACT_TO_EMAIL=` "
            "so users know which secrets to configure before deploying",
        )

    text = env_example.read_text(encoding="utf-8", errors="ignore")
    if not _ENV_RESEND_RE.search(text):
        return CheckResult(
            "env_example_present", "fail",
            ".env.example exists but is missing RESEND_API_KEY — "
            "the contact form Server Action requires it to send mail via Resend",
        )

    return CheckResult(
        "env_example_present", "pass",
        ".env.example present with RESEND_API_KEY",
    )


# ---------------------------------------------------------------------------
# 39. email_helper_present — FOUNDATION (contact form runtime safety)
# ---------------------------------------------------------------------------

_RESEND_IMPORT_RE = re.compile(r"""from\s+['"]resend['"]""", re.IGNORECASE)


@check_metadata(static_files=("lib/email.ts",))
def email_helper_present(ctx: BuildContext) -> CheckResult:
    """`lib/email.ts` must exist and import Resend so the contact form Server
    Action can send mail at runtime.

    The contact form scaffold is:
        app/actions/contact.ts  → Server Action, imports from lib/email.ts
        lib/email.ts            → Resend client wrapper (server-only)
        components/forms/ContactForm.tsx → useActionState client form

    If `lib/email.ts` is missing, `next dev` / `next build` throws
    "Cannot find module '@/lib/email'" and the entire site fails to start.
    The `contact_form_uses_server_action` check catches the form-side gap;
    this check closes the helper-side gap.

    The check is deliberately loose: it only verifies the file exists and
    imports from 'resend'. The Resend API key is validated at runtime.
    """
    if not ctx.site_dir.exists():
        return CheckResult("email_helper_present", "skip", "no site directory")

    email_lib = ctx.site_dir / "lib" / "email.ts"
    if not email_lib.exists():
        return CheckResult(
            "email_helper_present", "fail",
            "lib/email.ts is missing — the contact form Server Action imports "
            "from '@/lib/email' at runtime; without this file, next dev crashes "
            "with 'Cannot find module'. Add the Resend client wrapper from Code Pattern 8.",
        )

    text = email_lib.read_text(encoding="utf-8", errors="ignore")
    if not _RESEND_IMPORT_RE.search(text):
        return CheckResult(
            "email_helper_present", "fail",
            "lib/email.ts exists but does not import from 'resend' — "
            "the file must wrap the Resend SDK (import { Resend } from 'resend')",
        )

    return CheckResult(
        "email_helper_present", "pass",
        "lib/email.ts present with Resend import",
    )


# ---------------------------------------------------------------------------
# 40. navbar_present — FOUNDATION
# ---------------------------------------------------------------------------

_NAVBAR_LIQUID_GLASS_RE = re.compile(r"liquid-glass")


@check_metadata(static_files=("components/layout/Navbar.tsx",))
def navbar_present(ctx: BuildContext) -> CheckResult:
    """`components/layout/Navbar.tsx` must exist and use the liquid-glass chip.

    The navbar is the visual signature of every Pebble build. It must live at
    the canonical path — not inlined into layout.tsx or page.tsx — so the
    repair loop can patch it independently. The `.liquid-glass` class produces
    the frosted-glass backdrop that distinguishes the chip from a plain bar.

    A missing Navbar.tsx means the build either has no navigation or baked it
    into layout.tsx (which the LLM sometimes does under token pressure).
    """
    if not ctx.site_dir.exists():
        return CheckResult("navbar_present", "skip", "no site directory")

    navbar = ctx.site_dir / "components" / "layout" / "Navbar.tsx"
    if not navbar.exists():
        return CheckResult(
            "navbar_present", "fail",
            "components/layout/Navbar.tsx is missing — the navbar must be a "
            "dedicated component at this path (Code Pattern 2), not inlined into "
            "layout.tsx or page.tsx",
        )

    text = navbar.read_text(encoding="utf-8", errors="ignore")
    if not _NAVBAR_LIQUID_GLASS_RE.search(text):
        return CheckResult(
            "navbar_present", "fail",
            "Navbar.tsx exists but doesn't reference the liquid-glass class — "
            "the <nav> chip must use .liquid-glass from globals.css (Code Pattern 2)",
        )

    return CheckResult(
        "navbar_present", "pass",
        "Navbar.tsx present with liquid-glass chip pattern",
    )


# ---------------------------------------------------------------------------
# 41. no_lorem_ipsum — QUALITY
# ---------------------------------------------------------------------------

_LOREM_IPSUM_RE = re.compile(r"\blorem\s+ipsum\b", re.IGNORECASE)
_SOURCE_SCAN_DIRS = ("app", "components", "lib")


@check_metadata()
def no_lorem_ipsum(ctx: BuildContext) -> CheckResult:
    """No `lorem ipsum` placeholder text in any TSX/TS source file.

    When the LLM runs low on context or hits a token cap it sometimes emits
    Lorem ipsum filler in testimonial copy, paragraph text, or placeholder
    sections. A site with Lorem ipsum visible to a real customer destroys
    trust instantly — it signals an unfinished product.

    Scans app/, components/, and lib/ recursively (*.tsx + *.ts only).
    """
    if not ctx.site_dir.exists():
        return CheckResult("no_lorem_ipsum", "skip", "no site directory")

    hits: list[str] = []
    for subdir in _SOURCE_SCAN_DIRS:
        d = ctx.site_dir / subdir
        if not d.exists():
            continue
        for p in d.rglob("*.tsx"):
            try:
                if _LOREM_IPSUM_RE.search(p.read_text(encoding="utf-8", errors="ignore")):
                    hits.append(str(p.relative_to(ctx.site_dir)))
            except OSError:
                pass
        for p in d.rglob("*.ts"):
            try:
                if _LOREM_IPSUM_RE.search(p.read_text(encoding="utf-8", errors="ignore")):
                    hits.append(str(p.relative_to(ctx.site_dir)))
            except OSError:
                pass

    if not hits:
        return CheckResult("no_lorem_ipsum", "pass", "no lorem ipsum placeholder text found")

    return CheckResult(
        "no_lorem_ipsum", "fail",
        f"{len(hits)} file(s) contain lorem ipsum placeholder text — replace with real copy",
        details={"files": hits[:10]},
    )


# ---------------------------------------------------------------------------
# 42. inter_font_applied — FOUNDATION
# ---------------------------------------------------------------------------

_FONT_INTER_VAR_RE = re.compile(r"var\(--font-inter\)")


@check_metadata(static_files=("tailwind.config.ts", "app/globals.css"))
def inter_font_applied(ctx: BuildContext) -> CheckResult:
    """`var(--font-inter)` must appear in both `tailwind.config.ts` and
    `app/globals.css`.

    Without `tailwind.config.ts` extending `fontFamily.sans`, Tailwind's
    `font-sans` utility resolves to the system stack, not Inter — every
    element that relies on the implicit sans default renders wrong.

    Without the `body` rule in `app/globals.css`, the Inter CSS variable
    from next/font is set but only applies via the `className` on `<html>`;
    any element outside the class cascade uses the browser default. Both
    are required by the checklist at line 977-978 of prompt_template.md.
    """
    if not ctx.site_dir.exists():
        return CheckResult("inter_font_applied", "skip", "no site directory")

    missing: list[str] = []

    tailwind = ctx.site_dir / "tailwind.config.ts"
    if not tailwind.exists():
        missing.append("tailwind.config.ts (missing)")
    elif not _FONT_INTER_VAR_RE.search(tailwind.read_text(encoding="utf-8", errors="ignore")):
        missing.append("tailwind.config.ts (no var(--font-inter) in fontFamily.sans)")

    css = ctx.site_dir / "app" / "globals.css"
    if not css.exists():
        missing.append("app/globals.css (missing)")
    elif not _FONT_INTER_VAR_RE.search(css.read_text(encoding="utf-8", errors="ignore")):
        missing.append("app/globals.css (no var(--font-inter) in body rule)")

    if not missing:
        return CheckResult(
            "inter_font_applied", "pass",
            "var(--font-inter) present in tailwind.config.ts + app/globals.css",
        )

    return CheckResult(
        "inter_font_applied", "fail",
        f"Inter CSS variable not wired: {'; '.join(missing)}",
        details={"missing": missing},
    )


# ---------------------------------------------------------------------------
# 43. no_gsap_split_text — QUALITY
# ---------------------------------------------------------------------------

_GSAP_SPLIT_TEXT_RE = re.compile(
    r"""from\s+['"]gsap/SplitText['"]|require\s*\(\s*['"]gsap/SplitText['"]\s*\)""",
    re.IGNORECASE,
)
@check_metadata()
def no_gsap_split_text(ctx: BuildContext) -> CheckResult:
    """No import of `gsap/SplitText` — this is a paid GSAP Club plugin.

    `gsap/SplitText` is not in the public npm registry. Any import crashes
    `next dev` with 'Cannot find module gsap/SplitText'. The hero h1 uses
    `AnimatedHeading` (Code Pattern 1) for per-character animation — that
    covers the primary SplitText use case without the paid dependency.
    """
    if not ctx.site_dir.exists():
        return CheckResult("no_gsap_split_text", "skip", "no site directory")

    hits: list[str] = []
    for subdir in _SOURCE_SCAN_DIRS:
        d = ctx.site_dir / subdir
        if not d.exists():
            continue
        for p in (*d.rglob("*.tsx"), *d.rglob("*.ts")):
            try:
                if _GSAP_SPLIT_TEXT_RE.search(p.read_text(encoding="utf-8", errors="ignore")):
                    hits.append(str(p.relative_to(ctx.site_dir)))
            except OSError:
                pass

    if not hits:
        return CheckResult("no_gsap_split_text", "pass", "no gsap/SplitText imports found")

    return CheckResult(
        "no_gsap_split_text", "fail",
        f"{len(hits)} file(s) import gsap/SplitText — paid Club plugin, crashes next dev; "
        "use AnimatedHeading (Code Pattern 1) instead",
        details={"files": hits[:10]},
    )


# ---------------------------------------------------------------------------
# 44. hero_uses_animated_heading — FOUNDATION
# ---------------------------------------------------------------------------

_ANIMATED_HEADING_USAGE_RE = re.compile(r"<AnimatedHeading\b|AnimatedHeading\s*\(")
_ANIMATED_HEADING_IMPORT_RE = re.compile(r"""from\s+['"]@?/components/ui/AnimatedHeading['"]""")


@check_metadata(static_files=("components/sections/Hero.tsx", "components/ui/AnimatedHeading.tsx"))
def hero_uses_animated_heading(ctx: BuildContext) -> CheckResult:
    """The hero file must import and render `AnimatedHeading` for the h1.

    `animation_components_present` verifies AnimatedHeading.tsx exists, but
    the LLM sometimes generates a plain `<h1>` in Hero.tsx instead of using
    the component. A bare `<h1>` skips the per-character entrance animation,
    the sr-only semantic text, and the built-in textShadow — three
    foundation constraints in one regression.

    Checks `components/sections/Hero.tsx` first; falls back to `app/page.tsx`
    in case the LLM inlines the hero there.

    LAYOUT DNA AWARENESS: layouts that deliberately use a plain <h1> (split_screen,
    magazine_scroll, manifesto, terminal, weather_report, chat_log, index_card,
    gallery_first, single_screen) set use_animated_heading=False. When the brief
    carries one of these layout ids, the check skips — the plain <h1> IS correct.
    """
    if not ctx.site_dir.exists():
        return CheckResult("hero_uses_animated_heading", "skip", "no site directory")

    # Layouts where a plain <h1> is the correct structural choice.
    _NO_ANIMATED_HEADING_LAYOUTS = {
        "split_screen", "magazine_scroll", "manifesto", "terminal",
        "weather_report", "chat_log", "index_card", "gallery_first", "single_screen",
    }
    layout_id = (ctx.brief.get("_layout_dna_id") or "gradient_mesh").strip()
    if layout_id in _NO_ANIMATED_HEADING_LAYOUTS:
        return CheckResult(
            "hero_uses_animated_heading", "skip",
            f"layout DNA '{layout_id}' uses a plain <h1> by design — AnimatedHeading not required",
        )

    for rel in ("components/sections/Hero.tsx", "app/page.tsx"):
        p = ctx.site_dir / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        if _ANIMATED_HEADING_USAGE_RE.search(text) or _ANIMATED_HEADING_IMPORT_RE.search(text):
            return CheckResult(
                "hero_uses_animated_heading", "pass",
                f"AnimatedHeading used in {rel}",
            )

    return CheckResult(
        "hero_uses_animated_heading", "fail",
        "neither Hero.tsx nor app/page.tsx imports or renders AnimatedHeading — "
        "the hero h1 must use AnimatedHeading (Code Pattern 1) for the a11y + "
        "animation contract",
    )


# ---------------------------------------------------------------------------
# 45. no_hardcoded_localhost — prevents dev URLs shipping to production
# ---------------------------------------------------------------------------

_LOCALHOST_URL_RE = re.compile(
    r"""https?://(?:localhost|127\.0\.0\.1)(?::\d+)?(?=/|['""\s]|$)""",
    re.IGNORECASE,
)


@check_metadata(details_file_key="files")
def no_hardcoded_localhost(ctx: BuildContext) -> CheckResult:
    """Source files must not contain hardcoded ``http://localhost`` URLs.

    A common LLM mistake: generating ``fetch("http://localhost:3000/api/...")``
    in a Server Action or ``href="http://localhost:8000/..."`` in a link.
    These work during local dev but ship completely broken links and API calls
    to production — the error is silent because Next.js builds without
    type-checking fetch URLs.

    Scans ``app/``, ``components/``, and ``lib/`` source files only.
    Line-only comments (``// http://localhost...``) are ignored; inline
    code is flagged regardless of surrounding strings.

    Fix: use relative paths (``/api/...``) or ``process.env.NEXT_PUBLIC_*``.
    """
    if not ctx.site_dir.exists():
        return CheckResult("no_hardcoded_localhost", "skip", "no site directory")

    offenders: list[str] = []
    for src_dir in _SOURCE_SCAN_DIRS:
        scan = ctx.site_dir / src_dir
        if not scan.exists():
            continue
        for f in scan.rglob("*"):
            if not f.is_file():
                continue
            if f.suffix not in {".ts", ".tsx", ".js", ".jsx", ".mjs"}:
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            # Strip lines that are pure comments (start with //) so that
            # documentation notes like `// dev: http://localhost:3000` are
            # ignored. Cannot use _LINE_COMMENT_RE here because its `//`
            # pattern also matches the `://` inside URL string literals.
            filtered = "\n".join(
                line for line in text.splitlines()
                if not line.lstrip().startswith("//")
            )
            if _LOCALHOST_URL_RE.search(filtered):
                offenders.append(f.relative_to(ctx.site_dir).as_posix())

    if not offenders:
        return CheckResult(
            "no_hardcoded_localhost", "pass",
            "no hardcoded localhost URLs in source files",
        )
    return CheckResult(
        "no_hardcoded_localhost", "fail",
        f"{len(offenders)} file(s) contain hardcoded localhost URLs (breaks production): "
        f"{', '.join(offenders[:5])}"
        + (f" and {len(offenders) - 5} more" if len(offenders) > 5 else "")
        + " — use relative paths or process.env.NEXT_PUBLIC_* instead",
        details={"files": offenders},
    )


# ---------------------------------------------------------------------------
# 46. no_pages_router_patterns — catches App Router + Pages Router mixups
# ---------------------------------------------------------------------------

# Patterns that are valid in Next.js Pages Router but crash or are silently
# broken in App Router. The LLM sometimes regresses to Pages Router patterns,
# especially for Head, data-fetching, and router imports.
_PAGES_ROUTER_PATTERNS: list[tuple[re.Pattern, str]] = [
    (
        re.compile(r"""import\s+(?:Head|default)\s+from\s+['"]next/head['"]"""),
        "next/head import (use `export const metadata` in layout.tsx instead)",
    ),
    (
        re.compile(r"""\bexport\s+(?:async\s+)?function\s+getServerSideProps\b"""),
        "getServerSideProps (Pages Router only — use async Server Components or Route Handlers)",
    ),
    (
        re.compile(r"""\bexport\s+(?:async\s+)?function\s+getStaticProps\b"""),
        "getStaticProps (Pages Router only — use async Server Components with fetch)",
    ),
    (
        re.compile(r"""\bexport\s+(?:async\s+)?function\s+getStaticPaths\b"""),
        "getStaticPaths (Pages Router only — use generateStaticParams)",
    ),
    (
        re.compile(r"""from\s+['"]next/router['"]"""),
        "next/router import (use next/navigation for App Router)",
    ),
]

@check_metadata(details_file_key="files")
def no_pages_router_patterns(ctx: BuildContext) -> CheckResult:
    """Source files must not use Next.js Pages Router APIs in an App Router build.

    The LLM sometimes regresses to Pages Router patterns — especially
    ``import Head from 'next/head'``, ``getServerSideProps``, and
    ``useRouter`` from ``next/router``. In an App Router build these are
    either silent no-ops (Head tags are ignored by the crawler) or runtime
    crashes. This check catches the five most common regressions:

    - ``next/head`` import → use ``export const metadata`` in layout.tsx
    - ``getServerSideProps`` → use async Server Components
    - ``getStaticProps`` → use fetch() in Server Components
    - ``getStaticPaths`` → use ``generateStaticParams``
    - ``next/router`` → use ``next/navigation``
    """
    if not ctx.site_dir.exists():
        return CheckResult("no_pages_router_patterns", "skip", "no site directory")

    offenders: list[str] = []
    seen: set[str] = set()

    for src_dir in _SOURCE_SCAN_DIRS:
        scan = ctx.site_dir / src_dir
        if not scan.exists():
            continue
        for f in scan.rglob("*"):
            if not f.is_file():
                continue
            if f.suffix not in {".ts", ".tsx", ".js", ".jsx"}:
                continue
            rel = f.relative_to(ctx.site_dir).as_posix()
            if rel in seen:
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            stripped = _LINE_COMMENT_RE.sub("", text)
            for pattern, label in _PAGES_ROUTER_PATTERNS:
                if pattern.search(stripped):
                    offenders.append(f"{rel}: {label}")
                    seen.add(rel)
                    break  # one offense per file

    if not offenders:
        return CheckResult(
            "no_pages_router_patterns", "pass",
            "no Pages Router patterns detected in App Router build",
        )
    return CheckResult(
        "no_pages_router_patterns", "fail",
        f"{len(offenders)} file(s) use Pages Router APIs (breaks App Router): "
        + "; ".join(offenders[:3])
        + ("..." if len(offenders) > 3 else ""),
        details={"files": offenders},
    )


# ---------------------------------------------------------------------------
# 47. foundation_pages_present — every Pebble site ships 4 navigable pages
# ---------------------------------------------------------------------------

_FOUNDATION_PAGE_ROUTES = (
    "app/services/page.tsx",
    "app/about/page.tsx",
    "app/contact/page.tsx",
)


@check_metadata(details_file_key="missing")
def foundation_pages_present(ctx: BuildContext) -> CheckResult:
    """The three core inner pages must exist as App Router route files.

    Every Pebble site guarantees four navigable pages: Homepage (checked
    by ``required_files_present``), Services, About, and Contact. The
    Navbar and Footer both link to ``/services``, ``/about``, and
    ``/contact`` by default. If any of these page files is missing, those
    navbar links are dead 404s — the most visible quality failure a
    small-business site can have.

    The LLM occasionally drops one or more inner pages when the context
    is long or the token budget is tight. This check makes that failure
    loud instead of silent.
    """
    if not ctx.site_dir.exists():
        return CheckResult("foundation_pages_present", "skip", "no site directory")

    missing = [path for path in _FOUNDATION_PAGE_ROUTES
               if not (ctx.site_dir / path).exists()]
    if not missing:
        return CheckResult(
            "foundation_pages_present", "pass",
            "all 3 foundation inner pages present (services / about / contact)",
        )
    return CheckResult(
        "foundation_pages_present", "fail",
        f"{len(missing)} foundation page(s) missing — dead navbar links: "
        + ", ".join(missing),
        details={"missing": missing},
    )


# ---------------------------------------------------------------------------
# 48. contact_form_has_inputs — form must be functional, not empty skeleton
# ---------------------------------------------------------------------------

_FORM_INPUT_RE = re.compile(
    r"""<(?:input|textarea|select)\b[^>]*\bname\s*=""",
    re.IGNORECASE,
)


@check_metadata(static_files=("components/forms/ContactForm.tsx",))
def contact_form_has_inputs(ctx: BuildContext) -> CheckResult:
    """ContactForm.tsx must have at least one named input field.

    ``contact_form_uses_server_action`` verifies the wiring is correct
    (Server Action + useActionState), but the LLM sometimes generates a
    correct-looking scaffold with an empty ``<form action={action} />``
    containing no fields. That form submits nothing, delivers nothing,
    and is invisible to the user as broken — there are no visible inputs
    to fill in.

    Pass criterion: ``components/forms/ContactForm.tsx`` contains at
    least one ``<input>``, ``<textarea>``, or ``<select>`` element with
    a ``name="..."`` attribute. Any single named field is enough — the
    detail is enforced by ``a11y_static_audit`` (aria-labels) and the
    prompt template.
    """
    if not ctx.site_dir.exists():
        return CheckResult("contact_form_has_inputs", "skip", "no site directory")

    form_path = ctx.site_dir / "components" / "forms" / "ContactForm.tsx"
    if not form_path.exists():
        return CheckResult(
            "contact_form_has_inputs", "skip",
            "ContactForm.tsx missing (contact_form_uses_server_action catches this)",
        )

    text = form_path.read_text(encoding="utf-8", errors="ignore")
    if _FORM_INPUT_RE.search(text):
        return CheckResult(
            "contact_form_has_inputs", "pass",
            "ContactForm.tsx has at least one named input field",
        )
    return CheckResult(
        "contact_form_has_inputs", "fail",
        "ContactForm.tsx has no <input>, <textarea>, or <select> with a name= attribute — "
        "the form submits nothing; add name, email, and message fields",
    )


# ---------------------------------------------------------------------------
# 39. design_tokens_defined — FOUNDATION (cinematic system, May 2026)
# ---------------------------------------------------------------------------

_ROOT_CSS_TOKEN_RE = re.compile(
    r":root\s*\{[^}]*--color-bg\b",
    re.IGNORECASE | re.DOTALL,
)


@check_metadata(static_files=("app/globals.css",))
def design_tokens_defined(ctx: BuildContext) -> CheckResult:
    """globals.css must open with a :root {} CSS token block defining --color-bg.

    The cinematic system moves ALL colors to CSS custom properties so DNA themes
    can be swapped without touching component files. Presence of --color-bg in a
    :root block implies the full token layer (--color-accent, --color-surface-*,
    --glass-blur, etc.) was emitted from the DNA block prepended at build time.
    """
    if not ctx.site_dir.exists():
        return CheckResult("design_tokens_defined", "skip", "no site directory")
    css = ctx.site_dir / "app" / "globals.css"
    if not css.exists():
        return CheckResult("design_tokens_defined", "skip", "no app/globals.css")
    text = css.read_text(encoding="utf-8", errors="ignore")
    if _ROOT_CSS_TOKEN_RE.search(text):
        return CheckResult(
            "design_tokens_defined", "pass",
            ":root { --color-bg } token block found in app/globals.css",
        )
    return CheckResult(
        "design_tokens_defined", "fail",
        "app/globals.css has no :root { --color-bg } block — DNA color tokens missing",
    )


# ---------------------------------------------------------------------------
# 40. grain_overlay_present — FOUNDATION (cinematic system, May 2026)
# ---------------------------------------------------------------------------


@check_metadata(static_files=("components/ui/GrainOverlay.tsx",))
def grain_overlay_present(ctx: BuildContext) -> CheckResult:
    """components/ui/GrainOverlay.tsx must exist for layouts that use grain.

    GrainOverlay is a fixed SVG feTurbulence grain layer injected once in
    app/layout.tsx. The gradient_mesh and single_screen layouts require it.

    LAYOUT DNA AWARENESS: layouts that don't use gradient backgrounds (terminal,
    chat_log, index_card, magazine_scroll, manifesto, weather_report) deliberately
    omit GrainOverlay — grain on a flat-background site looks like a rendering bug.
    """
    if not ctx.site_dir.exists():
        return CheckResult("grain_overlay_present", "skip", "no site directory")

    _NO_GRAIN_LAYOUTS = {
        "terminal", "chat_log", "index_card", "magazine_scroll",
        "manifesto", "weather_report",
    }
    layout_id = (ctx.brief.get("_layout_dna_id") or "gradient_mesh").strip()
    if layout_id in _NO_GRAIN_LAYOUTS:
        return CheckResult(
            "grain_overlay_present", "skip",
            f"layout DNA '{layout_id}' omits GrainOverlay by design",
        )

    grain = ctx.site_dir / "components" / "ui" / "GrainOverlay.tsx"
    if grain.exists():
        return CheckResult("grain_overlay_present", "pass", "GrainOverlay.tsx present")
    return CheckResult(
        "grain_overlay_present", "fail",
        "components/ui/GrainOverlay.tsx missing — cinematic grain layer required",
    )


# ---------------------------------------------------------------------------
# 41. framer_motion_in_dependencies — FOUNDATION (cinematic system, May 2026)
# ---------------------------------------------------------------------------


@check_metadata(static_files=("package.json",))
def framer_motion_in_dependencies(ctx: BuildContext) -> CheckResult:
    """package.json must declare framer-motion as a dependency.

    The cinematic system's ScrollReveal and MagneticButton components import
    from framer-motion. A missing declaration causes npm install failures on
    first deploy — same class of regression as the Ironwood react-icons
    incident (May 2026).
    """
    if not ctx.site_dir.exists():
        return CheckResult("framer_motion_in_dependencies", "skip", "no site directory")
    pkg = ctx.site_dir / "package.json"
    if not pkg.exists():
        return CheckResult("framer_motion_in_dependencies", "fail", "package.json missing")
    text = pkg.read_text(encoding="utf-8", errors="ignore")
    clean = _JSONC_COMMENT_RE.sub("", text)
    try:
        data = json.loads(clean)
    except json.JSONDecodeError as e:
        return CheckResult(
            "framer_motion_in_dependencies", "fail",
            f"package.json is invalid JSON: {e}",
        )
    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
    if "framer-motion" in deps:
        return CheckResult(
            "framer_motion_in_dependencies", "pass",
            f"framer-motion {deps['framer-motion']} declared in dependencies",
        )
    return CheckResult(
        "framer_motion_in_dependencies", "fail",
        "package.json missing framer-motion — ScrollReveal and MagneticButton require it",
    )


# ---------------------------------------------------------------------------
# 42. hero_uses_gradient_mesh — FOUNDATION (cinematic system, May 2026)
# ---------------------------------------------------------------------------

_GRADIENT_MESH_RE = re.compile(
    r"--color-accent-glow|conic-gradient|gradient-mesh|radial-gradient.*color-accent",
    re.IGNORECASE,
)


@check_metadata(static_files=("components/sections/Hero.tsx",))
def hero_uses_gradient_mesh(ctx: BuildContext) -> CheckResult:
    """Hero.tsx must use a CSS gradient mesh (--color-accent-glow or conic/radial-gradient).

    The cinematic system requires the gradient_mesh layout to use an ambient-light
    blob background. Flat heroes kill the DNA's atmospheric depth.

    LAYOUT DNA AWARENESS: layouts whose hero_type is NOT gradient_mesh legitimately
    use a different background treatment (split-screen photo, pure type, masonry
    grid, terminal prompt). When one of those layouts is active, this check skips.
    """
    if not ctx.site_dir.exists():
        return CheckResult("hero_uses_gradient_mesh", "skip", "no site directory")

    # Non-gradient-mesh layouts by design
    _NON_GRADIENT_LAYOUTS = {
        "split_screen", "magazine_scroll", "manifesto", "terminal",
        "weather_report", "chat_log", "index_card", "gallery_first", "single_screen",
    }
    layout_id = (ctx.brief.get("_layout_dna_id") or "gradient_mesh").strip()
    if layout_id in _NON_GRADIENT_LAYOUTS:
        return CheckResult(
            "hero_uses_gradient_mesh", "skip",
            f"layout DNA '{layout_id}' uses a non-mesh hero by design — gradient mesh not required",
        )

    hero = ctx.site_dir / "components" / "sections" / "Hero.tsx"
    if not hero.exists():
        return CheckResult("hero_uses_gradient_mesh", "skip", "Hero.tsx not found")
    src = hero.read_text(encoding="utf-8", errors="ignore")
    if _GRADIENT_MESH_RE.search(src):
        return CheckResult("hero_uses_gradient_mesh", "pass", "gradient mesh pattern found in Hero.tsx")
    return CheckResult(
        "hero_uses_gradient_mesh", "fail",
        "Hero.tsx has no CSS gradient mesh — add a radial/conic gradient using --color-accent-glow "
        "so the DNA's atmospheric depth is present",
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
    layout_is_server_component,
    scroll_trigger_ssr_safe,
    no_css_smooth_scroll,
    # FOUNDATION checks (May 2026 overhaul — cinematic hero pattern)
    hero_uses_animated_heading,
    inter_font_global,
    inter_font_applied,
    liquid_glass_class_present,
    animation_components_present,
    client_components_have_directive,
    prefers_reduced_motion_respected,
    # FOUNDATION a11y / legibility (May 2026 NLM cross-check addendum)
    animated_heading_screen_reader_safe,
    interactive_elements_have_focus_visible,
    hero_text_has_legibility_safeguard,
    # FOUNDATION functionality (May 2026 Base44/Lovable competitive addendum)
    navbar_present,
    contact_form_uses_server_action,
    email_helper_present,
    resend_in_dependencies,
    imports_resolve_to_dependencies,
    deploy_to_vercel_scaffold,
    env_example_present,
    industry_pages_present,
    plan_present,
    footer_lists_all_pages,
    no_duplicate_inline_forms,
    limitations_disclosed_in_readme,
    no_tracking_by_default,
    no_lorem_ipsum,
    no_gsap_split_text,
    a11y_static_audit,
    schema_org_jsonld_present,
    sitemap_and_robots_present,
    og_social_meta_present,
    favicon_defined,
    # FOUNDATION perf + conversion (May 2026 NLM research addendum — T14/T15/T16)
    perf_budget_or_lighter,
    hero_cta_above_fold,
    mobile_optimized_responsive,
    # FOUNDATION correctness — catches dev URLs + Pages Router regressions
    no_hardcoded_localhost,
    no_pages_router_patterns,
    # FOUNDATION completeness — all four navigable pages + working form
    foundation_pages_present,
    contact_form_has_inputs,
    # FOUNDATION cinematic system (May 2026 pivot — CSS token layer + grain)
    design_tokens_defined,
    grain_overlay_present,
    framer_motion_in_dependencies,
    hero_uses_gradient_mesh,
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
