"""
Tests for the SmartHybridOrchestrator.

Verifies:
- ML HIGH_CONF + rules OK → no LLM call; source="ml_rules_fastpath"
- ML GRAY_ZONE → LLM called; source="hybrid_llm_fallback"
- ML HIGH_CONF but Rules raises RuleViolationError → LLM called; rules_error in metadata
- LOW_CONF → LLM as primary coder
"""

from dataclasses import dataclass
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from modules.coder.application.smart_hybrid_policy import (
    OrchestratorResult,
    SmartHybridOrchestrator,
)
from modules.coder.rules_engine import RuleViolationError
from modules.ml_coder.thresholds import CaseDifficulty


@dataclass
class MockCodePrediction:
    """Mock CodePrediction for testing."""
    cpt: str
    prob: float


@dataclass
class MockCaseClassification:
    """Mock CaseClassification for testing."""
    predictions: List[MockCodePrediction]
    high_conf: List[MockCodePrediction]
    gray_zone: List[MockCodePrediction]
    difficulty: CaseDifficulty


@dataclass
class MockLLMSuggestion:
    """Mock LLM suggestion."""
    code: str
    confidence: float
    rationale: str


class TestSmartHybridOrchestratorHighConf:
    """Tests for HIGH_CONF fast path."""

    def test_high_conf_rules_ok_no_llm_call(self):
        """Verify HIGH_CONF + rules OK uses fast path without LLM."""
        # Setup mocks
        mock_ml = MagicMock()
        mock_rules = MagicMock()
        mock_llm = MagicMock()

        # ML returns HIGH_CONF with codes
        mock_ml.classify_case.return_value = MockCaseClassification(
            predictions=[
                MockCodePrediction("31653", 0.9),
                MockCodePrediction("31627", 0.85),
            ],
            high_conf=[
                MockCodePrediction("31653", 0.9),
                MockCodePrediction("31627", 0.85),
            ],
            gray_zone=[],
            difficulty=CaseDifficulty.HIGH_CONF,
        )

        # Rules validates successfully
        mock_rules.validate.return_value = ["31653", "31627"]

        orchestrator = SmartHybridOrchestrator(
            ml_predictor=mock_ml,
            rules_engine=mock_rules,
            llm_advisor=mock_llm,
        )

        result = orchestrator.get_codes("EBUS staging 4 stations sampled")

        # Verify
        assert result.source == "ml_rules_fastpath"
        assert set(result.codes) == {"31653", "31627"}
        assert result.metadata["llm_called"] is False
        mock_llm.suggest_codes.assert_not_called()
        mock_llm.suggest_with_context.assert_not_called()

    def test_high_conf_rules_error_triggers_llm(self):
        """Verify HIGH_CONF with rules error triggers LLM fallback."""
        mock_ml = MagicMock()
        mock_rules = MagicMock()
        mock_llm = MagicMock()

        # ML returns HIGH_CONF
        mock_ml.classify_case.return_value = MockCaseClassification(
            predictions=[
                MockCodePrediction("31640", 0.9),
                MockCodePrediction("31641", 0.85),
            ],
            high_conf=[
                MockCodePrediction("31640", 0.9),
                MockCodePrediction("31641", 0.85),
            ],
            gray_zone=[],
            difficulty=CaseDifficulty.HIGH_CONF,
        )

        # Rules raises violation for this combination
        mock_rules.validate.side_effect = [
            RuleViolationError("Cannot bill both debulking codes"),
            ["31641"],  # Second call (LLM output validation) succeeds
        ]

        # LLM returns corrected codes
        mock_llm.suggest_with_context.return_value = [
            MockLLMSuggestion("31641", 0.95, "Ablation documented"),
        ]

        orchestrator = SmartHybridOrchestrator(
            ml_predictor=mock_ml,
            rules_engine=mock_rules,
            llm_advisor=mock_llm,
        )

        result = orchestrator.get_codes("Tumor ablation performed")

        # Verify
        assert result.source == "hybrid_llm_fallback"
        assert "31641" in result.codes
        assert result.metadata["llm_called"] is True
        assert "debulking" in result.metadata["rules_error"].lower()
        mock_llm.suggest_with_context.assert_called_once()


