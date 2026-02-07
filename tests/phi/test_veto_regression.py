"""
Regression tests for PHI veto layer false positive prevention.

These tests document the expected behavior for the CLIENT-SIDE JavaScript
veto layer (protectedVeto.js). The actual validation happens via browser
testing or the audit scripts (make audit-phi-client, make gold-audit).

This file serves as:
1. Documentation of false positive cases that must be handled
2. Fixture definitions for browser-based testing
3. Integration with server-side veto IF compatible API is available

Test categories:
- Laterality + anatomy phrases (left adrenal, apical segment)
- Clinical heading comma phrases (Elastography, First)
- Single-token clinical terms (Air, Still, Flow)
- Vent settings integers (400, 12, 60)
- Balloon sizes as dates (8/9/10)
- Session name false positives
"""

import pytest
from typing import List, Dict, Any

# The server-side veto module uses a token-based BIO tagging API,
# while the client-side JS uses span-based offsets.
# We skip server-side testing if the API is incompatible.
HAS_COMPATIBLE_VETO = False
try:
    from app.phi.safety.veto import apply_protected_veto
    import inspect
    sig = inspect.signature(apply_protected_veto)
    params = list(sig.parameters.keys())
    # Check if it has the span-based API (spans, text) vs token-based (tokens, pred_tags, text)
    if 'spans' in params or (len(params) >= 2 and params[0] != 'tokens'):
        HAS_COMPATIBLE_VETO = True
except ImportError:
    pass


# =============================================================================
# TEST FIXTURES: Spans that MUST NOT be redacted
# =============================================================================

MUST_NOT_REDACT_PATIENT = [
    # Laterality + anatomy phrases (Phase 2B)
    {"text": "left adrenal", "label": "PATIENT"},
    {"text": "right adrenal", "label": "PATIENT"},
    {"text": "apical segment", "label": "PATIENT"},
    {"text": "posterior segment", "label": "PATIENT"},
    {"text": "lateral segment", "label": "PATIENT"},
    {"text": "left mainstem", "label": "PATIENT"},
    {"text": "right carina", "label": "PATIENT"},
    {"text": "bilateral hilum", "label": "PATIENT"},
    {"text": "subcarinal", "label": "PATIENT"},
    {"text": "left bronchus", "label": "PATIENT"},
    {"text": "right lung", "label": "PATIENT"},

    # Clinical heading comma phrases (Phase 2C)
    {"text": "Elastography, First", "label": "PATIENT"},
    {"text": "Cytology, Flow", "label": "PATIENT"},
    {"text": "Pathology, Surgical", "label": "PATIENT"},
    {"text": "Specimen, Primary", "label": "PATIENT"},
    {"text": "Lymphocytes, Additional", "label": "PATIENT"},

    # Single-token clinical terms (Phase 2D)
    {"text": "Air", "label": "PATIENT"},
    {"text": "Still", "label": "PATIENT"},
    {"text": "Flow", "label": "PATIENT"},
    {"text": "Serial", "label": "PATIENT"},
    {"text": "Pain", "label": "PATIENT"},
    {"text": "Mass", "label": "PATIENT"},
    {"text": "Clear", "label": "PATIENT"},
    {"text": "Stable", "label": "PATIENT"},
    {"text": "Suction", "label": "PATIENT"},
    {"text": "Lavage", "label": "PATIENT"},
    {"text": "Dilation", "label": "PATIENT"},
    {"text": "Scope", "label": "PATIENT"},

    # Clinical two-word phrases that look like names
    {"text": "Serial irrigation", "label": "PATIENT"},
    {"text": "Dilation balloon", "label": "PATIENT"},
]

MUST_NOT_REDACT_ID = [
    # Vent settings integers (Phase 3A)
    {"text": "400", "label": "ID", "context": "Vent settings: Mode AC, RR 12, TV 400, PEEP 5"},
    {"text": "12", "label": "ID", "context": "Ventilator parameters: RR 12, FiO2 60%"},
    {"text": "60", "label": "ID", "context": "FiO2 60%, PEEP 14"},
    {"text": "14", "label": "ID", "context": "PEEP 14, TV 450"},
    {"text": "450", "label": "ID", "context": "Tidal Volume 450 ml"},
    {"text": "70", "label": "ID", "context": "Flow 70 L/min"},
    {"text": "10", "label": "ID", "context": "PEEP 10, respiratory rate 17"},
    {"text": "17", "label": "ID", "context": "Respiratory rate 17"},
]

MUST_NOT_REDACT_DATE = [
    # Balloon sizes (Phase 3B)
    {"text": "8/9/10", "label": "DATE", "context": "Sequential balloon dilation 8/9/10 mm"},
    {"text": "10/11/12", "label": "DATE", "context": "Elation balloon 10/11/12 dilation"},
    {"text": "6/7/8", "label": "DATE", "context": "Balloon sizes 6/7/8 for stricture dilation"},
    {"text": "12/13/14", "label": "DATE", "context": "CRE dilation 12/13/14 mm"},
]

