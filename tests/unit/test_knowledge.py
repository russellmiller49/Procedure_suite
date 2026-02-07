from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.common import knowledge


def test_knowledge_snapshot_has_expected_fields() -> None:
    snapshot = knowledge.knowledge_snapshot(top_n=5)
    assert snapshot.version
    assert snapshot.sha256
    assert snapshot.rvus and len(snapshot.rvus) <= 5
    assert snapshot.add_on_codes is not None
    assert snapshot.bundling_rules is not None


def test_invalid_knowledge_raises_validation_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "version": "1.0.0",
        "rvus": {"31622": {"work": 1.0, "pe": 2.0}},  # missing mp field
        "add_on_codes": ["+31622"],
        "synonyms": {},
        "bundling_rules": {"dummy_rule": {"description": "demo"}},
        "ncci_pairs": [],
    }
    target = tmp_path / "bad_knowledge.json"
    target.write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setenv(knowledge.KNOWLEDGE_ENV_VAR, str(target))
    knowledge.reset_cache()

    with pytest.raises(knowledge.KnowledgeValidationError) as excinfo:
        knowledge.get_knowledge(force_reload=True)
    assert "rvus" in str(excinfo.value)
