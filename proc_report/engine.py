"""Pure report composition functions backed by Jinja templates."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from dataclasses import dataclass, field
from copy import deepcopy
import functools
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple, Literal

from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound, select_autoescape
from pydantic import BaseModel

import proc_schemas.clinical.airway as airway_schemas
import proc_schemas.clinical.pleural as pleural_schemas
from proc_schemas.clinical import (
    AnesthesiaInfo,
    BundlePatch,
    EncounterInfo,
    OperativeShellInputs,
    PatientInfo,
    PreAnesthesiaAssessment,
    ProcedureBundle,
    ProcedureInput,
    ProcedurePatch,
    SedationInfo,
)
from proc_schemas.procedure_report import ProcedureReport, ProcedureCore, NLPTrace
from proc_registry.adapters import AdapterRegistry
import proc_registry.adapters.airway  # noqa: F401
import proc_registry.adapters.pleural  # noqa: F401
from proc_nlp.normalize_proc import normalize_dictation
from proc_nlp.umls_linker import umls_link
from proc_report.metadata import (
    MissingFieldIssue,
    ProcedureAutocodeResult,
    ProcedureMetadata,
    ReportMetadata,
    StructuredReport,
    metadata_to_dict,
)
from proc_report.inference import InferenceEngine, PatchResult
from proc_report.validation import FieldConfig, ValidationEngine

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


# --- Structured reporter (template-driven) ---

_CONFIG_TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "configs" / "report_templates"
_DEFAULT_ORDER_PATH = _CONFIG_TEMPLATE_ROOT / "procedure_order.json"


def join_nonempty(values: Iterable[str], sep: str = ", ") -> str:
    """Join values while skipping empty/None entries."""
    return sep.join([v for v in values if v])


def _pronoun(sex: str | None, *, subject: bool = True) -> str:
    if not sex:
        return "they"
    normalized = sex.strip().lower()
    if normalized.startswith("f"):
        return "she" if subject else "her"
    if normalized.startswith("m"):
        return "he" if subject else "him"
    return "they" if subject else "them"


def _fmt_ml(value: Any) -> str:
    if value in (None, ""):
        return ""
    try:
        num = float(value)
        if num.is_integer():
            num = int(num)
        return f"{num} mL"
    except Exception:
        return str(value)


def _fmt_unit(value: Any, unit: str) -> str:
    if value in (None, ""):
        return ""
    try:
        num = float(value)
        if num.is_integer():
            num = int(num)
        return f"{num} {unit}"
    except Exception:
        return f"{value} {unit}"


def _build_structured_env(template_root: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(template_root)),
        autoescape=select_autoescape(default=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["join_nonempty"] = join_nonempty
    env.filters["pronoun"] = _pronoun
    env.filters["fmt_ml"] = _fmt_ml
    env.filters["fmt_unit"] = _fmt_unit
    return env


@dataclass
class TemplateMeta:
    id: str
    label: str
    category: str
    cpt_hints: list[str]
    schema_id: str
    output_section: str
    required_fields: list[str]
    optional_fields: list[str]
    template: Template
    proc_types: list[str] = field(default_factory=list)
    critical_fields: list[str] = field(default_factory=list)
    recommended_fields: list[str] = field(default_factory=list)
    template_path: Path | None = None
    field_configs: dict[str, FieldConfig] = field(default_factory=dict)


def _dedupe(items: Iterable[TemplateMeta]) -> list[TemplateMeta]:
    seen: set[str] = set()
    ordered: list[TemplateMeta] = []
    for meta in items:
        if meta.id in seen:
            continue
        seen.add(meta.id)
        ordered.append(meta)
    return ordered


class TemplateRegistry:
    """Load and index procedure templates from config files."""

    def __init__(self, env: Environment, root: Path | None = None) -> None:
        self.env = env
        self.root = root
        self._by_id: dict[str, TemplateMeta] = {}
        self._by_cpt: dict[str, list[TemplateMeta]] = {}
        self._by_proc_type: dict[str, list[TemplateMeta]] = {}

    def load_from_configs(self, root: Path) -> None:
        self.root = root
        if not root.exists():
            return
        for meta_path in sorted(root.iterdir()):
            if meta_path.suffix.lower() not in {".json", ".yaml", ".yml"}:
                continue
            payload = self._load_meta(meta_path)
            if "template_path" not in payload:
                # Skip config helpers such as procedure_order.json
                continue
            template_rel = payload["template_path"]
            try:
                template = self.env.get_template(template_rel)
            except TemplateNotFound as exc:
                raise FileNotFoundError(f"Template '{template_rel}' referenced in {meta_path.name} not found under {self.root}") from exc
            raw_fields = payload.get("fields", {}) or {}
            field_configs = {path: FieldConfig.from_template(path, cfg) for path, cfg in raw_fields.items()}
            required_fields = payload.get("required_fields", [])
            if not required_fields and field_configs:
                required_fields = [path for path, cfg in field_configs.items() if cfg.required]
            critical_fields = payload.get("critical_fields", [])
            if not critical_fields and field_configs:
                critical_fields = [path for path, cfg in field_configs.items() if cfg.critical]
            recommended_fields = payload.get("recommended_fields", [])
            if not recommended_fields and field_configs:
                recommended_fields = [path for path, cfg in field_configs.items() if cfg.required and not cfg.critical]
            meta = TemplateMeta(
                id=payload["id"],
                label=payload.get("label", payload["id"]),
                category=payload.get("category", ""),
                cpt_hints=[str(item) for item in payload.get("cpt_hints", [])],
                schema_id=payload["schema_id"],
                output_section=payload.get("output_section", "PROCEDURE_DETAILS"),
                required_fields=required_fields,
                optional_fields=payload.get("optional_fields", []),
                template=template,
                proc_types=payload.get("proc_types", []),
                critical_fields=critical_fields,
                recommended_fields=recommended_fields,
                template_path=meta_path,
                field_configs=field_configs,
            )
            self._register(meta)

    def _register(self, meta: TemplateMeta) -> None:
        self._by_id[meta.id] = meta
        for code in meta.cpt_hints:
            self._by_cpt.setdefault(code, []).append(meta)
        for proc_type in meta.proc_types:
            self._by_proc_type.setdefault(proc_type, []).append(meta)

    def _load_meta(self, path: Path) -> dict[str, Any]:
        if path.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore
            except ImportError as exc:  # pragma: no cover - optional dep
                raise RuntimeError("PyYAML is required to load YAML template configs") from exc
            return yaml.safe_load(path.read_text())
        return json.loads(path.read_text())

    def find_for_procedure(self, proc_type: str, cpt_codes: Sequence[str | int] | None = None) -> list[TemplateMeta]:
        matches = list(self._by_proc_type.get(proc_type, []))
        if matches:
            return _dedupe(matches)
        codes = [str(code) for code in (cpt_codes or [])]
        for code in codes:
            matches.extend(self._by_cpt.get(code, []))
        return _dedupe(matches)

    def get(self, template_id: str) -> TemplateMeta | None:
        return self._by_id.get(template_id)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._by_id)


class SchemaRegistry:
    """Map schema IDs to Pydantic models used for validation."""

    def __init__(self) -> None:
        self._schemas: dict[str, type[BaseModel]] = {}

    def register(self, schema_id: str, model: type[BaseModel]) -> None:
        self._schemas[schema_id] = model

    def get(self, schema_id: str) -> type[BaseModel]:
        if schema_id not in self._schemas:
            raise KeyError(f"Schema not registered: {schema_id}")
        return self._schemas[schema_id]



class ReporterEngine:
    """Render structured procedure bundles into notes using template configs."""

    def __init__(
        self,
        template_registry: TemplateRegistry,
        schema_registry: SchemaRegistry,
        *,
        procedure_order: dict[str, int] | None = None,
        shell_template_id: str | None = "ip_or_main_oper_report_shell",
    ) -> None:
        self.templates = template_registry
        self.schemas = schema_registry
        self.procedure_order = procedure_order or {}
        self.shell_template_id = shell_template_id

    def compose_report(self, bundle: ProcedureBundle, *, strict: bool = False) -> str:
        structured = self.compose_report_with_metadata(bundle, strict=strict, embed_metadata=False)
        return structured.text

    def compose_report_with_metadata(
        self,
        bundle: ProcedureBundle,
        *,
        strict: bool = False,
        validation_issues: list[MissingFieldIssue] | None = None,
        warnings: list[str] | None = None,
        embed_metadata: bool = False,
        autocode_result: ProcedureAutocodeResult | None = None,
    ) -> StructuredReport:
        note, metadata = self._compose_internal(bundle, strict=strict, autocode_result=autocode_result)
        if validation_issues:
            _attach_validation_metadata(metadata, validation_issues)
        output_text = _embed_metadata(note, metadata) if embed_metadata else note
        return StructuredReport(
            text=output_text,
            metadata=metadata,
            warnings=warnings or [],
            issues=validation_issues or [],
        )

    def _compose_internal(
        self,
        bundle: ProcedureBundle,
        *,
        strict: bool = False,
        autocode_result: ProcedureAutocodeResult | None = None,
    ) -> tuple[str, ReportMetadata]:
        sections: dict[str, list[str]] = {
            "HEADER": [],
            "PRE_ANESTHESIA": [],
            "PROCEDURE_DETAILS": [],
            "INSTRUCTIONS": [],
            "DISCHARGE": [],
        }
        procedure_labels: list[str] = []
        bronchoscopy_blocks: list[str] = []
        bronchoscopy_shells: list[tuple[TemplateMeta, ProcedureInput, ProcedureMetadata]] = []
        discharge_templates: dict[str, list[ProcedureMetadata]] = {}
        procedures_metadata: list[ProcedureMetadata] = []

        autocode_payload = autocode_result or _try_proc_autocode(bundle)
        autocode_codes = [str(code) for code in autocode_payload.get("cpt", [])] if autocode_payload else []
        autocode_modifiers = [str(mod) for mod in autocode_payload.get("modifiers", [])] if autocode_payload else []
        unmatched_autocode = set(autocode_codes)

        pre_meta = self.templates.get("ip_pre_anesthesia_assessment")
        if pre_meta and bundle.pre_anesthesia:
            rendered = self._render_payload(pre_meta, bundle.pre_anesthesia, bundle)
            if rendered:
                sections["PRE_ANESTHESIA"].append(rendered)

        for proc in self._sorted_procedures(bundle.procedures):
            metas = self.templates.find_for_procedure(proc.proc_type, proc.cpt_candidates)
            label = metas[0].label if metas else proc.proc_type
            section = metas[0].output_section if metas else ""
            proc_meta = ProcedureMetadata(
                proc_id=proc.proc_id or proc.schema_id,
                proc_type=proc.proc_type,
                label=label,
                cpt_candidates=[],
                icd_candidates=[],
                modifiers=[],
                section=section,
                templates_used=[],
                has_critical_missing=False,
                missing_critical_fields=[],
                extra={"data": _normalize_payload(proc.data)},
            )
            procedures_metadata.append(proc_meta)

            if not metas:
                proc_meta.has_critical_missing = True
                proc_meta.missing_critical_fields.append("template_missing")
                continue

            for meta in metas:
                if not proc_meta.label:
                    proc_meta.label = meta.label
                if not proc_meta.section:
                    proc_meta.section = meta.output_section

                if meta.id == "ip_general_bronchoscopy_shell":
                    cpts, modifiers = _merge_cpt_sources(proc, meta, autocode_payload)
                    proc_meta.cpt_candidates = _merge_str_lists(proc_meta.cpt_candidates, cpts)
                    proc_meta.modifiers = _merge_str_lists(proc_meta.modifiers, modifiers or autocode_modifiers)
                    proc_meta.icd_candidates = _merge_str_lists(
                        proc_meta.icd_candidates, autocode_payload.get("icd", []) if autocode_payload else []
                    )
                    proc_meta.templates_used = _merge_str_lists(proc_meta.templates_used, [meta.id])
                    for code in cpts:
                        unmatched_autocode.discard(code)
                    bronchoscopy_shells.append((meta, proc, proc_meta))
                    continue
                # Track discharge/instructions attachments based on procedures
                if meta.id in ("tunneled_pleural_catheter_insert", "ipc_insert"):
                    discharge_templates.setdefault("pleurx_instructions", []).append(proc_meta)
                if meta.id == "blvr_valve_placement":
                    discharge_templates.setdefault("blvr_discharge_instructions", []).append(proc_meta)
                if meta.id in ("chest_tube", "pigtail_catheter"):
                    discharge_templates.setdefault("chest_tube_discharge", []).append(proc_meta)
                if meta.id in ("peg_placement",):
                    discharge_templates.setdefault("peg_discharge", []).append(proc_meta)

                rendered = self._render_procedure_template(meta, proc, bundle)
                proc_meta.templates_used = _merge_str_lists(proc_meta.templates_used, [meta.id])
                cpts, modifiers = _merge_cpt_sources(proc, meta, autocode_payload)
                proc_meta.cpt_candidates = _merge_str_lists(proc_meta.cpt_candidates, cpts)
                proc_meta.modifiers = _merge_str_lists(proc_meta.modifiers, modifiers or autocode_modifiers)
                proc_meta.icd_candidates = _merge_str_lists(
                    proc_meta.icd_candidates, autocode_payload.get("icd", []) if autocode_payload else []
                )
                for code in cpts:
                    unmatched_autocode.discard(code)

                if not rendered:
                    continue
                if meta.output_section == "PROCEDURE_DETAILS":
                    procedure_labels.append(meta.label)
                if meta.category == "bronchoscopy":
                    bronchoscopy_blocks.append(rendered)
                else:
                    sections.setdefault(meta.output_section, []).append(rendered)

        if bronchoscopy_blocks:
            joined_bronch = self._join_blocks(bronchoscopy_blocks)
            if bronchoscopy_shells:
                for meta, proc, proc_meta in bronchoscopy_shells:
                    cpts, modifiers = _merge_cpt_sources(proc, meta, autocode_payload)
                    proc_meta.cpt_candidates = _merge_str_lists(proc_meta.cpt_candidates, cpts)
                    proc_meta.modifiers = _merge_str_lists(proc_meta.modifiers, modifiers or autocode_modifiers)
                    proc_meta.icd_candidates = _merge_str_lists(
                        proc_meta.icd_candidates, autocode_payload.get("icd", []) if autocode_payload else []
                    )
                    proc_meta.templates_used = _merge_str_lists(proc_meta.templates_used, [meta.id])
                    for code in cpts:
                        unmatched_autocode.discard(code)
                    rendered = self._render_procedure_template(
                        meta,
                        proc,
                        bundle,
                        extra_context={
                            "procedure_details": joined_bronch,
                            "procedures_summary": ", ".join(_dedupe_labels(procedure_labels)),
                        },
                    )
                    if rendered:
                        if meta.output_section == "PROCEDURE_DETAILS":
                            procedure_labels.append(meta.label)
                        sections.setdefault(meta.output_section, []).append(rendered)
            else:
                sections["PROCEDURE_DETAILS"].append(joined_bronch)

        # Attach discharge/education templates driven by procedure presence
        for discharge_id, owners in discharge_templates.items():
            discharge_meta = self.templates.get(discharge_id)
            if discharge_meta:
                rendered = self._render_payload(discharge_meta, {}, bundle)
                if rendered:
                    sections.setdefault(discharge_meta.output_section, []).append(rendered)
                    for owner in owners:
                        owner.templates_used = _merge_str_lists(owner.templates_used, [discharge_id])

        shell = self.templates.get(self.shell_template_id) if self.shell_template_id else None
        if shell:
            procedure_details_block = self._join_blocks(
                sections.get("PRE_ANESTHESIA", [])
                + sections.get("PROCEDURE_DETAILS", [])
                + sections.get("INSTRUCTIONS", [])
                + sections.get("DISCHARGE", [])
            )
            label_summary = ", ".join(_dedupe_labels(procedure_labels))
            cpt_summary = _summarize_cpt_candidates(procedures_metadata, unmatched_autocode)
            shell_payload = OperativeShellInputs(
                indication_text=bundle.indication_text,
                preop_diagnosis_text=bundle.preop_diagnosis_text,
                postop_diagnosis_text=bundle.postop_diagnosis_text,
                procedures_summary=label_summary,
                cpt_summary=cpt_summary,
                estimated_blood_loss=bundle.estimated_blood_loss,
                complications_text=bundle.complications_text,
                specimens_text=bundle.specimens_text,
                impression_plan=bundle.impression_plan,
            )
            shell_context = {
                "procedure_details_block": procedure_details_block,
            }
            rendered = self._render_payload(shell, shell_payload, bundle, extra_context=shell_context)
            if strict:
                self._validate_style(rendered)
            metadata = self._build_metadata(bundle, procedures_metadata, autocode_payload)
            return rendered, metadata

        note = self._join_sections(sections)
        if strict:
            self._validate_style(note)
        metadata = self._build_metadata(bundle, procedures_metadata, autocode_payload)
        return note, metadata

    def _sorted_procedures(self, procedures: Sequence[ProcedureInput]) -> list[ProcedureInput]:
        return sorted(
            procedures,
            key=lambda proc: (self.procedure_order.get(proc.proc_type, 10_000), proc.proc_type),
        )

    def _render_procedure_template(
        self,
        meta: TemplateMeta,
        proc: ProcedureInput,
        bundle: ProcedureBundle,
        *,
        extra_context: dict[str, Any] | None = None,
    ) -> str:
        model_cls = self.schemas.get(meta.schema_id)
        model = proc.data if isinstance(proc.data, BaseModel) else model_cls.model_validate(proc.data or {})
        self._check_required(meta, model)
        return self._render(meta, bundle, model, extra_context=extra_context)

    def _render_payload(
        self,
        meta: TemplateMeta,
        payload: BaseModel | dict[str, Any],
        bundle: ProcedureBundle,
        *,
        extra_context: dict[str, Any] | None = None,
    ) -> str:
        model_cls = self.schemas.get(meta.schema_id)
        model = payload if isinstance(payload, BaseModel) else model_cls.model_validate(payload or {})
        self._check_required(meta, model)
        return self._render(meta, bundle, model, extra_context=extra_context)

    def _render(
        self,
        meta: TemplateMeta,
        bundle: ProcedureBundle,
        model: BaseModel,
        *,
        extra_context: dict[str, Any] | None = None,
    ) -> str:
        context = {
            "patient": bundle.patient,
            "encounter": bundle.encounter,
            "proc": model,
            "sedation": bundle.sedation,
            "anesthesia": bundle.anesthesia,
            "indication_text": bundle.indication_text,
            "preop_diagnosis_text": bundle.preop_diagnosis_text,
            "postop_diagnosis_text": bundle.postop_diagnosis_text,
            "impression_plan": bundle.impression_plan,
        }
        if extra_context:
            context.update(extra_context)
        raw = meta.template.render(**context)
        return self._postprocess(raw)

    def _check_required(self, meta: TemplateMeta, model: BaseModel) -> None:
        missing: list[str] = []
        for field in meta.required_fields:
            value = getattr(model, field, None)
            if value in (None, "", [], {}):
                missing.append(field)
        if missing:
            raise ValueError(f"Missing required fields for {meta.id}: {missing}")

    def _join_blocks(self, blocks: Sequence[str]) -> str:
        cleaned = [block.strip() for block in blocks if block and block.strip()]
        return "\n\n".join(cleaned)

    def _join_sections(self, sections: Dict[str, list[str]]) -> str:
        ordered_sections = ["HEADER", "PRE_ANESTHESIA", "PROCEDURE_DETAILS", "INSTRUCTIONS", "DISCHARGE"]
        output: list[str] = []
        for section in ordered_sections:
            blocks = sections.get(section, [])
            if not blocks:
                continue
            header = section.replace("_", " ").title()
            output.append(header)
            output.append(self._join_blocks(blocks))
        return self._postprocess("\n\n".join(output))

    def _postprocess(self, raw: str) -> str:
        lines = []
        for line in raw.splitlines():
            stripped = line.strip()
            if not stripped:
                lines.append("")
                continue
            cleaned = re.sub(r"\s+([.,;:])", r"\1", stripped)
            cleaned = re.sub(r"\s{2,}", " ", cleaned)
            cleaned = cleaned.replace("..", ".")
            lines.append(cleaned)
        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _validate_style(self, text: str) -> None:
        """Raise if obvious formatting artifacts remain."""
        errors: list[str] = []
        if "{{" in text or "}}" in text:
            errors.append("Unrendered Jinja variables found.")
        if re.search(r"\[[^\]\n]{2,}\]", text):
            errors.append("Bracketed placeholder text remains.")
        if re.search(r"\bNone\b", text):
            errors.append("Literal 'None' found in rendered text.")
        if ".." in text:
            errors.append("Double periods found.")
        if re.search(r"\s{3,}", text):
            errors.append("Excessive spacing found.")
        if errors:
            raise ValueError("Style validation failed: " + "; ".join(errors))

    def _build_metadata(
        self,
        bundle: ProcedureBundle,
        procedures_metadata: list[ProcedureMetadata],
        autocode_payload: dict[str, Any] | ProcedureAutocodeResult | None,
    ) -> ReportMetadata:
        missing = list_missing_critical_fields(
            bundle,
            template_registry=self.templates,
            schema_registry=self.schemas,
        )
        missing_by_proc: dict[str, list[str]] = {}
        for issue in missing:
            missing_by_proc.setdefault(issue.proc_id, []).append(issue.field_path)

        for proc_meta in procedures_metadata:
            proc_missing = missing_by_proc.get(proc_meta.proc_id, [])
            proc_meta.missing_critical_fields = proc_missing
            proc_meta.has_critical_missing = bool(proc_missing)

        return ReportMetadata(
            patient_id=bundle.patient.patient_id,
            mrn=bundle.patient.mrn,
            encounter_id=bundle.encounter.encounter_id,
            date_of_procedure=_parse_date(bundle.encounter.date),
            attending=bundle.encounter.attending,
            location=bundle.encounter.location,
            procedures=procedures_metadata,
            autocode_payload=autocode_payload or {},
        )


def _dedupe_labels(labels: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for label in labels:
        if label in seen:
            continue
        seen.add(label)
        ordered.append(label)
    return ordered


def _merge_str_lists(existing: Sequence[str] | None, new: Sequence[str] | None) -> list[str]:
    merged: list[str] = list(existing or [])
    for item in new or []:
        val = str(item)
        if val and val not in merged:
            merged.append(val)
    return merged


def _normalize_payload(payload: BaseModel | dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {}
    if isinstance(payload, BaseModel):
        return payload.model_dump(exclude_none=True)
    if isinstance(payload, dict):
        return {k: v for k, v in payload.items() if v not in (None, "", [], {})}
    return {"value": payload}


def apply_patch_result(bundle: ProcedureBundle, result: PatchResult) -> ProcedureBundle:
    changes = result.changes or {}
    updated = bundle
    procedure_changes = changes.get("procedures", {}) or {}
    if procedure_changes:
        patch = BundlePatch(
            procedures=[
                ProcedurePatch(proc_id=proc_id, updates=updates or {}) for proc_id, updates in procedure_changes.items()
            ]
        )
        updated = apply_bundle_patch(updated, patch)
    bundle_updates = changes.get("bundle", {}) or {}
    if bundle_updates:
        data = updated.model_dump(exclude_none=False)
        data.update(bundle_updates)
        updated = ProcedureBundle.model_validate(data)
    return updated


def _attach_validation_metadata(metadata: ReportMetadata, issues: list[MissingFieldIssue]) -> None:
    issues_by_proc: dict[str, list[MissingFieldIssue]] = {}
    for issue in issues:
        issues_by_proc.setdefault(issue.proc_id, []).append(issue)
    for proc_meta in metadata.procedures:
        proc_issues = issues_by_proc.get(proc_meta.proc_id, [])
        if not proc_issues:
            continue
        warning_paths = [issue.field_path for issue in proc_issues if issue.severity in ("warning", "critical")]
        recommended_paths = [issue.field_path for issue in proc_issues if issue.severity == "recommended"]
        proc_meta.missing_critical_fields = warning_paths
        proc_meta.has_critical_missing = bool(warning_paths)
        if recommended_paths:
            proc_meta.extra.setdefault("recommended_missing", recommended_paths)


def _merge_cpt_sources(
    proc: ProcedureInput, meta: TemplateMeta, autocode_payload: dict[str, Any] | None
) -> tuple[list[str], list[str]]:
    candidates: list[str] = []
    modifiers: list[str] = []

    def _add(items: Sequence[Any] | None) -> None:
        for item in items or []:
            val = str(item)
            if val and val not in candidates:
                candidates.append(val)

    _add(proc.cpt_candidates)
    _add(meta.cpt_hints)

    if autocode_payload:
        auto_codes = [str(code) for code in autocode_payload.get("cpt", []) or []]
        hinted = set(proc.cpt_candidates or []) | set(meta.cpt_hints or [])
        if hinted:
            auto_codes = [code for code in auto_codes if code in hinted]
        _add(auto_codes)
        for mod in autocode_payload.get("modifiers", []) or []:
            mod_str = str(mod)
            if mod_str and mod_str not in modifiers:
                modifiers.append(mod_str)

    return candidates, modifiers


def _summarize_cpt_candidates(
    procedures: Sequence[ProcedureMetadata], unmatched_autocode: set[str] | Sequence[str] | None
) -> str:
    parts: list[str] = []
    for proc in procedures:
        if not proc.cpt_candidates and not proc.modifiers:
            continue
        codes = ", ".join(proc.cpt_candidates) if proc.cpt_candidates else "None"
        modifier_suffix = f" [modifiers: {', '.join(proc.modifiers)}]" if proc.modifiers else ""
        label = proc.label or proc.proc_type
        parts.append(f"{label}: {codes}{modifier_suffix}")
    unmatched = list(unmatched_autocode or [])
    if unmatched:
        parts.append(f"Unmapped autocode: {', '.join(sorted(set(unmatched)))}")
    return "; ".join(parts) if parts else "Not available (verify locally)"


def _parse_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    try:
        return dt.date.fromisoformat(value)
    except Exception:
        try:
            return dt.datetime.fromisoformat(value).date()
        except Exception:
            return None


def _embed_metadata(text: str, metadata: ReportMetadata) -> str:
    payload = metadata_to_dict(metadata)
    metadata_json = json.dumps(payload, sort_keys=True, indent=2)
    return "\n\n".join(
        [
            text.strip(),
            "---REPORT_METADATA_JSON_START---",
            metadata_json,
            "---REPORT_METADATA_JSON_END---",
        ]
    ).strip()


def _try_proc_autocode(bundle: ProcedureBundle) -> dict[str, Any] | None:
    note = getattr(bundle, "free_text_hint", None)
    if not note:
        return None
    try:
        from proc_autocode.engine import autocode
    except Exception:
        return None
    try:
        report, _ = compose_report_from_text(note, {})
        billing = autocode(report)
    except Exception:
        return None

    codes = [line.cpt for line in getattr(billing, "codes", []) or []]
    modifiers: list[str] = []
    for line in getattr(billing, "codes", []) or []:
        for mod in line.modifiers:
            if mod not in modifiers:
                modifiers.append(mod)
    payload: dict[str, Any] = {
        "cpt": codes,
        "modifiers": modifiers,
        "icd": [],
        "notes": "Generated via proc_autocode.engine.autocode",
    }
    if hasattr(billing, "model_dump"):
        payload["billing"] = billing.model_dump()
    return payload


def list_missing_critical_fields(
    bundle: ProcedureBundle,
    *,
    template_registry: TemplateRegistry | None = None,
    schema_registry: SchemaRegistry | None = None,
) -> list[MissingFieldIssue]:
    templates = template_registry or default_template_registry()
    schemas = schema_registry or default_schema_registry()
    validator = ValidationEngine(templates, schemas)
    return validator.list_missing_critical_fields(bundle)


def apply_warn_if_rules(
    bundle: ProcedureBundle,
    *,
    template_registry: TemplateRegistry | None = None,
    schema_registry: SchemaRegistry | None = None,
) -> list[str]:
    templates = template_registry or default_template_registry()
    schemas = schema_registry or default_schema_registry()
    validator = ValidationEngine(templates, schemas)
    return validator.apply_warn_if_rules(bundle)


def apply_bundle_patch(bundle: ProcedureBundle, patch: BundlePatch) -> ProcedureBundle:
    patch_map = {p.proc_id: p for p in patch.procedures}
    updated_procs: list[ProcedureInput] = []
    ack_map: dict[str, list[str]] = deepcopy(bundle.acknowledged_omissions)

    for proc in bundle.procedures:
        proc_id = proc.proc_id or proc.schema_id
        patch_item = patch_map.get(proc_id)
        if not patch_item:
            updated_procs.append(proc)
            continue
        data = _normalize_payload(proc.data)
        merged = {**data, **(patch_item.updates or {})}
        if isinstance(proc.data, BaseModel):
            try:
                new_data = proc.data.__class__(**merged)
            except Exception:
                new_data = merged
        else:
            new_data = merged
        updated_procs.append(
            ProcedureInput(
                proc_type=proc.proc_type,
                schema_id=proc.schema_id,
                proc_id=proc_id,
                data=new_data,
                cpt_candidates=list(proc.cpt_candidates),
            )
        )
        if patch_item.acknowledge_missing:
            ack_list = ack_map.get(proc_id, [])
            for field in patch_item.acknowledge_missing:
                if field not in ack_list:
                    ack_list.append(field)
            ack_map[proc_id] = ack_list

    return ProcedureBundle(
        patient=bundle.patient,
        encounter=bundle.encounter,
        procedures=updated_procs,
        sedation=bundle.sedation,
        anesthesia=bundle.anesthesia,
        pre_anesthesia=bundle.pre_anesthesia,
        indication_text=bundle.indication_text,
        preop_diagnosis_text=bundle.preop_diagnosis_text,
        postop_diagnosis_text=bundle.postop_diagnosis_text,
        impression_plan=bundle.impression_plan,
        estimated_blood_loss=bundle.estimated_blood_loss,
        complications_text=bundle.complications_text,
        specimens_text=bundle.specimens_text,
        free_text_hint=bundle.free_text_hint,
        acknowledged_omissions=ack_map,
    )


def _load_procedure_order(order_path: Path | None = None) -> dict[str, int]:
    path = order_path or _DEFAULT_ORDER_PATH
    if path.exists():
        try:
            raw = json.loads(path.read_text())
            return {str(k): int(v) for k, v in raw.items()}
        except Exception:
            return {}
    return {}


def _template_config_hash(root: Path) -> str:
    hasher = hashlib.sha256()
    if not root.exists():
        return ""
    exts = {".json", ".yaml", ".yml", ".j2", ".jinja"}
    for meta_path in sorted(root.iterdir()):
        if meta_path.suffix.lower() not in exts:
            continue
        try:
            hasher.update(meta_path.read_bytes())
        except Exception:
            continue
    return hasher.hexdigest()


@functools.lru_cache(maxsize=None)
def _build_cached_template_registry(root: Path, config_hash: str) -> TemplateRegistry:
    env = _build_structured_env(root)
    registry = TemplateRegistry(env, root)
    registry.load_from_configs(root)
    return registry


def default_template_registry(template_root: Path | None = None) -> TemplateRegistry:
    root = template_root or _CONFIG_TEMPLATE_ROOT
    config_hash = _template_config_hash(root)
    return _build_cached_template_registry(root, config_hash)


def default_schema_registry() -> SchemaRegistry:
    registry = SchemaRegistry()
    airway_models = {
        "emn_bronchoscopy_v1": airway_schemas.EMNBronchoscopy,
        "fiducial_marker_placement_v1": airway_schemas.FiducialMarkerPlacement,
        "radial_ebus_survey_v1": airway_schemas.RadialEBUSSurvey,
        "robotic_ion_bronchoscopy_v1": airway_schemas.RoboticIonBronchoscopy,
        "ion_registration_complete_v1": airway_schemas.IonRegistrationComplete,
        "ion_registration_partial_v1": airway_schemas.IonRegistrationPartial,
        "ion_registration_drift_v1": airway_schemas.IonRegistrationDrift,
        "cbct_cact_fusion_v1": airway_schemas.CBCTFusion,
        "tool_in_lesion_confirmation_v1": airway_schemas.ToolInLesionConfirmation,
        "robotic_monarch_bronchoscopy_v1": airway_schemas.RoboticMonarchBronchoscopy,
        "radial_ebus_sampling_v1": airway_schemas.RadialEBUSSampling,
        "cbct_augmented_bronchoscopy_v1": airway_schemas.CBCTAugmentedBronchoscopy,
        "dye_marker_placement_v1": airway_schemas.DyeMarkerPlacement,
        "ebus_tbna_v1": airway_schemas.EBUSTBNA,
        "ebus_ifb_v1": airway_schemas.EBUSIntranodalForcepsBiopsy,
        "ebus_19g_fnb_v1": airway_schemas.EBUS19GFNB,
        "blvr_valve_placement_v1": airway_schemas.BLVRValvePlacement,
        "blvr_valve_removal_exchange_v1": airway_schemas.BLVRValveRemovalExchange,
        "blvr_post_procedure_protocol_v1": airway_schemas.BLVRPostProcedureProtocol,
        "blvr_discharge_instructions_v1": airway_schemas.BLVRDischargeInstructions,
        "transbronchial_cryobiopsy_v1": airway_schemas.TransbronchialCryobiopsy,
        "endobronchial_cryoablation_v1": airway_schemas.EndobronchialCryoablation,
        "cryo_extraction_mucus_v1": airway_schemas.CryoExtractionMucus,
        "bpf_localization_occlusion_v1": airway_schemas.BPFLocalizationOcclusion,
        "bpf_valve_air_leak_v1": airway_schemas.BPFValvePlacement,
        "bpf_endobronchial_sealant_v1": airway_schemas.BPFSealantApplication,
        "endobronchial_hemostasis_v1": airway_schemas.EndobronchialHemostasis,
        "endobronchial_blocker_v1": airway_schemas.EndobronchialBlockerPlacement,
        "pdt_light_v1": airway_schemas.PhotodynamicTherapyLight,
        "pdt_debridement_v1": airway_schemas.PhotodynamicTherapyDebridement,
        "foreign_body_removal_v1": airway_schemas.ForeignBodyRemoval,
        "awake_foi_v1": airway_schemas.AwakeFiberopticIntubation,
        "dlt_placement_v1": airway_schemas.DoubleLumenTubePlacement,
        "stent_surveillance_v1": airway_schemas.AirwayStentSurveillance,
        "whole_lung_lavage_v1": airway_schemas.WholeLungLavage,
        "eusb_v1": airway_schemas.EUSB,
        "bal_v1": airway_schemas.BAL,
        "bal_alt_v1": airway_schemas.BronchoalveolarLavageAlt,
        "bronchial_washing_v1": airway_schemas.BronchialWashing,
        "bronchial_brushings_v1": airway_schemas.BronchialBrushing,
        "endobronchial_biopsy_v1": airway_schemas.EndobronchialBiopsy,
        "transbronchial_lung_biopsy_v1": airway_schemas.TransbronchialLungBiopsy,
        "transbronchial_needle_aspiration_v1": airway_schemas.TransbronchialNeedleAspiration,
        "therapeutic_aspiration_v1": airway_schemas.TherapeuticAspiration,
        "rigid_bronchoscopy_v1": airway_schemas.RigidBronchoscopy,
        "bronchoscopy_shell_v1": airway_schemas.BronchoscopyShell,
    }
    pleural_models = {
        "paracentesis_v1": pleural_schemas.Paracentesis,
        "peg_placement_v1": pleural_schemas.PEGPlacement,
        "peg_exchange_v1": pleural_schemas.PEGExchange,
        "pleurx_instructions_v1": pleural_schemas.PleurxInstructions,
        "chest_tube_discharge_v1": pleural_schemas.ChestTubeDischargeInstructions,
        "peg_discharge_v1": pleural_schemas.PEGDischargeInstructions,
        "thoracentesis_v1": pleural_schemas.Thoracentesis,
        "thoracentesis_detailed_v1": pleural_schemas.ThoracentesisDetailed,
        "thoracentesis_manometry_v1": pleural_schemas.ThoracentesisManometry,
        "chest_tube_v1": pleural_schemas.ChestTube,
        "tunneled_pleural_catheter_insert_v1": pleural_schemas.TunneledPleuralCatheterInsert,
        "tunneled_pleural_catheter_remove_v1": pleural_schemas.TunneledPleuralCatheterRemove,
        "pigtail_catheter_v1": pleural_schemas.PigtailCatheter,
        "transthoracic_needle_biopsy_v1": pleural_schemas.TransthoracicNeedleBiopsy,
    }

    for schema_id, model in airway_models.items():
        registry.register(schema_id, model)
    for schema_id, model in pleural_models.items():
        registry.register(schema_id, model)
    registry.register("pre_anesthesia_assessment_v1", PreAnesthesiaAssessment)
    registry.register("ip_or_main_oper_report_shell_v1", OperativeShellInputs)
    return registry


def _normalize_cpt_candidates(codes: Any) -> list[str | int]:
    return list(codes) if isinstance(codes, list) else []


def _extract_patient(raw: dict[str, Any]) -> PatientInfo:
    return PatientInfo(
        name=raw.get("patient_name"),
        age=raw.get("patient_age"),
        sex=raw.get("gender") or raw.get("sex"),
        patient_id=raw.get("patient_id") or raw.get("patient_identifier"),
        mrn=raw.get("mrn") or raw.get("patient_mrn"),
    )


def _extract_encounter(raw: dict[str, Any]) -> EncounterInfo:
    return EncounterInfo(
        date=raw.get("procedure_date"),
        encounter_id=raw.get("encounter_id") or raw.get("visit_id"),
        location=raw.get("location") or raw.get("procedure_location"),
        referred_physician=raw.get("referred_physician"),
        attending=raw.get("attending_name"),
        assistant=raw.get("fellow_name") or raw.get("assistant_name"),
    )


def _extract_sedation_details(raw: dict[str, Any]) -> tuple[SedationInfo | None, AnesthesiaInfo | None]:
    sedation = SedationInfo(type=raw.get("sedation_type")) if raw.get("sedation_type") else None
    anesthesia_desc = None
    agents = raw.get("anesthesia_agents")
    if agents:
        anesthesia_desc = ", ".join(agents)
    anesthesia = None
    if raw.get("sedation_type") or anesthesia_desc:
        anesthesia = AnesthesiaInfo(
            type=raw.get("sedation_type"),
            description=anesthesia_desc,
        )
    return sedation, anesthesia


def _extract_pre_anesthesia(raw: dict[str, Any]) -> dict[str, Any] | None:
    asa_status = raw.get("asa_class")
    if not asa_status:
        return None
    return {
        "asa_status": f"ASA {asa_status}",
        "anesthesia_plan": raw.get("sedation_type") or "Per anesthesia team",
        "anticoagulant_use": raw.get("anticoagulant_use"),
        "prophylactic_antibiotics": raw.get("prophylactic_antibiotics"),
        "time_out_confirmed": True,
    }


def _coerce_prebuilt_procedures(entries: Any, cpt_candidates: list[str | int]) -> list[ProcedureInput]:
    procedures: list[ProcedureInput] = []
    if not isinstance(entries, list):
        return procedures
    for entry in entries:
        if isinstance(entry, ProcedureInput):
            procedures.append(entry)
            continue
        if not isinstance(entry, dict):
            continue
        proc_type = entry.get("proc_type")
        schema_id = entry.get("schema_id")
        data = entry.get("data", {})
        proc_id = entry.get("proc_id")
        if proc_type and schema_id:
            identifier = proc_id or f"{proc_type}_{len(procedures) + 1}"
            procedures.append(
                ProcedureInput(
                    proc_type=proc_type,
                    schema_id=schema_id,
                    proc_id=identifier,
                    data=data,
                    cpt_candidates=list(cpt_candidates),
                )
            )
    return procedures


def _procedures_from_adapters(
    raw: dict[str, Any],
    cpt_candidates: list[str | int],
    *,
    start_index: int = 0,
) -> list[ProcedureInput]:
    procedures: list[ProcedureInput] = []
    for adapter_cls in AdapterRegistry.all():
        model = adapter_cls.extract(raw)
        if model is None:
            continue
        proc_id = f"{adapter_cls.proc_type}_{start_index + len(procedures) + 1}"
        procedures.append(
            ProcedureInput(
                proc_type=adapter_cls.proc_type,
                schema_id=adapter_cls.get_schema_id(),
                proc_id=proc_id,
                data=model,
                cpt_candidates=list(cpt_candidates),
            )
        )
    return procedures


def build_procedure_bundle_from_extraction(extraction: Any) -> ProcedureBundle:
    """
    Convert a registry extraction payload (dict or RegistryRecord) into a ProcedureBundle.

    This is a light adapter that reads from the RegistryRecord fields without mutating
    the source. It is intentionally permissive so it can accept partially populated
    dicts from tests or upstream extractors.
    """
    raw = extraction.model_dump() if hasattr(extraction, "model_dump") else deepcopy(extraction or {})

    patient = _extract_patient(raw)
    encounter = _extract_encounter(raw)
    sedation, anesthesia = _extract_sedation_details(raw)
    pre_anesthesia = _extract_pre_anesthesia(raw)
    cpt_candidates = _normalize_cpt_candidates(raw.get("cpt_codes") or raw.get("verified_cpt_codes") or [])

    procedures = _coerce_prebuilt_procedures(raw.get("procedures"), cpt_candidates)
    procedures.extend(_procedures_from_adapters(raw, cpt_candidates, start_index=len(procedures)))

    bundle = ProcedureBundle(
        patient=patient,
        encounter=encounter,
        procedures=procedures,
        sedation=sedation,
        anesthesia=anesthesia,
        indication_text=raw.get("primary_indication") or raw.get("indication"),
        preop_diagnosis_text=raw.get("preop_diagnosis_text"),
        postop_diagnosis_text=raw.get("postop_diagnosis_text"),
        impression_plan=raw.get("follow_up_plan", [""])[0] if isinstance(raw.get("follow_up_plan"), list) else raw.get("follow_up_plan"),
        estimated_blood_loss=str(raw.get("ebl_ml")) if raw.get("ebl_ml") is not None else None,
        specimens_text=raw.get("specimens_text"),
        pre_anesthesia=pre_anesthesia,
        free_text_hint=raw.get("source_text") or raw.get("note_text") or raw.get("raw_note"),
    )
    return bundle


def _infer_and_validate_bundle(
    bundle: ProcedureBundle, templates: TemplateRegistry, schemas: SchemaRegistry
) -> tuple[ProcedureBundle, PatchResult, list[MissingFieldIssue], list[str], list[str]]:
    inference_engine = InferenceEngine()
    inference_result = inference_engine.infer_bundle(bundle)
    updated_bundle = apply_patch_result(bundle, inference_result)
    validator = ValidationEngine(templates, schemas)
    issues = validator.list_missing_critical_fields(updated_bundle)
    warnings = validator.apply_warn_if_rules(updated_bundle)
    suggestions = validator.list_suggestions(updated_bundle)
    return updated_bundle, inference_result, issues, warnings, suggestions


def compose_structured_report(
    bundle: ProcedureBundle,
    template_registry: TemplateRegistry | None = None,
    schema_registry: SchemaRegistry | None = None,
    *,
    strict: bool = False,
) -> str:
    templates = template_registry or default_template_registry()
    schemas = schema_registry or default_schema_registry()
    bundle, _, _, _, _ = _infer_and_validate_bundle(bundle, templates, schemas)
    engine = ReporterEngine(
        templates,
        schemas,
        procedure_order=_load_procedure_order(),
    )
    return engine.compose_report(bundle, strict=strict)


def compose_structured_report_from_extraction(
    extraction: Any,
    template_registry: TemplateRegistry | None = None,
    schema_registry: SchemaRegistry | None = None,
    *,
    strict: bool = False,
) -> str:
    bundle = build_procedure_bundle_from_extraction(extraction)
    return compose_structured_report(bundle, template_registry, schema_registry, strict=strict)


def compose_structured_report_with_meta(
    bundle: ProcedureBundle,
    template_registry: TemplateRegistry | None = None,
    schema_registry: SchemaRegistry | None = None,
    *,
    strict: bool = False,
    embed_metadata: bool = False,
) -> StructuredReport:
    templates = template_registry or default_template_registry()
    schemas = schema_registry or default_schema_registry()
    bundle, _, issues, warnings, _ = _infer_and_validate_bundle(bundle, templates, schemas)
    engine = ReporterEngine(
        templates,
        schemas,
        procedure_order=_load_procedure_order(),
    )
    return engine.compose_report_with_metadata(
        bundle,
        strict=strict,
        embed_metadata=embed_metadata,
        validation_issues=issues,
        warnings=warnings,
    )


def compose_structured_report_from_extraction_with_meta(
    extraction: Any,
    template_registry: TemplateRegistry | None = None,
    schema_registry: SchemaRegistry | None = None,
    *,
    strict: bool = False,
    embed_metadata: bool = False,
) -> StructuredReport:
    bundle = build_procedure_bundle_from_extraction(extraction)
    return compose_structured_report_with_meta(
        bundle,
        template_registry=template_registry,
        schema_registry=schema_registry,
        strict=strict,
        embed_metadata=embed_metadata,
    )


def get_missing_critical_fields_from_extraction(extraction: Any) -> list[MissingFieldIssue]:
    bundle = build_procedure_bundle_from_extraction(extraction)
    return list_missing_critical_fields(bundle)


def compose_report_with_patch(extraction: Any, patch: BundlePatch, *, embed_metadata: bool = False) -> StructuredReport:
    bundle = build_procedure_bundle_from_extraction(extraction)
    patched = apply_bundle_patch(bundle, patch)
    return compose_structured_report_with_meta(patched, embed_metadata=embed_metadata)


def get_coder_view(bundle: ProcedureBundle) -> dict[str, Any]:
    structured = compose_structured_report_with_meta(bundle)
    meta = structured.metadata
    return {
        "global": {
            "patient_id": meta.patient_id,
            "mrn": meta.mrn,
            "encounter_id": meta.encounter_id,
            "date_of_procedure": meta.date_of_procedure.isoformat() if meta.date_of_procedure else None,
            "attending": meta.attending,
            "location": meta.location,
        },
        "procedures": [
            {
                "proc_type": proc.proc_type,
                "label": proc.label,
                "cpt_candidates": proc.cpt_candidates,
                "modifiers": proc.modifiers,
                "templates_used": proc.templates_used,
                "section": proc.section,
                "missing": proc.missing_critical_fields,
                "data": proc.extra.get("data"),
            }
            for proc in meta.procedures
        ],
        "autocode": meta.autocode_payload,
    }


__all__ = [
    "compose_report_from_text",
    "compose_report_from_form",
    "compose_structured_report",
    "compose_structured_report_from_extraction",
    "compose_structured_report_with_meta",
    "compose_structured_report_from_extraction_with_meta",
    "compose_report_with_patch",
    "get_missing_critical_fields_from_extraction",
    "ReporterEngine",
    "TemplateRegistry",
    "TemplateMeta",
    "SchemaRegistry",
    "ProcedureBundle",
    "ProcedureInput",
    "BundlePatch",
    "ProcedurePatch",
    "PatientInfo",
    "EncounterInfo",
    "SedationInfo",
    "AnesthesiaInfo",
    "build_procedure_bundle_from_extraction",
    "default_template_registry",
    "default_schema_registry",
    "list_missing_critical_fields",
    "apply_warn_if_rules",
    "apply_bundle_patch",
    "apply_patch_result",
    "get_coder_view",
    "StructuredReport",
    "ReportMetadata",
    "ProcedureMetadata",
    "MissingFieldIssue",
]
