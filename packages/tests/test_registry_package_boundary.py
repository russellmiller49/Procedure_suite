import hashlib
from pathlib import Path
import sys
from uuid import uuid4

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "packages/ip_registry_contracts/src"), str(ROOT / "packages/ip_registry_engine/src")]
from ip_registry_contracts.models import ExtractionRequest, NationalRegistryRecord
from ip_registry_engine.engine import LocalDeterministicProvider


@pytest.mark.parametrize("relative", ["sanitize.py", "pathology/normalize.py", "pathology/extract_pathology.py", "clinical/extract_clinical_update.py"])
def test_packaged_clinical_logic_is_unchanged(relative):
    original = (ROOT / "app/registry/aggregation" / relative).read_text()
    packaged = (ROOT / "packages/ip_registry_engine/src/ip_registry_engine/aggregation" / relative).read_text()
    assert packaged == original.replace("app.registry.aggregation", "ip_registry_engine.aggregation")


@pytest.mark.parametrize("text,expected", [
    ("Station 7: Negative for malignancy.", "Negative"),
    ("Station 4R: Positive for malignant cells.", "Positive"),
    ("Station 11L: Non-diagnostic specimen.", "Non-diagnostic"),
])
def test_pathology_proposal_carries_source_binding(text, expected):
    request = ExtractionRequest(job_id=uuid4(), source_document_id=uuid4(), source_digest=hashlib.sha256(text.encode()).hexdigest(), text=text, kind="pathology")
    result = LocalDeterministicProvider().extract(request)
    assert result.job_id == request.job_id and result.source_digest == request.source_digest
    assert result.observations["node_updates"][0]["path_result"] == expected
    assert "requires_clinical_review" in result.warnings
