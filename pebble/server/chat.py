"""Pebble assistant chat — POST /api/chat (2026-05-23).

A multi-turn conversation endpoint that powers the dashboard's
Control Center side-panel. Differs from /api/bot-message in three
ways:

  1. Multi-turn — accepts the full conversation history per call.
     Client-side history (sessionStorage / React state) keeps the
     server stateless and the per-user privacy story simple.
  2. Structured response — returns JSON with optional `navigate_to`
     and `confirm_action` fields so the frontend can act on the
     model's intent (router.push, open a billing portal, etc.) rather
     than relying on text parsing.
  3. Route-aware system prompt — the frontend passes the sitemap of
     authed routes so the model only suggests destinations that
     actually exist in this Pebble build.

Model: openai/gpt-4o-mini via OpenRouter. ~$0.0002 per turn.
"""
from __future__ import annotations

import json
import os
from typing import Any

from pebble.log import log
from pebble.security import client_ip, plan_limiter, resolve_user_id


# Hardcoded model — Phase 28 will route intent-based but for now the
# assistant is always cheap-and-fast.
CHAT_MODEL = "openai/gpt-4o-mini"
CHAT_MAX_TOKENS = 600
CHAT_MAX_HISTORY = 24   # turns kept from client; rest dropped
CHAT_MAX_BODY = 64 * 1024


# Sitemap baked in so the model never invents a route. Frontend can
# override per-call but this is the safe default.
DEFAULT_SITEMAP: list[dict[str, str]] = [
    {"path": "/dashboard",                "label": "Dashboard"},
    {"path": "/designs",                  "label": "My designs"},
    {"path": "/templates",                "label": "Templates"},
    {"path": "/integrations",             "label": "Integrations"},
    {"path": "/community",                "label": "Community"},
    {"path": "/community/launchpad",      "label": "Community: Launchpad"},
    {"path": "/community/hire-a-partner", "label": "Community: Hire a partner"},
    {"path": "/community/affiliate",      "label": "Community: Affiliate program"},
    {"path": "/settings",                 "label": "Account settings"},
    {"path": "/pricing",                  "label": "Pricing"},
    {"path": "/trust",                    "label": "Trust Charter"},
]


# Destructive intents the model can SUGGEST but never auto-execute.
# Returned in `confirm_action` so the UI can show a "Are you sure?"
# step before doing anything irreversible.
CONFIRM_ACTIONS: dict[str, dict[str, str]] = {
    "open_billing_portal": {
        "label":  "Open billing portal",
        "intent": "User wants to manage their subscription, change plan, update payment method, or cancel.",
    },
    "delete_account": {
        "label":  "Delete account",
        "intent": "User wants to permanently delete their account and all projects.",
    },
}


def _build_system(sitemap: list[dict[str, str]]) -> str:
    routes_list = "\n".join(f"  - {r['path']} — {r['label']}" for r in sitemap)
    confirm_list = "\n".join(
        f"  - {k}: {v['intent']}" for k, v in CONFIRM_ACTIONS.items()
    )
    return (
        "You are Pebble, the warm AI assistant inside the Pebble website-"
        "building app. You help users navigate, answer questions about the "
        "app, and act on their requests. You are friendly, brief, and "
        "concrete.\n\n"

        "OUTPUT FORMAT — strict JSON, no markdown fences, no prose around "
        "the JSON. Every reply MUST be a single JSON object with this "
        "shape:\n"
        "{\n"
        '  "reply": "<your short 1-3 sentence response shown to the user>",\n'
        '  "navigate_to": "<path or null>",\n'
        '  "confirm_action": "<action key or null>"\n'
        "}\n\n"

        "WHEN THE USER ASKS TO GO SOMEWHERE: set `navigate_to` to one of "
        "these exact paths and ONLY these paths — never invent a new one:\n"
        f"{routes_list}\n\n"

        "WHEN THE USER ASKS FOR A DESTRUCTIVE ACTION (cancel, delete, "
        "remove billing, etc.): set `confirm_action` to one of these "
        "exact keys and ALSO set `navigate_to` to the relevant page if "
        "applicable. The frontend will show a confirmation prompt — never "
        "claim you already performed the action.\n"
        f"{confirm_list}\n\n"

        "STYLE:\n"
        "  - Default reply length: under 40 words. Aim for under 20.\n"
        "  - Conversational, not corporate. No exclamation points.\n"
        "  - Don't promise specific times or invent features.\n"
        "  - If the user just chats, set navigate_to and confirm_action "
        "to null and answer warmly.\n"
        "  - If the user is on the dashboard and asks 'what can I do', "
        "suggest one specific next step (Templates, build a site, etc.)."
    )


def _extract_json_object(raw: str) -> dict[str, Any] | None:
    """LLMs sometimes wrap JSON in markdown fences or trailing prose.
    Pull the first {...} that parses cleanly."""
    import re
    if not raw:
        return None
    # Try the whole string first — happy path for compliant models.
    try:
        parsed = json.loads(raw.strip())
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    # Fall back to the first balanced {...} block.
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return None
    try:
        parsed = json.loads(m.group(0))
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    return None


