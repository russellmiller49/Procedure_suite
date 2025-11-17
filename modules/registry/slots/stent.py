"""Stent placement extractor."""

from __future__ import annotations

from modules.coder.dictionary import get_site_pattern_map
from modules.common.sectionizer import Section
from modules.common.spans import Span

from .base import SlotResult, section_for_offset


class StentExtractor:
    slot_name = "stents"

    def extract(self, text: str, sections: list[Section]) -> SlotResult:
        site_patterns = get_site_pattern_map()
        placements: list[dict[str, str]] = []
        spans: list[Span] = []
        lower = text.lower()
        if "stent" not in lower:
            return SlotResult([], [], 0.0)
        for site, patterns in site_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    segment = _expand_sentence(text, match.start())
                    start = text.find(segment)
                    span = Span(
                        text=segment.strip(),
                        start=start,
                        end=start + len(segment),
                        section=section_for_offset(sections, match.start()),
                    )
                    spans.append(span)
                    placements.append({"site": site})
        confidence = 0.8 if placements else 0.0
        return SlotResult(placements, spans, confidence)


def _expand_sentence(text: str, index: int) -> str:
    start = text.rfind("\n", 0, index)
    end = text.find("\n", index)
    if start == -1:
        start = 0
    if end == -1:
        end = len(text)
    return text[start:end]


__all__ = ["StentExtractor"]