class TestSmartHybridOrchestratorGrayZone:
    """Tests for GRAY_ZONE with LLM fallback."""

    def test_gray_zone_triggers_llm(self):
        """Verify GRAY_ZONE triggers LLM as final judge."""
        mock_ml = MagicMock()
        mock_rules = MagicMock()
        mock_llm = MagicMock()

        # ML returns GRAY_ZONE
        mock_ml.classify_case.return_value = MockCaseClassification(
            predictions=[
                MockCodePrediction("31628", 0.55),
                MockCodePrediction("31624", 0.52),
            ],
            high_conf=[],
            gray_zone=[
                MockCodePrediction("31628", 0.55),
                MockCodePrediction("31624", 0.52),
            ],
            difficulty=CaseDifficulty.GRAY_ZONE,
        )

        # Rules would pass (but won't be used for fast path)
        mock_rules.validate.return_value = ["31628"]

        # LLM decides
        mock_llm.suggest_with_context.return_value = [
            MockLLMSuggestion("31628", 0.90, "Biopsy clearly documented"),
        ]

        orchestrator = SmartHybridOrchestrator(
            ml_predictor=mock_ml,
            rules_engine=mock_rules,
            llm_advisor=mock_llm,
        )

        result = orchestrator.get_codes("Transbronchial biopsy")

        # Verify
        assert result.source == "hybrid_llm_fallback"
        assert result.metadata["llm_called"] is True
        assert result.metadata["reason_for_fallback"] == "gray_zone"
        mock_llm.suggest_with_context.assert_called_once()

    def test_gray_zone_llm_receives_ml_context(self):
        """Verify LLM receives ML predictions as context."""
        mock_ml = MagicMock()
        mock_rules = MagicMock()
        mock_llm = MagicMock()

        # ML returns GRAY_ZONE
        mock_ml.classify_case.return_value = MockCaseClassification(
            predictions=[
                MockCodePrediction("31628", 0.55),
                MockCodePrediction("31627", 0.45),
            ],
            high_conf=[],
            gray_zone=[MockCodePrediction("31628", 0.55)],
            difficulty=CaseDifficulty.GRAY_ZONE,
        )

        mock_rules.validate.return_value = ["31628"]
        mock_llm.suggest_with_context.return_value = [
            MockLLMSuggestion("31628", 0.9, "Confirmed"),
        ]

        orchestrator = SmartHybridOrchestrator(
            ml_predictor=mock_ml,
            rules_engine=mock_rules,
            llm_advisor=mock_llm,
        )

        orchestrator.get_codes("Some note")

        # Check context passed to LLM
        call_args = mock_llm.suggest_with_context.call_args
        context = call_args[0][1]  # Second positional arg is context
        assert "ml_suggestion" in context
        assert "difficulty" in context
        assert context["difficulty"] == "gray_zone"


class TestSmartHybridOrchestratorLowConf:
    """Tests for LOW_CONF with LLM as primary."""

    def test_low_conf_llm_primary(self):
        """Verify LOW_CONF uses LLM as primary coder."""
        mock_ml = MagicMock()
        mock_rules = MagicMock()
        mock_llm = MagicMock()

        # ML returns LOW_CONF (all predictions below threshold)
        mock_ml.classify_case.return_value = MockCaseClassification(
            predictions=[
                MockCodePrediction("31622", 0.35),
                MockCodePrediction("31628", 0.30),
            ],
            high_conf=[],
            gray_zone=[],
            difficulty=CaseDifficulty.LOW_CONF,
        )

        mock_rules.validate.return_value = ["31653", "31627"]
        mock_llm.suggest_with_context.return_value = [
            MockLLMSuggestion("31653", 0.95, "EBUS 3 stations"),
            MockLLMSuggestion("31627", 0.85, "Navigation used"),
        ]

        orchestrator = SmartHybridOrchestrator(
            ml_predictor=mock_ml,
            rules_engine=mock_rules,
            llm_advisor=mock_llm,
        )

        result = orchestrator.get_codes("Complex procedure note")

        # Verify
        assert result.source == "hybrid_llm_fallback"
        assert result.metadata["reason_for_fallback"] == "low_confidence"
        assert result.metadata["llm_called"] is True
        assert set(result.codes) == {"31653", "31627"}


