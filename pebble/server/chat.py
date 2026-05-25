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
import re
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


# Edit operations the model can dispatch via `dispatch_op`.
# Maps op name → required params + description for the system prompt.
# NEVER include ops that modify auth, billing, or project ownership.
DISPATCH_OPS: dict[str, dict] = {
    "font-family": {
        "description": "Change a font family on an element or globally",
        "required_params": ["new_font_family"],
        "optional_params": ["selector_hint"],
    },
    "color": {
        "description": "Change a specific element's color",
        "required_params": ["new_color"],
        "optional_params": ["selector_hint", "original_text"],
    },
    "font-size": {
        "description": "Make text bigger (delta: 1) or smaller (delta: -1)",
        "required_params": ["delta"],
        "optional_params": ["selector_hint"],
    },
    "palette-swap": {
        "description": "Change the overall brand color scheme via CSS variables",
        "required_params": [],
        "optional_params": ["primary", "secondary", "accent", "background", "foreground"],
    },
    "image-swap": {
        "description": "Replace a specific image with a new URL",
        "required_params": ["original_src", "new_src"],
        "optional_params": [],
    },
}

_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _safe_dispatch(raw: object, current_slug: str | None) -> dict | None:
    """Validate and normalise a `dispatch_op` object from the LLM.

    Security rules:
      - `op` must be in DISPATCH_OPS allowlist
      - `current_slug` must be provided by the server (never trust the LLM's slug)
      - Unknown params are stripped; only allowlisted param keys pass through
      - Returns None for any invalid input

    The returned dict is ready to pass directly to the frontend as
    ``dispatch_op`` in the chat response.
    """
    if not isinstance(raw, dict) or not current_slug:
        return None

    op = raw.get("op")
    if not isinstance(op, str) or op not in DISPATCH_OPS:
        return None

    params_raw = raw.get("params") or {}
    if not isinstance(params_raw, dict):
        return None

    spec = DISPATCH_OPS[op]
    allowed_keys = set(spec["required_params"]) | set(spec["optional_params"])

    # Strip anything the LLM added that isn't in the spec — prevents
    # prompt-injection attacks from sneaking extra fields through.
    clean_params: dict = {k: v for k, v in params_raw.items() if k in allowed_keys}

    # Validate required params are present and non-empty.
    for req in spec["required_params"]:
        if req not in clean_params or not clean_params[req]:
            return None  # LLM didn't provide enough info — don't dispatch

    # palette-swap: validate hex values, wrap into "palette" key that
    # matches what _edit_palette_swap expects on the backend.
    if op == "palette-swap":
        palette: dict = {}
        for color_key in ["primary", "secondary", "accent", "background", "foreground"]:
            val = clean_params.get(color_key)
            if val and isinstance(val, str) and _HEX_RE.match(val):
                palette[color_key] = val
        if not palette:
            return None  # no valid colors — decline
        clean_params = {"palette": palette}

    # The slug always comes from the server, never from the LLM output.
    clean_params["slug"] = current_slug

    return {"op": op, "params": clean_params}


