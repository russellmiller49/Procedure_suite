from __future__ import annotations

from app.registry.completeness import generate_missing_field_prompts
from app.registry.schema import RegistryRecord


def test_ecog_prompt_is_recommended_when_missing() -> None:
    record = RegistryRecord.model_validate({})

    prompts = generate_missing_field_prompts(record)
    ecog_prompt = next((p for p in prompts if p.path == "clinical_context.ecog_score"), None)

    assert ecog_prompt is not None
    assert ecog_prompt.label == "ECOG/Zubrod performance status"
    assert ecog_prompt.severity == "recommended"


def test_ecog_prompt_not_emitted_when_present() -> None:
    record = RegistryRecord.model_validate({"clinical_context": {"ecog_score": 2}})

    prompts = generate_missing_field_prompts(record)
    paths = {p.path for p in prompts}

    assert "clinical_context.ecog_score" not in paths
