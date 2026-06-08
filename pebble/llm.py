"""LLM client wrappers and provider selection.

Provides a uniform `.generate(system, user, max_tokens, images) -> str`
interface across providers so the engine swaps Gemini and Anthropic
without callers caring.

Streaming is mandatory for Anthropic (prompts >10min would otherwise 400).
Gemini's non-streaming endpoint is fine at the prompt sizes we hit.

Prompt caching strategy (Anthropic only):
    The system prompt in this project is ~32k tokens and is static across
    builds (same PROMPT.md template rendered identically for each call).
    We pass it as a content block with cache_control={"type": "ephemeral"}
    so Anthropic caches the prefix after the first request.
    Cache hits are billed at ~10% of the normal input rate, reducing
    per-build costs by 70-80% on the system-prompt tokens.
    The streaming path uses the same block form — Anthropic requires the
    list form (not a bare string) to apply cache_control.
"""
from __future__ import annotations
import json
import os
import time
from typing import Iterator, Optional


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
_GEMINI_DEFAULT_MODEL     = "gemini-2.5-flash"
_ANTHROPIC_DEFAULT_MODEL  = "claude-sonnet-4-6"
# OpenRouter is the "many models behind one API" provider. Default to
# Qwen 3.6 Plus (Alibaba's April-2026 flagship "Plus" tier in the Qwen3.6
# series). 1M context window — fits Pebble's full prompt (seed brief +
# Layout DNA + Style DNA + research) without splitting. ~7-9x cheaper
# than Sonnet 4.6 on output, comparable instruction-following.
#
# Override via PEBBLE_MODEL=... to test alternatives:
#   qwen/qwen3.6-max-preview-20260420 → bigger but pricier ($1.04/$6.24)
#   qwen/qwen3.6-flash                → cheaper still ($0.19/$1.13), 1M ctx
#   qwen/qwen3.5-plus-20260420        → prior generation Plus
#   deepseek/deepseek-chat            → strong code, different vendor
_OPENROUTER_DEFAULT_MODEL = "qwen/qwen3.6-plus-04-02"


# ---- Errors -------------------------------------------------------------

class LLMError(Exception):
    """Wraps any provider error so callers handle one exception type."""
    pass


# ---- Transient-error retry --------------------------------------------------
# A streamed generate can take minutes; a single dropped TCP connection
# (WinError 10054 "connection forcibly closed", a reset proxy, a flaky link to
# the provider) used to kill an entire build with no recovery. We retry the
# WHOLE call on transient connection errors — partial stream output is
# discarded and we start fresh. The system prompt is cache_control'd, so a
# retry re-reads the cached prefix cheaply.
_MAX_LLM_ATTEMPTS = 3
_RETRY_BACKOFF_S = 1.5  # multiplied by attempt number; monkeypatched to 0 in tests

# Substrings that unambiguously signal a transient network/connection reset,
# used as a fallback when the SDK wraps the cause in a generic exception type.
_TRANSIENT_MARKERS = (
    "10054",
    "forcibly closed",
    "connection reset",
    "connection aborted",
    "peer closed",
    "incomplete",
    "remoteprotocol",
    "server disconnected",
    "connection error",
    "timed out",
    "temporarily unavailable",
    "overloaded",
    "502",
    "503",
    "529",
)


