"""Guard against truncated/incomplete generated source files.

Real incident (2026-06-08): a Sonnet build wrote components/sections/CtaMinimal.tsx
truncated mid-string (`href="tel:[BUSINESS`) and the engine reported success.
`next dev` is lazy/lenient so it shipped; `next build` (needed to publish) fails.
This guard flags such files via delimiter balance so the engine never reports a
truncated site as a clean build.
"""
from __future__ import annotations

from pebble import codegen_validate as cv


# A realistic truncated component (cut mid-string, scopes left open).
TRUNCATED = '''import { Navbar } from "@/components/layout/Navbar";

export function CtaMinimal() {
  return (
    <section>
      <Link href="/menu">View today's menu</Link>
      <a
        href="tel:[BUSINESS'''

# A complete, valid component — note JSX-text apostrophe ("today's") which a
# naive quote-counter would mis-handle; brace/paren balance must not false-positive.
COMPLETE = '''import { Navbar } from "@/components/layout/Navbar";

export function CtaMinimal() {
  const label = "View today's menu";  // apostrophe in a string is fine
  return (
    <section style={{ padding: "2rem" }}>
      <Navbar />
      <a href="tel:[BUSINESS PHONE]">{label}</a>
    </section>
  );
}
'''


def test_truncated_file_flagged():
    ok, reason = cv.check_source_complete(TRUNCATED)
    assert ok is False
    assert reason  # has a human reason


def test_complete_file_passes():
    ok, reason = cv.check_source_complete(COMPLETE)
    assert ok is True, f"false positive: {reason}"


def test_jsx_text_apostrophes_do_not_false_positive():
    src = '''export function X() {
  return <p>It's a baker's dozen — don't worry, we've got you.</p>;
}
'''
    ok, _ = cv.check_source_complete(src)
    assert ok is True


def test_block_comment_braces_ignored():
    src = '''/* note: handle the { edge case here */
export const A = 1;
'''
    ok, _ = cv.check_source_complete(src)
    assert ok is True


def test_quotes_in_jsx_text_and_urls_do_not_false_positive():
    # Double-quotes in JSX text + a URL with // — neither must trip the guard.
    src = '''export function X() {
  const u = "https://res.cloudinary.com/acct/video.mp4";
  return <p>She said "hello" and it's a baker's dozen.</p>;
}
'''
    ok, reason = cv.check_source_complete(src)
    assert ok is True, f"false positive: {reason}"


def test_find_truncated_files_scans_site(tmp_path):
    site = tmp_path / "site"
    (site / "components" / "sections").mkdir(parents=True)
    (site / "app").mkdir()
    (site / "node_modules" / "junk").mkdir(parents=True)
    good = site / "app" / "page.tsx"
    bad = site / "components" / "sections" / "CtaMinimal.tsx"
    good.write_text(COMPLETE, encoding="utf-8")
    bad.write_text(TRUNCATED, encoding="utf-8")
    # node_modules file must be ignored even if "broken"
    (site / "node_modules" / "junk" / "x.ts").write_text("export const y = (", encoding="utf-8")

    broken = cv.find_truncated_files(site)
    rels = {b["file"] for b in broken}
    assert "components/sections/CtaMinimal.tsx" in rels
    assert "app/page.tsx" not in rels
    assert not any("node_modules" in r for r in rels)
