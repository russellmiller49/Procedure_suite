import pytest

from app.reporting import (
    EncounterInfo,
    PatientInfo,
    ProcedureBundle,
    ProcedureInput,
    build_procedure_bundle_from_extraction,
    compose_structured_report,
    compose_structured_report_from_extraction,
)
from app.registry.processing.linear_ebus_stations_detail import extract_linear_ebus_stations_detail


def _minimal_bronch_core() -> ProcedureInput:
    return ProcedureInput(
        proc_type="bronchoscopy_core",
        schema_id="bronchoscopy_shell_v1",
        proc_id="bronchoscopy_core_1",
        data={
            "airway_overview": "Systematic airway inspection completed.",
            "right_lung_overview": "Patent.",
            "left_lung_overview": "Patent.",
        },
        sequence=1,
    )


def test_cbct_ordering_and_single_tool_in_lesion_confirmation() -> None:
    bundle = ProcedureBundle(
        patient=PatientInfo(name="Ordering Test"),
        encounter=EncounterInfo(date="2026-02-20", attending="Dr. Ordering"),
        procedures=[
            _minimal_bronch_core(),
            ProcedureInput(
                proc_type="cbct_cact_fusion",
                schema_id="cbct_cact_fusion_v1",
                proc_id="cbct_1",
                data={"overlay_result": "corrected trajectory to lesion center"},
                sequence=2,
            ),
            ProcedureInput(
                proc_type="radial_ebus_sampling",
                schema_id="radial_ebus_sampling_v1",
                proc_id="radial_sampling_1",
                data={
                    "ultrasound_pattern": "concentric",
                    "sampling_tools": ["forceps"],
                },
                sequence=3,
            ),
            ProcedureInput(
                proc_type="tool_in_lesion_confirmation",
                schema_id="tool_in_lesion_confirmation_v1",
                proc_id="til_1",
                data={"confirmation_method": "CBCT", "rebus_pattern": "concentric"},
                sequence=4,
            ),
        ],
        free_text_hint="CBCT was used for localization confirmation.",
    )

    note = compose_structured_report(bundle)
    cbct_idx = note.find("A CBCT/CACT spin was obtained")
    til_idx = note.find("Tool-in-lesion was confirmed")
    assert cbct_idx != -1 and til_idx != -1
    assert cbct_idx < til_idx
    assert note.count("Tool-in-lesion was confirmed") == 1


def test_moderate_sedation_does_not_fall_back_to_general_anesthesia() -> None:
    extraction = {
        "source_text": (
            "Moderate sedation was provided with midazolam 2 mg and fentanyl 75 mcg. "
            "Sedation start: 10:10. Sedation end: 10:36."
        ),
        "procedures": [
            {
                "proc_type": "bronchoscopy_core",
                "schema_id": "bronchoscopy_shell_v1",
                "proc_id": "bronchoscopy_core_1",
                "data": {
                    "airway_overview": "Survey completed.",
                    "right_lung_overview": "Patent.",
                    "left_lung_overview": "Patent.",
                },
            }
        ],
    }

    note = compose_structured_report_from_extraction(extraction)
    assert "Moderate sedation" in note
    assert "General anesthesia" not in note
    assert "After adequate sedation was achieved" in note


def test_multi_target_navigation_summary_and_sampling_not_collapsed() -> None:
    bundle = ProcedureBundle(
        patient=PatientInfo(name="Multi Target"),
        encounter=EncounterInfo(date="2026-02-20", attending="Dr. Multi"),
        procedures=[
            _minimal_bronch_core(),
            ProcedureInput(
                proc_type="robotic_navigation",
                schema_id="robotic_navigation_v1",
                proc_id="nav_1",
                data={"platform": "Ion", "lesion_location": "RUL"},
                sequence=2,
            ),
            ProcedureInput(
                proc_type="robotic_navigation",
                schema_id="robotic_navigation_v1",
                proc_id="nav_2",
                data={"platform": "Ion", "lesion_location": "RML"},
                sequence=3,
            ),
            ProcedureInput(
                proc_type="robotic_navigation",
                schema_id="robotic_navigation_v1",
                proc_id="nav_3",
                data={"platform": "Ion", "lesion_location": "LLL"},
                sequence=4,
            ),
            ProcedureInput(
                proc_type="transbronchial_biopsy",
                schema_id="transbronchial_biopsy_v1",
                proc_id="tbbx_1",
                data={"lobe": "RUL", "guidance": "Fluoroscopy", "tool": "Forceps", "number_of_biopsies": 2},
                sequence=10,
            ),
            ProcedureInput(
                proc_type="transbronchial_biopsy",
                schema_id="transbronchial_biopsy_v1",
                proc_id="tbbx_2",
                data={"lobe": "RML", "guidance": "Fluoroscopy", "tool": "Forceps", "number_of_biopsies": 2},
                sequence=11,
            ),
            ProcedureInput(
                proc_type="transbronchial_biopsy",
                schema_id="transbronchial_biopsy_v1",
                proc_id="tbbx_3",
                data={"lobe": "LLL", "guidance": "Fluoroscopy", "tool": "Forceps", "number_of_biopsies": 2},
                sequence=12,
            ),
        ],
    )

    note_1 = compose_structured_report(bundle)
    note_2 = compose_structured_report(bundle)

    assert "to 3 targets (RUL, RML, LLL)" in note_1
    assert "Transbronchial biopsy of RUL" in note_1
    assert "Transbronchial biopsy of RML" in note_1
    assert "Transbronchial biopsy of LLL" in note_1
    assert note_1 == note_2


