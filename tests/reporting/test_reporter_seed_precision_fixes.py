from app.reporting import (
    EncounterInfo,
    PatientInfo,
    ProcedureBundle,
    ProcedureInput,
    build_procedure_bundle_from_extraction,
    compose_structured_report,
)
from app.reporting.normalization.compat_enricher import _add_compat_flat_fields
from app.reporting.quality_gate import (
    _complication_contradiction_flags,
    build_reporter_quality_flags,
)

_THORACENTESIS_NOTE = (
    "Left thoracentesis performed under ultrasound guidance at the 7th intercostal "
    "space along the mid-axillary line. A total of 900 mL of serous fluid was removed. "
    "A post-procedure chest x-ray was ordered."
)


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


def _minimal_bundle(complications_text: str = "None") -> ProcedureBundle:
    return ProcedureBundle(
        patient=PatientInfo(name="Precision Test"),
        encounter=EncounterInfo(date="2026-03-01", attending="Dr. Precision"),
        procedures=[_minimal_bronch_core()],
        complications_text=complications_text,
    )


def _injection_notes(extraction: dict) -> str:
    bundle = build_procedure_bundle_from_extraction(extraction)
    proc = next(p for p in bundle.procedures if p.proc_type == "therapeutic_injection")
    data = proc.data.model_dump(exclude_none=False) if hasattr(proc.data, "model_dump") else dict(proc.data or {})
    return str(data.get("notes") or "")


def test_status_only_tracheostomy_does_not_fabricate_delivery_route() -> None:
    extraction = {
        "source_text": (
            "Patient: 45 F\n"
            "Indication: Aspergilloma\n"
            "Airway: Tracheostomy\n"
            "Procedure: Injection of Voriconazole (50mg)\n"
            "Target: Left Lower Lobe (LLL)\n"
            "Findings: thick tan secretions"
        ),
    }

    assert "tracheostomy" not in _injection_notes(extraction).lower()
    bundle = build_procedure_bundle_from_extraction(extraction)
    note = compose_structured_report(bundle)
    assert "via tracheostomy" not in note.lower()


def test_explicit_via_tracheostomy_delivery_keeps_route_note() -> None:
    extraction = {
        "source_text": (
            "Indication: Aspergilloma. Voriconazole (50mg) injection was performed "
            "via the tracheostomy into the left lower lobe."
        ),
    }

    assert _injection_notes(extraction) == "Delivered via tracheostomy."


def test_routine_fluid_removal_does_not_contradict_complications_none() -> None:
    for source in (
        _THORACENTESIS_NOTE,
        "Removed 900 mL of serous fluid without difficulty.",
    ):
        flags = _complication_contradiction_flags(
            source,
            _minimal_bundle(),
            "COMPLICATIONS None",
        )
        assert flags == []


def test_negated_required_does_not_contradict_complications_none() -> None:
    flags = _complication_contradiction_flags(
        "Diagnostic bronchoscopy completed. No further intervention was required.",
        _minimal_bundle(),
        "COMPLICATIONS None",
    )
    assert flags == []


def test_device_removal_still_contradicts_complications_none() -> None:
    flags = _complication_contradiction_flags(
        "The chest tube was removed emergently due to malposition.",
        _minimal_bundle(),
        "COMPLICATIONS None",
    )
    assert [flag["code"] for flag in flags] == ["COMPLICATIONS_NONE_CONTRADICTION"]


def test_affirmative_required_still_contradicts_complications_none() -> None:
    flags = _complication_contradiction_flags(
        "Desaturation occurred and the patient required emergent intubation.",
        _minimal_bundle(),
        "COMPLICATIONS None",
    )
    assert [flag["code"] for flag in flags] == ["COMPLICATIONS_NONE_CONTRADICTION"]


def test_thoracentesis_report_has_no_blocking_complication_flag() -> None:
    flags, _needs_review = build_reporter_quality_flags(
        source_text=_THORACENTESIS_NOTE,
        bundle=_minimal_bundle(),
        markdown="COMPLICATIONS None",
    )
    assert "COMPLICATIONS_NONE_CONTRADICTION" not in {flag["code"] for flag in flags}


def test_pleural_fluid_appearance_extracts_serous_from_ml_of_form() -> None:
    raw = {
        "procedures_performed": {},
        "pleural_procedures": {"thoracentesis": {"performed": True}},
        "source_text": _THORACENTESIS_NOTE,
    }
    _add_compat_flat_fields(raw)
    assert raw["pleural_fluid_appearance"] == "serous"


def test_pleural_fluid_appearance_verb_forms_do_not_swallow_of_or_aux() -> None:
    for source, expected in (
        ("Drained 1.2 L of cloudy amber fluid.", "cloudy amber"),
        ("500 mL straw-colored fluid was drained.", "straw-colored"),
    ):
        raw = {
            "procedures_performed": {},
            "pleural_procedures": {"thoracentesis": {"performed": True}},
            "source_text": source,
        }
        _add_compat_flat_fields(raw)
        assert raw["pleural_fluid_appearance"] == expected


def test_intercostal_space_parses_explicit_ordinal() -> None:
    raw = {
        "procedures_performed": {},
        "pleural_procedures": {"thoracentesis": {"performed": True}},
        "source_text": _THORACENTESIS_NOTE,
    }
    _add_compat_flat_fields(raw)
    assert raw["pleural_intercostal_space"] == "7th"


def test_intercostal_space_defaults_to_unspecified_when_absent() -> None:
    raw = {
        "procedures_performed": {},
        "pleural_procedures": {"thoracentesis": {"performed": True}},
        "source_text": "Left thoracentesis performed under ultrasound guidance. 900 mL of serous fluid was removed.",
    }
    _add_compat_flat_fields(raw)
    assert raw["pleural_intercostal_space"] == "unspecified"
