from __future__ import annotations

import pytest

from app.reporting.engine import ReporterEngine, _load_procedure_order, default_schema_registry, default_template_registry
from app.reporting.macro_registry import get_macro_registry
from app.reporting.pipeline import _clean_shell_specimens_text, _clean_shell_text


def _engine() -> ReporterEngine:
    return ReporterEngine(
        default_template_registry(),
        default_schema_registry(),
        procedure_order=_load_procedure_order(),
        render_style="builder",
        macro_registry=get_macro_registry(),
    )


def test_validate_style_allows_approved_redaction_placeholders_and_complications_none() -> None:
    engine = _engine()

    engine._validate_style(
        "DATE OF PROCEDURE: [Date]\n"
        "CC Referred Physician: [Name]\n"
        "INDICATION FOR OPERATION [Patient Name] is a [Age]-year-old [Sex] who presents with cough.\n"
        "COMPLICATIONS None\n"
    )


def test_validate_style_rejects_unknown_bracket_placeholder() -> None:
    engine = _engine()

    with pytest.raises(ValueError, match="Bracketed placeholder text remains"):
        engine._validate_style("ANESTHESIA [General anesthesia / airway type]")


def test_clean_shell_text_strips_inline_metadata_tail() -> None:
    cleaned = _clean_shell_text("ROSE Suspicious for malignancy, Complications: None, EBL: <10mL Dispo: Home")

    assert cleaned == "ROSE Suspicious for malignancy"


def test_clean_shell_specimens_text_suppresses_literal_none() -> None:
    assert _clean_shell_specimens_text("None.") is None
