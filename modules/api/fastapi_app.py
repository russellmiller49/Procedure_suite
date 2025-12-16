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
from contextlib import asynccontextmanager

# Load .env file early so API keys are available
from dotenv import load_dotenv


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


# Prefer explicitly-exported environment variables over values in `.env`.
# Tests can opt out (and avoid accidental real network calls) by setting `PROCSUITE_SKIP_DOTENV=1`.
if not _truthy_env("PROCSUITE_SKIP_DOTENV"):
    load_dotenv(override=False)
import subprocess
import uuid
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from typing import Any, AsyncIterator, List

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Coding entry points:
# - Primary: /api/v1/procedures/{id}/codes/suggest (CodingService, PHI-gated)
# - Legacy shim: /v1/coder/run (non-PHI/synthetic only; blocked when CODER_REQUIRE_PHI_REVIEW=true)

# Import ML Advisor router
from modules.api.ml_advisor_router import router as ml_advisor_router
from modules.api.routes.phi import router as phi_router
from modules.api.routes.procedure_codes import router as procedure_codes_router
from modules.api.routes.metrics import router as metrics_router
from modules.api.routes.phi_demo_cases import router as phi_demo_router
from modules.api.routes_registry import router as registry_extract_router

# All API schemas (base + QA pipeline)
from modules.api.schemas import (
    # Base schemas
    CoderRequest,
    CoderResponse,
    HybridPipelineMetadata,
    KnowledgeMeta,
    QARunRequest,
    RegistryRequest,
    RegistryResponse,
    RenderRequest,
    RenderResponse,
    VerifyRequest,
    VerifyResponse,
    # QA pipeline schemas
    CodeEntry,
    CoderData,
    ModuleResult,
    ModuleStatus,
    QARunResponse,
    RegistryData,
    ReporterData,
)

# QA Pipeline service
from modules.api.services.qa_pipeline import (
    ModuleOutcome,
    QAPipelineResult,
    QAPipelineService,
)
from modules.api.dependencies import get_coding_service, get_qa_pipeline_service

from config.settings import CoderSettings
from modules.coder.schema import CodeDecision, CoderOutput
from modules.common.knowledge import knowledge_hash, knowledge_version
from modules.common.spans import Span
from modules.registry.engine import RegistryEngine

# New architecture imports
from modules.coder.application.coding_service import CodingService
from modules.api.coder_adapter import convert_coding_result_to_coder_output
from modules.coder.phi_gating import is_phi_review_required

from modules.reporting import MissingFieldIssue, ProcedureBundle
from modules.reporting.engine import (
    ReporterEngine,
    _load_procedure_order,
    apply_bundle_patch,
    apply_patch_result,
    build_procedure_bundle_from_extraction,
    default_schema_registry,
    default_template_registry,
)
from modules.reporting.inference import InferenceEngine
from modules.reporting.validation import ValidationEngine


