"""Tests for terminology normalizer and QA rule checker."""

from pathlib import Path

from modules.autocode.ip_kb.terminology_utils import QARuleChecker, TerminologyNormalizer

KNOWLEDGE_PATH = Path("data/knowledge/ip_coding_billing.v2_7.json")


def test_terminology_normalizer_handles_variations() -> None:
    normalizer = TerminologyNormalizer(KNOWLEDGE_PATH)

    assert normalizer.to_canonical("conscious sedation", "procedure_categories") == "moderate_sedation"
    assert normalizer.to_canonical("ion", "procedure_categories") == "navigation"
    lobes = normalizer.normalize_with_category("Right upper lobe")
    assert lobes and lobes["canonical_key"] == "rul"
    modifier = normalizer.to_canonical("modifier 59", "modifiers")
    assert modifier in {"mod_59", "59"}


def test_qachecker_passes_when_documentation_complete() -> None:
    checker = QARuleChecker(KNOWLEDGE_PATH)
    documentation = {
        "navigation_system_used": True,
        "catheter_advanced_under_navigation_guidance": True,
        "target_lesion_identified": True,
    }
    issues = checker.evaluate_code("+31627", documentation)
    assert issues == []


def test_qachecker_reports_missing_navigation_elements() -> None:
    checker = QARuleChecker(KNOWLEDGE_PATH)
    documentation = {
        "navigation_system_used": False,
        "catheter_advanced_under_navigation_guidance": False,
        "target_lesion_identified": False,
    }
    issues = checker.evaluate_code("+31627", documentation)
    assert issues
    assert issues[0]["missing"]
