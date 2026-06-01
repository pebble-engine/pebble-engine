"""Preview warmup — start `npm install` in a background thread as soon as
package.json lands on disk during the LLM stream.

The motivation (Phase 13f, 2026-05-20):
  - LLM stream takes 5-8 min for a multi-page build.
  - Post-stream npm install + next dev takes another 60-120s on cold cache.
  - Total time to clickable preview: 6-10 min.
  - With early warmup: npm install runs IN PARALLEL with the LLM stream, so
    by the time the stream finishes, install is done (or nearly done) and
    next dev can start immediately. Total time to preview: ~LLM time + 30s.

Design:
  - Single PreviewWarmup instance per build, scoped to the build's site_dir.
  - `start_install()` is idempotent — safe to call repeatedly as the
    streaming loop notices package.json on disk.
  - `wait_for_install(timeout)` blocks until install finishes or fails.
  - The thread is daemon so it doesn't block engine shutdown. If the engine
    restarts mid-install, the install dies cleanly with the process.

Failure modes:
  - npm not on PATH → install_error set, thread exits, post-build catches it.
  - Install timeout (600s) → install_error set.
  - package.json malformed (LLM emitted partial JSON before fix-up) → npm
    install crashes with non-zero exit; install_error captures stderr.

Thread-safety:
  - install_done is a threading.Event — safe to .set() once and .wait() from
    multiple threads.
  - install_error is set BEFORE install_done.set(); readers must check
    install_done first, then install_error.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional

from pebble.log import log


def _win_no_window_kwargs() -> dict:
    """Windows-only subprocess kwargs that suppress the console window.

    npm resolves to npm.cmd (a batch file), so spawning it routes through
    cmd.exe — which flashes a console window unless explicitly suppressed.
    Both the warmup npm install and the detached next dev would otherwise
    pop a window EVERY time a preview warms up (and repeatedly, since the
    workspace iframe re-polls every 2s while a preview isn't ready). Plain
    DETACHED_PROCESS did not suppress it for the cmd.exe→node chain;
    CREATE_NO_WINDOW + a hidden STARTUPINFO does. No-op off Windows.
    """
    if sys.platform != "win32":
        return {}
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    return {
        "creationflags": subprocess.CREATE_NO_WINDOW,
        "startupinfo": startupinfo,
    }


class PreviewWarmup:
    """Orchestrate `npm install` in the background, in parallel with the
    LLM stream that's writing the project files. One instance per build."""

    __slots__ = (
        "site_dir",
        "_install_thread",
        "install_done",
        "install_error",
        "_started_at",
        "_elapsed_seconds",
    )

    def __init__(self, site_dir: Path):
        self.site_dir = site_dir
        self._install_thread: Optional[threading.Thread] = None
        self.install_done = threading.Event()
        self.install_error: Optional[str] = None
        self._started_at: Optional[float] = None
        self._elapsed_seconds: Optional[float] = None

    @property
    def started(self) -> bool:
        return self._install_thread is not None

    @property
    def elapsed_seconds(self) -> Optional[float]:
        """How long install took (or has been running). None if never started."""
        if self._started_at is None:
            return None
        if self._elapsed_seconds is not None:
            return self._elapsed_seconds
        import time as _t
        return _t.time() - self._started_at

    def start_install(self) -> None:
        """Kick off npm install. Idempotent — safe to call multiple times
        (only the first call starts the thread)."""
        if self._install_thread is not None:
            return
        if not (self.site_dir / "package.json").exists():
            # Defensive: caller should check first, but if package.json
            # isn't there yet just no-op (caller retries next chunk).
            return

        import time as _t
        self._started_at = _t.time()
        self._install_thread = threading.Thread(
            target=self._run_install, daemon=True, name=f"npm-install-{self.site_dir.name}",
        )
        self._install_thread.start()
        log.info("[warmup] npm install kicked off in background for %s", self.site_dir.name)

    def _run_install(self) -> None:
        """Body of the background thread. Sets install_done at the end no
        matter what — readers can always rely on the event firing."""
        import time as _t
        try:
            npm = shutil.which("npm") or shutil.which("npm.cmd")
            if not npm:
                self.install_error = "npm not found in PATH; install Node.js"
                log.warning("[warmup] %s", self.install_error)
                return

            try:
                subprocess.run(
                    [npm, "install", "--no-audit", "--no-fund", "--loglevel=error"],
                    cwd=str(self.site_dir),
                    check=True,
                    timeout=600,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    **_win_no_window_kwargs(),
                )
                self._elapsed_seconds = _t.time() - (self._started_at or _t.time())
                log.info("[warmup] npm install completed in %.1fs for %s",
                         self._elapsed_seconds, self.site_dir.name)
            except subprocess.CalledProcessError as exc:
                stderr_text = exc.stderr.decode("utf-8", "ignore") if exc.stderr else ""
                self.install_error = f"npm install failed: {stderr_text[:500]}"
                log.warning("[warmup] %s", self.install_error)
            except subprocess.TimeoutExpired:
                self.install_error = "npm install timed out after 600s"
                log.warning("[warmup] %s", self.install_error)
        finally:
            self.install_done.set()

    def wait_for_install(self, timeout: float = 600.0) -> bool:
        """Block until install finishes or `timeout` seconds elapse.
        Returns True on success, False if install failed or timed out.

        Safe to call even when start_install() was never called — returns
        False immediately in that case."""
        if self._install_thread is None:
            return False
        ok = self.install_done.wait(timeout=timeout)
        if not ok:
            # Event never fired — install is hung.
            return False
        return self.install_error is None


def start_next_dev_after_install(
    site_dir: Path,
    warmup: PreviewWarmup,
    install_wait_timeout: float = 600.0,
    server_poll_timeout: int = 60,
) -> dict:
    """Replacement for `post_build_run_dev_server` when a PreviewWarmup
    instance is available. Waits for the warmup's install to finish (it
    usually already has by the time the LLM stream completes), then starts
    next dev on a free port and polls until it responds.

    Returns {"port": int, "pid": int, "url": str, "errors": [str],
             "install_seconds": float | None}.
    """
    import socket
    import time
    import urllib.request

    result: dict = {
        "port": None, "pid": None, "url": None,
        "errors": [], "install_seconds": warmup.elapsed_seconds,
    }

    if not site_dir.exists() or not (site_dir / "package.json").exists():
        result["errors"].append("no package.json in site_dir; skip dev server")
        return result

    # Wait for the warmup install to finish (or fail)
    install_ok = warmup.wait_for_install(timeout=install_wait_timeout)
    result["install_seconds"] = warmup.elapsed_seconds
    if not install_ok:
        err = warmup.install_error or "npm install did not complete"
        result["errors"].append(err)
        return result

    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm:
        result["errors"].append("npm not found in PATH; install Node.js")
        return result

    # Find a free port for next dev
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    log.info("[warmup] starting next dev on port %d (install was %.1fs)",
             port, warmup.elapsed_seconds or 0)

    try:
        dev_kwargs = _win_no_window_kwargs()
        if sys.platform == "win32":
            # CREATE_NO_WINDOW suppresses the console; CREATE_NEW_PROCESS_GROUP
            # detaches the dev server from the engine's Ctrl+C.
            dev_kwargs["creationflags"] = (
                subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
            )
        proc = subprocess.Popen(
            [npm, "run", "dev", "--", "-p", str(port)],
            cwd=str(site_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **dev_kwargs,
        )
    except Exception as exc:
        result["errors"].append(f"failed to start dev server: {exc}")
        return result

    # Poll until server responds
    deadline = time.time() + server_poll_timeout
    server_up = False
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if 200 <= r.status < 500:
                    server_up = True
                    break
        except Exception:
            time.sleep(1.0)
    if not server_up:
        result["errors"].append(f"dev server did not respond within {server_poll_timeout}s")
        try:
            proc.terminate()
        except Exception:
            pass
        return result

    result["port"] = port
    result["pid"] = proc.pid
    result["url"] = url
    return result


__all__ = ["PreviewWarmup", "start_next_dev_after_install"]
