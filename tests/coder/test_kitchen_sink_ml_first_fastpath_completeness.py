from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

from app.coder.application.smart_hybrid_policy import SmartHybridOrchestrator
from app.coder.rules_engine import CodingRulesEngine
from ml.lib.ml_coder.thresholds import CaseDifficulty


@dataclass
class _MockPrediction:
    cpt: str
    prob: float


@dataclass
class _MockCaseClassification:
    predictions: list[_MockPrediction]
    high_conf: list[_MockPrediction]
    gray_zone: list[_MockPrediction]
    difficulty: CaseDifficulty


def test_kitchen_sink_ml_first_fastpath_is_complete() -> None:
    note_text = Path(
        "tests/fixtures/notes/kitchen_sink_ion_nav_ebus_fiducial_dilation.txt"
    ).read_text()

    mock_ml = MagicMock()
    mock_ml.classify_case.return_value = _MockCaseClassification(
        predictions=[_MockPrediction("31627", 0.99)],
        high_conf=[_MockPrediction("31627", 0.99)],
        gray_zone=[],
        difficulty=CaseDifficulty.HIGH_CONF,
    )

    llm = MagicMock()
    llm.suggest_codes.side_effect = RuntimeError("LLM should not be called in fastpath")
    llm.suggest_with_context.side_effect = RuntimeError(
        "LLM should not be called in fastpath"
    )

    orchestrator = SmartHybridOrchestrator(
        ml_predictor=mock_ml,
        rules_engine=CodingRulesEngine(),
        llm_advisor=llm,
    )

    result = orchestrator.get_codes(note_text)
    codes = {c.lstrip("+") for c in result.codes}

    assert result.source == "ml_rules_fastpath"

    assert {"31626", "31630"}.issubset(codes)
    assert ("31652" in codes) or ("31653" in codes)

    assert "31646" not in codes
    assert "31635" not in codes

