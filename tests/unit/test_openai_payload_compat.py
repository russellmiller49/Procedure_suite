from __future__ import annotations

import copy

import httpx
import pytest

from app.common.exceptions import LLMError
from app.common.llm import OpenAILLM
from app.common.model_capabilities import filter_payload_for_model


def test_filter_payload_for_model_removes_response_format_for_gpt5() -> None:
    payload = {
        "model": "gpt-5-mini",
        "messages": [{"role": "user", "content": "hi"}],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
        "top_p": 0.9,
    }
    original = copy.deepcopy(payload)

    filtered = filter_payload_for_model(payload, "gpt-5-mini")

    assert payload == original  # does not mutate input
    assert "response_format" not in filtered
    assert "temperature" not in filtered
    assert "top_p" not in filtered
    assert filtered["model"] == "gpt-5-mini"


def test_openai_llm_retries_once_on_unsupported_response_format(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_OFFLINE", raising=False)
    # Force Chat Completions mode for this test (tests Chat-specific retry logic)
    monkeypatch.setenv("OPENAI_PRIMARY_API", "chat")

    llm = OpenAILLM(api_key="test-key", model="gpt-4.1", timeout_seconds=1.0)
    sent_payloads: list[dict] = []

    def _mock_post(self, url, headers=None, json=None, **_kwargs):  # noqa: ANN001
        sent_payloads.append(copy.deepcopy(json))
        request = httpx.Request("POST", url)
        if len(sent_payloads) == 1:
            return httpx.Response(
                400,
                request=request,
                headers={"x-request-id": "req_1"},
                json={
                    "error": {
                        "message": "Unsupported parameter: response_format",
                        "type": "invalid_request_error",
                        "param": "response_format",
                    }
                },
            )

        return httpx.Response(
            200,
            request=request,
            json={"choices": [{"message": {"content": "{\"ok\": true}"}}]},
        )

    monkeypatch.setattr(httpx.Client, "post", _mock_post)

    out = llm.generate("hi")
    assert out
    assert len(sent_payloads) == 2
    assert "response_format" in sent_payloads[0]
    assert "response_format" not in sent_payloads[1]


def test_openai_llm_retries_once_on_unsupported_sampling_params(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_OFFLINE", raising=False)
    # Force Chat Completions mode for this test (tests Chat-specific retry logic)
    monkeypatch.setenv("OPENAI_PRIMARY_API", "chat")

    llm = OpenAILLM(api_key="test-key", model="gpt-4.1", timeout_seconds=1.0)
    sent_payloads: list[dict] = []

    def _mock_post(self, url, headers=None, json=None, **_kwargs):  # noqa: ANN001
        sent_payloads.append(copy.deepcopy(json))
        request = httpx.Request("POST", url)
        if len(sent_payloads) == 1:
            return httpx.Response(
                400,
                request=request,
                json={
                    "error": {
                        "message": "Unknown parameter: temperature",
                        "type": "invalid_request_error",
                        "param": "temperature",
                    }
                },
            )
        return httpx.Response(
            200,
            request=request,
            json={"choices": [{"message": {"content": "{}"}}]},
        )

    monkeypatch.setattr(httpx.Client, "post", _mock_post)

    llm.generate("hi", temperature=0.2, top_p=0.9, seed=123, logprobs=True)

    assert len(sent_payloads) == 2
    assert sent_payloads[0]["temperature"] == 0.2
    assert sent_payloads[0]["top_p"] == 0.9
    assert sent_payloads[0]["seed"] == 123
    assert sent_payloads[0]["logprobs"] is True

    assert "temperature" not in sent_payloads[1]
    assert "top_p" not in sent_payloads[1]
    assert "seed" not in sent_payloads[1]
    assert "logprobs" not in sent_payloads[1]


def test_openai_llm_only_retries_once(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_OFFLINE", raising=False)
    # Force Chat Completions mode for this test (tests Chat-specific retry logic)
    monkeypatch.setenv("OPENAI_PRIMARY_API", "chat")

    llm = OpenAILLM(api_key="test-key", model="gpt-4.1", timeout_seconds=1.0)
    sent_payloads: list[dict] = []

    def _mock_post(self, url, headers=None, json=None, **_kwargs):  # noqa: ANN001
        sent_payloads.append(copy.deepcopy(json))
        request = httpx.Request("POST", url)
        return httpx.Response(
            400,
            request=request,
            json={
                "error": {
                    "message": "Unsupported parameter: response_format",
                    "type": "invalid_request_error",
                    "param": "response_format",
                }
            },
        )

    monkeypatch.setattr(httpx.Client, "post", _mock_post)

    with pytest.raises(LLMError):
        llm.generate("hi")

    assert len(sent_payloads) == 2
    assert "response_format" in sent_payloads[0]
    assert "response_format" not in sent_payloads[1]

