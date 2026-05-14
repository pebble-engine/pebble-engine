"""Tests for pebble.repair — the critique-and-fix loop.

All tests use a FakeClient — no live LLM calls. The synthetic
``broken_build`` fixture fails two specific checks (missing app/page.tsx,
DNA display_font not honored) to mirror sentinel-hvac-e2e-2's real
failure profile, so the test surface tracks the production proof point.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pebble.evals import BuildContext
from pebble.evals.runner import CheckResult
from pebble.repair import (
    REPAIR_SYSTEM,
    build_repair_prompt,
    files_for_failure,
    repair_build,
)


# ---------------------------------------------------------------------------
# FakeClient — mocks the LLM client interface used by repair_build
# ---------------------------------------------------------------------------

def _write_foundation_files(site: Path) -> None:
    """Write the May 2026 foundation files (Inter, AnimatedHeading, FadeIn,
    liquid-glass, reduced-motion, video hero) into a synthetic site dir so
    inline fixtures pass the new FOUNDATION eval checks without duplicating
    50 lines of boilerplate each.

    The components are minimal but satisfy all FOUNDATION checks including
    the May 2026 a11y/legibility addendum: AnimatedHeading wraps decoration
    in aria-hidden and exposes sr-only semantic text; the hero video has
    a poster attribute; AnimatedHeading carries textShadow."""
    (site / "components" / "sections").mkdir(parents=True, exist_ok=True)
    (site / "components" / "ui").mkdir(parents=True, exist_ok=True)
    (site / "components" / "sections" / "Hero.tsx").write_text(
        'export function Hero() {\n'
        '  return (\n'
        '    <section className="relative min-h-[100dvh] bg-black">\n'
        '      <video autoPlay muted loop playsInline className="absolute inset-0 w-full h-full object-cover" src="/videos/hero.mp4" poster="/images/hero-poster.jpg" />\n'
        '    </section>\n'
        '  );\n'
        '}'
    )
    (site / "components" / "ui" / "AnimatedHeading.tsx").write_text(
        '"use client";\n'
        'export function AnimatedHeading({text}:{text:string}){\n'
        '  return (\n'
        '    <h1 style={{ textShadow: "0 2px 24px rgba(0,0,0,0.5)" }}>\n'
        '      <span className="sr-only">{text}</span>\n'
        '      <span aria-hidden="true">{text}</span>\n'
        '    </h1>\n'
        '  );\n'
        '}'
    )
    (site / "components" / "ui" / "FadeIn.tsx").write_text(
        '"use client";\nexport function FadeIn({children}:{children:any}){return <div>{children}</div>;}'
    )
    # Contact form Server Action scaffold (Resend wiring).
    (site / "app" / "actions").mkdir(parents=True, exist_ok=True)
    (site / "app" / "actions" / "contact.ts").write_text(
        '"use server";\n'
        'export async function submitContactForm(_p:any, _f:FormData) { return { ok: true }; }'
    )
    (site / "components" / "forms").mkdir(parents=True, exist_ok=True)
    (site / "components" / "forms" / "ContactForm.tsx").write_text(
        '"use client";\n'
        'import { useActionState } from "react";\n'
        'import { submitContactForm } from "@/app/actions/contact";\n'
        'export function ContactForm() { const [_, a] = useActionState(submitContactForm, null); return <form action={a} />; }'
    )


def _write_minimal_package_json(site: Path) -> None:
    """Minimal package.json that satisfies resend_in_dependencies. Use this
    alongside _write_foundation_files in inline fixtures that need the
    contact-form scaffold to pass evals."""
    (site / "package.json").write_text(json.dumps({
        "name": "x",
        "dependencies": {"next": "^15.0.0", "react": "^19.0.0", "resend": "^4.0.0"},
    }))


class FakeClient:
    """Returns canned text from ``.generate()``. Tracks calls for assertions."""

    def __init__(self, response: str = "", *, raise_with: Exception | None = None):
        self.response = response
        self.raise_with = raise_with
        self.calls: list[dict] = []
        self.model = "fake-model-1"
        self.provider = "fake"

    def generate(self, system: str, user: str, max_tokens: int = 16000, **_kw) -> str:
        self.calls.append({"system": system, "user": user, "max_tokens": max_tokens})
        if self.raise_with:
            raise self.raise_with
        return self.response


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def broken_build(tmp_path: Path) -> Path:
    """A build that fails three checks the LLM can repair:

    - ``required_files_present`` (missing app/page.tsx)
    - ``hero_has_h1`` (page.tsx missing entirely)
    - ``dna_display_font_honored`` (no Cormorant Garamond — DNA is swiss_magazine)

    Everything else passes, so we can assert on the failures we expect.
    """
    d = tmp_path / "broken-build"
    site = d / "site"
    (site / "app").mkdir(parents=True)
    (site / "components" / "sections").mkdir(parents=True)
    (site / "components" / "ui").mkdir(parents=True)

    (d / "brief.json").write_text(json.dumps({
        "business_name": "Broken Co",
        "business_type": "hvac",
        "phone": "(212) 234-9876",
        "_design_dna": "swiss_magazine",
        "_industry_intel_key": "hvac",
    }))

    (site / "package.json").write_text(json.dumps({"name":"broken","dependencies":{"resend":"^4.0.0"}}))
    (site / "tsconfig.json").write_text(json.dumps({
        "compilerOptions": {"paths": {"@/*": ["./*"]}}
    }))
    (site / "tailwind.config.ts").write_text(
        "export default { theme: { extend: { fontFamily: { sans: ['var(--font-inter)', 'Inter'] } } } }"
    )
    (site / "postcss.config.js").write_text("module.exports = {}")
    (site / "next.config.mjs").write_text("/** @type {import('next').NextConfig} */\nexport default {};\n")
    # Layout includes Inter + brief phone (foundation Inter + no_invented_phone pass).
    # Intentionally lacks Cormorant Garamond so dna_display_font_honored fails.
    (site / "app" / "layout.tsx").write_text(
        'import { Inter } from "next/font/google";\n'
        'import { Hero } from "@/components/sections/Hero";\n'
        'import "./globals.css";\n'
        'const inter = Inter({ subsets: ["latin"], weight: ["300","400","500","600"], variable: "--font-inter" });\n'
        'export default function L({children}: any) {\n'
        '  return <html lang="en" className={inter.variable}><body className={inter.className}><Hero /><footer>(212) 234-9876</footer>{children}</body></html>;\n'
        '}'
    )
    # Intentionally NO app/page.tsx → required_files_present + hero_has_h1 fail.
    (site / "app" / "globals.css").write_text(
        "body { font-family: var(--font-inter), Inter, sans-serif; height: 100dvh; }\n"
        ".liquid-glass { background: rgba(0,0,0,0.4); backdrop-filter: blur(4px); }\n"
        "@media (prefers-reduced-motion: reduce) { * { transition-duration: 0.01ms !important; } }\n"
    )
    # Foundation hero (background video, no overlay, with poster).
    (site / "components" / "sections" / "Hero.tsx").write_text(
        'export function Hero() {\n'
        '  return (\n'
        '    <section className="relative min-h-[100dvh] bg-black">\n'
        '      <video autoPlay muted loop playsInline className="absolute inset-0 w-full h-full object-cover" src="/videos/hero.mp4" poster="/images/hero-poster.jpg" />\n'
        '    </section>\n'
        '  );\n'
        '}'
    )
    # Foundation animation components with a11y wrappers + legibility shadow
    # so the broken_build only fails the three intentional checks.
    (site / "components" / "ui" / "AnimatedHeading.tsx").write_text(
        '"use client";\n'
        'export function AnimatedHeading({text}:{text:string}){\n'
        '  return (\n'
        '    <h1 style={{ textShadow: "0 2px 24px rgba(0,0,0,0.5)" }}>\n'
        '      <span className="sr-only">{text}</span>\n'
        '      <span aria-hidden="true">{text}</span>\n'
        '    </h1>\n'
        '  );\n'
        '}'
    )
    (site / "components" / "ui" / "FadeIn.tsx").write_text(
        '"use client";\nexport function FadeIn({children}:{children:any}){return <div>{children}</div>;}'
    )
    # Contact form scaffold so the new contact_form_uses_server_action check
    # passes — broken_build's three intentional failures stay scoped to
    # required_files_present, hero_has_h1, and dna_display_font_honored.
    (site / "app" / "actions").mkdir(parents=True, exist_ok=True)
    (site / "app" / "actions" / "contact.ts").write_text(
        '"use server";\n'
        'export async function submitContactForm(_p:any, _f:FormData) { return { ok: true }; }'
    )
    (site / "components" / "forms").mkdir(parents=True, exist_ok=True)
    (site / "components" / "forms" / "ContactForm.tsx").write_text(
        '"use client";\n'
        'import { useActionState } from "react";\n'
        'import { submitContactForm } from "@/app/actions/contact";\n'
        'export function ContactForm() { const [_, a] = useActionState(submitContactForm, null); return <form action={a} />; }'
    )
    (site / ".gitignore").write_text("node_modules/\n.next/\n")
    return d


# ---------------------------------------------------------------------------
# files_for_failure — the mapping logic
# ---------------------------------------------------------------------------

def test_files_for_failure_uses_details_for_required_files():
    r = CheckResult(
        name="required_files_present", status="fail",
        message="...", details={"missing": ["app/page.tsx", "tsconfig.json"]},
    )
    assert files_for_failure(r, Path("/fake")) == ["app/page.tsx", "tsconfig.json"]


def test_files_for_failure_uses_details_for_no_invented_phone():
    r = CheckResult(
        name="no_invented_phone", status="fail",
        message="...", details={"files": ["app/page.tsx", "components/Footer.tsx"]},
    )
    files = files_for_failure(r, Path("/fake"))
    assert "app/page.tsx" in files
    assert "components/Footer.tsx" in files


def test_files_for_failure_reads_site_compiles_files_detail():
    """site_compiles now populates details["files"] directly (path extraction
    moved into the check itself per the metadata-driven refactor). repair just
    reads the list — uniform with the other checks that expose details["files"]."""
    r = CheckResult(
        name="site_compiles", status="fail",
        message="...",
        details={
            "first_errors": ["components/Hero.tsx(12,5): error TS2322: x"],
            "files": ["components/Hero.tsx", "app/page.tsx"],
        },
    )
    assert files_for_failure(r, Path("/fake")) == ["components/Hero.tsx", "app/page.tsx"]


def test_files_for_failure_dna_font_lists_canonical_locations():
    r = CheckResult(name="dna_display_font_honored", status="fail", message="...")
    files = files_for_failure(r, Path("/fake"))
    assert "app/globals.css" in files
    assert "tailwind.config.ts" in files
    assert "app/layout.tsx" in files


def test_files_for_failure_no_src_directory_returns_empty():
    """Structural failures don't map to a file; the prompt handles them via prose."""
    r = CheckResult(name="no_src_directory", status="fail", message="...")
    assert files_for_failure(r, Path("/fake")) == []


