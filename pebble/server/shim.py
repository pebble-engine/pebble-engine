"""HandlerShim — adapts a FastAPI Request to the handler interface that
all pebble/server/run_X() and pebble_engine.PebbleHandler._handle_X()
functions expect.

``HandlerShim`` is created lazily as a subclass of ``PebbleHandler`` the
first time a FastAPI request fires. Subclassing gives it the full
``_handle_X()`` method table without needing to extract every handler.

The socket-level methods (send_response, send_header, end_headers, wfile)
are overridden to capture the response in memory instead of writing to a
socket. ``shim_to_response()`` converts that captured state back to a
FastAPI ``Response``.
"""
from __future__ import annotations

import io
import json
import sys
from typing import Optional


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

class _HeadersDict:
    """Case-insensitive header wrapper that mimics http.client.HTTPMessage.get()."""

    def __init__(self, d: dict):
        self._d = {k.lower(): v for k, v in d.items()}

    def get(self, name: str, default: str = "") -> str:
        return self._d.get(name.lower(), default)


class _CaptureWFile:
    """Accumulates bytes from wfile.write() calls."""

    def __init__(self, shim: "HandlerShim"):
        self._shim = shim

    def write(self, data: bytes) -> int:
        if self._shim.binary_body is None:
            self._shim.binary_body = b""
        self._shim.binary_body += data
        return len(data)

    def flush(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Lazy class factory
# ---------------------------------------------------------------------------

_SHIM_CLASS: Optional[type] = None


def _build_shim_class() -> type:
    """Create HandlerShim subclassing PebbleHandler.

    Called once — result is cached in _SHIM_CLASS. PebbleHandler is
    looked up via sys.modules so we don't import pebble_engine at the
    module level (that would create a circular dependency because
    pebble_engine lazily imports pebble.app which imports this module).
    """
    mod = sys.modules.get("pebble_engine") or sys.modules.get("__main__")
    PebbleHandler = mod.PebbleHandler

    class HandlerShim(PebbleHandler):
        """Subclasses PebbleHandler to inherit all _handle_X() methods.

        Does NOT call BaseHTTPRequestHandler.__init__ — that requires a
        real socket. All attributes those methods depend on are set here.
        """

        def __init__(
            self,
            path: str,
            method: str,
            body: bytes,
            headers: dict,
            client_host: str = "127.0.0.1",
        ):
            self.path = path
            self._raw_path = path
            self.command = method.upper()
            self.client_address = (client_host, 0)
            self.rfile = io.BytesIO(body)
            self.headers = _HeadersDict(headers)
            self.request_version = "HTTP/1.1"
            self.close_connection = True

            # Response capture
            self.response_status: int = 200
            self.response_headers: list = []
            self.binary_body: Optional[bytes] = None
            self.wfile = _CaptureWFile(self)

        # -- Override socket-level methods to capture instead of write ------

        def send_response(self, code: int, message: str = "") -> None:
            self.response_status = code

        def send_header(self, keyword: str, value: str) -> None:
            self.response_headers.append((keyword, value))

        def end_headers(self) -> None:
            pass

        def _write_cors_headers(self) -> None:
            pass  # FastAPI CORSMiddleware handles CORS

        def log_message(self, fmt: str, *args) -> None:
            pass  # suppress BaseHTTPRequestHandler per-request stderr logging

        def log_request(self, code="-", size="-") -> None:
            pass

    return HandlerShim


class HandlerShim:
    """Placeholder so callers can do ``from pebble.server.shim import HandlerShim``.

    The real class is returned by ``get_shim_class()`` and is a subclass of
    PebbleHandler. This stub is never actually instantiated directly.
    """


def get_shim_class() -> type:
    global _SHIM_CLASS
    if _SHIM_CLASS is None:
        _SHIM_CLASS = _build_shim_class()
    return _SHIM_CLASS


def make_shim(
    path: str,
    method: str,
    body: bytes,
    headers: dict,
    client_host: str = "127.0.0.1",
):
    """Create a HandlerShim for the given request parameters."""
    return get_shim_class()(path, method, body, headers, client_host)


# ---------------------------------------------------------------------------
# Response converter
# ---------------------------------------------------------------------------

def shim_to_response(shim):
    """Convert captured shim response state to a FastAPI Response."""
    from fastapi.responses import JSONResponse, Response

    content_type = "application/octet-stream"
    for name, value in shim.response_headers:
        if name.lower() == "content-type":
            content_type = value
            break

    body_bytes = shim.binary_body or b""

    if "application/json" in content_type:
        try:
            data = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            data = {"error": "handler returned non-JSON body"}
        return JSONResponse(content=data, status_code=shim.response_status)

    # For responses with extra headers (e.g. Set-Cookie on auth endpoints),
    # copy them onto the Response object.
    extra = {
        k: v for k, v in shim.response_headers
        if k.lower() not in ("content-type", "content-length")
    }
    resp = Response(
        content=body_bytes,
        media_type=content_type,
        status_code=shim.response_status,
    )
    for k, v in extra.items():
        resp.headers[k] = v
    return resp
