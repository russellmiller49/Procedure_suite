"""Assign ``ProcedureInput.sequence`` from the order of the source dictation.

Reporter-only. Runs while seeding, after the fidelity reconcilers. It never
changes procedure data, registry fields, or coding; it only records where each
procedure was mentioned so the report can follow the dictated workflow instead
of a fixed type ranking.

Two source layouts are recognized, mirroring the fidelity modules:

* short peripheral/EBUS prompts (``is_short_peripheral_prompt``)
* the institutional operative narrative ("Robotic navigation bronchoscopy was
  performed with ...", "EBUS-Findings")

Any other note keeps ``sequence=None`` and therefore the legacy ordering.

Dictation order is a proxy for chronology, so three clinical constraints are
enforced per target: navigation precedes everything, localization (radial
EBUS / cone-beam CT / tool-in-lesion) precedes tissue sampling, and a fiducial
marker follows tissue sampling.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from pydantic import BaseModel

from app.reporting.normalization.robotic_ebus_fidelity import _END, _NAV_START
from app.reporting.normalization.robotic_prompt_fidelity import (
    _MODALITIES,
    _targets,
    is_short_peripheral_prompt,
    normalize_prompt,
    split_peripheral_nodal,
)
from proc_schemas.clinical import ProcedureBundle, ProcedureInput

NAVIGATION_TYPES = frozenset(
    {
        "emn_bronchoscopy",
        "robotic_navigation",
        "robotic_ion_bronchoscopy",
        "robotic_monarch_bronchoscopy",
        "ion_registration_complete",
        "ion_registration_partial",
        "ion_registration_drift",
    }
)
LOCALIZATION_TYPES = frozenset(
    {
        "radial_ebus_survey",
        "radial_ebus_sampling",
        "cbct_cact_fusion",
        "cbct_augmented_bronchoscopy",
        "tool_in_lesion_confirmation",
    }
)
SAMPLING_TYPES = frozenset(
    {
        "transbronchial_biopsy",
        "transbronchial_lung_biopsy",
        "transbronchial_needle_aspiration",
        "transbronchial_cryobiopsy",
        "bronchial_brushings",
        "bronchial_washing",
        "bal",
        "bal_variant",
        "endobronchial_biopsy",
        "peripheral_ablation",
    }
)
TISSUE_TYPES = frozenset(
    {
        "transbronchial_biopsy",
        "transbronchial_lung_biopsy",
        "transbronchial_needle_aspiration",
        "transbronchial_cryobiopsy",
    }
)
FIDUCIAL_TYPES = frozenset({"fiducial_marker_placement", "dye_marker_placement"})
STAGING_TYPES = frozenset({"ebus_tbna", "ebus_survey", "ebus_ifb", "ebus_19g_fnb", "eusb"})
EARLY_TYPES = frozenset({"bronchoscopy_core", "therapeutic_aspiration"})

# Institutional sampling order, used only to break ties and to place a
# target-bound sample that has no keyword of its own inside its target clause.
_SAMPLING_RANK = {
    "transbronchial_needle_aspiration": 1,
    "transbronchial_biopsy": 2,
    "transbronchial_lung_biopsy": 2,
    "transbronchial_cryobiopsy": 3,
    "bronchial_brushings": 4,
    "bronchial_washing": 5,
    "bal": 5,
    "bal_variant": 5,
    "endobronchial_biopsy": 6,
    "peripheral_ablation": 7,
}

_NAV = r"\b(?:Ion|Monarch|Galaxy|robot\w*|navigat\w*)\b"
_RADIAL = r"\b(?:radial|r-?EBUS)\b"
_CBCT = r"\b(?:CBCT|cone[- ]?beam|Cios|spins?|spun|3-plane)\b"
_TIL = r"\b(?:tool[- ]in[- ]lesion|TIL|needle in (?:the )?lesion)\b"
_LAVAGE = r"(?:\b|(?<=mini))(?:BAL(?=\b|\d)|lavag\w*|wash(?:ed|es)?\b)"
_FIDUCIAL = r"\bfiducial\b|\b(?:gold )?marker\b"


def _modality(kind: str) -> str:
    return r"\b(?:" + _MODALITIES[kind] + r")(?=\b|\d)"


_PROMPT_ANCHORS: dict[str, str] = {
    **{kind: _NAV for kind in NAVIGATION_TYPES},
    "radial_ebus_survey": _RADIAL,
    "radial_ebus_sampling": _RADIAL,
    "cbct_cact_fusion": _CBCT,
    "cbct_augmented_bronchoscopy": _CBCT,
    "tool_in_lesion_confirmation": _TIL,
    "transbronchial_needle_aspiration": _modality("transbronchial_needle_aspiration"),
    "transbronchial_cryobiopsy": _modality("transbronchial_cryobiopsy"),
    "transbronchial_lung_biopsy": _modality("transbronchial_lung_biopsy"),
    "transbronchial_biopsy": _modality("transbronchial_lung_biopsy"),
    "bronchial_brushings": _modality("bronchial_brushings"),
    "bal": _LAVAGE,
    "bal_variant": _LAVAGE,
    "bronchial_washing": _LAVAGE,
    "fiducial_marker_placement": _FIDUCIAL,
    "therapeutic_aspiration": (
        r"\btherapeutic aspiration\b|\bsuction\w*|\bairway clearance\b|"
        r"\bclear(?:ed|ing)\b[^.;]{0,30}\b(?:airways?|secretions|mucus)"
    ),
    "endobronchial_blocker": r"\b(?:blocker|balloon)\b",
}

_NARRATIVE_ANCHORS: dict[str, str] = {
    **{kind: r"^[ \t]*Robotic navigation bronchoscopy was performed" for kind in NAVIGATION_TYPES},
    "radial_ebus_survey": r"^[ \t]*Radial EBUS was performed",
    "radial_ebus_sampling": r"^[ \t]*Radial EBUS was performed",
    "cbct_cact_fusion": r"^[ \t]*Cone Beam CT was performed",
    "cbct_augmented_bronchoscopy": r"^[ \t]*Cone Beam CT was performed",
    "tool_in_lesion_confirmation": r"tool[- ]in[- ]lesion",
    "transbronchial_needle_aspiration": r"^[ \t]*Transbronchial needle aspiration was performed",
    "transbronchial_cryobiopsy": r"^[ \t]*Transbronchial cryobiopsy was performed",
    "transbronchial_lung_biopsy": r"^[ \t]*Transbronchial biopsy was performed",
    "transbronchial_biopsy": r"^[ \t]*Transbronchial biopsy was performed",
    "bronchial_brushings": r"^[ \t]*Transbronchial brushing was performed",
    "bal": r"^[ \t]*Bronchial alveolar lavage was performed",
    "bal_variant": r"^[ \t]*Bronchial alveolar lavage was performed",
    "fiducial_marker_placement": r"^[ \t]*Fiducial marker\b",
    "therapeutic_aspiration": r"\btherapeutic aspiration\b",
    "endobronchial_blocker": r"\b(?:blocker|balloon)\b",
}

_LOCATION_KEYS = (
    "lung_segment",
    "location",
    "lesion_location",
    "airway_location",
    "segment",
    "lobe",
)


@dataclass(frozen=True)
class _Layout:
    text: str
    anchors: dict[str, str]
    slices: list[tuple[str, int, int]]  # (target label, start, end)
    ebus_pos: int | None
    narrative: bool


def source_sequence_enabled() -> bool:
    return os.getenv("REPORTER_SOURCE_SEQUENCE", "1").strip().lower() in {"1", "true", "yes", "y"}


def _data(proc: ProcedureInput) -> dict:
    if isinstance(proc.data, BaseModel):
        return proc.data.model_dump(exclude_none=True)
    return proc.data if isinstance(proc.data, dict) else {}


def _location(proc: ProcedureInput) -> str:
    data = _data(proc)
    for key in _LOCATION_KEYS:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _prompt_layout(source: str) -> _Layout | None:
    text = normalize_prompt(source)
    text = re.sub(r"(?i)(\d+)\s+(\d{2}G)\s+passes", r"\1 \2 needle passes", text)
    peripheral, nodal = split_peripheral_nodal(text)
    targets = _targets(peripheral)
    if not targets:
        return None
    slices: list[tuple[str, int, int]] = []
    cursor = 0
    for label, local in targets:
        start = peripheral.find(local, cursor) if local else -1
        if start < 0:
            start = cursor
        slices.append((label, start, start + len(local)))
        cursor = start
    if len(slices) == 1:
        slices = [(slices[0][0], 0, len(peripheral))]
    return _Layout(
        text=text,
        anchors=_PROMPT_ANCHORS,
        slices=slices,
        ebus_pos=len(peripheral) if nodal else None,
        narrative=False,
    )


def _narrative_layout(source: str) -> _Layout | None:
    starts = list(_NAV_START.finditer(source))
    ebus = re.search(r"(?im)^[ \t]*EBUS[- ]Findings\b", source)
    if not starts and ebus is None:
        return None
    slices: list[tuple[str, int, int]] = []
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(source)
        stop = _END.search(source, start.end(), end)
        if stop:
            end = stop.start()
        label = re.search(
            r"(?i)catheter was used to engage the\s+([^\n.]+)", source[start.start() : end]
        )
        slices.append((re.sub(r"\s+", " ", label[1]).strip() if label else "", start.start(), end))
    return _Layout(
        text=source,
        anchors=_NARRATIVE_ANCHORS,
        slices=slices,
        ebus_pos=ebus.start() if ebus else None,
        narrative=True,
    )


def _layout(source: str) -> _Layout | None:
    if is_short_peripheral_prompt(source):
        return _prompt_layout(source)
    return _narrative_layout(source)


def _bound_slice(proc: ProcedureInput, layout: _Layout) -> int | None:
    if not layout.slices:
        return None
    if layout.narrative:
        block = re.search(r"_source_(\d+)$", proc.proc_id or "")
        if block and 0 < int(block[1]) <= len(layout.slices):
            return int(block[1]) - 1
    location = _location(proc).lower()
    if not location:
        return None
    for index, (label, _, _) in enumerate(layout.slices):
        if label and label.lower() == location:
            return index
    return None


def _matches(pattern: str, text: str, start: int, end: int) -> list[int]:
    return [start + m.start() for m in re.finditer(pattern, text[start:end], re.I | re.M)]


def assign_source_sequence(bundle: ProcedureBundle, source_text: str | None) -> ProcedureBundle:
    """Return a bundle whose procedures carry dictation-order ``sequence`` values.

    Bundles that already carry any sequence (prebuilt/LLM bundles) are returned
    unchanged, as are notes in an unrecognized layout.
    """
    procs = list(bundle.procedures or [])
    if not source_sequence_enabled() or not source_text or len(procs) < 2:
        return bundle
    if any(proc.sequence is not None for proc in procs):
        return bundle
    layout = _layout(source_text)
    if layout is None:
        return bundle

    text = layout.text
    positions: dict[int, float] = {}
    bound: dict[int, int | None] = {}
    used: dict[tuple[str, int | None], int] = {}

    for index, proc in enumerate(procs):
        kind = proc.proc_type
        slice_index = _bound_slice(proc, layout)
        bound[index] = slice_index
        if kind in STAGING_TYPES:
            if layout.ebus_pos is not None:
                positions[index] = float(layout.ebus_pos)
            continue
        pattern = layout.anchors.get(kind)
        if not pattern:
            continue
        start, end = layout.slices[slice_index][1:] if slice_index is not None else (0, len(text))
        hits = _matches(pattern, text, start, end)
        if hits and slice_index is None:
            # An unbound sample (e.g. a separate lobe's lavage) belongs to the
            # mention that names its own location, when one does.
            token = re.split(r"[\s(/]", _location(proc), maxsplit=1)[0]
            if token:
                near = [
                    hit
                    for hit in hits
                    if re.search(
                        r"(?i)\b" + re.escape(token) + r"\b",
                        # A narrative sentence names its site after the verb.
                        text[max(0, hit - 25) : hit + (80 if layout.narrative else 25)],
                    )
                ]
                hits = near or hits
        if hits:
            key = (kind, slice_index)
            nth = used.get(key, 0)
            used[key] = nth + 1
            positions[index] = float(hits[min(nth, len(hits) - 1)])
        elif slice_index is not None:
            # Target-bound step without its own keyword in the target clause
            # (shared "both"/"each" counts): place it by phase inside the clause.
            if kind in NAVIGATION_TYPES:
                positions[index] = start - 0.5
            elif kind in LOCALIZATION_TYPES:
                positions[index] = start + 0.2
            elif kind in SAMPLING_TYPES:
                positions[index] = end - 1 + _SAMPLING_RANK.get(kind, 9) * 0.01
            elif kind in FIDUCIAL_TYPES:
                positions[index] = end - 0.3
        elif kind in EARLY_TYPES:
            positions[index] = -1.0

    def _members(slice_index: int | None, kinds: frozenset[str]) -> list[int]:
        return [
            i
            for i, proc in enumerate(procs)
            if i in positions and proc.proc_type in kinds and bound[i] == slice_index
        ]

    all_sampling = [i for i in positions if procs[i].proc_type in SAMPLING_TYPES]
    slice_ids: list[int | None] = [*range(len(layout.slices)), None]
    for slice_index in slice_ids:
        sampling = _members(slice_index, SAMPLING_TYPES)
        # Unbound localization (one cone-beam CT entry for the case) is held
        # ahead of the first tissue sample overall.
        reference = sampling or (all_sampling if slice_index is None else [])
        if reference:
            first_sample = min(positions[i] for i in reference)
            late = sorted(
                (
                    i
                    for i in _members(slice_index, LOCALIZATION_TYPES)
                    if positions[i] > first_sample
                ),
                key=lambda i: positions[i],
            )
            for offset, i in enumerate(late):
                positions[i] = first_sample - 0.5 + offset * 0.01
        if slice_index is not None:
            members = [i for i in positions if bound[i] == slice_index]
            for i in _members(slice_index, NAVIGATION_TYPES):
                others = [positions[j] for j in members if j != i]
                if others:
                    positions[i] = min(positions[i], min(others) - 0.5)

    # Case-level localization cannot precede navigation to the first target.
    nav_positions = [positions[i] for i in positions if procs[i].proc_type in NAVIGATION_TYPES]
    if nav_positions:
        first_nav = min(nav_positions)
        for i in _members(None, LOCALIZATION_TYPES):
            if positions[i] < first_nav:
                positions[i] = first_nav + 0.3

    # A marker is deployed after tissue (needle/forceps/cryo) sampling of its
    # target. Its order relative to brushing and lavage varies between cases,
    # so those keep the dictated order.
    all_tissue = [i for i in all_sampling if procs[i].proc_type in TISSUE_TYPES]
    for index, proc in enumerate(procs):
        if proc.proc_type not in FIDUCIAL_TYPES:
            continue
        sampling = _members(bound[index], TISSUE_TYPES) if bound[index] is not None else []
        sampling = sampling or [i for i in all_tissue if positions[i] < (layout.ebus_pos or 1e12)]
        if sampling:
            last_sample = max(positions[i] for i in sampling)
            positions[index] = max(positions.get(index, last_sample), last_sample + 0.5)

    # Tool-in-lesion is a cone-beam/radial confirmation; keep it with the last
    # spin of its own target (or of the case when it is not target-bound).
    cbct_kinds = {"cbct_cact_fusion", "cbct_augmented_bronchoscopy"}
    for index, proc in enumerate(procs):
        if proc.proc_type != "tool_in_lesion_confirmation":
            continue
        spins = [
            i
            for i in positions
            if procs[i].proc_type in cbct_kinds
            and (bound[index] is None or bound[i] in (None, bound[index]))
        ]
        if spins:
            positions[index] = max(positions[i] for i in spins) + 0.25

    if len(positions) < 2:
        return bundle

    order = sorted(
        positions,
        key=lambda i: (positions[i], _SAMPLING_RANK.get(procs[i].proc_type, 0), i),
    )
    updated = list(procs)
    for rank, index in enumerate(order, 1):
        updated[index] = procs[index].model_copy(update={"sequence": rank})
    return bundle.model_copy(update={"procedures": updated})


__all__ = [
    "EARLY_TYPES",
    "FIDUCIAL_TYPES",
    "LOCALIZATION_TYPES",
    "NAVIGATION_TYPES",
    "SAMPLING_TYPES",
    "STAGING_TYPES",
    "assign_source_sequence",
    "source_sequence_enabled",
]
