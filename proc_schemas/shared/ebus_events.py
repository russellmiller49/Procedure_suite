"""Shared EBUS node-event primitives.

These types are used in multiple schema layers (V2 dynamic registry + V3 proc schemas)
to represent station-level interactions while keeping a single authoritative definition.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

NodeActionType = Literal[
    "inspected_only",  # Visual/Ultrasound only (NO needle)
    "needle_aspiration",  # TBNA / FNA
    "core_biopsy",  # FNB / Core needle
    "forceps_biopsy",  # Mini-forceps / intranodal forceps
]

NodeOutcomeType = Literal[
    "benign",
    "malignant",
    "suspicious",
    "nondiagnostic",
    "deferred_to_final_path",
    "unknown",
]


class NodeInteraction(BaseModel):
    """Represents an interaction with an EBUS lymph node station.

    Distinguishes inspection-only from actual sampling.
    """

    model_config = ConfigDict(extra="ignore")

    station: str
    action: NodeActionType
    outcome: NodeOutcomeType | None = None
    evidence_quote: str


__all__ = ["NodeActionType", "NodeOutcomeType", "NodeInteraction"]

