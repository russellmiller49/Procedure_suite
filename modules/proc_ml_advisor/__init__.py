"""
ML Advisor Module for Procedure Suite

This module provides ML/LLM-based advisory capabilities for CPT/HCPCS coding.
The advisor suggests codes but does not override the deterministic rule engine.

Key Design Principles:
- Rules remain authoritative (v1): Advisor only suggests, never decides
- Transparent: All disagreements clearly marked
- Auditable: Complete trace logging for evaluation
- Pluggable: Multiple backends (stub, gemini, future: openai, local)

Usage:
    from modules.proc_ml_advisor import (
        MLAdvisorInput,
        MLAdvisorSuggestion,
        HybridCodingResult,
        CodingTrace,
    )
"""

from modules.proc_ml_advisor.schemas import (
    # Enums
    AdvisorBackend,
    CodingPolicy,
    CodeType,
    ConfidenceLevel,
    ProcedureCategory,
    # Code-level models
    CodeWithConfidence,
    CodeModifier,
    NCCIWarning,
    # Structured report models
    SamplingStation,
    PleuralProcedureDetails,
    BronchoscopyProcedureDetails,
    SedationDetails,
    StructuredProcedureReport,
    # ML Advisor models
    MLAdvisorInput,
    MLAdvisorSuggestion,
    # Hybrid result models
    RuleEngineResult,
    HybridCodingResult,
    # Coding trace model
    CodingTrace,
    # API models
    CodeRequest,
    CodeResponse,
    EvaluationMetrics,
)

__all__ = [
    # Enums
    "AdvisorBackend",
    "CodingPolicy",
    "CodeType",
    "ConfidenceLevel",
    "ProcedureCategory",
    # Code-level models
    "CodeWithConfidence",
    "CodeModifier",
    "NCCIWarning",
    # Structured report models
    "SamplingStation",
    "PleuralProcedureDetails",
    "BronchoscopyProcedureDetails",
    "SedationDetails",
    "StructuredProcedureReport",
    # ML Advisor models
    "MLAdvisorInput",
    "MLAdvisorSuggestion",
    # Hybrid result models
    "RuleEngineResult",
    "HybridCodingResult",
    # Coding trace model
    "CodingTrace",
    # API models
    "CodeRequest",
    "CodeResponse",
    "EvaluationMetrics",
]
