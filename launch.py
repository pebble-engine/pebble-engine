#!/usr/bin/env python3
"""
Pebble Engine — launcher
────────────────────────
Run this file to start the program. It handles everything:

  • Starts the local server
  • Waits until it's ready
  • Opens the UI in a clean browser window

You should never need to run pebble_engine.py directly.
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
PORT = 8000
URL  = f"http://localhost:{PORT}"

# ── Dependency check ──────────────────────────────────────────────────────────

def check_python():
    if sys.version_info < (3, 8):
        print("✗ Pebble Engine needs Python 3.8 or later.")
        print(f"  You have Python {sys.version}")
        print("  Download the latest version from python.org")
        sys.exit(1)


def check_and_install_deps():
    """Install optional deps if they're listed in requirements.txt but missing."""
    req = ROOT / "requirements.txt"
    if not req.exists():
        return
    missing = []
    for line in req.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Extract package name (without version spec)
        pkg = line.split(">=")[0].split("==")[0].split("[")[0].strip()
        # Normalize: google-genai → google.genai
        import_name = pkg.replace("-", "_").lower()
        # Special cases
        if import_name == "google_genai":
            import_name = "google.genai"
        try:
            __import__(import_name.split(".")[0])
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"  Installing optional packages: {', '.join(missing)}")
        subprocess.run(
            [sys.executable, "-m", "pip", "install"] + missing + ["--break-system-packages", "-q"],
            check=False
        )


# ── Server startup ────────────────────────────────────────────────────────────

def start_server():
    """Import and run the server in a background thread."""
    # Add project root to path so pebble_engine is importable
    sys.path.insert(0, str(ROOT))
    from pebble_engine import serve  # type: ignore
    serve(port=PORT, open_browser=False)


def wait_for_server(timeout=15):
    """Block until the server responds or timeout."""
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(URL, timeout=1)
            return True
        except Exception:
            time.sleep(0.2)
    return False


# ── Browser open ─────────────────────────────────────────────────────────────

def open_browser():
    """Try to open in app mode (no address bar) — falls back to normal browser."""
    # macOS: try Chrome app mode first, then Safari, then default
    if sys.platform == "darwin":
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ]
        for chrome in chrome_paths:
            if Path(chrome).exists():
                subprocess.Popen([chrome, f"--app={URL}", "--window-size=1280,850"])
                return

    # Windows: try Chrome/Edge app mode
    elif sys.platform == "win32":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        for chrome in chrome_paths:
            if Path(chrome).exists():
                subprocess.Popen([chrome, f"--app={URL}", "--window-size=1280,850"])
                return

    # Linux: try chromium or google-chrome
    elif sys.platform.startswith("linux"):
        for cmd in ["google-chrome", "chromium", "chromium-browser", "brave-browser"]:
            try:
                subprocess.Popen([cmd, f"--app={URL}", "--window-size=1280,850"])
                return
            except FileNotFoundError:
                continue

    # Final fallback: default browser (shows address bar)
    webbrowser.open(URL)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    check_python()

    print()
    print("  ─────────────────────────────────────────")
    print("   Pebble Engine")
    print("  ─────────────────────────────────────────")
    print("  Starting up… ")
    print()

    # Install any missing optional deps
    check_and_install_deps()

    # Start the server in a daemon thread (dies when this script dies)
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()

    # Wait for server to be ready
    print("  Waiting for server…")
    ready = wait_for_server(timeout=20)
    if not ready:
        print("  ✗ Server didn't start within 20 seconds.")
        print(f"    Try opening {URL} manually in your browser.")
        input("  Press Enter to exit.")
        sys.exit(1)

    print(f"  ✓ Running at {URL}")
    print("  Opening Pebble Engine…")
    print()
    print("  ─────────────────────────────────────────")
    print("  Close this window to stop the program.")
    print("  ─────────────────────────────────────────")

    open_browser()

    # Keep main thread alive (the server thread is daemon, we need this)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Stopped.")


if __name__ == "__main__":
    main()
