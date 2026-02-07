# Procedure Suite V8 Migration Plan
## Updated with Physician-in-the-Loop PHI Review

This document updates the original migration plan to incorporate the Human-in-the-Loop (HITL) PHI review workflow, where the **physician who writes the note also confirms PHI flagging** before submission.

---

## Implementation snapshot (Phase 0.1–0.6)

- PHI vault + review models/migrations are live (`PHIVault`, `ProcedureData`, `ScrubbingFeedback`, `AuditLog`).
- PHIService provides preview, vault, reidentify, review fetch, and scrubbing feedback update.
- /v1/phi API: preview, submit, status, procedure review, feedback, reidentify (raw text only on reidentify).
- PHI review status: `ProcessingStatus.PHI_REVIEWED` is required for coding when `CODER_REQUIRE_PHI_REVIEW=true`.
- Audit action: `SCRUBBING_FEEDBACK_APPLIED` records review events without raw PHI.
- Coding PHI gating: `/api/v1/procedures/{id}/codes/suggest` enforces PHI review and uses only `ProcedureData.scrubbed_text`.
- Encryption adapters:
  - `PHI_ENCRYPTION_MODE=demo` → insecure demo adapter (synthetic data only).
  - `PHI_ENCRYPTION_MODE=fernet` (default) → `FernetEncryptionAdapter` using `PHI_ENCRYPTION_KEY`.
- Scrubber adapters: stub + Presidio scaffold (stubbed), ready to swap when Presidio is installed.
- Phase 1 cutover: CodingService is the sole backend coder; `/v1/coder/run` is a legacy shim (blocked when `CODER_REQUIRE_PHI_REVIEW=true`, non-PHI/synthetic only otherwise).
- Primary coding path: `/v1/phi/submit` → review/feedback (`PHI_REVIEWED`) → `/api/v1/procedures/{id}/codes/suggest` (CodingService).
- Phase 2: Legacy coding/LLM routes are marked non-PHI/synthetic-only; FastAPI does not call `EnhancedCPTCoder` directly; CodingService is the canonical coding orchestrator.
- Phase 3: FastAPI remains a thin adapter over services; dependencies centralized in `app/api/dependencies.py` and `app/api/phi_dependencies.py`; warmup/infra stays in `app/infra/*`.

## PHI Regression Checklist (Phase 4)

- Tests to run:
  - `pytest tests/integration/test_phi_workflow_end_to_end.py tests/integration/test_phi_response_safety.py tests/integration/test_phi_logging_safety.py -q`
  - plus core suites: `tests/phi/*`, `tests/api/test_phi_endpoints.py`, `tests/api/test_coding_phi_gating.py`, `tests/coding/test_phi_gating.py`
- Expect:
  - PHI appears only in `/v1/phi/reidentify` responses.
  - No raw PHI fragments in submit/status/procedure/coding responses or logs.
  - Coding gated when `CODER_REQUIRE_PHI_REVIEW=true` and uses `ProcedureData.scrubbed_text`.
- Env for PHI flows:
  - `CODER_REQUIRE_PHI_REVIEW=true`
  - `PHI_ENCRYPTION_MODE=fernet` with `PHI_ENCRYPTION_KEY` set (demo may use `PHI_ENCRYPTION_MODE=demo` with synthetic data only).

Recommended env flags for the PHI demo
- `CODER_REQUIRE_PHI_REVIEW=true` (forces reviewed status before coding)
- `PHI_ENCRYPTION_MODE=fernet` and `PHI_ENCRYPTION_KEY=<fernet-key>` for closer-to-prod encryption
- `PHI_DATABASE_URL` to point PHI tables to the desired Postgres/SQLite target
- `PRESIDIO_NLP_MODEL` retained for future Presidio wiring

The sections below remain the original migration narrative; implemented pieces above supersede earlier placeholders.

## Architecture Overview (Updated)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         PHYSICIAN WORKFLOW (NEW)                                 │
│                                                                                  │
│  ┌───────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │
│  │ 1. Write  │──▶│ 2. Preview  │──▶│ 3. Review   │──▶│ 4. Confirm & Submit │   │
│  │ Note      │   │ PHI         │   │ Highlights  │   │                     │   │
│  │           │   │ (Presidio)  │   │ (Inline)    │   │                     │   │
│  └───────────┘   └─────────────┘   └─────────────┘   └──────────┬──────────┘   │
│                                                                  │              │
└──────────────────────────────────────────────────────────────────┼──────────────┘
                                                                   │
┌──────────────────────────────────────────────────────────────────┼──────────────┐
│                         SECURE BACKEND                           │              │
│                                                                  ▼              │
│  ┌─────────────────────┐         ┌─────────────────────────────────────────┐   │
│  │ PHI VAULT           │         │ PROCEDURE DATA (No PHI)                 │   │
│  │                     │◀──UUID──▶│                                         │   │
│  │ • Encrypted PHI     │         │ • Scrubbed text                         │   │
│  │ • Audit trail       │         │ • Entity map (reconstruction)           │   │
│  └─────────────────────┘         └──────────────────┬──────────────────────┘   │
│                                                     │                          │
│                                                     ▼                          │
│                                          ┌─────────────────────┐               │
│                                          │ CodingService       │               │
│                                          │ (DDD / Hexagonal)   │               │
│                                          │                     │               │
│                                          │ • Rule Engine       │               │
│                                          │ • LLM Advisor       │               │
│                                          │ • KB Adapter        │               │
│                                          └──────────┬──────────┘               │
│                                                     │                          │
│                                                     ▼                          │
│                                          ┌─────────────────────┐               │
│                                          │ Results + Audit     │               │
│                                          └─────────────────────┘               │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0 (NEW) – PHI Infrastructure Setup

