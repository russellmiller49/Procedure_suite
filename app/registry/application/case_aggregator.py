"""Case event -> canonical snapshot aggregation service."""

from __future__ import annotations

import logging
import os
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.registry.aggregation.clinical.extract_clinical_update import extract_clinical_update_event
from app.registry.aggregation.clinical.patch_clinical_update import patch_clinical_update
from app.registry.aggregation.imaging.extract_ct import extract_ct_event
from app.registry.aggregation.imaging.extract_pet_ct import extract_pet_ct_event
from app.registry.aggregation.imaging.patch_imaging import patch_imaging_update
from app.registry.aggregation.pathology.extract_pathology import extract_pathology_event
from app.registry.aggregation.pathology.patch_pathology import patch_pathology_update
from app.registry.schema import RegistryRecord
from app.registry_store.models import RegistryAppendedDocument, RegistryCaseRecord


logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _truthy_env(name: str, *, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes")


def _aggregation_strategy() -> str:
    strategy = os.getenv("REGISTRY_CASE_AGGREGATION_STRATEGY", "pending_only")
    normalized = strategy.strip().lower()
    if normalized in {"pending_only", "reprocess_all"}:
        return normalized
    return "pending_only"


def _safe_row_text(row: RegistryAppendedDocument) -> str:
    note = str(row.note_text or "")
    if note.strip():
        return note
    metadata = row.metadata_json or {}
    structured = metadata.get("structured_data") if isinstance(metadata, dict) else None
    if isinstance(structured, dict) and structured:
        parts = [f"{k}={v}" for k, v in sorted(structured.items())]
        return "; ".join(parts)
    return ""


def _default_registry_json() -> dict[str, Any]:
    validated = RegistryRecord()
    return validated.model_dump(exclude_none=True, mode="json")


class CaseAggregator:
    """Deterministic case event aggregator with field-level lock filtering."""

    def __init__(self, *, strategy: str | None = None) -> None:
        self.strategy = (strategy or _aggregation_strategy()).strip().lower()

    def aggregate(
        self,
        *,
        db: Session,
        registry_uuid: uuid.UUID,
        user_id: str | None = None,
    ) -> RegistryCaseRecord:
        case_record = db.get(RegistryCaseRecord, registry_uuid)
        if case_record is None:
            now = _utcnow()
            case_record = RegistryCaseRecord(
                registry_uuid=registry_uuid,
                registry_json=_default_registry_json(),
                schema_version=(os.getenv("REGISTRY_SCHEMA_VERSION") or "v3").strip(),
                version=1,
                source_run_id=None,
                manual_overrides={},
                created_at=now,
                updated_at=now,
            )
            db.add(case_record)
            db.flush()

        registry_json = dict(case_record.registry_json or {})
        manual_overrides = dict(case_record.manual_overrides or {})

        events = self._load_events(db=db, registry_uuid=registry_uuid, user_id=user_id)
        if not events:
            return case_record

        changed = False
        processed_ids: list[str] = []

        for event_row in events:
            extracted = self._extract_event(event_row)
            event_row.extracted_json = extracted

            event_changed, qa_flags = self._apply_patch(
                registry_json,
                extracted=extracted,
                event_row=event_row,
                manual_overrides=manual_overrides,
            )

            try:
                validated = RegistryRecord(**registry_json)
                registry_json = validated.model_dump(exclude_none=True, mode="json")
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(
                    f"Case aggregation validation failed for event {event_row.id}"
                ) from exc

            changed = changed or event_changed
            event_row.aggregated_at = _utcnow()
            processed_ids.append(str(event_row.id))
            if qa_flags:
                logger.info(
                    "case_aggregator event_qa_flags event_id=%s event_type=%s qa_flags=%s",
                    event_row.id,
                    event_row.event_type,
                    ",".join(sorted(set(qa_flags))),
                )

        if changed:
            case_record.registry_json = registry_json
            case_record.version = int(case_record.version or 1) + 1
            case_record.updated_at = _utcnow()

        final_version = int(case_record.version or 1)
        for event_row in events:
            event_row.aggregation_version = final_version
            db.add(event_row)

        db.add(case_record)
        logger.info(
            "case_aggregator aggregate_complete registry_uuid=%s processed_events=%d changed=%s",
            registry_uuid,
            len(processed_ids),
            changed,
        )
        return case_record

    def _load_events(
        self,
        *,
        db: Session,
        registry_uuid: uuid.UUID,
        user_id: str | None,
    ) -> list[RegistryAppendedDocument]:
        stmt: Select[tuple[RegistryAppendedDocument]] = select(RegistryAppendedDocument).where(
            RegistryAppendedDocument.registry_uuid == registry_uuid
        )
        if user_id:
            stmt = stmt.where(RegistryAppendedDocument.user_id == user_id)

        if self.strategy != "reprocess_all":
            stmt = stmt.where(RegistryAppendedDocument.aggregated_at.is_(None))

        stmt = stmt.order_by(RegistryAppendedDocument.created_at.asc(), RegistryAppendedDocument.id.asc())
        return list(db.execute(stmt).scalars().all())

    def _extract_event(self, row: RegistryAppendedDocument) -> dict[str, Any]:
        event_type = str(row.event_type or "other").strip().lower()
        note_text = _safe_row_text(row)

        if event_type == "pathology":
            payload = extract_pathology_event(note_text)
            payload["event_type"] = event_type
            return payload

        if event_type == "imaging":
            source_modality = str(row.source_modality or "").strip().lower()
            if "pet" in source_modality:
                payload = extract_pet_ct_event(
                    note_text,
                    relative_day_offset=row.relative_day_offset,
                    event_subtype=row.event_subtype,
                )
            else:
                payload = extract_ct_event(
                    note_text,
                    relative_day_offset=row.relative_day_offset,
                    event_subtype=row.event_subtype,
                )
            payload["event_type"] = event_type
            payload["source_modality"] = source_modality or "ct"
            return payload

        clinical_type = {
            "clinical_update": "clinical_update",
            "treatment_update": "treatment_update",
            "complication": "complication",
            "clinical_status": "clinical_update",
            "procedure_addendum": "other",
            "procedure": "other",
            "other": "other",
        }.get(event_type)

        if clinical_type is not None:
            payload = extract_clinical_update_event(
                note_text,
                update_type=clinical_type,
                relative_day_offset=row.relative_day_offset,
            )
            payload["event_type"] = event_type
            return payload

        return {
            "event_type": event_type,
            "qa_flags": ["unsupported_event_type"],
        }

    def _apply_patch(
        self,
        registry_json: dict[str, Any],
        *,
        extracted: dict[str, Any],
        event_row: RegistryAppendedDocument,
        manual_overrides: dict[str, Any] | None,
    ) -> tuple[bool, list[str]]:
        event_type = str(event_row.event_type or "other").strip().lower()
        event_id = str(event_row.id)

        if event_type == "pathology":
            return patch_pathology_update(
                registry_json,
                extracted=extracted,
                event_id=event_id,
                relative_day_offset=event_row.relative_day_offset,
                manual_overrides=manual_overrides,
            )

        if event_type == "imaging":
            return patch_imaging_update(
                registry_json,
                extracted=extracted,
                event_id=event_id,
                relative_day_offset=event_row.relative_day_offset,
                event_subtype=event_row.event_subtype,
                event_title=event_row.event_title,
                source_modality=event_row.source_modality,
                manual_overrides=manual_overrides,
            )

        if event_type in {
            "clinical_update",
            "treatment_update",
            "complication",
            "clinical_status",
            "procedure_addendum",
            "procedure",
            "other",
        }:
            return patch_clinical_update(
                registry_json,
                extracted=extracted,
                event_title=event_row.event_title,
                manual_overrides=manual_overrides,
            )

        return False, list(extracted.get("qa_flags") or ["unsupported_event_type"])


def get_case_aggregator() -> CaseAggregator:
    return CaseAggregator()


__all__ = ["CaseAggregator", "get_case_aggregator"]
