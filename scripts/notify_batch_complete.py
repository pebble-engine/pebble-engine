#!/usr/bin/env python3
"""Post batch-complete summary to Telegram via Hermes env vars.

Usage:
  python scripts/notify_batch_complete.py "Batch C shipped" "pytest green"
  python scripts/notify_batch_complete.py --handoff HANDOFF_BATCH_C_2026-06-12.md

Requires in .env:
  TELEGRAM_BOT_TOKEN
  TELEGRAM_ALLOWED_CHAT_ID
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def send_telegram(text: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_ALLOWED_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN or TELEGRAM_ALLOWED_CHAT_ID not set — skip send")
        return False
    url = (
        f"https://api.telegram.org/bot{token}/sendMessage?"
        + urllib.parse.urlencode({"chat_id": chat_id, "text": text[:4000]})
    )
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status == 200


def main() -> int:
    _load_dotenv()
    parser = argparse.ArgumentParser(description="Telegram batch notification")
    parser.add_argument("title", nargs="?", default="Pebble batch update")
    parser.add_argument("body", nargs="?", default="")
    parser.add_argument("--handoff", help="Append first 500 chars of handoff file")
    args = parser.parse_args()

    parts = [f"✅ {args.title}"]
    if args.body:
        parts.append(args.body)
    if args.handoff:
        p = ROOT / args.handoff
        if p.exists():
            parts.append(p.read_text(encoding="utf-8")[:500])
    msg = "\n\n".join(parts)

    if send_telegram(msg):
        print("Telegram sent.")
        return 0
    print("Telegram not sent (missing config or API error).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
