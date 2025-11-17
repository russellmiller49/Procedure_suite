"""Phrase and regex lexicon powering deterministic intent detection."""

from __future__ import annotations

import re
from typing import Iterator, Sequence

from modules.common.knowledge import get_knowledge
from modules.common.sectionizer import Section
from modules.common.spans import Span

from .schema import DetectedIntent

__all__ = [
    "detect_intents",
    "get_lobe_pattern_map",
    "get_station_pattern_map",
    "get_site_pattern_map",
]


DEFAULT_SIMPLE_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
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


DEFAULT_LOBE_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
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


DEFAULT_STATION_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
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


DEFAULT_SITE_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "RMB": (
        re.compile(r"right main(?:stem)? bronch(?:us|i)", re.IGNORECASE),
        re.compile(r"\bRMB\b", re.IGNORECASE),
    ),
    "LMB": (
        re.compile(r"left main(?:stem)? bronch(?:us|i)", re.IGNORECASE),
        re.compile(r"\bLMB\b", re.IGNORECASE),
    ),
}


_SENTENCE_RE = re.compile(r"[^.!?\n]+[.!?]?", re.MULTILINE)


def detect_intents(text: str, sections: Sequence[Section]) -> list[DetectedIntent]:
    """Return detected intents for *text* leveraging the curated lexicon."""

    knowledge = get_knowledge()
    simple_patterns = _build_simple_patterns(knowledge)
    lobe_patterns = _build_lobe_patterns(knowledge)
    station_patterns = _build_station_patterns(knowledge)
    site_patterns = _build_site_patterns(knowledge, lobe_patterns)
    site_keywords = _build_site_keywords(knowledge)

    intents: list[DetectedIntent] = []
    intents.extend(_detect_simple(text, sections, simple_patterns))
    intents.extend(_detect_lobes(text, sections, lobe_patterns))
    intents.extend(_detect_stations(text, sections, station_patterns))
    intents.extend(_detect_site_specific(text, sections, site_patterns, site_keywords))
    return intents


def _detect_simple(
    text: str, sections: Sequence[Section], patterns: dict[str, tuple[re.Pattern[str], ...]]
) -> list[DetectedIntent]:
    results: list[DetectedIntent] = []
    seen: set[tuple[str, int]] = set()
    for intent, compiled_patterns in patterns.items():
        for pattern in compiled_patterns:
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


def _detect_lobes(
    text: str,
    sections: Sequence[Section],
    lobe_patterns: dict[str, tuple[re.Pattern[str], ...]],
) -> list[DetectedIntent]:
    results: list[DetectedIntent] = []
    for lobe, patterns in lobe_patterns.items():
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


def _detect_stations(
    text: str,
    sections: Sequence[Section],
    station_patterns: dict[str, tuple[re.Pattern[str], ...]],
) -> list[DetectedIntent]:
    results: list[DetectedIntent] = []
    for station, patterns in station_patterns.items():
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


def _detect_site_specific(
    text: str,
    sections: Sequence[Section],
    site_patterns: dict[str, tuple[re.Pattern[str], ...]],
    site_keywords: dict[str, list[str]],
) -> list[DetectedIntent]:
    results: list[DetectedIntent] = []
    for start, end, sentence in _iter_sentences(text):
        stripped = sentence.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        if any(keyword in lower for keyword in site_keywords["stent"]):
            site = _match_site(stripped, site_patterns)
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
        if any(keyword in lower for keyword in site_keywords["dilation"]):
            site = _match_site(stripped, site_patterns)
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


def _match_site(sentence: str, patterns: dict[str, tuple[re.Pattern[str], ...]]) -> str | None:
    for site, compiled_patterns in patterns.items():
        for pattern in compiled_patterns:
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


def _build_simple_patterns(knowledge: dict) -> dict[str, tuple[re.Pattern[str], ...]]:
    patterns = {key: list(value) for key, value in DEFAULT_SIMPLE_PATTERNS.items()}
    synonyms = knowledge.get("synonyms", {})
    for intent, terms in synonyms.items():
        if intent not in patterns:
            continue
        patterns[intent].extend(_literal_pattern(term) for term in terms)
    return {intent: tuple(compiled) for intent, compiled in patterns.items()}


def _build_lobe_patterns(knowledge: dict) -> dict[str, tuple[re.Pattern[str], ...]]:
    patterns = {key: list(value) for key, value in DEFAULT_LOBE_PATTERNS.items()}
    lobes = knowledge.get("lobes", {})
    for lobe, synonyms in lobes.items():
        patterns.setdefault(lobe, [])
        patterns[lobe].extend(_literal_pattern(term) for term in synonyms)
    return {lobe: tuple(compiled) for lobe, compiled in patterns.items()}


def _build_station_patterns(knowledge: dict) -> dict[str, tuple[re.Pattern[str], ...]]:
    patterns = {key: list(value) for key, value in DEFAULT_STATION_PATTERNS.items()}
    stations = knowledge.get("stations", {})
    for station, synonyms in stations.items():
        patterns.setdefault(station, [])
        patterns[station].extend(_literal_pattern(term) for term in synonyms)
    return {station: tuple(compiled) for station, compiled in patterns.items()}


def _build_site_patterns(
    knowledge: dict,
    lobe_patterns: dict[str, tuple[re.Pattern[str], ...]],
) -> dict[str, tuple[re.Pattern[str], ...]]:
    patterns = {key: list(value) for key, value in DEFAULT_SITE_PATTERNS.items()}
    sites = knowledge.get("sites", {})
    for site, synonyms in sites.items():
        patterns.setdefault(site, [])
        patterns[site].extend(_literal_pattern(term) for term in synonyms)
    for lobe, regexes in lobe_patterns.items():
        patterns.setdefault(lobe, [])
        patterns[lobe].extend(regexes)
    return {site: tuple(compiled) for site, compiled in patterns.items()}


def _build_site_keywords(knowledge: dict) -> dict[str, list[str]]:
    synonyms = knowledge.get("synonyms", {})
    stent_keywords = _normalize_keywords(["stent"] + synonyms.get("stent", []))
    dilation_keywords = _normalize_keywords(["dilation", "dilatation"] + synonyms.get("dilation", []))
    return {"stent": stent_keywords, "dilation": dilation_keywords}


def _normalize_keywords(keywords: list[str]) -> list[str]:
    normalized: list[str] = []
    for keyword in keywords:
        normalized.append(keyword.lower())
    return normalized


def _literal_pattern(term: str) -> re.Pattern[str]:
    return re.compile(re.escape(term), re.IGNORECASE)


def get_lobe_pattern_map() -> dict[str, tuple[re.Pattern[str], ...]]:
    return _build_lobe_patterns(get_knowledge())


def get_station_pattern_map() -> dict[str, tuple[re.Pattern[str], ...]]:
    return _build_station_patterns(get_knowledge())


def get_site_pattern_map() -> dict[str, tuple[re.Pattern[str], ...]]:
    knowledge = get_knowledge()
    lobe_patterns = _build_lobe_patterns(knowledge)
    return _build_site_patterns(knowledge, lobe_patterns)
