"""Integration tests ensuring CodingService uses sectionizer before LLM calls."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from config.settings import CoderSettings
from modules.coder.application.coding_service import CodingService
from modules.coder.adapters.nlp.simple_negation_detector import SimpleNegationDetector


class DummyLLMAdvisor:
    def __init__(self):
        self.version = "dummy_llm"
        self.last_text: str | None = None

    def suggest_codes(self, report_text: str):
        self.last_text = report_text
        return []


@dataclass
class StubRuleEngineResult:
    codes: list[str]
    confidence: dict[str, float]


class StubRuleEngine:
    def generate_candidates(self, report_text: str) -> StubRuleEngineResult:
        return StubRuleEngineResult(codes=[], confidence={})


class StubKnowledgeBaseRepository:
    version = "stub_kb"

    def get_all_codes(self):
        return set()

    def get_procedure_info(self, code: str):
        return None

    def get_mer_group(self, code: str):
        return None

    def get_ncci_pairs(self, code: str):
        return []

    def is_addon_code(self, code: str):
        return False

    def get_parent_codes(self, addon_code: str):
        return []

    def get_bundled_codes(self, code: str):
        return []


class StubKeywordMappingRepository:
    version = "stub_keyword"

    def get_mapping(self, code: str):
        return None


def test_sectionizer_applied_to_llm_prompts(monkeypatch):
    monkeypatch.setenv("CODING_SECTIONIZER_ENABLED", "true")
    monkeypatch.setenv("CODING_MAX_LLM_INPUT_TOKENS", "20")

    kb_repo = StubKnowledgeBaseRepository()
    keyword_repo = StubKeywordMappingRepository()
    neg_detector = SimpleNegationDetector()
    rule_engine = StubRuleEngine()
    llm_advisor = DummyLLMAdvisor()
    config = CoderSettings()

    service = CodingService(
        kb_repo=kb_repo,
        keyword_repo=keyword_repo,
        negation_detector=neg_detector,
        rule_engine=rule_engine,  # type: ignore[arg-type]
        llm_advisor=llm_advisor,  # type: ignore[arg-type]
        config=config,
    )

    long_text = (
        "HISTORY: " + ("hx " * 200) + "\n"
        "PROCEDURE: Bronchoscopy with EBUS performed.\n"
        "FINDINGS: Stations 7, 4R sampled.\n"
    )

    service._run_llm_advisor(report_text=long_text, use_llm=True)
    assert llm_advisor.last_text is not None
    lowered = llm_advisor.last_text.lower()
    assert "procedure:" in lowered
    assert "findings:" in lowered
    assert "history:" not in lowered
