"""Tests for `pebble.storage` — the Supabase Storage REST wrapper.

The actual upload talks to Supabase's REST API; we monkeypatch
`urllib.request.urlopen` so no network call escapes. The HTTP
endpoint (POST /api/forms/<slug>/upload) is exercised in
tests/test_forms.py.
"""
from __future__ import annotations

import io
import json
from typing import Any

import pytest

from pebble import storage


# Real magic bytes for the types we accept — used as a baseline body
# in upload tests so the magic-byte validator passes.
_PNG_HEADER  = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
_JPEG_HEADER = b"\xff\xd8\xff\xe0" + b"\x00" * 16
_PDF_HEADER  = b"%PDF-1.4\n" + b"\x00" * 16


# ---- Config helpers + fixtures ------------------------------------------

@pytest.fixture(autouse=True)
def _set_supabase_env(monkeypatch):
    """Default fixture: act as if Supabase env is configured."""
    monkeypatch.setenv("PEBBLE_SUPABASE_URL", "https://proj.supabase.co")
    monkeypatch.setenv("PEBBLE_SUPABASE_SERVICE_ROLE_KEY", "service-role-fake-key")
    monkeypatch.delenv("PEBBLE_SUPABASE_FORM_UPLOADS_BUCKET", raising=False)
    yield


# ---- is_configured -------------------------------------------------------

def test_is_configured_requires_both_vars(monkeypatch):
    assert storage.is_configured() is True
    monkeypatch.delenv("PEBBLE_SUPABASE_URL")
    assert storage.is_configured() is False


def test_is_configured_false_when_service_role_missing(monkeypatch):
    monkeypatch.delenv("PEBBLE_SUPABASE_SERVICE_ROLE_KEY")
    assert storage.is_configured() is False


def test_is_configured_false_when_url_blank(monkeypatch):
    monkeypatch.setenv("PEBBLE_SUPABASE_URL", "")
    assert storage.is_configured() is False


# ---- _safe_name ----------------------------------------------------------

def test_safe_name_strips_disallowed_chars():
    assert storage._safe_name("my file (1).pdf") == "my_file_1_.pdf"


def test_safe_name_strips_directory_traversal():
    assert storage._safe_name("../../etc/passwd") == "passwd"


def test_safe_name_caps_length_preserves_extension():
    name = "a" * 200 + ".pdf"
    out = storage._safe_name(name)
    assert out.endswith(".pdf")
    assert len(out) <= 80


def test_safe_name_handles_empty_input():
    assert storage._safe_name("") == "file"
    assert storage._safe_name(None) == "file"  # type: ignore[arg-type]


def test_safe_name_handles_unicode():
    """Non-ASCII gets collapsed to underscores — Supabase keys are
    safer with strict ASCII."""
    out = storage._safe_name("résumé café.pdf")
    assert "/" not in out
    assert out.endswith(".pdf")


# ---- _safe_slug ----------------------------------------------------------

def test_safe_slug_lowercases_and_strips():
    assert storage._safe_slug("Acme-Co_123") == "acme-co_123"


def test_safe_slug_rejects_path_traversal():
    out = storage._safe_slug("../escape")
    assert "/" not in out
    assert ".." not in out


def test_safe_slug_handles_empty():
    assert storage._safe_slug("") == "unknown"
    assert storage._safe_slug(None) == "unknown"  # type: ignore[arg-type]


# ---- upload_attachment ---------------------------------------------------

class _FakeResponse:
    def __init__(self, status: int = 200, body: bytes = b'{"Key":"x"}'):
        self.status = status
        self._body = body

    def read(self, n: int = -1) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def test_upload_raises_when_not_configured(monkeypatch):
    monkeypatch.delenv("PEBBLE_SUPABASE_URL")
    with pytest.raises(storage.StorageError, match="not configured"):
        storage.upload_attachment(
            "acme", "x.png", _PNG_HEADER, "image/png",
        )


def test_upload_rejects_empty_content():
    with pytest.raises(storage.StorageError, match="empty"):
        storage.upload_attachment("acme", "x.png", b"", "image/png")


def test_upload_rejects_missing_content_type():
    with pytest.raises(storage.StorageError, match="content_type"):
        storage.upload_attachment("acme", "x.png", b"data", "")


def test_upload_constructs_correct_url(monkeypatch):
    captured: dict[str, Any] = {}
    def fake_urlopen(req, *_args, **_kwargs):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.headers)
        captured["data"] = req.data
        captured["method"] = req.method
        return _FakeResponse(200)
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    result = storage.upload_attachment(
        slug="acme",
        filename="photo.jpg",
        content=_JPEG_HEADER,
        content_type="image/jpeg",
    )
    assert captured["method"] == "POST"
    # URL starts with the project base + storage endpoint + bucket
    assert captured["url"].startswith("https://proj.supabase.co/storage/v1/object/form-uploads/")
    # Path begins with slug folder
    assert "acme/" in captured["url"]
    # File body sent through
    assert captured["data"] == _JPEG_HEADER
    # Bearer token + content-type set (urllib normalizes header casing)
    headers_lower = {k.lower(): v for k, v in captured["headers"].items()}
    assert headers_lower["authorization"] == "Bearer service-role-fake-key"
    assert headers_lower["content-type"] == "image/jpeg"
    # Result carries the bucket-relative path + a derived public URL
    assert result.path.startswith("acme/")
    assert result.public_url and "public/form-uploads/" in result.public_url


