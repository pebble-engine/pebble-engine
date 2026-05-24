"""Fly.io preview deployment — per-project Fly app + Machine that runs
`next dev` for a generated Pebble site.

2026-05-23 POC complete: validated indie-bookstore deploys, serves, sleeps,
and wakes. Cold deploy ~17s, cold wake ~50s, hot navigation 5-7s.

Architecture:
  - One Fly app per slug: `pebble-preview-<slug>`
  - One Machine inside, auto-stop on idle (5 min default), auto-wake on traffic
  - Site files baked into Docker image on each deploy
  - URL: https://pebble-preview-<slug>.fly.dev

This module is the CLI bridge — it provides `deploy_project(slug, site_dir)`
that the engine's `_handle_preview` can call (next-session work) AND a
standalone CLI for one-off manual deploys.

Usage:
    python -m pebble.fly_preview deploy indie-bookstore
    python -m pebble.fly_preview status indie-bookstore
    python -m pebble.fly_preview destroy indie-bookstore

Requires:
    - FLY_API_TOKEN in .env (Fly personal access token)
    - flyctl installed (auto-detected at standard paths)
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pebble.log import log


# Fly's free + cheap path: shared-cpu-1x with 1GB RAM, $0.0027/hr running, $0 sleeping.
# Per-project app keeps URLs stable and provisioning simple.
FLY_REGION_DEFAULT = "ord"  # Chicago — low latency from US Eastern
FLY_VM_SIZE = "shared-cpu-1x"
FLY_VM_MEMORY = "1gb"


def _find_flyctl() -> Optional[str]:
    """Locate flyctl. Returns the executable path or None if not installed."""
    # Standard PATH lookup
    found = shutil.which("flyctl") or shutil.which("fly")
    if found:
        return found
    # Windows default install location
    home = Path.home()
    for candidate in [
        home / ".fly" / "bin" / "flyctl.exe",
        home / ".fly" / "bin" / "fly.exe",
        home / ".fly" / "bin" / "flyctl",
        home / ".fly" / "bin" / "fly",
    ]:
        if candidate.exists():
            return str(candidate)
    return None


def _fly_env() -> dict:
    """Environment for flyctl subprocess calls. FLY_API_TOKEN is required."""
    env = os.environ.copy()
    token = env.get("FLY_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "FLY_API_TOKEN not set. Get one at https://fly.io/user/personal_access_tokens "
            "and add it to .env."
        )
    # Ensure flyctl sees the token (it reads FLY_API_TOKEN or FLY_ACCESS_TOKEN).
    env["FLY_API_TOKEN"] = token
    return env


def _run_fly(args: list[str], cwd: Optional[Path] = None, timeout: int = 600) -> subprocess.CompletedProcess:
    """Run flyctl with the given args. Raises if flyctl isn't installed."""
    flyctl = _find_flyctl()
    if not flyctl:
        raise RuntimeError(
            "flyctl not found. Install via PowerShell: "
            "`iwr https://fly.io/install.ps1 -useb | iex`"
        )
    return subprocess.run(
        [flyctl, *args],
        cwd=str(cwd) if cwd else None,
        env=_fly_env(),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ─────────────────────────────────────────────────────────────────
# Dockerfile + fly.toml templates — written into a temp build context
# alongside the slug's site files for `flyctl deploy`.
# ─────────────────────────────────────────────────────────────────

DOCKERFILE_TEMPLATE = """\
# Pebble preview Machine — runs `next dev` for a single generated site.
FROM node:20-alpine AS base
WORKDIR /app
RUN apk add --no-cache tini
COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund --loglevel=error
COPY . .
ENV NODE_ENV=development
ENV PORT=8080
EXPOSE 8080
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["npm", "run", "dev", "--", "-p", "8080", "-H", "0.0.0.0"]
"""

FLY_TOML_TEMPLATE = """\
app = "pebble-preview-{slug}"
primary_region = "{region}"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 0
  [http_service.concurrency]
    type = "requests"
    soft_limit = 50
    hard_limit = 100

[[vm]]
  size = "{vm_size}"
  memory = "{vm_memory}"
"""

DOCKERIGNORE = """\
node_modules
.next
.git
*.md
HANDOFF.md
CLIENT_ANSWERS.md
STYLE_GUIDE.md
TODO_ASSETS.md
.env*
.fly
"""


# ─────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────

@dataclass
class DeployResult:
    """Outcome of a deploy_project call."""
    ok:      bool
    url:     Optional[str]      # Live preview URL on success
    app:     str                # The Fly app name (pebble-preview-<slug>)
    error:   Optional[str]      # Human-readable error on failure
    elapsed: float              # Seconds spent on the deploy


def app_name(slug: str) -> str:
    """The Fly app name for a given project slug. Stable across deploys."""
    return f"pebble-preview-{slug}"


def preview_url(slug: str) -> str:
    """The public Fly URL for a project's preview. Stable across deploys."""
    return f"https://{app_name(slug)}.fly.dev"


def app_exists(slug: str) -> bool:
    """True when the Fly app for this slug has been created."""
    result = _run_fly(["apps", "list", "--json"], timeout=30)
    if result.returncode != 0:
        log.warning("[fly] apps list failed: %s", result.stderr[:200])
        return False
    import json
    try:
        apps = json.loads(result.stdout or "[]")
        target = app_name(slug)
        return any(a.get("Name") == target for a in apps)
    except Exception as exc:
        log.warning("[fly] failed to parse apps list: %s", exc)
        return False


def deploy_project(
    slug: str,
    site_dir: Path,
    org: str = "personal",
    region: str = FLY_REGION_DEFAULT,
) -> DeployResult:
    """Deploy a Pebble-generated site to its Fly preview app.

    Creates the app on first call (one-shot, idempotent). Subsequent calls
    redeploy with current files — Fly handles the rolling restart.

    Args:
      slug: project slug (e.g. "indie-bookstore"). Determines app name + URL.
      site_dir: path to the project's site/ directory (where package.json lives).
      org: Fly org slug. Default "personal".
      region: Fly region code. Default "ord" (Chicago).

    Returns DeployResult with url + app + ok flag.
    """
    import time
    started = time.time()
    target_app = app_name(slug)

    if not site_dir.exists() or not (site_dir / "package.json").exists():
        return DeployResult(
            ok=False, url=None, app=target_app, elapsed=time.time() - started,
            error=f"site_dir {site_dir} missing or has no package.json",
        )

    # Stage 1: ensure the app exists.
    if not app_exists(slug):
        log.info("[fly] creating app %s in org %s", target_app, org)
        result = _run_fly(["apps", "create", target_app, "--org", org], timeout=60)
        if result.returncode != 0:
            return DeployResult(
                ok=False, url=None, app=target_app, elapsed=time.time() - started,
                error=f"flyctl apps create failed: {result.stderr.strip()[:400]}",
            )

    # Stage 2: stage Dockerfile + fly.toml + .dockerignore alongside the site files.
    # We write them into the site_dir itself rather than a temp dir so the build
    # context is exactly one directory tree. flyctl deploy's tar-and-ship treats
    # site_dir as the docker build root.
    (site_dir / "Dockerfile").write_text(DOCKERFILE_TEMPLATE, encoding="utf-8")
    (site_dir / "fly.toml").write_text(FLY_TOML_TEMPLATE.format(
        slug=slug, region=region, vm_size=FLY_VM_SIZE, vm_memory=FLY_VM_MEMORY,
    ), encoding="utf-8")
    (site_dir / ".dockerignore").write_text(DOCKERIGNORE, encoding="utf-8")

    # Stage 3: deploy. --remote-only uses Fly's builders (no local Docker needed).
    # --ha=false keeps a single Machine (no high-availability replica for preview use).
    log.info("[fly] deploying %s from %s", target_app, site_dir)
    result = _run_fly(
        ["deploy", "--remote-only", "--ha=false"],
        cwd=site_dir,
        timeout=900,  # 15 min ceiling; typical 60-180s
    )
    if result.returncode != 0:
        # Surface as much of the flyctl stderr as is useful for triage.
        tail = result.stderr.strip().split("\n")[-20:]
        return DeployResult(
            ok=False, url=None, app=target_app, elapsed=time.time() - started,
            error=f"flyctl deploy failed:\n" + "\n".join(tail),
        )

    log.info("[fly] %s deployed in %.1fs", target_app, time.time() - started)
    return DeployResult(
        ok=True, url=preview_url(slug), app=target_app,
        elapsed=time.time() - started, error=None,
    )


def status(slug: str) -> dict:
    """Return Fly's view of the app's machines. Useful for the engine to
    decide whether a preview is warm, stopped, or absent."""
    if not app_exists(slug):
        return {"slug": slug, "app": app_name(slug), "exists": False}
    result = _run_fly(["machines", "list", "-a", app_name(slug), "--json"], timeout=30)
    if result.returncode != 0:
        return {
            "slug": slug, "app": app_name(slug), "exists": True,
            "error": result.stderr.strip()[:200],
        }
    import json
    try:
        machines = json.loads(result.stdout or "[]")
        return {
            "slug": slug, "app": app_name(slug), "exists": True,
            "url": preview_url(slug),
            "machine_count": len(machines),
            "states": [m.get("state") for m in machines],
        }
    except Exception as exc:
        return {"slug": slug, "app": app_name(slug), "exists": True, "error": str(exc)}


def destroy(slug: str) -> bool:
    """Tear down the Fly app for a slug. Used when a Pebble project is deleted."""
    if not app_exists(slug):
        return True
    result = _run_fly(["apps", "destroy", app_name(slug), "--yes"], timeout=60)
    if result.returncode != 0:
        log.warning("[fly] destroy failed for %s: %s", slug, result.stderr.strip()[:200])
        return False
    return True


# Module-level lock + dedup map so two concurrent build pipelines (rare but
# possible if Marc retries during a slow LLM round) don't kick off two
# deploys for the same slug. Daemon threads = won't block engine shutdown.
import threading as _threading
_DEPLOY_LOCK   = _threading.Lock()
_IN_FLIGHT_DEPLOYS: dict[str, _threading.Thread] = {}


def deploy_in_background(slug: str, site_dir: Path, org: str = "personal") -> bool:
    """Fire-and-forget deploy. Returns True if a thread was started (or one
    is already running for this slug); False on hard pre-check failures.

    Errors during the actual deploy are logged and dropped — the build
    pipeline must not be blocked by Fly hiccups. The engine's _handle_preview
    falls back to local previews gracefully when the Fly app doesn't exist.
    """
    if os.environ.get("PEBBLE_PREVIEW_BACKEND", "").strip().lower() != "fly":
        return False  # Backend not enabled; nothing to do
    if not (site_dir / "package.json").exists():
        log.info("[fly] skipping background deploy for %s — no package.json", slug)
        return False

    with _DEPLOY_LOCK:
        existing = _IN_FLIGHT_DEPLOYS.get(slug)
        if existing and existing.is_alive():
            log.info("[fly] deploy already in flight for %s, skipping duplicate", slug)
            return True

        def _runner() -> None:
            try:
                log.info("[fly] background deploy starting for %s", slug)
                result = deploy_project(slug, site_dir, org=org)
                if result.ok:
                    log.info("[fly] background deploy OK for %s in %.1fs → %s",
                             slug, result.elapsed, result.url)
                else:
                    log.warning("[fly] background deploy FAILED for %s in %.1fs: %s",
                                slug, result.elapsed, (result.error or "")[:300])
            except Exception as exc:
                log.warning("[fly] background deploy crashed for %s: %s", slug, exc)
            finally:
                with _DEPLOY_LOCK:
                    _IN_FLIGHT_DEPLOYS.pop(slug, None)

        thread = _threading.Thread(
            target=_runner, daemon=True, name=f"fly-deploy-{slug}",
        )
        _IN_FLIGHT_DEPLOYS[slug] = thread
        thread.start()
        return True


# ─────────────────────────────────────────────────────────────────
# CLI — `python -m pebble.fly_preview <cmd> <slug>`
# ─────────────────────────────────────────────────────────────────

def _cli() -> int:
    parser = argparse.ArgumentParser(
        prog="pebble.fly_preview",
        description="Deploy Pebble-generated sites to Fly.io for instant preview hosting.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_deploy = sub.add_parser("deploy", help="Create + deploy a Fly app for a project")
    p_deploy.add_argument("slug")
    p_deploy.add_argument("--org", default="personal")
    p_deploy.add_argument("--region", default=FLY_REGION_DEFAULT)
    p_deploy.add_argument("--root", help="Repo root (default: discovers via env or cwd)")

    p_status = sub.add_parser("status", help="Show Fly state for a project")
    p_status.add_argument("slug")

    p_destroy = sub.add_parser("destroy", help="Tear down a project's Fly app")
    p_destroy.add_argument("slug")

    p_migrate = sub.add_parser(
        "migrate-all",
        help="Bulk-deploy every project in output/ that has package.json. "
             "Use once after flipping PEBBLE_PREVIEW_BACKEND=fly so existing "
             "projects also have Fly apps.",
    )
    p_migrate.add_argument("--org", default="personal")
    p_migrate.add_argument("--root", help="Repo root (default: cwd)")
    p_migrate.add_argument("--dry-run", action="store_true",
                           help="List what would deploy without actually deploying")
    p_migrate.add_argument("--sleep", type=int, default=10,
                           help="Seconds to wait between deploys (default 10). "
                                "Spreads out Fly API calls so we don't hammer them.")

    args = parser.parse_args()

    # Load .env so FLY_API_TOKEN + sibling vars are available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    # Resolve site_dir for deploy
    def _resolve_site_dir(slug: str, root_arg: Optional[str]) -> Path:
        root = Path(root_arg) if root_arg else Path(os.environ.get("PEBBLE_BRIEF_ROOT", "")) or Path.cwd()
        # If the engine writes output/ here, the site lives at output/<slug>/site/
        for candidate in [
            root / "output" / slug / "site",
            Path.cwd() / "output" / slug / "site",
            Path(__file__).resolve().parent.parent / "output" / slug / "site",
        ]:
            if candidate.exists():
                return candidate
        # Fall back to the last candidate so the error in deploy_project is clear
        return root / "output" / slug / "site"

    if args.cmd == "deploy":
        site_dir = _resolve_site_dir(args.slug, args.root)
        print(f"→ deploying {args.slug} from {site_dir}")
        try:
            result = deploy_project(args.slug, site_dir, org=args.org, region=args.region)
        except RuntimeError as exc:
            print(f"✗ {exc}", file=sys.stderr)
            return 1
        if result.ok:
            print(f"✓ {result.app} live in {result.elapsed:.1f}s")
            print(f"  {result.url}")
            return 0
        else:
            print(f"✗ deploy failed in {result.elapsed:.1f}s:\n{result.error}", file=sys.stderr)
            return 1

    if args.cmd == "status":
        try:
            s = status(args.slug)
        except RuntimeError as exc:
            print(f"✗ {exc}", file=sys.stderr)
            return 1
        import json
        print(json.dumps(s, indent=2))
        return 0

    if args.cmd == "destroy":
        try:
            ok = destroy(args.slug)
        except RuntimeError as exc:
            print(f"✗ {exc}", file=sys.stderr)
            return 1
        print("✓ destroyed" if ok else "✗ destroy failed")
        return 0 if ok else 1

    if args.cmd == "migrate-all":
        import time as _time
        root = Path(args.root) if args.root else (
            Path(os.environ.get("PEBBLE_BRIEF_ROOT", "")) or Path.cwd()
        )
        output_dir = root / "output"
        if not output_dir.exists():
            print(f"✗ {output_dir} does not exist", file=sys.stderr)
            return 1
        # Find every project that has a package.json — those are the ones
        # that can actually run next dev on Fly.
        candidates: list[tuple[str, Path]] = []
        for project_dir in sorted(output_dir.iterdir()):
            if not project_dir.is_dir():
                continue
            site = project_dir / "site"
            if (site / "package.json").exists():
                candidates.append((project_dir.name, site))
        if not candidates:
            print("No project directories with site/package.json found.")
            return 0
        print(f"Found {len(candidates)} project(s) eligible for Fly deploy:")
        for slug, _ in candidates:
            print(f"  - {slug}")
        if args.dry_run:
            print("\n(dry-run; nothing deployed)")
            return 0
        print(f"\nDeploying — {args.sleep}s between calls so Fly's rate limits stay happy.\n")
        succeeded, failed = 0, 0
        for i, (slug, site) in enumerate(candidates):
            print(f"[{i+1}/{len(candidates)}] {slug} → ", end="", flush=True)
            try:
                r = deploy_project(slug, site, org=args.org)
            except RuntimeError as exc:
                print(f"✗ {exc}")
                failed += 1
                continue
            if r.ok:
                print(f"✓ {r.elapsed:.1f}s → {r.url}")
                succeeded += 1
            else:
                print(f"✗ {(r.error or '').splitlines()[0][:100]}")
                failed += 1
            # Don't sleep after the last one
            if i < len(candidates) - 1 and args.sleep > 0:
                _time.sleep(args.sleep)
        print(f"\nDone — {succeeded} succeeded, {failed} failed.")
        return 0 if failed == 0 else 1

    return 2


if __name__ == "__main__":
    sys.exit(_cli())


__all__ = [
    "DeployResult",
    "app_name",
    "preview_url",
    "app_exists",
    "deploy_project",
    "status",
    "destroy",
]
