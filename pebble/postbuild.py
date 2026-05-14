"""Post-build chain — runs after the LLM writes the site files.

1. `npm install` in the generated site_dir
2. `next dev` on a free port in the background
3. Poll the URL until it responds (4-min ceiling for first-build npm fetch)
4. Optional Playwright screenshots of hero/trust/services/footer

Every step soft-fails — a missing npm or unresponsive dev server returns
an error list to the caller, never raises.
"""
from __future__ import annotations
import socket
import sys
import time
import urllib.request
from pathlib import Path


def _find_free_port() -> int:
    """Ask the kernel for an unused TCP port. Used for the Next.js dev server
    so two concurrent builds don't fight over port 3000."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _poll_server(url: str, timeout_seconds: int = 90) -> bool:
    """Hit `url` every 1.5s until any 2xx-4xx response, or timeout. True if up."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if 200 <= r.status < 500:
                    return True
        except Exception:
            time.sleep(1.5)
    return False


def post_build_run_dev_server(site_dir: Path) -> dict:
    """npm install + next dev on a free port, in the background.

    Returns {"port": int, "pid": int, "url": str, "errors": [str]}.
    Caller is responsible for the lifetime of the spawned process.
    """
    import shutil
    import subprocess

    result: dict = {"port": None, "pid": None, "url": None, "errors": []}

    if not site_dir.exists() or not (site_dir / "package.json").exists():
        result["errors"].append("no package.json in site_dir; skip dev server")
        return result

    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm:
        result["errors"].append("npm not found in PATH; install Node.js")
        return result

    # 1. npm install — bounded timeout, captured.
    print(f"  Running `npm install` in {site_dir.name}...")
    try:
        subprocess.run(
            [npm, "install", "--no-audit", "--no-fund", "--loglevel=error"],
            cwd=str(site_dir),
            check=True,
            timeout=600,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode("utf-8", "ignore") if e.stderr else ""
        result["errors"].append(f"npm install failed: {stderr[:500]}")
        return result
    except subprocess.TimeoutExpired:
        result["errors"].append("npm install timed out after 600s")
        return result

    # 2. Start dev server on a free port in the background.
    port = _find_free_port()
    url = f"http://127.0.0.1:{port}"
    print(f"  Starting `next dev` on port {port}...")
    try:
        # Windows needs creationflags to detach; POSIX inherits stdin/out fine.
        creationflags = 0
        if sys.platform == "win32":
            creationflags = (
                subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            )
        proc = subprocess.Popen(
            [npm, "run", "dev", "--", "-p", str(port)],
            cwd=str(site_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags if sys.platform == "win32" else 0,
        )
    except Exception as e:
        result["errors"].append(f"failed to start dev server: {e}")
        return result

    # 3. Poll until server responds.
    # 240s — first build does npm install + initial Next compile, often 2-3 min.
    if not _poll_server(url, timeout_seconds=240):
        result["errors"].append("dev server did not respond within 240s")
        try:
            proc.terminate()
        except Exception:
            pass
        return result

    result["port"] = port
    result["pid"] = proc.pid
    result["url"] = url
    return result


def post_build_screenshots(server_url: str, out_dir: Path) -> dict:
    """Use Playwright to capture hero/trust-bar/services/footer screenshots.

    Gracefully degrades if Playwright is not installed.
    Returns {"screenshots": [relative paths], "errors": [str]}.
    """
    result: dict = {"screenshots": [], "errors": []}
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        result["errors"].append(
            "playwright not installed (pip install playwright && playwright install chromium)"
        )
        return result

    shots_dir = out_dir / "screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()
            page.goto(server_url, wait_until="domcontentloaded", timeout=15000)
            try:
                page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass

            shots = [
                ("01-hero.png",      0),
                ("02-trust-bar.png", 900),
                ("03-services.png",  1800),
                ("04-footer.png",    "bottom"),
            ]
            for filename, scroll in shots:
                try:
                    if scroll == "bottom":
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    else:
                        page.evaluate(f"window.scrollTo(0, {scroll})")
                    page.wait_for_timeout(900)
                    target = shots_dir / filename
                    page.screenshot(path=str(target), full_page=False)
                    result["screenshots"].append(str(target.relative_to(out_dir)))
                except Exception as e:
                    result["errors"].append(f"{filename}: {e}")

            browser.close()
    except Exception as e:
        result["errors"].append(f"playwright run failed: {e}")
    return result


__all__ = [
    "post_build_run_dev_server",
    "post_build_screenshots",
    "_find_free_port",
    "_poll_server",
]
