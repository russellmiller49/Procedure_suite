from fastapi import FastAPI

from proc_schemas.procedure_report import ProcedureReport
from proc_schemas.billing import BillingResult
from proc_autocode.engine import autocode
from proc_report.engine import compose_report_from_text
from proc_registry.adapter import report_to_registry
from proc_registry.supabase_sink import upsert_bundle

app = FastAPI()


@app.post("/proc/compose")
def compose(payload: dict):
    report, note_md = compose_report_from_text(payload["text"], payload.get("hints", {}))
    return {"report": report.model_dump(), "note_md": note_md}


@app.post("/proc/autocode")
def code(report: ProcedureReport):
    billing = autocode(report)
    return {"billing": billing.model_dump()}


@app.post("/proc/compose_and_code")
def compose_and_code(payload: dict):
    report, note_md = compose_report_from_text(payload["text"], payload.get("hints", {}))
    billing = autocode(report)
    return {"report": report.model_dump(), "note_md": note_md, "billing": billing.model_dump()}


@app.post("/proc/upsert")
def upsert(payload: dict):
    bundle = report_to_registry(
        ProcedureReport(**payload["report"]), BillingResult(**payload["billing"])
    )
    upsert_bundle(bundle)
    return {"status": "ok"}
