"""Claude ``ExtractionProvider`` for robotic_ebus_v1 procedure notes.

Same request/response contract and proposal shape as the local deterministic
engine, so review tooling and the evaluation scorers work on either. Lives in
``app/`` and never in the vendored packages: the clinical worker is local-only.

The caller declares text provenance with ``app.common.llm_egress.egress_context``;
this provider never asserts it on the caller's behalf. Pathology, imaging and
clinical-update documents are delegated to the local engine for now.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from app.common.anthropic_client import (
    ClaudeClient,
    ClaudeResult,
    build_params,
    result_from_message,
)
from app.llm_extraction.facts_schema import schema_digest
from app.registry_workbench.extraction.assembler import Assembler, Assembly
from app.registry_workbench.extraction.contract_spec import contract_spec, dictionary
from app.registry_workbench.extraction.prompt import (
    PROMPT_VERSION,
    prompt_digest,
    system_prompt,
    user_message,
)
from ip_registry_contracts.models import ExtractionRequest, ExtractionResponse
from ip_registry_engine.engine import LocalDeterministicProvider
from ip_registry_engine.focused import prepare_text

PROVIDER_NAME = "claude"


def repair_message(prepared_text: str, previous: dict[str, Any], errors: list[str]) -> str:
    return (
        user_message(prepared_text)
        + "\n\nA previous answer for this document failed registry validation."
        + f"\n<previous_answer>\n{json.dumps(previous, sort_keys=True)}\n</previous_answer>"
        + f"\n<validation_errors>\n{chr(10).join(sorted(set(errors)))}\n</validation_errors>"
        + "\nReturn a corrected, complete answer."
    )


class ClaudeRegistryProvider:
    def __init__(self, client: ClaudeClient | None = None, *, repair: bool = True) -> None:
        self.client = client or ClaudeClient()
        self.repair = repair
        self.spec = contract_spec()

    # Shared by online calls and the Batch API runner.
    def build_params(self, request: ExtractionRequest, *, previous: dict | None = None, errors: list[str] | None = None) -> dict[str, Any]:
        prepared = prepare_text(request.text)
        user = repair_message(prepared, previous, errors or []) if previous is not None else user_message(prepared)
        return build_params(self.client.settings, system=system_prompt(), user=user, schema=self.spec.schema())

    def _assemble(self, request: ExtractionRequest, facts: dict[str, Any], model: str) -> Assembly:
        return Assembler(
            source_text=request.text,
            prepared_text=prepare_text(request.text),
            source_document_id=str(request.source_document_id),
            source_digest=request.source_digest,
            extractor_version=f"{model}/{PROMPT_VERSION}",
        ).assemble(facts)

    def _call(self, request: ExtractionRequest, **kwargs: Any) -> ClaudeResult:
        params = self.build_params(request, **kwargs)
        return self.client.complete_json(
            system=params["system"][0]["text"],
            user=params["messages"][0]["content"],
            schema=self.spec.schema(),
        )

    def response(
        self,
        request: ExtractionRequest,
        result: ClaudeResult,
        *,
        repair_result: ClaudeResult | None = None,
        first_assembly: Assembly | None = None,
    ) -> ExtractionResponse:
        """Build the response from completed call(s); used by online and batch paths."""
        settings = self.client.settings
        calls = [r for r in (result, repair_result) if r is not None]
        final = repair_result if repair_result is not None and repair_result.ok else result
        assembly = None
        if final.ok:
            assembly = (
                first_assembly
                if final is result and first_assembly is not None
                else self._assemble(request, final.parsed or {}, final.model)
            )
        warnings = ["requires_clinical_review", "full_procedure_engine_unqualified"]
        if assembly is None:
            status, signal = "degraded", "failed"
            warnings.append("model_inference_failed")
        elif assembly.errors == ["no_procedure_component"]:
            status, signal = "unsupported", "completed"
            warnings.append("outside_launch_scope")
        elif not assembly.valid:
            status, signal = "degraded", "completed"
        elif not assembly.has_started_component:
            status, signal = "degraded", "completed"
            warnings.append("eligibility_requires_review")
        else:
            status, signal = "proposed", "completed"
        cost = [r.cost_usd for r in calls if r.cost_usd is not None]
        observations: dict[str, Any] = {
            "proposal": assembly.proposal if assembly else None,
            "quality_signals": [
                {"phase": "llm_extraction", "status": signal, "stop_reason": final.stop_reason},
                {
                    "phase": "contract_validation",
                    "status": "passed" if assembly and assembly.valid else "failed",
                    "errors": assembly.errors if assembly else [],
                },
                {"phase": "approval_checks", "errors": assembly.approval_errors if assembly else []},
            ],
            "unresolved_mentions": assembly.unresolved if assembly else [],
            "assembly_stats": assembly.stats if assembly else {},
            "event_date_candidate": None,
            "inference": {
                "provider": PROVIDER_NAME,
                "requested_model": settings.model,
                "model": final.model,
                "fallback_used": final.fallback_used,
                "effort": settings.effort,
                "prompt_version": PROMPT_VERSION,
                "prompt_digest": prompt_digest(),
                "schema_digest": schema_digest(self.spec.schema()),
                "dictionary_sha256": dictionary().get("source_sha256"),
                "request_ids": [r.request_id for r in calls],
                "repair_used": repair_result is not None,
                "usage": [r.usage for r in calls],
                "cost_usd": round(sum(cost), 6) if cost else None,
                "latency_s": round(sum(r.latency_s or 0 for r in calls), 3),
                "clinical_qualification": "pending",
            },
        }
        return ExtractionResponse(
            job_id=request.job_id,
            source_digest=request.source_digest,
            status=status,
            observations=observations,
            warnings=sorted(set(warnings)),
        )

    def needs_repair(self, request: ExtractionRequest, result: ClaudeResult) -> tuple[Assembly | None, list[str]]:
        if not result.ok:
            return None, []
        assembly = self._assemble(request, result.parsed or {}, result.model)
        if assembly.valid or assembly.errors == ["no_procedure_component"]:
            return assembly, []
        return assembly, assembly.errors

    def extract(self, request: ExtractionRequest) -> ExtractionResponse:
        if hashlib.sha256(request.text.encode()).hexdigest() != request.source_digest:
            raise ValueError("source digest mismatch")
        if request.kind != "procedure":
            return LocalDeterministicProvider().extract(request)
        result = self._call(request)
        assembly, errors = self.needs_repair(request, result)
        repair_result = None
        if errors and self.repair:
            repair_result = self._call(request, previous=result.parsed, errors=errors)
        return self.response(request, result, repair_result=repair_result, first_assembly=assembly)

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
