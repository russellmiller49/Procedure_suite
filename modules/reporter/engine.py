"""Structured report engine that wraps LLM inference and templating."""

from __future__ import annotations

import json
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from modules.common.llm import GeminiLLM, LLMInterface, DeterministicStubLLM
from modules.common.logger import get_logger
from . import prompts
from .schema import StructuredReport

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
logger = get_logger("reporter")


class ReportEngine:
    """Handles NL→structured conversion, validation, and rendering."""

    def __init__(self, llm: LLMInterface | None = None) -> None:
        if llm:
            self.llm = llm
        else:
            use_oauth = os.getenv("GEMINI_USE_OAUTH", "").lower() in ("true", "1", "yes")
            api_key = os.getenv("GEMINI_API_KEY")
            
            if use_oauth:
                logger.info("Initializing GeminiLLM with OAuth2/service account authentication.")
                try:
                    self.llm = GeminiLLM(use_oauth=True)
                except Exception as e:
                    logger.error(f"Failed to initialize OAuth2 authentication: {e}")
                    logger.warning("Falling back to DeterministicStubLLM.")
                    self.llm = DeterministicStubLLM()
            elif api_key:
                logger.info("Initializing GeminiLLM with API key from environment.")
                self.llm = GeminiLLM(api_key=api_key)
            else:
                logger.warning("GEMINI_API_KEY not found and GEMINI_USE_OAUTH not set. Falling back to DeterministicStubLLM.")
                self.llm = DeterministicStubLLM()

        self._jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=select_autoescape(enabled_extensions=("jinja", "md")),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def from_free_text(self, note: str) -> StructuredReport:
        logger.info(f"Generating report from note (length: {len(note)})")
        prompt_text = prompts.build_prompt(note)
        raw = self.llm.generate(prompt_text)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON. Falling back to default.")
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


class ReporterEngine(ReportEngine):
    """Compatibility shim exposing a ReporterEngine-friendly signature."""

    def __init__(self, model: LLMInterface | None = None) -> None:
        super().__init__(llm=model)


__all__ = ["ReportEngine", "ReporterEngine"]

