"""OpenAI Responses API wrapper for schema-constrained extraction.

Mirrors ``ClaudeClient``: every request passes the egress gate first, constrains
the reply with a strict JSON schema (``text.format``), sets reasoning effort and
returns an ``LLMResult``. Raw ``httpx`` (no SDK dependency) against an endpoint
pinned to ``https://api.openai.com``; only ``PROCSUITE_OPENAI_BASE_URL`` moves it,
never an ambient ``OPENAI_BASE_URL``. ``store`` is always false.

Request notes (OpenAI docs, read 2026-11-25):
  - The static prompt is a leading ``developer`` message, not top-level
    ``instructions``: GPT-6.2 models append ``instructions`` after ``input`` and
    bill them uncached, which would defeat prompt caching.
  - ``max_output_tokens`` includes reasoning tokens.
  - ``usage.input_tokens`` includes cached tokens; this module normalises usage to
    the Anthropic convention (``input_tokens`` = uncached input only).
  - Sampling controls (temperature/top_p) are never sent.

Not built on ``app.common.openai_responses.post_responses``, which strips
parameters and retries on its own terms. Retries here are bounded and only for
429 rate limits (never quota errors) and 5xx; timeouts are not retried.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.common.exceptions import LLMError
from app.common.llm_egress import assert_egress_allowed
from app.common.logger import get_logger
from app.llm_extraction.result import LLMResult

logger = get_logger("common.openai_structured_client")

PROVIDER = "openai"
DEFAULT_BASE_URL = "https://api.openai.com"
SCHEMA_NAME = "registry_facts"

# Text models this client is priced and tested for, with the reasoning efforts
# their model pages list. ``minimal`` is listed for no 6.x model; the 6.2 models
# reject ``none``.
_COMMON_EFFORTS = ("low", "medium", "high", "xhigh", "max")
MODEL_EFFORTS: dict[str, tuple[str, ...]] = {
    "gpt-6.2-astra": _COMMON_EFFORTS,
    "gpt-6.2-sol": _COMMON_EFFORTS,
    "gpt-6.1-terra": ("none", *_COMMON_EFFORTS),
    "gpt-6-luna": ("none", *_COMMON_EFFORTS),
}

# USD per million tokens (developers.openai.com/api/docs/pricing, 2026-11-25).
# Cache writes (30-minute default TTL) cost 1.25x input. Prompts over 272K input
# tokens are billed higher; extraction prompts are far below that.
_DEFAULT_PRICING_PER_MTOK: dict[str, dict[str, float]] = {
    "gpt-6.2-astra": {"input": 8.00, "output": 40.00, "cache_read": 0.40},
    "gpt-6.2-sol": {"input": 2.00, "output": 10.00, "cache_read": 0.10},
    "gpt-6.1-terra": {"input": 1.00, "output": 5.00, "cache_read": 0.05},
    "gpt-6-luna": {"input": 0.10, "output": 0.50, "cache_read": 0.01},
}
_CACHE_WRITE_MULTIPLIER = 1.25
_RETRY_STATUSES = {429, 500, 502, 503, 504}


class OpenAITimeoutError(LLMError):
    """The request timed out (not retried)."""


def _pricing() -> dict[str, dict[str, float]]:
    pricing = {model: dict(rates) for model, rates in _DEFAULT_PRICING_PER_MTOK.items()}
    raw = os.getenv("OPENAI_PRICING_JSON", "").strip()
    if raw:
        try:
            for model, rates in json.loads(raw).items():
                pricing[model] = {key: float(value) for key, value in rates.items()}
        except (ValueError, TypeError, AttributeError):
            logger.warning("Ignoring malformed OPENAI_PRICING_JSON")
    return pricing


def _rates_for(model: str) -> dict[str, float] | None:
    """Exact model id, else the longest priced id the snapshot name starts with."""
    pricing = _pricing()
    if model in pricing:
        return pricing[model]
    matches = [m for m in pricing if model.startswith(m + "-")]
    return pricing[max(matches, key=len)] if matches else None


def estimate_cost_usd(model: str, usage: dict[str, int]) -> float | None:
    rates = _rates_for(model)
    if rates is None:
        return None
    per_token = {key: value / 1_000_000 for key, value in rates.items()}
    cache_read_rate = per_token.get("cache_read", per_token["input"])
    return (
        usage.get("input_tokens", 0) * per_token["input"]
        + usage.get("cache_read_input_tokens", 0) * cache_read_rate
        + usage.get("cache_write_tokens", 0) * per_token["input"] * _CACHE_WRITE_MULTIPLIER
        + usage.get("output_tokens", 0) * per_token["output"]
    )


def usage_dict(usage: dict[str, Any] | None) -> dict[str, int]:
    """Normalise Responses API usage to uncached input + cache reads/writes."""
    if not usage:
        return {}
    in_details = usage.get("input_tokens_details") or {}
    out_details = usage.get("output_tokens_details") or {}
    total_input = int(usage.get("input_tokens") or 0)
    cached = int(in_details.get("cached_tokens") or 0)
    written = int(in_details.get("cache_write_tokens") or 0)
    return {
        "input_tokens": max(total_input - cached - written, 0),
        "output_tokens": int(usage.get("output_tokens") or 0),
        "cache_read_input_tokens": cached,
        "cache_write_tokens": written,
        "reasoning_tokens": int(out_details.get("reasoning_tokens") or 0),
    }


@dataclass(frozen=True)
class OpenAISettings:
    model: str = "gpt-6.2-sol"
    effort: str = "medium"
    max_output_tokens: int = 64000
    timeout_s: float = 600.0
    max_retries: int = 2

    @classmethod
    def from_env(cls, **overrides: Any) -> OpenAISettings:
        values: dict[str, Any] = {
            "model": os.getenv("PROCSUITE_OPENAI_MODEL", cls.model),
            "effort": os.getenv("PROCSUITE_OPENAI_EFFORT", cls.effort),
            "max_output_tokens": int(
                os.getenv("PROCSUITE_OPENAI_MAX_OUTPUT_TOKENS", cls.max_output_tokens)
            ),
            "timeout_s": float(os.getenv("PROCSUITE_OPENAI_TIMEOUT_S", cls.timeout_s)),
            "max_retries": int(os.getenv("PROCSUITE_OPENAI_MAX_RETRIES", cls.max_retries)),
        }
        values.update({key: value for key, value in overrides.items() if value is not None})
        return cls(**values)


def build_params(
    settings: OpenAISettings, *, system: str, user: str, schema: dict[str, Any]
) -> dict[str, Any]:
    """Responses API body. The developer message is the cacheable prefix."""
    return {
        "model": settings.model,
        "input": [
            {"role": "developer", "content": system},
            {"role": "user", "content": user},
        ],
        "text": {
            "format": {"type": "json_schema", "name": SCHEMA_NAME, "schema": schema, "strict": True}
        },
        "reasoning": {"effort": settings.effort},
        "max_output_tokens": settings.max_output_tokens,
        "store": False,
        # Routes requests sharing the static prompt to the same cache.
        "prompt_cache_key": "procsuite-" + hashlib.sha256(system.encode()).hexdigest()[:24],
    }


def result_from_response(
    data: dict[str, Any], *, requested_model: str, latency_s: float | None = None
) -> LLMResult:
    """Parse a raw Responses API body (``output_text`` is an SDK helper, not in the JSON)."""
    texts: list[str] = []
    refused = False
    for item in data.get("output") or []:
        if item.get("type") != "message":
            continue
        for part in item.get("content") or []:
            if part.get("type") == "output_text":
                texts.append(part.get("text") or "")
            elif part.get("type") == "refusal":
                refused = True
    text = "".join(texts)
    status = data.get("status")
    if refused:
        stop_reason = "refusal"
    elif status == "incomplete":
        reason = (data.get("incomplete_details") or {}).get("reason")
        stop_reason = "max_tokens" if reason == "max_output_tokens" else f"incomplete:{reason}"
    else:
        stop_reason = status
    parsed = None
    if stop_reason == "completed" and text:
        try:
            parsed = json.loads(text)
        except ValueError:
            parsed = None
    usage = usage_dict(data.get("usage"))
    model = data.get("model") or requested_model
    return LLMResult(
        parsed=parsed if isinstance(parsed, dict) else None,
        text=text,
        stop_reason=stop_reason,
        model=model,
        requested_model=requested_model,
        request_id=data.get("id"),
        usage=usage,
        cost_usd=estimate_cost_usd(model, usage),
        latency_s=latency_s,
        provider=PROVIDER,
    )


def _retry_delay(response: httpx.Response, attempt: int) -> float | None:
    """Seconds to wait before retrying, or None when the error is not retryable."""
    if response.status_code not in _RETRY_STATUSES:
        return None
    if response.status_code == 429:
        try:
            error = (response.json() or {}).get("error") or {}
        except ValueError:
            error = {}
        if error.get("code") == "insufficient_quota" or error.get("type") == "insufficient_quota":
            return None
    header = response.headers.get("retry-after")
    try:
        return max(float(header), 0.0) if header else min(2.0 * 2**attempt, 30.0)
    except ValueError:
        return min(2.0 * 2**attempt, 30.0)


def _error_summary(response: httpx.Response) -> str:
    """Status and error type/code only; never echo request content."""
    try:
        error = (response.json() or {}).get("error") or {}
    except ValueError:
        error = {}
    return f"HTTP {response.status_code} type={error.get('type')} code={error.get('code')}"


class OpenAIStructuredClient:
    """Online strict-schema calls. ``transport`` lets tests stand in for the network."""

    def __init__(
        self,
        settings: OpenAISettings | None = None,
        *,
        transport: httpx.BaseTransport | None = None,
        sleep: Any = time.sleep,
    ) -> None:
        self.settings = settings or OpenAISettings.from_env()
        self._transport = transport
        self._sleep = sleep
        self._http: httpx.Client | None = None
        self._lock = threading.Lock()

    @property
    def base_url(self) -> str:
        return (os.getenv("PROCSUITE_OPENAI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")

    @property
    def http(self) -> httpx.Client:
        with self._lock:
            if self._http is None:
                self._http = httpx.Client(
                    base_url=self.base_url,
                    timeout=self.settings.timeout_s,
                    transport=self._transport,
                    trust_env=False,  # no ambient proxies for clinical-text egress
                )
            return self._http

    def _headers(self) -> dict[str, str]:
        key = os.getenv("OPENAI_API_KEY", "").strip()
        if not key:
            raise LLMError("OPENAI_API_KEY is not set")
        return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def complete_json(self, *, system: str, user: str, schema: dict[str, Any]) -> LLMResult:
        assert_egress_allowed(PROVIDER)
        params = build_params(self.settings, system=system, user=user, schema=schema)
        headers = self._headers()
        started = time.monotonic()
        attempt = 0
        while True:
            try:
                response = self.http.post("/v1/responses", json=params, headers=headers)
            except httpx.TimeoutException as exc:
                raise OpenAITimeoutError(f"OpenAI request timed out: {type(exc).__name__}") from exc
            except httpx.HTTPError as exc:
                raise LLMError(f"OpenAI request failed: {type(exc).__name__}") from exc
            if response.status_code < 400:
                break
            delay = _retry_delay(response, attempt)
            if delay is None or attempt >= self.settings.max_retries:
                raise LLMError(f"OpenAI request failed: {_error_summary(response)}")
            attempt += 1
            logger.info(
                "openai_retry status=%s attempt=%s delay=%.1f",
                response.status_code,
                attempt,
                delay,
            )
            self._sleep(delay)
        try:
            data = response.json()
        except ValueError as exc:
            raise LLMError("OpenAI response was not JSON") from exc
        result = result_from_response(
            data, requested_model=self.settings.model, latency_s=time.monotonic() - started
        )
        logger.info(
            "openai_call model=%s stop=%s in=%s out=%s reasoning=%s cache_read=%s cost=%s",
            result.model,
            result.stop_reason,
            result.usage.get("input_tokens"),
            result.usage.get("output_tokens"),
            result.usage.get("reasoning_tokens"),
            result.usage.get("cache_read_input_tokens"),
            None if result.cost_usd is None else round(result.cost_usd, 6),
        )
        return result


__all__ = [
    "MODEL_EFFORTS",
    "OpenAISettings",
    "OpenAIStructuredClient",
    "OpenAITimeoutError",
    "build_params",
    "estimate_cost_usd",
    "result_from_response",
    "usage_dict",
]