class TestSmartHybridOrchestratorRulesVetoLLM:
    """Tests for rules veto on LLM output."""

    def test_rules_cleans_llm_output(self):
        """Verify rules engine cleans LLM output in non-strict mode."""
        mock_ml = MagicMock()
        mock_rules = MagicMock()
        mock_llm = MagicMock()

        # ML returns GRAY_ZONE
        mock_ml.classify_case.return_value = MockCaseClassification(
            predictions=[MockCodePrediction("31628", 0.5)],
            high_conf=[],
            gray_zone=[MockCodePrediction("31628", 0.5)],
            difficulty=CaseDifficulty.GRAY_ZONE,
        )

        # First call (strict) succeeds, second call (non-strict on LLM output) cleans
        mock_rules.validate.side_effect = [
            ["31628"],  # ML candidates validation
            ["31628", "31653"],  # LLM output cleaned (31622 removed)
        ]

        # LLM suggests 31622 + 31628 + 31653
        mock_llm.suggest_with_context.return_value = [
            MockLLMSuggestion("31622", 0.7, "Diagnostic"),  # Should be removed
            MockLLMSuggestion("31628", 0.9, "Biopsy"),
            MockLLMSuggestion("31653", 0.85, "EBUS"),
        ]

        orchestrator = SmartHybridOrchestrator(
            ml_predictor=mock_ml,
            rules_engine=mock_rules,
            llm_advisor=mock_llm,
        )

        result = orchestrator.get_codes("EBUS with biopsy")

        # Verify 31622 was cleaned out by rules
        assert "31622" not in result.codes
        assert "31628" in result.codes
        assert "31653" in result.codes
        # Raw LLM codes preserved in metadata
        assert "31622" in result.metadata["llm_raw_codes"]


class TestOrchestratorResult:
    """Tests for OrchestratorResult dataclass."""

    def test_result_structure(self):
        """Verify OrchestratorResult has expected fields."""
        result = OrchestratorResult(
            codes=["31628", "31653"],
            source="ml_rules_fastpath",
            metadata={"llm_called": False},
        )

        assert result.codes == ["31628", "31653"]
        assert result.source == "ml_rules_fastpath"
        assert result.metadata["llm_called"] is False

    def test_result_default_metadata(self):
        """Verify metadata defaults to empty dict."""
        result = OrchestratorResult(
            codes=["31628"],
            source="test",
        )
        assert result.metadata == {}


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_ml_candidates_triggers_llm(self):
        """Verify empty ML candidates triggers LLM."""
        mock_ml = MagicMock()
        mock_rules = MagicMock()
        mock_llm = MagicMock()

        # ML returns no candidates above threshold
        mock_ml.classify_case.return_value = MockCaseClassification(
            predictions=[MockCodePrediction("31622", 0.2)],
            high_conf=[],
            gray_zone=[],
            difficulty=CaseDifficulty.LOW_CONF,
        )

        mock_rules.validate.return_value = ["31628"]
        mock_llm.suggest_with_context.return_value = [
            MockLLMSuggestion("31628", 0.9, "Found biopsy"),
        ]

        orchestrator = SmartHybridOrchestrator(
            ml_predictor=mock_ml,
            rules_engine=mock_rules,
            llm_advisor=mock_llm,
        )

        result = orchestrator.get_codes("Unclear note")

        assert result.source == "hybrid_llm_fallback"
        assert result.metadata["llm_called"] is True

    def test_llm_without_suggest_with_context_falls_back(self):
        """Verify fallback to suggest_codes if suggest_with_context not available."""
        mock_ml = MagicMock()
        mock_rules = MagicMock()
        mock_llm = MagicMock(spec=["suggest_codes"])  # No suggest_with_context

        mock_ml.classify_case.return_value = MockCaseClassification(
            predictions=[MockCodePrediction("31628", 0.5)],
            high_conf=[],
            gray_zone=[MockCodePrediction("31628", 0.5)],
            difficulty=CaseDifficulty.GRAY_ZONE,
        )

        mock_rules.validate.return_value = ["31628"]
        mock_llm.suggest_codes.return_value = [
            MockLLMSuggestion("31628", 0.9, "Biopsy"),
        ]

        orchestrator = SmartHybridOrchestrator(
            ml_predictor=mock_ml,
            rules_engine=mock_rules,
            llm_advisor=mock_llm,
        )

        result = orchestrator.get_codes("Some note")

        # Should have used suggest_codes instead
        mock_llm.suggest_codes.assert_called_once()
        assert "31628" in result.codes
