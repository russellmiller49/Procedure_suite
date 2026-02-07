"""Unit tests for OpenAI Responses API primary path.

Tests the migration from Chat Completions to Responses API as primary path.
All tests use mocked httpx - no real network calls.
"""

from __future__ import annotations

import logging

import httpx
import pytest

from app.common.exceptions import LLMError
from app.common.llm import OpenAILLM
from app.common.openai_responses import (
    parse_responses_text,
    parse_responses_json_object,
    ResponsesEndpointNotFound,
)


# =============================================================================
# Test A: Responses API succeeds
# =============================================================================


def test_responses_api_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that Responses API is used by default and returns correct output."""
    monkeypatch.delenv("OPENAI_OFFLINE", raising=False)
    monkeypatch.setenv("OPENAI_PRIMARY_API", "responses")

    llm = OpenAILLM(api_key="test-key", model="gpt-5-mini")
    calls = {"urls": []}

    def _mock_post(self, url, headers=None, json=None, **_kwargs):  # noqa: ANN001
        calls["urls"].append(url)
        request = httpx.Request("POST", url)
        # Responses API format
        return httpx.Response(
            200,
            request=request,
            json={"output_text": '{"result": "success"}'},
        )

    monkeypatch.setattr(httpx.Client, "post", _mock_post)

    out = llm.generate("Test prompt", task="registry_extraction")

    assert out == '{"result": "success"}'
    assert len(calls["urls"]) == 1
    assert "/v1/responses" in calls["urls"][0]


def test_responses_api_with_output_list_format(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test Responses API with output as list of message segments."""
    monkeypatch.delenv("OPENAI_OFFLINE", raising=False)
    monkeypatch.setenv("OPENAI_PRIMARY_API", "responses")

    llm = OpenAILLM(api_key="test-key", model="gpt-5-mini")

    def _mock_post(self, url, headers=None, json=None, **_kwargs):  # noqa: ANN001
        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            request=request,
            json={
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "text", "text": '{"a": 1}'}],
                    }
                ]
            },
        )

    monkeypatch.setattr(httpx.Client, "post", _mock_post)

    out = llm.generate("Test prompt")
    assert out == '{"a": 1}'


# =============================================================================
# Test B: Responses transient timeout retries once
# =============================================================================