# =============================================================================
# TEST FIXTURES: Spans that MUST be redacted (safety net)
# =============================================================================

MUST_REDACT = [
    {"text": "John Smith", "label": "PATIENT", "context": "Patient: John Smith"},
    {"text": "12345678", "label": "ID", "context": "MRN: 12345678"},
    {"text": "01/15/1960", "label": "DATE", "context": "DOB: 01/15/1960"},
    {"text": "Jane Doe", "label": "PATIENT", "context": "Patient Name: Jane Doe"},
]


# =============================================================================
# TEST CONTEXT SNIPPETS FOR FULL-TEXT TESTING
# =============================================================================

VENT_SETTINGS_SNIPPET = """
Ventilation Parameters:
Mode: AC/VC
RR: 12
TV: 400 ml
PEEP: 14
FiO2: 60%
Flow: 70 L/min
Pmean: 17
"""

ELASTOGRAPHY_SNIPPET = """
Elastography, First Target Lesion:
The mass in the left adrenal was evaluated using EUS elastography.
Cytology, Flow analysis showed lymphocytes and macrophages.
"""

BALLOON_DILATION_SNIPPET = """
Procedure: Esophageal stricture dilation
Using Elation CRE balloon, sequential dilation performed at 8/9/10 mm.
Good result achieved. Patient tolerated procedure well.
"""

CLINICAL_SENTENCE_SNIPPET = """
Air was noted in the pleural space.
Still evaluating the posterior segment.
Serial irrigation performed with saline.
Flow was adequate through the scope.
"""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_span(text: str, full_text: str, label: str, score: float = 0.9) -> Dict[str, Any]:
    """Create a span dict from text within a document."""
    start = full_text.find(text)
    if start == -1:
        raise ValueError(f"Text '{text}' not found in document")
    return {
        "start": start,
        "end": start + len(text),
        "label": label,
        "score": score,
        "source": "test",
    }


def veto_should_reject(span_text: str, label: str, context: str = "") -> bool:
    """
    Test whether the veto layer should reject (veto) a span.

    NOTE: The actual client-side veto runs in JavaScript (protectedVeto.js).
    This helper skips tests if the server-side API is incompatible.
    Use browser-based testing or `make audit-phi-client` for full validation.
    """
    if not HAS_COMPATIBLE_VETO:
        pytest.skip("Server-side veto module has incompatible API (token-based vs span-based)")

    full_text = context if context else f"Clinical note: {span_text} was observed."
    spans = [create_span(span_text, full_text, label)]

    # Apply veto - if span is removed, it was correctly vetoed
    result = apply_protected_veto(spans, full_text)
    return len(result) == 0


# =============================================================================
# TESTS
# =============================================================================

class TestLateralityAnatomyVeto:
    """Phase 2B: Laterality + anatomy phrases should not be redacted."""

    @pytest.mark.parametrize("fixture", MUST_NOT_REDACT_PATIENT[:11])
    def test_laterality_anatomy_vetoed(self, fixture):
        """Laterality + anatomy phrases should be vetoed."""
        text = fixture["text"]
        context = f"Findings: The {text} was unremarkable."
        assert veto_should_reject(text, "PATIENT", context), \
            f"'{text}' should have been vetoed but was kept"


class TestClinicalHeadingCommaVeto:
    """Phase 2C: Clinical heading comma phrases should not be redacted."""

    @pytest.mark.parametrize("fixture", MUST_NOT_REDACT_PATIENT[11:16])
    def test_clinical_heading_comma_vetoed(self, fixture):
        """Clinical heading comma phrases should be vetoed."""
        text = fixture["text"]
        context = f"Report:\n{text}\nResults pending."
        assert veto_should_reject(text, "PATIENT", context), \
            f"'{text}' should have been vetoed but was kept"


class TestSingleTokenClinicalVeto:
    """Phase 2D: Single-token clinical terms should not be redacted."""

    @pytest.mark.parametrize("fixture", MUST_NOT_REDACT_PATIENT[16:28])
    def test_single_token_clinical_vetoed(self, fixture):
        """Single-token clinical terms should be vetoed when not in patient context."""
        text = fixture["text"]
        context = f"Procedure note: {text} was observed during bronchoscopy."
        assert veto_should_reject(text, "PATIENT", context), \
            f"'{text}' should have been vetoed but was kept"


class TestVentSettingsIdVeto:
    """Phase 3A: Vent settings integers should not be redacted as IDs."""

    @pytest.mark.parametrize("fixture", MUST_NOT_REDACT_ID)
    def test_vent_settings_vetoed(self, fixture):
        """Vent settings numbers should be vetoed when in vent context."""
        text = fixture["text"]
        context = fixture.get("context", VENT_SETTINGS_SNIPPET)
        assert veto_should_reject(text, "ID", context), \
            f"'{text}' in vent context should have been vetoed but was kept"


