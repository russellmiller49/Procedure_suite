"""Sectionization utilities with optional medspaCy support."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence

try:  # pragma: no cover - optional dependency
    import spacy
    from spacy.language import Language
except ImportError:  # pragma: no cover - optional dependency
    spacy = None  # type: ignore
    Language = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from medspacy.sectionizer import Sectionizer as MedspacySectionizer
except ImportError:  # pragma: no cover - optional dependency
    MedspacySectionizer = None  # type: ignore

LOGGER = logging.getLogger(__name__)

SECTION_HEADINGS: tuple[str, ...] = (
    "INDICATION",
    "FINDINGS",
    "PROCEDURE",
    "TECHNIQUE",
    "EBUS",
    "RADIAL",
    "NAVIGATION",
    "STENT",
    "DILATION",
    "BLVR",
    "PLEURA",
    "SEDATION",
    "COMPLICATIONS",
    "DISPOSITION",
)

SECTION_PATTERN = re.compile(
    r"^\s*(?P<title>{})(?:\s*:)?\s*$".format("|".join(map(re.escape, SECTION_HEADINGS))),
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(slots=True)
class Section:
    """Represents a named section of a clinical document."""

    title: str
    text: str
    start: int
    end: int


class SectionizerService:
    """Wraps medspaCy's sectionizer with a regex fallback when unavailable."""

    def __init__(self, headings: Sequence[str] | None = None) -> None:
        self.headings: tuple[str, ...] = tuple(headings or SECTION_HEADINGS)
        self._nlp: Language | None = None
        self._sectionizer = None

        if spacy is not None and MedspacySectionizer is not None:  # pragma: no cover - import guard
            self._nlp = spacy.blank("en")
            rules = self._build_rules(self.headings)
            self._sectionizer = MedspacySectionizer(self._nlp, rules=rules)

    def sectionize(self, text: str) -> list[Section]:
        """Split *text* into logical sections."""

        if self._sectionizer and self._nlp:  # pragma: no branch - runtime guard
            try:
                doc = self._sectionizer(self._nlp(text))
                sections: list[Section] = []
                for sec in doc._.sections:  # type: ignore[attr-defined]
                    sections.append(
                        Section(
                            title=str(sec.category or sec.title).upper(),
                            text=sec.span.text.strip(),
                            start=sec.span.start_char,
                            end=sec.span.end_char,
                        )
                    )
                if sections:
                    return sections
            except Exception as exc:  # pragma: no cover - defensive fallback
                LOGGER.debug("MedspaCy sectionizer failed; falling back to regex: %s", exc)

        return self._regex_sectionize(text)

    def _regex_sectionize(self, text: str) -> list[Section]:
        matches = list(SECTION_PATTERN.finditer(text))
        sections: list[Section] = []

        if not matches:
            clean = text.strip()
            if not clean:
                return []
            return [Section(title="BODY", text=clean, start=0, end=len(text))]

        # Capture any leading narrative before the first heading.
        first_start = matches[0].start()
        if first_start > 0:
            lead_text = text[:first_start].strip()
            if lead_text:
                sections.append(Section(title="PREFACE", text=lead_text, start=0, end=first_start))

        for idx, match in enumerate(matches):
            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            if not body:
                continue
            title = match.group("title").upper()
            sections.append(Section(title=title, text=body, start=start, end=end))

        return sections

    @staticmethod
    def _build_rules(headings: Iterable[str]) -> list[dict[str, object]]:
        rules: list[dict[str, object]] = []
        for heading in headings:
            rules.append(
                {
                    "section_title": heading.upper(),
                    "pattern": rf"^{re.escape(heading)}:?$",
                    "lower": True,
                    "regex": True,
                }
            )
        return rules


__all__ = ["SECTION_HEADINGS", "Section", "SectionizerService"]

