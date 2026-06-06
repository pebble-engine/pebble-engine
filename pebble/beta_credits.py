"""Beta credit grants — top up invited testers so a Free account can
run a few real engine builds during the closed beta.

WHY THIS EXISTS
---------------
A full engine build costs ``COST_FULL_ENGINE_BUILD`` (10) credits. The
Free plan deliberately grants only 5/month (see pebble/credits.py) so
that anonymous bot signups can't burn LLM spend — the engine is a paid
path by design. That gate is correct for production.

For a closed beta of ~10 hand-invited testers we still want them to feel
the core "describe → build" flow. Rather than re-pricing the Free plan
globally (which would re-expose prod to bot LLM-burn), we top up ONLY the
invited testers by user_id/email. Targeted, auditable (every grant writes
a REASON_ADMIN_GRANT ledger row), reversible (credits simply get spent,
or Marc can zero them), and adds zero HTTP attack surface — it's a CLI
the operator runs with the service-role key, not a public endpoint.

USAGE
-----
    # Grant 3 builds (default) to each tester, by email or user_id:
    python -m pebble.beta_credits alice@example.com bob@example.com

    # Custom allotment + a dry run that changes nothing:
    python -m pebble.beta_credits alice@example.com --builds 2 --dry-run

Semantics are "ensure at least N builds": if a tester already has enough
credits the grant is a no-op (running it twice never double-grants). The
row's hard_cap is raised to fit the grant when needed; an existing higher
cap is never lowered.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pebble import credits
from pebble.log import log


def _load_env(path: Path) -> None:
    """Stdlib-only .env loader matching pebble_engine.load_env_file so the
    CLI picks up SUPABASE_* without depending on python-dotenv. Existing
    real env vars win over file values."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key and (key not in os.environ or not os.environ[key].strip()):
            os.environ[key] = val


DEFAULT_BETA_BUILDS = 3  # Marc: "small allotment (2-3 builds)"

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ─── Pure helpers (unit-tested) ──────────────────────────────────────── #

def builds_to_credits(builds: int) -> int:
    """Convert a number of engine builds into the credit cost. One build
    costs COST_FULL_ENGINE_BUILD; raises on a non-positive count so a
    typo like ``--builds 0`` fails loudly instead of granting nothing."""
    if builds <= 0:
        raise ValueError(f"builds must be positive, got {builds}")
    return builds * credits.COST_FULL_ENGINE_BUILD


def plan_topup(current_balance: int, current_cap: int, target: int) -> tuple[int, int]:
    """Compute (new_cap, credit_delta) to ensure a row holds at least
    ``target`` credits.

    - new_cap rises to ``target`` when the existing cap is too low to
      hold the grant; an existing higher cap is preserved (never lowered).
    - credit_delta is what we must ADD to reach ``target``; 0 when the
      balance already meets or exceeds it (idempotent — never removes).
    """
    new_cap = max(current_cap, target)
    delta = max(0, target - current_balance)
    return new_cap, delta


def looks_like_email(value: str) -> bool:
    return bool(_EMAIL_RE.match(value.strip()))


def looks_like_uuid(value: str) -> bool:
    return bool(_UUID_RE.match(value.strip()))


# ─── Supabase-touching ops ───────────────────────────────────────────── #

def resolve_email_to_uid(email: str) -> Optional[str]:
    """Resolve a tester's email to their Supabase user_id via the GoTrue
    admin list-users API (service-role). Paginates and matches
    case-insensitively. Returns None if not found or Supabase is down."""
    if not credits.is_configured():
        return None
    target = email.strip().lower()
    try:
        import httpx
        page = 1
        while page <= 50:  # 50 * 200 = 10k users — far beyond a beta
            resp = httpx.get(
                f"{credits._env_url()}/auth/v1/admin/users",
                headers=credits._headers(),
                params={"page": str(page), "per_page": "200"},
                timeout=8.0,
            )
            if resp.status_code >= 400:
                log.warning("[beta_credits] admin list users HTTP %d: %s",
                            resp.status_code, resp.text[:200])
                return None
            body = resp.json()
            users = body.get("users", body) if isinstance(body, dict) else body
            if not users:
                return None
            for u in users:
                if str(u.get("email", "")).strip().lower() == target:
                    return u.get("id")
            if len(users) < 200:
                return None  # last page
            page += 1
        return None
    except Exception as e:
        log.warning("[beta_credits] resolve_email errored: %s", e)
        return None


def _set_hard_cap(user_id: str, new_cap: int) -> bool:
    """Raise the row's hard_cap so a grant can exceed the plan default.
    Safe vs the DB CHECK (balance <= hard_cap) because we raise the cap
    BEFORE topping up the balance."""
    if not credits.is_configured():
        return False
    try:
        import httpx
        resp = httpx.patch(
            f"{credits._env_url()}/rest/v1/credits",
            headers=credits._headers(),
            params={"user_id": f"eq.{user_id}"},
            json={"hard_cap": new_cap},
            timeout=5.0,
        )
        if resp.status_code >= 400:
            log.warning("[beta_credits] set_hard_cap HTTP %d: %s",
                        resp.status_code, resp.text[:200])
            return False
        return True
    except Exception as e:
        log.warning("[beta_credits] set_hard_cap errored: %s", e)
        return False