Before the hard cutover, we need the PHI vault and review infrastructure in place.

### 0.1 Add Database Models for PHI Vault

**New Files:**
- `app/phi/models.py`
- `app/phi/schemas.py`

**Tasks:**

1. Create the PHI domain models:

```python
# app/phi/models.py

from sqlalchemy import Column, String, Text, DateTime, LargeBinary, Boolean, Enum, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from app.shared.database import Base


class ProcessingStatus(PyEnum):
    PENDING_REVIEW = "pending_review"
    PHI_CONFIRMED = "phi_confirmed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AuditAction(PyEnum):
    PHI_CREATED = "phi_created"
    PHI_ACCESSED = "phi_accessed"
    PHI_DECRYPTED = "phi_decrypted"
    REVIEW_STARTED = "review_started"
    ENTITY_CONFIRMED = "entity_confirmed"
    ENTITY_UNFLAGGED = "entity_unflagged"
    ENTITY_ADDED = "entity_added"
    REVIEW_COMPLETED = "review_completed"
    LLM_CALLED = "llm_called"
    REIDENTIFIED = "reidentified"


class PHIVault(Base):
    """Encrypted storage for Protected Health Information."""
    __tablename__ = "phi_vault"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    encrypted_data = Column(LargeBinary, nullable=False)
    data_hash = Column(String(64), nullable=False)
    encryption_algorithm = Column(String(50), default="FERNET")
    key_version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    procedure_data = relationship("ProcedureData", back_populates="phi_vault", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="phi_vault")


class ProcedureData(Base):
    """De-identified clinical text and processing results."""
    __tablename__ = "procedure_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phi_vault_id = Column(UUID(as_uuid=True), ForeignKey("phi_vault.id"), nullable=False)
    
    scrubbed_text = Column(Text, nullable=False)
    original_text_hash = Column(String(64), nullable=False)
    entity_map = Column(JSONB, nullable=False, default=list)
    
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING_REVIEW)
    coding_results = Column(JSONB, nullable=True)
    
    document_type = Column(String(100), nullable=True)
    specialty = Column(String(100), nullable=True)
    
    submitted_by = Column(String(255), nullable=False)
    reviewed_by = Column(String(255), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    phi_vault = relationship("PHIVault", back_populates="procedure_data")
    audit_logs = relationship("AuditLog", back_populates="procedure_data")


class AuditLog(Base):
    """HIPAA-compliant audit trail."""
    __tablename__ = "audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    phi_vault_id = Column(UUID(as_uuid=True), ForeignKey("phi_vault.id"), nullable=True)
    procedure_data_id = Column(UUID(as_uuid=True), ForeignKey("procedure_data.id"), nullable=True)
    
    user_id = Column(String(255), nullable=False)
    user_email = Column(String(255), nullable=True)
    user_role = Column(String(100), nullable=True)
    
    action = Column(Enum(AuditAction), nullable=False)
    action_detail = Column(Text, nullable=True)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(255), nullable=True)
    metadata = Column(JSONB, nullable=True, default=dict)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    phi_vault = relationship("PHIVault", back_populates="audit_logs")
    procedure_data = relationship("ProcedureData", back_populates="audit_logs")


class ScrubbingFeedback(Base):
    """ML improvement data from physician corrections."""
    __tablename__ = "scrubbing_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    procedure_data_id = Column(UUID(as_uuid=True), ForeignKey("procedure_data.id"))
    
    presidio_entities = Column(JSONB, nullable=False)
    confirmed_entities = Column(JSONB, nullable=False)
    
    false_positives = Column(JSONB, default=list)
    false_negatives = Column(JSONB, default=list)
    true_positives = Column(Integer, default=0)
    
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    
    document_type = Column(String(100), nullable=True)
    specialty = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
```

2. Create Pydantic schemas in `app/phi/schemas.py` (see previous code)

3. Run migrations:
```bash
alembic revision --autogenerate -m "Add PHI vault and audit tables"
alembic upgrade head
```

### 0.2 Create PHI Service Layer

**New Files:**
- `app/phi/adapters/encryption_adapter.py`
- `app/phi/adapters/presidio_adapter.py`
- `app/phi/application/phi_service.py`
- `app/phi/ports/phi_ports.py`

**Tasks:**

1. Define ports (interfaces):

```python
# app/phi/ports/phi_ports.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from uuid import UUID


class EncryptionPort(ABC):
    @abstractmethod
    def encrypt(self, plaintext: str) -> bytes:
        pass
    
    @abstractmethod
    def decrypt(self, ciphertext: bytes) -> str:
        pass


class PHIScrubberPort(ABC):
    @abstractmethod
    def analyze(self, text: str) -> List[Dict[str, Any]]:
        """Detect PHI entities in text."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        pass


class PHIVaultPort(ABC):
    @abstractmethod
    async def store(self, token_id: UUID, encrypted_data: bytes, data_hash: str) -> None:
        pass
    
    @abstractmethod
    async def retrieve(self, token_id: UUID) -> bytes:
        pass


class AuditLoggerPort(ABC):
    @abstractmethod
    async def log(self, action: str, user_id: str, **kwargs) -> None:
        pass
```

