"""Minimal NCCI gatekeeper for deterministic bundling."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Set

NCCI_BUNDLED_REASON_PREFIX = "ncci:bundled_into:"


@lru_cache()
def load_ncci_ptp() -> Dict[str, Any]:
    """Load NCCI procedure-to-procedure rules."""
    root = Path(__file__).resolve().parents[2]
    path = root / "data" / "knowledge" / "ncci_ptp.v1.json"
    with path.open() as f:
        data: Dict[str, Any] = json.load(f)
    return data


class NCCIResult:
    """Result of applying NCCI bundling rules."""

    def __init__(self, allowed: Set[str], bundled: Dict[str, str]):
        self.allowed = allowed
        self.bundled = bundled


class NCCIEngine:
    """Applies simple PTP bundling rules."""

    def __init__(self, ptp_cfg: Dict[str, Any] | None = None):
        cfg = ptp_cfg or load_ncci_ptp()
        self._pairs: List[Dict[str, Any]] = cfg.get("pairs", []) or []

    def apply(self, codes: Set[str]) -> NCCIResult:
        allowed = set(codes)
        bundled: Dict[str, str] = {}

        for rule in self._pairs:
            c1 = rule.get("column1")
            c2 = rule.get("column2")
            modifier_allowed = bool(rule.get("modifier_allowed", False))

            if not c1 or not c2:
                continue

            if c1 in allowed and c2 in allowed and not modifier_allowed:
                allowed.discard(c2)
                bundled[c2] = c1

        return NCCIResult(allowed=allowed, bundled=bundled)


__all__ = [
    "NCCIEngine",
    "NCCIResult",
    "load_ncci_ptp",
    "NCCI_BUNDLED_REASON_PREFIX",
]
