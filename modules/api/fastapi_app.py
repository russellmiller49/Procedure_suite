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
    QARunRequest,
    QARunResponse,
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
# Enable LLM advisor if CODER_USE_LLM_ADVISOR env var is set
import os
use_llm_advisor = os.getenv("CODER_USE_LLM_ADVISOR", "").lower() in ("true", "1", "yes")
_enhanced_coder = EnhancedCPTCoder(use_llm_advisor=use_llm_advisor)

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
            "qa_run": "/qa/run",
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
async def coder_run(req: CoderRequest, mode: str | None = None) -> CoderResponse:
    """Enhanced auto-coding with RVU calculations and bundling rules."""
    procedure_data = {
        "note_text": req.note,
        "locality": req.locality,
        "setting": req.setting,
        "output_mode": mode or req.mode,
    }
    
    # Use enhanced coder
    result = _enhanced_coder.code_procedure(procedure_data)
    
    # Convert to CoderOutput format for API compatibility
    codes = []
    for code_data in result.get("codes", []):
        cpt = code_data.get("cpt", "")
        # Get description from the code_data (populated by enhanced coder)
        description = code_data.get("description") or f"CPT {cpt}"
        rvu_data = code_data.get("rvu_data") or {}
        rationale_raw = code_data.get("rationale") or ["Detected via IP knowledge base"]
        if isinstance(rationale_raw, list):
            rationale_val = rationale_raw
        else:
            rationale_val = [str(rationale_raw)]

        codes.append(CodeDecision(
            cpt=cpt,
            description=description,
            modifiers=code_data.get("modifiers", []),
            rationale=rationale_val,
            confidence=0.9,
            context={
                "groups": code_data.get("groups", []),
                "rvu_data": rvu_data
            },
            mer_role=code_data.get("mer_role"),
            mer_explanation=code_data.get("mer_explanation"),
            mer_allowed=rvu_data.get("payment") * rvu_data.get("multiplier", 1.0) if rvu_data else None,
        ))
    
    # Build financials summary from enhanced coder result
    financials = None
    if result.get("total_work_rvu") is not None:
        from modules.coder.schema import FinancialSummary, PerCodeBilling
        
        per_code_billing = []
        for code_data in result.get("codes", []):
            rvu_data = code_data.get("rvu_data") or {}
            multiplier = rvu_data.get("multiplier", 1.0)
            mer_role = code_data.get("mer_role")
            payment = rvu_data.get("payment", 0.0)  # Note: key is "payment" not "payment_amount"
            per_code_billing.append(PerCodeBilling(
                cpt_code=code_data.get("cpt", ""),
                description=code_data.get("description") or rvu_data.get("description", ""),
                modifiers=code_data.get("modifiers", []),
                work_rvu=rvu_data.get("work_rvu", 0.0),
                total_facility_rvu=rvu_data.get("total_rvu", 0.0),
                facility_payment=payment,
                allowed_facility_rvu=rvu_data.get("work_rvu", 0.0) * multiplier,
                allowed_facility_payment=payment * multiplier,
                mer_role=mer_role,
                mer_allowed=payment * multiplier if mer_role else None,
                mer_reduction=(1.0 - multiplier) * payment if mer_role == "secondary" else None,
                mp_rule=f"multiple_endoscopy_{mer_role}" if mer_role else None,
            ))
        
        financials = FinancialSummary(
            conversion_factor=1.0,  # Default, could be calculated
            locality=result.get("locality", "00"),
            per_code=per_code_billing,
            total_work_rvu=result.get("total_work_rvu", 0.0),
            total_facility_payment=result.get("estimated_payment", 0.0),
            total_nonfacility_payment=0.0,  # Enhanced coder currently only supports facility
        )
    
    # Extract LLM suggestions and disagreements if available
    llm_suggestions = []
    llm_disagreements = []
    if result.get("llm_suggestions"):
        from modules.coder.schema import LLMCodeSuggestion
        llm_suggestions = [
            LLMCodeSuggestion(
                cpt=s.get("cpt", ""),
                description=s.get("description", ""),
                rationale=s.get("rationale", ""),
            )
            for s in result.get("llm_suggestions", [])
        ]
    if result.get("llm_disagreements"):
        llm_disagreements = result.get("llm_disagreements", [])

    # Convert bundling decisions to BundleDecision format
    from modules.coder.schema import BundleDecision
    ncci_actions = []
    for bundle in result.get("bundled_codes", []):
        ncci_actions.append(BundleDecision(
            pair=(bundle.get("dominant_cpt", ""), bundle.get("bundled_cpt", "")),
            action="bundled",
            reason=bundle.get("reason", ""),
            rule=bundle.get("rule"),
        ))

    return CoderOutput(
        codes=codes,
        intents=[],  # Enhanced coder doesn't provide intents
        mer_summary=None,  # Could be added later
        financials=financials,
        ncci_actions=ncci_actions,  # Bundling decisions with explanations
        warnings=llm_disagreements,  # Include LLM disagreements in warnings
        version="0.2.0",  # Enhanced version
        llm_suggestions=llm_suggestions,
        llm_disagreements=llm_disagreements,
        llm_assistant_payload=result.get("llm_assistant_payload"),
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


# --- QA Sandbox Endpoint ---

def _get_git_info() -> tuple[str | None, str | None]:
    """Extract git branch and commit SHA for version tracking."""
    import subprocess
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return branch, commit
    except Exception:
        return None, None


# Configuration for QA sandbox
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
REPORTER_VERSION = os.getenv("REPORTER_VERSION", "v0.2.0")
CODER_VERSION = os.getenv("CODER_VERSION", "v0.2.0")


@app.post("/qa/run", response_model=QARunResponse)
async def qa_run(payload: QARunRequest) -> QARunResponse:
    """
    QA sandbox endpoint: runs reporter, coder, and/or registry on input text.

    This endpoint does NOT persist data - that is handled by the Next.js layer.
    Returns outputs + version metadata for tracking.
    """
    from fastapi import HTTPException
    from proc_report.engine import compose_report_from_text

    note_text = payload.note_text
    modules_run = payload.modules_run
    procedure_type = payload.procedure_type

    reporter_output = None
    coder_output = None
    registry_output = None
    branch, commit = _get_git_info()

    try:
        # Run registry if requested
        if modules_run in ("registry", "all"):
            eng = RegistryEngine()
            result = eng.run(note_text, explain=True)
            if isinstance(result, tuple):
                record, evidence = result
            else:
                record, evidence = result, getattr(result, 'evidence', {})

            registry_output = {
                "record": record.model_dump() if hasattr(record, 'model_dump') else dict(record),
                "evidence": _serialize_evidence(evidence) if evidence else {},
            }

        # Run reporter if requested
        if modules_run in ("reporter", "all"):
            # Use compose_report_from_text for dictation-style input
            hints = {}
            if procedure_type:
                hints["procedure_type"] = procedure_type

            report, markdown = compose_report_from_text(note_text, hints)
            reporter_output = {
                "markdown": markdown,
                "procedure_core": report.procedure_core.model_dump() if hasattr(report.procedure_core, "model_dump") else {},
                "indication": report.indication,
                "postop": report.postop,
            }

        # Run coder if requested
        if modules_run in ("coder", "all"):
            procedure_data = {
                "note_text": note_text,
                "locality": "00",  # Default locality
                "setting": "facility",
            }
            if procedure_type:
                procedure_data["procedure_type"] = procedure_type

            coder_result = _enhanced_coder.code_procedure(procedure_data)
            coder_output = {
                "codes": coder_result.get("codes", []),
                "total_work_rvu": coder_result.get("total_work_rvu"),
                "estimated_payment": coder_result.get("estimated_payment"),
                "bundled_codes": coder_result.get("bundled_codes", []),
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return QARunResponse(
        reporter_output=reporter_output,
        coder_output=coder_output,
        registry_output=registry_output,
        reporter_version=REPORTER_VERSION,
        coder_version=CODER_VERSION,
        repo_branch=branch,
        repo_commit_sha=commit,
    )


__all__ = ["app"]
