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
from modules.coder.engine import CoderEngine
from modules.common.knowledge import knowledge_hash, knowledge_version
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
