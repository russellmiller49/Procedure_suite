"""Registry schema entrypoint.

This module is the stable import surface for the dynamic registry model
(`RegistryRecord`) and related helpers.

Implementation lives in `app.registry.schema.v2_dynamic` while this file keeps
`app.registry.schema.<submodule>` imports working via the `__path__` shim.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

# Allow `app.registry.schema.<submodule>` imports even though this file is a module.
# This lets us keep backwards compatibility while adding an `app/registry/schema/` folder.
__path__ = [str(Path(__file__).with_name("schema"))]

from app.registry.schema.ebus_events import NodeActionType, NodeInteraction, NodeOutcomeType
from app.registry.schema.v2_dynamic import (
    AspirationEvent,
    BiopsySite,
    BLVRData,
    CaoIntervention,
    CUSTOM_FIELD_TYPES,
    DestructionEvent,
    EnhancedDilationEvent,
    LinearEBUSProcedure,
)
from app.registry.schema_granular import (
    EnhancedRegistryGranularData,
    derive_aggregate_fields,
    validate_ebus_consistency,
)

if TYPE_CHECKING:
    class RegistryRecord(BaseModel):
        """Typing facade for the dynamically-built runtime model.

        The runtime `RegistryRecord` is created via `create_model`, which mypy
        treats as a variable assignment and rejects in type positions. This
        facade preserves strict static typing while runtime imports still use
        the dynamic model from `v2_dynamic`.
        """

        evidence: dict[str, list[Any]] = Field(default_factory=dict)
        procedures_performed: Any | None = None
        granular_data: Any | None = None

        def __getattr__(self, name: str) -> Any: ...

else:
    from app.registry.schema.v2_dynamic import RegistryRecord

__all__ = [
    "RegistryRecord",
    "BLVRData",
    "DestructionEvent",
    "EnhancedDilationEvent",
    "AspirationEvent",
    "CaoIntervention",
    "BiopsySite",
    "LinearEBUSProcedure",
    "CUSTOM_FIELD_TYPES",
    "NodeActionType",
    "NodeInteraction",
    "NodeOutcomeType",
    # Granular data exports
    "EnhancedRegistryGranularData",
    "validate_ebus_consistency",
    "derive_aggregate_fields",
]