@dataclass
class GrantResult:
    ok: bool
    user_id: Optional[str]
    recipient: str
    builds: int
    credited: int          # credits actually added this run
    new_balance: Optional[int]
    message: str


def grant_beta_builds(
    user_id: str,
    builds: int = DEFAULT_BETA_BUILDS,
    *,
    recipient: Optional[str] = None,
    dry_run: bool = False,
) -> GrantResult:
    """Ensure ``user_id`` holds at least ``builds`` engine builds' worth
    of credits. Raises hard_cap to fit, tops up the difference, writes a
    REASON_ADMIN_GRANT ledger row. Idempotent (re-running won't stack)."""
    rcpt = recipient or user_id
    if not credits.is_configured():
        return GrantResult(False, user_id, rcpt, builds, 0, None,
                           "Supabase not configured (service-role env missing).")

    target = builds_to_credits(builds)
    row = credits.get_or_init_row(user_id)
    if row is None:
        return GrantResult(False, user_id, rcpt, builds, 0, None,
                           "Could not read or init the credits row.")

    cur_balance = int(row.get("balance") or 0)
    cur_cap = int(row.get("hard_cap") or credits.DEFAULT_HARD_CAP)
    new_cap, delta = plan_topup(cur_balance, cur_cap, target)

    if delta == 0:
        return GrantResult(True, user_id, rcpt, builds, 0, cur_balance,
                           f"Already has {cur_balance} credits "
                           f"(>= {target} = {builds} builds) - no change.")

    if dry_run:
        return GrantResult(True, user_id, rcpt, builds, delta, cur_balance + delta,
                           f"[dry-run] would raise cap {cur_cap}->{new_cap}, "
                           f"add {delta} -> balance {cur_balance + delta}.")

    if new_cap > cur_cap and not _set_hard_cap(user_id, new_cap):
        return GrantResult(False, user_id, rcpt, builds, 0, cur_balance,
                           f"Failed to raise hard_cap to {new_cap}.")

    ok = credits.refill(user_id, delta, credits.REASON_ADMIN_GRANT, ref_id="beta_grant")
    if not ok:
        return GrantResult(False, user_id, rcpt, builds, 0, cur_balance,
                           "refill() failed (see engine log).")

    return GrantResult(True, user_id, rcpt, builds, delta, cur_balance + delta,
                       f"Granted {delta} credits -> balance {cur_balance + delta} "
                       f"({builds} builds available).")


# ─── CLI ─────────────────────────────────────────────────────────────── #

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="python -m pebble.beta_credits",
        description="Top up invited beta testers with engine-build credits.",
    )
    p.add_argument("recipients", nargs="+",
                   help="Tester emails and/or Supabase user_ids.")
    p.add_argument("--builds", type=int, default=DEFAULT_BETA_BUILDS,
                   help=f"Builds to grant each tester (default {DEFAULT_BETA_BUILDS}).")
    p.add_argument("--dry-run", action="store_true",
                   help="Show what would change without writing anything.")
    return p.parse_args(argv)


def _resolve(recipient: str) -> tuple[Optional[str], str]:
    """Return (user_id, note). Accepts a raw uuid or an email to look up."""
    r = recipient.strip()
    if looks_like_uuid(r):
        return r, ""
    if looks_like_email(r):
        uid = resolve_email_to_uid(r)
        return uid, ("" if uid else "no account found for that email")
    return None, "not a valid email or user_id"


def main(argv: Optional[list[str]] = None) -> int:
    # Load .env from the repo root (two levels up: pebble/ → repo) so the
    # operator can run this from a fresh shell without exporting secrets.
    _load_env(Path(__file__).resolve().parent.parent / ".env")
    ns = parse_args(argv)
    if ns.builds <= 0:
        print(f"error: --builds must be positive (got {ns.builds})", file=sys.stderr)
        return 2
    if not credits.is_configured():
        print("error: Supabase service-role env not configured "
              "(SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY). Aborting.",
              file=sys.stderr)
        return 1

    mode = " [DRY RUN]" if ns.dry_run else ""
    print(f"Granting {ns.builds} build(s) "
          f"= {builds_to_credits(ns.builds)} credits to "
          f"{len(ns.recipients)} recipient(s){mode}\n")

    failures = 0
    for rcpt in ns.recipients:
        uid, note = _resolve(rcpt)
        if uid is None:
            print(f"  [SKIP] {rcpt:<38} {note}")
            failures += 1
            continue
        res = grant_beta_builds(uid, ns.builds, recipient=rcpt, dry_run=ns.dry_run)
        mark = "[ok]  " if res.ok else "[FAIL]"
        print(f"  {mark} {rcpt:<38} {res.message}")
        if not res.ok:
            failures += 1

    print(f"\nDone. {len(ns.recipients) - failures} ok, {failures} failed.")
    return 1 if failures else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