def _safe_navigate(target: Any, sitemap: list[dict[str, str]]) -> str | None:
    """Only allow navigation to paths in the sitemap. Anything else is
    dropped silently — never trust the LLM to invent a route."""
    if not isinstance(target, str) or not target.startswith("/"):
        return None
    allowed = {r["path"] for r in sitemap}
    return target if target in allowed else None


def _safe_confirm(action: Any) -> str | None:
    if isinstance(action, str) and action in CONFIRM_ACTIONS:
        return action
    return None


def run_chat(handler) -> None:
    """POST /api/chat
    Body: {
      messages: [{role: "user"|"assistant", content: str}, ...],
      sitemap?: [{path, label}, ...],   // optional override
    }
    Returns: {
      reply: str,
      navigate_to: str | null,
      confirm_action: { key: str, label: str } | null,
      fallback?: bool,
    }
    """
    # Auth-gate. Chat is an authed-only feature — no anonymous LLM
    # spend, no per-IP rate limit gaming.
    uid = resolve_user_id(handler)
    if not uid:
        handler._json(401, {"error": "sign in required"})
        return

    ip = client_ip(handler)
    if not plan_limiter.allow(ip or ""):
        handler._json(429, {"error": "slow down — too many chat messages"})
        return

    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return
    if length <= 0 or length > CHAT_MAX_BODY:
        handler._json(400, {"error": "missing or oversized body"}); return
    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return

    messages_in = body.get("messages") or []
    if not isinstance(messages_in, list) or not messages_in:
        handler._json(400, {"error": "messages must be a non-empty array"}); return

    # Validate + cap history. Drop anything past CHAT_MAX_HISTORY so a
    # runaway client can't blow up token spend.
    cleaned: list[dict[str, str]] = []
    for m in messages_in[-CHAT_MAX_HISTORY:]:
        if not isinstance(m, dict):
            continue
        role = (m.get("role") or "").strip()
        content = m.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str):
            continue
        c = content.strip()
        if not c:
            continue
        cleaned.append({"role": role, "content": c[:2000]})  # per-message cap
    if not cleaned or cleaned[-1]["role"] != "user":
        handler._json(400, {"error": "last message must be from user"}); return

    sitemap = body.get("sitemap")
    if not isinstance(sitemap, list) or not sitemap:
        sitemap = DEFAULT_SITEMAP
    else:
        # Filter to safe shape — any malformed entries are dropped.
        sitemap = [
            {"path": s["path"], "label": s.get("label") or s["path"]}
            for s in sitemap
            if isinstance(s, dict) and isinstance(s.get("path"), str) and s["path"].startswith("/")
        ] or DEFAULT_SITEMAP

    system = _build_system(sitemap)

    # Call OpenRouter directly so we can pass a full message array
    # (the existing OpenRouterClient.generate only takes system+user
    # strings; chat needs the history).
    try:
        import httpx
        api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")

        full_messages = [{"role": "system", "content": system}, *cleaned]
        resp = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
                "HTTP-Referer":  "https://pebbleapp.ai",
                "X-Title":       "Pebble Assistant Chat",
            },
            json={
                "model":       CHAT_MODEL,
                "messages":    full_messages,
                "max_tokens":  CHAT_MAX_TOKENS,
                "temperature": 0.6,
                # Force JSON output where the provider supports it. GPT-4o-mini
                # honors this strictly via OpenAI; OpenRouter passes it through.
                "response_format": {"type": "json_object"},
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"] or ""
    except Exception as e:
        log.warning("[chat] LLM call failed: %s", e)
        handler._json(200, {
            "reply":          "I'm having trouble reaching my brain right now — try again in a moment.",
            "navigate_to":    None,
            "confirm_action": None,
            "fallback":       True,
        })
        return

    parsed = _extract_json_object(raw)
    if not parsed:
        # Model returned non-JSON despite the strict instruction. Treat
        # the whole string as a plain reply and ship it.
        handler._json(200, {
            "reply":          (raw or "Sorry, I didn't catch that.").strip()[:600],
            "navigate_to":    None,
            "confirm_action": None,
        })
        return

    reply = (parsed.get("reply") or "").strip()[:600] or "Okay."
    nav = _safe_navigate(parsed.get("navigate_to"), sitemap)
    confirm_key = _safe_confirm(parsed.get("confirm_action"))
    confirm_obj = (
        {"key": confirm_key, "label": CONFIRM_ACTIONS[confirm_key]["label"]}
        if confirm_key else None
    )

    handler._json(200, {
        "reply":          reply,
        "navigate_to":    nav,
        "confirm_action": confirm_obj,
    })


__all__ = ["run_chat", "CHAT_MODEL", "DEFAULT_SITEMAP", "CONFIRM_ACTIONS"]
