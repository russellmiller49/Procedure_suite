"""Dependency injection factories for API endpoints.

Provides fully wired service instances for FastAPI dependency injection.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from config.settings import CoderSettings
from modules.coder.application.coding_service import CodingService
from modules.coder.adapters.persistence.csv_kb_adapter import JsonKnowledgeBaseAdapter
from modules.coder.adapters.nlp.keyword_mapping_loader import YamlKeywordMappingRepository
from modules.coder.adapters.nlp.simple_negation_detector import SimpleNegationDetector
from modules.coder.adapters.llm.gemini_advisor import GeminiAdvisorAdapter, MockLLMAdvisor
from modules.domain.coding_rules.rule_engine import RuleEngine
from modules.domain.procedure_store.repository import ProcedureStore
from modules.coder.adapters.persistence.inmemory_procedure_store import (
    InMemoryProcedureStore,
)
from modules.registry.application.registry_service import RegistryService
from modules.registry.adapters.schema_registry import get_schema_registry
from observability.logging_config import get_logger

logger = get_logger("api_dependencies")

# Global singleton for the procedure store (supports both memory and supabase backends)
_procedure_store: ProcedureStore | None = None


@lru_cache(maxsize=1)
def get_coder_settings() -> CoderSettings:
    """Get cached CoderSettings from environment."""
    return CoderSettings()


@lru_cache(maxsize=1)
def get_coding_service() -> CodingService:
    """Create a fully wired CodingService instance.

    This factory:
    - Loads CoderSettings from environment
    - Instantiates JsonKnowledgeBaseAdapter (KnowledgeBaseRepository)
    - Instantiates YamlKeywordMappingRepository
    - Instantiates SimpleNegationDetector
    - Instantiates RuleEngine using the KB
    - Instantiates GeminiAdvisorAdapter (or MockLLMAdvisor in rules_only mode)
    - Returns a CodingService with all dependencies wired

    The instance is cached for reuse across requests.
    """
    config = get_coder_settings()
    logger.info(
        "Initializing CodingService",
        extra={
            "kb_path": config.kb_path,
            "kb_version": config.kb_version,
            "keyword_mapping_dir": config.keyword_mapping_dir,
        },
    )

    # 1. Knowledge base repository
    kb_repo = JsonKnowledgeBaseAdapter(config.kb_path)
    logger.info(f"Loaded KB version: {kb_repo.version}")

    # 2. Keyword mapping repository
    keyword_repo = YamlKeywordMappingRepository(config.keyword_mapping_dir)
    logger.info(f"Loaded keyword mappings version: {keyword_repo.version}")

    # 3. Negation detector
    negation_detector = SimpleNegationDetector()
    logger.info(f"Negation detector version: {negation_detector.version}")

    # 4. Rule engine
    rule_engine = RuleEngine(kb_repo)
    logger.info(f"Rule engine version: {rule_engine.version}")

    # 5. LLM advisor (conditionally enabled)
    llm_advisor: Optional[GeminiAdvisorAdapter | MockLLMAdvisor] = None
    use_llm = os.getenv("CODER_USE_LLM_ADVISOR", "").lower() in ("true", "1", "yes")

    if use_llm:
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if api_key:
            llm_advisor = GeminiAdvisorAdapter(
                model_name=config.model_version,
                allowed_codes=list(kb_repo.get_all_codes()),
                api_key=api_key,
            )
            logger.info(f"LLM advisor enabled: {config.model_version}")
        else:
            logger.warning("GOOGLE_API_KEY not set, LLM advisor disabled")
    else:
        logger.info("LLM advisor disabled (CODER_USE_LLM_ADVISOR not set)")

    # 6. Build CodingService
    service = CodingService(
        kb_repo=kb_repo,
        keyword_repo=keyword_repo,
        negation_detector=negation_detector,
        rule_engine=rule_engine,
        llm_advisor=llm_advisor,
        config=config,
    )

    logger.info("CodingService initialized successfully")
    return service


def reset_coding_service_cache() -> None:
    """Reset the cached CodingService instance.

    Useful for testing or when settings change.
    """
    get_coding_service.cache_clear()
    get_coder_settings.cache_clear()


@lru_cache(maxsize=1)
def get_registry_service() -> RegistryService:
    """Create a RegistryService instance for registry export operations.

    This factory:
    - Uses the default RegistrySchemaRegistry for schema access
    - Configures default version from environment (REGISTRY_DEFAULT_VERSION)
    - Returns a cached instance for reuse across requests
    """
    import os

    default_version = os.getenv("REGISTRY_DEFAULT_VERSION", "v2")
    schema_registry = get_schema_registry()

    service = RegistryService(
        schema_registry=schema_registry,
        default_version=default_version,
    )

    logger.info(
        "RegistryService initialized",
        extra={"default_version": default_version},
    )

    return service


def reset_registry_service_cache() -> None:
    """Reset the cached RegistryService instance.

    Useful for testing or when settings change.
    """
    get_registry_service.cache_clear()


def get_procedure_store() -> ProcedureStore:
    """Get the procedure store instance.

    This factory:
    - Reads PROCEDURE_STORE_BACKEND environment variable (default: "memory")
    - If "memory" → returns InMemoryProcedureStore singleton
    - If "supabase" → returns SupabaseProcedureStore singleton (requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)

    The instance is cached as a singleton for reuse across requests.

    Returns:
        ProcedureStore implementation based on configuration
    """
    global _procedure_store

    if _procedure_store is not None:
        return _procedure_store

    backend = os.getenv("PROCEDURE_STORE_BACKEND", "memory").lower()

    if backend == "supabase":
        # Try to use Supabase backend
        from modules.coder.adapters.persistence.supabase_procedure_store import (
            is_supabase_available,
            SupabaseProcedureStore,
        )

        if is_supabase_available():
            try:
                _procedure_store = SupabaseProcedureStore()
                logger.info("ProcedureStore initialized with Supabase backend")
                return _procedure_store
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Supabase store, falling back to memory: {e}"
                )
        else:
            logger.warning(
                "Supabase credentials not configured, falling back to memory backend"
            )

    # Default: in-memory backend
    _procedure_store = InMemoryProcedureStore()
    logger.info("ProcedureStore initialized with in-memory backend")
    return _procedure_store


def reset_procedure_store() -> None:
    """Reset the procedure store singleton.

    This clears all data and resets the singleton to None,
    forcing a fresh instance on the next get_procedure_store() call.

    Useful for testing to ensure clean state between tests.
    """
    global _procedure_store

    if _procedure_store is not None:
        _procedure_store.clear_all()
        _procedure_store = None
        logger.debug("ProcedureStore reset")
