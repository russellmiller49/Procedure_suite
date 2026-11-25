"""Sample plausible robotic bronchoscopy / linear EBUS cases as statement units.

A unit is one statable fact: the contract fields it sets and the sentence group
it renders in. Groups render as one sentence from whichever of their units are
stated, so omitting a unit drops both its words and its gold values.

Traps (TRAPS) are deliberate failure modes seen in real extraction: surveyed
stations that were not sampled, failed navigation, tool-in-lesion claimed from
radial EBUS alone, explicit negated complications, per-pass sampling detail,
planned-only EBUS, historical procedures, and sizes in centimetres.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

LOBES: dict[str, tuple[str, list[tuple[str, str]]]] = {
    "RUL": ("right upper lobe", [("apical", "RB1"), ("posterior", "RB2"), ("anterior", "RB3")]),
    "RML": ("right middle lobe", [("lateral", "RB4"), ("medial", "RB5")]),
    "RLL": (
        "right lower lobe",
        [
            ("superior", "RB6"),
            ("anterior basal", "RB8"),
            ("lateral basal", "RB9"),
            ("posterior basal", "RB10"),
        ],
    ),
    "LUL": ("left upper lobe", [("apicoposterior", "LB1+2"), ("anterior", "LB3")]),
    "Lingula": ("lingula", [("superior lingular", "LB4"), ("inferior lingular", "LB5")]),
    "LLL": (
        "left lower lobe",
        [("superior", "LB6"), ("lateral basal", "LB9"), ("posterior basal", "LB10")],
    ),
}
SIDE = {
    "RUL": "right",
    "RML": "right",
    "RLL": "right",
    "LUL": "left",
    "Lingula": "left",
    "LLL": "left",
}
ATTENUATION = {
    "solid": "solid",
    "part_solid": "part-solid",
    "ground_glass": "ground-glass",
    "cavitary": "cavitary",
}
PLATFORMS = ("Ion", "Monarch", "Galaxy")
STATIONS = ("2R", "2L", "4R", "4L", "7", "10R", "10L", "11R", "11L", "11Rs", "11Ri")
VOLUMETRIC = {
    "mobile_CBCT": ("mobile cone-beam CT", "volumetric_imaging"),
    "fixed_CBCT": ("fixed cone-beam CT", "volumetric_imaging"),
    "CBCT_unspecified": ("cone-beam CT", "volumetric_imaging"),
    "digital_tomosynthesis": ("digital tomosynthesis", "tomosynthesis"),
}
ROSE_LUNG = (
    ("malignant cells consistent with non-small cell carcinoma", True),
    ("atypical cells", True),
    ("benign bronchial cells and macrophages", True),
    ("scant cellularity, nondiagnostic", False),
)
ROSE_NODE = (
    ("lymphocytes, adequate for evaluation", True),
    ("malignant cells", True),
    ("non-necrotizing granulomas", True),
    ("blood only, inadequate", False),
)
NOT_SAMPLED_REASONS = (
    "it measured under 5 mm with benign sonographic features",
    "an intervening vessel prevented a safe needle path",
    "it appeared benign on ultrasound",
)
ABORT_REASONS = (
    "the target could not be reached despite repeated attempts",
    "persistent airway bleeding obscured the pathway",
    "registration divergence could not be corrected",
)
TRAPS = {
    "surveyed_not_sampled": "An EBUS station is visualized but not sampled, with a stated reason.",
    "aborted_navigation": "Navigation to the only lung target fails and nothing is sampled.",
    "til_without_volumetric": "Radial EBUS alone is described as confirming tool-in-lesion; TIL is not recordable.",
    "negated_complications": "Specific complications are explicitly denied.",
    "per_pass_detail": "Each needle pass is described individually (single-pass records).",
    "planned_only_ebus": "Linear EBUS staging was planned but not performed.",
    "historical_mention": "A prior procedure and its stations appear only in the history.",
    "size_in_cm": "Lesion size is given in centimetres.",
    "complication_present": "A procedural complication occurred.",
}


@dataclass
class Unit:
    id: str
    group: str
    kind: str
    role: str
    params: dict[str, Any]
    sets: list[tuple[str, str, str, Any]]
    core: bool = False
    weight: float = 0.75
    assertion: str = "active"
    trap: str | None = None


@dataclass
class Scenario:
    family_id: str
    seed: int
    components: tuple[str, ...]
    platform: str | None
    event_date: date
    rows: dict[str, list[dict[str, Any]]]
    units: list[Unit]
    traps: list[str]
    groups: list[str] = field(default_factory=list)  # render order


class _Builder:
    def __init__(self) -> None:
        self.rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.units: list[Unit] = []
        self.groups: list[str] = []
        self.counts: Counter[str] = Counter()

    def row(self, collection: str, prefix: str, **parents: str) -> str:
        self.counts[prefix] += 1
        local_id = f"{prefix}{self.counts[prefix]}"
        self.rows[collection].append({"local_id": local_id, "parents": parents})
        return local_id

    def unit(
        self,
        group: str,
        kind: str,
        role: str,
        sets,
        *,
        core=False,
        weight=0.75,
        assertion="active",
        trap=None,
        **params,
    ) -> None:
        if group not in self.groups:
            self.groups.append(group)
        self.units.append(
            Unit(
                f"u{len(self.units) + 1}",
                group,
                kind,
                role,
                params,
                list(sets),
                core,
                weight,
                assertion,
                trap,
            )
        )


def _pick_traps(rng: random.Random, robotic: bool, ebus: bool) -> list[str]:
    candidates = ["negated_complications", "complication_present", "historical_mention"]
    if robotic:
        candidates += [
            "aborted_navigation",
            "til_without_volumetric",
            "per_pass_detail",
            "size_in_cm",
        ]
        if not ebus:
            candidates.append("planned_only_ebus")
    if ebus:
        candidates.append("surveyed_not_sampled")
    chosen = rng.sample(candidates, k=rng.choice([0, 1, 1, 2]))
    if "complication_present" in chosen and "negated_complications" in chosen:
        chosen.remove("negated_complications")
    return chosen


def _case_details(b: _Builder, rng: random.Random, robotic: bool, ebus: bool) -> None:
    age, sex = rng.randint(45, 88), rng.choice(["male", "female"])
    b.unit(
        "demographics",
        "demographics",
        "age_sex",
        [
            ("case_details", "case_details", "age_at_procedure_years", float(age)),
            ("case_details", "case_details", "sex_at_birth", sex),
        ],
        weight=0.9,
        age=age,
        sex=sex,
    )
    smoking = rng.choice(["never", "former", "former", "current"])
    sets = [("case_details", "case_details", "smoking_status", smoking)]
    pack_years = None
    if smoking != "never":
        pack_years = rng.choice([10, 15, 20, 25, 30, 40, 50])
        sets.append(("case_details", "case_details", "pack_years", float(pack_years)))
    b.unit(
        "demographics",
        "demographics",
        "smoking",
        sets,
        weight=0.5,
        status=smoking,
        pack_years=pack_years,
    )
    intent = (
        "diagnosis_and_staging" if robotic and ebus else ("diagnosis" if robotic else "staging")
    )
    text = {
        "diagnosis": "tissue diagnosis of a peripheral lung lesion",
        "staging": "mediastinal staging of known lung cancer",
        "diagnosis_and_staging": "tissue diagnosis of a peripheral lung lesion and mediastinal staging",
    }[intent]
    b.unit(
        "indication",
        "indication",
        "indication",
        [
            ("case_details", "case_details", "indication", text),
            ("case_details", "case_details", "intent", intent),
        ],
        weight=0.85,
        text=text,
    )
    asa = rng.choice([2, 3, 3, 4])
    b.unit(
        "asa",
        "asa",
        "asa",
        [("case_details", "case_details", "asa_physical_status", asa)],
        weight=0.5,
        asa=asa,
    )
    anesthesia = rng.choices(["general", "moderate"], weights=[0.85, 0.15])[0]
    if anesthesia == "general":
        device = rng.choice(["ETT", "ETT", "LMA"])
        size, unit = (
            (rng.choice([7.5, 8.0, 8.5]), "mm")
            if device == "ETT"
            else (rng.choice([4.0, 5.0]), "LMA_size")
        )
    else:
        device, size, unit = "natural_airway", None, None
    sets = [
        ("case_details", "case_details", "anesthesia_type", anesthesia),
        ("case_details", "case_details", "airway_device", device),
    ]
    if size is not None:
        sets += [
            ("case_details", "case_details", "airway_size_value", size),
            ("case_details", "case_details", "airway_size_unit", unit),
        ]
    b.unit(
        "anesthesia",
        "anesthesia",
        "anesthesia",
        sets,
        weight=0.9,
        type=anesthesia,
        device=device,
        size=size,
    )


def _lung_target(
    b: _Builder,
    rng: random.Random,
    number: int,
    traps: list[str],
    platform: str,
    specimen_labels: list[str],
) -> bool:
    """Returns True when the target was sampled."""
    lobe = rng.choice(list(LOBES))
    lobe_text, segments = LOBES[lobe]
    segment, code = rng.choice(segments)
    target = b.row("targets", "T")
    group = f"target:{target}"
    size = rng.randint(8, 42)
    b.unit(
        group,
        "target",
        "identity",
        [
            ("targets", target, "site", "lung"),
            ("targets", target, "lobe", lobe),
            ("targets", target, "anatomic_label", f"Target {number}"),
        ],
        core=True,
        number=number,
        lobe=lobe_text,
    )
    b.unit(
        group,
        "target",
        "segment",
        [("targets", target, "segment", f"{segment} segment ({code})")],
        weight=0.6,
        segment=f"{segment} segment ({code})",
    )
    b.unit(
        group,
        "target",
        "size",
        [("targets", target, "max_diameter_mm", float(size))],
        weight=0.85,
        size=size,
        cm="size_in_cm" in traps,
        trap="size_in_cm" if "size_in_cm" in traps else None,
    )
    attenuation = rng.choices(list(ATTENUATION), weights=[0.6, 0.2, 0.15, 0.05])[0]
    b.unit(
        group,
        "target",
        "attenuation",
        [("targets", target, "lesion_attenuation_type", attenuation)],
        weight=0.7,
        attenuation=ATTENUATION[attenuation],
    )
    bronchus = rng.random() < 0.6
    b.unit(
        group,
        "target",
        "bronchus",
        [("targets", target, "bronchus_sign_present", bronchus)],
        weight=0.6,
        assertion="active" if bronchus else "negated",
        present=bronchus,
    )
    if rng.random() < 0.6:
        avid = rng.random() < 0.75
        sets = [("targets", target, "pet_avid", avid)]
        suv = round(rng.uniform(2.6, 14.0), 1) if avid else None
        if suv is not None:
            sets.append(("targets", target, "pet_suv_max", suv))
        b.unit(
            group,
            "target",
            "pet",
            sets,
            weight=0.7,
            assertion="active" if avid else "negated",
            avid=avid,
            suv=suv,
        )
    b.unit(
        group,
        "target",
        "prespecified",
        [("targets", target, "prespecified_biopsy_target", True)],
        weight=0.5,
    )

    aborted = "aborted_navigation" in traps
    runs = 2 if not aborted and rng.random() < 0.1 else 1
    reached_run = None
    for index in range(runs):
        run = b.row("navigation_runs", "NR", target_id=target)
        reached = not aborted and index == runs - 1
        sets = [
            ("navigation_runs", run, "target_reached_operational", reached),
            # Dictionary: "Whether platform/operator declared target reached." The sentence
            # is that declaration, so it states this field as well.
            ("navigation_runs", run, "navigation_success_system_reported", reached),
            ("targets", target, "diagnostic_attempted", True),
        ]
        if reached:
            sets.append(("navigation_runs", run, "navigation_run_outcome", "reached_and_sampled"))
            reached_run = run
        else:
            reason = rng.choice(ABORT_REASONS[1:]) if not aborted else ABORT_REASONS[0]
            sets += [
                (
                    "navigation_runs",
                    run,
                    "navigation_run_outcome",
                    "aborted" if aborted else "not_reached_not_sampled",
                ),
                ("navigation_runs", run, "navigation_failure_reason", reason),
            ]
        b.unit(
            f"navigation:{run}",
            "navigation",
            "run",
            sets,
            core=True,
            number=number,
            reached=reached,
            attempt=index + 1,
            attempts=runs,
            reason=None if reached else sets[-1][3],
            assertion="active" if reached else "negated",
        )
        b.unit(
            f"platform:{run}",
            "platform",
            "platform",
            [("navigation_runs", run, "platform_family", platform)],
            weight=0.9 if index == 0 else 0.0,
            platform=platform,
        )
    if aborted:
        b.unit(
            group,
            "target",
            "not_sampled",
            [
                ("targets", target, "sampling_attempted", False),
                ("targets", target, "reason_sampling_not_attempted", "target not reached"),
            ],
            core=True,
            assertion="negated",
            trap="aborted_navigation",
        )
        return False

    events = []
    til_trap = "til_without_volumetric" in traps
    if til_trap or rng.random() < 0.85:
        event = b.row("localization_events", "L", target_id=target, navigation_run_id=reached_run)
        view = (
            "concentric"
            if til_trap
            else rng.choice(["concentric", "concentric", "eccentric", "adjacent"])
        )
        b.unit(
            f"loc:{event}",
            "radial",
            "radial",
            [
                ("localization_events", event, "localization_modality", "radial_EBUS"),
                ("localization_events", event, "radial_ebus_view", view),
                ("localization_events", event, "lesion_visible", True),
            ],
            core=True,
            view=view,
            claim_til=til_trap,
            trap="til_without_volumetric" if til_trap else None,
        )
        events.append(event)
    if rng.random() < 0.7 and "til_without_volumetric" not in traps:
        event = b.row("localization_events", "L", target_id=target, navigation_run_id=reached_run)
        modality = rng.choice(list(VOLUMETRIC))
        phrase, basis = VOLUMETRIC[modality]
        sets = [("localization_events", event, "localization_modality", modality)]
        til = rng.random() < 0.75
        if til:
            component = rng.choice(["needle_tip", "sampling_tool"])
            sets += [
                ("localization_events", event, f, v)
                for f, v in (
                    ("tool_lesion_relationship", "TIL"),
                    ("actual_lesion_vs_virtual_target", "actual_lesion"),
                    ("sampling_tool_present", True),
                    ("verified_tool_component", component),
                    ("confirmation_basis", basis),
                    ("final_prebiopsy_confirmation", True),
                    ("event_phase", "prebiopsy"),
                    ("lesion_visible", True),
                )
            ]
        else:
            sets += [
                ("localization_events", event, "tool_lesion_relationship", "touching"),
                ("localization_events", event, "lesion_visible", True),
            ]
        b.unit(
            f"loc:{event}",
            "volumetric",
            "event",
            sets,
            core=True,
            modality=phrase,
            til=til,
            component="needle tip" if til and component == "needle_tip" else "biopsy needle",
        )
        events.append(event)
    if rng.random() < 0.4:
        event = b.row("localization_events", "L", target_id=target, navigation_run_id=reached_run)
        b.unit(
            f"loc:{event}",
            "fluoroscopy",
            "event",
            [("localization_events", event, "localization_modality", "2D_fluoroscopy")],
            core=True,
        )
        events.append(event)

    tools = [
        t
        for t, p in (
            ("aspiration_needle", 0.8),
            ("forceps", 0.7),
            ("cryoprobe", 0.35),
            ("brush", 0.3),
        )
        if rng.random() < p
    ] or ["forceps"]
    if "per_pass_detail" in traps and "aspiration_needle" not in tools:
        tools.insert(0, "aspiration_needle")
    acquisitions: list[tuple[str, str]] = []
    for tool in tools:
        gauge = rng.choice([19, 21, 22, 25]) if tool == "aspiration_needle" else None
        size = rng.choice([1.1, 1.7, 2.4]) if tool == "cryoprobe" else None
        passes = rng.randint(2, 7) if tool != "brush" else rng.randint(1, 2)
        if tool == "aspiration_needle" and "per_pass_detail" in traps:
            for index in range(1, min(passes, 4) + 1):
                acquisition = b.row("sampling_acquisitions", "A", target_id=target)
                b.unit(
                    f"pass:{acquisition}",
                    "single_pass",
                    "pass",
                    [
                        (
                            "sampling_acquisitions",
                            acquisition,
                            "acquisition_record_granularity",
                            "single_pass",
                        ),
                        ("sampling_acquisitions", acquisition, "sampling_tool", tool),
                        ("sampling_acquisitions", acquisition, "needle_gauge", gauge),
                        ("targets", target, "sampling_attempted", True),
                        # Dictionary: target needle fields apply whenever a needle is used.
                        ("targets", target, "needle_gauge", gauge),
                    ]
                    + (
                        [("targets", target, "needle_pass_count", index)]
                        if index == min(passes, 4)
                        else []
                    ),
                    core=True,
                    number=index,
                    target=number,
                    gauge=gauge,
                    trap="per_pass_detail",
                )
                acquisitions.append((acquisition, tool))
            continue
        acquisition = b.row("sampling_acquisitions", "A", target_id=target)
        sets = [
            (
                "sampling_acquisitions",
                acquisition,
                "acquisition_record_granularity",
                "aggregate_reported",
            ),
            ("sampling_acquisitions", acquisition, "sampling_tool", tool),
            ("targets", target, "sampling_attempted", True),
        ]
        if gauge:
            sets.append(("sampling_acquisitions", acquisition, "needle_gauge", gauge))
            sets.append(("targets", target, "needle_gauge", gauge))
        if size:
            sets.append(("sampling_acquisitions", acquisition, "tool_size_mm", size))
        b.unit(
            f"acq:{acquisition}",
            "acquisition",
            "tool",
            sets,
            core=True,
            tool=tool,
            gauge=gauge,
            size=size,
        )
        b.unit(
            f"acq:{acquisition}",
            "acquisition",
            "passes",
            [("sampling_acquisitions", acquisition, "reported_pass_count", passes)]
            + (
                [("targets", target, "needle_pass_count", passes)]
                if tool == "aspiration_needle"
                else []
            ),
            weight=0.85,
            passes=passes,
        )
        acquisitions.append((acquisition, tool))

    if rng.random() < 0.7:
        result, adequate = rng.choice(ROSE_LUNG)
        b.unit(
            f"rose:{target}",
            "rose",
            "rose",
            [
                ("targets", target, "rose_used", True),
                ("targets", target, "rose_result", result),
                ("targets", target, "rose_adequate", adequate),
            ]
            + [
                ("sampling_acquisitions", a, "rose_performed", True)
                for a, t in acquisitions
                if t == "aspiration_needle"
            ],
            weight=1.0,
            result=result,
            adequate=adequate,
            number=number,
        )

    by_type: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for acquisition, tool in acquisitions:
        by_type["cytology" if tool in {"aspiration_needle", "brush"} else "histology"].append(
            (acquisition, tool)
        )
    for specimen_type, members in by_type.items():
        label = chr(ord("A") + len(specimen_labels))
        specimen_labels.append(label)
        specimen = b.row("specimens", "SP", target_id=target)
        sets = [
            ("specimens", specimen, "specimen_label", label),
            ("specimens", specimen, "specimen_type", specimen_type),
            ("specimens", specimen, "target_attribution_status", "attributed"),
            ("targets", target, "specimen_obtained", True),
        ]
        for acquisition, _ in members:
            link = b.row(
                "sampling_specimen_links", "LK", sampling_pass_id=acquisition, specimen_id=specimen
            )
            sets.append(("sampling_specimen_links", link, "link_certainty", "confirmed"))
        b.unit(
            f"specimen:{specimen}",
            "specimen",
            "specimen",
            sets,
            weight=0.8,
            label=label,
            specimen_type=specimen_type,
            number=number,
            tools=sorted({t for _, t in members}),
        )
    return True


def _ebus(b: _Builder, rng: random.Random, traps: list[str], specimen_labels: list[str]) -> None:
    session = b.row("ebus_sessions", "ES")
    purpose = rng.choice(["initial_staging", "initial_staging", "targeted_diagnosis", "restaging"])
    strategy = "systematic" if purpose != "targeted_diagnosis" else "targeted"
    b.unit(
        "ebus_session",
        "ebus_session",
        "session",
        [
            ("ebus_sessions", session, "primary_purpose", purpose),
            ("ebus_sessions", session, "performed_sampling_strategy", strategy),
        ],
        core=True,
        purpose=purpose,
        strategy=strategy,
    )
    if strategy == "systematic":
        b.unit(
            "ebus_session",
            "ebus_session",
            "complete",
            [("ebus_sessions", session, "systematic_exam_complete", True)],
            weight=0.5,
        )
    surveyed = rng.sample(STATIONS, k=rng.randint(3, 6))
    sampled = surveyed[: rng.randint(1, min(4, len(surveyed)))]
    if "surveyed_not_sampled" in traps and len(sampled) == len(surveyed):
        sampled = sampled[:-1] or sampled
    for station in surveyed:
        survey = b.row("station_surveys", "S", ebus_session_id=session)
        was_sampled = station in sampled
        group = f"station:{survey}"
        sets = [
            ("station_surveys", survey, "iaslc_station", station),
            ("station_surveys", survey, "survey_modality", "EBUS"),
            ("station_surveys", survey, "station_surveyed", True),
            ("station_surveys", survey, "station_visualized", True),
            ("station_surveys", survey, "station_sampled", was_sampled),
        ]
        reason = None
        if not was_sampled:
            reason = rng.choice(NOT_SAMPLED_REASONS)
            sets.append(("station_surveys", survey, "reason_not_sampled", reason))
        b.unit(
            group,
            "station",
            "survey",
            sets,
            core=True,
            station=station,
            sampled=was_sampled,
            reason=reason,
            assertion="active" if was_sampled else "negated",
            trap="surveyed_not_sampled"
            if not was_sampled and "surveyed_not_sampled" in traps
            else None,
        )
        node = None
        if was_sampled:
            node = b.row("targets", "N", station_survey_id=survey, ebus_session_id=session)
            passes, gauge = rng.randint(2, 5), rng.choice([21, 22, 22, 25])
            acquisition = b.row("sampling_acquisitions", "A", target_id=node)
            b.unit(
                f"node:{node}",
                "node_sampling",
                "needle",
                [
                    ("targets", node, "site", "lymph_node"),
                    ("targets", node, "iaslc_station", station),
                    ("targets", node, "sampling_attempted", True),
                    ("targets", node, "needle_pass_count", passes),
                    ("targets", node, "needle_gauge", gauge),
                    ("targets", node, "puncture_route", "EBUS"),
                    (
                        "sampling_acquisitions",
                        acquisition,
                        "acquisition_record_granularity",
                        "aggregate_reported",
                    ),
                    ("sampling_acquisitions", acquisition, "sampling_tool", "aspiration_needle"),
                    ("sampling_acquisitions", acquisition, "reported_pass_count", passes),
                    ("sampling_acquisitions", acquisition, "needle_gauge", gauge),
                ],
                core=True,
                station=station,
                passes=passes,
                gauge=gauge,
            )
        if rng.random() < 0.45:
            size = rng.randint(6, 24) if was_sampled else rng.randint(3, 9)
            sets = [
                ("station_surveys", survey, "largest_short_axis_mm", float(size)),
                ("station_surveys", survey, "size_axis_explicit", True),
            ]
            if node:
                sets += [
                    ("targets", node, "short_axis_mm", float(size)),
                    ("targets", node, "size_axis_explicit", True),
                    ("targets", node, "measurement_modality", "EBUS"),
                ]
            b.unit(group, "station", "axis", sets, weight=1.0, station=station, size=size)
        if node and rng.random() < 0.7:
            result, adequate = rng.choice(ROSE_NODE)
            b.unit(
                f"node_rose:{node}",
                "node_rose",
                "rose",
                [
                    ("targets", node, "rose_used", True),
                    ("targets", node, "rose_result", result),
                    ("targets", node, "rose_adequate", adequate),
                    ("ebus_sessions", session, "rose_used", True),
                    ("sampling_acquisitions", acquisition, "rose_performed", True),
                ],
                weight=1.0,
                station=station,
                result=result,
            )
        if node and rng.random() < 0.6:
            label = chr(ord("A") + len(specimen_labels))
            specimen_labels.append(label)
            specimen = b.row("specimens", "SP", target_id=node)
            link = b.row(
                "sampling_specimen_links", "LK", sampling_pass_id=acquisition, specimen_id=specimen
            )
            b.unit(
                f"specimen:{specimen}",
                "node_specimen",
                "specimen",
                [
                    ("specimens", specimen, "specimen_label", label),
                    ("specimens", specimen, "specimen_type", "cytology"),
                    ("specimens", specimen, "target_attribution_status", "attributed"),
                    ("targets", node, "specimen_obtained", True),
                    ("sampling_specimen_links", link, "link_certainty", "confirmed"),
                ],
                weight=1.0,
                label=label,
                station=station,
            )


def _complications(
    b: _Builder, rng: random.Random, traps: list[str], side: str | None, robotic: bool
) -> str:
    if "complication_present" in traps:
        complication = b.row("complications", "C")
        tube = rng.random() < 0.5
        laterality = side or rng.choice(["left", "right"])
        b.unit(
            "complications",
            "complications",
            "present",
            [
                ("complications", complication, "category", "pneumothorax"),
                ("complications", complication, "state", "present"),
                ("complications", complication, "event_time_window", "immediate"),
                ("complications", complication, "pneumothorax_laterality", laterality),
                ("complications", complication, "pleural_intervention", tube),
                (
                    "complications",
                    complication,
                    "procedure_component_attribution",
                    "robotic_bronchoscopy" if robotic else "linear_ebus",
                ),
                ("revision", "revision", "complication_assessment", "present"),
            ],
            core=True,
            laterality=laterality,
            tube=tube,
            robotic=robotic,
            trap="complication_present",
        )
        return "inpatient" if tube else "observation"
    b.unit(
        "complications",
        "complications",
        "summary",
        [("revision", "revision", "complication_assessment", "absent")],
        core=True,
        assertion="negated",
    )
    if "negated_complications" in traps:
        sets = []
        for category in ("pneumothorax", "bleeding"):
            complication = b.row("complications", "C")
            sets += [
                ("complications", complication, "category", category),
                ("complications", complication, "state", "absent"),
            ]
        b.unit(
            "complications",
            "complications",
            "negated",
            sets,
            core=True,
            assertion="negated",
            trap="negated_complications",
        )
    return rng.choice(["home", "home", "observation"])


def sample_scenario(seed: int) -> Scenario:
    rng = random.Random(seed)
    b = _Builder()
    mix = rng.choices(["robotic", "ebus", "both"], weights=[0.35, 0.25, 0.40])[0]
    robotic, ebus = mix in {"robotic", "both"}, mix in {"ebus", "both"}
    traps = _pick_traps(rng, robotic, ebus)
    platform = rng.choice(PLATFORMS) if robotic else None
    planned_only = "planned_only_ebus" in traps
    _case_details(b, rng, robotic, ebus)
    if "historical_mention" in traps:
        b.unit(
            "history",
            "history",
            "history",
            [],
            core=True,
            station=rng.choice(["7", "4R", "11L"]),
            year=rng.choice([2023, 2024, 2025]),
            trap="historical_mention",
        )
    aborted = "aborted_navigation" in traps
    if robotic:
        sets = [
            ("procedures", "P1", "category", "robotic_bronchoscopy"),
            ("procedures", "P1", "planned", True),
            ("procedures", "P1", "performance", "attempted" if aborted else "performed"),
            ("procedures", "P1", "completion", "aborted_after_start" if aborted else "completed"),
        ]
        if aborted:
            sets.append(("procedures", "P1", "abort_reason", "target could not be reached"))
        b.rows["procedures"].append({"local_id": "P1", "parents": {}})
        b.unit("procedure_robotic", "procedure", "robotic", sets, core=True, aborted=aborted)
    if ebus or planned_only:
        local = "P2" if robotic else "P1"
        b.rows["procedures"].append({"local_id": local, "parents": {}})
        if planned_only:
            sets = [
                ("procedures", local, "category", "linear_ebus"),
                ("procedures", local, "planned", True),
                ("procedures", local, "performance", "not_performed"),
                ("procedures", local, "completion", "not_started"),
            ]
            b.unit(
                "procedure_ebus",
                "procedure",
                "ebus_planned_only",
                sets,
                core=True,
                assertion="negated",
                trap="planned_only_ebus",
            )
        else:
            sets = [
                ("procedures", local, "category", "linear_ebus"),
                ("procedures", local, "planned", True),
                ("procedures", local, "performance", "performed"),
                ("procedures", local, "completion", "completed"),
            ]
            b.unit("procedure_ebus", "procedure", "ebus", sets, core=True)
    specimen_labels: list[str] = []
    side = None
    if robotic:
        count = 1 if aborted else rng.choices([1, 2], weights=[0.85, 0.15])[0]
        for number in range(1, count + 1):
            _lung_target(b, rng, number, traps, platform, specimen_labels)
        side = SIDE[next(f[3] for u in b.units for f in u.sets if f[2] == "lobe")]
    if ebus and not planned_only:
        _ebus(b, rng, traps, specimen_labels)
    disposition = _complications(b, rng, traps, side, robotic)
    minutes = rng.randint(35, 130)
    b.unit(
        "duration",
        "duration",
        "duration",
        [("case_details", "case_details", "procedure_duration_minutes", float(minutes))],
        weight=0.5,
        minutes=minutes,
    )
    b.unit(
        "disposition",
        "disposition",
        "disposition",
        [("case_details", "case_details", "immediate_disposition", disposition)],
        weight=0.6,
        disposition=disposition,
    )
    components = tuple(
        c
        for c, on in (("robotic_bronchoscopy", robotic), ("linear_ebus", ebus and not planned_only))
        if on
    )
    return Scenario(
        family_id=f"truth-{seed}",
        seed=seed,
        components=components,
        platform=platform or "linear_ebus",
        event_date=date(2026, 1, 5) + timedelta(days=rng.randint(0, 300)),
        rows=dict(b.rows),
        units=b.units,
        traps=traps,
        groups=b.groups,
    )


__all__ = ["LOBES", "STATIONS", "TRAPS", "Scenario", "Unit", "sample_scenario"]