2. Implement Presidio adapter with IP-specific allow-lists:

```python
# app/phi/adapters/presidio_adapter.py

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
import logging

logger = logging.getLogger(__name__)


class PresidioAdapter:
    """
    Presidio-based PHI scrubber with IP-specific configuration.
    
    Configured to preserve anatomical terms critical for procedure coding.
    """
    
    # Terms that should NOT be flagged as PHI (critical for coding)
    ANATOMICAL_ALLOW_LIST = {
        # Laterality
        "left", "right", "bilateral", "unilateral",
        "medial", "lateral", "anterior", "posterior",
        "superior", "inferior", "proximal", "distal",
        
        # Lung anatomy (critical for IP)
        "upper lobe", "middle lobe", "lower lobe",
        "right upper lobe", "rul", "right middle lobe", "rml",
        "right lower lobe", "rll", "left upper lobe", "lul",
        "left lower lobe", "lll", "lingula",
        "carina", "trachea", "bronchus", "bronchi",
        "mainstem", "segmental", "subsegmental",
        
        # Mediastinal stations
        "mediastinum", "hilum", "hilar", "paratracheal",
        "subcarinal", "aortopulmonary", "prevascular",
        "station 4r", "station 4l", "station 7",
        "station 10", "station 10r", "station 10l",
        "station 11", "station 11r", "station 11l",
        "station 12", "station 2r", "station 2l",
        
        # Procedure terms
        "ebus", "eus", "tbna", "bal", "bronchoscopy",
        "endobronchial", "transbronchial", "electromagnetic",
        "navigation", "robotic", "cone beam", "fluoroscopy",
        
        # Common clinical terms
        "malignancy", "carcinoma", "adenocarcinoma",
        "squamous", "small cell", "non-small cell",
        "lymph node", "lymphadenopathy", "mass", "nodule",
    }
    
    def __init__(self, nlp_model: str = "en_core_web_lg"):
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": nlp_model}]
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine = provider.create_engine()
        
        self._analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
        logger.info(f"Presidio initialized with {len(self.ANATOMICAL_ALLOW_LIST)} allow-listed terms")
    
    def analyze(self, text: str) -> list:
        """
        Analyze text for PHI, filtering out allowed anatomical terms.
        """
        results = self._analyzer.analyze(
            text=text,
            language="en",
            entities=[
                "PERSON", "DATE_TIME", "PHONE_NUMBER", "EMAIL_ADDRESS",
                "US_SSN", "LOCATION", "MEDICAL_LICENSE", "US_DRIVER_LICENSE"
            ],
        )
        
        # Filter out allowed anatomical/clinical terms
        filtered_results = []
        text_lower = text.lower()
        
        for result in results:
            detected_text = text[result.start:result.end].lower()
            
            # Check if detected text is in allow list
            if detected_text in self.ANATOMICAL_ALLOW_LIST:
                logger.debug(f"Allowing clinical term: {detected_text}")
                continue
            
            # Check if detected text contains an allowed term (for compound phrases)
            is_allowed = False
            for allowed in self.ANATOMICAL_ALLOW_LIST:
                if allowed in detected_text or detected_text in allowed:
                    # Additional check: is this likely a name or a clinical term?
                    # Names typically don't have medical context words nearby
                    context_start = max(0, result.start - 50)
                    context_end = min(len(text), result.end + 50)
                    context = text_lower[context_start:context_end]
                    
                    medical_context_words = ["lobe", "station", "bronch", "lung", "node"]
                    if any(word in context for word in medical_context_words):
                        is_allowed = True
                        logger.debug(f"Allowing in medical context: {detected_text}")
                        break
            
            if not is_allowed:
                filtered_results.append(result)
        
        return filtered_results
    
    def get_version(self) -> str:
        try:
            import presidio_analyzer
            return presidio_analyzer.__version__
        except:
            return "unknown"
```

3. Create the PHI Service that orchestrates the workflow:

