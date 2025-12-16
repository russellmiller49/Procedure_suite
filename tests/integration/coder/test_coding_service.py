"""Integration tests for the CodingService.

Tests the end-to-end coding pipeline including rule-based coding,
LLM advisor, hybrid merge, and compliance rules.
"""

import pytest
from dataclasses import dataclass, field
from typing import Optional, Any

from modules.coder.application.coding_service import CodingService
from modules.coder.application.smart_hybrid_policy import HybridDecision
from config.settings import CoderSettings


# ============================================================================
# Mock implementations
# ============================================================================


@dataclass
class MockProcedureInfo:
    """Mock procedure info."""

    code: str
    description: str = ""


class MockKnowledgeBaseRepository:
    """Mock KB repo."""

    def __init__(self):
        self.version = "mock_kb_v1"
        self._codes = {
            "31622": "Bronchoscopy with BAL",
            "31623": "Bronchoscopy with brushing",
            "31624": "Bronchoscopy with biopsy",
            "31652": "EBUS-TBNA",
            "31653": "EBUS-TBNA additional sites",
        }

    def get_all_codes(self) -> list[str]:
        return list(self._codes.keys())

    def get_procedure_info(self, code: str) -> Optional[MockProcedureInfo]:
        if code in self._codes:
            return MockProcedureInfo(code=code, description=self._codes[code])
        return None

    def get_ncci_pairs(self, code: str) -> list[tuple[str, int]]:
        """Return NCCI pairs for a code. Empty for mock."""
        return []

    def get_mer_bundles(self, code: str) -> list[str]:
        """Return MER bundles for a code. Empty for mock."""
        return []


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
        self.version = "mock_keyword_v1"
        self._mappings = {
            "31622": MockKeywordMapping(
                code="31622",
                positive_phrases=["bronchoalveolar lavage", "bal"],
                negative_phrases=["no bal"],
            ),
            "31624": MockKeywordMapping(
                code="31624",
                positive_phrases=["biopsy", "tblb"],
                negative_phrases=["no biopsy"],
            ),
            "31652": MockKeywordMapping(
                code="31652",
                positive_phrases=["ebus", "tbna"],
                negative_phrases=["no ebus"],
            ),
        }

    def get_mapping(self, code: str) -> Optional[MockKeywordMapping]:
        return self._mappings.get(code)


class MockNegationDetector:
    """Mock negation detector."""

    def __init__(self):
        self.version = "mock_negation_v1"

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

    def __init__(self, codes_to_return: dict[str, float] | None = None):
        self._codes_to_return = codes_to_return or {}

    def generate_candidates(self, report_text: str) -> MockRuleEngineResult:
        """Generate codes based on configured return values."""
        return MockRuleEngineResult(
            codes=list(self._codes_to_return.keys()),
            confidence=self._codes_to_return,
        )


@dataclass
class MockLLMSuggestion:
    """Mock LLM suggestion."""

    code: str
    confidence: float


class MockLLMAdvisor:
    """Mock LLM advisor."""

    def __init__(self, codes_to_return: dict[str, float] | None = None):
        self._codes_to_return = codes_to_return or {}
        self.version = "mock_llm_v1"

    def suggest_codes(self, report_text: str) -> list[MockLLMSuggestion]:
        """Return configured suggestions."""
        return [
            MockLLMSuggestion(code=code, confidence=conf)
            for code, conf in self._codes_to_return.items()
        ]


# ============================================================================
# Mock NCCI/MER functions
# ============================================================================


@dataclass
class MockComplianceResult:
    """Mock compliance check result."""

    kept_codes: list[str]
    removed_codes: list[str]
    warnings: list[str]


def mock_apply_ncci_edits(
    codes: list[str], kb_repo: Any
) -> MockComplianceResult:
    """Mock NCCI edits - removes nothing by default."""
    return MockComplianceResult(
        kept_codes=list(codes),
        removed_codes=[],
        warnings=[],
    )


