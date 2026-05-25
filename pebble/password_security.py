"""Check passwords against HaveIBeenPwned's free Pwned Passwords API.

Why this module exists
----------------------
Supabase Auth offers leaked-password protection as a Pro-plan-only toggle
(verified 2026-05-24 — Free plan rejects the API call with "Configuring
leaked password protection via HaveIBeenPwned.org is available on Pro
Plans and up"). Rather than pay $25/mo for one feature OR ship without
it, we wire the same HIBP backend ourselves.

How it works (k-anonymity range query)
--------------------------------------
1. SHA-1 the password locally.
2. Send ONLY the first 5 hex chars of that hash to HIBP.
3. HIBP returns every hash starting with those 5 chars + a per-hash
   count of how many times the password appears in known breach dumps.
4. We scan the response locally for our remaining 35 chars.

The plaintext password and the full hash NEVER leave this server. HIBP
sees a 5-character prefix shared by ~500-1000 other passwords. That's
the k-anonymity property they document — see
https://haveibeenpwned.com/API/v3#PwnedPasswords.

API specifics
-------------
- Endpoint:    GET https://api.pwnedpasswords.com/range/<5-hex-chars>
- Auth:        None required
- Rate limit:  None published (intentionally permissive for this use)
- Cost:        $0
- Padding:     We send `Add-Padding: true` so the response length doesn't
               leak the popularity bucket of our prefix (defense against
               passive network observers).

Fail-OPEN policy
----------------
If the HIBP request times out or errors, we return None and the caller
should ACCEPT the password rather than block it. Rationale: a transient
HIBP outage shouldn't lock thousands of users out of changing their
password. The trade-off is that an attacker who can DoS HIBP from our
network could push a leaked password through — but that's a sophisticated
attack and the failure mode (one weak password accepted) is much milder
than the alternative (real users blocked for hours).

Known coverage gap
------------------
This module wires HIBP into `/api/account/change-password` only.
- Signup happens directly through Supabase Auth in v3 — bypassing the
  engine — so a new account CAN be created with a leaked password.
- Password reset goes through Supabase's own reset flow.
Closing those gaps requires Supabase Auth Hooks (beta) or moving signup
through the engine. Deferred.
"""
from __future__ import annotations

import hashlib
import urllib.error
import urllib.request
from typing import Optional

from pebble.log import log


_API_BASE = "https://api.pwnedpasswords.com/range/"
_TIMEOUT_SEC = 3.0
_USER_AGENT = "PebbleEngine/1.0 (+https://pebbleapp.ai)"


def _fetch_range(prefix: str) -> Optional[str]:
    """Fetch the HIBP range response for a SHA-1 prefix.

    Returns the raw response body as text, or None on any failure.
    Separated so tests can monkeypatch one symbol.
    """
    req = urllib.request.Request(
        _API_BASE + prefix,
        headers={
            "User-Agent":  _USER_AGENT,
            "Add-Padding": "true",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT_SEC) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        log.warning("[password_security] HIBP range fetch failed: %s", exc)
        return None


def check_pwned(password: str) -> Optional[int]:
    """Return how many breaches this password appears in.

    Returns:
        int >= 1: Password has been seen in N known breaches. Reject it.
        0:        Password has never been seen. Accept it.
        None:     HIBP API unreachable. Fail-OPEN — caller should accept.

    The password argument is consumed locally (SHA-1) and never sent
    anywhere. Only the first 5 hex chars of the hash leave this process.
    """
    if not password:
        return 0  # empty/None is "not in any breach" — caller handles min-length elsewhere

    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    body = _fetch_range(prefix)
    if body is None:
        return None

    for line in body.splitlines():
        # Each line is "<35-hex-suffix>:<count>"
        line = line.strip()
        if not line:
            continue
        line_suffix, sep, count_str = line.partition(":")
        if not sep:
            continue
        if line_suffix.strip().upper() == suffix:
            try:
                return int(count_str.strip())
            except ValueError:
                # Malformed count column — treat the same as "not found"
                # rather than fail-OPEN, because we DID find a hash match.
                # A safe default for a corrupted response is "reject" (return
                # large breach count) — but the corruption could also be on
                # the line itself, so we conservatively return 1.
                return 1
    return 0


__all__ = ["check_pwned"]
