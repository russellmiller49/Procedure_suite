"""FastAPI application wiring for the Procedure Suite services."""

from __future__ import annotations

import os
from dataclasses import asdict
from typing import Any, List

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
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

from modules.coder.engine import CoderEngine, _RVU_FILE, _GPCI_FILE
from modules.common.knowledge import knowledge_hash, knowledge_version
from modules.common.spans import Span
from modules.registry.engine import RegistryEngine
from proc_report import MissingFieldIssue, ProcedureBundle
from proc_report.engine import (
    ReporterEngine,
    apply_bundle_patch,
    apply_patch_result,
    apply_warn_if_rules,
    build_procedure_bundle_from_extraction,
    default_schema_registry,
    default_template_registry,
    list_missing_critical_fields,
    _load_procedure_order,
)
from proc_report.inference import InferenceEngine
from proc_autocode.rvu.rvu_calculator import ProcedureRVUCalculator

app = FastAPI(title="Procedure Suite API", version="0.1.0")

_DISABLE_STATIC = os.getenv("DISABLE_STATIC_FILES", "").lower() in ("1", "true", "yes")
if not _DISABLE_STATIC:
    app.mount("/ui", StaticFiles(directory="modules/api/static", html=True), name="ui")
else:
    @app.get("/ui/", include_in_schema=False)
    @app.get("/ui", include_in_schema=False)
    async def ui_stub() -> HTMLResponse:
        """Lightweight fallback UI placeholder to avoid filesystem access in tests."""
        return HTMLResponse("<html><body><h1>Procedure Suite Workbench</h1></body></html>")


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
        "version": "0.1.0",
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
    if _RVU_FILE.exists() and _GPCI_FILE.exists():
        calc = ProcedureRVUCalculator(_RVU_FILE, _GPCI_FILE)
        localities = []
        for code, record in calc.gpci_data.items():
            localities.append(LocalityInfo(code=code, name=record.locality_name))
        localities.sort(key=lambda x: x.name)
        return localities
    return []


@app.post("/v1/coder/run", response_model=CoderResponse)
async def coder_run(req: CoderRequest) -> CoderResponse:
    eng = CoderEngine(allow_weak_sedation_docs=req.allow_weak_sedation_docs)
    return eng.run(
        req.note, 
        explain=req.explain,
        locality=req.locality,
        setting=req.setting
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


def _verify_bundle(bundle) -> tuple[ProcedureBundle, list[MissingFieldIssue], list[str], list[str]]:
    templates = default_template_registry()
    schemas = default_schema_registry()
    inference = InferenceEngine()
    inference_result = inference.infer_bundle(bundle)
    bundle = apply_patch_result(bundle, inference_result)
    issues = list_missing_critical_fields(bundle, template_registry=templates, schema_registry=schemas)
    warnings = apply_warn_if_rules(bundle, template_registry=templates, schema_registry=schemas)
    return bundle, issues, warnings, inference_result.notes


@app.post("/report/verify", response_model=VerifyResponse)
async def report_verify(req: VerifyRequest) -> VerifyResponse:
    bundle = build_procedure_bundle_from_extraction(req.extraction)
    bundle, issues, warnings, notes = _verify_bundle(bundle)
    return VerifyResponse(bundle=bundle, issues=issues, warnings=warnings, inference_notes=notes)


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
    issues = list_missing_critical_fields(bundle, template_registry=templates, schema_registry=schemas)
    warnings = apply_warn_if_rules(bundle, template_registry=templates, schema_registry=schemas)

    markdown = None
    if not any(issue.severity == "critical" for issue in issues):
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
