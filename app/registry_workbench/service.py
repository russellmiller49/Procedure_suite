"""Workbench business rules: cases, immutable documents, extraction runs, revisions.

Mirrors the clinical app's review rules (append-only revisions with optimistic
concurrency, evidence spans re-verified against stored sources, approval only
when ``approval_errors`` is empty) without patient identity or EHR context.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timezone
from typing import Any

from pydantic import ValidationError
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.registry_workbench import compare as comparison
from app.registry_workbench.db import Case, Document, Event, ExtractionRun, Revision
from app.registry_workbench.profile import profile
from ip_registry_contracts.measures import launch_measures
from ip_registry_contracts.models import ClinicalRevision, approval_errors
from ip_registry_contracts.projection import analysis_tables

KINDS = ("procedure", "pathology", "imaging", "clinical_update")
PROVIDERS = ("deterministic", "claude")
MODES = ("blinded", "assisted")
_DATE = re.compile(
    r"(?i)(?:date(?:/time)? of procedure|procedure date|date of service)\s*[:\-]?\s*"
    r"(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})"
)


class WorkbenchError(Exception):
    def __init__(self, status: int, code: str, detail: Any = None) -> None:
        super().__init__(code)
        self.status, self.code, self.detail = status, code, detail


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _get(db: Session, model: Any, key: str, code: str) -> Any:
    row = db.get(model, key)
    if row is None:
        raise WorkbenchError(404, code)
    return row


def _event(db: Session, event_kind: str, *, case_id=None, document_id=None, **detail: Any) -> None:
    db.add(Event(kind=event_kind, case_id=case_id, document_id=document_id, detail=detail))


def parse_event_date(text: str) -> date | None:
    match = _DATE.search(text)
    if not match:
        return None
    raw = match.group(1)
    try:
        if "-" in raw:
            return date.fromisoformat(raw)
        month, day, year = (int(part) for part in raw.split("/"))
        return date(year + 2000 if year < 100 else year, month, day)
    except ValueError:
        return None


# -- cases and documents -------------------------------------------------------


def get_case(db: Session, case_id: str) -> Case:
    return _get(db, Case, case_id, "case_not_found")


def create_case(
    db: Session, *, label: str, source: str, event_date: date | None = None, **meta: Any
) -> Case:
    if db.scalar(select(Case).where(Case.label == label)) is not None:
        raise WorkbenchError(409, "case_label_exists")
    case = Case(label=label, source=source, event_date=event_date, **meta)
    db.add(case)
    db.flush()
    _event(db, "case_created", case_id=case.id, source=source)
    return case


def add_document(
    db: Session, case: Case, *, kind: str, text: str, exposure: str = "development", **meta: Any
) -> Document:
    if kind not in KINDS:
        raise WorkbenchError(422, "unknown_document_kind")
    if not text.strip():
        raise WorkbenchError(422, "empty_document")
    sha = _digest(text)
    existing = db.scalar(
        select(Document).where(Document.case_id == case.id, Document.sha256 == sha)
    )
    if existing is not None:
        return existing
    document = Document(
        case_id=case.id, kind=kind, text=text, sha256=sha, exposure=exposure, **meta
    )
    db.add(document)
    db.flush()
    if case.event_date is None and kind == "procedure":
        case.event_date = parse_event_date(text)
    _event(db, "document_added", case_id=case.id, document_id=document.id, kind=kind)
    return document


def _status(case: Case) -> str:
    return (
        "approved"
        if case.approved_revision_id and not case.draft_revision_id
        else ("draft" if case.draft_revision_id else "new")
    )


def _missing(case: Case, approved: Revision | None) -> list[str]:
    missing = [] if case.event_date else ["event_date"]
    if approved is None:
        return missing + ["approval"]
    values = approved.payload
    if {f["window"] for f in values.get("follow_up", []) if f.get("complete")} != {
        "days_0_7",
        "days_8_30",
    }:
        missing.append("follow_up")
    results = values.get("pathology_results", [])
    if not results or any(p["result_status"] in {"pending", "preliminary"} for p in results):
        missing.append("pathology")
    return missing


def worklist(
    db: Session, *, split: str | None = None, query: str | None = None
) -> list[dict[str, Any]]:
    stmt = select(Case).order_by(Case.split, Case.label)
    if split:
        stmt = stmt.where(Case.split == split)
    if query:
        stmt = stmt.where(Case.label.contains(query))
    cases = list(db.scalars(stmt))
    counts = dict(
        db.execute(select(Document.case_id, func.count()).group_by(Document.case_id)).all()
    )
    approved = {
        r.id: r
        for r in db.scalars(
            select(Revision).where(
                Revision.id.in_([c.approved_revision_id for c in cases if c.approved_revision_id])
            )
        )
    }
    return [
        {
            "id": c.id,
            "label": c.label,
            "platform": c.platform,
            "split": c.split,
            "event_date": c.event_date.isoformat() if c.event_date else None,
            "status": _status(c),
            "documents": counts.get(c.id, 0),
            "missing": _missing(c, approved.get(c.approved_revision_id or "")),
        }
        for c in cases
    ]


def _run_summary(run: ExtractionRun) -> dict[str, Any]:
    response = run.response or {}
    observations = response.get("observations") or {}
    return {
        "id": run.id,
        "document_id": run.document_id,
        "provider": run.provider,
        "model": run.model,
        "effort": run.effort,
        "status": run.status,
        "proposal_status": response.get("status"),
        "warnings": response.get("warnings", []),
        "error": run.error,
        "cost_usd": run.cost_usd,
        "latency_s": run.latency_s,
        "has_proposal": bool(observations.get("proposal")),
        "contract_errors": next(
            (
                signal.get("errors", [])
                for signal in observations.get("quality_signals") or []
                if signal.get("phase") == "contract_validation"
            ),
            [],
        ),
        "unresolved_mentions": (observations.get("unresolved_mentions") or [])[:100],
        "unresolved": len(observations.get("unresolved_mentions") or []),
        "created_at": run.created_at.isoformat(),
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
    }


def case_detail(db: Session, case_id: str) -> dict[str, Any]:
    case = _get(db, Case, case_id, "case_not_found")
    documents = list(
        db.scalars(
            select(Document).where(Document.case_id == case.id).order_by(Document.created_at)
        )
    )
    runs = list(
        db.scalars(
            select(ExtractionRun)
            .where(ExtractionRun.document_id.in_([d.id for d in documents]))
            .order_by(ExtractionRun.created_at)
        )
    )
    revisions = list(
        db.scalars(select(Revision).where(Revision.case_id == case.id).order_by(Revision.number))
    )
    by_id = {r.id: r for r in revisions}
    return {
        "id": case.id,
        "label": case.label,
        "platform": case.platform,
        "split": case.split,
        "source": case.source,
        "event_date": case.event_date.isoformat() if case.event_date else None,
        "version": case.version,
        "status": _status(case),
        "draft_revision_id": case.draft_revision_id,
        "approved_revision_id": case.approved_revision_id,
        "draft": by_id[case.draft_revision_id].payload if case.draft_revision_id else None,
        "approved": by_id[case.approved_revision_id].payload if case.approved_revision_id else None,
        "documents": [
            {
                "id": d.id,
                "kind": d.kind,
                "variant": d.variant,
                "exposure": d.exposure,
                "sha256": d.sha256,
                "characters": len(d.text),
            }
            for d in documents
        ],
        "runs": [_run_summary(r) for r in runs],
        "revisions": [
            {
                "id": r.id,
                "number": r.number,
                "mode": r.mode,
                "created_at": r.created_at.isoformat(),
                "approved_at": r.approved_at.isoformat() if r.approved_at else None,
            }
            for r in revisions
        ],
    }


def read_document(db: Session, document_id: str) -> dict[str, Any]:
    document = _get(db, Document, document_id, "document_not_found")
    if document.exposure != "development":
        _event(db, "exposed_document_viewed", case_id=document.case_id, document_id=document.id)
        db.commit()
    return {
        "id": document.id,
        "case_id": document.case_id,
        "kind": document.kind,
        "variant": document.variant,
        "exposure": document.exposure,
        "sha256": document.sha256,
        "text": document.text,
    }


# -- extraction runs -------------------------------------------------------------


def queue_extraction(
    db: Session,
    document_id: str,
    *,
    provider: str,
    model: str | None = None,
    effort: str | None = None,
) -> ExtractionRun:
    document = _get(db, Document, document_id, "document_not_found")
    if provider not in PROVIDERS:
        raise WorkbenchError(422, "unknown_provider")
    run = ExtractionRun(document_id=document.id, provider=provider, model=model, effort=effort)
    db.add(run)
    db.flush()
    _event(
        db,
        "extraction_queued",
        case_id=document.case_id,
        document_id=document.id,
        provider=provider,
    )
    db.commit()
    return run


def run_detail(db: Session, run_id: str) -> dict[str, Any]:
    run = _get(db, ExtractionRun, run_id, "run_not_found")
    return {**_run_summary(run), "response": run.response}


def compare_case(db: Session, case_id: str, run_ids: list[str]) -> dict[str, Any]:
    detail = case_detail(db, case_id)
    sources: dict[str, dict[str, Any] | None] = {}
    for run_id in run_ids:
        run = _get(db, ExtractionRun, run_id, "run_not_found")
        if run.document_id not in {d["id"] for d in detail["documents"]}:
            raise WorkbenchError(422, "run_not_in_case")
        label = f"{run.provider}{(':' + run.model) if run.model else ''} · {run.id[:6]}"
        sources[label] = ((run.response or {}).get("observations") or {}).get("proposal")
    for name in ("draft", "approved"):
        if detail[name]:
            sources[name] = detail[name]
    return {"sources": list(sources), "rows": comparison.compare(sources)}


# -- revisions -------------------------------------------------------------------


def _verify_evidence(db: Session, case: Case, revision: ClinicalRevision) -> None:
    documents = {d.id: d for d in db.scalars(select(Document).where(Document.case_id == case.id))}
    spans = [
        (p.source_document_id, p.source_digest, p.source_start, p.source_end, p.source_excerpt)
        for p in revision.field_provenance
        if p.source_document_id is not None
    ] + [(e.source_document_id, e.source_digest, e.start, e.end, e.text) for e in revision.evidence]
    for doc_id, digest, start, end, excerpt in spans:
        document = documents.get(str(doc_id))
        if document is None or document.sha256 != digest:
            raise WorkbenchError(422, "evidence_context_mismatch")
        if document.text[start:end] != excerpt:
            raise WorkbenchError(422, "evidence_span_mismatch")


def save_revision(
    db: Session,
    case_id: str,
    *,
    expected_version: int,
    values: dict[str, Any],
    mode: str,
    source_run_ids: list[str] | None = None,
) -> Revision:
    case = _get(db, Case, case_id, "case_not_found")
    if mode not in MODES:
        raise WorkbenchError(422, "unknown_review_mode")
    if not values.get("event_date"):
        raise WorkbenchError(422, "event_date_required")
    try:
        revision = ClinicalRevision.model_validate(values)
    except ValidationError as exc:
        errors = [{"loc": list(e["loc"]), "msg": e["msg"]} for e in exc.errors()][:50]
        raise WorkbenchError(422, "revision_invalid", errors) from None
    _verify_evidence(db, case, revision)
    payload = revision.model_dump(mode="json")
    number = (
        db.scalar(select(func.max(Revision.number)).where(Revision.case_id == case.id)) or 0
    ) + 1
    row = Revision(
        case_id=case.id,
        number=number,
        parent_id=case.draft_revision_id or case.approved_revision_id,
        payload=payload,
        payload_digest=_digest(json.dumps(payload, sort_keys=True)),
        mode=mode,
        source_run_ids=list(source_run_ids or []),
    )
    db.add(row)
    db.flush()
    changed = db.execute(
        update(Case)
        .where(Case.id == case.id, Case.version == expected_version)
        .values(version=Case.version + 1, draft_revision_id=row.id, event_date=revision.event_date)
    )
    if changed.rowcount != 1:
        db.rollback()
        raise WorkbenchError(409, "stale_revision")
    _event(db, "revision_saved", case_id=case.id, revision_id=row.id, mode=mode)
    db.commit()
    return row


def approve(db: Session, case_id: str, *, expected_version: int, revision_id: str) -> Revision:
    case = _get(db, Case, case_id, "case_not_found")
    revision = db.get(Revision, revision_id)
    if revision is None or revision.case_id != case.id or case.draft_revision_id != revision.id:
        raise WorkbenchError(409, "approval_context_mismatch")
    try:
        values = ClinicalRevision.model_validate(revision.payload)
    except ValidationError:
        raise WorkbenchError(422, "revision_integrity_failed") from None
    errors = approval_errors(values)
    if errors:
        raise WorkbenchError(422, "approval_review_required", errors)
    changed = db.execute(
        update(Case)
        .where(
            Case.id == case.id,
            Case.version == expected_version,
            Case.draft_revision_id == revision.id,
        )
        .values(version=Case.version + 1, approved_revision_id=revision.id, draft_revision_id=None)
    )
    if changed.rowcount != 1:
        db.rollback()
        raise WorkbenchError(409, "stale_approval")
    revision.approved_at = _now()
    _event(db, "revision_approved", case_id=case.id, revision_id=revision.id, mode=revision.mode)
    db.commit()
    return revision


def _approved_records(db: Session) -> list[tuple[Case, Revision, ClinicalRevision]]:
    rows = db.execute(
        select(Case, Revision).join(Revision, Case.approved_revision_id == Revision.id)
    )
    records = []
    for case, revision in rows:
        values = ClinicalRevision.model_validate(revision.payload)
        if not approval_errors(values):
            records.append((case, revision, values))
    return records


def analysis(db: Session) -> dict[str, Any]:
    records = _approved_records(db)
    return {
        **analysis_tables([(case.id, values) for case, _, values in records]),
        "measures": launch_measures(values for _, _, values in records),
    }


def gold_lines(db: Session) -> list[str]:
    lines = []
    for case, revision, _ in _approved_records(db):
        documents = list(db.scalars(select(Document).where(Document.case_id == case.id)))
        lines.append(
            json.dumps(
                {
                    "case_label": case.label,
                    "family_id": case.family_id,
                    "split": case.split,
                    "review_mode": revision.mode,
                    "qualification_eligible": revision.mode == "blinded",
                    "revision_digest": revision.payload_digest,
                    "documents": [
                        {
                            "id": d.id,
                            "corpus_document_id": d.corpus_document_id,
                            "sha256": d.sha256,
                            "kind": d.kind,
                        }
                        for d in documents
                    ],
                    "revision": revision.payload,
                },
                sort_keys=True,
            )
        )
    return lines


__all__ = [
    "KINDS",
    "MODES",
    "PROVIDERS",
    "WorkbenchError",
    "add_document",
    "analysis",
    "approve",
    "case_detail",
    "compare_case",
    "create_case",
    "get_case",
    "gold_lines",
    "parse_event_date",
    "profile",
    "queue_extraction",
    "read_document",
    "run_detail",
    "save_revision",
    "worklist",
]
