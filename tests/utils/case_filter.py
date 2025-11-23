import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "synthetic_notes_with_registry.jsonl"

def load_synthetic_cases() -> List[Dict[str, Any]]:
    """Load all synthetic cases from the JSONL file."""
    cases = []
    if not DATA_PATH.exists():
        return cases
        
    with open(DATA_PATH, "r") as f:
        for line in f:
            if line.strip():
                try:
                    cases.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return cases

def filter_cases(cases: Iterable[Dict[str, Any]], required_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Return only those cases where at least one of the required_fields is present
    and not in (None, "", [], {}).
    If required_fields is None, return all cases.
    """
    if not required_fields:
        return list(cases)
    
    filtered = []
    for case in cases:
        expected = case.get("registry_entry", {})
        has_field = False
        for field in required_fields:
            val = expected.get(field)
            if val not in (None, "", [], {}):
                has_field = True
                break
        if has_field:
            filtered.append(case)
    return filtered

def categorize_case(case: Dict[str, Any]) -> str:
    """Return a coarse category label based on expected registry values."""
    reg = case.get("registry_entry", {})
    if reg.get("ebus_stations_sampled") or reg.get("ebus_systematic_staging"):
        return "EBUS"
    if reg.get("pleural_procedure_type"):
        return "Pleural"
    if reg.get("stent_type"):
        return "Stent"
    return "Other"
