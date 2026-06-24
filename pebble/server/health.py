"""GET /api/health — engine + LLM + preview diagnostics."""
from __future__ import annotations

import os

from pebble.llm import get_llm_client


def run_health(handler) -> None:
    """Return engine readiness, provider, preview backend flags."""
    import pebble_engine as pe

    client, reason = get_llm_client()
    provider = getattr(client, "provider", None) if client else None
    model = getattr(client, "model", None) if client else None
    preview_backend = os.environ.get("PEBBLE_PREVIEW_BACKEND", "local").strip().lower()
    try:
        from pebble.vercel_deploy import vercel_configured as _vercel_configured
        vercel_ok = _vercel_configured()
    except Exception:
        vercel_ok = bool(os.environ.get("VERCEL_TOKEN", "").strip())

    payload = {
        "engine_ok": pe._ENGINE_OK,
        "google_installed": pe._GOOGLE_OK,
        "anthropic_installed": pe._ANTHROPIC_OK,
        "google_key_set": bool(
            os.environ.get("GOOGLE_API_KEY", "").strip()
            or os.environ.get("GEMINI_API_KEY", "").strip()
        ),
        "anthropic_key_set": bool(os.environ.get("ANTHROPIC_API_KEY", "").strip()),
        "llm_ready": reason == "ok",
        "llm_reason": reason,
        "provider": provider,
        "model": model,
        "preview_backend": preview_backend,
        "vercel_configured": vercel_ok,
        "preview_prod_ready": preview_backend == "vercel" and vercel_ok,
    }
    try:
        from pebble.build_queue import stats as _bq_stats
        payload["build_queue"] = _bq_stats()
    except Exception:
        pass
    try:
        from pebble.beta_invite import is_enabled as _beta_on
        payload["beta_invite_only"] = _beta_on()
    except Exception:
        pass
    try:
        out = pe.OUTPUT_DIR
        writable = False
        project_count = 0
        if out.exists():
            try:
                probe = out / ".pebble_volume_probe"
                probe.write_text("ok", encoding="utf-8")
                writable = probe.read_text(encoding="utf-8") == "ok"
            except OSError:
                writable = False
            project_count = sum(
                1 for d in out.iterdir()
                if d.is_dir() and not d.name.startswith(".") and (d / "brief.json").exists()
            )
        payload["output_volume"] = {
            "path": str(out),
            "writable": writable,
            "project_count": project_count,
        }
    except Exception:
        pass
    handler._json(200, payload)


__all__ = ["run_health"]