```python
# app/phi/application/phi_service.py

import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID, uuid4

from app.phi.ports.phi_ports import EncryptionPort, PHIScrubberPort, AuditLoggerPort
from app.phi.models import AuditAction


class PHIService:
    """
    Orchestrates PHI detection, vaulting, and retrieval.
    
    Implements the physician-in-the-loop workflow:
    1. preview() - Auto-detect PHI for physician review
    2. confirm_and_vault() - Vault confirmed PHI, return scrubbed text
    3. reidentify() - Decrypt and merge for display
    """
    
    def __init__(
        self,
        scrubber: PHIScrubberPort,
        encryption: EncryptionPort,
        audit_logger: AuditLoggerPort,
    ):
        self._scrubber = scrubber
        self._encryption = encryption
        self._audit = audit_logger
    
    async def preview(
        self,
        text: str,
        user_id: str,
        document_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Step 1: Auto-detect PHI for physician review.
        
        Returns detected entities for the UI to highlight.
        Does NOT store anything yet.
        """
        preview_id = f"prev_{uuid4().hex[:12]}"
        
        # Run Presidio analysis
        results = self._scrubber.analyze(text)
        
        # Convert to response format
        entities = []
        for i, result in enumerate(results):
            entities.append({
                "id": f"auto-{i}",
                "text": text[result.start:result.end],
                "start": result.start,
                "end": result.end,
                "entity_type": self._map_entity_type(result.entity_type),
                "confidence": result.score,
                "source": "auto",
            })
        
        # Log the preview (no PHI stored)
        await self._audit.log(
            action=AuditAction.REVIEW_STARTED,
            user_id=user_id,
            metadata={
                "preview_id": preview_id,
                "text_length": len(text),
                "entities_detected": len(entities),
                "document_type": document_type,
            }
        )
        
        return {
            "raw_text": text,
            "entities": entities,
            "preview_id": preview_id,
            "presidio_version": self._scrubber.get_version(),
        }
    
    def vault_phi(
        self,
        raw_text: str,
        confirmed_entities: List[Dict[str, Any]],
    ) -> Tuple[UUID, str, bytes, str, List[Dict]]:
        """
        Step 2: Encrypt PHI and generate scrubbed text.
        
        Returns:
            - token_id: UUID linking vault to procedure data
            - scrubbed_text: Text with PHI replaced by placeholders
            - encrypted_phi: Encrypted PHI data
            - data_hash: SHA-256 of plaintext for integrity
            - entity_map: Mapping for reconstruction
        """
        token_id = uuid4()
        
        # Extract PHI values
        phi_data = {
            "entities": [
                {
                    "original_text": e["text"],
                    "original_start": e["start"],
                    "original_end": e["end"],
                    "entity_type": e["entity_type"],
                    "confidence": e.get("confidence", 1.0),
                    "source": e.get("source", "manual"),
                }
                for e in confirmed_entities
            ],
            "extracted_at": datetime.utcnow().isoformat(),
        }
        
        # Encrypt
        phi_json = json.dumps(phi_data)
        encrypted_phi = self._encryption.encrypt(phi_json)
        data_hash = hashlib.sha256(phi_json.encode()).hexdigest()
        
        # Generate scrubbed text
        scrubbed_text, entity_map = self._apply_scrubbing(raw_text, confirmed_entities)
        
        return token_id, scrubbed_text, encrypted_phi, data_hash, entity_map
    
    def reidentify(
        self,
        scrubbed_text: str,
        entity_map: List[Dict],
        encrypted_phi: bytes,
    ) -> Tuple[str, List[Dict]]:
        """
        Step 3: Decrypt PHI and reconstruct original text.
        """
        # Decrypt
        phi_json = self._encryption.decrypt(encrypted_phi)
        phi_data = json.loads(phi_json)
        
        # Reconstruct
        original_text = self._reconstruct_text(scrubbed_text, entity_map, phi_data)
        
        return original_text, phi_data.get("entities", [])
    
    def calculate_feedback_metrics(
        self,
        raw_text: str,
        confirmed_entities: List[Dict],
    ) -> Dict[str, Any]:
        """
        Calculate precision/recall of Presidio vs physician decisions.
        
        Used for ML improvement loop.
        """
        # Re-run Presidio to get original predictions
        presidio_results = self._scrubber.analyze(raw_text)
        
        presidio_set = {
            (r.start, r.end, r.entity_type)
            for r in presidio_results
        }
        
        confirmed_set = {
            (e["start"], e["end"], e["entity_type"])
            for e in confirmed_entities
        }
        
        true_positives = presidio_set & confirmed_set
        false_positives = presidio_set - confirmed_set
        false_negatives = confirmed_set - presidio_set
        
        tp = len(true_positives)
        fp = len(false_positives)
        fn = len(false_negatives)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            "true_positives": tp,
            "false_positives": [
                {"start": s, "end": e, "type": t, "text": raw_text[s:e]}
                for s, e, t in false_positives
            ],
            "false_negatives": [
                {"start": s, "end": e, "type": t, "text": raw_text[s:e]}
                for s, e, t in false_negatives
            ],
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
        }
    
    def _apply_scrubbing(
        self,
        raw_text: str,
        entities: List[Dict],
    ) -> Tuple[str, List[Dict]]:
        """Replace PHI with placeholders."""
        sorted_entities = sorted(entities, key=lambda e: e["start"], reverse=True)
        
        scrubbed = raw_text
        entity_map = []
        
        for i, entity in enumerate(sorted_entities):
            placeholder = f"<{entity['entity_type']}_{i}>"
            
            entity_map.append({
                "placeholder": placeholder,
                "entity_type": entity["entity_type"],
                "original_start": entity["start"],
                "original_end": entity["end"],
            })
            
            scrubbed = scrubbed[:entity["start"]] + placeholder + scrubbed[entity["end"]:]
        
        entity_map.reverse()
        return scrubbed, entity_map
    
    def _reconstruct_text(
        self,
        scrubbed_text: str,
        entity_map: List[Dict],
        phi_data: Dict,
    ) -> str:
        """Replace placeholders with original PHI."""
        result = scrubbed_text
        
        phi_lookup = {
            f"<{e['entity_type']}_{i}>": e["original_text"]
            for i, e in enumerate(phi_data.get("entities", []))
        }
        
        for entry in entity_map:
            placeholder = entry["placeholder"]
            if placeholder in phi_lookup:
                result = result.replace(placeholder, phi_lookup[placeholder])
        
        return result
    
    def _map_entity_type(self, presidio_type: str) -> str:
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
```

### 0.3 Add PHI Review Endpoints

**Files:**
- `app/api/routes/phi_review.py` (new)
- `app/api/dependencies.py` (update)

**Tasks:**

1. Create the PHI review router:

