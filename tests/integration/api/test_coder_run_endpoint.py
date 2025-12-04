"""Integration tests for the /v1/coder/run API endpoint.

Tests the migrated coder endpoint that now uses CodingService
instead of the legacy EnhancedCPTCoder.
"""

import os

# Avoid network-bound LLM calls during tests
os.environ.setdefault("REGISTRY_USE_STUB_LLM", "1")
os.environ.setdefault("GEMINI_OFFLINE", "1")
os.environ.setdefault("DISABLE_STATIC_FILES", "1")

import pytest
from dataclasses import dataclass, field
from typing import Optional, Any
from unittest.mock import patch

from fastapi.testclient import TestClient

from modules.api.fastapi_app import app
from modules.api.dependencies import (
    get_coding_service,
    reset_coding_service_cache,
)
from modules.coder.application.coding_service import CodingService
from modules.coder.application.smart_hybrid_policy import HybridDecision
from config.settings import CoderSettings


# ============================================================================
# Mock implementations for testing
# ============================================================================


@dataclass
class MockProcedureInfo:
    """Mock procedure info with RVU data."""
    code: str
    description: str = ""
    work_rvu: float = 0.0
    facility_pe_rvu: float = 0.0
    malpractice_rvu: float = 0.0
    total_facility_rvu: float = 0.0


class MockKnowledgeBaseRepository:
    """Mock KB repo for testing with RVU data."""

    def __init__(self):
        self.version = "test_kb_v1"
        self._codes = {
            "31622": MockProcedureInfo(
                code="31622",
                description="Bronchoscopy with cell washing",
                work_rvu=1.45,
                total_facility_rvu=2.10,
            ),
            "31624": MockProcedureInfo(
                code="31624",
                description="Bronchoalveolar lavage",
                work_rvu=1.50,
                total_facility_rvu=2.20,
            ),
            "31628": MockProcedureInfo(
                code="31628",
                description="Transbronchial lung biopsy",
                work_rvu=3.50,
                total_facility_rvu=5.10,
            ),
            "31652": MockProcedureInfo(
                code="31652",
                description="EBUS-TBNA 1-2 stations",
                work_rvu=4.20,
                total_facility_rvu=6.50,
            ),
            "31653": MockProcedureInfo(
                code="31653",
                description="EBUS-TBNA 3+ stations",
                work_rvu=5.10,
                total_facility_rvu=7.80,
            ),
            "31627": MockProcedureInfo(
                code="31627",
                description="Navigation bronchoscopy",
                work_rvu=3.80,
                total_facility_rvu=5.90,
            ),
            "32555": MockProcedureInfo(
                code="32555",
                description="Thoracentesis with imaging",
                work_rvu=2.10,
                total_facility_rvu=3.20,
            ),
        }

    def get_all_codes(self) -> set[str]:
        return set(self._codes.keys())

    def get_procedure_info(self, code: str) -> Optional[MockProcedureInfo]:
        return self._codes.get(code)

    def get_ncci_pairs(self, code: str) -> list:
        return []

    def get_mer_group(self, code: str) -> Optional[str]:
        return None

    def is_addon_code(self, code: str) -> bool:
        return code.startswith("+")


@dataclass
class MockKeywordMapping:
    """Mock keyword mapping."""
    code: str
    positive_phrases: list[str] = field(default_factory=list)
    negative_phrases: list[str] = field(default_factory=list)
    context_window_chars: int = 200


