"""Claude Messages API wrapper for schema-constrained extraction.

Every request streams, carries a cached static system block, constrains the reply
with ``output_config.format`` and passes the egress gate first. Sampling
parameters (temperature/top_p/top_k) are never sent: current models reject them.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any

from app.common.exceptions import LLMError
from app.common.llm_egress import assert_egress_allowed
from app.common.logger import get_logger

logger = get_logger("common.anthropic_client")

PROVIDER = "anthropic"
FALLBACK_BETA = "server-side-fallback-2026-07-01"

# USD per million tokens. Cache writes are priced from the input rate
# (5-minute TTL 1.25x, 1-hour TTL 2x); batch requests are half price.
_DEFAULT_PRICING_PER_MTOK: dict[str, dict[str, float]] = {
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_read": 0.20},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_read": 0.20},
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50, "cache_read": 0.01},
}
_CACHE_WRITE_MULTIPLIER = {"5m": 1.25, "1h": 2.0}
_BATCH_DISCOUNT = 0.5


def _pricing() -> dict[str, dict[str, float]]:
    pricing = {model: dict(rates) for model, rates in _DEFAULT_PRICING_PER_MTOK.items()}
    raw = os.getenv("ANTHROPIC_PRICING_JSON", "").strip()
    if raw:
        try:
            for model, rates in json.loads(raw).items():
                pricing[model] = {key: float(value) for key, value in rates.items()}
        except (ValueError, TypeError, AttributeError):
            logger.warning("Ignoring malformed ANTHROPIC_PRICING_JSON")
    return pricing


def estimate_cost_usd(model: str, usage: dict[str, int], *, batch: bool = False) -> float | None:
    rates = _pricing().get(model)
    if rates is None:
        return None
    per_token = {key: value / 1_000_000 for key, value in rates.items()}
    cost = (
        usage.get("input_tokens", 0) * per_token["input"]
        + usage.get("output_tokens", 0) * per_token["output"]
        + usage.get("cache_read_input_tokens", 0) * per_token["cache_read"]
        + usage.get("cache_write_5m_tokens", 0) * per_token["input"] * _CACHE_WRITE_MULTIPLIER["5m"]
        + usage.get("cache_write_1h_tokens", 0) * per_token["input"] * _CACHE_WRITE_MULTIPLIER["1h"]
    )
    return cost * (_BATCH_DISCOUNT if batch else 1.0)


def usage_dict(usage: Any) -> dict[str, int]:
    """Flatten an SDK ``Usage`` (or its dict form) into integer token counts."""
    if usage is None:
        return {}
    data = usage if isinstance(usage, dict) else usage.model_dump()
    creation = data.get("cache_creation") or {}
    write_5m = int(creation.get("ephemeral_5m_input_tokens") or 0)
    write_1h = int(creation.get("ephemeral_1h_input_tokens") or 0)
    if not creation and data.get("cache_creation_input_tokens"):
        write_5m = int(data["cache_creation_input_tokens"])
    return {
        "input_tokens": int(data.get("input_tokens") or 0),
        "output_tokens": int(data.get("output_tokens") or 0),
        "cache_read_input_tokens": int(data.get("cache_read_input_tokens") or 0),
        "cache_write_5m_tokens": write_5m,
        "cache_write_1h_tokens": write_1h,
    }


@dataclass(frozen=True)
class ClaudeSettings:
    model: str = "claude-opus-5-5"
    effort: str = "medium"
    max_tokens: int = 64000
    cache_ttl: str = "1h"
    fallbacks: bool = True
    timeout_s: float = 600.0

    @classmethod
    def from_env(cls, **overrides: Any) -> ClaudeSettings:
        values: dict[str, Any] = {
            "model": os.getenv("PROCSUITE_ANTHROPIC_MODEL", cls.model),
            "effort": os.getenv("PROCSUITE_ANTHROPIC_EFFORT", cls.effort),
            "max_tokens": int(os.getenv("PROCSUITE_ANTHROPIC_MAX_TOKENS", cls.max_tokens)),
            "cache_ttl": os.getenv("PROCSUITE_ANTHROPIC_CACHE_TTL", cls.cache_ttl),
            "fallbacks": os.getenv("PROCSUITE_ANTHROPIC_FALLBACKS", "default").strip().lower()
            != "off",
            "timeout_s": float(os.getenv("PROCSUITE_ANTHROPIC_TIMEOUT_S", cls.timeout_s)),
        }
        values.update({key: value for key, value in overrides.items() if value is not None})
        return cls(**values)


@dataclass
class ClaudeResult:
    parsed: dict[str, Any] | None
    text: str
    stop_reason: str | None
    model: str
    requested_model: str
    request_id: str | None
    usage: dict[str, int] = field(default_factory=dict)
    cost_usd: float | None = None
    latency_s: float | None = None

    @property
    def fallback_used(self) -> bool:
        return self.model != self.requested_model

    @property
    def ok(self) -> bool:
        return self.parsed is not None and self.stop_reason not in {"refusal", "max_tokens"}


def build_params(
    settings: ClaudeSettings, *, system: str, user: str, schema: dict[str, Any]
) -> dict[str, Any]:
    """Messages API parameters shared by online calls and batch requests.

    The system block is the cached prefix; the note goes in the user turn after it.
    """
    return {
        "model": settings.model,
        "max_tokens": settings.max_tokens,
        "system": [
            {
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral", "ttl": settings.cache_ttl},
            }
        ],
        "messages": [{"role": "user", "content": user}],
        "output_config": {
            "effort": settings.effort,
            "format": {"type": "json_schema", "schema": schema},
        },
    }


def result_from_message(
    message: Any, *, requested_model: str, latency_s: float | None = None, batch: bool = False
) -> ClaudeResult:
    data = message if isinstance(message, dict) else message.model_dump()
    text = "".join(
        block.get("text", "") for block in data.get("content") or [] if block.get("type") == "text"
    )
    stop_reason = data.get("stop_reason")
    parsed = None
    if stop_reason not in {"refusal", "max_tokens"} and text:
        try:
            parsed = json.loads(text)
        except ValueError:
            parsed = None
    usage = usage_dict(data.get("usage"))
    model = data.get("model") or requested_model
    return ClaudeResult(
        parsed=parsed if isinstance(parsed, dict) else None,
        text=text,
        stop_reason=stop_reason,
        model=model,
        requested_model=requested_model,
        request_id=data.get("id"),
        usage=usage,
        cost_usd=estimate_cost_usd(model, usage, batch=batch),
        latency_s=latency_s,
    )


class ClaudeClient:
    """Online structured-output calls. ``sdk`` may be any object with the SDK's surface."""

    def __init__(self, settings: ClaudeSettings | None = None, *, sdk: Any = None) -> None:
        self.settings = settings or ClaudeSettings.from_env()
        self._sdk = sdk

    @property
    def sdk(self) -> Any:
        if self._sdk is None:
            import anthropic

            self._sdk = anthropic.Anthropic(timeout=self.settings.timeout_s)
        return self._sdk

    def complete_json(self, *, system: str, user: str, schema: dict[str, Any]) -> ClaudeResult:
        assert_egress_allowed(PROVIDER)
        params = build_params(self.settings, system=system, user=user, schema=schema)
        started = time.monotonic()
        try:
            if self.settings.fallbacks:
                stream = self.sdk.beta.messages.stream(
                    **params, betas=[FALLBACK_BETA], fallbacks="default"
                )
            else:
                stream = self.sdk.messages.stream(**params)
            with stream as active:
                message = active.get_final_message()
        except LLMError:
            raise
        except Exception as exc:  # SDK errors carry status/request ids; keep the type name only
            raise LLMError(f"Claude request failed: {type(exc).__name__}: {exc}") from exc
        result = result_from_message(
            message, requested_model=self.settings.model, latency_s=time.monotonic() - started
        )
        logger.info(
            "claude_call model=%s stop=%s fallback=%s in=%s out=%s cache_read=%s cost=%s",
            result.model,
            result.stop_reason,
            result.fallback_used,
            result.usage.get("input_tokens"),
            result.usage.get("output_tokens"),
            result.usage.get("cache_read_input_tokens"),
            None if result.cost_usd is None else round(result.cost_usd, 6),
        )
        return result


__all__ = [
    "ClaudeClient",
    "ClaudeResult",
    "ClaudeSettings",
    "build_params",
    "estimate_cost_usd",
    "result_from_message",
    "usage_dict",
]
