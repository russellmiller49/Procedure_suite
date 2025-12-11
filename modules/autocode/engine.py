from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Sequence, Optional

import yaml

from proc_schemas.billing import BillingLine, BillingResult
from proc_schemas.procedure_report import ProcedureReport

from .rules import RuleHit, derive_features, evaluate_rules, load_rulebook
from .confidence import score_confidence
from .ip_kb.ip_kb import IPCodingKnowledgeBase
from .rvu.rvu_calculator import ProcedureRVUCalculator

# Path is: modules/autocode/engine.py -> autocode -> modules -> repo_root
_ROOT = Path(__file__).resolve().parents[2]
_NCCI_PATH = _ROOT / "configs" / "coding" / "ncci_edits.yaml"
_PAYER_PATH = _ROOT / "configs" / "coding" / "payer_overrides.yaml"

# Initialize singletons
_KB_CANDIDATES = [
    _ROOT / "data" / "knowledge" / "ip_coding_billing_v2_8.json",
    _ROOT / "proc_autocode" / "ip_kb" / "ip_coding_billing_v2_8.json",
    _ROOT / "data" / "knowledge" / "ip_coding_billing.v2_2.json",
    _ROOT / "proc_autocode" / "ip_kb" / "ip_coding_billing.v2_2.json",
]
for _candidate in _KB_CANDIDATES:
    if _candidate.exists():
        _KB_PATH = _candidate
        break
else:
    _KB_PATH = _KB_CANDIDATES[0]

_RVU_DIR = _ROOT / "proc_autocode" / "rvu" / "data"
_GPCI_FILE = _RVU_DIR / "gpci_2025.csv"

_KB: Optional[IPCodingKnowledgeBase] = None
_RVU_CALC: Optional[ProcedureRVUCalculator] = None

def _get_kb() -> IPCodingKnowledgeBase:
    global _KB
    if _KB is None:
        _KB = IPCodingKnowledgeBase(_KB_PATH)
    return _KB

def _get_rvu_calc() -> ProcedureRVUCalculator:
    global _RVU_CALC
    if _RVU_CALC is None:
        gpci_path = _GPCI_FILE if _GPCI_FILE.exists() else None
        _RVU_CALC = ProcedureRVUCalculator(_get_kb(), gpci_path)
    return _RVU_CALC


def autocode(report: ProcedureReport, payer: str | None = None) -> BillingResult:
    rulebook = load_rulebook()
    features = derive_features(report)
    hits = evaluate_rules(report, features, rulebook)
    codes = [_hit_to_line(hit, report) for hit in hits]
    
    # Apply bundling from KB
    kb = _get_kb()
    bundled_cpt_list = kb.apply_bundling([line.cpt for line in codes])
    # Filter codes based on bundling
    codes = [line for line in codes if line.cpt in bundled_cpt_list]

    _apply_rule_modifiers(codes, rulebook.get("modifiers", []), features)
    _apply_payer_overrides(codes, payer or report.meta.get("payer"))
    ncci_conflicts = _evaluate_ncci(codes)
    
    # Calculate RVUs
    rvu_calc = _get_rvu_calc()
    locality = report.meta.get("locality", "00")
    setting = report.meta.get("setting", "facility")
    
    procedures = []
    for i, line in enumerate(codes):
        procedures.append({
            "cpt_code": line.cpt,
            "modifiers": line.modifiers,
            "multiplier": 1.0 if i == 0 else 0.5  # Simple multiple procedure rule
        })
    
    case_rvu = rvu_calc.calculate_case_rvu(procedures, locality, setting)
    
    # Attach RVU data to lines
    for line, proc_rvu in zip(codes, case_rvu["breakdown"]):
        line.rvu = proc_rvu

    confidence = score_confidence(features, codes, ncci_conflicts)
    
    audit_trail = {
        "features": features,
        "matched_rules": [asdict(hit) for hit in hits],
        "modifiers": [line.modifiers for line in codes],
        "ncci_conflicts": ncci_conflicts,
        "confidence": confidence.details,
    }
    review_required = confidence.score < 0.6 or bool(ncci_conflicts)
    
    financials = {
        "total_work_rvu": case_rvu["total_work_rvu"],
        "estimated_payment": case_rvu["total_payment"],
        "locality": locality,
        "setting": setting
    }

    return BillingResult(
        codes=codes,
        ncci_conflicts=ncci_conflicts,
        confidence=confidence.score,
        audit_trail=audit_trail,
        review_required=review_required,
        financials=financials
    )


