"""HTTP API for the synthetic registry workbench (mounted at /api/v1/workbench).

Only included when ``workbench_enabled()``; it has no patient identity, EHR
context or authentication because it holds synthetic documents only.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.registry_workbench import jobs, service
from app.registry_workbench.db import get_db
from app.registry_workbench.extraction.prompt import prompt_digest
from app.registry_workbench.settings import claude_configured

router = APIRouter(tags=["registry-workbench"])
_db_dep = Depends(get_db)


def _call(fn, *args: Any, **kwargs: Any) -> Any:
    try:
        return fn(*args, **kwargs)
    except service.WorkbenchError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "errors": exc.detail}) from None


class CaseInput(BaseModel):
    label: str = Field(min_length=1, max_length=200)
    event_date: date | None = None
    synthetic_attestation: Literal[True]


class DocumentInput(BaseModel):
    kind: Literal["procedure", "pathology", "imaging", "clinical_update"]
    text: str = Field(min_length=1, max_length=1_000_000)
    synthetic_attestation: Literal[True]


class ExtractionInput(BaseModel):
    provider: Literal["deterministic", "claude"]
    model: Literal["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"] | None = None
    effort: Literal["low", "medium", "high", "xhigh", "max"] | None = None


class RevisionInput(BaseModel):
    expected_version: int
    values: dict[str, Any]
    mode: Literal["blinded", "assisted"]
    source_run_ids: list[str] = Field(default_factory=list, max_length=20)


class ApprovalInput(BaseModel):
    expected_version: int
    revision_id: str


@router.get("/status")
def status() -> dict[str, Any]:
    return {
        "claude_configured": claude_configured(),
        "prompt_digest": prompt_digest(),
        "egress": "synthetic documents only",
    }


@router.get("/profile")
def profile() -> dict[str, Any]:
    return service.profile()


@router.get("/cases")
def cases(split: str | None = None, q: str | None = None, db: Session = _db_dep):
    return service.worklist(db, split=split, query=q)


@router.post("/cases", status_code=201)
def create_case(body: CaseInput, db: Session = _db_dep):
    case = _call(
        service.create_case,
        db,
        label=body.label,
        source="workbench_manual",
        event_date=body.event_date,
    )
    db.commit()
    return service.case_detail(db, case.id)


@router.get("/cases/{case_id}")
def case(case_id: str, db: Session = _db_dep):
    return _call(service.case_detail, db, case_id)


@router.post("/cases/{case_id}/documents", status_code=201)
def add_document(case_id: str, body: DocumentInput, db: Session = _db_dep):
    case = _call(service.get_case, db, case_id)
    document = _call(
        service.add_document, db, case, kind=body.kind, text=body.text, variant="manual"
    )
    db.commit()
    return {"id": document.id, "sha256": document.sha256}


@router.get("/documents/{document_id}")
def document(document_id: str, db: Session = _db_dep):
    return _call(service.read_document, db, document_id)


@router.post("/documents/{document_id}/extractions", status_code=202)
def extract(document_id: str, body: ExtractionInput, db: Session = _db_dep):
    if body.provider == "claude" and not claude_configured():
        raise HTTPException(409, {"code": "claude_not_configured", "errors": None})
    model = body.model or ("claude-opus-5-5" if body.provider == "claude" else None)
    effort = body.effort or ("medium" if body.provider == "claude" else None)
    run = _call(
        service.queue_extraction,
        db,
        document_id,
        provider=body.provider,
        model=model,
        effort=effort,
    )
    jobs.submit(run.id)
    db.expire_all()
    return service.run_detail(db, run.id)


@router.get("/extractions/{run_id}")
def extraction(run_id: str, db: Session = _db_dep):
    return _call(service.run_detail, db, run_id)


@router.get("/cases/{case_id}/compare")
def compare(case_id: str, runs: str, db: Session = _db_dep):
    return _call(service.compare_case, db, case_id, [r for r in runs.split(",") if r][:4])


@router.post("/cases/{case_id}/revisions", status_code=201)
def save_revision(case_id: str, body: RevisionInput, db: Session = _db_dep):
    revision = _call(
        service.save_revision,
        db,
        case_id,
        expected_version=body.expected_version,
        values=body.values,
        mode=body.mode,
        source_run_ids=body.source_run_ids,
    )
    return {"revision_id": revision.id, "number": revision.number}


@router.post("/cases/{case_id}/approve")
def approve(case_id: str, body: ApprovalInput, db: Session = _db_dep):
    revision = _call(
        service.approve,
        db,
        case_id,
        expected_version=body.expected_version,
        revision_id=body.revision_id,
    )
    return {"approved_revision_id": revision.id}


@router.get("/analysis")
def analysis(db: Session = _db_dep):
    return service.analysis(db)


@router.get("/export/gold.jsonl", response_class=PlainTextResponse)
def export_gold(db: Session = _db_dep):
    lines = service.gold_lines(db)
    return PlainTextResponse(
        "\n".join(lines) + ("\n" if lines else ""),
        media_type="application/x-ndjson",
        headers={"Content-Disposition": 'attachment; filename="robotic_ebus_gold.jsonl"'},
    )


__all__ = ["router"]
