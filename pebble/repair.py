"""Pebble Engine — critique-and-fix loop.

Reads a build's eval results, builds a focused repair prompt naming
specific failures + their likely-responsible files, calls the same LLM
as the original build, parses the response, writes corrected files,
re-runs evals. Repeats up to ``max_rounds`` rounds.

The loop only commits a round's output when the score actually improves;
an LLM that worsens a build is wasted tokens, not progress. A round
that doesn't improve also halts further rounds — same prompt would
produce similar output, so the marginal call is unlikely to pay off.

Use:
    python -m pebble.repair <slug>                # up to 2 rounds
    python -m pebble.repair <slug> --max-rounds 4
    python -m pebble.repair <slug> --dry-run      # build prompt, no LLM
    python -m pebble.repair <slug> --with-compile # include tsc in evals

API:
    from pebble.repair import repair_build
    report = repair_build("sentinel-hvac-e2e-2", max_rounds=2)
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from pebble.evals import ALL_CHECKS, BuildContext, OUTPUT_DIR
from pebble.evals.checks import site_compiles
from pebble.evals.runner import CheckResult
from pebble.llm import LLMError, get_llm_client
from pebble.log import log


# ---------------------------------------------------------------------------
# Check → likely-responsible-files mapping
# ---------------------------------------------------------------------------

# Some checks point at the exact failing files via their ``details`` payload
# (required_files_present, images_use_next_image, etc.) — we read those at
# runtime. Others always live in the same place in a Next 14 project; those
# hints are hard-coded here.
_STATIC_FILE_HINTS: dict[str, tuple[str, ...]] = {
    "tsconfig_paths_alias":     ("tsconfig.json",),
    "next_config_is_mjs":       ("next.config.mjs",),
    "dna_display_font_honored": (
        "app/globals.css",
        "tailwind.config.ts",
        "app/layout.tsx",
    ),
    "hero_has_h1":              ("app/page.tsx",),
    "html_lang_attr":           ("app/layout.tsx",),
    # no_src_directory is structural — no specific file to embed; prose only.
}

# Checks that surface offending paths via ``details["files"]``. Keep this in
# sync with the checks themselves; a missing entry here means repair falls
# back to the no-mapping prose default, which still works but ignores the
# specific files the check already pinpointed.
_CHECKS_WITH_FILES_DETAIL = frozenset({
    "images_use_next_image",
    "images_have_alt",
    "no_invented_phone",
    "uses_100dvh_not_100vh",
    "scroll_trigger_ssr_safe",
    "no_css_smooth_scroll",
})


def files_for_failure(result: CheckResult, site_dir: Path) -> list[str]:
    """Relative paths inside ``site_dir`` likely responsible for ``result``.

    Empty list means "no specific file" — the prompt will fall back to prose.
    """
    name = result.name
    details = result.details or {}

    if name == "required_files_present":
        return list(details.get("missing") or [])

    if name in _CHECKS_WITH_FILES_DETAIL:
        return list(details.get("files") or [])

    if name == "site_compiles":
        # tsc errors look like "components/Foo.tsx(12,5): error TS2322: ..."
        # Take everything before the first "(" on each line.
        out: list[str] = []
        for line in details.get("first_errors", []):
            head = line.split("(", 1)[0].strip()
            if head and head not in out:
                out.append(head)
        return out

    return list(_STATIC_FILE_HINTS.get(name, ()))


# ---------------------------------------------------------------------------
# Repair prompt
# ---------------------------------------------------------------------------

REPAIR_SYSTEM = (
    "You are repairing a previously generated website. The original build "
    "passed most quality checks but failed a few specific ones. Your job is "
    "to emit replacement files for ONLY the failures listed in the user "
    "message — do not regenerate unrelated files. Files you don't emit will "
    "be left as-is.\n\n"

    "RULES:\n"
    "1. Output ONLY <pebble-file> blocks. No preamble. No plan. First char is `<`.\n"
    "2. Every emitted file must be complete. Zero TODOs. Zero stubs.\n"
    "3. Honor the existing Design DNA — fonts, hero structure, motion language. "
    "Do not substitute defaults like Inter/Fraunces.\n"
    "4. Anti-slop rules still apply: no fake testimonials, no invented phone "
    "numbers, real headlines.\n"
    "5. iOS rules still apply: 100dvh not 100vh, all autoplay video has "
    "muted+playsInline+loop, form inputs >= 16px font-size.\n"
    "6. Tooling rules still apply: next/image only (no raw <img>), tsconfig "
    "paths {\"@/*\": [\"./*\"]}, next.config.mjs only, no site/src/."
)


def _read_file_safe(path: Path, max_chars: int = 8000) -> str:
    """Read ``path``; return a placeholder if missing, truncate if oversized."""
    if not path.exists():
        return "(file does not exist — generate it from scratch)"
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        return f"(read failed: {e})"
    if len(text) > max_chars:
        return text[:max_chars] + f"\n\n... (truncated; original was {len(text)} chars)"
    return text


def build_repair_prompt(ctx: BuildContext, failed: list[CheckResult]) -> str:
    """Construct the focused repair prompt.

    Names each failure, embeds the current contents of likely-responsible
    files, and ends with a minimal output-format instruction.
    """
    brief_for_prompt = dict(ctx.brief)
    brief_for_prompt.pop("design_reference_images", None)
    brief_json = json.dumps(brief_for_prompt, indent=2)

    parts: list[str] = []
    parts.append(
        f"The previous build of \"{ctx.brief.get('business_name', ctx.slug)}\" "
        f"failed {len(failed)} quality check(s) against the Pebble eval suite. "
        "Fix ONLY the named failures. Do not modify unrelated files. Keep the "
        "existing DNA, structure, and design language.\n"
    )
    parts.append("## BRIEF (unchanged)\n```json\n" + brief_json + "\n```\n")

    dna_id = ctx.brief.get("_design_dna", "")
    if dna_id:
        parts.append(
            f"## DESIGN DNA: {dna_id}\n"
            "The DNA card chosen for this build is the highest authority on visual "
            "choices — fonts, hero structure, motion. Honor it. Do not substitute.\n"
        )

    parts.append("## FAILURES TO FIX\n")

    for i, r in enumerate(failed, start=1):
        parts.append(f"### {i}. `{r.name}`\n**Failure:** {r.message}\n")

        if r.name == "no_src_directory":
            parts.append(
                "**ACTION:** Do NOT place any files under `site/src/`. Every file "
                "lives at the project root — `app/`, `components/`, `lib/`, `config/`, "
                "`public/` are direct children. The tsconfig path alias `@/*` resolves "
                "to `./*` from the project root.\n"
            )
            continue

        files = files_for_failure(r, ctx.site_dir)
        if not files:
            parts.append(
                "**ACTION:** No specific files identified. Regenerate the most "
                "likely candidates based on the failure message above.\n"
            )
            continue

        parts.append("**Likely-responsible files (current contents below):**\n")
        for rel in files:
            parts.append(f"\n#### `{rel}`\n```\n{_read_file_safe(ctx.site_dir / rel)}\n```\n")

    parts.append(
        "\n## OUTPUT FORMAT\n"
        "Return ONLY `<pebble-file>` blocks for the files you are replacing or creating. "
        "No commentary. First character of the response is `<`.\n\n"
        "```\n"
        "<pebble-file path=\"app/page.tsx\">\n"
        "...complete file contents...\n"
        "</pebble-file>\n"
        "```\n\n"
        "Only emit blocks for files you are actually changing or creating. Every "
        "file you emit must be complete — zero TODOs, zero stubs."
    )

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Report dataclasses
# ---------------------------------------------------------------------------

@dataclass
class RoundReport:
    round: int
    failed_checks: list[str]
    files_requested: list[str]
    elapsed_seconds: float
    score_before: str
    score_after: str
    pass_before: int
    pass_after: int
    files_written: list[str]
    kept: bool
    note: str = ""


@dataclass
class RepairReport:
    slug: str
    started_at: str
    max_rounds: int
    dry_run: bool
    baseline_score: str
    final_score: str
    rounds: list[RoundReport] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "started_at": self.started_at,
            "max_rounds": self.max_rounds,
            "dry_run": self.dry_run,
            "baseline_score": self.baseline_score,
            "final_score": self.final_score,
            "rounds": [asdict(r) for r in self.rounds],
        }


# ---------------------------------------------------------------------------
# Core loop
# ---------------------------------------------------------------------------

def _score(results: list[CheckResult]) -> tuple[str, int]:
    p = sum(1 for r in results if r.status == "pass")
    f = sum(1 for r in results if r.status == "fail")
    return f"{p}/{p + f}", p


def _failed(results: list[CheckResult]) -> list[CheckResult]:
    return [r for r in results if r.status == "fail"]


def _run_checks_on(ctx: BuildContext, checks) -> list[CheckResult]:
    """Like run_checks() but takes an already-loaded ctx so we can point at
    a temp site dir for the staging eval."""
    out: list[CheckResult] = []
    for check in checks:
        try:
            out.append(check(ctx))
        except Exception as e:  # noqa: BLE001
            out.append(CheckResult(
                name=check.__name__,
                status="error",
                message=f"check raised: {type(e).__name__}: {e}",
            ))
    return out


def _parse_files(response: str) -> list[tuple[str, str]]:
    """Parse <pebble-file> blocks. Delegates to pebble_engine.parse_files so
    the repair loop never drifts from the engine's tolerant parser."""
    pe = sys.modules.get("pebble_engine")
    if pe is None:
        import pebble_engine as pe  # type: ignore
    return pe.parse_files(response)


