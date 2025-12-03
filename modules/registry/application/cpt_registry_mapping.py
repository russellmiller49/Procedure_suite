"""CPT code to registry field mapping.

Maps CPT codes to IP Registry schema fields for automatic population
of boolean flags and structured fields during registry export.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RegistryFieldMapping:
    """Mapping from a CPT code to registry fields.

    Attributes:
        fields: Dict of field names to values to set (e.g., {"ebus_performed": True})
        hints: Dict of hints for fields that need additional context
               (e.g., {"station_count_hint": "1-2"} for 31652)
        v3_only_fields: Fields only applicable to v3 schema
    """
    fields: dict[str, Any] = field(default_factory=dict)
    hints: dict[str, str] = field(default_factory=dict)
    v3_only_fields: dict[str, Any] = field(default_factory=dict)


# CPT code mappings to IP Registry fields
# Based on common interventional pulmonology procedures
CPT_TO_REGISTRY_MAPPING: dict[str, RegistryFieldMapping] = {
    # Diagnostic bronchoscopy base code
    "31622": RegistryFieldMapping(
        fields={},  # Base bronchoscopy, no specific registry flags
        hints={"procedure_type": "diagnostic_bronchoscopy"},
    ),

    # BAL
    "31624": RegistryFieldMapping(
        fields={"bal_performed": True},
        hints={"procedure_type": "bronchoalveolar_lavage"},
    ),

    # Navigation bronchoscopy
    "31627": RegistryFieldMapping(
        fields={"navigation_performed": True},
        hints={"navigation_type": "electromagnetic"},
    ),

    # Transbronchial lung biopsy
    "31628": RegistryFieldMapping(
        fields={"tblb_performed": True},
        hints={"biopsy_technique": "forceps"},
    ),

    # TBLB with fluoroscopy
    "31629": RegistryFieldMapping(
        fields={"tblb_performed": True},
        hints={"biopsy_technique": "forceps_fluoro"},
    ),

    # EBUS-TBNA 1-2 stations
    "31652": RegistryFieldMapping(
        fields={"ebus_performed": True},
        hints={"station_count_hint": "1-2", "procedure_type": "ebus_tbna"},
    ),

    # EBUS-TBNA 3+ stations
    "31653": RegistryFieldMapping(
        fields={"ebus_performed": True},
        hints={"station_count_hint": "3+", "procedure_type": "ebus_tbna"},
    ),

    # Bronchial brush biopsy
    "31623": RegistryFieldMapping(
        fields={},
        hints={"biopsy_technique": "brush"},
    ),

    # Bronchial alveolar lavage protected
    "31625": RegistryFieldMapping(
        fields={"bal_performed": True},
        hints={"bal_type": "protected"},
    ),

    # Bronchial stent placement
    "31636": RegistryFieldMapping(
        fields={"stent_placed": True},
        hints={"stent_type": "initial_placement"},
    ),

    # Bronchial stent revision
    "31637": RegistryFieldMapping(
        fields={"stent_placed": True},
        hints={"stent_type": "revision"},
    ),

    # Dilation bronchoscopy
    "31630": RegistryFieldMapping(
        fields={"dilation_performed": True},
        hints={"dilation_technique": "balloon"},
    ),

    # Rigid bronchoscopy (therapeutic)
    "31641": RegistryFieldMapping(
        fields={},
        hints={"scope_type": "rigid", "procedure_type": "therapeutic"},
    ),

    # Bronchial thermoplasty
    "31660": RegistryFieldMapping(
        fields={"ablation_performed": True},
        hints={"ablation_technique": "thermoplasty"},
        v3_only_fields={"ablation_technique": "thermoplasty"},
    ),
    "31661": RegistryFieldMapping(
        fields={"ablation_performed": True},
        hints={"ablation_technique": "thermoplasty"},
        v3_only_fields={"ablation_technique": "thermoplasty"},
    ),

    # Endobronchial valve placement (BLVR)
    "31647": RegistryFieldMapping(
        fields={"blvr_performed": True},
        hints={"procedure_type": "blvr_valve_initial"},
    ),
    "31648": RegistryFieldMapping(
        fields={"blvr_performed": True},
        hints={"procedure_type": "blvr_valve_additional"},
    ),
    "31649": RegistryFieldMapping(
        fields={"blvr_performed": True},
        hints={"procedure_type": "blvr_valve_removal"},
    ),

    # Thoracentesis (not directly in IP registry but may indicate pleural involvement)
    "32555": RegistryFieldMapping(
        fields={},  # Not a registry field directly
        hints={"pleural_procedure": "thoracentesis_imaging"},
    ),
    "32556": RegistryFieldMapping(
        fields={},
        hints={"pleural_procedure": "thoracentesis_with_catheter"},
    ),
    "32557": RegistryFieldMapping(
        fields={},
        hints={"pleural_procedure": "chest_tube_imaging"},
    ),

    # Pleuroscopy / VATS
    "32601": RegistryFieldMapping(
        fields={},
        hints={"pleural_procedure": "pleuroscopy_diagnostic"},
    ),
    "32650": RegistryFieldMapping(
        fields={},
        hints={"pleural_procedure": "pleurodesis"},
    ),

    # Cryotherapy / ablation
    "31641": RegistryFieldMapping(
        fields={"ablation_performed": True},
        hints={"ablation_technique": "cryotherapy"},
        v3_only_fields={"ablation_technique": "cryotherapy"},
    ),

    # Radial EBUS
    "31620": RegistryFieldMapping(
        fields={"radial_ebus_performed": True},
        hints={"procedure_type": "radial_ebus"},
    ),
}


def get_registry_fields_for_code(
    code: str,
    version: str = "v2",
) -> dict[str, Any]:
    """Get registry fields to set based on a CPT code.

    Args:
        code: CPT code (e.g., "31652")
        version: Registry schema version ("v2" or "v3")

    Returns:
        Dict of field names to values for the registry entry.
        Returns empty dict if code is not mapped.
    """
    mapping = CPT_TO_REGISTRY_MAPPING.get(code)
    if not mapping:
        return {}

    result = dict(mapping.fields)

    # Add v3-only fields if applicable
    if version == "v3":
        result.update(mapping.v3_only_fields)

    return result


def get_registry_hints_for_code(code: str) -> dict[str, str]:
    """Get hints for a CPT code mapping.

    These hints provide context for more detailed field population
    that may require additional processing (e.g., parsing station count).

    Args:
        code: CPT code

    Returns:
        Dict of hint keys to hint values.
    """
    mapping = CPT_TO_REGISTRY_MAPPING.get(code)
    if not mapping:
        return {}
    return dict(mapping.hints)


def aggregate_registry_fields(
    codes: list[str],
    version: str = "v2",
) -> dict[str, Any]:
    """Aggregate registry fields from multiple CPT codes.

    Combines fields from multiple codes, with later codes overwriting
    earlier ones for the same field. Boolean fields use OR semantics.

    Args:
        codes: List of CPT codes
        version: Registry schema version

    Returns:
        Aggregated dict of registry fields.
    """
    result: dict[str, Any] = {}

    for code in codes:
        fields = get_registry_fields_for_code(code, version)
        for field_name, value in fields.items():
            if field_name in result and isinstance(value, bool):
                # For boolean fields, use OR semantics
                result[field_name] = result[field_name] or value
            else:
                result[field_name] = value

    return result


def aggregate_registry_hints(codes: list[str]) -> dict[str, list[str]]:
    """Aggregate hints from multiple CPT codes.

    Collects all hints into lists, allowing multiple values per key.

    Args:
        codes: List of CPT codes

    Returns:
        Dict mapping hint keys to lists of hint values.
    """
    result: dict[str, list[str]] = {}

    for code in codes:
        hints = get_registry_hints_for_code(code)
        for key, value in hints.items():
            if key not in result:
                result[key] = []
            if value not in result[key]:
                result[key].append(value)

    return result
