from __future__ import annotations

from app.api.schemas import RenderRequest
from proc_schemas.clinical.airway import EBUSTBNA, EBUSStationSample
from proc_schemas.clinical.common import (
    EncounterInfo,
    PatientInfo,
    ProcedureBundle,
    ProcedureInput,
)


def _bundle() -> ProcedureBundle:
    return ProcedureBundle(
        patient=PatientInfo(name="Test Patient", age=65, sex="female"),
        encounter=EncounterInfo(date="2026-02-05", attending="Dr. Test"),
        procedures=[
            ProcedureInput(
                proc_type="ebus_tbna",
                schema_id="ebus_tbna_v1",
                proc_id="ebus_tbna_1",
                data=EBUSTBNA(
                    needle_gauge=None,
                    stations=[
                        EBUSStationSample(
                            station_name="7",
                            size_mm=None,
                            passes=None,
                            echo_features=None,
                            biopsy_tools=["TBNA"],
                            rose_result=None,
                            comments=None,
                        )
                    ],
                    rose_available=None,
                    overall_rose_diagnosis=None,
                ),
            )
        ],
    )


def test_render_request_normalizes_echo_features_and_tests_patch_values() -> None:
    req = RenderRequest.model_validate(
        {
            "bundle": _bundle(),
            "patch": [
                {
                    "op": "replace",
                    "path": "/procedures/0/data/stations/0/echo_features",
                    "value": ["heterogeneous", "round"],
                },
                {
                    "op": "replace",
                    "path": "/procedures/0/data/tests",
                    "value": "Cytology; Microbiology\nFlow Cytometry",
                },
                {
                    "op": "replace",
                    "path": "/procedures/0/data/tests",
                    "value": [" Pathology ", " Cytology "],
                },
            ],
        }
    )

    assert isinstance(req.patch, list)
    assert req.patch[0].value == "heterogeneous, round"
    assert req.patch[1].value == ["Cytology", "Microbiology", "Flow Cytometry"]
    assert req.patch[2].value == ["Pathology", "Cytology"]
