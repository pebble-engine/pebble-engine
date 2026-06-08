"""AnthropicClient.generate must retry transient connection resets.

A mid-stream WinError 10054 / ConnectionReset used to kill an entire build
with no retry. These tests pin the retry-on-transient behavior and confirm
deterministic errors (auth/400) are NOT retried.
"""
from __future__ import annotations

import pytest

from pebble import llm
from pebble.llm import AnthropicClient, LLMError


class _FakeStreamCtx:
    """Context manager mimicking client.messages.stream(...)."""
    def __init__(self, chunks=None, raise_exc=None):
        self._chunks = chunks or []
        self._raise = raise_exc

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    @property
    def text_stream(self):
        if self._raise is not None:
            raise self._raise
        return iter(self._chunks)


class _FakeMessages:
    def __init__(self, behaviors):
        self._behaviors = list(behaviors)
        self.calls = 0

    def stream(self, **kw):
        b = self._behaviors[self.calls]
        self.calls += 1
        return b


class _FakeClient:
    def __init__(self, behaviors):
        self.messages = _FakeMessages(behaviors)


def _make_client(behaviors):
    c = AnthropicClient.__new__(AnthropicClient)  # bypass __init__ (no real key)
    c.client = _FakeClient(behaviors)
    c.model = "claude-test"
    c.provider = "anthropic"
    return c


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(llm.time, "sleep", lambda *_a, **_k: None)


def test_retries_on_connection_reset_then_succeeds():
    reset = ConnectionResetError(10054, "An existing connection was forcibly closed by the remote host")
    c = _make_client([
        _FakeStreamCtx(raise_exc=reset),     # attempt 1 — transient
        _FakeStreamCtx(chunks=["hello ", "world"]),  # attempt 2 — succeeds
    ])
    assert c.generate("sys", "user", max_tokens=10) == "hello world"
    assert c.client.messages.calls == 2


def test_retries_exhaust_then_raises_llmerror():
    reset = ConnectionResetError(10054, "forcibly closed")
    c = _make_client([_FakeStreamCtx(raise_exc=reset) for _ in range(llm._MAX_LLM_ATTEMPTS)])
    with pytest.raises(LLMError):
        c.generate("sys", "user", max_tokens=10)
    assert c.client.messages.calls == llm._MAX_LLM_ATTEMPTS


def test_does_not_retry_deterministic_error():
    class _AuthError(Exception):
        pass
    c = _make_client([_FakeStreamCtx(raise_exc=_AuthError("401 invalid x-api-key"))])
    with pytest.raises(LLMError):
        c.generate("sys", "user", max_tokens=10)
    assert c.client.messages.calls == 1  # no retry on a non-transient error


def test_string_match_forcibly_closed_is_transient():
    # Some SDK wrappers surface the reset as a generic Exception whose text
    # still names the reset. Treat that as transient too.
    c = _make_client([
        _FakeStreamCtx(raise_exc=Exception("peer closed connection without sending complete message body")),
        _FakeStreamCtx(chunks=["ok"]),
    ])
    assert c.generate("sys", "user", max_tokens=10) == "ok"
    assert c.client.messages.calls == 2
