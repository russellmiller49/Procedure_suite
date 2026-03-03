from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid

from sqlalchemy.orm import sessionmaker

from app.phi.db import Base
from app.registry.application.case_aggregator import CaseAggregator
from app.registry_store.dependencies import get_registry_store_engine
from app.registry_store.models import RegistryAppendedDocument, RegistryCaseRecord


def test_case_aggregator_imaging_subtype_baseline_vs_followups(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "case_aggregator_imaging_summary.db"
    monkeypatch.setenv("REGISTRY_STORE_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("REGISTRY_APPEND_EXTRACTION_MODE", "deterministic")

    engine = get_registry_store_engine()
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        registry_uuid = uuid.uuid4()
        now = datetime.now(timezone.utc)

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
                id=uuid.uuid4(),
                user_id="user_a",
                registry_uuid=registry_uuid,
                note_text="CT CHEST\nIMPRESSION: Stable right upper lobe nodule measuring 10 mm.",
                note_sha256="x" * 64,
                event_type="imaging",
                document_kind="imaging",
                source_modality="ct",
                event_subtype="preop",
                event_title="Baseline CT",
                relative_day_offset=0,
                created_at=now,
            )
        )
        db.add(
            RegistryAppendedDocument(
                id=uuid.uuid4(),
                user_id="user_a",
                registry_uuid=registry_uuid,
                note_text="PET/CT\nIMPRESSION: Increased size of right upper lobe lesion. SUV max 12.3.",
                note_sha256="y" * 64,
                event_type="imaging",
                document_kind="imaging",
                source_modality="pet_ct",
                event_subtype="followup",
                event_title="Follow-up PET-CT",
                relative_day_offset=30,
                created_at=now + timedelta(seconds=1),
            )
        )
        db.commit()

        aggregator = CaseAggregator()
        case = aggregator.aggregate(db=db, registry_uuid=registry_uuid, user_id="user_a")
        db.commit()

        imaging = case.registry_json.get("imaging_summary") or {}
        assert isinstance(imaging, dict)

        baseline = imaging.get("baseline") or None
        assert isinstance(baseline, dict)
        assert baseline.get("subtype") == "preop"
        assert baseline.get("modality") == "ct"

        followups = imaging.get("followups") or []
        assert isinstance(followups, list)
        assert len(followups) == 1
        assert isinstance(followups[0], dict)
        assert followups[0].get("subtype") == "followup"
        assert followups[0].get("modality") == "pet_ct"
    finally:
        db.close()

