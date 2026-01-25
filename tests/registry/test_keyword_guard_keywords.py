from __future__ import annotations

from modules.registry.self_correction.keyword_guard import keyword_guard_passes


def test_keyword_guard_passes_for_fiducials_31626() -> None:
    assert keyword_guard_passes(
        cpt="31626",
        evidence_text="Fiducial marker placement performed in the right upper lobe.",
    )


def test_keyword_guard_passes_for_tbna_31629() -> None:
    assert keyword_guard_passes(
        cpt="31629",
        evidence_text="TBNA performed at station 7 with adequate sampling.",
    )


def test_keyword_guard_passes_for_tbna_terms_31652() -> None:
    assert keyword_guard_passes(
        cpt="31652",
        evidence_text="Transbronchial needle aspiration performed of station 4R.",
    )


def test_keyword_guard_passes_for_transbronchial_forceps_biopsy_31628() -> None:
    assert keyword_guard_passes(
        cpt="31628",
        evidence_text="Transbronchial forceps biopsy performed with standard forceps.",
    )


def test_keyword_guard_passes_for_mechanical_debulking_31640() -> None:
    assert keyword_guard_passes(
        cpt="31640",
        evidence_text="Rigid bronchoscopy with mechanical debulking using a microdebrider.",
    )


def test_keyword_guard_passes_for_fibrinolysis_32562() -> None:
    assert keyword_guard_passes(
        cpt="32562",
        evidence_text="Intrapleural fibrinolysis with tPA/DNase instillation via chest tube (subsequent day).",
    )