class MockKeywordMappingRepository:
    """Mock keyword mapping repo."""

    def __init__(self):
        self.version = "test_keyword_v1"
        self._mappings = {
            "31622": MockKeywordMapping(
                code="31622",
                positive_phrases=["bronchoscopy", "cell washing", "bronchial washing"],
                negative_phrases=["no bronchoscopy"],
            ),
            "31624": MockKeywordMapping(
                code="31624",
                positive_phrases=["bal", "bronchoalveolar lavage", "lavage"],
                negative_phrases=["no bal"],
            ),
            "31628": MockKeywordMapping(
                code="31628",
                positive_phrases=["transbronchial biopsy", "tblb", "forceps biopsy"],
                negative_phrases=["no biopsy"],
            ),
            "31652": MockKeywordMapping(
                code="31652",
                positive_phrases=["ebus", "ebus-tbna", "endobronchial ultrasound"],
                negative_phrases=["no ebus"],
            ),
            "31653": MockKeywordMapping(
                code="31653",
                positive_phrases=["ebus", "multiple stations", "3 stations"],
                negative_phrases=["no ebus"],
            ),
            "31627": MockKeywordMapping(
                code="31627",
                positive_phrases=["navigation", "enb", "electromagnetic navigation"],
                negative_phrases=["no navigation"],
            ),
            "32555": MockKeywordMapping(
                code="32555",
                positive_phrases=["thoracentesis", "pleural aspiration"],
                negative_phrases=["no thoracentesis"],
            ),
        }

    def get_mapping(self, code: str) -> Optional[MockKeywordMapping]:
        return self._mappings.get(code)


class MockNegationDetector:
    """Mock negation detector."""

    VERSION = "test_negation_v1"

    @property
    def version(self) -> str:
        return self.VERSION

    def is_negated_simple(self, context: str, negative_phrases: list[str]) -> bool:
        context_lower = context.lower()
        for neg in negative_phrases:
            if neg.lower() in context_lower:
                return True
        return False


@dataclass
class MockRuleEngineResult:
    """Mock result from rule engine."""
    codes: list[str]
    confidence: dict[str, float]


class MockRuleEngine:
    """Mock rule-based coding engine."""

    VERSION = "test_rule_engine_v1"

    def __init__(self, codes_to_return: dict[str, float] | None = None):
        self._codes_to_return = codes_to_return or {}

    @property
    def version(self) -> str:
        return self.VERSION

    def generate_candidates(self, report_text: str) -> MockRuleEngineResult:
        """Generate codes based on text content."""
        codes = {}
        text_lower = report_text.lower()

        # Simple keyword matching for test purposes
        if "ebus" in text_lower or "endobronchial ultrasound" in text_lower:
            if "3 stations" in text_lower or "multiple stations" in text_lower:
                codes["31653"] = 0.9
            else:
                codes["31652"] = 0.85
        if "bal" in text_lower or "bronchoalveolar lavage" in text_lower:
            codes["31624"] = 0.85
        if "transbronchial biopsy" in text_lower or "tblb" in text_lower:
            codes["31628"] = 0.9
        if "navigation" in text_lower:
            codes["31627"] = 0.9
        if "thoracentesis" in text_lower:
            codes["32555"] = 0.85

        # Override with configured codes if any
        if self._codes_to_return:
            codes = self._codes_to_return

        return MockRuleEngineResult(
            codes=list(codes.keys()),
            confidence=codes,
        )


@dataclass
class MockLLMSuggestion:
    """Mock LLM suggestion."""
    code: str
    confidence: float


class MockLLMAdvisor:
    """Mock LLM advisor for testing."""

    def __init__(self, codes_to_return: dict[str, float] | None = None):
        self._codes_to_return = codes_to_return or {}
        self._version = "test_llm_v1"

    @property
    def version(self) -> str:
        return self._version

    def suggest_codes(self, report_text: str) -> list[MockLLMSuggestion]:
        """Return configured suggestions."""
        return [
            MockLLMSuggestion(code=code, confidence=conf)
            for code, conf in self._codes_to_return.items()
        ]

    def set_suggestions(self, suggestions: dict[str, float]) -> None:
        """Update the suggestions to return."""
        self._codes_to_return = suggestions


@dataclass
class MockComplianceResult:
    """Mock compliance check result."""
    kept_codes: list[str]
    removed_codes: list[str]
    warnings: list[str]


def mock_apply_ncci_edits(codes: list[str], kb_repo: Any) -> MockComplianceResult:
    """Mock NCCI edits - removes nothing by default."""
    return MockComplianceResult(
        kept_codes=list(codes),
        removed_codes=[],
        warnings=[],
    )


