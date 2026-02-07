"""Integration tests ensuring CodingService ignores LLM in extraction-first mode."""

from __future__ import annotations

from dataclasses import dataclass

from config.settings import CoderSettings
from app.coder.application.coding_service import CodingService
from app.coder.adapters.nlp.simple_negation_detector import SimpleNegationDetector
from app.registry.application.registry_service import RegistryExtractionResult
from app.registry.schema import RegistryRecord


class DummyLLMAdvisor:
    def __init__(self) -> None:
        self.version = "dummy_llm"
        self.called = False

    def suggest_codes(self, report_text: str):
        self.called = True
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


class StubRegistryService:
    def __init__(self) -> None:
        self._result = RegistryExtractionResult(
            record=RegistryRecord(),
            cpt_codes=[],
            coder_difficulty="LOW_CONF",
            coder_source="extraction_first",
            mapped_fields={},
            code_rationales={},
            derivation_warnings=[],
            warnings=[],
            needs_manual_review=False,
            validation_errors=[],
            audit_warnings=[],
        )

    def extract_fields_extraction_first(self, note_text: str) -> RegistryExtractionResult:
        return self._result


def test_llm_is_not_called_in_extraction_first():
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
        registry_service=StubRegistryService(),
    )

    service.generate_suggestions(
        procedure_id="test-proc",
        report_text="Bronchoscopy performed.",
        use_llm=True,
    )

    assert llm_advisor.called is False
