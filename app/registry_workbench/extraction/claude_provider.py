"""Claude ``ExtractionProvider`` for robotic_ebus_v1 procedure notes.

The shared extraction flow (prompt, repair, assembly, response shape) lives in
``base_provider.LLMRegistryProvider``. This subclass adds the Messages API
parameters shared with the Batch API runner and the batch-result entry point.
"""

from __future__ import annotations

from typing import Any

from ip_registry_contracts.models import ExtractionRequest, ExtractionResponse

from app.common.anthropic_client import ClaudeClient, build_params, result_from_message
from app.registry_workbench.extraction.base_provider import LLMRegistryProvider, repair_message

PROVIDER_NAME = "claude"


class ClaudeRegistryProvider(LLMRegistryProvider):
    provider_name = PROVIDER_NAME

    def __init__(self, client: ClaudeClient | None = None, *, repair: bool = True) -> None:
        super().__init__(client or ClaudeClient(), repair=repair)

    # Shared by online calls and the Batch API runner.
    def build_params(
        self,
        request: ExtractionRequest,
        *,
        previous: dict | None = None,
        errors: list[str] | None = None,
    ) -> dict[str, Any]:
        system, user = self.messages(request, previous=previous, errors=errors)
        return build_params(
            self.client.settings, system=system, user=user, schema=self.spec.schema()
        )

    def response_from_batch(
        self, request: ExtractionRequest, message: Any, *, repair_message_obj: Any = None
    ) -> ExtractionResponse:
        model = self.client.settings.model
        result = result_from_message(message, requested_model=model, batch=True)
        repair_result = (
            result_from_message(repair_message_obj, requested_model=model, batch=True)
            if repair_message_obj is not None
            else None
        )
        return self.response(request, result, repair_result=repair_result)


__all__ = ["ClaudeRegistryProvider", "PROVIDER_NAME", "repair_message"]
