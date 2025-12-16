"""RAW-ML auditor for extraction-first registry pipeline.

Critical invariant:
This auditor must use raw ML output only via MLCoderPredictor.classify_case(raw_note_text)
and must never call SmartHybridOrchestrator.get_codes() or any rules validation / LLM fallback.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from modules.ml_coder.predictor import CaseClassification, CodePrediction, MLCoderPredictor


@dataclass(frozen=True)
class RawMLAuditConfig:
    use_buckets: bool = True
    top_k: int = 25
    min_prob: float = 0.50
    self_correct_min_prob: float = 0.95

    @classmethod
    def from_env(cls) -> "RawMLAuditConfig":
        def _as_bool(name: str, default: str) -> bool:
            return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y"}

        def _as_int(name: str, default: int) -> int:
            try:
                return int(os.getenv(name, str(default)).strip())
            except ValueError:
                return default

        def _as_float(name: str, default: float) -> float:
            try:
                return float(os.getenv(name, str(default)).strip())
            except ValueError:
                return default

        return cls(
            use_buckets=_as_bool("REGISTRY_ML_AUDIT_USE_BUCKETS", "1"),
            top_k=_as_int("REGISTRY_ML_AUDIT_TOP_K", 25),
            min_prob=_as_float("REGISTRY_ML_AUDIT_MIN_PROB", 0.50),
            self_correct_min_prob=_as_float("REGISTRY_ML_SELF_CORRECT_MIN_PROB", 0.95),
        )


class RawMLAuditor:
    def __init__(self, predictor: MLCoderPredictor | None = None) -> None:
        self._predictor = predictor or MLCoderPredictor()

    def classify(self, raw_note_text: str) -> CaseClassification:
        return self._predictor.classify_case(raw_note_text)

    def audit_predictions(
        self, cls: CaseClassification, cfg: RawMLAuditConfig | None = None
    ) -> list[CodePrediction]:
        cfg = cfg or RawMLAuditConfig.from_env()

        if cfg.use_buckets:
            return list(cls.high_conf) + list(cls.gray_zone)

        preds = cls.predictions[: cfg.top_k]
        return [p for p in preds if p.prob >= cfg.min_prob]

    def self_correct_triggers(
        self, cls: CaseClassification, cfg: RawMLAuditConfig | None = None
    ) -> list[CodePrediction]:
        cfg = cfg or RawMLAuditConfig.from_env()
        return [p for p in cls.high_conf if p.prob >= cfg.self_correct_min_prob]


__all__ = ["RawMLAuditor", "RawMLAuditConfig"]

