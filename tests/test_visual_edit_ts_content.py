"""Regression: click-to-edit text must work on TEMPLATE sites.

Template-instantiated sites store copy in `content/site.ts` as exported
constants (`export const HERO_HEADLINE = "..."`) and render `{HERO_HEADLINE}`
in the component. The visual-edit text op fell back to a global substring
search (`_edit_text`) that only scanned .tsx/.jsx/.html/.css — never .ts —
so the literal in content/site.ts was never found. The endpoint then returned
200 "success" with zero changes, so the UI lied ("Text updated") while the
headline stayed the same.

Fix: `_edit_text` now also searches `**/*.ts` (excluding build dirs), so the
constant's string value is found and replaced.
"""
from pathlib import Path

from pebble.server.visual_edit import _edit_text


def _make_template_site(tmp_path: Path) -> Path:
    site = tmp_path / "site"
    (site / "content").mkdir(parents=True)
    (site / "components" / "sections").mkdir(parents=True)
    (site / "content" / "site.ts").write_text(
        'export const HERO_HEADLINE = "Your wedding day, done beautifully.";\n'
        'export const ABOUT_BODY = "We plan weddings on Long Island.";\n',
        encoding="utf-8",
    )
    (site / "components" / "sections" / "Hero.tsx").write_text(
        'import { HERO_HEADLINE } from "@/content/site";\n'
        'export default function Hero() {\n'
        '  return <h1 data-pebble-id="pb-hero">{HERO_HEADLINE}</h1>;\n'
        '}\n',
        encoding="utf-8",
    )
    return site


def test_text_edit_reaches_content_site_ts(tmp_path):
    site = _make_template_site(tmp_path)
    result = _edit_text(
        site,
        "Your wedding day, done beautifully.",
        "Your perfect day, beautifully planned.",
    )
    site_ts = (site / "content" / "site.ts").read_text(encoding="utf-8")
    assert "Your perfect day, beautifully planned." in site_ts
    assert "Your wedding day, done beautifully." not in site_ts
    assert "content/site.ts" in result["files_changed"]
    assert result["replacements"] >= 1


def test_no_match_reports_zero_changes(tmp_path):
    """A genuinely unmatchable edit must report no files changed (so the UI
    can tell the truth instead of a false success)."""
    site = _make_template_site(tmp_path)
    result = _edit_text(site, "This text is nowhere on the site.", "x")
    assert result["files_changed"] == []
    assert result["replacements"] == 0


def test_node_modules_is_not_scanned(tmp_path):
    """Adding .ts to the search must NOT pull in node_modules (perf + safety):
    a matching string buried in a dependency must be left untouched."""
    site = _make_template_site(tmp_path)
    dep = site / "node_modules" / "somepkg"
    dep.mkdir(parents=True)
    (dep / "index.ts").write_text(
        'const x = "Your wedding day, done beautifully.";\n', encoding="utf-8"
    )
    _edit_text(site, "Your wedding day, done beautifully.", "Replaced.")
    dep_text = (dep / "index.ts").read_text(encoding="utf-8")
    assert "Your wedding day, done beautifully." in dep_text  # untouched
