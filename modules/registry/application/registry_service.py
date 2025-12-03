"""Registry Service for exporting procedure data to the IP Registry.

This application-layer service orchestrates:
- Building registry entries from final codes and procedure metadata
- Mapping CPT codes to registry boolean flags
- Validating entries against the registry schema
- Managing export state
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any, Literal

from pydantic import BaseModel, ValidationError

from modules.common.exceptions import RegistryError
from modules.registry.adapters.schema_registry import (
    RegistrySchemaRegistry,
    get_schema_registry,
)
from modules.registry.application.cpt_registry_mapping import (
    aggregate_registry_fields,
    aggregate_registry_hints,
)
from proc_schemas.coding import FinalCode, CodingResult
from proc_schemas.registry.ip_v2 import (
    IPRegistryV2,
    PatientInfo as PatientInfoV2,
    ProcedureInfo as ProcedureInfoV2,
)
from proc_schemas.registry.ip_v3 import (
    IPRegistryV3,
    PatientInfo as PatientInfoV3,
    ProcedureInfo as ProcedureInfoV3,
)


@dataclass
class RegistryDraftResult:
    """Result from building a draft registry entry."""

    entry: IPRegistryV2 | IPRegistryV3
    completeness_score: float
    missing_fields: list[str]
    suggested_values: dict[str, Any]
    warnings: list[str]
    hints: dict[str, list[str]]  # Aggregated hints from CPT mappings


@dataclass
class RegistryExportResult:
    """Result from exporting a procedure to the registry."""

    entry: IPRegistryV2 | IPRegistryV3
    registry_id: str
    schema_version: str
    export_id: str
    export_timestamp: datetime
    status: Literal["success", "partial", "failed"]
    warnings: list[str] = field(default_factory=list)


class RegistryService:
    """Application service for registry export operations.

    This service:
    - Builds registry entries from coding results and procedure metadata
    - Maps CPT codes to registry boolean flags using cpt_registry_mapping
    - Validates entries against Pydantic schemas
    - Produces structured export results with warnings
    """

    VERSION = "registry_service_v1"

    def __init__(
        self,
        schema_registry: RegistrySchemaRegistry | None = None,
        default_version: str = "v2",
    ):
        """Initialize RegistryService.

        Args:
            schema_registry: Registry for versioned schemas. Uses default if None.
            default_version: Default schema version to use if not specified.
        """
        self.schema_registry = schema_registry or get_schema_registry()
        self.default_version = default_version

    def build_draft_entry(
        self,
        procedure_id: str,
        final_codes: list[FinalCode],
        procedure_metadata: dict[str, Any] | None = None,
        version: str | None = None,
    ) -> RegistryDraftResult:
        """Build a draft registry entry from final codes and metadata.

        This method:
        1. Maps CPT codes to registry boolean flags
        2. Merges with provided procedure metadata
        3. Validates against the target schema
        4. Computes completeness score and missing fields

        Args:
            procedure_id: The procedure identifier
            final_codes: List of approved FinalCode objects
            procedure_metadata: Optional dict with patient/procedure info
            version: Schema version ("v2" or "v3"), defaults to default_version

        Returns:
            RegistryDraftResult with entry, completeness, and warnings
        """
        version = version or self.default_version
        metadata = procedure_metadata or {}
        warnings: list[str] = []
        missing_fields: list[str] = []

        # Extract CPT codes
        cpt_codes = [fc.code for fc in final_codes]

        # Get aggregated registry fields from CPT mappings
        registry_fields = aggregate_registry_fields(cpt_codes, version)
        hints = aggregate_registry_hints(cpt_codes)

        # Build patient info
        patient_info = self._build_patient_info(metadata, version, missing_fields)

        # Build procedure info
        procedure_info = self._build_procedure_info(
            procedure_id, metadata, version, missing_fields
        )

        # Build the registry entry based on version
        if version == "v3":
            entry = self._build_v3_entry(
                procedure_id=procedure_id,
                patient=patient_info,
                procedure=procedure_info,
                registry_fields=registry_fields,
                metadata=metadata,
            )
        else:
            entry = self._build_v2_entry(
                procedure_id=procedure_id,
                patient=patient_info,
                procedure=procedure_info,
                registry_fields=registry_fields,
                metadata=metadata,
            )

        # Validate and generate warnings
        validation_warnings = self._validate_entry(entry, version)
        warnings.extend(validation_warnings)

        # Compute completeness score
        completeness_score = self._compute_completeness(entry, missing_fields)

        # Suggest values based on hints
        suggested_values = self._generate_suggestions(hints, entry)

        return RegistryDraftResult(
            entry=entry,
            completeness_score=completeness_score,
            missing_fields=missing_fields,
            suggested_values=suggested_values,
            warnings=warnings,
            hints=hints,
        )

    def export_procedure(
        self,
        procedure_id: str,
        final_codes: list[FinalCode],
        procedure_metadata: dict[str, Any] | None = None,
        version: str | None = None,
    ) -> RegistryExportResult:
        """Export a procedure to the registry.

        This method:
        1. Builds a draft entry using build_draft_entry()
        2. Generates an export ID for tracking
        3. Returns a structured export result

        Note: Actual persistence is handled by the caller (API layer),
        keeping this service focused on business logic.

        Args:
            procedure_id: The procedure identifier
            final_codes: List of approved FinalCode objects
            procedure_metadata: Optional dict with patient/procedure info
            version: Schema version ("v2" or "v3")

        Returns:
            RegistryExportResult with entry and export metadata

        Raises:
            RegistryError: If export fails due to validation errors
        """
        version = version or self.default_version

        # Build the draft entry
        draft = self.build_draft_entry(
            procedure_id=procedure_id,
            final_codes=final_codes,
            procedure_metadata=procedure_metadata,
            version=version,
        )

        # Generate export ID
        export_id = f"export_{uuid.uuid4().hex[:12]}"
        export_timestamp = datetime.utcnow()

        # Determine status based on completeness
        if draft.completeness_score >= 0.8:
            status: Literal["success", "partial", "failed"] = "success"
        elif draft.completeness_score >= 0.5:
            status = "partial"
            draft.warnings.append(
                f"Export completed with partial data (completeness: {draft.completeness_score:.0%})"
            )
        else:
            # Still allow export but mark as partial
            status = "partial"
            draft.warnings.append(
                f"Low completeness score ({draft.completeness_score:.0%}). "
                "Consider adding more procedure metadata."
            )

        return RegistryExportResult(
            entry=draft.entry,
            registry_id="ip_registry",
            schema_version=version,
            export_id=export_id,
            export_timestamp=export_timestamp,
            status=status,
            warnings=draft.warnings,
        )

    def _build_patient_info(
        self,
        metadata: dict[str, Any],
        version: str,
        missing_fields: list[str],
    ) -> PatientInfoV2 | PatientInfoV3:
        """Build PatientInfo from metadata."""
        patient_data = metadata.get("patient", {})

        patient_id = patient_data.get("patient_id", "")
        mrn = patient_data.get("mrn", "")
        age = patient_data.get("age")
        sex = patient_data.get("sex")

        if not patient_id and not mrn:
            missing_fields.append("patient.patient_id or patient.mrn")

        # For v3, use PatientInfoV3 with additional fields
        if version == "v3":
            bmi = patient_data.get("bmi")
            smoking_status = patient_data.get("smoking_status")
            return PatientInfoV3(
                patient_id=patient_id,
                mrn=mrn,
                age=age,
                sex=sex,
                bmi=bmi,
                smoking_status=smoking_status,
            )
        else:
            return PatientInfoV2(
                patient_id=patient_id,
                mrn=mrn,
                age=age,
                sex=sex,
            )

    def _build_procedure_info(
        self,
        procedure_id: str,
        metadata: dict[str, Any],
        version: str,
        missing_fields: list[str],
    ) -> ProcedureInfoV2 | ProcedureInfoV3:
        """Build ProcedureInfo from metadata."""
        proc_data = metadata.get("procedure", {})

        procedure_date = proc_data.get("procedure_date")
        if isinstance(procedure_date, str):
            try:
                procedure_date = date.fromisoformat(procedure_date)
            except ValueError:
                procedure_date = None

        if not procedure_date:
            missing_fields.append("procedure.procedure_date")

        procedure_type = proc_data.get("procedure_type", "")
        indication = proc_data.get("indication", "")
        urgency = proc_data.get("urgency", "routine")

        if not indication:
            missing_fields.append("procedure.indication")

        # For v3, use ProcedureInfoV3 with additional fields
        if version == "v3":
            operator = proc_data.get("operator", "")
            facility = proc_data.get("facility", "")
            return ProcedureInfoV3(
                procedure_id=procedure_id,
                procedure_date=procedure_date,
                procedure_type=procedure_type,
                indication=indication,
                urgency=urgency,
                operator=operator,
                facility=facility,
            )
        else:
            return ProcedureInfoV2(
                procedure_id=procedure_id,
                procedure_date=procedure_date,
                procedure_type=procedure_type,
                indication=indication,
                urgency=urgency,
            )

    def _build_v2_entry(
        self,
        procedure_id: str,
        patient: PatientInfoV2,
        procedure: ProcedureInfoV2,
        registry_fields: dict[str, Any],
        metadata: dict[str, Any],
    ) -> IPRegistryV2:
        """Build an IPRegistryV2 entry."""
        # Start with base entry
        entry_data: dict[str, Any] = {
            "patient": patient,
            "procedure": procedure,
        }

        # Apply registry fields from CPT mappings
        entry_data.update(registry_fields)

        # Apply any direct overrides from metadata
        for key in [
            "sedation",
            "ebus_stations",
            "tblb_sites",
            "bal_sites",
            "navigation_system",
            "stents",
            "findings",
            "complications",
            "disposition",
            "impression",
            "recommendations",
        ]:
            if key in metadata:
                entry_data[key] = metadata[key]

        # Handle any_complications flag
        complications = metadata.get("complications", [])
        if complications:
            entry_data["any_complications"] = True

        return IPRegistryV2(**entry_data)

    def _build_v3_entry(
        self,
        procedure_id: str,
        patient: PatientInfoV3,
        procedure: ProcedureInfoV3,
        registry_fields: dict[str, Any],
        metadata: dict[str, Any],
    ) -> IPRegistryV3:
        """Build an IPRegistryV3 entry."""
        entry_data: dict[str, Any] = {
            "patient": patient,
            "procedure": procedure,
        }

        # Apply registry fields from CPT mappings
        entry_data.update(registry_fields)

        # Apply v3-specific fields from metadata
        v3_fields = [
            "sedation",
            "events",
            "ebus_stations",
            "ebus_station_count",
            "tblb_sites",
            "tblb_technique",
            "navigation_target_reached",
            "radial_ebus_findings",
            "bal_sites",
            "bal_volume_ml",
            "bal_return_ml",
            "dilation_sites",
            "dilation_technique",
            "stents",
            "ablation_sites",
            "blvr_chartis_performed",
            "blvr_cv_result",
            "findings",
            "complications",
            "outcome",
            "disposition",
            "length_of_stay_hours",
            "impression",
            "recommendations",
        ]

        for key in v3_fields:
            if key in metadata:
                entry_data[key] = metadata[key]

        # Handle any_complications flag
        complications = metadata.get("complications", [])
        if complications:
            entry_data["any_complications"] = True

        return IPRegistryV3(**entry_data)

    def _validate_entry(
        self,
        entry: IPRegistryV2 | IPRegistryV3,
        version: str,
    ) -> list[str]:
        """Validate an entry and return warnings."""
        warnings: list[str] = []

        # Check for common data quality issues
        if not entry.patient.patient_id and not entry.patient.mrn:
            warnings.append("Patient identifier missing (patient_id or mrn)")

        if not entry.procedure.procedure_date:
            warnings.append("Procedure date not specified")

        if not entry.procedure.indication:
            warnings.append("Procedure indication not specified")

        # Check for procedure-specific completeness
        if entry.ebus_performed and not entry.ebus_stations:
            warnings.append("EBUS performed but no stations documented")

        if entry.tblb_performed and not entry.tblb_sites:
            warnings.append("TBLB performed but no biopsy sites documented")

        if entry.bal_performed and not entry.bal_sites:
            warnings.append("BAL performed but no sites documented")

        if entry.stent_placed and not entry.stents:
            warnings.append("Stent placed but no stent details documented")

        return warnings

    def _compute_completeness(
        self,
        entry: IPRegistryV2 | IPRegistryV3,
        missing_fields: list[str],
    ) -> float:
        """Compute a completeness score for the entry.

        Score is based on:
        - Required fields present (patient ID, date, indication)
        - Procedure-specific fields when relevant
        """
        max_score = 10.0
        score = max_score

        # Deduct for missing required fields
        required_deductions = {
            "patient.patient_id or patient.mrn": 2.0,
            "procedure.procedure_date": 1.5,
            "procedure.indication": 1.0,
        }

        for field in missing_fields:
            if field in required_deductions:
                score -= required_deductions[field]

        # Deduct for procedure-specific missing data
        if entry.ebus_performed and not entry.ebus_stations:
            score -= 0.5
        if entry.tblb_performed and not entry.tblb_sites:
            score -= 0.5
        if entry.stent_placed and not entry.stents:
            score -= 0.5

        return max(0.0, score / max_score)

    def _generate_suggestions(
        self,
        hints: dict[str, list[str]],
        entry: IPRegistryV2 | IPRegistryV3,
    ) -> dict[str, Any]:
        """Generate suggested values based on hints and entry state."""
        suggestions: dict[str, Any] = {}

        # Suggest EBUS station count based on CPT hint
        if "station_count_hint" in hints:
            hint_values = hints["station_count_hint"]
            if "3+" in hint_values:
                suggestions["ebus_station_count"] = "3 or more stations (based on 31653)"
            elif "1-2" in hint_values:
                suggestions["ebus_station_count"] = "1-2 stations (based on 31652)"

        # Suggest navigation system if navigation performed
        if entry.navigation_performed and not entry.navigation_system:
            suggestions["navigation_system"] = "Consider specifying navigation system"

        return suggestions


# Factory function for DI
def get_registry_service() -> RegistryService:
    """Get a RegistryService instance with default configuration."""
    return RegistryService()
