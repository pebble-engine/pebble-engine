"""Build Integrity — pre-launch checklist (Phase 36, 2026-05-21).

A curated subset of the full eval suite, surfaced to users as a visible
"is this site ready to publish?" checklist that animates pass-by-pass
during the publish flow. The diagram's Phase-4 "Build Integrity" panel.

Why a curated subset, not the full suite:

  - The full suite has 50+ checks tuned for internal QA (DNA fidelity,
    anti-slop patterns, prompt-template invariants). Most are noise to
    a non-technical user about to click "publish."
  - The diagram's checklist mood is "infrastructure looks healthy" —
    short labels, concrete subjects, professional vocabulary.
  - We want EVERY item to pass on a healthy build. If we surfaced
    every eval, a flaky check on a perfectly-good build would scare
    the user away from publishing.

The curated list (10 items) maps the existing eval functions to
user-readable labels. Adding a new critical check: add a new entry to
CRITICAL_CHECKS, point at an existing check function from
pebble.evals.checks. Don't invent a new check function here — keep eval
logic in one place.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from pebble.evals import checks as eval_checks
from pebble.evals.runner import BuildContext, CheckResult, OUTPUT_DIR


@dataclass(frozen=True)
class IntegrityCheck:
    """One entry on the pre-launch checklist."""
    id:        str                                          # stable key for the UI
    label:     str                                          # user-facing copy
    fn:        Callable[[BuildContext], CheckResult]        # the actual check
    must_pass: bool                                         # blocks publish vs warning-only


# Order matters — the UI displays in this order, animating each step
# as it completes. Group by mental category (structure → content →
# accessibility → SEO → perf) so the progression feels logical.
CRITICAL_CHECKS: list[IntegrityCheck] = [
    # Structure
    IntegrityCheck("plan",       "Build plan generated",            eval_checks.plan_present,                must_pass=True),
    IntegrityCheck("nextjs",     "Next.js project structure valid", eval_checks.next_js_static_check,        must_pass=True),
    IntegrityCheck("pages",      "Foundation pages present",        eval_checks.foundation_pages_present,    must_pass=True),
    # Content quality
    IntegrityCheck("form",       "Contact form wired to email",     eval_checks.contact_form_uses_server_action, must_pass=True),
    IntegrityCheck("navbar",     "Navbar links wired up",           eval_checks.navbar_present,              must_pass=False),
    # Accessibility
    IntegrityCheck("lang",       "Language declared on <html>",     eval_checks.html_lang_attr,              must_pass=True),
    IntegrityCheck("mobile",     "Mobile-optimized + responsive",   eval_checks.mobile_optimized_responsive, must_pass=True),
    # SEO + sharing
    IntegrityCheck("schema",     "Structured data (Schema.org)",    eval_checks.schema_org_jsonld_present,   must_pass=False),
    IntegrityCheck("sitemap",    "Sitemap + robots.txt present",    eval_checks.sitemap_and_robots_present,  must_pass=False),
    # Performance
    IntegrityCheck("perf",       "Performance budget within limits", eval_checks.perf_budget_or_lighter,     must_pass=False),
]


@dataclass(frozen=True)
class IntegrityResult:
    """One row in the API response."""
    id:        str
    label:     str
    status:    str            # "pass" | "fail" | "skip" | "error"
    message:   str
    must_pass: bool

    def to_dict(self) -> dict:
        return {
            "id":        self.id,
            "label":     self.label,
            "status":    self.status,
            "message":   self.message,
            "must_pass": self.must_pass,
        }


def run_integrity(slug: str) -> Optional[list[IntegrityResult]]:
    """Run the curated checklist against a build directory.

    Returns None if the build directory doesn't exist (caller should
    return 404). Returns a list of IntegrityResults — same order as
    CRITICAL_CHECKS — on success.

    Each check is run in isolation; a raising check becomes a `status="error"`
    row rather than crashing the whole run.
    """
    build_dir = OUTPUT_DIR / slug
    if not build_dir.exists() or not (build_dir / "brief.json").exists():
        return None

    ctx = BuildContext.load(build_dir)
    out: list[IntegrityResult] = []
    for entry in CRITICAL_CHECKS:
        try:
            r = entry.fn(ctx)
            out.append(IntegrityResult(
                id=entry.id,
                label=entry.label,
                status=r.status,
                message=r.message,
                must_pass=entry.must_pass,
            ))
        except Exception as e:
            out.append(IntegrityResult(
                id=entry.id,
                label=entry.label,
                status="error",
                message=f"{type(e).__name__}: {e}",
                must_pass=entry.must_pass,
            ))
    return out


def is_publishable(results: list[IntegrityResult]) -> bool:
    """A build is publishable when every must_pass check has status 'pass'.

    Non-must_pass checks can fail without blocking — they show up as
    warnings in the UI, not gates. This matches the diagram's mood:
    nothing blocks the user from publishing if the infrastructure is
    healthy, even if a soft check (e.g. perf budget) is slightly off.
    """
    for r in results:
        if r.must_pass and r.status != "pass":
            return False
    return True