def test_files_for_failure_html_lang_attr_points_at_layout():
    r = CheckResult(name="html_lang_attr", status="fail", message="...")
    assert files_for_failure(r, Path("/fake")) == ["app/layout.tsx"]


def test_files_for_failure_no_css_smooth_scroll_uses_details_files():
    r = CheckResult(
        name="no_css_smooth_scroll", status="fail",
        message="...", details={"files": ["app/globals.css"]},
    )
    assert files_for_failure(r, Path("/fake")) == ["app/globals.css"]


def test_files_for_failure_scroll_trigger_ssr_safe_uses_details_files():
    r = CheckResult(
        name="scroll_trigger_ssr_safe", status="fail",
        message="...", details={"files": ["components/Motion.tsx"]},
    )
    assert files_for_failure(r, Path("/fake")) == ["components/Motion.tsx"]


def test_files_for_failure_images_have_alt_uses_details_files():
    r = CheckResult(
        name="images_have_alt", status="fail",
        message="...", details={"files": ["app/page.tsx"]},
    )
    assert files_for_failure(r, Path("/fake")) == ["app/page.tsx"]


# ---------------------------------------------------------------------------
# build_repair_prompt — content assertions
# ---------------------------------------------------------------------------

def test_prompt_names_failures_and_embeds_files(broken_build):
    ctx = BuildContext.load(broken_build)
    failed = [
        CheckResult(
            name="required_files_present", status="fail",
            message="1 required file(s) missing",
            details={"missing": ["app/page.tsx"]},
        ),
        CheckResult(
            name="dna_display_font_honored", status="fail",
            message="DNA expected display_font 'Cormorant Garamond', not found",
            details={"expected_font": "Cormorant Garamond"},
        ),
    ]
    prompt = build_repair_prompt(ctx, failed)

    # Names both failures with their messages
    assert "required_files_present" in prompt
    assert "dna_display_font_honored" in prompt
    assert "Cormorant Garamond" in prompt

    # Embeds the current content of the three font-location files
    assert "Inter" in prompt  # current globals.css uses Inter
    assert "tailwind.config.ts" in prompt
    assert "app/globals.css" in prompt

    # Mentions the missing file by name
    assert "app/page.tsx" in prompt

    # Format instruction present
    assert "<pebble-file" in prompt

    # DNA section present
    assert "swiss_magazine" in prompt