def _hit_to_line(hit: RuleHit, report: ProcedureReport) -> BillingLine:
    evidence = _build_evidence(report)
    return BillingLine(
        cpt=hit.cpt,
        units=hit.units,
        modifiers=[],
        reason=hit.reason,
        evidence=evidence,
    )


def _build_evidence(report: ProcedureReport) -> List[Dict[str, str]]:
    evidence: List[Dict[str, str]] = []
    for hash_ in (report.nlp.paragraph_hashes or [])[:2]:
        evidence.append({"type": "paragraph_hash", "value": hash_})
    for concept in (report.nlp.umls or [])[:2]:
        evidence.append({"type": "cui", "value": concept.get("cui", ""), "text": concept.get("text", "")})
    if not evidence:
        evidence.append({"type": "meta", "value": "structured_fields"})
    return evidence


def _apply_rule_modifiers(codes: List[BillingLine], modifiers_cfg: Sequence[Dict], features: Dict[str, Any]):
    for mod in modifiers_cfg or []:
        apply_if = mod.get("apply_if", {})
        if not _feature_match(apply_if, features):
            continue
        target_cpts = mod.get("cpt")
        target_list = target_cpts if isinstance(target_cpts, list) else [target_cpts] if target_cpts else None
        for line in codes:
            if target_list and line.cpt not in target_list:
                continue
            for modifier in mod.get("modifiers", []):
                if modifier not in line.modifiers:
                    line.modifiers.append(modifier)


def _apply_payer_overrides(codes: List[BillingLine], payer: str | None):
    overrides = _load_yaml(_PAYER_PATH).get("suppliers", [])
    if not overrides:
        return
    targets = [entry for entry in overrides if entry.get("payer") in {payer, "Default"}]
    for entry in targets:
        for spec in entry.get("replaces", []) or []:
            for line in codes:
                if line.cpt == spec.get("cpt"):
                    line.cpt = spec.get("with", line.cpt)
                    line.reason = f"{line.reason} | Override: {spec.get('reason', '')}".strip()
        for spec in entry.get("modifiers", []) or []:
            for line in codes:
                cpt_match = spec.get("cpt")
                if cpt_match and line.cpt != cpt_match:
                    continue
                for modifier in spec.get("add", []):
                    if modifier not in line.modifiers:
                        line.modifiers.append(modifier)


def _evaluate_ncci(codes: List[BillingLine]) -> List[Dict[str, str]]:
    table = _load_yaml(_NCCI_PATH).get("pairs", [])
    conflicts: List[Dict[str, str]] = []
    for row in table:
        pair = set(row.get("codes", []))
        if len(pair) != len(row.get("codes", [])):
            continue
        present = [line for line in codes if line.cpt in pair]
        if len(present) != len(pair):
            continue
        allowed = set(row.get("allow_modifiers", []))
        if allowed and any(set(line.modifiers) & allowed for line in present):
            continue
        conflicts.append(
            {
                "codes": ",".join(sorted(pair)),
                "rationale": row.get("rationale", ""),
            }
        )
    return conflicts


def _feature_match(requirements: Dict[str, Any], features: Dict[str, Any]) -> bool:
    for key, expected in (requirements or {}).items():
        if key == "laterality":
            allowed = expected if isinstance(expected, list) else [expected]
            if features.get("laterality") not in allowed:
                return False
        elif key == "distinct_targets":
            if bool(features.get("distinct_targets")) != bool(expected):
                return False
        else:
            if features.get(key) != expected:
                return False
    return True


def _load_yaml(path: Path) -> Dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


__all__ = ["autocode"]
