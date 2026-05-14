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

    (d / "brief.json").write_text(json.dumps({
        "business_name": "Broken Co",
        "business_type": "hvac",
        "phone": "(212) 234-9876",
        "_design_dna": "swiss_magazine",
        "_industry_intel_key": "hvac",
    }))

    (site / "package.json").write_text('{"name":"broken"}')
    (site / "tsconfig.json").write_text(json.dumps({
        "compilerOptions": {"paths": {"@/*": ["./*"]}}
    }))
    (site / "tailwind.config.ts").write_text(
        "export default { theme: { fontFamily: { display: ['Inter'] } } }"
    )
    (site / "postcss.config.js").write_text("module.exports = {}")
    (site / "next.config.mjs").write_text("export default {}")
    # Layout includes the brief phone so no_invented_phone passes.
    (site / "app" / "layout.tsx").write_text(
        'import "./globals.css";\n'
        'export default function L({children}: any) {\n'
        '  return <html><body>{children}<footer>(212) 234-9876</footer></body></html>;\n'
        '}'
    )
    # Intentionally NO app/page.tsx → required_files_present + hero_has_h1 fail.
    # Inter (not Cormorant Garamond) → dna_display_font_honored fails.
    (site / "app" / "globals.css").write_text(
        "body { font-family: 'Inter', sans-serif; height: 100dvh; }"
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


def test_files_for_failure_parses_tsc_error_paths():
    r = CheckResult(
        name="site_compiles", status="fail",
        message="...",
        details={"first_errors": [
            "components/Hero.tsx(12,5): error TS2322: x is not y",
            "app/page.tsx(3,1): error TS2304: cannot find name 'Foo'",
            "components/Hero.tsx(40,2): error TS2345: again",  # duplicate path
        ]},
    )
    files = files_for_failure(r, Path("/fake"))
    assert files == ["components/Hero.tsx", "app/page.tsx"]  # dedup, ordered


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
    (site / "package.json").write_text('{"name":"x"}')
    (site / "tsconfig.json").write_text(json.dumps({
        "compilerOptions": {"paths": {"@/*": ["./*"]}}
    }))
    (site / "tailwind.config.ts").write_text(
        "export default { theme: { fontFamily: { display: ['Cormorant Garamond'] } } }"
    )
    (site / "postcss.config.js").write_text("module.exports = {}")
    (site / "next.config.mjs").write_text("export default {}")
    (site / "app" / "layout.tsx").write_text(
        'export default function L({children}: any) { return <html lang="en"><body>{children}</body></html>; }'
    )
    (site / "app" / "page.tsx").write_text(
        'export default function P() { return <main><h1>(212) 234-9876</h1></main>; }'
    )
    (site / "app" / "globals.css").write_text("body { font-family: 'Cormorant Garamond'; height: 100dvh; }")
    (site / ".gitignore").write_text("node_modules/\n")

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
    """LLM emits garbage that lowers the score → canonical site untouched."""
    # Replace globals.css with content that drops the existing 100dvh, while
    # NOT fixing the missing page.tsx. New score will be lower.
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
    )

    assert report.rounds[0].kept is False
    # Canonical globals.css preserved (Inter font still there, 100dvh still there)
    css_after = (broken_build / "site" / "app" / "globals.css").read_text()
    assert css_after == css_before
    # The non-improvement breaks the loop after round 1
    assert len(report.rounds) == 1


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
    (site / "package.json").write_text('{"name":"x"}')
    (site / "tsconfig.json").write_text(json.dumps({"compilerOptions": {"paths": {"@/*": ["./*"]}}}))
    (site / "tailwind.config.ts").write_text("export default { theme: { fontFamily: { display: ['Cormorant Garamond'] } } }")
    (site / "postcss.config.js").write_text("module.exports = {}")
    (site / "next.config.mjs").write_text("export default {}")
    (site / "app" / "layout.tsx").write_text('export default function L({children}: any) { return <html lang="en"><body>{children}</body></html>; }')
    (site / "app" / "page.tsx").write_text('export default function P() { return <main><h1>(212) 234-9876</h1></main>; }')
    (site / "app" / "globals.css").write_text("body { font-family: 'Cormorant Garamond'; height: 100dvh; }")
    (site / ".gitignore").write_text("")

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
