from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import sessionmaker

from app.phi.db import Base
from app.registry.application.case_aggregator import CaseAggregator
from app.registry_store.dependencies import get_registry_store_engine
from app.registry_store.models import RegistryAppendedDocument, RegistryCaseRecord


def test_case_aggregator_structured_clinical_followup_updates_current_state(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "case_aggregator_clinical_followup.db"
    monkeypatch.setenv("REGISTRY_STORE_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("REGISTRY_APPEND_EXTRACTION_MODE", "deterministic")

    engine = get_registry_store_engine()
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        registry_uuid = uuid.uuid4()
        now = datetime.now(timezone.utc)
        append_id = uuid.uuid4()

        db.add(
            RegistryCaseRecord(
                registry_uuid=registry_uuid,
                registry_json={},
                schema_version="v3",
                version=1,
                source_run_id=None,
                manual_overrides={},
                created_at=now,
                updated_at=now,
            )
        )

        db.add(
            RegistryAppendedDocument(
                id=append_id,
                user_id="user_a",
                registry_uuid=registry_uuid,
                note_text="",
                note_sha256="x" * 64,
                event_type="clinical_update",
                document_kind="clinical_update",
                relative_day_offset=10,
                metadata_json={
                    "structured_data": {
                        "hospital_admission": True,
                        "icu_admission": True,
                        "deceased": None,
                        "disease_status": "Progression",
                        "comment": "Admitted to ICU for respiratory failure.",
                    }
                },
                created_at=now,
            )
        )
        db.commit()

        aggregator = CaseAggregator()
        case = aggregator.aggregate(db=db, registry_uuid=registry_uuid, user_id="user_a")
        db.commit()

        clinical = case.registry_json.get("clinical_course") or {}
        assert isinstance(clinical, dict)

        updates = clinical.get("updates") or []
        assert isinstance(updates, list)
        assert len(updates) == 1
        assert isinstance(updates[0], dict)

        assert updates[0].get("hospital_admission") is True
        assert updates[0].get("icu_admission") is True
        assert updates[0].get("disease_status") == "Progression"
        assert updates[0].get("source_event_id") is not None

        current = clinical.get("current_state") or {}
        assert isinstance(current, dict)
        assert current.get("hospital_admission") is True
        assert current.get("icu_admission") is True
        assert current.get("disease_status") == "Progression"
        assert current.get("source_event_id") is not None
    finally:
        db.close()

