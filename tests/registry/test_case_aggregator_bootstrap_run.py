from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import sessionmaker

from app.phi.db import Base
from app.registry.application.case_aggregator import CaseAggregator
from app.registry.schema import RegistryRecord
from app.registry_store.dependencies import get_registry_store_engine
from app.registry_store.models import RegistryAppendedDocument, RegistryRun


def test_case_aggregator_bootstraps_procedure_context_from_latest_run(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "case_aggregator_bootstrap_run.db"
    monkeypatch.setenv("REGISTRY_STORE_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("REGISTRY_APPEND_EXTRACTION_MODE", "deterministic")

    engine = get_registry_store_engine()
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        registry_uuid = uuid.uuid4()
        now = datetime.now(timezone.utc)

        baseline_registry = RegistryRecord().model_dump(exclude_none=True, mode="json")
        baseline_registry.setdefault("procedure", {})["indication"] = "Mediastinal adenopathy"

        run_id = uuid.uuid4()
        db.add(
            RegistryRun(
                id=run_id,
                created_at=now,
                submitter_name=None,
                note_text="Baseline scrubbed procedure note",
                note_sha256="a" * 64,
                schema_version="v3",
                pipeline_config={},
                raw_response_json={
                    "registry_uuid": str(registry_uuid),
                    "registry": baseline_registry,
                },
                needs_manual_review=False,
                review_status="new",
            )
        )

        append_id = uuid.uuid4()
        db.add(
            RegistryAppendedDocument(
                id=append_id,
                user_id="user_a",
                registry_uuid=registry_uuid,
                note_text="PATHOLOGY FINAL REPORT\nFINAL DIAGNOSIS: Benign lymph node aspirate.",
                note_sha256="b" * 64,
                event_type="pathology",
                document_kind="pathology",
                relative_day_offset=0,
                created_at=now,
            )
        )
        db.commit()

        aggregator = CaseAggregator()
        case = aggregator.aggregate(db=db, registry_uuid=registry_uuid, user_id="user_a")
        db.commit()

        assert str(case.source_run_id) == str(run_id)
        assert (case.registry_json.get("procedure") or {}).get("indication") == "Mediastinal adenopathy"
        assert bool((case.registry_json.get("pathology_results") or {}).get("final_diagnosis"))
    finally:
        db.close()
