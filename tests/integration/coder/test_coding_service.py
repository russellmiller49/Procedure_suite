"""Integration tests for the extraction-first CodingService."""

from dataclasses import dataclass
from typing import Optional

import pytest

from config.settings import CoderSettings
from app.coder.application.coding_service import CodingService
from app.registry.application.registry_service import RegistryExtractionResult
from app.registry.schema import RegistryRecord


@dataclass
class MockProcedureInfo:
    code: str
    description: str = ""


class MockKnowledgeBaseRepository:
    def __init__(self) -> None:
        self.version = "mock_kb_v1"
        self._codes = {
            "31622": "Bronchoscopy with BAL",
            "31652": "EBUS-TBNA",
        }

    def get_procedure_info(self, code: str) -> Optional[MockProcedureInfo]:
        if code in self._codes:
            return MockProcedureInfo(code=code, description=self._codes[code])
        return None


class MockKeywordMappingRepository:
    version = "mock_keyword_v1"

    def get_mapping(self, code: str):
        return None


class MockNegationDetector:
    version = "mock_negation_v1"

    def is_negated_simple(self, context: str, negative_phrases: list[str]) -> bool:
        return False


class MockRegistryService:
    def __init__(self, result: RegistryExtractionResult) -> None:
        self._result = result

    def extract_fields_extraction_first(self, note_text: str) -> RegistryExtractionResult:
        return self._result


def make_extraction_result(
    *,
    cpt_codes: list[str],
    code_rationales: dict[str, str] | None = None,
    coder_difficulty: str = "HIGH_CONF",
    audit_warnings: list[str] | None = None,
    derivation_warnings: list[str] | None = None,
    needs_manual_review: bool = False,
) -> RegistryExtractionResult:
    return RegistryExtractionResult(
        record=RegistryRecord(),
        cpt_codes=cpt_codes,
        coder_difficulty=coder_difficulty,
        coder_source="extraction_first",
        mapped_fields={},
        code_rationales=code_rationales or {},
        derivation_warnings=derivation_warnings or [],
        warnings=[],
        needs_manual_review=needs_manual_review,
        validation_errors=[],
        audit_warnings=audit_warnings or [],
    )


@pytest.fixture
def config() -> CoderSettings:
    return CoderSettings(
        advisor_confidence_auto_accept=0.85,
        rule_confidence_low_threshold=0.6,
        context_window_chars=200,
    )


class TestCodingServiceExtractionFirst:
    def test_generate_suggestions_uses_registry_output(self, config: CoderSettings) -> None:
        kb_repo = MockKnowledgeBaseRepository()
        keyword_repo = MockKeywordMappingRepository()
        negation_detector = MockNegationDetector()
        extraction_result = make_extraction_result(
            cpt_codes=["31622"],
            code_rationales={"31622": "diagnostic_bronchoscopy.performed=true"},
        )
        registry_service = MockRegistryService(extraction_result)

        service = CodingService(
            kb_repo=kb_repo,
            keyword_repo=keyword_repo,
            negation_detector=negation_detector,
            rule_engine=None,  # type: ignore[arg-type]
            llm_advisor=None,
            config=config,
            registry_service=registry_service,
        )

        suggestions, latency_ms = service.generate_suggestions(
            procedure_id="test-123",
            report_text="Bronchoscopy performed.",
            use_llm=True,
        )

        assert latency_ms >= 0
        assert len(suggestions) == 1
        assert suggestions[0].code == "31622"
        assert suggestions[0].hybrid_decision == "EXTRACTION_FIRST"
        assert suggestions[0].reasoning.policy_version == service.POLICY_VERSION
        assert "DETERMINISTIC" in suggestions[0].reasoning.rule_paths[0]

    def test_review_flag_required_when_manual_review(self, config: CoderSettings) -> None:
        kb_repo = MockKnowledgeBaseRepository()
        keyword_repo = MockKeywordMappingRepository()
        negation_detector = MockNegationDetector()
        extraction_result = make_extraction_result(
            cpt_codes=["31652"],
            code_rationales={"31652": "linear_ebus.performed=true"},
            needs_manual_review=True,
        )
        registry_service = MockRegistryService(extraction_result)

        service = CodingService(
            kb_repo=kb_repo,
            keyword_repo=keyword_repo,
            negation_detector=negation_detector,
            rule_engine=None,  # type: ignore[arg-type]
            llm_advisor=None,
            config=config,
            registry_service=registry_service,
        )

        suggestions, _ = service.generate_suggestions(
            procedure_id="test-124",
            report_text="EBUS performed.",
            use_llm=False,
        )

        assert suggestions[0].review_flag == "required"

    def test_review_flag_recommended_on_audit_warning(self, config: CoderSettings) -> None:
        kb_repo = MockKnowledgeBaseRepository()
        keyword_repo = MockKeywordMappingRepository()
        negation_detector = MockNegationDetector()
        extraction_result = make_extraction_result(
            cpt_codes=["31622"],
            code_rationales={"31622": "diagnostic_bronchoscopy.performed=true"},
            audit_warnings=["RAW_ML_AUDIT: missing 31624"],
        )
        registry_service = MockRegistryService(extraction_result)

        service = CodingService(
            kb_repo=kb_repo,
            keyword_repo=keyword_repo,
            negation_detector=negation_detector,
            rule_engine=None,  # type: ignore[arg-type]
            llm_advisor=None,
            config=config,
            registry_service=registry_service,
        )

        suggestions, _ = service.generate_suggestions(
            procedure_id="test-125",
            report_text="Bronchoscopy performed.",
            use_llm=False,
        )

        assert suggestions[0].review_flag == "recommended"


class TestCodingServiceResult:
    def test_generate_result_includes_metadata(self, config: CoderSettings) -> None:
        kb_repo = MockKnowledgeBaseRepository()
        keyword_repo = MockKeywordMappingRepository()
        negation_detector = MockNegationDetector()
        extraction_result = make_extraction_result(
            cpt_codes=["31622"],
            code_rationales={"31622": "diagnostic_bronchoscopy.performed=true"},
            coder_difficulty="GRAY_ZONE",
        )
        registry_service = MockRegistryService(extraction_result)

        service = CodingService(
            kb_repo=kb_repo,
            keyword_repo=keyword_repo,
            negation_detector=negation_detector,
            rule_engine=None,  # type: ignore[arg-type]
            llm_advisor=None,
            config=config,
            registry_service=registry_service,
        )

        result = service.generate_result(
            procedure_id="test-126",
            report_text="Bronchoscopy performed.",
            use_llm=False,
        )

        assert result.procedure_id == "test-126"
        assert len(result.suggestions) == 1
        assert result.kb_version == "mock_kb_v1"
        assert result.policy_version == service.POLICY_VERSION
        assert result.model_version == ""
        assert result.processing_time_ms > 0
