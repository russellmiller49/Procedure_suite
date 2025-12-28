from __future__ import annotations

import logging

import httpx
import pytest

from modules.common.exceptions import LLMError
from modules.common.llm import OpenAILLM, _resolve_openai_timeout


def test_resolve_openai_timeout_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_TIMEOUT_READ_REGISTRY_SECONDS", raising=False)
    monkeypatch.delenv("OPENAI_TIMEOUT_READ_DEFAULT_SECONDS", raising=False)
    monkeypatch.delenv("OPENAI_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("OPENAI_TIMEOUT_SECONDS_STRUCTURER", raising=False)
    monkeypatch.delenv("OPENAI_TIMEOUT_SECONDS_JUDGE", raising=False)
    monkeypatch.delenv("OPENAI_TIMEOUT_SECONDS_SUMMARIZER", raising=False)

    assert _resolve_openai_timeout("registry_extraction").read == 180.0
    assert _resolve_openai_timeout("registry").read == 180.0
    assert _resolve_openai_timeout("structurer").read == 180.0
    assert _resolve_openai_timeout(None).read == 60.0


def test_openai_llm_retries_once_on_read_timeout(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.delenv("OPENAI_OFFLINE", raising=False)
    # Force Chat Completions mode for this test
    monkeypatch.setenv("OPENAI_PRIMARY_API", "chat")

    llm = OpenAILLM(api_key="test-key", model="gpt-5-mini")
    prompt = "VERY_SENSITIVE_PROMPT_SHOULD_NOT_APPEAR_IN_LOGS"

    calls = {"count": 0}

    def _mock_post(self, url, headers=None, json=None, **_kwargs):  # noqa: ANN001
        calls["count"] += 1
        request = httpx.Request("POST", url)
        if calls["count"] == 1:
            raise httpx.ReadTimeout("read timeout", request=request)
        return httpx.Response(
            200,
            request=request,
            json={"choices": [{"message": {"content": "{\"ok\": true}"}}]},
        )

    monkeypatch.setattr(httpx.Client, "post", _mock_post)
    monkeypatch.setattr("modules.common.llm.time.sleep", lambda _seconds: None)

    caplog.set_level(logging.WARNING, logger="common.llm")

    out = llm.generate(prompt, task="registry_extraction")
    assert out
    assert calls["count"] == 2
    assert prompt not in caplog.text


def test_openai_llm_raises_after_one_timeout_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_OFFLINE", raising=False)
    # Force Chat Completions mode for this test
    monkeypatch.setenv("OPENAI_PRIMARY_API", "chat")

    llm = OpenAILLM(api_key="test-key", model="gpt-5-mini")
    calls = {"count": 0}

    def _mock_post(self, url, headers=None, json=None, **_kwargs):  # noqa: ANN001
        calls["count"] += 1
        request = httpx.Request("POST", url)
        raise httpx.ReadTimeout("read timeout", request=request)

    monkeypatch.setattr(httpx.Client, "post", _mock_post)
    monkeypatch.setattr("modules.common.llm.time.sleep", lambda _seconds: None)

    with pytest.raises(LLMError):
        llm.generate("hi", task="registry_extraction")

    assert calls["count"] == 2

