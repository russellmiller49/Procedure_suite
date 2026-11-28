"""Structured seed inputs: enumerated selections that augment a seed prompt.

The Reporter Builder sends these next to the free-text prompt. They are applied
to the bundle *after* extraction, so they never alter how the text is parsed
(appending them to the text would disable short-prompt handling).

Rules:

* Every field is optional. ``None`` means "not specified" and writes nothing;
  an undocumented item is never defaulted to false, zero or "none".
* A specified value is authoritative: it overrides the extracted value and the
  override is reported in ``applied``.
* Values are enumerated only (no free text), so this channel cannot carry PHI.
* Nodal inputs never create an EBUS-TBNA procedure. Sampling must come from the
  dictation; otherwise the selection is recorded as a finding with a warning.

v2 candidates (not implemented): ventilation parameter table, per-site CT size
and PET avidity, distance to target, lesion ROSE, free-text plan items (these
would have to pass the PHI gate).
"""

from __future__ import annotations

import typing
from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.reporting.normalization.source_sequence import (
    EARLY_TYPES,
    FIDUCIAL_TYPES,
    LOCALIZATION_TYPES,
    NAVIGATION_TYPES,
    SAMPLING_TYPES,
    STAGING_TYPES,
)
from app.reporting.questions import QuestionInputType
from proc_schemas.clinical import ProcedureBundle, ProcedureInput
from proc_schemas.clinical.common import AnesthesiaInfo

SEED_INPUTS_VERSION = "reporter_seed_inputs.v1"

ElastographyPattern = Literal["Type 1", "Type 2", "Type 3"]
EBUSStation = Literal["2R", "2L", "4R", "4L", "5", "7", "10R", "10L", "11Rs", "11Ri", "11R", "11L"]
NeedleGauge = Literal["19G", "21G", "22G", "25G"]

_TECHNIQUE_SENTENCES = {
    "All stations assessed; nodes 5 mm or larger sampled": (
        "All lymph node stations were assessed. Only those 5 mm or greater in short axis "
        "were sampled."
    ),
    "Targeted nodal sampling": "Targeted nodal sampling was performed.",
}
_ANESTHESIA_TYPES = {
    "General anesthesia via endotracheal tube": "General anesthesia",
    "General anesthesia via laryngeal mask airway": "General anesthesia",
    "Deep sedation / TIVA": "Deep sedation",
    "Moderate sedation": "Moderate sedation",
}
_AIRWAY_EXAM_NORMAL = (
    "Initial airway inspection: the tracheobronchial tree was examined to at least the "
    "first subsegmental level and was normal."
)


class _Inputs(BaseModel):
    # Typos in the UI or a fixture must fail loudly, not vanish.
    model_config = ConfigDict(extra="forbid")


class EBUSElastographyInputs(_Inputs):
    used: bool | None = None
    scope: Literal["All sampled/inspected nodes", "Specific nodes"] | None = None
    uniform_pattern: ElastographyPattern | None = None
    stations_type_1: list[EBUSStation] = Field(default_factory=list)
    stations_type_2: list[EBUSStation] = Field(default_factory=list)
    stations_type_3: list[EBUSStation] = Field(default_factory=list)

    @model_validator(mode="after")
    def _consistent(self) -> EBUSElastographyInputs:
        stations = self.stations_type_1 + self.stations_type_2 + self.stations_type_3
        if len(set(stations)) != len(stations):
            raise ValueError("A station can have only one elastography type.")
        detail = bool(self.scope or self.uniform_pattern or stations)
        if self.used is not True and detail:
            raise ValueError("Elastography details require 'used' to be yes.")
        if self.scope == "Specific nodes" and self.uniform_pattern:
            raise ValueError("Use the per-type station lists when scope is specific nodes.")
        if self.scope == "All sampled/inspected nodes" and stations:
            raise ValueError("Station lists apply only when scope is specific nodes.")
        return self

    def per_station(self) -> dict[str, str]:
        return {
            station.upper(): pattern
            for pattern, stations in (
                ("Type 1", self.stations_type_1),
                ("Type 2", self.stations_type_2),
                ("Type 3", self.stations_type_3),
            )
            for station in stations
        }


