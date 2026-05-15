"""First-party privacy analytics — page views without fingerprinting.

What we record per page view:

- ``path``         — the path within the user's site
- ``recorded_at``  — UTC timestamp
- ``referrer_host`` — JUST the host of the referer (not the full URL)
- ``visitor_hour`` — SHA-256(IP + UA + ``YYYY-MM-DDTHH``)[:16]; rotates
  every hour so we get session-ish cardinality without ever storing
  an identifier that survives a clock change

What we never store:

- The raw IP address
- The full User-Agent string
- Query strings or fragments from the URL
- Cookies, localStorage IDs, fingerprints, anything device-specific

Storage: ``output/<slug>/analytics/<YYYY-MM-DD>.jsonl`` — one event per
line. Files are append-only and capped at ~10k events/day per project
(beyond that, additional events are silently dropped — abuse signal,
not an accuracy goal).
"""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.parse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


MAX_EVENTS_PER_DAY = 10_000
MAX_PATH_LEN       = 200

# File-size-based cap, used as a cheap proxy for the event-count cap.
# Each event is ~150-220 bytes serialized; 320 bytes/event is a safe
# upper bound that still keeps the daily file under ~3.2 MB at the
# event cap. O(1) `os.path.getsize` replaces the O(n) line count that
# was reading the whole file on every record_page_view call.
_AVG_EVENT_BYTES   = 320
MAX_DAILY_BYTES    = MAX_EVENTS_PER_DAY * _AVG_EVENT_BYTES


def _engine_output_dir() -> Path:
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path(__file__).parent.parent.resolve() / "output"


def _analytics_dir(slug: str) -> Path:
    d = _engine_output_dir() / slug / "analytics"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _today_path(slug: str, when: Optional[datetime] = None) -> Path:
    day = (when or datetime.now(timezone.utc)).strftime("%Y-%m-%d")
    return _analytics_dir(slug) / f"{day}.jsonl"


def _normalize_path(raw: str) -> str:
    """Strip query strings + fragments; cap length. Default to '/'."""
    if not raw or not isinstance(raw, str):
        return "/"
    try:
        parsed = urllib.parse.urlsplit(raw)
        # Reduce to just the path, no scheme/host/query/fragment
        p = parsed.path or "/"
    except Exception:
        p = raw
    return p[:MAX_PATH_LEN] or "/"


def _referrer_host(raw: Optional[str]) -> str:
    if not raw:
        return ""
    try:
        host = urllib.parse.urlsplit(raw).hostname or ""
        return host.lower()[:128]
    except Exception:
        return ""


def _visitor_hour_hash(ip: Optional[str], user_agent: Optional[str], when: Optional[datetime] = None) -> str:
    when = when or datetime.now(timezone.utc)
    key = f"{ip or ''}|{user_agent or ''}|{when.strftime('%Y-%m-%dT%H')}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def record_page_view(
    slug: str,
    *,
    path: str,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    referrer: Optional[str] = None,
    when: Optional[datetime] = None,
) -> bool:
    """Append a page-view event. Returns True if recorded, False if the
    project's daily cap was already hit.

    Cap check is O(1) ``os.path.getsize`` against ``MAX_DAILY_BYTES`` —
    the previous O(n) line count was reading the whole file on every
    write (NotebookLM flagged it as an I/O nightmare under load).
    """
    file_path = _today_path(slug, when)
    try:
        if file_path.exists() and file_path.stat().st_size >= MAX_DAILY_BYTES:
            return False
    except Exception:
        pass

    event = {
        "path":          _normalize_path(path),
        "recorded_at":   (when or datetime.now(timezone.utc)).isoformat(),
        "referrer_host": _referrer_host(referrer),
        "visitor_hour":  _visitor_hour_hash(ip, user_agent, when),
    }
    try:
        with file_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, separators=(",", ":")))
            f.write("\n")
    except Exception:
        return False
    return True


def summarize(slug: str, days: int = 7) -> dict:
    """Aggregate the last ``days`` days. Returns top paths, top referrer
    hosts, day-by-day totals, and an approximate visitor count (unique
    visitor_hour hashes)."""
    today = datetime.now(timezone.utc).date()
    paths: Counter = Counter()
    referrers: Counter = Counter()
    by_day: dict[str, int] = {}
    visitors: set[str] = set()
    total = 0

    for i in range(days):
        day = today - timedelta(days=i)
        file_path = _analytics_dir(slug) / f"{day.isoformat()}.jsonl"
        day_count = 0
        if file_path.exists():
            try:
                with file_path.open("r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            ev = json.loads(line)
                        except Exception:
                            continue
                        paths[ev.get("path", "/")] += 1
                        rh = ev.get("referrer_host", "")
                        if rh:
                            referrers[rh] += 1
                        vh = ev.get("visitor_hour", "")
                        if vh:
                            visitors.add(vh)
                        day_count += 1
                        total += 1
            except Exception:
                pass
        by_day[day.isoformat()] = day_count

    return {
        "slug":              slug,
        "window_days":       days,
        "total_views":       total,
        "approx_visitors":   len(visitors),
        "top_paths":         [{"path": p, "views": c} for p, c in paths.most_common(10)],
        "top_referrer_hosts":[{"host": h, "views": c} for h, c in referrers.most_common(10)],
        "by_day":            [{"date": d, "views": by_day[d]} for d in sorted(by_day.keys())],
    }


__all__ = [
    "MAX_EVENTS_PER_DAY",
    "record_page_view",
    "summarize",
]
