"""OpenAI ``ExtractionProvider`` for robotic_ebus_v1 procedure notes.

Shares the prompt, facts schema, repair flow and assembly with the Claude
provider (``base_provider.LLMRegistryProvider``). Online only: no batch path.
"""

from __future__ import annotations

from typing import Any

from ip_registry_contracts.models import ExtractionRequest

from app.common.openai_structured_client import OpenAIStructuredClient, build_params
from app.registry_workbench.extraction.base_provider import LLMRegistryProvider

PROVIDER_NAME = "openai"


class OpenAIRegistryProvider(LLMRegistryProvider):
    provider_name = PROVIDER_NAME

    def __init__(
        self, client: OpenAIStructuredClient | None = None, *, repair: bool = True
    ) -> None:
        super().__init__(client or OpenAIStructuredClient(), repair=repair)

    def build_params(
        self,
        request: ExtractionRequest,
        *,
        previous: dict | None = None,
        errors: list[str] | None = None,
    ) -> dict[str, Any]:
        """Request body for inspection and dry runs; ``extract`` sends the same."""
        system, user = self.messages(request, previous=previous, errors=errors)
        return build_params(
            self.client.settings, system=system, user=user, schema=self.spec.schema()
        )


__all__ = ["OpenAIRegistryProvider", "PROVIDER_NAME"]
