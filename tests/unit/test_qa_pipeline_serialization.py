import json

from app.api.services.qa_pipeline import _serialize_jsonable
from app.reporting.metadata import MissingFieldIssue


def test_qa_pipeline_serializes_missing_field_issues_to_json() -> None:
    issues = [
        MissingFieldIssue(
            proc_id="proc_1",
            proc_type="ebus_tbna",
            template_id="ebus_tbna",
            field_path="stations[0].station_name",
            severity="warning",
            message="Missing station name",
        )
    ]

    payload = {"issues": issues}
    serialized = _serialize_jsonable(payload)

    # Must be JSON-serializable (this used to crash when calling `.model_dump()` on dataclasses).
    json.dumps(serialized)

    assert serialized["issues"][0]["proc_id"] == "proc_1"
