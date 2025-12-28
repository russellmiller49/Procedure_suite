"""
FastAPI Endpoints for PHI Review Workflow

This module implements the physician-in-the-loop PHI scrubbing workflow:
1. POST /scrub/preview - Auto-detect PHI, return highlights for review
2. POST /submit - Confirm PHI, vault it, queue for processing
3. GET /status/{job_id} - Check processing status
4. POST /reidentify - Re-attach PHI to results (authorized users only)
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    ScrubPreviewRequest, ScrubPreviewResponse,
    SubmitRequest, SubmitResponse,
    JobStatusResponse, ReidentifyRequest, ReidentifyResponse,
    PHIEntityDetected, PHIEntityConfirmed, EntitySource,
    ProcessingStatus, ErrorResponse
)
from .models import (
    PHIVault, ProcedureData, AuditLog, EntityAuditDetail, ScrubbingFeedback,
    AuditAction, EntityType as DBEntityType, ProcessingStatus as DBProcessingStatus
)
from .dependencies import (
    get_db_session, get_current_user, get_presidio_analyzer,
    get_encryption_service, get_task_queue, get_audit_logger
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/coder", tags=["PHI Review & Coding"])


# =============================================================================
# PREVIEW ENDPOINT
# =============================================================================

@router.post(
    "/scrub/preview",
    response_model=ScrubPreviewResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Preview PHI detection",
    description="Analyzes clinical text and returns detected PHI entities for physician review."
)
async def preview_scrub(
    request: ScrubPreviewRequest,
    http_request: Request,
    presidio = Depends(get_presidio_analyzer),
    current_user = Depends(get_current_user),
    audit_logger = Depends(get_audit_logger),
):
    """
    Step 1: Auto-detect PHI using Presidio.
    
    Returns highlighted entities for the physician to review/modify
    before final submission.
    """
    start_time = datetime.now(timezone.utc)
    preview_id = f"prev_{uuid4().hex[:12]}"
    
    try:
        # Run Presidio analysis
        analyzer_results = presidio.analyze(
            text=request.raw_text,
            language="en",
            # Configure which entity types to detect
            entities=[
                "PERSON", "DATE_TIME", "PHONE_NUMBER", "EMAIL_ADDRESS",
                "US_SSN", "LOCATION", "MEDICAL_LICENSE", "US_DRIVER_LICENSE"
            ],
        )
        
        # Convert Presidio results to our schema
        entities = []
        for result in analyzer_results:
            # Map Presidio entity types to our types
            entity_type = _map_presidio_entity_type(result.entity_type)
            
            entities.append(PHIEntityDetected(
                text=request.raw_text[result.start:result.end],
                start=result.start,
                end=result.end,
                entity_type=entity_type,
                confidence=result.score,
                source=EntitySource.AUTO,
            ))
        
        # Sort by position
        entities.sort(key=lambda e: e.start)
        
        processing_time = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        
        # Log the preview action (no PHI stored yet)
        await audit_logger.log(
            action=AuditAction.REVIEW_STARTED,
            user_id=current_user.id,
            user_email=current_user.email,
            ip_address=http_request.client.host,
            metadata={
                "preview_id": preview_id,
                "text_length": len(request.raw_text),
                "entities_detected": len(entities),
                "document_type": request.document_type,
                "specialty": request.specialty,
            }
        )
        
        return ScrubPreviewResponse(
            raw_text=request.raw_text,
            entities=entities,
            preview_id=preview_id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            presidio_version=presidio.get_version() if hasattr(presidio, 'get_version') else "unknown",
            processing_time_ms=processing_time,
        )
        
    except Exception as e:
        logger.exception(f"Error in preview_scrub: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "scrub_failed", "message": str(e)}
        )


# =============================================================================
# SUBMIT ENDPOINT
# =============================================================================

@router.post(
    "/submit",
    response_model=SubmitResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Submit confirmed PHI for processing",
    description="Vaults confirmed PHI, scrubs the text, and queues for LLM processing."
)
async def submit_for_coding(
    request: SubmitRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    encryption = Depends(get_encryption_service),
    task_queue = Depends(get_task_queue),
    current_user = Depends(get_current_user),
    audit_logger = Depends(get_audit_logger),
    presidio = Depends(get_presidio_analyzer),
):
    """
    Step 2: Vault PHI and submit for processing.
    
    This endpoint:
    1. Extracts confirmed PHI entities from the text
    2. Encrypts and stores PHI in the vault
    3. Creates scrubbed text with placeholders
    4. Queues the job for LLM processing
    5. Logs comprehensive audit trail
    """
    job_id = uuid4()
    
    try:
        # Extract PHI values for encryption
        phi_data = _extract_phi_for_vault(request.raw_text, request.confirmed_phi)
        
        # Encrypt PHI
        encrypted_phi = encryption.encrypt(json.dumps(phi_data))
        data_hash = hashlib.sha256(json.dumps(phi_data).encode()).hexdigest()
        
        # Generate scrubbed text with placeholders
        scrubbed_text, entity_map = _apply_scrubbing(request.raw_text, request.confirmed_phi)
        original_hash = hashlib.sha256(request.raw_text.encode()).hexdigest()
        
        # === BEGIN TRANSACTION ===
        async with db.begin():
            # Create PHI Vault entry
            phi_vault = PHIVault(
                id=job_id,
                encrypted_data=encrypted_phi,
                data_hash=data_hash,
                encryption_algorithm="FERNET",
                key_version=1,
            )
            db.add(phi_vault)
            
            # Create Procedure Data entry
            procedure_data = ProcedureData(
                id=uuid4(),
                phi_vault_id=job_id,
                scrubbed_text=scrubbed_text,
                original_text_hash=original_hash,
                entity_map=entity_map,
                status=DBProcessingStatus.PHI_CONFIRMED,
                document_type=request.document_type,
                specialty=request.specialty,
                submitted_by=current_user.id,
                reviewed_by=current_user.id,
                reviewed_at=datetime.now(timezone.utc),
            )
            db.add(procedure_data)
            
            # Create audit log
            audit_entry = AuditLog(
                phi_vault_id=job_id,
                procedure_data_id=procedure_data.id,
                user_id=current_user.id,
                user_email=current_user.email,
                user_role=current_user.role,
                action=AuditAction.PHI_CREATED,
                action_detail=f"PHI vaulted with {len(request.confirmed_phi)} entities",
                ip_address=http_request.client.host,
                user_agent=http_request.headers.get("user-agent"),
                request_id=http_request.headers.get("x-request-id"),
                metadata={
                    "preview_id": request.preview_id,
                    "entity_count": len(request.confirmed_phi),
                    "document_type": request.document_type,
                    "specialty": request.specialty,
                    "text_length_original": len(request.raw_text),
                    "text_length_scrubbed": len(scrubbed_text),
                }
            )
            db.add(audit_entry)
            
            # Log entity-level details
            for entity in request.confirmed_phi:
                entity_detail = EntityAuditDetail(
                    audit_log_id=audit_entry.id,
                    entity_text=entity.text,  # Note: This contains PHI
                    entity_type=DBEntityType(entity.entity_type.value),
                    start_position=entity.start,
                    end_position=entity.end,
                    detected_by=entity.source.value,
                    detection_confidence=entity.confidence,
                    was_confirmed=True,
                )
                db.add(entity_detail)
            
            # Capture feedback for ML improvement
            await _capture_scrubbing_feedback(
                db=db,
                procedure_data_id=procedure_data.id,
                raw_text=request.raw_text,
                confirmed_phi=request.confirmed_phi,
                presidio=presidio,
                document_type=request.document_type,
                specialty=request.specialty,
            )
        
        # === END TRANSACTION ===
        
        # Queue for async LLM processing
        await task_queue.enqueue(
            task_name="process_coding",
            job_id=str(job_id),
            payload={
                "procedure_data_id": str(procedure_data.id),
                "scrubbed_text": scrubbed_text,
                "document_type": request.document_type,
                "specialty": request.specialty,
            }
        )
        
        return SubmitResponse(
            job_id=job_id,
            status=ProcessingStatus.PHI_CONFIRMED,
            message="PHI secured. Job queued for processing.",
            phi_entities_secured=len(request.confirmed_phi),
            scrubbed_text_preview=scrubbed_text[:200] + "..." if len(scrubbed_text) > 200 else scrubbed_text,
            status_url=f"/v1/coder/status/{job_id}",
            estimated_completion_seconds=30,
        )
        
    except Exception as e:
        logger.exception(f"Error in submit_for_coding: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "submit_failed", "message": str(e)}
        )


# =============================================================================
# STATUS ENDPOINT
# =============================================================================

@router.get(
    "/status/{job_id}",
    response_model=JobStatusResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get job status",
    description="Returns the current status and results of a coding job."
)
async def get_job_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user),
):
    """Check the status of a submitted coding job."""
    
    # Query procedure data by phi_vault_id (which is our job_id)
    result = await db.execute(
        select(ProcedureData).where(ProcedureData.phi_vault_id == job_id)
    )
    procedure_data = result.scalar_one_or_none()
    
    if not procedure_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Authorization check
    if procedure_data.submitted_by != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this job")
    
    return JobStatusResponse(
        job_id=job_id,
        status=ProcessingStatus(procedure_data.status.value),
        message=_get_status_message(procedure_data.status),
        created_at=procedure_data.created_at,
        updated_at=procedure_data.updated_at,
        completed_at=procedure_data.processed_at,
        coding_results=procedure_data.coding_results if procedure_data.status == DBProcessingStatus.COMPLETED else None,
        error_detail=None,  # Would come from a separate error tracking system
    )


# =============================================================================
# RE-IDENTIFICATION ENDPOINT
# =============================================================================

@router.post(
    "/reidentify",
    response_model=ReidentifyResponse,
    responses={
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse}
    },
    summary="Re-identify processed results",
    description="Decrypts PHI and merges with coding results for display."
)
async def reidentify_results(
    request: ReidentifyRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db_session),
    encryption = Depends(get_encryption_service),
    current_user = Depends(get_current_user),
    audit_logger = Depends(get_audit_logger),
):
    """
    Re-attach PHI to processed results.
    
    This is a sensitive operation that:
    1. Decrypts PHI from the vault
    2. Merges with coding results
    3. Logs the access for audit
    """
    
    # Fetch procedure data and vault
    result = await db.execute(
        select(ProcedureData, PHIVault)
        .join(PHIVault, ProcedureData.phi_vault_id == PHIVault.id)
        .where(ProcedureData.phi_vault_id == request.job_id)
    )
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    
    procedure_data, phi_vault = row
    
    # Authorization check
    if procedure_data.submitted_by != current_user.id and not current_user.is_admin:
        # Log unauthorized access attempt
        await audit_logger.log(
            action=AuditAction.PHI_ACCESSED,
            user_id=current_user.id,
            phi_vault_id=phi_vault.id,
            ip_address=http_request.client.host,
            metadata={"authorized": False, "reason": "not_owner"}
        )
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check job is complete
    if procedure_data.status != DBProcessingStatus.COMPLETED:
        raise HTTPException(
            status_code=400, 
            detail=f"Job not complete. Current status: {procedure_data.status.value}"
        )
    
    # Decrypt PHI
    try:
        decrypted_data = encryption.decrypt(phi_vault.encrypted_data)
        phi_data = json.loads(decrypted_data)
    except Exception as e:
        logger.error(f"Decryption failed for job {request.job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to decrypt PHI")
    
    # Verify data integrity
    computed_hash = hashlib.sha256(decrypted_data.encode()).hexdigest()
    if computed_hash != phi_vault.data_hash:
        logger.error(f"Data integrity check failed for job {request.job_id}")
        raise HTTPException(status_code=500, detail="Data integrity check failed")
    
    # Log the access
    await audit_logger.log(
        action=AuditAction.PHI_DECRYPTED,
        user_id=current_user.id,
        user_email=current_user.email,
        phi_vault_id=phi_vault.id,
        procedure_data_id=procedure_data.id,
        ip_address=http_request.client.host,
        user_agent=http_request.headers.get("user-agent"),
        metadata={
            "include_original_text": request.include_original_text,
            "entity_count": len(phi_data.get("entities", [])),
        }
    )
    
    # Reconstruct original text if requested
    original_text = None
    if request.include_original_text:
        original_text = _reconstruct_original_text(
            scrubbed_text=procedure_data.scrubbed_text,
            entity_map=procedure_data.entity_map,
            phi_data=phi_data,
        )
    
    # Convert entity map to response format
    phi_entities = [
        PHIEntityConfirmed(
            text=e["original_text"],
            start=e["original_start"],
            end=e["original_end"],
            entity_type=e["entity_type"],
            confidence=e.get("confidence", 1.0),
            source=EntitySource(e.get("source", "auto")),
        )
        for e in phi_data.get("entities", [])
    ]
    
    return ReidentifyResponse(
        job_id=request.job_id,
        original_text=original_text,
        coding_results=procedure_data.coding_results,
        phi_entities=phi_entities,
        reidentified_at=datetime.now(timezone.utc),
        reidentified_by=current_user.id,
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _map_presidio_entity_type(presidio_type: str) -> str:
    """Map Presidio entity types to our schema."""
    mapping = {
        "PERSON": "PERSON",
        "DATE_TIME": "DATE",
        "PHONE_NUMBER": "PHONE",
        "EMAIL_ADDRESS": "EMAIL",
        "US_SSN": "SSN",
        "LOCATION": "LOCATION",
        "MEDICAL_LICENSE": "LICENSE_NUMBER",
        "US_DRIVER_LICENSE": "LICENSE_NUMBER",
    }
    return mapping.get(presidio_type, "OTHER")


def _extract_phi_for_vault(raw_text: str, entities: list[PHIEntityConfirmed]) -> dict:
    """Extract PHI data to be encrypted and stored in vault."""
    return {
        "entities": [
            {
                "original_text": e.text,
                "original_start": e.start,
                "original_end": e.end,
                "entity_type": e.entity_type.value,
                "confidence": e.confidence,
                "source": e.source.value,
            }
            for e in entities
        ],
        "extracted_at": datetime.now(timezone.utc).isoformat(),
    }


def _apply_scrubbing(raw_text: str, entities: list[PHIEntityConfirmed]) -> tuple[str, list]:
    """
    Replace PHI with placeholders and return scrubbed text + entity map.
    
    Entity map allows reconstruction of original text during re-identification.
    """
    # Sort entities by position (descending) to replace from end to start
    sorted_entities = sorted(entities, key=lambda e: e.start, reverse=True)
    
    scrubbed = raw_text
    entity_map = []
    
    for i, entity in enumerate(sorted_entities):
        # Create unique placeholder
        placeholder = f"<{entity.entity_type.value}_{i}>"
        
        # Store mapping for reconstruction
        entity_map.append({
            "placeholder": placeholder,
            "entity_type": entity.entity_type.value,
            "original_start": entity.start,
            "original_end": entity.end,
            "scrubbed_start": None,  # Will be calculated after all replacements
            "scrubbed_end": None,
        })
        
        # Replace in text
        scrubbed = scrubbed[:entity.start] + placeholder + scrubbed[entity.end:]
    
    # Reverse entity_map to match original order and calculate new positions
    entity_map.reverse()
    _calculate_scrubbed_positions(scrubbed, entity_map)
    
    return scrubbed, entity_map


def _calculate_scrubbed_positions(scrubbed_text: str, entity_map: list):
    """Calculate positions of placeholders in scrubbed text."""
    for entry in entity_map:
        placeholder = entry["placeholder"]
        pos = scrubbed_text.find(placeholder)
        if pos != -1:
            entry["scrubbed_start"] = pos
            entry["scrubbed_end"] = pos + len(placeholder)


def _reconstruct_original_text(scrubbed_text: str, entity_map: list, phi_data: dict) -> str:
    """Reconstruct original text by replacing placeholders with PHI."""
    result = scrubbed_text
    
    # Create lookup from placeholder to original text
    phi_lookup = {
        f"<{e['entity_type']}_{i}>": e["original_text"]
        for i, e in enumerate(phi_data.get("entities", []))
    }
    
    # Sort by position (descending) for safe replacement
    sorted_map = sorted(entity_map, key=lambda e: e.get("scrubbed_start", 0), reverse=True)
    
    for entry in sorted_map:
        placeholder = entry["placeholder"]
        if placeholder in phi_lookup:
            result = result.replace(placeholder, phi_lookup[placeholder])
    
    return result


def _get_status_message(status: DBProcessingStatus) -> str:
    """Get human-readable status message."""
    messages = {
        DBProcessingStatus.PENDING_REVIEW: "Awaiting PHI review",
        DBProcessingStatus.PHI_CONFIRMED: "PHI secured, queued for processing",
        DBProcessingStatus.PROCESSING: "Processing with AI model",
        DBProcessingStatus.COMPLETED: "Processing complete",
        DBProcessingStatus.FAILED: "Processing failed",
        DBProcessingStatus.CANCELLED: "Cancelled by user",
    }
    return messages.get(status, "Unknown status")


async def _capture_scrubbing_feedback(
    db: AsyncSession,
    procedure_data_id: UUID,
    raw_text: str,
    confirmed_phi: list[PHIEntityConfirmed],
    presidio,
    document_type: Optional[str],
    specialty: Optional[str],
):
    """
    Capture delta between Presidio's detection and physician's confirmation.
    
    This feeds the ML improvement loop.
    """
    # Re-run Presidio to get original predictions
    presidio_results = presidio.analyze(text=raw_text, language="en")
    
    # Convert to comparable format
    presidio_entities = {
        (r.start, r.end, r.entity_type): r.score
        for r in presidio_results
    }
    
    confirmed_entities = {
        (e.start, e.end, e.entity_type.value): e.confidence
        for e in confirmed_phi
    }
    
    # Calculate differences
    presidio_keys = set(presidio_entities.keys())
    confirmed_keys = set(confirmed_entities.keys())
    
    false_positives = presidio_keys - confirmed_keys  # Presidio flagged, physician unflagged
    false_negatives = confirmed_keys - presidio_keys  # Physician added, Presidio missed
    true_positives = presidio_keys & confirmed_keys
    
    # Calculate metrics
    tp = len(true_positives)
    fp = len(false_positives)
    fn = len(false_negatives)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    feedback = ScrubbingFeedback(
        procedure_data_id=procedure_data_id,
        presidio_entities=[
            {"start": s, "end": e, "type": t, "score": presidio_entities[(s, e, t)]}
            for s, e, t in presidio_keys
        ],
        confirmed_entities=[
            {"start": s, "end": e, "type": t, "confidence": confirmed_entities[(s, e, t)]}
            for s, e, t in confirmed_keys
        ],
        false_positives=[
            {"start": s, "end": e, "type": t, "text": raw_text[s:e]}
            for s, e, t in false_positives
        ],
        false_negatives=[
            {"start": s, "end": e, "type": t, "text": raw_text[s:e]}
            for s, e, t in false_negatives
        ],
        true_positives=tp,
        precision=precision,
        recall=recall,
        f1_score=f1,
        document_type=document_type,
        specialty=specialty,
        text_length=len(raw_text),
    )
    
    db.add(feedback)
