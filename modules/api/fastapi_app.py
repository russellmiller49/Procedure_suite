"""FastAPI application wiring for the Procedure Suite services.

⚠️ SOURCE OF TRUTH: This is the MAIN FastAPI application.
- Running on port 8000 via scripts/devserver.sh
- Uses CodingService from modules/coder/application/coding_service.py (new hexagonal architecture)
- DO NOT edit api/app.py - it's deprecated

See AI_ASSISTANT_GUIDE.md for details.
"""

from __future__ import annotations

import logging
import os
import uuid
from dataclasses import asdict
from functools import lru_cache
from typing import Any, List

from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import ML Advisor router
from modules.api.ml_advisor_router import router as ml_advisor_router
from modules.api.routes.phi import router as phi_router
from modules.api.schemas import (
    CoderRequest,
    CoderResponse,
    KnowledgeMeta,
    QARunRequest,
    QARunResponse,
    RegistryRequest,
    RegistryResponse,
    RenderRequest,
    RenderResponse,
    VerifyRequest,
    VerifyResponse,
)
from modules.coder.schema import CodeDecision, CoderOutput
from modules.common.knowledge import knowledge_hash, knowledge_version
from modules.common.spans import Span
from modules.registry.engine import RegistryEngine

# New architecture imports
from modules.coder.application.coding_service import CodingService
from modules.api.dependencies import get_coding_service
from modules.api.coder_adapter import convert_coding_result_to_coder_output

from proc_report import MissingFieldIssue, ProcedureBundle
from proc_report.engine import (
    ReporterEngine,
    _load_procedure_order,
    apply_bundle_patch,
    apply_patch_result,
    build_procedure_bundle_from_extraction,
    default_schema_registry,
    default_template_registry,
)
from proc_report.inference import InferenceEngine
from proc_report.validation import ValidationEngine

app = FastAPI(title="Procedure Suite API", version="0.3.0")

# Include ML Advisor router
app.include_router(ml_advisor_router, prefix="/api/v1", tags=["ML Advisor"])
# Include PHI router
app.include_router(phi_router)

# Skip static file mounting when DISABLE_STATIC_FILES is set (useful for testing)
if os.getenv("DISABLE_STATIC_FILES", "").lower() not in ("true", "1", "yes"):
    app.mount("/ui", StaticFiles(directory="modules/api/static", html=True), name="ui")

# Configure logging
_logger = logging.getLogger(__name__)


# ============================================================================
# Heavy NLP model preloading (delegated to modules.infra.nlp_warmup)
# ============================================================================
from modules.infra.nlp_warmup import (
    should_skip_warmup,
    warm_heavy_resources as _warm_heavy_resources,
    is_nlp_warmed,
    get_spacy_model,
    get_sectionizer,
)


@app.on_event("startup")
async def warm_heavy_resources() -> None:
    """Preload heavy NLP models at startup to avoid cold-start latency.

    This hook is called when the FastAPI app starts. Loading models here
    ensures the first request doesn't incur a long delay waiting for
    model initialization.

    Environment variables:
    - PROCSUITE_SKIP_WARMUP: Set to "1", "true", or "yes" to skip warmup entirely
    - RAILWAY_ENVIRONMENT: If set, skips warmup (Railway caches models separately)

    On failure, the app will still start but NLP features may be degraded.
    """
    if should_skip_warmup():
        _logger.info("Skipping heavy NLP warmup (disabled via environment)")
        return

    try:
        await _warm_heavy_resources()
    except Exception as exc:
        _logger.error(
            "Heavy NLP warmup failed - starting API without NLP features. "
            "Some endpoints may return errors or degraded results. Error: %s",
            exc,
            exc_info=True,
        )


class LocalityInfo(BaseModel):
    code: str
    name: str


