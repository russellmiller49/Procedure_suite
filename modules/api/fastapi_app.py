"""FastAPI application wiring for the Procedure Suite services.

⚠️ SOURCE OF TRUTH: This is the MAIN FastAPI application.
- Running on port 8000 via scripts/devserver.sh
- Uses EnhancedCPTCoder from proc_autocode/coder.py
- DO NOT edit api/app.py - it's deprecated

See AI_ASSISTANT_GUIDE.md for details.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, List

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from modules.api.schemas import (
    CoderRequest,
    CoderResponse,
    KnowledgeMeta,
    RegistryRequest,
    RegistryResponse,
    RenderRequest,
    RenderResponse,
    VerifyRequest,
    VerifyResponse,
)

from modules.common.knowledge import knowledge_hash, knowledge_version
from modules.common.spans import Span
from modules.registry.engine import RegistryEngine
from modules.coder.schema import CodeDecision, CoderOutput
from proc_report import MissingFieldIssue, ProcedureBundle
from proc_report.engine import (
    ReporterEngine,
    apply_bundle_patch,
    apply_patch_result,
    build_procedure_bundle_from_extraction,
    default_schema_registry,
    default_template_registry,
    _load_procedure_order,
)
from proc_report.inference import InferenceEngine
from proc_report.validation import ValidationEngine
from proc_autocode.coder import EnhancedCPTCoder

app = FastAPI(title="Procedure Suite API", version="0.1.0")

# Initialize enhanced coder (singleton)
_enhanced_coder = EnhancedCPTCoder()

app.mount("/ui", StaticFiles(directory="modules/api/static", html=True), name="ui")


class LocalityInfo(BaseModel):
    code: str
    name: str


@app.get("/")
async def root(request: Request) -> Any:
    """Root endpoint with API information or redirect to UI."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return RedirectResponse(url="/ui/")
        
    return {
        "name": "Procedure Suite API",
        "version": "0.2.0",
        "endpoints": {
            "ui": "/ui/",
            "health": "/health",
            "knowledge": "/knowledge",
            "docs": "/docs",
            "redoc": "/redoc",
            "coder": "/v1/coder/run",
            "localities": "/v1/coder/localities",
            "registry": "/v1/registry/run",
            "report_verify": "/report/verify",
            "report_render": "/report/render",
        },
        "note": "Coder now uses EnhancedCPTCoder with RVU calculations and IP knowledge base bundling",
    }


@app.get("/health")
async def health() -> dict[str, bool]:
    return {"ok": True}


@app.get("/knowledge", response_model=KnowledgeMeta)
async def knowledge() -> KnowledgeMeta:
    return KnowledgeMeta(version=knowledge_version() or "unknown", sha256=knowledge_hash() or "")


@app.get("/v1/coder/localities", response_model=List[LocalityInfo])
async def coder_localities() -> List[LocalityInfo]:
    """List available geographic localities for RVU calculation."""
    localities = []
    for code, record in _enhanced_coder.rvu_calc.gpci_data.items():
        localities.append(LocalityInfo(code=code, name=record.locality_name))
    localities.sort(key=lambda x: x.name)
    return localities


@app.post("/v1/coder/run", response_model=CoderResponse)
async def coder_run(req: CoderRequest) -> CoderResponse:
    """Enhanced auto-coding with RVU calculations and bundling rules."""
    procedure_data = {
        "note_text": req.note,
        "locality": req.locality,
        "setting": req.setting,
    }
    
    # Use enhanced coder
    result = _enhanced_coder.code_procedure(procedure_data)
    
    # Convert to CoderOutput format for API compatibility
    codes = []
    for code_data in result.get("codes", []):
        cpt = code_data.get("cpt", "")
        # Get description from RVU data or use a default
        rvu_data = code_data.get("rvu_data") or {}
        description = rvu_data.get("description", "") or f"CPT {cpt}"
        
        codes.append(CodeDecision(
            cpt=cpt,
            description=description,
            modifiers=code_data.get("modifiers", []),
            rationale=f"Detected via IP knowledge base",
            confidence=0.9,
            context={
                "groups": code_data.get("groups", []),
                "rvu_data": code_data.get("rvu_data", {})
            }
        ))
    
    # Build financials summary from enhanced coder result
    financials = None
    if result.get("total_work_rvu") is not None:
        from modules.coder.schema import FinancialSummary, PerCodeBilling
        
        per_code_billing = []
        for code_data in result.get("codes", []):
            rvu_data = code_data.get("rvu_data") or {}
            per_code_billing.append(PerCodeBilling(
                cpt_code=code_data.get("cpt", ""),
                description=rvu_data.get("description", ""),
                modifiers=code_data.get("modifiers", []),
                work_rvu=rvu_data.get("work_rvu", 0.0),
                total_facility_rvu=rvu_data.get("total_rvu", 0.0),
                facility_payment=rvu_data.get("payment", 0.0),
                allowed_facility_rvu=rvu_data.get("work_rvu", 0.0) * rvu_data.get("multiplier", 1.0),
                allowed_facility_payment=rvu_data.get("payment", 0.0) * rvu_data.get("multiplier", 1.0),
            ))
        
        financials = FinancialSummary(
            conversion_factor=1.0,  # Default, could be calculated
            locality=result.get("locality", "00"),
            per_code=per_code_billing,
            total_work_rvu=result.get("total_work_rvu", 0.0),
            total_facility_payment=result.get("estimated_payment", 0.0),
            total_nonfacility_payment=0.0,  # Enhanced coder currently only supports facility
        )
    
    return CoderOutput(
        codes=codes,
        intents=[],  # Enhanced coder doesn't provide intents
        mer_summary=None,  # Could be added later
        financials=financials,
        ncci_actions=[],  # Bundling is handled internally
        warnings=[],
        version="0.2.0",  # Enhanced version
        llm_suggestions=[],  # Enhanced coder doesn't use LLM advisor
        llm_disagreements=[],  # Enhanced coder doesn't use LLM advisor
    )


