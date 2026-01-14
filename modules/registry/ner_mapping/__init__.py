"""NER-to-Registry mapping module.

Maps granular NER entities to RegistryRecord fields for deterministic
CPT code derivation.
"""

from modules.registry.ner_mapping.entity_to_registry import (
    NERToRegistryMapper,
    RegistryMappingResult,
)
from modules.registry.ner_mapping.station_extractor import EBUSStationExtractor
from modules.registry.ner_mapping.procedure_extractor import ProcedureExtractor

__all__ = [
    "NERToRegistryMapper",
    "RegistryMappingResult",
    "EBUSStationExtractor",
    "ProcedureExtractor",
]