@lru_cache(maxsize=1)
def _load_gpci_data() -> dict[str, str]:
    """Load GPCI locality data from CSV file.

    Returns a dict mapping locality codes to locality names.
    """
    import csv
    from pathlib import Path

    gpci_file = Path("data/RVU_files/gpci_2025.csv")
    if not gpci_file.exists():
        gpci_file = Path("proc_autocode/rvu/data/gpci_2025.csv")

    localities: dict[str, str] = {}
    if gpci_file.exists():
        try:
            with gpci_file.open() as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = row.get("mac_locality", row.get("locality_code", ""))
                    name = row.get("locality_name", "")
                    if code and name:
                        localities[code] = name
        except Exception as e:
            _logger.warning(f"Failed to load GPCI data: {e}")

    # Add default national locality if not present
    if "00" not in localities:
        localities["00"] = "National (Default)"

    return localities


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
            "ml_advisor": {
                "health": "/api/v1/ml-advisor/health",
                "status": "/api/v1/ml-advisor/status",
                "code": "/api/v1/ml-advisor/code",
                "code_with_advisor": "/api/v1/ml-advisor/code_with_advisor",
                "suggest": "/api/v1/ml-advisor/suggest",
                "traces": "/api/v1/ml-advisor/traces",
                "metrics": "/api/v1/ml-advisor/metrics",
            },
        },
        "note": "Coder uses CodingService (hexagonal architecture) with smart hybrid policy. ML Advisor endpoints available at /api/v1/ml-advisor/*",
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
    gpci_data = _load_gpci_data()
    localities = [
        LocalityInfo(code=code, name=name)
        for code, name in gpci_data.items()
    ]
    localities.sort(key=lambda x: x.name)
    return localities


