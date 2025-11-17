"""Transbronchial biopsy slot extractor."""

from __future__ import annotations

from modules.coder.dictionary import get_lobe_pattern_map
from modules.common.sectionizer import Section
from modules.common.spans import Span

from .base import SlotResult, section_for_offset


class TBLBExtractor:
    slot_name = "tblb_lobes"

    def extract(self, text: str, sections: list[Section]) -> SlotResult:
        lobe_patterns = get_lobe_pattern_map()
        lobes: list[str] = []
        spans: list[Span] = []
        for lobe, patterns in lobe_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    lobes.append(lobe)
                    spans.append(
                        Span(
                            text=match.group(0),
                            start=match.start(),
                            end=match.end(),
                            section=section_for_offset(sections, match.start()),
                        )
                    )
        unique = sorted(dict.fromkeys(lobes))
        confidence = 0.0 if not unique else 0.8
        return SlotResult(unique, spans, confidence)


__all__ = ["TBLBExtractor"]