def test_prompt_handles_no_src_directory_with_prose_not_file_embed(broken_build):
    ctx = BuildContext.load(broken_build)
    failed = [CheckResult(name="no_src_directory", status="fail", message="src/ exists")]
    prompt = build_repair_prompt(ctx, failed)
    assert "no_src_directory" in prompt
    assert "site/src/" in prompt  # prose mentions the forbidden path


# ---------------------------------------------------------------------------
# repair_build — end-to-end with FakeClient
# ---------------------------------------------------------------------------

def test_repair_short_circuits_when_no_failures(tmp_path):
    """A build that already passes everything → no LLM call, exit clean."""
    # Build a minimal-but-complete build inline (avoid pulling the bigger fixture).
    d = tmp_path / "perfect-build"
    site = d / "site"
    (site / "app").mkdir(parents=True)
    (d / "brief.json").write_text(json.dumps({
        "business_name": "Perfect",
        "business_type": "plumbing",
        "phone": "(212) 234-9876",
        "_design_dna": "swiss_magazine",
    }))
    (site / "package.json").write_text(json.dumps({"name":"x","dependencies":{"resend":"^4.0.0"}}))
    (site / "tsconfig.json").write_text(json.dumps({
        "compilerOptions": {"paths": {"@/*": ["./*"]}}
    }))
    (site / "tailwind.config.ts").write_text(
        "export default { theme: { extend: { fontFamily: { sans: ['var(--font-inter)', 'Inter'], display: ['Cormorant Garamond'] } } } }"
    )
    (site / "postcss.config.js").write_text("module.exports = {}")
    (site / "next.config.mjs").write_text("/** @type {import('next').NextConfig} */\nexport default {};\n")
    (site / "app" / "layout.tsx").write_text(
        'import { Inter } from "next/font/google";\n'
        'const inter = Inter({ subsets: ["latin"], weight: ["300","400","500","600"], variable: "--font-inter" });\n'
        'export default function L({children}: any) { return <html lang="en" className={inter.variable}><body className={inter.className}>{children}</body></html>; }'
    )
    (site / "app" / "page.tsx").write_text(
        'import { Hero } from "@/components/sections/Hero";\n'
        'export default function P() { return <main><Hero /><h1>(212) 234-9876 Cormorant Garamond</h1></main>; }'
    )
    (site / "app" / "globals.css").write_text(
        "body { font-family: var(--font-inter), Inter, 'Cormorant Garamond', sans-serif; height: 100dvh; }\n"
        ".liquid-glass { background: rgba(0,0,0,0.4); backdrop-filter: blur(4px); }\n"
        "@media (prefers-reduced-motion: reduce) { * { transition-duration: 0.01ms !important; } }\n"
    )
    (site / ".gitignore").write_text("node_modules/\n")
    _write_foundation_files(site)

    client = FakeClient(response="should not be called")
    report = repair_build(slug=d.name, client=client, output_dir=tmp_path)
    assert report.rounds == []                       # no rounds run
    assert client.calls == []                        # LLM not called
    assert report.baseline_score == report.final_score


