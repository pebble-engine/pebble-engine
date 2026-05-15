"""Cross-cutting security primitives shared across handlers.

Three things live here:

1. ``require_project_owner`` — gate read/write project routes behind
   ownership. The current rule mirrors ``run_list_projects``: a logged-in
   user can touch their own projects + any unclaimed (legacy) project;
   nothing else.
2. ``client_ip`` — resolve the client IP with explicit trust of
   ``X-Forwarded-For`` only when the immediate peer is in
   ``PEBBLE_TRUSTED_PROXIES``. Without that config, header values are
   ignored — eliminates the rate-limit-bypass and analytics-poisoning
   vectors NotebookLM flagged.
3. ``RateLimiter`` — in-memory token bucket keyed by anything (IP, email,
   slug). Sub-second precision, decays automatically, defaults to closed
   when the bucket is empty.
"""
from __future__ import annotations

import ipaddress
import json
import os
import sys
import threading
import time
from pathlib import Path
from typing import Optional


# --------- Project ownership ----------------------------------------------

def _output_dir() -> Path:
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path(__file__).parent.parent.resolve() / "output"


def _project_owner(slug: str) -> Optional[str]:
    """Return the _user_id stamped in the project's brief, or None for
    unclaimed projects (no brief or no _user_id field)."""
    p = _output_dir() / slug / "brief.json"
    if not p.exists():
        return None
    try:
        brief = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    owner = brief.get("_user_id")
    return owner if isinstance(owner, str) and owner else None


def require_project_owner(handler, slug: str) -> Optional[str]:
    """Return the calling user's id on success, otherwise respond and
    return None.

    Rules:
    - Caller not signed in: 401.
    - Project doesn't exist: 404.
    - Project has an owner that isn't the caller: 403.
    - Project unclaimed (no _user_id): allow — matches dashboard listing.
    """
    project_dir = _output_dir() / slug
    if not project_dir.exists():
        handler._json(404, {"error": f"project not found: {slug}"})
        return None
    try:
        from pebble.server.auth import current_user_id
    except Exception:
        handler._json(500, {"error": "auth subsystem unavailable"})
        return None
    uid = current_user_id(handler)
    if not uid:
        handler._json(401, {"error": "sign in required"})
        return None
    owner = _project_owner(slug)
    if owner and owner != uid:
        handler._json(403, {"error": "not authorized for this project"})
        return None
    return uid


# --------- Trusted-proxy-aware client IP ----------------------------------

def _trusted_proxy_networks() -> list[ipaddress._BaseNetwork]:
    """Parse PEBBLE_TRUSTED_PROXIES (comma-separated CIDRs).

    Empty/unset = no trusted proxies, so X-Forwarded-For is ignored.
    """
    raw = os.environ.get("PEBBLE_TRUSTED_PROXIES", "") or ""
    out: list[ipaddress._BaseNetwork] = []
    for part in raw.split(","):
        s = part.strip()
        if not s:
            continue
        try:
            out.append(ipaddress.ip_network(s, strict=False))
        except Exception:
            continue
    return out


def _is_trusted_proxy(ip: str) -> bool:
    if not ip:
        return False
    try:
        addr = ipaddress.ip_address(ip)
    except Exception:
        return False
    for net in _trusted_proxy_networks():
        if addr in net:
            return True
    return False


def client_ip(handler) -> Optional[str]:
    """Resolve the calling client's IP.

    Only honors ``X-Forwarded-For`` when the immediate peer is in
    ``PEBBLE_TRUSTED_PROXIES``. Otherwise returns the raw peer address.
    """
    try:
        peer = handler.client_address[0]
    except Exception:
        peer = None
    fwd = handler.headers.get("X-Forwarded-For") if hasattr(handler, "headers") else None
    if fwd and peer and _is_trusted_proxy(peer):
        # XFF is "client, proxy1, proxy2"; the client is the left-most.
        first = fwd.split(",", 1)[0].strip()
        return first or peer
    return peer


# --------- Rate limiter ----------------------------------------------------

class RateLimiter:
    """Token-bucket rate limiter keyed by an opaque string.

    ``allow(key)`` returns True if the request fits the current budget,
    False if it must be rejected. Tokens refill at ``rate`` per second,
    capped at ``burst``. Buckets idle for more than ``decay_seconds``
    are pruned on the next access.

    All state is in-memory; this is per-process. Pebble runs as one
    process so that's correct today. If we ever scale out, swap for
    a Redis-backed equivalent.
    """

    def __init__(self, *, rate: float, burst: int, decay_seconds: float = 600.0) -> None:
        if rate <= 0 or burst <= 0:
            raise ValueError("rate and burst must be positive")
        self._rate = float(rate)
        self._burst = int(burst)
        self._decay = float(decay_seconds)
        self._lock = threading.Lock()
        self._buckets: dict[str, tuple[float, float]] = {}  # key -> (tokens, last_refill_ts)

    def allow(self, key: str) -> bool:
        if not key:
            return True  # never block unkeyed callers (caller can short-circuit)
        now = time.monotonic()
        with self._lock:
            self._gc(now)
            tokens, last = self._buckets.get(key, (float(self._burst), now))
            # Refill
            elapsed = max(0.0, now - last)
            tokens = min(float(self._burst), tokens + elapsed * self._rate)
            if tokens >= 1.0:
                tokens -= 1.0
                self._buckets[key] = (tokens, now)
                return True
            self._buckets[key] = (tokens, now)
            return False

    def reset(self, key: str) -> None:
        with self._lock:
            self._buckets.pop(key, None)

    def _gc(self, now: float) -> None:
        # Cheap pass — only walks every ~100 accesses to avoid O(n) per call.
        if len(self._buckets) < 256:
            return
        cutoff = now - self._decay
        dead = [k for k, (_, t) in self._buckets.items() if t < cutoff]
        for k in dead:
            self._buckets.pop(k, None)


# Pre-built limiters used across handlers. Module-level so they share
# state across requests.
forms_submit_limiter   = RateLimiter(rate=1/6.0,    burst=10)    # 10 / minute, ~600 / hour burst-friendly
track_view_limiter     = RateLimiter(rate=2.0,      burst=20)    # 120 / minute / IP
forgot_email_limiter   = RateLimiter(rate=1/300.0,  burst=3)     # 3 then 1 / 5 min / email


__all__ = [
    "RateLimiter",
    "client_ip",
    "require_project_owner",
    "forms_submit_limiter",
    "track_view_limiter",
    "forgot_email_limiter",
]