@app.post("/v1/registry/run", response_model=RegistryResponse)
async def registry_run(req: RegistryRequest) -> RegistryResponse:
    eng = RegistryEngine()
    result = eng.run(req.note, explain=req.explain)
    if isinstance(result, tuple):
        record, evidence = result
    else:
        record, evidence = result, result.evidence

    payload = record.model_dump()
    payload["evidence"] = _serialize_evidence(evidence)
    return RegistryResponse(**payload)


def _verify_bundle(bundle) -> tuple[ProcedureBundle, list[MissingFieldIssue], list[str], list[str], list[str]]:
    templates = default_template_registry()
    schemas = default_schema_registry()
    inference = InferenceEngine()
    inference_result = inference.infer_bundle(bundle)
    bundle = apply_patch_result(bundle, inference_result)
    validator = ValidationEngine(templates, schemas)
    issues = validator.list_missing_critical_fields(bundle)
    warnings = validator.apply_warn_if_rules(bundle)
    suggestions = validator.list_suggestions(bundle)
    return bundle, issues, warnings, suggestions, inference_result.notes


@app.post("/report/verify", response_model=VerifyResponse)
async def report_verify(req: VerifyRequest) -> VerifyResponse:
    bundle = build_procedure_bundle_from_extraction(req.extraction)
    bundle, issues, warnings, suggestions, notes = _verify_bundle(bundle)
    return VerifyResponse(bundle=bundle, issues=issues, warnings=warnings, suggestions=suggestions, inference_notes=notes)


@app.post("/report/render", response_model=RenderResponse)
async def report_render(req: RenderRequest) -> RenderResponse:
    templates = default_template_registry()
    schemas = default_schema_registry()
    bundle = req.bundle
    if req.patch:
        bundle = apply_bundle_patch(bundle, req.patch)
    inference = InferenceEngine()
    inference_result = inference.infer_bundle(bundle)
    bundle = apply_patch_result(bundle, inference_result)
    validator = ValidationEngine(templates, schemas)
    issues = validator.list_missing_critical_fields(bundle)
    warnings = validator.apply_warn_if_rules(bundle)
    suggestions = validator.list_suggestions(bundle)

    engine = ReporterEngine(
        templates,
        schemas,
        procedure_order=_load_procedure_order(),
    )
    structured = engine.compose_report_with_metadata(
        bundle,
        strict=req.strict,
        embed_metadata=req.embed_metadata,
        validation_issues=issues,
        warnings=warnings,
    )
    markdown = structured.text
    return RenderResponse(
        bundle=bundle,
        markdown=markdown,
        issues=issues,
        warnings=warnings,
        inference_notes=inference_result.notes,
        suggestions=suggestions,
    )


def _serialize_evidence(evidence: dict[str, list[Span]] | None) -> dict[str, list[dict[str, Any]]]:
    serialized: dict[str, list[dict[str, Any]]] = {}
    for field, spans in (evidence or {}).items():
        serialized[field] = [_span_to_dict(span) for span in spans]
    return serialized


def _span_to_dict(span: Span) -> dict[str, Any]:
    data = asdict(span)
    return data


__all__ = ["app"]
