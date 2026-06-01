"""Build the 15 gallery template sites from workflow-drafted briefs.

Reads briefs from _template_briefs.json (written after the workflow returns),
runs each through the REAL build_v2_core, and reports per-site results:
slug, block count, leak check, name. One real Sonnet call per brief (~$0.07).
"""
import json
import os
from pathlib import Path

# Load .env so PEXELS + ANTHROPIC keys are present. The real .env lives in the
# MAIN repo root (it's gitignored, so worktrees don't have a copy). Search a few
# candidate locations and FORCE-override os.environ — a pre-exported empty key in
# the shell would otherwise defeat setdefault().
_ENV_CANDIDATES = [
    Path(".env"),
    Path(__file__).resolve().parent / ".env",
    Path(r"C:\Users\marci\pebble-engine\.env"),
]
for envf in _ENV_CANDIDATES:
    if envf.exists():
        for line in envf.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                v = v.strip().strip('"').strip("'")
                if v:  # only override with a non-empty value
                    os.environ[k.strip()] = v
        print(f"loaded env from {envf}")
        break

from pebble.server.build_v2 import build_v2_core, BuildV2Error
from pebble.pexels_resolver import resolve_pexels_tags

briefs = json.loads(Path("_template_briefs.json").read_text(encoding="utf-8"))
results = []
for i, b in enumerate(briefs, 1):
    brief = {
        "business_name": b["business_name"],
        "industry": b["industry"],
        "extra_context": b["extra_context"],
        "_template": True,           # mark as a gallery template
        "_vibe": b.get("_vibe", ""),
    }
    try:
        res = build_v2_core(brief)
        slug = res["slug"]
        # resolve Pexels across section files (build_v2_core's HTTP path does this;
        # the core itself leaves [pexels:] tags for the endpoint, so do it here)
        site = Path(res["saved_to"]) / "site"
        secs = sorted((site / "components" / "sections").glob("*.tsx"))
        for s in secs:
            s.write_text(resolve_pexels_tags(s.read_text(encoding="utf-8")), encoding="utf-8")
        leaks = [s.name for s in secs if "{{" in s.read_text(encoding="utf-8")]
        results.append({
            "n": i, "vibe": b.get("_vibe"), "industry": b["industry"],
            "name": b["business_name"], "slug": slug,
            "sections": len(secs), "files": res["file_count"],
            "leaks": leaks, "ok": not leaks,
        })
        print(f"[{i:2}/15] {b['_vibe']:20} {b['business_name']:24} -> {slug} ({len(secs)} sections){' LEAKS!' if leaks else ''}")
    except BuildV2Error as e:
        results.append({"n": i, "industry": b["industry"], "name": b["business_name"], "error": e.message, "ok": False})
        print(f"[{i:2}/15] {b['industry']:20} FAILED: {e.message}")
    except Exception as e:
        results.append({"n": i, "industry": b["industry"], "name": b["business_name"], "error": str(e), "ok": False})
        print(f"[{i:2}/15] {b['industry']:20} ERROR: {e}")

Path("_template_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
okc = sum(1 for r in results if r.get("ok"))
print(f"\n=== {okc}/{len(results)} templates built clean ===")
