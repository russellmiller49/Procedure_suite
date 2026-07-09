from __future__ import annotations

from app.registry.deterministic_extractors import (
    extract_primary_indication,
    extract_therapeutic_injection,
)
from app.registry.postprocess import enrich_procedure_success_status
from app.registry.schema import RegistryRecord
from app.registry.self_correction.keyword_guard import apply_required_overrides


# --- 2.4 indication consent-boilerplate scrub -------------------------------


def test_indication_scrubs_consent_was_obtained_tail() -> None:
    text = (
        "INDICATIONS: bilobar collapse\n"
        "Consent was obtained from the patient prior to procedure after explanation in lay "
        "terms the indications, details of procedure, and potential risks and alternatives.\n"
    )
    assert extract_primary_indication(text) == "bilobar collapse"


def test_indication_keeps_clinical_reasoning() -> None:
    text = "INDICATIONS: Recurrent left pleural effusion with dyspnea at rest\n"
    assert extract_primary_indication(text) == "Recurrent left pleural effusion with dyspnea at rest"


# --- 2.5 partial-success outcome precedence ---------------------------------


def test_partial_reopening_percent_language_yields_partial_success() -> None:
    text = (
        "After debulking in the left upper lobe we had complete opening of the lobar and "
        "segmental bronchi. We were able to open the left lower lobe orifice to approximately "
        "70% of normal but despite our best efforts we could not completely remove the tumor "
        "due to the extent of disease."
    )
    record = RegistryRecord.model_validate({})
    enrich_procedure_success_status(record, text)
    assert record.outcomes is not None
    assert record.outcomes.procedure_success_status == "Partial success"


def test_global_abort_still_wins_over_partial_language() -> None:
    text = (
        "The airway was opened to 50% of normal. Shortly afterwards the procedure was aborted "
        "due to significant bleeding."
    )
    record = RegistryRecord.model_validate({})
    enrich_procedure_success_status(record, text)
    assert record.outcomes is not None
    assert record.outcomes.procedure_success_status == "Aborted"


def test_pure_failure_without_partial_achievement_stays_failed() -> None:
    text = "We were unable to complete the procedure and no therapeutic goal was achieved."
    record = RegistryRecord.model_validate({})
    enrich_procedure_success_status(record, text)
    assert record.outcomes is not None
    assert record.outcomes.procedure_success_status == "Failed"


# --- 2.2 topical hemostatic agents are not therapeutic injection ------------


def test_lidocaine_with_epinephrine_for_hemostasis_not_therapeutic_injection() -> None:
    text = (
        "Multiple forceps biopsies were obtained. Lidocaine with epinephrine was instilled in "
        "addition to cold saline to achieve adequate hemostasis."
    )
    assert extract_therapeutic_injection(text) == {}


def test_txa_instillation_for_bleeding_not_therapeutic_injection() -> None:
    text = "Bleeding was moderate and resolved with topical instillation of 1:1000 TXA through the bronchoscope."
    assert extract_therapeutic_injection(text) == {}


def test_true_intratumoral_injection_preserved() -> None:
    text = "Cisplatin 40 mg was injected intratumorally into the RMS lesion."
    proc = extract_therapeutic_injection(text).get("therapeutic_injection") or {}
    assert proc.get("performed") is True
    assert proc.get("medication") == "Cisplatin"


def test_amphotericin_instillation_preserved() -> None:
    text = "Amphotericin B 50 mg was instilled into the cavity for treatment of the mycetoma."
    proc = extract_therapeutic_injection(text).get("therapeutic_injection") or {}
    assert proc.get("performed") is True


# --- 2.3 chest-tube-removal hallucination guard (IPC placement mechanics) ---


def _removal_flag(note_text: str) -> bool | None:
    record = RegistryRecord.model_validate({})
    updated, _warnings = apply_required_overrides(note_text, record)
    removal = getattr(getattr(updated, "pleural_procedures", None), "chest_tube_removal", None)
    return getattr(removal, "performed", None)


def test_ipc_placement_tunneler_language_does_not_set_chest_tube_removal() -> None:
    text = (
        "The Pleurx catheter was attached to the tunneler and pulled through the subcutaneous "
        "tract, followed by dilatation of the pleural access tract with the 16 fr peel away "
        "sheath via seldinger technique."
    )
    assert _removal_flag(text) is not True


def test_needle_removed_catheter_left_in_place_does_not_set_removal() -> None:
    text = (
        "A guide wire was advanced into the pleural space through the catheter. The needle was "
        "removed and the catheter left in place."
    )
    assert _removal_flag(text) is not True


def test_true_chest_tube_removal_preserved() -> None:
    text = "The left chest tube was removed on post-operative day 2. The site was dressed."
    assert _removal_flag(text) is True


def test_existing_ipc_removal_preserved() -> None:
    text = "The existing PleurX catheter was removed intact from the pleural space."
    assert _removal_flag(text) is True


# --- airway type: LMA vs ETT -------------------------------------------------


def test_intubated_with_lma_is_lma_not_ett() -> None:
    from app.registry.deterministic_extractors import extract_sedation_airway

    text = (
        "Anesthesia: General anesthesia using a LMA. The patient was orally intubated with a "
        "LMA by the anesthesia team."
    )
    result = extract_sedation_airway(text)
    assert result.get("airway_type") == "LMA"


def test_explicit_ett_still_detected() -> None:
    from app.registry.deterministic_extractors import extract_sedation_airway

    text = "General anesthesia. The patient was intubated with an 8.0 ETT."
    result = extract_sedation_airway(text)
    assert result.get("airway_type") == "ETT"
