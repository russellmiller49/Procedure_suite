import pytest
from modules.registry.engine import RegistryEngine
from tests.utils.case_filter import load_synthetic_cases, filter_cases

# Load cases once
ALL_CASES = load_synthetic_cases()

@pytest.fixture(scope="module")
def registry_engine():
    return RegistryEngine()

@pytest.mark.ebus
def test_ebus_systematic_staging_extraction(registry_engine):
    """Test extraction of ebus_systematic_staging field."""
    cases = filter_cases(ALL_CASES, required_fields=["ebus_systematic_staging"])
    # Also include cases where it is explicitly False (filter_cases checks for not None/Empty)
    # But filter_cases implementation: val not in (None, "", [], {{}})
    # False is not in that set, so it should be included.
    
    assert len(cases) > 0, "No cases with ebus_systematic_staging found"
    
    for case in cases:
        note_text = case["note_text"]
        expected = case["registry_entry"]["ebus_systematic_staging"]
        
        result = registry_engine.run(note_text, include_evidence=False)
        assert result.ebus_systematic_staging == expected, \
            f"Failed for MRN {case['registry_entry'].get('patient_mrn')}"

@pytest.mark.ebus
def test_ebus_rose_extraction(registry_engine):
    """Test extraction of ebus_rose_available and ebus_rose_result."""
    cases = filter_cases(ALL_CASES, required_fields=["ebus_rose_available", "ebus_rose_result"])
    
    assert len(cases) > 0, "No cases with ROSE fields found"

    for case in cases:
        note_text = case["note_text"]
        expected_avail = case["registry_entry"].get("ebus_rose_available")
        expected_result = case["registry_entry"].get("ebus_rose_result")
        
        result = registry_engine.run(note_text, include_evidence=False)
        
        if expected_avail is not None:
            assert result.ebus_rose_available == expected_avail, \
                f"ROSE Available mismatch for MRN {case['registry_entry'].get('patient_mrn')}"
        
        if expected_result is not None:
            assert result.ebus_rose_result == expected_result, \
                f"ROSE Result mismatch for MRN {case['registry_entry'].get('patient_mrn')}"

@pytest.mark.ebus
def test_ebus_stations_sampled(registry_engine):
    """Test extraction of ebus_stations_sampled."""
    cases = filter_cases(ALL_CASES, required_fields=["ebus_stations_sampled"])
    
    assert len(cases) > 0, "No cases with stations sampled found"

    for case in cases:
        note_text = case["note_text"]
        expected = set(case["registry_entry"]["ebus_stations_sampled"])
        
        result = registry_engine.run(note_text, include_evidence=False)
        extracted = set(result.ebus_stations_sampled or [])
        
        # Allow for partial match if heuristic is imperfect, but for the updated cases it should match.
        # Or check if expected is subset of extracted or vice versa?
        # Ideally exact match or close.
        # For this test, let's assert expected is a subset of extracted or equal.
        # Actually, updated data has precise expectations.
        assert extracted == expected, \
            f"Stations mismatch for MRN {case['registry_entry'].get('patient_mrn')}. Expected {expected}, got {extracted}"

@pytest.mark.ebus
def test_ebus_scope_and_needle(registry_engine):
    """Test extraction of scope brand and needle info."""
    cases = filter_cases(ALL_CASES, required_fields=["ebus_scope_brand", "ebus_needle_gauge", "ebus_needle_type"])
    
    assert len(cases) > 0

    for case in cases:
        note_text = case["note_text"]
        exp_brand = case["registry_entry"].get("ebus_scope_brand")
        exp_gauge = case["registry_entry"].get("ebus_needle_gauge")
        exp_type = case["registry_entry"].get("ebus_needle_type")
        
        result = registry_engine.run(note_text, include_evidence=False)
        
        if exp_brand:
            assert result.ebus_scope_brand == exp_brand, f"Brand mismatch MRN {case['registry_entry'].get('patient_mrn')}"
        if exp_gauge:
            assert result.ebus_needle_gauge == exp_gauge, f"Gauge mismatch MRN {case['registry_entry'].get('patient_mrn')}"
        if exp_type:
            assert result.ebus_needle_type == exp_type, f"Needle type mismatch MRN {case['registry_entry'].get('patient_mrn')}"

@pytest.mark.ebus
def test_ebus_photodocumentation(registry_engine):
    """Test extraction of ebus_photodocumentation_complete."""
    cases = filter_cases(ALL_CASES, required_fields=["ebus_photodocumentation_complete"])
    
    assert len(cases) > 0

    for case in cases:
        note_text = case["note_text"]
        expected = case["registry_entry"]["ebus_photodocumentation_complete"]
        
        result = registry_engine.run(note_text, include_evidence=False)
        assert result.ebus_photodocumentation_complete == expected, \
             f"Photodoc mismatch MRN {case['registry_entry'].get('patient_mrn')}"

@pytest.mark.ebus
def test_sedation_reversal(registry_engine):
    """Test extraction of sedation reversal fields."""
    cases = filter_cases(ALL_CASES, required_fields=["sedation_reversal_given"])
    
    assert len(cases) > 0

    for case in cases:
        note_text = case["note_text"]
        exp_given = case["registry_entry"]["sedation_reversal_given"]
        exp_agent = case["registry_entry"].get("sedation_reversal_agent")
        
        result = registry_engine.run(note_text, include_evidence=False)
        assert result.sedation_reversal_given == exp_given, \
            f"Reversal given mismatch MRN {case['registry_entry'].get('patient_mrn')}"
        
        if exp_agent:
            assert result.sedation_reversal_agent == exp_agent, \
                f"Reversal agent mismatch MRN {case['registry_entry'].get('patient_mrn')}"