# ============================================================================
# Application Lifespan Context Manager
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan with resource management.

    This replaces the deprecated @app.on_event("startup") pattern.

    Startup:
    - Preloads heavy NLP models to avoid cold-start latency
    - Gracefully handles warmup failures (app still starts)

    Shutdown:
    - Placeholder for cleanup if needed in the future

    Environment variables:
    - PROCSUITE_SKIP_WARMUP: Set to "1", "true", or "yes" to skip warmup entirely
    - RAILWAY_ENVIRONMENT: If set, skips warmup (Railway caches models separately)
    """
    # Import here to avoid circular import at module load time
    from modules.infra.nlp_warmup import (
        should_skip_warmup as _should_skip_warmup,
        warm_heavy_resources as _warm_heavy_resources_fn,
    )

    # Startup phase
    if _should_skip_warmup():
        logging.getLogger(__name__).info(
            "Skipping heavy NLP warmup (disabled via environment)"
        )
    else:
        try:
            await _warm_heavy_resources_fn()
        except Exception as exc:
            logging.getLogger(__name__).error(
                "Heavy NLP warmup failed - starting API without NLP features. "
                "Some endpoints may return errors or degraded results. Error: %s",
                exc,
                exc_info=True,
            )

    # Optional: pull registry model bundle from S3 (does not block startup on failure).
    try:
        from modules.registry.model_bootstrap import ensure_registry_model_bundle

        ensure_registry_model_bundle()
    except Exception as exc:
        logging.getLogger(__name__).warning(
            "Registry model bundle bootstrap skipped/failed: %s", exc
        )

    yield  # Application runs

    # Shutdown phase (cleanup if needed)
    # Currently no cleanup required


app = FastAPI(
    title="Procedure Suite API",
    version="0.3.0",
    lifespan=lifespan,
)

# Include ML Advisor router
app.include_router(ml_advisor_router, prefix="/api/v1", tags=["ML Advisor"])
# Include PHI router
app.include_router(phi_router)
# Include procedure codes router
app.include_router(procedure_codes_router, prefix="/api/v1", tags=["procedure-codes"])
# Metrics router
app.include_router(metrics_router, tags=["metrics"])
# PHI demo cases router (non-PHI metadata)
app.include_router(phi_demo_router)
# Registry extraction router (hybrid-first pipeline)
app.include_router(registry_extract_router, tags=["registry"])

# Skip static file mounting when DISABLE_STATIC_FILES is set (useful for testing)
if os.getenv("DISABLE_STATIC_FILES", "").lower() not in ("true", "1", "yes"):
    # Use absolute path to static directory relative to this file
    static_dir = Path(__file__).parent / "static"
    app.mount("/ui", StaticFiles(directory=str(static_dir), html=True), name="ui")

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


# NOTE: The lifespan context manager is defined above app creation.
# See lifespan() function for startup/shutdown logic.


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
            "registry_extract": "/api/registry/extract",
        },
        "note": "Coder uses CodingService (hexagonal architecture) with smart hybrid policy. ML Advisor endpoints available at /api/v1/ml-advisor/*",
    }


@app.get("/health")
async def health() -> dict[str, bool]:
    return {"ok": True}


@app.get("/health/nlp")
async def nlp_health() -> JSONResponse:
    """Check NLP model readiness.

    Returns 200 OK if NLP models are loaded and ready.
    Returns 503 Service Unavailable if NLP features are degraded.

    This endpoint can be used by load balancers to route requests
    to instances with fully warmed NLP models.
    """
    if is_nlp_warmed():
        return JSONResponse(
            status_code=200,
            content={"status": "ok", "nlp_ready": True},
        )
    return JSONResponse(
        status_code=503,
        content={"status": "degraded", "nlp_ready": False},
    )


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
    """Legacy raw-text coder shim (non-PHI). Use PHI workflow + /api/v1/procedures/{id}/codes/suggest."""
    require_review = is_phi_review_required()
    procedure_id = str(uuid.uuid4())
    report_text = req.note

    # If PHI review is required, reject direct raw text coding
    if require_review:
        raise HTTPException(
            status_code=400,
            detail="Direct coding on raw text is disabled; submit via /v1/phi and review before coding.",
        )

    # Check if ML-first hybrid pipeline is requested
    if req.use_ml_first:
        return await _run_ml_first_pipeline(report_text, req.locality, coding_service)

    # Determine if LLM should be used based on mode
    use_llm = True
    if mode == "rules_only" or req.mode == "rules_only":
        use_llm = False

    # Run the coding pipeline
    result = coding_service.generate_result(
        procedure_id=procedure_id,
        report_text=report_text,
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


async def _run_ml_first_pipeline(
    report_text: str,
    locality: str,
    coding_service: CodingService,
) -> CoderResponse:
    """
    Run the ML-first hybrid pipeline (SmartHybridOrchestrator).

    Uses ternary classification (HIGH_CONF/GRAY_ZONE/LOW_CONF) to decide
    whether to use ML+Rules fast path or LLM fallback.

    Args:
        report_text: The procedure note text
        locality: Geographic locality for RVU calculations
        coding_service: CodingService for KB access and RVU calculation

    Returns:
        CoderResponse with codes and hybrid pipeline metadata
    """
    from modules.coder.application.smart_hybrid_policy import build_hybrid_orchestrator

    # Build orchestrator with default components
    orchestrator = build_hybrid_orchestrator()

    # Run the hybrid pipeline
    result = orchestrator.get_codes(report_text)

    # Build code decisions from orchestrator result
    from modules.coder.schema import CodeDecision

    code_decisions = []
    for cpt in result.codes:
        proc_info = coding_service.kb_repo.get_procedure_info(cpt)
        desc = proc_info.description if proc_info else ""
        code_decisions.append(
            CodeDecision(
                cpt=cpt,
                description=desc,
                confidence=1.0,  # Hybrid pipeline doesn't return per-code confidence
                modifiers=[],
                rationale=f"Source: {result.source}",
            )
        )

    # Calculate RVU/financials if we have codes
    financials = None
    if code_decisions:
        from modules.coder.schema import FinancialSummary, PerCodeBilling

        per_code_billing: list[PerCodeBilling] = []
        total_work_rvu = 0.0
        total_facility_payment = 0.0
        conversion_factor = CoderSettings().cms_conversion_factor

        for cd in code_decisions:
            proc_info = coding_service.kb_repo.get_procedure_info(cd.cpt)
            if proc_info:
                work_rvu = proc_info.work_rvu
                total_rvu = proc_info.total_facility_rvu
                payment = total_rvu * conversion_factor

                total_work_rvu += work_rvu
                total_facility_payment += payment

                per_code_billing.append(PerCodeBilling(
                    cpt_code=cd.cpt,
                    description=cd.description,
                    modifiers=cd.modifiers,
                    work_rvu=work_rvu,
                    total_facility_rvu=total_rvu,
                    facility_payment=payment,
                    allowed_facility_rvu=total_rvu,
                    allowed_facility_payment=payment,
                ))

        if per_code_billing:
            financials = FinancialSummary(
                conversion_factor=conversion_factor,
                locality=locality,
                per_code=per_code_billing,
                total_work_rvu=total_work_rvu,
                total_facility_payment=total_facility_payment,
                total_nonfacility_payment=0.0,
            )

    # Build hybrid pipeline metadata
    hybrid_metadata = HybridPipelineMetadata(
        difficulty=result.difficulty.value,  # Use top-level difficulty attribute
        source=result.source,
        llm_used=result.metadata.get("llm_called", False),
        ml_candidates=result.metadata.get("ml_candidates", []),
        fallback_reason=result.metadata.get("reason_for_fallback"),
        rules_error=result.metadata.get("rules_error"),
    )

    # Build response
    from modules.coder.schema import CoderOutput
    return CoderOutput(
        codes=code_decisions,
        financials=financials,
        warnings=[],
        explanation=None,
        hybrid_metadata=hybrid_metadata.model_dump(),
    )


@app.post("/v1/registry/run", response_model=RegistryResponse)
async def registry_run(req: RegistryRequest) -> RegistryResponse:
    eng = RegistryEngine()
    # For interactive/demo usage, best-effort extraction should return 200 whenever possible.
    # RegistryEngine.run now attempts internal pruning on validation issues; if something still
    # raises, fall back to an empty record rather than failing the request.
    try:
        result = eng.run(req.note, explain=req.explain)
    except Exception as exc:
        _logger.warning("registry_run failed; returning empty record", exc_info=True)
        record = RegistryResponse()
        record.evidence = {}
        return record
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


def _module_status_from_outcome(outcome: ModuleOutcome) -> ModuleStatus:
    """Convert ModuleOutcome to ModuleStatus enum."""
    if outcome.skipped:
        return ModuleStatus.SKIPPED
    if outcome.ok:
        return ModuleStatus.SUCCESS
    return ModuleStatus.ERROR


def _qapipeline_result_to_response(
    result: QAPipelineResult,
    reporter_version: str,
    coder_version: str,
    repo_branch: str | None,
    repo_commit_sha: str | None,
) -> QARunResponse:
    """Convert QAPipelineResult to QARunResponse.

    Handles status aggregation and data transformation for each module.
    """
    # Build registry ModuleResult
    registry_result: ModuleResult[RegistryData] | None = None
    if not result.registry.skipped:
        registry_data = None
        if result.registry.ok and result.registry.data:
            registry_data = RegistryData(
                record=result.registry.data.get("record", {}),
                evidence=result.registry.data.get("evidence", {}),
            )
        registry_result = ModuleResult[RegistryData](
            status=_module_status_from_outcome(result.registry),
            data=registry_data,
            error_message=result.registry.error_message,
            error_code=result.registry.error_code,
        )

    # Build reporter ModuleResult
    reporter_result: ModuleResult[ReporterData] | None = None
    if not result.reporter.skipped:
        reporter_data = None
        if result.reporter.ok and result.reporter.data:
            data = result.reporter.data
            reporter_data = ReporterData(
                markdown=data.get("markdown"),
                bundle=data.get("bundle"),
                issues=data.get("issues", []),
                warnings=data.get("warnings", []),
                procedure_core=data.get("procedure_core"),
                indication=data.get("indication"),
                postop=data.get("postop"),
                fallback_used=data.get("fallback_used", False),
            )
        reporter_result = ModuleResult[ReporterData](
            status=_module_status_from_outcome(result.reporter),
            data=reporter_data,
            error_message=result.reporter.error_message,
            error_code=result.reporter.error_code,
        )

    # Build coder ModuleResult
    coder_result: ModuleResult[CoderData] | None = None
    if not result.coder.skipped:
        coder_data = None
        if result.coder.ok and result.coder.data:
            data = result.coder.data
            codes = [
                CodeEntry(
                    cpt=c.get("cpt", ""),
                    description=c.get("description"),
                    confidence=c.get("confidence"),
                    source=c.get("source"),
                    hybrid_decision=c.get("hybrid_decision"),
                    review_flag=c.get("review_flag", False),
                )
                for c in data.get("codes", [])
            ]
            coder_data = CoderData(
                codes=codes,
                total_work_rvu=data.get("total_work_rvu"),
                estimated_payment=data.get("estimated_payment"),
                bundled_codes=data.get("bundled_codes", []),
                kb_version=data.get("kb_version"),
                policy_version=data.get("policy_version"),
                model_version=data.get("model_version"),
                processing_time_ms=data.get("processing_time_ms"),
            )
        coder_result = ModuleResult[CoderData](
            status=_module_status_from_outcome(result.coder),
            data=coder_data,
            error_message=result.coder.error_message,
            error_code=result.coder.error_code,
        )

    # Compute overall status
    active_results = []
    if registry_result:
        active_results.append(registry_result)
    if reporter_result:
        active_results.append(reporter_result)
    if coder_result:
        active_results.append(coder_result)

    if not active_results:
        overall_status = "completed"
    else:
        successes = sum(1 for r in active_results if r.status == ModuleStatus.SUCCESS)
        failures = sum(1 for r in active_results if r.status == ModuleStatus.ERROR)

        if failures == 0:
            overall_status = "completed"
        elif successes == 0:
            overall_status = "failed"
        else:
            overall_status = "partial_success"

    from modules.registry.model_runtime import get_registry_model_provenance

    model_provenance = get_registry_model_provenance()

    return QARunResponse(
        overall_status=overall_status,
        registry=registry_result,
        reporter=reporter_result,
        coder=coder_result,
        registry_output=(result.registry.data if result.registry.ok else None),
        reporter_output=(result.reporter.data if result.reporter.ok else None),
        coder_output=(result.coder.data if result.coder.ok else None),
        model_backend=model_provenance.backend,
        model_version=model_provenance.version,
        reporter_version=reporter_version,
        coder_version=coder_version,
        repo_branch=repo_branch,
        repo_commit_sha=repo_commit_sha,
    )


@app.post("/qa/run", response_model=QARunResponse)
async def qa_run(
    payload: QARunRequest,
    qa_service: QAPipelineService = Depends(get_qa_pipeline_service),
) -> QARunResponse:
    """
    QA sandbox endpoint: runs reporter, coder, and/or registry on input text.

    This endpoint does NOT persist data - that is handled by the Next.js layer.
    Returns structured outputs with per-module status + version metadata.

    The pipeline runs synchronously in a thread pool to avoid blocking the
    event loop during heavy NLP/ML processing.

    Returns HTTP 200 for all cases (success, partial failure, full failure).
    Check `overall_status` and individual module `status` fields for results.
    """
    branch, commit = _get_git_info()

    # Run pipeline in thread pool to avoid blocking event loop
    result = await run_in_threadpool(
        qa_service.run_pipeline,
        text=payload.note_text,
        modules=payload.modules_run,
        procedure_type=payload.procedure_type,
    )

    # Convert to response format
    return _qapipeline_result_to_response(
        result=result,
        reporter_version=REPORTER_VERSION,
        coder_version=CODER_VERSION,
        repo_branch=branch,
        repo_commit_sha=commit,
    )


__all__ = ["app"]
