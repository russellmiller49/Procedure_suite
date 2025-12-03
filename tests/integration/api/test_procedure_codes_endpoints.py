"""Integration tests for the procedure_codes API endpoints.

Tests the full end-to-end coding workflow using FastAPI's TestClient,
including CodingService integration with mocked LLM advisor.
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
from modules.api.routes.procedure_codes import clear_procedure_stores
from modules.api.dependencies import (
    get_coding_service,
    get_procedure_store,
    reset_coding_service_cache,
    reset_procedure_store,
)
from modules.coder.application.coding_service import CodingService
from modules.coder.application.smart_hybrid_policy import HybridDecision
from modules.coder.adapters.persistence.inmemory_procedure_store import InMemoryProcedureStore
from config.settings import CoderSettings


# ============================================================================
# Mock implementations for testing
# ============================================================================


@dataclass
class MockProcedureInfo:
    """Mock procedure info."""
    code: str
    description: str = ""


class MockKnowledgeBaseRepository:
    """Mock KB repo for testing."""

    def __init__(self):
        self.version = "test_kb_v1"
        self._codes = {
            "31622": "Bronchoscopy with cell washing",
            "31624": "Bronchoalveolar lavage",
            "31628": "Transbronchial lung biopsy",
            "31652": "EBUS-TBNA 1-2 stations",
            "31653": "EBUS-TBNA 3+ stations",
            "31627": "Navigation bronchoscopy",
            "32555": "Thoracentesis with imaging",
        }

    def get_all_codes(self) -> set[str]:
        return set(self._codes.keys())

    def get_procedure_info(self, code: str) -> Optional[MockProcedureInfo]:
        if code in self._codes:
            return MockProcedureInfo(code=code, description=self._codes[code])
        return None

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
    # Reset stores before each test
    reset_procedure_store()
    reset_coding_service_cache()

    # Create a fresh in-memory store for this test
    test_store = InMemoryProcedureStore()

    # Create mock service with the configurable LLM advisor
    mock_service = create_mock_coding_service(mock_llm_advisor)

    # Use FastAPI's dependency_overrides for proper injection
    app.dependency_overrides[get_coding_service] = lambda: mock_service
    app.dependency_overrides[get_procedure_store] = lambda: test_store

    # Patch the NCCI/MER functions
    with patch("modules.coder.application.coding_service.apply_ncci_edits", mock_apply_ncci_edits), \
         patch("modules.coder.application.coding_service.apply_mer_rules", mock_apply_mer_rules):
        yield TestClient(app), mock_llm_advisor

    # Clean up after test
    app.dependency_overrides.clear()
    reset_procedure_store()


# ============================================================================
# Test Scenarios
# ============================================================================


class TestSuggestCodesEndpoint:
    """Tests for POST /procedures/{id}/codes/suggest."""

    def test_suggest_codes_happy_path_rules_only(self, client):
        """Test suggestion endpoint with rules-only mode."""
        test_client, _ = client

        response = test_client.post(
            "/api/v1/procedures/test-001/codes/suggest",
            json={
                "report_text": "EBUS-TBNA performed at station 4R. BAL collected from RML.",
                "use_llm": False,  # Rules only
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["procedure_id"] == "test-001"
        assert len(data["suggestions"]) >= 1
        assert data["processing_time_ms"] >= 0
        assert data["kb_version"] == "test_kb_v1"
        assert data["policy_version"] == "smart_hybrid_v2"

        # Check suggestions have required fields
        for suggestion in data["suggestions"]:
            assert "code" in suggestion
            assert "description" in suggestion
            assert "source" in suggestion
            assert "reasoning" in suggestion
            assert "suggestion_id" in suggestion
            assert "procedure_id" in suggestion

    def test_suggest_codes_with_llm_agreement(self, client):
        """Test suggestion with LLM agreeing with rules."""
        test_client, llm_advisor = client

        # Configure LLM to agree with rules
        llm_advisor.set_suggestions({"31652": 0.95})

        response = test_client.post(
            "/api/v1/procedures/test-002/codes/suggest",
            json={
                "report_text": "EBUS-TBNA performed at station 4R.",
                "use_llm": True,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Find the EBUS suggestion
        ebus_suggestion = next(
            (s for s in data["suggestions"] if s["code"] == "31652"),
            None
        )
        assert ebus_suggestion is not None

        # When rule and LLM agree, should be hybrid source with agreement decision
        assert ebus_suggestion["hybrid_decision"] == HybridDecision.ACCEPTED_AGREEMENT.value
        assert ebus_suggestion["source"] == "hybrid"

    def test_suggest_codes_llm_addition_verified(self, client):
        """Test LLM-only code that gets verified by keywords."""
        test_client, llm_advisor = client

        # LLM suggests a code that rules miss
        llm_advisor.set_suggestions({"31627": 0.92})

        response = test_client.post(
            "/api/v1/procedures/test-003/codes/suggest",
            json={
                "report_text": "Electromagnetic navigation bronchoscopy performed.",
                "use_llm": True,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Navigation code should be present
        nav_suggestion = next(
            (s for s in data["suggestions"] if s["code"] == "31627"),
            None
        )
        assert nav_suggestion is not None

        # Should have reasoning with provenance
        reasoning = nav_suggestion["reasoning"]
        assert reasoning["kb_version"] == "test_kb_v1"
        assert reasoning["policy_version"] == "smart_hybrid_v2"
        assert reasoning["keyword_map_version"] == "test_keyword_v1"
        assert reasoning["negation_detector_version"] == "test_negation_v1"

    def test_suggest_codes_malformed_request(self, client):
        """Test validation error on malformed request."""
        test_client, _ = client

        # Missing required field
        response = test_client.post(
            "/api/v1/procedures/test-004/codes/suggest",
            json={"use_llm": True},  # Missing report_text
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestGetSuggestionsEndpoint:
    """Tests for GET /procedures/{id}/codes/suggest."""

    def test_get_suggestions_after_post(self, client):
        """Test retrieving suggestions after POST."""
        test_client, _ = client

        # First POST to generate suggestions
        post_response = test_client.post(
            "/api/v1/procedures/test-010/codes/suggest",
            json={
                "report_text": "EBUS-TBNA at station 4R. BAL performed.",
                "use_llm": False,
            },
        )
        assert post_response.status_code == 200

        # Then GET to retrieve
        get_response = test_client.get("/api/v1/procedures/test-010/codes/suggest")
        assert get_response.status_code == 200

        suggestions = get_response.json()
        assert len(suggestions) >= 1

        # All suggestions should have full structure
        for suggestion in suggestions:
            assert "code" in suggestion
            assert "reasoning" in suggestion
            assert suggestion["procedure_id"] == "test-010"

    def test_get_suggestions_not_found(self, client):
        """Test 404 for unknown procedure."""
        test_client, _ = client

        response = test_client.get("/api/v1/procedures/unknown-proc/codes/suggest")
        assert response.status_code == 404
        assert "No suggestions found" in response.json()["detail"]


class TestReviewEndpoint:
    """Tests for POST /procedures/{id}/codes/review."""

    def test_accept_suggestion(self, client):
        """Test accepting a code suggestion."""
        test_client, _ = client

        # Generate suggestions first
        post_response = test_client.post(
            "/api/v1/procedures/test-020/codes/suggest",
            json={
                "report_text": "EBUS-TBNA performed at station 4R.",
                "use_llm": False,
            },
        )
        assert post_response.status_code == 200
        suggestions = post_response.json()["suggestions"]
        assert len(suggestions) >= 1

        suggestion_id = suggestions[0]["suggestion_id"]
        code = suggestions[0]["code"]

        # Accept the suggestion
        review_response = test_client.post(
            "/api/v1/procedures/test-020/codes/review",
            json={
                "suggestion_id": suggestion_id,
                "action": "accept",
                "reviewer_id": "dr-smith",
            },
        )

        assert review_response.status_code == 200
        review_data = review_response.json()

        assert review_data["action"] == "accept"
        assert review_data["final_code"] is not None
        assert review_data["final_code"]["code"] == code
        assert "accepted" in review_data["message"].lower()

    def test_reject_suggestion(self, client):
        """Test rejecting a code suggestion."""
        test_client, _ = client

        # Generate suggestions first
        post_response = test_client.post(
            "/api/v1/procedures/test-021/codes/suggest",
            json={
                "report_text": "BAL performed.",
                "use_llm": False,
            },
        )
        assert post_response.status_code == 200
        suggestions = post_response.json()["suggestions"]
        assert len(suggestions) >= 1

        suggestion_id = suggestions[0]["suggestion_id"]

        # Reject the suggestion
        review_response = test_client.post(
            "/api/v1/procedures/test-021/codes/review",
            json={
                "suggestion_id": suggestion_id,
                "action": "reject",
                "reviewer_id": "dr-jones",
                "notes": "Not actually performed",
            },
        )

        assert review_response.status_code == 200
        review_data = review_response.json()

        assert review_data["action"] == "reject"
        assert review_data["final_code"] is None
        assert "rejected" in review_data["message"].lower()

    def test_modify_suggestion(self, client):
        """Test modifying a code suggestion."""
        test_client, _ = client

        # Generate suggestions first
        post_response = test_client.post(
            "/api/v1/procedures/test-022/codes/suggest",
            json={
                "report_text": "EBUS performed at station 4R.",
                "use_llm": False,
            },
        )
        assert post_response.status_code == 200
        suggestions = post_response.json()["suggestions"]
        assert len(suggestions) >= 1

        suggestion_id = suggestions[0]["suggestion_id"]

        # Modify to a different code
        review_response = test_client.post(
            "/api/v1/procedures/test-022/codes/review",
            json={
                "suggestion_id": suggestion_id,
                "action": "modify",
                "reviewer_id": "dr-wilson",
                "modified_code": "31653",
                "modified_description": "EBUS-TBNA 3+ stations",
                "notes": "Actually sampled 4 stations",
            },
        )

        assert review_response.status_code == 200
        review_data = review_response.json()

        assert review_data["action"] == "modify"
        assert review_data["final_code"] is not None
        assert review_data["final_code"]["code"] == "31653"
        assert review_data["final_code"]["source"] == "manual"

    def test_invalid_action(self, client):
        """Test validation error for invalid action."""
        test_client, _ = client

        response = test_client.post(
            "/api/v1/procedures/test-023/codes/review",
            json={
                "suggestion_id": "some-id",
                "action": "invalid_action",
                "reviewer_id": "dr-smith",
            },
        )

        assert response.status_code == 400
        assert "Invalid action" in response.json()["detail"]

    def test_suggestion_not_found(self, client):
        """Test 404 for unknown suggestion."""
        test_client, _ = client

        # Create some suggestions first
        test_client.post(
            "/api/v1/procedures/test-024/codes/suggest",
            json={"report_text": "BAL performed.", "use_llm": False},
        )

        response = test_client.post(
            "/api/v1/procedures/test-024/codes/review",
            json={
                "suggestion_id": "nonexistent-id",
                "action": "accept",
                "reviewer_id": "dr-smith",
            },
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestFinalCodesEndpoint:
    """Tests for GET /procedures/{id}/codes/final."""

    def test_final_codes_after_accept(self, client):
        """Test final codes are populated after accepting suggestions."""
        test_client, _ = client

        # Generate and accept a suggestion
        post_response = test_client.post(
            "/api/v1/procedures/test-030/codes/suggest",
            json={
                "report_text": "EBUS-TBNA at station 4R. BAL performed.",
                "use_llm": False,
            },
        )
        assert post_response.status_code == 200
        suggestions = post_response.json()["suggestions"]

        # Accept all suggestions
        for suggestion in suggestions:
            test_client.post(
                "/api/v1/procedures/test-030/codes/review",
                json={
                    "suggestion_id": suggestion["suggestion_id"],
                    "action": "accept",
                    "reviewer_id": "dr-smith",
                },
            )

        # Get final codes
        final_response = test_client.get("/api/v1/procedures/test-030/codes/final")
        assert final_response.status_code == 200

        final_codes = final_response.json()
        assert len(final_codes) == len(suggestions)

        # All final codes should have reasoning preserved
        for final_code in final_codes:
            assert "reasoning" in final_code
            assert final_code["reasoning"]["kb_version"] == "test_kb_v1"

    def test_final_codes_empty_before_review(self, client):
        """Test final codes are empty before review."""
        test_client, _ = client

        # Generate suggestions but don't review
        test_client.post(
            "/api/v1/procedures/test-031/codes/suggest",
            json={"report_text": "BAL performed.", "use_llm": False},
        )

        # Get final codes - should be empty
        final_response = test_client.get("/api/v1/procedures/test-031/codes/final")
        assert final_response.status_code == 200
        assert final_response.json() == []


class TestManualCodeEndpoint:
    """Tests for POST /procedures/{id}/codes/manual."""

    def test_add_manual_code(self, client):
        """Test adding a manual code."""
        test_client, _ = client

        response = test_client.post(
            "/api/v1/procedures/test-040/codes/manual",
            json={
                "code": "31622",
                "description": "Diagnostic bronchoscopy",
                "reviewer_id": "dr-smith",
                "notes": "Added for completeness",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["final_code"]["code"] == "31622"
        assert data["final_code"]["source"] == "manual"
        assert data["final_code"]["reasoning"]["confidence"] == 1.0

        # Should appear in final codes
        final_response = test_client.get("/api/v1/procedures/test-040/codes/final")
        assert len(final_response.json()) == 1
        assert final_response.json()[0]["code"] == "31622"


class TestMetricsEndpoint:
    """Tests for GET /procedures/{id}/codes/metrics."""

    def test_metrics_after_workflow(self, client):
        """Test metrics calculation after full workflow."""
        test_client, _ = client

        # Generate suggestions
        post_response = test_client.post(
            "/api/v1/procedures/test-050/codes/suggest",
            json={
                "report_text": "EBUS-TBNA at station 4R. BAL performed.",
                "use_llm": False,
            },
        )
        suggestions = post_response.json()["suggestions"]

        # Accept first, reject rest
        for i, suggestion in enumerate(suggestions):
            action = "accept" if i == 0 else "reject"
            test_client.post(
                "/api/v1/procedures/test-050/codes/review",
                json={
                    "suggestion_id": suggestion["suggestion_id"],
                    "action": action,
                    "reviewer_id": "dr-smith",
                },
            )

        # Add a manual code
        test_client.post(
            "/api/v1/procedures/test-050/codes/manual",
            json={
                "code": "99999",
                "description": "Test manual code",
                "reviewer_id": "dr-smith",
            },
        )

        # Get metrics
        metrics_response = test_client.get("/api/v1/procedures/test-050/codes/metrics")
        assert metrics_response.status_code == 200

        metrics = metrics_response.json()
        assert metrics["procedure_id"] == "test-050"
        assert metrics["total_suggestions"] == len(suggestions)
        assert metrics["accepted"] == 1
        assert metrics["rejected"] == len(suggestions) - 1
        assert metrics["manual_additions"] == 1
        assert metrics["final_codes_count"] == 2  # 1 accepted + 1 manual
        assert "kb_version" in metrics
        assert "policy_version" in metrics


class TestFullWorkflow:
    """End-to-end workflow tests."""

    def test_complete_coding_workflow(self, client):
        """Test complete suggest → review → final workflow."""
        test_client, llm_advisor = client

        # Configure LLM to suggest additional codes
        llm_advisor.set_suggestions({"31652": 0.95, "31627": 0.88})

        # Step 1: Generate suggestions
        suggest_response = test_client.post(
            "/api/v1/procedures/test-100/codes/suggest",
            json={
                "report_text": """
                PROCEDURE NOTE

                Indication: Lung mass, suspected malignancy

                Procedure: Flexible bronchoscopy with EBUS-TBNA and navigation

                Findings:
                - EBUS-TBNA performed at lymph node stations 4R and 7
                - Electromagnetic navigation used to access peripheral lesion
                - Samples sent to pathology

                Impression: Successful bronchoscopy with staging and biopsy
                """,
                "use_llm": True,
            },
        )

        assert suggest_response.status_code == 200
        suggest_data = suggest_response.json()

        assert len(suggest_data["suggestions"]) >= 1
        assert suggest_data["kb_version"] == "test_kb_v1"

        # Step 2: Get pending suggestions
        pending_response = test_client.get("/api/v1/procedures/test-100/codes/suggest")
        assert pending_response.status_code == 200
        pending = pending_response.json()
        assert len(pending) == len(suggest_data["suggestions"])

        # Step 3: Review suggestions
        accepted_codes = []
        for suggestion in pending[:2]:  # Accept first 2
            review_response = test_client.post(
                "/api/v1/procedures/test-100/codes/review",
                json={
                    "suggestion_id": suggestion["suggestion_id"],
                    "action": "accept",
                    "reviewer_id": "dr-pulmonologist",
                },
            )
            assert review_response.status_code == 200
            accepted_codes.append(suggestion["code"])

        # Step 4: Check final codes
        final_response = test_client.get("/api/v1/procedures/test-100/codes/final")
        assert final_response.status_code == 200

        final_codes = final_response.json()
        assert len(final_codes) == 2
        final_code_values = [fc["code"] for fc in final_codes]
        for code in accepted_codes:
            assert code in final_code_values

        # Step 5: Check all final codes have reasoning with provenance
        for final_code in final_codes:
            reasoning = final_code["reasoning"]
            assert reasoning["kb_version"] == "test_kb_v1"
            assert reasoning["policy_version"] == "smart_hybrid_v2"

        # Step 6: Check review history
        reviews_response = test_client.get("/api/v1/procedures/test-100/codes/reviews")
        assert reviews_response.status_code == 200
        reviews = reviews_response.json()
        assert len(reviews) == 2

        # Step 7: Check metrics
        metrics_response = test_client.get("/api/v1/procedures/test-100/codes/metrics")
        assert metrics_response.status_code == 200
        metrics = metrics_response.json()
        assert metrics["accepted"] == 2
        assert metrics["final_codes_count"] == 2

    def test_rules_only_mode_works_without_llm(self, client):
        """Verify rules_only mode doesn't require LLM."""
        test_client, llm_advisor = client

        # Even with LLM configured to return codes, use_llm=False should ignore it
        llm_advisor.set_suggestions({"99999": 0.99})  # Invalid code

        response = test_client.post(
            "/api/v1/procedures/test-101/codes/suggest",
            json={
                "report_text": "BAL performed. Thoracentesis with ultrasound guidance.",
                "use_llm": False,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Should have rule-based codes only
        codes = [s["code"] for s in data["suggestions"]]
        assert "99999" not in codes  # LLM code should not appear

        # All suggestions should be from rules
        for suggestion in data["suggestions"]:
            assert suggestion["source"] in ("rule", "hybrid")