def _write_files(target_site: Path, files: list[tuple[str, str]]) -> list[str]:
    """Write parsed files under ``target_site``. Path-traversal guarded."""
    written: list[str] = []
    for path, content in files:
        safe = path.lstrip("/\\")
        if ".." in Path(safe).parts or safe.startswith("/"):
            continue
        full = target_site / safe
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        written.append(safe)
    return written


def repair_build(
    slug: str,
    max_rounds: int = 2,
    dry_run: bool = False,
    skip_compile: bool = True,
    client=None,
    output_dir: Optional[Path] = None,
) -> RepairReport:
    """Run the critique-and-fix loop on a build.

    ``client`` is a duck-typed LLM client with ``.generate(system, user, max_tokens)``.
    Defaults to whatever the engine would pick. Pass an explicit client (or a
    mock) for tests.

    ``output_dir`` overrides the project's ``output/`` root — used in tests.
    ``skip_compile`` (default True) skips ``npx tsc`` in eval rounds; the
    LLM-driven repair pass works on static checks, and tsc takes 10-30s per
    round which makes the loop sluggish for little benefit.
    """
    out_root = output_dir or OUTPUT_DIR
    build_dir = out_root / slug
    if not build_dir.exists() or not (build_dir / "brief.json").exists():
        raise FileNotFoundError(f"build not found: {build_dir}")

    checks = [c for c in ALL_CHECKS if c is not site_compiles] if skip_compile else list(ALL_CHECKS)

    ctx = BuildContext.load(build_dir)
    baseline_results = _run_checks_on(ctx, checks)
    baseline_label, baseline_pass = _score(baseline_results)
    failed_now = _failed(baseline_results)

    report = RepairReport(
        slug=slug,
        started_at=datetime.now().isoformat(),
        max_rounds=max_rounds,
        dry_run=dry_run,
        baseline_score=baseline_label,
        final_score=baseline_label,
    )

    if not failed_now:
        log.info("[repair] %s already passes all checks (%s) — nothing to do",
                 slug, baseline_label)
        _write_history(build_dir, report)
        return report

    if client is None and not dry_run:
        client, reason = get_llm_client()
        if not client:
            raise LLMError(f"LLM not configured: {reason}")

    best_pass = baseline_pass
    best_label = baseline_label

    for round_no in range(1, max_rounds + 1):
        if not failed_now:
            break

        prompt = build_repair_prompt(ctx, failed_now)
        files_targeted = sorted({
            f for r in failed_now for f in files_for_failure(r, ctx.site_dir)
        })

        if dry_run:
            log.info("[repair] dry-run round %d prompt (%d chars):", round_no, len(prompt))
            print(prompt)
            report.rounds.append(RoundReport(
                round=round_no,
                failed_checks=[r.name for r in failed_now],
                files_requested=files_targeted,
                elapsed_seconds=0.0,
                score_before=best_label,
                score_after=best_label,
                pass_before=best_pass,
                pass_after=best_pass,
                files_written=[],
                kept=False,
                note="dry-run; LLM not called",
            ))
            break

        # Pre-step: a <pebble-file> block can't express "delete this file".
        # For next_config_is_mjs we need to drop any .ts/.js siblings before
        # the LLM emits the .mjs replacement, otherwise both end up coexisting.
        pre_actions: list[str] = []
        if any(r.name == "next_config_is_mjs" for r in failed_now):
            for sibling in ("next.config.ts", "next.config.js"):
                p = ctx.site_dir / sibling
                if p.exists():
                    p.unlink()
                    pre_actions.append(f"deleted {sibling}")

        t0 = time.time()
        try:
            response = client.generate(
                system=REPAIR_SYSTEM,
                user=prompt,
                max_tokens=16000,
            )
        except LLMError as e:
            log.warning("[repair] round %d: LLM call failed: %s", round_no, e)
            report.rounds.append(RoundReport(
                round=round_no,
                failed_checks=[r.name for r in failed_now],
                files_requested=files_targeted,
                elapsed_seconds=round(time.time() - t0, 1),
                score_before=best_label,
                score_after=best_label,
                pass_before=best_pass,
                pass_after=best_pass,
                files_written=[],
                kept=False,
                note=f"LLM error: {e}",
            ))
            break
        elapsed = time.time() - t0

        new_files = _parse_files(response)

        # Stage in a temp site copy. If the score doesn't improve, the canonical
        # site is untouched — no rollback needed.
        with tempfile.TemporaryDirectory(prefix=f"pebble-repair-{slug}-") as td:
            tmp_site = Path(td) / "site"
            shutil.copytree(ctx.site_dir, tmp_site)
            written_tmp = _write_files(tmp_site, new_files)

            tmp_ctx = BuildContext(
                slug=ctx.slug,
                build_dir=build_dir,
                site_dir=tmp_site,
                brief=ctx.brief,
                meta=ctx.meta,
            )
            new_results = _run_checks_on(tmp_ctx, checks)
            new_label, new_pass = _score(new_results)

            improved = new_pass > best_pass
            if improved:
                _write_files(ctx.site_dir, new_files)

        note_bits = []
        if pre_actions:
            note_bits.append("; ".join(pre_actions))
        if not new_files:
            note_bits.append("LLM returned 0 <pebble-file> blocks")

        report.rounds.append(RoundReport(
            round=round_no,
            failed_checks=[r.name for r in failed_now],
            files_requested=files_targeted,
            elapsed_seconds=round(elapsed, 1),
            score_before=best_label,
            score_after=new_label,
            pass_before=best_pass,
            pass_after=new_pass,
            files_written=written_tmp if improved else [],
            kept=improved,
            note=" | ".join(note_bits),
        ))

        if improved:
            best_pass = new_pass
            best_label = new_label
            ctx = BuildContext.load(build_dir)
            failed_now = _failed(_run_checks_on(ctx, checks))
        else:
            log.info("[repair] round %d did not improve (%s -> %s); stopping",
                     round_no, best_label, new_label)
            break

    report.final_score = best_label
    _write_history(build_dir, report)
    return report


