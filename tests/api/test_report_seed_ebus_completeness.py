from types import SimpleNamespace

import pytest

from app.api.dependencies import get_registry_service
from app.api.fastapi_app import app
from app.registry.schema import RegistryRecord

STALE_WARNING = (
    "procedures_performed.linear_ebus.performed=true but stations_sampled is empty/missing"
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "nodal,missing_station",
    [
        ("11L needle staging with EBUS", False),
        ("EBUS aspiration of subcarinal and left hilar nodes", False),
        ("EBUS aspiration of subcarinal and right paratracheal nodes", True),
        ("EBUS nodal aspiration", True),
    ],
)
async def test_seed_station_prompts_follow_source_supported_bundle(
    api_client, monkeypatch, nodal, missing_station
):
    monkeypatch.setenv("REPORTER_SEED_STRATEGY", "registry_extract_fields")
    monkeypatch.setenv("REPORTER_DISABLE_LLM", "1")
    record = RegistryRecord.model_validate(
        {"procedures_performed": {"linear_ebus": {"performed": True}}}
    )
    result = SimpleNamespace(
        record=record, warnings=[STALE_WARNING, "Unrelated review warning"]
    )
    monkeypatch.setitem(
        app.dependency_overrides,
        get_registry_service,
        lambda: SimpleNamespace(extract_fields=lambda _: result),
    )
    response = await api_client.post(
        "/report/seed_from_text",
        json={
            "text": f"Navigated to LLL nodule and biopsied. {nodal}. No complications.",
            "already_scrubbed": True,
            "strict": True,
            "include_debug": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert any(
        p["label"] == "EBUS stations documented" for p in data["missing_field_prompts"]
    ) is missing_station
    assert any(
        "EBUS stations documented" in s for s in data["suggestions"]
    ) is missing_station
    assert any(f["message"] == STALE_WARNING for f in data["quality_flags"]) is missing_station
    assert any(f["message"] == "Unrelated review warning" for f in data["quality_flags"])
    if not missing_station:
        assert any("passes" in q["pointer"] for q in data["questions"])
        assert "Pass count not documented" in data["markdown"]
    assert not any(n["type"] == "strict_fallback" for n in data["debug_notes"])
