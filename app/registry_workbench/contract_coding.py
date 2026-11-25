"""Suggested CPT codes from a robotic_ebus_v1 contract proposal.

The contract proposal is adapted to a minimal ``RegistryRecord`` and handed to
the existing registry-to-CPT rules, so station counting, bundling, modifier 59
and add-on handling stay in one place. This module only decides which contract
facts are firm enough to count, and keeps the supporting quote for every fact
that contributed to a code.

Nothing here reads note text. Facts that are unresolved, or sampling that is
not attributed to a target, never drive a code; they become review flags.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.coder.domain_rules.registry_to_cpt.coding_rules import (
    derive_all_codes_with_meta,
    derive_units_for_codes,
)
from app.registry.application.coding_support_builder import build_coding_support_payload
from app.registry.quality_signals import parse_quality_signal_warning
from app.registry.schema import RegistryRecord

STARTED = {"performed", "attempted"}
NODAL_ACTIONS = {
    "aspiration_needle": "needle_aspiration",
    "core_needle": "core_biopsy",
    "forceps": "forceps_biopsy",
    "mini_forceps": "forceps_biopsy",
}
NEEDLE_TOOLS = {"aspiration_needle", "core_needle"}
FORCEPS_TOOLS = {"forceps", "mini_forceps"}
RADIAL_VIEWS = {
    "concentric": "Concentric",
    "eccentric": "Eccentric",
    "adjacent": "Adjacent",
    "not_visualized": "Not visualized",
}
NODAL_CODES = {"31652", "31653"}

# Which adapter facts back which code. 31629's modifier 59 also rests on the
# nodal sampling, so that code shows both sites.
CODE_FACT_KEYS: dict[str, tuple[str, ...]] = {
    "31652": ("nodal",),
    "31653": ("nodal",),
    "31627": ("navigation",),
    "31654": ("radial",),
    "31628": ("lung_biopsy",),
    "31632": ("lung_biopsy",),
    "31629": ("lung_needle",),
    "31633": ("lung_needle",),
    "31623": ("brush",),
    "31624": ("bal",),
}

SCOPE_NOTE = (
    "Codes are suggested from the extracted registry facts for the linear EBUS and "
    "robotic bronchoscopy code family only, for review by a coder. Other codes are not assessed."
)
NOT_ASSESSED = [
    {"codes": ["31626"], "label": "Fiducial marker placement", "reason": "no registry field"},
    {
        "codes": ["77012", "76377"],
        "label": "Cone-beam CT guidance and 3D rendering",
        "reason": "imaging codes are not derived from registry facts",
    },
    {
        "codes": ["76982", "76983"],
        "label": "EBUS elastography",
        "reason": "no registry field",
    },
    {
        "codes": ["43237", "43238"],
        "label": "EUS-B sampling",
        "reason": "esophageal route is outside this code family",
    },
    {
        "codes": ["31622", "31625", "31645"],
        "label": "Diagnostic inspection, endobronchial biopsy, therapeutic aspiration",
        "reason": "not represented in the registry field list",
    },
    {
        "codes": ["99152", "99153"],
        "label": "Moderate sedation",
        "reason": "needs sedation times and provider, which the registry does not hold",
    },
]


@dataclass
class Evidence:
    """One contract fact that contributed to (or was excluded from) a code."""

    label: str
    paths: list[str]
    quote: str | None = None
    start: int | None = None
    end: int | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"label": self.label, "derived_from": self.paths}
        if self.start is not None and self.end is not None:
            out.update(quote=self.quote, start=self.start, end=self.end)
        return out


@dataclass
class Trace:
    facts: dict[str, list[Evidence]] = field(default_factory=dict)
    excluded: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    review_flags: list[dict[str, Any]] = field(default_factory=list)

    def add(self, key: str, evidence: Evidence) -> None:
        self.facts.setdefault(key, []).append(evidence)

    def exclude(self, key: str, evidence: Evidence, reason: str) -> None:
        self.excluded.setdefault(key, []).append({**evidence.as_dict(), "reason": reason})

    def flag(self, code: str, message: str, *, codes: tuple[str, ...] = ()) -> None:
        item = {"flag": code, "message": message, "codes": list(codes)}
        if item not in self.review_flags:
            self.review_flags.append(item)


class _Proposal:
    """Read access to a proposal that respects unresolved provenance."""

    def __init__(self, proposal: dict[str, Any], source_text: str | None) -> None:
        self.data = proposal
        self.text = source_text
        self.prov: dict[str, dict[str, Any]] = {}
        for entry in proposal.get("field_provenance") or []:
            path = entry.get("field_path")
            if isinstance(path, str):
                self.prov[path] = entry

    def rows(self, collection: str) -> list[dict[str, Any]]:
        rows = self.data.get(collection) or []
        return rows if isinstance(rows, list) else []

    def usable(self, path: str) -> bool:
        entry = self.prov.get(path)
        return entry is None or entry.get("conflict_status") != "unresolved"

    def get(self, collection: str, index: int, name: str) -> Any:
        """Value of a field, or None when it is absent or held as a conflict."""
        path = f"/{collection}/{index}/{name}"
        if not self.usable(path):
            return None
        return self.rows(collection)[index].get(name)

    def evidence(self, label: str, *paths: str) -> Evidence:
        """Evidence for the first of ``paths`` that carries a source span."""
        present = [p for p in paths if p in self.prov]
        for path in present:
            entry = self.prov[path]
            start, end = entry.get("source_start"), entry.get("source_end")
            if isinstance(start, int) and isinstance(end, int):
                quote = entry.get("source_excerpt")
                if quote is None and self.text is not None:
                    quote = self.text[start:end]
                return Evidence(label, present or list(paths), quote, start, end)
        return Evidence(label, present or list(paths))


def provenance_from_evidence_map(
    evidence: dict[str, list[Any]], source_text: str | None = None
) -> list[dict[str, Any]]:
    """Turn a gold ``{path: [start, end, assertion]}`` map into provenance entries."""
    out = []
    for path, (start, end, assertion) in sorted(evidence.items()):
        entry = {
            "field_path": path,
            "source_start": start,
            "source_end": end,
            "assertion_context": assertion,
            "conflict_status": "none",
        }
        if source_text is not None:
            entry["source_excerpt"] = source_text[start:end]
        out.append(entry)
    return out


def _lung_label(target: dict[str, Any]) -> str:
    """Text the existing rules can read a lobe from; generic when no lobe is known."""
    lobe = target.get("lobe")
    if not lobe:
        return "Lung nodule"
    segment = str(target.get("segment") or "").strip()
    return f"{lobe} {segment} nodule".replace("  ", " ") if segment else f"{lobe} nodule"


def to_registry_record(
    proposal: dict[str, Any], source_text: str | None = None
) -> tuple[RegistryRecord, Trace]:
    """Adapt the contract proposal to the minimal record the CPT rules read."""
    p, trace = _Proposal(proposal, source_text), Trace()
    procedures: dict[str, Any] = {}

    started: dict[str, int] = {}
    for index, _row in enumerate(p.rows("procedures")):
        if p.get("procedures", index, "performance") in STARTED:
            category = p.get("procedures", index, "category")
            if category:
                started[str(category)] = index

    targets = {
        str(row.get("target_id")): (index, row) for index, row in enumerate(p.rows("targets"))
    }
    surveys = {
        str(row.get("station_survey_id")): (index, row)
        for index, row in enumerate(p.rows("station_surveys"))
    }

    # Sampling rows grouped by target; unattributed sampling never drives a code.
    by_target: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for index, row in enumerate(p.rows("sampling_acquisitions")):
        tool = p.get("sampling_acquisitions", index, "sampling_tool")
        status = p.get("sampling_acquisitions", index, "attribution_status")
        target_id = str(row.get("target_id") or "")
        if status != "attributed" or target_id not in targets:
            trace.flag(
                "sampling_not_attributed",
                f"Sampling with {tool or 'an unnamed tool'} is not attributed to a target; "
                "it was not used for coding.",
            )
            continue
        by_target.setdefault(target_id, []).append((index, row))

    def acquisitions(target_id: str, tools: set[str]) -> list[tuple[int, str]]:
        out = []
        for index, _row in by_target.get(target_id, []):
            tool = p.get("sampling_acquisitions", index, "sampling_tool")
            if tool in tools:
                out.append((index, str(tool)))
        return out

    # --- Linear EBUS -------------------------------------------------------
    if "linear_ebus" in started:
        node_events: list[dict[str, Any]] = []
        seen_stations: set[str] = set()
        structure_sampled = False

        for target_id, (t_index, target) in targets.items():
            site = p.get("targets", t_index, "site")
            if site not in {"lymph_node", "central_mass"}:
                continue
            station = p.get("targets", t_index, "iaslc_station") if site == "lymph_node" else None
            label = f"Station {station}" if station else (target.get("anatomic_label") or site)
            survey_index = surveys.get(str(target.get("station_survey_id") or ""), (None, None))[0]
            survey_sampled = (
                p.get("station_surveys", survey_index, "station_sampled")
                if survey_index is not None
                else None
            )
            needle_rows = acquisitions(target_id, set(NODAL_ACTIONS))
            attempted = p.get("targets", t_index, "sampling_attempted") is True
            sampled = bool(needle_rows) or attempted or survey_sampled is True
            if not sampled:
                continue
            if site == "central_mass" and not target.get("ebus_session_id"):
                continue  # not sampled under linear EBUS; handled as not assessed below
            paths = [f"/sampling_acquisitions/{i}/sampling_tool" for i, _ in needle_rows]
            paths.append(f"/targets/{t_index}/sampling_attempted")
            if survey_index is not None:
                paths.append(f"/station_surveys/{survey_index}/station_sampled")
            evidence = p.evidence(f"{label} sampled", *paths)
            if survey_sampled is False:
                trace.exclude("nodal", evidence, "the station survey says it was not sampled")
                trace.flag(
                    "survey_target_disagreement",
                    f"{label}: sampling is recorded on the node but the station survey says "
                    "not sampled. It was not counted.",
                    codes=tuple(NODAL_CODES),
                )
                continue
            route = p.get("targets", t_index, "puncture_route")
            if route == "EUS_B":
                trace.exclude("nodal", evidence, "sampled by the esophageal (EUS-B) route")
                continue
            action = NODAL_ACTIONS[needle_rows[0][1]] if needle_rows else "needle_aspiration"
            event: dict[str, Any] = {
                "action": action,
                "evidence_quote": evidence.quote or f"{label} sampled",
            }
            if station:
                event["station"] = station
                seen_stations.add(str(station))
            else:
                event["target_text"] = str(label)
                structure_sampled = True
            node_events.append(event)
            trace.add("nodal", evidence)

        for s_index, _survey in enumerate(p.rows("station_surveys")):
            station = p.get("station_surveys", s_index, "iaslc_station")
            if not station or str(station) in seen_stations:
                continue
            sampled = p.get("station_surveys", s_index, "station_sampled")
            evidence = p.evidence(
                f"Station {station} surveyed",
                f"/station_surveys/{s_index}/station_sampled",
                f"/station_surveys/{s_index}/station_surveyed",
                f"/station_surveys/{s_index}/iaslc_station",
            )
            if sampled is True:
                if p.get("station_surveys", s_index, "survey_modality") == "EUS_B":
                    trace.exclude("nodal", evidence, "sampled by the esophageal (EUS-B) route")
                    continue
                evidence.label = f"Station {station} sampled"
                node_events.append(
                    {
                        "station": station,
                        "action": "needle_aspiration",
                        "evidence_quote": evidence.quote or f"Station {station} sampled",
                    }
                )
                seen_stations.add(str(station))
                trace.add("nodal", evidence)
                continue
            node_events.append(
                {
                    "station": station,
                    "action": "inspected_only",
                    "evidence_quote": evidence.quote or f"Station {station} surveyed",
                }
            )
            trace.exclude("nodal", evidence, "surveyed, not sampled")

        if structure_sampled and seen_stations:
            trace.flag(
                "nonstation_structure_with_stations",
                "A non-station structure was sampled under EBUS alongside nodal stations. "
                "The rules count stations only in this case; a coder should confirm the "
                "station or structure count.",
                codes=tuple(NODAL_CODES),
            )
        procedures["linear_ebus"] = {"performed": True, "node_events": node_events}

    # --- Peripheral sampling ----------------------------------------------
    tbbx_lobes: list[str] = []
    cryo_lobes: list[str] = []
    needle_targets: list[str] = []
    tbbx_done = cryo_done = brush_done = bal_done = False
    for target_id, (t_index, target) in targets.items():
        site = p.get("targets", t_index, "site")
        rows = by_target.get(target_id, [])
        if site != "lung":
            if site == "central_mass" and rows and not target.get("ebus_session_id"):
                trace.flag(
                    "central_mass_sampling_not_assessed",
                    "Sampling of a central mass outside linear EBUS is not assessed here "
                    "(for example endobronchial biopsy, 31625).",
                )
            continue
        visible = {"lobe": p.get("targets", t_index, "lobe"), "segment": target.get("segment")}
        label = _lung_label(visible)
        where = [f"/targets/{t_index}/lobe"]
        for a_index, _row in rows:
            tool = p.get("sampling_acquisitions", a_index, "sampling_tool")
            path = f"/sampling_acquisitions/{a_index}/sampling_tool"
            if tool in NEEDLE_TOOLS:
                needle_targets.append(label)
                trace.add("lung_needle", p.evidence(f"Needle sampling, {label}", path, *where))
            elif tool in FORCEPS_TOOLS:
                tbbx_done = True
                if visible["lobe"]:
                    tbbx_lobes.append(str(visible["lobe"]))
                trace.add("lung_biopsy", p.evidence(f"Forceps biopsy, {label}", path, *where))
            elif tool == "cryoprobe":
                cryo_done = True
                if visible["lobe"]:
                    cryo_lobes.append(str(visible["lobe"]))
                trace.add("lung_biopsy", p.evidence(f"Cryobiopsy, {label}", path, *where))
            elif tool == "brush":
                brush_done = True
                trace.add("brush", p.evidence(f"Brushing, {label}", path, *where))
            elif tool == "BAL":
                bal_done = True
                trace.add("bal", p.evidence(f"Bronchoalveolar lavage, {label}", path, *where))
            elif tool:
                trace.flag(
                    "sampling_tool_not_assessed",
                    f"Sampling with {tool} is not mapped to a code in this family.",
                )

    if needle_targets:
        procedures["peripheral_tbna"] = {
            "performed": True,
            "targets_sampled": list(dict.fromkeys(needle_targets)),
        }
    if tbbx_done:
        procedures["transbronchial_biopsy"] = {
            "performed": True,
            "locations": list(dict.fromkeys(tbbx_lobes)),
        }
    if cryo_done:
        procedures["transbronchial_cryobiopsy"] = {
            "performed": True,
            "locations_biopsied": list(dict.fromkeys(cryo_lobes)),
        }
    if brush_done:
        procedures["brushings"] = {"performed": True}
    if bal_done:
        procedures["bal"] = {"performed": True}

    # --- Radial EBUS -------------------------------------------------------
    views: list[str] = []
    for index, _row in enumerate(p.rows("localization_events")):
        if p.get("localization_events", index, "localization_modality") != "radial_EBUS":
            continue
        view = p.get("localization_events", index, "radial_ebus_view")
        views.append(str(view) if view else "")
        trace.add(
            "radial",
            p.evidence(
                "Radial EBUS" + (f", {view} view" if view else ""),
                f"/localization_events/{index}/localization_modality",
                f"/localization_events/{index}/radial_ebus_view",
            ),
        )
    if "radial" in trace.facts:
        seen = [v for v in views if v in RADIAL_VIEWS and v != "not_visualized"]
        position = seen[0] if seen else ("not_visualized" if "not_visualized" in views else None)
        radial: dict[str, Any] = {"performed": True}
        if position:
            radial["probe_position"] = RADIAL_VIEWS[position]
        procedures["radial_ebus"] = radial

    # --- Navigation --------------------------------------------------------
    if "robotic_bronchoscopy" in started and p.rows("navigation_runs"):
        outcomes = []
        for index, _row in enumerate(p.rows("navigation_runs")):
            outcomes.append(p.get("navigation_runs", index, "navigation_run_outcome"))
            trace.add(
                "navigation",
                p.evidence(
                    "Robotic navigation to target",
                    f"/navigation_runs/{index}/platform_family",
                    f"/navigation_runs/{index}/navigation_run_outcome",
                    f"/navigation_runs/{index}/target_reached_operational",
                    f"/procedures/{started['robotic_bronchoscopy']}/category",
                ),
            )
        procedures["navigational_bronchoscopy"] = {"performed": True}
        if outcomes and all(o in {"aborted", "not_reached_not_sampled"} for o in outcomes):
            trace.flag(
                "navigation_not_completed",
                "Navigation was started but no target was reached; confirm the navigation add-on.",
                codes=("31627",),
            )

    record = RegistryRecord.model_validate({"procedures_performed": procedures})
    return record, trace


def suggest_codes(
    proposal: dict[str, Any],
    *,
    source_text: str | None = None,
    unresolved: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Suggested codes with units, modifiers, rationale and every supporting quote."""
    record, trace = to_registry_record(proposal, source_text)
    codes, rationales, warnings = derive_all_codes_with_meta(record)
    units = derive_units_for_codes(record, codes)
    support = build_coding_support_payload(
        record=record,
        codes=codes,
        code_units=units,
        code_rationales=rationales,
        derivation_warnings=warnings,
    )
    lines = (support.get("coding_summary") or {}).get("lines") or []
    rationale = support.get("coding_rationale") or {}

    deferred = [
        item
        for item in unresolved or []
        if item.get("kind") in {"planned_only", "historical", "uncertain"}
    ]
    if deferred:
        trace.flag(
            "deferred_statements_not_coded",
            f"{len(deferred)} planned, historical or uncertain statement(s) were not used "
            "for coding.",
        )

    out_codes, dropped = [], []
    for line in lines:
        code = str(line.get("code"))
        if line.get("selection_status") != "selected":
            dropped.append({"code": code, "reason": line.get("selection_reason")})
            continue
        keys = CODE_FACT_KEYS.get(code, ())
        evidence = [e for key in keys for e in trace.facts.get(key, [])]
        if code == "31629" and "59" in (line.get("modifiers") or []):
            evidence += trace.facts.get("nodal", [])
        flags = [f["message"] for f in trace.review_flags if code in f["codes"]]
        if not any(e.start is not None for e in evidence):
            flags.append("No supporting passage is linked to this code.")
        out_codes.append(
            {
                "code": code,
                "description": line.get("description"),
                "units": line.get("units"),
                "modifiers": line.get("modifiers") or [],
                "role": line.get("role"),
                "rationale": line.get("selection_reason"),
                "evidence": [e.as_dict() for e in evidence],
                "excluded": [x for key in keys for x in trace.excluded.get(key, [])],
                "review_flags": flags,
                "needs_review": bool(flags),
            }
        )

    plain_warnings = []
    for warning in warnings:
        signal = parse_quality_signal_warning(warning)
        if signal is None:
            plain_warnings.append(str(warning))
        elif signal.get("signal") == "nonstation_ebus_structures_counted_for_nodal_cpt":
            trace.flag(
                "nonstation_structures_counted",
                str(signal.get("detail") or "Non-station EBUS structures were counted."),
                codes=tuple(NODAL_CODES),
            )
    for item in out_codes:
        extra = [
            f["message"]
            for f in trace.review_flags
            if item["code"] in f["codes"] and f["message"] not in item["review_flags"]
        ]
        if extra:
            item["review_flags"] += extra
            item["needs_review"] = True

    selected = {c["code"] for c in out_codes}
    addon_facts = {
        "31627": "navigation",
        "31654": "radial",
    }
    for code, key in addon_facts.items():
        if key in trace.facts and code not in selected:
            trace.flag(
                "addon_without_primary",
                f"{code} was not suggested: the add-on has no primary sampling code in the "
                "extracted facts.",
            )
    if "nodal" in trace.excluded and not (selected & NODAL_CODES) and "nodal" not in trace.facts:
        trace.flag(
            "no_station_sampled",
            "Linear EBUS stations were surveyed but none was sampled, so no EBUS sampling "
            "code is suggested.",
        )

    return {
        "status": "ok",
        "title": "Suggested codes for review",
        "codes": out_codes,
        "dropped": dropped,
        "rules_applied": rationale.get("rules_applied") or [],
        "review_flags": trace.review_flags,
        "excluded": trace.excluded,
        "not_assessed": NOT_ASSESSED,
        "scope_note": SCOPE_NOTE,
        "kb_version": support.get("knowledge_base_version"),
        "warnings": plain_warnings,
    }


__all__ = [
    "NOT_ASSESSED",
    "Evidence",
    "Trace",
    "provenance_from_evidence_map",
    "suggest_codes",
    "to_registry_record",
]