def test_upload_uses_custom_bucket_env(monkeypatch):
    monkeypatch.setenv("PEBBLE_SUPABASE_FORM_UPLOADS_BUCKET", "alt-bucket")
    captured = {}
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda req, *_a, **_k: captured.update({"url": req.full_url}) or _FakeResponse(200),
    )
    storage.upload_attachment("acme", "x.png", _PNG_HEADER, "image/png")
    assert "/alt-bucket/" in captured["url"]


def test_upload_includes_random_nonce_segment(monkeypatch):
    """Two uploads of the same filename should produce different paths
    so they don't collide (and so visitors can't predict each other's
    upload URLs)."""
    monkeypatch.setattr(
        "urllib.request.urlopen", lambda *_a, **_k: _FakeResponse(200))
    a = storage.upload_attachment("acme", "x.png", _PNG_HEADER, "image/png")
    b = storage.upload_attachment("acme", "x.png", _PNG_HEADER, "image/png")
    assert a.path != b.path


def test_upload_raises_on_http_error(monkeypatch):
    import urllib.error
    err = urllib.error.HTTPError(
        url="x", code=400, msg="Bad",
        hdrs=None,  # type: ignore[arg-type]
        fp=io.BytesIO(json.dumps({"message": "Bucket not found"}).encode()),
    )
    def fake_urlopen(*_a, **_kw):
        raise err
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(storage.StorageError, match="Bucket not found"):
        storage.upload_attachment("acme", "x.png", _PNG_HEADER, "image/png")


def test_upload_raises_on_url_error(monkeypatch):
    import urllib.error
    def fake_urlopen(*_a, **_kw):
        raise urllib.error.URLError("DNS lookup failed")
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(storage.StorageError, match="unreachable"):
        storage.upload_attachment("acme", "x.png", _PNG_HEADER, "image/png")


# ---- create_signed_url --------------------------------------------------

def test_signed_url_constructs_full_url(monkeypatch):
    def fake_urlopen(*_a, **_kw):
        body = json.dumps({"signedURL": "/object/sign/form-uploads/acme/abc/x.png?token=tok123"}).encode()
        return _FakeResponse(200, body)
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    url = storage.create_signed_url("acme/abc/x.png", expires_in_seconds=60)
    assert url.startswith("https://proj.supabase.co/storage/v1/")
    assert "token=tok123" in url


def test_signed_url_raises_when_not_configured(monkeypatch):
    monkeypatch.delenv("PEBBLE_SUPABASE_URL")
    with pytest.raises(storage.StorageError, match="not configured"):
        storage.create_signed_url("acme/x.png")


def test_signed_url_raises_on_missing_signed_url_field(monkeypatch):
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *_a, **_k: _FakeResponse(200, b'{"unrelated": "field"}'),
    )
    with pytest.raises(storage.StorageError, match="missing"):
        storage.create_signed_url("acme/x.png")


# ---- NLM round on Tracks 9–11: double-extension + magic-byte defense ----

def test_safe_name_collapses_internal_dots():
    """Double-extension confusion: "malware.php.jpg" must become
    "malware_php.jpg" so the file can't be mistaken for a PHP that
    happens to end in .jpg or a JPEG with a PHP-like middle name."""
    assert storage._safe_name("malware.php.jpg") == "malware_php.jpg"
    assert storage._safe_name("a.b.c.d.exe") == "a_b_c_d.exe"


def test_safe_name_preserves_simple_extension():
    """A single dot stays as-is."""
    assert storage._safe_name("photo.jpg") == "photo.jpg"
    assert storage._safe_name("report.pdf") == "report.pdf"


def test_validate_magic_bytes_accepts_real_png():
    assert storage.validate_magic_bytes(_PNG_HEADER, "image/png") is True


def test_validate_magic_bytes_accepts_real_jpeg():
    assert storage.validate_magic_bytes(_JPEG_HEADER, "image/jpeg") is True


def test_validate_magic_bytes_accepts_real_pdf():
    assert storage.validate_magic_bytes(_PDF_HEADER, "application/pdf") is True


def test_validate_magic_bytes_rejects_jpeg_with_png_header():
    """MIME-spoof defense: bytes are PNG but content_type says JPEG."""
    assert storage.validate_magic_bytes(_PNG_HEADER, "image/jpeg") is False


def test_validate_magic_bytes_rejects_arbitrary_bytes_as_image():
    """Plain text declared as image must be rejected."""
    assert storage.validate_magic_bytes(b"hello world" * 4, "image/png") is False


def test_validate_magic_bytes_accepts_heic_without_strict_check():
    """HEIC has variable ftyp box; we allow it (in the map with None)."""
    assert storage.validate_magic_bytes(b"\x00\x00\x00\x20ftypheic", "image/heic") is True


def test_validate_magic_bytes_rejects_short_input():
    """A 1-byte upload can't carry a 4-byte magic header."""
    assert storage.validate_magic_bytes(b"x", "image/png") is False


def test_validate_magic_bytes_rejects_unknown_mime():
    """If declared MIME isn't in the map, fail closed."""
    assert storage.validate_magic_bytes(_PNG_HEADER, "application/octet-stream") is False


def test_upload_refuses_mime_spoof(monkeypatch):
    """End-to-end: claim image/jpeg, send PNG bytes → upload refused
    before any network call. Closes the NLM T2."""
    monkeypatch.setattr("urllib.request.urlopen", lambda *_a, **_k: _FakeResponse(200))
    with pytest.raises(storage.StorageError, match="magic-byte"):
        storage.upload_attachment("acme", "x.jpg", _PNG_HEADER, "image/jpeg")
