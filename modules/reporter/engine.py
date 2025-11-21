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

    KNOWN_TEMPLATES = {
        "bronchoscopy": "bronchoscopy_synoptic.md.jinja",
        "pleural": "pleural_synoptic.md.jinja",
        "blvr": "blvr_synoptic.md.jinja",
    }
    KNOWLEDGE_TEMPLATE = Path(__file__).resolve().parents[2] / "data" / "knowledge" / "comprehensive_ip_procedural_templates9_18.md"

    def __init__(self, llm: LLMInterface | None = None) -> None:
        if llm:
            self.llm = llm
        else:
            use_oauth = os.getenv("GEMINI_USE_OAUTH", "").lower() in ("true", "1", "yes")
            api_key = os.getenv("GEMINI_API_KEY")
            model = os.getenv("GEMINI_MODEL")
            
            if use_oauth:
                logger.info("Initializing GeminiLLM with OAuth2/service account authentication.")
                try:
                    self.llm = GeminiLLM(use_oauth=True, model=model)
                except Exception as e:
                    logger.error(f"Failed to initialize OAuth2 authentication: {e}")
                    logger.warning("Falling back to DeterministicStubLLM.")
                    self.llm = DeterministicStubLLM()
            elif api_key:
                logger.info("Initializing GeminiLLM with API key from environment.")
                self.llm = GeminiLLM(api_key=api_key, model=model)
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
        if template in ("knowledge", "comprehensive", "comprehensive_ip"):
            return self._render_knowledge_template(report)

        template_name = self.KNOWN_TEMPLATES.get(template, template)
        tpl = self._jinja_env.get_template(template_name)
        return tpl.render(report=report)

    def _render_knowledge_template(self, report: StructuredReport) -> str:
        """Render using the comprehensive IP knowledge document as the body."""
        if self.KNOWLEDGE_TEMPLATE.exists():
            raw_body = self.KNOWLEDGE_TEMPLATE.read_text(encoding="utf-8")
        else:
            raw_body = "Comprehensive IP knowledge template not found."

        body = self._select_relevant_sections(raw_body, report)

        # Use a simple Jinja template built from the knowledge document content.
        tpl = self._jinja_env.from_string(
            "# Comprehensive IP Report\n"
            "## Summary\n"
            "- Indication: {{ report.indication }}\n"
            "- Anesthesia: {{ report.anesthesia }}\n"
            "- Localization: {{ report.localization }}\n"
            "- Sampling: {% if report.sampling %}{{ report.sampling | join(', ') }}{% else %}None{% endif %}\n"
            "- Therapeutics: {% if report.therapeutics %}{{ report.therapeutics | join(', ') }}{% else %}None{% endif %}\n"
            "- Complications: {% if report.complications %}{{ report.complications | join(', ') }}{% else %}None{% endif %}\n"
            "- Disposition: {{ report.disposition }}\n\n"
            "---\n"
            "## Reference Language (auto-inserted from knowledge file)\n"
            "{{ body }}\n"
        )
        return tpl.render(report=report, body=body)

    @staticmethod
    def _select_relevant_sections(body: str, report: StructuredReport, max_sections: int = 3) -> str:
        """Pick relevant template sections instead of dumping the entire knowledge file."""
        # Split on common separators; keep non-empty blocks
        blocks = [blk.strip() for blk in body.split("\n---") if blk.strip()]
        if not blocks:
            return body

        keywords: set[str] = set()
        fields = [
            report.indication,
            report.localization,
            " ".join(report.sampling or []),
            " ".join(report.therapeutics or []),
        ]
        for field in fields:
            for token in field.split():
                token = token.strip().lower()
                if len(token) >= 4 and token.isalpha():
                    keywords.add(token)

        # Score blocks by keyword hits
        scored: list[tuple[int, str]] = []
        for blk in blocks:
            lower_blk = blk.lower()
            score = sum(1 for kw in keywords if kw in lower_blk)
            scored.append((score, blk))

        scored.sort(key=lambda item: item[0], reverse=True)
        top_blocks = [blk for score, blk in scored if score > 0][:max_sections]
        if not top_blocks:
            top_blocks = blocks[:max_sections]

        return "\n\n---\n\n".join(top_blocks)

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
