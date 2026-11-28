"""Offline tests for the provider-neutral extractor and the OpenAI arm (no network).

The OpenAI client runs against ``httpx.MockTransport``; the Claude client against a
fake SDK. Both are fed the same hand-authored facts fixture.
"""

import copy
import hashlib
import json
import uuid
from pathlib import Path

import httpx
import pytest
from ip_registry_contracts.models import ExtractionRequest

from app.common.anthropic_client import ClaudeClient, ClaudeResult, ClaudeSettings
from app.common.exceptions import LLMError
from app.common.llm_egress import EgressDenied, egress_context
from app.common.openai_structured_client import (
    OpenAISettings,
    OpenAIStructuredClient,
    OpenAITimeoutError,
    build_params,
    estimate_cost_usd,
    result_from_response,
)
from app.llm_extraction.facts_schema import strict_schema_stats
from app.llm_extraction.result import LLMResult
from app.registry_workbench.extraction.assembler import Assembler
from app.registry_workbench.extraction.claude_provider import ClaudeRegistryProvider
from app.registry_workbench.extraction.contract_spec import contract_spec
from app.registry_workbench.extraction.openai_provider import OpenAIRegistryProvider
from app.registry_workbench.extraction.prompt import system_prompt
from ops.tools import eval_registry_llm as harness

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures/registry_workbench"
TEXT = (FIXTURES / "rebus_demo_procedure.txt").read_text()
FACTS = json.loads((FIXTURES / "rebus_demo_facts.json").read_text())

# OpenAI strict structured-output limits (developers.openai.com/api/docs/guides/
# structured-outputs, read 2026-11-25).
OPENAI_STRICT_LIMITS = {
    "properties": 5000,
    "depth": 10,
    "enum_values": 1000,
    "string_chars": 120_000,
    "large_enum_values": 250,  # a single enum above this many values ...
    "large_enum_chars": 15_000,  # ... must total at most this many characters
}


@pytest.fixture(autouse=True)
def _openai_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.delenv("PROCSUITE_OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_PRICING_JSON", raising=False)


def _request(text=TEXT):
    return ExtractionRequest(
        job_id=uuid.uuid4(),
        source_document_id=uuid.uuid4(),
        source_digest=hashlib.sha256(text.encode()).hexdigest(),
        text=text,
        kind="procedure",
    )


def _fact(facts, local_id, field):
    for array in ("enum_facts", "bool_facts", "number_facts", "text_facts"):
        for item in facts[array]:
            if item["local_id"] == local_id and item["field"] == field:
                return item
    raise KeyError((local_id, field))


def _openai_body(payload=None, *, status="completed", refusal=None, incomplete=None, model=None):
    content = (
        [{"type": "refusal", "refusal": refusal}]
        if refusal
        else [{"type": "output_text", "text": json.dumps(payload), "annotations": []}]
    )
    return {
        "id": "resp_test",
        "object": "response",
        "status": status,
        "incomplete_details": {"reason": incomplete} if incomplete else None,
        "model": model or "gpt-6.2-sol-2026-09-30",
        "output": [
            {"type": "reasoning", "id": "rs_1", "summary": []},
            {"type": "message", "role": "assistant", "content": content},
        ],
        "usage": {
            "input_tokens": 9000,
            "input_tokens_details": {"cached_tokens": 7000},
            "output_tokens": 2500,
            "output_tokens_details": {"reasoning_tokens": 1200},
            "total_tokens": 11500,
        },
    }


