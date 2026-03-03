from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import sessionmaker

from app.phi.db import Base
from app.registry.application.case_aggregator import CaseAggregator
from app.registry_store.dependencies import get_registry_store_engine
from app.registry_store.models import RegistryAppendedDocument, RegistryCaseRecord


def test_case_aggregator_respects_field_lock(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "case_aggregator_locks.db"
    monkeypatch.setenv("REGISTRY_STORE_DATABASE_URL", f"sqlite:///{db_path}")
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
                registry_json={
                    "procedures_performed": {
                        "linear_ebus": {
                            "node_events": [
                                {
                                    "station": "11L",
                                    "action": "needle_aspiration",
                                    "evidence_quote": "sampled station 11L",
                                    "path_result": "Positive",
                                }
                            ]
                        }
                    }
                },
                schema_version="v3",
                version=1,
                source_run_id=None,
                manual_overrides={
                    "/procedures_performed/linear_ebus/node_events/0/path_result": {
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
                note_text="A. 11L lymph node, fine needle aspiration: Negative for malignancy.",
                note_sha256="x" * 64,
                event_type="pathology",
                document_kind="pathology",
                relative_day_offset=3,
                created_at=now,
            )
        )
        db.commit()

        aggregator = CaseAggregator()
        case = aggregator.aggregate(db=db, registry_uuid=registry_uuid, user_id="user_a")
        db.commit()

        node_event = case.registry_json["procedures_performed"]["linear_ebus"]["node_events"][0]
        assert node_event["path_result"] == "Positive"

        row = db.query(RegistryAppendedDocument).filter_by(registry_uuid=registry_uuid).one()
        assert row.aggregated_at is not None
        assert row.aggregation_version == case.version
    finally:
        db.close()
