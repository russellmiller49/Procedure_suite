from modules.ml_coder.registry_label_constraints import apply_label_constraints


def test_bal_forces_bronchial_wash_off() -> None:
    row = {
        "note_text": "Procedure: Bronchoscopy with BAL performed.",
        "bal": 1,
        "bronchial_wash": 1,
    }
    apply_label_constraints(row)
    assert row["bal"] == 1
    assert row["bronchial_wash"] == 0


def test_transbronchial_cryobiopsy_implies_transbronchial_biopsy() -> None:
    row = {
        "transbronchial_cryobiopsy": 1,
        "transbronchial_biopsy": 0,
    }
    apply_label_constraints(row)
    assert row["transbronchial_cryobiopsy"] == 1
    assert row["transbronchial_biopsy"] == 1


def test_noop_for_unrelated_labels() -> None:
    row = {"linear_ebus": 1, "bal": 0, "bronchial_wash": 0}
    before = dict(row)
    apply_label_constraints(row)
    assert row == before

