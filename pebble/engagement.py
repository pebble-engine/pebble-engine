"""Per-user product analytics for the Pebble app itself (T17, 2026-05-17).

PRIVACY MOAT (this is load-bearing — read before changing):

1. We record ONLY ``{event: str, timestamp: ISO8601}``. Never the user's
   content (DNA card name, edited text, color value, etc).
2. The ``user_id`` is the Supabase Auth UUID — already pseudonymous — and
   it's stored as the FILENAME, never inside the event row. So a single
   .jsonl file is unidentifiable on its own.
3. ``log_event()`` rejects user_ids with path-traversal characters so an
   attacker can't write outside the engagement dir.
4. Event NAMES are restricted to ``^[a-z][a-z0-9_]+$`` so a caller can't
   accidentally leak user input by passing it as the event name.

Distinguishing from sibling modules:

- ``pebble.analytics`` — tracks PAGE VIEWS on the customer's GENERATED
  SITE (their visitors). Different surface, different data, different
  retention story.
- The eval ``no_tracking_by_default`` (check #34) governs GENERATED SITES
  not embedding Google Analytics / Meta Pixel / similar. Internal product
  analytics on Pebble's own app surface is a SEPARATE owned surface where
  the user is already authenticated and the data never leaves the engine.
  This module does not violate that eval.

Storage layout::

    output/.engagement/<user_id>.jsonl     # append-only, one event per line

A user with 10 events of 4 distinct types over the last 30 days bucks as
"active" (engagement_score). The bucketing is deliberately coarse — we
want the at-risk signal to be reliable, not precise.

Accepted trade-offs (NLM T17 round 2026-05-17 surfaced, deliberately
not fixed):

- **No filelock around append.** Concurrent log_event calls for the same
  user can theoretically interleave bytes within a line. read_user_events
  silently skips corrupt JSON lines, so the worst case is one lost event,
  not crash or data leak. A filelock would add a hot-path syscall for
  marginal benefit; revisit if interleaving becomes observable.
- **File size unbounded.** A user's total event count is visible via the
  file size on disk and exposed deliberately by the admin endpoint. Both
  surfaces are admin/operator-only (filesystem access already requires
  privilege; the API is gated by PEBBLE_ADMIN_EMAIL). No external visitor
  can observe these counts. Add rotation when this becomes an ops concern.
"""
from __future__ import annotations

import json
import re
import sys
from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Storage location
# ---------------------------------------------------------------------------

def _engagement_dir() -> Path:
    """Resolve the engagement-storage directory.

    Lazy lookup of pebble_engine.OUTPUT_DIR — (a) tests monkey-patch this
    by replacing the function, (b) avoids a circular import at module-load
    time when the server modules wire in engagement.log_event."""
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng is not None and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR")) / ".engagement"
    # CLI / test-without-engine fallback. Should rarely fire in production.
    return Path.cwd() / "output" / ".engagement"


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

# UUIDs from Supabase Auth match this; arbitrary strings with slashes / dots
# / etc do not. Cap at 128 chars to avoid pathological filenames.
_SAFE_USER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

# Event name: snake_case identifier, 1-64 chars, must start with a letter.
# Tight enough that no caller can leak content via the event-name channel.
_SAFE_EVENT_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")

# Windows reserved device names — `CON.jsonl` writes to the console; `NUL`
# silently discards; etc. Supabase UUIDs (36-char hex) never collide with
# these (3-4 chars), but the regex was permissive enough that a future
# caller passing a non-UUID could hit one. Forward-defense per NLM T17
# round 2026-05-17.
_WINDOWS_RESERVED = frozenset(
    {"con", "nul", "aux", "prn"}
    | {f"com{i}" for i in range(1, 10)}
    | {f"lpt{i}" for i in range(1, 10)}
)


def _is_safe_user_id(uid: object) -> bool:
    if not isinstance(uid, str):
        return False
    if not _SAFE_USER_ID_RE.fullmatch(uid):
        return False
    # Reject Windows reserved device names (case-insensitive).
    if uid.lower() in _WINDOWS_RESERVED:
        return False
    return True


def _normalize_user_id(uid: str) -> str:
    """NTFS is case-insensitive — `UserABC.jsonl` and `userabc.jsonl` share
    one inode. Lowercase so the filename is 1:1 with the in-memory key
    across platforms. NLM T17 round 2026-05-17."""
    return uid.lower()


