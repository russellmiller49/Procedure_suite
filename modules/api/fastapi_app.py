"""FastAPI application wiring for the Procedure Suite services.

⚠️ SOURCE OF TRUTH: This is the MAIN FastAPI application.
- Running on port 8000 via scripts/devserver.sh
- Uses CodingService from modules/coder/application/coding_service.py (new hexagonal architecture)
- DO NOT edit api/app.py - it's deprecated

See AI_ASSISTANT_GUIDE.md for details.
"""

from __future__ import annotations

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

# Load .env file early so API keys are available
from dotenv import load_dotenv
import httpx


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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
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
from modules.api.readiness import require_ready
from modules.infra.executors import run_cpu
from modules.api.routes.unified_process import router as unified_process_router

# All API schemas (base + QA pipeline)
from modules.api.schemas import (
    # Base schemas
    CoderRequest,
    CoderResponse,
    CodeSuggestionSummary,
    HybridPipelineMetadata,
    KnowledgeMeta,
    QARunRequest,
    RegistryRequest,
    RegistryResponse,
    RenderRequest,
    RenderResponse,
    UnifiedProcessRequest,
    UnifiedProcessResponse,
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
from modules.api.dependencies import (
    get_coding_service,
    get_qa_pipeline_service,
    get_registry_service,
)
from modules.api.phi_dependencies import get_phi_scrubber
from modules.api.phi_redaction import apply_phi_redaction

from config.settings import CoderSettings
from modules.coder.schema import CodeDecision, CoderOutput
from modules.common.knowledge import knowledge_hash, knowledge_version
from modules.common.exceptions import LLMError
from modules.common.spans import Span
from modules.registry.engine import RegistryEngine
from modules.registry.application.registry_service import RegistryService
from modules.registry.schema import RegistryRecord
from modules.api.normalization import simplify_billing_cpt_codes
from modules.api.routes_registry import _prune_none
from modules.registry.summarize import add_procedure_summaries

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
    - Initializes readiness state (/health vs /ready)
    - Starts heavy model warmup (background by default)

    Shutdown:
    - Placeholder for cleanup if needed in the future

    Environment variables (see modules.infra.settings.InfraSettings):
    - SKIP_WARMUP / PROCSUITE_SKIP_WARMUP: Skip warmup entirely
    - BACKGROUND_WARMUP: Run warmup in the background (default: true)
    - WAIT_FOR_READY_S: Optional await time for readiness gating
    """
    # Import here to avoid circular import at module load time
    from modules.infra.nlp_warmup import (
        should_skip_warmup as _should_skip_warmup,
        warm_heavy_resources_sync as _warm_heavy_resources_sync,
    )
    from modules.infra.settings import get_infra_settings

    settings = get_infra_settings()
    logger = logging.getLogger(__name__)
    from modules.registry.model_runtime import get_registry_runtime_dir, resolve_model_backend

    def _verify_registry_onnx_bundle() -> None:
        if resolve_model_backend() != "onnx":
            return
        runtime_dir = get_registry_runtime_dir()
        model_path = runtime_dir / "registry_model_int8.onnx"
        if not model_path.exists():
            raise RuntimeError(
                f"MODEL_BACKEND=onnx but missing registry model at {model_path}."
            )

    # Readiness state (liveness vs readiness)
    app.state.model_ready = False
    app.state.model_error = None
    app.state.ready_event = asyncio.Event()
    app.state.cpu_executor = ThreadPoolExecutor(max_workers=settings.cpu_workers)
    app.state.llm_sem = asyncio.Semaphore(settings.llm_concurrency)
    app.state.llm_http = httpx.AsyncClient(
        timeout=httpx.Timeout(
            connect=10.0,
            read=float(settings.llm_timeout_s),
            write=30.0,
            pool=30.0,
        )
    )

    # Ensure PHI database tables exist (auto-create on startup)
    try:
        from modules.phi.db import Base as PHIBase
        from modules.api.phi_dependencies import engine as phi_engine
        from modules.phi import models as _phi_models  # noqa: F401 - register models

        PHIBase.metadata.create_all(bind=phi_engine)
        logger.info("PHI database tables verified/created")
    except Exception as e:
        logger.warning(f"Could not initialize PHI tables: {e}")

    _verify_registry_onnx_bundle()

    loop = asyncio.get_running_loop()

    def _warmup_worker() -> None:
        try:
            _warm_heavy_resources_sync()
        except Exception as exc:  # noqa: BLE001
            ok = False
            error = f"{type(exc).__name__}: {exc}"
            logger.error("Warmup failed: %s", error, exc_info=True)
        else:
            ok = True
            error = None
        app.state.model_ready = ok
        app.state.model_error = error
        loop.call_soon_threadsafe(app.state.ready_event.set)

    def _bootstrap_registry_models() -> None:
        # Optional: pull registry model bundle from S3 (does not gate readiness).
        try:
            from modules.registry.model_bootstrap import ensure_registry_model_bundle

            ensure_registry_model_bundle()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Registry model bundle bootstrap skipped/failed: %s", exc)

    # Startup phase
    if settings.skip_warmup or _should_skip_warmup():
        logger.info("Skipping heavy NLP warmup (disabled via environment)")
        app.state.model_ready = True
        app.state.ready_event.set()
    elif settings.background_warmup:
        logger.info("Starting background warmup")
        loop.run_in_executor(app.state.cpu_executor, _warmup_worker)
    else:
        logger.info("Running warmup before serving traffic")
        try:
            await loop.run_in_executor(app.state.cpu_executor, _warm_heavy_resources_sync)
        except Exception as exc:  # noqa: BLE001
            ok = False
            error = f"{type(exc).__name__}: {exc}"
            logger.error("Warmup failed: %s", error, exc_info=True)
        else:
            ok = True
            error = None
        app.state.model_ready = ok
        app.state.model_error = error
        app.state.ready_event.set()

    # Kick off model bundle bootstrap in the background (best-effort).
    loop.run_in_executor(app.state.cpu_executor, _bootstrap_registry_models)

    yield  # Application runs

    # Shutdown phase (cleanup if needed)
    llm_http = getattr(app.state, "llm_http", None)
    if llm_http is not None:
        await llm_http.aclose()

    cpu_executor = getattr(app.state, "cpu_executor", None)
    if cpu_executor is not None:
        cpu_executor.shutdown(wait=False, cancel_futures=True)


app = FastAPI(
    title="Procedure Suite API",
    version="0.3.0",
    lifespan=lifespan,
)

# CORS (dev-friendly defaults)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev: allow all
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def _phi_redactor_headers(request: Request, call_next):
    """
    Ensure the PHI redactor UI (including /vendor/* model assets) works in
    cross-origin isolated contexts and when embedded/loaded from other origins
    during development.
    """
    resp = await call_next(request)
    path = request.url.path
    if path.startswith("/ui/phi_redactor"):
        # Required for SharedArrayBuffer in modern browsers (cross-origin isolation).
        resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        resp.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        # Allow these assets to be requested as subresources in COEP contexts.
        resp.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        # Dev convenience: make vendor assets fetchable from any origin.
        # (CORSMiddleware adds CORS headers when an Origin header is present,
        # but some contexts can still surface this as a "CORS error" without it.)
        resp.headers.setdefault("Access-Control-Allow-Origin", "*")
        resp.headers.setdefault("Access-Control-Allow-Methods", "*")
        resp.headers.setdefault("Access-Control-Allow-Headers", "*")
        # Chrome Private Network Access (PNA): when the UI is loaded from a
        # "public" secure context (e.g., an https webview) and it fetches
        # localhost resources, Chrome sends a preflight with
        # Access-Control-Request-Private-Network: true and expects this header.
        if request.headers.get("access-control-request-private-network", "").lower() == "true":
            resp.headers["Access-Control-Allow-Private-Network"] = "true"
        # Avoid stale caching during rapid iteration/debugging.
        resp.headers.setdefault("Cache-Control", "no-store")
    return resp

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
# Unified process router (UI entry point)
app.include_router(unified_process_router, prefix="/api")

def _phi_redactor_response(path: Path) -> FileResponse:
    resp = FileResponse(path)
    # Required for SharedArrayBuffer in modern browsers (cross-origin isolation).
    resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    resp.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    # Avoid stale client-side caching during rapid iteration/debugging.
    resp.headers["Cache-Control"] = "no-store"
    return resp


def _phi_redactor_static_dir() -> Path:
    return Path(__file__).parent / "static" / "phi_redactor"


def _static_files_enabled() -> bool:
    return os.getenv("DISABLE_STATIC_FILES", "").lower() not in ("true", "1", "yes")


@app.get("/ui/phi_redactor")
def phi_redactor_redirect() -> RedirectResponse:
    # Avoid "/ui/phi_redactor" being treated as a file path in the browser (breaks relative URLs).
    # Redirect ensures relative module imports resolve to "/ui/phi_redactor/...".
    resp = RedirectResponse(url="/ui/phi_redactor/")
    resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    resp.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.get("/ui/phi_redactor/")
def phi_redactor_index() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    index_path = _phi_redactor_static_dir() / "index.html"
    return _phi_redactor_response(index_path)


@app.get("/ui/phi_redactor/index.html")
def phi_redactor_index_html() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    index_path = _phi_redactor_static_dir() / "index.html"
    return _phi_redactor_response(index_path)


@app.get("/ui/phi_redactor/app.js")
def phi_redactor_app_js() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    return _phi_redactor_response(_phi_redactor_static_dir() / "app.js")


@app.get("/ui/phi_redactor/redactor.worker.js")
def phi_redactor_worker_js() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    return _phi_redactor_response(_phi_redactor_static_dir() / "redactor.worker.js")


@app.get("/ui/phi_redactor/styles.css")
def phi_redactor_styles_css() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    return _phi_redactor_response(_phi_redactor_static_dir() / "styles.css")


@app.get("/ui/phi_redactor/allowlist_trie.json")
def phi_redactor_allowlist() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    return _phi_redactor_response(_phi_redactor_static_dir() / "allowlist_trie.json")


@app.get("/ui/phi_redactor/sw.js")
def phi_redactor_sw() -> FileResponse:
    if not _static_files_enabled():
        raise HTTPException(status_code=404, detail="Static files disabled")
    return _phi_redactor_response(_phi_redactor_static_dir() / "sw.js")

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
        "version": "0.3.0",
        "endpoints": {
            "ui": "/ui/",
            "health": "/health",
            "ready": "/ready",
            "knowledge": "/knowledge",
            "docs": "/docs",
            "redoc": "/redoc",
            "unified_process": "/api/v1/process",  # NEW: Combined registry + coder
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
        "note": "Use /api/v1/process for extraction-first pipeline (registry → CPT codes in one call). Legacy endpoints /v1/coder/run and /v1/registry/run still available.",
    }


@app.get("/health")
async def health(request: Request) -> dict[str, bool]:
    return {"ok": True, "ready": bool(getattr(request.app.state, "model_ready", False))}


@app.get("/ready")
async def ready(request: Request) -> JSONResponse:
    is_ready = bool(getattr(request.app.state, "model_ready", False))
    if is_ready:
        return JSONResponse(status_code=200, content={"status": "ok", "ready": True})

    model_error = getattr(request.app.state, "model_error", None)
    content: dict[str, Any] = {"status": "warming", "ready": False}
    if model_error:
        content["status"] = "error"
        content["error"] = str(model_error)
        return JSONResponse(status_code=503, content=content)

    return JSONResponse(status_code=503, content=content, headers={"Retry-After": "10"})


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
    request: Request,
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
        return await _run_ml_first_pipeline(request, report_text, req.locality, coding_service)

    # Determine if LLM should be used based on mode
    use_llm = True
    if mode == "rules_only" or req.mode == "rules_only":
        use_llm = False

    # Run the coding pipeline
    result = await run_cpu(
        request.app,
        coding_service.generate_result,
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
    request: Request,
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

    def _run_hybrid() -> Any:
        orchestrator = build_hybrid_orchestrator()
        return orchestrator.get_codes(report_text)

    result = await run_cpu(request.app, _run_hybrid)

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


@app.post(
    "/v1/registry/run",
    response_model=RegistryResponse,
    response_model_exclude_none=True,
)
async def registry_run(
    req: RegistryRequest,
    request: Request,
    _ready: None = Depends(require_ready),
    phi_scrubber=Depends(get_phi_scrubber),
) -> RegistryResponse:
    # Early PHI redaction - scrub once at entry
    redaction = apply_phi_redaction(req.note, phi_scrubber)
    note_text = redaction.text

    eng = RegistryEngine()
    result = await run_cpu(request.app, eng.run, note_text, explain=req.explain)
    if isinstance(result, tuple):
        record, evidence = result
    else:
        record, evidence = result, getattr(result, "evidence", {})

    payload = _shape_registry_payload(record, evidence)
    return JSONResponse(content=payload)


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
        cleaned: list[dict[str, Any]] = []
        for span in spans or []:
            if span is None:
                continue
            cleaned.append(_prune_none(_span_to_dict(span)))
        if cleaned:
            serialized[field] = cleaned
    return serialized


def _span_to_dict(span: Span) -> dict[str, Any]:
    data = asdict(span)
    return data


def _shape_registry_payload(record: RegistryRecord, evidence: dict[str, list[Span]] | None) -> dict[str, Any]:
    """Convert a registry record + evidence into a JSON-safe, null-pruned payload."""
    payload = _prune_none(record.model_dump(exclude_none=True))

    # Optional UI-friendly enrichments
    simplify_billing_cpt_codes(payload)
    add_procedure_summaries(payload)

    payload["evidence"] = _serialize_evidence(evidence)
    return payload


# --- Unified Process Endpoint (Extraction-First) ---

@app.post("/api/v1/process", response_model=UnifiedProcessResponse)
async def unified_process(
    req: UnifiedProcessRequest,
    request: Request,
    _ready: None = Depends(require_ready),
    registry_service: RegistryService = Depends(get_registry_service),
    coding_service: CodingService = Depends(get_coding_service),
    phi_scrubber=Depends(get_phi_scrubber),
) -> UnifiedProcessResponse:
    """Unified endpoint combining registry extraction and CPT code derivation.

    This endpoint implements the extraction-first pipeline:
    1. Extracts structured registry fields from the procedure note
    2. Derives CPT codes deterministically from the registry fields
    3. Optionally calculates RVU/payment information

    Returns both registry data and derived CPT codes in a single response,
    making it ideal for production use where both outputs are needed.

    This replaces the need to call /v1/registry/run and /v1/coder/run separately.
    """
    import time
    from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
    from config.settings import CoderSettings

    start_time = time.time()

    if req.already_scrubbed:
        note_text = req.note
    else:
        # Early PHI redaction - scrub once at entry, use scrubbed text downstream
        redaction = apply_phi_redaction(req.note, phi_scrubber)
        note_text = redaction.text

    # Step 1: Registry extraction
    try:
        extraction_result = await run_cpu(request.app, registry_service.extract_fields, note_text)
    except httpx.HTTPStatusError as exc:
        if exc.response is not None and exc.response.status_code == 429:
            retry_after = exc.response.headers.get("Retry-After") or "10"
            raise HTTPException(
                status_code=503,
                detail="Upstream LLM rate limited",
                headers={"Retry-After": str(retry_after)},
            ) from exc
        raise
    except LLMError as exc:
        if "429" in str(exc):
            raise HTTPException(
                status_code=503,
                detail="Upstream LLM rate limited",
                headers={"Retry-After": "10"},
            ) from exc
        raise

    # Step 2: Derive CPT codes from registry
    record = extraction_result.record
    if record is None:
        from modules.registry.schema import RegistryRecord
        record = RegistryRecord.model_validate(extraction_result.mapped_fields)

    codes, rationales, derivation_warnings = derive_all_codes_with_meta(record)

    # Build suggestions with confidence and rationale
    suggestions = []
    base_confidence = 0.95 if extraction_result.coder_difficulty == "HIGH_CONF" else 0.80

    for code in codes:
        proc_info = coding_service.kb_repo.get_procedure_info(code)
        description = proc_info.description if proc_info else ""
        rationale = rationales.get(code, "")

        # Determine review flag
        if extraction_result.needs_manual_review:
            review_flag = "required"
        elif extraction_result.audit_warnings:
            review_flag = "recommended"
        else:
            review_flag = "optional"

        suggestions.append(CodeSuggestionSummary(
            code=code,
            description=description,
            confidence=base_confidence,
            rationale=rationale,
            review_flag=review_flag,
        ))

    # Step 3: Calculate financials if requested
    total_work_rvu = None
    estimated_payment = None
    per_code_billing = []

    if req.include_financials and codes:
        settings = CoderSettings()
        conversion_factor = settings.cms_conversion_factor
        total_work = 0.0
        total_payment = 0.0

        for code in codes:
            proc_info = coding_service.kb_repo.get_procedure_info(code)
            if proc_info:
                work_rvu = proc_info.work_rvu
                total_rvu = proc_info.total_facility_rvu
                payment = total_rvu * conversion_factor

                total_work += work_rvu
                total_payment += payment

                per_code_billing.append({
                    "cpt_code": code,
                    "description": proc_info.description,
                    "work_rvu": work_rvu,
                    "total_facility_rvu": total_rvu,
                    "facility_payment": round(payment, 2),
                })

        total_work_rvu = round(total_work, 2)
        estimated_payment = round(total_payment, 2)

    # Combine audit warnings
    all_warnings = list(extraction_result.audit_warnings or [])
    all_warnings.extend(derivation_warnings)

    processing_time_ms = (time.time() - start_time) * 1000

    # Build response
    registry_payload = _prune_none(record.model_dump(exclude_none=True))
    evidence_payload = {}
    if req.explain and hasattr(extraction_result, 'evidence'):
        evidence_payload = _serialize_evidence(getattr(extraction_result, 'evidence', {}))

    return UnifiedProcessResponse(
        registry=registry_payload,
        evidence=evidence_payload,
        cpt_codes=codes,
        suggestions=suggestions,
        total_work_rvu=total_work_rvu,
        estimated_payment=estimated_payment,
        per_code_billing=per_code_billing,
        pipeline_mode="extraction_first",
        coder_difficulty=extraction_result.coder_difficulty or "",
        needs_manual_review=extraction_result.needs_manual_review,
        audit_warnings=all_warnings,
        validation_errors=extraction_result.validation_errors or [],
        kb_version=coding_service.kb_repo.version,
        policy_version="extraction_first_v1",
        processing_time_ms=round(processing_time_ms, 2),
    )


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
    request: Request,
    _ready: None = Depends(require_ready),
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

    result = await run_cpu(
        request.app,
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