```python
# app/api/routes/phi_review.py

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from uuid import UUID
from datetime import datetime, timedelta

from app.api.dependencies import (
    get_phi_service, get_db_session, get_current_user, get_coding_service
)
from app.phi.schemas import (
    ScrubPreviewRequest, ScrubPreviewResponse,
    SubmitRequest, SubmitResponse,
    JobStatusResponse, ReidentifyRequest, ReidentifyResponse,
)
from app.phi.models import PHIVault, ProcedureData, AuditLog, ScrubbingFeedback
from app.phi.models import ProcessingStatus, AuditAction

router = APIRouter(prefix="/v1/phi", tags=["PHI Review"])


@router.post("/scrub/preview", response_model=ScrubPreviewResponse)
async def preview_scrub(
    request: ScrubPreviewRequest,
    http_request: Request,
    phi_service = Depends(get_phi_service),
    current_user = Depends(get_current_user),
):
    """
    Step 1: Preview PHI detection for physician review.
    
    Returns highlighted entities. Does not store anything.
    """
    result = await phi_service.preview(
        text=request.raw_text,
        user_id=current_user.id,
        document_type=request.document_type,
    )
    
    return ScrubPreviewResponse(
        raw_text=result["raw_text"],
        entities=result["entities"],
        preview_id=result["preview_id"],
        expires_at=datetime.utcnow() + timedelta(hours=1),
        presidio_version=result["presidio_version"],
        processing_time_ms=100,  # TODO: actual timing
    )


@router.post("/submit", response_model=SubmitResponse)
async def submit_for_coding(
    request: SubmitRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
    db = Depends(get_db_session),
    phi_service = Depends(get_phi_service),
    coding_service = Depends(get_coding_service),
    current_user = Depends(get_current_user),
):
    """
    Step 2: Vault PHI and submit for coding.
    
    Physician has confirmed PHI flagging. This endpoint:
    1. Encrypts and stores PHI in vault
    2. Stores scrubbed text
    3. Queues for CodingService processing
    """
    # Vault the PHI
    token_id, scrubbed_text, encrypted_phi, data_hash, entity_map = phi_service.vault_phi(
        raw_text=request.raw_text,
        confirmed_entities=[e.dict() for e in request.confirmed_phi],
    )
    
    # Store in database (single transaction)
    async with db.begin():
        # PHI Vault
        phi_vault = PHIVault(
            id=token_id,
            encrypted_data=encrypted_phi,
            data_hash=data_hash,
        )
        db.add(phi_vault)
        
        # Procedure Data
        procedure_data = ProcedureData(
            phi_vault_id=token_id,
            scrubbed_text=scrubbed_text,
            original_text_hash=hashlib.sha256(request.raw_text.encode()).hexdigest(),
            entity_map=entity_map,
            status=ProcessingStatus.PHI_CONFIRMED,
            document_type=request.document_type,
            specialty=request.specialty,
            submitted_by=current_user.id,
            reviewed_by=current_user.id,
            reviewed_at=datetime.utcnow(),
        )
        db.add(procedure_data)
        
        # Audit log
        audit = AuditLog(
            phi_vault_id=token_id,
            procedure_data_id=procedure_data.id,
            user_id=current_user.id,
            user_email=current_user.email,
            action=AuditAction.PHI_CREATED,
            action_detail=f"PHI vaulted with {len(request.confirmed_phi)} entities",
            ip_address=http_request.client.host,
            metadata={
                "entity_count": len(request.confirmed_phi),
                "document_type": request.document_type,
            }
        )
        db.add(audit)
        
        # Scrubbing feedback for ML improvement
        feedback_metrics = phi_service.calculate_feedback_metrics(
            raw_text=request.raw_text,
            confirmed_entities=[e.dict() for e in request.confirmed_phi],
        )
        feedback = ScrubbingFeedback(
            procedure_data_id=procedure_data.id,
            presidio_entities=feedback_metrics.get("presidio_raw", []),
            confirmed_entities=[e.dict() for e in request.confirmed_phi],
            false_positives=feedback_metrics["false_positives"],
            false_negatives=feedback_metrics["false_negatives"],
            true_positives=feedback_metrics["true_positives"],
            precision=feedback_metrics["precision"],
            recall=feedback_metrics["recall"],
            f1_score=feedback_metrics["f1_score"],
            document_type=request.document_type,
            specialty=request.specialty,
        )
        db.add(feedback)
    
    # Queue background processing with CodingService
    background_tasks.add_task(
        process_coding_job,
        job_id=token_id,
        scrubbed_text=scrubbed_text,
        procedure_type=request.document_type,
        coding_service=coding_service,
        db=db,
    )
    
    return SubmitResponse(
        job_id=token_id,
        status="phi_confirmed",
        message="PHI secured. Job queued for processing.",
        phi_entities_secured=len(request.confirmed_phi),
        scrubbed_text_preview=scrubbed_text[:200] + "..." if len(scrubbed_text) > 200 else scrubbed_text,
        status_url=f"/v1/phi/status/{token_id}",
        estimated_completion_seconds=30,
    )


async def process_coding_job(
    job_id: UUID,
    scrubbed_text: str,
    procedure_type: str,
    coding_service,
    db,
):
    """Background task to run CodingService on scrubbed text."""
    try:
        # Update status to processing
        await db.execute(
            update(ProcedureData)
            .where(ProcedureData.phi_vault_id == job_id)
            .values(status=ProcessingStatus.PROCESSING)
        )
        await db.commit()
        
        # Run coding
        result = coding_service.generate_result(
            note_id=str(job_id),
            report_text=scrubbed_text,
            procedure_type=procedure_type,
        )
        
        # Store results
        await db.execute(
            update(ProcedureData)
            .where(ProcedureData.phi_vault_id == job_id)
            .values(
                status=ProcessingStatus.COMPLETED,
                coding_results=result.dict() if hasattr(result, 'dict') else result,
                processed_at=datetime.utcnow(),
            )
        )
        await db.commit()
        
    except Exception as e:
        await db.execute(
            update(ProcedureData)
            .where(ProcedureData.phi_vault_id == job_id)
            .values(status=ProcessingStatus.FAILED)
        )
        await db.commit()
        raise


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: UUID,
    db = Depends(get_db_session),
    current_user = Depends(get_current_user),
):
    """Check status of a coding job."""
    result = await db.execute(
        select(ProcedureData).where(ProcedureData.phi_vault_id == job_id)
    )
    procedure_data = result.scalar_one_or_none()
    
    if not procedure_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if procedure_data.submitted_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return JobStatusResponse(
        job_id=job_id,
        status=procedure_data.status.value,
        message=_get_status_message(procedure_data.status),
        created_at=procedure_data.created_at,
        updated_at=procedure_data.created_at,
        completed_at=procedure_data.processed_at,
        coding_results=procedure_data.coding_results,
    )


@router.post("/reidentify", response_model=ReidentifyResponse)
async def reidentify_results(
    request: ReidentifyRequest,
    http_request: Request,
    db = Depends(get_db_session),
    phi_service = Depends(get_phi_service),
    current_user = Depends(get_current_user),
):
    """Re-attach PHI to results for authorized display."""
    # Fetch data
    result = await db.execute(
        select(ProcedureData, PHIVault)
        .join(PHIVault, ProcedureData.phi_vault_id == PHIVault.id)
        .where(ProcedureData.phi_vault_id == request.job_id)
    )
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    
    procedure_data, phi_vault = row
    
    # Auth check
    if procedure_data.submitted_by != current_user.id:
        # Log unauthorized attempt
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Decrypt and reconstruct
    original_text, phi_entities = phi_service.reidentify(
        scrubbed_text=procedure_data.scrubbed_text,
        entity_map=procedure_data.entity_map,
        encrypted_phi=phi_vault.encrypted_data,
    )
    
    # Audit the access
    audit = AuditLog(
        phi_vault_id=phi_vault.id,
        procedure_data_id=procedure_data.id,
        user_id=current_user.id,
        action=AuditAction.PHI_DECRYPTED,
        ip_address=http_request.client.host,
    )
    db.add(audit)
    await db.commit()
    
    return ReidentifyResponse(
        job_id=request.job_id,
        original_text=original_text if request.include_original_text else None,
        coding_results=procedure_data.coding_results,
        phi_entities=phi_entities,
        reidentified_at=datetime.utcnow(),
        reidentified_by=current_user.id,
    )
```