def _is_transient_conn_error(exc: Exception) -> bool:
    """True if *exc* (or anything in its cause/context chain) looks like a
    transient connection/network failure worth retrying. Deterministic errors
    (auth, 400 validation, model-not-found) return False so we fail fast."""
    seen: set[int] = set()
    e: Optional[BaseException] = exc
    while e is not None and id(e) not in seen:
        seen.add(id(e))
        # ConnectionResetError/ConnectionError/TimeoutError are all OSError
        # subclasses raised on socket-level resets.
        if isinstance(e, (ConnectionError, TimeoutError)):
            return True
        try:
            import httpx  # transitive dep of anthropic
            if isinstance(e, httpx.TransportError):
                return True
        except Exception:
            pass
        msg = str(e).lower()
        if any(m in msg for m in _TRANSIENT_MARKERS):
            return True
        e = e.__cause__ or e.__context__
    return False


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

            # Build the system param with prompt caching when a system prompt
            # is provided.  Passing system as a list of content blocks with
            # cache_control instructs Anthropic to cache the prefix, billing
            # subsequent cache hits at ~10% of the normal input token rate.
            # If system is empty/None we omit the param entirely to avoid an
            # API error (the SDK treats anthropic.NOT_GIVEN as "don't send").
            from anthropic import NOT_GIVEN  # local import keeps top-level clean
            if system:
                system_param = [{"type": "text", "text": system,
                                 "cache_control": {"type": "ephemeral"}}]
            else:
                system_param = NOT_GIVEN

            # Streaming is required for requests that could exceed 10 minutes —
            # our prompt + 32k max_tokens trips that threshold. We collect the
            # stream into a single string so the caller still sees a sync return.
            #
            # Retry the WHOLE stream on transient connection resets: a mid-stream
            # WinError 10054 / dropped link otherwise kills the entire build. We
            # discard any partial output and start over (the cached system prompt
            # keeps retries cheap). Deterministic errors (auth, 400) raise on the
            # first attempt — _is_transient_conn_error returns False for them.
            last_exc: Optional[Exception] = None
            for attempt in range(_MAX_LLM_ATTEMPTS):
                try:
                    parts: list[str] = []
                    with self.client.messages.stream(
                        model=self.model,
                        max_tokens=max_tokens,
                        system=system_param,
                        messages=messages,
                    ) as stream:
                        for chunk in stream.text_stream:
                            parts.append(chunk)
                    return "".join(parts)
                except Exception as e:  # noqa: BLE001 — classify then re-raise
                    last_exc = e
                    if attempt < _MAX_LLM_ATTEMPTS - 1 and _is_transient_conn_error(e):
                        try:
                            from pebble.log import log
                            log.warning(
                                "[llm] transient Anthropic error (attempt %d/%d), retrying: %s",
                                attempt + 1, _MAX_LLM_ATTEMPTS, e,
                            )
                        except Exception:
                            pass
                        time.sleep(_RETRY_BACKOFF_S * (attempt + 1))
                        continue
                    break
            raise LLMError(f"Anthropic API call failed: {last_exc}")
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"Anthropic API call failed: {e}")


