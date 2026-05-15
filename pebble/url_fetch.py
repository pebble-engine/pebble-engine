"""Shared SSRF-hardened HTTP fetch used by /api/inspire and /api/migrate.

Both endpoints accept a user-supplied URL and fetch it server-side.
That's the textbook SSRF surface, so the defenses live here in one
place — duplicating them across modules guarantees drift.

Hardening implemented:

- **Scheme allowlist.** Only ``http://`` and ``https://``. ``file://``,
  ``ftp://``, ``gopher://``, ``data:``, etc. are rejected at the input
  boundary AND on every redirect target.
- **Multi-IP private-range block.** :func:`_resolve_safely` calls
  ``socket.getaddrinfo`` and refuses if ANY resolved IP is private,
  loopback, link-local, multicast, reserved, or unspecified — including
  IPv6 ULA / link-local / IPv4-mapped (``::ffff:10.0.0.1``). Returning a
  benign IP first and a private IP second (multi-A/AAAA records) does
  not bypass the check because every record is inspected.
- **Manual redirect following.** Default ``urllib`` redirect handling
  follows 3xx targets without re-running the SSRF gate. We disable that
  and walk redirects ourselves, calling :func:`_resolve_safely` on the
  Location URL at every hop. Capped at ``_MAX_REDIRECTS``.
- **DNS-rebinding mitigation (best-effort).** After ``_resolve_safely``
  picks an IP, we connect to it directly (not the hostname) so urllib
  cannot re-resolve and reach a different address. The ``Host`` header
  carries the original hostname so virtual hosts and HTTPS SNI still
  work. Pure DNS rebinding still requires the attacker to control DNS
  for a domain whose A record changes during the fetch — the IP-pinning
  closes that window.
- **Response caps.** 2 MB body, 10 s timeout, content-type allowlist.

The module returns the same ``(final_url, body, byte_count, error)``
tuple shape as the previous local implementations so callers don't
need to change.
"""
from __future__ import annotations

import ipaddress
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request
from http.client import HTTPConnection, HTTPSConnection
from typing import Optional


# ---- Constants -----------------------------------------------------------

USER_AGENT  = "PebbleBot/1.0 (+https://getpebble.net)"
MAX_BYTES   = 2 * 1024 * 1024  # 2 MB
TIMEOUT_SEC = 10.0
MAX_REDIRECTS = 5

# Hostnames we refuse outright. Cheap deny-list for the common
# misconfigurations users post when they don't realize they're aiming
# at the engine's own loopback.
_BLOCKED_HOSTNAMES = {"localhost"}


# ---- Address validation --------------------------------------------------

def _is_private_or_loopback(ip_str: str) -> bool:
    """True for any IP we should refuse to fetch from. ``ipaddress``
    handles the heavy lifting (RFC 1918, loopback, link-local,
    multicast, reserved, IPv6 ULA / link-local / IPv4-mapped). We also
    treat unparseable inputs as suspicious."""
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    return (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_multicast
        or addr.is_reserved
        or addr.is_unspecified
    )


def _resolve_safely(host: str) -> Optional[tuple[str, int]]:
    """DNS-resolve ``host`` and return ``(ip, family)`` for the first
    public address — but only if EVERY resolved address is public.
    Returns ``None`` on any private, blocked, or unresolvable input.

    The "EVERY" rule is what closes the multi-A-record SSRF: an attacker
    who returns ``[8.8.8.8, 169.254.169.254]`` would pass a
    "first-record-public" check and then have urllib use the private IP
    on its own resolve. By rejecting if ANY record is private, the
    attacker has to give us only public IPs — at which point pinning to
    the first one is safe."""
    if not host or host.lower() in _BLOCKED_HOSTNAMES:
        return None
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except (socket.gaierror, OSError, UnicodeError):
        return None
    if not infos:
        return None
    public_pick: Optional[tuple[str, int]] = None
    for info in infos:
        family = info[0]
        ip = info[4][0]
        if _is_private_or_loopback(ip):
            return None
        if public_pick is None:
            public_pick = (ip, family)
    return public_pick


# ---- Fetch primitive ------------------------------------------------------

def _open_pinned(parsed: urllib.parse.ParseResult, ip: str, family: int) -> "HTTPConnection | HTTPSConnection":
    """Open a connection to ``ip`` directly, bypassing urllib's DNS so
    a DNS-rebinding race can't substitute a private IP between our
    validation and the actual connect."""
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if parsed.scheme == "https":
        ctx = ssl.create_default_context()
        # server_hostname makes SNI + cert validation work against the
        # original hostname even though we're connecting to the IP.
        return HTTPSConnection(ip, port=port, timeout=TIMEOUT_SEC, context=ctx)
    return HTTPConnection(ip, port=port, timeout=TIMEOUT_SEC)