def mock_apply_mer_rules(
    codes: list[str], kb_repo: Any
) -> MockComplianceResult:
    """Mock MER rules - removes nothing by default."""
    return MockComplianceResult(
        kept_codes=list(codes),
        removed_codes=[],
        warnings=[],
    )


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def kb_repo() -> MockKnowledgeBaseRepository:
    return MockKnowledgeBaseRepository()


@pytest.fixture
def keyword_repo() -> MockKeywordMappingRepository:
    return MockKeywordMappingRepository()


@pytest.fixture
def negation_detector() -> MockNegationDetector:
    return MockNegationDetector()


@pytest.fixture
def config() -> CoderSettings:
    return CoderSettings(
        advisor_confidence_auto_accept=0.85,
        rule_confidence_low_threshold=0.6,
        context_window_chars=200,
    )


@pytest.fixture
def rule_engine() -> MockRuleEngine:
    return MockRuleEngine(codes_to_return={"31622": 0.9, "31624": 0.85})


@pytest.fixture
def llm_advisor() -> MockLLMAdvisor:
    return MockLLMAdvisor(codes_to_return={"31622": 0.92, "31652": 0.88})


# ============================================================================
# Integration tests
# ============================================================================


class TestCodingServicePipeline:
    """Test the full coding pipeline."""

    def test_generate_suggestions_with_agreement(
        self,
        kb_repo: MockKnowledgeBaseRepository,
        keyword_repo: MockKeywordMappingRepository,
        negation_detector: MockNegationDetector,
        config: CoderSettings,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test pipeline when rule engine and LLM agree."""
        # Mock the compliance functions - must patch where they're imported/used
        import modules.coder.application.coding_service as coding_service_mod
        monkeypatch.setattr(coding_service_mod, "apply_ncci_edits", mock_apply_ncci_edits)
        monkeypatch.setattr(coding_service_mod, "apply_mer_rules", mock_apply_mer_rules)

        rule_engine = MockRuleEngine(codes_to_return={"31622": 0.9})
        llm_advisor = MockLLMAdvisor(codes_to_return={"31622": 0.95})

        service = CodingService(
            kb_repo=kb_repo,
            keyword_repo=keyword_repo,
            negation_detector=negation_detector,
            rule_engine=rule_engine,
            llm_advisor=llm_advisor,
            config=config,
        )

        suggestions, latency_ms = service.generate_suggestions(
            procedure_id="test-123",
            report_text="BAL was performed successfully.",
            use_llm=True,
        )

        assert len(suggestions) == 1
        assert latency_ms >= 0
        assert suggestions[0].code == "31622"
        assert suggestions[0].hybrid_decision == HybridDecision.ACCEPTED_AGREEMENT.value
        assert suggestions[0].source == "hybrid"
        assert suggestions[0].procedure_id == "test-123"
        assert suggestions[0].suggestion_id is not None

    def test_generate_suggestions_llm_addition_verified(
        self,
        kb_repo: MockKnowledgeBaseRepository,
        keyword_repo: MockKeywordMappingRepository,
        negation_detector: MockNegationDetector,
        config: CoderSettings,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test pipeline with LLM-only code that gets verified."""
        import modules.coder.application.coding_service as coding_service_mod
        monkeypatch.setattr(coding_service_mod, "apply_ncci_edits", mock_apply_ncci_edits)
        monkeypatch.setattr(coding_service_mod, "apply_mer_rules", mock_apply_mer_rules)

        rule_engine = MockRuleEngine(codes_to_return={})
        llm_advisor = MockLLMAdvisor(codes_to_return={"31652": 0.92})

        service = CodingService(
            kb_repo=kb_repo,
            keyword_repo=keyword_repo,
            negation_detector=negation_detector,
            rule_engine=rule_engine,
            llm_advisor=llm_advisor,
            config=config,
        )

        suggestions, latency_ms = service.generate_suggestions(
            procedure_id="test-124",
            report_text="EBUS-TBNA performed at lymph node station 4R.",
            use_llm=True,
        )

        assert len(suggestions) == 1
        assert latency_ms >= 0
        assert suggestions[0].code == "31652"
        assert suggestions[0].hybrid_decision == HybridDecision.ACCEPTED_HYBRID.value
        assert suggestions[0].source == "llm"
        assert suggestions[0].evidence_verified is True
        assert len(suggestions[0].trigger_phrases) > 0

    def test_generate_suggestions_without_llm(
        self,
        kb_repo: MockKnowledgeBaseRepository,
        keyword_repo: MockKeywordMappingRepository,
        negation_detector: MockNegationDetector,
        config: CoderSettings,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test pipeline with LLM disabled."""
        import modules.coder.application.coding_service as coding_service_mod
        monkeypatch.setattr(coding_service_mod, "apply_ncci_edits", mock_apply_ncci_edits)
        monkeypatch.setattr(coding_service_mod, "apply_mer_rules", mock_apply_mer_rules)

        rule_engine = MockRuleEngine(codes_to_return={"31622": 0.9, "31624": 0.85})
        llm_advisor = MockLLMAdvisor(codes_to_return={"99999": 0.99})  # Should be ignored

        service = CodingService(
            kb_repo=kb_repo,
            keyword_repo=keyword_repo,
            negation_detector=negation_detector,
            rule_engine=rule_engine,
            llm_advisor=llm_advisor,
            config=config,
        )

        suggestions, latency_ms = service.generate_suggestions(
            procedure_id="test-125",
            report_text="BAL and biopsy performed.",
            use_llm=False,  # LLM disabled
        )

        # Should only have rule-based codes
        assert latency_ms >= 0
        codes = {s.code for s in suggestions}
        assert "31622" in codes
        assert "31624" in codes
        assert "99999" not in codes


class TestCodingServiceResult:
    """Test the complete result generation."""

    def test_generate_result_includes_metadata(
        self,
        kb_repo: MockKnowledgeBaseRepository,
        keyword_repo: MockKeywordMappingRepository,
        negation_detector: MockNegationDetector,
        config: CoderSettings,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that generate_result includes all metadata."""
        import modules.coder.application.coding_service as coding_service_mod
        monkeypatch.setattr(coding_service_mod, "apply_ncci_edits", mock_apply_ncci_edits)
        monkeypatch.setattr(coding_service_mod, "apply_mer_rules", mock_apply_mer_rules)

        rule_engine = MockRuleEngine(codes_to_return={"31622": 0.9})
        llm_advisor = MockLLMAdvisor(codes_to_return={"31622": 0.95})

        service = CodingService(
            kb_repo=kb_repo,
            keyword_repo=keyword_repo,
            negation_detector=negation_detector,
            rule_engine=rule_engine,
            llm_advisor=llm_advisor,
            config=config,
        )

        result = service.generate_result(
            procedure_id="test-126",
            report_text="BAL was performed.",
            use_llm=True,
        )

        assert result.procedure_id == "test-126"
        assert len(result.suggestions) > 0
        assert result.kb_version == "mock_kb_v1"
        assert result.policy_version == "smart_hybrid_v2"
        assert result.model_version == "mock_llm_v1"
        assert result.processing_time_ms > 0


class TestCodingServiceReviewFlags:
    """Test review flag assignment."""

    def test_review_flag_required_for_human_review(
        self,
        kb_repo: MockKnowledgeBaseRepository,
        keyword_repo: MockKeywordMappingRepository,
        negation_detector: MockNegationDetector,
        config: CoderSettings,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that HUMAN_REVIEW_REQUIRED gets review_flag='required'."""
        import modules.coder.application.coding_service as coding_service_mod
        monkeypatch.setattr(coding_service_mod, "apply_ncci_edits", mock_apply_ncci_edits)
        monkeypatch.setattr(coding_service_mod, "apply_mer_rules", mock_apply_mer_rules)

        rule_engine = MockRuleEngine(codes_to_return={})
        llm_advisor = MockLLMAdvisor(codes_to_return={"31652": 0.90})

        service = CodingService(
            kb_repo=kb_repo,
            keyword_repo=keyword_repo,
            negation_detector=negation_detector,
            rule_engine=rule_engine,
            llm_advisor=llm_advisor,
            config=config,
        )

        # Text WITHOUT EBUS keywords → needs review
        suggestions, latency_ms = service.generate_suggestions(
            procedure_id="test-127",
            report_text="Normal bronchoscopy performed.",
            use_llm=True,
        )

        assert latency_ms >= 0
        ebus_suggestion = next((s for s in suggestions if s.code == "31652"), None)
        assert ebus_suggestion is not None
        assert ebus_suggestion.review_flag == "required"

    def test_review_flag_optional_for_high_confidence(
        self,
        kb_repo: MockKnowledgeBaseRepository,
        keyword_repo: MockKeywordMappingRepository,
        negation_detector: MockNegationDetector,
        config: CoderSettings,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that high confidence codes get review_flag='optional'."""
        import modules.coder.application.coding_service as coding_service_mod
        monkeypatch.setattr(coding_service_mod, "apply_ncci_edits", mock_apply_ncci_edits)
        monkeypatch.setattr(coding_service_mod, "apply_mer_rules", mock_apply_mer_rules)

        rule_engine = MockRuleEngine(codes_to_return={"31622": 0.95})
        llm_advisor = MockLLMAdvisor(codes_to_return={"31622": 0.98})

        service = CodingService(
            kb_repo=kb_repo,
            keyword_repo=keyword_repo,
            negation_detector=negation_detector,
            rule_engine=rule_engine,
            llm_advisor=llm_advisor,
            config=config,
        )

        suggestions, latency_ms = service.generate_suggestions(
            procedure_id="test-128",
            report_text="BAL was performed.",
            use_llm=True,
        )

        assert latency_ms >= 0
        assert len(suggestions) == 1
        assert suggestions[0].review_flag == "optional"


class TestCodingServiceReasoning:
    """Test reasoning/provenance in suggestions."""

    def test_reasoning_includes_versions(
        self,
        kb_repo: MockKnowledgeBaseRepository,
        keyword_repo: MockKeywordMappingRepository,
        negation_detector: MockNegationDetector,
        config: CoderSettings,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that reasoning includes all version info."""
        import modules.coder.application.coding_service as coding_service_mod
        monkeypatch.setattr(coding_service_mod, "apply_ncci_edits", mock_apply_ncci_edits)
        monkeypatch.setattr(coding_service_mod, "apply_mer_rules", mock_apply_mer_rules)

        rule_engine = MockRuleEngine(codes_to_return={"31622": 0.9})
        llm_advisor = MockLLMAdvisor(codes_to_return={"31622": 0.95})

        service = CodingService(
            kb_repo=kb_repo,
            keyword_repo=keyword_repo,
            negation_detector=negation_detector,
            rule_engine=rule_engine,
            llm_advisor=llm_advisor,
            config=config,
        )

        suggestions, latency_ms = service.generate_suggestions(
            procedure_id="test-129",
            report_text="BAL performed.",
            use_llm=True,
        )

        assert latency_ms >= 0
        assert len(suggestions) == 1
        reasoning = suggestions[0].reasoning

        assert reasoning.kb_version == "mock_kb_v1"
        assert reasoning.policy_version == "smart_hybrid_v2"
        assert reasoning.model_version == "mock_llm_v1"
        assert reasoning.keyword_map_version == "mock_keyword_v1"
        assert reasoning.negation_detector_version == "mock_negation_v1"
