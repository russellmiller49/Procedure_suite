"""PHI endpoints for preview, submission, status, and re-identification.

Raw PHI stays inside PHIService/PHIVault; responses expose only scrubbed text
except for the reidentify endpoint (intended for PHI-safe UI only).
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from modules.api.phi_dependencies import get_phi_service, get_phi_session
from modules.phi import models
from modules.phi.ports import ScrubResult
from modules.phi.service import PHIService

router = APIRouter(prefix="/v1/phi", tags=["phi"])


class ScrubbedEntityModel(BaseModel):
    placeholder: str
    entity_type: str
    original_start: int
    original_end: int


class ScrubPreviewRequest(BaseModel):
    text: str = Field(..., description="Raw clinical text (synthetic in demo)")
    document_type: str | None = None
    specialty: str | None = None


class ScrubPreviewResponse(BaseModel):
    scrubbed_text: str
    entities: List[ScrubbedEntityModel]


class SubmitRequest(BaseModel):
    text: str = Field(..., description="Raw clinical text to vault (synthetic in demo)")
    submitted_by: str = Field(..., description="User identifier submitting PHI")
    document_type: str | None = None
    specialty: str | None = None


class SubmitResponse(BaseModel):
    procedure_id: str
    status: str
    scrubbed_text: str
    entities: List[ScrubbedEntityModel]


class StatusResponse(BaseModel):
    procedure_id: str
    status: str
    document_type: str | None = None
    specialty: str | None = None
    submitted_by: str | None = None
    created_at: str | None = None


class ProcedureReviewResponse(BaseModel):
    procedure_id: str
    status: str
    scrubbed_text: str
    entities: List[ScrubbedEntityModel]
    document_type: str | None = None
    specialty: str | None = None
    submitted_by: str | None = None
    created_at: str | None = None


class ScrubbingFeedbackRequest(BaseModel):
    scrubbed_text: str
    entities: List[ScrubbedEntityModel]
    reviewer_id: str
    reviewer_email: str | None = None
    reviewer_role: str | None = None
    comment: str | None = None


class ReidentifyRequest(BaseModel):
    procedure_id: str
    user_id: str
    user_email: str | None = None
    user_role: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    request_id: str | None = None


class ReidentifyResponse(BaseModel):
    raw_text: str


def _to_entities(scrub_result: ScrubResult) -> list[ScrubbedEntityModel]:
    return [ScrubbedEntityModel(**entity) for entity in scrub_result.entities]


def _from_entity_map(entity_map) -> list[ScrubbedEntityModel]:
    if entity_map is None:
        return []
    return [ScrubbedEntityModel(**entity) for entity in entity_map]


@router.post("/scrub/preview", response_model=ScrubPreviewResponse, summary="Preview PHI scrubbing (no persistence)")
def preview_scrub(
    payload: ScrubPreviewRequest,
    phi_service: PHIService = Depends(get_phi_service),
) -> ScrubPreviewResponse:
    scrub_result = phi_service.preview(
        text=payload.text,
        document_type=payload.document_type,
        specialty=payload.specialty,
    )
    return ScrubPreviewResponse(scrubbed_text=scrub_result.scrubbed_text, entities=_to_entities(scrub_result))


@router.post("/submit", response_model=SubmitResponse, summary="Submit and vault PHI with scrubbing")
def submit_phi(
    payload: SubmitRequest,
    phi_service: PHIService = Depends(get_phi_service),
) -> SubmitResponse:
    scrub_result = phi_service.preview(
        text=payload.text,
        document_type=payload.document_type,
        specialty=payload.specialty,
    )
    proc = phi_service.vault_phi(
        raw_text=payload.text,
        scrub_result=scrub_result,
        submitted_by=payload.submitted_by,
        document_type=payload.document_type,
        specialty=payload.specialty,
    )
    return SubmitResponse(
        procedure_id=str(proc.id),
        status=proc.status.value if hasattr(proc.status, "value") else str(proc.status),
        scrubbed_text=scrub_result.scrubbed_text,
        entities=_to_entities(scrub_result),
    )


@router.get("/status/{procedure_id}", response_model=StatusResponse, summary="Check PHI record status")
def get_status(
    procedure_id: str,
    db: Session = Depends(get_phi_session),
) -> StatusResponse:
    try:
        proc_uuid = uuid.UUID(procedure_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid procedure_id") from exc

    proc = db.get(models.ProcedureData, proc_uuid)
    if proc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Procedure not found")

    return StatusResponse(
        procedure_id=str(proc.id),
        status=proc.status.value if hasattr(proc.status, "value") else str(proc.status),
        document_type=proc.document_type,
        specialty=proc.specialty,
        submitted_by=proc.submitted_by,
        created_at=proc.created_at.isoformat() if proc.created_at else None,
    )


@router.get(
    "/procedure/{procedure_id}",
    response_model=ProcedureReviewResponse,
    summary="Fetch scrubbed content for PHI review (no raw PHI)",
)
def get_procedure_for_review(
    procedure_id: str,
    phi_service: PHIService = Depends(get_phi_service),
) -> ProcedureReviewResponse:
    try:
        proc_uuid = uuid.UUID(procedure_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid procedure_id") from exc

    try:
        proc = phi_service.get_procedure_for_review(procedure_data_id=proc_uuid)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Procedure not found")

    return ProcedureReviewResponse(
        procedure_id=str(proc.id),
        status=proc.status.value if hasattr(proc.status, "value") else str(proc.status),
        scrubbed_text=proc.scrubbed_text,
        entities=_from_entity_map(proc.entity_map),
        document_type=proc.document_type,
        specialty=proc.specialty,
        submitted_by=proc.submitted_by,
        created_at=proc.created_at.isoformat() if proc.created_at else None,
    )


@router.post(
    "/procedure/{procedure_id}/feedback",
    response_model=ProcedureReviewResponse,
    summary="Apply scrubbing feedback and mark procedure as reviewed",
)
def submit_scrubbing_feedback(
    procedure_id: str,
    payload: ScrubbingFeedbackRequest,
    phi_service: PHIService = Depends(get_phi_service),
) -> ProcedureReviewResponse:
    try:
        proc_uuid = uuid.UUID(procedure_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid procedure_id") from exc

    try:
        proc = phi_service.apply_scrubbing_feedback(
            procedure_data_id=proc_uuid,
            scrubbed_text=payload.scrubbed_text,
            entities=[entity.model_dump() for entity in payload.entities],
            reviewer_id=payload.reviewer_id,
            reviewer_email=payload.reviewer_email,
            reviewer_role=payload.reviewer_role,
            comment=payload.comment,
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Procedure not found or missing PHI vault")

    return ProcedureReviewResponse(
        procedure_id=str(proc.id),
        status=proc.status.value if hasattr(proc.status, "value") else str(proc.status),
        scrubbed_text=proc.scrubbed_text,
        entities=_from_entity_map(proc.entity_map),
        document_type=proc.document_type,
        specialty=proc.specialty,
        submitted_by=proc.submitted_by,
        created_at=proc.created_at.isoformat() if proc.created_at else None,
    )


@router.post("/reidentify", response_model=ReidentifyResponse, summary="Reidentify raw PHI text (PHI-safe UI only)")
def reidentify_phi(
    payload: ReidentifyRequest,
    phi_service: PHIService = Depends(get_phi_service),
) -> ReidentifyResponse:
    try:
        proc_uuid = uuid.UUID(payload.procedure_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid procedure_id") from exc

    try:
        plaintext = phi_service.reidentify(
            procedure_data_id=proc_uuid,
            user_id=payload.user_id,
            user_email=payload.user_email,
            user_role=payload.user_role,
            ip_address=payload.ip_address,
            user_agent=payload.user_agent,
            request_id=payload.request_id,
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Procedure not found or missing PHI vault")

    return ReidentifyResponse(raw_text=plaintext)