def test_repair_improves_score_and_writes_files(broken_build):
    """Canned response fixes both failures → score goes up, files committed."""
    canned = """<pebble-file path="app/page.tsx">
export default function P() {
  return <main><h1>Welcome to Broken Co</h1><p>Call (212) 234-9876</p></main>;
}
</pebble-file>

<pebble-file path="app/globals.css">
body { font-family: 'Cormorant Garamond', serif; height: 100dvh; }
</pebble-file>
"""
    client = FakeClient(response=canned)
    report = repair_build(
        slug=broken_build.name,
        max_rounds=2,
        client=client,
        output_dir=broken_build.parent,
    )

    # The score improved
    assert report.rounds[0].pass_after > report.rounds[0].pass_before
    assert report.rounds[0].kept is True

    # Files actually written to the canonical site
    page = broken_build / "site" / "app" / "page.tsx"
    css = broken_build / "site" / "app" / "globals.css"
    assert page.exists()
    assert "Welcome to Broken Co" in page.read_text()
    assert "Cormorant Garamond" in css.read_text()

    # repair_history.json persisted
    hist = json.loads((broken_build / "repair_history.json").read_text())
    assert hist["slug"] == broken_build.name
    assert hist["baseline_score"] != hist["final_score"]
    assert hist["rounds"][0]["kept"] is True


