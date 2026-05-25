"""Instant subdomain publish — Phase 44 (2026-05-22).

Why this exists
---------------
The existing ``/api/publish`` flow uploads to Cloudflare Pages (30–60s
end-to-end). Base44's killer UX feature is "I clicked Publish and the
URL was live in under a second" — there's no external deploy step at all.
They achieve that by serving the published site directly from their own
edge.

We do the same thing here, riding on infrastructure that already exists:

* The engine already serves ``/preview/<slug>/`` from
  ``output/<slug>/site/`` (and proxies to a live ``next dev`` when one is
  running). The bytes are already on disk.
* The Railway deployment already terminates ``*.pebbleapp.ai`` (wildcard
  DNS — Marc sets up the CNAME once, then every project gets a subdomain
  for free).
* All we need is (a) a sentinel file marking which projects are
  "published" vs "draft", and (b) a router hook that maps
  ``<slug>.pebbleapp.ai`` to ``/preview/<slug>/`` for visitors.

What this module owns
---------------------
* ``run_publish_instant(handler)``  — POST ``/api/publish/instant``: flip
  the sentinel on. Snapshots first so the publish shows up in history.
* ``run_unpublish_instant(handler)`` — DELETE ``/api/publish/instant``:
  flip the sentinel off.
* ``run_get_instant_state(handler, slug)`` — GET
  ``/api/projects/<slug>/published``: read the sentinel.
* ``lookup_published_slug_by_subdomain(host)`` — used by the router to
  resolve ``bakery.pebbleapp.ai`` → ``bakery``.
* ``is_published(slug)`` — used by the preview handler to decide whether
  to inject the visual-edit bridge (workspace iframe = yes; public
  subdomain = no).

What this module does NOT own
-----------------------------
* Cloudflare deploys — still ``/api/publish`` (we keep that for "real"
  deploys to a custom domain).
* Page generation, content edits, billing.

Sentinel file shape (``output/<slug>/published.json``)
------------------------------------------------------
::

    {
        "slug":          "<slug>",
        "subdomain":     "<subdomain>",
        "published_at":  "<iso8601 utc>",
        "user_id":       "<owner id or null>",
        "snapshot_id":   "<id of pre-publish snapshot or null>"
    }

Removing this file unpublishes the site (subdomain stops resolving;
``/preview/<slug>/`` still works for the owner via the workspace).
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pebble.history import snapshot_site
from pebble.log import log
from pebble.security import (
    is_valid_slug,
    project_lock,
    require_project_owner,
    safe_user_id,
    user_publish_lock,
    validate_slug,
)
from pebble.server.publish import (
    FREE_PUBLISH_LIMIT,
    _clear_publish_intent,
    _count_published_sites,
    _subscription_active,
    _write_publish_intent,
)


# --------- subdomain shape + reserved list --------------------------------

# DNS label rules — stricter than the engine slug shape (no underscores,
# max 63 chars, must start AND end with alphanumeric).
_SUBDOMAIN_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")

# Subdomains we never let a project claim. Mix of:
#   * platform routes that need their own subdomain in the future
#     (www / app / api / admin / dashboard / status)
#   * legal / support common names users would type
#   * Pebble brand terms
# Conservative on purpose — easier to remove a name from this list than
# to claw it back from a user who already published to ``api.pebbleapp.ai``.
RESERVED_SUBDOMAINS = frozenset({
    "www", "api", "app", "admin", "dashboard", "pebble", "pebbleapp",
    "mail", "email", "support", "help", "blog", "docs", "status",
    "cdn", "assets", "static", "img", "images", "media", "files",
    "auth", "login", "signup", "signin", "register", "account",
    "settings", "billing", "checkout", "subscribe",
    "pricing", "terms", "privacy", "legal", "about", "contact",
    "home", "index", "root", "test", "staging", "dev", "preview",
    "ftp", "smtp", "ns", "ns1", "ns2", "mx", "imap", "pop",
})


def _pebble_public_domain() -> Optional[str]:
    """Resolve the public host suffix from env, e.g. ``pebbleapp.ai``.

    Returns ``None`` when unset — the endpoint and router will then short-
    circuit (no subdomain matching possible). Lower-cased so the Host
    header comparison is case-insensitive.
    """
    raw = os.environ.get("PEBBLE_PUBLIC_DOMAIN", "").strip().lower()
    return raw or None


def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


def _published_sentinel(slug: str) -> Path:
    return _output_dir() / slug / "published.json"


def is_valid_subdomain(sub: str) -> bool:
    """True when ``sub`` is a safe DNS label AND not on the reserved list."""
    if not isinstance(sub, str) or not sub:
        return False
    if len(sub) < 2 or len(sub) > 63:
        return False
    if not _SUBDOMAIN_RE.match(sub):
        return False
    if sub in RESERVED_SUBDOMAINS:
        return False
    return True


def _slug_to_subdomain(slug: str) -> str:
    """Turn a slug into a DNS-safe subdomain (lowercase, hyphens only).

    Engine slugs are usually already DNS-safe (``_slugify`` produces
    lowercase alphanumeric + hyphen). The only common reason this differs
    is legacy projects that contain ``_`` — strip those to ``-``.
    """
    sub = slug.lower().replace("_", "-")
    # Collapse runs of hyphens that the replace might introduce.
    sub = re.sub(r"-+", "-", sub).strip("-")
    return sub


# --------- subdomain → slug lookup (router-side) --------------------------

def _read_sentinel(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def lookup_published_slug_by_subdomain(host: str) -> Optional[str]:
    """Resolve ``bakery.pebbleapp.ai`` → ``bakery`` if that project is published.

    Returns ``None`` when:
      * ``PEBBLE_PUBLIC_DOMAIN`` is unset (instant publish disabled)
      * the host doesn't end in the configured suffix
      * the subdomain is the bare suffix (``pebbleapp.ai`` itself)
      * the subdomain is reserved
      * no project has published.json claiming that subdomain

    Pure read — no writes, safe to call on every request. The disk scan is
    bounded by the per-user 2-site free limit (and a small constant for
    paid users); see ``_count_published_sites``.
    """
    if not isinstance(host, str) or not host:
        return None
    public = _pebble_public_domain()
    if not public:
        return None
    # Strip the port — ``bakery.pebbleapp.ai:443``.
    host = host.split(":", 1)[0].strip().lower()
    if not host.endswith("." + public) and host != public:
        return None
    if host == public:
        return None  # bare apex — that's the marketing site, not a project
    sub = host[: -(len(public) + 1)]  # drop ".pebbleapp.ai"
    # Multi-level subdomains (e.g. ``foo.bar.pebbleapp.ai``) aren't
    # supported. Refuse cleanly so a wildcard cert mishit doesn't
    # accidentally resolve to a project.
    if "." in sub:
        return None
    if not is_valid_subdomain(sub):
        return None

    # Walk every project's published.json. O(n) scan but n is bounded by
    # active publishes (~2 per free user, ~tens for paid). Cheaper than a
    # secondary index until we cross 1k+ published sites.
    out = _output_dir()
    if not out.exists():
        return None
    for sentinel in out.glob("*/published.json"):
        data = _read_sentinel(sentinel)
        if not isinstance(data, dict):
            continue
        if data.get("subdomain", "").lower() == sub:
            slug = data.get("slug") or sentinel.parent.name
            if is_valid_slug(slug):
                return slug
    return None


def is_published(slug: str) -> bool:
    """True when the project has an active instant-publish sentinel."""
    if not is_valid_slug(slug):
        return False
    return _published_sentinel(slug).exists()


def read_instant_state(slug: str) -> Optional[dict]:
    """Read the sentinel for a project, or None when unpublished."""
    if not is_valid_slug(slug):
        return None
    return _read_sentinel(_published_sentinel(slug))


# --------- subdomain uniqueness ------------------------------------------

def _subdomain_in_use(subdomain: str, exclude_slug: str) -> bool:
    """True when another project (not ``exclude_slug``) is publishing on ``subdomain``."""
    out = _output_dir()
    if not out.exists():
        return False
    for sentinel in out.glob("*/published.json"):
        if sentinel.parent.name == exclude_slug:
            continue
        data = _read_sentinel(sentinel)
        if not isinstance(data, dict):
            continue
        if data.get("subdomain", "").lower() == subdomain:
            return True
    return False


def _allocate_subdomain(preferred: str, exclude_slug: str) -> Optional[str]:
    """Find an available subdomain near ``preferred``.

    Tries the preferred name first, then suffixed variants (-2, -3, …, -99).
    Returns ``None`` after 100 collisions — caller should surface as 409.
    """
    if not is_valid_subdomain(preferred):
        return None
    if not _subdomain_in_use(preferred, exclude_slug):
        return preferred
    for i in range(2, 100):
        candidate = f"{preferred}-{i}"
        if not is_valid_subdomain(candidate):
            continue  # too long after suffix
        if not _subdomain_in_use(candidate, exclude_slug):
            return candidate
    return None


# --------- request helpers ------------------------------------------------

def _read_body(handler) -> Optional[dict]:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"})
        return None
    if length <= 0:
        return {}
    if length > 32 * 1024:
        handler._json(413, {"error": "request too large"})
        return None
    try:
        return json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"})
        return None


def _public_url(subdomain: str) -> str:
    """Build the public URL for this subdomain.

    Picks https unless overridden via ``PEBBLE_PUBLIC_SCHEME=http`` (used
    by local dev — wildcard ``*.localhost`` resolves but TLS doesn't).
    """
    public = _pebble_public_domain() or "pebbleapp.ai"
    scheme = os.environ.get("PEBBLE_PUBLIC_SCHEME", "https").strip().lower() or "https"
    if scheme not in ("http", "https"):
        scheme = "https"
    return f"{scheme}://{subdomain}.{public}"


# --------- POST /api/publish/instant --------------------------------------

def run_publish_instant(handler) -> None:
    """Mark a project as instantly published on its subdomain.

    Body::

        { "slug": "<project-slug>", "subdomain"?: "<preferred>" }

    Returns 200::

        {
            "slug":         "...",
            "subdomain":    "...",
            "url":          "https://<sub>.pebbleapp.ai",
            "published_at": "<iso8601>",
            "snapshot_id":  "...",
            "kind":         "instant"
        }

    Errors:
      * 400 — invalid slug, invalid preferred subdomain
      * 402 — free-plan publish limit reached
      * 403 — not owner (via require_project_owner)
      * 404 — project not found
      * 409 — preferred subdomain taken AND no free suffix available
      * 500 — PEBBLE_PUBLIC_DOMAIN unset (operator config error)
      * 503 — concurrent publish in progress
    """
    if _pebble_public_domain() is None:
        handler._json(500, {
            "error": (
                "Instant publish is not configured. Operator: set "
                "PEBBLE_PUBLIC_DOMAIN in .env (e.g. pebbleapp.ai) and "
                "point wildcard DNS *.PEBBLE_PUBLIC_DOMAIN at the engine."
            ),
        })
        return

    body = _read_body(handler)
    if body is None:
        return

    slug = (body or {}).get("slug")
    if not isinstance(slug, str) or not validate_slug(handler, slug):
        return

    uid = require_project_owner(handler, slug)
    if uid is None:
        return

    project_dir = _output_dir() / slug
    if not project_dir.exists():
        handler._json(404, {"error": f"project not found: {slug}"})
        return

    # Free-plan site limit. Counts both Cloudflare publishes (publish.json)
    # AND instant publishes — they're the same product from billing's
    # point of view. Active subscribers are unlimited.
    if not _subscription_active(uid):
        with user_publish_lock(uid) as acquired:
            if not acquired:
                handler._json(503, {"error": "another publish is in progress; try again shortly"})
                return
            # _count_published_sites already counts publish.json + .publish_intent.
            # Extend with our new sentinel so the limit holds across modes.
            already = _count_published_sites(uid, exclude_slug=slug)
            instant_already = _count_instant_published(uid, exclude_slug=slug)
            total = already + instant_already
            if total >= FREE_PUBLISH_LIMIT:
                handler._json(402, {
                    "error": (
                        f"Free plan allows {FREE_PUBLISH_LIMIT} published sites. "
                        "Upgrade to Starter or Pro to publish unlimited sites."
                    ),
                    "upgrade_url": "/pricing",
                    "published_count": total,
                    "limit": FREE_PUBLISH_LIMIT,
                })
                return
            # Claim the slot before releasing the lock.
            _write_publish_intent(slug)

    started = time.time()

    # Pick the subdomain. User can suggest one; otherwise derive from slug.
    raw_preferred = (body or {}).get("subdomain")
    if isinstance(raw_preferred, str) and raw_preferred.strip():
        preferred = raw_preferred.strip().lower()
        if not is_valid_subdomain(preferred):
            _clear_publish_intent(slug)
            handler._json(400, {
                "error": (
                    "Invalid subdomain. Use lowercase letters, digits, and hyphens; "
                    "2–63 chars; can't start or end with a hyphen; reserved names blocked."
                ),
            })
            return
    else:
        preferred = _slug_to_subdomain(slug)
        if not is_valid_subdomain(preferred):
            _clear_publish_intent(slug)
            handler._json(400, {
                "error": (
                    f"Could not auto-generate a subdomain from slug '{slug}'. "
                    "Pass an explicit ``subdomain`` field."
                ),
            })
            return

    # If THIS project already has a sentinel, keep its subdomain (re-publish
    # shouldn't migrate the URL out from under links people already share).
    existing = read_instant_state(slug)
    if existing and is_valid_subdomain(existing.get("subdomain", "")):
        # Honour explicit override request, otherwise stick with current.
        if not isinstance(raw_preferred, str) or not raw_preferred.strip():
            preferred = existing["subdomain"].lower()

    # Per-slug lock around snapshot + sentinel write so concurrent
    # publishes for the SAME slug don't double-snapshot and race on the
    # uniqueness check below.
    with project_lock(slug):
        # Uniqueness check inside the lock — between picking ``preferred``
        # and writing the sentinel, another publish for a DIFFERENT slug
        # could land on the same subdomain. _allocate_subdomain suffixes.
        subdomain = _allocate_subdomain(preferred, exclude_slug=slug)
        if subdomain is None:
            _clear_publish_intent(slug)
            handler._json(409, {
                "error": (
                    f"Subdomain '{preferred}' and the next 99 suffixed variants "
                    "are all in use. Pick a different name."
                ),
            })
            return

        # Snapshot before flipping the sentinel — the publish itself
        # shows up in version history that way.
        snap = snapshot_site(slug, reason="publish-instant", source="POST /api/publish/instant")
        snapshot_id = snap.name if snap else None

        published_at = datetime.now(timezone.utc).isoformat()
        sentinel = {
            "slug":         slug,
            "subdomain":    subdomain,
            "published_at": published_at,
            "user_id":      uid,
            "snapshot_id":  snapshot_id,
            "kind":         "instant",
        }
        _write_sentinel_atomic(_published_sentinel(slug), sentinel)
        _clear_publish_intent(slug)

    log.info("instant-publish slug=%s subdomain=%s uid=%s", slug, subdomain, uid)

    handler._json(200, {
        "slug":             slug,
        "subdomain":        subdomain,
        "url":              _public_url(subdomain),
        "published_at":     published_at,
        "snapshot_id":      snapshot_id,
        "kind":             "instant",
        "elapsed_seconds":  round(time.time() - started, 3),
    })

    # 2026-05-24 — record a public site_published event so the
    # community feed reflects this launch + the user's bell pings.
    # Fire-and-forget; failures here never block the publish response.
    try:
        from pebble import events as _events
        # Read business_name from the project's brief.json if available.
        brief_path = _engine().OUTPUT_DIR / slug / "brief.json"
        business_name = slug
        if brief_path.exists():
            try:
                brief = json.loads(brief_path.read_text(encoding="utf-8"))
                business_name = (brief.get("business_name") or slug)
            except Exception:
                pass
        public_url = _public_url(subdomain)
        # PRIVATE notification to the owner ("Your site is live!").
        _events.record(
            user_id=uid,
            kind=_events.KIND_SITE_PUBLISHED,
            title=f"{business_name} is live",
            body=f"Your site is now reachable at {public_url}.",
            visibility=_events.VISIBILITY_PRIVATE,
            meta={"slug": slug, "url": public_url},
        )
        # PUBLIC event for the community feed ("Marc just launched X").
        _events.record(
            user_id=uid,
            kind=_events.KIND_SITE_PUBLISHED,
            title=f"{business_name} just launched",
            body=f"A new site went live on Pebble.",
            visibility=_events.VISIBILITY_PUBLIC,
            meta={"slug": slug, "url": public_url, "business_name": business_name},
        )
    except Exception as e:
        log.warning("events.record failed for site_published: %s", e)


def _write_sentinel_atomic(path: Path, data: dict) -> None:
    """Write the sentinel via temp-file + rename for atomicity."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def _count_instant_published(user_id: str, exclude_slug: str) -> int:
    """Count this user's OTHER instant-published sites.

    Mirrors ``_count_published_sites`` from pebble.server.publish but
    looks at ``published.json`` instead of ``publish.json``. We need both
    counts because the free-tier limit is total, not per-mode.
    """
    out = _output_dir()
    if not out.exists():
        return 0
    count = 0
    for sentinel in out.glob("*/published.json"):
        slug = sentinel.parent.name
        if slug == exclude_slug:
            continue
        data = _read_sentinel(sentinel)
        if not isinstance(data, dict):
            continue
        if data.get("user_id") != user_id:
            continue
        count += 1
    return count


# --------- DELETE /api/publish/instant ------------------------------------

def run_unpublish_instant(handler) -> None:
    """Remove the instant-publish sentinel — the subdomain stops resolving.

    Body::

        { "slug": "<project-slug>" }

    No snapshot is taken on unpublish (the bytes don't change; the
    sentinel is the only state). Idempotent — unpublishing a project
    that was never published returns 200 with ``was_published: false``.
    """
    body = _read_body(handler)
    if body is None:
        return

    slug = (body or {}).get("slug")
    if not isinstance(slug, str) or not validate_slug(handler, slug):
        return

    uid = require_project_owner(handler, slug)
    if uid is None:
        return

    with project_lock(slug):
        sentinel_path = _published_sentinel(slug)
        was_published = sentinel_path.exists()
        try:
            sentinel_path.unlink(missing_ok=True)
        except Exception as e:
            log.warning("instant-unpublish failed slug=%s: %s", slug, e)
            handler._json(500, {"error": f"unpublish failed: {e}"})
            return

    log.info("instant-unpublish slug=%s uid=%s was=%s", slug, uid, was_published)
    handler._json(200, {"slug": slug, "was_published": was_published})


# --------- GET /api/projects/<slug>/published -----------------------------

def run_get_instant_state(handler, slug: str) -> None:
    """Read the current instant-publish state for a project (owner-gated)."""
    if not validate_slug(handler, slug):
        return
    if require_project_owner(handler, slug) is None:
        return

    state = read_instant_state(slug)
    if state is None:
        handler._json(200, {
            "slug":      slug,
            "published": False,
        })
        return

    sub = state.get("subdomain", "")
    handler._json(200, {
        "slug":         slug,
        "published":    True,
        "subdomain":    sub,
        "url":          _public_url(sub) if is_valid_subdomain(sub) else None,
        "published_at": state.get("published_at"),
        "snapshot_id":  state.get("snapshot_id"),
    })
