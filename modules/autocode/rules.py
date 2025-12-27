from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

from proc_schemas.procedure_report import ProcedureReport

# Path is: modules/autocode/rules.py -> autocode -> modules -> repo_root
_RULEBOOK_PATH = Path(__file__).resolve().parents[2] / "configs" / "coding" / "ip_cpt_map.yaml"


@dataclass
class RuleHit:
    cpt: str
    description: str
    reason: str
    units: int
    section: str  # base_codes or addon_codes


@lru_cache(maxsize=1)
def load_rulebook(path: Path | None = None) -> Dict[str, Any]:
    book_path = path or _RULEBOOK_PATH
    with open(book_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def derive_features(report: ProcedureReport) -> Dict[str, Any]:
    core = report.procedure_core
    targets = core.targets
    stations = core.stations_sampled or [t.segment for t in targets if t.segment]
    stations = [s for s in stations if s]
    specimen_totals = sum(sum(specimens.values()) for specimens in [t.specimens for t in targets])
    narrative = str(report.intraop.get("narrative", "")).lower() if isinstance(report.intraop, dict) else ""
    has_bal = "bal" in narrative or any("bal" in (spec or "") for target in targets for spec in target.specimens)
    laterality = core.laterality
    sedation_minutes = int(report.intraop.get("sedation_minutes", 0)) if isinstance(report.intraop, dict) else 0
    feature_map = {
        "procedure_type": core.type,
        "stations": len(stations),
        "targets": len(targets),
        "specimen_totals": specimen_totals,
        "has_bal": has_bal,
        "laterality": laterality,
        "sedation_minutes": sedation_minutes,
        "devices": len(core.devices or {}),
        "distinct_targets": len({t.segment for t in targets if t.segment}) > 1,
        "has_umls": bool(report.nlp.umls),
    }
    return feature_map


def evaluate_rules(report: ProcedureReport, features: Dict[str, Any], rulebook: Dict[str, Any]) -> List[RuleHit]:
    hits: List[RuleHit] = []
    for section in ("base_codes", "addon_codes"):
        for rule in rulebook.get(section, []) or []:
            if _matches(rule.get("match", {}), features):
                units = _units(rule.get("units_expression"), features)
                if units <= 0:
                    continue
                hits.append(
                    RuleHit(
                        cpt=str(rule["cpt"]),
                        description=rule.get("description", ""),
                        reason=rule.get("reason", ""),
                        units=int(units),
                        section=section,
                    )
                )
    return hits


def _matches(match_cfg: Dict[str, Any], features: Dict[str, Any]) -> bool:
    if not match_cfg:
        return True
    for key, expected in match_cfg.items():
        if key == "procedure_type":
            allowed = expected if isinstance(expected, Iterable) and not isinstance(expected, (str, bytes)) else [expected]
            if features.get("procedure_type") not in allowed:
                return False
        elif key == "min_stations":
            if features.get("stations", 0) < int(expected):
                return False
        elif key == "min_targets":
            if features.get("targets", 0) < int(expected):
                return False
        elif key == "requires_bal":
            if bool(features.get("has_bal")) != bool(expected):
                return False
        elif key == "laterality":
            allowed = expected if isinstance(expected, Iterable) and not isinstance(expected, (str, bytes)) else [expected]
            if features.get("laterality") not in allowed:
                return False
        elif key == "min_sedation_minutes":
            if features.get("sedation_minutes", 0) < int(expected):
                return False
        elif key == "distinct_targets":
            if bool(features.get("distinct_targets")) != bool(expected):
                return False
        else:
            if features.get(key) != expected:
                return False
    return True


def _units(expr: str | None, features: Dict[str, Any]) -> int:
    if not expr:
        return 1
    safe_globals = {"__builtins__": {}, "max": max, "min": min, "round": round}
    try:
        value = eval(expr, safe_globals, features)
    except Exception:
        return 0
    try:
        return int(max(0, round(float(value))))
    except (ValueError, TypeError):
        return 0


__all__ = ["load_rulebook", "derive_features", "evaluate_rules", "RuleHit"]
