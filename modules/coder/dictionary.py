"""Phrase and regex lexicon powering deterministic intent detection."""

from __future__ import annotations

import re
from typing import Iterator, Sequence

from modules.common.sectionizer import Section
from modules.common.spans import Span

from .schema import DetectedIntent

__all__ = [
    "detect_intents",
    "LOBES",
    "STATION_PATTERNS",
    "SITE_SYNONYMS",
]


SIMPLE_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "navigation": (
        re.compile(r"electromagnetic navigation", re.IGNORECASE),
        re.compile(r"navigation (?:system|bronchoscopy)", re.IGNORECASE),
        re.compile(r"EMN", re.IGNORECASE),
    ),
    "radial_ebus": (
        re.compile(r"radial (?:ebus|endobronchial ultrasound)", re.IGNORECASE),
        re.compile(r"radial probe", re.IGNORECASE),
    ),
    "chartis": (
        re.compile(r"chartis", re.IGNORECASE),
    ),
    "valve": (
        re.compile(r"endobronchial valve", re.IGNORECASE),
        re.compile(r"zephyr valve", re.IGNORECASE),
        re.compile(r"spiration", re.IGNORECASE),
    ),
    "sedation": (
        re.compile(r"moderate sedation", re.IGNORECASE),
        re.compile(r"conscious sedation", re.IGNORECASE),
    ),
    "anesthesia": (
        re.compile(r"general anesthesia", re.IGNORECASE),
        re.compile(r"mac anesthesia", re.IGNORECASE),
    ),
    "aspiration": (
        re.compile(r"therapeutic aspiration", re.IGNORECASE),
    ),
}


LOBES: dict[str, tuple[re.Pattern[str], ...]] = {
    "RUL": (
        re.compile(r"right upper lobe", re.IGNORECASE),
        re.compile(r"\bRUL\b", re.IGNORECASE),
    ),
    "RML": (
        re.compile(r"right middle lobe", re.IGNORECASE),
        re.compile(r"\bRML\b", re.IGNORECASE),
    ),
    "RLL": (
        re.compile(r"right lower lobe", re.IGNORECASE),
        re.compile(r"\bRLL\b", re.IGNORECASE),
    ),
    "LUL": (
        re.compile(r"left upper lobe", re.IGNORECASE),
        re.compile(r"\bLUL\b", re.IGNORECASE),
    ),
    "LLL": (
        re.compile(r"left lower lobe", re.IGNORECASE),
        re.compile(r"\bLLL\b", re.IGNORECASE),
    ),
}


STATION_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "4R": (
        re.compile(r"\b4R\b", re.IGNORECASE),
        re.compile(r"station\s*4\s*(?:right|R)", re.IGNORECASE),
    ),
    "4L": (
        re.compile(r"\b4L\b", re.IGNORECASE),
    ),
    "7": (
        re.compile(r"\b7\b", re.IGNORECASE),
        re.compile(r"station\s*7", re.IGNORECASE),
    ),
    "11R": (
        re.compile(r"\b11R\b", re.IGNORECASE),
    ),
    "11L": (
        re.compile(r"\b11L\b", re.IGNORECASE),
    ),
}


SITE_SYNONYMS: dict[str, tuple[re.Pattern[str], ...]] = {
    "RMB": (
        re.compile(r"right main(?:stem)? bronch(?:us|i)", re.IGNORECASE),
        re.compile(r"\bRMB\b", re.IGNORECASE),
    ),
    "LMB": (
        re.compile(r"left main(?:stem)? bronch(?:us|i)", re.IGNORECASE),
        re.compile(r"\bLMB\b", re.IGNORECASE),
    ),
}
for lobe, patterns in LOBES.items():
    SITE_SYNONYMS[lobe] = patterns


_SENTENCE_RE = re.compile(r"[^.!?\n]+[.!?]?", re.MULTILINE)


def detect_intents(text: str, sections: Sequence[Section]) -> list[DetectedIntent]:
    """Return detected intents for *text* leveraging the curated lexicon."""

    intents: list[DetectedIntent] = []
    intents.extend(_detect_simple(text, sections))
    intents.extend(_detect_lobes(text, sections))
    intents.extend(_detect_stations(text, sections))
    intents.extend(_detect_site_specific(text, sections))
    return intents


def _detect_simple(text: str, sections: Sequence[Section]) -> list[DetectedIntent]:
    results: list[DetectedIntent] = []
    seen: set[tuple[str, int]] = set()
    for intent, patterns in SIMPLE_PATTERNS.items():
        for pattern in patterns:
            for match in pattern.finditer(text):
                key = (intent, match.start())
                if key in seen:
                    continue
                seen.add(key)
                span = _span_from_match(match, sections)
                payload = None
                if intent == "sedation":
                    payload = {"type": "moderate"}
                if intent == "anesthesia":
                    payload = {"type": "general"}
                results.append(
                    DetectedIntent(
                        intent=intent,
                        value=match.group(0),
                        payload=payload,
                        evidence=[span],
                    )
                )
    return results


def _detect_lobes(text: str, sections: Sequence[Section]) -> list[DetectedIntent]:
    results: list[DetectedIntent] = []
    for lobe, patterns in LOBES.items():
        for pattern in patterns:
            for match in pattern.finditer(text):
                span = _span_from_match(match, sections)
                results.append(
                    DetectedIntent(
                        intent="tblb_lobe",
                        value=lobe,
                        evidence=[span],
                        payload={"site": lobe},
                    )
                )
    return results


def _detect_stations(text: str, sections: Sequence[Section]) -> list[DetectedIntent]:
    results: list[DetectedIntent] = []
    for station, patterns in STATION_PATTERNS.items():
        for pattern in patterns:
            for match in pattern.finditer(text):
                span = _span_from_match(match, sections)
                results.append(
                    DetectedIntent(
                        intent="linear_ebus_station",
                        value=station,
                        evidence=[span],
                        payload={"station": station},
                    )
                )
    return results


def _detect_site_specific(text: str, sections: Sequence[Section]) -> list[DetectedIntent]:
    results: list[DetectedIntent] = []
    for start, end, sentence in _iter_sentences(text):
        stripped = sentence.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        if "stent" in lower:
            site = _match_site(stripped)
            if site:
                span = Span(text=stripped, start=start, end=end, section=_section_for_offset(sections, start))
                results.append(
                    DetectedIntent(
                        intent="stent",
                        value=site,
                        payload={"site": site},
                        evidence=[span],
                    )
                )
        if "dilation" in lower or "dilatation" in lower:
            site = _match_site(stripped)
            if site:
                span = Span(text=stripped, start=start, end=end, section=_section_for_offset(sections, start))
                results.append(
                    DetectedIntent(
                        intent="dilation",
                        value=site,
                        payload={"site": site},
                        evidence=[span],
                    )
                )
    return results


def _span_from_match(match: re.Match[str], sections: Sequence[Section]) -> Span:
    start, end = match.span()
    section = _section_for_offset(sections, start)
    return Span(text=match.group(0), start=start, end=end, section=section)


def _match_site(sentence: str) -> str | None:
    for site, patterns in SITE_SYNONYMS.items():
        for pattern in patterns:
            if pattern.search(sentence):
                return site
    return None


def _iter_sentences(text: str) -> Iterator[tuple[int, int, str]]:
    for match in _SENTENCE_RE.finditer(text):
        yield match.start(), match.end(), match.group(0)


def _section_for_offset(sections: Sequence[Section], offset: int) -> str | None:
    for section in sections:
        if section.start <= offset < section.end:
            return section.title
    return None
