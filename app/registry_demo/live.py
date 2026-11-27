"""Live reading of a tester's own note.

The note arrives already redacted in the tester's browser. It is read in memory and
returned; nothing here stores it, caches it or writes any of its text to a log.

The rules engine always reads the note on this server. The model reads it too when
a key is configured, today's spend cap has room, and the egress gate allows the kind
of text the tester declared:

- ``synthetic``      always allowed
- ``real_redacted``  only when the server owner has set the egress approval switches
  (``PROCSUITE_LLM_EGRESS_APPROVED``, ``PROCSUITE_LLM_EGRESS_PROVIDERS``,
  ``PROCSUITE_TRUST_CLIENT_SCRUB``); otherwise the text never leaves this server

When the model is not used the response says why, and the rules-engine reading is
what the tester reviews.
"""

from __future__ import annotations

import hashlib
import hmac
import threading
from typing import Any
from uuid import uuid4

from ip_registry_contracts.models import ExtractionRequest
from ip_registry_engine.engine import LocalDeterministicProvider

from app.common.exceptions import LLMError
from app.common.llm_egress import EgressDenied, assert_egress_allowed, egress_context
from app.common.logger import get_logger
from app.registry_demo import budget, settings
from app.registry_demo.errors import DemoError

logger = get_logger("registry_demo.live")

NOTE_KINDS = ("synthetic", "real_redacted")
FAILED_CODES = budget.RateLimit(limit=8, window_s=600)
LIVE_REQUESTS = budget.RateLimit(limit=6, window_s=60)
_MODEL_SLOTS = threading.BoundedSemaphore(2)

# Errors raised before the model produced anything: no spend to record.
_NO_SPEND_ERRORS = (
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "BadRequestError",
    "APIConnectionError",
    "RateLimitError",
    "EgressDenied",
)
READER_MESSAGES = {
    "model_not_configured": (
        "The model reader is not set up on this server. This note was read by the rules "
        "engine only."
    ),
    "real_notes_not_approved": (
        "Real redacted notes are not approved for the model on this server. This note was "
        "read by the rules engine on this server only and was sent nowhere else."
    ),
    "daily_cap_reached": (
        "Today's model budget is used up. This note was read by the rules engine only."
    ),
    "model_call_failed": (
        "The model did not return a result. This note was read by the rules engine only."
    ),
    "model_no_result": (
        "The model returned nothing usable for this note. Shown here is the rules-engine "
        "reading."
    ),
}


def check_code(code: str | None, client: str) -> None:
    """Raise unless ``code`` is one of the configured tester passwords."""
    if not settings.live_extraction_enabled():
        raise DemoError(403, "tester_access_off", "Tester access is not switched on here.")
    if FAILED_CODES.blocked(client):
        raise DemoError(429, "too_many_attempts", "Too many wrong passwords. Try again later.")
    given = (code or "").strip().encode()
    matched = False
    for known in settings.access_codes():
        matched |= hmac.compare_digest(given, known.encode())
    if not matched:
        FAILED_CODES.record(client)
        raise DemoError(401, "bad_access_code", "That tester password is not recognised.")


def describe() -> dict[str, Any]:
    """What an unlocked tester is told about this server's reader."""
    from app.common.anthropic_client import ClaudeSettings

    claude = ClaudeSettings.from_env()
    return {
        "model_configured": settings.model_configured(),
        "real_notes_to_model": settings.real_notes_to_model(),
        "model": claude.model,
        "effort": claude.effort,
        "provider": "Anthropic",
        "max_text_chars": settings.MAX_TEXT_CHARS,
    }


def _request(text: str) -> ExtractionRequest:
    return ExtractionRequest(
        job_id=uuid4(),
        source_document_id=uuid4(),
        source_digest=hashlib.sha256(text.encode()).hexdigest(),
        text=text,
        kind="procedure",
    )


def _model_reading(text: str) -> tuple[dict[str, Any] | None, str | None]:
    """(model response, reason it is missing). The caller holds the egress context."""
    from app.common.anthropic_client import ClaudeClient, ClaudeSettings
    from app.registry_workbench.extraction.claude_provider import ClaudeRegistryProvider

    if not _MODEL_SLOTS.acquire(blocking=False):
        raise DemoError(429, "busy", "Other notes are being read right now. Try again shortly.")
    try:
        hold = settings.reserve_usd()
        if not budget.reserve(hold):
            return None, "daily_cap_reached"
        cost: float | None = None  # unknown cost is charged as the whole hold
        try:
            client = ClaudeClient(ClaudeSettings.from_env(timeout_s=settings.timeout_s()))
            response = ClaudeRegistryProvider(client).extract(_request(text))
            dumped = response.model_dump(mode="json")
            cost = ((dumped.get("observations") or {}).get("inference") or {}).get("cost_usd")
        except LLMError as exc:
            kind = str(exc).split(":")[1].strip() if str(exc).count(":") else type(exc).__name__
            if kind in _NO_SPEND_ERRORS or isinstance(exc, EgressDenied):
                cost = 0.0
            # The error type only: a provider message can quote part of a request.
            logger.warning("demo live model_call_failed type=%s", kind)
            return None, "model_call_failed"
        finally:
            budget.settle(hold, cost)
    finally:
        _MODEL_SLOTS.release()
    if not (dumped.get("observations") or {}).get("proposal"):
        return dumped, "model_no_result"
    return dumped, None


def read_note(
    text: str, *, note_kind: str
) -> tuple[dict[str, Any] | None, dict[str, Any], dict[str, Any]]:
    """Read one redacted note: (model response or None, rules response, reader summary)."""
    rules = LocalDeterministicProvider().extract(_request(text)).model_dump(mode="json")
    model: dict[str, Any] | None = None
    reason: str | None
    if not settings.model_configured():
        reason = "model_not_configured"
    else:
        state = "synthetic" if note_kind == "synthetic" else "client_asserted"
        with egress_context(state, source=f"demo:live:{note_kind}"):  # type: ignore[arg-type]
            try:
                assert_egress_allowed(settings.EGRESS_PROVIDER)
            except EgressDenied:
                reason = "real_notes_not_approved"
            else:
                model, reason = _model_reading(text)
    reader = {
        "model_used": reason is None,
        "sent_to_provider": reason in (None, "model_no_result", "model_call_failed"),
        "reason": reason,
        "message": READER_MESSAGES.get(reason or ""),
    }
    return model, rules, reader


__all__ = [
    "FAILED_CODES",
    "LIVE_REQUESTS",
    "NOTE_KINDS",
    "READER_MESSAGES",
    "check_code",
    "describe",
    "read_note",
]
