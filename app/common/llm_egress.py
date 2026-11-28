"""Outbound LLM egress gate: note text leaves only when its provenance allows it.

Callers declare what the text is (``egress_context``); LLM clients call
``assert_egress_allowed`` before any request. With no declared context, or text
whose scrubbing failed, nothing is sent.

Policy:
  - ``synthetic``: always allowed (corpus manifests, truth-first generator output).
  - ``scrubbed_verified``: allowed only when ``PROCSUITE_LLM_EGRESS_APPROVED`` is set
    and the provider is listed in ``PROCSUITE_LLM_EGRESS_PROVIDERS``.
  - ``client_asserted``: as above, and additionally ``PROCSUITE_TRUST_CLIENT_SCRUB=1``.
  - ``scrub_failed``: never allowed.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Iterator, Literal

from app.common.exceptions import LLMError
from app.common.logger import get_logger

logger = get_logger("common.llm_egress")

TextState = Literal["synthetic", "scrubbed_verified", "client_asserted", "scrub_failed"]


class EgressDenied(LLMError):
    """The declared text provenance does not permit sending it to this provider."""


@dataclass(frozen=True)
class EgressContext:
    text_state: TextState
    source: str


_CURRENT: ContextVar[EgressContext | None] = ContextVar("llm_egress_context", default=None)


def _truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes"}


def _provider_approved(provider: str) -> bool:
    if not _truthy("PROCSUITE_LLM_EGRESS_APPROVED"):
        return False
    listed = {p.strip().lower() for p in os.getenv("PROCSUITE_LLM_EGRESS_PROVIDERS", "").split(",")}
    return provider.lower() in listed


@contextmanager
def egress_context(text_state: TextState, source: str) -> Iterator[EgressContext]:
    context = EgressContext(text_state=text_state, source=source)
    token = _CURRENT.set(context)
    try:
        yield context
    finally:
        _CURRENT.reset(token)


def current_egress_context() -> EgressContext | None:
    return _CURRENT.get()


def assert_egress_allowed(provider: str) -> EgressContext:
    context = _CURRENT.get()
    if context is None:
        allowed, reason = False, "no_declared_context"
    elif context.text_state == "synthetic":
        allowed, reason = True, "synthetic"
    elif context.text_state == "scrub_failed":
        allowed, reason = False, "scrub_failed"
    elif not _provider_approved(provider):
        allowed, reason = False, "provider_not_approved"
    elif context.text_state == "client_asserted" and not _truthy("PROCSUITE_TRUST_CLIENT_SCRUB"):
        allowed, reason = False, "client_scrub_not_trusted"
    else:
        allowed, reason = True, "approved"
    # Decision metadata only; never the text.
    logger.info(
        "llm_egress provider=%s allowed=%s reason=%s source=%s",
        provider,
        allowed,
        reason,
        context.source if context else None,
    )
    if not allowed:
        raise EgressDenied(f"LLM egress denied for {provider}: {reason}")
    return context  # type: ignore[return-value]


__all__ = [
    "EgressContext",
    "EgressDenied",
    "TextState",
    "assert_egress_allowed",
    "current_egress_context",
    "egress_context",
]
