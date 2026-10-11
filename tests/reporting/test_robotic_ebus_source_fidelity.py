"""Source-reviewed regressions from the user-supplied deidentified operative reports."""

from pathlib import Path

import pytest

from app.reporting import build_procedure_bundle_from_extraction, compose_structured_report
from app.reporting.engine import _extract_planned_not_performed_lines
from app.reporting.normalization.robotic_ebus_fidelity import reconcile_operative_blocks

FIXTURES = Path(__file__).parents[1] / "fixtures" / "reporting" / "robotic_ebus"


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


def seed(case):
    text = (FIXTURES / f"case_{case:02}.txt").read_text()
    return build_procedure_bundle_from_extraction({}, source_text=text)


def data(bundle, kind):
    return [
        p.data.model_dump() if hasattr(p.data, "model_dump") else p.data
        for p in bundle.procedures
        if p.proc_type == kind
    ]


@pytest.mark.parametrize(
    "case,tbna,cryo",
    [
        (1, [6], [8]),
        (2, [3, 3], [6, 6]),
        (3, [6], [5, 6]),
        (4, [7], [5]),
        (5, [6], [6]),
        (6, [7], [6]),
        (7, [7], [6]),
        (8, [5], [6]),
        (9, [5], [6]),
        (10, [6], [6]),
        (11, [3], [7]),
    ],
)
def test_source_counts_stay_with_sampling_modality(case, tbna, cryo):
    bundle = seed(case)
    assert [
        p["samples_collected"] for p in data(bundle, "transbronchial_needle_aspiration")
    ] == tbna
    assert [p["num_samples"] for p in data(bundle, "transbronchial_cryobiopsy")] == cryo
    assert not data(bundle, "transbronchial_biopsy")
    assert len(data(bundle, "transbronchial_lung_biopsy")) == (1 if case == 1 else 0)
    markdown = compose_structured_report(bundle)
    assert "31629 passes" not in markdown
    assert "Procedure was planned but not performed" not in markdown
    assert "absence of significant vessels" not in markdown
    assert "POSTOPERATIVE" not in bundle.preop_diagnosis_text
    assert "PROCEDURE IN DETAIL" not in (bundle.complications_text or "")
    assert "SPECIMEN(S)" not in (bundle.complications_text or "")
    assert "Histology" not in (bundle.specimens_text or "")  # retain source inventory


def test_two_targets_keep_different_rose_and_radial_patterns():
    bundle = seed(2)
    nav = data(bundle, "robotic_navigation")
    assert [n["lesion_location"] for n in nav] == [
        "Posterior Segment of RUL (RB2)",
        "Superior Segment of Lingula (LB4)",
    ]
    assert "Atypical cells present but no evidence of malignant neoplasm" in nav[0]["notes"]
    assert "Conclusive evidence of malignant neoplasm" in nav[1]["notes"]
    assert [n["rebus_features"] for n in data(bundle, "radial_ebus_survey")] == [
        "Eccentric",
        "Concentric",
    ]
    assert [n["registration_method"] for n in nav] == ["Partial", "Partial"]
    assert [n["instilled_volume_cc"] for n in data(bundle, "bal")] == [20, 20]


def test_two_targets_in_same_segment_do_not_clone_needle_sampling():
    bundle = seed(3)
    nav = data(bundle, "robotic_navigation")
    assert len(nav) == 2
    assert nav[0]["lesion_location"] == nav[1]["lesion_location"]
    assert "0.5 cm" in nav[0]["notes"] and "1.0 cm" in nav[1]["notes"]
    assert len(data(bundle, "transbronchial_needle_aspiration")) == 1
    for cryo in data(bundle, "transbronchial_cryobiopsy"):
        assert cryo["freeze_seconds"] is None
        assert cryo["notes"] == "Freeze time: 4-6 seconds"


def test_inspected_only_nodes_are_not_rendered_as_tbna():
    bundle = seed(8)
    assert not data(bundle, "ebus_tbna")
    for station in ["11L", "4L", "7", "4R", "11RS", "11RI"]:
        assert f"Station {station}: not sampled" in bundle.findings_text
    markdown = compose_structured_report(bundle)
    assert "EBUS-TBNA Staging" not in markdown
    assert "Linear EBUS survey" in markdown


def test_node_rose_not_performed_is_separate_from_target_rose():
    bundle = seed(11)
    ebus = data(bundle, "ebus_tbna")[0]
    assert ebus["rose_available"] is False
    assert ebus["overall_rose_diagnosis"] == "Not performed"
    assert [s["station_name"] for s in ebus["stations"]] == ["11RI", "11RS", "7", "11L"]
    assert [s["passes"] for s in ebus["stations"]] == [4, 4, 4, 4]
    for station in ebus["stations"]:
        assert station.get("size_mm") is None
        assert station["comments"] == "< 10 mm on CT"
        assert station["rose_result"] == "not performed and without preliminary results"
    assert data(bundle, "radial_ebus_survey")[0]["rebus_features"] == "not identifiable"
    assert data(bundle, "bal")[0]["instilled_volume_cc"] == 70
    assert data(bundle, "bal")[0]["returned_volume_cc"] == 15
    markdown = compose_structured_report(bundle)
    assert "Atypical cells present but no evidence of malignant neoplasm" in markdown
    assert "Not performed" in markdown


def test_node_specific_counts_and_elastography():
    ebus = data(seed(10), "ebus_tbna")[0]
    assert [(s["station_name"], s["passes"]) for s in ebus["stations"]] == [("11L", 4), ("7", 6)]
    assert all(s["echo_features"] == "Elastography Type 2" for s in ebus["stations"])


