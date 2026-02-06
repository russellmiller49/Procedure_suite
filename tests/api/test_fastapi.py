"""Integration tests for the FastAPI surface."""

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import AsyncClient

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
    data = response.json()
    assert data["ok"] is True
    # Ready field depends on app.state.model_ready (set by conftest.py fixture)


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
    found_codes = set(codes.keys())
    # Check that we have navigation (either 31627 or +31627)
    assert "31627" in found_codes or "+31627" in found_codes, (
        f"Expected navigation code (31627 or +31627), got {found_codes}"
    )
    # Check that we have radial EBUS (+31654)
    assert "+31654" in found_codes, (
        f"Expected radial EBUS code (+31654), got {found_codes}"
    )
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
    response = await api_client.post(
        "/v1/registry/run",
        json={"note": note, "explain": True},
    )
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


def _find_proc_index(bundle: dict, proc_type: str) -> int:
    for idx, proc in enumerate(bundle.get("procedures", [])):
        if proc.get("proc_type") == proc_type:
            return idx
    raise AssertionError(f"{proc_type} procedure not found in bundle")


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


async def test_report_questions__ebus_station7(api_client: AsyncClient) -> None:
    seed_resp = await api_client.post("/report/seed_from_text", json={"text": "EBUS biopsied station 7"})
    assert seed_resp.status_code == 200
    seed_payload = seed_resp.json()
    bundle = seed_payload["bundle"]

    questions_resp = await api_client.post("/report/questions", json={"bundle": bundle})
    assert questions_resp.status_code == 200
    payload = questions_resp.json()

    ebus_index = _find_proc_index(payload["bundle"], "ebus_tbna")
    pointers = {question["pointer"] for question in payload.get("questions") or []}
    assert f"/procedures/{ebus_index}/data/needle_gauge" in pointers
    assert f"/procedures/{ebus_index}/data/stations/0/passes" in pointers
    assert f"/procedures/{ebus_index}/data/stations/0/size_mm" in pointers


async def test_seed_from_text__ebus_station7(api_client: AsyncClient) -> None:
    response = await api_client.post("/report/seed_from_text", json={"text": "EBUS biopsied station 7"})
    assert response.status_code == 200
    payload = response.json()

    assert payload["bundle"]
    assert payload["markdown"], "Seed call should return a rendered draft markdown"
    assert payload.get("questions"), "Seed call should return follow-up questions"

    ebus_index = _find_proc_index(payload["bundle"], "ebus_tbna")
    pointers = {question["pointer"] for question in payload.get("questions") or []}
    assert f"/procedures/{ebus_index}/data/needle_gauge" in pointers


async def test_seed_from_text__ebus_staging_typos_generates_questions(api_client: AsyncClient) -> None:
    note = (
        "Staging EBUS via LMA staion 11L, 4L 7 and 4R evalauated. "
        "Biospy performed of 4R ROSE positive for malignancy"
    )
    response = await api_client.post("/report/seed_from_text", json={"text": note})
    assert response.status_code == 200
    payload = response.json()

    ebus_index = _find_proc_index(payload["bundle"], "ebus_tbna")

    markdown = payload.get("markdown") or ""
    assert "EBUS survey" in markdown
    assert "Station: 4R" in markdown

    questions = payload.get("questions") or []
    assert questions, "Seed call should return follow-up questions"
    pointers = {question["pointer"] for question in questions}
    assert f"/procedures/{ebus_index}/data/needle_gauge" in pointers
    assert any(
        pointer.startswith(f"/procedures/{ebus_index}/data/stations/") for pointer in pointers
    )


async def test_patch_and_rerender__ebus_station7(api_client: AsyncClient) -> None:
    seed_resp = await api_client.post("/report/seed_from_text", json={"text": "EBUS biopsied station 7"})
    assert seed_resp.status_code == 200
    seed_payload = seed_resp.json()

    bundle = seed_payload["bundle"]
    initial_issue_paths = {issue["field_path"] for issue in seed_payload.get("issues") or []}
    ebus_index = _find_proc_index(bundle, "ebus_tbna")

    patch_ops = [
        {"op": "replace", "path": f"/procedures/{ebus_index}/data/needle_gauge", "value": "22"},
        {"op": "replace", "path": f"/procedures/{ebus_index}/data/stations/0/passes", "value": 4},
        {"op": "replace", "path": f"/procedures/{ebus_index}/data/stations/0/size_mm", "value": 12},
        {"op": "replace", "path": f"/procedures/{ebus_index}/data/rose_available", "value": True},
    ]

    render_resp = await api_client.post(
        "/report/render",
        json={"bundle": bundle, "patch": patch_ops},
    )
    assert render_resp.status_code == 200
    render_payload = render_resp.json()

    markdown = render_payload.get("markdown") or ""
    assert "22 needle" in markdown
    assert "Number of Passes: 4" in markdown
    assert "Size: 12" in markdown
    assert "mmBiopsy Tools" not in markdown
    assert "TBNANumber of Passes" not in markdown

    updated_issue_paths = {issue["field_path"] for issue in render_payload.get("issues") or []}
    assert "needle_gauge" not in updated_issue_paths
    assert "stations[0].passes" not in updated_issue_paths
    assert "stations[0].size_mm" not in updated_issue_paths
    assert len(updated_issue_paths) < len(initial_issue_paths)


