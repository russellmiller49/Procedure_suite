"""Granular NER module for procedure note entity extraction."""

from modules.ner.inference import GranularNERPredictor, NEREntity, NERExtractionResult
from modules.ner.entity_types import EntityCategory, get_entity_category, CPT_RELEVANT_ENTITIES

__all__ = [
    "GranularNERPredictor",
    "NEREntity",
    "NERExtractionResult",
    "EntityCategory",
    "get_entity_category",
    "CPT_RELEVANT_ENTITIES",
]
