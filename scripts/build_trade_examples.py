#!/usr/bin/env python3
"""Build Wave-1 trade-pro example sites via build_v2_core.

Iterates pebble.examples_pipeline.trade_briefs.TRADE_BRIEFS and runs the
v2 block engine on each. Prints SSE-style events + the resulting slug /
ok status / any error. Builds land in output/<slug>/; promotion to
pebble/examples/ is a separate step (scripts/promote_example.py).

Usage:
    python scripts/build_trade_examples.py             # build all 8
    python scripts/build_trade_examples.py --only plumber
    python scripts/build_trade_examples.py --only auto    # substring match
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

# Allow running as `python scripts/build_trade_examples.py` from any cwd.
_REPO_ROOT = Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Load .env BEFORE importing build_v2 (which resolves the LLM client at import).
# pebble_engine.py owns the canonical loader; reuse it so behavior stays in sync.
import os  # noqa: E402
_env = _REPO_ROOT / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _, _v = _line.partition("=")
        _k, _v = _k.strip(), _v.strip().strip('"').strip("'")
        if _k and (_k not in os.environ or not os.environ[_k].strip()):
            os.environ[_k] = _v

from pebble.examples_pipeline.trade_briefs import TRADE_BRIEFS  # noqa: E402
from pebble.server.build_v2 import BuildV2Error, build_v2_core  # noqa: E402


def _progress(event: str, data: dict[str, Any]) -> None:
    """SSE-style line printer, mirrors what the v3 workspace feed renders."""
    print(f"  [{event}] {data}")


def _filter(briefs: list[dict], only: str | None) -> list[dict]:
    if not only:
        return briefs
    needle = only.strip().lower()
    return [b for b in briefs if needle in b.get("industry", "").lower()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--only",
        default=None,
        help="substring match against industry; builds only matching briefs",
    )
    args = ap.parse_args(argv)

    briefs = _filter(TRADE_BRIEFS, args.only)
    if not briefs:
        print(f"no briefs matched --only {args.only!r}", file=sys.stderr)
        return 2

    failed = 0
    for brief in briefs:
        print(f"\n=== building {brief['business_name']} ({brief['industry']}) ===")
        try:
            result = build_v2_core(dict(brief), progress_cb=_progress)
        except BuildV2Error as exc:
            print(f"  BUILD FAILED ({exc.status}): {exc.message}", file=sys.stderr)
            failed += 1
            continue
        except Exception as exc:  # noqa: BLE001 — script wants to keep going
            print(f"  BUILD FAILED (unexpected): {exc!r}", file=sys.stderr)
            failed += 1
            continue
        print(
            f"  -> slug={result.get('slug')} "
            f"files={result.get('file_count')} "
            f"elapsed={result.get('elapsed_seconds')}s"
        )

    print(f"\n{len(briefs) - failed}/{len(briefs)} succeeded")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
