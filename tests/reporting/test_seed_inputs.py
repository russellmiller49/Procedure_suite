"""Structured seed inputs: enumerated selections applied to the seeded bundle."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.reporting import build_procedure_bundle_from_extraction, compose_structured_report
from app.reporting.seed_inputs import (
    _FIELDS,
    ReporterSeedInputs,
    _annotation,
    apply_seed_inputs,
    build_seed_input_spec,
)
from ops.tools.eval_reporter_robotic_minimal import check_order, observed_order

PROMPT = (
    "Ion robotic bronch for 1 cm LUL apicoposterior nodule, eccentric radial EBUS, "
    "low-dose Cios spin and retargeting. 21G TBNA x6, forceps x2, 1.1 cryo x8, brush, BAL, "
    "fiducial. ROSE no malignancy; EBUS 11Ri/7/11L four passes each. No complications."
)
SURVEY_PROMPT = "Ion RLL RB10 nodule cryo x5. EBUS survey of 4R, 7 and 11L without nodal sampling."


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    for key, value in {
        "PROCSUITE_SKIP_DOTENV": "1",
        "REPORTER_DISABLE_LLM": "1",
        "OPENAI_OFFLINE": "1",
        "GEMINI_OFFLINE": "1",
        "ENABLE_UMLS_LINKER": "false",
    }.items():
        monkeypatch.setenv(key, value)


def seed(text: str = PROMPT):
    return build_procedure_bundle_from_extraction({}, source_text=text)


def apply(payload: dict, text: str = PROMPT):
    return apply_seed_inputs(seed(text), ReporterSeedInputs.model_validate(payload))


def proc(bundle, kind: str) -> dict:
    return next(p.data for p in bundle.procedures if p.proc_type == kind)


def test_empty_inputs_leave_the_bundle_untouched():
    bundle = seed()
    assert apply_seed_inputs(bundle, None).bundle is bundle
    assert apply_seed_inputs(bundle, ReporterSeedInputs()).bundle is bundle


def test_uniform_elastography_reaches_every_station_and_the_note():
    result = apply(
        {
            "ebus": {
                "elastography": {
                    "used": True,
                    "scope": "All sampled/inspected nodes",
                    "uniform_pattern": "Type 1",
                }
            }
        }
    )
    ebus = proc(result.bundle, "ebus_tbna")
    assert ebus["elastography_used"] is True
    assert ebus["elastography_pattern"] == "Type 1"
    assert [s["elastography_pattern"] for s in ebus["stations"]] == ["Type 1"] * 3
    rendered = compose_structured_report(result.bundle, strict=True)
    assert "All sampled nodes demonstrated a Type 1 elastographic pattern" in rendered
    assert not result.warnings


def test_specific_station_types_are_bound_to_those_stations_only():
    result = apply(
        {
            "ebus": {
                "elastography": {
                    "used": True,
                    "scope": "Specific nodes",
                    "stations_type_2": ["11Ri", "7"],
                    "stations_type_3": ["11L"],
                }
            }
        }
    )
    ebus = proc(result.bundle, "ebus_tbna")
    assert {s["station_name"]: s["elastography_pattern"] for s in ebus["stations"]} == {
        "11RI": "Type 2",
        "7": "Type 2",
        "11L": "Type 3",
    }
    assert ebus["elastography_pattern"] is None  # mixed: no record-level claim
    rendered = compose_structured_report(result.bundle, strict=True)
    assert "Station 11L. Type 3 elastographic pattern" in rendered
    assert "All sampled nodes demonstrated" not in rendered


def test_station_not_in_dictation_is_never_added_as_sampled():
    result = apply(
        {
            "ebus": {
                "elastography": {"used": True, "scope": "Specific nodes", "stations_type_1": ["4L"]}
            }
        }
    )
    ebus = proc(result.bundle, "ebus_tbna")
    assert [s["station_name"] for s in ebus["stations"]] == ["11RI", "7", "11L"]
    assert "4L Type 1" in result.bundle.findings_text
    assert any("4L Type 1" in warning for warning in result.warnings)


def test_elastography_without_any_ebus_block_does_not_create_sampling():
    result = apply(
        {"ebus": {"needle_gauges": ["22G"], "elastography": {"used": True}}},
        text="Ion LUL nodule cryo x4.",
    )
    assert not any(p.proc_type.startswith("ebus") for p in result.bundle.procedures)
    assert "EBUS elastography was performed" in result.bundle.findings_text
    assert len(result.warnings) == 2


def test_elastography_applies_to_a_survey_only_block():
    result = apply(
        {
            "ebus": {
                "elastography": {
                    "used": True,
                    "scope": "All sampled/inspected nodes",
                    "uniform_pattern": "Type 1",
                }
            }
        },
        text=SURVEY_PROMPT,
    )
    assert not any(p.proc_type == "ebus_tbna" for p in result.bundle.procedures)
    survey = proc(result.bundle, "ebus_survey")
    assert all(
        s["elastography_pattern"] == "Type 1" and s["sampled"] is False for s in survey["stations"]
    )
    rendered = compose_structured_report(result.bundle, strict=True)
    assert "All inspected nodes demonstrated a Type 1 elastographic pattern" in rendered
    assert "No lymph nodes were sampled." in rendered


def test_not_used_clears_extracted_patterns_with_a_warning():
    text = "Ion LUL nodule cryo x4. EBUS 7 x4, 4R x4, elastography type 2."
    result = apply({"ebus": {"elastography": {"used": False}}}, text=text)
    ebus = proc(result.bundle, "ebus_tbna")
    assert ebus["elastography_used"] is False
    assert not any(s.get("elastography_pattern") for s in ebus["stations"])
    assert result.warnings
    assert "elastograph" not in compose_structured_report(result.bundle, strict=True).lower()


def test_specified_value_overrides_extraction_and_unspecified_does_not():
    bundle = seed()
    before = proc(bundle, "robotic_navigation")
    result = apply({"navigation": {"platform": "Monarch"}})
    nav = proc(result.bundle, "robotic_navigation")
    assert before["platform"] == "Ion" and nav["platform"] == "Monarch"
    assert any("replaced 'Ion'" in note for note in result.applied)
    assert nav.get("registration_method") is None


def test_no_removes_extracted_procedures_and_warns():
    result = apply({"navigation": {"cbct_used": False, "fiducial": {"placed": False}}})
    kinds = {p.proc_type for p in result.bundle.procedures}
    assert "cbct_cact_fusion" not in kinds and "fiducial_marker_placement" not in kinds
    assert len(result.warnings) == 2


def test_closing_airway_and_navigation_details_render():
    result = apply(
        {
            "airway": {
                "anesthesia": "General anesthesia via endotracheal tube",
                "airway_exam_normal": True,
                "therapeutic_aspiration": True,
            },
            "navigation": {
                "registration": "Partial",
                "tool_in_lesion_confirmed": True,
                "cbct_attestation": True,
                "fiducial": {
                    "placed": True,
                    "marker_type": "Gold fiducial",
                    "count": 1,
                    "confirmation": "fluoroscopy",
                },
            },
            "ebus": {
                "needle_gauges": ["22G", "25G"],
                "technique": "All stations assessed; nodes 5 mm or larger sampled",
                "rose_available": False,
            },
            "closing": {
                "ebl": "Minimal",
                "complications_none": True,
                "disposition": (
                    "Extubated in the operating room and transported to the recovery room "
                    "in stable condition"
                ),
                "plan_items": ["CXR in PACU", "IP clinic follow-up in 1-2 weeks"],
            },
        }
    )
    rendered = compose_structured_report(result.bundle, strict=True)
    for expected in [
        "ANESTHESIA: General anesthesia via endotracheal tube",
        "was normal.",
        "Successful therapeutic aspiration was performed",
        "Partial registration was used.",
        "Tool-in-lesion was confirmed with cone-beam CT.",
        "I personally performed and interpreted the CT guidance images",
        "(Gold fiducial x1) was placed at the LUL target under fluoroscopy guidance.",
        "using 22G, 25G needles",
        "Only those 5 mm or greater in short axis were sampled.",
        "Overall EBUS TBNA ROSE Diagnosis: Not performed.",
        "ESTIMATED BLOOD LOSS: Minimal",
        "COMPLICATIONS: None",
        "the patient was extubated in the operating room",
        "- CXR in PACU",
        "- IP clinic follow-up in 1-2 weeks",
    ]:
        assert expected in rendered, expected
    # Added steps fall into the dictated workflow, not at the end.
    assert not check_order(rendered)
    blocks = observed_order(rendered)["detail_blocks"]
    assert blocks.index("tool_in_lesion_confirmation") == blocks.index("cbct_cact_fusion") + 1


def test_ebus_first_sequence_moves_the_nodal_block_ahead():
    result = apply({"sequence": "EBUS first, then peripheral target"})
    blocks = observed_order(compose_structured_report(result.bundle, strict=True))
    assert blocks["detail_blocks"][0] == "ebus_tbna"
    assert blocks["header_lines"][0] == "ebus_tbna"
    assert blocks["detail_blocks"][1:4] == [
        "robotic_navigation",
        "radial_ebus_survey",
        "cbct_cact_fusion",
    ]


def test_apply_is_pure_and_idempotent():
    inputs = ReporterSeedInputs.model_validate(
        {
            "sequence": "Peripheral target first, then EBUS",
            "airway": {"therapeutic_aspiration": True, "airway_exam_normal": True},
            "navigation": {"tool_in_lesion_confirmed": True, "cbct_attestation": True},
            "ebus": {
                "elastography": {
                    "used": True,
                    "scope": "Specific nodes",
                    "stations_type_1": ["7", "4L"],
                }
            },
            "closing": {"plan_items": ["CXR in PACU"], "complications_none": True},
        }
    )
    bundle = seed()
    snapshot = bundle.model_dump()
    once = apply_seed_inputs(bundle, inputs).bundle
    assert bundle.model_dump() == snapshot
    assert apply_seed_inputs(once, inputs).bundle.model_dump() == once.model_dump()


@pytest.mark.parametrize(
    "payload",
    [
        {"ebus": {"elastogrphy": {"used": True}}},
        {"ebus": {"elastography": {"scope": "Specific nodes", "stations_type_1": ["7"]}}},
        {
            "ebus": {
                "elastography": {"used": True, "stations_type_1": ["7"], "stations_type_2": ["7"]}
            }
        },
        {"ebus": {"elastography": {"used": True, "uniform_pattern": "Type 4"}}},
        {"navigation": {"fiducial": {"marker_type": "Gold fiducial"}}},
        {"navigation": {"cbct_used": False, "cbct_attestation": True}},
        {"closing": {"plan_items": ["free text is not allowed"]}},
    ],
)
def test_invalid_or_free_text_inputs_are_rejected(payload):
    with pytest.raises(ValidationError):
        ReporterSeedInputs.model_validate(payload)


def test_spec_is_derived_from_the_model():
    spec = build_seed_input_spec()
    pointers = [f.pointer for f in spec.fields]
    assert len(pointers) == len(set(pointers)) == len(_FIELDS)
    for f in spec.fields:
        _annotation(f.pointer)  # every pointer resolves to a model field
        assert f.input_type.value in {"boolean", "enum", "multiselect", "integer"}
        if f.input_type.value in {"enum", "multiselect"}:
            assert f.options
        for dep in f.depends_on:
            assert dep.pointer in pointers

    # Every leaf of the request model is offered as a dropdown.
    def leaves(model, prefix=""):
        for name, info in model.model_fields.items():
            if name == "version":
                continue
            nested = [
                a
                for a in getattr(info.annotation, "__args__", ())
                if isinstance(a, type) and hasattr(a, "model_fields")
            ]
            if nested:
                yield from leaves(nested[0], f"{prefix}/{name}")
            else:
                yield f"{prefix}/{name}"

    assert sorted(leaves(ReporterSeedInputs)) == sorted(pointers)
