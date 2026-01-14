"""EBUS station extraction from NER entities.

Maps ANAT_LN_STATION entities with nearby PROC_ACTION entities
to NodeInteraction records for CPT derivation (31652 vs 31653).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple, Set

from modules.ner.inference import NEREntity, NERExtractionResult
from modules.ner.entity_types import (
    SAMPLING_ACTION_KEYWORDS,
    INSPECTION_ACTION_KEYWORDS,
    VALID_LN_STATIONS,
    normalize_station,
)
from modules.registry.schema import NodeInteraction, NodeActionType, NodeOutcomeType


@dataclass
class StationExtractionResult:
    """Result from station extraction."""

    node_events: List[NodeInteraction]
    stations_sampled: List[str]
    stations_inspected_only: List[str]
    warnings: List[str]


class EBUSStationExtractor:
    """Extract EBUS station node_events from NER entities.

    Algorithm:
    1. Find all ANAT_LN_STATION entities
    2. For each station, find nearest PROC_ACTION within window
    3. Classify action: aspiration → needle_aspiration, viewed → inspected_only
    4. Find nearest OBS_ROSE for outcome
    5. Build NodeInteraction with evidence quote
    """

    # Maximum character distance to look for related entities
    ACTION_WINDOW_CHARS = 200
    ROSE_WINDOW_CHARS = 300

    # Station pattern for validation
    STATION_PATTERN = re.compile(
        r"^(2[RL]|4[RL]|5|7|8|9|10[RL]|11[RL]s?i?)$",
        re.IGNORECASE,
    )

    def __init__(
        self,
        action_window: int = ACTION_WINDOW_CHARS,
        rose_window: int = ROSE_WINDOW_CHARS,
    ) -> None:
        self.action_window = action_window
        self.rose_window = rose_window

    def extract(self, ner_result: NERExtractionResult) -> StationExtractionResult:
        """
        Extract NodeInteraction events from NER entities.

        Args:
            ner_result: NER extraction result with entities

        Returns:
            StationExtractionResult with node_events and station lists
        """
        stations = ner_result.entities_by_type.get("ANAT_LN_STATION", [])
        actions = ner_result.entities_by_type.get("PROC_ACTION", [])
        rose_entities = ner_result.entities_by_type.get("OBS_ROSE", [])

        node_events: List[NodeInteraction] = []
        stations_sampled: Set[str] = set()
        stations_inspected_only: Set[str] = set()
        warnings: List[str] = []
        seen_stations: Set[str] = set()

        for station_entity in stations:
            # Normalize station name
            station_name = self._normalize_station(station_entity.text)
            if not station_name:
                warnings.append(
                    f"Invalid station format: '{station_entity.text}'"
                )
                continue

            # Skip if we've already processed this station
            if station_name in seen_stations:
                continue
            seen_stations.add(station_name)

            # Find nearest action within window
            nearby_action = self._find_nearest(
                station_entity,
                actions,
                self.action_window,
            )

            action_type = self._classify_action(nearby_action)

            # Find nearby ROSE outcome
            nearby_rose = self._find_nearest(
                station_entity,
                rose_entities,
                self.rose_window,
            )
            outcome = self._classify_outcome(nearby_rose)

            # Build evidence quote
            evidence = station_entity.evidence_quote or ""

            node_events.append(
                NodeInteraction(
                    station=station_name,
                    action=action_type,
                    outcome=outcome,
                    evidence_quote=evidence,
                )
            )

            # Track sampled vs inspected
            if action_type != "inspected_only":
                stations_sampled.add(station_name)
            else:
                stations_inspected_only.add(station_name)

        return StationExtractionResult(
            node_events=node_events,
            stations_sampled=sorted(stations_sampled),
            stations_inspected_only=sorted(stations_inspected_only),
            warnings=warnings,
        )

    def _normalize_station(self, text: str) -> Optional[str]:
        """Normalize a station string to canonical format."""
        result = normalize_station(text)
        if result:
            return result

        # Try to extract station from longer text
        # e.g., "station 4R" or "level 7"
        match = re.search(
            r"\b(2[RL]|4[RL]|5|7|8|9|10[RL]|11[RL]s?i?)\b",
            text,
            re.IGNORECASE,
        )
        if match:
            return normalize_station(match.group(1))

        return None

    def _find_nearest(
        self,
        anchor: NEREntity,
        candidates: List[NEREntity],
        window_chars: int,
    ) -> Optional[NEREntity]:
        """Find the nearest candidate entity within window of anchor."""
        if not candidates:
            return None

        best_candidate: Optional[NEREntity] = None
        best_distance = float("inf")

        anchor_center = (anchor.start_char + anchor.end_char) / 2

        for candidate in candidates:
            candidate_center = (candidate.start_char + candidate.end_char) / 2
            distance = abs(anchor_center - candidate_center)

            if distance <= window_chars and distance < best_distance:
                best_distance = distance
                best_candidate = candidate

        return best_candidate

    def _classify_action(
        self,
        action_entity: Optional[NEREntity],
    ) -> NodeActionType:
        """Classify PROC_ACTION entity into NodeActionType."""
        if action_entity is None:
            return "inspected_only"

        text_lower = action_entity.text.lower()

        # Check for sampling keywords
        if any(kw in text_lower for kw in SAMPLING_ACTION_KEYWORDS):
            # Distinguish between aspiration types
            if any(kw in text_lower for kw in ["core", "fnb"]):
                return "core_biopsy"
            if "forceps" in text_lower:
                return "forceps_biopsy"
            return "needle_aspiration"

        # Check for inspection keywords
        if any(kw in text_lower for kw in INSPECTION_ACTION_KEYWORDS):
            return "inspected_only"

        # Default to inspected_only if unclear
        return "inspected_only"

    def _classify_outcome(
        self,
        rose_entity: Optional[NEREntity],
    ) -> Optional[NodeOutcomeType]:
        """Classify OBS_ROSE entity into NodeOutcomeType."""
        if rose_entity is None:
            return None

        text_lower = rose_entity.text.lower()

        if any(kw in text_lower for kw in ["malignant", "positive", "tumor", "cancer", "carcinoma"]):
            return "malignant"
        if any(kw in text_lower for kw in ["suspicious", "atypical"]):
            return "suspicious"
        if any(kw in text_lower for kw in ["benign", "negative", "reactive", "lymphoid"]):
            return "benign"
        if any(kw in text_lower for kw in ["nondiagnostic", "inadequate", "qns"]):
            return "nondiagnostic"

        return "deferred_to_final_path"