def test_repair_does_not_commit_when_score_worsens(broken_build):
    """LLM emits garbage that lowers the score → canonical site untouched.

    Disables provider fallback so a single attempt is exercised; the retry
    path has its own dedicated test below.
    """
    canned = """<pebble-file path="app/globals.css">
body { font-family: 'Helvetica'; height: 100vh; }
</pebble-file>
"""
    client = FakeClient(response=canned)
    css_before = (broken_build / "site" / "app" / "globals.css").read_text()
    report = repair_build(
        slug=broken_build.name,
        max_rounds=2,
        client=client,
        output_dir=broken_build.parent,
        allow_provider_fallback=False,
    )

    assert report.rounds[0].kept is False
    css_after = (broken_build / "site" / "app" / "globals.css").read_text()
    assert css_after == css_before
    assert len(report.rounds) == 1


class SequenceClient:
    """FakeClient variant that returns DIFFERENT responses on successive
    .generate() calls — for exercising the retry-once path."""
    def __init__(self, responses: list[str]):
        self.responses = list(responses)
        self.calls: list[dict] = []
        self.model = "fake-seq-client"
        self.provider = "fake"

    def generate(self, system: str, user: str, max_tokens: int = 16000, **_):
        self.calls.append({"system": system, "user": user})
        if not self.responses:
            return ""
        return self.responses.pop(0)


def test_retry_path_kicks_in_when_primary_does_not_improve(broken_build, monkeypatch):
    """Primary attempt returns garbage; retry returns a real fix. Both attempts
    should appear in rounds, and the retry's kept=True.

    Monkeypatches `_get_alt_client` to return None so the retry exercises the
    same-client path (LLM temperature non-determinism). The alt-provider path
    is exercised by a separate live integration test, not here.
    """
    import pebble.repair as repair_mod
    monkeypatch.setattr(repair_mod, "_get_alt_client", lambda _c: None)

    bad_attempt = """<pebble-file path="app/globals.css">
body { font-family: 'Helvetica'; }
</pebble-file>
"""
    good_attempt = """<pebble-file path="app/page.tsx">
export default function P() { return <main><h1>Hi</h1><p>(212) 234-9876</p></main>; }
</pebble-file>

<pebble-file path="app/globals.css">
body { font-family: 'Cormorant Garamond', serif; height: 100dvh; }
</pebble-file>
"""
    client = SequenceClient([bad_attempt, good_attempt])
    report = repair_build(
        slug=broken_build.name,
        max_rounds=1,  # primary + retry happen WITHIN one round
        client=client,
        output_dir=broken_build.parent,
    )
    assert len(report.rounds) == 2, "expected primary + retry"
    assert report.rounds[0].kept is False and report.rounds[0].is_retry is False
    assert report.rounds[1].kept is True and report.rounds[1].is_retry is True
    assert "Cormorant Garamond" in (broken_build / "site" / "app" / "globals.css").read_text()


def test_get_alt_client_called_on_non_improvement(broken_build, monkeypatch):
    """_get_alt_client is consulted exactly once per non-improving round.
    Records what client gets passed and what the retry uses."""
    import pebble.repair as repair_mod

    sentinel = FakeClient(response="""<pebble-file path="app/page.tsx">
export default function P() { return <main><h1>Hi</h1><p>(212) 234-9876</p></main>; }
</pebble-file>
""")
    sentinel.model = "alt-provider"
    sentinel.provider = "alt-fake"

    calls: list = []
    def fake_alt(current_client):
        calls.append(getattr(current_client, "provider", None))
        return sentinel

    monkeypatch.setattr(repair_mod, "_get_alt_client", fake_alt)

    bad = """<pebble-file path="app/globals.css">
body { /* no improvement */ }
</pebble-file>
"""
    primary = FakeClient(response=bad)
    report = repair_build(
        slug=broken_build.name,
        max_rounds=1,
        client=primary,
        output_dir=broken_build.parent,
    )

    assert calls == ["fake"], "alt-client lookup should pass the primary client"
    # The retry round should record the alt provider
    assert report.rounds[-1].provider == "alt-fake"
    assert report.rounds[-1].is_retry is True