async def test_report_render_returns_422_for_invalid_json_patch(api_client: AsyncClient) -> None:
    seed_resp = await api_client.post("/report/seed_from_text", json={"text": "EBUS biopsied station 7"})
    assert seed_resp.status_code == 200
    seed_payload = seed_resp.json()
    bundle = seed_payload["bundle"]
    ebus_index = _find_proc_index(bundle, "ebus_tbna")

    invalid_patch_ops = [
        {
            "op": "replace",
            "path": f"/procedures/{ebus_index}/data/does_not_exist",
            "value": "x",
        }
    ]

    render_resp = await api_client.post(
        "/report/render",
        json={"bundle": bundle, "patch": invalid_patch_ops},
    )
    assert render_resp.status_code == 422
    payload = render_resp.json()
    assert "patch" in str(payload.get("detail", "")).lower()


async def test_report_seed_from_text_strict_does_not_500(api_client: AsyncClient) -> None:
    response = await api_client.post(
        "/report/seed_from_text",
        json={"text": "EBUS biopsied station 7", "strict": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("markdown"), "Strict mode should still return a preview markdown"


async def test_report_render_coerces_echo_features_multiselect_to_string(api_client: AsyncClient) -> None:
    seed_resp = await api_client.post("/report/seed_from_text", json={"text": "EBUS biopsied station 7"})
    assert seed_resp.status_code == 200
    seed_payload = seed_resp.json()
    bundle = seed_payload["bundle"]
    ebus_index = _find_proc_index(bundle, "ebus_tbna")

    patch_ops = [
        {
            "op": "replace",
            "path": f"/procedures/{ebus_index}/data/stations/0/echo_features",
            "value": ["Round", "Hypoechoic"],
        }
    ]
    render_resp = await api_client.post(
        "/report/render",
        json={"bundle": bundle, "patch": patch_ops},
    )
    assert render_resp.status_code == 200
    payload = render_resp.json()

    echo_value = payload["bundle"]["procedures"][ebus_index]["data"]["stations"][0]["echo_features"]
    assert echo_value == "Round, Hypoechoic"

    markdown = payload.get("markdown") or ""
    assert "Echo Features:" in markdown
    assert "Round, Hypoechoic" in markdown


async def test_seed_from_text_and_patch__ion_nav_tbna_cryo(api_client: AsyncClient, monkeypatch) -> None:
    # The navigation + peripheral seeding relies on the extraction-first parallel_ner engine,
    # which produces the nested V3 shapes (equipment/procedures_performed) used by the compat layer.
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")

    note = (
        "Ion bronchoscopy RUL 2.2 cm nodule. Tool in lesion confirmed with CBCT. "
        "TBNA and cryobiopsy. ROSE + for malignancy"
    )
    seed_resp = await api_client.post("/report/seed_from_text", json={"text": note})
    assert seed_resp.status_code == 200
    seed_payload = seed_resp.json()

    bundle = seed_payload["bundle"]
    markdown = seed_payload.get("markdown") or ""
    assert "Robotic navigation using the Ion platform" in markdown
    assert "CBCT/CACT spin" in markdown
    assert "Tool-in-lesion was confirmed" in markdown

    assert bundle.get("procedures"), "Expected at least one procedure to be seeded"
    assert _find_proc_index(bundle, "robotic_navigation") >= 0
    assert _find_proc_index(bundle, "cbct_cact_fusion") >= 0
    assert _find_proc_index(bundle, "tool_in_lesion_confirmation") >= 0
    tna_index = _find_proc_index(bundle, "transbronchial_needle_aspiration")
    cryo_index = _find_proc_index(bundle, "transbronchial_cryobiopsy")

    pointers = {question["pointer"] for question in seed_payload.get("questions") or []}
    assert f"/procedures/{tna_index}/data/samples_collected" in pointers
    assert f"/procedures/{tna_index}/data/tests" in pointers
    assert f"/procedures/{cryo_index}/data/num_samples" in pointers
    assert f"/procedures/{cryo_index}/data/blocker_type" in pointers
    assert f"/procedures/{cryo_index}/data/cryoprobe_size_mm" in pointers

    patch_ops = [
        {"op": "replace", "path": f"/procedures/{tna_index}/data/lung_segment", "value": "RUL"},
        {"op": "replace", "path": f"/procedures/{tna_index}/data/samples_collected", "value": 6},
        # Accept a string for tests and let the server normalize to a list.
        {"op": "replace", "path": f"/procedures/{tna_index}/data/tests", "value": "Cytology, Microbiology"},
        {"op": "replace", "path": f"/procedures/{cryo_index}/data/lung_segment", "value": "RUL"},
        {"op": "replace", "path": f"/procedures/{cryo_index}/data/num_samples", "value": 4},
        {"op": "add", "path": f"/procedures/{cryo_index}/data/blocker_type", "value": "Fogarty"},
        {"op": "add", "path": f"/procedures/{cryo_index}/data/cryoprobe_size_mm", "value": 1.9},
    ]

    render_resp = await api_client.post(
        "/report/render",
        json={"bundle": bundle, "patch": patch_ops},
    )
    assert render_resp.status_code == 200
    render_payload = render_resp.json()

    assert not render_payload.get("issues"), "Expected missing-field issues to clear after patch"
    markdown = render_payload.get("markdown") or ""
    assert "Transbronchial needle aspiration was performed" in markdown
    assert "Cytology" in markdown
    assert "Microbiology" in markdown
    assert "Fogarty" in markdown

    updated_tests = render_payload["bundle"]["procedures"][tna_index]["data"]["tests"]
    assert updated_tests == ["Cytology", "Microbiology"]


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

    payload = _shape_registry_payload(
        record,
        {"clinical_context": [Span(text="ASA 3", start=0, end=5)]},
    )

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
    assert payload["evidence"]["clinical_context"][0]["span"] == [0, 5]
