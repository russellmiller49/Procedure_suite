"""Configuration settings using pydantic-settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class CoderSettings(BaseSettings):
    """Settings for the CPT coding pipeline."""

    model_version: str = "gemini-2.5-flash"
    kb_path: str = "data/knowledge/ip_coding_billing_v2_9.json"
    kb_version: str = "v3_0"
    keyword_mapping_dir: str = "data/keyword_mappings"
    keyword_mapping_version: str = "v1"

    # Smart hybrid thresholds
    advisor_confidence_auto_accept: float = 0.85
    rule_confidence_low_threshold: float = 0.6
    context_window_chars: int = 200

    # CMS conversion factor (updated annually by CMS)
    # CY 2026 Medicare Physician Fee Schedule Conversion Factor (non-QP)
    # Override via CODER_CMS_CONVERSION_FACTOR environment variable
    cms_conversion_factor: float = 33.4009

    model_config = {"env_prefix": "CODER_"}


class ReporterSettings(BaseSettings):
    """Settings for the reporter pipeline."""

    llm_model: str = "gemini-2.5-flash"
    max_retries: int = 3
    cache_strategy: str = "by_note_hash"
    fast_path_confidence_threshold: float = 0.95
    timeout_per_attempt_ms: int = 5000

    model_config = {"env_prefix": "REPORTER_"}


class RegistrySettings(BaseSettings):
    """Settings for registry export."""

    default_registry_version: str = "v2"
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    model_config = {"env_prefix": "REGISTRY_"}


class LLMExtractionConfig(BaseSettings):
    """Settings for LLM extraction with self-correction."""

    max_retries: int = 3
    cache_strategy: str = "by_note_hash"
    fast_path_confidence_threshold: float = 0.95
    timeout_per_attempt_ms: int = 5000

    model_config = {"env_prefix": "LLM_"}
