from __future__ import annotations

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.deterministic_extractors import (
    extract_endobronchial_biopsy,
)
from app.registry.schema.granular_models import EBUSStationDetail
from app.registry.postprocess import reconcile_ebus_sampling_from_narrative
from app.registry.postprocess.complications_reconcile import reconcile_complications_from_narrative
from app.registry.processing.linear_ebus_stations_detail import extract_linear_ebus_stations_detail
from app.registry.schema import RegistryRecord


def test_extract_linear_ebus_stations_detail_parses_bare_station_lines() -> None:
    note_text = """
    PROCEDURES: Bronchoscopy; Linear EBUS-TBNA
    FINDINGS:
    No endobronchial lesion.

    TBNA:
    7: 6 passes (22G)
    4L: 4 passes (22G)
    11L: 3 passes (22G)
    """

    details = extract_linear_ebus_stations_detail(note_text)
    by_station = {row["station"]: row for row in details}

    assert by_station["7"]["sampled"] is True
    assert by_station["7"]["number_of_passes"] == 6
    assert by_station["7"]["needle_gauge"] == 22

    assert by_station["4L"]["sampled"] is True
    assert by_station["4L"]["number_of_passes"] == 4

    assert by_station["11L"]["sampled"] is True
    assert by_station["11L"]["number_of_passes"] == 3


def test_extract_linear_ebus_stations_detail_ignores_total_passes_across_stations() -> None:
    note_text = """
    EBUS-TBNA:
    Station 2R: 3 passes.
    Station 4R: 4 passes.
    Station 4L: 3 passes.
    Station 7: 4 passes.
    Total TBNA passes: 14 passes across 4 stations.
    """

    details = extract_linear_ebus_stations_detail(note_text)
    by_station = {row["station"]: row for row in details}

    assert by_station["2R"]["number_of_passes"] == 3
    assert by_station["4R"]["number_of_passes"] == 4
    assert by_station["4L"]["number_of_passes"] == 3
    assert by_station["7"]["number_of_passes"] == 4


def test_extract_linear_ebus_stations_detail_sums_composite_pass_expression() -> None:
    note_text = """
    EBUS-TBNA:
    10L: x2+2 passes (21G)
    """

    details = extract_linear_ebus_stations_detail(note_text)
    by_station = {row["station"]: row for row in details}

    assert by_station["10L"]["number_of_passes"] == 4


def test_ebus_station_detail_clamps_out_of_range_pass_count() -> None:
    detail = EBUSStationDetail.model_validate({"station": "4R", "number_of_passes": 14})
    assert detail.number_of_passes == 10


def test_reconcile_ebus_sampling_uses_record_consistency_to_upgrade_node_events() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "stations_sampled": ["4L"],
                    "node_events": [
                        {
                            "station": "4L",
                            "action": "inspected_only",
                            "outcome": None,
                            "evidence_quote": "4L measured 1.1 cm.",
                        }
                    ],
                }
            },
            "granular_data": {
                "linear_ebus_stations_detail": [
                    {"station": "4L", "sampled": True, "number_of_passes": 3}
                ]
            },
        }
    )

    warnings = reconcile_ebus_sampling_from_narrative(
        record,
        "IMPRESSION: Uncomplicated EBUS-TBNA of station 4L.\nSPECIMENS: Station 4L FNA.\n",
    )

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    assert linear is not None
    assert linear.node_events is not None
    assert linear.node_events[0].action == "needle_aspiration"
    assert linear.node_events[0].passes == 3
    assert any("EBUS_NARRATIVE_RECONCILE" in str(w) for w in warnings)


def test_clinical_guardrails_clear_negated_endobronchial_lesion_text() -> None:
    note_text = (
        "Flexible bronchoscopy showed normal airway inspection. No endobronchial lesion. "
        "Copious secretions were suctioned from the right lower lobe."
    )
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "diagnostic_bronchoscopy": {
                    "performed": True,
                    "inspection_findings": "endobronchial lesion. lesion. secretions obstructing right lower lobe",
                    "airway_abnormalities": ["Endobronchial lesion", "Secretions"],
                }
            }
        }
    )

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record

    assert updated is not None
    assert updated.procedures_performed is not None
    proc = updated.procedures_performed.diagnostic_bronchoscopy
    assert proc is not None
    assert proc.airway_abnormalities == ["Secretions"]
    assert proc.inspection_findings == "secretions obstructing right lower lobe"


def test_clinical_guardrails_clear_bal_for_washings_and_promote_bronchial_wash() -> None:
    note_text = """
    THERAPEUTIC BRONCHOSCOPY
    Procedure: Bronchoscopy with therapeutic aspiration
    Findings: Copious thick secretions obstructing left lower lobe basilar segments.
    Therapeutic aspiration and saline lavage performed until segmental bronchi patent.
    No endobronchial lesion.
    Specimen: "LLL washings" for culture.
    """.strip()
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "bal": {"performed": True},
                "therapeutic_aspiration": {"performed": True, "material": "Mucus plug"},
            }
        }
    )

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record

    assert updated is not None
    assert updated.procedures_performed is not None
    bal = updated.procedures_performed.bal
    assert bal is not None
    assert bal.performed is False
    bronchial_wash = updated.procedures_performed.bronchial_wash
    assert bronchial_wash is not None
    assert bronchial_wash.performed is True
    assert bronchial_wash.location == "LLL"