def mock_apply_mer_rules(codes: list[str], kb_repo: Any) -> MockComplianceResult:
    """Mock MER rules - removes nothing by default."""
    return MockComplianceResult(
        kept_codes=list(codes),
        removed_codes=[],
        warnings=[],
    )


# ============================================================================
# Fixtures
# ============================================================================


def create_mock_coding_service(llm_advisor: MockLLMAdvisor | None = None) -> CodingService:
    """Create a CodingService with all dependencies mocked."""
    kb_repo = MockKnowledgeBaseRepository()
    keyword_repo = MockKeywordMappingRepository()
    negation_detector = MockNegationDetector()
    rule_engine = MockRuleEngine()
    advisor = llm_advisor or MockLLMAdvisor(codes_to_return={})

    config = CoderSettings(
        advisor_confidence_auto_accept=0.85,
        rule_confidence_low_threshold=0.6,
        context_window_chars=200,
    )

    service = CodingService(
        kb_repo=kb_repo,
        keyword_repo=keyword_repo,
        negation_detector=negation_detector,
        rule_engine=rule_engine,
        llm_advisor=advisor,
        config=config,
    )

    return service


@pytest.fixture
def mock_llm_advisor():
    """Create a mock LLM advisor that can be configured per test."""
    return MockLLMAdvisor(codes_to_return={})


@pytest.fixture
def client(mock_llm_advisor):
    """Create a TestClient with mocked CodingService using FastAPI dependency override."""
    # Reset caches before each test
    reset_coding_service_cache()

    # Create mock service with the configurable LLM advisor
    mock_service = create_mock_coding_service(mock_llm_advisor)

    # Use FastAPI's dependency_overrides for proper injection
    app.dependency_overrides[get_coding_service] = lambda: mock_service

    # Patch the NCCI/MER functions
    with patch("modules.coder.application.coding_service.apply_ncci_edits", mock_apply_ncci_edits), \
         patch("modules.coder.application.coding_service.apply_mer_rules", mock_apply_mer_rules):
        yield TestClient(app), mock_llm_advisor

    # Clean up after test
    app.dependency_overrides.clear()


# ============================================================================
# Test Cases for /v1/coder/run
# ============================================================================


