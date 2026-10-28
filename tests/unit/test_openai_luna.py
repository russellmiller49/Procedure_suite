"""Luna migration preserves JSON output and the existing non-reasoning workload."""

import httpx
import pytest

from app.common.llm import OpenAILLM
from app.common.model_capabilities import is_gpt6_luna
from app.common.openai_responses import build_responses_payload


@pytest.mark.parametrize("api", ["responses", "chat", "responses_fallback"])
def test_luna_request_contract(monkeypatch, api):
    monkeypatch.setenv("OPENAI_OFFLINE", "0")
    monkeypatch.setenv("OPENAI_PRIMARY_API", "chat" if api == "chat" else "responses")
    monkeypatch.setenv("OPENAI_RESPONSES_FALLBACK_TO_CHAT", "1")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com")
    monkeypatch.setenv("ENABLE_LLM_CACHE", "0")
    calls = []

    def post(_self, url, *, json, **kwargs):
        calls.append((url, json))
        request = httpx.Request("POST", url)
        if url.endswith("/responses"):
            assert json["reasoning"] == {"effort": "none"}
            assert "Return exactly one JSON object" in json["input"]
            if api == "responses_fallback":
                return httpx.Response(404, request=request, json={"error": "not found"})
            body = {"output_text": '{"station": "7", "passes": null}'}
        else:
            assert json["reasoning_effort"] == "none"
            assert json["response_format"] == {"type": "json_object"}
            assert "Return exactly one JSON object" in json["messages"][0]["content"]
            body = {"choices": [{"message": {"content": '{"station": "7", "passes": null}'}}]}
        assert "temperature" not in json
        assert "top_p" not in json
        assert "seed" not in json
        return httpx.Response(200, request=request, json=body)

    monkeypatch.setattr(httpx.Client, "post", post)
    result = OpenAILLM(api_key="test-key", model="gpt-6-luna", task="structurer").generate(
        "EBUS sampled station 7. Return JSON.", temperature=0.0, top_p=0.9, seed=42,
    )
    assert result == '{"station": "7", "passes": null}'
    assert len(calls) == (2 if api == "responses_fallback" else 1)


def test_existing_models_keep_their_reasoning_defaults():
    for model in ("gpt-5.2", "gpt-5-mini", "gpt-4o"):
        assert "reasoning" not in build_responses_payload(model, "Return JSON.")
    assert is_gpt6_luna("gpt-6-luna")
    assert is_gpt6_luna("gpt-6-luna-2026-10-01")
    assert not is_gpt6_luna("gpt-5.6-luna")
    assert not is_gpt6_luna("gpt-6-astra")


def test_explicit_responses_reasoning_is_preserved():
    payload = build_responses_payload(
        "gpt-6-luna", "Return JSON.", extra={"reasoning": {"effort": "low"}},
    )
    assert payload["reasoning"] == {"effort": "low"}
