"""Server-side wrapper for Supabase Storage.

Used by the form-upload endpoint to stash visitor-attached files
(images, PDFs, intake docs) somewhere durable instead of cramming
them into the submission record. Stores via the Storage REST API
using the service-role key so the request bypasses RLS — the
engine acts as a trusted upload broker for the visitor.

Environment:
    PEBBLE_SUPABASE_URL              project URL, https://xxx.supabase.co
    PEBBLE_SUPABASE_SERVICE_ROLE_KEY service-role JWT (admin key)
    PEBBLE_SUPABASE_FORM_UPLOADS_BUCKET  bucket name, default "form-uploads"

Operational notes:
- The bucket must exist before the first upload (one-time setup in
  the Supabase Dashboard → Storage). Make it PRIVATE; access is
  granted via signed URLs that the inbox endpoint hands out.
- `is_configured()` returns False when either env var is missing —
  the upload endpoint should refuse cleanly instead of crashing.
- Filenames are slugified and prefixed with a random hex segment to
  prevent collisions and path-traversal attempts.
- Size caps + MIME allowlist live in the HTTP handler (storage.py
  only knows how to push bytes; the handler decides what's safe).
"""
from __future__ import annotations

import json
import os
import re
import secrets
import urllib.parse
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Optional


class StorageError(Exception):
    """Upload or sign-URL failure surfaced to the HTTP caller."""


# Reasonable defaults — the env var lets ops change the bucket name
# without a code deploy.
_DEFAULT_BUCKET = "form-uploads"

# Cap individual filenames after slugify — long names are usually
# adversarial. The bucket-side key includes a random prefix so
# uniqueness is preserved even when names are truncated.
_MAX_SAFE_NAME_LEN = 80


def _env_url() -> str:
    return os.environ.get("PEBBLE_SUPABASE_URL", "").strip().rstrip("/")


def _env_key() -> str:
    return os.environ.get("PEBBLE_SUPABASE_SERVICE_ROLE_KEY", "").strip()


def _bucket() -> str:
    return os.environ.get("PEBBLE_SUPABASE_FORM_UPLOADS_BUCKET", _DEFAULT_BUCKET).strip() or _DEFAULT_BUCKET


def is_configured() -> bool:
    """True iff both URL and service-role key env vars are present.
    HTTP handlers call this first to refuse cleanly when storage
    hasn't been wired up yet (so e.g. local dev returns 503 instead
    of crashing on a missing env var)."""
    return bool(_env_url()) and bool(_env_key())


def _safe_name(filename: str) -> str:
    """Slugify the visitor-provided filename. Keeps the extension;
    drops everything that isn't `[a-zA-Z0-9._-]`. Caps the result so
    a 1KB filename can't blow up the storage key."""
    if not isinstance(filename, str) or not filename:
        return "file"
    # Strip any directory traversal pieces up front.
    base = os.path.basename(filename)
    # Replace runs of disallowed chars with a single underscore.
    base = re.sub(r"[^a-zA-Z0-9._-]+", "_", base).strip("._")
    if not base:
        base = "file"
    if len(base) > _MAX_SAFE_NAME_LEN:
        # Preserve the extension if present.
        if "." in base:
            head, _, ext = base.rpartition(".")
            base = head[: _MAX_SAFE_NAME_LEN - len(ext) - 1] + "." + ext
        else:
            base = base[:_MAX_SAFE_NAME_LEN]
    return base


def _safe_slug(slug: str) -> str:
    """The project slug becomes a folder in the bucket. Stricter than
    the form-submit slug guard because we're concatenating into a URL."""
    if not isinstance(slug, str):
        return "unknown"
    # Allow lowercase + digits + dash + underscore. Reject everything else.
    cleaned = re.sub(r"[^a-z0-9_-]", "-", slug.lower()).strip("-_")
    return cleaned or "unknown"


@dataclass
class UploadResult:
    """Result returned from `upload_attachment`."""
    path:        str   # bucket-relative storage key (e.g. "<slug>/<rand>/<name>")
    public_url:  Optional[str]  # public URL if the bucket is public; else None
    bucket:      str