def test_pebble_delete_tag_removes_files(broken_build):
    """LLM emits <pebble-delete/> alongside <pebble-file>; the file is removed
    from the canonical site when the round is kept."""
    # Seed a stray file that the LLM will request to delete.
    stray = broken_build / "site" / "app" / "stray.tsx"
    stray.write_text("// stale\n")
    assert stray.exists()

    canned = """<pebble-file path="app/page.tsx">
export default function P() { return <main><h1>Hi</h1><p>(212) 234-9876</p></main>; }
</pebble-file>
<pebble-delete path="app/stray.tsx"/>
"""
    client = FakeClient(response=canned)
    report = repair_build(
        slug=broken_build.name,
        max_rounds=1,
        client=client,
        output_dir=broken_build.parent,
        allow_provider_fallback=False,
    )
    assert report.rounds[0].kept is True
    assert "app/stray.tsx" in report.rounds[0].deletions_applied
    assert not stray.exists(), "stray.tsx should have been deleted"


def test_pebble_delete_path_traversal_rejected(broken_build):
    """A <pebble-delete> with ../ should be silently ignored, not executed."""
    canned = """<pebble-file path="app/page.tsx">
export default function P() { return <main><h1>X</h1><p>(212) 234-9876</p></main>; }
</pebble-file>
<pebble-delete path="../../../etc/passwd"/>
<pebble-delete path="/absolute/path"/>
"""
    client = FakeClient(response=canned)
    report = repair_build(
        slug=broken_build.name,
        max_rounds=1,
        client=client,
        output_dir=broken_build.parent,
        allow_provider_fallback=False,
    )
    # Neither malicious path should appear in deletions_applied
    assert report.rounds[0].deletions_applied == []


def test_pebble_delete_does_not_prune_protected_directories(tmp_path):
    """If the LLM deletes the only file under app/, the prune logic must NOT
    remove app/ itself — Next.js needs it. Verified directly against the
    internal helper to keep the assertion tight."""
    from pebble.repair import _apply_deletions

    site = tmp_path / "site"
    (site / "app").mkdir(parents=True)
    (site / "app" / "stale.tsx").write_text("// stale\n")
    (site / "public").mkdir()
    (site / "public" / "old.svg").write_text("<svg/>")

    deleted = _apply_deletions(site, ["app/stale.tsx", "public/old.svg"])
    assert "app/stale.tsx" in deleted
    assert "public/old.svg" in deleted
    # Both protected dirs must still exist even though their last file was deleted
    assert (site / "app").exists(), "app/ was pruned — would brick Next.js"
    assert (site / "public").exists(), "public/ was pruned — would brick assets"


def test_pebble_delete_prunes_nested_subdirectory_of_protected_dir(tmp_path):
    """Subdirectories OF protected dirs (e.g. app/legacy/) are still prunable
    when empty — the protection is only at depth 1."""
    from pebble.repair import _apply_deletions

    site = tmp_path / "site"
    (site / "app" / "legacy").mkdir(parents=True)
    (site / "app" / "legacy" / "old.tsx").write_text("// gone\n")
    (site / "app" / "page.tsx").write_text("// real\n")  # keeps app/ non-empty

    _apply_deletions(site, ["app/legacy/old.tsx"])
    assert not (site / "app" / "legacy").exists(), "nested empty dir should be pruned"
    assert (site / "app").exists(), "app/ stays — it has other files"


def test_get_alt_client_returns_none_when_no_keys(monkeypatch):
    """_get_alt_client should return None when the alt provider's API key
    isn't configured — the retry path falls back to the same client
    instead of crashing the loop."""
    import pebble.repair as repair_mod

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    primary = FakeClient()
    primary.provider = "gemini"
    alt = repair_mod._get_alt_client(primary)
    assert alt is None, "expected None when alt provider has no key configured"


