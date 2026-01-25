"""Registry schema entrypoint.

This module is the stable import surface for the dynamic registry model
(`RegistryRecord`) and related helpers.

Implementation lives in `modules.registry.schema.v2_dynamic` while this file keeps
`modules.registry.schema.<submodule>` imports working via the `__path__` shim.
"""

from __future__ import annotations

from pathlib import Path

# Allow `modules.registry.schema.<submodule>` imports even though this file is a module.
# This lets us keep backwards compatibility while adding a `modules/registry/schema/` folder.
__path__ = [str(Path(__file__).with_name("schema"))]

from modules.registry.schema.ebus_events import NodeActionType, NodeInteraction, NodeOutcomeType
from modules.registry.schema.v2_dynamic import (
    AspirationEvent,
    BiopsySite,
    BLVRData,
    CaoIntervention,
    CUSTOM_FIELD_TYPES,
    DestructionEvent,
    EnhancedDilationEvent,
    LinearEBUSProcedure,
    RegistryRecord,
)
from modules.registry.schema_granular import (
    EnhancedRegistryGranularData,
    derive_aggregate_fields,
    validate_ebus_consistency,
)

__all__ = [
    "RegistryRecord",
    "BLVRData",
    "DestructionEvent",
    "EnhancedDilationEvent",
    "AspirationEvent",
    "CaoIntervention",
    "BiopsySite",
    # Granular data exports
    "EnhancedRegistryGranularData",
    "validate_ebus_consistency",
    "derive_aggregate_fields",
]