@app.post("/v1/coder/run", response_model=CoderResponse)
async def coder_run(
    req: CoderRequest,
    mode: str | None = None,
    coding_service: CodingService = Depends(get_coding_service),
) -> CoderResponse:
    """Auto-coding using CodingService (new hexagonal architecture).

    This endpoint uses CodingService with:
    - Rule-based coding engine
    - Optional LLM advisor (smart hybrid policy)
    - NCCI/MER compliance validation
    - Evidence verification in note text

    Args:
        req: CoderRequest with note text, locality, setting
        mode: Optional output mode override
        coding_service: Injected CodingService instance

    Returns:
        CoderOutput with codes, financials, warnings
    """
    # Generate a procedure ID for this request
    procedure_id = str(uuid.uuid4())

    # Determine if LLM should be used based on mode
    use_llm = True
    if mode == "rules_only" or req.mode == "rules_only":
        use_llm = False

    # Run the coding pipeline
    result = coding_service.generate_result(
        procedure_id=procedure_id,
        report_text=req.note,
        use_llm=use_llm,
        procedure_type=None,  # Auto-detect
    )

    # Convert to legacy CoderOutput format for backward compatibility
    output = convert_coding_result_to_coder_output(
        result=result,
        kb_repo=coding_service.kb_repo,
        locality=req.locality,
    )

    return output


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
    import traceback

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
            try:
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
            except ValueError as ve:
                # Registry validation errors - provide detailed error message
                tb = traceback.format_exc()
                logging.error(f"Registry validation error: {ve}\n{tb}")
                raise HTTPException(
                    status_code=422,
                    detail=f"Registry validation failed: {str(ve)}"
                ) from ve
            except Exception as reg_err:
                # Other registry errors (e.g., missing spaCy model)
                tb = traceback.format_exc()
                logging.error(f"Registry extraction error: {reg_err}\n{tb}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Registry extraction failed: {str(reg_err)}"
                ) from reg_err

        # Run reporter if requested
        if modules_run in ("reporter", "all"):
            try:
                # If we have registry output, use structured reporter for rich output
                if registry_output and registry_output.get("record"):
                    # Build a ProcedureBundle from the registry extraction
                    bundle = build_procedure_bundle_from_extraction(
                        registry_output["record"]
                    )
                    # Run inference to enrich the bundle
                    inference = InferenceEngine()
                    inference_result = inference.infer_bundle(bundle)
                    bundle = apply_patch_result(bundle, inference_result)

                    # Validate and get issues
                    templates = default_template_registry()
                    schemas = default_schema_registry()
                    validator = ValidationEngine(templates, schemas)
                    issues = validator.list_missing_critical_fields(bundle)
                    warnings = validator.apply_warn_if_rules(bundle)

                    # Use the structured ReporterEngine for detailed output
                    engine = ReporterEngine(
                        templates,
                        schemas,
                        procedure_order=_load_procedure_order(),
                    )
                    structured = engine.compose_report_with_metadata(
                        bundle,
                        strict=False,
                        embed_metadata=False,
                        validation_issues=issues,
                        warnings=warnings,
                    )
                    reporter_output = {
                        "markdown": structured.text,
                        "bundle": bundle.model_dump() if hasattr(bundle, "model_dump") else {},
                        "issues": [i.model_dump() for i in issues] if issues else [],
                        "warnings": warnings,
                    }
                else:
                    # No registry data available - run registry extraction first
                    # to get structured procedure data for rich report generation
                    try:
                        reg_eng = RegistryEngine()
                        reg_result = reg_eng.run(note_text, explain=False)
                        if isinstance(reg_result, tuple):
                            reg_record, _ = reg_result
                        else:
                            reg_record = reg_result
                        reg_dict = reg_record.model_dump() if hasattr(reg_record, "model_dump") else {}

                        # Build bundle and generate structured report
                        bundle = build_procedure_bundle_from_extraction(reg_dict)
                        inference = InferenceEngine()
                        inference_result = inference.infer_bundle(bundle)
                        bundle = apply_patch_result(bundle, inference_result)

                        templates = default_template_registry()
                        schemas = default_schema_registry()
                        validator = ValidationEngine(templates, schemas)
                        issues = validator.list_missing_critical_fields(bundle)
                        warnings = validator.apply_warn_if_rules(bundle)

                        engine = ReporterEngine(
                            templates,
                            schemas,
                            procedure_order=_load_procedure_order(),
                        )
                        structured = engine.compose_report_with_metadata(
                            bundle,
                            strict=False,
                            embed_metadata=False,
                            validation_issues=issues,
                            warnings=warnings,
                        )
                        reporter_output = {
                            "markdown": structured.text,
                            "bundle": bundle.model_dump() if hasattr(bundle, "model_dump") else {},
                            "issues": [i.model_dump() for i in issues] if issues else [],
                            "warnings": warnings,
                        }
                    except Exception as reg_fallback_err:
                        # If registry extraction fails, fall back to simple reporter
                        # Log the error for debugging but continue with fallback
                        fallback_tb = traceback.format_exc()
                        logging.warning(
                            f"Reporter auto-registry extraction failed, using simple reporter: "
                            f"{reg_fallback_err}\n{fallback_tb}"
                        )
                        from proc_report.engine import compose_report_from_text

                        hints = {}
                        if procedure_type:
                            hints["procedure_type"] = procedure_type

                        report, markdown = compose_report_from_text(note_text, hints)
                        proc_core = report.procedure_core
                        core_dict = proc_core.model_dump() if hasattr(proc_core, "model_dump") else {}
                        reporter_output = {
                            "markdown": markdown,
                            "procedure_core": core_dict,
                            "indication": report.indication,
                            "postop": report.postop,
                        }
            except Exception as rep_err:
                # Reporter errors (e.g., missing spaCy model)
                tb = traceback.format_exc()
                logging.error(f"Reporter extraction error: {rep_err}\n{tb}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Reporter extraction failed: {str(rep_err)}"
                ) from rep_err

        # Run coder if requested
        if modules_run in ("coder", "all"):
            # Use CodingService from new hexagonal architecture
            coding_service = get_coding_service()
            procedure_id = str(uuid.uuid4())

            result = coding_service.generate_result(
                procedure_id=procedure_id,
                report_text=note_text,
                use_llm=True,
                procedure_type=procedure_type,
            )

            # Convert to output format expected by QA sandbox
            coder_output = {
                "codes": [
                    {
                        "cpt": s.code,
                        "description": s.description,
                        "confidence": s.final_confidence,
                        "source": s.source,
                        "hybrid_decision": s.hybrid_decision,
                        "review_flag": s.review_flag,
                    }
                    for s in result.suggestions
                ],
                "total_work_rvu": None,  # Would need RVU calculation service
                "estimated_payment": None,
                "bundled_codes": [],  # NCCI handled in CodingService
                "kb_version": result.kb_version,
                "policy_version": result.policy_version,
                "model_version": result.model_version,
                "processing_time_ms": result.processing_time_ms,
            }

    except HTTPException:
        # Re-raise HTTP exceptions without wrapping
        raise
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"QA run unexpected error: {e}\n{tb}")
        raise HTTPException(status_code=500, detail=str(e)) from e

    return QARunResponse(
        reporter_output=reporter_output,
        coder_output=coder_output,
        registry_output=registry_output,
        reporter_version=REPORTER_VERSION,
        coder_version=CODER_VERSION,
        repo_branch=branch,
        repo_commit_sha=commit,
    )


from modules.api.routes.procedure_codes import router as procedure_codes_router
from modules.api.routes.metrics import router as metrics_router

app.include_router(procedure_codes_router, prefix="/api/v1", tags=["procedure-codes"])
app.include_router(metrics_router, tags=["metrics"])

__all__ = ["app"]