class TestBalloonSizeDateVeto:
    """Phase 3B: Balloon sizes should not be redacted as dates."""

    @pytest.mark.parametrize("fixture", MUST_NOT_REDACT_DATE)
    def test_balloon_size_vetoed(self, fixture):
        """Balloon size patterns should be vetoed when in dilation context."""
        text = fixture["text"]
        context = fixture.get("context", BALLOON_DILATION_SNIPPET)
        assert veto_should_reject(text, "DATE", context), \
            f"'{text}' in balloon context should have been vetoed but was kept"


class TestMustRedactSafety:
    """Safety tests: These spans MUST be redacted."""

    @pytest.mark.parametrize("fixture", MUST_REDACT)
    def test_must_redact_kept(self, fixture):
        """True PHI should NOT be vetoed."""
        text = fixture["text"]
        label = fixture["label"]
        context = fixture.get("context", f"Record: {text}")

        # For safety tests, we expect the span to NOT be vetoed
        was_vetoed = veto_should_reject(text, label, context)
        assert not was_vetoed, \
            f"'{text}' ({label}) was incorrectly vetoed - this is PHI that should be redacted"


class TestFullTextSnippets:
    """Integration tests with realistic clinical text snippets."""

    def test_vent_settings_full_text(self):
        """Vent settings snippet should not have any false positive IDs."""
        if not HAS_COMPATIBLE_VETO:
            pytest.skip("Server-side veto module has incompatible API")

        # Create spans for all numbers in vent context
        spans = []
        for num in ["12", "400", "14", "60", "70", "17"]:
            try:
                spans.append(create_span(num, VENT_SETTINGS_SNIPPET, "ID"))
            except ValueError:
                continue

        result = apply_protected_veto(spans, VENT_SETTINGS_SNIPPET)
        assert len(result) == 0, \
            f"Expected all vent numbers to be vetoed, but {len(result)} spans remained"

    def test_elastography_full_text(self):
        """Elastography snippet should not have false positive PATIENT names."""
        if not HAS_COMPATIBLE_VETO:
            pytest.skip("Server-side veto module has incompatible API")

        # Test key phrases that might be false positives
        test_phrases = ["Elastography, First", "left adrenal", "Cytology, Flow"]
        spans = []
        for phrase in test_phrases:
            try:
                spans.append(create_span(phrase, ELASTOGRAPHY_SNIPPET, "PATIENT"))
            except ValueError:
                continue

        result = apply_protected_veto(spans, ELASTOGRAPHY_SNIPPET)
        assert len(result) == 0, \
            f"Expected clinical phrases to be vetoed, but {len(result)} spans remained"

    def test_balloon_dilation_full_text(self):
        """Balloon dilation snippet should not have false positive DATEs."""
        if not HAS_COMPATIBLE_VETO:
            pytest.skip("Server-side veto module has incompatible API")

        spans = [create_span("8/9/10", BALLOON_DILATION_SNIPPET, "DATE")]
        result = apply_protected_veto(spans, BALLOON_DILATION_SNIPPET)
        assert len(result) == 0, \
            "Expected balloon size to be vetoed, but it was kept as DATE"


# =============================================================================
# SMOKE TEST (matches phi-redactor.md checklist)
# =============================================================================

SMOKE_TEST_TEXT = """
Patient: John Smith, 65-year-old male
MRN: 12345678
DOB: 01/15/1960

Attending: Dr. Laura Brennan
Assistant: Dr. Miguel Santos (Fellow)

Procedure: Rigid bronchoscopy with EBUS-TBNA of stations 4R, 7, 11L.
The patient was intubated with size 8.0 ETT. Navigation performed
using Pentax EB-1990i scope. Follow-up in 1-2wks.

Pathology showed adenocarcinoma at station 7.
"""


class TestSmokeTest:
    """Smoke test matching the phi-redactor.md checklist."""

    def test_smoke_must_redact(self):
        """Patient PHI in smoke test should NOT be vetoed."""
        if not HAS_COMPATIBLE_VETO:
            pytest.skip("Server-side veto module has incompatible API")

        must_redact = ["John Smith", "12345678", "01/15/1960"]
        for text in must_redact:
            was_vetoed = veto_should_reject(text,
                "PATIENT" if text == "John Smith" else ("ID" if text == "12345678" else "DATE"),
                SMOKE_TEST_TEXT)
            assert not was_vetoed, f"'{text}' was incorrectly vetoed - should be redacted"

    def test_smoke_must_not_redact(self):
        """Clinical terms in smoke test SHOULD be vetoed."""
        if not HAS_COMPATIBLE_VETO:
            pytest.skip("Server-side veto module has incompatible API")

        must_not_redact = [
            ("4R", "PATIENT"),
            ("7", "ID"),
            ("11L", "PATIENT"),
            ("intubated", "PATIENT"),
            ("EB-1990i", "PATIENT"),
            ("1-2wks", "DATE"),
            ("adenocarcinoma", "PATIENT"),
        ]
        for text, label in must_not_redact:
            try:
                was_vetoed = veto_should_reject(text, label, SMOKE_TEST_TEXT)
                assert was_vetoed, f"'{text}' should have been vetoed but was kept"
            except ValueError:
                # Text not found in document - skip
                continue
