import hashlib
from typing import Protocol

from ip_registry_contracts.models import ExtractionRequest, ExtractionResponse

from .aggregation.clinical.extract_clinical_update import extract_clinical_update_event
from .aggregation.pathology.extract_pathology import extract_pathology_event


class ExtractionProvider(Protocol):
    def extract(self, request: ExtractionRequest) -> ExtractionResponse: ...


class LocalDeterministicProvider:
    """Reviewed suggestions only. The complete procedure/NER engine is not qualified here."""

    def extract(self, request: ExtractionRequest) -> ExtractionResponse:
        if hashlib.sha256(request.text.encode()).hexdigest() != request.source_digest:
            raise ValueError("source digest mismatch")
        if request.kind == "pathology":
            observations = extract_pathology_event(request.text)
        else:
            observations = extract_clinical_update_event(
                request.text, update_type="follow_up", relative_day_offset=None
            )
        return ExtractionResponse(
            job_id=request.job_id, source_digest=request.source_digest, engine_version="0.1.0",
            status="proposed", observations=observations,
            warnings=["requires_clinical_review", "full_procedure_engine_unqualified"],
        )
