"""Registry Service for exporting procedure data to the IP Registry.

This application-layer service orchestrates:
- Building registry entries from final codes and procedure metadata
- Mapping CPT codes to registry boolean flags
- Validating entries against the registry schema
- Managing export state
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Any, Literal, TYPE_CHECKING

import os
from pydantic import BaseModel, ValidationError

from modules.common.exceptions import RegistryError
from modules.common.logger import get_logger
from modules.registry.adapters.schema_registry import (
    RegistrySchemaRegistry,
    get_schema_registry,
)
from modules.registry.application.cpt_registry_mapping import (
    aggregate_registry_fields,
    aggregate_registry_fields_flat,
    aggregate_registry_hints,
)
from modules.registry.application.registry_builder import (
    RegistryBuilderProtocol,
    get_builder,
)
from modules.registry.engine import RegistryEngine
from modules.registry.schema import RegistryRecord
from modules.registry.schema_granular import derive_procedures_from_granular
from modules.registry.processing.masking import mask_extraction_noise
from modules.registry.audit.audit_types import AuditCompareReport, AuditPrediction

logger = get_logger("registry_service")
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
from modules.coder.application.smart_hybrid_policy import (
    SmartHybridOrchestrator,
    HybridCoderResult,
)
from modules.ml_coder.registry_predictor import RegistryMLPredictor
from modules.registry.model_runtime import get_registry_runtime_dir, resolve_model_backend
from modules.coder.parallel_pathway import ParallelPathwayOrchestrator
from modules.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails


if TYPE_CHECKING:
    from modules.registry.self_correction.types import SelfCorrectionMetadata


def focus_note_for_extraction(note_text: str) -> tuple[str, dict[str, Any]]:
    """Optionally focus/summarize a note for deterministic extraction.

    Guardrail: RAW-ML auditing must always run on the full raw note text and
    must never use the focused/summarized text.
    """
    from modules.registry.extraction.focus import focus_note_for_extraction as _focus

    return _focus(note_text)


_HEADER_START_RE = re.compile(
    r"(?:\bPROCEDURE\b|\bPROCEDURES\b|\bOPERATION\b|\bOPERATIONS\b)\s*:?",
    re.IGNORECASE,
)
_HEADER_END_RE = re.compile(
    r"(?:\bANESTHESIA\b|\bINDICATION\b|\bDESCRIPTION\b|\bFINDINGS\b)",
    re.IGNORECASE,
)
_CPT_RE = re.compile(r"\b([37]\d{4})\b")


def _extract_procedure_header_block(text: str) -> str | None:
    """Return the block immediately following the procedure header (signals only)."""
    if not text:
        return None

    start = _HEADER_START_RE.search(text)
    if not start:
        return None

    after = text[start.end() :]
    end = _HEADER_END_RE.search(after)
    header_body = after[: end.start()] if end else after[:1500]
    header_body = header_body.strip()
    return header_body or None


def _scan_header_for_codes(text: str) -> set[str]:
    """Scan the procedure header block for explicit CPT codes (e.g., 31653)."""
    header = _extract_procedure_header_block(text)
    if not header:
        return set()
    return set(_CPT_RE.findall(header))


def _hash_note_text(text: str) -> str:
    normalized = (text or "").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _append_self_correction_log(path: str, payload: dict[str, Any]) -> None:
    if not path:
        return
    try:
        log_path = Path(path)
        if log_path.exists() and log_path.is_dir():
            logger.warning("Self-correction log path is a directory: %s", log_path)
            return
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
    except Exception as exc:
        logger.warning("Failed to write self-correction log: %s", exc)


def _apply_granular_up_propagation(record: RegistryRecord) -> tuple[RegistryRecord, list[str]]:
    """Apply granular→aggregate propagation using derive_procedures_from_granular().

    This must remain the single place where granular evidence drives aggregate
    performed flags.
    """
    if record.granular_data is None:
        return record, []

    granular = record.granular_data.model_dump()
    existing_procedures = (
        record.procedures_performed.model_dump() if record.procedures_performed is not None else None
    )

    updated_procs, granular_warnings = derive_procedures_from_granular(
        granular_data=granular,
        existing_procedures=existing_procedures,
    )

    if not updated_procs and not granular_warnings:
        return record, []

    record_data = record.model_dump()
    if updated_procs:
        record_data["procedures_performed"] = updated_procs
    record_data.setdefault("granular_validation_warnings", [])
    record_data["granular_validation_warnings"].extend(granular_warnings)

    return RegistryRecord(**record_data), granular_warnings


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


@dataclass
class RegistryExtractionResult:
    """Result from hybrid-first registry field extraction.

    Combines:
    - CPT codes from SmartHybridOrchestrator
    - Registry fields mapped from CPT codes
    - Extracted fields from RegistryEngine
    - Validation results and manual review flags
    - ML audit results comparing CPT-derived flags with ML predictions

    Attributes:
        record: The extracted RegistryRecord.
        cpt_codes: CPT codes from the hybrid coder.
        coder_difficulty: Case difficulty (HIGH_CONF/GRAY_ZONE/LOW_CONF).
        coder_source: Where codes came from (ml_rules_fastpath/hybrid_llm_fallback).
        mapped_fields: Registry fields derived from CPT mapping.
        code_rationales: Deterministic derivation rationales keyed by CPT code.
        derivation_warnings: Warnings emitted during deterministic CPT derivation.
        warnings: Non-blocking warnings about the extraction.
        needs_manual_review: Whether this case requires human review.
        validation_errors: List of validation errors found during reconciliation.
        audit_warnings: ML vs CPT discrepancy warnings requiring human review.
    """

    record: RegistryRecord
    cpt_codes: list[str]
    coder_difficulty: str
    coder_source: str
    mapped_fields: dict[str, Any]
    code_rationales: dict[str, str] = field(default_factory=dict)
    derivation_warnings: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    needs_manual_review: bool = False
    validation_errors: list[str] = field(default_factory=list)
    audit_warnings: list[str] = field(default_factory=list)
    audit_report: AuditCompareReport | None = None
    self_correction: list["SelfCorrectionMetadata"] = field(default_factory=list)


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
        hybrid_orchestrator: SmartHybridOrchestrator | None = None,
        registry_engine: RegistryEngine | None = None,
        parallel_orchestrator: ParallelPathwayOrchestrator | None = None,
    ):
        """Initialize RegistryService.

        Args:
            schema_registry: Registry for versioned schemas. Uses default if None.
            default_version: Default schema version to use if not specified.
            hybrid_orchestrator: Optional SmartHybridOrchestrator for ML-first coding.
            registry_engine: Optional RegistryEngine for field extraction. Lazy-init if None.
        """
        self.schema_registry = schema_registry or get_schema_registry()
        self.default_version = default_version
        self.hybrid_orchestrator = hybrid_orchestrator
        self._registry_engine = registry_engine
        self._registry_ml_predictor: Any | None = None
        self._ml_predictor_init_attempted: bool = False
        self.parallel_orchestrator = parallel_orchestrator or ParallelPathwayOrchestrator()
        self.clinical_guardrails = ClinicalGuardrails()

    @property
    def registry_engine(self) -> RegistryEngine:
        """Lazy initialization of RegistryEngine."""
        if self._registry_engine is None:
            self._registry_engine = RegistryEngine()
        return self._registry_engine

    def _get_registry_ml_predictor(self) -> Any | None:
        """Get registry ML predictor with lazy initialization.

        Behavior:
        - If MODEL_BACKEND is set to "onnx", require ONNX and fail fast if unavailable.
        - If MODEL_BACKEND is set to "pytorch", prefer Torch and fall back to sklearn if unavailable.
        - Otherwise ("auto"), keep legacy behavior: try ONNX first (if available),
          then sklearn TF-IDF.

        Returns the predictor if available, or None if artifacts are missing.
        Logs once on initialization failure to avoid log spam.
        """
        if self._ml_predictor_init_attempted:
            return self._registry_ml_predictor

        self._ml_predictor_init_attempted = True

        backend = resolve_model_backend()
        runtime_dir = get_registry_runtime_dir()

        def _try_pytorch() -> Any | None:
            try:
                from modules.registry.inference_pytorch import TorchRegistryPredictor

                predictor = TorchRegistryPredictor(bundle_dir=runtime_dir)
                if predictor.available:
                    logger.info(
                        "Using TorchRegistryPredictor with %d labels",
                        len(getattr(predictor, "labels", [])),
                    )
                    return predictor
                logger.debug("Torch predictor initialized but not available")
            except ImportError as e:
                logger.debug("PyTorch/Transformers not available (%s)", e)
            except Exception as e:
                logger.debug("Torch predictor init failed (%s)", e)
            return None

        def _try_onnx() -> Any | None:
            try:
                from modules.registry.inference_onnx import ONNXRegistryPredictor

                # Prefer runtime bundle paths if present; otherwise keep defaults.
                model_path: Path | None = None
                for candidate in ("registry_model_int8.onnx", "registry_model.onnx"):
                    p = runtime_dir / candidate
                    if p.exists():
                        model_path = p
                        break

                tokenizer_path: Path | None = None
                for candidate in ("tokenizer", "roberta_registry_tokenizer"):
                    p = runtime_dir / candidate
                    if p.exists():
                        tokenizer_path = p
                        break

                thresholds_path: Path | None = None
                for candidate in ("thresholds.json", "registry_thresholds.json", "roberta_registry_thresholds.json"):
                    p = runtime_dir / candidate
                    if p.exists():
                        thresholds_path = p
                        break

                label_fields_path = (
                    runtime_dir / "registry_label_fields.json"
                    if (runtime_dir / "registry_label_fields.json").exists()
                    else None
                )

                predictor = ONNXRegistryPredictor(
                    model_path=model_path,
                    tokenizer_path=tokenizer_path,
                    thresholds_path=thresholds_path,
                    label_fields_path=label_fields_path,
                )
                if predictor.available:
                    logger.info(
                        "Using ONNXRegistryPredictor with %d labels",
                        len(getattr(predictor, "labels", [])),
                    )
                    return predictor
                logger.debug("ONNX model not available")
            except ImportError:
                logger.debug("ONNX runtime not available")
            except Exception as e:
                logger.debug("ONNX predictor init failed (%s)", e)
            return None

        if backend == "pytorch":
            predictor = _try_pytorch()
            if predictor is not None:
                self._registry_ml_predictor = predictor
                return self._registry_ml_predictor
        elif backend == "onnx":
            predictor = _try_onnx()
            if predictor is None:
                model_path = runtime_dir / "registry_model_int8.onnx"
                raise RuntimeError(
                    "MODEL_BACKEND=onnx but ONNXRegistryPredictor failed to initialize. "
                    f"Expected model at {model_path}."
                )
            self._registry_ml_predictor = predictor
            return self._registry_ml_predictor
        else:
            predictor = _try_onnx()
            if predictor is not None:
                self._registry_ml_predictor = predictor
                return self._registry_ml_predictor

        # Fall back to TF-IDF sklearn predictor
        try:
            self._registry_ml_predictor = RegistryMLPredictor()
            if not self._registry_ml_predictor.available:
                logger.warning(
                    "RegistryMLPredictor initialized but not available "
                    "(model artifacts missing). ML hybrid audit disabled."
                )
                self._registry_ml_predictor = None
            else:
                logger.info(
                    "Using RegistryMLPredictor (TF-IDF) with %d labels",
                    len(self._registry_ml_predictor.labels),
                )
        except Exception:
            logger.exception(
                "Failed to initialize RegistryMLPredictor; ML hybrid audit disabled."
            )
            self._registry_ml_predictor = None

        return self._registry_ml_predictor

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
        registry_fields = aggregate_registry_fields_flat(cpt_codes, version)
        hints = aggregate_registry_hints(cpt_codes)

        # Get the appropriate builder for this version
        builder = get_builder(version)

        # Build patient and procedure info using the builder
        patient_info = builder.build_patient(metadata, missing_fields)
        procedure_info = builder.build_procedure(procedure_id, metadata, missing_fields)

        # Build the registry entry using the builder
        entry = builder.build_entry(
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

    # NOTE: _build_patient_info, _build_procedure_info, _build_v2_entry, and
    # _build_v3_entry have been refactored into the registry_builder module
    # using the Strategy Pattern. See registry_builder.py for V2RegistryBuilder
    # and V3RegistryBuilder.

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

    # -------------------------------------------------------------------------
    # Hybrid-First Registry Extraction
    # -------------------------------------------------------------------------

    def extract_fields(self, note_text: str, mode: str = "default") -> RegistryExtractionResult:
        """Extract registry fields using hybrid-first flow.

        This method orchestrates:
        1. Run hybrid coder to get CPT codes and difficulty classification
        2. Map CPT codes to registry boolean flags
        3. Run RegistryEngine extractor with coder context as hints
        4. Merge CPT-driven fields into the extraction result
        5. Validate and finalize the result

        Args:
            note_text: The procedure note text.
            mode: Optional override (e.g., "parallel_ner").

        Returns:
            RegistryExtractionResult with extracted record and metadata.
        """
        masked_note_text, _mask_meta = mask_extraction_noise(note_text)

        if mode == "parallel_ner":
            predictor = self._get_registry_ml_predictor()
            result = self.parallel_orchestrator.run_parallel_process(
                masked_note_text,
                ml_predictor=predictor,
            )
            return self._apply_guardrails_to_result(masked_note_text, result)

        pipeline_mode = os.getenv("PROCSUITE_PIPELINE_MODE", "current").strip().lower()
        if pipeline_mode != "extraction_first":
            allow_legacy = os.getenv("PROCSUITE_ALLOW_LEGACY_PIPELINES", "0").strip().lower() in {
                "1",
                "true",
                "yes",
                "y",
            }
            if not allow_legacy:
                raise ValueError(
                    "Legacy pipelines are disabled. Set PROCSUITE_ALLOW_LEGACY_PIPELINES=1 to enable."
                )
        if pipeline_mode == "extraction_first":
            return self._extract_fields_extraction_first(note_text)

        # Legacy fallback: if no hybrid orchestrator is injected, run extractor only
        if self.hybrid_orchestrator is None:
            logger.info("No hybrid_orchestrator configured, running extractor-only mode")
            record = self.registry_engine.run(masked_note_text, context={"schema_version": "v3"})
            if isinstance(record, tuple):
                record = record[0]  # Unpack if evidence included
            return RegistryExtractionResult(
                record=record,
                cpt_codes=[],
                coder_difficulty="unknown",
                coder_source="extractor_only",
                mapped_fields={},
                warnings=["No hybrid orchestrator configured - CPT codes not extracted"],
            )

        # 1. Run Hybrid Coder
        logger.debug("Running hybrid coder for registry extraction")
        coder_result: HybridCoderResult = self.hybrid_orchestrator.get_codes(masked_note_text)

        # 2. Map Codes to Registry Fields
        mapped_fields = aggregate_registry_fields(
            coder_result.codes, version=self.default_version
        )
        logger.debug(
            "Mapped %d CPT codes to registry fields",
            len(coder_result.codes),
            extra={"cpt_codes": coder_result.codes, "mapped_fields": list(mapped_fields.keys())},
        )

        # 3. Run Extractor with Coder Hints
        extraction_context = {
            "verified_cpt_codes": coder_result.codes,
            "coder_difficulty": coder_result.difficulty.value,
            "hybrid_source": coder_result.source,
            "ml_metadata": coder_result.metadata.get("ml_result"),
            "schema_version": "v3",
        }

        engine_warnings: list[str] = []
        run_with_warnings = getattr(self.registry_engine, "run_with_warnings", None)
        if callable(run_with_warnings):
            record, engine_warnings = run_with_warnings(
                masked_note_text,
                context=extraction_context,
            )
        else:
            record = self.registry_engine.run(masked_note_text, context=extraction_context)
            if isinstance(record, tuple):
                record = record[0]  # Unpack if evidence included

        # 4. Merge CPT-driven fields into the extraction result
        merged_record = self._merge_cpt_fields_into_record(record, mapped_fields)

        # 5. Validate and finalize (includes ML hybrid audit)
        final_result = self._validate_and_finalize(
            RegistryExtractionResult(
                record=merged_record,
                cpt_codes=coder_result.codes,
                coder_difficulty=coder_result.difficulty.value,
                coder_source=coder_result.source,
                mapped_fields=mapped_fields,
                warnings=list(engine_warnings),
            ),
            coder_result=coder_result,
            note_text=masked_note_text,
        )

        return final_result

    def extract_fields_extraction_first(self, note_text: str) -> RegistryExtractionResult:
        """Extract registry fields using extraction-first flow.

        This bypasses the hybrid-first pipeline and always runs:
        1) Registry extraction
        2) Deterministic Registry→CPT derivation
        3) RAW-ML audit (if enabled)
        """
        return self._extract_fields_extraction_first(note_text)

    # -------------------------------------------------------------------------
    # Extraction-First Registry → Deterministic CPT → RAW-ML Audit
    # -------------------------------------------------------------------------

    def extract_record(
        self,
        note_text: str,
        *,
        note_id: str | None = None,
    ) -> tuple[RegistryRecord, list[str], dict[str, Any]]:
        """Extract a RegistryRecord from note text without CPT hints.

        This is the extraction-first entrypoint for registry evidence. It must
        not seed extraction with CPT codes, ML-predicted CPT codes, or any
        SmartHybridOrchestrator output.
        """
        warnings: list[str] = []
        meta: dict[str, Any] = {"note_id": note_id}

        extraction_engine = os.getenv("REGISTRY_EXTRACTION_ENGINE", "engine").strip().lower()
        meta["extraction_engine"] = extraction_engine

        raw_note_text = note_text
        masked_note_text, mask_meta = mask_extraction_noise(raw_note_text)
        meta["masked_note_text"] = masked_note_text
        meta["masking_meta"] = mask_meta

        text_for_extraction = masked_note_text
        if extraction_engine == "engine":
            pass
        elif extraction_engine == "agents_focus_then_engine":
            # Phase 2: focusing helper is optional; guardrail is that RAW-ML always
            # runs on the raw note text.
            try:
                focused_text, focus_meta = focus_note_for_extraction(masked_note_text)
                meta["focus_meta"] = focus_meta
                text_for_extraction = focused_text or masked_note_text
            except Exception as exc:
                warnings.append(f"focus_note_for_extraction failed ({exc}); using masked note")
                meta["focus_meta"] = {"status": "failed", "error": str(exc)}
                text_for_extraction = masked_note_text
        elif extraction_engine == "agents_structurer":
            try:
                from modules.registry.extraction.structurer import structure_note_to_registry_record

                record, struct_meta = structure_note_to_registry_record(
                    masked_note_text,
                    note_id=note_id,
                )
                meta["structurer_meta"] = struct_meta
                meta["extraction_text"] = masked_note_text

                record, granular_warnings = _apply_granular_up_propagation(record)
                warnings.extend(granular_warnings)

                from modules.registry.evidence.verifier import verify_evidence_integrity
                from modules.registry.postprocess import (
                    populate_ebus_node_events_fallback,
                    sanitize_ebus_events,
                )

                record, verifier_warnings = verify_evidence_integrity(record, masked_note_text)
                warnings.extend(verifier_warnings)
                warnings.extend(sanitize_ebus_events(record, masked_note_text))
                warnings.extend(populate_ebus_node_events_fallback(record, masked_note_text))

                return record, warnings, meta
            except NotImplementedError as exc:
                warnings.append(str(exc))
                meta["structurer_meta"] = {"status": "not_implemented"}
            except Exception as exc:
                warnings.append(f"Structurer failed ({exc}); falling back to engine")
                meta["structurer_meta"] = {"status": "failed", "error": str(exc)}
        elif extraction_engine == "parallel_ner":
            # Parallel NER pathway: Run NER → Registry mapping → Rules + ML safety net
            try:
                predictor = self._get_registry_ml_predictor()
                parallel_result = self.parallel_orchestrator.process(
                    masked_note_text,
                    ml_predictor=predictor,
                )

                # Get record from Path A (NER → Registry → Rules)
                path_a_details = parallel_result.path_a_result.details
                record = path_a_details.get("record")

                if record is None:
                    # Fallback: create empty record if NER pathway failed
                    record = RegistryRecord()
                    warnings.append("Parallel NER path_a produced no record; using empty record")

                ner_evidence = self.parallel_orchestrator._build_ner_evidence(
                    path_a_details.get("ner_entities")
                )
                if ner_evidence:
                    record_evidence = getattr(record, "evidence", None)
                    if not isinstance(record_evidence, dict):
                        record_evidence = {}
                    for key, spans in ner_evidence.items():
                        record_evidence.setdefault(key, []).extend(spans)
                    record.evidence = record_evidence

                # Deterministic fallback: fill common missed procedure flags so
                # extraction-first does not silently drop revenue when NER misses.
                try:
                    import re

                    from modules.common.spans import Span
                    from modules.registry.deterministic_extractors import (
                        AIRWAY_DILATION_PATTERNS,
                        AIRWAY_STENT_DEVICE_PATTERNS,
                        BAL_PATTERNS,
                        BRUSHINGS_PATTERNS,
                        CHEST_TUBE_PATTERNS,
                        CHEST_ULTRASOUND_PATTERNS,
                        CRYOPROBE_PATTERN,
                        CRYOTHERAPY_PATTERNS,
                        CRYOBIOPSY_PATTERN,
                        IPC_PATTERNS,
                        NAVIGATIONAL_BRONCHOSCOPY_PATTERNS,
                        PERIPHERAL_ABLATION_PATTERNS,
                        RIGID_BRONCHOSCOPY_PATTERNS,
                        ENDOBRONCHIAL_BIOPSY_PATTERNS,
                        RADIAL_EBUS_PATTERNS,
                        TBNA_CONVENTIONAL_PATTERNS,
                        THERMAL_ABLATION_PATTERNS,
                        TRANSBRONCHIAL_CRYOBIOPSY_PATTERNS,
                        run_deterministic_extractors,
                    )

                    seed = run_deterministic_extractors(masked_note_text)
                    seed_procs = seed.get("procedures_performed") if isinstance(seed, dict) else None
                    seed_pleural = seed.get("pleural_procedures") if isinstance(seed, dict) else None
                    seed_established_trach = (
                        seed.get("established_tracheostomy_route") is True if isinstance(seed, dict) else False
                    )
                    fiducial_candidate = "fiducial" in (masked_note_text or "").lower()

                    if (
                        (isinstance(seed_procs, dict) and seed_procs)
                        or (isinstance(seed_pleural, dict) and seed_pleural)
                        or seed_established_trach
                        or fiducial_candidate
                    ):
                        record_data = record.model_dump()
                        record_procs = record_data.get("procedures_performed") or {}
                        if not isinstance(record_procs, dict):
                            record_procs = {}

                        record_pleural = record_data.get("pleural_procedures") or {}
                        if not isinstance(record_pleural, dict):
                            record_pleural = {}

                        evidence = record_data.get("evidence") or {}
                        if not isinstance(evidence, dict):
                            evidence = {}

                        uplifted: list[str] = []
                        proc_modified = False
                        pleural_modified = False
                        other_modified = False

                        def _add_first_span(field: str, patterns: list[str]) -> None:
                            for pat in patterns:
                                match = re.search(pat, masked_note_text or "", re.IGNORECASE)
                                if match:
                                    evidence.setdefault(field, []).append(
                                        Span(
                                            text=match.group(0).strip(),
                                            start=match.start(),
                                            end=match.end(),
                                        )
                                    )
                                    return

                        def _add_first_span_skip_cpt_headers(field: str, patterns: list[str]) -> None:
                            cpt_line = re.compile(r"^\s*\d{5}\b")
                            offset = 0
                            for raw_line in (masked_note_text or "").splitlines(keepends=True):
                                line = raw_line.rstrip("\r\n")
                                if cpt_line.match(line):
                                    offset += len(raw_line)
                                    continue
                                for pat in patterns:
                                    match = re.search(pat, line, re.IGNORECASE)
                                    if match:
                                        evidence.setdefault(field, []).append(
                                            Span(
                                                text=match.group(0).strip(),
                                                start=offset + match.start(),
                                                end=offset + match.end(),
                                            )
                                        )
                                        return
                                offset += len(raw_line)

                        if isinstance(seed_procs, dict):
                            for proc_name, proc_data in seed_procs.items():
                                if not isinstance(proc_data, dict):
                                    continue
                                if proc_data.get("performed") is not True:
                                    continue

                                existing = record_procs.get(proc_name) or {}
                                if not isinstance(existing, dict):
                                    existing = {}
                                already_performed = existing.get("performed") is True
                                proc_changed = False

                                if not already_performed:
                                    existing["performed"] = True
                                    uplifted.append(proc_name)
                                    proc_changed = True

                                for key, value in proc_data.items():
                                    if key == "performed":
                                        continue
                                    if proc_name == "airway_stent":
                                        if key == "airway_stent_removal" and value is True and existing.get(key) is not True:
                                            existing[key] = True
                                            proc_changed = True
                                            continue
                                        if key == "action" and isinstance(value, str) and value.strip():
                                            existing_action = existing.get("action")
                                            if existing_action in (None, "", "Placement") and existing_action != value:
                                                existing[key] = value
                                                proc_changed = True
                                                continue

                                    if existing.get(key) in (None, "", [], {}):
                                        existing[key] = value
                                        proc_changed = True

                                if proc_changed:
                                    record_procs[proc_name] = existing
                                    proc_modified = True

                                if not already_performed:
                                    field_key = f"procedures_performed.{proc_name}.performed"
                                    if proc_name == "bal":
                                        _add_first_span(field_key, list(BAL_PATTERNS))
                                    elif proc_name == "endobronchial_biopsy":
                                        _add_first_span(
                                            field_key,
                                            list(ENDOBRONCHIAL_BIOPSY_PATTERNS),
                                        )
                                    elif proc_name == "radial_ebus":
                                        _add_first_span(field_key, list(RADIAL_EBUS_PATTERNS))
                                    elif proc_name == "navigational_bronchoscopy":
                                        _add_first_span(
                                            field_key,
                                            list(NAVIGATIONAL_BRONCHOSCOPY_PATTERNS),
                                        )
                                    elif proc_name == "tbna_conventional":
                                        _add_first_span(
                                            field_key,
                                            list(TBNA_CONVENTIONAL_PATTERNS),
                                        )
                                    elif proc_name == "brushings":
                                        _add_first_span(field_key, list(BRUSHINGS_PATTERNS))
                                    elif proc_name == "rigid_bronchoscopy":
                                        _add_first_span(
                                            field_key,
                                            list(RIGID_BRONCHOSCOPY_PATTERNS),
                                        )
                                    elif proc_name == "transbronchial_cryobiopsy":
                                        _add_first_span(
                                            field_key,
                                            list(TRANSBRONCHIAL_CRYOBIOPSY_PATTERNS),
                                        )
                                    elif proc_name == "airway_dilation":
                                        _add_first_span(field_key, list(AIRWAY_DILATION_PATTERNS))
                                    elif proc_name == "airway_stent":
                                        _add_first_span(field_key, list(AIRWAY_STENT_DEVICE_PATTERNS))
                                    elif proc_name == "foreign_body_removal":
                                        _add_first_span(
                                            field_key,
                                            [
                                                r"\bforeign\s+body\b",
                                                r"\bstent\b[^.\n]{0,80}\b(?:remov|retriev|extract|explant|pull|grasp)\w*",
                                                r"\b(?:remov|retriev|extract|explant|pull|grasp)\w*\b[^.\n]{0,80}\bstent\b",
                                            ],
                                        )
                                    elif proc_name == "peripheral_ablation":
                                        _add_first_span(
                                            field_key,
                                            list(PERIPHERAL_ABLATION_PATTERNS),
                                        )
                                    elif proc_name == "thermal_ablation":
                                        _add_first_span_skip_cpt_headers(
                                            field_key,
                                            list(THERMAL_ABLATION_PATTERNS),
                                        )
                                    elif proc_name == "cryotherapy":
                                        cryo_patterns = list(CRYOTHERAPY_PATTERNS)
                                        if not re.search(
                                            CRYOBIOPSY_PATTERN,
                                            masked_note_text or "",
                                            re.IGNORECASE,
                                        ):
                                            cryo_patterns.append(CRYOPROBE_PATTERN)
                                        _add_first_span_skip_cpt_headers(field_key, cryo_patterns)
                                    elif proc_name == "chest_ultrasound":
                                        _add_first_span(
                                            field_key,
                                            list(CHEST_ULTRASOUND_PATTERNS),
                                        )

                        if isinstance(seed_pleural, dict):
                            for proc_name, proc_data in seed_pleural.items():
                                if not isinstance(proc_data, dict):
                                    continue
                                if proc_data.get("performed") is not True:
                                    continue

                                existing = record_pleural.get(proc_name) or {}
                                if not isinstance(existing, dict):
                                    existing = {}
                                already_performed = existing.get("performed") is True
                                proc_changed = False

                                if not already_performed:
                                    existing["performed"] = True
                                    uplifted.append(f"pleural_procedures.{proc_name}")
                                    proc_changed = True

                                for key, value in proc_data.items():
                                    if key == "performed":
                                        continue
                                    if existing.get(key) in (None, "", [], {}):
                                        existing[key] = value
                                        proc_changed = True

                                if proc_changed:
                                    record_pleural[proc_name] = existing
                                    pleural_modified = True

                                if not already_performed:
                                    field_key = f"pleural_procedures.{proc_name}.performed"
                                    if proc_name == "chest_tube":
                                        _add_first_span(field_key, list(CHEST_TUBE_PATTERNS))
                                    elif proc_name == "ipc":
                                        _add_first_span(field_key, list(IPC_PATTERNS))

                        if seed_established_trach and not record_data.get("established_tracheostomy_route"):
                            record_data["established_tracheostomy_route"] = True
                            other_modified = True

                        if fiducial_candidate:
                            from modules.registry.processing.navigation_fiducials import (
                                apply_navigation_fiducials,
                            )

                            if apply_navigation_fiducials(record_data, masked_note_text):
                                other_modified = True

                        if uplifted:
                            warnings.append(
                                "DETERMINISTIC_UPLIFT: added performed=true for "
                                + ", ".join(sorted(set(uplifted)))
                            )

                        if proc_modified:
                            record_data["procedures_performed"] = record_procs
                        if pleural_modified:
                            record_data["pleural_procedures"] = record_pleural
                        if proc_modified or pleural_modified:
                            record_data["evidence"] = evidence

                        if proc_modified or pleural_modified or other_modified:
                            record = RegistryRecord(**record_data)
                except Exception as exc:
                    warnings.append(f"Deterministic uplift failed ({exc})")

                # Store parallel pathway metadata
                meta["parallel_pathway"] = {
                    "path_a": {
                        "source": parallel_result.path_a_result.source,
                        "codes": parallel_result.path_a_result.codes,
                        "processing_time_ms": parallel_result.path_a_result.processing_time_ms,
                        "ner_entity_count": path_a_details.get("ner_entity_count", 0),
                        "stations_sampled_count": path_a_details.get("stations_sampled_count", 0),
                    },
                    "path_b": {
                        "source": parallel_result.path_b_result.source,
                        "codes": parallel_result.path_b_result.codes,
                        "confidences": parallel_result.path_b_result.confidences,
                        "processing_time_ms": parallel_result.path_b_result.processing_time_ms,
                    },
                    "final_codes": parallel_result.final_codes,
                    "final_confidences": parallel_result.final_confidences,
                    "needs_review": parallel_result.needs_review,
                    "review_reasons": parallel_result.review_reasons,
                    "total_time_ms": parallel_result.total_time_ms,
                }
                meta["extraction_text"] = masked_note_text

                # Apply standard postprocessing
                record, granular_warnings = _apply_granular_up_propagation(record)
                warnings.extend(granular_warnings)

                from modules.registry.evidence.verifier import verify_evidence_integrity
                from modules.registry.postprocess import (
                    populate_ebus_node_events_fallback,
                    sanitize_ebus_events,
                )

                record, verifier_warnings = verify_evidence_integrity(record, masked_note_text)
                warnings.extend(verifier_warnings)
                warnings.extend(sanitize_ebus_events(record, masked_note_text))
                warnings.extend(populate_ebus_node_events_fallback(record, masked_note_text))

                # Add review warnings if parallel pathway flagged discrepancies
                if parallel_result.needs_review:
                    warnings.extend(parallel_result.review_reasons)

                return record, warnings, meta
            except Exception as exc:
                warnings.append(f"Parallel NER pathway failed ({exc}); falling back to engine")
                meta["parallel_pathway"] = {"status": "failed", "error": str(exc)}
        else:
            warnings.append(f"Unknown REGISTRY_EXTRACTION_ENGINE='{extraction_engine}', using engine")

        meta["extraction_text"] = text_for_extraction
        context: dict[str, Any] = {"schema_version": "v3"}
        if note_id:
            context["note_id"] = note_id
        engine_warnings: list[str] = []
        run_with_warnings = getattr(self.registry_engine, "run_with_warnings", None)
        if callable(run_with_warnings):
            record, engine_warnings = run_with_warnings(text_for_extraction, context=context)
        else:
            record = self.registry_engine.run(text_for_extraction, context=context)
            if isinstance(record, tuple):
                record = record[0]  # Unpack if evidence included
        warnings.extend(engine_warnings)

        record, granular_warnings = _apply_granular_up_propagation(record)
        warnings.extend(granular_warnings)

        from modules.registry.evidence.verifier import verify_evidence_integrity
        from modules.registry.postprocess import (
            populate_ebus_node_events_fallback,
            sanitize_ebus_events,
        )

        record, verifier_warnings = verify_evidence_integrity(record, masked_note_text)
        warnings.extend(verifier_warnings)
        warnings.extend(sanitize_ebus_events(record, masked_note_text))
        warnings.extend(populate_ebus_node_events_fallback(record, masked_note_text))

        return record, warnings, meta

    def _extract_fields_extraction_first(self, raw_note_text: str) -> RegistryExtractionResult:
        """Extraction-first registry pipeline.

        Order (must not call orchestrator / CPT seeding):
        1) extract_record(raw_note_text)
        2) deterministic Registry→CPT derivation (Phase 3)
        3) RAW-ML audit via MLCoderPredictor.classify_case(raw_note_text)
        """
        from modules.registry.audit.raw_ml_auditor import RawMLAuditor
        from modules.coder.domain_rules.registry_to_cpt.engine import apply as derive_registry_to_cpt
        from modules.registry.audit.compare import build_audit_compare_report
        from modules.registry.self_correction.apply import SelfCorrectionApplyError, apply_patch_to_record
        from modules.registry.self_correction.judge import RegistryCorrectionJudge
        from modules.registry.self_correction.keyword_guard import (
            apply_required_overrides,
            keyword_guard_check,
            keyword_guard_passes,
            scan_for_omissions,
        )
        from modules.registry.self_correction.types import SelfCorrectionMetadata, SelfCorrectionTrigger
        from modules.registry.self_correction.validation import (
            ALLOWED_PATHS,
            ALLOWED_PATH_PREFIXES,
            validate_proposal,
        )

        # Guardrail: auditing must always use the original raw note text. Do not
        # overwrite this variable with focused/summarized text.
        raw_text_for_audit = raw_note_text

        masked_note_text, _mask_meta = mask_extraction_noise(raw_note_text)

        def _env_flag(name: str, default: str = "0") -> bool:
            return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y"}

        def _env_int(name: str, default: int) -> int:
            raw = os.getenv(name)
            if raw is None:
                return default
            raw = raw.strip()
            if not raw:
                return default
            try:
                return int(raw)
            except ValueError:
                return default

        def _apply_navigation_target_heuristics(
            note_text: str, record_in: RegistryRecord
        ) -> tuple[RegistryRecord, list[str]]:
            if record_in is None:
                return RegistryRecord(), []

            text = note_text or ""
            nav_hint = re.search(
                r"(?i)\b(navigational bronchoscopy|robotic bronchoscopy|electromagnetic navigation|\benb\b|\bion\b|monarch|galaxy|planning station)\b",
                text,
            )
            if not nav_hint:
                return record_in, []

            target_lines = [line for line in text.splitlines() if re.search(r"(?i)target lesion", line)]
            if not target_lines:
                return record_in, []

            record_data = record_in.model_dump()
            granular = record_data.get("granular_data")
            if granular is None or not isinstance(granular, dict):
                granular = {}

            targets_raw = granular.get("navigation_targets")
            if isinstance(targets_raw, list):
                targets = [dict(t) for t in targets_raw if isinstance(t, dict)]
            else:
                targets = []

            existing_count = len(targets)
            needed_count = len(target_lines)
            if existing_count >= needed_count:
                return record_in, []

            for idx in range(existing_count, needed_count):
                line = target_lines[idx].strip()
                targets.append(
                    {
                        "target_number": idx + 1,
                        "target_location_text": line or f"Target lesion {idx + 1}",
                    }
                )

            granular["navigation_targets"] = targets
            record_data["granular_data"] = granular
            record_out = RegistryRecord(**record_data)

            added = needed_count - existing_count
            return record_out, [f"NAV_TARGET_HEURISTIC: added {added} navigation target(s) from text"]

        def _coverage_failures(note_text: str, record_in: RegistryRecord) -> list[str]:
            failures: list[str] = []
            text = note_text or ""

            ebus_hit = re.search(r"(?i)EBUS[- ]Findings|EBUS Lymph Nodes Sampled|\blinear\s+ebus\b", text)
            ebus_performed = False
            try:
                ebus_obj = (
                    record_in.procedures_performed.linear_ebus
                    if record_in.procedures_performed
                    else None
                )
                ebus_performed = bool(getattr(ebus_obj, "performed", False))
            except Exception:
                ebus_performed = False
            if ebus_hit and not ebus_performed:
                failures.append("linear_ebus missing")

            eus_hit = re.search(
                r"(?i)\bEUS-?B\b|\bleft adrenal\b|\btransgastric\b|\btransesophageal\b",
                text,
            )
            procedures = record_in.procedures_performed if record_in.procedures_performed else None
            if eus_hit and procedures is not None and hasattr(procedures, "eus_b"):
                eus_b_performed = False
                try:
                    eus_b_obj = getattr(procedures, "eus_b", None)
                    eus_b_performed = bool(getattr(eus_b_obj, "performed", False)) if eus_b_obj else False
                except Exception:
                    eus_b_performed = False
                if not eus_b_performed:
                    failures.append("eus_b missing")

            nav_hit = re.search(
                r"(?i)\b(navigational bronchoscopy|robotic bronchoscopy|electromagnetic navigation|\benb\b|\bion\b|monarch|galaxy)\b",
                text,
            )
            if nav_hit:
                target_mentions = len(re.findall(r"(?i)target lesion", text))
                try:
                    nav_targets = (
                        record_in.granular_data.navigation_targets
                        if record_in.granular_data is not None
                        else None
                    )
                    nav_count = len(nav_targets or [])
                except Exception:
                    nav_count = 0
                if target_mentions and nav_count < target_mentions:
                    failures.append(f"navigation_targets {nav_count} < {target_mentions}")

            return failures

        def _run_structurer_fallback(note_text: str) -> tuple[RegistryRecord | None, list[str]]:
            warnings: list[str] = []
            context: dict[str, Any] = {"schema_version": "v3"}
            try:
                run_with_warnings = getattr(self.registry_engine, "run_with_warnings", None)
                if callable(run_with_warnings):
                    record_out, engine_warnings = run_with_warnings(note_text, context=context)
                    warnings.extend(engine_warnings or [])
                else:
                    record_out = self.registry_engine.run(note_text, context=context)
                    if isinstance(record_out, tuple):
                        record_out = record_out[0]

                record_out, granular_warnings = _apply_granular_up_propagation(record_out)
                warnings.extend(granular_warnings)

                from modules.registry.evidence.verifier import verify_evidence_integrity
                from modules.registry.postprocess import (
                    populate_ebus_node_events_fallback,
                    sanitize_ebus_events,
                )

                record_out, verifier_warnings = verify_evidence_integrity(record_out, note_text)
                warnings.extend(verifier_warnings)
                warnings.extend(sanitize_ebus_events(record_out, note_text))
                warnings.extend(populate_ebus_node_events_fallback(record_out, note_text))
                return record_out, warnings
            except Exception as exc:
                warnings.append(f"STRUCTURER_FALLBACK_FAILED: {exc}")
                return None, warnings

        record, extraction_warnings, meta = self.extract_record(raw_note_text)
        extraction_text = meta.get("extraction_text") if isinstance(meta.get("extraction_text"), str) else None
        if isinstance(meta.get("masked_note_text"), str):
            masked_note_text = meta["masked_note_text"]

        # Omission detection: flag "silent failures" where high-value terms are present
        # in the raw text but the corresponding registry fields are missing/false.
        omission_warnings = scan_for_omissions(masked_note_text, record)
        if omission_warnings:
            extraction_warnings.extend(omission_warnings)

        record, override_warnings = apply_required_overrides(masked_note_text, record)
        if override_warnings:
            extraction_warnings.extend(override_warnings)

        record, nav_target_warnings = _apply_navigation_target_heuristics(masked_note_text, record)
        if nav_target_warnings:
            extraction_warnings.extend(nav_target_warnings)

        from modules.registry.postprocess import (
            populate_ebus_node_events_fallback,
            sanitize_ebus_events,
        )

        ebus_fallback_warnings = populate_ebus_node_events_fallback(record, masked_note_text)
        if ebus_fallback_warnings:
            extraction_warnings.extend(ebus_fallback_warnings)
        ebus_sanitize_warnings = sanitize_ebus_events(record, masked_note_text)
        if ebus_sanitize_warnings:
            extraction_warnings.extend(ebus_sanitize_warnings)

        guardrail_outcome = self.clinical_guardrails.apply_record_guardrails(
            masked_note_text, record
        )
        record = guardrail_outcome.record or record
        if guardrail_outcome.warnings:
            extraction_warnings.extend(guardrail_outcome.warnings)

        derivation = derive_registry_to_cpt(record)
        derived_codes = [c.code for c in derivation.codes]
        base_warnings = list(extraction_warnings)
        self_correct_warnings: list[str] = []
        coverage_warnings: list[str] = []
        self_correction_meta: list[SelfCorrectionMetadata] = []

        auditor_source = os.getenv("REGISTRY_AUDITOR_SOURCE", "raw_ml").strip().lower()
        audit_warnings: list[str] = []
        audit_report: AuditCompareReport | None = None
        coder_difficulty = "unknown"
        needs_manual_review = bool(omission_warnings) or guardrail_outcome.needs_review

        code_guardrail = self.clinical_guardrails.apply_code_guardrails(
            masked_note_text, derived_codes
        )
        if code_guardrail.warnings:
            base_warnings.extend(code_guardrail.warnings)
        if code_guardrail.needs_review:
            needs_manual_review = True

        baseline_needs_manual_review = needs_manual_review

        if auditor_source == "raw_ml":
            from modules.registry.audit.raw_ml_auditor import RawMLAuditConfig

            auditor = RawMLAuditor()
            cfg = RawMLAuditConfig.from_env()
            ml_case = auditor.classify(raw_text_for_audit)
            coder_difficulty = ml_case.difficulty.value

            audit_preds = auditor.audit_predictions(ml_case, cfg)

            audit_report = build_audit_compare_report(
                derived_codes=derived_codes,
                cfg=cfg,
                ml_case=ml_case,
                audit_preds=audit_preds,
            )

            header_codes = _scan_header_for_codes(raw_note_text)

            def _apply_balanced_triggers(
                report: AuditCompareReport, current_codes: list[str]
            ) -> None:
                nonlocal needs_manual_review

                derived_code_set = {str(c) for c in (current_codes or [])}
                missing_header_codes = sorted(header_codes - derived_code_set)
                if missing_header_codes:
                    warning = (
                        "HEADER_EXPLICIT: header lists "
                        f"{missing_header_codes} but deterministic derivation missed them"
                    )
                    if warning not in audit_warnings:
                        logger.info(
                            "HEADER_EXPLICIT mismatch: header has %s but derivation missed them.",
                            missing_header_codes,
                        )
                        audit_warnings.append(warning)

                    existing = {p.cpt for p in (report.high_conf_omissions or [])}
                    for missing in missing_header_codes:
                        if missing in existing:
                            continue
                        report.high_conf_omissions.append(
                            AuditPrediction(cpt=missing, prob=1.0, bucket="HEADER_EXPLICIT")
                        )
                        existing.add(missing)

                try:
                    ebus_obj = (
                        record.procedures_performed.linear_ebus
                        if record.procedures_performed
                        else None
                    )
                    ebus_performed = bool(getattr(ebus_obj, "performed", False))
                    stations = getattr(ebus_obj, "stations_sampled", None)
                    stations_empty = not stations
                except Exception:
                    ebus_performed = False
                    stations_empty = False

                if ebus_performed and stations_empty:
                    warning = (
                        "STRUCTURAL_FAILURE: linear_ebus performed but stations_sampled is empty "
                        "(station extraction likely failed)"
                    )
                    if warning not in audit_warnings:
                        audit_warnings.append(warning)
                    needs_manual_review = True

                    if "31653" in header_codes and "31653" not in derived_code_set:
                        existing = {p.cpt for p in (report.high_conf_omissions or [])}
                        if "31653" not in existing:
                            report.high_conf_omissions.append(
                                AuditPrediction(cpt="31653", prob=1.0, bucket="STRUCTURAL_FAILURE")
                            )

            def _audit_requires_review(report: AuditCompareReport, evidence: str) -> bool:
                if not report.high_conf_omissions:
                    return False
                for pred in report.high_conf_omissions:
                    if pred.bucket in {"HEADER_EXPLICIT", "STRUCTURAL_FAILURE"}:
                        return True
                    passes, reason = keyword_guard_check(cpt=pred.cpt, evidence_text=evidence)
                    if passes or reason == "no keywords configured":
                        return True
                return False

            needs_manual_review = baseline_needs_manual_review
            _apply_balanced_triggers(audit_report, derived_codes)
            needs_manual_review = needs_manual_review or _audit_requires_review(
                audit_report, masked_note_text
            )

            self_correct_enabled = _env_flag("REGISTRY_SELF_CORRECT_ENABLED", "0")
            if self_correct_enabled and audit_report.high_conf_omissions:
                max_attempts = max(0, _env_int("REGISTRY_SELF_CORRECT_MAX_ATTEMPTS", 1))
                bucket_by_cpt: dict[str, str | None] = {}
                for pred in (audit_report.ml_audit_codes or []):
                    bucket_by_cpt[pred.cpt] = pred.bucket
                for pred in (audit_report.high_conf_omissions or []):
                    if pred.bucket and pred.cpt not in bucket_by_cpt:
                        bucket_by_cpt[pred.cpt] = pred.bucket
                trigger_preds = sorted(
                    audit_report.high_conf_omissions,
                    key=lambda p: float(p.prob),
                    reverse=True,
                )

                judge = RegistryCorrectionJudge()

                def _allowlist_snapshot() -> list[str]:
                    raw = os.getenv("REGISTRY_SELF_CORRECT_ALLOWLIST", "").strip()
                    if raw:
                        return sorted({p.strip() for p in raw.split(",") if p.strip()})
                    defaults = set(ALLOWED_PATHS)
                    defaults.update(f"{prefix}/*" for prefix in ALLOWED_PATH_PREFIXES)
                    return sorted(defaults)

                corrections_applied = 0
                evidence_text = (
                    extraction_text
                    if extraction_text is not None and extraction_text.strip()
                    else masked_note_text
                )
                for pred in trigger_preds:
                    if corrections_applied >= max_attempts:
                        break

                    bucket = bucket_by_cpt.get(pred.cpt) or getattr(pred, "bucket", None) or "UNKNOWN"
                    bypass_guard = bucket in {"HEADER_EXPLICIT", "STRUCTURAL_FAILURE"}
                    guard_evidence = evidence_text
                    if bypass_guard:
                        header_block = _extract_procedure_header_block(masked_note_text)
                        if not header_block:
                            header_block = _extract_procedure_header_block(raw_note_text)
                        if header_block and header_block.strip():
                            guard_evidence = header_block

                    if bypass_guard:
                        passes, reason = True, "bucket bypass"
                    else:
                        passes, reason = keyword_guard_check(cpt=pred.cpt, evidence_text=guard_evidence)
                    if not passes:
                        self_correct_warnings.append(
                            f"SELF_CORRECT_SKIPPED: {pred.cpt}: keyword guard failed ({reason})"
                        )
                        continue

                    derived_codes_before = list(derived_codes)
                    trigger = SelfCorrectionTrigger(
                        target_cpt=pred.cpt,
                        ml_prob=float(pred.prob),
                        ml_bucket=bucket,
                        reason=bucket if bucket != "UNKNOWN" else "RAW_ML_HIGH_CONF_OMISSION",
                    )

                    if bucket == "HEADER_EXPLICIT":
                        discrepancy = (
                            f"Procedure header explicitly lists CPT {pred.cpt}, but deterministic "
                            "derivation missed it. Patch the registry fields (not billing codes) "
                            "so deterministic derivation includes this CPT if supported by the note."
                        )
                    elif bucket == "STRUCTURAL_FAILURE":
                        discrepancy = (
                            f"Registry shows a structural extraction failure related to CPT {pred.cpt}. "
                            "Patch the registry fields (not billing codes) so deterministic derivation "
                            "includes this CPT if supported by the note."
                        )
                    else:
                        discrepancy = (
                            f"RAW-ML suggests missing CPT {pred.cpt} "
                            f"(prob={float(pred.prob):.2f}, bucket={bucket})."
                        )
                    proposal = judge.propose_correction(
                        note_text=raw_note_text,
                        record=record,
                        discrepancy=discrepancy,
                        focused_procedure_text=extraction_text,
                    )
                    if proposal is None:
                        self_correct_warnings.append(f"SELF_CORRECT_SKIPPED: {pred.cpt}: judge returned null")
                        continue

                    is_valid, reason = validate_proposal(
                        proposal,
                        masked_note_text,
                        extraction_text=extraction_text,
                    )
                    if not is_valid:
                        self_correct_warnings.append(f"SELF_CORRECT_SKIPPED: {pred.cpt}: {reason}")
                        continue

                    try:
                        patched_record = apply_patch_to_record(record=record, patch=proposal.json_patch)
                    except SelfCorrectionApplyError as exc:
                        self_correct_warnings.append(f"SELF_CORRECT_SKIPPED: {pred.cpt}: apply failed ({exc})")
                        continue

                    if patched_record.model_dump() == record.model_dump():
                        self_correct_warnings.append(
                            f"SELF_CORRECT_SKIPPED: {pred.cpt}: patch produced no change"
                        )
                        continue

                    candidate_record, candidate_granular_warnings = _apply_granular_up_propagation(
                        patched_record
                    )

                    candidate_derivation = derive_registry_to_cpt(candidate_record)
                    candidate_codes = [c.code for c in candidate_derivation.codes]
                    if trigger.target_cpt not in candidate_codes:
                        self_correct_warnings.append(
                            f"SELF_CORRECT_SKIPPED: {pred.cpt}: patch did not derive target CPT"
                        )
                        continue

                    record = candidate_record
                    derivation = candidate_derivation
                    derived_codes = candidate_codes
                    corrections_applied += 1
                    self_correct_warnings.extend(candidate_granular_warnings)

                    self_correct_warnings.append(f"AUTO_CORRECTED: {pred.cpt}")
                    applied_paths = [
                        str(op.get("path"))
                        for op in proposal.json_patch
                        if isinstance(op, dict) and op.get("path") is not None
                    ]
                    allowlist_snapshot = _allowlist_snapshot()
                    config_snapshot = {
                        "max_attempts": max_attempts,
                        "allowlist": allowlist_snapshot,
                        "audit_config": audit_report.config.to_dict(),
                        "judge_rationale": proposal.rationale,
                    }
                    self_correction_meta.append(
                        SelfCorrectionMetadata(
                            trigger=trigger,
                            applied_paths=applied_paths,
                            evidence_quotes=[proposal.evidence_quote],
                            config_snapshot=config_snapshot,
                        )
                    )
                    log_path = os.getenv("REGISTRY_SELF_CORRECT_LOG_PATH", "").strip()
                    if log_path:
                        _append_self_correction_log(
                            log_path,
                            {
                                "event": "AUTO_CORRECTED",
                                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                "note_sha256": _hash_note_text(raw_note_text),
                                "note_length": len((raw_note_text or "").strip()),
                                "trigger": {
                                    "target_cpt": pred.cpt,
                                    "ml_prob": float(pred.prob),
                                    "bucket": bucket,
                                    "reason": trigger.reason,
                                },
                                "derived_codes_before": derived_codes_before,
                                "derived_codes_after": list(candidate_codes),
                                "json_patch": proposal.json_patch,
                                "evidence_quote": proposal.evidence_quote,
                                "judge_rationale": proposal.rationale,
                                "applied_paths": applied_paths,
                                "config_snapshot": config_snapshot,
                            },
                        )

                    audit_report = build_audit_compare_report(
                        derived_codes=derived_codes,
                        cfg=cfg,
                        ml_case=ml_case,
                        audit_preds=audit_preds,
                    )
                    needs_manual_review = baseline_needs_manual_review
                    _apply_balanced_triggers(audit_report, derived_codes)
                    needs_manual_review = needs_manual_review or _audit_requires_review(
                        audit_report, masked_note_text
                    )

            if _env_flag("REGISTRY_LLM_FALLBACK_ON_COVERAGE_FAIL", "0"):
                coverage_failures = _coverage_failures(masked_note_text, record)
                if coverage_failures:
                    coverage_warnings.append(
                        "COVERAGE_FAIL: " + "; ".join(coverage_failures)
                    )
                    needs_manual_review = True

                    fallback_record, fallback_warns = _run_structurer_fallback(masked_note_text)
                    if fallback_warns:
                        coverage_warnings.extend(fallback_warns)

                    if fallback_record is not None:
                        record = fallback_record
                        derivation = derive_registry_to_cpt(record)
                        derived_codes = [c.code for c in derivation.codes]

                        audit_report = build_audit_compare_report(
                            derived_codes=derived_codes,
                            cfg=cfg,
                            ml_case=ml_case,
                            audit_preds=audit_preds,
                        )
                        needs_manual_review = baseline_needs_manual_review
                        _apply_balanced_triggers(audit_report, derived_codes)
                        needs_manual_review = needs_manual_review or _audit_requires_review(
                            audit_report, masked_note_text
                        )

                        remaining = _coverage_failures(masked_note_text, record)
                        if remaining:
                            coverage_warnings.append(
                                "COVERAGE_FAIL_REMAINS: " + "; ".join(remaining)
                            )
        elif auditor_source == "disabled":
            from modules.registry.audit.raw_ml_auditor import RawMLAuditConfig

            cfg = RawMLAuditConfig.from_env()
            audit_report = build_audit_compare_report(
                derived_codes=derived_codes,
                cfg=cfg,
                ml_case=None,
                audit_preds=None,
                warnings=["REGISTRY_AUDITOR_SOURCE=disabled; RAW-ML audit set is empty"],
            )
            coder_difficulty = "disabled"
        else:
            raise ValueError(f"Unknown REGISTRY_AUDITOR_SOURCE='{auditor_source}'")

        if audit_report and audit_report.missing_in_derived:
            for pred in audit_report.missing_in_derived:
                bucket = pred.bucket or "AUDIT_SET"
                audit_warnings.append(
                    f"RAW_ML_AUDIT[{bucket}]: model suggests {pred.cpt} (prob={pred.prob:.2f}), "
                    "but deterministic derivation missed it"
                )

        # Populate billing CPT codes deterministically (never from the LLM).
        if derived_codes:
            record_data = record.model_dump()
            billing = record_data.get("billing")
            if not isinstance(billing, dict):
                billing = {}
            billing["cpt_codes"] = [{"code": str(code)} for code in derived_codes if str(code).strip()]
            record_data["billing"] = billing
            record = RegistryRecord(**record_data)

        derivation_warnings = list(derivation.warnings)
        warnings = list(base_warnings) + derivation_warnings + list(self_correct_warnings) + list(coverage_warnings)
        code_rationales = {c.code: c.rationale for c in derivation.codes}
        mapped_fields = (
            aggregate_registry_fields(derived_codes, version="v3") if derived_codes else {}
        )
        return RegistryExtractionResult(
            record=record,
            cpt_codes=derived_codes,
            coder_difficulty=coder_difficulty,
            coder_source="extraction_first",
            mapped_fields=mapped_fields,
            code_rationales=code_rationales,
            derivation_warnings=derivation_warnings,
            warnings=warnings,
            needs_manual_review=needs_manual_review,
            validation_errors=[],
            audit_warnings=audit_warnings,
            audit_report=audit_report,
            self_correction=self_correction_meta,
        )

    def _apply_guardrails_to_result(
        self,
        note_text: str,
        result: RegistryExtractionResult,
    ) -> RegistryExtractionResult:
        record_outcome = self.clinical_guardrails.apply_record_guardrails(
            note_text, result.record
        )
        record = record_outcome.record or result.record
        warnings = list(result.warnings) + list(record_outcome.warnings)
        needs_manual_review = result.needs_manual_review or record_outcome.needs_review

        if record_outcome.changed:
            from modules.coder.domain_rules.registry_to_cpt.engine import apply as derive_registry_to_cpt

            derivation = derive_registry_to_cpt(record)
            result.cpt_codes = [c.code for c in derivation.codes]
            result.derivation_warnings = list(derivation.warnings)
            result.code_rationales = {c.code: c.rationale for c in derivation.codes}
            result.mapped_fields = (
                aggregate_registry_fields(result.cpt_codes, version="v3")
                if result.cpt_codes
                else {}
            )

        result.record = record
        result.warnings = warnings
        result.needs_manual_review = needs_manual_review

        code_outcome = self.clinical_guardrails.apply_code_guardrails(note_text, result.cpt_codes)
        if code_outcome.warnings:
            result.warnings.extend(code_outcome.warnings)
        if code_outcome.needs_review:
            result.needs_manual_review = True

        return result

    def _merge_cpt_fields_into_record(
        self,
        record: RegistryRecord,
        mapped_fields: dict[str, Any],
    ) -> RegistryRecord:
        """Apply CPT-based mapped fields onto the registry record.

        Handles the NESTED structure from aggregate_registry_fields:
        {
            "procedures_performed": {
                "linear_ebus": {"performed": True},
                "bal": {"performed": True},
            },
            "pleural_procedures": {
                "thoracentesis": {"performed": True},
            }
        }

        This is conservative: only overwrite fields that are currently unset/False,
        unless there's a strong reason to prefer CPT over text extraction.

        Args:
            record: The extracted RegistryRecord from RegistryEngine.
            mapped_fields: Nested dict of fields from CPT mapping.

        Returns:
            Updated RegistryRecord with merged fields.
        """
        record_data = record.model_dump()

        # Handle procedures_performed section
        proc_map = mapped_fields.get("procedures_performed") or {}
        if proc_map:
            current_procs = record_data.get("procedures_performed") or {}
            for proc_name, proc_values in proc_map.items():
                current_proc = current_procs.get(proc_name) or {}

                # Merge each field in the procedure
                for field_name, cpt_value in proc_values.items():
                    current_val = current_proc.get(field_name)

                    # Only overwrite if current is falsy
                    if current_val in (None, False, "", [], {}):
                        current_proc[field_name] = cpt_value
                        logger.debug(
                            "Merged CPT field procedures_performed.%s.%s=%s (was %s)",
                            proc_name,
                            field_name,
                            cpt_value,
                            current_val,
                        )
                    elif isinstance(cpt_value, bool) and cpt_value is True:
                        # For boolean flags, CPT evidence is strong
                        if current_val is False:
                            current_proc[field_name] = True
                            logger.debug(
                                "Overrode procedures_performed.%s.%s to True based on CPT",
                                proc_name,
                                field_name,
                            )

                current_procs[proc_name] = current_proc
            record_data["procedures_performed"] = current_procs

        # Handle pleural_procedures section
        pleural_map = mapped_fields.get("pleural_procedures") or {}
        if pleural_map:
            current_pleural = record_data.get("pleural_procedures") or {}
            for proc_name, proc_values in pleural_map.items():
                current_proc = current_pleural.get(proc_name) or {}

                # Merge each field in the procedure
                for field_name, cpt_value in proc_values.items():
                    current_val = current_proc.get(field_name)

                    if current_val in (None, False, "", [], {}):
                        current_proc[field_name] = cpt_value
                        logger.debug(
                            "Merged CPT field pleural_procedures.%s.%s=%s (was %s)",
                            proc_name,
                            field_name,
                            cpt_value,
                            current_val,
                        )
                    elif isinstance(cpt_value, bool) and cpt_value is True:
                        if current_val is False:
                            current_proc[field_name] = True
                            logger.debug(
                                "Overrode pleural_procedures.%s.%s to True based on CPT",
                                proc_name,
                                field_name,
                            )

                current_pleural[proc_name] = current_proc
            record_data["pleural_procedures"] = current_pleural

        # Reconstruct the record
        return RegistryRecord(**record_data)

    def _validate_and_finalize(
        self,
        result: RegistryExtractionResult,
        *,
        coder_result: HybridCoderResult,
        note_text: str = "",
    ) -> RegistryExtractionResult:
        """Central validation and finalization logic.

        Compare CPT-driven signals (coder_result.codes) with registry fields and
        set validation flags accordingly. Also performs ML hybrid audit to detect
        procedures that ML predicted but CPT-derived flags did not capture.

        Marks cases for manual review when:
        - CPT codes don't match extracted registry fields
        - Case difficulty is LOW_CONF or GRAY_ZONE
        - ML predictor detects procedures not captured by CPT pathway

        Args:
            result: The extraction result to validate.
            coder_result: The original hybrid coder result for cross-validation.
            note_text: Original procedure note text for ML prediction.

        Returns:
            Validated and finalized RegistryExtractionResult with validation flags.
        """
        from modules.ml_coder.thresholds import CaseDifficulty

        codes = set(result.cpt_codes)
        record = result.record
        validation_errors: list[str] = list(result.validation_errors)
        warnings = list(result.warnings)
        audit_warnings: list[str] = list(result.audit_warnings)
        needs_manual_review = result.needs_manual_review

        # Get nested procedure objects (may be None)
        procedures = getattr(record, "procedures_performed", None)
        pleural = getattr(record, "pleural_procedures", None)

        # Helper to safely check if a nested procedure is present
        def _proc_is_set(obj, attr: str) -> bool:
            if obj is None:
                return False
            sub_obj = getattr(obj, attr, None)
            if sub_obj is None:
                return False
            # For nested Pydantic models, check if 'performed' field exists and is True
            if hasattr(sub_obj, "performed"):
                return bool(getattr(sub_obj, "performed", False))
            # Otherwise, just check if the object is truthy
            return bool(sub_obj)

        # -------------------------------------------------------------------------
        # 1. Derive aggregate procedure flags from granular_data if present
        # -------------------------------------------------------------------------
        granular = None
        if record.granular_data is not None:
            granular = record.granular_data.model_dump()

        existing_procedures = None
        if record.procedures_performed is not None:
            existing_procedures = record.procedures_performed.model_dump()

        if granular is not None:
            updated_procs, granular_warnings = derive_procedures_from_granular(
                granular_data=granular,
                existing_procedures=existing_procedures,
            )
            # Re-apply to record via reconstruction
            record_data = record.model_dump()
            if updated_procs:
                record_data["procedures_performed"] = updated_procs
            # Append warnings to both record + result
            record_data.setdefault("granular_validation_warnings", [])
            record_data["granular_validation_warnings"].extend(granular_warnings)
            validation_errors.extend(granular_warnings)
            # Reconstruct record with updated procedures
            record = RegistryRecord(**record_data)

        # Re-fetch procedures/pleural after potential update
        procedures = getattr(record, "procedures_performed", None)
        pleural = getattr(record, "pleural_procedures", None)

        # -------------------------------------------------------------------------
        # 2. CPT-to-Registry Field Consistency Checks
        # -------------------------------------------------------------------------

        # Linear EBUS: 31652 (1-2 stations), 31653 (3+ stations)
        if "31652" in codes or "31653" in codes:
            if not _proc_is_set(procedures, "linear_ebus"):
                validation_errors.append(
                    f"CPT {'31652' if '31652' in codes else '31653'} present "
                    "but procedures_performed.linear_ebus is not marked."
                )
            # Check station count hint
            if procedures and getattr(procedures, "linear_ebus", None):
                ebus_obj = procedures.linear_ebus
                stations = getattr(ebus_obj, "stations_sampled", None)
                if "31653" in codes and stations:
                    # 31653 implies 3+ stations
                    try:
                        station_count = len(stations) if isinstance(stations, list) else int(stations)
                        if station_count < 3:
                            warnings.append(
                                f"CPT 31653 implies 3+ EBUS stations, but only {station_count} recorded."
                            )
                    except (ValueError, TypeError):
                        pass

        # Radial EBUS: 31654
        if "31654" in codes:
            if not _proc_is_set(procedures, "radial_ebus"):
                validation_errors.append(
                    "CPT 31654 present but procedures_performed.radial_ebus is not marked."
                )

        # BAL: 31624, 31625
        if "31624" in codes or "31625" in codes:
            if not _proc_is_set(procedures, "bal"):
                validation_errors.append(
                    "CPT 31624/31625 present but procedures_performed.bal is not marked."
                )

        # Transbronchial biopsy: 31628, 31629
        if "31628" in codes or "31629" in codes:
            if not _proc_is_set(procedures, "transbronchial_biopsy"):
                validation_errors.append(
                    "CPT 31628/31629 present but procedures_performed.transbronchial_biopsy is not marked."
                )

        # Navigation: 31627
        if "31627" in codes:
            if not _proc_is_set(procedures, "navigational_bronchoscopy"):
                validation_errors.append(
                    "CPT 31627 present but procedures_performed.navigational_bronchoscopy is not marked."
                )

        # Stent: 31636, 31637
        if "31636" in codes or "31637" in codes:
            if not _proc_is_set(procedures, "airway_stent"):
                validation_errors.append(
                    "CPT 31636/31637 present but procedures_performed.airway_stent is not marked."
                )

        # Dilation: 31630, 31631
        if "31630" in codes or "31631" in codes:
            if not _proc_is_set(procedures, "airway_dilation"):
                validation_errors.append(
                    "CPT 31630/31631 present but procedures_performed.airway_dilation is not marked."
                )

        # BLVR (valve): 31647, 31648, 31649
        blvr_codes = {"31647", "31648", "31649"}
        if blvr_codes & codes:
            if not _proc_is_set(procedures, "blvr"):
                validation_errors.append(
                    "CPT 31647/31648/31649 present but procedures_performed.blvr is not marked."
                )

        # Thermoplasty: 31660, 31661
        if "31660" in codes or "31661" in codes:
            if not _proc_is_set(procedures, "bronchial_thermoplasty"):
                validation_errors.append(
                    "CPT 31660/31661 present but procedures_performed.bronchial_thermoplasty is not marked."
                )

        # Rigid bronchoscopy: 31641
        if "31641" in codes:
            if not _proc_is_set(procedures, "rigid_bronchoscopy"):
                # Only warn, as 31641 can also be thermal ablation
                warnings.append(
                    "CPT 31641 present - verify rigid_bronchoscopy or thermal ablation is marked."
                )

        # Tube thoracostomy: 32551
        if "32551" in codes:
            if not _proc_is_set(pleural, "chest_tube"):
                validation_errors.append(
                    "CPT 32551 present but pleural_procedures.chest_tube is not marked."
                )

        # Thoracentesis: 32554, 32555, 32556, 32557
        thoracentesis_codes = {"32554", "32555", "32556", "32557"}
        if thoracentesis_codes & codes:
            if not _proc_is_set(pleural, "thoracentesis") and not _proc_is_set(pleural, "chest_tube"):
                validation_errors.append(
                    "Thoracentesis CPT codes present but no pleural procedure marked."
                )

        # Medical thoracoscopy / pleuroscopy: 32601
        if "32601" in codes:
            if not _proc_is_set(pleural, "medical_thoracoscopy"):
                validation_errors.append(
                    "CPT 32601 present but pleural_procedures.medical_thoracoscopy is not marked."
                )

        # Pleurodesis: 32560, 32650
        if "32560" in codes or "32650" in codes:
            if not _proc_is_set(pleural, "pleurodesis"):
                validation_errors.append(
                    "CPT 32560/32650 present but pleural_procedures.pleurodesis is not marked."
                )

        # -------------------------------------------------------------------------
        # 3. Difficulty-based Manual Review Flags
        # -------------------------------------------------------------------------

        # Low-confidence cases: always require manual review
        if coder_result.difficulty == CaseDifficulty.LOW_CONF:
            needs_manual_review = True
            if not validation_errors:
                validation_errors.append(
                    "Hybrid coder marked this case as LOW_CONF; manual review required."
                )

        # Gray zone cases: also require manual review
        if coder_result.difficulty == CaseDifficulty.GRAY_ZONE:
            needs_manual_review = True

        # Any validation errors trigger manual review
        if validation_errors and not needs_manual_review:
            needs_manual_review = True

        # Granular validation warnings also trigger manual review
        granular_warnings_on_record = getattr(record, "granular_validation_warnings", [])
        if granular_warnings_on_record and not needs_manual_review:
            needs_manual_review = True

        # -------------------------------------------------------------------------
        # 4. ML Hybrid Audit: Compare ML predictions with CPT-derived flags
        # -------------------------------------------------------------------------
        # This is an audit overlay that cross-checks ML predictions against
        # CPT-derived flags to catch procedures the CPT pathway may have missed.

        ml_predictor = self._get_registry_ml_predictor()
        if ml_predictor is not None and note_text:
            ml_case = ml_predictor.classify_case(note_text)

            # Build CPT-derived flags dict from mapped_fields
            # The mapped_fields has structure like:
            # {"procedures_performed": {"linear_ebus": {"performed": True}, ...}}
            cpt_flags: dict[str, bool] = {}
            proc_map = result.mapped_fields.get("procedures_performed") or {}
            for proc_name, proc_values in proc_map.items():
                if isinstance(proc_values, dict) and proc_values.get("performed"):
                    cpt_flags[proc_name] = True

            pleural_map = result.mapped_fields.get("pleural_procedures") or {}
            for proc_name, proc_values in pleural_map.items():
                if isinstance(proc_values, dict) and proc_values.get("performed"):
                    cpt_flags[proc_name] = True

            # Build ML flags dict
            ml_flags: dict[str, bool] = {}
            for pred in ml_case.predictions:
                ml_flags[pred.field] = pred.is_positive

            # Compare flags and generate audit warnings
            # Scenario C: ML detected a procedure that CPT pathway did not
            for field_name, ml_positive in ml_flags.items():
                cpt_positive = cpt_flags.get(field_name, False)

                if ml_positive and not cpt_positive:
                    # ML detected a procedure the CPT pathway did not capture
                    # Find the probability for context
                    prob = next(
                        (p.probability for p in ml_case.predictions if p.field == field_name),
                        0.0,
                    )
                    audit_warnings.append(
                        f"ML detected procedure '{field_name}' with high confidence "
                        f"(prob={prob:.2f}), but no corresponding CPT-derived flag was set. "
                        f"Please review."
                    )
                    needs_manual_review = True

            # Log ML audit summary
            ml_detected_count = sum(1 for f, v in ml_flags.items() if v and not cpt_flags.get(f, False))
            if ml_detected_count > 0:
                logger.info(
                    "ml_hybrid_audit_discrepancy",
                    extra={
                        "ml_detected_not_in_cpt": ml_detected_count,
                        "audit_warnings": audit_warnings,
                    },
                )

        # -------------------------------------------------------------------------
        # Telemetry: Log validation outcome for monitoring
        # -------------------------------------------------------------------------
        logger.info(
            "registry_validation_complete",
            extra={
                "coder_difficulty": coder_result.difficulty.value,
                "coder_source": coder_result.source,
                "needs_manual_review": needs_manual_review,
                "validation_error_count": len(validation_errors),
                "warning_count": len(warnings),
                "audit_warning_count": len(audit_warnings),
                "cpt_code_count": len(codes),
            },
        )

        # -------------------------------------------------------------------------
        # 5. Return Updated Result
        # -------------------------------------------------------------------------
        return RegistryExtractionResult(
            record=record,  # Use potentially updated record from granular derivation
            cpt_codes=result.cpt_codes,
            coder_difficulty=result.coder_difficulty,
            coder_source=result.coder_source,
            mapped_fields=result.mapped_fields,
            warnings=warnings,
            needs_manual_review=needs_manual_review,
            validation_errors=validation_errors,
            audit_warnings=audit_warnings,
        )


# Factory function for DI
def get_registry_service() -> RegistryService:
    """Get a RegistryService instance with default configuration."""
    return RegistryService()
