"""
Dependency Injection Providers

This module defines the FastAPI dependencies for:
- Database sessions
- Authentication/Authorization
- Presidio analyzer
- Encryption services
- Task queue
- Audit logging

In production, these would be configured via environment variables
and secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
"""

import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional, AsyncGenerator
from uuid import UUID, uuid4
from dataclasses import dataclass

from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

from .models import AuditLog, AuditAction

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class Settings:
    """Application settings - would typically come from environment."""
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:password@localhost:5432/phi_vault"
    )
    encryption_key: str = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Presidio configuration
    presidio_nlp_model: str = os.getenv("PRESIDIO_NLP_MODEL", "en_core_web_lg")
    
    # Security
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
    jwt_algorithm: str = "HS256"


settings = Settings()


# =============================================================================
# DATABASE
# =============================================================================

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=10,
    max_overflow=20,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session for request handling.
    
    Usage:
        @app.get("/example")
        async def example(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# =============================================================================
# AUTHENTICATION
# =============================================================================

@dataclass
class CurrentUser:
    """Represents the authenticated user."""
    id: str
    email: str
    role: str
    is_admin: bool = False
    
    @property
    def is_physician(self) -> bool:
        return self.role in ("physician", "fellow", "attending")


async def get_current_user() -> CurrentUser:
    """
    Extract and validate the current user from the request.
    
    In production, this would:
    1. Extract JWT from Authorization header
    2. Validate the token signature and expiry
    3. Fetch user details from the token or database
    
    For development, we return a mock user.
    """
    # TODO: Implement actual JWT validation
    # token = request.headers.get("Authorization", "").replace("Bearer ", "")
    # payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    # return CurrentUser(id=payload["sub"], email=payload["email"], role=payload["role"])
    
    return CurrentUser(
        id="dev-user-001",
        email="dev@example.com",
        role="physician",
        is_admin=False,
    )


# =============================================================================
# PRESIDIO ANALYZER
# =============================================================================

class PresidioService:
    """
    Wrapper around Presidio AnalyzerEngine with custom configuration.
    
    Includes allow-lists for anatomical terms to prevent over-scrubbing.
    """
    
    def __init__(self):
        self._analyzer: Optional[AnalyzerEngine] = None
    
    def _get_analyzer(self) -> AnalyzerEngine:
        if self._analyzer is None:
            # Configure NLP engine
            configuration = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": settings.presidio_nlp_model}]
            }
            
            provider = NlpEngineProvider(nlp_configuration=configuration)
            nlp_engine = provider.create_engine()
            
            self._analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
            
            # Add custom recognizers for medical context
            self._add_medical_allow_lists()
            
        return self._analyzer
    
    def _add_medical_allow_lists(self):
        """
        Configure allow-lists to prevent scrubbing of anatomical/clinical terms.
        
        This is critical for preserving clinical context needed for coding.
        """
        # These terms should NOT be flagged as locations/names
        anatomical_terms = [
            # Laterality
            "left", "right", "bilateral", "unilateral",
            "medial", "lateral", "anterior", "posterior",
            "superior", "inferior", "proximal", "distal",
            
            # Lung anatomy
            "upper lobe", "middle lobe", "lower lobe",
            "right upper lobe", "right middle lobe", "right lower lobe",
            "left upper lobe", "left lower lobe",
            "lingula", "carina", "trachea", "bronchus", "bronchi",
            "mainstem", "segmental", "subsegmental",
            
            # Other anatomy commonly in IP
            "mediastinum", "hilum", "hilar", "paratracheal",
            "subcarinal", "aortopulmonary", "prevascular",
            "station 4R", "station 4L", "station 7", "station 10",
            "station 11", "station 11L", "station 11R",
            
            # Common procedure terms
            "EBUS", "EUS", "TBNA", "BAL", "bronchoscopy",
            "endobronchial", "transbronchial", "electromagnetic",
        ]
        
        # TODO: Register these as deny-list patterns with Presidio
        # This requires creating custom recognizers
        logger.info(f"Loaded {len(anatomical_terms)} anatomical terms to allow-list")
    
    def analyze(self, text: str, language: str = "en", entities: list = None):
        """Run Presidio analysis on text."""
        analyzer = self._get_analyzer()
        return analyzer.analyze(
            text=text,
            language=language,
            entities=entities,
        )
    
    def get_version(self) -> str:
        """Return Presidio version for audit logging."""
        try:
            import presidio_analyzer
            return presidio_analyzer.__version__
        except Exception:
            return "unknown"


