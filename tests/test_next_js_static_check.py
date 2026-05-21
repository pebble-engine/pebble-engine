"""next_js_static_check eval tests (Phase 16a, 2026-05-20).

Catches Next.js compile-time gotchas via static analysis. Triggered by
Marc's 2026-05-20 mechanic build that emitted a `next/font` import with
BOTH `weight` AND `axes` set — legal individually, illegal together, and
not caught by any other Pebble eval. After this lands, the repair loop
will auto-fix the class on next iteration.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from pebble.evals.checks import next_js_static_check
from pebble.evals.runner import BuildContext


def _ctx(tmp_path: Path) -> BuildContext:
    """Build a minimal BuildContext pointing at tmp_path/site/."""
    site = tmp_path / "site"
    site.mkdir(exist_ok=True)
    (site / "app").mkdir(exist_ok=True)
    (site / "components").mkdir(exist_ok=True)
    (site / "lib").mkdir(exist_ok=True)
    return BuildContext(
        slug="test", build_dir=tmp_path, site_dir=site,
        brief={"business_name": "Test", "business_type": "test"},
        meta={},
    )


def _write(ctx: BuildContext, rel: str, content: str) -> None:
    full = ctx.site_dir / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")


# ------------------------------------------------------------------ #
# Passes when nothing is wrong                                          #
# ------------------------------------------------------------------ #

def test_clean_site_passes(tmp_path):
    ctx = _ctx(tmp_path)
    _write(ctx, "app/layout.tsx", "// Clean Server Component\nexport default function() {}\n")
    result = next_js_static_check(ctx)
    assert result.status == "pass"


def test_skip_when_no_site_dir(tmp_path):
    ctx = BuildContext(
        slug="test", build_dir=tmp_path,
        site_dir=tmp_path / "missing",
        brief={}, meta={},
    )
    assert next_js_static_check(ctx).status == "skip"


# ------------------------------------------------------------------ #
# Gotcha 1: next/font axes+weight collision (the actual Marc bug)      #
# ------------------------------------------------------------------ #

def test_detects_fraunces_axes_plus_weight():
    """The smoking-gun fixture from Marc's 2026-05-20 mechanic build."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        ctx = _ctx(tmp)
        _write(ctx, "app/layout.tsx", """
import { Inter, Fraunces } from "next/font/google";

const fraunces = Fraunces({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-display",
  axes: ["SOFT"],
});
""")
        result = next_js_static_check(ctx)
        assert result.status == "fail"
        assert "next/font" in result.message.lower() or "weight" in result.message.lower()


def test_passes_with_only_weight_no_axes():
    """The fix shape: pinned weights, no axes."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/layout.tsx", """
import { Fraunces } from "next/font/google";
const fraunces = Fraunces({ subsets: ["latin"], weight: ["400", "500", "600"] });
""")
        assert next_js_static_check(ctx).status == "pass"


def test_passes_with_variable_weight_plus_axes():
    """The other valid combo: variable weight + axes."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/layout.tsx", """
import { Fraunces } from "next/font/google";
const fraunces = Fraunces({ subsets: ["latin"], weight: "variable", axes: ["SOFT"] });
""")
        # Note: regex only triggers on weight-array-PLUS-axes-array.
        # weight: "variable" + axes: [...] is the LEGAL form, must pass.
        assert next_js_static_check(ctx).status == "pass"


# ------------------------------------------------------------------ #
# Gotcha 2: ScrollTrigger at module level                              #
# ------------------------------------------------------------------ #

def test_detects_scrolltrigger_module_level():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "components/Hero.tsx", """
import { ScrollTrigger } from "gsap/ScrollTrigger";
ScrollTrigger.normalizeScroll(true);
ScrollTrigger.config({ ignoreMobileResize: true });

export default function Hero() {
  return <div>hero</div>;
}
""")
        result = next_js_static_check(ctx)
        assert result.status == "fail"
        assert "scrolltrigger" in result.message.lower() or "module level" in result.message.lower()


def test_passes_scrolltrigger_inside_useeffect():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "components/Hero.tsx", """
import { useEffect } from "react";
import { ScrollTrigger } from "gsap/ScrollTrigger";

export default function Hero() {
  useEffect(() => {
    ScrollTrigger.normalizeScroll(true);
  }, []);
  return <div>hero</div>;
}
""")
        assert next_js_static_check(ctx).status == "pass"


# ------------------------------------------------------------------ #
# Gotcha 3: "use client" on app/layout.tsx                              #
# ------------------------------------------------------------------ #

def test_detects_use_client_on_layout():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/layout.tsx", '"use client";\nexport default function() {}\n')
        result = next_js_static_check(ctx)
        assert result.status == "fail"
        assert "use client" in result.message.lower() or "server component" in result.message.lower()


