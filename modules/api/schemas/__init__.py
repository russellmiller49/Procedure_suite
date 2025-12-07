"""API schemas package.

This package contains all Pydantic schemas for the FastAPI integration layer.
"""

# Base schemas (legacy compatibility)
from modules.api.schemas.base import (
    CoderRequest,
    CoderResponse,
    HybridPipelineMetadata,
    KnowledgeMeta,
    QARunRequest,
    RegistryRequest,
    RegistryResponse,
    RenderRequest,
    RenderResponse,
    VerifyRequest,
    VerifyResponse,
)

# QA pipeline schemas (new structured response)
from modules.api.schemas.qa import (
    CodeEntry,
    CoderData,
    ModuleResult,
    ModuleStatus,
    QARunResponse,
    RegistryData,
    ReporterData,
)

__all__ = [
    # Base schemas
    "CoderRequest",
    "CoderResponse",
    "HybridPipelineMetadata",
    "KnowledgeMeta",
    "QARunRequest",
    "RegistryRequest",
    "RegistryResponse",
    "RenderRequest",
    "RenderResponse",
    "VerifyRequest",
    "VerifyResponse",
    # QA pipeline schemas
    "CodeEntry",
    "CoderData",
    "ModuleResult",
    "ModuleStatus",
    "QARunResponse",
    "RegistryData",
    "ReporterData",
]