2. Update dependencies to include PHI services:

```python
# app/api/dependencies.py (additions)

from functools import lru_cache
from app.phi.application.phi_service import PHIService
from app.phi.adapters.presidio_adapter import PresidioAdapter
from app.phi.adapters.encryption_adapter import FernetEncryptionAdapter
from app.phi.adapters.audit_adapter import DatabaseAuditLogger


@lru_cache()
def get_presidio_adapter() -> PresidioAdapter:
    return PresidioAdapter()


@lru_cache()
def get_encryption_adapter() -> FernetEncryptionAdapter:
    key = os.environ.get("PHI_ENCRYPTION_KEY")
    if not key:
        raise ValueError("PHI_ENCRYPTION_KEY environment variable not set")
    return FernetEncryptionAdapter(key)


def get_phi_service(
    presidio = Depends(get_presidio_adapter),
    encryption = Depends(get_encryption_adapter),
    audit = Depends(get_audit_logger),
) -> PHIService:
    return PHIService(
        scrubber=presidio,
        encryption=encryption,
        audit_logger=audit,
    )
```

3. Register the router in `fastapi_app.py`:

```python
from app.api.routes.phi_review import router as phi_router
app.include_router(phi_router)
```

---

## Phase 1 – Hard Cutover: API Uses CodingService Everywhere

*(Original Phase 1, now with PHI integration)*

### 1.1 Update `/v1/coder/run` to Use CodingService

The key change: **the `/v1/coder/run` endpoint should now require PHI review first.**

**Option A: Require PHI Review (Recommended)**

Redirect users to the new PHI workflow:

```python
@router.post("/v1/coder/run")
def run_coder_legacy(request: CoderRequestModel):
    """
    DEPRECATED: Use /v1/phi/submit after reviewing PHI via /v1/phi/scrub/preview
    """
    raise HTTPException(
        status_code=400,
        detail={
            "error": "phi_review_required",
            "message": "Direct coding is no longer supported. Use the PHI review workflow.",
            "workflow": [
                "1. POST /v1/phi/scrub/preview - Get PHI highlights",
                "2. Review and confirm PHI in UI",
                "3. POST /v1/phi/submit - Submit with confirmed PHI",
                "4. GET /v1/phi/status/{job_id} - Check results",
            ]
        }
    )
```

**Option B: Backward Compatibility Mode**

Allow direct coding but log a deprecation warning:

