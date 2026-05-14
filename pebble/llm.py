"""LLM client wrappers and provider selection.

Provides a uniform `.generate(system, user, max_tokens, images) -> str`
interface across providers so the engine swaps Gemini and Anthropic
without callers caring.

Streaming is mandatory for Anthropic (prompts >10min would otherwise 400).
Gemini's non-streaming endpoint is fine at the prompt sizes we hit.
"""
from __future__ import annotations
import os
from typing import Optional


# ---- Optional provider SDKs (import-guarded so the engine still runs
#      if a user only installed one of them, or none). -----------------------

try:
    from anthropic import Anthropic  # type: ignore
    _ANTHROPIC_OK = True
except Exception:
    Anthropic = None  # type: ignore
    _ANTHROPIC_OK = False

try:
    from google import genai as _genai                # type: ignore
    from google.genai import types as _genai_types    # type: ignore
    _GOOGLE_OK = True
except Exception:
    _genai = None                                     # type: ignore
    _genai_types = None                               # type: ignore
    _GOOGLE_OK = False


# ---- Defaults -----------------------------------------------------------

# Pinned, not aliased. Aliases like `gemini-flash-latest` would silently
# upgrade across model deprecations and surprise the user. When Google
# retires this, we want the build to fail loudly so we update intentionally.
_GEMINI_DEFAULT_MODEL    = "gemini-2.5-flash"
_ANTHROPIC_DEFAULT_MODEL = "claude-sonnet-4-6"


# ---- Errors -------------------------------------------------------------

class LLMError(Exception):
    """Wraps any provider error so callers handle one exception type."""
    pass


# ---- Clients ------------------------------------------------------------

class GeminiClient:
    """Wraps google-genai. Same `generate()` shape as AnthropicClient."""

    def __init__(self, api_key: str, model: str):
        if not _GOOGLE_OK:
            raise LLMError("google-genai package not installed. Run: pip install google-genai")
        self.client = _genai.Client(api_key=api_key)
        self.model = model
        self.provider = "gemini"

    def generate(self, system: str, user: str, max_tokens: int = 16000,
                 images: Optional[list[dict]] = None) -> str:
        try:
            config = _genai_types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=max_tokens,
                temperature=0.7,
            )
            if images:
                import base64 as _b64
                parts: list = [user]
                for img in images:
                    raw = img.get("data", "")
                    if not raw:
                        continue
                    try:
                        img_bytes = _b64.b64decode(raw)
                    except Exception:
                        continue
                    parts.append(_genai_types.Part.from_bytes(
                        data=img_bytes,
                        mime_type=img.get("media_type", "image/png"),
                    ))
                contents = parts
            else:
                contents = user
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )
            return response.text
        except Exception as e:
            raise LLMError(f"Gemini API call failed: {e}")


class AnthropicClient:
    """Wraps anthropic. Same `generate()` shape as GeminiClient."""

    def __init__(self, api_key: str, model: str):
        if not _ANTHROPIC_OK:
            raise LLMError("anthropic package not installed. Run: pip install anthropic")
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.provider = "anthropic"

    def generate(self, system: str, user: str, max_tokens: int = 16000,
                 images: Optional[list[dict]] = None) -> str:
        try:
            if images:
                content_blocks: list = []
                for img in images:
                    raw = img.get("data", "")
                    if not raw:
                        continue
                    content_blocks.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": img.get("media_type", "image/png"),
                            "data": raw,
                        },
                    })
                content_blocks.append({"type": "text", "text": user})
                messages = [{"role": "user", "content": content_blocks}]
            else:
                messages = [{"role": "user", "content": user}]

            # Streaming is required for requests that could exceed 10 minutes —
            # our prompt + 32k max_tokens trips that threshold. We collect the
            # stream into a single string so the caller still sees a sync return.
            parts: list[str] = []
            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            ) as stream:
                for chunk in stream.text_stream:
                    parts.append(chunk)
            return "".join(parts)
        except Exception as e:
            raise LLMError(f"Anthropic API call failed: {e}")


# ---- Provider selector --------------------------------------------------

def get_llm_client() -> tuple[Optional[object], str]:
    """Return (client, reason). Client is None if unavailable; reason explains why.

    Provider priority:
        PEBBLE_PROVIDER=gemini     -> GeminiClient (default if key present)
        PEBBLE_PROVIDER=anthropic  -> AnthropicClient
        (unset)                    -> try Gemini first, fall back to Anthropic
    """
    provider = os.environ.get("PEBBLE_PROVIDER", "").strip().lower()

    # -- Explicit Anthropic request --
    if provider == "anthropic":
        if not _ANTHROPIC_OK:
            return None, "anthropic package not installed (run: pip install anthropic)"
        key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not key:
            return None, "ANTHROPIC_API_KEY not set (PEBBLE_PROVIDER=anthropic)"
        model = os.environ.get("PEBBLE_MODEL", _ANTHROPIC_DEFAULT_MODEL).strip() or _ANTHROPIC_DEFAULT_MODEL
        try:
            return AnthropicClient(api_key=key, model=model), "ok"
        except LLMError as e:
            return None, str(e)

    # -- Gemini (explicit or default) --
    gemini_key = os.environ.get("GOOGLE_API_KEY", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()
    if gemini_key and _GOOGLE_OK:
        model = os.environ.get("PEBBLE_MODEL", _GEMINI_DEFAULT_MODEL).strip() or _GEMINI_DEFAULT_MODEL
        try:
            return GeminiClient(api_key=gemini_key, model=model), "ok"
        except LLMError as e:
            return None, str(e)

    # -- Fall back to Anthropic if Gemini key isn't set --
    if provider != "gemini":
        if _ANTHROPIC_OK:
            key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
            if key:
                model = os.environ.get("PEBBLE_MODEL", _ANTHROPIC_DEFAULT_MODEL).strip() or _ANTHROPIC_DEFAULT_MODEL
                try:
                    return AnthropicClient(api_key=key, model=model), "ok"
                except LLMError as e:
                    return None, str(e)

    # -- Nothing configured --
    if not _GOOGLE_OK and not _ANTHROPIC_OK:
        return None, "no LLM package installed (run: pip install -r requirements.txt)"
    if not gemini_key:
        return None, "GOOGLE_API_KEY not set -- add it to .env (or set PEBBLE_PROVIDER=anthropic)"
    return None, "LLM not configured"


__all__ = [
    "LLMError",
    "GeminiClient",
    "AnthropicClient",
    "get_llm_client",
    "_ANTHROPIC_OK",
    "_GOOGLE_OK",
    "_GEMINI_DEFAULT_MODEL",
    "_ANTHROPIC_DEFAULT_MODEL",
]
