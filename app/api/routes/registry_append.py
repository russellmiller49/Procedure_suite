"""Case-level append endpoint keyed by registry_uuid."""

from __future__ import annotations

import hashlib
import os
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.api.auth import AuthenticatedUser, get_current_user
from app.api.phi_dependencies import get_phi_scrubber
from app.api.phi_redaction import apply_phi_redaction
from app.api.readiness import require_ready
from app.registry_store.dependencies import get_registry_store_db
from app.registry_store.models import RegistryAppendedDocument
from app.registry_store.phi_gate import scan_text_for_phi_risk
from app.vault.models import UserPatientVault


router = APIRouter(tags=["registry-append"])

_ready_dep = Depends(require_ready)
_current_user_dep = Depends(get_current_user)
_db_dep = Depends(get_registry_store_db)
_phi_scrubber_dep = Depends(get_phi_scrubber)


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _note_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class RegistryAppendRequest(BaseModel):
    note: str = Field(..., description="Appended scrubbed note text (or raw when already_scrubbed=false).")
    already_scrubbed: bool = Field(
        True,
        description="If false, server performs PHI scrubbing before persistence.",
    )
    source_type: str | None = Field(
        None,
        description="Optional source marker (e.g., camera_ocr, pdf_local, manual_entry).",
    )
    ocr_correction_applied: bool = Field(
        False,
        description="Whether post-redaction OCR correction was applied.",
    )
    document_kind: str = Field(
        "pathology",
        max_length=64,
        description="Document kind label for this append (default: pathology).",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Optional non-PHI metadata for append tracking.",
    )


class RegistryAppendResponse(BaseModel):
    append_id: str
    user_id: str
    registry_uuid: str
    document_kind: str
    source_type: str | None = None
    ocr_correction_applied: bool = False
    note_sha256: str
    created_at: str


@router.post(
    "/v1/registry/{registry_uuid}/append",
    response_model=RegistryAppendResponse,
    summary="Append a scrubbed document to an existing registry case",
)
def append_registry_document(
    registry_uuid: uuid.UUID,
    payload: RegistryAppendRequest,
    _ready: None = _ready_dep,
    current_user: AuthenticatedUser = _current_user_dep,
    db: Session = _db_dep,
    phi_scrubber=_phi_scrubber_dep,
) -> RegistryAppendResponse:
    # Ensure the target case belongs to the current user.
    case_stmt: Select[tuple[UserPatientVault]] = select(UserPatientVault).where(
        UserPatientVault.user_id == current_user.id,
        UserPatientVault.registry_uuid == registry_uuid,
    )
    case_row = db.execute(case_stmt).scalar_one_or_none()
    if case_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registry case not found for this user",
        )

    if payload.already_scrubbed:
        note_text = payload.note
    else:
        redaction = apply_phi_redaction(payload.note, phi_scrubber)
        note_text = redaction.text

    phi_risk_reasons = scan_text_for_phi_risk(note_text)
    allow_phi_risk_persist = _truthy_env("REGISTRY_RUNS_ALLOW_PHI_RISK_PERSIST")
    if phi_risk_reasons and not allow_phi_risk_persist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "PHI risk detected in scrubbed text; append rejected",
                "reasons": phi_risk_reasons,
            },
        )

    row = RegistryAppendedDocument(
        id=uuid.uuid4(),
        user_id=current_user.id,
        registry_uuid=registry_uuid,
        note_text=note_text,
        note_sha256=_note_sha256(note_text),
        document_kind=(payload.document_kind or "pathology").strip() or "pathology",
        source_type=(payload.source_type or None),
        ocr_correction_applied=bool(payload.ocr_correction_applied),
        metadata_json=payload.metadata or None,
        created_at=_utcnow(),
    )
    db.add(row)
    db.commit()

    return RegistryAppendResponse(
        append_id=str(row.id),
        user_id=str(row.user_id),
        registry_uuid=str(row.registry_uuid),
        document_kind=str(row.document_kind),
        source_type=row.source_type,
        ocr_correction_applied=bool(row.ocr_correction_applied),
        note_sha256=str(row.note_sha256),
        created_at=row.created_at.isoformat(),
    )


__all__ = ["router"]