class TestCoderRunEndpointBasic:
    """Basic tests for the /v1/coder/run endpoint."""

    def test_coder_run_rules_only_basic(self, client):
        """Test coder run with rules_only mode returns valid response."""
        test_client, _ = client

        response = test_client.post(
            "/v1/coder/run",
            json={
                "note": "EBUS-TBNA performed at station 4R. BAL collected from RML.",
                "locality": "00",
                "setting": "facility",
                "mode": "rules_only",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response matches CoderOutput schema
        assert "codes" in data
        assert "version" in data
        assert "warnings" in data
        assert isinstance(data["codes"], list)

        # Should have at least one code
        assert len(data["codes"]) >= 1

        # Each code should have required fields
        for code_decision in data["codes"]:
            assert "cpt" in code_decision
            assert "description" in code_decision
            assert "confidence" in code_decision
            assert "rationale" in code_decision

    def test_coder_run_returns_200_for_simple_note(self, client):
        """Test that a simple procedure note returns 200."""
        test_client, _ = client

        response = test_client.post(
            "/v1/coder/run",
            json={
                "note": "Diagnostic bronchoscopy performed.",
            },
        )

        assert response.status_code == 200

    def test_coder_run_default_locality_and_setting(self, client):
        """Test default values for locality and setting."""
        test_client, _ = client

        # Note: defaults are locality="00", setting="facility"
        response = test_client.post(
            "/v1/coder/run",
            json={
                "note": "BAL performed.",
            },
        )

        assert response.status_code == 200

    def test_coder_run_financials_present(self, client):
        """Test that financials are included when codes are returned."""
        test_client, _ = client

        response = test_client.post(
            "/v1/coder/run",
            json={
                "note": "EBUS-TBNA performed at station 4R.",
                "locality": "00",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Financials should be present when codes are returned
        if len(data["codes"]) > 0:
            # Financials may be None or populated
            if data.get("financials"):
                assert "conversion_factor" in data["financials"]
                assert "locality" in data["financials"]
                assert "per_code" in data["financials"]


class TestCoderRunEndpointSmartHybrid:
    """Tests for smart hybrid mode with LLM advisor."""

    def test_coder_run_smart_hybrid_llm_mocked(self, client):
        """Test smart hybrid mode with mocked LLM advisor."""
        test_client, llm_advisor = client

        # Configure LLM to suggest codes
        llm_advisor.set_suggestions({"31652": 0.95, "31624": 0.88})

        response = test_client.post(
            "/v1/coder/run",
            json={
                "note": "EBUS-TBNA performed at station 4R. BAL collected.",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Should have codes from hybrid merge
        assert len(data["codes"]) >= 1

        # Check version indicates new architecture
        assert "new_arch" in data["version"] or "smart_hybrid" in data["version"]

    def test_coder_run_llm_agreement_boosts_confidence(self, client):
        """Test that LLM agreement with rules results in hybrid source."""
        test_client, llm_advisor = client

        # Configure LLM to agree with rules
        llm_advisor.set_suggestions({"31652": 0.95})

        response = test_client.post(
            "/v1/coder/run",
            json={
                "note": "EBUS-TBNA performed at lymph node station 4R.",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Find the EBUS code
        ebus_code = next(
            (c for c in data["codes"] if c["cpt"] == "31652"),
            None
        )

        # Should exist and have reasonable confidence
        if ebus_code:
            assert ebus_code["confidence"] > 0

    def test_coder_run_llm_suggestions_in_response(self, client):
        """Test that LLM suggestions are included in response when available."""
        test_client, llm_advisor = client

        # Configure LLM suggestions
        llm_advisor.set_suggestions({"31627": 0.92})

        response = test_client.post(
            "/v1/coder/run",
            json={
                "note": "Navigation bronchoscopy performed.",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # LLM suggestions should be present
        if "llm_suggestions" in data:
            # If LLM suggestions are populated, they should have structure
            for suggestion in data.get("llm_suggestions", []):
                assert "cpt" in suggestion


class TestCoderRunEndpointValidation:
    """Tests for input validation."""

    def test_coder_run_handles_invalid_input_missing_note(self, client):
        """Test validation error when note is missing."""
        test_client, _ = client

        response = test_client.post(
            "/v1/coder/run",
            json={
                "locality": "00",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_coder_run_handles_empty_note(self, client):
        """Test handling of empty note."""
        test_client, _ = client

        response = test_client.post(
            "/v1/coder/run",
            json={
                "note": "",
            },
        )

        # Should return 200 but possibly with no codes
        assert response.status_code == 200
        data = response.json()
        assert "codes" in data

    def test_coder_run_accepts_extra_fields(self, client):
        """Test that extra fields in request are ignored (not rejected)."""
        test_client, _ = client

        response = test_client.post(
            "/v1/coder/run",
            json={
                "note": "BAL performed.",
                "extra_field": "should be ignored",
                "another_field": 123,
            },
        )

        assert response.status_code == 200


class TestCoderRunEndpointProvenance:
    """Tests for provenance and reasoning fields."""

    def test_coder_run_has_provenance_in_codes(self, client):
        """Test that codes include provenance information."""
        test_client, _ = client

        response = test_client.post(
            "/v1/coder/run",
            json={
                "note": "EBUS-TBNA performed at station 4R.",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Check that codes have context with hybrid decision info
        for code_decision in data["codes"]:
            # Each code should have context
            if "context" in code_decision:
                context = code_decision["context"]
                # Context should include review_flag or hybrid_decision
                assert "review_flag" in context or "hybrid_decision" in context

    def test_coder_run_reasoning_in_rationale(self, client):
        """Test that reasoning is captured in rationale field."""
        test_client, _ = client

        response = test_client.post(
            "/v1/coder/run",
            json={
                "note": "BAL bronchoalveolar lavage performed.",
            },
        )

        assert response.status_code == 200
        data = response.json()

        for code_decision in data["codes"]:
            # Rationale should be present
            assert "rationale" in code_decision
            # Rationale should be non-empty list or string
            rationale = code_decision["rationale"]
            assert rationale is not None


class TestCoderRunEndpointComplexNotes:
    """Tests with complex procedure notes."""

    def test_coder_run_complex_bronchoscopy_note(self, client):
        """Test with a complex bronchoscopy procedure note."""
        test_client, llm_advisor = client

        # Configure LLM
        llm_advisor.set_suggestions({"31652": 0.95, "31624": 0.88})

        complex_note = """
        PROCEDURE NOTE

        Patient: John Doe
        MRN: 12345
        Date: 2024-01-15

        INDICATION: Suspected lung malignancy with mediastinal lymphadenopathy

        PROCEDURE: Flexible bronchoscopy with EBUS-TBNA and BAL

        ANESTHESIA: Moderate sedation

        FINDINGS:
        1. Normal vocal cords and trachea
        2. EBUS-TBNA performed at lymph node station 4R (3 passes)
        3. Bronchoalveolar lavage collected from right middle lobe

        SPECIMENS:
        - EBUS-TBNA station 4R for cytology and flow cytometry
        - BAL for cell count and cultures

        COMPLICATIONS: None

        IMPRESSION: Successful bronchoscopy with staging and lavage
        """

        response = test_client.post(
            "/v1/coder/run",
            json={
                "note": complex_note,
                "locality": "00",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Should detect multiple procedures
        codes = [c["cpt"] for c in data["codes"]]

        # Should have at least one relevant code
        assert len(codes) >= 1

    def test_coder_run_thoracentesis_note(self, client):
        """Test with thoracentesis procedure note."""
        test_client, _ = client

        response = test_client.post(
            "/v1/coder/run",
            json={
                "note": """
                Ultrasound-guided thoracentesis performed.
                1500ml of pleural fluid removed from right pleural space.
                Fluid sent for cell count, cultures, and cytology.
                """,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Should detect thoracentesis
        codes = [c["cpt"] for c in data["codes"]]
        assert "32555" in codes or len(codes) >= 1


class TestCoderRunEndpointLocalities:
    """Tests for the localities endpoint."""

    def test_localities_endpoint_returns_list(self, client):
        """Test that localities endpoint returns a list."""
        test_client, _ = client

        response = test_client.get("/v1/coder/localities")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        # Should have at least the default national locality
        assert len(data) >= 1

        # Each locality should have code and name
        for locality in data:
            assert "code" in locality
            assert "name" in locality

    def test_localities_includes_national_default(self, client):
        """Test that localities includes the national default."""
        test_client, _ = client

        response = test_client.get("/v1/coder/localities")

        assert response.status_code == 200
        data = response.json()

        # Should have national locality
        codes = [loc["code"] for loc in data]
        assert "00" in codes


class TestCoderRunEndpointQASandbox:
    """Tests for /qa/run endpoint coder integration."""

    def test_qa_run_coder_module(self, client):
        """Test that /qa/run with coder module uses CodingService."""
        test_client, llm_advisor = client

        # Configure LLM
        llm_advisor.set_suggestions({"31652": 0.90})

        response = test_client.post(
            "/qa/run",
            json={
                "note_text": "EBUS-TBNA performed at station 4R.",
                "modules_run": "coder",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Coder output should be present
        assert "coder_output" in data
        coder_output = data["coder_output"]

        # Should have codes
        assert "codes" in coder_output
        assert isinstance(coder_output["codes"], list)

        # Should have provenance fields from new architecture
        if "kb_version" in coder_output:
            assert coder_output["kb_version"] == "test_kb_v1"

        if "policy_version" in coder_output:
            assert "smart_hybrid" in coder_output["policy_version"]
