"""
⚠️ DEPRECATED: This FastAPI app is NOT used.

The active FastAPI application is: modules/api/fastapi_app.py
This file exists for reference only. Do not edit or use this file.

See AI_ASSISTANT_GUIDE.md for the current architecture.
"""

from fastapi import FastAPI

from proc_schemas.procedure_report import ProcedureReport
from proc_schemas.billing import BillingResult
from proc_autocode.engine import autocode
from proc_report.engine import compose_report_from_text
from proc_registry.adapter import report_to_registry
from proc_registry.supabase_sink import upsert_bundle
from api.enhanced_coder_routes import router as enhanced_router

app = FastAPI()

app.include_router(enhanced_router)

@app.post("/proc/compose")
def compose(payload: dict):
    report, note_md = compose_report_from_text(payload["text"], payload.get("hints", {}))
    return {"report": report.model_dump(), "note_md": note_md}


@app.post("/proc/autocode")
def code(report: ProcedureReport):
    # Ensure meta has defaults if not provided
    report.meta.setdefault("locality", "00")
    report.meta.setdefault("setting", "facility")
    billing = autocode(report)
    return {"billing": billing.model_dump()}


@app.post("/proc/compose_and_code")
def compose_and_code(payload: dict):
    report, note_md = compose_report_from_text(payload["text"], payload.get("hints", {}))
    
    # Inject locality/setting into report meta for autocode to use
    if "locality" in payload:
        report.meta["locality"] = payload["locality"]
    if "setting" in payload:
        report.meta["setting"] = payload["setting"]
        
    billing = autocode(report)
    return {"report": report.model_dump(), "note_md": note_md, "billing": billing.model_dump()}


@app.post("/proc/upsert")
def upsert(payload: dict):
    bundle = report_to_registry(
        ProcedureReport(**payload["report"]), BillingResult(**payload["billing"])
    )
    upsert_bundle(bundle)
    return {"status": "ok"}
