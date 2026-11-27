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
from app.registry.self_correction.material_grounding import ground_material_type_from_quote


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
