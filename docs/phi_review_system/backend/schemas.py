"""
Pydantic Schemas for PHI Review API

These schemas define the request/response contracts for the API endpoints.
They handle validation, serialization, and documentation.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator


# =============================================================================
# ENUMS
# =============================================================================

class EntityType(str, Enum):
    """Types of PHI entities."""
    PERSON = "PERSON"
    PROVIDER = "PROVIDER"
    DATE = "DATE"
    MRN = "MRN"
    LOCATION = "LOCATION"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    SSN = "SSN"
    ACCOUNT_NUMBER = "ACCOUNT_NUMBER"
    LICENSE_NUMBER = "LICENSE_NUMBER"
    DEVICE_ID = "DEVICE_ID"
    URL = "URL"
    IP_ADDRESS = "IP_ADDRESS"
    OTHER = "OTHER"


class ProcessingStatus(str, Enum):
    """Status of a coding job."""
    PENDING_REVIEW = "pending_review"
    PHI_CONFIRMED = "phi_confirmed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EntitySource(str, Enum):
    """How an entity was detected."""
    AUTO = "auto"       # Detected by Presidio
    MANUAL = "manual"   # Added by physician
    REGEX = "regex"     # Detected by custom regex


# =============================================================================
# PHI ENTITY SCHEMAS
# =============================================================================

class PHIEntityBase(BaseModel):
    """Base schema for a PHI entity."""
    text: str = Field(..., description="The actual text content flagged as PHI")
    start: int = Field(..., ge=0, description="Start position in original text")
    end: int = Field(..., gt=0, description="End position in original text")
    entity_type: EntityType = Field(..., description="Type of PHI entity")
    
    @field_validator('end')
    @classmethod
    def end_must_be_greater_than_start(cls, v, info):
        if 'start' in info.data and v <= info.data['start']:
            raise ValueError('end must be greater than start')
        return v


class PHIEntityDetected(PHIEntityBase):
    """Entity as detected by the auto-scrubber (Presidio)."""
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence (0-1)")
    source: EntitySource = Field(default=EntitySource.AUTO)
    
    model_config = ConfigDict(from_attributes=True)


class PHIEntityConfirmed(PHIEntityBase):
    """Entity as confirmed by the physician."""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: EntitySource = Field(..., description="How this entity was identified")
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# PREVIEW ENDPOINT (Step 1: Auto-detect PHI)
# =============================================================================

class ScrubPreviewRequest(BaseModel):
    """Request to preview PHI detection on clinical text."""
    raw_text: str = Field(
        ..., 
        min_length=1, 
        max_length=100000,
        description="Raw clinical note text to analyze"
    )
    document_type: Optional[str] = Field(
        None, 
        description="Type of document (e.g., 'procedure_note', 'op_report')"
    )
    specialty: Optional[str] = Field(
        None,
        description="Medical specialty (e.g., 'interventional_pulmonology')"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "raw_text": "Patient John Smith (MRN: 12345) underwent EBUS of the LEFT UPPER LOBE on 03/15/2024. Attending: Dr. Jane Doe.",
                "document_type": "procedure_note",
                "specialty": "interventional_pulmonology"
            }
        }
    )


class ScrubPreviewResponse(BaseModel):
    """Response containing detected PHI entities for review."""
    raw_text: str = Field(..., description="Original text (echoed back)")
    entities: List[PHIEntityDetected] = Field(
        default_factory=list,
        description="List of detected PHI entities with positions and confidence"
    )
    preview_id: str = Field(..., description="Temporary ID for this preview session")
    expires_at: datetime = Field(..., description="When this preview expires")
    
    # Metadata
    presidio_version: Optional[str] = Field(None, description="Version of Presidio used")
    processing_time_ms: int = Field(..., description="Time taken to process (milliseconds)")
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# SUBMIT ENDPOINT (Step 2: Confirm PHI and Submit)
# =============================================================================

class SubmitRequest(BaseModel):
    """Request to submit confirmed PHI for processing."""
    raw_text: str = Field(
        ..., 
        min_length=1,
        description="Original clinical note text"
    )
    confirmed_phi: List[PHIEntityConfirmed] = Field(
        ...,
        description="List of physician-confirmed PHI entities"
    )
    preview_id: Optional[str] = Field(
        None,
        description="Preview ID from previous step (for correlation)"
    )
    document_type: Optional[str] = Field(None)
    specialty: Optional[str] = Field(None)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "raw_text": "Patient John Smith (MRN: 12345) underwent EBUS of the LEFT UPPER LOBE on 03/15/2024.",
                "confirmed_phi": [
                    {"text": "John Smith", "start": 8, "end": 18, "entity_type": "PERSON", "source": "auto", "confidence": 0.98},
                    {"text": "12345", "start": 25, "end": 30, "entity_type": "MRN", "source": "auto", "confidence": 0.95},
                    {"text": "03/15/2024", "start": 72, "end": 82, "entity_type": "DATE", "source": "auto", "confidence": 0.99}
                ],
                "preview_id": "prev_abc123",
                "document_type": "procedure_note"
            }
        }
    )


class SubmitResponse(BaseModel):
    """Response after submitting for processing."""
    job_id: UUID = Field(..., description="Unique job identifier for tracking")
    status: ProcessingStatus = Field(..., description="Current processing status")
    message: str = Field(..., description="Human-readable status message")
    
    # Counts for confirmation
    phi_entities_secured: int = Field(..., description="Number of PHI entities vaulted")
    scrubbed_text_preview: Optional[str] = Field(
        None,
        description="First 200 chars of scrubbed text (for verification)"
    )
    
    # Polling information
    status_url: str = Field(..., description="URL to poll for status updates")
    estimated_completion_seconds: Optional[int] = Field(
        None,
        description="Estimated time to completion"
    )
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# STATUS ENDPOINT
# =============================================================================

class JobStatusResponse(BaseModel):
    """Response for job status queries."""
    job_id: UUID
    status: ProcessingStatus
    message: str
    
    # Progress info
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    # Results (only populated when completed)
    coding_results: Optional[Dict[str, Any]] = Field(
        None,
        description="CPT/ICD codes and related data (when completed)"
    )
    error_detail: Optional[str] = Field(
        None,
        description="Error message (when failed)"
    )
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# RE-IDENTIFICATION ENDPOINT
# =============================================================================

class ReidentifyRequest(BaseModel):
    """Request to re-attach PHI to processed results."""
    job_id: UUID = Field(..., description="Job ID from submit response")
    include_original_text: bool = Field(
        default=False,
        description="Whether to include the original (PHI-containing) text"
    )


class ReidentifyResponse(BaseModel):
    """Response with re-identified (PHI-restored) data."""
    job_id: UUID
    
    # Re-identified content
    original_text: Optional[str] = Field(
        None,
        description="Original text with PHI (if requested)"
    )
    coding_results: Dict[str, Any] = Field(
        ...,
        description="Coding results with PHI context restored"
    )
    
    # PHI summary
    phi_entities: List[PHIEntityConfirmed] = Field(
        ...,
        description="PHI entities that were secured"
    )
    
    # Audit
    reidentified_at: datetime
    reidentified_by: str
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# AUDIT LOG SCHEMAS
# =============================================================================

class AuditLogEntry(BaseModel):
    """Schema for audit log entries."""
    id: UUID
    timestamp: datetime
    
    # Who
    user_id: str
    user_email: Optional[str]
    user_role: Optional[str]
    
    # What
    action: str
    action_detail: Optional[str]
    
    # Context
    phi_vault_id: Optional[UUID]
    procedure_data_id: Optional[UUID]
    ip_address: Optional[str]
    
    # Additional data
    metadata: Optional[Dict[str, Any]]
    
    model_config = ConfigDict(from_attributes=True)


class AuditLogQuery(BaseModel):
    """Query parameters for audit log search."""
    user_id: Optional[str] = None
    action: Optional[str] = None
    phi_vault_id: Optional[UUID] = None
    procedure_data_id: Optional[UUID] = None
    
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)


class AuditLogResponse(BaseModel):
    """Response for audit log queries."""
    entries: List[AuditLogEntry]
    total_count: int
    limit: int
    offset: int
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# SCRUBBING FEEDBACK / METRICS
# =============================================================================

class ScrubbingMetrics(BaseModel):
    """Metrics for Presidio accuracy tracking."""
    total_documents: int
    total_entities_detected: int
    total_entities_confirmed: int
    
    # Accuracy metrics
    true_positives: int
    false_positives: int
    false_negatives: int
    
    precision: float = Field(..., ge=0.0, le=1.0)
    recall: float = Field(..., ge=0.0, le=1.0)
    f1_score: float = Field(..., ge=0.0, le=1.0)
    
    # Breakdown by entity type
    metrics_by_type: Dict[EntityType, Dict[str, float]]
    
    # Time range
    period_start: datetime
    period_end: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackSummary(BaseModel):
    """Summary of physician corrections for ML improvement."""
    document_id: UUID
    
    # What Presidio got wrong
    false_positive_examples: List[Dict[str, Any]] = Field(
        ...,
        description="Entities Presidio flagged that physician unflagged"
    )
    false_negative_examples: List[Dict[str, Any]] = Field(
        ...,
        description="Entities physician added that Presidio missed"
    )
    
    # Context
    document_type: Optional[str]
    specialty: Optional[str]
    
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# ERROR SCHEMAS
# =============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Human-readable error message")
    detail: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error context"
    )
    request_id: Optional[str] = Field(
        None,
        description="Request ID for support/debugging"
    )


class ValidationErrorDetail(BaseModel):
    """Detail for validation errors."""
    field: str
    message: str
    invalid_value: Optional[Any] = None
