from __future__ import annotations

import pytest

from modules.api.services.qa_pipeline import (
    ReporterStrategyError,
    ReportingStrategy,
    SimpleReporterStrategy,
)
from modules.reporting.metadata import MissingFieldIssue
from modules.reporting.engine import build_procedure_bundle_from_extraction


def _strategy_for_serialization_tests() -> ReportingStrategy:
    return ReportingStrategy(
        reporter_engine=object(),
        inference_engine=object(),
        validation_engine=object(),
        registry_engine=object(),
        simple_strategy=SimpleReporterStrategy(),
    )


def test_issue_serialization_supports_missing_field_issue_dataclass() -> None:
    strategy = _strategy_for_serialization_tests()
    issues = [
        MissingFieldIssue(
            proc_id="p1",
            proc_type="ebus_tbna",
            template_id="ebus_tbna_v1",
            field_path="stations[0].passes",
            severity="warning",
            message="Passes not documented",
        )
    ]

    serialized = strategy._serialize_issues(issues)

    assert len(serialized) == 1
    assert serialized[0]["proc_id"] == "p1"
    assert serialized[0]["template_id"] == "ebus_tbna_v1"
    assert serialized[0]["field_path"] == "stations[0].passes"


def test_issue_serialization_raises_explicit_reporter_error_code() -> None:
    class _UnsupportedIssue:
        pass

    strategy = _strategy_for_serialization_tests()

    with pytest.raises(ReporterStrategyError) as exc_info:
        strategy._serialize_issues([_UnsupportedIssue()])

    assert exc_info.value.error_code == "REPORTER_ISSUE_SERIALIZATION_ERROR"


def test_bundle_mapping_synthesizes_core_text_fields() -> None:
    extraction = {
        "clinical_context": {
            "primary_indication": "Peripheral right upper lobe nodule for staging",
            "lesion_location": "RUL",
            "lesion_size_mm": 22,
        },
        "diagnosis": "Lung nodule",
        "post_procedure_diagnosis": "Lung nodule sampled",
        "complications": ["none"],
        "specimens": ["TBNA station 4R", "TBNA station 7"],
        "follow_up_plan": ["Review cytology and follow in clinic"],
    }

    bundle = build_procedure_bundle_from_extraction(extraction)

    assert bundle.indication_text == "Peripheral right upper lobe nodule for staging"
    assert bundle.preop_diagnosis_text == "Lung nodule"
    assert bundle.postop_diagnosis_text == "Lung nodule sampled"
    assert bundle.complications_text == "None"
    assert "TBNA station 4R" in (bundle.specimens_text or "")
    assert bundle.impression_plan == "Review cytology and follow in clinic"


def test_bundle_mapping_adds_bridge_procedures_and_thoracentesis_alias() -> None:
    extraction = {
        "primary_indication": "Pulmonary lesion sampling",
        "linear_ebus_stations": ["4R", "7"],
        "ebus_needle_gauge": "19G",
        "procedures": [
            {
                "proc_type": "thoracentesis_detailed",
                "schema_id": "thoracentesis_detailed_v1",
                "proc_id": "thora_detailed_1",
                "data": {
                    "side": "left",
                    "intercostal_space": "7th",
                    "entry_location": "posterior axillary",
                    "volume_removed_ml": 900,
                    "fluid_appearance": "serous",
                    "effusion_volume": "moderate",
                    "effusion_echogenicity": "anechoic",
                    "specimen_tests": ["protein", "LDH"],
                },
            }
        ],
        "procedures_performed": {
            "linear_ebus": {
                "performed": True,
                "stations_sampled": ["4R", "7"],
                "needle_gauge": "19G",
                "needle_type": "forceps-compatible",
            },
            "eus_b": {
                "performed": True,
                "stations_sampled": ["7", "8"],
                "needle_gauge": "22G",
                "passes": 3,
            },
            "navigational_bronchoscopy": {
                "performed": True,
                "divergence_mm": 4.5,
            },
        },
        "granular_data": {
            "navigation_targets": [
                {
                    "target_lobe": "RUL",
                    "target_segment": "RB1",
                    "fiducial_marker_placed": True,
                    "fiducial_marker_details": "Fiducial marker deployed at RB1 target.",
                }
            ]
        },
        "ion_registration_partial": {
            "indication": "Partial registration for efficiency strategy",
            "scope_of_registration": "segmental bronchi only",
        },
        "ion_registration_drift": {
            "cause": "airway deformation",
            "mitigation": "repeat landmark registration",
        },
        "cbct_augmented_bronchoscopy": {
            "ventilation_settings": "VC mode with inspiratory hold",
            "adjustment_description": "2 mm posterior correction",
        },
        "dye_marker_placement": {
            "guidance_method": "fluoroscopy",
            "needle_gauge": "21G",
            "dye_type": "methylene blue",
            "volume_ml": 0.7,
        },
        "blvr_valve_removal_exchange": {
            "indication": "Valve repositioning for persistent leak",
            "locations": ["RUL", "RML"],
            "valves_removed": 2,
            "valves_exchanged": 1,
        },
    }

    bundle = build_procedure_bundle_from_extraction(extraction)
    proc_types = {proc.proc_type for proc in bundle.procedures}

    expected = {
        "thoracentesis",
        "fiducial_marker_placement",
        "ebus_ifb",
        "ebus_19g_fnb",
        "ion_registration_partial",
        "ion_registration_drift",
        "cbct_augmented_bronchoscopy",
        "dye_marker_placement",
        "eusb",
        "blvr_valve_removal_exchange",
    }
    missing = expected - proc_types
    assert not missing, f"Expected bridge proc types missing: {sorted(missing)}"