```python
@router.post("/v1/coder/run", response_model=CodingResult, deprecated=True)
async def run_coder(
    request: CoderRequestModel,
    background_tasks: BackgroundTasks,
    service: CodingService = Depends(get_coding_service),
    phi_service: PHIService = Depends(get_phi_service),
    db = Depends(get_db_session),
    current_user = Depends(get_current_user),
):
    """
    DEPRECATED: Use /v1/phi/submit workflow for HIPAA compliance.
    
    This endpoint auto-scrubs and processes without physician review.
    """
    logger.warning(f"Legacy /v1/coder/run used by {current_user.id} - migrate to PHI workflow")
    
    # Auto-scrub (no physician review)
    preview = await phi_service.preview(request.report_text, current_user.id)
    
    # Auto-confirm all detected entities (no HITL)
    token_id, scrubbed_text, encrypted_phi, data_hash, entity_map = phi_service.vault_phi(
        raw_text=request.report_text,
        confirmed_entities=preview["entities"],
    )
    
    # Store and process
    # ... (similar to /v1/phi/submit but synchronous)
    
    result = service.generate_result(
        note_id=request.note_id,
        report_text=scrubbed_text,  # Use scrubbed text
        procedure_type=request.procedure_type,
    )
    
    return result
```

### 1.2 Remove EnhancedCPTCoder from FastAPI

*(Same as original plan)*

- Delete global singleton in `fastapi_app.py`
- Remove all imports of `EnhancedCPTCoder` from API layer
- Ensure `CodingService` is the single entry point

---

## Phase 2 – Kill Legacy LLM Path and Rule Duplication

*(Same as original, no changes)*

### 2.1 Remove Old LLM Client Usage
### 2.2 Eliminate Duplicate Rule/KB Logic

---

## Phase 3 – Finish Decoupling FastAPI App

*(Same as original, with PHI additions)*

### 3.1 Move NLP Warmup to Infra

Update to also warm Presidio:

```python
# app/infra/nlp_warmup.py

async def warm_heavy_resources():
    """Warm all heavy NLP resources including Presidio."""
    
    # spaCy, UMLS, etc.
    # ...
    
    # Presidio (uses spaCy under the hood)
    try:
        from app.phi.adapters.presidio_adapter import PresidioAdapter
        presidio = PresidioAdapter()
        # Run a test analysis to warm the model
        presidio.analyze("Test patient John Smith on 01/01/2024")
        logger.info("Presidio warmed successfully")
    except Exception as e:
        logger.warning(f"Presidio warmup failed: {e}")
```

### 3.2 DI as Single Source

Add PHI dependencies to the composition root:

```python
# app/api/dependencies.py

# All dependencies in one place:
# - get_coding_service()
# - get_phi_service()
# - get_presidio_adapter()
# - get_encryption_adapter()
# - get_audit_logger()
# - get_db_session()
# - get_current_user()
```

---

## Phase 4 – Tests, Cleanup, and Regression Guardrails

*(Updated to include PHI workflow tests)*

### 4.1 Add PHI Workflow Integration Tests

```python
# tests/integration/api/test_phi_workflow.py

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_phi_preview_detects_entities(client: AsyncClient):
    """PHI preview should detect names and dates."""
    response = await client.post("/v1/phi/scrub/preview", json={
        "raw_text": "Patient John Smith underwent EBUS on 03/15/2024.",
        "document_type": "procedure_note",
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Should detect PERSON and DATE
    entity_types = {e["entity_type"] for e in data["entities"]}
    assert "PERSON" in entity_types
    assert "DATE" in entity_types


@pytest.mark.asyncio
async def test_phi_preview_preserves_anatomical_terms(client: AsyncClient):
    """PHI preview should NOT flag anatomical terms."""
    response = await client.post("/v1/phi/scrub/preview", json={
        "raw_text": "EBUS of LEFT UPPER LOBE, Station 7, and right paratracheal nodes.",
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # These should NOT be flagged
    flagged_texts = {e["text"].lower() for e in data["entities"]}
    assert "left upper lobe" not in flagged_texts
    assert "station 7" not in flagged_texts
    assert "right paratracheal" not in flagged_texts


@pytest.mark.asyncio
async def test_phi_submit_creates_vault_entry(client: AsyncClient, db_session):
    """Submit should create encrypted vault entry."""
    response = await client.post("/v1/phi/submit", json={
        "raw_text": "Patient John Smith MRN 12345.",
        "confirmed_phi": [
            {"text": "John Smith", "start": 8, "end": 18, "entity_type": "PERSON", "source": "auto", "confidence": 0.98},
            {"text": "12345", "start": 23, "end": 28, "entity_type": "MRN", "source": "auto", "confidence": 0.95},
        ],
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify vault entry exists
    job_id = data["job_id"]
    vault_entry = await db_session.get(PHIVault, job_id)
    assert vault_entry is not None
    assert vault_entry.encrypted_data is not None


@pytest.mark.asyncio
async def test_scrubbed_text_has_no_phi(client: AsyncClient):
    """Scrubbed text should have placeholders, not PHI."""
    response = await client.post("/v1/phi/submit", json={
        "raw_text": "Patient John Smith MRN 12345.",
        "confirmed_phi": [
            {"text": "John Smith", "start": 8, "end": 18, "entity_type": "PERSON", "source": "auto", "confidence": 0.98},
        ],
    })
    
    data = response.json()
    preview = data["scrubbed_text_preview"]
    
    # Should have placeholder, not name
    assert "John Smith" not in preview
    assert "<PERSON" in preview


@pytest.mark.asyncio
async def test_audit_log_created_on_access(client: AsyncClient, db_session):
    """Every PHI access should create an audit entry."""
    # First, create a record
    submit_response = await client.post("/v1/phi/submit", json={...})
    job_id = submit_response.json()["job_id"]
    
    # Then reidentify
    await client.post("/v1/phi/reidentify", json={"job_id": job_id})
    
    # Check audit log
    audits = await db_session.execute(
        select(AuditLog).where(AuditLog.phi_vault_id == job_id)
    )
    audit_actions = [a.action for a in audits.scalars()]
    
    assert AuditAction.PHI_CREATED in audit_actions
    assert AuditAction.PHI_DECRYPTED in audit_actions
```

