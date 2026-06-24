"""One-off: enable beta invite-only mode on Railway prod. Do not commit secrets."""
from __future__ import annotations

import sys
from pathlib import Path

# Reuse Railway helpers from preview fix script
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _railway_fix_preview_once import find_project, load_env, upsert_var  # noqa: E402

PROJECT_NAME = "magnificent-simplicity"
SERVICE_NAME = "web"
DEFAULT_CODES = "beta01,beta02,beta03,beta04,beta05,beta06,beta07,beta08,beta09,beta10"


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    env = load_env(root / ".env")
    token = env.get("RAILWAY_TOKEN", "").strip()
    if not token:
        print("RAILWAY_TOKEN missing from .env")
        return 1

    codes = env.get("PEBBLE_BETA_INVITE_CODES", DEFAULT_CODES).strip() or DEFAULT_CODES
    print(f"Looking up Railway project {PROJECT_NAME!r} …")
    project_id, env_id, service_id = find_project(token)
    upsert_var(token, project_id, env_id, service_id, "PEBBLE_BETA_INVITE_ONLY", "true")
    upsert_var(token, project_id, env_id, service_id, "PEBBLE_BETA_INVITE_CODES", codes)
    print("\nBeta invite env set. After redeploy (~2 min):")
    print("  curl -s https://www.pebbleapp.ai/api/health | grep beta_invite_only")
    print("\nSignup links: docs/BETA_RECRUIT.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
