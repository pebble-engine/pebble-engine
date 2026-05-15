"""Publish flow — package a generated site for hosting.

Produces a downloadable ZIP of the site by default. When
``CLOUDFLARE_ACCOUNT_ID`` and ``CLOUDFLARE_API_TOKEN`` are configured,
:func:`publish_to_cloudflare` deploys a built static artifact to
Cloudflare Pages via the Direct Upload API.

The ZIP path is the testable-without-credentials fallback. It's also
useful in its own right — users can drag-and-drop the archive into
Vercel, Netlify, or any static host.

State files written per project:

- ``output/<slug>/dist.zip``       — most recent zip artifact
- ``output/<slug>/publish.json``   — last publish result (kind, url, ...)
- ``output/<slug>/publish_log.json`` — chronological history (last 50)
"""
from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# --------- Paths ----------------------------------------------------------

def _engine_output_dir() -> Path:
    """Resolve OUTPUT_DIR through the engine module so tests can monkeypatch."""
    eng = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    if eng and hasattr(eng, "OUTPUT_DIR"):
        return Path(getattr(eng, "OUTPUT_DIR"))
    return Path(__file__).parent.parent.resolve() / "output"


def _site_dir(slug: str) -> Path:
    return _engine_output_dir() / slug / "site"


# Build artifacts and bookkeeping files we never publish.
PUBLISH_EXCLUDE_DIRS = {
    "node_modules", ".next", ".vercel", "out", "dist", ".turbo", ".git",
    "__pycache__", ".pytest_cache",
}
PUBLISH_EXCLUDE_FILES = {
    ".env", ".env.local", ".env.production",
    ".pebble-ids.json", ".starred", "dist.zip",
    ".DS_Store", "Thumbs.db",
}


class PublishError(Exception):
    """Raised for any user-visible publish failure (no site, bad config, API error).

    ``status`` is the HTTP code from Cloudflare when the failure was an
    API response (else None). Lets callers distinguish "404 — needs
    create" from "401 — auth busted" so we don't paper over real errors.
    """
    def __init__(self, message: str, *, status: Optional[int] = None) -> None:
        super().__init__(message)
        self.status = status


@dataclass
class PublishResult:
    slug:                str
    kind:                str             # "zip" | "cloudflare"
    url:                 str             # download URL or live URL
    deployed_at:         str
    bytes_published:     int = 0
    files_published:     int = 0
    snapshot_id:         Optional[str]  = None
    deployment_id:       Optional[str]  = None
    project_name:        Optional[str]  = None
    note:                Optional[str]  = None
    cloudflare_setup_md: Optional[str]  = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


# --------- Zip packaging --------------------------------------------------

def _is_excluded(rel: Path) -> bool:
    parts = rel.parts
    if any(p in PUBLISH_EXCLUDE_DIRS for p in parts):
        return True
    if parts and parts[-1] in PUBLISH_EXCLUDE_FILES:
        return True
    return False


def package_zip(slug: str) -> tuple[Path, int, int]:
    """Zip ``output/<slug>/site/`` to ``output/<slug>/dist.zip``.

    Returns ``(zip_path, files_count, bytes_count)``. Raises
    :class:`PublishError` if the site directory is missing or contains
    no publishable files.
    """
    site = _site_dir(slug)
    if not site.exists() or not site.is_dir():
        raise PublishError(f"No site to publish for {slug}. Run a build first.")

    zip_path = _engine_output_dir() / slug / "dist.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        try: zip_path.unlink()
        except Exception: pass

    file_count = 0
    byte_count = 0
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src in sorted(site.rglob("*")):
            if not src.is_file():
                continue
            rel = src.relative_to(site)
            if _is_excluded(rel):
                continue
            # Forward slashes inside zip — portable across OSes.
            arcname = "/".join(rel.parts)
            zf.write(src, arcname=arcname)
            file_count += 1
            byte_count += src.stat().st_size

    if file_count == 0:
        try: zip_path.unlink()
        except Exception: pass
        raise PublishError(f"No publishable files in site/ for {slug}.")

    return zip_path, file_count, byte_count


# --------- Cloudflare config / checklist ----------------------------------

def cloudflare_configured() -> bool:
    """True iff both Cloudflare creds are present in the environment."""
    return bool(
        os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
        and os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    )


def cloudflare_setup_checklist() -> str:
    """Paste-ready markdown checklist to wire Cloudflare Pages publishing."""
    return (
        "## Cloudflare Pages — one-time setup (5 min)\n\n"
        "Pebble can deploy your site to a live URL on Cloudflare Pages (free tier).\n\n"
        "1. **Sign up** at https://dash.cloudflare.com/sign-up (~60 seconds)\n"
        "2. **Find your Account ID** — on any Cloudflare dashboard page, "
        "the Account ID is shown on the right side\n"
        "3. **Create an API token** at https://dash.cloudflare.com/profile/api-tokens\n"
        "   - Click **Create Token** → **Create Custom Token**\n"
        "   - Token name: `pebble-publish`\n"
        "   - Permissions: **Account → Cloudflare Pages → Edit**\n"
        "   - Account Resources: **Include → your account**\n"
        "   - Click **Continue to summary** → **Create Token**\n"
        "   - Copy the token (Cloudflare only shows it once)\n"
        "4. **Add the keys to `.env`** in the Pebble Engine directory:\n"
        "   ```\n"
        "   CLOUDFLARE_ACCOUNT_ID=<your-account-id>\n"
        "   CLOUDFLARE_API_TOKEN=<your-api-token>\n"
        "   ```\n"
        "5. **Restart** `python pebble_engine.py`. The Publish button now deploys live.\n\n"
        "Cost: Cloudflare Pages is free for 500 builds/month + unlimited bandwidth.\n"
    )