class OpenRouterClient:
    """Wraps OpenRouter's OpenAI-compatible API. Routes to any model
    OpenRouter exposes (Qwen, DeepSeek, Llama, etc.) — one integration,
    many model choices.

    Talks HTTP via httpx (already a transitive dep of anthropic, no extra
    install). Non-streaming for simplicity; if Qwen outputs start hitting
    long-prompt timeouts we'll add streaming. OpenRouter's headers
    `HTTP-Referer` and `X-Title` are optional metadata fields they use
    for their model leaderboard — provided here for accurate attribution."""

    _BASE_URL = "https://openrouter.ai/api/v1"
    _PEBBLE_REFERER = "https://pebbleapp.ai"
    _PEBBLE_TITLE   = "Pebble Engine"

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise LLMError("OPENROUTER_API_KEY is empty")
        self.api_key = api_key
        self.model = model
        self.provider = "openrouter"

    def generate(self, system: str, user: str, max_tokens: int = 16000,
                 images: Optional[list[dict]] = None) -> str:
        try:
            import httpx
        except ImportError:
            raise LLMError("httpx not installed (run: pip install httpx)")

        # Build OpenAI-shaped messages. System prompt is a separate message;
        # user message can be a string OR a content array when images are
        # attached.
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})

        if images:
            user_content: list[dict] = [{"type": "text", "text": user}]
            for img in images:
                media_type = img.get("media_type", "image/png")
                data = img.get("data", "")
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{media_type};base64,{data}"},
                })
            messages.append({"role": "user", "content": user_content})
        else:
            messages.append({"role": "user", "content": user})

        # Qwen-specific sampling (see generate_stream for rationale).
        sampling: dict = {}
        if self.model.startswith("qwen/"):
            sampling = {
                "temperature": 1.0,
                "top_p": 0.95,
                "top_k": 40,
                "min_p": 0.2,
            }

        try:
            resp = httpx.post(
                f"{self._BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": self._PEBBLE_REFERER,
                    "X-Title": self._PEBBLE_TITLE,
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    **sampling,
                },
                # 10 min — full site generations can take 60-180s
                # comfortably; pad for slower model + queue depth on
                # OpenRouter's side.
                timeout=600.0,
            )
            resp.raise_for_status()
            body = resp.json()
            return body["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            # Try to pull the structured error message OpenRouter returns;
            # fall back to the raw status. Common failures: 402 (credits),
            # 404 (unknown model), 429 (rate limit), 502 (upstream provider).
            try:
                err = e.response.json().get("error", {})
                msg = err.get("message") or str(e)
            except Exception:
                msg = str(e)
            raise LLMError(f"OpenRouter API call failed (HTTP {e.response.status_code}): {msg}")
        except httpx.HTTPError as e:
            raise LLMError(f"OpenRouter network error: {e}")
        except (KeyError, IndexError, ValueError) as e:
            raise LLMError(f"OpenRouter response shape unexpected: {e}")

    def generate_stream(self, system: str, user: str, max_tokens: int = 60000,
                        images: Optional[list[dict]] = None) -> Iterator[str]:
        """Yield text chunks as they arrive from OpenRouter's streaming
        endpoint. Same shape as ``generate()`` but with ``stream: true``
        and the response parsed as SSE.

        Use this when downstream wants to react to partial output (e.g.
        the engine emits a `file_written` SSE event per complete
        <pebble-file> block as it streams in). The user perceives the
        build as 2-3x faster even though total wall time is unchanged.

        Yields plain text chunks. The caller is responsible for buffering
        and parsing structured content out of the stream.
        """
        try:
            import httpx
        except ImportError:
            raise LLMError("httpx not installed (run: pip install httpx)")

        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        if images:
            user_content: list[dict] = [{"type": "text", "text": user}]
            for img in images:
                media_type = img.get("media_type", "image/png")
                data = img.get("data", "")
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{media_type};base64,{data}"},
                })
            messages.append({"role": "user", "content": user_content})
        else:
            messages.append({"role": "user", "content": user})

        # Qwen 3.x recommended sampling params per HF Qwen3-Coder-Next card
        # + the HN-thread fix for the "loop-in-format-thinking" failure mode
        # (min_p=0.2). Applied only when the model id starts with "qwen/" to
        # avoid pinning these to non-Qwen routes that might prefer different
        # defaults (e.g. deepseek/anthropic/llama via OpenRouter).
        sampling: dict = {}
        if self.model.startswith("qwen/"):
            sampling = {
                "temperature": 1.0,
                "top_p": 0.95,
                "top_k": 40,
                "min_p": 0.2,
            }

        try:
            with httpx.stream(
                "POST",
                f"{self._BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": self._PEBBLE_REFERER,
                    "X-Title": self._PEBBLE_TITLE,
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "stream": True,
                    **sampling,
                },
                timeout=900.0,  # match SSE outer timeout
            ) as resp:
                if resp.status_code >= 400:
                    # Read the body to surface the structured error
                    try:
                        body_bytes = resp.read()
                        err_body = json.loads(body_bytes.decode("utf-8")).get("error", {})
                        msg = err_body.get("message") or f"HTTP {resp.status_code}"
                    except Exception:
                        msg = f"HTTP {resp.status_code}"
                    raise LLMError(
                        f"OpenRouter streaming call failed (HTTP {resp.status_code}): {msg}"
                    )

                for raw_line in resp.iter_lines():
                    if not raw_line:
                        continue
                    line = raw_line if isinstance(raw_line, str) else raw_line.decode("utf-8", errors="ignore")
                    if not line.startswith("data: "):
                        continue
                    payload = line[6:].strip()
                    # OpenRouter follows OpenAI's convention: data: [DONE]
                    # at end of stream. Stop cleanly without yielding it.
                    if payload == "[DONE]":
                        return
                    try:
                        event = json.loads(payload)
                    except json.JSONDecodeError:
                        # OpenRouter occasionally emits keep-alive comments
                        # (lines starting with `: `) which iter_lines already
                        # strips. Anything else that's not valid JSON is
                        # also non-fatal — skip.
                        continue
                    try:
                        delta = event["choices"][0]["delta"]
                    except (KeyError, IndexError, TypeError):
                        continue
                    chunk = delta.get("content")
                    if chunk:
                        yield chunk
        except httpx.HTTPError as e:
            raise LLMError(f"OpenRouter network error during stream: {e}")


