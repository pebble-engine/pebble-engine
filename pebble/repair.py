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
import os
import shutil
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from pebble.evals import ALL_CHECKS, BuildContext, OUTPUT_DIR, check_file_hints
from pebble.evals.checks import site_compiles
from pebble.evals.runner import CheckResult
from pebble.llm import LLMError, get_llm_client
from pebble.log import log


def files_for_failure(result: CheckResult, site_dir: Path) -> list[str]:
    """Relative paths inside ``site_dir`` likely responsible for ``result``.

    Delegates to :func:`pebble.evals.check_file_hints` so the mapping lives
    on the check itself via the ``@check_metadata`` decorator. An empty list
    means "no specific file" — the prompt falls back to a prose ACTION clause.
    """
    return check_file_hints(result.name, result.details)


# ---------------------------------------------------------------------------
# Repair prompt
# ---------------------------------------------------------------------------

REPAIR_SYSTEM = (
    "You are repairing a previously generated website. The original build "
    "passed most quality checks but failed a few specific ones. Your job is "
    "to emit replacement files for ONLY the failures listed in the user "
    "message — do not regenerate unrelated files. Files you don't emit will "
    "be left as-is.\n\n"

    "OUTPUT TAGS (the only two valid emissions):\n"
    "  <pebble-file path=\"relative/path.tsx\">…contents…</pebble-file>\n"
    "  <pebble-delete path=\"relative/path.tsx\"/>\n"
    "Use <pebble-delete> to request file removal — needed when fixing "
    "structural failures like files placed under site/src/. The path is "
    "validated against the site root; traversal attempts are dropped.\n\n"

    "RULES:\n"
    "1. Output ONLY <pebble-file> blocks and/or <pebble-delete/> tags. No "
    "preamble. No plan. First char is `<`.\n"
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
            # List the actual files under src/ so the LLM has concrete paths
            # to emit `<pebble-delete>` for AND to recreate at the project root.
            src_dir = ctx.site_dir / "src"
            existing: list[str] = []
            if src_dir.exists():
                for p in src_dir.rglob("*"):
                    if p.is_file():
                        existing.append(str(p.relative_to(ctx.site_dir)).replace("\\", "/"))
            parts.append(
                "**ACTION:** Every file under `site/src/` is mis-placed. The `@/*` "
                "tsconfig alias resolves to `./*` from the project root, so files "
                "must live directly under `app/`, `components/`, `lib/`, `config/`, "
                "`public/`. For each file under `src/`:\n"
                "  1. Re-emit it at the correct project-root path via `<pebble-file>`.\n"
                "  2. Emit a `<pebble-delete path=\"src/...\"/>` for the old location.\n"
            )
            if existing:
                parts.append("\n**Current files under `site/src/` (delete these):**\n")
                for path in existing[:50]:  # cap the list
                    parts.append(f"- `{path}`\n")
                if len(existing) > 50:
                    parts.append(f"- ...and {len(existing) - 50} more\n")
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
    # Cost telemetry. The clients don't currently expose token usage on the
    # `.generate()` interface; chars/4 is the standard rough conversion.
    prompt_chars: int = 0
    response_chars: int = 0
    # Which provider produced this round's output ("gemini" / "anthropic" / "fake").
    # Surfaces when the multi-provider fallback kicks in.
    provider: str = ""
    # Files removed via <pebble-delete> tags in the LLM response. Audited so
    # the repair history makes deletions visible at a glance.
    deletions_applied: list[str] = field(default_factory=list)
    # True if this round was a retry attempt after a non-improving round.
    is_retry: bool = False


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


def _engine():
    pe = sys.modules.get("pebble_engine")
    if pe is None:
        import pebble_engine as pe  # type: ignore
    return pe


def _parse_files(response: str) -> list[tuple[str, str]]:
    """Parse <pebble-file> blocks. Delegates to pebble_engine.parse_files so
    the repair loop never drifts from the engine's tolerant parser."""
    return _engine().parse_files(response)


def _parse_deletions(response: str) -> list[str]:
    """Parse <pebble-delete path="..."/> tags. Delegates to pebble_engine."""
    return _engine().parse_deletions(response)


def _is_safe_relative(path: str) -> bool:
    """Reject path-traversal and absolute paths. Used for both writes and deletes."""
    safe = path.lstrip("/\\")
    return not (safe.startswith("/") or ".." in Path(safe).parts)


def _write_files(target_site: Path, files: list[tuple[str, str]]) -> list[str]:
    """Write parsed files under ``target_site``. Path-traversal guarded."""
    written: list[str] = []
    for path, content in files:
        if not _is_safe_relative(path):
            continue
        safe = path.lstrip("/\\")
        full = target_site / safe
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        written.append(safe)
    return written


def _apply_deletions(target_site: Path, paths: list[str]) -> list[str]:
    """Delete each path under ``target_site``. Path-traversal guarded; missing
    files are silently skipped. Empty directories left after deletion are
    pruned bottom-up so structural checks like ``no_src_directory`` clear."""
    deleted: list[str] = []
    for path in paths:
        if not _is_safe_relative(path):
            continue
        safe = path.lstrip("/\\")
        full = target_site / safe
        if not full.exists() or not full.is_file():
            continue
        full.unlink()
        deleted.append(safe)
    # Prune now-empty parent directories under target_site.
    for path in deleted:
        parent = (target_site / path).parent
        while parent != target_site and parent.exists():
            try:
                parent.rmdir()  # only succeeds if empty
            except OSError:
                break
            parent = parent.parent
    return deleted


def _get_alt_client(current_client):
    """Try to instantiate the alternate LLM provider.

    If primary is gemini and ANTHROPIC_API_KEY is set, returns an Anthropic
    client. If primary is anthropic and GOOGLE_API_KEY is set, returns a
    Gemini client. Otherwise None. Lets the repair loop attempt a recovery
    pass with a different model when the primary's output is non-improving.
    """
    current_provider = getattr(current_client, "provider", None)
    saved = os.environ.get("PEBBLE_PROVIDER", "")
    try:
        target = "anthropic" if current_provider == "gemini" else "gemini"
        os.environ["PEBBLE_PROVIDER"] = target
        alt, reason = get_llm_client()
        if alt is not None and getattr(alt, "provider", None) != current_provider:
            return alt
        log.info("[repair] alt provider unavailable: %s", reason)
        return None
    finally:
        if saved:
            os.environ["PEBBLE_PROVIDER"] = saved
        else:
            os.environ.pop("PEBBLE_PROVIDER", None)


def _attempt_round(
    ctx: BuildContext,
    failed_now: list[CheckResult],
    client,
    build_dir: Path,
    checks_list: list,
    best_pass: int,
):
    """One repair attempt: build prompt, call LLM, stage output, eval, decide
    keep-or-revert. Returns a tuple of (RoundReport-friendly fields, improved,
    new_pass, new_label, new_ctx). The canonical site is only mutated when
    improved is True. Returned ctx is refreshed iff improved.

    Used both for the primary round and the retry attempt — keeps the loop
    body small and ensures retry logic exactly mirrors primary logic.
    """
    prompt = build_repair_prompt(ctx, failed_now)
    files_targeted = sorted({
        f for r in failed_now for f in files_for_failure(r, ctx.site_dir)
    })

    t0 = time.time()
    response = client.generate(system=REPAIR_SYSTEM, user=prompt, max_tokens=16000)
    elapsed = time.time() - t0

    new_files = _parse_files(response)
    deletions_requested = _parse_deletions(response)

    with tempfile.TemporaryDirectory(prefix=f"pebble-repair-{ctx.slug}-") as td:
        tmp_site = Path(td) / "site"
        shutil.copytree(ctx.site_dir, tmp_site)
        written_tmp = _write_files(tmp_site, new_files)
        deleted_tmp = _apply_deletions(tmp_site, deletions_requested)

        tmp_ctx = BuildContext(
            slug=ctx.slug, build_dir=build_dir,
            site_dir=tmp_site, brief=ctx.brief, meta=ctx.meta,
        )
        new_results = _run_checks_on(tmp_ctx, checks_list)
        new_label, new_pass = _score(new_results)

        improved = new_pass > best_pass
        if improved:
            _write_files(ctx.site_dir, new_files)
            _apply_deletions(ctx.site_dir, deletions_requested)

    payload = {
        "elapsed_seconds": round(elapsed, 1),
        "files_targeted": files_targeted,
        "new_files": new_files,
        "written_tmp": written_tmp,
        "deleted_tmp": deleted_tmp,
        "new_label": new_label,
        "new_pass": new_pass,
        "prompt_chars": len(prompt),
        "response_chars": len(response),
        "provider": getattr(client, "provider", "unknown"),
    }
    return payload, improved


def repair_build(
    slug: str,
    max_rounds: int = 2,
    dry_run: bool = False,
    skip_compile: bool = True,
    client=None,
    output_dir: Optional[Path] = None,
    allow_provider_fallback: bool = True,
) -> RepairReport:
    """Run the critique-and-fix loop on a build.

    ``client`` is a duck-typed LLM client with ``.generate(system, user, max_tokens)``.
    Defaults to whatever the engine would pick. Pass an explicit client (or a
    mock) for tests.

    ``output_dir`` overrides the project's ``output/`` root — used in tests.
    ``skip_compile`` (default True) skips ``npx tsc`` in eval rounds; the
    LLM-driven repair pass works on static checks.

    ``allow_provider_fallback`` (default True): on a non-improving round,
    attempt one retry — preferring the alternate provider if configured
    (handles non-determinism + cross-provider quality variance). Set False
    to halt immediately on any non-improvement (the old behavior).
    """
    out_root = output_dir or OUTPUT_DIR
    build_dir = out_root / slug
    if not build_dir.exists() or not (build_dir / "brief.json").exists():
        raise FileNotFoundError(f"build not found: {build_dir}")

    checks_list = [c for c in ALL_CHECKS if c is not site_compiles] if skip_compile else list(ALL_CHECKS)

    ctx = BuildContext.load(build_dir)
    baseline_results = _run_checks_on(ctx, checks_list)
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

        prompt_preview = build_repair_prompt(ctx, failed_now)
        files_targeted = sorted({
            f for r in failed_now for f in files_for_failure(r, ctx.site_dir)
        })

        if dry_run:
            log.info("[repair] dry-run round %d prompt (%d chars):", round_no, len(prompt_preview))
            print(prompt_preview)
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
                prompt_chars=len(prompt_preview),
            ))
            break

        # Pre-step: a <pebble-file> block can't express "delete this file"
        # WHEN the LLM doesn't know the file exists. For next_config_is_mjs
        # we drop .ts/.js siblings ourselves — deterministic, doesn't rely
        # on the LLM emitting <pebble-delete>. For no_src_directory, the
        # prompt lists existing src/ files so the LLM CAN emit deletes.
        pre_actions: list[str] = []
        if any(r.name == "next_config_is_mjs" for r in failed_now):
            for sibling in ("next.config.ts", "next.config.js"):
                p = ctx.site_dir / sibling
                if p.exists():
                    p.unlink()
                    pre_actions.append(f"deleted {sibling}")

        # Primary attempt.
        try:
            payload, improved = _attempt_round(
                ctx, failed_now, client, build_dir, checks_list, best_pass,
            )
        except LLMError as e:
            log.warning("[repair] round %d: LLM call failed: %s", round_no, e)
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
                note=f"LLM error: {e}",
                provider=getattr(client, "provider", "unknown"),
            ))
            break

        note_bits = list(pre_actions)
        if not payload["new_files"] and not payload["deleted_tmp"]:
            note_bits.append("LLM returned 0 <pebble-file>/<pebble-delete> tags")

        report.rounds.append(RoundReport(
            round=round_no,
            failed_checks=[r.name for r in failed_now],
            files_requested=files_targeted,
            elapsed_seconds=payload["elapsed_seconds"],
            score_before=best_label,
            score_after=payload["new_label"],
            pass_before=best_pass,
            pass_after=payload["new_pass"],
            files_written=payload["written_tmp"] if improved else [],
            kept=improved,
            note="; ".join(note_bits),
            prompt_chars=payload["prompt_chars"],
            response_chars=payload["response_chars"],
            provider=payload["provider"],
            deletions_applied=payload["deleted_tmp"] if improved else [],
        ))

        if improved:
            best_pass = payload["new_pass"]
            best_label = payload["new_label"]
            ctx = BuildContext.load(build_dir)
            failed_now = _failed(_run_checks_on(ctx, checks_list))
            continue

        # Primary attempt didn't improve. One retry — prefer alt provider
        # if available (handles cross-provider quality variance); else use
        # the same client (handles LLM temperature non-determinism).
        if not allow_provider_fallback:
            log.info("[repair] round %d did not improve; halting (fallback disabled)",
                     round_no)
            break

        retry_client = _get_alt_client(client) or client
        retry_provider = getattr(retry_client, "provider", "unknown")
        log.info("[repair] round %d retrying with provider=%s", round_no, retry_provider)
        try:
            payload, improved = _attempt_round(
                ctx, failed_now, retry_client, build_dir, checks_list, best_pass,
            )
        except LLMError as e:
            log.warning("[repair] round %d retry: LLM call failed: %s", round_no, e)
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
                note=f"retry LLM error: {e}",
                provider=retry_provider,
                is_retry=True,
            ))
            break

        retry_note_bits: list[str] = []
        if not payload["new_files"] and not payload["deleted_tmp"]:
            retry_note_bits.append("LLM returned 0 <pebble-file>/<pebble-delete> tags")

        report.rounds.append(RoundReport(
            round=round_no,
            failed_checks=[r.name for r in failed_now],
            files_requested=files_targeted,
            elapsed_seconds=payload["elapsed_seconds"],
            score_before=best_label,
            score_after=payload["new_label"],
            pass_before=best_pass,
            pass_after=payload["new_pass"],
            files_written=payload["written_tmp"] if improved else [],
            kept=improved,
            note="; ".join(retry_note_bits),
            prompt_chars=payload["prompt_chars"],
            response_chars=payload["response_chars"],
            provider=payload["provider"],
            deletions_applied=payload["deleted_tmp"] if improved else [],
            is_retry=True,
        ))

        if improved:
            best_pass = payload["new_pass"]
            best_label = payload["new_label"]
            ctx = BuildContext.load(build_dir)
            failed_now = _failed(_run_checks_on(ctx, checks_list))
            continue

        log.info("[repair] round %d retry also did not improve; halting", round_no)
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
