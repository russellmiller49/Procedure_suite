from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import sessionmaker

from app.phi.db import Base
from app.registry.application.case_aggregator import CaseAggregator
from app.registry_store.dependencies import get_registry_store_engine
from app.registry_store.models import RegistryAppendedDocument, RegistryCaseRecord


def test_case_aggregator_pathology_results_populates_fields_and_respects_locks(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "case_aggregator_pathology_results.db"
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
                manual_overrides={
                    "/pathology_results/final_diagnosis": {
                        "locked": True,
                        "updated_at": now.isoformat(),
                        "source": "manual",
                    }
                },
                created_at=now,
                updated_at=now,
            )
        )

        db.add(
            RegistryAppendedDocument(
                id=uuid.uuid4(),
                user_id="user_a",
                registry_uuid=registry_uuid,
                note_text=(
                    "PATHOLOGY FINAL REPORT\n"
                    "FINAL DIAGNOSIS:\n"
                    "Adenocarcinoma, positive for malignancy.\n"
                    "PD-L1 TPS: 60%\n"
                ),
                note_sha256="x" * 64,
                event_type="pathology",
                document_kind="pathology",
                relative_day_offset=2,
                created_at=now,
            )
        )
        db.commit()

        aggregator = CaseAggregator()
        case = aggregator.aggregate(db=db, registry_uuid=registry_uuid, user_id="user_a")
        db.commit()

        pathology = case.registry_json.get("pathology_results") or {}
        assert isinstance(pathology, dict)

        # Locked: should not be filled even if extracted.
        assert "final_diagnosis" not in pathology or pathology.get("final_diagnosis") in (None, "")

        # Still fill other pathology_results fields when unlocked (e.g., PD-L1).
        assert pathology.get("pdl1_tps_percent") == 60
    finally:
        db.close()