# ---- Provider selector --------------------------------------------------

def get_llm_client() -> tuple[Optional[object], str]:
    """Return (client, reason). Client is None if unavailable; reason explains why.

    Provider priority:
        PEBBLE_PROVIDER=anthropic  -> AnthropicClient
        PEBBLE_PROVIDER=gemini     -> GeminiClient
        PEBBLE_PROVIDER=openrouter -> OpenRouterClient (Qwen / DeepSeek / etc.)
        (unset)                    -> try Anthropic first if ANTHROPIC_API_KEY is set,
                                      then fall back to Gemini
        (unset, no Anthropic key)  -> try Gemini
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

    # -- Explicit OpenRouter request (Qwen, DeepSeek, Llama, etc.) --
    if provider == "openrouter":
        key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if not key:
            return None, "OPENROUTER_API_KEY not set (PEBBLE_PROVIDER=openrouter)"
        model = os.environ.get("PEBBLE_MODEL", _OPENROUTER_DEFAULT_MODEL).strip() or _OPENROUTER_DEFAULT_MODEL
        try:
            return OpenRouterClient(api_key=key, model=model), "ok"
        except LLMError as e:
            return None, str(e)

    # -- Explicit Gemini request --
    if provider == "gemini":
        gemini_key = os.environ.get("GOOGLE_API_KEY", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()
        if not gemini_key:
            return None, "GOOGLE_API_KEY not set (PEBBLE_PROVIDER=gemini)"
        if not _GOOGLE_OK:
            return None, "google-genai package not installed (run: pip install google-genai)"
        model = os.environ.get("PEBBLE_MODEL", _GEMINI_DEFAULT_MODEL).strip() or _GEMINI_DEFAULT_MODEL
        try:
            return GeminiClient(api_key=gemini_key, model=model), "ok"
        except LLMError as e:
            return None, str(e)

    # -- Auto-detect: Anthropic first (faster, more instruction-following) --
    if _ANTHROPIC_OK:
        key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if key:
            model = os.environ.get("PEBBLE_MODEL", _ANTHROPIC_DEFAULT_MODEL).strip() or _ANTHROPIC_DEFAULT_MODEL
            try:
                return AnthropicClient(api_key=key, model=model), "ok"
            except LLMError as e:
                return None, str(e)

    # -- Fall back to Gemini if no Anthropic key --
    gemini_key = os.environ.get("GOOGLE_API_KEY", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()
    if gemini_key and _GOOGLE_OK:
        model = os.environ.get("PEBBLE_MODEL", _GEMINI_DEFAULT_MODEL).strip() or _GEMINI_DEFAULT_MODEL
        try:
            return GeminiClient(api_key=gemini_key, model=model), "ok"
        except LLMError as e:
            return None, str(e)

    # -- Nothing configured --
    if not _GOOGLE_OK and not _ANTHROPIC_OK:
        return None, "no LLM package installed (run: pip install -r requirements.txt)"
    if not os.environ.get("ANTHROPIC_API_KEY", "").strip() and not gemini_key:
        return None, "no API key set -- add ANTHROPIC_API_KEY or GOOGLE_API_KEY to .env"
    return None, "LLM not configured"


__all__ = [
    "LLMError",
    "GeminiClient",
    "AnthropicClient",
    "OpenRouterClient",
    "get_llm_client",
    "_ANTHROPIC_OK",
    "_GOOGLE_OK",
    "_GEMINI_DEFAULT_MODEL",
    "_ANTHROPIC_DEFAULT_MODEL",
    "_OPENROUTER_DEFAULT_MODEL",
]