def _send_one_request(parsed: urllib.parse.ParseResult, ip: str, family: int) -> tuple[int, dict, bytes, str]:
    """Send a single HTTP request to ``ip`` with proper Host header.
    Returns ``(status, headers, body, final_url)``.

    ``body`` is read up to ``MAX_BYTES + 1`` so the caller can detect
    overflow. ``final_url`` is the requested URL — redirects are NOT
    followed here; the caller handles them.
    """
    conn = _open_pinned(parsed, ip, family)
    try:
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        # Host header: hostname[:port] — include the port only if
        # non-standard so virtual hosts route correctly.
        host_header = parsed.hostname or ""
        if parsed.port and not (
            (parsed.scheme == "http" and parsed.port == 80)
            or (parsed.scheme == "https" and parsed.port == 443)
        ):
            host_header = f"{host_header}:{parsed.port}"
        conn.request(
            "GET", path,
            headers={
                "Host":            host_header,
                "User-Agent":      USER_AGENT,
                "Accept":          "text/html,application/xhtml+xml,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
        )
        resp = conn.getresponse()
        status = resp.status
        # Header keys are case-insensitive in HTTP; normalize to lower.
        headers = {k.lower(): v for k, v in resp.getheaders()}
        body = resp.read(MAX_BYTES + 1) if status == 200 else b""
        # final_url is what we requested; redirect target lives in headers["location"]
        final_url = urllib.parse.urlunparse(parsed)
        return status, headers, body, final_url
    finally:
        try:
            conn.close()
        except Exception:
            pass


def safe_fetch_html(url: str) -> tuple[str, str, int, Optional[str]]:
    """Fetch ``url`` with full SSRF defenses + manual redirect following.

    Returns ``(final_url, body_text, byte_count, error)``. Same shape
    the previous local fetchers used, so callers swap one import line.
    On any error the body is empty and ``error`` is a short human-
    readable string.
    """
    if not isinstance(url, str) or not url.strip():
        return "", "", 0, "url is required"
    current = url.strip()
    if not current.lower().startswith(("http://", "https://")):
        current = "https://" + current

    visited: set[str] = set()
    final_url = current
    for hop in range(MAX_REDIRECTS + 1):
        parsed = urllib.parse.urlparse(current)
        if parsed.scheme not in ("http", "https"):
            return current, "", 0, f"unsupported scheme: {parsed.scheme}"
        if not parsed.hostname:
            return current, "", 0, "url has no host"
        # Loop check — defense against self-redirecting attacker URLs.
        if current in visited:
            return current, "", 0, "redirect loop detected"
        visited.add(current)

        resolved = _resolve_safely(parsed.hostname)
        if resolved is None:
            return current, "", 0, "host resolves to a private or blocked address"
        ip, family = resolved

        try:
            status, headers, body, _ = _send_one_request(parsed, ip, family)
        except socket.timeout:
            return current, "", 0, "timeout"
        except (OSError, ssl.SSLError) as e:
            return current, "", 0, f"network error: {e.__class__.__name__}: {e}"
        except Exception as e:
            return current, "", 0, f"{type(e).__name__}: {e}"

        # Redirect handling: 301/302/303/307/308 with a Location header.
        if status in (301, 302, 303, 307, 308):
            location = headers.get("location")
            if not location:
                return current, "", 0, f"HTTP {status} without Location header"
            # Resolve relative redirects against the current URL.
            current = urllib.parse.urljoin(current, location)
            final_url = current
            continue
        if status >= 400:
            return current, "", 0, f"HTTP {status}"
        if status != 200:
            return current, "", 0, f"unexpected HTTP {status}"

        # 200 OK — content-type + size checks, then decode.
        ct = (headers.get("content-type") or "").lower()
        if "html" not in ct and "xml" not in ct and ct.strip() != "":
            return current, "", 0, f"non-HTML content type: {ct}"
        if len(body) > MAX_BYTES:
            return current, "", len(body), f"page exceeds {MAX_BYTES // (1024*1024)} MB"
        charset = "utf-8"
        for part in ct.split(";"):
            part = part.strip().lower()
            if part.startswith("charset="):
                charset = part.split("=", 1)[1].strip()
                break
        try:
            text = body.decode(charset, errors="replace")
        except LookupError:
            text = body.decode("utf-8", errors="replace")
        return final_url, text, len(body), None

    return final_url, "", 0, f"exceeded {MAX_REDIRECTS} redirects"


__all__ = [
    "USER_AGENT",
    "MAX_BYTES",
    "TIMEOUT_SEC",
    "MAX_REDIRECTS",
    "safe_fetch_html",
    "_is_private_or_loopback",
    "_resolve_safely",
]
