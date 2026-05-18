"""FastAPI application for Pebble Engine.

Wraps all existing PebbleHandler routes via HandlerShim so every
run_X() and _handle_X() function works unchanged, and adds a new
SSE endpoint (/api/generate-stream) for real-time build progress.

Import note: this module is imported lazily inside serve() in
pebble_engine.py — by the time it loads, pebble_engine is already in
sys.modules, which HandlerShim requires for the PebbleHandler lookup.
"""
from __future__ import annotations

import asyncio
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from pebble.server.router import route_delete, route_get, route_patch, route_post
from pebble.server.shim import make_shim, shim_to_response

# ---------------------------------------------------------------------------
# App + CORS
# ---------------------------------------------------------------------------

app = FastAPI(title="Pebble Engine", docs_url=None, redoc_url=None)

_allowed = [o.strip() for o in os.environ.get("PEBBLE_ALLOWED_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed if _allowed else ["*"],
    allow_credentials=bool(_allowed),   # credentials only when origins are explicit
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _request_path(request: Request) -> str:
    """Full path including query string (some handlers need the query)."""
    path = str(request.url.path)
    if request.url.query:
        path = f"{path}?{request.url.query}"
    return path


async def _run_route(request: Request, route_fn) -> None:
    """Create a HandlerShim and run route_fn in a thread executor."""
    body = await request.body()
    headers = dict(request.headers)
    client_host = (request.client.host if request.client else "127.0.0.1")
    shim = make_shim(_request_path(request), request.method, body, headers, client_host)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, route_fn, shim)
    return shim


# ---------------------------------------------------------------------------
# SSE endpoint — must be registered BEFORE the catch-all POST route
# ---------------------------------------------------------------------------

@app.post("/api/generate-stream")
async def generate_stream(request: Request):
    """POST /api/generate-stream — SSE build progress stream.

    Emits 8 event types: started, industry, style, generating, writing,
    evaluating, done, error. The ``done`` event carries the full
    GenerateResponse payload. Errors emit ``error`` then close.

    Uses fetch + ReadableStream on the client side (not EventSource,
    because EventSource only supports GET).
    """
    from pebble.server.build_stream import build_stream_generator

    body = await request.body()
    headers = dict(request.headers)
    client_host = (request.client.host if request.client else "127.0.0.1")
    return StreamingResponse(
        build_stream_generator(body, headers, client_host),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx/Caddy buffering
        },
    )


# ---------------------------------------------------------------------------
# Catch-all routes — delegate to existing route_X() dispatch functions
# ---------------------------------------------------------------------------

@app.get("/{path:path}")
async def handle_get(path: str, request: Request):
    shim = await _run_route(request, route_get)
    return shim_to_response(shim)


@app.post("/{path:path}")
async def handle_post(path: str, request: Request):
    shim = await _run_route(request, route_post)
    return shim_to_response(shim)


@app.delete("/{path:path}")
async def handle_delete(path: str, request: Request):
    shim = await _run_route(request, route_delete)
    return shim_to_response(shim)


@app.patch("/{path:path}")
async def handle_patch(path: str, request: Request):
    shim = await _run_route(request, route_patch)
    return shim_to_response(shim)