def _write_history(build_dir: Path, report: RepairReport) -> None:
    (build_dir / "repair_history.json").write_text(
        json.dumps(report.to_dict(), indent=2), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    # Importing pebble_engine here triggers its .env loader, so GOOGLE_API_KEY
    # (etc.) are visible when get_llm_client() runs. Lazy import keeps the
    # module testable without the engine on sys.path.
    import pebble_engine  # noqa: F401

    parser = argparse.ArgumentParser(
        prog="python -m pebble.repair",
        description="Run the critique-and-fix loop on a Pebble Engine build.",
    )
    parser.add_argument("slug", help="build slug to repair")
    parser.add_argument(
        "--max-rounds", type=int, default=2,
        help="maximum repair rounds (default: 2)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="build the repair prompt and print it; do not call the LLM",
    )
    parser.add_argument(
        "--with-compile", action="store_true",
        help="include site_compiles (tsc --noEmit) in evals (slower; skipped by default)",
    )
    args = parser.parse_args(argv)

    try:
        report = repair_build(
            slug=args.slug,
            max_rounds=args.max_rounds,
            dry_run=args.dry_run,
            skip_compile=not args.with_compile,
        )
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2
    except LLMError as e:
        print(f"LLM error: {e}", file=sys.stderr)
        return 3

    print(f"=== repair: {report.slug} ===")
    print(f"baseline: {report.baseline_score}   final: {report.final_score}")
    for r in report.rounds:
        glyph = "[+]" if r.kept else "[-]"
        print(f"  {glyph} round {r.round}: {r.score_before} -> {r.score_after}"
              f"   (failed: {', '.join(r.failed_checks) or 'none'})")
        if r.files_written:
            print(f"      wrote: {', '.join(r.files_written)}")
        if r.note:
            print(f"      note: {r.note}")

    # Mirror evals CLI: exit non-zero if there are still failing checks.
    try:
        p, total = (int(x) for x in report.final_score.split("/"))
    except ValueError:
        return 1
    return 0 if p == total else 1


if __name__ == "__main__":
    sys.exit(main())