def slug_to_project_name(slug: str) -> str:
    """Normalize a Pebble slug into a Cloudflare Pages project name.

    Cloudflare Pages requires lowercase, alphanumeric + hyphens,
    max 58 characters, no leading/trailing hyphen.
    """
    s = (slug or "").strip().lower()
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    if not s:
        s = "site"
    name = f"pebble-{s}"
    return name[:58].rstrip("-")


# --------- Cloudflare publishing ------------------------------------------

CF_API_BASE   = "https://api.cloudflare.com/client/v4"
CF_PAGES_API  = f"{CF_API_BASE}/pages"


def _cf_request(
    method: str,
    url: str,
    *,
    token: str,
    body: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> dict:
    """Bare JSON Cloudflare API helper. Raises :class:`PublishError` on failure."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            err_body = json.loads(raw)
        except Exception:
            err_body = {"raw": raw}
        raise PublishError(
            f"Cloudflare API {method} {url} failed: HTTP {e.code} — {err_body}",
            status=e.code,
        )
    except Exception as e:
        raise PublishError(f"Cloudflare API {method} {url} unreachable: {e}")
    try:
        return json.loads(raw)
    except Exception:
        raise PublishError(f"Cloudflare API {method} {url} returned non-JSON: {raw[:200]}")


def _cf_blake3_hash(content: bytes, content_type: str) -> str:
    """BLAKE3 of (content || contentType-bytes), hex, first 32 chars.

    Matches Cloudflare's @cloudflare/pages-shared asset-hash algorithm.
    Requires the optional ``blake3`` package (pure-Rust wheel) — pip
    install it to enable Cloudflare deploys.
    """
    try:
        import blake3  # type: ignore
    except ImportError as e:
        raise PublishError(
            "Cloudflare publish requires the `blake3` package. "
            "Install with: pip install blake3"
        ) from e
    ct_bytes = content_type.encode("utf-8")
    combined = content + ct_bytes
    return blake3.blake3(combined).hexdigest()[:32]


def _enumerate_publish_files(source_dir: Path) -> list[tuple[Path, str]]:
    """Yield (absolute path, relative path with leading slash) for every
    file we'd publish from ``source_dir``. Respects the exclude lists.
    """
    out: list[tuple[Path, str]] = []
    for src in sorted(source_dir.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(source_dir)
        if _is_excluded(rel):
            continue
        # Cloudflare manifest paths are URL-style with leading slash.
        url_path = "/" + "/".join(rel.parts)
        out.append((src, url_path))
    return out


def _ensure_cloudflare_project(account_id: str, token: str, project_name: str) -> dict:
    """Return the project record, creating it if missing.

    Only treats a 404 from the GET as "create"; auth, rate-limit, or
    network failures bubble up so we don't paper over real errors with
    a spurious POST.
    """
    try:
        return _cf_request(
            "GET",
            f"{CF_API_BASE}/accounts/{account_id}/pages/projects/{project_name}",
            token=token,
        )
    except PublishError as e:
        # Anything other than "not found" is a real error — surface it.
        if e.status not in (404,):
            raise
    return _cf_request(
        "POST",
        f"{CF_API_BASE}/accounts/{account_id}/pages/projects",
        token=token,
        body={"name": project_name, "production_branch": "main"},
    )


def publish_to_cloudflare(
    slug: str,
    *,
    source_dir: Optional[Path] = None,
    project_name: Optional[str] = None,
) -> PublishResult:
    """Deploy a static-artifact directory to Cloudflare Pages.

    ``source_dir`` defaults to ``output/<slug>/site/out``  (Next.js
    static-export output) if it exists, falling back to the source
    ``site/`` tree. Static-export-only is the practical scope here:
    Server Actions and SSR Next.js need ``@cloudflare/next-on-pages``
    which is a separate build step.

    Raises :class:`PublishError` on missing creds, missing artifact, or
    API failures.
    """
    if not cloudflare_configured():
        raise PublishError("Cloudflare not configured. See cloudflare_setup_checklist().")

    account_id = os.environ["CLOUDFLARE_ACCOUNT_ID"].strip()
    token      = os.environ["CLOUDFLARE_API_TOKEN"].strip()

    site = _site_dir(slug)
    if source_dir is None:
        # Prefer a static-export `out/` if it exists; else publish source files.
        out_dir = site / "out"
        source_dir = out_dir if out_dir.exists() else site
    if not source_dir.exists() or not source_dir.is_dir():
        raise PublishError(f"Source directory missing: {source_dir}")

    name = project_name or slug_to_project_name(slug)
    _ensure_cloudflare_project(account_id, token, name)

    # Get an upload JWT for the asset endpoints
    tok_resp = _cf_request(
        "GET",
        f"{CF_API_BASE}/accounts/{account_id}/pages/projects/{name}/upload-token",
        token=token,
    )
    jwt = (tok_resp.get("result") or {}).get("jwt")
    if not jwt:
        raise PublishError(f"Cloudflare upload-token: {tok_resp}")

    # Hash every file (read once, cache bytes + content-type by hash).
    # Big sites otherwise paid 2x disk I/O — once to hash, once to upload.
    files = _enumerate_publish_files(source_dir)
    if not files:
        raise PublishError("No files to publish.")
    manifest: dict[str, str] = {}
    hash_to_payload: dict[str, tuple[bytes, str]] = {}
    byte_count = 0
    for path, url_path in files:
        data = path.read_bytes()
        byte_count += len(data)
        ct, _ = mimetypes.guess_type(path.name)
        ct = ct or "application/octet-stream"
        h = _cf_blake3_hash(data, ct)
        manifest[url_path] = h
        # First file at a hash wins; later duplicates re-use bytes.
        hash_to_payload.setdefault(h, (data, ct))

    # Check missing
    missing_resp = _cf_request(
        "POST",
        f"{CF_PAGES_API}/assets/check-missing",
        token=jwt,
        body={"hashes": list(hash_to_payload.keys())},
    )
    missing = (missing_resp.get("result") or [])

    # Upload missing in batches (Cloudflare suggests up to ~50 per batch / 5 MB total)
    BATCH = 30
    for i in range(0, len(missing), BATCH):
        batch = missing[i:i + BATCH]
        payload = []
        for h in batch:
            entry = hash_to_payload.get(h)
            if not entry:
                continue
            data, ct = entry
            payload.append({
                "key":      h,
                "value":    base64.b64encode(data).decode("ascii"),
                "metadata": {"contentType": ct},
                "base64":   True,
            })
        if not payload:
            continue
        _cf_request(
            "POST",
            f"{CF_PAGES_API}/assets/upload",
            token=jwt,
            body=payload,
        )

    # Create deployment (multipart form with the manifest)
    deploy_resp = _create_cloudflare_deployment(
        account_id, token, name, manifest, branch="main",
    )
    result_obj = deploy_resp.get("result") or {}
    deployment_id = result_obj.get("id") or ""
    live_url = result_obj.get("url") or f"https://{name}.pages.dev"

    return PublishResult(
        slug=slug,
        kind="cloudflare",
        url=live_url,
        deployed_at=datetime.now(timezone.utc).isoformat(),
        bytes_published=byte_count,
        files_published=len(files),
        deployment_id=deployment_id,
        project_name=name,
    )


def _create_cloudflare_deployment(
    account_id: str,
    token: str,
    project_name: str,
    manifest: dict,
    branch: str = "main",
) -> dict:
    """POST a deployment via multipart/form-data containing the manifest."""
    boundary = "pebbleboundary" + str(int(time.time() * 1000))
    url = f"{CF_API_BASE}/accounts/{account_id}/pages/projects/{project_name}/deployments"

    parts: list[bytes] = []

    def _field(name: str, value: str) -> None:
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        parts.append(value.encode("utf-8"))
        parts.append(b"\r\n")

    _field("manifest", json.dumps(manifest))
    _field("branch", branch)
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type":  f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            err_body = json.loads(raw)
        except Exception:
            err_body = {"raw": raw}
        raise PublishError(f"Cloudflare deployment failed: HTTP {e.code} — {err_body}")
    except Exception as e:
        raise PublishError(f"Cloudflare deployment unreachable: {e}")
    try:
        return json.loads(raw)
    except Exception:
        raise PublishError(f"Cloudflare deployment returned non-JSON: {raw[:200]}")


# --------- Publish state files --------------------------------------------

def _publish_state_path(slug: str) -> Path:
    return _engine_output_dir() / slug / "publish.json"


def _publish_history_path(slug: str) -> Path:
    return _engine_output_dir() / slug / "publish_log.json"


def write_publish_state(slug: str, result: PublishResult) -> None:
    """Persist the latest publish result + append to publish_log.json."""
    try:
        _publish_state_path(slug).write_text(
            json.dumps(result.to_dict(), indent=2), encoding="utf-8"
        )
    except Exception:
        pass
    try:
        log = read_publish_history(slug)
        log.append(result.to_dict())
        _publish_history_path(slug).write_text(
            json.dumps(log[-50:], indent=2), encoding="utf-8"
        )
    except Exception:
        pass


def read_publish_state(slug: str) -> Optional[dict]:
    p = _publish_state_path(slug)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def read_publish_history(slug: str) -> list[dict]:
    p = _publish_history_path(slug)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


__all__ = [
    "PublishError",
    "PublishResult",
    "package_zip",
    "cloudflare_configured",
    "cloudflare_setup_checklist",
    "slug_to_project_name",
    "publish_to_cloudflare",
    "read_publish_state",
    "read_publish_history",
    "write_publish_state",
]
