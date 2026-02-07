from __future__ import annotations

from modules.reporter import ReportEngine
from modules.reporter.engine import ReporterEngine
from modules.reporter.schema import StructuredReport


def test_legacy_reporter_import_surface_is_available() -> None:
    assert ReportEngine is not None
    assert ReporterEngine is not None


def test_legacy_report_engine_from_free_text_and_render() -> None:
    engine = ReportEngine()
    report = engine.from_free_text("Diagnostic bronchoscopy with lavage was performed.")

    assert isinstance(report, StructuredReport)
    assert report.indication
    rendered = engine.render(report, template="bronchoscopy")
    assert "Bronchoscopy Synoptic Report" in rendered
