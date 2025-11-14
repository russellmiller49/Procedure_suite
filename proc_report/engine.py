"""Pure report composition functions backed by Jinja templates."""

from __future__ import annotations

import hashlib
from copy import deepcopy
from pathlib import Path
from typing import Dict, Tuple, Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from proc_schemas.procedure_report import ProcedureReport, ProcedureCore, NLPTrace
from proc_nlp.normalize_proc import normalize_dictation
from proc_nlp.umls_linker import umls_link

_TEMPLATE_ROOT = Path(__file__).parent / "templates"
_TEMPLATE_MAP = {
    "ebus_tbna": "ebus_tbna.jinja",
    "bronchoscopy": "bronchoscopy.jinja",
    "robotic_nav": "bronchoscopy.jinja",
    "cryobiopsy": "cryobiopsy.jinja",
    "thoracentesis": "thoracentesis.jinja",
    "ipc": "ipc.jinja",
    "pleuroscopy": "pleuroscopy.jinja",
    "stent": "stent.jinja",
}

_ENV = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_ROOT)),
    autoescape=select_autoescape(default=False),
    trim_blocks=True,
    lstrip_blocks=True,
)


def compose_report_from_text(text: str, hints: Dict[str, Any] | None = None) -> Tuple[ProcedureReport, str]:
    """Normalize dictation + hints into a ProcedureReport and Markdown note."""
    hints = deepcopy(hints or {})
    normalized_core = normalize_dictation(text, hints)
    procedure_core = ProcedureCore(**normalized_core)
    umls = [_serialize_concept(concept) for concept in umls_link(text)]
    paragraph_hashes = _hash_paragraphs(text)
    nlp = NLPTrace(paragraph_hashes=paragraph_hashes, umls=umls)

    report = ProcedureReport(
        meta={"source": "dictation", "hints": hints},
        indication={"text": hints.get("indication", "Clinical evaluation")},
        procedure_core=procedure_core,
        intraop={"narrative": text},
        postop={"plan": hints.get("plan", "Observation and follow-up as needed")},
        nlp=nlp,
    )
    note_md = _render_note(report)
    return report, note_md


def compose_report_from_form(form: Dict[str, Any] | ProcedureReport) -> Tuple[ProcedureReport, str]:
    """Accept structured dicts/forms and hydrate a ProcedureReport."""
    if isinstance(form, ProcedureReport):
        report = form
    else:
        payload = deepcopy(form)
        core = payload.get("procedure_core")
        if not core:
            raise ValueError("form must contain procedure_core")
        if not isinstance(core, ProcedureCore):
            core = ProcedureCore(**core)
        payload["procedure_core"] = core
        nlp_payload = payload.get("nlp")
        if nlp_payload and not isinstance(nlp_payload, NLPTrace):
            payload["nlp"] = NLPTrace(**nlp_payload)
        elif not nlp_payload:
            text = _extract_text(payload)
            payload["nlp"] = NLPTrace(
                paragraph_hashes=_hash_paragraphs(text),
                umls=[_serialize_concept(concept) for concept in umls_link(text)],
            )
        report = ProcedureReport(**payload)
    note_md = _render_note(report)
    return report, note_md


def _extract_text(payload: Dict[str, Any]) -> str:
    intraop = payload.get("intraop") or {}
    return str(intraop.get("narrative", ""))


def _hash_paragraphs(text: str) -> list[str]:
    paragraphs = [p.strip() for p in (text or "").splitlines() if p.strip()]
    return [hashlib.sha1(p.encode("utf-8")).hexdigest() for p in paragraphs]


def _render_note(report: ProcedureReport) -> str:
    template_name = _TEMPLATE_MAP.get(report.procedure_core.type, "bronchoscopy.jinja")
    template = _ENV.get_template(template_name)
    context = {
        "report": report,
        "core": report.procedure_core,
        "targets": report.procedure_core.targets,
        "meta": report.meta,
        "summarize_specimens": _summarize_specimens,
    }
    return template.render(**context)


def _summarize_specimens(specimens: Dict[str, Any]) -> str:
    if not specimens:
        return "N/A"
    return ", ".join(f"{key}: {value}" for key, value in specimens.items())


def _serialize_concept(concept: Any) -> Dict[str, Any]:
    if isinstance(concept, dict):
        return concept
    attrs = getattr(concept, "__dict__", None)
    if isinstance(attrs, dict):
        return attrs
    return {"text": str(concept)}


__all__ = ["compose_report_from_text", "compose_report_from_form"]
