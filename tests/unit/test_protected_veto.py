"""Tests for PHI protected veto module."""

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


# =============================================================================
# NEW TESTS: Drop-whole-entity-on-veto logic
# =============================================================================


def test_drop_whole_entity_chartis():
    """Test that 'chartis' inside entity drops the ENTIRE entity, not just chartis tokens.

    This is the core fix: without drop-whole-entity, IOB repair would turn "a" into B-PATIENT.
    """
    tokens = ["did", "a", "chart", "##is", "on", "gloria", "ortiz"]
    preds = ["O", "I-PATIENT", "I-PATIENT", "I-PATIENT", "O", "B-PATIENT", "I-PATIENT"]

    out = apply_protected_veto(tokens, preds)

    # The erroneous span ["a", "chart", "##is"] should be completely cleared
    assert out[1] == "O", "Token 'a' should be O, not promoted to B-PATIENT"
    assert out[2] == "O", "Token 'chart' should be O"
    assert out[3] == "O", "Token '##is' should be O"

    # The correct patient name should remain
    assert out[5] == "B-PATIENT", "Token 'gloria' should remain B-PATIENT"
    assert out[6] == "I-PATIENT", "Token 'ortiz' should remain I-PATIENT"


def test_drop_whole_entity_device_at_start():
    """Protected term at START of entity drops whole span."""
    tokens = ["chart", "##is", "test"]
    preds = ["B-PATIENT", "I-PATIENT", "I-PATIENT"]

    out = apply_protected_veto(tokens, preds)
    assert out == ["O", "O", "O"], "Entire entity should be dropped"


def test_drop_whole_entity_device_at_end():
    """Protected term at END of entity drops whole span."""
    tokens = ["test", "chart", "##is"]
    preds = ["B-PATIENT", "I-PATIENT", "I-PATIENT"]

    out = apply_protected_veto(tokens, preds)
    assert out == ["O", "O", "O"], "Entire entity should be dropped"


def test_drop_whole_entity_device_in_middle():
    """Protected term in MIDDLE of entity drops whole span."""
    tokens = ["pre", "chart", "##is", "post"]
    preds = ["B-PATIENT", "I-PATIENT", "I-PATIENT", "I-PATIENT"]

    out = apply_protected_veto(tokens, preds)
    assert out == ["O", "O", "O", "O"], "Entire entity should be dropped"


def test_stopword_only_span_dropped():
    """Entity containing only stopwords should be dropped."""
    tokens = ["a"]
    preds = ["B-PATIENT"]

    out = apply_protected_veto(tokens, preds)
    assert out == ["O"], "Stopword-only span should be dropped"


def test_punctuation_start_span_dropped():
    """Entity starting with punctuation should be dropped."""
    tokens = ["(", "760", "##00"]
    preds = ["B-ID", "I-ID", "I-ID"]

    out = apply_protected_veto(tokens, preds)
    assert out == ["O", "O", "O"], "Span starting with '(' should be dropped"


def test_adjacent_entities_preserved():
    """When one entity is dropped, adjacent entities should be preserved."""
    tokens = ["the", "chart", "##is", "and", "jennifer", "wu"]
    preds = ["B-PATIENT", "I-PATIENT", "I-PATIENT", "O", "B-PATIENT", "I-PATIENT"]

    out = apply_protected_veto(tokens, preds)

    # First entity (containing chartis) should be dropped
    assert out[0:4] == ["O", "O", "O", "O"], "First entity with chartis should be dropped"

    # Second entity (jennifer wu) should be preserved
    assert out[4] == "B-PATIENT", "Token 'jennifer' should remain B-PATIENT"
    assert out[5] == "I-PATIENT", "Token 'wu' should remain I-PATIENT"


# =============================================================================
# NEW TESTS: Atomic numeric spans
# =============================================================================


def test_cbct_numeric_code_veto():
    """CBCT context should clear numeric codes."""
    tokens = ["cbct", "(", "760", "##00", "/", "770", "##02", ")"]
    preds = ["O", "B-ID", "I-ID", "I-ID", "I-ID", "I-ID", "I-ID", "I-ID"]

    out = apply_protected_veto(tokens, preds, text="CBCT (76000/77002) is distinct")

    # All the numeric code tokens should be O
    assert out[2] == "O", "760 should be O in CBCT context"
    assert out[3] == "O", "##00 should be O in CBCT context"
    assert out[5] == "O", "770 should be O in CBCT context"
    assert out[6] == "O", "##02 should be O in CBCT context"


def test_coding_context_numeric_veto():
    """Coding: prefix should trigger numeric code veto."""
    tokens = ["coding", ":", "316", "##41"]
    preds = ["O", "O", "B-ID", "I-ID"]

    out = apply_protected_veto(tokens, preds, text="Coding: 31641")

    assert out[2] == "O", "CPT code should be O in coding context"
    assert out[3] == "O", "CPT code continuation should be O"


def test_mrn_without_coding_context_preserved():
    """MRN-like numbers outside coding context should NOT be cleared."""
    tokens = ["mrn", ":", "12345"]
    preds = ["O", "O", "B-ID"]

    out = apply_protected_veto(tokens, preds)

    # MRN context != CPT context, should preserve
    assert out[2] == "B-ID", "MRN should be preserved (not in CPT context)"


# =============================================================================
# NEW TESTS: Dangling entity prevention
# =============================================================================


def test_no_dangling_single_letter_entity():
    """Single letter entities should not survive."""
    tokens = ["a", "patient", "name"]
    preds = ["B-PATIENT", "O", "O"]

    out = apply_protected_veto(tokens, preds)
    assert out[0] == "O", "Single letter 'a' should not be a PATIENT entity"


def test_very_short_span_dropped():
    """Very short spans (< 2 chars) should be dropped."""
    tokens = ["I"]
    preds = ["B-PATIENT"]

    out = apply_protected_veto(tokens, preds)
    assert out == ["O"], "Single letter entity should be dropped"