def _build_system(
    sitemap: list[dict[str, str]],
    project_context: dict | None = None,
) -> str:
    routes_list = "\n".join(f"  - {r['path']} — {r['label']}" for r in sitemap)
    confirm_list = "\n".join(
        f"  - {k}: {v['intent']}" for k, v in CONFIRM_ACTIONS.items()
    )
    dispatch_list = "\n".join(
        f'  - "{k}": {v["description"]}' for k, v in DISPATCH_OPS.items()
    )

    ctx_block = ""
    if project_context and isinstance(project_context, dict):
        name     = project_context.get("name", "")
        industry = project_context.get("industry", "")
        dna      = project_context.get("design_dna", "")
        published = project_context.get("is_published", False)
        ctx_lines = [f"  - Project name: {name}"] if name else []
        if industry: ctx_lines.append(f"  - Industry: {industry}")
        if dna:      ctx_lines.append(f"  - Design style: {dna.replace('_', ' ')}")
        ctx_lines.append(f"  - Published: {'yes' if published else 'no'}")
        if ctx_lines:
            ctx_block = (
                "\nPROJECT CONTEXT (the user's current project — use this to "
                "give specific, relevant answers):\n"
                + "\n".join(ctx_lines)
                + "\n"
            )

    return (
        "You are Pebble, the warm AI assistant inside the Pebble website-"
        "building app. You help users navigate, answer questions about the "
        "app, and act on their requests. You are friendly, brief, and "
        "concrete.\n"
        + ctx_block
        + "\nOUTPUT FORMAT — strict JSON, no markdown fences, no prose around "
        "the JSON. Every reply MUST be a single JSON object with this "
        "shape:\n"
        "{\n"
        '  "reply": "<your short 1-3 sentence response shown to the user>",\n'
        '  "navigate_to": "<path or null>",\n'
        '  "confirm_action": "<action key or null>",\n'
        '  "dispatch_op": {"op": "<op>", "params": {...}} or null\n'
        "}\n\n"

        "WHEN THE USER ASKS TO GO SOMEWHERE: set `navigate_to` to one of "
        "these exact paths and ONLY these paths — never invent a new one:\n"
        f"{routes_list}\n\n"

        "WHEN THE USER ASKS FOR A DESTRUCTIVE ACTION (cancel, delete, "
        "remove billing, etc.): set `confirm_action` to one of these "
        "exact keys. The frontend will confirm — never claim you already "
        "performed the action.\n"
        f"{confirm_list}\n\n"

        "WHEN THE USER ASKS TO CHANGE SOMETHING ON THEIR SITE (font, color, "
        "image, brand colors): set `dispatch_op` with one of these ops. "
        "Only set it when you have enough information to fill ALL required "
        "params. If you're missing info (e.g. no new image URL), ask the "
        "user instead.\n"
        f"{dispatch_list}\n\n"
        "dispatch_op param rules:\n"
        '  - font-family: {"new_font_family": "Font Name", "selector_hint": "optional"}\n'
        '  - color: {"new_color": "#RRGGBB", "selector_hint": "optional"}\n'
        '  - font-size: {"delta": 1} for bigger, {"delta": -1} for smaller\n'
        '  - palette-swap: {"primary": "#hex", "secondary": "#hex"} — only include colors mentioned\n'
        '  - image-swap: {"original_src": "<exact old URL>", "new_src": "<new URL>"}\n'
        "IMPORTANT: Never invent image URLs. Ask the user to paste the URL.\n\n"

        "STYLE:\n"
        "  - Default reply length: under 40 words. Aim for under 20.\n"
        "  - Conversational, not corporate. No exclamation points.\n"
        "  - Don't promise specific times or invent features.\n"
        "  - If the user just chats, set navigate_to, confirm_action, and "
        "dispatch_op to null and answer warmly.\n"
        "  - If the user is on the dashboard and asks 'what can I do', "
        "suggest one specific next step (Templates, build a site, etc.)."
    )


def _extract_json_object(raw: str) -> dict[str, Any] | None:
    """LLMs sometimes wrap JSON in markdown fences or trailing prose.
    Pull the first {...} that parses cleanly."""
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

    # Optional project context — passed from the frontend dashboard when
    # the user has projects loaded. Keeps the server stateless: we don't
    # fetch project data here, we trust what the authenticated frontend sends.
    project_context_raw = body.get("project_context")
    project_context: dict | None = (
        project_context_raw
        if isinstance(project_context_raw, dict)
        else None
    )
    # current_slug: the project the user is currently working on. Used to
    # scope dispatch_op edits. NEVER let the LLM supply the slug — only
    # the authenticated request can set it.
    current_slug_raw = body.get("current_slug")
    current_slug: str | None = (
        current_slug_raw.strip()
        if isinstance(current_slug_raw, str) and current_slug_raw.strip()
        else None
    )

    system = _build_system(sitemap, project_context=project_context)

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
    dispatch_obj = _safe_dispatch(parsed.get("dispatch_op"), current_slug)

    handler._json(200, {
        "reply":          reply,
        "navigate_to":    nav,
        "confirm_action": confirm_obj,
        "dispatch_op":    dispatch_obj,
    })


__all__ = ["run_chat", "CHAT_MODEL", "DEFAULT_SITEMAP", "CONFIRM_ACTIONS", "DISPATCH_OPS"]
