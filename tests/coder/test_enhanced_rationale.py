import pytest

from modules.autocode.coder import CodeSuggestion, EnhancedCPTCoder


def test_code_procedure_emits_rationale(monkeypatch):
    coder = EnhancedCPTCoder(use_llm_advisor=False)

    def fake_generate(self, procedure_data):
        suggestion = CodeSuggestion("31641")
        suggestion.description = "Bronchoscopy with endobronchial tumor destruction"
        suggestion.groups = ["bronchoscopy_ablation"]
        return [suggestion]

    monkeypatch.setattr(EnhancedCPTCoder, "_generate_codes", fake_generate, raising=False)

    result = coder.code_procedure({"note_text": "Tumor debulked with APC", "locality": "00", "setting": "facility"})
    codes = result.get("codes") or []
    assert codes, "Expected at least one code in the result"

    rationale = codes[0].get("rationale")
    assert isinstance(rationale, list)
    assert rationale, "Rationale should not be empty"
    assert codes[0].get("description"), "Description should be populated"
