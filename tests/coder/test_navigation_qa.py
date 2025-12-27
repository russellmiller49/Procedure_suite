"""Integration tests for QA advisories in coder output."""

from modules.autocode.coder import EnhancedCPTCoder


def test_navigation_missing_documentation_flags_qa_warning() -> None:
    coder = EnhancedCPTCoder()
    note = """
    PROCEDURE:
    Ion robotic bronchoscopy with electromagnetic navigation to sample a right upper lobe nodule.
    Radial EBUS confirmed the lesion visually.
    """
    procedure = {
        "note_text": note,
        "registry": {
            "nav_tool_in_lesion": False,
            "nav_sampling_tools": ["forceps"],
            "nav_rebus_used": True,
            "nav_rebus_view": "Concentric",
        },
    }
    result = coder.code_procedure(procedure)
    warnings = result.get("qa_warnings") or []
    assert any("31627" in warning for warning in warnings), warnings
    codes = result["codes"]
    nav_code = next(code for code in codes if code["cpt"] in ("31627", "+31627"))
    assert nav_code.get("qa_flags")
