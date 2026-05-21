"""no_invented_time_markers eval tests (Phase 20b, 2026-05-20).

Catches the anti-slop pattern Marc surfaced in the 2026-05-20 mechanic build:

  - "Honest work. Fair pricing. Reliable service - since 2015."
  - "serving Queens drivers since day one."
  - "mechanic shop inqueens uptime: 11 years, 139 days"

None of those numbers were in the brief. The eval treats year markers,
vibey "since X" phrases, and N-years claims as failures unless the brief
itself contains a matching founded_year / years_in_business field.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from pebble.evals.checks import no_invented_time_markers
from pebble.evals.runner import BuildContext


def _ctx(tmp_path: Path, brief: dict | None = None) -> BuildContext:
    site = tmp_path / "site"
    site.mkdir(exist_ok=True)
    (site / "app").mkdir(exist_ok=True)
    (site / "components").mkdir(exist_ok=True)
    return BuildContext(
        slug="test", build_dir=tmp_path, site_dir=site,
        brief=brief or {"business_name": "Test", "business_type": "test"},
        meta={},
    )


def _write(ctx: BuildContext, rel: str, content: str) -> None:
    full = ctx.site_dir / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")


# ------------------------------------------------------------------ #
# Clean site                                                          #
# ------------------------------------------------------------------ #


def test_clean_site_passes():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", "export default function Page() { return <h1>Hi</h1>; }\n")
        assert no_invented_time_markers(ctx).status == "pass"


def test_skip_when_no_site_dir(tmp_path):
    ctx = BuildContext(
        slug="test", build_dir=tmp_path,
        site_dir=tmp_path / "missing",
        brief={}, meta={},
    )
    assert no_invented_time_markers(ctx).status == "skip"


# ------------------------------------------------------------------ #
# Pattern 1: "since YYYY"                                              #
# ------------------------------------------------------------------ #


def test_detects_since_2015_with_no_brief_year():
    """The smoking-gun fixture from Marc's 2026-05-20 mechanic build."""
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "components/Footer.tsx",
               'export default function Footer() {\n'
               '  return <p>Honest work. Fair pricing. Reliable service - since 2015.</p>;\n'
               '}\n')
        result = no_invented_time_markers(ctx)
        assert result.status == "fail"
        assert "components/Footer.tsx" in result.details["files"]


def test_passes_since_2015_when_brief_has_matching_founded_year():
    """If the brief states the year, the LLM is allowed to use it."""
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td), brief={"business_name": "T", "founded_year": 2015})
        _write(ctx, "components/Footer.tsx", '<p>since 2015</p>')
        assert no_invented_time_markers(ctx).status == "pass"


def test_fails_since_when_brief_year_mismatches():
    """Brief says 2018, site says 2015 — fabricated."""
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td), brief={"business_name": "T", "founded_year": 2018})
        _write(ctx, "components/Footer.tsx", '<p>since 2015</p>')
        result = no_invented_time_markers(ctx)
        assert result.status == "fail"


# ------------------------------------------------------------------ #
# Pattern 2: established / founded / est.                              #
# ------------------------------------------------------------------ #


def test_detects_established_year():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>established 2017</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_detects_established_in_year():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>established in 2017</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_detects_est_year_abbreviated():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>Brooklyn Bagels · Est. 2009</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_detects_founded_year():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>founded 1998</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_detects_founded_in_year():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>founded in 1998</p>')
        assert no_invented_time_markers(ctx).status == "fail"


# ------------------------------------------------------------------ #
# Pattern 3: vibey "since day one" — always slop                       #
# ------------------------------------------------------------------ #


def test_detects_since_day_one():
    """'since day one' is the actual phrase from the mechanic build."""
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>serving Queens drivers since day one.</p>')
        result = no_invented_time_markers(ctx)
        assert result.status == "fail"


def test_detects_since_the_beginning():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>since the beginning</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_detects_since_inception():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>since inception</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_vibey_time_fails_even_with_founded_year():
    """Brief has founded_year=2015 but site says 'since day one' — that's
    still slop because day-one is unfalsifiable vibing."""
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td), brief={"business_name": "T", "founded_year": 2015})
        _write(ctx, "app/page.tsx", '<p>serving customers since day one</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_detects_over_a_decade():
    """The exact phrase from the 2026-05-20 wedding-photographer build:
    'over a decade of experience capturing love'."""
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/about/page.tsx",
               '<p>over a decade of experience capturing love</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_detects_over_decades():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>over decades of service</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_detects_decades_of_experience():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>decades of experience</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_detects_for_years():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>serving the community for years</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_detects_for_many_years():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>working with brides for many years</p>')
        assert no_invented_time_markers(ctx).status == "fail"


