"""Format eval results for humans (text) or machines (JSON)."""
from __future__ import annotations

from pebble.evals.runner import CheckResult


# ASCII glyphs (not Unicode) for Windows terminal compatibility — the cp1252
# default codepage chokes on ✓/✗ and crashes print() on a fresh shell.
STATUS_GLYPH = {
    "pass":  "[+]",
    "fail":  "[-]",
    "skip":  "[~]",
    "error": "[X]",
}


def format_text(slug: str, brief: dict, results: list[CheckResult]) -> str:
    """Single-build text report."""
    lines: list[str] = []

    dna = brief.get("_design_dna", "")
    industry = brief.get("_industry_intel_key") or brief.get("business_type") or ""
    extras = " | ".join(x for x in (industry, f"dna: {dna}" if dna else "") if x)

    header = f"=== {slug}"
    if extras:
        header += f"  ({extras})"
    header += " ==="
    lines.append(header)

    for r in results:
        glyph = STATUS_GLYPH.get(r.status, "[?]")
        lines.append(f"  {glyph} {r.name:<32} {r.message}")

    counts = _count_statuses(results)
    gradeable = counts["pass"] + counts["fail"]
    pct = (counts["pass"] / gradeable * 100) if gradeable else 0.0
    summary = f"Score: {counts['pass']}/{gradeable} ({pct:.0f}%)"
    if counts["skip"] or counts["error"]:
        summary += f"   skip={counts['skip']} error={counts['error']}"
    lines.append("")
    lines.append(summary)

    return "\n".join(lines)


def format_summary(rows: list[dict]) -> str:
    """Multi-build summary table. Each row: {slug, dna, pass, fail, skip, error}."""
    if not rows:
        return "(no builds)"

    name_w = max(len("Build"), max(len(r["slug"]) for r in rows))
    dna_w = max(len("DNA"), max(len(r.get("dna") or "") for r in rows))

    header = f"{'Build':<{name_w}}  {'DNA':<{dna_w}}  Score    Pct"
    lines = [header, "-" * len(header)]

    for r in rows:
        gradeable = r["pass"] + r["fail"]
        pct = (r["pass"] / gradeable * 100) if gradeable else 0.0
        score = f"{r['pass']}/{gradeable}"
        suffix = ""
        if r["skip"] or r["error"]:
            suffix = f"   skip={r['skip']} error={r['error']}"
        lines.append(
            f"{r['slug']:<{name_w}}  "
            f"{(r.get('dna') or ''):<{dna_w}}  "
            f"{score:>5}   {pct:>4.0f}%{suffix}"
        )

    return "\n".join(lines)


def to_json(results: list[CheckResult], slug: str, brief: dict) -> dict:
    """Machine-readable representation. Stable shape for downstream tooling."""
    return {
        "slug": slug,
        "dna": brief.get("_design_dna"),
        "industry": brief.get("_industry_intel_key") or brief.get("business_type"),
        "results": [
            {
                "name": r.name,
                "status": r.status,
                "message": r.message,
                "details": dict(r.details) if r.details else {},
            }
            for r in results
        ],
        "summary": _count_statuses(results),
    }


def _count_statuses(results: list[CheckResult]) -> dict:
    out = {"pass": 0, "fail": 0, "skip": 0, "error": 0}
    for r in results:
        if r.status in out:
            out[r.status] += 1
    return out
