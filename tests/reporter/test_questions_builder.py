from __future__ import annotations

from modules.reporting.engine import list_missing_critical_fields
from modules.reporting.questions import build_questions
from proc_schemas.clinical.airway import EBUSStationSample, EBUSTBNA
from proc_schemas.clinical.common import EncounterInfo, PatientInfo, ProcedureBundle, ProcedureInput


def _ebus_station7_bundle_missing_core_fields() -> ProcedureBundle:
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


def test_questions_from_missing_fields__ebus_station7() -> None:
    bundle = _ebus_station7_bundle_missing_core_fields()
    issues = list_missing_critical_fields(bundle)
    questions = build_questions(bundle, issues)

    by_pointer = {question.pointer: question for question in questions}

    assert "/procedures/0/data/needle_gauge" in by_pointer
    assert "/procedures/0/data/stations/0/passes" in by_pointer
    assert "/procedures/0/data/stations/0/size_mm" in by_pointer

    # Group should include station label for station-scoped fields.
    station_passes_question = by_pointer["/procedures/0/data/stations/0/passes"]
    assert station_passes_question.group == "EBUS Station 7"

    # Prompt registry should include high-yield quality fields beyond critical gaps.
    assert "/procedures/0/data/stations/0/echo_features" in by_pointer
    assert "/procedures/0/data/rose_available" in by_pointer
