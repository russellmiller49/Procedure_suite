from modules.phi.safety.veto import apply_protected_veto


def test_veto_cpt_context():
    tokens = ["cpt", "316", "##53"]
    preds = ["O", "B-ID", "I-ID"]
    out = apply_protected_veto(tokens, preds, text="CPT 31653 billed")
    assert out[1:] == ["O", "O"]


def test_veto_ln_station():
    tokens = ["4", "##r", "station"]
    preds = ["B-GEO", "I-GEO", "O"]
    out = apply_protected_veto(tokens, preds)
    assert out[0] == "O"
    assert out[1] == "O"


def test_veto_device_name():
    tokens = ["du", "##mon"]
    preds = ["B-ID", "I-ID"]
    out = apply_protected_veto(tokens, preds)
    assert out == ["O", "O"]


def test_veto_anatomy_phrase():
    tokens = ["left", "upper", "lobe"]
    preds = ["B-GEO", "I-GEO", "I-GEO"]
    out = apply_protected_veto(tokens, preds)
    assert out == ["O", "O", "O"]


def test_veto_leaves_patient_name():
    tokens = ["jennifer", "wu"]
    preds = ["B-PATIENT", "I-PATIENT"]
    out = apply_protected_veto(tokens, preds)
    assert out == preds
