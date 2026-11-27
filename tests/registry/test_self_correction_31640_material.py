# ruff: noqa: E501  (clinical note strings are kept on one line for readability)
"""Self-correction may restore 31640 only for quote-anchored tumor debulking.

31640 is derived only when ``mechanical_debulking.material_type == "tumor"``. Self-correction
patches switch debulking on; the material type is re-derived from the procedure sentence that
contains the judge's evidence quote (never from the judge's own value).
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.registry.application.registry_service import RegistryService
from app.registry.schema import RegistryRecord
from app.registry.self_correction.material_grounding import (
    ground_material_type_from_quote,
    ground_mechanical_debulking_material,
)


class _StubRegistryEngine:
    def run(self, note_text: str, *, context=None, **_kwargs):  # type: ignore[no-untyped-def]
        return RegistryRecord()


def _stub_raw_ml_high_conf(monkeypatch: pytest.MonkeyPatch, *, cpt: str, prob: float = 0.99) -> None:
    from ml.lib.ml_coder.predictor import CaseClassification, CodePrediction, MLCoderPredictor
    from ml.lib.ml_coder.thresholds import CaseDifficulty

    pred = CodePrediction(cpt=cpt, prob=prob)
    monkeypatch.setattr(MLCoderPredictor, "__init__", lambda self, *a, **k: None)
    monkeypatch.setattr(
        MLCoderPredictor,
        "classify_case",
        lambda self, raw_note_text: CaseClassification(
            predictions=[pred],
            high_conf=[pred],
            gray_zone=[],
            difficulty=CaseDifficulty.HIGH_CONF,
        ),
    )


# --- grounding unit cases: exact material type from the anchored quote ---------------------


@pytest.mark.parametrize(
    ("note_text", "quote", "expected"),
    [
        pytest.param(
            "PROCEDURE:\nRigid bronchoscopy with tumor excision of left mainstem tumor.\n",
            "tumor excision",
            "tumor",
            id="tumor_excision",
        ),
        pytest.param(
            "PROCEDURE:\nThe exophytic tumor in the bronchus intermedius was excised with the microdebrider.\n",
            "The exophytic tumor in the bronchus intermedius was excised",
            "tumor",
            id="exophytic_tumor_microdebrider",
        ),
        pytest.param(
            "PROCEDURE:\nFungal-appearing material occluding the RUL bronchus was removed with forceps.\n",
            "Fungal-appearing material occluding the RUL bronchus was removed",
            "fungal_material",
            id="fungal_material",
        ),
        pytest.param(
            "PROCEDURE:\nA large mucus plug obstructing the left lower lobe bronchus was removed with forceps.\n",
            "A large mucus plug obstructing the left lower lobe bronchus was removed",
            "mucus",
            id="mucus_plug",
        ),
        pytest.param(
            "PROCEDURE:\nA blood clot obstructing the right middle lobe bronchus was removed with forceps.\n",
            "A blood clot obstructing the right middle lobe bronchus was removed",
            "mucus",
            id="blood_clot",
        ),
        pytest.param(
            "PROCEDURE:\nGranulation tissue at the stent edge was excised with forceps.\n",
            "Granulation tissue at the stent edge was excised",
            "granulation",
            id="granulation_tissue",
        ),
        pytest.param(
            "PROCEDURE:\nForceps and a cryoprobe were introduced into the left mainstem bronchus.\n",
            "Forceps and a cryoprobe were introduced into the left mainstem bronchus",
            "unknown",
            id="tools_without_tissue_or_action",
        ),
        pytest.param(
            "HISTORY: Left mainstem tumor, s/p rigid tumor debulking in 2024.\n"
            "PROCEDURE:\nDiagnostic bronchoscopy; the left mainstem was patent.\n",
            "s/p rigid tumor debulking in 2024",
            "unknown",
            id="tumor_only_in_history",
        ),
        pytest.param(
            "PROCEDURE:\nDiagnostic bronchoscopy with airway inspection.\n"
            "PLAN: Will perform tumor debulking at the next bronchoscopy.\n",
            "Will perform tumor debulking at the next bronchoscopy",
            "unknown",
            id="tumor_only_in_plan",
        ),
        pytest.param(
            "PROCEDURE:\nNo tumor was seen; the airway was cleared with suction.\n",
            "No tumor was seen; the airway was cleared",
            "unknown",
            id="negated_tumor",
        ),
        pytest.param(
            "PROCEDURE:\nDiagnostic bronchoscopy with airway inspection.\n",
            "The endobronchial tumor was excised with forceps",
            "unknown",
            id="quote_not_in_note",
        ),
        # Action on something other than the tumor (review cases 1-3).
        pytest.param(
            "PROCEDURE IN DETAIL:\nThe stent was removed and tumor ingrowth was noted at the distal end.\n",
            "The stent was removed and tumor ingrowth was noted at the distal end",
            "unknown",
            id="stent_removed_tumor_only_noted",
        ),
        pytest.param(
            "PROCEDURE IN DETAIL:\nThe bronchoscope was removed after the tumor was inspected.\n",
            "The bronchoscope was removed after the tumor was inspected",
            "unknown",
            id="scope_removed_tumor_only_inspected",
        ),
        pytest.param(
            "PROCEDURE IN DETAIL:\nClot was extracted from the right mainstem; the underlying mass was not biopsied.\n",
            "Clot was extracted from the right mainstem",
            "unknown",
            id="clot_extracted_mass_in_other_clause",
        ),
        # Conservative misses that must ground to tumor (review cases 5-6).
        pytest.param(
            "PROCEDURE IN DETAIL:\nThe tumor, measuring 2.5 cm, was debulked with forceps.\n",
            "was debulked with forceps",
            "tumor",
            id="decimal_measurement_not_a_sentence_break",
        ),
        pytest.param(
            "PROCEDURE IN DETAIL:\nExophytic tumor was debulked with the microdebrider and specimens will be sent to pathology.\n",
            "Exophytic tumor was debulked with the microdebrider and specimens will be sent to pathology",
            "tumor",
            id="plan_word_after_the_action",
        ),
    ],
)
def test_ground_material_type_from_quote(note_text: str, quote: str, expected: str) -> None:
    assert ground_material_type_from_quote(note_text, quote) == expected


# --- self-correction loop: exact derived codes ---------------------------------------------


@pytest.mark.parametrize(
    ("note_text", "quote", "judge_material", "expected_codes"),
    [
        pytest.param(
            "PROCEDURE:\nRigid bronchoscopy was performed. The exophytic tumor in the bronchus intermedius "
            "was excised with the microdebrider until the airway was patent.\n",
            "The exophytic tumor in the bronchus intermedius was excised with the microdebrider",
            None,
            ["31640"],
            id="preserve_exophytic_tumor_microdebrider",
        ),
        pytest.param(
            "PROCEDURE IN DETAIL: Mechanical debulking of an obstructing endobronchial tumor in the left "
            "mainstem was performed with forceps and the rigid barrel.\n",
            "Mechanical debulking of an obstructing endobronchial tumor in the left mainstem was performed",
            None,
            ["31640"],
            id="preserve_mechanical_debulking_tumor",
        ),
        pytest.param(
            "PROCEDURE:\nMechanical debulking of fungal-appearing material occluding the RUL bronchus was "
            "performed with forceps.\n",
            "Mechanical debulking of fungal-appearing material occluding the RUL bronchus was performed",
            "tumor",
            [],
            id="suppress_fungal_even_if_judge_claims_tumor",
        ),
        pytest.param(
            "PROCEDURE:\nForceps debulking of a large mucus plug obstructing the left lower lobe bronchus "
            "was performed.\n",
            "Forceps debulking of a large mucus plug obstructing the left lower lobe bronchus was performed",
            None,
            [],
            id="suppress_mucus_plug",
        ),
        pytest.param(
            "PROCEDURE:\nMechanical debulking of blood clot in the right middle lobe bronchus was performed "
            "with forceps.\n",
            "Mechanical debulking of blood clot in the right middle lobe bronchus was performed",
            None,
            [],
            id="suppress_blood_clot",
        ),
        pytest.param(
            "PROCEDURE:\nMechanical debulking of granulation tissue at the stent edge in the left mainstem "
            "was performed with forceps.\n",
            "Mechanical debulking of granulation tissue at the stent edge in the left mainstem was performed",
            None,
            [],
            id="suppress_granulation",
        ),
        pytest.param(
            "PROCEDURE:\nThe microdebrider was set up at the bedside. Airway inspection showed a patent "
            "left mainstem.\n",
            "The microdebrider was set up at the bedside",
            "tumor",
            [],
            id="suppress_tool_mention_even_if_judge_claims_tumor",
        ),
        pytest.param(
            "HISTORY: Left mainstem tumor, s/p mechanical debulking in 2024.\nPROCEDURE:\n"
            "Diagnostic bronchoscopy with airway inspection; the left mainstem was patent.\n",
            "s/p mechanical debulking in 2024",
            None,
            [],
            id="suppress_tumor_only_in_history",
        ),
        pytest.param(
            "PROCEDURE:\nDiagnostic bronchoscopy with airway inspection.\n"
            "PLAN: Will perform mechanical debulking of the tumor at the next bronchoscopy.\n",
            "Will perform mechanical debulking of the tumor at the next bronchoscopy",
            None,
            [],
            id="suppress_tumor_only_in_plan",
        ),
    ],
)
def test_self_correction_31640_requires_grounded_tumor(
    monkeypatch: pytest.MonkeyPatch,
    note_text: str,
    quote: str,
    judge_material: str | None,
    expected_codes: list[str],
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "1")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")
    _stub_raw_ml_high_conf(monkeypatch, cpt="31640", prob=0.99)

    from app.registry.self_correction.judge import PatchProposal, RegistryCorrectionJudge

    patch = [{"op": "add", "path": "/procedures_performed/mechanical_debulking/performed", "value": True}]
    if judge_material is not None:
        patch.append(
            {"op": "add", "path": "/procedures_performed/mechanical_debulking/material_type", "value": judge_material}
        )
    monkeypatch.setattr(
        RegistryCorrectionJudge,
        "propose_correction",
        MagicMock(return_value=PatchProposal(rationale="test", json_patch=patch, evidence_quote=quote)),
    )
    orchestrator = MagicMock()
    orchestrator.get_codes.side_effect = RuntimeError("SmartHybridOrchestrator.get_codes() called")

    service = RegistryService(hybrid_orchestrator=orchestrator, registry_engine=_StubRegistryEngine())
    result = service.extract_fields(note_text)

    assert result.cpt_codes == expected_codes
    assert any(w.startswith("AUTO_CORRECTED: 31640") for w in result.warnings) is bool(expected_codes)


# --- pre-patch material is never replaced (review case 4) ----------------------------------


def _record(material: str | None) -> RegistryRecord:
    debulking: dict[str, object] = {"performed": True}
    if material is not None:
        debulking["material_type"] = material
    return RegistryRecord.model_validate({"procedures_performed": {"mechanical_debulking": debulking}})


_PERFORMED_PATCH = [{"op": "add", "path": "/procedures_performed/mechanical_debulking/performed", "value": True}]
_TWO_SENTENCE_NOTE = (
    "PROCEDURE IN DETAIL:\nThe endobronchial tumor in the left mainstem was debulked with forceps. "
    "Debulking was completed with the microdebrider.\n"
)


def test_known_tumor_material_is_kept_when_quote_names_no_tissue() -> None:
    record, warning = ground_mechanical_debulking_material(
        _record("tumor"),
        patch=_PERFORMED_PATCH,
        evidence_quote="Debulking was completed with the microdebrider",
        note_text=_TWO_SENTENCE_NOTE,
        original_record=_record("tumor"),
    )
    assert record.procedures_performed.mechanical_debulking.material_type == "tumor"
    assert warning is None


def test_judge_written_material_is_reverted_to_known_pre_patch_value() -> None:
    patch = _PERFORMED_PATCH + [
        {"op": "add", "path": "/procedures_performed/mechanical_debulking/material_type", "value": "tumor"}
    ]
    record, warning = ground_mechanical_debulking_material(
        _record("tumor"),
        patch=patch,
        evidence_quote="Fungal-appearing material was removed with forceps",
        note_text="PROCEDURE IN DETAIL:\nFungal-appearing material was removed with forceps.\n",
        original_record=_record("fungal_material"),
    )
    assert record.procedures_performed.mechanical_debulking.material_type == "fungal_material"
    assert warning is not None and warning.startswith("SELF_CORRECT_MATERIAL_GROUNDED: kept pre-patch")


def test_conflicting_known_material_keeps_pre_patch_value_and_warns() -> None:
    record, warning = ground_mechanical_debulking_material(
        _record("tumor"),
        patch=_PERFORMED_PATCH,
        evidence_quote="Granulation tissue was excised with forceps",
        note_text="PROCEDURE IN DETAIL:\nGranulation tissue was excised with forceps.\n",
        original_record=_record("tumor"),
    )
    assert record.procedures_performed.mechanical_debulking.material_type == "tumor"
    assert warning is not None and warning.startswith("SELF_CORRECT_MATERIAL_CONFLICT")


def test_missing_material_is_filled_from_quote() -> None:
    record, warning = ground_mechanical_debulking_material(
        _record(None),
        patch=_PERFORMED_PATCH,
        evidence_quote="The endobronchial tumor in the left mainstem was debulked with forceps",
        note_text=_TWO_SENTENCE_NOTE,
        original_record=RegistryRecord(),
    )
    assert record.procedures_performed.mechanical_debulking.material_type == "tumor"
    assert warning is not None and "material_type=tumor" in warning