class _Transport:
    """Records requests and replays queued (status, body, headers) replies."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.requests = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        status, body, headers = reply if isinstance(reply, tuple) else (200, reply, {})
        return httpx.Response(status, json=body, headers=headers)

    @property
    def bodies(self):
        return [json.loads(r.content) for r in self.requests]


def _openai_provider(replies, settings=None, **kwargs):
    transport = _Transport(replies)
    client = OpenAIStructuredClient(
        settings or OpenAISettings(),
        transport=httpx.MockTransport(transport),
        sleep=lambda s: None,
    )
    return OpenAIRegistryProvider(client, **kwargs), transport


# Fake Anthropic SDK, as in test_claude_extraction.py.
class _Stream:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self.message


class _FakeSDK:
    def __init__(self, replies):
        replies = list(replies)
        messages = type("M", (), {"stream": lambda _self, **p: _Stream(replies.pop(0))})()
        self.messages = messages
        self.beta = type("Beta", (), {"messages": messages})()


def _claude_message(payload):
    return {
        "id": "msg_test",
        "model": "claude-opus-5-5",
        "stop_reason": "end_turn",
        "content": [{"type": "text", "text": json.dumps(payload)}],
        "usage": {"input_tokens": 900, "output_tokens": 2500, "cache_read_input_tokens": 7000},
    }


def _without_model_version(node):
    if isinstance(node, dict):
        return {
            k: _without_model_version(v)
            for k, v in node.items()
            if k not in {"extractor_model_version", "derivation_rule_version"}
        }
    if isinstance(node, list):
        return [_without_model_version(v) for v in node]
    return node


# -- schema limits -------------------------------------------------------------


def test_facts_schema_counts_are_pinned_and_within_openai_strict_limits():
    stats = strict_schema_stats(contract_spec().schema())
    assert {
        k: stats[k] for k in ("objects", "properties", "enums", "enum_values", "depth", "unions")
    } == {
        "objects": 9,
        "properties": 40,
        "enums": 14,
        "enum_values": 459,
        "depth": 3,
        "unions": 0,
    }
    assert stats["properties"] <= OPENAI_STRICT_LIMITS["properties"]
    assert stats["depth"] <= OPENAI_STRICT_LIMITS["depth"]
    assert stats["enum_values"] <= OPENAI_STRICT_LIMITS["enum_values"]
    assert stats["string_chars"] <= OPENAI_STRICT_LIMITS["string_chars"]
    if stats["largest_enum"] > OPENAI_STRICT_LIMITS["large_enum_values"]:
        assert stats["largest_enum_chars"] <= OPENAI_STRICT_LIMITS["large_enum_chars"]


def test_strict_schema_stats_flag_a_schema_over_the_enum_limit():
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["a"],
        "properties": {"a": {"type": "string", "enum": [f"v{i}" for i in range(1001)]}},
    }
    assert strict_schema_stats(schema)["enum_values"] > OPENAI_STRICT_LIMITS["enum_values"]


def test_every_object_in_the_facts_schema_is_closed_and_fully_required():
    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "object":
                assert node["additionalProperties"] is False
                assert set(node["required"]) == set(node["properties"])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(contract_spec().schema())


# -- client --------------------------------------------------------------------


def test_request_body_is_strict_unstored_and_caches_the_developer_prompt():
    body = build_params(
        OpenAISettings(effort="high"), system="S", user="U", schema={"type": "object"}
    )
    assert body["input"] == [
        {"role": "developer", "content": "S"},
        {"role": "user", "content": "U"},
    ]
    assert body["text"]["format"] == {
        "type": "json_schema",
        "name": "registry_facts",
        "schema": {"type": "object"},
        "strict": True,
    }
    assert body["reasoning"] == {"effort": "high"} and body["store"] is False
    assert (
        body["prompt_cache_key"]
        == build_params(OpenAISettings(), system="S", user="other", schema={})["prompt_cache_key"]
    )
    assert not {"temperature", "top_p", "instructions", "previous_response_id"} & set(body)


def test_endpoint_is_pinned_and_overridable_only_by_procsuite_env(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "https://proxy.invalid")
    provider, transport = _openai_provider([_openai_body(FACTS)])
    with egress_context("synthetic", source="test"):
        provider.extract(_request())
    request = transport.requests[0]
    assert str(request.url) == "https://api.openai.com/v1/responses"
    assert request.headers["authorization"] == "Bearer test-openai-key"
    monkeypatch.setenv("PROCSUITE_OPENAI_BASE_URL", "https://gateway.example")
    assert OpenAIStructuredClient().base_url == "https://gateway.example"


def test_egress_is_denied_without_a_declared_context():
    provider, transport = _openai_provider([_openai_body(FACTS)])
    with pytest.raises(EgressDenied):
        provider.extract(_request())
    assert transport.requests == []


def test_scrubbed_text_needs_openai_listed_as_an_approved_provider(monkeypatch):
    monkeypatch.setenv("PROCSUITE_LLM_EGRESS_APPROVED", "1")
    monkeypatch.setenv("PROCSUITE_LLM_EGRESS_PROVIDERS", "anthropic")
    provider, transport = _openai_provider([_openai_body(FACTS)])
    with egress_context("scrubbed_verified", source="test"), pytest.raises(EgressDenied):
        provider.extract(_request())
    assert transport.requests == []


def test_cost_counts_cached_tokens_at_the_cached_rate():
    result = result_from_response(_openai_body(FACTS), requested_model="gpt-6.2-sol")
    assert result.usage == {
        "input_tokens": 2000,
        "output_tokens": 2500,
        "cache_read_input_tokens": 7000,
        "cache_write_tokens": 0,
        "reasoning_tokens": 1200,
    }
    # 2000 x $2 + 7000 x $0.10 + 2500 x $10, per million tokens; snapshot ids price as the base.
    assert result.cost_usd == pytest.approx((2000 * 2 + 7000 * 0.10 + 2500 * 10) / 1e6)
    assert result.provider == "openai" and not result.fallback_used and result.ok


def test_cache_writes_and_pricing_override(monkeypatch):
    usage = {"input_tokens": 0, "cache_write_tokens": 1_000_000}
    assert estimate_cost_usd("gpt-6.2-astra", usage) == pytest.approx(10.0)
    monkeypatch.setenv("OPENAI_PRICING_JSON", json.dumps({"gpt-6-luna": {"input": 1, "output": 2}}))
    assert estimate_cost_usd("gpt-6-luna", {"cache_read_input_tokens": 1_000_000}) == pytest.approx(
        1.0
    )
    assert estimate_cost_usd("gpt-unknown", usage) is None


def test_incomplete_and_failed_responses_are_unusable():
    truncated = result_from_response(
        _openai_body(FACTS, status="incomplete", incomplete="max_output_tokens"),
        requested_model="gpt-6.2-sol",
    )
    assert truncated.stop_reason == "max_tokens" and truncated.parsed is None
    filtered = result_from_response(
        _openai_body(FACTS, status="incomplete", incomplete="content_filter"),
        requested_model="gpt-6.2-sol",
    )
    assert filtered.stop_reason == "incomplete:content_filter" and not filtered.ok


def test_rate_limits_retry_with_retry_after_but_quota_errors_do_not():
    sleeps = []
    transport = _Transport(
        [
            (
                429,
                {"error": {"type": "rate_limit_error", "code": "slow_down"}},
                {"retry-after": "3"},
            ),
            _openai_body(FACTS),
        ]
    )
    client = OpenAIStructuredClient(
        OpenAISettings(), transport=httpx.MockTransport(transport), sleep=sleeps.append
    )
    with egress_context("synthetic", source="test"):
        assert client.complete_json(system="S", user="U", schema={}).ok
    assert sleeps == [3.0] and len(transport.requests) == 2

    quota = _Transport(
        [(429, {"error": {"type": "insufficient_quota", "code": "insufficient_quota"}}, {})]
    )
    client = OpenAIStructuredClient(OpenAISettings(), transport=httpx.MockTransport(quota))
    with (
        egress_context("synthetic", source="test"),
        pytest.raises(LLMError, match="insufficient_quota"),
    ):
        client.complete_json(system="S", user="U", schema={})
    assert len(quota.requests) == 1


def test_timeouts_raise_a_timeout_error_without_retrying():
    transport = _Transport([httpx.ReadTimeout("slow")])
    client = OpenAIStructuredClient(OpenAISettings(), transport=httpx.MockTransport(transport))
    with egress_context("synthetic", source="test"), pytest.raises(OpenAITimeoutError):
        client.complete_json(system="S", user="U", schema={})
    assert len(transport.requests) == 1


# -- provider ------------------------------------------------------------------


def test_claude_and_openai_give_the_same_proposal_for_the_same_facts():
    request = _request()
    claude = ClaudeRegistryProvider(
        ClaudeClient(ClaudeSettings(), sdk=_FakeSDK([_claude_message(FACTS)]))
    )
    openai, transport = _openai_provider([_openai_body(FACTS)])
    with egress_context("synthetic", source="test"):
        from_claude = claude.extract(request)
        from_openai = openai.extract(request)
    assert from_claude.status == from_openai.status == "proposed"
    assert from_claude.warnings == from_openai.warnings
    assert _without_model_version(from_openai.observations["proposal"]) == _without_model_version(
        from_claude.observations["proposal"]
    )
    inference = from_openai.observations["inference"]
    assert inference["provider"] == "openai" and inference["requested_model"] == "gpt-6.2-sol"
    assert from_claude.observations["inference"]["provider"] == "claude"
    # Both providers send the same prompt and schema.
    body = transport.bodies[0]
    assert body["input"][0]["content"] == system_prompt()
    assert body["text"]["format"]["schema"] == contract_spec().schema()


def test_openai_repair_call_fires_once_for_an_unfixable_answer(monkeypatch):
    broken = copy.deepcopy(FACTS)
    _fact(broken, "P_RB", "procedures.performance")["value"] = "unknown"
    monkeypatch.setattr(Assembler, "_fix_link", lambda self, code: False)
    provider, transport = _openai_provider([_openai_body(broken), _openai_body(FACTS)])
    with egress_context("synthetic", source="test"):
        response = provider.extract(_request())
    assert response.status == "proposed" and response.observations["inference"]["repair_used"]
    first, repair = transport.bodies
    assert repair["input"][0] == first["input"][0] and len(repair["input"]) == 2
    content = repair["input"][1]["content"]
    assert "navigation_requires_started_robotic_component" in content
    assert "<previous_answer>" in content
    assert len(response.observations["inference"]["request_ids"]) == 2


def test_openai_refusal_is_degraded_not_raised():
    provider, _ = _openai_provider([_openai_body(refusal="I can't help with that.")])
    with egress_context("synthetic", source="test"):
        response = provider.extract(_request())
    assert response.status == "degraded" and "model_inference_failed" in response.warnings
    assert response.observations["proposal"] is None
    assert response.observations["quality_signals"][0]["stop_reason"] == "refusal"


def test_claude_result_is_the_provider_neutral_result():
    assert ClaudeResult is LLMResult


# -- eval harness ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("label", "model", "effort"),
    [
        ("openai:gpt-6.2-sol:medium", "gpt-6.2-sol", "medium"),
        ("openai:gpt-6-luna:low", "gpt-6-luna", "low"),
        ("openai:gpt-6.1-terra:none", "gpt-6.1-terra", "none"),
        ("openai:gpt-6.2-astra:xhigh", "gpt-6.2-astra", "xhigh"),
    ],
)
def test_openai_arm_labels_parse(label, model, effort):
    assert harness.parse_arm(label) == {
        "label": label,
        "kind": "openai",
        "model": model,
        "effort": effort,
    }


@pytest.mark.parametrize(
    "label",
    [
        "openai:gpt-4o:medium",
        "openai:gpt-6.2-sol",
        "openai:gpt-6.2-sol:medium:extra",
        "openai:gpt-6.2-sol:none",  # 6.2 models reject effort "none"
        "openai:gpt-6-luna:turbo",
        "openai:sol:medium",
    ],
)
def test_invalid_openai_arm_labels_are_rejected(label):
    with pytest.raises(SystemExit):
        harness.parse_arm(label)


def test_batch_mode_is_rejected_for_openai_arms():
    arms = [harness.parse_arm(a) for a in ("deterministic", "openai:gpt-6.2-sol:medium")]
    with pytest.raises(SystemExit, match="openai:gpt-6.2-sol:medium"):
        harness.check_mode(arms, "batch")
    harness.check_mode(arms, "online")
    harness.check_mode([harness.parse_arm("claude:opus:medium")], "batch")


def test_only_the_keys_the_arms_need_are_loaded(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    env = tmp_path / ".env"
    env.write_text("ANTHROPIC_API_KEY=a-key\nOPENAI_API_KEY=o-key\nPROCSUITE_ENV=production\n")
    harness.load_keys([harness.parse_arm("openai:gpt-6-luna:low")], env)
    import os

    assert os.environ["OPENAI_API_KEY"] == "o-key"
    assert "ANTHROPIC_API_KEY" not in os.environ and os.environ.get("PROCSUITE_ENV") != "production"
    with pytest.raises(SystemExit, match="ANTHROPIC_API_KEY"):
        harness.load_keys([harness.parse_arm("claude:opus:medium")], tmp_path / "missing.env")


def test_online_runner_keeps_order_and_enters_egress_per_thread(monkeypatch):
    rows = [
        {
            "document_id": f"d{i}",
            "text": TEXT,
            "text_sha256": hashlib.sha256(TEXT.encode()).hexdigest(),
        }
        for i in range(5)
    ]
    replies = [_openai_body(FACTS) for _ in rows]
    provider, transport = _openai_provider(replies)
    arm = harness.parse_arm("openai:gpt-6.2-sol:medium")
    results = harness.run_online(arm, rows, provider, "test", concurrency=3)
    assert list(results) == [r["document_id"] for r in rows]
    assert all(r["status"] == "proposed" for r in results.values())
    assert len(transport.requests) == 5
    mechanics = harness.mechanics(results)
    assert mechanics["outcomes"] == {
        "first_pass_success": 5,
        "repairs": 0,
        "refusals": 0,
        "timeouts": 0,
        "errors": 0,
        "degraded": 0,
    }
    assert mechanics["usage_totals"]["cache_read_input_tokens"] == 35000
    assert mechanics["latency_s"]["n"] == 5 and set(mechanics["latency_s"]) == {
        "n",
        "mean",
        "p50",
        "p95",
    }


def test_outcome_counts_classify_refusals_timeouts_and_repairs():
    values = [
        {"status": "proposed", "repair_used": False},
        {"status": "proposed", "repair_used": True},
        {"status": "degraded", "stop_reason": "refusal"},
        harness.summarize(OpenAITimeoutError("OpenAI request timed out: ReadTimeout")),
        harness.summarize(RuntimeError("boom")),
    ]
    assert harness.outcome_counts(values) == {
        "first_pass_success": 1,
        "repairs": 1,
        "refusals": 1,
        "timeouts": 1,
        "errors": 2,
        "degraded": 1,
    }
    assert harness.latency_stats([1.0, 2.0, 3.0, 4.0, 10.0]) == {
        "n": 5,
        "mean": 4.0,
        "p50": 3.0,
        "p95": 10.0,
    }
