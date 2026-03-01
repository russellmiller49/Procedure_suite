"""Complication extractor."""

from __future__ import annotations

import re

from app.common.sectionizer import Section
from app.common.spans import Span

from .base import SlotResult, section_for_offset

try:
    from .. import schema as registry_schema

    exported_complications = getattr(registry_schema, "COMPLICATIONS", None)
    if isinstance(exported_complications, (list, tuple)):
        _COMPLICATIONS = tuple(str(item) for item in exported_complications)
    else:
        raise AttributeError("COMPLICATIONS not exported")
except Exception:  # pragma: no cover - compat fallback when schema doesn't export constant
    _COMPLICATIONS = (
        "None",
        "Bleeding",
        "Pneumothorax",
        "Hypoxia",
        "Bronchospasm",
        "Hemoptysis",
    )

PATTERNS = {label: re.compile(label, re.IGNORECASE) for label in _COMPLICATIONS if label != "None"}


class ComplicationsExtractor:
    slot_name = "complications"

    def extract(self, text: str, sections: list[Section]) -> SlotResult:
        lower = text.lower()
        if "complication" in lower and "none" in lower:
            idx = lower.find("complication")
            span = Span(
                text="No complications",
                start=idx,
                end=idx + len("No complications"),
                section=section_for_offset(sections, idx),
            )
            return SlotResult(["None"], [span], 0.7)

        evidence: list[Span] = []
        values: list[str] = []
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                values.append(label)
                evidence.append(
                    Span(
                        text=match.group(0),
                        start=match.start(),
                        end=match.end(),
                        section=section_for_offset(sections, match.start()),
                    )
                )
        unique = sorted(dict.fromkeys(values))
        return SlotResult(unique, evidence, 0.7 if unique else 0.0)


__all__ = ["ComplicationsExtractor"]