def test_unrecognized_source_does_not_replace_existing_bundle():
    bundle = seed(1)
    assert (
        reconcile_operative_blocks(bundle, "Robotic bronchoscopy planned for next week.") is bundle
    )


def test_procedure_abortion_still_survives():
    assert _extract_planned_not_performed_lines("Bronchoscopy aborted due to instability.") == [
        "Bronchoscopy was planned but not performed."
    ]
    assert (
        _extract_planned_not_performed_lines("Overall EBUS TBNA ROSE Diagnosis: Not performed")
        == []
    )


@pytest.mark.parametrize("case", range(1, 12))
def test_operative_quality_checks_ignore_headers_and_negated_events(case):
    from app.reporting.quality_gate import build_reporter_quality_flags

    bundle = seed(case)
    text = (FIXTURES / f"case_{case:02}.txt").read_text()
    flags, _ = build_reporter_quality_flags(
        source_text=text, bundle=bundle, markdown=compose_structured_report(bundle)
    )
    assert not [
        f
        for f in flags
        if f["code"]
        in {
            "COMPLICATIONS_NONE_CONTRADICTION",
            "EXPLICIT_CPT_SHORTHAND_MISMATCH",
            "OMITTED_MAJOR_PROCEDURE_FAMILY",
            "MULTI_TARGET_COLLAPSE",
        }
    ]


def test_actual_bleeding_in_narrative_overrides_none():
    from app.reporting.quality_gate import _complication_contradiction_flags

    bundle = seed(1)
    bundle.complications_text = "None"
    note = "PROCEDURE IN DETAIL:\nSignificant bleeding required balloon tamponade."
    assert _complication_contradiction_flags(note, bundle, "COMPLICATIONS None")
    parsed = build_procedure_bundle_from_extraction({}, source_text=note)
    assert "bleeding" in parsed.complications_text.lower()


def test_explicit_therapeutic_cpt_shorthand_still_requires_procedure():
    from app.reporting.quality_gate import _explicit_cpt_shorthand_flags

    assert _explicit_cpt_shorthand_flags("31641 tumor destruction", seed(2), "")


def test_routine_scope_withdrawal_is_not_complication_but_emergency_remains_flagged():
    from app.reporting.quality_gate import _complication_contradiction_flags

    bundle = seed(1)
    bundle.complications_text = "None"
    assert not _complication_contradiction_flags("The bronchoscope was removed.", bundle, "")
    assert _complication_contradiction_flags(
        "The bronchoscope was removed emergently due to instability.", bundle, ""
    )


def test_aborted_procedure_with_rose_in_same_sentence_is_not_hidden():
    assert _extract_planned_not_performed_lines("ROSE showed atypia and bronchoscopy aborted.")


def test_real_registry_seed_path_preserves_source_blocks(monkeypatch):
    from app.registry.application.registry_service import RegistryService
    from app.reporting.seed_pipeline import (
        run_reporter_seed_pipeline,
        seed_outcome_from_registry_result,
    )

    for key, value in {
        "PROCSUITE_SKIP_WARMUP": "1",
        "PROCSUITE_PIPELINE_MODE": "extraction_first",
        "REGISTRY_EXTRACTION_ENGINE": "parallel_ner",
        "REGISTRY_SCHEMA_VERSION": "v3",
        "REGISTRY_USE_STUB_LLM": "1",
        "REGISTRY_SELF_CORRECT_ENABLED": "0",
        "REGISTRY_LLM_FALLBACK_ON_COVERAGE_FAIL": "0",
        "REGISTRY_AUDITOR_SOURCE": "disabled",
    }.items():
        monkeypatch.setenv(key, value)
    service = RegistryService()
    for case, tbna, cryo in [
        (1, [6], [8]),
        (2, [3, 3], [6, 6]),
        (3, [6], [5, 6]),
        (4, [7], [5]),
        (5, [6], [6]),
        (6, [7], [6]),
        (7, [7], [6]),
        (8, [5], [6]),
        (9, [5], [6]),
        (10, [6], [6]),
        (11, [3], [7]),
    ]:
        text = (FIXTURES / f"case_{case:02}.txt").read_text()
        pipeline = run_reporter_seed_pipeline(
            seed_outcome_from_registry_result(service.extract_fields(text), masked_seed_text=text),
            note_text=text,
            strict=True,
            debug_enabled=False,
        )
        assert [
            p["samples_collected"]
            for p in data(pipeline.bundle, "transbronchial_needle_aspiration")
        ] == tbna, case
        assert [
            p["num_samples"] for p in data(pipeline.bundle, "transbronchial_cryobiopsy")
        ] == cryo, case
        # Deidentification placeholders remain review blockers; clinical facts
        # and source-aware quality checks should not add false blockers.
        assert {f["code"] for f in pipeline.quality_flags if f["severity"] == "blocker"} <= {
            "UNRESOLVED_PLACEHOLDER"
        }, case
        if pipeline.render_fallback_used:
            assert pipeline.render_fallback_reason == "style_disallowed_placeholder", case


def test_plan_preserved_and_undocumented_technique_not_added():
    bundle = seed(2)
    assert "f/u CXR" in bundle.impression_plan
    markdown = compose_structured_report(bundle)
    assert "withdrawn en bloc" not in markdown
    assert "Post-procedure assessment for pneumothorax was performed" not in markdown