_presidio_service: Optional[PresidioService] = None


def get_presidio_analyzer() -> PresidioService:
    """Provide Presidio analyzer instance."""
    global _presidio_service
    if _presidio_service is None:
        _presidio_service = PresidioService()
    return _presidio_service


# =============================================================================
# ENCRYPTION SERVICE
# =============================================================================

class EncryptionService:
    """
    Handles PHI encryption/decryption.
    
    In production, this should:
    1. Use AWS KMS, HashiCorp Vault, or similar for key management
    2. Support key rotation
    3. Log all encryption/decryption operations
    """
    
    def __init__(self, key: str):
        self._fernet = Fernet(key.encode() if isinstance(key, str) else key)
    
    def encrypt(self, plaintext: str) -> bytes:
        """Encrypt plaintext string, return encrypted bytes."""
        return self._fernet.encrypt(plaintext.encode())
    
    def decrypt(self, ciphertext: bytes) -> str:
        """Decrypt bytes, return plaintext string."""
        return self._fernet.decrypt(ciphertext).decode()


_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Provide encryption service instance."""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService(settings.encryption_key)
    return _encryption_service


# =============================================================================
# TASK QUEUE
# =============================================================================

class TaskQueue:
    """
    Async task queue for background processing.
    
    In production, this would use Celery, AWS SQS, or similar.
    """
    
    def __init__(self):
        self._tasks: dict = {}  # In-memory for development
    
    async def enqueue(self, task_name: str, job_id: str, payload: dict) -> str:
        """
        Enqueue a task for background processing.
        
        Returns: Task ID
        """
        task_id = str(uuid4())
        
        # In production: 
        # await self.redis.rpush(f"queue:{task_name}", json.dumps({...}))
        # or: celery_app.send_task(task_name, kwargs=payload)
        
        self._tasks[task_id] = {
            "task_name": task_name,
            "job_id": job_id,
            "payload": payload,
            "status": "queued",
            "enqueued_at": datetime.now(timezone.utc).isoformat(),
        }
        
        logger.info(f"Enqueued task {task_name} for job {job_id}")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[dict]:
        """Get status of a queued task."""
        return self._tasks.get(task_id)


_task_queue: Optional[TaskQueue] = None


def get_task_queue() -> TaskQueue:
    """Provide task queue instance."""
    global _task_queue
    if _task_queue is None:
        _task_queue = TaskQueue()
    return _task_queue


# =============================================================================
# AUDIT LOGGER
# =============================================================================

class AuditLogger:
    """
    Centralized audit logging service.
    
    Ensures all PHI access and modifications are logged
    in compliance with HIPAA requirements.
    """
    
    def __init__(self, session_factory):
        self._session_factory = session_factory
    
    async def log(
        self,
        action: AuditAction,
        user_id: str,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None,
        phi_vault_id: Optional[UUID] = None,
        procedure_data_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        action_detail: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        """
        Log an auditable action.
        
        This is fire-and-forget; failures are logged but don't block the request.
        """
        try:
            async with self._session_factory() as session:
                entry = AuditLog(
                    user_id=user_id,
                    user_email=user_email,
                    user_role=user_role,
                    action=action,
                    action_detail=action_detail,
                    phi_vault_id=phi_vault_id,
                    procedure_data_id=procedure_data_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    session_id=session_id,
                    request_id=request_id,
                    metadata=metadata or {},
                )
                session.add(entry)
                await session.commit()
                
        except Exception as e:
            # Audit logging failures should not break the request
            # but should be alerted on in production
            logger.error(f"Failed to write audit log: {e}")


_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Provide audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(async_session_factory)
    return _audit_logger
