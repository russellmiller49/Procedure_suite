"""Template rendering tests for StructuredReport."""

from modules.reporter.engine import ReportEngine
from modules.reporter.schema import StructuredReport


def sample_report() -> StructuredReport:
    return StructuredReport(
        indication="Peripheral lesion",
        anesthesia="Moderate Sedation",
        survey=["Airways normal"],
        localization="RUL nodule",
        sampling=["TBNA 4R"],
        therapeutics=["Stent RMB"],
        complications=["None"],
        disposition="Home",
    )


def test_bronchoscopy_template_renders():
    engine = ReportEngine()
    output = engine.render(sample_report(), template="bronchoscopy")
    assert "Bronchoscopy Synoptic Report" in output
    assert "Stent RMB" in output


def test_pleural_and_blvr_templates_render():
    engine = ReportEngine()
    report = sample_report()
    pleural = engine.render(report, template="pleural")
    blvr = engine.render(report, template="blvr")
    assert "Pleural Procedure Synoptic Report" in pleural
    assert "BLVR Synoptic Report" in blvr