def test_clinical_guardrails_correct_bedside_trach_sedation_provider_conflict() -> None:
    note_text = """
    ANESTHESIA: Moderate sedation [CONFLICT: bedside general anesthesia in record; no anesthesiologist present; attending performed own sedation per ICU credentialing].
    """
    record = RegistryRecord.model_validate(
        {
            "sedation": {
                "type": "General",
                "anesthesia_provider": "Anesthesiologist",
            }
        }
    )

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record

    assert updated is not None
    assert updated.sedation is not None
    assert updated.sedation.type == "Moderate"
    assert updated.sedation.anesthesia_provider == "Proceduralist"


def test_clinical_guardrails_clear_bal_and_normalize_stent_metadata_for_airway_toilet_case() -> None:
    note_text = """
    Tracheal stent identified: migrated distally, tip 8 mm from carina.
    Stent removed with forceps through rigid barrel. Mucus cleared with lavage and suction.
    Repeat stent selection: same 18 mm x 60 mm Dumon stent repositioned and deployed with stent pusher;
    repositioned to 15 mm from carina under direct rigid vision.
    SPECIMENS: Granulation tissue from proximal stent contact site - formalin.
    """.strip()
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "bal": {"performed": True},
                "airway_stent": {
                    "performed": True,
                    "action": "Revision/Repositioning",
                    "action_type": "revision",
                    "airway_stent_removal": True,
                    "stent_type": "Silicone - Dumon",
                    "stent_brand": "ENT",
                    "location": "Carina (Y)",
                },
            }
        }
    )

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record

    assert updated is not None
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.bal is not None
    assert updated.procedures_performed.bal.performed is False
    stent = updated.procedures_performed.airway_stent
    assert stent is not None
    assert stent.stent_brand == "Dumon"
    assert stent.location == "Trachea"


def test_extract_endobronchial_biopsy_skips_peripheral_case_with_no_endobronchial_disease() -> None:
    note_text = (
        "Robotic navigation bronchoscopy to a left lower lobe peripheral nodule was performed. "
        "Radial EBUS confirmed eccentric view. Forceps biopsies were obtained. "
        "No endobronchial lesion was seen."
    )

    assert extract_endobronchial_biopsy(note_text) == {}


def test_clinical_guardrails_clear_model_endobronchial_biopsy_for_peripheral_forceps_case() -> None:
    note_text = (
        "Robotic navigation bronchoscopy to a left lower lobe peripheral nodule was performed. "
        "Radial EBUS confirmed eccentric view. TBNA x3 and forceps biopsies x7 were obtained. "
        'Specimens: "LLL TBNA", "LLL bx".'
    )
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "endobronchial_biopsy": {"performed": True},
                "transbronchial_biopsy": {"performed": True, "locations": ["LLL"]},
            }
        }
    )

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record

    assert updated is not None
    assert updated.procedures_performed is not None
    ebbx = updated.procedures_performed.endobronchial_biopsy
    assert ebbx is not None
    assert ebbx.performed is False


def test_clinical_guardrails_clear_foreign_body_removal_for_stent_removal() -> None:
    note_text = (
        "Flexible bronchoscopy demonstrated silicone stent in left mainstem bronchus. "
        "Rigid forceps used to grasp stent retrieval loop and stent removed en bloc."
    )
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "airway_stent": {"performed": True, "action": "Removal", "action_type": "removal"},
                "foreign_body_removal": {"performed": True},
            }
        }
    )

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record

    assert updated is not None
    assert updated.procedures_performed is not None
    foreign_body = updated.procedures_performed.foreign_body_removal
    assert foreign_body is not None
    assert foreign_body.performed is False


def test_clinical_guardrails_existing_stent_toileting_is_not_new_stent_placement() -> None:
    note_text = """
    Patient with prior tracheal stent for benign stenosis.
    Findings: Silicone tracheal stent in place with moderate granulation tissue at distal edge and adherent secretions.
    Mechanical debridement of granulation tissue with forceps.
    APC applied to focal granulation areas for hemostasis.
    Stent lumen suctioned clear.
    """.strip()
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "airway_stent": {
                    "performed": True,
                    "action": "Placement",
                    "action_type": "placement",
                }
            }
        }
    )

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record

    assert updated is not None
    assert updated.procedures_performed is not None
    stent = updated.procedures_performed.airway_stent
    assert stent is not None
    assert stent.action == "Assessment only"

    codes, _rationales, _warnings = derive_all_codes_with_meta(updated)
    assert "31636" not in codes


def test_reconcile_complications_ignores_minor_oozing_with_complications_none() -> None:
    note_text = (
        "Complications: None.\n"
        "Minor oozing resolved with suction and cold saline.\n"
    )
    record = RegistryRecord.model_validate({})

    reconcile_complications_from_narrative(record, note_text)

    complications = record.complications
    assert complications is None or complications.any_complication is not True


def test_clinical_guardrails_clear_existing_low_grade_bleeding_false_positive() -> None:
    note_text = (
        "Complications: None.\n"
        "Minor oozing resolved with suction.\n"
    )
    record = RegistryRecord.model_validate(
        {
            "complications": {
                "any_complication": True,
                "complication_list": ["Bleeding - Mild"],
                "events": [{"type": "Bleeding", "notes": "Minor oozing resolved with suction."}],
                "bleeding": {"occurred": True, "bleeding_grade_nashville": 1},
            }
        }
    )

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record

    assert updated is not None
    assert updated.complications is not None
    assert updated.complications.any_complication is False
    assert updated.complications.complication_list == []
    assert updated.complications.events == []
    assert updated.complications.bleeding is not None
    assert updated.complications.bleeding.occurred is False
    assert updated.complications.bleeding.bleeding_grade_nashville == 0


def test_registry_to_cpt_counts_record_level_elastography_as_single_target_without_per_station_flags() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "elastography_used": True,
                    "stations_sampled": ["7", "11R"],
                }
            }
        }
    )

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)

    assert "76982" in codes
    assert "76983" not in codes