def test_passes_use_client_on_other_components():
    """"use client" is fine on components — only app/layout.tsx is special."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "components/Hero.tsx", '"use client";\nexport default function() {}\n')
        _write(ctx, "app/layout.tsx", "export default function() {}\n")
        assert next_js_static_check(ctx).status == "pass"


# ------------------------------------------------------------------ #
# Gotcha 4: next/head import (Pages Router pattern)                     #
# ------------------------------------------------------------------ #

def test_detects_next_head_import():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", 'import Head from "next/head";\nexport default function() {}\n')
        result = next_js_static_check(ctx)
        assert result.status == "fail"
        assert "next/head" in result.message.lower()


# ------------------------------------------------------------------ #
# Gotcha 5: next/router import (Pages Router pattern)                   #
# ------------------------------------------------------------------ #

def test_detects_next_router_import():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", 'import { useRouter } from "next/router";\nexport default function() {}\n')
        result = next_js_static_check(ctx)
        assert result.status == "fail"
        assert "next/router" in result.message.lower() or "next/navigation" in result.message.lower()


def test_passes_next_navigation_import():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", 'import { useRouter } from "next/navigation";\nexport default function() {}\n')
        assert next_js_static_check(ctx).status == "pass"


# ------------------------------------------------------------------ #
# Gotcha 6: document./window. in JSX expression (Phase 29, 2026-05-20) #
# ------------------------------------------------------------------ #
# Caught in the wild on 2026-05-20: Qwen-generated Footer.tsx had
# `document.body.classList.contains("show-grid")` inside both the
# className template literal AND the JSX child expression. 500'd the
# whole page on SSR even though "use client" was set. The eval must
# catch this pattern.


def test_detects_document_in_jsx_attribute():
    """`className={document.body.classList.contains(...) ? ... : ...}` —
    the exact pattern from Marc's 2026-05-20 mechanic Footer."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "components/Footer.tsx", """\
"use client";
export function Footer() {
  return (
    <button
      onClick={() => {}}
      className={`px-4 ${document.body.classList.contains("show-grid") ? 'bg-accent' : ''}`}
    >
      Toggle
    </button>
  );
}
""")
        result = next_js_static_check(ctx)
        assert result.status == "fail"
        assert any("Footer.tsx" in f for f in result.details.get("files", []))


def test_detects_document_in_jsx_child():
    """`{document.body.classList.contains("x") ? "ON" : "OFF"}` — the
    other half of the same Footer bug."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "components/Footer.tsx", """\
"use client";
export function Footer() {
  return (
    <button onClick={() => {}}>
      {document.body.classList.contains("show-grid") ? "HIDE" : "SHOW"}
    </button>
  );
}
""")
        result = next_js_static_check(ctx)
        assert result.status == "fail"


def test_detects_window_in_jsx_template_literal():
    """`className={`w-${window.innerWidth}px`}` — the matchMedia / sizing
    family of failures."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "components/Banner.tsx", """\
"use client";
export function Banner() {
  return <div className={`w-${window.innerWidth}px`}>Hi</div>;
}
""")
        result = next_js_static_check(ctx)
        assert result.status == "fail"


def test_passes_document_inside_useeffect():
    """`useEffect(() => { document.body.classList.add(...) }, [])` is SAFE
    — runs only after hydration. Must NOT flag."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "components/Footer.tsx", """\
"use client";
import { useEffect } from "react";
export function Footer() {
  useEffect(() => {
    document.body.classList.add("ready");
  }, []);
  return <div>hi</div>;
}
""")
        assert next_js_static_check(ctx).status == "pass"


def test_passes_document_with_typeof_guard():
    """`typeof window !== "undefined" && window.matchMedia(...)` — SSR-safe."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "components/Banner.tsx", """\
"use client";
export function Banner() {
  const dark = typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches;
  return <div>{dark ? "Dark" : "Light"}</div>;
}
""")
        assert next_js_static_check(ctx).status == "pass"


def test_passes_document_inside_onclick_handler():
    """`onClick={() => document.body.classList.toggle("x")}` — runs only on
    user click, after hydration. Must NOT flag."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "components/Toggle.tsx", """\
"use client";
export function Toggle() {
  return (
    <button onClick={() => document.body.classList.toggle("dark")}>
      Toggle
    </button>
  );
}
""")
        assert next_js_static_check(ctx).status == "pass"


# ------------------------------------------------------------------ #
# Details payload — repair loop reads this to focus the repair prompt   #
# ------------------------------------------------------------------ #

def test_failure_includes_offending_files_in_details():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/layout.tsx", '"use client";\nexport default function() {}\n')
        _write(ctx, "app/page.tsx", 'import Head from "next/head";\nexport default function() {}\n')
        result = next_js_static_check(ctx)
        assert result.status == "fail"
        files = result.details.get("files", [])
        assert "app/layout.tsx" in files
        assert "app/page.tsx" in files


def test_failure_lists_each_issue():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/layout.tsx", """
import { Fraunces } from "next/font/google";
const fraunces = Fraunces({ subsets: ["latin"], weight: ["400"], axes: ["SOFT"] });
""")
        result = next_js_static_check(ctx)
        assert result.status == "fail"
        issues = result.details.get("issues", [])
        assert len(issues) >= 1


# ------------------------------------------------------------------ #
# Registry inclusion                                                    #
# ------------------------------------------------------------------ #

def test_registered_in_ALL_CHECKS():
    from pebble.evals.checks import ALL_CHECKS
    names = [c.__name__ for c in ALL_CHECKS]
    assert "next_js_static_check" in names


def test_appears_before_site_compiles_in_registry():
    """site_compiles is the slow last check — static_check must run before
    so the repair loop can fix issues without invoking tsc."""
    from pebble.evals.checks import ALL_CHECKS
    names = [c.__name__ for c in ALL_CHECKS]
    static_idx = names.index("next_js_static_check")
    compile_idx = names.index("site_compiles")
    assert static_idx < compile_idx
