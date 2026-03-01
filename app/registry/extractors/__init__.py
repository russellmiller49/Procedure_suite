# Registry extractors module
from app.registry.slots.base import SlotResult

from .llm_detailed import LLMDetailedExtractor
from .v3_extractor import extract_v3_draft

__all__ = ["LLMDetailedExtractor", "SlotResult", "extract_v3_draft"]
