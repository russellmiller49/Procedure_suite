"""Structured report engine that wraps LLM inference and templating."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import prompts
from .schema import StructuredReport

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


class LLMInterface(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class DeterministicStubLLM:
    """Simple deterministic LLM stub used for tests and local runs."""

    def __init__(self, payload: dict | None = None) -> None:
        self.payload = payload or {
            "indication": "Peripheral nodule",
            "anesthesia": "Moderate Sedation",
            "survey": ["Airways inspected"],
            "localization": "Navigated to RUL",
            "sampling": ["EBUS 4R"],
            "therapeutics": ["Stent RMB"],
            "complications": [],
            "disposition": "Home",
        }

    def generate(self, prompt: str) -> str:  # pragma: no cover - trivial
        return json.dumps(self.payload)


class ReportEngine:
    """Handles NL→structured conversion, validation, and rendering."""

    def __init__(self, llm: LLMInterface | None = None) -> None:
        self.llm = llm or DeterministicStubLLM()
        self._jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=select_autoescape(enabled_extensions=("jinja", "md")),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def from_free_text(self, note: str) -> StructuredReport:
        prompt_text = prompts.build_prompt(note)
        raw = self.llm.generate(prompt_text)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = self._fallback_payload()
        payload = self._normalize_payload(payload)
        report = StructuredReport(**payload)
        return self.validate_and_autofix(report)

    def validate_and_autofix(self, report: StructuredReport) -> StructuredReport:
        data = report.model_dump()
        for key in ("survey", "sampling", "therapeutics", "complications"):
            value = data.get(key)
            if not isinstance(value, list):
                data[key] = []
        for field in ("indication", "anesthesia", "localization", "disposition"):
            if not data.get(field):
                data[field] = "Unknown"

        if "stent" in " ".join(data["therapeutics"]).lower() and not data["sampling"]:
            data["sampling"].append("Stent site documented")

        return StructuredReport(**data)

    def render(self, report: StructuredReport, template: str = "bronchoscopy") -> str:
        template_name = {
            "bronchoscopy": "bronchoscopy_synoptic.md.jinja",
            "pleural": "pleural_synoptic.md.jinja",
            "blvr": "blvr_synoptic.md.jinja",
        }.get(template, template)
        tpl = self._jinja_env.get_template(template_name)
        return tpl.render(report=report)

    @staticmethod
    def _fallback_payload() -> dict:
        return {
            "indication": "Unknown",
            "anesthesia": "Unknown",
            "survey": [],
            "localization": "Unknown",
            "sampling": [],
            "therapeutics": [],
            "complications": [],
            "disposition": "Unknown",
        }

    @staticmethod
    def _normalize_payload(payload: dict | object) -> dict:
        if not isinstance(payload, dict):
            return ReportEngine._fallback_payload()
        data = ReportEngine._fallback_payload() | payload
        for key in ("survey", "sampling", "therapeutics", "complications"):
            value = data.get(key)
            if isinstance(value, list):
                continue
            if value in (None, ""):
                data[key] = []
            else:
                data[key] = [str(value)]
        return data


__all__ = ["ReportEngine", "DeterministicStubLLM", "LLMInterface"]
