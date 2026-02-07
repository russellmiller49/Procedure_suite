from __future__ import annotations

from unittest.mock import MagicMock

from app.coder.parallel_pathway.orchestrator import ParallelPathwayOrchestrator


class _LegacyPredictor:
    available = True

    def predict(self, note_text: str) -> list[str]:
        return ["bal", "endobronchial_biopsy"]


class _Pred:
    def __init__(self, *, field: str, probability: float, is_positive: bool) -> None:
        self.field = field
        self.probability = probability
        self.is_positive = is_positive


class _Classification:
    def __init__(self) -> None:
        self.predictions = [_Pred(field="bal", probability=0.91, is_positive=True)]
        self.positive_fields = ["bal"]
        self.difficulty = "HIGH_CONF"


class _PredictorWithClassifyCase:
    available = True

    def classify_case(self, note_text: str) -> _Classification:
        return _Classification()


def _orchestrator_without_loading_ner() -> ParallelPathwayOrchestrator:
    return ParallelPathwayOrchestrator(
        ner_predictor=MagicMock(available=False),
        ner_mapper=MagicMock(),
    )


def test_path_b_handles_predict_returning_list() -> None:
    orchestrator = _orchestrator_without_loading_ner()
    result = orchestrator._run_path_b("test note", ml_predictor=_LegacyPredictor())

    assert "31624" in result.codes
    assert "31625" in result.codes
    assert result.details.get("ml_positive_fields") == ["bal", "endobronchial_biopsy"]


def test_path_b_uses_classify_case_when_available() -> None:
    orchestrator = _orchestrator_without_loading_ner()
    result = orchestrator._run_path_b("test note", ml_predictor=_PredictorWithClassifyCase())

    assert result.codes == ["31624"]
    assert abs(result.confidences["31624"] - 0.91) < 1e-6
    assert result.details.get("ml_positive_fields") == ["bal"]
    assert result.details.get("ml_difficulty") == "HIGH_CONF"
