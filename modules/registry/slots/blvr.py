"""BLVR slot extraction."""

from __future__ import annotations

import re

from modules.coder.dictionary import LOBES
from modules.common.sectionizer import Section
from modules.common.spans import Span

from ..schema import BLVRData
from .base import SlotResult, section_for_offset

VALVE_PATTERN = re.compile(r"valve", re.IGNORECASE)
MANUFACTURERS = {
    "Zephyr": re.compile(r"zephyr", re.IGNORECASE),
    "Spiration": re.compile(r"spiration", re.IGNORECASE),
}


class BLVRExtractor:
    slot_name = "blvr"

    def extract(self, text: str, sections: list[Section]) -> SlotResult:
        if "valve" not in text.lower() and "chartis" not in text.lower():
            return SlotResult(None, [], 0.0)

        lobes: list[str] = []
        evidence: list[Span] = []
        for lobe, patterns in LOBES.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    lobes.append(lobe)
                    evidence.append(
                        Span(
                            text=match.group(0),
                            start=match.start(),
                            end=match.end(),
                            section=section_for_offset(sections, match.start()),
                        )
                    )

        valve_mentions = list(VALVE_PATTERN.finditer(text))
        valve_count = len(valve_mentions)
        for match in valve_mentions:
            evidence.append(
                Span(
                    text=match.group(0),
                    start=match.start(),
                    end=match.end(),
                    section=section_for_offset(sections, match.start()),
                )
            )

        manufacturer = None
        for label, pattern in MANUFACTURERS.items():
            m = pattern.search(text)
            if m:
                manufacturer = label
                evidence.append(
                    Span(
                        text=m.group(0),
                        start=m.start(),
                        end=m.end(),
                        section=section_for_offset(sections, m.start()),
                    )
                )
                break

        if not lobes and valve_count == 0:
            return SlotResult(None, [], 0.0)

        value = BLVRData(lobes=sorted(dict.fromkeys(lobes)) or ["Unknown"], valve_count=valve_count or None, manufacturer=manufacturer)
        return SlotResult(value, evidence, 0.75)


__all__ = ["BLVRExtractor"]