class EBUSInputs(_Inputs):
    needle_gauges: list[NeedleGauge] = Field(default_factory=list)
    technique: (
        Literal["All stations assessed; nodes 5 mm or larger sampled", "Targeted nodal sampling"]
        | None
    ) = None
    rose_available: bool | None = None
    overall_rose: (
        Literal[
            "Adequate lymphocytes, no malignancy",
            "Malignant",
            "Atypical cells",
            "Granulomas",
            "Nondiagnostic",
        ]
        | None
    ) = None
    elastography: EBUSElastographyInputs | None = None


class FiducialInputs(_Inputs):
    placed: bool | None = None
    marker_type: Literal["Gold fiducial", "Coil fiducial"] | None = None
    count: int | None = Field(default=None, ge=1, le=10)
    confirmation: Literal["fluoroscopy", "cone-beam CT"] | None = None

    @model_validator(mode="after")
    def _consistent(self) -> FiducialInputs:
        if self.placed is not True and (self.marker_type or self.count or self.confirmation):
            raise ValueError("Fiducial details require 'placed' to be yes.")
        return self


class NavigationInputs(_Inputs):
    platform: Literal["Ion", "Monarch", "Galaxy"] | None = None
    registration: Literal["Full", "Partial"] | None = None
    rebus_view: Literal["Concentric", "Eccentric", "Adjacent", "Not identifiable"] | None = None
    cbct_used: bool | None = None
    tool_in_lesion_confirmed: bool | None = None
    cbct_attestation: bool | None = None
    fiducial: FiducialInputs | None = None

    @model_validator(mode="after")
    def _consistent(self) -> NavigationInputs:
        if self.cbct_used is False and self.cbct_attestation:
            raise ValueError("The CT interpretation attestation requires cone-beam CT.")
        return self


class AirwayInputs(_Inputs):
    anesthesia: (
        Literal[
            "General anesthesia via endotracheal tube",
            "General anesthesia via laryngeal mask airway",
            "Deep sedation / TIVA",
            "Moderate sedation",
        ]
        | None
    ) = None
    airway_exam_normal: bool | None = None
    therapeutic_aspiration: bool | None = None


class ClosingInputs(_Inputs):
    ebl: Literal["Minimal", "< 5 mL", "5-10 mL", "10-50 mL", "> 50 mL"] | None = None
    complications_none: bool | None = None
    disposition: (
        Literal[
            "Extubated in the operating room and transported to the recovery room in stable condition",
            "Laryngeal mask airway removed and transported to the recovery room in stable condition",
            "Transported to the recovery room in stable condition",
            "Remained intubated and transported to the ICU",
        ]
        | None
    ) = None
    plan_items: list[
        Literal[
            "CXR in PACU",
            "Follow up pathology/cytology results",
            "IP clinic follow-up in 1-2 weeks",
            "Discharge home when recovery criteria are met",
        ]
    ] = Field(default_factory=list)


class ReporterSeedInputs(_Inputs):
    version: Literal["reporter_seed_inputs.v1"] = SEED_INPUTS_VERSION
    sequence: (
        Literal["Peripheral target first, then EBUS", "EBUS first, then peripheral target"] | None
    ) = None
    ebus: EBUSInputs | None = None
    navigation: NavigationInputs | None = None
    airway: AirwayInputs | None = None
    closing: ClosingInputs | None = None

    def is_empty(self) -> bool:
        return not self.model_dump(exclude_none=True, exclude_defaults=True)


@dataclass
class SeedInputApplyResult:
    bundle: ProcedureBundle
    applied: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- apply


def _payload(proc: ProcedureInput) -> dict[str, Any]:
    if isinstance(proc.data, BaseModel):
        return proc.data.model_dump()
    return dict(proc.data) if isinstance(proc.data, dict) else {}


def _new(kind: str, data: dict[str, Any]) -> ProcedureInput:
    return ProcedureInput(
        proc_type=kind, schema_id=kind + "_v1", proc_id=f"{kind}_seed_input", data=data
    )


