"""Phase 1 plumbing tests for the coding pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from config.settings import CoderSettings
from modules.coder.adapters.nlp.simple_negation_detector import SimpleNegationDetector
from modules.coder.application.coding_service import CodingService
from modules.coder.rules_engine import CodingRulesEngine
from modules.coder.types import CodeCandidate
from modules.registry.application.registry_service import RegistryExtractionResult
from modules.registry.schema import RegistryRecord


def test_rules_engine_noop_does_not_change_candidates():
    engine = CodingRulesEngine()
    original = [
        CodeCandidate(code="31624", confidence=0.9),
        CodeCandidate(code="31645", confidence=0.8),
    ]

    result = engine.apply(original, note_text="synthetic note with biopsy details")

    assert result is not original
    assert [c.code for c in result] == ["31624", "31645"]


@dataclass
class StubProcedureInfo:
    code: str
    description: str
    total_facility_rvu: float = 10.0


class StubKnowledgeBaseRepository:
    """Minimal KB repository for exercising CodingService."""

    def __init__(self):
        self.version = "stub_kb_v1"
        self._codes = {
            "31624": StubProcedureInfo("31624", "Bronchoscopy with biopsy"),
            "31652": StubProcedureInfo("31652", "EBUS-TBNA"),
        }

    def get_all_codes(self) -> set[str]:
        return set(self._codes.keys())

    def get_procedure_info(self, code: str) -> StubProcedureInfo | None:
        return self._codes.get(code)

    def get_mer_group(self, code: str) -> str | None:
        return None

    def get_ncci_pairs(self, code: str) -> list:
        return []

    def is_addon_code(self, code: str) -> bool:
        return code.startswith("+")

    def get_parent_codes(self, addon_code: str) -> list[str]:
        return []

    def get_bundled_codes(self, code: str) -> list[str]:
        return []


class StubKeywordMapping:
    def __init__(self, code: str, positive_phrases: list[str]):
        self.code = code
        self.description = f"Keywords for {code}"
        self.positive_phrases = positive_phrases
        self.negative_phrases = ["no", "not"]
        self.context_window_chars = 200
        self.version = "stub"
        self.notes = None


class StubKeywordMappingRepository:
    """Keyword repository with deterministic mappings."""

    def __init__(self):
        self.version = "stub_keyword_v1"
        self._mappings = {
            "31624": StubKeywordMapping("31624", ["bal", "biopsy"]),
            "31652": StubKeywordMapping("31652", ["ebus"]),
        }

    def get_mapping(self, code: str) -> StubKeywordMapping | None:
        normalized = code.lstrip("+")
        return self._mappings.get(code) or self._mappings.get(normalized)

    def get_all_codes(self) -> list[str]:
        return list(self._mappings.keys())


class StubRegistryService:
    def __init__(self, result: RegistryExtractionResult) -> None:
        self._result = result

    def extract_fields_extraction_first(self, note_text: str) -> RegistryExtractionResult:
        return self._result


class StubRuleEngineResult:
    def __init__(self, codes_to_return: dict[str, float]):
        self.codes = list(codes_to_return.keys())
        self.confidence = codes_to_return


class StubRuleEngine:
    """Rule engine that always returns the configured codes."""

    def __init__(self, codes_to_return: dict[str, float]):
        self._result = StubRuleEngineResult(codes_to_return)

    def generate_candidates(self, report_text: str) -> StubRuleEngineResult:
        return self._result


def test_coding_service_generates_suggestions_with_new_pipeline():
    kb_repo = StubKnowledgeBaseRepository()
    keyword_repo = StubKeywordMappingRepository()
    neg_detector = SimpleNegationDetector()
    rule_engine = StubRuleEngine({"31624": 0.9, "31652": 0.88})
    config = CoderSettings()

    extraction_result = RegistryExtractionResult(
        record=RegistryRecord(),
        cpt_codes=["31624", "31652"],
        coder_difficulty="HIGH_CONF",
        coder_source="extraction_first",
        mapped_fields={},
        code_rationales={
            "31624": "bal.performed=true",
            "31652": "linear_ebus.performed=true",
        },
        derivation_warnings=[],
        warnings=[],
        needs_manual_review=False,
        validation_errors=[],
        audit_warnings=[],
    )
    registry_service = StubRegistryService(extraction_result)

    service = CodingService(
        kb_repo=kb_repo,
        keyword_repo=keyword_repo,
        negation_detector=neg_detector,
        rule_engine=rule_engine,
        llm_advisor=None,
        config=config,
        registry_service=registry_service,
    )

    note_text = (
        "Diagnostic bronchoscopy performed with BAL and linear EBUS-TBNA "
        "sampling in two stations."
    )
    result = service.generate_result(
        procedure_id="test-proc",
        report_text=note_text,
        use_llm=False,
        procedure_type="bronch_diagnostic",
    )

    assert {s.code for s in result.suggestions} == {"31624", "31652"}
