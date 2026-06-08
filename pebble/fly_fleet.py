"""Engine-side client for the Fly Machines preview fleet.

Each active preview runs in its own Fly Machine cloned from the shared
preview-machine image (see fleet/preview-machine/). This module:
  - creates / starts / stops / destroys machines (Fly Machines REST API),
  - keeps a slug -> machine registry (survives engine restarts),
  - pushes source files to a machine's receiver (/__pebble/sync) for HMR,
  - reaps idle machines + enforces a concurrency cap.

Pure Python. Live verification (a real machine boot + HMR + per-machine public
routing) needs FLY_API_TOKEN and is done separately — see the design spec.

Env: FLY_API_TOKEN, FLY_APP, FLY_PREVIEW_IMAGE, PEBBLE_FLEET_SECRET
     (optional) PEBBLE_FLEET_MAX (default 50), PEBBLE_FLEET_IDLE_MIN (default 15)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

import httpx

_FLY_API = "https://api.machines.dev"


# --------------------------------------------------------------------------- #
# Config + registry
# --------------------------------------------------------------------------- #

def fleet_configured() -> bool:
    return all(
        os.environ.get(k, "").strip()
        for k in ("FLY_API_TOKEN", "FLY_APP", "FLY_PREVIEW_IMAGE", "PEBBLE_FLEET_SECRET")
    )


def _app() -> str:
    return os.environ["FLY_APP"].strip()


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {os.environ['FLY_API_TOKEN'].strip()}",
            "Content-Type": "application/json"}


def _max() -> int:
    try:
        return int(os.environ.get("PEBBLE_FLEET_MAX", "50"))
    except ValueError:
        return 50


def _fleet_dir() -> Path:
    eng = sys.modules.get("pebble_engine") or sys.modules["__main__"]
    return Path(eng.OUTPUT_DIR) / ".fleet"


def _registry_path() -> Path:
    return _fleet_dir() / "registry.json"


def _load_registry() -> dict[str, Any]:
    p = _registry_path()
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def _save_registry(reg: dict[str, Any]) -> None:
    p = _registry_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(reg, indent=2), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Public routing
# --------------------------------------------------------------------------- #

def machine_public_url(slug: str, machine: Optional[dict] = None) -> str:
    """Public base URL the browser iframe + the engine talk to.

    ⚠️ LIVE-VALIDATION ITEM: Fly's shared-app domain load-balances across
    machines and does NOT target one machine by URL. The two clean options
    (decide during live verification):
      - app-per-slug → https://pebble-preview-<slug>.fly.dev  (legacy scaffold)
      - one app + engine proxies with `fly-force-instance-id: <machine_id>`
    Until resolved, this returns the app domain (correct only with 1 machine).
    """
    return f"https://{_app()}.fly.dev"


# --------------------------------------------------------------------------- #
# Fly Machines REST
# --------------------------------------------------------------------------- #

def create_machine(slug: str) -> dict[str, Any]:
    body = {
        "config": {
            "image": os.environ["FLY_PREVIEW_IMAGE"].strip(),
            "guest": {"cpu_kind": "shared", "cpus": 1, "memory_mb": 512},
            "env": {"PEBBLE_FLEET_SECRET": os.environ["PEBBLE_FLEET_SECRET"].strip(),
                    "PORT": "8080"},
            "services": [{
                "protocol": "tcp",
                "internal_port": 8080,
                "ports": [
                    {"port": 443, "handlers": ["tls", "http"]},
                    {"port": 80, "handlers": ["http"]},
                ],
            }],
            "auto_destroy": False,
        },
    }
    r = httpx.post(f"{_FLY_API}/v1/apps/{_app()}/machines", headers=_headers(),
                   json=body, timeout=60.0)
    r.raise_for_status()
    return r.json()


def get_machine(machine_id: str) -> dict[str, Any]:
    r = httpx.get(f"{_FLY_API}/v1/apps/{_app()}/machines/{machine_id}",
                  headers=_headers(), timeout=30.0)
    r.raise_for_status()
    return r.json()


def start_machine(machine_id: str) -> None:
    httpx.post(f"{_FLY_API}/v1/apps/{_app()}/machines/{machine_id}/start",
               headers=_headers(), timeout=30.0).raise_for_status()


def stop_machine(machine_id: str) -> None:
    httpx.post(f"{_FLY_API}/v1/apps/{_app()}/machines/{machine_id}/stop",
               headers=_headers(), timeout=30.0).raise_for_status()


def destroy_machine(machine_id: str) -> None:
    httpx.delete(f"{_FLY_API}/v1/apps/{_app()}/machines/{machine_id}?force=true",
                 headers=_headers(), timeout=30.0).raise_for_status()


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

def ensure_machine(slug: str):
    """Ensure a started machine exists for *slug*; return its public URL.
    Returns None if the concurrency cap is hit for a NEW machine."""
    reg = _load_registry()
    entry = reg.get(slug)
    if entry:
        # Reuse — make sure it's started.
        try:
            state = get_machine(entry["machine_id"]).get("state")
        except Exception:
            state = None
        if state != "started":
            try:
                start_machine(entry["machine_id"])
            except Exception:
                pass
        entry["last_seen"] = time.time()
        reg[slug] = entry
        _save_registry(reg)
        return entry.get("url") or machine_public_url(slug)

    # New machine — enforce the concurrency cap.
    if len(reg) >= _max():
        return None
    m = create_machine(slug)
    url = machine_public_url(slug, m)
    reg[slug] = {"machine_id": m.get("id"), "url": url, "last_seen": time.time()}
    _save_registry(reg)
    return url


def touch(slug: str) -> None:
    reg = _load_registry()
    if slug in reg:
        reg[slug]["last_seen"] = time.time()
        _save_registry(reg)


def sync_files(slug: str, files: list[dict[str, Any]],
               deleted: Optional[list[str]] = None, timeout: float = 30.0) -> dict[str, Any]:
    """Push source files to the machine's receiver → HMR."""
    base = machine_public_url(slug)
    r = httpx.post(
        f"{base}/__pebble/sync",
        headers={"x-pebble-secret": os.environ["PEBBLE_FLEET_SECRET"].strip(),
                 "Content-Type": "application/json"},
        json={"files": files, "deleted": deleted or []},
        timeout=timeout,
    )
    r.raise_for_status()
    touch(slug)
    return r.json()


def wait_ready(slug: str, timeout: float = 60.0, interval: float = 2.0) -> bool:
    base = machine_public_url(slug)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = httpx.get(f"{base}/__pebble/healthz", timeout=10.0)
            if r.status_code == 200 and (r.json() or {}).get("ready"):
                return True
        except Exception:
            pass
        time.sleep(interval)
    return False


def reap_idle(max_idle_s: Optional[float] = None) -> list[str]:
    """Stop machines idle longer than max_idle_s. Returns stopped slugs."""
    if max_idle_s is None:
        try:
            max_idle_s = float(os.environ.get("PEBBLE_FLEET_IDLE_MIN", "15")) * 60
        except ValueError:
            max_idle_s = 900.0
    reg = _load_registry()
    now = time.time()
    stopped: list[str] = []
    for slug, entry in list(reg.items()):
        if now - float(entry.get("last_seen", now)) > max_idle_s:
            try:
                stop_machine(entry["machine_id"])
                stopped.append(slug)
            except Exception:
                pass
    return stopped


__all__ = [
    "fleet_configured", "machine_public_url",
    "create_machine", "get_machine", "start_machine", "stop_machine", "destroy_machine",
    "ensure_machine", "sync_files", "wait_ready", "touch", "reap_idle",
]