def upload_attachment(
    slug: str,
    filename: str,
    content: bytes,
    content_type: str,
    *,
    timeout_sec: float = 10.0,
) -> UploadResult:
    """Push `content` to Supabase Storage under `<bucket>/<slug>/<rand>/<name>`.

    Raises StorageError on any non-2xx response or missing config.
    Caller is responsible for size + MIME validation upstream.
    """
    if not is_configured():
        raise StorageError(
            "Supabase Storage not configured. Set PEBBLE_SUPABASE_URL + "
            "PEBBLE_SUPABASE_SERVICE_ROLE_KEY in .env."
        )
    if not isinstance(content, (bytes, bytearray)) or not content:
        raise StorageError("upload content is empty")
    if not isinstance(content_type, str) or not content_type:
        raise StorageError("content_type is required")

    bucket = _bucket()
    safe_slug = _safe_slug(slug)
    safe_name = _safe_name(filename)
    # 16 hex chars = 64 bits of randomness; vastly more than enough to
    # avoid collisions within a single project. Keeps the visible URL
    # short.
    nonce = secrets.token_hex(8)
    object_path = f"{safe_slug}/{nonce}/{safe_name}"

    url = f"{_env_url()}/storage/v1/object/{urllib.parse.quote(bucket)}/{urllib.parse.quote(object_path)}"
    req = urllib.request.Request(
        url,
        data=bytes(content),
        method="POST",
        headers={
            "Authorization": f"Bearer {_env_key()}",
            "Content-Type":  content_type,
            "x-upsert":      "false",  # never silently overwrite
            "User-Agent":    "PebbleEngine/1.0 (+https://getpebble.net)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            status = resp.status
            body = resp.read(2048)
    except urllib.error.HTTPError as e:
        # Try to extract Supabase's error JSON for the message.
        try:
            payload = json.loads(e.read().decode("utf-8", errors="replace"))
            msg = payload.get("message") or payload.get("error") or str(e)
        except Exception:
            msg = f"HTTP {e.code}"
        raise StorageError(f"Supabase Storage upload failed: {msg}") from e
    except urllib.error.URLError as e:
        raise StorageError(f"Supabase Storage unreachable: {e.reason}") from e

    if not (200 <= status < 300):
        raise StorageError(f"Supabase Storage upload returned HTTP {status}")

    # The bucket's public-URL conventions are:
    #   <project>/storage/v1/object/public/<bucket>/<path>
    # We return this regardless of public/private since signed URLs
    # use a different path. The HTTP layer wraps this into a signed
    # URL when needed.
    public_url = f"{_env_url()}/storage/v1/object/public/{bucket}/{urllib.parse.quote(object_path)}"
    return UploadResult(path=object_path, public_url=public_url, bucket=bucket)


def create_signed_url(
    path: str,
    *,
    expires_in_seconds: int = 3600,
    timeout_sec: float = 10.0,
) -> str:
    """Return a time-limited download URL for a stored object.
    The inbox UI uses this to give the project owner a download link
    without exposing the bucket publicly.

    Raises StorageError on failure or missing config.
    """
    if not is_configured():
        raise StorageError("Supabase Storage not configured")
    if not isinstance(path, str) or not path:
        raise StorageError("path is required")
    bucket = _bucket()
    url = f"{_env_url()}/storage/v1/object/sign/{urllib.parse.quote(bucket)}/{urllib.parse.quote(path)}"
    body = json.dumps({"expiresIn": int(expires_in_seconds)}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {_env_key()}",
            "Content-Type":  "application/json",
            "User-Agent":    "PebbleEngine/1.0 (+https://getpebble.net)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode("utf-8", errors="replace"))
            msg = err.get("message") or err.get("error") or str(e)
        except Exception:
            msg = f"HTTP {e.code}"
        raise StorageError(f"sign URL failed: {msg}") from e
    except urllib.error.URLError as e:
        raise StorageError(f"Supabase Storage unreachable: {e.reason}") from e

    relative = payload.get("signedURL") or payload.get("signedUrl")
    if not relative:
        raise StorageError("sign URL response missing signedURL field")
    return f"{_env_url()}/storage/v1{relative}"


__all__ = [
    "StorageError",
    "UploadResult",
    "is_configured",
    "upload_attachment",
    "create_signed_url",
    "_safe_name",
    "_safe_slug",
]
