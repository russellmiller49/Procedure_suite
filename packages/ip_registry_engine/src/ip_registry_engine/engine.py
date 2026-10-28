import hashlib
from typing import Protocol

from ip_registry_contracts.models import ExtractionRequest, ExtractionResponse

from .focused import extract_procedure, prepare_text
from .updates import pathology_update, imaging_update, clinical_update


class ExtractionProvider(Protocol):
    def extract(self, request: ExtractionRequest) -> ExtractionResponse: ...


class LocalDeterministicProvider:
    """Local review proposals; missing NER is explicit and never a cloud fallback.

    Compatibility name retained for the original pathology/update provider.
    """

    def __init__(self, model_dir=None):
        self.ner = None
        self.model_error = "model_unavailable"
        if model_dir:
            try:
                from .local_ner import LocalNER

                self.ner = LocalNER(model_dir)
            except (OSError, ValueError, ImportError, KeyError, TypeError, RuntimeError):
                self.model_error = "model_incompatible"

    def extract(self, request: ExtractionRequest) -> ExtractionResponse:
        if hashlib.sha256(request.text.encode()).hexdigest() != request.source_digest:
            raise ValueError("source digest mismatch")
        warnings = ["requires_clinical_review"]
        status = "proposed"
        if request.kind == "procedure":
            inference_error = self.model_error if self.ner is None else None
            try:
                spans = self.ner.predict(prepare_text(request.text)) if self.ner else []
            except (RuntimeError, ValueError, OSError):
                # Preserve bounded review proposals and identify the failed local engine.
                # A failed inference must never look like a successful NER run.
                spans, inference_error = [], "model_inference_failed"
            observations, focused_warnings = extract_procedure(request, spans)
            warnings.extend(focused_warnings)
            if "outside_launch_scope" in focused_warnings:
                status = "unsupported"
            elif "eligibility_requires_review" in focused_warnings:
                status = "degraded"
            elif inference_error:
                status = "degraded"
            if inference_error:
                warnings.append(inference_error)
            observations["inference"] = {
                "deterministic_version": "0.2.0",
                "ner_available": inference_error is None,
                "model_manifest_digest": getattr(self.ner, "manifest_digest", None),
                "clinical_qualification": "pending",
            }
        elif request.kind == "imaging":
            observations = imaging_update(request)
            warnings.append("unresolved_target_attribution")
        elif request.kind == "pathology":
            observations = pathology_update(request)
            warnings.append("unresolved_target_attribution")
        else:
            observations = clinical_update(request)
        return ExtractionResponse(
            job_id=request.job_id,
            source_digest=request.source_digest,
            engine_version="0.2.0",
            status=status,
            observations=observations,
            warnings=warnings,
        )
