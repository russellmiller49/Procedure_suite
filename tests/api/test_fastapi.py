"""Integration tests for the FastAPI surface."""

from __future__ import annotations

from pathlib import Path

from httpx import AsyncClient
import pytest

from modules.api.fastapi_app import _shape_registry_payload
from modules.common.spans import Span
from modules.registry.schema import RegistryRecord

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

pytestmark = pytest.mark.asyncio


def _read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


async def test_health_endpoint(api_client: AsyncClient) -> None:
    response = await api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


async def test_knowledge_endpoint(api_client: AsyncClient) -> None:
    response = await api_client.get("/knowledge")
    assert response.status_code == 200
    payload = response.json()
    assert payload["version"], "Knowledge version should not be empty"
    assert payload["sha256"], "Knowledge hash should not be empty"


async def test_coder_run_fixture_response(api_client: AsyncClient) -> None:
    note = _read_fixture("ppl_nav_radial_tblb.txt")
    response = await api_client.post("/v1/coder/run", json={"note": note})
    assert response.status_code == 200
    payload = response.json()
    codes = {entry["cpt"]: entry for entry in payload["codes"]}
    # EnhancedCPTCoder uses IP knowledge base which has navigation as +31627 (add-on)
    # and radial EBUS as +31654 (add-on). Accept either format for compatibility.
    expected_codes = {"31627", "+31627", "+31654", "31629", "31628", "31624"}
    found_codes = set(codes.keys())
    # Check that we have navigation (either 31627 or +31627)
    assert "31627" in found_codes or "+31627" in found_codes, f"Expected navigation code (31627 or +31627), got {found_codes}"
    # Check that we have radial EBUS (+31654)
    assert "+31654" in found_codes, f"Expected radial EBUS code (+31654), got {found_codes}"
    # Check other required codes
    assert "31629" in found_codes, "Expected TBNA code (31629)"
    assert "31628" in found_codes, "Expected TBLB code (31628)"
    assert "31624" in found_codes, "Expected BAL code (31624)"

    # MER summary is not provided by EnhancedCPTCoder (uses IP knowledge base bundling instead)
    # Only check if present (for legacy CoderEngine compatibility)
    mer_summary = payload.get("mer_summary")
    if mer_summary:
        adjustments = mer_summary.get("adjustments", [])
        if adjustments:
            assert all(adj.get("role") for adj in adjustments)


async def test_registry_run_normalizes_stations(api_client: AsyncClient) -> None:
    note = _read_fixture("ebus_staging_4R_7_11R.txt")
    response = await api_client.post("/v1/registry/run", json={"note": note, "explain": True})
    assert response.status_code == 200
    payload = response.json()
    assert payload["linear_ebus_stations"] == ["4R", "7", "11R"]
    evidence = payload.get("evidence", {})
    assert "linear_ebus_stations" in evidence
    assert evidence["linear_ebus_stations"], "Evidence for stations should be captured"


def _thoracentesis_extraction() -> dict:
    return {
        "patient_name": "Test Patient",
        "gender": "female",
        "procedure_date": "2024-05-01",
        "pleural_procedure_type": "thoracentesis",
        "pleural_side": "left",
        "pleural_volume_drained_ml": 900,
        "pleural_fluid_appearance": "serous",
        "intercostal_space": "7th",
        "entry_location": "mid-axillary",
        "pleural_guidance": "Ultrasound",
        "cxr_ordered": False,
    }


async def test_report_verify_and_render_flow(api_client: AsyncClient) -> None:
    extraction = _thoracentesis_extraction()
    verify_resp = await api_client.post("/report/verify", json={"extraction": extraction})
    assert verify_resp.status_code == 200
    verify_payload = verify_resp.json()
    warnings = verify_payload.get("warnings") or []
    assert any("CXR" in msg for msg in warnings), "Should warn when CXR not ordered"

    bundle = verify_payload["bundle"]
    proc_id = bundle["procedures"][0]["proc_id"]
    patch = {"procedures": [{"proc_id": proc_id, "updates": {"cxr_ordered": True}}]}

    render_resp = await api_client.post("/report/render", json={"bundle": bundle, "patch": patch})
    assert render_resp.status_code == 200
    render_payload = render_resp.json()
    assert render_payload["markdown"], "Rendered markdown should be present when issues resolved"
    assert not render_payload.get("issues"), "No critical issues expected after patch"
    assert not render_payload.get("warnings"), "Warnings should clear after patch"


async def test_shape_registry_payload_prunes_none_and_enriches():
    record = RegistryRecord(
        clinical_context={"asa_class": 3, "primary_indication": "Test case"},
        sedation={"type": "General", "agents_used": None},
        procedures_performed={
            "tbna_conventional": {
                "performed": True,
                "passes_per_station": 6,
                "stations_sampled": ["LB10"],
                "needle_gauge": None,
            }
        },
        billing={"cpt_codes": [{"code": "31645", "description": None}]},
    )

    payload = _shape_registry_payload(record, {"clinical_context": [Span(text="ASA 3", start=0, end=5)]})

    def _contains_none(obj):
        if obj is None:
            return True
        if isinstance(obj, dict):
            return any(_contains_none(v) for v in obj.values())
        if isinstance(obj, list):
            return any(_contains_none(v) for v in obj)
        return False

    assert not _contains_none(payload), "Payload should be pruned of None values"
    assert payload["billing"]["cpt_codes_simple"] == ["31645"]
    tbna = payload["procedures_performed"]["tbna_conventional"]
    assert tbna["summary"].startswith("Performed")
    assert payload["evidence"]["clinical_context"][0]["start"] == 0