def _phase(kind: str) -> float:
    if kind in EARLY_TYPES:
        return -1
    if kind in NAVIGATION_TYPES:
        return 0
    if kind in LOCALIZATION_TYPES:
        return 1
    if kind in SAMPLING_TYPES:
        return 2
    if kind in FIDUCIAL_TYPES:
        return 2.5
    if kind in STAGING_TYPES:
        return 3
    return 4


class _Applier:
    def __init__(self, bundle: ProcedureBundle) -> None:
        self.bundle = bundle.model_copy(deep=True)
        self.applied: list[str] = []
        self.warnings: list[str] = []

    # -- helpers
    def procs(self, *kinds: str) -> list[ProcedureInput]:
        return [p for p in self.bundle.procedures if p.proc_type in kinds]

    def warn(self, message: str) -> None:
        self.warnings.append("SEED_INPUT: " + message)

    def set_field(self, proc: ProcedureInput, key: str, value: Any, label: str) -> None:
        data = _payload(proc)
        previous = data.get(key)
        if previous == value:
            proc.data = data
            return
        data[key] = value
        proc.data = data
        note = f"{label}: {value}"
        if previous not in (None, "", [], {}):
            note += f" (replaced '{previous}')"
        self.applied.append(note)

    def remove(self, kinds: tuple[str, ...], label: str) -> None:
        if self.procs(*kinds):
            self.bundle.procedures = [p for p in self.bundle.procedures if p.proc_type not in kinds]
            self.applied.append(f"{label}: removed")
            self.warn(f"{label} was extracted from the text but set to 'no'; it was removed.")

    def add(self, proc: ProcedureInput, label: str) -> ProcedureInput:
        self.bundle.procedures.append(proc)
        self.applied.append(f"{label}: added")
        return proc

    def add_finding(self, sentence: str, *, first: bool = False) -> None:
        lines = [line for line in (self.bundle.findings_text or "").split("\n") if line.strip()]
        if sentence in lines:
            return
        lines = [sentence, *lines] if first else [*lines, sentence]
        self.bundle.findings_text = "\n".join(lines)

    def peripheral_location(self) -> str | None:
        for proc in self.bundle.procedures:
            if proc.proc_type not in NAVIGATION_TYPES | LOCALIZATION_TYPES | SAMPLING_TYPES:
                continue
            data = _payload(proc)
            for key in ("lesion_location", "location", "lung_segment"):
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return None

    # -- groups
    def ebus(self, inputs: EBUSInputs) -> None:
        sampled = self.procs("ebus_tbna")
        surveyed = self.procs("ebus_survey")
        target = (sampled or surveyed or [None])[0]
        if inputs.needle_gauges:
            if sampled:
                self.set_field(
                    sampled[0], "needle_gauge", ", ".join(inputs.needle_gauges), "EBUS needle"
                )
            else:
                self.warn("EBUS needle gauge ignored: no EBUS-TBNA sampling in the dictation.")
        if inputs.technique:
            if target is not None:
                self.set_field(
                    target,
                    "survey_technique",
                    _TECHNIQUE_SENTENCES[inputs.technique],
                    "EBUS technique",
                )
            else:
                self.warn("EBUS technique ignored: no linear EBUS in the dictation.")
        if inputs.rose_available is not None or inputs.overall_rose:
            if not sampled:
                self.warn("Nodal ROSE ignored: no EBUS-TBNA sampling in the dictation.")
            else:
                if inputs.rose_available is not None:
                    self.set_field(
                        sampled[0], "rose_available", inputs.rose_available, "Nodal ROSE"
                    )
                overall = inputs.overall_rose or (
                    "Not performed" if inputs.rose_available is False else None
                )
                if overall:
                    self.set_field(
                        sampled[0], "overall_rose_diagnosis", overall, "Overall nodal ROSE"
                    )
        if inputs.elastography and inputs.elastography.used is not None:
            self.elastography(inputs.elastography, target)

    def elastography(self, inputs: EBUSElastographyInputs, target: ProcedureInput | None) -> None:
        per_station = inputs.per_station()
        if target is None:
            if inputs.used:
                detail = ", ".join(f"{name} {pattern}" for name, pattern in per_station.items())
                if inputs.uniform_pattern:
                    detail = f"all assessed nodes {inputs.uniform_pattern}"
                self.add_finding(
                    "EBUS elastography was performed" + (f": {detail}." if detail else ".")
                )
                self.applied.append("Elastography: recorded in findings")
                self.warn(
                    "No linear EBUS block in the dictation; elastography is documented in "
                    "findings only."
                )
            return
        data = _payload(target)
        stations = [dict(st) for st in data.get("stations") or []]
        if inputs.used is False:
            cleared = bool(data.get("elastography_pattern")) or any(
                st.get("elastography_pattern") for st in stations
            )
            for st in stations:
                st.pop("elastography_pattern", None)
            data.update(elastography_used=False, elastography_pattern=None, stations=stations)
            target.data = data
            self.applied.append("Elastography: not used")
            if cleared:
                self.warn("Elastography types from the text were removed (set to 'not used').")
            return
        data["elastography_used"] = True
        self.applied.append("Elastography: used")
        if inputs.uniform_pattern:
            data["elastography_pattern"] = inputs.uniform_pattern
            for st in stations:
                st["elastography_pattern"] = inputs.uniform_pattern
            self.applied.append(f"Elastography: all nodes {inputs.uniform_pattern}")
        elif per_station:
            names = {str(st.get("station_name", "")).upper(): st for st in stations}
            missing = []
            for name, pattern in per_station.items():
                if name in names:
                    names[name]["elastography_pattern"] = pattern
                    self.applied.append(f"Elastography: station {name} {pattern}")
                else:
                    missing.append(f"{name} {pattern}")
            patterns = {st.get("elastography_pattern") for st in stations}
            data["elastography_pattern"] = (
                patterns.pop() if len(patterns) == 1 and None not in patterns else None
            )
            if missing:
                # Never add a station the dictation did not name as sampled/inspected.
                self.add_finding(
                    "EBUS elastography of nodes not otherwise documented: "
                    + ", ".join(missing)
                    + "."
                )
                self.warn(
                    "Elastography was given for station(s) not in the dictated list ("
                    + ", ".join(missing)
                    + "); recorded in findings."
                )
        data["stations"] = stations
        target.data = data

    def navigation(self, inputs: NavigationInputs) -> None:
        location = self.peripheral_location()
        nav = self.procs("robotic_navigation")
        if inputs.platform or inputs.registration:
            if not nav and location:
                nav = [
                    self.add(
                        _new("robotic_navigation", {"lesion_location": location}),
                        "Robotic navigation",
                    )
                ]
            if not nav:
                self.warn(
                    "Navigation platform/registration ignored: no peripheral target in the dictation."
                )
            for proc in nav:
                if inputs.platform:
                    self.set_field(proc, "platform", inputs.platform, "Platform")
                if inputs.registration:
                    self.set_field(proc, "registration_method", inputs.registration, "Registration")
        if inputs.rebus_view:
            surveys = self.procs("radial_ebus_survey")
            view = (
                "not identifiable" if inputs.rebus_view == "Not identifiable" else inputs.rebus_view
            )
            if not surveys and location:
                surveys = [
                    self.add(_new("radial_ebus_survey", {"location": location}), "Radial EBUS")
                ]
            if not surveys:
                self.warn("Radial EBUS view ignored: no peripheral target in the dictation.")
            elif len(surveys) == 1:
                self.set_field(surveys[0], "rebus_features", view, "Radial EBUS view")
            else:
                # One selection cannot overwrite different views dictated per target.
                for proc in surveys:
                    if not _payload(proc).get("rebus_features"):
                        self.set_field(proc, "rebus_features", view, "Radial EBUS view")
        if inputs.cbct_used is False:
            self.remove(("cbct_cact_fusion", "cbct_augmented_bronchoscopy"), "Cone-beam CT")
        elif inputs.cbct_used or inputs.cbct_attestation:
            cbct = self.procs("cbct_cact_fusion")
            if not cbct:
                cbct = [self.add(_new("cbct_cact_fusion", {}), "Cone-beam CT")]
            if inputs.cbct_attestation:
                self.set_field(
                    cbct[0], "physician_interpreted", True, "CT interpretation attestation"
                )
        if inputs.tool_in_lesion_confirmed is False:
            self.remove(("tool_in_lesion_confirmation",), "Tool-in-lesion confirmation")
        elif inputs.tool_in_lesion_confirmed and not self.procs("tool_in_lesion_confirmation"):
            method = "cone-beam CT" if self.procs("cbct_cact_fusion") else "imaging"
            self.add(
                _new("tool_in_lesion_confirmation", {"confirmation_method": method}),
                "Tool-in-lesion confirmation",
            )
        if inputs.fiducial and inputs.fiducial.placed is not None:
            self.fiducial(inputs.fiducial, location)

    def fiducial(self, inputs: FiducialInputs, location: str | None) -> None:
        if inputs.placed is False:
            self.remove(("fiducial_marker_placement",), "Fiducial marker")
            return
        markers = self.procs("fiducial_marker_placement")
        if not markers:
            if not location:
                self.warn("Fiducial marker ignored: no peripheral target in the dictation.")
                return
            markers = [
                self.add(
                    _new("fiducial_marker_placement", {"airway_location": location}),
                    "Fiducial marker",
                )
            ]
        details = inputs.marker_type
        if inputs.count:
            details = f"{details or 'fiducial'} x{inputs.count}"
        if details:
            self.set_field(markers[0], "marker_details", details, "Fiducial details")
        if inputs.confirmation:
            self.set_field(
                markers[0], "confirmation_method", inputs.confirmation, "Fiducial confirmation"
            )

    def airway(self, inputs: AirwayInputs) -> None:
        if inputs.anesthesia:
            self.bundle.anesthesia = AnesthesiaInfo(
                type=_ANESTHESIA_TYPES[inputs.anesthesia], description=inputs.anesthesia
            )
            if inputs.anesthesia.startswith("General"):
                self.bundle.sedation = None
            self.applied.append(f"Anesthesia: {inputs.anesthesia}")
        if inputs.airway_exam_normal:
            self.add_finding(_AIRWAY_EXAM_NORMAL, first=True)
            self.applied.append("Airway exam: normal")
        elif inputs.airway_exam_normal is False:
            self.warn("Airway exam marked abnormal; describe the findings in the dictation.")
        if inputs.therapeutic_aspiration is False:
            self.remove(("therapeutic_aspiration",), "Therapeutic aspiration")
        elif inputs.therapeutic_aspiration and not self.procs("therapeutic_aspiration"):
            self.add(
                _new(
                    "therapeutic_aspiration",
                    {"airway_segment": "airways", "aspirate_type": "secretions"},
                ),
                "Therapeutic aspiration",
            )

    def closing(self, inputs: ClosingInputs) -> None:
        if inputs.ebl:
            self.bundle.estimated_blood_loss = inputs.ebl
            self.applied.append(f"EBL: {inputs.ebl}")
        if inputs.complications_none:
            self.bundle.complications_text = "None"
            self.applied.append("Complications: none")
        elif inputs.complications_none is False:
            self.warn("Complications indicated; dictate the details (none were written).")
        if inputs.disposition:
            sentence = (
                "At the conclusion of the operation, the patient was "
                + inputs.disposition[0].lower()
                + inputs.disposition[1:]
                + "."
            )
            if inputs.complications_none:
                sentence = (
                    "The patient tolerated the procedure well. There were no immediate "
                    "complications. " + sentence
                )
            self.bundle.closing_text = sentence
            self.applied.append("Disposition set")
        if inputs.plan_items:
            existing = [
                block.strip()
                for block in (self.bundle.impression_plan or "").split("\n\n")
                if block.strip()
            ]
            lowered = " ".join(existing).lower()
            for item in inputs.plan_items:
                if item.lower() not in lowered:
                    existing.append("- " + item)
                    self.applied.append(f"Plan: {item}")
            self.bundle.impression_plan = "\n\n".join(existing)

    def sequence(self, choice: str) -> None:
        procs = self.bundle.procedures
        ebus_first = choice.startswith("EBUS first")

        def key(item: tuple[int, ProcedureInput]) -> tuple:
            index, proc = item
            staging = proc.proc_type in STAGING_TYPES
            early = proc.proc_type in EARLY_TYPES
            block = 0 if early else (1 if staging == ebus_first else 2)
            return (
                block,
                proc.sequence if proc.sequence is not None else 10_000,
                _phase(proc.proc_type),
                index,
            )

        ordered = sorted(enumerate(procs), key=key)
        if len(ordered) < 2:
            return
        ranks = {index: rank for rank, (index, _) in enumerate(ordered, 1)}
        self.bundle.procedures = [
            proc.model_copy(update={"sequence": ranks[index]}) for index, proc in enumerate(procs)
        ]
        self.applied.append(f"Sequence: {choice}")