### 4.2 Add Scrubbing Feedback Tests

```python
# tests/integration/test_scrubbing_feedback.py

@pytest.mark.asyncio
async def test_feedback_captures_false_positives(client, db_session):
    """When physician unflaggs an item, it should be recorded as false positive."""
    # Preview detects "Smith" as PERSON
    preview = await client.post("/v1/phi/scrub/preview", json={
        "raw_text": "Smith's fracture of the left ankle.",  # Medical term, not a name
    })
    
    presidio_entities = preview.json()["entities"]
    
    # Physician unflaggs (empty confirmed list)
    await client.post("/v1/phi/submit", json={
        "raw_text": "Smith's fracture of the left ankle.",
        "confirmed_phi": [],  # Physician says: no PHI here
    })
    
    # Check feedback was recorded
    feedback = await db_session.execute(select(ScrubbingFeedback).limit(1))
    feedback = feedback.scalar_one()
    
    assert len(feedback.false_positives) > 0
    assert feedback.precision < 1.0  # Not perfect
```

---

## Phase 5 (NEW) – Frontend Integration

### 5.1 Add PHI Review Component

Add the React component to your frontend:

```
frontend/
├── src/
│   ├── components/
│   │   ├── PHIReviewEditor.jsx    # From our phi_review_system
│   │   └── PHIReviewDemo.jsx
│   └── pages/
│       └── CodingWorkflow.jsx     # Main page using PHI review
```

### 5.2 Update API Client

```typescript
// frontend/src/api/phiApi.ts

export const phiApi = {
  preview: async (rawText: string, documentType?: string) => {
    const response = await fetch('/v1/phi/scrub/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw_text: rawText, document_type: documentType }),
    });
    return response.json();
  },
  
  submit: async (rawText: string, confirmedPhi: PHIEntity[]) => {
    const response = await fetch('/v1/phi/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw_text: rawText, confirmed_phi: confirmedPhi }),
    });
    return response.json();
  },
  
  getStatus: async (jobId: string) => {
    const response = await fetch(`/v1/phi/status/${jobId}`);
    return response.json();
  },
  
  reidentify: async (jobId: string) => {
    const response = await fetch('/v1/phi/reidentify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId, include_original_text: true }),
    });
    return response.json();
  },
};
```

---

## Environment Variables

Add to your `.env`:

```bash
# PHI Encryption (CRITICAL - generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
PHI_ENCRYPTION_KEY=your-generated-key-here

# Presidio configuration
PRESIDIO_NLP_MODEL=en_core_web_lg

# Feature flags
CODER_USE_LLM_ADVISOR=true
CODER_REQUIRE_PHI_REVIEW=true  # Set to false for backward compat
```

---

## Migration Checklist

```
Phase 0: PHI Infrastructure
[ ] Create app/phi/ directory structure
[ ] Add database models (PHIVault, AuditLog, ScrubbingFeedback)
[ ] Run migrations
[ ] Implement PresidioAdapter with IP allow-lists
[ ] Implement FernetEncryptionAdapter
[ ] Implement PHIService
[ ] Add /v1/phi/* endpoints
[ ] Test encryption/decryption round-trip
[ ] Test Presidio preserves anatomical terms

Phase 1: Hard Cutover
[ ] Update /v1/coder/run to require PHI workflow (or deprecate)
[ ] Remove EnhancedCPTCoder from FastAPI
[ ] Ensure CodingService receives scrubbed text

Phase 2: Legacy Cleanup
[ ] Remove old LLM client
[ ] Mark proc_autocode/ as deprecated
[ ] Standardize on single KB

Phase 3: Composition
[ ] Move warmup to infra (include Presidio)
[ ] Centralize all DI in dependencies.py

Phase 4: Tests
[ ] Add PHI workflow integration tests
[ ] Add scrubbing feedback tests
[ ] Run regression comparison

Phase 5: Frontend
[ ] Add PHI Review components
[ ] Update API client
[ ] Test full workflow end-to-end
```

---

## Summary of Changes from Original Plan

| Original | Updated |
|----------|---------|
| Direct LLM access to raw text | LLM only sees scrubbed text |
| No PHI protection layer | Full vault pattern with encryption |
| No audit trail | Comprehensive HIPAA audit logging |
| Presidio scrubs everything | Physician reviews and corrects PHI flags |
| No ML feedback loop | Precision/recall tracking for Presidio tuning |
| Single `/v1/coder/run` endpoint | Multi-step PHI review workflow |

The key architectural insight: **the physician IS the reviewer**, eliminating the traditional HITL bottleneck while ensuring clinical context is preserved.
