from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_process_bundle_rejects_absolute_dates(api_client: AsyncClient) -> None:
    payload = {
        "zk_patient_id": "zk_1",
        "episode_id": "ep_1",
        "documents": [
            {
                "timepoint_role": "INDEX_PROCEDURE",
                "seq": 1,
                "text": "Procedure date: 2024-01-01\\nBronchoscopy performed.",
            }
        ],
    }
    resp = await api_client.post("/api/v1/process_bundle", json=payload)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_process_bundle_rejects_absolute_dates_inside_bracket_tokens(
    api_client: AsyncClient,
) -> None:
    payload = {
        "zk_patient_id": "zk_1",
        "episode_id": "ep_1",
        "documents": [
            {
                "timepoint_role": "INDEX_PROCEDURE",
                "seq": 1,
                "text": "[SYSTEM: DOC_DATE=2024-01-01]\\nBronchoscopy performed.",
            }
        ],
    }
    resp = await api_client.post("/api/v1/process_bundle", json=payload)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_process_bundle_succeeds_with_relative_tokens(api_client: AsyncClient) -> None:
    payload = {
        "zk_patient_id": "zk_1",
        "episode_id": "ep_1",
        "documents": [
            {
                "timepoint_role": "INDEX_PROCEDURE",
                "seq": 2,
                "text": "[SYSTEM: Document timeline is T+0 DAYS from Index Procedure]\\nBronchoscopy performed.",
            },
            {
                "timepoint_role": "FOLLOW_UP",
                "seq": 1,
                "text": "[SYSTEM: Document timeline is T+5 DAYS from Index Procedure]\\nPatient seen on [DATE: T+5 DAYS] for follow-up.",
            },
        ],
        "already_scrubbed": True,
        "include_financials": False,
        "explain": False,
    }

    resp = await api_client.post("/api/v1/process_bundle", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["zk_patient_id"] == "zk_1"
    assert data["episode_id"] == "ep_1"
    assert len(data["documents"]) == 2
    assert data["documents"][0]["seq"] == 1
    assert data["documents"][0]["timepoint_role"] == "FOLLOW_UP"
    assert data["documents"][0]["doc_t_offset_days"] == 5
    assert data["documents"][1]["seq"] == 2
    assert data["documents"][1]["timepoint_role"] == "INDEX_PROCEDURE"
    assert data["documents"][1]["doc_t_offset_days"] == 0

    timeline = data.get("timeline") or {}
    assert timeline.get("doc_offsets_by_role", {}).get("INDEX_PROCEDURE") == 0
    assert timeline.get("follow_up_offsets") == [5]