def test_round_records_token_telemetry(broken_build):
    """prompt_chars + response_chars + provider land in the RoundReport."""
    canned = """<pebble-file path="app/page.tsx">
export default function P() { return <main><h1>Hi</h1><p>(212) 234-9876</p></main>; }
</pebble-file>
"""
    client = FakeClient(response=canned)
    report = repair_build(
        slug=broken_build.name,
        max_rounds=1,
        client=client,
        output_dir=broken_build.parent,
        allow_provider_fallback=False,
    )
    r = report.rounds[0]
    assert r.prompt_chars > 0
    assert r.response_chars > 0
    assert r.response_chars == len(canned)
    assert r.provider == "fake"


def test_repair_dry_run_does_not_call_llm(broken_build, capsys):
    client = FakeClient(response="should not be called")
    report = repair_build(
        slug=broken_build.name,
        client=client,
        dry_run=True,
        output_dir=broken_build.parent,
    )
    assert client.calls == []
    assert report.dry_run is True
    assert len(report.rounds) == 1
    assert "dry-run" in report.rounds[0].note
    # The prompt was printed
    captured = capsys.readouterr()
    assert "FAILURES TO FIX" in captured.out


def test_repair_propagates_llm_error_into_round_note(broken_build):
    """A raised LLMError on the LLM call → recorded in note, loop stops."""
    from pebble.llm import LLMError
    client = FakeClient(raise_with=LLMError("rate limited"))
    report = repair_build(
        slug=broken_build.name,
        max_rounds=2,
        client=client,
        output_dir=broken_build.parent,
    )
    assert len(report.rounds) == 1
    assert report.rounds[0].kept is False
    assert "rate limited" in report.rounds[0].note


def test_repair_writes_history_even_when_baseline_passes(tmp_path):
    """Persisting history for clean builds keeps the file's presence stable —
    callers can rely on it being there after any repair_build() invocation."""
    d = tmp_path / "perfect-2"
    site = d / "site"
    (site / "app").mkdir(parents=True)
    (d / "brief.json").write_text(json.dumps({
        "business_name": "X", "business_type": "y",
        "phone": "(212) 234-9876", "_design_dna": "swiss_magazine",
    }))
    (site / "package.json").write_text(json.dumps({"name":"x","dependencies":{"resend":"^4.0.0"}}))
    (site / "tsconfig.json").write_text(json.dumps({"compilerOptions": {"paths": {"@/*": ["./*"]}}}))
    (site / "tailwind.config.ts").write_text("export default { theme: { extend: { fontFamily: { sans: ['var(--font-inter)', 'Inter'], display: ['Cormorant Garamond'] } } } }")
    (site / "postcss.config.js").write_text("module.exports = {}")
    (site / "next.config.mjs").write_text("/** @type {import('next').NextConfig} */\nexport default {};\n")
    (site / "app" / "layout.tsx").write_text(
        'import { Inter } from "next/font/google";\n'
        'const inter = Inter({ subsets: ["latin"], weight: ["300","400","500","600"], variable: "--font-inter" });\n'
        'export default function L({children}: any) { return <html lang="en" className={inter.variable}><body className={inter.className}>{children}</body></html>; }'
    )
    (site / "app" / "page.tsx").write_text(
        'import { Hero } from "@/components/sections/Hero";\n'
        'export default function P() { return <main><Hero /><h1>(212) 234-9876 Cormorant Garamond</h1></main>; }'
    )
    (site / "app" / "globals.css").write_text(
        "body { font-family: var(--font-inter), Inter, 'Cormorant Garamond', sans-serif; height: 100dvh; }\n"
        ".liquid-glass { background: rgba(0,0,0,0.4); backdrop-filter: blur(4px); }\n"
        "@media (prefers-reduced-motion: reduce) { * { transition-duration: 0.01ms !important; } }\n"
    )
    (site / ".gitignore").write_text("")
    _write_foundation_files(site)

    client = FakeClient()
    repair_build(slug=d.name, client=client, output_dir=tmp_path)
    assert (d / "repair_history.json").exists()


def test_repair_raises_when_build_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        repair_build(slug="does-not-exist", output_dir=tmp_path, client=FakeClient())


# ---------------------------------------------------------------------------
# REPAIR_SYSTEM smoke — guard against accidental empty system message
# ---------------------------------------------------------------------------

def test_repair_system_mentions_anti_slop_and_dna():
    assert "Design DNA" in REPAIR_SYSTEM
    assert "<pebble-file" in REPAIR_SYSTEM
    assert "TODOs" in REPAIR_SYSTEM
