"""HTTP route handlers extracted from PebbleHandler.

Each module exposes a `run_*` function that takes the BaseHTTPRequestHandler
instance as its first argument and writes the response on it. The dispatch
in PebbleHandler.do_POST / do_GET stays in pebble_engine.py — these modules
just hold the per-route implementations.
"""
