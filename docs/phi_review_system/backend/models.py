"""
Database Models for PHI Vault Pattern with Audit Logging

This module defines the SQLAlchemy models for:
- PHI Vault: Encrypted storage of protected health information
- Procedure Data: De-identified clinical text and processing results
- Audit Logs: Comprehensive tracking of all PHI access and modifications
- Scrubbing Feedback: ML improvement data from physician corrections
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Integer, 
    Float, Boolean, Enum, Index, JSON, LargeBinary
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


# =============================================================================
# ENUMS
# =============================================================================

class ProcessingStatus(PyEnum):
    """Status of a coding job through the pipeline."""
    PENDING_REVIEW = "pending_review"       # Awaiting physician PHI confirmation
    PHI_CONFIRMED = "phi_confirmed"         # Physician confirmed PHI, ready to process
    PROCESSING = "processing"               # LLM inference in progress
    COMPLETED = "completed"                 # Successfully processed
    FAILED = "failed"                       # Processing error
    CANCELLED = "cancelled"                 # Cancelled by user


class AuditAction(PyEnum):
    """Types of auditable actions in the system."""
    # PHI Vault actions
    PHI_CREATED = "phi_created"
    PHI_ACCESSED = "phi_accessed"
    PHI_DECRYPTED = "phi_decrypted"
    PHI_DELETED = "phi_deleted"
    
    # Review actions
    REVIEW_STARTED = "review_started"
    ENTITY_CONFIRMED = "entity_confirmed"
    ENTITY_UNFLAGGED = "entity_unflagged"
    ENTITY_ADDED = "entity_added"
    REVIEW_COMPLETED = "review_completed"
    
    # Processing actions
    SCRUB_EXECUTED = "scrub_executed"
    LLM_CALLED = "llm_called"
    REIDENTIFIED = "reidentified"
    
    # Access actions
    RESULT_VIEWED = "result_viewed"
    RESULT_EXPORTED = "result_exported"


class EntityType(PyEnum):
    """Types of PHI entities that can be detected/flagged."""
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


# =============================================================================
# CORE TABLES
# =============================================================================

class PHIVault(Base):
    """
    Encrypted storage for Protected Health Information.
    
    This table stores encrypted PHI separately from clinical text.
    The encryption key should be managed via a KMS (AWS KMS, HashiCorp Vault, etc.)
    
    HIPAA Considerations:
    - All data in encrypted_data column is AES-256 encrypted
    - Access requires explicit decryption request (logged)
    - Supports key rotation via key_version field
    """
    __tablename__ = "phi_vault"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Encrypted PHI blob (Fernet or AES-256-GCM encrypted JSON)
    encrypted_data = Column(LargeBinary, nullable=False)
    
    # Encryption metadata
    encryption_algorithm = Column(String(50), default="FERNET", nullable=False)
    key_version = Column(Integer, default=1, nullable=False)  # For key rotation
    
    # Data integrity
    data_hash = Column(String(64), nullable=False)  # SHA-256 of plaintext for verification
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional TTL
    
    # Soft delete support
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(String(255), nullable=True)
    
    # Relationships
    procedure_data = relationship("ProcedureData", back_populates="phi_vault", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="phi_vault")
    
    __table_args__ = (
        Index("ix_phi_vault_created_at", "created_at"),
        Index("ix_phi_vault_expires_at", "expires_at"),
    )


class ProcedureData(Base):
    """
    De-identified clinical text and processing results.
    
    This table contains ONLY scrubbed/de-identified data that is safe
    to process via external LLM APIs.
    """
    __tablename__ = "procedure_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Link to PHI (foreign key to vault)
    phi_vault_id = Column(UUID(as_uuid=True), ForeignKey("phi_vault.id"), nullable=False, unique=True)
    
    # De-identified content
    scrubbed_text = Column(Text, nullable=False)  # Text sent to LLM
    original_text_hash = Column(String(64), nullable=False)  # SHA-256 for integrity
    
    # Entity mapping (for re-identification)
    # Stores: [{"placeholder": "<PATIENT_1>", "entity_type": "PERSON", "position": {"start": 0, "end": 10}}]
    entity_map = Column(JSONB, nullable=False, default=list)
    
    # Processing status
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING_REVIEW, nullable=False)
    
    # LLM results (stored after processing)
    coding_results = Column(JSONB, nullable=True)  # CPT/ICD codes returned
    llm_model_version = Column(String(100), nullable=True)
    llm_response_raw = Column(Text, nullable=True)  # Raw response for debugging
    
    # Metadata
    document_type = Column(String(100), nullable=True)  # e.g., "procedure_note", "op_report"
    specialty = Column(String(100), nullable=True)  # e.g., "interventional_pulmonology"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Submitting user
    submitted_by = Column(String(255), nullable=False)  # User ID of physician
    reviewed_by = Column(String(255), nullable=True)    # May differ from submitter
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    phi_vault = relationship("PHIVault", back_populates="procedure_data")
    audit_logs = relationship("AuditLog", back_populates="procedure_data")
    scrubbing_feedback = relationship("ScrubbingFeedback", back_populates="procedure_data")
    
    __table_args__ = (
        Index("ix_procedure_data_status", "status"),
        Index("ix_procedure_data_submitted_by", "submitted_by"),
        Index("ix_procedure_data_created_at", "created_at"),
    )


# =============================================================================
# AUDIT LOGGING
# =============================================================================

class AuditLog(Base):
    """
    Comprehensive audit trail for HIPAA compliance.
    
    Every access to PHI, every modification, and every processing step
    is logged here. This table should be append-only in production
    (no updates or deletes).
    
    HIPAA Requirements Addressed:
    - §164.312(b): Audit controls
    - §164.308(a)(1)(ii)(D): Information system activity review
    """
    __tablename__ = "audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # What was accessed
    phi_vault_id = Column(UUID(as_uuid=True), ForeignKey("phi_vault.id"), nullable=True)
    procedure_data_id = Column(UUID(as_uuid=True), ForeignKey("procedure_data.id"), nullable=True)
    
    # Who performed the action
    user_id = Column(String(255), nullable=False)
    user_email = Column(String(255), nullable=True)
    user_role = Column(String(100), nullable=True)  # e.g., "physician", "coder", "admin"
    
    # What action was performed
    action = Column(Enum(AuditAction), nullable=False)
    action_detail = Column(Text, nullable=True)  # Human-readable description
    
    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)
    request_id = Column(String(255), nullable=True)  # Correlation ID
    
    # Additional context (flexible JSON for action-specific data)
    metadata = Column(JSONB, nullable=True, default=dict)
    
    # Timestamp (immutable)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    phi_vault = relationship("PHIVault", back_populates="audit_logs")
    procedure_data = relationship("ProcedureData", back_populates="audit_logs")
    
    __table_args__ = (
        Index("ix_audit_log_timestamp", "timestamp"),
        Index("ix_audit_log_user_id", "user_id"),
        Index("ix_audit_log_action", "action"),
        Index("ix_audit_log_phi_vault_id", "phi_vault_id"),
        Index("ix_audit_log_procedure_data_id", "procedure_data_id"),
        # Composite index for common queries
        Index("ix_audit_log_user_timestamp", "user_id", "timestamp"),
    )


class EntityAuditDetail(Base):
    """
    Detailed tracking of PHI entity-level changes during review.
    
    This captures the granular decisions made by physicians:
    - Which entities were confirmed as PHI
    - Which were unflagged (false positives)
    - Which were manually added (false negatives)
    
    This data feeds the ML improvement loop.
    """
    __tablename__ = "entity_audit_detail"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Parent audit log entry
    audit_log_id = Column(UUID(as_uuid=True), ForeignKey("audit_log.id"), nullable=False)
    
    # Entity details
    entity_text = Column(String(500), nullable=False)  # The actual text (may be PHI - encrypted in practice)
    entity_type = Column(Enum(EntityType), nullable=False)
    
    # Position in original text
    start_position = Column(Integer, nullable=False)
    end_position = Column(Integer, nullable=False)
    
    # Detection source and outcome
    detected_by = Column(String(50), nullable=False)  # "presidio", "manual", "regex"
    detection_confidence = Column(Float, nullable=True)  # 0.0 - 1.0
    
    # Physician decision
    was_confirmed = Column(Boolean, nullable=False)  # True = kept as PHI, False = unflagged
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("ix_entity_audit_audit_log_id", "audit_log_id"),
        Index("ix_entity_audit_entity_type", "entity_type"),
    )


# =============================================================================
# ML IMPROVEMENT / FEEDBACK LOOP
# =============================================================================

class ScrubbingFeedback(Base):
    """
    Captures delta between automated scrubbing and physician corrections.
    
    This data is used to:
    1. Track Presidio accuracy metrics over time
    2. Generate training data for model fine-tuning
    3. Identify patterns in false positives/negatives
    """
    __tablename__ = "scrubbing_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Link to procedure
    procedure_data_id = Column(UUID(as_uuid=True), ForeignKey("procedure_data.id"), nullable=False)
    
    # Presidio's original predictions
    presidio_entities = Column(JSONB, nullable=False)  # Raw Presidio output
    presidio_version = Column(String(50), nullable=True)
    
    # Physician's final determination
    confirmed_entities = Column(JSONB, nullable=False)  # What physician approved
    
    # Computed metrics for this document
    false_positives = Column(JSONB, nullable=False, default=list)  # Presidio flagged, physician unflagged
    false_negatives = Column(JSONB, nullable=False, default=list)  # Physician added, Presidio missed
    true_positives = Column(Integer, nullable=False, default=0)
    
    # Aggregate scores
    precision = Column(Float, nullable=True)  # TP / (TP + FP)
    recall = Column(Float, nullable=True)     # TP / (TP + FN)
    f1_score = Column(Float, nullable=True)
    
    # Context for ML training
    document_type = Column(String(100), nullable=True)
    specialty = Column(String(100), nullable=True)
    text_length = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    procedure_data = relationship("ProcedureData", back_populates="scrubbing_feedback")
    
    __table_args__ = (
        Index("ix_scrubbing_feedback_created_at", "created_at"),
        Index("ix_scrubbing_feedback_specialty", "specialty"),
    )


# =============================================================================
# USER SESSION TRACKING (Optional - for detailed access patterns)
# =============================================================================

class UserSession(Base):
    """
    Tracks user sessions for security analysis and access patterns.
    
    Useful for detecting anomalous access patterns (e.g., bulk PHI access).
    """
    __tablename__ = "user_session"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(String(255), nullable=False)
    session_token_hash = Column(String(64), nullable=False)  # SHA-256 of session token
    
    # Session metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Session state
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index("ix_user_session_user_id", "user_id"),
        Index("ix_user_session_active", "is_active"),
    )