def test_responses_api_retries_once_on_timeout(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that Responses API retries exactly once on read timeout."""
    monkeypatch.delenv("OPENAI_OFFLINE", raising=False)
    monkeypatch.setenv("OPENAI_PRIMARY_API", "responses")

    llm = OpenAILLM(api_key="test-key", model="gpt-5-mini")
    prompt = "SENSITIVE_PROMPT_SHOULD_NOT_LOG"
    calls = {"count": 0}

    def _mock_post(self, url, headers=None, json=None, **_kwargs):  # noqa: ANN001
        calls["count"] += 1
        request = httpx.Request("POST", url)
        if calls["count"] == 1:
            raise httpx.ReadTimeout("read timeout", request=request)
        return httpx.Response(
            200,
            request=request,
            json={"output_text": '{"ok": true}'},
        )

    monkeypatch.setattr(httpx.Client, "post", _mock_post)
    monkeypatch.setattr("app.common.openai_responses.time.sleep", lambda _s: None)

    caplog.set_level(logging.WARNING, logger="common.openai_responses")

    out = llm.generate(prompt, task="registry_extraction")

    assert out == '{"ok": true}'
    assert calls["count"] == 2
    # PHI safety: prompt should not appear in logs
    assert prompt not in caplog.text


def test_responses_api_raises_after_one_timeout_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that Responses API raises after exactly one retry on timeout."""
    monkeypatch.delenv("OPENAI_OFFLINE", raising=False)
    monkeypatch.setenv("OPENAI_PRIMARY_API", "responses")

    llm = OpenAILLM(api_key="test-key", model="gpt-5-mini")
    calls = {"count": 0}

    def _mock_post(self, url, headers=None, json=None, **_kwargs):  # noqa: ANN001
        calls["count"] += 1
        request = httpx.Request("POST", url)
        raise httpx.ReadTimeout("read timeout", request=request)

    monkeypatch.setattr(httpx.Client, "post", _mock_post)
    monkeypatch.setattr("app.common.openai_responses.time.sleep", lambda _s: None)

    with pytest.raises(LLMError, match="transport error after retry"):
        llm.generate("hi", task="registry_extraction")

    assert calls["count"] == 2


# =============================================================================
# Test C: Responses unsupported-param 400 retries once
# =============================================================================


def test_responses_api_retries_on_unsupported_param(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that Responses API retries once on 400 unsupported param."""
    monkeypatch.delenv("OPENAI_OFFLINE", raising=False)
    monkeypatch.setenv("OPENAI_PRIMARY_API", "responses")

    llm = OpenAILLM(api_key="test-key", model="gpt-4o")  # Non-GPT-5 to allow temperature
    prompt = "ANOTHER_SENSITIVE_PROMPT"
    calls = {"count": 0, "payloads": []}

    def _mock_post(self, url, headers=None, json=None, **_kwargs):  # noqa: ANN001
        calls["count"] += 1
        calls["payloads"].append(dict(json) if json else {})
        request = httpx.Request("POST", url)
        if calls["count"] == 1:
            return httpx.Response(
                400,
                request=request,
                json={
                    "error": {
                        "message": "Unsupported parameter: temperature",
                        "type": "invalid_request_error",
                        "param": "temperature",
                    }
                },
            )
        return httpx.Response(
            200,
            request=request,
            json={"output_text": '{"fixed": true}'},
        )

    monkeypatch.setattr(httpx.Client, "post", _mock_post)

    caplog.set_level(logging.WARNING, logger="common.openai_responses")

    # Pass temperature so it's in the payload and can be removed on retry
    out = llm.generate(prompt, task="registry_extraction", temperature=0.5)

    assert out == '{"fixed": true}'
    assert calls["count"] == 2
    # Verify first call had temperature, second didn't
    assert "temperature" in calls["payloads"][0]
    assert "temperature" not in calls["payloads"][1]
    # PHI safety
    assert prompt not in caplog.text


# =============================================================================
# Test D: Responses endpoint missing falls back to Chat Completions
# =============================================================================


def test_responses_api_fallback_to_chat_on_404(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that 404 from Responses API triggers fallback to Chat Completions."""
    monkeypatch.delenv("OPENAI_OFFLINE", raising=False)
    monkeypatch.setenv("OPENAI_PRIMARY_API", "responses")
    monkeypatch.setenv("OPENAI_RESPONSES_FALLBACK_TO_CHAT", "1")

    llm = OpenAILLM(api_key="test-key", model="gpt-5-mini")
    calls = {"urls": []}

    def _mock_post(self, url, headers=None, json=None, **_kwargs):  # noqa: ANN001
        calls["urls"].append(url)
        request = httpx.Request("POST", url)
        if "/v1/responses" in url:
            return httpx.Response(
                404,
                request=request,
                json={"error": {"message": "Not found"}},
            )
        # Chat Completions path
        return httpx.Response(
            200,
            request=request,
            json={"choices": [{"message": {"content": '{"fallback": true}'}}]},
        )

    monkeypatch.setattr(httpx.Client, "post", _mock_post)

    out = llm.generate("Test prompt")

    assert out == '{"fallback": true}'
    assert len(calls["urls"]) == 2
    assert "/v1/responses" in calls["urls"][0]
    assert "/v1/chat/completions" in calls["urls"][1]


# =============================================================================
# Test E: Fallback disabled
# =============================================================================


def test_responses_api_no_fallback_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that 404 raises when fallback is disabled."""
    monkeypatch.delenv("OPENAI_OFFLINE", raising=False)
    monkeypatch.setenv("OPENAI_PRIMARY_API", "responses")
    monkeypatch.setenv("OPENAI_RESPONSES_FALLBACK_TO_CHAT", "0")

    llm = OpenAILLM(api_key="test-key", model="gpt-5-mini")

    def _mock_post(self, url, headers=None, json=None, **_kwargs):  # noqa: ANN001
        request = httpx.Request("POST", url)
        return httpx.Response(
            404,
            request=request,
            json={"error": {"message": "Not found"}},
        )

    monkeypatch.setattr(httpx.Client, "post", _mock_post)

    with pytest.raises(ResponsesEndpointNotFound):
        llm.generate("Test prompt")


# =============================================================================
# Test: Chat Completions mode bypasses Responses API
# =============================================================================


def test_chat_mode_bypasses_responses_api(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that OPENAI_PRIMARY_API=chat uses Chat Completions directly."""
    monkeypatch.delenv("OPENAI_OFFLINE", raising=False)
    monkeypatch.setenv("OPENAI_PRIMARY_API", "chat")

    llm = OpenAILLM(api_key="test-key", model="gpt-5-mini")
    calls = {"urls": []}

    def _mock_post(self, url, headers=None, json=None, **_kwargs):  # noqa: ANN001
        calls["urls"].append(url)
        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            request=request,
            json={"choices": [{"message": {"content": '{"chat": true}'}}]},
        )

    monkeypatch.setattr(httpx.Client, "post", _mock_post)

    out = llm.generate("Test prompt")

    assert out == '{"chat": true}'
    assert len(calls["urls"]) == 1
    assert "/v1/chat/completions" in calls["urls"][0]


# =============================================================================
# Parse robustness tests
# =============================================================================


def test_parse_responses_text_output_text() -> None:
    """Test parsing output_text format."""
    resp = {"output_text": "Hello world"}
    assert parse_responses_text(resp) == "Hello world"


def test_parse_responses_text_direct_string_output() -> None:
    """Test parsing direct string output."""
    resp = {"output": "Direct string"}
    assert parse_responses_text(resp) == "Direct string"


def test_parse_responses_text_message_list() -> None:
    """Test parsing message list output."""
    resp = {
        "output": [
            {"type": "message", "content": [{"type": "text", "text": "Part 1"}]},
            {"type": "message", "content": [{"type": "text", "text": "Part 2"}]},
        ]
    }
    assert parse_responses_text(resp) == "Part 1Part 2"


def test_parse_responses_text_text_type_list() -> None:
    """Test parsing text-type list output."""
    resp = {"output": [{"type": "text", "text": "Just text"}]}
    assert parse_responses_text(resp) == "Just text"


def test_parse_responses_text_missing_output_raises() -> None:
    """Test that missing output raises ValueError with safe message."""
    with pytest.raises(ValueError, match="no extractable output"):
        parse_responses_text({})


def test_parse_responses_text_non_dict_raises() -> None:
    """Test that non-dict input raises ValueError."""
    with pytest.raises(ValueError, match="non-dict"):
        parse_responses_text("not a dict")  # type: ignore[arg-type]


def test_parse_responses_json_object_success() -> None:
    """Test JSON object parsing success."""
    resp = {"output_text": '{"key": "value"}'}
    result = parse_responses_json_object(resp)
    assert result == {"key": "value"}


def test_parse_responses_json_object_with_code_fences() -> None:
    """Test JSON parsing with markdown code fences."""
    resp = {"output_text": '```json\n{"key": "value"}\n```'}
    result = parse_responses_json_object(resp)
    assert result == {"key": "value"}


def test_parse_responses_json_object_returns_none_on_invalid() -> None:
    """Test that invalid JSON returns None."""
    resp = {"output_text": "not valid json"}
    result = parse_responses_json_object(resp)
    assert result is None


def test_parse_responses_json_object_returns_none_on_missing() -> None:
    """Test that missing output returns None."""
    result = parse_responses_json_object({})
    assert result is None
