"""Provider-neutral result of one schema-constrained LLM call.

``ClaudeResult`` in ``app.common.anthropic_client`` is an alias of this class.
``stop_reason`` uses one vocabulary across providers: ``refusal`` and
``max_tokens`` mean the answer is unusable; other values are provider-specific
(``end_turn`` for Claude, ``completed`` / ``incomplete:<reason>`` / ``failed`` for
OpenAI). ``usage`` keys follow the Anthropic convention: ``input_tokens`` counts
uncached input only, cache reads and writes are separate keys.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

UNUSABLE_STOP_REASONS = frozenset({"refusal", "max_tokens"})


@dataclass
class LLMResult:
    parsed: dict[str, Any] | None
    text: str
    stop_reason: str | None
    model: str
    requested_model: str
    request_id: str | None
    usage: dict[str, int] = field(default_factory=dict)
    cost_usd: float | None = None
    latency_s: float | None = None
    provider: str = "anthropic"

    @property
    def fallback_used(self) -> bool:
        # A dated snapshot of the requested model (``gpt-6.2-sol-2026-09-30``) is
        # the same model, not a fallback.
        return self.model != self.requested_model and not self.model.startswith(
            self.requested_model + "-"
        )

    @property
    def ok(self) -> bool:
        return self.parsed is not None and self.stop_reason not in UNUSABLE_STOP_REASONS


__all__ = ["LLMResult", "UNUSABLE_STOP_REASONS"]