def test_rose_not_propagated_to_ebus_stations_without_station_scoped_evidence() -> None:
    extraction = {
        "source_text": (
            "Peripheral lesion sampling ROSE: site 1 and 3 atypical cells. "
            "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
            "EBUS staging was completed with stations 4R and 7 sampled."
        ),
        "linear_ebus_stations": ["4R", "7"],
        "ebus_rose_result": "site 1 and 3 atypical cells",
        "procedures": [
            {
                "proc_type": "bronchoscopy_core",
                "schema_id": "bronchoscopy_shell_v1",
                "proc_id": "bronchoscopy_core_1",
                "data": {
                    "airway_overview": "Survey completed.",
                    "right_lung_overview": "Patent.",
                    "left_lung_overview": "Patent.",
                },
            }
        ],
    }

    bundle = build_procedure_bundle_from_extraction(extraction)
    ebus_proc = next(proc for proc in bundle.procedures if proc.proc_type == "ebus_tbna")
    ebus_data = ebus_proc.data.model_dump(exclude_none=False) if hasattr(ebus_proc.data, "model_dump") else ebus_proc.data
    for station in ebus_data.get("stations") or []:
        assert not station.get("rose_result")

    note = compose_structured_report(bundle)
    assert "Station 4R" in note or "Station: 4R" in note
    assert "ROSE Results:" not in note


def test_shortform_note_populates_ebus_station_detail_and_sample_counts() -> None:
    note = (
        "Ion robotic bronchoscopy and staging EBUS for RUL nodule. "
        "5 peripheral needle biopsies with ROSE positive for malignancy followed by 3 cryobiopsies with 1.1 mm probe. "
        "Biopsy of 4L (7.6mm) 5 passes 22G needle ROSE adequate, "
        "7 (6.2 mm) 5 passes 22G needle ROSE adequate, "
        "4R (8.2mm) 5 passes 22G needle ROSE malignant."
    )

    extraction = {
        "source_text": note,
        "procedures_performed": {
            "peripheral_tbna": {"performed": True},
            "transbronchial_cryobiopsy": {"performed": True},
            "linear_ebus": {"performed": True},
        },
        "linear_ebus_stations": ["4L", "7", "4R"],
        "granular_data": {
            "linear_ebus_stations_detail": extract_linear_ebus_stations_detail(note),
        },
        "nav_platform": "Ion",
        "lesion_location": "RUL",
    }

    bundle = build_procedure_bundle_from_extraction(extraction)

    ebus_proc = next(proc for proc in bundle.procedures if proc.proc_type == "ebus_tbna")
    ebus_data = ebus_proc.data.model_dump(exclude_none=False) if hasattr(ebus_proc.data, "model_dump") else ebus_proc.data
    stations = {st.get("station_name"): st for st in (ebus_data.get("stations") or [])}
    assert ebus_data.get("needle_gauge")
    assert stations["4L"]["size_mm"] == 7.6
    assert stations["4L"]["passes"] == 5
    assert stations["4L"]["rose_result"] == "Adequate lymphocytes"
    assert stations["7"]["size_mm"] == 6.2
    assert stations["7"]["passes"] == 5
    assert stations["7"]["rose_result"] == "Adequate lymphocytes"
    assert stations["4R"]["size_mm"] == 8.2
    assert stations["4R"]["passes"] == 5
    assert stations["4R"]["rose_result"] == "Malignant"

    tbna_proc = next(proc for proc in bundle.procedures if proc.proc_type == "transbronchial_needle_aspiration")
    tbna_data = tbna_proc.data.model_dump(exclude_none=False) if hasattr(tbna_proc.data, "model_dump") else tbna_proc.data
    assert tbna_data["samples_collected"] == 5

    cryo_proc = next(proc for proc in bundle.procedures if proc.proc_type == "transbronchial_cryobiopsy")
    cryo_data = cryo_proc.data.model_dump(exclude_none=False) if hasattr(cryo_proc.data, "model_dump") else cryo_proc.data
    assert cryo_data["num_samples"] == 3
    assert cryo_data["cryoprobe_size_mm"] == 1.1


def test_biopsy_evidence_gating_prevents_phantom_transbronchial_biopsy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REPORTER_EVIDENCE_GATING", "1")
    extraction = {
        "source_text": "Robotic bronchoscopy with lavage and brushings only. No additional tissue procedure documented.",
        "bronch_num_tbbx": 4,
        "bronch_location_lobe": "RUL",
        "bronch_guidance": "Fluoroscopy",
        "bronch_tbbx_tool": "Forceps",
        "procedures": [
            {
                "proc_type": "bronchoscopy_core",
                "schema_id": "bronchoscopy_shell_v1",
                "proc_id": "bronchoscopy_core_1",
                "data": {
                    "airway_overview": "Survey completed.",
                    "right_lung_overview": "Patent.",
                    "left_lung_overview": "Patent.",
                },
            }
        ],
    }

    bundle = build_procedure_bundle_from_extraction(extraction)
    assert not any(proc.proc_type == "transbronchial_biopsy" for proc in bundle.procedures)
    note = compose_structured_report(bundle)
    assert "Transbronchial biopsy" not in note


def test_planned_not_performed_cpt_is_surfaced() -> None:
    extraction = {
        "source_text": "Procedure summary: bronchoscopy completed. 32555 planned not done mod73 due to inadequate fluid pocket.",
        "procedures": [
            {
                "proc_type": "bronchoscopy_core",
                "schema_id": "bronchoscopy_shell_v1",
                "proc_id": "bronchoscopy_core_1",
                "data": {
                    "airway_overview": "Survey completed.",
                    "right_lung_overview": "Patent.",
                    "left_lung_overview": "Patent.",
                },
            }
        ],
    }

    note = compose_structured_report_from_extraction(extraction)
    assert "Thoracentesis (CPT 32555) was planned but not performed." in note