def apply_seed_inputs(
    bundle: ProcedureBundle,
    inputs: ReporterSeedInputs | None,
) -> SeedInputApplyResult:
    """Apply structured selections to a seeded bundle. Pure and idempotent."""
    if inputs is None or inputs.is_empty():
        return SeedInputApplyResult(bundle=bundle)
    applier = _Applier(bundle)
    if inputs.airway:
        applier.airway(inputs.airway)
    if inputs.navigation:
        applier.navigation(inputs.navigation)
    if inputs.ebus:
        applier.ebus(inputs.ebus)
    if inputs.closing:
        applier.closing(inputs.closing)
    if inputs.sequence:
        applier.sequence(inputs.sequence)
    return SeedInputApplyResult(
        bundle=ProcedureBundle.model_validate(applier.bundle.model_dump(exclude_none=False)),
        applied=applier.applied,
        warnings=list(dict.fromkeys(applier.warnings)),
    )


# ---------------------------------------------------------------------------- spec


class SeedInputDependency(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pointer: str
    equals: Any


class SeedInputFieldSpec(BaseModel):
    """One dropdown. Same shape as a reporter question, plus ``depends_on``."""

    model_config = ConfigDict(extra="forbid")
    id: str
    pointer: str
    label: str
    input_type: QuestionInputType
    options: list[str | int] = Field(default_factory=list)
    help: str | None = None
    group: str
    depends_on: list[SeedInputDependency] = Field(default_factory=list)


class SeedInputSpecResponse(BaseModel):
    version: str
    groups: list[str]
    fields: list[SeedInputFieldSpec]


_USED = [("/ebus/elastography/used", True)]
_SPECIFIC = [*_USED, ("/ebus/elastography/scope", "Specific nodes")]
_FIDUCIAL = [("/navigation/fiducial/placed", True)]

# (pointer, label, group, help, depends_on)
_FIELDS: tuple[tuple[str, str, str, str | None, list[tuple[str, Any]]], ...] = (
    ("/sequence", "Order of procedures", "Workflow", "Controls which part is described first.", []),
    ("/airway/anesthesia", "Anesthesia / airway", "Airway", None, []),
    (
        "/airway/airway_exam_normal",
        "Airway exam normal",
        "Airway",
        "Yes adds a normal airway inspection sentence.",
        [],
    ),
    ("/airway/therapeutic_aspiration", "Therapeutic aspiration of secretions", "Airway", None, []),
    ("/navigation/platform", "Robotic platform", "Navigation", None, []),
    ("/navigation/registration", "Registration", "Navigation", None, []),
    ("/navigation/rebus_view", "Radial EBUS view", "Navigation", None, []),
    ("/navigation/cbct_used", "Cone-beam CT used", "Navigation", None, []),
    ("/navigation/tool_in_lesion_confirmed", "Tool-in-lesion confirmed", "Navigation", None, []),
    (
        "/navigation/cbct_attestation",
        "CT guidance personally performed and interpreted",
        "Navigation",
        "Yes adds the radiologic supervision and interpretation attestation.",
        [],
    ),
    ("/navigation/fiducial/placed", "Fiducial marker placed", "Fiducial", None, []),
    ("/navigation/fiducial/marker_type", "Marker type", "Fiducial", None, _FIDUCIAL),
    ("/navigation/fiducial/count", "Number of markers", "Fiducial", None, _FIDUCIAL),
    ("/navigation/fiducial/confirmation", "Placement guidance", "Fiducial", None, _FIDUCIAL),
    ("/ebus/needle_gauges", "EBUS needle gauge(s)", "EBUS", None, []),
    ("/ebus/technique", "Nodal sampling approach", "EBUS", None, []),
    ("/ebus/rose_available", "Nodal ROSE performed", "EBUS", None, []),
    ("/ebus/overall_rose", "Overall nodal ROSE", "EBUS", None, [("/ebus/rose_available", True)]),
    ("/ebus/elastography/used", "Elastography used", "EBUS elastography", None, []),
    ("/ebus/elastography/scope", "Elastography applied to", "EBUS elastography", None, _USED),
    (
        "/ebus/elastography/uniform_pattern",
        "Elastography type (all nodes)",
        "EBUS elastography",
        "Type 1 soft, Type 2 mixed, Type 3 stiff.",
        [*_USED, ("/ebus/elastography/scope", "All sampled/inspected nodes")],
    ),
    ("/ebus/elastography/stations_type_1", "Type 1 nodes", "EBUS elastography", None, _SPECIFIC),
    ("/ebus/elastography/stations_type_2", "Type 2 nodes", "EBUS elastography", None, _SPECIFIC),
    ("/ebus/elastography/stations_type_3", "Type 3 nodes", "EBUS elastography", None, _SPECIFIC),
    ("/closing/ebl", "Estimated blood loss", "Closing", None, []),
    (
        "/closing/complications_none",
        "No complications",
        "Closing",
        "Yes writes COMPLICATIONS: None.",
        [],
    ),
    ("/closing/disposition", "Disposition", "Closing", None, []),
    ("/closing/plan_items", "Plan items", "Closing", None, []),
)


def _annotation(pointer: str) -> Any:
    model: Any = ReporterSeedInputs
    annotation: Any = None
    for part in pointer.strip("/").split("/"):
        annotation = model.model_fields[part].annotation
        nested = [
            arg
            for arg in typing.get_args(annotation)
            if isinstance(arg, type) and issubclass(arg, BaseModel)
        ]
        if nested:
            model = nested[0]
    return annotation


def _input_type(annotation: Any) -> tuple[QuestionInputType, list[str | int]]:
    args = [arg for arg in typing.get_args(annotation) if arg is not type(None)]
    origin = typing.get_origin(annotation)
    if origin is list:
        return QuestionInputType.MULTISELECT, list(typing.get_args(args[0]))
    inner = args[0] if args else annotation
    if inner is bool:
        return QuestionInputType.BOOLEAN, []
    if inner is int:
        return QuestionInputType.INTEGER, []
    if typing.get_origin(inner) is Literal:
        return QuestionInputType.ENUM, list(typing.get_args(inner))
    raise TypeError(f"Unsupported seed input annotation: {annotation!r}")


def build_seed_input_spec() -> SeedInputSpecResponse:
    """Dropdown catalog derived from the request model, so they cannot drift."""
    fields = []
    for pointer, label, group, help_text, depends_on in _FIELDS:
        input_type, options = _input_type(_annotation(pointer))
        fields.append(
            SeedInputFieldSpec(
                id=pointer.strip("/").replace("/", "."),
                pointer=pointer,
                label=label,
                input_type=input_type,
                options=options,
                help=help_text,
                group=group,
                depends_on=[SeedInputDependency(pointer=p, equals=v) for p, v in depends_on],
            )
        )
    return SeedInputSpecResponse(
        version=SEED_INPUTS_VERSION,
        groups=list(dict.fromkeys(spec.group for spec in fields)),
        fields=fields,
    )


__all__ = [
    "ReporterSeedInputs",
    "SeedInputApplyResult",
    "SeedInputFieldSpec",
    "SeedInputSpecResponse",
    "apply_seed_inputs",
    "build_seed_input_spec",
]
