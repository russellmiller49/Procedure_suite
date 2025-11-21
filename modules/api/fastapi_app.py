"""FastAPI application wiring for the Procedure Suite services."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from modules.api.schemas import (
    CoderRequest,
    CoderResponse,
    KnowledgeMeta,
    RegistryRequest,
    RegistryResponse,
    ReporterRequest,
    ReporterResponse,
)
import os

from modules.coder.engine import CoderEngine
from modules.common.knowledge import knowledge_hash, knowledge_version
from modules.common.llm import GeminiLLM, DeterministicStubLLM
from modules.common.spans import Span
from modules.registry.engine import RegistryEngine
from modules.reporter.engine import ReporterEngine

app = FastAPI(title="Procedure Suite API", version="0.1.0")

app.mount("/ui", StaticFiles(directory="modules/api/static", html=True), name="ui")


@app.get("/")
def root(request: Request) -> Any:
    """Root endpoint with API information or redirect to UI."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return RedirectResponse(url="/ui/")
        
    return {
        "name": "Procedure Suite API",
        "version": "0.1.0",
        "endpoints": {
            "ui": "/ui/",
            "health": "/health",
            "knowledge": "/knowledge",
            "gemini": "/gemini/status",
            "docs": "/docs",
            "redoc": "/redoc",
            "coder": "/v1/coder/run",
            "registry": "/v1/registry/run",
            "reporter": "/v1/reporter/generate",
        },
    }


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.get("/knowledge", response_model=KnowledgeMeta)
def knowledge() -> KnowledgeMeta:
    return KnowledgeMeta(version=knowledge_version() or "unknown", sha256=knowledge_hash() or "")


@app.get("/gemini/status")
def gemini_status() -> dict[str, Any]:
    """Diagnostic endpoint to check Gemini API configuration and test connectivity."""
    # Check environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    use_oauth = os.getenv("GEMINI_USE_OAUTH", "").lower() in ("true", "1", "yes")
    configured_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    
    # Determine which LLM would be used
    if use_oauth:
        llm_type = "GeminiLLM (OAuth2)"
        auth_method = "OAuth2/Service Account"
        has_auth = True
    elif api_key:
        llm_type = "GeminiLLM (API Key)"
        auth_method = "API Key"
        has_auth = True
    else:
        llm_type = "DeterministicStubLLM (Fallback)"
        auth_method = "None - No API calls will be made!"
        has_auth = False
    
    # Test actual LLM instance
    try:
        eng = ReporterEngine(model=None)
        actual_llm_type = type(eng.llm).__name__
        is_gemini = isinstance(eng.llm, GeminiLLM)
        is_stub = isinstance(eng.llm, DeterministicStubLLM)
    except Exception as e:
        actual_llm_type = f"Error: {e}"
        is_gemini = False
        is_stub = False
    
    # Test API call if Gemini is configured
    test_result = None
    if has_auth and is_gemini:
        try:
            test_response = eng.llm.generate('{"test": "connection"}')
            if test_response and test_response != "{}":
                test_result = {
                    "status": "success",
                    "message": "Gemini API is responding correctly",
                    "response_preview": test_response[:100] + "..." if len(test_response) > 100 else test_response
                }
            else:
                test_result = {
                    "status": "error",
                    "message": "Gemini API returned empty response"
                }
        except Exception as e:
            test_result = {
                "status": "error",
                "message": f"Gemini API test failed: {str(e)}"
            }
    
    return {
        "configured_llm": llm_type,
        "actual_llm": actual_llm_type,
        "is_gemini": is_gemini,
        "is_stub": is_stub,
        "auth_method": auth_method,
        "model": configured_model,
        "environment": {
            "GEMINI_API_KEY": "***SET***" if api_key else "NOT SET",
            "GEMINI_USE_OAUTH": str(use_oauth),
            "GEMINI_MODEL": configured_model,
            "GOOGLE_APPLICATION_CREDENTIALS": os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or "NOT SET"
        },
        "test_result": test_result,
        "warning": "No API calls are being made - billing will show zero usage!" if is_stub else None
    }


@app.post("/v1/coder/run", response_model=CoderResponse)
def coder_run(req: CoderRequest) -> CoderResponse:
    eng = CoderEngine(allow_weak_sedation_docs=req.allow_weak_sedation_docs)
    return eng.run(req.note, explain=req.explain)


@app.post("/v1/registry/run", response_model=RegistryResponse)
def registry_run(req: RegistryRequest) -> RegistryResponse:
    eng = RegistryEngine()
    result = eng.run(req.note, explain=req.explain)
    if isinstance(result, tuple):
        record, evidence = result
    else:
        record, evidence = result, result.evidence

    payload = record.model_dump()
    payload["evidence"] = _serialize_evidence(evidence)
    return RegistryResponse(**payload)


@app.post("/v1/reporter/generate", response_model=ReporterResponse)
def reporter_generate(req: ReporterRequest) -> ReporterResponse:
    eng = ReporterEngine(model=None)
    struct = eng.from_free_text(req.note)
    struct = eng.validate_and_autofix(struct)
    report = eng.render(struct, template=req.template)
    return ReporterResponse(report=report, struct=struct)


def _serialize_evidence(evidence: dict[str, list[Span]] | None) -> dict[str, list[dict[str, Any]]]:
    serialized: dict[str, list[dict[str, Any]]] = {}
    for field, spans in (evidence or {}).items():
        serialized[field] = [_span_to_dict(span) for span in spans]
    return serialized


def _span_to_dict(span: Span) -> dict[str, Any]:
    data = asdict(span)
    return data


__all__ = ["app"]