def _is_safe_event_name(name: object) -> bool:
    return isinstance(name, str) and bool(_SAFE_EVENT_NAME_RE.fullmatch(name))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_event(user_id: Optional[str], event_name: str) -> bool:
    """Append one event row to the user's engagement log.

    Returns True if written, False on any validation or I/O failure.
    Callers MUST treat this as best-effort — never raise, never block
    the user-facing response on a failure. The reason for the silent
    False is the wire-in pattern: every server route calls this in a
    fire-and-forget way and a logging failure must not propagate.
    """
    if not _is_safe_user_id(user_id):
        return False
    if not _is_safe_event_name(event_name):
        return False
    uid = _normalize_user_id(user_id)  # type: ignore[arg-type]

    row = {
        "event": event_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    storage = _engagement_dir()
    try:
        storage.mkdir(parents=True, exist_ok=True)
        path = storage / f"{uid}.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")
        return True
    except OSError:
        return False


def read_user_events(user_id: str, limit: int = 1000) -> list[dict]:
    """Return up to ``limit`` most-recent events for ``user_id``.

    Empty list if the user has no log yet (or the id is unsafe).
    Returned chronologically (oldest first) — last ``limit`` entries.

    NLM T17 round 2026-05-17: streams the file line-by-line into a
    bounded deque so memory stays constant regardless of file size.
    The previous read_text-then-slice approach OOM'd on arbitrarily
    large logs."""
    if not _is_safe_user_id(user_id):
        return []
    uid = _normalize_user_id(user_id)
    path = _engagement_dir() / f"{uid}.jsonl"
    if not path.exists():
        return []
    if limit is None or limit <= 0:
        limit = 1000
    tail: deque[str] = deque(maxlen=limit)
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    tail.append(line)
    except OSError:
        return []
    out: list[dict] = []
    for line in tail:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # corrupt or truncated line — skip
    return out


def _distinct_event_count(rows: list[dict], window_days: int) -> tuple[int, int]:
    """Count distinct event-types AND total events within the window.
    Returns (distinct, total). Reused by engagement_score + engagement_summary."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    distinct: set[str] = set()
    total = 0
    for row in rows:
        ts = row.get("timestamp", "")
        if not isinstance(ts, str):
            continue
        try:
            event_ts = datetime.fromisoformat(ts)
        except ValueError:
            continue
        if event_ts.tzinfo is None:
            event_ts = event_ts.replace(tzinfo=timezone.utc)
        if event_ts < cutoff:
            continue
        evt = row.get("event")
        if isinstance(evt, str):
            distinct.add(evt)
            total += 1
    return len(distinct), total


def _bucket(distinct: int) -> str:
    if distinct >= 5:
        return "power"
    if distinct >= 2:
        return "active"
    return "at_risk"


def engagement_score(user_id: str, window_days: int = 30) -> str:
    """Bucket a user as ``power`` / ``active`` / ``at_risk``.

    Buckets by distinct event-types in the last ``window_days``:
    - >= 5 → power (uses many features)
    - 2-4 → active (some breadth)
    - 0-1 → at_risk (stuck or doesn't return)

    Counting distinct types (not total events) is the cheaper signal.
    A user who fires ``build_completed`` 50 times but never tries refine
    or visual-edit is still stuck. Variety beats frequency for retention
    forecasting."""
    rows = read_user_events(user_id, limit=10_000)
    distinct, _ = _distinct_event_count(rows, window_days)
    return _bucket(distinct)


def engagement_summary(window_days: int = 30) -> list[dict]:
    """All users with at least one logged event + their engagement bucket.

    Returns ``[{user_id, score, distinct_events, total_events}, ...]``
    sorted power → active → at_risk, then by distinct_events DESC inside
    each bucket. Admin-only — never expose to non-admins.

    NLM T17 round 2026-05-17: per-user read is capped at 10k events to
    bound memory across the whole summary. A user with >10k events in
    30 days bucks as ``power`` regardless of the exact count, so the
    cap is functionally lossless for the bucketing decision."""
    storage = _engagement_dir()
    if not storage.exists():
        return []
    out: list[dict] = []
    for f in storage.glob("*.jsonl"):
        uid = f.stem
        if not _is_safe_user_id(uid):
            continue
        rows = read_user_events(uid, limit=10_000)
        distinct, total = _distinct_event_count(rows, window_days)
        out.append({
            "user_id": uid,
            "score": _bucket(distinct),
            "distinct_events": distinct,
            "total_events": total,
        })
    score_rank = {"power": 0, "active": 1, "at_risk": 2}
    out.sort(key=lambda x: (score_rank[x["score"]], -x["distinct_events"]))
    return out
