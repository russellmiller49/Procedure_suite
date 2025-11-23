"""Pure report composition functions backed by Jinja templates."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound, select_autoescape
from pydantic import BaseModel, ConfigDict, Field

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
    template_path: Path | None = None


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
            meta = TemplateMeta(
                id=payload["id"],
                label=payload.get("label", payload["id"]),
                category=payload.get("category", ""),
                cpt_hints=[str(item) for item in payload.get("cpt_hints", [])],
                schema_id=payload["schema_id"],
                output_section=payload.get("output_section", "PROCEDURE_DETAILS"),
                required_fields=payload.get("required_fields", []),
                optional_fields=payload.get("optional_fields", []),
                template=template,
                proc_types=payload.get("proc_types", []),
                template_path=meta_path,
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


class PatientInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str | None = None
    age: int | None = None
    sex: str | None = None


class EncounterInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    date: str | None = None
    referred_physician: str | None = None
    attending: str | None = None
    assistant: str | None = None


class SedationInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: str | None = None
    description: str | None = None


class AnesthesiaInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: str | None = None
    description: str | None = None


class EMNBronchoscopy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    navigation_system: str
    target_lung_segment: str
    lesion_size_cm: float | None = None
    tool_to_target_distance_cm: float | None = None
    navigation_catheter: str | None = None
    registration_method: str | None = None
    adjunct_imaging: List[str] | None = None
    notes: str | None = None


class FiducialMarkerPlacement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    airway_location: str
    marker_details: str | None = None
    confirmation_method: str | None = None


class RadialEBUSSurvey(BaseModel):
    model_config = ConfigDict(extra="ignore")
    location: str
    rebus_features: str | None = None
    notes: str | None = None


class RoboticIonBronchoscopy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    navigation_plan_source: str | None = None
    vent_mode: str
    vent_rr: int
    vent_tv_ml: int
    vent_peep_cm_h2o: float
    vent_fio2_pct: int
    vent_flow_rate: str | None = None
    vent_pmean_cm_h2o: float | None = None
    cbct_performed: bool | None = None
    radial_pattern: str | None = None
    notes: str | None = None


class IonRegistrationComplete(BaseModel):
    model_config = ConfigDict(extra="ignore")
    method: str | None = None
    airway_landmarks: List[str] | None = None
    fiducial_error_mm: float | None = None
    alignment_quality: str | None = None
    notes: str | None = None


class IonRegistrationPartial(BaseModel):
    model_config = ConfigDict(extra="ignore")
    indication: str
    scope_of_registration: str | None = None
    registered_landmarks: List[str] | None = None
    registration_start_time: str | None = None
    registration_complete_time: str | None = None
    navigation_start_time: str | None = None
    time_to_primary_nodule_min: float | None = None
    navigation_time_min: float | None = None
    divergence_pct: float | None = None
    rebus_pattern: str | None = None
    tool_in_lesion_confirmation: str | None = None
    rose_adequacy: str | None = None
    diagnostic_yield_pct: float | None = None
    followup_plan: str | None = None


class IonRegistrationDrift(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cause: str | None = None
    findings: str | None = None
    mitigation: str | None = None
    post_correction_alignment: str | None = None
    proceeded_strategy: str | None = None


class CBCTFusion(BaseModel):
    model_config = ConfigDict(extra="ignore")
    ventilation_settings: str | None = None
    translation_mm: str | None = None
    rotation_degrees: str | None = None
    overlay_result: str | None = None
    confirmatory_spin_result: str | None = None
    notes: str | None = None


class ToolInLesionConfirmation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    confirmation_method: str
    margin_mm: float | None = None
    rebus_pattern: str | None = None
    lesion_size_mm: float | None = None
    fluoro_angle_deg: str | None = None
    projection: str | None = None
    screenshots_saved: bool | None = None
    notes: str | None = None


class RoboticMonarchBronchoscopy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    radial_pattern: str | None = None
    cbct_used: bool | None = None
    vent_mode: str | None = None
    vent_rr: int | None = None
    vent_tv_ml: int | None = None
    vent_peep_cm_h2o: float | None = None
    vent_fio2_pct: int | None = None
    vent_flow_rate: str | None = None
    vent_pmean_cm_h2o: float | None = None
    notes: str | None = None


class RadialEBUSSampling(BaseModel):
    model_config = ConfigDict(extra="ignore")
    guide_sheath_diameter: str | None = None
    ultrasound_pattern: str
    lesion_size_mm: float | None = None
    sampling_tools: List[str]
    passes_per_tool: str | None = None
    fluoro_used: bool | None = None
    rose_result: str | None = None
    specimens: List[str] | None = None
    cxr_ordered: bool | None = None
    notes: str | None = None


class CBCTAugmentedBronchoscopy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    ventilation_settings: str | None = None
    adjustment_description: str | None = None
    final_position: str | None = None
    radiation_parameters: str | None = None
    notes: str | None = None


class DyeMarkerPlacement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    guidance_method: str
    needle_gauge: str
    distance_from_pleura_cm: float | None = None
    dye_type: str
    dye_concentration: str | None = None
    volume_ml: float
    diffusion_observed: str | None = None
    notes: str | None = None


class EBUSStationSample(BaseModel):
    model_config = ConfigDict(extra="ignore")
    station_name: str
    size_mm: int | None = None
    passes: int
    echo_features: str | None = None
    biopsy_tools: List[str] = Field(default_factory=list)
    rose_result: str | None = None
    comments: str | None = None


class EBUSTBNA(BaseModel):
    model_config = ConfigDict(extra="ignore")
    needle_gauge: str | None = None
    stations: List[EBUSStationSample]
    elastography_used: bool | None = None
    rose_available: bool | None = None
    overall_rose_diagnosis: str | None = None


class EBUSIntranodalForcepsBiopsy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    station_name: str
    size_mm: int | None = None
    ultrasound_features: str | None = None
    needle_gauge: str
    core_samples: int
    rose_result: str | None = None
    specimen_medium: str | None = None


class EBUS19GFNB(BaseModel):
    model_config = ConfigDict(extra="ignore")
    station_name: str
    passes: int
    rose_result: str | None = None
    elastography_pattern: str | None = None
    findings: str | None = None


class ValvePlacement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    valve_type: str
    valve_size: str | None = None
    lobe: str
    segment: str | None = None


class BLVRValvePlacement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    balloon_occlusion_performed: bool | None = None
    chartis_used: bool | None = None
    collateral_ventilation_absent: bool | None = None
    lobes_treated: List[str]
    valves: List[ValvePlacement]
    air_leak_reduction: str | None = None
    notes: str | None = None


class BLVRValveRemovalExchange(BaseModel):
    model_config = ConfigDict(extra="ignore")
    indication: str
    device_brand: str | None = None
    locations: List[str] = Field(default_factory=list)
    valves_removed: int
    valves_exchanged: int | None = None
    replacement_sizes: str | None = None
    mucosa_status: str | None = None
    tolerance_notes: str | None = None


class BLVRPostProcedureProtocol(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cxr_schedule: List[str] | None = None
    monitoring_plan: str | None = None
    steroids_plan: str | None = None
    antibiotics_plan: str | None = None
    ambulation_plan: str | None = None
    discharge_plan: str | None = None


class BLVRDischargeInstructions(BaseModel):
    model_config = ConfigDict(extra="ignore")
    activity_restrictions: str | None = None
    monitoring_plan: str | None = None
    follow_up_plan: str | None = None
    contact_info: str | None = None


class TransbronchialCryobiopsy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    lung_segment: str
    num_samples: int
    cryoprobe_size_mm: float | None = None
    freeze_seconds: int | None = None
    thaw_seconds: int | None = None
    blocker_type: str | None = None
    blocker_volume_ml: float | None = None
    blocker_location: str | None = None
    tests: List[str] | None = None
    radial_vessel_check: bool | None = None
    notes: str | None = None


class EndobronchialCryoablation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    site: str
    cryoprobe_size_mm: float | None = None
    freeze_seconds: int | None = None
    thaw_seconds: int | None = None
    cycles: int | None = None
    pattern: str | None = None
    post_patency: str | None = None
    notes: str | None = None


class CryoExtractionMucus(BaseModel):
    model_config = ConfigDict(extra="ignore")
    airway_segment: str
    probe_size_mm: float | None = None
    freeze_seconds: int | None = None
    num_casts: int | None = None
    ventilation_result: str | None = None
    notes: str | None = None


class BPFLocalizationOcclusion(BaseModel):
    model_config = ConfigDict(extra="ignore")
    culprit_segment: str
    balloon_type: str | None = None
    balloon_size_mm: int | None = None
    leak_reduction: str | None = None
    methylene_blue_used: bool | None = None
    contrast_used: bool | None = None
    instillation_findings: str | None = None
    notes: str | None = None


class BPFValvePlacement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    etiology: str | None = None
    culprit_location: str
    valve_type: str | None = None
    valve_size: str | None = None
    valves_placed: int | None = None
    leak_reduction: str | None = None
    additional_valves: str | None = None
    post_plan: str | None = None


class BPFSealantApplication(BaseModel):
    model_config = ConfigDict(extra="ignore")
    sealant_type: str
    volume_ml: float | None = None
    dwell_minutes: int | None = None
    leak_reduction: str | None = None
    applications: int | None = None
    notes: str | None = None


class EndobronchialHemostasis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    airway_segment: str
    iced_saline_ml: int | None = None
    epinephrine_concentration: str | None = None
    epinephrine_volume_ml: float | None = None
    tranexamic_acid_dose: str | None = None
    topical_thrombin_dose: str | None = None
    balloon_type: str | None = None
    balloon_location: str | None = None
    balloon_duration_sec: int | None = None
    balloon_cycles: int | None = None
    hemostasis_result: str | None = None
    escalation_plan: str | None = None
    tolerance: str | None = None


class EndobronchialBlockerPlacement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    blocker_type: str
    size: str | None = None
    side: str
    location: str
    inflation_volume_ml: float | None = None
    secured_method: str | None = None
    indication: str | None = None
    tolerance: str | None = None


class PhotodynamicTherapyLight(BaseModel):
    model_config = ConfigDict(extra="ignore")
    agent: str
    administration_time: str | None = None
    lesion_site: str
    wavelength_nm: int | None = None
    fluence_j_cm2: float | None = None
    duration_minutes: int | None = None
    notes: str | None = None


class PhotodynamicTherapyDebridement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    site: str
    debridement_tool: str | None = None
    pre_patency_pct: int | None = None
    post_patency_pct: int | None = None
    bleeding: bool | None = None
    notes: str | None = None


class ForeignBodyRemoval(BaseModel):
    model_config = ConfigDict(extra="ignore")
    airway_segment: str
    tools_used: List[str]
    passes: int | None = None
    removed_intact: bool | None = None
    mucosal_trauma: str | None = None
    bleeding: str | None = None
    hemostasis_method: str | None = None
    cxr_ordered: bool | None = None


class AwakeFiberopticIntubation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    lidocaine_concentration: str | None = None
    lidocaine_volume_ml: int | None = None
    sedative: str | None = None
    ett_size: str
    route: str
    depth_cm: float | None = None
    tolerated: bool | None = None


class DoubleLumenTubePlacement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    side: str
    size_fr: int
    alignment: str | None = None
    adjustments: str | None = None
    tolerated: bool | None = None


class AirwayStentSurveillance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    stent_type: str
    location: str
    findings: List[str] | None = None
    interventions: List[str] | None = None
    final_patency_pct: int | None = None


class WholeLungLavage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    side: str
    dlt_size_fr: int | None = None
    position: str | None = None
    total_volume_l: float | None = None
    max_volume_l: float | None = None
    aliquot_volume_l: float | None = None
    dwell_time_min: int | None = None
    num_cycles: int | None = None
    notes: str | None = None


class EUSB(BaseModel):
    model_config = ConfigDict(extra="ignore")
    stations_sampled: List[str]
    needle_gauge: str | None = None
    passes: int | None = None
    rose_result: str | None = None
    complications: str | None = None


class Paracentesis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    site_description: str | None = None
    volume_removed_ml: int
    fluid_character: str | None = None
    tests: List[str] | None = None
    imaging_guidance: str | None = None


class PEGPlacement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    incision_location: str | None = None
    endoscope_time_seconds: int | None = None
    wire_route: str | None = None
    bumper_depth_cm: float | None = None
    tube_size_fr: int | None = None
    procedural_time_min: int | None = None
    complications: str | None = None


class PEGExchange(BaseModel):
    model_config = ConfigDict(extra="ignore")
    new_tube_size_fr: int | None = None
    bumper_depth_cm: float | None = None
    complications: str | None = None


class PleurxInstructions(BaseModel):
    model_config = ConfigDict(extra="ignore")
    followup_timeframe: str | None = None
    contact_info: str | None = None


class ChestTubeDischargeInstructions(BaseModel):
    model_config = ConfigDict(extra="ignore")
    drainage_plan: str | None = None
    infection_signs: str | None = None
    followup_timeframe: str | None = None


class PEGDischargeInstructions(BaseModel):
    model_config = ConfigDict(extra="ignore")
    feeding_plan: str | None = None
    medication_plan: str | None = None
    wound_care: str | None = None
    contact_info: str | None = None


class BronchialWashing(BaseModel):
    model_config = ConfigDict(extra="ignore")
    airway_segment: str
    instilled_volume_ml: int
    returned_volume_ml: int
    tests: List[str]


class BronchialBrushing(BaseModel):
    model_config = ConfigDict(extra="ignore")
    lung_segment: str
    samples_collected: int
    brush_tool: str | None = None
    tests: List[str]


class BronchoalveolarLavageAlt(BaseModel):
    model_config = ConfigDict(extra="ignore")
    lung_segment: str
    instilled_volume_cc: int
    returned_volume_cc: int
    tests: List[str]


class EndobronchialBiopsy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    airway_segment: str
    samples_collected: int
    tests: List[str]
    hemostasis_method: str | None = None
    lesion_removed: bool | None = None


class TransbronchialLungBiopsy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    lung_segment: str
    samples_collected: int
    forceps_tools: str
    tests: List[str]


class TransbronchialNeedleAspiration(BaseModel):
    model_config = ConfigDict(extra="ignore")
    lung_segment: str
    needle_tools: str
    samples_collected: int
    tests: List[str]


class TherapeuticAspiration(BaseModel):
    model_config = ConfigDict(extra="ignore")
    airway_segment: str
    aspirate_type: str


class RigidBronchoscopy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    size_or_model: str | None = None
    hf_jv: bool | None = None
    interventions: List[str]
    flexible_scope_used: bool | None = None
    estimated_blood_loss_ml: int | None = None
    specimens: List[str] | None = None
    post_procedure_plan: str | None = None


class Thoracentesis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    side: str
    effusion_size: str
    effusion_echogenicity: str
    loculations: str | None = None
    ultrasound_findings: str | None = None
    anesthesia_lidocaine_1_pct_ml: int | None = None
    intercostal_space: str
    entry_location: str
    volume_removed_ml: int
    fluid_appearance: str
    specimen_tests: List[str]
    cxr_ordered: bool | None = None


class ThoracentesisDetailed(BaseModel):
    model_config = ConfigDict(extra="ignore")
    side: str
    ultrasound_feasible: bool | None = None
    anesthesia_lidocaine_ml: int | None = None
    intercostal_space: str
    entry_location: str
    volume_removed_ml: int
    fluid_appearance: str
    drainage_device: str | None = None
    suction_cmh2o: str | None = None
    specimen_tests: List[str] | None = None
    cxr_ordered: bool | None = None
    sutured: bool | None = None
    effusion_volume: str | None = None
    effusion_echogenicity: str | None = None
    loculations: str | None = None
    diaphragm_motion: str | None = None
    lung_sliding_pre: str | None = None
    lung_sliding_post: str | None = None
    lung_consolidation: str | None = None
    pleura_description: str | None = None
    pleural_guidance: str | None = None


class ThoracentesisManometry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    side: str
    guidance: str | None = None
    opening_pressure_cmh2o: float | None = None
    pressure_readings: List[str] | None = None
    stopping_criteria: str | None = None
    total_removed_ml: int
    post_procedure_imaging: str | None = None
    effusion_size: str | None = None
    effusion_echogenicity: str | None = None
    loculations: str | None = None
    diaphragm_motion: str | None = None
    lung_sliding_pre: str | None = None
    lung_sliding_post: str | None = None
    lung_consolidation: str | None = None
    pleura_description: str | None = None


class ChestTube(BaseModel):
    model_config = ConfigDict(extra="ignore")
    side: str
    intercostal_space: str
    entry_line: str
    guidance: str | None = None
    fluid_removed_ml: int | None = None
    fluid_appearance: str | None = None
    specimen_tests: List[str] | None = None
    cxr_ordered: bool | None = None
    effusion_volume: str | None = None
    effusion_echogenicity: str | None = None
    loculations: str | None = None
    diaphragm_motion: str | None = None
    lung_sliding_pre: str | None = None
    lung_sliding_post: str | None = None
    lung_consolidation: str | None = None
    pleura_description: str | None = None


class TunneledPleuralCatheterInsert(BaseModel):
    model_config = ConfigDict(extra="ignore")
    side: str | None = None
    intercostal_space: str
    entry_location: str
    tunnel_length_cm: int | None = None
    exit_site: str | None = None
    anesthesia_lidocaine_ml: int | None = None
    fluid_removed_ml: int | None = None
    fluid_appearance: str | None = None
    pleural_pressures: dict[str, float | int] | None = None
    drainage_device: str | None = None
    suction: str | None = None
    specimen_tests: List[str] | None = None
    cxr_ordered: bool | None = None
    pleural_guidance: str | None = None
    effusion_volume: str | None = None
    effusion_echogenicity: str | None = None
    loculations: str | None = None
    diaphragm_motion: str | None = None
    lung_sliding_pre: str | None = None
    lung_sliding_post: str | None = None
    lung_consolidation: str | None = None
    pleura_description: str | None = None


class TunneledPleuralCatheterRemove(BaseModel):
    model_config = ConfigDict(extra="ignore")
    side: str
    insertion_date: str | None = None
    reason: str | None = None
    site_assessment: str | None = None
    anesthesia_lidocaine_ml: int | None = None
    sutured: bool | None = None
    complications: str | None = None
    antibiotics: str | None = None


class PigtailCatheter(BaseModel):
    model_config = ConfigDict(extra="ignore")
    side: str
    intercostal_space: str
    entry_location: str
    size_fr: str
    anesthesia_lidocaine_ml: int | None = None
    fluid_removed_ml: int | None = None
    fluid_appearance: str | None = None
    specimen_tests: List[str] | None = None
    cxr_ordered: bool | None = None


class TransthoracicNeedleBiopsy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    needle_gauge: str
    samples_collected: int
    imaging_modality: str | None = None
    cxr_ordered: bool | None = None


class BAL(BaseModel):
    model_config = ConfigDict(extra="ignore")
    lung_segment: str
    instilled_volume_cc: int
    returned_volume_cc: int
    tests: List[str]


class PreAnesthesiaAssessment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    anticoagulant_use: str | None = None
    prophylactic_antibiotics: bool | None = None
    asa_status: str
    anesthesia_plan: str
    sedation_history: str | None = None
    time_out_confirmed: bool | None = None


class BronchoscopyShell(BaseModel):
    model_config = ConfigDict(extra="ignore")
    sedation_type: str | None = None
    airway_route: str | None = None
    airway_overview: str | None = None
    right_lung_overview: str | None = None
    left_lung_overview: str | None = None
    mucosa_overview: str | None = None
    secretions_overview: str | None = None
    summary: str | None = None


class OperativeShellInputs(BaseModel):
    model_config = ConfigDict(extra="ignore")
    indication_text: str | None = None
    preop_diagnosis_text: str | None = None
    postop_diagnosis_text: str | None = None
    procedures_summary: str | None = None
    estimated_blood_loss: str | None = None
    complications_text: str | None = None
    specimens_text: str | None = None
    impression_plan: str | None = None


class ProcedureInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    proc_type: str
    schema_id: str
    data: dict[str, Any] | BaseModel
    cpt_candidates: List[str | int] = Field(default_factory=list)


class ProcedureBundle(BaseModel):
    model_config = ConfigDict(extra="ignore")
    patient: PatientInfo
    encounter: EncounterInfo
    procedures: List[ProcedureInput]
    sedation: SedationInfo | None = None
    anesthesia: AnesthesiaInfo | None = None
    pre_anesthesia: PreAnesthesiaAssessment | dict[str, Any] | None = None
    indication_text: str | None = None
    preop_diagnosis_text: str | None = None
    postop_diagnosis_text: str | None = None
    impression_plan: str | None = None
    estimated_blood_loss: str | None = None
    complications_text: str | None = None
    specimens_text: str | None = None
    free_text_hint: str | None = None


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
        sections: dict[str, list[str]] = {
            "HEADER": [],
            "PRE_ANESTHESIA": [],
            "PROCEDURE_DETAILS": [],
            "INSTRUCTIONS": [],
            "DISCHARGE": [],
        }
        procedure_labels: list[str] = []
        bronchoscopy_blocks: list[str] = []
        bronchoscopy_shells: list[tuple[TemplateMeta, ProcedureInput]] = []
        discharge_templates: list[str] = []

        pre_meta = self.templates.get("ip_pre_anesthesia_assessment")
        if pre_meta and bundle.pre_anesthesia:
            rendered = self._render_payload(pre_meta, bundle.pre_anesthesia, bundle)
            if rendered:
                sections["PRE_ANESTHESIA"].append(rendered)

        for proc in self._sorted_procedures(bundle.procedures):
            metas = self.templates.find_for_procedure(proc.proc_type, proc.cpt_candidates)
            if not metas:
                continue
            for meta in metas:
                if meta.id == "ip_general_bronchoscopy_shell":
                    bronchoscopy_shells.append((meta, proc))
                    continue
                # Track discharge/instructions attachments based on procedures
                if meta.id in ("tunneled_pleural_catheter_insert", "ipc_insert"):
                    discharge_templates.append("pleurx_instructions")
                if meta.id == "blvr_valve_placement":
                    discharge_templates.append("blvr_discharge_instructions")
                if meta.id in ("chest_tube", "pigtail_catheter"):
                    discharge_templates.append("chest_tube_discharge")
                if meta.id in ("peg_placement",):
                    discharge_templates.append("peg_discharge")
                rendered = self._render_procedure_template(meta, proc, bundle)
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
                for meta, proc in bronchoscopy_shells:
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
        for discharge_id in _dedupe_labels(discharge_templates):
            discharge_meta = self.templates.get(discharge_id)
            if discharge_meta:
                rendered = self._render_payload(discharge_meta, {}, bundle)
                if rendered:
                    sections.setdefault(discharge_meta.output_section, []).append(rendered)

        shell = self.templates.get(self.shell_template_id) if self.shell_template_id else None
        if shell:
            procedure_details_block = self._join_blocks(
                sections.get("PRE_ANESTHESIA", [])
                + sections.get("PROCEDURE_DETAILS", [])
                + sections.get("INSTRUCTIONS", [])
                + sections.get("DISCHARGE", [])
            )
            shell_payload = OperativeShellInputs(
                indication_text=bundle.indication_text,
                preop_diagnosis_text=bundle.preop_diagnosis_text,
                postop_diagnosis_text=bundle.postop_diagnosis_text,
                procedures_summary=", ".join(_dedupe_labels(procedure_labels)),
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
            return rendered

        note = self._join_sections(sections)
        if strict:
            self._validate_style(note)
        return note

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


def _dedupe_labels(labels: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for label in labels:
        if label in seen:
            continue
        seen.add(label)
        ordered.append(label)
    return ordered


def _load_procedure_order(order_path: Path | None = None) -> dict[str, int]:
    path = order_path or _DEFAULT_ORDER_PATH
    if path.exists():
        try:
            raw = json.loads(path.read_text())
            return {str(k): int(v) for k, v in raw.items()}
        except Exception:
            return {}
    return {}


def default_template_registry(template_root: Path | None = None) -> TemplateRegistry:
    root = template_root or _CONFIG_TEMPLATE_ROOT
    env = _build_structured_env(root)
    registry = TemplateRegistry(env, root)
    registry.load_from_configs(root)
    return registry


def default_schema_registry() -> SchemaRegistry:
    registry = SchemaRegistry()
    registry.register("emn_bronchoscopy_v1", EMNBronchoscopy)
    registry.register("fiducial_marker_placement_v1", FiducialMarkerPlacement)
    registry.register("radial_ebus_survey_v1", RadialEBUSSurvey)
    registry.register("robotic_ion_bronchoscopy_v1", RoboticIonBronchoscopy)
    registry.register("ion_registration_complete_v1", IonRegistrationComplete)
    registry.register("ion_registration_partial_v1", IonRegistrationPartial)
    registry.register("ion_registration_drift_v1", IonRegistrationDrift)
    registry.register("cbct_cact_fusion_v1", CBCTFusion)
    registry.register("tool_in_lesion_confirmation_v1", ToolInLesionConfirmation)
    registry.register("robotic_monarch_bronchoscopy_v1", RoboticMonarchBronchoscopy)
    registry.register("radial_ebus_sampling_v1", RadialEBUSSampling)
    registry.register("cbct_augmented_bronchoscopy_v1", CBCTAugmentedBronchoscopy)
    registry.register("dye_marker_placement_v1", DyeMarkerPlacement)
    registry.register("ebus_tbna_v1", EBUSTBNA)
    registry.register("ebus_ifb_v1", EBUSIntranodalForcepsBiopsy)
    registry.register("ebus_19g_fnb_v1", EBUS19GFNB)
    registry.register("blvr_valve_placement_v1", BLVRValvePlacement)
    registry.register("blvr_valve_removal_exchange_v1", BLVRValveRemovalExchange)
    registry.register("blvr_post_procedure_protocol_v1", BLVRPostProcedureProtocol)
    registry.register("blvr_discharge_instructions_v1", BLVRDischargeInstructions)
    registry.register("transbronchial_cryobiopsy_v1", TransbronchialCryobiopsy)
    registry.register("endobronchial_cryoablation_v1", EndobronchialCryoablation)
    registry.register("cryo_extraction_mucus_v1", CryoExtractionMucus)
    registry.register("bpf_localization_occlusion_v1", BPFLocalizationOcclusion)
    registry.register("bpf_valve_air_leak_v1", BPFValvePlacement)
    registry.register("bpf_endobronchial_sealant_v1", BPFSealantApplication)
    registry.register("endobronchial_hemostasis_v1", EndobronchialHemostasis)
    registry.register("endobronchial_blocker_v1", EndobronchialBlockerPlacement)
    registry.register("pdt_light_v1", PhotodynamicTherapyLight)
    registry.register("pdt_debridement_v1", PhotodynamicTherapyDebridement)
    registry.register("foreign_body_removal_v1", ForeignBodyRemoval)
    registry.register("awake_foi_v1", AwakeFiberopticIntubation)
    registry.register("dlt_placement_v1", DoubleLumenTubePlacement)
    registry.register("stent_surveillance_v1", AirwayStentSurveillance)
    registry.register("whole_lung_lavage_v1", WholeLungLavage)
    registry.register("eusb_v1", EUSB)
    registry.register("paracentesis_v1", Paracentesis)
    registry.register("peg_placement_v1", PEGPlacement)
    registry.register("peg_exchange_v1", PEGExchange)
    registry.register("pleurx_instructions_v1", PleurxInstructions)
    registry.register("chest_tube_discharge_v1", ChestTubeDischargeInstructions)
    registry.register("peg_discharge_v1", PEGDischargeInstructions)
    registry.register("thoracentesis_v1", Thoracentesis)
    registry.register("thoracentesis_detailed_v1", ThoracentesisDetailed)
    registry.register("thoracentesis_manometry_v1", ThoracentesisManometry)
    registry.register("chest_tube_v1", ChestTube)
    registry.register("tunneled_pleural_catheter_insert_v1", TunneledPleuralCatheterInsert)
    registry.register("tunneled_pleural_catheter_remove_v1", TunneledPleuralCatheterRemove)
    registry.register("pigtail_catheter_v1", PigtailCatheter)
    registry.register("transthoracic_needle_biopsy_v1", TransthoracicNeedleBiopsy)
    registry.register("bal_v1", BAL)
    registry.register("bal_alt_v1", BronchoalveolarLavageAlt)
    registry.register("bronchial_washing_v1", BronchialWashing)
    registry.register("bronchial_brushings_v1", BronchialBrushing)
    registry.register("endobronchial_biopsy_v1", EndobronchialBiopsy)
    registry.register("transbronchial_lung_biopsy_v1", TransbronchialLungBiopsy)
    registry.register("transbronchial_needle_aspiration_v1", TransbronchialNeedleAspiration)
    registry.register("therapeutic_aspiration_v1", TherapeuticAspiration)
    registry.register("rigid_bronchoscopy_v1", RigidBronchoscopy)
    registry.register("pre_anesthesia_assessment_v1", PreAnesthesiaAssessment)
    registry.register("bronchoscopy_shell_v1", BronchoscopyShell)
    registry.register("ip_or_main_oper_report_shell_v1", OperativeShellInputs)
    return registry


def build_procedure_bundle_from_extraction(extraction: Any) -> ProcedureBundle:
    """
    Convert a registry extraction payload (dict or RegistryRecord) into a ProcedureBundle.

    This is a light adapter that reads from the RegistryRecord fields without mutating
    the source. It is intentionally permissive so it can accept partially populated
    dicts from tests or upstream extractors.
    """
    raw = extraction.model_dump() if hasattr(extraction, "model_dump") else deepcopy(extraction or {})

    patient = PatientInfo(
        name=raw.get("patient_name"),
        age=raw.get("patient_age"),
        sex=raw.get("gender") or raw.get("sex"),
    )
    encounter = EncounterInfo(
        date=raw.get("procedure_date"),
        referred_physician=raw.get("referred_physician"),
        attending=raw.get("attending_name"),
        assistant=raw.get("fellow_name") or raw.get("assistant_name"),
    )

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

    cpt_codes = raw.get("cpt_codes") or raw.get("verified_cpt_codes") or []
    procedures: list[ProcedureInput] = []

    def _append_proc(proc_type: str, schema_id: str, data: dict | BaseModel) -> None:
        procedures.append(
            ProcedureInput(
                proc_type=proc_type,
                schema_id=schema_id,
                data=data,
                cpt_candidates=list(cpt_codes) if isinstance(cpt_codes, list) else [],
            )
        )

    # Accept pre-built procedures for maximal flexibility.
    prebuilt = raw.get("procedures")
    if isinstance(prebuilt, list):
        for entry in prebuilt:
            if isinstance(entry, ProcedureInput):
                procedures.append(entry)
                continue
            if isinstance(entry, dict):
                proc_type = entry.get("proc_type")
                schema_id = entry.get("schema_id")
                data = entry.get("data", {})
                if proc_type and schema_id:
                    _append_proc(proc_type, schema_id, data)

    # Pre-anesthesia if available
    asa_status = raw.get("asa_class")
    if asa_status:
        pre_anesthesia = {
            "asa_status": f"ASA {asa_status}",
            "anesthesia_plan": raw.get("sedation_type") or "Per anesthesia team",
            "anticoagulant_use": raw.get("anticoagulant_use"),
            "prophylactic_antibiotics": raw.get("prophylactic_antibiotics"),
            "time_out_confirmed": True,
        }
    else:
        pre_anesthesia = None

    # Bronchoscopy shell if airway survey fields exist
    airway_overview = raw.get("airway_overview")
    if airway_overview:
        _append_proc(
            "bronchoscopy_core",
            "bronchoscopy_shell_v1",
            {
                "airway_overview": airway_overview,
                "right_lung_overview": raw.get("right_lung_overview"),
                "left_lung_overview": raw.get("left_lung_overview"),
                "mucosa_overview": raw.get("mucosa_overview"),
                "secretions_overview": raw.get("secretions_overview"),
            },
        )

    # Navigation / robotic
    nav_platform = (raw.get("nav_platform") or "").lower()
    if nav_platform == "emn":
        if raw.get("nav_registration_method") or raw.get("nav_rebus_used"):
            _append_proc(
                "emn_bronchoscopy",
                "emn_bronchoscopy_v1",
                {
                    "navigation_system": raw.get("nav_platform", "EMN"),
                    "target_lung_segment": raw.get("nav_target_segment", "target lesion"),
                    "registration_method": raw.get("nav_registration_method"),
                    "adjunct_imaging": [img for img in [raw.get("nav_imaging_verification")] if img],
                    # TODO: extractor missing lesion_size_cm, tool_to_target_distance_cm
                },
            )
    if nav_platform == "ion":
        if raw.get("ventilation_mode"):
            _append_proc(
                "robotic_ion_bronchoscopy",
                "robotic_ion_bronchoscopy_v1",
                {
                    "navigation_plan_source": "pre-procedure CT" if raw.get("nav_registration_method") else None,
                    "vent_mode": raw.get("ventilation_mode"),
                    "vent_rr": raw.get("vent_rr") or 14,
                    "vent_tv_ml": raw.get("vent_tv_ml") or 450,
                    "vent_peep_cm_h2o": raw.get("vent_peep_cm_h2o") or 8,
                    "vent_fio2_pct": raw.get("vent_fio2_pct") or 40,
                    "vent_flow_rate": raw.get("vent_flow_rate"),
                    "vent_pmean_cm_h2o": raw.get("vent_pmean_cm_h2o"),
                    "cbct_performed": raw.get("nav_imaging_verification") == "Cone Beam CT",
                    "radial_pattern": raw.get("nav_rebus_view"),
                },
            )
        if raw.get("nav_registration_method"):
            _append_proc(
                "ion_registration_complete",
                "ion_registration_complete_v1",
                {
                    "method": raw.get("nav_registration_method"),
                    "fiducial_error_mm": raw.get("nav_registration_error_mm"),
                    "alignment_quality": raw.get("nav_registration_alignment"),
                    # TODO: extractor missing airway_landmarks
                },
            )
        if raw.get("nav_imaging_verification") in ("Cone Beam CT", "O-Arm"):
            _append_proc(
                "cbct_cact_fusion",
                "cbct_cact_fusion_v1",
                {
                    "overlay_result": raw.get("nav_imaging_verification"),
                    # TODO: extractor missing translation_mm, rotation_degrees
                },
            )
    if nav_platform in ("monarch", "auris"):
        _append_proc(
            "robotic_monarch_bronchoscopy",
            "robotic_monarch_bronchoscopy_v1",
            {
                "radial_pattern": raw.get("nav_rebus_view"),
                "cbct_used": raw.get("nav_imaging_verification") in ("Cone Beam CT", "O-Arm"),
                # TODO: extractor missing ventilation parameters
            },
        )
    if raw.get("nav_rebus_used"):
        # Survey level
        _append_proc(
            "radial_ebus_survey",
            "radial_ebus_survey_v1",
            {
                "location": raw.get("nav_target_segment", "target lesion"),
                "rebus_features": raw.get("nav_rebus_view"),
            },
        )
    if raw.get("nav_sampling_tools"):
        _append_proc(
            "radial_ebus_sampling",
            "radial_ebus_sampling_v1",
            {
                "ultrasound_pattern": raw.get("nav_rebus_view") or "concentric",
                "sampling_tools": raw.get("nav_sampling_tools") or [],
                "lesion_size_mm": raw.get("nav_lesion_size_mm"),
                # TODO: extractor missing passes_per_tool, specimens
            },
        )
    if raw.get("nav_tool_in_lesion"):
        _append_proc(
            "tool_in_lesion_confirmation",
            "tool_in_lesion_confirmation_v1",
            {
                "confirmation_method": raw.get("nav_imaging_verification") or "imaging confirmation",
                # TODO: extractor missing margin_mm, fluoro_angle_deg, projection
            },
        )

    # EBUS
    ebus_stations = raw.get("ebus_stations_sampled") or []
    if ebus_stations:
        station_entries = []
        for station in ebus_stations:
            station_entries.append(
                {
                    "station_name": station,
                    "passes": raw.get("ebus_passes", 1),  # TODO: extractor missing per-station pass counts
                    "echo_features": raw.get("ebus_echo_features"),
                    "biopsy_tools": ["TBNA"],
                    "rose_result": raw.get("ebus_rose_result"),
                }
            )
        _append_proc(
            "ebus_tbna",
            "ebus_tbna_v1",
            {
                "needle_gauge": raw.get("ebus_needle_gauge"),
                "stations": station_entries,
                "elastography_used": raw.get("ebus_elastography"),
                "rose_available": raw.get("ebus_rose_available"),
                "overall_rose_diagnosis": raw.get("ebus_rose_result"),
            },
        )

    # Pleural procedures derived from registry fields
    # Bronchoscopy/airway procedures (if provided as dict payloads)
    simple_map = [
        ("bronchial_washing", "bronchial_washing_v1", "bronchial_washing"),
        ("bronchial_brushings", "bronchial_brushings_v1", "bronchial_brushings"),
        ("bal", "bal_v1", "bal"),
        ("bal_variant", "bal_alt_v1", "bal_variant"),
        ("endobronchial_biopsy", "endobronchial_biopsy_v1", "endobronchial_biopsy"),
        ("transbronchial_lung_biopsy", "transbronchial_lung_biopsy_v1", "transbronchial_lung_biopsy"),
        ("transbronchial_needle_aspiration", "transbronchial_needle_aspiration_v1", "transbronchial_needle_aspiration"),
        ("therapeutic_aspiration", "therapeutic_aspiration_v1", "therapeutic_aspiration"),
        ("rigid_bronchoscopy", "rigid_bronchoscopy_v1", "rigid_bronchoscopy"),
        ("transbronchial_cryobiopsy", "transbronchial_cryobiopsy_v1", "transbronchial_cryobiopsy"),
        ("endobronchial_cryoablation", "endobronchial_cryoablation_v1", "endobronchial_cryoablation"),
        ("cryo_extraction_mucus", "cryo_extraction_mucus_v1", "cryo_extraction_mucus"),
        ("endobronchial_hemostasis", "endobronchial_hemostasis_v1", "endobronchial_hemostasis"),
        ("endobronchial_blocker", "endobronchial_blocker_v1", "endobronchial_blocker"),
        ("pdt_light", "pdt_light_v1", "pdt_light"),
        ("pdt_debridement", "pdt_debridement_v1", "pdt_debridement"),
        ("foreign_body_removal", "foreign_body_removal_v1", "foreign_body_removal"),
        ("awake_foi", "awake_foi_v1", "awake_foi"),
        ("dlt_placement", "dlt_placement_v1", "dlt_placement"),
        ("stent_surveillance", "stent_surveillance_v1", "stent_surveillance"),
    ]
    for key, schema_id, proc_type in simple_map:
        if isinstance(raw.get(key), (dict, BaseModel)):
            _append_proc(proc_type, schema_id, raw[key])

    # Pleural procedures derived from registry fields
    pleural_type = (raw.get("pleural_procedure_type") or "").lower()
    pleural_side = raw.get("pleural_side") or raw.get("laterality") or raw.get("side")

    if pleural_type == "thoracentesis":
        uses_manometry = bool(raw.get("pleural_opening_pressure_measured")) or raw.get("pleural_opening_pressure_cmh2o") is not None
        schema_id = "thoracentesis_manometry_v1" if uses_manometry else "thoracentesis_detailed_v1"
        proc_type = "thoracentesis_manometry" if uses_manometry else "thoracentesis_detailed"
        thoracentesis_payload = {
            "side": pleural_side or "unspecified",
            "guidance": raw.get("pleural_guidance"),
            "intercostal_space": raw.get("intercostal_space", "unspecified"),
            "entry_location": raw.get("entry_location", "mid-axillary"),
            "volume_removed_ml": raw.get("pleural_volume_drained_ml"),
            "fluid_appearance": raw.get("pleural_fluid_appearance"),
            "specimen_tests": raw.get("specimen_tests") or raw.get("specimens"),
            "effusion_volume": raw.get("pleural_effusion_volume"),
            "effusion_echogenicity": raw.get("pleural_echogenicity"),
            "loculations": raw.get("pleural_loculations"),
            "diaphragm_motion": raw.get("pleural_diaphragm_motion"),
            "lung_sliding_pre": raw.get("pleural_lung_sliding_pre"),
            "lung_sliding_post": raw.get("pleural_lung_sliding_post"),
            "lung_consolidation": raw.get("pleural_lung_consolidation"),
            "pleura_description": raw.get("pleural_description"),
            "opening_pressure_cmh2o": raw.get("pleural_opening_pressure_cmh2o"),
            "pressure_readings": raw.get("pleural_pressure_readings"),
            "stopping_criteria": raw.get("pleural_stopping_criteria"),
            "post_procedure_imaging": raw.get("post_procedure_imaging"),
            "total_removed_ml": raw.get("pleural_volume_drained_ml"),
            "pleural_guidance": raw.get("pleural_guidance"),
        }
        _append_proc(proc_type, schema_id, thoracentesis_payload)
    elif pleural_type == "chest tube":
        chest_payload = {
            "side": pleural_side or "unspecified",
            "intercostal_space": raw.get("intercostal_space", "unspecified"),
            "entry_line": raw.get("entry_location", "mid-axillary"),
            "guidance": raw.get("pleural_guidance"),
            "fluid_removed_ml": raw.get("pleural_volume_drained_ml"),
            "fluid_appearance": raw.get("pleural_fluid_appearance"),
            "specimen_tests": raw.get("specimen_tests") or raw.get("specimens"),
            "cxr_ordered": raw.get("cxr_ordered"),
            "effusion_volume": raw.get("pleural_effusion_volume"),
            "effusion_echogenicity": raw.get("pleural_echogenicity"),
            "loculations": raw.get("pleural_loculations"),
            "diaphragm_motion": raw.get("pleural_diaphragm_motion"),
            "lung_sliding_pre": raw.get("pleural_lung_sliding_pre"),
            "lung_sliding_post": raw.get("pleural_lung_sliding_post"),
            "lung_consolidation": raw.get("pleural_lung_consolidation"),
            "pleura_description": raw.get("pleural_description"),
        }
        _append_proc("chest_tube", "chest_tube_v1", chest_payload)
    elif pleural_type == "tunneled catheter":
        tpc_payload = {
            "side": pleural_side,
            "intercostal_space": raw.get("intercostal_space", "unspecified"),
            "entry_location": raw.get("entry_location", "mid-axillary"),
            "tunnel_length_cm": raw.get("tunnel_length_cm"),
            "exit_site": raw.get("exit_site"),
            "anesthesia_lidocaine_ml": raw.get("anesthesia_lidocaine_ml"),
            "fluid_removed_ml": raw.get("pleural_volume_drained_ml"),
            "fluid_appearance": raw.get("pleural_fluid_appearance"),
            "pleural_pressures": raw.get("pleural_pressures"),
            "drainage_device": raw.get("drainage_device"),
            "suction": raw.get("suction"),
            "specimen_tests": raw.get("specimen_tests") or raw.get("specimens"),
            "cxr_ordered": raw.get("cxr_ordered"),
            "pleural_guidance": raw.get("pleural_guidance"),
        }
        _append_proc("tunneled_pleural_catheter_insert", "tunneled_pleural_catheter_insert_v1", tpc_payload)
    elif pleural_type == "pigtail catheter":
        pigtail_payload = {
            "side": pleural_side or "unspecified",
            "intercostal_space": raw.get("intercostal_space", "unspecified"),
            "entry_location": raw.get("entry_location", "mid-axillary"),
            "size_fr": raw.get("size_fr", "unspecified"),
            "anesthesia_lidocaine_ml": raw.get("anesthesia_lidocaine_ml"),
            "fluid_removed_ml": raw.get("pleural_volume_drained_ml"),
            "fluid_appearance": raw.get("pleural_fluid_appearance"),
            "specimen_tests": raw.get("specimen_tests") or raw.get("specimens"),
            "cxr_ordered": raw.get("cxr_ordered"),
        }
        _append_proc("pigtail_catheter", "pigtail_catheter_v1", pigtail_payload)

    # Whole lung lavage
    if raw.get("wll_volume_instilled_l") is not None:
        _append_proc(
            "whole_lung_lavage",
            "whole_lung_lavage_v1",
            {
                "side": raw.get("wll_side", "right"),
                "dlt_size_fr": raw.get("wll_dlt_used_size"),
                "position": raw.get("wll_position"),
                "total_volume_l": raw.get("wll_volume_instilled_l"),
                "max_volume_l": raw.get("wll_volume_instilled_l"),
                "aliquot_volume_l": raw.get("wll_aliquot_volume_l"),
                "dwell_time_min": raw.get("wll_dwell_time_min"),
                "num_cycles": raw.get("wll_num_cycles"),
            },
        )

    # BLVR if available from registry
    if raw.get("blvr_valve_type") or raw.get("blvr_number_of_valves"):
        target_lobe = raw.get("blvr_target_lobe") or "target lobe"
        valves: list[dict[str, Any]] = []
        valve_count = raw.get("blvr_number_of_valves") or 1
        for _ in range(max(1, int(valve_count))):
            valves.append({"valve_type": raw.get("blvr_valve_type") or "Valve", "lobe": target_lobe})
        _append_proc(
            "blvr_valve_placement",
            "blvr_valve_placement_v1",
            {
                "lobes_treated": [target_lobe],
                "valves": valves,
                # TODO: extractor missing balloon_occlusion_performed, chartis_used, collateral_ventilation_absent
            },
        )

    # BPF localization/valve/sealant if explicitly provided
    if isinstance(raw.get("bpf_localization"), (dict, BaseModel)):
        _append_proc("bpf_localization_occlusion", "bpf_localization_occlusion_v1", raw["bpf_localization"])
    if isinstance(raw.get("bpf_valve_placement"), (dict, BaseModel)):
        _append_proc("bpf_valve_air_leak", "bpf_valve_air_leak_v1", raw["bpf_valve_placement"])
    if isinstance(raw.get("bpf_sealant_application"), (dict, BaseModel)):
        _append_proc("bpf_endobronchial_sealant", "bpf_endobronchial_sealant_v1", raw["bpf_sealant_application"])

    # Other large procedures
    if raw.get("paracentesis_performed"):
        _append_proc(
            "paracentesis",
            "paracentesis_v1",
            {
                "volume_removed_ml": raw.get("paracentesis_volume_ml") or 0,
                "site_description": raw.get("paracentesis_site"),
                "fluid_character": raw.get("paracentesis_fluid_character"),
                "tests": raw.get("paracentesis_tests"),
                "imaging_guidance": raw.get("paracentesis_guidance"),
            },
        )
    if raw.get("peg_placed"):
        _append_proc(
            "peg_placement",
            "peg_placement_v1",
            {
                "incision_location": raw.get("peg_incision_location"),
                "tube_size_fr": raw.get("peg_size_fr"),
                "bumper_depth_cm": raw.get("peg_bumper_depth_cm"),
                "procedural_time_min": raw.get("peg_time_minutes"),
                "complications": raw.get("peg_complications"),
            },
        )
    if raw.get("peg_exchanged"):
        _append_proc(
            "peg_exchange",
            "peg_exchange_v1",
            {
                "new_tube_size_fr": raw.get("peg_size_fr"),
                "bumper_depth_cm": raw.get("peg_bumper_depth_cm"),
                "complications": raw.get("peg_complications"),
            },
        )

    # Direct payloads for removal or exchange actions
    if isinstance(raw.get("tunneled_pleural_catheter_remove"), (dict, BaseModel)):
        _append_proc("tunneled_pleural_catheter_remove", "tunneled_pleural_catheter_remove_v1", raw["tunneled_pleural_catheter_remove"])
    if isinstance(raw.get("transthoracic_needle_biopsy"), (dict, BaseModel)):
        _append_proc("transthoracic_needle_biopsy", "transthoracic_needle_biopsy_v1", raw["transthoracic_needle_biopsy"])

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
    )
    return bundle


def compose_structured_report(
    bundle: ProcedureBundle,
    template_registry: TemplateRegistry | None = None,
    schema_registry: SchemaRegistry | None = None,
    *,
    strict: bool = False,
) -> str:
    templates = template_registry or default_template_registry()
    schemas = schema_registry or default_schema_registry()
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


__all__ = [
    "compose_report_from_text",
    "compose_report_from_form",
    "compose_structured_report",
    "ReporterEngine",
    "TemplateRegistry",
    "TemplateMeta",
    "SchemaRegistry",
    "ProcedureBundle",
    "ProcedureInput",
    "PatientInfo",
    "EncounterInfo",
    "SedationInfo",
    "AnesthesiaInfo",
    "build_procedure_bundle_from_extraction",
]
