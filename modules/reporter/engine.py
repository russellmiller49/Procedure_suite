"""Deprecated compatibility shim for reporter imports."""

from __future__ import annotations

from pathlib import Path
import warnings
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from modules.reporting.engine import *  # noqa: F401,F403
from modules.reporting.engine import ReporterEngine, compose_report_from_text

from .schema import StructuredReport

_LEGACY_TEMPLATE_ROOT = Path(__file__).parent / "templates"
_LEGACY_ENV = Environment(
    loader=FileSystemLoader(str(_LEGACY_TEMPLATE_ROOT)),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)

_LEGACY_TEMPLATE_MAP = {
    "bronchoscopy": "bronchoscopy_synoptic.md.jinja",
    "pleural": "pleural_synoptic.md.jinja",
    "blvr": "blvr_synoptic.md.jinja",
}


def _as_text(value: Any, default: str = "") -> str:
    if value in (None, "", [], {}):
        return default
    if isinstance(value, str):
        return value
    return str(value)


class ReportEngine:
    """Backwards-compatible legacy report engine wrapper."""

    def from_free_text(self, text: str) -> StructuredReport:
        report, _ = compose_report_from_text(text, {})
        core = report.procedure_core
        indication = _as_text((report.indication or {}).get("text"), "Clinical evaluation")
        anesthesia = _as_text((report.meta or {}).get("anesthesia"), "See anesthesia record")
        targets = [str(item) for item in (core.targets or []) if str(item)]
        survey = [f"Target: {item}" for item in targets] if targets else ["Airway survey completed"]
        sampling = [f"Sampled target: {item}" for item in targets] if targets else []
        disposition = _as_text((report.postop or {}).get("plan"), "Observation and follow-up as needed")

        return StructuredReport(
            indication=indication,
            anesthesia=anesthesia,
            survey=survey,
            localization=_as_text(core.laterality, "See procedural narrative"),
            sampling=sampling,
            therapeutics=[],
            complications=[],
            disposition=disposition,
            metadata={
                "source": "modules.reporter.ReportEngine shim",
                "procedure_type": _as_text(core.type, "bronchoscopy"),
            },
        )

    def validate_and_autofix(self, report: StructuredReport | dict[str, Any]) -> StructuredReport:
        if isinstance(report, StructuredReport):
            return report
        return StructuredReport.model_validate(report)

    def render(self, report: StructuredReport, template: str = "bronchoscopy") -> str:
        normalized = self.validate_and_autofix(report)
        template_name = _LEGACY_TEMPLATE_MAP.get(template, template)
        if not template_name.endswith(".jinja"):
            template_name = f"{template_name}.md.jinja"
        try:
            tmpl = _LEGACY_ENV.get_template(template_name)
        except TemplateNotFound as exc:
            raise ValueError(f"Unknown legacy reporter template: {template}") from exc
        return tmpl.render(report=normalized).strip()


warnings.warn(
    "modules.reporter.engine is deprecated; please import from modules.reporting.engine instead.",
    DeprecationWarning,
    stacklevel=2,
)


__all__ = ["ReportEngine", "ReporterEngine"]