# ------------------------------------------------------------------ #
# Pattern 4: "N years experience / service / business / uptime"        #
# ------------------------------------------------------------------ #


def test_detects_11_years_uptime():
    """The exact phrase from Marc's mechanic build."""
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "components/Stats.tsx", '<p>uptime: 11 years</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_detects_years_experience():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>15 years experience</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_detects_years_in_business():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>20 years in business</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_detects_for_n_years():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>For 7 years of service</p>')
        assert no_invented_time_markers(ctx).status == "fail"


def test_passes_when_brief_has_matching_years_in_business():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td), brief={"business_name": "T", "years_in_business": 15})
        _write(ctx, "app/page.tsx", '<p>15 years experience</p>')
        assert no_invented_time_markers(ctx).status == "pass"


# ------------------------------------------------------------------ #
# Brief-field aliases — schema flexibility                             #
# ------------------------------------------------------------------ #


def test_accepts_underscored_brief_keys():
    """_founded_year (private form) should be honored same as founded_year."""
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td), brief={"business_name": "T", "_founded_year": 2015})
        _write(ctx, "components/Footer.tsx", '<p>since 2015</p>')
        assert no_invented_time_markers(ctx).status == "pass"


def test_accepts_year_founded_alias():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td), brief={"business_name": "T", "year_founded": 2015})
        _write(ctx, "components/Footer.tsx", '<p>since 2015</p>')
        assert no_invented_time_markers(ctx).status == "pass"


# ------------------------------------------------------------------ #
# Repair-loop details payload                                          #
# ------------------------------------------------------------------ #


def test_failure_includes_offending_files_in_details():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "components/Footer.tsx", '<p>since 2015</p>')
        _write(ctx, "components/Hero.tsx", '<p>serving since day one</p>')
        result = no_invented_time_markers(ctx)
        files = result.details["files"]
        assert "components/Footer.tsx" in files
        assert "components/Hero.tsx" in files


def test_failure_lists_phrase_per_file():
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "components/Footer.tsx", '<p>since 2015 and est. 2018</p>')
        result = no_invented_time_markers(ctx)
        issues = result.details["issues"]
        assert any("since 2015" in i.lower() for i in issues)


# ------------------------------------------------------------------ #
# False-positive guards                                                #
# ------------------------------------------------------------------ #


def test_does_not_flag_4_digit_numbers_that_arent_years():
    """A pricing or product number like '2024 widgets sold' shouldn't fire
    on the year regex — '2024' alone, not in a 'since/est/founded' context."""
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>2024 widgets sold last quarter</p>')
        assert no_invented_time_markers(ctx).status == "pass"


def test_does_not_flag_phone_numbers():
    """A phone like (718) 555-2015 must NOT trigger 'since 2015'."""
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>Call (718) 555-2015</p>')
        assert no_invented_time_markers(ctx).status == "pass"


def test_does_not_flag_unrelated_year_text():
    """'In 2015' or '2015 update' shouldn't fire — only the trust-signal
    framings (since/est/founded)."""
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        _write(ctx, "app/page.tsx", '<p>The 2015 update introduced new features.</p>')
        assert no_invented_time_markers(ctx).status == "pass"


def test_does_not_scan_node_modules():
    """Third-party packages may contain 'since 2015' in their own copy."""
    with tempfile.TemporaryDirectory() as td:
        ctx = _ctx(Path(td))
        # File inside node_modules that says "since 2015" should NOT be scanned
        nm = ctx.site_dir / "node_modules" / "fake-lib"
        nm.mkdir(parents=True)
        (nm / "index.tsx").write_text('<p>fake-lib since 2015</p>', encoding="utf-8")
        # A legitimate file in app/ that's clean
        _write(ctx, "app/page.tsx", '<p>welcome</p>')
        assert no_invented_time_markers(ctx).status == "pass"


# ------------------------------------------------------------------ #
# Registry inclusion                                                   #
# ------------------------------------------------------------------ #


def test_registered_in_ALL_CHECKS():
    from pebble.evals.checks import ALL_CHECKS
    names = [c.__name__ for c in ALL_CHECKS]
    assert "no_invented_time_markers" in names


def test_appears_near_no_invented_phone():
    """The two anti-invention checks should sit together for readability."""
    from pebble.evals.checks import ALL_CHECKS
    names = [c.__name__ for c in ALL_CHECKS]
    phone_idx = names.index("no_invented_phone")
    time_idx = names.index("no_invented_time_markers")
    # Adjacent
    assert abs(phone_idx - time_idx) == 1
