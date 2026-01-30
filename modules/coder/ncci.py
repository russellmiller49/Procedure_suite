"""Minimal NCCI gatekeeper for deterministic bundling."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Set

from config.settings import KnowledgeSettings

NCCI_BUNDLED_REASON_PREFIX = "ncci:bundled_into:"


@lru_cache()
def load_ncci_ptp(path: str | Path | None = None) -> Dict[str, Any]:
    """Load NCCI procedure-to-procedure rules."""
    cfg_path = Path(path) if path is not None else KnowledgeSettings().ncci_path
    with cfg_path.open(encoding="utf-8") as f:
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
            indicator = rule.get("modifier_indicator")
            if indicator not in {"0", "1"}:
                # Backward compatibility: older files used `modifier_allowed: bool`
                indicator = "1" if bool(rule.get("modifier_allowed", False)) else "0"
            modifier_allowed = indicator == "1"

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
